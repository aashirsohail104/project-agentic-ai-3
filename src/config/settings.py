"""Configuration settings for Student Ops Desk."""

import os
from functools import lru_cache
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Gemini / OpenAI-compatible configuration
    gemini_api_key: str = Field(
        default="your_gemini_api_key_here",
        description="Gemini API key from Google AI Studio",
    )
    openai_base_url: str = Field(
        default="https://generativelanguage.googleapis.com/v1beta/openai/",
        description="OpenAI-compatible base URL for Gemini",
    )
    model_name: str = Field(
        default="gemini-2.5-flash",
        description="Model name to use",
    )

    # Tracing
    tracing_key: str | None = Field(
        default=None,
        description="Optional tracing export key",
    )

    # Chainlit
    chainlit_host: str = Field(default="0.0.0.0", description="Chainlit host")
    chainlit_port: int = Field(default=8000, description="Chainlit port")

    # Logging
    log_level: str = Field(default="INFO", description="Log level")

    def validate_required(self) -> None:
        """Validate that all required settings are present."""
        if not self.gemini_api_key or self.gemini_api_key == "your_gemini_api_key_here":
            raise ValueError(
                "GEMINI_API_KEY is required. "
                "Get your API key from https://aistudio.google.com/ "
                "and set it in .env file."
            )


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Get cached settings instance."""
    settings = Settings()
    settings.validate_required()
    return settings