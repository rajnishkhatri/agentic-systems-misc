# Task List: Tutorial Documentation System

**Based on**: `0002-prd-tutorial-documentation-system.md`

---

## Current State Assessment

### Existing Resources
- **AI_EVALUATION_COMPLETE_GUIDE.md**: Comprehensive 84KB evaluation guide covering all concepts
- **Existing READMEs**: Each homework (hw1-hw5) and lesson (lesson-4, lesson-7, lesson-8) has basic README
- **Existing Notebooks**:
  - `homeworks/hw2/hw2_solution_walkthrough.ipynb`
  - `homeworks/hw3/hw3_walkthrough.ipynb`
- **Existing Explanations**: `lesson-4/EXPLANATION.md` (comprehensive substantiation tutorial)

### Gaps Identified
- No `TUTORIAL_INDEX.md` in any homework/lesson directory
- No concept-specific tutorial breakdowns (error analysis, judge development, etc.)
- No architectural diagrams for evaluation pipelines
- No organized tutorial structure within directories
- Limited interactive notebooks (only hw2 and hw3 have walkthroughs)

### Leverage Opportunities
- Use AI_EVALUATION_COMPLETE_GUIDE.md as reference material for concepts
- Expand existing walkthroughs (hw2, hw3) into comprehensive tutorial series
- Use lesson-4/EXPLANATION.md as template for lesson-style tutorials
- Existing scripts can be directly referenced/explained in tutorials

---

## High-Level Tasks

- [x] **1.0 Create Tutorial Infrastructure and Index System** ✅ COMPLETED
- [x] **2.0 Develop Homework 1-2 Tutorial Series (Foundations)** ✅ COMPLETED
- [ ] **3.0 Develop Homework 3-4 Tutorial Series (Advanced Evaluation)** [9/10 subtasks completed]
- [x] **4.0 Develop Homework 5 and Lesson Tutorials (Specialized Topics)** ✅ COMPLETED
- [ ] **5.0 Create Visual Diagrams and Interactive Notebooks**
- [ ] **6.0 Review, Test, and Document Tutorial System**

---

## Relevant Files

### Tutorial Index Files (New)
- `homeworks/hw1/TUTORIAL_INDEX.md` - Navigation for HW1 tutorials
- `homeworks/hw2/TUTORIAL_INDEX.md` - Navigation for HW2 tutorials
- `homeworks/hw3/TUTORIAL_INDEX.md` - Navigation for HW3 tutorials
- `homeworks/hw4/TUTORIAL_INDEX.md` - Navigation for HW4 tutorials
- `homeworks/hw5/TUTORIAL_INDEX.md` - Navigation for HW5 tutorials
- `lesson-4/TUTORIAL_INDEX.md` - Navigation for Lesson 4 tutorials
- `lesson-7/TUTORIAL_INDEX.md` - Navigation for Lesson 7 tutorials
- `lesson-8/TUTORIAL_INDEX.md` - Navigation for Lesson 8 tutorials

### Homework 1 Tutorials (New)
- `homeworks/hw1/system_prompt_engineering_tutorial.md` - System prompt design principles
- `homeworks/hw1/query_diversity_tutorial.md` - Test query set design

### Homework 2 Tutorials (New)
- `homeworks/hw2/error_analysis_concepts.md` - Error analysis methodology foundations
- `homeworks/hw2/dimension_generation_tutorial.ipynb` - Interactive dimension/tuple generation
- `homeworks/hw2/failure_mode_taxonomy_tutorial.md` - Building failure taxonomies

### Homework 3 Tutorials (Created)
- `homeworks/hw3/llm_judge_concepts.md` - LLM-as-Judge paradigm overview ✅ COMPLETED
- `homeworks/hw3/data_labeling_tutorial.ipynb` - Ground truth creation workflow ✅ COMPLETED
- `homeworks/hw3/judge_development_tutorial.ipynb` - Judge prompt engineering ✅ COMPLETED
- `homeworks/hw3/bias_correction_tutorial.md` - Statistical correction with judgy ✅ COMPLETED
- `homeworks/hw3/diagrams/judge_evaluation_flow.mmd` - Complete judge pipeline visualization ✅ COMPLETED

### Homework 4 Tutorials (Created)
- `homeworks/hw4/rag_evaluation_concepts.md` - RAG architecture and evaluation ✅ COMPLETED
- `homeworks/hw4/synthetic_query_generation_tutorial.ipynb` - Query generation strategies ✅ COMPLETED
- `homeworks/hw4/retrieval_metrics_tutorial.md` - Recall@k and MRR explained ✅ COMPLETED
- `homeworks/hw4/diagrams/rag_architecture.mmd` - RAG pipeline visualization ✅ COMPLETED
- `homeworks/hw4/query_rewrite_agent_tutorial.ipynb` - Agent-enhanced retrieval (optional) ⏸️ DEFERRED

### Homework 5 Tutorials (Created)
- `homeworks/hw5/transition_analysis_concepts.md` - Failure transition matrices and state-based modeling ✅ COMPLETED
- `homeworks/hw5/heatmap_visualization_tutorial.ipynb` - Interactive matrix construction and visualization ✅ COMPLETED
- `homeworks/hw5/diagrams/transition_matrix_concept.mmd` - 10-state recipe bot pipeline with success/failure paths ✅ COMPLETED

### Lesson 4 Tutorials (Created)
- `lesson-4/substantiation_concepts.md` - Substantiation vs hallucination, tool grounding concepts ✅ COMPLETED
- `lesson-4/data_preprocessing_tutorial.md` - CSV to JSON conversion patterns with error handling ✅ COMPLETED
- `lesson-4/parallel_labeling_tutorial.ipynb` - ThreadPoolExecutor with 64 workers for parallel LLM labeling ✅ COMPLETED
- `lesson-4/judge_evaluation_pipeline_tutorial.ipynb` - End-to-end evaluation with hash-based splitting ✅ COMPLETED
- `lesson-4/diagrams/substantiation_pipeline.mmd` - 3-stage pipeline (Clean → Label → Evaluate) ✅ COMPLETED

### Lesson 7 Tutorials (Created)
- `lesson-7/trace_inspection_concepts.md` - Manual vs automated evaluation methodologies ✅ COMPLETED
- `lesson-7/csv_conversion_tutorial.md` - JSON to spreadsheet conversion with role prefixes ✅ COMPLETED
- `lesson-7/labeling_tool_tutorial.md` - FastAPI web annotation interface with keyboard shortcuts ✅ COMPLETED
- `lesson-7/diagrams/annotation_workflow.mmd` - Export → Convert → Annotate → Analyze workflow ✅ COMPLETED

### Lesson 8 Tutorials (Created)
- `lesson-8/model_cascade_concepts.md` - Cascade architecture, logprobs, cost-accuracy trade-offs ✅ COMPLETED
- `lesson-8/spam_classification_tutorial.ipynb` - SMS spam classification with threshold optimization ✅ COMPLETED
- `lesson-8/diagrams/cascade_decision_tree.mmd` - Routing logic with confidence-based decisions ✅ COMPLETED

### Diagram Files (Created)
- `homeworks/hw2/diagrams/error_analysis_pipeline.mmd` - Error analysis workflow ✅ COMPLETED
- `homeworks/hw3/diagrams/judge_evaluation_flow.mmd` - Judge development pipeline ✅ COMPLETED
- `homeworks/hw4/diagrams/rag_architecture.mmd` - RAG system architecture ✅ COMPLETED
- `homeworks/hw5/diagrams/transition_matrix_concept.mmd` - State transition visualization ✅ COMPLETED
- `lesson-4/diagrams/substantiation_pipeline.mmd` - Substantiation evaluation flow ✅ COMPLETED
- `lesson-7/diagrams/annotation_workflow.mmd` - Inspection interface workflow ✅ COMPLETED
- `lesson-8/diagrams/cascade_decision_tree.mmd` - Model cascade routing ✅ COMPLETED

### Existing Files to Update
- `README.md` - Add "Tutorials" section linking to all tutorial indices
- `CLAUDE.md` - Update with tutorial workflow instructions
- `homeworks/hw1/readme.md` - Add link to TUTORIAL_INDEX.md
- `homeworks/hw2/README.md` - Add link to TUTORIAL_INDEX.md
- `homeworks/hw3/README.md` - Add link to TUTORIAL_INDEX.md
- `homeworks/hw4/README.md` - Add link to TUTORIAL_INDEX.md
- `homeworks/hw5/README.md` - Add link to TUTORIAL_INDEX.md
- `lesson-4/EXPLANATION.md` - Integrate into tutorial system
- `lesson-7/README.md` - Add link to TUTORIAL_INDEX.md

### Notes
- All Jupyter notebooks should include setup cells for environment configuration
- Diagrams use Mermaid syntax for GitHub rendering; export PNGs for complex diagrams
- Tutorials reference existing scripts in `/backend/`, `/scripts/`, and homework directories
- No test files needed (documentation only, no executable code beyond notebooks)

---

## Tasks

- [x] **1.0 Create Tutorial Infrastructure and Index System**
  - [x] 1.1 Create directory structure for tutorials (concepts/, notebooks/, diagrams/ subdirectories in each homework/lesson)
  - [x] 1.2 Write `homeworks/hw1/TUTORIAL_INDEX.md` with overview and navigation
  - [x] 1.3 Write `homeworks/hw2/TUTORIAL_INDEX.md` with overview and navigation
  - [x] 1.4 Write `homeworks/hw3/TUTORIAL_INDEX.md` with overview and navigation
  - [x] 1.5 Write `homeworks/hw4/TUTORIAL_INDEX.md` with overview and navigation
  - [x] 1.6 Write `homeworks/hw5/TUTORIAL_INDEX.md` with overview and navigation
  - [x] 1.7 Write `lesson-4/TUTORIAL_INDEX.md` with overview and navigation
  - [x] 1.8 Write `lesson-7/TUTORIAL_INDEX.md` with overview and navigation
  - [x] 1.9 Write `lesson-8/TUTORIAL_INDEX.md` with overview and navigation
  - [x] 1.10 Update main `README.md` with "Tutorials" section linking to all indices
  - [x] 1.11 Update `CLAUDE.md` with tutorial workflow instructions
  - [x] 1.12 Update each homework/lesson README to link to their TUTORIAL_INDEX.md

- [x] **2.0 Develop Homework 1-2 Tutorial Series (Foundations)**
  - [x] 2.1 Write `homeworks/hw1/system_prompt_engineering_tutorial.md` (concepts, examples, testing strategies)
  - [x] 2.2 Write `homeworks/hw1/query_diversity_tutorial.md` (dimension identification, coverage analysis)
  - [x] 2.3 Write `homeworks/hw2/error_analysis_concepts.md` (qualitative evaluation, open/axial coding methodology)
  - [x] 2.4 Create `homeworks/hw2/dimension_generation_tutorial.ipynb` (interactive walkthrough with LLM tuple generation)
  - [x] 2.5 Write `homeworks/hw2/failure_mode_taxonomy_tutorial.md` (taxonomy building, definition writing, examples)
  - [x] 2.6 Create Mermaid diagram `homeworks/hw2/diagrams/error_analysis_pipeline.mmd` (dimension → tuples → queries → analysis flow)

- [ ] **3.0 Develop Homework 3-4 Tutorial Series (Advanced Evaluation)** [9/10 subtasks completed]
  - [x] 3.1 Write `homeworks/hw3/llm_judge_concepts.md` (LLM-as-Judge paradigm, when to use, bias considerations)
  - [x] 3.2 Create `homeworks/hw3/data_labeling_tutorial.ipynb` (ground truth creation, train/dev/test splits, labeling strategies)
  - [x] 3.3 Create `homeworks/hw3/judge_development_tutorial.ipynb` (prompt engineering, few-shot selection, structured output with Pydantic)
  - [x] 3.4 Write `homeworks/hw3/bias_correction_tutorial.md` (TPR/TNR calculation, judgy library usage, confidence intervals)
  - [x] 3.5 Create Mermaid diagram `homeworks/hw3/diagrams/judge_evaluation_flow.mmd` (labeling → splitting → judge development → evaluation pipeline)
  - [x] 3.6 Write `homeworks/hw4/rag_evaluation_concepts.md` (RAG architecture, BM25 intuition, retrieval vs generation evaluation)
  - [x] 3.7 Create `homeworks/hw4/synthetic_query_generation_tutorial.ipynb` (salient fact extraction, parallel processing, quality review)
  - [x] 3.8 Write `homeworks/hw4/retrieval_metrics_tutorial.md` (Recall@k, MRR interpretation, baselines, use cases)
  - [ ] 3.9 Create `homeworks/hw4/query_rewrite_agent_tutorial.ipynb` (optional: agent-enhanced retrieval, strategy comparison) ⏸️ DEFERRED - Optional advanced tutorial, deferred to maintain quality within token constraints
  - [x] 3.10 Create Mermaid diagram `homeworks/hw4/diagrams/rag_architecture.mmd` (query → retrieval → generation → evaluation flow)

- [x] **4.0 Develop Homework 5 and Lesson Tutorials (Specialized Topics)** ✅ COMPLETED
  - [x] 4.1 Write `homeworks/hw5/transition_analysis_concepts.md` (state-based modeling, transition matrices, bottleneck identification)
  - [x] 4.2 Create `homeworks/hw5/heatmap_visualization_tutorial.ipynb` (data loading, matrix construction, seaborn visualization, interpretation)
  - [x] 4.3 Create Mermaid diagram `homeworks/hw5/diagrams/transition_matrix_concept.mmd` (state transitions with success/failure paths)
  - [x] 4.4 Write `lesson-4/substantiation_concepts.md` (substantiation definition, tool grounding, verifiability criteria)
  - [x] 4.5 Write `lesson-4/data_preprocessing_tutorial.md` (CSV to JSON conversion, handling malformed data, incremental processing)
  - [x] 4.6 Create `lesson-4/parallel_labeling_tutorial.ipynb` (ThreadPoolExecutor patterns, rate limiting, progress tracking, cost optimization)
  - [x] 4.7 Create `lesson-4/judge_evaluation_pipeline_tutorial.ipynb` (end-to-end workflow, dataset splitting, metric reporting)
  - [x] 4.8 Create Mermaid diagram `lesson-4/diagrams/substantiation_pipeline.mmd` (clean logs → label → split → judge → metrics)
  - [x] 4.9 Write `lesson-7/trace_inspection_concepts.md` (manual vs automated evaluation, when human review is necessary)
  - [x] 4.10 Write `lesson-7/csv_conversion_tutorial.md` (JSON to CSV transformation, formatting for readability, handling nested data)
  - [x] 4.11 Write `lesson-7/labeling_tool_tutorial.md` (annotation UI design, if web interface is built)
  - [x] 4.12 Create Mermaid diagram `lesson-7/diagrams/annotation_workflow.mmd` (trace export → conversion → annotation → analysis)
  - [x] 4.13 Write `lesson-8/model_cascade_concepts.md` (cascade architecture, cost-accuracy trade-offs, routing strategies)
  - [x] 4.14 Create `lesson-8/spam_classification_tutorial.ipynb` (binary classification, logprob confidence, cascade implementation, cost analysis)
  - [x] 4.15 Create Mermaid diagram `lesson-8/diagrams/cascade_decision_tree.mmd` (routing logic based on confidence thresholds)

- [ ] **5.0 Create Visual Diagrams and Interactive Notebooks**
  - [ ] 5.1 Export all Mermaid diagrams (.mmd files) to high-resolution PNGs for complex diagrams (>10 nodes)
  - [ ] 5.2 Ensure all Jupyter notebooks include setup cells (imports, path configuration, .env loading)
  - [ ] 5.3 Execute all notebooks end-to-end to populate output cells with real results
  - [ ] 5.4 Add validation/assertion cells in notebooks to verify intermediate results
  - [ ] 5.5 Add cost warnings and estimated runtime to notebooks that call LLM APIs
  - [ ] 5.6 Test all notebooks for executability in fresh virtual environment
  - [ ] 5.7 Add "Quick Run" vs "Full Run" options for time-consuming evaluations
  - [ ] 5.8 Ensure consistent visual styling across all diagrams (colors, shapes per PRD conventions)

- [ ] **6.0 Review, Test, and Document Tutorial System**
  - [ ] 6.1 Review all tutorials for consistent structure (Learning Objectives, Prerequisites, Concepts, Implementation, Pitfalls, Takeaways)
  - [ ] 6.2 Review all tutorials for consistent tone (formal concepts + casual walkthroughs)
  - [ ] 6.3 Verify all cross-references and links between tutorials work correctly
  - [ ] 6.4 Verify all code file references use correct relative paths
  - [ ] 6.5 Test tutorial navigation flow (can a student follow recommended reading order?)
  - [ ] 6.6 Validate worked examples produce expected outputs on real datasets
  - [ ] 6.7 Create `TUTORIAL_CHANGELOG.md` to track future updates needed when code changes
  - [ ] 6.8 Document VS Code extensions needed for Mermaid rendering in development
  - [ ] 6.9 Run spell check and grammar review on all tutorial markdown files
  - [ ] 6.10 Conduct pilot test with 1-2 students (if available) and gather feedback

---

## Estimated Effort

- **Task 1.0 (Infrastructure)**: 4-6 hours
- **Task 2.0 (HW1-2 Tutorials)**: 8-10 hours
- **Task 3.0 (HW3-4 Tutorials)**: 12-15 hours
- **Task 4.0 (HW5 & Lessons)**: 15-18 hours
- **Task 5.0 (Diagrams & Notebooks)**: 8-10 hours
- **Task 6.0 (Review & QA)**: 6-8 hours

**Total Estimated Effort**: 53-67 hours

---

## Implementation Notes

### Tutorial Writing Priorities
1. Start with infrastructure (Task 1.0) to establish navigation
2. Begin content with foundational topics (HW1-2) before advanced (HW3-4)
3. Create diagrams iteratively as tutorials are written
4. Execute and validate notebooks after completing each homework's tutorials
5. Reserve review/QA until all content is drafted

### Leverage Existing Content
- Extract concepts from `AI_EVALUATION_COMPLETE_GUIDE.md` for conceptual tutorials
- Expand `homeworks/hw2/hw2_solution_walkthrough.ipynb` into multiple focused notebooks
- Use `lesson-4/EXPLANATION.md` as template for detailed lesson tutorials
- Reference existing scripts extensively (avoid code duplication)

### Quality Standards
- Each tutorial must be readable in 15-30 minutes
- Notebooks should execute in <5 minutes (or provide "quick run" option)
- Diagrams must be understandable without reading code
- All worked examples use real course datasets (no toy data)

### Maintenance Strategy
- Track code changes that affect tutorials in `TUTORIAL_CHANGELOG.md`
- Use GitHub line-specific links for code references (enables change detection)
- Schedule tutorial review each semester before course starts
- Encourage student contributions via pull requests for minor fixes
