
from typing import Optional, Dict, AsyncIterable
from fastapi.responses import StreamingResponse
from . import input_sanitization  # import your defense module
from . import system_prompt_hardening
from .MaskedDefender import masked_defender
from .PIGuard import piguard
from .LlamaGuard import llama_guard
from . import perturb_defense
from .GuardrailsAI import guardrails_run
# Global counter for generate_streaming calls per session
_generate_streaming_call_counts = {}

def get_generate_streaming_call_count(session_id: str) -> int:
    """Get the number of generate_streaming calls for a session."""
    count = _generate_streaming_call_counts.get(session_id, 0)
    print(f"DEBUG: Retrieved count for session {session_id}: {count}")
    return count

def reset_generate_streaming_call_count(session_id: str):
    """Reset the call count for a session."""
    print(f"DEBUG: Resetting count for session {session_id}")
    _generate_streaming_call_counts[session_id] = 0

def increment_generate_streaming_call_count(session_id: str):
    """Increment the call count for a session."""
    if session_id not in _generate_streaming_call_counts:
        _generate_streaming_call_counts[session_id] = 0
    _generate_streaming_call_counts[session_id] += 1
    print(f"DEBUG: Incremented count for session {session_id} to {_generate_streaming_call_counts[session_id]}")

# Local import of model runner
import sys
import os
# Add the parent directory to the path so we can import from the backend root
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from model import generate_streaming

# history cache (Redis-backed)
try:
    from history_cache import add_message, get_recent, get_compact_summary
except Exception:
    # history cache may not be available at runtime
    def add_message(session_id, role, text):
        return

    def get_recent(session_id, limit_messages=5):
        return []

    def get_compact_summary(session_id, max_chars=800, recent_keep=5):
        return ""

# Map frontend defense strings to functions
DEFENSES = {
    "input_sanitization": input_sanitization.run,
    "masked_defender": masked_defender.run,
    "system_prompt_hardening": system_prompt_hardening.run,
    "piguard": piguard.run,
    "llama_guard": llama_guard.run,
    "llama_guard_4": llama_guard.run_v4,
    #"multi_turn": guardrails_validators.run_multi_turn,
    "llm_judge": guardrails_run.run_llm_judge,
    #"unicode": guardrails_validators.run_unicode,
    #"role_persona": guardrails_validators.run_role_persona,
    #"tool_call": guardrails_validators.run_tool_call,
    #"guardrails_full": guardrails_validators.guardrails_full,  # full stacked defense
    "guardrails_detect_jailbreak": guardrails_run.run_detect_jailbreak,
    "semantic_perturbation": perturb_defense.run,
    "character_perturbation": perturb_defense.run,
    "hybrid_perturbation":perturb_defense.run,
}


async def _capture_and_forward(body_iterator: AsyncIterable, session_id: Optional[str]):
    """Async generator that forwards chunks from `body_iterator` while capturing
    the full assistant output and storing it in history after completion.
    """
    collected = []
    # try async iteration first
    try:
        async for chunk in body_iterator:
            # preserve original chunk type
            collected.append(chunk.decode('utf-8') if isinstance(chunk, (bytes, bytearray)) else str(chunk))
            yield chunk
    except TypeError:
        # Not an async iterable, try sync iteration
        for chunk in body_iterator:
            collected.append(chunk.decode('utf-8') if isinstance(chunk, (bytes, bytearray)) else str(chunk))
            yield chunk
    finally:
        try:
            full = ''.join(collected)
            if session_id and full:
                add_message(session_id, 'assistant', full)
        except Exception:
            # never raise while streaming
            pass

async def apply_defense(
    defense: str,
    prompt: str,
    model_id: Optional[str] = None,
    device: str = "cpu",
    generation_options: Optional[Dict] = None,
    session_id: Optional[str] = None,
    store_history: bool = True,
    skip_progress: bool = False,
) -> tuple[bool, Optional[StreamingResponse]]:
    """
    Runs the selected defense. If the defense blocks the prompt, returns a StreamingResponse
    (blocking message). If not blocked and `model_id` is provided, runs the model via
    the centralized `generate_streaming` and returns its StreamingResponse.
    """
    defense_func = DEFENSES.get(defense)
    if defense_func:
        blocked_resp = await defense_func(prompt)
        if blocked_resp:
            return True, blocked_resp

    if model_id:
        # Initialize call counter for this session
        
        prefix_parts = []
        try:
            if session_id:
                summary = get_compact_summary(session_id, max_chars=800, recent_keep=5)
                recent_msgs = get_recent(session_id, limit_messages=5)
                if summary:
                    prefix_parts.append(f"Conversation summary:\n{summary}")
                if recent_msgs:
                    recent_lines = []
                    for m in recent_msgs:
                        role = m.get('role', 'user')
                        text = m.get('text', '')
                        label = 'User' if role == 'user' else 'Assistant'
                        recent_lines.append(f"{label}: {text}")
                    prefix_parts.append("Recent messages:\n" + "\n".join(recent_lines))
        except Exception:
            prefix_parts = []

        if defense == "semantic_perturbation":
            prompt = perturb_defense.run_semantic_perturb(prompt)
        elif defense == "character_perturbation":
            prompt = perturb_defense.run_character_perturb(prompt)
        elif defense == "hybrid_perturbation":
            prompt = perturb_defense.run_hybrid_defense(prompt)
        elif defense == "hybrid_perturbation_with_judge":
            prompt = await perturb_defense.hybrid_perturb_with_judge(prompt)
        #print("NEW PROMPT:" + prompt)
        context_prefix = "\n\n".join(prefix_parts).strip()
        if context_prefix:
            augmented_prompt = f"{context_prefix}\n\nUser: {prompt}"
        else:
            augmented_prompt = prompt

        if defense == "system_prompt_hardening":
            augmented_prompt = system_prompt_hardening.apply_system_prompt_hardening(augmented_prompt)

        if session_id and store_history:
            try:
                add_message(session_id, 'user', prompt)
            except Exception:
                pass
        
        # Increment counter before calling generate_streaming
        if session_id:
            increment_generate_streaming_call_count(session_id)

        resp = await generate_streaming(model_id=model_id, prompt=augmented_prompt, device=device, generation_options=generation_options, session_id=session_id, skip_progress=skip_progress)

        # model.py handles logging the assistant response cleanly, so we just return the response
        return False, resp

    return False, None
