"""HITLController - Human-in-the-Loop Controller for regulatory compliance.

This module implements Gap 6 from the Closing the Gaps framework,
providing tiered human oversight for multi-agent bank dispute systems.

Regulatory Requirements:
    - Federal Reserve SR 11-7: Evaluation, monitoring, outcomes analysis
    - EU AI Act Article 14: Four oversight models
    - Sardine AI Framework: Tiered oversight implementation

Oversight Tiers:
    - TIER_1_HIGH: Full HITL required (SAR filing, payment blocking)
    - TIER_2_MEDIUM: Sample-based review (fraud triage, KYC)
    - TIER_3_LOW: Logged only (knowledge search, status lookup)

Example:
    >>> controller = HITLController(confidence_threshold=0.85)
    >>> decision = controller.should_interrupt(
    ...     confidence=0.72,
    ...     amount=15000,
    ...     dispute_type="fraud"
    ... )
    >>> if decision.should_interrupt:
    ...     print(f"Human review required: {decision.reason}")
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class OversightTier(str, Enum):
    """Tiered oversight model per Sardine AI framework.

    Attributes:
        TIER_1_HIGH: Full HITL required for high-risk actions
        TIER_2_MEDIUM: Sample-based review for medium-risk actions
        TIER_3_LOW: Logged only for low-risk actions
    """

    TIER_1_HIGH = "tier_1"
    TIER_2_MEDIUM = "tier_2"
    TIER_3_LOW = "tier_3"


class InterruptDecision(BaseModel):
    """Result of HITL interrupt check.

    Attributes:
        should_interrupt: Whether human review is required
        reason: Human-readable reason for the decision
        tier: Oversight tier classification
        confidence: Model's confidence score that triggered decision
        amount: Dispute amount (if applicable)
        dispute_type: Type of dispute being processed
        timestamp: When the decision was made
        decision_id: Unique identifier for audit trail
    """

    should_interrupt: bool
    reason: str
    tier: OversightTier
    confidence: float = Field(ge=0.0, le=1.0)
    amount: float | None
    dispute_type: str
    timestamp: datetime
    decision_id: str


# Actions that always require Tier 1 (full HITL)
TIER_1_ACTIONS = frozenset(
    {
        "sar_filing",
        "payment_block",
        "account_close",
        "fraud_escalation",
    }
)

# Actions that are Tier 3 (logged only)
TIER_3_ACTIONS = frozenset(
    {
        "info_lookup",
        "status_lookup",
        "knowledge_search",
        "faq_response",
    }
)

# High-risk dispute types
HIGH_RISK_DISPUTE_TYPES = frozenset(
    {
        "fraud",
        "identity_theft",
        "money_laundering",
        "account_takeover",
    }
)


class HITLController:
    """Human-in-the-Loop Controller per Gap 6.

    Implements tiered oversight model for regulatory compliance:
        - Tier 1: SAR filing, payment blocking → Full HITL
        - Tier 2: Fraud triage, KYC → Sample-based review
        - Tier 3: Knowledge search → Logged only

    Attributes:
        _default_tier: Default oversight tier for unclassified actions
        _confidence_threshold: Below this, always interrupt
        _amount_threshold: Above this amount, always interrupt
        _log_to_db: Whether to log decisions to PostgreSQL
        _decision_stats: Running statistics on decisions

    Example:
        >>> controller = HITLController()
        >>> decision = controller.should_interrupt(
        ...     confidence=0.72,
        ...     amount=15000,
        ...     dispute_type="fraud"
        ... )
        >>> print(decision.tier)  # OversightTier.TIER_1_HIGH
    """

    def __init__(
        self,
        default_tier: OversightTier = OversightTier.TIER_2_MEDIUM,
        confidence_threshold: float = 0.85,
        amount_threshold: float = 10000.0,
        log_to_db: bool = True,
    ) -> None:
        """Initialize controller with configurable thresholds.

        Args:
            default_tier: Default oversight tier for unclassified actions
            confidence_threshold: Below this, always interrupt
            amount_threshold: Above this amount, always interrupt
            log_to_db: Log all decisions to PostgreSQL
        """
        self._default_tier = default_tier
        self._confidence_threshold = confidence_threshold
        self._amount_threshold = amount_threshold
        self._log_to_db = log_to_db

        # Statistics tracking
        self._decision_stats: dict[str, int] = {
            "total_decisions": 0,
            "tier_1_count": 0,
            "tier_2_count": 0,
            "tier_3_count": 0,
            "interrupts": 0,
            "auto_processed": 0,
        }

        # Review tracking (in production, this would be in database)
        self._pending_reviews: dict[str, dict[str, Any]] = {}

    def should_interrupt(
        self,
        confidence: float,
        amount: float | None = None,
        dispute_type: str = "general",
        action_type: str | None = None,
    ) -> InterruptDecision:
        """Determine if human review is required.

        Decision Logic:
            1. TIER 1 actions ALWAYS require human approval
            2. TIER 2 triggers on:
               - Confidence < threshold (default 0.85)
               - Amount > threshold (default $10,000)
               - Dispute type is high-risk (fraud, identity_theft)
            3. TIER 3 (logged only):
               - Knowledge base queries
               - Status lookups
               - Low-value disputes with high confidence

        Args:
            confidence: Model's confidence in decision (0.0-1.0)
            amount: Dispute amount in dollars (optional)
            dispute_type: Type of dispute (e.g., "fraud", "billing_error")
            action_type: Specific action being taken (e.g., "sar_filing")

        Returns:
            InterruptDecision with should_interrupt flag and reason

        Raises:
            TypeError: If confidence is not a float
            ValueError: If confidence not in [0.0, 1.0]
        """
        # Input validation
        if not isinstance(confidence, (int, float)):
            raise TypeError("confidence must be a float")

        confidence = float(confidence)

        if not (0.0 <= confidence <= 1.0):
            raise ValueError("confidence must be between 0.0 and 1.0")

        # Generate unique decision ID
        decision_id = str(uuid.uuid4())
        timestamp = datetime.now(UTC)

        # Get base tier classification
        tier = self.get_tier(dispute_type, action_type)

        # Possibly downgrade Tier 2 to Tier 3 for low-risk conditions
        if tier == OversightTier.TIER_2_MEDIUM:
            if self._should_downgrade_to_tier_3(confidence, amount, dispute_type):
                tier = OversightTier.TIER_3_LOW

        # Determine if we should interrupt based on tier and conditions
        should_interrupt, reason = self._evaluate_interrupt(
            tier=tier,
            confidence=confidence,
            amount=amount,
            dispute_type=dispute_type,
            action_type=action_type,
        )

        # Possibly upgrade tier based on conditions
        if should_interrupt and tier == OversightTier.TIER_2_MEDIUM:
            # Check if conditions warrant Tier 1 upgrade
            if self._should_upgrade_to_tier_1(confidence, amount, dispute_type):
                tier = OversightTier.TIER_1_HIGH
                reason = self._get_tier_1_upgrade_reason(confidence, amount, dispute_type)

        # Create decision
        decision = InterruptDecision(
            should_interrupt=should_interrupt,
            reason=reason,
            tier=tier,
            confidence=confidence,
            amount=amount,
            dispute_type=dispute_type,
            timestamp=timestamp,
            decision_id=decision_id,
        )

        # Update statistics
        self._update_stats(decision)

        # Log decision
        self._log_decision(decision)

        return decision

    def request_human_review(
        self,
        decision: InterruptDecision,
        context: dict[str, Any],
    ) -> str:
        """Create human review request and return review_id.

        Args:
            decision: The interrupt decision that triggered review
            context: Full context for human reviewer

        Returns:
            review_id (UUID) for tracking
        """
        review_id = str(uuid.uuid4())

        # Store review request (in production, this goes to database/queue)
        self._pending_reviews[review_id] = {
            "review_id": review_id,
            "decision_id": decision.decision_id,
            "created_at": datetime.now(UTC),
            "context": context,
            "status": "pending",
            "decision": decision.model_dump(),
        }

        return review_id

    def record_human_decision(
        self,
        review_id: str,
        approved: bool,
        reviewer_id: str,
        notes: str | None = None,
    ) -> None:
        """Record human reviewer's decision.

        Args:
            review_id: ID from request_human_review
            approved: Whether human approved the action
            reviewer_id: ID of human reviewer
            notes: Optional reviewer notes
        """
        if review_id in self._pending_reviews:
            self._pending_reviews[review_id].update(
                {
                    "status": "approved" if approved else "rejected",
                    "reviewed_at": datetime.now(UTC),
                    "approved": approved,
                    "reviewer_id": reviewer_id,
                    "notes": notes,
                }
            )

        # In production, this would update the database

    def get_tier(
        self, dispute_type: str, action_type: str | None = None
    ) -> OversightTier:
        """Classify action into oversight tier.

        Args:
            dispute_type: Type of dispute
            action_type: Specific action being taken

        Returns:
            OversightTier classification
        """
        # Tier 1: High-risk actions that always require human
        if action_type and action_type in TIER_1_ACTIONS:
            return OversightTier.TIER_1_HIGH

        # Tier 3: Low-risk actions that are logged only
        if action_type and action_type in TIER_3_ACTIONS:
            return OversightTier.TIER_3_LOW

        # Default to configured tier
        return self._default_tier

    def get_escalation_stats(self) -> dict[str, Any]:
        """Get statistics on escalation rates by tier.

        Returns:
            Dictionary with escalation statistics
        """
        stats = self._decision_stats.copy()

        # Calculate rates
        total = stats["total_decisions"]
        if total > 0:
            stats["tier_counts"] = {
                "tier_1": stats["tier_1_count"],
                "tier_2": stats["tier_2_count"],
                "tier_3": stats["tier_3_count"],
            }
            stats["interrupt_rate"] = stats["interrupts"] / total
            stats["auto_process_rate"] = stats["auto_processed"] / total

        return stats

    def _evaluate_interrupt(
        self,
        tier: OversightTier,
        confidence: float,
        amount: float | None,
        dispute_type: str,
        action_type: str | None,
    ) -> tuple[bool, str]:
        """Evaluate whether to interrupt based on conditions.

        Returns:
            (should_interrupt, reason) tuple
        """
        # Tier 1 always interrupts
        if tier == OversightTier.TIER_1_HIGH:
            reason = f"Tier 1 action ({action_type or dispute_type}) requires human approval"
            return True, reason

        # Tier 3 never interrupts (just logged)
        if tier == OversightTier.TIER_3_LOW:
            return False, "Automated processing allowed - Tier 3 logged only"

        # Tier 2: Evaluate conditions
        reasons = []

        # Low confidence triggers interrupt
        if confidence < self._confidence_threshold:
            reasons.append(f"Confidence {confidence:.2f} below threshold {self._confidence_threshold}")

        # High amount triggers interrupt
        if amount is not None and amount > self._amount_threshold:
            reasons.append(f"Amount ${amount:,.2f} exceeds threshold ${self._amount_threshold:,.2f}")

        # High-risk dispute type triggers interrupt
        if dispute_type in HIGH_RISK_DISPUTE_TYPES:
            reasons.append(f"High-risk dispute type: {dispute_type}")

        if reasons:
            return True, "; ".join(reasons)

        return False, "Automated processing allowed"

    def _should_downgrade_to_tier_3(
        self,
        confidence: float,
        amount: float | None,
        dispute_type: str,
    ) -> bool:
        """Check if conditions allow downgrading to Tier 3.

        Tier 3 conditions:
            - High confidence (>= threshold)
            - Low amount (< threshold or None)
            - Low-risk dispute type
        """
        # Must have high confidence
        if confidence < self._confidence_threshold:
            return False

        # Amount must be below threshold (or None for non-financial)
        if amount is not None and amount >= self._amount_threshold:
            return False

        # Must not be high-risk dispute type
        if dispute_type in HIGH_RISK_DISPUTE_TYPES:
            return False

        return True

    def _should_upgrade_to_tier_1(
        self,
        confidence: float,
        amount: float | None,
        dispute_type: str,
    ) -> bool:
        """Check if conditions warrant upgrading to Tier 1.

        Tier 1 upgrade conditions:
            - High-value fraud with low confidence
            - Identity theft with any concerning factor
        """
        # High-value fraud with low confidence
        if dispute_type == "fraud":
            if amount is not None and amount > self._amount_threshold:
                if confidence < self._confidence_threshold:
                    return True

        # Identity theft always warrants Tier 1
        if dispute_type == "identity_theft":
            return True

        return False

    def _get_tier_1_upgrade_reason(
        self,
        confidence: float,
        amount: float | None,
        dispute_type: str,
    ) -> str:
        """Get reason for Tier 1 upgrade."""
        if dispute_type == "identity_theft":
            return "Identity theft requires Tier 1 review"

        if dispute_type == "fraud" and amount and amount > self._amount_threshold:
            return f"High-value fraud (${amount:,.2f}) with confidence {confidence:.2f} requires Tier 1 review"

        return "Conditions warrant Tier 1 human review"

    def _update_stats(self, decision: InterruptDecision) -> None:
        """Update internal statistics."""
        self._decision_stats["total_decisions"] += 1

        if decision.tier == OversightTier.TIER_1_HIGH:
            self._decision_stats["tier_1_count"] += 1
        elif decision.tier == OversightTier.TIER_2_MEDIUM:
            self._decision_stats["tier_2_count"] += 1
        else:
            self._decision_stats["tier_3_count"] += 1

        if decision.should_interrupt:
            self._decision_stats["interrupts"] += 1
        else:
            self._decision_stats["auto_processed"] += 1

    def _log_decision(self, decision: InterruptDecision) -> None:
        """Log decision to database.

        Args:
            decision: Decision to log
        """
        if not self._log_to_db:
            return

        # In production, this would write to PostgreSQL
        _log_data = {
            "decision_id": decision.decision_id,
            "timestamp": decision.timestamp.isoformat(),
            "should_interrupt": decision.should_interrupt,
            "reason": decision.reason,
            "tier": decision.tier.value,
            "confidence": decision.confidence,
            "amount": decision.amount,
            "dispute_type": decision.dispute_type,
        }
        # TODO: Async write to PostgreSQL

