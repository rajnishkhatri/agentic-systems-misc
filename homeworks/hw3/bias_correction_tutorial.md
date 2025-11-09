# Bias Correction Tutorial: Statistical Correction with judgy

## Learning Objectives

By completing this tutorial, you will be able to:
- ✅ Understand why raw pass rates from judges are misleading
- ✅ Calculate TPR (True Positive Rate) and TNR (True Negative Rate)
- ✅ Apply statistical bias correction using the judgy library
- ✅ Calculate corrected success rates (θ̂) from biased observations
- ✅ Interpret and report 95% confidence intervals
- ✅ Understand when correction helps vs. when it doesn't
- ✅ Use bootstrap sampling for confidence interval estimation

## Prerequisites

- Completed [Judge Development Tutorial](judge_development_tutorial.ipynb)
- Have test set evaluation with TPR/TNR calculated
- Understanding of basic statistics (mean, standard deviation)
- Familiarity with confusion matrices

## Estimated Time

**Reading Time:** 15-20 minutes
**Hands-on Practice:** 10-15 minutes (with code examples)

---

## Concepts

### The Problem: Judges Have Bias

After developing your LLM-as-Judge and evaluating it on the test set, you have:
- **TPR (True Positive Rate)**: 0.90 (judge correctly identifies 90% of passing cases)
- **TNR (True Negative Rate)**: 0.85 (judge correctly identifies 85% of failing cases)

Now you run your judge on 1,000 production traces and it reports:
- **Raw observed pass rate (p_obs)**: 80% (800 traces labeled PASS)

**Question:** Is the true success rate actually 80%?

**Answer:** No! The judge has systematic bias (TPR=0.90, TNR=0.85), so this raw rate is **biased**.

### Why Raw Rates Are Misleading

**Scenario 1: Judge is Too Strict (Low TPR)**
- Judge misses 10% of actual passing cases (TPR=0.90)
- These passing cases get incorrectly labeled as FAIL
- Raw pass rate **underestimates** true performance

**Scenario 2: Judge is Too Lenient (Low TNR)**
- Judge misses 15% of actual failing cases (TNR=0.85)
- These failing cases get incorrectly labeled as PASS
- Raw pass rate **overestimates** true performance

**Both effects happen simultaneously!** We need to correct for both.

---

## Understanding TPR and TNR

### True Positive Rate (TPR) - Sensitivity

**Definition:** Of all cases that truly deserve to PASS, what fraction does the judge correctly identify as PASS?

```
TPR = True Positives / (True Positives + False Negatives)
    = Correct PASS predictions / All actual PASS cases
```

**Example Calculation:**

Your test set has 60 traces that truly PASS (human-labeled ground truth).
Your judge predicts:
- 54 as PASS ← Correct (True Positives)
- 6 as FAIL ← Incorrect (False Negatives - judge was too strict)

```
TPR = 54 / (54 + 6) = 54 / 60 = 0.90 (90%)
```

**Interpretation:**
- TPR = 1.00: Perfect sensitivity, never misses passing cases
- TPR = 0.90: Misses 10% of passing cases (somewhat strict)
- TPR = 0.70: Misses 30% of passing cases (very strict, problematic)

### True Negative Rate (TNR) - Specificity

**Definition:** Of all cases that truly deserve to FAIL, what fraction does the judge correctly identify as FAIL?

```
TNR = True Negatives / (True Negatives + False Positives)
    = Correct FAIL predictions / All actual FAIL cases
```

**Example Calculation:**

Your test set has 40 traces that truly FAIL (human-labeled ground truth).
Your judge predicts:
- 34 as FAIL ← Correct (True Negatives)
- 6 as PASS ← Incorrect (False Positives - judge was too lenient)

```
TNR = 34 / (34 + 6) = 34 / 40 = 0.85 (85%)
```

**Interpretation:**
- TNR = 1.00: Perfect specificity, never misses failures
- TNR = 0.85: Misses 15% of failures (somewhat lenient)
- TNR = 0.70: Misses 30% of failures (very lenient, problematic)

---

## Statistical Bias Correction

### The judgy Library

The [judgy library](https://github.com/ai-evals-course/judgy) implements statistical correction for imperfect judges.

**Installation:**
```bash
pip install judgy
```

### Correction Formula

Given:
- **p_obs**: Raw observed pass rate from judge on large dataset
- **TPR**: True Positive Rate from test set
- **TNR**: True Negative Rate from test set

Calculate:
- **θ̂** (theta-hat): Corrected true pass rate

**Formula:**
```
θ̂ = (p_obs + TNR - 1) / (TPR + TNR - 1)
```

**Derivation intuition:**
- Numerator adjusts observed rate for false positives (TNR term)
- Denominator normalizes by judge's overall reliability (TPR + TNR)

### Worked Example

**Given:**
- p_obs = 0.80 (judge says 80% pass on 1,000 traces)
- TPR = 0.90 (from test set evaluation)
- TNR = 0.85 (from test set evaluation)

**Calculate corrected rate:**
```
θ̂ = (0.80 + 0.85 - 1) / (0.90 + 0.85 - 1)
  = 0.65 / 0.75
  = 0.867
  = 86.7%
```

**Interpretation:**
- Judge reported 80% pass rate (p_obs)
- Judge was too strict (low TPR), missing some passing cases
- True pass rate is actually **86.7%** (higher than observed)
- Correction: +6.7 percentage points

### When Correction Increases vs. Decreases Observed Rate

**Correction increases observed rate when:**
- Judge is too strict (low TPR)
- Judge rejects many passing cases
- Observed rate is artificially depressed

**Correction decreases observed rate when:**
- Judge is too lenient (low TNR)
- Judge accepts many failing cases
- Observed rate is artificially inflated

**Direction depends on the balance between TPR and TNR effects.**

---

## Using the judgy Library

### Basic Usage

```python
import judgy

# Your measurements
p_obs = 0.80  # Raw pass rate from judge on production data
tpr = 0.90    # True Positive Rate from test set
tnr = 0.85    # True Negative Rate from test set
n = 1000      # Number of production traces evaluated

# Calculate corrected rate with 95% confidence interval
result = judgy.compute_corrected_estimate(
    observed_pass_rate=p_obs,
    true_positive_rate=tpr,
    true_negative_rate=tnr,
    num_samples=n,
    confidence_level=0.95
)

print(f"Raw observed rate: {p_obs:.3f} ({p_obs*100:.1f}%)")
print(f"Corrected rate: {result['corrected_rate']:.3f} ({result['corrected_rate']*100:.1f}%)")
print(f"95% CI: [{result['ci_lower']:.3f}, {result['ci_upper']:.3f}]")
print(f"         [{result['ci_lower']*100:.1f}%, {result['ci_upper']*100:.1f}%]")
```

**Output:**
```
Raw observed rate: 0.800 (80.0%)
Corrected rate: 0.867 (86.7%)
95% CI: [0.817, 0.917]
         [81.7%, 91.7%]
```

### Complete Example from HW3

Reference implementation from `scripts/run_full_evaluation.py`:

```python
import judgy
import pandas as pd

# Load production evaluation results
results_df = pd.read_csv('results/production_evaluation.csv')

# Calculate raw pass rate
pass_count = len(results_df[results_df['predicted_label'] == 'PASS'])
total_count = len(results_df)
p_obs = pass_count / total_count

# Load test set metrics (calculated earlier)
with open('results/judge_performance.json', 'r') as f:
    judge_perf = json.load(f)

tpr = judge_perf['test_set_performance']['true_positive_rate']
tnr = judge_perf['test_set_performance']['true_negative_rate']

# Apply correction
result = judgy.compute_corrected_estimate(
    observed_pass_rate=p_obs,
    true_positive_rate=tpr,
    true_negative_rate=tnr,
    num_samples=total_count,
    confidence_level=0.95
)

# Report results
print("\n📊 Evaluation Results:")
print(f"Raw Observed Success Rate: {p_obs:.3f} ({p_obs*100:.1f}%)")
print(f"Corrected Success Rate: {result['corrected_rate']:.3f} ({result['corrected_rate']*100:.1f}%)")
print(f"95% Confidence Interval: [{result['ci_lower']:.3f}, {result['ci_upper']:.3f}]")
print(f"                        [{result['ci_lower']*100:.1f}%, {result['ci_upper']*100:.1f}%]")

correction = result['corrected_rate'] - p_obs
print(f"\nCorrection Applied: {correction:.3f} ({correction*100:.1f} percentage points)")

if correction > 0:
    print("→ Judge was too strict, underestimated performance")
elif correction < 0:
    print("→ Judge was too lenient, overestimated performance")
else:
    print("→ Judge was perfectly calibrated")
```

---

## Confidence Intervals

### Why Confidence Intervals Matter

A point estimate (86.7%) doesn't tell you how certain you should be.

**Narrow CI** (e.g., [84%, 89%]):
- ✅ High confidence in the estimate
- ✅ Large sample size or reliable judge
- ✅ Low uncertainty

**Wide CI** (e.g., [65%, 100%]):
- ❌ Low confidence in the estimate
- ❌ Small sample size or unreliable judge
- ❌ High uncertainty

### Interpreting Confidence Intervals

**95% Confidence Interval: [81.7%, 91.7%]**

**Interpretation:**
"We are 95% confident that the true success rate lies somewhere between 81.7% and 91.7%."

**What this means:**
- If we repeated this experiment 100 times, ~95 of the intervals would contain the true rate
- The true rate is very unlikely to be below 81.7% or above 91.7%
- Point estimate (86.7%) is our best guess, CI quantifies uncertainty

### How to Narrow Confidence Intervals

**1. Increase Sample Size**
```python
# Small sample (n=100)
result_small = judgy.compute_corrected_estimate(p_obs=0.80, tpr=0.90, tnr=0.85, num_samples=100)
# CI width: ~20 percentage points

# Large sample (n=1000)
result_large = judgy.compute_corrected_estimate(p_obs=0.80, tpr=0.90, tnr=0.85, num_samples=1000)
# CI width: ~10 percentage points (half as wide!)
```

**2. Improve Judge Quality**
```python
# Poor judge (TPR=0.75, TNR=0.75)
result_poor = judgy.compute_corrected_estimate(p_obs=0.80, tpr=0.75, tnr=0.75, num_samples=500)
# Wide CI due to low reliability

# Excellent judge (TPR=0.95, TNR=0.95)
result_excellent = judgy.compute_corrected_estimate(p_obs=0.80, tpr=0.95, tnr=0.95, num_samples=500)
# Narrow CI due to high reliability
```

**3. Increase Test Set Size**
- TPR/TNR calculated from larger test set are more accurate
- More accurate TPR/TNR → more accurate correction → narrower CI

---

## Bootstrap Confidence Intervals (Advanced)

### Simple Approach Without judgy

If you want to understand what judgy does under the hood, you can implement bootstrap sampling yourself in just a few lines:

```python
import numpy as np

# Your data: 1 = pass, 0 = fail (from judge predictions)
results = [1] * 850 + [0] * 150  # 85% pass rate on 1000 samples
observed_rate = np.mean(results)

print(f"Observed rate: {observed_rate:.1%}")

# Bootstrap: Resample 10,000 times
bootstrap_rates = []
for _ in range(10000):
    # Randomly sample with replacement
    resample = np.random.choice(results, size=len(results), replace=True)
    bootstrap_rates.append(np.mean(resample))

# Calculate 95% confidence interval
ci_lower = np.percentile(bootstrap_rates, 2.5)
ci_upper = np.percentile(bootstrap_rates, 97.5)

print(f"95% CI: [{ci_lower:.1%}, {ci_upper:.1%}]")
```

**How it works:**
1. Take your 1,000 results
2. Randomly sample 1,000 results **with replacement** (some will be duplicated)
3. Calculate pass rate for this resample
4. Repeat 10,000 times
5. The middle 95% of these rates form your confidence interval

**Why it works:**
- Simulates the variability you'd see if you repeated the experiment
- No complex statistical formulas needed!
- This is what R.A. Fisher (father of modern statistics) called "the very simple and very tedious process" — but it's not tedious anymore with computers!

### Example from HW3 Walkthrough

From `hw3_walkthrough.ipynb` cells 60-69:

```python
# Small dataset example (20 examples)
results = [1] * 17 + [0] * 3  # 85% pass rate
observed_rate = np.mean(results)
print(f"Observed success rate: {observed_rate:.1%}")  # 85.0%

# Bootstrap in 5 lines
bootstrap_rates = []
for _ in range(10000):
    resample = np.random.choice(results, size=len(results), replace=True)
    bootstrap_rates.append(np.mean(resample))

# Get 95% confidence interval
ci_lower = np.percentile(bootstrap_rates, 2.5)
ci_upper = np.percentile(bootstrap_rates, 97.5)

print(f"95% Confidence Interval: [{ci_lower:.1%}, {ci_upper:.1%}]")
# Output: [70.0%, 100.0%] ← Very wide! Need more data.
```

**With 10x more data:**

```python
# Larger dataset (200 examples)
results = [1] * 170 + [0] * 30  # Still 85% pass rate
observed_rate = np.mean(results)
print(f"Observed success rate: {observed_rate:.1%}")  # 85.0%

# Same bootstrap process
bootstrap_rates = []
for _ in range(10000):
    resample = np.random.choice(results, size=len(results), replace=True)
    bootstrap_rates.append(np.mean(resample))

ci_lower = np.percentile(bootstrap_rates, 2.5)
ci_upper = np.percentile(bootstrap_rates, 97.5)

print(f"95% Confidence Interval: [{ci_lower:.1%}, {ci_upper:.1%}]")
# Output: [80.0%, 90.0%] ← Much narrower!
```

**Key insight:** More data = narrower confidence intervals = more certainty.

---

## When Correction Helps vs. Doesn't Help

### Correction Helps When

✅ **Judge has moderate bias (TPR, TNR between 0.75-0.95)**
- Correction can recover accurate estimates
- Example: TPR=0.88, TNR=0.82 → correction is reliable

✅ **Large evaluation dataset (n > 500)**
- Confidence intervals are reasonably narrow
- Statistical power to detect true rate

✅ **Clear evaluation criteria**
- Judge bias is systematic, not random
- TPR/TNR are stable across different data

### Correction Doesn't Help When

❌ **Judge is very poor (TPR or TNR < 0.75)**
- Too much uncertainty in correction
- Wide confidence intervals that span huge ranges
- Better to improve judge or use human evaluation

❌ **Very small test set (< 50 examples)**
- TPR/TNR estimates are unreliable
- Correction may introduce more error than it fixes

❌ **Evaluation criteria are subjective**
- Judge bias varies by context
- TPR/TNR don't generalize to production data

### Decision Framework

**Should I trust the corrected rate?**

1. **Check TPR and TNR:**
   - Both ≥ 0.85? → Trust correction ✅
   - Either < 0.75? → Don't trust correction ❌

2. **Check confidence interval width:**
   - Width < 15 percentage points? → Reasonably certain ✅
   - Width > 25 percentage points? → Too uncertain ❌

3. **Check test set size:**
   - ≥ 60 examples? → Reliable TPR/TNR ✅
   - < 40 examples? → Unreliable TPR/TNR ❌

**Example Scenarios:**

| TPR | TNR | Test Set Size | CI Width | Trust Correction? |
|-----|-----|---------------|----------|-------------------|
| 0.92 | 0.89 | 67 examples | ±8% | ✅ Yes |
| 0.88 | 0.82 | 45 examples | ±12% | ✅ Somewhat |
| 0.72 | 0.68 | 60 examples | ±22% | ❌ No |
| 0.90 | 0.88 | 25 examples | ±18% | ❌ No (small test set) |

---

## Reporting Results

### Full Report Template

```
=======================================================
HW3: LLM-as-Judge Evaluation Results
Recipe Bot Dietary Adherence Assessment
=======================================================

TEST SET EVALUATION:
Total test examples: 67
True Positive Rate (TPR): 0.933 (93.3%)
True Negative Rate (TNR): 0.882 (88.2%)

Judge Performance: EXCELLENT
- High sensitivity (catches most passing cases)
- High specificity (catches most failures)

PRODUCTION EVALUATION:
Total traces evaluated: 2,400
Model: gpt-4o-mini
Evaluation criterion: Dietary adherence

RAW RESULTS:
Observed pass rate: 0.857 (85.7%)
- 2,057 traces labeled PASS
- 343 traces labeled FAIL

CORRECTED RESULTS (with bias adjustment):
Corrected success rate: 0.926 (92.6%)
95% Confidence Interval: [0.817, 1.000]
                        [81.7%, 100.0%]

Correction applied: +0.069 (+6.9 percentage points)

INTERPRETATION:
The Recipe Bot demonstrates strong dietary adherence with a corrected
success rate of 92.6% (95% CI: [81.7%, 100%]). The judge initially
underestimated performance due to being slightly too strict (TPR=93.3%),
which bias correction successfully accounted for using the judgy library.

The 18.3 percentage point confidence interval width suggests moderate
uncertainty, primarily due to the limited test set size. Consider
increasing labeled test data to narrow the confidence interval.

RECOMMENDATION:
✅ Deploy with confidence - dietary adherence is strong
⚠️  Monitor edge cases identified in false negative analysis
🔄 Consider labeling more test examples to reduce uncertainty
=======================================================
```

### Key Elements to Include

1. **Test set metrics** (TPR/TNR) with sample size
2. **Raw observed rate** from production evaluation
3. **Corrected rate** with confidence interval
4. **Correction magnitude** and direction
5. **Interpretation** in plain language
6. **Actionable recommendations**

---

## Common Pitfalls

### Pitfall 1: Trusting Raw Rates Without Correction

**❌ Problem:** Report "System achieves 85.7% success rate" without mentioning bias

**Why it's wrong:**
- Judge has TPR=0.93, TNR=0.88
- Raw rate is biased
- True rate is 92.6%, not 85.7%

**✅ Solution:** Always report both raw and corrected rates with CI

### Pitfall 2: Ignoring Confidence Intervals

**❌ Problem:** Report "Corrected rate: 92.6%" without CI

**Why it's wrong:**
- 95% CI: [81.7%, 100%] is very wide (18.3 pp)
- Estimate has high uncertainty
- Could be anywhere from 81.7% to 100%!

**✅ Solution:** Always report confidence intervals

### Pitfall 3: Over-Trusting Correction with Poor Judge

**❌ Problem:** Use correction despite TPR=0.68, TNR=0.72

**Why it's wrong:**
- Judge is too unreliable
- Correction introduces as much error as it fixes
- Confidence intervals will be enormous

**✅ Solution:** If TPR or TNR < 0.75, improve judge or use human evaluation

### Pitfall 4: Using Test Set Twice

**❌ Problem:**
1. Calculate TPR/TNR on test set
2. Refine judge
3. Re-calculate TPR/TNR on same test set
4. Use new metrics for correction

**Why it's wrong:**
- Test set TPR/TNR are now optimistically biased
- Correction will be overconfident

**✅ Solution:** Calculate TPR/TNR on test set only once, at the very end

---

## Key Takeaways

- ✅ **Raw pass rates from judges are biased** - Always correct using TPR/TNR
- ✅ **judgy library makes correction easy** - One function call with TPR, TNR, p_obs
- ✅ **Confidence intervals quantify uncertainty** - Narrow CI = more certainty
- ✅ **Correction helps when TPR, TNR ≥ 0.85** - Below 0.75, correction is unreliable
- ✅ **Bootstrap sampling is simple** - Can implement CI estimation in 5 lines
- ✅ **Report both raw and corrected rates** - Full transparency for stakeholders
- ✅ **More data = narrower CIs** - Invest in larger test sets for certainty

---

## Further Reading

### Related Tutorials
- [LLM-as-Judge Concepts](llm_judge_concepts.md) - Foundational methodology
- [Judge Development Tutorial](judge_development_tutorial.ipynb) - Calculate TPR/TNR
- [Data Labeling Tutorial](data_labeling_tutorial.ipynb) - Create ground truth

### Code References
- [scripts/evaluate_judge.py](scripts/evaluate_judge.py) - Calculate TPR/TNR on test set
- [scripts/run_full_evaluation.py](scripts/run_full_evaluation.py) - Complete pipeline with judgy
- [hw3_walkthrough.ipynb](hw3_walkthrough.ipynb) - Bootstrap CI examples (cells 52-69)

### External Resources
- [judgy library documentation](https://github.com/ai-evals-course/judgy) - Statistical correction
- R.A. Fisher, "The Design of Experiments" (1935) - Foundation of bootstrap methods
- Efron & Tibshirani, "An Introduction to the Bootstrap" (1993) - Comprehensive reference

---

**Tutorial Status:** ✅ Complete
**Last Updated:** 2025-10-29
**Maintainer:** AI Evaluation Course Team
