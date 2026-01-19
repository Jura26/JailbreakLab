from typing import AsyncGenerator, Optional
from fastapi.responses import StreamingResponse
from guardrails.hub import DetectJailbreak
from guardrails import Guard
from guardrails.errors import ValidationError
from .advanced_guardrails import LLMJudge
async def run_detect_jailbreak( prompt: str, session_history=None) -> Optional[StreamingResponse]:
    session_history = session_history or []
    guard = Guard().use(
        DetectJailbreak(on_fail="exception", threshold=0.81)
        )
    try:
        guard.validate(prompt, metadata={"session_history": session_history})
        
    except Exception as e:
        async def blocked_stream() -> AsyncGenerator[bytes, None]:
            # Send a short structured message so frontend can display what was caught
            msg = f"BLOCKED_PROMPT: \n{prompt}\n"
            yield msg.encode("utf-8")
            # Also include a simple human-readable line for frontend compatibility
            yield b"Blocked input\n"

        return StreamingResponse(blocked_stream(), media_type="text/plain; charset=utf-8")
    
async def run_llm_judge( prompt: str, session_history=None) -> Optional[StreamingResponse]:
    session_history = session_history or []
    guard = Guard().use(
        LLMJudge()
        )
    try:
        result = guard.validate(prompt, metadata={"session_history": session_history}, raise_on_error=True)
        #FAIL SAFE
        if result is None or not hasattr(result, "validation_passed"):
            is_safe = False
        else:
            is_safe = result.validation_passed
        if not is_safe:
            async def blocked_stream() -> AsyncGenerator[bytes, None]:
                msg = f"BLOCKED_PROMPT: \n{prompt}\n"
                yield msg.encode("utf-8")
                yield b"Blocked input\n"

            return StreamingResponse(blocked_stream(), media_type="text/plain; charset=utf-8")

        # Safe prompt → return None (can continue processing)
        return None

    except ValidationError:
        async def blocked_stream() -> AsyncGenerator[bytes, None]:
            # Send a short structured message so frontend can display what was caught
            msg = f"BLOCKED_PROMPT: \n{prompt}\n"
            yield msg.encode("utf-8")
            # Also include a simple human-readable line for frontend compatibility
            yield b"Blocked input\n"

        return StreamingResponse(blocked_stream(), media_type="text/plain; charset=utf-8")
    
async def run_unicode(prompt:str, session_history=None)->Optional[StreamingResponse]:
    session_history = session_history or []


