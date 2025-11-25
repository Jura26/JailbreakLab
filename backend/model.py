import asyncio
from typing import Optional, Dict, Tuple

import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from fastapi.responses import StreamingResponse

# Simple cache to avoid re-loading models repeatedly
_MODEL_CACHE: Dict[str, Tuple[AutoTokenizer, AutoModelForCausalLM]] = {}


def get_model_and_tokenizer(model_id: str, device: str = "cpu"):
    """Load (and cache) tokenizer and model for a given `model_id`.
    Uses float16 on CUDA when available, otherwise float32 on CPU.

    Note: This function no longer prints progress markers. Progress for
    direct model calls is streamed from `_generate_and_stream` instead.
    """
    key = f"{model_id}:{device}"
    if key in _MODEL_CACHE:
        print(f"Using cached model: {model_id}")
        return _MODEL_CACHE[key]

    print(f"Loading model {model_id} from HuggingFace (this may take a while)...")
    dtype = torch.float16 if (device == "cuda" and torch.cuda.is_available()) else torch.float32

    try:
        # Load tokenizer
        print(f"Loading tokenizer for {model_id}...")
        tokenizer = AutoTokenizer.from_pretrained(model_id)
        if getattr(tokenizer, "pad_token_id", None) is None:
            tokenizer.pad_token_id = tokenizer.eos_token_id
        print(f"Tokenizer loaded successfully")

        # Load or reuse model
        print(f"Loading model weights for {model_id}...")
        model = AutoModelForCausalLM.from_pretrained(
            model_id,
            dtype=dtype,
            device_map="auto" if (device == "cuda" and torch.cuda.is_available()) else None,
        )
        print(f"Model {model_id} loaded successfully")

        model.eval()
        _MODEL_CACHE[key] = (tokenizer, model)
        return tokenizer, model
    except Exception as e:
        print(f"Failed to load model {model_id}: {e}")
        raise


async def _generate_and_stream(tokenizer, model, prompt: str, generation_options: Dict) -> StreamingResponse:
    """Run generation synchronously but expose results as an async stream (yields one chunk).
    This keeps the StreamingResponse interface while keeping implementation simple.
    """

    async def _aiter():
        # Run generation in a thread to avoid blocking async loop
        loop = asyncio.get_running_loop()
        
        yield b"[PROGRESS] 10\n"

        def _run():
            # Determine positional embeddings and safe max_new_tokens
            max_pos = getattr(model.config, "n_positions", None) or getattr(model.config, "max_position_embeddings", None) or getattr(model.config, "n_ctx", None)
            if max_pos is None:
                max_pos = 1024

            # Tokenize with truncation to fit model
            encoded = tokenizer(prompt, truncation=True, max_length=int(max_pos) - 1, return_tensors="pt")
            input_ids = encoded.get("input_ids")
            input_len = int(input_ids.shape[1]) if input_ids is not None else 0

            # Compute max_new_tokens safely
            requested_new = int(generation_options.get("max_new_tokens", 128))
            max_new_tokens = max(1, min(requested_new, int(max_pos) - max(1, input_len)))

            gen_kwargs = {
                "input_ids": encoded["input_ids"].to(model.device),
                "max_new_tokens": max_new_tokens,
                "do_sample": generation_options.get("do_sample", True),
                "temperature": generation_options.get("temperature", 0.9),
                "top_p": generation_options.get("top_p", 0.95),
                "top_k": generation_options.get("top_k", 50),
                "repetition_penalty": generation_options.get("repetition_penalty", 1.0),
                "pad_token_id": tokenizer.eos_token_id,
            }

            # Attach attention mask only if it exists (avoid boolean-check on tensor)
            attention_mask = encoded.get("attention_mask")
            if attention_mask is not None:
                gen_kwargs["attention_mask"] = attention_mask.to(model.device)

            # Merge any additional kwargs user passed
            extra = generation_options.get("extra_generation_kwargs") or {}
            gen_kwargs.update(extra)

            with torch.no_grad():
                output = model.generate(**gen_kwargs)

            # Decode and strip prompt echo if present
            text = tokenizer.decode(output[0], skip_special_tokens=True)
            if text.startswith(prompt):
                text = text[len(prompt):].lstrip()
            return text

        yield b"[PROGRESS] 40\n"
        text = await loop.run_in_executor(None, _run)
        yield b"[PROGRESS] 95\n"
        yield text.encode("utf-8")

    return StreamingResponse(_aiter(), media_type="text/plain")


async def generate_streaming(model_id: str, prompt: str, device: str = "cpu", generation_options: Optional[Dict] = None) -> StreamingResponse:
    """Public helper to generate text for `prompt` using `model_id` and return a StreamingResponse.
    """
    if generation_options is None:
        generation_options = {}

    async def _stream_with_loading():
        # Yield early progress markers while loading model
        yield b"[PROGRESS] 0\n"
        
        # Load model in thread to avoid blocking
        loop = asyncio.get_running_loop()
        
        def _load_model():
            return get_model_and_tokenizer(model_id, device)
        
        yield b"[PROGRESS] 5\n"
        tokenizer, model = await loop.run_in_executor(None, _load_model)
        yield b"[PROGRESS] 8\n"
        
        # Now stream generation results
        resp = await _generate_and_stream(tokenizer, model, prompt, generation_options)
        async for chunk in resp.body_iterator:
            yield chunk
    
    return StreamingResponse(_stream_with_loading(), media_type="text/plain")
