"""Script to generate transaction dataset for fraud detection testing.

Generates data/transactions_100.json with:
- 100 transactions
- 10% fraud rate (10 fraud, 90 legitimate)
- Fraud types: 40% stolen_card, 35% account_takeover, 25% synthetic_fraud
- 20% ambiguous patterns
- High-value transactions >$10K for voting ensemble use case
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.data_generation.transactions import generate_transaction_dataset


def main() -> None:
    """Generate and save transaction dataset."""
    # Step 1: Generate dataset
    print("Generating transaction dataset (100 transactions, 10% fraud rate)...")
    transactions = generate_transaction_dataset(
        count=100,
        fraud_rate=0.1,
        seed=42,
    )

    # Step 2: Calculate statistics
    fraud_count = sum(1 for txn in transactions if txn["fraud_label"] is True)
    fraud_txns = [txn for txn in transactions if txn["fraud_label"] is True]
    fraud_types = [txn["fraud_type"] for txn in fraud_txns]

    stolen_card = fraud_types.count("stolen_card")
    account_takeover = fraud_types.count("account_takeover")
    synthetic_fraud = fraud_types.count("synthetic_fraud")

    ambiguous_count = sum(1 for txn in transactions if 0.4 <= txn["gold_label_confidence"] <= 0.6)
    high_value_count = sum(1 for txn in transactions if txn["amount"] > 10000)
    unique_merchants = len({txn["merchant"] for txn in transactions})

    # Step 3: Create output with metadata
    output = {
        "metadata": {
            "total_count": len(transactions),
            "fraud_count": fraud_count,
            "fraud_rate": fraud_count / len(transactions),
            "fraud_type_distribution": {
                "stolen_card": stolen_card,
                "account_takeover": account_takeover,
                "synthetic_fraud": synthetic_fraud,
            },
            "ambiguous_count": ambiguous_count,
            "high_value_count": high_value_count,
            "unique_merchants": unique_merchants,
            "seed": 42,
        },
        "transactions": transactions,
    }

    # Step 4: Save to file
    output_path = Path(__file__).parent.parent / "data" / "transactions_100.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w") as f:
        json.dump(output, f, indent=2)

    # Step 5: Print summary
    print(f"\nDataset saved to: {output_path}")
    print(f"File size: {output_path.stat().st_size / 1024:.2f} KB")
    print("\nDataset Statistics:")
    print(f"  Total transactions: {len(transactions)}")
    print(f"  Fraud count: {fraud_count} ({fraud_count / len(transactions) * 100:.1f}%)")
    print("  Fraud type distribution:")
    print(f"    - stolen_card: {stolen_card}")
    print(f"    - account_takeover: {account_takeover}")
    print(f"    - synthetic_fraud: {synthetic_fraud}")
    print(f"  Ambiguous patterns: {ambiguous_count} ({ambiguous_count / len(transactions) * 100:.1f}%)")
    print(f"  High-value (>$10K): {high_value_count} ({high_value_count / len(transactions) * 100:.1f}%)")
    print(f"  Unique merchants: {unique_merchants}")


if __name__ == "__main__":
    main()
