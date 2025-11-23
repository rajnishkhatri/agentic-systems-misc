"""Financial task suite generation for benchmark evaluation (FR5.1).

Generates benchmark test suites from datasets with:
- Task sampling strategies (random, difficulty-stratified, edge-case-focused)
- Task wrapper structure with metadata
- Filtering by difficulty/challenge type
- Reproducible seed-based generation
- Task statistics and batch support
"""

from __future__ import annotations

import json
import random
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Literal

# ============================================================================
# Task Data Structures
# ============================================================================


@dataclass
class Task:
    """Wrapper for benchmark task with metadata.

    Attributes:
        task_id: Unique task identifier
        task_type: Type of task (invoice, transaction, reconciliation)
        input_data: Original task data from dataset
        gold_label: Expected output for validation
        difficulty: Task difficulty level (easy, medium, hard, None)
        challenge_types: List of challenges present (ocr_error, fraud, date_mismatch, etc.)
    """

    task_id: str
    task_type: Literal["invoice", "transaction", "reconciliation"]
    input_data: dict[str, Any]
    gold_label: Any
    difficulty: str | None = None
    challenge_types: list[str] = field(default_factory=list)


# ============================================================================
# FinancialTaskGenerator Class
# ============================================================================


class FinancialTaskGenerator:
    """Generate benchmark task suites from financial datasets.

    Supports multiple sampling strategies and task filtering for comprehensive
    orchestrator evaluation.
    """

    def __init__(self) -> None:
        """Initialize task generator with empty dataset storage."""
        self.invoices: list[dict[str, Any]] = []
        self.transactions: list[dict[str, Any]] = []
        self.reconciliations: list[dict[str, Any]] = []
        self._data_dir: Path | None = None

    def load_datasets(self, data_dir: Path) -> None:
        """Load all 3 dataset files from data directory.

        Args:
            data_dir: Path to directory containing dataset JSON files

        Raises:
            TypeError: If data_dir is not a Path object
            FileNotFoundError: If dataset files are missing
            ValueError: If dataset files are invalid JSON
        """
        # Step 1: Type checking (defensive)
        if not isinstance(data_dir, Path):
            raise TypeError("data_dir must be a Path object")

        # Step 2: Input validation
        if not data_dir.exists():
            raise FileNotFoundError(f"Data directory not found: {data_dir}")

        # Step 3: Load datasets
        invoice_file = data_dir / "invoices_100.json"
        transaction_file = data_dir / "transactions_100.json"
        reconciliation_file = data_dir / "reconciliation_100.json"

        # Check all files exist
        for file in [invoice_file, transaction_file, reconciliation_file]:
            if not file.exists():
                raise FileNotFoundError(f"Dataset file not found: {file}")

        # Load JSON data
        try:
            with open(invoice_file) as f:
                invoice_data = json.load(f)
                # Handle both list format and dict with metadata format
                self.invoices = invoice_data if isinstance(invoice_data, list) else invoice_data

            with open(transaction_file) as f:
                transaction_data = json.load(f)
                # Extract transactions array if metadata present
                if isinstance(transaction_data, dict) and "transactions" in transaction_data:
                    self.transactions = transaction_data["transactions"]
                else:
                    self.transactions = transaction_data

            with open(reconciliation_file) as f:
                reconciliation_data = json.load(f)
                # Extract reconciliations array if metadata present
                if isinstance(reconciliation_data, dict) and "reconciliations" in reconciliation_data:
                    self.reconciliations = reconciliation_data["reconciliations"]
                else:
                    self.reconciliations = reconciliation_data
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in dataset files: {e}") from e

        # Step 4: Store data directory
        self._data_dir = data_dir

    def generate_task_suite(
        self,
        count: int = 300,
        strategy: Literal["random", "difficulty_stratified", "edge_case_focused"] = "random",
        seed: int = 42,
    ) -> list[Task]:
        """Generate task suite using specified sampling strategy.

        Args:
            count: Total number of tasks to generate (must be positive)
            strategy: Sampling strategy (random, difficulty_stratified, edge_case_focused)
            seed: Random seed for reproducibility

        Returns:
            List of Task objects with metadata

        Raises:
            TypeError: If arguments have wrong types
            ValueError: If count <= 0 or datasets not loaded
        """
        # Step 1: Type checking (defensive)
        if not isinstance(count, int):
            raise TypeError("count must be int")
        if not isinstance(seed, int):
            raise TypeError("seed must be int")
        if strategy not in ["random", "difficulty_stratified", "edge_case_focused"]:
            raise ValueError(f"Invalid strategy: {strategy}")

        # Step 2: Input validation
        if count <= 0:
            raise ValueError("count must be positive")
        if not self.invoices or not self.transactions or not self.reconciliations:
            raise ValueError("Datasets not loaded. Call load_datasets() first.")

        # Step 3: Initialize random with seed
        rng = random.Random(seed)

        # Step 4: Sample tasks based on strategy
        if strategy == "random":
            tasks = self._random_sampling(count, rng)
        elif strategy == "difficulty_stratified":
            tasks = self._difficulty_stratified_sampling(count, rng)
        elif strategy == "edge_case_focused":
            tasks = self._edge_case_focused_sampling(count, rng)
        else:
            tasks = self._random_sampling(count, rng)  # Fallback

        # Step 5: Deduplicate tasks
        tasks = self._deduplicate_tasks(tasks)

        return tasks

    def _random_sampling(self, count: int, rng: random.Random) -> list[Task]:
        """Sample tasks randomly from all datasets.

        Args:
            count: Number of tasks to sample
            rng: Random number generator

        Returns:
            List of Task objects
        """
        # Sample evenly from each dataset type
        tasks_per_type = count // 3
        remainder = count % 3

        tasks: list[Task] = []

        # Sample invoices
        invoice_count = tasks_per_type + (1 if remainder > 0 else 0)
        invoice_samples = rng.choices(self.invoices, k=invoice_count)
        for inv in invoice_samples:
            tasks.append(self._create_task_from_invoice(inv))

        # Sample transactions
        transaction_count = tasks_per_type + (1 if remainder > 1 else 0)
        transaction_samples = rng.choices(self.transactions, k=transaction_count)
        for txn in transaction_samples:
            tasks.append(self._create_task_from_transaction(txn))

        # Sample reconciliations
        reconciliation_samples = rng.choices(self.reconciliations, k=tasks_per_type)
        for rec in reconciliation_samples:
            tasks.append(self._create_task_from_reconciliation(rec))

        return tasks

    def _difficulty_stratified_sampling(self, count: int, rng: random.Random) -> list[Task]:
        """Sample tasks maintaining difficulty distribution.

        Args:
            count: Number of tasks to sample
            rng: Random number generator

        Returns:
            List of Task objects stratified by difficulty
        """
        # Reconciliation has difficulty, others default to medium
        easy_recs = [r for r in self.reconciliations if r.get("difficulty") == "easy"]
        medium_recs = [r for r in self.reconciliations if r.get("difficulty") == "medium"]
        hard_recs = [r for r in self.reconciliations if r.get("difficulty") == "hard"]

        # Target distribution: 20% easy, 50% medium, 30% hard
        tasks_per_type = count // 3
        easy_count = int(tasks_per_type * 0.2)
        medium_count = int(tasks_per_type * 0.5)
        hard_count = tasks_per_type - easy_count - medium_count

        tasks: list[Task] = []

        # Sample reconciliations by difficulty
        easy_samples = rng.choices(easy_recs, k=easy_count) if easy_recs else []
        medium_samples = rng.choices(medium_recs, k=medium_count) if medium_recs else []
        hard_samples = rng.choices(hard_recs, k=hard_count) if hard_recs else []

        for rec in easy_samples + medium_samples + hard_samples:
            tasks.append(self._create_task_from_reconciliation(rec))

        # Sample invoices and transactions (no difficulty stratification)
        invoice_samples = rng.choices(self.invoices, k=tasks_per_type)
        for inv in invoice_samples:
            tasks.append(self._create_task_from_invoice(inv))

        transaction_samples = rng.choices(self.transactions, k=tasks_per_type)
        for txn in transaction_samples:
            tasks.append(self._create_task_from_transaction(txn))

        return tasks

    def _edge_case_focused_sampling(self, count: int, rng: random.Random) -> list[Task]:
        """Sample tasks prioritizing those with challenge flags.

        Args:
            count: Number of tasks to sample
            rng: Random number generator

        Returns:
            List of Task objects prioritizing edge cases
        """
        tasks_per_type = count // 3

        tasks: list[Task] = []

        # Prioritize invoices with challenges (support both 'challenges' and 'challenge_types')
        invoice_challenges = [
            inv for inv in self.invoices if inv.get("challenges") or inv.get("challenge_types")
        ]
        invoice_normal = [
            inv for inv in self.invoices if not inv.get("challenges") and not inv.get("challenge_types")
        ]

        # 70% challenges, 30% normal
        challenge_count = int(tasks_per_type * 0.7)
        normal_count = tasks_per_type - challenge_count

        invoice_samples = (
            rng.choices(invoice_challenges, k=challenge_count) if invoice_challenges else []
        ) + (rng.choices(invoice_normal, k=normal_count) if invoice_normal else [])

        for inv in invoice_samples:
            tasks.append(self._create_task_from_invoice(inv))

        # Prioritize transactions with challenges
        txn_challenges = [txn for txn in self.transactions if txn.get("challenges") or txn.get("challenge_types")]
        txn_normal = [
            txn for txn in self.transactions if not txn.get("challenges") and not txn.get("challenge_types")
        ]

        txn_samples = (rng.choices(txn_challenges, k=challenge_count) if txn_challenges else []) + (
            rng.choices(txn_normal, k=normal_count) if txn_normal else []
        )

        for txn in txn_samples:
            tasks.append(self._create_task_from_transaction(txn))

        # Prioritize reconciliations with challenges
        rec_challenges = [rec for rec in self.reconciliations if rec.get("challenges") or rec.get("challenge_types")]
        rec_normal = [
            rec for rec in self.reconciliations if not rec.get("challenges") and not rec.get("challenge_types")
        ]

        rec_samples = (rng.choices(rec_challenges, k=challenge_count) if rec_challenges else []) + (
            rng.choices(rec_normal, k=normal_count) if rec_normal else []
        )

        for rec in rec_samples:
            tasks.append(self._create_task_from_reconciliation(rec))

        return tasks

    def _create_task_from_invoice(self, invoice: dict[str, Any]) -> Task:
        """Create Task object from invoice data.

        Args:
            invoice: Invoice dictionary from dataset

        Returns:
            Task object with metadata
        """
        return Task(
            task_id=invoice["invoice_id"],
            task_type="invoice",
            input_data=invoice,
            gold_label={
                "vendor": invoice.get("vendor"),
                "amount": invoice.get("amount"),
                "status": invoice.get("status"),
            },
            difficulty=None,  # Invoices don't have difficulty
            challenge_types=invoice.get("challenge_types", invoice.get("challenges", [])),
        )

    def _create_task_from_transaction(self, transaction: dict[str, Any]) -> Task:
        """Create Task object from transaction data.

        Args:
            transaction: Transaction dictionary from dataset

        Returns:
            Task object with metadata
        """
        return Task(
            task_id=transaction["transaction_id"],
            task_type="transaction",
            input_data=transaction,
            gold_label={
                "fraud_label": transaction.get("fraud_label"),
                "fraud_type": transaction.get("fraud_type"),
            },
            difficulty=None,  # Transactions don't have difficulty
            challenge_types=transaction.get("challenge_types", transaction.get("challenges", [])),
        )

    def _create_task_from_reconciliation(self, reconciliation: dict[str, Any]) -> Task:
        """Create Task object from reconciliation data.

        Args:
            reconciliation: Reconciliation dictionary from dataset

        Returns:
            Task object with metadata
        """
        return Task(
            task_id=reconciliation["reconciliation_id"],
            task_type="reconciliation",
            input_data=reconciliation,
            gold_label={
                "expected_matches": reconciliation.get("expected_matches"),
                "status": reconciliation.get("reconciliation_status"),
            },
            difficulty=reconciliation.get("difficulty"),
            challenge_types=reconciliation.get("challenge_types", reconciliation.get("challenges", [])),
        )

    def _deduplicate_tasks(self, tasks: list[Task]) -> list[Task]:
        """Remove duplicate tasks by task_id.

        Args:
            tasks: List of Task objects potentially with duplicates

        Returns:
            List of Task objects with duplicates removed
        """
        seen_ids: set[str] = set()
        unique_tasks: list[Task] = []

        for task in tasks:
            if task.task_id not in seen_ids:
                seen_ids.add(task.task_id)
                unique_tasks.append(task)

        return unique_tasks

    def filter_tasks(
        self,
        tasks: list[Task],
        difficulty: str | None = None,
        challenge_type: str | None = None,
    ) -> list[Task]:
        """Filter tasks by difficulty and/or challenge type.

        Args:
            tasks: List of Task objects to filter
            difficulty: Filter by difficulty level (easy, medium, hard, None)
            challenge_type: Filter by specific challenge type (ocr_error, fraud, etc.)

        Returns:
            Filtered list of Task objects

        Raises:
            TypeError: If tasks is not a list
        """
        # Step 1: Type checking (defensive)
        if not isinstance(tasks, list):
            raise TypeError("tasks must be a list")

        # Step 2: Filter by difficulty if specified
        filtered = tasks
        if difficulty is not None:
            filtered = [t for t in filtered if t.difficulty == difficulty]

        # Step 3: Filter by challenge type if specified
        if challenge_type is not None:
            filtered = [t for t in filtered if challenge_type in t.challenge_types]

        return filtered

    def get_task_statistics(self, tasks: list[Task]) -> dict[str, Any]:
        """Calculate statistics for task suite.

        Args:
            tasks: List of Task objects

        Returns:
            Dictionary with challenge distribution, difficulty histogram, gold label balance

        Raises:
            TypeError: If tasks is not a list
        """
        # Step 1: Type checking (defensive)
        if not isinstance(tasks, list):
            raise TypeError("tasks must be a list")

        # Step 2: Calculate task type distribution
        task_types = {"invoice": 0, "transaction": 0, "reconciliation": 0}
        for task in tasks:
            task_types[task.task_type] += 1

        # Step 3: Calculate challenge distribution
        challenge_counts: dict[str, int] = {}
        for task in tasks:
            for challenge in task.challenge_types:
                challenge_counts[challenge] = challenge_counts.get(challenge, 0) + 1

        # Step 4: Calculate difficulty histogram
        difficulty_hist = {"easy": 0, "medium": 0, "hard": 0, "none": 0}
        for task in tasks:
            if task.difficulty:
                difficulty_hist[task.difficulty] += 1
            else:
                difficulty_hist["none"] += 1

        # Step 5: Calculate gold label balance (for transactions)
        fraud_count = 0
        legitimate_count = 0
        for task in tasks:
            if task.task_type == "transaction":
                if task.gold_label.get("fraud_label"):
                    fraud_count += 1
                else:
                    legitimate_count += 1

        # Step 6: Return statistics
        return {
            "total_tasks": len(tasks),
            "task_type_distribution": task_types,
            "challenge_distribution": challenge_counts,
            "difficulty_histogram": difficulty_hist,
            "fraud_balance": {
                "fraud": fraud_count,
                "legitimate": legitimate_count,
                "fraud_rate": fraud_count / (fraud_count + legitimate_count) if (fraud_count + legitimate_count) > 0 else 0.0,
            },
        }


# ============================================================================
# Public API
# ============================================================================

__all__ = ["Task", "FinancialTaskGenerator"]
