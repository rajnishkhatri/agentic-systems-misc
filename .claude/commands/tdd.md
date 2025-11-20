# /tdd Command

**Version:** 1.0.0
**Category:** Development Workflow Guidance
**Related Skill:** `.claude/skills/tdd-methodology/SKILL.md`

---

## Purpose

Provides phase-specific guidance and reminders for Test-Driven Development (TDD) workflow. This command is a **guidance tool** that displays best practices and recommendations when you invoke it manually.

**Key Distinction:**
- **This command** (`/tdd`): Manual guidance and reminders ("What should I do now?")
- **TDD Methodology Skill**: Automatic enforcement during development ("You must follow this rule")

The command helps you stay on track with TDD phases without blocking your actions.

---

## Usage

```
/tdd [phase]
```

### Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| phase | string | No | status | Phase to enter or query: `red`, `green`, `refactor`, `status` |

### Examples

```bash
# Enter RED phase (write failing test)
/tdd red

# Enter GREEN phase (minimal implementation)
/tdd green

# Enter REFACTOR phase (improve code quality)
/tdd refactor

# Check current phase and guidance
/tdd status
/tdd
```

---

## Commands

### /tdd red
**Purpose:** Enter RED phase - Write a failing test

**Guidance provided:**
- ✅ Write ONE failing test for single behavior
- ✅ Use naming convention: `test_should_[result]_when_[condition]()`
- ✅ Run test and confirm it fails with `pytest path/to/test.py::test_name -v`
- ❌ Do NOT write implementation code yet
- 💡 Focus on describing the expected behavior clearly

**Output format:**
```
🔴 RED Phase Active

Write a failing test for the next behavior.

Reminders:
✅ ONE failing test only
✅ Naming: test_should_[result]_when_[condition]()
✅ Run test to confirm it fails
❌ NO implementation code

Next step: Run pytest to verify failure → /tdd green
```

**Example workflow:**
```python
# RED phase: Write failing test
def test_should_sum_items_when_valid_list():
    assert calculate_total([1, 2, 3]) == 6
```

---

### /tdd green
**Purpose:** Enter GREEN phase - Write minimal code to pass test

**Guidance provided:**
- ✅ Write ONLY enough code to make the test pass
- ✅ No extra features or future-proofing
- ✅ Run test and confirm it passes with `pytest path/to/test.py::test_name -v`
- ❌ Do NOT modify the test
- 💡 Simplest implementation that works

**Output format:**
```
🟢 GREEN Phase Active

Write minimal code to make the test pass.

Reminders:
✅ Minimal code only (no extras)
✅ Run test to confirm it passes
❌ NO test modifications
❌ NO additional features

Next step: Run pytest to verify pass → /tdd refactor
```

**Example workflow:**
```python
# GREEN phase: Minimal implementation
def calculate_total(items: list[int]) -> int:
    return sum(items)  # Simplest solution
```

---

### /tdd refactor
**Purpose:** Enter REFACTOR phase - Improve code quality while keeping tests green

**Guidance provided:**
- ✅ Improve code quality (DRY, readability, performance)
- ✅ Apply defensive coding principles (see CLAUDE.md:65-115)
  - Add type hints
  - Add input validation
  - Add error handling
- ✅ Run tests after EACH change to ensure they still pass
- 💡 Keep tests passing throughout refactoring

**Output format:**
```
🔵 REFACTOR Phase Active

Improve code quality. Keep tests passing.

Reminders:
✅ Apply defensive coding (type hints, validation, error handling)
✅ Improve readability and DRY
✅ Run pytest after EACH change
✅ All tests must stay green

Defensive coding checklist:
  [ ] Type hints on all functions
  [ ] Input validation with guard clauses
  [ ] Specific exception handling
  [ ] Descriptive error messages

Next step: When done → /tdd red (next behavior)
```

**Example workflow:**
```python
# REFACTOR phase: Apply defensive coding
def calculate_total(items: list[int] | None) -> int:
    """Calculate sum of integer items.

    Args:
        items: List of integers to sum

    Returns:
        Sum of all items

    Raises:
        ValueError: If items is empty
        TypeError: If items contains non-integers
    """
    # Input validation
    if not items:
        raise ValueError("items cannot be empty")
    if not all(isinstance(x, int) for x in items):
        raise TypeError("all items must be integers")

    return sum(items)
```

---

### /tdd status
**Purpose:** Display current phase and phase-specific guidance

**Output format:**
```
📊 TDD Status

Current Phase: 🟢 GREEN
Last Updated: 2025-11-19 14:23:45

Phase Guidance:
Write minimal code to make the test pass.

Reminders:
✅ Minimal code only (no extras)
✅ Run test to confirm it passes
❌ NO test modifications
❌ NO additional features

Next step: Run pytest to verify pass → /tdd refactor

---

Phase History:
🔴 RED    → 14:20:15 (test_should_sum_items_when_valid_list)
🟢 GREEN  → 14:23:45 (current)

TDD Workflow: RED → GREEN → REFACTOR → RED (next behavior)
```

---

## Phase State Tracking

The command maintains a simple state file to track current phase and history:

**State file location:** `.claude/.tdd-state.json`

**State structure:**
```json
{
  "current_phase": "green",
  "last_updated": "2025-11-19T14:23:45Z",
  "history": [
    {
      "phase": "red",
      "timestamp": "2025-11-19T14:20:15Z",
      "test_name": "test_should_sum_items_when_valid_list"
    },
    {
      "phase": "green",
      "timestamp": "2025-11-19T14:23:45Z"
    }
  ]
}
```

**Note:** State is stored locally and resets when you start a new Claude Code session. This is intentional to keep the command lightweight and session-scoped.

---

## Integration with TDD Methodology Skill

**Command Role (Manual Guidance):**
- You invoke `/tdd [phase]` manually to get reminders
- Displays best practices and next steps
- Does NOT block or prevent actions
- Helps you remember TDD workflow

**Skill Role (Automatic Enforcement):**
- Activates automatically when you write tests or implement features
- Enforces TDD rules (blocks violations)
- Provides enforcement guidance ("You must write test first")
- See `.claude/skills/tdd-methodology/SKILL.md` for details

**When to use command vs. skill:**
- Use `/tdd [phase]` when you want to remind yourself of best practices
- Skill activates automatically when you say "write test", "implement function", etc.
- Both work together: command guides, skill enforces

---

## Best Practices

### 1. Start with /tdd red
When beginning a new feature, always start in RED phase:
```bash
/tdd red
# Write failing test
# Run pytest to verify failure
```

### 2. Use phase transitions sequentially
Follow the cycle strictly:
```bash
/tdd red      # Write failing test
/tdd green    # Minimal implementation
/tdd refactor # Improve quality
/tdd red      # Next behavior
```

### 3. Run tests at phase boundaries
Always verify test status when transitioning:
```bash
# End of RED phase
pytest path/to/test.py::test_name -v  # Should FAIL

# End of GREEN phase
pytest path/to/test.py::test_name -v  # Should PASS

# During REFACTOR phase
pytest path/to/test.py -v  # Should PASS after each change
```

### 4. Check status when resuming work
If you're resuming a TDD session:
```bash
/tdd status  # See current phase and guidance
```

---

## Common Scenarios

### Starting a new feature
```bash
/tdd red
# Write test: test_should_authenticate_user_when_valid_credentials()
pytest tests/test_auth.py::test_should_authenticate_user_when_valid_credentials -v
# Verify it fails
/tdd green
```

### Implementing the feature
```bash
# (In GREEN phase)
# Write minimal auth logic
pytest tests/test_auth.py::test_should_authenticate_user_when_valid_credentials -v
# Verify it passes
/tdd refactor
```

### Improving code quality
```bash
# (In REFACTOR phase)
# Add type hints
pytest tests/test_auth.py -v  # Verify still passing
# Add input validation
pytest tests/test_auth.py -v  # Verify still passing
# Add error handling
pytest tests/test_auth.py -v  # Verify still passing
/tdd red  # Ready for next behavior
```

### Checking progress mid-session
```bash
/tdd status
# See current phase, history, and next steps
```

---

## Troubleshooting

### "I'm not sure which phase I'm in"
```bash
/tdd status  # Check current phase and guidance
```

### "I accidentally skipped a phase"
No problem! The command provides guidance, not enforcement:
```bash
/tdd red  # Go back to RED phase
# Write the missing test
# Continue with proper cycle
```

### "The skill is blocking me but I want to continue"
The command and skill serve different purposes:
- **Skill enforcement is intentional** to maintain TDD discipline
- If you need to bypass temporarily, consider if TDD is appropriate for your task
- See `.claude/skills/tdd-methodology/SKILL.md` for skill behavior

### "How do I disable phase tracking?"
Phase tracking is session-scoped and lightweight:
- It resets when you start a new Claude Code session
- No need to disable; just don't use `/tdd` commands if not needed

---

## References

- **TDD Methodology Skill:** `.claude/skills/tdd-methodology/SKILL.md` (automatic enforcement)
- **CLAUDE.md TDD Mode:** CLAUDE.md:33-115 (comprehensive TDD workflow)
- **TDD Pattern:** `patterns/tdd-workflow.md` (detailed pattern template)
- **Phase Rules:** `.claude/skills/tdd-methodology/references/phase-rules.md`
- **Test Naming Guide:** `.claude/skills/tdd-methodology/references/test-naming-guide.md`
- **Good TDD Session Example:** `.claude/skills/tdd-methodology/examples/good-tdd-session.md`

---

## Version History

**1.0.0** (2025-11-19)
- Initial implementation
- Phase state tracking (red/green/refactor)
- Phase-specific guidance and reminders
- Integration with TDD Methodology Skill
- Session-scoped state management
