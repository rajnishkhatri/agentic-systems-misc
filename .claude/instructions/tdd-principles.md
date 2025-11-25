# Extracted from CLAUDE.md - TDD & Defensive Coding Principles

## TDD Mode: RED → GREEN → REFACTOR

## You MUST follow Test-Driven Development strictly:

### TDD Rules:
**RED**: Write ONE failing test
- Create test for single behavior
- Naming: `test_should_[result]_when_[condition]`
- Run test and confirm it fails
- NEVER write implementation code

**GREEN**: Minimal code to pass
- Write ONLY enough code to make test pass
- No extra features or anticipation
- Run test and confirm it passes
- NEVER modify the test

**REFACTOR**: Improve with tests green
- Clean up code (DRY, readability, performance)
- always write defensive coding
- Keep all tests passing
- Run tests after each change

### Strict Constraints:
- ❌ NEVER write code before test exists
- ❌ NEVER write multiple tests at once
- ❌ NEVER add code not required by current test
- ❌ NEVER modify test and code together
- ✅ ASK for clarification if unclear
- ✅ SHOW test output at each step

## Defensive Python (MANDATORY):

### Type Safety:
- Type hints on ALL functions: `def func(x: int) -> str:`
- Use `list[T]`, `dict[K, V]`, `Optional[T]` or `T | None`
- Dataclasses or Pydantic for data structures

### Input Validation:
- Guard clauses at function start
- Check for `None`, empty collections, invalid ranges
- Raise descriptive exceptions: `ValueError`, `TypeError`

### Error Handling:
- ❌ NEVER use bare `except:`
- ✅ Catch specific exceptions: `except ValueError as e:`
- Log errors, don't silently fail
- Use context managers (`with`) for resources

### Example:
```python
# RED: Test first
def test_should_sum_items_when_valid_list():
    assert calculate_total([1, 2, 3]) == 6

def test_should_raise_when_empty_list():
    with pytest.raises(ValueError, match="items required"):
        calculate_total([])

# GREEN: Defensive implementation
def calculate_total(items: list[int] | None) -> int:
    if not items:
        raise ValueError("items required")
    if not all(isinstance(x, int) for x in items):
        raise TypeError("all items must be integers")
    return sum(items)

# REFACTOR: Keep it clean
```

### Workflow:
1. Human provides failing test (RED)
2. You implement minimal passing code (GREEN)
3. Together we refactor (REFACTOR)
4. Repeat for next feature

### Commands:
- Start: "TDD mode: RED phase. Ready for test."
- Verify: "Run test. Show output. No implementation."
- Implement: "GREEN phase. Make test pass minimally."
- Clean: "REFACTOR phase. Improve code, keep tests green."

Always state current phase before any action.

### Defensive Function Design Template:
All functions should follow this 5-step pattern for robustness:

```python
def function_name(arg: Type, optional: Type = default) -> ReturnType:
    """Brief description of what the function does.

    Args:
        arg: Description of argument
        optional: Description of optional argument

    Returns:
        Description of return value

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

**Example from Task 2.3** (`check_performance_alert` in `workflow.py:301-344`):
```python
def check_performance_alert(state: dict[str, Any], threshold: float = 10.0) -> dict[str, Any]:
    """Check if query exceeds performance threshold and identify bottleneck.

    Args:
        state: Workflow state with timing metrics
        threshold: Time threshold in seconds (default: 10.0)

    Returns:
        Alert dictionary with is_slow flag and details

    Raises:
        TypeError: If state is not a dict
        ValueError: If threshold is negative
    """
    # Step 1: Type checking
    if not isinstance(state, dict):
        raise TypeError("state must be a dict")
    if threshold < 0:
        raise ValueError("threshold must be non-negative")

    # Step 2: Get total time (with safe default)
    total_time = state.get("total_time", 0.0)

    # Step 3: Main logic
    is_slow = total_time > threshold
    alert = {
        "is_slow": is_slow,
        "threshold": threshold,
        "total_time": total_time,
    }

    if is_slow:
        alert["message"] = f"Query exceeded threshold ({total_time:.1f}s > {threshold}s)"
        timing = state.get("_metrics", {}).get("timing", {})
        if timing:
            slowest_agent = max(timing.items(), key=lambda x: x[1])
            alert["slowest_agent"] = slowest_agent[0]
            alert["slowest_time"] = slowest_agent[1]
    else:
        alert["message"] = f"Query completed within threshold ({total_time:.1f}s ≤ {threshold}s)"

    # Step 4: Return
    return alert
```

### Test Naming Convention:
Use the pattern `test_should_[result]_when_[condition]()` for clarity:

**Pattern**: `test_should_[expected_result]_when_[condition_or_input]()`

**Benefits**:
- Reads like a specification: "Test should [do what] when [under what circumstances]"
- Makes test intent immediately clear
- Groups related tests alphabetically
- Easy to identify missing test cases

**Examples from Task 2.3** (`test_chainlit_ui.py`):

```python
# Testing expected behavior
def test_should_detect_slow_query_when_exceeds_10s() -> None:
    """Test that queries over 10s trigger performance alert."""
    state = {"total_time": 12.5}
    alert = check_performance_alert(state)
    assert alert["is_slow"] is True

def test_should_not_alert_when_query_under_10s() -> None:
    """Test that fast queries don't trigger alert."""
    state = {"total_time": 7.3}
    alert = check_performance_alert(state)
    assert alert["is_slow"] is False

# Testing error conditions
def test_should_raise_error_for_invalid_state_type() -> None:
    """Test that invalid state type raises TypeError."""
    with pytest.raises(TypeError, match="state must be a dict"):
        check_performance_alert("not a dict")

def test_should_raise_error_for_negative_threshold() -> None:
    """Test that negative threshold raises ValueError."""
    state = {"total_time": 5.0}
    with pytest.raises(ValueError, match="threshold must be non-negative"):
        check_performance_alert(state, threshold=-1.0)

# Testing edge cases
def test_should_handle_empty_verses_list() -> None:
    """Test handling of empty retrieval results."""
    counts = calculate_source_counts([])
    assert counts["unique_verses"] == 0
    assert counts["total_chunks"] == 0

def test_should_handle_missing_total_time() -> None:
    """Test handling of state without total_time."""
    state = {}
    alert = check_performance_alert(state)
    assert alert["is_slow"] is False
    assert alert["total_time"] == 0.0
```

**Anti-patterns to avoid**:
- ❌ `test_performance()` - Too vague
- ❌ `test_1()` - No context
- ❌ `test_check_performance_alert_function()` - Describes implementation, not behavior
- ✅ `test_should_detect_slow_query_when_exceeds_10s()` - Clear expectation and condition
