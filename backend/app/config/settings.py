"""
Filename: settings.py
Purpose: Application configuration and environment variable management
Author: Fish Monitoring System
Created: 2026-02-15

This module manages all environment variables and application settings
using Pydantic Settings for type-safe configuration.

Dependencies:
    - pydantic-settings: Settings management
    - python-dotenv: Load .env files

Example:
    >>> from app.config.settings import get_settings
    >>> settings = get_settings()
    >>> print(settings.SUPABASE_URL)
"""

from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.

    All settings are loaded from .env file or environment variables.
    Required settings will raise ValidationError if not set.

    Attributes:
        ANTHROPIC_API_KEY: API key for Claude AI
        SUPABASE_URL: Supabase project URL
        SUPABASE_KEY: Supabase anon/service key
        N8N_WEBHOOK_URL: Webhook URL for n8n integration
        CORS_ORIGINS: List of allowed CORS origins
        ENVIRONMENT: Environment name (development/production)
        API_HOST: API server host
        API_PORT: API server port

    Example:
        >>> settings = Settings()
        >>> print(settings.ENVIRONMENT)
        'development'
    """

    # AI Configuration
    ANTHROPIC_API_KEY: str

    # Database Configuration
    SUPABASE_URL: str
    SUPABASE_KEY: str

    # n8n Integration
    N8N_WEBHOOK_URL: str = "http://localhost:5678/webhook/fish-monitoring"

    # CORS Configuration
    CORS_ORIGINS: str = "http://localhost:5173,http://localhost:3000"

    # Environment
    ENVIRONMENT: str = "development"

    # API Configuration
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True
    )

    def get_cors_origins_list(self) -> List[str]:
        """
        Parse CORS_ORIGINS string into list.

        Returns:
            List of origin URLs

        Example:
            >>> settings = Settings()
            >>> origins = settings.get_cors_origins_list()
            >>> print(origins)
            ['http://localhost:5173', 'http://localhost:3000']
        """
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]


# Singleton instance
_settings = None


def get_settings() -> Settings:
    """
    Get singleton settings instance.

    This ensures settings are loaded only once and reused throughout
    the application lifecycle.

    Returns:
        Settings instance

    Example:
        >>> settings = get_settings()
        >>> print(settings.API_PORT)
        8000
    """
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings
