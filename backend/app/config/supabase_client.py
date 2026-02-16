"""
Supabase REST API client configuration
"""
from supabase import create_client, Client
from typing import Generator
from app.config.settings import get_settings

settings = get_settings()

# Create Supabase client
supabase: Client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)


def get_supabase() -> Generator[Client, None, None]:
    """
    Dependency function to get Supabase client.

    Yields:
        Supabase Client object
    """
    yield supabase
