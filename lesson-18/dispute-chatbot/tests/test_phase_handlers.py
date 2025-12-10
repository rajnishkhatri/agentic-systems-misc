import pytest
import datetime
from unittest.mock import AsyncMock, patch
from backend.phases.classify import classify_dispute
from backend.phases.gather_evidence import gather_evidence
from backend.phases.validate import validate_evidence
from backend.phases.submit import submit_dispute
from backend.phases.monitor import monitor_dispute

# Import fixtures locally to ensure they are available
from tests.fixtures.dispute_fixtures import (
    example_data,
    fraud_dispute_fixture,
    pnr_dispute_fixture,
    ce3_dispute_fixture,
    subscription_dispute_fixture,
    duplicate_dispute_fixture,
    mastercard_dispute_fixture
)

@pytest.mark.asyncio
class TestClassifyPhase:
    """Tests for the classify_dispute phase handler."""

    async def test_should_raise_typeerror_when_task_not_dict(self):
        """Test defensive coding: input must be a dict."""
        with pytest.raises(TypeError, match="task must be a dictionary"):
            await classify_dispute("not a dict")

    async def test_should_return_classification_when_valid_fraud_dispute(self, fraud_dispute_fixture):
        """Happy path for fraud dispute."""
        # Mock LLM service
        with patch("backend.phases.classify.get_default_service") as mock_get_service:
            mock_service = AsyncMock()
            mock_get_service.return_value = mock_service
            
            # Setup mock return value
            mock_result = AsyncMock()
            mock_result.reason_code = "10.4"
            mock_result.network = "visa"
            mock_result.confidence = 0.95
            mock_result.reasoning = "Fraud pattern detected"
            mock_service.complete_structured.return_value = mock_result
            
            # Use data from fixture
            task = {"dispute_id": fraud_dispute_fixture["id"], "description": "Unrecognized charge"}
            result = await classify_dispute(task)
            
            assert result["reason_code"] == "10.4"
            assert result["network"] == "visa"
            assert "deadline" in result

    async def test_should_handle_missing_description(self):
        """Edge case: description missing should be handled gracefully."""
        with patch("backend.phases.classify.get_default_service") as mock_get_service:
            mock_service = AsyncMock()
            mock_get_service.return_value = mock_service
            mock_result = AsyncMock()
            mock_result.reason_code = "10.4"
            mock_result.network = "visa"
            mock_service.complete_structured.return_value = mock_result
            
            task = {"dispute_id": "123"} # No description
            result = await classify_dispute(task)
            assert result["reason_code"] == "10.4"

@pytest.mark.asyncio
class TestGatherEvidencePhase:
    """Tests for the gather_evidence phase handler."""

    async def test_should_raise_typeerror_when_task_not_dict(self):
        with pytest.raises(TypeError, match="task must be a dictionary"):
            await gather_evidence(None)

    async def test_should_raise_valueerror_when_reason_code_missing(self):
        with pytest.raises(ValueError, match="task must contain 'reason_code'"):
            await gather_evidence({"dispute_id": "123"})

    async def test_should_return_evidence_when_valid_input(self):
        task = {"reason_code": "10.4"}
        result = await gather_evidence(task)
        assert result["evidence_gathered"] is True

@pytest.mark.asyncio
class TestValidatePhase:
    """Tests for the validate_evidence phase handler."""

    async def test_should_raise_typeerror_when_task_not_dict(self):
        with pytest.raises(TypeError, match="task must be a dictionary"):
            await validate_evidence([])

    async def test_should_raise_valueerror_when_evidence_data_missing(self):
        """Should fail if there is no evidence to validate."""
        # Assuming we require 'evidence_gathered' or similar key from previous phase
        # For now, let's say we check for 'evidence_gathered' key based on gather_evidence output
        with pytest.raises(ValueError, match="task must contain 'evidence_gathered'"):
             await validate_evidence({"random": "key"})

    async def test_should_return_validation_passed_when_evidence_complete(self):
        task = {"evidence_gathered": True}
        result = await validate_evidence(task)
        assert result["validation_passed"] is True

@pytest.mark.asyncio
class TestSubmitPhase:
    """Tests for the submit_dispute phase handler."""

    async def test_should_raise_typeerror_when_task_not_dict(self):
        with pytest.raises(TypeError, match="task must be a dictionary"):
            await submit_dispute("string")

    async def test_should_raise_valueerror_when_validation_missing(self):
        with pytest.raises(ValueError, match="task must contain 'validation_passed'"):
             await submit_dispute({"some": "data"})

    async def test_should_return_submission_when_valid(self):
        task = {"validation_passed": True, "case_id": "123"}
        result = await submit_dispute(task)
        assert result["submission_status"] == "success"

@pytest.mark.asyncio
class TestMonitorPhase:
    """Tests for the monitor_dispute phase handler."""

    async def test_should_raise_typeerror_when_task_not_dict(self):
        with pytest.raises(TypeError, match="task must be a dictionary"):
            await monitor_dispute(123)

    async def test_should_raise_valueerror_when_case_id_missing(self):
        with pytest.raises(ValueError, match="task must contain 'case_id'"):
            await monitor_dispute({"status": "pending"})

    async def test_should_return_status_when_valid(self):
        task = {"case_id": "VIS-12345"}
        result = await monitor_dispute(task)
        assert "current_status" in result

