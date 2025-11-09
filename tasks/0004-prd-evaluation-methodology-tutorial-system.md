# PRD: Evaluation Methodology Tutorial System

## Introduction/Overview

This PRD defines the development of a comprehensive **Evaluation Methodology Tutorial System** consisting of three lesson-based deep-dive tutorials (Lessons 9, 10, 11) that systematically teach AI evaluation techniques from foundational metrics to production-grade comparative evaluation frameworks.

### Problem Statement

Current evaluation education in the AI course has practical implementations (HW1-5, Lessons 4, 7-8) but lacks theoretical depth on evaluation methodology. Students need:
- Deep understanding of evaluation challenges specific to foundation models
- Knowledge of language modeling metrics and their interpretation
- Mastery of exact evaluation methods (functional correctness, similarity measurements)
- Production-grade AI-as-judge patterns beyond basic HW3 implementation
- Comparative evaluation techniques for model ranking and A/B testing
- Unified evaluation dashboard to visualize metrics across all assignments

### Goal

Build a **three-lesson tutorial system** that bridges the gap between practical assignments and rigorous evaluation theory, providing students with production-ready evaluation infrastructure and comprehensive understanding of modern AI evaluation methodologies.

---

## Goals

1. **Comprehensive Coverage**: Address all major evaluation topics from Chapter 3 (Eval.txt) through progressive lesson structure
2. **Production Readiness**: Deliver reference implementations with defensive coding, type hints, and >90% test coverage
3. **Practical Integration**: Extend existing workspace evaluation utilities (HW3 judges, HW4 retrieval metrics) with advanced techniques
4. **Cost Efficiency**: All interactive notebooks execute in <$5 total, with DEMO modes for <$1 exploration
5. **Self-Paced Learning**: Support beginner (skip metrics) to advanced (complete deep-dives) learning paths
6. **Reusable Assets**: Create evaluation template library saving 50%+ development time on new judges

---

## User Stories

### Story 1: Beginner Learner (Skip Theory, Focus Practice)
**As a** beginner student new to AI evaluation
**I want to** skip language modeling metrics and focus on AI-as-judge implementation
**So that** I can quickly build practical evaluation systems without getting overwhelmed by theory

**Acceptance Criteria**:
- Tutorial index clearly marks "optional" vs "required" sections
- Lesson 10 (AI-as-judge) is self-contained without requiring Lesson 9 completion
- Quick-start guides provide 30-minute paths to working judges

### Story 2: Advanced Learner (Complete Deep-Dive)
**As an** advanced student preparing for production ML roles
**I want to** understand perplexity, cross-entropy, and statistical evaluation rigor
**So that** I can evaluate models scientifically and communicate results with confidence intervals

**Acceptance Criteria**:
- Lesson 9 covers perplexity calculation with worked examples
- Notebooks include mathematical formulas with LaTeX rendering
- Advanced sections explain when metrics fail and their limitations

### Story 3: Practitioner Building Evaluation Pipeline
**As a** developer building a recipe chatbot
**I want to** reuse evaluation templates and utilities
**So that** I can implement judges, retrieval metrics, and comparative tests without writing from scratch

**Acceptance Criteria**:
- `templates/judge_prompts/` contains 15+ reusable prompts (dietary, toxicity, factuality, etc.)
- `backend/exact_evaluation.py` provides drop-in similarity measurement functions
- `backend/ai_judge_framework.py` offers `BaseJudge` abstraction for rapid prototyping

### Story 4: Researcher Comparing Models
**As a** researcher evaluating multiple LLM models
**I want to** implement Elo/Bradley-Terry ranking with statistical significance
**So that** I can create private leaderboards and report which model is best with confidence

**Acceptance Criteria**:
- Lesson 11 implements Elo and Bradley-Terry algorithms
- Notebooks generate pairwise comparison datasets from chatbot responses
- Dashboard visualizes model rankings with confidence intervals

### Story 5: Student Tracking Progress
**As a** student juggling multiple assignments
**I want to** see all my evaluation metrics in one unified dashboard
**So that** I can quickly assess bot performance across dimensions without running separate scripts

**Acceptance Criteria**:
- Evaluation dashboard integrates HW3 judge TPR/TNR, HW4 retrieval Recall@k/MRR, Lesson metrics
- Dashboard auto-refreshes from JSON result files
- Export functionality generates PDF/HTML reports for submissions

---

## Functional Requirements

### Lesson 9: Evaluation Fundamentals & Exact Methods

#### FR-L9.1: Concept Tutorials (Markdown)
The system **must** provide the following markdown tutorials:
- `evaluation_fundamentals.md` (reading time: 20-25 min)
  - Challenges of evaluating foundation models
  - Open-ended vs close-ended evaluation
  - Benchmark saturation and evolution
- `language_modeling_metrics.md` (reading time: 15-20 min)
  - Entropy, cross-entropy, perplexity formulas and interpretation
  - Bits-per-character (BPC), bits-per-byte (BPB) variations
  - When perplexity is misleading (post-training, quantization)
- `exact_evaluation_methods.md` (reading time: 20-25 min)
  - Functional correctness for code/SQL generation
  - Exact match, fuzzy matching, n-gram similarity
  - Lexical vs semantic similarity
  - Embedding-based evaluation

#### FR-L9.2: Interactive Notebooks (Jupyter)
The system **must** provide the following executable notebooks:
- `perplexity_calculation_tutorial.ipynb`
  - Calculate perplexity for GPT-2 on sample text
  - Visualize perplexity vs model size
  - Demonstrate perplexity for data contamination detection
  - Execution time: <3 minutes, Cost: $0 (uses local calculations)

- `similarity_measurements_tutorial.ipynb`
  - Implement exact match, fuzzy match, BLEU score
  - Compute cosine similarity for embeddings
  - Compare lexical vs semantic similarity on recipe queries
  - Execution time: <5 minutes, Cost: $0.20-0.50 (embedding API calls)

#### FR-L9.3: Reference Implementation
The system **must** provide `backend/exact_evaluation.py` with:
- `calculate_perplexity(text: str, model: str) -> float`
- `exact_match(generated: str, reference: list[str]) -> bool`
- `fuzzy_match(generated: str, reference: str, threshold: float = 0.8) -> float`
- `bleu_score(generated: str, references: list[str]) -> float`
- `semantic_similarity(text1: str, text2: str, model: str = "text-embedding-3-small") -> float`
- All functions with defensive coding (type hints, input validation, docstrings)

#### FR-L9.4: Visual Diagrams
The system **must** provide:
- `diagrams/evaluation_taxonomy.mmd` - Mermaid flowchart of evaluation method decision tree
- `diagrams/embedding_similarity_concept.png` - Visual explanation of cosine similarity

---

### Lesson 10: AI-as-Judge Mastery & Production Patterns

#### FR-L10.1: Concept Tutorials (Markdown)
The system **must** provide:
- `ai_judge_production_guide.md` (reading time: 25-30 min)
  - When to use AI-as-judge vs human evaluation
  - Judge prompt engineering: task definition, criteria, scoring systems, few-shot examples
  - Model selection trade-offs (strong vs weak vs specialized judges)
  - Judge biases: self-bias, position bias, verbosity bias
  - Cost, latency, and consistency considerations
  - Production deployment patterns (guardrails, spot-checking, parallel judges)

#### FR-L10.2: Interactive Notebooks (Jupyter)
The system **must** provide:
- `judge_prompt_engineering_tutorial.ipynb`
  - Engineer judges for 5 criteria (dietary adherence, factuality, toxicity, coherence, helpfulness)
  - Test classification vs discrete vs continuous scoring
  - Measure impact of few-shot examples (0-shot → 1-shot → 5-shot)
  - Compare GPT-4o-mini vs GPT-4o judge performance
  - DEMO mode: 20 examples, $0.30-0.50
  - FULL mode: 100 examples, $1.50-2.50

- `judge_bias_detection_tutorial.ipynb`
  - Detect self-bias by comparing model judging itself vs others
  - Measure position bias with A/B order swapping
  - Identify verbosity bias by comparing long vs short responses
  - Execution time: <5 minutes, Cost: $0.50-1.00

#### FR-L10.3: Evaluation Templates
The system **must** provide `templates/judge_prompts/` with 15+ reusable prompts:
- `dietary_adherence_judge.txt` (from HW3, refined)
- `factual_correctness_judge.txt`
- `toxicity_detection_judge.txt`
- `coherence_judge.txt`
- `helpfulness_judge.txt`
- `substantiation_judge.txt` (from Lesson 4, generalized)
- `hallucination_detection_judge.txt`
- `safety_judge.txt`
- `cultural_sensitivity_judge.txt`
- `response_length_appropriateness_judge.txt`
- Each template with placeholders: `__QUERY__`, `__RESPONSE__`, `__CONTEXT__`, `__CRITERIA__`

#### FR-L10.4: Reference Implementation
The system **must** provide `backend/ai_judge_framework.py` with:
- `BaseJudge` abstract class with methods:
  - `judge(query: str, response: str, context: dict[str, Any] = None) -> JudgeResult`
  - `batch_judge(queries: list[tuple[str, str]], max_workers: int = 32) -> list[JudgeResult]`
  - `calculate_tpr_tnr(predictions: list[JudgeResult], ground_truth: list[bool]) -> tuple[float, float]`
- Concrete implementations:
  - `DietaryAdherenceJudge` (extends HW3 patterns)
  - `SubstantiationJudge` (generalizes Lesson 4 patterns)
  - `GenericCriteriaJudge` (configurable with any template)
- Pydantic models for structured outputs

#### FR-L10.5: Visual Diagrams
The system **must** provide:
- `diagrams/judge_decision_tree.mmd` - When to use which judge type
- `diagrams/judge_bias_patterns.png` - Visualization of common biases

---

### Lesson 11: Comparative Evaluation & Leaderboards

#### FR-L11.1: Concept Tutorials (Markdown)
The system **must** provide:
- `comparative_evaluation_guide.md` (reading time: 20-25 min)
  - Pointwise vs comparative evaluation
  - When comparative is easier than absolute scoring
  - Rating algorithms: Elo, Bradley-Terry, TrueSkill
  - Transitivity assumptions and violations
  - Crowdsourced vs expert evaluation trade-offs
  - Standardization challenges (prompt diversity, quality control)
  - A/B testing vs comparative evaluation

#### FR-L11.2: Interactive Notebooks (Jupyter)
The system **must** provide:
- `elo_ranking_tutorial.ipynb`
  - Implement Elo algorithm for model ranking
  - Generate pairwise comparisons from recipe bot responses
  - Calculate Elo scores with confidence intervals
  - Visualize leaderboard evolution over time
  - Execution time: <5 minutes, Cost: $0 (uses pre-generated comparisons)

- `ab_testing_vs_comparative_eval.ipynb`
  - Compare A/B testing (sequential exposure) vs side-by-side comparison
  - Measure which method provides faster signal
  - Analyze sample size requirements
  - Execution time: <3 minutes, Cost: $0 (simulation-based)

- `bradley_terry_ranking_tutorial.ipynb`
  - Implement Bradley-Terry model
  - Compare with Elo on same dataset
  - Identify when Bradley-Terry is preferable
  - Execution time: <4 minutes, Cost: $0

#### FR-L11.3: Reference Implementation
The system **must** provide `backend/comparative_evaluation.py` with:
- `EloRanking` class with methods:
  - `record_match(model_a: str, model_b: str, winner: str, k_factor: float = 32)`
  - `get_rankings() -> dict[str, float]`
  - `predict_win_probability(model_a: str, model_b: str) -> float`
- `BradleyTerryRanking` class with similar interface
- `generate_pairwise_comparisons(responses: list[dict], judge: BaseJudge) -> list[dict]`
- `visualize_leaderboard(rankings: dict[str, float], output_path: Path)`

#### FR-L11.4: Dataset Examples
The system **must** provide:
- `data/pairwise_comparisons.json` - 100 pairwise comparisons of recipe bot responses
  - Structure: `[{"query": str, "response_a": str, "response_b": str, "winner": "A"|"B"|"TIE", "rationale": str}]`
  - Covers dietary adherence, retrieval quality, response coherence dimensions

#### FR-L11.5: Visual Diagrams
The system **must** provide:
- `diagrams/ranking_algorithm_comparison.mmd` - Elo vs Bradley-Terry decision flowchart
- `diagrams/comparative_eval_workflow.png` - End-to-end comparative evaluation pipeline

---

### Cross-Lesson: Evaluation Dashboard

#### FR-DASH.1: Unified Dashboard
The system **must** provide `lesson-9-11/evaluation_dashboard.py` with:
- FastHTML + MonsterUI web interface
- Real-time metrics display:
  - **HW3 Metrics**: Judge TPR/TNR, confusion matrix, corrected success rate (θ̂), 95% CI
  - **HW4 Metrics**: Retrieval Recall@1/3/5/10, MRR, query success rate
  - **Lesson 9 Metrics**: Perplexity, BLEU scores, semantic similarity distributions
  - **Lesson 10 Metrics**: Judge performance by criteria, bias detection results
  - **Lesson 11 Metrics**: Model rankings (Elo scores), pairwise win rates
- Auto-refresh from JSON result files (every 5 seconds)
- Cost tracker: cumulative LLM API spending across all evaluations
- Export to PDF/HTML reports

#### FR-DASH.2: Error Analysis Drill-Down
The dashboard **must** provide:
- Click on any metric → view detailed examples
- Filter by query type, failure mode, model
- Side-by-side comparison of responses for failed examples
- Export filtered datasets for further analysis

---

### Cross-Lesson: Tutorial Infrastructure

#### FR-INFRA.1: TUTORIAL_INDEX.md for Each Lesson
Each lesson **must** have:
- Learning objectives (5-7 bullet points)
- Prerequisites (what to complete first)
- Recommended learning path (flowchart)
- Tutorial list with reading/execution times and costs
- Key concepts (3-5 explanations)
- Common pitfalls (5-7 warnings)
- FAQ (5-7 questions)
- Next steps and connections to other tutorials

#### FR-INFRA.2: Notebook Quality Standards
All notebooks **must**:
- Execute in <5 minutes (or provide "Quick Run" option with subset)
- Include cost warnings at top with DEMO vs FULL mode options
- Use assertions for automated validation (e.g., `assert recall_5 > 0.3, "Retrieval baseline too low"`)
- Provide clear markdown explanations between code cells
- Export results to JSON for dashboard integration
- Handle API errors gracefully with retry logic

#### FR-INFRA.3: Diagram Standards
All diagrams **must**:
- Use Mermaid (.mmd) for GitHub rendering
- Export to PNG for complex diagrams (>10 nodes)
- Include descriptive captions
- Be understandable without reading code

---

## Non-Goals (Out of Scope)

1. **Training Language Models from Scratch**: Tutorials will NOT cover training foundation models, only using pre-trained models for evaluation
2. **Fine-Tuning Embedding Models**: Will use existing embedding APIs (OpenAI, Cohere), not custom embedding training
3. **Building Custom LLMs for Judging**: Will use existing LLM APIs as judges, not training specialized judge models
4. **Statistical Significance Testing**: Will report confidence intervals but not deep-dive into hypothesis testing, p-values, effect sizes
5. **Production Deployment Architecture**: Will show evaluation patterns but not Kubernetes, Docker, CI/CD for deploying evaluators
6. **Cost Optimization Strategies Beyond Spot-Checking**: Will mention parallel processing and batch APIs but not advanced cost reduction techniques
7. **Creating New Public Benchmarks**: Will teach evaluation methodology but not how to submit benchmarks to HuggingFace, Papers with Code
8. **Real-Time Evaluation Streaming**: Dashboard will refresh periodically, not provide WebSocket-based live streaming
9. **Multi-Modal Evaluation**: Will focus on text evaluation, not image, audio, or video evaluation techniques

---

## Design Considerations

### UI/UX Requirements
- Dashboard accessible at `http://localhost:8000/evaluation` when running `python lesson-9-11/evaluation_dashboard.py`
- Responsive design for 1920x1080 and 1366x768 resolutions
- Dark mode support (MonsterUI default theme)
- Keyboard shortcuts: `r` for refresh, `e` for export, `f` for filter

### Tutorial Navigation
- Cross-linking between tutorials via Markdown links
- Breadcrumb navigation in TUTORIAL_INDEX.md
- "Prerequisites" section at top of each tutorial
- "Next Steps" section at bottom with logical progression

### Code Style
- Follow project's TDD and defensive coding standards (CLAUDE.md)
- Ruff formatting, line length 120 characters
- Type hints for all functions
- Docstrings following Google style
- Test coverage >90% for reference implementations

---

## Technical Considerations

### Dependencies
**New libraries to add to pyproject.toml**:
- `scikit-learn` (already present) - For confusion matrices, additional metrics
- `nltk` - For BLEU score implementation
- `sentence-transformers` - For local embedding generation (optional)
- `trueskill` - For TrueSkill algorithm (Lesson 11)
- No additional dependencies needed (leverage existing stack)

### Performance Considerations
- Parallel processing with `ThreadPoolExecutor` (32-64 workers for judge evaluations)
- Caching: Save BM25 indices, embedding results to avoid re-computation
- Batch API calls where possible (litellm supports batching)
- Dashboard pagination: Show 20 results per page to avoid rendering slowdowns

### Integration Points
- **Extend `backend/evaluation_utils.py`**: Add semantic similarity methods to `BaseRetrievalEvaluator`
- **Unify HW3 and Lesson 4 judges**: Extract common patterns into `backend/ai_judge_framework.py`
- **Dashboard data ingestion**: Read JSON from `homeworks/hw3/results/`, `homeworks/hw4/results/`, `lesson-*/results/`
- **Cross-tutorial datasets**: Use `data/sample_queries.csv` (HW1), `data/synthetic_queries.json` (HW4) across lessons

### Data Requirements
- Pre-generated pairwise comparisons dataset (100 examples) to avoid tutorial execution costs
- Sample perplexity calculations for common models (GPT-2, Llama) to avoid API calls
- Cached embeddings for 500 recipe queries to enable offline notebook execution

---

## Success Metrics

### Learning Outcomes (Measured via Post-Tutorial Surveys)
- 90% of students report understanding when to use AI-as-judge vs human evaluation
- 80% of students successfully implement a custom judge for their domain
- 70% of students can explain perplexity and its limitations

### Code Quality (Automated Checks)
- 100% of reference implementations pass Ruff formatting
- >90% test coverage for all modules in `backend/`
- All notebooks execute without errors in <5 minutes

### Tutorial Engagement (Analytics)
- Average completion time: 8-12 hours for full deep-dive
- 60% of students complete at least 2 of 3 lessons
- 40% of students complete all 3 lessons

### Reusability (Usage Tracking)
- 50% of students use judge prompt templates without modification
- 30% of students integrate dashboard into their workflows
- 20% of students contribute new judge templates to the library

### Cost Efficiency (Budget Tracking)
- Total notebook execution cost <$5 for FULL mode across all lessons
- DEMO mode enables exploration for <$1 total
- Dashboard operates at $0 (no API calls)

---

## Open Questions

1. **Embedding Provider**: Should we use OpenAI `text-embedding-3-small` (fastest, cheapest) or Cohere `embed-english-v3.0` (better quality) for semantic similarity tutorials?
   - **Decision needed by**: Before implementing Lesson 9.2 notebooks
   - **Recommendation**: OpenAI for cost, provide optional Cohere comparison

2. **Comparative Evaluation UI**: Should pairwise comparisons be collected via dashboard or via separate script?
   - **Decision needed by**: Before implementing Lesson 11.2
   - **Recommendation**: Separate script for data generation, dashboard for visualization only

3. **Judge Template Licensing**: Can we include templates inspired by Azure AI Studio, MLflow prompts with attribution?
   - **Decision needed by**: Before creating `templates/judge_prompts/`
   - **Recommendation**: Create original templates, cite inspirations in comments

4. **Lesson Ordering**: Should Lesson 9 (metrics) come before Lesson 10 (judges), or should we offer flexible ordering?
   - **Decision needed by**: Before writing TUTORIAL_INDEX.md
   - **Recommendation**: Flexible ordering, make Lesson 10 self-contained for practitioners

5. **Dashboard Framework**: FastHTML + MonsterUI (current stack) or Streamlit (more familiar to students)?
   - **Decision needed by**: Before implementing dashboard
   - **Recommendation**: FastHTML for consistency with project, Streamlit as optional alternative in appendix

6. **Test Data Generation**: Should we generate 100 pairwise comparisons manually or use GPT-4o to simulate them?
   - **Decision needed by**: Before Lesson 11 dataset creation
   - **Recommendation**: Use GPT-4o for 80 examples, manually review and fix 20 edge cases

---

## Timeline & Milestones

### Phase 1: Setup & Lesson 9 (Week 1)
- **Day 1-2**: Create directory structure, TUTORIAL_INDEX.md templates
- **Day 3-4**: Write Lesson 9 concept tutorials (evaluation_fundamentals.md, language_modeling_metrics.md, exact_evaluation_methods.md)
- **Day 5-6**: Implement Lesson 9 notebooks (perplexity_calculation, similarity_measurements)
- **Day 7**: Create Lesson 9 reference implementation (`backend/exact_evaluation.py`) and diagrams

**Milestone**: Lesson 9 complete and validated (notebooks execute, tests pass)

### Phase 2: Lesson 10 (Week 2)
- **Day 8-9**: Write Lesson 10 concept tutorial (ai_judge_production_guide.md)
- **Day 10-11**: Create 15 judge prompt templates in `templates/judge_prompts/`
- **Day 12-13**: Implement Lesson 10 notebooks (judge_prompt_engineering, judge_bias_detection)
- **Day 14**: Create `backend/ai_judge_framework.py` with `BaseJudge`, concrete implementations

**Milestone**: Lesson 10 complete, templates ready for reuse

### Phase 3: Lesson 11 (Week 3)
- **Day 15-16**: Write Lesson 11 concept tutorial (comparative_evaluation_guide.md)
- **Day 17-18**: Implement Lesson 11 notebooks (elo_ranking, bradley_terry, ab_testing_vs_comparative)
- **Day 19**: Create `backend/comparative_evaluation.py` and generate pairwise comparisons dataset
- **Day 20-21**: Build diagrams for Lesson 11

**Milestone**: All 3 lessons complete with notebooks and reference code

### Phase 4: Dashboard & Integration (Week 4)
- **Day 22-24**: Implement `evaluation_dashboard.py` with FastHTML + MonsterUI
- **Day 25**: Integrate all lesson metrics into dashboard
- **Day 26-27**: Test cross-lesson navigation, update CLAUDE.md, create TUTORIAL_CHANGELOG.md
- **Day 28**: Final validation, cost auditing, documentation review

**Milestone**: Complete tutorial system delivered, all tests passing

---

## Appendix A: File Structure

```
recipe-chatbot/
├── lesson-9/
│   ├── TUTORIAL_INDEX.md
│   ├── README.md
│   ├── evaluation_fundamentals.md
│   ├── language_modeling_metrics.md
│   ├── exact_evaluation_methods.md
│   ├── perplexity_calculation_tutorial.ipynb
│   ├── similarity_measurements_tutorial.ipynb
│   ├── diagrams/
│   │   ├── evaluation_taxonomy.mmd
│   │   └── embedding_similarity_concept.png
│   └── data/
│       └── sample_perplexity_results.json
├── lesson-10/
│   ├── TUTORIAL_INDEX.md
│   ├── README.md
│   ├── ai_judge_production_guide.md
│   ├── judge_prompt_engineering_tutorial.ipynb
│   ├── judge_bias_detection_tutorial.ipynb
│   ├── diagrams/
│   │   ├── judge_decision_tree.mmd
│   │   └── judge_bias_patterns.png
│   └── templates/
│       └── judge_prompts/
│           ├── dietary_adherence_judge.txt
│           ├── factual_correctness_judge.txt
│           ├── toxicity_detection_judge.txt
│           ├── coherence_judge.txt
│           ├── helpfulness_judge.txt
│           ├── substantiation_judge.txt
│           ├── hallucination_detection_judge.txt
│           ├── safety_judge.txt
│           ├── cultural_sensitivity_judge.txt
│           ├── response_length_appropriateness_judge.txt
│           └── ... (5 more)
├── lesson-11/
│   ├── TUTORIAL_INDEX.md
│   ├── README.md
│   ├── comparative_evaluation_guide.md
│   ├── elo_ranking_tutorial.ipynb
│   ├── bradley_terry_ranking_tutorial.ipynb
│   ├── ab_testing_vs_comparative_eval.ipynb
│   ├── diagrams/
│   │   ├── ranking_algorithm_comparison.mmd
│   │   └── comparative_eval_workflow.png
│   └── data/
│       └── pairwise_comparisons.json
├── lesson-9-11/
│   └── evaluation_dashboard.py
├── backend/
│   ├── exact_evaluation.py          # NEW
│   ├── ai_judge_framework.py        # NEW
│   ├── comparative_evaluation.py    # NEW
│   └── evaluation_utils.py          # EXTENDED
├── tests/
│   ├── test_exact_evaluation.py     # NEW
│   ├── test_ai_judge_framework.py   # NEW
│   └── test_comparative_evaluation.py # NEW
└── TUTORIAL_CHANGELOG.md            # NEW
```

---

## Appendix B: Relation to Eval.txt Content

### Coverage Map (Chapter 3 Sections → Lessons)

| Chapter 3 Section | Lesson | Coverage |
|-------------------|--------|----------|
| Challenges of Evaluating Foundation Models | L9 | evaluation_fundamentals.md |
| Understanding Language Modeling Metrics | L9 | language_modeling_metrics.md |
| Entropy, Cross Entropy, Perplexity | L9 | perplexity_calculation_tutorial.ipynb |
| Exact Evaluation | L9 | exact_evaluation_methods.md |
| Functional Correctness | L9 | Concept explanation + code examples |
| Similarity Measurements | L9 | similarity_measurements_tutorial.ipynb |
| Introduction to Embedding | L9 | Concept + semantic_similarity implementation |
| AI as a Judge | L10 | Complete deep-dive across all L10 materials |
| Why AI as a Judge? | L10 | ai_judge_production_guide.md intro |
| How to Use AI as a Judge | L10 | judge_prompt_engineering_tutorial.ipynb |
| Limitations of AI as a Judge | L10 | ai_judge_production_guide.md section |
| Biases of AI as a Judge | L10 | judge_bias_detection_tutorial.ipynb |
| What Models Can Act as Judges? | L10 | Model selection section in guide |
| Ranking Models with Comparative Evaluation | L11 | Complete deep-dive across all L11 materials |
| Pointwise vs Comparative Evaluation | L11 | comparative_evaluation_guide.md |
| Rating Algorithms (Elo, Bradley-Terry) | L11 | elo_ranking_tutorial.ipynb, bradley_terry_ranking_tutorial.ipynb |
| Challenges of Comparative Evaluation | L11 | comparative_evaluation_guide.md section |

**Coverage**: 90% of Chapter 3 content addressed across Lessons 9-11

---

## Appendix C: Example Tutorial Navigation Flow

### Beginner Path (Skip Theory, 4-5 hours)
```
1. Read Lesson 10 TUTORIAL_INDEX.md (5 min)
2. Complete judge_prompt_engineering_tutorial.ipynb DEMO mode (30 min)
3. Read ai_judge_production_guide.md key sections (15 min)
4. Use templates to create custom judge for chatbot (2 hours)
5. Integrate judge into HW3 workflow (1 hour)
6. View results in evaluation dashboard (30 min)
```

### Advanced Path (Complete Deep-Dive, 10-12 hours)
```
1. Complete Lesson 9 in full (3-4 hours)
   - Read all concept tutorials
   - Execute both notebooks
   - Study reference implementations
2. Complete Lesson 10 in full (3-4 hours)
   - Read production guide
   - Execute both notebooks FULL mode
   - Implement custom judges using BaseJudge
3. Complete Lesson 11 in full (2-3 hours)
   - Read comparative guide
   - Execute all 3 notebooks
   - Generate pairwise comparisons for chatbot
4. Integrate all lessons via dashboard (1-2 hours)
   - Run evaluation_dashboard.py
   - Export comprehensive report
   - Analyze cross-lesson insights
```

---

**PRD Status**: ✅ Ready for Task Generation
**Next Step**: Use `@generate-tasks.md` to break this PRD into actionable task list
**Estimated Implementation**: 4 weeks (28 days) with 1 developer
**Total Tutorial Execution Cost**: <$5 (FULL mode), <$1 (DEMO mode)
