# Lesson 11: Comparative Evaluation & Leaderboards - Tutorial Index

## Overview

Lesson 11 covers **comparative evaluation methodologies** and **leaderboard ranking systems** for LLM evaluation. You'll learn when comparative evaluation outperforms pointwise scoring, how to implement Elo and Bradley-Terry ranking algorithms, and how to build robust leaderboards for model comparison.

**Learning Time:** ~3-4 hours
**Difficulty:** Intermediate
**Prerequisites:** Completion of Lesson 10, basic understanding of probability and statistics

---

## Learning Objectives

By completing these tutorials, you will be able to:
- ✅ Understand when to use comparative vs pointwise evaluation
- ✅ Implement Elo ranking algorithm for dynamic leaderboards
- ✅ Implement Bradley-Terry model for probabilistic skill estimation
- ✅ Analyze transitivity violations in pairwise comparisons
- ✅ Compare A/B testing vs comparative evaluation for model selection
- ✅ Generate high-quality pairwise comparison datasets using AI judges

---

## Tutorials

### 1. Comparative Evaluation Guide
**File:** `comparative_evaluation_guide.md`
**Reading Time:** 20-25 minutes
**Topics:**
- Pointwise vs comparative evaluation trade-offs
- Why comparative evaluation is more reliable for subjective criteria
- Ranking algorithms: Elo vs Bradley-Terry vs TrueSkill
- Handling transitivity violations (A > B > C but C > A)
- Crowdsourced vs expert comparisons
- A/B testing vs side-by-side comparative evaluation
- Private leaderboards and contamination prevention

**When to use:** Essential foundation before implementing any comparative evaluation system.

---

### 2. Elo Ranking Tutorial (Interactive Notebook)
**File:** `elo_ranking_tutorial.ipynb`
**Execution Time:** <5 minutes
**Cost:** $0 (simulation-based, no API calls)
**Topics:**
- Elo formula and intuition (borrowed from chess)
- Implementation from scratch with K-factor tuning
- Record pairwise matches and update rankings
- Visualize leaderboard evolution over time
- Calculate confidence intervals for rankings
- Analyze transitivity violations

**When to use:** Hands-on implementation of dynamic ranking system.

---

### 3. Bradley-Terry Ranking Tutorial (Interactive Notebook)
**File:** `bradley_terry_ranking_tutorial.ipynb`
**Execution Time:** <4 minutes
**Cost:** $0 (simulation-based, no API calls)
**Topics:**
- Bradley-Terry model explanation (logistic regression for pairwise comparisons)
- Maximum likelihood estimation (MLE) for skill parameters
- Fit model to comparison data
- Visualize skill estimates with uncertainty
- Compare Bradley-Terry vs Elo rankings
- When to use Bradley-Terry (static analysis) vs Elo (dynamic updates)

**When to use:** Learn probabilistic ranking when you have complete comparison data.

---

### 4. A/B Testing vs Comparative Evaluation (Interactive Notebook)
**File:** `ab_testing_vs_comparative_eval.ipynb`
**Execution Time:** <3 minutes
**Cost:** $0 (simulation-based, no API calls)
**Topics:**
- A/B testing simulation (variant A vs variant B)
- Comparative evaluation simulation (side-by-side comparisons)
- Sample size comparison for same statistical power
- Speed to signal analysis (how fast can you detect 5% improvement?)
- Trade-offs: simplicity vs information efficiency
- When to use each approach

**When to use:** Understand when comparative evaluation saves time/cost over A/B testing.

---

## Recommended Learning Path

```
┌─────────────────────────────────────────────────────┐
│              Lesson 11 Learning Flow                │
├─────────────────────────────────────────────────────┤
│                                                     │
│  1. Read README.md                                  │
│     ↓                                               │
│  2. Complete Comparative Evaluation Guide          │
│     ↓                                               │
│  3. Run Elo Ranking Notebook                       │
│     ↓                                               │
│  4. Run Bradley-Terry Ranking Notebook             │
│     ↓                                               │
│  5. Run A/B Testing vs Comparative Eval Notebook   │
│     ↓                                               │
│  6. Generate pairwise comparisons for your models  │
│     ↓                                               │
│  7. Build leaderboard for your use case            │
└─────────────────────────────────────────────────────┘
```

---

## Key Concepts

### Elo Rating System

**Formula:**
```
Expected Score:  E_A = 1 / (1 + 10^((R_B - R_A) / 400))
New Rating:      R_A' = R_A + K * (S_A - E_A)

Where:
- R_A, R_B: Current Elo ratings for models A and B
- E_A: Expected win probability for A
- S_A: Actual outcome (1 if A wins, 0 if B wins, 0.5 if tie)
- K: Learning rate (typical: 32 for established, 64 for new)
```

**Intuition:**
- If strong model (high Elo) beats weak model (low Elo): small rating change
- If weak model beats strong model: large rating change (upset!)
- Self-correcting: ratings converge to true skill over time

**Pros:**
- Simple, intuitive, well-understood (70+ years of use)
- Online updates (process comparisons one at a time)
- Handles new models easily

**Cons:**
- Order-dependent (early matches have outsized impact)
- Requires K-factor tuning
- No uncertainty estimates

---

### Bradley-Terry Model

**Formula:**
```
P(A beats B) = exp(θ_A) / (exp(θ_A) + exp(θ_B))
             = 1 / (1 + exp(θ_B - θ_A))

Where:
- θ_A, θ_B: Skill parameters for models A and B
- Estimated via maximum likelihood on all pairwise data
```

**Intuition:**
- Probabilistic model: each model has a latent "skill" parameter
- Win probability follows logistic curve
- MLE finds skill values that best explain observed comparisons

**Pros:**
- Batch estimation (uses all data simultaneously, order-independent)
- Provides uncertainty estimates (via standard errors)
- Statistically principled (likelihood-based inference)

**Cons:**
- Requires complete dataset (can't process incrementally)
- More complex to implement
- Doesn't handle new models without refitting

---

### When to Use Which Algorithm?

| Criterion | Elo | Bradley-Terry | TrueSkill |
|-----------|-----|---------------|-----------|
| **Online updates** | ✅ Yes | ❌ No (batch only) | ✅ Yes |
| **Uncertainty estimates** | ❌ No | ✅ Yes | ✅ Yes |
| **Order-independent** | ❌ No | ✅ Yes | ✅ Yes |
| **Handles ties** | ✅ Yes | ⚠️ Can extend | ✅ Yes |
| **Complexity** | Simple | Moderate | Complex |
| **Best for** | Dynamic leaderboards | Static analysis | Team competitions |

**Decision Rule:**
- **Elo**: Live leaderboard with continuous model updates (e.g., Chatbot Arena)
- **Bradley-Terry**: One-time ranking of fixed set of models
- **TrueSkill**: Multi-player scenarios (not covered in this lesson)

---

### Comparative vs Pointwise Evaluation

**Pointwise Evaluation:**
- Judge evaluates each response independently: "Rate this response 1-5"
- Absolute scoring scale
- Suffers from: score drift, inconsistent standards, scale misuse

**Comparative Evaluation:**
- Judge compares two responses directly: "Which is better: A or B?"
- Relative preference only
- More reliable for subjective criteria (helpfulness, coherence, style)

**Research Finding (Chatbot Arena):**
> Comparative evaluation requires **~50% fewer human judgments** to achieve same statistical power as pointwise evaluation for model ranking.

**Example:**
- To detect 5% win rate difference with 95% confidence:
  - A/B testing (pointwise): ~1,600 samples per variant = 3,200 total
  - Comparative (pairwise): ~1,000 pairwise comparisons = 1,000 total
  - **3.2x sample efficiency!**

---

## Pairwise Comparison Dataset

This lesson includes a **pre-generated dataset** of 100 pairwise comparisons:

**File:** `data/pairwise_comparisons.json`

**Format:**
```json
{
  "query": "How do I make gluten-free pasta from scratch?",
  "response_a": "...",
  "response_b": "...",
  "winner": "A",
  "rationale": "Response A provides more detailed ingredient ratios and addresses common pitfalls.",
  "dimension": "helpfulness"
}
```

**Dimensions covered:**
- **Helpfulness** (30 comparisons)
- **Correctness** (30 comparisons)
- **Conciseness** (20 comparisons)
- **Safety** (20 comparisons)

**Generation script:** `scripts/generate_pairwise_comparisons.py`

---

## Practical Exercises

After completing the tutorials, try these exercises:

1. **Elo vs Bradley-Terry Comparison**
   - Take 50 pairwise comparisons
   - Compute rankings with both algorithms
   - Compare rank orderings (Spearman correlation)
   - Analyze cases where they disagree

2. **Transitivity Violation Analysis**
   - Find cycles in pairwise comparisons (A > B > C > A)
   - Calculate violation rate
   - Investigate causes (ambiguous queries? inconsistent judge?)
   - Decide how to handle violations (remove? re-evaluate?)

3. **Sample Size Sensitivity**
   - Start with 10 comparisons
   - Compute rankings
   - Add 10 more, recompute
   - Plot ranking stability vs sample size
   - Determine minimum comparisons needed for reliable rankings

4. **Build Your Own Leaderboard**
   - Generate 100 pairwise comparisons for 5 different models/prompts
   - Implement live Elo leaderboard with updates
   - Visualize ranking evolution
   - Add confidence intervals

---

## Common Pitfalls

### Comparative Evaluation Design
- ❌ **Biased pair selection:** Only comparing strong vs weak models → Inflate differences
- ❌ **Insufficient comparisons:** <20 per model pair → High variance
- ❌ **Ignoring ties:** Forcing win/loss when responses are equivalent → Adds noise
- ❌ **Not randomizing order:** Always showing model A first → Position bias

### Ranking Algorithms
- ❌ **Wrong K-factor in Elo:** Too high = volatile, too low = slow convergence
- ❌ **Ignoring cold start:** New models start at default rating → Unreliable initially
- ❌ **Comparing across different comparison sets:** Elo ratings only meaningful within same pool
- ❌ **Over-interpreting small rating differences:** 10 Elo point difference ≈ ~1.5% win rate difference

### Leaderboard Management
- ❌ **No contamination prevention:** Public test set → Models overfit to leaderboard
- ❌ **Infrequent updates:** Stale leaderboard doesn't reflect latest models
- ❌ **No uncertainty communication:** Showing point estimates without confidence intervals
- ❌ **Cherry-picking comparisons:** Only evaluating on favorable queries → Gaming system

---

## Resources

### Reference Files
- [`README.md`](README.md) - Lesson setup and overview
- [`backend/comparative_evaluation.py`](../backend/comparative_evaluation.py) - EloRanking and BradleyTerryRanking classes
- [`tests/test_comparative_evaluation.py`](../tests/test_comparative_evaluation.py) - Unit tests with examples
- [`data/pairwise_comparisons.json`](data/pairwise_comparisons.json) - 100 pre-generated comparisons
- [`scripts/generate_pairwise_comparisons.py`](scripts/generate_pairwise_comparisons.py) - Comparison generation script

### Diagrams
- [`diagrams/ranking_algorithm_comparison.mmd`](diagrams/ranking_algorithm_comparison.mmd) - Algorithm decision flowchart
- [`diagrams/comparative_eval_workflow.png`](diagrams/comparative_eval_workflow.png) - End-to-end pipeline

### Real-World Examples
- [Chatbot Arena Leaderboard](https://chat.lmsys.org/?leaderboard) - Elo-based rankings from 100K+ human votes
- [AlpacaEval Leaderboard](https://tatsu-lab.github.io/alpaca_eval/) - Automated win-rate evaluations
- [Open LLM Leaderboard](https://huggingface.co/spaces/HuggingFaceH4/open_llm_leaderboard) - Pointwise benchmarks

### External Resources
- [Elo Rating System (Wikipedia)](https://en.wikipedia.org/wiki/Elo_rating_system)
- [Bradley-Terry Model (Wikipedia)](https://en.wikipedia.org/wiki/Bradley%E2%80%93Terry_model)
- [Chatbot Arena Paper (2023)](https://arxiv.org/abs/2306.05685)

---

## Next Steps

After completing Lesson 11, you'll have:
- ✅ Understanding of comparative vs pointwise evaluation trade-offs
- ✅ Elo and Bradley-Terry ranking implementations
- ✅ Pairwise comparison dataset generation pipeline
- ✅ Leaderboard visualization skills

**Move on to the Evaluation Dashboard** to see unified metrics across all lessons.

👉 [Evaluation Dashboard](../lesson-9-11/README.md)

---

## FAQ

**Q: When should I use comparative evaluation instead of pointwise scoring?**
A: Use comparative for subjective criteria (helpfulness, coherence, style) where absolute scales are unreliable. Use pointwise for objective criteria (factual correctness, formatting adherence) with clear ground truth.

**Q: How many pairwise comparisons do I need per model?**
A: Minimum 20-30 comparisons per model pair for stable rankings. More if win rates are close (e.g., 48% vs 52% requires ~200 comparisons for 95% confidence).

**Q: What if my comparisons have cycles (A > B > C > A)?**
A: Some cycles are expected due to noise. If >10% of triplets violate transitivity, investigate: (1) inconsistent judge, (2) query-dependent preferences, (3) ties forced to wins/losses.

**Q: Should I use Elo or Bradley-Terry?**
A: Elo for dynamic leaderboards (continuous updates), Bradley-Terry for static analysis (one-time ranking). Elo is simpler; Bradley-Terry provides uncertainty.

**Q: How do I choose Elo K-factor?**
A: Start with K=32. Increase to 64 for new/volatile models. Decrease to 16 for mature/stable models. Validate by checking rating convergence speed.

**Q: Can I compare Elo ratings across different leaderboards?**
A: No. Elo ratings are relative to the comparison pool. 1500 Elo on one leaderboard ≠ 1500 Elo on another.

**Q: How do I handle ties in comparisons?**
A: Elo supports ties (S_A = 0.5). Bradley-Terry requires extension (e.g., Davidson model). Alternatively, ask judge to break ties with "slightly better" option.

---

**Tutorial Status:** ✅ Complete
**Last Updated:** 2025-11-09
**Maintainer:** AI Evaluation Course Team

---

## Implementation Notes

**Backend Module:** `backend/comparative_evaluation.py`
- ✅ EloRanking class implemented
- ✅ BradleyTerryRanking class implemented
- ✅ Helper functions (calculate_expected_score, calculate_win_rate, generate_pairwise_comparisons, visualize_leaderboard)
- ✅ 97% test coverage (45 tests passing)

**Dataset:** `lesson-11/data/pairwise_comparisons.json`
- ✅ 100 pairwise comparisons across 4 dimensions
- ✅ 30 helpfulness, 30 correctness, 20 conciseness, 20 safety comparisons

**Generation Script:** `lesson-11/scripts/generate_pairwise_comparisons.py`
- ✅ CLI tool for generating new comparison datasets
- ✅ Parallel processing support
- ✅ Multiple dimension support

**Diagrams:**
- ✅ `diagrams/ranking_algorithm_comparison.mmd` - Algorithm decision flowchart
- ✅ `diagrams/comparative_eval_workflow.mmd` - End-to-end pipeline visualization
