import unicodedata
from typing import AsyncGenerator, Optional
from fastapi.responses import StreamingResponse

async def run(prompt: str) -> Optional[StreamingResponse]:
    """
    Detects suspicious or potentially unsafe instructions in a prompt.
    Returns a StreamingResponse("Blocked input") if detected, otherwise None.
    """

    suspicious_phrases = [
        "ignore the above",
        "ignore previous",
        "ignore above",
        "ignore all",
        "disregard instructions",
        "pretend you are",
        "reveal",
        "bypass safety",
        "disable filter",
    ]

    # Normalize text (removes invisible characters, accents, etc.)
    normalized = unicodedata.normalize("NFKC", prompt).lower()
    # Check for suspicious phrases and report which one matched
    for phrase in suspicious_phrases:
        if phrase in normalized:
            matched = phrase

            async def blocked_stream() -> AsyncGenerator[bytes, None]:
                # Send a short structured message so frontend can display what was caught
                msg = f"BLOCKED_PROMPT:\n{prompt}\n"
                yield msg.encode("utf-8")
                # Also include a simple human-readable line for frontend compatibility
                yield b"Blocked input\n"

            return StreamingResponse(blocked_stream(), media_type="text/plain; charset=utf-8")

    # No suspicious content found
    return None
