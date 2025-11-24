"""Generate reconciliation dataset for Lesson 16.

This script generates 100 reconciliation tasks with account matching challenges.
"""

from __future__ import annotations

import json
import sys
from datetime import datetime
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.data_generation.reconciliation import generate_reconciliation_dataset


def main() -> None:
    """Generate and save reconciliation dataset."""
    # Generate dataset
    print("Generating 100 reconciliation tasks...")
    reconciliations = generate_reconciliation_dataset(count=100, difficulty="mixed", seed=42)

    # Calculate statistics
    challenge_counts = {
        "date_mismatch": sum(1 for r in reconciliations if "date_mismatch" in r["challenge_types"]),
        "amount_rounding": sum(1 for r in reconciliations if "amount_rounding" in r["challenge_types"]),
        "duplicate_entries": sum(1 for r in reconciliations if "duplicate_entries" in r["challenge_types"]),
        "missing_counterparty": sum(1 for r in reconciliations if "missing_counterparty" in r["challenge_types"]),
    }

    status_counts = {
        "perfect_match": sum(1 for r in reconciliations if r["reconciliation_status"] == "perfect_match"),
        "resolvable_with_logic": sum(1 for r in reconciliations if r["reconciliation_status"] == "resolvable_with_logic"),
        "manual_review_required": sum(1 for r in reconciliations if r["reconciliation_status"] == "manual_review_required"),
    }

    # Add metadata
    metadata = {
        "generation_date": datetime.now().isoformat(),
        "count": len(reconciliations),
        "schema_version": "1.0",
        "challenge_distribution": challenge_counts,
        "status_distribution": status_counts,
        "description": "Account reconciliation dataset with 4 challenge types and 3 difficulty levels",
    }

    # Save dataset
    output_path = Path(__file__).parent.parent / "data" / "reconciliation_100.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open("w") as f:
        json.dump({"metadata": metadata, "reconciliations": reconciliations}, f, indent=2)

    print(f"\nDataset saved to: {output_path}")
    print(f"File size: {output_path.stat().st_size / 1024:.2f} KB")
    print("\nChallenge Distribution:")
    for challenge, count in challenge_counts.items():
        print(f"  {challenge}: {count} ({count}%)")
    print("\nStatus Distribution:")
    for status, count in status_counts.items():
        print(f"  {status}: {count} ({count}%)")


if __name__ == "__main__":
    main()
