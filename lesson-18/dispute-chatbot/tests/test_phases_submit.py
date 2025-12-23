import pytest
from backend.phases.submit import submit_dispute

@pytest.mark.asyncio
async def test_should_raise_typeerror_when_task_not_dict():
    """Test that submit_dispute raises TypeError when task is not a dictionary."""
    with pytest.raises(TypeError, match="task must be a dictionary"):
        await submit_dispute("not a dict")

@pytest.mark.asyncio
async def test_should_raise_valueerror_when_validation_passed_missing():
    """Test that submit_dispute raises ValueError when 'validation_passed' is missing."""
    with pytest.raises(ValueError, match="task must contain 'validation_passed'"):
        await submit_dispute({"some_other_key": "value"})

@pytest.mark.asyncio
async def test_should_return_mock_submission_status_on_success():
    """Test that submit_dispute returns mock status when inputs are valid."""
    task = {"validation_passed": True}
    result = await submit_dispute(task)
    
    assert isinstance(result, dict)
    assert result["submission_status"] == "success"
    assert "case_id" in result
    assert "submitted_at" in result

