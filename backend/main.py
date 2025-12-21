# main.py
import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import asyncio
from typing import AsyncGenerator
import uuid
import torch

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from defenses.defense_manager import *
from history_cache import clear_history
from database import log_bert_statistic

# Import attack functions for in-process execution (no subprocess)
from attacks.promptInjection import (
    run_role_playing_attack,
    run_chain_of_questions_attack,
    run_dan_attack,
    run_ascii_art_jailbreak_attack,
)
from attacks.FCB import run_fcb_attack
from attacks.neuroStrike.neuroStrike import run_neurostrike_attack
from attacks.GCG import run_gcg_attack

app = FastAPI()

# CORS middleware must be added before routes
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
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

@app.post("/api/test/classifier")
async def test_classifier(request: Request):
    """Test endpoint for attack success detection."""
    from model import detect_attack_success
    
    data = await request.json()
    text = data.get("text", "")
    
    if not text:
        return {"error": "No text provided"}
    
    success, confidence, label = detect_attack_success(text)
    
    return {
        "text_preview": text[:200] + "..." if len(text) > 200 else text,
        "attack_success": success,
        "confidence": confidence,
        "label": label,
        "interpretation": "Attack succeeded - model provided harmful content" if success else "Attack failed - model refused or gave safe response"
    }

class PromptRequest(BaseModel):
    prompt: str
    attack: str
    defense: str
    model: str

# helper: async generator that runs the script and yields chunks of stdout (used for FCB only now)
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
    async def gpu_info_and_stream(generator, session_id_to_clear: str = None, model_type: str = "", attack_type: str = "", defense_type: str = ""):
        # Send GPU info IMMEDIATELY before waiting for generator
        if torch.cuda.is_available():
            gpu_name = torch.cuda.get_device_name(0)
            yield f"GPU name: {gpu_name}\n".encode("utf-8")
        else:
            yield b"No compatible GPU detected\n"

        # Now stream the rest from the generator
        try:
            async for chunk in generator:
                # Check for attack success marker and log to database
                try:
                    decoded = chunk.decode("utf-8") if isinstance(chunk, bytes) else str(chunk)
                    if "[ATTACK_SUCCESS]" in decoded:
                        success = "true" in decoded.lower()
                        log_bert_statistic(
                            session_id=session_id_to_clear or "",
                            model_type=model_type,
                            attack_type=attack_type,
                            defense_type=defense_type,
                            attack_success=success,
                            was_blocked=False
                        )
                except Exception as e:
                    print(f"Error logging to database: {e}")
                yield chunk
        finally:
            # Cleanup history after stream finishes
            if session_id_to_clear:
                try:
                    clear_history(session_id_to_clear)
                except Exception as e:
                    print(f"Error clearing history for {session_id_to_clear}: {e}")

    # Attack: prompt-injection flows - now run in-process (no subprocess)
    if request.attack == "role-playing-social-engeneering":
        session_id = uuid.uuid4().hex  # unique session per attack
        generator = run_role_playing_attack(
            model_id=request.model,
            template=request.prompt,
            defense=request.defense,
            session_id=session_id
        )
        return StreamingResponse(gpu_info_and_stream(generator, session_id, request.model, request.attack, request.defense), media_type="text/plain; charset=utf-8")
    
    if request.attack == "chain-of-questions":
        session_id = uuid.uuid4().hex  # unique session per attack
        generator = run_chain_of_questions_attack(
            model_id=request.model,
            template=request.prompt,
            defense=request.defense,
            session_id=session_id
        )
        return StreamingResponse(gpu_info_and_stream(generator, session_id, request.model, request.attack, request.defense), media_type="text/plain; charset=utf-8")
    
    if request.attack == "DAN":
        session_id = uuid.uuid4().hex  # unique session per attack
        generator = run_dan_attack(
            model_id=request.model,
            template=request.prompt,
            defense=request.defense,
            session_id=session_id
        )
        return StreamingResponse(gpu_info_and_stream(generator, session_id, request.model, request.attack, request.defense), media_type="text/plain; charset=utf-8")
    
    if request.attack == "ascii-art-jailbreak":
        session_id = uuid.uuid4().hex  # unique session per attack
        generator = run_ascii_art_jailbreak_attack(
            model_id=request.model,
            template=request.prompt,
            defense=request.defense,
            session_id=session_id
        )
        return StreamingResponse(gpu_info_and_stream(generator, session_id, request.model, request.attack, request.defense), media_type="text/plain; charset=utf-8")

    if request.attack == "neurostrike":
        session_id = uuid.uuid4().hex  # unique session per attack
        generator = run_neurostrike_attack(
            model_id=request.model,
            template=request.prompt,
            defense=request.defense,
            session_id=session_id
        )
        return StreamingResponse(gpu_info_and_stream(generator, session_id, request.model, request.attack, request.defense), media_type="text/plain; charset=utf-8")

    # FCB attack now runs in-process (reuses model cache)
    if request.attack == "fcb-bias_guided":
        session_id = uuid.uuid4().hex  # unique session per attack
        generator = run_fcb_attack(
            model_id=request.model,
            template=request.prompt,
            defense=request.defense,
            session_id=session_id
        )
        return StreamingResponse(gpu_info_and_stream(generator, session_id, request.model, request.attack, request.defense), media_type="text/plain; charset=utf-8")
    
    # GCG attack - gradient-based adversarial suffix optimization
    if request.attack == "gcg-gradient":
        session_id = uuid.uuid4().hex  # unique session per attack
        generator = run_gcg_attack(
            model_id=request.model,
            template=request.prompt,
            defense=request.defense,
            session_id=session_id
        )
        return StreamingResponse(gpu_info_and_stream(generator, session_id, request.model, request.attack, request.defense), media_type="text/plain; charset=utf-8")

    if(request.attack == "none"):
        # No special attack selected → go through defenses + model directly
        session_id = uuid.uuid4().hex  # unique session per request
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
                    session_id=session_id,
                )
                print(f"Model processing complete, blocked: {blocked}")
                
                # Stream the response
                if resp and isinstance(resp, StreamingResponse):
                    async for chunk in resp.body_iterator:
                        # Check for attack success marker and log to database
                        try:
                            decoded = chunk.decode("utf-8") if isinstance(chunk, bytes) else str(chunk)
                            if "[ATTACK_SUCCESS]" in decoded:
                                success = "true" in decoded.lower()
                                log_bert_statistic(
                                    session_id=session_id,
                                    model_type=request.model,
                                    attack_type=request.attack,
                                    defense_type=request.defense,
                                    attack_success=success,
                                    was_blocked=blocked
                                )
                        except Exception as e:
                            print(f"Error logging to database: {e}")
                        yield chunk
                elif resp:
                    yield str(resp).encode("utf-8")
            except Exception as e:
                print(f"ERROR in model processing: {e}")
                import traceback
                traceback.print_exc()
                yield f"Error: {str(e)}\n".encode("utf-8")
                yield b"Model loading failed. Check backend logs.\n"
            finally:
                # Cleanup history
                try:
                    clear_history(session_id)
                except Exception as e:
                    print(f"Error clearing history for {session_id}: {e}")
        
        return StreamingResponse(stream_with_gpu_info(), media_type="text/plain; charset=utf-8")

    # return a single small stream
    async def just_return() -> AsyncGenerator[bytes, None]:
        yield b"No script run.\n"
    return StreamingResponse(just_return(), media_type="text/plain; charset=utf-8")
