# Plan: AgentFacts Finance Deep Dive (Part 2 of BlackBox Series)

**Created:** 2025-11-29
**Status:** ✅ Completed - Article created at `agentfacts_governance_finance.md`

---

## Context

This article is **Part 2 of the BlackBox narrative series**, continuing from `blackbox_narrative_deepdive.md`.

### Part 1 Summary (BlackBox Deep Dive)
- **Opening Incident:** 2:05 AM, November 27, 2024 - 47 invoices stuck in processing
- **Domain:** Invoice processing, finance operations
- **Primary Agent:** `invoice-extractor-v2` version 2.3.1
- **Supporting Agents:** `invoice-validator-v1`, `invoice-approver-v1`
- **Root Cause:** `confidence_threshold` changed from 0.8 → 0.95
- **Business Impact:** $247,350 stuck, SLA at risk, vendor relationships affected
- **Owner:** `finance-automation-team`
- **Resolution:** 5 minutes to root cause (vs 3 hours without BlackBox)
- **Word Count:** ~9,500 words, 45-minute read

### Part 2 Narrative Hook
Two weeks after the invoice incident, the finance director faces a quarterly **SOX Section 404 audit**. The auditor asks questions that BlackBox *cannot* answer:

- "Who authorized that parameter change?"
- "What policies should have prevented a 95% threshold?"
- "Has this agent been tampered with since deployment?"
- "Show me the complete governance history for compliance."

This gap leads to building **AgentFacts** - the agent credential/identity system.

---

## Critique of Original AgentFacts Article

The original `agentfacts_governance_deepdive.md` has these issues:

| Issue | Problem | Impact |
|-------|---------|--------|
| **Domain Scattering** | Jumps between healthcare (HIPAA), finance (fraud), legal (contracts), research | Reader context-switching overhead |
| **Healthcare Dominance** | ~60% examples are medical (patient #47829, physician approval, HIPAA) | Finance readers mentally translate every example |
| **Repetitive Aviation Analogy** | Pilot/driver's license mentioned 5+ times | Diminishing returns after Part 2 |
| **Excessive Length** | ~12,000 words, 55-minute read | Practitioners may abandon |
| **Generic Code Examples** | Uses `diagnosis-generator-v1` | No cohesive domain narrative |
| **Missing Finance Depth** | Surface-level SOX, PCI-DSS, AML treatment | Finance practitioners need deeper regulatory context |

---

## Target Article

### File Location
```
lesson-17/articles/agentfacts_governance_finance.md
```

### Target Metrics
- **Word Count:** ~7,000 words
- **Reading Time:** 35 minutes
- **Domain:** Finance only (no healthcare)
- **Primary Agent:** `invoice-extractor-v2` (same as Part 1)
- **Compliance Focus:** SOX Section 404, PCI-DSS 4.0, AML/KYC

---

## Article Structure

### Part 1: The Question BlackBox Couldn't Answer (~700 words)
- Pick up 2 weeks after the invoice incident
- Same finance director, quarterly SOX Section 404 audit
- Auditor asks: "Show me which version of invoice-extractor-v2 was running, what policies governed it, and who authorized the confidence threshold change"
- BlackBox shows *what* happened, but not *who was authorized* or *what policies should have governed*
- This gap leads to building AgentFacts

**Opening Hook:**
```
It was two weeks after the invoice processing incident when the finance director
walked into my office with a manila folder marked "Q4 SOX Audit Prep."

"Remember how we fixed the confidence threshold issue in 5 minutes using BlackBox?"

I nodded, still proud of that investigation.

"Well, the external auditors have follow-up questions that your flight recorder
can't answer..."
```

### Part 2: Learning from Aviation (Streamlined) (~600 words)
- Same aviation credential analogy, but mapped to finance
- Series 7/63 licenses, trading authorizations → agent capabilities
- Single table: Aviation → Finance → AgentFacts
- Keep shorter since Part 1 established the aviation metaphor

**Key Table:**
| Aviation | Finance | AgentFacts |
|----------|---------|------------|
| Pilot Certificate Number | Trading License ID | `agent_id` |
| Type Rating (Boeing 737) | Product Authorization | `capabilities[]` |
| Medical Certificate | Active Status | `policy.effective_until` |
| Operating Limitations | Trading Limits | `policies[]` |
| Security Hologram | Tamper Detection | `signature_hash` |

### Part 3: The Four Core Data Types (Finance Focus) (~1,400 words)

**3.1 Capability Examples:**
- `extract_invoice` - Invoice data extraction
- `score_transaction` - Fraud risk scoring
- `approve_payment` - Payment authorization
- `classify_expense` - Expense categorization

**3.2 Policy Examples:**
```json
// Rate Limit Policy (Fraud Detector)
{
  "policy_type": "rate_limit",
  "constraints": {
    "max_calls_per_minute": 1000,
    "max_calls_per_hour": 50000,
    "burst_limit": 100
  }
}

// Data Access Policy (PCI-DSS)
{
  "policy_type": "data_access",
  "constraints": {
    "allowed_data_sources": ["transaction_db"],
    "pii_handling_mode": "tokenize",
    "card_data_access": "masked_only",
    "audit_all_access": true
  }
}

// Approval Required Policy (Large Payments)
{
  "policy_type": "approval_required",
  "constraints": {
    "threshold_amount": 100000,
    "approval_role": "cfo",
    "max_pending_hours": 4,
    "auto_escalate": true
  }
}
```

**3.3 AgentFacts Example:**
Complete `invoice-extractor-v2` identity document (reuse from Part 1)

**3.4 AuditEntry Example:**
SOX-compliant change tracking with 7-year retention

### Part 4: Registry Architecture (~600 words)
- Same dual-storage pattern as BlackBox
- Finance-specific: regulatory retention requirements (SOX 7 years)
- Integration with existing `cache/` directory from BlackBox
- CRUD operations reference table

### Part 5: Tamper Detection (~1,000 words)

**Finance Tampering Scenario:**
Attacker modifies `max_payment_amount` from $100,000 to $10,000,000 to approve unauthorized large payments without CFO review.

```python
# Original Agent State
agent = registry.get("invoice-approver-v1")
print(f"Max Payment: ${agent.policies[0].constraints['threshold_amount']:,}")
# Output: Max Payment: $100,000

# Simulated Tampering (bypassing registry)
tampered_data = agent.model_dump()
tampered_data["policies"][0]["constraints"]["threshold_amount"] = 10000000

# Detection
tampered_agent = AgentFacts(**tampered_data)
print(f"Tampered Agent Valid: {tampered_agent.verify_signature()}")
# Output: False ← TAMPERING DETECTED!
```

**Security Limitations (Honest Disclosure):**
- SHA256 provides integrity verification, not cryptographic security
- For finance (SOX compliance): recommend Level 2 (asymmetric signatures)
- Mention HSM integration for production financial systems

### Part 5.5: Policy Verification vs. Enforcement (~700 words)
- Same two-layer model
- Finance examples:
  - Rate limits → Transaction volume limits
  - Data access → PCI-DSS card data handling
  - Approval required → Large payment authorization
- Bridge to GuardRails (already covered in Part 1)

### Part 6: The SOX Audit Revisited (~500 words)
- Answer the auditor's questions in 2 minutes (not 4 hours)
- Export for SOX Section 404 compliance documentation
- Before/After time comparison table

**Auditor Questions Answered:**
1. "Which version?" → `agent.version` → "2.3.1"
2. "What policies governed it?" → `agent.get_active_policies()` → instant list
3. "Who authorized the threshold change?" → `audit_trail` → "compliance-team@company.com"
4. "Has anyone tampered with config?" → `verify()` → True (valid)

### Part 7: The Governance Triangle Complete (~500 words)
- BlackBox (What happened?) + AgentFacts (Who was authorized?) + GuardRails (Was it valid?)
- Show how all three work together for the invoice processing pipeline
- Reference Part 1's incident with AgentFacts layer added

```
                     ┌─────────────┐
                     │  AgentFacts │
                     │  (WHO)      │
                     └──────┬──────┘
                            │
              ┌─────────────┼─────────────┐
              │             │             │
              ▼             │             ▼
       ┌─────────────┐      │      ┌─────────────┐
       │  BlackBox   │◄─────┴─────►│  GuardRails │
       │  (WHAT)     │             │  (VALID?)   │
       └─────────────┘             └─────────────┘
```

### Part 8: Finance Best Practices (~600 words)
- SOX 7-year retention policy
- PCI-DSS policy expiration monitoring (automated alerts)
- Individual accountability (email, not team names)
- Real-time verification for high-value transactions (>$100K)
- Capability schema validation (ensure declared capabilities match actual behavior)

### Part 9: Reflections (~400 words)
- Key takeaways for financial services
- The complete governance stack
- Mental model: agent credentials = financial licenses
- Call to action

---

## Cross-References

### Links to Add
- Part 1: `[BlackBox Recording Deep Dive](./blackbox_narrative_deepdive.md)`
- GuardRails: `[GuardRails Validation](../backend/explainability/guardrails.py)`
- Implementation: `[AgentFacts Implementation](../backend/explainability/agent_facts.py)`

### Shared Elements from Part 1
- Same incident (November 27, 2024)
- Same agents (`invoice-extractor-v2`, `invoice-validator-v1`, `invoice-approver-v1`)
- Same team (`finance-automation-team`)
- Same `cache/` directory structure
- Same aviation metaphor (but streamlined)

---

## Comparison: Original vs. Finance Series Version

| Aspect | Original Article | Finance Series Version |
|--------|------------------|------------------------|
| **Position** | Standalone | Part 2 of BlackBox series |
| **Opening** | HIPAA audit cold open | Continues invoice incident from Part 1 |
| **Domain** | Healthcare/mixed | Finance only |
| **Primary Agent** | `diagnosis-generator-v1` | `invoice-extractor-v2` (same as Part 1) |
| **Compliance** | HIPAA | SOX Section 404, PCI-DSS 4.0 |
| **Length** | 12,000 words (55 min) | ~7,000 words (35 min) |
| **Aviation mentions** | 5+ times | 1-2 times (Part 1 covered it) |
| **Policy Examples** | Healthcare (HIPAA, physician approval) | Finance (payment limits, PCI-DSS, SOX) |
| **Tampering Scenario** | Remove `requires_approval` for diagnosis | Increase `max_payment_amount` limit |

---

## Implementation Notes

1. **Don't modify original article** - `agentfacts_governance_deepdive.md` is valuable for healthcare audience
2. **Create new file** - `agentfacts_governance_finance.md`
3. **Reuse code examples** - Adapt from original but change domain
4. **Maintain consistency** - Same Pydantic models, same registry API
5. **Link both articles** - Add "See also" sections in both

---

## Next Steps

1. [x] Create `agentfacts_governance_finance.md`
2. [x] Write Part 1 (continue from BlackBox incident)
3. [x] Adapt Parts 2-9 with finance focus
4. [x] Add cross-references to Part 1 (BlackBox deep dive)
5. [x] Update Part 1 to reference Part 2 in References section
6. [ ] Validate all code examples work with existing implementation

**Completed:** 2025-11-29 - Article created at ~4,500 words (more concise than original 12,000-word healthcare version)
