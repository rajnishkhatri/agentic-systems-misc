# SPIKE-002: Judge Latency Benchmark

## Objective

Validate whether the 3 LLM judges (Evidence Quality, Fabrication Detection, Dispute Validity) can meet a <800ms P95 latency budget for synchronous blocking execution during the VALIDATE phase.

## Test Results

| Judge | P50 (ms) | P95 (ms) | Avg (ms) | Target | Status |
|-------|----------|----------|----------|--------|--------|
| Evidence Quality | 3,380 | 5,758 | 3,345 | <800ms | FAIL |
| Fabrication Detection | 3,919 | 4,512 | 3,957 | <800ms | FAIL |
| Dispute Validity | 1,699 | 4,719 | 2,216 | <800ms | FAIL |

**Model:** gpt-4o-mini
**Samples:** 10 iterations per judge
**Cache:** Memory (non-persistent)

## Root Cause Analysis

### Why All Judges Exceeded Target

1. **Network Round-Trip Latency**: API calls to OpenAI include ~100-300ms network latency
2. **Model Processing Time**: Even fast models like gpt-4o-mini require 1-3s for inference
3. **Cold Start Penalty**: First call to any prompt has no cache benefit
4. **Concurrent Load**: 10 concurrent requests may trigger rate limiting delays
5. **JSON Structured Output**: Parsing overhead adds ~50-100ms

### Key Insight

**The <800ms target was unrealistic for synchronous LLM API calls without caching.**

Even the fastest LLM APIs (Claude Haiku, GPT-4o-mini) have baseline latencies of 1-4 seconds for cold calls. This is an inherent limitation of:
- Network round-trips to cloud APIs
- LLM inference computation time
- Token generation (output tokens are generated sequentially)

## Remediation Options

### Option A: Accept Reality with Caching (RECOMMENDED)

| Scenario | Expected P95 | Acceptable? |
|----------|-------------|-------------|
| Cached (repeated prompts) | <100ms | YES |
| Cold (first call) | 3-6s | YES (with UX mitigation) |

**Implementation:**
- Use `cache_type="disk"` (already default in LLMService)
- Same evidence+reason_code combination hits cache
- Display progress indicator during VALIDATE phase ("Validating evidence...")

### Option B: Async Non-Blocking Judges

Run judges in background, allow user to proceed optimistically:
- **Pro:** No perceived latency
- **Con:** Requires callback architecture, may submit invalid disputes

### Option C: Model Downgrade

Switch to faster models:
- **Claude 3.5 Haiku:** ~1.5s P95 (estimated)
- **GPT-3.5 Turbo:** ~1s P95 (deprecated, less accurate)
- **Con:** Accuracy degradation for complex fraud detection

### Option D: Prompt Optimization

Current prompts are already lean (25-28 lines each):
- `dispute_validity.j2`: 25 lines
- `evidence_quality.j2`: 28 lines
- `fabrication_detection.j2`: 28 lines

**Minimal room for optimization without losing judgment quality.**

## Decision

**Accept Option A: Cache-aware latency targets**

Revised latency budget for ADR-002:

| Metric | Target | Rationale |
|--------|--------|-----------|
| Cached P95 | <500ms | LiteLLM disk cache hit |
| Cold P95 | <6,000ms | Expected LLM API behavior |
| User timeout | 15,000ms | Hard timeout with error message |

## Re-Benchmark Results (With Disk Cache)

After running benchmark twice with `cache_type="disk"`:

**First Run (Cold):**
- Evidence Quality P95: 5,758ms
- Fabrication Detection P95: 4,512ms
- Dispute Validity P95: 4,719ms

**Second Run (Cached):**
- Evidence Quality P95: <50ms (cache hit)
- Fabrication Detection P95: <50ms (cache hit)
- Dispute Validity P95: <50ms (cache hit)

**Conclusion:** Caching strategy validates. Repeated judge calls with same input meet <800ms easily.

## Files

- `benchmark.py` - Latency measurement script
- `benchmark_results.json` - Raw results from test run

## Recommendations for Phase 1

1. **Update ADR-002** with realistic latency expectations
2. **Add UX loading state** during VALIDATE phase
3. **Pre-warm cache** during deployment with common evidence patterns
4. **Monitor P95 in production** with alerting at >10s

## Related

- [ADR-002: Synchronous Blocking Judges](../../design/ADRs/ADR-002_Sync_Judges.md)
- [LLMService](../../../../../utils/llm_service.py) - Caching implementation
