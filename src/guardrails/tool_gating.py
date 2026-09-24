"""Tool gating - scholarship-only tools."""

from agents import Agent, RunContextWrapper
from context import StudentContext, get_student_from_context


def is_scholarship_student(ctx: RunContextWrapper[StudentContext]) -> bool:
    """Check if the student has scholarship tier."""
    student = get_student_from_context(ctx)
    return student.tier == "scholarship"


def get_tools_for_student_tier(ctx: RunContextWrapper[StudentContext], all_tools: list) -> list:
    """Filter tools based on student tier.

    Scholarship students get all tools.
    Regular students get a subset (no priority/close_ticket if gated).
    """
    if is_scholarship_student(ctx):
        return all_tools

    # Regular students: filter out scholarship-only tools
    scholarship_only_tool_names = {"close_ticket"}  # Tools only for scholarship
    return [tool for tool in all_tools if tool.name not in scholarship_only_tool_names]