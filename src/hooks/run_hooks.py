"""Run-level hooks for audit trail."""

from typing import Any
from agents import RunHooks, RunContextWrapper, Agent, Tool, Handoff
from src.context import StudentContext


class RunHooksImpl(RunHooks):
    """Run-level hooks that record an ordered timeline of all agent activity.

    These hooks fire for every agent in the run, including during handoffs.
    """

    def __init__(self):
        self.timeline: list[dict[str, Any]] = []

    def _record(self, event: str, agent_name: str, details: dict[str, Any] | None = None) -> None:
        entry = {"event": event, "agent": agent_name}
        if details:
            entry.update(details)
        self.timeline.append(entry)

    async def on_agent_start(self, context: RunContextWrapper[StudentContext], agent: Agent[StudentContext]) -> None:
        self._record("agent_start", agent.name)

    async def on_agent_end(self, context: RunContextWrapper[StudentContext], agent: Agent[StudentContext], output: Any) -> None:
        self._record("agent_end", agent.name, {"output_type": type(output).__name__})

    async def on_handoff(self, context: RunContextWrapper[StudentContext], from_agent: Agent[StudentContext], to_agent: Agent[StudentContext]) -> None:
        self._record("handoff", from_agent.name, {"to_agent": to_agent.name})

    async def on_tool_start(self, context: RunContextWrapper[StudentContext], agent: Agent[StudentContext], tool: Tool) -> None:
        self._record("tool_start", agent.name, {"tool": tool.name})

    async def on_tool_end(self, context: RunContextWrapper[StudentContext], agent: Agent[StudentContext], tool: Tool, result: Any) -> None:
        self._record("tool_end", agent.name, {"tool": tool.name, "result_type": type(result).__name__})

    def get_timeline(self) -> list[dict[str, Any]]:
        """Get the recorded timeline."""
        return self.timeline.copy()


# Alias for backward compatibility
RunHooks = RunHooksImpl