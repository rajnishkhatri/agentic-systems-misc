"""Generate test queries for Recipe Bot evaluation.

This script generates diverse test queries based on dimension combinations
to evaluate the Recipe Bot's response quality across different scenarios.

Based on PRD: tasks/0001-prd-test-query-generation.md
"""

from __future__ import annotations

import csv
import json
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Final

import sys
import os

# Add parent directory to path to import backend.utils
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from backend.utils import get_agent_response

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


def verify_dimension_coverage(tuples: list[dict[str, str]]) -> dict[str, list[str]]:
    """Verify that tuples provide adequate coverage of dimension values.

    Checks that at least one tuple exists for required dimension values
    (from priorities 1, 2, 4, 5 as per PRD FR5).

    Args:
        tuples: List of dimension tuple dictionaries

    Returns:
        Dictionary mapping dimension names to lists of missing values.
        Empty lists indicate full coverage for that dimension.
    """
    if not tuples:
        raise ValueError("No tuples provided for coverage verification")

    # Collect actual values used in tuples
    dietary_used = set()
    ingredient_used = set()
    complexity_used = set()
    meal_type_used = set()

    for t in tuples:
        dietary_used.add(t.get("dietary_restriction", ""))
        ingredient_used.add(t.get("ingredient_constraints", ""))
        complexity_used.add(t.get("complexity_level", ""))
        meal_type_used.add(t.get("meal_type", ""))

    # Remove "none" and empty strings from consideration
    dietary_used.discard("")
    dietary_used.discard(NONE_VALUE)
    ingredient_used.discard("")
    ingredient_used.discard(NONE_VALUE)

    # Check coverage requirements
    missing = {}

    # Priority 1: dietary_restriction (at least MIN_DIETARY_VALUES different values)
    if len(dietary_used) < MIN_DIETARY_VALUES:
        missing["dietary_restriction"] = [
            v for v in DIETARY_RESTRICTIONS if v not in dietary_used
        ][:MIN_DIETARY_VALUES - len(dietary_used)]
    else:
        missing["dietary_restriction"] = []

    # Priority 2: ingredient_constraints (at least MIN_INGREDIENT_VALUES different values)
    if len(ingredient_used) < MIN_INGREDIENT_VALUES:
        missing["ingredient_constraints"] = [
            v for v in INGREDIENT_CONSTRAINTS if v not in ingredient_used
        ][:MIN_INGREDIENT_VALUES - len(ingredient_used)]
    else:
        missing["ingredient_constraints"] = []

    # Priority 4: complexity_level (ALL 3 values required)
    missing_complexity = [v for v in COMPLEXITY_LEVELS if v not in complexity_used]
    missing["complexity_level"] = missing_complexity

    # Priority 5: meal_type (at least MIN_MEAL_TYPE_VALUES different values)
    if len(meal_type_used) < MIN_MEAL_TYPE_VALUES:
        missing["meal_type"] = [
            v for v in MEAL_TYPES if v not in meal_type_used
        ][:MIN_MEAL_TYPE_VALUES - len(meal_type_used)]
    else:
        missing["meal_type"] = []

    return missing


# --- Tuple Generation (Task 2.1) ---

def generate_dimension_tuples() -> list[dict[str, str]]:
    """Generate 15-20 unique dimension tuples using LLM.

    Uses get_agent_response() to call LLM with a custom prompt that maximizes
    coverage across all dimensions while creating realistic user scenarios.

    Includes retry logic (up to 3 attempts with exponential backoff) for LLM API failures.

    Returns:
        List of dimension tuple dictionaries, each containing:
        - dietary_restriction (str)
        - ingredient_constraints (str)
        - meal_portion (str, optional - may be empty)
        - complexity_level (str)
        - meal_type (str)
        - cuisine_type (str, optional - may be empty)

    Raises:
        ValueError: If LLM response cannot be parsed
        RuntimeError: If generation fails after all retries
    """
    max_retries = 3
    base_delay = 1.0  # seconds

    for attempt in range(max_retries):
        try:
            return _generate_dimension_tuples_impl()
        except Exception as e:
            if attempt < max_retries - 1:
                delay = base_delay * (2 ** attempt)  # Exponential backoff
                print(f"Attempt {attempt + 1}/{max_retries} failed: {e}")
                print(f"Retrying in {delay:.1f} seconds...")
                time.sleep(delay)
            else:
                raise RuntimeError(f"Failed to generate tuples after {max_retries} attempts") from e

    # Should never reach here, but satisfies type checker
    raise RuntimeError(f"Failed to generate tuples after {max_retries} attempts")


def _generate_dimension_tuples_impl() -> list[dict[str, str]]:
    """Internal implementation of tuple generation (Task 2.7).

    Separated to enable retry logic without code duplication.

    Returns:
        List of dimension tuple dictionaries

    Raises:
        ValueError: If LLM response cannot be parsed
        Exception: For any LLM API errors
    """
    # Construct prompt for tuple generation (Task 2.2)
    system_prompt = """You are a test data generator for a Recipe Bot evaluation system.
Your task is to generate diverse dimension combinations that represent realistic user scenarios."""

    user_prompt = f"""Generate {NUM_QUERIES_TARGET} unique dimension combinations for recipe bot test queries.

**Dimensions:**
1. dietary_restriction: {', '.join(DIETARY_RESTRICTIONS)} OR "none"
2. ingredient_constraints: {', '.join(INGREDIENT_CONSTRAINTS)} OR "none"
3. meal_portion: {', '.join(MEAL_PORTIONS)} OR "" (empty string, optional)
4. complexity_level: {', '.join(COMPLEXITY_LEVELS)} (ALL 3 must appear)
5. meal_type: {', '.join(MEAL_TYPES)}
6. cuisine_type: {', '.join(CUISINE_TYPES)} OR "" (empty string, optional)

**Coverage Requirements:**
- Include at least {MIN_DIETARY_VALUES} different dietary_restriction values
- Include at least {MIN_INGREDIENT_VALUES} different ingredient_constraints values
- Include ALL {MIN_COMPLEXITY_VALUES} complexity_level values
- Include at least {MIN_MEAL_TYPE_VALUES} different meal_type values
- Include meal_portion in {int(MEAL_PORTION_MIN_PERCENTAGE * 100)}-{int(MEAL_PORTION_MAX_PERCENTAGE * 100)}% of tuples (use "" when not relevant)
- Include at least {int(EDGE_CASE_MIN_PERCENTAGE * NUM_QUERIES_TARGET)} edge cases (contradictory/unusual combinations)

**Realistic Scenarios:**
Generate combinations that represent real users:
- Family dinners (4-6 people, moderate complexity)
- Quick solo meals (1 person, quick/simple)
- Special dietary needs with constraints
- Beginner cooks with simple ingredients
- Food enthusiasts trying gourmet recipes

**Edge Cases (15% minimum):**
Include challenging scenarios like:
- Over-constrained: multiple restrictions + limited ingredients
- Minimal info: "none" for dietary + "none" for ingredients
- Unusual: vegan + specific meat-focused cuisine

**Output Format:**
Return ONLY a valid JSON array of objects. Each object must have ALL required fields.

Example:
```json
[
  {{
    "dietary_restriction": "vegan",
    "ingredient_constraints": "pantry-only",
    "meal_portion": "4 people",
    "complexity_level": "quick/simple",
    "meal_type": "dinner",
    "cuisine_type": ""
  }},
  {{
    "dietary_restriction": "none",
    "ingredient_constraints": "specific ingredients available",
    "meal_portion": "",
    "complexity_level": "moderate",
    "meal_type": "lunch",
    "cuisine_type": "Italian"
  }}
]
```

Generate {NUM_QUERIES_TARGET} unique tuples now. Return ONLY the JSON array, no other text."""

    # Call LLM with custom system prompt
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]

    response_messages = get_agent_response(messages)

    # Extract assistant's response (last message)
    assistant_response = response_messages[-1]["content"]

    # Parse JSON response (Task 2.4)
    try:
        # Remove code blocks if present
        if "```json" in assistant_response:
            assistant_response = assistant_response.split("```json")[1].split("```")[0]
        elif "```" in assistant_response:
            assistant_response = assistant_response.split("```")[1].split("```")[0]

        tuples = json.loads(assistant_response.strip())

        if not isinstance(tuples, list):
            raise ValueError("LLM response is not a JSON array")

        # Convert to list of dicts and validate
        validated_tuples = []
        seen_tuples = set()  # For deduplication (Task 2.5)

        for i, t in enumerate(tuples):
            if not isinstance(t, dict):
                print(f"Warning: Tuple {i} is not a dict, skipping")
                continue

            # Ensure all required fields present
            if not validate_tuple(t):
                print(f"Warning: Tuple {i} failed validation, skipping")
                continue

            # Deduplication: Create a comparable string representation (Task 2.5)
            # Sort keys to ensure consistent comparison
            tuple_signature = json.dumps(t, sort_keys=True)

            if tuple_signature in seen_tuples:
                print(f"Warning: Tuple {i} is a duplicate, skipping")
                continue

            seen_tuples.add(tuple_signature)
            validated_tuples.append(t)

        if len(validated_tuples) < NUM_QUERIES_TARGET:
            print(f"Warning: Only {len(validated_tuples)} valid tuples generated (target: {NUM_QUERIES_TARGET})")

        # Verify coverage (Task 2.6)
        missing_values = verify_dimension_coverage(validated_tuples)
        has_missing = any(missing_values.values())

        if has_missing:
            print("\nCoverage verification warnings:")
            for dim, missing in missing_values.items():
                if missing:
                    print(f"  - {dim}: Missing {len(missing)} value(s): {', '.join(missing)}")

        return validated_tuples

    except (json.JSONDecodeError, ValueError) as e:
        raise ValueError(f"Failed to parse LLM response as JSON: {e}\nResponse: {assistant_response[:200]}") from e


# --- Query Verification (Task 1.3) ---

def convert_tuple_to_query(tuple_dict: dict[str, str]) -> str:
    """Convert a dimension tuple to a natural language query.
    
    Args:
        tuple_dict: Dictionary containing dimension values
        
    Returns:
        Natural language query string
    """
    parts = []
    
    # Dietary restriction
    if tuple_dict.get("dietary_restriction") and tuple_dict["dietary_restriction"] != NONE_VALUE:
        parts.append(f"I'm {tuple_dict['dietary_restriction']}")
    
    # Ingredient constraints
    if tuple_dict.get("ingredient_constraints") and tuple_dict["ingredient_constraints"] != NONE_VALUE:
        if tuple_dict["ingredient_constraints"] == "pantry-only":
            parts.append("I only have basic pantry ingredients")
        elif tuple_dict["ingredient_constraints"] == "leftovers":
            parts.append("I want to use up leftovers")
        elif tuple_dict["ingredient_constraints"] == "seasonal ingredients":
            parts.append("I want to use seasonal ingredients")
        elif tuple_dict["ingredient_constraints"] == "minimal ingredients":
            parts.append("I want something with minimal ingredients")
        elif tuple_dict["ingredient_constraints"] == "one-pot meals":
            parts.append("I want a one-pot meal")
        elif tuple_dict["ingredient_constraints"] == "specific ingredients available":
            parts.append("I have some specific ingredients I want to use")
    
    # Meal portion
    if tuple_dict.get("meal_portion"):
        parts.append(f"for {tuple_dict['meal_portion']}")
    
    # Complexity level
    if tuple_dict.get("complexity_level"):
        if tuple_dict["complexity_level"] == "quick/simple":
            parts.append("something quick and simple")
        elif tuple_dict["complexity_level"] == "moderate":
            parts.append("something moderate difficulty")
        elif tuple_dict["complexity_level"] == "advanced/gourmet":
            parts.append("something advanced or gourmet")
    
    # Meal type
    if tuple_dict.get("meal_type"):
        parts.append(f"for {tuple_dict['meal_type']}")
    
    # Cuisine type
    if tuple_dict.get("cuisine_type"):
        parts.append(f"in {tuple_dict['cuisine_type']} style")
    
    # Construct the query
    if parts:
        query = "I need a recipe " + ", ".join(parts) + "."
    else:
        query = "I need a recipe."
    
    return query


def verify_query_with_agent(tuple_dict: dict[str, str]) -> dict[str, Any]:
    """Verify that a dimension tuple produces a valid recipe response.
    
    Args:
        tuple_dict: Dictionary containing dimension values
        
    Returns:
        Dictionary with verification results:
        - success: bool
        - query: str (the generated query)
        - response: str (the agent's response)
        - error: str (if any error occurred)
    """
    try:
        # Convert tuple to natural language query
        query = convert_tuple_to_query(tuple_dict)
        
        # Create messages for the agent
        messages = [
            {"role": "user", "content": query}
        ]
        
        # Get agent response
        response_messages = get_agent_response(messages)
        response = response_messages[-1]["content"]
        
        # Basic validation: check if response contains expected recipe structure
        response_lower = response.lower()
        
        # Check for title (markdown bold formatting)
        has_title = "**" in response and any(word in response_lower for word in ["recipe", "dish", "meal", "crisp", "toast", "skillet", "enchilada", "frittata", "eggplant", "parmigiana"])
        
        # Check for ingredients (markdown list or bullet points)
        has_ingredients = ("**ingredients" in response_lower or 
                          "* " in response or 
                          "- " in response or
                          any(word in response_lower for word in ["ingredients:", "ingredients list"]))
        
        # Check for instructions (numbered steps or cooking verbs)
        has_instructions = ("**instructions" in response_lower or
                           any(word in response_lower for word in ["step", "cook", "prepare", "bake", "heat", "mix", "add", "place", "serve"]) or
                           any(char.isdigit() for char in response))  # Contains numbers (likely step numbers)
        
        success = has_title and has_ingredients and has_instructions
        
        return {
            "success": success,
            "query": query,
            "response": response,
            "error": None
        }
        
    except Exception as e:
        return {
            "success": False,
            "query": convert_tuple_to_query(tuple_dict),
            "response": "",
            "error": str(e)
        }


def verify_all_queries(tuples: list[dict[str, str]]) -> dict[str, Any]:
    """Verify all generated tuples produce valid recipe responses.

    Args:
        tuples: List of dimension tuple dictionaries

    Returns:
        Dictionary with verification results:
        - total: int (total number of tuples)
        - successful: int (number of successful verifications)
        - failed: int (number of failed verifications)
        - pass_rate: float (success rate)
        - results: list[dict] (detailed results for each tuple)
    """
    print("Verifying queries with Recipe Bot agent...")
    print()

    results = []
    successful = 0

    for i, tuple_dict in enumerate(tuples, 1):
        print(f"Verifying query {i}/{len(tuples)}: {tuple_dict['dietary_restriction']} | {tuple_dict['ingredient_constraints']} | {tuple_dict['complexity_level']} | {tuple_dict['meal_type']}")

        result = verify_query_with_agent(tuple_dict)
        results.append(result)

        if result["success"]:
            successful += 1
            print(f"  ✅ Success")
        else:
            print(f"  ❌ Failed: {result['error'] or 'Invalid response format'}")

        print()

    pass_rate = successful / len(tuples) if tuples else 0.0

    return {
        "total": len(tuples),
        "successful": successful,
        "failed": len(tuples) - successful,
        "pass_rate": pass_rate,
        "results": results
    }


# --- CSV Output (Task 4.0) ---

def write_queries_to_csv(tuples: list[dict[str, str]], output_path: str | None = None) -> str:
    """Write dimension tuples and natural language queries to CSV file.

    Creates a CSV file with columns: query_id, dietary_restriction, ingredient_constraints,
    meal_portion, complexity_level, meal_type, cuisine_type, natural_language_query.

    Args:
        tuples: List of dimension tuple dictionaries
        output_path: Optional output file path. If None, generates timestamped filename
                    in data/ directory (format: test_queries_generated_YYYYMMDD_HHMMSS.csv)

    Returns:
        The path to the created CSV file

    Raises:
        ValueError: If tuples list is empty
        OSError: If file writing fails (permissions, disk space, etc.)
        TypeError: If tuples is not a list or contains non-dict elements
    """
    # Step 1: Type checking
    if not isinstance(tuples, list):
        raise TypeError("tuples must be a list")

    if not tuples:
        raise ValueError("tuples list cannot be empty")

    for i, t in enumerate(tuples):
        if not isinstance(t, dict):
            raise TypeError(f"tuple at index {i} must be a dict, got {type(t).__name__}")

    # Step 2: Generate output path with timestamp if not provided (Task 4.3)
    if output_path is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = f"data/test_queries_generated_{timestamp}.csv"

    # Step 3: Create data directory if it doesn't exist (Task 4.6)
    output_file = Path(output_path)
    try:
        output_file.parent.mkdir(parents=True, exist_ok=True)
    except OSError as e:
        raise OSError(f"Failed to create directory {output_file.parent}: {e}") from e

    # Step 4: Write CSV with proper schema (Task 4.2, 4.4, 4.5)
    try:
        with open(output_file, 'w', encoding='utf-8', newline='') as f:
            # Define CSV schema per PRD FR4
            fieldnames = [
                'query_id',
                'dietary_restriction',
                'ingredient_constraints',
                'meal_portion',
                'complexity_level',
                'meal_type',
                'cuisine_type',
                'natural_language_query'
            ]

            # Use csv.QUOTE_MINIMAL for proper escaping (Task 4.4)
            writer = csv.DictWriter(f, fieldnames=fieldnames, quoting=csv.QUOTE_MINIMAL)

            # Write header
            writer.writeheader()

            # Write each tuple as a row
            for i, tuple_dict in enumerate(tuples, start=1):
                # Generate natural language query from tuple
                natural_query = convert_tuple_to_query(tuple_dict)

                # Create row with all fields
                row = {
                    'query_id': f"Q{i:03d}",  # Format as Q001, Q002, etc.
                    'dietary_restriction': tuple_dict.get('dietary_restriction', ''),
                    'ingredient_constraints': tuple_dict.get('ingredient_constraints', ''),
                    'meal_portion': tuple_dict.get('meal_portion', ''),
                    'complexity_level': tuple_dict.get('complexity_level', ''),
                    'meal_type': tuple_dict.get('meal_type', ''),
                    'cuisine_type': tuple_dict.get('cuisine_type', ''),
                    'natural_language_query': natural_query
                }

                writer.writerow(row)

        return str(output_file)

    except OSError as e:
        raise OSError(f"Failed to write CSV file {output_file}: {e}") from e


# --- Main Execution ---

def main():
    """Main function to generate and save test queries."""
    print("Generating test queries for Recipe Bot evaluation...")
    print(f"Target: {NUM_QUERIES_TARGET}-{NUM_QUERIES_MAX} queries")
    print()
    
    try:
        # Generate dimension tuples
        tuples = generate_dimension_tuples()
        
        print(f"Successfully generated {len(tuples)} dimension tuples")
        print()
        
        # Display summary
        print("Generated tuples summary:")
        for i, t in enumerate(tuples, 1):
            print(f"{i:2d}. {t['dietary_restriction']} | {t['ingredient_constraints']} | {t['complexity_level']} | {t['meal_type']}")
            if t.get('meal_portion'):
                print(f"     Portion: {t['meal_portion']}")
            if t.get('cuisine_type'):
                print(f"     Cuisine: {t['cuisine_type']}")
            print()
        
        # Save to CSV file (Task 4.0)
        print(f"Writing queries to CSV...")
        csv_file = write_queries_to_csv(tuples)
        print(f"✅ Saved {len(tuples)} queries to {csv_file}")

        # Also save JSON for reference
        json_file = csv_file.replace('.csv', '.json')
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(tuples, f, indent=2)
        print(f"✅ Saved dimension tuples to {json_file}")
        
        # Verify queries with Recipe Bot agent (Task 1.3)
        print("\n" + "="*60)
        verification_results = verify_all_queries(tuples)
        
        print(f"\nVerification Summary:")
        print(f"  Total queries: {verification_results['total']}")
        print(f"  Successful: {verification_results['successful']}")
        print(f"  Failed: {verification_results['failed']}")
        print(f"  Pass rate: {verification_results['pass_rate']:.1%}")
        
        # Check if pass rate meets requirement (PRD FR5.5)
        if verification_results['pass_rate'] < VALIDATION_PASS_RATE_TARGET:
            print(f"\n⚠️  WARNING: Pass rate {verification_results['pass_rate']:.1%} is below target {VALIDATION_PASS_RATE_TARGET:.1%}")
            print("Some queries may need adjustment for better Recipe Bot compatibility.")
        else:
            print(f"\n✅ All queries passed validation (≥{VALIDATION_PASS_RATE_TARGET:.1%})")

        # Save verification results
        verification_file = csv_file.replace('.csv', '_verification.json')
        with open(verification_file, 'w', encoding='utf-8') as f:
            json.dump(verification_results, f, indent=2)
        print(f"✅ Verification results saved to {verification_file}")

        print(f"\n{'='*60}")
        print(f"Summary:")
        print(f"  CSV output: {csv_file}")
        print(f"  JSON output: {json_file}")
        print(f"  Verification: {verification_file}")
        print(f"{'='*60}")
        
    except Exception as e:
        print(f"Error generating test queries: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
