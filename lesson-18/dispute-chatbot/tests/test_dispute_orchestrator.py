import json
from unittest.mock import AsyncMock, patch

import pytest

from backend.orchestrators.dispute_orchestrator import DisputeOrchestrator
from backend.orchestrators.dispute_state import DisputeState

# Import fixtures locally to ensure they are available


@pytest.fixture
def mock_redis_store():
    with patch("backend.orchestrators.dispute_orchestrator.RedisStore") as MockRedis:
        mock_instance = MockRedis.return_value
        mock_instance.load_state = AsyncMock(return_value=None)
        mock_instance.save_state = AsyncMock()
        yield mock_instance

@pytest.mark.asyncio
async def test_should_initialize_with_6_states_when_created(mock_redis_store):
    """TDD: RED -> GREEN -> REFACTOR
    Test that the orchestrator initializes with the correct state configuration.
    """
    orchestrator = DisputeOrchestrator()
    assert orchestrator.name == "dispute_orchestrator"
    assert orchestrator.initial_state == DisputeState.CLASSIFY
    assert len(orchestrator.states) == 6
    # Verify all handlers are registered
    assert len(orchestrator.state_handlers) == 5

@pytest.mark.asyncio
async def test_should_complete_all_phases_when_happy_path(fraud_dispute_fixture, mock_redis_store):
    """TDD: RED -> GREEN -> REFACTOR
    Test the happy path execution using a fraud dispute fixture.
    """
    # Mock handlers
    mock_classify = AsyncMock(return_value={
        "reason_code": "10.4",
        "network": "visa",
        "deadline": "2025-01-01"
    })
    mock_gather = AsyncMock(return_value={
        "evidence_gathered": True,
        "transaction_history": []
    })
    mock_validate = AsyncMock(return_value={
        "validation_passed": True,
        "scores": {"quality": 0.9}
    })
    mock_submit = AsyncMock(return_value={
        "submission_status": "success",
        "case_id": "VIS-123"
    })
    mock_monitor = AsyncMock(return_value={
        "current_status": "pending"
    })

    orchestrator = DisputeOrchestrator()

    # Override handlers for testing to avoid actual logic execution
    orchestrator.register_state_handler(DisputeState.CLASSIFY, mock_classify)
    orchestrator.register_state_handler(DisputeState.GATHER_EVIDENCE, mock_gather)
    orchestrator.register_state_handler(DisputeState.VALIDATE, mock_validate)
    orchestrator.register_state_handler(DisputeState.SUBMIT, mock_submit)
    orchestrator.register_state_handler(DisputeState.MONITOR, mock_monitor)

    task = {
        "task_id": "test_happy_path",
        "dispute_id": fraud_dispute_fixture["id"],
        "description": "fraud dispute"
    }

    result = await orchestrator.execute(task)

    assert result["status"] == "success"
    assert result["final_state"] == DisputeState.MONITOR

    # Verify execution order
    mock_classify.assert_called_once()
    mock_gather.assert_called_once()
    mock_validate.assert_called_once()
    mock_submit.assert_called_once()
    mock_monitor.assert_called_once()

    # Verify context accumulation
    # Check that gather received output from classify
    classify_output = mock_classify.return_value
    gather_call_args = mock_gather.call_args[0][0]
    assert gather_call_args["reason_code"] == classify_output["reason_code"]

    # Check final output contains data from all phases
    final_output = result["final_output"]
    assert final_output["reason_code"] == "10.4"
    assert final_output["evidence_gathered"] is True
    assert final_output["submission_status"] == "success"

@pytest.mark.asyncio
async def test_should_escalate_when_validation_fails(mock_redis_store):
    """TDD: RED -> GREEN -> REFACTOR
    Test escalation logic when validation fails.
    """
    # Setup orchestrator with mocked handlers
    orchestrator = DisputeOrchestrator()

    mock_classify = AsyncMock(return_value={})
    mock_gather = AsyncMock(return_value={})
    # Validation fails
    mock_validate = AsyncMock(return_value={"validation_passed": False})

    orchestrator.register_state_handler(DisputeState.CLASSIFY, mock_classify)
    orchestrator.register_state_handler(DisputeState.GATHER_EVIDENCE, mock_gather)
    orchestrator.register_state_handler(DisputeState.VALIDATE, mock_validate)

    task = {
        "task_id": "test_escalate",
        "dispute_id": "test_escalate_id",
        "description": "dispute"
    }
    result = await orchestrator.execute(task)

    assert result["status"] == "success"
    assert result["final_state"] == DisputeState.ESCALATE

    # Should not reach SUBMIT
    assert DisputeState.SUBMIT not in result["state_history"]

@pytest.mark.asyncio
async def test_should_retry_3_times_when_classify_fails(mock_redis_store):
    """TDD: RED -> GREEN -> REFACTOR
    Test retry logic with 3 attempts on failure.
    """
    orchestrator = DisputeOrchestrator()

    # Classify fails twice then succeeds
    mock_classify = AsyncMock(side_effect=[ValueError("Fail 1"), ValueError("Fail 2"), {"result": "ok"}])

    orchestrator.register_state_handler(DisputeState.CLASSIFY, mock_classify)

    # Mock others to return minimal
    orchestrator.register_state_handler(DisputeState.GATHER_EVIDENCE, AsyncMock(return_value={}))
    orchestrator.register_state_handler(DisputeState.VALIDATE, AsyncMock(return_value={"validation_passed": False})) # Short circuit to ESCALATE

    task = {
        "task_id": "test_retry",
        "dispute_id": "test_retry_id",
        "description": "retry test"
    }
    result = await orchestrator.execute(task)

    assert mock_classify.call_count == 3
    assert result["status"] == "success"

@pytest.mark.asyncio
async def test_should_persist_state_when_redis_configured(mock_redis_store):
    """TDD: RED -> GREEN -> REFACTOR
    Test state persistence when Redis is configured.
    """
    mock_redis_store.load_state.return_value = {"state": "loaded"}

    orchestrator = DisputeOrchestrator(redis_url="redis://test")

    # Test save
    await orchestrator._save_state_checkpoint("task1", "STATE", {"data": 1})
    mock_redis_store.save_state.assert_called_with("task1", {"data": 1})

    # Test load
    state = await orchestrator.load_state("task1")
    assert state == {"state": "loaded"}

@pytest.mark.asyncio
async def test_should_recover_workflow_from_checkpoint(tmp_path, mock_redis_store):
    """Test workflow recovery from checkpoint."""
    # Ensure Redis returns None so fallback logic runs or we simulate Redis miss
    mock_redis_store.load_state.return_value = None

    # Setup orchestrator with temp checkpoint dir
    orchestrator = DisputeOrchestrator(checkpoint_dir=tmp_path)

    # Create a fake checkpoint file
    task_id = "test_recovery"
    state = {
        "task_id": task_id,
        "current_state": DisputeState.GATHER_EVIDENCE,
        "state_history": [DisputeState.CLASSIFY, DisputeState.GATHER_EVIDENCE],
        "audit_trail": [],
        "invariant_violations": [],
        "accumulated_data": {"reason_code": "10.4"}
    }

    checkpoint_path = tmp_path / f"{task_id}_state_{DisputeState.GATHER_EVIDENCE}.json"
    checkpoint_path.write_text(json.dumps(state))

    # Verify recovery
    recovered = await orchestrator.recover_workflow_from_checkpoint(task_id)
    assert recovered is not None
    assert recovered["current_state"] == DisputeState.GATHER_EVIDENCE
    assert recovered["accumulated_data"]["reason_code"] == "10.4"

    # Verify orchestrator state is updated
    assert orchestrator.current_state == DisputeState.GATHER_EVIDENCE

@pytest.mark.asyncio
async def test_should_resume_execution_from_checkpoint(tmp_path, mock_redis_store):
    """Test that execution resumes from checkpoint."""
    # Ensure Redis returns None
    mock_redis_store.load_state.return_value = None

    orchestrator = DisputeOrchestrator(checkpoint_dir=tmp_path)

    task_id = "test_resume"

    # Create checkpoint at VALIDATE state
    # This simulates that VALIDATE has just completed
    state = {
        "task_id": task_id,
        "current_state": DisputeState.VALIDATE,
        "state_history": [DisputeState.CLASSIFY, DisputeState.GATHER_EVIDENCE, DisputeState.VALIDATE],
        "audit_trail": [],
        "invariant_violations": [],
        "accumulated_data": {
            "reason_code": "10.4",
            "evidence_gathered": True,
            "validation_passed": True
        }
    }

    # Write checkpoint
    checkpoint_path = tmp_path / f"{task_id}_state_{DisputeState.VALIDATE}.json"
    checkpoint_path.write_text(json.dumps(state))

    # Mock handlers
    # We only expect SUBMIT and MONITOR to run
    mock_classify = AsyncMock()
    mock_gather = AsyncMock()
    mock_validate = AsyncMock()

    mock_submit = AsyncMock(return_value={"submission_status": "success", "case_id": "123"})
    mock_monitor = AsyncMock(return_value={"current_status": "pending"})

    orchestrator.register_state_handler(DisputeState.CLASSIFY, mock_classify)
    orchestrator.register_state_handler(DisputeState.GATHER_EVIDENCE, mock_gather)
    orchestrator.register_state_handler(DisputeState.VALIDATE, mock_validate)
    orchestrator.register_state_handler(DisputeState.SUBMIT, mock_submit)
    orchestrator.register_state_handler(DisputeState.MONITOR, mock_monitor)

    task = {"task_id": task_id}

    result = await orchestrator.execute(task)

    assert result["status"] == "success"

    # Verify previous handlers NOT called
    mock_classify.assert_not_called()
    mock_gather.assert_not_called()
    mock_validate.assert_not_called()

    # Verify subsequent handlers CALLED
    mock_submit.assert_called_once()
    mock_monitor.assert_called_once()
