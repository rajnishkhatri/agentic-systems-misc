"""CLASSIFY Phase Handler V9-RAG.

Enhanced classification with improved observability, resilience, and confidence calibration:
- Configurable RAG feature flags via environment variables
- Graceful fallback when vector store is missing
- RAGMetrics dataclass for observability
- Confidence calibration based on precedent agreement
- Precedent diversity check with warnings

Version: 9.0.0
"""

from __future__ import annotations

import datetime
import logging
import os
import time
from typing import Any, Dict, List, Optional, Tuple

from pydantic import BaseModel, Field, field_validator

from backend.adapters.reason_code_catalog import get_reason_code_catalog
from utils.llm_service import get_default_service
from utils.prompt_service import render_prompt

logger = logging.getLogger(__name__)

# =============================================================================
# Phase 1: Feature Flags & Configuration
# =============================================================================

RAG_ENABLED = os.getenv("CLASSIFY_RAG_ENABLED", "true").lower() == "true"
RAG_TOP_K = int(os.getenv("CLASSIFY_RAG_TOP_K", "3"))
RAG_SIMILARITY_THRESHOLD = float(os.getenv("CLASSIFY_RAG_THRESHOLD", "0.4"))
RAG_HIGH_CONFIDENCE_THRESHOLD = float(os.getenv("CLASSIFY_RAG_HIGH_CONFIDENCE", "0.85"))

# Default model for V9-RAG
V9_RAG_MODEL = "openai/gpt-4o"

# Global retriever instance
_RAG_RETRIEVER = None


def get_rag_retriever():
    """Get or initialize the global RagRetriever instance."""
    global _RAG_RETRIEVER
    if _RAG_RETRIEVER is None:
        from backend.adapters.rag_retriever import RagRetriever
        _RAG_RETRIEVER = RagRetriever()
    return _RAG_RETRIEVER


def get_rag_retriever_safe() -> Optional[Any]:
    """Get retriever with graceful fallback.

    Returns:
        RagRetriever instance or None if unavailable/disabled.
    """
    if not RAG_ENABLED:
        logger.info("RAG disabled via CLASSIFY_RAG_ENABLED=false")
        return None
    try:
        return get_rag_retriever()
    except FileNotFoundError as e:
        logger.warning(f"RAG unavailable (vector store missing): {e}")
        return None
    except Exception as e:
        logger.error(f"RAG initialization failed: {e}")
        return None


# =============================================================================
# Phase 2: RAG Metrics & Observability
# =============================================================================

class RAGMetrics(BaseModel):
    """Metrics about RAG retrieval for observability."""

    enabled: bool = Field(default=False, description="Whether RAG was enabled")
    precedents_retrieved: int = Field(default=0, description="Number of precedents found")
    top_similarity: float = Field(default=0.0, description="Highest similarity score")
    avg_similarity: float = Field(default=0.0, description="Average similarity of retrieved")
    precedent_categories: List[str] = Field(default_factory=list, description="Categories from precedents")
    retrieval_time_ms: float = Field(default=0.0, description="Time spent in retrieval")
    high_confidence_match: bool = Field(default=False, description="Has match above high threshold")


def build_rag_metrics(
    examples: List[Dict[str, Any]],
    retrieval_time_ms: float,
    rag_enabled: bool,
    high_confidence_threshold: float = RAG_HIGH_CONFIDENCE_THRESHOLD,
) -> RAGMetrics:
    """Build RAGMetrics from retrieved examples.

    Args:
        examples: List of retrieved examples with similarity_score and category
        retrieval_time_ms: Time spent in retrieval
        rag_enabled: Whether RAG was enabled
        high_confidence_threshold: Threshold for high confidence match

    Returns:
        RAGMetrics with computed aggregates
    """
    if not examples:
        return RAGMetrics(
            enabled=rag_enabled,
            precedents_retrieved=0,
            retrieval_time_ms=retrieval_time_ms,
        )

    similarities = [e.get("similarity_score", 0.0) for e in examples]
    categories = [e.get("category", "unknown") for e in examples]

    top_sim = max(similarities) if similarities else 0.0
    avg_sim = sum(similarities) / len(similarities) if similarities else 0.0

    return RAGMetrics(
        enabled=rag_enabled,
        precedents_retrieved=len(examples),
        top_similarity=top_sim,
        avg_similarity=avg_sim,
        precedent_categories=categories,
        retrieval_time_ms=retrieval_time_ms,
        high_confidence_match=top_sim >= high_confidence_threshold,
    )


# =============================================================================
# Phase 3: Confidence Calibration
# =============================================================================

def calibrate_confidence(
    base_confidence: float,
    rag_metrics: RAGMetrics,
    precedent_agreement: bool,
) -> Tuple[float, str]:
    """Calibrate confidence based on RAG signals.

    Args:
        base_confidence: Original confidence from classifier
        rag_metrics: Metrics from RAG retrieval
        precedent_agreement: Whether output matches top precedent's category

    Returns:
        Tuple of (adjusted_confidence, adjustment_reason)
    """
    if not rag_metrics.enabled or rag_metrics.precedents_retrieved == 0:
        return base_confidence, "No adjustment"

    adjustment = 0.0
    reasons = []

    # Boost for high-similarity precedent agreement
    if rag_metrics.high_confidence_match and precedent_agreement:
        adjustment += 0.05
        reasons.append("+0.05: High-similarity precedent agrees")

    # Penalty for high-similarity precedent disagreement
    if rag_metrics.high_confidence_match and not precedent_agreement:
        adjustment -= 0.10
        reasons.append("-0.10: High-similarity precedent disagrees (review recommended)")

    # Boost for precedent consensus (all same category, 2+ precedents)
    if len(set(rag_metrics.precedent_categories)) == 1 and rag_metrics.precedents_retrieved >= 2:
        if not rag_metrics.high_confidence_match:  # Don't double-count
            adjustment += 0.03
            reasons.append("+0.03: All precedents agree on category")

    adjusted = min(1.0, max(0.0, base_confidence + adjustment))
    return adjusted, "; ".join(reasons) if reasons else "No adjustment"


# =============================================================================
# Phase 4: Precedent Diversity Check
# =============================================================================

def check_precedent_diversity(examples: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Check if precedents are diverse or potentially biased.

    Args:
        examples: List of retrieved examples

    Returns:
        Dict with is_diverse, unique_categories, similarity_spread, and warning
    """
    if len(examples) < 2:
        return {
            "is_diverse": True,
            "unique_categories": len(examples),
            "similarity_spread": 0.0,
            "warning": None,
        }

    categories = [e.get("category", "unknown") for e in examples]
    unique = set(categories)

    similarities = [e.get("similarity_score", 0.0) for e in examples]
    spread = max(similarities) - min(similarities) if similarities else 0.0

    warning = None
    is_diverse = len(unique) > 1 or spread >= 0.1

    if len(unique) == 1 and spread < 0.1:
        warning = "All precedents similar and same category - potential bias"

    return {
        "is_diverse": is_diverse,
        "unique_categories": len(unique),
        "similarity_spread": round(spread, 2),
        "warning": warning,
    }


# =============================================================================
# Pydantic Models (from V8, with V9 extensions)
# =============================================================================

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


class CategoryResultV9Rag(BaseModel):
    """Structured output for V9 RAG category identification."""

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

    # V9 additions
    precedent_override_applied: Optional[bool] = Field(
        default=None,
        description="Whether a precedent override was applied"
    )
    precedent_disagreement_note: Optional[str] = Field(
        default=None,
        description="Note if classifier disagreed with precedent"
    )

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


# =============================================================================
# Helper Functions
# =============================================================================

def _identify_network(description: str) -> str:
    """Identify payment network from description."""
    if not isinstance(description, str):
        return "visa"
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


def extract_branch_summary(result: CategoryResultV9Rag) -> Dict[str, str]:
    """Extract summary for logging."""
    return {
        "branch_a_conclusion": result.branch_a.conclusion,
        "branch_b_complaint": result.branch_b.complaint_type,
        "branch_c_persona": result.branch_c.persona,
        "branch_agreement": str(result.synthesis.branch_agreement),
        "priority_rule": result.synthesis.priority_rule_applied or "none",
        "reason_code_group": result.reason_code_group,
    }


def check_branch_conflict(result: CategoryResultV9Rag) -> Optional[Dict[str, Any]]:
    """Check for conflicting signals."""
    if result.branch_a.conclusion == "denied" and result.branch_b.complaint_type == "amount":
        return {"type": "denial_with_amount", "resolution": "amount_overrides_denial"}
    if result.branch_a.conclusion == "unclear" and result.branch_c.persona == "accusatory":
        return {"type": "unclear_with_accusatory", "resolution": "needs_persona_tiebreaker"}
    if result.branch_b.complaint_type == "delivery" and result.branch_a.conclusion == "unclear":
        return {"type": "delivery_with_unclear_acknowledgment", "resolution": "delivery_implies_purchase"}
    return None


# =============================================================================
# Core Classification Functions
# =============================================================================

async def _identify_category_v9_rag(
    description: str,
    examples: List[Dict[str, Any]],
    diversity_info: Dict[str, Any],
    model: Optional[str] = None
) -> CategoryResultV9Rag:
    """Identify category using V9 RAG prompt."""
    if not isinstance(description, str) or not description.strip():
        raise ValueError("Invalid description")

    service = get_default_service()

    prompt = render_prompt(
        "DisputeClassifier_identify_category_v9_rag.j2",
        description=description,
        examples=examples,
        diversity_warning=diversity_info.get("warning"),
    )

    target_model = model or V9_RAG_MODEL

    return await service.complete_structured(
        messages=[{"role": "user", "content": prompt}],
        response_model=CategoryResultV9Rag,
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


# =============================================================================
# Main Entry Point
# =============================================================================

async def classify_dispute_v9_rag(
    task: Dict[str, Any],
    model: Optional[str] = None
) -> Dict[str, Any]:
    """Execute the CLASSIFY phase V9-RAG.

    Args:
        task: Dictionary with dispute_id, description, and optional fields
        model: Optional model override

    Returns:
        Classification result with RAG metrics, confidence calibration, etc.

    Raises:
        TypeError: If task is not a dictionary
        ValueError: If required fields are missing
        RuntimeError: If classification fails
    """
    if not isinstance(task, dict):
        raise TypeError("task must be a dictionary")

    dispute_id = task.get("dispute_id")
    description = task.get("description")

    if not dispute_id or not description:
        raise ValueError("Missing dispute_id or description")

    try:
        # Network identification
        target_network = task.get("network") or _identify_network(description)

        # RAG retrieval with timing
        examples: List[Dict[str, Any]] = []
        retrieval_start = time.perf_counter()

        retriever = get_rag_retriever_safe()
        if retriever:
            matches = retriever.retrieve_similar(
                description,
                k=RAG_TOP_K,
                threshold=RAG_SIMILARITY_THRESHOLD
            )
            examples = matches
            logger.info(f"Retrieved {len(examples)} examples for RAG.")

        retrieval_time_ms = (time.perf_counter() - retrieval_start) * 1000

        # Build RAG metrics
        rag_metrics = build_rag_metrics(
            examples=examples,
            retrieval_time_ms=retrieval_time_ms,
            rag_enabled=RAG_ENABLED and retriever is not None,
            high_confidence_threshold=RAG_HIGH_CONFIDENCE_THRESHOLD,
        )

        # Check precedent diversity
        diversity_info = check_precedent_diversity(examples)

        # Category identification (V9 RAG)
        category_result = await _identify_category_v9_rag(
            description, examples, diversity_info, model=model
        )
        target_category = category_result.category
        reason_code_group = category_result.reason_code_group

        logger.info(
            f"Dispute {dispute_id}: V9-RAG classified as {target_category} "
            f"(conf: {category_result.confidence:.2f})"
        )

        # Confidence calibration
        precedent_agreement = False
        if rag_metrics.precedent_categories:
            top_precedent_category = rag_metrics.precedent_categories[0]
            precedent_agreement = target_category == top_precedent_category

        adjusted_confidence, adjustment_reason = calibrate_confidence(
            base_confidence=category_result.confidence,
            rag_metrics=rag_metrics,
            precedent_agreement=precedent_agreement,
        )

        confidence_adjustment = adjusted_confidence - category_result.confidence

        # Branch Summary & Conflicts
        branch_summary = extract_branch_summary(category_result)
        conflict = check_branch_conflict(category_result)

        # Code Selection
        catalog = get_reason_code_catalog()
        candidate_codes = catalog.get_codes_for_network_and_category(target_network, target_category)

        if not candidate_codes:
            candidate_codes = catalog.get_codes_for_network(target_network)
            if not candidate_codes:
                raise ValueError(f"No codes for network {target_network}")

        code_result = await _select_code(
            description, target_network, target_category, candidate_codes, branch_summary
        )

        # Post-processing: deadline calculation
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
            "classification_confidence": adjusted_confidence,
            "original_confidence": category_result.confidence,
            "confidence_adjustment": round(confidence_adjustment, 3),
            "confidence_adjustment_reason": adjustment_reason,
            "code_selection_confidence": code_result.confidence,
            "classification_reasoning": category_result.synthesis.reasoning,
            "confidence_rationale": category_result.confidence_rationale,
            # V9 specific
            "branch_a_conclusion": category_result.branch_a.conclusion,
            "branch_b_complaint": category_result.branch_b.complaint_type,
            "branch_c_persona": category_result.branch_c.persona,
            "branch_agreement": category_result.synthesis.branch_agreement,
            "priority_rule_applied": category_result.synthesis.priority_rule_applied,
            "branch_conflict": conflict,
            # RAG observability
            "rag_metrics": rag_metrics.model_dump(),
            "precedent_diversity": diversity_info,
            "precedent_agreement": precedent_agreement,
            # Metadata
            "classifier_version": "9.0.0-RAG",
            "model_used": model or V9_RAG_MODEL,
        }

    except Exception as e:
        logger.error(
            f"Classification V9-RAG phase failed for dispute {dispute_id}: {e}",
            exc_info=True
        )
        raise RuntimeError(f"Classification failed: {str(e)}") from e
