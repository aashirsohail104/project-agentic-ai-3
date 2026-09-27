"""Tests for the smart model router."""

import pytest
from src.config.model_router import (
    classify_complexity,
    get_model_for_request,
    Complexity,
    RoutingDecision,
)
from src.config import get_simple_model_name, get_complex_model_name


class TestModelRouter:
    """Tests for the smart model router."""

    def test_simple_question_what_is_course(self):
        """Simple course lookup should use simple model."""
        decision = classify_complexity("What is my course?")
        assert decision.complexity == Complexity.SIMPLE
        assert decision.model_name == get_simple_model_name()

    def test_simple_question_available_courses(self):
        """List available courses should use simple model."""
        decision = classify_complexity("What courses are available?")
        assert decision.complexity == Complexity.SIMPLE
        assert decision.model_name == get_simple_model_name()

    def test_simple_question_schedule(self):
        """Schedule lookup should use simple model."""
        decision = classify_complexity("What is my schedule?")
        assert decision.complexity == Complexity.SIMPLE
        assert decision.model_name == get_simple_model_name()

    def test_simple_question_deadline(self):
        """Deadline lookup should use simple model."""
        decision = classify_complexity("What is the deadline?")
        assert decision.complexity == Complexity.SIMPLE
        assert decision.model_name == get_simple_model_name()

    def test_simple_question_summarize(self):
        """Summarize request should use simple model."""
        decision = classify_complexity("Summarize this short text.")
        assert decision.complexity == Complexity.SIMPLE
        assert decision.model_name == get_simple_model_name()

    def test_simple_question_define_term(self):
        """Definition request should use simple model."""
        decision = classify_complexity("What does 'assignment' mean?")
        assert decision.complexity == Complexity.SIMPLE
        assert decision.model_name == get_simple_model_name()

    def test_complex_debug_request(self):
        """Debugging request should use complex model."""
        decision = classify_complexity("Debug this Python code and explain why the asynchronous handoff is failing.")
        assert decision.complexity == Complexity.COMPLEX
        assert decision.model_name == get_complex_model_name()

    def test_complex_multi_step_reasoning(self):
        """Multi-step reasoning should use complex model."""
        decision = classify_complexity("Analyze my assignment requirements, summarize them, generate a ticket, and hand the task to the assignments specialist.")
        assert decision.complexity == Complexity.COMPLEX
        assert decision.model_name == get_complex_model_name()

    def test_complex_coding_request(self):
        """Coding/debugging keywords should trigger complex model."""
        decision = classify_complexity("Fix this async function that's causing a timeout error.")
        assert decision.complexity == Complexity.COMPLEX
        assert decision.model_name == get_complex_model_name()

    def test_complex_explicit_handoff(self):
        """Explicit handoff request should use complex model."""
        decision = classify_complexity("Transfer me to the assignments specialist.")
        assert decision.complexity == Complexity.COMPLEX
        assert decision.model_name == get_complex_model_name()

    def test_complex_multiple_questions(self):
        """Multiple questions should use complex model."""
        decision = classify_complexity("What is my schedule? Also, what are the policies? And what about assignments?")
        assert decision.complexity == Complexity.COMPLEX
        assert decision.model_name == get_complex_model_name()

    def test_complex_code_indicators(self):
        """Code-like patterns should trigger complex model."""
        decision = classify_complexity("Fix this async def function that returns a promise.")
        assert decision.complexity == Complexity.COMPLEX
        assert decision.model_name == get_complex_model_name()

    def test_complex_long_message(self):
        """Long messages should use complex model."""
        long_message = " ".join(["This is a test sentence."] * 20)  # ~100 words
        decision = classify_complexity(long_message)
        assert decision.complexity == Complexity.COMPLEX
        assert decision.model_name == get_complex_model_name()

    def test_context_conversation_length(self):
        """Long conversation should escalate to complex model."""
        decision = classify_complexity(
            "What is my schedule?",
            context={"conversation_length": 5}
        )
        assert decision.complexity == Complexity.COMPLEX
        assert decision.model_name == get_complex_model_name()

    def test_context_previous_handoffs(self):
        """Previous handoffs should escalate to complex model."""
        decision = classify_complexity(
            "What is my schedule?",
            context={"previous_handoffs": 1}
        )
        assert decision.complexity == Complexity.COMPLEX
        assert decision.model_name == get_complex_model_name()

    def test_context_many_tools_used(self):
        """Many tools used should escalate to complex model."""
        decision = classify_complexity(
            "What is my schedule?",
            context={"tools_used": ["tool1", "tool2", "tool3"]}
        )
        assert decision.complexity == Complexity.COMPLEX
        assert decision.model_name == get_complex_model_name()

    def test_empty_message(self):
        """Empty message should default to simple model."""
        decision = classify_complexity("")
        assert decision.complexity == Complexity.SIMPLE
        assert decision.model_name == get_simple_model_name()

    def test_get_model_for_request_simple(self):
        """Convenience function for simple request."""
        model = get_model_for_request("What is my course?")
        assert model == get_simple_model_name()

    def test_get_model_for_request_complex(self):
        """Convenience function for complex request."""
        model = get_model_for_request("Debug this Python code and implement a new feature.")
        assert model == get_complex_model_name()

    def test_decision_has_reason(self):
        """Decision should include reason for routing."""
        decision = classify_complexity("What is my course?")
        assert decision.reason is not None
        assert len(decision.reason) > 0

    def test_decision_immutable(self):
        """RoutingDecision should be immutable (frozen dataclass)."""
        decision = classify_complexity("What is my course?")
        with pytest.raises(AttributeError):
            decision.complexity = Complexity.COMPLEX


class TestModelRouterIntegration:
    """Integration-style tests for model router with agent context."""

    def test_conversation_escalation(self):
        """Verify that conversation context escalates complexity."""
        # First few messages simple
        for i in range(3):
            decision = classify_complexity(
                f"Question {i}",
                context={"conversation_length": i}
            )
            assert decision.complexity == Complexity.SIMPLE

        # 4th message should escalate
        decision = classify_complexity(
            "Question 4",
            context={"conversation_length": 4}
        )
        assert decision.complexity == Complexity.COMPLEX

    def test_handoff_context_escalation(self):
        """Handoff in context should make subsequent requests complex."""
        decision = classify_complexity(
            "What is my schedule?",
            context={"previous_handoffs": 1}
        )
        assert decision.complexity == Complexity.COMPLEX

    def test_tools_used_context(self):
        """Multiple tools used should escalate."""
        decision = classify_complexity(
            "What is my schedule?",
            context={"tools_used": ["list_courses", "get_course_schedule", "get_course_policies"]}
        )
        assert decision.complexity == Complexity.COMPLEX