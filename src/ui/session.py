"""Per-session state management for Chainlit UI."""

from typing import Any
import chainlit as cl
from src.context import StudentContext, create_student_context
from models.student import StudentProfile
from agents import RunContextWrapper
from src.runner import run_with_tracking
from src.support_agents.base import base_agent


class SessionState:
    """Manages per-session state for a student conversation.

    - Agent and student profile built once per session
    - Conversation history maintained
    - Isolated between browser windows/sessions
    """

    def __init__(self, profile: StudentProfile):
        self.profile = profile
        self.context = create_student_context(profile)
        self.agent = base_agent
        self.history: list[dict] = []
        self.conversation_id = f"conv_{id(self)}"

    def get_context_wrapper(self) -> RunContextWrapper[StudentContext]:
        """Get a RunContextWrapper for the current session."""
        return RunContextWrapper(context=self.context)

    def add_to_history(self, role: str, content: str) -> None:
        """Add a message to the conversation history."""
        self.history.append({"role": role, "content": content})

    def get_history(self) -> list[dict]:
        """Get the conversation history."""
        return self.history.copy()


def create_session_state(profile: StudentProfile) -> SessionState:
    """Create a new session state for a student."""
    return SessionState(profile)


async def get_or_create_session() -> SessionState:
    """Get or create the session state from Chainlit user session."""
    session_state = cl.user_session.get("session_state")
    if session_state is None:
        # For demo: create a default student profile
        # In production, this would come from authentication
        profile = StudentProfile(
            name="Demo Student",
            roll_no="SAI-2024-001",
            course_id="agentic-ai-w4",
            tier="regular",
            open_tickets=0,
        )
        session_state = create_session_state(profile)
        cl.user_session.set("session_state", session_state)
    return session_state


async def run_agent_in_session(question: str) -> Any:
    """Run the agent for the current session with the given question."""
    session = await get_or_create_session()

    # Add user message to history
    session.add_to_history("user", question)

    # Run the agent with session context
    context_wrapper = session.get_context_wrapper()
    result = await run_with_tracking(
        starting_agent=session.agent,
        input=question,
        context=context_wrapper,
    )

    # Add agent response to history
    if hasattr(result, "final_output"):
        session.add_to_history("assistant", str(result.final_output))

    return result