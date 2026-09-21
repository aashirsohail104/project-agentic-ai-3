"""Tests for StudentProfile model."""

import pytest
from src.models.student import StudentProfile


class TestStudentProfile:
    """Tests for StudentProfile."""

    def test_student_profile_creation(self):
        """Test creating a student profile with all fields."""
        profile = StudentProfile(
            name="Ahmed Khan",
            roll_no="SAI-2024-001",
            course_id="agentic-ai-w4",
            tier="scholarship",
            open_tickets=2,
        )
        assert profile.name == "Ahmed Khan"
        assert profile.roll_no == "SAI-2024-001"
        assert profile.course_id == "agentic-ai-w4"
        assert profile.tier == "scholarship"
        assert profile.open_tickets == 2

    def test_student_profile_defaults(self):
        """Test default values for tier and open_tickets."""
        profile = StudentProfile(
            name="Fatima Ali",
            roll_no="SAI-2024-002",
            course_id="agentic-ai-w4",
        )
        assert profile.tier == "regular"
        assert profile.open_tickets == 0

    def test_student_profile_str(self):
        """Test string representation."""
        profile = StudentProfile(
            name="Ahmed Khan",
            roll_no="SAI-2024-001",
            course_id="agentic-ai-w4",
            tier="scholarship",
            open_tickets=2,
        )
        assert str(profile) == "Ahmed Khan (SAI-2024-001) - agentic-ai-w4 [scholarship]"