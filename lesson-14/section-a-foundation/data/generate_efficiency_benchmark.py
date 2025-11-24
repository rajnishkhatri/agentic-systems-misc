#!/usr/bin/env python3
"""Generate agent_efficiency_benchmark.json with 50 test cases.

This script generates a benchmark dataset comparing optimal vs suboptimal
agent plans to test efficiency scoring algorithms.

Test Case Distribution:
- 20 optimal-only cases (no suboptimal comparison)
- 15 redundant call cases (duplicate tool calls)
- 10 unnecessary step cases (extra steps not needed)
- 5 wrong order cases (correct tools, wrong sequence)

Efficiency Scoring Formula:
    base_efficiency = optimal_steps / actual_steps
    redundancy_penalty = num_duplicates * 0.2
    unnecessary_penalty = num_unnecessary * 0.1
    ordering_penalty = num_out_of_order * 0.15
    final_efficiency = max(0.0, base_efficiency - penalties)

Created: 2025-11-12
Task: 3.8 from tasks-0005-prd-rag-agent-evaluation-tutorial-system.md
"""

import json
from typing import Any

# Tool definitions (aligned with agent_planning_benchmark.json)
TOOLS = [
    {
        "name": "search_recipes",
        "description": "Search recipe database with filters",
        "parameters": {
            "ingredients": {"type": "list[str]", "required": False},
            "dietary_restrictions": {"type": "list[str]", "required": False},
            "cuisine": {"type": "str", "required": False},
            "meal_type": {"type": "str", "required": False},
            "max_cook_time": {"type": "int", "required": False},
            "max_results": {"type": "int", "required": False, "default": 10},
        },
    },
    {
        "name": "get_user_preferences",
        "description": "Retrieve user dietary preferences and restrictions",
        "parameters": {},
    },
    {
        "name": "get_recipe_details",
        "description": "Get full recipe information by ID",
        "parameters": {"recipe_id": {"type": "int", "required": True}},
    },
    {
        "name": "add_to_shopping_list",
        "description": "Add ingredients to shopping list",
        "parameters": {"ingredients": {"type": "list[str]", "required": True}},
    },
    {
        "name": "check_ingredient_availability",
        "description": "Check if ingredient is in stock",
        "parameters": {"ingredient": {"type": "str", "required": True}},
    },
    {
        "name": "get_nutrition_info",
        "description": "Get nutritional information for food",
        "parameters": {"food": {"type": "str", "required": True}},
    },
    {
        "name": "filter_by_ingredients",
        "description": "Filter recipes by available ingredients",
        "parameters": {"recipes": {"type": "list", "required": True}},
    },
    {
        "name": "get_gita_verses",
        "description": "Search Bhagavad Gita verses",
        "parameters": {
            "chapter": {"type": "int", "required": False},
            "verse": {"type": "int", "required": False},
            "keyword": {"type": "str", "required": False},
        },
    },
]


def calculate_efficiency_score(
    plan: dict[str, Any], optimal_step_count: int = 0
) -> float:
    """Calculate plan efficiency score using defensive formula.

    Formula:
        base_efficiency = optimal_steps / actual_steps (if optimal > 0)
        redundancy_penalty = num_duplicate_tools * 0.2
        final_score = max(0.0, min(1.0, base_efficiency - redundancy_penalty))

    Args:
        plan: Agent plan with 'steps' list
        optimal_step_count: Number of steps in optimal plan (0 means this IS optimal)

    Returns:
        Efficiency score between 0.0 and 1.0

    Raises:
        TypeError: If plan is not a dict
        ValueError: If plan missing 'steps' or optimal_step_count negative
    """
    # Step 1: Type checking (defensive)
    if not isinstance(plan, dict):
        raise TypeError("plan must be a dictionary")
    if not isinstance(optimal_step_count, int):
        raise TypeError("optimal_step_count must be an integer")

    # Step 2: Input validation (defensive)
    if "steps" not in plan:
        raise ValueError("plan must have 'steps' key")
    if not isinstance(plan["steps"], list):
        raise ValueError("plan['steps'] must be a list")
    if optimal_step_count < 0:
        raise ValueError("optimal_step_count must be non-negative")

    # Step 3: Edge case handling
    actual_steps = len(plan["steps"])
    if actual_steps == 0:
        return 0.0
    if optimal_step_count == 0:
        # This IS the optimal plan
        return 1.0

    # Step 4: Main logic - Calculate base efficiency
    base_efficiency = optimal_step_count / actual_steps

    # Detect redundancy (duplicate tool calls)
    tools_used = [step.get("tool", "") for step in plan["steps"]]
    unique_tools = len(set(tools_used))
    total_tools = len(tools_used)
    num_duplicates = total_tools - unique_tools
    redundancy_penalty = num_duplicates * 0.2

    # Calculate final score
    efficiency = base_efficiency - redundancy_penalty

    # Step 5: Return bounded result
    return max(0.0, min(1.0, round(efficiency, 2)))


def generate_optimal_only_cases() -> list[dict]:
    """Generate 20 optimal-only test cases (no suboptimal comparison).

    Returns:
        List of 20 test case dictionaries

    Raises:
        None
    """
    cases = []

    # Simple single-step tasks (10 cases)
    simple_tasks = [
        ("Find vegan recipes", "search_recipes", {"dietary_restrictions": ["vegan"]}),
        (
            "Find Italian recipes",
            "search_recipes",
            {"cuisine": "Italian"},
        ),
        (
            "Find breakfast recipes",
            "search_recipes",
            {"meal_type": "breakfast"},
        ),
        (
            "Find quick recipes under 30 minutes",
            "search_recipes",
            {"max_cook_time": 30},
        ),
        ("Get user dietary preferences", "get_user_preferences", {}),
        ("Get recipe 123 details", "get_recipe_details", {"recipe_id": 123}),
        (
            "Check if tomatoes are available",
            "check_ingredient_availability",
            {"ingredient": "tomatoes"},
        ),
        (
            "Get nutrition info for chicken",
            "get_nutrition_info",
            {"food": "chicken"},
        ),
        (
            "Search for karma yoga verses",
            "get_gita_verses",
            {"keyword": "karma yoga"},
        ),
        (
            "Get Chapter 2 verses",
            "get_gita_verses",
            {"chapter": 2},
        ),
    ]

    for i, (task, tool, args) in enumerate(simple_tasks):
        cases.append(
            {
                "id": f"eff_{i+1:03d}_optimal",
                "task": task,
                "optimal_plan": {
                    "goal": task,
                    "steps": [{"step": 1, "tool": tool, "args": args}],
                    "step_count": 1,
                    "efficiency_score": 1.0,
                },
                "labels": {
                    "has_suboptimal": False,
                    "optimal_step_count": 1,
                    "category": "optimal_only",
                },
                "difficulty": "easy",
            }
        )

    # Two-step complex tasks (10 cases)
    complex_tasks = [
        (
            "Find vegan recipes with user preferences",
            [
                {"step": 1, "tool": "get_user_preferences", "args": {}},
                {
                    "step": 2,
                    "tool": "search_recipes",
                    "args": {"dietary_restrictions": ["vegan"]},
                },
            ],
        ),
        (
            "Get recipe details and add to shopping list",
            [
                {"step": 1, "tool": "get_recipe_details", "args": {"recipe_id": 456}},
                {
                    "step": 2,
                    "tool": "add_to_shopping_list",
                    "args": {"ingredients": ["{{recipe_ingredients}}"]},
                },
            ],
        ),
        (
            "Check ingredient availability and get nutrition",
            [
                {
                    "step": 1,
                    "tool": "check_ingredient_availability",
                    "args": {"ingredient": "chicken"},
                },
                {"step": 2, "tool": "get_nutrition_info", "args": {"food": "chicken"}},
            ],
        ),
        (
            "Find Italian dinner recipes",
            [
                {
                    "step": 1,
                    "tool": "search_recipes",
                    "args": {"cuisine": "Italian", "meal_type": "dinner"},
                },
                {
                    "step": 2,
                    "tool": "get_recipe_details",
                    "args": {"recipe_id": "{{top_result}}"},
                },
            ],
        ),
        (
            "Search Gita verses and get details",
            [
                {"step": 1, "tool": "get_gita_verses", "args": {"keyword": "dharma"}},
                {
                    "step": 2,
                    "tool": "get_gita_verses",
                    "args": {"chapter": "{{result_chapter}}", "verse": "{{result_verse}}"},
                },
            ],
        ),
        (
            "Get preferences and find breakfast",
            [
                {"step": 1, "tool": "get_user_preferences", "args": {}},
                {
                    "step": 2,
                    "tool": "search_recipes",
                    "args": {"meal_type": "breakfast"},
                },
            ],
        ),
        (
            "Find keto recipes with short cooking time",
            [
                {
                    "step": 1,
                    "tool": "search_recipes",
                    "args": {"dietary_restrictions": ["keto"], "max_cook_time": 45},
                },
                {
                    "step": 2,
                    "tool": "get_recipe_details",
                    "args": {"recipe_id": "{{best_match}}"},
                },
            ],
        ),
        (
            "Check pasta availability and search recipes",
            [
                {
                    "step": 1,
                    "tool": "check_ingredient_availability",
                    "args": {"ingredient": "pasta"},
                },
                {
                    "step": 2,
                    "tool": "search_recipes",
                    "args": {"ingredients": ["pasta"]},
                },
            ],
        ),
        (
            "Get nutrition for salmon and find recipes",
            [
                {"step": 1, "tool": "get_nutrition_info", "args": {"food": "salmon"}},
                {
                    "step": 2,
                    "tool": "search_recipes",
                    "args": {"ingredients": ["salmon"]},
                },
            ],
        ),
        (
            "Search dessert recipes and get details",
            [
                {
                    "step": 1,
                    "tool": "search_recipes",
                    "args": {"meal_type": "dessert"},
                },
                {
                    "step": 2,
                    "tool": "get_recipe_details",
                    "args": {"recipe_id": "{{top_dessert}}"},
                },
            ],
        ),
    ]

    for i, (task, steps) in enumerate(complex_tasks):
        cases.append(
            {
                "id": f"eff_{11+i:03d}_optimal",
                "task": task,
                "optimal_plan": {
                    "goal": task,
                    "steps": steps,
                    "step_count": 2,
                    "efficiency_score": 1.0,
                },
                "labels": {
                    "has_suboptimal": False,
                    "optimal_step_count": 2,
                    "category": "optimal_only",
                },
                "difficulty": "medium",
            }
        )

    return cases


def generate_redundant_cases() -> list[dict]:
    """Generate 15 redundant call test cases (duplicate tool calls).

    Returns:
        List of 15 test case dictionaries with optimal and suboptimal plans

    Raises:
        None
    """
    cases = []

    redundant_scenarios = [
        # Duplicate get_user_preferences
        {
            "task": "Find vegan recipes matching user preferences",
            "optimal": [
                {"step": 1, "tool": "get_user_preferences", "args": {}},
                {
                    "step": 2,
                    "tool": "search_recipes",
                    "args": {"dietary_restrictions": ["vegan"]},
                },
            ],
            "suboptimal": [
                {"step": 1, "tool": "get_user_preferences", "args": {}},
                {
                    "step": 2,
                    "tool": "search_recipes",
                    "args": {"dietary_restrictions": ["vegan"]},
                },
                {"step": 3, "tool": "get_user_preferences", "args": {}},  # Redundant
                {
                    "step": 4,
                    "tool": "filter_by_ingredients",
                    "args": {"recipes": "{{results}}"},
                },
            ],
            "reason": "Redundant get_user_preferences call at step 3",
        },
        # Duplicate search_recipes
        {
            "task": "Find Italian pasta recipes",
            "optimal": [
                {
                    "step": 1,
                    "tool": "search_recipes",
                    "args": {"cuisine": "Italian", "ingredients": ["pasta"]},
                }
            ],
            "suboptimal": [
                {
                    "step": 1,
                    "tool": "search_recipes",
                    "args": {"cuisine": "Italian"},
                },
                {
                    "step": 2,
                    "tool": "search_recipes",
                    "args": {"ingredients": ["pasta"]},
                },  # Redundant
            ],
            "reason": "Could combine filters in single search_recipes call",
        },
        # Duplicate check_ingredient_availability
        {
            "task": "Check if tomatoes are available",
            "optimal": [
                {
                    "step": 1,
                    "tool": "check_ingredient_availability",
                    "args": {"ingredient": "tomatoes"},
                }
            ],
            "suboptimal": [
                {
                    "step": 1,
                    "tool": "check_ingredient_availability",
                    "args": {"ingredient": "tomatoes"},
                },
                {
                    "step": 2,
                    "tool": "check_ingredient_availability",
                    "args": {"ingredient": "tomatoes"},
                },  # Redundant
            ],
            "reason": "Duplicate check for same ingredient",
        },
        # Duplicate get_recipe_details
        {
            "task": "Get recipe 789 details",
            "optimal": [
                {"step": 1, "tool": "get_recipe_details", "args": {"recipe_id": 789}}
            ],
            "suboptimal": [
                {"step": 1, "tool": "get_recipe_details", "args": {"recipe_id": 789}},
                {
                    "step": 2,
                    "tool": "get_recipe_details",
                    "args": {"recipe_id": 789},
                },  # Redundant
            ],
            "reason": "Duplicate fetch of same recipe",
        },
        # Multiple redundant calls
        {
            "task": "Find gluten-free recipes with preferences",
            "optimal": [
                {"step": 1, "tool": "get_user_preferences", "args": {}},
                {
                    "step": 2,
                    "tool": "search_recipes",
                    "args": {"dietary_restrictions": ["gluten-free"]},
                },
            ],
            "suboptimal": [
                {"step": 1, "tool": "get_user_preferences", "args": {}},
                {
                    "step": 2,
                    "tool": "search_recipes",
                    "args": {"dietary_restrictions": ["gluten-free"]},
                },
                {"step": 3, "tool": "get_user_preferences", "args": {}},  # Redundant
                {
                    "step": 4,
                    "tool": "search_recipes",
                    "args": {"dietary_restrictions": ["gluten-free"]},
                },  # Redundant
            ],
            "reason": "Two redundant calls (preferences at step 3, search at step 4)",
        },
    ]

    # Generate 15 cases (3 copies of 5 scenarios)
    for i in range(15):
        scenario = redundant_scenarios[i % len(redundant_scenarios)]
        optimal_steps = len(scenario["optimal"])
        suboptimal_steps = len(scenario["suboptimal"])

        cases.append(
            {
                "id": f"eff_{21+i:03d}_redundant",
                "task": scenario["task"],
                "optimal_plan": {
                    "goal": scenario["task"],
                    "steps": scenario["optimal"],
                    "step_count": optimal_steps,
                    "efficiency_score": 1.0,
                },
                "suboptimal_plan": {
                    "goal": scenario["task"],
                    "steps": scenario["suboptimal"],
                    "step_count": suboptimal_steps,
                    "efficiency_score": calculate_efficiency_score(
                        {"steps": scenario["suboptimal"]}, optimal_steps
                    ),
                    "inefficiency_type": "REDUNDANT_CALLS",
                    "inefficiency_reason": scenario["reason"],
                },
                "labels": {
                    "has_suboptimal": True,
                    "optimal_step_count": optimal_steps,
                    "suboptimal_step_count": suboptimal_steps,
                    "efficiency_difference": round(
                        1.0
                        - calculate_efficiency_score(
                            {"steps": scenario["suboptimal"]}, optimal_steps
                        ),
                        2,
                    ),
                    "category": "suboptimal_redundant",
                },
                "difficulty": "medium",
            }
        )

    return cases


def generate_unnecessary_step_cases() -> list[dict]:
    """Generate 10 unnecessary step test cases.

    Returns:
        List of 10 test case dictionaries with optimal and suboptimal plans

    Raises:
        None
    """
    cases = []

    unnecessary_scenarios = [
        {
            "task": "Find vegan recipes",
            "optimal": [
                {
                    "step": 1,
                    "tool": "search_recipes",
                    "args": {"dietary_restrictions": ["vegan"]},
                }
            ],
            "suboptimal": [
                {
                    "step": 1,
                    "tool": "get_user_preferences",
                    "args": {},
                },  # Unnecessary
                {
                    "step": 2,
                    "tool": "search_recipes",
                    "args": {"dietary_restrictions": ["vegan"]},
                },
            ],
            "reason": "get_user_preferences unnecessary when dietary restriction explicitly specified",
        },
        {
            "task": "Find Italian recipes",
            "optimal": [
                {"step": 1, "tool": "search_recipes", "args": {"cuisine": "Italian"}}
            ],
            "suboptimal": [
                {"step": 1, "tool": "search_recipes", "args": {"cuisine": "Italian"}},
                {
                    "step": 2,
                    "tool": "filter_by_ingredients",
                    "args": {"recipes": "{{results}}"},
                },  # Unnecessary
            ],
            "reason": "filter_by_ingredients unnecessary without ingredient constraints",
        },
        {
            "task": "Get recipe 999 details",
            "optimal": [
                {"step": 1, "tool": "get_recipe_details", "args": {"recipe_id": 999}}
            ],
            "suboptimal": [
                {
                    "step": 1,
                    "tool": "search_recipes",
                    "args": {"max_results": 1},
                },  # Unnecessary
                {"step": 2, "tool": "get_recipe_details", "args": {"recipe_id": 999}},
            ],
            "reason": "search_recipes unnecessary when recipe ID known",
        },
        {
            "task": "Check if chicken is available",
            "optimal": [
                {
                    "step": 1,
                    "tool": "check_ingredient_availability",
                    "args": {"ingredient": "chicken"},
                }
            ],
            "suboptimal": [
                {
                    "step": 1,
                    "tool": "get_nutrition_info",
                    "args": {"food": "chicken"},
                },  # Unnecessary
                {
                    "step": 2,
                    "tool": "check_ingredient_availability",
                    "args": {"ingredient": "chicken"},
                },
            ],
            "reason": "get_nutrition_info unnecessary for availability check",
        },
        {
            "task": "Search for dharma verses in Gita",
            "optimal": [
                {"step": 1, "tool": "get_gita_verses", "args": {"keyword": "dharma"}}
            ],
            "suboptimal": [
                {
                    "step": 1,
                    "tool": "get_gita_verses",
                    "args": {"chapter": 1},
                },  # Unnecessary
                {"step": 2, "tool": "get_gita_verses", "args": {"keyword": "dharma"}},
            ],
            "reason": "Chapter 1 fetch unnecessary for keyword search",
        },
    ]

    # Generate 10 cases (2 copies of 5 scenarios)
    for i in range(10):
        scenario = unnecessary_scenarios[i % len(unnecessary_scenarios)]
        optimal_steps = len(scenario["optimal"])
        suboptimal_steps = len(scenario["suboptimal"])

        cases.append(
            {
                "id": f"eff_{36+i:03d}_unnecessary",
                "task": scenario["task"],
                "optimal_plan": {
                    "goal": scenario["task"],
                    "steps": scenario["optimal"],
                    "step_count": optimal_steps,
                    "efficiency_score": 1.0,
                },
                "suboptimal_plan": {
                    "goal": scenario["task"],
                    "steps": scenario["suboptimal"],
                    "step_count": suboptimal_steps,
                    "efficiency_score": calculate_efficiency_score(
                        {"steps": scenario["suboptimal"]}, optimal_steps
                    ),
                    "inefficiency_type": "UNNECESSARY_STEPS",
                    "inefficiency_reason": scenario["reason"],
                },
                "labels": {
                    "has_suboptimal": True,
                    "optimal_step_count": optimal_steps,
                    "suboptimal_step_count": suboptimal_steps,
                    "efficiency_difference": round(
                        1.0
                        - calculate_efficiency_score(
                            {"steps": scenario["suboptimal"]}, optimal_steps
                        ),
                        2,
                    ),
                    "category": "suboptimal_unnecessary",
                },
                "difficulty": "medium",
            }
        )

    return cases


def generate_wrong_order_cases() -> list[dict]:
    """Generate 5 wrong order test cases.

    Returns:
        List of 5 test case dictionaries with optimal and suboptimal plans

    Raises:
        None
    """
    cases = []

    wrong_order_scenarios = [
        {
            "task": "Find recipes with user preferences and add to shopping list",
            "optimal": [
                {"step": 1, "tool": "get_user_preferences", "args": {}},
                {
                    "step": 2,
                    "tool": "search_recipes",
                    "args": {"dietary_restrictions": "{{preferences}}"},
                },
                {
                    "step": 3,
                    "tool": "get_recipe_details",
                    "args": {"recipe_id": "{{top_result}}"},
                },
                {
                    "step": 4,
                    "tool": "add_to_shopping_list",
                    "args": {"ingredients": "{{recipe_ingredients}}"},
                },
            ],
            "suboptimal": [
                {
                    "step": 1,
                    "tool": "search_recipes",
                    "args": {},
                },  # Should get preferences first
                {"step": 2, "tool": "get_user_preferences", "args": {}},  # Wrong order
                {
                    "step": 3,
                    "tool": "get_recipe_details",
                    "args": {"recipe_id": "{{top_result}}"},
                },
                {
                    "step": 4,
                    "tool": "add_to_shopping_list",
                    "args": {"ingredients": "{{recipe_ingredients}}"},
                },
            ],
            "reason": "Should get_user_preferences before search_recipes to apply filters",
        },
        {
            "task": "Check ingredient availability then find recipes",
            "optimal": [
                {
                    "step": 1,
                    "tool": "check_ingredient_availability",
                    "args": {"ingredient": "pasta"},
                },
                {
                    "step": 2,
                    "tool": "search_recipes",
                    "args": {"ingredients": ["pasta"]},
                },
            ],
            "suboptimal": [
                {
                    "step": 1,
                    "tool": "search_recipes",
                    "args": {"ingredients": ["pasta"]},
                },  # Wrong order
                {
                    "step": 2,
                    "tool": "check_ingredient_availability",
                    "args": {"ingredient": "pasta"},
                },
            ],
            "reason": "Should check availability before searching recipes",
        },
        {
            "task": "Get recipe details then add to shopping list",
            "optimal": [
                {"step": 1, "tool": "get_recipe_details", "args": {"recipe_id": 555}},
                {
                    "step": 2,
                    "tool": "add_to_shopping_list",
                    "args": {"ingredients": "{{recipe_ingredients}}"},
                },
            ],
            "suboptimal": [
                {
                    "step": 1,
                    "tool": "add_to_shopping_list",
                    "args": {"ingredients": []},
                },  # Wrong order
                {"step": 2, "tool": "get_recipe_details", "args": {"recipe_id": 555}},
            ],
            "reason": "Need recipe details before adding ingredients to shopping list",
        },
        {
            "task": "Find keto recipes and get nutrition info",
            "optimal": [
                {
                    "step": 1,
                    "tool": "search_recipes",
                    "args": {"dietary_restrictions": ["keto"]},
                },
                {
                    "step": 2,
                    "tool": "get_recipe_details",
                    "args": {"recipe_id": "{{top_result}}"},
                },
                {
                    "step": 3,
                    "tool": "get_nutrition_info",
                    "args": {"food": "{{recipe_name}}"},
                },
            ],
            "suboptimal": [
                {
                    "step": 1,
                    "tool": "get_nutrition_info",
                    "args": {"food": "unknown"},
                },  # Wrong order
                {
                    "step": 2,
                    "tool": "search_recipes",
                    "args": {"dietary_restrictions": ["keto"]},
                },
                {
                    "step": 3,
                    "tool": "get_recipe_details",
                    "args": {"recipe_id": "{{top_result}}"},
                },
            ],
            "reason": "Should search and get recipe details before getting nutrition info",
        },
        {
            "task": "Search Gita verses by chapter then get details",
            "optimal": [
                {"step": 1, "tool": "get_gita_verses", "args": {"chapter": 3}},
                {
                    "step": 2,
                    "tool": "get_gita_verses",
                    "args": {"chapter": 3, "verse": "{{first_verse}}"},
                },
            ],
            "suboptimal": [
                {
                    "step": 1,
                    "tool": "get_gita_verses",
                    "args": {"chapter": 3, "verse": 1},
                },  # Wrong order (specific before browse)
                {"step": 2, "tool": "get_gita_verses", "args": {"chapter": 3}},
            ],
            "reason": "Should browse chapter first to identify relevant verse",
        },
    ]

    for i, scenario in enumerate(wrong_order_scenarios):
        optimal_steps = len(scenario["optimal"])
        suboptimal_steps = len(scenario["suboptimal"])

        # Apply ordering penalty (0.15 per out-of-order step)
        ordering_penalty = 0.15
        base_efficiency = optimal_steps / suboptimal_steps
        efficiency = max(0.0, base_efficiency - ordering_penalty)

        cases.append(
            {
                "id": f"eff_{46+i:03d}_wrong_order",
                "task": scenario["task"],
                "optimal_plan": {
                    "goal": scenario["task"],
                    "steps": scenario["optimal"],
                    "step_count": optimal_steps,
                    "efficiency_score": 1.0,
                },
                "suboptimal_plan": {
                    "goal": scenario["task"],
                    "steps": scenario["suboptimal"],
                    "step_count": suboptimal_steps,
                    "efficiency_score": round(efficiency, 2),
                    "inefficiency_type": "WRONG_ORDER",
                    "inefficiency_reason": scenario["reason"],
                },
                "labels": {
                    "has_suboptimal": True,
                    "optimal_step_count": optimal_steps,
                    "suboptimal_step_count": suboptimal_steps,
                    "efficiency_difference": round(1.0 - efficiency, 2),
                    "category": "suboptimal_wrong_order",
                },
                "difficulty": "hard",
            }
        )

    return cases


def generate_benchmark() -> dict[str, Any]:
    """Generate complete agent efficiency benchmark.

    Returns:
        Complete benchmark dictionary with all test cases

    Raises:
        AssertionError: If test case count validation fails
    """
    benchmark = {
        "version": "1.0",
        "created": "2025-11-12",
        "description": "Agent Efficiency Benchmark - 50 test cases comparing optimal vs suboptimal plans",
        "statistics": {
            "total_cases": 50,
            "optimal_only": 20,
            "suboptimal_redundant": 15,
            "suboptimal_unnecessary": 10,
            "suboptimal_wrong_order": 5,
        },
        "efficiency_scoring": {
            "formula": "base_efficiency = optimal_steps / actual_steps",
            "redundancy_penalty": 0.2,
            "unnecessary_penalty": 0.1,
            "ordering_penalty": 0.15,
            "range": [0.0, 1.0],
        },
        "available_tools": TOOLS,
        "test_cases": [],
    }

    # Generate all test case categories
    print("Generating optimal-only cases...")
    optimal_cases = generate_optimal_only_cases()
    benchmark["test_cases"].extend(optimal_cases)

    print("Generating redundant call cases...")
    redundant_cases = generate_redundant_cases()
    benchmark["test_cases"].extend(redundant_cases)

    print("Generating unnecessary step cases...")
    unnecessary_cases = generate_unnecessary_step_cases()
    benchmark["test_cases"].extend(unnecessary_cases)

    print("Generating wrong order cases...")
    wrong_order_cases = generate_wrong_order_cases()
    benchmark["test_cases"].extend(wrong_order_cases)

    # Validation
    total_cases = len(benchmark["test_cases"])
    assert total_cases == 50, f"Expected 50 cases, got {total_cases}"

    # Count by category
    optimal_only = sum(
        1 for c in benchmark["test_cases"] if c["labels"]["category"] == "optimal_only"
    )
    redundant = sum(
        1
        for c in benchmark["test_cases"]
        if c["labels"]["category"] == "suboptimal_redundant"
    )
    unnecessary = sum(
        1
        for c in benchmark["test_cases"]
        if c["labels"]["category"] == "suboptimal_unnecessary"
    )
    wrong_order = sum(
        1
        for c in benchmark["test_cases"]
        if c["labels"]["category"] == "suboptimal_wrong_order"
    )

    assert optimal_only == 20, f"Expected 20 optimal_only, got {optimal_only}"
    assert redundant == 15, f"Expected 15 redundant, got {redundant}"
    assert unnecessary == 10, f"Expected 10 unnecessary, got {unnecessary}"
    assert wrong_order == 5, f"Expected 5 wrong_order, got {wrong_order}"

    print(f"\n✅ Generated {total_cases} test cases")
    print(f"   - Optimal only: {optimal_only}")
    print(f"   - Redundant calls: {redundant}")
    print(f"   - Unnecessary steps: {unnecessary}")
    print(f"   - Wrong order: {wrong_order}")

    return benchmark


if __name__ == "__main__":
    benchmark = generate_benchmark()

    # Save to file
    output_path = "lesson-14/data/agent_efficiency_benchmark.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(benchmark, f, indent=2, ensure_ascii=False)

    print(f"\n📁 Saved to: {output_path}")
    print()
    print("📊 Statistics:")
    for key, value in benchmark["statistics"].items():
        print(f"   - {key}: {value}")
    print()
    print("🎯 Efficiency Scoring:")
    for key, value in benchmark["efficiency_scoring"].items():
        print(f"   - {key}: {value}")
