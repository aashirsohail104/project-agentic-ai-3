"""Handoff logic for specialist agents."""

from typing import Any
from agents import Agent, Handoff
from src.context import StudentContext
from src.config import get_model_name

MODEL_NAME = get_model_name()


async def _invoke_assignments_handoff(ctx: Any, _: Any) -> Agent[StudentContext]:
    """Invoke handler for assignments handoff - imports locally to avoid circular imports."""
    from src.support_agents.assignments import assignments_agent
    return assignments_agent


async def _invoke_careers_handoff(ctx: Any, _: Any) -> Agent[StudentContext]:
    """Invoke handler for careers handoff - imports locally to avoid circular imports."""
    from src.support_agents.careers import careers_agent
    return careers_agent


def create_assignments_handoff(assignments_agent: Agent[StudentContext]) -> Handoff:
    """Create handoff to Assignments Specialist."""
    return Handoff(
        tool_name="transfer_to_assignments_specialist",
        tool_description="Transfer to the Assignments Specialist for assignment-specific questions.",
        agent_name="AssignmentsSpecialist",
        input_json_schema={"type": "object", "properties": {}, "additionalProperties": False},
        on_invoke_handoff=_invoke_assignments_handoff,
    )


def create_careers_handoff(careers_agent: Agent[StudentContext]) -> Handoff:
    """Create handoff to Careers Specialist."""
    return Handoff(
        tool_name="transfer_to_careers_specialist",
        tool_description="Transfer to the Careers Specialist for career guidance questions.",
        agent_name="CareersSpecialist",
        input_json_schema={"type": "object", "properties": {}, "additionalProperties": False},
        on_invoke_handoff=_invoke_careers_handoff,
    )