"""Evaluate V5-ToT classifier on golden set failures with tracing.

This script runs the V5-ToT Tree-of-Thought classifier on the same 50 failures
used for V4 evaluation, capturing branch analysis for comparison.
"""

import asyncio
import csv
import json
import logging
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple

# Disable LLM caching to avoid missing dependency errors
os.environ["LLM_CACHE_TYPE"] = "disabled"

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from pydantic import BaseModel, Field

from utils.llm_service import get_default_service
from utils.prompt_service import render_prompt
from backend.phases.classify_v5_tot import (
    CategoryResultV5ToT,
    BranchAResult,
    BranchBResult,
    BranchCResult,
    SynthesisResult,
    V5_TOT_MODEL,
    extract_branch_summary,
    check_branch_conflict,
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def _identify_category_v5_tot_trace(
    description: str,
    model: str | None = None
) -> Tuple[CategoryResultV5ToT, Dict[str, Any]]:
    """Identify category using V5-ToT prompt with tracing.

    Args:
        description: The dispute description to classify.
        model: Optional model override.

    Returns:
        Tuple of (CategoryResultV5ToT, trace_dict)
    """
    service = get_default_service()
    prompt = render_prompt(
        "DisputeClassifier_identify_category_v5_tot.j2",
        description=description
    )

    target_model = model or V5_TOT_MODEL

    # Use complete() to get raw response for tracing
    completion = await service.complete(
        messages=[{"role": "user", "content": prompt}],
        model=target_model,
        temperature=0.0
    )

    # Parse manually with robust JSON extraction
    try:
        content = completion.content.strip()

        # Remove markdown code blocks if present
        if "```json" in content:
            content = content.split("```json")[1]
        if "```" in content:
            content = content.split("```")[0]
        content = content.strip()

        # Try to find JSON object boundaries
        if not content.startswith("{"):
            start = content.find("{")
            if start != -1:
                content = content[start:]
        if not content.endswith("}"):
            end = content.rfind("}")
            if end != -1:
                content = content[:end + 1]

        # Parse JSON first to check structure
        import json as json_lib
        parsed = json_lib.loads(content)

        # Add missing fields with defaults if needed
        if "confidence_rationale" not in parsed:
            parsed["confidence_rationale"] = "Confidence based on branch analysis"

        # Fix invalid branch_b values
        if parsed.get("branch_b", {}).get("complaint_type") not in ["amount", "quality", "processing", "unspecified"]:
            original = parsed["branch_b"]["complaint_type"]
            # Map common mistakes
            if "not_received" in original or "not received" in original.lower():
                parsed["branch_b"]["complaint_type"] = "processing"
            elif "canceled" in original or "subscription" in original:
                parsed["branch_b"]["complaint_type"] = "processing"
            else:
                parsed["branch_b"]["complaint_type"] = "unspecified"
            logger.warning(f"Fixed invalid branch_b complaint_type: {original} -> {parsed['branch_b']['complaint_type']}")

        result = CategoryResultV5ToT.model_validate(parsed)
    except Exception as e:
        logger.error(f"Failed to parse V5-ToT result: {e}")
        logger.error(f"Raw content: {completion.content[:500]}...")
        raise ValueError(f"Failed to parse output: {content[:200]}") from e

    trace = {
        "step": "identify_category_v5_tot",
        "prompt": prompt,
        "llm_response": completion.content,
        "parsed_output": result.model_dump(),
        "model": target_model
    }

    return result, trace


async def evaluate_v5_tot_trace(
    max_cases: int = 50,
    model: str | None = None
) -> None:
    """Run V5-ToT evaluation on golden set failures.

    Args:
        max_cases: Maximum number of cases to evaluate.
        model: Optional model override.
    """
    # Paths
    results_path = project_root / "qualitative" / "phase1" / "natural_language_results.csv"
    output_json_path = project_root / "qualitative" / "phase1" / "natural_language_trace_results_v5_tot.json"

    # Load failures from CSV
    failures: List[Dict[str, str]] = []
    try:
        with open(results_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row["status"] == "FAIL":
                    failures.append(row)
    except FileNotFoundError:
        logger.error(f"Could not find results file at {results_path}")
        return

    # Select cases (same as V4)
    selected_cases = failures[:max_cases]
    trace_results: List[Dict[str, Any]] = []

    print(f"Testing {len(selected_cases)} failed cases with V5-ToT prompt and capturing traces...\n")
    print(f"Model: {model or V5_TOT_MODEL}\n")

    for i, case in enumerate(selected_cases):
        description = case["description"]
        expected = case["expected_category"]
        dispute_id = case["dispute_id"]

        try:
            result, trace = await _identify_category_v5_tot_trace(description, model=model)
            v5_prediction = result.category

            is_pass = v5_prediction == expected
            status = "PASS" if is_pass else "FAIL"

            # Extract branch summary for reporting
            branch_summary = extract_branch_summary(result)
            branch_conflict = check_branch_conflict(result)

            trace_entry = {
                "case": case,
                "result": {
                    "category": v5_prediction,
                    "reasoning": result.synthesis.reasoning,
                    "confidence": result.confidence,
                    "confidence_rationale": result.confidence_rationale,
                },
                "branch_analysis": {
                    "branch_a": {
                        "conclusion": result.branch_a.conclusion,
                        "evidence_for": result.branch_a.evidence_for_acknowledgment,
                        "evidence_against": result.branch_a.evidence_against_acknowledgment,
                    },
                    "branch_b": {
                        "complaint_type": result.branch_b.complaint_type,
                        "evidence": result.branch_b.evidence,
                    },
                    "branch_c": {
                        "persona": result.branch_c.persona,
                        "evidence": result.branch_c.evidence,
                    },
                    "synthesis": {
                        "branch_agreement": result.synthesis.branch_agreement,
                        "priority_rule_applied": result.synthesis.priority_rule_applied,
                    },
                    "conflict": branch_conflict,
                },
                "trace": {
                    "steps": [trace]
                },
                "status": status,
                "model": model or V5_TOT_MODEL,
            }
            trace_results.append(trace_entry)

            # Progress output
            conflict_indicator = " [CONFLICT]" if branch_conflict else ""
            print(
                f"[{i+1}/{len(selected_cases)}] {dispute_id}: {status} "
                f"(Exp: {expected}, Got: {v5_prediction}) "
                f"[A:{result.branch_a.conclusion}, B:{result.branch_b.complaint_type}, C:{result.branch_c.persona}]"
                f"{conflict_indicator}"
            )

        except Exception as e:
            logger.error(f"Error processing {dispute_id}: {e}")
            # Record failure in results
            trace_results.append({
                "case": case,
                "result": {
                    "category": "ERROR",
                    "reasoning": str(e),
                    "confidence": 0.0,
                    "confidence_rationale": "Processing error",
                },
                "branch_analysis": None,
                "trace": {"steps": []},
                "status": "ERROR",
                "model": model or V5_TOT_MODEL,
            })

    # Save to JSON
    with open(output_json_path, "w") as f:
        json.dump(trace_results, f, indent=2)

    # Calculate stats
    passed = sum(1 for r in trace_results if r["status"] == "PASS")
    total = len(trace_results)
    errors = sum(1 for r in trace_results if r["status"] == "ERROR")

    # Calculate per-persona stats
    persona_stats: Dict[str, Dict[str, int]] = {}
    for r in trace_results:
        if r["status"] == "ERROR":
            continue
        persona = r["case"].get("variation_type", "unknown")
        if persona not in persona_stats:
            persona_stats[persona] = {"pass": 0, "total": 0}
        persona_stats[persona]["total"] += 1
        if r["status"] == "PASS":
            persona_stats[persona]["pass"] += 1

    # Calculate branch conflict stats
    conflicts_resolved = sum(
        1 for r in trace_results
        if r.get("branch_analysis") and r["branch_analysis"].get("conflict") and r["status"] == "PASS"
    )
    total_conflicts = sum(
        1 for r in trace_results
        if r.get("branch_analysis") and r["branch_analysis"].get("conflict")
    )

    print("\n" + "=" * 60)
    print("V5-ToT Evaluation Complete")
    print("=" * 60)
    print(f"\nOverall: {passed}/{total} ({passed/total*100:.1f}%)")
    if errors > 0:
        print(f"Errors: {errors}")
    print(f"\nPerformance by Persona:")
    for persona, stats in sorted(persona_stats.items()):
        rate = stats["pass"] / stats["total"] * 100 if stats["total"] > 0 else 0
        print(f"  {persona.title()}: {rate:.1f}% ({stats['pass']}/{stats['total']})")

    if total_conflicts > 0:
        print(f"\nBranch Conflicts: {total_conflicts} detected, {conflicts_resolved} resolved correctly")

    print(f"\nTrace results saved to {output_json_path}")
    print("\nRun generate_trace_report_v5_tot.py to generate HTML report.")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Evaluate V5-ToT classifier on golden set failures")
    parser.add_argument("--max-cases", type=int, default=50, help="Maximum cases to evaluate")
    parser.add_argument("--model", type=str, default=None, help="Model override")
    args = parser.parse_args()

    asyncio.run(evaluate_v5_tot_trace(max_cases=args.max_cases, model=args.model))
