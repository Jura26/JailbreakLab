import torch
import os
from .MaskedDefender import MaskedDefender
import unicodedata
from typing import AsyncGenerator, Optional
from fastapi.responses import StreamingResponse

# Module-level singleton defender to avoid reloading/training on every request
_DEFENDER: Optional[MaskedDefender] = None

def _get_model_path() -> str:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(BASE_DIR, "best_masked_defender_m5.pth")

def _load_defender(device: str | None = None) -> MaskedDefender:
    """Load the MaskedDefender and weights from disk (if available).

    This is intentionally lightweight and safe to call multiple times; the
    underlying object is cached in the module to avoid repeated I/O.
    """
    global _DEFENDER
    if _DEFENDER is not None:
        return _DEFENDER

    model_path = _get_model_path()
    # Let MaskedDefender auto-detect device when device is None
    defender = MaskedDefender(device=device)

    if os.path.exists(model_path):
        try:
            # Prepare kwargs for torch.load; use defender.device so map_location matches where the model lives
            map_loc = torch.device(defender.device if defender.device is not None else "cpu")
            load_kwargs = {"map_location": map_loc}

            # Use inspect to check if torch.load supports weights_only (PyTorch >=2.6)
            import inspect, pathlib, torch.serialization as serialization
            sig = inspect.signature(torch.load)
            if 'weights_only' in sig.parameters:
                load_kwargs['weights_only'] = False

            # Add pathlib.PosixPath to safe globals if the API is available (addresses the error seen in PyTorch 2.6+)
            try:
                if hasattr(serialization, 'add_safe_globals'):
                    serialization.add_safe_globals([pathlib.PosixPath])
            except Exception:
                # If we can't register safe globals, we'll still attempt load and handle errors below
                pass

            checkpoint = torch.load(model_path, **load_kwargs)

            # load_state_dict expects the exact keys; guard if checkpoint format differs
            if isinstance(checkpoint, dict) and 'mask_generator_state_dict' in checkpoint and 'safety_evaluator_state_dict' in checkpoint:
                defender.mask_generator.load_state_dict(checkpoint['mask_generator_state_dict'])
                defender.safety_evaluator.load_state_dict(checkpoint['safety_evaluator_state_dict'])
        except Exception as e:
            # Try a safer fallback: attempt load without weights_only if that was set, or report
            try:
                load_kwargs.pop('weights_only', None)
                checkpoint = torch.load(model_path, map_location=map_loc)
                if isinstance(checkpoint, dict) and 'mask_generator_state_dict' in checkpoint and 'safety_evaluator_state_dict' in checkpoint:
                    defender.mask_generator.load_state_dict(checkpoint['mask_generator_state_dict'])
                    defender.safety_evaluator.load_state_dict(checkpoint['safety_evaluator_state_dict'])
            except Exception as e2:
                print(f"Error loading MaskedDefender checkpoint: {e}\nFallback error: {e2}")

    defender.mask_generator.eval()
    defender.safety_evaluator.eval()
    _DEFENDER = defender
    return _DEFENDER


async def run(prompt: str) -> Optional[StreamingResponse]:
    """Evaluate a prompt using the cached MaskedDefender.

    Loads the pretrained `.pth` file once (on first call) and reuses the model
    for subsequent requests so you don't retrain or reload weights each time.
    """
    defender = _load_defender(device='cpu')

    # Synchronous defend call; keep behavior identical to previous implementation
    result = defender.defend(prompt)

    if result['is_safe']:
        # Allowed — return None so downstream processing continues
        return None
    else:
        # Build a informative blocked message including confidence and original text
        confidence = result.get('confidence', 0.0)

        async def blocked_stream() -> AsyncGenerator[bytes, None]:
            msg = f"BLOCKED_BY=masked_defender;CONFIDENCE={confidence:.3f};PROMPT={prompt}\n"
            yield msg.encode("utf-8")
            # Also include a simple human-readable line for frontend compatibility
            yield b"Blocked input\n"

        return StreamingResponse(blocked_stream(), media_type="text/plain; charset=utf-8")