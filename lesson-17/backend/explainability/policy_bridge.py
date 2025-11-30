"""Policy Bridge - Connect AgentFacts policies to GuardRails enforcement.

This module bridges the gap between policy declaration (AgentFacts) and
policy enforcement (GuardRails), converting declarative policies into
runtime-enforceable constraints.

Key Concepts:
- AgentFacts declares WHAT policies should govern an agent
- GuardRails enforces WHETHER output complies with those policies
- This bridge converts between the two systems

Example:
    >>> from backend.explainability.policy_bridge import enforce_agent_policies
    >>> results = enforce_agent_policies(
    ...     agent_id="diagnosis-generator-v1",
    ...     registry=registry,
    ...     validator=validator,
    ...     output_data={"diagnosis": "...", "confidence": 0.92}
    ... )
    >>> for policy_name, passed, message in results:
    ...     print(f"{policy_name}: {'✓' if passed else '✗'} {message}")

Note:
    Rate limiting policies require external enforcement (Redis, etc.)
    and are not handled by this bridge. See documentation for integration
    patterns with rate limiting middleware.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from .agent_facts import Policy
from .guardrails import (
    Constraint,
    FailAction,
    GuardRail,
    GuardRailValidator,
    Severity,
)

if TYPE_CHECKING:
    from .agent_facts import AgentFactsRegistry


def policy_to_guardrail(policy: Policy) -> GuardRail | None:
    """Convert an AgentFacts policy to an enforceable GuardRail.

    This bridge function reads the declarative policy from AgentFacts
    and creates runtime enforcement via GuardRails.

    Args:
        policy: AgentFacts Policy to convert

    Returns:
        GuardRail for enforcement, or None if policy type requires
        external enforcement (e.g., rate_limit)

    Raises:
        TypeError: If policy is not a Policy instance

    Example:
        >>> policy = Policy(
        ...     policy_id="hipaa-001",
        ...     name="HIPAA Compliance",
        ...     policy_type="data_access",
        ...     constraints={"pii_handling_mode": "redact"}
        ... )
        >>> guardrail = policy_to_guardrail(policy)
        >>> guardrail.name
        'data_access_hipaa-001'
    """
    if not isinstance(policy, Policy):
        raise TypeError("policy must be a Policy instance")

    if policy.policy_type == "rate_limit":
        # Rate limiting requires external counter (Redis, etc.)
        # GuardRails validates; external system enforces counts
        return None  # Handled by rate limiter middleware

    elif policy.policy_type == "data_access":
        constraints = []

        # Convert PII handling mode to constraint
        if policy.constraints.get("pii_handling_mode") == "redact":
            constraints.append(
                Constraint(
                    name="no_pii_in_output",
                    description="Output must not contain PII",
                    check_fn="pii",
                    params={},
                    severity=Severity.ERROR,
                    on_fail=FailAction.FIX,  # Attempt to redact
                )
            )

        if policy.constraints.get("audit_all_access"):
            constraints.append(
                Constraint(
                    name="log_all_access",
                    description="Log all data access for audit",
                    check_fn="always_pass",
                    params={"message": f"Audit log for {policy.name}"},
                    severity=Severity.INFO,
                    on_fail=FailAction.LOG,
                )
            )

        # If no constraints were generated, return None
        if not constraints:
            return None

        return GuardRail(
            name=f"data_access_{policy.policy_id}",
            description=f"Enforces: {policy.name}",
            constraints=constraints,
            on_fail_default=FailAction.REJECT,
        )

    elif policy.policy_type == "approval_required":
        # Approval gating requires workflow integration
        # GuardRails can validate that approval_id is present
        return GuardRail(
            name=f"approval_{policy.policy_id}",
            description=f"Validates approval for: {policy.name}",
            constraints=[
                Constraint(
                    name="approval_id_present",
                    description="Output must include approval reference",
                    check_fn="required",
                    params={"fields": ["approval_id", "approved_by"]},
                    severity=Severity.ERROR,
                    on_fail=FailAction.ESCALATE,
                )
            ],
            on_fail_default=FailAction.ESCALATE,
        )

    # Unknown policy type - cannot convert
    return None


def enforce_agent_policies(
    agent_id: str,
    registry: AgentFactsRegistry,
    validator: GuardRailValidator,
    output_data: dict,
) -> list[tuple[str, bool, str]]:
    """Enforce all active policies for an agent against its output.

    This function:
    1. Looks up the agent in the registry
    2. Gets all currently active policies
    3. Converts each policy to a GuardRail (if possible)
    4. Validates the output against each GuardRail
    5. Returns results for all policies

    Args:
        agent_id: Agent to check
        registry: AgentFacts registry
        validator: GuardRails validator
        output_data: Agent output to validate

    Returns:
        List of (policy_name, passed, message) tuples

    Raises:
        TypeError: If arguments are wrong type

    Example:
        >>> results = enforce_agent_policies(
        ...     "diagnosis-generator-v1",
        ...     registry,
        ...     validator,
        ...     {"diagnosis": "Common cold", "confidence": 0.85}
        ... )
        >>> for name, passed, msg in results:
        ...     print(f"{name}: {passed}")
        HIPAA Compliance: True
        Physician Approval: False
    """
    if not isinstance(agent_id, str):
        raise TypeError("agent_id must be a string")
    if not isinstance(output_data, dict):
        raise TypeError("output_data must be a dictionary")

    agent = registry.get(agent_id)
    if not agent:
        return [("agent_lookup", False, f"Agent {agent_id} not found")]

    results: list[tuple[str, bool, str]] = []

    for policy in agent.get_active_policies():
        guardrail = policy_to_guardrail(policy)
        if guardrail:
            result = validator.validate(output_data, guardrail)
            results.append(
                (
                    policy.name,
                    result.is_valid,
                    f"{result.total_errors} errors, {result.total_warnings} warnings",
                )
            )
        else:
            # Policy type requires external enforcement
            results.append(
                (
                    policy.name,
                    True,  # Assume pass - external system responsible
                    f"Policy type '{policy.policy_type}' requires external enforcement",
                )
            )

    return results


def get_enforceable_policies(
    agent_id: str, registry: AgentFactsRegistry
) -> list[tuple[Policy, GuardRail]]:
    """Get all policies that can be enforced via GuardRails.

    Filters out policies that require external enforcement (e.g., rate_limit).

    Args:
        agent_id: Agent to check
        registry: AgentFacts registry

    Returns:
        List of (Policy, GuardRail) tuples for enforceable policies

    Raises:
        ValueError: If agent not found
    """
    agent = registry.get(agent_id)
    if not agent:
        raise ValueError(f"Agent {agent_id} not found")

    enforceable: list[tuple[Policy, GuardRail]] = []

    for policy in agent.get_active_policies():
        guardrail = policy_to_guardrail(policy)
        if guardrail:
            enforceable.append((policy, guardrail))

    return enforceable


def get_external_enforcement_policies(
    agent_id: str, registry: AgentFactsRegistry
) -> list[Policy]:
    """Get policies that require external enforcement systems.

    These policies cannot be enforced by GuardRails alone and need
    integration with external systems (Redis for rate limiting, etc.)

    Args:
        agent_id: Agent to check
        registry: AgentFacts registry

    Returns:
        List of Policy objects requiring external enforcement

    Raises:
        ValueError: If agent not found
    """
    agent = registry.get(agent_id)
    if not agent:
        raise ValueError(f"Agent {agent_id} not found")

    external: list[Policy] = []

    for policy in agent.get_active_policies():
        if policy_to_guardrail(policy) is None:
            external.append(policy)

    return external
