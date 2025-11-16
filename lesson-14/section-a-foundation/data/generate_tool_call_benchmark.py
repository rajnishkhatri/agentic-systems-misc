#!/usr/bin/env python3
"""Generate agent_tool_call_benchmark.json with 150 tool calling validation cases.

This benchmark tests agent tool calling accuracy across 5 error categories:
- Correct calls (50 cases)
- Wrong tool selection (30 cases)
- Missing required arguments (25 cases)
- Invalid argument types (25 cases)
- Invalid argument values (20 cases)

Usage:
    python lesson-14/data/generate_tool_call_benchmark.py
"""

import json
from typing import Any


TOOLS = [
    {
        "name": "search_recipes",
        "description": "Search recipe database",
        "parameters": {
            "ingredients": {"type": "list[str]", "required": False},
            "dietary_restrictions": {"type": "list[str]", "required": False},
            "cuisine": {"type": "str", "required": False},
            "meal_type": {
                "type": "str",
                "required": False,
                "options": ["breakfast", "lunch", "dinner", "dessert", "snack"],
            },
            "max_cook_time": {"type": "int", "required": False, "min": 1, "max": 240},
            "max_results": {
                "type": "int",
                "required": False,
                "default": 10,
                "min": 1,
                "max": 100,
            },
        },
    },
    {
        "name": "get_recipe_details",
        "description": "Get full recipe by ID",
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
        "description": "Get nutritional information",
        "parameters": {"food": {"type": "str", "required": True}},
    },
    {
        "name": "get_user_preferences",
        "description": "Retrieve user dietary preferences",
        "parameters": {},
    },
    {
        "name": "search_web",
        "description": "Search external web",
        "parameters": {"query": {"type": "str", "required": True}},
    },
    {
        "name": "get_gita_verses",
        "description": "Search Bhagavad Gita verses",
        "parameters": {
            "chapter": {"type": "int", "required": False, "min": 1, "max": 18},
            "verse": {"type": "int", "required": False},
            "keyword": {"type": "str", "required": False},
            "max_results": {"type": "int", "required": False, "default": 5},
        },
    },
]


def generate_correct_calls() -> list[dict]:
    """Generate 50 correct tool calls."""
    cases = []

    # Recipe searches with dietary restrictions (25 cases)
    diets = ["vegan", "vegetarian", "gluten-free", "keto", "paleo"]
    for i in range(25):
        cases.append(
            {
                "id": f"tool_{i+1:03d}",
                "task": f"Find {diets[i % len(diets)]} recipes",
                "tool_call": {
                    "tool": "search_recipes",
                    "args": {"dietary_restrictions": [diets[i % len(diets)]]},
                },
                "labels": {
                    "is_valid": True,
                    "tool_selection": "CORRECT",
                    "args_validation": "VALID",
                },
                "difficulty": "easy",
            }
        )

    # Recipe searches with cuisine (15 cases)
    cuisines = ["Italian", "Chinese", "Mexican", "Indian", "Thai"]
    for i in range(25, 40):
        cases.append(
            {
                "id": f"tool_{i+1:03d}",
                "task": f"Find {cuisines[i % len(cuisines)]} recipes",
                "tool_call": {
                    "tool": "search_recipes",
                    "args": {"cuisine": cuisines[i % len(cuisines)]},
                },
                "labels": {
                    "is_valid": True,
                    "tool_selection": "CORRECT",
                    "args_validation": "VALID",
                },
                "difficulty": "easy",
            }
        )

    # Get recipe details (5 cases)
    for i in range(40, 45):
        cases.append(
            {
                "id": f"tool_{i+1:03d}",
                "task": f"Get recipe {i+1} details",
                "tool_call": {"tool": "get_recipe_details", "args": {"recipe_id": i + 1}},
                "labels": {
                    "is_valid": True,
                    "tool_selection": "CORRECT",
                    "args_validation": "VALID",
                },
                "difficulty": "easy",
            }
        )

    # Gita verses (5 cases)
    for i in range(45, 50):
        cases.append(
            {
                "id": f"tool_{i+1:03d}",
                "task": f"Get Gita Chapter {i-43} verses",
                "tool_call": {"tool": "get_gita_verses", "args": {"chapter": i - 43}},
                "labels": {
                    "is_valid": True,
                    "tool_selection": "CORRECT",
                    "args_validation": "VALID",
                },
                "difficulty": "easy",
            }
        )

    return cases


def generate_wrong_tool_calls() -> list[dict]:
    """Generate 30 wrong tool selection cases."""
    cases = []

    diets = [
        "vegan",
        "vegetarian",
        "gluten-free",
        "keto",
        "paleo",
        "dairy-free",
        "nut-free",
    ]

    for i in range(30):
        cases.append(
            {
                "id": f"tool_{51+i:03d}_wrong_tool",
                "task": f"Find {diets[i % len(diets)]} recipes",
                "tool_call": {
                    "tool": "search_web",
                    "args": {"query": f"{diets[i % len(diets)]} recipes"},
                },
                "gold_call": {
                    "tool": "search_recipes",
                    "args": {"dietary_restrictions": [diets[i % len(diets)]]},
                },
                "labels": {
                    "is_valid": False,
                    "tool_selection": "WRONG_TOOL",
                    "failure_reason": "Should use search_recipes (internal DB), not search_web (external)",
                },
                "difficulty": "easy",
            }
        )

    return cases


def generate_missing_required_args() -> list[dict]:
    """Generate 25 missing required argument cases."""
    cases = []

    # Missing recipe_id (15 cases)
    for i in range(15):
        cases.append(
            {
                "id": f"tool_{81+i:03d}_missing_required",
                "task": "Get recipe details",
                "tool_call": {"tool": "get_recipe_details", "args": {}},
                "labels": {
                    "is_valid": False,
                    "tool_selection": "CORRECT",
                    "args_validation": "MISSING_REQUIRED",
                    "failure_reason": "Missing required arg: recipe_id",
                },
                "difficulty": "easy",
            }
        )

    # Missing ingredients for shopping list (10 cases)
    for i in range(15, 25):
        cases.append(
            {
                "id": f"tool_{81+i:03d}_missing_required",
                "task": "Add to shopping list",
                "tool_call": {"tool": "add_to_shopping_list", "args": {}},
                "labels": {
                    "is_valid": False,
                    "tool_selection": "CORRECT",
                    "args_validation": "MISSING_REQUIRED",
                    "failure_reason": "Missing required arg: ingredients",
                },
                "difficulty": "easy",
            }
        )

    return cases


def generate_invalid_type_args() -> list[dict]:
    """Generate 25 invalid type cases."""
    cases = []

    type_errors = [
        ("max_cook_time", "30 minutes", "Should be int, not str", "search_recipes"),
        ("max_results", "ten", "Should be int, not str", "search_recipes"),
        ("ingredients", "pasta", "Should be list[str], not str", "search_recipes"),
        (
            "dietary_restrictions",
            "vegan",
            "Should be list[str], not str",
            "search_recipes",
        ),
        ("recipe_id", "123", "Should be int, not str", "get_recipe_details"),
    ]

    for i in range(25):
        arg_name, wrong_value, reason, tool_name = type_errors[i % len(type_errors)]

        cases.append(
            {
                "id": f"tool_{106+i:03d}_type_error",
                "task": f"Call with wrong {arg_name} type",
                "tool_call": {"tool": tool_name, "args": {arg_name: wrong_value}},
                "labels": {
                    "is_valid": False,
                    "tool_selection": "CORRECT",
                    "args_validation": "TYPE_ERROR",
                    "failure_reason": reason,
                },
                "difficulty": "medium",
            }
        )

    return cases


def generate_invalid_value_args() -> list[dict]:
    """Generate 20 invalid value cases."""
    cases = []

    # Invalid max_cook_time (out of range) (10 cases)
    for i in range(10):
        cases.append(
            {
                "id": f"tool_{131+i:03d}_value_error",
                "task": "Search with invalid cook time",
                "tool_call": {
                    "tool": "search_recipes",
                    "args": {"max_cook_time": -10 - i},
                },
                "labels": {
                    "is_valid": False,
                    "tool_selection": "CORRECT",
                    "args_validation": "VALUE_ERROR",
                    "failure_reason": "max_cook_time must be between 1 and 240",
                },
                "difficulty": "medium",
            }
        )

    # Invalid meal_type (not in options) (10 cases)
    invalid_meals = [
        "brunch",
        "snack-time",
        "teatime",
        "supper",
        "appetizer",
        "beverage",
        "course",
        "side",
        "main",
        "entree",
    ]
    for i in range(10):
        cases.append(
            {
                "id": f"tool_{141+i:03d}_value_error",
                "task": "Search with invalid meal type",
                "tool_call": {
                    "tool": "search_recipes",
                    "args": {"meal_type": invalid_meals[i]},
                },
                "labels": {
                    "is_valid": False,
                    "tool_selection": "CORRECT",
                    "args_validation": "VALUE_ERROR",
                    "failure_reason": "meal_type must be one of: breakfast, lunch, dinner, dessert, snack",
                },
                "difficulty": "medium",
            }
        )

    return cases


def generate_benchmark() -> dict[str, Any]:
    """Generate complete tool call benchmark.

    Returns:
        Benchmark dictionary with 150 test cases

    Raises:
        AssertionError: If test case count is incorrect
    """
    benchmark = {
        "version": "1.0",
        "created": "2025-11-12",
        "description": "Tool Call Validation Benchmark - 150 test cases for function calling errors",
        "statistics": {
            "total_cases": 150,
            "correct_calls": 50,
            "wrong_tool": 30,
            "missing_required_args": 25,
            "invalid_arg_types": 25,
            "invalid_arg_values": 20,
        },
        "available_tools": TOOLS,
        "test_cases": [],
    }

    # Generate all test case categories
    benchmark["test_cases"].extend(generate_correct_calls())
    benchmark["test_cases"].extend(generate_wrong_tool_calls())
    benchmark["test_cases"].extend(generate_missing_required_args())
    benchmark["test_cases"].extend(generate_invalid_type_args())
    benchmark["test_cases"].extend(generate_invalid_value_args())

    return benchmark


if __name__ == "__main__":
    benchmark = generate_benchmark()

    # Validate count
    assert (
        len(benchmark["test_cases"]) == 150
    ), f"Expected 150 cases, got {len(benchmark['test_cases'])}"

    # Save to file
    output_path = "lesson-14/data/agent_tool_call_benchmark.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(benchmark, f, indent=2, ensure_ascii=False)

    print(f"✅ Generated {len(benchmark['test_cases'])} tool call test cases")
    print(f"   Saved to: {output_path}")
    print()
    print("📊 Statistics:")
    for key, value in benchmark["statistics"].items():
        print(f"   - {key}: {value}")
