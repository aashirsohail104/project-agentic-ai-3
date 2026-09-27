"""Input guardrail - rejects non-course questions before the Desk model runs."""

from agents import GuardrailFunctionOutput, InputGuardrailTripwireTriggered, InputGuardrail
from agents import RunContextWrapper, Agent
from pydantic import BaseModel
from src.context import StudentContext


class GuardrailOutput(BaseModel):
    """Output of the input guardrail."""

    is_course_related: bool
    reason: str


# Keywords that indicate course-related questions
COURSE_KEYWORDS = [
    "assignment", "homework", "project", "due", "deadline", "submit", "grade",
    "schedule", "class", "lecture", "session", "time", "day", "week",
    "policy", "late", "penalty", "extension", "absence", "attendance",
    "course", "curriculum", "syllabus", "module", "topic", "lesson",
    "career", "job", "interview", "resume", "portfolio", "placement",
    "instructor", "teacher", "mentor", "ta", "assistant",
    "exam", "quiz", "test", "assessment", "evaluation",
    "bootcamp", "program", "batch", "cohort", "enrollment",
    "fee", "payment", "scholarship", "financial", "aid",
    "certificate", "completion", "graduation", "alumni",
]


async def input_guardrail_function(
    ctx: RunContextWrapper[StudentContext],
    agent: Agent,
    input: str | list,
) -> GuardrailFunctionOutput:
    """Check if the input is related to the course/bootcamp.

    This runs BEFORE the model, so off-topic questions are rejected cheaply.
    """
    # Convert input to string for checking
    if isinstance(input, list):
        # For list inputs (message history), check the last user message
        user_messages = [msg for msg in input if isinstance(msg, dict) and msg.get("role") == "user"]
        if user_messages:
            text = user_messages[-1].get("content", "").lower()
        else:
            text = ""
    else:
        text = str(input).lower()

    # Check for course-related keywords
    is_related = any(keyword in text for keyword in COURSE_KEYWORDS)

    # Also allow greetings and basic interactions (including variations)
    greetings = ["hello", "hi", "hey", "thanks", "thank you", "ok", "okay", "yes", "no"]
    text_lower = text.strip().lower()
    is_greeting = any(text_lower.startswith(greeting) for greeting in greetings)

    # Allow profile/identity queries (student context)
    profile_keywords = ["profile", "identity", "who am i", "my info", "my details", "student"]
    is_profile_query = any(keyword in text_lower for keyword in profile_keywords)

    if is_related or is_greeting or is_profile_query:
        return GuardrailFunctionOutput(
            output_info=GuardrailOutput(is_course_related=True, reason="Course-related, greeting, or profile query"),
            tripwire_triggered=False,
        )

    # Off-topic - trigger the tripwire
    return GuardrailFunctionOutput(
        output_info=GuardrailOutput(
            is_course_related=False,
            reason="Question does not appear to be related to the bootcamp courses, assignments, careers, or administration",
        ),
        tripwire_triggered=True,
    )


def create_input_guardrail() -> InputGuardrail:
    """Create the input guardrail for the base agent."""
    return InputGuardrail(guardrail_function=input_guardrail_function)


# Handler for when guardrail trips
async def handle_guardrail_tripwire(ctx, agent, input):
    """Handle a guardrail tripwire - polite refusal without model call."""
    return "I'm here to help with questions about your bootcamp courses, assignments, schedules, policies, or career guidance. I can't help with topics outside of the program. Is there something about your coursework I can assist you with?"