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

from attacks.attack_manager import run_attack

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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

@app.post("/api/prompt/stream")
async def prompt_stream(request: PromptRequest):
    print(f"POST received - Model: {request.model}, Attack: {request.attack}, Defense: {request.defense}")
    
    # Stream with GPU info
    async def gpu_info_and_stream(generator, session_id_to_clear: str = None, model_type: str = "", attack_type: str = "", defense_type: str = "", prompt: str = ""):
        import time
        start_time = time.time()
        query_count = 0
        token_count = 0
        refusal_type = None
        was_blocked = False  # Initialize to False
        logged_to_db = False  # Track if we've already logged this session
        
        # Send GPU info
        if torch.cuda.is_available():
            gpu_name = torch.cuda.get_device_name(0)
            yield f"GPU name: {gpu_name}\n".encode("utf-8")
        else:
            yield b"No compatible GPU detected\n"

        # Stream response
        try:
            async for chunk in generator:
                # Track metrics
                query_count += 1  # Simple count, could be more sophisticated
                decoded = chunk.decode("utf-8") if isinstance(chunk, bytes) else str(chunk)
                token_count += len(decoded.split())  # Rough token count
                
                # Extract metadata
                if "[TOKEN_COUNT]" in decoded:
                    try:
                        token_count_str = decoded.split("[TOKEN_COUNT] ")[1].strip()
                        token_count = int(token_count_str)
                    except (ValueError, IndexError):
                        pass
                
                if "[REFUSAL_TYPE]" in decoded:
                    try:
                        refusal_type = decoded.split("[REFUSAL_TYPE] ")[1].strip()
                    except IndexError:
                        pass
                if "BLOCKED_PROMPT" in decoded:
                    was_blocked = True
                
                # Log attack success
                try:
                    if "[ATTACK_SUCCESS]" in decoded and not logged_to_db:
                        success = "true" in decoded.lower()
                        time_to_bypass = time.time() - start_time  # Always calculate total time spent
                        # Use actual generate_streaming call count instead of chunk count
                        actual_query_count = get_generate_streaming_call_count(session_id_to_clear) if session_id_to_clear else query_count
                        
                        # Analyze prompt and response
                        is_attack_prompt, prompt_confidence, prompt_label = detect_prompt_attack(prompt)
                        tool_misuse_detected = detect_tool_misuse_from_prompt_and_response(
                            prompt, decoded, [], success  # Pass original attack success
                        )
                        
                        # Detect data leakage
                        data_leakage_detected = detect_data_leakage(decoded)
                        
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
                        )
                        logged_to_db = True
                except Exception as e:
                    import traceback
                    traceback.print_exc()
                
                # Filter metadata
                if not ("[TOKEN_COUNT]" in decoded or "[REFUSAL_TYPE]" in decoded):
                    yield chunk
                
            # Log failed attacks
            if not logged_to_db and session_id_to_clear:
                try:
                    time_to_bypass = time.time() - start_time  # Total time spent on the attack attempt
                    actual_query_count = get_generate_streaming_call_count(session_id_to_clear)
                    
                    # Analyze prompt
                    is_attack_prompt, prompt_confidence, prompt_label = detect_prompt_attack(prompt)
                    
                    # Basic analysis
                    if is_attack_prompt:
                        final_attack_success = False  # Attack prompt was blocked
                    else:
                        final_attack_success = False  # Regular prompt, no attack success
                    
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
                except Exception as e:
                    import traceback
                    traceback.print_exc()
                    
        finally:
            # Cleanup history
            if session_id_to_clear:
                try:
                    clear_history(session_id_to_clear)
                except Exception as e:
                    print(f"Error clearing history for {session_id_to_clear}: {e}")

    # Handle attacks
    if request.attack != "none":
        session_id = uuid.uuid4().hex  # unique session per attack
        generator = run_attack(request.attack, request.model, request.prompt, request.defense, session_id)
        if generator:
            return StreamingResponse(gpu_info_and_stream(generator, session_id, request.model, request.attack, request.defense, request.prompt), media_type="text/plain; charset=utf-8")
        else:
            async def error_gen():
                yield b"Unknown attack type\n"
            return StreamingResponse(error_gen(), media_type="text/plain; charset=utf-8")

    if(request.attack == "none"):
        # Handle direct requests
        session_id = uuid.uuid4().hex  # unique session per request
        async def stream_with_gpu_info():
            import time
            start_time = time.time()
            query_count = 0
            token_count = 0
            refusal_type = None
            logged_to_db = False  # Track if we've already logged this session
            
            # Send GPU info
            if torch.cuda.is_available():
                gpu_name = torch.cuda.get_device_name(0)
                yield f"GPU name: {gpu_name}\n".encode("utf-8")
            else:
                yield b"No compatible GPU detected\n"
            
            # Process model
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
                        
                        # Extract metadata
                        if "[TOKEN_COUNT]" in decoded:
                            try:
                                token_count_str = decoded.split("[TOKEN_COUNT] ")[1].strip()
                                token_count = int(token_count_str)
                            except (ValueError, IndexError):
                                pass
                        
                        if "[REFUSAL_TYPE]" in decoded:
                            try:
                                refusal_type = decoded.split("[REFUSAL_TYPE] ")[1].strip()
                            except IndexError:
                                pass
                        
                        # Log attack success
                        try:
                            if "[ATTACK_SUCCESS]" in decoded and not logged_to_db:
                                logged_to_db = True  # Set flag first to prevent double logging
                                success = "true" in decoded.lower()
                                time_to_bypass = time.time() - start_time  # Always calculate total time spent
                                # Use actual generate_streaming call count instead of chunk count
                                actual_query_count = get_generate_streaming_call_count(session_id) if session_id else query_count
                                
                                # Analyze prompt and response
                                is_attack_prompt, prompt_confidence, prompt_label = detect_prompt_attack(request.prompt)
                                tool_misuse_detected = detect_tool_misuse_from_prompt_and_response(
                                    request.prompt, decoded, [], success  # Pass original attack success
                                )
                                
                                # Detect data leakage
                                data_leakage_detected = detect_data_leakage(decoded)
                               
                                if is_attack_prompt == False:
                                    final_attack_success = False
                                else:
                                    final_attack_success = success
                               
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

                        except Exception as e:
                            import traceback
                            traceback.print_exc()
                        
                        # Filter metadata
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
            
            # Log failed cases
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
                except Exception as e:
                    import traceback
                    traceback.print_exc()
        
        return StreamingResponse(stream_with_gpu_info(), media_type="text/plain; charset=utf-8")

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