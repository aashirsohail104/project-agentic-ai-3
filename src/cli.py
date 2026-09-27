"""CLI entry point for Student Ops Desk - terminal demo."""

import argparse
import asyncio
from src.context import StudentContext, create_student_context
from models.student import StudentProfile
from agents import RunContextWrapper
from src.runner import run_with_tracking
from src.support_agents.base import base_agent
from src.tracing import configure_tracing


# Configure tracing
configure_tracing()


def create_demo_profile() -> StudentProfile:
    """Create a demo student profile for CLI."""
    return StudentProfile(
        name="Demo Student",
        roll_no="SAI-2024-001",
        course_id="agentic-ai-w4",
        tier="regular",
        open_tickets=0,
    )


async def run_cli(question: str, profile: StudentProfile | None = None) -> None:
    """Run the agent with the given question."""
    if profile is None:
        profile = create_demo_profile()

    context = create_student_context(profile)
    context_wrapper = RunContextWrapper(context=context)

    print(f"🎓 Student: {profile.name} ({profile.roll_no})")
    print(f"📚 Course: {profile.course_id} [{profile.tier}]")
    print(f"❓ Question: {question}")
    print("-" * 60)

    result = await run_with_tracking(
        starting_agent=base_agent,
        input=question,
        context=context_wrapper,
    )

    print(f"🤖 Response:")
    if hasattr(result, "final_output"):
        output = result.final_output
        if hasattr(output, "category"):
            ticket = output
            status = "RESOLVED" if ticket.resolved else "UNRESOLVED"
            escalate = " [ESCALATE]" if ticket.escalate else ""
            print(f"  [{ticket.category.upper()}] {ticket.summary}")
            print(f"  Status: {status}{escalate}")
            print(f"  Next Step: {ticket.next_step}")
        else:
            print(f"  {output}")
    else:
        print(f"  {result}")

    if hasattr(result, "request_id"):
        print(f"\n📋 Request ID: {result.request_id}")
        print(f"⏱️  Elapsed: {result.elapsed_ms}ms")


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(description="Student Ops Desk CLI")
    parser.add_argument("question", nargs="?", help="Question to ask the Desk")
    parser.add_argument("--name", default="Demo Student", help="Student name")
    parser.add_argument("--roll", default="SAI-2024-001", help="Roll number")
    parser.add_argument("--course", default="agentic-ai-w4", help="Course ID")
    parser.add_argument("--tier", default="regular", choices=["regular", "scholarship"], help="Student tier")
    parser.add_argument("--tickets", type=int, default=0, help="Open tickets count")

    args = parser.parse_args()

    if not args.question:
        parser.print_help()
        return

    profile = StudentProfile(
        name=args.name,
        roll_no=args.roll,
        course_id=args.course,
        tier=args.tier,
        open_tickets=args.tickets,
    )

    asyncio.run(run_cli(args.question, profile))


if __name__ == "__main__":
    main()