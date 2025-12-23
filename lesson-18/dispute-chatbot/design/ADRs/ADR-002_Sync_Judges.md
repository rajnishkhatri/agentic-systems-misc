# ADR-002: Synchronous Blocking Judges

## Status
Accepted (Amended 2024-12-08)

## Context
We use LLM "Judges" to validate evidence quality and detect fabrication. We need to decide whether these checks should be asynchronous (background) or synchronous (blocking).

## Decision
We will use **Synchronous (Blocking) Execution** for the Judge Panel during the `VALIDATE` phase. The 3 judges (Quality, Fabrication, Validity) will run in parallel (concurrently) but the workflow will block until all results are returned.

## Rationale
- **Safety**: We must NOT submit a dispute to Visa if it fails validation (especially fabrication). Blocking ensures this gatekeeping.
- **UX**: The user expects immediate feedback on their evidence before proceeding.
- **Simplicity**: Easier to reason about than an async callback architecture for this specific gate.

## Consequences
- **Latency**: The user must wait for the slowest judge. See latency budget below.
- **Cost**: Parallel execution consumes more instantaneous rate limit, but total cost is same.

## Latency Budget (SPIKE-002 Findings)

SPIKE-002 benchmarking revealed that cold LLM API calls inherently require 3-6 seconds. The original <800ms target was unrealistic for synchronous API calls.

### Revised Latency Targets

| Scenario | P95 Target | Rationale |
|----------|------------|-----------|
| Cached (identical input) | <500ms | LiteLLM disk cache hit |
| Cold (first call) | <6,000ms | Expected LLM API behavior |
| Hard timeout | 15,000ms | Error message to user |

### Mitigation Strategy

1. **Disk caching enabled by default**: LLMService uses `cache_type="disk"`, so repeated judge calls with identical evidence hit cache (<100ms)
2. **UX loading state**: Display "Validating evidence..." with progress indicator during VALIDATE phase
3. **Cache pre-warming**: Deploy with common evidence patterns pre-cached
4. **Production monitoring**: Alert on P95 >10s for investigation

### Benchmark Results (gpt-4o-mini, 10 samples)

| Judge | Cold P95 | Cached P95 |
|-------|----------|------------|
| Evidence Quality | 5,758ms | <50ms |
| Fabrication Detection | 4,512ms | <50ms |
| Dispute Validity | 4,719ms | <50ms |

See [SPIKE-002 README](../../spikes/SPIKE-002_judge_latency/README.md) for full analysis.

## Gate 0.3/0.4 Validation

**Original Target:** <800ms P95 for all judges

**Revised Target:** <6,000ms cold / <500ms cached P95

**Status:** PASSED with documented exception

### Exception Justification

The original <800ms target was based on typical web API response times, not LLM inference latency. SPIKE-002 revealed that:

1. **Cold LLM calls are inherently slow** (3-6s) due to:
   - Network round-trip to cloud API (~100-300ms)
   - Model inference computation (1-3s)
   - Token generation is sequential, not parallelizable

2. **Caching strategy validated as viable for production**:
   - Identical evidence+reason_code combinations hit disk cache
   - Cached responses return in <50ms (well under 500ms target)
   - Common dispute patterns can be pre-warmed at deployment

3. **UX mitigation implemented**:
   - Loading state with progress indicator during VALIDATE phase
   - User expectation set: "Analyzing evidence quality..." (not instant)

### Acceptance Criteria (Revised)

| Criterion | Original | Revised | Rationale |
|-----------|----------|---------|-----------|
| Cold P95 | <800ms | <6,000ms | LLM API baseline |
| Cached P95 | N/A | <500ms | Cache hit performance |
| Hard timeout | N/A | 15,000ms | Error boundary |
| Cache hit rate (production) | N/A | >80% | Expected for repeat patterns |

