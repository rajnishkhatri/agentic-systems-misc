# Common TDD Violations and Anti-Patterns

This document catalogs common violations of TDD discipline and explains why they're problematic.

---

## Violation 1: Implementation Before Test

### ❌ What It Looks Like

```python
# WRONG: Writing implementation first
def calculate_total(items: list[int]) -> int:
    """Calculate sum of items."""
    if not items:
        raise ValueError("items required")
    return sum(items)

# Test written after implementation
def test_should_return_sum_when_valid_inputs():
    assert calculate_total([1, 2, 3]) == 6
```

### Why It's Wrong

1. **No verification of requirements** - Implementation might solve the wrong problem
2. **Over-engineering risk** - Might add features not actually needed
3. **Tests become validation, not specification** - Tests verify implementation, don't define behavior
4. **Missing edge cases** - Without test-first thinking, edge cases often overlooked
5. **Harder to refactor** - Tests are coupled to implementation details

### ✅ Correct Approach

```python
# RED: Write test FIRST to specify behavior
def test_should_return_sum_when_valid_inputs():
    assert calculate_total([1, 2, 3]) == 6

# Verify test fails
# FAILED - ImportError: cannot import name 'calculate_total'

# GREEN: Minimal implementation
def calculate_total(items: list[int]) -> int:
    return sum(items)

# Verify test passes
# PASSED ✓

# REFACTOR: Add defensive coding
def calculate_total(items: list[int] | None) -> int:
    """Calculate sum of items.

    Args:
        items: List of integers to sum

    Returns:
        Sum of all items

    Raises:
        ValueError: If items is empty or None
    """
    if not items:
        raise ValueError("items required")
    return sum(items)
```

### Real-World Example from Codebase

**Symptom:** Function has untested code paths

```python
# Implementation with multiple branches
def check_performance_alert(state: dict, threshold: float = 10.0) -> dict:
    total_time = state.get("total_time", 0.0)
    is_slow = total_time > threshold

    if is_slow:
        # Complex slowest agent detection - but no test for this path!
        timing = state.get("_metrics", {}).get("timing", {})
        slowest_agent = max(timing.items(), key=lambda x: x[1])
        return {"is_slow": True, "slowest_agent": slowest_agent[0]}

    return {"is_slow": False}
```

**Fix:** Write test for missing path FIRST, then implement

```python
# RED: Test for slowest agent detection
def test_should_identify_slowest_agent_when_query_exceeds_threshold():
    state = {
        "total_time": 12.5,
        "_metrics": {
            "timing": {"retrieval": 3.0, "synthesis": 8.5, "validation": 1.0}
        }
    }
    alert = check_performance_alert(state)
    assert alert["slowest_agent"] == "synthesis"
```

---

## Violation 2: Writing Multiple Tests at Once

### ❌ What It Looks Like

```python
# WRONG: Writing multiple tests in RED phase
class TestCalculateTotal:
    def test_should_return_sum_when_valid_inputs(self):
        assert calculate_total([1, 2, 3]) == 6

    def test_should_raise_error_when_empty_list(self):
        with pytest.raises(ValueError):
            calculate_total([])

    def test_should_raise_error_when_invalid_type(self):
        with pytest.raises(TypeError):
            calculate_total([1, "2", 3])

    def test_should_handle_negative_numbers(self):
        assert calculate_total([-1, -2]) == -3

# Then implementing all at once
def calculate_total(items):
    # Big implementation covering all test cases
    ...
```

### Why It's Wrong

1. **Multiple failing tests** - Hard to diagnose which requirement is causing issues
2. **Lost focus** - Cognitive overload trying to satisfy multiple specs simultaneously
3. **Unclear cause-effect** - If implementation fails, which test drove which code?
4. **Violates TDD rhythm** - Should be RED→GREEN→REFACTOR for EACH test
5. **Harder to track progress** - Can't celebrate small wins

### ✅ Correct Approach

```python
# Iteration 1: RED
def test_should_return_sum_when_valid_inputs(self):
    assert calculate_total([1, 2, 3]) == 6

# Iteration 1: GREEN
def calculate_total(items):
    return sum(items)

# Iteration 1: REFACTOR (add type hints, docstring)

# Iteration 2: RED (NEW test)
def test_should_raise_error_when_empty_list(self):
    with pytest.raises(ValueError):
        calculate_total([])

# Iteration 2: GREEN (add validation)
def calculate_total(items):
    if not items:
        raise ValueError("items required")
    return sum(items)

# Continue for each test...
```

### Real-World Impact

**Multiple failing tests:**
```
FAILED test_should_return_sum_when_valid_inputs
FAILED test_should_raise_error_when_empty_list
FAILED test_should_raise_error_when_invalid_type
FAILED test_should_handle_negative_numbers

4 failed in 0.12s
```

**One failing test at a time:**
```
FAILED test_should_return_sum_when_valid_inputs
```
Fix it ✅
```
FAILED test_should_raise_error_when_empty_list
```
Fix it ✅
```
All tests pass!
```

**Clear progress, easier debugging, lower cognitive load.**

---

## Violation 3: Modifying Tests During GREEN Phase

### ❌ What It Looks Like

```python
# RED: Original test
def test_should_return_sum_when_valid_inputs():
    result = calculate_total([1, 2, 3])
    assert result == 6, f"Expected 6, got {result}"

# Run test - FAILED: calculate_total() doesn't exist

# WRONG: Changing test expectation instead of implementing function
def test_should_return_sum_when_valid_inputs():
    result = calculate_total([1, 2, 3])
    assert result == 0, f"Expected 0, got {result}"  # Changed from 6 to 0!
```

### Why It's Wrong

1. **Test defines the specification** - Changing test defeats the purpose
2. **Moving goalposts** - Makes it impossible to verify if implementation is correct
3. **Hides bugs** - Real bug might exist, but test was changed to hide it
4. **Loss of trust** - Tests no longer represent real requirements
5. **Technical debt** - Wrong specification will cause issues later

### ✅ Correct Approach

```python
# RED: Test defines requirement (DO NOT CHANGE)
def test_should_return_sum_when_valid_inputs():
    result = calculate_total([1, 2, 3])
    assert result == 6  # This is the specification

# GREEN: Implement to satisfy test (CHANGE ONLY THIS)
def calculate_total(items: list[int]) -> int:
    return sum(items)  # Implementation matches specification

# If test expectation was WRONG, go back to RED and write CORRECT test
```

### Exception: Fixing Test Bugs

**Only acceptable reason to modify test in GREEN phase:**

```python
# RED: Test has TYPO (not wrong expectation)
def test_should_return_sum_when_valid_inputs():
    result = calculate_total([1, 2, 3])
    assert result == 5  # TYPO: 1+2+3 = 6, not 5

# Fix typo (this is fixing test bug, not changing specification)
def test_should_return_sum_when_valid_inputs():
    result = calculate_total([1, 2, 3])
    assert result == 6  # Corrected typo
```

**How to distinguish:**
- **Typo:** Mathematical error, syntax error, wrong variable name
- **Specification change:** Changing expected behavior to match implementation

**Rule:** If you're changing test expectation to match implementation, you're doing it WRONG.

---

## Violation 4: Adding Extra Features in GREEN Phase

### ❌ What It Looks Like

```python
# RED: Test only requires basic sum
def test_should_return_sum_when_valid_inputs():
    assert calculate_total([1, 2, 3]) == 6

# WRONG: Adding features not required by current test
def calculate_total(items: list[int], multiplier: float = 1.0) -> float:
    if not items:  # Not tested yet
        raise ValueError("items required")  # Not tested yet
    if not all(isinstance(x, int) for x in items):  # Not tested yet
        raise TypeError("must be integers")  # Not tested yet

    total = sum(items)
    return total * multiplier  # Not tested yet!
```

### Why It's Wrong

1. **Anticipating requirements** - YAGNI (You Aren't Gonna Need It) violation
2. **Untested code paths** - Features without tests might have bugs
3. **Violates "minimal code" rule** - GREEN phase should be MINIMAL
4. **Over-engineering** - Adding complexity before it's needed
5. **Harder to debug** - More code = more places for bugs

### ✅ Correct Approach

```python
# RED: Test requires basic sum
def test_should_return_sum_when_valid_inputs():
    assert calculate_total([1, 2, 3]) == 6

# GREEN: MINIMAL implementation (only what's needed to pass test)
def calculate_total(items: list[int]) -> int:
    return sum(items)  # That's it!

# REFACTOR: Add defensive coding (still no new features)
def calculate_total(items: list[int]) -> int:
    """Calculate sum of items."""
    if not isinstance(items, list):
        raise TypeError("items must be a list")
    return sum(items)

# If you need multiplier feature, write NEW test FIRST:
# RED: New test for multiplier
def test_should_multiply_sum_when_multiplier_provided():
    assert calculate_total([1, 2, 3], multiplier=2.0) == 12.0

# Then add minimal code to pass
```

### Real-World Example

**Over-engineered GREEN phase:**
```python
# Test only asks for exact match
def test_should_match_when_strings_identical():
    assert exact_match("hello", "hello") is True

# WRONG: Adding normalization, regex, fuzzy matching
def exact_match(text1, text2, normalize=False, use_regex=False, fuzzy_threshold=0.8):
    if use_regex:
        return re.match(text1, text2) is not None
    if normalize:
        text1, text2 = normalize_text(text1), normalize_text(text2)
    if fuzzy_threshold < 1.0:
        return fuzzy_match(text1, text2, fuzzy_threshold)
    return text1 == text2
```

**Correct GREEN phase:**
```python
# Test asks for exact match
def test_should_match_when_strings_identical():
    assert exact_match("hello", "hello") is True

# Minimal code
def exact_match(text1: str, text2: str) -> bool:
    return text1 == text2  # Just what's needed!
```

---

## Violation 5: Skipping Test Execution

### ❌ What It Looks Like

```python
# RED: Write test
def test_should_return_sum_when_valid_inputs():
    assert calculate_total([1, 2, 3]) == 6

# WRONG: Immediately writing implementation without running test
def calculate_total(items: list[int]) -> int:
    return sum(items)

# Then running both at once
# $ pytest tests/test_calculator.py
# PASSED ✓  <-- Did test actually fail first?
```

### Why It's Wrong

1. **No verification of test validity** - Test might be passing for wrong reason
2. **False positives** - Test might have been written incorrectly
3. **Lost TDD rhythm** - Can't verify cause-effect relationship
4. **Risk of tautological tests** - Test might not actually test anything

```python
# Example: Test that always passes (useless test)
def test_should_return_sum_when_valid_inputs():
    assert True  # Always passes, doesn't test anything!
```

### ✅ Correct Approach

```python
# RED: Write test
def test_should_return_sum_when_valid_inputs():
    assert calculate_total([1, 2, 3]) == 6

# RUN TEST AND VERIFY IT FAILS
# $ pytest tests/test_calculator.py::test_should_return_sum_when_valid_inputs -v
# FAILED - ImportError: cannot import name 'calculate_total'
# ✅ Confirmed: Test fails for the RIGHT reason

# GREEN: Implement
def calculate_total(items: list[int]) -> int:
    return sum(items)

# RUN TEST AND VERIFY IT PASSES
# $ pytest tests/test_calculator.py::test_should_return_sum_when_valid_inputs -v
# PASSED ✓
# ✅ Confirmed: Implementation makes test pass
```

### Real-World Trap: Tautological Tests

```python
# Test that doesn't actually test anything
def test_should_calculate_total():
    total = calculate_total([1, 2, 3])
    # WRONG: Testing against itself instead of expected value
    assert total == calculate_total([1, 2, 3])  # Always passes!

# Correct version
def test_should_return_sum_when_valid_inputs():
    assert calculate_total([1, 2, 3]) == 6  # Tests against known value
```

**How to catch:** If you skip RED phase verification, you might miss tautological tests.

---

## Violation 6: Refactoring Without Green Tests

### ❌ What It Looks Like

```python
# Test passes
def test_should_return_sum_when_valid_inputs():
    assert calculate_total([1, 2, 3]) == 6
# PASSED ✓

# Current implementation
def calculate_total(items):
    return sum(items)

# WRONG: Refactoring without running tests first
def calculate_total(items: list[int]) -> int:
    """Calculate sum with validation."""
    if not items:
        raise ValueError("items required")
    if not all(isinstance(x, int) for x in items):
        raise TypeError("must be integers")
    return sum(items)

# Assuming tests still pass without running them!
```

### Why It's Wrong

1. **Might break existing tests** - New validation might fail existing test cases
2. **No safety net** - Refactoring without green tests is dangerous
3. **Lost confidence** - Can't be sure refactoring is safe
4. **Introduces bugs** - Defensive code might have wrong logic

### ✅ Correct Approach

```python
# Verify all tests are GREEN before refactoring
# $ pytest tests/test_calculator.py -v
# PASSED test_should_return_sum_when_valid_inputs ✓
# ✅ All tests green, safe to refactor

# Refactor: Add defensive coding
def calculate_total(items: list[int] | None) -> int:
    """Calculate sum with validation."""
    if not items:
        raise ValueError("items required")
    return sum(items)

# Run tests IMMEDIATELY after refactoring
# $ pytest tests/test_calculator.py -v
# FAILED test_should_return_sum_when_valid_inputs
# AssertionError: ValueError: items required
# ❌ Refactoring broke test! (items=[1,2,3] is truthy, but "if not items" is too strict)

# Fix refactoring
def calculate_total(items: list[int] | None) -> int:
    """Calculate sum with validation."""
    if items is None or len(items) == 0:  # More precise check
        raise ValueError("items required")
    return sum(items)

# Run tests again
# $ pytest tests/test_calculator.py -v
# PASSED test_should_return_sum_when_valid_inputs ✓
# ✅ Refactoring successful
```

### Rule: REFACTOR phase checklist

1. ✅ All tests GREEN before starting
2. ✅ Make ONE refactoring change at a time
3. ✅ Run tests after EVERY change
4. ✅ If tests fail, REVERT or FIX immediately
5. ✅ Never commit with failing tests

---

## Violation 7: Testing Implementation Details Instead of Behavior

### ❌ What It Looks Like

```python
# WRONG: Testing internal implementation
def test_should_use_sum_function_internally():
    """Test that calculate_total uses Python's sum() function."""
    with patch('builtins.sum') as mock_sum:
        mock_sum.return_value = 6
        result = calculate_total([1, 2, 3])
        mock_sum.assert_called_once_with([1, 2, 3])
        assert result == 6
```

### Why It's Wrong

1. **Tightly coupled to implementation** - Can't refactor without breaking tests
2. **Tests don't specify behavior** - Tests verify "how", not "what"
3. **Brittle tests** - Break when implementation changes, even if behavior is correct
4. **Hinders refactoring** - Fear of breaking tests prevents improvements

### ✅ Correct Approach

```python
# Correct: Test behavior, not implementation
def test_should_return_sum_when_valid_inputs():
    """Test that calculate_total returns correct sum."""
    result = calculate_total([1, 2, 3])
    assert result == 6  # Only cares about output, not how it's computed

# This allows refactoring from sum() to manual loop without breaking test:
def calculate_total(items: list[int]) -> int:
    total = 0
    for item in items:
        total += item
    return total  # Different implementation, same behavior
```

### When to Test Implementation Details

**Only test implementation when it's part of the specification:**

```python
# If requirement is "must use ThreadPoolExecutor for parallel processing"
def test_should_use_thread_pool_for_parallel_processing():
    with patch('concurrent.futures.ThreadPoolExecutor') as mock_executor:
        process_batch(items, parallel=True)
        mock_executor.assert_called_once()
```

**Rule:** Test implementation ONLY if it's an explicit requirement, not just how you chose to implement it.

---

## Quick Reference: Common Violations

| Violation | Symptom | Fix |
|-----------|---------|-----|
| **Implementation First** | Code written before test | Write test FIRST, verify it fails |
| **Multiple Tests** | Many failing tests at once | ONE test at a time, RED→GREEN→REFACTOR |
| **Modifying Tests** | Changing test to match code | NEVER change test in GREEN; fix code instead |
| **Extra Features** | Code beyond current test | Minimal code only; new features need new tests |
| **Skipping Execution** | Not running test in RED | ALWAYS run test and verify failure reason |
| **Refactor Without Green** | Refactoring with failing tests | GREEN tests required before refactoring |
| **Testing Implementation** | Tests coupled to "how" | Test behavior (outputs), not implementation |

---

## Self-Assessment Questions

Before committing code, ask yourself:

1. ✅ Did I write the test BEFORE the implementation?
2. ✅ Did I verify the test FAILED for the right reason?
3. ✅ Did I write MINIMAL code to make the test pass?
4. ✅ Did I run tests AFTER implementation to verify they pass?
5. ✅ Did I add defensive coding during REFACTOR (not GREEN)?
6. ✅ Did I run tests AFTER refactoring to ensure they still pass?
7. ✅ Are my tests specifying BEHAVIOR, not implementation?
8. ✅ Did I work on ONE test at a time?

**If any answer is "No", you've violated TDD discipline.**

---

## See Also

- **Phase Rules**: `../references/phase-rules.md` for detailed RED/GREEN/REFACTOR rules
- **Good TDD Session**: `good-tdd-session.md` for real workflow example
- **Test Naming Guide**: `../references/test-naming-guide.md` for naming conventions
- **CLAUDE.md TDD Mode**: `../../CLAUDE.md` lines 33-115 for comprehensive workflow
