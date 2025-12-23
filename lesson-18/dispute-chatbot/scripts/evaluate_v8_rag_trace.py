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

# Disable TensorFlow to avoid Keras 3 compatibility issues in Transformers
# We only use PyTorch via SentenceTransformers
os.environ["USE_TF"] = "0"

# Mock torch._dynamo to prevent transformers from triggering a "Duplicate dispatch rule" error
# which happens on some environments (Mac MPS) when is_compiling() is checked repeatedly.
class _MockDynamo:
    def is_compiling(self):
        return False
sys.modules["torch._dynamo"] = _MockDynamo()

# Disable LLM caching to avoid missing dependency errors
os.environ["LLM_CACHE_TYPE"] = "disabled"

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from utils.llm_service import get_default_service
from utils.prompt_service import render_prompt
from backend.phases.classify_v8_rag import (
    CategoryResultV8Rag,
    CodeSelectionResult,
    V8_RAG_MODEL,
    extract_branch_summary,
    check_branch_conflict,
    get_rag_retriever,
    _identify_network
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
        # Hard stop if retrieval fails
        matches = retriever.retrieve_similar(description, k=3, threshold=0.4)
        examples = matches
            
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

    # Use complete() to get raw response for tracing
    # Note: Using routing_model as per original implementation
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
            if start != -1: content = content[start:]
        if not content.endswith("}"):
            end = content.rfind("}")
            if end != -1: content = content[:end + 1]

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


async def evaluate_v8_rag_trace(
    model: str = None,
    limit: int = 20 # Ignored if using trace file
) -> None:
    """Run V8-RAG evaluation using golden set v3 and v6 trace IDs."""
    
    # 1. Load V6 Trace Results to get the list of Dispute IDs
    v6_trace_path = project_root / "qualitative" / "phase1" / "natural_language_trace_results_v6.json"
    if not v6_trace_path.exists():
        logger.error(f"V6 trace results not found at {v6_trace_path}")
        return

    with open(v6_trace_path, "r", encoding="utf-8") as f:
        v6_results = json.load(f)
    
    # Extract IDs to test
    target_ids = [r["case"]["dispute_id"] for r in v6_results if "case" in r and "dispute_id" in r["case"]]
    if limit and limit > 0:
        target_ids = target_ids[:limit]
    logger.info(f"Loaded {len(target_ids)} target cases from V6 trace.")

    # 2. Load Golden Set V3
    golden_v3_path = project_root / "synthetic_data" / "phase1" / "golden_set" / "natural_language_classification_v3.json"
    if not golden_v3_path.exists():
        logger.error(f"Golden Set V3 not found at {golden_v3_path}")
        return

    with open(golden_v3_path, "r", encoding="utf-8") as f:
        golden_v3 = json.load(f)
    
    # Create lookup for Golden V3
    golden_v3_lookup = {item["dispute_id"]: item for item in golden_v3}

    # Output path
    output_json_path = project_root / "qualitative" / "phase1" / "natural_language_trace_results_v8_rag.json"

    trace_results: List[Dict[str, Any]] = []

    print(f"Testing {len(target_ids)} cases with V8-RAG prompt...\n")
    print(f"Model: {model or V8_RAG_MODEL}\n")

    for i, dispute_id in enumerate(target_ids):
        # Get case data from Golden V3
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
            "expected_category": expected, # V3 Expectation
            "description": description,
            "network": golden_case.get("network", "unknown"),
            "true_reason_code": golden_case.get("true_reason_code", "unknown"),
            "expected_category_v3": expected,
            "category_v3_previous": golden_case.get("category_v3_previous"),
            "category_change_reason": golden_case.get("category_change_reason"),
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
            # 1. Classification
            result, trace = await _identify_category_v8_rag_trace(description, model=model)
            prediction = result.category
            
            trace_steps = [trace]

            is_pass = prediction == expected_norm
            status = "PASS" if is_pass else "FAIL"

            branch_conflict = check_branch_conflict(result)

            # 2. Code Selection
            # Identify network
            target_network = case_info.get("network")
            if not target_network or target_network == "unknown":
                target_network = _identify_network(description)
            
            # Get candidates
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

            trace_entry = {
                "case": case_info,
                "result": {
                    "category": prediction,
                    "reason_code_group": result.reason_code_group,
                    "reasoning": result.synthesis.reasoning,
                    "confidence": result.confidence,
                    "confidence_rationale": result.confidence_rationale,
                    **code_result_data
                },
                "branch_analysis": extract_branch_summary(result),
                "branch_conflict": branch_conflict,
                "trace": {"steps": trace_steps},
                "status": status,
                "model": model or V8_RAG_MODEL,
            }
            trace_results.append(trace_entry)

            conflict_indicator = " [CONFLICT]" if branch_conflict else ""
            code_info = f" Code: {code_result_data.get('selected_code', 'N/A')}"
            
            print(
                f"[{i+1}/{len(target_ids)}] {dispute_id}: {status} "
                f"(Exp: {expected}, Got: {prediction}){code_info} "
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

