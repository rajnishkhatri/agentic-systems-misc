"""GATHER_EVIDENCE Phase Handler (FR3).

Delegates evidence collection to hierarchical specialist agents.
"""

from typing import Any


async def gather_evidence(task: dict[str, Any]) -> dict[str, Any]:
    """Execute the GATHER_EVIDENCE phase.
    
    Args:
        task: Task dictionary containing 'reason_code' from CLASSIFY phase
        
    Returns:
        Dictionary with gathered evidence

    Raises:
        TypeError: If task is not a dictionary.
        ValueError: If 'reason_code' is missing.
    """
    # Step 1: Type checking
    if not isinstance(task, dict):
        raise TypeError("task must be a dictionary")

    # Step 2: Input validation
    if "reason_code" not in task:
        raise ValueError("task must contain 'reason_code'")

    # Step 3: Edge case handling
    # (None specific for now beyond missing key)

    # Step 4: Main logic
    # Stub implementation - will delegate to HierarchicalEvidenceGatherer later
    # For now, return mock evidence
    
    # Step 5: Return
    return {
        "evidence_gathered": True,
        "transaction_history": [],
        "shipping_proof": {},
        "customer_profile": {}
    }
