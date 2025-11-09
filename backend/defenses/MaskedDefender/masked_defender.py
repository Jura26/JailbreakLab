import torch
import os
from .MaskedDefender import MaskedDefender
import unicodedata
from typing import AsyncGenerator, Optional
from fastapi.responses import StreamingResponse
# Load trained model

async def run(prompt: str)->Optional[StreamingResponse]:

    # Get directory of the current file
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Construct absolute path to the checkpoint
    MODEL_PATH = os.path.join(BASE_DIR, "best_masked_defender_m5.pth")

    defender = MaskedDefender(device='cpu')
    checkpoint = torch.load(MODEL_PATH,map_location=torch.device('cpu'), weights_only=False)
    defender.mask_generator.load_state_dict(checkpoint['mask_generator_state_dict'])
    defender.safety_evaluator.load_state_dict(checkpoint['safety_evaluator_state_dict'])
    defender.mask_generator.eval()
    defender.safety_evaluator.eval()

    

    # Check any prompt
    result = defender.defend(prompt)

    print("Prompt:", repr(prompt))
    print("Defender result:", result)
    
    if result['is_safe']:
    # Send to your LLM
        return None
    else:
        async def blocked_stream() -> AsyncGenerator[bytes, None]:
            yield b"Blocked input\n"
        return StreamingResponse(blocked_stream(), media_type="text/plain; charset=utf-8")
        #return None