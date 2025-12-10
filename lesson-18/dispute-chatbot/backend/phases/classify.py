"""CLASSIFY Phase Handler (FR1.3).

Identifies the dispute reason code, network, and deadline using LLM classification.
"""

from __future__ import annotations

import datetime
from typing import Any

from pydantic import BaseModel, Field

from utils.llm_service import get_default_service


class ClassificationResult(BaseModel):
    """Structured output for dispute classification."""
    
    reason_code: str = Field(description="Visa reason code (e.g., '10.4', '13.1')")
    network: str = Field(description="Payment network (e.g., 'visa')")
    is_fraud: bool = Field(description="Whether this is a fraud-related dispute")
    confidence: float = Field(description="Confidence score between 0.0 and 1.0")
    reasoning: str = Field(description="Explanation for the classification")


async def classify_dispute(task: dict[str, Any]) -> dict[str, Any]:
    """Execute the CLASSIFY phase.

    Args:
        task: Task dictionary containing 'dispute_id' and optionally 'description' or 'files'

    Returns:
        Dictionary with classification results:
        {
            "reason_code": "10.4",
            "network": "visa",
            "deadline": "YYYY-MM-DD",
            "classification_confidence": 0.95
        }
    
    Raises:
        TypeError: If task is not a dictionary.
    """
    # Step 1: Type checking
    if not isinstance(task, dict):
        raise TypeError("task must be a dictionary")

    # Step 2: Input validation
    # dispute_id and description are technically optional for the handler (it defaults)
    # but let's ensure we at least handle the extraction safely.
    dispute_id = task.get("dispute_id", "UNKNOWN")
    description = task.get("description", "")
    
    # Step 3: Edge case handling
    # (Handled by defaults above)
    
    # Step 4: Main logic
    service = get_default_service()
    
    prompt = f"""
    You are a Dispute Resolution Specialist for Visa transactions.
    Classify the following dispute based on the description.
    
    Dispute ID: {dispute_id}
    Description: {description}
    
    Determine the Visa Reason Code (e.g., 10.4 for Fraud/Auth, 13.1 for Merchandise Not Received).
    Also identify the network (Visa).
    """
    
    # Use routing model for cost efficiency as per PRD
    try:
        result = await service.complete_structured(
            messages=[{"role": "user", "content": prompt}],
            response_model=ClassificationResult,
            model=service.routing_model
        )
        
        # Calculate deadline (mock: 14 days from now)
        # In production this would be based on dispute_date from VROL
        deadline = (datetime.datetime.now() + datetime.timedelta(days=14)).strftime("%Y-%m-%d")
        
        # Step 5: Return
        return {
            "reason_code": result.reason_code,
            "network": result.network.lower(),
            "deadline": deadline,
            "classification_confidence": result.confidence,
            "classification_reasoning": result.reasoning
        }
        
    except Exception as e:
        # Fallback or re-raise
        # For prototype, return a default if LLM fails (or re-raise to trigger retry)
        raise RuntimeError(f"Classification failed: {e}")
