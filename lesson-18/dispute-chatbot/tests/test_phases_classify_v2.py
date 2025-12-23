"""Tests for CLASSIFY Phase Handler V2.

Tests the enhanced classification with:
- Negative examples in category prompt
- Few-shot examples in code selection prompt
- Keyword disambiguation hints
- Network family intermediate signal
"""

import datetime
import pytest
from unittest.mock import AsyncMock, Mock, patch, MagicMock

from backend.phases.classify_v2 import (
    classify_dispute_v2,
    _identify_network,
    _detect_network_family,
    _get_keyword_code_hint,
    _load_keyword_hints,
    CategoryResult,
    CodeSelectionResult,
)

# Test data
DISPUTE_ID = "DIS-12345"


class TestNetworkIdentification:
    """Tests for network identification logic."""

    def test_should_identify_amex_from_keyword(self):
        assert _identify_network("My Amex card was charged") == "amex"
        assert _identify_network("American Express charge unknown") == "amex"

    def test_should_identify_visa_from_keyword(self):
        assert _identify_network("Visa card declined") == "visa"

    def test_should_identify_mastercard_from_keyword(self):
        assert _identify_network("Mastercard transaction failed") == "mastercard"

    def test_should_identify_discover_from_keyword(self):
        assert _identify_network("Discover card issue") == "discover"

    def test_should_default_to_visa_when_no_network_mentioned(self):
        assert _identify_network("Unknown charge on my card") == "visa"


class TestNetworkFamilyDetection:
    """Tests for network family detection from keywords."""

    def test_should_detect_fraud_family(self):
        assert _detect_network_family("My card was stolen") == "fraud"
        assert _detect_network_family("I didn't make this purchase") == "fraud"

    def test_should_detect_authorization_family(self):
        assert _detect_network_family("Card was declined at checkout") == "authorization"
        assert _detect_network_family("Transaction was rejected") == "authorization"

    def test_should_detect_cardholder_disputes_family(self):
        assert _detect_network_family("I returned the item but no refund") == "cardholder_disputes"
        assert _detect_network_family("Item was damaged when received") == "cardholder_disputes"

    def test_should_detect_processing_errors_family(self):
        assert _detect_network_family("I was charged twice for the same purchase") == "processing_errors"
        assert _detect_network_family("Wrong amount on my statement") == "processing_errors"

    def test_should_return_none_when_no_family_detected(self):
        assert _detect_network_family("Hello, I need help") is None


class TestKeywordCodeHint:
    """Tests for keyword disambiguation hints."""

    def test_should_hint_a08_for_declined(self):
        hint = _get_keyword_code_hint("My card was declined at the store", "amex")
        assert hint is not None
        assert hint["code"] == "A08"
        assert "declined" in hint["matched_keywords"]

    def test_should_hint_f24_for_fraud_keywords(self):
        hint = _get_keyword_code_hint("My card was stolen and someone else used it", "amex")
        assert hint is not None
        assert hint["code"] == "F24"

    def test_should_hint_c04_for_returned_goods(self):
        hint = _get_keyword_code_hint("I returned the item but never got my refund", "amex")
        assert hint is not None
        assert hint["code"] == "C04"

    def test_should_hint_p08_for_duplicate(self):
        hint = _get_keyword_code_hint("I was charged twice for the same thing", "amex")
        assert hint is not None
        assert hint["code"] == "P08"

    def test_should_hint_c14_for_paid_cash(self):
        hint = _get_keyword_code_hint("I paid cash but also got charged on card", "amex")
        assert hint is not None
        assert hint["code"] == "C14"

    def test_should_return_none_when_no_match(self):
        hint = _get_keyword_code_hint("Hello, I have a question", "amex")
        assert hint is None

    def test_should_use_correct_network_code(self):
        hint_amex = _get_keyword_code_hint("Card was declined", "amex")
        hint_visa = _get_keyword_code_hint("Card was declined", "visa")

        assert hint_amex["code"] == "A08"
        assert hint_visa["code"] == "11.2"


class TestInputValidation:
    """Tests for input validation in classify_dispute_v2."""

    @pytest.mark.asyncio
    async def test_should_raise_typeerror_when_task_is_not_dict(self):
        with pytest.raises(TypeError, match="task must be a dictionary"):
            await classify_dispute_v2(None)

    @pytest.mark.asyncio
    async def test_should_raise_valueerror_when_dispute_id_missing(self):
        with pytest.raises(ValueError, match="task must contain 'dispute_id'"):
            await classify_dispute_v2({"description": "Some description"})

    @pytest.mark.asyncio
    async def test_should_raise_valueerror_when_description_missing(self):
        with pytest.raises(ValueError, match="task must contain 'description'"):
            await classify_dispute_v2({"dispute_id": DISPUTE_ID})


class TestClassifyDisputeV2:
    """Integration tests for classify_dispute_v2."""

    @pytest.fixture
    def mock_llm_service(self):
        with patch("backend.phases.classify_v2.get_default_service") as mock_get:
            mock_service = Mock()
            mock_service.routing_model = "mock-routing-model"
            mock_get.return_value = mock_service
            yield mock_service

    @pytest.fixture
    def mock_render_prompt(self):
        with patch("backend.phases.classify_v2.render_prompt") as mock_render:
            mock_render.return_value = "Mock Prompt"
            yield mock_render

    @pytest.fixture
    def mock_catalog(self):
        with patch("backend.phases.classify_v2.get_reason_code_catalog") as mock_get_catalog:
            mock_instance = Mock()
            mock_instance.get_codes_for_network_and_category.return_value = [
                {"code": "C08", "description": "Goods Not Received", "category": "product_not_received"}
            ]
            mock_instance.get_codes_for_network.return_value = [
                {"code": "C08", "description": "Goods Not Received", "category": "product_not_received"}
            ]
            mock_get_catalog.return_value = mock_instance
            yield mock_instance

    @pytest.mark.asyncio
    async def test_should_classify_with_v2_prompts(self, mock_llm_service, mock_render_prompt, mock_catalog):
        """Verify V2 prompts are used."""
        # Setup mock responses for two LLM calls
        mock_category = CategoryResult(category="product_not_received", reasoning="Item not delivered")
        mock_code = CodeSelectionResult(reason_code="C08", confidence=0.95, reasoning="Matches PNR")

        mock_llm_service.complete_structured = AsyncMock(side_effect=[mock_category, mock_code])

        task = {"dispute_id": DISPUTE_ID, "description": "My order from Amex never arrived"}
        result = await classify_dispute_v2(task)

        # Verify V2 prompts were used
        assert mock_render_prompt.call_count == 2
        prompt_calls = [call[0][0] for call in mock_render_prompt.call_args_list]
        assert "DisputeClassifier_identify_category_v2.j2" in prompt_calls
        assert "DisputeClassifier_select_code_v2.j2" in prompt_calls

    @pytest.mark.asyncio
    async def test_should_return_v2_metadata(self, mock_llm_service, mock_render_prompt, mock_catalog):
        """Verify V2-specific fields are in response."""
        mock_category = CategoryResult(category="product_not_received", reasoning="Item not delivered")
        mock_code = CodeSelectionResult(reason_code="C08", confidence=0.95, reasoning="Matches PNR")
        mock_llm_service.complete_structured = AsyncMock(side_effect=[mock_category, mock_code])

        task = {"dispute_id": DISPUTE_ID, "description": "My Amex order never arrived"}
        result = await classify_dispute_v2(task)

        # V2-specific fields
        assert result["classifier_version"] == "2.0.0"
        assert "network_family" in result
        assert "keyword_hint_used" in result

    @pytest.mark.asyncio
    async def test_should_use_keyword_hint_for_declined(self, mock_llm_service, mock_render_prompt, mock_catalog):
        """Verify keyword hint is detected and used for 'declined' scenario."""
        mock_category = CategoryResult(category="general", reasoning="Authorization issue")
        mock_code = CodeSelectionResult(reason_code="A08", confidence=0.95, reasoning="Card declined")
        mock_llm_service.complete_structured = AsyncMock(side_effect=[mock_category, mock_code])

        task = {"dispute_id": DISPUTE_ID, "description": "My Amex card was declined at checkout"}
        result = await classify_dispute_v2(task)

        assert result["keyword_hint_used"] is True
        assert result["reason_code"] == "A08"

    @pytest.mark.asyncio
    async def test_should_use_preselected_network(self, mock_llm_service, mock_render_prompt, mock_catalog):
        """Verify pre-selected network from task is used."""
        mock_category = CategoryResult(category="product_not_received", reasoning="Test")
        mock_code = CodeSelectionResult(reason_code="13.1", confidence=0.9, reasoning="Test")
        mock_llm_service.complete_structured = AsyncMock(side_effect=[mock_category, mock_code])

        task = {
            "dispute_id": DISPUTE_ID,
            "description": "Order never arrived",
            "network": "visa"  # Pre-selected
        }
        result = await classify_dispute_v2(task)

        assert result["network"] == "visa"
        mock_catalog.get_codes_for_network_and_category.assert_called_with("visa", "product_not_received")

    @pytest.mark.asyncio
    async def test_should_fallback_to_network_codes_when_category_empty(self, mock_llm_service, mock_render_prompt, mock_catalog):
        """Verify fallback when no codes match network+category."""
        mock_catalog.get_codes_for_network_and_category.return_value = []  # No matches

        mock_category = CategoryResult(category="unrecognized", reasoning="Test")
        mock_code = CodeSelectionResult(reason_code="C08", confidence=0.8, reasoning="Fallback")
        mock_llm_service.complete_structured = AsyncMock(side_effect=[mock_category, mock_code])

        task = {"dispute_id": DISPUTE_ID, "description": "Unknown Amex charge"}
        result = await classify_dispute_v2(task)

        # Should have called network-only fallback
        mock_catalog.get_codes_for_network.assert_called_with("amex")

    @pytest.mark.asyncio
    async def test_should_calculate_deadline_correctly(self, mock_llm_service, mock_render_prompt, mock_catalog):
        """Verify deadline calculation from provided date."""
        mock_category = CategoryResult(category="product_not_received", reasoning="Test")
        mock_code = CodeSelectionResult(reason_code="C08", confidence=0.9, reasoning="Test")
        mock_llm_service.complete_structured = AsyncMock(side_effect=[mock_category, mock_code])

        task = {
            "dispute_id": DISPUTE_ID,
            "description": "Order never arrived",
            "current_date": "2023-01-01"
        }
        result = await classify_dispute_v2(task)

        assert result["deadline"] == "2023-01-15"  # 2023-01-01 + 14 days

    @pytest.mark.asyncio
    async def test_should_set_is_fraud_for_fraudulent_category(self, mock_llm_service, mock_render_prompt, mock_catalog):
        """Verify is_fraud flag is set correctly."""
        mock_catalog.get_codes_for_network_and_category.return_value = [
            {"code": "F24", "description": "No Cardholder Authorization", "category": "fraudulent"}
        ]

        mock_category = CategoryResult(category="fraudulent", reasoning="Fraud claim")
        mock_code = CodeSelectionResult(reason_code="F24", confidence=0.95, reasoning="Fraud")
        mock_llm_service.complete_structured = AsyncMock(side_effect=[mock_category, mock_code])

        task = {"dispute_id": DISPUTE_ID, "description": "My Amex card was stolen and used fraudulently"}
        result = await classify_dispute_v2(task)

        assert result["is_fraud"] is True
        assert result["category"] == "fraudulent"

    @pytest.mark.asyncio
    async def test_should_raise_runtimeerror_on_llm_failure(self, mock_llm_service, mock_render_prompt, mock_catalog):
        """Verify exceptions are caught and re-raised as RuntimeError."""
        mock_llm_service.complete_structured = AsyncMock(side_effect=Exception("LLM Error"))

        with pytest.raises(RuntimeError, match=f"Classification failed for dispute {DISPUTE_ID}"):
            await classify_dispute_v2({"dispute_id": DISPUTE_ID, "description": "Test"})


class TestKeywordHintsLoading:
    """Tests for keyword hints file loading."""

    def test_should_load_hints_from_file(self):
        hints = _load_keyword_hints()
        assert "_version" in hints
        assert "disambiguation_rules" in hints
        assert "network_family_hints" in hints
