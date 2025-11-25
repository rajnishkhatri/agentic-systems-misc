# Sessions Pattern - Quick Reference

**Pattern:** Context Management
**Use Case:** Multi-turn conversations with automatic compression
**File:** `backend/sessions/gita_session.py:13-120`

---

## Core Template

```python
from backend.sessions.context_compressor import ContextCompressor
from backend.sessions.protected_context import identify_protected_context

class GitaSession:
    """Manage multi-turn conversations with automatic compression."""

    def __init__(self, max_tokens: int = 8000, compression_threshold: float = 0.95) -> None:
        self.events: list[dict[str, Any]] = []
        self.session_state: dict[str, Any] = {}
        self.compression_count = 0
        self.compressor = ContextCompressor(max_tokens, compression_threshold)

    def append_event(self, turn: int, role: str, content: str, event_type: str) -> None:
        # Type & input validation
        if not isinstance(turn, int): raise TypeError("turn must be int")
        if not content.strip(): raise ValueError("content cannot be empty")

        # Create & protect event
        event = {"turn": turn, "role": role, "content": content, "event_type": event_type}
        event["is_protected"] = identify_protected_context(event)["is_protected"]

        # Append & check compression
        self.events.append(event)
        if self.compressor.should_compress(self.events):
            self._compress_events()

    def get_context_window(self) -> list[dict[str, Any]]:
        return self.events
```

## Protected Context Function

```python
def identify_protected_context(event: dict[str, Any]) -> dict[str, Any]:
    """Identify if event contains protected context.

    Protected: Turn 0, constraints, auth checkpoints.
    """
    if not isinstance(event, dict): raise TypeError("event must be dict")

    event_type = event["event_type"]
    turn = event["turn"]

    if turn == 0: return {"is_protected": True, "reason": "initial_objective"}
    if event_type == "constraint": return {"is_protected": True, "reason": "explicit_constraint"}
    if event_type == "auth_checkpoint": return {"is_protected": True, "reason": "authentication"}

    return {"is_protected": False, "reason": "compressible"}
```

## Usage Example

```python
# Initialize
session = GitaSession(max_tokens=8000, compression_threshold=0.95)

# Add events
session.append_event(turn=0, role="user", content="Explain karma yoga", event_type="initial_objective")
session.append_event(turn=1, role="assistant", content="Karma yoga is...", event_type="casual")

# Get context (automatically compressed at 95% threshold)
context = session.get_context_window()
```

---

**See also:**
- [Tutorial](./sessions-tutorial.md) - Full explanation with examples
- [Advanced](./sessions-advanced.md) - Performance, pitfalls, production tips
- [TERMINOLOGY.md](../google-context/TERMINOLOGY.md) - Session vs. Context distinction
