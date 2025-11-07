# main.py
import os
import sys
import asyncio
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

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
async def _run_script_and_stream(cmd: list[str], env: dict | None = None) -> AsyncGenerator[bytes, None]:
    # start subprocess
    proc = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.STDOUT,
        env=env,
        # no shell
    )

    assert proc.stdout is not None
    # read line-by-line (or chunk-by-chunk) while process runs
    try:
        while True:
            line = await proc.stdout.readline()
            if not line:  # EOF
                break
            # yield raw bytes to StreamingResponse
            yield line
        # wait for process to finish
        await proc.wait()
        # optionally yield a final marker
        yield b"\n[PROCESS ENDED]\n"
    except asyncio.CancelledError:
        # if client disconnects, try to terminate subprocess
        try:
            proc.terminate()
        except Exception:
            pass
        raise

@app.post("/api/prompt/stream")
async def prompt_stream(request: PromptRequest):
    # Only run this if the attack matches
    if request.attack != "role-playing-social-engeneering":
        # return a single small stream
        async def just_return() -> AsyncGenerator[bytes, None]:
            yield b"Not a role-playing attack. No script run.\n"
        return StreamingResponse(just_return(), media_type="text/plain; charset=utf-8")

    # Build command using the same Python interpreter
    cmd = [
        sys.executable,
        "./attacks/promptInjection.py",
        "--model_id", request.model,
        "--template", request.prompt
    ]

    # ensure python subprocess does not buffer output
    env = os.environ.copy()
    env["PYTHONUNBUFFERED"] = "1"

    generator = _run_script_and_stream(cmd, env=env)
    # StreamingResponse sends bytes to the client as they are yielded
    return StreamingResponse(generator, media_type="text/plain; charset=utf-8")
