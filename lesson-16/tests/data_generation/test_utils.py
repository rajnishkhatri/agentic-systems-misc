"""Tests for data generation utility functions.

Tests random_vendor_name, random_amount, random_date, and validate_json_schema.
Following TDD methodology with test_should_[result]_when_[condition] naming.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

import pytest

import sys
from pathlib import Path

# Add lesson-16 to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from backend.data_generation import random_amount, random_date, random_vendor_name, validate_json_schema


# ============================================================================
# Tests for random_vendor_name
# ============================================================================


def test_should_return_vendor_name_when_called_without_seed() -> None:
    """Test that random_vendor_name returns a string vendor name."""
    vendor = random_vendor_name()
    assert isinstance(vendor, str)
    assert len(vendor) > 0


def test_should_return_same_vendor_when_same_seed_used() -> None:
    """Test that same seed produces same vendor name (reproducibility)."""
    vendor1 = random_vendor_name(seed=42)
    vendor2 = random_vendor_name(seed=42)
    assert vendor1 == vendor2


def test_should_raise_error_when_seed_not_int() -> None:
    """Test that non-integer seed raises TypeError."""
    with pytest.raises(TypeError, match="seed must be int or None"):
        random_vendor_name(seed="not_an_int")  # type: ignore[arg-type]


# ============================================================================
# Tests for random_amount
# ============================================================================


def test_should_return_amount_within_range_when_called() -> None:
    """Test that random_amount returns value within min/max range."""
    amount = random_amount(min_amount=100.0, max_amount=1000.0, seed=42)
    assert 100.0 <= amount <= 1000.0
    assert isinstance(amount, float)


def test_should_round_to_two_decimals_when_amount_generated() -> None:
    """Test that amounts are rounded to 2 decimal places."""
    amount = random_amount(seed=42)
    decimal_places = len(str(amount).split(".")[-1])
    assert decimal_places <= 2


def test_should_return_same_amount_when_same_seed_used() -> None:
    """Test that same seed produces same amount (reproducibility)."""
    amount1 = random_amount(seed=42)
    amount2 = random_amount(seed=42)
    assert amount1 == amount2


def test_should_raise_error_when_min_amount_negative() -> None:
    """Test that negative min_amount raises ValueError."""
    with pytest.raises(ValueError, match="min_amount must be non-negative"):
        random_amount(min_amount=-100.0)


def test_should_raise_error_when_max_amount_negative() -> None:
    """Test that negative max_amount raises ValueError."""
    with pytest.raises(ValueError, match="max_amount must be non-negative"):
        random_amount(max_amount=-100.0)


def test_should_raise_error_when_min_greater_than_max() -> None:
    """Test that min >= max raises ValueError."""
    with pytest.raises(ValueError, match="min_amount must be less than max_amount"):
        random_amount(min_amount=1000.0, max_amount=100.0)


def test_should_raise_error_when_min_amount_not_numeric() -> None:
    """Test that non-numeric min_amount raises TypeError."""
    with pytest.raises(TypeError, match="min_amount must be numeric"):
        random_amount(min_amount="not_numeric")  # type: ignore[arg-type]


# ============================================================================
# Tests for random_date
# ============================================================================


def test_should_return_date_within_range_when_called() -> None:
    """Test that random_date returns date within start/end range."""
    date_str = random_date(start_date="2024-01-01", end_date="2024-12-31", seed=42)

    # Parse and validate
    date_obj = datetime.strptime(date_str, "%Y-%m-%d")
    start_obj = datetime.strptime("2024-01-01", "%Y-%m-%d")
    end_obj = datetime.strptime("2024-12-31", "%Y-%m-%d")

    assert start_obj <= date_obj <= end_obj


def test_should_return_same_date_when_same_seed_used() -> None:
    """Test that same seed produces same date (reproducibility)."""
    date1 = random_date(seed=42)
    date2 = random_date(seed=42)
    assert date1 == date2


def test_should_raise_error_when_date_format_invalid() -> None:
    """Test that invalid date format raises ValueError."""
    with pytest.raises(ValueError, match="Invalid date format"):
        random_date(start_date="2024/01/01")  # Wrong format


def test_should_raise_error_when_start_after_end() -> None:
    """Test that start >= end raises ValueError."""
    with pytest.raises(ValueError, match="start_date must be before end_date"):
        random_date(start_date="2024-12-31", end_date="2024-01-01")


def test_should_raise_error_when_start_date_not_string() -> None:
    """Test that non-string start_date raises TypeError."""
    with pytest.raises(TypeError, match="start_date must be string"):
        random_date(start_date=20240101)  # type: ignore[arg-type]


# ============================================================================
# Tests for validate_json_schema
# ============================================================================


def test_should_validate_successfully_when_all_fields_present() -> None:
    """Test that data with all required fields passes validation."""
    schema = {
        "required": ["name", "age"],
        "properties": {"name": {"type": "string"}, "age": {"type": "integer"}},
    }
    data = {"name": "John Doe", "age": 30}

    is_valid, errors = validate_json_schema(data, schema)

    assert is_valid is True
    assert len(errors) == 0


def test_should_fail_validation_when_required_field_missing() -> None:
    """Test that missing required field fails validation."""
    schema = {
        "required": ["name", "age"],
        "properties": {"name": {"type": "string"}, "age": {"type": "integer"}},
    }
    data = {"name": "John Doe"}  # Missing 'age'

    is_valid, errors = validate_json_schema(data, schema)

    assert is_valid is False
    assert "Missing required field: age" in errors


def test_should_fail_validation_when_field_type_wrong() -> None:
    """Test that wrong field type fails validation."""
    schema = {
        "required": ["name", "age"],
        "properties": {"name": {"type": "string"}, "age": {"type": "integer"}},
    }
    data = {"name": "John Doe", "age": "30"}  # age should be int, not str

    is_valid, errors = validate_json_schema(data, schema)

    assert is_valid is False
    assert any("wrong type" in error for error in errors)


def test_should_raise_error_when_data_not_dict() -> None:
    """Test that non-dict data raises TypeError."""
    schema = {"required": ["name"]}

    with pytest.raises(TypeError, match="data must be dict"):
        validate_json_schema(data="not_a_dict", schema=schema)  # type: ignore[arg-type]


def test_should_raise_error_when_schema_not_dict() -> None:
    """Test that non-dict schema raises TypeError."""
    data = {"name": "John"}

    with pytest.raises(TypeError, match="schema must be dict"):
        validate_json_schema(data=data, schema="not_a_dict")  # type: ignore[arg-type]
