# Comparative Evaluation & Leaderboards: A Comprehensive Guide

**Reading Time:** 20-25 minutes
**Difficulty:** Intermediate
**Prerequisites:** Lesson 10 (AI-as-Judge), basic statistics

---

## Table of Contents

1. [Pointwise vs Comparative Evaluation](#1-pointwise-vs-comparative-evaluation)
2. [Why Comparative Evaluation is More Reliable](#2-why-comparative-evaluation-is-more-reliable)
3. [Ranking Algorithms: Elo, Bradley-Terry, and TrueSkill](#3-ranking-algorithms-elo-bradley-terry-and-trueskill)
4. [Handling Transitivity Violations](#4-handling-transitivity-violations)
5. [Crowdsourced vs Expert Comparisons](#5-crowdsourced-vs-expert-comparisons)
6. [A/B Testing vs Comparative Evaluation](#6-ab-testing-vs-comparative-evaluation)
7. [Private Leaderboards and Contamination Prevention](#7-private-leaderboards-and-contamination-prevention)

---

## 1. Pointwise vs Comparative Evaluation

### Pointwise Evaluation

**Definition:** Evaluating each response independently on an absolute scale.

**Example:**
```
Query: "How do I make pasta carbonara?"
Response: "Heat olive oil in a pan, cook pancetta..."

Judge Prompt: "Rate this recipe response on a scale of 1-5 for helpfulness."
Output: 4/5
```

**Characteristics:**
- **Absolute scoring:** Each response gets a score without reference to other responses
- **Rating scales:** Typically 1-5 (Likert scale) or 0-100 (percentage)
- **Independent judgments:** No need to see alternative responses

**Pros:**
- ✅ Simple to implement and understand
- ✅ Can evaluate single responses in isolation
- ✅ Straightforward aggregation (mean, median)
- ✅ Works well for objective criteria (factual correctness, formatting)

**Cons:**
- ❌ Score drift over time (judge becomes more/less lenient)
- ❌ Inconsistent standards across different queries
- ❌ Scale misuse (judge avoids extremes, clusters around midpoint)
- ❌ Requires calibration for absolute quality thresholds

---

### Comparative Evaluation

**Definition:** Evaluating responses by direct pairwise comparison.

**Example:**
```
Query: "How do I make pasta carbonara?"

Response A: "Heat olive oil, cook pancetta, mix with pasta and raw eggs."
Response B: "Cook pasta. Fry guanciale. Mix eggs and cheese. Combine off heat."

Judge Prompt: "Which response is better?"
Output: "B" (more authentic, clearer steps)
```

**Characteristics:**
- **Relative judgments:** Responses evaluated side-by-side
- **Binary decisions:** "A is better" or "B is better" (sometimes "Tie")
- **Context-dependent:** Winner depends on specific comparison pair

**Pros:**
- ✅ More reliable for subjective criteria (helpfulness, coherence, style)
- ✅ Fewer calibration issues (easier to compare than rate)
- ✅ Robust to judge drift (comparisons are relative)
- ✅ Higher inter-annotator agreement

**Cons:**
- ❌ Requires multiple responses per query
- ❌ Scales as O(n²) for n models (all pairwise comparisons)
- ❌ Need ranking algorithm to derive leaderboard
- ❌ Potential for intransitive preferences (cycles)

---

### When to Use Which?

| Criterion | Pointwise | Comparative |
|-----------|-----------|-------------|
| **Objective criteria** (exact match, formatting) | ✅ Preferred | ⚠️ Overkill |
| **Subjective criteria** (helpfulness, coherence) | ⚠️ Less reliable | ✅ Preferred |
| **Single model evaluation** | ✅ Works | ❌ Need alternatives |
| **Model comparison** | ⚠️ Absolute scores can mislead | ✅ Direct comparison |
| **Speed** | ✅ Faster (linear) | ⚠️ Slower (quadratic) |
| **Interpretability** | ✅ Easy (score = quality) | ⚠️ Need ranking algorithm |

**Rule of Thumb:** Use comparative evaluation for model selection and ranking; use pointwise for pass/fail filtering.

---

## 2. Why Comparative Evaluation is More Reliable

### Research Evidence

**Chatbot Arena Study (LMSYS, 2023):**
> Comparative evaluation requires **~50% fewer human judgments** to achieve the same statistical power as pointwise evaluation for ranking models.

**Key Finding:** Human annotators can more reliably choose between two responses than assign absolute scores.

---

### Cognitive Psychology Explanation

**1. Anchoring Bias in Pointwise Evaluation**

Humans struggle with absolute judgments without reference points.

**Example:**
```
Query: "Explain quantum entanglement."
Response: "Quantum entanglement is when two particles share a quantum state..."

Judge without reference: "Hmm, is this a 3/5 or 4/5?"
```

Without seeing alternatives, judges:
- Over-rely on first impression
- Drift toward middle values (avoiding extremes)
- Struggle to maintain consistent standards across queries

**2. Relative Comparison Advantage**

Humans excel at detecting differences.

**Example:**
```
Response A: "Quantum entanglement is spooky action at a distance."
Response B: "Quantum entanglement occurs when particles share correlated quantum states..."

Judge: "B is clearly better—more precise and less anthropomorphic."
```

---

### Empirical Validation: Inter-Annotator Agreement

**Pointwise Agreement (Krippendorff's Alpha):**
- Expert annotators: ~0.65 (moderate agreement)
- Crowd workers: ~0.45 (weak agreement)

**Comparative Agreement (Cohen's Kappa):**
- Expert annotators: ~0.80 (strong agreement)
- Crowd workers: ~0.70 (substantial agreement)

**Interpretation:** Annotators agree more on "which is better" than "how good is this."

---

### Sample Efficiency

To detect a **5% improvement** with 95% confidence:

**Pointwise (A/B testing):**
- Collect ~1,600 independent ratings per model
- Total judgments: 3,200

**Comparative (pairwise):**
- Collect ~1,000 pairwise comparisons
- Total judgments: 1,000

**Result:** **3.2x sample efficiency** for comparative evaluation.

---

## 3. Ranking Algorithms: Elo, Bradley-Terry, and TrueSkill

### Elo Rating System

**Origin:** Developed by Arpad Elo for chess in the 1960s. Adapted for LLMs by Chatbot Arena.

**Formula:**
```
Expected Score:  E_A = 1 / (1 + 10^((R_B - R_A) / 400))
New Rating:      R_A' = R_A + K * (S_A - E_A)

Where:
- R_A, R_B: Current ratings for models A and B
- E_A: Expected win probability for A
- S_A: Actual outcome (1 if A wins, 0 if B wins, 0.5 if tie)
- K: Learning rate (K-factor, typically 32)
```

**Intuition:**
- If you beat a weaker opponent: Small rating gain
- If you beat a stronger opponent: Large rating gain (upset!)
- Ratings converge to true skill over many matches

**Pros:**
- ✅ **Online updates:** Process comparisons one at a time
- ✅ **Simple:** Easy to implement and explain
- ✅ **Well-understood:** 60+ years of use in competitive games
- ✅ **Handles new models:** Just initialize at default rating (1500)

**Cons:**
- ❌ **Order-dependent:** Early matches have outsized impact
- ❌ **No uncertainty:** Point estimate only, no confidence intervals
- ❌ **K-factor tuning:** Need to choose learning rate

**When to use:** Dynamic leaderboards with continuous model updates (e.g., Chatbot Arena).

---

### Bradley-Terry Model

**Origin:** Probabilistic model from statistics (Bradley & Terry, 1952).

**Formula:**
```
P(A beats B) = exp(θ_A) / (exp(θ_A) + exp(θ_B))
             = 1 / (1 + exp(θ_B - θ_A))

Where:
- θ_A, θ_B: Latent skill parameters for models A and B
- Estimated via maximum likelihood using ALL pairwise data
```

**Intuition:**
- Each model has a latent "skill" parameter θ
- Win probability follows a logistic curve
- Use MLE to find skills that best explain observed comparisons

**Pros:**
- ✅ **Order-independent:** Uses all data simultaneously
- ✅ **Uncertainty estimates:** Can compute standard errors for skills
- ✅ **Statistically principled:** Maximum likelihood estimation

**Cons:**
- ❌ **Batch-only:** Must refit from scratch for new data
- ❌ **More complex:** Requires optimization library
- ❌ **Doesn't handle new models:** Need to refit entire model

**When to use:** One-time ranking of fixed set of models with complete comparison data.

---

### TrueSkill (Microsoft Research)

**Extension of Elo/Bradley-Terry for multi-player scenarios.**

**Key Features:**
- Represents skill as a Gaussian distribution: μ (mean) ± σ (uncertainty)
- Updates both mean and variance after each match
- Handles team competitions (not just 1v1)

**Pros:**
- ✅ Uncertainty-aware (confident about established models, uncertain about new ones)
- ✅ Conservative matchmaking (avoids unfair pairings)
- ✅ Handles draws and multi-way comparisons

**Cons:**
- ❌ More complex than Elo
- ❌ Requires TrueSkill library (not standard)

**When to use:** Advanced scenarios with team competitions or when you need uncertainty quantification.

**Note:** TrueSkill is not covered in detail in this lesson (Elo and Bradley-Terry are sufficient for most LLM evaluation use cases).

---

### Comparison Table

| Feature | Elo | Bradley-Terry | TrueSkill |
|---------|-----|---------------|-----------|
| **Update type** | Online (incremental) | Batch (refit all) | Online |
| **Uncertainty** | No | Yes (standard errors) | Yes (σ parameter) |
| **Order-dependent** | Yes | No | No |
| **Handles ties** | Yes | Can extend | Yes |
| **Complexity** | Low | Medium | High |
| **Best for** | Live leaderboards | Static analysis | Multi-player |

---

## 4. Handling Transitivity Violations

### What are Transitivity Violations?

**Definition:** A cycle in pairwise preferences where A > B, B > C, but C > A.

**Example:**
```
Comparison 1: Model A beats Model B (A > B)
Comparison 2: Model B beats Model C (B > C)
Comparison 3: Model C beats Model A (C > A) ← Violation!

Transitive expectation: A > B > C, so A should beat C
Reality: C beats A (cycle!)
```

---

### Why Do Violations Occur?

**1. Noise in Judgments**

Human judges (or AI judges) aren't perfectly consistent.

**Example:**
- Judge evaluates A vs B on Monday → A wins
- Judge evaluates same pair on Friday → B wins (different mood/context)

**Mitigation:** Collect multiple judgments per pair, use majority vote.

**2. Query-Dependent Preferences**

Some models excel on certain query types.

**Example:**
- Model A (GPT-4): Best at complex reasoning
- Model B (Claude): Best at creative writing
- Model C (Llama-2): Best at factual recall

On reasoning query: A > B > C
On creative query: B > C > A
On factual query: C > A > B

**Aggregate Result:** Cycles appear due to heterogeneous query distribution.

**Mitigation:** Stratify comparisons by query type, fit separate rankings.

**3. Incomparable Models**

Models that serve different purposes.

**Example:**
- Model A: Concise, fast responses
- Model B: Detailed, slow responses

For "quick answer" query: A > B
For "in-depth explanation" query: B > A

**Mitigation:** Define clear evaluation criteria before comparison.

---

### Measuring Transitivity Violations

**Cycle Detection Algorithm:**

```python
def count_transitivity_violations(comparisons):
    """Count cycles in pairwise comparisons."""
    wins = defaultdict(set)  # wins[A] = {B, C, ...} (A beat B and C)

    for comp in comparisons:
        winner = comp['winner']
        loser = comp['model_a'] if winner == comp['model_b'] else comp['model_b']
        wins[winner].add(loser)

    violations = 0
    models = list(wins.keys())

    # Check all triplets (A, B, C)
    for i, A in enumerate(models):
        for j, B in enumerate(models):
            for k, C in enumerate(models):
                if A != B != C != A:
                    # Check if A > B, B > C, but C > A
                    if B in wins[A] and C in wins[B] and A in wins[C]:
                        violations += 1

    return violations
```

**Violation Rate:**
```
Violation Rate = (Number of cyclic triplets) / (Total triplets)
```

**Typical Values:**
- **<5%:** Excellent consistency (likely objective criteria)
- **5-10%:** Good consistency (expected noise)
- **10-15%:** Moderate consistency (check for query heterogeneity)
- **>15%:** Poor consistency (investigate judge quality or stratify by query type)

---

### How Ranking Algorithms Handle Violations

**Elo:**
- Doesn't explicitly detect violations
- Ratings converge to a "best fit" that minimizes prediction error
- Cycles absorbed into rating uncertainty

**Bradley-Terry:**
- Fits a model that minimizes total log-likelihood
- Implicitly finds skills that best explain all comparisons (including violations)
- Violations reduce model fit (higher deviance)

**Practical Implication:** Both algorithms are robust to moderate violations (<10%).

---

## 5. Crowdsourced vs Expert Comparisons

### Crowdsourced Comparisons

**Examples:** Amazon Mechanical Turk, Scale AI, Chatbot Arena (volunteer users).

**Pros:**
- ✅ **Scalable:** Can collect 10,000+ judgments per day
- ✅ **Cost-effective:** $0.05-0.20 per comparison (vs $5-10 for experts)
- ✅ **Diverse perspectives:** Represents real-world user preferences
- ✅ **Fast:** Parallel work by many annotators

**Cons:**
- ❌ **Lower quality:** ~20% error rate (vs ~5% for experts)
- ❌ **Gaming:** Some workers click randomly for payment
- ❌ **Limited domain knowledge:** Can't evaluate technical content (medical, legal)

**Best for:** Consumer-facing applications (chatbots, content generation) where user preference is the ground truth.

---

### Expert Comparisons

**Examples:** Domain specialists (e.g., doctors for medical QA, lawyers for legal analysis).

**Pros:**
- ✅ **High quality:** ~5% error rate
- ✅ **Domain expertise:** Can evaluate correctness, not just preference
- ✅ **Consistent standards:** Experts apply well-calibrated criteria

**Cons:**
- ❌ **Expensive:** $5-50 per comparison (depending on domain)
- ❌ **Slow:** Limited pool of qualified annotators
- ❌ **Potential bias:** Experts may prefer responses matching their training

**Best for:** High-stakes domains (medical, legal, finance) where correctness matters more than user preference.

---

### Hybrid Approach

**Strategy:** Use crowdsourced comparisons for initial ranking, then expert validation.

**Example (Chatbot Arena):**
1. Collect 100,000 crowdsourced comparisons → Initial Elo rankings
2. Hire experts to validate top-10 models → Confirm ordering
3. Use crowd + expert data to compute final leaderboard

**Benefits:**
- Cost-effective (experts only for ambiguous cases)
- Scalable (crowd does bulk of work)
- High-quality (experts ensure correctness)

---

## 6. A/B Testing vs Comparative Evaluation

### A/B Testing (Traditional)

**Setup:**
- Deploy Model A to 50% of users
- Deploy Model B to 50% of users
- Measure success metric (e.g., user satisfaction, task completion rate)

**Example:**
```
Metric: % of queries where user clicks "thumbs up"

Model A: 72% thumbs up (n=1,000 queries)
Model B: 75% thumbs up (n=1,000 queries)

Statistical Test: Is 3% difference significant?
Z-test: p < 0.05 → Yes, B is significantly better
```

**Pros:**
- ✅ Real-world deployment (ecological validity)
- ✅ Captures long-term effects (user retention, engagement)
- ✅ Measures business metrics (revenue, conversion)

**Cons:**
- ❌ Requires production deployment (risky)
- ❌ Slow (need days/weeks for statistical power)
- ❌ Sample size inefficiency (need ~1,600 users per variant for 5% difference detection)

---

### Comparative Evaluation (Side-by-Side)

**Setup:**
- Show users both Model A and Model B responses
- Ask: "Which is better?"

**Example:**
```
Query: "Explain neural networks."

Response A: "Neural networks are like brains..."
Response B: "Neural networks are computational models with layers of interconnected nodes..."

User choice: B (more precise)

Repeat for 1,000 queries → 55% prefer B
```

**Pros:**
- ✅ **Sample efficient:** ~1,000 comparisons vs ~3,200 A/B test users
- ✅ **Fast:** Offline evaluation, no production deployment
- ✅ **Cheaper:** Use crowdworkers or LLM judges
- ✅ **Controlled:** Same query shown to both models

**Cons:**
- ❌ Artificial setting (users don't see alternatives in production)
- ❌ Doesn't capture long-term effects (only first-impression preferences)
- ❌ Position bias (order matters—need to randomize)

---

### Sample Size Comparison

**Scenario:** Detect a 5% improvement in win rate with 95% confidence.

**A/B Testing:**
```
Sample size per variant: n = (Z_α/2 + Z_β)² * (p₁(1-p₁) + p₂(1-p₂)) / (p₂ - p₁)²

Assuming p₁ = 0.70, p₂ = 0.75:
n ≈ 1,600 per variant
Total: 3,200 users
```

**Comparative Evaluation:**
```
Sample size for pairwise comparisons: n = (Z_α/2 + Z_β)² / (4 * (p - 0.5)²)

Assuming p(B wins) = 0.55:
n ≈ 1,000 comparisons
Total: 1,000 judgments
```

**Result:** **3.2x fewer judgments** for comparative evaluation.

---

### When to Use Which?

| Scenario | A/B Testing | Comparative Evaluation |
|----------|-------------|------------------------|
| **Pre-production model selection** | ❌ Too slow | ✅ Fast and cheap |
| **Final validation before launch** | ✅ Real-world signal | ⚠️ May miss production effects |
| **Comparing 5+ models** | ❌ Need 5 groups | ✅ Pairwise comparisons scale |
| **Long-term impact (retention)** | ✅ Captures | ❌ Misses |
| **Limited production traffic** | ❌ Need 1,000s of users | ✅ Offline evaluation |

**Best Practice:** Use comparative evaluation for model selection, then A/B test finalists in production.

---

## 7. Private Leaderboards and Contamination Prevention

### The Benchmark Contamination Problem

**Definition:** When training data includes evaluation benchmarks, causing artificially high scores.

**Example (MMLU Contamination):**
- MMLU benchmark: 15,000 multiple-choice questions from exams
- GPT-4 training data: Scraped from internet (includes exam prep sites)
- Result: GPT-4 may have "seen" MMLU questions during training → Inflated score

**Evidence:**
- GPT-4: 86% MMLU accuracy (2023)
- GPT-3.5: 70% MMLU accuracy (2022)
- Improvement: 16% (but is it true skill or memorization?)

---

### How Public Leaderboards Fail

**Problem:** Once a benchmark is public, models can overfit to it.

**Process:**
1. Researcher releases benchmark (e.g., HumanEval for code)
2. Lab A trains model, scores 65% → Publishes
3. Lab B sees public test set, trains on similar data, scores 75%
4. Lab C directly trains on HumanEval (unintentionally via web scrape), scores 85%
5. Leaderboard saturates → Benchmark loses signal

**Example:** GSM8K (math word problems)
- 2021: GPT-3 scores 35%
- 2023: GPT-4 scores 92%
- 2024: Fine-tuned Llama-3 scores 97%
- Problem: Is Llama-3 better at math, or just better at GSM8K-style questions?

---

### Solution: Private Leaderboards

**Strategy:** Keep test set secret, only allow limited submissions.

**Examples:**

**1. Kaggle-Style Private Leaderboard**
- Public leaderboard: Use 50% of test set
- Private leaderboard: Hold out 50% of test set
- Reveal private leaderboard only after competition ends
- Prevents overfitting to public test set

**2. HELM (Holistic Evaluation of Language Models)**
- Continuously add new test scenarios
- Some scenarios are private (not revealed to model developers)
- Rotate private scenarios every 6 months

**3. Chatbot Arena**
- Test set = live user queries (unpredictable)
- Models can't "study" for the test
- Leaderboard updates continuously based on real user votes

---

### Best Practices for Contamination Prevention

**1. Diverse Test Set Construction**

Don't just sample from one distribution.

**Example:**
- Bad: All math problems from GSM8K style ("John has 5 apples...")
- Good: Mix of GSM8K + AMC12 + Math Olympiad + Real student homework

**Benefit:** Harder to overfit when test set is heterogeneous.

**2. Regular Test Set Rotation**

**Schedule:**
- Month 1-3: Use Test Set A
- Month 4-6: Use Test Set B
- Month 7-9: Use Test Set C

**Benefit:** Even if Test Set A leaks, B and C remain clean.

**3. Submission Limits**

**Rule:** Each team can submit at most 5 models per month.

**Benefit:** Prevents "gridsearch" over leaderboard (trying 1,000 hyperparameter combinations).

**4. Require Training Data Disclosure**

**Rule:** To submit to leaderboard, must disclose training data sources.

**Example (HELM):**
```
Model: GPT-4
Training Data:
- CommonCrawl (2023 snapshot)
- Books3
- Wikipedia (2022)
- GitHub (public repos)

Excluded: MMLU, HumanEval, HellaSwag (benchmark contamination prevention)
```

**Benefit:** Community can audit for contamination.

**5. Use Differential Leaderboards**

**Idea:** Compare models only on queries where training data provenance is certain.

**Example:**
- GPT-4 trained on data before 2022
- Test on queries from 2024 → No contamination possible

---

### Case Study: Chatbot Arena (LMSYS)

**Approach:**
- Crowdsourced comparisons from real users
- Dynamic test set (users ask unpredictable questions)
- Anonymous model labels (users don't know which model they're rating)
- Continuous updates (leaderboard refreshes daily)

**Result:**
- 100,000+ comparisons collected
- Low contamination risk (can't train on future user queries)
- High ecological validity (real-world usage)

**Leaderboard (May 2024):**
1. GPT-4 (Elo: 1250)
2. Claude-3-Opus (Elo: 1210)
3. Gemini-Pro (Elo: 1150)
4. GPT-3.5-Turbo (Elo: 1100)

**Criticism:**
- Self-selection bias (users who visit arena ≠ general population)
- Position bias (sometimes users prefer first response)
- Query distribution skew (more creative queries than factual)

**Mitigation:**
- Randomize model order (swap A/B positions)
- Stratify analysis by query category
- Validate top models with expert evaluators

---

## Summary

### Key Takeaways

1. **Comparative evaluation is more reliable than pointwise** for subjective criteria (3.2x sample efficiency).

2. **Choose ranking algorithm based on use case:**
   - **Elo:** Live leaderboards with continuous updates
   - **Bradley-Terry:** One-time ranking with uncertainty estimates

3. **Transitivity violations are expected** (<10% is normal). Algorithms are robust to moderate violations.

4. **Hybrid crowdsourcing + experts** balances cost and quality.

5. **Comparative evaluation is faster and cheaper than A/B testing** for model selection (use A/B for final validation).

6. **Private leaderboards prevent benchmark contamination.** Use diverse test sets, rotation, and submission limits.

---

## Practical Recommendations

### For Model Selection
- Use comparative evaluation with crowdsourced judgments
- Collect 30-50 comparisons per model pair
- Fit Elo rankings for interpretability

### For Leaderboard Deployment
- Use private test set with rotation
- Limit submissions (5 per team per month)
- Require training data disclosure
- Validate top-3 with expert evaluators

### For Research
- Report both pointwise metrics and pairwise win rates
- Check for transitivity violations (report violation rate)
- Stratify analysis by query type

---

## Further Reading

**Papers:**
- [Chatbot Arena: Elo Rating for LLM Evaluation (LMSYS, 2023)](https://arxiv.org/abs/2306.05685)
- [Bradley-Terry Model (Bradley & Terry, 1952)](https://www.jstor.org/stable/2334029)
- [On the Dangers of Stochastic Parrots (Bender et al., 2021)](https://dl.acm.org/doi/10.1145/3442188.3445922) — Discusses benchmark contamination

**Leaderboards:**
- [Chatbot Arena](https://chat.lmsys.org/?leaderboard)
- [AlpacaEval](https://tatsu-lab.github.io/alpaca_eval/)
- [Open LLM Leaderboard](https://huggingface.co/spaces/HuggingFaceH4/open_llm_leaderboard)

**Next Steps:**
- Implement Elo ranking in `elo_ranking_tutorial.ipynb`
- Compare Elo vs Bradley-Terry in `bradley_terry_ranking_tutorial.ipynb`
- Analyze sample efficiency in `ab_testing_vs_comparative_eval.ipynb`

---

## Related Tutorials

- [Lesson 10: AI-as-Judge Production Guide](../lesson-10/ai_judge_production_guide.md) - Engineer judges for pairwise comparisons
- [Lesson 10: Judge Bias Detection Tutorial](../lesson-10/judge_bias_detection_tutorial.ipynb) - Detect position bias in comparisons
- [Elo Ranking Tutorial (Notebook)](elo_ranking_tutorial.ipynb) - Implement dynamic leaderboard rankings
- [Bradley-Terry Ranking Tutorial (Notebook)](bradley_terry_ranking_tutorial.ipynb) - Probabilistic skill estimation
- [A/B Testing vs Comparative Eval (Notebook)](ab_testing_vs_comparative_eval.ipynb) - Sample efficiency analysis
- [Lesson 9-11: Evaluation Dashboard](../lesson-9-11/README.md) - Visualize unified metrics across lessons

---

**Last Updated:** 2025-11-09
**Author:** AI Evaluation Course Team
