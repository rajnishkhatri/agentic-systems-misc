"""Base Evaluator - Abstract Base Class for all gap evaluators.

This module provides the foundation for the evaluation framework using
the ABC pattern from patterns/abstract-base-class.md.

Key Features:
    - Defensive initialization with type checking and validation
    - Abstract methods for evaluate() and explain() (required)
    - Shared validation helpers for subclasses
    - Pydantic models for structured results

Design Decisions:
    1. All evaluators must implement explain() for explainability (Gap 8)
    2. Results include confidence scores for statistical testing (Gap 7)
    3. Recommendations field guides remediation actions

Example:
    >>> class MyEvaluator(BaseEvaluator):
    ...     def evaluate(self, data):
    ...         return EvaluationResult(evaluator_name="my_eval", ...)
    ...     def explain(self, result):
    ...         return f"Evaluated with score {result.score}"
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import UTC, datetime
from typing import Any

from pydantic import BaseModel, Field


class EvaluationResult(BaseModel):
    """Structured result from any evaluator.

    Attributes:
        evaluator_name: Name of the evaluator that produced this result
        is_valid: Whether the evaluation passed overall
        score: Numeric score between 0.0 and 1.0
        confidence: Statistical confidence in the score (0.0-1.0)
        samples_evaluated: Number of samples used in evaluation
        reasoning: Human-readable explanation of the result
        recommendations: List of actionable recommendations
        metadata: Additional evaluator-specific data
        timestamp: When evaluation was performed
    """

    evaluator_name: str
    is_valid: bool
    score: float = Field(ge=0.0, le=1.0)
    confidence: float = Field(ge=0.0, le=1.0)
    samples_evaluated: int = Field(ge=0)
    reasoning: str
    recommendations: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))

    class Config:
        extra = "forbid"


class BaseEvaluator(ABC):
    """Abstract base class for all gap evaluators.

    Applies the ABC pattern from patterns/abstract-base-class.md with
    defensive initialization per TDD principles.

    Subclasses must implement:
        - evaluate(): Run the evaluation logic
        - explain(): Provide human-readable explanation

    Provides shared functionality:
        - Input validation
        - Configuration management
        - Helper methods for common operations

    Attributes:
        name: Unique name for this evaluator
        min_samples: Minimum samples required for statistical validity
        confidence_threshold: Minimum confidence to consider result valid

    Example:
        >>> class MyEvaluator(BaseEvaluator):
        ...     def evaluate(self, data):
        ...         # Implementation
        ...         pass
        ...     def explain(self, result):
        ...         return f"Score: {result.score}"
    """

    def __init__(self, config: dict[str, Any]) -> None:
        """Initialize evaluator with defensive validation.

        Args:
            config: Configuration dictionary with required keys:
                - name: Evaluator name (str)
                - min_samples: Minimum samples for validity (int, >= 1)
                - confidence_threshold: Minimum confidence (float, 0.0-1.0)

        Raises:
            TypeError: If config is not a dictionary
            ValueError: If required keys are missing or values are invalid
        """
        # Step 1: Type checking (defensive)
        if not isinstance(config, dict):
            raise TypeError("config must be a dictionary")

        # Step 2: Input validation - required keys
        required_keys = ["name", "min_samples", "confidence_threshold"]
        missing = [k for k in required_keys if k not in config]
        if missing:
            raise ValueError(f"Missing required config keys: {missing}")

        # Step 3: Type validation for each field
        if not isinstance(config["name"], str):
            raise TypeError("config['name'] must be a string")
        if not isinstance(config["min_samples"], int):
            raise TypeError("config['min_samples'] must be an integer")
        if not isinstance(config["confidence_threshold"], (int, float)):
            raise TypeError("config['confidence_threshold'] must be a number")

        # Step 4: Value validation
        if not config["name"].strip():
            raise ValueError("config['name'] cannot be empty")
        if config["min_samples"] < 1:
            raise ValueError("config['min_samples'] must be at least 1")
        if not (0.0 <= config["confidence_threshold"] <= 1.0):
            raise ValueError("config['confidence_threshold'] must be between 0.0 and 1.0")

        # Step 5: Initialize instance attributes
        self.name = config["name"]
        self.min_samples = config["min_samples"]
        self.confidence_threshold = config["confidence_threshold"]
        self._config = config

    @abstractmethod
    def evaluate(self, data: dict[str, Any]) -> EvaluationResult:
        """Run evaluation on provided data.

        Subclasses must implement this method to perform their specific
        evaluation logic.

        Args:
            data: Dictionary containing data to evaluate. Structure depends
                on the specific evaluator implementation.

        Returns:
            EvaluationResult with score, confidence, and recommendations

        Raises:
            TypeError: If data is not a dictionary
            ValueError: If required data fields are missing
        """
        pass

    @abstractmethod
    def explain(self, result: EvaluationResult) -> str:
        """Provide human-readable explanation of evaluation result.

        Required for explainability (Gap 8). Should follow First Principles
        Teaching pattern: start with the problem, use analogies, concrete
        before abstract.

        Args:
            result: EvaluationResult to explain

        Returns:
            Human-readable explanation string (markdown format recommended)

        Raises:
            TypeError: If result is not an EvaluationResult
        """
        pass

    def validate_input(self, data: dict[str, Any], required_fields: list[str]) -> None:
        """Shared validation helper for subclasses.

        Args:
            data: Data dictionary to validate
            required_fields: List of required field names

        Raises:
            TypeError: If data is not a dictionary
            ValueError: If required fields are missing
        """
        if not isinstance(data, dict):
            raise TypeError("data must be a dictionary")

        missing = [f for f in required_fields if f not in data]
        if missing:
            raise ValueError(f"Missing required fields: {missing}")

    def has_sufficient_samples(self, sample_count: int) -> bool:
        """Check if sample count meets minimum requirement.

        Args:
            sample_count: Number of samples available

        Returns:
            True if sample_count >= min_samples
        """
        return sample_count >= self.min_samples

    def meets_confidence_threshold(self, confidence: float) -> bool:
        """Check if confidence meets threshold.

        Args:
            confidence: Confidence score (0.0-1.0)

        Returns:
            True if confidence >= confidence_threshold
        """
        return confidence >= self.confidence_threshold

    def create_result(
        self,
        *,
        is_valid: bool,
        score: float,
        confidence: float,
        samples_evaluated: int,
        reasoning: str,
        recommendations: list[str] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> EvaluationResult:
        """Factory method to create EvaluationResult with evaluator name.

        Args:
            is_valid: Whether evaluation passed
            score: Numeric score (0.0-1.0)
            confidence: Statistical confidence (0.0-1.0)
            samples_evaluated: Number of samples used
            reasoning: Human-readable explanation
            recommendations: Optional list of recommendations
            metadata: Optional additional data

        Returns:
            EvaluationResult with this evaluator's name
        """
        return EvaluationResult(
            evaluator_name=self.name,
            is_valid=is_valid,
            score=score,
            confidence=confidence,
            samples_evaluated=samples_evaluated,
            reasoning=reasoning,
            recommendations=recommendations or [],
            metadata=metadata or {},
        )

    def __repr__(self) -> str:
        """Return string representation."""
        return (
            f"{self.__class__.__name__}(name={self.name!r}, "
            f"min_samples={self.min_samples}, "
            f"confidence_threshold={self.confidence_threshold})"
        )
