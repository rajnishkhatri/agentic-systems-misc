# Memory Pattern - Quick Reference

**Pattern:** Long-term user persistence
**Use Case:** Cross-session user preferences and learning patterns
**File:** `backend/memory/provenance.py:14-144`

---

## Core Template

```python
from dataclasses import dataclass, field
from datetime import datetime
from typing import Literal
import re
import uuid

@dataclass
class MemoryProvenance:
    """Provenance metadata for memory entries."""
    memory_id: str
    source_session_id: str
    extraction_timestamp: datetime
    confidence_score: float  # 0.0-1.0
    validation_status: Literal["agent_inferred", "user_confirmed", "disputed"]
    confidence_history: list[dict[str, float | str]] = field(default_factory=list)

    def __post_init__(self) -> None:
        if not (0.0 <= self.confidence_score <= 1.0):
            raise ValueError("confidence_score must be between 0.0 and 1.0")

        if not self.confidence_history:
            self.confidence_history = [{
                "score": self.confidence_score,
                "timestamp": self.extraction_timestamp.isoformat(),
                "reason": "Initial extraction"
            }]

    def add_confidence_update(self, new_score: float, reason: str) -> None:
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
        """Boost/penalty: user_confirmed +0.1, disputed -0.2"""
        if self.validation_status == "user_confirmed":
            return min(1.0, self.confidence_score + 0.1)
        elif self.validation_status == "disputed":
            return max(0.0, self.confidence_score - 0.2)
        return self.confidence_score
```

## PII Redaction

```python
class PIIRedactor:
    """Redact PII, preserve Gita context."""

    def __init__(self) -> None:
        self.email_pattern = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
        self.phone_pattern = re.compile(r'\b(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3,4}[-.\s]?\d{4}\b')
        self.name_pattern = re.compile(r'\b[A-Z][a-z]+ (?:[A-Z]\. )?[A-Z][a-z]+\b')
        self.whitelist = {"Arjuna", "Krishna", "Sanjaya", "Dhritarashtra", "Brahman", "Atman"}

    def redact(self, text: str) -> tuple[str, bool]:
        pii_found = False
        redacted = text
        if self.email_pattern.search(redacted):
            redacted = self.email_pattern.sub("[EMAIL_REDACTED]", redacted)
            pii_found = True
        if self.phone_pattern.search(redacted):
            redacted = self.phone_pattern.sub("[PHONE_REDACTED]", redacted)
            pii_found = True
        # Redact names not in whitelist
        for name in self.name_pattern.findall(redacted):
            if name not in self.whitelist:
                redacted = redacted.replace(name, "[NAME_REDACTED]")
                pii_found = True
        return redacted, pii_found
```

## Integration Function

```python
def extract_memory_with_pii_redaction(
    text: str,
    source_session_id: str,
    confidence_score: float = 0.7,
    validation_status: str = "agent_inferred"
) -> tuple[str, MemoryProvenance]:
    """Extract memory with PII redaction and provenance."""
    redactor = PIIRedactor()
    redacted_text, _ = redactor.redact(text)

    provenance = MemoryProvenance(
        memory_id=str(uuid.uuid4()),
        source_session_id=source_session_id,
        extraction_timestamp=datetime.now(),
        confidence_score=confidence_score,
        validation_status=validation_status
    )
    return redacted_text, provenance
```

## Usage Example

```python
# Extract memory
memory_text = "User prefers Swami Sivananda translations"
redacted, provenance = extract_memory_with_pii_redaction(
    memory_text, source_session_id="sess_abc", confidence_score=0.8
)

# Update confidence
provenance.add_confidence_update(0.9, "User confirmed preference")
provenance.validation_status = "user_confirmed"

# Export audit log
audit = provenance.to_audit_log()
```

---

**See also:**
- [Tutorial](./memory-tutorial.md) - Full explanation with examples
- [Advanced](./memory-advanced.md) - Pitfalls, conflict resolution, production
- [TERMINOLOGY.md](../google-context/TERMINOLOGY.md) - Memory vs. RAG distinction
