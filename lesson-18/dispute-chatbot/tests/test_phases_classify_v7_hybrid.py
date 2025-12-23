"""Tests for CLASSIFY Phase V7-Hybrid.

Tests the Tree-of-Thought classification with reason_code_group mapping.
"""

from __future__ import annotations

import pytest

from backend.phases.classify_v7_hybrid import (
    BranchAResult,
    BranchBResult,
    BranchCResult,
    CategoryResultV7Hybrid,
    SynthesisResult,
    _identify_network,
    extract_branch_summary,
    check_branch_conflict,
    infer_reason_code_group,
)


# ============================================================================
# Branch A Tests
# ============================================================================


class TestBranchAResult:
    """Tests for BranchAResult validation."""

    def test_should_accept_acknowledged_conclusion(self) -> None:
        """Test that 'acknowledged' is a valid conclusion."""
        result = BranchAResult(
            evidence_for_acknowledgment=["my purchase", "when I visited"],
            evidence_against_acknowledgment=[],
            conclusion="acknowledged"
        )
        assert result.conclusion == "acknowledged"

    def test_should_accept_denied_conclusion(self) -> None:
        """Test that 'denied' is a valid conclusion."""
        result = BranchAResult(
            evidence_for_acknowledgment=[],
            evidence_against_acknowledgment=["never went there"],
            conclusion="denied"
        )
        assert result.conclusion == "denied"

    def test_should_accept_unclear_conclusion(self) -> None:
        """Test that 'unclear' is a valid conclusion."""
        result = BranchAResult(
            evidence_for_acknowledgment=[],
            evidence_against_acknowledgment=[],
            conclusion="unclear"
        )
        assert result.conclusion == "unclear"

    def test_should_normalize_uppercase_conclusion(self) -> None:
        """Test that uppercase conclusions are normalized."""
        result = BranchAResult(
            evidence_for_acknowledgment=[],
            evidence_against_acknowledgment=[],
            conclusion="ACKNOWLEDGED"
        )
        assert result.conclusion == "acknowledged"

    def test_should_reject_invalid_conclusion(self) -> None:
        """Test that invalid conclusions are rejected."""
        with pytest.raises(ValueError, match="must be one of"):
            BranchAResult(
                evidence_for_acknowledgment=[],
                evidence_against_acknowledgment=[],
                conclusion="maybe"
            )


# ============================================================================
# Branch B Tests (V7: includes 'delivery')
# ============================================================================


class TestBranchBResult:
    """Tests for BranchBResult validation."""

    def test_should_accept_amount_complaint(self) -> None:
        """Test that 'amount' is a valid complaint type."""
        result = BranchBResult(
            complaint_type="amount",
            evidence=["wrong amount", "$500 vs $50"]
        )
        assert result.complaint_type == "amount"

    def test_should_accept_quality_complaint(self) -> None:
        """Test that 'quality' is a valid complaint type."""
        result = BranchBResult(
            complaint_type="quality",
            evidence=["broken", "damaged"]
        )
        assert result.complaint_type == "quality"

    def test_should_accept_processing_complaint(self) -> None:
        """Test that 'processing' is a valid complaint type."""
        result = BranchBResult(
            complaint_type="processing",
            evidence=["charged twice", "duplicate"]
        )
        assert result.complaint_type == "processing"

    def test_should_accept_delivery_complaint(self) -> None:
        """Test that 'delivery' is a valid complaint type (V7 addition)."""
        result = BranchBResult(
            complaint_type="delivery",
            evidence=["never arrived", "didn't receive"]
        )
        assert result.complaint_type == "delivery"

    def test_should_accept_unspecified_complaint(self) -> None:
        """Test that 'unspecified' is a valid complaint type."""
        result = BranchBResult(
            complaint_type="unspecified",
            evidence=[]
        )
        assert result.complaint_type == "unspecified"

    def test_should_normalize_discrepancy_to_amount(self) -> None:
        """Test that 'discrepancy' alias maps to 'amount'."""
        result = BranchBResult(
            complaint_type="discrepancy",
            evidence=["numbers don't match"]
        )
        assert result.complaint_type == "amount"

    def test_should_normalize_not_received_to_delivery(self) -> None:
        """Test that 'not_received' alias maps to 'delivery'."""
        result = BranchBResult(
            complaint_type="not_received",
            evidence=["item missing"]
        )
        assert result.complaint_type == "delivery"

    def test_should_fallback_invalid_to_unspecified(self) -> None:
        """Test that invalid complaint types fallback to 'unspecified'."""
        result = BranchBResult(
            complaint_type="unknown_type",
            evidence=[]
        )
        assert result.complaint_type == "unspecified"


# ============================================================================
# Branch C Tests
# ============================================================================


class TestBranchCResult:
    """Tests for BranchCResult validation."""

    def test_should_accept_frustrated_persona(self) -> None:
        """Test that 'frustrated' is a valid persona."""
        result = BranchCResult(
            persona="frustrated",
            evidence=["FIX THIS NOW!", "exclamation marks"]
        )
        assert result.persona == "frustrated"

    def test_should_accept_confused_persona(self) -> None:
        """Test that 'confused' is a valid persona."""
        result = BranchCResult(
            persona="confused",
            evidence=["what is this?", "I don't understand"]
        )
        assert result.persona == "confused"

    def test_should_accept_accusatory_persona(self) -> None:
        """Test that 'accusatory' is a valid persona."""
        result = BranchCResult(
            persona="accusatory",
            evidence=["I never", "someone stole"]
        )
        assert result.persona == "accusatory"

    def test_should_accept_neutral_persona(self) -> None:
        """Test that 'neutral' is a valid persona."""
        result = BranchCResult(
            persona="neutral",
            evidence=["factual description"]
        )
        assert result.persona == "neutral"

    def test_should_normalize_angry_to_frustrated(self) -> None:
        """Test that 'angry' alias maps to 'frustrated'."""
        result = BranchCResult(
            persona="angry",
            evidence=["ALL CAPS"]
        )
        assert result.persona == "frustrated"


# ============================================================================
# Category Result V7 Tests (includes reason_code_group)
# ============================================================================


class TestCategoryResultV7Hybrid:
    """Tests for CategoryResultV7Hybrid validation."""

    @pytest.fixture
    def valid_result_data(self) -> dict:
        """Fixture providing valid result data."""
        return {
            "branch_a": {
                "evidence_for_acknowledgment": ["my purchase"],
                "evidence_against_acknowledgment": [],
                "conclusion": "acknowledged"
            },
            "branch_b": {
                "complaint_type": "amount",
                "evidence": ["wrong amount"]
            },
            "branch_c": {
                "persona": "frustrated",
                "evidence": ["FIX THIS!"]
            },
            "synthesis": {
                "branch_agreement": 0.85,
                "priority_rule_applied": "Rule 1: Specifics Override Denial",
                "reasoning": "Amount complaint overrides denial language"
            },
            "category": "general",
            "reason_code_group": "authorization",
            "confidence": 0.92,
            "confidence_rationale": "High confidence due to clear amount complaint"
        }

    def test_should_validate_complete_result(self, valid_result_data: dict) -> None:
        """Test that complete valid result passes validation."""
        result = CategoryResultV7Hybrid(**valid_result_data)
        assert result.category == "general"
        assert result.reason_code_group == "authorization"
        assert result.confidence == 0.92

    def test_should_normalize_fraud_category_to_fraudulent(self) -> None:
        """Test that 'fraud' alias maps to 'fraudulent'."""
        data = {
            "branch_a": {"evidence_for_acknowledgment": [], "evidence_against_acknowledgment": ["never went"], "conclusion": "denied"},
            "branch_b": {"complaint_type": "unspecified", "evidence": []},
            "branch_c": {"persona": "accusatory", "evidence": ["I never"]},
            "synthesis": {"branch_agreement": 0.95, "priority_rule_applied": None, "reasoning": "Clear fraud"},
            "category": "fraud",  # Should normalize to 'fraudulent'
            "reason_code_group": "fraud",
            "confidence": 0.95,
            "confidence_rationale": "Strong fraud indicators"
        }
        result = CategoryResultV7Hybrid(**data)
        assert result.category == "fraudulent"

    def test_should_validate_all_reason_code_groups(self) -> None:
        """Test that all valid reason_code_groups are accepted."""
        valid_groups = ["fraud", "authorization", "processing_errors", "cardholder_disputes", "consumer_disputes"]
        base_data = {
            "branch_a": {"evidence_for_acknowledgment": [], "evidence_against_acknowledgment": [], "conclusion": "unclear"},
            "branch_b": {"complaint_type": "unspecified", "evidence": []},
            "branch_c": {"persona": "neutral", "evidence": []},
            "synthesis": {"branch_agreement": 0.8, "priority_rule_applied": None, "reasoning": "Test"},
            "category": "general",
            "confidence": 0.8,
            "confidence_rationale": "Test"
        }
        for group in valid_groups:
            data = {**base_data, "reason_code_group": group}
            result = CategoryResultV7Hybrid(**data)
            assert result.reason_code_group == group

    def test_should_fallback_invalid_reason_code_group(self) -> None:
        """Test that invalid reason_code_group falls back to cardholder_disputes."""
        data = {
            "branch_a": {"evidence_for_acknowledgment": [], "evidence_against_acknowledgment": [], "conclusion": "unclear"},
            "branch_b": {"complaint_type": "unspecified", "evidence": []},
            "branch_c": {"persona": "neutral", "evidence": []},
            "synthesis": {"branch_agreement": 0.8, "priority_rule_applied": None, "reasoning": "Test"},
            "category": "general",
            "reason_code_group": "invalid_group",
            "confidence": 0.8,
            "confidence_rationale": "Test"
        }
        result = CategoryResultV7Hybrid(**data)
        assert result.reason_code_group == "cardholder_disputes"


# ============================================================================
# Network Identification Tests
# ============================================================================


class TestIdentifyNetwork:
    """Tests for _identify_network function."""

    def test_should_identify_amex(self) -> None:
        """Test that Amex network is identified."""
        assert _identify_network("My Amex card was charged") == "amex"
        assert _identify_network("American Express charge") == "amex"

    def test_should_identify_visa(self) -> None:
        """Test that Visa network is identified."""
        assert _identify_network("Visa card charge") == "visa"

    def test_should_identify_mastercard(self) -> None:
        """Test that Mastercard network is identified."""
        assert _identify_network("Mastercard transaction") == "mastercard"

    def test_should_identify_discover(self) -> None:
        """Test that Discover network is identified."""
        assert _identify_network("Discover card") == "discover"

    def test_should_default_to_visa(self) -> None:
        """Test that unknown networks default to Visa."""
        assert _identify_network("Some random charge") == "visa"

    def test_should_raise_for_non_string(self) -> None:
        """Test that TypeError is raised for non-string input."""
        with pytest.raises(TypeError, match="must be a string"):
            _identify_network(123)


# ============================================================================
# Helper Function Tests
# ============================================================================


class TestExtractBranchSummary:
    """Tests for extract_branch_summary function."""

    def test_should_extract_summary_with_reason_code_group(self) -> None:
        """Test that summary includes reason_code_group (V7 addition)."""
        result = CategoryResultV7Hybrid(
            branch_a=BranchAResult(
                evidence_for_acknowledgment=["my order"],
                evidence_against_acknowledgment=[],
                conclusion="acknowledged"
            ),
            branch_b=BranchBResult(complaint_type="delivery", evidence=["never arrived"]),
            branch_c=BranchCResult(persona="frustrated", evidence=["!"]),
            synthesis=SynthesisResult(branch_agreement=0.9, priority_rule_applied="Rule 2", reasoning="Delivery"),
            category="product_not_received",
            reason_code_group="cardholder_disputes",
            confidence=0.94,
            confidence_rationale="Clear delivery complaint"
        )
        summary = extract_branch_summary(result)
        assert summary["branch_a_conclusion"] == "acknowledged"
        assert summary["branch_b_complaint"] == "delivery"
        assert summary["branch_c_persona"] == "frustrated"
        assert summary["reason_code_group"] == "cardholder_disputes"


class TestCheckBranchConflict:
    """Tests for check_branch_conflict function."""

    def test_should_detect_denial_with_amount_conflict(self) -> None:
        """Test detection of denial + amount conflict."""
        result = CategoryResultV7Hybrid(
            branch_a=BranchAResult(
                evidence_for_acknowledgment=[],
                evidence_against_acknowledgment=["I didn't authorize"],
                conclusion="denied"
            ),
            branch_b=BranchBResult(complaint_type="amount", evidence=["bill too high"]),
            branch_c=BranchCResult(persona="frustrated", evidence=["!"]),
            synthesis=SynthesisResult(branch_agreement=0.7, priority_rule_applied="Rule 1", reasoning="Amount overrides"),
            category="general",
            reason_code_group="authorization",
            confidence=0.85,
            confidence_rationale="Amount complaint detected"
        )
        conflict = check_branch_conflict(result)
        assert conflict is not None
        assert conflict["type"] == "denial_with_amount"
        assert conflict["resolution"] == "amount_overrides_denial"

    def test_should_detect_delivery_with_unclear_conflict(self) -> None:
        """Test detection of delivery + unclear acknowledgment conflict (V7 addition)."""
        result = CategoryResultV7Hybrid(
            branch_a=BranchAResult(
                evidence_for_acknowledgment=[],
                evidence_against_acknowledgment=[],
                conclusion="unclear"
            ),
            branch_b=BranchBResult(complaint_type="delivery", evidence=["never arrived"]),
            branch_c=BranchCResult(persona="neutral", evidence=[]),
            synthesis=SynthesisResult(branch_agreement=0.75, priority_rule_applied="Rule 2", reasoning="Delivery implies purchase"),
            category="product_not_received",
            reason_code_group="cardholder_disputes",
            confidence=0.8,
            confidence_rationale="Delivery complaint with unclear acknowledgment"
        )
        conflict = check_branch_conflict(result)
        assert conflict is not None
        assert conflict["type"] == "delivery_with_unclear_acknowledgment"
        assert conflict["resolution"] == "delivery_implies_purchase"

    def test_should_return_none_when_no_conflict(self) -> None:
        """Test that None is returned when no conflict detected."""
        result = CategoryResultV7Hybrid(
            branch_a=BranchAResult(
                evidence_for_acknowledgment=["my order"],
                evidence_against_acknowledgment=[],
                conclusion="acknowledged"
            ),
            branch_b=BranchBResult(complaint_type="quality", evidence=["broken"]),
            branch_c=BranchCResult(persona="neutral", evidence=[]),
            synthesis=SynthesisResult(branch_agreement=0.95, priority_rule_applied=None, reasoning="Clear quality complaint"),
            category="product_unacceptable",
            reason_code_group="cardholder_disputes",
            confidence=0.94,
            confidence_rationale="Strong quality evidence"
        )
        conflict = check_branch_conflict(result)
        assert conflict is None


class TestInferReasonCodeGroup:
    """Tests for infer_reason_code_group function."""

    def test_should_infer_fraud_for_fraudulent(self) -> None:
        """Test that fraudulent maps to fraud group."""
        assert infer_reason_code_group("fraudulent") == "fraud"

    def test_should_infer_authorization_for_general(self) -> None:
        """Test that general maps to authorization group."""
        assert infer_reason_code_group("general") == "authorization"

    def test_should_infer_processing_errors_for_duplicate(self) -> None:
        """Test that duplicate maps to processing_errors group."""
        assert infer_reason_code_group("duplicate") == "processing_errors"

    def test_should_infer_cardholder_disputes_for_product_categories(self) -> None:
        """Test that product categories map to cardholder_disputes."""
        assert infer_reason_code_group("product_not_received") == "cardholder_disputes"
        assert infer_reason_code_group("product_unacceptable") == "cardholder_disputes"
        assert infer_reason_code_group("credit_not_processed") == "cardholder_disputes"
        assert infer_reason_code_group("subscription_canceled") == "cardholder_disputes"
        assert infer_reason_code_group("unrecognized") == "cardholder_disputes"

    def test_should_default_to_cardholder_disputes(self) -> None:
        """Test that unknown categories default to cardholder_disputes."""
        assert infer_reason_code_group("unknown") == "cardholder_disputes"
