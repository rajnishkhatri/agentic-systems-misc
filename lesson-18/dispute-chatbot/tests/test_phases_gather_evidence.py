import pytest
from backend.phases.gather_evidence import gather_evidence

@pytest.mark.asyncio
async def test_should_raise_typeerror_when_task_not_dict():
    """Test that gather_evidence raises TypeError when task is not a dictionary."""
    with pytest.raises(TypeError, match="task must be a dictionary"):
        await gather_evidence("not a dict")

@pytest.mark.asyncio
async def test_should_raise_valueerror_when_reason_code_missing():
    """Test that gather_evidence raises ValueError when 'reason_code' is missing."""
    with pytest.raises(ValueError, match="task must contain 'reason_code'"):
        await gather_evidence({"some_other_key": "value"})

@pytest.mark.asyncio
async def test_should_return_mock_evidence_on_success():
    """Test that gather_evidence returns mock evidence when inputs are valid."""
    task = {"reason_code": "10.4"}
    result = await gather_evidence(task)
    
    assert isinstance(result, dict)
    assert result["evidence_gathered"] is True
    assert "transaction_history" in result
    assert "shipping_proof" in result
    assert "customer_profile" in result

