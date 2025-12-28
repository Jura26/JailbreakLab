#!/usr/bin/env python3
"""
GCG Attack - Refactored for in-process execution (no subprocess)

Exports:
    - run_gcg_attack() - async generator for in-process use from main.py
"""
import os
import gc
import warnings
import asyncio
import traceback
from typing import AsyncGenerator, Optional

import numpy as np
import torch
import torch.nn as nn
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
from fastapi.responses import StreamingResponse

from defenses.defense_manager import apply_defense

# Silence warnings
os.environ["TRANSFORMERS_VERBOSITY"] = "error"
os.environ["HF_HUB_OFFLINE"] = "0"
os.environ["TOKENIZERS_PARALLELISM"] = "false"
warnings.filterwarnings("ignore")
import logging
logging.getLogger("transformers").setLevel(logging.ERROR)


class GCGAttack:
    """
    GCG (Greedy Coordinate Gradient) Attack Implementation
    Optimized for production use with model caching and streaming output.
    """
    
    def __init__(
        self,
        model,
        tokenizer,
        device: str = "cuda" if torch.cuda.is_available() else "cpu",
        num_steps: int = 220,
        batch_size: int = 256,
        topk: int = 256,
        allow_non_ascii: bool = False
    ):
        self.model = model
        self.tokenizer = tokenizer
        self.device = device
        self.num_steps = num_steps
        self.batch_size = batch_size
        self.topk = topk
        self.allow_non_ascii = allow_non_ascii
        
    async def attack(
        self,
        user_prompt: str,
        target_output: str,
        adv_string_init: str = "! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! !",
    ) -> AsyncGenerator[bytes, None]:
        """
        Run GCG attack with streaming progress updates.
        
        Yields progress updates and final adversarial suffix.
        """
        yield b"[PROGRESS] 0\n"
        yield "Starting GCG Attack Optimization\n".encode("utf-8")
        yield f"Model: {self.model.config._name_or_path}\n".encode("utf-8")
        yield f"Device: {self.device}\n".encode("utf-8")
        yield f"Max iterations: {self.num_steps}\n".encode("utf-8")
        yield f"Batch size: {self.batch_size}\n".encode("utf-8")
        yield ("=" * 60 + "\n\n").encode("utf-8")
        
        # Tokenize components
        user_toks = self.tokenizer(user_prompt, add_special_tokens=False).input_ids
        target_toks = self.tokenizer(target_output, add_special_tokens=False).input_ids
        adv_toks = self.tokenizer(adv_string_init, add_special_tokens=False).input_ids
        
        best_adv_toks = adv_toks.copy()
        losses = []
        best_loss = float('inf')
        
        # Get embedding layer and vocab size
        embed_layer = self.model.get_input_embeddings()
        embed_weights = embed_layer.weight
        vocab_size = embed_weights.shape[0]
        
        # Create token filter mask
        filter_mask = torch.ones(vocab_size, dtype=torch.bool, device=self.device)
        if not self.allow_non_ascii:
            for i in range(vocab_size):
                try:
                    token_str = self.tokenizer.decode([i])
                    if any(ord(c) > 127 for c in token_str):
                        filter_mask[i] = False
                except:
                    filter_mask[i] = False
        
        yield f"Vocabulary size: {vocab_size}, Allowed tokens: {filter_mask.sum().item()}\n\n".encode("utf-8")
        yield b"[PROGRESS] 5\n"
        
        for step in range(self.num_steps):
            # Construct full input
            full_toks = user_toks + best_adv_toks + target_toks
            input_ids = torch.tensor(full_toks, device=self.device)
            
            adv_start = len(user_toks)
            adv_end = adv_start + len(best_adv_toks)
            
            # Create one-hot encoding for adversarial tokens
            adv_ids = input_ids[adv_start:adv_end]
            one_hot = torch.zeros(
                len(best_adv_toks),
                vocab_size,
                device=self.device,
                dtype=embed_weights.dtype
            )
            one_hot.scatter_(1, adv_ids.unsqueeze(1), 1.0)
            one_hot.requires_grad_(True)
            
            # Get embeddings
            with torch.no_grad():
                embeds = embed_layer(input_ids).detach()
            
            # Compute adversarial embeddings with gradient
            adv_embeds = one_hot @ embed_weights
            
            # Construct full embeddings
            full_embeds = torch.cat([
                embeds[:adv_start],
                adv_embeds,
                embeds[adv_end:]
            ], dim=0).unsqueeze(0)
            
            # Forward pass
            logits = self.model(inputs_embeds=full_embeds).logits[0]
            
            # Compute loss using proper slice alignment (as in paper)
            # Loss slice should be target_slice.start-1 to target_slice.stop-1
            target_start = adv_end
            loss_slice = slice(target_start-1, target_start-1+len(target_toks))
            target_slice = slice(target_start, target_start+len(target_toks))
            loss = nn.CrossEntropyLoss()(logits[loss_slice, :], input_ids[target_slice])
            
            # Backward pass
            loss.backward()
            
            # Get gradients and normalize (critical for GCG paper)
            grad = one_hot.grad.clone()
            grad = grad / grad.norm(dim=-1, keepdim=True)
            
            # Apply token filter to gradients
            with torch.no_grad():
                grad[:, ~filter_mask] = float('inf')
            
            # Sample candidates using coordinate-wise greedy sampling (as in paper)
            with torch.no_grad():
                # Get top-k tokens for each position
                top_indices = (-grad).topk(self.topk, dim=1).indices
                
                # Generate candidates using proper coordinate-wise sampling from paper
                # This is critical: sample positions uniformly and substitute with top-k tokens
                control_toks_tensor = torch.tensor(best_adv_toks, device=self.device)
                original_control_toks = control_toks_tensor.repeat(self.batch_size, 1)
                
                # Sample positions uniformly across the suffix (coordinate-wise)
                new_token_pos = torch.arange(
                    0, 
                    len(best_adv_toks), 
                    len(best_adv_toks) / self.batch_size,
                    device=self.device
                ).type(torch.int64)
                
                # Sample token values from top-k for each position
                new_token_val = torch.gather(
                    top_indices[new_token_pos], 1, 
                    torch.randint(0, self.topk, (self.batch_size, 1), device=self.device)
                )
                
                # Create new candidates by scattering new token values
                new_control_toks = original_control_toks.scatter_(1, new_token_pos.unsqueeze(-1), new_token_val)
                
                # Convert to list of token lists
                candidates = [new_control_toks[i].cpu().tolist() for i in range(self.batch_size)]
                
                # Batch evaluate candidates
                eval_batch_size = 32
                best_candidate = best_adv_toks
                best_cand_loss = best_loss
                
                for i in range(0, len(candidates), eval_batch_size):
                    batch = candidates[i:i+eval_batch_size]
                    
                    # Stack inputs
                    batch_inputs = []
                    for cand in batch:
                        full_toks = user_toks + cand + target_toks
                        batch_inputs.append(torch.tensor(full_toks, device=self.device))
                    batch_inputs = torch.stack(batch_inputs)
                    
                    # Batch forward pass
                    with torch.no_grad():
                        batch_logits = self.model(batch_inputs).logits
                        
                        for j, cand in enumerate(batch):
                            target_start = len(user_toks) + len(cand)
                            target_logits = batch_logits[j, target_start-1:target_start-1+len(target_toks)]
                            target_ids = batch_inputs[j, target_start:target_start+len(target_toks)]
                            cand_loss = nn.CrossEntropyLoss()(target_logits, target_ids).item()
                            
                            if cand_loss < best_cand_loss:
                                best_cand_loss = cand_loss
                                best_candidate = cand
                    
                    # Periodic cleanup
                    if (i // eval_batch_size) % 4 == 0:
                        torch.cuda.empty_cache() if torch.cuda.is_available() else None
                
                # Update best suffix
                if best_cand_loss < best_loss:
                    best_loss = best_cand_loss
                    best_adv_toks = best_candidate
            
            losses.append(best_loss)
            
            # Progress reporting
            if step % 10 == 0 or step == 0:
                progress_pct = 5 + ((step + 1) / self.num_steps * 85)  # 5-90% range
                yield f"[PROGRESS] {progress_pct:.2f}\n".encode("utf-8")
                adv_string = self.tokenizer.decode(best_adv_toks)
                yield f"Step {step+1}/{self.num_steps} ({((step+1)/self.num_steps*100):.1f}%) | Loss: {best_loss:.4f}\n".encode("utf-8")
                yield f"Suffix: {adv_string[:100]}...\n\n".encode("utf-8")
                await asyncio.sleep(0)  # Allow other tasks to run
            
            # Early stopping if converged
            if len(losses) > 20:
                recent_losses = losses[-20:]
                if max(recent_losses) - min(recent_losses) < 0.01:
                    yield "Early stopping: Loss converged\n".encode("utf-8")
                    break
            
            # Cleanup
            del one_hot, adv_embeds, full_embeds, logits, grad
            if step % 20 == 0:
                gc.collect()
                torch.cuda.empty_cache() if torch.cuda.is_available() else None
        
        best_adv_string = self.tokenizer.decode(best_adv_toks)
        
        yield b"[PROGRESS] 90\n"
        yield ("\n" + "=" * 60 + "\n").encode("utf-8")
        yield "Optimization Complete!\n".encode("utf-8")
        yield ("=" * 60 + "\n").encode("utf-8")
        yield f"Best adversarial suffix: {best_adv_string}\n".encode("utf-8")
        yield f"Final loss: {losses[-1]:.4f}\n".encode("utf-8")
        yield f"Total iterations: {len(losses)}\n\n".encode("utf-8")
        
        # Test the attack
        yield b"Testing adversarial prompt:\n"
        test_prompt = f"{user_prompt} {best_adv_string}"
        yield f"Prompt: {test_prompt}\n\n".encode("utf-8")
        yield b"Generating response...\n\n"
        yield b"[PROGRESS] 95\n"
        
        # Tokenize and generate
        inputs = self.tokenizer(test_prompt, return_tensors="pt").to(self.device)
        outputs = self.model.generate(
            **inputs,
            max_new_tokens=100,
            do_sample=False,
            temperature=1.0,
            pad_token_id=self.tokenizer.eos_token_id
        )
        
        response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        yield f"Model response:\n{response}\n".encode("utf-8")
        yield b"[PROGRESS] 100\n"


async def run_gcg_attack(
    model_id: str,
    template: str,
    defense: str,
    session_id: Optional[str] = None,
    num_steps: int = 220,
    batch_size: int = 256,
    topk: int = 256
) -> AsyncGenerator[bytes, None]:
    """
    Run GCG attack with defense checking and streaming output.
    
    Args:
        model_id: HuggingFace model ID
        template: User prompt to attack
        defense: Defense mechanism to apply
        session_id: Session ID for history tracking
        num_steps: Number of optimization steps
        batch_size: Batch size for candidate evaluation
        topk: Top-k tokens to consider
    
    Yields:
        Bytes containing progress updates and results
    """
    yield b"[PROGRESS] 0\n"
    device = "cuda" if torch.cuda.is_available() else "cpu"
    
    # Check defense first
    try:
        blocked, resp = await apply_defense(defense, template, model_id=model_id, device=device, session_id=session_id, skip_progress=True)
        if blocked:
            if resp and isinstance(resp, StreamingResponse):
                async for chunk in resp.body_iterator:
                    yield chunk
            else:
                yield b"Request blocked by defense mechanism\n"
            yield b"[PROGRESS] 100\n"
            return
    except Exception as e:
        yield f"Error in defense check: {e}\n".encode("utf-8")
        traceback.print_exc()
    
    # Load model and tokenizer
    try:
        yield b"[PROGRESS] 1\n"
        yield b"Loading model and tokenizer...\n"
        
        tokenizer = AutoTokenizer.from_pretrained(model_id)
        tokenizer.pad_token = tokenizer.eos_token
        
        yield b"[PROGRESS] 2\n"
        
        # Use 8-bit quantization for large models
        use_8bit = "7b" in model_id.lower() or "13b" in model_id.lower()
        
        if use_8bit and torch.cuda.is_available():
            yield b"Using 8-bit quantization for large model...\n"
            quantization_config = BitsAndBytesConfig(
                load_in_8bit=True,
                llm_int8_threshold=6.0
            )
            model = AutoModelForCausalLM.from_pretrained(
                model_id,
                device_map="auto",
                quantization_config=quantization_config,
                torch_dtype=torch.float16
            )
        else:
            model = AutoModelForCausalLM.from_pretrained(
                model_id,
                torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32
            )
            model = model.to(device)
        
        model.eval()
        yield b"[PROGRESS] 4\n"
        yield b"Model loaded successfully!\n\n"
        
    except Exception as e:
        yield f"Error loading model: {e}\n".encode("utf-8")
        traceback.print_exc()
        yield b"[PROGRESS] 100\n"
        return
    
    # Run attack
    try:
        attack = GCGAttack(
            model=model,
            tokenizer=tokenizer,
            device=device,
            num_steps=num_steps,
            batch_size=batch_size,
            topk=topk,
            allow_non_ascii=False
        )
        
        # Default target output
        target_output = "Sure, here is a response to your request"
        
        async for chunk in attack.attack(template, target_output):
            yield chunk
            
    except Exception as e:
        yield f"\nError during attack: {e}\n".encode("utf-8")
        traceback.print_exc()
        yield b"[PROGRESS] 100\n"
    finally:
        # Cleanup
        del model
        gc.collect()
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
