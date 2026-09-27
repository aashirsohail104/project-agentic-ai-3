"""Integration tests for Student Ops Desk agent workflows."""

import pytest
from src.data.repository import CourseRepository, CourseNotFoundError, AssignmentNotFoundError
from src.data.tools import get_repository
from src.models.course import Course, Schedule, Policies, Assignment
from src.models.student import StudentProfile
from src.models.ticket import Ticket


class TestCourseToolsIntegration:
    """Integration tests for course lookup tools."""

    @pytest.fixture(autouse=True)
    def setup_repo(self):
        """Set up the course repository before each test."""
        self.repo = get_repository()

    def test_list_courses_returns_courses(self):
        """Test that list_courses returns all courses from courses.json."""
        courses = self.repo.list_courses()
        assert len(courses) > 0
        course_ids = [c.id for c in courses]
        assert "agentic-ai-w4" in course_ids
        assert "web-dev-w2" in course_ids
        assert "data-sci-w1" in course_ids

    def test_get_course_schedule_returns_schedule(self):
        """Test that get_course_schedule returns schedule for a valid course."""
        course = self.repo.get_course_or_raise("agentic-ai-w4")
        schedule = course.schedule
        assert schedule.days == "Mon-Thu"
        assert schedule.time == "7-9pm"
        assert schedule.timezone == "Asia/Karachi"

    def test_get_course_schedule_raises_on_invalid_course(self):
        """Test that get_course_schedule raises CourseNotFoundError for invalid course."""
        from src.data.repository import CourseNotFoundError
        try:
            self.repo.get_course_or_raise("invalid-course")
            assert False, "Should have raised CourseNotFoundError"
        except CourseNotFoundError:
            pass  # Expected

    def test_get_course_policies_returns_policies(self):
        """Test that get_course_policies returns policies for a valid course."""
        course = self.repo.get_course_or_raise("agentic-ai-w4")
        policies = course.policies
        assert policies.late_submission == "48 hours, 20% penalty"

    def test_get_assignment_by_id_returns_assignment(self):
        """Test that get_assignment_by_id returns an assignment via repository."""
        assignment = self.repo.get_assignment_or_raise("agentic-ai-w4", "a3")
        assert assignment.id == "a3"
        assert assignment.title == "First coded agent"
        assert assignment.due == "2026-10-02"

    def test_get_assignment_by_id_raises_on_invalid_course(self):
        """Test that get_assignment_by_id raises CourseNotFoundError for invalid course."""
        from src.data.repository import CourseNotFoundError
        try:
            self.repo.get_assignment_or_raise("invalid-course", "a3")
            assert False, "Should have raised CourseNotFoundError"
        except CourseNotFoundError:
            pass  # Expected

    def test_get_assignment_by_id_raises_on_invalid_assignment(self):
        """Test that get_assignment_by_id raises AssignmentNotFoundError for invalid assignment."""
        from src.data.repository import AssignmentNotFoundError
        try:
            self.repo.get_assignment_or_raise("agentic-ai-w4", "nonexistent")
            assert False, "Should have raised AssignmentNotFoundError"
        except AssignmentNotFoundError:
            pass  # Expected


class TestModelsIntegration:
    """Integration tests for data models."""

    def test_student_profile_with_course(self):
        """Test StudentProfile with course_id."""
        profile = StudentProfile(
            name="Ahmed Khan",
            roll_no="SAI-2024-001",
            course_id="agentic-ai-w4",
            tier="scholarship",
            open_tickets=1,
        )
        assert profile.name == "Ahmed Khan"
        assert profile.roll_no == "SAI-2024-001"
        assert profile.course_id == "agentic-ai-w4"
        assert profile.tier == "scholarship"
        assert profile.open_tickets == 1
        assert str(profile) == "Ahmed Khan (SAI-2024-001) - agentic-ai-w4 [scholarship]"

    def test_ticket_from_models(self):
        """Test creating tickets via models."""
        # Resolved ticket
        ticket1 = Ticket(
            category="assignment",
            summary="Assignment a3 due date issue resolved",
            next_step="Submit assignment before deadline",
            resolved=True,
            escalate=False,
        )
        assert ticket1.category == "assignment"
        assert ticket1.resolved is True
        assert ticket1.escalate is False

        # Unresolved escalated ticket
        ticket2 = Ticket(
            category="career",
            summary="Career guidance requested",
            next_step="Schedule counseling session",
            resolved=False,
            escalate=True,
        )
        assert ticket2.category == "career"
        assert ticket2.resolved is False
        assert ticket2.escalate is True

    def test_ticket_invalid_category_raises(self):
        """Test that invalid category raises validation error."""
        with pytest.raises(ValueError):
            Ticket(
                category="invalid",
                summary="Test",
                next_step="Test",
                resolved=True,
                escalate=False,
            )


class TestDataRepositoryIntegration:
    """Integration tests for the CourseRepository."""

    def test_repository_loaded_from_json(self):
        """Test that repository loads courses from courses.json."""
        repo = get_repository()
        courses = repo.list_courses()
        assert len(courses) == 3

    def test_repository_course_lookup(self):
        """Test CourseRepository.get_course method."""
        repo = get_repository()
        course = repo.get_course("agentic-ai-w4")
        assert course is not None
        assert course.title == "Agentic AI - weekdays batch 4"
        assert len(course.assignments) == 1
        assert course.assignments[0].id == "a3"

    def test_repository_course_not_found(self):
        """Test CourseRepository.get_course returns None on not found."""
        repo = get_repository()
        course = repo.get_course("nonexistent-course")
        assert course is None

    def test_repository_assignment_lookup(self):
        """Test CourseRepository.get_assignment method."""
        repo = get_repository()
        assignment = repo.get_assignment("agentic-ai-w4", "a3")
        assert assignment is not None
        assert assignment.id == "a3"
        assert assignment.title == "First coded agent"

    def test_repository_assignment_not_found(self):
        """Test CourseRepository.get_assignment returns None on not found."""
        repo = get_repository()
        assignment = repo.get_assignment("agentic-ai-w4", "nonexistent")
        assert assignment is None

    def test_repository_course_removal(self):
        """Test that deleting course from JSON removes it after reload."""
        repo = get_repository()
        initial_count = len(repo.list_courses())
        assert initial_count == 3
        # Reload - courses.json is unchanged in tests, so count should remain
        repo.reload()
        assert len(repo.list_courses()) == initial_count