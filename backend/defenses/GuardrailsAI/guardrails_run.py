from typing import AsyncGenerator, Optional
from fastapi.responses import StreamingResponse
from guardrails.hub import DetectJailbreak
from guardrails import Guard
from guardrails.errors import ValidationError

async def run_detect_jailbreak( prompt: str, session_history=None) -> Optional[StreamingResponse]:
    session_history = session_history or []
    guard = Guard().use(
        DetectJailbreak(on_fail="exception", threshold=0.7)
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

