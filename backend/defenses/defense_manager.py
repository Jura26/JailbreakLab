
from typing import Optional
from fastapi.responses import StreamingResponse
from . import input_sanitization  # import your defense module
from .MaskedDefender import masked_defender
# Map frontend defense strings to functions
DEFENSES = {
    "input_sanitization": input_sanitization.run,
    "masked_defender": masked_defender.run,
    
    # You can add more later, e.g. "ml_filter": ml_filter.run
}

async def apply_defense(defense: str, prompt: str) -> Optional[StreamingResponse]:
    """
    Runs the selected defense based on frontend input.
    Returns a StreamingResponse if blocked, otherwise None.
    """
    defense_func = DEFENSES.get(defense)
    if defense_func:
        return await defense_func(prompt)
    return None
