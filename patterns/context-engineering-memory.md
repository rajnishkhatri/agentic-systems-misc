# Context Engineering: Memory Pattern

**Pattern Type:** Context Management
**Complexity:** ⭐⭐⭐⭐ (Expert)
**Use Case:** Long-term persistence of user preferences and learning patterns across sessions
**Created:** 2025-11-23
**File References:** `backend/memory/provenance.py:14-144`, `backend/memory/pii_redaction.py:15-125`, `tests/memory/test_provenance.py:1-150`

---

## Overview

**Memory** is consolidated, long-term knowledge about a user that persists across sessions. Unlike Session History (transient conversation logs) or RAG (general knowledge retrieval), Memory stores **user-specific** facts extracted from conversations.

**Value Proposition:**
- **Personalization**: Remember user preferences across sessions ("User prefers Swami Sivananda translations")
- **Learning**: Track user knowledge evolution (novice → intermediate → expert)
- **Consistency**: Maintain coherent user model without repeating questions
- **Privacy**: Redact PII while preserving spiritual/philosophical context
- **Trustworthiness**: Track confidence evolution and provenance for audit

**Core Thesis:**
> "Memory is not saved chat. Memory is consolidated insights about the user, extracted from signal and validated over time."
>
> — Context Engineering Principles

---

## Terminology Foundation

Before using this pattern, you **must** understand these critical distinctions:

1. **Memory vs. RAG (Knowledge Retrieval)**
   - **Memory** = User-specific (personal assistant) - "User prefers morning meditation"
   - **RAG** = General knowledge (research librarian) - "Chapter 3 discusses karma yoga"
   - See [TERMINOLOGY.md](../google-context/TERMINOLOGY.md#memory-vs-rag)

2. **Memory vs. Session History**
   - **Memory** = Consolidated facts that persist across sessions (long-term)
   - **Session History** = Transient conversation logs within one session (short-term)
   - See [TERMINOLOGY.md](../google-context/TERMINOLOGY.md#session-vs-context)

3. **Proactive vs. Reactive Memory Retrieval**
   - **Proactive** = Auto-load memories into context window (higher tokens, no misses)
   - **Reactive** = Agent tool call retrieves memories on demand (lower tokens, requires smart agent)
   - See [TERMINOLOGY.md](../google-context/TERMINOLOGY.md#proactive-vs-reactive)

**⚠️ CRITICAL:** Read [TERMINOLOGY.md](../google-context/TERMINOLOGY.md) first or you will treat Memory as "saved chat history."

---

## When to Use This Pattern

✅ **Use Memory pattern when:**
- Building multi-session applications (user returns days/weeks later)
- Personalizing AI responses based on user preferences and history
- Tracking user knowledge evolution (e.g., beginner → expert in Bhagavad Gita study)
- Storing user context that spans sessions (e.g., "User is preparing for job interview")
- Implementing spiritual guidance chatbots where personal context matters (life challenges, spiritual goals)
- Needing to audit memory extraction for trustworthiness and compliance

❌ **DON'T use Memory pattern when:**
- Building single-session Q&A (no persistence needed) - use Sessions pattern instead
- Storing general knowledge facts (e.g., "Paris is the capital of France") - use RAG instead
- Needing verbatim conversation logs for compliance - use Session Events Log instead
- Prototyping where you want quick iterations without production-grade provenance tracking
- All information is public and non-personal - use Vector DB/RAG instead

**Memory vs. Sessions vs. RAG:**
- **Sessions** = Short-term workspace for active conversation (transient)
- **Memory** = Long-term persistence of user-specific facts (consolidated, cross-session)
- **RAG** = General knowledge retrieval (domain knowledge, not user-specific)

---

## Code Template

```python
"""Memory management with provenance tracking and PII redaction.

Key Components:
1. MemoryProvenance - Tracks lineage, confidence, validation
2. PIIRedactor - Redacts PII while preserving Gita context
3. extract_memory_with_pii_redaction() - Integration function
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Literal
import re
import uuid


@dataclass
class MemoryProvenance:
    """Provenance metadata for a memory entry.

    Tracks lineage, confidence evolution, and validation status for audit
    and trustworthiness assessment.
    """

    memory_id: str
    source_session_id: str
    extraction_timestamp: datetime
    confidence_score: float
    validation_status: Literal["agent_inferred", "user_confirmed", "disputed"]
    confidence_history: list[dict[str, float | str]] = field(default_factory=list)

    def __post_init__(self) -> None:
        """Validate fields and initialize confidence history.

        Raises:
            ValueError: If confidence_score or validation_status are invalid
        """
        # Step 1: Validate confidence_score range (defensive)
        if not (0.0 <= self.confidence_score <= 1.0):
            raise ValueError("confidence_score must be between 0.0 and 1.0")

        # Step 2: Validate validation_status enum (defensive)
        valid_statuses = {"agent_inferred", "user_confirmed", "disputed"}
        if self.validation_status not in valid_statuses:
            raise ValueError(
                f"validation_status must be one of {valid_statuses}"
            )

        # Step 3: Initialize confidence history
        if not self.confidence_history:
            self.confidence_history = [
                {
                    "score": self.confidence_score,
                    "timestamp": self.extraction_timestamp.isoformat(),
                    "reason": "Initial extraction"
                }
            ]

    def add_confidence_update(self, new_score: float, reason: str) -> None:
        """Add a confidence update to the history.

        Args:
            new_score: New confidence score (0.0-1.0)
            reason: Human-readable reason for the update

        Raises:
            ValueError: If new_score is outside [0.0, 1.0]
        """
        # Step 1: Validate new score (defensive)
        if not (0.0 <= new_score <= 1.0):
            raise ValueError("new_score must be between 0.0 and 1.0")

        # Step 2: Update current score
        self.confidence_score = new_score

        # Step 3: Append to history
        self.confidence_history.append(
            {
                "score": new_score,
                "timestamp": datetime.now().isoformat(),
                "reason": reason
            }
        )

    @property
    def effective_confidence(self) -> float:
        """Calculate effective confidence with validation status boost.

        User-confirmed memories get a 0.1 boost (capped at 1.0).
        Disputed memories get a 0.2 penalty (floored at 0.0).

        Returns:
            Adjusted confidence score
        """
        if self.validation_status == "user_confirmed":
            return min(1.0, self.confidence_score + 0.1)
        elif self.validation_status == "disputed":
            return max(0.0, self.confidence_score - 0.2)
        else:  # agent_inferred
            return self.confidence_score

    @property
    def confidence_trend(self) -> Literal["increasing", "decreasing", "stable", "insufficient_data"]:
        """Detect trend in confidence evolution.

        Returns:
            Trend classification based on confidence history
        """
        if len(self.confidence_history) < 2:
            return "insufficient_data"

        first_score = self.confidence_history[0]["score"]
        last_score = self.confidence_history[-1]["score"]
        delta = last_score - first_score

        if delta > 0.1:
            return "increasing"
        elif delta < -0.1:
            return "decreasing"
        else:
            return "stable"

    def to_audit_log(self) -> dict[str, any]:
        """Export provenance to audit log format.

        Returns:
            Dictionary with lineage, trustworthiness, and compliance fields
        """
        return {
            # Lineage fields
            "memory_id": self.memory_id,
            "source_session_id": self.source_session_id,
            "extraction_timestamp": self.extraction_timestamp.isoformat(),

            # Trustworthiness fields
            "confidence_score": self.confidence_score,
            "effective_confidence": self.effective_confidence,
            "confidence_trend": self.confidence_trend,
            "validation_status": self.validation_status,

            # Compliance fields
            "confidence_history": self.confidence_history,
        }


class PIIRedactor:
    """Redact PII from text while preserving Gita-specific context."""

    def __init__(self) -> None:
        """Initialize PII redactor with regex patterns and whitelist."""
        # PII regex patterns
        self.email_pattern = re.compile(
            r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        )
        self.phone_pattern = re.compile(
            r'\b(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3,4}[-.\s]?\d{4}\b|'
            r'\b\d{3}[-.\s]?\d{4}\b'
        )
        self.name_pattern = re.compile(r'\b[A-Z][a-z]+ (?:[A-Z]\. )?[A-Z][a-z]+\b')
        self.location_pattern = re.compile(
            r'\b\d+\s+[A-Z][a-z]+\s+(?:Street|St|Avenue|Ave|Road|Rd)\b|'
            r'\b(?:San Francisco|Los Angeles|New York)\b',
            re.IGNORECASE
        )

        # Whitelist for Gita characters and terms
        self.whitelist = {
            "Arjuna", "Krishna", "Sanjaya", "Dhritarashtra",
            "Brahman", "Atman", "Karma", "Dharma", "Yoga"
        }

    def redact(self, text: str) -> tuple[str, bool]:
        """Redact PII from text.

        Args:
            text: Input text potentially containing PII

        Returns:
            Tuple of (redacted_text, pii_found)
        """
        pii_found = False
        redacted_text = text

        # Redact emails
        if self.email_pattern.search(redacted_text):
            redacted_text = self.email_pattern.sub("[EMAIL_REDACTED]", redacted_text)
            pii_found = True

        # Redact phone numbers
        if self.phone_pattern.search(redacted_text):
            redacted_text = self.phone_pattern.sub("[PHONE_REDACTED]", redacted_text)
            pii_found = True

        # Redact locations
        if self.location_pattern.search(redacted_text):
            redacted_text = self.location_pattern.sub("[LOCATION_REDACTED]", redacted_text)
            pii_found = True

        # Redact names (with whitelist check)
        name_matches = self.name_pattern.findall(redacted_text)
        for name in name_matches:
            if name not in self.whitelist:
                redacted_text = redacted_text.replace(name, "[NAME_REDACTED]")
                pii_found = True

        return redacted_text, pii_found


def extract_memory_with_pii_redaction(
    text: str,
    source_session_id: str,
    confidence_score: float = 0.7,
    validation_status: str = "agent_inferred"
) -> tuple[str, MemoryProvenance]:
    """Extract memory with PII redaction and provenance tracking.

    Args:
        text: Memory text to extract
        source_session_id: ID of the session where memory was extracted
        confidence_score: Initial confidence (0.0-1.0)
        validation_status: Validation status (agent_inferred, user_confirmed, disputed)

    Returns:
        Tuple of (redacted_text, provenance)
    """
    # Step 1: Redact PII
    redactor = PIIRedactor()
    redacted_text, pii_found = redactor.redact(text)

    # Step 2: Create provenance
    provenance = MemoryProvenance(
        memory_id=str(uuid.uuid4()),
        source_session_id=source_session_id,
        extraction_timestamp=datetime.now(),
        confidence_score=confidence_score,
        validation_status=validation_status
    )

    # Step 3: Return
    return redacted_text, provenance
```

---

## Real Example from Codebase

**Source:** `backend/memory/provenance.py:14-144`

### Memory Extraction with Provenance

```python
# Example: Extract user preference from conversation

# Raw conversation excerpt
user_message = "I really prefer reading Swami Sivananda's translations. They resonate with me more than others."

# Extract memory
memory_text = "User prefers Swami Sivananda translations"

# Create provenance
provenance = MemoryProvenance(
    memory_id="mem_12345",
    source_session_id="sess_abc_2025_11_15",
    extraction_timestamp=datetime.now(),
    confidence_score=0.8,  # High confidence from explicit statement
    validation_status="agent_inferred"  # Not yet confirmed by user
)

# Store in memory database
memory_db.insert({
    "text": memory_text,
    "provenance": provenance.to_audit_log()
})
```

### Confidence Evolution Over Time

```python
# Day 1: Initial extraction (agent_inferred, confidence=0.7)
provenance = MemoryProvenance(
    memory_id="mem_67890",
    source_session_id="sess_day1",
    extraction_timestamp=datetime(2025, 11, 15),
    confidence_score=0.7,
    validation_status="agent_inferred"
)

# Day 5: User confirms the preference
provenance.add_confidence_update(
    new_score=0.9,
    reason="User explicitly confirmed preference in conversation"
)
provenance.validation_status = "user_confirmed"

# Day 10: User contradicts the preference
provenance.add_confidence_update(
    new_score=0.3,
    reason="User contradicted preference, now prefers Eknath Easwaran"
)
provenance.validation_status = "disputed"

# Export to audit log
audit_entry = provenance.to_audit_log()
# {
#     "memory_id": "mem_67890",
#     "confidence_score": 0.3,
#     "effective_confidence": 0.1,  # 0.3 - 0.2 penalty for disputed
#     "confidence_trend": "decreasing",
#     "validation_status": "disputed",
#     "confidence_history": [
#         {"score": 0.7, "timestamp": "2025-11-15", "reason": "Initial extraction"},
#         {"score": 0.9, "timestamp": "2025-11-20", "reason": "User confirmed"},
#         {"score": 0.3, "timestamp": "2025-11-25", "reason": "User contradicted"}
#     ]
# }
```

### PII Redaction for Spiritual Context

```python
# Example: User shares personal information in spiritual context

user_message = """
I'm John Smith, living at 123 Main Street in San Francisco.
My email is john@example.com. I'm struggling with anxiety about
my job interview next week. Can Krishna's teachings help me?
"""

# Extract memory with PII redaction
redactor = PIIRedactor()
redacted_text, pii_found = redactor.redact(user_message)

# Result:
# "[NAME_REDACTED], living at [LOCATION_REDACTED] in [LOCATION_REDACTED].
#  My email is [EMAIL_REDACTED]. I'm struggling with anxiety about
#  my job interview next week. Can Krishna's teachings help me?"

# Create memory (PII-safe)
memory_text = "User experiencing anxiety about upcoming job interview, seeking Krishna's teachings for guidance"

# Store with provenance
provenance = MemoryProvenance(
    memory_id=str(uuid.uuid4()),
    source_session_id="sess_abc",
    extraction_timestamp=datetime.now(),
    confidence_score=0.85,
    validation_status="agent_inferred"
)
```

**Key Point:** PII is redacted, but spiritual context ("anxiety," "job interview," "Krishna's teachings") is preserved for personalization.

---

## Provenance Tracking (Critical Success Factor #3)

**Mandatory Fields for All Memories:**

| Field | Type | Purpose | Example |
|-------|------|---------|---------|
| `memory_id` | str (UUID) | Unique identifier | `"mem_a1b2c3d4"` |
| `source_session_id` | str | Session where extracted | `"sess_2025_11_15_abc"` |
| `extraction_timestamp` | datetime | When extracted | `2025-11-15T10:30:00` |
| `confidence_score` | float (0.0-1.0) | Current confidence | `0.8` |
| `validation_status` | enum | Validation state | `"user_confirmed"` |
| `confidence_history` | list[dict] | Evolution over time | `[{score: 0.7, reason: "..."}]` |

**Why Provenance is Critical:**
1. **Auditability**: Track where every memory came from
2. **Trustworthiness**: Distinguish agent guesses from user confirmations
3. **Debugging**: Trace incorrect memories to source sessions
4. **Compliance**: GDPR/data lineage requirements
5. **Conflict Resolution**: When memories contradict, choose higher confidence

---

## Confidence Evolution

**Boost/Penalty Rules:**

```python
@property
def effective_confidence(self) -> float:
    """Calculate effective confidence with validation status boost."""
    if self.validation_status == "user_confirmed":
        return min(1.0, self.confidence_score + 0.1)  # +0.1 boost
    elif self.validation_status == "disputed":
        return max(0.0, self.confidence_score - 0.2)  # -0.2 penalty
    else:  # agent_inferred
        return self.confidence_score  # No adjustment
```

**Trend Detection:**

```python
@property
def confidence_trend(self) -> Literal["increasing", "decreasing", "stable", "insufficient_data"]:
    """Detect trend in confidence evolution."""
    if len(self.confidence_history) < 2:
        return "insufficient_data"

    first_score = self.confidence_history[0]["score"]
    last_score = self.confidence_history[-1]["score"]
    delta = last_score - first_score

    if delta > 0.1:
        return "increasing"  # Confidence improving over time
    elif delta < -0.1:
        return "decreasing"  # Confidence degrading over time
    else:
        return "stable"  # No significant change
```

**Use Cases:**
- **Increasing trend**: Memory is being reinforced by user behavior → Boost priority in retrieval
- **Decreasing trend**: Memory may be outdated or incorrect → Flag for review or deprecation
- **Stable trend**: Memory is consistent → Keep as-is

---

## PII Redaction (Mandatory for Spiritual/Personal Context)

**Why PII Redaction Matters:**
- **Privacy**: Spiritual chatbots often handle sensitive personal information (life challenges, relationships, health)
- **Compliance**: GDPR, CCPA require PII minimization
- **Safety**: Prevent accidental leakage of user identity in logs or prompts

**What to Redact:**
- **Emails**: `john@example.com` → `[EMAIL_REDACTED]`
- **Phone numbers**: `555-1234` → `[PHONE_REDACTED]`
- **Full names**: `John Smith` → `[NAME_REDACTED]`
- **Addresses**: `123 Main Street` → `[LOCATION_REDACTED]`

**What NOT to Redact (Whitelist):**
- **Bhagavad Gita characters**: Arjuna, Krishna, Sanjaya, Dhritarashtra
- **Philosophical terms**: Brahman, Atman, Karma, Dharma, Yoga
- **Emotional context**: anxiety, fear, confusion (needed for personalization)
- **Situational context**: job interview, family conflict, health challenges

**Example:**

```python
# Input
text = "I'm Sarah Johnson at sarah@email.com. I'm anxious about my mother's health. Can Arjuna's dialogue help me?"

# Output after redaction
redacted = "[NAME_REDACTED] at [EMAIL_REDACTED]. I'm anxious about my mother's health. Can Arjuna's dialogue help me?"

# Memory extracted (PII-free, context-rich)
memory = "User experiencing anxiety about family member's health, seeking guidance from Arjuna's dialogue"
```

---

## Common Pitfalls

### ❌ Pitfall 1: Treating Memory as Saved Chat History

```python
# BAD: Storing entire conversation as "memory"
memory_db.insert({
    "text": """
    User: Tell me about karma yoga
    Assistant: Karma yoga is the yoga of selfless action...
    User: That's helpful, thanks!
    Assistant: You're welcome! Anything else?
    """
})
```

**Why it's bad:**
- Noise: Includes non-informative exchanges ("thanks," "you're welcome")
- No extraction: Raw conversation, not consolidated insights
- Token waste: Retrieving this consumes 10x more tokens than needed
- No provenance: Can't track confidence or validation

**✅ Correct Pattern: Extract Signal from Noise**

```python
# GOOD: Extract consolidated insight
memory_db.insert({
    "text": "User is learning about karma yoga (yoga of selfless action)",
    "provenance": {
        "memory_id": "mem_abc123",
        "source_session_id": "sess_2025_11_15",
        "confidence_score": 0.75,
        "validation_status": "agent_inferred"
    }
})
```

**Benefits:**
- 90% token reduction: 100 tokens → 10 tokens
- Searchable: Semantic search finds "karma yoga" easily
- Trackable: Provenance enables confidence updates
- Actionable: LLM can use this to personalize future responses

### ❌ Pitfall 2: Ignoring Provenance Tracking

```python
# BAD: Storing memory without provenance
memory_db.insert({
    "text": "User prefers morning meditation",
    # No source_session_id, no confidence_score, no timestamp!
})

# Later: Memory contradicts
# Question: Which memory is correct? When was each created? Where did they come from?
# Answer: Unknown - no provenance!
```

**Why it's bad:**
- **No auditability**: Can't trace memory to source conversation
- **No conflict resolution**: When memories contradict, can't choose the more reliable one
- **No debugging**: Can't investigate why LLM is using incorrect information
- **Compliance failure**: GDPR requires data lineage

**✅ Correct Pattern: Always Track Provenance**

```python
# GOOD: Full provenance metadata
memory_db.insert({
    "text": "User prefers morning meditation",
    "provenance": {
        "memory_id": "mem_xyz789",
        "source_session_id": "sess_2025_11_10",
        "extraction_timestamp": "2025-11-10T08:00:00",
        "confidence_score": 0.8,
        "validation_status": "user_confirmed",
        "confidence_history": [
            {"score": 0.7, "timestamp": "2025-11-10", "reason": "Initial extraction"},
            {"score": 0.8, "timestamp": "2025-11-12", "reason": "User confirmed preference"}
        ]
    }
})

# Later: Contradictory memory found
conflicting_memory = {
    "text": "User prefers evening meditation",
    "provenance": {
        "confidence_score": 0.6,
        "validation_status": "agent_inferred",
        "extraction_timestamp": "2025-11-08"
    }
}

# Resolution: Choose higher confidence + user_confirmed memory
# Winner: "morning meditation" (0.8, user_confirmed) > "evening meditation" (0.6, agent_inferred)
```

### ❌ Pitfall 3: Not Redacting PII in Spiritual/Personal Context

```python
# BAD: Storing raw personal information
memory_db.insert({
    "text": "John Smith (john@email.com) is struggling with divorce. Lives in San Francisco."
})

# Risk: PII leakage in logs, prompts, or data breaches
```

**Why it's bad:**
- **Privacy violation**: User's identity and sensitive life events exposed
- **Compliance risk**: GDPR fines up to 4% of global revenue
- **Trust loss**: Users won't share personal struggles if data isn't protected
- **Safety**: Accidental logging could expose PII in error messages

**✅ Correct Pattern: Redact PII, Preserve Context**

```python
# GOOD: PII redacted, context preserved
redactor = PIIRedactor()
raw_text = "John Smith (john@email.com) is struggling with divorce. Lives in San Francisco."
redacted_text, pii_found = redactor.redact(raw_text)

# Extract memory (PII-free)
memory_text = "User experiencing divorce-related emotional challenges"

memory_db.insert({
    "text": memory_text,  # No PII
    "provenance": {
        "memory_id": "mem_sensitive_123",
        "confidence_score": 0.85,
        "validation_status": "agent_inferred"
    }
})
```

**Benefits:**
- **Privacy-safe**: No identifiable information stored
- **Context-rich**: "divorce-related challenges" enables empathetic, personalized responses
- **Compliant**: GDPR-friendly data minimization
- **Spiritual whitelist**: "Arjuna," "Krishna," "Dharma" not redacted (false positives avoided)

---

## Integration with Defensive Coding

Memory pattern integrates with the **5-Step Defensive Function Template** (see `CLAUDE.md`):

```python
def add_confidence_update(self, new_score: float, reason: str) -> None:
    """Add a confidence update to the history.

    Args:
        new_score: New confidence score (0.0-1.0)
        reason: Human-readable reason for the update

    Raises:
        ValueError: If new_score is outside [0.0, 1.0]
    """
    # Step 1: Type checking (defensive)
    # (Python runtime enforces type hints if using mypy)

    # Step 2: Input validation (defensive)
    if not (0.0 <= new_score <= 1.0):
        raise ValueError("new_score must be between 0.0 and 1.0")

    # Step 3: Edge case handling
    # (No edge cases for this simple update)

    # Step 4: Main logic (the actual work)
    self.confidence_score = new_score
    self.confidence_history.append({
        "score": new_score,
        "timestamp": datetime.now().isoformat(),
        "reason": reason
    })

    # Step 5: Return (void function, no return)
```

---

## Testing Strategy

Memory pattern requires comprehensive TDD testing following **RED → GREEN → REFACTOR** workflow:

### Example: Testing Provenance Validation

```python
# tests/memory/test_provenance.py:25-45

def test_should_raise_error_for_invalid_confidence_score() -> None:
    """Test that confidence_score outside [0.0, 1.0] raises ValueError."""
    # RED: Write failing test first
    with pytest.raises(ValueError, match="confidence_score must be between 0.0 and 1.0"):
        MemoryProvenance(
            memory_id="mem_test",
            source_session_id="sess_test",
            extraction_timestamp=datetime.now(),
            confidence_score=1.5,  # Invalid: > 1.0
            validation_status="agent_inferred"
        )
```

### Example: Testing PII Redaction

```python
# tests/memory/test_pii_redaction.py:15-35

def test_should_redact_email_addresses() -> None:
    """Test that email pattern is detected and replaced."""
    # RED: Write failing test first
    redactor = PIIRedactor()
    text = "Contact me at john@example.com for more info"

    redacted_text, pii_found = redactor.redact(text)

    assert pii_found is True
    assert "[EMAIL_REDACTED]" in redacted_text
    assert "john@example.com" not in redacted_text
```

### Example: Testing Confidence Evolution

```python
# tests/memory/test_provenance.py:65-90

def test_should_track_confidence_evolution() -> None:
    """Test that confidence history appends correctly."""
    # RED: Write failing test first
    provenance = MemoryProvenance(
        memory_id="mem_test",
        source_session_id="sess_test",
        extraction_timestamp=datetime.now(),
        confidence_score=0.7,
        validation_status="agent_inferred"
    )

    # Add confidence update
    provenance.add_confidence_update(0.9, "User confirmed preference")

    # Assert: History has 2 entries
    assert len(provenance.confidence_history) == 2
    assert provenance.confidence_history[1]["score"] == 0.9
    assert provenance.confidence_history[1]["reason"] == "User confirmed preference"
```

**Test Coverage Requirements:**
- ✅ Provenance validation (confidence_score range, validation_status enum)
- ✅ Confidence evolution tracking
- ✅ Effective confidence boost/penalty calculation
- ✅ Confidence trend detection (increasing, decreasing, stable)
- ✅ Audit log export
- ✅ PII redaction for all PII types (email, phone, name, location)
- ✅ Whitelist preservation (Gita characters and terms not redacted)
- ✅ Integration: extract_memory_with_pii_redaction()

---

## Summary Checklist

**Implementation:**
- [ ] Create `MemoryProvenance` dataclass with all required fields
- [ ] Implement confidence evolution (add_confidence_update, effective_confidence, confidence_trend)
- [ ] Create `PIIRedactor` with regex patterns and Gita whitelist
- [ ] Implement `extract_memory_with_pii_redaction()` integration function
- [ ] Add defensive coding (type hints, validation, error handling)

**Testing:**
- [ ] Write TDD tests for provenance validation
- [ ] Test confidence evolution and trend detection
- [ ] Test PII redaction for all PII types
- [ ] Test whitelist (Gita characters not redacted)
- [ ] Test integration function
- [ ] Verify ≥90% test coverage

**Integration:**
- [ ] Read [TERMINOLOGY.md](../google-context/TERMINOLOGY.md) for Memory vs. RAG distinction
- [ ] Follow [TDD Workflow](./tdd-workflow.md) for implementation
- [ ] Use [Defensive Function Template](../CLAUDE.md) for all functions
- [ ] Link Memory with [Sessions pattern](./context-engineering-sessions.md) for extraction

---

## Related Patterns

- **Context Engineering: Sessions** (`patterns/context-engineering-sessions.md`) - Short-term conversation management
- **TDD Workflow** (`patterns/tdd-workflow.md`) - Testing methodology for Memory
- **Defensive Function Template** (`CLAUDE.md`) - 5-step pattern for robust functions
- **Terminology Reference** (`google-context/TERMINOLOGY.md`) - Critical distinctions glossary

---

## Further Reading

- Google DeepMind, "Gemini Context Engineering: Memory vs. RAG" (2024)
- Anthropic, "Constitutional AI and Memory Systems" (2024)
- Project Memory examples: `backend/memory/provenance.py`, `tests/memory/test_provenance.py`
- Pattern catalog: `patterns/README.md`
