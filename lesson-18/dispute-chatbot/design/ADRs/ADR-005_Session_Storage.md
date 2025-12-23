# ADR-005: Redis for Session and State Persistence

## Status
Accepted

## Context
The chatbot is stateful. If the container restarts or scales, we must not lose the active dispute context.

## Decision
We will use **Redis** as the backing store for:
1. User Session Data (Chainlit session).
2. Dispute State Machine Context.

## Rationale
- **Speed**: In-memory access is required for real-time chat latency.
- **TTL Support**: Easy to expire sessions automatically (e.g., 30 mins idle).
- **Persistence**: AOF/RDB persistence allows recovery after crash (verified in SPIKE-005).

## Consequences
- Dependency on a Redis instance (docker-compose for local, managed service for prod).
- Requires serialization of state objects (Pydantic models help here).

