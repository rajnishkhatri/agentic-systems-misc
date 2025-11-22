# Test Naming Convention Guide

## The Pattern: `test_should_[result]_when_[condition]()`

This naming convention makes test intent immediately clear and reads like a specification.

---

## Structure

```
test_should_[expected_result]_when_[condition_or_input]()
```

**Components:**
- `test_` - Required prefix for pytest/unittest discovery
- `should_` - Describes the expected behavior
- `[expected_result]` - What the function/method should do
- `when_` - Introduces the context or condition
- `[condition_or_input]` - The specific scenario being tested

---

## Benefits

### 1. Reads Like a Specification
Tests become self-documenting requirements:
- "Test should return sum when given valid inputs"
- "Test should raise error when given invalid type"
- "Test should handle empty list gracefully"

### 2. Groups Related Tests Alphabetically
Tests for the same function naturally cluster together in file listings:
```
test_should_calculate_total_when_valid_inputs()
test_should_handle_empty_list_when_no_items()
test_should_raise_error_when_invalid_type()
test_should_raise_error_when_negative_threshold()
```

### 3. Easy to Identify Missing Test Cases
Gaps in coverage become obvious:
- Have test for valid inputs? ✅
- Have test for empty inputs? ✅
- Have test for invalid types? ✅
- Have test for None input? ❌ Missing!

### 4. Improves Test Failure Messages
```
FAILED tests/test_calculator.py::test_should_return_sum_when_valid_inputs
```
vs.
```
FAILED tests/test_calculator.py::test_1
```

---

## Examples from Codebase

### Testing Expected Behavior

**Pattern:** Describe what should happen under normal conditions

```python
def test_should_detect_slow_query_when_exceeds_10s() -> None:
    """Test that queries over 10s trigger performance alert."""
    state = {"total_time": 12.5}
    alert = check_performance_alert(state)
    assert alert["is_slow"] is True
    assert alert["total_time"] == 12.5
```

**Pattern:** Describe what should NOT happen under specific conditions

```python
def test_should_not_alert_when_query_under_10s() -> None:
    """Test that fast queries don't trigger alert."""
    state = {"total_time": 7.3}
    alert = check_performance_alert(state)
    assert alert["is_slow"] is False
```

### Testing Error Conditions

**Pattern:** Focus on the error type and triggering condition

```python
def test_should_raise_error_for_invalid_state_type() -> None:
    """Test that invalid state type raises TypeError."""
    with pytest.raises(TypeError, match="state must be a dict"):
        check_performance_alert("not a dict")


def test_should_raise_error_for_negative_threshold() -> None:
    """Test that negative threshold raises ValueError."""
    state = {"total_time": 5.0}
    with pytest.raises(ValueError, match="threshold must be non-negative"):
        check_performance_alert(state, threshold=-1.0)
```

### Testing Edge Cases

**Pattern:** Describe the edge case scenario and expected handling

```python
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

### Testing Return Values

**Pattern:** Emphasize what value is returned under what condition

```python
def test_should_return_empty_list_when_no_matches() -> None:
    """Test that search returns empty list when no verses match."""
    results = search_verses("nonexistent_query")
    assert results == []


def test_should_return_sorted_results_when_multiple_matches() -> None:
    """Test that multiple matches are sorted by relevance score."""
    results = search_verses("dharma")
    assert len(results) > 1
    assert results[0]["score"] >= results[1]["score"]
```

### Testing State Changes

**Pattern:** Describe the state change and triggering action

```python
def test_should_increment_counter_when_query_processed() -> None:
    """Test that query counter increments after processing."""
    initial_count = get_query_count()
    process_query("test query")
    assert get_query_count() == initial_count + 1


def test_should_clear_cache_when_reset_called() -> None:
    """Test that cache is cleared after reset."""
    populate_cache(["item1", "item2"])
    reset_cache()
    assert get_cache_size() == 0
```

---

## Common Patterns by Test Type

### 1. Happy Path Tests
```python
test_should_[action]_when_[valid_input]()
test_should_return_[value]_when_[normal_condition]()
test_should_calculate_[result]_when_[expected_scenario]()
```

**Examples:**
- `test_should_return_sum_when_valid_inputs()`
- `test_should_retrieve_verse_when_valid_id()`
- `test_should_calculate_score_when_matching_keywords()`

### 2. Error Handling Tests
```python
test_should_raise_[error_type]_when_[invalid_input]()
test_should_raise_error_for_[condition]()
```

**Examples:**
- `test_should_raise_ValueError_when_empty_list()`
- `test_should_raise_TypeError_when_invalid_type()`
- `test_should_raise_error_for_negative_threshold()`

### 3. Edge Case Tests
```python
test_should_handle_[edge_case]_when_[condition]()
test_should_return_[default]_when_[boundary_condition]()
```

**Examples:**
- `test_should_handle_empty_list_when_no_items()`
- `test_should_return_zero_when_all_items_negative()`
- `test_should_handle_unicode_when_special_characters()`

### 4. Boundary Tests
```python
test_should_[action]_when_at_[boundary]()
test_should_[behavior]_when_exactly_[threshold]()
```

**Examples:**
- `test_should_pass_when_at_max_length()`
- `test_should_trigger_alert_when_exactly_10s()`
- `test_should_accept_when_at_minimum_value()`

### 5. Integration Tests
```python
test_should_[end_to_end_behavior]_when_[workflow_condition]()
```

**Examples:**
- `test_should_complete_workflow_when_all_agents_succeed()`
- `test_should_fallback_to_cache_when_api_fails()`
- `test_should_retry_request_when_timeout_occurs()`

---

## Anti-Patterns to Avoid

### ❌ Too Vague
```python
def test_performance():  # What aspect of performance?
def test_error():        # What error, what condition?
def test_feature():      # What feature, what behavior?
```

### ❌ Numbered Tests
```python
def test_1():  # No context about what is tested
def test_2():
def test_3():
```

### ❌ Implementation-Focused Names
```python
def test_check_performance_alert_function():  # Describes code, not behavior
def test_calculate_total_implementation():
def test_class_method():
```

### ❌ Missing Context
```python
def test_returns_sum():        # When does it return sum?
def test_raises_error():       # What error, what condition?
def test_handles_empty():      # Handles how?
```

### ✅ Good Names (Using Convention)
```python
def test_should_return_sum_when_valid_inputs():
def test_should_raise_ValueError_when_empty_list():
def test_should_handle_empty_list_when_no_items():
```

---

## Variations and Flexibility

While the core pattern is `test_should_[result]_when_[condition]()`, you can adapt it slightly for readability:

### Alternative: `test_should_[result]_for_[input]`
```python
def test_should_raise_error_for_invalid_state_type()  # Slightly more concise
def test_should_return_zero_for_empty_list()
```

### Alternative: `test_should_[result]_given_[precondition]`
```python
def test_should_succeed_given_valid_credentials()
def test_should_fail_given_expired_token()
```

### Negative Form: `test_should_not_[action]_when_[condition]`
```python
def test_should_not_alert_when_query_under_10s()
def test_should_not_modify_original_list_when_sorting()
```

**Key principle:** Prioritize clarity over strict adherence. If a variation makes the test intent clearer, use it.

---

## Docstring Integration

Always pair the descriptive name with a concise docstring:

```python
def test_should_detect_slow_query_when_exceeds_10s() -> None:
    """Test that queries over 10s trigger performance alert.

    Verifies that check_performance_alert correctly identifies
    slow queries and includes relevant timing information.
    """
    state = {"total_time": 12.5}
    alert = check_performance_alert(state)
    assert alert["is_slow"] is True
```

**Guideline:**
- Test name = One-line specification
- Docstring = Brief explanation of why this test matters

---

## Test Organization Example

```python
# tests/test_calculator.py

class TestCalculateTotal:
    """Test suite for calculate_total function."""

    # Happy path tests
    def test_should_return_sum_when_valid_inputs(self) -> None:
        """Test basic sum calculation with valid integers."""
        assert calculate_total([1, 2, 3]) == 6

    def test_should_return_zero_when_single_zero(self) -> None:
        """Test that single zero input returns zero."""
        assert calculate_total([0]) == 0

    # Error condition tests
    def test_should_raise_ValueError_when_empty_list(self) -> None:
        """Test that empty list raises ValueError."""
        with pytest.raises(ValueError, match="items required"):
            calculate_total([])

    def test_should_raise_TypeError_when_invalid_type(self) -> None:
        """Test that non-integer items raise TypeError."""
        with pytest.raises(TypeError, match="all items must be integers"):
            calculate_total([1, "2", 3])

    # Edge case tests
    def test_should_handle_negative_numbers_when_present(self) -> None:
        """Test sum calculation with negative integers."""
        assert calculate_total([-1, -2, -3]) == -6

    def test_should_handle_large_numbers_when_valid(self) -> None:
        """Test sum calculation with large integers."""
        assert calculate_total([10**6, 10**6]) == 2 * 10**6
```

**Benefits of this organization:**
- Tests group by category (happy path, errors, edge cases)
- Clear progression from simple to complex scenarios
- Easy to identify missing test coverage
- Test names describe complete specifications

---

## Quick Reference

| Test Type | Pattern | Example |
|-----------|---------|---------|
| Happy Path | `test_should_[action]_when_[valid_input]()` | `test_should_return_sum_when_valid_inputs()` |
| Error Handling | `test_should_raise_[error]_when_[invalid]()` | `test_should_raise_ValueError_when_empty()` |
| Edge Case | `test_should_handle_[case]_when_[condition]()` | `test_should_handle_None_when_optional()` |
| Boundary | `test_should_[action]_when_at_[boundary]()` | `test_should_pass_when_at_max_length()` |
| Negative | `test_should_not_[action]_when_[condition]()` | `test_should_not_modify_when_readonly()` |

---

## See Also

- **Phase Rules**: `phase-rules.md` for RED/GREEN/REFACTOR constraints
- **Good TDD Session**: `../examples/good-tdd-session.md` for real workflow with proper naming
- **CLAUDE.md TDD Mode**: `../../CLAUDE.md` lines 33-115 for complete TDD workflow
- **Pattern Library**: `/patterns/tdd-workflow.md` for TDD pattern template
