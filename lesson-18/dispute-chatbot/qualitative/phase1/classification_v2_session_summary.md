# Classification V2 Implementation Session Summary

**Date:** 2025-12-13
**Session Focus:** Improve reason code classification accuracy using Pólya framework analysis

---

## Problem Statement

- **V1 Accuracy:** 35% overall pass rate (303 test cases)
- **Key Failures:** Fine-grained code confusion (A01→F24, A08→A02, C04→C02, C14→P08)
- **Target:** 60%+ accuracy

### V1 → V2 Report Comparison (Prior Analysis)

| Metric | V1 | V2 (baseline) | Target |
|--------|-----|---------------|--------|
| Overall Pass Rate | 14.2% | 35.0% | 60%+ |
| Ambiguous Persona | 5.9% | 21.8% | 40%+ |
| Emotional Persona | 11.9% | 40.6% | 55%+ |
| Narrative Persona | 24.8% | 42.6% | 55%+ |

---

## Pólya Framework Analysis Applied

### Phase 1: UNDERSTAND
- 101 reason codes across 6 networks
- 8 unified categories (general has 45 codes - too broad)
- `network_family` field underutilized in catalog

### Phase 2: PLAN
- Root cause: LLM conflates semantically similar but distinct codes
- Strategy: Decomposition + Keyword disambiguation + Few-shot examples

### Phase 3: TASKS (Implemented)
1. ✅ Add negative examples to category prompt
2. ✅ Add few-shot examples to code selection prompt
3. ✅ Create keyword disambiguation map
4. ✅ Add network_family as intermediate signal
5. ✅ Create classify_v2.py with all improvements
6. ✅ Write and pass 29 unit tests

---

## Files Created

| File | Description |
|------|-------------|
| `prompts/DisputeClassifier_identify_category_v2.j2` | Category prompt with IS/IS NOT contrastive examples |
| `prompts/DisputeClassifier_select_code_v2.j2` | Code selection with few-shot examples for confusable pairs |
| `backend/adapters/keyword_hints.json` | Disambiguation rules mapping keywords to preferred codes |
| `backend/phases/classify_v2.py` | Enhanced classifier integrating all improvements |
| `tests/test_phases_classify_v2.py` | 29 unit tests (all passing) |

---

## Key Changes in V2

### 1. Category Prompt (IS/IS NOT Examples)

```
1. **fraudulent**: The cardholder claims they did not participate in or authorize the transaction.
   - IS: "I didn't make this purchase", "My card was stolen"
   - IS NOT: "They charged me more than I agreed to" (→ general)
```

### 2. Code Selection Prompt (Few-Shot Examples)

```
**Authorization vs Fraud:**
- "Card was DECLINED at checkout" → A08/11.2 (authorization)
- "I DIDN'T MAKE this purchase" → F24/10.4 (fraud)
```

### 3. Keyword Disambiguation Map

```json
{
  "prefer_authorization": {
    "keywords": ["declined", "wouldn't go through", "refused"],
    "codes": {"amex": "A08", "visa": "11.2"}
  },
  "prefer_fraud": {
    "keywords": ["stolen", "didn't make", "someone else"],
    "codes": {"amex": "F24", "visa": "10.4"}
  }
}
```

### 4. Network Family Detection

New intermediate signal from keywords:
- `authorization`: declined, expired, rejected
- `fraud`: stolen, unauthorized, didn't make
- `cardholder_disputes`: returned, cancelled, refund
- `processing_errors`: duplicate, wrong amount, twice

### 5. V2 Response Schema

```python
{
    "reason_code": "A08",
    "network": "amex",
    "category": "general",
    "network_family": "authorization",  # NEW
    "is_fraud": False,
    "deadline": "2023-01-15",
    "classification_confidence": 0.95,
    "classification_reasoning": "...",
    "keyword_hint_used": True,  # NEW
    "classifier_version": "2.0.0"  # NEW
}
```

---

## Test Results

```
tests/test_phases_classify_v2.py: 29 passed in 1.38s
```

Test coverage includes:
- Network identification (5 tests)
- Network family detection (5 tests)
- Keyword code hints (7 tests)
- Input validation (3 tests)
- Full classification flow (8 tests)
- Hints file loading (1 test)

---

## Next Steps for Next Session

1. **Integration:** Update orchestrator to use `classify_dispute_v2()` instead of V1
2. **Live Testing:** Run V2 classifier against the 303 natural language test cases
3. **Generate V3 Report:** Create `natural_language_report_v3.html` with V2 classifier
4. **Measure Improvement:** Compare V2 → V3 accuracy gains
5. **Iterate:** If <60%, consider:
   - Two-stage selection for `general` category (45 codes)
   - Confidence-based fallback with clarifying questions
   - Additional keyword patterns for remaining failures

---

## Reference Files

- V1 Report: `qualitative/phase1/natural_language_report.html`
- V2 Report: `qualitative/phase1/natural_language_report_v2.html`
- Reason Codes: `lesson-18/dispute-schema/REASON_CODES_CATALOG.md`
- Pólya Framework: `ai-dev-tasks/polya-analysis.md`
