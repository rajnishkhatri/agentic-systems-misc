"""Tests for AgentFacts Registry - Verifiable agent metadata.

Tests the AgentFacts implementation including:
- AgentFacts model creation and validation
- Signature computation and verification
- Registry operations (register, update, verify)
- Audit trail tracking
- Capability-based discovery
"""

from __future__ import annotations

import json
import tempfile
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest

import sys
from pathlib import Path

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.explainability.agent_facts import (
    AgentFacts,
    AgentFactsRegistry,
    AuditEntry,
    Capability,
    Policy,
)


class TestCapabilityModel:
    """Tests for Capability Pydantic model."""

    def test_create_capability(self) -> None:
        """Test creating a valid capability."""
        cap = Capability(
            name="extract_vendor",
            description="Extracts vendor name from invoice",
            input_schema={"type": "object", "properties": {"text": {"type": "string"}}},
            output_schema={"type": "object", "properties": {"vendor": {"type": "string"}}},
            estimated_latency_ms=500,
            cost_per_call=0.01,
            requires_approval=False,
            tags=["extraction", "invoice"],
        )
        assert cap.name == "extract_vendor"
        assert cap.estimated_latency_ms == 500
        assert len(cap.tags) == 2

    def test_capability_empty_name_rejected(self) -> None:
        """Test empty capability name is rejected."""
        with pytest.raises(ValueError, match="cannot be empty"):
            Capability(name="  ", description="Test")

    def test_capability_defaults(self) -> None:
        """Test capability default values."""
        cap = Capability(name="test", description="Test capability")
        assert cap.estimated_latency_ms == 1000
        assert cap.cost_per_call is None
        assert cap.requires_approval is False
        assert cap.tags == []


class TestPolicyModel:
    """Tests for Policy Pydantic model."""

    def test_create_policy(self) -> None:
        """Test creating a valid policy."""
        policy = Policy(
            policy_id="rate-limit-001",
            name="Rate Limit",
            description="Limits API calls per minute",
            policy_type="rate_limit",
            constraints={"max_calls_per_minute": 60},
        )
        assert policy.policy_id == "rate-limit-001"
        assert policy.is_active is True

    def test_policy_is_effective(self) -> None:
        """Test policy effectiveness checking."""
        now = datetime.now(UTC)

        # Active policy with no end date
        policy = Policy(
            policy_id="p1",
            name="Test",
            description="Test",
            policy_type="test",
            effective_from=now - timedelta(days=1),
        )
        assert policy.is_effective() is True

        # Inactive policy
        policy.is_active = False
        assert policy.is_effective() is False

        # Future policy
        policy.is_active = True
        policy.effective_from = now + timedelta(days=1)
        assert policy.is_effective() is False

        # Expired policy
        policy.effective_from = now - timedelta(days=10)
        policy.effective_until = now - timedelta(days=1)
        assert policy.is_effective() is False


class TestAgentFactsModel:
    """Tests for AgentFacts Pydantic model."""

    def test_create_agent_facts(self) -> None:
        """Test creating valid agent facts."""
        facts = AgentFacts(
            agent_id="invoice-extractor-v1",
            agent_name="Invoice Extractor",
            owner="finance-team",
            version="1.0.0",
            description="Extracts data from invoices",
            capabilities=[
                Capability(name="extract_vendor", description="Extracts vendor"),
            ],
            policies=[
                Policy(
                    policy_id="p1",
                    name="Rate Limit",
                    description="Limit calls",
                    policy_type="rate_limit",
                ),
            ],
        )
        assert facts.agent_id == "invoice-extractor-v1"
        assert len(facts.capabilities) == 1
        assert len(facts.policies) == 1

    def test_agent_id_not_empty(self) -> None:
        """Test agent_id cannot be empty."""
        with pytest.raises(ValueError, match="cannot be empty"):
            AgentFacts(
                agent_id="  ",
                agent_name="Test",
                owner="team",
                version="1.0.0",
            )

    def test_owner_not_empty(self) -> None:
        """Test owner cannot be empty."""
        with pytest.raises(ValueError, match="cannot be empty"):
            AgentFacts(
                agent_id="test",
                agent_name="Test",
                owner="  ",
                version="1.0.0",
            )

    def test_compute_signature(self) -> None:
        """Test signature computation."""
        facts = AgentFacts(
            agent_id="test",
            agent_name="Test",
            owner="team",
            version="1.0.0",
        )
        sig1 = facts.compute_signature()
        sig2 = facts.compute_signature()

        assert sig1 == sig2  # Deterministic
        assert len(sig1) == 64  # SHA256

    def test_verify_signature(self) -> None:
        """Test signature verification."""
        facts = AgentFacts(
            agent_id="test",
            agent_name="Test",
            owner="team",
            version="1.0.0",
        )
        # No signature set
        assert facts.verify_signature() is False

        # Set valid signature
        facts.signature_hash = facts.compute_signature()
        assert facts.verify_signature() is True

        # Tamper with data
        facts.version = "2.0.0"
        assert facts.verify_signature() is False

    def test_get_capability(self) -> None:
        """Test getting capability by name."""
        facts = AgentFacts(
            agent_id="test",
            agent_name="Test",
            owner="team",
            version="1.0.0",
            capabilities=[
                Capability(name="cap1", description="Cap 1"),
                Capability(name="cap2", description="Cap 2"),
            ],
        )
        assert facts.get_capability("cap1") is not None
        assert facts.get_capability("cap1").name == "cap1"
        assert facts.get_capability("nonexistent") is None

    def test_get_active_policies(self) -> None:
        """Test getting active policies."""
        now = datetime.now(UTC)
        facts = AgentFacts(
            agent_id="test",
            agent_name="Test",
            owner="team",
            version="1.0.0",
            policies=[
                Policy(
                    policy_id="active",
                    name="Active",
                    description="Active policy",
                    policy_type="test",
                    effective_from=now - timedelta(days=1),
                ),
                Policy(
                    policy_id="inactive",
                    name="Inactive",
                    description="Inactive policy",
                    policy_type="test",
                    is_active=False,
                ),
            ],
        )
        active = facts.get_active_policies()
        assert len(active) == 1
        assert active[0].policy_id == "active"


class TestAgentFactsRegistry:
    """Tests for AgentFactsRegistry class."""

    @pytest.fixture
    def temp_storage(self) -> Path:
        """Create temporary storage directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)

    @pytest.fixture
    def registry(self, temp_storage: Path) -> AgentFactsRegistry:
        """Create an AgentFactsRegistry instance."""
        return AgentFactsRegistry(storage_path=temp_storage)

    @pytest.fixture
    def sample_facts(self) -> AgentFacts:
        """Create sample agent facts."""
        return AgentFacts(
            agent_id="test-agent",
            agent_name="Test Agent",
            owner="test-team",
            version="1.0.0",
            capabilities=[
                Capability(name="test_cap", description="Test capability"),
            ],
        )

    def test_register_agent(
        self, registry: AgentFactsRegistry, sample_facts: AgentFacts
    ) -> None:
        """Test registering an agent."""
        registry.register(sample_facts, registered_by="admin")

        # Verify agent is registered
        retrieved = registry.get("test-agent")
        assert retrieved is not None
        assert retrieved.agent_id == "test-agent"
        assert retrieved.signature_hash != ""  # Signature computed

    def test_register_duplicate_rejected(
        self, registry: AgentFactsRegistry, sample_facts: AgentFacts
    ) -> None:
        """Test registering duplicate agent is rejected."""
        registry.register(sample_facts)

        with pytest.raises(ValueError, match="already registered"):
            registry.register(sample_facts)

    def test_update_agent(
        self, registry: AgentFactsRegistry, sample_facts: AgentFacts
    ) -> None:
        """Test updating agent facts."""
        registry.register(sample_facts)

        updated = registry.update(
            "test-agent",
            {"version": "2.0.0", "description": "Updated description"},
            updated_by="admin",
        )

        assert updated.version == "2.0.0"
        assert updated.description == "Updated description"
        # Signature should be recomputed
        assert updated.verify_signature() is True

    def test_update_nonexistent_rejected(self, registry: AgentFactsRegistry) -> None:
        """Test updating nonexistent agent is rejected."""
        with pytest.raises(ValueError, match="not registered"):
            registry.update("nonexistent", {"version": "2.0.0"})

    def test_verify_agent(
        self, registry: AgentFactsRegistry, sample_facts: AgentFacts
    ) -> None:
        """Test verifying agent signature."""
        registry.register(sample_facts)

        assert registry.verify("test-agent") is True
        assert registry.verify("nonexistent") is False

    def test_get_capabilities(
        self, registry: AgentFactsRegistry, sample_facts: AgentFacts
    ) -> None:
        """Test getting capabilities for an agent."""
        registry.register(sample_facts)

        caps = registry.get_capabilities("test-agent")
        assert len(caps) == 1
        assert caps[0].name == "test_cap"

        assert registry.get_capabilities("nonexistent") == []

    def test_get_policies(
        self, registry: AgentFactsRegistry, sample_facts: AgentFacts
    ) -> None:
        """Test getting policies for an agent."""
        sample_facts.policies = [
            Policy(
                policy_id="p1",
                name="Test Policy",
                description="Test",
                policy_type="test",
            )
        ]
        registry.register(sample_facts)

        policies = registry.get_policies("test-agent")
        assert len(policies) == 1

    def test_find_by_capability(
        self, registry: AgentFactsRegistry, temp_storage: Path
    ) -> None:
        """Test finding agents by capability."""
        # Register multiple agents
        agent1 = AgentFacts(
            agent_id="agent1",
            agent_name="Agent 1",
            owner="team",
            version="1.0.0",
            capabilities=[Capability(name="shared_cap", description="Shared")],
        )
        agent2 = AgentFacts(
            agent_id="agent2",
            agent_name="Agent 2",
            owner="team",
            version="1.0.0",
            capabilities=[
                Capability(name="shared_cap", description="Shared"),
                Capability(name="unique_cap", description="Unique"),
            ],
        )
        registry.register(agent1)
        registry.register(agent2)

        # Find by shared capability
        found = registry.find_by_capability("shared_cap")
        assert len(found) == 2

        # Find by unique capability
        found = registry.find_by_capability("unique_cap")
        assert len(found) == 1
        assert found[0].agent_id == "agent2"

    def test_find_by_owner(self, registry: AgentFactsRegistry) -> None:
        """Test finding agents by owner."""
        agent1 = AgentFacts(
            agent_id="agent1",
            agent_name="Agent 1",
            owner="team-a",
            version="1.0.0",
        )
        agent2 = AgentFacts(
            agent_id="agent2",
            agent_name="Agent 2",
            owner="team-b",
            version="1.0.0",
        )
        registry.register(agent1)
        registry.register(agent2)

        found = registry.find_by_owner("team-a")
        assert len(found) == 1
        assert found[0].agent_id == "agent1"

    def test_audit_trail(
        self, registry: AgentFactsRegistry, sample_facts: AgentFacts
    ) -> None:
        """Test audit trail is maintained."""
        registry.register(sample_facts, registered_by="admin")
        registry.update("test-agent", {"version": "2.0.0"}, updated_by="dev")
        registry.verify("test-agent")

        trail = registry.audit_trail("test-agent")
        assert len(trail) == 3
        assert trail[0].action == "register"
        assert trail[1].action == "update"
        assert trail[2].action == "verify"

    def test_export_for_audit(
        self, registry: AgentFactsRegistry, sample_facts: AgentFacts, temp_storage: Path
    ) -> None:
        """Test exporting agent facts for audit."""
        registry.register(sample_facts)

        export_path = temp_storage / "audit_export.json"
        registry.export_for_audit(["test-agent"], export_path)

        assert export_path.exists()

        with open(export_path) as f:
            data = json.load(f)

        assert "test-agent" in data["agents"]
        assert data["agents"]["test-agent"]["is_valid"] is True

    def test_list_all(
        self, registry: AgentFactsRegistry, sample_facts: AgentFacts
    ) -> None:
        """Test listing all registered agents."""
        registry.register(sample_facts)

        agent2 = AgentFacts(
            agent_id="agent2",
            agent_name="Agent 2",
            owner="team",
            version="1.0.0",
        )
        registry.register(agent2)

        all_agents = registry.list_all()
        assert len(all_agents) == 2
        assert "test-agent" in all_agents
        assert "agent2" in all_agents

    def test_unregister(
        self, registry: AgentFactsRegistry, sample_facts: AgentFacts
    ) -> None:
        """Test unregistering an agent."""
        registry.register(sample_facts)
        assert registry.get("test-agent") is not None

        registry.unregister("test-agent", unregistered_by="admin")
        assert registry.get("test-agent") is None

        # Audit trail should record unregister
        trail = registry.audit_trail("test-agent")
        assert any(e.action == "unregister" for e in trail)

    def test_persistence(self, temp_storage: Path, sample_facts: AgentFacts) -> None:
        """Test data persists across registry instances."""
        # Register with first registry
        registry1 = AgentFactsRegistry(storage_path=temp_storage)
        registry1.register(sample_facts)

        # Create new registry and verify data loads
        registry2 = AgentFactsRegistry(storage_path=temp_storage)
        retrieved = registry2.get("test-agent")
        assert retrieved is not None
        assert retrieved.agent_id == "test-agent"

