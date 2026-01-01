from guardrails.validators import Validator
from typing import Any


class MultiTurnInjection(Validator):
    def validate(self, value: str, metadata: dict | None = None) -> Any:
        return value


class LLMJudge(Validator):
    def validate(self, value: str, metadata: dict | None = None) -> Any:
        return value


class UnicodeObfuscation(Validator):
    def validate(self, value: str, metadata: dict | None = None) -> Any:
        return value


class RolePersonaEnforcement(Validator):
    def validate(self, value: str, metadata: dict | None = None) -> Any:
        return value


class ToolCallSafety(Validator):
    def validate(self, value: str, metadata: dict | None = None) -> Any:
        return value
