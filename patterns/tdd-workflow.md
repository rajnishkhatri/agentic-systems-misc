# TDD Workflow Pattern

**Pattern Type:** Development Methodology
**Complexity:** ⭐⭐ (Medium)
**Source:** Lesson 13 - RAG Generation & Attribution
**Created:** 2025-11-12
**File References:** `tests/test_rag_generation_eval.py:1-50`

---

## Overview

**Test-Driven Development (TDD)** is a software development methodology where you write tests *before* writing implementation code. The core principle: **Let failing tests guide your implementation.**

**Value Proposition:**
- **Design clarity**: Writing tests first forces you to think about API design and usage patterns before implementation
- **Living documentation**: Tests serve as executable specifications that never go stale
- **Fearless refactoring**: Comprehensive test coverage allows you to improve code with confidence
- **Bug prevention**: Catches edge cases early, before they reach production
- **Defensive coding by default**: TDD naturally leads to input validation and error handling

---

## When to Use

✅ **Use TDD when:**
- Building new features from scratch
- Refactoring existing code (write tests first to capture current behavior)
- Working with critical business logic that must be correct
- Developing public APIs where contract clarity is essential
- Fixing bugs (write a failing test that reproduces the bug, then fix it)

❌ **DON'T use TDD when:**
- Doing exploratory prototyping or proof-of-concepts (write tests after you validate the approach)
- Working with UI/UX design where requirements are highly fluid
- Spiking on unfamiliar libraries (learn first, then apply TDD)
- Facing tight deadlines where you need quick-and-dirty solutions (though this usually backfires)

---

## The TDD Cycle: RED → GREEN → REFACTOR

### 1. RED: Write ONE Failing Test

**Goal:** Define expected behavior before writing code.

```python
def test_should_extract_claims_when_response_has_multiple_statements() -> None:
    """Test extracting atomic claims from LLM response."""
    detector = AttributionDetector()
    response = "The Bhagavad Gita teaches dharma. It was spoken by Krishna to Arjuna."

    claims = detector.extract_claims(response)

    assert isinstance(claims, list)
    assert len(claims) >= 2
    assert all(isinstance(claim, str) for claim in claims)
```

**Rules:**
- Write ONLY ONE test at a time
- Run the test and confirm it fails
- NEVER write implementation code in this phase

### 2. GREEN: Write Minimal Passing Code

**Goal:** Make the test pass with the simplest code possible.

```python
class AttributionDetector:
    """Detects attribution and hallucination in LLM responses."""

    def extract_claims(self, response: str) -> list[str]:
        """Extract atomic claims from response text.

        Args:
            response: LLM response text

        Returns:
            List of atomic claims
        """
        if not response:
            return []

        # Minimal implementation: split by sentences
        claims = response.split(". ")
        return [claim.strip() for claim in claims if claim.strip()]
```

**Rules:**
- Write ONLY enough code to make the test pass
- No extra features or "future-proofing"
- Run test and confirm it passes
- NEVER modify the test in this phase

### 3. REFACTOR: Improve Code Quality

**Goal:** Clean up code while keeping all tests green.

```python
class AttributionDetector:
    """Detects attribution and hallucination in LLM responses."""

    def extract_claims(self, response: str) -> list[str]:
        """Extract atomic claims from response text.

        Args:
            response: LLM response text

        Returns:
            List of atomic claims

        Raises:
            TypeError: If response is not a string
        """
        # Step 1: Type checking (defensive)
        if not isinstance(response, str):
            raise TypeError("response must be a string")

        # Step 2: Input validation (defensive)
        if not response.strip():
            return []

        # Step 3: Main logic (improved with better sentence splitting)
        import re
        # Split on sentence boundaries (.!?)
        claims = re.split(r'[.!?]+', response)

        # Step 4: Return
        return [claim.strip() for claim in claims if claim.strip()]
```

**Rules:**
- Keep all tests passing
- Apply DRY (Don't Repeat Yourself) principle
- Add defensive coding (type hints, validation, error handling)
- Improve readability and performance
- Run tests after each change

---

## Test Naming Convention

**Pattern:** `test_should_[expected_result]_when_[condition]()`

**Benefits:**
- Reads like a specification: "Test should [do what] when [under what circumstances]"
- Makes test intent immediately clear
- Groups related tests alphabetically
- Easy to identify missing test cases

### Real Examples from Codebase

```python
# Testing expected behavior
def test_should_extract_claims_when_response_has_multiple_statements() -> None:
    """Test extracting atomic claims from LLM response."""
    # Source: tests/test_rag_generation_eval.py:27

def test_should_return_empty_list_when_response_is_empty() -> None:
    """Test handling of empty response."""
    # Source: tests/test_rag_generation_eval.py:38

def test_should_verify_attribution_when_claim_matches_context() -> None:
    """Test verifying claims against context documents."""
    # Source: tests/test_rag_generation_eval.py:46

# Testing error conditions
def test_should_raise_error_for_invalid_state_type() -> None:
    """Test that invalid state type raises TypeError."""
    with pytest.raises(TypeError, match="state must be a dict"):
        check_performance_alert("not a dict")

def test_should_raise_error_for_negative_threshold() -> None:
    """Test that negative threshold raises ValueError."""
    with pytest.raises(ValueError, match="threshold must be non-negative"):
        check_performance_alert(state, threshold=-1.0)

# Testing edge cases
def test_should_handle_empty_verses_list() -> None:
    """Test handling of empty retrieval results."""
    counts = calculate_source_counts([])
    assert counts["unique_verses"] == 0

def test_should_handle_missing_total_time() -> None:
    """Test handling of state without total_time."""
    state = {}
    alert = check_performance_alert(state)
    assert alert["is_slow"] is False
```

**Anti-patterns to avoid:**
- ❌ `test_performance()` - Too vague
- ❌ `test_1()` - No context
- ❌ `test_check_performance_alert_function()` - Describes implementation, not behavior

---

## Code Template: TDD Test Structure

```python
"""Tests for [Module Name] ([Lesson Number]).

TDD-RED Phase: Tests for [ClassNames or Functions].

Test Naming Convention: test_should_[expected_result]_when_[condition]
"""

from unittest.mock import MagicMock, patch

import pytest

from backend.module_name import ClassName


# =============================================================================
# [ClassName] Tests
# =============================================================================


class TestClassName:
    """Test suite for ClassName class."""

    def test_should_[expected_result]_when_[condition](self) -> None:
        """Test [specific behavior being tested]."""
        # Arrange: Set up test data
        instance = ClassName()
        input_data = "test input"

        # Act: Call the method
        result = instance.method_name(input_data)

        # Assert: Verify expectations
        assert isinstance(result, expected_type)
        assert result == expected_value

    def test_should_return_empty_when_input_is_empty(self) -> None:
        """Test handling of empty input."""
        instance = ClassName()

        result = instance.method_name("")

        assert result == []

    def test_should_raise_error_when_input_invalid(self) -> None:
        """Test error handling for invalid input."""
        instance = ClassName()

        with pytest.raises(TypeError, match="must be string"):
            instance.method_name(123)
```

---

## Real Example from Codebase

**Source:** `tests/test_rag_generation_eval.py:1-50`

```python
"""Tests for RAG Generation Evaluation Module (Lesson 13).

TDD-RED Phase: Tests for AttributionDetector, HallucinationDetector, and ContextUtilizationScorer.

Test Naming Convention: test_should_[expected_result]_when_[condition]
"""

from unittest.mock import MagicMock, patch

import pytest

from backend.rag_generation_eval import (
    AttributionDetector,
    ContextUtilizationScorer,
    HallucinationDetector,
)


# =============================================================================
# AttributionDetector Tests
# =============================================================================


class TestAttributionDetector:
    """Test suite for AttributionDetector class."""

    def test_should_extract_claims_when_response_has_multiple_statements(self) -> None:
        """Test extracting atomic claims from LLM response."""
        detector = AttributionDetector()
        response = "The Bhagavad Gita teaches dharma. It was spoken by Krishna to Arjuna."

        claims = detector.extract_claims(response)

        assert isinstance(claims, list)
        assert len(claims) >= 2
        assert all(isinstance(claim, str) for claim in claims)

    def test_should_return_empty_list_when_response_is_empty(self) -> None:
        """Test handling of empty response."""
        detector = AttributionDetector()

        claims = detector.extract_claims("")

        assert claims == []

    def test_should_verify_attribution_when_claim_matches_context(self) -> None:
        """Test verifying claims against context documents."""
        detector = AttributionDetector()
        claims = ["Krishna teaches Arjuna about duty"]
        context = ["Krishna teaches Arjuna about his duty and dharma in the battlefield."]

        # Test implementation here...
```

---

## Integration with Defensive Coding

TDD naturally integrates with the **5-Step Defensive Function Template** (see `CLAUDE.md`):

```python
def function_name(arg: Type, optional: Type = default) -> ReturnType:
    """Brief description.

    Args:
        arg: Description
        optional: Description (default: value)

    Returns:
        Description

    Raises:
        TypeError: When type validation fails
        ValueError: When value validation fails
    """
    # Step 1: Type checking (defensive)
    if not isinstance(arg, ExpectedType):
        raise TypeError("arg must be ExpectedType")

    # Step 2: Input validation (defensive)
    if arg < 0:
        raise ValueError("arg must be non-negative")

    # Step 3: Edge case handling
    if len(arg) == 0:
        return default_value

    # Step 4: Main logic (the actual work)
    result = process(arg)

    # Step 5: Return
    return result
```

**How TDD enforces defensive coding:**
1. **RED phase**: Write tests for type errors and invalid inputs
2. **GREEN phase**: Add validation to make tests pass
3. **REFACTOR phase**: Ensure all 5 steps are present and clean

---

## Common Pitfalls

### ❌ Pitfall 1: Writing Implementation Before Test

```python
# BAD: Implementation first
class Calculator:
    def add(self, a: int, b: int) -> int:
        return a + b

# Then writing tests...
def test_add():
    assert Calculator().add(2, 3) == 5
```

**Why it's bad:** You've already decided on the implementation without thinking about the API design or edge cases.

**Fix:** Write the test first to drive the design.

### ❌ Pitfall 2: Testing Too Much at Once

```python
# BAD: One test checking multiple behaviors
def test_calculator():
    calc = Calculator()
    assert calc.add(2, 3) == 5
    assert calc.subtract(5, 3) == 2
    assert calc.multiply(2, 3) == 6
    assert calc.divide(6, 3) == 2
```

**Why it's bad:** When the test fails, you don't know which behavior broke. Hard to debug.

**Fix:** One test per behavior.

### ❌ Pitfall 3: Modifying Tests to Match Implementation

```python
# RED: Initial test
def test_should_return_list_of_claims():
    claims = extract_claims("Text here.")
    assert isinstance(claims, list)

# GREEN: Implementation returns dict instead
def extract_claims(text: str) -> dict:
    return {"claims": text.split(".")}

# BAD: Changing test to match implementation
def test_should_return_list_of_claims():
    claims = extract_claims("Text here.")
    assert isinstance(claims, dict)  # Changed!
```

**Why it's bad:** The test was your specification. Changing it means you're not testing what you originally intended.

**Fix:** Keep the test, fix the implementation.

### ❌ Pitfall 4: Skipping the Refactor Phase

```python
# GREEN: Minimal code that works
def extract_claims(response: str) -> list[str]:
    return response.split(". ")

# BAD: Moving to next test without refactoring
def test_should_handle_empty_response():
    # Next test...
```

**Why it's bad:** Code accumulates technical debt. Becomes harder to maintain and extend.

**Fix:** Always refactor after GREEN before moving to next test. Add defensive coding, improve readability, eliminate duplication.

---

## Summary Checklist

**RED Phase:**
- [ ] Write ONE failing test
- [ ] Test describes expected behavior clearly
- [ ] Test uses naming convention: `test_should_[result]_when_[condition]`
- [ ] Run test and confirm it fails
- [ ] NEVER write implementation code

**GREEN Phase:**
- [ ] Write ONLY enough code to make test pass
- [ ] No extra features or anticipation
- [ ] Run test and confirm it passes
- [ ] NEVER modify the test

**REFACTOR Phase:**
- [ ] Clean up code (DRY, readability, performance)
- [ ] Add defensive coding (type hints, validation, error handling)
- [ ] Keep all tests passing
- [ ] Run tests after each change

**Result:**
- [ ] Code is well-tested, maintainable, and production-ready
- [ ] Tests serve as living documentation
- [ ] Fearless refactoring enabled

---

## Related Patterns

- **Defensive Function Template** (`CLAUDE.md`) - 5-step pattern for robust functions
- **Abstract Base Class** (`patterns/abstract-base-class.md`) - OOP pattern that pairs well with TDD
- **ThreadPoolExecutor Parallel** (`patterns/threadpool-parallel.md`) - Concurrency pattern tested with TDD

---

## Further Reading

- Kent Beck, "Test-Driven Development by Example"
- Martin Fowler, "Refactoring: Improving the Design of Existing Code"
- Project TDD examples: `tests/test_rag_generation_eval.py`, `tests/test_ai_judge_framework.py`, `tests/test_exact_evaluation.py`
