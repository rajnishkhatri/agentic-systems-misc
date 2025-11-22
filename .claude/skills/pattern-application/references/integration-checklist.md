# Pattern Integration Checklist

**Purpose:** Step-by-step guide for applying pattern templates to your code with defensive coding

**Last Updated:** 2025-11-18

---

## Overview

This checklist ensures you correctly apply pattern templates from the pattern library (`/patterns/`) with all defensive coding elements included.

**Core Principle:** Copy template → Customize → Test → Document

---

## Universal Integration Steps (All Patterns)

Follow these steps for EVERY pattern application:

### Step 1: Identify the Right Pattern

**Use decision tree:** `pattern-decision-tree.md`

**Ask yourself:**
- What problem am I solving?
- Which pattern matches my use case?
- Am I sure I need this pattern? (avoid premature abstraction)

**Verification:**
- [ ] I've read the "When to use" section in pattern documentation
- [ ] I've checked "When NOT to use" to avoid anti-patterns
- [ ] This is the simplest pattern that solves my problem

---

### Step 2: Read Full Pattern Documentation

**Don't skip to the code template!** Read the entire pattern file first.

**Pattern documentation structure:**
- Overview (what the pattern does)
- When to use / When NOT to use
- Core concepts
- Code template
- Real examples from codebase
- Common pitfalls
- Integration with defensive coding

**Verification:**
- [ ] I've read the full pattern documentation
- [ ] I understand the core concepts
- [ ] I've reviewed the real examples
- [ ] I know the common pitfalls to avoid

---

### Step 3: Copy Pattern Template

**Location:** Each pattern file has a "Code Template" section

**How to copy:**
1. Open pattern file (e.g., `patterns/threadpool-parallel.md`)
2. Navigate to "Code Template" section
3. Copy the complete template (don't extract snippets)
4. Paste into your target file

**Verification:**
- [ ] I copied the complete template (not partial code)
- [ ] Template includes all defensive coding elements
- [ ] Template includes type hints, docstrings, error handling

---

### Step 4: Apply Defensive Coding (If Not Already Included)

**All patterns include defensive coding by default**, but verify:

#### Type Hints
- [ ] All function parameters have type hints: `def func(x: int, y: str) -> dict:`
- [ ] Complex types use proper syntax: `list[str]`, `dict[str, Any]`, `Optional[int]`
- [ ] Return types are specified: `-> None`, `-> list[dict]`, etc.

#### Input Validation
- [ ] Guard clauses at function start check for None, empty collections, invalid ranges
- [ ] Specific exception types: `TypeError` for type errors, `ValueError` for value errors
- [ ] Descriptive error messages: `raise ValueError("threshold must be non-negative")`

#### Error Handling
- [ ] No bare `except:` statements (catch specific exceptions)
- [ ] Exceptions are logged or re-raised with context
- [ ] Resources use context managers (`with` statements)

#### Docstrings
- [ ] Function has docstring with brief description
- [ ] `Args:` section documents all parameters
- [ ] `Returns:` section documents return value
- [ ] `Raises:` section documents exceptions

**Example defensive function template:**
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

---

### Step 5: Add Pattern Reference Comment

**Add comment at top of function/class referencing pattern:**

```python
# Pattern: TDD Workflow (patterns/tdd-workflow.md)
def test_should_extract_claims_when_response_has_multiple_statements() -> None:
    ...

# Pattern: ThreadPoolExecutor Parallel (patterns/threadpool-parallel.md)
def batch_process_queries(queries: list[str]) -> list[dict]:
    ...

# Pattern: Abstract Base Class (patterns/abstract-base-class.md)
class BaseJudge(ABC):
    ...
```

**Verification:**
- [ ] Pattern reference comment added
- [ ] Comment includes pattern name and file path
- [ ] Comment is above the function/class definition

---

### Step 6: Test Using TDD Workflow

**Even if your pattern isn't TDD, test the implementation:**

1. **Write test** for pattern implementation
2. **Run test** and verify it passes
3. **Test edge cases** (empty input, None, errors)

**Verification:**
- [ ] Test written for happy path
- [ ] Tests for edge cases (empty, None, invalid input)
- [ ] Tests for error conditions (TypeError, ValueError)
- [ ] All tests pass

---

### Step 7: Review Checklist for Pattern Quality

**Final verification before committing:**

- [ ] Pattern correctly addresses my use case
- [ ] Template fully customized (no placeholder names)
- [ ] Defensive coding included (types, validation, errors, docstrings)
- [ ] Pattern reference comment added
- [ ] Tests written and passing
- [ ] Code follows project style (120 char line length, Ruff formatting)
- [ ] No anti-patterns from pattern documentation

---

## Pattern-Specific Checklists

### TDD Workflow Pattern Integration

**File:** `patterns/tdd-workflow.md`

**Checklist:**
- [ ] **RED Phase:** Write ONE failing test first
  - [ ] Test named: `test_should_[result]_when_[condition]()`
  - [ ] Run test and confirm it fails
  - [ ] No implementation code written yet
- [ ] **GREEN Phase:** Write minimal code to pass test
  - [ ] Code makes test pass
  - [ ] No extra features or anticipation
  - [ ] Test not modified during GREEN phase
- [ ] **REFACTOR Phase:** Improve code quality
  - [ ] Apply defensive coding (type hints, validation)
  - [ ] Improve readability, DRY principle
  - [ ] All tests still pass after refactoring

**Common pitfalls to avoid:**
- ❌ Writing code before test exists
- ❌ Writing multiple tests at once
- ❌ Adding code not required by current test
- ❌ Modifying test during GREEN phase

**Example integration:**
```python
# RED: Write failing test
# Pattern: TDD Workflow (patterns/tdd-workflow.md)
def test_should_sum_items_when_valid_list() -> None:
    assert calculate_total([1, 2, 3]) == 6

# GREEN: Minimal implementation
def calculate_total(items: list[int]) -> int:
    return sum(items)

# REFACTOR: Add defensive coding
def calculate_total(items: list[int] | None) -> int:
    """Calculate sum of integer list.

    Args:
        items: List of integers to sum

    Returns:
        Sum of all items

    Raises:
        ValueError: If items is empty or None
        TypeError: If items contains non-integers
    """
    if not items:
        raise ValueError("items required")
    if not all(isinstance(x, int) for x in items):
        raise TypeError("all items must be integers")
    return sum(items)
```

---

### ThreadPoolExecutor Parallel Pattern Integration

**File:** `patterns/threadpool-parallel.md`

**Checklist:**
- [ ] **Confirm I/O-bound:** Tasks spend time waiting (API calls, file I/O, database)
- [ ] **Order preservation:** Using `future_to_index` mapping
- [ ] **Exception handling:** Try-except per task, don't crash batch
- [ ] **Progress tracking:** Using `tqdm` with `as_completed()`
- [ ] **Worker tuning:** `max_workers` set appropriately (5-20 for I/O tasks)
- [ ] **Fallback values:** Failed tasks return None or default value
- [ ] **Resource management:** Using `with` context manager

**Common pitfalls to avoid:**
- ❌ Using for CPU-bound tasks (use ProcessPoolExecutor instead)
- ❌ Sequential dependencies (Task N depends on Task N-1)
- ❌ Not preserving result order
- ❌ Missing exception handling (one failure crashes batch)
- ❌ No progress feedback for long batches

**Example integration:**
```python
# Pattern: ThreadPoolExecutor Parallel (patterns/threadpool-parallel.md)
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm

def batch_process_queries(queries: list[str]) -> list[dict | None]:
    """Process multiple queries in parallel using ThreadPoolExecutor.

    Args:
        queries: List of query strings to process

    Returns:
        List of result dicts in same order as queries (None for failures)

    Raises:
        TypeError: If queries is not a list
        ValueError: If queries is empty
    """
    # Defensive coding: Type and input validation
    if not isinstance(queries, list):
        raise TypeError("queries must be a list")
    if not queries:
        raise ValueError("queries cannot be empty")

    # Initialize results list with None (order preservation)
    results: list[dict | None] = [None] * len(queries)

    # ThreadPoolExecutor with context manager (resource management)
    with ThreadPoolExecutor(max_workers=10) as executor:
        # Submit tasks with index mapping (order preservation)
        future_to_index = {
            executor.submit(process_single_query, query): i
            for i, query in enumerate(queries)
        }

        # Collect results with progress bar
        for future in tqdm(as_completed(future_to_index), total=len(queries), desc="Processing"):
            index = future_to_index[future]
            try:
                # Exception handling per task
                results[index] = future.result()
            except Exception as e:
                print(f"Error processing query {index}: {e}")
                results[index] = None  # Fallback value

    return results
```

---

### Abstract Base Class Pattern Integration

**File:** `patterns/abstract-base-class.md`

**Checklist:**
- [ ] **Base class inherits from ABC:** `class BaseName(ABC):`
- [ ] **Abstract methods marked:** Using `@abstractmethod` decorator
- [ ] **Defensive base `__init__`:** Type/value validation in base class
- [ ] **Shared functionality:** Common helpers in base class (retry logic, validation)
- [ ] **Subclass contract:** Subclasses call `super().__init__()`
- [ ] **Clear interface:** Abstract methods define what subclasses must implement
- [ ] **Type hints:** All abstract methods have type hints

**Common pitfalls to avoid:**
- ❌ Premature abstraction (only 1 implementation)
- ❌ Forgetting `super().__init__()` in subclass
- ❌ Not marking methods with `@abstractmethod`
- ❌ Duplicating logic instead of sharing in base class

**Example integration:**
```python
# Pattern: Abstract Base Class (patterns/abstract-base-class.md)
from abc import ABC, abstractmethod

class BaseJudge(ABC):
    """Abstract base class for all judge implementations.

    Enforces common interface and provides shared functionality.
    """

    def __init__(self, model: str, temperature: float = 0.0):
        """Initialize base judge.

        Args:
            model: LLM model name
            temperature: Sampling temperature (0.0-2.0)

        Raises:
            TypeError: If model is not a string
            ValueError: If temperature out of range
        """
        # Defensive validation in base class
        if not isinstance(model, str):
            raise TypeError("model must be a string")
        if not (0.0 <= temperature <= 2.0):
            raise ValueError("temperature must be between 0.0 and 2.0")

        self.model = model
        self.temperature = temperature

    @abstractmethod
    def evaluate(self, query: str, response: str) -> dict:
        """Evaluate response quality. Subclasses must implement.

        Args:
            query: User query
            response: System response

        Returns:
            Evaluation dict with score and reasoning
        """
        pass

    def _call_llm(self, prompt: str) -> str:
        """Shared helper method for LLM calls."""
        # Retry logic, API calls, etc.
        pass


class DietaryAdherenceJudge(BaseJudge):
    """Concrete implementation for dietary adherence evaluation."""

    def __init__(self, model: str, temperature: float = 0.0):
        # CRITICAL: Call parent initializer
        super().__init__(model, temperature)
        self.prompt_template = self._load_template("dietary.txt")

    def evaluate(self, query: str, response: str) -> dict:
        """Implement required abstract method."""
        # Defensive validation
        if not isinstance(query, str) or not isinstance(response, str):
            raise TypeError("query and response must be strings")

        # Use shared helper
        prompt = self.prompt_template.format(query=query, response=response)
        raw = self._call_llm(prompt)
        return {"score": 1.0, "reasoning": raw}
```

---

## Combining Multiple Patterns

### Checklist for Pattern Combinations

When using multiple patterns together:

- [ ] **Identify all applicable patterns** (use decision tree)
- [ ] **Apply patterns in order:** Usually TDD first, then others
- [ ] **Verify patterns don't conflict** (e.g., TDD tests for ABC implementation)
- [ ] **Reference all patterns in comments**

**Example: TDD + ThreadPoolExecutor**

```python
# RED: Write test first
# Pattern: TDD Workflow (patterns/tdd-workflow.md)
def test_should_process_100_queries_in_parallel() -> None:
    queries = [f"query_{i}" for i in range(100)]
    results = batch_process(queries)
    assert len(results) == 100
    assert all(r is not None for r in results)

# GREEN: Implement using ThreadPoolExecutor
# Pattern: ThreadPoolExecutor Parallel (patterns/threadpool-parallel.md)
def batch_process(queries: list[str]) -> list[dict]:
    # Implementation using ThreadPoolExecutor template
    ...

# REFACTOR: Add defensive coding, progress bars
```

---

## Post-Integration Verification

After applying a pattern, verify:

### Code Quality
- [ ] Run `ruff format` (code formatting)
- [ ] Run `ruff check` (linting)
- [ ] No type errors (if using mypy)
- [ ] Line length ≤120 characters

### Testing
- [ ] All tests pass: `pytest`
- [ ] Test coverage includes pattern implementation
- [ ] Edge cases tested (empty input, None, errors)

### Documentation
- [ ] Pattern reference comment added
- [ ] Docstrings complete (Args, Returns, Raises)
- [ ] README or CHANGELOG updated if pattern adds new feature

### Review
- [ ] Pattern correctly solves problem
- [ ] No anti-patterns from pattern documentation
- [ ] Code follows defensive coding principles
- [ ] Similar to real examples in pattern file

---

## Quick Reference: Integration Steps Summary

1. **Identify** pattern using decision tree
2. **Read** full pattern documentation
3. **Copy** complete template from pattern file
4. **Apply** defensive coding (if not included)
5. **Add** pattern reference comment
6. **Test** using TDD workflow
7. **Review** quality checklist

**Time estimate:** 15-30 minutes for first pattern application, <10 minutes for subsequent uses

---

## Troubleshooting

### Problem: "I'm not sure which pattern to use"
**Solution:** Use `pattern-decision-tree.md` flowchart and use case table

### Problem: "Pattern template doesn't fit my use case"
**Solution:** Patterns are templates, not rigid rules. Customize for your needs, but keep defensive coding elements.

### Problem: "My tests are failing after applying pattern"
**Solution:**
1. Check you followed TDD workflow (RED → GREEN → REFACTOR)
2. Verify defensive validation isn't too strict
3. Review "Common Pitfalls" in pattern documentation

### Problem: "Pattern seems too complex for my simple use case"
**Solution:** Don't use it! Check "When NOT to use" section. Simpler code is better than premature pattern application.

---

## Further Reading

- **Pattern Library:** `patterns/README.md`
- **Decision Tree:** `pattern-decision-tree.md`
- **TDD Workflow:** `patterns/tdd-workflow.md`
- **ThreadPoolExecutor Parallel:** `patterns/threadpool-parallel.md`
- **Abstract Base Class:** `patterns/abstract-base-class.md`
- **Defensive Coding:** `CLAUDE.md` (Defensive Function Template)

---

**Last Updated:** 2025-11-18
**Pattern Count:** 3 (TDD Workflow, ThreadPoolExecutor Parallel, Abstract Base Class)
