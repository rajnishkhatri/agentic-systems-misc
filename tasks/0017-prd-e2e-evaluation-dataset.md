# PRD: Semantic End-to-End Evaluation Dataset Generator

## 1. Introduction/Overview

This PRD defines the requirements for a **Semantic End-to-End Evaluation System** for the Dispute Chatbot. It entails creating a dataset generator that deterministically links and semantically "patches" classification scenarios (natural language complaints) with evidence records (transaction logs, shipping data). This ensures that when a user claims "I didn't buy this TV," the corresponding evidence record actually reflects a TV purchase, enabling rigorous end-to-end testing of the `Classify` -> `Gather Evidence` pipeline.

## 2. Problem Understanding

*   **Restated Problem:** The current testing infrastructure has disjointed datasets. Classification tests use natural language strings (e.g., "Item not received"), while Evidence tests use unrelated synthetic JSON records. We cannot test the full pipeline because the data is inconsistent (e.g., a "Fraud" complaint might map to a "Shipping" evidence record if picked randomly).
*   **Key Constraints:**
    *   **Deterministic Generation:** The same input files must always yield the exact same test dataset (using hashing).
    *   **Semantic Consistency:** Evidence fields (Amount, Date, Merchant) must be modified ("patched") to match the details found in the text description.
    *   **Mock Injection:** The evaluation runner must be able to force the system to use this new synthetic data instead of the default files.
*   **Success Criteria:**
    *   A script that generates `e2e_evaluation_set.json` with 100+ coherent test cases.
    *   An evaluation runner that executes the full pipeline with >90% success rate on "Happy Path" scenarios.
    *   Evidence records that visually match the complaint text (e.g., matching amounts).

## 3. Goals

1.  **Data coherence:** Eliminate mismatch between complaint text and evidence data.
2.  **Pipeline Coverage:** Enable testing of the handover between `Classify` (Phase 1) and `Gather Evidence` (Phase 2).
3.  **Reproducibility:** Ensure tests are deterministic and reproducible across different environments.
4.  **Extensibility:** Allow for easy addition of new test scenarios (e.g., "Friendly Fraud" where evidence proves the user is lying).

## 4. Strategic Approach

*   **Strategy:** **Semantic Patching & Deterministic Linking**.
    *   We will not generate data from scratch. Instead, we will "clone and patch" existing valid evidence records.
    *   We will use `hash(dispute_id) % total_evidence_records` to deterministically select a base record to modify.
    *   We will use a lightweight regex/heuristic parser to extract "facts" (Amount, Merchant) from the complaint text to apply as patches.
*   **Major Components:**
    1.  `Generator Script`: The ETL process to create the dataset.
    2.  `Patching Engine`: Logic to overwrite JSON fields based on text analysis.
    3.  `Evaluation Runner`: A test harness that mocks the `DataLoader` to serve this new dataset.
*   **Recommended Heuristics:**
    *   **Analogy:** Treat this like "Database Seeding" for integration tests.
    *   **Simplification:** Only patch the fields strictly necessary for the dispute logic (Amount, Merchant, Date). Ignore irrelevant fields like "User Agent" unless specific to the test.

## 5. User Stories

*   **US-1 (Coherent Fraud Test):** As a QA engineer, when I run a test for a "Fraud" dispute where the user says "I didn't spend $500 at Apple," the evidence gatherer should return a transaction record showing exactly $500 at Apple, so I can verify the logic works on specific data points.
*   **US-2 (Deterministic Runs):** As a developer, I want the dataset generator to produce the exact same JSON file every time I run it, so I don't get flaky tests in CI/CD.
*   **US-3 (End-to-End Validation):** As a Product Owner, I want to see a report showing that a dispute classified as "10.4" correctly triggers the "CE 3.0" evidence gathering strategy, utilizing the specific transaction data we planted.

## 6. Functional Requirements

### 6.1 Dataset Generator (`scripts/generate_e2e_golden_set.py`)
1.  **Load Inputs:** Must read `natural_language_classification.json` and all 3 evidence files (`transaction_histories.json`, etc.).
2.  **Deterministic Selection:** For each classification scenario, select a base evidence profile using `sha256(dispute_id)`.
3.  **Semantic Patching Logic:**
    *   **Extract:** Identify Amount (e.g., "$45.50"), Merchant (e.g., "Amazon"), and Date hints from the description.
    *   **Patch:** Overwrite the selected `transaction_evidence` with these values.
    *   **Logic Patching:** If the true reason code is `13.1` (Product Not Received), ensure the `shipping_evidence` shows "Delivered" (to test the conflict) or "In Transit" (to test the happy path), based on a flag or random deterministic choice.
4.  **Output:** Save to `synthetic_data/phase1/golden_set/e2e_evaluation_set.json`.

### 6.2 Evaluation Runner (`scripts/evaluate_e2e.py`)
5.  **Mock Injection:** Must subclass or patch `DataLoader` to return records from `e2e_evaluation_set.json` instead of the standard raw files.
6.  **Pipeline Execution:**
    *   Run `classify_dispute_v9_rag(input)`.
    *   Capture `reason_code` and `confidence`.
    *   Run `gather_evidence(reason_code, dispute_id)`.
    *   Validate the `EvidencePackage`.
7.  **Reporting:** Output a summary of Pass/Fail for both phases.

## 7. Non-Goals (Out of Scope)
*   LLM-based text generation for new complaints (we are using existing ones).
*   Real-time generation during test execution (data is pre-generated).
*   Complex NLP for extraction (simple Regex is sufficient for Phase 1).

## 8. Design Considerations
*   **File Structure:** The output JSON should group `input`, `expected_classification`, and `expected_evidence` together to be self-contained.
*   **Performance:** Generation should take < 10 seconds. Evaluation should run in parallel using `asyncio`.

## 9. Technical Considerations
*   **Recommended Implementation Strategy: Decorator Pattern for Mocks**
    *   Use a decorator or context manager to swap out the `DataLoader` singleton during the test run.
    *   *Why:* Keeps the production code clean and isolates the test data injection.
    *   *Watch for:* Ensure the singleton is properly reset after tests to avoid side effects.
*   **Library Usage:** Use standard `re` for extraction and `hashlib` for stability.

## 10. Success Metrics
*   **Generation Consistency:** Checksum of the output file remains identical across runs.
*   **Patch Accuracy:** 100% of "extracted" amounts appear in the generated transaction evidence.
*   **Test Reliability:** The runner yields consistent Pass/Fail results for the same code version.

## 11. Validation Checkpoints
*   **Checkpoint 1 (Generation):** Inspect 5 random records in the generated JSON. Do the amounts in the text match the amounts in the transaction list?
*   **Checkpoint 2 (Runner):** Deliberately break the `classify` logic (e.g., force all to "Fraud") and verify the E2E test fails appropriately.

## 12. Open Questions
*   *None at this stage.* (Resolved via chat: We chose "Semantic Patching" over simple random linking).


