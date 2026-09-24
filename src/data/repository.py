"""Course repository - reads course data from courses.json."""

import json
from pathlib import Path
from typing import Optional
from models.course import Course, Assignment, Schedule, Policies


class CourseNotFoundError(Exception):
    """Raised when a course is not found."""

    pass


class AssignmentNotFoundError(Exception):
    """Raised when an assignment is not found."""

    pass


class CourseRepository:
    """Repository for accessing course data from courses.json.

    The agent can only reach course information through this repository's tools.
    Course facts live in courses.json and are never embedded in prompts.
    """

    def __init__(self, data_path: Optional[str] = None):
        """Initialize the repository.

        Args:
            data_path: Path to courses.json. Defaults to src/data/courses.json
        """
        if data_path is None:
            data_path = Path(__file__).parent / "courses.json"
        self.data_path = Path(data_path)
        self._courses: dict[str, Course] = {}
        self._load()

    def _load(self) -> None:
        """Load courses from JSON file."""
        with open(self.data_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        for course_data in data.get("courses", []):
            course = Course(
                id=course_data["id"],
                title=course_data["title"],
                schedule=Schedule(**course_data["schedule"]),
                policies=Policies(**course_data["policies"]),
                assignments=[Assignment(**a) for a in course_data.get("assignments", [])],
            )
            self._courses[course.id] = course

    def list_courses(self) -> list[Course]:
        """List all available courses."""
        return list(self._courses.values())

    def get_course(self, course_id: str) -> Optional[Course]:
        """Get a course by ID.

        Args:
            course_id: The course identifier

        Returns:
            Course if found, None otherwise
        """
        return self._courses.get(course_id)

    def get_course_or_raise(self, course_id: str) -> Course:
        """Get a course by ID, raising if not found.

        Args:
            course_id: The course identifier

        Returns:
            Course

        Raises:
            CourseNotFoundError: If course not found
        """
        course = self._courses.get(course_id)
        if course is None:
            raise CourseNotFoundError(f"Course '{course_id}' not found")
        return course

    def get_assignment(self, course_id: str, assignment_id: str) -> Optional[Assignment]:
        """Get an assignment by course ID and assignment ID.

        Args:
            course_id: The course identifier
            assignment_id: The assignment identifier

        Returns:
            Assignment if found, None otherwise
        """
        course = self._courses.get(course_id)
        if course is None:
            return None
        for assignment in course.assignments:
            if assignment.id == assignment_id:
                return assignment
        return None

    def get_assignment_or_raise(self, course_id: str, assignment_id: str) -> Assignment:
        """Get an assignment, raising if not found.

        Args:
            course_id: The course identifier
            assignment_id: The assignment identifier

        Returns:
            Assignment

        Raises:
            CourseNotFoundError: If course not found
            AssignmentNotFoundError: If assignment not found
        """
        course = self.get_course_or_raise(course_id)
        assignment = self.get_assignment(course_id, assignment_id)
        if assignment is None:
            raise AssignmentNotFoundError(
                f"Assignment '{assignment_id}' not found in course '{course_id}'"
            )
        return assignment

    def reload(self) -> None:
        """Reload courses from file (useful after external changes)."""
        self._courses.clear()
        self._load()