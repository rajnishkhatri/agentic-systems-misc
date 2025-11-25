"""Infrastructure tests for integration test setup.

This module validates that all integration test infrastructure is correctly set up:
- Fixtures work correctly
- Mock agents behave as expected
- Test data generators produce valid data
- Integration markers are configured
"""

from typing import Any

import pytest

from .conftest import (
    EdgeCaseDataGenerator,
    MockLLMAgent,
)

# ============================================================================
# Test 1: Mock Agent Basic Functionality
# ============================================================================


@pytest.mark.integration
def test_should_create_mock_agent_when_valid_parameters() -> None:
    """Test that MockLLMAgent can be instantiated with valid parameters."""
    # Arrange & Act
    agent = MockLLMAgent(
        name="test_agent",
        success_rate=0.9,
        response_template='{"result": "{input}"}',
        latency_ms=50,
    )

    # Assert
    assert agent.name == "test_agent"
    assert agent.success_rate == 0.9
    assert agent.latency_ms == 50
    assert agent.call_count == 0
    assert len(agent.call_history) == 0


# ============================================================================
# Test 2: Mock Agent Execute Success
# ============================================================================


@pytest.mark.integration
@pytest.mark.asyncio
async def test_should_execute_successfully_when_no_failure_mode() -> None:
    """Test that MockLLMAgent executes successfully with no failure mode."""
    # Arrange
    agent = MockLLMAgent(
        name="success_agent",
        success_rate=1.0,
        response_template='{"result": "processed"}',
        latency_ms=10,
    )
    input_data = {"query": "test"}

    # Act
    response = await agent.execute(input_data)

    # Assert
    assert response["agent"] == "success_agent"
    assert response["confidence"] == 0.95
    assert agent.call_count == 1
    assert len(agent.call_history) == 1
    assert agent.call_history[0]["status"] == "success"


# ============================================================================
# Test 3: Mock Agent Failure Modes
# ============================================================================


@pytest.mark.integration
@pytest.mark.asyncio
async def test_should_raise_timeout_when_timeout_failure_mode() -> None:
    """Test that MockLLMAgent raises TimeoutError with timeout failure mode."""
    # Arrange
    agent = MockLLMAgent(
        name="timeout_agent",
        success_rate=1.0,
        failure_mode="timeout",
        latency_ms=10,
    )
    input_data = {"query": "test"}

    # Act & Assert
    with pytest.raises(TimeoutError, match="timeout_agent failed"):
        await agent.execute(input_data)

    assert agent.call_count == 1
    assert agent.call_history[0]["status"] == "timeout"


@pytest.mark.integration
@pytest.mark.asyncio
async def test_should_raise_error_when_error_failure_mode() -> None:
    """Test that MockLLMAgent raises RuntimeError with error failure mode."""
    # Arrange
    agent = MockLLMAgent(
        name="error_agent",
        success_rate=1.0,
        failure_mode="error",
        latency_ms=10,
    )
    input_data = {"query": "test"}

    # Act & Assert
    with pytest.raises(RuntimeError, match="error_agent failed"):
        await agent.execute(input_data)

    assert agent.call_count == 1
    assert agent.call_history[0]["status"] == "error"


@pytest.mark.integration
@pytest.mark.asyncio
async def test_should_return_hallucinated_data_when_hallucination_failure_mode() -> None:
    """Test that MockLLMAgent returns hallucinated data with hallucination failure mode."""
    # Arrange
    agent = MockLLMAgent(
        name="hallucination_agent",
        success_rate=1.0,
        failure_mode="hallucination",
        latency_ms=10,
    )
    input_data = {"query": "test"}

    # Act
    response = await agent.execute(input_data)

    # Assert
    assert response["result"] == "HALLUCINATED_DATA"
    assert response["confidence"] == 0.3
    assert agent.call_count == 1
    assert agent.call_history[0]["status"] == "hallucination"


# ============================================================================
# Test 4: Edge Case Data Generators
# ============================================================================


@pytest.mark.integration
def test_should_generate_invoice_edge_cases_when_called() -> None:
    """Test that EdgeCaseDataGenerator produces valid invoice edge cases."""
    # Arrange
    generator = EdgeCaseDataGenerator()

    # Act
    edge_cases = generator.generate_invoice_edge_cases()

    # Assert
    assert len(edge_cases) == 8, "Should generate 8 invoice edge cases"
    assert any("vendor" not in case for case in edge_cases), "Should include missing vendor case"
    assert any(case.get("amount", 1) < 0 for case in edge_cases), "Should include negative amount case"
    assert any(case.get("amount") == 0 for case in edge_cases), "Should include zero amount case"
    assert any(case.get("amount", 0) > 1000000 for case in edge_cases), "Should include large amount case"


@pytest.mark.integration
def test_should_generate_transaction_edge_cases_when_called() -> None:
    """Test that EdgeCaseDataGenerator produces valid transaction edge cases."""
    # Arrange
    generator = EdgeCaseDataGenerator()

    # Act
    edge_cases = generator.generate_transaction_edge_cases()

    # Assert
    assert len(edge_cases) == 8, "Should generate 8 transaction edge cases"
    assert any(case.get("amount", 0) > 100000 for case in edge_cases), "Should include high-value transaction"
    assert any(case.get("amount") == 0 for case in edge_cases), "Should include zero amount case"
    assert any("merchant" not in case for case in edge_cases), "Should include missing merchant case"


@pytest.mark.integration
def test_should_generate_reconciliation_edge_cases_when_called() -> None:
    """Test that EdgeCaseDataGenerator produces valid reconciliation edge cases."""
    # Arrange
    generator = EdgeCaseDataGenerator()

    # Act
    edge_cases = generator.generate_reconciliation_edge_cases()

    # Assert
    assert len(edge_cases) == 5, "Should generate 5 reconciliation edge cases"
    assert any("expected_matches" in case for case in edge_cases), "Should include exact match case"
    assert any("date_mismatch" in case.get("challenge_types", []) for case in edge_cases), "Should include date mismatch"
    assert any("amount_rounding" in case.get("challenge_types", []) for case in edge_cases), "Should include amount rounding"
    assert any("missing_counterparty" in case.get("challenge_types", []) for case in edge_cases), "Should include missing counterparty"


# ============================================================================
# Test 5: Fixture Integration (Invoice)
# ============================================================================


@pytest.mark.integration
def test_should_provide_mock_extract_vendor_agent_when_fixture_used(
    mock_extract_vendor_agent: MockLLMAgent,
) -> None:
    """Test that invoice vendor extraction agent fixture works correctly."""
    # Assert
    assert mock_extract_vendor_agent.name == "extract_vendor_agent"
    assert mock_extract_vendor_agent.success_rate == 0.9
    assert mock_extract_vendor_agent.latency_ms == 50
    assert mock_extract_vendor_agent.call_count == 0


# ============================================================================
# Test 6: Fixture Integration (Fraud)
# ============================================================================


@pytest.mark.integration
def test_should_provide_mock_fraud_detection_agent_when_fixture_used(
    mock_fraud_detection_agent: MockLLMAgent,
) -> None:
    """Test that fraud detection agent fixture works correctly."""
    # Assert
    assert mock_fraud_detection_agent.name == "fraud_detection_agent"
    assert mock_fraud_detection_agent.success_rate == 0.85
    assert mock_fraud_detection_agent.latency_ms == 100
    assert mock_fraud_detection_agent.call_count == 0


# ============================================================================
# Test 7: Fixture Integration (Reconciliation)
# ============================================================================


@pytest.mark.integration
def test_should_provide_mock_reconciliation_agent_when_fixture_used(
    mock_reconciliation_agent: MockLLMAgent,
) -> None:
    """Test that reconciliation agent fixture works correctly."""
    # Assert
    assert mock_reconciliation_agent.name == "reconciliation_agent"
    assert mock_reconciliation_agent.success_rate == 0.8
    assert mock_reconciliation_agent.latency_ms == 150
    assert mock_reconciliation_agent.call_count == 0


# ============================================================================
# Test 8: Workflow State Fixtures
# ============================================================================


@pytest.mark.integration
def test_should_provide_workflow_state_fixtures_when_used(
    sample_invoice_workflow_state: dict[str, Any],
    sample_fraud_workflow_state: dict[str, Any],
    sample_reconciliation_workflow_state: dict[str, Any],
) -> None:
    """Test that all workflow state fixtures contain required keys."""
    # Assert invoice workflow state
    assert "workflow_id" in sample_invoice_workflow_state
    assert "invoice_id" in sample_invoice_workflow_state
    assert "vendor" in sample_invoice_workflow_state
    assert "amount" in sample_invoice_workflow_state
    assert "status" in sample_invoice_workflow_state

    # Assert fraud workflow state
    assert "workflow_id" in sample_fraud_workflow_state
    assert "transaction_id" in sample_fraud_workflow_state
    assert "amount" in sample_fraud_workflow_state
    assert "merchant" in sample_fraud_workflow_state
    assert "user_id" in sample_fraud_workflow_state

    # Assert reconciliation workflow state
    assert "workflow_id" in sample_reconciliation_workflow_state
    assert "reconciliation_id" in sample_reconciliation_workflow_state
    assert "bank_amount" in sample_reconciliation_workflow_state
    assert "ledger_amount" in sample_reconciliation_workflow_state
    assert "discrepancy" in sample_reconciliation_workflow_state
