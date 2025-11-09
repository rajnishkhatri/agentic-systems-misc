# Quantitative Metrics Family

**When to use this family**: Known evaluation criteria, need numeric benchmarks, comparing system versions, reporting to stakeholders

---

## Overview

Quantitative metrics provide **numeric measurements** for objective comparison. Use these when:
- ✅ Evaluation criteria are clear and testable
- ✅ Need to track performance over time
- ✅ Comparing multiple approaches/models
- ✅ Reporting results with statistical rigor

---

## Techniques in This Family

### 1. Recall@k (HW4)
**What it measures**: What fraction of queries successfully retrieve the target in top-k results

**Formula**: `Recall@k = (# queries with target in top-k) / (total queries)`

**Typical ranges**:
- Recall@1: 40-60% (target is #1 result)
- Recall@3: 60-80% (target in top 3)
- Recall@5: 70-90% (target in top 5)

**Use for**: Retrieval evaluation (RAG systems)

---

### 2. Mean Reciprocal Rank (MRR) (HW4)
**What it measures**: Average quality of ranking (rewards higher positions)

**Formula**: `MRR = (1/N) × Σ(1 / rank_i)`

**Example**:
```
Query 1: rank=1 → RR=1.0
Query 2: rank=3 → RR=0.33
Query 3: rank=2 → RR=0.5
MRR = (1.0+0.33+0.5)/3 = 0.61
```

**Interpretation**: MRR=0.61 means target averages around rank 1.6

**Use for**: Ranking quality evaluation

---

### 3. True Positive Rate (TPR) / Sensitivity (HW3)
**What it measures**: How often classifier correctly identifies positive examples

**Formula**: `TPR = TP / (TP + FN)`

**Interpretation**:
- TPR = 95% → Misses 5% of positive cases (low false negative rate)
- TPR = 70% → Misses 30% of positive cases (high false negative rate)

**Use for**: Binary classifier evaluation (LLM-as-Judge)

---

### 4. True Negative Rate (TNR) / Specificity (HW3)
**What it measures**: How often classifier correctly identifies negative examples

**Formula**: `TNR = TN / (TN + FP)`

**Interpretation**:
- TNR = 90% → Incorrectly flags 10% as positive (low false positive rate)
- TNR = 60% → Incorrectly flags 40% as positive (high false positive rate)

**Use for**: Binary classifier evaluation (LLM-as-Judge)

---

### 5. Transition Frequencies (HW5)
**What it measures**: How often agent fails at specific state transitions

**Data structure**: Matrix where cell (i,j) = # of failures from state i to state j

**Analysis**:
- **Row sums**: Which success state leads to most failures
- **Column sums**: Which failure state occurs most often (bottleneck)
- **Cell values**: Specific problematic transitions

**Use for**: Agent pipeline debugging

---

### 6. Confidence Intervals (HW3)
**What it measures**: Uncertainty range around point estimates

**Formula** (for success rate): 95% CI using normal approximation or judgy library

**Example**: Success rate = 85% ± 4% (95% CI: [81%, 89%])

**Why it matters**: "85% accurate" with CI [60%, 95%] is not very reliable. With CI [82%, 88%] is much more trustworthy.

**Use for**: Reporting evaluation results with statistical rigor

---

## Metric Selection Guide

### By Task Type

| Task | Primary Metric | Secondary Metrics |
|------|---------------|-------------------|
| **Retrieval (RAG)** | Recall@5 | Recall@1, MRR |
| **Binary Classification** | TPR + TNR | Accuracy, F1 |
| **Multi-Class Classification** | Precision/Recall per class | Macro/Micro F1 |
| **Ranking** | MRR | NDCG, MAP |
| **Agent Debugging** | Transition Frequencies | State-wise failure rates |

### By Stakeholder

**For Engineers**:
- TPR/TNR (understand error types)
- Transition frequencies (identify bottlenecks)

**For Product Managers**:
- Overall accuracy with confidence intervals
- Cost per 1000 queries
- Success rate trends over time

**For Executives**:
- Single summary metric (e.g., "92% accurate")
- Cost savings (e.g., "65% reduction")
- User impact (e.g., "resolves 80% of queries")

---

## Common Pitfalls

### ❌ Accuracy Paradox
**Problem**: 95% accuracy sounds great, but if 95% of examples are negative, a classifier that always predicts "negative" achieves 95% accuracy without learning anything.

**Solution**: Use TPR + TNR for imbalanced datasets

### ❌ Only Reporting Point Estimates
**Problem**: "85% accurate" without confidence intervals → don't know if it's reliably 85% or could be 60-95%

**Solution**: Always report 95% confidence intervals

### ❌ Metric Misalignment
**Problem**: Optimizing for Recall@1 when users actually look at top 5 results

**Solution**: Choose metrics that align with user behavior

### ❌ Cherry-Picking Metrics
**Problem**: Reporting only the metric that looks good

**Solution**: Pre-register primary metric before evaluation

---

## Combining Metrics

### Retrieval Systems
Report **all three**:
- Recall@1: User's best-case experience
- Recall@5: Realistic user experience (scanning top 5)
- MRR: Average ranking quality

### Binary Classifiers
Report **both**:
- TPR: False negative rate
- TNR: False positive rate

**Why both?** High TPR + Low TNR = system is too lenient (false positives). Low TPR + High TNR = system is too strict (false negatives).

### Agent Systems
Report **layered metrics**:
- Overall success rate (high-level)
- Per-state failure rates (debugging)
- Transition frequencies (root cause)

---

## Statistical Significance

### Sample Size Guidelines

**For binary classification** (target margin of error ±3%):
- Need ~1000 examples for 95% confidence
- 100 examples → ±10% margin
- 400 examples → ±5% margin

**For retrieval** (target Recall@5 ±5%):
- Need ~400 queries
- 100 queries → ±10% margin

### A/B Testing
When comparing two systems:
```python
# Paired t-test for query-level metrics
from scipy.stats import ttest_rel

baseline_scores = [1, 0, 1, 1, 0, ...]  # Per query
new_system_scores = [1, 1, 1, 1, 0, ...]

t_stat, p_value = ttest_rel(baseline_scores, new_system_scores)

if p_value < 0.05:
    print("Statistically significant improvement")
```

---

## Metric Evolution Over Time

### Monitoring Dashboard Structure
```
High-Level Overview (refresh daily):
├─ Overall success rate (with CI)
├─ Cost per 1000 queries
└─ Latency (p50, p95, p99)

Detailed Metrics (refresh weekly):
├─ TPR/TNR breakdown
├─ Failure mode frequencies
└─ Per-category performance

Deep Dive (on-demand):
├─ Transition matrices
├─ Error analysis
└─ User feedback correlation
```

---

## Integration with Other Families

### Qualitative Methods → Quantitative Metrics
After identifying failure modes qualitatively (HW2), measure their **frequency** quantitatively.

### Automated Evaluation → Quantitative Metrics
LLM-as-Judge (HW3) produces predictions → Calculate TPR/TNR → Apply bias correction.

### Optimization Techniques → Quantitative Metrics
Model cascades (Lesson 8) require measuring **cost vs accuracy trade-off** numerically.

---

## Real-World Example

**Scenario**: RAG system for recipe retrieval

### Baseline Measurement
```
Dataset: 100 synthetic queries
Retriever: BM25

Results:
Recall@1: 52% (52 queries found target as #1 result)
Recall@3: 71% (71 queries found target in top 3)
Recall@5: 83% (83 queries found target in top 5)
MRR: 0.62 (average reciprocal rank)
```

### Interpretation
- **Good**: 83% Recall@5 means most users find relevant recipe
- **Gap**: 52% → 83% (R@1 to R@5) means ranking could improve
- **MRR**: 0.62 ≈ average rank of 1.6, pretty good

### Improvement Experiment
```
New system: BM25 + Query Rewrite Agent

Results:
Recall@1: 58% (+6pp)
Recall@3: 79% (+8pp)
Recall@5: 91% (+8pp)
MRR: 0.68 (+0.06)

Statistical significance: p < 0.01 (paired t-test)
Cost: +$0.0002 per query (gpt-4o-mini rewrite)

Decision: Deploy (8% improvement worth small cost increase)
```

---

## Further Reading

**From tutorials**:
- [HW3: TPR/TNR for LLM-as-Judge](../../homeworks/hw3/TUTORIAL_INDEX.md)
- [HW4: Recall@k and MRR for Retrieval](../../homeworks/hw4/TUTORIAL_INDEX.md)
- [HW5: Transition Frequencies for Agents](../../homeworks/hw5/TUTORIAL_INDEX.md)

**External references**:
- Information Retrieval Evaluation (Manning et al.)
- Statistical Significance Testing in ML (Dror et al., 2018)
