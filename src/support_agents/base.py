"""Base Student Support Agent with dynamic instructions."""

from typing import Optional
from agents import Agent, RunContextWrapper, GuardrailFunctionOutput, InputGuardrail
from pydantic import BaseModel

from src.config import create_gemini_client, get_model_name
from src.context import StudentContext, get_student_from_context
from src.data.tools import (
    list_courses,
    get_course_schedule,
    get_course_policies,
    get_assignment_by_id,
)
from src.guardrails.input_guardrail import create_input_guardrail
from src.hooks.run_hooks import RunHooks
from src.hooks.agent_hooks import AgentHooks
from .assignments import assignments_agent
from .careers import careers_agent
from .handoffs import create_assignments_handoff, create_careers_handoff
from src.tools.summarizer import summarize_text
from src.tools.ticket_tools import close_ticket


# Model configuration - agent level, not global
MODEL_NAME = get_model_name()


class GuardrailOutput(BaseModel):
    """Output of the input guardrail."""

    is_course_related: bool
    reason: str


def build_dynamic_instructions(ctx: RunContextWrapper[StudentContext], agent: Agent) -> str:
    """Build system prompt dynamically from student profile.

    The prompt is built at request time from the profile:
    - Greets the student by name
    - Names the course they are enrolled in
    - Becomes terser once open_tickets >= 3
    """
    student = get_student_from_context(ctx)

    # Base instructions
    base_instructions = f"""You are the Saylani Student Ops Desk - the front door for student questions about this bootcamp.

STUDENT CONTEXT:
- Name: {student.name}
- Roll Number: {student.roll_no}
- Course: {student.course_id}
- Tier: {student.tier}
- Open Tickets: {student.open_tickets}

YOUR ROLE:
1. Determine if the question is about an assignment, career, or course administration
2. Answer from real course data using your tools
3. Refuse anything that isn't about the course
4. Close every conversation with a structured ticket

TOOLS AVAILABLE:
- list_courses: List all available courses
- get_course_schedule: Get schedule for a course
- get_course_policies: Get policies for a course
- get_assignment_by_id: Look up an assignment by ID

HANDOFFS:
- Assignments Specialist: For assignment-specific questions
- Careers Specialist: For career guidance questions

RULES:
- Never invent course information not in your tools
- If a question is off-topic, the guardrail will catch it
- Always produce a Ticket as your final output when resolved
- Use close_ticket tool to end the conversation with a ticket"""

    # Terser mode for students with many open tickets
    if student.open_tickets >= 3:
        base_instructions += """

TERSE MODE ACTIVE: This student has 3+ open tickets. Be concise and direct."""

    return base_instructions


def create_base_agent() -> Agent[StudentContext]:
    """Create the base student support agent.

    The model is configured at the agent level through an OpenAI-compatible client.
    No set_default_openai_client appears anywhere.
    """
    # Create handoffs to specialist agents
    assignments_handoff = create_assignments_handoff(assignments_agent)
    careers_handoff = create_careers_handoff(careers_agent)

    return Agent[StudentContext](
        name="StudentOpsDesk",
        instructions=build_dynamic_instructions,
        model=MODEL_NAME,
        tools=[
            list_courses,
            get_course_schedule,
            get_course_policies,
            get_assignment_by_id,
            summarize_text,
            close_ticket,
        ],
        handoffs=[assignments_handoff, careers_handoff],
        input_guardrails=[create_input_guardrail()],
        hooks=AgentHooks("StudentOpsDesk"),
    )


# Create the base agent instance
base_agent = create_base_agent()