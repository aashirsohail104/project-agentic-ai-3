"""Handoff logic for specialist agents."""

from agents import Agent, Handoff
from src.context import StudentContext
from src.config import get_model_name
from typing import Any

MODEL_NAME = get_model_name()


def create_assignments_handoff(assignments_agent: Agent[StudentContext]) -> Handoff:
    """Create handoff to Assignments Specialist."""
    return Handoff(
        tool_name="transfer_to_assignments_specialist",
        tool_description="Transfer to the Assignments Specialist for assignment-specific questions.",
        agent_name="AssignmentsSpecialist",
        input_json_schema={"type": "object", "properties": {}, "additionalProperties": False},
        on_invoke_handoff=lambda ctx, _: assignments_agent,
    )


def create_careers_handoff(careers_agent: Agent[StudentContext]) -> Handoff:
    """Create handoff to Careers Specialist."""
    return Handoff(
        tool_name="transfer_to_careers_specialist",
        tool_description="Transfer to the Careers Specialist for career guidance questions.",
        agent_name="CareersSpecialist",
        input_json_schema={"type": "object", "properties": {}, "additionalProperties": False},
        on_invoke_handoff=lambda ctx, _: careers_agent,
    )