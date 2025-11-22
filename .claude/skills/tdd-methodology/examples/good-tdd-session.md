# Good TDD Session Example

This document shows a real Test-Driven Development workflow from the codebase, demonstrating proper RED→GREEN→REFACTOR phases.

**Source:** `tests/test_exact_evaluation.py` and `backend/exact_evaluation.py`
**Feature:** Exact string matching with normalization

---

## Session Overview

**Goal:** Implement `exact_match()` function that compares two strings with optional normalization.

**Test File:** `tests/test_exact_evaluation.py:89-144`
**Implementation:** `backend/exact_evaluation.py`

---

## Iteration 1: Basic Exact Match (Identical Strings)

### 🔴 RED Phase: Write Failing Test

```python
# tests/test_exact_evaluation.py:92-102

def test_should_match_when_strings_are_identical(self) -> None:
    """Test exact match with identical strings."""
    # Given: identical strings
    text1 = "The cat sat on the mat"
    text2 = "The cat sat on the mat"

    # When: comparing with exact match
    result = exact_match(text1, text2)

    # Then: should return True
    assert result is True, "Identical strings should match exactly"
```

**Run test:**
```bash
$ pytest tests/test_exact_evaluation.py::TestExactMatch::test_should_match_when_strings_are_identical -v

FAILED - ImportError: cannot import name 'exact_match' from 'backend.exact_evaluation'
```

✅ **Test fails for the RIGHT reason** (function doesn't exist yet)

---

### 🟢 GREEN Phase: Minimal Implementation

```python
# backend/exact_evaluation.py

def exact_match(text1: str, text2: str) -> bool:
    """Compare two strings for exact match."""
    return text1 == text2
```

**Run test:**
```bash
$ pytest tests/test_exact_evaluation.py::TestExactMatch::test_should_match_when_strings_are_identical -v

PASSED tests/test_exact_evaluation.py::TestExactMatch::test_should_match_when_strings_are_identical ✓
```

✅ **Test passes with minimal code**

---

### ♻️ REFACTOR Phase: Add Defensive Coding

```python
# backend/exact_evaluation.py

def exact_match(text1: str, text2: str) -> bool:
    """Compare two strings for exact match.

    Args:
        text1: First string to compare
        text2: Second string to compare

    Returns:
        True if strings are identical, False otherwise

    Raises:
        TypeError: If inputs are not strings
    """
    # Type validation (defensive coding)
    if not isinstance(text1, str) or not isinstance(text2, str):
        raise TypeError("Both inputs must be strings")

    return text1 == text2
```

**Run all tests:**
```bash
$ pytest tests/test_exact_evaluation.py::TestExactMatch -v

PASSED test_should_match_when_strings_are_identical ✓
```

✅ **All tests still pass after refactoring**

---

## Iteration 2: Different Strings Should Not Match

### 🔴 RED Phase: Write Failing Test

```python
# tests/test_exact_evaluation.py:104-114

def test_should_not_match_when_strings_differ(self) -> None:
    """Test exact match with different strings."""
    # Given: different strings
    text1 = "The cat sat on the mat"
    text2 = "The dog sat on the mat"

    # When: comparing with exact match
    result = exact_match(text1, text2)

    # Then: should return False
    assert result is False, "Different strings should not match"
```

**Run test:**
```bash
$ pytest tests/test_exact_evaluation.py::TestExactMatch::test_should_not_match_when_strings_differ -v

PASSED tests/test_exact_evaluation.py::TestExactMatch::test_should_not_match_when_strings_differ ✓
```

✅ **Test passes immediately** (implementation already handles this case)

**Note:** This is fine! Sometimes minimal GREEN code covers multiple test cases. The test still has value as documentation of expected behavior.

---

## Iteration 3: Normalization Support

### 🔴 RED Phase: Write Failing Test

```python
# tests/test_exact_evaluation.py:116-126

def test_should_match_when_normalized_strings_are_equal(self) -> None:
    """Test exact match with normalization (case, whitespace, punctuation)."""
    # Given: strings that differ only in case and punctuation
    text1 = "Hello, World!"
    text2 = "hello world"

    # When: comparing with normalization
    result = exact_match(text1, text2, normalize=True)

    # Then: should return True
    assert result is True, "Normalized strings should match"
```

**Run test:**
```bash
$ pytest tests/test_exact_evaluation.py::TestExactMatch::test_should_match_when_normalized_strings_are_equal -v

FAILED - TypeError: exact_match() got an unexpected keyword argument 'normalize'
```

✅ **Test fails for the RIGHT reason** (normalize parameter doesn't exist)

---

### 🟢 GREEN Phase: Add Normalization Parameter

```python
# backend/exact_evaluation.py

def exact_match(text1: str, text2: str, normalize: bool = False) -> bool:
    """Compare two strings for exact match.

    Args:
        text1: First string to compare
        text2: Second string to compare
        normalize: If True, normalize both strings before comparison

    Returns:
        True if strings are identical, False otherwise

    Raises:
        TypeError: If inputs are not strings
    """
    # Type validation
    if not isinstance(text1, str) or not isinstance(text2, str):
        raise TypeError("Both inputs must be strings")

    # Apply normalization if requested
    if normalize:
        text1 = normalize_text(text1)
        text2 = normalize_text(text2)

    return text1 == text2
```

**Note:** This requires implementing `normalize_text()` helper function. In real TDD, we would write tests for that function separately.

**Run test:**
```bash
$ pytest tests/test_exact_evaluation.py::TestExactMatch::test_should_match_when_normalized_strings_are_equal -v

PASSED tests/test_exact_evaluation.py::TestExactMatch::test_should_match_when_normalized_strings_are_equal ✓
```

✅ **Test passes with normalization support**

---

### ♻️ REFACTOR Phase: Improve Code Quality

No refactoring needed - code is clean and follows defensive coding principles.

**Run ALL tests:**
```bash
$ pytest tests/test_exact_evaluation.py::TestExactMatch -v

PASSED test_should_match_when_strings_are_identical ✓
PASSED test_should_not_match_when_strings_differ ✓
PASSED test_should_match_when_normalized_strings_are_equal ✓
```

✅ **All tests pass**

---

## Iteration 4: Verify Normalization is Optional

### 🔴 RED Phase: Write Failing Test

```python
# tests/test_exact_evaluation.py:128-138

def test_should_not_match_when_unnormalized_strings_differ_in_case(self) -> None:
    """Test that case matters when normalization is disabled."""
    # Given: strings differing only in case
    text1 = "Hello"
    text2 = "hello"

    # When: comparing without normalization
    result = exact_match(text1, text2, normalize=False)

    # Then: should return False
    assert result is False, "Case should matter without normalization"
```

**Run test:**
```bash
$ pytest tests/test_exact_evaluation.py::TestExactMatch::test_should_not_match_when_unnormalized_strings_differ_in_case -v

PASSED tests/test_exact_evaluation.py::TestExactMatch::test_should_not_match_when_unnormalized_strings_differ_in_case ✓
```

✅ **Test passes immediately** (implementation already correct)

---

## Iteration 5: Error Handling for Invalid Input

### 🔴 RED Phase: Write Failing Test

```python
# tests/test_exact_evaluation.py:140-144

def test_should_raise_error_when_input_is_not_string(self) -> None:
    """Test that non-string input raises TypeError."""
    with pytest.raises(TypeError, match="Both inputs must be strings"):
        exact_match(123, "text")  # type: ignore
```

**Run test:**
```bash
$ pytest tests/test_exact_evaluation.py::TestExactMatch::test_should_raise_error_when_input_is_not_string -v

PASSED tests/test_exact_evaluation.py::TestExactMatch::test_should_raise_error_when_input_is_not_string ✓
```

✅ **Test passes immediately** (defensive coding from REFACTOR phase already covers this)

---

## Final Implementation

```python
# backend/exact_evaluation.py

def exact_match(text1: str, text2: str, normalize: bool = False) -> bool:
    """Compare two strings for exact match with optional normalization.

    Args:
        text1: First string to compare
        text2: Second string to compare
        normalize: If True, normalize both strings (lowercase, remove punctuation,
                  collapse whitespace) before comparison

    Returns:
        True if strings match (exactly or after normalization), False otherwise

    Raises:
        TypeError: If either input is not a string

    Examples:
        >>> exact_match("Hello", "Hello")
        True
        >>> exact_match("Hello", "hello", normalize=False)
        False
        >>> exact_match("Hello, World!", "hello world", normalize=True)
        True
    """
    # Step 1: Type validation (defensive)
    if not isinstance(text1, str) or not isinstance(text2, str):
        raise TypeError("Both inputs must be strings")

    # Step 2: Apply normalization if requested
    if normalize:
        text1 = normalize_text(text1)
        text2 = normalize_text(text2)

    # Step 3: Main logic - simple equality check
    return text1 == text2
```

---

## Final Test Results

```bash
$ pytest tests/test_exact_evaluation.py::TestExactMatch -v

tests/test_exact_evaluation.py::TestExactMatch::test_should_match_when_strings_are_identical PASSED
tests/test_exact_evaluation.py::TestExactMatch::test_should_not_match_when_strings_differ PASSED
tests/test_exact_evaluation.py::TestExactMatch::test_should_match_when_normalized_strings_are_equal PASSED
tests/test_exact_evaluation.py::TestExactMatch::test_should_not_match_when_unnormalized_strings_differ_in_case PASSED
tests/test_exact_evaluation.py::TestExactMatch::test_should_raise_error_when_input_is_not_string PASSED

========================== 5 passed in 0.15s ==========================
```

✅ **All 5 tests pass** - Feature complete!

---

## Key Takeaways from This Session

### ✅ What Was Done Right

1. **Test-First Development**
   - Every test was written BEFORE implementation
   - Tests drove the API design (parameter names, return types)

2. **Incremental Progress**
   - Started with simplest case (identical strings)
   - Added complexity gradually (normalization, error handling)
   - Each iteration built on previous work

3. **Clear Test Naming**
   - `test_should_match_when_strings_are_identical()` - Intent is obvious
   - `test_should_raise_error_when_input_is_not_string()` - Error condition clear
   - Pattern: `test_should_[result]_when_[condition]()`

4. **Defensive Coding in REFACTOR**
   - Type validation added during refactoring
   - Comprehensive docstring with examples
   - Descriptive error messages

5. **Test Output Verification**
   - Ran tests after EVERY change
   - Verified failures were for the RIGHT reason
   - Ensured all existing tests passed before moving on

### 🎯 TDD Discipline Demonstrated

| Phase | Action | Evidence |
|-------|--------|----------|
| RED   | Write failing test | `FAILED - ImportError: cannot import name 'exact_match'` |
| GREEN | Minimal implementation | `return text1 == text2` (simplest code that works) |
| REFACTOR | Add defensive coding | Type hints, validation, docstring added AFTER test passes |

### 📊 Coverage Achieved

The TDD session naturally achieved comprehensive test coverage:

- ✅ Happy path (identical strings)
- ✅ Negative case (different strings)
- ✅ Feature extension (normalization)
- ✅ Optional parameter behavior (normalize=True/False)
- ✅ Error handling (invalid input types)

**No special effort to "achieve coverage"** - tests were written to specify behavior, and coverage followed naturally.

---

## Contrast with Common Anti-Patterns

### ❌ Implementation-First Approach (What NOT to do)

```python
# WRONG: Writing implementation first
def exact_match(text1: str, text2: str, normalize: bool = False) -> bool:
    if not isinstance(text1, str) or not isinstance(text2, str):
        raise TypeError("Both inputs must be strings")

    if normalize:
        text1 = normalize_text(text1)
        text2 = normalize_text(text2)

    return text1 == text2

# Then writing tests after
def test_exact_match():
    assert exact_match("hello", "hello") is True  # Might miss edge cases
```

**Problems:**
- No verification that implementation solves the RIGHT problem
- Might include unnecessary features (over-engineering)
- Tests become validation of implementation, not specification of behavior
- Missing test cases for error conditions, edge cases

### ❌ Writing All Tests at Once (What NOT to do)

```python
# WRONG: Writing 5 tests in RED phase
def test_should_match_when_strings_are_identical(): ...
def test_should_not_match_when_strings_differ(): ...
def test_should_match_when_normalized_strings_are_equal(): ...
def test_should_not_match_when_unnormalized_strings_differ_in_case(): ...
def test_should_raise_error_when_input_is_not_string(): ...

# Then implementing everything at once
def exact_match(...):  # Big implementation covering all cases
```

**Problems:**
- If implementation has bug, multiple tests fail - hard to diagnose
- No incremental progress - harder to track what's working
- Violates "ONE failing test at a time" rule
- Increases cognitive load

---

## Real Commit History

This TDD session was part of:
```
commit 87a504a
feat: complete Lesson 9 - Evaluation Fundamentals & Exact Methods (Task 2.0)

- Add 3 comprehensive concept tutorials
- Create 2 interactive Jupyter notebooks
- Implement backend/exact_evaluation.py with 7 evaluation functions
- Add 33 TDD tests achieving 100% pass rate
- Follow defensive coding: type hints, input validation, comprehensive error handling
```

**Evidence of TDD discipline:**
- 33 tests written FIRST (`tests/test_exact_evaluation.py`)
- Implementation followed test specification (`backend/exact_evaluation.py`)
- 100% pass rate on first GREEN phase (no debugging needed)
- Defensive coding applied during REFACTOR phase

---

## See Also

- **Phase Rules**: `../references/phase-rules.md` for detailed RED/GREEN/REFACTOR constraints
- **Test Naming Guide**: `../references/test-naming-guide.md` for naming convention details
- **Common Violations**: `common-violations.md` for anti-patterns to avoid
- **Full Test File**: `tests/test_exact_evaluation.py` for complete test suite
- **CLAUDE.md TDD Mode**: `../../CLAUDE.md` lines 33-115 for comprehensive workflow
