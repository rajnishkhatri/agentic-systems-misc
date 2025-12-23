import json
import os

from synthetic_data.schemas import SyntheticDispute

# Use absolute path relative to this test file's location
_TEST_DIR = os.path.dirname(os.path.abspath(__file__))
_PROJECT_DIR = os.path.dirname(_TEST_DIR)
DATA_DIR = os.path.join(_PROJECT_DIR, "synthetic_data", "phase1")

REQUIRED_FILES = [
    "disputes/fraud_10.4_cases.json",
    "disputes/pnr_13.1_cases.json",
    "disputes/edge_cases.json",
    "evidence/transaction_histories.json",
    "evidence/shipping_records.json",
    "evidence/incomplete_evidence.json",
    "conversations/happy_path_dialogues.json",
    "conversations/error_recovery_dialogues.json",
    "conversations/escalation_dialogues.json",
    "golden_set/classification_labels.json",
    "golden_set/evidence_quality_scores.json",
    "golden_set/fabrication_examples.json"
]


def test_should_have_all_required_files_when_generation_complete() -> None:
    """Verify that all required Phase 1 data files exist after generation."""
    for rel_path in REQUIRED_FILES:
        full_path = os.path.join(DATA_DIR, rel_path)
        assert os.path.exists(full_path), f"Missing file: {rel_path}"


def test_should_have_valid_non_empty_json_when_files_exist() -> None:
    """Verify JSON files are valid and contain data."""
    for rel_path in REQUIRED_FILES:
        full_path = os.path.join(DATA_DIR, rel_path)
        with open(full_path, 'r') as f:
            data = json.load(f)
            assert isinstance(data, list), f"{rel_path} should be a list"
            assert len(data) > 0, f"{rel_path} is empty"


def test_should_match_pydantic_schema_when_fraud_disputes_loaded() -> None:
    """Verify that generated fraud disputes match the Pydantic schema."""
    path = os.path.join(DATA_DIR, "disputes/fraud_10.4_cases.json")
    with open(path, 'r') as f:
        data = json.load(f)

    for item in data[:10]:  # Check first 10
        dispute = SyntheticDispute(**item)
        assert dispute.reason_code == "10.4"
        assert dispute.network == "visa"


def test_should_match_pydantic_schema_when_pnr_disputes_loaded() -> None:
    """Verify that generated PNR disputes match the Pydantic schema."""
    path = os.path.join(DATA_DIR, "disputes/pnr_13.1_cases.json")
    with open(path, 'r') as f:
        data = json.load(f)

    for item in data[:10]:  # Check first 10
        dispute = SyntheticDispute(**item)
        assert dispute.reason_code == "13.1"
        assert dispute.network == "visa"


def test_should_link_evidence_to_disputes_when_both_generated() -> None:
    """Verify that evidence files link back to disputes via dispute_id."""
    dispute_path = os.path.join(DATA_DIR, "disputes/fraud_10.4_cases.json")
    evidence_path = os.path.join(DATA_DIR, "evidence/transaction_histories.json")

    with open(dispute_path, 'r') as f:
        disputes = json.load(f)
    with open(evidence_path, 'r') as f:
        evidence = json.load(f)

    assert len(disputes) == len(evidence), "Dispute and evidence counts must match"
    assert disputes[0]['dispute_id'] == evidence[0]['dispute_id'], "First dispute_id must match"


def test_should_have_200_fraud_cases_when_generation_complete() -> None:
    """Verify 200 fraud 10.4 cases were generated per PRD requirement."""
    path = os.path.join(DATA_DIR, "disputes/fraud_10.4_cases.json")
    with open(path, 'r') as f:
        data = json.load(f)
    assert len(data) == 200, f"Expected 200 fraud cases, got {len(data)}"


def test_should_have_200_pnr_cases_when_generation_complete() -> None:
    """Verify 200 PNR 13.1 cases were generated per PRD requirement."""
    path = os.path.join(DATA_DIR, "disputes/pnr_13.1_cases.json")
    with open(path, 'r') as f:
        data = json.load(f)
    assert len(data) == 200, f"Expected 200 PNR cases, got {len(data)}"


def test_should_have_100_edge_cases_when_generation_complete() -> None:
    """Verify 100 edge cases were generated per PRD requirement."""
    path = os.path.join(DATA_DIR, "disputes/edge_cases.json")
    with open(path, 'r') as f:
        data = json.load(f)
    assert len(data) == 100, f"Expected 100 edge cases, got {len(data)}"


def test_should_have_ce3_transactions_when_fraud_evidence_present() -> None:
    """Verify fraud evidence includes CE 3.0 prior transactions."""
    path = os.path.join(DATA_DIR, "evidence/transaction_histories.json")
    with open(path, 'r') as f:
        evidence_list = json.load(f)

    # At least some evidence should have CE 3.0 transactions (win cases)
    has_ce3 = any(len(e.get('ce3_transactions', [])) > 0 for e in evidence_list)
    assert has_ce3, "At least some fraud evidence should have CE 3.0 transactions"


def test_should_have_shipping_records_when_pnr_evidence_present() -> None:
    """Verify PNR evidence includes shipping records."""
    path = os.path.join(DATA_DIR, "evidence/shipping_records.json")
    with open(path, 'r') as f:
        evidence_list = json.load(f)

    # At least some evidence should have shipping (win cases)
    has_shipping = any(e.get('shipping') is not None for e in evidence_list)
    assert has_shipping, "At least some PNR evidence should have shipping records"

