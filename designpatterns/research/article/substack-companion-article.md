# Failure Taxonomy for AI Agents: A TLDR Companion

> **⚠️ Disclaimer**: The narrative scenarios, use cases, and code examples in this article are provided for **illustration purposes only**. They demonstrate concepts and patterns—not production-ready implementations. Adapt these patterns to your specific domain, regulatory requirements, and system architecture.

---

I recently published a deep-dive tutorial on building failure taxonomies for AI agents. At ~25 minutes, it's comprehensive—but not everyone has that kind of time.

This companion distills the key concepts into a quick reference you can bookmark and return to.

For the full tutorial with complete methodology and code, check out the [GitHub repository](https://github.com/YOUR_USERNAME/failure-taxonomy).

---

## The Core Problem

Traditional software fails honestly. A `500 error` or `TimeoutError` tells you something went wrong. You can catch it, log it, retry.

AI agents fail differently.

They can **succeed while being completely wrong**—a confident, well-formatted response citing fabricated transaction IDs, invented signatures, or statistics that don't compute.

That's what I caught at 11 PM on a Thursday: an agent citing "Transaction TXN-002 for $250.00" as evidence. The problem? TXN-002 didn't exist. The only real transaction was TXN-001 for $150.00.

The agent had fabricated evidence. And it looked perfectly plausible.

This is why we need failure taxonomy—a systematic way to catch these "silent failures" before they cause harm.

---

## The Six Failure Modes

After reviewing 100+ agent traces using qualitative research methodology (open coding → axial coding → taxonomy construction), six distinct failure modes emerged:

| Mode | What Happens | Severity | Blocking? |
|------|--------------|----------|-----------|
| **Network Timeout** | System doesn't respond | Medium | If retries exhausted |
| **Evidence Contradiction** | Data doesn't add up | High | Yes |
| **Evidence Fabrication** | Agent invents details | Critical | Yes (Hard) |
| **Classification Error** | Wrong category assigned | High | No (Warning) |
| **User Escalation** | User requests human | Low | Yes |
| **Compliance Violation** | PII/PCI exposure | Critical | Yes (Hard) |

Each requires a different detection strategy. Let me walk through the key patterns.

---

## Detection Patterns

### Network Timeout (The Honest Failure)

This is the one failure mode that tells you it happened.

**Red flags:**
- `TimeoutError`, `ConnectionError`, `ETIMEDOUT`
- "System is slow", "Retrying..."
- Response time > 30,000ms

**Detection:** Application logic with exponential backoff (1s → 2s → 4s) and circuit breakers.

```python
def is_network_timeout(trace: dict) -> bool:
    return any([
        "TimeoutError" in str(trace.get("error", "")),
        trace.get("duration_ms", 0) > 30000,
        "retrying" in trace.get("assistant_message", "").lower()
    ])
```

---

### Evidence Fabrication (The Nightmare Scenario)

This is the most dangerous failure mode because it looks plausible.

**Categories:**
- `transaction_fabrication`: Invented TXN-ID, amount, or date
- `tracking_fabrication`: Made-up delivery/shipping details
- `partial_fabrication`: Correct base data + fabricated details (most insidious)
- `regulatory_fabrication`: Wrong deadline/policy claims

**Red flags:**
- Transaction IDs not in source evidence
- Dates not derivable from any timestamp
- Names/signatures not in customer profile or shipping records
- Statistics that don't match calculable values

**Detection:** Compare every claim against source evidence.

```python
def detect_fabrication(agent_output: str, evidence: dict) -> list[str]:
    red_flags = []
    
    # Check transaction IDs
    valid_txn_ids = {t["id"] for t in evidence.get("transactions", [])}
    mentioned_txn_ids = extract_txn_ids(agent_output)  # regex: TXN-\w+
    
    for txn_id in mentioned_txn_ids:
        if txn_id not in valid_txn_ids:
            red_flags.append(f"Transaction {txn_id} not in evidence")
    
    return red_flags
```

The partial fabrication pattern is especially dangerous. The agent gets the base facts right (correct tracking number, correct transaction date) but adds fabricated details (signature name, delivery time). It looks completely plausible on first review.

---

### Evidence Contradiction

When the evidence doesn't add up—and the agent correctly recognizes it.

**Red flags:**
- Explicit phrases: "contradictory", "inconsistent", "conflicting"
- Field mismatches: `user_claim.date != evidence.transaction_date`
- Multiple sources with incompatible values

**Example:** User claims "product not received," but tracking shows delivery with a signature.

---

### Classification Error

The agent picks the wrong category, which leads to gathering the wrong evidence.

**Red flags:**
- "didn't receive" / "never arrived" → should be Product Not Received (13.1), not Fraud (10.4)
- "didn't authorize" / "wasn't me" → should be Fraud (10.4), not PNR (13.1)

Wrong classification → wrong evidence gathered → weak case.

```python
pnr_keywords = ["didn't receive", "never arrived", "missing package"]
fraud_keywords = ["didn't authorize", "wasn't me", "unauthorized"]

if has_pnr_signal and assigned_code == "10.4":
    flag("PNR keywords but classified as Fraud")
```

---

### Compliance Violation

PII or PCI-sensitive data in output or logs. This is the regulatory nightmare.

```python
PCI_PATTERNS = {
    "pan": r"\b\d{13,19}\b",           # Card numbers
    "cvv": r"\bCVV:?\s*\d{3,4}\b",     # Security codes
    "ssn": r"\b\d{3}-\d{2}-\d{4}\b",   # Social Security
}
```

**Detection:** GuardRails with regex/NLP, not LLM judges. This needs deterministic, fast detection.

---

## Why These Thresholds?

Each threshold encodes your risk tolerance:

| Judge | Threshold | Rationale |
|-------|-----------|-----------|
| Fabrication | 0.95 | Zero tolerance—false negative = filing with fake evidence |
| Evidence Quality | 0.80 | "Good enough to win" baseline |
| Classification | 0.70 | Softer threshold—disputes can be ambiguous |

**The tradeoff:**
- High threshold (0.95) → More false positives, catches more real failures
- Low threshold (0.70) → Fewer blocks, but may miss issues

For fabrication, the cost of a false negative is catastrophic. We'd rather flag correctly-formatted evidence for review than let fabricated evidence slip through.

---

## Validation: Does It Work?

Two validation methods:

**Saturation** — Have we found all the patterns?

Review traces until < 1 new failure mode per 20 traces. After 100+ traces with no new patterns in 50 consecutive reviews, we achieved theoretical saturation.

**Inter-Rater Reliability (κ)** — Can we apply it consistently?

Cohen's Kappa measures agreement beyond chance. Two independent raters (human + LLM) classified the same traces:

- **Observed Agreement:** 85%
- **Cohen's Kappa:** 0.831 ("Almost perfect agreement")
- **Required Threshold:** ≥ 0.75

The 3 disagreements were instructive—they helped us refine our definitions (e.g., uncertainty expression ≠ classification error).

---

## Quick Reference Card

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    FAILURE TAXONOMY QUICK REFERENCE                      │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  NETWORK TIMEOUT                    EVIDENCE CONTRADICTION               │
│  ├─ "TimeoutError", "Retrying"      ├─ "contradictory", "inconsistent"  │
│  ├─ duration > 30000ms              ├─ Field mismatches in evidence      │
│  └─ Handler: App logic + retries    └─ Handler: EvidenceQualityJudge     │
│                                                                          │
│  EVIDENCE FABRICATION               CLASSIFICATION ERROR                 │
│  ├─ IDs/amounts not in evidence     ├─ Wrong reason code for keywords    │
│  ├─ Invented names, dates           ├─ PNR ↔ Fraud signal mismatch       │
│  └─ Handler: FabricationJudge       └─ Handler: ValidityJudge            │
│                                                                          │
│  USER ESCALATION                    COMPLIANCE VIOLATION                 │
│  ├─ "human", "supervisor"           ├─ PAN: \d{13,19}                    │
│  ├─ Frustration markers             ├─ SSN: \d{3}-\d{2}-\d{4}            │
│  └─ Handler: Intent classifier      └─ Handler: GuardRails               │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## When to Update Your Taxonomy

| Trigger | Action |
|---------|--------|
| 100 new production traces | Re-run saturation check |
| New failure pattern emerges | Add to taxonomy, update judges |
| Judge calibration issues | Adjust thresholds, document reasoning |
| Quarterly review cycle | Comprehensive audit |
| Regulatory changes | Update compliance failure mode |

A failure taxonomy is a living document. Version it, changelog it, treat it like code.

---

## Key Takeaways

1. **AI agents fail by succeeding**—confident responses can be completely wrong
2. **Six distinct failure modes** require different detection strategies
3. **LLM judges** operationalize the taxonomy with calibrated thresholds
4. **Saturation + IRR (κ = 0.831)** validate completeness and consistency
5. **The taxonomy is living**—update it as your system evolves

---

## Go Deeper

The full tutorial (~25 min) covers the complete methodology, all detection code, inter-rater reliability validation, and practical exercises.

**📖 [Full Tutorial on GitHub](https://github.com/YOUR_USERNAME/failure-taxonomy)**

---

*This is part of my series on AI Agent Reliability & Explainability. Subscribe to get notified when the next piece drops.*

*What failure modes have you encountered in your AI systems? Reply and let me know—I'm always looking for patterns I haven't documented yet.*
