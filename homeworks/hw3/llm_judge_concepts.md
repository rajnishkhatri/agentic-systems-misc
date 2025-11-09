# LLM-as-Judge Concepts Tutorial

## Learning Objectives

By completing this tutorial, you will be able to:
- ✅ Understand the LLM-as-Judge paradigm and when it provides value
- ✅ Identify scenarios where automated evaluation is appropriate vs. human evaluation
- ✅ Recognize bias considerations: judge alignment and systematic errors
- ✅ Design effective ground truth creation strategies
- ✅ Evaluate cost-accuracy trade-offs in judge model selection
- ✅ Understand calibration requirements and confidence intervals
- ✅ Apply LLM-as-Judge methodology to real evaluation tasks

## Prerequisites

- Completed [HW2: Error Analysis](../hw2/error_analysis_concepts.md)
- Familiarity with failure taxonomies and qualitative evaluation
- Basic understanding of classification metrics (precision, recall)
- Experience with LLM API calls and prompt engineering

## Estimated Time

**Reading Time:** 20-25 minutes
**Hands-on Practice:** 30-45 minutes (when applying to your own system)

---

## Concepts

### Why LLM-as-Judge?

After performing error analysis (HW2) and identifying failure modes, you face a scaling problem:

**The Manual Evaluation Bottleneck:**
- 👤 1 human can label ~50-100 examples/hour
- 📊 You need 1000s of evaluations for statistical confidence
- 💰 Manual labeling is expensive ($20-50/hour)
- 🔄 Re-evaluation after each system change is tedious
- 📈 Production monitoring requires continuous evaluation

**Manual evaluation doesn't scale.** But what if you could use an LLM to evaluate another LLM?

### What is LLM-as-Judge?

**LLM-as-Judge** is an evaluation methodology where you use a high-quality LLM to automatically evaluate specific properties of AI system outputs.

```
┌──────────────────────────────────────────────────────┐
│           LLM-AS-JUDGE WORKFLOW                      │
├──────────────────────────────────────────────────────┤
│                                                      │
│  AI System (being evaluated)                         │
│  ↓                                                   │
│  Generates output (e.g., recipe, response)           │
│  ↓                                                   │
│  Judge LLM (with evaluation prompt)                  │
│  ↓                                                   │
│  Evaluates: PASS or FAIL + reasoning                 │
│  ↓                                                   │
│  Statistical correction (using TPR/TNR)              │
│  ↓                                                   │
│  True success rate with confidence interval          │
└──────────────────────────────────────────────────────┘
```

**Key Insight:** Judges aren't perfect! They have systematic bias:
- **False Positives**: Saying PASS when it's actually FAIL (too lenient)
- **False Negatives**: Saying FAIL when it's actually PASS (too strict)

But we can **measure and correct** this bias using statistics.

---

## When to Use LLM-as-Judge

### ✅ Good Use Cases

**1. Clear, Objective Criteria**
- ✅ Dietary restriction adherence (vegan recipe contains no animal products)
- ✅ Format compliance (response contains required sections)
- ✅ Factual accuracy with grounded context (answer is supported by retrieved documents)
- ✅ Constraint adherence (recipe takes <30 minutes as requested)

**Why it works:** The evaluation criterion is testable and has clear pass/fail boundaries.

**2. Large-Scale Evaluation Needs**
- ✅ Evaluating 1000s of production traces
- ✅ Continuous monitoring in production
- ✅ A/B testing different system versions
- ✅ Regression testing after system changes

**Why it works:** Cost per evaluation is ~$0.001-0.01, enabling large-scale analysis.

**3. Repeatable, Consistent Judgments Required**
- ✅ Comparing system performance across time
- ✅ Tracking metrics over multiple deployments
- ✅ Establishing performance baselines

**Why it works:** Judges are perfectly consistent (same input → same output with temperature=0).

### ❌ When to Avoid LLM-as-Judge

**1. Highly Subjective Criteria**
- ❌ "Response is engaging" (what defines engaging?)
- ❌ "Recipe sounds delicious" (personal preference)
- ❌ "Tone is friendly" (subjective interpretation)

**Problem:** No clear ground truth, judges will be inconsistent and unreliable.

**2. Safety-Critical Applications**
- ❌ Medical diagnoses
- ❌ Legal advice
- ❌ Financial recommendations

**Problem:** Even small error rates are unacceptable. Use human expert review.

**3. Very Small Datasets**
- ❌ <50 labeled examples
- ❌ Insufficient data to measure TPR/TNR reliably

**Problem:** Can't estimate judge bias accurately, correction will be unreliable.

**4. Domain-Specific Expertise Required**
- ❌ Evaluating advanced mathematics proofs
- ❌ Medical image interpretation
- ❌ Specialized legal compliance

**Problem:** Current LLMs lack deep domain expertise for reliable judgments.

---

## The Complete LLM-as-Judge Pipeline

```
┌─────────────────────────────────────────────────────┐
│     PHASE 1: GROUND TRUTH CREATION                  │
├─────────────────────────────────────────────────────┤
│                                                     │
│  1. Generate/Collect Traces                         │
│     → Run your AI system on diverse test queries    │
│     → Collect inputs and outputs                    │
│                                                     │
│  2. Define Evaluation Criterion                     │
│     → Write clear PASS/FAIL definitions             │
│     → Document edge cases                           │
│                                                     │
│  3. Manually Label Subset                           │
│     → Label 150-200 examples (ground truth)         │
│     → Ensure high-quality, consistent labels        │
│     → Use best available LLM or domain expert       │
│                                                     │
│  4. Split Data                                      │
│     → Train: 15% (few-shot examples)                │
│     → Dev: 40% (iterative refinement)               │
│     → Test: 45% (final evaluation)                  │
└─────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────┐
│     PHASE 2: JUDGE DEVELOPMENT                      │
├─────────────────────────────────────────────────────┤
│                                                     │
│  5. Develop Judge Prompt                            │
│     → Write clear task description                  │
│     → Add PASS/FAIL definitions                     │
│     → Include 2-5 few-shot examples from Train      │
│     → Specify structured output format (JSON)       │
│                                                     │
│  6. Test on Dev Set                                 │
│     → Run judge on Dev set examples                 │
│     → Calculate accuracy                            │
│     → Analyze errors (false positives/negatives)    │
│                                                     │
│  7. Iterate on Prompt                               │
│     → Clarify definitions based on errors           │
│     → Add edge case examples                        │
│     → Adjust reasoning requirements                 │
│     → Re-test on Dev set                            │
│     → Repeat until satisfactory performance         │
└─────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────┐
│     PHASE 3: FINAL EVALUATION                       │
├─────────────────────────────────────────────────────┤
│                                                     │
│  8. Evaluate on Test Set                            │
│     → Run finalized judge on Test set (ONCE)        │
│     → Calculate TPR (True Positive Rate)            │
│     → Calculate TNR (True Negative Rate)            │
│     → These measure judge bias                      │
│                                                     │
│  9. Apply to Large Dataset                          │
│     → Run judge on 1000s of unlabeled examples      │
│     → Get raw observed pass rate (p_obs)            │
│                                                     │
│  10. Statistical Bias Correction                    │
│      → Use TPR/TNR to correct p_obs                 │
│      → Calculate true pass rate (θ̂)                 │
│      → Compute 95% confidence interval              │
│      → Report corrected results                     │
└─────────────────────────────────────────────────────┘
```

---

## Ground Truth Creation Strategies

### Strategy 1: Manual Labeling by Domain Expert

**Best for:** Safety-critical applications, complex evaluation criteria

**Process:**
1. Domain expert (e.g., nutritionist for dietary evaluation) labels examples
2. Clear labeling guidelines with edge case documentation
3. Multiple experts for inter-annotator agreement validation
4. Review and discuss disagreements

**Pros:**
- ✅ Highest quality ground truth
- ✅ Captures nuanced edge cases
- ✅ Builds deep understanding of failure modes

**Cons:**
- ❌ Expensive ($50-150/hour)
- ❌ Slow (50-100 examples/hour)
- ❌ Requires finding and scheduling experts

### Strategy 2: Automated Labeling with High-Quality LLM

**Best for:** Clear criteria, rapid iteration, cost constraints

**Process:**
1. Use GPT-4o, Claude Sonnet, or similar high-quality model
2. Provide extremely clear labeling criteria
3. **Critically important:** Manually review and correct all labels
4. Spot-check for systematic labeling errors

**Pros:**
- ✅ Fast (100s of examples/hour)
- ✅ Inexpensive (~$0.01-0.05 per label)
- ✅ Consistent application of criteria
- ✅ Good for clear, objective criteria

**Cons:**
- ❌ May miss subtle edge cases
- ❌ Can have systematic biases
- ❌ Still requires manual validation

**⚠️ Critical Warning:**
Using an LLM to create ground truth for training an LLM-as-Judge is essentially using an LLM judge already. You must:
- Use a much higher-quality model for ground truth than for judging
- Manually review at least 30-50% of automated labels
- Validate that labeling criteria are consistently applied

### Strategy 3: Hybrid Approach (Recommended)

**Best for:** Most real-world applications

**Process:**
1. Use high-quality LLM for initial labeling
2. Human expert reviews all labels
3. Expert corrects errors and documents reasoning
4. Build labeling guidelines from disagreements
5. Re-label if systematic issues found

**Pros:**
- ✅ High quality (human-reviewed)
- ✅ Faster than pure manual (LLM does first pass)
- ✅ Builds understanding through review
- ✅ Reasonable cost

---

## Judge Model Selection: Cost vs. Accuracy Trade-offs

### Model Comparison for Judging

| Model | Cost per 1K evals | Typical TPR/TNR | Speed | Best For |
|-------|-------------------|-----------------|-------|----------|
| **GPT-4o** | $0.50-1.50 | 0.90-0.95 | Slow | High-stakes, complex criteria |
| **Claude Sonnet** | $0.30-1.00 | 0.88-0.93 | Medium | Balanced performance |
| **GPT-4o-mini** | $0.01-0.05 | 0.82-0.88 | Fast | Simple criteria, high volume |
| **Claude Haiku** | $0.01-0.03 | 0.80-0.86 | Fast | Clear criteria, cost-sensitive |

**Selection Guidelines:**

**Use premium models (GPT-4o, Claude Sonnet) when:**
- ✅ Evaluation criteria are complex or nuanced
- ✅ False positives/negatives have high business cost
- ✅ Evaluating <1000 examples (cost is manageable)
- ✅ Need maximum accuracy (TPR/TNR >0.90)

**Use mini/fast models (GPT-4o-mini, Haiku) when:**
- ✅ Evaluation criteria are simple and objective
- ✅ Evaluating 10,000+ examples (cost matters)
- ✅ Can tolerate TPR/TNR ~0.85
- ✅ Statistical correction will adjust for bias anyway

**Trade-off Example:**

Evaluating 10,000 Recipe Bot traces for dietary adherence:
- **GPT-4o**: $10, TPR=0.93, TNR=0.91, corrected θ̂ uncertainty: ±3%
- **GPT-4o-mini**: $0.30, TPR=0.85, TNR=0.83, corrected θ̂ uncertainty: ±5%

**Decision:** If ±5% uncertainty is acceptable, GPT-4o-mini saves $9.70 (97% cost reduction).

---

## Bias Considerations

### Understanding Judge Bias

**All judges have bias.** Even humans disagree on subjective evaluations. The key is:
1. **Measure bias** (TPR and TNR on labeled test set)
2. **Correct bias** (statistical adjustment using judgy library)
3. **Report uncertainty** (95% confidence intervals)

### Types of Judge Bias

**1. Leniency Bias (Low TNR)**
- Judge passes responses that should fail
- False positive rate is high
- **Example:** Judge says "Close enough!" to vegan recipe with honey
- **Impact:** Overestimates system performance

**2. Strictness Bias (Low TPR)**
- Judge fails responses that should pass
- False negative rate is high
- **Example:** Judge rejects vegan recipe because "nutritional yeast might confuse users"
- **Impact:** Underestimates system performance

**3. Systematic Pattern Errors**
- Judge consistently mishandles specific edge cases
- **Example:** Always misses hidden gluten in soy sauce
- **Impact:** Creates blind spots in evaluation

### Measuring Bias: TPR and TNR

**True Positive Rate (TPR) - Sensitivity**
```
TPR = True Positives / (True Positives + False Negatives)
    = Correct PASS labels / All actual PASS cases
```

**Example:**
- 60 recipes that truly adhere to dietary restrictions
- Judge correctly identifies 54 as PASS
- TPR = 54/60 = 0.90 (90%)

**Interpretation:**
- TPR = 1.00: Judge never misses passing cases (perfect sensitivity)
- TPR = 0.90: Judge misses 10% of passing cases (somewhat strict)
- TPR = 0.70: Judge misses 30% of passing cases (very strict)

**True Negative Rate (TNR) - Specificity**
```
TNR = True Negatives / (True Negatives + False Positives)
    = Correct FAIL labels / All actual FAIL cases
```

**Example:**
- 40 recipes that violate dietary restrictions
- Judge correctly identifies 36 as FAIL
- TNR = 36/40 = 0.90 (90%)

**Interpretation:**
- TNR = 1.00: Judge never misses failures (perfect specificity)
- TNR = 0.90: Judge misses 10% of failures (somewhat lenient)
- TNR = 0.70: Judge misses 30% of failures (very lenient)

### Acceptable TPR/TNR Thresholds

**Minimum Acceptable (with correction):**
- TPR ≥ 0.75 and TNR ≥ 0.75
- Below this, correction becomes unreliable

**Good Performance:**
- TPR ≥ 0.85 and TNR ≥ 0.85
- Suitable for most production use cases

**Excellent Performance:**
- TPR ≥ 0.90 and TNR ≥ 0.90
- High confidence in corrected results

**If TPR or TNR < 0.75:**
- ❌ Rethink evaluation criterion (too subjective?)
- ❌ Refine judge prompt with better examples
- ❌ Consider if LLM-as-Judge is appropriate for this task
- ❌ Use a higher-quality judge model

---

## Calibration and Confidence Intervals

### Why Calibration Matters

Your judge reports a raw pass rate (p_obs) on a large dataset. But this is **biased**:

**Scenario:**
- Judge has TPR=0.90, TNR=0.85
- Judge reports 80% pass rate on 1000 traces

**Question:** What's the **true** pass rate?

**Answer:** We need to correct for judge bias using statistical methods.

### Statistical Correction Formula

The `judgy` library uses this formula to compute corrected pass rate (θ̂):

```
θ̂ = (p_obs + TNR - 1) / (TPR + TNR - 1)
```

Where:
- **p_obs**: Raw observed pass rate from judge
- **TPR**: True Positive Rate from test set
- **TNR**: True Negative Rate from test set
- **θ̂**: Corrected true pass rate

**Example Calculation:**
- p_obs = 0.80 (judge says 80% pass)
- TPR = 0.90 (judge correctly identifies 90% of passing cases)
- TNR = 0.85 (judge correctly identifies 85% of failing cases)

```
θ̂ = (0.80 + 0.85 - 1) / (0.90 + 0.85 - 1)
  = 0.65 / 0.75
  = 0.867 (86.7% true pass rate)
```

**Interpretation:** Judge was too strict (low TPR), causing underestimation. True pass rate is higher.

### Confidence Intervals

A point estimate (86.7%) isn't enough. We need **uncertainty quantification**:

**95% Confidence Interval**: We are 95% confident the true pass rate is in this range.

**Example:** [81.2%, 92.1%]

**Interpretation:**
- **Narrow CI** (±5%): High confidence, judge is reliable or test set is large
- **Wide CI** (±15%): Low confidence, need more labeled data or better judge

**How to improve CI width:**
- ✅ Increase test set size (more labeled examples)
- ✅ Improve TPR/TNR (better judge prompt)
- ✅ Balance PASS/FAIL ratio in test set

---

## Common Pitfalls

### Ground Truth Creation Pitfalls

#### 1. Using LLM Labels Without Manual Review
**❌ Problem:** Trust automated labels completely

**Example:**
- Use GPT-4o to label 200 examples
- Never manually review any labels
- Discover judge has 60% accuracy (TPR=0.60)

**Why it happens:** Automated labeler had systematic errors that propagated to ground truth.

**✅ Solution:** Always manually review at least 30-50% of automated labels. Look for systematic errors.

#### 2. Insufficient Labeled Data
**❌ Problem:** Label only 30-40 examples total

**Example:**
- Test set has only 15 examples
- Calculate TPR=0.93, TNR=0.87
- These metrics are unreliable due to small sample

**✅ Solution:** Label at least 150-200 examples total. Test set should have 60-90 examples minimum.

#### 3. Imbalanced PASS/FAIL Ratio
**❌ Problem:** 90% PASS, 10% FAIL in labeled data

**Example:**
- 180 PASS examples, 20 FAIL examples
- TNR calculated on only 20 examples (unreliable)

**✅ Solution:** Aim for 40-60% PASS ratio. Oversample failure cases if needed.

### Judge Development Pitfalls

#### 4. Overfitting to Dev Set
**❌ Problem:** Iterate 20+ times on dev set, add specific examples for every dev error

**Example:**
- Dev set TPR=0.95, TNR=0.93 (looks great!)
- Test set TPR=0.78, TNR=0.81 (overfitted!)

**✅ Solution:** Limit dev set iterations to 5-10. Use test set only once at the end.

#### 5. Vague Evaluation Criteria
**❌ Problem:** Judge instructions say "Evaluate if response is good"

**Example:**
```
TASK: Determine if the recipe is good.
Answer: PASS or FAIL
```

**✅ Solution:** Define "good" precisely with objective criteria:
```
TASK: Evaluate if recipe adheres to dietary restriction.
PASS: All ingredients comply with [specific restriction]
FAIL: Any ingredient violates [specific restriction]
```

#### 6. Poor Few-Shot Examples
**❌ Problem:** All few-shot examples are trivial, don't cover edge cases

**Example:**
- Example 1: Vegan recipe with obvious animal product (bacon) → FAIL
- Example 2: Vegan recipe with clearly plant-based ingredients → PASS

**✅ Solution:** Include edge cases in few-shot examples:
- Honey in vegan recipe (not obvious to everyone)
- "Gluten-free wrap" without verification (ambiguous)
- Optional cheese topping (still a violation)

### Evaluation and Reporting Pitfalls

#### 7. Ignoring Confidence Intervals
**❌ Problem:** Report "System achieves 87.3% success rate" without uncertainty

**Example:**
- Corrected θ̂ = 0.873
- 95% CI: [0.65, 1.00]
- Extremely wide interval ignored!

**✅ Solution:** Always report: "Success rate: 87.3% (95% CI: [65%, 100%]). High uncertainty due to small test set."

#### 8. Testing on Training Data
**❌ Problem:** Calculate TPR/TNR on the same data used for few-shot examples

**Example:**
- Use all 150 labeled examples for few-shot selection
- Test judge performance on same 150 examples
- TPR/TNR are inflated (overfitting)

**✅ Solution:** Strict data splitting. Train/dev/test must be completely separate.

#### 9. No Error Analysis
**❌ Problem:** Judge has TNR=0.78, but never investigate which cases it misses

**Example:**
- Judge consistently misses honey in vegan recipes
- Never discover this pattern
- Deploy to production with blind spot

**✅ Solution:** Analyze all false positives and false negatives. Look for patterns. Fix prompt based on analysis.

---

## Key Takeaways

- ✅ **LLM-as-Judge enables scalable evaluation** - Evaluate 1000s of examples at $0.001-0.01 each
- ✅ **Use for clear, objective criteria** - Subjective tasks require human judgment
- ✅ **All judges have bias** - Measure TPR/TNR, correct statistically, report confidence intervals
- ✅ **Ground truth is critical** - Invest in high-quality labeled data (150-200 examples minimum)
- ✅ **Iterate on dev set, evaluate on test set once** - Avoid overfitting to evaluation data
- ✅ **Report corrected rates with uncertainty** - Raw pass rates are misleading without correction
- ✅ **Analyze errors systematically** - False positives/negatives reveal prompt improvement opportunities
- ✅ **Choose model based on task complexity** - Premium models for complex criteria, mini models for simple criteria

---

## Further Reading

### Related Tutorials
- [Data Labeling Tutorial](data_labeling_tutorial.ipynb) - Create ground truth datasets
- [Judge Development Tutorial](judge_development_tutorial.ipynb) - Build and refine judge prompts
- [Bias Correction Tutorial](bias_correction_tutorial.md) - Apply statistical correction with judgy
- [Error Analysis Concepts](../hw2/error_analysis_concepts.md) - Prerequisite methodology

### Methodological Background
- **LLM-as-Judge Research**: Zheng et al. (2023) "Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena"
- **Statistical Correction**: Theory of imperfect annotators in ML
- **Evaluation Methodology**: Test/dev/train splitting best practices from ML research

### Course Materials
- [AI Evaluation Complete Guide](../../AI_EVALUATION_COMPLETE_GUIDE.md) - Section 4: LLM-as-Judge
- [HW3 Assignment README](README.md) - Full homework instructions
- [HW3 Walkthrough Notebook](hw3_walkthrough.ipynb) - Complete worked example with judgy
- [HW3 Tutorial Index](TUTORIAL_INDEX.md) - All HW3 learning resources

### Code References
- [scripts/label_data.py](scripts/label_data.py) - Automated ground truth creation
- [scripts/develop_judge.py](scripts/develop_judge.py) - Judge prompt engineering
- [scripts/evaluate_judge.py](scripts/evaluate_judge.py) - TPR/TNR calculation
- [scripts/run_full_evaluation.py](scripts/run_full_evaluation.py) - Complete pipeline with judgy

### External Resources
- [judgy library documentation](https://github.com/ai-evals-course/judgy) - Statistical bias correction
- [LiteLLM documentation](https://docs.litellm.ai/) - Multi-provider LLM API access

---

**Tutorial Status:** ✅ Complete
**Last Updated:** 2025-10-29
**Maintainer:** AI Evaluation Course Team
