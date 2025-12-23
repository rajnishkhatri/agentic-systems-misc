# ADR-001: Explicit State Machine for Dispute Orchestration

## Status
Accepted

## Context
The dispute resolution process involves distinct phases (Classify, Gather, Validate, Submit, Monitor) with strict transition rules. We need a robust way to manage this flow, handle errors, and support resumption.

## Decision
We will implement a custom **State Machine Orchestrator** using the State Pattern, rather than a generic workflow engine (like Airflow) or a simple if-else script.

## Rationale
- **Control**: Allows fine-grained control over transitions and side effects (e.g., logging, notifications).
- **Testability**: Each state can be tested in isolation.
- **Resilience**: State can be easily persisted to Redis (ADR-005) for recovery.
- **Lesson Alignment**: Follows the pattern established in Lesson 16.

## Consequences
- Requires defining explicit `DisputeState` enum and `Transition` rules.
- Adds some boilerplate code compared to a linear script.

