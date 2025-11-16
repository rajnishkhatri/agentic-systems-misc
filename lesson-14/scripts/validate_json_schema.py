"""Validation script for memory_systems_demo_results.json schema compliance.

This script validates that the generated JSON output matches the expected schema
for the evaluation dashboard and lesson 14 results format.

Usage:
    python lesson-14/scripts/validate_json_schema.py

Returns:
    Exit code 0 if validation passes, 1 if validation fails
"""

import json
import sys
from pathlib import Path
from typing import Any


def validate_schema(data: dict[str, Any]) -> list[str]:
    """Validate JSON data against expected schema.

    Args:
        data: Dictionary loaded from JSON file

    Returns:
        List of validation error messages (empty if valid)

    Raises:
        TypeError: If data is not a dict
    """
    if not isinstance(data, dict):
        raise TypeError("Data must be a dictionary")

    errors = []

    # 1. Required top-level keys
    required_keys = ["version", "created", "execution_mode", "num_trajectories",
                     "summary_statistics", "radar_chart_data", "detailed_results"]

    for key in required_keys:
        if key not in data:
            errors.append(f"Missing required top-level key: {key}")

    if errors:
        return errors  # Early return if top-level structure is wrong

    # 2. Validate version
    if not isinstance(data["version"], str):
        errors.append(f"version must be a string, got {type(data['version']).__name__}")

    # 3. Validate created (date string)
    if not isinstance(data["created"], str):
        errors.append(f"created must be a string, got {type(data['created']).__name__}")

    # 4. Validate execution_mode
    if data["execution_mode"] not in ["DEMO", "FULL"]:
        errors.append(f"execution_mode must be 'DEMO' or 'FULL', got {data['execution_mode']}")

    # 5. Validate num_trajectories
    if not isinstance(data["num_trajectories"], int) or data["num_trajectories"] < 0:
        errors.append(f"num_trajectories must be a non-negative integer, got {data.get('num_trajectories')}")

    # 6. Validate summary_statistics structure
    if not isinstance(data["summary_statistics"], dict):
        errors.append("summary_statistics must be a dictionary")
    else:
        # Each metric should have mean and std
        for metric_name, metric_data in data["summary_statistics"].items():
            if not isinstance(metric_data, dict):
                errors.append(f"summary_statistics[{metric_name}] must be a dict")
                continue

            if "mean" not in metric_data:
                errors.append(f"summary_statistics[{metric_name}] missing 'mean'")
            elif not isinstance(metric_data["mean"], (int, float)):
                errors.append(f"summary_statistics[{metric_name}]['mean'] must be numeric")

            if "std" not in metric_data:
                errors.append(f"summary_statistics[{metric_name}] missing 'std'")
            elif not isinstance(metric_data["std"], (int, float)):
                errors.append(f"summary_statistics[{metric_name}]['std'] must be numeric")

    # 7. Validate radar_chart_data structure
    if not isinstance(data["radar_chart_data"], dict):
        errors.append("radar_chart_data must be a dictionary")
    else:
        if "labels" not in data["radar_chart_data"]:
            errors.append("radar_chart_data missing 'labels'")
        elif not isinstance(data["radar_chart_data"]["labels"], list):
            errors.append("radar_chart_data['labels'] must be a list")

        if "values" not in data["radar_chart_data"]:
            errors.append("radar_chart_data missing 'values'")
        elif not isinstance(data["radar_chart_data"]["values"], list):
            errors.append("radar_chart_data['values'] must be a list")

        # Labels and values should have same length
        if "labels" in data["radar_chart_data"] and "values" in data["radar_chart_data"]:
            if len(data["radar_chart_data"]["labels"]) != len(data["radar_chart_data"]["values"]):
                errors.append(
                    f"radar_chart_data labels ({len(data['radar_chart_data']['labels'])}) "
                    f"and values ({len(data['radar_chart_data']['values'])}) must have same length"
                )

    # 8. Validate detailed_results structure
    if not isinstance(data["detailed_results"], list):
        errors.append("detailed_results must be a list")
    else:
        for idx, result in enumerate(data["detailed_results"]):
            if not isinstance(result, dict):
                errors.append(f"detailed_results[{idx}] must be a dict")
                continue

            # Each result should have exercise, metric, and value
            required_result_keys = ["exercise", "metric", "value"]
            for key in required_result_keys:
                if key not in result:
                    errors.append(f"detailed_results[{idx}] missing '{key}'")

    # 9. Validate no NaN, Infinity, or None in numeric values
    def check_numeric_values(obj: Any, path: str = "root") -> None:
        """Recursively check for invalid numeric values."""
        if isinstance(obj, dict):
            for key, value in obj.items():
                check_numeric_values(value, f"{path}.{key}")
        elif isinstance(obj, list):
            for idx, value in enumerate(obj):
                check_numeric_values(value, f"{path}[{idx}]")
        elif isinstance(obj, float):
            import math
            if math.isnan(obj):
                errors.append(f"NaN found at {path}")
            elif math.isinf(obj):
                errors.append(f"Infinity found at {path}")
        elif obj is None and "value" in path:  # None is OK in some contexts but not for metric values
            errors.append(f"None/null found at {path}")

    check_numeric_values(data)

    return errors


def main() -> int:
    """Main validation function.

    Returns:
        0 if validation passes, 1 if validation fails
    """
    # Step 1: Locate JSON file
    json_path = Path(__file__).parent.parent / "results" / "memory_systems_demo_results.json"

    if not json_path.exists():
        print(f"❌ ERROR: File not found: {json_path}")
        return 1

    # Step 2: Load JSON
    try:
        with open(json_path) as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        print(f"❌ ERROR: Invalid JSON: {e}")
        return 1
    except OSError as e:
        print(f"❌ ERROR: Could not read file: {e}")
        return 1

    # Step 3: Validate schema
    errors = validate_schema(data)

    # Step 4: Report results
    if errors:
        print("❌ VALIDATION FAILED")
        print(f"\nFound {len(errors)} error(s):\n")
        for idx, error in enumerate(errors, 1):
            print(f"  {idx}. {error}")
        return 1
    else:
        print("✅ VALIDATION PASSED")
        print(f"\nValidated schema for {json_path.name}")
        print(f"  - Execution mode: {data['execution_mode']}")
        print(f"  - Trajectories: {data['num_trajectories']}")
        print(f"  - Metrics: {len(data['summary_statistics'])}")
        print(f"  - Detailed results: {len(data['detailed_results'])}")
        return 0


if __name__ == "__main__":
    sys.exit(main())
