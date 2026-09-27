"""Summarizer tool - condenses long policy answers to 3 lines."""

from agents import function_tool, RunContextWrapper
from pydantic import BaseModel
from src.context import StudentContext


class SummarizerInput(BaseModel):
    """Input for the summarizer tool."""

    text: str


class SummarizerOutput(BaseModel):
    """Output from the summarizer tool."""

    summary: str


@function_tool
async def summarize_text(
    ctx: RunContextWrapper[StudentContext],
    input: SummarizerInput,
) -> SummarizerOutput:
    """Condense long text into a 3-line summary.

    The Desk (base agent) calls this tool and continues the conversation
    in its own voice after receiving the summary.

    Args:
        text: The text to summarize (typically a long policy explanation)

    Returns:
        A 3-line summary
    """
    text = input.text.strip()

    # Simple extraction-based summarization: take first 3 sentences
    # In production, this could use an LLM call
    sentences = [s.strip() for s in text.split(".") if s.strip()]

    if len(sentences) <= 3:
        summary = text
    else:
        summary = ". ".join(sentences[:3]) + "."

    return SummarizerOutput(summary=summary)