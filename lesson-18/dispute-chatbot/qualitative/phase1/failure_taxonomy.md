# Phase 1 Failure Taxonomy

**Version:** 1.1
**Source:** Qualitative analysis of synthetic conversation traces (Phase 1)
**Last Updated:** 2025-12-09
**Next Review:** After 100 new production traces OR before Task 9.0 judge calibration

---

## Changelog

| Version | Date       | Author       | Changes                                                                 |
|---------|------------|--------------|-------------------------------------------------------------------------|
| 1.0     | 2025-12-09 | AI Assistant | Initial taxonomy with 5 failure modes from open coding analysis         |
| 1.1     | 2025-12-09 | AI Assistant | Added specific red flag indicators per reflection feedback; added version control; added review triggers |

### Review Triggers

This taxonomy should be reviewed and updated when:
1. **100 new production traces** have been analyzed
2. **New failure pattern** emerges that doesn't fit existing categories
3. **Judge calibration** reveals threshold issues (Task 9.0)
4. **Quarterly review** cycle (post-MVP)
5. **Regulatory change** affects compliance requirements

---

## 1. Failure Mode: Network Timeout (System Reliability)

**Definition:** The backend tool execution exceeds the defined timeout threshold (e.g., 30s), causing a temporary failure state.

### Red Flag Indicators

Agent output contains ANY of:
- Error messages matching: `TimeoutError`, `ConnectionError`, `ETIMEDOUT`
- Phrases: "System is slow", "Retrying...", "Unable to connect"
- Tool response with `status: "timeout"` or `status: "error"`
- Response time > 30000ms in trace metadata

### Detection Rules
```python
# Programmatic detection
def is_network_timeout(trace: dict) -> bool:
    return any([
        "TimeoutError" in str(trace.get("error", "")),
        trace.get("tool_response", {}).get("status") == "timeout",
        trace.get("duration_ms", 0) > 30000,
        "retrying" in trace.get("assistant_message", "").lower()
    ])
```

**Illustrative Examples:**
1. *Trace ID*: `TRC-9a2f15de`
   *Issue*: `check_status` tool returned `TimeoutError` after initial call.
   *Resolution*: Auto-retry succeeded.

2. *Trace ID*: `TRC-8977a9ea`
   *Issue*: Assistant reported "System is slow. Retrying..." after tool failure.

**Frequency:** Common (observed in ~30% of recovery traces)
**Severity:** Medium
**Blocking:** No (if retry succeeds), Yes (if retry budget exhausted)
**Proposed Fix:** Exponential backoff retry logic (1s, 2s, 4s).
**LLM Judge Mapping:** N/A (Handled by application logic/`tenacity` library, not LLM Judge).

---

## 2. Failure Mode: Evidence Contradiction (Evidence Quality)

**Definition:** The agent detects conflicting information between user-provided claims and retrieved evidence (or internal consistency checks).

### Red Flag Indicators

Agent output contains ANY of:
- Explicit contradiction phrases: "contradictory", "inconsistent", "conflicting"
- Evidence field mismatches: `user_claim.date != evidence.transaction_date`
- Multiple evidence sources with incompatible values for same field
- Confidence qualifiers: "appears to conflict", "doesn't match"

### Detection Rules
```python
# Programmatic detection
def has_evidence_contradiction(trace: dict) -> bool:
    contradiction_phrases = [
        "contradictory", "inconsistent", "conflicting",
        "doesn't match", "does not match", "appears to conflict"
    ]
    assistant_msg = trace.get("assistant_message", "").lower()
    return any(phrase in assistant_msg for phrase in contradiction_phrases)
```

**Illustrative Examples:**
1. *Trace ID*: `TRC-a58e226f`
   *Issue*: Assistant stated "The evidence is contradictory" regarding the dispute claim.

2. *Trace ID*: `TRC-ca7d751f`
   *Issue*: Complex case flag raised due to internal inconsistency.

**Frequency:** Occasional (trigger for escalation)
**Severity:** High (requires human judgment)
**Blocking:** Yes (blocks automated submission)
**Proposed Fix:** Route to `human_escalation` workflow.
**LLM Judge Mapping:** `evidence_quality` (Score < 0.8 should trigger this).

---

## 3. Failure Mode: Evidence Fabrication (Hallucination)

**Definition:** Agent generates evidence details (transactions, dates, IDs) that do not exist in the source context or tool outputs.

### Red Flag Indicators

Agent output contains ANY of:
- **Transaction IDs** not in `tool_output.transactions[].id`
- **Dates** not derivable from `evidence_package.timestamps` or calculable from known dates
- **Tracking numbers** not in `shipping_records.tracking_ids`
- **Amounts** not matching any `transaction.amount` field (exact match required)
- **Names/signatures** not in `customer_profile` or `shipping.pod`
- **Policy claims** with no `policy_document` reference in context
- **Statistics** that don't match calculable values from evidence

### Detection Rules
```python
# Programmatic detection (requires evidence context)
def detect_fabrication(agent_output: str, evidence: dict) -> list[str]:
    red_flags = []

    # Check transaction IDs
    valid_txn_ids = {t["id"] for t in evidence.get("transactions", [])}
    mentioned_txn_ids = extract_txn_ids(agent_output)  # regex: TXN-\w+
    for txn_id in mentioned_txn_ids:
        if txn_id not in valid_txn_ids:
            red_flags.append(f"Transaction ID {txn_id} not in tool_output.transactions[]")

    # Check amounts
    valid_amounts = {t["amount"] for t in evidence.get("transactions", [])}
    mentioned_amounts = extract_amounts(agent_output)  # regex: \$[\d,]+\.?\d*
    for amount in mentioned_amounts:
        if amount not in valid_amounts:
            red_flags.append(f"Amount ${amount} not in any evidence field")

    # Check tracking numbers
    valid_tracking = evidence.get("shipping", {}).get("tracking_id")
    mentioned_tracking = extract_tracking(agent_output)
    for tracking in mentioned_tracking:
        if tracking != valid_tracking:
            red_flags.append(f"Tracking {tracking} not in shipping_records")

    return red_flags
```

### Fabrication Categories (from golden set)
| Category | Example | Severity |
|----------|---------|----------|
| `transaction_fabrication` | Invented TXN-ID, amount, or date | Critical |
| `tracking_fabrication` | Fabricated tracking/delivery details | Critical |
| `date_fabrication` | Invented timeline events | High |
| `amount_fabrication` | Altered transaction amounts | Critical |
| `ce3_fabrication` | Inflated CE 3.0 history | Critical |
| `device_fabrication` | Invented device fingerprint | High |
| `partial_fabrication` | Correct base data + fabricated details | High |
| `regulatory_fabrication` | Wrong deadline/policy claims | Critical |
| `statistical_fabrication` | Misrepresented numbers | High |
| `composite_fabrication` | Multiple fabrications in one output | Critical |

**Illustrative Examples:**
*(From `fabrication_examples.json` - 15 adversarial test cases)*
1. *FAB-001*: Agent claims "TXN-002 for $250.00" when only TXN-001 for $150.00 exists.
2. *FAB-007*: Agent correctly cites tracking but fabricates "signature from Mary Johnson".
3. *FAB-015*: Multiple fabrications in single output (date, address, amount).

**Frequency:** Rare (in current synthetic data) but Critical risk.
**Severity:** Critical
**Blocking:** Yes (Hard Block)
**Proposed Fix:** `FabricationDetectionJudge` with 0.95 threshold.
**LLM Judge Mapping:** `fabrication_detection`.

---

## 4. Failure Mode: Classification Error

**Definition:** The agent assigns an incorrect reason code (e.g., 10.4 vs 13.1) based on the dispute description.

### Red Flag Indicators

Agent output contains ANY of:
- Reason code assignment that contradicts dispute keywords:
  - "didn't receive" / "never arrived" / "not delivered" → should be 13.1 (PNR), not 10.4
  - "didn't authorize" / "wasn't me" / "stolen" → should be 10.4 (Fraud), not 13.1
- Missing key evidence request for assigned code:
  - 10.4 assigned but no fraud indicators requested
  - 13.1 assigned but no shipping evidence requested
- Confidence score < 0.7 on classification

### Detection Rules
```python
# Programmatic detection
def detect_classification_error(trace: dict) -> list[str]:
    red_flags = []
    user_msg = trace.get("user_message", "").lower()
    assigned_code = trace.get("reason_code")

    pnr_keywords = ["didn't receive", "never arrived", "not delivered", "missing package"]
    fraud_keywords = ["didn't authorize", "wasn't me", "stolen", "fraud", "unauthorized"]

    has_pnr_signal = any(kw in user_msg for kw in pnr_keywords)
    has_fraud_signal = any(kw in user_msg for kw in fraud_keywords)

    if has_pnr_signal and assigned_code == "10.4":
        red_flags.append("PNR keywords detected but classified as Fraud (10.4)")
    if has_fraud_signal and assigned_code == "13.1":
        red_flags.append("Fraud keywords detected but classified as PNR (13.1)")

    return red_flags
```

**Illustrative Examples:**
*(Implicit in success cases)*
1. *Success Case*: `TRC-04dd4579` correctly identified "It's a fraud dispute" from context.
2. *Failure Case*: Misinterpreting "I didn't receive it" as Fraud (10.4) instead of PNR (13.1).

**Frequency:** Rare (assuming robust routing model)
**Severity:** High
**Blocking:** No (Warning only - `dispute_validity` judge)
**Proposed Fix:** Improve routing model few-shot examples.
**LLM Judge Mapping:** `dispute_validity`.

---

## 5. Failure Mode: User-Requested Escalation

**Definition:** The user explicitly asks for a human agent, overriding the automated flow.

### Red Flag Indicators

User message contains ANY of:
- Explicit requests: "human", "agent", "representative", "supervisor", "manager"
- Frustration markers: "this isn't working", "I give up", "just let me talk to"
- Repeated same question (>2 times indicates confusion)

### Detection Rules
```python
# Programmatic detection
def is_user_escalation_request(user_message: str) -> bool:
    escalation_phrases = [
        "human", "agent", "representative", "supervisor",
        "manager", "talk to someone", "real person",
        "this isn't working", "let me speak to"
    ]
    return any(phrase in user_message.lower() for phrase in escalation_phrases)
```

**Illustrative Examples:**
1. *Trace ID*: `TRC-6371b389`
   *Issue*: User said "I need a human to look at this."

**Frequency:** Variable
**Severity:** Low (Expected behavior)
**Blocking:** Yes (Stops automation)
**Proposed Fix:** N/A (Feature, not bug).
**LLM Judge Mapping:** N/A (Intent classification).

---

## 6. Failure Mode: Compliance Violation (Anticipated)

**Definition:** Agent output or processing violates PCI-DSS requirements or exposes PII.

### Red Flag Indicators

Agent output or logs contain ANY of:
- Full PAN (card number): `\b\d{13,19}\b` without masking
- CVV/CVC: 3-4 digit code in context of payment
- Full SSN: `\d{3}-\d{2}-\d{4}`
- Unmasked email in logs: `[^@]+@[^@]+\.\w+` (should be `j***@example.com`)
- Deadline arithmetic errors: calculated deadline != filed_date + network_days

### Detection Rules
```python
# Programmatic detection (GuardRails)
import re

PCI_PATTERNS = {
    "pan": r"\b\d{13,19}\b",
    "cvv": r"\bCVV:?\s*\d{3,4}\b",
    "ssn": r"\b\d{3}-\d{2}-\d{4}\b",
}

def detect_pci_violation(text: str) -> list[str]:
    violations = []
    for pci_type, pattern in PCI_PATTERNS.items():
        if re.search(pattern, text):
            violations.append(f"Potential {pci_type.upper()} exposure detected")
    return violations
```

**Illustrative Examples:**
*(Anticipated - zero tolerance)*
1. *Hypothetical*: Agent logs full card number instead of masked `****1234`.
2. *Hypothetical*: Deadline calculated as 21 days instead of 30 days for Visa.

**Frequency:** Should be zero (GuardRails enforced)
**Severity:** Critical
**Blocking:** Yes (Hard Block)
**Proposed Fix:** `GuardRails` PII detection with PASS/FAIL.
**LLM Judge Mapping:** `GuardRails` (Regex/NLP), not LLM Judge.

---

## Summary: Red Flag Quick Reference

| Failure Mode | Key Red Flags | Responsible System |
|--------------|---------------|-------------------|
| Network Timeout | `TimeoutError`, duration > 30s, "Retrying" | Application logic |
| Evidence Contradiction | "contradictory", field mismatches | `EvidenceQualityJudge` |
| Evidence Fabrication | IDs/dates/amounts not in evidence | `FabricationDetectionJudge` |
| Classification Error | PNR↔Fraud keyword mismatch | `DisputeValidityJudge` |
| User Escalation | "human", "agent", frustration markers | Intent classifier |
| Compliance Violation | PAN, CVV, SSN patterns | `GuardRails` |

---

## Annotation Guidelines

When reviewing new traces against this taxonomy:

1. **Read trace completely** before assigning failure mode
2. **Check all red flag indicators** - one match is sufficient for flagging
3. **Prefer specific category** when multiple could apply (e.g., `partial_fabrication` over generic `fabrication`)
4. **Document uncertainty** in notes column if borderline case
5. **Escalate new patterns** that don't fit existing modes for taxonomy update

---

## Known Gaps & Required Follow-ups

- **Trace coverage:** Current coding evidence is limited; expand `open_codes.csv` to ≥50 traces and refresh taxonomy if new modes appear.
- **Inter-rater reliability:** Run κ on a 20-trace sample with ≥2 raters; update modes/definitions if disagreement surfaces.
- **Boundary cases:** Code `boundary_case_dialogues.json` (multi-turn confusion, deadline edges, PII near-miss) and add/adjust failure modes and red flags accordingly.
- **Judge validation:** Re-validate fabrication and evidence-quality judges on updated examples; adjust thresholds if false positives/negatives rise.
- **Gate 6.17.6:** Marked **pending** until the above actions are completed and reviewed.

### Boundary Case Observations (newly coded)
- **Multi-turn confusion & ambiguous classification:** TRC-BC-001, TRC-BC-005, TRC-BC-011 — ensure `Classification Error` red flags cover story changes and low-confidence classifications.
- **Deadline edge & compliance:** TRC-BC-003 — reinforce `Compliance Violation` red flags for near-deadline delays.
- **PII near-miss:** TRC-BC-009 — handled via `Compliance Violation` → `GuardRails` (PASS/FAIL).
- **Tool failure cascades:** TRC-BC-007 — aligns with `Network Timeout`/system reliability patterns.
- **Empty/partial evidence & contradictions:** TRC-BC-002, TRC-BC-008, TRC-BC-012 — map to `Evidence Quality` (blocking) and `Evidence Contradiction`.

---

## References

- [Open Codes CSV](open_codes.csv) - Raw qualitative codes
- [Axial Categories](axial_categories.md) - Category groupings
- [Judge Mapping](judge_mapping.md) - LLM judge assignments
- [Saturation Log](saturation_log.md) - Analysis completion evidence
- [Fabrication Examples](../synthetic_data/phase1/golden_set/fabrication_examples.json) - Adversarial test set
