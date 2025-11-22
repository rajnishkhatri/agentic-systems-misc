---
name: tdd-methodology
description: Enforce Test-Driven Development workflow with RED→GREEN→REFACTOR phases and defensive coding principles
version: 1.0.0
activation_context:
  - write test
  - implement function
  - add feature
  - refactor
  - TDD
  - test-driven
  - failing test
  - make test pass
references:
  - references/phase-rules.md
  - references/test-naming-guide.md
  - examples/good-tdd-session.md
  - examples/common-violations.md
  - ../../CLAUDE.md#tdd-mode
---

# TDD Methodology Skill

## Purpose

This skill activates **automatically** during feature development to **enforce** Test-Driven Development (TDD) workflow, ensuring tests are written BEFORE implementation and the RED→GREEN→REFACTOR cycle is followed strictly.

**Key Distinction:**
- **This skill** (automatic enforcement): Blocks TDD violations during development ("You must write test first")
- **/tdd command** (manual guidance): Displays reminders when you invoke it ("What should I do now?")

See `.claude/commands/tdd.md` for manual guidance tool.

## When This Skill Activates

This skill **automatically activates** when you:
- Write tests for new features
- Implement functions or add features
- Refactor existing code
- Work in TDD mode explicitly
- Create failing tests or make tests pass

**Activation is automatic** based on conversation context (keywords like "write test", "implement function", etc.).

## Key Principles

### 1. RED → GREEN → REFACTOR Cycle

**RED Phase:**
- Write ONE failing test for single behavior
- Use naming convention: `test_should_[result]_when_[condition]()`
- Run test and confirm it fails
- ❌ NEVER write implementation code

**GREEN Phase:**
- Write ONLY enough code to make test pass
- No extra features or anticipation
- Run test and confirm it passes
- ❌ NEVER modify the test

**REFACTOR Phase:**
- Clean up code (DRY, readability, performance)
- Apply defensive coding principles
- Keep all tests passing
- Run tests after each change

See `references/phase-rules.md` for detailed constraints.

### 2. Test Naming Convention

Use pattern: `test_should_[expected_result]_when_[condition]()`

**Examples:**
- `test_should_detect_slow_query_when_exceeds_10s()`
- `test_should_raise_error_for_invalid_state_type()`
- `test_should_handle_empty_verses_list()`

See `references/test-naming-guide.md` for comprehensive guide.

### 3. Defensive Coding Integration

During REFACTOR phase, always apply:
- Type hints on ALL functions
- Input validation with guard clauses
- Specific exception handling (no bare `except:`)
- Descriptive error messages

See CLAUDE.md:65-115 for defensive coding standards.

## What This Skill Does

When activated, this skill will:

✅ **Enforce** RED→GREEN→REFACTOR phase discipline
✅ **Block** implementation before test exists
✅ **Block** test modifications during GREEN phase
✅ **Remind** to show test output at each step
✅ **Guide** test naming convention
✅ **Ensure** defensive coding during REFACTOR
✅ **Reference** good examples and common violations

## What This Skill Does NOT Do

❌ Replace manual testing or QA
❌ Generate tests automatically (you write them)
❌ Allow shortcuts or phase-skipping
❌ Override pytest or testing frameworks

## Strict Constraints

**NEVER:**
- ❌ Write code before test exists
- ❌ Write multiple tests at once
- ❌ Add code not required by current test
- ❌ Modify test and code together

**ALWAYS:**
- ✅ Ask for clarification if unclear
- ✅ Show test output at each step
- ✅ Run tests after every change
- ✅ Apply defensive coding in REFACTOR phase

## Integration with Other Tools

- **CLAUDE.md TDD Mode** (CLAUDE.md:33-115): Comprehensive TDD workflow including:
  - TDD Rules (RED/GREEN/REFACTOR phases)
  - Defensive Python requirements (type safety, validation, error handling)
  - Workflow commands and phase transitions
  - Example test-first implementation
- **/tdd command** (`.claude/commands/tdd.md`): Manual phase tracking and guidance
  - **Command role**: Displays best practices when you invoke `/tdd [phase]` manually
  - **Skill role**: Automatically enforces TDD rules and blocks violations
  - **Relationship**: Command guides ("What should I do?"), Skill enforces ("You must follow this")
- **Pattern Library (patterns/tdd-workflow.md)**: Detailed TDD pattern template with examples
- **pytest**: Test execution framework

## Quick Reference

**Starting new feature?**
1. **RED Phase**: Write failing test with `test_should_[result]_when_[condition]()` naming
2. Run test → Verify it fails
3. **GREEN Phase**: Write minimal code to pass test
4. Run test → Verify it passes
5. **REFACTOR Phase**: Apply defensive coding, improve quality
6. Run tests → Ensure all still pass
7. Repeat for next behavior

**Common Violations:** See `examples/common-violations.md`

**Good TDD Session Example:** See `examples/good-tdd-session.md`

**For detailed rules:** See CLAUDE.md:33-115 (TDD Mode section)
