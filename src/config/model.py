"""Model configuration for Student Ops Desk - OpenAI-compatible client for Gemini."""

from openai import AsyncOpenAI
from src.config.settings import get_settings


def create_gemini_client() -> AsyncOpenAI:
    """Create an OpenAI-compatible AsyncOpenAI client configured for Gemini.

    This client is configured at the agent level, not globally.
    The model is set on the agent itself, not here.
    """
    settings = get_settings()
    return AsyncOpenAI(
        api_key=settings.gemini_api_key,
        base_url=settings.openai_base_url,
    )


def get_model_name() -> str:
    """Get the model name for agent configuration."""
    return get_settings().model_name