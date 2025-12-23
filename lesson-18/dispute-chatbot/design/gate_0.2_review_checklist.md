# Gate 0.2 Review Checklist: API Contracts & Sequence Diagrams

**Task**: 2.10 - API contracts reviewed by tech lead + frontend consumer
**PRD Reference**: [0014-prd-merchant-dispute-chatbot.md](../../tasks/0014-prd-merchant-dispute-chatbot.md)
**Review Date**: _______________
**Reviewers**:
- Tech Lead: _______________
- Frontend Consumer: _______________

---

## Pre-Review Requirements

- [ ] All 2.1-2.9 tasks marked complete
- [ ] All YAML files pass `openapi-spec-validator` validation
- [ ] All Mermaid diagrams render without syntax errors

---

## 1. API Specification Review

### 1.1 MCP Tools API (`mcp_tools.yaml`)

| Criterion | Pass | Fail | N/A | Notes |
|-----------|:----:|:----:|:---:|-------|
| **Completeness** |
| All 4 MCP tools defined (classify, gather, validate, submit) | ☐ | ☐ | ☐ | |
| Each tool has request/response schemas | ☐ | ☐ | ☐ | |
| Examples provided for fraud 10.4 and PNR 13.1 | ☐ | ☐ | ☐ | |
| **Error Handling** |
| 400 Bad Request responses defined | ☐ | ☐ | ☐ | |
| 422 Validation Error responses defined | ☐ | ☐ | ☐ | |
| 500 Internal Error responses defined | ☐ | ☐ | ☐ | |
| Error codes are specific and actionable | ☐ | ☐ | ☐ | |
| **Type Safety** |
| All fields have explicit types | ☐ | ☐ | ☐ | |
| UUIDs use `format: uuid` | ☐ | ☐ | ☐ | |
| Dates use `format: date-time` | ☐ | ☐ | ☐ | |
| Enums defined for constrained values | ☐ | ☐ | ☐ | |
| **LLMService Integration** |
| `classify_dispute` uses `routing_model` | ☐ | ☐ | ☐ | |
| `gather_evidence` uses `default_model` | ☐ | ☐ | ☐ | |
| `validate_evidence` uses `judge_model` | ☐ | ☐ | ☐ | |

### 1.2 Internal Events (`internal_events.yaml`)

| Criterion | Pass | Fail | N/A | Notes |
|-----------|:----:|:----:|:---:|-------|
| All state transitions have corresponding events | ☐ | ☐ | ☐ | |
| Event schema versioning documented | ☐ | ☐ | ☐ | |
| Explainability events included (BlackBox, PhaseLogger) | ☐ | ☐ | ☐ | |
| Error/escalation events defined | ☐ | ☐ | ☐ | |

### 1.3 Network Payloads (`network_payloads.yaml`)

| Criterion | Pass | Fail | N/A | Notes |
|-----------|:----:|:----:|:---:|-------|
| **VROL Format** |
| Fraud 10.4 VROL request/response defined | ☐ | ☐ | ☐ | |
| PNR 13.1 VROL request/response defined | ☐ | ☐ | ☐ | |
| CE 3.0 evidence structure documented | ☐ | ☐ | ☐ | |
| Shipping evidence structure documented | ☐ | ☐ | ☐ | |
| **Type Safety** |
| `oneOf` polymorphism used for evidence types | ☐ | ☐ | ☐ | |
| Discriminator prevents invalid combinations | ☐ | ☐ | ☐ | |
| Field mapping table provided | ☐ | ☐ | ☐ | |

### 1.4 Conversation Protocol (`conversation_protocol.yaml`)

| Criterion | Pass | Fail | N/A | Notes |
|-----------|:----:|:----:|:---:|-------|
| 5-turn flow documented | ☐ | ☐ | ☐ | |
| Intent extraction schema defined | ☐ | ☐ | ☐ | |
| Error recovery patterns documented | ☐ | ☐ | ☐ | |
| Session timeout handling defined | ☐ | ☐ | ☐ | |

### 1.5 Common Schemas (`common_schemas.yaml`)

| Criterion | Pass | Fail | N/A | Notes |
|-----------|:----:|:----:|:---:|-------|
| No duplicate schemas across files | ☐ | ☐ | ☐ | |
| All shared types centralized | ☐ | ☐ | ☐ | |
| `$ref` references used consistently | ☐ | ☐ | ☐ | |

---

## 2. Sequence Diagram Review

### 2.1 Happy Path Diagrams

| Diagram | Criterion | Pass | Fail | N/A | Notes |
|---------|-----------|:----:|:----:|:---:|-------|
| **happy_path_fraud_10.4.mmd** |
| | All 5 phases shown (CLASSIFY→MONITOR) | ☐ | ☐ | ☐ | |
| | CE 3.0 evidence flow included | ☐ | ☐ | ☐ | |
| | Parallel evidence gathering shown | ☐ | ☐ | ☐ | |
| | Explainability hooks present | ☐ | ☐ | ☐ | |
| **happy_path_pnr_13.1.mmd** |
| | Shipping specialist flow shown | ☐ | ☐ | ☐ | |
| | POD verification included | ☐ | ☐ | ☐ | |
| | Tracking data retrieval shown | ☐ | ☐ | ☐ | |

### 2.2 Error Recovery Diagram (`error_recovery.mmd`)

| Criterion | Pass | Fail | N/A | Notes |
|-----------|:----:|:----:|:---:|-------|
| Timeout recovery pattern shown | ☐ | ☐ | ☐ | |
| Judge failure handling shown | ☐ | ☐ | ☐ | |
| Partial results handling shown | ☐ | ☐ | ☐ | |
| Max retries / exponential backoff shown | ☐ | ☐ | ☐ | |
| Deadline approach handling shown | ☐ | ☐ | ☐ | |

### 2.3 Escalation Flow Diagram (`escalation_flow.mmd`)

| Criterion | Pass | Fail | N/A | Notes |
|-----------|:----:|:----:|:---:|-------|
| Human handoff trigger conditions shown | ☐ | ☐ | ☐ | |
| Context preservation documented | ☐ | ☐ | ☐ | |
| Escalation ticket creation shown | ☐ | ☐ | ☐ | |
| Return-to-bot flow shown | ☐ | ☐ | ☐ | |

### 2.4 CE 3.0 Qualification Diagram (`ce3_qualification.mmd`)

| Criterion | Pass | Fail | N/A | Notes |
|-----------|:----:|:----:|:---:|-------|
| Prior transaction matching shown | ☐ | ☐ | ☐ | |
| 2+ transaction requirement shown | ☐ | ☐ | ☐ | |
| 120-day window enforced | ☐ | ☐ | ☐ | |
| 2+ matching signals validated | ☐ | ☐ | ☐ | |
| Signal types listed (device, IP, email, address) | ☐ | ☐ | ☐ | |

---

## 3. Frontend Consumer Validation

| Criterion | Pass | Fail | N/A | Notes |
|-----------|:----:|:----:|:---:|-------|
| API request/response formats are frontend-friendly | ☐ | ☐ | ☐ | |
| Error messages are displayable to users | ☐ | ☐ | ☐ | |
| Phase step events can drive UI updates | ☐ | ☐ | ☐ | |
| Explainability data is renderable in sidebar | ☐ | ☐ | ☐ | |
| Conversation turn structure matches Chainlit needs | ☐ | ☐ | ☐ | |

---

## 4. Cross-Cutting Concerns

| Criterion | Pass | Fail | N/A | Notes |
|-----------|:----:|:----:|:---:|-------|
| **PRD Alignment** |
| All FR-2 (MCP Tools) requirements covered | ☐ | ☐ | ☐ | |
| All FR-4 (LLM Judges) thresholds documented | ☐ | ☐ | ☐ | |
| All FR-5 (Explainability) hooks present | ☐ | ☐ | ☐ | |
| **Security** |
| No PII in examples (uses synthetic data) | ☐ | ☐ | ☐ | |
| Authentication requirements documented | ☐ | ☐ | ☐ | |
| **Implementation Readiness** |
| Specs are sufficient to implement Phase 1 | ☐ | ☐ | ☐ | |
| No ambiguity that would block development | ☐ | ☐ | ☐ | |

---

## 5. Issues Found

| # | Severity | File | Description | Resolution |
|---|----------|------|-------------|------------|
| 1 | | | | |
| 2 | | | | |
| 3 | | | | |

**Severity Levels**: 🔴 Blocker | 🟠 Major | 🟡 Minor | 🔵 Improvement

---

## 6. Sign-Off

### Tech Lead Approval

- [ ] All blockers resolved
- [ ] Ready for Phase 1 implementation

**Tech Lead Signature**: _______________
**Date**: _______________

### Frontend Consumer Approval

- [ ] API contracts are frontend-compatible
- [ ] Ready for Chainlit UI integration

**Frontend Consumer Signature**: _______________
**Date**: _______________

---

## Gate 0.2 Status

- [ ] **PASSED** - Proceed to Phase 0.5 (Chainlit UI Foundation)
- [ ] **FAILED** - Resolve issues and re-review

**Final Decision Date**: _______________

---

## Files Reviewed

### API Specifications
- [ ] `design/04_api_specifications/mcp_tools.yaml`
- [ ] `design/04_api_specifications/internal_events.yaml`
- [ ] `design/04_api_specifications/network_payloads.yaml`
- [ ] `design/04_api_specifications/conversation_protocol.yaml`
- [ ] `design/04_api_specifications/common_schemas.yaml`

### Sequence Diagrams
- [ ] `design/03_sequence_diagrams/happy_path_fraud_10.4.mmd`
- [ ] `design/03_sequence_diagrams/happy_path_pnr_13.1.mmd`
- [ ] `design/03_sequence_diagrams/error_recovery.mmd`
- [ ] `design/03_sequence_diagrams/escalation_flow.mmd`
- [ ] `design/03_sequence_diagrams/ce3_qualification.mmd`
