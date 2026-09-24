"""Tests for course models."""

import pytest
from models.course import Course, Schedule, Policies, Assignment


class TestSchedule:
    """Tests for Schedule model."""

    def test_schedule_creation(self):
        """Test creating a schedule."""
        schedule = Schedule(days="Mon-Thu", time="7-9pm", timezone="Asia/Karachi")
        assert schedule.days == "Mon-Thu"
        assert schedule.time == "7-9pm"
        assert schedule.timezone == "Asia/Karachi"

    def test_schedule_default_timezone(self):
        """Test default timezone."""
        schedule = Schedule(days="Mon-Fri", time="9-11am")
        assert schedule.timezone == "UTC"


class TestPolicies:
    """Tests for Policies model."""

    def test_policies_creation(self):
        """Test creating policies."""
        policies = Policies(late_submission="48 hours, 20% penalty")
        assert policies.late_submission == "48 hours, 20% penalty"


class TestAssignment:
    """Tests for Assignment model."""

    def test_assignment_creation(self):
        """Test creating an assignment."""
        assignment = Assignment(id="a3", title="First coded agent", due="2026-10-02")
        assert assignment.id == "a3"
        assert assignment.title == "First coded agent"
        assert assignment.due == "2026-10-02"


class TestCourse:
    """Tests for Course model."""

    def test_course_creation(self):
        """Test creating a course with all fields."""
        course = Course(
            id="agentic-ai-w4",
            title="Agentic AI - weekdays batch 4",
            schedule=Schedule(days="Mon-Thu", time="7-9pm"),
            policies=Policies(late_submission="48 hours, 20% penalty"),
            assignments=[
                Assignment(id="a3", title="First coded agent", due="2026-10-02")
            ],
        )
        assert course.id == "agentic-ai-w4"
        assert course.title == "Agentic AI - weekdays batch 4"
        assert len(course.assignments) == 1
        assert course.assignments[0].id == "a3"

    def test_course_default_assignments(self):
        """Test default empty assignments list."""
        course = Course(
            id="test-course",
            title="Test Course",
            schedule=Schedule(days="Mon", time="10-12pm"),
            policies=Policies(late_submission="24 hours"),
        )
        assert course.assignments == []