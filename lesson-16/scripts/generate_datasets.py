"""Script to generate all financial datasets for Lesson 16.

Generates:
- invoices_100.json (100 invoice processing tasks)
- transactions_100.json (100 fraud detection tasks)
- reconciliation_100.json (100 account matching tasks)
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

# Add lesson-16 to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.data_generation.invoices import generate_invoice_dataset


def main() -> None:
    """Generate all datasets and save to data/ directory."""
    # Setup paths
    data_dir = Path(__file__).parent.parent / "data"
    data_dir.mkdir(exist_ok=True)

    print("=" * 80)
    print("Lesson 16: Generating Financial Datasets")
    print("=" * 80)

    # Generate invoice dataset
    print("\n[1/3] Generating invoices_100.json...")
    invoices = generate_invoice_dataset(
        count=100, seed=42, ocr_error_rate=0.15, missing_field_rate=0.10, duplicate_rate=0.08
    )

    # Save invoice dataset
    invoice_file = data_dir / "invoices_100.json"
    with open(invoice_file, "w") as f:
        json.dump(invoices, f, indent=2)

    print(f"✓ Generated {len(invoices)} invoices")
    print(f"  - File: {invoice_file}")
    print(f"  - OCR errors: {sum(1 for inv in invoices if inv.get('has_ocr_error', False))}")
    print(f"  - Missing fields: {sum(1 for inv in invoices if inv.get('has_missing_fields', False))}")
    print(f"  - Duplicates: {sum(1 for inv in invoices if inv.get('is_duplicate', False))}")

    # TODO: Generate transaction dataset (Task 6.3)
    print("\n[2/3] Generating transactions_100.json...")
    print("  ⏳ Not implemented yet (Task 6.3)")

    # TODO: Generate reconciliation dataset (Task 6.4)
    print("\n[3/3] Generating reconciliation_100.json...")
    print("  ⏳ Not implemented yet (Task 6.4)")

    print("\n" + "=" * 80)
    print("Dataset generation complete!")
    print("=" * 80)


if __name__ == "__main__":
    main()
