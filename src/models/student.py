"""Student profile model."""

from dataclasses import dataclass
from typing import Literal


@dataclass
class StudentProfile:
    """Student profile passed as runtime context.

    Never hardcoded into prompts - injected via RunContextWrapper.
    """

    name: str
    roll_no: str
    course_id: str
    tier: Literal["regular", "scholarship"] = "regular"
    open_tickets: int = 0

    def __str__(self) -> str:
        return f"{self.name} ({self.roll_no}) - {self.course_id} [{self.tier}]"