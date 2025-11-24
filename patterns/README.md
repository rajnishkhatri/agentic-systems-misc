# Pattern Library

**Purpose:** Reusable code patterns for building robust, maintainable AI evaluation systems

**Target Audience:** Junior developers and AI assistants (Claude Code)

**Last Updated:** 2025-11-12

---

## Overview

This pattern library documents proven code patterns discovered in Lessons 9-13 of the LLM Evaluation Tutorial System. Each pattern includes:

- **When to use** (and when NOT to use)
- **Copy-paste code templates** with defensive coding
- **Real examples** from the codebase with file:line references
- **Common pitfalls** and how to avoid them
- **Integration** with defensive coding principles

**Philosophy:** "Stop thinking in terms of files and functions. Start thinking about patterns and reusable solutions."

---

## Quick Reference Table

| Pattern | Complexity | Primary Use Case | Quick Ref | Tutorial | Advanced |
|---------|-----------|------------------|-----------|----------|----------|
| [TDD Workflow](#tdd-workflow) | ⭐⭐ (Medium) | Testing & development methodology | [tdd-workflow.md](tdd-workflow.md) | - | - |
| [ThreadPoolExecutor Parallel](#threadpoolexecutor-parallel) | ⭐⭐⭐ (High) | Concurrent batch processing (I/O-bound) | [threadpool-parallel.md](threadpool-parallel.md) | - | - |
| [Abstract Base Class](#abstract-base-class) | ⭐⭐⭐ (High) | OOP interface enforcement & polymorphism | [abstract-base-class.md](abstract-base-class.md) | - | - |
| [Sessions](#context-engineering-sessions) | ⭐⭐⭐ (Advanced) | Multi-turn conversations with compression | [sessions-quickref.md](sessions-quickref.md) | [sessions-tutorial.md](sessions-tutorial.md) | [sessions-advanced.md](sessions-advanced.md) |
| [Memory](#context-engineering-memory) | ⭐⭐⭐⭐ (Expert) | Long-term persistence with provenance | [memory-quickref.md](memory-quickref.md) | [memory-tutorial.md](memory-tutorial.md) | [memory-advanced.md](memory-advanced.md) |

**Complexity Legend:**
- ⭐ (Low): Can be understood and applied in <15 minutes
- ⭐⭐ (Medium): Requires 15-30 minutes to understand, practice needed
- ⭐⭐⭐ (High): Requires 30-60 minutes to understand, significant practice needed
- ⭐⭐⭐⭐ (Expert): Requires 60+ minutes, production experience recommended

**Progressive Disclosure Navigation:**
- **Quick Ref** - Code templates only (2 min lookup)
- **Tutorial** - Full explanation with examples (12-15 min read)
- **Advanced** - Pitfalls, performance, production tips (10-12 min read)

---

## Pattern Catalog

### TDD Workflow

**Pattern Type:** Development Methodology
**Complexity:** ⭐⭐ (Medium)
**Source:** Lesson 13 - RAG Generation & Attribution

**What it is:** Test-Driven Development (TDD) methodology where you write tests *before* implementation code. Follow the RED → GREEN → REFACTOR cycle.

**When to use:**
- Building new features from scratch
- Refactoring existing code
- Fixing bugs (write failing test first, then fix)
- Working with critical business logic

**When NOT to use:**
- Exploratory prototyping or proof-of-concepts
- UI/UX design with highly fluid requirements
- Spiking on unfamiliar libraries

**Key concepts:**
- **RED**: Write ONE failing test
- **GREEN**: Write minimal code to make test pass
- **REFACTOR**: Improve code quality while keeping tests green
- **Test naming convention**: `test_should_[result]_when_[condition]()`

**Quick example:**
```python
# RED: Write failing test
def test_should_extract_claims_when_response_has_multiple_statements() -> None:
    detector = AttributionDetector()
    response = "The Gita teaches dharma. It was spoken by Krishna."
    claims = detector.extract_claims(response)
    assert len(claims) >= 2

# GREEN: Minimal implementation
class AttributionDetector:
    def extract_claims(self, response: str) -> list[str]:
        if not response:
            return []
        return response.split(". ")

# REFACTOR: Add defensive coding
class AttributionDetector:
    def extract_claims(self, response: str) -> list[str]:
        if not isinstance(response, str):
            raise TypeError("response must be a string")
        if not response.strip():
            return []
        import re
        return [c.strip() for c in re.split(r'[.!?]+', response) if c.strip()]
```

**[→ Full documentation](tdd-workflow.md)**

---

### ThreadPoolExecutor Parallel

**Pattern Type:** Concurrency
**Complexity:** ⭐⭐⭐ (High)
**Source:** Lesson 12 - Hybrid Retrieval & Context Quality

**What it is:** Python's built-in pattern for executing multiple I/O-bound tasks in parallel using threads, with order preservation and progress tracking.

**When to use:**
- Batch processing (API calls, file I/O, database queries)
- I/O-bound tasks that spend time waiting on external resources
- Need to preserve result order matching input order
- Users need real-time progress feedback

**When NOT to use:**
- CPU-bound tasks (use `ProcessPoolExecutor` instead)
- Shared state modifications (risk of race conditions)
- Sequential dependencies (Task N depends on Task N-1)
- Memory constraints (each thread consumes memory)

**Key concepts:**
- **`future_to_index` mapping**: Preserve result order
- **Exception handling**: Catch failures without crashing batch
- **Progress tracking**: Integrate `tqdm` with `as_completed()`
- **`max_workers` tuning**: 5-20 for I/O tasks, consider API rate limits

**Quick example:**
```python
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm

queries = ["q1", "q2", "q3"]
results = [None] * len(queries)

with ThreadPoolExecutor(max_workers=5) as executor:
    # Submit with index mapping
    future_to_index = {
        executor.submit(process_query, query): i
        for i, query in enumerate(queries)
    }

    # Collect with progress bar
    for future in tqdm(as_completed(future_to_index), total=len(queries)):
        index = future_to_index[future]
        try:
            results[index] = future.result()
        except Exception as e:
            print(f"Error processing query {index}: {e}")
            results[index] = None  # Fallback
```

**Real-world performance:**
- Sequential: ~300s for 100 API calls
- Parallel (max_workers=10): ~30s (10× speedup)

**[→ Full documentation](threadpool-parallel.md)**

---

### Abstract Base Class

**Pattern Type:** Object-Oriented Programming (OOP)
**Complexity:** ⭐⭐⭐ (High)
**Source:** Lesson 10 - AI-as-Judge Mastery & Production Patterns

**What it is:** Design pattern for enforcing interface contracts in OOP. Define common interface that all subclasses must implement, preventing instantiation of incomplete implementations.

**When to use:**
- Multiple implementations sharing a common interface
- Building frameworks or plugin systems
- Need polymorphic behavior (code works with base class type)
- Shared functionality across implementations (retry logic, validation)

**When NOT to use:**
- Single implementation (YAGNI principle)
- Simple inheritance is sufficient
- Functional code (use protocols/interfaces instead)
- Premature abstraction without clear need

**Key concepts:**
- **`ABC` inheritance**: Base class for abstract classes
- **`@abstractmethod` decorator**: Mark methods that must be implemented
- **Defensive initialization**: Validate inputs in base class `__init__`
- **`super().__init__()` call**: Subclasses MUST call parent initializer

**Quick example:**
```python
from abc import ABC, abstractmethod

class BaseJudge(ABC):
    """Abstract base class for all judge implementations."""

    def __init__(self, model: str, temperature: float = 0.0):
        # Defensive validation
        if not isinstance(model, str):
            raise TypeError("model must be a string")
        if not (0.0 <= temperature <= 2.0):
            raise ValueError("temperature must be between 0.0 and 2.0")

        self.model = model
        self.temperature = temperature

    @abstractmethod
    def evaluate(self, query: str, response: str) -> dict:
        """Subclasses must implement."""
        pass

    def _call_llm(self, prompt: str) -> str:
        """Shared helper method."""
        # Retry logic, API calls, etc.
        pass


class DietaryAdherenceJudge(BaseJudge):
    """Concrete implementation."""

    def __init__(self, model: str, temperature: float = 0.0):
        super().__init__(model, temperature)  # CRITICAL: Call parent
        self.prompt_template = self._load_template("dietary.txt")

    def evaluate(self, query: str, response: str) -> dict:
        """Implement required method."""
        prompt = self.prompt_template.format(query=query, response=response)
        raw = self._call_llm(prompt)  # Use shared helper
        return {"score": 1.0, "reasoning": raw}
```

**[→ Full documentation](abstract-base-class.md)**

---

### Context Engineering: Sessions

**Pattern Type:** Context Management
**Complexity:** ⭐⭐⭐ (Advanced)
**Source:** Context Engineering Critical Success Factors

**What it is:** Short-term workspace for managing multi-turn conversations with automatic context compression. Intelligently curates what gets included in the Context Window (8K tokens) from Session History (50K+ tokens).

**When to use:**
- Building multi-turn conversational AI (chatbots, assistants)
- Working with LLMs that have limited context windows
- Managing conversations that span 20+ turns
- Needing to preserve critical information (objectives, constraints) across long sessions
- Wanting to reduce API costs by sending only essential context

**When NOT to use:**
- Building single-turn Q&A systems
- Working with massive context windows (200K+) where compression isn't needed
- Prototyping where you want quick iterations
- All information must be retained verbatim (use Memory with provenance instead)

**Key concepts:**
- **Session History vs. Context Window**: Full log (50K tokens) vs. curated subset (8K tokens)
- **Protected Context**: Events that must survive compression (turn 0, constraints, auth)
- **Compression Trigger**: Activates at 95% of token capacity
- **Token Efficiency**: 6x reduction (50K → 8K) while preserving intelligence

**Quick example:**
```python
from backend.sessions import GitaSession

# Initialize session with 8K context window
session = GitaSession(max_tokens=8000, compression_threshold=0.95)

# Add initial objective (protected, will never be compressed)
session.append_event(
    turn=0,
    role="user",
    content="Help me understand karma yoga from Chapter 3",
    event_type="initial_objective"
)

# Add 49 more turns (triggers automatic compression at turn ~40)
for turn in range(1, 50):
    session.append_event(
        turn=turn,
        role="user" if turn % 2 == 1 else "assistant",
        content=f"Turn {turn} conversation...",
        event_type="casual"
    )

# Get compressed context window (initial objective preserved)
context = session.get_context_window()  # 8K tokens, protected events intact
```

**Real-world performance:**
- 50 turns: 1 compression cycle, <200ms
- 100 turns: 2-3 compression cycles, <2 seconds
- Token reduction: 84% (50K → 8K)
- Cost savings: $1.50 → $0.24 per query (GPT-4)

**Documentation:**
- [Quick Reference](sessions-quickref.md) - Code templates (2 min)
- [Tutorial](sessions-tutorial.md) - Full guide (12-15 min)
- [Advanced](sessions-advanced.md) - Production tips (10-12 min)

---

### Context Engineering: Memory

**Pattern Type:** Context Management
**Complexity:** ⭐⭐⭐⭐ (Expert)
**Source:** Context Engineering Critical Success Factors

**What it is:** Long-term persistence of user-specific facts with provenance tracking, confidence evolution, and PII redaction. Memory is consolidated insights, not saved chat.

**When to use:**
- Building multi-session applications (user returns days/weeks later)
- Personalizing AI responses based on user preferences
- Tracking user knowledge evolution (beginner → expert)
- Implementing spiritual/sensitive chatbots where personal context matters
- Needing to audit memory extraction for trustworthiness and compliance

**When NOT to use:**
- Building single-session Q&A
- Storing general knowledge facts (use RAG instead)
- Needing verbatim conversation logs (use Session Events Log)
- Prototyping without production-grade provenance

**Key concepts:**
- **Memory vs. RAG**: User-specific (personal assistant) vs. general knowledge (research librarian)
- **Provenance Tracking**: Source session, confidence score, validation status, evolution history
- **Confidence Evolution**: Boost user_confirmed (+0.1), penalty disputed (-0.2)
- **PII Redaction**: Protect privacy while preserving spiritual/emotional context
- **Whitelist**: Preserve Bhagavad Gita characters (Arjuna, Krishna) from redaction

**Quick example:**
```python
from backend.memory import MemoryProvenance, PIIRedactor, extract_memory_with_pii_redaction
from datetime import datetime

# Extract memory with PII redaction
user_message = "I'm John Smith at john@email.com. I'm anxious about job interview. Can Krishna help?"

redacted_text, provenance = extract_memory_with_pii_redaction(
    text="User experiencing anxiety about upcoming job interview",
    source_session_id="sess_2025_11_15",
    confidence_score=0.85,
    validation_status="agent_inferred"
)

# Track confidence evolution
provenance.add_confidence_update(0.9, "User confirmed preference")
provenance.validation_status = "user_confirmed"

# Export audit log
audit = provenance.to_audit_log()
# {
#     "memory_id": "mem_xyz",
#     "confidence_score": 0.9,
#     "effective_confidence": 1.0,  # 0.9 + 0.1 boost
#     "confidence_trend": "increasing",
#     "validation_status": "user_confirmed"
# }
```

**Critical Success Factors:**
1. **Provenance Tracking**: Every memory traceable to source session
2. **Confidence Evolution**: Track validation status changes over time
3. **PII Redaction**: Privacy-safe personalization with domain whitelist

**Documentation:**
- [Quick Reference](memory-quickref.md) - Code templates (2 min)
- [Tutorial](memory-tutorial.md) - Full guide (15-18 min)
- [Advanced](memory-advanced.md) - Conflict resolution, production (12-15 min)

---

## How to Use This Library

### For Developers

1. **Identify your problem domain:**
   - Need to write tests? → [TDD Workflow](tdd-workflow.md)
   - Need to parallelize I/O tasks? → [ThreadPoolExecutor Parallel](threadpool-parallel.md)
   - Need multiple implementations of same interface? → [Abstract Base Class](abstract-base-class.md)
   - Need to manage multi-turn conversations? → [Sessions Quick Ref](sessions-quickref.md) or [Tutorial](sessions-tutorial.md)
   - Need to persist user-specific facts across sessions? → [Memory Quick Ref](memory-quickref.md) or [Tutorial](memory-tutorial.md)

2. **Read the pattern documentation:**
   - Understand "When to use" and "When NOT to use"
   - Study the code template
   - Review real examples from codebase

3. **Copy-paste the template:**
   - All templates include defensive coding (type hints, validation, error handling)
   - Customize for your specific use case
   - Run tests to verify (use TDD pattern!)

4. **Avoid common pitfalls:**
   - Each pattern documents mistakes to avoid
   - Learn from real project experience

### For AI Assistants (Claude Code)

**When generating code, follow this priority:**

1. **Check if a pattern applies:**
   - Writing tests? → Use TDD Workflow pattern
   - Batch processing? → Use ThreadPoolExecutor pattern
   - Multiple implementations? → Use Abstract Base Class pattern

2. **Apply pattern templates:**
   - Use exact template structure from pattern docs
   - Include all defensive coding elements (type hints, validation, error handling)
   - Reference pattern in code comments: `# Pattern: TDD Workflow (patterns/tdd-workflow.md)`

3. **Integrate with defensive coding:**
   - All functions follow 5-step defensive template (see `CLAUDE.md`)
   - Type hints on ALL functions
   - Input validation with guard clauses
   - Specific exception types with descriptive messages

4. **Cross-reference patterns:**
   - TDD tests for ThreadPoolExecutor code
   - Abstract Base Classes tested with TDD
   - Defensive coding in all patterns

**Example prompt for Claude Code:**

> "Implement batch query processing using ThreadPoolExecutor pattern from `patterns/threadpool-parallel.md`. Include future_to_index mapping, tqdm progress bar, exception handling with fallbacks, and defensive validation. Test with TDD pattern from `patterns/tdd-workflow.md`."

---

## Integration with Project Standards

This pattern library complements project guidelines in `CLAUDE.md`:

### 1. Defensive Function Template (5-Step Pattern)

All code follows this structure:

```python
def function_name(arg: Type, optional: Type = default) -> ReturnType:
    """Brief description.

    Args:
        arg: Description
        optional: Description

    Returns:
        Description

    Raises:
        TypeError: When type validation fails
        ValueError: When value validation fails
    """
    # Step 1: Type checking
    if not isinstance(arg, ExpectedType):
        raise TypeError("arg must be ExpectedType")

    # Step 2: Input validation
    if arg < 0:
        raise ValueError("arg must be non-negative")

    # Step 3: Edge case handling
    if len(arg) == 0:
        return default_value

    # Step 4: Main logic
    result = process(arg)

    # Step 5: Return
    return result
```

**Pattern integration:**
- TDD Workflow: Write tests for each step
- ThreadPoolExecutor: Apply template to batch processing functions
- Abstract Base Class: Apply template to `__init__` and abstract methods

### 2. Test Naming Convention

**Pattern:** `test_should_[expected_result]_when_[condition]()`

**Examples:**
```python
def test_should_extract_claims_when_response_has_multiple_statements() -> None:
def test_should_return_empty_list_when_response_is_empty() -> None:
def test_should_raise_error_for_invalid_state_type() -> None:
```

**See:** [TDD Workflow - Test Naming Convention](tdd-workflow.md#test-naming-convention)

### 3. Quality Standards

- **Line length:** 120 characters (Ruff)
- **Type hints:** Required for all functions
- **Test coverage:** Aim for 90%+
- **Documentation:** Docstrings with Args/Returns/Raises
- **Error handling:** Specific exceptions (TypeError, ValueError), never bare `except:`

---

## Contributing New Patterns

**To add a new pattern to this library:**

### 1. Identify a Reusable Pattern

**Criteria:**
- Used in 2+ lessons or tutorials
- Solves a common problem
- Has clear "when to use" guidelines
- Includes defensive coding best practices

### 2. Use the Pattern Template Structure

All pattern documents must include:

```markdown
# Pattern Name

**Pattern Type:** [Development Methodology | Concurrency | OOP | Data Structure]
**Complexity:** [⭐/⭐⭐/⭐⭐⭐]
**Source:** [Lesson Number - Lesson Name]
**Created:** [YYYY-MM-DD]
**File References:** `file/path.py:start-end`

---

## Overview
[2-3 paragraphs explaining pattern value proposition and benefits]

## When to Use
✅ Use when: [3-5 specific scenarios]
❌ DON'T use when: [3-5 anti-patterns]

## Core Concepts
[2-4 key concepts with code examples]

## Code Template
[Copy-paste ready template with defensive coding]

## Real Example from Codebase
[Actual code from project with file:line references]

## Integration with Defensive Coding
[How pattern applies defensive principles]

## Common Pitfalls
[❌ Bad examples with explanations]
[✅ Fixes for each pitfall]

## Summary Checklist
- [ ] Checklist items for implementation

## Related Patterns
[Links to other patterns that complement this one]

## Further Reading
[External resources and project file references]
```

### 3. Code Quality Requirements

- All code examples must be **executable** (copy-paste ready)
- Include **type hints** and **defensive coding**
- Show both **correct usage** and **common mistakes**
- Reference **actual files with line numbers**: `file.py:123-145`

### 4. Add to Quick Reference Table

Update the table in this README with:
- Pattern name (linked)
- Complexity rating (⭐-⭐⭐⭐)
- Primary use case (1 sentence)
- Source file reference

### 5. Submit for Review

- Create pattern markdown file in `/patterns/` directory
- Update this README.md
- Update `CLAUDE.md` with pattern reference if needed
- Run tests to ensure examples work
- Commit with message: `docs: add [PatternName] pattern to library`

---

## Pattern Discovery Process

**How we identified these patterns:**

1. **Code review:** Analyzed Lessons 9-13 implementations
2. **Repetition detection:** Found code structures used 3+ times
3. **Abstraction:** Extracted common elements into reusable templates
4. **Documentation:** Added defensive coding, pitfalls, and usage guidelines
5. **Validation:** Tested templates against real project requirements

**Recent patterns added:**
- Context Engineering: Sessions (2025-11-23) - Multi-turn conversation management
- Context Engineering: Memory (2025-11-23) - Long-term persistence with provenance

**Future patterns under consideration:**
- Defensive Function Template (from `CLAUDE.md`)
- Jupyter Notebook Structure (from lesson tutorials)
- LLM Prompt Template Pattern (from judge implementations)
- Metrics Visualization Dashboard (from lesson-9-11)
- File-based Configuration Pattern (from judge prompts)

---

## Success Metrics

**Pattern library effectiveness is measured by:**

1. **Development speed:** 50% faster tutorial development (Target: Lessons 14-15)
2. **Code consistency:** All new code follows documented patterns
3. **Onboarding time:** Junior developers productive in <1 week
4. **AI assistant accuracy:** Claude Code generates correct pattern implementations 90%+ of time
5. **Bug reduction:** Defensive patterns catch errors before production

---

## Related Documentation

- **Project Guidelines:** `/CLAUDE.md` - Project philosophy, TDD mode, defensive coding
- **Tutorial System:** `*/TUTORIAL_INDEX.md` - Learning paths and interactive tutorials
- **Task Management:** `/tasks/` - PRDs and task lists for implementation
- **Test Suite:** `/tests/` - Examples of TDD pattern in practice

---

## Questions?

**For pattern usage questions:**
1. Read the full pattern documentation (linked above)
2. Check "Common Pitfalls" section for your specific issue
3. Review real examples from codebase (file:line references provided)
4. Search test files for usage examples: `tests/test_*.py`

**For new pattern suggestions:**
1. Verify pattern is used 2+ times in project
2. Draft pattern doc using template structure above
3. Create issue or PR with pattern documentation

---

**Last Updated:** 2025-11-23
**Pattern Count:** 5 (TDD Workflow, ThreadPoolExecutor Parallel, Abstract Base Class, Context Engineering: Sessions, Context Engineering: Memory)
**Source Lessons:** 9-13 (Evaluation Fundamentals → RAG Generation & Attribution), Context Engineering Critical Success Factors
