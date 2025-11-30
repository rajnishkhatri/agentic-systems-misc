"""Synthetic data generators for Lesson 17 explainability framework.

This module provides base classes and utilities for generating synthetic
datasets used in tutorial notebooks and case studies.

Pattern follows lesson-16/backend/data_generation/ with:
- Deterministic seeding for reproducibility
- Gold labels for validation testing
- Pydantic schema compliance
"""

from __future__ import annotations

import json
import random
from abc import ABC, abstractmethod
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any


class BaseGenerator(ABC):
    """Abstract base class for synthetic data generators.

    All generators use deterministic seeding for reproducibility.

    Attributes:
        seed: Random seed for reproducible generation
        _random: Random instance with seed applied
    """

    def __init__(self, seed: int = 42):
        """Initialize generator with seed.

        Args:
            seed: Random seed for reproducibility (default: 42)
        """
        self.seed = seed
        self._random = random.Random(seed)

    @abstractmethod
    def generate(self, count: int) -> list[dict[str, Any]]:
        """Generate synthetic data records.

        Args:
            count: Number of records to generate

        Returns:
            List of generated records as dictionaries
        """
        ...

    def save(self, data: list[dict[str, Any]], path: Path) -> None:
        """Save generated data to JSON file.

        Args:
            data: List of records to save
            path: Output file path
        """
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w") as f:
            json.dump(data, f, indent=2, default=str)

    def random_choice(self, choices: list[Any]) -> Any:
        """Thread-safe random choice using instance random."""
        return self._random.choice(choices)

    def random_int(self, a: int, b: int) -> int:
        """Thread-safe random integer using instance random."""
        return self._random.randint(a, b)

    def random_float(self, a: float, b: float) -> float:
        """Thread-safe random float using instance random."""
        return self._random.uniform(a, b)

    def random_sample(self, population: list[Any], k: int) -> list[Any]:
        """Thread-safe random sample using instance random."""
        return self._random.sample(population, k)

    def random_datetime(
        self,
        start: datetime | None = None,
        end: datetime | None = None,
    ) -> datetime:
        """Generate random datetime within range.

        Args:
            start: Start of range (default: 30 days ago)
            end: End of range (default: now)

        Returns:
            Random datetime within range
        """
        if end is None:
            end = datetime.now(UTC)
        if start is None:
            start = end - timedelta(days=30)

        delta = end - start
        random_seconds = self._random.randint(0, int(delta.total_seconds()))
        return start + timedelta(seconds=random_seconds)


# Common data pools for realistic synthetic generation

FIRST_NAMES = [
    "James", "Mary", "John", "Patricia", "Robert", "Jennifer", "Michael",
    "Linda", "William", "Elizabeth", "David", "Barbara", "Richard", "Susan",
    "Joseph", "Jessica", "Thomas", "Sarah", "Charles", "Karen", "Daniel",
    "Emily", "Matthew", "Ashley", "Anthony", "Amanda", "Mark", "Melissa",
]

LAST_NAMES = [
    "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller",
    "Davis", "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez",
    "Wilson", "Anderson", "Thomas", "Taylor", "Moore", "Jackson", "Martin",
    "Lee", "Perez", "Thompson", "White", "Harris", "Sanchez", "Clark", "Lewis",
]

COMPANY_NAMES = [
    "Acme Corporation", "TechNova Solutions", "Global Dynamics", "Apex Industries",
    "Quantum Systems", "Nexus Technologies", "Pinnacle Enterprises", "Synergy Labs",
    "Horizon Consulting", "Catalyst Partners", "Vertex Analytics", "Fusion Innovations",
    "Spectrum Health", "Atlas Financial", "Meridian Services", "Vanguard Solutions",
]

MEDICAL_CONDITIONS = [
    "Type 2 Diabetes", "Hypertension", "Asthma", "Chronic Kidney Disease",
    "Heart Failure", "COPD", "Arthritis", "Depression", "Anxiety", "Migraine",
    "Hypothyroidism", "Hyperthyroidism", "Anemia", "Osteoporosis", "GERD",
]

MEDICATIONS = [
    "Metformin 500mg", "Lisinopril 10mg", "Atorvastatin 20mg", "Amlodipine 5mg",
    "Metoprolol 25mg", "Omeprazole 20mg", "Losartan 50mg", "Gabapentin 300mg",
    "Sertraline 50mg", "Levothyroxine 50mcg", "Prednisone 10mg", "Albuterol",
]

US_STATES = [
    "CA", "NY", "TX", "FL", "IL", "PA", "OH", "GA", "NC", "MI",
    "NJ", "VA", "WA", "AZ", "MA", "TN", "IN", "MO", "MD", "WI",
]

EMAIL_DOMAINS = [
    "gmail.com", "yahoo.com", "outlook.com", "hotmail.com", "company.com",
    "work.org", "mail.net", "example.com", "test.org", "demo.net",
]


def generate_ssn(rng: random.Random) -> str:
    """Generate fake SSN pattern."""
    area = rng.randint(100, 999)
    group = rng.randint(10, 99)
    serial = rng.randint(1000, 9999)
    return f"{area}-{group}-{serial}"


def generate_credit_card(rng: random.Random) -> str:
    """Generate fake credit card pattern."""
    groups = [rng.randint(1000, 9999) for _ in range(4)]
    return "-".join(str(g) for g in groups)


def generate_phone(rng: random.Random) -> str:
    """Generate fake phone number."""
    area = rng.randint(200, 999)
    exchange = rng.randint(200, 999)
    number = rng.randint(1000, 9999)
    return f"+1-{area}-{exchange}-{number}"


def generate_email(rng: random.Random, first_name: str, last_name: str) -> str:
    """Generate fake email address."""
    domain = rng.choice(EMAIL_DOMAINS)
    separator = rng.choice([".", "_", ""])
    return f"{first_name.lower()}{separator}{last_name.lower()}@{domain}"


def generate_medical_record_number(rng: random.Random) -> str:
    """Generate fake medical record number."""
    number = rng.randint(10000000, 99999999)
    return f"MRN-{number}"


def generate_passport_number(rng: random.Random) -> str:
    """Generate fake passport number."""
    number = rng.randint(10000000, 99999999)
    return f"P{number}"


def generate_drivers_license(rng: random.Random) -> str:
    """Generate fake driver's license number."""
    state = rng.choice(US_STATES)
    letter = rng.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
    number = rng.randint(1000000, 9999999)
    return f"DL-{state}-{letter}{number}"

