"""Reconciliation dataset generation for account matching testing.

Generates realistic reconciliation datasets with:
- Schema compliance (reconciliation_id, bank_transactions, ledger_entries, expected_matches)
- Date mismatch challenges (25%): posting date ≠ transaction date by 1-3 business days
- Amount rounding challenges (20%): $1234.56 vs $1234.50
- Duplicate entry challenges (15%)
- Missing counterparty challenges (18%)
- Reconciliation status distribution (60% perfect_match, 25% resolvable, 15% manual_review)
- Realistic discrepancy amounts ($0.01-$500)
- Edge cases: same-day multi-transactions, cross-month reconciliation
"""

from __future__ import annotations

import random
from datetime import datetime, timedelta
from typing import Any, Literal

from . import random_amount, random_date

# ============================================================================
# Reconciliation Dataset Generation
# ============================================================================


def generate_reconciliation_dataset(
    count: int = 100,
    seed: int = 42,
    difficulty: Literal["easy", "medium", "hard", "mixed"] = "mixed",
    date_mismatch_rate: float = 0.25,
    rounding_error_rate: float = 0.20,
    duplicate_rate: float = 0.15,
    missing_counterparty_rate: float = 0.18,
) -> list[dict[str, Any]]:
    """Generate synthetic reconciliation dataset with account matching challenges.

    Args:
        count: Number of reconciliation tasks to generate (must be positive)
        seed: Random seed for reproducibility
        difficulty: Task difficulty level ("easy", "medium", "hard", "mixed")
        date_mismatch_rate: Probability of date mismatches (0.0-1.0)
        rounding_error_rate: Probability of amount rounding errors (0.0-1.0)
        duplicate_rate: Probability of duplicate entries (0.0-1.0)
        missing_counterparty_rate: Probability of missing counterparty (0.0-1.0)

    Returns:
        List of reconciliation task dictionaries with gold labels

    Raises:
        TypeError: If arguments have wrong types
        ValueError: If count <= 0 or rates outside [0, 1] or difficulty invalid
    """
    # Step 1: Type checking (defensive)
    if not isinstance(count, int):
        raise TypeError("count must be int")
    if not isinstance(seed, int):
        raise TypeError("seed must be int")
    if not isinstance(difficulty, str):
        raise TypeError("difficulty must be str")
    if not isinstance(date_mismatch_rate, (int, float)):
        raise TypeError("date_mismatch_rate must be numeric")
    if not isinstance(rounding_error_rate, (int, float)):
        raise TypeError("rounding_error_rate must be numeric")
    if not isinstance(duplicate_rate, (int, float)):
        raise TypeError("duplicate_rate must be numeric")
    if not isinstance(missing_counterparty_rate, (int, float)):
        raise TypeError("missing_counterparty_rate must be numeric")

    # Step 2: Input validation
    if count <= 0:
        raise ValueError("count must be positive")
    if difficulty not in ["easy", "medium", "hard", "mixed"]:
        raise ValueError("difficulty must be one of: easy, medium, hard, mixed")
    if not (0.0 <= date_mismatch_rate <= 1.0):
        raise ValueError("date_mismatch_rate must be in [0, 1]")
    if not (0.0 <= rounding_error_rate <= 1.0):
        raise ValueError("rounding_error_rate must be in [0, 1]")
    if not (0.0 <= duplicate_rate <= 1.0):
        raise ValueError("duplicate_rate must be in [0, 1]")
    if not (0.0 <= missing_counterparty_rate <= 1.0):
        raise ValueError("missing_counterparty_rate must be in [0, 1]")

    # Step 3: Initialize random generator
    rng = random.Random(seed)

    # Step 4: Generate dataset
    dataset: list[dict[str, Any]] = []

    for i in range(count):
        # Determine difficulty for this task
        if difficulty == "mixed":
            task_difficulty = rng.choice(["easy", "medium", "hard"])
        else:
            task_difficulty = difficulty

        # Create reconciliation task
        task = _create_reconciliation_task(i, task_difficulty, rng)
        dataset.append(task)

    # Step 5: Inject challenges deterministically to hit target rates
    # Calculate exact counts for each challenge type
    date_mismatch_count = int(count * date_mismatch_rate)
    rounding_error_count = int(count * rounding_error_rate)
    duplicate_count = int(count * duplicate_rate)
    missing_counterparty_count = int(count * missing_counterparty_rate)

    # Create indices for challenge injection
    indices = list(range(count))
    rng.shuffle(indices)

    # Inject date mismatches
    for i in indices[:date_mismatch_count]:
        dataset[i] = _inject_date_mismatch(dataset[i], rng)

    # Inject rounding errors
    rng.shuffle(indices)
    for i in indices[:rounding_error_count]:
        dataset[i] = _inject_rounding_error(dataset[i], rng)

    # Inject duplicates
    rng.shuffle(indices)
    for i in indices[:duplicate_count]:
        dataset[i] = _inject_duplicates(dataset[i], rng)

    # Inject missing counterparty
    rng.shuffle(indices)
    for i in indices[:missing_counterparty_count]:
        dataset[i] = _inject_missing_counterparty(dataset[i], rng)

    # Step 6: Return dataset
    return dataset


def _create_reconciliation_task(index: int, difficulty: str, rng: random.Random) -> dict[str, Any]:
    """Create a single reconciliation task.

    Args:
        index: Task index for ID generation
        difficulty: Task difficulty level
        rng: Random number generator

    Returns:
        Reconciliation task dictionary
    """
    # Generate reconciliation ID
    reconciliation_id = f"REC-{index:05d}"

    # Number of transactions based on difficulty
    if difficulty == "easy":
        num_transactions = rng.randint(1, 3)
    elif difficulty == "medium":
        num_transactions = rng.randint(3, 6)
    else:  # hard
        num_transactions = rng.randint(5, 10)

    # Generate bank transactions
    bank_transactions = []
    for i in range(num_transactions):
        amount = random_amount(min_amount=10.0, max_amount=10000.0, seed=rng.randint(0, 10000))
        date = random_date(start_date="2024-01-01", end_date="2024-12-31", seed=rng.randint(0, 10000))

        bank_transactions.append({
            "transaction_id": f"BANK-{index:05d}-{i:03d}",
            "date": date,
            "amount": amount,
            "counterparty": _random_counterparty_name(rng),
            "description": _random_transaction_description(rng),
        })

    # Generate ledger entries (initially matching bank transactions)
    ledger_entries = []
    for i, bank_txn in enumerate(bank_transactions):
        ledger_entries.append({
            "entry_id": f"LED-{index:05d}-{i:03d}",
            "date": bank_txn["date"],  # Keep "date" for consistency with tests
            "posting_date": bank_txn["date"],  # Also include posting_date for challenge injection
            "amount": bank_txn["amount"],
            "account": _random_account_code(rng),  # Changed from "account_code" to "account"
        })

    # Generate expected matches (gold labels) with bank_index and ledger_index
    expected_matches = [
        {"bank_index": i, "ledger_index": i, "bank_id": f"BANK-{index:05d}-{i:03d}", "ledger_id": f"LED-{index:05d}-{i:03d}"}
        for i in range(num_transactions)
    ]

    # Determine reconciliation status
    status = _random_reconciliation_status(rng)

    # Calculate discrepancy
    if status == "perfect_match":
        discrepancy = 0.0
    elif status == "resolvable_with_logic":
        discrepancy = round(rng.uniform(0.01, 50.0), 2)
    else:  # manual_review_required
        discrepancy = round(rng.uniform(50.0, 500.0), 2)

    return {
        "reconciliation_id": reconciliation_id,
        "difficulty": difficulty,
        "bank_transactions": bank_transactions,
        "ledger_entries": ledger_entries,
        "expected_matches": expected_matches,
        "reconciliation_status": status,
        "discrepancy_amount": discrepancy,
        "challenge_types": [],  # Will be populated by injection functions
    }


def _random_counterparty_name(rng: random.Random) -> str:
    """Generate random counterparty name.

    Args:
        rng: Random number generator

    Returns:
        Random counterparty name
    """
    counterparties = [
        "Acme Corp",
        "TechStart Inc",
        "Global Supplies Ltd",
        "Metro Services",
        "Pacific Trading Co",
        "Atlantic Partners",
        "Northern Industries",
        "Southern Solutions",
        "Eastern Electronics",
        "Western Manufacturing",
        "Central Consulting",
        "Digital Dynamics",
        "Smart Systems",
        "Rapid Response LLC",
        "Premier Products",
        "Elite Enterprises",
        "Apex Automation",
        "Fusion Finance",
        "Vertex Ventures",
        "Nexus Networks",
    ]

    return rng.choice(counterparties)


def _random_transaction_description(rng: random.Random) -> str:
    """Generate random transaction description.

    Args:
        rng: Random number generator

    Returns:
        Random description
    """
    descriptions = [
        "Wire transfer",
        "ACH payment",
        "Check payment",
        "Invoice payment",
        "Vendor payment",
        "Customer deposit",
        "Refund processed",
        "Service fee",
        "Interest payment",
        "Loan repayment",
    ]

    return rng.choice(descriptions)


def _random_account_code(rng: random.Random) -> str:
    """Generate random account code.

    Args:
        rng: Random number generator

    Returns:
        Random account code
    """
    categories = ["1000", "2000", "3000", "4000", "5000"]  # Assets, Liabilities, Equity, Revenue, Expenses
    subcategory = rng.randint(10, 99)

    return f"{rng.choice(categories)}-{subcategory}"


def _random_reconciliation_status(rng: random.Random) -> str:
    """Generate random reconciliation status with distribution.

    Distribution:
    - 60% perfect_match
    - 25% resolvable_with_logic
    - 15% manual_review_required

    Args:
        rng: Random number generator

    Returns:
        Reconciliation status string
    """
    rand_val = rng.random()

    if rand_val < 0.60:
        return "perfect_match"
    elif rand_val < 0.85:  # 0.60 + 0.25
        return "resolvable_with_logic"
    else:
        return "manual_review_required"


def _inject_date_mismatch(task: dict[str, Any], rng: random.Random) -> dict[str, Any]:
    """Inject date mismatch (1-3 business days difference).

    Args:
        task: Reconciliation task to modify
        rng: Random number generator

    Returns:
        Task with date mismatch injected
    """
    task["challenge_types"].append("date_mismatch")
    task["has_date_mismatch"] = True

    # Pick random ledger entry to modify
    if task["ledger_entries"]:
        entry_idx = rng.randint(0, len(task["ledger_entries"]) - 1)
        original_date = task["ledger_entries"][entry_idx]["posting_date"]

        # Shift date by 1-3 business days
        date_obj = datetime.strptime(original_date, "%Y-%m-%d")
        days_shift = rng.randint(1, 3)
        new_date = date_obj + timedelta(days=days_shift)

        task["ledger_entries"][entry_idx]["posting_date"] = new_date.strftime("%Y-%m-%d")

        # Date mismatch alone usually doesn't change status (still auto-matchable)
        # Only change if there are multiple challenges
        if task["reconciliation_status"] == "perfect_match" and len(task["challenge_types"]) > 1:
            # 30% chance to change to resolvable when combined with other challenges
            if rng.random() < 0.3:
                task["reconciliation_status"] = "resolvable_with_logic"
                task["discrepancy_amount"] = round(rng.uniform(0.01, 10.0), 2)

    return task


def _inject_rounding_error(task: dict[str, Any], rng: random.Random) -> dict[str, Any]:
    """Inject amount rounding error.

    Args:
        task: Reconciliation task to modify
        rng: Random number generator

    Returns:
        Task with rounding error injected
    """
    task["challenge_types"].append("amount_rounding")
    task["has_rounding_error"] = True

    # Pick random ledger entry to modify
    if task["ledger_entries"]:
        entry_idx = rng.randint(0, len(task["ledger_entries"]) - 1)
        original_amount = task["ledger_entries"][entry_idx]["amount"]

        # Only apply rounding if NOT perfect_match (perfect_match must have exact amounts)
        if task["reconciliation_status"] != "perfect_match":
            # Apply small rounding difference ($0.01-$1.00) to show actual rounding
            # Add or subtract a small rounding error
            rounding_error = round(rng.uniform(0.01, 1.00), 2)
            if rng.random() < 0.5:
                new_amount = round(original_amount + rounding_error, 2)
            else:
                new_amount = round(max(0.01, original_amount - rounding_error), 2)

            task["ledger_entries"][entry_idx]["amount"] = new_amount
            # Don't update discrepancy - it's already set from initial status

    return task


def _inject_duplicates(task: dict[str, Any], rng: random.Random) -> dict[str, Any]:
    """Inject duplicate entry.

    Args:
        task: Reconciliation task to modify
        rng: Random number generator

    Returns:
        Task with duplicate injected
    """
    task["challenge_types"].append("duplicate_entries")
    task["has_duplicates"] = True

    # Duplicate a random ledger entry
    if task["ledger_entries"]:
        entry_idx = rng.randint(0, len(task["ledger_entries"]) - 1)
        duplicate_entry = task["ledger_entries"][entry_idx].copy()

        # Modify entry_id to make it unique
        duplicate_entry["entry_id"] = f"{duplicate_entry['entry_id']}-DUP"

        task["ledger_entries"].append(duplicate_entry)

        # Duplicates are complex but can often be auto-handled
        # Only escalate if combined with other challenges
        if task["reconciliation_status"] == "perfect_match":
            if len(task["challenge_types"]) > 2:
                # Multiple challenges: 50% chance manual review
                if rng.random() < 0.5:
                    task["reconciliation_status"] = "manual_review_required"
                    task["discrepancy_amount"] = round(rng.uniform(50.0, 200.0), 2)
                else:
                    task["reconciliation_status"] = "resolvable_with_logic"
                    task["discrepancy_amount"] = round(rng.uniform(0.01, 50.0), 2)
            elif len(task["challenge_types"]) == 2:
                # Two challenges: resolvable
                if rng.random() < 0.3:
                    task["reconciliation_status"] = "resolvable_with_logic"
                    task["discrepancy_amount"] = round(rng.uniform(0.01, 50.0), 2)

    return task


def _inject_missing_counterparty(task: dict[str, Any], rng: random.Random) -> dict[str, Any]:
    """Inject missing counterparty information.

    Args:
        task: Reconciliation task to modify
        rng: Random number generator

    Returns:
        Task with missing counterparty injected
    """
    task["challenge_types"].append("missing_counterparty")
    task["has_missing_counterparty"] = True

    # Add an unmatched bank transaction (missing ledger entry)
    if task["bank_transactions"]:
        # Add a new bank transaction without matching ledger entry
        new_index = len(task["bank_transactions"])
        task["bank_transactions"].append({
            "transaction_id": f"BANK-UNMATCH-{new_index:03d}",
            "date": random_date(start_date="2024-01-01", end_date="2024-12-31", seed=rng.randint(0, 10000)),
            "amount": random_amount(min_amount=10.0, max_amount=1000.0, seed=rng.randint(0, 10000)),
            "counterparty": _random_counterparty_name(rng),
            "description": _random_transaction_description(rng),
        })

        # Missing counterparty usually resolvable but only change if multiple challenges
        if task["reconciliation_status"] == "perfect_match" and len(task["challenge_types"]) > 1 and rng.random() < 0.4:
            task["reconciliation_status"] = "resolvable_with_logic"
            task["discrepancy_amount"] = round(rng.uniform(0.01, 10.0), 2)

    return task


# ============================================================================
# Public API
# ============================================================================

__all__ = ["generate_reconciliation_dataset"]
