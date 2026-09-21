"""Models package for Student Ops Desk."""

from src.models.student import StudentProfile
from src.models.course import Course, Schedule, Policies, Assignment
from src.models.ticket import Ticket

__all__ = [
    "StudentProfile",
    "Course",
    "Schedule",
    "Policies",
    "Assignment",
    "Ticket",
]