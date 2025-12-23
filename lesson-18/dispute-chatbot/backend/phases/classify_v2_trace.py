"""CLASSIFY Phase Handler V2 (Trace Instrumented).

Enhanced classification with full execution tracing for debugging.
Based on classify_v2.py Version 2.0.0
"""

from __future__ import annotations

import datetime
import json
import logging
from pathlib import Path
from typing import Any, List, Dict, Optional, Tuple

from pydantic import BaseModel, Field

from utils.llm_service import get_default_service
from utils.prompt_service import render_prompt
from backend.adapters.reason_code_catalog import get_reason_code_catalog
from backend.phases.classify_v2 import (
    CategoryResult,
    CodeSelectionResult,
    _load_keyword_hints,
    _identify_network,
    _detect_network_family,
    _get_keyword_code_hint
)

logger = logging.getLogger(__name__)

async def _identify_category_trace(description: str) -> Tuple[CategoryResult, Dict[str, Any]]:
    """Step 2: Identify the unified category using LLM with v2 prompt (traced)."""
    service = get_default_service()
    prompt = render_prompt(
        "DisputeClassifier_identify_category_v2.j2",
        description=description
    )

    # Use complete() instead of complete_structured to capture raw response
    completion = await service.complete(
        messages=[{"role": "user", "content": prompt}],
        model=service.routing_model,
        temperature=0.0
    )
    
    # Parse manually
    try:
        # Clean up potential markdown code blocks if the model adds them
        content = completion.content.strip()
        if content.startswith("```json"):
            content = content[7:]
        if content.startswith("```"):
            content = content[3:]
        if content.endswith("```"):
            content = content[:-3]
        content = content.strip()
            
        result = CategoryResult.model_validate_json(content)
    except Exception as e:
        logger.error(f"Failed to parse category result: {e}")
        raise ValueError(f"Failed to parse output: {content}") from e

    trace = {
        "step": "identify_category",
        "prompt": prompt,
        "raw_response": completion.content,
        "parsed_output": result.model_dump()
    }

    return result, trace


async def _select_code_trace(
    description: str,
    network: str,
    category: str,
    candidate_codes: List[Dict[str, str]],
    keyword_hint: Optional[Dict[str, str]] = None
) -> Tuple[CodeSelectionResult, Dict[str, Any]]:
    """Step 3: Select specific reason code from filtered candidates using v2 prompt (traced)."""
    service = get_default_service()

    # If we have a keyword hint, add it to the description context
    enhanced_description = description
    if keyword_hint:
        enhanced_description = (
            f"{description}\n\n"
            f"[System hint: Based on keywords '{keyword_hint.get('matched_keywords', [])}', "
            f"consider code {keyword_hint['code']} - {keyword_hint['explanation']}]"
        )

    prompt = render_prompt(
        "DisputeClassifier_select_code_v2.j2",
        description=enhanced_description,
        network=network,
        category=category,
        candidate_codes=candidate_codes
    )

    # Use complete() instead of complete_structured
    completion = await service.complete(
        messages=[{"role": "user", "content": prompt}],
        model=service.routing_model,
        temperature=0.0
    )

    try:
        # Clean up potential markdown code blocks
        content = completion.content.strip()
        if content.startswith("```json"):
            content = content[7:]
        if content.startswith("```"):
            content = content[3:]
        if content.endswith("```"):
            content = content[:-3]
        content = content.strip()

        result = CodeSelectionResult.model_validate_json(content)
    except Exception as e:
        logger.error(f"Failed to parse code selection result: {e}")
        raise ValueError(f"Failed to parse output: {content}") from e

    trace = {
        "step": "select_code",
        "prompt": prompt,
        "raw_response": completion.content,
        "parsed_output": result.model_dump(),
        "candidate_codes": candidate_codes
    }

    return result, trace


async def classify_dispute_v2_trace(task: dict[str, Any]) -> Tuple[dict[str, Any], Dict[str, Any]]:
    """Execute the CLASSIFY phase V2 with enhanced prompts and hints, returning full traces.
    
    Returns:
        Tuple[Result Dict, Trace Dict]
    """
    traces = {
        "dispute_id": task.get("dispute_id"),
        "steps": []
    }

    # Step 1: Input Validation
    if not isinstance(task, dict):
        raise TypeError("task must be a dictionary")

    dispute_id = task.get("dispute_id")
    if not dispute_id:
        raise ValueError("task must contain 'dispute_id'")

    description = task.get("description")
    if not description:
        raise ValueError("task must contain 'description'")
    
    try:
        # Step 2: Network Identification (Hybrid: Explicit > Deterministic)
        target_network = task.get("network")
        network_source = "explicit"
        if target_network:
            logger.info(f"Dispute {dispute_id}: Using pre-selected network {target_network}")
        else:
            target_network = _identify_network(description)
            network_source = "keyword_detection"
            logger.info(f"Dispute {dispute_id}: Identified network as {target_network}")
        
        traces["steps"].append({
            "step": "identify_network",
            "network": target_network,
            "source": network_source
        })

        # Step 2.5: Network Family Detection (NEW in V2)
        network_family = _detect_network_family(description)
        traces["steps"].append({
            "step": "detect_network_family",
            "family": network_family
        })

        # Step 3: Keyword Hint Detection (NEW in V2)
        keyword_hint = _get_keyword_code_hint(description, target_network)
        if keyword_hint:
            traces["steps"].append({
                "step": "keyword_hint",
                "hint": keyword_hint
            })

        # Step 4: Category Identification (LLM with V2 prompt)
        category_result, category_trace = await _identify_category_trace(description)
        target_category = category_result.category
        traces["steps"].append(category_trace)
        logger.info(f"Dispute {dispute_id}: Identified category as {target_category}")

        # Step 5: Code Selection (LLM with V2 prompt + hints)
        catalog = get_reason_code_catalog()
        candidate_codes = catalog.get_codes_for_network_and_category(target_network, target_category)

        if not candidate_codes:
            logger.warning(
                f"No reason codes found for network {target_network} and category {target_category}. "
                f"Falling back to network-only search."
            )
            candidate_codes = catalog.get_codes_for_network(target_network)
            traces["steps"].append({
                "step": "fallback_search",
                "message": "Falling back to network-only search"
            })
            if not candidate_codes:
                raise ValueError(f"No reason codes found for network {target_network}")

        code_result, code_trace = await _select_code_trace(
            description,
            target_network,
            target_category,
            candidate_codes,
            keyword_hint=keyword_hint
        )
        traces["steps"].append(code_trace)
        logger.info(f"Dispute {dispute_id}: Selected code {code_result.reason_code} (confidence: {code_result.confidence})")

        # Step 6: Post-processing
        current_date_str = task.get("current_date")
        if current_date_str:
            try:
                current_date = datetime.datetime.strptime(current_date_str, "%Y-%m-%d")
            except ValueError:
                current_date = datetime.datetime.now()
        else:
            current_date = datetime.datetime.now()

        deadline = (current_date + datetime.timedelta(days=14)).strftime("%Y-%m-%d")
        is_fraud = target_category == "fraudulent"

        result = {
            "reason_code": code_result.reason_code,
            "network": target_network,
            "category": target_category,
            "network_family": network_family,  # NEW in V2
            "is_fraud": is_fraud,
            "deadline": deadline,
            "classification_confidence": code_result.confidence,
            "classification_reasoning": f"Category: {category_result.reasoning} | Code: {code_result.reasoning}",
            "keyword_hint_used": keyword_hint is not None,  # NEW in V2
            "classifier_version": "2.0.0-trace"
        }
        
        return result, traces

    except Exception as e:
        logger.error(f"Classification V2 Trace phase failed for dispute {dispute_id}: {e}", exc_info=True)
        traces["error"] = str(e)
        # We re-raise to maintain API behavior, but the caller should ideally catch this if they want the partial trace
        raise RuntimeError(f"Classification failed for dispute {dispute_id}: {str(e)}") from e

