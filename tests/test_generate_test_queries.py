"""Unit tests for generate_test_queries.py

Tests for dimension configuration, validation functions, and query generation logic.
"""

from __future__ import annotations

import pytest

from generate_test_queries import (
    COMPLEXITY_LEVELS,
    CUISINE_TYPES,
    DIETARY_RESTRICTIONS,
    INGREDIENT_CONSTRAINTS,
    MEAL_PORTIONS,
    MEAL_TYPES,
    NONE_VALUE,
    validate_dimension_value,
    validate_tuple,
)


# --- Task 1.4: Unit Tests for Dimension Configuration Validation ---


class TestValidateDimensionValue:
    """Test validate_dimension_value function."""

    def test_should_return_true_when_valid_dietary_restriction(self) -> None:
        """Test that valid dietary restriction values are accepted."""
        assert validate_dimension_value("vegan", "dietary_restriction") is True
        assert validate_dimension_value("gluten-free", "dietary_restriction") is True
        assert validate_dimension_value("keto", "dietary_restriction") is True

    def test_should_return_true_when_none_for_dietary_restriction(self) -> None:
        """Test that 'none' is valid for dietary_restriction."""
        assert validate_dimension_value(NONE_VALUE, "dietary_restriction") is True

    def test_should_return_false_when_invalid_dietary_restriction(self) -> None:
        """Test that invalid dietary restriction values are rejected."""
        assert validate_dimension_value("invalid-diet", "dietary_restriction") is False
        assert validate_dimension_value("", "dietary_restriction") is False

    def test_should_return_true_when_valid_ingredient_constraints(self) -> None:
        """Test that valid ingredient constraint values are accepted."""
        assert validate_dimension_value("pantry-only", "ingredient_constraints") is True
        assert validate_dimension_value("leftovers", "ingredient_constraints") is True
        assert validate_dimension_value("seasonal ingredients", "ingredient_constraints") is True

    def test_should_return_true_when_none_for_ingredient_constraints(self) -> None:
        """Test that 'none' is valid for ingredient_constraints."""
        assert validate_dimension_value(NONE_VALUE, "ingredient_constraints") is True

    def test_should_return_true_when_valid_meal_portion(self) -> None:
        """Test that valid meal portion values are accepted."""
        assert validate_dimension_value("1 person", "meal_portion") is True
        assert validate_dimension_value("4 people", "meal_portion") is True
        assert validate_dimension_value("6 people", "meal_portion") is True

    def test_should_return_true_when_empty_string_for_meal_portion(self) -> None:
        """Test that empty string is valid for optional meal_portion."""
        assert validate_dimension_value("", "meal_portion") is True

    def test_should_return_false_when_none_for_meal_portion(self) -> None:
        """Test that 'none' is NOT valid for meal_portion (use empty string instead)."""
        assert validate_dimension_value(NONE_VALUE, "meal_portion") is False

    def test_should_return_true_when_valid_complexity_level(self) -> None:
        """Test that valid complexity level values are accepted."""
        assert validate_dimension_value("quick/simple", "complexity_level") is True
        assert validate_dimension_value("moderate", "complexity_level") is True
        assert validate_dimension_value("advanced/gourmet", "complexity_level") is True

    def test_should_return_false_when_invalid_complexity_level(self) -> None:
        """Test that invalid complexity level values are rejected."""
        assert validate_dimension_value("super-easy", "complexity_level") is False
        assert validate_dimension_value("", "complexity_level") is False

    def test_should_return_true_when_valid_meal_type(self) -> None:
        """Test that valid meal type values are accepted."""
        assert validate_dimension_value("breakfast", "meal_type") is True
        assert validate_dimension_value("dinner", "meal_type") is True
        assert validate_dimension_value("dessert", "meal_type") is True

    def test_should_return_true_when_valid_cuisine_type(self) -> None:
        """Test that valid cuisine type values are accepted."""
        assert validate_dimension_value("Italian", "cuisine_type") is True
        assert validate_dimension_value("Japanese", "cuisine_type") is True
        assert validate_dimension_value("Mediterranean", "cuisine_type") is True

    def test_should_return_true_when_empty_string_for_cuisine_type(self) -> None:
        """Test that empty string is valid for optional cuisine_type."""
        assert validate_dimension_value("", "cuisine_type") is True

    def test_should_raise_error_for_unknown_dimension(self) -> None:
        """Test that ValueError is raised for unknown dimension names."""
        with pytest.raises(ValueError, match="Unknown dimension"):
            validate_dimension_value("some-value", "unknown_dimension")

    def test_should_return_false_when_non_string_value(self) -> None:
        """Test that non-string values are rejected."""
        assert validate_dimension_value(123, "dietary_restriction") is False  # type: ignore
        assert validate_dimension_value(None, "meal_type") is False  # type: ignore
        assert validate_dimension_value(["vegan"], "dietary_restriction") is False  # type: ignore


class TestValidateTuple:
    """Test validate_tuple function."""

    def test_should_return_true_when_valid_complete_tuple(self) -> None:
        """Test that a valid complete tuple is accepted."""
        valid_tuple = {
            "dietary_restriction": "vegan",
            "ingredient_constraints": "pantry-only",
            "meal_portion": "4 people",
            "complexity_level": "quick/simple",
            "meal_type": "dinner",
            "cuisine_type": "Italian",
        }
        assert validate_tuple(valid_tuple) is True

    def test_should_return_true_when_valid_tuple_without_optional_dimensions(self) -> None:
        """Test that a valid tuple without optional dimensions is accepted."""
        valid_tuple = {
            "dietary_restriction": "gluten-free",
            "ingredient_constraints": "leftovers",
            "complexity_level": "moderate",
            "meal_type": "lunch",
        }
        assert validate_tuple(valid_tuple) is True

    def test_should_return_true_when_valid_tuple_with_empty_optional_dimensions(self) -> None:
        """Test that a valid tuple with empty optional dimensions is accepted."""
        valid_tuple = {
            "dietary_restriction": "keto",
            "ingredient_constraints": "minimal ingredients",
            "meal_portion": "",
            "complexity_level": "quick/simple",
            "meal_type": "breakfast",
            "cuisine_type": "",
        }
        assert validate_tuple(valid_tuple) is True

    def test_should_return_true_when_valid_tuple_with_none_values(self) -> None:
        """Test that a valid tuple with 'none' for allowed dimensions is accepted."""
        valid_tuple = {
            "dietary_restriction": NONE_VALUE,
            "ingredient_constraints": NONE_VALUE,
            "complexity_level": "moderate",
            "meal_type": "snack",
        }
        assert validate_tuple(valid_tuple) is True

    def test_should_return_false_when_missing_required_dimension(self) -> None:
        """Test that tuples missing required dimensions are rejected."""
        # Missing dietary_restriction
        invalid_tuple = {
            "ingredient_constraints": "pantry-only",
            "complexity_level": "quick/simple",
            "meal_type": "dinner",
        }
        assert validate_tuple(invalid_tuple) is False

        # Missing complexity_level
        invalid_tuple = {
            "dietary_restriction": "vegan",
            "ingredient_constraints": "pantry-only",
            "meal_type": "dinner",
        }
        assert validate_tuple(invalid_tuple) is False

    def test_should_return_false_when_invalid_dimension_value(self) -> None:
        """Test that tuples with invalid dimension values are rejected."""
        invalid_tuple = {
            "dietary_restriction": "invalid-diet",
            "ingredient_constraints": "pantry-only",
            "complexity_level": "quick/simple",
            "meal_type": "dinner",
        }
        assert validate_tuple(invalid_tuple) is False

    def test_should_return_false_when_non_dict_input(self) -> None:
        """Test that non-dict inputs are rejected."""
        assert validate_tuple("not a dict") is False  # type: ignore
        assert validate_tuple(None) is False  # type: ignore
        assert validate_tuple([]) is False  # type: ignore

    def test_should_return_false_when_invalid_optional_dimension(self) -> None:
        """Test that tuples with invalid optional dimension values are rejected."""
        invalid_tuple = {
            "dietary_restriction": "vegan",
            "ingredient_constraints": "pantry-only",
            "meal_portion": "10 people",  # Not in MEAL_PORTIONS
            "complexity_level": "quick/simple",
            "meal_type": "dinner",
        }
        assert validate_tuple(invalid_tuple) is False


class TestDimensionConstants:
    """Test that dimension constants match PRD specifications."""

    def test_should_have_correct_dietary_restrictions_count(self) -> None:
        """Test that DIETARY_RESTRICTIONS has at least 3 values (PRD FR1)."""
        assert len(DIETARY_RESTRICTIONS) >= 3
        assert len(DIETARY_RESTRICTIONS) == 9  # Exact count from PRD

    def test_should_have_correct_ingredient_constraints_count(self) -> None:
        """Test that INGREDIENT_CONSTRAINTS has at least 3 values (PRD FR1)."""
        assert len(INGREDIENT_CONSTRAINTS) >= 3
        assert len(INGREDIENT_CONSTRAINTS) == 6  # Exact count from PRD

    def test_should_have_all_complexity_levels(self) -> None:
        """Test that COMPLEXITY_LEVELS has all 3 values (PRD FR1)."""
        assert len(COMPLEXITY_LEVELS) == 3
        assert "quick/simple" in COMPLEXITY_LEVELS
        assert "moderate" in COMPLEXITY_LEVELS
        assert "advanced/gourmet" in COMPLEXITY_LEVELS

    def test_should_have_correct_meal_types_count(self) -> None:
        """Test that MEAL_TYPES has at least 3 values (PRD FR1)."""
        assert len(MEAL_TYPES) >= 3
        assert len(MEAL_TYPES) == 7  # Exact count from PRD

    def test_should_have_correct_meal_portions_count(self) -> None:
        """Test that MEAL_PORTIONS has 4 values (PRD FR1)."""
        assert len(MEAL_PORTIONS) == 4
        assert "1 person" in MEAL_PORTIONS
        assert "2 people" in MEAL_PORTIONS
        assert "4 people" in MEAL_PORTIONS
        assert "6 people" in MEAL_PORTIONS

    def test_should_have_cuisine_types(self) -> None:
        """Test that CUISINE_TYPES has values (PRD FR1 optional dimension)."""
        assert len(CUISINE_TYPES) >= 3
        assert len(CUISINE_TYPES) == 8  # Exact count from PRD
