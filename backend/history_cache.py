import os
import json
import time
from typing import List, Dict, Optional

try:
    import redis
except Exception:
    redis = None

_redis_client = None


def _get_redis_client():
    global _redis_client
    if _redis_client is not None:
        return _redis_client
    if redis is None:
        raise RuntimeError("`redis` package is not available. Install requirements or run without Redis.")
    url = os.environ.get("REDIS_URL", "redis://localhost:6379/0")
    _redis_client = redis.from_url(url, decode_responses=True)
    return _redis_client


def add_message(session_id: Optional[str], role: str, text: str, ttl_seconds: int = 86400) -> None:
    """Append a message to the Redis-backed session history list.

    Each entry is stored as a small JSON blob with timestamp, role and text.
    
    Args:
        session_id: Unique session identifier
        role: Message role ("user" or "assistant")
        text: Message content
        ttl_seconds: Time-to-live in seconds (default 86400 = 1 day)
    """
    if not session_id:
        return
    r = _get_redis_client()
    key = f"session:{session_id}:history"
    entry = json.dumps({"t": int(time.time()), "role": role, "text": text})
    # Keep history bounded
    r.rpush(key, entry)
    r.ltrim(key, -200, -1)
    # Set TTL to auto-expire inactive sessions
    r.expire(key, ttl_seconds)


def get_recent(session_id: Optional[str], limit_messages: int = 5) -> List[Dict]:
    """Return the last `limit_messages` messages (in chronological order).

    Returns list of dicts: {t, role, text}
    """
    if not session_id:
        return []
    r = _get_redis_client()
    key = f"session:{session_id}:history"
    raw = r.lrange(key, -limit_messages, -1)
    out: List[Dict] = []
    for v in raw:
        try:
            out.append(json.loads(v))
        except Exception:
            out.append({"t": 0, "role": "unknown", "text": v})
    return out


def get_compact_summary(session_id: Optional[str], max_chars: int = 800, recent_keep: int = 5) -> str:
    """Create a compact extractive summary of older conversation messages.

    This is intentionally lightweight (no ML). It extracts the first sentence
    from older messages (excluding the last `recent_keep`) until `max_chars`.
    """
    if not session_id:
        return ""
    r = _get_redis_client()
    key = f"session:{session_id}:history"
    total = r.llen(key)
    if total <= recent_keep:
        return ""

    # older messages: from 0 .. -(recent_keep+1)
    end_index = -(recent_keep + 1)
    if end_index == 0:
        vals = r.lrange(key, 0, -1)
    else:
        vals = r.lrange(key, 0, end_index)

    pieces: List[str] = []
    cur_len = 0
    for v in vals:
        try:
            obj = json.loads(v)
            txt = obj.get("text", "")
        except Exception:
            txt = v
        # crude sentence split: take up to the first period or newline
        if not txt:
            continue
        first = None
        for sep in (".\n", ".", "\n"):
            if sep in txt:
                first = txt.split(sep)[0].strip()
                break
        if first is None:
            first = txt.strip()
        if not first:
            continue
        snippet = first
        if not snippet.endswith('.'):
            snippet = snippet + '.'
        # append until max_chars reached
        if cur_len + len(snippet) > max_chars:
            remaining = max_chars - cur_len
            if remaining > 0:
                pieces.append(snippet[:remaining])
                cur_len += remaining
            break
        pieces.append(snippet)
        cur_len += len(snippet)

    summary = ' '.join(pieces)
    return summary


def clear_history(session_id: Optional[str]) -> None:
    if not session_id:
        return
    r = _get_redis_client()
    key = f"session:{session_id}:history"
    r.delete(key)
