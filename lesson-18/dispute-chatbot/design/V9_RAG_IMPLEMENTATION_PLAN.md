# V9 Classification Pipeline Implementation Plan

## Overview
Evolve V8-RAG → V9-RAG-Enhanced with improved observability, resilience, and confidence calibration.

---

## Task Breakdown

### Phase 1: Core Infrastructure (TDD)

#### Task 1.1: Add RAG Feature Flag & Configuration
**Files:** `classify_v9_rag.py`, `.env.example`
```python
# New constants at module level
RAG_ENABLED = os.getenv("CLASSIFY_RAG_ENABLED", "true").lower() == "true"
RAG_TOP_K = int(os.getenv("CLASSIFY_RAG_TOP_K", "3"))
RAG_SIMILARITY_THRESHOLD = float(os.getenv("CLASSIFY_RAG_THRESHOLD", "0.4"))
RAG_HIGH_CONFIDENCE_THRESHOLD = float(os.getenv("CLASSIFY_RAG_HIGH_CONFIDENCE", "0.85"))
```
**Tests:** `test_should_respect_rag_enabled_flag()`, `test_should_use_configurable_thresholds()`

#### Task 1.2: Graceful RAG Fallback
**Files:** `classify_v9_rag.py`
```python
def get_rag_retriever_safe() -> Optional[RagRetriever]:
    """Get retriever with graceful fallback."""
    if not RAG_ENABLED:
        logger.info("RAG disabled via CLASSIFY_RAG_ENABLED=false")
        return None
    try:
        return get_rag_retriever()
    except FileNotFoundError as e:
        logger.warning(f"RAG unavailable (vector store missing): {e}")
        return None
    except Exception as e:
        logger.error(f"RAG initialization failed: {e}")
        return None
```
**Tests:** `test_should_continue_without_rag_when_store_missing()`, `test_should_disable_rag_via_env_var()`

---

### Phase 2: RAG Metrics & Observability

#### Task 2.1: Add RAGMetrics Dataclass
**Files:** `classify_v9_rag.py`
```python
class RAGMetrics(BaseModel):
    """Metrics about RAG retrieval for observability."""
    enabled: bool = Field(description="Whether RAG was enabled")
    precedents_retrieved: int = Field(default=0, description="Number of precedents found")
    top_similarity: float = Field(default=0.0, description="Highest similarity score")
    avg_similarity: float = Field(default=0.0, description="Average similarity of retrieved")
    precedent_categories: List[str] = Field(default_factory=list, description="Categories from precedents")
    retrieval_time_ms: float = Field(default=0.0, description="Time spent in retrieval")
    high_confidence_match: bool = Field(default=False, description="Has match above high threshold")
```
**Tests:** `test_should_compute_rag_metrics_correctly()`, `test_should_handle_empty_retrieval()`

#### Task 2.2: Integrate RAGMetrics into Output
**Files:** `classify_v9_rag.py`
- Add `rag_metrics` key to return dictionary
- Track retrieval time with `time.perf_counter()`
- Compute aggregates from retrieved examples

**Tests:** `test_should_include_rag_metrics_in_output()`, `test_should_track_retrieval_latency()`

---

### Phase 3: Confidence Calibration

#### Task 3.1: Implement Confidence Calibration Function
**Files:** `classify_v9_rag.py`
```python
def calibrate_confidence(
    base_confidence: float,
    rag_metrics: RAGMetrics,
    precedent_agreement: bool  # Does output match top precedent's category?
) -> tuple[float, str]:
    """Calibrate confidence based on RAG signals.

    Returns:
        (adjusted_confidence, adjustment_reason)
    """
    adjustment = 0.0
    reasons = []

    # Boost for high-similarity precedent agreement
    if rag_metrics.high_confidence_match and precedent_agreement:
        adjustment += 0.05
        reasons.append(f"+0.05: High-similarity precedent agrees")

    # Penalty for high-similarity precedent disagreement
    if rag_metrics.high_confidence_match and not precedent_agreement:
        adjustment -= 0.10
        reasons.append(f"-0.10: High-similarity precedent disagrees (review recommended)")

    # Boost for precedent consensus
    if len(set(rag_metrics.precedent_categories)) == 1 and rag_metrics.precedents_retrieved >= 2:
        adjustment += 0.03
        reasons.append(f"+0.03: All precedents agree on category")

    adjusted = min(1.0, max(0.0, base_confidence + adjustment))
    return adjusted, "; ".join(reasons) if reasons else "No adjustment"
```
**Tests:**
- `test_should_boost_confidence_when_precedent_agrees()`
- `test_should_penalize_confidence_when_precedent_disagrees()`
- `test_should_boost_for_unanimous_precedents()`
- `test_should_clamp_confidence_to_valid_range()`

#### Task 3.2: Apply Calibration in Main Flow
**Files:** `classify_v9_rag.py`
- After classification, check if output matches top precedent
- Apply calibration and record adjustment reason
- Add `confidence_adjustment` and `confidence_adjustment_reason` to output

---

### Phase 4: Precedent Diversity Check

#### Task 4.1: Implement Diversity Scorer
**Files:** `classify_v9_rag.py`
```python
def check_precedent_diversity(examples: List[Dict]) -> Dict[str, Any]:
    """Check if precedents are diverse or potentially biased.

    Returns:
        {
            "is_diverse": bool,
            "unique_categories": int,
            "warning": Optional[str]
        }
    """
    if len(examples) < 2:
        return {"is_diverse": True, "unique_categories": len(examples), "warning": None}

    categories = [e.get("category") for e in examples]
    unique = set(categories)

    # Warning if all precedents have same category but low similarity spread
    similarities = [e.get("similarity_score", 0) for e in examples]
    spread = max(similarities) - min(similarities) if similarities else 0

    warning = None
    if len(unique) == 1 and spread < 0.1:
        warning = "All precedents similar and same category - potential bias"

    return {
        "is_diverse": len(unique) > 1 or spread >= 0.1,
        "unique_categories": len(unique),
        "similarity_spread": spread,
        "warning": warning
    }
```
**Tests:** `test_should_detect_low_diversity_precedents()`, `test_should_accept_diverse_precedents()`

---

### Phase 5: Enhanced Prompt (V9)

#### Task 5.1: Create V9 Prompt Template
**Files:** `prompts/DisputeClassifier_identify_category_v9_rag.j2`
- Add precedent diversity warning section
- Add explicit instruction for disagreement handling
- Add confidence calibration guidance

#### Task 5.2: Update CategoryResultV9Rag Model
**Files:** `classify_v9_rag.py`
- Add optional `precedent_override_applied: bool` field
- Add optional `precedent_disagreement_note: str` field

---

### Phase 6: Evaluation Script Updates

#### Task 6.1: Update Trace Script for V9 Metrics
**Files:** `scripts/evaluate_v9_rag_trace.py`
- Include RAG metrics in trace output
- Add aggregate RAG statistics to summary

#### Task 6.2: Create V9 Comparison Report
**Files:** `scripts/generate_report_v9_vs_v8.py`
- Compare V8 vs V9 accuracy
- Analyze confidence calibration impact
- Report RAG hit rates and correlation with accuracy

---

### Phase 7: Tests & Documentation

#### Task 7.1: Comprehensive Test Suite
**Files:** `tests/test_phases_classify_v9_rag.py`
- ~15-20 TDD tests covering all new functionality
- Mock-based tests (no LLM calls)
- Edge case coverage

#### Task 7.2: Update .env.example
**Files:** `lesson-18/dispute-chatbot/.env.example`
```bash
# V9 RAG Configuration
CLASSIFY_RAG_ENABLED=true
CLASSIFY_RAG_TOP_K=3
CLASSIFY_RAG_THRESHOLD=0.4
CLASSIFY_RAG_HIGH_CONFIDENCE=0.85
```

---

## File Summary

| File | Action | Description |
|------|--------|-------------|
| `backend/phases/classify_v9_rag.py` | CREATE | New V9 handler with all improvements |
| `prompts/DisputeClassifier_identify_category_v9_rag.j2` | CREATE | V9 prompt with diversity guidance |
| `tests/test_phases_classify_v9_rag.py` | CREATE | TDD test suite (~18 tests) |
| `scripts/evaluate_v9_rag_trace.py` | CREATE | V9 evaluation script |
| `scripts/generate_report_v9_vs_v8.py` | CREATE | Comparison report |
| `.env.example` | EDIT | Add V9 config vars |

---

## Success Criteria

1. RAG can be disabled via env var without errors
2. Missing vector store doesn't crash classification
3. Output includes `rag_metrics` with 7 fields
4. Confidence calibration adjusts score based on precedent agreement
5. Low-diversity precedents trigger warning
6. All tests pass (`pytest tests/test_phases_classify_v9_rag.py -v`)
7. V9 accuracy >= V8 accuracy on golden set

---

## Estimated Effort

| Phase | Tasks | Est. Time |
|-------|-------|-----------|
| 1. Infrastructure | 2 | 30 min |
| 2. RAG Metrics | 2 | 45 min |
| 3. Confidence Calibration | 2 | 45 min |
| 4. Diversity Check | 1 | 20 min |
| 5. Enhanced Prompt | 2 | 30 min |
| 6. Evaluation Scripts | 2 | 40 min |
| 7. Tests & Docs | 2 | 30 min |
| **Total** | **13 tasks** | **~4 hours** |

---

## Risks & Mitigations

| Risk | Mitigation |
|------|------------|
| Confidence calibration over-adjusts | Cap adjustments at ±0.10 |
| RAG fallback hides critical errors | Log at WARNING level, include in output |
| V9 slower than V8 | Track `retrieval_time_ms`, set timeout |
| Prompt too long with diversity warning | Make section conditional |

---

## V8 Reflection Insights (Source)

This plan was derived from `/reflect` analysis of `classify_v8_rag.py`:

**What Worked in V8:**
- Incremental evolution from V7-Hybrid
- Clean RAG integration with lazy singleton
- Precedent Override Rule (Rule 0) in prompt
- Defensive validators with aliases

**What Needed Improvement:**
- Silent fallback on RAG failure
- No confidence calibration based on RAG
- Hardcoded RAG parameters
- Missing observability for RAG hits
- Vector store dependency not graceful

---

*Generated: 2025-12-20*
*Source: /reflect on classify_v8_rag.py*
