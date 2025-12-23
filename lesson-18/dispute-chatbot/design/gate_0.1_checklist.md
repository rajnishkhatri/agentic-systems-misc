# Gate 0.1 Validation Checklist: Domain Model Review

**Gate ID:** 0.1
**Document Under Review:** `design/02_domain_model.md`
**Reviewer Role:** Domain Expert (Dispute Analyst)
**Date:** _______________
**Reviewer Name:** _______________

---

## Pre-Review Requirements

- [ ] Reviewer has ≥2 years dispute resolution experience (financial services or payment operations)
- [ ] Reviewer has read the full PRD (`tasks/0014-prd-merchant-dispute-chatbot.md`)
- [ ] Reviewer has access to `design/02_domain_model.md` and `design/02_domain_model.mmd`

---

## Entity Validation Checklist

### 1. Dispute Entity

| Item | Validated | Notes |
|------|-----------|-------|
| [ ] All 14 attributes are necessary and sufficient | | |
| [ ] `DisputeStatus` enum covers all workflow states | | |
| [ ] `ReasonCode` enum covers Phase 1 scope (10.4, 13.1) | | |
| [ ] Deadline calculation rule is accurate (dispute_date + 14 days) | | |
| [ ] CE 3.0 eligibility criteria are correct (≥2 txns, 120 days, 2+ matching signals) | | |
| [ ] Immutable fields list is appropriate | | |

**Questions for Reviewer:**
1. Are there any dispute statuses missing from the workflow?
2. Is the 14-day deadline accurate for all Visa dispute types?
3. Are the CE 3.0 rules correctly captured?

**Reviewer Comments:**
```
[Space for reviewer comments]
```

---

### 2. Evidence Entity

| Item | Validated | Notes |
|------|-----------|-------|
| [ ] All 12 `EvidenceType` values are relevant | | |
| [ ] All 5 `EvidenceSource` values cover real-world sources | | |
| [ ] Hash verification rule is appropriate for integrity | | |
| [ ] Timestamp ordering rule (evidence ≤ dispute_date) is correct | | |
| [ ] CE 3.0 matching criteria (device/IP/email) are accurate | | |
| [ ] Quality threshold (0.5 warning) is reasonable | | |

**Questions for Reviewer:**
1. Are there evidence types missing for fraud (10.4) disputes?
2. Are there evidence types missing for PNR (13.1) disputes?
3. Should `MANUAL_ENTRY` evidence trigger additional validation?

**Reviewer Comments:**
```
[Space for reviewer comments]
```

---

### 3. Merchant Entity

| Item | Validated | Notes |
|------|-----------|-------|
| [ ] All 6 `Platform` values cover major payment processors | | |
| [ ] `MerchantTier` thresholds ($1M, $50M) are appropriate | | |
| [ ] Win rate calculation formula is correct | | |
| [ ] Tier priority rule (ENTERPRISE = higher priority) is appropriate | | |

**Questions for Reviewer:**
1. Are the revenue thresholds for merchant tiers accurate?
2. Should any other payment platforms be included?
3. Is merchant category code (MCC) important for dispute handling?

**Reviewer Comments:**
```
[Space for reviewer comments]
```

---

### 4. Judge Entity

| Item | Validated | Notes |
|------|-----------|-------|
| [ ] All 3 `JudgeType` values are necessary | | |
| [ ] Threshold values are appropriate (0.8, 0.95, 0.7) | | |
| [ ] Blocking behavior is correctly assigned | | |
| [ ] Latency SLA (<800ms P95) is achievable | | |
| [ ] Calibration requirement (≥90% accuracy) is appropriate | | |

**Questions for Reviewer:**
1. Is the Evidence Quality threshold (0.8) appropriate for blocking?
2. Is Fabrication Detection threshold (0.95) sufficient for compliance?
3. Should Dispute Validity be blocking or warning?

**Reviewer Comments:**
```
[Space for reviewer comments]
```

---

### 5. Submission Entity

| Item | Validated | Notes |
|------|-----------|-------|
| [ ] All 7 `SubmissionStatus` values cover the lifecycle | | |
| [ ] All 4 `Resolution` values are accurate | | |
| [ ] One submission per dispute rule is correct | | |
| [ ] Retry logic (3x, exponential backoff) is appropriate | | |
| [ ] Payload immutability after SUBMITTED is correct | | |
| [ ] Deadline enforcement rule is accurate | | |

**Questions for Reviewer:**
1. Can a dispute ever have multiple submissions?
2. Is 3 retries sufficient for network failures?
3. Are there other resolution outcomes beyond WON/LOST/WITHDRAWN/EXPIRED?

**Reviewer Comments:**
```
[Space for reviewer comments]
```

---

### 6. AuditLog Entity

| Item | Validated | Notes |
|------|-----------|-------|
| [ ] All 4 `ExplainabilityPillar` values are necessary | | |
| [ ] All 5 `LogSeverity` levels are appropriate | | |
| [ ] Immutability rule is correct for compliance | | |
| [ ] Retention policies are compliant (BlackBox 90d, PhaseLogger 1yr, GuardRails 7yr) | | |
| [ ] PII redaction rule is sufficient for PCI-DSS | | |
| [ ] Microsecond timestamp precision is necessary | | |

**Questions for Reviewer:**
1. Is 7-year retention for GuardRails violations required by PCI?
2. Is 90-day BlackBox retention sufficient for post-incident analysis?
3. Are there any additional log fields needed for regulatory compliance?

**Reviewer Comments:**
```
[Space for reviewer comments]
```

---

### 7. Conversation Entity

| Item | Validated | Notes |
|------|-----------|-------|
| [ ] All 9 `ConversationState` values cover the UX flow | | |
| [ ] Turn limit target (≤5 turns) is realistic | | |
| [ ] Escalation trigger (turn 10) is appropriate | | |
| [ ] Session timeout (30 minutes) is reasonable | | |
| [ ] Tool call logging requirement is necessary | | |

**Questions for Reviewer:**
1. Is 5 turns sufficient for complex disputes?
2. Is 30-minute session timeout appropriate for merchants?
3. Should there be a "paused" state for merchant to gather evidence?

**Reviewer Comments:**
```
[Space for reviewer comments]
```

---

## Relationship Validation

| Relationship | Cardinality | Validated | Notes |
|--------------|-------------|-----------|-------|
| Merchant → Dispute | 1:N | [ ] | |
| Dispute → Evidence | 1:N | [ ] | |
| Dispute → Submission | 1:1 | [ ] | |
| Dispute → Conversation | 1:1 | [ ] | |
| Dispute → AuditLog | 1:N | [ ] | |
| Evidence → Judge (validated_by) | N:1 | [ ] | |
| Judge → AuditLog (recorded_in) | 1:N | [ ] | |
| Conversation → Merchant | N:1 | [ ] | |

**Questions for Reviewer:**
1. Are any relationships missing?
2. Are the cardinalities correct?

**Reviewer Comments:**
```
[Space for reviewer comments]
```

---

## Business Rules Validation

### Cross-Entity Constraints

| Rule ID | Description | Validated | Notes |
|---------|-------------|-----------|-------|
| BR-001 | Cannot submit past deadline | [ ] | |
| BR-002 | Evidence timestamp ≤ dispute_date | [ ] | |
| BR-003 | Blocking judges gate phase transitions | [ ] | |
| BR-004 | Evidence hash changes must be logged | [ ] | |
| BR-005 | Conversation links to dispute once identified | [ ] | |
| BR-006 | Win rate recalculated on resolution | [ ] | |

### Deadline Rules (Reg E/Z Compliance)

| Rule | Timeline | Validated | Notes |
|------|----------|-----------|-------|
| Evidence submission | 14 calendar days | [ ] | |
| CE 3.0 prior transactions | Within 120 days | [ ] | |
| Network response | 30 business days | [ ] | |

### CE 3.0 Qualification Rules

| Criterion | Requirement | Validated | Notes |
|-----------|-------------|-----------|-------|
| Prior transactions | ≥2 undisputed | [ ] | |
| Time window | Within 120 days | [ ] | |
| Matching criteria | At least 2 of: device, IP, email, shipping address | [ ] | |

**Reviewer Comments:**
```
[Space for reviewer comments]
```

---

## Overall Assessment

### Completeness Check

| Criterion | Met? | Notes |
|-----------|------|-------|
| [ ] All 7 entities are fully documented | | |
| [ ] All relationships have correct cardinality | | |
| [ ] All business rules are captured and accurate | | |
| [ ] Enums cover all required values | | |
| [ ] No missing entities identified | | |
| [ ] No conflicting business rules | | |

### Identified Gaps

| # | Gap Description | Severity | Recommended Action |
|---|-----------------|----------|-------------------|
| 1 | | | |
| 2 | | | |
| 3 | | | |

### Additional Recommendations

```
[Space for additional recommendations]
```

---

## Sign-Off

### Gate 0.1 Decision

- [ ] **APPROVED** - Domain model is complete and accurate. Proceed to Phase 0.5/Phase 1.
- [ ] **APPROVED WITH CONDITIONS** - Minor updates required (list below). Proceed with parallel work.
- [ ] **NOT APPROVED** - Significant gaps identified. Iterate on domain model before proceeding.

### Required Updates (if any)

| # | Update Required | Owner | Due Date |
|---|-----------------|-------|----------|
| 1 | | | |
| 2 | | | |
| 3 | | | |

### Signatures

**Domain Expert Reviewer:**
- Name: _______________
- Title: _______________
- Date: _______________
- Signature: _______________

**Technical Lead:**
- Name: _______________
- Date: _______________
- Signature: _______________

**Product Owner:**
- Name: _______________
- Date: _______________
- Signature: _______________

---

## Appendix: Reference Documents

- PRD: `tasks/0014-prd-merchant-dispute-chatbot.md`
- Domain Model: `design/02_domain_model.md`
- Entity Relationship Diagram: `design/02_domain_model.mmd`
- System Context: `design/00_system_context.md`
- Component Architecture: `design/01_component_architecture.md`

---

*Gate 0.1 Checklist Version 1.0 | Created: 2025-12-08*
