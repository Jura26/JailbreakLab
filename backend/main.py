# main.py
import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import asyncio
from typing import AsyncGenerator
import torch

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from defenses.defense_manager import *
app = FastAPI()

# CORS middleware must be added before routes
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add middleware to log all requests
@app.middleware("http")
async def log_requests(request: Request, call_next):
    print(f"{request.method} {request.url.path} from {request.client.host}")
    try:
        response = await call_next(request)
        print(f"Response status: {response.status_code}")
        return response
    except Exception as e:
        print(f"Error processing request: {e}")
        import traceback
        traceback.print_exc()
        raise

@app.get("/")
async def root():
    return {"status": "ok", "message": "Backend is running"}

@app.options("/api/prompt/stream")
async def options_prompt_stream():
    return {"status": "ok"}

class PromptRequest(BaseModel):
    prompt: str
    attack: str
    defense: str
    model: str

# Registry for prompt-injection attack scripts and metadata
PROMPT_INJECTION_ATTACKS = {
    "role-playing-social-engeneering": {
        "num_prompts": 1,
    },
    "chain-of-questions": {
        "num_prompts": 9,
    },
    "DAN": {
        "num_prompts": 2,
    },
    "ascii-art-jailbreak": {
        "num_prompts": 2,
    }
}

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
        # track last yielded absolute progress so we never go backwards
        last_yielded_progress = -1.0

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

                    # normalize if multiple prompts (weighted per-prompt progress)
                    absolute_progress = currPrompt * 100.0 / numOfPrompts + progress_val / numOfPrompts

                    # ensure monotonic non-decreasing progress (clamp to last yielded)
                    if absolute_progress < last_yielded_progress:
                        absolute_progress = last_yielded_progress

                    # if this prompt reports completion, advance the "currPrompt" index
                    if progress_val >= 99.99:
                        currPrompt = min(currPrompt + 1, numOfPrompts)

                    # reformat as string
                    new_line = f"[PROGRESS] {absolute_progress:.2f}\n"
                    # convert back to bytes for StreamingResponse
                    yield new_line.encode("utf-8")

                    # update last yielded
                    last_yielded_progress = absolute_progress
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
    print(f"POST received - Model: {request.model}, Attack: {request.attack}, Defense: {request.defense}")
    
    # Send GPU info as first yield for all attacks
    async def gpu_info_and_stream(generator):
        # Send GPU info IMMEDIATELY before waiting for generator
        if torch.cuda.is_available():
            gpu_name = torch.cuda.get_device_name(0)
            yield f"GPU name: {gpu_name}\n".encode("utf-8")
        else:
            yield b"No compatible GPU detected\n"
        
        # Now stream the rest from the generator
        async for chunk in generator:
            yield chunk

    # Attack: prompt-injection flows use the same script but different modes/lengths.
    if request.attack in PROMPT_INJECTION_ATTACKS:
        entry = PROMPT_INJECTION_ATTACKS[request.attack]

        # Build command using the same Python interpreter
        cmd = [
            sys.executable,
            "./attacks/promptInjection.py",
            "--model_id", request.model,
            "--template", request.prompt,
            "--prompt_type", request.attack,
            "--defense_type", request.defense
        ]

        # ensure python subprocess does not buffer output
        env = os.environ.copy()
        env["PYTHONUNBUFFERED"] = "1"

        numOfPrompts = int(entry.get("num_prompts", 1))
        generator = _run_script_and_stream(cmd, numOfPrompts=numOfPrompts, env=env)
        # StreamingResponse sends bytes to the client as they are yielded
        return StreamingResponse(gpu_info_and_stream(generator), media_type="text/plain; charset=utf-8")

    if (request.attack == "fcb-bias_guided"):
        # Build command using the same Python interpreter
        cmd = [
            sys.executable,
            "./attacks/FCB.py",
            "--model_id", request.model,
            "--template", request.prompt,
            "--defense_type", request.defense
        ]
        # ensure python subprocess does not buffer output
        env = os.environ.copy()
        env["PYTHONUNBUFFERED"] = "1"
        generator = _run_script_and_stream(cmd, env=env, numOfPrompts=1)
        # StreamingResponse sends bytes to the client as they are yielded
        return StreamingResponse(gpu_info_and_stream(generator), media_type="text/plain; charset=utf-8")

    if(request.attack == "none"):
        # No special attack selected → go through defenses + model directly
        async def stream_with_gpu_info():
            # Send GPU info FIRST before any processing
            if torch.cuda.is_available():
                gpu_name = torch.cuda.get_device_name(0)
                yield f"GPU name: {gpu_name}\n".encode("utf-8")
            else:
                yield b"No compatible GPU detected\n"
            
            # Now do the expensive work
            try:
                print(f"Starting model load: {request.model}")
                blocked, resp = await apply_defense(
                    defense=request.defense,
                    prompt=request.prompt,
                    model_id=request.model,
                    device="cuda" if torch.cuda.is_available() else "cpu",
                    generation_options={},
                    session_id=None,
                )
                print(f"Model processing complete, blocked: {blocked}")
                
                # Stream the response
                if resp and isinstance(resp, StreamingResponse):
                    async for chunk in resp.body_iterator:
                        yield chunk
                elif resp:
                    yield str(resp).encode("utf-8")
            except Exception as e:
                print(f"ERROR in model processing: {e}")
                import traceback
                traceback.print_exc()
                yield f"Error: {str(e)}\n".encode("utf-8")
                yield b"Model loading failed. Check backend logs.\n"
        
        return StreamingResponse(stream_with_gpu_info(), media_type="text/plain; charset=utf-8")

    # return a single small stream
    async def just_return() -> AsyncGenerator[bytes, None]:
        yield b"No script run.\n"
    return StreamingResponse(just_return(), media_type="text/plain; charset=utf-8")
