"""CLASSIFY Phase Handler V8-RAG.

Enhanced classification combining V7-Hybrid logic with RAG-based precedents:
- Retrieves semantically similar historical disputes
- Injects validated precedents into the prompt context
- Uses 'Stripe-inspired' pattern matching to resolve ambiguity

Version: 8.0.0
"""

from __future__ import annotations

import datetime
import logging
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, field_validator

from utils.llm_service import get_default_service
from utils.prompt_service import render_prompt
from backend.adapters.reason_code_catalog import get_reason_code_catalog
# Import RagRetriever lazily or at module level? Module level is fine if we use lazy init function.

logger = logging.getLogger(__name__)

# Default model for V8-RAG
V8_RAG_MODEL = "openai/gpt-4o"

# Global retriever instance
_RAG_RETRIEVER = None

def get_rag_retriever():
    """Get or initialize the global RagRetriever instance."""
    global _RAG_RETRIEVER
    if _RAG_RETRIEVER is None:
        # Hard stop if initialization fails
        from backend.adapters.rag_retriever import RagRetriever
        _RAG_RETRIEVER = RagRetriever()
    return _RAG_RETRIEVER


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
        allowed = {"acknowledged", "denied", "unclear"}
        if v.lower() not in allowed:
            raise ValueError(f"Branch A conclusion must be one of {allowed}, got: {v}")
        return v.lower()


class BranchBResult(BaseModel):
    """Branch B: Complaint Specifics Analysis."""

    complaint_type: str = Field(
        description="Type of complaint: amount, quality, processing, delivery, or unspecified"
    )
    evidence: List[str] = Field(
        default_factory=list,
        description="Specific phrases indicating the complaint type"
    )

    @field_validator("complaint_type")
    @classmethod
    def validate_complaint_type(cls, v: str) -> str:
        allowed = {"amount", "quality", "processing", "delivery", "unspecified"}
        v_norm = v.lower().strip()
        
        aliases = {
            "discrepancy": "amount",
            "billing_error": "amount",
            "refund": "processing",
            "fraud": "unspecified",
            "unauthorized": "unspecified",
            "duplicate": "processing",
            "non_receipt": "delivery",
            "not_received": "delivery",
            "missing": "delivery",
        }
        
        v_norm = aliases.get(v_norm, v_norm)
        
        if v_norm not in allowed:
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
        allowed = {"frustrated", "confused", "accusatory", "neutral"}
        v_norm = v.lower().strip()
        
        aliases = {
            "concerned": "neutral",
            "worried": "neutral",
            "angry": "frustrated",
            "upset": "frustrated",
            "annoyed": "frustrated"
        }
        
        v_norm = aliases.get(v_norm, v_norm)
        
        if v_norm not in allowed:
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


class CategoryResultV8Rag(BaseModel):
    """Structured output for V8 RAG category identification."""

    branch_a: BranchAResult = Field(description="Transaction acknowledgment analysis")
    branch_b: BranchBResult = Field(description="Complaint specifics analysis")
    branch_c: BranchCResult = Field(description="User persona analysis")
    
    synthesis: SynthesisResult = Field(description="Branch synthesis and priority rules")
    
    category: str = Field(description="Selected standardized category")
    reason_code_group: str = Field(description="Mapped reason code group for network routing")
    confidence: float = Field(
        ge=0.0,
        le=1.0,
        description="Confidence score"
    )
    confidence_rationale: str = Field(description="Explanation for confidence level")

    @field_validator("category")
    @classmethod
    def validate_category(cls, v: str) -> str:
        allowed = {
            "fraudulent", "general", "product_not_received", "duplicate",
            "subscription_canceled", "product_unacceptable", "credit_not_processed",
            "unrecognized"
        }
        v_norm = v.lower().strip().replace(" ", "_").replace("-", "_")
        
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

    @field_validator("reason_code_group")
    @classmethod
    def validate_reason_code_group(cls, v: str) -> str:
        allowed = {
            "fraud", "authorization", "processing_errors",
            "cardholder_disputes", "consumer_disputes"
        }
        v_norm = v.lower().strip().replace(" ", "_").replace("-", "_")
        
        aliases = {
            "fraudulent": "fraud",
            "auth": "authorization",
            "processing": "processing_errors",
            "cardholder": "cardholder_disputes",
            "consumer": "consumer_disputes",
        }
        
        v_norm = aliases.get(v_norm, v_norm)
        
        if v_norm not in allowed:
            logger.warning(f"Invalid reason_code_group '{v}', defaulting to 'cardholder_disputes'")
            return "cardholder_disputes"
        return v_norm


class CodeSelectionResult(BaseModel):
    """Structured output for reason code selection."""
    reason_code: str
    confidence: float
    reasoning: str


def _identify_network(description: str) -> str:
    """Identify payment network from description."""
    if not isinstance(description, str):
        return "visa"
    desc_lower = description.lower()
    if "amex" in desc_lower or "american express" in desc_lower: return "amex"
    if "mastercard" in desc_lower: return "mastercard"
    if "discover" in desc_lower: return "discover"
    if "visa" in desc_lower: return "visa"
    if "paypal" in desc_lower: return "paypal"
    return "visa"


def extract_branch_summary(result: CategoryResultV8Rag) -> Dict[str, str]:
    """Extract summary for logging."""
    return {
        "branch_a_conclusion": result.branch_a.conclusion,
        "branch_b_complaint": result.branch_b.complaint_type,
        "branch_c_persona": result.branch_c.persona,
        "branch_agreement": str(result.synthesis.branch_agreement),
        "priority_rule": result.synthesis.priority_rule_applied or "none",
        "reason_code_group": result.reason_code_group,
    }


def check_branch_conflict(result: CategoryResultV8Rag) -> Optional[Dict[str, Any]]:
    """Check for conflicting signals."""
    if (result.branch_a.conclusion == "denied" and result.branch_b.complaint_type == "amount"):
        return {"type": "denial_with_amount", "resolution": "amount_overrides_denial"}
    if (result.branch_a.conclusion == "unclear" and result.branch_c.persona == "accusatory"):
        return {"type": "unclear_with_accusatory", "resolution": "needs_persona_tiebreaker"}
    if (result.branch_b.complaint_type == "delivery" and result.branch_a.conclusion == "unclear"):
        return {"type": "delivery_with_unclear_acknowledgment", "resolution": "delivery_implies_purchase"}
    return None


async def _identify_category_v8_rag(
    description: str,
    model: Optional[str] = None
) -> CategoryResultV8Rag:
    """Identify category using V8 RAG prompt."""
    if not isinstance(description, str) or not description.strip():
        raise ValueError("Invalid description")

    service = get_default_service()
    
    # Retrieve similar examples
    examples = []
    retriever = get_rag_retriever()
    if retriever:
        # Hard stop if retrieval fails
        matches = retriever.retrieve_similar(description, k=3, threshold=0.4)
        examples = matches
        logger.info(f"Retrieved {len(examples)} examples for RAG.")
    
    prompt = render_prompt(
        "DisputeClassifier_identify_category_v8_rag.j2",
        description=description,
        examples=examples
    )

    target_model = model or V8_RAG_MODEL

    return await service.complete_structured(
        messages=[{"role": "user", "content": prompt}],
        response_model=CategoryResultV8Rag,
        model=target_model
    )


async def _select_code(
    description: str,
    network: str,
    category: str,
    candidate_codes: List[Dict[str, str]],
    branch_summary: Optional[Dict[str, str]] = None
) -> CodeSelectionResult:
    """Select specific reason code."""
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

    # Use V2 selection prompt as V8 doesn't change selection logic, only category logic
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


async def classify_dispute_v8_rag(
    task: Dict[str, Any],
    model: Optional[str] = None
) -> Dict[str, Any]:
    """Execute the CLASSIFY phase V8-RAG."""
    if not isinstance(task, dict): raise TypeError("task must be a dictionary")
    dispute_id = task.get("dispute_id")
    description = task.get("description")
    if not dispute_id or not description: raise ValueError("Missing dispute_id or description")

    try:
        # Network ID
        target_network = task.get("network") or _identify_network(description)
        
        # Category ID (V8 RAG)
        category_result = await _identify_category_v8_rag(description, model=model)
        target_category = category_result.category
        reason_code_group = category_result.reason_code_group
        
        logger.info(f"Dispute {dispute_id}: V8-RAG classified as {target_category} (conf: {category_result.confidence:.2f})")

        # Branch Summary & Conflicts
        branch_summary = extract_branch_summary(category_result)
        conflict = check_branch_conflict(category_result)
        
        # Code Selection
        catalog = get_reason_code_catalog()
        candidate_codes = catalog.get_codes_for_network_and_category(target_network, target_category)
        
        if not candidate_codes:
            candidate_codes = catalog.get_codes_for_network(target_network)
            if not candidate_codes: raise ValueError(f"No codes for network {target_network}")

        code_result = await _select_code(
            description, target_network, target_category, candidate_codes, branch_summary
        )

        # Post-processing
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
            "reason_code_group": reason_code_group,
            "is_fraud": is_fraud,
            "deadline": deadline,
            "classification_confidence": category_result.confidence,
            "code_selection_confidence": code_result.confidence,
            "classification_reasoning": category_result.synthesis.reasoning,
            "confidence_rationale": category_result.confidence_rationale,
            # V8 specific
            "branch_a_conclusion": category_result.branch_a.conclusion,
            "branch_b_complaint": category_result.branch_b.complaint_type,
            "branch_c_persona": category_result.branch_c.persona,
            "branch_agreement": category_result.synthesis.branch_agreement,
            "priority_rule_applied": category_result.synthesis.priority_rule_applied,
            "branch_conflict": conflict,
            "classifier_version": "8.0.0-RAG",
            "model_used": model or V8_RAG_MODEL,
        }

    except Exception as e:
        logger.error(f"Classification V8-RAG phase failed for dispute {dispute_id}: {e}", exc_info=True)
        raise RuntimeError(f"Classification failed: {str(e)}") from e

