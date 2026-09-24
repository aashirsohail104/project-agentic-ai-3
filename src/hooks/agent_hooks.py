"""Agent-level hooks for specialist audit trail."""

from typing import Any
from agents import AgentHooks, RunContextWrapper, Agent, Tool
from context import StudentContext


class AgentHooksImpl(AgentHooks):
    """Agent-level hooks attached to exactly one specialist.

    These hooks go quiet at handoff moment (only fire for the specialist they're attached to).
    """

    def __init__(self, specialist_name: str):
        self.specialist_name = specialist_name
        self.events: list[dict[str, Any]] = []

    def _record(self, event: str, details: dict[str, Any] | None = None) -> None:
        entry = {"specialist": self.specialist_name, "event": event}
        if details:
            entry.update(details)
        self.events.append(entry)

    async def on_agent_start(self, context: RunContextWrapper[StudentContext], agent: Agent[StudentContext]) -> None:
        self._record("agent_start")

    async def on_agent_end(self, context: RunContextWrapper[StudentContext], agent: Agent[StudentContext], output: Any) -> None:
        self._record("agent_end", {"output_type": type(output).__name__})

    async def on_tool_start(self, context: RunContextWrapper[StudentContext], agent: Agent[StudentContext], tool: Tool) -> None:
        self._record("tool_start", {"tool": tool.name})

    async def on_tool_end(self, context: RunContextWrapper[StudentContext], agent: Agent[StudentContext], tool: Tool, result: Any) -> None:
        self._record("tool_end", {"tool": tool.name, "result_type": type(result).__name__})

    def get_events(self) -> list[dict[str, Any]]:
        """Get the recorded events for this specialist."""
        return self.events.copy()


# Alias for backward compatibility
AgentHooks = AgentHooksImpl