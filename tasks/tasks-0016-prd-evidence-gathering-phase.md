## Relevant Files

- `lesson-18/dispute-chatbot/backend/phases/evidence_models.py` - Pydantic models for evidence (Plan, Specialists, Package)
- `lesson-18/dispute-chatbot/backend/adapters/specialists.py` - Mock adapters for Transaction, Customer, and Shipping specialists
- `lesson-18/dispute-chatbot/backend/phases/gather_evidence.py` - Main orchestration logic (Planner, Parallel Execution, CE 3.0 Logic)
- `lesson-18/dispute-chatbot/tests/test_gather_evidence.py` - Integration tests for the full phase

### Notes

- This task list focuses on using **Mock APIs** as specified in the PRD.
- All code follows strictly typed Pydantic models to prevent runtime data issues.
- `asyncio` is used for parallel execution of specialist tasks.

### Assumptions Made

- [Assumption 1]: `LLMService` integration is not required for the V1 Evidence Planner (simple rule-based mapping is sufficient).
- [Assumption 2]: CE 3.0 qualification logic is deterministic based on the provided mock data.
- [Assumption 3]: No persistent storage (database) is needed for this phase; in-memory `EvidencePackage` is sufficient.

## Tasks

- [x] 1.0 Implement Data Models for Evidence Phase
  - [x] 1.1 Create `evidence_models.py` with `EvidencePlan` and `SpecialistResult` base class
        Input: PRD Section 6.1 | Output: Pydantic models | Verification: Import models without error
  - [x] 1.2 Implement specific result types (`TransactionEvidence`, `CustomerEvidence`, `ShippingEvidence`)
        Input: PRD Sequence Diagrams | Output: Subclass definitions | Verification: Instantiate with test data
  - [x] 1.3 Implement `EvidencePackage` and `CE3QualificationResult` models
        Input: PRD Section 6.1 | Output: Aggregate model | Verification: Validate full structure

- [x] 2.0 Create Mock Specialist Adapters
  - [x] 2.1 Create `specialists.py` and implement `TransactionSpecialist` (mock history)
        Input: PRD Section 6.2 | Output: Class with `get_history` method | Verification: Returns list of Pydantic objs
  - [x] 2.2 Implement `CustomerSpecialist` (mock device/IP/email)
        Input: PRD Section 6.2 | Output: Class with `get_signals` method | Verification: Returns mock signals
  - [x] 2.3 Implement `ShippingSpecialist` (mock tracking/POD)
        Input: PRD Section 6.2 | Output: Class with `get_tracking` method | Verification: Returns mock POD data
  - [x] 2.4 Add configuration support to mocks (Happy/Unhappy paths)
        Input: PRD Section 6.2 | Output: Configurable mocks | Verification: Toggle between success/fail responses

- [x] 3.0 Implement Evidence Planner & Aggregator Logic
  - [x] 3.1 Implement `EvidencePlanner` with rule-based mapping (`reason_code` -> `plan`)
        Input: PRD Section 6.3 | Output: Function returning `EvidencePlan` | Verification: Check output for "Fraud 10.4"
  - [x] 3.2 Implement `validate_ce3_eligibility` logic (counts, dates, matches)
        Input: PRD Section 6.4 | Output: Boolean + reasoning | Verification: Unit test with boundary cases
  - [x] 3.3 Implement main `gather_evidence` orchestrator with `asyncio.gather`
        Input: `task` dict | Output: `EvidencePackage` | Verification: Latency check (parallel execution)

- [x] 4.0 Testing and Validation
  - [x] 4.1 Create `test_gather_evidence.py` framework
        Input: Test requirements | Output: Pytest file | Verification: Tests runnable
  - [x] 4.2 Write tests for CE 3.0 Qualification (Qualified vs Not Qualified)
        Input: Mock data variations | Output: Assertions | Verification: Tests pass
  - [x] 4.3 Write tests for PNR 13.1 (Shipping Evidence retrieval)
        Input: Mock shipping data | Output: Assertions | Verification: Tests pass
  - [x] 4.4 Run full integration test and verify `EvidencePackage` structure
        Input: `gather_evidence` | Output: Validated JSON | Verification: 100% field coverage
