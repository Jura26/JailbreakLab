import torch
from typing import AsyncGenerator, Optional
from fastapi.responses import StreamingResponse
from transformers import pipeline

# Module-level singleton to avoid reloading model on every request
_SAFETY_CLASSIFIER = None


def _load_classifier():
    """Load the toxicity classifier once and cache it."""
    global _SAFETY_CLASSIFIER
    if _SAFETY_CLASSIFIER is not None:
        return _SAFETY_CLASSIFIER

    device = 0 if torch.cuda.is_available() else -1
    
    # Using unitary/toxic-bert - a popular toxicity detection model
    # Alternative models you can use:
    # - "facebook/roberta-hate-speech-dynabench-r4-target" (hate speech)
    # - "martin-ha/toxic-comment-model" (toxic comments)
    _SAFETY_CLASSIFIER = pipeline(
        "text-classification",
        model="unitary/toxic-bert",
        device=device,
        truncation=True,
        max_length=512
    )
    
    return _SAFETY_CLASSIFIER


async def filter_output_stream(
    body_iterator,
    confidence_threshold: float = 0.7
) -> AsyncGenerator[bytes, None]:
    """
    Async generator that forwards progress markers immediately while collecting
    the actual output, then checks it for toxicity.
    
    Args:
        body_iterator: The original response stream from the model
        confidence_threshold: Minimum confidence to block (0.0-1.0)
    
    Yields:
        bytes: Progress markers forwarded immediately, then filtered output or block message
    """
    
    # Collect only the actual output text, forward progress immediately
    collected = []
    try:
        async for chunk in body_iterator:
            if isinstance(chunk, (bytes, bytearray)):
                decoded = chunk.decode('utf-8', errors='ignore')
            else:
                decoded = str(chunk)
            
            # Forward progress markers immediately
            if decoded.startswith('[PROGRESS]'):
                yield chunk if isinstance(chunk, (bytes, bytearray)) else chunk.encode('utf-8')
            else:
                # Collect actual output for safety check
                collected.append(decoded)
    except TypeError:
        # Not async iterable, try sync
        for chunk in body_iterator:
            if isinstance(chunk, (bytes, bytearray)):
                decoded = chunk.decode('utf-8', errors='ignore')
            else:
                decoded = str(chunk)
            
            if decoded.startswith('[PROGRESS]'):
                yield chunk if isinstance(chunk, (bytes, bytearray)) else chunk.encode('utf-8')
            else:
                collected.append(decoded)
    
    full_output = ''.join(collected).strip()
    
    # Empty output is safe
    if not full_output:
        return
    
    # Run safety check (this may take a moment on first load)
    try:
        classifier = _load_classifier()
        result = classifier(full_output[:512])[0]  # Check first 512 chars for efficiency
        
        is_toxic = result['label'].lower() == 'toxic'
        confidence = result['score']
        
        if is_toxic and confidence >= confidence_threshold:
            # Block the output and send a safe message instead
            block_message = (
                f"BLOCKED_PROMPT:\n{result}\n"
            )
            yield block_message.encode('utf-8')
        else:
            # Output is safe, send it
            yield full_output.encode('utf-8')
    
    except Exception as e:
        # If classification fails, forward the output anyway with a warning
        # (Don't block on technical errors - only on detected toxicity)
        import traceback
        print(f"Output filtering error: {e}")
        traceback.print_exc()
        yield full_output.encode('utf-8')


async def run(prompt: str) -> Optional[StreamingResponse]:
    """
    Output filtering defense - this is a no-op for input checking.
    
    Output filtering works differently: it wraps the model's response stream
    after generation, not before. This function returns None to indicate
    the prompt should be allowed, and the actual filtering happens in
    defense_manager by wrapping the response stream.
    
    Returns:
        None - always allows the prompt through (filtering happens on output)
    """
    # Output filtering doesn't block inputs, only outputs
    return None
