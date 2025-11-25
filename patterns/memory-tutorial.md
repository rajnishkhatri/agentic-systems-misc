# Memory Pattern - Tutorial

**Pattern:** Long-term user persistence
**Complexity:** ⭐⭐⭐⭐ (Expert)
**Reading Time:** 15-18 minutes
**Created:** 2025-11-23

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

---

## Terminology Foundation

Before using this pattern, **understand these critical distinctions:**

1. **Memory vs. RAG (Knowledge Retrieval)**
   - **Memory** = User-specific (personal assistant) - "User prefers morning meditation"
   - **RAG** = General knowledge (research librarian) - "Chapter 3 discusses karma yoga"
   - See [TERMINOLOGY.md](../google-context/TERMINOLOGY.md#memory-vs-rag)

2. **Memory vs. Session History**
   - **Memory** = Consolidated facts that persist across sessions (long-term)
   - **Session History** = Transient conversation logs within one session (short-term)

3. **Proactive vs. Reactive Memory Retrieval**
   - **Proactive** = Auto-load memories into context window (higher tokens, no misses)
   - **Reactive** = Agent tool call retrieves memories on demand (lower tokens, requires smart agent)

**⚠️ CRITICAL:** Read [TERMINOLOGY.md](../google-context/TERMINOLOGY.md) first or you will treat Memory as "saved chat history."

---

## When to Use This Pattern

✅ **Use Memory pattern when:**
- Building multi-session applications (user returns days/weeks later)
- Personalizing AI responses based on user preferences and history
- Tracking user knowledge evolution (e.g., beginner → expert in Bhagavad Gita study)
- Storing user context that spans sessions (e.g., "User is preparing for job interview")
- Implementing spiritual guidance chatbots where personal context matters
- Needing to audit memory extraction for trustworthiness and compliance

❌ **DON'T use Memory pattern when:**
- Building single-session Q&A (no persistence needed) - use Sessions pattern instead
- Storing general knowledge facts (e.g., "Paris is capital of France") - use RAG instead
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
        """Validate fields and initialize confidence history."""
        if not (0.0 <= self.confidence_score <= 1.0):
            raise ValueError("confidence_score must be between 0.0 and 1.0")

        valid_statuses = {"agent_inferred", "user_confirmed", "disputed"}
        if self.validation_status not in valid_statuses:
            raise ValueError(f"validation_status must be one of {valid_statuses}")

        if not self.confidence_history:
            self.confidence_history = [{
                "score": self.confidence_score,
                "timestamp": self.extraction_timestamp.isoformat(),
                "reason": "Initial extraction"
            }]

    def add_confidence_update(self, new_score: float, reason: str) -> None:
        """Add a confidence update to the history."""
        if not (0.0 <= new_score <= 1.0):
            raise ValueError("new_score must be between 0.0 and 1.0")

        self.confidence_score = new_score
        self.confidence_history.append({
            "score": new_score,
            "timestamp": datetime.now().isoformat(),
            "reason": reason
        })

    @property
    def effective_confidence(self) -> float:
        """Calculate effective confidence with validation status boost.

        User-confirmed memories get +0.1 boost (capped at 1.0).
        Disputed memories get -0.2 penalty (floored at 0.0).
        """
        if self.validation_status == "user_confirmed":
            return min(1.0, self.confidence_score + 0.1)
        elif self.validation_status == "disputed":
            return max(0.0, self.confidence_score - 0.2)
        return self.confidence_score

    @property
    def confidence_trend(self) -> Literal["increasing", "decreasing", "stable", "insufficient_data"]:
        """Detect trend in confidence evolution."""
        if len(self.confidence_history) < 2:
            return "insufficient_data"

        first_score = self.confidence_history[0]["score"]
        last_score = self.confidence_history[-1]["score"]
        delta = last_score - first_score

        if delta > 0.1: return "increasing"
        elif delta < -0.1: return "decreasing"
        else: return "stable"

    def to_audit_log(self) -> dict[str, any]:
        """Export provenance to audit log format."""
        return {
            "memory_id": self.memory_id,
            "source_session_id": self.source_session_id,
            "extraction_timestamp": self.extraction_timestamp.isoformat(),
            "confidence_score": self.confidence_score,
            "effective_confidence": self.effective_confidence,
            "confidence_trend": self.confidence_trend,
            "validation_status": self.validation_status,
            "confidence_history": self.confidence_history,
        }


class PIIRedactor:
    """Redact PII from text while preserving Gita-specific context."""

    def __init__(self) -> None:
        """Initialize PII redactor with regex patterns and whitelist."""
        self.email_pattern = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
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
        """Redact PII from text."""
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
    """Extract memory with PII redaction and provenance tracking."""
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

## Real Example: Confidence Evolution

**Source:** `backend/memory/provenance.py:14-144`

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
provenance.add_confidence_update(0.9, "User explicitly confirmed preference")
provenance.validation_status = "user_confirmed"

# Day 10: User contradicts the preference
provenance.add_confidence_update(0.3, "User contradicted preference")
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

---

## Real Example: PII Redaction

```python
# User shares personal information in spiritual context
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
memory_text = "User experiencing anxiety about upcoming job interview, seeking Krishna's teachings"

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

## Provenance Tracking (Critical)

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
    return self.confidence_score  # No adjustment for agent_inferred
```

**Trend Detection:**

```python
@property
def confidence_trend(self) -> Literal["increasing", "decreasing", "stable", "insufficient_data"]:
    if len(self.confidence_history) < 2:
        return "insufficient_data"

    first_score = self.confidence_history[0]["score"]
    last_score = self.confidence_history[-1]["score"]
    delta = last_score - first_score

    if delta > 0.1: return "increasing"
    elif delta < -0.1: return "decreasing"
    else: return "stable"
```

**Use Cases:**
- **Increasing trend**: Memory reinforced by user behavior → Boost priority in retrieval
- **Decreasing trend**: Memory may be outdated → Flag for review or deprecation
- **Stable trend**: Memory is consistent → Keep as-is

---

## PII Redaction (Mandatory)

**Why PII Redaction Matters:**
- **Privacy**: Spiritual chatbots handle sensitive personal information
- **Compliance**: GDPR, CCPA require PII minimization
- **Safety**: Prevent accidental leakage in logs or prompts

**What to Redact:**
- **Emails**: `john@example.com` → `[EMAIL_REDACTED]`
- **Phone numbers**: `555-1234` → `[PHONE_REDACTED]`
- **Full names**: `John Smith` → `[NAME_REDACTED]`
- **Addresses**: `123 Main Street` → `[LOCATION_REDACTED]`

**What NOT to Redact (Whitelist):**
- **Bhagavad Gita characters**: Arjuna, Krishna, Sanjaya
- **Philosophical terms**: Brahman, Atman, Karma, Dharma
- **Emotional context**: anxiety, fear (needed for personalization)
- **Situational context**: job interview, family conflict

---

## Testing Strategy

Memory pattern requires TDD testing following **RED → GREEN → REFACTOR**:

### Test 1: Provenance Validation

```python
def test_should_raise_error_for_invalid_confidence_score() -> None:
    """Test that confidence_score outside [0.0, 1.0] raises ValueError."""
    with pytest.raises(ValueError, match="confidence_score must be between 0.0 and 1.0"):
        MemoryProvenance(
            memory_id="mem_test",
            source_session_id="sess_test",
            extraction_timestamp=datetime.now(),
            confidence_score=1.5,  # Invalid: > 1.0
            validation_status="agent_inferred"
        )
```

### Test 2: PII Redaction

```python
def test_should_redact_email_addresses() -> None:
    """Test that email pattern is detected and replaced."""
    redactor = PIIRedactor()
    text = "Contact me at john@example.com for more info"

    redacted_text, pii_found = redactor.redact(text)

    assert pii_found is True
    assert "[EMAIL_REDACTED]" in redacted_text
    assert "john@example.com" not in redacted_text
```

### Test 3: Confidence Evolution

```python
def test_should_track_confidence_evolution() -> None:
    """Test that confidence history appends correctly."""
    provenance = MemoryProvenance(
        memory_id="mem_test",
        source_session_id="sess_test",
        extraction_timestamp=datetime.now(),
        confidence_score=0.7,
        validation_status="agent_inferred"
    )

    provenance.add_confidence_update(0.9, "User confirmed preference")

    assert len(provenance.confidence_history) == 2
    assert provenance.confidence_history[1]["score"] == 0.9
```

**Test Coverage Requirements:**
- ✅ Provenance validation (confidence_score range, validation_status enum)
- ✅ Confidence evolution tracking
- ✅ Effective confidence boost/penalty calculation
- ✅ PII redaction for all types (email, phone, name, location)
- ✅ Whitelist preservation (Gita characters not redacted)

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
- [ ] Verify ≥90% test coverage

**Integration:**
- [ ] Read [TERMINOLOGY.md](../google-context/TERMINOLOGY.md) for Memory vs. RAG distinction
- [ ] Follow [TDD Workflow](./tdd-workflow.md) for implementation
- [ ] Link Memory with [Sessions pattern](./sessions-tutorial.md) for extraction

---

**See also:**
- [Quick Reference](./memory-quickref.md) - Code templates only
- [Advanced Guide](./memory-advanced.md) - Pitfalls, conflict resolution, production
- [Pattern Library](./README.md) - All patterns
