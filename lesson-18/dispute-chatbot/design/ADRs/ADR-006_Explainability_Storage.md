# ADR-006: Comprehensive Explainability Storage

## Status
Accepted

## Context
For AI decisions in financial services, "black box" behavior is unacceptable. We need to trace *why* an agent made a decision.

## Decision
We will implement a **4-Pillar Explainability Store**:
1. **BlackBoxRecorder**: Raw input/output of every LLM call.
2. **AgentFacts**: Version and prompt hash of the agent used.
3. **GuardRails**: PII and safety check results.
4. **PhaseLogger**: High-level reasoning for state transitions.

All traces will be stored in **structured JSON logs** (and sent to CloudWatch/S3 in prod).

## Rationale
- **Auditability**: Essential for compliance and dispute defense.
- **Debugging**: Allows replaying specific failures.
- **Trust**: Users can see "Why did you say that?" in the UI sidebar.

## Consequences
- Increased storage volume.
- Performance overhead (minimal with async logging).

