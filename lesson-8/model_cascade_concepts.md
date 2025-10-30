# Model Cascade Concepts Tutorial

## Learning Objectives

- ✅ Understand model cascade architecture and when to use it
- ✅ Explain cost-accuracy trade-off fundamentals
- ✅ Use log probabilities (logprobs) for confidence-based routing
- ✅ Set optimal confidence thresholds for routing decisions
- ✅ Calculate cost savings and evaluate cascade performance
- ✅ Identify when cascades are effective vs. when they fail
- ✅ Consider latency implications for production systems

## Prerequisites

- Understanding of LLM API calls (temperature, logprobs)
- Basic probability concepts
- Cost awareness for production AI systems

## Estimated Time

**Reading Time:** 20-25 minutes

---

## Concepts

### What is a Model Cascade?

**Model cascade** is an optimization pattern where you route queries through multiple models based on difficulty, using cheap models for easy cases and expensive models for hard cases.

**The Cost Problem:**

```
Scenario: Content moderation system
- GPT-4o: $10 per 1M tokens (accurate)
- GPT-4o-mini: $0.15 per 1M tokens (mostly accurate)
- 1M queries per month

Expensive-only cost: $10,000/month
```

**The Insight:** Not all queries are hard!

```
Easy: "This is spam" → 95% confident (mini model sufficient)
Hard: "Subtle sarcasm with borderline content" → 60% confident (need expensive model)
```

**The Solution: Cascade**

```
Query → Cheap Model (GPT-4o-mini)
           ↓
     Confident? (≥90%)
           ↓
         YES → Return answer (save $)
           ↓
         NO → Expensive Model (GPT-4o) → Return answer
```

**Result:** 40-70% cost savings while maintaining accuracy

---

## Architecture Patterns

### Basic 2-Tier Cascade

```
┌──────────────────────────────────────────────────┐
│         BASIC CASCADE WORKFLOW                   │
├──────────────────────────────────────────────────┤
│                                                  │
│  Input Query                                     │
│  ↓                                               │
│  Tier 1: Cheap Model (GPT-4o-mini)              │
│  → Extract confidence from logprobs              │
│  ↓                                               │
│  Confidence ≥ Threshold? (e.g., 0.90)            │
│  ↓          ↓                                    │
│  YES       NO                                    │
│  ↓          ↓                                    │
│  Return    Tier 2: Expensive Model (GPT-4o)     │
│  Answer    → Return Answer                       │
└──────────────────────────────────────────────────┘
```

### Multi-Tier Cascade (3+ Models)

```
Input → Mini (< $0.01) → Confident?
                 ↓ No
        → Small (~$0.10) → Confident?
                 ↓ No
        → Large (~$1.00) → Return Answer
```

**When to use:**
- ✅ Clear difficulty gradation in queries
- ✅ Multiple model tiers available
- ❌ Diminishing returns after 2 tiers

---

## Log Probabilities (Logprobs)

### What are Logprobs?

**Log probability** = natural logarithm of token probability

```python
# LLM considers two tokens for binary classification
logprobs = {
    "True": -0.05,   # log(P("True"))
    "False": -3.00   # log(P("False"))
}

# Convert to probabilities
import numpy as np
prob_true = np.exp(-0.05)   # ≈ 0.9512
prob_false = np.exp(-3.00)  # ≈ 0.0498

# Normalize (ensure sum = 1)
total = prob_true + prob_false
normalized_true = prob_true / total  # ≈ 0.95
```

**Confidence = normalized probability of predicted token**

### Extracting Confidence

**API Call:**
```python
import litellm

response = litellm.completion(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": "Is this spam: ..."}],
    logprobs=True,
    top_logprobs=10,  # Get top 10 token probabilities
    max_tokens=1
)

# Access logprobs
first_token_logprobs = response.choices[0].logprobs['content'][0]
```

**Calculate Confidence:**
```python
def get_confidence(logprobs_dict, predicted_answer):
    \"\"\"Calculate normalized confidence for binary classification.\"\"\"

    # Extract probabilities for True/False
    probs = {token: np.exp(logprob) for token, logprob in logprobs_dict.items()}

    if 'True' in probs and 'False' in probs:
        true_prob = probs['True']
        false_prob = probs['False']

        # Normalize
        total = true_prob + false_prob
        answer_prob = true_prob if predicted_answer == 1 else false_prob

        return answer_prob / total

    # Fallback: max probability
    return max(probs.values())
```

---

## Confidence Thresholding

### Setting Thresholds

**Threshold Trade-off:**

| Threshold | % to Cheap | Accuracy | Cost | Use Case |
|-----------|------------|----------|------|----------|
| 0.50 | 98% | 96.5% | Very Low | Cost-critical, acceptable accuracy |
| 0.70 | 95% | 98.2% | Low | General use |
| 0.90 | 85% | 99.0% | Medium | Recommended (balanced) |
| 0.95 | 70% | 99.5% | Higher | High accuracy need |
| 0.99 | 40% | 99.9% | Highest | Near-perfect accuracy |

**Choosing Threshold:**

1. **Set Target Accuracy** (e.g., 99%)
2. **Measure cheap model accuracy** on test set
3. **If cheap = 96%, expensive = 99%:**
   - Need to route ~40% to expensive
   - Find threshold where 40% queries have confidence < threshold
4. **Validate on dev set**
5. **Measure cost savings**

### Example Calculation

**Scenario: SMS Spam Classification**

- Cheap model (mini): 97% accuracy
- Expensive model (GPT-4o): 99% accuracy
- Target: 99% accuracy
- Test set: 1000 SMS messages

**Threshold Sweep Results:**

```python
threshold = 0.90

cheap_confident = 850  # 85% have confidence ≥ 0.90
cheap_correct = 830    # 97% of 850 ≈ 825

expensive_queries = 150
expensive_correct = 149  # 99% of 150 ≈ 148

total_correct = 830 + 149 = 979
cascade_accuracy = 979 / 1000 = 97.9%
```

**Too strict! Need lower threshold:**

```python
threshold = 0.85

cheap_confident = 900
expensive_queries = 100

total_correct = (900 * 0.97) + (100 * 0.99) = 873 + 99 = 972
cascade_accuracy = 97.2%
```

**Still not 99%! Adjust threshold iteratively...**

---

## Cost Analysis

### Cost Calculation

**Pricing (example, 2024):**
- GPT-4o-mini: $0.15 per 1M input tokens
- GPT-4o: $2.50 per 1M input tokens

**Cascade Strategy (threshold = 0.90):**

```python
total_queries = 100_000
avg_tokens_per_query = 500

# Routing
cheap_queries = 85_000  # 85%
expensive_queries = 15_000  # 15%

# Costs
cheap_cost = (85_000 * 500 * $0.15) / 1_000_000 = $6.38
expensive_cost = (15_000 * 500 * $2.50) / 1_000_000 = $18.75

cascade_total = $6.38 + $18.75 = $25.13
```

**Baseline (expensive-only):**

```python
baseline_cost = (100_000 * 500 * $2.50) / 1_000_000 = $125.00
```

**Savings:**

```python
savings = $125.00 - $25.13 = $99.87
percentage = ($99.87 / $125.00) * 100 = 79.9%
```

**Cascade saves ~80% while maintaining 99% accuracy!**

---

## When Cascades Work vs. Fail

### ✅ Cascades Work Well When

**1. Clear Easy/Hard Distinction**
```
Easy: "BUY NOW!!! Click here!!!" → 99% spam (mini detects)
Hard: "Reminder: Your package delivery tomorrow" → 60% spam? (need GPT-4o)
```

**2. Cheap Model is "Good Enough" on Easy Cases**
```
Mini accuracy on high-confidence cases: ≥95%
→ Cascade routing to mini is safe
```

**3. Large Volume, Low-Latency Tolerance**
```
1M queries/month → Cost matters
Latency tolerance: 2-5 seconds → Sequential cascade acceptable
```

**4. Confidence Scores are Calibrated**
```
When mini says 95% confident, it's correct 95% of the time
→ Threshold is meaningful
```

### ❌ Cascades Fail When

**1. Cheap Model is Too Weak**
```
Mini accuracy: 70% even on "easy" cases
→ Routing to mini hurts accuracy unacceptably
```

**2. Expensive Model Isn't Much Better**
```
Mini: 92% accuracy
GPT-4o: 93% accuracy
→ Paying 16x for 1% gain (not worth it)
```

**3. Latency is Critical**
```
User needs <500ms response
Cascade adds sequential LLM calls (2-3s total)
→ Unacceptable for real-time systems
```

**4. Confidence Scores are Unreliable**
```
Model says 90% confident but is only right 70% of the time
→ Threshold routing doesn't work
```

---

## Latency Considerations

### Cascade Latency Overhead

**Sequential Cascade:**
```
Time = T_cheap + (P_uncertain * T_expensive)

Example:
T_cheap = 800ms
P_uncertain = 15%
T_expensive = 2000ms

Average latency = 800ms + (0.15 * 2000ms) = 1100ms
```

**vs. Expensive-Only:**
```
Time = T_expensive = 2000ms
```

**Cascade is faster on average!** (if most queries route to cheap)

### Parallel Cascade (Advanced)

**Call both models simultaneously:**
```python
from concurrent.futures import ThreadPoolExecutor

with ThreadPoolExecutor(max_workers=2) as executor:
    cheap_future = executor.submit(call_cheap_model, query)
    expensive_future = executor.submit(call_expensive_model, query)

    cheap_result = cheap_future.result()

    if cheap_result.confidence >= 0.90:
        expensive_future.cancel()  # Stop if possible
        return cheap_result
    else:
        return expensive_future.result()
```

**Trade-off:**
- ✅ Lower latency (no sequential waiting)
- ❌ Higher cost (both models always called)
- ❌ More complex (cancellation not always possible)

---

## Key Takeaways

- ✅ **Cascades save 40-80% cost** while maintaining target accuracy
- ✅ **Logprobs provide confidence scores** for routing decisions
- ✅ **Threshold tuning is critical** - Test on dev set iteratively
- ✅ **Works when cheap model handles most cases well** (80%+ with high confidence)
- ✅ **Sequential cascades can reduce latency** (vs. expensive-only)
- ✅ **Not a silver bullet** - Requires calibrated models and clear easy/hard split

**When to use:**
- Production systems with high query volume
- Cost is a concern (millions of queries)
- Clear accuracy target (e.g., 99%)
- Mix of easy and hard queries

**When to avoid:**
- Real-time systems (<500ms latency requirement)
- Cheap model is too weak
- Expensive model isn't much better

---

## Further Reading

- [Spam Classification Tutorial](spam_classification_tutorial.ipynb) - Hands-on cascade implementation
- [Cascade Decision Tree Diagram](diagrams/cascade_decision_tree.mmd) - Visual routing logic
- [Lesson 8 Tutorial Index](TUTORIAL_INDEX.md) - Complete learning path

---

**Tutorial Status:** ✅ Complete
**Last Updated:** 2025-10-30
**Maintainer:** AI Evaluation Course Team
