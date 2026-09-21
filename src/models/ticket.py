"""Ticket model for structured conversation resolution."""

from pydantic import BaseModel, Field
from typing import Literal


class Ticket(BaseModel):
    """Structured ticket produced at conversation resolution.

    This is the final output type for resolved conversations.
    """

    category: Literal["assignment", "career", "admin"] = Field(
        description="Category of the student's question"
    )
    summary: str = Field(description="Brief summary of the issue and resolution")
    next_step: str = Field(description="Recommended next step for the student")
    resolved: bool = Field(description="Whether the question was fully resolved")
    escalate: bool = Field(description="Whether this needs human escalation")

    def __str__(self) -> str:
        status = "RESOLVED" if self.resolved else "UNRESOLVED"
        esc = " [ESCALATE]" if self.escalate else ""
        return f"[{self.category.upper()}] {self.summary} - {status}{esc}"