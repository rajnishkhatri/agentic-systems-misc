"""State Transition Rules (FR1.2).

Defines the allowed transitions between dispute states.
"""

from backend.orchestrators.dispute_state import DisputeState

# Define allowed transitions (Adjacency List)
DISPUTE_TRANSITIONS: dict[str, list[str]] = {
    # CLASSIFY can transition to GATHER_EVIDENCE
    DisputeState.CLASSIFY: [DisputeState.GATHER_EVIDENCE],

    # GATHER_EVIDENCE can transition to VALIDATE
    DisputeState.GATHER_EVIDENCE: [DisputeState.VALIDATE],

    # VALIDATE can transition to SUBMIT (pass) or ESCALATE (fail)
    DisputeState.VALIDATE: [DisputeState.SUBMIT, DisputeState.ESCALATE],

    # SUBMIT can transition to MONITOR (success) or ESCALATE (failure)
    DisputeState.SUBMIT: [DisputeState.MONITOR, DisputeState.ESCALATE],

    # MONITOR is terminal
    DisputeState.MONITOR: [],

    # ESCALATE is terminal
    DisputeState.ESCALATE: []
}

