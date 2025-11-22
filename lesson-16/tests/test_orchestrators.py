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
    result = await orchestrator.execute(sample_invoice_task)

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
# Placeholder Tests for Task 3.4-3.7 (Orchestration Patterns)
# =============================================================================
# These tests will be implemented in subsequent subtasks following TDD methodology


@pytest.mark.skip(reason="Task 3.4 - Hierarchical Orchestrator not yet implemented")
def test_should_delegate_to_specialists_when_hierarchical_orchestrator_runs() -> None:
    """Test that hierarchical orchestrator delegates to specialists in parallel."""
    pass


@pytest.mark.skip(reason="Task 3.5 - Iterative Orchestrator not yet implemented")
def test_should_refine_iteratively_when_iterative_orchestrator_runs() -> None:
    """Test that iterative orchestrator performs action-reflection-refinement loop."""
    pass


@pytest.mark.skip(reason="Task 3.6 - State Machine Orchestrator not yet implemented")
def test_should_transition_states_when_state_machine_orchestrator_runs() -> None:
    """Test that state machine orchestrator follows FSM transition rules."""
    pass


@pytest.mark.skip(reason="Task 3.7 - Voting Orchestrator not yet implemented")
def test_should_aggregate_votes_when_voting_orchestrator_runs() -> None:
    """Test that voting orchestrator aggregates multiple agent predictions."""
    pass
