"""Tests for invoice dataset generation.

Tests the generate_invoice_dataset function with 12 comprehensive tests.
Following TDD methodology: RED → GREEN → REFACTOR
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

# Add lesson-16 to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from backend.data_generation.invoices import generate_invoice_dataset

# ============================================================================
# RED PHASE: Write failing tests
# ============================================================================


def test_should_return_list_when_dataset_generated() -> None:
    """Test that generate_invoice_dataset returns a list."""
    dataset = generate_invoice_dataset(count=10, seed=42)
    assert isinstance(dataset, list)
    assert len(dataset) == 10


def test_should_comply_with_schema_when_invoice_generated() -> None:
    """Test that generated invoices comply with required schema."""
    dataset = generate_invoice_dataset(count=5, seed=42)

    # Core required fields (always present)
    required_fields = ["invoice_id", "vendor", "amount", "date", "line_items"]
    # Optional fields (may be missing due to challenge injection)
    optional_fields = ["status"]

    for invoice in dataset:
        assert isinstance(invoice, dict)
        # Check required fields always present
        for field in required_fields:
            assert field in invoice, f"Missing required field: {field}"

        # Optional fields may be missing if has_missing_fields is True
        if not invoice.get("has_missing_fields", False):
            for field in optional_fields:
                assert field in invoice, f"Missing optional field: {field} (but no missing_fields flag)"


def test_should_have_diverse_vendors_when_dataset_generated() -> None:
    """Test that dataset has at least 30 unique vendors."""
    dataset = generate_invoice_dataset(count=100, seed=42)

    vendors = {invoice["vendor"] for invoice in dataset}
    assert len(vendors) >= 30, f"Expected ≥30 unique vendors, got {len(vendors)}"


def test_should_have_amounts_in_range_when_invoices_generated() -> None:
    """Test that invoice amounts are within $10-$50K range."""
    dataset = generate_invoice_dataset(count=50, seed=42)

    for invoice in dataset:
        amount = invoice["amount"]
        assert 10.0 <= amount <= 50000.0, f"Amount {amount} outside range [$10, $50K]"


def test_should_have_realistic_dates_when_invoices_generated() -> None:
    """Test that invoice dates are in 2024 (realistic range)."""
    dataset = generate_invoice_dataset(count=20, seed=42)

    for invoice in dataset:
        date_str = invoice["date"]
        assert date_str.startswith("2024"), f"Date {date_str} not in 2024"


def test_should_have_correct_invoice_id_format_when_generated() -> None:
    """Test that invoice IDs follow 'INV-YYYY-NNN' format."""
    dataset = generate_invoice_dataset(count=10, seed=42)

    for invoice in dataset:
        invoice_id = invoice["invoice_id"]
        assert invoice_id.startswith("INV-"), f"Invoice ID {invoice_id} doesn't start with INV-"
        assert len(invoice_id.split("-")) == 3, f"Invoice ID {invoice_id} doesn't have 3 parts"


def test_should_have_line_items_structure_when_invoice_generated() -> None:
    """Test that line_items is a list with valid structure."""
    dataset = generate_invoice_dataset(count=5, seed=42)

    for invoice in dataset:
        line_items = invoice["line_items"]
        assert isinstance(line_items, list), "line_items must be a list"
        assert len(line_items) > 0, "line_items must not be empty"

        for item in line_items:
            assert "description" in item
            assert "quantity" in item
            assert "unit_price" in item


def test_should_inject_ocr_errors_when_requested() -> None:
    """Test that OCR errors are injected at ~15% rate."""
    dataset = generate_invoice_dataset(count=100, seed=42, ocr_error_rate=0.15)

    # Count invoices with OCR errors (indicated by has_ocr_error flag or corrupted data)
    ocr_errors = sum(1 for inv in dataset if inv.get("has_ocr_error", False))

    # Allow ±5% tolerance (15% ± 5% = 10-20%)
    assert 10 <= ocr_errors <= 20, f"Expected 10-20 OCR errors out of 100, got {ocr_errors}"


def test_should_inject_missing_fields_when_requested() -> None:
    """Test that missing fields are injected at ~10% rate."""
    dataset = generate_invoice_dataset(count=100, seed=42, missing_field_rate=0.10)

    # Count invoices with missing optional fields
    missing_fields = sum(1 for inv in dataset if inv.get("has_missing_fields", False))

    # Allow ±5% tolerance (10% ± 5% = 5-15%)
    assert 5 <= missing_fields <= 15, f"Expected 5-15 missing field cases out of 100, got {missing_fields}"


def test_should_detect_duplicate_invoices_when_generated() -> None:
    """Test that duplicate invoice detection works at ~8% rate."""
    dataset = generate_invoice_dataset(count=100, seed=42, duplicate_rate=0.08)

    # Count invoices marked as duplicates
    duplicates = sum(1 for inv in dataset if inv.get("is_duplicate", False))

    # Allow ±3% tolerance (8% ± 3% = 5-11%)
    assert 5 <= duplicates <= 11, f"Expected 5-11 duplicates out of 100, got {duplicates}"


def test_should_have_accurate_gold_labels_when_invoices_generated() -> None:
    """Test that gold labels are accurate for validation."""
    dataset = generate_invoice_dataset(count=20, seed=42)

    for invoice in dataset:
        # Gold label should have validation status
        assert "gold_label" in invoice
        gold_label = invoice["gold_label"]

        assert "is_valid" in gold_label
        assert isinstance(gold_label["is_valid"], bool)

        # If invalid, should have reason
        if not gold_label["is_valid"]:
            assert "reason" in gold_label


def test_should_be_reproducible_when_same_seed_used() -> None:
    """Test that same seed produces identical datasets."""
    dataset1 = generate_invoice_dataset(count=10, seed=42)
    dataset2 = generate_invoice_dataset(count=10, seed=42)

    # Compare invoice IDs and amounts (deterministic fields)
    ids1 = [inv["invoice_id"] for inv in dataset1]
    ids2 = [inv["invoice_id"] for inv in dataset2]

    amounts1 = [inv["amount"] for inv in dataset1]
    amounts2 = [inv["amount"] for inv in dataset2]

    assert ids1 == ids2, "Invoice IDs should be identical with same seed"
    assert amounts1 == amounts2, "Amounts should be identical with same seed"


def test_should_raise_error_when_count_invalid() -> None:
    """Test that invalid count raises ValueError."""
    with pytest.raises(ValueError, match="count must be positive"):
        generate_invoice_dataset(count=0, seed=42)

    with pytest.raises(ValueError, match="count must be positive"):
        generate_invoice_dataset(count=-10, seed=42)
