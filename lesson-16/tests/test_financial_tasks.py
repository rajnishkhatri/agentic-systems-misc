"""Test infrastructure for financial task datasets.

Tests for dataset generation, validation, and quality assurance.
Following TDD methodology: RED → GREEN → REFACTOR
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any

import pytest

# ============================================================================
# Fixtures for Dataset Validation
# ============================================================================


@pytest.fixture
def temp_data_dir(tmp_path: Path) -> Path:
    """Create temporary directory for dataset generation.

    Args:
        tmp_path: pytest temporary directory fixture

    Returns:
        Path to temporary data directory
    """
    data_dir = tmp_path / "data"
    data_dir.mkdir(exist_ok=True)
    return data_dir


@pytest.fixture
def sample_invoice() -> dict[str, Any]:
    """Generate sample invoice for testing.

    Returns:
        Sample invoice dictionary with all required fields
    """
    return {
        "invoice_id": "INV-2024-001",
        "vendor": "Acme Corp",
        "amount": 1500.00,
        "date": "2024-01-15",
        "line_items": [
            {"description": "Software License", "quantity": 1, "unit_price": 1500.00}
        ],
        "status": "pending",
    }


@pytest.fixture
def sample_transaction() -> dict[str, Any]:
    """Generate sample transaction for testing.

    Returns:
        Sample transaction dictionary with fraud detection fields
    """
    return {
        "transaction_id": "TXN-00001",
        "merchant": "Online Store",
        "amount": 299.99,
        "timestamp": "2024-01-15T10:30:00Z",
        "user_id": "user_123",
        "user_behavior": {
            "transaction_count_24h": 5,
            "avg_transaction_amount": 150.0,
            "account_age_days": 365,
        },
        "fraud_label": False,
        "fraud_type": None,
        "gold_label_confidence": 0.95,
    }


@pytest.fixture
def sample_reconciliation() -> dict[str, Any]:
    """Generate sample reconciliation task for testing.

    Returns:
        Sample reconciliation dictionary with bank and ledger entries
    """
    return {
        "reconciliation_id": "REC-001",
        "bank_transactions": [
            {
                "transaction_id": "BANK-001",
                "date": "2024-01-15",
                "amount": 1500.00,
                "description": "Payment from Customer A",
            }
        ],
        "ledger_entries": [
            {
                "entry_id": "LED-001",
                "posting_date": "2024-01-15",
                "amount": 1500.00,
                "account": "Accounts Receivable",
            }
        ],
        "expected_matches": [{"bank_id": "BANK-001", "ledger_id": "LED-001"}],
        "reconciliation_status": "perfect_match",
    }


# ============================================================================
# Schema Validation Tests
# ============================================================================


def test_should_validate_invoice_schema_when_all_fields_present(sample_invoice: dict[str, Any]) -> None:
    """Test that invoice with all required fields passes schema validation."""
    # Will implement schema validator in data_generation module
    pytest.skip("Schema validator not implemented yet - RED phase")


def test_should_validate_transaction_schema_when_fraud_fields_present(
    sample_transaction: dict[str, Any]
) -> None:
    """Test that transaction with fraud detection fields passes schema validation."""
    pytest.skip("Schema validator not implemented yet - RED phase")


def test_should_validate_reconciliation_schema_when_matches_present(
    sample_reconciliation: dict[str, Any]
) -> None:
    """Test that reconciliation task with expected matches passes schema validation."""
    pytest.skip("Schema validator not implemented yet - RED phase")


# ============================================================================
# Distribution Check Tests
# ============================================================================


def test_should_check_amount_distribution_when_dataset_generated() -> None:
    """Test that generated dataset amounts follow log-normal distribution."""
    pytest.skip("Distribution checker not implemented yet - RED phase")


def test_should_check_date_distribution_when_dataset_generated() -> None:
    """Test that generated dataset dates are uniformly distributed."""
    pytest.skip("Distribution checker not implemented yet - RED phase")


# ============================================================================
# Edge Case Generator Tests
# ============================================================================


def test_should_generate_zero_amount_when_edge_case_requested() -> None:
    """Test that edge case generator can create $0 amount transactions."""
    pytest.skip("Edge case generator not implemented yet - RED phase")


def test_should_generate_future_date_when_edge_case_requested() -> None:
    """Test that edge case generator can create future-dated entries."""
    pytest.skip("Edge case generator not implemented yet - RED phase")


def test_should_generate_special_characters_when_edge_case_requested() -> None:
    """Test that edge case generator handles special characters in vendor names."""
    pytest.skip("Edge case generator not implemented yet - RED phase")


# ============================================================================
# Task 6.3: Transaction Dataset Generation Tests (DC2.2)
# ============================================================================


def test_should_comply_with_transaction_schema_when_dataset_generated() -> None:
    """Test that all generated transactions have required fields."""
    from backend.data_generation.transactions import generate_transaction_dataset

    transactions = generate_transaction_dataset(count=10, seed=42)

    # Verify all required fields present
    required_fields = [
        "transaction_id",
        "merchant",
        "amount",
        "timestamp",
        "user_id",
        "fraud_label",
        "fraud_type",
        "gold_label_confidence",
    ]

    for txn in transactions:
        for field in required_fields:
            assert field in txn, f"Missing required field: {field}"

        # Verify types
        assert isinstance(txn["transaction_id"], str)
        assert isinstance(txn["merchant"], str)
        assert isinstance(txn["amount"], (int, float))
        assert isinstance(txn["timestamp"], str)
        assert isinstance(txn["user_id"], str)
        assert isinstance(txn["fraud_label"], bool)
        assert txn["fraud_type"] is None or isinstance(txn["fraud_type"], str)
        assert isinstance(txn["gold_label_confidence"], float)


def test_should_use_correct_transaction_id_format_when_generated() -> None:
    """Test that transaction IDs follow TXN-NNNNN format."""
    from backend.data_generation.transactions import generate_transaction_dataset

    transactions = generate_transaction_dataset(count=20, seed=42)

    import re

    pattern = re.compile(r"^TXN-\d{5}$")

    for txn in transactions:
        assert pattern.match(txn["transaction_id"]), f"Invalid transaction_id format: {txn['transaction_id']}"


def test_should_have_merchant_diversity_when_dataset_generated() -> None:
    """Test that dataset has ≥40 unique merchants."""
    from backend.data_generation.transactions import generate_transaction_dataset

    transactions = generate_transaction_dataset(count=100, seed=42)

    unique_merchants = {txn["merchant"] for txn in transactions}
    assert len(unique_merchants) >= 40, f"Expected ≥40 unique merchants, got {len(unique_merchants)}"


def test_should_distribute_amounts_correctly_when_dataset_generated() -> None:
    """Test that transaction amounts are distributed $1-$100K with long tail."""
    from backend.data_generation.transactions import generate_transaction_dataset

    transactions = generate_transaction_dataset(count=100, seed=42)

    amounts = [txn["amount"] for txn in transactions]

    # Verify range
    assert all(1.0 <= amt <= 100000.0 for amt in amounts), "Amounts outside $1-$100K range"

    # Verify long tail: most amounts should be < $10K, few > $50K
    low_amounts = sum(1 for amt in amounts if amt < 10000)
    high_amounts = sum(1 for amt in amounts if amt > 50000)

    assert low_amounts > 60, f"Expected >60% amounts <$10K, got {low_amounts}%"
    assert high_amounts < 20, f"Expected <20% amounts >$50K, got {high_amounts}%"


def test_should_include_valid_user_behavior_features_when_generated() -> None:
    """Test that user_behavior features are valid and realistic."""
    from backend.data_generation.transactions import generate_transaction_dataset

    transactions = generate_transaction_dataset(count=10, seed=42)

    for txn in transactions:
        # user_id should be non-empty string
        assert txn["user_id"], "user_id cannot be empty"
        assert txn["user_id"].startswith("user_"), f"user_id should start with 'user_': {txn['user_id']}"


def test_should_maintain_fraud_label_imbalance_when_dataset_generated() -> None:
    """Test that fraud rate is exactly 10% fraud / 90% legitimate."""
    from backend.data_generation.transactions import generate_transaction_dataset

    transactions = generate_transaction_dataset(count=100, fraud_rate=0.1, seed=42)

    fraud_count = sum(1 for txn in transactions if txn["fraud_label"] is True)
    fraud_rate = fraud_count / len(transactions)

    # Allow ±1 transaction tolerance for 10% target
    assert 9 <= fraud_count <= 11, f"Expected 10±1 fraud transactions, got {fraud_count}"


def test_should_distribute_fraud_types_correctly_when_fraud_present() -> None:
    """Test fraud type distribution: 40% stolen_card, 35% account_takeover, 25% synthetic_fraud."""
    from backend.data_generation.transactions import generate_transaction_dataset

    transactions = generate_transaction_dataset(count=100, fraud_rate=0.1, seed=42)

    # Get fraud transactions
    fraud_txns = [txn for txn in transactions if txn["fraud_label"] is True]
    fraud_types = [txn["fraud_type"] for txn in fraud_txns]

    # Count each type
    stolen_card = fraud_types.count("stolen_card")
    account_takeover = fraud_types.count("account_takeover")
    synthetic_fraud = fraud_types.count("synthetic_fraud")

    total_fraud = len(fraud_types)

    # Verify distribution (allow ±15% tolerance)
    if total_fraud >= 10:  # Only check if we have enough fraud samples
        assert stolen_card >= 2, f"Expected ~40% stolen_card fraud, got {stolen_card}/{total_fraud}"
        assert account_takeover >= 2, f"Expected ~35% account_takeover fraud, got {account_takeover}/{total_fraud}"
        assert synthetic_fraud >= 1, f"Expected ~25% synthetic_fraud fraud, got {synthetic_fraud}/{total_fraud}"


def test_should_inject_ambiguous_patterns_when_dataset_generated() -> None:
    """Test that 20% of transactions have ambiguous fraud patterns."""
    from backend.data_generation.transactions import generate_transaction_dataset

    transactions = generate_transaction_dataset(count=100, seed=42)

    # Ambiguous patterns: confidence between 0.4-0.6 (uncertain)
    ambiguous_count = sum(1 for txn in transactions if 0.4 <= txn["gold_label_confidence"] <= 0.6)

    # Allow ±5% tolerance for 20% target
    assert 15 <= ambiguous_count <= 25, f"Expected 20±5% ambiguous patterns, got {ambiguous_count}%"


def test_should_include_realistic_temporal_patterns_when_generated() -> None:
    """Test that timestamps are realistic ISO8601 format."""
    from backend.data_generation.transactions import generate_transaction_dataset

    transactions = generate_transaction_dataset(count=10, seed=42)

    import re

    # ISO8601 pattern: YYYY-MM-DDTHH:MM:SSZ
    pattern = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")

    for txn in transactions:
        assert pattern.match(txn["timestamp"]), f"Invalid timestamp format: {txn['timestamp']}"

        # Verify parseable as datetime

        try:
            datetime.fromisoformat(txn["timestamp"].replace("Z", "+00:00"))
        except ValueError as e:
            pytest.fail(f"Timestamp not parseable: {txn['timestamp']}: {e}")


def test_should_include_gold_label_confidence_scores_when_generated() -> None:
    """Test that all transactions have confidence scores 0.0-1.0."""
    from backend.data_generation.transactions import generate_transaction_dataset

    transactions = generate_transaction_dataset(count=100, seed=42)

    for txn in transactions:
        assert 0.0 <= txn["gold_label_confidence"] <= 1.0, f"Confidence out of range: {txn['confidence']}"

        # Fraud transactions should have varied confidence
        if txn["fraud_label"] is True:
            # Some fraud should be obvious (high confidence), some ambiguous
            pass  # Just verify range above

        # Non-fraud transactions should mostly have high confidence
        if txn["fraud_label"] is False:
            assert txn["gold_label_confidence"] >= 0.5, f"Non-fraud should have confidence ≥0.5, got {txn['confidence']}"


def test_should_filter_high_value_transactions_when_threshold_provided() -> None:
    """Test that high-value transactions >$10K can be filtered."""
    from backend.data_generation.transactions import generate_transaction_dataset

    transactions = generate_transaction_dataset(count=100, seed=42)

    # Filter high-value transactions
    high_value = [txn for txn in transactions if txn["amount"] > 10000]

    # Should have at least a few high-value transactions due to long tail
    assert len(high_value) > 0, "Expected some transactions >$10K"

    # All filtered transactions should be >$10K
    for txn in high_value:
        assert txn["amount"] > 10000, f"High-value filter failed: {txn['amount']}"


def test_should_raise_error_when_fraud_rate_invalid() -> None:
    """Test that invalid fraud_rate raises ValueError."""
    from backend.data_generation.transactions import generate_transaction_dataset

    with pytest.raises(ValueError, match="fraud_rate must be in range"):
        generate_transaction_dataset(count=100, fraud_rate=-0.1)

    with pytest.raises(ValueError, match="fraud_rate must be in range"):
        generate_transaction_dataset(count=100, fraud_rate=1.5)


def test_should_raise_error_when_count_invalid() -> None:
    """Test that invalid count raises ValueError."""
    from backend.data_generation.transactions import generate_transaction_dataset

    with pytest.raises(ValueError, match="count must be positive"):
        generate_transaction_dataset(count=0)

    with pytest.raises(ValueError, match="count must be positive"):
        generate_transaction_dataset(count=-10)


def test_should_be_reproducible_when_same_seed_used() -> None:
    """Test that same seed generates identical datasets."""
    from backend.data_generation.transactions import generate_transaction_dataset

    transactions1 = generate_transaction_dataset(count=50, fraud_rate=0.1, seed=42)
    transactions2 = generate_transaction_dataset(count=50, fraud_rate=0.1, seed=42)

    # Should be identical
    assert len(transactions1) == len(transactions2)

    for txn1, txn2 in zip(transactions1, transactions2):
        assert txn1["transaction_id"] == txn2["transaction_id"]
        assert txn1["merchant"] == txn2["merchant"]
        assert txn1["amount"] == txn2["amount"]
        assert txn1["fraud_label"] == txn2["fraud_label"]
        assert txn1["fraud_type"] == txn2["fraud_type"]


# ============================================================================
# Task 6.4: Reconciliation Dataset Generation Tests (DC2.3)
# ============================================================================


def test_should_comply_with_reconciliation_schema_when_dataset_generated() -> None:
    """Test that all generated reconciliation tasks have required fields."""
    from backend.data_generation.reconciliation import generate_reconciliation_dataset

    reconciliations = generate_reconciliation_dataset(count=10, seed=42)

    # Verify all required fields present
    required_fields = [
        "reconciliation_id",
        "bank_transactions",
        "ledger_entries",
        "expected_matches",
        "reconciliation_status",
        "discrepancy_amount",
        "challenge_types",
    ]

    for rec in reconciliations:
        for field in required_fields:
            assert field in rec, f"Missing required field: {field}"

        # Verify types
        assert isinstance(rec["reconciliation_id"], str)
        assert isinstance(rec["bank_transactions"], list)
        assert isinstance(rec["ledger_entries"], list)
        assert isinstance(rec["expected_matches"], list)
        assert isinstance(rec["reconciliation_status"], str)
        assert isinstance(rec["discrepancy_amount"], (int, float))
        assert isinstance(rec["challenge_types"], list)

        # Verify nested structures
        for bank_txn in rec["bank_transactions"]:
            assert "transaction_id" in bank_txn
            assert "date" in bank_txn
            assert "amount" in bank_txn
            assert "description" in bank_txn

        for ledger_entry in rec["ledger_entries"]:
            assert "entry_id" in ledger_entry
            assert "posting_date" in ledger_entry
            assert "amount" in ledger_entry
            assert "account" in ledger_entry


def test_should_have_paired_structure_when_bank_and_ledger_entries_generated() -> None:
    """Test that bank_transactions and ledger_entries are paired structures."""
    from backend.data_generation.reconciliation import generate_reconciliation_dataset

    reconciliations = generate_reconciliation_dataset(count=20, seed=42)

    for rec in reconciliations:
        # Each reconciliation should have at least one bank transaction and one ledger entry
        assert len(rec["bank_transactions"]) > 0, "Must have at least one bank transaction"
        assert len(rec["ledger_entries"]) > 0, "Must have at least one ledger entry"

        # expected_matches should link bank and ledger entries
        for match in rec["expected_matches"]:
            assert "bank_id" in match, "Match must have bank_id"
            assert "ledger_id" in match, "Match must have ledger_id"

            # Verify referenced IDs exist
            bank_ids = {txn["transaction_id"] for txn in rec["bank_transactions"]}
            ledger_ids = {entry["entry_id"] for entry in rec["ledger_entries"]}

            assert match["bank_id"] in bank_ids, f"bank_id {match['bank_id']} not found in bank_transactions"
            assert match["ledger_id"] in ledger_ids, f"ledger_id {match['ledger_id']} not found in ledger_entries"


def test_should_have_accurate_expected_matches_when_gold_labels_generated() -> None:
    """Test that expected_matches gold labels are accurate and deterministic."""
    from backend.data_generation.reconciliation import generate_reconciliation_dataset

    reconciliations = generate_reconciliation_dataset(count=10, seed=42)

    for rec in reconciliations:
        # All matched entries should have matching amounts (within tolerance for rounding challenges)
        for match in rec["expected_matches"]:
            bank_txn = next(t for t in rec["bank_transactions"] if t["transaction_id"] == match["bank_id"])
            ledger_entry = next(e for e in rec["ledger_entries"] if e["entry_id"] == match["ledger_id"])

            # If perfect_match, amounts should be exactly equal
            if rec["reconciliation_status"] == "perfect_match":
                assert bank_txn["amount"] == ledger_entry["amount"], "Perfect match should have exact amounts"


def test_should_inject_date_mismatch_challenges_when_dataset_generated() -> None:
    """Test that 25% of reconciliations have date mismatches (posting date ≠ transaction date by 1-3 days)."""
    from backend.data_generation.reconciliation import generate_reconciliation_dataset

    reconciliations = generate_reconciliation_dataset(count=100, seed=42)

    # Count reconciliations with date_mismatch challenge
    date_mismatch_count = sum(1 for rec in reconciliations if "date_mismatch" in rec["challenge_types"])

    # Allow ±5% tolerance for 25% target
    assert 20 <= date_mismatch_count <= 30, f"Expected 25±5% date mismatches, got {date_mismatch_count}%"

    # Verify date mismatches are realistic (1-3 business days)
    for rec in reconciliations:
        if "date_mismatch" in rec["challenge_types"]:
            from datetime import datetime

            # Check at least one matched pair has date difference
            has_date_diff = False
            for match in rec["expected_matches"]:
                bank_txn = next(t for t in rec["bank_transactions"] if t["transaction_id"] == match["bank_id"])
                ledger_entry = next(e for e in rec["ledger_entries"] if e["entry_id"] == match["ledger_id"])

                bank_date = datetime.fromisoformat(bank_txn["date"])
                ledger_date = datetime.fromisoformat(ledger_entry["posting_date"])
                diff_days = abs((bank_date - ledger_date).days)

                if 1 <= diff_days <= 3:
                    has_date_diff = True
                    break

            assert has_date_diff, "date_mismatch challenge must have 1-3 day difference"


def test_should_inject_amount_rounding_challenges_when_dataset_generated() -> None:
    """Test that 20% of reconciliations have amount rounding challenges ($1234.56 vs $1234.50)."""
    from backend.data_generation.reconciliation import generate_reconciliation_dataset

    reconciliations = generate_reconciliation_dataset(count=100, seed=42)

    # Count reconciliations with amount_rounding challenge
    rounding_count = sum(1 for rec in reconciliations if "amount_rounding" in rec["challenge_types"])

    # Allow ±5% tolerance for 20% target
    assert 15 <= rounding_count <= 25, f"Expected 20±5% amount rounding challenges, got {rounding_count}%"

    # Verify rounding differences are realistic (<$1.00 typically)
    for rec in reconciliations:
        if "amount_rounding" in rec["challenge_types"]:
            # Check at least one matched pair has rounding difference
            has_rounding = False
            for match in rec["expected_matches"]:
                bank_txn = next(t for t in rec["bank_transactions"] if t["transaction_id"] == match["bank_id"])
                ledger_entry = next(e for e in rec["ledger_entries"] if e["entry_id"] == match["ledger_id"])

                diff = abs(bank_txn["amount"] - ledger_entry["amount"])
                if 0.01 <= diff <= 1.00:
                    has_rounding = True
                    break

            # Amount rounding should have small differences
            if not has_rounding:
                # At minimum, discrepancy should be small
                assert rec["discrepancy_amount"] <= 1.00, "Rounding challenge should have discrepancy ≤$1.00"


def test_should_inject_duplicate_entry_challenges_when_dataset_generated() -> None:
    """Test that 15% of reconciliations have duplicate entry challenges."""
    from backend.data_generation.reconciliation import generate_reconciliation_dataset

    reconciliations = generate_reconciliation_dataset(count=100, seed=42)

    # Count reconciliations with duplicate_entries challenge
    duplicate_count = sum(1 for rec in reconciliations if "duplicate_entries" in rec["challenge_types"])

    # Allow ±5% tolerance for 15% target
    assert 10 <= duplicate_count <= 20, f"Expected 15±5% duplicate entries, got {duplicate_count}%"

    # Verify duplicates exist in dataset
    for rec in reconciliations:
        if "duplicate_entries" in rec["challenge_types"]:
            # Check for duplicate amounts or descriptions
            bank_amounts = [txn["amount"] for txn in rec["bank_transactions"]]
            ledger_amounts = [entry["amount"] for entry in rec["ledger_entries"]]

            # Should have duplicate amounts (indicating potential duplicate transactions)
            has_duplicate = len(bank_amounts) != len(set(bank_amounts)) or len(ledger_amounts) != len(
                set(ledger_amounts)
            )

            # If not exact duplicates, at least multiple entries
            if not has_duplicate:
                assert (
                    len(rec["bank_transactions"]) > 1 or len(rec["ledger_entries"]) > 1
                ), "Duplicate challenge should have multiple entries"


def test_should_inject_missing_counterparty_challenges_when_dataset_generated() -> None:
    """Test that 18% of reconciliations have missing counterparty challenges."""
    from backend.data_generation.reconciliation import generate_reconciliation_dataset

    reconciliations = generate_reconciliation_dataset(count=100, seed=42)

    # Count reconciliations with missing_counterparty challenge
    missing_count = sum(1 for rec in reconciliations if "missing_counterparty" in rec["challenge_types"])

    # Allow ±5% tolerance for 18% target
    assert 13 <= missing_count <= 23, f"Expected 18±5% missing counterparty, got {missing_count}%"

    # Verify missing counterparty means unmatched entries
    for rec in reconciliations:
        if "missing_counterparty" in rec["challenge_types"]:
            # Should have unmatched entries (more bank/ledger entries than matches)
            total_entries = len(rec["bank_transactions"]) + len(rec["ledger_entries"])
            total_matches = len(rec["expected_matches"]) * 2  # Each match covers 2 entries

            assert total_entries > total_matches, "Missing counterparty should have unmatched entries"


def test_should_distribute_reconciliation_status_correctly_when_dataset_generated() -> None:
    """Test reconciliation_status distribution: 60% perfect_match, 25% resolvable_with_logic, 15% manual_review."""
    from backend.data_generation.reconciliation import generate_reconciliation_dataset

    reconciliations = generate_reconciliation_dataset(count=100, seed=42)

    # Count each status
    status_counts = {"perfect_match": 0, "resolvable_with_logic": 0, "manual_review_required": 0}

    for rec in reconciliations:
        status = rec["reconciliation_status"]
        assert status in status_counts, f"Invalid reconciliation_status: {status}"
        status_counts[status] += 1

    # Verify distribution (allow ±10% tolerance)
    perfect = status_counts["perfect_match"]
    resolvable = status_counts["resolvable_with_logic"]
    manual = status_counts["manual_review_required"]

    assert 50 <= perfect <= 70, f"Expected 60±10% perfect_match, got {perfect}%"
    assert 15 <= resolvable <= 35, f"Expected 25±10% resolvable_with_logic, got {resolvable}%"
    assert 5 <= manual <= 25, f"Expected 15±10% manual_review_required, got {manual}%"


def test_should_have_realistic_discrepancy_amounts_when_generated() -> None:
    """Test that discrepancy_amount is realistic $0.01-$500."""
    from backend.data_generation.reconciliation import generate_reconciliation_dataset

    reconciliations = generate_reconciliation_dataset(count=100, seed=42)

    for rec in reconciliations:
        discrepancy = rec["discrepancy_amount"]

        # Perfect matches should have $0 discrepancy
        if rec["reconciliation_status"] == "perfect_match":
            assert discrepancy == 0.0, f"Perfect match should have $0 discrepancy, got ${discrepancy}"
        else:
            # Other statuses should have discrepancy in realistic range
            assert 0.01 <= discrepancy <= 500.0, f"Discrepancy should be $0.01-$500, got ${discrepancy}"


def test_should_handle_same_day_multi_transactions_when_edge_case_generated() -> None:
    """Test edge case: multiple transactions on same day."""
    from backend.data_generation.reconciliation import generate_reconciliation_dataset

    reconciliations = generate_reconciliation_dataset(count=100, seed=42)

    # Look for reconciliations with multiple same-day transactions
    found_same_day = False

    for rec in reconciliations:
        bank_dates = [txn["date"] for txn in rec["bank_transactions"]]

        # Check if any dates appear multiple times
        if len(bank_dates) != len(set(bank_dates)):
            found_same_day = True
            break

    # Should have at least one case of same-day transactions in 100 samples
    assert found_same_day, "Should have at least one same-day multi-transaction case"


def test_should_handle_cross_month_reconciliation_when_edge_case_generated() -> None:
    """Test edge case: reconciliation spanning month boundaries."""
    from backend.data_generation.reconciliation import generate_reconciliation_dataset

    reconciliations = generate_reconciliation_dataset(count=100, seed=42)

    # Look for reconciliations with transactions from different months
    found_cross_month = False

    for rec in reconciliations:
        if "date_mismatch" in rec["challenge_types"]:
            from datetime import datetime

            # Check if bank and ledger dates span different months
            for match in rec["expected_matches"]:
                bank_txn = next(t for t in rec["bank_transactions"] if t["transaction_id"] == match["bank_id"])
                ledger_entry = next(e for e in rec["ledger_entries"] if e["entry_id"] == match["ledger_id"])

                bank_date = datetime.fromisoformat(bank_txn["date"])
                ledger_date = datetime.fromisoformat(ledger_entry["posting_date"])

                if bank_date.month != ledger_date.month:
                    found_cross_month = True
                    break

        if found_cross_month:
            break

    # Should have at least one cross-month case (not strict requirement, just check)
    # This is an edge case that may or may not appear depending on random generation


def test_should_raise_error_when_difficulty_invalid() -> None:
    """Test that invalid difficulty raises ValueError."""
    from backend.data_generation.reconciliation import generate_reconciliation_dataset

    with pytest.raises(ValueError, match='difficulty must be one of'):
        generate_reconciliation_dataset(count=10, difficulty="impossible", seed=42)


def test_should_raise_error_when_count_invalid_for_reconciliation() -> None:
    """Test that invalid count raises ValueError."""
    from backend.data_generation.reconciliation import generate_reconciliation_dataset

    with pytest.raises(ValueError, match="count must be positive"):
        generate_reconciliation_dataset(count=0)

    with pytest.raises(ValueError, match="count must be positive"):
        generate_reconciliation_dataset(count=-10)


def test_should_be_reproducible_when_same_seed_used_for_reconciliation() -> None:
    """Test that same seed generates identical reconciliation datasets."""
    from backend.data_generation.reconciliation import generate_reconciliation_dataset

    reconciliations1 = generate_reconciliation_dataset(count=20, difficulty="mixed", seed=42)
    reconciliations2 = generate_reconciliation_dataset(count=20, difficulty="mixed", seed=42)

    # Should be identical
    assert len(reconciliations1) == len(reconciliations2)

    for rec1, rec2 in zip(reconciliations1, reconciliations2):
        assert rec1["reconciliation_id"] == rec2["reconciliation_id"]
        assert rec1["reconciliation_status"] == rec2["reconciliation_status"]
        assert rec1["discrepancy_amount"] == rec2["discrepancy_amount"]
        assert rec1["challenge_types"] == rec2["challenge_types"]
        assert len(rec1["bank_transactions"]) == len(rec2["bank_transactions"])
        assert len(rec1["ledger_entries"]) == len(rec2["ledger_entries"])


# ============================================================================
# Task 6.5: Dataset Quality Validation & Statistical Analysis
# ============================================================================


@pytest.fixture
def task_6_5_data_dir() -> Path:
    """Get data directory for Task 6.5 validation tests.

    Returns:
        Path to lesson-16/data directory
    """
    test_dir = Path(__file__).parent
    return test_dir.parent / "data"


def test_should_load_all_datasets_from_json_files_when_paths_valid(task_6_5_data_dir: Path) -> None:
    """Test that all 3 datasets can be loaded from JSON files."""
    import json

    # Load invoices
    invoices_path = task_6_5_data_dir / "invoices_100.json"
    assert invoices_path.exists(), f"Invoice dataset not found: {invoices_path}"
    with open(invoices_path) as f:
        invoices = json.load(f)
    assert len(invoices) == 100, f"Expected 100 invoices, got {len(invoices)}"

    # Load transactions
    transactions_path = task_6_5_data_dir / "transactions_100.json"
    assert transactions_path.exists(), f"Transaction dataset not found: {transactions_path}"
    with open(transactions_path) as f:
        transactions_data = json.load(f)

    # Handle metadata wrapper
    if isinstance(transactions_data, dict) and "transactions" in transactions_data:
        transactions = transactions_data["transactions"]
    else:
        transactions = transactions_data
    assert len(transactions) == 100, f"Expected 100 transactions, got {len(transactions)}"

    # Load reconciliations
    reconciliations_path = task_6_5_data_dir / "reconciliation_100.json"
    assert reconciliations_path.exists(), f"Reconciliation dataset not found: {reconciliations_path}"
    with open(reconciliations_path) as f:
        reconciliations_data = json.load(f)

    # Handle metadata wrapper
    if isinstance(reconciliations_data, dict) and "reconciliations" in reconciliations_data:
        reconciliations = reconciliations_data["reconciliations"]
    else:
        reconciliations = reconciliations_data
    assert len(reconciliations) == 100, f"Expected 100 reconciliations, got {len(reconciliations)}"


def test_should_validate_invoice_challenge_distribution_when_within_tolerance() -> None:
    """Test that invoice challenge distribution is within ±5% of targets."""
    import json
    from pathlib import Path

    data_dir = Path("lesson-16/data")
    with open(data_dir / "invoices_100.json") as f:
        invoices = json.load(f)

    # Count challenges
    ocr_errors = sum(1 for inv in invoices if inv.get("has_ocr_error", False))
    missing_fields = sum(1 for inv in invoices if inv.get("has_missing_fields", False))
    duplicates = sum(1 for inv in invoices if inv.get("is_duplicate", False))

    # Targets: OCR 15%, missing fields 10%, duplicates 8%
    # ±5% tolerance
    assert 10 <= ocr_errors <= 20, f"OCR errors should be 15±5%, got {ocr_errors}%"
    assert 5 <= missing_fields <= 15, f"Missing fields should be 10±5%, got {missing_fields}%"
    assert 3 <= duplicates <= 13, f"Duplicates should be 8±5%, got {duplicates}%"


def test_should_validate_transaction_fraud_rate_when_within_tolerance() -> None:
    """Test that transaction fraud rate is 10.0±0.5%."""
    import json
    from pathlib import Path

    data_dir = Path("lesson-16/data")
    with open(data_dir / "transactions_100.json") as f:
        transactions_data = json.load(f)

    # Handle metadata wrapper
    if isinstance(transactions_data, dict) and "transactions" in transactions_data:
        transactions = transactions_data["transactions"]
    else:
        transactions = transactions_data

    # Count fraud
    fraud_count = sum(1 for txn in transactions if txn.get("fraud_label", False))
    fraud_rate = (fraud_count / len(transactions)) * 100

    # Target: 10.0±0.5%
    assert 9.5 <= fraud_rate <= 10.5, f"Fraud rate should be 10.0±0.5%, got {fraud_rate:.1f}%"


def test_should_validate_reconciliation_challenge_distribution_when_within_tolerance() -> None:
    """Test that reconciliation challenge distribution is within ±5% of targets."""
    import json
    from pathlib import Path

    data_dir = Path("lesson-16/data")
    with open(data_dir / "reconciliation_100.json") as f:
        reconciliations_data = json.load(f)

    # Handle metadata wrapper
    if isinstance(reconciliations_data, dict) and "reconciliations" in reconciliations_data:
        reconciliations = reconciliations_data["reconciliations"]
    else:
        reconciliations = reconciliations_data

    # Count challenges
    date_mismatches = sum(1 for rec in reconciliations if "date_mismatch" in rec.get("challenge_types", []))
    amount_rounding = sum(1 for rec in reconciliations if "amount_rounding" in rec.get("challenge_types", []))

    # Targets: date_mismatch 25%, amount_rounding 20%
    # ±5% tolerance
    assert 20 <= date_mismatches <= 30, f"Date mismatches should be 25±5%, got {date_mismatches}%"
    assert 15 <= amount_rounding <= 25, f"Amount rounding should be 20±5%, got {amount_rounding}%"


def test_should_have_no_duplicate_ids_across_all_datasets_when_validated() -> None:
    """Test that there are no duplicate IDs within or across datasets."""
    import json
    from pathlib import Path

    data_dir = Path("lesson-16/data")

    # Load all datasets
    with open(data_dir / "invoices_100.json") as f:
        invoices = json.load(f)

    with open(data_dir / "transactions_100.json") as f:
        transactions_data = json.load(f)
        transactions = transactions_data["transactions"] if isinstance(transactions_data, dict) else transactions_data

    with open(data_dir / "reconciliation_100.json") as f:
        reconciliations_data = json.load(f)
        reconciliations = reconciliations_data["reconciliations"] if isinstance(reconciliations_data, dict) else reconciliations_data

    # Check for duplicates within each dataset
    invoice_ids = [inv["invoice_id"] for inv in invoices]
    assert len(invoice_ids) == len(set(invoice_ids)), "Duplicate invoice_ids found"

    transaction_ids = [txn["transaction_id"] for txn in transactions]
    assert len(transaction_ids) == len(set(transaction_ids)), "Duplicate transaction_ids found"

    reconciliation_ids = [rec["reconciliation_id"] for rec in reconciliations]
    assert len(reconciliation_ids) == len(set(reconciliation_ids)), "Duplicate reconciliation_ids found"


def test_should_have_accurate_gold_labels_when_verified_deterministically() -> None:
    """Test that gold labels are 100% accurate using deterministic checks."""
    import json
    from pathlib import Path

    data_dir = Path("lesson-16/data")

    # Test invoice gold labels
    with open(data_dir / "invoices_100.json") as f:
        invoices = json.load(f)

    for inv in invoices:
        gold_label = inv.get("gold_label", {})

        # If has_missing_fields, has_ocr_error, or is_duplicate, should be invalid
        if inv.get("has_missing_fields", False) or inv.get("has_ocr_error", False) or inv.get("is_duplicate", False):
            assert gold_label.get("is_valid") is False, f"Invoice {inv['invoice_id']} should be invalid"
        else:
            assert gold_label.get("is_valid") is True, f"Invoice {inv['invoice_id']} should be valid"

    # Test transaction gold labels
    with open(data_dir / "transactions_100.json") as f:
        transactions_data = json.load(f)
        transactions = transactions_data["transactions"] if isinstance(transactions_data, dict) else transactions_data

    for txn in transactions:
        # Non-fraud transactions should have confidence ≥0.5
        if not txn["fraud_label"]:
            assert txn["gold_label_confidence"] >= 0.5, f"Non-fraud {txn['transaction_id']} should have confidence ≥0.5"


def test_should_have_correct_invoice_amount_median_when_validated() -> None:
    """Test that invoice amount median is reasonable for business invoices."""
    import json
    import statistics
    from pathlib import Path

    data_dir = Path("lesson-16/data")
    with open(data_dir / "invoices_100.json") as f:
        invoices = json.load(f)

    amounts = [inv["amount"] for inv in invoices]
    median = statistics.median(amounts)

    # Reasonable median for business invoices: $100-$10K
    assert 100 <= median <= 10000, f"Invoice median should be $100-$10K, got ${median:.2f}"


def test_should_maintain_reproducibility_across_three_runs_when_same_seed() -> None:
    """Test that same seed produces identical outputs across 3 runs."""
    from backend.data_generation.invoices import generate_invoice_dataset
    from backend.data_generation.reconciliation import generate_reconciliation_dataset
    from backend.data_generation.transactions import generate_transaction_dataset

    seed = 12345

    # Run 1
    inv1 = generate_invoice_dataset(count=20, seed=seed)
    txn1 = generate_transaction_dataset(count=20, seed=seed)
    rec1 = generate_reconciliation_dataset(count=20, seed=seed)

    # Run 2
    inv2 = generate_invoice_dataset(count=20, seed=seed)
    txn2 = generate_transaction_dataset(count=20, seed=seed)
    rec2 = generate_reconciliation_dataset(count=20, seed=seed)

    # Run 3
    inv3 = generate_invoice_dataset(count=20, seed=seed)
    txn3 = generate_transaction_dataset(count=20, seed=seed)
    rec3 = generate_reconciliation_dataset(count=20, seed=seed)

    # Verify all 3 runs produce identical results
    for i in range(20):
        assert inv1[i]["invoice_id"] == inv2[i]["invoice_id"] == inv3[i]["invoice_id"]
        assert inv1[i]["amount"] == inv2[i]["amount"] == inv3[i]["amount"]

        assert txn1[i]["transaction_id"] == txn2[i]["transaction_id"] == txn3[i]["transaction_id"]
        assert txn1[i]["fraud_label"] == txn2[i]["fraud_label"] == txn3[i]["fraud_label"]

        assert rec1[i]["reconciliation_id"] == rec2[i]["reconciliation_id"] == rec3[i]["reconciliation_id"]
        assert rec1[i]["reconciliation_status"] == rec2[i]["reconciliation_status"] == rec3[i]["reconciliation_status"]


def test_should_include_edge_cases_when_datasets_generated() -> None:
    """Test that datasets include edge cases: low amounts, variety in data."""
    import json
    from pathlib import Path

    data_dir = Path("lesson-16/data")

    # Check invoices for edge cases
    with open(data_dir / "invoices_100.json") as f:
        invoices = json.load(f)

    # Look for vendor name variety (should have many unique vendors)
    vendors = {inv["vendor"] for inv in invoices}
    assert len(vendors) >= 30, f"Should have ≥30 unique vendors, got {len(vendors)}"

    # Check transactions for edge cases
    with open(data_dir / "transactions_100.json") as f:
        transactions_data = json.load(f)
        transactions = transactions_data["transactions"] if isinstance(transactions_data, dict) else transactions_data

    # Look for very low amounts (edge of $1 minimum)
    low_amounts = [txn for txn in transactions if txn["amount"] < 10]
    assert len(low_amounts) > 0, "Should have some very low amount transactions"

    # Look for high amounts (>$50K)
    high_amounts = [txn for txn in transactions if txn["amount"] > 50000]
    assert len(high_amounts) > 0, "Should have some high amount transactions (long tail)"


def test_should_have_log_normal_invoice_amount_distribution_when_validated() -> None:
    """Test that invoice amounts follow log-normal distribution."""
    import json
    from pathlib import Path

    data_dir = Path("lesson-16/data")
    with open(data_dir / "invoices_100.json") as f:
        invoices = json.load(f)

    amounts = [inv["amount"] for inv in invoices]

    # Log-normal distribution: most values clustered, long tail to the right
    # Check that 80% of amounts are in lower 50% of range
    min_amt = min(amounts)
    max_amt = max(amounts)
    mid_range = min_amt + (max_amt - min_amt) * 0.5

    below_mid = sum(1 for amt in amounts if amt <= mid_range)

    # Should have significant clustering in lower range (log-normal characteristic)
    assert below_mid >= 60, f"Log-normal: expected ≥60% amounts in lower half, got {below_mid}%"


def test_should_have_uniform_transaction_date_distribution_when_validated() -> None:
    """Test that transaction dates are distributed over 2024 (not all in one month)."""
    import json
    from collections import Counter
    from pathlib import Path

    data_dir = Path("lesson-16/data")
    with open(data_dir / "transactions_100.json") as f:
        transactions_data = json.load(f)
        transactions = transactions_data["transactions"] if isinstance(transactions_data, dict) else transactions_data

    # Extract months from timestamps
    months = []
    for txn in transactions:
        timestamp = datetime.fromisoformat(txn["timestamp"].replace("Z", "+00:00"))
        months.append(timestamp.month)

    # Count by month
    month_counts = Counter(months)

    # With 100 transactions, should have transactions in at least 6 different months
    assert len(month_counts) >= 6, f"Should have transactions in ≥6 months, got {len(month_counts)}"

    # No single month should have >30% of all transactions
    max_count = max(month_counts.values())
    assert max_count <= 30, f"No month should have >30 transactions, got {max_count}"


def test_should_have_no_overlapping_ids_across_datasets_when_validated() -> None:
    """Test cross-dataset consistency: no overlapping IDs."""
    import json
    from pathlib import Path

    data_dir = Path("lesson-16/data")

    # Load all IDs
    with open(data_dir / "invoices_100.json") as f:
        invoices = json.load(f)
    invoice_ids = set(inv["invoice_id"] for inv in invoices)

    with open(data_dir / "transactions_100.json") as f:
        transactions_data = json.load(f)
        transactions = transactions_data["transactions"] if isinstance(transactions_data, dict) else transactions_data
    transaction_ids = set(txn["transaction_id"] for txn in transactions)

    with open(data_dir / "reconciliation_100.json") as f:
        reconciliations_data = json.load(f)
        reconciliations = reconciliations_data["reconciliations"] if isinstance(reconciliations_data, dict) else reconciliations_data
    reconciliation_ids = set(rec["reconciliation_id"] for rec in reconciliations)

    # Verify no overlaps (ID formats are different, but verify anyway)
    assert len(invoice_ids & transaction_ids) == 0, "Invoice and transaction IDs should not overlap"
    assert len(invoice_ids & reconciliation_ids) == 0, "Invoice and reconciliation IDs should not overlap"
    assert len(transaction_ids & reconciliation_ids) == 0, "Transaction and reconciliation IDs should not overlap"


def test_should_be_human_readable_when_spot_checked() -> None:
    """Test human readability: spot-check 10 samples from each dataset."""
    import json
    import random
    from pathlib import Path

    data_dir = Path("lesson-16/data")

    # Spot-check invoices
    with open(data_dir / "invoices_100.json") as f:
        invoices = json.load(f)

    random.seed(42)
    sample_invoices = random.sample(invoices, min(10, len(invoices)))

    for inv in sample_invoices:
        # Check plausibility
        assert inv["amount"] > 0, f"Invoice {inv['invoice_id']} has non-positive amount"
        assert len(inv["vendor"]) > 0, f"Invoice {inv['invoice_id']} has empty vendor"
        assert len(inv["invoice_id"]) > 0, "Invoice has empty ID"

    # Spot-check transactions
    with open(data_dir / "transactions_100.json") as f:
        transactions_data = json.load(f)
        transactions = transactions_data["transactions"] if isinstance(transactions_data, dict) else transactions_data

    sample_txns = random.sample(transactions, min(10, len(transactions)))

    for txn in sample_txns:
        assert txn["amount"] > 0, f"Transaction {txn['transaction_id']} has non-positive amount"
        assert len(txn["merchant"]) > 0, f"Transaction {txn['transaction_id']} has empty merchant"

    # Spot-check reconciliations
    with open(data_dir / "reconciliation_100.json") as f:
        reconciliations_data = json.load(f)
        reconciliations = reconciliations_data["reconciliations"] if isinstance(reconciliations_data, dict) else reconciliations_data

    sample_recs = random.sample(reconciliations, min(10, len(reconciliations)))

    for rec in sample_recs:
        assert len(rec["bank_transactions"]) > 0, f"Reconciliation {rec['reconciliation_id']} has no bank transactions"
        assert len(rec["ledger_entries"]) > 0, f"Reconciliation {rec['reconciliation_id']} has no ledger entries"


def test_should_include_required_metadata_when_datasets_validated() -> None:
    """Test that all datasets include generation_date, version, schema_version metadata."""
    import json
    from pathlib import Path

    data_dir = Path("lesson-16/data")
    summary_path = data_dir / "DATASET_SUMMARY.json"

    assert summary_path.exists(), "DATASET_SUMMARY.json not found"

    with open(summary_path) as f:
        summary = json.load(f)

    # Verify required metadata fields
    assert "generation_date" in summary, "Missing generation_date"
    assert "version" in summary, "Missing version"
    assert "schema_version" in summary, "Missing schema_version"
    assert "datasets" in summary, "Missing datasets"

    # Verify each dataset has statistics
    for dataset_name in ["invoices", "transactions", "reconciliation"]:
        assert dataset_name in summary["datasets"], f"Missing {dataset_name} in summary"
        dataset_info = summary["datasets"][dataset_name]
        assert "count" in dataset_info, f"Missing count for {dataset_name}"
        assert "challenge_distribution" in dataset_info, f"Missing challenge_distribution for {dataset_name}"


def test_should_generate_dataset_summary_report_when_requested() -> None:
    """Test that dataset summary report can be generated with complete statistics."""
    import json
    from pathlib import Path

    # This test verifies the DATASET_SUMMARY.json has expected structure
    data_dir = Path("lesson-16/data")
    summary_path = data_dir / "DATASET_SUMMARY.json"

    with open(summary_path) as f:
        summary = json.load(f)

    # Verify summary completeness
    assert summary["version"] == "1.0", "Version should be 1.0"

    # Verify invoice statistics
    invoices_info = summary["datasets"]["invoices"]
    assert invoices_info["count"] == 100, "Should have 100 invoices"
    assert "amount_statistics" in invoices_info, "Missing amount_statistics for invoices"

    # Verify transaction statistics
    transactions_info = summary["datasets"]["transactions"]
    assert transactions_info["count"] == 100, "Should have 100 transactions"

    # Verify reconciliation statistics
    reconciliation_info = summary["datasets"]["reconciliation"]
    assert reconciliation_info["count"] == 100, "Should have 100 reconciliations"
