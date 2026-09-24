"""Tracing configuration - one trace per student conversation."""

import os
from agents import set_tracing_disabled, set_tracing_export_api_key, trace
from context import StudentContext


def configure_tracing() -> None:
    """Configure tracing for the Student Ops Desk.

    - One trace per complete student conversation
    - Spans named for each agent, tool, and handoff
    - Export under own key (from TRACING_KEY env var)
    """
    tracing_key = os.getenv("TRACING_KEY")

    if tracing_key:
        set_tracing_export_api_key(tracing_key)
    else:
        # Disable tracing if no key provided (for local development)
        set_tracing_disabled(True)


def create_conversation_trace(student_id: str, conversation_id: str):
    """Create a trace for a complete student conversation.

    Args:
        student_id: The student's roll number
        conversation_id: Unique conversation identifier

    Returns:
        A trace context manager
    """
    trace_name = f"student-ops-desk:{student_id}:{conversation_id}"
    return trace(trace_name)


def get_trace_name(student_id: str, conversation_id: str) -> str:
    """Get the trace name for a conversation."""
    return f"student-ops-desk:{student_id}:{conversation_id}"