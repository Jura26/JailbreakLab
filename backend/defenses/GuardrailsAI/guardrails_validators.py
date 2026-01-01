from typing import AsyncGenerator, Optional
from fastapi.responses import StreamingResponse
from guardrails import Guard
from .advanced_guardrails import (
    MultiTurnInjection,
    LLMJudge,
    UnicodeObfuscation,
    RolePersonaEnforcement,
    ToolCallSafety,
)

async def run_multi_turn(prompt: str, session_history=None) -> Optional[StreamingResponse]:
    session_history = session_history or []
    guard = Guard().use(MultiTurnInjection())
    try:
        guard.validate(prompt, metadata={"session_history": session_history})
    except Exception as e:
        async def blocked_stream() -> AsyncGenerator[bytes, None]:
            yield f"BLOCKED_BY_MULTI_TURN:\n{prompt}\nReason: {e}\n".encode("utf-8")
            yield b"Blocked input\n"
        return StreamingResponse(blocked_stream(), media_type="text/plain")
    return None

async def run_llm_judge(prompt: str) -> Optional[StreamingResponse]:
    guard = Guard().use(LLMJudge())
    try:
        guard.validate(prompt)
    except Exception as e:
        async def blocked_stream() -> AsyncGenerator[bytes, None]:
            yield f"BLOCKED_BY_LLM_JUDGE:\n{prompt}\nReason: {e}\n".encode("utf-8")
            yield b"Blocked input\n"
        return StreamingResponse(blocked_stream(), media_type="text/plain")
    return None

async def run_unicode(prompt: str) -> Optional[StreamingResponse]:
    guard = Guard().use(UnicodeObfuscation())
    try:
        guard.validate(prompt)
    except Exception as e:
        async def blocked_stream() -> AsyncGenerator[bytes, None]:
            yield f"BLOCKED_BY_UNICODE:\n{prompt}\nReason: {e}\n".encode("utf-8")
            yield b"Blocked input\n"
        return StreamingResponse(blocked_stream(), media_type="text/plain")
    return None

async def run_role_persona(prompt: str) -> Optional[StreamingResponse]:
    guard = Guard().use(RolePersonaEnforcement())
    try:
        guard.validate(prompt)
    except Exception as e:
        async def blocked_stream() -> AsyncGenerator[bytes, None]:
            yield f"BLOCKED_BY_ROLE_PERSONA:\n{prompt}\nReason: {e}\n".encode("utf-8")
            yield b"Blocked input\n"
        return StreamingResponse(blocked_stream(), media_type="text/plain")
    return None

async def run_tool_call(prompt: str) -> Optional[StreamingResponse]:
    guard = Guard().use(ToolCallSafety())
    try:
        guard.validate(prompt)
    except Exception as e:
        async def blocked_stream() -> AsyncGenerator[bytes, None]:
            yield f"BLOCKED_BY_TOOL_CALL:\n{prompt}\nReason: {e}\n".encode("utf-8")
            yield b"Blocked input\n"
        return StreamingResponse(blocked_stream(), media_type="text/plain")
    return None

async def guardrails_full(prompt: str, session_history=None) -> Optional[StreamingResponse]:
    #Runs all Guardrails validators sequentially on the prompt.
    #Returns a StreamingResponse if any validator blocks the input.
    
    session_history = session_history or []

    validators = [
        run_multi_turn,
        run_llm_judge,
        run_unicode,
        run_role_persona,
        run_tool_call,
    ]

    for validator in validators:
        blocked = await validator(prompt, session_history=session_history)
        if blocked:
            return blocked

    return None
