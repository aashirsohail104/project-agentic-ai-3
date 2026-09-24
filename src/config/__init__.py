"""Configuration package for Student Ops Desk."""

from config.settings import Settings, get_settings
from config.model import create_gemini_client, get_model_name

__all__ = [
    "Settings",
    "get_settings",
    "create_gemini_client",
    "get_model_name",
]