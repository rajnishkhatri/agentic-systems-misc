# Automated Evaluation Family

**When to use this family**: Scale evaluation (100+ examples), objective criteria exist, production monitoring, cost-effective quality assurance

---

## Overview

Automated evaluation uses **LLMs or programmatic methods** to evaluate outputs at scale. Use when:
- ✅ Have 100+ examples to evaluate
- ✅ Criteria are objective and clearly defined
- ✅ Need repeatable, consistent judgments
- ✅ Want production monitoring without human reviewers

---

## Core Technique: LLM-as-Judge (HW3)

### When It Works Well
- ✅ Clear, testable criteria (e.g., "Does recipe contain animal products?")
- ✅ Binary or multi-class classification
- ✅ Factual correctness evaluation
- ✅ Format compliance checking

### When It Fails
- ❌ Highly subjective criteria (e.g., "Is this response funny?")
- ❌ Safety-critical tasks (use human review)
- ❌ Judge can't verify claims (needs external knowledge)

### Complete Workflow

```
1. Ground Truth Creation (15-30 min, $0.50-1.00)
   └─ Label 100-200 examples with GPT-4o

2. Dataset Splitting (5 min, Free)
   └─ 15% train / 40% dev / 45% test

3. Judge Development (2-3 hours, $0.03-0.05 per 100)
   ├─ Engineer prompt with clear criteria
   ├─ Select few-shot examples from train set
   ├─ Iterate on dev set
   └─ Measure TPR/TNR on dev set

4. Final Evaluation (Once only, $0.03-0.05)
   └─ Measure TPR/TNR on test set

5. Bias Correction (10 min, Free)
   └─ Apply judgy library correction

6. Production Deployment (Ongoing, $0.03 per 100)
   └─ Monitor with bias-corrected metrics
```

---

## Techniques in This Family

### 1. Ground Truth Labeling (HW3)
**Purpose**: Create high-quality labeled dataset

**Key decisions**:
- **Model choice**: GPT-4o or Claude Sonnet (NOT gpt-4o-mini for ground truth)
- **Spot-check**: Manually review 10-20% of labels
- **Criteria clarity**: Write 1-page labeling guide

**Cost**: $0.50-1.00 per 150 examples (GPT-4o)

---

### 2. LLM-as-Judge (HW3)
**Purpose**: Automated evaluation with cheaper model

**Judge prompt structure**:
```markdown
You are evaluating [system] outputs for [specific criterion].

CRITERIA:
A response is PASS if [clear definition].
A response is FAIL if [clear definition].

EXAMPLES:
[1 PASS example]
[3 FAIL examples showing edge cases]

TASK:
Evaluate the following output and respond with:
- verdict: "PASS" or "FAIL"
- reasoning: Brief explanation
```

**Few-shot ratio**: 1 PASS : 3 FAIL recommended (highlights edge cases)

**Cost**: $0.03-0.05 per 100 examples (gpt-4o-mini as judge)

---

### 3. Bias Correction (HW3 + Lesson 4)
**Purpose**: Account for systematic judge errors

**When to apply**:
- Judge has known TPR/TNR (measured on test set)
- Reporting results for large unlabeled dataset
- Want statistically rigorous success rates

**Using judgy library**:
```python
from judgy import binary_correction

# Measured on test set
TPR = 0.93  # Judge correctly identifies 93% of passes
TNR = 0.88  # Judge correctly identifies 88% of fails

# Observed on large production dataset
observed_pass_rate = 0.85

# Corrected estimate
corrected_result = binary_correction(
    observed_pass_rate,
    tpr=TPR,
    tnr=TNR,
    n=1000  # Sample size
)

print(f"Corrected rate: {corrected_result.theta:.2%}")
print(f"95% CI: [{corrected_result.ci_lower:.2%}, {corrected_result.ci_upper:.2%}]")
```

**Why it matters**: Judge with TPR=90%, TNR=95% reporting 85% might indicate **true** rate of 92%±5%.

---

### 4. Parallel Labeling (Lesson 4)
**Purpose**: Speed up labeling from 40min → 5min

**Pattern**:
```python
from concurrent.futures import ThreadPoolExecutor
from tqdm import tqdm

def label_one_trace(trace):
    response = litellm.completion(
        model="gpt-4o",
        messages=[...],
        timeout=30
    )
    return {**trace, "label": response.choices[0].message.content}

# Parallel execution
with ThreadPoolExecutor(max_workers=64) as executor:
    labeled_traces = list(tqdm(
        executor.map(label_one_trace, traces),
        total=len(traces),
        desc="Labeling"
    ))
```

**Worker count**: Start with 10, increase to 64 if no rate limit errors

**Cost**: Same total cost, just faster

---

### 5. Substantiation Evaluation (Lesson 4)
**Purpose**: Verify agent responses are grounded in tool outputs

**Definition**: A response is SUBSTANTIATED if every factual claim can be verified by:
1. User-provided information
2. Tool outputs
3. Tool metadata
4. Information obtainable by calling available tools

**Judge prompt focuses on**:
- Identifying factual claims in response
- Checking each claim against tool outputs
- Flagging unverifiable claims (hallucinations)

**Typical TPR/TNR**: >90% for both with well-engineered prompt

---

### 6. Synthetic Query Generation (HW2, HW4)
**Purpose**: Expand test coverage systematically

**Two approaches**:

**A. Dimension Tuples (HW2)**:
```
1. Identify dimensions (cuisine, dietary, meal_type, time)
2. LLM generates tuples: (Thai, vegan, dinner, <30min)
3. Convert to queries: "Quick Thai vegan dinner under 30 minutes?"
```

**B. Salient Fact Extraction (HW4)**:
```
1. LLM extracts facts from document
2. Convert facts to queries
3. Map query → source document
```

**Cost**: $0.05-0.40 for 100 queries (gpt-4o-mini)

---

## Anti-Patterns

### ❌ Using Cheap Model for Ground Truth
**Problem**: gpt-4o-mini labels have errors → entire judge evaluation is compromised

**Solution**: Always use best model (GPT-4o, Claude) for ground truth

### ❌ Testing on Training Data
**Problem**: Judge prompt optimized on test set → inflated performance metrics

**Solution**: Strict train/dev/test split, **never** look at test set during development

### ❌ Ignoring Judge Errors
**Problem**: Treating judge predictions as perfect → overconfidence in results

**Solution**: Always measure TPR/TNR, apply bias correction

### ❌ No Human Validation
**Problem**: Trusting automated labels without spot-checking

**Solution**: Manually review 10-20% of labels for quality assurance

---

## Cost Optimization Strategies

### 1. Model Selection
```
Ground Truth: GPT-4o ($0.0025/1K input) ← Worth it for quality
Judge: gpt-4o-mini ($0.00015/1K input) ← 16x cheaper, acceptable quality
```

### 2. Prompt Optimization
- Shorter prompts = lower cost
- Remove unnecessary context
- Use few-shot examples sparingly (1+3 = 4 examples sufficient)

### 3. Sampling
- Don't evaluate all 10,000 production traces
- Sample 500-1000 for weekly monitoring
- Deep-dive on flagged failures

### 4. Caching
- Cache judge responses for identical inputs
- Reuse ground truth labels across experiments

---

## Quality Assurance Checklist

**Before deploying judge**:
- [ ] Test set TPR ≥ 85%
- [ ] Test set TNR ≥ 85%
- [ ] Spot-checked 20 false positives (understand why)
- [ ] Spot-checked 20 false negatives (understand why)
- [ ] Documented evaluation criteria clearly
- [ ] Set up monitoring dashboard

**During production**:
- [ ] Weekly sampling of 500-1000 traces
- [ ] Monthly re-measurement of TPR/TNR on new test set
- [ ] Quarterly review of judge prompt (update if criteria changed)

---

## Integration with Other Families

### Qualitative → Automated
1. Manual annotation (Lesson 7) creates initial dataset
2. LLM-as-Judge (HW3) scales evaluation
3. Monitor with quantitative metrics

### Automated → Optimization
1. LLM-as-Judge identifies expensive model performance
2. Cheaper judge approximates expensive model
3. Model cascade (Lesson 8) routes based on confidence

---

## Real-World Example

**Scenario**: Recipe chatbot - evaluate dietary adherence at scale

### Phase 1: Ground Truth (30 min, $1.00)
- Collect 150 traces with dietary restrictions
- Label with GPT-4o: "Does response violate dietary restriction?"
- Spot-check 20 labels manually → 95% correct

### Phase 2: Judge Development (2 hours, $0.10)
- Split: 23 train / 60 dev / 67 test
- Engineer prompt with 4 few-shot examples (1 pass, 3 fail)
- Iterate on dev set → Achieve TPR=92%, TNR=89%

### Phase 3: Test Evaluation (5 min, $0.03)
- Measure on test set: TPR=93%, TNR=88%
- Result: Judge is reliable

### Phase 4: Production (Weekly, $0.15)
- Evaluate 500 sampled traces per week
- Raw pass rate: 85%
- Bias-corrected rate: 92% (95% CI: [88%, 96%])
- Report: "92% of responses adhere to dietary restrictions"

### Phase 5: Monitoring (Ongoing)
- Set alert: If corrected rate < 90%, investigate
- Monthly re-validation: Re-measure TPR/TNR on new test set
- Quarterly review: Update judge prompt if criteria evolve

---

## Further Reading

**From tutorials**:
- [HW3: LLM-as-Judge Complete Workflow](../../homeworks/hw3/TUTORIAL_INDEX.md)
- [Lesson 4: Substantiation + Parallel Labeling](../../lesson-4/TUTORIAL_INDEX.md)
- [HW2: Synthetic Query Generation](../../homeworks/hw2/TUTORIAL_INDEX.md)

**Research**:
- "Judging LLM-as-a-Judge" (Zheng et al., 2023)
- judgy library: https://github.com/ai-evals-course/judgy
