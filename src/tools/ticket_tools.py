"""Ticket tools - close_ticket tool that ends the run immediately."""

from agents import function_tool, RunContextWrapper
from pydantic import BaseModel
from src.context import StudentContext
from models.ticket import Ticket


class CloseTicketInput(BaseModel):
    """Input for the close_ticket tool."""

    category: str  # "assignment", "career", "admin"
    summary: str
    next_step: str
    resolved: bool
    escalate: bool


@function_tool
async def close_ticket(
    ctx: RunContextWrapper[StudentContext],
    input: CloseTicketInput,
) -> Ticket:
    """Close the conversation with a structured ticket.

    This tool ends the run immediately - its output becomes the final result.

    Args:
        category: Category of the question (assignment, career, admin)
        summary: Brief summary of the issue and resolution
        next_step: Recommended next step for the student
        resolved: Whether the question was fully resolved
        escalate: Whether this needs human escalation

    Returns:
        Ticket object that becomes the final output of the run
    """
    return Ticket(
        category=input.category,
        summary=input.summary,
        next_step=input.next_step,
        resolved=input.resolved,
        escalate=input.escalate,
    )