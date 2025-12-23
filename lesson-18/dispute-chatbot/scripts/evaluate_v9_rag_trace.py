"""Evaluate V9-RAG classifier on golden set with tracing.

This script runs the V9-RAG classifier with enhanced observability:
- RAG metrics tracking
- Confidence calibration
- Precedent diversity checks
"""

import asyncio
import json
import logging
import os
import re
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# Disable TensorFlow to avoid Keras 3 compatibility issues
os.environ["USE_TF"] = "0"

# Mock torch._dynamo to prevent errors
class _MockDynamo:
    def is_compiling(self):
        return False
sys.modules["torch._dynamo"] = _MockDynamo()

# Disable LLM caching
os.environ["LLM_CACHE_TYPE"] = "disabled"

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from utils.llm_service import get_default_service
from utils.prompt_service import render_prompt
from backend.phases.classify_v9_rag import (
    CategoryResultV9Rag,
    CodeSelectionResult,
    RAGMetrics,
    V9_RAG_MODEL,
    RAG_TOP_K,
    RAG_SIMILARITY_THRESHOLD,
    RAG_HIGH_CONFIDENCE_THRESHOLD,
    extract_branch_summary,
    check_branch_conflict,
    build_rag_metrics,
    calibrate_confidence,
    check_precedent_diversity,
    get_rag_retriever_safe,
    _identify_network,
)
from backend.adapters.reason_code_catalog import get_reason_code_catalog

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


async def _identify_category_v9_rag_trace(
    description: str,
    model: str = None
) -> Tuple[CategoryResultV9Rag, Dict[str, Any], RAGMetrics, Dict[str, Any]]:
    """Identify category using V9-RAG prompt with tracing.

    Returns:
        Tuple of (CategoryResult, trace, RAGMetrics, diversity_info)
    """
    service = get_default_service()

    # Retrieve examples for prompt rendering with timing
    examples = []
    retrieval_start = time.perf_counter()

    retriever = get_rag_retriever_safe()
    if retriever:
        matches = retriever.retrieve_similar(
            description,
            k=RAG_TOP_K,
            threshold=RAG_SIMILARITY_THRESHOLD
        )
        examples = matches

    retrieval_time_ms = (time.perf_counter() - retrieval_start) * 1000

    # Build RAG metrics
    rag_metrics = build_rag_metrics(
        examples=examples,
        retrieval_time_ms=retrieval_time_ms,
        rag_enabled=retriever is not None,
        high_confidence_threshold=RAG_HIGH_CONFIDENCE_THRESHOLD,
    )

    # Check diversity
    diversity_info = check_precedent_diversity(examples)

    prompt = render_prompt(
        "DisputeClassifier_identify_category_v9_rag.j2",
        description=description,
        examples=examples,
        diversity_warning=diversity_info.get("warning"),
    )

    target_model = model or V9_RAG_MODEL

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
            if start != -1:
                content = content[start:]
        if not content.endswith("}"):
            end = content.rfind("}")
            if end != -1:
                content = content[:end + 1]

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

        # V9 fields defaults
        if "confidence_rationale" not in parsed:
            parsed["confidence_rationale"] = "Confidence based on branch analysis"
        if "reason_code_group" not in parsed:
            parsed["reason_code_group"] = "cardholder_disputes"
        if "precedent_override_applied" not in parsed:
            parsed["precedent_override_applied"] = None
        if "precedent_disagreement_note" not in parsed:
            parsed["precedent_disagreement_note"] = None

        result = CategoryResultV9Rag.model_validate(parsed)
    except Exception as e:
        logger.error(f"Failed to parse V9-RAG result: {e}")
        raise ValueError(f"Failed to parse output: {content[:200]}") from e

    trace = {
        "step": "identify_category_v9_rag",
        "prompt": prompt,
        "llm_response": completion.content,
        "parsed_output": result.model_dump(),
        "model": target_model,
        "retrieved_examples": examples,
        "rag_metrics": rag_metrics.model_dump(),
        "diversity_info": diversity_info,
    }

    return result, trace, rag_metrics, diversity_info


async def _select_code_trace(
    description: str,
    network: str,
    category: str,
    candidate_codes: List[Dict[str, str]],
    branch_summary: Optional[Dict[str, str]] = None
) -> Tuple[CodeSelectionResult, Dict[str, Any]]:
    """Select specific reason code with tracing."""
    service = get_default_service()

    enhanced_description = description
    if branch_summary:
        enhanced_description = (
            f"{description}\n\n"
            f"[Analysis: Acknowledgment={branch_summary.get('branch_a_conclusion', 'unknown')}, "
            f"Complaint={branch_summary.get('branch_b_complaint', 'unknown')}, "
            f"Persona={branch_summary.get('branch_c_persona', 'unknown')}, "
            f"ReasonCodeGroup={branch_summary.get('reason_code_group', 'unknown')}]"
        )

    prompt = render_prompt(
        "DisputeClassifier_select_code_v2.j2",
        description=enhanced_description,
        network=network,
        category=category,
        candidate_codes=candidate_codes
    )

    target_model = service.routing_model

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
            if start != -1:
                content = content[start:]
        if not content.endswith("}"):
            end = content.rfind("}")
            if end != -1:
                content = content[:end + 1]

        content = _repair_json(content)

        import json as json_lib
        try:
            parsed = json_lib.loads(content)
        except json.JSONDecodeError:
            from json_repair import repair_json
            repaired = repair_json(content)
            parsed = json_lib.loads(repaired)

        result = CodeSelectionResult.model_validate(parsed)
    except Exception as e:
        logger.error(f"Failed to parse Code Selection result: {e}")
        raise ValueError(f"Failed to parse code selection: {content[:200]}") from e

    trace = {
        "step": "select_code_v2",
        "prompt": prompt,
        "llm_response": completion.content,
        "parsed_output": result.model_dump(),
        "model": target_model
    }

    return result, trace


async def evaluate_v9_rag_trace(
    model: str = None,
    limit: int = 20
) -> None:
    """Run V9-RAG evaluation using golden set v3."""

    # Load V8 or V6 trace results for target IDs
    v8_trace_path = project_root / "qualitative" / "phase1" / "natural_language_trace_results_v8_rag.json"
    v6_trace_path = project_root / "qualitative" / "phase1" / "natural_language_trace_results_v6.json"

    trace_source = None
    target_ids = []

    if v8_trace_path.exists():
        with open(v8_trace_path, "r", encoding="utf-8") as f:
            trace_results = json.load(f)
        target_ids = [r["case"]["dispute_id"] for r in trace_results if "case" in r]
        trace_source = "V8"
    elif v6_trace_path.exists():
        with open(v6_trace_path, "r", encoding="utf-8") as f:
            trace_results = json.load(f)
        target_ids = [r["case"]["dispute_id"] for r in trace_results if "case" in r]
        trace_source = "V6"
    else:
        logger.error("No previous trace results found (V8 or V6).")
        return

    if limit and limit > 0:
        target_ids = target_ids[:limit]
    logger.info(f"Loaded {len(target_ids)} target cases from {trace_source} trace.")

    # Load Golden Set V3
    golden_v3_path = project_root / "synthetic_data" / "phase1" / "golden_set" / "natural_language_classification_v3.json"
    if not golden_v3_path.exists():
        logger.error(f"Golden Set V3 not found at {golden_v3_path}")
        return

    with open(golden_v3_path, "r", encoding="utf-8") as f:
        golden_v3 = json.load(f)

    golden_v3_lookup = {item["dispute_id"]: item for item in golden_v3}

    # Output path
    output_json_path = project_root / "qualitative" / "phase1" / "natural_language_trace_results_v9_rag.json"

    results: List[Dict[str, Any]] = []

    # Aggregate RAG stats
    rag_stats = {
        "total_cases": 0,
        "rag_enabled_cases": 0,
        "avg_precedents_retrieved": 0.0,
        "avg_top_similarity": 0.0,
        "high_confidence_matches": 0,
        "precedent_agreements": 0,
        "precedent_disagreements": 0,
        "confidence_adjustments": [],
        "diversity_warnings": 0,
    }

    print(f"Testing {len(target_ids)} cases with V9-RAG prompt...\n")
    print(f"Model: {model or V9_RAG_MODEL}")
    print(f"RAG Config: TOP_K={RAG_TOP_K}, THRESHOLD={RAG_SIMILARITY_THRESHOLD}, HIGH_CONF={RAG_HIGH_CONFIDENCE_THRESHOLD}\n")

    for i, dispute_id in enumerate(target_ids):
        golden_case = golden_v3_lookup.get(dispute_id)
        if not golden_case:
            logger.warning(f"Dispute {dispute_id} not found in Golden Set V3. Skipping.")
            continue

        description = golden_case["description"]
        expected = golden_case["category"]
        variation_type = golden_case.get("variation_type", "unknown")

        case_info = {
            "dispute_id": dispute_id,
            "variation_type": variation_type,
            "expected_category": expected,
            "description": description,
            "network": golden_case.get("network", "unknown"),
            "true_reason_code": golden_case.get("true_reason_code", "unknown"),
        }

        # Normalize expected category
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
            # Classification with V9 RAG
            result, trace, rag_metrics, diversity_info = await _identify_category_v9_rag_trace(
                description, model=model
            )
            prediction = result.category

            trace_steps = [trace]

            # Confidence calibration
            precedent_agreement = False
            if rag_metrics.precedent_categories:
                top_precedent_category = rag_metrics.precedent_categories[0]
                precedent_agreement = prediction == top_precedent_category

            adjusted_confidence, adjustment_reason = calibrate_confidence(
                base_confidence=result.confidence,
                rag_metrics=rag_metrics,
                precedent_agreement=precedent_agreement,
            )
            confidence_adjustment = adjusted_confidence - result.confidence

            is_pass = prediction == expected_norm
            status = "PASS" if is_pass else "FAIL"

            branch_conflict = check_branch_conflict(result)

            # Code Selection
            target_network = case_info.get("network")
            if not target_network or target_network == "unknown":
                target_network = _identify_network(description)

            catalog = get_reason_code_catalog()
            candidate_codes = catalog.get_codes_for_network_and_category(target_network, prediction)

            if not candidate_codes:
                candidate_codes = catalog.get_codes_for_network(target_network)

            code_result_data = {}
            if candidate_codes:
                try:
                    code_res, code_trace = await _select_code_trace(
                        description,
                        target_network,
                        prediction,
                        candidate_codes,
                        extract_branch_summary(result)
                    )
                    trace_steps.append(code_trace)

                    code_result_data = {
                        "selected_code": code_res.reason_code,
                        "code_confidence": code_res.confidence,
                        "code_reasoning": code_res.reasoning
                    }
                except Exception as e:
                    logger.error(f"Code selection failed for {dispute_id}: {e}")
                    code_result_data = {"error": str(e)}

            # Update aggregate stats
            rag_stats["total_cases"] += 1
            if rag_metrics.enabled:
                rag_stats["rag_enabled_cases"] += 1
                rag_stats["avg_precedents_retrieved"] += rag_metrics.precedents_retrieved
                rag_stats["avg_top_similarity"] += rag_metrics.top_similarity
                if rag_metrics.high_confidence_match:
                    rag_stats["high_confidence_matches"] += 1
                if precedent_agreement:
                    rag_stats["precedent_agreements"] += 1
                else:
                    rag_stats["precedent_disagreements"] += 1
            if diversity_info.get("warning"):
                rag_stats["diversity_warnings"] += 1
            if confidence_adjustment != 0:
                rag_stats["confidence_adjustments"].append(confidence_adjustment)

            trace_entry = {
                "case": case_info,
                "result": {
                    "category": prediction,
                    "reason_code_group": result.reason_code_group,
                    "reasoning": result.synthesis.reasoning,
                    "original_confidence": result.confidence,
                    "adjusted_confidence": adjusted_confidence,
                    "confidence_adjustment": round(confidence_adjustment, 3),
                    "confidence_adjustment_reason": adjustment_reason,
                    "confidence_rationale": result.confidence_rationale,
                    "precedent_override_applied": result.precedent_override_applied,
                    "precedent_disagreement_note": result.precedent_disagreement_note,
                    **code_result_data
                },
                "branch_analysis": extract_branch_summary(result),
                "branch_conflict": branch_conflict,
                "rag_metrics": rag_metrics.model_dump(),
                "precedent_diversity": diversity_info,
                "precedent_agreement": precedent_agreement,
                "trace": {"steps": trace_steps},
                "status": status,
                "model": model or V9_RAG_MODEL,
            }
            results.append(trace_entry)

            conflict_indicator = " [CONFLICT]" if branch_conflict else ""
            rag_indicator = f" RAG:{rag_metrics.precedents_retrieved}@{rag_metrics.top_similarity:.2f}" if rag_metrics.enabled else " [NO RAG]"
            adj_indicator = f" Adj:{confidence_adjustment:+.2f}" if confidence_adjustment != 0 else ""
            code_info = f" Code: {code_result_data.get('selected_code', 'N/A')}"

            print(
                f"[{i+1}/{len(target_ids)}] {dispute_id}: {status} "
                f"(Exp: {expected}, Got: {prediction}){code_info}"
                f"{rag_indicator}{adj_indicator}{conflict_indicator}"
            )

        except Exception as e:
            logger.error(f"Error processing {dispute_id}: {e}")
            results.append({
                "case": case_info,
                "result": {"category": "ERROR", "reasoning": str(e)},
                "status": "ERROR",
                "model": model or V9_RAG_MODEL,
            })

    # Finalize aggregate stats
    if rag_stats["rag_enabled_cases"] > 0:
        rag_stats["avg_precedents_retrieved"] /= rag_stats["rag_enabled_cases"]
        rag_stats["avg_top_similarity"] /= rag_stats["rag_enabled_cases"]

    avg_adj = sum(rag_stats["confidence_adjustments"]) / len(rag_stats["confidence_adjustments"]) if rag_stats["confidence_adjustments"] else 0
    rag_stats["avg_confidence_adjustment"] = round(avg_adj, 4)
    rag_stats["confidence_adjustments"] = len(rag_stats["confidence_adjustments"])  # Just count

    # Save results
    output = {
        "results": results,
        "aggregate_rag_stats": rag_stats,
    }

    with open(output_json_path, "w") as f:
        json.dump(output, f, indent=2)

    # Stats
    passed = sum(1 for r in results if r["status"] == "PASS")
    total = len(results)

    print("\n" + "=" * 70)
    print("V9-RAG Evaluation Complete")
    print("=" * 70)
    print(f"\nOverall Accuracy: {passed}/{total} ({passed/total*100:.1f}%)")
    print("\nRAG Statistics:")
    print(f"  - Cases with RAG: {rag_stats['rag_enabled_cases']}/{total}")
    print(f"  - Avg precedents retrieved: {rag_stats['avg_precedents_retrieved']:.2f}")
    print(f"  - Avg top similarity: {rag_stats['avg_top_similarity']:.3f}")
    print(f"  - High confidence matches: {rag_stats['high_confidence_matches']}")
    print(f"  - Precedent agreements: {rag_stats['precedent_agreements']}")
    print(f"  - Precedent disagreements: {rag_stats['precedent_disagreements']}")
    print(f"  - Diversity warnings: {rag_stats['diversity_warnings']}")
    print(f"  - Avg confidence adjustment: {rag_stats['avg_confidence_adjustment']:+.4f}")
    print(f"\nTrace results saved to {output_json_path}")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", type=str, default=None)
    parser.add_argument("--limit", type=int, default=20)
    args = parser.parse_args()

    asyncio.run(evaluate_v9_rag_trace(model=args.model, limit=args.limit))
