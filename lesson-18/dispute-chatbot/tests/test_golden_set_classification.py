import json
import pytest
from pathlib import Path
from unittest.mock import AsyncMock, patch, Mock
from backend.phases.classify import classify_dispute, CodeSelectionResult, CategoryResult

# Load golden set data
# This assumes the test is running from a context where we can resolve the path relative to this file
# File structure:
# lesson-18/dispute-chatbot/tests/test_golden_set_classification.py
# lesson-18/dispute-chatbot/synthetic_data/phase1/golden_set/diverse_classification_labels.json
DATA_PATH = Path(__file__).parents[1] / "synthetic_data/phase1/golden_set/diverse_classification_labels.json"

def load_test_cases():
    """Load classification test cases from the golden set JSON."""
    if not DATA_PATH.exists():
        # Fallback if running from a different root or if file is missing (though it should exist)
        return []
    
    with open(DATA_PATH, "r") as f:
        return json.load(f)

test_cases = load_test_cases()

@pytest.mark.asyncio
@pytest.mark.parametrize("case", test_cases)
async def test_classify_golden_set(case):
    """
    Data-driven test to verify classify_dispute against the golden set.
    
    This mocks the LLM response to return the expected 'true_reason_code' and 'network'
    to verify that the phase handler correctly orchestrates the input and output
    given a successful LLM classification.
    """
    # Extract data from the case
    dispute_id = case["dispute_id"]
    description = case["description"]
    expected_reason = case["true_reason_code"]
    expected_network = case["network"]

    # Mock the LLM service
    with patch("backend.phases.classify.get_default_service") as mock_get_service:
        mock_service = Mock()
        # Mock the routing_model attribute if accessed
        mock_service.routing_model = "mock-routing-model"
        mock_get_service.return_value = mock_service

        # Mock Category ID (Step 2)
        mock_category_result = CategoryResult(
            category="fraudulent", # Assuming fraud for golden set mostly
            reasoning="Mocked category reasoning"
        )
        
        # Mock Code Selection (Step 3)
        mock_code_result = CodeSelectionResult(
            reason_code=expected_reason,
            confidence=0.95,
            reasoning=f"Mocked classification for {dispute_id}"
        )
        
        # Mock complete_structured to return different types based on response_model
        async def side_effect(*args, **kwargs):
            response_model = kwargs.get("response_model")
            if response_model == CategoryResult:
                return mock_category_result
            elif response_model == CodeSelectionResult:
                return mock_code_result
            return None

        mock_service.complete_structured = AsyncMock(side_effect=side_effect)

        # Call the function under test
        task = {"dispute_id": dispute_id, "description": description}
        result = await classify_dispute(task)

        # Print input and output for report capture
        print(f"\nTest Input (Case): {json.dumps(case, indent=2)}")
        print(f"Test Output (Result): {json.dumps(result, indent=2)}")

        # Assertions
        assert result["reason_code"] == expected_reason
        assert result["network"] == expected_network.lower()
        assert "deadline" in result
        assert result["classification_confidence"] == 0.95

