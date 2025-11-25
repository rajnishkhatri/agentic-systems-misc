"""Fixtures for integration tests.

This module provides shared fixtures for end-to-end testing of the reliability framework:
- Mock LLM agents with deterministic responses
- Test data generators for edge cases
- Orchestrator fixtures with reliability components
- Financial workflow test data (invoices, fraud, reconciliation)
"""

import asyncio
import json
import tempfile
from pathlib import Path
from typing import Any

import pytest

# ============================================================================
# Mock LLM Agents with Deterministic Responses
# ============================================================================


class MockLLMAgent:
    """Mock LLM agent with deterministic responses for testing.

    Args:
        name: Agent name for identification
        success_rate: Probability of successful execution (0.0-1.0)
        response_template: Template for responses with {input} placeholder
        latency_ms: Simulated latency in milliseconds
        failure_mode: Type of failure ('timeout', 'error', 'hallucination', None)
    """

    def __init__(
        self,
        name: str,
        success_rate: float = 1.0,
        response_template: str = "Processed: {input}",
        latency_ms: int = 100,
        failure_mode: str | None = None,
    ) -> None:
        """Initialize mock agent with deterministic behavior."""
        # Step 1: Type checking
        if not isinstance(name, str):
            raise TypeError("name must be a string")
        if not isinstance(success_rate, (int, float)):
            raise TypeError("success_rate must be a number")
        if not isinstance(response_template, str):
            raise TypeError("response_template must be a string")
        if not isinstance(latency_ms, int):
            raise TypeError("latency_ms must be an integer")

        # Step 2: Input validation
        if not name:
            raise ValueError("name cannot be empty")
        if not 0.0 <= success_rate <= 1.0:
            raise ValueError("success_rate must be between 0.0 and 1.0")
        if latency_ms < 0:
            raise ValueError("latency_ms must be non-negative")
        if failure_mode and failure_mode not in ["timeout", "error", "hallucination", "context_overflow"]:
            raise ValueError(f"Invalid failure_mode: {failure_mode}")

        # Step 3: Initialize
        self.name = name
        self.success_rate = success_rate
        self.response_template = response_template
        self.latency_ms = latency_ms
        self.failure_mode = failure_mode
        self.call_count = 0
        self.call_history: list[dict[str, Any]] = []

    async def execute(self, input_data: dict[str, Any]) -> dict[str, Any]:
        """Execute agent with deterministic behavior.

        Args:
            input_data: Input data for agent

        Returns:
            Response dictionary with result or error

        Raises:
            TimeoutError: If failure_mode is 'timeout'
            RuntimeError: If failure_mode is 'error'
        """
        # Step 1: Type checking
        if not isinstance(input_data, dict):
            raise TypeError("input_data must be a dictionary")

        # Step 2: Increment call count
        self.call_count += 1

        # Step 3: Simulate latency
        await asyncio.sleep(self.latency_ms / 1000.0)

        # Step 4: Determine success based on call_count and success_rate
        # Use deterministic pattern: fail every N calls where N = 1/success_rate
        should_succeed = self.success_rate == 1.0 or (self.call_count % int(1 / (1 - self.success_rate))) != 0

        # Step 5: Handle failure modes
        if not should_succeed or self.failure_mode:
            error_msg = f"{self.name} failed on call {self.call_count}"

            if self.failure_mode == "timeout":
                self.call_history.append({"input": input_data, "status": "timeout", "call": self.call_count})
                raise TimeoutError(error_msg)
            elif self.failure_mode == "error":
                self.call_history.append({"input": input_data, "status": "error", "call": self.call_count})
                raise RuntimeError(error_msg)
            elif self.failure_mode == "hallucination":
                # Return incorrect data
                response = {"result": "HALLUCINATED_DATA", "confidence": 0.3, "agent": self.name}
                self.call_history.append({"input": input_data, "response": response, "status": "hallucination", "call": self.call_count})
                return response
            elif self.failure_mode == "context_overflow":
                # Return truncated data
                response = {"result": "TRUNCATED...", "warning": "context_overflow", "agent": self.name}
                self.call_history.append({"input": input_data, "response": response, "status": "context_overflow", "call": self.call_count})
                return response

        # Step 6: Success path
        # Use simple string concatenation to avoid format string issues with JSON
        result = f"Processed: {json.dumps(input_data)}"
        response = {"result": result, "confidence": 0.95, "agent": self.name}
        self.call_history.append({"input": input_data, "response": response, "status": "success", "call": self.call_count})

        return response

    def reset(self) -> None:
        """Reset agent state for new test."""
        self.call_count = 0
        self.call_history = []


# ============================================================================
# Test Data Generators for Edge Cases
# ============================================================================


class EdgeCaseDataGenerator:
    """Generate edge case test data for financial workflows."""

    @staticmethod
    def generate_invoice_edge_cases() -> list[dict[str, Any]]:
        """Generate invoice edge cases for testing.

        Returns:
            List of invoice dictionaries with edge cases
        """
        return [
            # Edge case 1: Missing vendor
            {"invoice_id": "INV-EDGE-001", "amount": 1000.0, "line_items": []},
            # Edge case 2: Negative amount
            {"invoice_id": "INV-EDGE-002", "vendor": "Test Vendor", "amount": -500.0},
            # Edge case 3: Zero amount
            {"invoice_id": "INV-EDGE-003", "vendor": "Test Vendor", "amount": 0.0},
            # Edge case 4: Extremely large amount
            {"invoice_id": "INV-EDGE-004", "vendor": "Test Vendor", "amount": 999999999.99},
            # Edge case 5: OCR error in vendor name
            {"invoice_id": "INV-EDGE-005", "vendor": "T3st V3nd0r", "amount": 1000.0, "ocr_confidence": 0.3},
            # Edge case 6: Duplicate invoice ID
            {"invoice_id": "INV-2024-001", "vendor": "Duplicate Vendor", "amount": 500.0},
            # Edge case 7: Missing line items
            {"invoice_id": "INV-EDGE-007", "vendor": "Test Vendor", "amount": 1000.0, "line_items": None},
            # Edge case 8: Future date
            {"invoice_id": "INV-EDGE-008", "vendor": "Test Vendor", "amount": 1000.0, "date": "2030-12-31"},
        ]

    @staticmethod
    def generate_transaction_edge_cases() -> list[dict[str, Any]]:
        """Generate transaction edge cases for fraud detection testing.

        Returns:
            List of transaction dictionaries with edge cases
        """
        return [
            # Edge case 1: High-value transaction ($100K+)
            {"transaction_id": "TXN-EDGE-001", "amount": 150000.0, "merchant": "Luxury Store", "user_id": "user_001"},
            # Edge case 2: Midnight transaction (suspicious timing)
            {"transaction_id": "TXN-EDGE-002", "amount": 5000.0, "merchant": "Gas Station", "timestamp": "2024-11-01T03:45:00Z", "user_id": "user_002"},
            # Edge case 3: Foreign country transaction
            {"transaction_id": "TXN-EDGE-003", "amount": 2000.0, "merchant": "Foreign Vendor", "country": "Unknown", "user_id": "user_003"},
            # Edge case 4: Multiple rapid transactions (velocity check)
            {"transaction_id": "TXN-EDGE-004", "amount": 100.0, "merchant": "Store A", "timestamp": "2024-11-01T10:00:00Z", "user_id": "user_004"},
            {"transaction_id": "TXN-EDGE-005", "amount": 200.0, "merchant": "Store B", "timestamp": "2024-11-01T10:01:00Z", "user_id": "user_004"},
            {"transaction_id": "TXN-EDGE-006", "amount": 300.0, "merchant": "Store C", "timestamp": "2024-11-01T10:02:00Z", "user_id": "user_004"},
            # Edge case 5: Zero amount transaction
            {"transaction_id": "TXN-EDGE-007", "amount": 0.0, "merchant": "Test Merchant", "user_id": "user_005"},
            # Edge case 6: Missing merchant
            {"transaction_id": "TXN-EDGE-008", "amount": 500.0, "user_id": "user_006"},
        ]

    @staticmethod
    def generate_reconciliation_edge_cases() -> list[dict[str, Any]]:
        """Generate reconciliation edge cases for account matching testing.

        Returns:
            List of reconciliation dictionaries with edge cases
        """
        return [
            # Edge case 1: Exact match
            {
                "reconciliation_id": "REC-EDGE-001",
                "bank_transactions": [{"bank_id": "B001", "amount": 1000.0, "date": "2024-11-01"}],
                "ledger_entries": [{"ledger_id": "L001", "amount": 1000.0, "date": "2024-11-01"}],
                "expected_matches": [{"bank_id": "B001", "ledger_id": "L001"}],
            },
            # Edge case 2: Date mismatch (posting delay)
            {
                "reconciliation_id": "REC-EDGE-002",
                "bank_transactions": [{"bank_id": "B002", "amount": 500.0, "date": "2024-11-01"}],
                "ledger_entries": [{"ledger_id": "L002", "amount": 500.0, "date": "2024-11-03"}],
                "challenge_types": ["date_mismatch"],
            },
            # Edge case 3: Amount rounding difference
            {
                "reconciliation_id": "REC-EDGE-003",
                "bank_transactions": [{"bank_id": "B003", "amount": 1234.56, "date": "2024-11-01"}],
                "ledger_entries": [{"ledger_id": "L003", "amount": 1234.50, "date": "2024-11-01"}],
                "challenge_types": ["amount_rounding"],
            },
            # Edge case 4: Missing counterparty (unmatched bank transaction)
            {
                "reconciliation_id": "REC-EDGE-004",
                "bank_transactions": [{"bank_id": "B004", "amount": 750.0, "date": "2024-11-01"}],
                "ledger_entries": [],
                "challenge_types": ["missing_counterparty"],
            },
            # Edge case 5: Duplicate entries (same amount, same date)
            {
                "reconciliation_id": "REC-EDGE-005",
                "bank_transactions": [
                    {"bank_id": "B005", "amount": 100.0, "date": "2024-11-01"},
                    {"bank_id": "B006", "amount": 100.0, "date": "2024-11-01"},
                ],
                "ledger_entries": [{"ledger_id": "L005", "amount": 100.0, "date": "2024-11-01"}],
                "challenge_types": ["duplicate_entries"],
            },
        ]


# ============================================================================
# Pytest Fixtures
# ============================================================================


@pytest.fixture
def mock_extract_vendor_agent() -> MockLLMAgent:
    """Fixture: Mock agent for invoice vendor extraction."""
    return MockLLMAgent(
        name="extract_vendor_agent",
        success_rate=0.9,
        response_template='{{vendor": "{input}", "confidence": 0.95}}',
        latency_ms=50,
    )


@pytest.fixture
def mock_validate_amount_agent() -> MockLLMAgent:
    """Fixture: Mock agent for invoice amount validation."""
    return MockLLMAgent(
        name="validate_amount_agent",
        success_rate=0.95,
        response_template='{{is_valid": true, "amount": "{input}"}}',
        latency_ms=30,
    )


@pytest.fixture
def mock_route_approval_agent() -> MockLLMAgent:
    """Fixture: Mock agent for approval routing."""
    return MockLLMAgent(
        name="route_approval_agent",
        success_rate=1.0,
        response_template='{{"approver": "manager", "reason": "Amount under $10K"}}',
        latency_ms=20,
    )


@pytest.fixture
def mock_fraud_detection_agent() -> MockLLMAgent:
    """Fixture: Mock agent for fraud detection."""
    return MockLLMAgent(
        name="fraud_detection_agent",
        success_rate=0.85,
        response_template='{{"is_fraud": false, "confidence": 0.9, "reason": "Normal transaction pattern"}}',
        latency_ms=100,
    )


@pytest.fixture
def mock_reconciliation_agent() -> MockLLMAgent:
    """Fixture: Mock agent for account reconciliation."""
    return MockLLMAgent(
        name="reconciliation_agent",
        success_rate=0.8,
        response_template='{{"matched": true, "discrepancy": 0.0}}',
        latency_ms=150,
    )


@pytest.fixture
def failing_agent() -> MockLLMAgent:
    """Fixture: Agent that always fails (for error testing)."""
    return MockLLMAgent(
        name="failing_agent",
        success_rate=0.0,
        failure_mode="error",
        latency_ms=10,
    )


@pytest.fixture
def timeout_agent() -> MockLLMAgent:
    """Fixture: Agent that always times out."""
    return MockLLMAgent(
        name="timeout_agent",
        success_rate=0.0,
        failure_mode="timeout",
        latency_ms=10,
    )


@pytest.fixture
def hallucination_agent() -> MockLLMAgent:
    """Fixture: Agent that hallucinates (returns incorrect data)."""
    return MockLLMAgent(
        name="hallucination_agent",
        success_rate=1.0,
        failure_mode="hallucination",
        latency_ms=50,
    )


@pytest.fixture
def edge_case_generator() -> EdgeCaseDataGenerator:
    """Fixture: Edge case data generator."""
    return EdgeCaseDataGenerator()


@pytest.fixture
def invoice_edge_cases(edge_case_generator: EdgeCaseDataGenerator) -> list[dict[str, Any]]:
    """Fixture: Invoice edge case test data."""
    return edge_case_generator.generate_invoice_edge_cases()


@pytest.fixture
def transaction_edge_cases(edge_case_generator: EdgeCaseDataGenerator) -> list[dict[str, Any]]:
    """Fixture: Transaction edge case test data."""
    return edge_case_generator.generate_transaction_edge_cases()


@pytest.fixture
def reconciliation_edge_cases(edge_case_generator: EdgeCaseDataGenerator) -> list[dict[str, Any]]:
    """Fixture: Reconciliation edge case test data."""
    return edge_case_generator.generate_reconciliation_edge_cases()


@pytest.fixture
def temp_checkpoint_dir() -> Path:
    """Fixture: Temporary directory for checkpoint storage."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def temp_cache_dir() -> Path:
    """Fixture: Temporary directory for cache storage."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def sample_invoice_workflow_state() -> dict[str, Any]:
    """Fixture: Sample workflow state for invoice processing."""
    return {
        "workflow_id": "test_invoice_001",
        "invoice_id": "INV-2024-001",
        "vendor": "Acme Corp",
        "amount": 5000.0,
        "status": "pending",
        "steps_completed": [],
        "errors": [],
    }


@pytest.fixture
def sample_fraud_workflow_state() -> dict[str, Any]:
    """Fixture: Sample workflow state for fraud detection."""
    return {
        "workflow_id": "test_fraud_001",
        "transaction_id": "TXN-12345",
        "amount": 15000.0,
        "merchant": "Luxury Store",
        "user_id": "user_123",
        "status": "pending",
        "fraud_checks": [],
        "confidence_scores": [],
    }


@pytest.fixture
def sample_reconciliation_workflow_state() -> dict[str, Any]:
    """Fixture: Sample workflow state for account reconciliation."""
    return {
        "workflow_id": "test_recon_001",
        "reconciliation_id": "REC-2024-001",
        "bank_amount": 1234.56,
        "ledger_amount": 1234.50,
        "discrepancy": 0.06,
        "status": "pending",
        "iterations": 0,
        "max_iterations": 5,
    }
