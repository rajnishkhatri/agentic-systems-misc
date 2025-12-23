"""Evaluate V6-MIPRO prompt on V5-ToT trace subset.

This script evaluates the MIPRO-optimized prompt (v6) on the specific 50 examples
used in the V5-ToT trace report, using the standard LLM service (no DSPy).
"""

import asyncio
import json
import logging
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from utils.llm_service import get_default_service
from utils.prompt_service import render_prompt
from backend.phases.classify_v5_tot import (
    CategoryResultV5ToT,
    extract_branch_summary,
    check_branch_conflict,
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Constants
V5_TRACE_PATH = project_root / "qualitative" / "phase1" / "natural_language_trace_results_v5_tot.json"
OUTPUT_PATH = project_root / "qualitative" / "phase1" / "natural_language_trace_results_v6_mipro.json"
V6_PROMPT_TEMPLATE = "DisputeClassifier_identify_category_v6_mipro.j2"
TARGET_MODEL = "openai/gpt-4o"  # Using GPT-4o for strong baseline comparison

async def _identify_category_v6_mipro(
    description: str,
    model: str = TARGET_MODEL
) -> Tuple[CategoryResultV5ToT, Dict[str, Any]]:
    """Identify category using V6-MIPRO prompt.

    Args:
        description: The dispute description to classify.
        model: Model to use.

    Returns:
        Tuple of (CategoryResultV5ToT, trace_dict)
    """
    service = get_default_service()
    prompt = render_prompt(
        V6_PROMPT_TEMPLATE,
        description=description
    )

    # Use complete() to get raw response for tracing
    # Using json_object response format to ensure valid JSON and increasing max_tokens to avoid truncation
    completion = await service.complete(
        messages=[{"role": "user", "content": prompt}],
        model=model,
        temperature=0.0,
        max_tokens=4096,
        response_format={"type": "json_object"}
    )

    # Parse manually with robust JSON extraction (similar to V5 evaluation)
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

        # Fix invalid branch_b values (common issue handling)
        if parsed.get("branch_b", {}).get("complaint_type") not in ["amount", "quality", "processing", "unspecified"]:
            original = parsed.get("branch_b", {}).get("complaint_type", "")
            if "not_received" in original or "not received" in original.lower():
                parsed["branch_b"]["complaint_type"] = "processing"
            elif "canceled" in original or "subscription" in original:
                parsed["branch_b"]["complaint_type"] = "processing"
            else:
                parsed["branch_b"]["complaint_type"] = "unspecified"
            logger.warning(f"Fixed invalid branch_b complaint_type: {original} -> {parsed['branch_b']['complaint_type']}")

        result = CategoryResultV5ToT.model_validate(parsed)
    except Exception as e:
        logger.error(f"Failed to parse V6-MIPRO result: {e}")
        logger.error(f"Raw content: {completion.content[:500]}...")
        # Return partial/error result if parsing fails completely? 
        # For evaluation, we want to capture the error.
        raise ValueError(f"Failed to parse output: {content[:200]}") from e

    trace = {
        "step": "identify_category_v6_mipro",
        "prompt": prompt,
        "llm_response": completion.content,
        "parsed_output": result.model_dump(),
        "model": model
    }

    return result, trace

async def evaluate_v6_mipro():
    """Run V6-MIPRO evaluation on the 50 cases from V5 trace."""
    if not V5_TRACE_PATH.exists():
        logger.error(f"V5 trace file not found at {V5_TRACE_PATH}")
        return

    # Load V5 cases
    print(f"Loading V5 trace data from {V5_TRACE_PATH}...")
    with open(V5_TRACE_PATH, "r") as f:
        v5_data = json.load(f)
    
    # Extract unique cases (should be 50)
    cases_to_run = []
    seen_ids = set()
    for entry in v5_data:
        # Check if entry has 'case' field (structure of trace results)
        case = entry.get("case")
        if not case:
            continue
            
        dispute_id = case.get("dispute_id")
        if dispute_id and dispute_id not in seen_ids:
            cases_to_run.append(case)
            seen_ids.add(dispute_id)
    
    print(f"Found {len(cases_to_run)} unique cases to evaluate.")
    
    trace_results = []
    
    for i, case in enumerate(cases_to_run):
        dispute_id = case["dispute_id"]
        description = case["description"]
        expected = case["expected_category"]
        
        print(f"Processing [{i+1}/{len(cases_to_run)}] {dispute_id}...")
        
        try:
            result, trace = await _identify_category_v6_mipro(description)
            prediction = result.category
            
            is_pass = prediction == expected
            status = "PASS" if is_pass else "FAIL"
            
            # Extract summary and checks
            branch_summary = extract_branch_summary(result)
            branch_conflict = check_branch_conflict(result)
            
            trace_entry = {
                "case": case,
                "result": {
                    "category": prediction,
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
                "model": TARGET_MODEL,
            }
            trace_results.append(trace_entry)
            
            print(f"  Result: {status} (Exp: {expected}, Got: {prediction})")
            
        except Exception as e:
            logger.error(f"Error processing {dispute_id}: {e}")
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
                "model": TARGET_MODEL,
            })

    # Save results
    print(f"Saving results to {OUTPUT_PATH}...")
    with open(OUTPUT_PATH, "w") as f:
        json.dump(trace_results, f, indent=2)
        
    # Simple summary
    passed = sum(1 for r in trace_results if r["status"] == "PASS")
    total = len(trace_results)
    print(f"V6-MIPRO Evaluation Complete. Accuracy: {passed}/{total} ({passed/total*100:.1f}%)")

if __name__ == "__main__":
    asyncio.run(evaluate_v6_mipro())

