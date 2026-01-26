"""
Supabase client for database and authentication.
"""
from supabase import create_client, Client
from core.config import get_settings

settings = get_settings()

_supabase_client: Client = None


def get_supabase() -> Client:
    """Get or create Supabase client instance."""
    global _supabase_client
    
    if _supabase_client is None:
        if not settings.supabase_url or not settings.supabase_key:
            raise ValueError(
                "Supabase URL and Key must be set in environment variables. "
                "Get them from: https://supabase.com/dashboard/project/_/settings/api"
            )
        _supabase_client = create_client(
            settings.supabase_url,
            settings.supabase_key
        )
    
    return _supabase_client
