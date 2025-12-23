import json
from pathlib import Path

import pytest

# Get the absolute path to the schema examples file
# Assuming the file structure:
# root/
#   lesson-18/
#     dispute-chatbot/
#       tests/
#         fixtures/
#           dispute_fixtures.py
#     dispute-schema/
#       examples.json

CURRENT_DIR = Path(__file__).parent
SCHEMA_DIR = CURRENT_DIR.parents[3] / "lesson-18" / "dispute-schema"
EXAMPLES_FILE = SCHEMA_DIR / "examples.json"

@pytest.fixture(scope="session")
def example_data():
    """Load the examples.json file."""
    if not EXAMPLES_FILE.exists():
        pytest.fail(f"Test data file not found at: {EXAMPLES_FILE}")

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

