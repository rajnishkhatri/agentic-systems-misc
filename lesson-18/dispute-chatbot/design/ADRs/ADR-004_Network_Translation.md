# ADR-004: Adapter Pattern for Network Translation

## Status
Accepted

## Context
We need to communicate with Visa VROL, which has a complex SOAP/JSON schema. Our internal domain model should not be tightly coupled to this external format.

## Decision
We will use the **Adapter Pattern** to isolate VROL specifics.
- `VisaVrolAdapter` class will convert internal `Dispute` objects to VROL-compliant JSON payloads.
- Internal schema will remain domain-centric.

## Rationale
- **Decoupling**: Changes to VROL API (v1 -> v2) only affect the Adapter, not the core logic.
- **Testability**: We can easily mock the Adapter for integration tests (as done in Phase 1).
- **Maintainability**: Keeps the core domain logic clean of external API quirks.

## Consequences
- Requires maintaining mapping logic (Task 11.2) which can be tedious.
- SPIKE-001 was required to validate the schema assumptions.

