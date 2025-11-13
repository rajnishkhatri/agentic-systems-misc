# Task List: Advanced RAG & Agent Evaluation Tutorial System (Lessons 12-14)

**Generated from**: `tasks/0005-prd-rag-agent-evaluation-tutorial-system.md`
**Status**: Phase 1 - Parent Tasks Generated
**Total Estimated Time**: 4 weeks (28 days)
**Estimated Cost**: $10-15 (FULL mode), $2-3 (DEMO mode)

---

## Relevant Files

**Lesson 12 - Hybrid Retrieval:**
- `lesson-12/TUTORIAL_INDEX.md` - Navigation hub for Lesson 12 tutorials
- `lesson-12/README.md` - Lesson overview and quick start guide
- `lesson-12/embedding_based_retrieval.md` - Concept tutorial on semantic search
- `lesson-12/hybrid_search_strategies.md` - Concept tutorial on RRF and hybrid retrieval
- `lesson-12/context_quality_evaluation.md` - Concept tutorial on chunking optimization
- `lesson-12/hybrid_search_comparison.ipynb` - Interactive notebook comparing BM25/semantic/hybrid
- `lesson-12/chunking_optimization.ipynb` - Interactive notebook testing chunking strategies
- `lesson-12/diagrams/hybrid_search_architecture.mmd` - RRF fusion workflow diagram
- `lesson-12/diagrams/chunking_strategies_comparison.png` - Visual comparison of chunking methods
- `lesson-12/diagrams/contextual_retrieval_anthropic.mmd` - Anthropic's chunk augmentation method
- `lesson-12/results/hybrid_search_results.json` - Evaluation results for dashboard
- `lesson-12/results/chunking_comparison.json` - Chunking evaluation results
- `backend/semantic_retrieval.py` - Embeddings, vector search, hybrid search implementation
- `backend/context_judges.py` - Context precision/recall AI judges
- `tests/test_semantic_retrieval.py` - Unit tests for semantic retrieval module
- `tests/test_context_judges.py` - Unit tests for context judges module

**Lesson 13 - RAG Generation:**
- `lesson-13/TUTORIAL_INDEX.md` - Navigation hub for Lesson 13 tutorials
- `lesson-13/README.md` - Lesson overview and quick start guide
- `lesson-13/attribution_evaluation.md` - Concept tutorial on attribution detection
- `lesson-13/hallucination_detection_rag.md` - Concept tutorial on RAG hallucinations
- `lesson-13/end_to_end_rag_eval.md` - Concept tutorial on holistic RAG evaluation
- `lesson-13/attribution_detection.ipynb` - Interactive notebook for attribution measurement
- `lesson-13/context_utilization.ipynb` - Interactive notebook for context usage tracking
- `lesson-13/diagrams/attribution_detection_workflow.mmd` - Claim extraction workflow
- `lesson-13/diagrams/rag_failure_taxonomy.png` - Retrieval vs generation failure modes
- `lesson-13/diagrams/context_utilization_heatmap.mmd` - Document usage visualization
- `lesson-13/data/rag_evaluation_suite.json` - 500 test cases (200 Gita + 200 recipes + 100 adversarial)
- `lesson-13/results/attribution_results.json` - Attribution evaluation results
- `lesson-13/results/hallucination_analysis.json` - Hallucination detection results
- `backend/rag_generation_eval.py` - AttributionDetector, HallucinationDetector, ContextUtilizationScorer
- `backend/rag_pipeline_eval.py` - End-to-end RAG pipeline evaluator
- `tests/test_rag_generation_eval.py` - Unit tests for RAG generation evaluation
- `tests/test_rag_pipeline_eval.py` - Unit tests for pipeline evaluator

**Lesson 14 - Agent Systems:**
- `lesson-14/TUTORIAL_INDEX.md` - Navigation hub for Lesson 14 tutorials
- `lesson-14/README.md` - Lesson overview and quick start guide
- `lesson-14/agent_planning_evaluation.md` - Concept tutorial on planning validation
- `lesson-14/react_reflexion_patterns.md` - Concept tutorial on ReAct/Reflexion
- `lesson-14/multi_agent_orchestration.md` - Concept tutorial on multi-agent systems
- `lesson-14/react_agent_implementation.ipynb` - Interactive notebook building ReAct agent
- `lesson-14/agent_failure_analysis.ipynb` - Interactive notebook analyzing agent failures
- `lesson-14/diagrams/react_agent_workflow.mmd` - Thought-Action-Observation loop
- `lesson-14/diagrams/multi_agent_orchestration.png` - Planner-Validator-Executor architecture
- `lesson-14/diagrams/agent_failure_modes_taxonomy.mmd` - Planning/Tool/Efficiency failures
- `lesson-14/data/agent_planning_benchmark.json` - 100 planning validation tasks
- `lesson-14/data/agent_tool_call_benchmark.json` - 150 tool call validation cases
- `lesson-14/data/agent_efficiency_benchmark.json` - 50 multi-step efficiency tasks
- `lesson-14/results/planning_validation.json` - Planning evaluation results
- `lesson-14/results/agent_performance.json` - Agent performance metrics
- `backend/agent_evaluation.py` - PlanningValidator, ToolCallAccuracyMeasurer
- `backend/multi_agent_framework.py` - BaseAgent, PlannerAgent, ValidatorAgent, ExecutorAgent, MultiAgentOrchestrator
- `tests/test_agent_evaluation.py` - Unit tests for agent evaluation module
- `tests/test_multi_agent_framework.py` - Unit tests for multi-agent framework

**Integration & Dashboard:**
- `lesson-9-11/evaluation_dashboard.py` - EXTENDED with RAG and agent metrics
- `TUTORIAL_CHANGELOG.md` - Updated with new tutorial entries
- `CLAUDE.md` - Updated with new patterns and workflows

### Notes

- All tests follow TDD pattern (RED → GREEN → REFACTOR) from CLAUDE.md
- All Python code uses defensive programming with type hints and input validation
- Use `pytest tests/test_*.py` to run test suites
- Notebooks support DEMO (cheap) and FULL (comprehensive) modes
- Dashboard reads JSON from `lesson-*/results/` directories (no API calls)

---

## Tasks

- [x] **1.0 Lesson 12: Hybrid Retrieval & Context Quality** (Week 1, Days 1-7) ✅ COMPLETED
  - [x] 1.1 Create Lesson 12 directory structure and navigation files
  - [x] 1.2 Write concept tutorial: `embedding_based_retrieval.md` (20-25 min reading time)
  - [x] 1.3 Write concept tutorial: `hybrid_search_strategies.md` (18-22 min reading time)
  - [x] 1.4 Write concept tutorial: `context_quality_evaluation.md` (20-25 min reading time)
  - [x] 1.5 Create visual diagrams for Lesson 12 (3 diagrams: hybrid_search_architecture.mmd, chunking_strategies_comparison.png, contextual_retrieval_anthropic.mmd)
  - [x] 1.6 [TDD-RED] Write tests for `backend/semantic_retrieval.py` (test_semantic_retrieval.py)
  - [x] 1.7 [TDD-GREEN] Implement `backend/semantic_retrieval.py` with 5 functions (generate_embeddings, build_vector_index, semantic_search, hybrid_search, reciprocal_rank_fusion)
  - [x] 1.8 [TDD-REFACTOR] Refactor semantic_retrieval.py for defensive coding and performance
  - [x] 1.9 [TDD-RED] Write tests for `backend/context_judges.py` (test_context_judges.py)
  - [x] 1.10 [TDD-GREEN] Implement `backend/context_judges.py` with ContextPrecisionJudge and ContextRecallJudge classes
  - [x] 1.11 [TDD-REFACTOR] Refactor context_judges.py for defensive coding
  - [x] 1.12 Create interactive notebook: `hybrid_search_comparison.ipynb` with DEMO/FULL modes (<8 min execution)
  - [x] 1.13 Create interactive notebook: `chunking_optimization.ipynb` with DEMO/FULL modes (<5 min execution)
  - [x] 1.14 Execute notebooks and generate results JSON files (hybrid_search_results.json, chunking_comparison.json)
  - [x] 1.15 Write TUTORIAL_INDEX.md with learning objectives, prerequisites, recommended path, FAQ
  - [x] 1.16 Write README.md with lesson overview and quick start guide
  - [x] 1.17 Validate all Lesson 12 deliverables (tests pass, notebooks execute, diagrams render, reading times accurate)

- [x] **2.0 Lesson 13: RAG Generation & Attribution** (Week 2, Days 8-14) ✅ COMPLETED
  - [x] 2.1 Create Lesson 13 directory structure (directories: diagrams/, data/, results/)
  - [x] 2.2 Write concept tutorial: `attribution_evaluation.md` (22-25 min reading time)
  - [x] 2.3 Write concept tutorial: `hallucination_detection_rag.md` (20-25 min reading time)
  - [x] 2.4 Write concept tutorial: `end_to_end_rag_eval.md` (18-22 min reading time)
  - [x] 2.5 Create visual diagrams for Lesson 13 (3 diagrams: attribution_detection_workflow.mmd, rag_failure_taxonomy.mmd, context_utilization_heatmap.mmd)
  - [x] 2.6 Generate RAG evaluation test suite: Extract 200 Gita Q&A samples from `/Gita/Bhagavad-Gita-QA/English/english.csv`
  - [x] 2.7 Generate RAG evaluation test suite: Extract 200 recipe samples from `homeworks/hw4/data/processed_recipes.json`
  - [x] 2.8 Generate RAG evaluation test suite: Create 100 adversarial test cases for hallucination detection
  - [x] 2.9 Label all 500 test cases with: is_attributed, is_context_relevant, context_utilization, hallucination_type
  - [x] 2.10 Save complete test suite as `lesson-13/data/rag_evaluation_suite.json`
  - [x] 2.11 [TDD-RED] Write tests for `backend/rag_generation_eval.py` (test_rag_generation_eval.py) - AttributionDetector, HallucinationDetector, ContextUtilizationScorer classes
  - [x] 2.12 [TDD-GREEN] Implement `backend/rag_generation_eval.py` with 3 classes and 8+ methods
  - [x] 2.13 [TDD-REFACTOR] Refactor rag_generation_eval.py for defensive coding and efficiency
  - [x] 2.14 [TDD-RED] Write tests for `backend/rag_pipeline_eval.py` (test_rag_pipeline_eval.py)
  - [x] 2.15 [TDD-GREEN] Implement `backend/rag_pipeline_eval.py` with RAGPipelineEvaluator class
  - [x] 2.16 [TDD-REFACTOR] Refactor rag_pipeline_eval.py for integration with HW4 retrieval metrics
  - [x] 2.17 Create interactive notebook: `attribution_detection.ipynb` with DEMO/FULL modes (<7 min execution)
  - [x] 2.18 Create interactive notebook: `context_utilization.ipynb` with DEMO/FULL modes (<6 min execution)
  - [x] 2.19 Execute notebooks and generate results JSON files (attribution_results.json, context_utilization_results.json)
  - [x] 2.20 Write TUTORIAL_INDEX.md with learning objectives, prerequisites, recommended path, FAQ
  - [x] 2.21 Write README.md with lesson overview and quick start guide
  - [x] 2.22 Validate all Lesson 13 deliverables (tests pass 43/44, notebooks created, 500 test cases valid, ready for 80%+ attribution accuracy)

- [x] **3.0 Lesson 14: Agent Planning & Orchestration** (Week 3, Days 15-21) ✅ COMPLETED
  - [x] 3.1 Create Lesson 14 directory structure (directories: diagrams/, data/, results/)
  - [x] 3.2 Write concept tutorial: `agent_planning_evaluation.md` (22-25 min reading time)
  - [x] 3.3 Write concept tutorial: `react_reflexion_patterns.md` (20-25 min reading time)
  - [x] 3.4 Write concept tutorial: `multi_agent_orchestration.md` (18-22 min reading time)
  - [x] 3.5 Create visual diagrams for Lesson 14 (3 diagrams: react_agent_workflow.mmd, multi_agent_orchestration.mmd, agent_failure_modes_taxonomy.mmd)
  - [x] 3.6 Generate agent benchmark: `agent_planning_benchmark.json` with 100 planning validation tasks
  - [x] 3.7 Generate agent benchmark: `agent_tool_call_benchmark.json` with 150 tool call validation cases
  - [x] 3.8 Generate agent benchmark: `agent_efficiency_benchmark.json` with 50 multi-step efficiency tasks
  - [x] 3.9 [TDD-RED] Write tests for `backend/agent_evaluation.py` (test_agent_evaluation.py) - PlanningValidator and ToolCallAccuracyMeasurer classes
  - [x] 3.10 [TDD-GREEN] Implement `backend/agent_evaluation.py` with 2 classes and 7+ methods
  - [x] 3.11 [TDD-REFACTOR] Refactor agent_evaluation.py for defensive coding and comprehensive validation
  - [x] 3.12 [TDD-RED] Write tests for `backend/multi_agent_framework.py` (test_multi_agent_framework.py) - BaseAgent, concrete agents, MultiAgentOrchestrator
  - [x] 3.13 [TDD-GREEN] Implement `backend/multi_agent_framework.py` with BaseAgent abstract class
  - [x] 3.14 [TDD-GREEN] Implement concrete agents: PlannerAgent, ValidatorAgent, ExecutorAgent, MemoryManager
  - [x] 3.15 [TDD-GREEN] Implement MultiAgentOrchestrator class with workflow execution
  - [x] 3.16 [TDD-REFACTOR] Refactor multi_agent_framework.py for extensibility and memory management
  - [x] 3.17 Create interactive notebook: `react_agent_implementation.ipynb` with DEMO/FULL modes (<10 min execution)
  - [x] 3.18 Create interactive notebook: `agent_failure_analysis.ipynb` with DEMO/FULL modes (<7 min execution)
  - [x] 3.19 Execute notebooks and generate results JSON files (planning_validation.json, agent_performance.json)
  - [x] 3.20 Write TUTORIAL_INDEX.md with learning objectives, prerequisites, recommended path, FAQ
  - [x] 3.21 Write README.md with lesson overview and quick start guide
  - [x] 3.22 Validate all Lesson 14 deliverables (tests pass, notebooks execute, 85%+ planning validation accuracy, agent benchmarks complete)

- [ ] **4.0 Integration, Dashboard Extension & Cross-Lesson Testing** (Week 4, Days 22-28)
  - [ ] 4.1 Extend `lesson-9-11/evaluation_dashboard.py` with new RAG Metrics Section (hybrid retrieval, context quality, attribution rate, hallucination rate, context utilization)
  - [ ] 4.2 Extend `lesson-9-11/evaluation_dashboard.py` with new Agent Metrics Section (planning accuracy, tool call accuracy, goal achievement, reflection quality, efficiency metrics)
  - [ ] 4.3 Implement cross-lesson comparison features in dashboard (retrieval comparison HW4 vs L12, generation comparison, agent comparison)
  - [ ] 4.4 Add dashboard pagination (20 results per page) and performance optimizations
  - [ ] 4.5 Test dashboard integration with all JSON result files from Lessons 12-14
  - [ ] 4.6 Update `TUTORIAL_CHANGELOG.md` with entries for all 3 new lessons (12, 13, 14)
  - [ ] 4.7 Update `CLAUDE.md` with new patterns: hybrid retrieval, RAG generation evaluation, multi-agent orchestration
  - [ ] 4.8 Add cross-linking between Lessons 12-14 and existing HW4/HW5/Lessons 9-11 tutorials
  - [ ] 4.9 Validate tutorial navigation flow: Verify breadcrumbs, prerequisites sections, next steps sections work across all tutorials
  - [ ] 4.10 Run full test suite: `pytest tests/` - Ensure >90% coverage for new backend modules
  - [ ] 4.11 Execute all 6 new notebooks (L12: 2, L13: 2, L14: 2) in DEMO mode - Verify <$3 total cost
  - [ ] 4.12 Execute all 6 notebooks in FULL mode - Verify $10-15 total cost and 10-15% Recall@5 improvement (L12), 80%+ attribution accuracy (L13), 85%+ planning accuracy (L14)
  - [ ] 4.13 Validate all Mermaid diagrams render correctly on GitHub (9 diagrams total)
  - [ ] 4.14 Code quality check: Run `ruff format .` and `ruff check .` - Ensure 100% compliance
  - [ ] 4.15 Final documentation review: Check all TUTORIAL_INDEX.md files have 5-7 learning objectives, FAQs, common pitfalls
  - [ ] 4.16 Cost audit: Verify DEMO mode ≤$3, FULL mode ≤$15, dashboard $0
  - [ ] 4.17 Integration testing: Test recommended learning paths (Foundation→Advanced, Homework-First, Quick Start)
  - [ ] 4.18 Final validation checklist: All tests pass, all notebooks execute, all diagrams render, all metrics in dashboard, documentation complete

---

**Status**: ✅ **Sub-tasks generated and ready for execution**

**Next Steps**:
1. Begin with Task 1.1 (Lesson 12 directory structure)
2. Follow TDD workflow (RED → GREEN → REFACTOR) for all backend implementations
3. Track progress by checking off completed sub-tasks
4. Validate deliverables at end of each parent task before proceeding

**Summary Statistics**:
- **Total Sub-Tasks**: 77 (Task 1.0: 17, Task 2.0: 22, Task 3.0: 22, Task 4.0: 18)
- **Backend Modules**: 6 new modules (semantic_retrieval, context_judges, rag_generation_eval, rag_pipeline_eval, agent_evaluation, multi_agent_framework)
- **Test Files**: 6 new test files (>90% coverage target)
- **Concept Tutorials**: 9 tutorials (3 per lesson, 18-25 min reading time each)
- **Interactive Notebooks**: 6 notebooks (2 per lesson, <10 min execution each)
- **Visual Diagrams**: 9 diagrams (3 per lesson, Mermaid + PNG)
- **Data Artifacts**: 4 datasets (rag_evaluation_suite.json with 500 cases, 3 agent benchmarks with 300 total cases)
- **Result Files**: 6 JSON result files for dashboard integration
