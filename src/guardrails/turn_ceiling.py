"""Turn ceiling - prevents unbounded agent loops."""

from agents import RunContextWrapper, Agent
from context import StudentContext


class TurnCeilingExceeded(Exception):
    """Raised when the turn ceiling is exceeded."""

    def __init__(self, max_turns: int):
        self.max_turns = max_turns
        super().__init__(f"Turn ceiling exceeded: maximum {max_turns} turns reached")


# Maximum number of turns allowed per conversation
# Default: 10 turns - enough for most Q&A but prevents infinite loops
MAX_TURNS = 10


def check_turn_ceiling(ctx: RunContextWrapper[StudentContext], agent: Agent, turn_count: int) -> None:
    """Check if the turn ceiling has been exceeded.

    Args:
        ctx: Run context wrapper
        agent: The agent
        turn_count: Current turn number (1-indexed)

    Raises:
        TurnCeilingExceeded: If turn_count exceeds MAX_TURNS
    """
    if turn_count > MAX_TURNS:
        raise TurnCeilingExceeded(MAX_TURNS)


def get_max_turns() -> int:
    """Get the configured maximum turns."""
    return MAX_TURNS