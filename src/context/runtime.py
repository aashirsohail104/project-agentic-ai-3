"""Student runtime context - injected at runtime, never in prompts."""

from dataclasses import dataclass
from typing import Any
from agents import RunContextWrapper


@dataclass
class StudentContext:
    """Runtime context containing the student profile.

    This is passed to every run as local context. Tools read from it.
    The prompt text never contains the student's name, roll number, or tier.
    """

    profile: "StudentProfile"

    def get_profile(self) -> "StudentProfile":
        """Get the student profile."""
        return self.profile


# Import here to avoid circular dependency
from models.student import StudentProfile


def create_student_context(profile: StudentProfile) -> StudentContext:
    """Create a StudentContext from a StudentProfile."""
    return StudentContext(profile=profile)


def get_student_from_context(ctx: RunContextWrapper[StudentContext]) -> StudentProfile:
    """Extract student profile from run context wrapper.

    This is the pattern tools should use - they read from context,
    not from a wrapper parameter in the tool schema.
    """
    return ctx.context.profile