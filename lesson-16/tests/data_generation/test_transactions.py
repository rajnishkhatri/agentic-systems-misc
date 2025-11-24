"""Tests for transaction dataset generation.

Tests the generate_transaction_dataset function with 14 comprehensive tests.
Following TDD methodology: RED → GREEN → REFACTOR
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

# Add lesson-16 to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from backend.data_generation.transactions import generate_transaction_dataset

# ============================================================================
# RED PHASE: Write failing tests
# ============================================================================


def test_should_return_list_when_dataset_generated() -> None:
    """Test that generate_transaction_dataset returns a list."""
    dataset = generate_transaction_dataset(count=10, seed=42)
    assert isinstance(dataset, list)
    assert len(dataset) == 10


def test_should_comply_with_schema_when_transaction_generated() -> None:
    """Test that generated transactions comply with required schema."""
    dataset = generate_transaction_dataset(count=5, seed=42)

    required_fields = [
        "transaction_id",
        "merchant",
        "amount",
        "timestamp",
        "user_behavior",
        "fraud_label",
    ]

    for transaction in dataset:
        assert isinstance(transaction, dict)
        for field in required_fields:
            assert field in transaction, f"Missing required field: {field}"


def test_should_have_correct_transaction_id_format_when_generated() -> None:
    """Test that transaction IDs follow 'TXN-NNNNN' format."""
    dataset = generate_transaction_dataset(count=10, seed=42)

    for transaction in dataset:
        txn_id = transaction["transaction_id"]
        assert txn_id.startswith("TXN-"), f"Transaction ID {txn_id} doesn't start with TXN-"
        # Extract numeric part and verify it's 5 digits
        numeric_part = txn_id.split("-")[1]
        assert len(numeric_part) == 5, f"Transaction ID {txn_id} numeric part should be 5 digits"
        assert numeric_part.isdigit(), f"Transaction ID {txn_id} numeric part should be digits only"


def test_should_have_diverse_merchants_when_dataset_generated() -> None:
    """Test that dataset has at least 40 unique merchants."""
    dataset = generate_transaction_dataset(count=100, seed=42)

    merchants = {txn["merchant"] for txn in dataset}
    assert len(merchants) >= 40, f"Expected ≥40 unique merchants, got {len(merchants)}"


def test_should_have_amounts_in_range_when_transactions_generated() -> None:
    """Test that transaction amounts are within $1-$100K range with long tail."""
    dataset = generate_transaction_dataset(count=100, seed=42)

    for transaction in dataset:
        amount = transaction["amount"]
        assert 1.0 <= amount <= 100000.0, f"Amount {amount} outside range [$1, $100K]"


def test_should_have_valid_user_behavior_features_when_generated() -> None:
    """Test that user_behavior features are valid."""
    dataset = generate_transaction_dataset(count=20, seed=42)

    for transaction in dataset:
        behavior = transaction["user_behavior"]
        assert isinstance(behavior, dict), "user_behavior must be a dict"

        # Check for expected behavior features
        expected_features = ["transaction_count_24h", "avg_transaction_amount", "account_age_days"]

        for feature in expected_features:
            assert feature in behavior, f"Missing behavior feature: {feature}"
            assert isinstance(behavior[feature], (int, float)), f"Feature {feature} must be numeric"


def test_should_have_exact_fraud_imbalance_when_generated() -> None:
    """Test that fraud label imbalance is exactly 10% fraud / 90% legitimate."""
    dataset = generate_transaction_dataset(count=100, seed=42, fraud_rate=0.1)

    fraud_count = sum(1 for txn in dataset if txn["fraud_label"] is True)

    # Allow ±1% tolerance (10% ± 1% = 9-11 out of 100)
    assert 9 <= fraud_count <= 11, f"Expected 9-11 fraud cases out of 100, got {fraud_count}"


def test_should_have_correct_fraud_type_distribution_when_generated() -> None:
    """Test that fraud types follow 40% stolen_card, 35% account_takeover, 25% synthetic_fraud."""
    dataset = generate_transaction_dataset(count=1000, seed=42, fraud_rate=0.1)

    # Get fraud transactions
    fraud_txns = [txn for txn in dataset if txn["fraud_label"] is True]

    # Count fraud types
    fraud_types = [txn.get("fraud_type") for txn in fraud_txns]
    stolen_card = fraud_types.count("stolen_card")
    account_takeover = fraud_types.count("account_takeover")
    synthetic = fraud_types.count("synthetic_fraud")

    total_fraud = len(fraud_txns)

    if total_fraud > 0:
        # Calculate percentages with ±15% tolerance
        stolen_pct = stolen_card / total_fraud
        takeover_pct = account_takeover / total_fraud
        synthetic_pct = synthetic / total_fraud

        # 40% ± 10% = 30-50%
        assert 0.30 <= stolen_pct <= 0.50, f"Expected stolen_card 30-50%, got {stolen_pct:.1%}"
        # 35% ± 10% = 25-45%
        assert 0.25 <= takeover_pct <= 0.45, f"Expected account_takeover 25-45%, got {takeover_pct:.1%}"
        # 25% ± 10% = 15-35%
        assert 0.15 <= synthetic_pct <= 0.35, f"Expected synthetic_fraud 15-35%, got {synthetic_pct:.1%}"


def test_should_inject_ambiguous_patterns_when_requested() -> None:
    """Test that ambiguous patterns are injected at ~20% rate."""
    dataset = generate_transaction_dataset(count=100, seed=42, ambiguous_rate=0.20)

    ambiguous_count = sum(1 for txn in dataset if txn.get("is_ambiguous", False))

    # Allow ±5% tolerance (20% ± 5% = 15-25%)
    assert 15 <= ambiguous_count <= 25, f"Expected 15-25 ambiguous patterns out of 100, got {ambiguous_count}"


def test_should_have_realistic_temporal_patterns_when_generated() -> None:
    """Test that timestamps are realistic (2024 dates)."""
    dataset = generate_transaction_dataset(count=50, seed=42)

    for transaction in dataset:
        timestamp = transaction["timestamp"]
        # Check format is ISO 8601 and year is 2024
        assert timestamp.startswith("2024"), f"Timestamp {timestamp} not in 2024"
        assert "T" in timestamp, f"Timestamp {timestamp} not in ISO format"


def test_should_have_gold_label_confidence_scores_when_generated() -> None:
    """Test that gold labels include confidence scores."""
    dataset = generate_transaction_dataset(count=20, seed=42)

    for transaction in dataset:
        assert "gold_label_confidence" in transaction
        confidence = transaction["gold_label_confidence"]

        assert isinstance(confidence, float), "Confidence must be float"
        assert 0.0 <= confidence <= 1.0, f"Confidence {confidence} must be in [0, 1]"


def test_should_filter_high_value_transactions_when_requested() -> None:
    """Test that high-value transaction filtering (>$10K) works."""
    dataset = generate_transaction_dataset(count=100, seed=42)

    # Get high-value transactions
    high_value = [txn for txn in dataset if txn["amount"] > 10000.0]

    # Should have some high-value transactions (long tail distribution)
    assert len(high_value) >= 5, f"Expected ≥5 high-value transactions, got {len(high_value)}"


def test_should_be_reproducible_when_same_seed_used() -> None:
    """Test that same seed produces identical datasets."""
    dataset1 = generate_transaction_dataset(count=10, seed=42)
    dataset2 = generate_transaction_dataset(count=10, seed=42)

    # Compare transaction IDs and amounts (deterministic fields)
    ids1 = [txn["transaction_id"] for txn in dataset1]
    ids2 = [txn["transaction_id"] for txn in dataset2]

    amounts1 = [txn["amount"] for txn in dataset1]
    amounts2 = [txn["amount"] for txn in dataset2]

    assert ids1 == ids2, "Transaction IDs should be identical with same seed"
    assert amounts1 == amounts2, "Amounts should be identical with same seed"


def test_should_raise_error_when_count_invalid() -> None:
    """Test that invalid count raises ValueError."""
    with pytest.raises(ValueError, match="count must be positive"):
        generate_transaction_dataset(count=0, seed=42)

    with pytest.raises(ValueError, match="count must be positive"):
        generate_transaction_dataset(count=-10, seed=42)


def test_should_raise_error_when_fraud_rate_invalid() -> None:
    """Test that invalid fraud_rate raises ValueError."""
    with pytest.raises(ValueError, match="fraud_rate must be in"):
        generate_transaction_dataset(count=10, seed=42, fraud_rate=-0.1)

    with pytest.raises(ValueError, match="fraud_rate must be in"):
        generate_transaction_dataset(count=10, seed=42, fraud_rate=1.5)
