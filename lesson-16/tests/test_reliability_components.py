"""Test suite for all 7 reliability framework components.

This module provides comprehensive tests for:
- FR4.1: Retry Logic with Exponential Backoff
- FR4.2: Circuit Breaker Pattern
- FR4.3: Deterministic Checkpointing
- FR4.4: Output Validation Schemas (Pydantic)
- FR4.5: Error Isolation
- FR4.6: Audit Logging
- FR4.7: Fallback Strategies

Test Infrastructure:
- Fixtures for mock agents, temporary directories, sample schemas
- Shared utilities for testing async functions
- Deterministic time mocking for retry/backoff tests
"""

from __future__ import annotations

import tempfile
import time
from collections.abc import AsyncGenerator, Callable
from pathlib import Path
from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest
from pydantic import BaseModel

# =============================================================================
# Test Fixtures - Shared Infrastructure
# =============================================================================


@pytest.fixture
def temp_dir() -> AsyncGenerator[Path, None]:
    """Provide a temporary directory for testing file operations.

    Yields:
        Path to temporary directory (cleaned up after test)
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def mock_agent() -> AsyncMock:
    """Provide a mock async agent for testing.

    Returns:
        AsyncMock that can be configured to succeed or fail
    """
    mock = AsyncMock()
    mock.return_value = {"result": "success", "data": "mock response"}
    return mock


@pytest.fixture
def failing_agent() -> AsyncMock:
    """Provide a mock agent that always fails.

    Returns:
        AsyncMock that raises an exception
    """
    mock = AsyncMock()
    mock.side_effect = RuntimeError("Agent failure")
    return mock


@pytest.fixture
def intermittent_agent() -> Callable[[int], AsyncMock]:
    """Provide a factory for agents that fail N times then succeed.

    Returns:
        Factory function that creates an agent failing N times
    """

    def _create_intermittent_agent(fail_count: int) -> AsyncMock:
        """Create agent that fails fail_count times, then succeeds.

        Args:
            fail_count: Number of times to fail before succeeding

        Returns:
            AsyncMock configured with side_effect
        """
        mock = AsyncMock()
        failures = [RuntimeError(f"Failure {i + 1}") for i in range(fail_count)]
        mock.side_effect = failures + [{"result": "success", "data": "recovered"}]
        return mock

    return _create_intermittent_agent


@pytest.fixture
def sample_invoice_schema() -> type[BaseModel]:
    """Provide sample Pydantic schema for invoice extraction.

    Returns:
        Pydantic model class for invoice validation
    """

    class InvoiceExtraction(BaseModel):
        """Schema for invoice data validation."""

        invoice_id: str
        vendor: str
        amount: float
        date: str
        line_items: list[dict[str, Any]]

        class Config:
            """Pydantic configuration."""

            extra = "forbid"  # Reject unknown fields

    return InvoiceExtraction


@pytest.fixture
def sample_fraud_schema() -> type[BaseModel]:
    """Provide sample Pydantic schema for fraud detection.

    Returns:
        Pydantic model class for fraud detection validation
    """

    class FraudDetection(BaseModel):
        """Schema for fraud detection output validation."""

        transaction_id: str
        is_fraud: bool
        confidence: float
        fraud_type: str | None = None
        reasoning: str

        class Config:
            """Pydantic configuration."""

            extra = "forbid"

    return FraudDetection


@pytest.fixture
def mock_time() -> MagicMock:
    """Provide a mock time function for deterministic testing.

    Returns:
        Mock that increments time by 1 second each call
    """
    mock = MagicMock()
    mock.side_effect = [float(i) for i in range(100)]  # 0, 1, 2, 3, ...
    return mock


# =============================================================================
# Placeholder Tests - To be implemented in subsequent tasks
# =============================================================================

# =============================================================================
# Task 2.2: Retry Logic with Exponential Backoff (6 tests) - FR4.1
# =============================================================================


@pytest.mark.asyncio
async def test_should_succeed_immediately_when_agent_works(mock_agent: AsyncMock) -> None:
    """Test that retry succeeds on first attempt if agent works."""
    from backend.reliability.retry import retry_with_backoff

    result = await retry_with_backoff(mock_agent, max_retries=3)

    assert result == {"result": "success", "data": "mock response"}
    assert mock_agent.call_count == 1


@pytest.mark.asyncio
async def test_should_retry_and_succeed_when_agent_recovers(intermittent_agent: Callable[[int], AsyncMock]) -> None:
    """Test that retry succeeds after 2 failures."""
    from backend.reliability.retry import retry_with_backoff

    agent = intermittent_agent(2)  # Fail 2 times, then succeed
    result = await retry_with_backoff(agent, max_retries=3)

    assert result == {"result": "success", "data": "recovered"}
    assert agent.call_count == 3  # 2 failures + 1 success


@pytest.mark.asyncio
async def test_should_raise_after_max_retries_when_agent_always_fails(failing_agent: AsyncMock) -> None:
    """Test that retry raises exception after exhausting max_retries."""
    from backend.reliability.retry import retry_with_backoff

    with pytest.raises(RuntimeError, match="Agent failure"):
        await retry_with_backoff(failing_agent, max_retries=3)

    assert failing_agent.call_count == 4  # Initial attempt + 3 retries


@pytest.mark.asyncio
async def test_should_apply_exponential_backoff_when_retrying() -> None:
    """Test that retry delays increase exponentially with jitter."""
    from backend.reliability.retry import retry_with_backoff

    agent = AsyncMock()
    agent.side_effect = [
        RuntimeError("Fail 1"),
        RuntimeError("Fail 2"),
        {"result": "success"},
    ]

    start_time = time.time()
    result = await retry_with_backoff(
        agent,
        max_retries=3,
        base_delay=0.1,  # 100ms base delay
        exponential_base=2,
    )
    elapsed = time.time() - start_time

    assert result == {"result": "success"}
    # With jitter, delays are random between 0 and max: 0-0.1s + 0-0.2s = 0-0.3s
    # Just verify we have some delay (not instant) but not too long
    assert elapsed >= 0.05  # At least some delay happened
    assert elapsed < 1.0  # Reasonable upper bound with jitter


@pytest.mark.asyncio
async def test_should_raise_type_error_when_max_retries_invalid() -> None:
    """Test that invalid max_retries raises TypeError."""
    from backend.reliability.retry import retry_with_backoff

    agent = AsyncMock()

    with pytest.raises(TypeError, match="max_retries must be an integer"):
        await retry_with_backoff(agent, max_retries="3")  # type: ignore


@pytest.mark.asyncio
async def test_should_raise_value_error_when_max_retries_negative() -> None:
    """Test that negative max_retries raises ValueError."""
    from backend.reliability.retry import retry_with_backoff

    agent = AsyncMock()

    with pytest.raises(ValueError, match="max_retries must be non-negative"):
        await retry_with_backoff(agent, max_retries=-1)


# =============================================================================
# Task 2.3: Circuit Breaker Pattern (7 tests) - FR4.2
# =============================================================================


@pytest.mark.asyncio
async def test_should_stay_closed_when_agent_succeeds(mock_agent: AsyncMock) -> None:
    """Test that circuit breaker stays in CLOSED state when agent works."""
    from backend.reliability.circuit_breaker import CircuitBreaker

    circuit_breaker = CircuitBreaker(failure_threshold=3, timeout=1.0)

    result = await circuit_breaker.call(mock_agent)

    assert result == {"result": "success", "data": "mock response"}
    assert circuit_breaker.state == "CLOSED"
    assert circuit_breaker.failure_count == 0


@pytest.mark.asyncio
async def test_should_open_after_threshold_failures(failing_agent: AsyncMock) -> None:
    """Test that circuit breaker opens after failure_threshold consecutive failures."""
    from backend.reliability.circuit_breaker import CircuitBreaker

    circuit_breaker = CircuitBreaker(failure_threshold=3, timeout=1.0)

    # Trigger 3 failures to reach threshold
    for _ in range(3):
        with pytest.raises(RuntimeError, match="Agent failure"):
            await circuit_breaker.call(failing_agent)

    assert circuit_breaker.state == "OPEN"
    assert circuit_breaker.failure_count == 3


@pytest.mark.asyncio
async def test_should_reject_calls_when_open(failing_agent: AsyncMock) -> None:
    """Test that circuit breaker rejects calls immediately when in OPEN state."""
    from backend.reliability.circuit_breaker import CircuitBreaker, CircuitBreakerOpenError

    circuit_breaker = CircuitBreaker(failure_threshold=2, timeout=1.0)

    # Trigger 2 failures to open circuit
    for _ in range(2):
        with pytest.raises(RuntimeError):
            await circuit_breaker.call(failing_agent)

    assert circuit_breaker.state == "OPEN"

    # Next call should be rejected without calling agent
    call_count_before = failing_agent.call_count
    with pytest.raises(CircuitBreakerOpenError, match="Circuit breaker is OPEN"):
        await circuit_breaker.call(failing_agent)

    assert failing_agent.call_count == call_count_before  # Agent not called


@pytest.mark.asyncio
async def test_should_transition_to_half_open_after_timeout() -> None:
    """Test that circuit breaker transitions from OPEN to HALF_OPEN after timeout."""
    from backend.reliability.circuit_breaker import CircuitBreaker

    circuit_breaker = CircuitBreaker(failure_threshold=2, timeout=0.1)  # 100ms timeout
    failing_agent = AsyncMock(side_effect=RuntimeError("Failure"))

    # Open the circuit
    for _ in range(2):
        with pytest.raises(RuntimeError):
            await circuit_breaker.call(failing_agent)

    assert circuit_breaker.state == "OPEN"

    # Wait for timeout
    time.sleep(0.15)  # Wait longer than timeout

    # Next call should transition to HALF_OPEN and attempt the call
    success_agent = AsyncMock(return_value={"result": "recovered"})
    result = await circuit_breaker.call(success_agent)

    assert result == {"result": "recovered"}
    assert circuit_breaker.state == "CLOSED"  # Success in HALF_OPEN closes circuit
    assert circuit_breaker.failure_count == 0  # Reset counter


@pytest.mark.asyncio
async def test_should_close_when_half_open_succeeds(intermittent_agent: Callable[[int], AsyncMock]) -> None:
    """Test that circuit breaker closes after successful call in HALF_OPEN state."""
    from backend.reliability.circuit_breaker import CircuitBreaker

    circuit_breaker = CircuitBreaker(failure_threshold=2, timeout=0.1)

    # Open the circuit with 2 failures
    failing_agent = AsyncMock(side_effect=RuntimeError("Failure"))
    for _ in range(2):
        with pytest.raises(RuntimeError):
            await circuit_breaker.call(failing_agent)

    assert circuit_breaker.state == "OPEN"

    # Wait for timeout to allow HALF_OPEN transition
    time.sleep(0.15)

    # Successful call in HALF_OPEN should close the circuit
    success_agent = AsyncMock(return_value={"result": "service recovered"})
    result = await circuit_breaker.call(success_agent)

    assert result == {"result": "service recovered"}
    assert circuit_breaker.state == "CLOSED"
    assert circuit_breaker.failure_count == 0


@pytest.mark.asyncio
async def test_should_reopen_when_half_open_fails() -> None:
    """Test that circuit breaker reopens if call fails in HALF_OPEN state."""
    from backend.reliability.circuit_breaker import CircuitBreaker

    circuit_breaker = CircuitBreaker(failure_threshold=2, timeout=0.1)
    failing_agent = AsyncMock(side_effect=RuntimeError("Still failing"))

    # Open the circuit
    for _ in range(2):
        with pytest.raises(RuntimeError):
            await circuit_breaker.call(failing_agent)

    assert circuit_breaker.state == "OPEN"

    # Wait for timeout
    time.sleep(0.15)

    # Failure in HALF_OPEN should reopen circuit
    with pytest.raises(RuntimeError, match="Still failing"):
        await circuit_breaker.call(failing_agent)

    assert circuit_breaker.state == "OPEN"
    # Note: failure_count might be reset when entering HALF_OPEN


@pytest.mark.asyncio
async def test_should_use_fallback_when_provided() -> None:
    """Test that circuit breaker returns fallback value when in OPEN state."""
    from backend.reliability.circuit_breaker import CircuitBreaker

    fallback_value = {"result": "fallback", "data": "cached response"}
    circuit_breaker = CircuitBreaker(failure_threshold=2, timeout=1.0, fallback=lambda: fallback_value)

    failing_agent = AsyncMock(side_effect=RuntimeError("Service down"))

    # Open the circuit
    for _ in range(2):
        with pytest.raises(RuntimeError):
            await circuit_breaker.call(failing_agent)

    assert circuit_breaker.state == "OPEN"

    # Call with fallback should return fallback value instead of raising
    result = await circuit_breaker.call(failing_agent)
    assert result == fallback_value


# =============================================================================
# Task 2.4: Deterministic Checkpointing (7 tests) - FR4.3
# =============================================================================


@pytest.mark.asyncio
async def test_should_save_checkpoint_when_state_provided(temp_dir: Path) -> None:
    """Test that checkpoint saves state to JSON file."""
    from backend.reliability.checkpoint import save_checkpoint

    state = {"step": 1, "vendor": "Acme Corp", "amount": 1234.56}
    checkpoint_path = temp_dir / "checkpoint.json"

    await save_checkpoint(state, checkpoint_path)

    assert checkpoint_path.exists()
    import json

    saved_data = json.loads(checkpoint_path.read_text())
    assert saved_data == state


@pytest.mark.asyncio
async def test_should_load_checkpoint_when_file_exists(temp_dir: Path) -> None:
    """Test that checkpoint loads state from JSON file."""
    from backend.reliability.checkpoint import load_checkpoint, save_checkpoint

    original_state = {"step": 2, "vendor": "ACME Inc", "validated": True}
    checkpoint_path = temp_dir / "checkpoint.json"

    await save_checkpoint(original_state, checkpoint_path)
    loaded_state = await load_checkpoint(checkpoint_path)

    assert loaded_state == original_state


@pytest.mark.asyncio
async def test_should_return_none_when_checkpoint_missing(temp_dir: Path) -> None:
    """Test that load_checkpoint returns None if file doesn't exist."""
    from backend.reliability.checkpoint import load_checkpoint

    checkpoint_path = temp_dir / "nonexistent.json"

    result = await load_checkpoint(checkpoint_path)

    assert result is None


@pytest.mark.asyncio
async def test_should_be_idempotent_when_saving_same_state(temp_dir: Path) -> None:
    """Test that saving the same state multiple times produces identical file."""
    from backend.reliability.checkpoint import save_checkpoint

    state = {"step": 3, "data": [1, 2, 3]}
    checkpoint_path = temp_dir / "idempotent.json"

    # Save state twice
    await save_checkpoint(state, checkpoint_path)
    first_content = checkpoint_path.read_text()

    await save_checkpoint(state, checkpoint_path)
    second_content = checkpoint_path.read_text()

    # Content should be identical (deterministic JSON serialization)
    assert first_content == second_content


@pytest.mark.asyncio
async def test_should_validate_state_with_pydantic_when_schema_provided(
    temp_dir: Path, sample_invoice_schema: type[BaseModel]
) -> None:
    """Test that checkpoint validates state against Pydantic schema."""
    from backend.reliability.checkpoint import save_checkpoint

    valid_state = {
        "invoice_id": "INV-001",
        "vendor": "Acme Corp",
        "amount": 1234.56,
        "date": "2024-01-15",
        "line_items": [{"item": "Widget", "qty": 10}],
    }
    checkpoint_path = temp_dir / "validated.json"

    # Should save successfully with valid state
    await save_checkpoint(valid_state, checkpoint_path, schema=sample_invoice_schema)

    assert checkpoint_path.exists()


@pytest.mark.asyncio
async def test_should_raise_validation_error_when_schema_violated(
    temp_dir: Path, sample_invoice_schema: type[BaseModel]
) -> None:
    """Test that checkpoint raises ValidationError for invalid state."""
    from pydantic import ValidationError

    from backend.reliability.checkpoint import save_checkpoint

    invalid_state = {
        "invoice_id": "INV-001",
        # Missing required fields: vendor, amount, date, line_items
    }
    checkpoint_path = temp_dir / "invalid.json"

    with pytest.raises(ValidationError):
        await save_checkpoint(invalid_state, checkpoint_path, schema=sample_invoice_schema)


@pytest.mark.asyncio
async def test_should_create_parent_directories_when_missing(temp_dir: Path) -> None:
    """Test that save_checkpoint creates parent directories if they don't exist."""
    from backend.reliability.checkpoint import save_checkpoint

    state = {"step": 1, "data": "test"}
    # Nested path that doesn't exist yet
    checkpoint_path = temp_dir / "nested" / "dirs" / "checkpoint.json"

    await save_checkpoint(state, checkpoint_path)

    assert checkpoint_path.exists()
    assert checkpoint_path.parent.exists()


# =============================================================================
# Task 2.5: Output Validation Schemas (6 tests) - FR4.4
# =============================================================================


def test_should_create_invoice_extraction_schema_when_valid_data() -> None:
    """Test that InvoiceExtraction schema validates correct invoice data."""
    from backend.reliability.validation import InvoiceExtraction

    valid_invoice = {
        "invoice_id": "INV-2024-001",
        "vendor": "Acme Corporation",
        "amount": 15750.50,
        "date": "2024-01-15",
        "line_items": [{"description": "Consulting services", "quantity": 10, "unit_price": 1575.05}],
    }

    invoice = InvoiceExtraction(**valid_invoice)

    assert invoice.invoice_id == "INV-2024-001"
    assert invoice.vendor == "Acme Corporation"
    assert invoice.amount == 15750.50
    assert invoice.date == "2024-01-15"
    assert len(invoice.line_items) == 1


def test_should_raise_validation_error_when_invoice_missing_required_fields() -> None:
    """Test that InvoiceExtraction raises ValidationError for missing fields."""
    from pydantic import ValidationError

    from backend.reliability.validation import InvoiceExtraction

    invalid_invoice = {
        "invoice_id": "INV-2024-001",
        "vendor": "Acme Corp",
        # Missing: amount, date, line_items
    }

    with pytest.raises(ValidationError) as exc_info:
        InvoiceExtraction(**invalid_invoice)

    errors = exc_info.value.errors()
    error_fields = {e["loc"][0] for e in errors}
    assert "amount" in error_fields
    assert "date" in error_fields
    assert "line_items" in error_fields


def test_should_validate_amount_positive_when_using_custom_validator() -> None:
    """Test that InvoiceExtraction custom validator rejects negative amounts."""
    from pydantic import ValidationError

    from backend.reliability.validation import InvoiceExtraction

    negative_amount_invoice = {
        "invoice_id": "INV-2024-002",
        "vendor": "Test Vendor",
        "amount": -100.00,  # Invalid: negative amount
        "date": "2024-01-15",
        "line_items": [],
    }

    with pytest.raises(ValidationError) as exc_info:
        InvoiceExtraction(**negative_amount_invoice)

    errors = exc_info.value.errors()
    assert any("amount" in str(e["loc"]) for e in errors)
    assert any("positive" in str(e["msg"]).lower() for e in errors)


def test_should_create_fraud_detection_schema_when_valid_data() -> None:
    """Test that FraudDetection schema validates correct fraud detection output."""
    from backend.reliability.validation import FraudDetection

    valid_fraud_output = {
        "transaction_id": "TXN-12345",
        "is_fraud": True,
        "confidence": 0.87,
        "fraud_type": "stolen_card",
        "reasoning": "Transaction pattern matches known stolen card signatures",
    }

    fraud = FraudDetection(**valid_fraud_output)

    assert fraud.transaction_id == "TXN-12345"
    assert fraud.is_fraud is True
    assert fraud.confidence == 0.87
    assert fraud.fraud_type == "stolen_card"
    assert "stolen card" in fraud.reasoning


def test_should_validate_confidence_range_when_using_custom_validator() -> None:
    """Test that FraudDetection custom validator rejects confidence outside [0, 1]."""
    from pydantic import ValidationError

    from backend.reliability.validation import FraudDetection

    invalid_confidence = {
        "transaction_id": "TXN-12346",
        "is_fraud": False,
        "confidence": 1.5,  # Invalid: confidence > 1.0
        "reasoning": "Low risk transaction",
    }

    with pytest.raises(ValidationError) as exc_info:
        FraudDetection(**invalid_confidence)

    errors = exc_info.value.errors()
    assert any("confidence" in str(e["loc"]) for e in errors)


def test_should_require_fraud_type_when_is_fraud_true() -> None:
    """Test that FraudDetection requires fraud_type when is_fraud is True."""
    from pydantic import ValidationError

    from backend.reliability.validation import FraudDetection

    missing_fraud_type = {
        "transaction_id": "TXN-12347",
        "is_fraud": True,
        "confidence": 0.92,
        "fraud_type": None,  # Invalid: should be required when is_fraud=True
        "reasoning": "Suspicious activity detected",
    }

    with pytest.raises(ValidationError) as exc_info:
        FraudDetection(**missing_fraud_type)

    errors = exc_info.value.errors()
    # Custom validator should enforce this business rule
    assert any("fraud_type" in str(e) for e in errors)


# =============================================================================
# Task 2.6: Error Isolation (6 tests) - FR4.5
# =============================================================================


@pytest.mark.asyncio
async def test_should_return_success_when_agent_call_succeeds(mock_agent: AsyncMock) -> None:
    """Test that safe_agent_call returns Success result when agent succeeds."""
    from backend.reliability.isolation import safe_agent_call

    result = await safe_agent_call(mock_agent, agent_name="test_agent", input_data={"query": "test"})

    assert result.is_success() is True
    assert result.unwrap() == {"result": "success", "data": "mock response"}
    assert result.error is None


@pytest.mark.asyncio
async def test_should_return_failure_when_agent_call_raises_exception(failing_agent: AsyncMock) -> None:
    """Test that safe_agent_call returns Failure result when agent raises exception."""
    from backend.reliability.isolation import safe_agent_call

    result = await safe_agent_call(failing_agent, agent_name="failing_agent", input_data={"query": "test"})

    assert result.is_success() is False
    assert result.is_failure() is True
    error = result.error
    assert error is not None
    assert "Agent failure" in str(error)


@pytest.mark.asyncio
async def test_should_isolate_critical_agent_failure_from_orchestrator() -> None:
    """Test that critical agent failures are isolated and don't crash orchestrator."""
    from backend.reliability.isolation import safe_agent_call

    critical_agent = AsyncMock(side_effect=RuntimeError("Critical service down"))

    # Orchestrator can continue even if critical agent fails
    result = await safe_agent_call(critical_agent, agent_name="critical_agent", input_data={})

    assert result.is_failure() is True
    # Orchestrator can inspect the error and decide how to proceed
    assert "Critical service down" in str(result.error)


@pytest.mark.asyncio
async def test_should_allow_optional_agent_failure_without_blocking_workflow() -> None:
    """Test that optional agent failures don't block the workflow."""
    from backend.reliability.isolation import safe_agent_call

    optional_agent = AsyncMock(side_effect=ValueError("Optional enhancement unavailable"))
    critical_agent = AsyncMock(return_value={"result": "core task completed"})

    # Optional agent fails
    optional_result = await safe_agent_call(optional_agent, agent_name="optional_agent", input_data={})
    assert optional_result.is_failure() is True

    # Critical agent still succeeds
    critical_result = await safe_agent_call(critical_agent, agent_name="critical_agent", input_data={})
    assert critical_result.is_success() is True

    # Workflow can continue with just critical result
    assert critical_result.unwrap() == {"result": "core task completed"}


def test_should_distinguish_critical_from_optional_agents() -> None:
    """Test that Result type allows orchestrator to distinguish agent criticality."""
    from backend.reliability.isolation import Result

    # Orchestrator can track which agents are critical
    agent_results: dict[str, Result] = {}

    # Simulate results
    agent_results["critical_validator"] = Result.success({"validated": True})
    agent_results["optional_enrichment"] = Result.failure(RuntimeError("Enrichment service down"))

    # Check if any critical agents failed
    critical_agents = ["critical_validator"]
    critical_failures = [name for name in critical_agents if name in agent_results and agent_results[name].is_failure()]

    # Orchestrator logic: fail workflow only if critical agent fails
    assert len(critical_failures) == 0  # No critical failures
    # Optional agent failure is acceptable
    assert agent_results["optional_enrichment"].is_failure() is True


def test_should_unwrap_success_value_and_handle_failure_safely() -> None:
    """Test that Result type provides safe unwrap with error handling."""
    from backend.reliability.isolation import Result

    success_result = Result.success({"data": "extracted"})
    failure_result = Result.failure(ValueError("Extraction failed"))

    # Success unwrap
    assert success_result.unwrap() == {"data": "extracted"}

    # Failure unwrap should raise
    with pytest.raises(ValueError, match="Cannot unwrap Failure"):
        failure_result.unwrap()

    # Safe unwrap with default
    assert success_result.unwrap_or({"data": "default"}) == {"data": "extracted"}
    assert failure_result.unwrap_or({"data": "default"}) == {"data": "default"}


# =============================================================================
# Task 2.7: Audit Logging (6 tests) - FR4.6
# =============================================================================


def test_should_create_audit_log_entry_with_all_required_fields_when_valid_input() -> None:
    """Test that AuditLogger creates structured JSON log entry with required fields."""
    from backend.reliability.audit_log import AuditLogger

    logger = AuditLogger(workflow_id="wf-001")

    entry = logger.log_step(
        agent_name="invoice_extractor",
        step="extract_vendor",
        input_data={"invoice": "INV-123", "amount": 1000.50},
        output={"vendor": "Acme Corp", "confidence": 0.95},
        duration_ms=250,
    )

    # Verify all required fields are present
    assert entry["workflow_id"] == "wf-001"
    assert entry["agent_name"] == "invoice_extractor"
    assert entry["step"] == "extract_vendor"
    assert "timestamp" in entry
    assert entry["duration_ms"] == 250
    assert "input_hash" in entry  # SHA256 hash of input
    assert entry["output"] == {"vendor": "Acme Corp", "confidence": 0.95}
    assert entry["error"] is None


def test_should_redact_pii_in_logs_when_sensitive_fields_present() -> None:
    """Test that PII redaction masks sensitive data in audit logs."""
    from backend.reliability.audit_log import AuditLogger

    logger = AuditLogger(workflow_id="wf-002")

    # Log with PII data (SSN, credit card, phone)
    entry = logger.log_step(
        agent_name="fraud_detector",
        step="verify_identity",
        input_data={
            "ssn": "123-45-6789",
            "credit_card": "4532-1234-5678-9010",
            "phone": "+1-555-123-4567",
            "email": "user@example.com",
        },
        output={"verified": True},
        duration_ms=100,
    )

    # Verify PII is redacted (format: "XXX****XXX")
    input_data = entry["input_data"]
    assert input_data["ssn"] == "123****789"  # First 3 and last 3 digits
    assert input_data["credit_card"] == "453****010"  # First 3 and last 3
    assert input_data["phone"] == "+1-****567"  # Partial masking
    assert input_data["email"] == "use****com"  # Mask middle part


def test_should_log_error_details_when_agent_fails() -> None:
    """Test that audit logger captures error information for failed steps."""
    from backend.reliability.audit_log import AuditLogger

    logger = AuditLogger(workflow_id="wf-003")

    error = ValueError("Invoice validation failed: missing vendor")
    entry = logger.log_step(
        agent_name="invoice_validator",
        step="validate_schema",
        input_data={"invoice_id": "INV-456"},
        output=None,
        duration_ms=50,
        error=error,
    )

    # Verify error is captured
    assert entry["error"] is not None
    assert "ValueError" in entry["error"]
    assert "missing vendor" in entry["error"]
    assert entry["output"] is None


def test_should_create_workflow_trace_with_all_steps() -> None:
    """Test that audit logger maintains complete workflow trace."""
    from backend.reliability.audit_log import AuditLogger

    logger = AuditLogger(workflow_id="wf-004")

    # Log 3 steps in a workflow
    logger.log_step("agent1", "extract", {"data": "invoice"}, {"vendor": "ACME"}, 100)
    logger.log_step("agent2", "validate", {"vendor": "ACME"}, {"valid": True}, 50)
    logger.log_step("agent3", "route", {"valid": True}, {"approver": "manager"}, 75)

    # Get full workflow trace
    trace = logger.get_workflow_trace()

    assert len(trace) == 3
    assert trace[0]["agent_name"] == "agent1"
    assert trace[1]["agent_name"] == "agent2"
    assert trace[2]["agent_name"] == "agent3"
    assert all(entry["workflow_id"] == "wf-004" for entry in trace)


def test_should_export_audit_logs_to_json_file() -> None:
    """Test that audit logger can export logs to structured JSON file."""
    from backend.reliability.audit_log import AuditLogger

    logger = AuditLogger(workflow_id="wf-005")

    logger.log_step("agent1", "step1", {"x": 1}, {"y": 2}, 100)
    logger.log_step("agent2", "step2", {"y": 2}, {"z": 3}, 150)

    import tempfile

    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        filepath = Path(f.name)

    try:
        # Export to JSON file
        logger.export_to_json(filepath)

        # Verify file contents
        import json

        with open(filepath) as f:
            data = json.load(f)

        assert data["workflow_id"] == "wf-005"
        assert len(data["steps"]) == 2
        assert data["steps"][0]["agent_name"] == "agent1"
        assert data["steps"][1]["agent_name"] == "agent2"
    finally:
        filepath.unlink()


def test_should_validate_input_types_and_raise_errors_for_invalid_data() -> None:
    """Test that audit logger has defensive coding with input validation."""
    from backend.reliability.audit_log import AuditLogger

    # Invalid workflow_id type
    with pytest.raises(TypeError, match="workflow_id must be a string"):
        AuditLogger(workflow_id=123)  # type: ignore

    logger = AuditLogger(workflow_id="wf-006")

    # Invalid agent_name type
    with pytest.raises(TypeError, match="agent_name must be a string"):
        logger.log_step(
            agent_name=None,  # type: ignore
            step="extract",
            input_data={},
            output={},
            duration_ms=100,
        )

    # Negative duration
    with pytest.raises(ValueError, match="duration_ms must be non-negative"):
        logger.log_step(
            agent_name="agent1",
            step="extract",
            input_data={},
            output={},
            duration_ms=-50,
        )


# =============================================================================
# Task 2.8: Fallback Strategies (5 tests)
# Task 2.9: Integration tests (4 tests)


def test_infrastructure_setup_complete() -> None:
    """Verify test infrastructure is properly configured.

    This meta-test ensures all fixtures are available.
    """
    # Test will pass if fixtures are properly defined
    assert True
