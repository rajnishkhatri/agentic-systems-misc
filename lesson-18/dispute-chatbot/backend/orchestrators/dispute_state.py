"""Dispute State Enum (FR1.1).

Defines the valid states for the Dispute Resolution State Machine.
"""

from enum import Enum


class DisputeState(str, Enum):
    """Enum representing the phases of the dispute resolution workflow."""

    CLASSIFY = "CLASSIFY"
    GATHER_EVIDENCE = "GATHER_EVIDENCE"
    VALIDATE = "VALIDATE"
    SUBMIT = "SUBMIT"
    MONITOR = "MONITOR"
    ESCALATE = "ESCALATE"

