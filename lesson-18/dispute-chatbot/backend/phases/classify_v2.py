"""CLASSIFY Phase Handler V2 (FR1.3).

Enhanced classification with:
- Negative examples in category prompt
- Few-shot examples in code selection prompt
- Keyword disambiguation hints
- Network family intermediate signal

Version: 2.0.0
"""

from __future__ import annotations

import datetime
import json
import logging
import re
from pathlib import Path
from typing import Any, List, Dict, Optional

from pydantic import BaseModel, Field

from utils.llm_service import get_default_service
from utils.prompt_service import render_prompt
from backend.adapters.reason_code_catalog import get_reason_code_catalog

logger = logging.getLogger(__name__)

# Load keyword hints at module level
_KEYWORD_HINTS: Optional[Dict[str, Any]] = None


def _load_keyword_hints() -> Dict[str, Any]:
    """Load keyword disambiguation hints from JSON file."""
    global _KEYWORD_HINTS
    if _KEYWORD_HINTS is not None:
        return _KEYWORD_HINTS

    hints_path = Path(__file__).parent.parent / "adapters" / "keyword_hints.json"
    if hints_path.exists():
        with open(hints_path, "r", encoding="utf-8") as f:
            _KEYWORD_HINTS = json.load(f)
    else:
        logger.warning(f"Keyword hints file not found at {hints_path}")
        _KEYWORD_HINTS = {}

    return _KEYWORD_HINTS


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

    Falls back to 'visa' if no specific network is mentioned.
    """
    desc_lower = description.lower()

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
    if "gateway" in desc_lower or "quota" in desc_lower:
        return "openapi_gateway_response"

    return "visa"


def _detect_network_family(description: str) -> Optional[str]:
    """Detect likely network family from keywords in description.

    Returns one of: authorization, fraud, cardholder_disputes, processing_errors, or None.
    """
    hints = _load_keyword_hints()
    family_hints = hints.get("network_family_hints", {})

    desc_lower = description.lower()
    scores = {}

    for family, keywords in family_hints.items():
        score = sum(1 for kw in keywords if kw in desc_lower)
        if score > 0:
            scores[family] = score

    if scores:
        return max(scores, key=scores.get)
    return None


def _get_keyword_code_hint(description: str, network: str) -> Optional[Dict[str, str]]:
    """Check if description matches any disambiguation rule.

    Returns dict with 'code' and 'explanation' if a strong match is found.
    """
    hints = _load_keyword_hints()
    rules = hints.get("disambiguation_rules", {})

    desc_lower = description.lower()

    for rule_group in rules.values():
        for rule_name, rule_data in rule_group.items():
            keywords = rule_data.get("keywords", [])
            codes = rule_data.get("codes", {})

            # Check if any keyword matches
            matches = [kw for kw in keywords if kw in desc_lower]
            if matches and network in codes:
                return {
                    "code": codes[network],
                    "explanation": rule_data.get("explanation", ""),
                    "matched_keywords": matches
                }

    return None


async def _identify_category(description: str) -> CategoryResult:
    """Step 2: Identify the unified category using LLM with v2 prompt."""
    service = get_default_service()
    prompt = render_prompt(
        "DisputeClassifier_identify_category_v2.j2",
        description=description
    )

    return await service.complete_structured(
        messages=[{"role": "user", "content": prompt}],
        response_model=CategoryResult,
        model=service.routing_model
    )


async def _select_code(
    description: str,
    network: str,
    category: str,
    candidate_codes: List[Dict[str, str]],
    keyword_hint: Optional[Dict[str, str]] = None
) -> CodeSelectionResult:
    """Step 3: Select specific reason code from filtered candidates using v2 prompt."""
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

    return await service.complete_structured(
        messages=[{"role": "user", "content": prompt}],
        response_model=CodeSelectionResult,
        model=service.routing_model
    )


async def classify_dispute_v2(task: dict[str, Any]) -> dict[str, Any]:
    """Execute the CLASSIFY phase V2 with enhanced prompts and hints.

    Improvements over V1:
    - Uses prompts with negative examples and few-shot examples
    - Applies keyword disambiguation for confusable codes
    - Detects network family as intermediate signal

    Args:
        task: Task dictionary containing 'dispute_id' and 'description'

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
        target_network = task.get("network")
        if target_network:
            logger.info(f"Dispute {dispute_id}: Using pre-selected network {target_network}")
        else:
            target_network = _identify_network(description)
            logger.info(f"Dispute {dispute_id}: Identified network as {target_network}")

        # Step 2.5: Network Family Detection (NEW in V2)
        network_family = _detect_network_family(description)
        if network_family:
            logger.info(f"Dispute {dispute_id}: Detected network family hint: {network_family}")

        # Step 3: Keyword Hint Detection (NEW in V2)
        keyword_hint = _get_keyword_code_hint(description, target_network)
        if keyword_hint:
            logger.info(
                f"Dispute {dispute_id}: Keyword hint suggests code {keyword_hint['code']} "
                f"based on: {keyword_hint['matched_keywords']}"
            )

        # Step 4: Category Identification (LLM with V2 prompt)
        category_result = await _identify_category(description)
        target_category = category_result.category
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
            if not candidate_codes:
                raise ValueError(f"No reason codes found for network {target_network}")

        code_result = await _select_code(
            description,
            target_network,
            target_category,
            candidate_codes,
            keyword_hint=keyword_hint
        )
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

        return {
            "reason_code": code_result.reason_code,
            "network": target_network,
            "category": target_category,
            "network_family": network_family,  # NEW in V2
            "is_fraud": is_fraud,
            "deadline": deadline,
            "classification_confidence": code_result.confidence,
            "classification_reasoning": f"Category: {category_result.reasoning} | Code: {code_result.reasoning}",
            "keyword_hint_used": keyword_hint is not None,  # NEW in V2
            "classifier_version": "2.0.0"  # NEW in V2
        }

    except Exception as e:
        logger.error(f"Classification V2 phase failed for dispute {dispute_id}: {e}", exc_info=True)
        raise RuntimeError(f"Classification failed for dispute {dispute_id}: {str(e)}") from e
