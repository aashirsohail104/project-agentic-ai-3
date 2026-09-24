"""Hooks package for Student Ops Desk."""

from hooks.run_hooks import RunHooks
from hooks.agent_hooks import AgentHooks

__all__ = [
    "RunHooks",
    "AgentHooks",
]