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
    """
    key = f"{model_id}:{device}"
    if key in _MODEL_CACHE:
        return _MODEL_CACHE[key]

    print("[PROGRESS] 10", flush=True)
    dtype = torch.float16 if (device == "cuda" and torch.cuda.is_available()) else torch.float32

    # Load tokenizer
    tokenizer = AutoTokenizer.from_pretrained(model_id)
    if getattr(tokenizer, "pad_token_id", None) is None:
        tokenizer.pad_token_id = tokenizer.eos_token_id
    print("[PROGRESS] 20", flush=True)

    # Load or reuse model
    print("[PROGRESS] 30", flush=True)
    model = AutoModelForCausalLM.from_pretrained(
        model_id,
        dtype=dtype,
        device_map="auto" if (device == "cuda" and torch.cuda.is_available()) else None,
    )

    model.eval()
    _MODEL_CACHE[key] = (tokenizer, model)
    print("[PROGRESS] 40", flush=True)
    return tokenizer, model


async def _generate_and_stream(tokenizer, model, prompt: str, generation_options: Dict) -> StreamingResponse:
    """Run generation synchronously but expose results as an async stream (yields one chunk).
    This keeps the StreamingResponse interface while keeping implementation simple.
    """

    async def _aiter():
        # Run generation in a thread to avoid blocking async loop
        loop = asyncio.get_running_loop()

        def _run():
            print("[PROGRESS] 60", flush=True)
            # Determine positional embeddings and safe max_new_tokens
            max_pos = getattr(model.config, "n_positions", None) or getattr(model.config, "max_position_embeddings", None) or getattr(model.config, "n_ctx", None)
            if max_pos is None:
                max_pos = 1024

            # Tokenize with truncation to fit model
            encoded = tokenizer(prompt, truncation=True, max_length=int(max_pos) - 1, return_tensors="pt")
            input_ids = encoded.get("input_ids")
            input_len = int(input_ids.shape[1]) if input_ids is not None else 0
            print("[PROGRESS] 70", flush=True)

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

            print("[PROGRESS] 80", flush=True)
            with torch.no_grad():
                output = model.generate(**gen_kwargs)

            print("[PROGRESS] 95", flush=True)
            # Decode and strip prompt echo if present
            text = tokenizer.decode(output[0], skip_special_tokens=True)
            if text.startswith(prompt):
                text = text[len(prompt):].lstrip()
            print("[PROGRESS] 100", flush=True)
            return text

        try:
            text = await loop.run_in_executor(None, _run)
            # Yield as a single chunk — consumers can iterate the stream
            yield text.encode("utf-8")
        except Exception as e:
            # Yield an error message (keeps StreamingResponse contract)
            yield f"[ERROR] Generation failed: {e}\n".encode("utf-8")

    return StreamingResponse(_aiter(), media_type="text/plain")


async def generate_streaming(model_id: str, prompt: str, device: str = "cpu", generation_options: Optional[Dict] = None) -> StreamingResponse:
    """Public helper to generate text for `prompt` using `model_id` and return a StreamingResponse.
    """
    if generation_options is None:
        generation_options = {}

    tokenizer, model = get_model_and_tokenizer(model_id, device)
    return await _generate_and_stream(tokenizer, model, prompt, generation_options)
