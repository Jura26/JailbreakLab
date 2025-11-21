
from typing import Optional, Dict, AsyncIterable
from fastapi.responses import StreamingResponse
from . import input_sanitization  # import your defense module
from .MaskedDefender import masked_defender

# Local import of model runner (relative to package)
try:
    from model import generate_streaming
except Exception:
    # fallback if package import context differs
    from ..model import generate_streaming

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
    # You can add more later, e.g. "ml_filter": ml_filter.run
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
) -> tuple[bool, Optional[StreamingResponse]]:
    """
    Runs the selected defense. If the defense blocks the prompt, returns a StreamingResponse
    (blocking message). If not blocked and `model_id` is provided, runs the model via
    the centralized `generate_streaming` and returns its StreamingResponse.

    This variant supports an optional Redis-based recent-history cache. When a
    `session_id` is supplied, `apply_defense` will:
      - build a compact summary of older messages and include recent messages
        as a context prefix to the model prompt
      - append the user message to history (after defenses pass)
      - capture the assistant response and persist it to history when streaming completes

    Returns:
      (blocked: bool, streaming_response_or_block: Optional[StreamingResponse])
    """
    defense_func = DEFENSES.get(defense)
    if defense_func:
        # defense functions are expected to return a StreamingResponse when blocking
        blocked_resp = await defense_func(prompt)
        if blocked_resp:
            # signal that defense blocked the prompt
            return True, blocked_resp

    # If a model_id is provided, run the model and return its StreamingResponse (not a block)
    if model_id:
        # Prepare context from history (excluding current prompt)
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
            # if history cache fails, proceed without context
            prefix_parts = []

        context_prefix = "\n\n".join(prefix_parts).strip()
        if context_prefix:
            augmented_prompt = f"{context_prefix}\n\nUser: {prompt}"
        else:
            augmented_prompt = prompt

        # store the user message into history (after defenses passed) so it's available
        # for subsequent calls; don't block on failures
        if session_id and store_history:
            try:
                add_message(session_id, 'user', prompt)
            except Exception:
                pass

        resp = await generate_streaming(model_id=model_id, prompt=augmented_prompt, device=device, generation_options=generation_options)

        # If we have a session id and are storing history, wrap the response iterator
        # to capture assistant output and persist it when streaming completes.
        if session_id and store_history and isinstance(resp, StreamingResponse):
            wrapped = StreamingResponse(_capture_and_forward(resp.body_iterator, session_id), media_type=getattr(resp, 'media_type', 'text/plain'))
            return False, wrapped
        return False, resp

    # Passed defenses, no model requested
    return False, None
