from typing import AsyncGenerator, Optional, Dict, Any, Union, List
from fastapi.responses import StreamingResponse
from guardrails import Guard
from guardrails.validators import Validator, register_validator
import asyncio
import logging
from openai import OpenAI
from guardrails.errors import ValidationError
from guardrails.validator_base import (
    FailResult,
    PassResult,
    ValidationResult,
)
# -------------------------
# OpenAI Client
# -------------------------

client = OpenAI()

# -------------------------
# Validator Implementations
# -------------------------

@register_validator("multi_turn_injection", data_type="string")
class MultiTurnInjection(Validator):
    rail_alias = "multi_turn_injection"

    def validate(self, value: str, metadata: Dict[str, Any] | None = None) -> Any:
        # Placeholder – always allow for now
        return value





@register_validator("llm_judge", data_type="string")
class LLMJudge(Validator):
    rail_alias = "llm_judge"

    def _judge(self, prompt: str) -> bool:
        """
        True  -> SAFE
        False -> BLOCK
        """
        system_prompt = """
You are a strict content safety classifier. 
Your job is to decide whether a user prompt is unsafe. 
Unsafe means: violence, sexual content, self-harm, illegal activity, or anything clearly harmful. 
Safe means everything else.

ONLY respond with a Python boolean literal: 
- True if the prompt is SAFE 
- False if the prompt is UNSAFE (blocked)

Do not add any explanation, quotes, or punctuation. 
Your response must be exactly "True" or "False".
"""


        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                temperature=0,
                messages=[
                    {
                        "role": "system",
                        "content": system_prompt,
                    },
                    {"role": "user", "content": prompt},
                ],
            )
            verdict_str = response.choices[0].message.content.strip().upper()
            verdict = verdict_str == "TRUE"
            logging.debug(f"[LLMJudge verdict] {verdict_str}->{verdict}")
            
            return verdict

        except Exception as e:
            logging.error(f"[LLMJudge ERROR] {e}")
            # Fail-open
            return True

    def validate(
        self,
        value: Union[str, List[str]],
        metadata: Optional[dict] = None,
    ) -> ValidationResult:

        is_safe = self._judge(value)

        if not is_safe:
            return FailResult(error_message="Blocked by LLMJudge")

        return PassResult()





@register_validator("unicode_obfuscation", data_type="string")
class UnicodeObfuscation(Validator):
    rail_alias = "unicode_obfuscation"

    def validate(self, value: str, metadata: Dict[str, Any] | None = None) -> Any:
        return value


@register_validator("role_persona_enforcement", data_type="string")
class RolePersonaEnforcement(Validator):
    rail_alias = "role_persona_enforcement"

    def validate(self, value: str, metadata: Dict[str, Any] | None = None) -> Any:
        return value


@register_validator("tool_call_safety", data_type="string")
class ToolCallSafety(Validator):
    rail_alias = "tool_call_safety"

    def validate(self, value: str, metadata: Dict[str, Any] | None = None) -> Any:
        return value


# -------------------------
# Guardrails Runner
# -------------------------

async def run_validator(
    validator_cls: type[Validator],
    prompt: str,
    session_history=None
) -> Optional[StreamingResponse]:

    session_history = session_history or []
    guard = Guard().use(validator_cls())

    try:
        guard.validate(prompt, metadata={"session_history": session_history})

    except Exception:
        async def blocked_stream() -> AsyncGenerator[bytes, None]:
            yield f"BLOCKED_BY_{validator_cls.rail_alias.upper()}\n".encode("utf-8")

        return StreamingResponse(blocked_stream(), media_type="text/plain")

    return None


async def guardrails_full(prompt: str, session_history=None) -> Optional[StreamingResponse]:
    validators = [
        MultiTurnInjection,
        LLMJudge,
        UnicodeObfuscation,
        RolePersonaEnforcement,
        ToolCallSafety,
    ]

    for validator_cls in validators:
        blocked = await run_validator(validator_cls, prompt, session_history)
        if blocked:
            return blocked

    return None
