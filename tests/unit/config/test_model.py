"""Tests for model configuration."""

import pytest
from unittest.mock import patch, MagicMock
from src.config.model import create_gemini_client, get_model_name


class TestModelConfig:
    """Tests for model configuration."""

    @patch("src.config.model.get_settings")
    def test_create_gemini_client(self, mock_get_settings):
        """Test that create_gemini_client returns AsyncOpenAI with correct config."""
        mock_settings = MagicMock()
        mock_settings.gemini_api_key = "test-api-key"
        mock_settings.openai_base_url = "https://custom.example.com/v1"
        mock_get_settings.return_value = mock_settings

        client = create_gemini_client()

        assert client.api_key == "test-api-key"
        assert str(client.base_url) == "https://custom.example.com/v1/"

    @patch("src.config.model.get_settings")
    def test_get_model_name(self, mock_get_settings):
        """Test that get_model_name returns the configured model."""
        mock_settings = MagicMock()
        mock_settings.model_name = "gemini-2.5-flash"
        mock_get_settings.return_value = mock_settings

        assert get_model_name() == "gemini-2.5-flash"

    @patch("src.config.model.get_settings")
    def test_model_name_custom(self, mock_get_settings):
        """Test that get_model_name returns custom model name."""
        mock_settings = MagicMock()
        mock_settings.model_name = "custom-model"
        mock_get_settings.return_value = mock_settings

        assert get_model_name() == "custom-model"