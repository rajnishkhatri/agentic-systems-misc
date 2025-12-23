import pytest
from backend.phases.validate import validate_evidence

@pytest.mark.asyncio
async def test_should_raise_typeerror_when_task_not_dict():
    """Test that validate_evidence raises TypeError when task is not a dictionary."""
    with pytest.raises(TypeError, match="task must be a dictionary"):
        await validate_evidence("not a dict")

@pytest.mark.asyncio
async def test_should_raise_valueerror_when_evidence_gathered_missing():
    """Test that validate_evidence raises ValueError when 'evidence_gathered' is missing."""
    with pytest.raises(ValueError, match="task must contain 'evidence_gathered'"):
        await validate_evidence({"some_other_key": "value"})

@pytest.mark.asyncio
async def test_should_return_mock_validation_results_on_success():
    """Test that validate_evidence returns mock results when inputs are valid."""
    task = {"evidence_gathered": True}
    result = await validate_evidence(task)
    
    assert isinstance(result, dict)
    assert result["validation_passed"] is True
    assert "scores" in result
    assert result["scores"]["evidence_quality"] == 0.9

