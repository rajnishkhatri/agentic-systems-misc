"""Data generation utilities for financial datasets.

Shared functions for generating realistic financial data for benchmarking
agent orchestration patterns.
"""

from __future__ import annotations

import random
from datetime import datetime, timedelta
from typing import Any


# ============================================================================
# Random Data Generation Helpers
# ============================================================================


def random_vendor_name(seed: int | None = None) -> str:
    """Generate random vendor name from predefined list.

    Args:
        seed: Random seed for reproducibility (optional)

    Returns:
        Random vendor name

    Raises:
        TypeError: If seed is not int or None
    """
    # Step 1: Type checking
    if seed is not None and not isinstance(seed, int):
        raise TypeError("seed must be int or None")

    # Step 2: Initialize random with seed if provided
    rng = random.Random(seed)

    # Step 3: Vendor name pool
    vendors = [
        "Acme Corp",
        "Global Industries",
        "TechSolutions Ltd",
        "Premier Services",
        "Elite Consulting",
        "Summit Partners",
        "Apex Systems",
        "Fusion Enterprises",
        "Vertex Technologies",
        "Nexus Solutions",
        "Quantum Industries",
        "Sterling Group",
        "Phoenix Corporation",
        "Atlas Services",
        "Zenith Partners",
        "Horizon Technologies",
        "Pinnacle Systems",
        "Catalyst Consulting",
        "Synergy Solutions",
        "Momentum Enterprises",
        "Vanguard Industries",
        "Titan Corporation",
        "Infinity Services",
        "Paradigm Solutions",
        "Velocity Technologies",
        "Optimal Systems",
        "Dynamic Partners",
        "Strategic Consulting",
        "Innovative Solutions",
        "Advanced Technologies",
    ]

    # Step 4: Return random choice
    return rng.choice(vendors)


def random_amount(min_amount: float = 10.0, max_amount: float = 50000.0, seed: int | None = None) -> float:
    """Generate random amount following log-normal distribution.

    Args:
        min_amount: Minimum amount (default: 10.0)
        max_amount: Maximum amount (default: 50000.0)
        seed: Random seed for reproducibility (optional)

    Returns:
        Random amount rounded to 2 decimal places

    Raises:
        TypeError: If arguments are not numeric
        ValueError: If min_amount >= max_amount or amounts are negative
    """
    # Step 1: Type checking
    if not isinstance(min_amount, (int, float)):
        raise TypeError("min_amount must be numeric")
    if not isinstance(max_amount, (int, float)):
        raise TypeError("max_amount must be numeric")
    if seed is not None and not isinstance(seed, int):
        raise TypeError("seed must be int or None")

    # Step 2: Input validation
    if min_amount < 0:
        raise ValueError("min_amount must be non-negative")
    if max_amount < 0:
        raise ValueError("max_amount must be non-negative")
    if min_amount >= max_amount:
        raise ValueError("min_amount must be less than max_amount")

    # Step 3: Initialize random with seed if provided
    rng = random.Random(seed)

    # Step 4: Generate log-normal distributed amount
    # Use lognormal distribution to create realistic amount distribution
    # Most amounts clustered at lower end, with long tail for high values
    import math

    # Calculate mean and std for log-normal to fit within min/max range
    log_min = math.log(min_amount)
    log_max = math.log(max_amount)
    log_mean = (log_min + log_max) / 2
    log_std = (log_max - log_min) / 6  # 99.7% of values within 3 std devs

    # Generate log-normal random value
    amount = rng.lognormvariate(log_mean, log_std)

    # Clamp to min/max range
    amount = max(min_amount, min(max_amount, amount))

    # Step 5: Return rounded amount
    return round(amount, 2)


def random_date(
    start_date: str = "2024-01-01", end_date: str = "2024-12-31", seed: int | None = None
) -> str:
    """Generate random date within range, uniformly distributed.

    Args:
        start_date: Start date in YYYY-MM-DD format (default: 2024-01-01)
        end_date: End date in YYYY-MM-DD format (default: 2024-12-31)
        seed: Random seed for reproducibility (optional)

    Returns:
        Random date in YYYY-MM-DD format

    Raises:
        TypeError: If arguments are not strings or seed not int
        ValueError: If dates are invalid format or start >= end
    """
    # Step 1: Type checking
    if not isinstance(start_date, str):
        raise TypeError("start_date must be string")
    if not isinstance(end_date, str):
        raise TypeError("end_date must be string")
    if seed is not None and not isinstance(seed, int):
        raise TypeError("seed must be int or None")

    # Step 2: Parse dates and validate
    try:
        start_dt = datetime.strptime(start_date, "%Y-%m-%d")
        end_dt = datetime.strptime(end_date, "%Y-%m-%d")
    except ValueError as e:
        raise ValueError(f"Invalid date format (expected YYYY-MM-DD): {e}") from e

    if start_dt >= end_dt:
        raise ValueError("start_date must be before end_date")

    # Step 3: Initialize random with seed if provided
    rng = random.Random(seed)

    # Step 4: Generate random date
    days_between = (end_dt - start_dt).days
    random_days = rng.randint(0, days_between)
    random_dt = start_dt + timedelta(days=random_days)

    # Step 5: Return formatted date
    return random_dt.strftime("%Y-%m-%d")


def validate_json_schema(data: dict[str, Any], schema: dict[str, Any]) -> tuple[bool, list[str]]:
    """Validate data against JSON schema.

    Args:
        data: Data dictionary to validate
        schema: JSON schema specification

    Returns:
        Tuple of (is_valid, error_messages)

    Raises:
        TypeError: If data or schema are not dictionaries
    """
    # Step 1: Type checking
    if not isinstance(data, dict):
        raise TypeError("data must be dict")
    if not isinstance(schema, dict):
        raise TypeError("schema must be dict")

    # Step 2: Collect validation errors
    errors: list[str] = []

    # Step 3: Check required fields
    required_fields = schema.get("required", [])
    for field in required_fields:
        if field not in data:
            errors.append(f"Missing required field: {field}")

    # Step 4: Check field types
    properties = schema.get("properties", {})
    for field, field_schema in properties.items():
        if field in data:
            expected_type = field_schema.get("type")
            actual_value = data[field]

            # Map JSON schema types to Python types
            type_map = {
                "string": str,
                "number": (int, float),
                "integer": int,
                "boolean": bool,
                "array": list,
                "object": dict,
            }

            if expected_type and expected_type in type_map:
                expected_py_type = type_map[expected_type]
                if not isinstance(actual_value, expected_py_type):
                    errors.append(
                        f"Field '{field}' has wrong type: "
                        f"expected {expected_type}, got {type(actual_value).__name__}"
                    )

    # Step 5: Return validation result
    is_valid = len(errors) == 0
    return is_valid, errors


# ============================================================================
# Public API
# ============================================================================

__all__ = [
    "random_vendor_name",
    "random_amount",
    "random_date",
    "validate_json_schema",
]
