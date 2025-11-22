# Evaluation Methodology Research Report
## Comprehensive Analysis of ML & Statistical Evaluation Methods in Homework Assignments

**Report Date:** 2025-11-21
**Research Scope:** `/homeworks` folder (HW1-HW5)
**Purpose:** Document all evaluation criteria, ML methodologies, and statistical methods used for AI system assessment

---

## Executive Summary

This report documents all evaluation methodologies discovered across 5 homework assignments in an AI evaluation course. The research reveals a **systematic progression from qualitative to quantitative evaluation**, with each assignment introducing complementary methodologies:

| Assignment | Focus | Primary Methodologies |
|------------|-------|----------------------|
| **HW1** | Prompt Engineering | Qualitative review, manual testing |
| **HW2** | Error Analysis | Open coding, axial coding, failure taxonomies |
| **HW3** | LLM-as-Judge | TPR/TNR, statistical bias correction, bootstrap sampling |
| **HW4** | RAG Evaluation | Recall@k, MRR, BM25, information retrieval metrics |
| **HW5** | Agent Failure Analysis | Transition matrices, state-based analysis, heatmap visualization |

**Key Finding:** The course teaches a **defensive evaluation philosophy** - start qualitative (understand failures), then quantitative (measure at scale), then correct for bias (statistical methods).

---

## Table of Contents

1. [Statistical Classification Metrics](#1-statistical-classification-metrics)
2. [Information Retrieval Metrics](#2-information-retrieval-metrics)
3. [Qualitative Evaluation Methods](#3-qualitative-evaluation-methods)
4. [Statistical Correction Methods](#4-statistical-correction-methods)
5. [Specialized Evaluation Methodologies](#5-specialized-evaluation-methodologies)
6. [Evaluation Workflow Progression](#6-evaluation-workflow-progression)
7. [Cross-Assignment Patterns](#7-cross-assignment-patterns)

---

## 1. Statistical Classification Metrics

### 1.1 True Positive Rate (TPR) - Sensitivity

**Definition:** Of all actual positive cases (ground truth PASS), what fraction does the judge correctly identify as PASS?

**Formula:**
```
TPR = True Positives / (True Positives + False Negatives)
    = Correct PASS predictions / All actual PASS cases
```

**Use Case:** Measuring LLM judge strictness in HW3

**Example from HW3:**
- Test set: 60 traces that truly PASS (dietary restrictions adhered)
- Judge predicts: 54 as PASS (correct), 6 as FAIL (incorrect)
- **TPR = 54/60 = 0.90 (90%)**

**Interpretation:**
- TPR = 1.00: Perfect sensitivity, never misses passing cases
- TPR = 0.90: Misses 10% of passing cases (somewhat strict)
- TPR < 0.75: Judge is too strict, correction becomes unreliable

**File Reference:** `homeworks/hw3/llm_judge_concepts.md:336-352`

---

### 1.2 True Negative Rate (TNR) - Specificity

**Definition:** Of all actual negative cases (ground truth FAIL), what fraction does the judge correctly identify as FAIL?

**Formula:**
```
TNR = True Negatives / (True Negatives + False Positives)
    = Correct FAIL predictions / All actual FAIL cases
```

**Use Case:** Measuring LLM judge leniency in HW3

**Example from HW3:**
- Test set: 40 traces that truly FAIL (dietary restrictions violated)
- Judge predicts: 34 as FAIL (correct), 6 as PASS (incorrect)
- **TNR = 34/40 = 0.85 (85%)**

**Interpretation:**
- TNR = 1.00: Perfect specificity, never misses failures
- TNR = 0.85: Misses 15% of failures (somewhat lenient)
- TNR < 0.75: Judge is too lenient, correction becomes unreliable

**File Reference:** `homeworks/hw3/llm_judge_concepts.md:354-369`

---

### 1.3 Accuracy

**Definition:** Overall fraction of correct predictions (both PASS and FAIL).

**Formula:**
```
Accuracy = (True Positives + True Negatives) / Total Predictions
```

**Use Case:** Overall judge performance in HW3

**Example from HW3:**
- 100 total predictions
- 54 correct PASS + 34 correct FAIL = 88 correct
- **Accuracy = 88/100 = 0.88 (88%)**

**Limitation:** Accuracy can be misleading with imbalanced datasets (e.g., 90% PASS, 10% FAIL).

**File Reference:** `homeworks/hw3/scripts/evaluate_judge.py:185-186`

---

### 1.4 Balanced Accuracy

**Definition:** Average of TPR and TNR, accounts for class imbalance.

**Formula:**
```
Balanced Accuracy = (TPR + TNR) / 2
```

**Use Case:** Judge performance metric that handles imbalanced test sets in HW3

**Example from HW3:**
- TPR = 0.90, TNR = 0.85
- **Balanced Accuracy = (0.90 + 0.85) / 2 = 0.875 (87.5%)**

**File Reference:** `homeworks/hw3/scripts/evaluate_judge.py:182`

---

### 1.5 Confusion Matrix

**Definition:** 2x2 matrix showing all possible classification outcomes.

**Structure:**
```
                  Predicted
               PASS      FAIL
Actual  PASS    TP        FN
        FAIL    FP        TN
```

**Components:**
- **TP (True Positive):** Correctly predicted PASS
- **TN (True Negative):** Correctly predicted FAIL
- **FP (False Positive):** Incorrectly predicted PASS (should be FAIL)
- **FN (False Negatives):** Incorrectly predicted FAIL (should be PASS)

**Use Case:** Calculating TPR/TNR for LLM judge evaluation in HW3

**Example from HW3:**
```python
tp = sum(1 for p in predictions if p["true_label"] == "PASS" and p["predicted_label"] == "PASS")
fn = sum(1 for p in predictions if p["true_label"] == "PASS" and p["predicted_label"] == "FAIL")
tn = sum(1 for p in predictions if p["true_label"] == "FAIL" and p["predicted_label"] == "FAIL")
fp = sum(1 for p in predictions if p["true_label"] == "FAIL" and p["predicted_label"] == "PASS")

tpr = tp / (tp + fn) if (tp + fn) > 0 else 0.0
tnr = tn / (tn + fp) if (tn + fp) > 0 else 0.0
```

**File Reference:** `homeworks/hw3/scripts/evaluate_judge.py:138-144`

---

## 2. Information Retrieval Metrics

### 2.1 Recall@k

**Definition:** Fraction of queries where the target document appears in the top-k retrieved results.

**Formula:**
```
Recall@k = (Number of queries with target in top-k) / Total queries
```

**Binary Metric:** Each query either succeeds (target found in top-k) or fails (target not found).

**Use Case:** RAG retrieval evaluation in HW4

**Common k values and interpretation:**

| Metric | User Experience | Typical Range |
|--------|----------------|---------------|
| **Recall@1** | Instant gratification, no scrolling | 40-60% (good) |
| **Recall@3** | Minimal scrolling, top 3 results | 60-80% (good) |
| **Recall@5** | Standard evaluation metric | 70-90% (good) |
| **Recall@10** | Upper bound, significant scrolling | 80-95% (good) |

**Example Calculation from HW4:**

After evaluating 100 synthetic queries:
- Recall@1: 52/100 = **0.52 (52%)**
- Recall@3: 71/100 = **0.71 (71%)**
- Recall@5: 83/100 = **0.83 (83%)**
- Recall@10: 91/100 = **0.91 (91%)**

**Interpretation:**
- 52% of users find answer as #1 result (excellent UX)
- 83% find answer in top 5 (good performance)
- Gap between Recall@1 and Recall@5 suggests ranking can be improved

**File Reference:** `homeworks/hw4/retrieval_metrics_tutorial.md:41-153`

---

### 2.2 Mean Reciprocal Rank (MRR)

**Definition:** Average of reciprocal ranks across all queries, heavily weights top positions.

**Formula:**
```
MRR = (1/N) × Σ(1 / rank_i)

Where:
- N = total number of queries
- rank_i = position of target document for query i
- 1/rank = reciprocal rank (higher rank → lower score)
```

**Use Case:** Measuring ranking quality in HW4 RAG evaluation

**Worked Example from HW4:**

6 queries with target ranks:
- Query 1: rank 1 → RR = 1/1 = **1.00**
- Query 2: rank 2 → RR = 1/2 = **0.50**
- Query 3: rank 3 → RR = 1/3 = **0.33**
- Query 4: rank 5 → RR = 1/5 = **0.20**
- Query 5: rank 10 → RR = 1/10 = **0.10**
- Query 6: not found → RR = **0.00**

```
MRR = (1.00 + 0.50 + 0.33 + 0.20 + 0.10 + 0.00) / 6
    = 2.13 / 6
    = 0.355 (35.5%)
```

**Interpretation:**
```
MRR ≈ 1 / (average rank of target)

MRR = 1.00: All targets at rank #1 (perfect)
MRR = 0.50: Average rank is #2
MRR = 0.33: Average rank is #3
MRR = 0.10: Average rank is #10
```

**MRR vs. Recall@k:**
- Recall@5 only cares **if** target is in top-5 (binary: yes/no)
- MRR cares **where** in top-5:
  - Target at #1 → MRR contribution: 1.00
  - Target at #5 → MRR contribution: 0.20
  - **5x difference in scoring!**

**File Reference:** `homeworks/hw4/retrieval_metrics_tutorial.md:156-238`

---

### 2.3 BM25 (Best Matching 25)

**Definition:** Probabilistic ranking function for information retrieval based on TF-IDF scoring.

**Core Formula (Simplified):**
```
Score(t, d) = IDF(t) × (TF(t, d) × (k1 + 1)) / (TF(t, d) + k1 × (1 - b + b × (len(d) / avg_len)))

Where:
- IDF(t): Inverse Document Frequency of term t
- TF(t, d): Term frequency in document d
- k1: Term frequency saturation (typically 1.2-2.0)
- b: Length normalization (typically 0.75)
- len(d): Document length
- avg_len: Average document length in corpus
```

**Three Key Components:**

1. **Term Frequency (TF):** How often query terms appear in document
   - More appearances → higher relevance

2. **Inverse Document Frequency (IDF):** How rare query terms are across corpus
   - Rarer terms → more discriminative → higher weight
   - Formula: `IDF(t) = log((N - df(t) + 0.5) / (df(t) + 0.5))`
   - N = total documents, df(t) = documents containing term t

3. **Document Length Normalization:** Prevent bias toward long documents
   - Longer documents naturally have more matches
   - Normalization adjusts for this

**Use Case:** Primary retrieval algorithm in HW4 RAG evaluation

**Example from HW4:**

Query: "air fryer chicken"

**Document 1:** "Air fryer chicken breast recipe with crispy skin. Cook in air fryer at 400°F." (15 words)
- TF("air fryer"): 2 occurrences
- Score: **HIGH** (frequent term appearances)

**Document 2:** "Chicken recipes including oven, stovetop, and air fryer methods." (11 words)
- TF("air fryer"): 1 occurrence
- Score: **MEDIUM** (single term appearance)

**Document 1 ranks higher** due to higher term frequency.

**File Reference:** `homeworks/hw4/rag_evaluation_concepts.md:139-220`

---

## 3. Qualitative Evaluation Methods

### 3.1 Open Coding

**Definition:** Exploratory analysis technique for reviewing interaction traces without preconceived categories.

**Origin:** Borrowed from Grounded Theory (Glaser & Strauss, 1967)

**Process:**
1. **Collect traces** - Run AI system on diverse queries (20-50+ traces)
2. **Initial review** - Read through each trace without judgment
3. **Descriptive labeling** - Assign specific, descriptive labels to observations
4. **Pattern identification** - Review labels to find recurring themes

**Key Principle:** Let patterns emerge from data rather than imposing structure upfront.

**Use Case:** Initial error analysis in HW2 to identify failure modes

**Example from HW2:**

Query: "Quick egg spinach cheese recipe pls"

Response: [Recipe with optional ingredients, no serving size, no time estimate]

**Open Codes Applied:**
- `no_serving_size` → Doesn't specify how many people this serves
- `vague_measurement` → "Shredded cheese (amount to taste)" - no quantity
- `optional_complexity` → Suggests optional ingredients for "quick" recipe
- `missing_cooking_time` → No total time estimate provided
- `good_structure` → [Positive] Clear Markdown formatting
- `step_by_step_clear` → [Positive] Instructions are easy to follow

**Pattern Recognition:**
After coding 20 traces:
- `no_serving_size`: 14/20 (70%) ← High-priority failure
- `vague_measurement`: 8/20 (40%)
- `missing_cooking_time`: 12/20 (60%) ← High-priority failure
- `optional_complexity`: 6/20 (30%)

**File Reference:** `homeworks/hw2/error_analysis_concepts.md:105-236`

---

### 3.2 Axial Coding

**Definition:** Organizational technique that groups related open codes into structured failure mode taxonomies.

**Goal:** Create categories that are:
- **Mutually exclusive** (conceptually distinct)
- **Collectively exhaustive** (cover all observed failures)
- **Clearly defined** (testable pass/fail criteria)

**Process:**
1. Review all open codes
2. Group similar codes into 3-8 categories
3. Name each category with clear, descriptive title
4. Write one-sentence definition
5. Select 1-2 illustrative examples

**Use Case:** Building failure taxonomies in HW2

**Example from HW2:**

**Open codes:**
- `no_serving_size`
- `missing_cooking_time`
- `vague_measurement`
- `no_prep_time_breakdown`

**Axial Grouping:**
→ **Failure Mode: "Missing Recipe Information"**

**Definition:** Bot fails to provide essential recipe details (serving size, time estimates, precise measurements).

**Examples:**
1. Query: "quick egg recipe" → Response missing serving size and total time
2. Query: "simple pasta dish" → Response with "cheese to taste" (no quantity)

**File Reference:** `homeworks/hw2/error_analysis_concepts.md:236-338`

---

### 3.3 Failure Mode Taxonomy

**Definition:** Structured documentation of system failure patterns with clear definitions and examples.

**Template:**
```markdown
## Failure Mode: [Title]

**Definition:** [One sentence describing failure condition]

**Illustrative Examples:**
1. *User Query*: "[query text]"
   *Bot Response Issue*: [What went wrong]

2. *User Query*: "[query text]"
   *Bot Response Issue*: [What went wrong]
```

**Use Case:** Systematic documentation of AI system failures in HW2

**Example Failure Mode from HW2:**

#### Failure Mode: Overcomplicated Simple Recipes

**Definition:** Bot provides recipes with too many ingredients or steps for what should be a simple dish.

**Illustrative Examples:**
1. *User Query*: "quick egg spinach cheese recipe pls"
   *Bot Response Issue*: Includes optional ingredients like garlic powder, red pepper flakes, and multiple preparation steps that could be simplified for a "quick" request.

2. *User Query*: "simple recipe using salmon lemon and fresh herbs"
   *Bot Response Issue*: Provides complex marinade preparation and multiple cooking methods (baking and pan-frying) when a simpler approach would suffice for a "simple" request.

**Sweet Spot for Taxonomy Size:** 3-8 failure modes
- Too few (<3): Too broad, not actionable
- Too many (>10): Dilutes focus, hard to track

**File Reference:** `homeworks/hw2/error_analysis_concepts.md:266-338`

---

## 4. Statistical Correction Methods

### 4.1 Bias Correction Formula (judgy Library)

**Definition:** Statistical adjustment for imperfect judge predictions using measured TPR/TNR.

**Problem:** LLM judges have systematic bias (false positives and false negatives). Raw pass rates are misleading.

**Formula:**
```
θ̂ = (p_obs + TNR - 1) / (TPR + TNR - 1)

Where:
- θ̂ (theta-hat): Corrected true pass rate
- p_obs: Raw observed pass rate from judge
- TPR: True Positive Rate from test set
- TNR: True Negative Rate from test set
```

**Derivation Intuition:**
- Numerator: Adjusts observed rate for false positives (TNR term)
- Denominator: Normalizes by judge's overall reliability (TPR + TNR)

**Use Case:** Correcting LLM judge bias in HW3 production evaluation

**Worked Example from HW3:**

Given:
- p_obs = 0.80 (judge says 80% pass on 1,000 traces)
- TPR = 0.90 (from test set evaluation)
- TNR = 0.85 (from test set evaluation)

Calculate:
```
θ̂ = (0.80 + 0.85 - 1) / (0.90 + 0.85 - 1)
  = 0.65 / 0.75
  = 0.867
  = 86.7%
```

**Interpretation:**
- Judge reported 80% pass rate (p_obs)
- Judge was too strict (TPR = 0.90), missing some passing cases
- **True pass rate is actually 86.7%** (higher than observed)
- Correction: **+6.7 percentage points**

**File Reference:** `homeworks/hw3/bias_correction_tutorial.md:113-177`

---

### 4.2 Bootstrap Confidence Intervals

**Definition:** Resampling method to estimate confidence intervals without complex statistical formulas.

**Algorithm:**
```python
# Step 1: Take your data (1 = pass, 0 = fail)
results = [1] * 850 + [0] * 150  # 85% pass rate, 1000 samples

# Step 2: Resample 10,000 times with replacement
bootstrap_rates = []
for _ in range(10000):
    resample = np.random.choice(results, size=len(results), replace=True)
    bootstrap_rates.append(np.mean(resample))

# Step 3: Calculate 95% CI from distribution
ci_lower = np.percentile(bootstrap_rates, 2.5)
ci_upper = np.percentile(bootstrap_rates, 97.5)
```

**Use Case:** Quantifying uncertainty in LLM judge evaluation (HW3)

**Example from HW3:**

**Small Dataset (20 samples):**
- Observed rate: 85% (17 pass, 3 fail)
- 95% CI: **[70%, 100%]** ← Very wide! Need more data.

**Large Dataset (200 samples):**
- Observed rate: 85% (170 pass, 30 fail)
- 95% CI: **[80%, 90%]** ← Much narrower!

**Key Insight:** More data → narrower confidence intervals → more certainty

**Why It Works:**
- Simulates variability you'd see if you repeated experiment
- Middle 95% of resampled rates form confidence interval
- No complex formulas needed (R.A. Fisher's "very simple and very tedious process")

**File Reference:** `homeworks/hw3/bias_correction_tutorial.md:326-412`

---

### 4.3 95% Confidence Interval Interpretation

**Definition:** Range where we are 95% confident the true parameter lies.

**Interpretation:**
"If we repeated this experiment 100 times, approximately 95 of the intervals would contain the true value."

**Example from HW3:**

**Result:** Corrected success rate = 92.6%, 95% CI = [81.7%, 100%]

**What this means:**
- Point estimate: 92.6% (best guess)
- We're 95% confident true rate is between 81.7% and 100%
- True rate very unlikely to be below 81.7%

**CI Width Analysis:**

**Narrow CI** (e.g., [84%, 89%], width = 5%):
- ✅ High confidence in estimate
- ✅ Large sample size or reliable judge
- ✅ Low uncertainty

**Wide CI** (e.g., [65%, 100%], width = 35%):
- ❌ Low confidence in estimate
- ❌ Small sample size or unreliable judge
- ❌ High uncertainty

**How to Narrow CI:**
1. Increase sample size (more labeled test data)
2. Improve judge quality (higher TPR/TNR)
3. Balance PASS/FAIL ratio in test set

**File Reference:** `homeworks/hw3/bias_correction_tutorial.md:268-324`

---

## 5. Specialized Evaluation Methodologies

### 5.1 Transition Matrix Analysis

**Definition:** Quantitative method for multi-step agent systems that counts failure transitions between states.

**Core Concept:**
- **State-based modeling:** Represent agent pipeline as sequence of discrete states
- **Failure transition:** Edge from last successful state to first failing state
- **Transition matrix:** Count frequencies of all (success → failure) pairs

**Use Case:** Agent failure analysis in HW5 (Recipe Bot with 10-state pipeline)

**State Pipeline Example from HW5:**
```
ParseRequest → PlanToolCalls → GenCustomerArgs → GetCustomerProfile
→ GenRecipeArgs → GetRecipes → GenWebArgs → GetWebInfo
→ ComposeResponse → DeliverResponse
```

**Failure Transition Identification:**
```
Successful: ParseRequest ✓ → PlanToolCalls ✓ → GenRecipeArgs ✓ → GetRecipes ✓
Failed:     ParseRequest ✓ → PlanToolCalls ✓ → GenRecipeArgs ✓ → GetRecipes ✗
                                                              ↑              ↑
                                                        Last Success   First Failure

Failure Transition: (GenRecipeArgs → GetRecipes)
```

**Transition Matrix Structure:**
```
               First Failing State →
            Parse  Plan  GenRec  GetRec  Compose
Last     ┌────────────────────────────────────┐
Success  │                                    │
  ↓      │                                    │
Parse    │   0      3      0       0       0  │
Plan     │   0      0      5       0       2  │
GenRec   │   0      0      0      22       0  │  ← Bottleneck!
GetRec   │   0      0      0       0       8  │
Compose  │   0      0      0       0       0  │
         └────────────────────────────────────┘
```

**Reading the Matrix:**
- Rows: Where system last succeeded
- Columns: Where system first failed
- Cell value: Number of traces with that transition
- **Cell (GenRec, GetRec) = 22:** Primary bottleneck (58% of failures)

**File Reference:** `homeworks/hw5/transition_analysis_concepts.md:1-196`

---

### 5.2 Bottleneck Identification Strategies

**Strategy 1: Sum by Column (Which State Fails Most?)**

```
              Parse  GenRec  GetRec  Compose  Total
Total Fails      5      12      35       8     60
```

**Interpretation:** `GetRecipes` fails 35/60 times (58%) → **Primary bottleneck**

**Action:** Prioritize fixing `GetRecipes` tool

**Strategy 2: Sum by Row (After Which State Do Failures Occur?)**

```
              Failures After This State
GenRec                  40
Plan                    15
GetRec                   5
```

**Interpretation:** 40/60 failures happen after `GenRecipeArgs`

**Hypothesis:** `GenRecipeArgs` output is often incorrect, causing downstream failures

**Action:** Improve `GenRecipeArgs` prompt or add validation

**Strategy 3: Diagonal Analysis (Same State Success → Fail)**

```
              Parse  Plan  GenRec
Parse           12      0      0
Plan             0      8      0
GenRec           0      0      5
```

**Interpretation:** Diagonal failures = state succeeds then immediately fails on re-execution

**Diagnosis:** Flaky LLM or non-deterministic tool behavior

**Action:** Add temperature=0 for determinism, investigate tool intermittency

**File Reference:** `homeworks/hw5/transition_analysis_concepts.md:326-381`

---

### 5.3 LLM vs. Tool Failure Attribution

**Definition:** Distinguishing whether failures are due to LLM generation errors or tool execution errors.

**State Types:**
1. **LLM States:** `ParseRequest`, `PlanToolCalls`, `GenRecipeArgs`, `ComposeResponse`
2. **Tool States:** `GetCustomerProfile`, `GetRecipes`, `GetWebInfo`
3. **System States:** `DeliverResponse`

**Different Solutions:**
- **LLM failures** → Fix prompts, add examples, improve model
- **Tool failures** → Fix APIs, improve data quality, add retries
- **System failures** → Fix infrastructure, add monitoring

**Investigation Process from HW5:**

**Scenario:** High failure count at `(GenRecipeArgs → GetRecipes)`

**Question:** Is LLM generating bad arguments or is tool failing?

**Pattern A: LLM Generates Invalid Arguments**
```json
GenRecipeArgs output: {"query": "xyzabc123", "limit": -5}
GetRecipes error: "Invalid query format"
```
**Diagnosis:** LLM failure → Fix prompt to generate valid queries

**Pattern B: LLM Generates Valid Arguments, Tool Returns Empty**
```json
GenRecipeArgs output: {"query": "vegan pasta gluten-free", "limit": 10}
GetRecipes output: {"results": [], "total": 0}
```
**Diagnosis:** Tool failure (data quality) → Add more recipes or improve search

**Key Takeaway:** Transition analysis identifies **where** failures happen. Trace inspection identifies **why**.

**File Reference:** `homeworks/hw5/transition_analysis_concepts.md:282-322`

---

### 5.4 Heatmap Visualization

**Definition:** Visual representation of transition matrix using color intensity to show failure frequency.

**Best Practices from HW5:**

**✅ Good Color Scheme:**
```python
sns.heatmap(matrix, cmap="YlOrRd", annot=True, fmt="d")
# Sequential colormap = clear patterns
```

**❌ Bad Color Scheme:**
```python
sns.heatmap(matrix, cmap="jet")
# Rainbow = confusing
```

**Required Elements:**
- `annot=True, fmt="d"`: Show actual counts in cells
- Ordered states: Follow pipeline sequence (not random)
- Axis labels: Clear state names

**Use Case:** Quickly identify bottlenecks in HW5 agent pipeline

**File Reference:** `homeworks/hw5/transition_analysis_concepts.md:499-533`

---

## 6. Evaluation Workflow Progression

### 6.1 HW1: Prompt Engineering (Foundational)

**Focus:** System prompt design and query diversity

**Evaluation Methods:**
- Manual testing with diverse queries
- Qualitative review of responses
- No formal metrics

**Purpose:** Establish baseline system behavior before systematic evaluation

**File Reference:** `homeworks/hw1/readme.md`

---

### 6.2 HW2: Error Analysis (Qualitative → Structured)

**Focus:** Systematic failure identification and taxonomy building

**Evaluation Methods:**
1. **Open Coding:** Exploratory analysis without preconceived categories
2. **Axial Coding:** Group related failures into structured taxonomies
3. **Failure Mode Documentation:** Write clear definitions and examples
4. **(Optional) Spreadsheet Analysis:** Track failure frequencies

**Key Outputs:**
- Failure mode taxonomy (3-8 modes)
- Prioritization by frequency × severity ÷ effort

**Transition to HW3:** "Now that we understand *what* failures occur (HW2), let's measure *how often* they occur at scale (HW3)"

**File Reference:** `homeworks/hw2/error_analysis_concepts.md`

---

### 6.3 HW3: LLM-as-Judge (Quantitative + Statistical)

**Focus:** Automated evaluation with bias correction

**Evaluation Methods:**
1. **Ground Truth Creation:** Manual labeling or LLM-assisted labeling
2. **Data Splitting:** Train (15%), Dev (40%), Test (45%)
3. **Judge Development:** Iterative prompt engineering on Dev set
4. **Performance Measurement:** TPR/TNR calculation on Test set
5. **Bias Correction:** Statistical adjustment using judgy library
6. **Confidence Intervals:** Bootstrap sampling for uncertainty quantification

**Key Metrics:**
- **TPR (True Positive Rate):** Judge sensitivity (catches passing cases)
- **TNR (True Negative Rate):** Judge specificity (catches failures)
- **Corrected Success Rate (θ̂):** Bias-adjusted true performance
- **95% Confidence Interval:** Uncertainty quantification

**Decision Thresholds:**
- Minimum: TPR ≥ 0.75 and TNR ≥ 0.75
- Good: TPR ≥ 0.85 and TNR ≥ 0.85
- Excellent: TPR ≥ 0.90 and TNR ≥ 0.90

**Transition to HW4:** "LLM-as-Judge works for end-to-end evaluation. But for RAG systems, evaluate retrieval separately first (cheaper, faster, clearer attribution)."

**File References:**
- `homeworks/hw3/llm_judge_concepts.md`
- `homeworks/hw3/bias_correction_tutorial.md`
- `homeworks/hw3/README.md`

---

### 6.4 HW4: RAG Evaluation (Information Retrieval)

**Focus:** Retrieval-specific metrics before end-to-end evaluation

**Evaluation Methods:**
1. **Synthetic Query Generation:** Create test queries from documents
2. **BM25 Retrieval:** TF-IDF-based ranking
3. **Retrieval Metrics:** Recall@k, MRR
4. **Query Segmentation:** Analyze by query type/complexity
5. **Baseline Comparison:** Random, title-only, full-text BM25

**Key Metrics:**
- **Recall@1, @3, @5, @10:** Success rate at different cutoffs
- **MRR (Mean Reciprocal Rank):** Ranking quality metric

**Typical Performance Ranges (well-designed systems):**
- Recall@1: 40-60% (good)
- Recall@5: 70-90% (good)
- MRR: 0.4-0.6 (good)

**Gap Analysis:**
- **High Recall@5, Low Recall@1:** Ranking problem (target retrieved but ranked low)
- **Low Recall@5, Low Recall@1:** Retrieval problem (target not retrieved at all)

**Transition to HW5:** "Now that we can evaluate single-step retrieval (HW4), let's handle multi-step agent pipelines (HW5)."

**File References:**
- `homeworks/hw4/rag_evaluation_concepts.md`
- `homeworks/hw4/retrieval_metrics_tutorial.md`
- `homeworks/hw4/README.md`

---

### 6.5 HW5: Agent Failure Analysis (State-Based Quantitative)

**Focus:** Multi-step agent debugging with transition matrices

**Evaluation Methods:**
1. **State Definition:** Map agent pipeline to discrete states
2. **Failure Transition Labeling:** Identify (last success → first failure)
3. **Transition Matrix Construction:** Count failure transition frequencies
4. **Bottleneck Identification:** Column/row sums, diagonal analysis
5. **LLM vs. Tool Attribution:** Trace inspection for root cause
6. **Heatmap Visualization:** Visual bottleneck identification

**Key Outputs:**
- Transition count matrix
- Primary bottleneck identification (highest-frequency transition)
- LLM vs. tool failure attribution
- Targeted improvement recommendations

**When to Use:**
- ✅ Multi-step agent systems with clear state boundaries
- ✅ Production debugging at scale (1000s of traces)
- ✅ Iterative improvement (fix bottleneck → rebuild matrix)

**When to Avoid:**
- ❌ Ambiguous state boundaries
- ❌ Very small datasets (<30 failure traces)
- ❌ Extremely diverse failure modes (no clustering)

**File References:**
- `homeworks/hw5/transition_analysis_concepts.md`
- `homeworks/hw5/README.md`

---

## 7. Cross-Assignment Patterns

### 7.1 Evaluation Philosophy: Qualitative → Quantitative → Corrected

**Pattern Observed:**
```
HW2 (Qualitative)        →  HW3 (Quantitative)       →  HW3 (Statistical)
Open/Axial Coding          LLM-as-Judge               Bias Correction
Understand failures        Measure at scale           Account for bias

HW4 (Quantitative)        →  HW5 (Quantitative)
Recall@k, MRR              Transition Matrices
Single-step retrieval      Multi-step agents
```

**Key Insight:** Start with understanding (qualitative), then scale measurement (quantitative), then correct for imperfections (statistical).

---

### 7.2 Defensive Evaluation Mindset

**Recurring Themes:**
1. **Always measure uncertainty** (confidence intervals in HW3)
2. **Establish baselines** (random, simple, full-text in HW4)
3. **Segment analysis** (query type, state type in HW4/HW5)
4. **Validate hypotheses with trace inspection** (HW2 + HW5)
5. **Report both raw and corrected metrics** (HW3)

---

### 7.3 When to Use Each Methodology

| Methodology | When to Use | When NOT to Use |
|-------------|-------------|-----------------|
| **Open/Axial Coding (HW2)** | Unknown failure modes, initial exploration, <50 traces | Need large-scale metrics, already know failure modes |
| **LLM-as-Judge (HW3)** | Clear objective criteria, need scalability (1000s of evaluations) | Subjective criteria, safety-critical applications, <50 labeled examples |
| **Recall@k / MRR (HW4)** | RAG systems, retrieval bottlenecks, need cheap evaluation | End-to-end quality is all that matters (evaluate generation too) |
| **Transition Matrices (HW5)** | Multi-step agents, production debugging at scale, clear state boundaries | Ambiguous states, <30 failure traces, extremely diverse failures |
| **Statistical Correction (HW3)** | Imperfect judges with measurable bias (TPR, TNR ≥ 0.75) | Perfect judges, very small test sets, subjective criteria |

---

## 8. Conclusion

This research reveals a **comprehensive, defensively-designed evaluation curriculum** that progresses systematically:

1. **Understand failures qualitatively** (HW2: Open/Axial Coding)
2. **Measure at scale quantitatively** (HW3: LLM-as-Judge; HW4: Recall@k; HW5: Transition Matrices)
3. **Correct for imperfections statistically** (HW3: Bias correction, confidence intervals)
4. **Validate with trace inspection** (HW2 + HW5)

**All methodologies share common principles:**
- Transparency (report raw + corrected metrics)
- Uncertainty quantification (confidence intervals, baselines)
- Segmented analysis (query types, state types, failure modes)
- Actionable insights (not just numbers, but "what to fix")

**Recommended Evaluation Workflow:**
```
1. HW2 Methods: Understand failures with open/axial coding
2. Choose quantitative method based on system type:
   - Simple classifier → HW3 (LLM-as-Judge)
   - RAG system → HW4 (Retrieval metrics)
   - Multi-step agent → HW5 (Transition matrices)
3. Apply statistical correction (HW3: Bias correction, confidence intervals)
4. Iterate: Fix bottleneck → Re-evaluate → Verify improvement
```

---

**Report Compiled By:** Claude Code
**Data Sources:** 5 homework folders, 22 tutorial files, 6 Python scripts
**Total Pages Read:** ~15,000 lines of documentation and code
**Methodologies Documented:** 20+ distinct evaluation techniques

---

## Appendix: File References by Category

### Statistical Metrics
- `homeworks/hw3/llm_judge_concepts.md` (TPR/TNR/Accuracy)
- `homeworks/hw3/scripts/evaluate_judge.py` (Implementation)

### Information Retrieval
- `homeworks/hw4/retrieval_metrics_tutorial.md` (Recall@k, MRR)
- `homeworks/hw4/rag_evaluation_concepts.md` (BM25)
- `homeworks/hw4/scripts/evaluate_retrieval.py` (Implementation)

### Qualitative Methods
- `homeworks/hw2/error_analysis_concepts.md` (Open/Axial Coding)
- `homeworks/hw2/failure_mode_taxonomy.md` (Examples)

### Statistical Correction
- `homeworks/hw3/bias_correction_tutorial.md` (judgy, Bootstrap)
- `homeworks/hw3/scripts/run_full_evaluation.py` (Implementation)

### Agent Evaluation
- `homeworks/hw5/transition_analysis_concepts.md` (Transition Matrices)
- `homeworks/hw5/analysis/transition_heatmaps.py` (Implementation)

---

**End of Report**
