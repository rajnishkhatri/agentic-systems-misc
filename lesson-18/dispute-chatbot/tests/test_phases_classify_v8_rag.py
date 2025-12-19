import pytest
from unittest.mock import AsyncMock, Mock, patch

from backend.phases.classify_v8_rag import (
    classify_dispute_v8_rag,
    CategoryResultV8Rag,
    CodeSelectionResult,
    BranchAResult, BranchBResult, BranchCResult, SynthesisResult
)

DISPUTE_ID = "DIS-12345"

@pytest.fixture
def mock_llm_service():
    with patch("backend.phases.classify_v8_rag.get_default_service") as mock_get:
        mock_service = Mock()
        mock_service.routing_model = "mock-routing-model"
        mock_get.return_value = mock_service
        yield mock_service

@pytest.fixture
def mock_render_prompt():
    with patch("backend.phases.classify_v8_rag.render_prompt") as mock_render:
        mock_render.return_value = "Mock Prompt"
        yield mock_render

@pytest.fixture
def mock_rag_retriever():
    with patch("backend.phases.classify_v8_rag.get_rag_retriever") as mock_get:
        mock_retriever = Mock()
        mock_retriever.retrieve_similar.return_value = [
            {"description": "Past case", "category": "fraudulent", "similarity_score": 0.9}
        ]
        mock_get.return_value = mock_retriever
        yield mock_retriever

@pytest.fixture
def mock_catalog():
    with patch("backend.phases.classify_v8_rag.get_reason_code_catalog") as mock_get_catalog:
        mock_instance = Mock()
        mock_instance.get_codes_for_network_and_category.return_value = [
            {"code": "F24", "description": "Fraud", "category": "fraudulent"}
        ]
        mock_instance.get_codes_for_network.return_value = [
             {"code": "F24", "description": "Fraud", "category": "fraudulent"}
        ]
        mock_get_catalog.return_value = mock_instance
        yield mock_instance

@pytest.mark.asyncio
async def test_should_classify_with_v8_rag(mock_llm_service, mock_render_prompt, mock_rag_retriever, mock_catalog):
    # Setup mock responses
    mock_category = CategoryResultV8Rag(
        branch_a=BranchAResult(conclusion="denied"),
        branch_b=BranchBResult(complaint_type="unspecified"),
        branch_c=BranchCResult(persona="accusatory"),
        synthesis=SynthesisResult(branch_agreement=0.9, reasoning="Fraud"),
        category="fraudulent",
        reason_code_group="fraud",
        confidence=0.95,
        confidence_rationale="Strong fraud indicators"
    )
    mock_code = CodeSelectionResult(reason_code="F24", confidence=0.95, reasoning="Matches fraud")

    mock_llm_service.complete_structured = AsyncMock(side_effect=[mock_category, mock_code])

    task = {"dispute_id": DISPUTE_ID, "description": "Fraudulent charge on my card"}
    result = await classify_dispute_v8_rag(task)

    # Verify RAG was called
    mock_rag_retriever.retrieve_similar.assert_called_once()
    
    # Verify prompt rendering includes examples
    # First call is identify_category, second is select_code
    assert mock_render_prompt.call_count == 2
    first_call_kwargs = mock_render_prompt.call_args_list[0].kwargs
    assert "examples" in first_call_kwargs
    assert len(first_call_kwargs["examples"]) == 1
    
    assert result["category"] == "fraudulent"
    assert result["classifier_version"] == "8.0.0-RAG"
    assert result["reason_code_group"] == "fraud"

