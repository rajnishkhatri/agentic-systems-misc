# Sessions Pattern - Tutorial

**Pattern:** Context Management
**Complexity:** ⭐⭐⭐ (Advanced)
**Reading Time:** 12-15 minutes
**Created:** 2025-11-23

---

## Overview

**Sessions** are short-term workspaces for managing multi-turn conversations in AI systems. Unlike sending the entire chat history to an LLM (which wastes tokens and context), a Session intelligently curates what gets included in the **Context Window**.

**Value Proposition:**
- **Token efficiency**: Compress verbose conversation history into compact, curated context
- **Intelligence preservation**: Automatically identify and protect critical information
- **Scalability**: Support 50-100+ turn conversations without hitting context limits
- **Cost reduction**: 84% API cost savings (50K → 8K tokens)

**Core Thesis:**
> "Bigger models aren't enough. Intelligence emerges from orchestration."

---

## Terminology Foundation

Before using this pattern, **understand these critical distinctions:**

1. **Session History vs. Context Window**
   - **Session History** = Full conversation log (50 turns, 50K tokens) stored in backend
   - **Context Window** = Curated subset (8K tokens) sent to LLM after compression
   - See [TERMINOLOGY.md](../google-context/TERMINOLOGY.md#session-vs-context)

2. **Protected vs. Compressible Context**
   - **Protected Context** = Must survive compression (objectives, constraints, auth)
   - **Compressible Context** = Can be summarized or removed (casual conversation)

3. **Events Log vs. Session State**
   - **Events Log** = Immutable conversation history (append-only)
   - **Session State** = Mutable scratchpad for temporary data

**⚠️ CRITICAL:** Read [TERMINOLOGY.md](../google-context/TERMINOLOGY.md) first or you will conflate Session History with Context Window.

---

## When to Use This Pattern

✅ **Use Sessions pattern when:**
- Building multi-turn conversational AI (chatbots, assistants, tutoring systems)
- Working with LLMs that have limited context windows (e.g., 8K tokens)
- Managing conversations that span 20+ turns where history would exceed context limits
- Needing to preserve critical information (user objectives, constraints) across long sessions
- Wanting to reduce API costs by sending only essential context

❌ **DON'T use Sessions pattern when:**
- Building single-turn Q&A systems (no conversation state to manage)
- Working with models that have massive context windows (200K+ tokens) AND conversation stays under limit
- Prototyping where you want to iterate quickly without production-grade context management
- All information must be retained verbatim (audit logs, legal compliance) - use Memory with provenance instead

**Sessions vs. Memory:**
- **Sessions** = Short-term workspace for active conversation (this pattern)
- **Memory** = Long-term persistence across sessions (see [memory-tutorial.md](./memory-tutorial.md))

---

## Code Template

```python
"""Session management with context compression.

Key Components:
1. GitaSession - Main session manager
2. ContextCompressor - Handles compression at 95% threshold
3. identify_protected_context() - Marks protected events
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
        """Initialize session.

        Args:
            max_tokens: Maximum token capacity for context window
            compression_threshold: Fraction of capacity to trigger compression (0.0-1.0)

        Raises:
            ValueError: If compression_threshold not between 0.0 and 1.0
        """
        self.events: list[dict[str, Any]] = []
        self.session_state: dict[str, Any] = {}
        self.compression_count = 0
        self.compressor = ContextCompressor(max_tokens, compression_threshold)

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
        if not isinstance(turn, int): raise TypeError("turn must be an int")
        if not isinstance(role, str): raise TypeError("role must be a str")
        if not isinstance(content, str): raise TypeError("content must be a str")
        if not isinstance(event_type, str): raise TypeError("event_type must be a str")

        # Step 2: Input validation (defensive)
        if not content.strip(): raise ValueError("content cannot be empty")
        if not event_type.strip(): raise ValueError("event_type cannot be empty")

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
        return self.events

    def _compress_events(self) -> None:
        """Internal method to compress events log."""
        compressed_events = self.compressor.compress(self.events)
        self.events = compressed_events
        self.compression_count += 1
```

---

## Real Example: Protected Context Identification

**Source:** `backend/sessions/protected_context.py:12-54`

```python
def identify_protected_context(event: dict[str, Any]) -> dict[str, Any]:
    """Identify if an event contains protected context.

    Protected context includes:
    - Initial objectives (turn 0)
    - Explicit constraints
    - Authentication checkpoints
    - Goal statements

    Args:
        event: Conversation event with turn, role, content, event_type

    Returns:
        Dict with is_protected flag and reason

    Raises:
        TypeError: If event is not a dict
        ValueError: If required fields missing
    """
    # Step 1: Type checking (defensive)
    if not isinstance(event, dict):
        raise TypeError("event must be a dict")

    # Step 2: Input validation (defensive)
    required_fields = ["turn", "role", "content", "event_type"]
    for field in required_fields:
        if field not in event:
            raise ValueError(f"event missing required field: {field}")

    # Step 3: Check protection criteria
    event_type = event["event_type"]
    turn = event["turn"]

    # Initial objectives (turn 0)
    if turn == 0:
        return {"is_protected": True, "reason": "initial_objective"}

    # Explicit constraints
    if event_type == "constraint":
        return {"is_protected": True, "reason": "explicit_constraint"}

    # Authentication checkpoints
    if event_type == "auth_checkpoint":
        return {"is_protected": True, "reason": "authentication"}

    # Step 4: Default to not protected
    return {"is_protected": False, "reason": "compressible"}
```

---

## Real Example: 50-Turn Conversation

**Source:** `tests/sessions/test_long_conversation.py:15-60`

```python
def test_should_preserve_objectives_in_50_turn_conversation() -> None:
    """Test that initial objective survives 50 turns."""
    # Arrange
    session = GitaSession(max_tokens=8000, compression_threshold=0.95)

    # Act: Add initial objective
    session.append_event(
        turn=0,
        role="user",
        content="I want to understand karma yoga from Chapter 3",
        event_type="initial_objective"
    )

    # Add 49 more casual conversation turns
    for turn in range(1, 50):
        session.append_event(
            turn=turn,
            role="user" if turn % 2 == 1 else "assistant",
            content=f"Turn {turn} casual conversation about dharma...",
            event_type="casual"
        )

    # Assert: Initial objective still in context window
    context = session.get_context_window()
    initial_objective = next((e for e in context if e["turn"] == 0), None)

    assert initial_objective is not None
    assert initial_objective["is_protected"] is True
    assert "karma yoga" in initial_objective["content"]
    assert session.compression_count >= 1  # Compression triggered
```

---

## Integration with Defensive Coding

Sessions pattern follows the **5-Step Defensive Function Template**:

1. **Type checking** - Validate argument types
2. **Input validation** - Check for empty/invalid values
3. **Edge case handling** - Handle special scenarios
4. **Main logic** - Core functionality
5. **Return** - Return result or void

Example:

```python
def append_event(self, turn: int, role: str, content: str, event_type: str) -> None:
    # Step 1: Type checking
    if not isinstance(turn, int): raise TypeError("turn must be an int")

    # Step 2: Input validation
    if not content.strip(): raise ValueError("content cannot be empty")

    # Step 3: Edge case handling (create event)
    event = {"turn": turn, "role": role, "content": content, "event_type": event_type}

    # Step 4: Main logic
    protection_result = identify_protected_context(event)
    event["is_protected"] = protection_result["is_protected"]
    self.events.append(event)

    if self.compressor.should_compress(self.events):
        self._compress_events()

    # Step 5: Return (void)
```

---

## Testing Strategy

Sessions pattern requires TDD testing following **RED → GREEN → REFACTOR**:

### Test 1: Protected Context Preservation

```python
def test_should_preserve_objectives_in_50_turn_conversation() -> None:
    """Test that initial objective survives 50 turns."""
    session = GitaSession(max_tokens=8000, compression_threshold=0.95)

    # Add initial objective (turn 0)
    session.append_event(turn=0, role="user", content="I want karma yoga", event_type="initial_objective")

    # Add 49 casual turns
    for turn in range(1, 50):
        session.append_event(turn=turn, role="user", content=f"Turn {turn}", event_type="casual")

    # Assert: Initial objective survives
    context = session.get_context_window()
    initial = next((e for e in context if e["turn"] == 0), None)
    assert initial is not None
    assert initial["is_protected"] is True
```

### Test 2: Compression Trigger

```python
def test_should_trigger_compression_at_95_percent_capacity() -> None:
    """Test that compression triggers at 7600/8000 tokens."""
    compressor = ContextCompressor(max_tokens=8000, trigger_threshold=0.95)

    # Create events totaling 7600 tokens
    events = [{"turn": i, "role": "user", "content": "x" * 100} for i in range(76)]

    # Assert: Compression triggers
    assert compressor.should_compress(events) is True
```

**Test Coverage Requirements:**
- ✅ Protected context preserved across 50+ turns
- ✅ Compression triggers at 95% threshold
- ✅ Type errors raise TypeError
- ✅ Invalid thresholds raise ValueError
- ✅ Performance: <2 seconds for 100 turns

---

## Summary Checklist

**Implementation:**
- [ ] Create `GitaSession` class with events log and session state
- [ ] Implement `identify_protected_context()` function
- [ ] Create `ContextCompressor` with 95% threshold trigger
- [ ] Add defensive coding (type hints, validation, error handling)

**Testing:**
- [ ] Write TDD tests for protected context identification
- [ ] Test compression trigger at 95% threshold
- [ ] Test multi-turn conversations (50-100 turns)
- [ ] Verify protected events survive compression

**Integration:**
- [ ] Read [TERMINOLOGY.md](../google-context/TERMINOLOGY.md)
- [ ] Follow [TDD Workflow](./tdd-workflow.md)
- [ ] Link with [Memory pattern](./memory-tutorial.md) for long-term persistence

---

**See also:**
- [Quick Reference](./sessions-quickref.md) - Code templates only
- [Advanced Guide](./sessions-advanced.md) - Pitfalls, performance, production
- [Pattern Library](./README.md) - All patterns
