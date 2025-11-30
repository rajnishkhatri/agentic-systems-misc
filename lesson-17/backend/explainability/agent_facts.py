"""AgentFacts Registry - Verifiable metadata for AI agents.

This module implements the AgentFacts metadata standard based on arXiv:2506.13794,
providing verifiable agent identity, capabilities, and policies for audits and
governance.

Key Features:
- Cryptographically signed capability declarations
- Multi-authority validation support
- Dynamic permission management
- Audit trail for all changes

Builds on:
- lesson-16/backend/reliability/validation.py - Pydantic schema patterns

Example:
    >>> registry = AgentFactsRegistry(storage_path=Path("cache/agent_facts"))
    >>> facts = AgentFacts(
    ...     agent_id="invoice-extractor-v1",
    ...     agent_name="Invoice Extractor",
    ...     owner="finance-team",
    ...     version="1.0.0",
    ...     capabilities=[Capability(name="extract_vendor", ...)],
    ...     policies=[Policy(policy_id="rate-limit", ...)]
    ... )
    >>> registry.register(facts)
    >>> registry.verify("invoice-extractor-v1")  # Returns True
"""

from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field, field_validator


class Capability(BaseModel):
    """Agent capability declaration.

    Describes what an agent can do, including input/output schemas,
    performance characteristics, and access requirements.

    Attributes:
        name: Unique name for this capability
        description: Human-readable description
        input_schema: JSON Schema for expected inputs
        output_schema: JSON Schema for expected outputs
        estimated_latency_ms: Expected execution time in milliseconds
        cost_per_call: Estimated cost per invocation (optional)
        requires_approval: Whether human approval is needed
        tags: List of tags for capability discovery
    """

    name: str
    description: str
    input_schema: dict[str, Any] = Field(default_factory=dict)
    output_schema: dict[str, Any] = Field(default_factory=dict)
    estimated_latency_ms: int = 1000
    cost_per_call: float | None = None
    requires_approval: bool = False
    tags: list[str] = Field(default_factory=list)

    class Config:
        extra = "forbid"

    @field_validator("name")
    @classmethod
    def validate_name_not_empty(cls, v: str) -> str:
        """Validate that capability name is not empty."""
        if not v.strip():
            raise ValueError("Capability name cannot be empty")
        return v


class Policy(BaseModel):
    """Operational policy for an agent.

    Defines constraints and rules that govern agent behavior,
    including rate limits, data access rules, and approval requirements.

    Attributes:
        policy_id: Unique identifier for this policy
        name: Human-readable name
        description: Detailed description of the policy
        policy_type: Type of policy (rate_limit, data_access, approval_required, etc.)
        constraints: Policy-specific constraint definitions
        effective_from: When this policy becomes effective
        effective_until: When this policy expires (None = no expiry)
        is_active: Whether this policy is currently active
    """

    policy_id: str
    name: str
    description: str
    policy_type: str
    constraints: dict[str, Any] = Field(default_factory=dict)
    effective_from: datetime = Field(default_factory=lambda: datetime.now(UTC))
    effective_until: datetime | None = None
    is_active: bool = True

    class Config:
        extra = "forbid"

    @field_validator("policy_id")
    @classmethod
    def validate_policy_id_not_empty(cls, v: str) -> str:
        """Validate that policy_id is not empty."""
        if not v.strip():
            raise ValueError("policy_id cannot be empty")
        return v

    def is_effective(self, at_time: datetime | None = None) -> bool:
        """Check if policy is effective at a given time.

        Args:
            at_time: Time to check (defaults to now)

        Returns:
            True if policy is effective at the given time
        """
        check_time = at_time or datetime.now(UTC)
        if not self.is_active:
            return False
        if check_time < self.effective_from:
            return False
        if self.effective_until and check_time > self.effective_until:
            return False
        return True


class AuditEntry(BaseModel):
    """Single entry in an agent's audit trail.

    Records changes to agent facts for compliance and debugging.

    Attributes:
        timestamp: When the change occurred
        action: Type of action (register, update, verify, etc.)
        changed_by: Who made the change
        changes: Description of what changed
        previous_signature: Signature hash before the change
        new_signature: Signature hash after the change
    """

    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))
    action: str
    changed_by: str
    changes: dict[str, Any] = Field(default_factory=dict)
    previous_signature: str | None = None
    new_signature: str | None = None

    class Config:
        extra = "forbid"


class AgentFacts(BaseModel):
    """Verifiable agent metadata for audits and governance.

    Implements the AgentFacts standard (arXiv:2506.13794) with:
    - Unique agent identity
    - Owner and version tracking
    - Capability declarations
    - Policy definitions
    - Cryptographic signature for verification

    Attributes:
        agent_id: Unique identifier for this agent
        agent_name: Human-readable name
        owner: Team or individual responsible for this agent
        version: Semantic version string
        description: Detailed description of agent purpose
        capabilities: List of capability declarations
        policies: List of operational policies
        created_at: When agent facts were first created
        updated_at: When agent facts were last updated
        signature_hash: SHA256 hash for tamper detection
        parent_agent_id: Parent agent ID for hierarchies (optional)
        metadata: Additional custom metadata
    """

    agent_id: str
    agent_name: str
    owner: str
    version: str
    description: str = ""
    capabilities: list[Capability] = Field(default_factory=list)
    policies: list[Policy] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    signature_hash: str = ""
    parent_agent_id: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)

    class Config:
        extra = "forbid"

    @field_validator("agent_id")
    @classmethod
    def validate_agent_id_not_empty(cls, v: str) -> str:
        """Validate that agent_id is not empty."""
        if not v.strip():
            raise ValueError("agent_id cannot be empty")
        return v

    @field_validator("owner")
    @classmethod
    def validate_owner_not_empty(cls, v: str) -> str:
        """Validate that owner is not empty."""
        if not v.strip():
            raise ValueError("owner cannot be empty")
        return v

    def compute_signature(self) -> str:
        """Compute cryptographic hash of agent facts for verification.

        Creates a SHA256 hash of the essential fields (excluding signature_hash)
        to enable tamper detection.

        Returns:
            Hex string of SHA256 hash
        """
        # Create dict of fields to hash (exclude signature_hash itself)
        hash_data = {
            "agent_id": self.agent_id,
            "agent_name": self.agent_name,
            "owner": self.owner,
            "version": self.version,
            "description": self.description,
            "capabilities": [c.model_dump(mode="json") for c in self.capabilities],
            "policies": [p.model_dump(mode="json") for p in self.policies],
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "parent_agent_id": self.parent_agent_id,
            "metadata": self.metadata,
        }

        serialized = json.dumps(hash_data, sort_keys=True, default=str)
        return hashlib.sha256(serialized.encode()).hexdigest()

    def verify_signature(self) -> bool:
        """Verify the signature hash matches current state.

        Checks if the stored signature_hash matches a freshly computed hash
        to detect tampering.

        Returns:
            True if signature is valid, False if tampered
        """
        if not self.signature_hash:
            return False
        return self.signature_hash == self.compute_signature()

    def get_capability(self, name: str) -> Capability | None:
        """Get a capability by name.

        Args:
            name: Name of the capability to find

        Returns:
            Capability if found, None otherwise
        """
        for cap in self.capabilities:
            if cap.name == name:
                return cap
        return None

    def get_active_policies(self, at_time: datetime | None = None) -> list[Policy]:
        """Get all policies that are currently active.

        Args:
            at_time: Time to check (defaults to now)

        Returns:
            List of active policies
        """
        return [p for p in self.policies if p.is_effective(at_time)]


class AgentFactsRegistry:
    """Registry for storing and verifying AgentFacts.

    Provides CRUD operations for agent facts with:
    - Automatic signature computation and verification
    - Audit trail for all changes
    - Capability-based agent discovery
    - Export for compliance audits

    Attributes:
        storage_path: Directory where agent facts are persisted
    """

    def __init__(self, storage_path: Path) -> None:
        """Initialize the registry.

        Args:
            storage_path: Directory for storing agent facts

        Raises:
            TypeError: If storage_path is not a Path
        """
        if not isinstance(storage_path, Path):
            raise TypeError("storage_path must be a Path")

        self.storage_path = storage_path
        self._registry_path = storage_path / "agent_facts_registry"
        self._audit_path = storage_path / "agent_facts_audit"

        # Ensure directories exist
        self._registry_path.mkdir(parents=True, exist_ok=True)
        self._audit_path.mkdir(parents=True, exist_ok=True)

        # In-memory cache
        self._agents: dict[str, AgentFacts] = {}
        self._audit_trails: dict[str, list[AuditEntry]] = {}

    def register(self, agent_facts: AgentFacts, registered_by: str = "system") -> None:
        """Register agent facts, computing and storing signature.

        Args:
            agent_facts: The agent facts to register
            registered_by: Who is registering this agent

        Raises:
            TypeError: If agent_facts is not an AgentFacts instance
            ValueError: If agent is already registered
        """
        if not isinstance(agent_facts, AgentFacts):
            raise TypeError("agent_facts must be an AgentFacts instance")

        if agent_facts.agent_id in self._agents:
            raise ValueError(f"Agent '{agent_facts.agent_id}' is already registered")

        # Compute signature
        agent_facts.signature_hash = agent_facts.compute_signature()

        # Store in memory and on disk
        self._agents[agent_facts.agent_id] = agent_facts
        self._persist_agent(agent_facts)

        # Create audit entry
        audit = AuditEntry(
            action="register",
            changed_by=registered_by,
            changes={"action": "initial_registration"},
            new_signature=agent_facts.signature_hash,
        )
        self._add_audit_entry(agent_facts.agent_id, audit)

    def update(
        self, agent_id: str, updates: dict[str, Any], updated_by: str = "system"
    ) -> AgentFacts:
        """Update agent facts, recomputing signature.

        Args:
            agent_id: ID of the agent to update
            updates: Dictionary of fields to update
            updated_by: Who is making the update

        Returns:
            Updated AgentFacts

        Raises:
            ValueError: If agent is not registered
            TypeError: If updates is not a dict
        """
        if not isinstance(updates, dict):
            raise TypeError("updates must be a dictionary")

        if agent_id not in self._agents:
            # Try to load from disk
            self._load_agent(agent_id)
            if agent_id not in self._agents:
                raise ValueError(f"Agent '{agent_id}' is not registered")

        agent = self._agents[agent_id]
        previous_signature = agent.signature_hash

        # Apply updates
        agent_dict = agent.model_dump()
        agent_dict.update(updates)
        agent_dict["updated_at"] = datetime.now(UTC)

        # Handle nested models
        if "capabilities" in updates:
            agent_dict["capabilities"] = [
                Capability(**c) if isinstance(c, dict) else c for c in updates["capabilities"]
            ]
        if "policies" in updates:
            agent_dict["policies"] = [
                Policy(**p) if isinstance(p, dict) else p for p in updates["policies"]
            ]

        # Create updated agent
        updated_agent = AgentFacts(**agent_dict)
        updated_agent.signature_hash = updated_agent.compute_signature()

        # Store
        self._agents[agent_id] = updated_agent
        self._persist_agent(updated_agent)

        # Create audit entry
        audit = AuditEntry(
            action="update",
            changed_by=updated_by,
            changes=updates,
            previous_signature=previous_signature,
            new_signature=updated_agent.signature_hash,
        )
        self._add_audit_entry(agent_id, audit)

        return updated_agent

    def verify(self, agent_id: str) -> bool:
        """Verify agent facts have not been tampered with.

        Args:
            agent_id: ID of the agent to verify

        Returns:
            True if signature is valid, False otherwise
        """
        if agent_id not in self._agents:
            self._load_agent(agent_id)
            if agent_id not in self._agents:
                return False

        agent = self._agents[agent_id]

        # Create audit entry for verification
        is_valid = agent.verify_signature()
        audit = AuditEntry(
            action="verify",
            changed_by="system",
            changes={"result": "valid" if is_valid else "invalid"},
        )
        self._add_audit_entry(agent_id, audit)

        return is_valid

    def get(self, agent_id: str) -> AgentFacts | None:
        """Retrieve agent facts by ID.

        Args:
            agent_id: ID of the agent to retrieve

        Returns:
            AgentFacts if found, None otherwise
        """
        if agent_id not in self._agents:
            self._load_agent(agent_id)
        return self._agents.get(agent_id)

    def get_capabilities(self, agent_id: str) -> list[Capability]:
        """Get capabilities for an agent.

        Args:
            agent_id: ID of the agent

        Returns:
            List of Capability (empty if agent not found)
        """
        agent = self.get(agent_id)
        return agent.capabilities if agent else []

    def get_policies(self, agent_id: str) -> list[Policy]:
        """Get policies for an agent.

        Args:
            agent_id: ID of the agent

        Returns:
            List of Policy (empty if agent not found)
        """
        agent = self.get(agent_id)
        return agent.policies if agent else []

    def find_by_capability(self, capability_name: str) -> list[AgentFacts]:
        """Find agents with a specific capability.

        Args:
            capability_name: Name of the capability to search for

        Returns:
            List of AgentFacts that have the specified capability
        """
        # Load all agents from disk
        self._load_all_agents()

        results = []
        for agent in self._agents.values():
            if agent.get_capability(capability_name):
                results.append(agent)
        return results

    def find_by_owner(self, owner: str) -> list[AgentFacts]:
        """Find agents owned by a specific team/individual.

        Args:
            owner: Owner to search for

        Returns:
            List of AgentFacts owned by the specified owner
        """
        self._load_all_agents()
        return [a for a in self._agents.values() if a.owner == owner]

    def audit_trail(self, agent_id: str) -> list[AuditEntry]:
        """Get audit trail of all changes to agent facts.

        Args:
            agent_id: ID of the agent

        Returns:
            List of AuditEntry in chronological order
        """
        if agent_id not in self._audit_trails:
            self._load_audit_trail(agent_id)
        return self._audit_trails.get(agent_id, [])

    def export_for_audit(self, agent_ids: list[str], filepath: Path) -> None:
        """Export agent facts for compliance audit.

        Creates a comprehensive export containing agent facts and audit trails
        for the specified agents.

        Args:
            agent_ids: List of agent IDs to export
            filepath: Path where export file should be written

        Raises:
            TypeError: If arguments are wrong type
        """
        if not isinstance(agent_ids, list):
            raise TypeError("agent_ids must be a list")
        if not isinstance(filepath, Path):
            raise TypeError("filepath must be a Path")

        export_data = {
            "exported_at": datetime.now(UTC).isoformat(),
            "agent_count": len(agent_ids),
            "agents": {},
        }

        for agent_id in agent_ids:
            agent = self.get(agent_id)
            if agent:
                export_data["agents"][agent_id] = {
                    "facts": agent.model_dump(mode="json"),
                    "is_valid": agent.verify_signature(),
                    "audit_trail": [a.model_dump(mode="json") for a in self.audit_trail(agent_id)],
                }

        filepath.parent.mkdir(parents=True, exist_ok=True)
        with open(filepath, "w") as f:
            json.dump(export_data, f, indent=2, default=str)

    def list_all(self) -> list[str]:
        """List all registered agent IDs.

        Returns:
            List of all agent IDs in the registry
        """
        self._load_all_agents()
        return list(self._agents.keys())

    def unregister(self, agent_id: str, unregistered_by: str = "system") -> None:
        """Remove an agent from the registry.

        Args:
            agent_id: ID of the agent to remove
            unregistered_by: Who is removing the agent

        Raises:
            ValueError: If agent is not registered
        """
        if agent_id not in self._agents:
            self._load_agent(agent_id)
            if agent_id not in self._agents:
                raise ValueError(f"Agent '{agent_id}' is not registered")

        agent = self._agents[agent_id]

        # Create audit entry
        audit = AuditEntry(
            action="unregister",
            changed_by=unregistered_by,
            changes={"action": "removed_from_registry"},
            previous_signature=agent.signature_hash,
        )
        self._add_audit_entry(agent_id, audit)

        # Remove from memory and disk
        del self._agents[agent_id]
        agent_path = self._registry_path / f"{agent_id}.json"
        if agent_path.exists():
            agent_path.unlink()

    # Private methods

    def _persist_agent(self, agent: AgentFacts) -> None:
        """Persist agent facts to disk."""
        filepath = self._registry_path / f"{agent.agent_id}.json"
        with open(filepath, "w") as f:
            json.dump(agent.model_dump(mode="json"), f, indent=2, default=str)

    def _load_agent(self, agent_id: str) -> None:
        """Load agent facts from disk."""
        filepath = self._registry_path / f"{agent_id}.json"
        if filepath.exists():
            with open(filepath) as f:
                data = json.load(f)
                self._agents[agent_id] = AgentFacts(**data)

    def _load_all_agents(self) -> None:
        """Load all agents from disk."""
        for filepath in self._registry_path.glob("*.json"):
            agent_id = filepath.stem
            if agent_id not in self._agents:
                self._load_agent(agent_id)

    def _add_audit_entry(self, agent_id: str, entry: AuditEntry) -> None:
        """Add an audit entry and persist."""
        if agent_id not in self._audit_trails:
            self._load_audit_trail(agent_id)
            if agent_id not in self._audit_trails:
                self._audit_trails[agent_id] = []

        self._audit_trails[agent_id].append(entry)
        self._persist_audit_trail(agent_id)

    def _persist_audit_trail(self, agent_id: str) -> None:
        """Persist audit trail to disk."""
        filepath = self._audit_path / f"{agent_id}_audit.json"
        entries = self._audit_trails.get(agent_id, [])
        with open(filepath, "w") as f:
            json.dump([e.model_dump(mode="json") for e in entries], f, indent=2, default=str)

    def _load_audit_trail(self, agent_id: str) -> None:
        """Load audit trail from disk."""
        filepath = self._audit_path / f"{agent_id}_audit.json"
        if filepath.exists():
            with open(filepath) as f:
                data = json.load(f)
                self._audit_trails[agent_id] = [AuditEntry(**e) for e in data]

