"""Course-related models."""

from pydantic import BaseModel, Field
from typing import Literal


class Schedule(BaseModel):
    """Course schedule information."""

    days: str = Field(description="Days of the week (e.g., 'Mon-Thu')")
    time: str = Field(description="Time range (e.g., '7-9pm')")
    timezone: str = Field(default="UTC", description="Timezone")


class Policies(BaseModel):
    """Course policies."""

    late_submission: str = Field(description="Late submission policy")


class Assignment(BaseModel):
    """Course assignment."""

    id: str = Field(description="Assignment ID")
    title: str = Field(description="Assignment title")
    due: str = Field(description="Due date (YYYY-MM-DD)")


class Course(BaseModel):
    """Course information from courses.json."""

    id: str = Field(description="Unique course identifier")
    title: str = Field(description="Course title")
    schedule: Schedule
    policies: Policies
    assignments: list[Assignment] = Field(default_factory=list)