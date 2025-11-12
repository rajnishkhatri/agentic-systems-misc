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

| Pattern | Complexity | Primary Use Case | Source File |
|---------|-----------|------------------|-------------|
| [TDD Workflow](#tdd-workflow) | ⭐⭐ (Medium) | Testing & development methodology | `tests/test_rag_generation_eval.py:1-50` |
| [ThreadPoolExecutor Parallel](#threadpoolexecutor-parallel) | ⭐⭐⭐ (High) | Concurrent batch processing (I/O-bound) | `backend/query_rewrite_agent.py:187-208` |
| [Abstract Base Class](#abstract-base-class) | ⭐⭐⭐ (High) | OOP interface enforcement & polymorphism | `backend/ai_judge_framework.py:64-277` |

**Complexity Legend:**
- ⭐ (Low): Can be understood and applied in <15 minutes
- ⭐⭐ (Medium): Requires 15-30 minutes to understand, practice needed
- ⭐⭐⭐ (High): Requires 30-60 minutes to understand, significant practice needed

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

## How to Use This Library

### For Developers

1. **Identify your problem domain:**
   - Need to write tests? → [TDD Workflow](tdd-workflow.md)
   - Need to parallelize I/O tasks? → [ThreadPoolExecutor Parallel](threadpool-parallel.md)
   - Need multiple implementations of same interface? → [Abstract Base Class](abstract-base-class.md)

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

**Last Updated:** 2025-11-12
**Pattern Count:** 3 (TDD Workflow, ThreadPoolExecutor Parallel, Abstract Base Class)
**Source Lessons:** 9-13 (Evaluation Fundamentals → RAG Generation & Attribution)
