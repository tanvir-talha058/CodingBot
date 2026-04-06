"""In-memory conversation history manager."""

from __future__ import annotations

from collections import defaultdict, deque

import config


class ConversationHistory:
    """Stores per-user conversation turns (role/content pairs).

    Keeps only the last ``MAX_HISTORY`` turns to stay within token limits.
    """

    def __init__(self, max_turns: int = config.MAX_HISTORY) -> None:
        self._max_turns = max_turns
        self._history: dict[int, deque[dict[str, str]]] = defaultdict(
            lambda: deque(maxlen=max_turns * 2)  # each turn = user + assistant
        )

    def add_user(self, user_id: int, content: str) -> None:
        """Append a user message."""
        self._history[user_id].append({"role": "user", "content": content})

    def add_assistant(self, user_id: int, content: str) -> None:
        """Append an assistant message."""
        self._history[user_id].append({"role": "assistant", "content": content})

    def get(self, user_id: int) -> list[dict[str, str]]:
        """Return the full conversation history for a user."""
        return list(self._history[user_id])

    def clear(self, user_id: int) -> None:
        """Clear conversation history for a user."""
        self._history[user_id].clear()


# Shared singleton used across handlers
history = ConversationHistory()
