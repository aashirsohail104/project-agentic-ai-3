"""Careers Specialist Agent - cloned from base, warmer tone."""

from agents import Agent
from src.context import StudentContext, get_student_from_context
from src.config import get_model_name

MODEL_NAME = get_model_name()


def build_careers_instructions(ctx: StudentContext, agent: Agent) -> str:
    """Build system prompt for Careers Specialist.

    Warmer, encouraging tone. Focused on career guidance.
    """
    student = get_student_from_context(ctx)

    return f"""You are the Careers Specialist for the Saylani Student Ops Desk.

STUDENT CONTEXT:
- Name: {student.name}
- Roll Number: {student.roll_no}
- Course: {student.course_id}
- Tier: {student.tier}
- Open Tickets: {student.open_tickets}

YOUR ROLE:
- Provide thoughtful career guidance for bootcamp students
- Be warm, encouraging, and supportive in your tone
- Draw on general career knowledge for tech roles (interviews, portfolios, job search)
- If the question is about a specific assignment or course admin, say so and the base agent will handle it

RULES:
- Do not use course tools — career guidance comes from your training
- Be supportive but realistic about job market expectations
- Focus on actionable next steps: portfolio, interview prep, networking
- When you have provided guidance, the base agent will close with a ticket"""


def create_careers_agent() -> Agent[StudentContext]:
    """Create the Careers Specialist agent.

    Cloned from base agent but with different instructions and no course tools.
    Shares the same model configuration.
    """
    return Agent[StudentContext](
        name="CareersSpecialist",
        instructions=build_careers_instructions,
        model=MODEL_NAME,
        tools=[],
        handoffs=[],
    )


# Create the careers agent instance
careers_agent = create_careers_agent()