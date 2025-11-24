"""Unit tests for generate_test_queries.py

Tests for dimension configuration, validation functions, and query generation logic.
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from generate_test_queries import (
    COMPLEXITY_LEVELS,
    CUISINE_TYPES,
    DIETARY_RESTRICTIONS,
    INGREDIENT_CONSTRAINTS,
    MEAL_PORTIONS,
    MEAL_TYPES,
    NONE_VALUE,
    _generate_dimension_tuples_impl,
    generate_dimension_tuples,
    validate_dimension_value,
    validate_tuple,
    verify_dimension_coverage,
    write_queries_to_csv,
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


# --- Task 2.8: Unit Tests for Tuple Generation ---


class TestVerifyDimensionCoverage:
    """Test verify_dimension_coverage function."""

    def test_should_return_empty_lists_when_full_coverage(self) -> None:
        """Test that full coverage returns empty missing lists."""
        tuples = [
            {"dietary_restriction": "vegan", "ingredient_constraints": "pantry-only", "complexity_level": "quick/simple", "meal_type": "breakfast"},
            {"dietary_restriction": "gluten-free", "ingredient_constraints": "leftovers", "complexity_level": "moderate", "meal_type": "lunch"},
            {"dietary_restriction": "keto", "ingredient_constraints": "seasonal ingredients", "complexity_level": "advanced/gourmet", "meal_type": "dinner"},
        ]
        missing = verify_dimension_coverage(tuples)
        assert missing["dietary_restriction"] == []
        assert missing["ingredient_constraints"] == []
        assert missing["complexity_level"] == []
        assert missing["meal_type"] == []

    def test_should_detect_missing_complexity_values(self) -> None:
        """Test that missing complexity levels are detected."""
        tuples = [
            {"dietary_restriction": "vegan", "ingredient_constraints": "pantry-only", "complexity_level": "quick/simple", "meal_type": "breakfast"},
            {"dietary_restriction": "gluten-free", "ingredient_constraints": "leftovers", "complexity_level": "quick/simple", "meal_type": "lunch"},
        ]
        missing = verify_dimension_coverage(tuples)
        assert "moderate" in missing["complexity_level"]
        assert "advanced/gourmet" in missing["complexity_level"]

    def test_should_detect_insufficient_dietary_values(self) -> None:
        """Test that insufficient dietary restriction values are detected."""
        tuples = [
            {"dietary_restriction": "vegan", "ingredient_constraints": "pantry-only", "complexity_level": "quick/simple", "meal_type": "breakfast"},
            {"dietary_restriction": "vegan", "ingredient_constraints": "leftovers", "complexity_level": "moderate", "meal_type": "lunch"},
        ]
        missing = verify_dimension_coverage(tuples)
        assert len(missing["dietary_restriction"]) > 0  # Need at least 3 different values

    def test_should_ignore_none_values_in_coverage(self) -> None:
        """Test that 'none' values don't count toward coverage."""
        tuples = [
            {"dietary_restriction": NONE_VALUE, "ingredient_constraints": NONE_VALUE, "complexity_level": "quick/simple", "meal_type": "breakfast"},
            {"dietary_restriction": "vegan", "ingredient_constraints": "pantry-only", "complexity_level": "moderate", "meal_type": "lunch"},
            {"dietary_restriction": "gluten-free", "ingredient_constraints": "leftovers", "complexity_level": "advanced/gourmet", "meal_type": "dinner"},
        ]
        missing = verify_dimension_coverage(tuples)
        # Should still need 1 more dietary value (have 2, need 3)
        assert len(missing["dietary_restriction"]) >= 1

    def test_should_raise_error_when_no_tuples(self) -> None:
        """Test that ValueError is raised when no tuples provided."""
        with pytest.raises(ValueError, match="No tuples provided"):
            verify_dimension_coverage([])


class TestGenerateDimensionTuplesImpl:
    """Test _generate_dimension_tuples_impl function with mocked LLM."""

    @patch("generate_test_queries.get_agent_response")
    def test_should_return_valid_tuples_when_llm_succeeds(self, mock_get_agent: MagicMock) -> None:
        """Test that valid tuples are returned when LLM provides good response."""
        mock_response = [
            {"role": "system", "content": "..."},
            {"role": "user", "content": "..."},
            {"role": "assistant", "content": '''```json
[
  {
    "dietary_restriction": "vegan",
    "ingredient_constraints": "pantry-only",
    "meal_portion": "4 people",
    "complexity_level": "quick/simple",
    "meal_type": "dinner",
    "cuisine_type": ""
  },
  {
    "dietary_restriction": "gluten-free",
    "ingredient_constraints": "leftovers",
    "meal_portion": "",
    "complexity_level": "moderate",
    "meal_type": "lunch",
    "cuisine_type": "Italian"
  }
]
```'''}
        ]
        mock_get_agent.return_value = mock_response

        tuples = _generate_dimension_tuples_impl()

        assert len(tuples) == 2
        assert tuples[0]["dietary_restriction"] == "vegan"
        assert tuples[1]["dietary_restriction"] == "gluten-free"

    @patch("generate_test_queries.get_agent_response")
    def test_should_skip_invalid_tuples(self, mock_get_agent: MagicMock) -> None:
        """Test that invalid tuples are skipped with warnings."""
        mock_response = [
            {"role": "system", "content": "..."},
            {"role": "user", "content": "..."},
            {"role": "assistant", "content": '''```json
[
  {
    "dietary_restriction": "vegan",
    "ingredient_constraints": "pantry-only",
    "meal_portion": "4 people",
    "complexity_level": "quick/simple",
    "meal_type": "dinner",
    "cuisine_type": ""
  },
  {
    "dietary_restriction": "invalid-diet",
    "ingredient_constraints": "pantry-only",
    "meal_portion": "",
    "complexity_level": "quick/simple",
    "meal_type": "lunch",
    "cuisine_type": ""
  }
]
```'''}
        ]
        mock_get_agent.return_value = mock_response

        tuples = _generate_dimension_tuples_impl()

        assert len(tuples) == 1  # Only valid tuple returned
        assert tuples[0]["dietary_restriction"] == "vegan"

    @patch("generate_test_queries.get_agent_response")
    def test_should_deduplicate_tuples(self, mock_get_agent: MagicMock) -> None:
        """Test that duplicate tuples are removed."""
        mock_response = [
            {"role": "system", "content": "..."},
            {"role": "user", "content": "..."},
            {"role": "assistant", "content": '''```json
[
  {
    "dietary_restriction": "vegan",
    "ingredient_constraints": "pantry-only",
    "meal_portion": "4 people",
    "complexity_level": "quick/simple",
    "meal_type": "dinner",
    "cuisine_type": ""
  },
  {
    "dietary_restriction": "vegan",
    "ingredient_constraints": "pantry-only",
    "meal_portion": "4 people",
    "complexity_level": "quick/simple",
    "meal_type": "dinner",
    "cuisine_type": ""
  }
]
```'''}
        ]
        mock_get_agent.return_value = mock_response

        tuples = _generate_dimension_tuples_impl()

        assert len(tuples) == 1  # Duplicate removed

    @patch("generate_test_queries.get_agent_response")
    def test_should_raise_error_when_invalid_json(self, mock_get_agent: MagicMock) -> None:
        """Test that ValueError is raised when LLM returns invalid JSON."""
        mock_response = [
            {"role": "system", "content": "..."},
            {"role": "user", "content": "..."},
            {"role": "assistant", "content": "This is not JSON"}
        ]
        mock_get_agent.return_value = mock_response

        with pytest.raises(ValueError, match="Failed to parse LLM response as JSON"):
            _generate_dimension_tuples_impl()


class TestGenerateDimensionTuplesRetry:
    """Test generate_dimension_tuples retry logic."""

    @patch("generate_test_queries._generate_dimension_tuples_impl")
    @patch("generate_test_queries.time.sleep")
    def test_should_retry_on_failure_and_succeed(self, mock_sleep: MagicMock, mock_impl: MagicMock) -> None:
        """Test that function retries on failure and eventually succeeds."""
        mock_impl.side_effect = [
            ValueError("First attempt failed"),
            ValueError("Second attempt failed"),
            [{"dietary_restriction": "vegan", "ingredient_constraints": "pantry-only", "complexity_level": "quick/simple", "meal_type": "dinner"}]
        ]

        result = generate_dimension_tuples()

        assert len(result) == 1
        assert mock_impl.call_count == 3
        assert mock_sleep.call_count == 2  # Slept twice before third attempt

    @patch("generate_test_queries._generate_dimension_tuples_impl")
    @patch("generate_test_queries.time.sleep")
    def test_should_raise_runtime_error_after_max_retries(self, mock_sleep: MagicMock, mock_impl: MagicMock) -> None:
        """Test that RuntimeError is raised after all retries fail."""
        mock_impl.side_effect = ValueError("Always fails")

        with pytest.raises(RuntimeError, match="Failed to generate tuples after 3 attempts"):
            generate_dimension_tuples()

        assert mock_impl.call_count == 3
        assert mock_sleep.call_count == 2  # Slept twice (not after final failure)

    @patch("generate_test_queries._generate_dimension_tuples_impl")
    @patch("generate_test_queries.time.sleep")
    def test_should_use_exponential_backoff(self, mock_sleep: MagicMock, mock_impl: MagicMock) -> None:
        """Test that exponential backoff is used between retries."""
        mock_impl.side_effect = [
            ValueError("First attempt failed"),
            ValueError("Second attempt failed"),
            [{"dietary_restriction": "vegan", "ingredient_constraints": "pantry-only", "complexity_level": "quick/simple", "meal_type": "dinner"}]
        ]

        generate_dimension_tuples()

        # Check sleep durations: 1s, 2s
        assert mock_sleep.call_count == 2
        assert mock_sleep.call_args_list[0][0][0] == 1.0  # 1 * 2^0
        assert mock_sleep.call_args_list[1][0][0] == 2.0  # 1 * 2^1


# --- Task 4.8: Unit Tests for CSV Output ---


class TestWriteQueriesToCSV:
    """Test write_queries_to_csv function."""

    def test_should_write_csv_with_correct_schema(self, tmp_path) -> None:
        """Test that CSV is written with correct headers and data."""
        import csv

        tuples = [
            {
                "dietary_restriction": "vegan",
                "ingredient_constraints": "pantry-only",
                "meal_portion": "4 people",
                "complexity_level": "quick/simple",
                "meal_type": "dinner",
                "cuisine_type": "Italian"
            },
            {
                "dietary_restriction": "gluten-free",
                "ingredient_constraints": "leftovers",
                "meal_portion": "",
                "complexity_level": "moderate",
                "meal_type": "lunch",
                "cuisine_type": ""
            }
        ]

        output_path = tmp_path / "test_output.csv"
        result_path = write_queries_to_csv(tuples, str(output_path))

        assert result_path == str(output_path)
        assert output_path.exists()

        # Read and verify CSV content
        with open(output_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = list(reader)

            # Check headers
            assert reader.fieldnames == [
                'query_id',
                'dietary_restriction',
                'ingredient_constraints',
                'meal_portion',
                'complexity_level',
                'meal_type',
                'cuisine_type',
                'natural_language_query'
            ]

            # Check row count
            assert len(rows) == 2

            # Check first row
            assert rows[0]['query_id'] == 'Q001'
            assert rows[0]['dietary_restriction'] == 'vegan'
            assert rows[0]['ingredient_constraints'] == 'pantry-only'
            assert rows[0]['meal_portion'] == '4 people'
            assert rows[0]['complexity_level'] == 'quick/simple'
            assert rows[0]['meal_type'] == 'dinner'
            assert rows[0]['cuisine_type'] == 'Italian'
            assert 'recipe' in rows[0]['natural_language_query'].lower()

            # Check second row
            assert rows[1]['query_id'] == 'Q002'
            assert rows[1]['dietary_restriction'] == 'gluten-free'
            assert rows[1]['meal_portion'] == ''
            assert rows[1]['cuisine_type'] == ''

    def test_should_generate_timestamped_filename_when_path_none(self, tmp_path, monkeypatch) -> None:
        """Test that timestamped filename is generated when output_path is None."""

        # Change to tmp_path for testing
        monkeypatch.chdir(tmp_path)

        tuples = [
            {
                "dietary_restriction": "vegan",
                "ingredient_constraints": "pantry-only",
                "meal_portion": "",
                "complexity_level": "quick/simple",
                "meal_type": "dinner",
                "cuisine_type": ""
            }
        ]

        result_path = write_queries_to_csv(tuples)

        # Check filename format
        assert result_path.startswith('data/test_queries_generated_')
        assert result_path.endswith('.csv')
        assert (tmp_path / result_path).exists()

    def test_should_create_directory_when_not_exists(self, tmp_path) -> None:
        """Test that parent directory is created if it doesn't exist."""
        output_path = tmp_path / "subdir" / "nested" / "output.csv"

        tuples = [
            {
                "dietary_restriction": "vegan",
                "ingredient_constraints": "pantry-only",
                "meal_portion": "",
                "complexity_level": "quick/simple",
                "meal_type": "dinner",
                "cuisine_type": ""
            }
        ]

        result_path = write_queries_to_csv(tuples, str(output_path))

        assert result_path == str(output_path)
        assert output_path.exists()
        assert output_path.parent.exists()

    def test_should_escape_commas_and_quotes_properly(self, tmp_path) -> None:
        """Test that CSV properly escapes commas and quotes in data."""
        import csv

        tuples = [
            {
                "dietary_restriction": "vegan",
                "ingredient_constraints": "specific ingredients available",
                "meal_portion": "",
                "complexity_level": "quick/simple",
                "meal_type": "dinner",
                "cuisine_type": ""
            }
        ]

        output_path = tmp_path / "test_escaping.csv"
        write_queries_to_csv(tuples, str(output_path))

        # Read and verify escaping
        with open(output_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = list(reader)

            # Natural language query should contain commas but be properly escaped
            query = rows[0]['natural_language_query']
            assert ',' in query  # Query contains commas
            # If we can read it back correctly, escaping worked

    def test_should_use_utf8_encoding(self, tmp_path) -> None:
        """Test that CSV uses UTF-8 encoding."""
        tuples = [
            {
                "dietary_restriction": "vegan",
                "ingredient_constraints": "pantry-only",
                "meal_portion": "",
                "complexity_level": "quick/simple",
                "meal_type": "dinner",
                "cuisine_type": ""
            }
        ]

        output_path = tmp_path / "test_utf8.csv"
        write_queries_to_csv(tuples, str(output_path))

        # Verify file is readable as UTF-8
        with open(output_path, 'r', encoding='utf-8') as f:
            content = f.read()
            assert len(content) > 0

    def test_should_raise_type_error_when_tuples_not_list(self, tmp_path) -> None:
        """Test that TypeError is raised when tuples is not a list."""
        with pytest.raises(TypeError, match="tuples must be a list"):
            write_queries_to_csv("not a list", str(tmp_path / "output.csv"))

    def test_should_raise_value_error_when_tuples_empty(self, tmp_path) -> None:
        """Test that ValueError is raised when tuples list is empty."""
        with pytest.raises(ValueError, match="tuples list cannot be empty"):
            write_queries_to_csv([], str(tmp_path / "output.csv"))

    def test_should_raise_type_error_when_tuple_not_dict(self, tmp_path) -> None:
        """Test that TypeError is raised when tuple element is not a dict."""
        tuples = [
            {"dietary_restriction": "vegan", "ingredient_constraints": "pantry-only", "complexity_level": "quick/simple", "meal_type": "dinner"},
            "not a dict"
        ]

        with pytest.raises(TypeError, match="tuple at index 1 must be a dict"):
            write_queries_to_csv(tuples, str(tmp_path / "output.csv"))

    def test_should_handle_missing_optional_fields(self, tmp_path) -> None:
        """Test that missing optional fields are handled gracefully."""
        import csv

        tuples = [
            {
                "dietary_restriction": "vegan",
                "ingredient_constraints": "pantry-only",
                "complexity_level": "quick/simple",
                "meal_type": "dinner"
                # Missing meal_portion and cuisine_type
            }
        ]

        output_path = tmp_path / "test_missing_fields.csv"
        write_queries_to_csv(tuples, str(output_path))

        # Read and verify
        with open(output_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = list(reader)

            assert rows[0]['meal_portion'] == ''
            assert rows[0]['cuisine_type'] == ''

    def test_should_format_query_id_with_leading_zeros(self, tmp_path) -> None:
        """Test that query IDs are formatted with leading zeros."""
        import csv

        tuples = [
            {"dietary_restriction": "vegan", "ingredient_constraints": "pantry-only", "complexity_level": "quick/simple", "meal_type": "dinner"},
            {"dietary_restriction": "keto", "ingredient_constraints": "leftovers", "complexity_level": "moderate", "meal_type": "lunch"}
        ]

        output_path = tmp_path / "test_ids.csv"
        write_queries_to_csv(tuples, str(output_path))

        with open(output_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = list(reader)

            assert rows[0]['query_id'] == 'Q001'
            assert rows[1]['query_id'] == 'Q002'
