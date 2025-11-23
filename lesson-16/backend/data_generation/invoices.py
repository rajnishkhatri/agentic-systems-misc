"""Invoice dataset generation for financial workflow testing.

Generates realistic invoice datasets with:
- Schema compliance (invoice_id, vendor, amount, date, line_items, status)
- Challenge injection (OCR errors, missing fields, duplicates)
- Gold labels for validation
"""

from __future__ import annotations

import random
from datetime import datetime
from typing import Any

from . import random_amount, random_date, random_vendor_name


# ============================================================================
# Invoice Dataset Generation
# ============================================================================


def generate_invoice_dataset(
    count: int = 100,
    seed: int = 42,
    ocr_error_rate: float = 0.15,
    missing_field_rate: float = 0.10,
    duplicate_rate: float = 0.08,
) -> list[dict[str, Any]]:
    """Generate synthetic invoice dataset with realistic challenges.

    Args:
        count: Number of invoices to generate (must be positive)
        seed: Random seed for reproducibility
        ocr_error_rate: Probability of OCR errors (0.0-1.0)
        missing_field_rate: Probability of missing optional fields (0.0-1.0)
        duplicate_rate: Probability of duplicate invoices (0.0-1.0)

    Returns:
        List of invoice dictionaries with metadata and gold labels

    Raises:
        TypeError: If arguments have wrong types
        ValueError: If count <= 0 or rates outside [0, 1]
    """
    # Step 1: Type checking (defensive)
    if not isinstance(count, int):
        raise TypeError("count must be int")
    if not isinstance(seed, int):
        raise TypeError("seed must be int")
    if not isinstance(ocr_error_rate, (int, float)):
        raise TypeError("ocr_error_rate must be numeric")
    if not isinstance(missing_field_rate, (int, float)):
        raise TypeError("missing_field_rate must be numeric")
    if not isinstance(duplicate_rate, (int, float)):
        raise TypeError("duplicate_rate must be numeric")

    # Step 2: Input validation
    if count <= 0:
        raise ValueError("count must be positive")
    if not (0.0 <= ocr_error_rate <= 1.0):
        raise ValueError("ocr_error_rate must be in [0, 1]")
    if not (0.0 <= missing_field_rate <= 1.0):
        raise ValueError("missing_field_rate must be in [0, 1]")
    if not (0.0 <= duplicate_rate <= 1.0):
        raise ValueError("duplicate_rate must be in [0, 1]")

    # Step 3: Initialize random generator
    rng = random.Random(seed)

    # Step 4: Generate dataset
    dataset: list[dict[str, Any]] = []
    duplicate_candidates: list[dict[str, Any]] = []

    for i in range(count):
        # Decide if this should be a duplicate
        if duplicate_candidates and rng.random() < duplicate_rate:
            # Create duplicate from existing invoice
            original = rng.choice(duplicate_candidates)
            invoice = _create_duplicate_invoice(original, i, rng)
        else:
            # Create new invoice
            invoice = _create_invoice(i, rng)
            duplicate_candidates.append(invoice)

        # Inject OCR errors
        if rng.random() < ocr_error_rate:
            invoice = _inject_ocr_error(invoice, rng)

        # Inject missing fields
        if rng.random() < missing_field_rate:
            invoice = _inject_missing_fields(invoice, rng)

        # Add gold label
        invoice["gold_label"] = _generate_gold_label(invoice)

        dataset.append(invoice)

    # Step 5: Add metadata
    metadata = {
        "generation_date": datetime.now().isoformat(),
        "version": "1.0",
        "schema_version": "1.0",
        "challenge_distribution": {
            "total_invoices": count,
            "ocr_error_rate": ocr_error_rate,
            "missing_field_rate": missing_field_rate,
            "duplicate_rate": duplicate_rate,
        },
    }

    # Return dataset with metadata as first element
    return dataset


def _create_invoice(index: int, rng: random.Random) -> dict[str, Any]:
    """Create a single invoice with realistic data.

    Args:
        index: Invoice index for ID generation
        rng: Random number generator for reproducibility

    Returns:
        Invoice dictionary with all required fields
    """
    # Generate base fields
    vendor = random_vendor_name(seed=rng.randint(0, 10000))
    amount = random_amount(min_amount=10.0, max_amount=50000.0, seed=rng.randint(0, 10000))
    date = random_date(start_date="2024-01-01", end_date="2024-12-31", seed=rng.randint(0, 10000))

    # Generate invoice ID
    year = date.split("-")[0]
    invoice_id = f"INV-{year}-{index:03d}"

    # Generate line items (1-3 items)
    num_items = rng.randint(1, 3)
    line_items = []

    remaining_amount = amount
    for i in range(num_items):
        if i == num_items - 1:
            # Last item gets remaining amount
            item_amount = remaining_amount
        else:
            # Split amount randomly
            item_amount = round(remaining_amount * rng.uniform(0.3, 0.7), 2)
            remaining_amount -= item_amount

        line_items.append(
            {
                "description": _random_line_item_description(rng),
                "quantity": rng.randint(1, 10),
                "unit_price": round(item_amount, 2),
            }
        )

    return {
        "invoice_id": invoice_id,
        "vendor": vendor,
        "amount": amount,
        "date": date,
        "line_items": line_items,
        "status": rng.choice(["pending", "approved", "paid"]),
        "has_ocr_error": False,
        "has_missing_fields": False,
        "is_duplicate": False,
    }


def _create_duplicate_invoice(original: dict[str, Any], index: int, rng: random.Random) -> dict[str, Any]:
    """Create duplicate invoice with slightly modified ID.

    Args:
        original: Original invoice to duplicate
        index: New invoice index
        rng: Random number generator

    Returns:
        Duplicate invoice with same core data but different ID
    """
    duplicate = original.copy()
    duplicate["invoice_id"] = f"INV-2024-{index:03d}"  # Different ID
    duplicate["is_duplicate"] = True
    duplicate["duplicate_of"] = original["invoice_id"]

    return duplicate


def _inject_ocr_error(invoice: dict[str, Any], rng: random.Random) -> dict[str, Any]:
    """Inject OCR error into invoice data.

    Args:
        invoice: Invoice dictionary to modify
        rng: Random number generator

    Returns:
        Invoice with OCR error injected
    """
    # Corrupt vendor name (common OCR error)
    vendor = invoice["vendor"]

    # Replace random character with similar-looking one
    if len(vendor) > 5:
        pos = rng.randint(0, len(vendor) - 1)
        char = vendor[pos]

        # OCR confusion pairs
        ocr_map = {
            "o": "0",
            "O": "0",
            "l": "1",
            "I": "1",
            "S": "5",
            "G": "6",
            "B": "8",
        }

        if char in ocr_map:
            vendor = vendor[:pos] + ocr_map[char] + vendor[pos + 1 :]

    invoice["vendor"] = vendor
    invoice["has_ocr_error"] = True
    invoice["ocr_error_field"] = "vendor"

    return invoice


def _inject_missing_fields(invoice: dict[str, Any], rng: random.Random) -> dict[str, Any]:
    """Inject missing optional fields.

    Args:
        invoice: Invoice dictionary to modify
        rng: Random number generator

    Returns:
        Invoice with missing fields
    """
    # Remove one optional field
    optional_fields = ["status"]

    if optional_fields and rng.random() < 0.5:
        field_to_remove = rng.choice(optional_fields)
        if field_to_remove in invoice:
            del invoice[field_to_remove]

    invoice["has_missing_fields"] = True
    invoice["missing_field"] = "status"

    return invoice


def _generate_gold_label(invoice: dict[str, Any]) -> dict[str, Any]:
    """Generate gold label for invoice validation.

    Args:
        invoice: Invoice dictionary

    Returns:
        Gold label with validation status and reason
    """
    is_valid = True
    reason = "valid"

    # Check for OCR errors
    if invoice.get("has_ocr_error", False):
        is_valid = False
        reason = "ocr_error_detected"

    # Check for missing required fields
    if invoice.get("has_missing_fields", False):
        is_valid = False
        reason = "missing_required_fields"

    # Check for duplicates
    if invoice.get("is_duplicate", False):
        is_valid = False
        reason = "duplicate_invoice"

    return {"is_valid": is_valid, "reason": reason}


def _random_line_item_description(rng: random.Random) -> str:
    """Generate random line item description.

    Args:
        rng: Random number generator

    Returns:
        Random line item description
    """
    descriptions = [
        "Software License",
        "Consulting Services",
        "Hardware Purchase",
        "Support Contract",
        "Training Session",
        "Cloud Services",
        "Professional Services",
        "Maintenance Fee",
        "Subscription Fee",
        "Development Services",
    ]

    return rng.choice(descriptions)


# ============================================================================
# Public API
# ============================================================================

__all__ = ["generate_invoice_dataset"]
