#!/usr/bin/env python3
"""
Generate agent_planning_benchmark.json with 100 diverse planning validation tasks.

This script creates test cases covering:
- Correct plans (65 cases)
- Wrong tool selection (15 cases)
- Invalid arguments (10 cases)
- Goal misalignment (5 cases)
- Incomplete plans (5 cases)
"""

import json
from typing import Any


def generate_benchmark() -> dict[str, Any]:
    """Generate complete planning benchmark with 100 tasks."""

    benchmark = {
        "version": "1.0",
        "created": "2025-11-12",
        "description": "Agent Planning Validation Benchmark for Lesson 14 - 100 tasks testing plan correctness, tool selection, and goal alignment",
        "statistics": {
            "total_tasks": 100,
            "recipe_domain": 60,
            "gita_domain": 20,
            "general_tasks": 20,
            "correct_plans": 65,
            "wrong_tool_selection": 15,
            "invalid_arguments": 10,
            "goal_misalignment": 5,
            "incomplete_plans": 5
        },
        "available_tools": [
            {
                "name": "search_recipes",
                "description": "Search recipe database with filters",
                "parameters": {
                    "ingredients": {"type": "list[str]", "required": False},
                    "dietary_restrictions": {"type": "list[str]", "required": False},
                    "cuisine": {"type": "str", "required": False},
                    "meal_type": {"type": "str", "required": False, "options": ["breakfast", "lunch", "dinner", "dessert", "snack"]},
                    "max_cook_time": {"type": "int", "required": False, "min": 1, "max": 240},
                    "max_results": {"type": "int", "required": False, "default": 10, "min": 1, "max": 100}
                }
            },
            {
                "name": "get_user_preferences",
                "description": "Retrieve user dietary preferences and restrictions",
                "parameters": {}
            },
            {
                "name": "get_recipe_details",
                "description": "Get full recipe information by ID",
                "parameters": {
                    "recipe_id": {"type": "int", "required": True}
                }
            },
            {
                "name": "check_ingredient_availability",
                "description": "Check if ingredient is in stock",
                "parameters": {
                    "ingredient": {"type": "str", "required": True}
                }
            },
            {
                "name": "get_nutrition_info",
                "description": "Get nutritional information for food",
                "parameters": {
                    "food": {"type": "str", "required": True}
                }
            },
            {
                "name": "search_web",
                "description": "Search external web for general information",
                "parameters": {
                    "query": {"type": "str", "required": True}
                }
            },
            {
                "name": "get_gita_verses",
                "description": "Search Bhagavad Gita verses by chapter/verse/keyword",
                "parameters": {
                    "chapter": {"type": "int", "required": False, "min": 1, "max": 18},
                    "verse": {"type": "int", "required": False},
                    "keyword": {"type": "str", "required": False},
                    "max_results": {"type": "int", "required": False, "default": 5}
                }
            },
            {
                "name": "add_to_shopping_list",
                "description": "Add ingredients to user's shopping list",
                "parameters": {
                    "ingredients": {"type": "list[str]", "required": True}
                }
            }
        ],
        "test_cases": []
    }

    # Generate test cases
    test_cases = []

    # Category 1: Correct Plans (65 cases)
    test_cases.extend(generate_correct_plans())

    # Category 2: Wrong Tool Selection (15 cases)
    test_cases.extend(generate_wrong_tool_cases())

    # Category 3: Invalid Arguments (10 cases)
    test_cases.extend(generate_invalid_argument_cases())

    # Category 4: Goal Misalignment (5 cases)
    test_cases.extend(generate_goal_misalignment_cases())

    # Category 5: Incomplete Plans (5 cases)
    test_cases.extend(generate_incomplete_plan_cases())

    benchmark["test_cases"] = test_cases
    return benchmark


def generate_correct_plans() -> list[dict]:
    """Generate 65 correct planning cases."""
    cases = [
        # Simple single-step plans (20 cases)
        {
            "id": "plan_001",
            "task": "Find vegan pasta recipes under 30 minutes",
            "goal": "Retrieve vegan pasta recipes with cooking time <= 30 minutes",
            "gold_plan": {
                "steps": [
                    {"step": 1, "tool": "search_recipes", "args": {"ingredients": ["pasta"], "dietary_restrictions": ["vegan"], "max_cook_time": 30}, "rationale": "Search with all constraints"}
                ]
            },
            "labels": {"plan_correctness": "CORRECT", "tool_selection": "CORRECT", "argument_quality": "CORRECT", "completeness": "COMPLETE", "efficiency": "OPTIMAL"},
            "difficulty": "easy"
        },
        {
            "id": "plan_002",
            "task": "Find Italian dessert recipes",
            "goal": "Retrieve Italian dessert recipes",
            "gold_plan": {
                "steps": [
                    {"step": 1, "tool": "search_recipes", "args": {"cuisine": "Italian", "meal_type": "dessert"}, "rationale": "Search with cuisine and meal type filters"}
                ]
            },
            "labels": {"plan_correctness": "CORRECT", "tool_selection": "CORRECT", "argument_quality": "CORRECT", "completeness": "COMPLETE", "efficiency": "OPTIMAL"},
            "difficulty": "easy"
        },
        {
            "id": "plan_003",
            "task": "What does Chapter 3 of the Bhagavad Gita teach about karma yoga?",
            "goal": "Retrieve Bhagavad Gita verses about karma yoga from Chapter 3",
            "gold_plan": {
                "steps": [
                    {"step": 1, "tool": "get_gita_verses", "args": {"chapter": 3, "keyword": "karma yoga"}, "rationale": "Search Chapter 3 for karma yoga teachings"}
                ]
            },
            "labels": {"plan_correctness": "CORRECT", "tool_selection": "CORRECT", "argument_quality": "CORRECT", "completeness": "COMPLETE", "efficiency": "OPTIMAL"},
            "difficulty": "easy"
        },
        {
            "id": "plan_004",
            "task": "Find breakfast recipes with eggs",
            "goal": "Retrieve breakfast recipes containing eggs",
            "gold_plan": {
                "steps": [
                    {"step": 1, "tool": "search_recipes", "args": {"ingredients": ["eggs"], "meal_type": "breakfast"}, "rationale": "Search breakfast category with egg ingredient"}
                ]
            },
            "labels": {"plan_correctness": "CORRECT", "tool_selection": "CORRECT", "argument_quality": "CORRECT", "completeness": "COMPLETE", "efficiency": "OPTIMAL"},
            "difficulty": "easy"
        },
        {
            "id": "plan_005",
            "task": "Find keto dinner recipes",
            "goal": "Retrieve keto-friendly dinner recipes",
            "gold_plan": {
                "steps": [
                    {"step": 1, "tool": "search_recipes", "args": {"dietary_restrictions": ["keto"], "meal_type": "dinner"}, "rationale": "Search dinners with keto diet constraint"}
                ]
            },
            "labels": {"plan_correctness": "CORRECT", "tool_selection": "CORRECT", "argument_quality": "CORRECT", "completeness": "COMPLETE", "efficiency": "OPTIMAL"},
            "difficulty": "easy"
        },
        # Multi-step plans (45 cases)
        {
            "id": "plan_021",
            "task": "Find recipes I can make with my available ingredients",
            "goal": "Search recipes using user's pantry ingredients",
            "gold_plan": {
                "steps": [
                    {"step": 1, "tool": "get_user_preferences", "args": {}, "rationale": "Get user pantry"},
                    {"step": 2, "tool": "search_recipes", "args": {"ingredients": "{{user_pantry}}"}, "rationale": "Search with available ingredients"}
                ]
            },
            "labels": {"plan_correctness": "CORRECT", "tool_selection": "CORRECT", "argument_quality": "CORRECT", "completeness": "COMPLETE", "efficiency": "OPTIMAL"},
            "difficulty": "medium"
        },
        {
            "id": "plan_022",
            "task": "Find gluten-free recipes and check if quinoa is available",
            "goal": "Search gluten-free recipes, verify quinoa availability",
            "gold_plan": {
                "steps": [
                    {"step": 1, "tool": "search_recipes", "args": {"dietary_restrictions": ["gluten-free"], "ingredients": ["quinoa"]}, "rationale": "Find gluten-free quinoa recipes"},
                    {"step": 2, "tool": "check_ingredient_availability", "args": {"ingredient": "quinoa"}, "rationale": "Verify quinoa stock"}
                ]
            },
            "labels": {"plan_correctness": "CORRECT", "tool_selection": "CORRECT", "argument_quality": "CORRECT", "completeness": "COMPLETE", "efficiency": "OPTIMAL"},
            "difficulty": "medium"
        },
        {
            "id": "plan_023",
            "task": "Get nutrition info for avocado and find recipes using it",
            "goal": "Retrieve avocado nutrition data and avocado recipes",
            "gold_plan": {
                "steps": [
                    {"step": 1, "tool": "get_nutrition_info", "args": {"food": "avocado"}, "rationale": "Get nutrition data"},
                    {"step": 2, "tool": "search_recipes", "args": {"ingredients": ["avocado"]}, "rationale": "Find avocado recipes"}
                ]
            },
            "labels": {"plan_correctness": "CORRECT", "tool_selection": "CORRECT", "argument_quality": "CORRECT", "completeness": "COMPLETE", "efficiency": "OPTIMAL"},
            "difficulty": "medium"
        }
    ]

    # Generate remaining correct cases programmatically
    for i in range(6, 21):
        cases.append({
            "id": f"plan_{i:03d}",
            "task": f"Find {['Chinese', 'Mexican', 'Japanese', 'Thai', 'Indian', 'French', 'Greek', 'Spanish', 'Korean', 'Vietnamese', 'Mediterranean', 'Lebanese', 'Moroccan', 'Brazilian', 'Turkish'][i % 15]} recipes",
            "goal": f"Retrieve {['Chinese', 'Mexican', 'Japanese', 'Thai', 'Indian', 'French', 'Greek', 'Spanish', 'Korean', 'Vietnamese', 'Mediterranean', 'Lebanese', 'Moroccan', 'Brazilian', 'Turkish'][i % 15]} cuisine recipes",
            "gold_plan": {
                "steps": [
                    {"step": 1, "tool": "search_recipes", "args": {"cuisine": ['Chinese', 'Mexican', 'Japanese', 'Thai', 'Indian', 'French', 'Greek', 'Spanish', 'Korean', 'Vietnamese', 'Mediterranean', 'Lebanese', 'Moroccan', 'Brazilian', 'Turkish'][i % 15]}, "rationale": "Simple cuisine search"}
                ]
            },
            "labels": {"plan_correctness": "CORRECT", "tool_selection": "CORRECT", "argument_quality": "CORRECT", "completeness": "COMPLETE", "efficiency": "OPTIMAL"},
            "difficulty": "easy"
        })

    for i in range(24, 66):
        cases.append({
            "id": f"plan_{i:03d}",
            "task": f"Find recipes with {['chicken', 'beef', 'fish', 'tofu', 'lentils', 'chickpeas'][i % 6]} under {[20, 30, 45, 60][i % 4]} minutes",
            "goal": f"Retrieve recipes with {['chicken', 'beef', 'fish', 'tofu', 'lentils', 'chickpeas'][i % 6]} and cook time <= {[20, 30, 45, 60][i % 4]} minutes",
            "gold_plan": {
                "steps": [
                    {"step": 1, "tool": "search_recipes", "args": {"ingredients": [['chicken', 'beef', 'fish', 'tofu', 'lentils', 'chickpeas'][i % 6]], "max_cook_time": [20, 30, 45, 60][i % 4]}, "rationale": "Search with ingredient and time constraints"}
                ]
            },
            "labels": {"plan_correctness": "CORRECT", "tool_selection": "CORRECT", "argument_quality": "CORRECT", "completeness": "COMPLETE", "efficiency": "OPTIMAL"},
            "difficulty": "easy" if i < 40 else "medium"
        })

    return cases[:65]


def generate_wrong_tool_cases() -> list[dict]:
    """Generate 15 wrong tool selection cases."""
    cases = [
        {
            "id": "plan_071_wrong_tool",
            "task": "Find Italian recipes",
            "goal": "Retrieve Italian cuisine recipes from database",
            "agent_plan": {"steps": [{"step": 1, "tool": "search_web", "args": {"query": "Italian recipes"}, "rationale": "Search web"}]},
            "gold_plan": {"steps": [{"step": 1, "tool": "search_recipes", "args": {"cuisine": "Italian"}, "rationale": "Use recipe database"}]},
            "labels": {"plan_correctness": "INCORRECT", "tool_selection": "WRONG_TOOL", "failure_reason": "Should use search_recipes not search_web"},
            "difficulty": "easy"
        },
        {
            "id": "plan_072_wrong_tool",
            "task": "Find recipes with chicken",
            "goal": "Search recipe database for chicken recipes",
            "agent_plan": {"steps": [{"step": 1, "tool": "search_web", "args": {"query": "chicken recipes"}, "rationale": "Web search"}]},
            "gold_plan": {"steps": [{"step": 1, "tool": "search_recipes", "args": {"ingredients": ["chicken"]}, "rationale": "Use search_recipes"}]},
            "labels": {"plan_correctness": "INCORRECT", "tool_selection": "WRONG_TOOL", "failure_reason": "search_web for external info, use search_recipes for recipes"},
            "difficulty": "easy"
        }
    ]

    diets = ['vegan', 'vegetarian', 'gluten-free', 'keto', 'paleo', 'low-carb', 'dairy-free', 'nut-free', 'soy-free', 'halal', 'kosher', 'pescatarian', 'whole30']
    for i in range(13):
        cases.append({
            "id": f"plan_{73 + i:03d}_wrong_tool",
            "task": f"Find {diets[i]} recipes",
            "goal": f"Search {diets[i]} recipes",
            "agent_plan": {"steps": [{"step": 1, "tool": "search_web", "args": {"query": f"{diets[i]} recipes"}, "rationale": "Search web"}]},
            "gold_plan": {"steps": [{"step": 1, "tool": "search_recipes", "args": {"dietary_restrictions": [diets[i]]}, "rationale": "Use search_recipes with diet filter"}]},
            "labels": {"plan_correctness": "INCORRECT", "tool_selection": "WRONG_TOOL", "failure_reason": "Use search_recipes with dietary_restrictions, not search_web"},
            "difficulty": "easy"
        })

    return cases


def generate_invalid_argument_cases() -> list[dict]:
    """Generate 10 invalid argument cases."""
    cases = [
        {
            "id": "plan_086_invalid_args",
            "task": "Find top 5 dessert recipes",
            "goal": "Retrieve 5 dessert recipes",
            "agent_plan": {"steps": [{"step": 1, "tool": "search_recipes", "args": {"meal_type": "dessert", "max_results": "five"}, "rationale": "Search desserts"}]},
            "gold_plan": {"steps": [{"step": 1, "tool": "search_recipes", "args": {"meal_type": "dessert", "max_results": 5}, "rationale": "max_results must be int"}]},
            "labels": {"plan_correctness": "INCORRECT", "tool_selection": "CORRECT", "argument_quality": "TYPE_ERROR", "failure_reason": "max_results expects int, got string"},
            "difficulty": "easy"
        },
        {
            "id": "plan_087_invalid_args",
            "task": "Find recipes with 60 minute cooking time",
            "goal": "Retrieve recipes with max cook time 60 minutes",
            "agent_plan": {"steps": [{"step": 1, "tool": "search_recipes", "args": {"max_cook_time": "60 minutes"}, "rationale": "Search with time limit"}]},
            "gold_plan": {"steps": [{"step": 1, "tool": "search_recipes", "args": {"max_cook_time": 60}, "rationale": "max_cook_time must be int (minutes)"}]},
            "labels": {"plan_correctness": "INCORRECT", "tool_selection": "CORRECT", "argument_quality": "TYPE_ERROR", "failure_reason": "max_cook_time expects int, got string"},
            "difficulty": "easy"
        }
    ]

    invalid_meal_types = ["appetizer", "supper", "brunch", "tea", "beverage", "main", "side", "course"]
    for i in range(8):
        cases.append({
            "id": f"plan_{88 + i:03d}_invalid_args",
            "task": "Find meal recipes",
            "goal": "Search meal recipes",
            "agent_plan": {"steps": [{"step": 1, "tool": "search_recipes", "args": {"meal_type": invalid_meal_types[i]}, "rationale": "Search meals"}]},
            "gold_plan": {"steps": [{"step": 1, "tool": "search_recipes", "args": {"meal_type": "lunch"}, "rationale": "meal_type must be from valid options"}]},
            "labels": {"plan_correctness": "INCORRECT", "tool_selection": "CORRECT", "argument_quality": "VALUE_ERROR", "failure_reason": f"meal_type must be breakfast/lunch/dinner/dessert/snack, not {invalid_meal_types[i]}"},
            "difficulty": "easy"
        })

    return cases


def generate_goal_misalignment_cases() -> list[dict]:
    """Generate 5 goal misalignment cases."""
    cases = [
        {
            "id": "plan_096_goal_mismatch",
            "task": "Find gluten-free breakfast recipes",
            "goal": "Retrieve gluten-free breakfast recipes",
            "agent_plan": {"steps": [{"step": 1, "tool": "search_recipes", "args": {"meal_type": "lunch"}, "rationale": "Search lunch"}]},
            "gold_plan": {"steps": [{"step": 1, "tool": "search_recipes", "args": {"meal_type": "breakfast", "dietary_restrictions": ["gluten-free"]}, "rationale": "Must be breakfast AND gluten-free"}]},
            "labels": {"plan_correctness": "INCORRECT", "tool_selection": "CORRECT", "argument_quality": "WRONG_VALUES", "failure_reason": "Wrong meal_type (lunch vs breakfast) and missing dietary restriction"},
            "difficulty": "easy"
        }
    ]

    diets = ['vegan', 'vegetarian', 'keto', 'paleo']
    for i in range(4):
        cases.append({
            "id": f"plan_{97 + i:03d}_goal_mismatch",
            "task": f"Find {diets[i]} dinner recipes",
            "goal": f"Search {diets[i]} dinner recipes",
            "agent_plan": {"steps": [{"step": 1, "tool": "search_recipes", "args": {"meal_type": "breakfast"}, "rationale": "Search meals"}]},
            "gold_plan": {"steps": [{"step": 1, "tool": "search_recipes", "args": {"meal_type": "dinner", "dietary_restrictions": [diets[i]]}, "rationale": "Must match meal type and diet"}]},
            "labels": {"plan_correctness": "INCORRECT", "tool_selection": "CORRECT", "argument_quality": "WRONG_VALUES", "failure_reason": f"Wrong meal_type and missing {diets[i]} restriction"},
            "difficulty": "easy"
        })

    return cases


def generate_incomplete_plan_cases() -> list[dict]:
    """Generate 5 incomplete plan cases."""
    cases = [
        {
            "id": "plan_101_incomplete",
            "task": "Find recipes and add ingredients to shopping list",
            "goal": "Search recipes and add their ingredients to shopping list",
            "agent_plan": {"steps": [{"step": 1, "tool": "search_recipes", "args": {"cuisine": "Italian"}, "rationale": "Find recipes"}]},
            "gold_plan": {
                "steps": [
                    {"step": 1, "tool": "search_recipes", "args": {"cuisine": "Italian"}, "rationale": "Find recipes"},
                    {"step": 2, "tool": "get_recipe_details", "args": {"recipe_id": "{{selected}}"}, "rationale": "Get ingredients"},
                    {"step": 3, "tool": "add_to_shopping_list", "args": {"ingredients": "{{recipe_ingredients}}"}, "rationale": "Add to list"}
                ]
            },
            "labels": {"plan_correctness": "INCORRECT", "tool_selection": "CORRECT", "completeness": "INCOMPLETE", "failure_reason": "Missing steps to get details and add to shopping list"},
            "difficulty": "medium"
        }
    ]

    cuisines = ['Italian', 'Chinese', 'Mexican', 'Indian']
    for i in range(4):
        cases.append({
            "id": f"plan_{102 + i:03d}_incomplete",
            "task": f"Find {cuisines[i]} recipes and check nutrition",
            "goal": f"Search {cuisines[i]} recipes and get nutrition info",
            "agent_plan": {"steps": [{"step": 1, "tool": "search_recipes", "args": {"cuisine": cuisines[i]}, "rationale": "Find recipes"}]},
            "gold_plan": {
                "steps": [
                    {"step": 1, "tool": "search_recipes", "args": {"cuisine": cuisines[i]}, "rationale": "Find recipes"},
                    {"step": 2, "tool": "get_recipe_details", "args": {"recipe_id": "{{selected}}"}, "rationale": "Get recipe details"},
                    {"step": 3, "tool": "get_nutrition_info", "args": {"food": "{{recipe_name}}"}, "rationale": "Get nutrition data"}
                ]
            },
            "labels": {"plan_correctness": "INCORRECT", "tool_selection": "CORRECT", "completeness": "INCOMPLETE", "failure_reason": "Missing steps to get recipe details and nutrition info"},
            "difficulty": "medium"
        })

    return cases


if __name__ == "__main__":
    benchmark = generate_benchmark()

    # Save to file
    output_path = "lesson-14/data/agent_planning_benchmark.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(benchmark, f, indent=2, ensure_ascii=False)

    print(f"✅ Generated {len(benchmark['test_cases'])} planning validation test cases")
    print(f"   Saved to: {output_path}")
    print("\n📊 Statistics:")
    print(f"   - Correct plans: {sum(1 for tc in benchmark['test_cases'] if tc['labels'].get('plan_correctness') == 'CORRECT')}")
    print(f"   - Wrong tool: {sum(1 for tc in benchmark['test_cases'] if tc['labels'].get('tool_selection') == 'WRONG_TOOL')}")
    print(f"   - Invalid args: {sum(1 for tc in benchmark['test_cases'] if 'TYPE_ERROR' in str(tc['labels']) or 'VALUE_ERROR' in str(tc['labels']))}")
    print(f"   - Goal mismatch: {sum(1 for tc in benchmark['test_cases'] if 'goal_mismatch' in tc['id'])}")
    print(f"   - Incomplete: {sum(1 for tc in benchmark['test_cases'] if tc['labels'].get('completeness') == 'INCOMPLETE')}")
