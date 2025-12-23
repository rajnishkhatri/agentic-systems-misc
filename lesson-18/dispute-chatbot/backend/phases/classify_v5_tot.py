"""CLASSIFY Phase Handler V5-ToT (Tree-of-Thought).

Enhanced classification with:
- Tree-of-Thought reasoning with 3 independent branches
- Positive framing for checkpoints
- Branch synthesis with priority rules
- Confidence calibration with rationale
- Anthropic Claude model support

Version: 5.0.0
"""

from __future__ import annotations

import datetime
import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, field_validator

from utils.llm_service import get_default_service
from utils.prompt_service import render_prompt
from backend.adapters.reason_code_catalog import get_reason_code_catalog

logger = logging.getLogger(__name__)

# Default model for V5-ToT (can be overridden)
V5_TOT_MODEL = "anthropic/claude-sonnet-4-20250514"


class BranchAResult(BaseModel):
    """Branch A: Transaction Acknowledgment Analysis."""

    evidence_for_acknowledgment: List[str] = Field(
        default_factory=list,
        description="Phrases showing user acknowledges the transaction"
    )
    evidence_against_acknowledgment: List[str] = Field(
        default_factory=list,
        description="Phrases showing user denies the transaction"
    )
    conclusion: str = Field(
        description="Conclusion: acknowledged, denied, or unclear"
    )

    @field_validator("conclusion")
    @classmethod
    def validate_conclusion(cls, v: str) -> str:
        """Validate conclusion is one of the allowed values."""
        allowed = {"acknowledged", "denied", "unclear"}
        if v.lower() not in allowed:
            raise ValueError(f"Branch A conclusion must be one of {allowed}, got: {v}")
        return v.lower()


class BranchBResult(BaseModel):
    """Branch B: Complaint Specifics Analysis."""

    complaint_type: str = Field(
        description="Type of complaint: amount, quality, processing, or unspecified"
    )
    evidence: List[str] = Field(
        default_factory=list,
        description="Specific phrases indicating the complaint type"
    )

    @field_validator("complaint_type")
    @classmethod
    def validate_complaint_type(cls, v: str) -> str:
        """Validate complaint type is one of the allowed values."""
        allowed = {"amount", "quality", "processing", "unspecified"}
        v_norm = v.lower().strip()
        
        # Normalization
        aliases = {
            "discrepancy": "amount",
            "billing_error": "amount",
            "refund": "processing",
            "fraud": "unspecified",
            "unauthorized": "unspecified",
            "duplicate": "processing"
        }
        
        v_norm = aliases.get(v_norm, v_norm)
        
        if v_norm not in allowed:
            # Fallback to unspecified rather than failing
            logger.warning(f"Invalid Branch B complaint_type '{v}', defaulting to 'unspecified'")
            return "unspecified"
        return v_norm


class BranchCResult(BaseModel):
    """Branch C: User Persona Analysis."""

    persona: str = Field(
        description="User persona: frustrated, confused, accusatory, or neutral"
    )
    evidence: List[str] = Field(
        default_factory=list,
        description="Phrases indicating the persona type"
    )

    @field_validator("persona")
    @classmethod
    def validate_persona(cls, v: str) -> str:
        """Validate persona is one of the allowed values."""
        allowed = {"frustrated", "confused", "accusatory", "neutral"}
        v_norm = v.lower().strip()
        
        # Normalization
        aliases = {
            "concerned": "neutral",
            "worried": "neutral",
            "angry": "frustrated",
            "upset": "frustrated",
            "annoyed": "frustrated"
        }
        
        v_norm = aliases.get(v_norm, v_norm)
        
        if v_norm not in allowed:
            # Fallback to neutral rather than failing
            logger.warning(f"Invalid Branch C persona '{v}', defaulting to 'neutral'")
            return "neutral"
        return v_norm


class SynthesisResult(BaseModel):
    """Branch synthesis with priority rule application."""

    branch_agreement: float = Field(
        ge=0.0,
        le=1.0,
        description="How aligned are the 3 branches (0.0-1.0)"
    )
    priority_rule_applied: Optional[str] = Field(
        default=None,
        description="Which priority rule was applied, if any"
    )
    reasoning: str = Field(
        description="Step-by-step synthesis logic"
    )


class CategoryResultV5ToT(BaseModel):
    """Structured output for V5 Tree-of-Thought category identification."""

    # Branch results
    branch_a: BranchAResult = Field(description="Transaction acknowledgment analysis")
    branch_b: BranchBResult = Field(description="Complaint specifics analysis")
    branch_c: BranchCResult = Field(description="User persona analysis")

    # Synthesis
    synthesis: SynthesisResult = Field(description="Branch synthesis and priority rules")

    # Final classification
    category: str = Field(description="Selected standardized category")
    confidence: float = Field(
        ge=0.0,
        le=1.0,
        description="Confidence score: 0.95+ exact, 0.85-0.94 strong, 0.70-0.84 moderate, <0.70 uncertain"
    )
    confidence_rationale: str = Field(description="Explanation for confidence level")

    @field_validator("category")
    @classmethod
    def validate_category(cls, v: str) -> str:
        """Validate category is one of the allowed values."""
        allowed = {
            "fraudulent", "general", "product_not_received", "duplicate",
            "subscription_canceled", "product_unacceptable", "credit_not_processed",
            "unrecognized"
        }
        v_norm = v.lower().strip().replace(" ", "_").replace("-", "_")
        
        # Aliases normalization
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
        
        v_norm = aliases.get(v_norm, v_norm)
        
        if v_norm not in allowed:
            raise ValueError(f"Category must be one of {allowed}, got: {v}")
        return v_norm


class CodeSelectionResult(BaseModel):
    """Structured output for reason code selection."""

    reason_code: str = Field(description="Selected reason code from the candidate list")
    confidence: float = Field(
        ge=0.0,
        le=1.0,
        description="Confidence score between 0.0 and 1.0"
    )
    reasoning: str = Field(description="Explanation for the specific code selection")


def _identify_network(description: str) -> str:
    """Identify payment network from description using keywords.

    Args:
        description: The dispute description text.

    Returns:
        Network identifier string. Defaults to 'visa' if no specific network mentioned.
    """
    if not isinstance(description, str):
        raise TypeError("description must be a string")

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

    return "visa"


def extract_branch_summary(result: CategoryResultV5ToT) -> Dict[str, str]:
    """Extract a summary of branch conclusions for logging/debugging.

    Args:
        result: The V5-ToT category result.

    Returns:
        Dictionary with branch conclusion summaries.
    """
    if not isinstance(result, CategoryResultV5ToT):
        raise TypeError("result must be a CategoryResultV5ToT instance")

    return {
        "branch_a_conclusion": result.branch_a.conclusion,
        "branch_b_complaint": result.branch_b.complaint_type,
        "branch_c_persona": result.branch_c.persona,
        "branch_agreement": result.synthesis.branch_agreement,
        "priority_rule": result.synthesis.priority_rule_applied or "none",
    }


def check_branch_conflict(result: CategoryResultV5ToT) -> Optional[Dict[str, Any]]:
    """Check if branches have conflicting signals that required priority rules.

    Args:
        result: The V5-ToT category result.

    Returns:
        Dictionary with conflict details if detected, None otherwise.
    """
    if not isinstance(result, CategoryResultV5ToT):
        raise TypeError("result must be a CategoryResultV5ToT instance")

    # Conflict detection: denial + amount complaint
    if (result.branch_a.conclusion == "denied" and
            result.branch_b.complaint_type == "amount"):
        return {
            "type": "denial_with_amount",
            "resolution": "amount_overrides_denial",
            "branch_a": result.branch_a.conclusion,
            "branch_b": result.branch_b.complaint_type,
            "rule_applied": result.synthesis.priority_rule_applied,
        }

    # Conflict detection: unclear acknowledgment + accusatory persona
    if (result.branch_a.conclusion == "unclear" and
            result.branch_c.persona == "accusatory"):
        return {
            "type": "unclear_with_accusatory",
            "resolution": "needs_persona_tiebreaker",
            "branch_a": result.branch_a.conclusion,
            "branch_c": result.branch_c.persona,
            "rule_applied": result.synthesis.priority_rule_applied,
        }

    return None


async def _identify_category_v5_tot(
    description: str,
    model: Optional[str] = None
) -> CategoryResultV5ToT:
    """Identify category using V5 Tree-of-Thought prompt.

    Args:
        description: The dispute description to classify.
        model: Optional model override. Defaults to V5_TOT_MODEL.

    Returns:
        CategoryResultV5ToT with branch analysis and final classification.

    Raises:
        TypeError: If description is not a string.
        ValueError: If description is empty.
    """
    if not isinstance(description, str):
        raise TypeError("description must be a string")
    if not description.strip():
        raise ValueError("description cannot be empty")

    service = get_default_service()
    prompt = render_prompt(
        "DisputeClassifier_identify_category_v5_tot.j2",
        description=description
    )

    target_model = model or V5_TOT_MODEL

    return await service.complete_structured(
        messages=[{"role": "user", "content": prompt}],
        response_model=CategoryResultV5ToT,
        model=target_model
    )


async def _select_code(
    description: str,
    network: str,
    category: str,
    candidate_codes: List[Dict[str, str]],
    branch_summary: Optional[Dict[str, str]] = None
) -> CodeSelectionResult:
    """Select specific reason code from filtered candidates.

    Args:
        description: The dispute description.
        network: Target payment network.
        category: Identified dispute category.
        candidate_codes: List of candidate reason codes.
        branch_summary: Optional branch analysis summary for context.

    Returns:
        CodeSelectionResult with selected code and reasoning.
    """
    service = get_default_service()

    # Enhance description with branch summary if available
    enhanced_description = description
    if branch_summary:
        enhanced_description = (
            f"{description}\n\n"
            f"[Analysis: Acknowledgment={branch_summary.get('branch_a_conclusion', 'unknown')}, "
            f"Complaint={branch_summary.get('branch_b_complaint', 'unknown')}, "
            f"Persona={branch_summary.get('branch_c_persona', 'unknown')}]"
        )

    # Use V2 prompt for code selection (proven effective)
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


async def classify_dispute_v5_tot(
    task: Dict[str, Any],
    model: Optional[str] = None
) -> Dict[str, Any]:
    """Execute the CLASSIFY phase V5-ToT with Tree-of-Thought reasoning.

    Improvements over V4:
    - Tree-of-Thought with 3 independent analysis branches
    - Positive framing in prompts
    - Priority rules with explicit rationale
    - Conflict detection and resolution tracking
    - Confidence calibration with branch agreement

    Args:
        task: Task dictionary containing 'dispute_id' and 'description'.
        model: Optional model override. Defaults to V5_TOT_MODEL.

    Returns:
        Dictionary with classification results including branch analysis.

    Raises:
        TypeError: If task is not a dictionary.
        ValueError: If required fields are missing.
        RuntimeError: If classification fails.
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
        # Step 2: Network Identification
        target_network = task.get("network")
        if target_network:
            logger.info(f"Dispute {dispute_id}: Using pre-selected network {target_network}")
        else:
            target_network = _identify_network(description)
            logger.info(f"Dispute {dispute_id}: Identified network as {target_network}")

        # Step 3: Category Identification with V5-ToT
        category_result = await _identify_category_v5_tot(description, model=model)
        target_category = category_result.category
        logger.info(
            f"Dispute {dispute_id}: V5-ToT classified as {target_category} "
            f"(confidence: {category_result.confidence:.2f})"
        )

        # Step 4: Extract branch summary for downstream use
        branch_summary = extract_branch_summary(category_result)
        logger.info(f"Dispute {dispute_id}: Branch summary: {branch_summary}")

        # Step 5: Check for branch conflicts
        conflict = check_branch_conflict(category_result)
        if conflict:
            logger.info(f"Dispute {dispute_id}: Branch conflict detected: {conflict}")

        # Step 6: Code Selection
        catalog = get_reason_code_catalog()
        candidate_codes = catalog.get_codes_for_network_and_category(
            target_network, target_category
        )

        if not candidate_codes:
            logger.warning(
                f"No reason codes found for network {target_network} and "
                f"category {target_category}. Falling back to network-only search."
            )
            candidate_codes = catalog.get_codes_for_network(target_network)
            if not candidate_codes:
                raise ValueError(f"No reason codes found for network {target_network}")

        code_result = await _select_code(
            description,
            target_network,
            target_category,
            candidate_codes,
            branch_summary=branch_summary
        )
        logger.info(
            f"Dispute {dispute_id}: Selected code {code_result.reason_code} "
            f"(confidence: {code_result.confidence:.2f})"
        )

        # Step 7: Post-processing
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
            "is_fraud": is_fraud,
            "deadline": deadline,
            "classification_confidence": category_result.confidence,
            "code_selection_confidence": code_result.confidence,
            "classification_reasoning": category_result.synthesis.reasoning,
            "confidence_rationale": category_result.confidence_rationale,
            # V5-ToT specific fields
            "branch_a_conclusion": category_result.branch_a.conclusion,
            "branch_b_complaint": category_result.branch_b.complaint_type,
            "branch_c_persona": category_result.branch_c.persona,
            "branch_agreement": category_result.synthesis.branch_agreement,
            "priority_rule_applied": category_result.synthesis.priority_rule_applied,
            "branch_conflict": conflict,
            "classifier_version": "5.0.0-ToT",
            "model_used": model or V5_TOT_MODEL,
        }

    except Exception as e:
        logger.error(
            f"Classification V5-ToT phase failed for dispute {dispute_id}: {e}",
            exc_info=True
        )
        raise RuntimeError(
            f"Classification failed for dispute {dispute_id}: {str(e)}"
        ) from e
