# TDD Phase Rules: RED → GREEN → REFACTOR

This document defines the strict constraints for each phase of the Test-Driven Development cycle.

---

## RED Phase: Write Failing Test

### Purpose
Create a test that specifies the desired behavior BEFORE any implementation exists.

### Rules

✅ **ALLOWED:**
- Write ONE test for a single behavior
- Use test naming convention: `test_should_[result]_when_[condition]()`
- Run the test to confirm it fails
- Document expected behavior in test docstring
- Import necessary testing utilities (pytest, unittest, etc.)
- Set up test fixtures or test data

❌ **FORBIDDEN:**
- Write implementation code
- Write multiple tests at once
- Modify existing implementation code
- Skip running the test
- Write tests without assertions
- Create passing tests (test must fail initially)

### Expected Outcome
```
FAILED tests/test_feature.py::test_should_return_sum_when_valid_inputs - AttributeError: module has no attribute 'calculate_total'
```

### Phase Transition
Move to GREEN phase ONLY when:
1. Test is written with clear assertion
2. Test has been run
3. Test fails for the RIGHT reason (missing implementation, not syntax error)

---

## GREEN Phase: Minimal Implementation

### Purpose
Write the SMALLEST amount of code needed to make the failing test pass.

### Rules

✅ **ALLOWED:**
- Write minimal code to satisfy current test
- Add necessary imports
- Create functions/classes referenced by test
- Use simple, direct solutions (even if not optimal)
- Run the test to confirm it passes

❌ **FORBIDDEN:**
- Modify the test in any way
- Add features not required by current test
- Optimize prematurely
- Add defensive coding (that's for REFACTOR phase)
- Write code for anticipated future needs
- Add multiple features at once

### Expected Outcome
```
PASSED tests/test_feature.py::test_should_return_sum_when_valid_inputs
```

### Phase Transition
Move to REFACTOR phase ONLY when:
1. Current test passes
2. ALL existing tests still pass
3. No test modifications were made

---

## REFACTOR Phase: Improve Quality

### Purpose
Improve code quality, apply defensive coding, and ensure maintainability while keeping all tests green.

### Rules

✅ **ALLOWED:**
- Improve code readability (rename variables, extract functions)
- Apply defensive coding principles:
  - Add type hints to all functions
  - Add input validation with guard clauses
  - Add specific exception handling
  - Add descriptive error messages
- Eliminate code duplication (DRY principle)
- Optimize performance (if needed)
- Improve code organization
- Run tests after EVERY change

❌ **FORBIDDEN:**
- Modify test behavior or assertions
- Add new features (write new test first)
- Break existing tests
- Skip running tests
- Remove defensive coding
- Make changes without running tests

### Expected Outcome
```
PASSED tests/test_feature.py::test_should_return_sum_when_valid_inputs
PASSED tests/test_feature.py::test_should_raise_when_empty_list
PASSED tests/test_feature.py::test_should_raise_when_invalid_type
==================== 3 passed in 0.12s ====================
```

### Phase Transition
Move to next RED phase (new test) when:
1. All tests pass
2. Code quality is improved
3. Defensive coding is applied
4. No duplication remains

---

## Phase Violation Examples

### ❌ RED Phase Violation: Implementation Before Test

```python
# WRONG: Writing implementation first
def calculate_total(items: list[int]) -> int:
    return sum(items)

# Test written after
def test_should_return_sum_when_valid_inputs():
    assert calculate_total([1, 2, 3]) == 6
```

**Why wrong:** Violates TDD principle of test-first development. May lead to untested code paths.

---

### ❌ GREEN Phase Violation: Modifying Test

```python
# Original failing test
def test_should_return_sum_when_valid_inputs():
    assert calculate_total([1, 2, 3]) == 6  # Fails: function doesn't exist

# WRONG: Changing test to make it pass
def test_should_return_sum_when_valid_inputs():
    assert calculate_total([1, 2, 3]) == 0  # Changed expectation instead of implementing
```

**Why wrong:** Test defines the specification. Changing test defeats the purpose of TDD.

---

### ❌ GREEN Phase Violation: Adding Extra Features

```python
# Test only requires sum of valid inputs
def test_should_return_sum_when_valid_inputs():
    assert calculate_total([1, 2, 3]) == 6

# WRONG: Adding features not required by test
def calculate_total(items: list[int]) -> int:
    if not items:  # NOT required by current test
        raise ValueError("items required")
    if not all(isinstance(x, int) for x in items):  # NOT required by current test
        raise TypeError("all items must be integers")
    return sum(items)
```

**Why wrong:** Add minimal code to pass current test. Write NEW tests for edge cases, THEN implement.

**Correct GREEN implementation:**
```python
def calculate_total(items: list[int]) -> int:
    return sum(items)  # Minimal code to pass test
```

---

### ❌ REFACTOR Phase Violation: Adding Features

```python
# Tests pass with current implementation
def calculate_total(items: list[int]) -> int:
    if not items:
        raise ValueError("items required")
    return sum(items)

# WRONG: Adding new feature during REFACTOR
def calculate_total(items: list[int], multiplier: float = 1.0) -> float:
    if not items:
        raise ValueError("items required")
    return sum(items) * multiplier  # NEW feature without test
```

**Why wrong:** New features require new tests first. REFACTOR improves existing code, doesn't add functionality.

---

## Quick Reference Table

| Phase | Write Test? | Modify Test? | Write Code? | Optimize Code? | Run Tests? |
|-------|-------------|--------------|-------------|----------------|------------|
| RED   | ✅ ONE test | ❌ No        | ❌ No       | ❌ No          | ✅ Must fail |
| GREEN | ❌ No       | ❌ No        | ✅ Minimal  | ❌ No          | ✅ Must pass |
| REFACTOR | ❌ No    | ❌ No        | ✅ Improve  | ✅ Yes         | ✅ Must pass |

---

## Integration with Defensive Coding

Defensive coding is applied primarily in the **REFACTOR phase**:

### Step 1: RED - Test for edge case
```python
def test_should_raise_when_empty_list():
    with pytest.raises(ValueError, match="items required"):
        calculate_total([])
```

### Step 2: GREEN - Minimal code to pass
```python
def calculate_total(items):
    if not items:
        raise ValueError("items required")
    return sum(items)
```

### Step 3: REFACTOR - Add defensive coding
```python
def calculate_total(items: list[int] | None) -> int:  # Type hints
    """Calculate sum of items.

    Args:
        items: List of integers to sum

    Returns:
        Sum of all items

    Raises:
        ValueError: If items is empty or None
        TypeError: If items contains non-integers
    """
    # Input validation
    if not items:
        raise ValueError("items required")

    # Type validation
    if not all(isinstance(x, int) for x in items):
        raise TypeError("all items must be integers")

    return sum(items)
```

---

## Common Questions

**Q: Can I write multiple tests in RED phase if they test the same function?**
A: No. Write ONE test, make it pass (GREEN), refactor, then write the NEXT test. This ensures incremental progress and clear cause-effect relationships.

**Q: What if the minimal GREEN implementation feels too simple?**
A: That's the point! Simple code is easier to understand and refactor. Trust the process - complexity will emerge naturally as you add more tests.

**Q: Can I add type hints in GREEN phase?**
A: Only if absolutely necessary to make the test pass (e.g., type checker is part of your test suite). Otherwise, add them in REFACTOR phase.

**Q: What if I discover a bug during REFACTOR?**
A: Stop refactoring, write a NEW test that exposes the bug (RED phase), fix it minimally (GREEN phase), then continue refactoring.

**Q: How do I know when REFACTOR is done?**
A: When code follows DRY principle, has defensive coding, is readable, and all tests pass. If you can't think of improvements that maintain test success, you're done.

---

## See Also

- **Test Naming Guide**: `test-naming-guide.md` for naming convention details
- **Good TDD Session**: `../examples/good-tdd-session.md` for real workflow example
- **Common Violations**: `../examples/common-violations.md` for anti-patterns
- **CLAUDE.md TDD Mode**: `../../CLAUDE.md` lines 33-115 for comprehensive TDD workflow
- **Pattern Library**: `/patterns/tdd-workflow.md` for TDD pattern template
