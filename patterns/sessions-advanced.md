# Sessions Pattern - Advanced Guide

**Pattern:** Context Management
**Audience:** Senior engineers optimizing for production
**Reading Time:** 10-12 minutes

---

## Common Pitfalls

### ❌ Pitfall 1: Sending Entire Session History to LLM

```python
# BAD: Sending entire conversation history
def query_llm(conversation_history: list[dict]) -> str:
    messages = conversation_history  # Could be 50K+ tokens!
    response = llm.generate(messages=messages)
    return response
```

**Why it's bad:**
- Token waste: Sending verbose acknowledgments like "Sure, I'll help with that"
- Cost explosion: API costs scale with tokens (GPT-4: $0.03/1K tokens)
- Context truncation: LLM silently drops oldest messages when limit exceeded
- Objective loss: Initial user goals get truncated away

**✅ Correct Pattern: Compress and Curate**

```python
# GOOD: Use GitaSession to compress
def query_llm(session: GitaSession) -> str:
    context_window = session.get_context_window()  # 8K tokens, protected context preserved
    response = llm.generate(messages=context_window)
    return response
```

**Benefits:**
- 6x reduction: 50K tokens → 8K tokens
- Protected context preserved: Initial objectives never lost
- Cost savings: $1.50 → $0.24 per query (GPT-4)
- Scalability: Support 100+ turn conversations

---

### ❌ Pitfall 2: Not Marking Critical Context as Protected

```python
# BAD: Treating all events equally
def append_event(event: dict) -> None:
    events.append(event)  # No protection marking

    # During compression, important constraints get removed!
    if should_compress(events):
        events = events[-10:]  # Keep only last 10 - LOSES OBJECTIVES!
```

**Why it's bad:**
- Initial objectives get compressed away
- User constraints ignored in later turns
- Authentication state lost
- Inconsistent responses (LLM forgets user's preferences)

**✅ Correct Pattern: Identify Protected Context**

```python
# GOOD: Mark protected context before compression
def append_event(event: dict) -> None:
    # Step 1: Identify if protected
    protection_result = identify_protected_context(event)
    event["is_protected"] = protection_result["is_protected"]

    # Step 2: Append to events
    events.append(event)

    # Step 3: Compress (protected events survive)
    if should_compress(events):
        events = compressor.compress(events)  # Protected events pinned
```

**Protection Criteria:**
- Turn 0 (initial objectives)
- `event_type == "constraint"`
- `event_type == "auth_checkpoint"`
- Goal statements

---

### ❌ Pitfall 3: Ignoring Compression Trigger Threshold

```python
# BAD: Compressing too early or too late
def append_event(event: dict) -> None:
    events.append(event)

    # Compress every 10 turns (arbitrary, may compress too early)
    if len(events) % 10 == 0:
        events = compress(events)
```

**Why it's bad:**
- Too early compression: Wastes compute on small conversations
- Too late compression: Risk exceeding context limit and triggering truncation
- No token awareness: Number of events ≠ number of tokens

**✅ Correct Pattern: Token-Based 95% Threshold**

```python
# GOOD: Compress at 95% of token capacity
class ContextCompressor:
    def should_compress(self, events: list[dict]) -> bool:
        """Check if compression needed.

        Returns:
            True if token count >= 95% of max_tokens
        """
        total_tokens = self._count_tokens(events)
        threshold_tokens = self.max_tokens * self.trigger_threshold
        return total_tokens >= threshold_tokens

# Usage
compressor = ContextCompressor(max_tokens=8000, trigger_threshold=0.95)
if compressor.should_compress(events):
    events = compressor.compress(events)  # Triggers at 7600 tokens
```

**Benefits:**
- Safety margin: 5% buffer prevents context overflow
- Token-aware: Counts actual tokens, not just event count
- Configurable: Adjust threshold per use case (e.g., 0.90 for more safety)

---

## Performance Optimization

**Benchmarks from Testing:**
- 50-turn conversation: 1 compression cycle, <200ms processing time
- 100-turn conversation: 2-3 compression cycles, <2 seconds total
- Token reduction: 50K → 8K tokens (6x reduction)
- Cost savings: 84% reduction in API costs (GPT-4)

**Optimization Tips:**

### 1. Batch Token Counting

```python
# BAD: Count tokens per event
def append_event(event: dict) -> None:
    events.append(event)
    total = sum(count_tokens(e["content"]) for e in events)  # Recounts all events!
    if total > threshold: compress()

# GOOD: Count once during compression check
def append_event(event: dict) -> None:
    events.append(event)
    if compressor.should_compress(events):  # Counts once internally
        compress()
```

### 2. Lazy Compression

```python
# BAD: Compress on every event
def append_event(event: dict) -> None:
    events.append(event)
    compress()  # Wasteful!

# GOOD: Compress only when threshold reached
def append_event(event: dict) -> None:
    events.append(event)
    if compressor.should_compress(events):  # Only at 95%
        compress()
```

### 3. Protected Event Indexing

```python
# BAD: Linear search for protected events
def get_protected_events() -> list[dict]:
    return [e for e in events if e.get("is_protected")]  # O(n) every time

# GOOD: Cache protected event indices
class GitaSession:
    def __init__(self):
        self.events = []
        self._protected_indices = set()  # O(1) lookup

    def append_event(self, event: dict) -> None:
        idx = len(self.events)
        if event["is_protected"]:
            self._protected_indices.add(idx)
        self.events.append(event)
```

### 4. Async Compression (Large Sessions)

```python
# For very large sessions (200+ turns)
import asyncio

class GitaSession:
    async def append_event_async(self, event: dict) -> None:
        self.events.append(event)
        if self.compressor.should_compress(self.events):
            # Run compression in background
            asyncio.create_task(self._compress_events_async())

    async def _compress_events_async(self) -> None:
        compressed = await asyncio.to_thread(self.compressor.compress, self.events)
        self.events = compressed
        self.compression_count += 1
```

---

## Production Considerations

### 1. Security: Session Isolation

```python
# Ensure sessions don't leak between users
class SessionManager:
    def __init__(self):
        self._sessions: dict[str, GitaSession] = {}

    def get_session(self, user_id: str) -> GitaSession:
        if user_id not in self._sessions:
            self._sessions[user_id] = GitaSession()
        return self._sessions[user_id]

    def delete_session(self, user_id: str) -> None:
        """Cleanup session when user logs out."""
        if user_id in self._sessions:
            del self._sessions[user_id]
```

### 2. Lifecycle: Session Expiration

```python
from datetime import datetime, timedelta

class GitaSession:
    def __init__(self, ttl_hours: int = 24):
        self.events = []
        self.created_at = datetime.now()
        self.ttl = timedelta(hours=ttl_hours)

    def is_expired(self) -> bool:
        return datetime.now() > self.created_at + self.ttl

# SessionManager checks expiration
class SessionManager:
    def get_session(self, user_id: str) -> GitaSession:
        if user_id in self._sessions:
            session = self._sessions[user_id]
            if session.is_expired():
                del self._sessions[user_id]
                return GitaSession()
            return session
        return GitaSession()
```

### 3. Scale: Distributed Sessions

```python
# For multi-server deployments, store sessions in Redis
import redis
import json

class RedisSessionStore:
    def __init__(self):
        self.redis = redis.Redis()

    def save_session(self, user_id: str, session: GitaSession) -> None:
        data = {
            "events": session.events,
            "state": session.session_state,
            "compression_count": session.compression_count,
        }
        self.redis.setex(f"session:{user_id}", 86400, json.dumps(data))

    def load_session(self, user_id: str) -> GitaSession | None:
        data = self.redis.get(f"session:{user_id}")
        if not data:
            return None

        parsed = json.loads(data)
        session = GitaSession()
        session.events = parsed["events"]
        session.session_state = parsed["state"]
        session.compression_count = parsed["compression_count"]
        return session
```

---

## Multi-Agent Session Architectures

### Pattern 1: Shared Session (All Agents See Same Context)

```python
class MultiAgentSession:
    def __init__(self):
        self.shared_session = GitaSession()

    def agent_query(self, agent_name: str, query: str) -> str:
        # All agents share same context window
        context = self.shared_session.get_context_window()
        response = self.agents[agent_name].process(context, query)

        # Append agent response to shared session
        self.shared_session.append_event(
            turn=len(self.shared_session.events),
            role=agent_name,
            content=response,
            event_type="agent_response"
        )
        return response
```

**Use case:** Collaborative agents building on each other's work (e.g., retrieval → synthesis → validation)

### Pattern 2: Isolated Sessions (Agent-Specific Context)

```python
class MultiAgentSession:
    def __init__(self):
        self.sessions: dict[str, GitaSession] = {
            "retrieval": GitaSession(),
            "synthesis": GitaSession(),
            "validator": GitaSession(),
        }

    def agent_query(self, agent_name: str, query: str) -> str:
        # Each agent has isolated context
        agent_session = self.sessions[agent_name]
        context = agent_session.get_context_window()
        response = self.agents[agent_name].process(context, query)

        agent_session.append_event(
            turn=len(agent_session.events),
            role=agent_name,
            content=response,
            event_type="agent_response"
        )
        return response
```

**Use case:** Independent agents with specialized tasks (e.g., fraud detection + customer service)

---

## Advanced Protection Rules

### Custom Protection Logic

```python
def identify_protected_context(event: dict[str, Any]) -> dict[str, Any]:
    """Extended protection rules for domain-specific needs."""

    # Base rules (turn 0, constraints, auth)
    if event["turn"] == 0:
        return {"is_protected": True, "reason": "initial_objective"}

    if event["event_type"] == "constraint":
        return {"is_protected": True, "reason": "explicit_constraint"}

    # Domain-specific: Bhagavad Gita verse references
    content = event["content"].lower()
    if any(keyword in content for keyword in ["chapter", "verse", "bhagavad gita"]):
        return {"is_protected": True, "reason": "scripture_reference"}

    # Domain-specific: Banking compliance
    if event["event_type"] == "fraud_alert":
        return {"is_protected": True, "reason": "compliance"}

    # Domain-specific: Medical history
    if event.get("metadata", {}).get("contains_phi"):
        return {"is_protected": True, "reason": "protected_health_info"}

    return {"is_protected": False, "reason": "compressible"}
```

---

## Monitoring & Observability

### Key Metrics to Track

```python
class GitaSession:
    def get_metrics(self) -> dict[str, Any]:
        """Export session metrics for monitoring."""
        total_tokens = sum(count_tokens(e["content"]) for e in self.events)
        protected_count = sum(1 for e in self.events if e["is_protected"])

        return {
            "total_events": len(self.events),
            "total_tokens": total_tokens,
            "protected_events": protected_count,
            "compression_count": self.compression_count,
            "compression_ratio": 1 - (len(self.events) / max(1, self.compression_count * 50)),
            "avg_tokens_per_event": total_tokens / max(1, len(self.events)),
        }

# Usage with logging
import logging

logger = logging.getLogger(__name__)

session = GitaSession()
# ... conversation happens ...
metrics = session.get_metrics()
logger.info(f"Session metrics: {metrics}")
```

**Monitor for:**
- `compression_count` - Frequent compression = verbose conversations
- `compression_ratio` - Low ratio = ineffective compression
- `protected_events` / `total_events` - High ratio = most content protected (may need rule tuning)

---

## Related Patterns

- [Memory Pattern - Tutorial](./memory-tutorial.md) - Long-term persistence across sessions
- [TDD Workflow](./tdd-workflow.md) - Testing methodology
- [Quick Reference](./sessions-quickref.md) - Code templates
- [Tutorial](./sessions-tutorial.md) - Full explanation

---

## Further Reading

- Google DeepMind, "Gemini 1.5 Context Engineering" (2024)
- Anthropic, "Long Context Windows" (2024)
- [TERMINOLOGY.md](../google-context/TERMINOLOGY.md) - Critical distinctions
- [Pattern Library](./README.md) - All patterns
