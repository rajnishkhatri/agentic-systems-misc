"""Tests for Agent Evaluation Module (Lesson 14).

TDD-RED Phase: Tests for agent planning and tool call validation.

This test file follows TDD methodology:
- RED: Write failing tests first (this file)
- GREEN: Implement minimal code to pass tests
- REFACTOR: Clean up and improve implementation

Test Coverage:
- validate_tool_call() - 10+ tests
- validate_plan_correctness() - 8+ tests
- validate_plan_completeness() - 5+ tests
- calculate_plan_efficiency() - 5+ tests
- PlanValidator class - 5+ tests
- ToolCallValidator class - 3+ tests
- PlanEvaluator class - 3+ tests

Total: 40+ tests

Test Naming Convention: test_should_[expected_result]_when_[condition]

Created: 2025-11-12
Task: 3.9 from tasks-0005-prd-rag-agent-evaluation-tutorial-system.md
"""


import pytest

from backend.agent_evaluation import (
    PlanEvaluator,
    PlanValidator,
    ToolCallValidator,
    calculate_plan_efficiency,
    validate_plan_completeness,
    validate_plan_correctness,
    validate_tool_call,
)

# =============================================================================
# Tool Call Validation Tests (10+ tests)
# =============================================================================


class TestToolCallValidation:
    """Test suite for tool call validation functions."""

    def test_should_validate_correct_tool_call_when_all_args_valid(self) -> None:
        """Test validation passes for correct tool call."""
        # Arrange: Valid tool call
        tool_call = {
            "tool": "search_recipes",
            "args": {"dietary_restrictions": ["vegan"]},
        }
        tool_schema = {
            "name": "search_recipes",
            "parameters": {
                "dietary_restrictions": {"type": "list[str]", "required": False}
            },
        }

        # Act: Validate tool call
        result = validate_tool_call(tool_call, tool_schema)

        # Assert: Should pass validation
        assert result["is_valid"] is True
        assert result["errors"] == []

    def test_should_reject_when_missing_required_arg(self) -> None:
        """Test validation fails when required argument missing."""
        # Arrange
        tool_call = {"tool": "get_recipe_details", "args": {}}
        tool_schema = {
            "name": "get_recipe_details",
            "parameters": {"recipe_id": {"type": "int", "required": True}},
        }

        # Act
        result = validate_tool_call(tool_call, tool_schema)

        # Assert
        assert result["is_valid"] is False
        assert any("recipe_id" in error for error in result["errors"])

    def test_should_reject_when_arg_type_wrong(self) -> None:
        """Test validation fails when argument has wrong type."""
        # Arrange
        tool_call = {
            "tool": "search_recipes",
            "args": {"max_cook_time": "30 minutes"},  # Should be int
        }
        tool_schema = {
            "name": "search_recipes",
            "parameters": {"max_cook_time": {"type": "int", "required": False}},
        }

        # Act
        result = validate_tool_call(tool_call, tool_schema)

        # Assert
        assert result["is_valid"] is False
        assert any("type" in error.lower() for error in result["errors"])

    def test_should_reject_when_arg_value_out_of_range(self) -> None:
        """Test validation fails when argument value violates constraints."""
        # Arrange
        tool_call = {"tool": "search_recipes", "args": {"max_cook_time": -10}}
        tool_schema = {
            "name": "search_recipes",
            "parameters": {
                "max_cook_time": {
                    "type": "int",
                    "required": False,
                    "min": 1,
                    "max": 240,
                }
            },
        }

        # Act
        result = validate_tool_call(tool_call, tool_schema)

        # Assert
        assert result["is_valid"] is False
        assert any(
            "range" in error.lower() or "between" in error.lower()
            for error in result["errors"]
        )

    def test_should_raise_error_for_invalid_tool_call_input(self) -> None:
        """Test validation raises TypeError for non-dict input."""
        with pytest.raises(TypeError, match="tool_call must be a dictionary"):
            validate_tool_call("not a dict", {})  # type: ignore

    def test_should_raise_error_for_invalid_schema_input(self) -> None:
        """Test validation raises TypeError for non-dict schema."""
        with pytest.raises(TypeError, match="tool_schema must be a dictionary"):
            validate_tool_call({}, "not a dict")  # type: ignore

    def test_should_raise_error_when_tool_call_missing_tool_field(self) -> None:
        """Test validation raises ValueError when tool_call missing 'tool' field."""
        with pytest.raises(ValueError, match="tool_call must have 'tool' field"):
            validate_tool_call({"args": {}}, {"name": "test"})

    def test_should_raise_error_when_tool_call_missing_args_field(self) -> None:
        """Test validation raises ValueError when tool_call missing 'args' field."""
        with pytest.raises(ValueError, match="tool_call must have 'args' field"):
            validate_tool_call({"tool": "test"}, {"name": "test"})

    def test_should_reject_when_tool_name_mismatch(self) -> None:
        """Test validation fails when tool name doesn't match schema."""
        # Arrange
        tool_call = {"tool": "wrong_tool", "args": {}}
        tool_schema = {"name": "search_recipes", "parameters": {}}

        # Act
        result = validate_tool_call(tool_call, tool_schema)

        # Assert
        assert result["is_valid"] is False
        assert any("mismatch" in error.lower() for error in result["errors"])

    def test_should_reject_when_unknown_argument_provided(self) -> None:
        """Test validation fails when unknown argument provided."""
        # Arrange
        tool_call = {"tool": "search_recipes", "args": {"unknown_param": "value"}}
        tool_schema = {
            "name": "search_recipes",
            "parameters": {"cuisine": {"type": "str", "required": False}},
        }

        # Act
        result = validate_tool_call(tool_call, tool_schema)

        # Assert
        assert result["is_valid"] is False
        assert any("unknown" in error.lower() for error in result["errors"])

    def test_should_accept_when_optional_arg_missing(self) -> None:
        """Test validation passes when optional argument missing."""
        # Arrange
        tool_call = {"tool": "search_recipes", "args": {}}
        tool_schema = {
            "name": "search_recipes",
            "parameters": {"cuisine": {"type": "str", "required": False}},
        }

        # Act
        result = validate_tool_call(tool_call, tool_schema)

        # Assert
        assert result["is_valid"] is True
        assert result["errors"] == []


# =============================================================================
# Plan Correctness Validation Tests (8+ tests)
# =============================================================================


class TestPlanCorrectnessValidation:
    """Test suite for plan correctness validation."""

    def test_should_validate_correct_plan_when_achieves_goal(self) -> None:
        """Test validation passes for correct plan."""
        # Arrange
        plan = {
            "goal": "Find vegan pasta recipes",
            "steps": [
                {
                    "step": 1,
                    "tool": "search_recipes",
                    "args": {"ingredients": ["pasta"], "dietary_restrictions": ["vegan"]},
                }
            ],
        }

        # Act
        result = validate_plan_correctness(plan)

        # Assert
        assert result["is_correct"] is True
        assert result["score"] >= 0.8

    def test_should_reject_when_wrong_tool_selected(self) -> None:
        """Test validation fails for wrong tool selection."""
        # Arrange
        plan = {
            "goal": "Find Italian recipes",
            "steps": [
                {"step": 1, "tool": "search_web", "args": {"query": "Italian recipes"}}
            ],
        }
        gold_plan = {
            "steps": [
                {"step": 1, "tool": "search_recipes", "args": {"cuisine": "Italian"}}
            ]
        }

        # Act
        result = validate_plan_correctness(plan, gold_plan)

        # Assert
        assert result["is_correct"] is False
        assert "tool_selection" in result["failure_reason"].lower()

    def test_should_reject_when_plan_has_no_steps(self) -> None:
        """Test validation fails for empty plan."""
        # Arrange
        plan = {"goal": "Find recipes", "steps": []}

        # Act
        result = validate_plan_correctness(plan)

        # Assert
        assert result["is_correct"] is False
        assert result["score"] == 0.0

    def test_should_raise_error_for_invalid_plan_input(self) -> None:
        """Test validation raises TypeError for non-dict plan."""
        with pytest.raises(TypeError, match="plan must be a dictionary"):
            validate_plan_correctness("not a dict")  # type: ignore

    def test_should_raise_error_when_plan_missing_goal(self) -> None:
        """Test validation raises ValueError when plan missing 'goal' field."""
        with pytest.raises(ValueError, match="plan must have 'goal' field"):
            validate_plan_correctness({"steps": []})

    def test_should_raise_error_when_plan_missing_steps(self) -> None:
        """Test validation raises ValueError when plan missing 'steps' field."""
        with pytest.raises(ValueError, match="plan must have 'steps' list"):
            validate_plan_correctness({"goal": "test"})

    def test_should_compare_tool_selection_with_gold_plan(self) -> None:
        """Test validation compares tool selection against gold plan."""
        # Arrange
        plan = {
            "goal": "Find vegan recipes",
            "steps": [
                {
                    "step": 1,
                    "tool": "search_recipes",
                    "args": {"dietary_restrictions": ["vegan"]},
                }
            ],
        }
        gold_plan = {
            "steps": [
                {
                    "step": 1,
                    "tool": "search_recipes",
                    "args": {"dietary_restrictions": ["vegan"]},
                }
            ]
        }

        # Act
        result = validate_plan_correctness(plan, gold_plan)

        # Assert
        assert result["is_correct"] is True
        assert result["score"] == 1.0

    def test_should_reject_when_tools_dont_match_gold_plan(self) -> None:
        """Test validation fails when tools don't match gold plan."""
        # Arrange
        plan = {
            "goal": "Find recipes and add to list",
            "steps": [
                {"step": 1, "tool": "search_recipes", "args": {}},
                {"step": 2, "tool": "filter_results", "args": {}},
            ],
        }
        gold_plan = {
            "steps": [
                {"step": 1, "tool": "search_recipes", "args": {}},
                {"step": 2, "tool": "add_to_shopping_list", "args": {}},
            ]
        }

        # Act
        result = validate_plan_correctness(plan, gold_plan)

        # Assert
        assert result["is_correct"] is False


# =============================================================================
# Plan Completeness Tests (5+ tests)
# =============================================================================


class TestPlanCompleteness:
    """Test suite for plan completeness validation."""

    def test_should_validate_complete_plan_when_all_subtasks_covered(self) -> None:
        """Test validation passes for complete plan."""
        # Arrange
        plan = {
            "goal": "Find recipes and add to shopping list",
            "steps": [
                {"step": 1, "tool": "search_recipes", "args": {}},
                {"step": 2, "tool": "get_recipe_details", "args": {}},
                {"step": 3, "tool": "add_to_shopping_list", "args": {}},
            ],
        }

        # Act
        result = validate_plan_completeness(plan)

        # Assert
        assert result["is_complete"] is True
        assert result["completeness_score"] == 1.0

    def test_should_reject_when_multi_task_goal_has_single_step(self) -> None:
        """Test validation fails for incomplete plan (multi-task goal with single step)."""
        # Arrange
        plan = {
            "goal": "Find recipes and add to shopping list",
            "steps": [{"step": 1, "tool": "search_recipes", "args": {}}],
        }

        # Act
        result = validate_plan_completeness(plan)

        # Assert
        assert result["is_complete"] is False
        assert result["completeness_score"] < 1.0

    def test_should_detect_missing_shopping_list_step(self) -> None:
        """Test validation detects missing shopping list step."""
        # Arrange
        plan = {
            "goal": "Find Italian recipes and add to shopping list",
            "steps": [
                {"step": 1, "tool": "search_recipes", "args": {}},
                {"step": 2, "tool": "get_recipe_details", "args": {}},
            ],
        }

        # Act
        result = validate_plan_completeness(plan)

        # Assert
        assert result["is_complete"] is False
        assert "shopping" in result["missing_tasks"].lower()

    def test_should_raise_error_for_invalid_plan_input(self) -> None:
        """Test validation raises TypeError for non-dict plan."""
        with pytest.raises(TypeError, match="plan must be a dictionary"):
            validate_plan_completeness("not a dict")  # type: ignore

    def test_should_accept_single_step_for_simple_goal(self) -> None:
        """Test validation passes for single-step plan with simple goal."""
        # Arrange
        plan = {
            "goal": "Find Italian recipes",
            "steps": [{"step": 1, "tool": "search_recipes", "args": {}}],
        }

        # Act
        result = validate_plan_completeness(plan)

        # Assert
        assert result["is_complete"] is True


# =============================================================================
# Plan Efficiency Tests (5+ tests)
# =============================================================================


class TestPlanEfficiency:
    """Test suite for plan efficiency calculations."""

    def test_should_score_optimal_plan_as_1_0(self) -> None:
        """Test optimal plan gets perfect efficiency score."""
        # Arrange
        plan = {
            "goal": "Find vegan recipes",
            "steps": [
                {
                    "step": 1,
                    "tool": "search_recipes",
                    "args": {"dietary_restrictions": ["vegan"]},
                }
            ],
        }

        # Act
        efficiency = calculate_plan_efficiency(plan)

        # Assert
        assert efficiency == 1.0

    def test_should_penalize_redundant_steps(self) -> None:
        """Test efficiency decreases with redundant steps."""
        # Arrange
        plan = {
            "goal": "Find vegan recipes",
            "steps": [
                {"step": 1, "tool": "get_user_preferences", "args": {}},
                {"step": 2, "tool": "search_recipes", "args": {}},
                {"step": 3, "tool": "get_user_preferences", "args": {}},  # Redundant
            ],
        }

        # Act
        efficiency = calculate_plan_efficiency(plan)

        # Assert
        assert efficiency < 1.0
        assert efficiency >= 0.5

    def test_should_penalize_unnecessary_steps(self) -> None:
        """Test efficiency decreases with unnecessary steps."""
        # Arrange
        plan = {
            "goal": "Find Italian recipes",
            "steps": [
                {"step": 1, "tool": "get_trending_cuisines", "args": {}},  # Unnecessary
                {"step": 2, "tool": "search_recipes", "args": {}},
            ],
        }

        # Act
        efficiency = calculate_plan_efficiency(plan)

        # Assert
        assert efficiency < 1.0

    def test_should_raise_error_for_invalid_plan_input(self) -> None:
        """Test validation raises TypeError for non-dict plan."""
        with pytest.raises(TypeError, match="plan must be a dictionary"):
            calculate_plan_efficiency("not a dict")  # type: ignore

    def test_should_raise_error_when_plan_has_no_steps(self) -> None:
        """Test validation raises ValueError for empty plan."""
        with pytest.raises(ValueError, match="plan must have at least one step"):
            calculate_plan_efficiency({"goal": "test", "steps": []})


# =============================================================================
# PlanValidator Class Tests (5+ tests)
# =============================================================================


class TestPlanValidator:
    """Test suite for PlanValidator class."""

    def test_should_initialize_with_tools(self) -> None:
        """Test PlanValidator initialization."""
        # Arrange
        tools = [{"name": "search_recipes", "parameters": {}}]

        # Act
        validator = PlanValidator(tools)

        # Assert
        assert validator.tools == tools

    def test_should_raise_error_for_invalid_tools_input(self) -> None:
        """Test initialization raises TypeError for non-list tools."""
        with pytest.raises(TypeError, match="tools must be a list"):
            PlanValidator("not a list")  # type: ignore

    def test_should_validate_complete_plan(self) -> None:
        """Test end-to-end plan validation."""
        # Arrange
        tools = [
            {
                "name": "search_recipes",
                "parameters": {"cuisine": {"type": "str", "required": False}},
            }
        ]
        validator = PlanValidator(tools)

        plan = {
            "goal": "Find Italian recipes",
            "steps": [
                {"step": 1, "tool": "search_recipes", "args": {"cuisine": "Italian"}}
            ],
        }

        # Act
        result = validator.validate(plan)

        # Assert
        assert result["overall_valid"] is True
        assert result["tool_selection_valid"] is True
        assert result["args_valid"] is True

    def test_should_detect_invalid_tool_selection(self) -> None:
        """Test validator detects invalid tool selection."""
        # Arrange
        tools = [{"name": "search_recipes", "parameters": {}}]
        validator = PlanValidator(tools)

        plan = {
            "goal": "Find recipes",
            "steps": [{"step": 1, "tool": "unknown_tool", "args": {}}],
        }

        # Act
        result = validator.validate(plan)

        # Assert
        assert result["tool_selection_valid"] is False

    def test_should_detect_invalid_arguments(self) -> None:
        """Test validator detects invalid arguments."""
        # Arrange
        tools = [
            {
                "name": "search_recipes",
                "parameters": {"max_cook_time": {"type": "int", "required": False}},
            }
        ]
        validator = PlanValidator(tools)

        plan = {
            "goal": "Find recipes",
            "steps": [
                {
                    "step": 1,
                    "tool": "search_recipes",
                    "args": {"max_cook_time": "invalid"},
                }
            ],
        }

        # Act
        result = validator.validate(plan)

        # Assert
        assert result["args_valid"] is False


# =============================================================================
# ToolCallValidator Class Tests (3+ tests)
# =============================================================================


class TestToolCallValidator:
    """Test suite for ToolCallValidator class."""

    def test_should_validate_schema_correctly(self) -> None:
        """Test schema validation."""
        # Arrange
        validator = ToolCallValidator()

        tool_call = {"tool": "search_recipes", "args": {"cuisine": "Italian"}}
        schema = {
            "name": "search_recipes",
            "parameters": {"cuisine": {"type": "str", "required": False}},
        }

        # Act
        result = validator.validate_schema(tool_call, schema)

        # Assert
        assert result["is_valid"] is True

    def test_should_validate_semantic_correctness(self) -> None:
        """Test semantic validation (e.g., vegan != vegetarian)."""
        # Arrange
        validator = ToolCallValidator()

        query = "Find vegan recipes"
        tool_call = {
            "tool": "search_recipes",
            "args": {"dietary_restrictions": ["vegetarian"]},
        }

        # Act
        result = validator.validate_semantics(tool_call, query)

        # Assert
        assert result["valid"] is False
        assert "vegan" in result["issues"][0].lower()

    def test_should_pass_semantic_validation_when_matching(self) -> None:
        """Test semantic validation passes when query matches args."""
        # Arrange
        validator = ToolCallValidator()

        query = "Find vegan recipes"
        tool_call = {
            "tool": "search_recipes",
            "args": {"dietary_restrictions": ["vegan"]},
        }

        # Act
        result = validator.validate_semantics(tool_call, query)

        # Assert
        assert result["valid"] is True


# =============================================================================
# PlanEvaluator Class Tests (3+ tests)
# =============================================================================


class TestPlanEvaluator:
    """Test suite for PlanEvaluator class (orchestrates all validations)."""

    def test_should_evaluate_complete_plan_pipeline(self) -> None:
        """Test end-to-end plan evaluation."""
        # Arrange
        tools = [{"name": "search_recipes", "parameters": {}}]
        evaluator = PlanEvaluator(tools)

        plan = {
            "goal": "Find vegan recipes",
            "steps": [
                {
                    "step": 1,
                    "tool": "search_recipes",
                    "args": {"dietary_restrictions": ["vegan"]},
                }
            ],
        }

        # Act
        result = evaluator.evaluate(plan)

        # Assert
        assert "correctness_score" in result
        assert "efficiency_score" in result
        assert "completeness_score" in result
        assert "overall_score" in result
        assert 0.0 <= result["overall_score"] <= 1.0

    def test_should_calculate_weighted_overall_score(self) -> None:
        """Test evaluator calculates weighted overall score."""
        # Arrange
        tools = [{"name": "search_recipes", "parameters": {}}]
        evaluator = PlanEvaluator(tools)

        plan = {
            "goal": "Find recipes",
            "steps": [{"step": 1, "tool": "search_recipes", "args": {}}],
        }

        # Act
        result = evaluator.evaluate(plan)

        # Assert: Overall score should be weighted average
        assert result["overall_score"] > 0.0
        assert result["overall_score"] <= 1.0

    def test_should_include_validation_details(self) -> None:
        """Test evaluator includes full validation details."""
        # Arrange
        tools = [{"name": "search_recipes", "parameters": {}}]
        evaluator = PlanEvaluator(tools)

        plan = {
            "goal": "Find recipes",
            "steps": [{"step": 1, "tool": "search_recipes", "args": {}}],
        }

        # Act
        result = evaluator.evaluate(plan)

        # Assert
        assert "validation_details" in result
        assert "correctness" in result["validation_details"]
        assert "completeness" in result["validation_details"]
