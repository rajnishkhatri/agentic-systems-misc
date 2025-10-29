# Lesson 8: Tutorial Index

## Overview

Lesson 8 teaches **model cascade optimization** for cost-effective AI systems. Using SMS spam classification as a case study, you'll learn to route queries between cheap and expensive models based on confidence scores (logprobs), achieving target accuracy while minimizing cost. This pattern is critical for production systems handling millions of requests.

**Learning Time:** ~3-4 hours
**Difficulty:** Intermediate to Advanced
**Prerequisites:** Understanding of classification tasks, probability/confidence scores, cost-accuracy trade-offs

---

## Learning Objectives

By completing these tutorials, you will be able to:
- ✅ Understand cascade architecture patterns and when to use them
- ✅ Extract and interpret log probabilities (logprobs) from LLM outputs
- ✅ Set confidence thresholds for routing decisions
- ✅ Calculate cost-accuracy trade-offs for model selection
- ✅ Implement binary classification cascades
- ✅ Evaluate cascade performance (accuracy, cost, latency)
- ✅ Optimize thresholds for specific accuracy targets
- ✅ Apply cascade patterns to multi-class and ranking problems

---

## Tutorials

### 1. Model Cascade Concepts
**File:** `model_cascade_concepts.md`
**Reading Time:** 18-22 minutes
**Topics:**
- What is a model cascade and why use it?
- Cost-accuracy trade-off fundamentals
- Routing strategies: confidence, complexity, domain
- Cascade architecture patterns (binary, multi-tier, specialized)
- When cascades are effective vs. when they fail
- Latency considerations for production systems
- Evaluation metrics for cascades

**When to use:** Start here to understand the cascade paradigm before implementing.

**Key Pattern:**
```
Input → Cheap Model (GPT-4o-mini)
           ↓
     High confidence? → Return answer (save cost)
           ↓
     Low confidence → Expensive Model (GPT-4o) → Return answer
```

---

### 2. Spam Classification Tutorial (Interactive)
**File:** `spam_classification_tutorial.ipynb`
**Execution Time:** 25-30 minutes
**Topics:**
- Binary classification with LLMs (spam vs. ham)
- Extracting log probabilities for "True"/"False" tokens
- Normalizing logprobs to confidence scores
- Setting confidence thresholds (0.7, 0.8, 0.9, 0.95)
- Measuring cascade accuracy on test set
- Calculating cost savings vs. baseline
- Analyzing failure cases (low-confidence errors)

**When to use:** After understanding concepts, use this to implement and evaluate a cascade.

**Interactive Features:**
- Live SMS spam classification
- Logprob extraction and visualization
- Threshold sweep analysis
- Cost calculation for different strategies
- Confusion matrix for cascade performance

**Expected Results:**
- Target: 99% accuracy (matching expensive model alone)
- Cascade: 85-90% routed to cheap model → 40-50% cost savings
- Remaining 10-15% routed to expensive model for hard cases

---

### 3. Cascade Decision Tree Diagram (Visual)
**File:** `diagrams/cascade_decision_tree.mmd`
**Format:** Mermaid diagram (viewable on GitHub)
**Topics:**
- Routing logic based on confidence thresholds
- Decision paths for different confidence levels
- Cost and accuracy implications of each path
- Fallback mechanisms for edge cases

**When to use:** Reference this to understand routing logic visually.

---

## Recommended Learning Path

```
┌────────────────────────────────────────────────────────┐
│       Lesson 8: Model Cascade Workflow                 │
├────────────────────────────────────────────────────────┤
│                                                        │
│  STEP 1: Understand Cascades                          │
│  ┌──────────────────────────────────────────────────┐ │
│  │ 1. Complete "Model Cascade Concepts" tutorial    │ │
│  │ 2. Review cost-accuracy trade-off examples       │ │
│  │ 3. Understand when cascades are appropriate      │ │
│  └──────────────────────────────────────────────────┘ │
│                                                        │
│  STEP 2: Implement Binary Cascade                     │
│  ┌──────────────────────────────────────────────────┐ │
│  │ 4. Load SMS spam dataset (sms_spam.csv)          │ │
│  │ 5. Complete "Spam Classification" tutorial       │ │
│  │ 6. Run model_cascade.py for baseline comparison │ │
│  │    → Cheap model only (baseline cost)            │ │
│  │    → Expensive model only (target accuracy)      │ │
│  │    → Cascade (optimized cost+accuracy)           │ │
│  └──────────────────────────────────────────────────┘ │
│                                                        │
│  STEP 3: Optimize Thresholds                          │
│  ┌──────────────────────────────────────────────────┐ │
│  │ 7. Test thresholds: 0.70, 0.80, 0.90, 0.95, 0.99│ │
│  │ 8. For each threshold, measure:                  │ │
│  │    - % routed to cheap model                     │ │
│  │    - Final cascade accuracy                      │ │
│  │    - Total cost (in dollars)                     │ │
│  │ 9. Identify optimal threshold for 99% accuracy  │ │
│  └──────────────────────────────────────────────────┘ │
│                                                        │
│  STEP 4: Analysis & Reporting                         │
│  ┌──────────────────────────────────────────────────┐ │
│  │ 10. Calculate cost savings vs. expensive-only    │ │
│  │ 11. Analyze failure cases (where cascade errs)  │ │
│  │ 12. Document findings and recommendations        │ │
│  └──────────────────────────────────────────────────┘ │
└────────────────────────────────────────────────────────┘
```

---

## Key Concepts

### Model Cascade Architecture
A **cascade** uses cheap models for easy cases, expensive models for hard cases:

**Benefits:**
- ✅ **Cost Savings:** 40-70% reduction vs. using expensive model for everything
- ✅ **Maintained Accuracy:** Matches expensive model on aggregate
- ✅ **Latency Optimization:** Cheap models are often faster

**Requirements:**
- Cheap model must provide confidence scores
- Clear threshold for "confident" vs. "uncertain"
- Expensive model must handle hard cases well

### Log Probabilities (Logprobs)
**Logprobs** are the natural logarithm of token probabilities:

```python
# LLM considers two tokens for binary classification
logprobs = {
    "True": -0.05,   # log(P("True")) ≈ log(0.95) = -0.05
    "False": -3.00   # log(P("False")) ≈ log(0.05) = -3.00
}

# Convert to probabilities
prob_true = exp(-0.05) = 0.9512
prob_false = exp(-3.00) = 0.0498

# Normalize (ensure sum = 1)
normalized_prob_true = 0.9512 / (0.9512 + 0.0498) = 0.95
```

**High confidence:** One token has much higher probability
**Low confidence:** Tokens have similar probabilities

### Confidence Thresholding
**Routing decision:**

```python
confidence = get_answer_prob_binary(logprobs, answer)

if confidence >= threshold:  # e.g., 0.90
    # High confidence: Trust cheap model
    return cheap_model_answer
else:
    # Low confidence: Route to expensive model
    return expensive_model_answer
```

**Threshold Trade-offs:**
| Threshold | % to Cheap | Accuracy | Cost |
|-----------|------------|----------|------|
| 0.70 | 95% | 98.2% | Low |
| 0.90 | 85% | 99.0% | Medium |
| 0.95 | 70% | 99.5% | Higher |
| 0.99 | 40% | 99.9% | Highest |

### Cost Analysis
**Cost calculation:**

```python
# Model pricing (example)
CHEAP_COST_PER_CALL = $0.0001   # GPT-4o-mini
EXPENSIVE_COST_PER_CALL = $0.001 # GPT-4o

# Cascade strategy
cheap_calls = 1000 * 0.85 = 850
expensive_calls = 1000 * 0.15 = 150

cascade_cost = (850 * $0.0001) + (150 * $0.001)
             = $0.085 + $0.150 = $0.235

# Baseline (expensive only)
baseline_cost = 1000 * $0.001 = $1.00

# Savings
savings = ($1.00 - $0.235) / $1.00 = 76.5%
```

---

## Practical Exercises

After completing the tutorials, try these exercises:

1. **Threshold Optimization**
   - Run cascade with thresholds: 0.5, 0.7, 0.8, 0.9, 0.95, 0.99
   - Plot: threshold vs. accuracy, threshold vs. cost
   - Identify the "knee" of the curve (optimal trade-off)

2. **Failure Analysis**
   - Find all examples where cascade made errors
   - Check: Were they routed to cheap or expensive model?
   - Identify patterns (e.g., "ambiguous wording", "sarcasm")
   - Propose improvements (better prompts, different threshold)

3. **Multi-Model Cascade**
   - Extend to 3 models: mini → small → large
   - Set two thresholds (e.g., 0.80 and 0.95)
   - Measure if 3-tier cascade improves cost-accuracy

---

## Common Pitfalls

### Architecture Design
- ❌ **No confidence scores:** Model doesn't provide logprobs → can't route
- ❌ **Cheap model too weak:** Even high-confidence answers are wrong
- ❌ **Expensive model not much better:** Paying more for similar accuracy
- ❌ **Ignoring latency:** Cascading adds overhead (sequential calls)

### Threshold Selection
- ❌ **Too low (0.6):** Routes bad answers from cheap model → hurts accuracy
- ❌ **Too high (0.99):** Routes everything to expensive model → no savings
- ❌ **No validation:** Setting threshold on test set (data leakage)
- ❌ **Fixed threshold:** Not adjusting for different task difficulties

### Cost Calculation
- ❌ **Forgetting cascade overhead:** Both models called in series
- ❌ **Ignoring prompt length:** Longer prompts cost more per call
- ❌ **No latency cost:** Cascades add user-perceived delay
- ❌ **Only optimizing for cost:** Ignoring accuracy degradation

### Evaluation
- ❌ **Only measuring accuracy:** Not tracking which model answered
- ❌ **No baseline comparison:** Don't know if cascade helps
- ❌ **Insufficient test set:** 50 examples isn't enough to measure 99% accuracy reliably
- ❌ **No error analysis:** Not understanding why cascade fails

---

## Reference Files

### Assignment Materials
- [`README.md`](README.md) - Lesson overview (currently missing - to be created)
- [`model_cascade.py`](model_cascade.py) - Cascade implementation script
- [`sms_spam.csv`](sms_spam.csv) - SMS spam dataset (~5000 messages)
- [`sms_spam_predictions.csv`](sms_spam_predictions.csv) - Predictions with confidence scores
- [`sms_spam_predictions_test.csv`](sms_spam_predictions_test.csv) - Test set results
- [`sms_spam_predictions_train.csv`](sms_spam_predictions_train.csv) - Train set results

---

## Tools & Libraries

**Required:**
- `litellm` - Multi-provider LLM API access with logprobs
- `pandas` - Dataset manipulation
- `numpy` - Probability calculations
- `concurrent.futures` - Parallel processing (optional)
- `tqdm` - Progress bars

**Installation:**
```bash
pip install litellm pandas numpy tqdm
```

**API Requirements:**
- OpenAI API key (for GPT-4o-mini and GPT-4o)
- Or any provider supporting logprobs via litellm

---

## Expected Outputs

After completing Lesson 8, you should have:
- ✅ Understanding of cascade architecture patterns
- ✅ Working spam classification cascade
- ✅ Performance metrics (accuracy, cost, routing %) for various thresholds
- ✅ Cost analysis showing savings vs. baseline
- ✅ Recommendations for production deployment

**Example Results:**
```
Baseline Strategies:
  Cheap Only (GPT-4o-mini):  Accuracy = 96.5%, Cost = $0.50
  Expensive Only (GPT-4o):   Accuracy = 99.2%, Cost = $5.00

Cascade Strategy (threshold = 0.90):
  Accuracy = 99.1%
  % to Cheap Model = 87%
  Total Cost = $1.15
  Savings vs. Expensive = 77%

Interpretation: Cascade achieves 99.1% accuracy (matching
expensive model) while saving 77% in cost by routing 87% of
queries to the cheap model.
```

---

## Real-World Applications

Model cascades are used in production for:
- **Content moderation:** Cheap model for obvious cases, expensive for nuanced
- **Customer support:** Simple queries → FAQ lookup, complex → agent routing
- **Search ranking:** Fast reranker for top-100, expensive reranker for top-10
- **Translation:** Short/common phrases → cache, long/technical → expensive model
- **Code generation:** Template code → cheap model, complex logic → expensive

**Key Insight:** Most production queries are "easy"—cascades exploit this to save 50-80% in cost.

---

## Connection to Course Themes

| Lesson/HW | Connection to Cascades |
|-----------|------------------------|
| **HW3** | LLM-as-Judge uses cheap model as judge, expensive for ground truth |
| **HW4** | Query rewrite agent could cascade: simple queries → no rewrite, complex → rewrite |
| **Lesson 4** | Ground truth labeling (expensive) vs. judge evaluation (cheap) |

**Broader Theme:** Optimization for production requires balancing accuracy, cost, and latency—cascades are one powerful pattern.

---

## Next Steps

After completing Lesson 8, you'll have:
- ✅ Cost optimization skills for production AI systems
- ✅ Understanding of confidence-based routing
- ✅ Ability to evaluate and optimize cascade architectures

**Explore advanced topics:**
- Multi-tier cascades (3+ models)
- Domain-specific routing (different models for different query types)
- Dynamic threshold adjustment based on load
- Combining cascades with caching and retrieval

---

## FAQ

**Q: Does cascading always save money?**
A: No. If the cheap model is too weak, you'll route everything to the expensive model and waste the cheap call. Need 60%+ routing to cheap model for meaningful savings.

**Q: Can I use embeddings instead of logprobs for confidence?**
A: Embeddings don't directly provide confidence. Logprobs are ideal for classification. For other tasks, consider model-specific confidence metrics.

**Q: What if the cheap model doesn't support logprobs?**
A: Some models provide alternative confidence scores. Otherwise, cascading based on input features (e.g., query length, keyword presence) is an option.

**Q: Should I cascade in series or parallel?**
A: Series is standard (cheap first, expensive if needed). Parallel (both at once) wastes the cheap model's cost but reduces latency.

**Q: How do I handle cases where both models are uncertain?**
A: Options: (1) Return "uncertain" to user, (2) Route to human, (3) Use a third model, (4) Provide best-effort answer with disclaimer.

**Q: Can cascades be used for generative tasks (not classification)?**
A: Yes, but confidence is harder to measure. Techniques: token-level entropy, self-consistency, or using a separate "evaluator" model.

---

**Tutorial Status:** ⏳ In Development
**Last Updated:** 2025-10-29
**Maintainer:** AI Evaluation Course Team
