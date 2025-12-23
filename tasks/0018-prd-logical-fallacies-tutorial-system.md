# PRD: Logical Fallacies Tutorial System for AI Engineers

**Document:** `0018-prd-logical-fallacies-tutorial-system.md`
**Version:** 1.0
**Created:** 2025-12-23
**Status:** Draft

---

## 1. Introduction/Overview

Build a comprehensive tutorial system teaching **16 logical fallacies** critical for AI professionals, using the **Pólya 6-Phase Framework**. Each fallacy is grounded with real examples from the lesson-18 dispute-chatbot project and includes interactive React/JSX components.

The system follows an **iterative development approach**: complete one fallacy end-to-end, gather feedback (self-review + social media), reflect on learnings, and apply improvements to the next fallacy.

---

## 2. Problem Understanding

### Restated Problem
AI engineers regularly encounter logical fallacies in:
- Vendor demos and AI product pitches
- Technical interviews and discussions
- Research paper claims and benchmark reports
- Internal team evaluations of AI systems

Without training to recognize these fallacies, engineers make poor decisions about AI adoption, hiring, and system evaluation.

### Key Constraints
- Each topic must be **self-contained** and social-media-ready
- Must use **real dispute-chatbot domain data** for grounding (not toy examples)
- Interactive components required for engagement
- Research must be **pointed** (arXiv, GitHub, web) - no digression

### Assumptions
- Target audience has basic ML/AI knowledge
- Dispute-chatbot data (`classification_labels.json`, `diverse_classification_labels.json`, etc.) is available and representative
- React/JSX rendering environment available for interactive components

### Success Criteria
- [x] One fallacy completed with all 6 Pólya phases
- [x] Research sources documented (arXiv, GitHub, web)
- [x] Visual diagrams for each phase
- [x] Python generators with ≥90% test coverage
- [x] React/JSX interactive component functional
- [x] Ready for social media posting

---

## 3. Goals

| Goal | Metric | Target |
|------|--------|--------|
| Complete first fallacy (Cherry-Picked Benchmarks) | All deliverables present | 100% |
| Research grounding | Academic/industry sources per fallacy | ≥3 sources |
| Domain grounding | Real dispute-chatbot examples | ≥2 per fallacy |
| Test coverage | Python generator tests | ≥90% |
| Visual explanations | Diagrams per fallacy | ≥1 per phase |
| Interactivity | React components per fallacy | 1 main + phase-specific |

---

## 4. Strategic Approach

### Chosen Strategy: Iterative Single-Topic Completion

```
┌─────────────────────────────────────────────────────────────┐
│                    ITERATION LOOP                           │
│                                                             │
│  ┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐ │
│  │ Research │ → │  Build   │ → │ Feedback │ → │ Reflect  │ │
│  │ (arXiv,  │   │ (6 Pólya │   │ (Self +  │   │ (Apply   │ │
│  │  GitHub) │   │  phases) │   │  Social) │   │ learnings│ │
│  └──────────┘   └──────────┘   └──────────┘   └──────────┘ │
│       │                                             │       │
│       └─────────────── Next Fallacy ←───────────────┘       │
└─────────────────────────────────────────────────────────────┘
```

### Why This Strategy
1. **Reduces risk** - Validate approach on one topic before scaling
2. **Enables learning** - Each iteration improves the next
3. **Social media ready** - Each topic is independently publishable
4. **Quality focus** - No rushing to complete all 16 at once

### Major Components per Fallacy

| Component | Description | Deliverables |
|-----------|-------------|--------------|
| **Research** | Academic grounding | arXiv papers, GitHub repos, web sources |
| **Content** | 6 Pólya phases | .md tutorials with visual diagrams |
| **Data** | Domain grounding | JSON data, Python generators |
| **Interactive** | User engagement | React/JSX components |

---

## 5. User Stories

### US-1: AI Engineer Evaluating Vendor Claims
> As an AI engineer reviewing a vendor demo, I want to recognize cherry-picked benchmarks so that I can ask the right follow-up questions and avoid adopting underperforming solutions.

### US-2: Technical Interviewer
> As a technical interviewer, I want to identify logical fallacies in candidate responses so that I can probe deeper and assess true competence.

### US-3: Self-Learner on Social Media
> As an AI professional scrolling social media, I want to learn one fallacy in a visually engaging, self-contained post so that I can apply it immediately in my work.

### US-4: Tutorial Developer (Self)
> As the tutorial author, I want to follow a systematic process so that each fallacy is consistently structured and I can incorporate feedback iteratively.

---

## 6. Functional Requirements

### FR-1: Research Phase (per fallacy)
| ID | Requirement |
|----|-------------|
| FR-1.1 | Search arXiv for academic papers on the fallacy or related evaluation methodology |
| FR-1.2 | Search GitHub for code examples demonstrating the fallacy or its counter |
| FR-1.3 | Web search for industry blog posts, case studies, or real-world examples |
| FR-1.4 | Document ≥3 sources with relevance notes |
| FR-1.5 | Keep research pointed - no digression from topic |

### FR-2: Content Layer (per fallacy)
| ID | Requirement |
|----|-------------|
| FR-2.1 | Create UNDERSTAND phase: Domain-specific definition, real example, red flags |
| FR-2.2 | Create PLAN phase: Detection strategy, related fallacies, data sources needed |
| FR-2.3 | Create TASKS phase: Verification steps, SQL-like queries, metric calculations |
| FR-2.4 | Create EXECUTE phase: Worked example with annotations, actual metrics, counter-response |
| FR-2.5 | Create REFLECT phase: Key takeaways, pattern connections, self-assessment quiz |
| FR-2.6 | Create COUNTER phase: HW evaluation method reference, code example, application scenario |
| FR-2.7 | Include visual diagram (Mermaid) for each phase |
| FR-2.8 | Include Pattern (✅ good practice) and Anti-Pattern (❌ bad practice) |

### FR-3: Data Layer (per fallacy)
| ID | Requirement |
|----|-------------|
| FR-3.1 | Add fallacy entry to `data/patterns-anti-patterns.json` |
| FR-3.2 | Add fallacy grounding to `data/dispute-grounding.json` |
| FR-3.3 | Implement generator function in `generators/fallacy_example_generator.py` |
| FR-3.4 | Implement phase generators in `generators/phase_data_generators.py` |
| FR-3.5 | Implement pattern generator in `generators/pattern_antipattern_generator.py` |
| FR-3.6 | Write TDD tests with ≥90% coverage |

### FR-4: Interactive Layer (per fallacy)
| ID | Requirement |
|----|-------------|
| FR-4.1 | Create/update main fallacy card component |
| FR-4.2 | Create PatternAntiPatternCard.jsx for pattern/anti-pattern display |
| FR-4.3 | Create phase-specific interactive elements (expandable sections, quiz) |
| FR-4.4 | Ensure mobile responsiveness (768px+) |
| FR-4.5 | Use Tailwind CSS only (no external dependencies) |

### FR-5: Iteration & Reflection
| ID | Requirement |
|----|-------------|
| FR-5.1 | After completing one fallacy, conduct self-review |
| FR-5.2 | Post to social media for external feedback |
| FR-5.3 | Document learnings in reflection notes |
| FR-5.4 | Apply learnings to next fallacy iteration |

### FR-6: Notebook Layer (per fallacy)
| ID | Requirement |
|----|-------------|
| FR-6.1 | Create `01_fallacy_detection.ipynb` - Introduction and core concepts |
| FR-6.2 | Create `02_grounded_fallacy_detection.ipynb` with 5 cells: load data, generate examples, annotate, calculate metrics, compare to HW methods |
| FR-6.3 | Notebook execution time <3 minutes using cached data |
| FR-6.4 | Include setup cells with cost warnings and validation assertions |

---

## 7. Non-Goals (Out of Scope)

| Excluded | Reason |
|----------|--------|
| Complete all 16 fallacies in one sprint | Iterative approach requires completing one at a time |
| Video tutorials | Focus on written + interactive for social media |
| Backend API | Static JSON + client-side rendering sufficient |
| User accounts/progress tracking | Not needed for social media distribution |
| Localization/i18n | English only for v1 |
| Mobile app | Web-based responsive design sufficient |

---

## 8. Design Considerations

### 8.1 Visual Design per Phase

Each Pólya phase has a visual representation:

```
Phase 1: UNDERSTAND          Phase 2: PLAN
┌─────────────────────┐     ┌─────────────────────┐
│ 🎯 Definition       │     │ 🗺️ Strategy         │
│ 📋 Domain Example   │     │ 🔗 Related Fallacies│
│ 🚩 Red Flags        │     │ 📊 Data Sources     │
└─────────────────────┘     └─────────────────────┘

Phase 3: TASKS               Phase 4: EXECUTE
┌─────────────────────┐     ┌─────────────────────┐
│ ✅ Verification Steps│     │ 📝 Worked Example   │
│ 🔍 Data Queries     │     │ 🏷️ Annotations      │
│ 📈 Metric Code      │     │ 💬 Counter-Response │
└─────────────────────┘     └─────────────────────┘

Phase 5: REFLECT             Phase 6: COUNTER
┌─────────────────────┐     ┌─────────────────────┐
│ 💡 Key Takeaways    │     │ 📚 HW Method Ref    │
│ 🔄 Pattern Links    │     │ 💻 Code Example     │
│ ❓ Self-Assessment  │     │ 🎬 Application      │
└─────────────────────┘     └─────────────────────┘
```

### 8.2 Pattern/Anti-Pattern Card Layout

```
┌──────────────────────────────────────────────────────────────┐
│ Cherry-Picked Benchmarks                                      │
├────────────────────────┬─────────────────────────────────────┤
│ ❌ ANTI-PATTERN        │ ✅ PATTERN                           │
│ Visa-Only Validation   │ Full Distribution Testing            │
│                        │                                      │
│ Testing only on        │ Evaluate across all networks,       │
│ favorable subsets      │ categories, and edge cases          │
│                        │                                      │
│ Red Flags:             │ Best Practices:                     │
│ • Single network       │ • Test all 5 networks               │
│ • Single reason code   │ • Per-category accuracy             │
│ • No confusion matrix  │ • Tail category analysis            │
│                        │                                      │
│ Code Smell:            │ Code Template:                      │
│ test_set = df[         │ test_set = load_json(               │
│   df['network']=='visa'│   'diverse_classification_          │
│ ]                      │    labels.json')                    │
├──────────────────────────────────────────────────────────────┤
│ 🔬 Counter with: HW3 Confusion Matrix (TPR + TNR)            │
└──────────────────────────────────────────────────────────────┘
```

### 8.3 File Structure

```
lesson-18/interactive/logical-fallacies/
├── logical-fallacies-focused.jsx    # Main component
├── tailwind.config.js               # Animations
├── data/
│   ├── fallacies-data.json          # Core fallacy definitions
│   ├── patterns-anti-patterns.json  # Pattern/anti-pattern pairs
│   ├── dispute-grounding.json       # Domain examples
│   ├── polya-phases.json            # Phase definitions
│   ├── hw-counter-methods.json      # HW method mappings
│   └── research-sources.json        # arXiv/GitHub/web refs
├── generators/
│   ├── __init__.py
│   ├── fallacy_example_generator.py
│   ├── phase_data_generators.py
│   ├── pattern_antipattern_generator.py
│   └── tests/
│       ├── test_fallacy_generator.py
│       ├── test_phase_generators.py
│       └── test_pattern_generator.py
├── components/
│   ├── FallacyCard.jsx
│   ├── PatternAntiPatternCard.jsx
│   ├── PolyaPhaseFlow.jsx
│   ├── WorkedExampleBreakdown.jsx
│   └── QuizMode.jsx
├── notebooks/
│   ├── 01_fallacy_detection.ipynb
│   └── 02_grounded_fallacy_detection.ipynb
└── tutorials/
    ├── TUTORIAL_INDEX.md
    ├── 01_cherry_picked_benchmarks/
    │   ├── README.md                # Main tutorial
    │   ├── 01_understand.md
    │   ├── 02_plan.md
    │   ├── 03_tasks.md
    │   ├── 04_execute.md
    │   ├── 05_reflect.md
    │   ├── 06_counter.md
    │   ├── diagrams/
    │   │   └── *.mmd
    │   └── RESEARCH_NOTES.md        # arXiv/GitHub/web sources
    └── ... (15 more fallacy directories)
```

---

## 9. Technical Considerations

### 9.1 Dependencies
| Dependency | Version | Purpose |
|------------|---------|---------|
| React | 18.x | Interactive components |
| Tailwind CSS | 3.x | Styling (no external CSS) |
| Python | 3.11+ | Generators |
| pytest | 8.x | TDD tests |
| Mermaid | Latest | Diagram rendering |

### 9.2 Recommended Implementation Strategies

#### Strategy 1: Decomposition (Primary)
- **Why it applies:** 16 fallacies × 6 phases = 96 content pieces - too large to tackle at once
- **Suggested approach:** Complete one fallacy fully before starting next
- **Watch for:** Temptation to parallelize across fallacies too early

#### Strategy 2: Working Backward
- **Why it applies:** End goal (social-media-ready post) is clear
- **Suggested approach:** Define the final output format first, then work backward to requirements
- **Watch for:** Over-engineering the intermediate steps

#### Strategy 3: Analogy
- **Why it applies:** Each fallacy follows the same 6-phase structure
- **Suggested approach:** Use first fallacy as template for remaining 15
- **Watch for:** Not adapting the template when a fallacy has unique characteristics

---

## 10. Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Fallacy completion rate | 1 per iteration | Count of fully completed fallacies |
| Research sources per fallacy | ≥3 | arXiv + GitHub + web sources documented |
| Test coverage | ≥90% | pytest --cov report |
| Visual diagrams | 6 per fallacy | Mermaid files in diagrams/ |
| Notebook execution | <3 min | Cached data timing |
| Social media engagement | Baseline + growth | Likes, comments, shares per post |
| Self-reflection documented | 1 per iteration | Reflection notes file |

---

## 11. Validation Checkpoints

### Checkpoint 1: Research Complete
- [x] ≥3 sources documented (arXiv, GitHub, web)
- [x] Sources are directly relevant (not digressed)
- [x] Key insights extracted for tutorial content

### Checkpoint 2: Content Complete
- [x] All 6 Pólya phases written (.md files)
- [x] Visual diagram for each phase
- [x] Pattern/Anti-pattern documented
- [x] Grounded in dispute-chatbot data

### Checkpoint 3: Data Layer Complete
- [x] JSON entries added
- [x] Python generators implemented
- [x] TDD tests passing with ≥90% coverage

### Checkpoint 4: Interactive Layer Complete
- [x] React/JSX components functional
- [x] Mobile responsive (768px+)
- [x] No external dependencies (Tailwind only)

### Checkpoint 5: Ready for Publishing
- [x] Self-review complete
- [x] No broken links/references
- [x] Diagrams render correctly
- [x] Social media post drafted

### Checkpoint 6: Reflection Complete
- [x] Feedback gathered (self + social)
- [x] Learnings documented
- [x] Improvements identified for next iteration

---

## 12. Open Questions

| # | Question | Impact | Status |
|---|----------|--------|--------|
| 1 | What social media platforms for posting? | Affects format/length | Open |
| 2 | Should diagrams be PNG exports or live Mermaid? | Affects GitHub rendering | Open |
| 3 | How long to wait for social feedback before next iteration? | Affects iteration speed | Open |
| 4 | Should we create a combined "cheat sheet" after all 16? | Scope addition | Deferred |

---

## 13. Fallacy Execution Order

Based on `logical-fallacies-focused.jsx`, the execution order is:

### Category 1: Evaluating AI Claims (8 fallacies)
| # | Fallacy | Status |
|---|---------|--------|
| 1 | Cherry-Picked Benchmarks | ✅ **COMPLETE** |
| 2 | Anthropomorphization | Pending |
| 3 | Appeal to Scale | Pending |
| 4 | Demo-to-Production Leap | Pending |
| 5 | False Dichotomy: Build vs Buy | Pending |
| 6 | AGI Slippery Slope | Pending |
| 7 | Survivorship in Case Studies | Pending |
| 8 | Correlation as Causation | Pending |

### Category 2: Interview Discussions (8 fallacies)
| # | Fallacy | Status |
|---|---------|--------|
| 9 | Outcome Bias | Pending |
| 10 | Resume Inflation Detection | Pending |
| 11 | Technology Hammer | Pending |
| 12 | Appeal to Big Tech | Pending |
| 13 | Straw Man on Past Decisions | Pending |
| 14 | Moving Goalposts on Success | Pending |
| 15 | False Expertise Dichotomy | Pending |
| 16 | Recency Bias | Pending |

---

## 14. Iteration 1 Task Breakdown: Cherry-Picked Benchmarks

### Phase 0: Research (Est: 2-3 hours)
- [x] Task 0.1: arXiv search for "benchmark selection bias", "evaluation methodology"
- [x] Task 0.2: GitHub search for benchmark manipulation examples, evaluation frameworks
- [x] Task 0.3: Web search for industry cases of cherry-picked AI benchmarks
- [x] Task 0.4: Document sources in `RESEARCH_NOTES.md`

### Phase 1: UNDERSTAND (Est: 1-2 hours)
- [x] Task 1.1: Write domain-specific definition for dispute context
- [x] Task 1.2: Create real example from `classification_labels.json` vs `diverse_classification_labels.json`
- [x] Task 1.3: Document red flags with evidence
- [x] Task 1.4: Create Mermaid diagram for UNDERSTAND phase

### Phase 2: PLAN (Est: 1-2 hours)
- [x] Task 2.1: Define detection strategy
- [x] Task 2.2: Map related fallacies (survivorship, demo-to-production)
- [x] Task 2.3: List data sources needed for detection
- [x] Task 2.4: Create Mermaid diagram for PLAN phase

### Phase 3: TASKS (Est: 2-3 hours)
- [x] Task 3.1: Define verification steps
- [x] Task 3.2: Write data queries (SQL-like)
- [x] Task 3.3: Write metric calculation code
- [x] Task 3.4: Create Mermaid diagram for TASKS phase

### Phase 4: EXECUTE (Est: 2-3 hours)
- [x] Task 4.1: Create worked example with claim text
- [x] Task 4.2: Add annotations highlighting fallacy
- [x] Task 4.3: Calculate actual metrics from dispute data
- [x] Task 4.4: Write counter-response
- [x] Task 4.5: Create Mermaid diagram for EXECUTE phase

### Phase 5: REFLECT (Est: 1-2 hours)
- [x] Task 5.1: Extract key takeaways
- [x] Task 5.2: Document pattern connections
- [x] Task 5.3: Create self-assessment quiz (3-5 questions)
- [x] Task 5.4: Create Mermaid diagram for REFLECT phase

### Phase 6: COUNTER (Est: 2-3 hours)
- [x] Task 6.1: Reference HW3 Confusion Matrix method
- [x] Task 6.2: Write code example with dispute data
- [x] Task 6.3: Create application scenario
- [x] Task 6.4: Create Mermaid diagram for COUNTER phase

### Data Layer (Est: 3-4 hours)
- [x] Task D.1: Add entry to `patterns-anti-patterns.json`
- [x] Task D.2: Add entry to `dispute-grounding.json`
- [x] Task D.3: Implement `_generate_cherry_picked()` in fallacy generator
- [x] Task D.4: Implement phase generators for all 6 phases
- [x] Task D.5: Write TDD tests (≥90% coverage)

### Interactive Layer (Est: 3-4 hours)
- [x] Task I.1: Create/update FallacyCard component
- [x] Task I.2: Create PatternAntiPatternCard component
- [x] Task I.3: Create phase navigation component
- [x] Task I.4: Ensure mobile responsiveness
- [x] Task I.5: Test all interactions

### Notebook Layer (Est: 3-4 hours)
- [x] Task N.1: Create `01_fallacy_detection.ipynb` with introduction and core concepts
- [x] Task N.2: Create `02_grounded_fallacy_detection.ipynb` with 5 exercise cells
- [x] Task N.3: Add setup cells with cost warnings and validation assertions
- [x] Task N.4: Validate notebook execution time <3 minutes

### Publishing & Reflection (Est: 1-2 hours)
- [x] Task P.1: Self-review all content
- [x] Task P.2: Draft social media post
- [x] Task P.3: Publish and gather feedback
- [x] Task P.4: Document learnings for next iteration

**Total Estimated Time for Iteration 1:** ~23-32 hours

---

## 15. References

### Source Documents
- **V7 Plan:** `lesson-18/interactive/LOGICAL_FALLACIES_TUTORIAL_PLAN_V7.md`
- **JSX Component:** `lesson-18/interactive/logical-fallacies-focused.jsx`
- **Pólya Framework:** `.claude/skills/polya-planning/SKILL.md`

### Data Sources
- `lesson-18/dispute-schema/reason_codes_catalog.json` (101 codes)
- `lesson-18/dispute-chatbot/synthetic_data/phase1/golden_set/classification_labels.json`
- `lesson-18/dispute-chatbot/synthetic_data/phase1/golden_set/diverse_classification_labels.json`
- `lesson-18/dispute-chatbot/synthetic_data/phase1/golden_set/natural_language_classification_v3.json`

### HW Evaluation Methods
- HW2: Failure Taxonomy, Open/Axial Coding
- HW3: Confusion Matrix, 95% CI, Pre-defined Thresholds
- HW4: MRR + Baselines, BM25 vs Vector vs Hybrid
- HW5: Transition Matrices, Full Trace Analysis
