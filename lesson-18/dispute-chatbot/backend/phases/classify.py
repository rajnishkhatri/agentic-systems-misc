"""CLASSIFY Phase Handler (FR1.3).

Identifies the dispute reason code, network, and deadline using LLM classification
and standardized reason code catalog via a 3-step optimized flow.
"""

from __future__ import annotations

import datetime
import logging
from typing import Any, List, Dict, Optional

from pydantic import BaseModel, Field

from utils.llm_service import get_default_service
from utils.prompt_service import render_prompt
from backend.adapters.reason_code_catalog import get_reason_code_catalog

logger = logging.getLogger(__name__)


class CategoryResult(BaseModel):
    """Structured output for category identification."""
    category: str = Field(description="Selected standardized category")
    reasoning: str = Field(description="Explanation for the category choice")


class CodeSelectionResult(BaseModel):
    """Structured output for reason code selection."""
    reason_code: str = Field(description="Selected reason code from the candidate list")
    confidence: float = Field(description="Confidence score between 0.0 and 1.0")
    reasoning: str = Field(description="Explanation for the specific code selection")


def _identify_network(description: str) -> str:
    """Identify payment network from description using keywords.
    
    Falls back to 'visa' if no specific network is mentioned, but allows
    for 'amex', 'mastercard', 'discover', 'paypal', etc. if present.
    """
    desc_lower = description.lower()
    
    # Priority order matters slightly if multiple are present, but usually they are distinct
    if "amex" in desc_lower or "american express" in desc_lower:
        return "amex"
    if "mastercard" in desc_lower:
        return "mastercard"
    if "discover" in desc_lower:
        return "discover"
    if "visa" in desc_lower:
        return "visa"
    if "paypal" in desc_lower:
        return "paypal"
    if "gateway" in desc_lower or "quota" in desc_lower or "unauthorized" in desc_lower:
        # Heuristic for openapi_gateway_response based on error codes
        return "openapi_gateway_response"
    
    # Default to visa if unknown (for V1)
    return "visa"


async def _identify_category(description: str) -> CategoryResult:
    """Step 2: Identify the unified category using LLM."""
    service = get_default_service()
    prompt = render_prompt(
        "DisputeClassifier_identify_category.j2",
        description=description
    )
    
    return await service.complete_structured(
        messages=[{"role": "user", "content": prompt}],
        response_model=CategoryResult,
        model=service.routing_model
    )


async def _select_code(description: str, network: str, category: str, candidate_codes: List[Dict[str, str]]) -> CodeSelectionResult:
    """Step 3: Select specific reason code from filtered candidates."""
    service = get_default_service()
    prompt = render_prompt(
        "DisputeClassifier_select_code.j2",
        description=description,
        network=network,
        category=category,
        candidate_codes=candidate_codes
    )
    
    return await service.complete_structured(
        messages=[{"role": "user", "content": prompt}],
        response_model=CodeSelectionResult,
        model=service.routing_model
    )


async def classify_dispute(task: dict[str, Any]) -> dict[str, Any]:
    """Execute the CLASSIFY phase using the 3-step funnel approach.

    Args:
        task: Task dictionary containing 'dispute_id' and optionally 'description' or 'files'

    Returns:
        Dictionary with classification results.

    Raises:
        TypeError: If task is not a dictionary.
        ValueError: If required fields are missing.
    """
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
        # Check if network was already selected in UI
        target_network = task.get("network")

        if target_network:
            logger.info(f"Dispute {dispute_id}: Using pre-selected network {target_network}")
        else:
            # Fallback to internal identification if not provided
            target_network = _identify_network(description)
            logger.info(f"Dispute {dispute_id}: Identified network as {target_network}")

        # Step 3: Category Identification (LLM)
        category_result = await _identify_category(description)
        target_category = category_result.category
        logger.info(f"Dispute {dispute_id}: Identified category as {target_category}")

        # Step 4: Code Selection (LLM with Filtered Candidates)
        catalog = get_reason_code_catalog()
        candidate_codes = catalog.get_codes_for_network_and_category(target_network, target_category)
        
        if not candidate_codes:
            logger.warning(f"No reason codes found for network {target_network} and category {target_category}. Falling back to network-only search.")
            candidate_codes = catalog.get_codes_for_network(target_network)
            if not candidate_codes:
                raise ValueError(f"No reason codes found for network {target_network}")

        code_result = await _select_code(description, target_network, target_category, candidate_codes)
        logger.info(f"Dispute {dispute_id}: Selected code {code_result.reason_code}")

        # Step 5: Post-processing
        
        # Calculate deadline (mock: 14 days from now)
        current_date_str = task.get("current_date")
        if current_date_str:
            try:
                current_date = datetime.datetime.strptime(current_date_str, "%Y-%m-%d")
            except ValueError:
                 current_date = datetime.datetime.now()
        else:
            current_date = datetime.datetime.now()

        deadline = (current_date + datetime.timedelta(days=14)).strftime("%Y-%m-%d")
        
        # Determine is_fraud based on category
        is_fraud = target_category == "fraudulent"

        return {
            "reason_code": code_result.reason_code,
            "network": target_network,
            "category": target_category,
            "is_fraud": is_fraud,
            "deadline": deadline,
            "classification_confidence": code_result.confidence,
            "classification_reasoning": f"Category: {category_result.reasoning} | Code: {code_result.reasoning}"
        }

    except Exception as e:
        logger.error(f"Classification phase failed for dispute {dispute_id}: {e}", exc_info=True)
        raise RuntimeError(f"Classification failed for dispute {dispute_id}: {str(e)}") from e
