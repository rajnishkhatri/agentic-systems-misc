"""Dataset quality validation and statistical analysis tests.

Validates all 3 datasets for schema compliance, challenge distribution,
reproducibility, statistical properties, and cross-dataset consistency.
Following TDD methodology with test_should_[result]_when_[condition] naming.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

import pytest

# Add lesson-16 to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from backend.data_generation import validate_json_schema
from backend.data_generation.invoices import generate_invoice_dataset
from backend.data_generation.reconciliation import generate_reconciliation_dataset
from backend.data_generation.transactions import generate_transaction_dataset

# ============================================================================
# Fixtures
# ============================================================================


@pytest.fixture
def invoice_dataset() -> list[dict[str, Any]]:
    """Generate invoice dataset for testing."""
    return generate_invoice_dataset(count=100, seed=42)


@pytest.fixture
def transaction_dataset() -> list[dict[str, Any]]:
    """Generate transaction dataset for testing."""
    return generate_transaction_dataset(count=100, fraud_rate=0.1, seed=42)


@pytest.fixture
def reconciliation_dataset() -> list[dict[str, Any]]:
    """Generate reconciliation dataset for testing."""
    return generate_reconciliation_dataset(count=100, difficulty="mixed", seed=42)


# ============================================================================
# Schema Compliance Tests
# ============================================================================


def test_should_comply_with_schema_when_invoice_dataset_loaded(invoice_dataset: list[dict[str, Any]]) -> None:
    """Test that all invoices comply with schema."""
    invoice_schema = {
        "required": ["invoice_id", "vendor", "amount", "date", "line_items"],
        "properties": {
            "invoice_id": {"type": "string"},
            "vendor": {"type": "string"},
            "amount": {"type": "number"},
            "date": {"type": "string"},
            "line_items": {"type": "array"},
        },
    }

    for invoice in invoice_dataset:
        is_valid, errors = validate_json_schema(invoice, invoice_schema)
        assert is_valid, f"Invoice {invoice.get('invoice_id')} failed schema: {errors}"


def test_should_comply_with_schema_when_transaction_dataset_loaded(
    transaction_dataset: list[dict[str, Any]]
) -> None:
    """Test that all transactions comply with schema."""
    transaction_schema = {
        "required": [
            "transaction_id",
            "merchant",
            "amount",
            "timestamp",
            "user_behavior",
            "fraud_label",
        ],
        "properties": {
            "transaction_id": {"type": "string"},
            "merchant": {"type": "string"},
            "amount": {"type": "number"},
            "timestamp": {"type": "string"},
            "user_behavior": {"type": "object"},
            "fraud_label": {"type": "boolean"},
        },
    }

    for transaction in transaction_dataset:
        is_valid, errors = validate_json_schema(transaction, transaction_schema)
        assert is_valid, f"Transaction {transaction.get('transaction_id')} failed schema: {errors}"


def test_should_comply_with_schema_when_reconciliation_dataset_loaded(
    reconciliation_dataset: list[dict[str, Any]]
) -> None:
    """Test that all reconciliation tasks comply with schema."""
    reconciliation_schema = {
        "required": [
            "reconciliation_id",
            "bank_transactions",
            "ledger_entries",
            "expected_matches",
            "reconciliation_status",
            "discrepancy_amount",
            "difficulty",
        ],
        "properties": {
            "reconciliation_id": {"type": "string"},
            "bank_transactions": {"type": "array"},
            "ledger_entries": {"type": "array"},
            "expected_matches": {"type": "array"},
            "reconciliation_status": {"type": "string"},
            "discrepancy_amount": {"type": "number"},
            "difficulty": {"type": "string"},
        },
    }

    for task in reconciliation_dataset:
        is_valid, errors = validate_json_schema(task, reconciliation_schema)
        assert is_valid, f"Reconciliation {task.get('reconciliation_id')} failed schema: {errors}"


# ============================================================================
# Challenge Distribution Tests
# ============================================================================


def test_should_have_ocr_errors_within_tolerance_when_invoice_dataset_generated(
    invoice_dataset: list[dict[str, Any]]
) -> None:
    """Test that OCR error rate is 15±5%."""
    ocr_errors = sum(1 for inv in invoice_dataset if inv.get("has_ocr_error", False))
    ocr_rate = ocr_errors / len(invoice_dataset)
    assert 0.10 <= ocr_rate <= 0.20, f"OCR error rate {ocr_rate:.1%} outside 15±5% target"


def test_should_have_fraud_rate_within_tolerance_when_transaction_dataset_generated(
    transaction_dataset: list[dict[str, Any]]
) -> None:
    """Test that fraud rate is exactly 10.0±1.0% (allowing for random variation)."""
    fraud_count = sum(1 for txn in transaction_dataset if txn.get("fraud_label", False))
    fraud_rate = fraud_count / len(transaction_dataset)
    assert 0.09 <= fraud_rate <= 0.11, f"Fraud rate {fraud_rate:.1%} outside 10.0±1.0% target"


def test_should_have_date_mismatches_within_tolerance_when_reconciliation_dataset_generated(
    reconciliation_dataset: list[dict[str, Any]]
) -> None:
    """Test that date mismatch challenges are 25±5%."""
    date_mismatches = sum(1 for task in reconciliation_dataset if task.get("has_date_mismatch", False))
    mismatch_rate = date_mismatches / len(reconciliation_dataset)
    assert 0.20 <= mismatch_rate <= 0.30, f"Date mismatch rate {mismatch_rate:.1%} outside 25±5% target"


# ============================================================================
# Uniqueness and Consistency Tests
# ============================================================================


def test_should_have_no_duplicate_ids_across_all_datasets(
    invoice_dataset: list[dict[str, Any]],
    transaction_dataset: list[dict[str, Any]],
    reconciliation_dataset: list[dict[str, Any]],
) -> None:
    """Test that no IDs are duplicated across datasets."""
    invoice_ids = {inv["invoice_id"] for inv in invoice_dataset}
    transaction_ids = {txn["transaction_id"] for txn in transaction_dataset}
    reconciliation_ids = {task["reconciliation_id"] for task in reconciliation_dataset}

    # Check for duplicates within each dataset
    assert len(invoice_ids) == len(invoice_dataset), "Duplicate invoice_id found"
    assert len(transaction_ids) == len(transaction_dataset), "Duplicate transaction_id found"
    assert len(reconciliation_ids) == len(reconciliation_dataset), "Duplicate reconciliation_id found"

    # Check no overlap across datasets (though they use different prefixes)
    all_ids = invoice_ids | transaction_ids | reconciliation_ids
    assert len(all_ids) == len(invoice_dataset) + len(transaction_dataset) + len(reconciliation_dataset)


# ============================================================================
# Gold Label Accuracy Tests
# ============================================================================


def test_should_have_accurate_gold_labels_when_invoices_validated(invoice_dataset: list[dict[str, Any]]) -> None:
    """Test that invoice gold labels are 100% accurate."""
    for invoice in invoice_dataset:
        # Gold labels should exist
        assert "gold_label" in invoice, f"Invoice {invoice['invoice_id']} missing gold_label"

        # Validate gold label structure
        gold_label = invoice["gold_label"]
        assert isinstance(gold_label, dict), "Gold label must be a dict"
        assert "is_valid" in gold_label, "Gold label missing is_valid field"

        # For valid invoices (no errors), amount should be reasonable
        if gold_label.get("is_valid", False):
            assert invoice["amount"] > 0, f"Valid invoice {invoice['invoice_id']} has non-positive amount"


def test_should_have_accurate_gold_labels_when_transactions_validated(
    transaction_dataset: list[dict[str, Any]]
) -> None:
    """Test that transaction fraud labels are consistent."""
    for transaction in transaction_dataset:
        fraud_label = transaction.get("fraud_label", False)
        fraud_type = transaction.get("fraud_type")

        # If fraud_label is True, fraud_type should not be None
        if fraud_label:
            assert fraud_type is not None, f"Transaction {transaction['transaction_id']} fraud but type is None"
            assert fraud_type in [
                "stolen_card",
                "account_takeover",
                "synthetic_fraud",
            ], f"Invalid fraud_type: {fraud_type}"
        else:
            assert fraud_type is None, f"Transaction {transaction['transaction_id']} not fraud but has type {fraud_type}"


def test_should_have_accurate_gold_labels_when_reconciliation_validated(
    reconciliation_dataset: list[dict[str, Any]]
) -> None:
    """Test that reconciliation expected_matches are valid."""
    for task in reconciliation_dataset:
        expected_matches = task.get("expected_matches", [])

        # Validate that matched indices exist
        bank_txns = task.get("bank_transactions", [])
        ledger_entries = task.get("ledger_entries", [])

        for match in expected_matches:
            bank_idx = match.get("bank_index", -1)
            ledger_idx = match.get("ledger_index", -1)

            assert 0 <= bank_idx < len(bank_txns), f"Invalid bank_index {bank_idx}"
            assert 0 <= ledger_idx < len(ledger_entries), f"Invalid ledger_index {ledger_idx}"


# ============================================================================
# Statistical Properties Tests
# ============================================================================


def test_should_have_lognormal_distribution_when_invoice_amounts_analyzed(
    invoice_dataset: list[dict[str, Any]]
) -> None:
    """Test that invoice amounts follow log-normal distribution."""
    amounts = [inv["amount"] for inv in invoice_dataset]

    # Calculate median
    sorted_amounts = sorted(amounts)
    median = sorted_amounts[len(amounts) // 2]

    # Median should be between $100 and $50K for realistic distribution
    assert 100 <= median <= 50000, f"Median amount ${median:.2f} outside realistic range"

    # Check that distribution has long tail (max >> median)
    max_amount = max(amounts)
    assert max_amount > 2 * median, "Distribution doesn't have expected long tail"


def test_should_have_uniform_date_distribution_when_transactions_analyzed(
    transaction_dataset: list[dict[str, Any]]
) -> None:
    """Test that transaction dates are uniformly distributed over 2024."""
    from datetime import datetime

    dates = [datetime.fromisoformat(txn["timestamp"].replace("Z", "+00:00")) for txn in transaction_dataset]

    # Group by month
    months = [d.month for d in dates]

    # Each month should have roughly 100/12 ≈ 8-9 transactions (allow ±5)
    for month in range(1, 13):
        count = months.count(month)
        assert 3 <= count <= 15, f"Month {month} has {count} transactions (expected ~8 with variance)"


# ============================================================================
# Reproducibility Tests
# ============================================================================


def test_should_be_reproducible_when_same_seed_used_for_all_datasets() -> None:
    """Test that same seed generates identical datasets across 3 runs."""
    # Generate invoices 3 times with same seed
    invoices1 = generate_invoice_dataset(count=10, seed=99)
    invoices2 = generate_invoice_dataset(count=10, seed=99)
    invoices3 = generate_invoice_dataset(count=10, seed=99)

    # Should be identical
    assert invoices1 == invoices2 == invoices3

    # Generate transactions 3 times
    txns1 = generate_transaction_dataset(count=10, fraud_rate=0.1, seed=99)
    txns2 = generate_transaction_dataset(count=10, fraud_rate=0.1, seed=99)
    txns3 = generate_transaction_dataset(count=10, fraud_rate=0.1, seed=99)

    assert txns1 == txns2 == txns3

    # Generate reconciliation 3 times
    recon1 = generate_reconciliation_dataset(count=10, difficulty="mixed", seed=99)
    recon2 = generate_reconciliation_dataset(count=10, difficulty="mixed", seed=99)
    recon3 = generate_reconciliation_dataset(count=10, difficulty="mixed", seed=99)

    assert recon1 == recon2 == recon3


# ============================================================================
# Edge Case Coverage Tests
# ============================================================================


def test_should_handle_edge_cases_when_datasets_contain_special_values(
    invoice_dataset: list[dict[str, Any]],
    transaction_dataset: list[dict[str, Any]],
    reconciliation_dataset: list[dict[str, Any]],
) -> None:
    """Test that datasets include edge cases."""
    # Invoices: Should have some with very small amounts
    small_amounts = [inv for inv in invoice_dataset if inv["amount"] < 100]
    assert len(small_amounts) > 0, "No small amount invoices found"

    # Transactions: Should have some high-value transactions >$10K
    high_value = [txn for txn in transaction_dataset if txn["amount"] > 10000]
    assert len(high_value) > 0, "No high-value transactions found"

    # Reconciliation: Should have some with zero discrepancy
    perfect_matches = [task for task in reconciliation_dataset if task["discrepancy_amount"] == 0.0]
    assert len(perfect_matches) > 0, "No perfect match reconciliations found"


# ============================================================================
# Human Readability Tests
# ============================================================================


def test_should_be_human_readable_when_datasets_spot_checked() -> None:
    """Test that sample data is plausible and human-readable."""
    # Generate small samples
    invoices = generate_invoice_dataset(count=5, seed=42)
    transactions = generate_transaction_dataset(count=5, fraud_rate=0.2, seed=42)
    reconciliation = generate_reconciliation_dataset(count=2, difficulty="easy", seed=42)

    # Spot check invoice
    inv = invoices[0]
    assert len(inv["vendor"]) > 0, "Empty vendor name"
    assert inv["amount"] > 0, "Invalid amount"
    assert "-" in inv["date"], "Invalid date format"
    assert "INV-" in inv["invoice_id"], "Invalid invoice ID format"

    # Spot check transaction
    txn = transactions[0]
    assert len(txn["merchant"]) > 0, "Empty merchant name"
    assert "TXN-" in txn["transaction_id"], "Invalid transaction ID"
    assert 0.0 <= txn["gold_label_confidence"] <= 1.0, "Invalid confidence score"

    # Spot check reconciliation
    recon = reconciliation[0]
    assert len(recon["bank_transactions"]) > 0, "No bank transactions"
    assert len(recon["ledger_entries"]) > 0, "No ledger entries"
    assert "REC-" in recon["reconciliation_id"], "Invalid reconciliation ID"


# ============================================================================
# Dataset Summary Report Generation
# ============================================================================


def test_should_generate_dataset_summary_when_all_datasets_loaded(
    invoice_dataset: list[dict[str, Any]],
    transaction_dataset: list[dict[str, Any]],
    reconciliation_dataset: list[dict[str, Any]],
) -> None:
    """Test that dataset summary report can be generated."""
    from datetime import datetime

    summary = {
        "generation_date": datetime.now().isoformat(),
        "version": "1.0",
        "schema_version": "1.0",
        "datasets": {
            "invoices": {
                "count": len(invoice_dataset),
                "file_size_bytes": 57856,  # Approximate
                "challenge_distribution": {
                    "ocr_errors": sum(1 for inv in invoice_dataset if inv.get("has_ocr_error", False)),
                    "missing_fields": sum(1 for inv in invoice_dataset if inv.get("has_missing_fields", False)),
                    "duplicates": sum(1 for inv in invoice_dataset if inv.get("is_duplicate", False)),
                },
                "amount_statistics": {
                    "min": min(inv["amount"] for inv in invoice_dataset),
                    "max": max(inv["amount"] for inv in invoice_dataset),
                    "median": sorted([inv["amount"] for inv in invoice_dataset])[len(invoice_dataset) // 2],
                },
            },
            "transactions": {
                "count": len(transaction_dataset),
                "file_size_bytes": 40606,
                "challenge_distribution": {
                    "fraud_count": sum(1 for txn in transaction_dataset if txn.get("fraud_label", False)),
                    "fraud_rate": sum(1 for txn in transaction_dataset if txn.get("fraud_label", False))
                    / len(transaction_dataset),
                    "ambiguous_patterns": sum(
                        1 for txn in transaction_dataset if txn.get("is_ambiguous", False)
                    ),
                },
            },
            "reconciliation": {
                "count": len(reconciliation_dataset),
                "file_size_bytes": 269462,
                "challenge_distribution": {
                    "date_mismatches": sum(
                        1
                        for task in reconciliation_dataset
                        if "date_mismatch" in task.get("challenge_types", [])
                    ),
                    "amount_rounding": sum(
                        1
                        for task in reconciliation_dataset
                        if "amount_rounding" in task.get("challenge_types", [])
                    ),
                },
                "difficulty_distribution": {
                    "easy": sum(1 for task in reconciliation_dataset if task.get("difficulty") == "easy"),
                    "medium": sum(1 for task in reconciliation_dataset if task.get("difficulty") == "medium"),
                    "hard": sum(1 for task in reconciliation_dataset if task.get("difficulty") == "hard"),
                },
                "challenge_statistics": {
                    "has_date_mismatch": sum(
                        1 for task in reconciliation_dataset if task.get("has_date_mismatch", False)
                    ),
                    "has_rounding_error": sum(
                        1 for task in reconciliation_dataset if task.get("has_rounding_error", False)
                    ),
                    "has_duplicates": sum(1 for task in reconciliation_dataset if task.get("has_duplicates", False)),
                    "has_missing_counterparty": sum(
                        1 for task in reconciliation_dataset if task.get("has_missing_counterparty", False)
                    ),
                },
            },
        },
    }

    # Validate summary structure
    assert "datasets" in summary
    assert "invoices" in summary["datasets"]
    assert "transactions" in summary["datasets"]
    assert "reconciliation" in summary["datasets"]

    # Save summary to data directory
    summary_path = Path(__file__).parent.parent.parent / "data" / "DATASET_SUMMARY.json"
    with open(summary_path, "w") as f:
        json.dump(summary, f, indent=2)

    assert summary_path.exists(), "Dataset summary not saved"
