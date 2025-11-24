"""Generate RAG Evaluation Test Suite with 500 labeled cases.

This script creates lesson-13/data/rag_evaluation_suite.json with:
- 200 Bhagavad Gita Q&A samples (stratified by chapter)
- 200 recipe samples from HW4 corpus
- 100 adversarial cases for hallucination detection

Each test case includes labels for:
- is_attributed: Whether answer properly cites context
- is_context_relevant: Whether context matches query
- context_utilization: USED/PARTIAL/IGNORED
- hallucination_type: NONE/INTRINSIC/EXTRINSIC
"""

import csv
import json
import random
from pathlib import Path
from typing import Any


def load_gita_qa_samples(csv_path: Path, n_samples: int = 200) -> list[dict[str, Any]]:
    """Load stratified Gita Q&A samples across all chapters.

    Args:
        csv_path: Path to english.csv with Gita Q&A pairs
        n_samples: Number of samples to extract (default: 200)

    Returns:
        List of test cases with query, context, answer, and labels
    """
    if not csv_path.exists():
        raise FileNotFoundError(f"Gita Q&A file not found: {csv_path}")

    # Load all Q&A pairs
    with open(csv_path, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        all_qa = list(reader)

    # Stratify by chapter (18 chapters in Bhagavad Gita)
    chapter_buckets: dict[int, list[dict]] = {}
    for qa in all_qa:
        chapter = int(qa["chapter_no"])
        if chapter not in chapter_buckets:
            chapter_buckets[chapter] = []
        chapter_buckets[chapter].append(qa)

    # Sample proportionally from each chapter
    samples_per_chapter = n_samples // len(chapter_buckets)
    remainder = n_samples % len(chapter_buckets)

    samples = []
    for chapter_no in sorted(chapter_buckets.keys()):
        chapter_qa = chapter_buckets[chapter_no]
        n = samples_per_chapter + (1 if remainder > 0 else 0)
        remainder -= 1

        selected = random.sample(chapter_qa, min(n, len(chapter_qa)))
        for qa in selected:
            # Create test case with GROUND TRUTH labels
            # These are "perfect" RAG responses where attribution is correct
            test_case = {
                "id": f"gita_{qa['chapter_no']}_{qa['verse_no']}_{len(samples)}",
                "source": "bhagavad_gita",
                "query": qa["question"],
                "context": [
                    f"Bhagavad Gita, Chapter {qa['chapter_no']}, Verse {qa['verse_no']}: {qa['answer']}"
                ],
                "answer": qa["answer"],
                "labels": {
                    "is_attributed": True,  # Answer matches context exactly
                    "is_context_relevant": True,  # Context directly answers query
                    "context_utilization": "USED",  # LLM uses the context
                    "hallucination_type": "NONE",  # No hallucinations
                },
                "metadata": {
                    "chapter": int(qa["chapter_no"]),
                    "verse": int(qa["verse_no"]),
                    "difficulty": "medium",
                },
            }
            samples.append(test_case)

    return samples[:n_samples]


def load_recipe_samples(recipes_path: Path, n_samples: int = 200) -> list[dict[str, Any]]:
    """Load recipe samples from HW4 corpus.

    Args:
        recipes_path: Path to processed_recipes.json from HW4
        n_samples: Number of samples to extract (default: 200)

    Returns:
        List of test cases with recipe queries and contexts
    """
    if not recipes_path.exists():
        raise FileNotFoundError(f"Recipe file not found: {recipes_path}")

    with open(recipes_path, "r", encoding="utf-8") as f:
        recipes = json.load(f)

    # Sample recipes randomly
    selected_recipes = random.sample(recipes, min(n_samples, len(recipes)))

    samples = []
    for i, recipe in enumerate(selected_recipes):
        # Generate query variations
        query_templates = [
            f"How do I make {recipe.get('title', 'this dish')}?",
            f"What are the ingredients for {recipe.get('title', 'this recipe')}?",
            f"Can you give me a recipe for {recipe.get('title', 'this')}?",
            f"What is the recipe for {recipe.get('title', 'this dish')}?",
        ]
        query = random.choice(query_templates)

        # Build context from recipe data
        ingredients = recipe.get("ingredients", [])
        directions = recipe.get("directions", [])

        context_text = f"Recipe: {recipe.get('title', 'Unknown')}\n\n"
        context_text += "Ingredients:\n" + "\n".join(f"- {ing}" for ing in ingredients[:5])
        context_text += "\n\nDirections:\n" + "\n".join(f"{i+1}. {d}" for i, d in enumerate(directions[:3]))

        # Generate answer that uses the context
        answer = f"To make {recipe.get('title', 'this dish')}, you'll need: "
        answer += ", ".join(ingredients[:3])
        answer += f". {directions[0] if directions else 'Follow the recipe instructions.'}"

        test_case = {
            "id": f"recipe_{i}",
            "source": "recipes",
            "query": query,
            "context": [context_text],
            "answer": answer,
            "labels": {
                "is_attributed": True,  # Answer uses recipe context
                "is_context_relevant": True,  # Recipe matches query
                "context_utilization": "USED",  # LLM uses recipe data
                "hallucination_type": "NONE",  # No fabricated ingredients
            },
            "metadata": {
                "recipe_id": recipe.get("id", i),
                "category": recipe.get("category", "unknown"),
                "difficulty": "easy",
            },
        }
        samples.append(test_case)

    return samples


def generate_adversarial_cases(n_samples: int = 100) -> list[dict[str, Any]]:
    """Generate adversarial test cases for hallucination detection.

    Creates 100 cases with deliberate attribution failures:
    - 40 intrinsic hallucinations (contradicts context)
    - 40 extrinsic hallucinations (not in context)
    - 20 context irrelevance cases

    Args:
        n_samples: Number of adversarial cases (default: 100)

    Returns:
        List of adversarial test cases with failure labels
    """
    adversarial = []

    # Pattern 1: Intrinsic Hallucinations (40 cases)
    intrinsic_templates = [
        {
            "query": "What is the main teaching of the Bhagavad Gita?",
            "context": ["The Bhagavad Gita teaches dharma (duty), karma (action), and moksha (liberation)."],
            "answer": "The Bhagavad Gita teaches that one should avoid all duties and focus on pleasure.",
            "labels": {
                "is_attributed": False,
                "is_context_relevant": True,
                "context_utilization": "IGNORED",
                "hallucination_type": "INTRINSIC",  # Contradicts context
            },
        },
        {
            "query": "What temperature should I bake the cake at?",
            "context": ["Preheat oven to 350°F (175°C). Bake for 30 minutes."],
            "answer": "Bake the cake at 450°F for 10 minutes.",
            "labels": {
                "is_attributed": False,
                "is_context_relevant": True,
                "context_utilization": "IGNORED",
                "hallucination_type": "INTRINSIC",  # Wrong temperature
            },
        },
    ]

    for i in range(40):
        template = intrinsic_templates[i % len(intrinsic_templates)]
        case = {
            "id": f"adversarial_intrinsic_{i}",
            "source": "adversarial",
            **template,
            "metadata": {"adversarial_type": "intrinsic_hallucination", "difficulty": "hard"},
        }
        adversarial.append(case)

    # Pattern 2: Extrinsic Hallucinations (40 cases)
    extrinsic_templates = [
        {
            "query": "Who was Arjuna's teacher?",
            "context": ["Arjuna was a great warrior in the Mahabharata."],
            "answer": "Arjuna's teacher was Dronacharya, and he studied for 12 years in the forest.",
            "labels": {
                "is_attributed": False,
                "is_context_relevant": True,
                "context_utilization": "PARTIAL",
                "hallucination_type": "EXTRINSIC",  # Extra info not in context
            },
        },
        {
            "query": "What ingredients do I need for chocolate chip cookies?",
            "context": ["Chocolate chip cookies are a popular dessert."],
            "answer": "You need flour, sugar, butter, eggs, vanilla extract, and chocolate chips.",
            "labels": {
                "is_attributed": False,
                "is_context_relevant": True,
                "context_utilization": "IGNORED",
                "hallucination_type": "EXTRINSIC",  # Ingredients not in context
            },
        },
    ]

    for i in range(40):
        template = extrinsic_templates[i % len(extrinsic_templates)]
        case = {
            "id": f"adversarial_extrinsic_{i}",
            "source": "adversarial",
            **template,
            "metadata": {"adversarial_type": "extrinsic_hallucination", "difficulty": "medium"},
        }
        adversarial.append(case)

    # Pattern 3: Context Irrelevance (20 cases)
    irrelevant_templates = [
        {
            "query": "What is the capital of France?",
            "context": ["The Bhagavad Gita is a 700-verse Hindu scripture."],
            "answer": "Paris is the capital of France.",
            "labels": {
                "is_attributed": False,
                "is_context_relevant": False,  # Context doesn't match query
                "context_utilization": "IGNORED",
                "hallucination_type": "EXTRINSIC",  # Correct answer but not from context
            },
        },
        {
            "query": "How do I fix a flat tire?",
            "context": ["Chocolate cake requires flour, eggs, sugar, cocoa powder, and butter."],
            "answer": "Remove the wheel, patch or replace the inner tube, and re-inflate.",
            "labels": {
                "is_attributed": False,
                "is_context_relevant": False,  # Recipe context for car repair query
                "context_utilization": "IGNORED",
                "hallucination_type": "EXTRINSIC",
            },
        },
    ]

    for i in range(20):
        template = irrelevant_templates[i % len(irrelevant_templates)]
        case = {
            "id": f"adversarial_irrelevant_{i}",
            "source": "adversarial",
            **template,
            "metadata": {"adversarial_type": "context_irrelevance", "difficulty": "easy"},
        }
        adversarial.append(case)

    return adversarial


def main() -> None:
    """Generate complete RAG evaluation test suite."""
    # Set random seed for reproducibility
    random.seed(42)

    # Define paths
    base_dir = Path(__file__).parent.parent
    gita_csv = base_dir / "Gita" / "Bhagavad-Gita-QA" / "English" / "english.csv"
    recipes_json = base_dir / "homeworks" / "hw4" / "data" / "processed_recipes.json"
    output_json = base_dir / "lesson-13" / "data" / "rag_evaluation_suite.json"

    print("🔄 Generating RAG Evaluation Test Suite...")
    print(f"   Gita Q&A source: {gita_csv}")
    print(f"   Recipe source: {recipes_json}")
    print(f"   Output: {output_json}\n")

    # Generate test cases
    print("📖 Extracting 200 Gita Q&A samples (stratified by chapter)...")
    gita_samples = load_gita_qa_samples(gita_csv, n_samples=200)
    print(f"   ✅ Generated {len(gita_samples)} Gita test cases\n")

    print("🍳 Extracting 200 recipe samples...")
    recipe_samples = load_recipe_samples(recipes_json, n_samples=200)
    print(f"   ✅ Generated {len(recipe_samples)} recipe test cases\n")

    print("⚠️  Generating 100 adversarial test cases...")
    adversarial_samples = generate_adversarial_cases(n_samples=100)
    print(f"   ✅ Generated {len(adversarial_samples)} adversarial cases\n")

    # Combine all test cases
    all_test_cases = gita_samples + recipe_samples + adversarial_samples

    # Create test suite metadata
    test_suite = {
        "version": "1.0",
        "created": "2025-11-11",
        "description": "RAG evaluation test suite for Lesson 13 - Attribution & Hallucination Detection",
        "statistics": {
            "total_cases": len(all_test_cases),
            "gita_samples": len(gita_samples),
            "recipe_samples": len(recipe_samples),
            "adversarial_samples": len(adversarial_samples),
            "attribution_pass": sum(1 for tc in all_test_cases if tc["labels"]["is_attributed"]),
            "attribution_fail": sum(1 for tc in all_test_cases if not tc["labels"]["is_attributed"]),
            "hallucination_none": sum(
                1 for tc in all_test_cases if tc["labels"]["hallucination_type"] == "NONE"
            ),
            "hallucination_intrinsic": sum(
                1 for tc in all_test_cases if tc["labels"]["hallucination_type"] == "INTRINSIC"
            ),
            "hallucination_extrinsic": sum(
                1 for tc in all_test_cases if tc["labels"]["hallucination_type"] == "EXTRINSIC"
            ),
        },
        "test_cases": all_test_cases,
    }

    # Save to JSON
    output_json.parent.mkdir(parents=True, exist_ok=True)
    with open(output_json, "w", encoding="utf-8") as f:
        json.dump(test_suite, f, indent=2, ensure_ascii=False)

    print(f"✅ Test suite saved to {output_json}")
    print("\n📊 Statistics:")
    print(f"   Total cases: {test_suite['statistics']['total_cases']}")
    print(f"   Attribution PASS: {test_suite['statistics']['attribution_pass']}")
    print(f"   Attribution FAIL: {test_suite['statistics']['attribution_fail']}")
    print(f"   No Hallucination: {test_suite['statistics']['hallucination_none']}")
    print(f"   Intrinsic Hallucination: {test_suite['statistics']['hallucination_intrinsic']}")
    print(f"   Extrinsic Hallucination: {test_suite['statistics']['hallucination_extrinsic']}")


if __name__ == "__main__":
    main()
