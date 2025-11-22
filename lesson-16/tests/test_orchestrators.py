"""Test suite for all 5 orchestration patterns.

This module provides comprehensive tests for:
- FR3.1: Sequential Orchestration
- FR3.2: Hierarchical Delegation
- FR3.3: Iterative Refinement (ReAct/Reflexion)
- FR3.4: State Machine Orchestration
- FR3.5: Voting/Ensemble Orchestration

Test Infrastructure:
- Fixtures for mock agents with configurable behavior
- Sample financial workflow tasks (invoice, fraud, reconciliation)
- Integration with reliability components (retry, circuit breaker, checkpointing)
- Shared utilities for testing orchestrator patterns

Following TDD methodology: Write tests BEFORE implementation (RED → GREEN → REFACTOR)
Test naming convention: test_should_[result]_when_[condition]()
"""

from __future__ import annotations

import asyncio
import tempfile
from collections.abc import AsyncGenerator, Callable
from pathlib import Path
from typing import Any
from unittest.mock import AsyncMock

import pytest

# =============================================================================
# Test Fixtures - Mock Agents
# =============================================================================


@pytest.fixture
def mock_successful_agent() -> AsyncMock:
    """Provide a mock agent that always succeeds.

    Returns:
        AsyncMock configured to return success response
    """
    mock = AsyncMock()
    mock.return_value = {"status": "success", "result": "Agent completed successfully"}
    return mock


@pytest.fixture
def mock_failing_agent() -> AsyncMock:
    """Provide a mock agent that always fails.

    Returns:
        AsyncMock configured to raise RuntimeError
    """
    mock = AsyncMock()
    mock.side_effect = RuntimeError("Agent execution failed")
    return mock


@pytest.fixture
def mock_slow_agent() -> AsyncMock:
    """Provide a mock agent with configurable delay.

    Returns:
        AsyncMock that sleeps before returning
    """

    async def slow_response(*args: Any, **kwargs: Any) -> dict[str, Any]:
        """Simulate slow agent response.

        Returns:
            Success response after delay
        """
        delay = kwargs.get("delay", 0.5)
        await asyncio.sleep(delay)
        return {"status": "success", "result": "Slow agent completed", "delay": delay}

    mock = AsyncMock(side_effect=slow_response)
    return mock


@pytest.fixture
def mock_intermittent_agent() -> Callable[[int], AsyncMock]:
    """Factory for agents that fail N times then succeed.

    Returns:
        Factory function creating intermittent failure agents
    """

    def _create_agent(fail_count: int) -> AsyncMock:
        """Create agent that fails fail_count times, then succeeds.

        Args:
            fail_count: Number of failures before success

        Returns:
            AsyncMock with configured side_effect
        """
        mock = AsyncMock()
        failures = [RuntimeError(f"Failure {i + 1}") for i in range(fail_count)]
        mock.side_effect = failures + [{"status": "success", "result": "Recovered after retries"}]
        return mock

    return _create_agent


@pytest.fixture
def mock_invoice_extraction_agent() -> AsyncMock:
    """Mock agent for invoice extraction use case.

    Returns:
        AsyncMock returning invoice data matching InvoiceExtraction schema
    """
    mock = AsyncMock()
    mock.return_value = {
        "vendor_name": "Acme Corp",
        "invoice_number": "INV-2024-001",
        "total_amount": 1250.00,
        "line_items": [
            {"description": "Widget A", "quantity": 10, "unit_price": 100.0, "total": 1000.0},
            {"description": "Widget B", "quantity": 5, "unit_price": 50.0, "total": 250.0},
        ],
    }
    return mock


@pytest.fixture
def mock_fraud_detection_agent() -> AsyncMock:
    """Mock agent for fraud detection use case.

    Returns:
        AsyncMock returning fraud analysis results
    """
    mock = AsyncMock()
    mock.return_value = {
        "transaction_id": "TXN-12345",
        "is_fraud": False,
        "fraud_score": 0.15,
        "risk_factors": ["high_velocity", "new_merchant"],
        "confidence": 0.92,
    }
    return mock


@pytest.fixture
def mock_reconciliation_agent() -> AsyncMock:
    """Mock agent for account reconciliation use case.

    Returns:
        AsyncMock returning reconciliation match results
    """
    mock = AsyncMock()
    mock.return_value = {
        "bank_transaction_id": "BANK-001",
        "ledger_entry_id": "LED-001",
        "match_confidence": 0.98,
        "discrepancy_amount": 0.0,
        "resolution_status": "perfect_match",
    }
    return mock


# =============================================================================
# Test Fixtures - Financial Workflow Tasks
# =============================================================================


@pytest.fixture
def sample_invoice_task() -> dict[str, Any]:
    """Provide sample invoice processing task.

    Returns:
        Invoice task dictionary with OCR text and expected fields
    """
    return {
        "task_id": "INV-TASK-001",
        "task_type": "invoice_extraction",
        "input_data": {
            "ocr_text": "INVOICE\nVendor: Acme Corp\nInvoice #: INV-2024-001\nAmount: $1,250.00",
            "image_path": "/data/invoices/inv_001.pdf",
        },
        "gold_label": {
            "vendor_name": "Acme Corp",
            "invoice_number": "INV-2024-001",
            "total_amount": 1250.00,
        },
        "difficulty": "medium",
        "challenge_types": ["ocr_noise", "formatting_variation"],
    }


@pytest.fixture
def sample_fraud_task() -> dict[str, Any]:
    """Provide sample fraud detection task.

    Returns:
        Fraud detection task with transaction data
    """
    return {
        "task_id": "FRD-TASK-001",
        "task_type": "fraud_detection",
        "input_data": {
            "transaction_id": "TXN-12345",
            "amount": 450.00,
            "merchant": "Online Electronics Store",
            "user_id": "USER-789",
            "timestamp": "2024-11-22T10:30:00Z",
            "location": "New York, NY",
        },
        "gold_label": {"is_fraud": False, "fraud_type": None},
        "difficulty": "easy",
        "challenge_types": ["legitimate_high_velocity"],
    }


@pytest.fixture
def sample_reconciliation_task() -> dict[str, Any]:
    """Provide sample account reconciliation task.

    Returns:
        Reconciliation task with bank and ledger entries
    """
    return {
        "task_id": "REC-TASK-001",
        "task_type": "reconciliation",
        "input_data": {
            "bank_transactions": [
                {"id": "BANK-001", "date": "2024-11-20", "amount": 1234.56, "description": "Payment received"},
            ],
            "ledger_entries": [
                {"id": "LED-001", "date": "2024-11-20", "amount": 1234.56, "description": "Customer payment"},
            ],
        },
        "gold_label": {
            "matches": [{"bank_id": "BANK-001", "ledger_id": "LED-001", "confidence": 1.0}],
            "discrepancies": [],
        },
        "difficulty": "easy",
        "challenge_types": ["perfect_match"],
    }


@pytest.fixture
def complex_invoice_batch() -> list[dict[str, Any]]:
    """Provide batch of invoices with varying difficulty.

    Returns:
        List of 5 invoice tasks (2 easy, 2 medium, 1 hard)
    """
    return [
        {
            "task_id": f"INV-BATCH-{i:03d}",
            "task_type": "invoice_extraction",
            "input_data": {"ocr_text": f"Invoice {i} data", "image_path": f"/data/inv_{i}.pdf"},
            "difficulty": ["easy", "easy", "medium", "medium", "hard"][i],
            "challenge_types": [["none"], ["formatting"], ["ocr_noise"], ["missing_fields"], ["duplicate"]][i],
        }
        for i in range(5)
    ]


# =============================================================================
# Test Fixtures - Reliability Component Integration
# =============================================================================


@pytest.fixture
def temp_checkpoint_dir() -> AsyncGenerator[Path, None]:
    """Provide temporary directory for checkpoint storage.

    Yields:
        Path to temporary checkpoint directory
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def mock_circuit_breaker():
    """Provide configured circuit breaker for testing.

    Returns:
        CircuitBreaker instance with test-friendly settings
    """
    from backend.reliability.circuit_breaker import CircuitBreaker

    return CircuitBreaker(
        failure_threshold=3,  # Open after 3 failures
        timeout=2.0,  # 2 second timeout before half-open
    )


@pytest.fixture
def mock_audit_logger():
    """Provide audit logger for workflow tracing.

    Returns:
        AuditLogger instance for test workflow
    """
    from backend.reliability.audit_log import AuditLogger

    return AuditLogger(workflow_id="TEST-WF-001")


@pytest.fixture
def mock_fallback_handler():
    """Provide fallback handler with cache and default strategies.

    Returns:
        FallbackHandler with test configuration
    """
    from backend.reliability.fallback import FallbackHandler

    fallback = FallbackHandler()
    # Pre-populate cache with test data
    fallback.cache["test_key"] = {"status": "success", "result": "Cached response", "source": "cache"}
    return fallback


# =============================================================================
# Test Fixtures - Orchestrator Testing Utilities
# =============================================================================


@pytest.fixture
def mock_agent_registry() -> dict[str, AsyncMock]:
    """Provide registry of named mock agents for orchestrators.

    Returns:
        Dictionary mapping agent names to AsyncMock instances
    """
    return {
        "extractor": AsyncMock(return_value={"extracted_data": {"vendor": "Acme"}}),
        "validator": AsyncMock(return_value={"is_valid": True, "validation_errors": []}),
        "router": AsyncMock(return_value={"route": "finance_approval", "approver": "CFO"}),
        "planner": AsyncMock(return_value={"plan": ["analyze_transaction", "check_merchant", "assess_risk"]}),
        "specialist_1": AsyncMock(return_value={"analysis": "Transaction pattern normal"}),
        "specialist_2": AsyncMock(return_value={"analysis": "Merchant verified"}),
        "specialist_3": AsyncMock(return_value={"analysis": "Risk score low"}),
    }


@pytest.fixture
def workflow_state_factory() -> Callable[[str], dict[str, Any]]:
    """Factory for creating workflow state dictionaries.

    Returns:
        Factory function that creates workflow state
    """

    def _create_state(workflow_type: str) -> dict[str, Any]:
        """Create workflow state for given type.

        Args:
            workflow_type: Type of workflow (invoice, fraud, reconciliation)

        Returns:
            Initial workflow state dictionary

        Raises:
            ValueError: If workflow_type is invalid
        """
        if workflow_type not in ["invoice", "fraud", "reconciliation"]:
            raise ValueError(f"Invalid workflow_type: {workflow_type}")

        base_state = {
            "workflow_id": f"{workflow_type.upper()}-WF-001",
            "status": "initialized",
            "current_step": 0,
            "steps_completed": [],
            "errors": [],
            "start_time": 0.0,
            "end_time": None,
        }

        if workflow_type == "invoice":
            base_state["data"] = {"vendor": None, "amount": None, "invoice_number": None}
        elif workflow_type == "fraud":
            base_state["data"] = {"transaction_id": None, "fraud_score": None, "is_fraud": None}
        elif workflow_type == "reconciliation":
            base_state["data"] = {"matches": [], "discrepancies": []}

        return base_state

    return _create_state


# =============================================================================
# Test Fixtures - Performance and Cost Tracking
# =============================================================================


@pytest.fixture
def cost_tracker() -> dict[str, Any]:
    """Provide cost tracking dictionary for orchestrator tests.

    Returns:
        Dictionary for tracking LLM API costs
    """
    return {
        "total_calls": 0,
        "total_tokens": 0,
        "total_cost_usd": 0.0,
        "calls_by_agent": {},
        "calls_by_model": {},
    }


@pytest.fixture
def performance_monitor() -> dict[str, Any]:
    """Provide performance monitoring dictionary.

    Returns:
        Dictionary for tracking latency and throughput
    """
    return {
        "start_time": 0.0,
        "end_time": None,
        "total_duration": None,
        "step_durations": {},
        "parallel_speedup": None,
    }


# =============================================================================
# Infrastructure Tests - Verify Fixtures Work
# =============================================================================


def test_should_provide_successful_mock_agent_when_fixture_called(mock_successful_agent: AsyncMock) -> None:
    """Test that successful mock agent fixture provides working agent."""
    assert mock_successful_agent is not None
    assert isinstance(mock_successful_agent, AsyncMock)


def test_should_provide_failing_mock_agent_when_fixture_called(mock_failing_agent: AsyncMock) -> None:
    """Test that failing mock agent fixture provides agent that raises."""
    assert mock_failing_agent is not None
    assert isinstance(mock_failing_agent, AsyncMock)


def test_should_provide_invoice_task_when_fixture_called(sample_invoice_task: dict[str, Any]) -> None:
    """Test that invoice task fixture provides valid task structure."""
    assert sample_invoice_task["task_type"] == "invoice_extraction"
    assert "input_data" in sample_invoice_task
    assert "gold_label" in sample_invoice_task
    assert sample_invoice_task["difficulty"] in ["easy", "medium", "hard"]


def test_should_provide_fraud_task_when_fixture_called(sample_fraud_task: dict[str, Any]) -> None:
    """Test that fraud task fixture provides valid task structure."""
    assert sample_fraud_task["task_type"] == "fraud_detection"
    assert "transaction_id" in sample_fraud_task["input_data"]
    assert "gold_label" in sample_fraud_task


def test_should_provide_reconciliation_task_when_fixture_called(sample_reconciliation_task: dict[str, Any]) -> None:
    """Test that reconciliation task fixture provides valid task structure."""
    assert sample_reconciliation_task["task_type"] == "reconciliation"
    assert "bank_transactions" in sample_reconciliation_task["input_data"]
    assert "ledger_entries" in sample_reconciliation_task["input_data"]


def test_should_provide_circuit_breaker_when_fixture_called(mock_circuit_breaker) -> None:
    """Test that circuit breaker fixture provides configured instance."""
    from backend.reliability.circuit_breaker import CircuitBreaker

    assert mock_circuit_breaker is not None
    assert isinstance(mock_circuit_breaker, CircuitBreaker)
    assert mock_circuit_breaker.failure_threshold == 3
    assert mock_circuit_breaker.timeout == 2.0


def test_should_provide_audit_logger_when_fixture_called(mock_audit_logger) -> None:
    """Test that audit logger fixture provides working logger."""
    from backend.reliability.audit_log import AuditLogger

    assert mock_audit_logger is not None
    assert isinstance(mock_audit_logger, AuditLogger)
    assert mock_audit_logger.workflow_id == "TEST-WF-001"


def test_should_create_workflow_state_when_factory_called(workflow_state_factory: Callable) -> None:
    """Test that workflow state factory creates valid states."""
    invoice_state = workflow_state_factory("invoice")
    assert invoice_state["workflow_id"].startswith("INVOICE-WF")
    assert invoice_state["status"] == "initialized"
    assert "data" in invoice_state

    fraud_state = workflow_state_factory("fraud")
    assert fraud_state["workflow_id"].startswith("FRAUD-WF")

    reconciliation_state = workflow_state_factory("reconciliation")
    assert reconciliation_state["workflow_id"].startswith("RECONCILIATION-WF")


def test_should_raise_when_invalid_workflow_type(workflow_state_factory: Callable) -> None:
    """Test that workflow factory validates workflow type."""
    with pytest.raises(ValueError, match="Invalid workflow_type"):
        workflow_state_factory("invalid_type")


# =============================================================================
# Task 3.2: Abstract Base Class Tests (7 Tests)
# =============================================================================


def test_should_raise_when_orchestrator_abc_instantiated_directly() -> None:
    """Test that Orchestrator ABC cannot be instantiated without implementing abstract methods."""
    from backend.orchestrators.base import Orchestrator

    # Attempt to instantiate abstract class should raise TypeError
    with pytest.raises(TypeError, match="Can't instantiate abstract class"):
        Orchestrator(name="test_orchestrator")


async def test_should_register_agent_when_register_agent_called() -> None:
    """Test that orchestrator can register named agents."""
    from backend.orchestrators.base import Orchestrator

    # Create a minimal concrete implementation for testing
    class TestOrchestrator(Orchestrator):
        async def _execute(self, task: dict[str, Any]) -> dict[str, Any]:
            return {"status": "success"}

    orchestrator = TestOrchestrator(name="test")
    mock_agent = AsyncMock(return_value={"result": "test"})

    # Register agent
    orchestrator.register_agent("test_agent", mock_agent)

    # Verify agent is registered
    assert "test_agent" in orchestrator.agents
    assert orchestrator.agents["test_agent"] is mock_agent


async def test_should_aggregate_results_when_aggregate_results_called() -> None:
    """Test that orchestrator aggregates multiple agent results."""
    from backend.orchestrators.base import Orchestrator

    class TestOrchestrator(Orchestrator):
        async def _execute(self, task: dict[str, Any]) -> dict[str, Any]:
            return {"status": "success"}

    orchestrator = TestOrchestrator(name="test")

    # Create sample results
    results = [
        {"agent": "agent1", "output": "result1", "status": "success"},
        {"agent": "agent2", "output": "result2", "status": "success"},
        {"agent": "agent3", "output": "result3", "status": "success"},
    ]

    # Aggregate results
    aggregated = orchestrator.aggregate_results(results)

    # Verify aggregation
    assert "results" in aggregated
    assert len(aggregated["results"]) == 3
    assert aggregated["total_agents"] == 3
    assert aggregated["successful_agents"] == 3


async def test_should_log_execution_when_log_step_called() -> None:
    """Test that orchestrator logs execution steps."""
    from backend.orchestrators.base import Orchestrator

    class TestOrchestrator(Orchestrator):
        async def _execute(self, task: dict[str, Any]) -> dict[str, Any]:
            return {"status": "success"}

    orchestrator = TestOrchestrator(name="test")

    # Log execution step
    orchestrator.log_step(step="step_1", status="success", output={"data": "test"})

    # Verify log entry
    assert len(orchestrator.execution_log) == 1
    assert orchestrator.execution_log[0]["step"] == "step_1"
    assert orchestrator.execution_log[0]["status"] == "success"
    assert "timestamp" in orchestrator.execution_log[0]


async def test_should_integrate_retry_when_retry_configured(mock_intermittent_agent: Callable) -> None:
    """Test that orchestrator integrates retry logic from reliability framework."""
    from backend.orchestrators.base import Orchestrator

    class TestOrchestrator(Orchestrator):
        async def _execute(self, task: dict[str, Any]) -> dict[str, Any]:
            # Use retry wrapper
            agent = self.agents["test_agent"]
            result = await self.with_retry(agent, task)
            return result

    orchestrator = TestOrchestrator(name="test")

    # Register agent that fails 2 times then succeeds
    failing_agent = mock_intermittent_agent(2)
    orchestrator.register_agent("test_agent", failing_agent)

    # Execute with retry
    task = {"task_id": "test"}
    result = await orchestrator.execute(task)

    # Verify retry succeeded
    assert result["status"] == "success"
    assert result["result"] == "Recovered after retries"
    assert failing_agent.call_count == 3  # 2 failures + 1 success


async def test_should_integrate_circuit_breaker_when_breaker_configured(mock_failing_agent: AsyncMock) -> None:
    """Test that orchestrator integrates circuit breaker from reliability framework."""
    from backend.orchestrators.base import Orchestrator
    from backend.reliability.circuit_breaker import CircuitBreakerOpenError

    class TestOrchestrator(Orchestrator):
        async def _execute(self, task: dict[str, Any]) -> dict[str, Any]:
            agent = self.agents["test_agent"]
            result = await self.with_circuit_breaker(agent, task)
            return result

    orchestrator = TestOrchestrator(name="test")
    orchestrator.register_agent("test_agent", mock_failing_agent)

    # Execute multiple times to trigger circuit breaker
    task = {"task_id": "test"}

    # First few failures should attempt call
    for _ in range(3):
        with pytest.raises(RuntimeError, match="Agent execution failed"):
            await orchestrator.execute(task)

    # Circuit breaker should now be OPEN - subsequent calls fail fast
    with pytest.raises(CircuitBreakerOpenError, match="Circuit breaker is OPEN"):
        await orchestrator.execute(task)


async def test_should_validate_task_input_when_execute_called() -> None:
    """Test that orchestrator validates task input before execution."""
    from backend.orchestrators.base import Orchestrator

    class TestOrchestrator(Orchestrator):
        async def _execute(self, task: dict[str, Any]) -> dict[str, Any]:
            # Base class should validate before this runs
            return {"status": "success"}

    orchestrator = TestOrchestrator(name="test")

    # Invalid task input - not a dict
    with pytest.raises(TypeError, match="task must be a dictionary"):
        await orchestrator.execute("not a dict")  # type: ignore

    # Invalid task input - missing task_id
    with pytest.raises(ValueError, match="task must contain 'task_id'"):
        await orchestrator.execute({})


# =============================================================================
# Task 3.3: Sequential Orchestration Tests (8 Tests - FR3.1)
# =============================================================================


async def test_should_execute_agents_in_order_when_sequential_orchestrator_runs(
    mock_agent_registry: dict[str, AsyncMock],
    sample_invoice_task: dict[str, Any],
) -> None:
    """Test that sequential orchestrator executes agents in registered order."""
    from backend.orchestrators.sequential import SequentialOrchestrator

    orchestrator = SequentialOrchestrator(name="invoice_workflow")

    # Register agents in specific order: extract → validate → route
    orchestrator.register_agent("extractor", mock_agent_registry["extractor"])
    orchestrator.register_agent("validator", mock_agent_registry["validator"])
    orchestrator.register_agent("router", mock_agent_registry["router"])

    # Execute workflow
    result = await orchestrator.execute(sample_invoice_task)

    # Verify all agents called exactly once in order
    assert mock_agent_registry["extractor"].call_count == 1
    assert mock_agent_registry["validator"].call_count == 1
    assert mock_agent_registry["router"].call_count == 1

    # Verify result contains all step outputs
    assert result["status"] == "success"
    assert "steps" in result
    assert len(result["steps"]) == 3


async def test_should_save_checkpoint_after_each_step_when_checkpoint_dir_provided(
    mock_agent_registry: dict[str, AsyncMock],
    sample_invoice_task: dict[str, Any],
    temp_checkpoint_dir: Path,
) -> None:
    """Test that sequential orchestrator saves checkpoint after each step."""
    from backend.orchestrators.sequential import SequentialOrchestrator

    orchestrator = SequentialOrchestrator(name="invoice_workflow", checkpoint_dir=temp_checkpoint_dir)

    # Register 3 agents
    orchestrator.register_agent("extractor", mock_agent_registry["extractor"])
    orchestrator.register_agent("validator", mock_agent_registry["validator"])
    orchestrator.register_agent("router", mock_agent_registry["router"])

    # Execute workflow
    result = await orchestrator.execute(sample_invoice_task)

    # Verify checkpoints saved (3 agents = 3 checkpoints)
    checkpoint_files = list(temp_checkpoint_dir.glob("*.json"))
    assert len(checkpoint_files) >= 3  # At least one checkpoint per step

    # Verify result successful
    assert result["status"] == "success"


async def test_should_terminate_early_when_validation_fails(
    mock_agent_registry: dict[str, AsyncMock],
    sample_invoice_task: dict[str, Any],
) -> None:
    """Test that sequential orchestrator terminates early on validation failure."""
    from backend.orchestrators.sequential import SequentialOrchestrator

    orchestrator = SequentialOrchestrator(name="invoice_workflow", validate_steps=True)

    # Configure validator to fail
    mock_agent_registry["validator"].return_value = {
        "is_valid": False,
        "validation_errors": ["Amount exceeds threshold"],
    }

    # Register agents
    orchestrator.register_agent("extractor", mock_agent_registry["extractor"])
    orchestrator.register_agent("validator", mock_agent_registry["validator"])
    orchestrator.register_agent("router", mock_agent_registry["router"])  # Should NOT be called

    # Execute workflow
    result = await orchestrator.execute(sample_invoice_task)

    # Verify extractor and validator called, but NOT router (early termination)
    assert mock_agent_registry["extractor"].call_count == 1
    assert mock_agent_registry["validator"].call_count == 1
    assert mock_agent_registry["router"].call_count == 0  # Early termination

    # Verify result indicates failure and includes error
    assert result["status"] == "validation_failed"
    assert "error" in result
    assert "validation_errors" in result


async def test_should_pass_output_to_next_step_when_executing_chain(
    mock_agent_registry: dict[str, AsyncMock],
    sample_invoice_task: dict[str, Any],
) -> None:
    """Test that sequential orchestrator passes each step's output to the next step."""
    from backend.orchestrators.sequential import SequentialOrchestrator

    orchestrator = SequentialOrchestrator(name="invoice_workflow")

    # Register agents
    orchestrator.register_agent("extractor", mock_agent_registry["extractor"])
    orchestrator.register_agent("validator", mock_agent_registry["validator"])

    # Execute workflow
    await orchestrator.execute(sample_invoice_task)

    # Verify validator received extractor's output
    validator_call_args = mock_agent_registry["validator"].call_args
    assert validator_call_args is not None

    # Validator should receive task with extractor's output in context
    passed_task = validator_call_args[0][0]
    assert "previous_output" in passed_task or "extracted_data" in passed_task


async def test_should_restore_from_checkpoint_when_workflow_resumes(
    mock_agent_registry: dict[str, AsyncMock],
    sample_invoice_task: dict[str, Any],
    temp_checkpoint_dir: Path,
) -> None:
    """Test that sequential orchestrator can resume from checkpoint after failure."""
    from backend.orchestrators.sequential import SequentialOrchestrator

    # First execution: fail at step 2
    orchestrator1 = SequentialOrchestrator(name="invoice_workflow", checkpoint_dir=temp_checkpoint_dir)

    orchestrator1.register_agent("extractor", mock_agent_registry["extractor"])

    # Validator fails on first attempt
    failing_validator = AsyncMock(side_effect=RuntimeError("Temporary failure"))
    orchestrator1.register_agent("validator", failing_validator)

    # Execute and expect failure
    with pytest.raises(RuntimeError, match="Temporary failure"):
        await orchestrator1.execute(sample_invoice_task)

    # Second execution: resume from checkpoint
    orchestrator2 = SequentialOrchestrator(name="invoice_workflow", checkpoint_dir=temp_checkpoint_dir)

    # Use same agents, but validator now succeeds
    orchestrator2.register_agent("extractor", mock_agent_registry["extractor"])
    orchestrator2.register_agent("validator", mock_agent_registry["validator"])
    orchestrator2.register_agent("router", mock_agent_registry["router"])

    # Resume execution
    result = await orchestrator2.execute(sample_invoice_task)

    # Verify workflow completed successfully
    assert result["status"] == "success"


async def test_should_track_execution_log_when_steps_complete(
    mock_agent_registry: dict[str, AsyncMock],
    sample_invoice_task: dict[str, Any],
) -> None:
    """Test that sequential orchestrator logs each step execution."""
    from backend.orchestrators.sequential import SequentialOrchestrator

    orchestrator = SequentialOrchestrator(name="invoice_workflow")

    # Register agents
    orchestrator.register_agent("extractor", mock_agent_registry["extractor"])
    orchestrator.register_agent("validator", mock_agent_registry["validator"])
    orchestrator.register_agent("router", mock_agent_registry["router"])

    # Execute workflow
    await orchestrator.execute(sample_invoice_task)

    # Verify execution log contains entries for all 3 steps
    assert len(orchestrator.execution_log) >= 3

    # Verify log entries have expected structure
    for log_entry in orchestrator.execution_log:
        assert "step" in log_entry
        assert "status" in log_entry
        assert "timestamp" in log_entry


async def test_should_handle_invoice_processing_use_case_when_all_steps_succeed(
    mock_invoice_extraction_agent: AsyncMock,
    sample_invoice_task: dict[str, Any],
) -> None:
    """Test sequential orchestrator with complete invoice processing workflow."""
    from backend.orchestrators.sequential import SequentialOrchestrator

    orchestrator = SequentialOrchestrator(name="invoice_processing")

    # Create validation agent that checks extracted data
    validator = AsyncMock(return_value={"is_valid": True, "validation_errors": []})

    # Create routing agent that determines approval path
    router = AsyncMock(return_value={"route": "finance_approval", "approver": "CFO", "reason": "amount > $1000"})

    # Register agents for invoice workflow
    orchestrator.register_agent("extract_invoice", mock_invoice_extraction_agent)
    orchestrator.register_agent("validate_extraction", validator)
    orchestrator.register_agent("route_for_approval", router)

    # Execute complete workflow
    result = await orchestrator.execute(sample_invoice_task)

    # Verify all agents called
    assert mock_invoice_extraction_agent.call_count == 1
    assert validator.call_count == 1
    assert router.call_count == 1

    # Verify workflow completed successfully
    assert result["status"] == "success"
    assert "steps" in result
    assert len(result["steps"]) == 3

    # Verify final output contains routing decision
    assert "route" in result["final_output"]


async def test_should_raise_when_no_agents_registered(
    sample_invoice_task: dict[str, Any],
) -> None:
    """Test that sequential orchestrator raises error when no agents registered."""
    from backend.orchestrators.sequential import SequentialOrchestrator

    orchestrator = SequentialOrchestrator(name="empty_workflow")

    # Attempt to execute without registered agents
    with pytest.raises(ValueError, match="No agents registered"):
        await orchestrator.execute(sample_invoice_task)


# =============================================================================
# Task 3.4: Hierarchical Delegation Pattern Tests (9 Tests - FR3.2)
# =============================================================================


async def test_should_create_task_list_when_planner_validates_output(
    mock_agent_registry: dict[str, AsyncMock],
    sample_fraud_task: dict[str, Any],
) -> None:
    """Test that planner creates validated task list for specialists."""
    from backend.orchestrators.hierarchical import HierarchicalOrchestrator

    orchestrator = HierarchicalOrchestrator(name="fraud_detection")

    # Configure planner to return validated task list
    mock_agent_registry["planner"].return_value = {
        "status": "success",
        "tasks": [
            {"specialist": "transaction_analysis", "input": sample_fraud_task["input_data"]},
            {"specialist": "merchant_verification", "input": sample_fraud_task["input_data"]},
            {"specialist": "user_behavior_check", "input": sample_fraud_task["input_data"]},
        ],
    }

    # Register planner
    orchestrator.register_agent("planner", mock_agent_registry["planner"])

    # Register specialists
    orchestrator.register_agent("transaction_analysis", mock_agent_registry["specialist_1"])
    orchestrator.register_agent("merchant_verification", mock_agent_registry["specialist_2"])
    orchestrator.register_agent("user_behavior_check", mock_agent_registry["specialist_3"])

    # Execute workflow
    result = await orchestrator.execute(sample_fraud_task)

    # Verify planner called to create task list
    assert mock_agent_registry["planner"].call_count == 1

    # Verify result contains validated task assignments
    assert result["status"] == "success"
    assert "specialist_results" in result
    assert len(result["specialist_results"]) == 3


async def test_should_execute_specialists_in_parallel_when_tasks_assigned(
    mock_agent_registry: dict[str, AsyncMock],
    sample_fraud_task: dict[str, Any],
) -> None:
    """Test that specialists execute in parallel using ThreadPoolExecutor pattern."""
    from backend.orchestrators.hierarchical import HierarchicalOrchestrator

    orchestrator = HierarchicalOrchestrator(name="fraud_detection")

    # Configure planner
    mock_agent_registry["planner"].return_value = {
        "status": "success",
        "tasks": [
            {"specialist": "transaction_analysis", "input": sample_fraud_task["input_data"]},
            {"specialist": "merchant_verification", "input": sample_fraud_task["input_data"]},
            {"specialist": "user_behavior_check", "input": sample_fraud_task["input_data"]},
        ],
    }

    # Register planner and specialists
    orchestrator.register_agent("planner", mock_agent_registry["planner"])
    orchestrator.register_agent("transaction_analysis", mock_agent_registry["specialist_1"])
    orchestrator.register_agent("merchant_verification", mock_agent_registry["specialist_2"])
    orchestrator.register_agent("user_behavior_check", mock_agent_registry["specialist_3"])

    # Execute workflow
    result = await orchestrator.execute(sample_fraud_task)

    # Verify all 3 specialists called
    assert mock_agent_registry["specialist_1"].call_count == 1
    assert mock_agent_registry["specialist_2"].call_count == 1
    assert mock_agent_registry["specialist_3"].call_count == 1

    # Verify parallel execution (all specialists in result)
    assert len(result["specialist_results"]) == 3


async def test_should_reduce_latency_when_parallel_vs_sequential(
    mock_slow_agent: AsyncMock,
    sample_fraud_task: dict[str, Any],
) -> None:
    """Test that parallel execution achieves 30% latency reduction vs sequential."""
    from backend.orchestrators.hierarchical import HierarchicalOrchestrator

    orchestrator = HierarchicalOrchestrator(name="fraud_detection")

    # Configure planner
    planner = AsyncMock(
        return_value={
            "status": "success",
            "tasks": [
                {"specialist": "specialist_1", "input": sample_fraud_task["input_data"]},
                {"specialist": "specialist_2", "input": sample_fraud_task["input_data"]},
                {"specialist": "specialist_3", "input": sample_fraud_task["input_data"]},
            ],
        }
    )

    # Register planner and slow specialists (0.5s each)
    orchestrator.register_agent("planner", planner)
    orchestrator.register_agent("specialist_1", mock_slow_agent)
    orchestrator.register_agent("specialist_2", mock_slow_agent)
    orchestrator.register_agent("specialist_3", mock_slow_agent)

    # Execute workflow and measure time
    import time

    start_time = time.time()
    result = await orchestrator.execute(sample_fraud_task)
    parallel_duration = time.time() - start_time

    # Sequential would take ~1.5s (3 × 0.5s), parallel should take ~0.5s
    # Verify parallel execution completes faster than sequential
    # With overhead, parallel should be < 1.0s (allowing 0.5s for overhead)
    assert parallel_duration < 1.0, f"Parallel execution took {parallel_duration:.2f}s, expected < 1.0s"

    # Verify successful execution
    assert result["status"] == "success"
    assert len(result["specialist_results"]) == 3


async def test_should_isolate_error_when_specialist_fails(
    mock_agent_registry: dict[str, AsyncMock],
    sample_fraud_task: dict[str, Any],
) -> None:
    """Test that specialist failure doesn't crash orchestrator (error isolation)."""
    from backend.orchestrators.hierarchical import HierarchicalOrchestrator

    orchestrator = HierarchicalOrchestrator(name="fraud_detection")

    # Configure planner
    mock_agent_registry["planner"].return_value = {
        "status": "success",
        "tasks": [
            {"specialist": "transaction_analysis", "input": sample_fraud_task["input_data"]},
            {"specialist": "merchant_verification", "input": sample_fraud_task["input_data"]},
            {"specialist": "user_behavior_check", "input": sample_fraud_task["input_data"]},
        ],
    }

    # Register planner
    orchestrator.register_agent("planner", mock_agent_registry["planner"])

    # Register specialists - specialist_2 fails
    orchestrator.register_agent("transaction_analysis", mock_agent_registry["specialist_1"])

    failing_specialist = AsyncMock(side_effect=RuntimeError("Merchant API unavailable"))
    orchestrator.register_agent("merchant_verification", failing_specialist)

    orchestrator.register_agent("user_behavior_check", mock_agent_registry["specialist_3"])

    # Execute workflow
    result = await orchestrator.execute(sample_fraud_task)

    # Verify orchestrator didn't crash - partial success
    assert result["status"] == "partial_success"

    # Verify successful specialists completed
    assert mock_agent_registry["specialist_1"].call_count == 1
    assert mock_agent_registry["specialist_3"].call_count == 1

    # Verify failure recorded but isolated
    assert "errors" in result
    assert len(result["errors"]) == 1
    assert "Merchant API unavailable" in result["errors"][0]

    # Verify successful results still present
    successful_results = [r for r in result["specialist_results"] if r.get("status") == "success"]
    assert len(successful_results) == 2


async def test_should_validate_planner_output_when_planner_executes(
    sample_fraud_task: dict[str, Any],
) -> None:
    """Test that orchestrator validates planner output schema with Pydantic."""
    from backend.orchestrators.hierarchical import HierarchicalOrchestrator

    orchestrator = HierarchicalOrchestrator(name="fraud_detection")

    # Configure planner with INVALID output (missing required fields)
    invalid_planner = AsyncMock(
        return_value={
            "status": "success",
            # Missing "tasks" field - invalid schema
        }
    )

    orchestrator.register_agent("planner", invalid_planner)

    # Execute workflow - should detect invalid planner output
    with pytest.raises(ValueError, match="Planner output validation failed|missing 'tasks'"):
        await orchestrator.execute(sample_fraud_task)


async def test_should_aggregate_specialist_results_when_all_complete(
    mock_agent_registry: dict[str, AsyncMock],
    sample_fraud_task: dict[str, Any],
) -> None:
    """Test that orchestrator aggregates specialist outputs into final decision."""
    from backend.orchestrators.hierarchical import HierarchicalOrchestrator

    orchestrator = HierarchicalOrchestrator(name="fraud_detection")

    # Configure planner
    mock_agent_registry["planner"].return_value = {
        "status": "success",
        "tasks": [
            {"specialist": "transaction_analysis", "input": sample_fraud_task["input_data"]},
            {"specialist": "merchant_verification", "input": sample_fraud_task["input_data"]},
            {"specialist": "user_behavior_check", "input": sample_fraud_task["input_data"]},
        ],
    }

    # Configure specialists with fraud signals
    mock_agent_registry["specialist_1"].return_value = {
        "status": "success",
        "fraud_score": 0.7,
        "analysis": "High transaction velocity detected",
    }
    mock_agent_registry["specialist_2"].return_value = {
        "status": "success",
        "fraud_score": 0.3,
        "analysis": "Merchant verified",
    }
    mock_agent_registry["specialist_3"].return_value = {
        "status": "success",
        "fraud_score": 0.5,
        "analysis": "User behavior normal",
    }

    # Register planner and specialists
    orchestrator.register_agent("planner", mock_agent_registry["planner"])
    orchestrator.register_agent("transaction_analysis", mock_agent_registry["specialist_1"])
    orchestrator.register_agent("merchant_verification", mock_agent_registry["specialist_2"])
    orchestrator.register_agent("user_behavior_check", mock_agent_registry["specialist_3"])

    # Execute workflow
    result = await orchestrator.execute(sample_fraud_task)

    # Verify aggregation contains all specialist results
    assert result["status"] == "success"
    assert len(result["specialist_results"]) == 3

    # Verify final aggregation computed (e.g., average fraud score)
    assert "final_decision" in result
    assert "aggregated_fraud_score" in result["final_decision"]

    # Average fraud score should be (0.7 + 0.3 + 0.5) / 3 = 0.5
    assert abs(result["final_decision"]["aggregated_fraud_score"] - 0.5) < 0.01


async def test_should_handle_fraud_detection_use_case_when_complete_workflow(
    mock_fraud_detection_agent: AsyncMock,
    sample_fraud_task: dict[str, Any],
) -> None:
    """Test hierarchical orchestrator with complete fraud detection workflow."""
    from backend.orchestrators.hierarchical import HierarchicalOrchestrator

    orchestrator = HierarchicalOrchestrator(name="fraud_detection")

    # Create planner that analyzes transaction and creates specialist tasks
    planner = AsyncMock(
        return_value={
            "status": "success",
            "tasks": [
                {"specialist": "transaction_pattern_analysis", "input": sample_fraud_task["input_data"]},
                {"specialist": "merchant_risk_assessment", "input": sample_fraud_task["input_data"]},
                {"specialist": "user_behavior_profiling", "input": sample_fraud_task["input_data"]},
            ],
        }
    )

    # Create specialist agents for fraud detection
    transaction_specialist = AsyncMock(
        return_value={
            "status": "success",
            "fraud_score": 0.15,
            "risk_factors": ["high_velocity"],
            "confidence": 0.88,
        }
    )

    merchant_specialist = AsyncMock(
        return_value={
            "status": "success",
            "fraud_score": 0.25,
            "risk_factors": ["new_merchant"],
            "confidence": 0.92,
        }
    )

    user_specialist = AsyncMock(
        return_value={"status": "success", "fraud_score": 0.10, "risk_factors": [], "confidence": 0.95}
    )

    # Register planner and specialists
    orchestrator.register_agent("planner", planner)
    orchestrator.register_agent("transaction_pattern_analysis", transaction_specialist)
    orchestrator.register_agent("merchant_risk_assessment", merchant_specialist)
    orchestrator.register_agent("user_behavior_profiling", user_specialist)

    # Execute complete workflow
    result = await orchestrator.execute(sample_fraud_task)

    # Verify all agents called
    assert planner.call_count == 1
    assert transaction_specialist.call_count == 1
    assert merchant_specialist.call_count == 1
    assert user_specialist.call_count == 1

    # Verify workflow completed successfully
    assert result["status"] == "success"
    assert len(result["specialist_results"]) == 3

    # Verify final fraud decision made
    assert "final_decision" in result
    assert "is_fraud" in result["final_decision"]
    assert "aggregated_fraud_score" in result["final_decision"]


async def test_should_preserve_result_order_when_parallel_execution_completes(
    mock_agent_registry: dict[str, AsyncMock],
    sample_fraud_task: dict[str, Any],
) -> None:
    """Test that specialist results preserve task order despite parallel execution."""
    from backend.orchestrators.hierarchical import HierarchicalOrchestrator

    orchestrator = HierarchicalOrchestrator(name="fraud_detection")

    # Configure planner with specific task order
    mock_agent_registry["planner"].return_value = {
        "status": "success",
        "tasks": [
            {"specialist": "specialist_1", "input": sample_fraud_task["input_data"]},
            {"specialist": "specialist_2", "input": sample_fraud_task["input_data"]},
            {"specialist": "specialist_3", "input": sample_fraud_task["input_data"]},
        ],
    }

    # Register planner and specialists
    orchestrator.register_agent("planner", mock_agent_registry["planner"])
    orchestrator.register_agent("specialist_1", mock_agent_registry["specialist_1"])
    orchestrator.register_agent("specialist_2", mock_agent_registry["specialist_2"])
    orchestrator.register_agent("specialist_3", mock_agent_registry["specialist_3"])

    # Execute workflow
    result = await orchestrator.execute(sample_fraud_task)

    # Verify result order matches task order (specialist_1, specialist_2, specialist_3)
    assert result["specialist_results"][0]["specialist"] == "specialist_1"
    assert result["specialist_results"][1]["specialist"] == "specialist_2"
    assert result["specialist_results"][2]["specialist"] == "specialist_3"


async def test_should_raise_when_no_planner_registered(
    sample_fraud_task: dict[str, Any],
) -> None:
    """Test that hierarchical orchestrator requires planner agent."""
    from backend.orchestrators.hierarchical import HierarchicalOrchestrator

    orchestrator = HierarchicalOrchestrator(name="fraud_detection")

    # Register specialists but NO planner
    specialist = AsyncMock(return_value={"status": "success"})
    orchestrator.register_agent("specialist_1", specialist)

    # Attempt to execute without planner
    with pytest.raises(ValueError, match="Planner agent 'planner' not registered"):
        await orchestrator.execute(sample_fraud_task)


# =============================================================================
# Task 3.5: Iterative Refinement (ReAct/Reflexion) Tests (9 Tests - FR3.3)
# =============================================================================


async def test_should_execute_action_reflection_refinement_loop_when_iterative_orchestrator_runs(
    mock_reconciliation_agent: AsyncMock,
    sample_reconciliation_task: dict[str, Any],
) -> None:
    """Test that iterative orchestrator performs action-reflection-refinement loop."""
    from backend.orchestrators.iterative import IterativeOrchestrator

    orchestrator = IterativeOrchestrator(name="reconciliation_workflow", max_iterations=3)

    # Configure agent to improve discrepancy each iteration
    call_count = 0

    async def iterative_agent(task: dict[str, Any]) -> dict[str, Any]:
        nonlocal call_count
        call_count += 1
        # Improve discrepancy each iteration: 10.0 → 5.0 → 0.5 → converged
        discrepancies = [10.0, 5.0, 0.5]
        discrepancy = discrepancies[min(call_count - 1, len(discrepancies) - 1)]

        return {
            "status": "success",
            "discrepancy_amount": discrepancy,
            "match_confidence": 0.95 if discrepancy < 1.0 else 0.70,
            "iteration": call_count,
            "reflection": f"Reduced discrepancy to ${discrepancy}",
        }

    orchestrator.register_agent("reconciliation_agent", iterative_agent)

    # Execute workflow
    result = await orchestrator.execute(sample_reconciliation_task)

    # Verify action-reflection-refinement loop executed
    assert result["status"] == "success"
    assert "iterations" in result
    assert len(result["iterations"]) == 3  # 3 iterations to converge

    # Verify convergence achieved
    assert result["converged"] is True
    assert result["final_discrepancy"] < 1.0


async def test_should_enforce_max_iteration_limit_when_not_converged(
    sample_reconciliation_task: dict[str, Any],
) -> None:
    """Test that iterative orchestrator enforces max iteration limit."""
    from backend.orchestrators.iterative import IterativeOrchestrator

    orchestrator = IterativeOrchestrator(name="reconciliation_workflow", max_iterations=5)

    # Create agent that never converges (always high discrepancy)
    non_converging_agent = AsyncMock(
        return_value={
            "status": "success",
            "discrepancy_amount": 100.0,  # Never converges
            "match_confidence": 0.30,
            "reflection": "Still high discrepancy",
        }
    )

    orchestrator.register_agent("reconciliation_agent", non_converging_agent)

    # Execute workflow
    result = await orchestrator.execute(sample_reconciliation_task)

    # Verify max iterations enforced
    assert len(result["iterations"]) == 5  # Stopped at max_iterations
    assert result["converged"] is False  # Did not converge
    assert non_converging_agent.call_count == 5


async def test_should_detect_convergence_when_discrepancy_below_threshold(
    sample_reconciliation_task: dict[str, Any],
) -> None:
    """Test that iterative orchestrator detects convergence when criteria met."""
    from backend.orchestrators.iterative import IterativeOrchestrator

    orchestrator = IterativeOrchestrator(
        name="reconciliation_workflow",
        max_iterations=5,
        convergence_threshold=0.01,  # Converge when discrepancy < $0.01
    )

    # Create agent that converges in 2 iterations
    call_count = 0

    async def converging_agent(task: dict[str, Any]) -> dict[str, Any]:
        nonlocal call_count
        call_count += 1
        # Iteration 1: 5.0, Iteration 2: 0.005 (converged)
        discrepancies = [5.0, 0.005]
        discrepancy = discrepancies[min(call_count - 1, len(discrepancies) - 1)]

        return {
            "status": "success",
            "discrepancy_amount": discrepancy,
            "match_confidence": 0.99 if discrepancy < 0.01 else 0.75,
            "reflection": "Converged" if discrepancy < 0.01 else "Refining",
        }

    orchestrator.register_agent("reconciliation_agent", converging_agent)

    # Execute workflow
    result = await orchestrator.execute(sample_reconciliation_task)

    # Verify early convergence (stopped at iteration 2, not 5)
    assert result["converged"] is True
    assert len(result["iterations"]) == 2  # Stopped early due to convergence
    assert result["final_discrepancy"] < 0.01


async def test_should_validate_progress_when_checking_refinement(
    sample_reconciliation_task: dict[str, Any],
) -> None:
    """Test that iterative orchestrator validates progress between iterations."""
    from backend.orchestrators.iterative import IterativeOrchestrator

    orchestrator = IterativeOrchestrator(name="reconciliation_workflow", max_iterations=4)

    # Create agent that shows progressive improvement
    iteration_discrepancies = [20.0, 15.0, 8.0, 2.0]  # Decreasing each iteration
    call_count = 0

    async def progressive_agent(task: dict[str, Any]) -> dict[str, Any]:
        nonlocal call_count
        discrepancy = iteration_discrepancies[call_count]
        call_count += 1

        return {
            "status": "success",
            "discrepancy_amount": discrepancy,
            "match_confidence": 0.95 if discrepancy < 5.0 else 0.70,
            "reflection": f"Iteration {call_count}: ${discrepancy}",
        }

    orchestrator.register_agent("reconciliation_agent", progressive_agent)

    # Execute workflow
    result = await orchestrator.execute(sample_reconciliation_task)

    # Verify progress tracking
    assert "iterations" in result
    assert len(result["iterations"]) == 4

    # Verify each iteration shows improvement
    for i in range(1, len(result["iterations"])):
        prev_discrepancy = result["iterations"][i - 1]["discrepancy_amount"]
        curr_discrepancy = result["iterations"][i]["discrepancy_amount"]
        assert curr_discrepancy < prev_discrepancy, f"No progress at iteration {i}"


async def test_should_pass_reflection_to_next_iteration_when_refining(
    sample_reconciliation_task: dict[str, Any],
) -> None:
    """Test that iterative orchestrator passes reflection context to next iteration."""
    from backend.orchestrators.iterative import IterativeOrchestrator

    orchestrator = IterativeOrchestrator(name="reconciliation_workflow", max_iterations=3)

    # Track task passed to agent at each iteration
    task_history = []

    async def reflection_agent(task: dict[str, Any]) -> dict[str, Any]:
        task_history.append(task)

        iteration_num = len(task_history)
        return {
            "status": "success",
            "discrepancy_amount": 10.0 / iteration_num,  # Improve each iteration
            "reflection": f"Iteration {iteration_num} reflection: Try adjusting date",
        }

    orchestrator.register_agent("reconciliation_agent", reflection_agent)

    # Execute workflow
    await orchestrator.execute(sample_reconciliation_task)

    # Verify reflection passed to subsequent iterations
    assert len(task_history) >= 2

    # Second iteration should have reflection from first
    second_iteration_task = task_history[1]
    assert "previous_reflection" in second_iteration_task
    assert "Iteration 1 reflection" in second_iteration_task["previous_reflection"]


async def test_should_handle_account_reconciliation_use_case_when_complete_workflow(
    sample_reconciliation_task: dict[str, Any],
) -> None:
    """Test iterative orchestrator with complete account reconciliation workflow."""
    from backend.orchestrators.iterative import IterativeOrchestrator

    orchestrator = IterativeOrchestrator(
        name="account_reconciliation",
        max_iterations=3,
        convergence_threshold=0.01,
    )

    # Simulate realistic reconciliation: date mismatch resolved iteratively
    iteration_count = 0

    async def reconciliation_agent(task: dict[str, Any]) -> dict[str, Any]:
        nonlocal iteration_count
        iteration_count += 1

        # Iteration 1: Detect date mismatch (discrepancy $1234.56)
        # Iteration 2: Adjust for posting date offset (discrepancy $0.06 - rounding)
        # Iteration 3: Apply rounding adjustment (discrepancy $0.00 - converged)
        scenarios = [
            {
                "discrepancy_amount": 1234.56,
                "resolution_status": "date_mismatch_detected",
                "reflection": "Bank date 2024-11-20 vs Ledger date 2024-11-22 - posting date offset",
            },
            {
                "discrepancy_amount": 0.06,
                "resolution_status": "amount_rounding_issue",
                "reflection": "Bank $1234.50 vs Ledger $1234.56 - rounding difference",
            },
            {
                "discrepancy_amount": 0.00,
                "resolution_status": "perfect_match",
                "reflection": "Matched after date+amount adjustments",
            },
        ]

        scenario = scenarios[min(iteration_count - 1, len(scenarios) - 1)]

        return {
            "status": "success",
            "bank_transaction_id": "BANK-001",
            "ledger_entry_id": "LED-001",
            "discrepancy_amount": scenario["discrepancy_amount"],
            "resolution_status": scenario["resolution_status"],
            "match_confidence": 0.99 if scenario["discrepancy_amount"] < 0.01 else 0.80,
            "reflection": scenario["reflection"],
        }

    orchestrator.register_agent("reconciliation_agent", reconciliation_agent)

    # Execute complete workflow
    result = await orchestrator.execute(sample_reconciliation_task)

    # Verify workflow completed successfully
    assert result["status"] == "success"
    assert result["converged"] is True
    assert len(result["iterations"]) == 3  # 3 iterations to resolve

    # Verify final reconciliation match
    assert result["final_discrepancy"] < 0.01
    assert result["resolution_status"] == "perfect_match"


async def test_should_stop_when_convergence_achieved_early(
    sample_reconciliation_task: dict[str, Any],
) -> None:
    """Test that iterative orchestrator stops early when convergence achieved."""
    from backend.orchestrators.iterative import IterativeOrchestrator

    orchestrator = IterativeOrchestrator(
        name="reconciliation_workflow",
        max_iterations=10,  # High limit
        convergence_threshold=0.01,
    )

    # Agent converges in 2 iterations
    call_count = 0

    async def fast_converging_agent(task: dict[str, Any]) -> dict[str, Any]:
        nonlocal call_count
        call_count += 1

        # Iteration 1: 50.0, Iteration 2: 0.001 (converged)
        discrepancy = 50.0 if call_count == 1 else 0.001

        return {
            "status": "success",
            "discrepancy_amount": discrepancy,
            "reflection": "Converged" if discrepancy < 0.01 else "Refining",
        }

    orchestrator.register_agent("reconciliation_agent", fast_converging_agent)

    # Execute workflow
    result = await orchestrator.execute(sample_reconciliation_task)

    # Verify early stop (2 iterations, not 10)
    assert result["converged"] is True
    assert len(result["iterations"]) == 2
    assert call_count == 2  # Agent called only 2 times


async def test_should_track_iteration_history_when_refining(
    sample_reconciliation_task: dict[str, Any],
) -> None:
    """Test that iterative orchestrator tracks complete iteration history."""
    from backend.orchestrators.iterative import IterativeOrchestrator

    orchestrator = IterativeOrchestrator(name="reconciliation_workflow", max_iterations=4)

    iteration_num = 0

    async def tracking_agent(task: dict[str, Any]) -> dict[str, Any]:
        nonlocal iteration_num
        iteration_num += 1

        return {
            "status": "success",
            "iteration": iteration_num,
            "discrepancy_amount": 20.0 / iteration_num,
            "reflection": f"Iteration {iteration_num} complete",
            "action_taken": f"Adjustment {iteration_num}",
        }

    orchestrator.register_agent("reconciliation_agent", tracking_agent)

    # Execute workflow
    result = await orchestrator.execute(sample_reconciliation_task)

    # Verify iteration history tracked
    assert "iterations" in result
    assert len(result["iterations"]) == 4

    # Verify each iteration has required fields
    for i, iteration in enumerate(result["iterations"]):
        assert iteration["iteration"] == i + 1
        assert "discrepancy_amount" in iteration
        assert "reflection" in iteration
        assert "action_taken" in iteration


async def test_should_raise_when_no_agent_registered_for_iterative_orchestrator(
    sample_reconciliation_task: dict[str, Any],
) -> None:
    """Test that iterative orchestrator raises error when no agent registered."""
    from backend.orchestrators.iterative import IterativeOrchestrator

    orchestrator = IterativeOrchestrator(name="empty_workflow")

    # Attempt to execute without registered agent
    with pytest.raises(ValueError, match="No agents registered"):
        await orchestrator.execute(sample_reconciliation_task)


async def test_should_raise_when_max_iterations_invalid() -> None:
    """Test that iterative orchestrator validates max_iterations parameter."""
    from backend.orchestrators.iterative import IterativeOrchestrator

    # Test invalid type
    with pytest.raises(TypeError, match="max_iterations must be an integer"):
        IterativeOrchestrator(name="test", max_iterations="invalid")  # type: ignore

    # Test invalid value (< 1)
    with pytest.raises(ValueError, match="max_iterations must be at least 1"):
        IterativeOrchestrator(name="test", max_iterations=0)


async def test_should_raise_when_convergence_threshold_invalid() -> None:
    """Test that iterative orchestrator validates convergence_threshold parameter."""
    from backend.orchestrators.iterative import IterativeOrchestrator

    # Test invalid type
    with pytest.raises(TypeError, match="convergence_threshold must be a number"):
        IterativeOrchestrator(name="test", convergence_threshold="invalid")  # type: ignore

    # Test invalid value (< 0)
    with pytest.raises(ValueError, match="convergence_threshold must be non-negative"):
        IterativeOrchestrator(name="test", convergence_threshold=-1.0)


async def test_should_handle_agent_failure_during_iteration(
    sample_reconciliation_task: dict[str, Any],
) -> None:
    """Test that iterative orchestrator handles agent failures during iteration."""
    from backend.orchestrators.iterative import IterativeOrchestrator

    orchestrator = IterativeOrchestrator(name="reconciliation_workflow", max_iterations=3)

    # Create agent that fails on iteration 2
    call_count = 0

    async def failing_agent(task: dict[str, Any]) -> dict[str, Any]:
        nonlocal call_count
        call_count += 1

        if call_count == 2:
            raise RuntimeError("Agent failed on iteration 2")

        return {
            "status": "success",
            "discrepancy_amount": 10.0,
            "reflection": f"Iteration {call_count}",
        }

    orchestrator.register_agent("reconciliation_agent", failing_agent)

    # Execute workflow - should fail on iteration 2
    with pytest.raises(RuntimeError, match="Agent failed on iteration 2"):
        await orchestrator.execute(sample_reconciliation_task)

    # Verify execution log contains failure
    assert len(orchestrator.execution_log) == 2  # Iteration 1 success, iteration 2 failure
    assert orchestrator.execution_log[1]["status"] == "failure"


async def test_should_handle_missing_discrepancy_field_when_checking_convergence(
    sample_reconciliation_task: dict[str, Any],
) -> None:
    """Test that convergence check handles missing discrepancy_amount field."""
    from backend.orchestrators.iterative import IterativeOrchestrator

    orchestrator = IterativeOrchestrator(name="reconciliation_workflow", max_iterations=2)

    # Create agent that returns output WITHOUT discrepancy_amount field
    async def incomplete_agent(task: dict[str, Any]) -> dict[str, Any]:
        return {
            "status": "success",
            # Missing "discrepancy_amount" field
            "reflection": "Processing",
        }

    orchestrator.register_agent("reconciliation_agent", incomplete_agent)

    # Execute workflow - should run all iterations (no convergence without discrepancy field)
    result = await orchestrator.execute(sample_reconciliation_task)

    # Verify did not converge (missing field prevents convergence detection)
    assert result["converged"] is False
    assert len(result["iterations"]) == 2  # Ran all max_iterations


async def test_should_handle_invalid_discrepancy_type_when_checking_convergence(
    sample_reconciliation_task: dict[str, Any],
) -> None:
    """Test that convergence check handles invalid discrepancy_amount type."""
    from backend.orchestrators.iterative import IterativeOrchestrator

    orchestrator = IterativeOrchestrator(name="reconciliation_workflow", max_iterations=2)

    # Create agent that returns non-numeric discrepancy_amount
    async def invalid_type_agent(task: dict[str, Any]) -> dict[str, Any]:
        return {
            "status": "success",
            "discrepancy_amount": "not_a_number",  # Invalid type
            "reflection": "Processing",
        }

    orchestrator.register_agent("reconciliation_agent", invalid_type_agent)

    # Execute workflow - should run all iterations (invalid type prevents convergence detection)
    result = await orchestrator.execute(sample_reconciliation_task)

    # Verify did not converge (invalid type prevents convergence detection)
    assert result["converged"] is False
    assert len(result["iterations"]) == 2  # Ran all max_iterations


# =============================================================================
# Placeholder Tests for Task 3.6-3.7 (Orchestration Patterns)
# =============================================================================


@pytest.mark.skip(reason="Task 3.6 - State Machine Orchestrator not yet implemented")
def test_should_transition_states_when_state_machine_orchestrator_runs() -> None:
    """Test that state machine orchestrator follows FSM transition rules."""
    pass


@pytest.mark.skip(reason="Task 3.7 - Voting Orchestrator not yet implemented")
def test_should_aggregate_votes_when_voting_orchestrator_runs() -> None:
    """Test that voting orchestrator aggregates multiple agent predictions."""
    pass
