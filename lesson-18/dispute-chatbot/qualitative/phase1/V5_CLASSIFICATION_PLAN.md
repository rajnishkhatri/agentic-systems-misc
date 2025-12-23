# Dispute Classification V5-ToT Implementation Plan

## Executive Summary

This plan outlines the creation of V5-ToT (Tree-of-Thought) classification system based on:
1. Comparative analysis of V2, V3, and V4 trace reports
2. Prompt engineering rules from `ai-dev-tasks/prompt-engineering-rules.md`
3. Tree-of-Thought reasoning for improved ambiguous case handling

V5-ToT addresses remaining failure modes (especially ambiguous persona at 45%) by:
- Switching to Anthropic Claude
- Adding Tree-of-Thought with 3 independent analysis branches
- Applying positive framing and priority rules with rationale

**Status: ✅ IMPLEMENTED** (2024-12-14)

---

## Performance Baseline (from Reflection)

| Version | Pass Rate | Key Limitation |
|---------|-----------|----------------|
| **V2**  | 37.0% (112/303) | Ambiguous rule priority |
| **V3 Fix** | 35.0% (7/20) | Still parsed "didn't authorize" as fraud |
| **V4**  | 56.0% (28/50) | Ambiguous persona only at 45% |

### V4's Winning Strategy (preserved in V5-ToT)
- Two-tier classification: Existence vs Detail Dispute
- Critical rule: "High bill" overrides "didn't authorize"
- Few-shot examples matching exact failure modes

### V4's Gaps (addressed in V5-ToT)
1. **Ambiguous persona** still at 45% → ToT Branch C (Persona Analysis)
2. **No confidence calibration** → Branch agreement score + rationale
3. **Implicit reasoning** → Explicit 3-branch ToT with synthesis

---

## Prompt Engineering Rules Applied

### Rule 1: Positive Framing (Ask for Positives)
**Before (V4)**: "Did user deny participating entirely?"
**After (V5-ToT)**: "Does user acknowledge making this transaction?"

### Rule 2: Bolster with Reasons
**Before (V4)**: "If amount_mentioned=True, classify as general"
**After (V5-ToT)**: "If amount_mentioned=True, classify as general BECAUSE users who mention specific amounts are disputing charge details, not transaction existence."

### Rule 3: Avoid Absolutes
**Before (V4)**: "ALWAYS classify as general when amount mentioned"
**After (V5-ToT)**: Priority rules with exceptions noted

### Few-Shot Mitigations Applied
1. **Randomized order** - Prevent spurious pattern learning
2. **Distribution-matched** - 60% clear cases, 40% ambiguous (reflects real data)
3. **Format-only for clear cases** - Reduce token bloat

---

## V5-ToT Architecture: Tree-of-Thought

### Three Independent Analysis Branches

```
┌─────────────────────────────────────────────────────────────┐
│                    Dispute Description                       │
└─────────────────────────────────────────────────────────────┘
                              │
         ┌────────────────────┼────────────────────┐
         ▼                    ▼                    ▼
┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│    Branch A     │  │    Branch B     │  │    Branch C     │
│  Acknowledgment │  │   Complaint     │  │     Persona     │
│    Analysis     │  │   Specifics     │  │    Analysis     │
├─────────────────┤  ├─────────────────┤  ├─────────────────┤
│ acknowledged    │  │ amount          │  │ frustrated      │
│ denied          │  │ quality         │  │ confused        │
│ unclear         │  │ processing      │  │ accusatory      │
│                 │  │ unspecified     │  │ neutral         │
└─────────────────┘  └─────────────────┘  └─────────────────┘
         │                    │                    │
         └────────────────────┼────────────────────┘
                              ▼
              ┌─────────────────────────────────┐
              │      Branch Synthesis           │
              │  - Agreement Score (0.0-1.0)    │
              │  - Priority Rule Application    │
              │  - Conflict Detection           │
              └─────────────────────────────────┘
                              │
                              ▼
              ┌─────────────────────────────────┐
              │      Final Classification       │
              │  - Category                     │
              │  - Confidence + Rationale       │
              └─────────────────────────────────┘
```

### Priority Rules (with Rationale)

| Rule | Trigger | Action | Rationale |
|------|---------|--------|-----------|
| **Rule 1** | Branch B = "amount" | Override Branch A denial | Amount complaints prove transaction awareness |
| **Rule 2** | Branch B = "processing" | Classify by processing type | Processing complaints = acknowledged transactions |
| **Rule 3** | Branch A ↔ B conflict | Use Branch C as tiebreaker | Persona reveals true intent |
| **Rule 4** | Branch A = "unclear" + B = "unspecified" | Default to "unrecognized" | Insufficient info, not fraud assumption |

---

## Implementation (✅ Complete)

### Files Created

| File | Purpose | Status |
|------|---------|--------|
| `backend/phases/classify_v5_tot.py` | ToT classifier with 3-branch analysis | ✅ |
| `prompts/DisputeClassifier_identify_category_v5_tot.j2` | ToT prompt with positive framing | ✅ |
| `tests/test_phases_classify_v5_tot.py` | 46 TDD tests (all passing) | ✅ |

### Pydantic Models

```python
class BranchAResult(BaseModel):
    evidence_for_acknowledgment: List[str]
    evidence_against_acknowledgment: List[str]
    conclusion: str  # "acknowledged" | "denied" | "unclear"

class BranchBResult(BaseModel):
    complaint_type: str  # "amount" | "quality" | "processing" | "unspecified"
    evidence: List[str]

class BranchCResult(BaseModel):
    persona: str  # "frustrated" | "confused" | "accusatory" | "neutral"
    evidence: List[str]

class SynthesisResult(BaseModel):
    branch_agreement: float  # 0.0-1.0
    priority_rule_applied: Optional[str]
    reasoning: str

class CategoryResultV5ToT(BaseModel):
    branch_a: BranchAResult
    branch_b: BranchBResult
    branch_c: BranchCResult
    synthesis: SynthesisResult
    category: str
    confidence: float
    confidence_rationale: str
```

### Key Functions

- `classify_dispute_v5_tot(task, model)` - Main entry point
- `_identify_category_v5_tot(description, model)` - ToT classification
- `extract_branch_summary(result)` - Extract branch conclusions for logging
- `check_branch_conflict(result)` - Detect conflicts requiring priority rules

---

## Testing Results

```
46 passed in 1.92s
```

### Test Categories
- Branch validation tests (17 tests)
- Network identification tests (7 tests)
- Branch summary extraction tests (3 tests)
- Branch conflict detection tests (4 tests)
- Category identification tests (3 tests)
- Full pipeline tests (11 tests)
- Model configuration tests (1 test)

---

## Success Criteria

| Metric | V4 Baseline | V5-ToT Target | Status |
|--------|-------------|---------------|--------|
| Overall Correction Rate | 56% | >70% | 🔄 Pending evaluation |
| Ambiguous Persona | 45% | >65% | 🔄 Pending evaluation |
| Emotional Persona | 75% | Maintain >70% | 🔄 Pending evaluation |
| Confidence Calibration | N/A | ✅ Included | ✅ |
| Branch Audit Trail | N/A | 100% | ✅ |
| Conflict Detection | N/A | ✅ Included | ✅ |

---

## Next Steps

1. **Run golden set evaluation** with V5-ToT classifier
2. **Generate trace report** comparing V4 vs V5-ToT
3. **Analyze ambiguous persona correction rate** (target: >65%)
4. **Tune priority rules** based on failure analysis

---

## Usage

```python
from backend.phases.classify_v5_tot import classify_dispute_v5_tot

result = await classify_dispute_v5_tot({
    "dispute_id": "DIS-12345",
    "description": "WHY IS MY BILL SO HIGH?! I DIDN'T AUTHORIZE THIS!",
})

# Result includes:
# - category: "general"
# - branch_a_conclusion: "acknowledged"
# - branch_b_complaint: "amount"
# - branch_c_persona: "frustrated"
# - branch_agreement: 0.90
# - priority_rule_applied: "Rule 1: Specifics Override Denial"
# - classification_confidence: 0.92
# - confidence_rationale: "High agreement across branches"
# - branch_conflict: {"type": "denial_with_amount", "resolution": "amount_overrides_denial"}
```
