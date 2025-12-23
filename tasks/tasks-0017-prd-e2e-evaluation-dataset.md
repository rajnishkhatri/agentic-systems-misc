## Relevant Files

- `scripts/generate_e2e_golden_set.py` - Script to generate the semantic end-to-end dataset.
- `scripts/evaluate_e2e.py` - Runner script to execute the evaluation pipeline with mocked data.
- `lesson-18/dispute-chatbot/synthetic_data/phase1/golden_set/e2e_evaluation_set.json` - The generated output dataset.
- `lesson-18/dispute-chatbot/synthetic_data/phase1/golden_set/natural_language_classification.json` - Input classification data.
- `lesson-18/dispute-chatbot/synthetic_data/phase1/evidence/transaction_histories.json` - Input evidence data.

### Notes

- The generator script should be deterministic.
- The runner script uses `asyncio` for the pipeline execution.
- Paths are relative to the project root.

### Assumptions Made

- [Assumption 1]: The "evidence" files (transactions, shipping, customer) are all in the same directory structure under `lesson-18/.../evidence/`.
- [Assumption 2]: The `Classify` and `Gather Evidence` logic is importable from the existing codebase (likely in `lesson-18` or `composable_app`). I will assume `composable_app` or `lesson-18` modules are available.

## Tasks

- [x] 1.0 Setup and Infrastructure
  - [x] 1.1 Create `scripts/generate_e2e_golden_set.py` and `scripts/evaluate_e2e.py` (empty files)
        Input: None
        Output: Empty Python files
        Verification: Files exist in `scripts/`
  - [x] 1.2 Verify input data paths and output directory existence
        Input: Path inspection
        Output: Confirmed paths
        Verification: `ls` shows input files exist; `mkdir -p` ensures output dir exists

- [x] 2.0 Implement Dataset Generator (`scripts/generate_e2e_golden_set.py`)
  - [x] 2.1 Implement `load_data` function to read classification and evidence JSONs
        Input: JSON file paths
        Output: Loaded Python dictionaries/lists
        Verification: Print/log loaded record counts
  - [x] 2.2 Implement `extract_semantic_features(text)` function using Regex
        Input: "I didn't buy this $500 TV from Samsung"
        Output: `{"amount": 500.0, "merchant": "Samsung", "product": "TV"}`
        Verification: Unit test with sample strings
  - [x] 2.3 Implement `patch_evidence(evidence_record, features, reason_code)` function
        Input: Base evidence record + Extracted features + Reason Code
        Output: Modified evidence record with matching Amount/Merchant AND shipping status logic (e.g. for 13.1)
        Verification: Assert `record['amount'] == features['amount']`; if reason='13.1', shipping status is set correctly
  - [x] 2.4 Implement `link_and_generate` main loop
        Input: All loaded data
        Output: List of combined test cases (Input + Expected Classification + Expected Evidence)
        Verification: Checksum of output list is stable across runs
  - [x] 2.5 Save output to `e2e_evaluation_set.json`
        Input: Generated list
        Output: JSON file on disk
        Verification: File exists and contains valid JSON

- [x] 3.0 Implement Evaluation Runner (`scripts/evaluate_e2e.py`)
  - [x] 3.1 Create `MockDataLoader` class/context manager
        Input: Path to `e2e_evaluation_set.json`
        Output: Object that intercepts `get_evidence` calls
        Verification: Calling `get_evidence` returns data from our JSON, not the DB/File
  - [x] 3.2 Implement `run_pipeline(test_case)` function
        Input: Single test case dict
        Output: Execution result (Classification + Evidence)
        Verification: Returns an `EvidencePackage` object
  - [x] 3.3 Implement comparison logic (`validate_result(actual, expected)`)
        Input: Actual vs Expected objects
        Output: Boolean Pass/Fail + Reason
        Verification: Passes for exact match, fails for mismatch
  - [x] 3.4 Implement main execution loop with `asyncio`
        Input: `e2e_evaluation_set.json`
        Output: Console report of Pass/Fail rates
        Verification: Script runs to completion and prints summary

- [x] 4.0 Verification and Validation
  - [x] 4.1 Run `generate_e2e_golden_set.py` and inspect 5 random records
        Input: Execution command
        Output: Visual inspection of JSON
        Verification: "Description" text matches "Transaction" details
  - [x] 4.2 Run `evaluate_e2e.py` on the generated set
        Input: Execution command
        Output: Test report
        Verification: High pass rate (>90%) for happy path
  - [x] 4.3 (Optional) Introduce a deliberate bug in `Classify` and verify test failure
        Input: Code modification
        Output: Test failure in report
        Verification: Runner correctly identifies the regression
