"""Evaluate V8-RAG classifier on golden set v2 with tracing.

This script runs the V8-RAG classifier on the golden set v2 cases.
"""

import asyncio
import json
import logging
import os
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple, Optional

# Disable LLM caching to avoid missing dependency errors
os.environ["LLM_CACHE_TYPE"] = "disabled"

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from utils.llm_service import get_default_service
from utils.prompt_service import render_prompt
from backend.phases.classify_v8_rag import (
    CategoryResultV8Rag,
    V8_RAG_MODEL,
    extract_branch_summary,
    check_branch_conflict,
    get_rag_retriever
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def _repair_json(content: str) -> str:
    """Repair common LLM JSON errors."""
    if not isinstance(content, str):
        raise TypeError("content must be a string")

    content = re.sub(r'("(?:[^"\\]|\\.)*")\s*-{1,2}\s*[^",\]\}]+(?=[,\]\}])', r'\1', content)
    content = re.sub(r'//[^\n]*', '', content)
    content = re.sub(r'#[^\n]*', '', content)
    content = re.sub(r',(\s*[\]\}])', r'\1', content)
    content = re.sub(r'\n\s*\n', '\n', content)

    return content.strip()


async def _identify_category_v8_rag_trace(
    description: str,
    model: str = None
) -> Tuple[CategoryResultV8Rag, Dict[str, Any]]:
    """Identify category using V8-RAG prompt with tracing."""
    service = get_default_service()
    
    # Retrieve examples for prompt rendering
    examples = []
    retriever = get_rag_retriever()
    if retriever:
        try:
            matches = retriever.retrieve_similar(description, k=3, threshold=0.4)
            examples = matches
        except Exception:
            pass
            
    prompt = render_prompt(
        "DisputeClassifier_identify_category_v8_rag.j2",
        description=description,
        examples=examples
    )

    target_model = model or V8_RAG_MODEL

    # Use complete() to get raw response for tracing
    completion = await service.complete(
        messages=[{"role": "user", "content": prompt}],
        model=target_model,
        temperature=0.0
    )

    try:
        content = completion.content.strip()
        
        if "```json" in content:
            content = content.split("```json")[1]
        if "```" in content:
            content = content.split("```")[0]
        content = content.strip()

        if not content.startswith("{"):
            start = content.find("{")
            if start != -1: content = content[start:]
        if not content.endswith("}"):
            end = content.rfind("}")
            if end != -1: content = content[:end + 1]

        content = _repair_json(content)

        import json as json_lib
        try:
            parsed = json_lib.loads(content)
        except json.JSONDecodeError as first_error:
            try:
                from json_repair import repair_json
                repaired = repair_json(content)
                parsed = json_lib.loads(repaired)
            except ImportError:
                raise first_error
            except Exception:
                raise first_error

        # V8 fields defaults
        if "confidence_rationale" not in parsed:
            parsed["confidence_rationale"] = "Confidence based on branch analysis"
        if "reason_code_group" not in parsed:
            parsed["reason_code_group"] = "cardholder_disputes" # fallback

        result = CategoryResultV8Rag.model_validate(parsed)
    except Exception as e:
        logger.error(f"Failed to parse V8-RAG result: {e}")
        raise ValueError(f"Failed to parse output: {content[:200]}") from e

    trace = {
        "step": "identify_category_v8_rag",
        "prompt": prompt,
        "llm_response": completion.content,
        "parsed_output": result.model_dump(),
        "model": target_model,
        "retrieved_examples": examples
    }

    return result, trace


async def evaluate_v8_rag_trace(
    model: str = None,
    limit: int = 20 # Limit to 20 for quick iteration like V6 trace
) -> None:
    """Run V8-RAG evaluation using golden set v2."""
    
    # We'll use the first N from golden set v2 or same subset as V5/V6 results?
    # V6 trace used a subset based on V5 results. Let's just use the first N items from golden set v2.
    
    golden_v2_path = project_root / "synthetic_data" / "phase1" / "golden_set" / "natural_language_classification_v2.json"
    output_json_path = project_root / "qualitative" / "phase1" / "natural_language_trace_results_v8_rag.json"

    try:
        with open(golden_v2_path, "r", encoding="utf-8") as f:
            golden_v2 = json.load(f)
    except FileNotFoundError:
        logger.error(f"Could not find golden set v2 at {golden_v2_path}")
        return

    # Use first N or specific subset. For now, first 20.
    test_cases = golden_v2[:limit]

    trace_results: List[Dict[str, Any]] = []

    print(f"Testing {len(test_cases)} cases with V8-RAG prompt...\n")
    print(f"Model: {model or V8_RAG_MODEL}\n")

    for i, case in enumerate(test_cases):
        dispute_id = case["dispute_id"]
        description = case["description"]
        expected = case["category"]
        variation_type = case.get("variation_type", "unknown")

        case_info = {
            "dispute_id": dispute_id,
            "variation_type": variation_type,
            "expected_category": expected,
            "description": description,
            "network": case.get("network", "unknown"),
            "true_reason_code": case.get("true_reason_code", "unknown"),
        }

        # Normalize expected category to match V8 schema
        aliases = {
            "fraud": "fraudulent",
            "unauthorized": "fraudulent",
            "authorization": "general",
            "processing_errors": "general",
            "processing_error": "general",
            "processing": "general",
            "duplicate_charge": "duplicate",
            "billing_error": "general",
            "discrepancy": "general",
            "subscription_cancelled": "subscription_canceled",
            "refund_not_processed": "credit_not_processed",
            "refund_not_received": "credit_not_processed",
            "product_not_as_described": "product_unacceptable",
            "unknown": "unrecognized"
        }
        expected_norm = expected.lower().strip().replace(" ", "_").replace("-", "_")
        expected_norm = aliases.get(expected_norm, expected_norm)

        try:
            result, trace = await _identify_category_v8_rag_trace(description, model=model)
            prediction = result.category

            is_pass = prediction == expected_norm
            status = "PASS" if is_pass else "FAIL"

            branch_conflict = check_branch_conflict(result)

            trace_entry = {
                "case": case_info,
                "result": {
                    "category": prediction,
                    "reason_code_group": result.reason_code_group,
                    "reasoning": result.synthesis.reasoning,
                    "confidence": result.confidence,
                },
                "branch_analysis": extract_branch_summary(result),
                "trace": {"steps": [trace]},
                "status": status,
                "model": model or V8_RAG_MODEL,
            }
            trace_results.append(trace_entry)

            conflict_indicator = " [CONFLICT]" if branch_conflict else ""
            print(
                f"[{i+1}/{len(test_cases)}] {dispute_id}: {status} "
                f"(Exp: {expected}, Got: {prediction}) "
                f"[A:{result.branch_a.conclusion}, B:{result.branch_b.complaint_type}, C:{result.branch_c.persona}]"
                f"{conflict_indicator}"
            )

        except Exception as e:
            logger.error(f"Error processing {dispute_id}: {e}")
            trace_results.append({
                "case": case_info,
                "result": {"category": "ERROR", "reasoning": str(e)},
                "status": "ERROR",
                "model": model or V8_RAG_MODEL,
            })

    # Save results
    with open(output_json_path, "w") as f:
        json.dump(trace_results, f, indent=2)

    # Stats
    passed = sum(1 for r in trace_results if r["status"] == "PASS")
    total = len(trace_results)
    
    print("\n" + "=" * 60)
    print("V8-RAG Evaluation Complete")
    print("=" * 60)
    print(f"\nOverall: {passed}/{total} ({passed/total*100:.1f}%)")
    print(f"\nTrace results saved to {output_json_path}")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", type=str, default=None)
    parser.add_argument("--limit", type=int, default=20)
    args = parser.parse_args()

    asyncio.run(evaluate_v8_rag_trace(model=args.model, limit=args.limit))

