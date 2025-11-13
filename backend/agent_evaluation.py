"""Agent Evaluation Module (Lesson 14).

This module provides functions and classes for evaluating agent planning,
tool call validation, and plan efficiency scoring.

Components:
- validate_tool_call(): Validate tool calls against schema
- validate_plan_correctness(): Validate plan correctness and tool selection
- validate_plan_completeness(): Check if plan covers all subtasks
- calculate_plan_efficiency(): Calculate plan efficiency score
- PlanValidator: Class for complete plan validation
- ToolCallValidator: Class for tool call validation with semantic checks
- PlanEvaluator: Orchestrator for all evaluation metrics

Created: 2025-11-12
Task: 3.10-3.11 from tasks-0005-prd-rag-agent-evaluation-tutorial-system.md
Pattern: TDD-GREEN phase (3.10) → TDD-REFACTOR phase (3.11)

Usage Example:
    >>> # Validate a tool call
    >>> tool_call = {"tool": "search_recipes", "args": {"cuisine": "Italian"}}
    >>> schema = {"name": "search_recipes", "parameters": {"cuisine": {"type": "str", "required": False}}}
    >>> result = validate_tool_call(tool_call, schema)
    >>> result["is_valid"]
    True

    >>> # Evaluate a complete plan
    >>> tools = [{"name": "search_recipes", "parameters": {}}]
    >>> evaluator = PlanEvaluator(tools)
    >>> plan = {"goal": "Find Italian recipes", "steps": [{"step": 1, "tool": "search_recipes"}]}
    >>> scores = evaluator.evaluate(plan)
    >>> scores["overall_score"]
    1.0
"""

from typing import Any

# =============================================================================
# Module-Level Constants
# =============================================================================

# Evaluation weights for overall score calculation
# Formula: overall = (correctness × 0.5) + (completeness × 0.3) + (efficiency × 0.2)
CORRECTNESS_WEIGHT = 0.5  # Most important: does plan achieve goal correctly?
COMPLETENESS_WEIGHT = 0.3  # Second: does plan cover all subtasks?
EFFICIENCY_WEIGHT = 0.2  # Third: is plan optimal (no redundancy/waste)?

# Efficiency penalties for suboptimal plans
UNNECESSARY_STEP_PENALTY = 0.05  # Penalty per unnecessary unique tool
REDUNDANCY_PENALTY = 0.12  # Penalty per duplicate tool call


# =============================================================================
# Helper Functions (Internal)
# =============================================================================


def _validate_dict_input(value: Any, param_name: str) -> None:
    """Validate that input is a dictionary (defensive helper).

    Args:
        value: Value to validate
        param_name: Parameter name for error message

    Raises:
        TypeError: If value is not a dictionary

    Example:
        >>> _validate_dict_input({"key": "value"}, "config")  # OK
        >>> _validate_dict_input("not a dict", "config")  # Raises TypeError
    """
    if not isinstance(value, dict):
        raise TypeError(f"{param_name} must be a dictionary")


def _validate_plan_structure(plan: dict[str, Any]) -> tuple[str, list[dict[str, Any]]]:
    """Validate plan has required structure and extract goal and steps.

    Args:
        plan: Agent plan dictionary

    Returns:
        Tuple of (goal string, steps list)

    Raises:
        TypeError: If plan is not a dictionary
        ValueError: If plan missing required fields

    Example:
        >>> plan = {"goal": "Find recipes", "steps": [{"tool": "search_recipes"}]}
        >>> goal, steps = _validate_plan_structure(plan)
        >>> goal
        'Find recipes'
    """
    # Type checking
    _validate_dict_input(plan, "plan")

    # Field validation
    if "goal" not in plan:
        raise ValueError("plan must have 'goal' field")
    if "steps" not in plan:
        raise ValueError("plan must have 'steps' list")

    return plan["goal"], plan.get("steps", [])


def _estimate_optimal_steps(goal: str) -> int:
    """Estimate optimal number of steps based on goal complexity.

    Uses simple heuristic: count tasks separated by "and" in goal text.

    Args:
        goal: Goal description string

    Returns:
        Estimated optimal step count (minimum 1)

    Example:
        >>> _estimate_optimal_steps("Find vegan recipes")
        1
        >>> _estimate_optimal_steps("Find recipes and add to shopping list")
        2
        >>> _estimate_optimal_steps("Search recipes and get details and add to list")
        3
    """
    goal_lower = goal.lower()
    if " and " in goal_lower:
        # Multi-task goal - count tasks
        return len(goal_lower.split(" and "))
    else:
        # Simple goal - single step optimal
        return 1


def _calculate_efficiency_score(
    total_tools: int,
    unique_tools: int,
    estimated_optimal: int,
) -> float:
    """Calculate efficiency score with penalties for redundancy and unnecessary steps.

    Formula:
        effective_optimal = max(unique_tools, estimated_optimal)
        base_efficiency = effective_optimal / total if total > effective else 1.0
        unnecessary_penalty = (unique - estimated) × 0.05 if unique > estimated
        redundancy_penalty = (total - unique) × 0.12
        final = base - unnecessary - redundancy (bounded to [0.0, 1.0])

    Args:
        total_tools: Total number of tool calls in plan
        unique_tools: Number of unique tools used
        estimated_optimal: Estimated optimal step count from goal

    Returns:
        Efficiency score between 0.0 and 1.0

    Example:
        >>> # Optimal plan (1 unique tool, 1 estimated)
        >>> _calculate_efficiency_score(1, 1, 1)
        1.0

        >>> # Redundant plan (4 total, 2 unique, 2 estimated)
        >>> _calculate_efficiency_score(4, 2, 2)
        0.26
    """
    # Give partial credit for unique tools to avoid over-penalization
    effective_optimal = max(unique_tools, estimated_optimal)

    # Base efficiency: compare effective optimal vs actual
    if total_tools > effective_optimal:
        base_efficiency = effective_optimal / total_tools
    else:
        base_efficiency = 1.0

    # Penalize unnecessary steps (more unique tools than needed)
    unnecessary_penalty = 0.0
    if unique_tools > estimated_optimal:
        unnecessary_penalty = (
            unique_tools - estimated_optimal
        ) * UNNECESSARY_STEP_PENALTY

    # Penalize redundancy (duplicate tool calls)
    num_duplicates = total_tools - unique_tools
    redundancy_penalty = num_duplicates * REDUNDANCY_PENALTY

    # Calculate final efficiency
    efficiency = base_efficiency - unnecessary_penalty - redundancy_penalty

    # Return bounded result
    return max(0.0, min(1.0, round(efficiency, 2)))


def _validate_parameter_type(
    param_name: str,
    param_value: Any,
    param_type: str,
) -> str | None:
    """Validate parameter type against schema specification.

    Args:
        param_name: Parameter name
        param_value: Actual parameter value
        param_type: Expected type string (e.g., "int", "str", "list[str]")

    Returns:
        Error message if validation fails, None if valid

    Example:
        >>> _validate_parameter_type("max_cook_time", 30, "int")
        None
        >>> _validate_parameter_type("max_cook_time", "30", "int")
        "Argument 'max_cook_time' must be type int, got str"
    """
    if param_type == "int" and not isinstance(param_value, int):
        return f"Argument '{param_name}' must be type int, got {type(param_value).__name__}"
    elif param_type == "str" and not isinstance(param_value, str):
        return f"Argument '{param_name}' must be type str, got {type(param_value).__name__}"
    elif param_type == "list[str]" and not isinstance(param_value, list):
        return f"Argument '{param_name}' must be type list[str], got {type(param_value).__name__}"
    return None


# =============================================================================
# Tool Call Validation Functions
# =============================================================================


def validate_tool_call(
    tool_call: dict[str, Any], tool_schema: dict[str, Any]
) -> dict[str, Any]:
    """Validate tool call against schema.

    Validates:
    - Tool name matches schema
    - All required arguments present
    - Argument types correct (int, str, list[str])
    - Argument values within constraints (min/max)
    - No unknown arguments provided

    Args:
        tool_call: Tool call with 'tool' and 'args' fields
        tool_schema: Tool schema with 'name' and 'parameters' fields

    Returns:
        Dictionary with 'is_valid' boolean and 'errors' list

    Raises:
        TypeError: If inputs are not dictionaries
        ValueError: If required fields missing

    Example:
        >>> tool_call = {"tool": "search_recipes", "args": {"cuisine": "Italian"}}
        >>> schema = {"name": "search_recipes", "parameters": {"cuisine": {"type": "str", "required": False}}}
        >>> result = validate_tool_call(tool_call, schema)
        >>> result["is_valid"]
        True

        >>> # Missing required arg
        >>> tool_call = {"tool": "get_recipe_details", "args": {}}
        >>> schema = {"name": "get_recipe_details", "parameters": {"recipe_id": {"type": "int", "required": True}}}
        >>> result = validate_tool_call(tool_call, schema)
        >>> result["is_valid"]
        False
        >>> "Missing required argument: recipe_id" in result["errors"][0]
        True

    See Also:
        - ToolCallValidator.validate_schema(): Class-based wrapper for this function
        - PlanValidator.validate(): Validates all tool calls in a plan
    """
    # Step 1: Type checking (defensive) - use helper
    _validate_dict_input(tool_call, "tool_call")
    _validate_dict_input(tool_schema, "tool_schema")

    # Step 2: Input validation (defensive)
    if "tool" not in tool_call:
        raise ValueError("tool_call must have 'tool' field")
    if "args" not in tool_call:
        raise ValueError("tool_call must have 'args' field")

    # Step 3: Initialize result
    errors = []

    # Step 4: Main logic - Validate tool call
    # Check tool name matches schema
    if tool_call["tool"] != tool_schema.get("name"):
        errors.append(
            f"Tool name mismatch: expected {tool_schema.get('name')}, got {tool_call['tool']}"
        )

    # Get parameters schema
    parameters = tool_schema.get("parameters", {})
    provided_args = tool_call.get("args", {})

    # Check for unknown arguments
    for arg_name in provided_args.keys():
        if arg_name not in parameters:
            errors.append(f"Unknown argument: {arg_name}")

    # Validate each parameter
    for param_name, param_spec in parameters.items():
        is_required = param_spec.get("required", False)
        param_type = param_spec.get("type", "")

        # Check required parameters
        if is_required and param_name not in provided_args:
            errors.append(f"Missing required argument: {param_name}")
            continue

        # If parameter provided, validate type and constraints
        if param_name in provided_args:
            value = provided_args[param_name]

            # Type validation using helper
            type_error = _validate_parameter_type(param_name, value, param_type)
            if type_error:
                errors.append(type_error)

            # Value constraints (range checking)
            if isinstance(value, int):
                min_val = param_spec.get("min")
                max_val = param_spec.get("max")
                if min_val is not None and value < min_val:
                    errors.append(
                        f"Argument '{param_name}' value {value} out of range (must be between {min_val} and {max_val})"
                    )
                if max_val is not None and value > max_val:
                    errors.append(
                        f"Argument '{param_name}' value {value} out of range (must be between {min_val} and {max_val})"
                    )

    # Step 5: Return result
    return {"is_valid": len(errors) == 0, "errors": errors}


# =============================================================================
# Plan Correctness Validation Functions
# =============================================================================


def validate_plan_correctness(
    plan: dict[str, Any], gold_plan: dict[str, Any] | None = None
) -> dict[str, Any]:
    """Validate plan correctness and tool selection.

    Compares plan against gold standard (if provided) to verify tool selection is correct.

    Args:
        plan: Agent plan with 'goal' and 'steps' fields
        gold_plan: Optional gold standard plan for comparison

    Returns:
        Dictionary with 'is_correct' boolean, 'score' float, and optional 'failure_reason'

    Raises:
        TypeError: If plan is not a dictionary
        ValueError: If plan missing required fields

    Example:
        >>> plan = {"goal": "Find recipes", "steps": [{"tool": "search_recipes"}]}
        >>> result = validate_plan_correctness(plan)
        >>> result["is_correct"]
        True

        >>> # Compare against gold plan
        >>> plan = {"goal": "Find recipes", "steps": [{"tool": "search_web"}]}
        >>> gold = {"steps": [{"tool": "search_recipes"}]}
        >>> result = validate_plan_correctness(plan, gold)
        >>> result["is_correct"]
        False

    See Also:
        - validate_plan_completeness(): Check if all subtasks covered
        - calculate_plan_efficiency(): Score plan efficiency
    """
    # Step 1-2: Validate structure using helper (defensive)
    goal, steps = _validate_plan_structure(plan)

    # Step 3: Edge case - empty plan
    if len(steps) == 0:
        return {
            "is_correct": False,
            "score": 0.0,
            "failure_reason": "Plan has no steps",
        }

    # Step 4: Main logic - Validate correctness
    # If no gold plan provided, assume correct if has steps
    if gold_plan is None:
        return {"is_correct": True, "score": 1.0}

    # Compare against gold plan
    gold_steps = gold_plan.get("steps", [])

    # Extract tool names from both plans
    plan_tools = [step.get("tool") for step in steps]
    gold_tools = [step.get("tool") for step in gold_steps]

    # Check if tools match
    if plan_tools == gold_tools:
        return {"is_correct": True, "score": 1.0}
    else:
        return {
            "is_correct": False,
            "score": 0.0,
            "failure_reason": "Wrong tool_selection: tools do not match gold plan",
        }


# =============================================================================
# Plan Completeness Validation Functions
# =============================================================================


def validate_plan_completeness(plan: dict[str, Any]) -> dict[str, Any]:
    """Check if plan covers all subtasks in goal.

    Detects multi-task goals (using "and" keyword) and validates all subtasks are addressed.

    Args:
        plan: Agent plan with 'goal' and 'steps' fields

    Returns:
        Dictionary with 'is_complete' boolean, 'completeness_score' float,
        and 'missing_tasks' string

    Raises:
        TypeError: If plan is not a dictionary

    Example:
        >>> # Simple goal with single step
        >>> plan = {"goal": "Find Italian recipes", "steps": [{"tool": "search_recipes"}]}
        >>> result = validate_plan_completeness(plan)
        >>> result["is_complete"]
        True

        >>> # Multi-task goal missing subtask
        >>> plan = {"goal": "Find recipes and add to shopping list", "steps": [{"tool": "search_recipes"}]}
        >>> result = validate_plan_completeness(plan)
        >>> result["is_complete"]
        False

    See Also:
        - _estimate_optimal_steps(): Estimates optimal step count from goal
        - validate_plan_correctness(): Validates tool selection correctness
    """
    # Step 1: Type checking (defensive) - use helper
    _validate_dict_input(plan, "plan")

    # Step 2: Get goal and steps
    goal = plan.get("goal", "").lower()
    steps = plan.get("steps", [])
    step_count = len(steps)

    # Step 3: Main logic - Detect multi-task goals
    missing_tasks = []

    # Check for "and" in goal indicating multiple tasks
    if " and " in goal:
        # Multi-task goal
        tasks = goal.split(" and ")

        # Check for specific missing tasks
        if "shopping" in goal or "shopping list" in goal:
            # Check if shopping list step exists
            has_shopping = any(
                "shopping" in step.get("tool", "").lower() for step in steps
            )
            if not has_shopping:
                missing_tasks.append("Add to shopping list")
                return {
                    "is_complete": False,
                    "completeness_score": step_count / (step_count + 1),
                    "missing_tasks": "shopping list step",
                }

        # Check if we have enough steps
        if step_count < len(tasks):
            # Incomplete
            return {
                "is_complete": False,
                "completeness_score": step_count / len(tasks),
                "missing_tasks": ", ".join(missing_tasks)
                if missing_tasks
                else "Multiple subtasks incomplete",
            }

    # Step 4: Return complete if simple goal or all subtasks covered
    return {"is_complete": True, "completeness_score": 1.0, "missing_tasks": ""}


# =============================================================================
# Plan Efficiency Functions
# =============================================================================


def calculate_plan_efficiency(plan: dict[str, Any]) -> float:
    """Calculate plan efficiency score (0.0-1.0).

    Efficiency formula:
        1. Estimate optimal steps from goal complexity (using "and" keyword)
        2. Calculate base efficiency: effective_optimal / total_tools
        3. Apply penalties:
           - Unnecessary steps: (unique - estimated) × 0.05
           - Redundant calls: (total - unique) × 0.12
        4. Bound result to [0.0, 1.0]

    Args:
        plan: Agent plan with 'steps' list

    Returns:
        Efficiency score between 0.0 and 1.0

    Raises:
        TypeError: If plan is not a dictionary
        ValueError: If plan has no steps

    Example:
        >>> # Optimal plan (1 step for simple goal)
        >>> plan = {"goal": "Find recipes", "steps": [{"tool": "search_recipes"}]}
        >>> calculate_plan_efficiency(plan)
        1.0

        >>> # Redundant plan (duplicate calls)
        >>> plan = {"goal": "Find recipes", "steps": [
        ...     {"tool": "get_preferences"},
        ...     {"tool": "search_recipes"},
        ...     {"tool": "get_preferences"}  # Duplicate!
        ... ]}
        >>> score = calculate_plan_efficiency(plan)
        >>> score < 1.0  # Penalized for redundancy
        True

    See Also:
        - _calculate_efficiency_score(): Core efficiency calculation logic
        - _estimate_optimal_steps(): Estimates optimal step count from goal
        - PlanEvaluator.evaluate(): Combines all evaluation metrics
    """
    # Step 1: Type checking (defensive) - use helper
    _validate_dict_input(plan, "plan")

    # Step 2: Input validation (defensive)
    steps = plan.get("steps", [])
    if len(steps) == 0:
        raise ValueError("plan must have at least one step")

    # Step 3: Main logic - Calculate efficiency using helpers
    # Count unique tools vs total tools
    tools_used = [step.get("tool", "") for step in steps]
    unique_tools_count = len(set(tools_used))
    total_tools = len(tools_used)

    # Estimate optimal step count from goal
    goal = plan.get("goal", "")
    estimated_optimal = _estimate_optimal_steps(goal)

    # Calculate efficiency score using helper
    efficiency = _calculate_efficiency_score(
        total_tools=total_tools,
        unique_tools=unique_tools_count,
        estimated_optimal=estimated_optimal,
    )

    # Step 4: Return result
    return efficiency


# =============================================================================
# PlanValidator Class
# =============================================================================


class PlanValidator:
    """Validator for complete plan validation.

    Validates:
    - Tool selection (all tools exist in schema)
    - Argument correctness (types, required fields, constraints)
    - Plan structure (goal and steps present)

    This class maintains a tool registry for O(1) lookups and validates
    all steps in a plan against their respective tool schemas.

    Attributes:
        tools: List of available tool schemas
        _tool_map: Internal dict mapping tool names to schemas (for fast lookup)

    Example:
        >>> tools = [
        ...     {"name": "search_recipes", "parameters": {"cuisine": {"type": "str", "required": False}}},
        ...     {"name": "get_recipe_details", "parameters": {"recipe_id": {"type": "int", "required": True}}}
        ... ]
        >>> validator = PlanValidator(tools)
        >>> plan = {
        ...     "goal": "Find Italian recipes",
        ...     "steps": [{"step": 1, "tool": "search_recipes", "args": {"cuisine": "Italian"}}]
        ... }
        >>> result = validator.validate(plan)
        >>> result["overall_valid"]
        True

        >>> # Invalid plan (unknown tool)
        >>> bad_plan = {
        ...     "goal": "Find recipes",
        ...     "steps": [{"tool": "unknown_tool", "args": {}}]
        ... }
        >>> result = validator.validate(bad_plan)
        >>> result["overall_valid"]
        False
        >>> result["tool_selection_valid"]
        False

    See Also:
        - validate_tool_call(): Validates individual tool calls
        - PlanEvaluator: Orchestrates all evaluation metrics
    """

    def __init__(self, tools: list[dict[str, Any]]):
        """Initialize validator with available tools.

        Args:
            tools: List of tool schemas with 'name' and 'parameters' fields

        Raises:
            TypeError: If tools is not a list

        Example:
            >>> tools = [{"name": "search_recipes", "parameters": {}}]
            >>> validator = PlanValidator(tools)
        """
        # Step 1: Type checking (defensive)
        if not isinstance(tools, list):
            raise TypeError("tools must be a list")

        # Step 2: Initialize
        self.tools = tools
        self._tool_map = {tool["name"]: tool for tool in tools}

    def validate(self, plan: dict[str, Any]) -> dict[str, Any]:
        """Validate complete plan.

        Args:
            plan: Agent plan with 'goal' and 'steps' fields

        Returns:
            Dictionary with validation results
        """
        # Initialize result
        result = {
            "overall_valid": True,
            "tool_selection_valid": True,
            "args_valid": True,
            "errors": [],
        }

        # Get plan steps
        steps = plan.get("steps", [])

        # Validate each step
        for step in steps:
            tool_name = step.get("tool", "")
            args = step.get("args", {})

            # Check if tool exists
            if tool_name not in self._tool_map:
                result["tool_selection_valid"] = False
                result["overall_valid"] = False
                result["errors"].append(f"Unknown tool: {tool_name}")
                continue

            # Validate tool call
            tool_schema = self._tool_map[tool_name]
            tool_call = {"tool": tool_name, "args": args}
            validation = validate_tool_call(tool_call, tool_schema)

            if not validation["is_valid"]:
                result["args_valid"] = False
                result["overall_valid"] = False
                result["errors"].extend(validation["errors"])

        return result


# =============================================================================
# ToolCallValidator Class
# =============================================================================


class ToolCallValidator:
    """Validator for tool calls with semantic checking."""

    def validate_schema(
        self, tool_call: dict[str, Any], schema: dict[str, Any]
    ) -> dict[str, Any]:
        """Validate tool call against schema.

        Args:
            tool_call: Tool call dictionary
            schema: Tool schema dictionary

        Returns:
            Validation result dictionary
        """
        return validate_tool_call(tool_call, schema)

    def validate_semantics(
        self, tool_call: dict[str, Any], query: str
    ) -> dict[str, Any]:
        """Validate semantic correctness (query matches arguments).

        Args:
            tool_call: Tool call dictionary
            query: User query string

        Returns:
            Dictionary with 'valid' boolean and 'issues' list
        """
        # Step 1: Type checking
        if not isinstance(query, str):
            query = str(query)

        # Step 2: Extract arguments
        args = tool_call.get("args", {})
        issues = []

        # Step 3: Semantic validation
        query_lower = query.lower()

        # Check dietary restrictions match
        if "dietary_restrictions" in args:
            restrictions = args["dietary_restrictions"]
            if isinstance(restrictions, list):
                for restriction in restrictions:
                    restriction_lower = restriction.lower()
                    # Check for semantic mismatches
                    if (
                        "vegan" in query_lower
                        and "vegetarian" in restriction_lower
                        and "vegan" not in restriction_lower
                    ):
                        issues.append(
                            f"Query asks for 'vegan' but tool call uses '{restriction}' (semantic mismatch)"
                        )

        # Step 4: Return result
        return {"valid": len(issues) == 0, "issues": issues}


# =============================================================================
# PlanEvaluator Class
# =============================================================================


class PlanEvaluator:
    """Orchestrator for all plan evaluation metrics.

    Combines three evaluation dimensions into a weighted overall score:
    - Correctness (50%): Does plan achieve goal with correct tools?
    - Completeness (30%): Are all subtasks covered?
    - Efficiency (20%): Is plan optimal (no redundancy/waste)?

    Formula:
        overall = (correctness × 0.5) + (completeness × 0.3) + (efficiency × 0.2)

    Attributes:
        tools: List of available tool schemas
        validator: PlanValidator instance for structure validation

    Example:
        >>> tools = [{"name": "search_recipes", "parameters": {}}]
        >>> evaluator = PlanEvaluator(tools)
        >>> plan = {"goal": "Find Italian recipes", "steps": [{"tool": "search_recipes"}]}
        >>> scores = evaluator.evaluate(plan)
        >>> scores.keys()
        dict_keys(['correctness_score', 'completeness_score', 'efficiency_score', 'overall_score', 'validation_details'])
        >>> 0.0 <= scores["overall_score"] <= 1.0
        True

        >>> # Detailed breakdown
        >>> scores["correctness_score"]  # 1.0 (correct)
        1.0
        >>> scores["completeness_score"]  # 1.0 (simple goal, single step)
        1.0
        >>> scores["efficiency_score"]  # 1.0 (optimal)
        1.0
        >>> scores["overall_score"]  # Weighted average
        1.0

    See Also:
        - validate_plan_correctness(): Correctness scoring
        - validate_plan_completeness(): Completeness scoring
        - calculate_plan_efficiency(): Efficiency scoring
    """

    def __init__(self, tools: list[dict[str, Any]]):
        """Initialize evaluator with available tools.

        Args:
            tools: List of tool schemas

        Example:
            >>> tools = [{"name": "search_recipes", "parameters": {}}]
            >>> evaluator = PlanEvaluator(tools)
        """
        self.tools = tools
        self.validator = PlanValidator(tools)

    def evaluate(self, plan: dict[str, Any]) -> dict[str, Any]:
        """Evaluate plan across all dimensions.

        Args:
            plan: Agent plan dictionary

        Returns:
            Dictionary with all evaluation scores and details
        """
        # Step 1: Validate plan structure
        validation = self.validator.validate(plan)

        # Step 2: Calculate correctness
        correctness = validate_plan_correctness(plan)
        correctness_score = correctness["score"]

        # Step 3: Calculate completeness
        completeness = validate_plan_completeness(plan)
        completeness_score = completeness["completeness_score"]

        # Step 4: Calculate efficiency
        try:
            efficiency_score = calculate_plan_efficiency(plan)
        except ValueError:
            efficiency_score = 0.0

        # Step 5: Calculate weighted overall score
        # Weights: correctness=0.5, completeness=0.3, efficiency=0.2
        overall_score = (
            correctness_score * CORRECTNESS_WEIGHT
            + completeness_score * COMPLETENESS_WEIGHT
            + efficiency_score * EFFICIENCY_WEIGHT
        )

        # Step 6: Return complete evaluation
        return {
            "correctness_score": correctness_score,
            "completeness_score": completeness_score,
            "efficiency_score": efficiency_score,
            "overall_score": round(overall_score, 2),
            "validation_details": {
                "correctness": correctness,
                "completeness": completeness,
                "validation": validation,
            },
        }
