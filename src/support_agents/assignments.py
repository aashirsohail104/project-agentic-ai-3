"""Assignments Specialist Agent - cloned from base, cold/factual tone."""

from agents import Agent
from context import StudentContext, get_student_from_context
from config import get_model_name

MODEL_NAME = get_model_name()


def build_assignments_instructions(ctx: StudentContext, agent: Agent) -> str:
    """Build system prompt for Assignments Specialist.

    Cold, factual tone. Focused only on assignment details.
    """
    student = get_student_from_context(ctx)

    return f"""You are the Assignments Specialist for the Saylani Student Ops Desk.

STUDENT CONTEXT:
- Name: {student.name}
- Roll Number: {student.roll_no}
- Course: {student.course_id}
- Tier: {student.tier}
- Open Tickets: {student.open_tickets}

YOUR ROLE:
- Answer assignment-specific questions with precise, factual information
- Use only the course tools to retrieve assignment data
- Be concise and direct — no conversational filler
- If the question is not about an assignment, say so and the base agent will handle it

TOOLS AVAILABLE:
- get_assignment_by_id: Look up an assignment by ID within the student's course

RULES:
- Never invent assignment information not in your tools
- Only answer about assignments for the student's enrolled course
- Do not provide career guidance or general course administration answers
- When you have the answer, provide it clearly and stop
- The base agent will close the conversation with a ticket"""


def create_assignments_agent() -> Agent[StudentContext]:
    """Create the Assignments Specialist agent.

    Cloned from base agent but with different instructions and no guardrails/tools
    beyond assignment lookup. Shares the same model configuration.
    """
    return Agent[StudentContext](
        name="AssignmentsSpecialist",
        instructions=build_assignments_instructions,
        model=MODEL_NAME,
        tools=[],
        handoffs=[],
    )


# Create the assignments agent instance
assignments_agent = create_assignments_agent()