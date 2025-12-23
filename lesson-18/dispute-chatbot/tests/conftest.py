"""Pytest fixtures for dispute chatbot tests.

Provides common fixtures for:
- Mock LLM responses
- Sample dispute data
- Evidence packages
- Judge configurations
"""

import json
from pathlib import Path
from typing import Any

import pytest

# --- Schema Data Fixtures ---

CURRENT_DIR = Path(__file__).parent
# Adjusted path: tests/conftest.py -> tests -> dispute-chatbot -> lesson-18 -> dispute-schema
# parents[0] = tests
# parents[1] = dispute-chatbot
# parents[2] = lesson-18
# parents[3] = recipe-chatbot (root)
# So if we want lesson-18/dispute-schema, it's parents[2].parent / "dispute-schema" ?
# No, parents[2] is lesson-18. So parents[2] / "dispute-schema".
SCHEMA_DIR = CURRENT_DIR.parents[1].parent / "dispute-schema"
# Let's verify:
# CURRENT_DIR = .../lesson-18/dispute-chatbot/tests
# parents[0] = .../lesson-18/dispute-chatbot
# parents[1] = .../lesson-18
# So SCHEMA_DIR = .../lesson-18/dispute-schema. This is correct.
EXAMPLES_FILE = SCHEMA_DIR / "examples.json"

@pytest.fixture(scope="session")
def example_data():
    """Load the examples.json file."""
    if not EXAMPLES_FILE.exists():
        # Fallback for different execution contexts
        alt_path = Path("lesson-18/dispute-schema/examples.json")
        if alt_path.exists():
            with open(alt_path, "r") as f:
                data = json.load(f)
            return data["examples"]
        pytest.fail(f"Test data file not found at: {EXAMPLES_FILE} or {alt_path}")

    with open(EXAMPLES_FILE, "r") as f:
        data = json.load(f)
    return data["examples"]

@pytest.fixture
def fraud_dispute_fixture(example_data):
    """Fixture for a standard fraud dispute needing response."""
    return example_data["fraud_dispute_needs_response"]

@pytest.fixture
def pnr_dispute_fixture(example_data):
    """Fixture for a product not received dispute."""
    return example_data["product_not_received"]

@pytest.fixture
def ce3_dispute_fixture(example_data):
    """Fixture for a fraud dispute qualified for CE 3.0."""
    return example_data["fraud_dispute_ce3_qualified"]

@pytest.fixture
def subscription_dispute_fixture(example_data):
    """Fixture for a subscription canceled dispute."""
    return example_data["subscription_canceled_dispute"]

@pytest.fixture
def duplicate_dispute_fixture(example_data):
    """Fixture for a duplicate charge dispute."""
    return example_data["duplicate_charge_dispute"]

@pytest.fixture
def mastercard_dispute_fixture(example_data):
    """Fixture for a Mastercard fraud dispute."""
    return example_data["mastercard_fraud_dispute"]

@pytest.fixture
def won_dispute_fixture(example_data):
    """Fixture for a won dispute."""
    return example_data["dispute_won"]

@pytest.fixture
def paypal_dispute_fixture(example_data):
    """Fixture for a PayPal dispute."""
    return example_data["paypal_dispute"]

# --- Common Fixtures ---

@pytest.fixture
def sample_dispute() -> dict[str, Any]:
    """Sample dispute data for testing."""
    return {
        "dispute_id": "D-2024-001",
        "transaction_id": "TXN-123456",
        "amount": 150.00,
        "currency": "USD",
        "merchant_name": "Test Merchant",
        "cardholder_claim": "I never received the merchandise",
        "transaction_date": "2024-01-15",
        "reason_code": "13.1",
        "reason_description": "Merchandise/Services Not Received",
    }


@pytest.fixture
def sample_evidence() -> dict[str, Any]:
    """Sample evidence package for testing."""
    return {
        "evidence_id": "E-2024-001",
        "dispute_id": "D-2024-001",
        "evidence_type": "shipping",
        "documents": [
            {
                "type": "tracking_number",
                "value": "1Z999AA10123456784",
                "source": "merchant_provided",
            },
            {
                "type": "delivery_confirmation",
                "value": "Delivered to front door on 2024-01-17",
                "source": "carrier_api",
            },
        ],
        "confidence_score": 0.85,
    }


@pytest.fixture
def sample_judge_config() -> dict[str, Any]:
    """Sample judge configuration for testing."""
    return {
        "evidence_quality": {
            "threshold": 0.8,
            "blocking": True,
            "model": "gpt-4o",
        },
        "fabrication_detection": {
            "threshold": 0.95,
            "blocking": True,
            "model": "gpt-4o",
        },
        "dispute_validity": {
            "threshold": 0.7,
            "blocking": False,
            "model": "gpt-4o-mini",
        },
    }


@pytest.fixture
def mock_llm_response() -> dict[str, Any]:
    """Mock LLM response for testing without API calls."""
    return {
        "classification": {
            "reason_code": "13.1",
            "confidence": 0.92,
            "evidence_requirements": [
                "shipping_tracking",
                "delivery_confirmation",
                "signed_receipt",
            ],
        }
    }
