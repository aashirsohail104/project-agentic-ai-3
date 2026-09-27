"""Custom runner - wraps every run with request ID and elapsed time."""

import time
import uuid
from typing import Any, TypeVar
from agents import Runner, RunContextWrapper, RunResult, RunConfig
from agents.models.multi_provider import MultiProvider
from openai import NotFoundError, RateLimitError
from src.context import StudentContext
from src.config.settings import get_settings

T = TypeVar("T")


def _format_quota_error(e: Exception) -> str:
    """Format a user-friendly message for quota/rate limit errors."""
    error_msg = str(e).lower()
    if "quota" in error_msg or "resource_exhausted" in error_msg or "429" in error_msg:
        # Try to extract retry delay from the error
        import re
        delay_match = re.search(r"retry.?delay.*?(\d+)\s*seconds?", str(e), re.IGNORECASE)
        if delay_match:
            delay = int(delay_match.group(1))
            return (
                f"⏳ Gemini API quota temporarily exhausted. "
                f"Please wait approximately {delay} seconds before trying again. "
                f"(Free tier limit: 20 requests/minute)"
            )
        return (
            "⏳ Gemini API quota temporarily exhausted. "
            "Please wait approximately 30 seconds before trying again. "
            "(Free tier limit: 20 requests/minute)"
        )
    return str(e)


def _create_gemini_model_provider() -> MultiProvider:
    """Create a MultiProvider configured for Gemini via OpenAI-compatible endpoint."""
    settings = get_settings()
    return MultiProvider(
        openai_api_key=settings.gemini_api_key,
        openai_base_url=settings.openai_base_url,
        unknown_prefix_mode="model_id",
        openai_use_responses=False,  # Use Chat Completions API, not Responses API
    )


_GEMINI_MODEL_PROVIDER: MultiProvider | None = None


def _get_gemini_model_provider() -> MultiProvider:
    """Get or create the Gemini MultiProvider singleton."""
    global _GEMINI_MODEL_PROVIDER
    if _GEMINI_MODEL_PROVIDER is None:
        _GEMINI_MODEL_PROVIDER = _create_gemini_model_provider()
    return _GEMINI_MODEL_PROVIDER


def _build_run_config(**kwargs) -> RunConfig:
    """Build RunConfig with Gemini model provider, preserving any user-provided settings."""
    run_config = kwargs.pop("run_config", None)
    if isinstance(run_config, dict):
        run_config = RunConfig(**run_config)
    if run_config is None:
        run_config = RunConfig()
    # Always inject our Gemini model provider to ensure correct Gemini configuration
    run_config.model_provider = _get_gemini_model_provider()
    return run_config


class CustomRunner:
    """Custom runner that wraps every run with request ID and elapsed time.

    Registered once at startup, no agent definition changes needed.
    """

    def __init__(self):
        self.run_count = 0

    async def run(
        self,
        starting_agent: Any,
        input: str | list,
        context: RunContextWrapper[StudentContext] | None = None,
        **kwargs,
    ) -> RunResult:
        """Run the agent with request ID and elapsed time tracking."""
        request_id = str(uuid.uuid4())[:8]
        self.run_count += 1

        start_time = time.perf_counter()

        try:
            run_config = _build_run_config(**kwargs)
            result = await Runner.run(starting_agent, input, context=context, run_config=run_config)
            elapsed_ms = int((time.perf_counter() - start_time) * 1000)

            # Attach metadata to result
            result.request_id = request_id
            result.elapsed_ms = elapsed_ms
            result.run_number = self.run_count

            return result
        except RateLimitError as e:
            elapsed_ms = int((time.perf_counter() - start_time) * 1000)
            user_msg = _format_quota_error(e)
            raise RuntimeError(
                f"Run {self.run_count} (request_id={request_id}) failed after {elapsed_ms}ms: {user_msg}"
            ) from e
        except NotFoundError as e:
            elapsed_ms = int((time.perf_counter() - start_time) * 1000)
            raise RuntimeError(
                f"Run {self.run_count} (request_id={request_id}) failed after {elapsed_ms}ms: {e}"
            ) from e
        except Exception as e:
            elapsed_ms = int((time.perf_counter() - start_time) * 1000)
            # Check if it's a quota error wrapped in a generic exception
            if "429" in str(e) or "quota" in str(e).lower() or "resource_exhausted" in str(e).lower():
                user_msg = _format_quota_error(e)
                raise RuntimeError(
                    f"Run {self.run_count} (request_id={request_id}) failed after {elapsed_ms}ms: {user_msg}"
                ) from e
            raise RuntimeError(
                f"Run {self.run_count} (request_id={request_id}) failed after {elapsed_ms}ms: {e}"
            ) from e


# Global runner instance
_runner: CustomRunner | None = None


def get_runner() -> CustomRunner:
    """Get or create the global custom runner."""
    global _runner
    if _runner is None:
        _runner = CustomRunner()
    return _runner


async def run_with_tracking(
    starting_agent: Any,
    input: str | list,
    context: RunContextWrapper[StudentContext] | None = None,
    **kwargs,
) -> RunResult:
    """Convenience function to run with the custom runner."""
    return await get_runner().run(starting_agent, input, context=context, **kwargs)