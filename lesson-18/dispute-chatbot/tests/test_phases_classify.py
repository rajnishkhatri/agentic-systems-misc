import datetime
import pytest
from unittest.mock import AsyncMock, Mock, patch

from backend.phases.classify import classify_dispute, ClassificationResult

# Mock data
DISPUTE_ID = "DIS-12345"
DESCRIPTION = "Customer claims they never received the item."
VALID_TASK = {"dispute_id": DISPUTE_ID, "description": DESCRIPTION}

@pytest.fixture
def mock_llm_service():
    with patch("backend.phases.classify.get_default_service") as mock_get:
        mock_service = Mock()
        mock_service.routing_model = "mock-routing-model"
        mock_get.return_value = mock_service
        yield mock_service

@pytest.fixture
def mock_render_prompt():
    with patch("backend.phases.classify.render_prompt") as mock_render:
        mock_render.return_value = "Mock Prompt"
        yield mock_render

@pytest.fixture
def mock_catalog():
    with patch("backend.phases.classify.get_reason_code_catalog") as mock_get_catalog:
        mock_instance = Mock()
        mock_instance.get_codes_for_network.return_value = [
            {"code": "13.1", "description": "PNR", "category": "product_not_received"}
        ]
        mock_get_catalog.return_value = mock_instance
        yield mock_instance

@pytest.mark.asyncio
async def test_should_raise_typeerror_when_task_is_not_dict():
    """Verify TypeError is raised when task is not a dictionary."""
    with pytest.raises(TypeError, match="task must be a dictionary"):
        await classify_dispute(None)

@pytest.mark.asyncio
async def test_should_raise_valueerror_when_dispute_id_missing():
    """Verify ValueError is raised when dispute_id is missing."""
    with pytest.raises(ValueError, match="task must contain 'dispute_id'"):
        await classify_dispute({"description": DESCRIPTION})

@pytest.mark.asyncio
async def test_should_raise_valueerror_when_description_missing():
    """Verify ValueError is raised when description is missing."""
    with pytest.raises(ValueError, match="task must contain 'description'"):
        await classify_dispute({"dispute_id": DISPUTE_ID})

@pytest.mark.asyncio
async def test_should_classify_fraud_dispute_correctly(mock_llm_service, mock_render_prompt, mock_catalog):
    """Verify correct classification result structure and values."""
    # Setup mock result
    mock_result = ClassificationResult(
        reason_code="10.4",
        network="visa",
        is_fraud=True,
        confidence=0.95,
        reasoning="Matches fraud pattern"
    )
    mock_llm_service.complete_structured = AsyncMock(return_value=mock_result)

    # Execute
    result = await classify_dispute(VALID_TASK)

    # Verify
    assert result["reason_code"] == "10.4"
    assert result["network"] == "visa"
    assert result["classification_confidence"] == 0.95
    assert result["classification_reasoning"] == "Matches fraud pattern"
    
    # Verify deadline logic (default: now + 14 days)
    assert isinstance(result["deadline"], str)

    # Verify LLM call
    mock_llm_service.complete_structured.assert_called_once()
    call_args = mock_llm_service.complete_structured.call_args
    assert call_args.kwargs["response_model"] == ClassificationResult
    assert call_args.kwargs["model"] == "mock-routing-model"

@pytest.mark.asyncio
async def test_should_render_prompt_with_network_and_codes(mock_llm_service, mock_render_prompt, mock_catalog):
    """Verify prompt template rendering is called with correct arguments including network and codes."""
    mock_llm_service.complete_structured = AsyncMock(return_value=ClassificationResult(
        reason_code="10.4", network="visa", is_fraud=True, confidence=0.95, reasoning="Reason"
    ))

    # Setup specific codes for this test
    mock_catalog.get_codes_for_network.return_value = [
        {"code": "CODE1", "description": "Desc1", "category": "cat1"}
    ]

    await classify_dispute(VALID_TASK)

    # Check that network was identified as 'visa' (default) and codes were passed
    mock_render_prompt.assert_called_once_with(
        "DisputeClassifier_classify.j2",
        dispute_id=DISPUTE_ID,
        description=DESCRIPTION,
        network="visa",
        candidate_codes=[{"code": "CODE1", "description": "Desc1", "category": "cat1"}]
    )

@pytest.mark.asyncio
async def test_should_identify_amex_network(mock_llm_service, mock_render_prompt, mock_catalog):
    """Verify network identification logic detects Amex."""
    mock_llm_service.complete_structured = AsyncMock(return_value=ClassificationResult(
        reason_code="A01", network="amex", is_fraud=False, confidence=0.9, reasoning="Reason"
    ))
    
    amex_task = {"dispute_id": DISPUTE_ID, "description": "Charge on American Express card unknown."}
    
    await classify_dispute(amex_task)
    
    mock_catalog.get_codes_for_network.assert_called_with("amex")
    mock_render_prompt.assert_called_once()
    assert mock_render_prompt.call_args[1]["network"] == "amex"

@pytest.mark.asyncio
async def test_should_raise_runtimeerror_on_llm_failure(mock_llm_service, mock_render_prompt, mock_catalog):
    """Verify exceptions are caught and re-raised as RuntimeError."""
    mock_llm_service.complete_structured = AsyncMock(side_effect=Exception("LLM Error"))

    with pytest.raises(RuntimeError, match=f"Classification failed for dispute {DISPUTE_ID}"):
        await classify_dispute(VALID_TASK)

@pytest.mark.asyncio
async def test_deadline_calculation_logic(mock_llm_service, mock_render_prompt, mock_catalog):
    """Verify deadline is calculated correctly from provided current_date."""
    mock_llm_service.complete_structured = AsyncMock(return_value=ClassificationResult(
        reason_code="10.4", network="visa", is_fraud=True, confidence=0.95, reasoning="Reason"
    ))

    task_with_date = VALID_TASK.copy()
    task_with_date["current_date"] = "2023-01-01"

    result = await classify_dispute(task_with_date)

    # 2023-01-01 + 14 days = 2023-01-15
    assert result["deadline"] == "2023-01-15"

@pytest.mark.asyncio
async def test_deadline_calculation_invalid_date(mock_llm_service, mock_render_prompt, mock_catalog):
    """Verify fallback to current time when date string is invalid."""
    mock_llm_service.complete_structured = AsyncMock(return_value=ClassificationResult(
        reason_code="10.4", network="visa", is_fraud=True, confidence=0.95, reasoning="Reason"
    ))

    task_with_invalid_date = VALID_TASK.copy()
    task_with_invalid_date["current_date"] = "invalid-date"

    # We patch datetime to verify fallback behavior
    fixed_now = datetime.datetime(2023, 10, 1)
    with patch("backend.phases.classify.datetime") as mock_datetime:
        mock_datetime.datetime.now.return_value = fixed_now
        # datetime.timedelta must be real
        mock_datetime.timedelta = datetime.timedelta
        # datetime.strptime still needs to raise ValueError
        mock_datetime.datetime.strptime.side_effect = ValueError

        result = await classify_dispute(task_with_invalid_date)
        
        # 2023-10-01 + 14 days = 2023-10-15
        assert result["deadline"] == "2023-10-15"
