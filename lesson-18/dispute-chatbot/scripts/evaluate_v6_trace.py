"""Evaluate V6 classifier on golden set v2 with tracing.

This script runs the V5-ToT Tree-of-Thought classifier on the same 20 cases
used in V5 evaluation, but uses golden_set_v2 as ground truth for expected categories.
"""

import asyncio
import json
import logging
import os
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple

# Disable LLM caching to avoid missing dependency errors
os.environ["LLM_CACHE_TYPE"] = "disabled"

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from utils.llm_service import get_default_service
from utils.prompt_service import render_prompt
from backend.phases.classify_v5_tot import (
    CategoryResultV5ToT,
    V5_TOT_MODEL,
    extract_branch_summary,
    check_branch_conflict,
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def _repair_json(content: str) -> str:
    """Repair common LLM JSON errors.

    Handles:
    - Inline comments: "text" - explanation → "text"
    - Double-dash comments: "text" -- note → "text"
    - Trailing commas: ["item",] → ["item"]
    - Line comments: // comment

    Args:
        content: Raw JSON string from LLM output.

    Returns:
        Repaired JSON string.
    """
    if not isinstance(content, str):
        raise TypeError("content must be a string")

    # Step 1: Remove inline comments in arrays: "value" - explanation (before comma/bracket)
    # Pattern matches: "quoted text" followed by - or -- and explanation text until , or ]
    content = re.sub(
        r'("(?:[^"\\]|\\.)*")\s*-{1,2}\s*[^",\]\}]+(?=[,\]\}])',
        r'\1',
        content
    )

    # Step 2: Remove // line comments
    content = re.sub(r'//[^\n]*', '', content)

    # Step 3: Remove # line comments (Python-style)
    content = re.sub(r'#[^\n]*', '', content)

    # Step 4: Fix trailing commas before closing brackets
    content = re.sub(r',(\s*[\]\}])', r'\1', content)

    # Step 5: Remove extra whitespace/newlines
    content = re.sub(r'\n\s*\n', '\n', content)

    return content.strip()


async def _identify_category_v5_tot_trace(
    description: str,
    model: str = None
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
        original_content = content  # Keep original for error reporting

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

        # Apply JSON repair for inline comments and other LLM artifacts
        content = _repair_json(content)

        # Parse JSON first to check structure
        import json as json_lib
        try:
            parsed = json_lib.loads(content)
        except json.JSONDecodeError as first_error:
            # If standard repair failed, try json-repair library as fallback
            logger.warning(f"Standard JSON repair failed, trying json-repair: {first_error}")
            try:
                from json_repair import repair_json
                repaired = repair_json(content)
                parsed = json_lib.loads(repaired)
                logger.info("JSON successfully repaired with json-repair library")
            except ImportError:
                logger.warning("json-repair not installed, cannot use fallback repair")
                raise first_error
            except Exception as repair_error:
                logger.error(f"json-repair also failed: {repair_error}")
                raise first_error

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


async def evaluate_v6_trace(
    model: str = None
) -> None:
    """Run V6 evaluation using golden set v2 as ground truth.

    Args:
        model: Optional model override.
    """
    # Paths
    v5_results_path = project_root / "qualitative" / "phase1" / "natural_language_trace_results_v5_tot.json"
    golden_v2_path = project_root / "synthetic_data" / "phase1" / "golden_set" / "natural_language_classification_v2.json"
    output_json_path = project_root / "qualitative" / "phase1" / "natural_language_trace_results_v6.json"

    # Load V5 results to get the 20 dispute IDs
    try:
        with open(v5_results_path, "r", encoding="utf-8") as f:
            v5_results = json.load(f)
    except FileNotFoundError:
        logger.error(f"Could not find V5 results file at {v5_results_path}")
        return

    # Load golden set v2 for ground truth
    try:
        with open(golden_v2_path, "r", encoding="utf-8") as f:
            golden_v2 = json.load(f)
    except FileNotFoundError:
        logger.error(f"Could not find golden set v2 at {golden_v2_path}")
        return

    # Create lookup by dispute_id
    golden_v2_lookup = {item["dispute_id"]: item for item in golden_v2}

    # Get the 20 cases from V5 results
    v5_dispute_ids = [r["case"]["dispute_id"] for r in v5_results]

    trace_results: List[Dict[str, Any]] = []

    print(f"Testing {len(v5_dispute_ids)} cases with V5-ToT prompt using Golden Set V2 ground truth...\n")
    print(f"Model: {model or V5_TOT_MODEL}\n")

    for i, dispute_id in enumerate(v5_dispute_ids):
        # Get ground truth from golden v2
        golden_case = golden_v2_lookup.get(dispute_id)
        if not golden_case:
            logger.error(f"Dispute ID {dispute_id} not found in golden set v2")
            continue

        description = golden_case["description"]
        expected = golden_case["category"]  # Ground truth from golden v2
        variation_type = golden_case.get("variation_type", "unknown")

        # Build case info matching V5 format
        case_info = {
            "dispute_id": dispute_id,
            "variation_type": variation_type,
            "expected_category": expected,
            "description": description,
            "network": golden_case.get("network", "unknown"),
            "true_reason_code": golden_case.get("true_reason_code", "unknown"),
        }

        try:
            result, trace = await _identify_category_v5_tot_trace(description, model=model)
            v6_prediction = result.category

            is_pass = v6_prediction == expected
            status = "PASS" if is_pass else "FAIL"

            # Extract branch summary for reporting
            branch_conflict = check_branch_conflict(result)

            trace_entry = {
                "case": case_info,
                "result": {
                    "category": v6_prediction,
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
                f"[{i+1}/{len(v5_dispute_ids)}] {dispute_id}: {status} "
                f"(Exp: {expected}, Got: {v6_prediction}) "
                f"[A:{result.branch_a.conclusion}, B:{result.branch_b.complaint_type}, C:{result.branch_c.persona}]"
                f"{conflict_indicator}"
            )

        except Exception as e:
            logger.error(f"Error processing {dispute_id}: {e}")
            # Record failure in results
            trace_results.append({
                "case": case_info,
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
    print("V6 Evaluation Complete (Golden Set V2 Ground Truth)")
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
    print("\nRun generate_trace_report_v6.py to generate HTML report.")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Evaluate V6 classifier on golden set v2")
    parser.add_argument("--model", type=str, default=None, help="Model override")
    args = parser.parse_args()

    asyncio.run(evaluate_v6_trace(model=args.model))
