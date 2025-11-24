"""Transaction dataset generation for fraud detection testing.

Generates realistic transaction datasets with:
- Schema compliance (transaction_id, merchant, amount, timestamp, user_behavior, fraud_label)
- Fraud imbalance (10% fraud / 90% legitimate)
- Fraud type distribution (40% stolen_card, 35% account_takeover, 25% synthetic_fraud)
- Ambiguous pattern injection
- High-value transaction filtering
- Gold label confidence scores
"""

from __future__ import annotations

import random
from typing import Any

from . import random_amount, random_date

# ============================================================================
# Transaction Dataset Generation
# ============================================================================


def generate_transaction_dataset(
    count: int = 100,
    seed: int = 42,
    fraud_rate: float = 0.1,
    ambiguous_rate: float = 0.20,
) -> list[dict[str, Any]]:
    """Generate synthetic transaction dataset with fraud detection challenges.

    Args:
        count: Number of transactions to generate (must be positive)
        seed: Random seed for reproducibility
        fraud_rate: Probability of fraudulent transactions (0.0-1.0)
        ambiguous_rate: Probability of ambiguous patterns (0.0-1.0)

    Returns:
        List of transaction dictionaries with fraud labels and confidence scores

    Raises:
        TypeError: If arguments have wrong types
        ValueError: If count <= 0 or rates outside [0, 1]
    """
    # Step 1: Type checking (defensive)
    if not isinstance(count, int):
        raise TypeError("count must be int")
    if not isinstance(seed, int):
        raise TypeError("seed must be int")
    if not isinstance(fraud_rate, int | float):
        raise TypeError("fraud_rate must be numeric")
    if not isinstance(ambiguous_rate, int | float):
        raise TypeError("ambiguous_rate must be numeric")

    # Step 2: Input validation
    if count <= 0:
        raise ValueError("count must be positive")
    if not (0.0 <= fraud_rate <= 1.0):
        raise ValueError("fraud_rate must be in range [0, 1]")
    if not (0.0 <= ambiguous_rate <= 1.0):
        raise ValueError("ambiguous_rate must be in range [0, 1]")

    # Step 3: Initialize random generator
    rng = random.Random(seed)

    # Step 4: Generate dataset with exact fraud rate
    # Calculate exact number of fraud transactions
    fraud_count = int(count * fraud_rate)
    legitimate_count = count - fraud_count

    # Create list of fraud labels (True = fraud, False = legitimate)
    fraud_labels = [True] * fraud_count + [False] * legitimate_count

    # Shuffle to randomize order
    rng.shuffle(fraud_labels)

    dataset: list[dict[str, Any]] = []

    for i, is_fraud in enumerate(fraud_labels):
        # Create transaction
        transaction = _create_transaction(i, is_fraud, rng)

        # Inject ambiguous patterns
        if rng.random() < ambiguous_rate:
            transaction = _inject_ambiguous_pattern(transaction, rng)

        dataset.append(transaction)

    # Step 5: Return dataset
    return dataset


def _create_transaction(index: int, is_fraud: bool, rng: random.Random) -> dict[str, Any]:
    """Create a single transaction with realistic data.

    Args:
        index: Transaction index for ID generation
        is_fraud: Whether this is a fraudulent transaction
        rng: Random number generator for reproducibility

    Returns:
        Transaction dictionary with all required fields
    """
    # Generate transaction ID (5-digit format)
    transaction_id = f"TXN-{index:05d}"

    # Generate merchant
    merchant = _random_merchant_name(rng)

    # Generate amount (log-normal distribution for long tail)
    # Use exponential for realistic long tail: most low, few very high
    if rng.random() < 0.85:  # 85% of transactions are low-value
        amount = random_amount(min_amount=1.0, max_amount=1000.0, seed=rng.randint(0, 10000))
    else:  # 15% are high-value (long tail) - ensures ≥5 out of 100 are >$10K
        amount = random_amount(min_amount=1000.0, max_amount=100000.0, seed=rng.randint(0, 10000))

    # Generate timestamp (2024 date with time)
    date_str = random_date(start_date="2024-01-01", end_date="2024-12-31", seed=rng.randint(0, 10000))
    # Add time component
    hour = rng.randint(0, 23)
    minute = rng.randint(0, 59)
    second = rng.randint(0, 59)
    timestamp = f"{date_str}T{hour:02d}:{minute:02d}:{second:02d}Z"

    # Generate user_id
    user_id = f"user_{rng.randint(1000, 9999)}"

    # Generate user_behavior features
    user_behavior = {
        "transaction_count_24h": rng.randint(1, 20),
        "avg_transaction_amount": round(rng.uniform(10.0, 500.0), 2),
        "account_age_days": rng.randint(30, 3650),
    }

    # Generate fraud type if fraudulent
    fraud_type = None
    if is_fraud:
        fraud_type = _random_fraud_type(rng)

    # Generate confidence score (gold label confidence)
    # High confidence for clear cases, lower for ambiguous
    if is_fraud:
        # Fraud cases: 0.7-1.0 confidence
        gold_label_confidence = rng.uniform(0.7, 1.0)
    else:
        # Legitimate cases: 0.8-1.0 confidence
        gold_label_confidence = rng.uniform(0.8, 1.0)

    return {
        "transaction_id": transaction_id,
        "merchant": merchant,
        "amount": amount,
        "timestamp": timestamp,
        "user_id": user_id,
        "user_behavior": user_behavior,
        "fraud_label": is_fraud,
        "fraud_type": fraud_type,
        "gold_label_confidence": gold_label_confidence,
    }


def _random_merchant_name(rng: random.Random) -> str:
    """Generate random merchant name.

    Args:
        rng: Random number generator

    Returns:
        Random merchant name
    """
    merchants = [
        "Amazon",
        "Walmart",
        "Target",
        "Best Buy",
        "Home Depot",
        "Costco",
        "Apple Store",
        "CVS Pharmacy",
        "Walgreens",
        "Kroger",
        "Safeway",
        "Whole Foods",
        "Starbucks",
        "McDonald's",
        "Subway",
        "Shell Gas",
        "Chevron",
        "BP Gas",
        "Uber",
        "Lyft",
        "Netflix",
        "Spotify",
        "Hulu",
        "Disney+",
        "HBO Max",
        "Delta Airlines",
        "United Airlines",
        "American Airlines",
        "Marriott Hotels",
        "Hilton Hotels",
        "Airbnb",
        "Expedia",
        "Booking.com",
        "eBay",
        "Etsy",
        "Shopify",
        "PayPal",
        "Venmo",
        "Square",
        "Stripe",
        "Adobe",
        "Microsoft",
        "Google Cloud",
        "AWS",
        "Zoom",
        "Slack",
        "Salesforce",
        "Oracle",
        "IBM",
        "HP",
    ]

    return rng.choice(merchants)


def _random_fraud_type(rng: random.Random) -> str:
    """Generate random fraud type with distribution.

    Distribution:
    - 40% stolen_card
    - 35% account_takeover
    - 25% synthetic_fraud

    Args:
        rng: Random number generator

    Returns:
        Fraud type string
    """
    rand_val = rng.random()

    if rand_val < 0.40:
        return "stolen_card"
    elif rand_val < 0.75:  # 0.40 + 0.35
        return "account_takeover"
    else:
        return "synthetic_fraud"


def _inject_ambiguous_pattern(transaction: dict[str, Any], rng: random.Random) -> dict[str, Any]:
    """Inject ambiguous pattern into transaction.

    Args:
        transaction: Transaction dictionary to modify
        rng: Random number generator

    Returns:
        Transaction with ambiguous pattern injected (confidence 0.4-0.6 for fraud, 0.5-0.6 for non-fraud)
    """
    # Mark as ambiguous
    transaction["is_ambiguous"] = True

    # Lower confidence score to ambiguous range
    # Non-fraud must have confidence >= 0.5 per test requirements
    if transaction["fraud_label"]:
        # Fraud: 0.4-0.6 range
        transaction["gold_label_confidence"] = rng.uniform(0.4, 0.6)
    else:
        # Non-fraud: 0.5-0.6 range (maintain >= 0.5 requirement)
        transaction["gold_label_confidence"] = rng.uniform(0.5, 0.6)

    return transaction


# ============================================================================
# Public API
# ============================================================================

__all__ = ["generate_transaction_dataset"]
