# PRD: Logical Fallacies Tutorial System - Stabilization

**Document ID:** 0019-prd-logical-fallacies-stabilization.md
**Parent PRD:** 0018-prd-logical-fallacies-tutorial-system.md
**Status:** Draft
**Created:** 2025-12-23

---

## 1. Introduction/Overview

This PRD addresses critical gaps discovered during the post-implementation reflection of Task 0018 (Logical Fallacies Tutorial System). The primary issues are:

1. **Empty Jupyter notebooks** - Both notebooks are shell files with zero cells
2. **Failing integration tests** - 6/14 tests fail due to brittle relative path resolution

This is a stabilization/bug-fix PRD, not a new feature PRD.

---

## 2. Problem Understanding

### Restated Problem
Task 0018 was marked complete, but two key deliverables are non-functional:
- Notebooks `01_fallacy_detection.ipynb` and `02_grounded_fallacy_detection.ipynb` contain no cells (119 bytes each)
- Integration tests in `test_integration_data.py` fail when run from project root due to hardcoded relative paths

### Key Constraints
- Must use existing JSON data files (verified present in `data/`)
- Must use existing Python generators (8/14 tests already pass)
- Notebooks must execute in <3 minutes total
- No new features - stabilization only

### Assumptions
- The existing generators (`fallacy_example_generator.py`, `phase_data_generators.py`, `pattern_antipattern_generator.py`) work correctly (unit tests pass)
- Tutorial markdown content in `tutorials/01_cherry_picked_benchmarks/` is complete and can be referenced

### Success Criteria
1. Both notebooks contain cells per Tasks 6.1-6.7
2. `jupyter nbconvert --execute` succeeds for both notebooks
3. All 14 tests pass when run from project root
4. Code coverage ≥90%

---

## 3. Goals

| Goal | Measurable Target |
|------|-------------------|
| Notebooks functional | 2/2 notebooks execute without error |
| Tests passing | 14/14 tests pass |
| Coverage restored | ≥90% line coverage |
| Execution time | <3 minutes total for both notebooks |

---

## 4. Strategic Approach

### Chosen Strategy: Decomposition + Working Backward

**Rationale:**
- Tasks 6.1-6.7 already specify exact cell requirements - work backward from these specs
- Two independent work streams (notebooks, tests) can be decomposed and tackled in priority order

### Major Phases
1. **Phase 1:** Implement Notebook 01 (theory/concepts)
2. **Phase 2:** Implement Notebook 02 (hands-on exercises)
3. **Phase 3:** Fix integration test paths
4. **Phase 4:** Validate all success criteria

### Recommended Implementation Heuristics
- **Working Backward:** Start from Task 6.x requirements, trace to implementation
- **Simplification:** Use static/cached data to meet <3 min execution constraint

---

## 5. User Stories

**US-1:** As a tutorial learner, I want to run `01_fallacy_detection.ipynb` so that I can understand cherry-picking concepts interactively.

**US-2:** As a tutorial learner, I want to run `02_grounded_fallacy_detection.ipynb` so that I can practice detecting cherry-picked benchmarks with real dispute data.

**US-3:** As a developer, I want all tests to pass when I run `pytest` from the project root so that CI/CD pipelines work correctly.

---

## 6. Functional Requirements

### FR-1: Notebook 01 - Introduction and Core Concepts (Task 6.1)

| Req ID | Requirement |
|--------|-------------|
| FR-1.1 | Create markdown cell with title and learning objectives |
| FR-1.2 | Create markdown cell explaining cherry-picked benchmarks definition |
| FR-1.3 | Create markdown cell with real-world example (Google Gemini demo) |
| FR-1.4 | Create markdown cell with dispute domain scenario |
| FR-1.5 | Create markdown cell with red flags checklist |
| FR-1.6 | Notebook executes without error in <1 minute |

### FR-2: Notebook 02 - Hands-On Exercises (Tasks 6.2-6.7)

| Req ID | Requirement | Source Task |
|--------|-------------|-------------|
| FR-2.1 | Cell 1: Load dispute data from JSON files with validation | Task 6.2 |
| FR-2.2 | Cell 2: Generate cherry-picked vs. full test sets using generator | Task 6.3 |
| FR-2.3 | Cell 3: Annotate fallacy red flags in generated example | Task 6.4 |
| FR-2.4 | Cell 4: Calculate accuracy, confusion matrix, per-category metrics | Task 6.5 |
| FR-2.5 | Cell 5: Compare to HW3 stratified sampling method | Task 6.6 |
| FR-2.6 | Setup cell at top with cost warnings and validation assertions | Task 6.7 |
| FR-2.7 | Notebook executes without error in <2 minutes | Task 6.8 |

### FR-3: Integration Test Path Fix

| Req ID | Requirement |
|--------|-------------|
| FR-3.1 | Update `test_integration_data.py` to use `Path(__file__).resolve()` for path resolution |
| FR-3.2 | All 6 currently failing tests pass |
| FR-3.3 | Tests work when run from any directory |

---

## 7. Non-Goals (Out of Scope)

- New features from REFLECTION_NOTES.md (GlossaryTooltip, interactive sliders)
- CI/CD pipeline additions
- React component changes
- Additional fallacy types beyond Cherry-Picked Benchmarks
- Tutorial markdown content changes

---

## 8. Design Considerations

### Notebook Structure

**Notebook 01 Layout:**
```
[1] Markdown: Title + Learning Objectives
[2] Markdown: Definition of Cherry-Picked Benchmarks
[3] Markdown: Real-World Example (Gemini Demo)
[4] Markdown: Dispute Domain Scenario
[5] Markdown: Red Flags Checklist
```

**Notebook 02 Layout:**
```
[1] Code: Setup (imports, warnings, assertions)
[2] Code: Load dispute data (classification_labels.json)
[3] Code: Generate cherry-picked vs. full sets
[4] Code: Annotate red flags
[5] Code: Calculate metrics (accuracy, confusion matrix)
[6] Code: Compare to HW3 method
[7] Markdown: Summary and next steps
```

---

## 9. Technical Considerations

### Dependencies
- `json` (stdlib)
- `pathlib` (stdlib)
- `collections` (stdlib for Counter)
- Existing generators in `generators/` directory

### Data Files Required
- `data/fallacies-data.json` (verified exists)
- `data/dispute-grounding.json` (verified exists)
- `data/patterns-anti-patterns.json` (verified exists)
- `data/polya-phases.json` (verified exists)
- `data/hw-counter-methods.json` (verified exists)

### Recommended Implementation Strategy

**Strategy:** Working Backward
- **Why it applies:** Task 6.x requirements are explicit specifications
- **Suggested approach:** Map each FR directly to a cell, implement minimally
- **Watch for:** Over-engineering cells beyond task requirements

### Path Resolution Fix Pattern
```python
# Before (brittle):
DATA_DIR = Path("lesson-18/interactive/logical-fallacies/data")

# After (robust):
DATA_DIR = Path(__file__).resolve().parent.parent / "data"
```

---

## 10. Success Metrics

| Metric | Target | Validation Command |
|--------|--------|-------------------|
| Notebook 01 executes | 0 errors | `jupyter nbconvert --execute 01_fallacy_detection.ipynb` |
| Notebook 02 executes | 0 errors | `jupyter nbconvert --execute 02_grounded_fallacy_detection.ipynb` |
| Total execution time | <3 min | `time jupyter nbconvert --execute *.ipynb` |
| Test pass rate | 14/14 | `uv run pytest generators/tests/ -v` |
| Code coverage | ≥90% | `uv run pytest generators/tests/ --cov` |

---

## 11. Validation Checkpoints

### Checkpoint 1: Notebook 01 Complete
- [ ] 4-5 markdown cells created
- [ ] Executes without error
- [ ] Content aligns with `tutorials/01_cherry_picked_benchmarks/01_understand.md`

### Checkpoint 2: Notebook 02 Complete
- [ ] 6-7 cells created (1 setup + 5 exercise + 1 summary)
- [ ] Loads data successfully
- [ ] Generates cherry-picked examples
- [ ] Calculates metrics
- [ ] Executes in <2 minutes

### Checkpoint 3: Tests Fixed
- [ ] Path resolution updated
- [ ] 14/14 tests pass
- [ ] ≥90% coverage

### Checkpoint 4: Final Validation
- [ ] Both notebooks execute from project root
- [ ] All tests pass from project root
- [ ] Task 0018 tasks list updated to reflect true completion

---

## 12. Open Questions

None - requirements are well-defined from Task 0018.

---

## Summary

| Aspect | Details |
|--------|---------|
| **Effort** | ~2-3 hours |
| **Priority** | Notebooks first, then tests |
| **Risk** | Low - isolated fixes using existing components |
| **Dependencies** | Existing generators and data files |
