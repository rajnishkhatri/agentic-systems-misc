"""Agent Explainability Components.

This module provides five core explainability components:

1. BlackBoxRecorder - Aviation-style flight recorder for agent workflows
   - Persisted task plans, collaborator lists, parameter substitution logs
   - Complete execution traces for post-incident analysis

2. AgentFacts - Verifiable agent metadata (arXiv:2506.13794)
   - Owner, capabilities, policies metadata
   - Cryptographic signature verification for audits

3. GuardRails - Declarative validation with transparency (Guardrails AI-inspired)
   - Schema validators with rich traces
   - Prompt structure documentation

4. PhaseLogger - Multi-phase workflow logging (AgentRxiv-inspired)
   - Phase-based logging (Planning → Execution → Validation → Reporting)
   - Decision tracking with reasoning and alternatives

5. PolicyBridge - Connect AgentFacts policies to GuardRails enforcement
   - Converts declarative policies to runtime constraints
   - Bridges verification (AgentFacts) and enforcement (GuardRails)

Integration with Lesson-16:
    - Extends AuditLogger patterns for structured logging
    - Reuses checkpoint persistence mechanisms
    - Leverages Pydantic validation schemas
    - Uses Result[T,E] type for error isolation
"""

# Lazy imports to avoid circular dependencies
# Users should import directly from submodules for now
__all__ = [
    # Black Box Recorder
    "BlackBoxRecorder",
    "TaskPlan",
    "PlanStep",
    "ExecutionTrace",
    "TraceEvent",
    # AgentFacts
    "AgentFacts",
    "AgentFactsRegistry",
    "Capability",
    "Policy",
    # GuardRails
    "GuardRail",
    "PromptGuardRail",
    "GuardRailValidator",
    "Constraint",
    "ValidationEntry",
    "ValidationResult",
    "FailAction",
    "BuiltInValidators",
    # Phase Logger
    "PhaseLogger",
    "WorkflowPhase",
    "Decision",
    "PhaseOutcome",
    "PhaseSummary",
]


def __getattr__(name: str):
    """Lazy import mechanism."""
    if name in (
        "BlackBoxRecorder",
        "TaskPlan",
        "PlanStep",
        "ExecutionTrace",
        "TraceEvent",
        "AgentInfo",
        "EventType",
    ):
        from . import black_box

        return getattr(black_box, name)
    elif name in ("AgentFacts", "AgentFactsRegistry", "Capability", "Policy", "AuditEntry"):
        from . import agent_facts

        return getattr(agent_facts, name)
    elif name in (
        "GuardRail",
        "PromptGuardRail",
        "GuardRailValidator",
        "Constraint",
        "ValidationEntry",
        "ValidationResult",
        "FailAction",
        "BuiltInValidators",
        "Severity",
    ):
        from . import guardrails

        return getattr(guardrails, name)
    elif name in (
        "PhaseLogger",
        "WorkflowPhase",
        "Decision",
        "PhaseOutcome",
        "PhaseSummary",
        "Artifact",
    ):
        from . import phase_logger

        return getattr(phase_logger, name)
    elif name in (
        "policy_to_guardrail",
        "enforce_agent_policies",
        "get_enforceable_policies",
        "get_external_enforcement_policies",
    ):
        from . import policy_bridge

        return getattr(policy_bridge, name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

__all__ = [
    # Black Box Recorder
    "BlackBoxRecorder",
    "TaskPlan",
    "PlanStep",
    "ExecutionTrace",
    "TraceEvent",
    # AgentFacts
    "AgentFacts",
    "AgentFactsRegistry",
    "Capability",
    "Policy",
    # GuardRails
    "GuardRail",
    "PromptGuardRail",
    "GuardRailValidator",
    "Constraint",
    "ValidationEntry",
    "ValidationResult",
    "FailAction",
    "BuiltInValidators",
    # Phase Logger
    "PhaseLogger",
    "WorkflowPhase",
    "Decision",
    "PhaseOutcome",
    "PhaseSummary",
    # Policy Bridge
    "policy_to_guardrail",
    "enforce_agent_policies",
    "get_enforceable_policies",
    "get_external_enforcement_policies",
]

