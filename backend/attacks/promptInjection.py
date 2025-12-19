#!/usr/bin/env python3

# main.py
import os

import argparse
import warnings
from typing import Optional, AsyncGenerator
from fastapi.responses import StreamingResponse

import asyncio
import torch
from defenses.defense_manager import apply_defense

from .rolePlaying import run_role_playing_attack
from .chainOfQuestions import run_chain_of_questions_attack
from .danAttack import run_dan_attack
from .asciiArtJailbreak import run_ascii_art_jailbreak_attack
from .neuroStrike.neuroStrike import run_neurostrike_attack

# silencing / controlling verbosity BEFORE importing transformers/accelerate/others
os.environ["TRANSFORMERS_VERBOSITY"] = "error"
os.environ["HF_HUB_OFFLINE"] = "0"
os.environ["TOKENIZERS_PARALLELISM"] = "false"

# Suppress device placement messages
warnings.filterwarnings("ignore")
import logging
logging.getLogger("transformers").setLevel(logging.ERROR)

async def _run_model_for_attack(model_id: str, template: str, defense: str, session_id: Optional[str] = None) -> Optional[StreamingResponse]:
    """Internal helper: Check defenses and run model. Returns StreamingResponse or None."""
    device = "cuda" if torch.cuda.is_available() else "cpu"
    
    try:
        blocked, resp = await apply_defense(defense, template, model_id=model_id, device=device, session_id=session_id)
    except Exception as e:
        print(f"Error loading/running model {model_id}: {e}", flush=True)
        import traceback
        traceback.print_exc()
        return None

    if blocked:
        return resp
    return resp


# ============================================================================
# CLI COMPATIBILITY (legacy subprocess mode)
# ============================================================================

async def main(model_id: str, template: str, print_output: bool, defense: str) -> Optional[StreamingResponse]:
    """Legacy CLI entry point (keeps compatibility with subprocess mode).
    Returns a StreamingResponse when `print_output` is True so callers can
    consume it, otherwise consumes and returns None.
    """
    print("[PROGRESS] 0", flush=True)
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print("[PROGRESS] 5", flush=True)

    # Request the defense manager to either block or run the model for us.
    print("[PROGRESS] 10", flush=True)
    try:
        resp = await _run_model_for_attack(model_id, template, defense)
    except Exception as e:
        print(f"Error loading/running model {model_id}: {e}", flush=True)
        import traceback
        traceback.print_exc()
        return None

    if resp:
        if print_output:
            return resp

        # consume silently
        if isinstance(resp, StreamingResponse):
            async for _chunk in resp.body_iterator:
                pass
        return None

    return None
async def consume_stream(resp: StreamingResponse):
    """Read and print all chunks from a StreamingResponse."""
    async for chunk in resp.body_iterator:
        if isinstance(chunk, (bytes, bytearray)):
            print(chunk.decode(errors="replace"), end="", flush=True)
        else:
            print(str(chunk), end="", flush=True)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Safe HF text-generation wrapper")
    parser.add_argument("--model_id", type=str, required=True)
    parser.add_argument("--template", type=str, required=True)
    parser.add_argument("--defense_type", type=str, required=False, default="None")
    parser.add_argument("--prompt_type", required=True)
    args = parser.parse_args()

    # Attack handlers registry: add new attack types here as small functions
    if(args.prompt_type == "chain-of-questions"):
        async def handler():
            async for chunk in run_chain_of_questions_attack(args.model_id, args.template, args.defense_type):
                print(chunk.decode(errors="replace"), end="", flush=True)
        asyncio.run(handler())
    
    elif(args.prompt_type == "role-playing"):
        async def handler():
            async for chunk in run_role_playing_attack(args.model_id, args.template, args.defense_type):
                print(chunk.decode(errors="replace"), end="", flush=True)
        asyncio.run(handler())

    elif(args.prompt_type == "DAN"):
        async def handler():
            async for chunk in run_dan_attack(args.model_id, args.template, args.defense_type):
                print(chunk.decode(errors="replace"), end="", flush=True)
        asyncio.run(handler())
    
    elif(args.prompt_type == "ascii-art-jailbreak"):
        async def handler():
            async for chunk in run_ascii_art_jailbreak_attack(args.model_id, args.template, args.defense_type):
                print(chunk.decode(errors="replace"), end="", flush=True)
        asyncio.run(handler())
    
    elif(args.prompt_type == "neurostrike"):
        async def handler():
            async for chunk in run_neurostrike_attack(args.model_id, args.template, args.defense_type):
                print(chunk.decode(errors="replace"), end="", flush=True)
        asyncio.run(handler())