"""Bhagavad Gita session management with context compression.

This module implements session state management for multi-turn conversations,
integrating protected context identification and compression.
"""

from typing import Any

from backend.sessions.context_compressor import ContextCompressor
from backend.sessions.protected_context import identify_protected_context


class GitaSession:
    """Manage multi-turn conversation sessions with automatic compression.

    This class maintains:
    - Events log: Full conversation history
    - Session state: Scratchpad for temporary data
    - Compression tracking: Number of compression cycles performed
    """

    def __init__(self, max_tokens: int = 8000, compression_threshold: float = 0.95) -> None:
        """Initialize Gita session.

        Args:
            max_tokens: Maximum token capacity for context window
            compression_threshold: Fraction of capacity to trigger compression (0.0-1.0)

        Raises:
            ValueError: If compression_threshold is not between 0.0 and 1.0
        """
        # Step 1: Initialize events log and state
        self.events: list[dict[str, Any]] = []
        self.session_state: dict[str, Any] = {}
        self.compression_count = 0

        # Step 2: Initialize compressor
        self.compressor = ContextCompressor(max_tokens=max_tokens, trigger_threshold=compression_threshold)

    def append_event(self, turn: int, role: str, content: str, event_type: str) -> None:
        """Append a conversation event to the session.

        Args:
            turn: Turn number (0-indexed)
            role: Speaker role (user, assistant, system)
            content: Event content
            event_type: Event type (initial_objective, constraint, casual, etc.)

        Raises:
            TypeError: If arguments have incorrect types
            ValueError: If required fields are empty
        """
        # Step 1: Type checking (defensive)
        if not isinstance(turn, int):
            raise TypeError("turn must be an int")
        if not isinstance(role, str):
            raise TypeError("role must be a str")
        if not isinstance(content, str):
            raise TypeError("content must be a str")
        if not isinstance(event_type, str):
            raise TypeError("event_type must be a str")

        # Step 2: Input validation (defensive)
        if not content.strip():
            raise ValueError("content cannot be empty")
        if not event_type.strip():
            raise ValueError("event_type cannot be empty")

        # Step 3: Create event
        event = {
            "turn": turn,
            "role": role,
            "content": content,
            "event_type": event_type,
        }

        # Step 4: Identify if protected
        protection_result = identify_protected_context(event)
        event["is_protected"] = protection_result["is_protected"]

        # Step 5: Append to events log
        self.events.append(event)

        # Step 6: Check if compression needed
        if self.compressor.should_compress(self.events):
            self._compress_events()

    def get_context_window(self) -> list[dict[str, Any]]:
        """Get current context window (may be compressed).

        Returns:
            List of events currently in context window
        """
        # Return current events (already compressed if needed)
        return self.events

    def _compress_events(self) -> None:
        """Internal method to compress events log."""
        # Step 1: Compress events
        compressed_events = self.compressor.compress(self.events)

        # Step 2: Update events log
        self.events = compressed_events

        # Step 3: Track compression count
        self.compression_count += 1
