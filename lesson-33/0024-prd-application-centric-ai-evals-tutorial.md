# PRD: Application-Centric AI Evals Tutorial System (Lesson 33)

**PRD Number:** 0024
**Feature Name:** Application-Centric AI Evals Tutorial System
**Author:** Claude Code
**Created:** 2026-01-26
**Status:** Draft

---

## 1. Introduction/Overview

Create a comprehensive tutorial system (`lesson-33/`) converting the 11-chapter textbook "Application-Centric AI Evals for Engineers and Technical Product Managers" by Shreya Shankar and Hamel Husain into accessible, First Principles-based learning materials.

**Source Material:** `lesson-33/llmeval.txt` (~3,250 lines, 160 pages equivalent)

**Methodology:** First Principles Deep Understanding Framework from `lesson-28/first_principles_prompt.md`

---

## 2. Problem Understanding

### Restated Problem
A dense 160-page textbook on LLM evaluation needs transformation into digestible tutorials that provide axiom-level understanding. The content covers the complete Analyze-Measure-Improve lifecycle for production LLM applications.

### Key Constraints
- **Tutorial-only:** No code implementations, notebooks, or video content
- **First Principles methodology:** Each tutorial follows 5-phase structure (WHAT → WHY → RECURSIVE WHYS → HOW → WHEN/WHERE)
- **Synthetic examples:** Use examples from textbook (Real Estate Agent Assistant)
- **Reading time:** 20-30 minutes per tutorial

### Assumptions
- Users range from junior developers to senior AI architects
- Target audience includes both engineers and technical product managers
- Learners have basic familiarity with LLMs and Python

### Success Criteria
- Learner can apply Analyze-Measure-Improve lifecycle to their own LLM applications
- Each tutorial provides axiom-level (irreducible) understanding of its topic
- Progressive learning path enables skill development from fundamentals to advanced topics

---

## 3. Goals

| # | Goal | Measurable Outcome |
|---|------|-------------------|
| 1 | Create navigation hub | `lesson-33/TUTORIAL_INDEX.md` with learning objectives, paths, FAQ |
| 2 | Deliver 11 concept tutorials | One tutorial per chapter, First Principles structure |
| 3 | Include visual diagrams | Mermaid diagrams for lifecycle, taxonomy, CI/CD flywheel |
| 4 | Maintain reading time | 20-30 minutes per tutorial |
| 5 | Enable progressive learning | Clear path from fundamentals to advanced topics |

---

## 4. Strategic Approach

### Chosen Strategy: Decomposition with First Principles Structure

Each chapter becomes a standalone tutorial following the First Principles framework:

```
PHASE 1: ESTABLISH BASELINE (WHAT)
├── What is [topic] at its most literal, observable level?
├── What are the constituent parts, components, or elements?
├── What terminology must be precisely defined?
└── Output: Factual inventory, key definitions, scope

PHASE 2: CHALLENGE ASSUMPTIONS (WHY)
├── Why does [topic] exist in its current form?
├── What assumptions are embedded in conventional explanations?
└── Output: Explicit/hidden assumptions, challenges to each

PHASE 3: DRILL TO AXIOMS (RECURSIVE WHYS)
├── Apply 5 Whys recursively to each claim
├── Validate at each level (evidence vs. assumption)
└── Output: Causal chains, identified first principles

PHASE 4: UNDERSTAND MECHANISMS (HOW)
├── How do fundamental components interact?
├── How does causation flow from first principles?
└── Output: Mechanistic model, leverage points

PHASE 5: CONTEXTUALIZE & APPLY (WHEN/WHERE)
├── When does this understanding apply? Break down?
├── What novel solutions emerge from recombining principles?
└── Output: Boundary conditions, transfer opportunities
```

### Recommended Implementation Heuristics

| Heuristic | Why It Applies | Suggested Approach |
|-----------|---------------|-------------------|
| **Decomposition** | 11 chapters too large to tackle at once | Create independent tutorials with clear boundaries |
| **Working Backward** | Clear learning outcomes needed first | Define axioms and objectives before structuring content |
| **Analogy** | Proven tutorial structure exists | Use `lesson-9/TUTORIAL_INDEX.md` as template |

---

## 5. User Stories

### Primary Users

**Junior Developer (Ana)**
> "As a junior developer building my first LLM application, I want to understand why evaluation is different from traditional ML testing, so that I can build reliable systems from the start."

**Senior Engineer (Marcus)**
> "As a senior engineer responsible for production LLM systems, I want to implement CI/CD evaluation pipelines, so that I can catch regressions before they reach users."

**Technical Product Manager (Priya)**
> "As a TPM defining success metrics for our AI product, I want to understand how to measure LLM quality, so that I can set meaningful targets and track improvement."

**AI Architect (David)**
> "As an AI architect designing evaluation infrastructure, I want axiom-level understanding of evaluation methodologies, so that I can make principled trade-offs between accuracy, cost, and latency."

---

## 6. Functional Requirements

### 6.1 TUTORIAL_INDEX.md (Navigation Hub)

| Req ID | Requirement |
|--------|-------------|
| F1.1 | Overview section explaining Analyze-Measure-Improve lifecycle |
| F1.2 | Learning objectives for the complete tutorial system |
| F1.3 | Prerequisites with links to prior lessons |
| F1.4 | Table of all 11 tutorials with reading times and key topics |
| F1.5 | Recommended learning paths (beginner, intermediate, advanced) |
| F1.6 | Key concepts quick reference |
| F1.7 | Common pitfalls section |
| F1.8 | FAQ section |
| F1.9 | Cross-references to related lessons (lesson-9, lesson-10) |

### 6.2 Tutorial Files (11 total)

Each tutorial MUST include:

| Req ID | Requirement |
|--------|-------------|
| F2.1 | Title and chapter reference |
| F2.2 | Reading time estimate (20-30 min) |
| F2.3 | Learning objectives (3-5 bullet points) |
| F2.4 | Phase 1: ESTABLISH BASELINE section |
| F2.5 | Phase 2: CHALLENGE ASSUMPTIONS section |
| F2.6 | Phase 3: DRILL TO AXIOMS section with explicit axiom statements |
| F2.7 | Phase 4: UNDERSTAND MECHANISMS section |
| F2.8 | Phase 5: CONTEXTUALIZE & APPLY section |
| F2.9 | First Principles Map (axioms with stopping criteria) |
| F2.10 | Uncertainty Register (what remains unknown) |
| F2.11 | Key Takeaways summary |
| F2.12 | Next Steps with link to next tutorial |

---

## 7. Deliverables

### 7.1 File List (12 files total)

| File | Source Chapter | Key Topics | Est. Reading Time |
|------|---------------|------------|-------------------|
| `TUTORIAL_INDEX.md` | Nav Hub | Learning objectives, paths, FAQ | 10 min |
| `01_introduction_three_gulfs.md` | Ch 1 | Gulf of Execution/Evaluation, Analyze-Measure-Improve lifecycle | 20 min |
| `02_llm_evaluation_basics.md` | Ch 2 | LLM strengths/weaknesses, prompting, evaluation metrics basics | 25 min |
| `03_error_analysis_deep_dive.md` | Ch 3 | Traces, open coding, axial coding, failure taxonomy, saturation | 30 min |
| `04_collaborative_evaluation_practices.md` | Ch 4 | Inter-annotator agreement, Cohen's κ, Fleiss' κ, alignment sessions | 25 min |
| `05_automated_evaluators_llm_judge.md` | Ch 5 | LLM-as-Judge, TPR/TNR, success rate estimation, rubrics | 30 min |
| `06_multi_turn_conversation_evaluation.md` | Ch 6 | Session-level metrics, consistency, escalation patterns | 20 min |
| `07_rag_pipeline_evaluation.md` | Ch 7 | Recall@k, MRR, NDCG, faithfulness, relevance, chunking strategies | 30 min |
| `08_tool_calling_agentic_systems.md` | Ch 8 | Tool selection, argument validation, agentic debugging, trace analysis | 30 min |
| `09_cicd_for_llm_applications.md` | Ch 9 | Golden datasets, CI regression tests, CD monitoring, flywheel | 25 min |
| `10_human_review_interfaces.md` | Ch 10 | HCI principles, sampling strategies, EvalGen, DocWrangler | 25 min |
| `11_accuracy_cost_optimization.md` | Ch 11 | Prompt refinement, model cascades, caching, cost reduction | 25 min |

**Total Estimated Learning Time:** ~5-6 hours

### 7.2 Mermaid Diagrams to Include

| Diagram | Location | Purpose |
|---------|----------|---------|
| Analyze-Measure-Improve Lifecycle | Tutorial 01 | Core framework visualization |
| Three Gulfs Model | Tutorial 01 | Norman's design theory for AI |
| Error Analysis Workflow | Tutorial 03 | Open → Axial coding process |
| Evaluation Taxonomy Decision Tree | Tutorial 05 | Choosing evaluation methods |
| RAG Evaluation Breakdown | Tutorial 07 | Retrieval vs. Generation metrics |
| Transition Failure Matrix | Tutorial 08 | Debugging agentic systems |
| CI/CD Flywheel | Tutorial 09 | Continuous improvement loop |
| Model Cascade Flow | Tutorial 11 | Proxy → Oracle routing |

---

## 8. Non-Goals (Out of Scope)

| Non-Goal | Rationale |
|----------|-----------|
| ❌ Code implementations or backend modules | Focus on conceptual understanding first |
| ❌ Interactive Jupyter notebooks | Tutorial-only deliverable per requirements |
| ❌ Video content | Text-based learning materials only |
| ❌ Production-ready evaluation frameworks | Teaching concepts, not shipping code |
| ❌ Real dataset integrations | Use synthetic examples from textbook |
| ❌ Exercises with solutions | Focus on learning guides, not assessments |

---

## 9. Design Considerations

### Tutorial Structure Template

```markdown
# Tutorial XX: [Title]

**Source:** Chapter X of "Application-Centric AI Evals"
**Reading Time:** XX minutes
**Difficulty:** [Beginner/Intermediate/Advanced]

## Learning Objectives
- [ ] Objective 1
- [ ] Objective 2
- [ ] Objective 3

---

## Phase 1: Establish Baseline (WHAT)
[Content following First Principles framework]

## Phase 2: Challenge Assumptions (WHY)
[Content following First Principles framework]

## Phase 3: Drill to Axioms (RECURSIVE WHYS)
[Content following First Principles framework]

## Phase 4: Understand Mechanisms (HOW)
[Content following First Principles framework]

## Phase 5: Contextualize & Apply (WHEN/WHERE)
[Content following First Principles framework]

---

## First Principles Map

### AXIOM 1: [Statement]
- **Stopping criterion met:** [which test]
- **Confidence level:** High/Medium/Low
- **Supporting evidence:** [brief]

### AXIOM 2: [Statement]
...

---

## Uncertainty Register
- What remains unknown
- Areas for further investigation

---

## Key Takeaways
1. Takeaway 1
2. Takeaway 2
3. Takeaway 3

---

## Next Steps
→ [Link to next tutorial]
```

---

## 10. Technical Considerations

### Dependencies
- **Markdown format** with GitHub-flavored Mermaid support
- **Synthetic examples** from textbook (Real Estate Agent Assistant)
- **Cross-references** to existing lessons where relevant

### Recommended Implementation Strategies

| Strategy | Why It Applies | Approach | Watch For |
|----------|---------------|----------|-----------|
| **Template-First** | Consistency across 11 tutorials | Create template file first, then populate | Template becoming too rigid for varied content |
| **Axiom Extraction** | First Principles methodology | Identify 3-5 axioms per chapter | Over-simplification losing nuance |
| **Progressive Complexity** | Junior → Senior progression | Order tutorials by dependency | Circular dependencies between topics |

---

## 11. Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Tutorial count | 11 + TUTORIAL_INDEX | File count in lesson-33/ |
| Reading time per tutorial | 20-30 minutes | Word count ÷ 200 WPM |
| First Principles compliance | 100% | Each tutorial has 5 phases + axiom map |
| Diagram coverage | 8+ diagrams | Mermaid blocks in tutorials |
| Cross-reference accuracy | 100% | All links resolve correctly |

---

## 12. Validation Checkpoints

### Phase 1: Structure Validation
- [ ] TUTORIAL_INDEX.md created with all sections
- [ ] All 11 tutorial files created with correct naming
- [ ] Template structure applied consistently

### Phase 2: Content Validation
- [ ] Each tutorial follows First Principles 5-phase structure
- [ ] Axioms explicitly stated with stopping criteria
- [ ] Reading time ≤30 min per tutorial (word count check)

### Phase 3: Integration Validation
- [ ] Mermaid diagrams render correctly
- [ ] Cross-references to related lessons verified
- [ ] Learning path flows logically

### Phase 4: Quality Validation
- [ ] Technical accuracy verified against source textbook
- [ ] Examples are synthetic and self-contained
- [ ] No code blocks requiring execution

---

## 13. Open Questions

| Question | Impact | Resolution Needed By |
|----------|--------|---------------------|
| Should diagrams be separate .mmd files or inline? | File organization | Before implementation |
| Include exercises from textbook appendix? | Scope creep risk | Before implementation |
| Link to external resources (papers, tools)? | Maintenance burden | During implementation |

---

## 14. Appendix: Source Chapter Mapping

| Tutorial | Source Chapter | Page Range | Key Concepts |
|----------|---------------|------------|--------------|
| 01 | Ch 1: Introduction | 1-20 | Three Gulfs, Analyze-Measure-Improve |
| 02 | Ch 2: LLMs, Prompts, Evaluation | 21-40 | LLM capabilities, prompting, metrics |
| 03 | Ch 3: Error Analysis | 41-60 | Traces, coding, taxonomies |
| 04 | Ch 4: Collaborative Evaluation | 61-75 | Agreement metrics, calibration |
| 05 | Ch 5: Automated Evaluators | 76-95 | LLM-as-Judge, TPR/TNR |
| 06 | Ch 6: Multi-Turn Conversations | 96-105 | Session metrics |
| 07 | Ch 7: RAG Evaluation | 106-125 | Retrieval metrics, chunking |
| 08 | Ch 8: Architectures & Modalities | 126-145 | Tool calling, agentic systems |
| 09 | Ch 9: CI/CD | 146-160 | Golden datasets, monitoring |
| 10 | Ch 10: Human Review Interfaces | 161-175 | HCI, sampling, EvalGen |
| 11 | Ch 11: Improvement | 176-190 | Accuracy, cost optimization |

---

**Document History:**
- 2026-01-26: Initial draft created
