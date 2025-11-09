# Qualitative Methods Family

**When to use this family**: Initial exploration, unknown failure modes, building labeled datasets, subjective evaluation

---

## Overview

Qualitative methods prioritize **understanding patterns through human observation** rather than numeric metrics. Use these techniques when:
- ✅ Failure modes are unknown (need exploration)
- ✅ Building initial evaluation datasets
- ✅ Criteria are subjective or ill-defined
- ✅ Need rich contextual understanding

---

## Techniques in This Family

### 1. Prompt Engineering (HW1)
**Purpose**: Define bot behavior through system instructions

**Workflow**:
```
Define role → Set rules → Control output → Add safety → Test → Iterate
```

**Key principle**: Balance specificity with flexibility. Too vague → unpredictable. Too restrictive → limited usefulness.

---

### 2. Query Diversity (HW1)
**Purpose**: Systematic test coverage across dimensions

**Workflow**:
```
Identify dimensions → List values → Select combinations → Write queries
```

**Example dimensions**:
- Domain-specific: cuisine, dietary restrictions, meal type
- Universal: complexity, edge cases, ambiguity level

---

### 3. Open Coding (HW2)
**Purpose**: Initial pattern discovery without preconceptions

**Workflow**:
```
Review traces → Label patterns → Take notes → Look for themes
```

**Key principle** (from Grounded Theory): Let patterns **emerge** from data, don't force observations into predetermined categories.

**Time**: 5-10 minutes per trace, 20-30 traces recommended

---

### 4. Axial Coding (HW2)
**Purpose**: Group open codes into structured categories

**Workflow**:
```
Review open codes → Identify themes → Create hierarchy → Define relationships
```

**Target**: 3-7 top-level categories (fewer = clearer, more = diluted focus)

---

### 5. Failure Taxonomy Construction (HW2)
**Purpose**: Formal documentation of failure modes

**Template**:
```markdown
### Failure Mode: [Title]
**Definition**: [Testable one-sentence description]
**Examples**:
1. [Real example from trace X]
2. [Additional example]
**Frequency**: [Common/Occasional/Rare]
**Severity**: [High/Medium/Low]
```

**Quality check**: Can a new team member read the definition and correctly classify a new trace?

---

### 6. Manual Annotation (Lesson 7)
**Purpose**: Human labeling for subjective or safety-critical tasks

**Best practices**:
- Define criteria in 1-page guide
- Provide 3-5 example annotations
- Track uncertain cases separately
- Measure inter-annotator agreement (if multiple people)

**When to stop**: Use manual annotation only for <100 examples. For larger scale, transition to LLM-as-Judge (HW3).

---

## Workflow: Qualitative to Quantitative

```
Manual Exploration (Open/Axial Coding)
         ↓
Structured Taxonomy (Failure Modes)
         ↓
Manual Labeling (Small dataset)
         ↓
LLM-as-Judge Development (Scale automation)
         ↓
Production Monitoring (Quantitative metrics)
```

---

## Common Pitfalls

### ❌ Premature Quantification
**Problem**: Jumping to metrics before understanding failure modes
**Solution**: Spend 2-3 hours on open coding first

### ❌ Confirmation Bias
**Problem**: Only noting failures that confirm initial hypothesis
**Solution**: Review successful traces too, look for unexpected patterns

### ❌ Inconsistent Granularity
**Problem**: Some codes are very specific ("honey in vegan recipe"), others very broad ("bad response")
**Solution**: Aim for consistent level of abstraction (axial coding helps)

### ❌ Over-categorization
**Problem**: Creating 20+ failure modes (too many to act on)
**Solution**: Target 3-7 top-level categories with sub-categories if needed

---

## Success Metrics

**You've succeeded with qualitative methods when**:
- ✅ Failure taxonomy clearly explains 80%+ of observed failures
- ✅ Team members agree on failure mode classifications (inter-rater reliability >80%)
- ✅ Can prioritize which failure modes to fix based on frequency/severity
- ✅ Ready to transition to automated evaluation (quantitative methods)

---

## Integration with Other Families

### → Quantitative Metrics
After building failure taxonomy, measure **frequency** of each failure mode numerically

### → Automated Evaluation
Use labeled examples from manual annotation as ground truth for LLM-as-Judge (HW3)

### → Debugging Methods
Use qualitative analysis (open coding) to interpret patterns from transition matrices (HW5)

---

## Real-World Example

**Scenario**: Recipe chatbot producing incorrect responses

### Phase 1: Open Coding (2 hours)
- Review 30 conversation traces
- Identify patterns:
  - "Suggested honey for vegan recipes" (8 traces)
  - "15-ingredient recipes for 'quick meals'" (5 traces)
  - "Ignored dietary restrictions" (12 traces)
  - "Provided irrelevant cuisine" (3 traces)

### Phase 2: Axial Coding (1 hour)
- Group into categories:
  - **Dietary Violations** (20 traces)
    - Subcategory: Vegan violations (8)
    - Subcategory: Gluten-free violations (6)
    - Subcategory: Other (6)
  - **Intent Misalignment** (5 traces)
  - **Retrieval Failures** (3 traces)

### Phase 3: Failure Taxonomy (1 hour)
```markdown
### Failure Mode: Dietary Restriction Violations

**Definition**: Bot suggests ingredients or recipes that violate user's stated dietary restrictions.

**Examples**:
1. User: "vegan pasta recipe" → Bot: "Try this pasta carbonara with eggs and bacon" (Trace #7)
2. User: "gluten-free bread" → Bot: "Here's a recipe using wheat flour" (Trace #19)

**Frequency**: Common (20 out of 30 traces)
**Severity**: High (violates user's core requirements)
**Proposed Fix**: Add dietary validation step before responding
```

### Phase 4: Transition to Automation
- Manually label 150 traces for dietary adherence (pass/fail)
- Build LLM-as-Judge to automate evaluation (HW3)
- Generate synthetic queries targeting dietary edge cases (HW2)

---

## When to Move Beyond Qualitative Methods

**Stay qualitative if**:
- Exploring new failure modes
- Evaluation dataset <50 examples
- Criteria are highly subjective

**Transition to quantitative if**:
- Failure modes are well-understood
- Have 100+ labeled examples
- Criteria are objective
- Need production-scale monitoring

---

## Further Reading

**From tutorials**:
- [HW1: Prompt Engineering & Query Diversity](../../homeworks/hw1/TUTORIAL_INDEX.md)
- [HW2: Error Analysis (Open/Axial Coding)](../../homeworks/hw2/TUTORIAL_INDEX.md)
- [Lesson 7: Manual Annotation Workflows](../../lesson-7/TUTORIAL_INDEX.md)

**External references**:
- Grounded Theory (Glaser & Strauss, 1967)
- Qualitative Data Analysis in Software Engineering
