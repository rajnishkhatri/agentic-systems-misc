"""Tests for CLASSIFY Phase Handler V5-ToT (Tree-of-Thought).

Tests the enhanced classification with:
- Tree-of-Thought reasoning with 3 independent branches
- Positive framing for checkpoints
- Branch synthesis with priority rules
- Confidence calibration with rationale
- Branch conflict detection

Following TDD principles: test_should_[result]_when_[condition]
"""

import datetime
import pytest
from unittest.mock import AsyncMock, Mock, patch, MagicMock
from pydantic import ValidationError

from backend.phases.classify_v5_tot import (
    classify_dispute_v5_tot,
    _identify_network,
    _identify_category_v5_tot,
    extract_branch_summary,
    check_branch_conflict,
    V5_TOT_MODEL,
    BranchAResult,
    BranchBResult,
    BranchCResult,
    SynthesisResult,
    CategoryResultV5ToT,
    CodeSelectionResult,
)

# Test data
DISPUTE_ID = "DIS-12345"


class TestBranchAResultValidation:
    """Tests for Branch A (Transaction Acknowledgment) validation."""

    def test_should_accept_acknowledged_conclusion(self) -> None:
        result = BranchAResult(
            evidence_for_acknowledgment=["my purchase"],
            evidence_against_acknowledgment=[],
            conclusion="acknowledged"
        )
        assert result.conclusion == "acknowledged"

    def test_should_accept_denied_conclusion(self) -> None:
        result = BranchAResult(
            evidence_for_acknowledgment=[],
            evidence_against_acknowledgment=["I never went there"],
            conclusion="denied"
        )
        assert result.conclusion == "denied"

    def test_should_accept_unclear_conclusion(self) -> None:
        result = BranchAResult(
            evidence_for_acknowledgment=[],
            evidence_against_acknowledgment=[],
            conclusion="unclear"
        )
        assert result.conclusion == "unclear"

    def test_should_normalize_conclusion_to_lowercase(self) -> None:
        result = BranchAResult(
            evidence_for_acknowledgment=[],
            evidence_against_acknowledgment=[],
            conclusion="ACKNOWLEDGED"
        )
        assert result.conclusion == "acknowledged"

    def test_should_reject_invalid_conclusion(self) -> None:
        with pytest.raises(ValidationError, match="Branch A conclusion must be one of"):
            BranchAResult(
                evidence_for_acknowledgment=[],
                evidence_against_acknowledgment=[],
                conclusion="invalid"
            )


class TestBranchBResultValidation:
    """Tests for Branch B (Complaint Specifics) validation."""

    def test_should_accept_amount_complaint_type(self) -> None:
        result = BranchBResult(
            complaint_type="amount",
            evidence=["bill too high"]
        )
        assert result.complaint_type == "amount"

    def test_should_accept_quality_complaint_type(self) -> None:
        result = BranchBResult(
            complaint_type="quality",
            evidence=["item was broken"]
        )
        assert result.complaint_type == "quality"

    def test_should_accept_processing_complaint_type(self) -> None:
        result = BranchBResult(
            complaint_type="processing",
            evidence=["charged twice"]
        )
        assert result.complaint_type == "processing"

    def test_should_accept_unspecified_complaint_type(self) -> None:
        result = BranchBResult(
            complaint_type="unspecified",
            evidence=[]
        )
        assert result.complaint_type == "unspecified"

    def test_should_normalize_complaint_type_to_lowercase(self) -> None:
        result = BranchBResult(
            complaint_type="AMOUNT",
            evidence=["high bill"]
        )
        assert result.complaint_type == "amount"

    def test_should_reject_invalid_complaint_type(self) -> None:
        with pytest.raises(ValidationError, match="Branch B complaint_type must be one of"):
            BranchBResult(
                complaint_type="invalid",
                evidence=[]
            )


class TestBranchCResultValidation:
    """Tests for Branch C (User Persona) validation."""

    def test_should_accept_frustrated_persona(self) -> None:
        result = BranchCResult(
            persona="frustrated",
            evidence=["ALL CAPS", "exclamation marks"]
        )
        assert result.persona == "frustrated"

    def test_should_accept_confused_persona(self) -> None:
        result = BranchCResult(
            persona="confused",
            evidence=["what is this?", "I don't understand"]
        )
        assert result.persona == "confused"

    def test_should_accept_accusatory_persona(self) -> None:
        result = BranchCResult(
            persona="accusatory",
            evidence=["I never", "someone stole"]
        )
        assert result.persona == "accusatory"

    def test_should_accept_neutral_persona(self) -> None:
        result = BranchCResult(
            persona="neutral",
            evidence=["factual description"]
        )
        assert result.persona == "neutral"

    def test_should_normalize_persona_to_lowercase(self) -> None:
        result = BranchCResult(
            persona="FRUSTRATED",
            evidence=[]
        )
        assert result.persona == "frustrated"

    def test_should_reject_invalid_persona(self) -> None:
        with pytest.raises(ValidationError, match="Branch C persona must be one of"):
            BranchCResult(
                persona="angry",
                evidence=[]
            )


class TestCategoryResultV5ToTValidation:
    """Tests for full V5-ToT category result validation."""

    def test_should_accept_valid_category_result(self) -> None:
        result = CategoryResultV5ToT(
            branch_a=BranchAResult(
                evidence_for_acknowledgment=["my bill"],
                evidence_against_acknowledgment=[],
                conclusion="acknowledged"
            ),
            branch_b=BranchBResult(
                complaint_type="amount",
                evidence=["too high"]
            ),
            branch_c=BranchCResult(
                persona="frustrated",
                evidence=["ALL CAPS"]
            ),
            synthesis=SynthesisResult(
                branch_agreement=0.90,
                priority_rule_applied=None,
                reasoning="All branches align"
            ),
            category="general",
            confidence=0.92,
            confidence_rationale="High agreement across branches"
        )
        assert result.category == "general"
        assert result.confidence == 0.92

    def test_should_reject_invalid_category(self) -> None:
        with pytest.raises(ValidationError, match="Category must be one of"):
            CategoryResultV5ToT(
                branch_a=BranchAResult(
                    evidence_for_acknowledgment=[],
                    evidence_against_acknowledgment=[],
                    conclusion="unclear"
                ),
                branch_b=BranchBResult(
                    complaint_type="unspecified",
                    evidence=[]
                ),
                branch_c=BranchCResult(
                    persona="neutral",
                    evidence=[]
                ),
                synthesis=SynthesisResult(
                    branch_agreement=0.5,
                    priority_rule_applied=None,
                    reasoning="test"
                ),
                category="invalid_category",
                confidence=0.5,
                confidence_rationale="test"
            )

    def test_should_reject_confidence_below_zero(self) -> None:
        with pytest.raises(ValidationError):
            CategoryResultV5ToT(
                branch_a=BranchAResult(
                    evidence_for_acknowledgment=[],
                    evidence_against_acknowledgment=[],
                    conclusion="unclear"
                ),
                branch_b=BranchBResult(
                    complaint_type="unspecified",
                    evidence=[]
                ),
                branch_c=BranchCResult(
                    persona="neutral",
                    evidence=[]
                ),
                synthesis=SynthesisResult(
                    branch_agreement=0.5,
                    priority_rule_applied=None,
                    reasoning="test"
                ),
                category="general",
                confidence=-0.1,
                confidence_rationale="test"
            )

    def test_should_reject_confidence_above_one(self) -> None:
        with pytest.raises(ValidationError):
            CategoryResultV5ToT(
                branch_a=BranchAResult(
                    evidence_for_acknowledgment=[],
                    evidence_against_acknowledgment=[],
                    conclusion="unclear"
                ),
                branch_b=BranchBResult(
                    complaint_type="unspecified",
                    evidence=[]
                ),
                branch_c=BranchCResult(
                    persona="neutral",
                    evidence=[]
                ),
                synthesis=SynthesisResult(
                    branch_agreement=0.5,
                    priority_rule_applied=None,
                    reasoning="test"
                ),
                category="general",
                confidence=1.5,
                confidence_rationale="test"
            )


class TestNetworkIdentification:
    """Tests for network identification logic."""

    def test_should_identify_amex_from_keyword(self) -> None:
        assert _identify_network("My Amex card was charged") == "amex"
        assert _identify_network("American Express charge unknown") == "amex"

    def test_should_identify_visa_from_keyword(self) -> None:
        assert _identify_network("Visa card declined") == "visa"

    def test_should_identify_mastercard_from_keyword(self) -> None:
        assert _identify_network("Mastercard transaction failed") == "mastercard"

    def test_should_identify_discover_from_keyword(self) -> None:
        assert _identify_network("Discover card issue") == "discover"

    def test_should_default_to_visa_when_no_network_mentioned(self) -> None:
        assert _identify_network("Unknown charge on my card") == "visa"

    def test_should_raise_type_error_for_non_string(self) -> None:
        with pytest.raises(TypeError, match="description must be a string"):
            _identify_network(123)

    def test_should_raise_type_error_for_none(self) -> None:
        with pytest.raises(TypeError, match="description must be a string"):
            _identify_network(None)


class TestExtractBranchSummary:
    """Tests for branch summary extraction."""

    def test_should_extract_all_branch_conclusions(self) -> None:
        result = CategoryResultV5ToT(
            branch_a=BranchAResult(
                evidence_for_acknowledgment=["my bill"],
                evidence_against_acknowledgment=[],
                conclusion="acknowledged"
            ),
            branch_b=BranchBResult(
                complaint_type="amount",
                evidence=["too high"]
            ),
            branch_c=BranchCResult(
                persona="frustrated",
                evidence=["ALL CAPS"]
            ),
            synthesis=SynthesisResult(
                branch_agreement=0.90,
                priority_rule_applied="Rule 1: Specifics Override Denial",
                reasoning="Amount complaint overrides"
            ),
            category="general",
            confidence=0.92,
            confidence_rationale="High agreement"
        )

        summary = extract_branch_summary(result)

        assert summary["branch_a_conclusion"] == "acknowledged"
        assert summary["branch_b_complaint"] == "amount"
        assert summary["branch_c_persona"] == "frustrated"
        assert summary["branch_agreement"] == 0.90
        assert summary["priority_rule"] == "Rule 1: Specifics Override Denial"

    def test_should_show_none_when_no_priority_rule(self) -> None:
        result = CategoryResultV5ToT(
            branch_a=BranchAResult(
                evidence_for_acknowledgment=[],
                evidence_against_acknowledgment=["never went"],
                conclusion="denied"
            ),
            branch_b=BranchBResult(
                complaint_type="unspecified",
                evidence=[]
            ),
            branch_c=BranchCResult(
                persona="accusatory",
                evidence=["I never"]
            ),
            synthesis=SynthesisResult(
                branch_agreement=0.95,
                priority_rule_applied=None,
                reasoning="All branches align to fraud"
            ),
            category="fraudulent",
            confidence=0.95,
            confidence_rationale="High agreement"
        )

        summary = extract_branch_summary(result)
        assert summary["priority_rule"] == "none"

    def test_should_raise_type_error_for_invalid_input(self) -> None:
        with pytest.raises(TypeError, match="result must be a CategoryResultV5ToT"):
            extract_branch_summary({"invalid": "dict"})


class TestCheckBranchConflict:
    """Tests for branch conflict detection."""

    def test_should_detect_denial_with_amount_conflict(self) -> None:
        result = CategoryResultV5ToT(
            branch_a=BranchAResult(
                evidence_for_acknowledgment=[],
                evidence_against_acknowledgment=["I didn't authorize"],
                conclusion="denied"
            ),
            branch_b=BranchBResult(
                complaint_type="amount",
                evidence=["bill too high"]
            ),
            branch_c=BranchCResult(
                persona="frustrated",
                evidence=["ALL CAPS"]
            ),
            synthesis=SynthesisResult(
                branch_agreement=0.75,
                priority_rule_applied="Rule 1: Specifics Override Denial",
                reasoning="Amount overrides denial"
            ),
            category="general",
            confidence=0.85,
            confidence_rationale="Conflict resolved by Rule 1"
        )

        conflict = check_branch_conflict(result)

        assert conflict is not None
        assert conflict["type"] == "denial_with_amount"
        assert conflict["resolution"] == "amount_overrides_denial"
        assert conflict["branch_a"] == "denied"
        assert conflict["branch_b"] == "amount"

    def test_should_detect_unclear_with_accusatory_conflict(self) -> None:
        result = CategoryResultV5ToT(
            branch_a=BranchAResult(
                evidence_for_acknowledgment=[],
                evidence_against_acknowledgment=[],
                conclusion="unclear"
            ),
            branch_b=BranchBResult(
                complaint_type="unspecified",
                evidence=[]
            ),
            branch_c=BranchCResult(
                persona="accusatory",
                evidence=["someone stole my card"]
            ),
            synthesis=SynthesisResult(
                branch_agreement=0.70,
                priority_rule_applied="Rule 3: Persona as Tiebreaker",
                reasoning="Accusatory tone suggests fraud"
            ),
            category="fraudulent",
            confidence=0.75,
            confidence_rationale="Moderate confidence due to conflict"
        )

        conflict = check_branch_conflict(result)

        assert conflict is not None
        assert conflict["type"] == "unclear_with_accusatory"
        assert conflict["resolution"] == "needs_persona_tiebreaker"

    def test_should_return_none_when_no_conflict(self) -> None:
        result = CategoryResultV5ToT(
            branch_a=BranchAResult(
                evidence_for_acknowledgment=["my order"],
                evidence_against_acknowledgment=[],
                conclusion="acknowledged"
            ),
            branch_b=BranchBResult(
                complaint_type="quality",
                evidence=["item broken"]
            ),
            branch_c=BranchCResult(
                persona="frustrated",
                evidence=["this is unacceptable"]
            ),
            synthesis=SynthesisResult(
                branch_agreement=0.95,
                priority_rule_applied=None,
                reasoning="All branches align"
            ),
            category="product_unacceptable",
            confidence=0.95,
            confidence_rationale="High agreement"
        )

        conflict = check_branch_conflict(result)
        assert conflict is None

    def test_should_raise_type_error_for_invalid_input(self) -> None:
        with pytest.raises(TypeError, match="result must be a CategoryResultV5ToT"):
            check_branch_conflict("invalid")


class TestIdentifyCategoryV5ToT:
    """Tests for V5-ToT category identification."""

    def test_should_raise_type_error_for_non_string_description(self) -> None:
        with pytest.raises(TypeError, match="description must be a string"):
            import asyncio
            asyncio.get_event_loop().run_until_complete(
                _identify_category_v5_tot(123)
            )

    def test_should_raise_value_error_for_empty_description(self) -> None:
        with pytest.raises(ValueError, match="description cannot be empty"):
            import asyncio
            asyncio.get_event_loop().run_until_complete(
                _identify_category_v5_tot("")
            )

    def test_should_raise_value_error_for_whitespace_only(self) -> None:
        with pytest.raises(ValueError, match="description cannot be empty"):
            import asyncio
            asyncio.get_event_loop().run_until_complete(
                _identify_category_v5_tot("   ")
            )


class TestClassifyDisputeV5ToT:
    """Tests for full V5-ToT classification pipeline."""

    def test_should_raise_type_error_for_non_dict_task(self) -> None:
        with pytest.raises(TypeError, match="task must be a dictionary"):
            import asyncio
            asyncio.get_event_loop().run_until_complete(
                classify_dispute_v5_tot("not a dict")
            )

    def test_should_raise_value_error_for_missing_dispute_id(self) -> None:
        with pytest.raises(ValueError, match="task must contain 'dispute_id'"):
            import asyncio
            asyncio.get_event_loop().run_until_complete(
                classify_dispute_v5_tot({"description": "test"})
            )

    def test_should_raise_value_error_for_missing_description(self) -> None:
        with pytest.raises(ValueError, match="task must contain 'description'"):
            import asyncio
            asyncio.get_event_loop().run_until_complete(
                classify_dispute_v5_tot({"dispute_id": DISPUTE_ID})
            )

    @pytest.mark.asyncio
    async def test_should_return_v5_tot_specific_fields(self) -> None:
        """Test that V5-ToT returns branch analysis fields."""
        mock_category_result = CategoryResultV5ToT(
            branch_a=BranchAResult(
                evidence_for_acknowledgment=["my bill"],
                evidence_against_acknowledgment=[],
                conclusion="acknowledged"
            ),
            branch_b=BranchBResult(
                complaint_type="amount",
                evidence=["too high"]
            ),
            branch_c=BranchCResult(
                persona="frustrated",
                evidence=["ALL CAPS"]
            ),
            synthesis=SynthesisResult(
                branch_agreement=0.90,
                priority_rule_applied="Rule 1: Specifics Override Denial",
                reasoning="Amount complaint overrides denial language"
            ),
            category="general",
            confidence=0.92,
            confidence_rationale="High agreement across branches"
        )

        mock_code_result = CodeSelectionResult(
            reason_code="V13.1",
            confidence=0.88,
            reasoning="Billing dispute code"
        )

        mock_catalog = MagicMock()
        mock_catalog.get_codes_for_network_and_category.return_value = [
            {"code": "V13.1", "description": "Billing dispute"}
        ]

        with patch(
            "backend.phases.classify_v5_tot._identify_category_v5_tot",
            return_value=mock_category_result
        ), patch(
            "backend.phases.classify_v5_tot._select_code",
            return_value=mock_code_result
        ), patch(
            "backend.phases.classify_v5_tot.get_reason_code_catalog",
            return_value=mock_catalog
        ):
            result = await classify_dispute_v5_tot({
                "dispute_id": DISPUTE_ID,
                "description": "WHY IS MY BILL SO HIGH?! I DIDN'T AUTHORIZE THIS!",
            })

        # Verify V5-ToT specific fields
        assert result["classifier_version"] == "5.0.0-ToT"
        assert result["branch_a_conclusion"] == "acknowledged"
        assert result["branch_b_complaint"] == "amount"
        assert result["branch_c_persona"] == "frustrated"
        assert result["branch_agreement"] == 0.90
        assert result["priority_rule_applied"] == "Rule 1: Specifics Override Denial"
        assert result["classification_confidence"] == 0.92
        assert result["confidence_rationale"] == "High agreement across branches"

    @pytest.mark.asyncio
    async def test_should_detect_branch_conflict_in_result(self) -> None:
        """Test that branch conflicts are detected and included in result."""
        mock_category_result = CategoryResultV5ToT(
            branch_a=BranchAResult(
                evidence_for_acknowledgment=[],
                evidence_against_acknowledgment=["I didn't authorize"],
                conclusion="denied"
            ),
            branch_b=BranchBResult(
                complaint_type="amount",
                evidence=["bill too high"]
            ),
            branch_c=BranchCResult(
                persona="frustrated",
                evidence=["ALL CAPS"]
            ),
            synthesis=SynthesisResult(
                branch_agreement=0.75,
                priority_rule_applied="Rule 1: Specifics Override Denial",
                reasoning="Amount overrides denial"
            ),
            category="general",
            confidence=0.85,
            confidence_rationale="Conflict resolved by Rule 1"
        )

        mock_code_result = CodeSelectionResult(
            reason_code="V13.1",
            confidence=0.85,
            reasoning="Billing dispute code"
        )

        mock_catalog = MagicMock()
        mock_catalog.get_codes_for_network_and_category.return_value = [
            {"code": "V13.1", "description": "Billing dispute"}
        ]

        with patch(
            "backend.phases.classify_v5_tot._identify_category_v5_tot",
            return_value=mock_category_result
        ), patch(
            "backend.phases.classify_v5_tot._select_code",
            return_value=mock_code_result
        ), patch(
            "backend.phases.classify_v5_tot.get_reason_code_catalog",
            return_value=mock_catalog
        ):
            result = await classify_dispute_v5_tot({
                "dispute_id": DISPUTE_ID,
                "description": "WHY IS MY BILL SO HIGH?! I DIDN'T AUTHORIZE THIS!",
            })

        # Verify conflict detection
        assert result["branch_conflict"] is not None
        assert result["branch_conflict"]["type"] == "denial_with_amount"
        assert result["branch_conflict"]["resolution"] == "amount_overrides_denial"

    @pytest.mark.asyncio
    async def test_should_use_pre_selected_network(self) -> None:
        """Test that pre-selected network is used when provided."""
        mock_category_result = CategoryResultV5ToT(
            branch_a=BranchAResult(
                evidence_for_acknowledgment=[],
                evidence_against_acknowledgment=["never went"],
                conclusion="denied"
            ),
            branch_b=BranchBResult(
                complaint_type="unspecified",
                evidence=[]
            ),
            branch_c=BranchCResult(
                persona="accusatory",
                evidence=["I never"]
            ),
            synthesis=SynthesisResult(
                branch_agreement=0.95,
                priority_rule_applied=None,
                reasoning="Clear fraud case"
            ),
            category="fraudulent",
            confidence=0.95,
            confidence_rationale="All branches align"
        )

        mock_code_result = CodeSelectionResult(
            reason_code="F24",
            confidence=0.95,
            reasoning="Fraud code"
        )

        mock_catalog = MagicMock()
        mock_catalog.get_codes_for_network_and_category.return_value = [
            {"code": "F24", "description": "Card not present fraud"}
        ]

        with patch(
            "backend.phases.classify_v5_tot._identify_category_v5_tot",
            return_value=mock_category_result
        ), patch(
            "backend.phases.classify_v5_tot._select_code",
            return_value=mock_code_result
        ), patch(
            "backend.phases.classify_v5_tot.get_reason_code_catalog",
            return_value=mock_catalog
        ):
            result = await classify_dispute_v5_tot({
                "dispute_id": DISPUTE_ID,
                "description": "I never went to this store!",
                "network": "amex",
            })

        assert result["network"] == "amex"

    @pytest.mark.asyncio
    async def test_should_use_default_model_when_not_specified(self) -> None:
        """Test that V5_TOT_MODEL is used by default."""
        mock_category_result = CategoryResultV5ToT(
            branch_a=BranchAResult(
                evidence_for_acknowledgment=[],
                evidence_against_acknowledgment=[],
                conclusion="unclear"
            ),
            branch_b=BranchBResult(
                complaint_type="unspecified",
                evidence=[]
            ),
            branch_c=BranchCResult(
                persona="neutral",
                evidence=[]
            ),
            synthesis=SynthesisResult(
                branch_agreement=0.5,
                priority_rule_applied=None,
                reasoning="Unclear case"
            ),
            category="unrecognized",
            confidence=0.6,
            confidence_rationale="Low clarity"
        )

        mock_code_result = CodeSelectionResult(
            reason_code="V75",
            confidence=0.6,
            reasoning="Unrecognized code"
        )

        mock_catalog = MagicMock()
        mock_catalog.get_codes_for_network_and_category.return_value = [
            {"code": "V75", "description": "Unrecognized transaction"}
        ]

        with patch(
            "backend.phases.classify_v5_tot._identify_category_v5_tot",
            return_value=mock_category_result
        ) as mock_identify, patch(
            "backend.phases.classify_v5_tot._select_code",
            return_value=mock_code_result
        ), patch(
            "backend.phases.classify_v5_tot.get_reason_code_catalog",
            return_value=mock_catalog
        ):
            result = await classify_dispute_v5_tot({
                "dispute_id": DISPUTE_ID,
                "description": "What is this charge?",
            })

        assert result["model_used"] == V5_TOT_MODEL


class TestV5ToTModel:
    """Tests for V5-ToT model configuration."""

    def test_should_use_anthropic_claude_model(self) -> None:
        assert "anthropic" in V5_TOT_MODEL
        assert "claude" in V5_TOT_MODEL
