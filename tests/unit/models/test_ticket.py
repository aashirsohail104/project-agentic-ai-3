"""Tests for Ticket model."""

import pytest
from models.ticket import Ticket


class TestTicket:
    """Tests for Ticket model."""

    def test_ticket_creation_resolved(self):
        """Test creating a resolved ticket."""
        ticket = Ticket(
            category="assignment",
            summary="Student asked about assignment a3 due date. Answered: due 2026-10-02.",
            next_step="Submit assignment before deadline",
            resolved=True,
            escalate=False,
        )
        assert ticket.category == "assignment"
        assert ticket.resolved is True
        assert ticket.escalate is False

    def test_ticket_creation_unresolved_escalate(self):
        """Test creating an unresolved ticket that needs escalation."""
        ticket = Ticket(
            category="admin",
            summary="Student asked about fee structure. Not in course data.",
            next_step="Contact admin office",
            resolved=False,
            escalate=True,
        )
        assert ticket.category == "admin"
        assert ticket.resolved is False
        assert ticket.escalate is True

    def test_ticket_str_resolved(self):
        """Test string representation of resolved ticket."""
        ticket = Ticket(
            category="assignment",
            summary="Assignment due date provided",
            next_step="Submit before deadline",
            resolved=True,
            escalate=False,
        )
        assert "[ASSIGNMENT]" in str(ticket)
        assert "RESOLVED" in str(ticket)
        assert "ESCALATE" not in str(ticket)

    def test_ticket_str_escalated(self):
        """Test string representation of escalated ticket."""
        ticket = Ticket(
            category="career",
            summary="Career guidance requested",
            next_step="Schedule counseling session",
            resolved=False,
            escalate=True,
        )
        assert "[CAREER]" in str(ticket)
        assert "UNRESOLVED" in str(ticket)
        assert "ESCALATE" in str(ticket)

    def test_ticket_category_validation(self):
        """Test that category must be one of the allowed values."""
        # Valid categories
        for cat in ["assignment", "career", "admin"]:
            ticket = Ticket(
                category=cat,
                summary="Test",
                next_step="Test",
                resolved=True,
                escalate=False,
            )
            assert ticket.category == cat

        # Invalid category should raise validation error
        with pytest.raises(ValueError):
            Ticket(
                category="invalid",
                summary="Test",
                next_step="Test",
                resolved=True,
                escalate=False,
            )