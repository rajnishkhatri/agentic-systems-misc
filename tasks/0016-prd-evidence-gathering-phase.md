# PRD: Evidence Gathering Phase (Phase 2)

## 1. Introduction/Overview
This PRD defines the implementation of **Phase 2: Gather Evidence** for the Dispute Chatbot. This phase is responsible for analyzing the dispute classification, planning the necessary evidence collection, and orchestrating parallel calls to specialist agents (mocked for now) to assemble a comprehensive defense package. It specifically addresses complex scenarios like **Compelling Evidence 3.0 (CE 3.0)** for fraud and proof of delivery for shipping disputes.

## 2. Problem Understanding
*   **Restated Problem:** Once a dispute is classified with a specific reason code (e.g., "Fraud 10.4" or "Product Not Received 13.1"), the system must autonomously gather the correct supporting evidence to prove the merchant's case. This requires different strategies for different dispute types and involves querying multiple data sources (Transactions, Shipping, Customer Logs).
*   **Key Constraints:**
    *   **Mock APIs:** Must use simulated adapters for all external integrations (Stripe, FedEx, etc.).
    *   **CE 3.0 Logic:** Must implement precise qualification rules (transaction counts, time windows, signal matching).
    *   **Integration:** Must fit into the existing `DisputeOrchestrator` state machine.
*   **Success Criteria:** A system that accepts a `ClassifyResponse` and outputs a strongly-typed `EvidencePackage` containing all necessary proofs and qualification flags.

## 3. Goals
1.  **Dynamic Planning:** Implement `EvidencePlanner` to generate tailored evidence collection plans based on the dispute reason code.
2.  **Parallel Execution:** Orchestrate simultaneous calls to multiple specialist agents to minimize phase latency.
3.  **CE 3.0 Qualification:** Implement precise logic to qualify transactions for Visa's Compelling Evidence 3.0 protections (Fraud 10.4).
4.  **Type Safety:** Ensure all data flows using strict Pydantic models to prevent runtime errors.

## 4. Strategic Approach
*   **Strategy:** **Hierarchical Agent Pattern (Manager-Worker)**.
    *   **Manager (`EvidencePlanner`):** Analyzes the task and decides *what* evidence is needed.
    *   **Workers (`Specialists`):** Specialized classes (`TransactionSpecialist`, `CustomerSpecialist`, `ShippingSpecialist`) that know *how* to fetch specific data points.
    *   **Aggregator:** Central logic that combines results and applies cross-domain rules (like CE 3.0 eligibility).
*   **Major Components:**
    1.  **Data Models:** Strict Pydantic schemas for all evidence types.
    2.  **Mock Adapters:** Simulated implementations of external APIs.
    3.  **Orchestrator Logic:** Asynchronous gathering and rule evaluation.
*   **Recommended Heuristics:**
    *   **Simplification:** Use Mock Adapters to simulate third-party APIs, allowing the team to focus on the orchestration and business logic without external dependencies.
    *   **Decomposition:** Separate the "fetching" responsibility (Specialists) from the "evaluating" responsibility (CE 3.0 Validator).

## 5. User Stories
*   **US-1 (Fraud Defense):** As the system, when I process a "Fraud 10.4" dispute, I want to automatically check for prior undisputed transactions and matching device/IP signals to see if we qualify for CE 3.0 liability shift.
*   **US-2 (Shipping Defense):** As the system, when I process a "PNR 13.1" dispute, I want to fetch tracking logs and Proof of Delivery (POD) signature to prove the item was delivered to the cardholder's address.
*   **US-3 (General Defense):** As the system, for other disputes, I want to fetch basic account standing and history to support a general defense.

## 6. Functional Requirements
### 6.1 Data Models (`backend/phases/evidence_models.py`)
1.  Define `EvidencePlan` containing a list of required evidence types and assigned specialists.
2.  Define `SpecialistResult` as a base class for all specialist outputs.
3.  Define `EvidencePackage` as the final aggregated object, including CE 3.0 qualification flags and raw evidence data.

### 6.2 Specialists (`backend/adapters/specialists.py`)
4.  **TransactionSpecialist:** Must return mock transaction history (configurable for CE 3.0 testing).
5.  **CustomerSpecialist:** Must return mock device fingerprints, IP addresses, and email logs.
6.  **ShippingSpecialist:** Must return mock tracking events, delivery status, and POD images/signatures.
7.  *Requirement:* All mocks must be configurable to simulate both "success" (evidence found) and "failure" (evidence missing) scenarios.

### 6.3 Evidence Planner (`backend/phases/gather_evidence.py`)
8.  Implement logic to map `reason_code` to a specific list of required evidence.
9.  (Optional V1) Use a static mapping or simple rule-based planner. (V2) Upgrade to LLM-based planning if flexibility is needed.

### 6.4 Orchestration & Validation
10. Use `asyncio.gather` to execute specialist calls in parallel.
11. Implement `check_ce3_eligibility(prior_txns, customer_signals)` to evaluate Fraud 10.4 criteria:
    *   At least 2 prior undisputed transactions > 120 days old (or specific window).
    *   At least 2 matching data elements (IP, Device, Email, Address).

## 7. Non-Goals (Out of Scope)
*   Real integration with Stripe, FedEx, or other third-party APIs.
*   Generation of the final PDF rebuttal document (this is Phase 4).
*   Complex retry logic for API failures (basic error handling only).

## 8. Design Considerations
*   **Modularity:** Specialists should be independent and easily swappable with real implementations later.
*   **Observability:** The `EvidencePackage` should contain a "trace" or summary of how the evidence was gathered (e.g., "Found 2 matching transactions").

## 9. Technical Considerations
*   **Recommended Implementation Strategy: Type-Driven Development**
    *   *Why:* Complex nested data structures are prone to runtime errors.
    *   *Approach:* Define Pydantic models *first*, then implement the mocks to strict interfaces.
    *   *Watch for:* `None` values or missing fields in the aggregated package.
*   **Concurrency:**
    *   Use `asyncio` for non-blocking execution.
    *   Ensure exception handling inside the parallel tasks doesn't crash the entire phase.

## 10. Success Metrics
*   **Completeness:** 100% of required evidence fields defined in the plan are present in the final package for the Golden Set.
*   **Latency:** Phase execution completes in < 2 seconds (using mocks).
*   **Accuracy:** CE 3.0 qualification logic correctly identifies eligible vs. ineligible cases in the test suite (100% pass rate on unit tests).

## 11. Validation Checkpoints
*   **Checkpoint 1 (Models):** Verify Pydantic models cover all fields required by the Sequence Diagrams.
*   **Checkpoint 2 (Mocks):** Ensure mocks can produce both "Happy Path" (qualified) and "Unhappy Path" (disqualified) data.
*   **Checkpoint 3 (Integration):** Run the full `gather_evidence` phase with a sample task and verify the output structure matches expectations.

## 12. Open Questions
*   Do we need to persist the `EvidencePackage` to disk/database at this stage, or just pass it in memory? (Assumption: In-memory return to Orchestrator).

