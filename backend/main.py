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

from defenses.defense_manager import apply_defense, get_generate_streaming_call_count
from history_cache import clear_history
from database import (
    log_bert_statistic, 
    get_bert_statistics, 
    get_unique_values,
    calculate_attack_success_rate,
    calculate_defense_bypass_rate,
    calculate_query_budget_metrics,
    calculate_refusal_metrics,
    calculate_tool_and_leakage_metrics,
    detect_data_leakage,
    calculate_additional_metrics
)

from model import detect_attack_success, detect_prompt_attack, detect_tool_misuse_from_prompt_and_response, detect_prompt_attack, detect_tool_misuse_from_prompt_and_response

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
    async def gpu_info_and_stream(generator, session_id_to_clear: str = None, model_type: str = "", attack_type: str = "", defense_type: str = "", prompt: str = ""):
        import time
        start_time = time.time()
        query_count = 0
        token_count = 0
        refusal_type = None
        was_blocked = False  # Initialize to False
        logged_to_db = False  # Track if we've already logged this session
        
        # Send GPU info IMMEDIATELY before waiting for generator
        if torch.cuda.is_available():
            gpu_name = torch.cuda.get_device_name(0)
            yield f"GPU name: {gpu_name}\n".encode("utf-8")
        else:
            yield b"No compatible GPU detected\n"

        # Now stream the rest from the generator
        try:
            async for chunk in generator:
                # Track metrics
                query_count += 1  # Simple count, could be more sophisticated
                decoded = chunk.decode("utf-8") if isinstance(chunk, bytes) else str(chunk)
                token_count += len(decoded.split())  # Rough token count
                
                # Check for metadata markers and extract values
                if "[TOKEN_COUNT]" in decoded:
                    try:
                        # Extract token count from metadata
                        token_count_str = decoded.split("[TOKEN_COUNT] ")[1].strip()
                        token_count = int(token_count_str)
                    except (ValueError, IndexError):
                        pass
                
                if "[REFUSAL_TYPE]" in decoded:
                    try:
                        # Extract refusal type from metadata
                        refusal_type = decoded.split("[REFUSAL_TYPE] ")[1].strip()
                    except IndexError:
                        pass
                if "BLOCKED_PROMPT" in decoded:
                    was_blocked = True
                
                # Check for attack success marker and log to database
                try:
                    if "[ATTACK_SUCCESS]" in decoded and not logged_to_db:
                        print(f"🔄 DEBUG: Detected [ATTACK_SUCCESS] marker, preparing to log to database...")
                        success = "true" in decoded.lower()
                        time_to_bypass = time.time() - start_time  # Always calculate total time spent
                        # Use actual generate_streaming call count instead of chunk count
                        actual_query_count = get_generate_streaming_call_count(session_id_to_clear) if session_id_to_clear else query_count
                        print(f"🔄 DEBUG: Retrieved query count for session {session_id_to_clear}: {actual_query_count} (type: {type(actual_query_count)})")
                        
                        # Analyze prompt for attack indicators and tool misuse
                        is_attack_prompt, prompt_confidence, prompt_label = detect_prompt_attack(prompt)
                        tool_misuse_detected = detect_tool_misuse_from_prompt_and_response(
                            prompt, decoded, [], success  # Pass original attack success
                        )
                        
                        # Detect data leakage in the response
                        data_leakage_detected = detect_data_leakage(decoded)
                        
                        print(f"🔄 DEBUG: Calling log_bert_statistic with session_id={session_id_to_clear}, attack_success={success}")
                        log_result = log_bert_statistic(
                            session_id=session_id_to_clear or "",
                            model_type=model_type,
                            attack_type=attack_type,
                            defense_type=defense_type,
                            attack_success=success,
                            was_blocked=was_blocked,
                            time_to_bypass=time_to_bypass,
                            query_count=actual_query_count,
                            token_count=token_count,
                            refusal_type=refusal_type,
                            tool_misuse=tool_misuse_detected,
                            data_leakage=data_leakage_detected,
                            prompt_toxicity_score=prompt_confidence,
                            # Add other metrics as available
                        )
                        print(f"✅ DEBUG: log_bert_statistic returned: {log_result}")
                        logged_to_db = True
                except Exception as e:
                    print(f"❌ DEBUG: Error in database logging section: {e}")
                    import traceback
                    traceback.print_exc()
                
                # Don't yield metadata markers to hide them from display
                if not ("[TOKEN_COUNT]" in decoded or "[REFUSAL_TYPE]" in decoded):
                    yield chunk
                
            # Log failed attacks at the end if we haven't logged yet
            if not logged_to_db and session_id_to_clear:
                try:
                    print(f"🔄 DEBUG: Attack completed without success marker, logging failed attack...")
                    time_to_bypass = time.time() - start_time  # Total time spent on the attack attempt
                    actual_query_count = get_generate_streaming_call_count(session_id_to_clear)
                    print(f"🔄 DEBUG: Retrieved query count for failed attack session {session_id_to_clear}: {actual_query_count} (type: {type(actual_query_count)})")
                    
                    # Analyze prompt for attack indicators
                    is_attack_prompt, prompt_confidence, prompt_label = detect_prompt_attack(prompt)
                    
                    # For failed attacks, we don't have the full response text, so we can't check for tool misuse or data leakage
                    # Use basic analysis
                    if is_attack_prompt:
                        final_attack_success = False  # Attack prompt was blocked
                    else:
                        final_attack_success = False  # Regular prompt, no attack success
                    
                    print(f"🔄 DEBUG: Calling log_bert_statistic for failed attack with session_id={session_id_to_clear}, attack_success={final_attack_success}")
                    log_result = log_bert_statistic(
                        session_id=session_id_to_clear,
                        model_type=model_type,
                        attack_type=attack_type,
                        defense_type=defense_type,
                        attack_success=final_attack_success,
                        was_blocked=True,
                        time_to_bypass=time_to_bypass,
                        query_count=actual_query_count,
                        token_count=token_count,
                        refusal_type=refusal_type,
                        tool_misuse=False,  # Can't detect without full response
                        data_leakage=False,  # Can't detect without full response
                        prompt_toxicity_score=prompt_confidence,
                    )
                    print(f"✅ DEBUG: log_bert_statistic for failed attack returned: {log_result}")
                except Exception as e:
                    print(f"❌ DEBUG: Error logging failed attack: {e}")
                    import traceback
                    traceback.print_exc()
                    
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
        return StreamingResponse(gpu_info_and_stream(generator, session_id, request.model, request.attack, request.defense, request.prompt), media_type="text/plain; charset=utf-8")
    
    if request.attack == "chain-of-questions":
        session_id = uuid.uuid4().hex  # unique session per attack
        generator = run_chain_of_questions_attack(
            model_id=request.model,
            template=request.prompt,
            defense=request.defense,
            session_id=session_id
        )
        return StreamingResponse(gpu_info_and_stream(generator, session_id, request.model, request.attack, request.defense, request.prompt), media_type="text/plain; charset=utf-8")
    
    if request.attack == "DAN":
        session_id = uuid.uuid4().hex  # unique session per attack
        generator = run_dan_attack(
            model_id=request.model,
            template=request.prompt,
            defense=request.defense,
            session_id=session_id
        )
        return StreamingResponse(gpu_info_and_stream(generator, session_id, request.model, request.attack, request.defense, request.prompt), media_type="text/plain; charset=utf-8")
    
    if request.attack == "ascii-art-jailbreak":
        session_id = uuid.uuid4().hex  # unique session per attack
        generator = run_ascii_art_jailbreak_attack(
            model_id=request.model,
            template=request.prompt,
            defense=request.defense,
            session_id=session_id
        )
        return StreamingResponse(gpu_info_and_stream(generator, session_id, request.model, request.attack, request.defense, request.prompt), media_type="text/plain; charset=utf-8")

    if request.attack == "neurostrike":
        session_id = uuid.uuid4().hex  # unique session per attack
        generator = run_neurostrike_attack(
            model_id=request.model,
            template=request.prompt,
            defense=request.defense,
            session_id=session_id
        )
        return StreamingResponse(gpu_info_and_stream(generator, session_id, request.model, request.attack, request.defense, request.prompt), media_type="text/plain; charset=utf-8")

    # FCB attack now runs in-process (reuses model cache)
    if request.attack == "fcb-bias_guided":
        session_id = uuid.uuid4().hex  # unique session per attack
        generator = run_fcb_attack(
            model_id=request.model,
            template=request.prompt,
            defense=request.defense,
            session_id=session_id
        )
        return StreamingResponse(gpu_info_and_stream(generator, session_id, request.model, request.attack, request.defense, request.prompt), media_type="text/plain; charset=utf-8")
    
    # GCG attack - gradient-based adversarial suffix optimization
    if request.attack == "gcg-gradient":
        session_id = uuid.uuid4().hex  # unique session per attack
        generator = run_gcg_attack(
            model_id=request.model,
            template=request.prompt,
            defense=request.defense,
            session_id=session_id
        )
        return StreamingResponse(gpu_info_and_stream(generator, session_id, request.model, request.attack, request.defense, request.prompt), media_type="text/plain; charset=utf-8")

    if(request.attack == "none"):
        # No special attack selected → go through defenses + model directly
        session_id = uuid.uuid4().hex  # unique session per request
        async def stream_with_gpu_info():
            import time
            start_time = time.time()
            query_count = 0
            token_count = 0
            refusal_type = None
            logged_to_db = False  # Track if we've already logged this session
            
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
                        query_count += 1
                        decoded = chunk.decode("utf-8") if isinstance(chunk, bytes) else str(chunk)
                        token_count += len(decoded.split())
                        
                        # Check for metadata markers and extract values
                        if "[TOKEN_COUNT]" in decoded:
                            try:
                                # Extract token count from metadata
                                token_count_str = decoded.split("[TOKEN_COUNT] ")[1].strip()
                                token_count = int(token_count_str)
                            except (ValueError, IndexError):
                                pass
                        
                        if "[REFUSAL_TYPE]" in decoded:
                            try:
                                # Extract refusal type from metadata
                                refusal_type = decoded.split("[REFUSAL_TYPE] ")[1].strip()
                            except IndexError:
                                pass
                        
                        # Check for attack success marker and log to database
                        try:
                            if "[ATTACK_SUCCESS]" in decoded and not logged_to_db:
                                logged_to_db = True  # Set flag first to prevent double logging
                                print(f"🔄 DEBUG: Detected [ATTACK_SUCCESS] marker in stream_with_gpu_info, preparing to log to database...")
                                success = "true" in decoded.lower()
                                time_to_bypass = time.time() - start_time  # Always calculate total time spent
                                # Use actual generate_streaming call count instead of chunk count
                                actual_query_count = get_generate_streaming_call_count(session_id) if session_id else query_count
                                print(f"🔄 DEBUG: Retrieved query count for session {session_id}: {actual_query_count}")
                                
                                # Analyze prompt for attack indicators and tool misuse
                                is_attack_prompt, prompt_confidence, prompt_label = detect_prompt_attack(request.prompt)
                                tool_misuse_detected = detect_tool_misuse_from_prompt_and_response(
                                    request.prompt, decoded, [], success  # Pass original attack success
                                )
                                
                                # Detect data leakage in the response
                                data_leakage_detected = detect_data_leakage(decoded)
                                
                                # Adjust attack success based on prompt analysis
                                if is_attack_prompt == False:
                                    final_attack_success = False  # Block non attack prompts
                                else:
                                    final_attack_success = success
                               
                                print(f"🔄 DEBUG: Calling log_bert_statistic with session_id={session_id}, attack_success={final_attack_success}")
                                log_result = log_bert_statistic(
                                    session_id=session_id,
                                    model_type=request.model,
                                    attack_type=request.attack,
                                    defense_type=request.defense,
                                    attack_success=final_attack_success,
                                    was_blocked=blocked,
                                    time_to_bypass=time_to_bypass,
                                    query_count=actual_query_count,
                                    token_count=token_count,
                                    refusal_type=refusal_type,
                                    tool_misuse=tool_misuse_detected,
                                    data_leakage=data_leakage_detected,
                                    prompt_toxicity_score=prompt_confidence,
                                )
                                print(f"✅ DEBUG: log_bert_statistic returned: {log_result}")
                        except Exception as e:
                            print(f"❌ DEBUG: Error in database logging section (stream_with_gpu_info): {e}")
                            import traceback
                            traceback.print_exc()
                        
                        # Don't yield metadata markers to hide them from display
                        if not ("[TOKEN_COUNT]" in decoded or "[REFUSAL_TYPE]" in decoded):
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
            
            # Log failed/blocked cases if not already logged
            if not logged_to_db:
                try:
                    logged_to_db = True  # Set flag first to prevent double logging
                    time_to_bypass = time.time() - start_time
                    actual_query_count = get_generate_streaming_call_count(session_id)
                    
                    is_attack_prompt, prompt_confidence, prompt_label = detect_prompt_attack(request.prompt)
                    
                    if blocked:
                        final_attack_success = False
                        was_blocked = True
                    else:
                        final_attack_success = False
                        was_blocked = False
                    
                    log_result = log_bert_statistic(
                        session_id=session_id,
                        model_type=request.model,
                        attack_type=request.attack,
                        defense_type=request.defense,
                        attack_success=final_attack_success,
                        was_blocked=was_blocked,
                        time_to_bypass=time_to_bypass,
                        query_count=actual_query_count,
                        token_count=token_count,
                        refusal_type=refusal_type,
                        tool_misuse=False,
                        data_leakage=False,
                        prompt_toxicity_score=prompt_confidence,
                    )
                    print(f"✅ DEBUG: log_bert_statistic for 'none' failed/blocked returned: {log_result}")
                except Exception as e:
                    print(f"❌ DEBUG: Error logging 'none' failed/blocked: {e}")
                    import traceback
                    traceback.print_exc()
        
        return StreamingResponse(stream_with_gpu_info(), media_type="text/plain; charset=utf-8")

    # return a single small stream
    async def just_return() -> AsyncGenerator[bytes, None]:
        yield b"No script run.\n"
    return StreamingResponse(just_return(), media_type="text/plain; charset=utf-8")


# Statistics API endpoints
@app.get("/api/statistics")
async def get_statistics(attack_type: str = "all", defense_type: str = "all"):
    """Fetch statistics with optional filters."""
    data = get_bert_statistics(attack_type=attack_type, defense_type=defense_type)
    return {"data": data}


@app.get("/api/statistics/filters")
async def get_filter_options():
    """Get unique values for filter dropdowns."""
    return get_unique_values()


@app.get("/api/statistics/asr")
async def get_attack_success_rate(attack_type: str = "all", defense_type: str = "all", model_type: str = "all"):
    """Get Attack Success Rate metrics."""
    return calculate_attack_success_rate(attack_type=attack_type, defense_type=defense_type, model_type=model_type)


@app.get("/api/statistics/defense-bypass")
async def get_defense_bypass_rate(defense_type: str = "all", model_type: str = "all"):
    """Get Defense Bypass Rate metrics."""
    return calculate_defense_bypass_rate(defense_type=defense_type, model_type=model_type)


@app.get("/api/statistics/query-budget")
async def get_query_budget_metrics(attack_type: str = "all", defense_type: str = "all", model_type: str = "all"):
    """Get Query/Attempt Budget metrics."""
    return calculate_query_budget_metrics(attack_type=attack_type, defense_type=defense_type, model_type=model_type)


@app.get("/api/statistics/refusal")
async def get_refusal_metrics(attack_type: str = "all", defense_type: str = "all", model_type: str = "all"):
    """Get Refusal and Safe Completion metrics."""
    return calculate_refusal_metrics(attack_type=attack_type, defense_type=defense_type, model_type=model_type)


@app.get("/api/statistics/tool-leakage")
async def get_tool_and_leakage_metrics(attack_type: str = "all", defense_type: str = "all", model_type: str = "all"):
    """Get Tool misuse and Data leakage metrics."""
    return calculate_tool_and_leakage_metrics(attack_type=attack_type, defense_type=defense_type, model_type=model_type)


@app.get("/api/statistics/additional")
async def get_additional_metrics(attack_type: str = "all", defense_type: str = "all", model_type: str = "all"):
    """Get additional metrics like toxicity scores, etc."""
    return calculate_additional_metrics(attack_type=attack_type, defense_type=defense_type, model_type=model_type)
