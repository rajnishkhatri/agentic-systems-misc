"""TDD Tests for HITLController (RED → GREEN → REFACTOR).

Tests cover:
    - OversightTier enum validation
    - InterruptDecision model validation
    - Tier 1 classification (always interrupt)
    - Tier 2 classification (conditional interrupt)
    - Tier 3 classification (logged only)
    - Human review request workflow
    - Input validation and error handling
"""

from __future__ import annotations

import sys
import uuid
from datetime import datetime
from pathlib import Path

import pytest

# Add the closing_the_gaps package to the path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from closing_the_gaps.governance.hitl_controller import (
    HITLController,
    InterruptDecision,
    OversightTier,
)


class TestOversightTierEnum:
    """Tests for OversightTier enum."""

    def test_should_have_three_tiers(self) -> None:
        """Test that OversightTier has exactly three tiers."""
        assert len(OversightTier) == 3

    def test_should_define_tier_1_high(self) -> None:
        """Test TIER_1_HIGH is defined for high-risk actions."""
        assert OversightTier.TIER_1_HIGH.value == "tier_1"

    def test_should_define_tier_2_medium(self) -> None:
        """Test TIER_2_MEDIUM is defined for sample-based review."""
        assert OversightTier.TIER_2_MEDIUM.value == "tier_2"

    def test_should_define_tier_3_low(self) -> None:
        """Test TIER_3_LOW is defined for logged-only actions."""
        assert OversightTier.TIER_3_LOW.value == "tier_3"


class TestInterruptDecisionModel:
    """Tests for InterruptDecision Pydantic model."""

    def test_should_create_interrupt_decision_with_required_fields(self) -> None:
        """Test InterruptDecision creation with all required fields."""
        decision = InterruptDecision(
            should_interrupt=True,
            reason="Tier 1 action requires human approval",
            tier=OversightTier.TIER_1_HIGH,
            confidence=0.72,
            amount=15000.0,
            dispute_type="fraud",
            timestamp=datetime.now(),
            decision_id=str(uuid.uuid4()),
        )

        assert decision.should_interrupt is True
        assert decision.tier == OversightTier.TIER_1_HIGH
        assert decision.amount == 15000.0

    def test_should_create_non_interrupt_decision(self) -> None:
        """Test InterruptDecision for automatic processing."""
        decision = InterruptDecision(
            should_interrupt=False,
            reason="Automated processing allowed",
            tier=OversightTier.TIER_3_LOW,
            confidence=0.95,
            amount=50.0,
            dispute_type="billing_error",
            timestamp=datetime.now(),
            decision_id=str(uuid.uuid4()),
        )

        assert decision.should_interrupt is False
        assert decision.tier == OversightTier.TIER_3_LOW

    def test_should_validate_confidence_range(self) -> None:
        """Test that confidence must be between 0.0 and 1.0."""
        from pydantic import ValidationError

        with pytest.raises(ValidationError):
            InterruptDecision(
                should_interrupt=True,
                reason="Test",
                tier=OversightTier.TIER_1_HIGH,
                confidence=1.5,  # Invalid: > 1.0
                amount=100.0,
                dispute_type="test",
                timestamp=datetime.now(),
                decision_id=str(uuid.uuid4()),
            )


class TestHITLControllerInitialization:
    """Tests for HITLController initialization."""

    def test_should_initialize_with_default_config(self) -> None:
        """Test initialization with default values."""
        controller = HITLController()

        assert controller._default_tier == OversightTier.TIER_2_MEDIUM
        assert controller._confidence_threshold == 0.85
        assert controller._amount_threshold == 10000.0

    def test_should_initialize_with_custom_thresholds(self) -> None:
        """Test initialization with custom thresholds."""
        controller = HITLController(
            default_tier=OversightTier.TIER_1_HIGH,
            confidence_threshold=0.90,
            amount_threshold=5000.0,
            log_to_db=False,
        )

        assert controller._default_tier == OversightTier.TIER_1_HIGH
        assert controller._confidence_threshold == 0.90
        assert controller._amount_threshold == 5000.0


class TestTier1Classification:
    """Tests for Tier 1 (always interrupt) classification."""

    def test_should_interrupt_for_sar_filing(self) -> None:
        """Test that SAR filing always requires human approval."""
        controller = HITLController()

        decision = controller.should_interrupt(
            confidence=0.99,  # Even high confidence
            amount=100.0,  # Even low amount
            dispute_type="fraud",
            action_type="sar_filing",
        )

        assert decision.should_interrupt is True
        assert decision.tier == OversightTier.TIER_1_HIGH
        assert "tier_1" in decision.reason.lower() or "sar" in decision.reason.lower()

    def test_should_interrupt_for_payment_block(self) -> None:
        """Test that payment blocking always requires human approval."""
        controller = HITLController()

        decision = controller.should_interrupt(
            confidence=0.99,
            amount=50.0,
            dispute_type="billing_error",
            action_type="payment_block",
        )

        assert decision.should_interrupt is True
        assert decision.tier == OversightTier.TIER_1_HIGH

    def test_should_interrupt_for_account_close(self) -> None:
        """Test that account closure always requires human approval."""
        controller = HITLController()

        decision = controller.should_interrupt(
            confidence=0.99,
            amount=0.0,
            dispute_type="general",
            action_type="account_close",
        )

        assert decision.should_interrupt is True
        assert decision.tier == OversightTier.TIER_1_HIGH

    def test_should_interrupt_for_high_value_fraud_low_confidence(self) -> None:
        """Test Tier 1 for high-value fraud with low confidence."""
        controller = HITLController()

        decision = controller.should_interrupt(
            confidence=0.72,  # Below threshold
            amount=15000.0,  # Above threshold
            dispute_type="fraud",
            action_type="refund_approve",
        )

        assert decision.should_interrupt is True
        assert decision.tier == OversightTier.TIER_1_HIGH


class TestTier2Classification:
    """Tests for Tier 2 (conditional interrupt) classification."""

    def test_should_interrupt_for_low_confidence(self) -> None:
        """Test interrupt triggered by confidence below threshold."""
        controller = HITLController(confidence_threshold=0.85)

        decision = controller.should_interrupt(
            confidence=0.72,  # Below 0.85
            amount=500.0,  # Below threshold
            dispute_type="billing_error",
        )

        assert decision.should_interrupt is True
        assert decision.tier == OversightTier.TIER_2_MEDIUM
        assert "confidence" in decision.reason.lower()

    def test_should_interrupt_for_high_amount(self) -> None:
        """Test interrupt triggered by amount above threshold."""
        controller = HITLController(amount_threshold=10000.0)

        decision = controller.should_interrupt(
            confidence=0.90,  # Above threshold
            amount=15000.0,  # Above 10000
            dispute_type="billing_error",
        )

        assert decision.should_interrupt is True
        assert decision.tier == OversightTier.TIER_2_MEDIUM
        assert "amount" in decision.reason.lower()

    def test_should_interrupt_for_fraud_dispute_type(self) -> None:
        """Test interrupt triggered by high-risk dispute type."""
        controller = HITLController()

        decision = controller.should_interrupt(
            confidence=0.90,  # Above threshold
            amount=500.0,  # Below threshold
            dispute_type="fraud",
        )

        # Fraud with high confidence might still be Tier 2
        assert decision.tier in [OversightTier.TIER_2_MEDIUM, OversightTier.TIER_3_LOW]

    def test_should_interrupt_for_identity_theft(self) -> None:
        """Test interrupt for identity theft disputes."""
        controller = HITLController()

        decision = controller.should_interrupt(
            confidence=0.88,
            amount=1000.0,
            dispute_type="identity_theft",
        )

        # Identity theft should trigger review
        assert decision.should_interrupt is True


class TestTier3Classification:
    """Tests for Tier 3 (logged only) classification."""

    def test_should_not_interrupt_for_info_lookup(self) -> None:
        """Test that info lookup is logged only, no interrupt."""
        controller = HITLController()

        decision = controller.should_interrupt(
            confidence=0.95,
            amount=None,
            dispute_type="general",
            action_type="info_lookup",
        )

        assert decision.should_interrupt is False
        assert decision.tier == OversightTier.TIER_3_LOW

    def test_should_not_interrupt_for_low_value_high_confidence(self) -> None:
        """Test no interrupt for low-value disputes with high confidence."""
        controller = HITLController()

        decision = controller.should_interrupt(
            confidence=0.95,  # High confidence
            amount=50.0,  # Low amount
            dispute_type="billing_error",  # Low risk type
        )

        assert decision.should_interrupt is False
        assert decision.tier == OversightTier.TIER_3_LOW

    def test_should_not_interrupt_for_status_lookup(self) -> None:
        """Test no interrupt for status lookup actions."""
        controller = HITLController()

        decision = controller.should_interrupt(
            confidence=0.99,
            amount=None,
            dispute_type="general",
            action_type="status_lookup",
        )

        assert decision.should_interrupt is False
        assert decision.tier == OversightTier.TIER_3_LOW


class TestGetTierMethod:
    """Tests for get_tier() classification method."""

    def test_should_return_tier_1_for_sar_filing(self) -> None:
        """Test Tier 1 classification for SAR filing."""
        controller = HITLController()

        tier = controller.get_tier("fraud", "sar_filing")

        assert tier == OversightTier.TIER_1_HIGH

    def test_should_return_tier_1_for_payment_block(self) -> None:
        """Test Tier 1 classification for payment blocking."""
        controller = HITLController()

        tier = controller.get_tier("fraud", "payment_block")

        assert tier == OversightTier.TIER_1_HIGH

    def test_should_return_tier_3_for_info_lookup(self) -> None:
        """Test Tier 3 classification for info lookup."""
        controller = HITLController()

        tier = controller.get_tier("general", "info_lookup")

        assert tier == OversightTier.TIER_3_LOW

    def test_should_return_default_tier_for_unknown_action(self) -> None:
        """Test default tier returned for unknown action types."""
        controller = HITLController(default_tier=OversightTier.TIER_2_MEDIUM)

        tier = controller.get_tier("general", "unknown_action")

        assert tier == OversightTier.TIER_2_MEDIUM


class TestHumanReviewWorkflow:
    """Tests for human review request workflow."""

    def test_should_create_review_request(self) -> None:
        """Test request_human_review creates review request."""
        controller = HITLController()

        decision = controller.should_interrupt(
            confidence=0.72,
            amount=15000.0,
            dispute_type="fraud",
        )

        context = {
            "dispute_id": "dispute_001",
            "customer_id": "cust_123",
            "transaction_details": "Suspicious transaction",
        }

        review_id = controller.request_human_review(decision, context)

        assert review_id is not None
        assert isinstance(review_id, str)
        # Should be a valid UUID
        uuid.UUID(review_id)

    def test_should_record_human_approval(self) -> None:
        """Test record_human_decision for approval."""
        controller = HITLController()

        decision = controller.should_interrupt(
            confidence=0.72,
            amount=15000.0,
            dispute_type="fraud",
        )

        review_id = controller.request_human_review(decision, {})

        # Record approval
        controller.record_human_decision(
            review_id=review_id,
            approved=True,
            reviewer_id="reviewer_001",
            notes="Verified legitimate transaction",
        )

        # Should not raise any errors

    def test_should_record_human_rejection(self) -> None:
        """Test record_human_decision for rejection."""
        controller = HITLController()

        decision = controller.should_interrupt(
            confidence=0.72,
            amount=15000.0,
            dispute_type="fraud",
        )

        review_id = controller.request_human_review(decision, {})

        # Record rejection
        controller.record_human_decision(
            review_id=review_id,
            approved=False,
            reviewer_id="reviewer_001",
            notes="Fraudulent activity confirmed",
        )

        # Should not raise any errors


class TestEscalationStatistics:
    """Tests for get_escalation_stats()."""

    def test_should_return_escalation_stats(self) -> None:
        """Test get_escalation_stats returns statistics."""
        controller = HITLController()

        # Trigger some decisions
        controller.should_interrupt(confidence=0.72, amount=15000.0, dispute_type="fraud")
        controller.should_interrupt(confidence=0.95, amount=50.0, dispute_type="billing_error")
        controller.should_interrupt(confidence=0.88, amount=5000.0, dispute_type="general")

        stats = controller.get_escalation_stats()

        assert isinstance(stats, dict)
        assert "total_decisions" in stats
        assert "tier_counts" in stats
        assert stats["total_decisions"] >= 3


class TestInputValidation:
    """Tests for input validation and error handling."""

    def test_should_raise_type_error_for_non_float_confidence(self) -> None:
        """Test TypeError raised for non-float confidence."""
        controller = HITLController()

        with pytest.raises(TypeError, match="confidence must be a float"):
            controller.should_interrupt(
                confidence="high",  # type: ignore
                amount=100.0,
                dispute_type="general",
            )

    def test_should_raise_value_error_for_confidence_below_zero(self) -> None:
        """Test ValueError raised for confidence < 0."""
        controller = HITLController()

        with pytest.raises(ValueError, match="confidence must be between"):
            controller.should_interrupt(
                confidence=-0.5,
                amount=100.0,
                dispute_type="general",
            )

    def test_should_raise_value_error_for_confidence_above_one(self) -> None:
        """Test ValueError raised for confidence > 1."""
        controller = HITLController()

        with pytest.raises(ValueError, match="confidence must be between"):
            controller.should_interrupt(
                confidence=1.5,
                amount=100.0,
                dispute_type="general",
            )

    def test_should_handle_none_amount(self) -> None:
        """Test handling of None amount for non-financial actions."""
        controller = HITLController()

        decision = controller.should_interrupt(
            confidence=0.95,
            amount=None,
            dispute_type="general",
            action_type="info_lookup",
        )

        assert decision is not None
        assert decision.amount is None

    def test_should_handle_zero_amount(self) -> None:
        """Test handling of zero amount."""
        controller = HITLController()

        decision = controller.should_interrupt(
            confidence=0.95,
            amount=0.0,
            dispute_type="general",
        )

        assert decision is not None
        assert decision.amount == 0.0


class TestDecisionIDGeneration:
    """Tests for decision ID uniqueness."""

    def test_should_generate_unique_decision_ids(self) -> None:
        """Test that each decision has a unique ID."""
        controller = HITLController()

        decision1 = controller.should_interrupt(confidence=0.72, amount=100.0, dispute_type="general")
        decision2 = controller.should_interrupt(confidence=0.72, amount=100.0, dispute_type="general")

        assert decision1.decision_id != decision2.decision_id

    def test_should_generate_valid_uuid_for_decision_id(self) -> None:
        """Test that decision_id is a valid UUID."""
        controller = HITLController()

        decision = controller.should_interrupt(confidence=0.72, amount=100.0, dispute_type="general")

        # Should not raise
        uuid.UUID(decision.decision_id)

