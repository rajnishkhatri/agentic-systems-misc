# Implementation Plan: Context Engineering Critical Success Factors

## Overview
Systematic implementation of context engineering foundations with emphasis on terminology clarity, context protection, and provenance tracking for the Bhagavad Gita chatbot and LLM evaluation tutorial system.

---

## Phase 1: Foundation - Terminology Clarification (Days 1-2)

### Task 1.1: Create Terminology Reference Guide
**File:** `google-context/TERMINOLOGY.md`

**Content Structure:**
```markdown
# Context Engineering Terminology Reference

## Critical Distinctions

### 1. Session History vs. Context Window
- **Session History:** Complete, immutable transcript of ALL turns
- **Context Window:** Curated subset sent to LLM in ONE turn
- **Analogy:** Library (history) vs. Desk (context)

### 2. Memory vs. RAG
- **Memory:** Personal assistant (user-specific, conversation-derived)
- **RAG:** Research librarian (general knowledge, document corpus)

### 3. Proactive vs. Reactive Retrieval
- **Proactive:** Auto-load every turn (higher tokens, no misses)
- **Reactive:** Agent calls tool when needed (lower tokens, requires smart agent)
```

**Acceptance Criteria:**
- [ ] All 6 key distinctions documented with examples
- [ ] Side-by-side comparison tables included
- [ ] Gita chatbot specific examples provided
- [ ] Linked from main tutorial index

**Estimated Time:** 3 hours

---

### Task 1.2: Create Visual Terminology Diagrams
**Files:**
- `google-context/diagrams/session_vs_context.mmd`
- `google-context/diagrams/memory_vs_rag.mmd`
- `google-context/diagrams/proactive_vs_reactive.mmd`

**Diagram 1: Session History vs. Context Window**
```mermaid
flowchart TD
    Session[Session History<br/>Turn 1-50<br/>50,000 tokens]

    subgraph Context Window
        Protected[Protected Context<br/>Objectives, Constraints<br/>500 tokens]
        Recent[Recent Turns 45-50<br/>3,000 tokens]
        Memory[Retrieved Memories<br/>800 tokens]
        RAG[RAG Results<br/>1,200 tokens]
    end

    Session -->|Compression<br/>at 95% capacity| Context Window

    style Session fill:#f0f5ff
    style Protected fill:#ffe0e0
    style Recent fill:#e0f0ff
    style Memory fill:#ffeacc
    style RAG fill:#e0ffe0
```

**Acceptance Criteria:**
- [ ] 3 Mermaid diagrams created
- [ ] SVG exports generated for each
- [ ] Embedded in TERMINOLOGY.md
- [ ] Visual quiz at end: "Which is which?"

**Estimated Time:** 4 hours

---

### Task 1.3: Add Terminology to Pattern Library
**File:** `patterns/context-engineering-sessions.md`

**Template:**
```markdown
# Context Engineering: Sessions Pattern

**Complexity:** ⭐⭐⭐
**Use Case:** Managing stateful multi-turn conversations

## Terminology Foundation

Before implementing, understand these distinctions:
- [Link to TERMINOLOGY.md sections]

## Pattern Overview
[Implementation details...]

## Common Mistakes
❌ **Anti-Pattern:** Sending entire session history to LLM
✅ **Correct Pattern:** Compress history, send curated context

## Real Example
See: `src/sessions/gita_session.py:45-67` (session history management)
See: `src/sessions/gita_session.py:89-112` (context window preparation)
```

**Acceptance Criteria:**
- [ ] Sessions pattern references TERMINOLOGY.md
- [ ] Memory pattern references TERMINOLOGY.md
- [ ] Anti-patterns highlighted with ❌/✅ notation
- [ ] Code examples show correct usage

**Estimated Time:** 2 hours

---

## Phase 2: Context Protection Implementation (Days 3-5)

### Task 2.1: Define Protected Context Schema
**File:** `src/sessions/protected_context.py`

**Implementation (TDD Mode - RED Phase):**
```python
# tests/sessions/test_protected_context.py

def test_should_identify_initial_objectives_as_protected() -> None:
    """Test that initial user objectives are marked as protected."""
    event = {
        "role": "user",
        "content": "Help me understand karma yoga in Bhagavad Gita Chapter 3",
        "turn": 0
    }

    result = identify_protected_context(event)

    assert result["is_protected"] is True
    assert result["reason"] == "initial_objective"

def test_should_identify_explicit_constraints_as_protected() -> None:
    """Test that explicit constraints are marked as protected."""
    event = {
        "role": "user",
        "content": "Only use translations from Swami Sivananda",
        "turn": 2,
        "intent": "constraint"
    }

    result = identify_protected_context(event)

    assert result["is_protected"] is True
    assert result["reason"] == "explicit_constraint"

def test_should_not_protect_casual_conversation() -> None:
    """Test that casual conversation is not protected."""
    event = {
        "role": "user",
        "content": "Thanks, that's helpful",
        "turn": 15
    }

    result = identify_protected_context(event)

    assert result["is_protected"] is False
    assert result["reason"] == "casual_acknowledgment"
```

**Acceptance Criteria:**
- [ ] Tests written for all protected context types
- [ ] Tests fail (RED phase confirmed)
- [ ] Schema validates: objectives, constraints, auth checkpoints
- [ ] 100% test coverage for schema validation

**Estimated Time:** 4 hours

---

### Task 2.2: Implement Context Compression with Protection
**File:** `src/sessions/context_compressor.py`

**Implementation (TDD Mode - GREEN Phase):**
```python
from typing import Any

class ContextCompressor:
    """Compress session history while preserving protected context."""

    def __init__(self, max_tokens: int = 8000, trigger_threshold: float = 0.95):
        """Initialize compressor with token budget and trigger threshold.

        Args:
            max_tokens: Maximum tokens for context window
            trigger_threshold: Compression triggers at this % of capacity (0.95 = 95%)

        Raises:
            ValueError: If trigger_threshold not in range [0.0, 1.0]
        """
        if not 0.0 <= trigger_threshold <= 1.0:
            raise ValueError("trigger_threshold must be in range [0.0, 1.0]")

        self.max_tokens = max_tokens
        self.trigger_threshold = trigger_threshold
        self.trigger_tokens = int(max_tokens * trigger_threshold)

    def should_compress(self, events: list[dict[str, Any]]) -> bool:
        """Check if compression should be triggered.

        Args:
            events: List of conversation events

        Returns:
            True if total tokens >= 95% of max capacity
        """
        total_tokens = sum(self._count_tokens(e["content"]) for e in events)
        return total_tokens >= self.trigger_tokens

    def compress(
        self,
        events: list[dict[str, Any]],
        protected_indices: set[int]
    ) -> list[dict[str, Any]]:
        """Compress events while preserving protected context.

        Args:
            events: Full conversation history
            protected_indices: Set of event indices to preserve

        Returns:
            Compressed event list with protected events intact

        Raises:
            TypeError: If events is not a list or protected_indices is not a set
        """
        if not isinstance(events, list):
            raise TypeError("events must be a list")
        if not isinstance(protected_indices, set):
            raise TypeError("protected_indices must be a set")

        # Step 1: Separate protected and compressible events
        protected_events = [e for i, e in enumerate(events) if i in protected_indices]
        compressible_events = [e for i, e in enumerate(events) if i not in protected_indices]

        # Step 2: Compress non-protected events
        summary = self._summarize_events(compressible_events)

        # Step 3: Reconstruct with protected events + summary
        compressed = protected_events + [{
            "role": "system",
            "content": f"[CONVERSATION SUMMARY]: {summary}",
            "is_compressed": True
        }]

        return compressed

    def _count_tokens(self, text: str) -> int:
        """Estimate token count (defensive implementation)."""
        if not isinstance(text, str):
            raise TypeError("text must be a string")
        # Rough estimate: 1 token ≈ 4 characters
        return len(text) // 4

    def _summarize_events(self, events: list[dict[str, Any]]) -> str:
        """Summarize events using LLM (stub for now)."""
        # TODO: Implement LLM summarization
        return f"Summary of {len(events)} conversation turns"
```

**Acceptance Criteria:**
- [ ] All tests pass (GREEN phase confirmed)
- [ ] Compression triggers at exactly 95% capacity
- [ ] Protected events never compressed
- [ ] Defensive coding: type hints, input validation, error handling

**Estimated Time:** 6 hours

---

### Task 2.3: Multi-Turn Conversation Test Suite
**File:** `tests/sessions/test_long_conversation.py`

**Implementation:**
```python
import pytest
from src.sessions.gita_session import GitaSession
from src.sessions.context_compressor import ContextCompressor

def test_should_preserve_objectives_in_50_turn_conversation() -> None:
    """Test that initial objectives survive 50 turns of compression."""
    session = GitaSession(user_id="test_user")
    compressor = ContextCompressor(max_tokens=8000, trigger_threshold=0.95)

    # Turn 0: Initial objective (PROTECTED)
    session.append_event({
        "role": "user",
        "content": "Help me understand dharma in Bhagavad Gita",
        "turn": 0
    })

    # Turns 1-49: Normal conversation (fills to 95% capacity)
    for turn in range(1, 50):
        session.append_event({
            "role": "user",
            "content": f"Follow-up question {turn} about dharma concepts",
            "turn": turn
        })
        session.append_event({
            "role": "assistant",
            "content": f"Response {turn} explaining dharma with verse references",
            "turn": turn
        })

    # Check if compression triggered
    assert compressor.should_compress(session.events) is True

    # Compress with protection
    protected_indices = {0}  # Protect initial objective
    compressed = compressor.compress(session.events, protected_indices)

    # Verify objective preserved
    assert any("Help me understand dharma" in e["content"] for e in compressed)
    assert len(compressed) < len(session.events)  # Compression occurred

def test_should_handle_multiple_compressions() -> None:
    """Test that compression can run multiple times (turns 1-100)."""
    # Test 100-turn conversation with 2-3 compression cycles
    pass  # TODO: Implement

def test_should_reject_compression_with_all_protected() -> None:
    """Test error handling when all events are protected."""
    # Edge case: What if everything is protected?
    pass  # TODO: Implement
```

**Acceptance Criteria:**
- [ ] 50-turn conversation test passes
- [ ] 100-turn conversation with multiple compressions passes
- [ ] Edge cases tested (all protected, no protected, empty events)
- [ ] Performance: Compression completes in <2 seconds

**Estimated Time:** 5 hours

---

## Phase 3: Provenance Tracking System (Days 6-7)

### Task 3.1: Define Provenance Data Model
**File:** `src/memory/provenance.py`

**Implementation (TDD Mode - RED Phase):**
```python
# tests/memory/test_provenance.py

def test_should_create_provenance_with_required_fields() -> None:
    """Test provenance creation with all required metadata."""
    from datetime import datetime

    provenance = MemoryProvenance(
        memory_id="mem_001",
        source_session_id="session_2025_11_22_001",
        extraction_timestamp=datetime.utcnow(),
        confidence_score=0.85,
        validation_status="agent_inferred"
    )

    assert provenance.memory_id == "mem_001"
    assert provenance.confidence_score == 0.85
    assert provenance.validation_status == "agent_inferred"

def test_should_track_confidence_evolution() -> None:
    """Test confidence score evolution tracking."""
    provenance = MemoryProvenance(...)

    # Initial extraction
    provenance.add_confidence_update(0.75, reason="initial_extraction")

    # User confirms
    provenance.add_confidence_update(0.95, reason="user_confirmed")

    assert len(provenance.confidence_history) == 2
    assert provenance.current_confidence == 0.95
    assert provenance.confidence_trend == "increasing"

def test_should_enforce_user_confirmed_higher_than_inferred() -> None:
    """Test that user-confirmed memories have higher confidence floor."""
    provenance_inferred = MemoryProvenance(
        ...,
        validation_status="agent_inferred",
        confidence_score=0.95
    )

    provenance_confirmed = MemoryProvenance(
        ...,
        validation_status="user_confirmed",
        confidence_score=0.95
    )

    # When both have same raw score, user-confirmed gets boosted
    assert provenance_confirmed.effective_confidence > provenance_inferred.effective_confidence
```

**Acceptance Criteria:**
- [ ] All required fields defined: memory_id, source_session_id, confidence_score, validation_status
- [ ] Tests fail (RED phase)
- [ ] Confidence evolution tracked with timestamps
- [ ] Validation status enum: {agent_inferred, user_confirmed, disputed}

**Estimated Time:** 3 hours

---

### Task 3.2: Implement Provenance Class
**File:** `src/memory/provenance.py`

**Implementation (GREEN Phase):**
```python
from dataclasses import dataclass, field
from datetime import datetime
from typing import Literal

ValidationStatus = Literal["agent_inferred", "user_confirmed", "disputed"]

@dataclass
class MemoryProvenance:
    """Provenance tracking for memory lifecycle (audit trail)."""

    memory_id: str
    source_session_id: str
    extraction_timestamp: datetime
    confidence_score: float
    validation_status: ValidationStatus

    confidence_history: list[tuple[datetime, float, str]] = field(default_factory=list)
    consolidation_history: list[dict] = field(default_factory=list)
    pii_redacted: bool = False

    def __post_init__(self) -> None:
        """Validate fields after initialization."""
        if not 0.0 <= self.confidence_score <= 1.0:
            raise ValueError("confidence_score must be in range [0.0, 1.0]")

        if self.validation_status not in ["agent_inferred", "user_confirmed", "disputed"]:
            raise ValueError("validation_status must be agent_inferred, user_confirmed, or disputed")

        # Initialize confidence history
        if not self.confidence_history:
            self.confidence_history.append((
                self.extraction_timestamp,
                self.confidence_score,
                f"initial_{self.validation_status}"
            ))

    def add_confidence_update(self, new_score: float, reason: str) -> None:
        """Add confidence score update with reason.

        Args:
            new_score: New confidence score (0.0 to 1.0)
            reason: Reason for update (e.g., "user_confirmed", "contradicted")

        Raises:
            ValueError: If new_score not in valid range
        """
        if not 0.0 <= new_score <= 1.0:
            raise ValueError("new_score must be in range [0.0, 1.0]")

        self.confidence_history.append((
            datetime.utcnow(),
            new_score,
            reason
        ))
        self.confidence_score = new_score  # Update current score

    @property
    def current_confidence(self) -> float:
        """Get current confidence score."""
        return self.confidence_history[-1][1] if self.confidence_history else self.confidence_score

    @property
    def confidence_trend(self) -> Literal["increasing", "decreasing", "stable", "insufficient_data"]:
        """Calculate confidence trend over history."""
        if len(self.confidence_history) < 2:
            return "insufficient_data"

        recent = self.confidence_history[-3:]  # Last 3 updates
        scores = [score for _, score, _ in recent]

        if all(scores[i] <= scores[i+1] for i in range(len(scores)-1)):
            return "increasing"
        elif all(scores[i] >= scores[i+1] for i in range(len(scores)-1)):
            return "decreasing"
        else:
            return "stable"

    @property
    def effective_confidence(self) -> float:
        """Calculate effective confidence with validation status boost.

        Returns:
            Boosted confidence score:
            - user_confirmed: +0.1 boost (capped at 1.0)
            - agent_inferred: no boost
            - disputed: -0.2 penalty (floored at 0.0)
        """
        base = self.current_confidence

        if self.validation_status == "user_confirmed":
            return min(1.0, base + 0.1)
        elif self.validation_status == "disputed":
            return max(0.0, base - 0.2)
        else:
            return base

    def to_audit_log(self) -> dict:
        """Export provenance for audit logging (FR4.6 compliance)."""
        return {
            "memory_id": self.memory_id,
            "lineage": {
                "origin_session": self.source_session_id,
                "extracted_at": self.extraction_timestamp.isoformat(),
                "modifications": self.consolidation_history
            },
            "trustworthiness": {
                "current_confidence": self.current_confidence,
                "effective_confidence": self.effective_confidence,
                "confidence_trend": self.confidence_trend,
                "validation": self.validation_status
            },
            "compliance": {
                "pii_handling": "redacted" if self.pii_redacted else "none_present"
            }
        }
```

**Acceptance Criteria:**
- [ ] All tests pass (GREEN phase)
- [ ] Confidence evolution tracking works
- [ ] Effective confidence calculation correct (user_confirmed > agent_inferred)
- [ ] Audit log export includes all required fields

**Estimated Time:** 5 hours

---

### Task 3.3: Integrate PII Redaction
**File:** `src/memory/pii_redaction.py`

**Implementation:**
```python
import re
from typing import Any

class PIIRedactor:
    """Redact PII from memory content (spiritual/personal context protection)."""

    # Patterns for common PII
    PATTERNS = {
        "email": r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
        "phone": r'\b(\+\d{1,2}\s?)?\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}\b',
        "name": r'\b(my name is|I am|I\'m)\s+([A-Z][a-z]+\s+[A-Z][a-z]+)\b',
        "location": r'\b(I live in|I\'m from)\s+([A-Z][a-z]+(?:,\s+[A-Z]{2})?)\b'
    }

    REPLACEMENTS = {
        "email": "[EMAIL_REDACTED]",
        "phone": "[PHONE_REDACTED]",
        "name": r'\1 [NAME_REDACTED]',
        "location": r'\1 [LOCATION_REDACTED]'
    }

    def redact(self, text: str) -> tuple[str, bool]:
        """Redact PII from text.

        Args:
            text: Input text potentially containing PII

        Returns:
            Tuple of (redacted_text, pii_found)
        """
        if not isinstance(text, str):
            raise TypeError("text must be a string")

        redacted = text
        pii_found = False

        for pattern_name, pattern in self.PATTERNS.items():
            replacement = self.REPLACEMENTS[pattern_name]
            redacted_new = re.sub(pattern, replacement, redacted)

            if redacted_new != redacted:
                pii_found = True

            redacted = redacted_new

        return redacted, pii_found

# Integration with provenance
def extract_memory_with_pii_redaction(content: str, session_id: str) -> tuple[dict, MemoryProvenance]:
    """Extract memory with automatic PII redaction and provenance tracking."""
    redactor = PIIRedactor()
    redacted_content, pii_found = redactor.redact(content)

    memory = {
        "content": redacted_content,
        "original_content_hash": hash(content)  # For auditing
    }

    provenance = MemoryProvenance(
        memory_id=generate_uuid(),
        source_session_id=session_id,
        extraction_timestamp=datetime.utcnow(),
        confidence_score=0.75,  # Lower for redacted content
        validation_status="agent_inferred",
        pii_redacted=pii_found
    )

    return memory, provenance
```

**Acceptance Criteria:**
- [ ] Email, phone, name, location patterns detected
- [ ] Redaction preserves sentence structure
- [ ] PII flag set in provenance metadata
- [ ] Tests for false positives (e.g., "karma" not flagged as name)

**Estimated Time:** 4 hours

---

## Phase 4: Documentation & Pattern Library (Days 8-10)

### Task 4.1: Create Context Engineering Sessions Pattern
**File:** `patterns/context-engineering-sessions.md`

**Content Structure:**
```markdown
# Context Engineering: Sessions Pattern

**Complexity:** ⭐⭐⭐
**Use Case:** Managing stateful multi-turn conversations with working memory

## Pattern Overview

Sessions are the short-term workspace for conversations, containing:
1. **Events Log:** Immutable, append-only record of all turns
2. **Session State:** Mutable scratchpad for structured data

## Terminology Foundation

**CRITICAL:** Session History ≠ Context Window
- **Session History:** Complete transcript (all 50 turns, 50K tokens)
- **Context Window:** Curated payload (protected context + recent turns + memories, 8K tokens)

See: [TERMINOLOGY.md](../google-context/TERMINOLOGY.md#session-vs-context)

## Code Template

```python
class GitaSession:
    """Session management for Bhagavad Gita conversations."""

    def __init__(self, user_id: str, max_context_tokens: int = 8000):
        self.user_id = user_id
        self.events: list[dict] = []  # Immutable log
        self.state: dict = {  # Mutable scratchpad
            "current_chapter": None,
            "verses_explored": set(),
            "preferred_commentators": []
        }
        self.max_context_tokens = max_context_tokens

    def append_event(self, event: dict) -> None:
        """Append to immutable event log."""
        self.events.append(event)

    def get_context_window(self) -> list[dict]:
        """Get curated context (NOT full history)."""
        compressor = ContextCompressor(self.max_context_tokens)

        if compressor.should_compress(self.events):
            protected_indices = self._identify_protected_events()
            return compressor.compress(self.events, protected_indices)

        return self.events  # No compression needed yet
```

## Real Example from Codebase

- Session management: `src/sessions/gita_session.py:12-89`
- Context compression: `src/sessions/context_compressor.py:45-112`
- Protected context identification: `src/sessions/protected_context.py:23-67`

## Common Pitfalls

❌ **Anti-Pattern: Sending entire session history to LLM**
```python
# WRONG: Will exceed context window after 20-30 turns
prompt = {
    "messages": session.events  # All 50 turns!
}
```

✅ **Correct Pattern: Compress and curate context**
```python
# RIGHT: Compress to fit context window, preserve protected context
context_window = session.get_context_window()
prompt = {
    "messages": context_window  # Only relevant turns
}
```

## Integration with Defensive Coding

- **Type hints:** All methods have parameter and return type annotations
- **Input validation:** Check events are dicts with required keys
- **Error handling:** Raise descriptive errors for invalid state transitions

## Testing Strategy

```python
def test_should_preserve_objectives_after_compression() -> None:
    """Test protected context survives compression."""
    session = GitaSession("user_123")
    session.append_event({"role": "user", "content": "Help me with dharma", "turn": 0})

    # Add 49 more turns to trigger compression
    for i in range(1, 50):
        session.append_event({"role": "user", "content": f"Turn {i}", "turn": i})

    context = session.get_context_window()

    assert any("Help me with dharma" in e["content"] for e in context)
```

## When to Use This Pattern

✅ **Use when:**
- Building chatbots with multi-turn conversations (>10 turns)
- Need to track conversation state across turns
- Context window management required

❌ **Don't use when:**
- Single-turn Q&A (no state needed)
- Stateless API endpoints
```

**Acceptance Criteria:**
- [ ] Pattern follows standard template (Complexity, Use Case, Overview, Template, Example, Pitfalls)
- [ ] Links to TERMINOLOGY.md for key concepts
- [ ] Real codebase examples with file:line references
- [ ] TDD test examples included

**Estimated Time:** 6 hours

---

### Task 4.2: Create Context Engineering Memory Pattern
**File:** `patterns/context-engineering-memory.md`

**Content Structure:**
```markdown
# Context Engineering: Memory Pattern

**Complexity:** ⭐⭐⭐⭐
**Use Case:** Long-term persistence of user preferences, facts, and learning patterns

## Pattern Overview

Memory is the long-term storage system for consolidated knowledge that survives across sessions.

## Terminology Foundation

**CRITICAL:** Memory ≠ RAG
- **Memory:** Personal assistant (user-specific, conversation-derived, "User prefers Sanskrit")
- **RAG:** Research librarian (general knowledge, document corpus, "Chapter 3 discusses karma")

See: [TERMINOLOGY.md](../google-context/TERMINOLOGY.md#memory-vs-rag)

## Code Template

[Full implementation with extraction, consolidation, retrieval]

## Provenance Tracking (Critical Success Factor #3)

Every memory MUST have:
1. **source_session_id:** Which conversation generated it
2. **confidence_score:** How reliable (0.0-1.0)
3. **validation_status:** {agent_inferred, user_confirmed, disputed}

```python
memory = {
    "content": "User prefers Swami Sivananda translations",
    "metadata": {
        "source_session_id": "session_2025_11_22_001",
        "confidence_score": 0.85,
        "validation_status": "agent_inferred",
        "created_at": "2025-11-22T10:30:00Z"
    }
}
```

**Confidence Evolution:**
- **Initial extraction:** 0.75 (agent_inferred)
- **User confirms:** 0.95 (user_confirmed) ← BOOST
- **Contradicted:** 0.30 (disputed) ← PENALTY

## PII Redaction (Mandatory for Spiritual/Personal Context)

```python
from src.memory.pii_redaction import PIIRedactor

redactor = PIIRedactor()
content = "My name is John and I'm struggling with anger"
redacted, pii_found = redactor.redact(content)

# Result: "[NAME_REDACTED] and I'm struggling with anger"
# pii_found = True → Set provenance.pii_redacted = True
```

## Common Pitfalls

❌ **Anti-Pattern: Treating memory as saved chat history**
```python
# WRONG: Just saving conversation verbatim
memory = {"content": session.events}
```

✅ **Correct Pattern: Extract signal from noise**
```python
# RIGHT: LLM extracts meaningful insights
memory = llm.extract(
    session.events,
    prompt="Extract user preferences, not casual chat"
)
```
```

**Acceptance Criteria:**
- [ ] Memory vs. RAG distinction clear
- [ ] Provenance tracking emphasized as mandatory
- [ ] PII redaction examples included
- [ ] Confidence evolution explained

**Estimated Time:** 6 hours

---

### Task 4.3: Create google-context/TUTORIAL_INDEX.md
**File:** `google-context/TUTORIAL_INDEX.md`

**Content Structure:**
```markdown
# Context Engineering Tutorial Index

## Overview
Google's November 2025 framework for building stateful AI agents through Sessions, Memory, and RAG orchestration.

**Core Thesis:** "Bigger models aren't enough. Intelligence emerges from orchestration."

## Prerequisites
- ✅ Understanding of LLM context windows
- ✅ Familiarity with RAG (Retrieval-Augmented Generation)
- ✅ Basic knowledge of vector databases
- ⚠️ **CRITICAL:** Read [TERMINOLOGY.md](TERMINOLOGY.md) FIRST to avoid confusion

## Learning Paths

### Path 1: Quick Start (30 minutes)
**Goal:** Understand core concepts without implementation

1. Read [TERMINOLOGY.md](TERMINOLOGY.md) (10 min)
   - Session History vs. Context Window
   - Memory vs. RAG
   - Proactive vs. Reactive Retrieval

2. Study diagrams (10 min)
   - [context_engineering_flow.svg](context_engineering_flow.svg)
   - [session_vs_context diagram](diagrams/session_vs_context.mmd)

3. Skim case study (10 min)
   - [dispute_transaction_sequence.md](dispute_transaction_sequence.md)

**Checkpoint:** Can you explain the difference between session history and context window?

### Path 2: Implementation-Focused (2-3 hours)
**Goal:** Build a session management system

1. Complete Path 1 ✓

2. Read pattern guides (45 min)
   - [Context Engineering: Sessions Pattern](../patterns/context-engineering-sessions.md)
   - [Context Engineering: Memory Pattern](../patterns/context-engineering-memory.md)

3. Study code templates (30 min)
   - Session management: `src/sessions/gita_session.py`
   - Context compression: `src/sessions/context_compressor.py`

4. Implement for your project (60 min)
   - Follow TDD: Write tests first
   - Use defensive coding: Type hints, validation, error handling

**Checkpoint:** Can you implement a session that compresses at 95% capacity?

### Path 3: Full Mastery (4-6 hours)
**Goal:** Production-ready context engineering system

1. Complete Path 2 ✓

2. Deep-dive tutorials (90 min)
   - [context_engineering_tutorial.md](context_engineering_tutorial.md) sections 1-7

3. Advanced topics (90 min)
   - Provenance tracking: `src/memory/provenance.py`
   - PII redaction: `src/memory/pii_redaction.py`
   - Multi-agent session architectures

4. Case study analysis (60 min)
   - Map banking fraud workflow to your domain
   - Identify compliance/sensitivity requirements

**Checkpoint:** Can you implement memory extraction with provenance tracking and PII redaction?

## Files

| File | Type | Lines | Purpose | Estimated Reading Time |
|------|------|-------|---------|----------------------|
| [TERMINOLOGY.md](TERMINOLOGY.md) | Reference | ~150 | **START HERE** - Critical distinctions | 10 min |
| [context_engineering_tutorial.md](context_engineering_tutorial.md) | Tutorial | 186 | Main pedagogical content (7 sections) | 25 min |
| [dispute_transaction_sequence.md](dispute_transaction_sequence.md) | Case Study | 27 | 19-step fraud dispute workflow | 10 min |
| [context_engineering_flow.mmd](context_engineering_flow.mmd) | Diagram | 65 | 3-part system architecture (Mermaid) | 5 min |
| [context_engineering_sequence.mmd](context_engineering_sequence.mmd) | Diagram | 43 | Service choreography (Mermaid) | 5 min |

## Critical Success Factors

Before implementing, internalize these:

### 1. Don't Confuse Terminology ⚠️
- Session History ≠ Context Window ([see TERMINOLOGY.md](TERMINOLOGY.md#session-vs-context))
- Memory ≠ RAG ([see TERMINOLOGY.md](TERMINOLOGY.md#memory-vs-rag))
- Proactive ≠ Reactive Retrieval ([see TERMINOLOGY.md](TERMINOLOGY.md#proactive-vs-reactive))

### 2. Protect Context During Compression
- **Always preserve:** Initial objectives, explicit constraints
- **Compression trigger:** 95% token capacity
- **Test:** 50+ turn conversations

See: [Protected Context Pattern](../patterns/context-engineering-sessions.md#protect-context)

### 3. Track Provenance for Trust
- **Every memory needs:** source_session_id, confidence_score, validation_status
- **Confidence evolution:** user_confirmed > agent_inferred
- **PII redaction:** Mandatory for spiritual/personal context

See: [Provenance Pattern](../patterns/context-engineering-memory.md#provenance-tracking)

## Integration with Course

| Lesson | Integration Point | Status |
|--------|------------------|--------|
| Lessons 9-11 | Add context coherence metrics to evaluation dashboard | 🔄 Planned |
| Lesson 12 (NEW) | Full tutorial on context engineering evaluation | 📝 To Create |
| Lesson 16 | Extend with memory provenance for audit logging (FR4.6) | 🔄 Planned |

## Common Pitfalls

### Pitfall #1: Sending entire session history to LLM
❌ **Wrong:**
```python
messages = session.events  # All 50 turns, exceeds context window
```

✅ **Right:**
```python
messages = session.get_context_window()  # Compressed, curated
```

### Pitfall #2: Treating memory as saved chat
❌ **Wrong:**
```python
memory = {"content": json.dumps(session.events)}
```

✅ **Right:**
```python
memory = memory_manager.extract_insights(session.events)
```

### Pitfall #3: Ignoring provenance
❌ **Wrong:**
```python
memory = {"content": "User prefers Python"}
```

✅ **Right:**
```python
memory = {
    "content": "User prefers Python",
    "metadata": {
        "source_session_id": "session_001",
        "confidence_score": 0.85,
        "validation_status": "agent_inferred"
    }
}
```

## Real-World Applications

1. **Bhagavad Gita Chatbot** ([see mapping](../analysis/context-engineering-gita-mapping.md))
   - Track spiritual learning journey across sessions
   - Personalize verse recommendations based on past resonance
   - Protect sensitive personal struggles with PII redaction

2. **Banking Fraud Dispute** ([case study](dispute_transaction_sequence.md))
   - Maintain compliance audit trails
   - Preserve user context across multi-day investigations
   - Provenance tracking for regulatory requirements

3. **Healthcare Triage**
   - Session state tracks symptoms across conversation
   - Memory stores patient preferences, allergies
   - HIPAA compliance through PII redaction

## FAQs

**Q: When should I use sessions vs. memory?**
A: Sessions = current conversation workspace. Memory = persistent facts across conversations.

**Q: How do I know when to compress?**
A: Trigger at 95% of max context tokens (e.g., 7600 tokens for 8K window).

**Q: What if I compress protected context by accident?**
A: Use `identify_protected_context()` to mark objectives/constraints before compression.

**Q: How do I test if my implementation is correct?**
A: Run 50-turn conversation test. Verify: (1) objectives preserved, (2) compression triggered, (3) token budget not exceeded.

## Next Steps

After completing this tutorial:
- [ ] Implement session management for your chatbot
- [ ] Add context compression with protection
- [ ] Build memory extraction pipeline
- [ ] Integrate provenance tracking
- [ ] Create evaluation metrics for context coherence

**Need help?** See [patterns/](../patterns/) for copy-paste templates with defensive coding.
```

**Acceptance Criteria:**
- [ ] 3 learning paths clearly defined (Quick Start, Implementation, Mastery)
- [ ] Critical Success Factors highlighted at top
- [ ] Common Pitfalls with ❌/✅ examples
- [ ] Files table with estimated reading times
- [ ] Integration roadmap with lessons

**Estimated Time:** 8 hours

---

### Task 4.4: Update CLAUDE.md with Context Engineering Principles
**File:** `CLAUDE.md`

**Addition (insert after "Quality Standards" section):**
```markdown
## Context Engineering Principles

Based on Google's November 2025 whitepaper (see `google-context/`):

### Core Concepts

**"Bigger models aren't enough. Intelligence emerges from orchestration."**

Context engineering is the process of dynamically managing information within an LLM's context window to enable stateful, intelligent agents. Unlike prompt engineering (what to do), context engineering provides everything needed to do it intelligently.

### Critical Distinctions

⚠️ **Avoid Common Confusion:**

1. **Session History ≠ Context Window**
   - **Session History:** Complete, immutable transcript of ALL turns (50 turns, 50K tokens)
   - **Context Window:** Curated subset sent to LLM in ONE turn (protected + recent + memories, 8K tokens)
   - **When to compress:** Trigger at 95% of max token capacity

2. **Memory ≠ RAG**
   - **Memory:** Personal assistant (user-specific, conversation-derived, "User prefers Sanskrit")
   - **RAG:** Research librarian (general knowledge, document corpus, "Chapter 3 explains karma")
   - **Use both:** RAG for facts, Memory for personalization

3. **Proactive ≠ Reactive Retrieval**
   - **Proactive:** Auto-load memories every turn (higher tokens, no missed context)
   - **Reactive (Memory-as-Tool):** Agent calls `search_memories()` when needed (lower tokens, requires smart agent)

See: [google-context/TERMINOLOGY.md](google-context/TERMINOLOGY.md) for detailed explanations.

### Protected Context Pattern

When compressing long conversations, **ALWAYS preserve:**
- ✅ Initial user objectives ("Help me understand dharma")
- ✅ Explicit constraints ("Only use Swami Sivananda translations")
- ✅ Authentication/authorization checkpoints
- ✅ Compliance notices (GDPR, healthcare, spiritual sensitivity)

**Compressible content:**
- Casual acknowledgments ("Thanks", "OK")
- Intermediate reasoning steps (unless part of final answer)
- Exploratory queries that didn't lead anywhere

```python
# Example: Protected context identification
def identify_protected_context(event: dict) -> dict:
    """Mark events that must survive compression."""
    if event["turn"] == 0:
        return {"is_protected": True, "reason": "initial_objective"}

    if "constraint" in event.get("intent", ""):
        return {"is_protected": True, "reason": "explicit_constraint"}

    return {"is_protected": False, "reason": "compressible"}
```

### Memory Provenance (Mandatory)

Every memory MUST include provenance metadata for trustworthiness:

```python
memory = {
    "content": "User prefers Swami Sivananda commentaries",
    "metadata": {
        "source_session_id": "session_2025_11_22_001",  # Which conversation?
        "confidence_score": 0.85,                        # How reliable? (0.0-1.0)
        "validation_status": "agent_inferred",           # vs. "user_confirmed"
        "created_at": "2025-11-22T10:30:00Z",
        "pii_redacted": False                            # Spiritual context safety
    }
}
```

**Confidence Evolution Rules:**
- **Initial extraction:** 0.75 (agent_inferred baseline)
- **User confirms:** Boost to 0.95 (user_confirmed)
- **Contradicted:** Penalize to 0.30 (disputed)

**Why this matters:**
- Retrieval can weight by confidence (trust user-confirmed > inferred)
- Audit trails for debugging ("Which session created this memory?")
- Compliance (GDPR right-to-explanation, healthcare provenance)

### PII Redaction for Spiritual Context

Users sharing personal struggles in Bhagavad Gita conversations may reveal PII. **Redaction is mandatory:**

```python
from src.memory.pii_redaction import PIIRedactor

content = "My name is John and I'm struggling with anger at work"
redacted, pii_found = PIIRedactor().redact(content)

# Result: "[NAME_REDACTED] and I'm struggling with anger at work"
# Set: provenance.pii_redacted = True
```

**Redacted patterns:** Email, phone, full name, specific location
**Preserved context:** Emotional state, spiritual questions, domain (work/family)

### Implementation Checklist

When building context-aware agents:
- [ ] Session management with events log + mutable state
- [ ] Context compression triggers at 95% token capacity
- [ ] Protected context preserved (objectives, constraints)
- [ ] Memory extraction with provenance tracking
- [ ] Confidence scores evolve (user_confirmed > agent_inferred)
- [ ] PII redaction for sensitive personal content
- [ ] Separate Memory (user-specific) from RAG (general knowledge)

### Learning Resources

- **Quick Start:** [google-context/TUTORIAL_INDEX.md](google-context/TUTORIAL_INDEX.md) Path 1 (30 min)
- **Patterns:** [patterns/context-engineering-sessions.md](patterns/context-engineering-sessions.md)
- **Case Study:** [google-context/dispute_transaction_sequence.md](google-context/dispute_transaction_sequence.md)
- **Diagrams:** [google-context/context_engineering_flow.svg](google-context/context_engineering_flow.svg)

**For Bhagavad Gita Chatbot specific guidance:** See [analysis/context-engineering-gita-mapping.md](analysis/context-engineering-gita-mapping.md)
```

**Acceptance Criteria:**
- [ ] Inserted after "Quality Standards" section in CLAUDE.md
- [ ] All 3 critical distinctions explained
- [ ] Protected context pattern with code example
- [ ] Provenance requirements documented
- [ ] PII redaction example for spiritual context
- [ ] Links to learning resources

**Estimated Time:** 3 hours

---

## Success Metrics

### Phase 1: Terminology Clarity
- [ ] TERMINOLOGY.md created with 6 key distinctions
- [ ] 3 Mermaid diagrams exported to SVG
- [ ] Terminology referenced in both pattern files

### Phase 2: Context Protection
- [ ] ContextCompressor class passes all tests (100% coverage)
- [ ] 50-turn conversation test passes
- [ ] Compression triggers at exactly 95% capacity
- [ ] Protected events never compressed

### Phase 3: Provenance Tracking
- [ ] MemoryProvenance class implemented with all required fields
- [ ] Confidence evolution tracking works
- [ ] PII redaction integrated
- [ ] Audit log export includes provenance

### Phase 4: Documentation
- [ ] 2 pattern files created (sessions, memory)
- [ ] google-context/TUTORIAL_INDEX.md created
- [ ] CLAUDE.md updated with context engineering section
- [ ] All files cross-linked

## Timeline Summary

| Phase | Days | Tasks | Deliverables |
|-------|------|-------|--------------|
| **Phase 1: Terminology** | 1-2 | 3 tasks | TERMINOLOGY.md, 3 diagrams, pattern updates |
| **Phase 2: Protection** | 3-5 | 3 tasks | ContextCompressor, protected_context.py, test suite |
| **Phase 3: Provenance** | 6-7 | 3 tasks | MemoryProvenance, PIIRedactor, audit integration |
| **Phase 4: Documentation** | 8-10 | 4 tasks | 2 patterns, TUTORIAL_INDEX.md, CLAUDE.md update |

**Total Duration:** 10 days (2 weeks calendar time with buffer)

## Risk Mitigation

### Risk #1: Terminology confusion persists
**Mitigation:**
- Visual diagrams for all concepts
- "Before/After" examples showing wrong vs. right usage
- Quiz at end of TERMINOLOGY.md

### Risk #2: Protected context accidentally compressed
**Mitigation:**
- Explicit test: "should_never_compress_initial_objectives"
- Defensive coding: Raise error if compression would drop protected events
- Audit log tracks what was compressed

### Risk #3: PII redaction false positives/negatives
**Mitigation:**
- Gold-standard test dataset of spiritual conversations
- Manual review of first 100 redactions
- User override: "Don't redact 'Arjuna'" (character name, not PII)

---

## Appendix: TDD Workflow Reminder

For all implementation tasks (Phases 2-3), follow TDD:

```
RED: Write failing test
  ↓
GREEN: Write minimal code to pass
  ↓
REFACTOR: Improve code quality, keep tests green
  ↓
Repeat
```

**Test naming:** `test_should_[result]_when_[condition]()`

**Defensive coding checklist:**
- [ ] Type hints on all functions
- [ ] Input validation (type checks, range checks)
- [ ] Raise descriptive exceptions
- [ ] Docstrings with Args/Returns/Raises
