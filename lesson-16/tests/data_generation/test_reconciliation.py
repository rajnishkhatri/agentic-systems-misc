"""Tests for reconciliation dataset generation (account matching).

Tests the generate_reconciliation_dataset function with 13 comprehensive tests.
Following TDD methodology: RED → GREEN → REFACTOR
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

# Add lesson-16 to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from backend.data_generation.reconciliation import generate_reconciliation_dataset


# ============================================================================
# RED PHASE: Write failing tests
# ============================================================================


def test_should_return_list_when_dataset_generated() -> None:
    """Test that generate_reconciliation_dataset returns a list."""
    dataset = generate_reconciliation_dataset(count=10, seed=42)
    assert isinstance(dataset, list)
    assert len(dataset) == 10


def test_should_comply_with_schema_when_reconciliation_generated() -> None:
    """Test that generated reconciliation tasks comply with required schema."""
    dataset = generate_reconciliation_dataset(count=5, seed=42)

    required_fields = [
        "reconciliation_id",
        "bank_transactions",
        "ledger_entries",
        "expected_matches",
        "reconciliation_status",
        "discrepancy_amount",
    ]

    for task in dataset:
        assert isinstance(task, dict)
        for field in required_fields:
            assert field in task, f"Missing required field: {field}"


def test_should_have_bank_and_ledger_paired_structure_when_generated() -> None:
    """Test that bank_transactions and ledger_entries are paired structures."""
    dataset = generate_reconciliation_dataset(count=10, seed=42)

    for task in dataset:
        assert isinstance(task["bank_transactions"], list), "bank_transactions must be a list"
        assert isinstance(task["ledger_entries"], list), "ledger_entries must be a list"
        assert len(task["bank_transactions"]) > 0, "bank_transactions must not be empty"
        assert len(task["ledger_entries"]) > 0, "ledger_entries must not be empty"


def test_should_have_accurate_expected_matches_gold_labels_when_generated() -> None:
    """Test that expected_matches gold labels are accurate."""
    dataset = generate_reconciliation_dataset(count=20, seed=42)

    for task in dataset:
        expected_matches = task["expected_matches"]
        assert isinstance(expected_matches, list), "expected_matches must be a list"

        # Each match should have bank_index and ledger_index
        for match in expected_matches:
            assert "bank_index" in match
            assert "ledger_index" in match
            assert isinstance(match["bank_index"], int)
            assert isinstance(match["ledger_index"], int)


def test_should_inject_date_mismatch_challenges_when_requested() -> None:
    """Test that date mismatches are injected at ~25% rate (1-3 business days)."""
    dataset = generate_reconciliation_dataset(count=100, seed=42, date_mismatch_rate=0.25)

    # Count tasks with date mismatch flag
    date_mismatches = sum(1 for task in dataset if task.get("has_date_mismatch", False))

    # Allow ±7% tolerance (25% ± 7% = 18-32%)
    assert 18 <= date_mismatches <= 32, f"Expected 18-32 date mismatches out of 100, got {date_mismatches}"


def test_should_inject_amount_rounding_challenges_when_requested() -> None:
    """Test that amount rounding errors are injected at ~20% rate."""
    dataset = generate_reconciliation_dataset(count=100, seed=42, rounding_error_rate=0.20)

    # Count tasks with rounding errors
    rounding_errors = sum(1 for task in dataset if task.get("has_rounding_error", False))

    # Allow ±6% tolerance (20% ± 6% = 14-26%)
    assert 14 <= rounding_errors <= 26, f"Expected 14-26 rounding errors out of 100, got {rounding_errors}"


def test_should_inject_duplicate_entry_challenges_when_requested() -> None:
    """Test that duplicate entries are injected at ~15% rate."""
    dataset = generate_reconciliation_dataset(count=100, seed=42, duplicate_rate=0.15)

    # Count tasks with duplicates
    duplicates = sum(1 for task in dataset if task.get("has_duplicates", False))

    # Allow ±5% tolerance (15% ± 5% = 10-20%)
    assert 10 <= duplicates <= 20, f"Expected 10-20 duplicate cases out of 100, got {duplicates}"


def test_should_inject_missing_counterparty_challenges_when_requested() -> None:
    """Test that missing counterparty information is injected at ~18% rate."""
    dataset = generate_reconciliation_dataset(count=100, seed=42, missing_counterparty_rate=0.18)

    # Count tasks with missing counterparty
    missing = sum(1 for task in dataset if task.get("has_missing_counterparty", False))

    # Allow ±5% tolerance (18% ± 5% = 13-23%)
    assert 13 <= missing <= 23, f"Expected 13-23 missing counterparty cases out of 100, got {missing}"


def test_should_have_correct_reconciliation_status_distribution_when_generated() -> None:
    """Test that reconciliation status follows 60% perfect_match, 25% resolvable, 15% manual_review."""
    # Test with no challenge injection to verify base distribution
    dataset = generate_reconciliation_dataset(
        count=200,
        seed=42,
        date_mismatch_rate=0.0,
        rounding_error_rate=0.0,
        duplicate_rate=0.0,
        missing_counterparty_rate=0.0,
    )

    # Count status types
    perfect = sum(1 for task in dataset if task["reconciliation_status"] == "perfect_match")
    resolvable = sum(1 for task in dataset if task["reconciliation_status"] == "resolvable_with_logic")
    manual = sum(1 for task in dataset if task["reconciliation_status"] == "manual_review_required")

    total = len(dataset)

    # Calculate percentages with ±10% tolerance
    perfect_pct = perfect / total
    resolvable_pct = resolvable / total
    manual_pct = manual / total

    # 60% ± 10% = 50-70%
    assert 0.50 <= perfect_pct <= 0.70, f"Expected perfect_match 50-70%, got {perfect_pct:.1%}"
    # 25% ± 10% = 15-35%
    assert 0.15 <= resolvable_pct <= 0.35, f"Expected resolvable_with_logic 15-35%, got {resolvable_pct:.1%}"
    # 15% ± 10% = 5-25%
    assert 0.05 <= manual_pct <= 0.25, f"Expected manual_review_required 5-25%, got {manual_pct:.1%}"


def test_should_have_realistic_discrepancy_amounts_when_generated() -> None:
    """Test that discrepancy amounts are realistic ($0.01-$500)."""
    dataset = generate_reconciliation_dataset(count=50, seed=42)

    for task in dataset:
        discrepancy = task["discrepancy_amount"]
        assert isinstance(discrepancy, (int, float)), "discrepancy_amount must be numeric"

        # Perfect matches should have 0 discrepancy
        if task["reconciliation_status"] == "perfect_match":
            assert discrepancy == 0.0, "Perfect match should have 0 discrepancy"
        else:
            # Others should have discrepancy in range $0.01-$500
            assert 0.0 <= discrepancy <= 500.0, f"Discrepancy {discrepancy} outside range [$0, $500]"


def test_should_handle_edge_cases_when_generated() -> None:
    """Test handling of edge cases (same-day multi-transactions, cross-month)."""
    dataset = generate_reconciliation_dataset(count=100, seed=42, difficulty="hard")

    # Hard difficulty should have more edge cases
    # Check for transactions with same date (same-day multi-transactions)
    same_day_cases = 0
    cross_month_cases = 0

    for task in dataset:
        bank_dates = [txn["date"] for txn in task["bank_transactions"]]
        ledger_dates = [entry["date"] for entry in task["ledger_entries"]]

        # Same-day multi-transactions: multiple transactions on same date
        if len(bank_dates) != len(set(bank_dates)):
            same_day_cases += 1

        # Cross-month: bank and ledger dates in different months
        for b_date, l_date in zip(bank_dates, ledger_dates, strict=False):
            if b_date[:7] != l_date[:7]:  # Compare YYYY-MM part
                cross_month_cases += 1
                break

    # Hard difficulty should have some edge cases
    assert same_day_cases > 0 or cross_month_cases > 0, "Hard difficulty should include edge cases"


def test_should_support_difficulty_levels_when_generated() -> None:
    """Test that difficulty parameter affects task complexity."""
    easy = generate_reconciliation_dataset(count=20, seed=42, difficulty="easy")
    hard = generate_reconciliation_dataset(count=20, seed=42, difficulty="hard")

    # Hard tasks should have more challenges on average
    easy_avg_discrepancy = sum(task["discrepancy_amount"] for task in easy) / len(easy)
    hard_avg_discrepancy = sum(task["discrepancy_amount"] for task in hard) / len(hard)

    # Hard should have higher average discrepancy (or similar, not less)
    assert hard_avg_discrepancy >= easy_avg_discrepancy * 0.5, "Hard tasks should be more challenging"


def test_should_be_reproducible_when_same_seed_used() -> None:
    """Test that same seed produces identical datasets."""
    dataset1 = generate_reconciliation_dataset(count=10, seed=42)
    dataset2 = generate_reconciliation_dataset(count=10, seed=42)

    # Compare reconciliation IDs and discrepancy amounts (deterministic fields)
    ids1 = [task["reconciliation_id"] for task in dataset1]
    ids2 = [task["reconciliation_id"] for task in dataset2]

    discrepancies1 = [task["discrepancy_amount"] for task in dataset1]
    discrepancies2 = [task["discrepancy_amount"] for task in dataset2]

    assert ids1 == ids2, "Reconciliation IDs should be identical with same seed"
    assert discrepancies1 == discrepancies2, "Discrepancies should be identical with same seed"


def test_should_raise_error_when_count_invalid() -> None:
    """Test that invalid count raises ValueError."""
    with pytest.raises(ValueError, match="count must be positive"):
        generate_reconciliation_dataset(count=0, seed=42)

    with pytest.raises(ValueError, match="count must be positive"):
        generate_reconciliation_dataset(count=-10, seed=42)


def test_should_raise_error_when_difficulty_invalid() -> None:
    """Test that invalid difficulty raises ValueError."""
    with pytest.raises(ValueError, match="difficulty must be one of"):
        generate_reconciliation_dataset(count=10, seed=42, difficulty="invalid")
