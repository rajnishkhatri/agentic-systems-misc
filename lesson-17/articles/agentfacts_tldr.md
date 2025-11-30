# AgentFacts: TL;DR Guide

**Reading time: 5 minutes** | [Full Article](./agentfacts_governance_deepdive.md) (~55 min)

---

## What Is AgentFacts?

A **verifiable metadata registry** for AI agents—think "driver's license for AI."

```
┌────────────────────────────────────────────────────┐
│  AGENTFACTS = WHO + WHAT + RULES + PROOF           │
├────────────────────────────────────────────────────┤
│  agent_id        → Unique identifier               │
│  capabilities[]  → What the agent can do           │
│  policies[]      → Rules governing behavior        │
│  signature_hash  → Tamper detection (SHA256)       │
│  audit_trail[]   → History of all changes          │
└────────────────────────────────────────────────────┘
```

---

## Why Use It?

**Before AgentFacts:**
- "Which agent version processed this data?" → 45 min searching logs
- "What policies govern this agent?" → 1 hour checking config files
- "Has anyone modified it?" → Impossible to know

**After AgentFacts:**
- Version lookup: **5 seconds**
- Policy listing: **10 seconds**
- Tamper verification: **2 seconds**

---

## Core Concepts (4 Data Types)

### 1. Capability
What the agent can do + input/output contracts.

```python
Capability(
    name="analyze_symptoms",
    input_schema={"symptoms": ["string"]},
    output_schema={"diagnoses": ["string"]},
    requires_approval=True  # Human-in-the-loop flag
)
```

### 2. Policy
Rules governing agent behavior.

| Type | Purpose | Example |
|------|---------|---------|
| `rate_limit` | Throttling | max 1000 calls/min |
| `data_access` | Data restrictions | PII redaction required |
| `approval_required` | Human oversight | Physician must approve |

### 3. AgentFacts
Complete identity document combining all of the above.

### 4. AuditEntry
Immutable change history (survives agent deletion).

---

## Quick Start

```python
from pathlib import Path
from backend.explainability.agent_facts import (
    AgentFactsRegistry, AgentFacts, Capability, Policy
)

# 1. Create registry
registry = AgentFactsRegistry(storage_path=Path("cache/agent_facts"))

# 2. Register an agent
agent = AgentFacts(
    agent_id="my-agent-v1",
    agent_name="My Agent",
    owner="my-team@company.com",
    version="1.0.0",
    capabilities=[Capability(name="do_thing", description="Does the thing")],
    policies=[Policy(
        policy_id="policy-001",
        name="Rate Limit",
        policy_type="rate_limit",
        constraints={"max_calls_per_minute": 100}
    )]
)
registry.register(agent, registered_by="admin@company.com")

# 3. Verify integrity
is_valid = registry.verify("my-agent-v1")  # True if not tampered

# 4. Query
agent = registry.get("my-agent-v1")
active_policies = agent.get_active_policies()
```

---

## Key Operations

| Operation | Code | Returns |
|-----------|------|---------|
| Register | `registry.register(agent, by="...")` | None |
| Get | `registry.get("agent-id")` | AgentFacts |
| Update | `registry.update("agent-id", changes={}, by="...")` | None |
| Verify | `registry.verify("agent-id")` | bool |
| Find by capability | `registry.find_by_capability("cap_name")` | list |
| Export for audit | `registry.export_for_audit(ids, path)` | JSON file |

---

## Critical Distinctions

### Verification vs. Enforcement

```
AgentFacts  →  "What policies SHOULD govern this agent?"  (declaration)
GuardRails  →  "Does this output comply?"                 (enforcement)
```

**AgentFacts does NOT enforce policies at runtime.** It declares them. Use GuardRails for actual enforcement.

### Security Limitations

| Protected Against | NOT Protected Against |
|-------------------|----------------------|
| ✅ Accidental changes | ❌ Malicious insiders with registry access |
| ✅ Configuration drift | ❌ Direct database modification |
| ✅ Audit trail gaps | ❌ Replay attacks |

**SHA256 = integrity check, not cryptographic security.**

For high-security environments, add:
- Level 1: RBAC on registry access
- Level 2: RSA signatures (private key signing)
- Level 3: Immutable ledger/blockchain

---

## Integration with Other Systems

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│ AgentFacts  │     │  BlackBox   │     │ GuardRails  │
│   (WHO)     │────▶│   (WHAT)    │────▶│  (VALID?)   │
│             │     │             │     │             │
│ Identity    │     │ Timeline    │     │ Constraints │
│ Policies    │     │ Decisions   │     │ PII Check   │
└─────────────┘     └─────────────┘     └─────────────┘

Together: "WHO did WHAT, and was it VALID?"
```

---

## Common Patterns

### Find expired policies
```python
from datetime import datetime, UTC, timedelta

for agent_id in registry.list_all():
    for policy in registry.get_policies(agent_id):
        if not policy.is_effective():
            print(f"EXPIRED: {policy.name} on {agent_id}")
```

### Batch verification
```python
invalid = [
    agent_id for agent_id in registry.list_all()
    if not registry.verify(agent_id)
]
if invalid:
    alert(f"TAMPERING DETECTED: {invalid}")
```

### Export for compliance audit
```python
registry.export_for_audit(
    agent_ids=["agent-1", "agent-2"],
    filepath=Path("audits/Q1-2025.json")
)
```

---

## When to Use AgentFacts

**Essential for:**
- Regulated industries (healthcare, finance)
- Multi-agent systems with complex authorization
- Compliance audits (HIPAA, SOX, GDPR)

**Optional for:**
- Single-agent systems
- Development/testing environments
- Low-stakes applications

---

## Files Reference

| File | Purpose |
|------|---------|
| `backend/explainability/agent_facts.py` | Core implementation |
| `backend/explainability/guardrails.py` | Policy enforcement |
| `data/agent_metadata_10.json` | Sample dataset |
| `notebooks/02_agent_facts_verification.ipynb` | Interactive demo |
| `tutorials/03_agent_facts_governance.md` | Step-by-step guide |

---

## Further Reading

- [Full Deep Dive Article](./agentfacts_governance_deepdive.md) — Complete 55-minute guide
- [Tutorial 3: AgentFacts for Governance](../tutorials/03_agent_facts_governance.md) — Hands-on implementation
- [BlackBox Recording](./blackbox_narrative_deepdive.md) — Companion "What Happened" system

---

*TL;DR created: 2025-11-29*
*Companion to: agentfacts_governance_deepdive.md*
