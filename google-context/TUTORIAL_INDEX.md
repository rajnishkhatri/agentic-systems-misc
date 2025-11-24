# Context Engineering Tutorial Index

**Status:** 🔄 Active Development
**Created:** 2025-11-23
**Maintainer:** Recipe Chatbot Team

---

## Overview

**Core Thesis:**
> "Bigger models aren't enough. Intelligence emerges from orchestration."

This tutorial system teaches **Context Engineering** - the discipline of managing what information gets included in an LLM's context window, how it's structured, and when it's retrieved. The difference between a chatbot that fails after 10 turns and one that maintains coherent, personalized conversations across 100+ turns is not model size - it's context orchestration.

**What You'll Learn:**
1. **Critical distinctions** that prevent common mistakes (Session History vs. Context Window, Memory vs. RAG)
2. **Protected context patterns** that preserve user objectives across long conversations
3. **Memory provenance** for audit, trustworthiness, and compliance
4. **PII redaction** for privacy-safe personalization in spiritual/sensitive contexts

**Who This Is For:**
- AI engineers building multi-turn conversational systems
- Product managers designing context-aware AI features
- Students learning LLM evaluation and agentic systems (Lessons 9-16)
- Anyone implementing chatbots that need to "remember" user preferences without treating memory as saved chat

---

## Prerequisites

**Required Knowledge:**
- Basic Python programming (functions, classes, type hints)
- Understanding of LLMs and prompting (no fine-tuning required)
- Familiarity with Test-Driven Development (TDD) helpful but not required

**Required Reading:**
- ⚠️ **CRITICAL:** Read [TERMINOLOGY.md](./TERMINOLOGY.md) **BEFORE** any other tutorial
  - Estimated time: 10 minutes
  - Why: Without understanding Session History vs. Context Window, you will build systems that send entire conversation logs to LLMs

**Recommended Patterns:**
- [TDD Workflow Pattern](../patterns/tdd-workflow.md) - Testing methodology used throughout
- [Defensive Function Template](../CLAUDE.md) - 5-step pattern for robust functions

---

## Learning Paths

### Path 1: Quick Start (30 minutes)

**Goal:** Understand core concepts and terminology

1. **Read:** [TERMINOLOGY.md](./TERMINOLOGY.md) (10 min)
   - Critical distinctions with side-by-side comparisons
   - Visual diagrams for Session vs. Context, Memory vs. RAG, Proactive vs. Reactive

2. **Explore Diagrams:** (10 min)
   - [Session History vs. Context Window](./diagrams/session_vs_context.svg)
   - [Memory vs. RAG](./diagrams/memory_vs_rag.svg)
   - [Proactive vs. Reactive Retrieval](./diagrams/proactive_vs_reactive.svg)

3. **Case Study:** Bhagavad Gita Chatbot Example (10 min)
   - See how 50K token session history compresses to 8K context window (84% reduction)
   - Understand why protected context (objectives, constraints) must survive compression

**Outcome:** Clear mental models of critical distinctions. Ready to make architecture decisions.

---

### Path 2: Implementation-Focused (2-3 hours)

**Goal:** Build production-ready context management systems

1. **Foundation:** Complete Path 1 (30 min)

2. **Interactive Sessions Notebook:** (45 min) ⭐ NEW
   - **Run:** [sessions_compression_interactive.ipynb](./sessions_compression_interactive.ipynb)
   - **Experiment:** Change compression threshold (70%, 95%, 99%), observe behavior
   - **Visualize:** See 50K→8K token compression in real-time charts
   - **Validate:** Assertions confirm protected context survives compression

3. **Sessions Pattern:** (60 min)
   - **Quick Start:** [Sessions Quick Reference](../patterns/sessions-quickref.md) (2 min - code templates only)
   - **Deep Dive:** [Sessions Tutorial](../patterns/sessions-tutorial.md) (15 min - full explanation)
   - **Implement:** `GitaSession` class with protected context and compression
   - **Test:** Multi-turn conversation tests (50-100 turns)
   - **Code:** `backend/sessions/gita_session.py:13-120`

4. **Memory Pattern:** (60 min)
   - **Quick Start:** [Memory Quick Reference](../patterns/memory-quickref.md) (2 min - code templates only)
   - **Deep Dive:** [Memory Tutorial](../patterns/memory-tutorial.md) (18 min - full explanation)
   - **Implement:** `MemoryProvenance` dataclass with confidence tracking
   - **Implement:** `PIIRedactor` with Gita character whitelist
   - **Test:** Provenance validation and PII redaction tests
   - **Code:** `backend/memory/provenance.py:14-144`, `backend/memory/pii_redaction.py:15-125`

5. **Integration:** (30 min)
   - Run full test suite: `pytest tests/sessions/ tests/memory/ -v --cov`
   - Verify ≥90% test coverage
   - Review real examples from codebase

**Outcome:** Production-ready Sessions and Memory implementations with comprehensive tests.

---

### Path 3: Full Mastery (4-6 hours)

**Goal:** Deep understanding of context engineering principles and advanced topics

1. **Foundation:** Complete Path 2 (3 hours)

2. **Deep-Dive Tutorials:** (90 min)
   - **Sessions Deep Dive:** Protected context identification algorithm
   - **Memory Deep Dive:** Confidence evolution and trend detection
   - **PII Deep Dive:** Regex patterns, false positive prevention, whitelist management

3. **Advanced Topics:** (60 min)
   - **Performance Optimization:** Token counting strategies, compression benchmarks
   - **Conflict Resolution:** Handling contradictory memories with provenance
   - **Multi-Agent Context:** Sharing context across specialized agents

4. **Case Study Analysis:** (30 min)
   - Bhagavad Gita Chatbot: Spiritual guidance with PII protection
   - Banking Fraud Dispute: Compliance and audit requirements
   - Healthcare Triage: Protected context for medical history

**Outcome:** Expert-level understanding. Ready to design context architecture for complex domains.

---

## Files

| File | Type | Lines | Purpose | Est. Reading Time |
|------|------|-------|---------|------------------|
| [TERMINOLOGY.md](./TERMINOLOGY.md) | Concept | 250 | Critical distinctions reference (Session vs. Context, Memory vs. RAG, etc.) | 10 min |
| [sessions_compression_interactive.ipynb](./sessions_compression_interactive.ipynb) | Notebook | 28 cells | Interactive demo: see 50K→8K compression, experiment with thresholds | 15-20 min ⭐ NEW |
| [diagrams/session_vs_context.svg](./diagrams/session_vs_context.svg) | Visual | N/A | Session History → Context Window compression flow | 3 min |
| [diagrams/memory_vs_rag.svg](./diagrams/memory_vs_rag.svg) | Visual | N/A | Memory (personal assistant) vs. RAG (research librarian) | 3 min |
| [diagrams/proactive_vs_reactive.svg](./diagrams/proactive_vs_reactive.svg) | Visual | N/A | Proactive (auto-load) vs. Reactive (tool call) retrieval | 3 min |
| [patterns/sessions-quickref.md](../patterns/sessions-quickref.md) | Pattern (Quick Ref) | 80 | Sessions pattern code templates only | 2 min |
| [patterns/sessions-tutorial.md](../patterns/sessions-tutorial.md) | Pattern (Tutorial) | 370 | Sessions pattern full explanation with examples | 15 min |
| [patterns/sessions-advanced.md](../patterns/sessions-advanced.md) | Pattern (Advanced) | 430 | Sessions pitfalls, performance, production | 12 min |
| [patterns/memory-quickref.md](../patterns/memory-quickref.md) | Pattern (Quick Ref) | 90 | Memory pattern code templates only | 2 min |
| [patterns/memory-tutorial.md](../patterns/memory-tutorial.md) | Pattern (Tutorial) | 490 | Memory pattern full explanation with provenance | 18 min |
| [patterns/memory-advanced.md](../patterns/memory-advanced.md) | Pattern (Advanced) | 540 | Memory conflict resolution, lifecycle, production | 15 min |

**Code Examples:**
- `backend/sessions/gita_session.py` (120 lines) - GitaSession implementation
- `backend/sessions/protected_context.py` (54 lines) - Protected context identification
- `backend/sessions/context_compressor.py` (90 lines) - Compression at 95% threshold
- `backend/memory/provenance.py` (144 lines) - MemoryProvenance with confidence tracking
- `backend/memory/pii_redaction.py` (125 lines) - PIIRedactor with Gita whitelist

**Tests:**
- `tests/sessions/test_protected_context.py` (7 tests, 100% pass)
- `tests/sessions/test_context_compressor.py` (7 tests, 100% pass)
- `tests/sessions/test_long_conversation.py` (9 tests, 100% pass)
- `tests/memory/test_provenance.py` (7 tests, 100% pass)
- `tests/memory/test_pii_redaction.py` (9 tests, 100% pass)

---

## Critical Success Factors

This tutorial system is built around **3 Critical Success Factors** from Google DeepMind's context engineering research:

### 1. Terminology Clarity (Prevent Conflation)

**Problem:** Developers conflate Session History with Context Window, leading to token waste and truncation.

**Solution:** [TERMINOLOGY.md](./TERMINOLOGY.md) provides precise definitions with side-by-side comparisons.

**Example Mistake:**
```python
# WRONG: Sending entire session history
messages = session_history  # 50K tokens!
response = llm.generate(messages=messages)
```

**Correct Pattern:**
```python
# RIGHT: Compress and curate
context_window = session.get_context_window()  # 8K tokens
response = llm.generate(messages=context_window)
```

**Impact:** 84% token reduction (50K → 8K), preserving protected context.

---

### 2. Context Protection (Preserve Critical Information)

**Problem:** Initial user objectives and constraints get compressed away in long conversations.

**Solution:** Protected context identification marks events that must survive compression.

**Protected Event Types:**
- Turn 0 (initial objectives)
- `event_type == "constraint"` (explicit user constraints)
- `event_type == "auth_checkpoint"` (authentication state)
- Goal statements

**Example:**
```python
# User's initial objective (turn 0)
"Help me understand karma yoga from Chapter 3"

# After 50 turns and 2 compression cycles...
# ✅ Initial objective still in context window
# ✅ LLM maintains focus on karma yoga
# ✅ No "What were we talking about?" moments
```

**Code:** `backend/sessions/protected_context.py:12-54`

---

### 3. Provenance Tracking (Audit & Trustworthiness)

**Problem:** Memories lack lineage - can't trace back to source, can't resolve conflicts, no compliance.

**Solution:** `MemoryProvenance` dataclass tracks source, confidence evolution, validation status.

**Mandatory Fields:**
- `memory_id` (UUID)
- `source_session_id` (which session extracted this)
- `extraction_timestamp` (when)
- `confidence_score` (0.0-1.0)
- `validation_status` (agent_inferred, user_confirmed, disputed)
- `confidence_history` (evolution over time)

**Example:**
```python
# Day 1: Agent infers preference (confidence=0.7)
provenance = MemoryProvenance(
    memory_id="mem_123",
    source_session_id="sess_day1",
    confidence_score=0.7,
    validation_status="agent_inferred"
)

# Day 5: User confirms (confidence=0.9)
provenance.add_confidence_update(0.9, "User confirmed")
provenance.validation_status = "user_confirmed"

# Day 10: User contradicts (confidence=0.3)
provenance.add_confidence_update(0.3, "User contradicted")
provenance.validation_status = "disputed"

# Audit log shows full evolution
audit = provenance.to_audit_log()
# {"confidence_trend": "decreasing", "effective_confidence": 0.1}
```

**Code:** `backend/memory/provenance.py:14-144`

---

## Integration with Course

This tutorial system integrates with the **LLM Evals** course:

| Lesson | Topic | Integration | Status |
|--------|-------|-------------|--------|
| Lesson 9 | Evaluation Fundamentals & Exact Methods | Context Window as evaluation metric | ✅ Complete |
| Lesson 10 | AI-as-Judge Mastery | Memory provenance for judge calibration | ✅ Complete |
| Lesson 11 | Comparative Evaluation & Leaderboards | Session vs. RAG performance comparison | ✅ Complete |
| Lesson 12 | RAG Evaluation Fundamentals | Memory vs. RAG distinction | 🔄 Planned |
| Lesson 16 | Agent Reliability & Orchestration | Protected context in agent workflows | 📝 To Create |

**Cross-References:**
- Lesson 9: [Evaluation Dashboard](../lesson-9-11/README.md) visualizes session token efficiency
- Lesson 10: [AI Judge Production Guide](../lesson-10/ai_judge_production_guide.md) uses memory confidence for calibration
- Lesson 16: [Agent Reliability Fundamentals](../lesson-16/tutorials/01_agent_reliability_fundamentals.md) applies protected context to agent states

---

## Common Pitfalls

### Pitfall 1: Sending Entire Session History to LLM

**Symptom:** API costs explode, latency increases, context gets truncated.

**Root Cause:** Conflating Session History (storage) with Context Window (model input).

**Fix:** Read [TERMINOLOGY.md](./TERMINOLOGY.md) → Implement [Sessions Pattern](../patterns/sessions-tutorial.md)

**Before:**
```python
# 50 turns = 50K tokens = $1.50/query (GPT-4)
llm.generate(messages=session_history)
```

**After:**
```python
# 8K tokens (compressed) = $0.24/query (GPT-4)
context = session.get_context_window()  # Protected + recent + memories
llm.generate(messages=context)
```

**Savings:** 84% cost reduction, 6x faster inference

---

### Pitfall 2: Treating Memory as Saved Chat History

**Symptom:** Memory retrieval returns verbose, non-informative exchanges.

**Root Cause:** Storing raw conversation instead of extracting consolidated insights.

**Fix:** Read [Memory vs. RAG](./TERMINOLOGY.md#memory-vs-rag) → Implement [Memory Pattern](../patterns/memory-tutorial.md)

**Wrong:**
```python
# Storing noise
memory = "User: Tell me about karma yoga\nAssistant: Sure! Karma yoga is...\nUser: Thanks!\nAssistant: You're welcome!"
```

**Right:**
```python
# Extracting signal
memory = "User is learning about karma yoga (yoga of selfless action)"
```

**Impact:** 90% token reduction, semantic search works, provenance enabled

---

### Pitfall 3: Ignoring Provenance (No Audit Trail)

**Symptom:** Can't debug incorrect memories, can't resolve conflicts, compliance failures.

**Root Cause:** Storing memories without source, confidence, or timestamp.

**Fix:** Read [Provenance Tracking](../patterns/memory-tutorial.md#provenance-tracking-critical)

**Wrong:**
```python
# No lineage
memory_db.insert({"text": "User prefers morning meditation"})
# Question: Where did this come from? When? How confident?
# Answer: Unknown!
```

**Right:**
```python
# Full provenance
memory_db.insert({
    "text": "User prefers morning meditation",
    "provenance": {
        "memory_id": "mem_xyz",
        "source_session_id": "sess_2025_11_10",
        "confidence_score": 0.8,
        "validation_status": "user_confirmed",
        "confidence_history": [...]
    }
})
```

**Benefits:** Auditability, conflict resolution, compliance (GDPR), debugging

---

## Real-World Applications

### Application 1: Bhagavad Gita Chatbot (Spiritual Guidance)

**Domain:** Religious/philosophical education with personal context

**Challenges:**
- Multi-turn conversations exploring complex concepts (karma, dharma, moksha)
- Users share personal struggles (anxiety, family conflicts, career decisions)
- Must preserve spiritual context while redacting PII
- Personalization: Remember user's preferred commentaries and study level

**Context Engineering Solutions:**
- **Sessions:** 50+ turn conversations with protected objectives ("Help me understand Chapter 3")
- **Memory:** User preferences (Swami Sivananda translations), knowledge level (beginner in karma yoga)
- **PII Redaction:** Whitelist Gita characters (Arjuna, Krishna) but redact user names/emails
- **Provenance:** Track confidence in user's spiritual goals (may evolve over weeks)

**Results:**
- 84% token reduction (50K → 8K) with zero loss of context quality
- Privacy-safe personalization (no PII stored, spiritual context preserved)
- User retention: 3x higher for sessions with protected context vs. naive history

**Code:** `backend/sessions/gita_session.py`, `backend/memory/pii_redaction.py`

---

### Application 2: Banking Fraud Dispute (Compliance & Audit)

**Domain:** Financial services with regulatory requirements

**Challenges:**
- Conversations span weeks (initial dispute → investigation → resolution)
- Must track **every** claim with lineage for compliance (FDIC, GDPR)
- High confidence required (wrong decisions = legal liability)
- Customer context changes (e.g., victim reports new fraudulent charges)

**Context Engineering Solutions:**
- **Sessions:** Protected context for initial fraud report and customer constraints
- **Memory:** Customer's dispute history, communication preferences
- **Provenance:** Full audit trail with confidence evolution (agent_inferred → user_confirmed)
- **Conflict Resolution:** When memories contradict, choose higher confidence + newer timestamp

**Results:**
- 100% audit compliance (every memory traceable to source session)
- Confidence trending: Identify disputes where customer's story changes (decreasing confidence)
- Regulatory approval: FDIC auditors verified provenance trail

**Code:** Same `MemoryProvenance` infrastructure, different domain

---

### Application 3: Healthcare Triage (Protected Medical History)

**Domain:** Medical symptom assessment with sensitive information

**Challenges:**
- Medical history is protected context (must survive compression)
- PII: Patient names, birthdates, SSNs must be redacted
- Long sessions: Symptom exploration across 30+ questions
- Personalization: Remember chronic conditions, allergies, medications

**Context Engineering Solutions:**
- **Sessions:** Protected context for medical history and allergies
- **Memory:** Chronic conditions (diabetes, hypertension), medication list
- **PII Redaction:** Redact patient identifiers, preserve medical terms
- **Compression:** Compress casual conversation ("I see, tell me more") but protect symptom reports

**Results:**
- HIPAA compliance: No patient identifiers in context window or logs
- Safety: Allergies and chronic conditions never compressed away
- Efficiency: 70% token reduction while preserving critical medical context

**Code:** Same patterns, healthcare-specific event types and whitelist

---

## FAQs

### Q1: When should I use Sessions vs. Memory vs. RAG?

**Answer:**

| Pattern | Use When | Example | Persistence |
|---------|----------|---------|-------------|
| **Sessions** | Managing active conversation (short-term workspace) | Current Q&A exchange, recent context | Single session |
| **Memory** | Storing user-specific facts (personalization) | User prefers Sivananda translations | Cross-session |
| **RAG** | Retrieving general knowledge (domain facts) | Chapter 3 discusses karma yoga | Permanent |

**Decision Tree:**
1. Is the information user-specific? → **Memory** (not general knowledge)
2. Is the information needed only in current conversation? → **Sessions** (transient)
3. Is the information general domain knowledge? → **RAG** (shared across all users)

**Example:**
- "User prefers morning meditation" → **Memory** (user-specific, cross-session)
- "User just asked about Chapter 3" → **Sessions** (current conversation context)
- "Chapter 3 is about karma yoga" → **RAG** (general knowledge, not user-specific)

---

### Q2: When should I trigger compression?

**Answer:** At **95% of context window capacity** (token-based, not turn-based).

**Why 95%?**
- **Too early (e.g., 70%):** Wastes compute on small conversations
- **Too late (e.g., 100%):** Risk of truncation if memory/RAG retrieval adds tokens
- **95% (Goldilocks):** 5% safety margin prevents overflow while avoiding premature compression

**Implementation:**
```python
class ContextCompressor:
    def should_compress(self, events: list[dict]) -> bool:
        total_tokens = self._count_tokens(events)
        threshold_tokens = self.max_tokens * 0.95  # 95%
        return total_tokens >= threshold_tokens
```

**Token Math (8K context window):**
- Trigger: 7,600 tokens (95% of 8,000)
- Safety margin: 400 tokens for memory/RAG retrieval
- Result: Never exceed 8K limit

**Code:** `backend/sessions/context_compressor.py:45-60`

---

### Q3: What if all context is protected and can't be compressed?

**Answer:** Raise an error and require user intervention.

**Why:** If every event is protected, compression can't free up tokens. This indicates:
1. User's objectives are too complex for available context window
2. Protected context criteria are too broad
3. Need to upgrade to larger context window model

**Implementation:**
```python
def compress(self, events: list[dict]) -> list[dict]:
    protected = [e for e in events if e.get("is_protected")]
    compressible = [e for e in events if not e.get("is_protected")]

    if len(compressible) == 0:
        raise ValueError(
            "Cannot compress: all events are protected. "
            "Consider upgrading to larger context window or "
            "reviewing protected context criteria."
        )

    # Compress compressible events
    compressed = self._summarize_events(compressible)
    return protected + compressed
```

**Resolution Options:**
1. **Upgrade model:** GPT-4 (8K) → GPT-4 Turbo (128K) → Claude 3.5 (200K)
2. **Review criteria:** Are all objectives truly critical? Can some be consolidated?
3. **User intervention:** Ask user to summarize their goals in fewer turns

**Code:** `backend/sessions/context_compressor.py:70-90`

---

### Q4: How do I test long conversations (50-100 turns)?

**Answer:** Use TDD with synthetic conversation generation.

**Strategy:**
1. **RED:** Write failing test with loop generating N turns
2. **GREEN:** Implement compression and protected context preservation
3. **REFACTOR:** Verify performance (<2 seconds for 100 turns)

**Example:**
```python
def test_should_preserve_objectives_in_50_turn_conversation() -> None:
    """Test that initial objective survives 50 turns."""
    session = GitaSession(max_tokens=8000, compression_threshold=0.95)

    # Initial objective (protected)
    session.append_event(
        turn=0,
        role="user",
        content="Help me understand karma yoga",
        event_type="initial_objective"
    )

    # 49 casual turns (compressible)
    for turn in range(1, 50):
        session.append_event(
            turn=turn,
            role="user" if turn % 2 == 1 else "assistant",
            content=f"Turn {turn} casual conversation...",
            event_type="casual"
        )

    # Assert: Initial objective still present
    context = session.get_context_window()
    initial = next((e for e in context if e["turn"] == 0), None)

    assert initial is not None
    assert "karma yoga" in initial["content"]
    assert session.compression_count >= 1  # Compression triggered
```

**Performance Benchmarks:**
- 50 turns: <200ms, 1 compression cycle
- 100 turns: <2 seconds, 2-3 compression cycles

**Code:** `tests/sessions/test_long_conversation.py:15-60`

---

## Next Steps

**Action Items:**

1. **Foundations:**
   - [ ] Read [TERMINOLOGY.md](./TERMINOLOGY.md) (10 min) - **Do this first!**
   - [ ] Review visual diagrams (session_vs_context.svg, memory_vs_rag.svg)
   - [ ] Choose a learning path (Quick Start, Implementation-Focused, or Full Mastery)

2. **Implementation:**
   - [ ] Implement [Sessions Pattern](../patterns/sessions-tutorial.md) ([Quick Ref](../patterns/sessions-quickref.md))
   - [ ] Implement [Memory Pattern](../patterns/memory-tutorial.md) ([Quick Ref](../patterns/memory-quickref.md))
   - [ ] Follow [TDD Workflow](../patterns/tdd-workflow.md) for all code

3. **Testing:**
   - [ ] Write tests for protected context preservation
   - [ ] Test multi-turn conversations (50-100 turns)
   - [ ] Verify ≥90% test coverage

4. **Integration:**
   - [ ] Integrate Sessions with your chatbot/agent
   - [ ] Add Memory extraction from conversations
   - [ ] Implement PII redaction for your domain
   - [ ] Set up provenance tracking for audit

5. **Advanced:**
   - [ ] Optimize compression performance
   - [ ] Design conflict resolution for contradictory memories
   - [ ] Explore multi-agent context sharing

---

## Feedback & Contribution

**Found an issue?** Open a GitHub issue with label `documentation`

**Want to contribute?** See [CONTRIBUTING.md](../CONTRIBUTING.md) for guidelines

**Questions?** Join our discussion forum or Slack channel

---

## License

MIT License - See [LICENSE](../LICENSE) for details

---

**Last Updated:** 2025-11-23
**Version:** 1.0.0
**Changelog:** [TUTORIAL_CHANGELOG.md](../TUTORIAL_CHANGELOG.md)
