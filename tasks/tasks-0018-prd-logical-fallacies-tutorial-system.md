# Task List: Logical Fallacies Tutorial System

**PRD:** `0018-prd-logical-fallacies-tutorial-system.md`
**Generated:** 2025-12-23
**Strategy:** Decomposition + Iterative Development
**Focus:** Iteration 1 - Cherry-Picked Benchmarks

---

## Relevant Files

### Project Structure
- `lesson-18/interactive/logical-fallacies/` - Root directory for tutorial system
- `lesson-18/interactive/logical-fallacies/data/` - JSON data files
- `lesson-18/interactive/logical-fallacies/generators/` - Python generators
- `lesson-18/interactive/logical-fallacies/generators/tests/` - TDD tests
- `lesson-18/interactive/logical-fallacies/components/` - React/JSX components
- `lesson-18/interactive/logical-fallacies/notebooks/` - Jupyter notebooks
- `lesson-18/interactive/logical-fallacies/tutorials/` - Markdown tutorials

### Data Layer
- `lesson-18/interactive/logical-fallacies/data/fallacies-data.json` - Core fallacy definitions
- `lesson-18/interactive/logical-fallacies/data/patterns-anti-patterns.json` - Pattern/anti-pattern pairs
- `lesson-18/interactive/logical-fallacies/data/dispute-grounding.json` - Domain examples from dispute-chatbot
- `lesson-18/interactive/logical-fallacies/data/polya-phases.json` - Phase definitions
- `lesson-18/interactive/logical-fallacies/data/hw-counter-methods.json` - HW method mappings
- `lesson-18/interactive/logical-fallacies/data/research-sources.json` - arXiv/GitHub/web references

### Python Generators
- `lesson-18/interactive/logical-fallacies/generators/__init__.py` - Package init
- `lesson-18/interactive/logical-fallacies/generators/fallacy_example_generator.py` - Generate fallacy examples
- `lesson-18/interactive/logical-fallacies/generators/phase_data_generators.py` - Generate phase content
- `lesson-18/interactive/logical-fallacies/generators/pattern_antipattern_generator.py` - Generate pattern pairs
- `lesson-18/interactive/logical-fallacies/generators/tests/__init__.py` - Test package init
- `lesson-18/interactive/logical-fallacies/generators/tests/test_fallacy_generator.py` - Tests for fallacy generator
- `lesson-18/interactive/logical-fallacies/generators/tests/test_phase_generators.py` - Tests for phase generators
- `lesson-18/interactive/logical-fallacies/generators/tests/test_pattern_generator.py` - Tests for pattern generator

### React/JSX Components
- `lesson-18/interactive/logical-fallacies/logical-fallacies-focused.jsx` - Main component (exists)
- `lesson-18/interactive/logical-fallacies/components/FallacyCard.jsx` - Fallacy card display
- `lesson-18/interactive/logical-fallacies/components/PatternAntiPatternCard.jsx` - Pattern comparison
- `lesson-18/interactive/logical-fallacies/components/PolyaPhaseFlow.jsx` - Phase navigation
- `lesson-18/interactive/logical-fallacies/components/WorkedExampleBreakdown.jsx` - Annotated examples
- `lesson-18/interactive/logical-fallacies/components/QuizMode.jsx` - Self-assessment quiz

### Notebooks
- `lesson-18/interactive/logical-fallacies/notebooks/01_fallacy_detection.ipynb` - Introduction and concepts
- `lesson-18/interactive/logical-fallacies/notebooks/02_grounded_fallacy_detection.ipynb` - Hands-on exercises

### Tutorials (Cherry-Picked Benchmarks)
- `lesson-18/interactive/logical-fallacies/tutorials/TUTORIAL_INDEX.md` - Navigation hub
- `lesson-18/interactive/logical-fallacies/tutorials/01_cherry_picked_benchmarks/README.md` - Main tutorial
- `lesson-18/interactive/logical-fallacies/tutorials/01_cherry_picked_benchmarks/01_understand.md` - Phase 1
- `lesson-18/interactive/logical-fallacies/tutorials/01_cherry_picked_benchmarks/02_plan.md` - Phase 2
- `lesson-18/interactive/logical-fallacies/tutorials/01_cherry_picked_benchmarks/03_tasks.md` - Phase 3
- `lesson-18/interactive/logical-fallacies/tutorials/01_cherry_picked_benchmarks/04_execute.md` - Phase 4
- `lesson-18/interactive/logical-fallacies/tutorials/01_cherry_picked_benchmarks/05_reflect.md` - Phase 5
- `lesson-18/interactive/logical-fallacies/tutorials/01_cherry_picked_benchmarks/06_counter.md` - Phase 6
- `lesson-18/interactive/logical-fallacies/tutorials/01_cherry_picked_benchmarks/RESEARCH_NOTES.md` - Sources
- `lesson-18/interactive/logical-fallacies/tutorials/01_cherry_picked_benchmarks/diagrams/*.mmd` - Mermaid diagrams

### Source Data (Read-only references)
- `lesson-18/dispute-chatbot/synthetic_data/phase1/golden_set/classification_labels.json`
- `lesson-18/dispute-chatbot/synthetic_data/phase1/golden_set/diverse_classification_labels.json`
- `lesson-18/dispute-chatbot/synthetic_data/phase1/golden_set/natural_language_classification_v3.json`
- `lesson-18/dispute-schema/reason_codes_catalog.json`

### Notes

- Unit tests should be placed in `generators/tests/` alongside generator code
- Use `uv run pytest lesson-18/interactive/logical-fallacies/generators/tests/ -v --cov` to run tests
- Notebooks should use cached data to achieve <3 minute execution
- React components use Tailwind CSS only (no external dependencies)

### Assumptions Made

- **Existing JSX setup:** `logical-fallacies-focused.jsx` exists and provides base component structure
- **Dispute data format:** Classification labels follow existing JSON schema from dispute-chatbot
- **HW method references:** HW2-HW5 evaluation methods are documented and can be referenced
- **Mermaid rendering:** GitHub renders .mmd files; PNG export available for complex diagrams

---

## Tasks

- [x] 1.0 Project Structure Setup
  - [x] 1.1 Create directory structure for logical-fallacies tutorial system
        Input: PRD file structure (Section 8.3)
        Output: All directories created
        Verification: `tree lesson-18/interactive/logical-fallacies/` shows expected structure
  - [x] 1.2 Create `__init__.py` files for Python packages
        Input: generators/ directory
        Output: Package initialization files
        Verification: `python -c "from generators import *"` succeeds
  - [x] 1.3 Create base JSON data files with schema structure
        Input: PRD data definitions
        Output: Empty JSON files with correct schema
        Verification: JSON files parse without error
  - [x] 1.4 Configure React/Tailwind environment
        Input: Existing `logical-fallacies-focused.jsx`, PRD Section 8.3
        Output: `tailwind.config.js` with animation presets, verified dev setup
        Verification: Components render without errors, Tailwind classes apply correctly
  - [x] 1.5 Analyze dispute data and draft example scenarios
        Input: `classification_labels.json`, `diverse_classification_labels.json`
        Output: `tutorials/01_cherry_picked_benchmarks/example_scenarios_draft.md`
        Contents: Category distribution analysis, 3-5 cherry-picking scenarios sketched
        Verification: Scenarios clearly demonstrate cherry-picking vs full distribution
        **Purpose:** Breaks circular dependency between content (3.0) and data (4.0) tasks

- [x] 2.0 Research Phase: Cherry-Picked Benchmarks
  - [x] 2.1 Search arXiv for "benchmark selection bias", "evaluation methodology", "dataset bias"
        **TIME BOX:** 45 minutes maximum
        Input: Search queries
        Output: ≥1 relevant paper with citation
        Relevance Criteria: Paper must mention "benchmark" + ("bias" | "selection" | "cherry" | "evaluation")
        Verification: Paper directly addresses benchmark cherry-picking in ML/AI
        Backup: If no relevant paper found, document 2 closest matches with gap analysis
  - [x] 2.2 Search GitHub for benchmark manipulation examples, evaluation frameworks
        **TIME BOX:** 45 minutes maximum
        Input: Search queries (e.g., "benchmark evaluation", "dataset splitting bias")
        Output: ≥1 relevant repository with relevance notes
        Relevance Criteria: Repo demonstrates benchmark bias OR provides evaluation framework
        Verification: Repository demonstrates or detects benchmark issues
        Backup: If no relevant repo found, document evaluation framework that could detect issue
  - [x] 2.3 Web search for industry cases of cherry-picked AI benchmarks
        **TIME BOX:** 45 minutes maximum
        Input: Search queries (vendor demos, AI benchmark controversies)
        Output: ≥1 blog post or case study
        Relevance Criteria: Article describes specific instance of benchmark manipulation
        Verification: Source describes real-world cherry-picking incident
        Backup: If no case study found, document vendor benchmark presentation as example
  - [x] 2.4 Document all sources in `RESEARCH_NOTES.md`
        Input: Research findings from 2.1-2.3
        Output: Structured markdown with citations, relevance notes, key insights
        Verification: ≥3 sources documented with relevance score (1-5) for each
        Format: Citation, relevance score, key insight, how it applies to tutorial

### ⏸️ CHECKPOINT: Research Quality Gate
- [x] ≥3 sources with relevance score ≥3
- [x] At least one academic source (arXiv)
- [x] At least one practical example (GitHub or case study)
- [x] Key insights mapped to tutorial phases
**GATE:** Do not proceed to Task 3.0 until checkpoint passes

- [x] 3.0 Content Layer: 6 Pólya Phase Tutorials
  - [x] 3.1 Write `01_understand.md` - Domain definition, real example, red flags
        Input: Research notes, dispute-chatbot data, example scenarios from Task 1.5
        Output: ~500-word tutorial with concrete examples
        Verification Checklist:
        - [x] Word count: 400-600 words
        - [x] Contains clear definition of cherry-picked benchmarks
        - [x] ≥1 dispute example from Task 1.5 scenarios
        - [x] ≥3 red flags with concrete indicators
        - [x] Links to RESEARCH_NOTES.md sources
  - [x] 3.2 Create Mermaid diagram for UNDERSTAND phase
        Input: Phase content
        Output: `diagrams/01_understand.mmd`
        Verification: `mmdc -i 01_understand.mmd -o 01_understand.png` succeeds, ≤10 nodes
  - [x] 3.3 Write `02_plan.md` - Detection strategy, related fallacies, data sources
        Input: Research notes, fallacy relationships
        Output: ~500-word tutorial with strategy outline
        Verification Checklist:
        - [x] Word count: 400-600 words
        - [x] Detection strategy with step-by-step approach
        - [x] Maps to ≥2 related fallacies (survivorship, demo-to-production)
        - [x] Lists ≥3 data sources for detection
  - [x] 3.4 Create Mermaid diagram for PLAN phase
        Input: Phase content
        Output: `diagrams/02_plan.mmd`
        Verification: Diagram shows detection workflow, `mmdc` succeeds
  - [x] 3.5 Write `03_tasks.md` - Verification steps, data queries, metric calculations
        Input: Detection strategy from 3.3
        Output: ~600-word tutorial with actionable checklist
        Verification Checklist:
        - [x] Word count: 500-700 words
        - [x] ≥5 verification steps with checkboxes
        - [x] ≥2 code snippets (data queries or metric calculations)
        - [x] Each step has expected output
  - [x] 3.6 Create Mermaid diagram for TASKS phase
        Input: Phase content
        Output: `diagrams/03_tasks.mmd`
        Verification: Diagram shows task flow/checklist, `mmdc` succeeds
  - [x] 3.7 Write `04_execute.md` - Worked example with claim, annotations, metrics, counter-response
        Input: Dispute-chatbot data, verification tasks, example scenarios from Task 1.5
        Output: ~800-word tutorial with fully annotated example
        Verification Checklist:
        - [x] Word count: 700-900 words
        - [x] Contains verbatim claim text (quoted)
        - [x] Line-by-line annotations highlighting fallacy
        - [x] Calculated metrics from real dispute data
        - [x] Counter-response template
  - [x] 3.8 Create Mermaid diagram for EXECUTE phase
        Input: Phase content
        Output: `diagrams/04_execute.mmd`
        Verification: Diagram shows example breakdown, `mmdc` succeeds
  - [x] 3.9 Write `05_reflect.md` - Key takeaways, pattern connections, self-assessment quiz
        Input: All previous phases
        Output: ~400-word tutorial with quiz
        Verification Checklist:
        - [x] Word count: 350-500 words
        - [x] ≥3 key takeaways (numbered)
        - [x] Pattern links to related fallacies
        - [x] 3-5 quiz questions with answers
  - [x] 3.10 Create Mermaid diagram for REFLECT phase
        Input: Phase content
        Output: `diagrams/05_reflect.mmd`
        Verification: Diagram shows reflection process, `mmdc` succeeds
  - [x] 3.11 Write `06_counter.md` - HW3 Confusion Matrix reference, code example, application scenario
        Input: HW3 documentation, dispute data
        Output: ~600-word tutorial with working code
        Verification Checklist:
        - [x] Word count: 500-700 words
        - [x] HW3 method reference with link
        - [x] Executable Python code (copy-paste ready)
        - [x] Realistic application scenario from dispute domain
  - [x] 3.12 Create Mermaid diagram for COUNTER phase
        Input: Phase content
        Output: `diagrams/06_counter.mmd`
        Verification: Diagram shows counter-methodology, `mmdc` succeeds
  - [x] 3.13 Write main `README.md` combining all phases with navigation
        Input: All phase tutorials
        Output: Overview tutorial with links to all phases
        Verification: All links work, provides learning path
  - [x] 3.14 Create `TUTORIAL_INDEX.md` navigation hub
        Input: All tutorials and notebooks
        Output: Index with learning objectives, paths, prerequisites
        Verification: Follows existing TUTORIAL_INDEX.md pattern from other lessons

- [ ] 4.0 Data Layer: JSON Files and Python Generators
  - [x] 4.1 Add Cherry-Picked Benchmarks entry to `fallacies-data.json`
        Input: PRD fallacy definition
        Output: JSON entry with id, name, category, description, ai_context
        Verification: JSON validates, contains all required fields
  - [x] 4.2 Add pattern/anti-pattern pair to `patterns-anti-patterns.json`
        Input: PRD Section 8.2 card layout
        Output: JSON entry with anti_pattern, pattern, red_flags, best_practices, code examples
        Verification: JSON validates, matches PRD design
  - [x] 4.3 Add dispute grounding examples to `dispute-grounding.json`
        Input: classification_labels.json, diverse_classification_labels.json
        Output: ≥2 grounded examples showing cherry-picking vs full distribution
        Verification: Examples use real dispute data, demonstrate fallacy clearly
  - [x] 4.4 Add phase definitions to `polya-phases.json`
        Input: 6 Pólya phases from PRD
        Output: JSON with phase metadata, icons, descriptions
        Verification: All 6 phases defined with consistent structure
  - [x] 4.5 Add HW method mapping to `hw-counter-methods.json`
        Input: PRD Section 15 (HW Evaluation Methods)
        Output: JSON mapping Cherry-Picked Benchmarks to HW3 Confusion Matrix
        Verification: Contains method reference, when_to_use, code_reference
  - [x] 4.6 Add research sources to `research-sources.json`
        Input: RESEARCH_NOTES.md from Task 2.4
        Output: JSON with structured citations (arXiv, GitHub, web)
        Verification: All sources from research phase included
  - [x] 4.7 Write TDD tests for `fallacy_example_generator.py` (RED phase)
        Input: Generator requirements
        Output: Failing tests in `test_fallacy_generator.py`
        Verification: Tests fail with clear assertions
  - [x] 4.8 Implement `fallacy_example_generator.py` (GREEN phase)
        Input: Failing tests, JSON data
        Output: `_generate_cherry_picked()` function
        Verification: All tests pass
  - [x] 4.9 Write TDD tests for `phase_data_generators.py` (RED phase)
        Input: Phase content requirements
        Output: Failing tests in `test_phase_generators.py`
        Verification: Tests fail for all 6 phase generators
  - [x] 4.10 Implement `phase_data_generators.py` (GREEN phase)
        Input: Failing tests, JSON data
        Output: Generator functions for all 6 phases
        Verification: All tests pass
  - [x] 4.11 Write TDD tests for `pattern_antipattern_generator.py` (RED phase)
        Input: Pattern requirements from PRD Section 8.2
        Output: Failing tests in `test_pattern_generator.py`
        Verification: Tests fail with clear assertions
  - [x] 4.12 Implement `pattern_antipattern_generator.py` (GREEN phase)
        Input: Failing tests, JSON data
        Output: Pattern/anti-pattern generator function
        Verification: All tests pass
  - [x] 4.13 Refactor generators for code quality (REFACTOR phase)
        Input: Passing tests
        Output: Clean, documented, defensive code
        Verification: Tests still pass, ruff check passes, ≥90% coverage

### ⏸️ CHECKPOINT: Generator Coverage Gate
- [x] `pytest --cov` shows ≥90% coverage
- [x] All tests pass (no failures or errors)
- [x] `ruff check` passes with no errors
- [x] All JSON files load correctly via generators
**GATE:** Do not proceed to Task 5.0 until checkpoint passes

- [x] 5.0 Interactive Layer: React/JSX Components
  - [x] 5.1 Create `FallacyCard.jsx` component
        Input: fallacies-data.json schema
        Output: React component displaying fallacy overview
        Verification: Renders with sample data, mobile responsive (768px+)
  - [x] 5.2 Create `PatternAntiPatternCard.jsx` component
        Input: patterns-anti-patterns.json, PRD Section 8.2 design
        Output: React component with side-by-side comparison
        Verification: Matches PRD design, responsive layout
  - [x] 5.3 Create `PolyaPhaseFlow.jsx` component
        Input: polya-phases.json
        Output: React component with phase navigation (expandable sections)
        Verification: All 6 phases navigable, current phase highlighted
  - [x] 5.4 Create `WorkedExampleBreakdown.jsx` component
        Input: EXECUTE phase content
        Output: React component with annotated claim breakdown
        Verification: Annotations highlight fallacy elements interactively
  - [x] 5.5 Create `QuizMode.jsx` component
        Input: REFLECT phase quiz questions
        Output: React component with interactive quiz
        Verification: Questions display, answers scored, feedback shown
  - [x] 5.6 Update `logical-fallacies-focused.jsx` to integrate all components
        Input: All component files
        Output: Main component importing and orchestrating sub-components
        Verification: Full tutorial flow works end-to-end
  - [x] 5.7 Verify mobile responsiveness (768px+ breakpoint)
        Input: All components
        Output: Responsive design verification
        Verification: Chrome DevTools device emulation at 768px, 1024px, 1440px
        Method: Screenshots saved to `docs/responsive-tests/`, no horizontal scroll at any breakpoint

### ⏸️ CHECKPOINT: Integration Test Gate
- [x] All 5 components render without errors
- [x] Data flows correctly: JSON → Generator → Component (Simulated via direct import)
- [x] Navigation between phases works (PolyaPhaseFlow)
- [x] Quiz mode scores and provides feedback (QuizMode)
- [x] Responsive at all breakpoints (768px, 1024px, 1440px)
**GATE:** Do not proceed to Task 6.0 until checkpoint passes

- [x] 6.0 Notebook Layer: Interactive Jupyter Notebooks
  - [x] 6.1 Create `01_fallacy_detection.ipynb` - Introduction and core concepts
        Input: Tutorial content, research notes
        Output: Notebook with 4-5 cells covering theory
        Verification: Executes without error, <1 minute runtime
  - [x] 6.2 Create `02_grounded_fallacy_detection.ipynb` Cell 1: Load dispute data
        Input: classification_labels.json, diverse_classification_labels.json
        Output: Data loading cell with validation
        Verification: Data loads, shape/schema printed
  - [x] 6.3 Create `02_grounded_fallacy_detection.ipynb` Cell 2: Generate cherry-picked examples
        Input: Loaded data, fallacy_example_generator
        Output: Cell generating biased vs full test sets
        Verification: Shows accuracy difference between sets
  - [x] 6.4 Create `02_grounded_fallacy_detection.ipynb` Cell 3: Annotate fallacy
        Input: Generated examples
        Output: Cell highlighting red flags in example
        Verification: Annotations match UNDERSTAND phase content
  - [x] 6.5 Create `02_grounded_fallacy_detection.ipynb` Cell 4: Calculate metrics
        Input: Test sets
        Output: Cell computing accuracy, confusion matrix, per-category metrics
        Verification: Metrics demonstrate cherry-picking effect quantitatively
  - [x] 6.6 Create `02_grounded_fallacy_detection.ipynb` Cell 5: Compare to HW3 method
        Input: Metrics, HW3 confusion matrix reference
        Output: Cell showing proper evaluation methodology
        Verification: Demonstrates counter-approach from HW3
  - [x] 6.7 Add setup cells with cost warnings and validation assertions
        Input: All notebook cells
        Output: Setup cell at top with warnings, assertion cells throughout
        Verification: Notebooks warn about any API costs, assertions catch errors
  - [x] 6.8 Validate notebook execution time <3 minutes
        Input: Both notebooks
        Output: Timing verification
        Verification: `time jupyter nbconvert --execute` <3 min total

- [ ] 7.0 Testing and Validation
  - [ ] 7.1 Run full test suite and verify ≥90% coverage
        Input: All generator tests
        Output: Coverage report
        Verification: `pytest --cov` shows ≥90% coverage
  - [ ] 7.2 Validate all JSON files parse correctly
        Input: All JSON files in data/
        Output: Validation script output
        Verification: No JSON parse errors
  - [ ] 7.3 Validate all Mermaid diagrams render
        Input: All .mmd files
        Output: Rendered diagrams
        Verification: `mmdc` converts all diagrams without error
  - [ ] 7.4 Validate all tutorial links work
        Input: All .md files
        Output: Link checker output
        Verification: No broken internal links
  - [ ] 7.5 Run ruff format and check on all Python files
        Input: All .py files
        Output: Ruff output
        Verification: No formatting or linting errors
  - [ ] 7.6 Manual review against PRD validation checkpoints
        Input: PRD Section 11 checkpoints
        Output: Checklist completion
        Verification: All 6 checkpoints pass
  - [ ] 7.7 Component integration test
        Input: All React components, JSON data files, Python generators
        Output: Automated integration test that mounts all components together
        Test Coverage:
        - Load all JSON data via generators
        - Mount FallacyCard with generated data
        - Mount PatternAntiPatternCard with pattern data
        - Navigate through all 6 phases in PolyaPhaseFlow
        - Complete quiz in QuizMode and verify scoring
        - Verify WorkedExampleBreakdown annotations render
        Verification: All integration tests pass, no console errors

- [ ] 8.0 Publishing and Reflection Documentation
  - [ ] 8.1 Conduct self-review of all content
        Input: All tutorials, notebooks, components
        Output: Self-review notes
        Verification: Review documented with any issues found
  - [ ] 8.2 Draft social media post for Cherry-Picked Benchmarks
        Input: Tutorial content, key visuals
        Output: Draft post (LinkedIn/Twitter format)
        Verification: Self-contained, engaging, links to full tutorial
  - [ ] 8.3 Document learnings in reflection notes
        Input: Development experience
        Output: `REFLECTION_NOTES.md` with lessons learned
        Verification: Contains ≥3 learnings for next iteration
  - [ ] 8.4 Identify improvements for next fallacy iteration
        Input: Reflection notes
        Output: Improvement list in reflection notes
        Verification: Actionable improvements documented
  - [ ] 8.5 Update PRD status (Cherry-Picked Benchmarks → Complete)
        Input: PRD Section 13 status table
        Output: Updated status
        Verification: PRD reflects completion

---

## Summary

| Task | Sub-tasks | Est. Hours | Notes |
|------|-----------|------------|-------|
| 1.0 Project Structure | 5 | 1-2 | +Tasks 1.4, 1.5 |
| 2.0 Research Phase | 4 | 4-6 | Time-boxed, +checkpoint |
| 3.0 Content Layer | 14 | 12-18 | 14 sub-tasks × 6 diagrams |
| 4.0 Data Layer | 13 | 4-5 | +coverage checkpoint |
| 5.0 Interactive Layer | 7 | 6-10 | 5 components from scratch |
| 6.0 Notebook Layer | 8 | 3-4 | Cached data |
| 7.0 Testing | 7 | 3-4 | +integration test |
| 8.0 Publishing | 5 | 1-2 | Unchanged |
| **Total** | **63** | **~35-50 hrs** | +50% buffer from original |

### Time Estimate Rationale
- **Research (2-3 → 4-6 hrs):** Research always expands; time-boxing mitigates but doesn't eliminate
- **Content (8-12 → 12-18 hrs):** 14 tutorials + 6 diagrams is substantial; quality takes time
- **Interactive (3-4 → 6-10 hrs):** 5 React components from scratch with responsive design
- **Buffer:** 50% increase accounts for unforeseen blockers and iteration

---

## PRD Validation Checkpoints

### Checkpoint 1: Research Complete (Task 2.0)
- [ ] ≥3 sources documented (arXiv, GitHub, web)
- [ ] Sources are directly relevant (not digressed)
- [ ] Key insights extracted for tutorial content

### Checkpoint 2: Content Complete (Task 3.0)
- [ ] All 6 Pólya phases written (.md files)
- [ ] Visual diagram for each phase
- [ ] Pattern/Anti-pattern documented
- [ ] Grounded in dispute-chatbot data

### Checkpoint 3: Data Layer Complete (Task 4.0)
- [ ] JSON entries added
- [ ] Python generators implemented
- [ ] TDD tests passing with ≥90% coverage

### Checkpoint 4: Interactive Layer Complete (Task 5.0)
- [ ] React/JSX components functional
- [ ] Mobile responsive (768px+)
- [ ] No external dependencies (Tailwind only)

### Checkpoint 5: Ready for Publishing (Task 7.0)
- [ ] Self-review complete
- [ ] No broken links/references
- [ ] Diagrams render correctly
- [ ] Social media post drafted

### Checkpoint 6: Reflection Complete (Task 8.0)
- [ ] Feedback gathered (self + social)
- [ ] Learnings documented
- [ ] Improvements identified for next iteration
