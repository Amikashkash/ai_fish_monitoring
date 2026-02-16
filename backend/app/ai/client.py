"""
Filename: client.py
Purpose: Claude API client initialization and configuration
Author: Fish Monitoring System
Created: 2026-02-15

This module provides a singleton Claude API client for AI interactions.
Ensures consistent configuration across all AI features.

Dependencies:
    - anthropic: Claude SDK
    - app.config.settings: Environment configuration

Example:
    >>> from app.ai.client import get_ai_client
    >>> client = get_ai_client()
    >>> response = client.messages.create(...)
"""

from anthropic import Anthropic
from typing import Optional

from app.config.settings import get_settings

# Singleton instance
_client: Optional[Anthropic] = None


def get_ai_client() -> Anthropic:
    """
    Get or create Claude API client instance.

    Uses singleton pattern to ensure only one client is created.
    Client is initialized with API key from environment settings.

    Returns:
        Anthropic client instance

    Raises:
        ValueError: If ANTHROPIC_API_KEY not set in environment

    Example:
        >>> client = get_ai_client()
        >>> # Use client for multiple API calls
        >>> response1 = client.messages.create(...)
        >>> response2 = client.messages.create(...)
    """
    global _client

    if _client is None:
        settings = get_settings()

        if not settings.ANTHROPIC_API_KEY:
            raise ValueError(
                "ANTHROPIC_API_KEY not set. "
                "Please configure in .env file."
            )

        _client = Anthropic(api_key=settings.ANTHROPIC_API_KEY)

    return _client


def reset_client() -> None:
    """
    Reset the AI client singleton.

    Useful for testing or when API key changes.
    Forces creation of new client on next get_ai_client() call.

    Example:
        >>> reset_client()
        >>> client = get_ai_client()  # Creates new client
    """
    global _client
    _client = None


# Default model configuration
DEFAULT_MODEL = "claude-sonnet-4-5-20250929"
DEFAULT_MAX_TOKENS = 2048
DEFAULT_TEMPERATURE = 1.0


def get_default_model() -> str:
    """
    Get default Claude model identifier.

    Returns:
        Model ID string for Claude Sonnet 4.5

    Example:
        >>> model = get_default_model()
        >>> print(model)  # "claude-sonnet-4-5-20250929"
    """
    return DEFAULT_MODEL


def get_default_max_tokens() -> int:
    """
    Get default maximum tokens for responses.

    Returns:
        Maximum token count (2048 for most use cases)

    Example:
        >>> max_tokens = get_default_max_tokens()
        >>> print(max_tokens)  # 2048
    """
    return DEFAULT_MAX_TOKENS


def get_default_temperature() -> float:
    """
    Get default temperature for responses.

    Returns:
        Temperature value (1.0 for balanced creativity/consistency)

    Example:
        >>> temp = get_default_temperature()
        >>> print(temp)  # 1.0
    """
    return DEFAULT_TEMPERATURE
