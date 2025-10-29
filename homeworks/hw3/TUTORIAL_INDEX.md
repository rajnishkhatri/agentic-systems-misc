# Homework 3: Tutorial Index

## Overview

Homework 3 introduces **LLM-as-Judge evaluation**, a powerful technique for automated assessment of AI system outputs. You'll learn to use a high-quality LLM to evaluate a specific failure mode ("Adherence to Dietary Preferences"), apply statistical bias correction, and report performance with confidence intervals using the `judgy` library.

**Learning Time:** ~5-6 hours
**Difficulty:** Intermediate to Advanced
**Prerequisites:** Completion of HW2 (error analysis and failure taxonomies)

---

## Learning Objectives

By completing these tutorials, you will be able to:
- ✅ Understand the LLM-as-Judge paradigm and when to use it
- ✅ Create high-quality ground truth labels for evaluation datasets
- ✅ Split datasets into train/dev/test sets for rigorous evaluation
- ✅ Engineer effective judge prompts with few-shot examples
- ✅ Measure judge performance using TPR (True Positive Rate) and TNR (True Negative Rate)
- ✅ Apply statistical bias correction using the `judgy` library
- ✅ Report corrected success rates with confidence intervals
- ✅ Identify and analyze systematic judge errors

---

## Tutorials

### 1. LLM-as-Judge Concepts
**File:** `llm_judge_concepts.md`
**Reading Time:** 20-25 minutes
**Topics:**
- What is LLM-as-Judge and why use it?
- When automated evaluation is appropriate vs. human evaluation
- Bias considerations: judge alignment and systematic errors
- Ground truth creation strategies
- Cost-accuracy trade-offs in judge model selection
- Calibration and confidence intervals

**When to use:** Start here to understand the methodology before building your judge.

---

### 2. Data Labeling Tutorial (Interactive)
**File:** `data_labeling_tutorial.ipynb`
**Execution Time:** 15-20 minutes
**Topics:**
- Manual vs. automated ground truth labeling
- Creating balanced train/dev/test splits
- Labeling consistency and inter-annotator agreement
- Using GPT-4o for automated labeling (with caveats)
- Quality validation and label review
- Handling edge cases and ambiguous examples

**When to use:** After collecting bot traces, use this to create your ground truth dataset.

**Interactive Features:**
- Dataset splitting code with reproducible random seeds
- Labeling interface examples
- Label distribution analysis
- Export labeled datasets to CSV

---

### 3. Judge Development Tutorial (Interactive)
**File:** `judge_development_tutorial.ipynb`
**Execution Time:** 20-30 minutes
**Topics:**
- Engineering effective judge prompts
- Few-shot example selection strategies
- Structured output with Pydantic models
- Iterative prompt refinement using dev set
- Debugging common judge errors
- Measuring TPR/TNR on validation data

**When to use:** After creating labeled dataset, use this to build and refine your judge.

**Interactive Features:**
- Live judge prompt testing
- TPR/TNR calculation on dev set
- Confusion matrix visualization
- False positive/negative analysis

---

### 4. Bias Correction Tutorial
**File:** `bias_correction_tutorial.md`
**Reading Time:** 15-20 minutes
**Topics:**
- Understanding TPR and TNR metrics
- Why raw pass rates can be misleading
- Statistical correction using the `judgy` library
- Calculating corrected success rates (θ̂)
- Interpreting 95% confidence intervals
- When correction helps vs. when it doesn't

**When to use:** After evaluating your judge on test set, use this to report corrected results.

**Key Formulas:**
```
TPR = True Positives / (True Positives + False Negatives)
TNR = True Negatives / (True Negatives + False Positives)

Corrected Rate (θ̂) = (p_obs + TNR - 1) / (TPR + TNR - 1)
```

---

### 5. Judge Evaluation Flow (Visual)
**File:** `diagrams/judge_evaluation_flow.mmd`
**Format:** Mermaid diagram (viewable on GitHub)
**Topics:**
- Complete pipeline from trace generation to final metrics
- Data splitting strategy visualization
- Judge development iteration loop
- Bias correction workflow

**When to use:** Reference this to understand the complete evaluation workflow.

---

## Recommended Learning Path

```
┌────────────────────────────────────────────────────────────┐
│          HW3 LLM-as-Judge Evaluation Workflow              │
├────────────────────────────────────────────────────────────┤
│                                                            │
│  OPTION 1: Full Implementation (Most Learning)            │
│  ┌──────────────────────────────────────────────────────┐ │
│  │ 1. Generate your own Recipe Bot traces               │ │
│  │ 2. Complete "Data Labeling Tutorial"                 │ │
│  │ 3. Label 100-200 examples manually                   │ │
│  │ 4. Split into train/dev/test                         │ │
│  └──────────────────────────────────────────────────────┘ │
│                                                            │
│  OPTION 2: Start with Raw Traces (Medium Implementation)  │
│  ┌──────────────────────────────────────────────────────┐ │
│  │ 1. Use provided raw_traces.csv (~2400 traces)        │ │
│  │ 2. Complete "Data Labeling Tutorial"                 │ │
│  │ 3. Label subset (100-200 examples)                   │ │
│  │ 4. Split into train/dev/test                         │ │
│  └──────────────────────────────────────────────────────┘ │
│                                                            │
│  OPTION 3: Start with Labeled Data (Judge Focus)          │
│  ┌──────────────────────────────────────────────────────┐ │
│  │ 1. Use provided labeled_traces.csv (150 examples)    │ │
│  │ 2. Skip directly to judge development                │ │
│  └──────────────────────────────────────────────────────┘ │
│                                                            │
│  ALL OPTIONS CONTINUE HERE:                               │
│  ┌──────────────────────────────────────────────────────┐ │
│  │ 5. Complete "LLM-as-Judge Concepts" tutorial         │ │
│  │ 6. Complete "Judge Development Tutorial"             │ │
│  │ 7. Iterate on judge prompt using dev set             │ │
│  │ 8. Measure final TPR/TNR on test set                 │ │
│  │ 9. Complete "Bias Correction Tutorial"               │ │
│  │ 10. Run judge on large unlabeled dataset             │ │
│  │ 11. Apply judgy correction and report results        │ │
│  └──────────────────────────────────────────────────────┘ │
└────────────────────────────────────────────────────────────┘
```

---

## Key Concepts

### LLM-as-Judge
**LLM-as-Judge** uses a high-quality LLM to evaluate specific properties of AI system outputs:
- **Ground Truth Creation:** Use GPT-4o/Claude to create labeled dataset
- **Judge Development:** Engineer prompts for automated evaluation
- **Bias Correction:** Account for systematic judge errors statistically

**When it works well:**
- ✅ Clear, objective evaluation criteria (e.g., dietary adherence)
- ✅ Large-scale evaluation needs (thousands of examples)
- ✅ Repeatable, consistent judgments required

**When to avoid:**
- ❌ Highly subjective criteria (e.g., "humor quality")
- ❌ Safety-critical applications (use human review)
- ❌ Very small datasets (<50 examples)

### True Positive Rate (TPR)
**TPR (Sensitivity)** measures how often the judge correctly identifies passing examples:
```
TPR = True Positives / (True Positives + False Negatives)
```
**High TPR** = Judge rarely misses passing examples (low false negative rate)

**Example:** If 100 recipes truly adhere to dietary restrictions, and judge says 95 pass:
- TPR = 95/100 = 0.95 (95%)

### True Negative Rate (TNR)
**TNR (Specificity)** measures how often the judge correctly identifies failing examples:
```
TNR = True Negatives / (True Negatives + False Positives)
```
**High TNR** = Judge rarely misses failing examples (low false positive rate)

**Example:** If 50 recipes violate dietary restrictions, and judge says 45 fail:
- TNR = 45/50 = 0.90 (90%)

### Statistical Bias Correction
The **judgy library** corrects for systematic judge errors:
- **Raw pass rate (p_obs):** What the judge reports
- **Corrected rate (θ̂):** True success rate accounting for TPR/TNR
- **95% CI:** Confidence interval for the corrected rate

**Why it matters:** A judge with 90% TPR and 95% TNR reporting 85% pass rate might indicate a **true** rate of 92%±5%.

---

## Practical Exercises

After completing the tutorials, try these exercises:

1. **Judge Prompt Engineering Exercise**
   - Write 3 different judge prompts for dietary adherence
   - Test each on the same dev set
   - Compare TPR/TNR for each version
   - Identify which prompt characteristics improve performance

2. **Few-Shot Selection Exercise**
   - Select 5 few-shot examples from train set
   - Test judge with: 0-shot, 1-shot, 3-shot, 5-shot
   - Measure how few-shot count affects TPR/TNR
   - Identify diminishing returns point

3. **Error Analysis Exercise**
   - Identify all false positives from test set
   - Identify all false negatives from test set
   - Group errors into categories
   - Propose prompt improvements to address each category

---

## Common Pitfalls

### Ground Truth Labeling
- ❌ **Inconsistent criteria:** Changing standards mid-labeling
- ❌ **Insufficient examples:** <50 labeled examples per class
- ❌ **Imbalanced dataset:** 90% pass, 10% fail makes training hard
- ❌ **No validation:** Trusting automated labels without spot-checking

### Judge Development
- ❌ **Overfitting to dev set:** Making prompt too specific to dev examples
- ❌ **Unclear criteria:** Judge doesn't know what "pass" means
- ❌ **Poor few-shot examples:** Examples don't cover edge cases
- ❌ **No structured output:** Free-text responses are hard to parse

### Evaluation & Reporting
- ❌ **Only reporting accuracy:** TPR and TNR give more insight
- ❌ **Ignoring confidence intervals:** Point estimates without uncertainty
- ❌ **Testing on training data:** Inflated performance metrics
- ❌ **No error analysis:** Not investigating why judge fails

---

## Reference Files

### Assignment Materials
- [`README.md`](README.md) - Assignment instructions and options
- [`hw3_walkthrough.ipynb`](hw3_walkthrough.ipynb) - Complete worked example
- [`data/dietary_queries.csv`](data/dietary_queries.csv) - 60 challenging edge case queries
- [`data/raw_traces.csv`](data/raw_traces.csv) - ~2400 bot traces (Option 2)
- [`data/labeled_traces.csv`](data/labeled_traces.csv) - 150 labeled examples (Option 3)

### Scripts
- [`scripts/generate_traces.py`](scripts/generate_traces.py) - Trace generation with parallel processing
- [`scripts/label_data.py`](scripts/label_data.py) - Automated labeling with GPT-4o
- [`scripts/split_data.py`](scripts/split_data.py) - Train/dev/test splitting
- [`scripts/develop_judge.py`](scripts/develop_judge.py) - Judge prompt engineering
- [`scripts/evaluate_judge.py`](scripts/evaluate_judge.py) - Test set evaluation
- [`scripts/run_full_evaluation.py`](scripts/run_full_evaluation.py) - Complete pipeline

### Video Walkthroughs
- [HW3 Solution Walkthrough](https://youtu.be/1d5aNfslwHg)

---

## Tools & Libraries

**Required:**
- `judgy` - Statistical bias correction ([GitHub](https://github.com/ai-evals-course/judgy))
- `litellm` - Multi-provider LLM API access
- `pydantic` - Structured output validation
- `pandas` - Data manipulation

**Installation:**
```bash
pip install judgy litellm pydantic pandas
```

---

## Expected Outputs

After completing HW3, you should have:
- ✅ Labeled dataset with train/dev/test splits
- ✅ Final judge prompt with few-shot examples
- ✅ Judge performance metrics (TPR/TNR) on test set
- ✅ Evaluation results with corrected success rate and 95% CI
- ✅ Brief analysis interpreting results (1-2 paragraphs)

**Example Result:**
```
Raw Observed Success Rate: 85.7%
Corrected Success Rate: 92.6%
95% Confidence Interval: [81.7%, 100.0%]
Correction Applied: +6.9 percentage points

Interpretation: The Recipe Bot has strong dietary adherence
(92.6% corrected success rate). The judge initially under-
estimated performance due to false negatives, which bias
correction successfully accounted for.
```

---

## Connection to Research

This assignment implements techniques from:
- **LLM-as-Judge:** Zheng et al. (2023) "Judging LLM-as-a-Judge"
- **Bias Correction:** Statistical correction for imperfect annotators
- **Evaluation Methodology:** Benchmark design from ML research

**Key Insight:** Even imperfect judges (80-90% accuracy) can provide valuable signal when bias-corrected.

---

## Next Steps

After completing HW3, you'll have:
- ✅ Automated evaluation capabilities for specific failure modes
- ✅ Statistical rigor in performance measurement
- ✅ Understanding of when LLM-as-Judge is appropriate

**Move on to Homework 4** to learn retrieval evaluation for RAG systems.

👉 [Homework 4 Tutorial Index](../hw4/TUTORIAL_INDEX.md)

---

## FAQ

**Q: Can I use a cheaper model as the ground truth labeler?**
A: Not recommended. Use the best available model (GPT-4o, Claude Sonnet) for ground truth.

**Q: How many labeled examples do I need?**
A: Minimum 100 total (50 pass, 50 fail). More is better. Reference implementation uses 150.

**Q: What if my judge has low TPR or TNR (<80%)?**
A: Refine your prompt, add better few-shot examples, or reconsider if the task is suitable for LLM-as-Judge.

**Q: When should I trust the corrected rate vs. raw rate?**
A: Always report both. Corrected rate is more accurate if your test set TPR/TNR are reliable.

**Q: Can I use a different failure mode than dietary adherence?**
A: Yes! But you'll need to generate all your own traces and define clear evaluation criteria.

**Q: How do I choose few-shot examples?**
A: Select diverse, representative examples that cover edge cases and clearly demonstrate pass/fail criteria.

---

**Tutorial Status:** ⏳ In Development
**Last Updated:** 2025-10-29
**Maintainer:** AI Evaluation Course Team
