"""Generate test queries for Recipe Bot evaluation.

This script generates diverse test queries based on dimension combinations
to evaluate the Recipe Bot's response quality across different scenarios.

Based on PRD: tasks/0001-prd-test-query-generation.md
"""

from __future__ import annotations

from typing import Final

# --- Dimension Configuration (Task 1.1) ---

# Priority 1: Dietary Restriction
DIETARY_RESTRICTIONS: Final[list[str]] = [
    "vegetarian",
    "vegan",
    "gluten-free",
    "dairy-free",
    "keto",
    "paleo",
    "nut-free",
    "low-carb",
    "halal",
]

# Priority 2: Ingredient Constraints
INGREDIENT_CONSTRAINTS: Final[list[str]] = [
    "specific ingredients available",
    "pantry-only",
    "leftovers",
    "seasonal ingredients",
    "minimal ingredients",
    "one-pot meals",
]

# Priority 3: Meal Portion (Optional)
MEAL_PORTIONS: Final[list[str]] = [
    "1 person",
    "2 people",
    "4 people",
    "6 people",
]

# Priority 4: Complexity Level
COMPLEXITY_LEVELS: Final[list[str]] = [
    "quick/simple",  # ≤30 min
    "moderate",      # 30-60 min
    "advanced/gourmet",  # >60 min
]

# Priority 5: Meal Type
MEAL_TYPES: Final[list[str]] = [
    "breakfast",
    "lunch",
    "dinner",
    "snack",
    "dessert",
    "brunch",
    "appetizer",
]

# Priority 6: Cuisine Type (Optional)
CUISINE_TYPES: Final[list[str]] = [
    "Italian",
    "Mexican",
    "Indian",
    "Japanese",
    "Chinese",
    "Thai",
    "Mediterranean",
    "American",
]

# Special value for "no restriction"
NONE_VALUE: Final[str] = "none"

# --- Coverage Requirements (Task 1.2) ---

# Total number of queries to generate (per PRD FR2)
NUM_QUERIES_TARGET: Final[int] = 15  # Minimum
NUM_QUERIES_MAX: Final[int] = 20     # Maximum

# Minimum values required from each dimension (per PRD FR5)
MIN_DIETARY_VALUES: Final[int] = 3      # Priority 1: at least 3 values
MIN_INGREDIENT_VALUES: Final[int] = 3   # Priority 2: at least 3 values
MIN_COMPLEXITY_VALUES: Final[int] = 3   # Priority 4: ALL 3 values required
MIN_MEAL_TYPE_VALUES: Final[int] = 3    # Priority 5: at least 3 values

# Meal portion is optional (Priority 3) - recommended 40-60% of queries
MEAL_PORTION_MIN_PERCENTAGE: Final[float] = 0.40  # 40%
MEAL_PORTION_MAX_PERCENTAGE: Final[float] = 0.60  # 60%

# Edge case queries requirement (per PRD FR5.4)
EDGE_CASE_MIN_PERCENTAGE: Final[float] = 0.15  # At least 15% (3+ queries)

# Query validation requirement (per PRD FR5.5)
VALIDATION_PASS_RATE_TARGET: Final[float] = 1.0  # 100% of queries must validate


# --- Validation Functions (Task 1.3) ---

def validate_dimension_value(value: str, dimension_name: str) -> bool:
    """Validate that a dimension value matches PRD specifications.

    Args:
        value: The dimension value to validate
        dimension_name: Name of the dimension being validated

    Returns:
        True if value is valid for the dimension, False otherwise

    Raises:
        ValueError: If dimension_name is not recognized
    """
    if not isinstance(value, str):
        return False

    # Special case: "none" is valid for optional dimensions
    if value == NONE_VALUE:
        return dimension_name in ["dietary_restriction", "ingredient_constraints"]

    # Empty string is valid for optional dimensions
    if value == "":
        return dimension_name in ["meal_portion", "cuisine_type"]

    # Validate against dimension lists
    dimension_map = {
        "dietary_restriction": DIETARY_RESTRICTIONS,
        "ingredient_constraints": INGREDIENT_CONSTRAINTS,
        "meal_portion": MEAL_PORTIONS,
        "complexity_level": COMPLEXITY_LEVELS,
        "meal_type": MEAL_TYPES,
        "cuisine_type": CUISINE_TYPES,
    }

    if dimension_name not in dimension_map:
        raise ValueError(f"Unknown dimension: {dimension_name}")

    return value in dimension_map[dimension_name]


def validate_tuple(tuple_dict: dict[str, str]) -> bool:
    """Validate that a dimension tuple contains all required fields with valid values.

    Args:
        tuple_dict: Dictionary containing dimension values

    Returns:
        True if tuple is valid, False otherwise
    """
    if not isinstance(tuple_dict, dict):
        return False

    # Required dimensions
    required_dimensions = [
        "dietary_restriction",
        "ingredient_constraints",
        "complexity_level",
        "meal_type",
    ]

    # Optional dimensions
    optional_dimensions = ["meal_portion", "cuisine_type"]

    # Check all required dimensions are present
    for dim in required_dimensions:
        if dim not in tuple_dict:
            return False
        if not validate_dimension_value(tuple_dict[dim], dim):
            return False

    # Check optional dimensions if present
    for dim in optional_dimensions:
        if dim in tuple_dict:
            if not validate_dimension_value(tuple_dict[dim], dim):
                return False

    return True
