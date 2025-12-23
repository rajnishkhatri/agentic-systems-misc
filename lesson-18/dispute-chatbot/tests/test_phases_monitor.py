import pytest
from backend.phases.monitor import monitor_dispute

@pytest.mark.asyncio
async def test_should_raise_typeerror_when_task_not_dict():
    """Test that monitor_dispute raises TypeError when task is not a dictionary."""
    with pytest.raises(TypeError, match="task must be a dictionary"):
        await monitor_dispute("not a dict")

@pytest.mark.asyncio
async def test_should_raise_valueerror_when_case_id_missing():
    """Test that monitor_dispute raises ValueError when 'case_id' is missing."""
    with pytest.raises(ValueError, match="task must contain 'case_id'"):
        await monitor_dispute({"some_other_key": "value"})

@pytest.mark.asyncio
async def test_should_return_mock_status_on_success():
    """Test that monitor_dispute returns mock status when inputs are valid."""
    task = {"case_id": "VIS-MOCK-123456"}
    result = await monitor_dispute(task)
    
    assert isinstance(result, dict)
    assert result["current_status"] == "pending"
    assert "last_checked" in result

