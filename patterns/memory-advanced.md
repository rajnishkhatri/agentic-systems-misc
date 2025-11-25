# Memory Pattern - Advanced Guide

**Pattern:** Long-term user persistence
**Audience:** Senior engineers optimizing for production
**Reading Time:** 12-15 minutes

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

---

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

---

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

## Conflict Resolution Strategies

When multiple memories contradict, use these strategies:

### Strategy 1: Confidence-Based Winner (Default)

```python
def resolve_conflicts(memories: list[dict]) -> dict:
    """Choose memory with highest effective confidence."""
    # Sort by effective_confidence descending
    sorted_memories = sorted(
        memories,
        key=lambda m: m["provenance"]["effective_confidence"],
        reverse=True
    )
    return sorted_memories[0]

# Example
memory_1 = {"text": "User prefers morning meditation", "provenance": {"confidence_score": 0.8, "validation_status": "user_confirmed"}}  # effective: 0.9
memory_2 = {"text": "User prefers evening meditation", "provenance": {"confidence_score": 0.6, "validation_status": "agent_inferred"}}  # effective: 0.6

winner = resolve_conflicts([memory_1, memory_2])
# Result: memory_1 (effective_confidence 0.9 > 0.6)
```

### Strategy 2: Recency-Based (Temporal)

```python
def resolve_conflicts_by_recency(memories: list[dict]) -> dict:
    """Choose most recently extracted memory."""
    sorted_memories = sorted(
        memories,
        key=lambda m: m["provenance"]["extraction_timestamp"],
        reverse=True
    )
    return sorted_memories[0]

# Use case: User preferences change over time
# Example: User initially preferred morning meditation (2025-11-01) but switched to evening (2025-11-20)
```

### Strategy 3: Hybrid (Confidence + Recency)

```python
from datetime import datetime, timedelta

def resolve_conflicts_hybrid(memories: list[dict], recency_weight: float = 0.3) -> dict:
    """Combine confidence and recency with weighted score."""
    now = datetime.now()

    def score(memory: dict) -> float:
        effective_conf = memory["provenance"]["effective_confidence"]
        extraction_time = datetime.fromisoformat(memory["provenance"]["extraction_timestamp"])
        days_old = (now - extraction_time).days

        # Decay confidence by 10% per 30 days
        recency_factor = max(0.0, 1.0 - (days_old / 30) * 0.1)

        return (1 - recency_weight) * effective_conf + recency_weight * recency_factor

    return max(memories, key=score)

# Example: 60-day old memory (0.9 confidence) vs. 5-day old memory (0.7 confidence)
# Old: (0.7 * 0.9) + (0.3 * 0.8) = 0.87
# Recent: (0.7 * 0.7) + (0.3 * 0.95) = 0.775
# Winner: Old memory (higher confidence outweighs age)
```

### Strategy 4: Ask User (Interactive)

```python
async def resolve_conflicts_interactive(memories: list[dict], llm) -> dict:
    """Present conflict to user for resolution."""
    conflict_prompt = f"""
    I found conflicting information in my memory:
    1. {memories[0]["text"]}
    2. {memories[1]["text"]}

    Which is correct, or has your preference changed?
    """

    user_response = await llm.ask_user(conflict_prompt)

    # Parse user selection and update validation_status
    if "1" in user_response:
        memories[0]["provenance"]["validation_status"] = "user_confirmed"
        memories[1]["provenance"]["validation_status"] = "disputed"
        return memories[0]
    elif "2" in user_response:
        memories[1]["provenance"]["validation_status"] = "user_confirmed"
        memories[0]["provenance"]["validation_status"] = "disputed"
        return memories[1]
```

---

## Memory Lifecycle Management

### Staleness Detection

```python
from datetime import datetime, timedelta

class MemoryStore:
    def detect_stale_memories(self, threshold_days: int = 90) -> list[dict]:
        """Identify memories that haven't been reaffirmed in N days."""
        stale = []
        now = datetime.now()

        for memory in self.memories:
            extraction_time = datetime.fromisoformat(
                memory["provenance"]["extraction_timestamp"]
            )
            days_old = (now - extraction_time).days

            # Check if confidence has degraded
            trend = memory["provenance"]["confidence_trend"]

            if days_old > threshold_days and trend == "decreasing":
                stale.append(memory)

        return stale

# Usage: Flag for review or deprecation
stale_memories = store.detect_stale_memories(threshold_days=90)
for memory in stale_memories:
    logger.warning(f"Stale memory detected: {memory['memory_id']}")
```

### Memory Deprecation

```python
class MemoryStore:
    def deprecate_memory(self, memory_id: str, reason: str) -> None:
        """Mark memory as deprecated (soft delete)."""
        memory = self.get_by_id(memory_id)

        # Add deprecation metadata
        memory["deprecated"] = True
        memory["deprecation_reason"] = reason
        memory["deprecation_timestamp"] = datetime.now().isoformat()

        # Don't delete - preserve for audit trail
        self.update(memory)

# Usage
store.deprecate_memory("mem_xyz", reason="User contradicted preference after 90 days")
```

### Memory Consolidation

```python
def consolidate_related_memories(memories: list[dict]) -> dict:
    """Merge related memories into single consolidated memory."""
    # Example: Multiple memories about user's Gita study progress
    # Memory 1: "User is learning about karma yoga"
    # Memory 2: "User completed Chapter 3 study"
    # Memory 3: "User asks questions about selfless action"

    # Consolidated: "User is studying karma yoga (Chapter 3, selfless action)"

    consolidated_text = " | ".join([m["text"] for m in memories])

    # Choose provenance from highest-confidence memory
    best_provenance = max(
        memories,
        key=lambda m: m["provenance"]["effective_confidence"]
    )["provenance"]

    return {
        "text": consolidated_text,
        "provenance": best_provenance,
        "consolidated_from": [m["memory_id"] for m in memories]
    }
```

---

## Production Considerations

### 1. Memory Retrieval Optimization

**Problem:** Retrieving 100+ memories for every query is expensive (tokens + latency).

**Solution A: Semantic Search with Threshold**

```python
def retrieve_relevant_memories(query: str, top_k: int = 5, threshold: float = 0.7) -> list[dict]:
    """Retrieve only highly relevant memories."""
    # Semantic search (cosine similarity)
    all_results = vector_db.search(query, top_k=top_k)

    # Filter by confidence and relevance
    filtered = [
        m for m in all_results
        if m["similarity"] > threshold and m["provenance"]["effective_confidence"] > 0.6
    ]

    return filtered

# Usage
memories = retrieve_relevant_memories("How do I practice karma yoga?", top_k=5, threshold=0.75)
```

**Solution B: Category-Based Retrieval**

```python
class MemoryStore:
    def __init__(self):
        self.categories = {
            "preferences": [],
            "knowledge_level": [],
            "life_context": [],
            "study_history": []
        }

    def retrieve_by_category(self, categories: list[str]) -> list[dict]:
        """Retrieve memories from specific categories only."""
        results = []
        for cat in categories:
            results.extend(self.categories[cat])
        return results

# Usage: For spiritual guidance queries, only load life_context + preferences
memories = store.retrieve_by_category(["life_context", "preferences"])
```

### 2. Memory Versioning

```python
@dataclass
class MemoryVersion:
    """Track memory evolution over time."""
    memory_id: str
    version: int
    text: str
    provenance: MemoryProvenance
    supersedes: str | None  # Previous version memory_id

# Usage
v1 = MemoryVersion(
    memory_id="mem_abc_v1",
    version=1,
    text="User prefers morning meditation",
    provenance=...,
    supersedes=None
)

# User updates preference
v2 = MemoryVersion(
    memory_id="mem_abc_v2",
    version=2,
    text="User prefers evening meditation",
    provenance=...,
    supersedes="mem_abc_v1"  # Links to previous version
)

# Audit: Trace preference evolution
versions = get_version_history("mem_abc")
# [v1, v2] - Shows preference changed over time
```

### 3. Multi-User Memory Isolation

```python
class UserMemoryStore:
    def __init__(self):
        self._stores: dict[str, list[dict]] = {}

    def get_user_memories(self, user_id: str) -> list[dict]:
        """Retrieve memories for specific user only."""
        if user_id not in self._stores:
            return []
        return self._stores[user_id]

    def add_memory(self, user_id: str, memory: dict) -> None:
        """Add memory with user isolation."""
        if user_id not in self._stores:
            self._stores[user_id] = []

        # Validate memory belongs to user
        if memory["provenance"]["user_id"] != user_id:
            raise ValueError("Memory user_id mismatch")

        self._stores[user_id].append(memory)

    def delete_user_memories(self, user_id: str) -> None:
        """GDPR Right to Erasure: Delete all user memories."""
        if user_id in self._stores:
            del self._stores[user_id]
```

---

## Advanced PII Redaction

### Custom Regex Patterns (Domain-Specific)

```python
class AdvancedPIIRedactor(PIIRedactor):
    def __init__(self):
        super().__init__()

        # Banking-specific PII
        self.account_number_pattern = re.compile(r'\b\d{8,12}\b')
        self.ssn_pattern = re.compile(r'\b\d{3}-\d{2}-\d{4}\b')

        # Medical-specific PII (HIPAA)
        self.medical_record_pattern = re.compile(r'\b(?:MRN|Patient ID):\s*\d+\b', re.IGNORECASE)

    def redact(self, text: str) -> tuple[str, bool]:
        redacted_text, pii_found = super().redact(text)

        # Additional domain-specific redaction
        if self.account_number_pattern.search(redacted_text):
            redacted_text = self.account_number_pattern.sub("[ACCOUNT_REDACTED]", redacted_text)
            pii_found = True

        if self.ssn_pattern.search(redacted_text):
            redacted_text = self.ssn_pattern.sub("[SSN_REDACTED]", redacted_text)
            pii_found = True

        return redacted_text, pii_found
```

### False Positive Handling

```python
def redact_with_context_check(text: str, redactor: PIIRedactor) -> tuple[str, bool]:
    """Redact PII but preserve false positives based on context."""

    # Step 1: Initial redaction
    redacted, pii_found = redactor.redact(text)

    # Step 2: Restore false positives
    # Example: "John Smith" in "The teaching of John Smith Yoga School"
    if "Yoga School" in redacted:
        # Likely a business name, not PII - restore
        redacted = redacted.replace("[NAME_REDACTED] Yoga School", "John Smith Yoga School")

    return redacted, pii_found
```

---

## Monitoring & Observability

```python
class MemoryMetrics:
    def __init__(self):
        self.total_memories = 0
        self.memories_by_status = {"agent_inferred": 0, "user_confirmed": 0, "disputed": 0}
        self.avg_confidence = 0.0
        self.stale_count = 0

    def update(self, memory: dict) -> None:
        self.total_memories += 1
        status = memory["provenance"]["validation_status"]
        self.memories_by_status[status] += 1

        # Recalculate average confidence
        all_confidences = [m["provenance"]["confidence_score"] for m in all_memories]
        self.avg_confidence = sum(all_confidences) / len(all_confidences)

    def export_dashboard(self) -> dict:
        return {
            "total_memories": self.total_memories,
            "confirmed_ratio": self.memories_by_status["user_confirmed"] / max(1, self.total_memories),
            "disputed_ratio": self.memories_by_status["disputed"] / max(1, self.total_memories),
            "avg_confidence": self.avg_confidence,
            "stale_memories": self.stale_count,
        }

# Usage
metrics = MemoryMetrics()
dashboard = metrics.export_dashboard()
logger.info(f"Memory health: {dashboard}")
```

**Monitor for:**
- `confirmed_ratio` - Low ratio = poor user validation loop
- `disputed_ratio` - High ratio = agent extraction quality issues
- `avg_confidence` - Declining = memories becoming unreliable
- `stale_memories` - Growing = need memory refresh workflow

---

## Related Patterns

- [Sessions Pattern - Tutorial](./sessions-tutorial.md) - Short-term conversation management
- [TDD Workflow](./tdd-workflow.md) - Testing methodology
- [Quick Reference](./memory-quickref.md) - Code templates
- [Tutorial](./memory-tutorial.md) - Full explanation

---

## Further Reading

- Google DeepMind, "Gemini Context Engineering: Memory vs. RAG" (2024)
- Anthropic, "Constitutional AI and Memory Systems" (2024)
- [TERMINOLOGY.md](../google-context/TERMINOLOGY.md) - Critical distinctions
- [Pattern Library](./README.md) - All patterns
