import os
from pathlib import Path
from dotenv import load_dotenv
from supabase import create_client, Client
from typing import Optional

# Load .env file from project root
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(env_path)

# Initialize Supabase client
_supabase_client: Optional[Client] = None


def get_supabase_client() -> Optional[Client]:
    """Get or create Supabase client."""
    global _supabase_client

    if _supabase_client is not None:
        return _supabase_client

    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_KEY")

    if not url or not key:
        print("Warning: SUPABASE_URL or SUPABASE_KEY not set. Database logging disabled.")
        return None

    try:
        _supabase_client = create_client(url, key)
        return _supabase_client
    except Exception as e:
        print(f"Error creating Supabase client: {e}")
        return None


def log_bert_statistic(
    session_id: str,
    model_type: str,
    attack_type: str,
    defense_type: str,
    attack_success: bool,
    was_blocked: bool = False
) -> bool:
    """
    Log attack detection result to bert_statistics table.
    Returns True if successful, False otherwise.
    """
    client = get_supabase_client()
    if not client:
        return False

    try:
        client.table("bert_statistics").insert({
            "session_id": session_id,
            "model_type": model_type,
            "attack_type": attack_type,
            "defense_type": defense_type,
            "attack_success": attack_success,
            "was_blocked": was_blocked
        }).execute()
        return True
    except Exception as e:
        print(f"Error logging to bert_statistics: {e}")
        return False


def log_manual_statistic(
    model_type: str,
    attack_type: str,
    defense_type: str,
    manual_attack_success: bool
) -> bool:
    """
    Log manual review result to manual_statistics table.
    Returns True if successful, False otherwise.
    """
    client = get_supabase_client()
    if not client:
        return False

    try:
        client.table("manual_statistics").insert({
            "model_type": model_type,
            "attack_type": attack_type,
            "defense_type": defense_type,
            "manual_attack_success": manual_attack_success
        }).execute()
        return True
    except Exception as e:
        print(f"Error logging to manual_statistics: {e}")
        return False
