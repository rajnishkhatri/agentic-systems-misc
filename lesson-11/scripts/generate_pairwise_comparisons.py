#!/usr/bin/env python3
"""
Generate pairwise comparison datasets for LLM evaluation.

This script creates a JSON file containing pairwise comparisons between model outputs
using AI judges. Supports multiple evaluation dimensions and parallel processing.

Usage:
    python generate_pairwise_comparisons.py --num_comparisons 100 --output comparisons.json
    python generate_pairwise_comparisons.py --dimension helpfulness --model gpt-4o-mini
"""

import argparse
import json
import os
import sys
from pathlib import Path
from typing import List, Dict, Any
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm

# Add parent directory to path to import backend modules
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from backend.ai_judge_framework import GenericCriteriaJudge


# ============================================================================
# Sample Queries and Responses (Recipe Bot Domain)
# ============================================================================

SAMPLE_QUERIES = [
    "How do I make gluten-free pasta from scratch?",
    "What's a quick weeknight dinner for a family of four?",
    "Can you suggest a vegan dessert for a birthday party?",
    "How do I properly brown butter for cookies?",
    "What are good substitutes for eggs in baking?",
    "How can I make crispy fried chicken at home?",
    "What's the best way to cook rice perfectly every time?",
    "Can you explain the difference between baking soda and baking powder?",
    "How do I make homemade pizza dough?",
    "What are some healthy breakfast options for busy mornings?",
    "How do I cook a perfect medium-rare steak?",
    "What's a good recipe for chocolate chip cookies?",
    "How can I make my own pasta sauce?",
    "What are some easy appetizers for a party?",
    "How do I make fluffy pancakes?",
    "What's the secret to a moist chocolate cake?",
    "How can I reduce sodium in my cooking?",
    "What are good meal prep ideas for the week?",
    "How do I make crispy roasted vegetables?",
    "What's a simple recipe for homemade bread?",
]

# Simulated responses from different models
# Model A: Detailed, comprehensive responses
# Model B: Concise, action-oriented responses
# Model C: Creative, conversational responses

def get_model_a_response(query: str) -> str:
    """Generate detailed response (simulated GPT-4 style)."""
    responses = {
        "How do I make gluten-free pasta from scratch?":
            "To make gluten-free pasta from scratch, you'll need 2 cups of gluten-free flour blend (rice flour + tapioca starch + xanthan gum), 3 large eggs, 1 tbsp olive oil, and a pinch of salt. Mix the dry ingredients, create a well in the center, add eggs and oil, then knead for 8-10 minutes until smooth. Rest the dough for 30 minutes covered, then roll out thinly and cut into desired shapes. Cook in boiling salted water for 2-3 minutes. The xanthan gum is crucial as it replaces the gluten's binding properties.",

        "What's a quick weeknight dinner for a family of four?":
            "A great quick weeknight dinner is Sheet Pan Chicken Fajitas. Slice 1.5 lbs chicken breast, 2 bell peppers, and 1 onion. Toss with 2 tbsp olive oil, 1 tsp cumin, 1 tsp chili powder, salt, and pepper. Spread on a sheet pan and roast at 425°F for 20 minutes. Serve with tortillas, sour cream, and guacamole. Total time: 30 minutes. You can prep the vegetables in advance to save even more time.",
    }
    return responses.get(query, "I'd recommend following these steps: First, gather your ingredients. Second, prepare them according to standard techniques. Third, cook using appropriate heat and timing. Finally, serve and enjoy!")

def get_model_b_response(query: str) -> str:
    """Generate concise response (simulated GPT-4o-mini style)."""
    responses = {
        "How do I make gluten-free pasta from scratch?":
            "Mix 2 cups gluten-free flour blend with 3 eggs and 1 tbsp olive oil. Knead 8-10 min, rest 30 min, roll out, cut, and cook 2-3 min in boiling water.",

        "What's a quick weeknight dinner for a family of four?":
            "Sheet Pan Chicken Fajitas: Toss sliced chicken, peppers, onions with spices and oil. Roast at 425°F for 20 min. Serve with tortillas. Done in 30 min.",
    }
    return responses.get(query, "Quick steps: Gather ingredients, prepare, cook, serve.")

def get_model_c_response(query: str) -> str:
    """Generate creative response (simulated Claude style)."""
    responses = {
        "How do I make gluten-free pasta from scratch?":
            "Making gluten-free pasta is like a delightful science experiment! You'll want to combine your gluten-free flour blend (think rice flour as your base) with eggs to create that silky dough. The magic ingredient? Xanthan gum—it's the superhero that gives your pasta that classic chewy texture. After kneading and a brief rest, you'll roll it out and transform it into beautiful ribbons or shapes. A quick 2-3 minute dip in boiling water, and voilà—fresh pasta that everyone can enjoy!",

        "What's a quick weeknight dinner for a family of four?":
            "Let me share a weeknight lifesaver: imagine tossing seasoned chicken strips and colorful bell peppers onto a single sheet pan, sliding it into a hot oven, and 20 minutes later—dinner's ready! We're talking Sheet Pan Chicken Fajitas here. The beauty? Everything cooks together, minimal cleanup, maximum flavor. Serve with warm tortillas and your family's favorite toppings. It's the kind of meal that makes you feel like a kitchen rockstar even on your busiest days.",
    }
    return responses.get(query, "Here's a creative approach: Think of cooking as an adventure. Start with quality ingredients, add a dash of confidence, and let your intuition guide you. The result will be delicious!")


# ============================================================================
# Comparison Generation
# ============================================================================

def generate_single_comparison(
    query: str,
    response_a: str,
    response_b: str,
    dimension: str,
    model: str,
    attempt: int = 0
) -> Dict[str, Any]:
    """Generate a single pairwise comparison using AI judge.

    Args:
        query: User query
        response_a: First model's response
        response_b: Second model's response
        dimension: Evaluation dimension
        model: Judge model to use
        attempt: Retry attempt number

    Returns:
        Comparison dictionary
    """
    criteria_map = {
        "helpfulness": "Evaluate which response better helps the user achieve their goal. Consider completeness, actionability, and clarity.",
        "correctness": "Evaluate which response is more factually accurate and follows proper techniques. Consider domain knowledge and best practices.",
        "conciseness": "Evaluate which response conveys the information more efficiently without sacrificing important details. Consider brevity and clarity.",
        "safety": "Evaluate which response better considers food safety, dietary restrictions, and potential hazards. Consider allergen awareness and safe cooking practices.",
    }

    criteria_description = criteria_map.get(
        dimension,
        f"Evaluate which response is better for {dimension}."
    )

    # Create judge
    judge = GenericCriteriaJudge(
        model=model,
        criteria=f"comparative_{dimension}",
        criteria_description=criteria_description,
        temperature=0.0
    )

    # Create combined prompt
    combined_query = f"""
Query: {query}

Response A: {response_a}

Response B: {response_b}

Which response is better for {dimension}? Respond with JSON containing:
- "answer": "A" or "B"
- "reasoning": Brief explanation of your choice
"""

    try:
        result = judge.evaluate(query=combined_query, response="")

        # Parse winner (handle various response formats)
        winner = result.score if result.score in ["A", "B"] else "A"

        return {
            "query": query,
            "response_a": response_a,
            "response_b": response_b,
            "winner": winner,
            "rationale": result.reasoning,
            "dimension": dimension,
            "judge_model": model
        }

    except Exception as e:
        # Retry once on failure
        if attempt < 1:
            print(f"  Retrying comparison (attempt {attempt + 1})...")
            return generate_single_comparison(
                query, response_a, response_b, dimension, model, attempt + 1
            )
        else:
            # Return default comparison on repeated failure
            return {
                "query": query,
                "response_a": response_a,
                "response_b": response_b,
                "winner": "A",  # Default
                "rationale": f"Evaluation failed: {str(e)}",
                "dimension": dimension,
                "judge_model": model
            }


def generate_comparisons_parallel(
    num_comparisons: int,
    dimension: str,
    model: str,
    max_workers: int = 5
) -> List[Dict[str, Any]]:
    """Generate pairwise comparisons in parallel.

    Args:
        num_comparisons: Number of comparisons to generate
        dimension: Evaluation dimension
        model: Judge model to use
        max_workers: Maximum parallel workers

    Returns:
        List of comparison dictionaries
    """
    print(f"Generating {num_comparisons} pairwise comparisons for '{dimension}'...")
    print(f"Using judge model: {model}")
    print(f"Parallel workers: {max_workers}")

    # Generate query-response triplets
    tasks = []
    for i in range(num_comparisons):
        query = SAMPLE_QUERIES[i % len(SAMPLE_QUERIES)]

        # Alternate between different model pairs for variety
        if i % 3 == 0:
            response_a = get_model_a_response(query)
            response_b = get_model_b_response(query)
        elif i % 3 == 1:
            response_a = get_model_b_response(query)
            response_b = get_model_c_response(query)
        else:
            response_a = get_model_a_response(query)
            response_b = get_model_c_response(query)

        tasks.append((query, response_a, response_b))

    # Execute in parallel
    comparisons = []
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {
            executor.submit(
                generate_single_comparison,
                query, resp_a, resp_b, dimension, model
            ): (query, resp_a, resp_b)
            for query, resp_a, resp_b in tasks
        }

        # Collect results with progress bar
        for future in tqdm(as_completed(futures), total=len(futures), desc="Generating"):
            try:
                comparison = future.result()
                comparisons.append(comparison)
            except Exception as e:
                print(f"Error generating comparison: {e}")

    return comparisons


# ============================================================================
# CLI Interface
# ============================================================================

def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Generate pairwise comparison datasets for LLM evaluation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate 100 comparisons for helpfulness
  python generate_pairwise_comparisons.py --num_comparisons 100 --dimension helpfulness

  # Use GPT-4o for judging
  python generate_pairwise_comparisons.py --num_comparisons 50 --model gpt-4o

  # Generate multi-dimensional dataset
  python generate_pairwise_comparisons.py --num_comparisons 30 --dimension correctness
        """
    )

    parser.add_argument(
        "--num_comparisons",
        type=int,
        default=100,
        help="Number of pairwise comparisons to generate (default: 100)"
    )

    parser.add_argument(
        "--dimension",
        type=str,
        default="helpfulness",
        choices=["helpfulness", "correctness", "conciseness", "safety"],
        help="Evaluation dimension (default: helpfulness)"
    )

    parser.add_argument(
        "--model",
        type=str,
        default="gpt-4o-mini",
        help="Judge model to use (default: gpt-4o-mini)"
    )

    parser.add_argument(
        "--output",
        type=str,
        default=None,
        help="Output JSON file path (default: lesson-11/data/pairwise_comparisons.json)"
    )

    parser.add_argument(
        "--max_workers",
        type=int,
        default=5,
        help="Maximum parallel workers (default: 5)"
    )

    args = parser.parse_args()

    # Validate environment
    if not os.getenv("OPENAI_API_KEY"):
        print("Error: OPENAI_API_KEY environment variable not set.")
        print("Please set your OpenAI API key: export OPENAI_API_KEY='your-key-here'")
        sys.exit(1)

    # Determine output path
    if args.output is None:
        output_path = Path(__file__).parent.parent / "data" / "pairwise_comparisons.json"
    else:
        output_path = Path(args.output)

    # Create output directory if it doesn't exist
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Generate comparisons
    comparisons = generate_comparisons_parallel(
        num_comparisons=args.num_comparisons,
        dimension=args.dimension,
        model=args.model,
        max_workers=args.max_workers
    )

    # Save to JSON
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(comparisons, f, indent=2, ensure_ascii=False)

    print(f"\n✅ Generated {len(comparisons)} comparisons")
    print(f"📁 Saved to: {output_path}")

    # Print statistics
    if comparisons:
        winner_a = sum(1 for c in comparisons if c['winner'] == 'A')
        winner_b = sum(1 for c in comparisons if c['winner'] == 'B')
        print(f"\n📊 Statistics:")
        print(f"   Winner A: {winner_a} ({winner_a/len(comparisons)*100:.1f}%)")
        print(f"   Winner B: {winner_b} ({winner_b/len(comparisons)*100:.1f}%)")
        print(f"   Dimension: {args.dimension}")
        print(f"   Judge Model: {args.model}")


if __name__ == "__main__":
    main()
