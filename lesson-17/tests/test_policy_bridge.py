"""Tests for Policy Bridge - Connect AgentFacts policies to GuardRails enforcement.

Tests the policy bridge implementation including:
- policy_to_guardrail() conversion for different policy types
- enforce_agent_policies() integration
- get_enforceable_policies() filtering
- get_external_enforcement_policies() filtering
- Error handling and edge cases
"""

from __future__ import annotations

import sys
from datetime import UTC, datetime
from pathlib import Path
from tempfile import TemporaryDirectory

import pytest

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.explainability.agent_facts import (
    AgentFacts,
    AgentFactsRegistry,
    Capability,
    Policy,
)
from backend.explainability.guardrails import (
    FailAction,
    GuardRail,
    GuardRailValidator,
    Severity,
)
from backend.explainability.policy_bridge import (
    enforce_agent_policies,
    get_enforceable_policies,
    get_external_enforcement_policies,
    policy_to_guardrail,
)


class TestPolicyToGuardrail:
    """Tests for policy_to_guardrail() conversion function."""

    def test_should_return_none_for_rate_limit_policy(self) -> None:
        """Rate limit policies require external enforcement (Redis)."""
        policy = Policy(
            policy_id="rate-001",
            name="API Rate Limit",
            description="Limits API calls per minute",
            policy_type="rate_limit",
            constraints={"max_calls_per_minute": 100},
        )
        result = policy_to_guardrail(policy)
        assert result is None

    def test_should_create_guardrail_for_data_access_with_pii_redact(self) -> None:
        """Data access policy with pii_handling_mode=redact creates PII constraint."""
        policy = Policy(
            policy_id="hipaa-001",
            name="HIPAA Compliance",
            description="Ensures HIPAA compliance for healthcare data",
            policy_type="data_access",
            constraints={"pii_handling_mode": "redact"},
        )
        result = policy_to_guardrail(policy)

        assert result is not None
        assert isinstance(result, GuardRail)
        assert result.name == "data_access_hipaa-001"
        assert len(result.constraints) == 1
        assert result.constraints[0].name == "no_pii_in_output"
        assert result.constraints[0].check_fn == "pii"
        assert result.constraints[0].on_fail == FailAction.FIX

    def test_should_create_guardrail_for_data_access_with_audit_logging(self) -> None:
        """Data access policy with audit_all_access creates logging constraint."""
        policy = Policy(
            policy_id="audit-001",
            name="Audit Logging",
            description="Log all data access for compliance",
            policy_type="data_access",
            constraints={"audit_all_access": True},
        )
        result = policy_to_guardrail(policy)

        assert result is not None
        assert len(result.constraints) == 1
        assert result.constraints[0].name == "log_all_access"
        assert result.constraints[0].check_fn == "always_pass"
        assert result.constraints[0].severity == Severity.INFO

    def test_should_create_guardrail_with_multiple_constraints(self) -> None:
        """Data access policy with both PII and audit creates both constraints."""
        policy = Policy(
            policy_id="combined-001",
            name="Full Compliance",
            description="Combined PII protection and audit logging",
            policy_type="data_access",
            constraints={"pii_handling_mode": "redact", "audit_all_access": True},
        )
        result = policy_to_guardrail(policy)

        assert result is not None
        assert len(result.constraints) == 2
        constraint_names = [c.name for c in result.constraints]
        assert "no_pii_in_output" in constraint_names
        assert "log_all_access" in constraint_names

    def test_should_return_none_for_data_access_without_constraints(self) -> None:
        """Data access policy without enforceable constraints returns None."""
        policy = Policy(
            policy_id="empty-001",
            name="Empty Policy",
            description="Policy with no enforceable constraints",
            policy_type="data_access",
            constraints={},
        )
        result = policy_to_guardrail(policy)
        assert result is None

    def test_should_create_guardrail_for_approval_required(self) -> None:
        """Approval required policy creates approval validation guardrail."""
        policy = Policy(
            policy_id="approval-001",
            name="Physician Approval",
            description="Requires physician approval for diagnoses",
            policy_type="approval_required",
            constraints={"approval_role": "physician"},
        )
        result = policy_to_guardrail(policy)

        assert result is not None
        assert result.name == "approval_approval-001"
        assert len(result.constraints) == 1
        assert result.constraints[0].name == "approval_id_present"
        assert result.constraints[0].check_fn == "required"
        assert result.constraints[0].params == {"fields": ["approval_id", "approved_by"]}
        assert result.on_fail_default == FailAction.ESCALATE

    def test_should_return_none_for_unknown_policy_type(self) -> None:
        """Unknown policy types return None (require custom handling)."""
        policy = Policy(
            policy_id="custom-001",
            name="Custom Policy",
            description="Custom policy type requiring external handling",
            policy_type="custom_unknown",
            constraints={"foo": "bar"},
        )
        result = policy_to_guardrail(policy)
        assert result is None

    def test_should_raise_type_error_for_invalid_input(self) -> None:
        """Invalid input raises TypeError."""
        with pytest.raises(TypeError, match="policy must be a Policy instance"):
            policy_to_guardrail("not a policy")  # type: ignore

        with pytest.raises(TypeError, match="policy must be a Policy instance"):
            policy_to_guardrail({"policy_type": "rate_limit"})  # type: ignore


class TestEnforceAgentPolicies:
    """Tests for enforce_agent_policies() integration function."""

    @pytest.fixture
    def temp_registry(self) -> AgentFactsRegistry:
        """Create a temporary registry for testing."""
        with TemporaryDirectory() as tmpdir:
            registry = AgentFactsRegistry(storage_path=Path(tmpdir))
            yield registry

    @pytest.fixture
    def sample_agent(self) -> AgentFacts:
        """Create a sample agent with multiple policies."""
        return AgentFacts(
            agent_id="test-agent-v1",
            agent_name="Test Agent",
            owner="test-team",
            version="1.0.0",
            capabilities=[
                Capability(name="process_data", description="Processes data")
            ],
            policies=[
                Policy(
                    policy_id="rate-001",
                    name="Rate Limit",
                    description="Limits API calls",
                    policy_type="rate_limit",
                    constraints={"max_calls_per_minute": 100},
                ),
                Policy(
                    policy_id="data-001",
                    name="PII Protection",
                    description="Protects PII in output",
                    policy_type="data_access",
                    constraints={"pii_handling_mode": "redact"},
                ),
                Policy(
                    policy_id="approval-001",
                    name="Manager Approval",
                    description="Requires manager approval",
                    policy_type="approval_required",
                    constraints={"approval_role": "manager"},
                ),
            ],
        )

    def test_should_return_error_for_nonexistent_agent(
        self, temp_registry: AgentFactsRegistry
    ) -> None:
        """Returns error tuple when agent not found."""
        validator = GuardRailValidator()
        results = enforce_agent_policies(
            "nonexistent-agent", temp_registry, validator, {"output": "test"}
        )

        assert len(results) == 1
        assert results[0][0] == "agent_lookup"
        assert results[0][1] is False
        assert "not found" in results[0][2]

    def test_should_enforce_all_active_policies(
        self, temp_registry: AgentFactsRegistry, sample_agent: AgentFacts
    ) -> None:
        """Enforces all active policies and returns results."""
        temp_registry.register(sample_agent, registered_by="test@test.com")
        validator = GuardRailValidator()

        # Output that passes PII check but fails approval check
        output_data = {"output": "No PII here", "confidence": 0.9}

        results = enforce_agent_policies(
            "test-agent-v1", temp_registry, validator, output_data
        )

        assert len(results) == 3
        policy_names = [r[0] for r in results]
        assert "Rate Limit" in policy_names
        assert "PII Protection" in policy_names
        assert "Manager Approval" in policy_names

        # Rate limit should indicate external enforcement
        rate_result = next(r for r in results if r[0] == "Rate Limit")
        assert rate_result[1] is True
        assert "external enforcement" in rate_result[2]

        # PII should pass (no PII in output)
        pii_result = next(r for r in results if r[0] == "PII Protection")
        assert pii_result[1] is True

        # Approval should fail (no approval_id in output)
        approval_result = next(r for r in results if r[0] == "Manager Approval")
        assert approval_result[1] is False

    def test_should_pass_approval_when_fields_present(
        self, temp_registry: AgentFactsRegistry, sample_agent: AgentFacts
    ) -> None:
        """Approval policy passes when required fields are present."""
        temp_registry.register(sample_agent, registered_by="test@test.com")
        validator = GuardRailValidator()

        output_data = {
            "output": "Approved result",
            "approval_id": "APR-12345",
            "approved_by": "manager@company.com",
        }

        results = enforce_agent_policies(
            "test-agent-v1", temp_registry, validator, output_data
        )

        approval_result = next(r for r in results if r[0] == "Manager Approval")
        assert approval_result[1] is True

    def test_should_detect_pii_in_output(
        self, temp_registry: AgentFactsRegistry, sample_agent: AgentFacts
    ) -> None:
        """PII protection policy fails when PII detected."""
        temp_registry.register(sample_agent, registered_by="test@test.com")
        validator = GuardRailValidator()

        # Output contains SSN
        output_data = {"output": "Patient SSN: 123-45-6789"}

        results = enforce_agent_policies(
            "test-agent-v1", temp_registry, validator, output_data
        )

        pii_result = next(r for r in results if r[0] == "PII Protection")
        assert pii_result[1] is False
        assert "1 errors" in pii_result[2]

    def test_should_raise_type_error_for_invalid_agent_id(
        self, temp_registry: AgentFactsRegistry
    ) -> None:
        """Invalid agent_id type raises TypeError."""
        validator = GuardRailValidator()
        with pytest.raises(TypeError, match="agent_id must be a string"):
            enforce_agent_policies(123, temp_registry, validator, {})  # type: ignore

    def test_should_raise_type_error_for_invalid_output_data(
        self, temp_registry: AgentFactsRegistry
    ) -> None:
        """Invalid output_data type raises TypeError."""
        validator = GuardRailValidator()
        with pytest.raises(TypeError, match="output_data must be a dictionary"):
            enforce_agent_policies("agent", temp_registry, validator, "not a dict")  # type: ignore


class TestGetEnforceablePolicies:
    """Tests for get_enforceable_policies() filtering function."""

    @pytest.fixture
    def temp_registry(self) -> AgentFactsRegistry:
        """Create a temporary registry for testing."""
        with TemporaryDirectory() as tmpdir:
            registry = AgentFactsRegistry(storage_path=Path(tmpdir))
            yield registry

    def test_should_return_only_enforceable_policies(
        self, temp_registry: AgentFactsRegistry
    ) -> None:
        """Returns only policies that can be enforced via GuardRails."""
        agent = AgentFacts(
            agent_id="mixed-agent",
            agent_name="Mixed Agent",
            owner="test-team",
            version="1.0.0",
            policies=[
                Policy(
                    policy_id="rate-001",
                    name="Rate Limit",
                    description="Limits API calls",
                    policy_type="rate_limit",
                    constraints={},
                ),
                Policy(
                    policy_id="data-001",
                    name="PII Check",
                    description="Checks for PII in output",
                    policy_type="data_access",
                    constraints={"pii_handling_mode": "redact"},
                ),
            ],
        )
        temp_registry.register(agent, registered_by="test@test.com")

        result = get_enforceable_policies("mixed-agent", temp_registry)

        assert len(result) == 1
        policy, guardrail = result[0]
        assert policy.name == "PII Check"
        assert isinstance(guardrail, GuardRail)

    def test_should_raise_value_error_for_nonexistent_agent(
        self, temp_registry: AgentFactsRegistry
    ) -> None:
        """Raises ValueError when agent not found."""
        with pytest.raises(ValueError, match="not found"):
            get_enforceable_policies("nonexistent", temp_registry)


class TestGetExternalEnforcementPolicies:
    """Tests for get_external_enforcement_policies() filtering function."""

    @pytest.fixture
    def temp_registry(self) -> AgentFactsRegistry:
        """Create a temporary registry for testing."""
        with TemporaryDirectory() as tmpdir:
            registry = AgentFactsRegistry(storage_path=Path(tmpdir))
            yield registry

    def test_should_return_only_external_policies(
        self, temp_registry: AgentFactsRegistry
    ) -> None:
        """Returns only policies requiring external enforcement."""
        agent = AgentFacts(
            agent_id="mixed-agent",
            agent_name="Mixed Agent",
            owner="test-team",
            version="1.0.0",
            policies=[
                Policy(
                    policy_id="rate-001",
                    name="Rate Limit",
                    description="Limits API calls",
                    policy_type="rate_limit",
                    constraints={"max_calls_per_minute": 100},
                ),
                Policy(
                    policy_id="data-001",
                    name="PII Check",
                    description="Checks for PII",
                    policy_type="data_access",
                    constraints={"pii_handling_mode": "redact"},
                ),
                Policy(
                    policy_id="custom-001",
                    name="Custom Policy",
                    description="Custom policy type",
                    policy_type="custom_type",
                    constraints={},
                ),
            ],
        )
        temp_registry.register(agent, registered_by="test@test.com")

        result = get_external_enforcement_policies("mixed-agent", temp_registry)

        assert len(result) == 2
        policy_names = [p.name for p in result]
        assert "Rate Limit" in policy_names
        assert "Custom Policy" in policy_names
        assert "PII Check" not in policy_names

    def test_should_raise_value_error_for_nonexistent_agent(
        self, temp_registry: AgentFactsRegistry
    ) -> None:
        """Raises ValueError when agent not found."""
        with pytest.raises(ValueError, match="not found"):
            get_external_enforcement_policies("nonexistent", temp_registry)


class TestAlwaysPassValidator:
    """Tests for the always_pass validator used in audit logging."""

    def test_should_always_pass_validation(self) -> None:
        """Always pass constraint always returns True."""
        from backend.explainability.guardrails import BuiltInValidators

        constraint = BuiltInValidators.always_pass("Audit log entry")

        assert constraint.name == "always_pass"
        assert constraint.severity == Severity.INFO
        assert constraint.on_fail == FailAction.LOG

    def test_should_pass_with_any_data(self) -> None:
        """Check function passes regardless of input."""
        from backend.explainability.guardrails import BuiltInValidators

        passed, message = BuiltInValidators.check_always_pass({}, "Test message")
        assert passed is True
        assert message == "Test message"

        passed, message = BuiltInValidators.check_always_pass(
            {"any": "data"}, "Custom"
        )
        assert passed is True
        assert message == "Custom"
