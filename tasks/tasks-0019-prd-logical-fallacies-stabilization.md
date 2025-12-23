# Task List: Logical Fallacies Tutorial System - Stabilization

**PRD:** `0019-prd-logical-fallacies-stabilization.md`
**Parent PRD:** `0018-prd-logical-fallacies-tutorial-system.md`
**Generated:** 2025-12-23
**Strategy:** Decomposition + Working Backward
**Focus:** Fix empty notebooks and failing integration tests

---

## Relevant Files

### Notebooks (to be populated)
- `lesson-18/interactive/logical-fallacies/notebooks/01_fallacy_detection.ipynb` - Introduction and core concepts notebook
- `lesson-18/interactive/logical-fallacies/notebooks/02_grounded_fallacy_detection.ipynb` - Hands-on exercises notebook

### Tests (to be fixed)
- `lesson-18/interactive/logical-fallacies/generators/tests/test_integration_data.py` - Integration tests with path resolution fix

### Reference Data (read-only)
- `lesson-18/interactive/logical-fallacies/data/fallacies-data.json` - Core fallacy definitions
- `lesson-18/interactive/logical-fallacies/data/dispute-grounding.json` - Domain examples
- `lesson-18/interactive/logical-fallacies/data/patterns-anti-patterns.json` - Pattern/anti-pattern pairs
- `lesson-18/interactive/logical-fallacies/data/polya-phases.json` - Phase definitions
- `lesson-18/interactive/logical-fallacies/data/hw-counter-methods.json` - HW method mappings

### Reference Tutorials (read-only)
- `lesson-18/interactive/logical-fallacies/tutorials/01_cherry_picked_benchmarks/01_understand.md` - Content source for Notebook 01
- `lesson-18/interactive/logical-fallacies/tutorials/01_cherry_picked_benchmarks/04_execute.md` - Content source for Notebook 02

### Generators (read-only)
- `lesson-18/interactive/logical-fallacies/generators/fallacy_example_generator.py` - Used by Notebook 02
- `lesson-18/interactive/logical-fallacies/generators/phase_data_generators.py` - Phase content generator
- `lesson-18/interactive/logical-fallacies/generators/pattern_antipattern_generator.py` - Pattern generator

### Notes

- Notebooks must execute in <3 minutes total
- Use existing JSON data files (no API calls)
- Tests must pass when run from project root: `uv run pytest lesson-18/interactive/logical-fallacies/generators/tests/ -v`

### Assumptions Made

- **Existing generators work:** Unit tests for generators pass (8/14 tests pass currently)
- **Tutorial content is complete:** Markdown tutorials can be referenced for notebook content
- **No external dependencies:** Notebooks use only stdlib + existing generators

---

## Tasks

- [x] 1.0 Implement Notebook 01 - Introduction and Core Concepts
  - [x] 1.1 Create markdown cell with title and learning objectives
        Input: PRD FR-1.1
        Output: Cell with "Cherry-Picked Benchmarks" title and 3-4 learning objectives
        Verification: Cell renders correctly in Jupyter
  - [x] 1.2 Create markdown cell explaining cherry-picked benchmarks definition
        Input: `01_understand.md` content
        Output: Cell with clear definition and "statistical hasty generalization" framing
        Verification: Content matches tutorial source
  - [x] 1.3 Create markdown cell with real-world example (Google Gemini demo)
        Input: `01_understand.md` "Hands-On Illusion" section
        Output: Cell with concrete example and "why this is dangerous" callout
        Verification: Example is accurate and relatable
  - [x] 1.4 Create markdown cell with dispute domain scenario
        Input: `01_understand.md` "99% Accuracy" section
        Output: Cell with ReasonCodeClassifier scenario
        Verification: Shows 99% → 25% accuracy drop
  - [x] 1.5 Create markdown cell with red flags checklist
        Input: `01_understand.md` red flags section
        Output: Cell with ≥3 red flags as checklist items
        Verification: Each red flag has concrete indicator
  - [x] 1.6 Validate notebook executes without error
        Input: Completed notebook
        Output: Successful execution log
        Verification: `jupyter nbconvert --execute 01_fallacy_detection.ipynb` succeeds

- [x] 2.0 Implement Notebook 02 - Hands-On Exercises
  - [x] 2.1 Create setup cell with imports, cost warnings, assertions
        Input: PRD FR-2.6
        Output: Code cell with imports (json, pathlib, collections), warning banner, path assertions
        Verification: Cell executes, prints "No API costs - using local data"
  - [x] 2.2 Create Cell 1: Load dispute data with validation
        Input: PRD FR-2.1, `dispute-grounding.json`
        Output: Code cell loading JSON, printing shape/schema summary
        Verification: Data loads, displays record count and sample keys
  - [x] 2.3 Create Cell 2: Generate cherry-picked vs. full test sets
        Input: PRD FR-2.2, `fallacy_example_generator.py`
        Output: Code cell creating biased (golden) and diverse test sets
        Verification: Shows category distribution difference between sets
  - [x] 2.4 Create Cell 3: Annotate fallacy red flags
        Input: PRD FR-2.3
        Output: Code cell highlighting red flags in generated example with comments
        Verification: Annotations match UNDERSTAND phase content
  - [x] 2.5 Create Cell 4: Calculate metrics (accuracy, confusion matrix)
        Input: PRD FR-2.4
        Output: Code cell computing accuracy on both sets, simple confusion matrix display
        Verification: Shows accuracy gap (cherry-picked ~99% vs. diverse ~25%)
  - [x] 2.6 Create Cell 5: Compare to HW3 stratified sampling method
        Input: PRD FR-2.5, `hw-counter-methods.json`
        Output: Code cell demonstrating proper evaluation with stratified approach
        Verification: Shows improved metrics with proper methodology
  - [x] 2.7 Create summary markdown cell
        Input: PRD requirements
        Output: Markdown cell with key takeaways and "next steps" suggestions
        Verification: Summary reinforces learning objectives
  - [x] 2.8 Validate notebook executes in <2 minutes
        Input: Completed notebook
        Output: Execution timing log
        Verification: `time jupyter nbconvert --execute 02_grounded_fallacy_detection.ipynb` < 120s

- [x] 3.0 Fix Integration Test Path Resolution
  - [x] 3.1 Update test_integration_data.py to use Path(__file__).resolve()
        Input: Current test file with hardcoded relative paths
        Output: Updated test file using `Path(__file__).resolve().parent.parent / "data"`
        Verification: Path works from any working directory
  - [x] 3.2 Verify all 6 previously failing tests now pass
        Input: Updated test file
        Output: pytest output showing 6/6 integration tests pass
        Verification: `uv run pytest generators/tests/test_integration_data.py -v` shows all pass
  - [x] 3.3 Verify tests run from both project root and local directory
        Input: Updated test file
        Output: pytest passes from both locations
        Verification: Run from project root AND from `generators/tests/` directory

- [x] 4.0 Validation and Verification
  - [x] 4.1 Run full test suite (target: 14/14 pass)
        Input: All test files
        Output: pytest summary
        Verification: `uv run pytest generators/tests/ -v` shows 14/14 passed
  - [x] 4.2 Verify coverage ≥90%
        Input: All test files
        Output: Coverage report
        Verification: `uv run pytest generators/tests/ --cov` shows ≥90%
  - [x] 4.3 Execute both notebooks with jupyter nbconvert
        Input: Both notebooks
        Output: Execution logs
        Verification: Both execute without error
  - [x] 4.4 Verify total execution time <3 minutes
        Input: Both notebooks
        Output: Timing log
        Verification: Combined execution < 180 seconds
  - [x] 4.5 Verify notebooks are not empty (>1KB each)
        Input: Both notebooks
        Output: File size confirmation
        Verification: `ls -la notebooks/*.ipynb` shows >1KB for each file

---

## Validation Checkpoints

### Checkpoint 1: Notebook 01 Complete (after Task 1.0)
- [x] 5 markdown cells created
- [x] Executes without error
- [x] Content aligns with `01_understand.md`

### Checkpoint 2: Notebook 02 Complete (after Task 2.0)
- [x] 7 cells created (1 setup + 5 exercise + 1 summary)
- [x] Loads data successfully
- [x] Generates cherry-picked examples
- [x] Calculates metrics showing accuracy gap
- [x] Executes in <2 minutes

### Checkpoint 3: Tests Fixed (after Task 3.0)
- [x] Path resolution updated to use `__file__`
- [x] 14/14 tests pass
- [x] Coverage ≥90%

### Checkpoint 4: Final Validation (after Task 4.0)
- [x] Both notebooks execute from project root
- [x] All tests pass from project root
- [x] PRD 0019 success criteria met

---

## Summary

| Task | Sub-tasks | Est. Time | Priority |
|------|-----------|-----------|----------|
| 1.0 Notebook 01 | 6 | 30-45 min | P0 (first) |
| 2.0 Notebook 02 | 8 | 60-90 min | P0 |
| 3.0 Test Fix | 3 | 15-20 min | P1 |
| 4.0 Validation | 5 | 15-20 min | P1 |
| **Total** | **22** | **~2-3 hrs** | |
