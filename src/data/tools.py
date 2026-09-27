"""Course lookup tools for the Student Ops Desk agent.

These tools are the ONLY way the agent accesses course information.
Course data lives in courses.json and is never embedded in prompts.
"""

from typing import Optional
from agents import function_tool, RunContextWrapper
from src.context.runtime import StudentContext
from src.data.repository import CourseRepository, CourseNotFoundError, AssignmentNotFoundError
from models.course import Course, Assignment, Schedule, Policies


# Global repository instance (initialized at startup)
_repository: Optional[CourseRepository] = None


def get_repository() -> CourseRepository:
    """Get or create the global course repository."""
    global _repository
    if _repository is None:
        _repository = CourseRepository()
    return _repository


@function_tool
async def list_courses(ctx: RunContextWrapper[StudentContext]) -> list[Course]:
    """List all available courses.

    Returns a list of all courses with their basic information.
    """
    repo = get_repository()
    return repo.list_courses()


@function_tool
async def get_course_schedule(ctx: RunContextWrapper[StudentContext], course_id: str) -> Schedule:
    """Get the schedule for a specific course.

    Args:
        course_id: The course identifier (e.g., "agentic-ai-w4")

    Returns:
        Schedule with days, time, and timezone

    Raises:
        CourseNotFoundError: If course_id not found
    """
    repo = get_repository()
    course = repo.get_course_or_raise(course_id)
    return course.schedule


@function_tool
async def get_course_policies(ctx: RunContextWrapper[StudentContext], course_id: str) -> Policies:
    """Get the policies for a specific course.

    Args:
        course_id: The course identifier (e.g., "agentic-ai-w4")

    Returns:
        Policies including late submission policy

    Raises:
        CourseNotFoundError: If course_id not found
    """
    repo = get_repository()
    course = repo.get_course_or_raise(course_id)
    return course.policies


@function_tool
async def get_assignment_by_id(
    ctx: RunContextWrapper[StudentContext], course_id: str, assignment_id: str
) -> Assignment:
    """Look up an assignment by its ID within a course.

    Args:
        course_id: The course identifier (e.g., "agentic-ai-w4")
        assignment_id: The assignment identifier (e.g., "a3")

    Returns:
        Assignment with id, title, and due date

    Raises:
        CourseNotFoundError: If course_id not found
        AssignmentNotFoundError: If assignment_id not found in that course
    """
    repo = get_repository()
    return repo.get_assignment_or_raise(course_id, assignment_id)