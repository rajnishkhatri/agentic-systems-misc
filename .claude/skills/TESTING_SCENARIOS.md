# Skill Activation Testing Scenarios

This document provides test scenarios for validating skill activation behavior. Test each skill in isolation before enabling multiple skills.

## Testing Workflow

### Phase 1: Individual Skill Testing
1. Enable ONE skill at a time
2. Run activation test scenarios for that skill
3. Verify expected guidance is provided
4. Verify no unexpected activations occur
5. Move to next skill only after validation passes

### Phase 2: Integration Testing
1. Enable multiple skills simultaneously
2. Test multi-skill activation scenarios
3. Verify no conflicts or contradictory guidance
4. Test edge cases where multiple skills should activate

### Phase 3: Quality Validation
1. Run YAML validation on all SKILL.md files
2. Verify all reference paths exist
3. Verify all example files exist
4. Manual review for content duplication

## Test Scenario Template

```markdown
### Test: [Test Name]

**Skill Under Test:** [Skill Name]

**User Input:** "[Exact phrase user would say]"

**Expected Behavior:**
- ✅ Skill should activate: [Yes/No]
- ✅ Guidance provided: [What guidance should appear]
- ✅ References shown: [Which references should be linked]
- ✅ Examples provided: [Which examples should be shown]

**Actual Behavior:**
- [ ] Skill activated: [Yes/No]
- [ ] Correct guidance: [Yes/No/Partial]
- [ ] Correct references: [Yes/No/Missing]
- [ ] Correct examples: [Yes/No/Missing]

**Status:** [ ] Pass / [ ] Fail / [ ] Partial

**Notes:**
[Any observations, issues, or improvements needed]
```

---

## Tutorial Standards Skill - Test Scenarios

### Test 1.1: Create Tutorial Trigger

**Skill Under Test:** Tutorial Standards

**User Input:** "I need to create a tutorial for evaluation metrics"

**Expected Behavior:**
- ✅ Skill should activate: Yes
- ✅ Guidance provided: TUTORIAL_INDEX.md structure requirements
- ✅ References shown:
  - `CLAUDE.md#tutorial-workflow`
  - `.claude/skills/tutorial-standards/references/tutorial-index-template.md`
- ✅ Examples provided: `lesson-9/TUTORIAL_INDEX.md`

**Actual Behavior:**
- [ ] Skill activated: [Record Yes/No]
- [ ] Correct guidance: [Record Yes/No/Partial]
- [ ] Correct references: [Record Yes/No/Missing]
- [ ] Correct examples: [Record Yes/No/Missing]

**Status:** [ ] Pass / [ ] Fail / [ ] Partial

**Notes:**

---

### Test 1.2: Add Notebook Trigger

**Skill Under Test:** Tutorial Standards

**User Input:** "Add a notebook for perplexity calculation tutorial"

**Expected Behavior:**
- ✅ Skill should activate: Yes
- ✅ Guidance provided:
  - Setup cell requirements
  - Cost warning reminder
  - Execution time <5 minutes
  - Validation assertions
- ✅ References shown:
  - `.claude/skills/tutorial-standards/references/notebook-standards.md`

**Actual Behavior:**
- [ ] Skill activated: [Record Yes/No]
- [ ] Correct guidance: [Record Yes/No/Partial]
- [ ] Correct references: [Record Yes/No/Missing]

**Status:** [ ] Pass / [ ] Fail / [ ] Partial

**Notes:**

---

### Test 1.3: TUTORIAL_INDEX Mention

**Skill Under Test:** Tutorial Standards

**User Input:** "Check if TUTORIAL_INDEX has all required sections"

**Expected Behavior:**
- ✅ Skill should activate: Yes
- ✅ Guidance provided: Required sections list (objectives, prerequisites, learning paths, FAQs)
- ✅ References shown:
  - `.claude/skills/tutorial-standards/references/tutorial-index-template.md`
- ✅ Examples provided: `examples/lesson-9-tutorial-index.md`

**Actual Behavior:**
- [ ] Skill activated: [Record Yes/No]
- [ ] Correct guidance: [Record Yes/No/Partial]
- [ ] Correct references: [Record Yes/No/Missing]
- [ ] Correct examples: [Record Yes/No/Missing]

**Status:** [ ] Pass / [ ] Fail / [ ] Partial

**Notes:**

---

### Test 1.4: No Activation - Unrelated Query

**Skill Under Test:** Tutorial Standards

**User Input:** "Write a function to calculate perplexity"

**Expected Behavior:**
- ✅ Skill should activate: No
- ✅ Guidance provided: None (skill should not interfere)

**Actual Behavior:**
- [ ] Skill activated: [Record Yes/No]
- [ ] Correct behavior: [Record Yes/No]

**Status:** [ ] Pass / [ ] Fail

**Notes:**

---

## TDD Methodology Skill - Test Scenarios

### Test 2.1: Write Test Trigger

**Skill Under Test:** TDD Methodology

**User Input:** "Write test for the calculate_total function"

**Expected Behavior:**
- ✅ Skill should activate: Yes
- ✅ Guidance provided:
  - Entering RED phase
  - Test naming convention: `test_should_[result]_when_[condition]`
  - Reminder: No implementation code in RED phase
- ✅ References shown:
  - `CLAUDE.md#tdd-mode`
  - `.claude/skills/tdd-methodology/references/phase-rules.md`
  - `.claude/skills/tdd-methodology/references/test-naming-guide.md`

**Actual Behavior:**
- [ ] Skill activated: [Record Yes/No]
- [ ] Correct guidance: [Record Yes/No/Partial]
- [ ] Correct references: [Record Yes/No/Missing]

**Status:** [ ] Pass / [ ] Fail / [ ] Partial

**Notes:**

---

### Test 2.2: Implement Function Trigger

**Skill Under Test:** TDD Methodology

**User Input:** "Implement the calculate_total function to pass the test"

**Expected Behavior:**
- ✅ Skill should activate: Yes
- ✅ Guidance provided:
  - Entering GREEN phase
  - Write minimal code to pass test
  - Reminder: No test modifications in GREEN phase
- ✅ References shown:
  - `.claude/skills/tdd-methodology/references/phase-rules.md`

**Actual Behavior:**
- [ ] Skill activated: [Record Yes/No]
- [ ] Correct guidance: [Record Yes/No/Partial]
- [ ] Correct references: [Record Yes/No/Missing]

**Status:** [ ] Pass / [ ] Fail / [ ] Partial

**Notes:**

---

### Test 2.3: Refactor Code Trigger

**Skill Under Test:** TDD Methodology

**User Input:** "Refactor this code to use list comprehension"

**Expected Behavior:**
- ✅ Skill should activate: Yes
- ✅ Guidance provided:
  - Entering REFACTOR phase
  - Improve code quality while keeping tests green
  - Reminder: Run pytest after changes
- ✅ References shown:
  - `.claude/skills/tdd-methodology/references/phase-rules.md`

**Actual Behavior:**
- [ ] Skill activated: [Record Yes/No]
- [ ] Correct guidance: [Record Yes/No/Partial]
- [ ] Correct references: [Record Yes/No/Missing]

**Status:** [ ] Pass / [ ] Fail / [ ] Partial

**Notes:**

---

### Test 2.4: TDD Explicit Mention

**Skill Under Test:** TDD Methodology

**User Input:** "Use TDD workflow for this feature"

**Expected Behavior:**
- ✅ Skill should activate: Yes
- ✅ Guidance provided:
  - Complete TDD workflow overview
  - RED → GREEN → REFACTOR phases
- ✅ References shown:
  - `CLAUDE.md#tdd-mode`
  - `.claude/skills/tdd-methodology/examples/good-tdd-session.md`

**Actual Behavior:**
- [ ] Skill activated: [Record Yes/No]
- [ ] Correct guidance: [Record Yes/No/Partial]
- [ ] Correct references: [Record Yes/No/Missing]

**Status:** [ ] Pass / [ ] Fail / [ ] Partial

**Notes:**

---

### Test 2.5: Common Violation Detection

**Skill Under Test:** TDD Methodology

**User Input:** "Write the implementation first, then write tests"

**Expected Behavior:**
- ✅ Skill should activate: Yes
- ✅ Guidance provided:
  - Warning about TDD violation
  - Correct approach: test-first
- ✅ References shown:
  - `.claude/skills/tdd-methodology/examples/common-violations.md`

**Actual Behavior:**
- [ ] Skill activated: [Record Yes/No]
- [ ] Correct guidance: [Record Yes/No/Partial]
- [ ] Correct references: [Record Yes/No/Missing]

**Status:** [ ] Pass / [ ] Fail / [ ] Partial

**Notes:**

---

## Pattern Application Skill - Test Scenarios

### Test 3.1: Parallel Processing Trigger

**Skill Under Test:** Pattern Application

**User Input:** "I need to process 100 API calls in parallel"

**Expected Behavior:**
- ✅ Skill should activate: Yes
- ✅ Guidance provided:
  - Suggest ThreadPoolExecutor pattern
  - I/O-bound task identification
- ✅ References shown:
  - `patterns/threadpool-parallel.md`
  - `patterns/README.md`
- ✅ Examples provided: Real codebase examples with file:line references

**Actual Behavior:**
- [ ] Skill activated: [Record Yes/No]
- [ ] Correct guidance: [Record Yes/No/Partial]
- [ ] Correct references: [Record Yes/No/Missing]
- [ ] Correct examples: [Record Yes/No/Missing]

**Status:** [ ] Pass / [ ] Fail / [ ] Partial

**Notes:**

---

### Test 3.2: Batch Processing Trigger

**Skill Under Test:** Pattern Application

**User Input:** "Batch process these evaluation tasks"

**Expected Behavior:**
- ✅ Skill should activate: Yes
- ✅ Guidance provided:
  - Suggest ThreadPoolExecutor pattern for I/O-bound tasks
  - Pattern decision tree reference
- ✅ References shown:
  - `patterns/threadpool-parallel.md`
  - `.claude/skills/pattern-application/references/pattern-decision-tree.md`

**Actual Behavior:**
- [ ] Skill activated: [Record Yes/No]
- [ ] Correct guidance: [Record Yes/No/Partial]
- [ ] Correct references: [Record Yes/No/Missing]

**Status:** [ ] Pass / [ ] Fail / [ ] Partial

**Notes:**

---

### Test 3.3: Abstract Base Class Trigger

**Skill Under Test:** Pattern Application

**User Input:** "Create an abstract base class for evaluation metrics"

**Expected Behavior:**
- ✅ Skill should activate: Yes
- ✅ Guidance provided:
  - Suggest Abstract Base Class pattern
  - Framework/interface use case
- ✅ References shown:
  - `patterns/abstract-base-class.md`
  - `.claude/skills/pattern-application/references/integration-checklist.md`

**Actual Behavior:**
- [ ] Skill activated: [Record Yes/No]
- [ ] Correct guidance: [Record Yes/No/Partial]
- [ ] Correct references: [Record Yes/No/Missing]

**Status:** [ ] Pass / [ ] Fail / [ ] Partial

**Notes:**

---

### Test 3.4: Pattern List Request

**Skill Under Test:** Pattern Application

**User Input:** "What patterns are available?"

**Expected Behavior:**
- ✅ Skill should activate: Yes
- ✅ Guidance provided:
  - List all patterns from patterns/README.md
  - Complexity ratings
  - Use cases
- ✅ References shown:
  - `patterns/README.md`

**Actual Behavior:**
- [ ] Skill activated: [Record Yes/No]
- [ ] Correct guidance: [Record Yes/No/Partial]
- [ ] Correct references: [Record Yes/No/Missing]

**Status:** [ ] Pass / [ ] Fail / [ ] Partial

**Notes:**

---

## Integration Testing - Multi-Skill Scenarios

### Test 4.1: TDD + Pattern Application

**Skills Under Test:** TDD Methodology + Pattern Application

**User Input:** "Implement parallel processing for API calls using TDD"

**Expected Behavior:**
- ✅ Both skills should activate
- ✅ TDD skill provides: Test-first workflow guidance
- ✅ Pattern skill provides: ThreadPoolExecutor pattern reference
- ✅ No conflicts or contradictory guidance

**Actual Behavior:**
- [ ] TDD skill activated: [Record Yes/No]
- [ ] Pattern skill activated: [Record Yes/No]
- [ ] Guidance coherent: [Record Yes/No]
- [ ] No conflicts: [Record Yes/No]

**Status:** [ ] Pass / [ ] Fail / [ ] Partial

**Notes:**

---

### Test 4.2: Tutorial + TDD

**Skills Under Test:** Tutorial Standards + TDD Methodology

**User Input:** "Create a tutorial with notebook for testing perplexity calculation"

**Expected Behavior:**
- ✅ Both skills should activate
- ✅ Tutorial skill provides: Notebook standards, TUTORIAL_INDEX requirements
- ✅ TDD skill provides: Test-first approach for notebook validation
- ✅ No conflicts

**Actual Behavior:**
- [ ] Tutorial skill activated: [Record Yes/No]
- [ ] TDD skill activated: [Record Yes/No]
- [ ] Guidance coherent: [Record Yes/No]
- [ ] No conflicts: [Record Yes/No]

**Status:** [ ] Pass / [ ] Fail / [ ] Partial

**Notes:**

---

### Test 4.3: All Three Skills

**Skills Under Test:** Tutorial Standards + TDD Methodology + Pattern Application

**User Input:** "Create a tutorial that uses TDD to implement parallel batch processing"

**Expected Behavior:**
- ✅ All three skills should activate
- ✅ Tutorial skill: Tutorial structure guidance
- ✅ TDD skill: Test-first workflow
- ✅ Pattern skill: ThreadPoolExecutor pattern
- ✅ Guidance is coherent and complementary

**Actual Behavior:**
- [ ] Tutorial skill activated: [Record Yes/No]
- [ ] TDD skill activated: [Record Yes/No]
- [ ] Pattern skill activated: [Record Yes/No]
- [ ] Guidance coherent: [Record Yes/No]
- [ ] No conflicts: [Record Yes/No]

**Status:** [ ] Pass / [ ] Fail / [ ] Partial

**Notes:**

---

## Edge Cases & Negative Tests

### Test 5.1: Overlapping Keywords

**User Input:** "test the tutorial notebook"

**Expected Behavior:**
- ✅ Tutorial skill should activate (tutorial notebook context)
- ✅ TDD skill should NOT activate (no test writing context)

**Actual Behavior:**
- [ ] Tutorial skill activated: [Record Yes/No]
- [ ] TDD skill activated: [Record Yes/No]
- [ ] Correct discrimination: [Record Yes/No]

**Status:** [ ] Pass / [ ] Fail

**Notes:**

---

### Test 5.2: Missing References

**Test:** Validate all reference paths exist

**Expected Behavior:**
- ✅ All paths in SKILL.md references section exist
- ✅ No broken links

**Actual Behavior:**
- [ ] All references valid: [Record Yes/No]
- [ ] List broken paths: [List here]

**Status:** [ ] Pass / [ ] Fail

**Notes:**

---

### Test 5.3: YAML Validation

**Test:** Parse YAML frontmatter of all SKILL.md files

**Expected Behavior:**
- ✅ All YAML frontmatter is valid
- ✅ All required fields present
- ✅ Version follows semantic versioning

**Command:**
```bash
python -c "import yaml; yaml.safe_load(open('.claude/skills/tutorial-standards/SKILL.md').read().split('---')[1])"
```

**Actual Behavior:**
- [ ] YAML valid: [Record Yes/No]
- [ ] Required fields present: [Record Yes/No]
- [ ] Version format correct: [Record Yes/No]

**Status:** [ ] Pass / [ ] Fail

**Notes:**

---

## Test Execution Log

### Phase 1: Individual Skill Testing

| Skill | Date Tested | Tests Passed | Tests Failed | Status |
|-------|-------------|--------------|--------------|--------|
| Tutorial Standards | YYYY-MM-DD | 0/4 | 0/4 | Not Started |
| TDD Methodology | YYYY-MM-DD | 0/5 | 0/5 | Not Started |
| Pattern Application | YYYY-MM-DD | 0/4 | 0/4 | Not Started |

### Phase 2: Integration Testing

| Test Scenario | Date Tested | Status | Notes |
|---------------|-------------|--------|-------|
| TDD + Pattern | YYYY-MM-DD | Not Started | |
| Tutorial + TDD | YYYY-MM-DD | Not Started | |
| All Three Skills | YYYY-MM-DD | Not Started | |

### Phase 3: Quality Validation

| Check | Date | Status | Issues Found |
|-------|------|--------|--------------|
| YAML Validation | YYYY-MM-DD | Not Started | |
| Reference Paths | YYYY-MM-DD | Not Started | |
| Example Files | YYYY-MM-DD | Not Started | |
| Content Duplication Review | YYYY-MM-DD | Not Started | |

---

**Last Updated:** 2025-11-18
**Phase 1 Target:** All individual skill tests passing before integration testing
