"""Tests for config settings."""

import pytest
from src.config.settings import Settings, get_settings


class TestSettings:
    """Tests for Settings class."""

    def test_settings_loads_from_env(self, monkeypatch):
        """Test that settings loads from environment variables."""
        monkeypatch.setenv("GEMINI_API_KEY", "test-key-123")
        monkeypatch.setenv("OPENAI_BASE_URL", "https://custom.example.com/v1")
        monkeypatch.setenv("MODEL_NAME", "custom-model")

        settings = Settings()
        assert settings.gemini_api_key == "test-key-123"
        assert settings.openai_base_url == "https://custom.example.com/v1"
        assert settings.model_name == "custom-model"

    def test_settings_defaults(self, monkeypatch):
        """Test that settings has correct defaults."""
        monkeypatch.setenv("GEMINI_API_KEY", "test-key")

        settings = Settings()
        assert settings.openai_base_url == "https://generativelanguage.googleapis.com/v1beta/openai/"
        assert settings.model_name == "gemini-2.5-flash"
        assert settings.chainlit_host == "0.0.0.0"
        assert settings.chainlit_port == 8000
        assert settings.log_level == "INFO"

    def test_validate_required_raises_on_missing_key(self, monkeypatch):
        """Test that validate_required raises clear error on missing key."""
        # Set to placeholder value to simulate missing key
        monkeypatch.setenv("GEMINI_API_KEY", "your_gemini_api_key_here")

        settings = Settings()
        with pytest.raises(ValueError, match="GEMINI_API_KEY is required"):
            settings.validate_required()

    def test_validate_required_passes_with_valid_key(self, monkeypatch):
        """Test that validate_required passes with valid key."""
        monkeypatch.setenv("GEMINI_API_KEY", "valid-api-key-123")

        settings = Settings()
        # Should not raise
        settings.validate_required()

    def test_validate_required_raises_on_placeholder_key(self, monkeypatch):
        """Test that validate_required raises on placeholder key."""
        monkeypatch.setenv("GEMINI_API_KEY", "your_gemini_api_key_here")

        settings = Settings()
        with pytest.raises(ValueError, match="GEMINI_API_KEY is required"):
            settings.validate_required()

    def test_get_settings_cached(self, monkeypatch):
        """Test that get_settings returns cached instance."""
        monkeypatch.setenv("GEMINI_API_KEY", "test-key")

        settings1 = get_settings()
        settings2 = get_settings()
        assert settings1 is settings2