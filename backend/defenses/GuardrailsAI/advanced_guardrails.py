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









