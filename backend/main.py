# main.py
import os
import sys
import asyncio
from typing import AsyncGenerator
import unicodedata

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from defenses.defense_manager import *
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class PromptRequest(BaseModel):
    prompt: str
    attack: str
    defense: str
    model: str

# helper: async generator that runs the script and yields chunks of stdout
async def _run_script_and_stream(cmd: list[str], numOfPrompts: int, env: dict | None = None) -> AsyncGenerator[bytes, None]:
    proc = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.STDOUT,
        env=env,
    )

    assert proc.stdout is not None

    try:
        currPrompt = 0
        while True:
            line = await proc.stdout.readline()
            if not line:  # EOF
                break

            # decode bytes to string
            decoded = line.decode("utf-8", errors="ignore").strip()

            if decoded.startswith("[PROGRESS] "):
                try:
                    # extract the number after [PROGRESS]
                    progress_val = float(decoded[len("[PROGRESS] "):].strip())

                    # normalize if multiple prompts
                    absolute_progress = currPrompt * 100 / numOfPrompts + progress_val / numOfPrompts

                    if(progress_val >= 99.99):
                        currPrompt += 1
                    
                    # reformat as string
                    new_line = f"[PROGRESS] {absolute_progress:.2f}\n"
                    # convert back to bytes for StreamingResponse
                    yield new_line.encode("utf-8")
                except ValueError:
                    # if parse fails, just forward original line
                    yield line
            else:
                # send original stdout lines
                yield line

        await proc.wait()

    except asyncio.CancelledError:
        try:
            proc.terminate()
        except Exception:
            pass
        raise

@app.post("/api/prompt/stream")
async def prompt_stream(request: PromptRequest):
    # Defence
    # Apply defense dynamically via defense manager
    blocked_response = await apply_defense(request.defense, request.prompt)
    if blocked_response:
        return blocked_response


    # Attack
    if (request.attack == "role-playing-social-engeneering" or request.attack == "chain-of-questions"):
        # Build command using the same Python interpreter
        cmd = [
            sys.executable,
            "./attacks/promptInjection.py",
            "--model_id", request.model,
            "--template", request.prompt,
            "--prompt_type", request.attack
        ]

        # ensure python subprocess does not buffer output
        env = os.environ.copy()
        env["PYTHONUNBUFFERED"] = "1"
        numOfPrompts = 1
        if (request.attack == "chain-of-questions"):
            numOfPrompts = 9
        generator = _run_script_and_stream(cmd, env=env, numOfPrompts=numOfPrompts)
        # StreamingResponse sends bytes to the client as they are yielded
        return StreamingResponse(generator, media_type="text/plain; charset=utf-8")

    if (request.attack == "fcb-bias_guided"):
        # Build command using the same Python interpreter
        cmd = [
            sys.executable,
            "./attacks/FCB.py",
            "--model_id", request.model,
            "--template", request.prompt
        ]
        # ensure python subprocess does not buffer output
        env = os.environ.copy()
        env["PYTHONUNBUFFERED"] = "1"
        generator = _run_script_and_stream(cmd, env=env, numOfPrompts=1)
        # StreamingResponse sends bytes to the client as they are yielded
        return StreamingResponse(generator, media_type="text/plain; charset=utf-8")

    # return a single small stream
    async def just_return() -> AsyncGenerator[bytes, None]:
        yield b"No script run.\n"
    return StreamingResponse(just_return(), media_type="text/plain; charset=utf-8")
