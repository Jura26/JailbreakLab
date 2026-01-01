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

async def run_validator(validator_cls, prompt: str, session_history=None) -> Optional[StreamingResponse]:
    session_history = session_history or []
    guard = Guard().use(validator_cls())

    try:
        guard.validate(prompt, metadata={"session_history": session_history})
    except Exception:
        async def blocked_stream() -> AsyncGenerator[bytes, None]:
            yield f"BLOCKED_BY_{validator_cls.rail_alias.upper()}\n".encode("utf-8")

        return StreamingResponse(blocked_stream(), media_type="text/plain")

    return None


async def run_multi_turn(prompt: str, session_history=None):
    return await run_validator(MultiTurnInjection, prompt, session_history)


async def run_llm_judge(prompt: str, session_history=None):
    return await run_validator(LLMJudge, prompt, session_history)


async def run_unicode(prompt: str, session_history=None):
    return await run_validator(UnicodeObfuscation, prompt, session_history)


async def run_role_persona(prompt: str, session_history=None):
    return await run_validator(RolePersonaEnforcement, prompt, session_history)


async def run_tool_call(prompt: str, session_history=None):
    return await run_validator(ToolCallSafety, prompt, session_history)


async def guardrails_full(prompt: str, session_history=None) -> Optional[StreamingResponse]:
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
