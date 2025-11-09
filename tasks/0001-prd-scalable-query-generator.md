# PRD: Scalable Recipe Query Test Data Generator

## Introduction/Overview

The current `hw2_assignment.py` script generates test query data for recipe chatbot evaluation by using LLMs to create dimension tuples and natural language queries. While functionally correct, the script is not production-ready for scalable, distributed deployment.

**Problem Statement**: The current implementation suffers from:
- High API costs due to lack of caching (regenerates identical data on every run)
- Poor reliability (~5-10% failure rate from brittle string parsing)
- Slow response times (4-6 seconds for operations that could take <200ms)
- No resilience to API failures (single failure crashes entire workflow)
- Limited observability (print statements only, no structured logging)

**Goal**: Refactor the query generator into a production-ready service optimized for **cost efficiency** while maintaining fast response times and supporting 10-50 concurrent users in a cloud-native environment.

## Goals

1. **Cost Reduction**: Reduce LLM API costs by >90% through intelligent caching
2. **Fast Response Times**: Achieve <200ms response time for cached queries, <3s for cache misses
3. **Reliability**: Reduce error rate from 5-10% to <0.1% through robust parsing and retry logic
4. **Observability**: Enable debugging and monitoring with structured logging
5. **Scalability**: Support 10-50 concurrent users with horizontal scaling capability
6. **Maintainability**: Clean, typed, testable code following project TDD standards

## User Stories

### US-1: Developer Generates Test Queries (Cached Path)
**As a** QA engineer
**I want to** generate test query datasets on-demand
**So that** I can quickly run evaluation benchmarks without waiting or incurring costs

**Acceptance Criteria**:
- First request generates fresh data (2-3s acceptable)
- Subsequent requests return cached results in <200ms
- Cache remains valid for configurable duration (default: 1 hour)

### US-2: Developer Handles API Failures Gracefully
**As a** developer running test generation
**I want** the system to retry failed LLM calls automatically
**So that** transient API issues don't require manual intervention

**Acceptance Criteria**:
- Automatic retry with exponential backoff (3 attempts)
- Clear error messages for permanent failures
- Success rate >99.9% under normal conditions

### US-3: DevOps Monitors System Health
**As a** DevOps engineer
**I want** structured logs with request traces
**So that** I can debug issues and monitor costs in production

**Acceptance Criteria**:
- JSON-formatted logs with correlation IDs
- Log entries include: duration, model used, token count, cache hit/miss
- Errors include full context (request ID, stack traces)

### US-4: Developer Validates Generated Data Quality
**As a** developer
**I want** guaranteed valid output format from LLM responses
**So that** I don't waste time debugging parsing failures

**Acceptance Criteria**:
- LLM returns structured JSON (enforced via `response_format`)
- Pydantic validation ensures all required fields present
- Invalid responses trigger retry with adjusted prompt

## Functional Requirements

### FR-1: Redis-Based Caching Layer
1. The system **must** cache LLM responses in Redis with configurable TTL
2. Cache keys **must** be deterministic hashes of prompts (SHA-256)
3. The system **must** support cache invalidation via manual command
4. The system **must** log cache hit/miss metrics for monitoring

### FR-2: Structured LLM Output with Validation
1. LLM calls **must** use `response_format={"type": "json_object"}` to enforce JSON output
2. The system **must** define Pydantic models for `DimensionTuple` and `NaturalLanguageQuery`
3. The system **must** validate all LLM responses against Pydantic schemas before use
4. Invalid responses **must** trigger retry with enhanced prompt guidance

### FR-3: Retry Logic with Exponential Backoff
1. All LLM API calls **must** implement retry logic with:
   - Maximum 3 attempts
   - Exponential backoff: 2s, 4s, 8s
   - Jitter to prevent thundering herd
2. The system **must** log each retry attempt with reason
3. After 3 failures, the system **must** raise descriptive exception

### FR-4: Rate Limiting and Timeout Protection
1. The system **must** implement rate limiting at 500 requests/minute (cloud-provider safe)
2. All LLM calls **must** have 15-second timeout (LiteLLM level)
3. Async operations **must** have 20-second timeout (asyncio level)
4. Rate limit exhaustion **must** return HTTP 429 with retry-after header

### FR-5: Structured Logging with Correlation
1. The system **must** use `structlog` for JSON-formatted logging
2. All requests **must** generate unique correlation ID (UUID)
3. Logs **must** include:
   - Timestamp, log level, correlation ID
   - Operation name, duration (milliseconds)
   - Model name, token count (for LLM calls)
   - Cache hit/miss status
   - Error details (for failures)
4. The system **must** support log level configuration via environment variable

### FR-6: Configuration Management
1. All configuration **must** be externalized via environment variables
2. The system **must** use Pydantic Settings for type-safe config
3. Required config parameters:
   - `MODEL_NAME`: LLM model to use (default: `gpt-4o-mini`)
   - `REDIS_URL`: Redis connection string
   - `CACHE_TTL_SECONDS`: Cache expiration (default: 3600)
   - `RATE_LIMIT_PER_MINUTE`: API rate limit (default: 500)
   - `LLM_TIMEOUT_SECONDS`: LLM call timeout (default: 15.0)
   - `LOG_LEVEL`: Logging verbosity (default: INFO)
4. The system **must** provide `.env.example` with documentation

### FR-7: Parallel Processing for Batch Operations
1. When generating multiple query batches, the system **must** process them in parallel using `asyncio.gather`
2. Batch size **must** be configurable (default: 5 tuples per batch)
3. The system **must** limit concurrent LLM calls to respect rate limits

### FR-8: Type Safety and Defensive Programming
1. All functions **must** include type hints for parameters and return values
2. Functions **must** validate inputs at runtime (guard clauses)
3. Functions **must** raise descriptive exceptions for invalid inputs:
   - `TypeError` for type mismatches
   - `ValueError` for invalid values
4. The system **must** follow the 5-step defensive function pattern from CLAUDE.md

## Non-Goals (Out of Scope)

1. **UI/Frontend Development**: This refactoring focuses on backend service; no web interface
2. **Model/Prompt Changes**: Keep existing prompts and `gpt-4o-mini` model unchanged
3. **Multi-Region Deployment**: Single-region deployment sufficient for 10-50 users
4. **Real-Time Streaming**: Batch processing acceptable; no WebSocket/SSE streaming
5. **New Features**: No additional functionality beyond scalability/reliability improvements
6. **LLM Provider Migration**: Remain with LiteLLM + OpenAI
7. **Database Persistence**: Redis cache only; no PostgreSQL/persistent storage for results
8. **Authentication/Authorization**: Service-to-service auth only (API keys); no user auth

## Technical Considerations

### Architecture Overview
```
┌─────────────────────────────────────────┐
│  FastAPI Service (3 workers)            │
│  - Async request handling               │
│  - Rate limiter middleware              │
│  - Correlation ID injection             │
└──────────┬──────────────────────────────┘
           │
      ┌────┼─────┐
      │    │     │
  ┌───▼─┐ ┌▼───┐ ┌▼────────┐
  │ LLM │ │Redis│ │ Logs    │
  │ API │ │Cache│ │(stdout) │
  └─────┘ └─────┘ └─────────┘
```

### Technology Stack
- **Framework**: FastAPI for async HTTP endpoints
- **Cache**: Redis (AWS ElastiCache / GCP Memorystore / Azure Cache)
- **LLM Client**: LiteLLM with OpenAI backend
- **Validation**: Pydantic v2
- **Logging**: structlog with JSON formatter
- **Rate Limiting**: `aiolimiter`
- **Retry Logic**: `tenacity`
- **Deployment**: Docker containers on AWS ECS / GCP Cloud Run / Azure Container Apps

### Cloud-Native Services (Cost-Optimized)
1. **Compute**:
   - AWS: ECS Fargate (0.25 vCPU, 0.5 GB RAM) - ~$10/month
   - GCP: Cloud Run (min instances: 0, max: 3) - ~$5/month
   - Azure: Container Apps (consumption plan) - ~$8/month

2. **Cache**:
   - AWS: ElastiCache (cache.t4g.micro) - ~$12/month
   - GCP: Memorystore (Basic tier, 1GB) - ~$35/month → **Use AWS ElastiCache**
   - Azure: Azure Cache for Redis (Basic C0) - ~$16/month

3. **Monitoring** (Optional Phase 2):
   - CloudWatch Logs (free tier: 5GB) - $0/month initially
   - Structured logs to stdout (container logs) - Free

**Estimated Monthly Cost**: ~$22/month (AWS) vs current ~$60/month in API costs

### Dependencies to Add
```toml
[tool.poetry.dependencies]
redis = {extras = ["hiredis"], version = "^5.0.0"}
pydantic-settings = "^2.0.0"
structlog = "^24.1.0"
tenacity = "^8.2.3"
aiolimiter = "^1.1.0"
fastapi = "^0.109.0"
uvicorn = {extras = ["standard"], version = "^0.27.0"}
```

### Migration Path
1. **Phase 1** (Week 1): Core refactoring
   - Add Redis caching
   - Implement structured outputs (Pydantic)
   - Add retry logic and timeouts
2. **Phase 2** (Week 2): Production readiness
   - FastAPI endpoint wrapper
   - Rate limiting
   - Structured logging
   - Configuration management
3. **Phase 3** (Week 3): Testing & deployment
   - Unit tests (90%+ coverage)
   - Integration tests with mocked Redis/LLM
   - Load tests (50 concurrent users)
   - Deploy to cloud environment

## Design Considerations

### API Endpoint Design (New FastAPI Wrapper)
```python
# POST /api/v1/generate-tuples
# Response: {"tuples": [...], "cached": true, "request_id": "..."}

# POST /api/v1/generate-queries
# Request: {"tuples": [...]}
# Response: {"queries": [...], "cached": false, "request_id": "..."}

# DELETE /api/v1/cache (admin only)
# Invalidate cache manually
```

### Error Response Format
```json
{
  "error": "LLM_API_FAILURE",
  "message": "Failed to generate tuples after 3 retries",
  "request_id": "550e8400-e29b-41d4-a716-446655440000",
  "retry_after": 60
}
```

### Pydantic Models
```python
class DimensionTuple(BaseModel):
    dietary_restriction: str
    meal_type: str
    preparation_time: str
    primary_ingredient: str
    cuisine_type: str

class GenerateTuplesResponse(BaseModel):
    tuples: list[DimensionTuple]
    cached: bool
    request_id: str
    duration_ms: float
```

## Success Metrics

### Performance Metrics
| Metric | Current | Target | Measurement |
|--------|---------|--------|-------------|
| Response time (cached) | N/A | <200ms | p95 latency |
| Response time (uncached) | 4-6s | <3s | p95 latency |
| Cache hit rate | 0% | >80% | Redis stats |
| Throughput | ~0.25 req/s | >10 req/s | Load test |
| Error rate | 5-10% | <0.1% | Error logs |

### Cost Metrics
| Metric | Current (est.) | Target | Measurement |
|--------|---------------|--------|-------------|
| Monthly LLM API cost | ~$60 | <$6 | OpenAI billing |
| Infrastructure cost | $0 | ~$22 | Cloud billing |
| Cost per 1000 queries | $0.60 | $0.03 | Calculated |

### Reliability Metrics
- **Uptime**: >99.5% (allowing 3.6 hours downtime/month for maintenance)
- **Retry success rate**: >95% of failed requests succeed on retry
- **Cache availability**: >99.9% (managed Redis service SLA)

### Quality Metrics
- **Test coverage**: >90% line coverage
- **Type coverage**: 100% (mypy strict mode)
- **Code quality**: Ruff passing with no warnings

## Open Questions

1. **Cloud Provider Choice**: Prefer AWS, GCP, or Azure?
   - **Recommendation**: AWS (lowest cost for Redis + compute combo)

2. **Cache TTL Strategy**:
   - Fixed 1-hour TTL sufficient?
   - Or allow different TTLs for tuples (longer) vs queries (shorter)?

3. **Monitoring Budget**:
   - Start with basic CloudWatch (free tier)?
   - Or invest in Datadog/New Relic upfront (~$15-30/month)?

4. **Deployment Automation**:
   - Use GitHub Actions for CI/CD?
   - Or manual deployment initially?

5. **Health Checks**:
   - What should `/health` endpoint check? (Redis connection, LLM API accessibility)

6. **Versioning**:
   - Version cache keys to allow side-by-side testing of prompt changes?
   - Format: `v1:tuples:{hash}` vs `v2:tuples:{hash}`

7. **Concurrent Request Limit**:
   - Hard cap at 50 concurrent requests (aligns with scale target)?
   - Or allow burst up to 100?

8. **Fallback Strategy**:
   - If Redis unavailable, bypass cache and call LLM directly (degraded mode)?
   - Or fail fast and return 503?

---

## Appendix: Code Review Summary

See `/review` output for detailed analysis. Key findings:
- **Critical**: No caching (20x cost increase), fragile parsing (10% failure rate)
- **High**: No retry logic, sequential processing (2x slower than needed)
- **Medium**: No rate limiting, no timeouts, poor observability
- **Estimated Impact**: 20-400x improvement in various metrics post-refactoring

**Next Steps**: Review PRD with stakeholders → Generate task list with `@generate-tasks.md` → Execute with `@process-task-list.md`
