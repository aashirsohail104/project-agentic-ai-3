"""Configuration package for Student Ops Desk."""

from src.config.settings import Settings, get_settings
from src.config.model import (
    create_gemini_client,
    get_model_name,
    get_simple_model_name,
    get_complex_model_name,
)
from src.config.model_router import (
    classify_complexity,
    get_model_for_request,
    Complexity,
    RoutingDecision,
)

__all__ = [
    "Settings",
    "get_settings",
    "create_gemini_client",
    "get_model_name",
    "get_simple_model_name",
    "get_complex_model_name",
    "classify_complexity",
    "get_model_for_request",
    "Complexity",
    "RoutingDecision",
]