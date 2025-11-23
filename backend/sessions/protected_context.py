"""Protected context identification logic.

This module identifies which conversation events should be protected during
context compression (e.g., initial objectives, constraints, auth checkpoints).
"""


def identify_protected_context(event: dict) -> dict:
    """Identify if a conversation event should be protected during compression.

    Args:
        event: Conversation event dictionary with keys:
            - turn (int): Turn number (0-indexed)
            - role (str): Speaker role (user, assistant, system)
            - content (str): Event content
            - event_type (str): Event type (initial_objective, constraint,
                               acknowledgment, auth_checkpoint, etc.)

    Returns:
        Dictionary with:
            - is_protected (bool): Whether event should be protected
            - reason (str): Human-readable explanation

    Raises:
        TypeError: If event is not a dict
        ValueError: If event is missing required fields
    """
    # Step 1: Type checking (defensive)
    if not isinstance(event, dict):
        raise TypeError("event must be a dict")

    # Step 2: Input validation (defensive)
    required_fields = ["turn", "role", "content", "event_type"]
    missing_fields = [field for field in required_fields if field not in event]
    if missing_fields:
        raise ValueError(f"event missing required fields: {missing_fields}")

    # Step 3: Extract event properties
    turn = event["turn"]
    event_type = event["event_type"]

    # Step 4: Main logic - Identify protected events
    protected_types = {
        "initial_objective": "Initial objective must be preserved throughout conversation",
        "constraint": "User constraint must be respected in all responses",
        "auth_checkpoint": "Authentication/security checkpoint cannot be compressed",
    }

    if event_type in protected_types:
        return {"is_protected": True, "reason": protected_types[event_type]}

    # Turn 0 events are always protected (initial context)
    if turn == 0:
        return {
            "is_protected": True,
            "reason": "Initial objective (turn 0) establishes conversation context",
        }

    # Non-protected event types
    if event_type in ["acknowledgment", "clarification", "casual"]:
        return {
            "is_protected": False,
            "reason": "Not critical to conversation context (casual/acknowledgment)",
        }

    # Step 5: Default to non-protected for unknown event types
    return {
        "is_protected": False,
        "reason": f"Event type '{event_type}' not identified as critical",
    }
