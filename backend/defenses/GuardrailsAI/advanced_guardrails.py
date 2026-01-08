from typing import AsyncGenerator, Optional, Dict, Any
from fastapi.responses import StreamingResponse
from guardrails import Guard
from guardrails.validators import Validator, register_validator
import asyncio
import logging
from openai import AsyncOpenAI

# -------------------------
# OpenAI Client
# -------------------------

client = AsyncOpenAI()

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

    def validate(self, value: str, metadata: Dict[str, Any] | None = None) -> Any:
        verdict = self._run_async(self._judge(value))

        if verdict is False:
            raise Exception("Blocked by LLMJudge")

        return value

    def _run_async(self, coro):
        """
        Safely run async code from sync context
        (FastAPI / Guardrails safe)
        """
        loop = asyncio.new_event_loop()
        try:
            asyncio.set_event_loop(loop)
            return loop.run_until_complete(coro)
        finally:
            loop.close()

    async def _judge(self, prompt: str) -> bool:
        """
        True  -> SAFE
        False -> BLOCK
        """
        try:
            response = await client.chat.completions.create(
                model="gpt-4o-mini",
                temperature=0,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are a strict content safety classifier.\n"
                            "Reply ONLY with:\n"
                            "- BLOCK (if clearly unsafe: violence, sexual content, self-harm, illegal activity)\n"
                            "- SAFE (otherwise)"
                        ),
                    },
                    {"role": "user", "content": prompt},
                ],
            )

            verdict = response.choices[0].message.content.strip().upper()
            logging.debug(f"[LLMJudge verdict] {verdict}")

            # 🔑 Block ONLY if the model explicitly says BLOCK
            return verdict != "BLOCK"

        except Exception as e:
            # Fail-open to prevent false positives
            logging.error(f"[LLMJudge ERROR] {e}")
            return True

    rail_alias = "llm_judge"

    def validate(self, value: str, metadata: Dict[str, Any] | None = None) -> Any:
        verdict = self._run_async(self._judge(value))

        if verdict is False:
            raise Exception("Blocked by LLMJudge")

        return value

    def _run_async(self, coro):
        """
        Safely run async code from sync context
        (FastAPI / Guardrails safe)
        """
        loop = asyncio.new_event_loop()
        try:
            asyncio.set_event_loop(loop)
            return loop.run_until_complete(coro)
        finally:
            loop.close()

    async def _judge(self, prompt: str) -> bool:
        """
        True  -> SAFE
        False -> BLOCK
        """
        try:
            response = await client.chat.completions.create(
                model="gpt-4o-mini",
                temperature=0,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are a strict content safety classifier.\n"
                            "Reply ONLY with:\n"
                            "- BLOCK (if clearly unsafe: violence, sexual content, self-harm, illegal activity)\n"
                            "- SAFE (otherwise)"
                        ),
                    },
                    {"role": "user", "content": prompt},
                ],
            )

            verdict = response.choices[0].message.content.strip().upper()
            logging.debug(f"[LLMJudge verdict] {verdict}")

            # 🔑 Block ONLY if the model explicitly says BLOCK
            return verdict != "BLOCK"

        except Exception as e:
            # Fail-open to prevent false positives
            logging.error(f"[LLMJudge ERROR] {e}")
            return True

    rail_alias = "llm_judge"

    def validate(self, value: str, metadata: Dict[str, Any] | None = None) -> Any:
        try:
            loop = asyncio.get_running_loop()
            task = loop.create_task(self._judge(value))
            verdict = loop.run_until_complete(asyncio.shield(task))
        except RuntimeError:
            # No running loop (CLI / tests)
            verdict = asyncio.run(self._judge(value))

        if verdict is False:
            raise Exception("Blocked by LLMJudge")

        return value

    async def _judge(self, prompt: str) -> bool:
        """
        Returns:
        True  -> SAFE
        False -> BLOCK
        """
        try:
            response = await client.chat.completions.create(
                model="gpt-4o-mini",
                temperature=0,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are a strict content safety classifier.\n"
                            "Reply ONLY with:\n"
                            "- BLOCK (if clearly unsafe: violence, sexual content, self-harm, illegal activity)\n"
                            "- SAFE (otherwise)"
                        ),
                    },
                    {"role": "user", "content": prompt},
                ],
            )

            verdict = response.choices[0].message.content.strip().upper()
            logging.debug(f"[LLMJudge verdict] {verdict}")

            # 🔑 Block ONLY on explicit BLOCK
            return verdict != "BLOCK"

        except Exception as e:
            # Fail-open to avoid false positives
            logging.error(f"[LLMJudge ERROR] {e}")
            return True


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
