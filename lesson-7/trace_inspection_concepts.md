# Trace Inspection Concepts Tutorial

## Learning Objectives

- ✅ Understand when manual inspection is necessary vs. automated evaluation
- ✅ Design effective annotation workflows for quality control
- ✅ Apply sampling strategies for efficient manual review
- ✅ Measure inter-annotator agreement for consistency
- ✅ Combine manual and automated evaluation methods
- ✅ Build quality control feedback loops

## Prerequisites

- Understanding of conversational AI systems
- Completed [HW2: Error Analysis](../homeworks/hw2/error_analysis_concepts.md) (recommended)
- Familiarity with qualitative evaluation methods

## Estimated Time

**Reading Time:** 15-18 minutes

---

## Concepts

### Why Manual Inspection?

**The Automation Paradox:**

Automated evaluation (LLM-as-Judge, metrics, etc.) is powerful but has limitations:
- ❌ Subjective criteria (tone, empathy, appropriateness)
- ❌ Edge cases requiring human judgment
- ❌ Safety-critical decisions needing human oversight
- ❌ Novel failure modes not yet captured in automated rules

**Manual inspection fills the gap** when:
1. Creating ground truth for LLM-as-Judge
2. Investigating edge cases
3. Validating automated evaluation quality
4. Discovering unknown failure modes

### Manual vs. Automated Trade-offs

```
┌──────────────────────────────────────────────────────┐
│     MANUAL vs AUTOMATED EVALUATION                   │
├──────────────────────────────────────────────────────┤
│                                                      │
│  MANUAL INSPECTION:                                  │
│  ✅ Subjective judgment (tone, appropriateness)     │
│  ✅ Catches novel/unexpected failures                │
│  ✅ Provides qualitative insights                    │
│  ❌ Slow (~50-100 traces/hour)                       │
│  ❌ Expensive ($20-50/hour labor)                    │
│  ❌ Not scalable to 1000s of traces                  │
│                                                      │
│  AUTOMATED EVALUATION:                               │
│  ✅ Fast (1000s of traces/hour)                      │
│  ✅ Consistent (same input → same output)            │
│  ✅ Scalable to production volumes                   │
│  ❌ Requires clear, objective criteria               │
│  ❌ Misses subjective quality issues                 │
│  ❌ Can have systematic blind spots                  │
└──────────────────────────────────────────────────────┘
```

**Optimal Strategy: Combine Both**
- Use manual inspection for edge cases and ground truth creation
- Use automated evaluation for large-scale monitoring
- Manual spot-checks validate automated quality

---

## When to Use Manual Inspection

### ✅ Essential Use Cases

**1. Ground Truth Creation**

Before training LLM-as-Judge (HW3, Lesson 4), you need labeled examples:
- Manually label 150-200 conversations
- Ensure high-quality, consistent annotations
- Use as train/dev/test sets for judge development

**Example:** Creating substantiation labels
- Read conversation + tool outputs
- Decide: Substantiated or not?
- Record rationale for decision

**2. Failure Mode Discovery (Open Coding)**

When you don't yet know what's failing (HW2):
- Read 30-50 failure traces
- Identify patterns (open coding)
- Build failure taxonomy
- Design automated detection later

**Example:** Recipe bot failures
- Manual review reveals: "Recipe doesn't match dietary restriction"
- Create category: "Dietary violation"
- Build LLM-as-Judge to detect at scale

**3. Edge Case Investigation**

When automated eval flags uncertain cases:
- LLM-as-Judge says "low confidence"
- Contradictory user feedback
- Safety-critical conversations

**Example:** Substantiation edge case
```
User: "Does A11 have a balcony?"
Agent: "I can check the property details for you."

Automated judge: Uncertain (could be courtesy or claim)
Manual review: PASS (offering to help, not claiming knowledge)
```

**4. Quality Validation**

Spot-checking automated labels (Lesson 4):
- Review 20-30 automated labels
- Compare to manual judgment
- Calculate agreement rate
- Identify systematic errors

**Example:** Judge validation
- Automated judge: 90% accuracy
- Manual spot-check: Finds judge marks all "I'll help you" as unsubstantiated
- Fix: Update judge prompt to allow courtesy statements

---

## Annotation Workflow Design

### Workflow Components

**1. Task Definition**
- **Clear criteria:** "Is the response substantiated?"
- **Decision rules:** "Courtesy statements don't need evidence"
- **Edge case guidance:** "If uncertain, mark as PASS"

**2. Annotation Interface**
- **Spreadsheet:** Quick for <50 traces
- **Web UI:** Better for 50+ traces, multiple annotators
- **CLI tool:** For technical annotators

**3. Quality Control**
- **Inter-annotator agreement:** Have 2+ annotators label same 20 traces
- **Consistency checks:** Re-label 10% of traces after 1 week
- **Disagreement resolution:** Discuss and refine criteria

### Example Workflow

```
┌────────────────────────────────────────────────────┐
│     ANNOTATION WORKFLOW                            │
├────────────────────────────────────────────────────┤
│                                                    │
│  1. Define Task                                    │
│     → Write evaluation criteria (1 page doc)      │
│     → Include 5 example annotations                │
│     ↓                                              │
│  2. Select Sample                                  │
│     → Random or stratified sampling                │
│     → 150-200 traces for ground truth              │
│     ↓                                              │
│  3. Annotate                                       │
│     → Use spreadsheet or web UI                    │
│     → Track time per trace                         │
│     → Mark uncertain cases                         │
│     ↓                                              │
│  4. Quality Check                                  │
│     → Calculate inter-annotator agreement          │
│     → Review uncertain cases                       │
│     → Refine criteria if needed                    │
│     ↓                                              │
│  5. Finalize                                       │
│     → Export labels                                │
│     → Document process                             │
│     → Use for automated eval development           │
└────────────────────────────────────────────────────┘
```

---

## Sampling Strategies

### Random Sampling

**When to use:** General quality assessment

**How:**
```python
import random
sample = random.sample(all_traces, 200)
```

**Pros:**
- ✅ Unbiased
- ✅ Represents overall distribution

**Cons:**
- ❌ May miss rare edge cases

### Stratified Sampling

**When to use:** Ensuring coverage of specific categories

**How:**
```python
# Sample 50 per customer persona
sample = []
for persona in personas:
    persona_traces = [t for t in traces if t['persona'] == persona]
    sample.extend(random.sample(persona_traces, 50))
```

**Pros:**
- ✅ Ensures representation of all categories
- ✅ Good for imbalanced datasets

**Cons:**
- ❌ Requires knowing categories upfront

### Targeted Sampling

**When to use:** Investigating specific issues

**Examples:**
- **Failure-only:** Sample only failed conversations
- **Low-confidence:** Sample traces where automated judge is uncertain
- **User-reported:** Sample conversations flagged by users

**How:**
```python
# Sample traces where judge confidence < 0.7
uncertain = [t for t in traces if t['judge_confidence'] < 0.7]
sample = random.sample(uncertain, min(200, len(uncertain)))
```

---

## Inter-Annotator Agreement

### Why It Matters

**Inconsistent annotations = unreliable ground truth**

If two annotators disagree frequently:
- Criteria are vague
- Task is too subjective
- Need clearer examples

### Measuring Agreement

**Cohen's Kappa:**
```
κ = (P_observed - P_expected) / (1 - P_expected)

κ > 0.80: Excellent agreement
κ 0.60-0.80: Good agreement
κ < 0.60: Poor agreement (refine criteria!)
```

**Simple Agreement Rate:**
```
Agreement = Matching labels / Total labels
```

### Example Calculation

**Scenario:** 2 annotators label 20 traces

| Trace | Annotator A | Annotator B | Match? |
|-------|-------------|-------------|--------|
| 1     | PASS        | PASS        | ✓      |
| 2     | FAIL        | FAIL        | ✓      |
| 3     | PASS        | FAIL        | ✗      |
| ...   | ...         | ...         | ...    |
| 20    | PASS        | PASS        | ✓      |

**Agreement:** 17/20 = 85%

**Interpretation:**
- 85% is good (≥80%)
- Review the 3 disagreements
- Clarify criteria for those cases

---

## Common Pitfalls

### Task Design Pitfalls

**1. Vague Criteria**
```
❌ Bad: "Is this response good?"
✅ Good: "Does the response answer the user's question with substantiated facts?"
```

**2. No Examples**
```
❌ Bad: Instructions only
✅ Good: Instructions + 5 annotated examples
```

**3. Too Many Options**
```
❌ Bad: 10 failure categories (confusing)
✅ Good: 3-5 categories with clear distinctions
```

### Annotation Pitfalls

**4. Fatigue**
```
❌ Bad: Annotate 200 traces in one sitting
✅ Good: 50 traces per session, 4 sessions over 2 weeks
```

**5. No Validation**
```
❌ Bad: Trust annotations without checking
✅ Good: Calculate inter-annotator agreement on 20% sample
```

**6. Confirmation Bias**
```
❌ Bad: Annotator knows automated label, confirms it
✅ Good: Blind annotation (hide automated labels)
```

---

## Integration with Automated Evaluation

### Feedback Loop

```
Manual Inspection → Identify Patterns → Build Automated Detector →
Validate with Manual Spot-Checks → Deploy to Production →
Edge Cases Flagged → Manual Review → Update Detector
```

**Example: Substantiation Evaluation**

1. **Manual:** Label 200 conversations for substantiation
2. **Automated:** Train LLM-as-Judge on labels
3. **Validation:** Manually review 30 judge predictions
4. **Production:** Apply judge to 10,000 logs
5. **Feedback:** Manual review of low-confidence cases
6. **Iteration:** Update judge prompt based on manual findings

---

## Key Takeaways

- ✅ **Manual inspection is essential for edge cases and ground truth** - Cannot be fully replaced by automation
- ✅ **Define clear criteria before annotating** - Vague tasks lead to inconsistent labels
- ✅ **Use sampling strategically** - Random for general quality, stratified for coverage, targeted for specific issues
- ✅ **Measure inter-annotator agreement** - κ ≥ 0.60 minimum, ≥ 0.80 ideal
- ✅ **Combine manual and automated** - Manual discovers, automated scales
- ✅ **Build feedback loops** - Manual reviews validate and improve automation

---

## Further Reading

- [CSV Conversion Tutorial](csv_conversion_tutorial.md) - Prepare traces for manual review
- [Labeling Tool Tutorial](labeling_tool_tutorial.md) - Build annotation interfaces
- [HW2: Error Analysis](../homeworks/hw2/error_analysis_concepts.md) - Open coding methodology
- [HW3: LLM-as-Judge](../homeworks/hw3/llm_judge_concepts.md) - Using manual labels for judge development

---

**Tutorial Status:** ✅ Complete
**Last Updated:** 2025-10-30
**Maintainer:** AI Evaluation Course Team
