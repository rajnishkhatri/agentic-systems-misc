"""Unit tests for JSON schema validation.

Tests the validate_json_schema.py script and its validation logic.
"""

import json
import sys
from pathlib import Path

import pytest

# Add lesson-14/scripts to path
sys.path.insert(0, str(Path(__file__).parent.parent / "lesson-14" / "scripts"))

from validate_json_schema import validate_schema


def test_should_pass_when_valid_schema() -> None:
    """Test that a valid schema passes validation."""
    data = {
        "version": "1.0",
        "created": "2025-11-15",
        "execution_mode": "DEMO",
        "num_trajectories": 5,
        "summary_statistics": {
            "metric1": {"mean": 0.5, "std": 0.1},
            "metric2": {"mean": 0.8, "std": 0.05},
        },
        "radar_chart_data": {
            "labels": ["metric1", "metric2"],
            "values": [0.5, 0.8],
        },
        "detailed_results": [
            {"exercise": "Ex1", "metric": "accuracy", "value": 0.9},
            {"exercise": "Ex2", "metric": "precision", "value": 0.85},
        ],
    }

    errors = validate_schema(data)
    assert errors == [], f"Expected no errors, got: {errors}"


def test_should_fail_when_missing_top_level_keys() -> None:
    """Test that missing required keys are detected."""
    data = {
        "version": "1.0",
        "created": "2025-11-15",
        # Missing execution_mode, num_trajectories, etc.
    }

    errors = validate_schema(data)
    assert len(errors) > 0, "Expected errors for missing keys"
    assert any("execution_mode" in err for err in errors)
    assert any("num_trajectories" in err for err in errors)


def test_should_fail_when_invalid_execution_mode() -> None:
    """Test that invalid execution_mode is detected."""
    data = {
        "version": "1.0",
        "created": "2025-11-15",
        "execution_mode": "INVALID",
        "num_trajectories": 5,
        "summary_statistics": {},
        "radar_chart_data": {"labels": [], "values": []},
        "detailed_results": [],
    }

    errors = validate_schema(data)
    assert any("execution_mode" in err and "DEMO" in err for err in errors)


def test_should_fail_when_negative_num_trajectories() -> None:
    """Test that negative num_trajectories is detected."""
    data = {
        "version": "1.0",
        "created": "2025-11-15",
        "execution_mode": "DEMO",
        "num_trajectories": -5,
        "summary_statistics": {},
        "radar_chart_data": {"labels": [], "values": []},
        "detailed_results": [],
    }

    errors = validate_schema(data)
    assert any("num_trajectories" in err and "non-negative" in err for err in errors)


def test_should_fail_when_summary_stats_missing_mean_std() -> None:
    """Test that summary statistics without mean/std are detected."""
    data = {
        "version": "1.0",
        "created": "2025-11-15",
        "execution_mode": "DEMO",
        "num_trajectories": 5,
        "summary_statistics": {
            "metric1": {"mean": 0.5},  # Missing std
            "metric2": {"std": 0.1},  # Missing mean
        },
        "radar_chart_data": {"labels": [], "values": []},
        "detailed_results": [],
    }

    errors = validate_schema(data)
    assert any("metric1" in err and "std" in err for err in errors)
    assert any("metric2" in err and "mean" in err for err in errors)


def test_should_fail_when_radar_labels_values_mismatch() -> None:
    """Test that mismatched radar chart labels and values are detected."""
    data = {
        "version": "1.0",
        "created": "2025-11-15",
        "execution_mode": "DEMO",
        "num_trajectories": 5,
        "summary_statistics": {},
        "radar_chart_data": {
            "labels": ["metric1", "metric2", "metric3"],
            "values": [0.5, 0.8],  # Mismatched length
        },
        "detailed_results": [],
    }

    errors = validate_schema(data)
    assert any("labels" in err and "values" in err and "same length" in err for err in errors)


def test_should_fail_when_detailed_results_missing_keys() -> None:
    """Test that detailed results without required keys are detected."""
    data = {
        "version": "1.0",
        "created": "2025-11-15",
        "execution_mode": "DEMO",
        "num_trajectories": 5,
        "summary_statistics": {},
        "radar_chart_data": {"labels": [], "values": []},
        "detailed_results": [
            {"exercise": "Ex1", "metric": "accuracy"},  # Missing value
            {"metric": "precision", "value": 0.85},  # Missing exercise
        ],
    }

    errors = validate_schema(data)
    assert any("detailed_results[0]" in err and "value" in err for err in errors)
    assert any("detailed_results[1]" in err and "exercise" in err for err in errors)


def test_should_fail_when_nan_in_values() -> None:
    """Test that NaN values are detected."""
    data = {
        "version": "1.0",
        "created": "2025-11-15",
        "execution_mode": "DEMO",
        "num_trajectories": 5,
        "summary_statistics": {
            "metric1": {"mean": float("nan"), "std": 0.1},
        },
        "radar_chart_data": {"labels": ["metric1"], "values": [0.5]},
        "detailed_results": [],
    }

    errors = validate_schema(data)
    assert any("NaN" in err for err in errors)


def test_should_fail_when_infinity_in_values() -> None:
    """Test that Infinity values are detected."""
    data = {
        "version": "1.0",
        "created": "2025-11-15",
        "execution_mode": "DEMO",
        "num_trajectories": 5,
        "summary_statistics": {
            "metric1": {"mean": float("inf"), "std": 0.1},
        },
        "radar_chart_data": {"labels": ["metric1"], "values": [0.5]},
        "detailed_results": [],
    }

    errors = validate_schema(data)
    assert any("Infinity" in err for err in errors)


def test_should_raise_when_data_not_dict() -> None:
    """Test that non-dict data raises TypeError."""
    with pytest.raises(TypeError, match="Data must be a dictionary"):
        validate_schema("not a dict")


def test_should_pass_with_actual_memory_systems_data() -> None:
    """Test validation with actual memory_systems_demo_results.json data."""
    json_path = Path(__file__).parent.parent / "lesson-14" / "results" / "memory_systems_demo_results.json"

    if not json_path.exists():
        pytest.skip("memory_systems_demo_results.json not found")

    with open(json_path) as f:
        data = json.load(f)

    errors = validate_schema(data)
    assert errors == [], f"Actual JSON file has validation errors: {errors}"
