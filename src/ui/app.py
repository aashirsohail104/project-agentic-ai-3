"""Chainlit UI application for Student Ops Desk."""

import chainlit as cl
from ui.session import get_or_create_session, run_agent_in_session
from tracing import configure_tracing


# Configure tracing on startup
configure_tracing()


@cl.on_chat_start
async def on_chat_start():
    """Initialize the session when a new chat starts.

    This runs once per browser session. The agent and student profile
    are built once and reused for all messages in this session.
    """
    session = await get_or_create_session()

    # Send welcome message
    await cl.Message(
        content=f"Welcome to the Saylani Student Ops Desk, {session.profile.name}!\n\n"
        f"You're enrolled in **{session.profile.course_id}** ({session.profile.tier} tier).\n\n"
        "Ask me about your assignments, schedule, policies, or career guidance. "
        "I'll answer from real course data and close our conversation with a structured ticket."
    ).send()


@cl.on_message
async def on_message(message: cl.Message):
    """Handle incoming messages from the student.

    The handler awaits the run (async), not a synchronous variant.
    Per-session memory is maintained through Chainlit's user_session.
    """
    question = message.content

    # Show thinking indicator
    msg = cl.Message(content="")
    await msg.send()

    try:
        # Run the agent with the question
        result = await run_agent_in_session(question)

        # Extract the final output
        if hasattr(result, "final_output"):
            output = result.final_output

            # If it's a Ticket, format it nicely
            if hasattr(output, "category"):
                ticket = output
                status = "✅ RESOLVED" if ticket.resolved else "⚠️ UNRESOLVED"
                escalate = " 🔴 ESCALATE" if ticket.escalate else ""
                content = f"{status}{escalate}\n\n**Category:** {ticket.category.upper()}\n**Summary:** {ticket.summary}\n**Next Step:** {ticket.next_step}"
            else:
                content = str(output)
        else:
            content = str(result)

        msg.content = content
        await msg.update()

    except Exception as e:
        msg.content = f"Sorry, I encountered an error: {str(e)}"
        await msg.update()