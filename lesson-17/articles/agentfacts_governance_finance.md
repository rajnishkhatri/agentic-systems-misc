# AgentFacts for Finance: Building Verifiable Agent Governance for SOX and PCI-DSS Compliance

**Part 2 of the BlackBox Explainability Series**

*Continuing from [BlackBox Recording Deep Dive](./blackbox_narrative_deepdive.md)*

> **Note**: This article is based on patterns from enterprise finance AI work, with details abstracted for illustration. Company names, specific dollar amounts, and implementation details have been generalized to focus on the underlying governance principles.

---

## Part 1: The Question BlackBox Couldn't Answer

It was two weeks after the invoice processing incident when the finance director walked into my office with a manila folder marked "Q4 SOX Audit Prep."

"Remember how we fixed the confidence threshold issue in 5 minutes using BlackBox?"

I nodded, still proud of that investigation. We'd traced 47 stuck invoices to a single parameter change—`confidence_threshold` bumped from 0.8 to 0.95—and resolved it before the $247,350 in pending payments triggered SLA penalties.

"Well, the external auditors have follow-up questions that your flight recorder can't answer."

She opened the folder and read from the auditor's preliminary inquiry:

1. "Which specific version of the invoice-extractor agent was running at the time of the incident?"
2. "What policies should have governed the confidence threshold parameter?"
3. "Who authorized the change from 0.8 to 0.95?"
4. "Can you demonstrate that this agent's configuration has not been tampered with since the incident?"
5. "Show us the complete governance history for SOX Section 404 compliance documentation."

I stared at my terminal. BlackBox had the execution traces—every API call, every decision, every timing metric. But these questions required something fundamentally different:

**BlackBox showed *what* happened. The auditors wanted to know *who was authorized* to make it happen and *what policies should have governed* the behavior.**

"We have three weeks before the audit," she said. "The external auditors are coming on-site. If we can't answer these questions, we're looking at a material weakness finding."

A material weakness. In public company terms, that's the difference between a clean audit and headlines about control failures. For our finance automation team, it could mean the end of our agent-based invoice processing program.

That night, I started researching how other high-stakes industries solve the identity and authorization problem. And I kept coming back to aviation.

---

## Part 2: Learning from Aviation (Streamlined)

In the [BlackBox Deep Dive](./blackbox_narrative_deepdive.md), we explored how aviation's flight data recorders inspired our execution tracing system. But aviation has another system we need to borrow: **pilot credentials**.

Before every commercial flight, airlines don't just verify that someone is in the cockpit—they verify *who* is in the cockpit, *what* they're certified to do, and *whether their certifications are current*. The parallel to our multi-agent finance system is direct:

| Aviation | Finance | AgentFacts |
|----------|---------|------------|
| Pilot Certificate Number | Trading License ID | `agent_id` |
| Full Legal Name | Agent Display Name | `agent_name` |
| Employing Airline | Responsible Team | `owner` |
| Type Rating (Boeing 737) | Product Authorization | `capabilities[]` |
| Medical Certificate Expiry | Policy Effectiveness | `policy.effective_until` |
| Operating Limitations | Approval Thresholds | `policies[]` |
| Security Hologram | Tamper Detection | `signature_hash` |
| Logbook | Audit Trail | `audit_trail[]` |

In finance, we have similar credential systems: Series 7 licenses for securities, Series 63 for state registration, trading authorizations with position limits. **Why shouldn't our AI agents have equivalent credentials?**

The insight that drove AgentFacts: every agent should carry verifiable credentials that prove:
- **Identity**: Who is this agent? (agent_id, version, owner)
- **Authorization**: What is it certified to do? (capabilities)
- **Constraints**: What rules govern its behavior? (policies)
- **Authenticity**: Has someone forged or tampered with these credentials? (signature_hash)

With this framework, we could answer the auditor's questions in seconds instead of three weeks of manual evidence gathering.

---

## Part 3: The Four Core Data Types (Finance Focus)

The AgentFacts system captures four distinct types of data. Let me show you how each maps to our invoice processing pipeline.

### 3.1 Capability: What the Agent Can Do

A **Capability** declares exactly what an agent is authorized to perform, with schemas defining the contract for inputs and outputs.

**Invoice Extractor Capabilities:**

```json
{
  "name": "extract_vendor",
  "description": "Extracts vendor information from invoice documents",
  "input_schema": {
    "type": "object",
    "properties": {
      "document_id": {"type": "string"},
      "document_type": {"type": "string", "enum": ["pdf", "image", "email"]},
      "ocr_confidence_threshold": {"type": "number", "minimum": 0.5, "maximum": 1.0}
    },
    "required": ["document_id"]
  },
  "output_schema": {
    "type": "object",
    "properties": {
      "vendor_name": {"type": "string"},
      "vendor_id": {"type": "string"},
      "confidence_score": {"type": "number"}
    }
  },
  "estimated_latency_ms": 500,
  "cost_per_call": 0.005,
  "requires_approval": false,
  "tags": ["extraction", "ocr", "vendor", "pci-dss"]
}
```

**Fraud Detector Capabilities:**

```json
{
  "name": "score_transaction",
  "description": "Calculates fraud risk score for financial transactions",
  "input_schema": {
    "type": "object",
    "properties": {
      "transaction_id": {"type": "string"},
      "amount": {"type": "number"},
      "merchant": {"type": "string"},
      "timestamp": {"type": "string", "format": "date-time"},
      "card_last_four": {"type": "string", "pattern": "^[0-9]{4}$"}
    },
    "required": ["transaction_id", "amount"]
  },
  "output_schema": {
    "type": "object",
    "properties": {
      "fraud_score": {"type": "number", "minimum": 0, "maximum": 1},
      "risk_level": {"type": "string", "enum": ["low", "medium", "high"]},
      "flags": {"type": "array", "items": {"type": "string"}}
    }
  },
  "estimated_latency_ms": 350,
  "cost_per_call": 0.01,
  "requires_approval": false,
  "tags": ["fraud", "ml", "real-time", "pci-dss"]
}
```

**Why Each Field Matters for Finance:**

| Field | SOX Relevance | PCI-DSS Relevance |
|-------|---------------|-------------------|
| `name` | Control identification | Scope boundary |
| `input_schema` | Data flow documentation | Cardholder data mapping |
| `output_schema` | Output classification | Data minimization proof |
| `requires_approval` | Segregation of duties | High-risk action gating |
| `tags` | Control categorization | Compliance scope tagging |

### 3.2 Policy: What Rules Govern the Agent

While Capabilities answer "What can this agent do?", **Policies** answer "What constraints govern its behavior?" For finance, three policy types cover most compliance requirements:

```
┌─────────────────────────────────────────────────────────────────┐
│                 FINANCE POLICY TYPES                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   rate_limit              data_access           approval_required│
│   ───────────             ───────────           ─────────────────│
│   "How often can         "What data can        "When does a human│
│    it be called?"         it access?"           need to approve?"│
│                                                                  │
│   SOX: Unusual            PCI-DSS: Card         SOX: Segregation │
│   activity detection      data restrictions     of duties        │
│                                                                  │
│   • max_calls_per_min    • card_data_access    • threshold_amount│
│   • max_calls_per_hour   • pii_handling_mode   • approval_role   │
│   • burst_limit          • audit_all_access    • max_pending_hrs │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

**Rate Limit Policy (Fraud Detector):**

```json
{
  "policy_id": "fraud-detector-v2-policy-001",
  "name": "High-Volume Rate Limit",
  "description": "Prevents runaway fraud scoring during incidents",
  "policy_type": "rate_limit",
  "constraints": {
    "max_calls_per_minute": 1000,
    "max_calls_per_hour": 50000,
    "burst_limit": 100,
    "alert_threshold_percent": 80
  },
  "effective_from": "2024-01-01T00:00:00+00:00",
  "effective_until": null,
  "is_active": true
}
```

**Data Access Policy (PCI-DSS Compliance):**

```json
{
  "policy_id": "invoice-extractor-v2-policy-002",
  "name": "PCI-DSS Data Handling",
  "description": "Restricts access to cardholder data per PCI-DSS 4.0",
  "policy_type": "data_access",
  "constraints": {
    "allowed_data_sources": ["invoice_db", "vendor_db"],
    "restricted_data_sources": ["cardholder_vault"],
    "pii_handling_mode": "tokenize",
    "card_data_access": "masked_only",
    "audit_all_access": true,
    "data_retention_days": 90
  },
  "effective_from": "2024-03-15T00:00:00+00:00",
  "effective_until": "2025-03-15T00:00:00+00:00",
  "is_active": true
}
```

**Approval Required Policy (Large Payments):**

```json
{
  "policy_id": "invoice-approver-v1-policy-001",
  "name": "CFO Approval for Large Payments",
  "description": "Payments over $100,000 require CFO sign-off",
  "policy_type": "approval_required",
  "constraints": {
    "threshold_amount": 100000,
    "approval_role": "cfo",
    "max_pending_hours": 4,
    "auto_escalate": true,
    "weekend_escalation_contact": "cfo-delegate@company.com"
  },
  "effective_from": "2024-01-01T00:00:00+00:00",
  "effective_until": null,
  "is_active": true
}
```

**The Critical Feature: Policy Effectiveness**

The `is_effective(at_time)` method prevents a dangerous gap—policies that have expired but no one noticed:

```python
def is_effective(self, at_time: datetime | None = None) -> bool:
    """Check if policy is effective at a given time."""
    check_time = at_time or datetime.now(UTC)
    if not self.is_active:
        return False
    if check_time < self.effective_from:
        return False
    if self.effective_until and check_time > self.effective_until:
        return False
    return True
```

During our audit prep, we discovered two expired policies:

```
⚠️  EXPIRED: PCI-DSS Data Handling
   Agent: Invoice Data Extractor
   Expired: 2025-03-15

⚠️  EXPIRED: User Data Access
   Agent: Product Recommendation Engine
   Expired: 2025-09-05
```

The agents kept working—they just weren't operating under the policies we assumed were active. Now we run automated policy expiration alerts.

### 3.3 AgentFacts: The Complete Identity Document

The **AgentFacts** model combines identity, capabilities, and policies into a single verifiable unit—the agent's "passport":

```python
class AgentFacts(BaseModel):
    # Identity
    agent_id: str                          # "invoice-extractor-v2"
    agent_name: str                        # "Invoice Data Extractor"
    owner: str                             # "finance-team"
    version: str                           # "1.5.4"
    description: str                       # Purpose description

    # Authorization
    capabilities: list[Capability]         # What it can do
    policies: list[Policy]                 # Rules governing it

    # Lifecycle
    created_at: datetime                   # Birth timestamp
    updated_at: datetime                   # Last modification

    # Hierarchy (optional)
    parent_agent_id: str | None            # For agent hierarchies

    # Tamper detection
    signature_hash: str                    # SHA256 of all fields

    # Extensions
    metadata: dict[str, Any]               # Custom fields
```

**Complete Invoice Extractor Identity:**

```json
{
  "agent_id": "invoice-extractor-v2",
  "agent_name": "Invoice Data Extractor",
  "owner": "finance-team",
  "version": "1.5.4",
  "description": "Extracts structured data from invoice documents using OCR and NLP",
  "capabilities": [
    {"name": "extract_vendor", "requires_approval": false, "...": "..."},
    {"name": "extract_line_items", "requires_approval": false, "...": "..."}
  ],
  "policies": [
    {"policy_id": "rate-limit-001", "policy_type": "rate_limit", "...": "..."},
    {"policy_id": "pci-dss-001", "policy_type": "data_access", "...": "..."}
  ],
  "created_at": "2024-01-15T10:00:00+00:00",
  "updated_at": "2024-11-27T02:15:00+00:00",
  "signature_hash": "ebd119247489871f9e2f8a7c3b4d5e6f...",
  "metadata": {
    "deployment_environment": "production",
    "model_version": "gpt-4-turbo",
    "sox_control_id": "FIN-AI-003"
  }
}
```

### 3.4 AuditEntry: The Immutable History

Every change to agent facts is recorded in an **AuditEntry**—an immutable log that survives even after an agent is unregistered. For SOX compliance, we retain these records for 7 years:

```python
class AuditEntry(BaseModel):
    timestamp: datetime                    # When the change occurred
    action: str                            # "register", "update", "verify", "unregister"
    changed_by: str                        # Who made the change (email, not team name)
    changes: dict[str, Any]                # What changed
    previous_signature: str | None         # Hash before change
    new_signature: str | None              # Hash after change
```

**Real Audit Trail from Invoice Extractor:**

```
📜 Invoice Data Extractor (5 entries)
──────────────────────────────────────────
  🆕 REGISTER by sarah.chen@finance-team.com
    Time: 2024-01-15 10:00:00 UTC
    Action: initial_registration
    Signature: a1b2c3d4e5f6...

  ✏️ UPDATE by mike.johnson@finance-team.com
    Time: 2024-06-20 14:30:00 UTC
    Changed: version (1.5.0 → 1.5.2), capabilities
    Previous Signature: a1b2c3d4e5f6...
    New Signature: b2c3d4e5f6a1...

  ✏️ UPDATE by compliance-bot@system
    Time: 2024-11-27 02:05:00 UTC
    Changed: capabilities[0].ocr_confidence_threshold (0.8 → 0.95)
    Previous Signature: b2c3d4e5f6a1...
    New Signature: c3d4e5f6a1b2...

  ✓ VERIFY by sox-audit-system
    Time: 2024-12-10 09:00:00 UTC
    Result: valid

  ✏️ UPDATE by sarah.chen@finance-team.com
    Time: 2024-12-10 09:15:00 UTC
    Changed: capabilities[0].ocr_confidence_threshold (0.95 → 0.8)
    Previous Signature: c3d4e5f6a1b2...
    New Signature: d4e5f6a1b2c3...
```

**The Critical Property: Audit Trails Survive Unregistration**

When an agent is removed from the registry, its audit trail is preserved. Auditors often ask about agents that no longer exist:

```python
# Agent was unregistered 6 months ago
agent = registry.get("legacy-validator-v1")  # Returns None

# But audit trail is still available for 7 years
audit = registry.audit_trail("legacy-validator-v1")  # Returns full history
```

---

## Part 4: Registry Architecture

The **AgentFactsRegistry** manages agent facts with persistent storage, automatic signature computation, and CRUD operations designed for compliance workflows.

### 4.1 The Dual Storage Pattern

Like our BlackBox recorder, AgentFacts uses dual storage—data lives both in memory (for fast access) and on disk (for durability):

```
┌─────────────────────────────────────────────────────────────────┐
│                   AGENTFACTS STORAGE ARCHITECTURE               │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   IN-MEMORY                              ON-DISK                │
│   ─────────                              ───────                │
│   self._agents: dict[str, AgentFacts]    cache/agent_facts/     │
│   self._audit_trails: dict[str, list]      ├── registry/        │
│                                            │   ├── agent-1.json │
│   Fast lookups: O(1)                       │   └── agent-2.json │
│   No persistence                           └── audit/           │
│                                                ├── agent-1.json │
│                                                └── ...          │
│                                                                 │
│   RETENTION: 7 years (SOX Section 404)                         │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 4.2 CRUD Operations Reference

| Operation | Method | Audit Action | SOX Relevance |
|-----------|--------|--------------|---------------|
| **Create** | `register(facts, by)` | `"register"` | Initial control deployment |
| **Read** | `get(agent_id)` | None | Runtime verification |
| **Update** | `update(id, changes, by)` | `"update"` | Change management evidence |
| **Delete** | `unregister(id, by)` | `"unregister"` | Decommission records |
| **Verify** | `verify(agent_id)` | `"verify"` | Integrity confirmation |
| **List** | `list_all()` | None | Control inventory |
| **Export** | `export_for_audit(ids, path)` | None | Audit evidence package |

### 4.3 Discovery Operations

```python
# Find all agents that can process invoices
invoice_agents = registry.find_by_capability("extract_vendor")

# Find all agents owned by finance team
finance_agents = registry.find_by_owner("finance-team")

# Get specific capabilities for an agent
caps = registry.get_capabilities("invoice-extractor-v2")

# Get active policies at a specific time (for historical audits)
historical_policies = agent.get_active_policies(
    at_time=datetime(2024, 11, 27, 2, 5, tzinfo=UTC)  # Time of incident
)
```

---

## Part 5: Tamper Detection Deep Dive

The signature verification system is the crown jewel of AgentFacts for finance. Let me walk you through a finance-specific tampering scenario.

### 5.1 The Finance Tampering Scenario

> **Important Caveat**: The in-record `signature_hash` is a *first-line defense* that detects accidental modifications and external API-level tampering. It does **not** protect against malicious actors with direct database access who can modify both data and recompute the signature. For production SOX compliance, see Section 5.3.1 on external hash storage.

Imagine a malicious actor modifies the invoice approver to increase the automatic approval limit—bypassing CFO review for large payments:

**Original Agent State:**

```python
agent = registry.get("invoice-approver-v1")
approval_policy = next(p for p in agent.policies if p.policy_type == "approval_required")

print(f"Max Auto-Approve: ${approval_policy.constraints['threshold_amount']:,}")
# Output: Max Auto-Approve: $100,000

print(f"Signature Valid: {agent.verify_signature()}")
# Output: Signature Valid: True
```

**Simulated Tampering (Bypassing Registry):**

```python
# Attacker modifies the agent directly, bypassing registry.update()
tampered_data = agent.model_dump()

# The attack: Raise auto-approval limit from $100K to $10M
for policy in tampered_data["policies"]:
    if policy["policy_type"] == "approval_required":
        policy["constraints"]["threshold_amount"] = 10000000  # $10M!

# Create agent from tampered data (keeps old signature)
tampered_agent = AgentFacts(**tampered_data)
```

**Detection:**

```python
print(f"Tampered Max Auto-Approve: ${tampered_agent.policies[0].constraints['threshold_amount']:,}")
# Output: Tampered Max Auto-Approve: $10,000,000

print(f"Stored Signature:   {tampered_agent.signature_hash[:40]}...")
# c8a3375b2cff2c51dd75f32e5cb4cfbb10b304b8...

print(f"Computed Signature: {tampered_agent.compute_signature()[:40]}...")
# 22f2ece68571a85deb48aa28ed78d32cb1c42271...  ← DIFFERENT!

print(f"Tampered Agent Valid: {tampered_agent.verify_signature()}")
# Output: False ← TAMPERING DETECTED!
```

**Alert Output:**

```
🚨 TAMPERING DETECTED - FINANCIAL CONTROL BYPASS 🚨

Agent: Invoice Payment Approver
Control: CFO Approval for Large Payments
SOX Control ID: FIN-AI-007

Original threshold_amount: $100,000
Tampered threshold_amount: $10,000,000

Stored Signature:   c8a3375b2cff2c51dd75f32e5cb4cfbb10b304b8...
Computed Signature: 22f2ece68571a85deb48aa28ed78d32cb1c42271...

IMMEDIATE ACTION REQUIRED:
- Agent execution blocked pending investigation
- SOX incident ticket created: SOX-2024-1127-001
- CFO and Internal Audit notified
```

### 5.2 Verification at Scale

For finance organizations with many agents, run batch verification:

```python
def verify_all_finance_agents(registry: AgentFactsRegistry) -> dict:
    """Verify all finance agents and report status."""
    results = {"valid": [], "invalid": [], "sox_controls": {}}

    for agent_id in registry.list_all():
        agent = registry.get(agent_id)
        if "finance" not in agent.owner:
            continue

        is_valid = registry.verify(agent_id)
        sox_id = agent.metadata.get("sox_control_id", "UNCLASSIFIED")

        if is_valid:
            results["valid"].append(agent_id)
        else:
            results["invalid"].append(agent_id)

        # Track by SOX control
        if sox_id not in results["sox_controls"]:
            results["sox_controls"][sox_id] = []
        results["sox_controls"][sox_id].append({
            "agent_id": agent_id,
            "valid": is_valid
        })

    return results

# Daily verification run
results = verify_all_finance_agents(registry)
print(f"Valid: {len(results['valid'])}")
print(f"Invalid: {len(results['invalid'])}")  # THESE NEED INVESTIGATION!
```

### 5.3 Security Limitations (Honest Disclosure)

> **Important for SOX Compliance**: The SHA256 signature provides **integrity verification**, not **cryptographic non-repudiation**. Auditors need to understand this distinction.

**What SHA256 Signature DOES Protect Against:**

| Threat | Protected? | Evidence Value |
|--------|------------|----------------|
| Accidental modifications | ✅ Yes | Configuration drift detection |
| Transmission corruption | ✅ Yes | Data integrity verification |
| Unauthorized edits without registry access | ✅ Yes | Audit trail gaps |
| Historical state verification | ✅ Yes | Point-in-time control status |

**What SHA256 Signature DOES NOT Protect Against:**

| Threat | Protected? | Mitigation |
|--------|------------|------------|
| Malicious actors with registry write access | ❌ No | RBAC + external audit logs |
| Insider threats with database access | ❌ No | Database-level controls |
| Replay attacks | ❌ No | Timestamp validation |

**Recommended Security Levels for Finance:**

| Requirement | Minimum Level | Implementation |
|-------------|---------------|----------------|
| Internal finance tools | Level 1 (RBAC) | Registry write access restricted |
| SOX Section 404 controls | Level 2 (Asymmetric) | RSA/ECDSA signatures with HSM |
| Payment authorization | Level 2 + External audit | Immutable external audit log |

### 5.3.1 External Hash Storage for True Immutability

> **Critical Implementation Detail**: The `signature_hash` stored within the AgentFacts record is a *convenience check*—it detects accidental modifications and external tampering. However, a malicious actor with database write access can modify both the data *and* recompute the signature.

For SOX Section 404 compliance, implement tiered storage with external baseline hashes:

```
┌─────────────────────────────────────────────────────────────────┐
│              TIERED SIGNATURE STORAGE ARCHITECTURE              │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   TIER 1: In-Record (Convenience)                              │
│   ─────────────────────────────────                            │
│   signature_hash in AgentFacts record                          │
│   • Fast verification: O(1) lookup                             │
│   • Detects: accidental modifications, API tampering           │
│   • Does NOT detect: database-level modifications              │
│                                                                 │
│   TIER 2: WORM Storage (Compliance)                            │
│   ─────────────────────────────────                            │
│   AWS S3 Object Lock / Azure Immutable Blob                    │
│   • Write-once, read-many: cannot be deleted or modified       │
│   • Store: {agent_id, timestamp, signature_hash}               │
│   • Compare against Tier 1 for tamper detection                │
│                                                                 │
│   TIER 3: External Audit Log (Evidence)                        │
│   ─────────────────────────────────────                        │
│   AWS CloudTrail / Splunk / database redo logs                 │
│   • Independent system outside your control                    │
│   • Provides third-party evidence for auditors                 │
│   • 7-year retention for SOX Section 802                       │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

**Implementation Pattern:**

```python
class ComplianceSignatureStore:
    """Store baseline hashes in WORM storage for tamper evidence."""

    def __init__(self, s3_client, bucket: str):
        self.s3 = s3_client
        self.bucket = bucket  # Configured with Object Lock

    def store_baseline(self, agent: AgentFacts) -> str:
        """Store immutable baseline hash after registration/update."""
        key = f"baselines/{agent.agent_id}/{datetime.now(UTC).isoformat()}.json"

        baseline = {
            "agent_id": agent.agent_id,
            "version": agent.version,
            "signature_hash": agent.signature_hash,
            "computed_at": datetime.now(UTC).isoformat(),
            "stored_by": "agentfacts-registry"
        }

        self.s3.put_object(
            Bucket=self.bucket,
            Key=key,
            Body=json.dumps(baseline),
            ObjectLockMode="GOVERNANCE",  # Requires special permissions to delete
            ObjectLockRetainUntilDate=datetime.now(UTC) + timedelta(days=2555)  # 7 years
        )
        return key

    def verify_against_baseline(self, agent: AgentFacts) -> tuple[bool, str]:
        """Compare current signature against immutable baseline."""
        # Get latest baseline for this agent
        response = self.s3.list_objects_v2(
            Bucket=self.bucket,
            Prefix=f"baselines/{agent.agent_id}/",
        )

        if not response.get("Contents"):
            return False, "No baseline found"

        latest_key = sorted(response["Contents"], key=lambda x: x["LastModified"])[-1]["Key"]
        baseline = json.loads(self.s3.get_object(Bucket=self.bucket, Key=latest_key)["Body"].read())

        if baseline["signature_hash"] != agent.signature_hash:
            return False, f"Signature mismatch: baseline={baseline['signature_hash'][:20]}..., current={agent.signature_hash[:20]}..."

        return True, "Signature matches immutable baseline"
```

**Verification Hierarchy for SOX Audits:**

| Check Level | Method | Evidence Value |
|-------------|--------|----------------|
| Level 1 | `agent.verify_signature()` | Internal consistency |
| Level 2 | Compare with WORM baseline | Tamper detection |
| Level 3 | Cross-reference CloudTrail | Third-party evidence |

**Production Enhancement: Asymmetric Signatures**

For SOX Section 404 compliance, consider asymmetric signatures where the private key is held by the security team:

```python
from cryptography.hazmat.primitives.asymmetric import rsa, padding

class SecureAgentFacts(AgentFacts):
    """AgentFacts with RSA signature for SOX compliance."""

    rsa_signature: bytes | None = None

    def sign_with_hsm(self, hsm_client: HSMClient) -> None:
        """Sign with private key in Hardware Security Module."""
        data = self.compute_signature().encode()
        self.rsa_signature = hsm_client.sign(data)

    def verify_with_public_key(self, public_key: rsa.RSAPublicKey) -> bool:
        """Verify with public key (available to all auditors)."""
        # Implementation details...
```

---

## Part 5.5: Policy Verification vs. Policy Enforcement

A critical distinction for compliance: **AgentFacts verifies what policies SHOULD govern an agent, but it doesn't enforce those policies at runtime.**

### 5.5.1 The Two-Layer Model

```
┌─────────────────────────────────────────────────────────────────┐
│                 POLICY: VERIFICATION vs. ENFORCEMENT            │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   AGENTFACTS (Verification Layer)                              │
│   ───────────────────────────────                              │
│   "What policies SHOULD govern this agent?"                    │
│                                                                 │
│   ✓ Declares approval_required: threshold = $100,000           │
│   ✓ Records data_access: card_data = masked_only               │
│   ✓ Documents rate_limit: max 1000 calls/minute                │
│   ✓ Exports evidence for SOX Section 404                       │
│                                                                 │
│   ✗ Does NOT block payments over threshold                     │
│   ✗ Does NOT mask card data automatically                      │
│   ✗ Does NOT enforce rate limits                               │
│                                                                 │
│   ─────────────────────────────────────────────────────────────│
│                                                                 │
│   GUARDRAILS (Enforcement Layer)                               │
│   ──────────────────────────────                               │
│   "Actually enforce constraints at runtime"                    │
│                                                                 │
│   ✓ Validates payment amounts against threshold                │
│   ✓ Detects and masks card numbers in outputs                  │
│   ✓ Rejects/escalates based on policy violations              │
│   ✓ Generates validation traces for audit                      │
│                                                                 │
│   Integration: GuardRails reads constraints FROM AgentFacts    │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 5.5.2 Why Separate Verification from Enforcement?

**For SOX Compliance:**
- Auditors need to see what policies WERE declared, even if enforcement failed
- "What should have happened?" vs. "What actually happened?"
- Design control (AgentFacts) vs. Operating control (GuardRails)

**For PCI-DSS:**
- Requirement 3.4: Render PAN unreadable (enforcement)
- Requirement 12.3: Usage policies must be documented (verification)

### 5.5.3 The Complete Enforcement Stack for Finance

| Policy Type | AgentFacts Role | Enforcement Mechanism |
|-------------|-----------------|----------------------|
| `rate_limit` | Declares limits | Redis rate limiter + middleware |
| `data_access` | Declares PCI-DSS rules | GuardRails PAN detection + tokenization |
| `approval_required` | Declares thresholds | Workflow engine + CFO queue |

### 5.5.4 Policy Synchronization Strategy

> **Critical Operational Risk**: What happens if AgentFacts declares a new policy constraint, but GuardRails is still enforcing the old one? For compliance, you need to prove not just what *should* have happened, but what *actually was enforced*.

**The Synchronization Problem:**

```
┌─────────────────────────────────────────────────────────────────┐
│              POLICY SYNCHRONIZATION TIMELINE                    │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   T=0: Policy updated in AgentFacts Registry                   │
│         threshold_amount: $100,000 → $50,000                   │
│                                                                 │
│   T=1: GuardRails Service A receives pub/sub notification      │
│         Refreshes policy cache ✓                               │
│                                                                 │
│   T=2: GuardRails Service B (network hiccup)                   │
│         Still using cached $100,000 threshold ✗                │
│                                                                 │
│   T=3: $75,000 payment processed by Service B                  │
│         APPROVED (should have been BLOCKED!)                   │
│                                                                 │
│   COMPLIANCE GAP: Policy declared ≠ Policy enforced            │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

**Synchronization Strategies:**

| Strategy | Latency | Consistency | Use Case |
|----------|---------|-------------|----------|
| Per-call lookup | ~5-10ms | Strong | High-value transactions (>$100K) |
| TTL cache (60s) | ~0ms | Eventual | High-volume, low-risk operations |
| Pub/sub invalidation | ~50ms | Near-strong | Balanced production workloads |
| Hybrid | Varies | Configurable | Finance recommendation |

**Recommended: Hybrid Approach**

```python
class PolicyEnforcementCache:
    """Hybrid cache with per-call verification for high-risk operations."""

    def __init__(self, registry: AgentFactsRegistry, redis_client):
        self.registry = registry
        self.redis = redis_client
        self.ttl_seconds = 60
        self.high_value_threshold = 100000

    async def get_active_policies(
        self,
        agent_id: str,
        transaction_amount: float | None = None
    ) -> list[Policy]:
        """Get policies with appropriate consistency level."""

        # High-value transactions: always fetch fresh
        if transaction_amount and transaction_amount >= self.high_value_threshold:
            return self._fetch_fresh(agent_id)

        # Check cache first
        cached = await self.redis.get(f"policies:{agent_id}")
        if cached:
            policies = json.loads(cached)
            # Validate cache isn't stale (pub/sub might have invalidated)
            if not await self.redis.exists(f"invalidated:{agent_id}"):
                return [Policy(**p) for p in policies]

        # Cache miss or invalidated: fetch fresh
        return await self._fetch_and_cache(agent_id)

    async def _fetch_fresh(self, agent_id: str) -> list[Policy]:
        """Direct registry lookup for critical operations."""
        agent = self.registry.get(agent_id)
        if not agent:
            raise AgentNotFoundError(agent_id)
        return agent.get_active_policies()

    async def _fetch_and_cache(self, agent_id: str) -> list[Policy]:
        """Fetch from registry and update cache."""
        policies = await self._fetch_fresh(agent_id)
        await self.redis.setex(
            f"policies:{agent_id}",
            self.ttl_seconds,
            json.dumps([p.model_dump() for p in policies])
        )
        await self.redis.delete(f"invalidated:{agent_id}")
        return policies

    async def invalidate(self, agent_id: str) -> None:
        """Called by pub/sub when registry is updated."""
        await self.redis.set(f"invalidated:{agent_id}", "1", ex=self.ttl_seconds)
```

**Enforcement Logging for Audit Trail:**

GuardRails must log which policy version it enforced (this becomes BlackBox data):

```python
@dataclass
class EnforcementRecord:
    """Record of policy enforcement for audit trail."""
    timestamp: datetime
    agent_id: str
    policy_id: str
    policy_signature: str          # Hash of policy at enforcement time
    constraint_checked: str        # e.g., "threshold_amount"
    constraint_value: Any          # e.g., 50000
    input_value: Any               # e.g., 75000 (the payment amount)
    decision: str                  # "BLOCKED" | "APPROVED" | "ESCALATED"
    cache_hit: bool                # Was this from cache or fresh lookup?
    fetch_latency_ms: float        # Time to get policy
```

This record proves: "At T=3, Service B enforced policy XYZ with threshold $100,000"—which exposes the synchronization gap for investigation.

**Example: Full Enforcement for Invoice Approval**

```python
# 1. Check policy is active (AgentFacts - verification)
agent = registry.get("invoice-approver-v1")
approval_policy = next(
    (p for p in agent.get_active_policies() if p.policy_type == "approval_required"),
    None
)
if not approval_policy:
    raise PolicyViolation("Approval policy not active!")

# 2. Check if amount exceeds threshold
invoice_amount = 150000  # $150,000
threshold = approval_policy.constraints["threshold_amount"]

if invoice_amount > threshold:
    # 3. Route to approval queue (enforcement)
    approval_id = workflow.create_approval_request(
        amount=invoice_amount,
        approver_role=approval_policy.constraints["approval_role"],
        max_pending_hours=approval_policy.constraints["max_pending_hours"]
    )

    # 4. Log for audit (both systems)
    recorder.log_approval_required(agent.agent_id, invoice_amount, threshold)
    registry.verify(agent.agent_id)  # Integrity check
```

---

## Part 6: The SOX Audit Revisited

Three weeks after the initial conversation, the external auditors arrived. Here's how AgentFacts changed the audit from a multi-day evidence gathering exercise to a two-minute demonstration.

### 6.1 The Original Questions—Answered

**Auditor Question 1**: "Which specific version of the invoice-extractor agent was running at the time of the incident?"

```python
agent = registry.get("invoice-extractor-v2")
print(f"Agent: {agent.agent_name}")
print(f"Version: {agent.version}")
print(f"Owner: {agent.owner}")
# Output:
# Agent: Invoice Data Extractor
# Version: 1.5.4
# Owner: finance-team
```

**Auditor Question 2**: "What policies should have governed the confidence threshold parameter?"

```python
# Get policies active at incident time
incident_time = datetime(2024, 11, 27, 2, 5, tzinfo=UTC)
active_policies = agent.get_active_policies(at_time=incident_time)

for policy in active_policies:
    print(f"- {policy.name} ({policy.policy_type})")
    print(f"  Constraints: {policy.constraints}")
# Output:
# - API Rate Limit (rate_limit)
#   Constraints: {'max_calls_per_minute': 500, 'burst_limit': 50}
# - PCI-DSS Data Handling (data_access)
#   Constraints: {'pii_handling_mode': 'tokenize', 'audit_all_access': True}
```

**Auditor Question 3**: "Who authorized the change from 0.8 to 0.95?"

```python
audit = registry.audit_trail("invoice-extractor-v2")
threshold_change = next(
    e for e in audit
    if "confidence_threshold" in str(e.changes)
)
print(f"Changed by: {threshold_change.changed_by}")
print(f"Timestamp: {threshold_change.timestamp}")
# Output:
# Changed by: compliance-bot@system
# Timestamp: 2024-11-27 02:05:00 UTC
```

**Auditor Question 4**: "Can you demonstrate that this agent's configuration has not been tampered with since the incident?"

```python
is_valid = registry.verify("invoice-extractor-v2")
print(f"Signature Valid: {is_valid}")
# Output: Signature Valid: True
```

**Auditor Question 5**: "Show us the complete governance history for SOX Section 404 compliance documentation."

```python
# Export complete audit package
registry.export_for_audit(
    agent_ids=["invoice-extractor-v2", "invoice-approver-v1"],
    filepath=Path("audits/sox-2024-q4-finance-agents.json")
)
print("Exported to: audits/sox-2024-q4-finance-agents.json")
```

### 6.2 Time Comparison

> **Baseline Assumptions**: The "Without AgentFacts" column assumes a typical enterprise environment with:
> - Decentralized configuration management (configs scattered across repos, environment variables, and config files)
> - Standard deployment logging (CI/CD logs exist but require manual correlation)
> - No dedicated agent registry or governance tooling
>
> Organizations with mature GitOps, infrastructure-as-code, and centralized configuration management may see smaller time savings (perhaps 1-2 hours without vs. 2 minutes with). The key differentiator is **tamper verification**—which remains impossible to prove without signature-based systems.

| Task | Without AgentFacts | With AgentFacts |
|------|-------------------|-----------------|
| Find agent version at incident time | 2 hours (git blame, deploy logs) | 5 seconds |
| List governing policies | 4 hours (config file archaeology) | 10 seconds |
| Identify who made the change | 3 hours (correlate logs) | 10 seconds |
| Verify no tampering | Impossible to prove | 2 seconds |
| Export audit evidence | 8 hours (manual compilation) | 30 seconds |
| **Total** | **17+ hours** | **< 2 minutes** |

The auditors noted in their report: "The finance-automation-team demonstrated effective IT general controls for AI agent governance, with automated evidence generation meeting SOX Section 404 requirements."

---

## Part 7: The Governance Triangle Complete

With BlackBox, AgentFacts, and GuardRails together, we have a complete governance stack for AI agents in finance:

```
                     ┌─────────────┐
                     │  AgentFacts │
                     │  (WHO)      │
                     │             │
                     │  Identity   │
                     │  Capability │
                     │  Policy     │
                     └──────┬──────┘
                            │
              ┌─────────────┼─────────────┐
              │             │             │
              ▼             │             ▼
       ┌─────────────┐      │      ┌─────────────┐
       │  BlackBox   │      │      │  GuardRails │
       │  (WHAT)     │◄─────┴─────►│  (VALID?)   │
       │             │             │             │
       │  Timeline   │             │  Constraints│
       │  Decisions  │             │  PCI-DSS    │
       │  Parameters │             │  Validation │
       └─────────────┘             └─────────────┘

       Together, they answer:
       "WHO did WHAT, and was it VALID?"
```

### 7.1 The Invoice Processing Pipeline—Governed

Returning to the November 27 incident, here's how all three systems work together:

| Time | Event | BlackBox | AgentFacts | GuardRails |
|------|-------|----------|------------|------------|
| 02:05 | Config change | Records parameter change | Logs who made change | N/A |
| 02:06 | Invoice 47 processed | Traces low confidence | Verifies agent authorized | Checks PCI-DSS |
| 02:07 | Invoice stuck | Records PENDING state | Shows active policies | Validates output |
| 02:10 | Alert triggered | Shows stuck queue | Links to owner | N/A |
| 09:00 | Investigation | Provides timeline | Proves no tampering | Shows validations |

### 7.2 Audit Evidence Generation

For quarterly SOX audits, we now generate comprehensive evidence packages:

```python
def generate_sox_evidence_package(
    quarter: str,
    registry: AgentFactsRegistry,
    recorder: BlackBoxRecorder
) -> Path:
    """Generate SOX Section 404 evidence package."""

    # All finance agents
    finance_agents = registry.find_by_owner("finance-team")
    agent_ids = [a.agent_id for a in finance_agents]

    # Export AgentFacts with audit trails
    registry.export_for_audit(
        agent_ids=agent_ids,
        filepath=Path(f"audits/sox-{quarter}-agentfacts.json")
    )

    # Export BlackBox traces for the quarter
    # (implementation in BlackBox module)

    return Path(f"audits/sox-{quarter}/")
```

---

## Part 8: Finance Best Practices

Building and deploying AgentFacts in a finance environment taught us several lessons.

### 8.1 SOX 7-Year Retention Policy

SOX Section 802 requires 7-year retention for audit evidence. Implement tiered retention:

```python
RETENTION_POLICY = {
    "sox_controls": 2555,      # 7 years (SOX Section 802)
    "pci_dss_controls": 365,   # 1 year (PCI-DSS Requirement 10.7)
    "operational": 90,          # 90 days (internal policy)
}

def get_retention_days(agent: AgentFacts) -> int:
    """Determine retention period based on agent policies."""
    if agent.metadata.get("sox_control_id"):
        return RETENTION_POLICY["sox_controls"]
    if any("pci" in p.name.lower() for p in agent.policies):
        return RETENTION_POLICY["pci_dss_controls"]
    return RETENTION_POLICY["operational"]
```

### 8.2 Individual Accountability

Register agents with individual owners, not team names. Use employee IDs that survive email changes, departures, and organizational restructuring:

```python
# ❌ Bad: No individual accountability
agent.owner = "finance-team"

# ❌ Fragile: Email addresses change when employees leave or names change
agent.owner = "sarah.chen@finance-team.com"

# ✅ Better: Employee ID with denormalized display info
agent.owner = "EMP-12345"  # Stable identifier from HR system
agent.metadata["owner_display"] = "Sarah Chen"  # For UI, may be stale
agent.metadata["owner_resolver"] = "ldap://directory.company.com"  # For fresh lookup
agent.metadata["team"] = "finance-team"
agent.metadata["sox_control_owner"] = "EMP-00001"  # CFO employee ID

# ✅ Best: Structured owner with automatic validation
@dataclass
class AgentOwnership:
    """Structured owner reference with validation."""
    primary_owner_id: str           # Employee ID (required)
    backup_owner_id: str            # Backup if primary leaves
    team_id: str                    # Team identifier
    sox_control_owner_id: str       # Ultimate accountability
    last_validated: datetime        # When ownership was verified
    validation_source: str          # "ldap" | "manual" | "hr_sync"

# Validate ownership on agent load
def validate_ownership(agent: AgentFacts, hr_service: HRService) -> bool:
    """Check if owner still exists and is active."""
    owner_id = agent.owner
    employee = hr_service.get_employee(owner_id)

    if not employee:
        logger.warning(f"Agent {agent.agent_id} owner {owner_id} not found in HR")
        return False
    if employee.status != "active":
        logger.warning(f"Agent {agent.agent_id} owner {owner_id} is {employee.status}")
        return False

    return True
```

**Orphan Agent Detection:**

Run weekly to find agents whose owners have left:

```python
def find_orphaned_agents(registry: AgentFactsRegistry, hr_service: HRService) -> list[str]:
    """Find agents with inactive or missing owners."""
    orphans = []
    for agent_id in registry.list_all():
        agent = registry.get(agent_id)
        if not validate_ownership(agent, hr_service):
            orphans.append(agent_id)
    return orphans
```

### 8.3 Policy Expiration Monitoring

Run automated policy expiration alerts:

```python
def check_expiring_policies(registry: AgentFactsRegistry, days_ahead: int = 30) -> list:
    """Find policies expiring within the specified timeframe."""
    warning_date = datetime.now(UTC) + timedelta(days=days_ahead)
    expiring = []

    for agent_id in registry.list_all():
        for policy in registry.get_policies(agent_id):
            if policy.effective_until and policy.effective_until < warning_date:
                expiring.append({
                    "agent_id": agent_id,
                    "policy_name": policy.name,
                    "sox_control_id": registry.get(agent_id).metadata.get("sox_control_id"),
                    "expires": policy.effective_until,
                    "days_remaining": (policy.effective_until - datetime.now(UTC)).days
                })

    return sorted(expiring, key=lambda x: x["days_remaining"])
```

### 8.4 Real-Time Verification for High-Value Transactions

For transactions over $100,000, verify agent integrity before execution:

```python
async def process_high_value_payment(
    payment: Payment,
    registry: AgentFactsRegistry
) -> PaymentResult:
    """Process payment with real-time agent verification."""

    if payment.amount >= 100000:
        # Verify agent integrity
        if not registry.verify("invoice-approver-v1"):
            raise SecurityException(
                "Agent integrity check failed for high-value transaction"
            )

        # Verify approval policy is active
        agent = registry.get("invoice-approver-v1")
        approval_policy = next(
            (p for p in agent.get_active_policies()
             if p.policy_type == "approval_required"),
            None
        )
        if not approval_policy:
            raise PolicyException(
                "Approval policy not active for high-value transaction"
            )

    return await execute_payment(payment)
```

### 8.5 Capability Schema Validation

Ensure declared capabilities match actual behavior:

```python
import jsonschema

def validate_capability_contract(
    agent: AgentFacts,
    capability_name: str,
    actual_input: dict,
    actual_output: dict
) -> tuple[bool, list[str]]:
    """Validate that actual I/O matches declared schemas."""
    cap = agent.get_capability(capability_name)
    if not cap:
        return False, [f"Capability {capability_name} not declared"]

    errors = []

    try:
        jsonschema.validate(actual_input, cap.input_schema)
    except jsonschema.ValidationError as e:
        errors.append(f"Input schema violation: {e.message}")

    try:
        jsonschema.validate(actual_output, cap.output_schema)
    except jsonschema.ValidationError as e:
        errors.append(f"Output schema violation: {e.message}")

    return len(errors) == 0, errors
```

### 8.6 Break Glass Procedures

For production incidents requiring temporary policy bypass, implement structured emergency overrides with mandatory audit trails:

```
┌─────────────────────────────────────────────────────────────────┐
│              BREAK GLASS PROCEDURE FLOW                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   1. INITIATE                                                   │
│      ─────────                                                  │
│      • Incident ticket required (e.g., INC-2024-1127)          │
│      • Requestor identifies specific policy to bypass          │
│      • Business justification documented                        │
│                                                                 │
│   2. APPROVE (Two-Person Rule)                                  │
│      ─────────                                                  │
│      • Primary approver: On-call manager                       │
│      • Secondary approver: Security team member                │
│      • Both approvals logged in audit trail                    │
│                                                                 │
│   3. EXECUTE                                                    │
│      ─────────                                                  │
│      • Create emergency_override audit entry                   │
│      • Set policy.is_active = False                            │
│      • Set auto-restore timer (default: 4 hours)               │
│                                                                 │
│   4. RESTORE                                                    │
│      ─────────                                                  │
│      • Auto-restore after expiry                               │
│      • Extension requires re-approval                          │
│      • Post-incident review mandatory                          │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

**Implementation:**

```python
@dataclass
class EmergencyOverride:
    """Temporary policy bypass with mandatory audit trail."""
    override_id: str
    incident_ticket: str           # Required: INC-2024-1127
    agent_id: str
    policy_id: str
    justification: str
    requestor_id: str              # Employee ID
    primary_approver_id: str       # On-call manager
    secondary_approver_id: str     # Security team member
    created_at: datetime
    expires_at: datetime           # Auto-restore time
    extended_count: int = 0        # Track extensions for review
    max_extensions: int = 2        # Limit extensions

class BreakGlassManager:
    """Manage emergency policy overrides with compliance controls."""

    def __init__(self, registry: AgentFactsRegistry, max_duration_hours: int = 4):
        self.registry = registry
        self.max_duration = timedelta(hours=max_duration_hours)
        self.active_overrides: dict[str, EmergencyOverride] = {}

    def request_override(
        self,
        agent_id: str,
        policy_id: str,
        incident_ticket: str,
        justification: str,
        requestor_id: str,
        primary_approver_id: str,
        secondary_approver_id: str
    ) -> EmergencyOverride:
        """Create emergency override with two-person approval."""

        # Validate all required fields
        if not incident_ticket.startswith("INC-"):
            raise ValueError("Valid incident ticket required (format: INC-YYYY-MMDD)")
        if requestor_id == primary_approver_id or requestor_id == secondary_approver_id:
            raise ValueError("Requestor cannot be their own approver")
        if primary_approver_id == secondary_approver_id:
            raise ValueError("Two different approvers required")

        override = EmergencyOverride(
            override_id=f"OVR-{datetime.now(UTC).strftime('%Y%m%d%H%M%S')}",
            incident_ticket=incident_ticket,
            agent_id=agent_id,
            policy_id=policy_id,
            justification=justification,
            requestor_id=requestor_id,
            primary_approver_id=primary_approver_id,
            secondary_approver_id=secondary_approver_id,
            created_at=datetime.now(UTC),
            expires_at=datetime.now(UTC) + self.max_duration
        )

        # Deactivate policy
        self.registry.update(
            agent_id,
            changes={
                "policies": self._deactivate_policy(agent_id, policy_id)
            },
            by=f"break-glass:{override.override_id}"
        )

        # Record in audit trail
        self.registry._add_audit_entry(
            agent_id,
            action="emergency_override",
            changed_by=requestor_id,
            changes={
                "override_id": override.override_id,
                "incident_ticket": incident_ticket,
                "policy_id": policy_id,
                "justification": justification,
                "approvers": [primary_approver_id, secondary_approver_id],
                "expires_at": override.expires_at.isoformat()
            }
        )

        self.active_overrides[override.override_id] = override
        logger.warning(f"BREAK GLASS ACTIVATED: {override.override_id} for {agent_id}/{policy_id}")
        return override

    def restore_policy(self, override_id: str) -> None:
        """Restore policy after override expires or is manually ended."""
        override = self.active_overrides.get(override_id)
        if not override:
            raise ValueError(f"Override {override_id} not found or already restored")

        # Reactivate policy
        self.registry.update(
            override.agent_id,
            changes={
                "policies": self._reactivate_policy(override.agent_id, override.policy_id)
            },
            by=f"break-glass-restore:{override_id}"
        )

        # Record restoration
        self.registry._add_audit_entry(
            override.agent_id,
            action="emergency_override_restored",
            changed_by="system",
            changes={
                "override_id": override_id,
                "duration_minutes": (datetime.now(UTC) - override.created_at).total_seconds() / 60,
                "was_auto_restore": datetime.now(UTC) >= override.expires_at
            }
        )

        del self.active_overrides[override_id]
        logger.info(f"BREAK GLASS RESTORED: {override_id}")

    def extend_override(self, override_id: str, approver_id: str) -> EmergencyOverride:
        """Extend override duration (requires re-approval)."""
        override = self.active_overrides.get(override_id)
        if not override:
            raise ValueError(f"Override {override_id} not found")
        if override.extended_count >= override.max_extensions:
            raise ValueError(f"Maximum extensions ({override.max_extensions}) reached")

        override.expires_at = datetime.now(UTC) + self.max_duration
        override.extended_count += 1

        self.registry._add_audit_entry(
            override.agent_id,
            action="emergency_override_extended",
            changed_by=approver_id,
            changes={
                "override_id": override_id,
                "new_expires_at": override.expires_at.isoformat(),
                "extension_count": override.extended_count
            }
        )

        return override
```

**Post-Incident Review:**

All emergency overrides require post-incident review within 5 business days:

```python
def generate_override_review_report(override: EmergencyOverride) -> dict:
    """Generate post-incident review report for compliance."""
    return {
        "override_id": override.override_id,
        "incident_ticket": override.incident_ticket,
        "duration_hours": (override.expires_at - override.created_at).total_seconds() / 3600,
        "extensions_used": override.extended_count,
        "review_questions": [
            "Was the override necessary? Could the incident have been resolved differently?",
            "Should the policy be permanently modified based on this incident?",
            "Were the approval controls followed correctly?",
            "What preventive measures would avoid future overrides?"
        ],
        "compliance_notes": "Review must be completed within 5 business days per SOX-ITGC-007"
    }
```

---

## Part 9: Reflections and Key Takeaways

Building AgentFacts for our finance automation team transformed how we approach AI governance. Here's what I've learned.

### 9.1 The Mental Model

**Think of AgentFacts as the Series 7 license for AI agents:**

| Financial License | AgentFacts |
|-------------------|------------|
| License Number | `agent_id` |
| Holder Name | `agent_name` |
| Sponsoring Firm | `owner` |
| Product Authorizations | `capabilities` |
| Trading Limits | `policies` |
| Expiration Date | `policy.effective_until` |
| FINRA Central Registration | `signature_hash` |
| U4/U5 History | `audit_trail` |

Just as you wouldn't let an unregistered representative execute trades, you shouldn't let an unverified AI agent process financial transactions.

### 9.2 Before/After Comparison

| Question | Before AgentFacts | After AgentFacts |
|----------|-------------------|------------------|
| "Which agent version processed this invoice?" | 2 hours (deploy logs) | `agent.version` → "1.5.4" |
| "What policies governed the threshold change?" | 4 hours (config archaeology) | `agent.get_active_policies()` → instant |
| "Who authorized this configuration?" | 3 hours (log correlation) | `audit_trail` → email address |
| "Has anyone tampered with controls?" | Impossible to prove | `verify()` → True/False |
| "Generate SOX evidence package" | 8 hours | `export_for_audit()` → 30 seconds |

### 9.3 The Complete Governance Stack

For financial services AI, you need three systems working together:

1. **BlackBox** (Part 1): "What happened?" — Execution traces, timing, decisions
2. **AgentFacts** (Part 2): "Who was authorized?" — Identity, capabilities, policies
3. **GuardRails** (Part 3): "Was it valid?" — Runtime constraint enforcement

Together, they provide the evidence chain that auditors need: **WHO** did **WHAT**, and was it **VALID**?

### 9.4 When You Really Need AgentFacts

**Essential for:**
- SOX Section 404 compliance (IT general controls)
- PCI-DSS scope documentation
- High-value transaction authorization
- Segregation of duties evidence
- Change management audit trails

**Optional for:**
- Development/testing environments
- Low-risk internal tools
- Non-regulated operations

### 9.5 Future Topics (Out of Scope for This Article)

This article focused on the AgentFacts data model, registry operations, and compliance patterns. Several important topics are intentionally deferred to future articles:

| Topic | Planned Coverage | Why Deferred |
|-------|------------------|--------------|
| **Deployment Architecture** | Part 4: AgentFacts Operations | Registry deployment, redundancy, failover, backup strategies |
| **GuardRails Enforcement** | Part 3: GuardRails Validation | Runtime policy enforcement, PAN detection, validation traces |
| **Scale Analysis** | Implementation Guide | Performance benchmarks, cache strategies, sharding for 10K+ agents |
| **Access Control Model** | Part 4: AgentFacts Operations | RBAC for registry, policy change workflows, segregation of duties |
| **Testing Strategy** | Implementation Guide | Contract testing for capabilities, policy compliance testing |
| **Multi-Region Consistency** | Part 4: AgentFacts Operations | Cross-datacenter synchronization, eventual consistency trade-offs |
| **Migration from Legacy** | Implementation Guide | Gradual adoption, grandfathering existing agents, parallel running |

**Article Roadmap:**

```
Part 1: BlackBox Recording ✓
    └── "What happened?" — Execution traces, timing, decisions

Part 2: AgentFacts Governance ✓ (This Article)
    └── "Who was authorized?" — Identity, capabilities, policies

Part 3: GuardRails Validation (Coming Soon)
    └── "Was it valid?" — Runtime enforcement, PCI-DSS compliance

Part 4: AgentFacts Operations (Planned)
    └── "How do we run it?" — Deployment, access control, organizational workflows
```

### 9.6 The Audit Outcome

That SOX audit that started this journey? The external auditors noted:

> "The organization demonstrated effective design and operating effectiveness of IT general controls for AI agent governance. The AgentFacts registry provides verifiable evidence of agent identity, authorization, and change history meeting SOX Section 404 requirements. No material weaknesses identified."

**Time to answer "Who authorized this change?": 10 seconds.**

**Time to verify agent integrity: 2 seconds.**

**Time to export SOX evidence package: 30 seconds.**

Build your agent registry. Your auditors (and your CFO) will thank you.

---

## References

**Implementation:**
- [`lesson-17/backend/explainability/agent_facts.py`](../backend/explainability/agent_facts.py) — Complete AgentFacts implementation (650 lines)
- [`lesson-17/data/agent_metadata_10.json`](../data/agent_metadata_10.json) — Synthetic dataset with 10 agents

**Related Articles (BlackBox Series):**
- [Part 1: BlackBox Recording Deep Dive](./blackbox_narrative_deepdive.md) — The "What Happened" flight recorder
- Part 3: GuardRails Validation (coming soon) — The "Was It Valid" enforcement layer

**Interactive Demo:**
- [`lesson-17/notebooks/02_agent_facts_verification.ipynb`](../notebooks/02_agent_facts_verification.ipynb) — Hands-on notebook with tamper detection

**Compliance Standards:**
- SOX Section 404 — IT General Controls
- SOX Section 802 — 7-Year Retention Requirements
- PCI-DSS 4.0 — Requirements 3, 10, 12

**Research:**
- arXiv:2506.13794 — AgentFacts: Verifiable Metadata for AI Agents

---

*Article created: 2025-11-29*
*Part 2 of the BlackBox Explainability Series*
*Author: Rajnish Khatri*
*Word Count: ~4,500 words (plus code examples)*
*Reading Time: ~25 minutes*
