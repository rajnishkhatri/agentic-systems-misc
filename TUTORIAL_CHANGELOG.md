# Tutorial Changelog

This file tracks when tutorials need updates after code changes, ensuring documentation stays synchronized with the codebase.

## How to Use This File

**When making code changes**, check if any tutorials reference the modified code:
1. Search for related tutorial files in the affected lesson directory
2. If found, add an entry below with the date and description
3. Update affected tutorials within 48 hours
4. Mark entry as ✅ RESOLVED when tutorial is updated

---

## Lesson 9: Evaluation Fundamentals & Exact Methods

**Last Updated:** 2025-11-09
**Status:** ✅ Complete

### Triggers for Update
- Changes to `backend/exact_evaluation.py` → Update `exact_evaluation_methods.md` and `similarity_measurements_tutorial.ipynb`
- Changes to `backend/evaluation_utils.py` semantic similarity methods → Update `exact_evaluation_methods.md`
- New evaluation metrics added → Update `evaluation_fundamentals.md` and decision tree diagram
- Changes to perplexity calculation → Update `language_modeling_metrics.md` and `perplexity_calculation_tutorial.ipynb`
- Test failures in `tests/test_exact_evaluation.py` → Review all Lesson 9 tutorials

### Update History
- **2025-11-09:** Initial creation with 3 concept tutorials, 2 notebooks, backend module, 33 tests (100% coverage) ✅

---

## Lesson 10: AI-as-Judge Mastery & Production Patterns

**Last Updated:** 2025-11-09
**Status:** ✅ Complete

### Triggers for Update
- Changes to `backend/ai_judge_framework.py` (BaseJudge, JudgeResult, concrete judges) → Update `ai_judge_production_guide.md` and both notebooks
- Modifications to judge templates in `lesson-10/templates/judge_prompts/` → Update `ai_judge_production_guide.md` template list
- Changes to `homeworks/hw3/scripts/develop_judge.py` integration → Update cross-references in guide
- Changes to `lesson-4/judge_substantiation.py` integration → Update cross-references in guide
- New bias detection methods → Update `judge_bias_detection_tutorial.ipynb`
- Test failures in `tests/test_ai_judge_framework.py` → Review all Lesson 10 tutorials

### Update History
- **2025-11-09:** Initial creation with production guide, 2 notebooks, 15 judge templates, framework module, 35 tests (92% coverage) ✅

---

## Lesson 11: Comparative Evaluation & Leaderboards

**Last Updated:** 2025-11-09
**Status:** ✅ Complete

### Triggers for Update
- Changes to `backend/comparative_evaluation.py` (EloRanking, BradleyTerryRanking) → Update `comparative_evaluation_guide.md` and all 3 notebooks
- Modifications to `lesson-11/data/pairwise_comparisons.json` dataset → Update notebooks that reference this data
- Changes to `lesson-11/scripts/generate_pairwise_comparisons.py` → Update guide section on dataset generation
- New ranking algorithms added → Update algorithm comparison table and decision flowchart
- Test failures in `tests/test_comparative_evaluation.py` → Review all Lesson 11 tutorials

### Update History
- **2025-11-09:** Initial creation with comparative guide, 3 notebooks, 2 diagrams, backend module, 45 tests (97% coverage) ✅

---

## Cross-Lesson: Evaluation Dashboard (Lessons 9-11)

**Last Updated:** 2025-11-09
**Status:** ✅ Complete

### Triggers for Update
- Changes to `lesson-9-11/evaluation_dashboard.py` → Update dashboard README and screenshots
- Changes to metrics JSON schema → Update dashboard data loading functions
- New metrics added to any lesson → Add corresponding dashboard section
- Changes to HW3/HW4 metrics structure → Update dashboard integration code
- Dashboard UI/UX improvements → Update dashboard README with new features

### Update History
- **2025-11-09:** Initial creation with FastHTML dashboard, unified metrics display, auto-refresh, export, keyboard shortcuts ✅

---

## Lesson 14: Memory Systems & Context Engineering

**Last Updated:** 2025-11-15
**Status:** ✅ Complete

### Triggers for Update
- Changes to `lesson-14/agents_memory.txt` canonical source → Update `memory_systems_fundamentals.md` citations and terminology
- Changes to `lesson-14/COMPASS_ARTIFACT_ANALYSIS.md` cost/ROI data → Update `context_engineering_guide.md` ROI examples and decision matrix
- Changes to `lesson-14/memory_systems_implementation.ipynb` → Update cross-references in `context_engineering_guide.md` and `TUTORIAL_INDEX.md`
- Modifications to Chroma setup or memory patterns → Update notebook exercises and `memory_systems_fundamentals.md` pattern descriptions
- New memory techniques or vector databases added → Update decision matrix in `memory_systems_fundamentals.md` and FAQ in `TUTORIAL_INDEX.md`
- Changes to `lesson-14/diagrams/*.mmd` diagrams → Re-export PNG/SVG and verify terminology alignment with `agents_memory.txt`
- Changes to `lesson-14/results/memory_systems_demo_results.json` schema → Update schema documentation and dashboard integration
- Updates to `lesson-14/04_Agentic_RAG.md` → Verify forward references to memory tutorials remain accurate
- Updates to `lesson-14/multi_agent_fundamentals.md` → Verify Component 1 (Memory) section remains consistent with memory tutorials
- Test failures in `tests/test_memory_systems_notebook.py` → Review notebook helper functions and defensive coding

### Update History
- **2025-11-15:** Initial creation with 3 tutorials (memory_systems_fundamentals.md, context_engineering_guide.md, memory_systems_implementation.ipynb), 3 diagrams (memory_types_taxonomy, context_engineering_workflow, search_o1_architecture), JSON schema documentation, 17 unit tests for notebook helpers, integration with TUTORIAL_INDEX.md Learning Path #5, expanded multi_agent_fundamentals.md Component 1 section, forward references from 04_Agentic_RAG.md ✅

---

## General Infrastructure

### Triggers for Update
- Changes to `pyproject.toml` dependencies → Check all notebooks for import statement compatibility
- Changes to `pytest.ini` or test infrastructure → Update testing instructions in all README files
- Changes to `.gitignore` → Verify tutorial outputs are properly excluded
- New lesson or homework added → Update CLAUDE.md tutorial navigation section
- Changes to `backend/evaluation_utils.py` (BaseRetrievalEvaluator) → Check HW4 and Lesson 9 cross-references

---

## Pending Updates

**None currently** - All tutorials are synchronized with codebase as of 2025-11-09.

---

## Tutorial Maintenance Checklist

When updating tutorials after code changes:

- [ ] Update affected concept tutorials (.md files)
- [ ] Update affected interactive notebooks (.ipynb files)
- [ ] Update diagrams if architecture/workflow changed
- [ ] Update TUTORIAL_INDEX.md if learning objectives/prerequisites changed
- [ ] Update code snippets with new API signatures
- [ ] Update error messages and expected outputs
- [ ] Update cost estimates if API pricing changed
- [ ] Test notebook execution (both DEMO and FULL modes)
- [ ] Update "Last Updated" timestamp in tutorial
- [ ] Mark changelog entry as ✅ RESOLVED

---

## Automated Checks

**Recommended CI/CD checks to detect tutorial drift:**

1. **API signature validation:** Extract function signatures from backend modules, compare with tutorial code examples
2. **Import validation:** Run `python -c "import X"` for all imports in tutorial code snippets
3. **Notebook execution:** Run `pytest tests/test_notebooks.py` to ensure all notebooks execute successfully
4. **Link checking:** Use markdown link checker to validate all cross-references
5. **Cost estimate validation:** Compare tutorial cost estimates with actual API pricing (monthly check)

---

**Maintainer:** AI Evaluation Course Team
**Last Review:** 2025-11-09
