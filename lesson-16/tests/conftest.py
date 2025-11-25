"""Shared test utilities and fixtures for Lesson 16 test suite.

This module provides shared utilities for all test modules:
- Dataset loaders for invoices, transactions, reconciliation
- Orchestrator factories with reliability components
- Metric calculators for validation
- Assertion helpers for common test patterns
"""

import json
from pathlib import Path
from typing import Any

import pytest

# ============================================================================
# Dataset Loaders
# ============================================================================


class DatasetLoader:
    """Utility class for loading test datasets."""

    @staticmethod
    def load_invoices(limit: int | None = None) -> list[dict[str, Any]]:
        """Load invoice dataset from data/invoices_100.json.

        Args:
            limit: Optional limit on number of invoices to load

        Returns:
            List of invoice dictionaries

        Raises:
            FileNotFoundError: If dataset file doesn't exist
            json.JSONDecodeError: If JSON is malformed
        """
        # Step 1: Construct path
        dataset_path = Path(__file__).parent.parent / "data" / "invoices_100.json"

        # Step 2: Validate file exists
        if not dataset_path.exists():
            raise FileNotFoundError(f"Dataset not found: {dataset_path}")

        # Step 3: Load JSON
        with open(dataset_path) as f:
            data = json.load(f)

        # Step 4: Extract invoices array from metadata wrapper
        if isinstance(data, dict) and "invoices" in data:
            invoices = data["invoices"]
        else:
            invoices = data

        # Step 5: Apply limit if specified
        if limit is not None:
            invoices = invoices[:limit]

        return invoices

    @staticmethod
    def load_transactions(limit: int | None = None) -> list[dict[str, Any]]:
        """Load transaction dataset from data/transactions_100.json.

        Args:
            limit: Optional limit on number of transactions to load

        Returns:
            List of transaction dictionaries

        Raises:
            FileNotFoundError: If dataset file doesn't exist
            json.JSONDecodeError: If JSON is malformed
        """
        # Step 1: Construct path
        dataset_path = Path(__file__).parent.parent / "data" / "transactions_100.json"

        # Step 2: Validate file exists
        if not dataset_path.exists():
            raise FileNotFoundError(f"Dataset not found: {dataset_path}")

        # Step 3: Load JSON
        with open(dataset_path) as f:
            data = json.load(f)

        # Step 4: Extract transactions array from metadata wrapper
        if isinstance(data, dict) and "transactions" in data:
            transactions = data["transactions"]
        else:
            transactions = data

        # Step 5: Apply limit if specified
        if limit is not None:
            transactions = transactions[:limit]

        return transactions

    @staticmethod
    def load_reconciliations(limit: int | None = None) -> list[dict[str, Any]]:
        """Load reconciliation dataset from data/reconciliation_100.json.

        Args:
            limit: Optional limit on number of reconciliations to load

        Returns:
            List of reconciliation dictionaries

        Raises:
            FileNotFoundError: If dataset file doesn't exist
            json.JSONDecodeError: If JSON is malformed
        """
        # Step 1: Construct path
        dataset_path = Path(__file__).parent.parent / "data" / "reconciliation_100.json"

        # Step 2: Validate file exists
        if not dataset_path.exists():
            raise FileNotFoundError(f"Dataset not found: {dataset_path}")

        # Step 3: Load JSON
        with open(dataset_path) as f:
            data = json.load(f)

        # Step 4: Extract reconciliations array from metadata wrapper
        if isinstance(data, dict) and "reconciliations" in data:
            reconciliations = data["reconciliations"]
        else:
            reconciliations = data

        # Step 5: Apply limit if specified
        if limit is not None:
            reconciliations = reconciliations[:limit]

        return reconciliations


# ============================================================================
# Assertion Helpers
# ============================================================================


class AssertionHelpers:
    """Helper functions for common test assertions."""

    @staticmethod
    def assert_success_rate_above_threshold(
        results: list[dict[str, Any]],
        threshold: float,
        status_key: str = "status",
        success_value: str = "success",
    ) -> None:
        """Assert that success rate meets or exceeds threshold.

        Args:
            results: List of result dictionaries
            threshold: Minimum success rate (0.0-1.0)
            status_key: Key in result dict containing status
            success_value: Value indicating success

        Raises:
            AssertionError: If success rate below threshold
        """
        # Step 1: Input validation
        if not results:
            raise ValueError("results list cannot be empty")
        if not 0.0 <= threshold <= 1.0:
            raise ValueError("threshold must be between 0.0 and 1.0")

        # Step 2: Calculate success rate
        successful = sum(1 for r in results if r.get(status_key) == success_value)
        success_rate = successful / len(results)

        # Step 3: Assert threshold
        assert success_rate >= threshold, (
            f"Success rate {success_rate:.2%} below threshold {threshold:.2%} "
            f"({successful}/{len(results)} successful)"
        )

    @staticmethod
    def assert_all_required_keys_present(
        data: dict[str, Any],
        required_keys: list[str],
    ) -> None:
        """Assert that all required keys are present in dictionary.

        Args:
            data: Dictionary to validate
            required_keys: List of required key names

        Raises:
            AssertionError: If any required keys missing
        """
        # Step 1: Input validation
        if not isinstance(data, dict):
            raise TypeError("data must be a dictionary")
        if not required_keys:
            raise ValueError("required_keys cannot be empty")

        # Step 2: Find missing keys
        missing_keys = [key for key in required_keys if key not in data]

        # Step 3: Assert no missing keys
        assert not missing_keys, f"Missing required keys: {missing_keys}"

    @staticmethod
    def assert_latency_below_threshold(
        latency_ms: float,
        threshold_ms: float,
    ) -> None:
        """Assert that latency is below threshold.

        Args:
            latency_ms: Measured latency in milliseconds
            threshold_ms: Maximum acceptable latency in milliseconds

        Raises:
            AssertionError: If latency exceeds threshold
        """
        # Step 1: Input validation
        if latency_ms < 0:
            raise ValueError("latency_ms must be non-negative")
        if threshold_ms < 0:
            raise ValueError("threshold_ms must be non-negative")

        # Step 2: Assert threshold
        assert latency_ms <= threshold_ms, (
            f"Latency {latency_ms:.1f}ms exceeds threshold {threshold_ms:.1f}ms"
        )

    @staticmethod
    def assert_error_rate_below_threshold(
        results: list[dict[str, Any]],
        threshold: float,
        status_key: str = "status",
        error_value: str = "error",
    ) -> None:
        """Assert that error rate is below threshold.

        Args:
            results: List of result dictionaries
            threshold: Maximum error rate (0.0-1.0)
            status_key: Key in result dict containing status
            error_value: Value indicating error

        Raises:
            AssertionError: If error rate exceeds threshold
        """
        # Step 1: Input validation
        if not results:
            raise ValueError("results list cannot be empty")
        if not 0.0 <= threshold <= 1.0:
            raise ValueError("threshold must be between 0.0 and 1.0")

        # Step 2: Calculate error rate
        errors = sum(1 for r in results if r.get(status_key) == error_value)
        error_rate = errors / len(results)

        # Step 3: Assert threshold
        assert error_rate <= threshold, (
            f"Error rate {error_rate:.2%} exceeds threshold {threshold:.2%} "
            f"({errors}/{len(results)} errors)"
        )


# ============================================================================
# Pytest Fixtures
# ============================================================================


@pytest.fixture
def dataset_loader() -> DatasetLoader:
    """Fixture: Dataset loader utility."""
    return DatasetLoader()


@pytest.fixture
def assertion_helpers() -> AssertionHelpers:
    """Fixture: Assertion helper utility."""
    return AssertionHelpers()


@pytest.fixture
def sample_invoices(dataset_loader: DatasetLoader) -> list[dict[str, Any]]:
    """Fixture: Load 10 sample invoices for testing."""
    return dataset_loader.load_invoices(limit=10)


@pytest.fixture
def sample_transactions(dataset_loader: DatasetLoader) -> list[dict[str, Any]]:
    """Fixture: Load 10 sample transactions for testing."""
    return dataset_loader.load_transactions(limit=10)


@pytest.fixture
def sample_reconciliations(dataset_loader: DatasetLoader) -> list[dict[str, Any]]:
    """Fixture: Load 5 sample reconciliations for testing."""
    return dataset_loader.load_reconciliations(limit=5)


@pytest.fixture
def all_invoices(dataset_loader: DatasetLoader) -> list[dict[str, Any]]:
    """Fixture: Load all 100 invoices for comprehensive testing."""
    return dataset_loader.load_invoices()


@pytest.fixture
def all_transactions(dataset_loader: DatasetLoader) -> list[dict[str, Any]]:
    """Fixture: Load all 100 transactions for comprehensive testing."""
    return dataset_loader.load_transactions()


@pytest.fixture
def all_reconciliations(dataset_loader: DatasetLoader) -> list[dict[str, Any]]:
    """Fixture: Load all 100 reconciliations for comprehensive testing."""
    return dataset_loader.load_reconciliations()
