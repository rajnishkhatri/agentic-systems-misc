"""Output validation schemas using Pydantic for reliable agent outputs.

This module implements FR4.4: Output Validation Schemas with Pydantic.

Features:
- InvoiceExtraction schema with business rule validation
- FraudDetection schema with confidence bounds and conditional requirements
- Custom validators for amount positivity, confidence range, fraud_type requirements
- Type safety and automatic validation error messages

Defensive coding:
- Type hints on all fields
- Custom validators with descriptive error messages
- Strict field requirements with Optional types where appropriate
- extra="forbid" to reject unknown fields (prevent hallucinated fields)
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, field_validator, model_validator


class InvoiceExtraction(BaseModel):
    """Schema for invoice extraction output validation.

    Validates that agent outputs contain all required invoice fields
    with correct types and business rule constraints.

    Attributes:
        invoice_id: Unique invoice identifier (e.g., "INV-2024-001")
        vendor: Vendor name
        amount: Invoice total amount (must be positive)
        date: Invoice date in ISO format (e.g., "2024-01-15")
        line_items: List of line item dictionaries

    Example:
        >>> invoice = InvoiceExtraction(
        ...     invoice_id="INV-2024-001",
        ...     vendor="Acme Corp",
        ...     amount=1234.56,
        ...     date="2024-01-15",
        ...     line_items=[{"description": "Widget", "quantity": 10, "unit_price": 123.456}]
        ... )
        >>> invoice.amount
        1234.56
    """

    invoice_id: str
    vendor: str
    amount: float
    date: str
    line_items: list[dict[str, Any]]

    class Config:
        """Pydantic configuration."""

        extra = "forbid"  # Reject unknown fields (prevents hallucinations)

    @field_validator("amount")
    @classmethod
    def validate_amount_positive(cls, v: float) -> float:
        """Validate that amount is positive.

        Args:
            v: Amount value to validate

        Returns:
            Validated amount

        Raises:
            ValueError: If amount is not positive
        """
        if v <= 0:
            raise ValueError("Amount must be positive")
        return v


class FraudDetection(BaseModel):
    """Schema for fraud detection output validation.

    Validates that fraud detection agents output all required fields
    with correct types and business logic constraints.

    Attributes:
        transaction_id: Unique transaction identifier
        is_fraud: Whether transaction is classified as fraud
        confidence: Confidence score in [0, 1] range
        fraud_type: Type of fraud detected (required when is_fraud=True)
        reasoning: Explanation of fraud determination

    Example:
        >>> fraud = FraudDetection(
        ...     transaction_id="TXN-12345",
        ...     is_fraud=True,
        ...     confidence=0.87,
        ...     fraud_type="stolen_card",
        ...     reasoning="Transaction pattern matches stolen card signatures"
        ... )
        >>> fraud.is_fraud
        True
    """

    transaction_id: str
    is_fraud: bool
    confidence: float
    fraud_type: str | None = None
    reasoning: str

    class Config:
        """Pydantic configuration."""

        extra = "forbid"  # Reject unknown fields

    @field_validator("confidence")
    @classmethod
    def validate_confidence_range(cls, v: float) -> float:
        """Validate that confidence is in [0, 1] range.

        Args:
            v: Confidence value to validate

        Returns:
            Validated confidence

        Raises:
            ValueError: If confidence is not in [0, 1]
        """
        if not 0 <= v <= 1:
            raise ValueError("Confidence must be between 0 and 1")
        return v

    @model_validator(mode="after")
    def validate_fraud_type_required_when_fraud(self) -> FraudDetection:
        """Validate that fraud_type is provided when is_fraud is True.

        Business rule: If fraud is detected, we must specify the fraud type
        for proper handling and routing.

        Returns:
            Validated model

        Raises:
            ValueError: If is_fraud=True but fraud_type is None
        """
        if self.is_fraud and self.fraud_type is None:
            raise ValueError("fraud_type is required when is_fraud is True")
        return self
