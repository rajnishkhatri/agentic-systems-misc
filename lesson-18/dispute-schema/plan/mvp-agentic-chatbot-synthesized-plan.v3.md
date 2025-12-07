# Synthesized MVP Plan v3: Agentic Bank Dispute Chatbot

## Executive Summary

| Metric | Value |
|--------|-------|
| **Deployment Context** | In-bank analyst assist (voice call → analyst uses chatbot) |
| **Timeline** | 8 weeks (post-auth gate) |
| **Backend Readiness** | 70% (existing `dispute-schema`) |
| **Target Call Time** | Reduce avg call from >20 min to ≤15 min |
| **Target STP Rate** | 50% (Phase 1), 70%+ (Phase 2) |
| **Critical Path** | Bank SAML SSO → MCP Tools → PCI Guardrails → Dialogue → Integration |

The MVP now assumes analysts operate inside the bank's secure network, authenticate via Bank SAML SSO (RS256 JWT), and use the chatbot to shorten live customer calls by capturing dispute details faster.

---

## Deployment Context & Success Criteria

- **Users**: Bank call-center analysts; customers relay details verbally, analyst enters data via chat UI.
- **Goal**: File a compliant dispute within 15 minutes of call start, including routing for non-Reg E cases and manager escalations when automation confidence is low.
- **Readiness Gate**: Week 0 requires Bank SAML SSO validation (per `mvp-bank-auth-integrated-plan.md`) before any MCP tool work starts.

---

## MVP Scope Definition (Updated)

### In Scope (Must Have)

| Component | Source Plan | Rationale |
|-----------|-------------|-----------|
| **Bank SAML SSO + RS256 JWT** | `mvp-bank-auth-integrated-plan.md` | Required for in-bank deployment and analyst identity binding |
| **4 Core MCP Tools** | Agentic Chatbot | Minimum for dispute filing flow |
| **PCI Guardrails** | Agentic Chatbot | Compliance non-negotiable |
| **Reg E/Z Deadline Calculator** | Dispute Resolution | Needed for debit + credit; determines routing |
| **Specialist Transfer Workflow** | Session Analysis | Ensures non-Reg E disputes route to specialist queue |
| **Manager Escalation Queue** | Session Analysis | Manual review for escalated cases with audit logging |
| **DynamoDB Session Store (bank fields)** | AWS Ecosystem | Tracks analyst session bindings, specialist/manager routing |
| **3 NLG Templates** | Agentic Chatbot | dispute-filed, status-update, deadline |

### Deferred to v2 (unchanged unless noted)

| Component | Reason for Deferral |
|-----------|---------------------|
| Phone/Email channels | Chatbot proves value first |
| Visa VROL integration | Manual submission acceptable for MVP |
| Fraud ML model | Existing `fraud_detector.py` heuristics sufficient |
| Full 6 MCP tools | `lookup_transaction` and `fraud_score` can wait |
| Analyst desktop UI polish | MVP uses lightweight manager console & alerts |

---

## Specialist Transfer Workflow (New)

1. **Card Product Detection**: Slot filling now captures `card_type` (`debit`, `credit`, `prepaid`) and `network` hints.
2. **Routing Logic**:
   - If `card_type === 'debit'`, continue standard Reg E pipeline.
   - Else mark dispute as `requires_specialist`, attach reason (Reg Z, prepaid, network-specific), and push to `specialist_queue` (EventBridge + DynamoDB view).
3. **Service-Level Agreement**: Specialist acknowledges within 4 business hours, resolution target 2 billing cycles (Reg Z). SLA tracked via `specialistStatus` fields on the dispute record.
4. **Audit Trail**: Each transfer logs timestamp, analyst ID, reason, and specialist assignment for compliance review.
5. **Customer Messaging**: NLG templates include messaging such as "A specialist will follow up within 1 business day" to keep calls within 15 minutes.

---

## Manager Escalation Workflow (New)

- **Trigger**: Auto-resolution confidence <70%, fraud score medium, or analyst invokes human review.
- **Queue**: Manager view (Kibana/QuickSight dashboard or lightweight React console) subscribed to `manager-escalations` EventBridge bus.
- **Notifications**: Email + Teams/SNS message containing dispute ID, captured notes, specialist status, and deadlines.
- **Actioning**: Manager opens the console, reviews evidence, updates decision (approve/deny/escalate) which writes to `auditLog` (`actorId`, `action`, `timestamp`, `notes`).
- **Reporting**: Audit entries flow into compliance dashboards to prove Reg E/Reg Z handling accuracy.

---

## MVP Architecture (Bank Auth Aligned)

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                      MVP AGENTIC CHATBOT ARCHITECTURE (v3)                   │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ANALYST (Call Center)                                                       │
│     │                                                                        │
│     │  WebSocket / REST                                                      │
│     ▼                                                                        │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │                        CHAT GATEWAY (API Gateway)                     │   │
│  │  ┌──────────────────┐  ┌─────────────┐  ┌─────────────────────────┐   │   │
│  │  │ Bank SAML SSO    │  │ Rate Limit  │  │     PCI INPUT FILTER    │   │   │
│  │  │  (RS256 JWT)     │  │  (100/min)  │  │  (Luhn + Regex + Block) │   │   │
│  │  └────────┬─────────┘  └─────────────┘  └──────────────┬──────────┘   │   │
│  └───────────┼────────────────────────────────────────────┼──────────────┘   │
│              │ BankUserContext                            │                 │
│              ▼                                            ▼                 │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │                     LLM ORCHESTRATOR (Lambda)                        │   │
│  │  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────────┐   │   │
│  │  │  Claude API     │  │ Dialogue State  │  │  Session Store      │   │   │
│  │  │                 │◄▶│  Manager        │◄▶│  (DynamoDB + JWT    │   │   │
│  │  └─────────────────┘  └─────────────────┘  │   binding fields)   │   │   │
│  │                   │ Tool Calls + Context  └─────────────────────┘   │   │
│  │                   ▼                                                 │   │
│  │  ┌──────────────────────────────────────────────────────────────┐   │   │
│  │  │                      MCP TOOL LAYER                         │   │   │
│  │  │  ┌────────────────┐  ┌────────────────┐                    │   │   │
│  │  │  │  file_dispute  │  │  check_status  │   (+ `_userContext`)│   │   │
│  │  │  ├────────────────┤  ├────────────────┤                    │   │   │
│  │  │  │ add_evidence   │  │ get_deadline   │                    │   │   │
│  │  │  └──────┬─────────┘  └──────┬────────┘                    │   │   │
│  │  │         │ Specialist Transfer │ Manager Escalation Events  │   │   │
│  │  └─────────┼─────────────────────┼────────────────────────────┘   │   │
│  └────────────┼─────────────────────┼────────────────────────────────┘   │
│               │                     │                                    │
│               ▼                     ▼                                    │
│  ┌──────────────────────────────────────────────────────────────────────┐ │
│  │                EXISTING DISPUTE-SCHEMA BACKEND                        │ │
│  │  REST APIs, Step Functions, DynamoDB, `reg_e_timelines.ts`, etc.      │ │
│  │  plus Specialist/Manager queues + audit log exporters                 │ │
│  └──────────────────────────────────────────────────────────────────────┘ │
└────────────────────────────────────────────────────────────────────────────┘
```

---

## Implementation Timeline (8 Weeks + Week 0 Gate)

### Week 0: Bank Auth Readiness (Go/No-Go)
- Configure Bank SAML metadata, JWKS endpoint, RS256 validation lambda.
- Implement `user-context.ts`, session binding (JWT subject + IP), and smoke tests.
- **Outcome**: Signed-off penetration test + greenlight to start Week 1 deliverables.

### Week 1-2: MCP Tool Layer Foundation (Auth-Aware)
```
Priority: CRITICAL
Deliverables:
├── mcp-server/src/tools/ (file-dispute.ts, check-status.ts, add-evidence.ts, compliance-deadline.ts)
├── Each tool requires `_userContext: BankUserContext` and account-access validation.
├── bank-aware unit tests in `mcp-server/tests/tools.test.ts`.
└── Specialist routing scaffolding (flags + queues) created.
```

### Week 3-4: PCI Guardrails + Session/Queue Management
```
Priority: CRITICAL (Compliance & Routing)
Deliverables:
├── PCI guardrails (input/output) unchanged but now log actorId from SSO.
├── chatbot/session/dynamodb-store.ts updated with bankUserId, jwtIssuer, ipAddress, specialistStatus.
├── Specialist transfer queue (EventBridge + DynamoDB stream consumer) implemented.
└── Manager escalation event bus skeleton ready for Week 5 wiring.
```

### Week 5-6: Dialogue, Slot Filling, Manager Workflow
```
Priority: HIGH
Deliverables:
├── Slot filling expanded: capture card_type, network, and specialist reason codes.
├── Dialogue manager surfaces transfer/manager outcomes back to analyst.
├── Lightweight manager console + notification templates (email/SNS/Teams).
├── Audit logging schema finalized (`auditLog` entries for transfers/escalations).
└── Specialist SLA tracking dashboard MVP (QuickSight/Looker).
```

### Week 7: Integration + Comprehensive Testing
```
Priority: HIGH
Integration:
├── Wire MCP server to Claude (Bedrock/direct) with `_userContext` injection.
├── Connect specialist & manager queues to existing Step Functions states.
Testing (automated + manual):
├── Happy path + credit/prepaid transfer path.
├── PCI/SAML negative tests (PAN injection, JWT tampering, replay).
├── Load test: 50 concurrent analysts, ensure chat latency supports 15-min call window.
├── Escalation workflow test: chatbot → manager console → audit log.
└── Observability: CloudWatch metrics for call duration proxy (session time), queue backlog alerts.
```

### Week 8: Security Review + Soft Launch
```
Priority: CRITICAL
├── Security: PCI SAQ-A, SAML pen test, RS256 key rotation rehearsal, audit log verification.
├── Operational readiness: runbooks for specialist queue backlog, manager SLA breaches.
├── Soft launch: internal pilot (analysts + managers) with daily standups, KPI monitoring (call duration, transfer volume, SLA adherence).
```

---

## MCP Tool Specifications (Auth + Routing Aware)

### Common Context
```typescript
interface BankUserContext {
  bankUserId: string;
  accountAccess: string[];
  roles: string[];              // analyst | specialist | manager
  jwtSubject: string;
  jwtIssuer: string;
  ipAddress: string;
  sessionId: string;
}
```

### Tool 1: `file_dispute`
- Inputs now include `_userContext` and optional `card_type`, `network_hint`.
- Implementation validates analyst access, captures card type, and sets `requires_specialist` when necessary.

### Tool 2: `check_dispute_status`
- Returns specialist or manager status plus audit summary when applicable.

### Tool 3: `get_compliance_deadline`
- Already accepts `card_type`; now enforces Reg Z timers and flags `needs_specialist` if mismatch between card type and existing workflow.

### Tool 4: `add_evidence`
- Records which role uploaded evidence (analyst vs specialist vs manager) for audit reporting.

---

## Testing & Observability Enhancements

| Area | Requirement |
|------|-------------|
| **Automated Tests** | Jest/Pytest suites covering MCP tools, specialist routing, manager escalation, JWT validation, PCI filters |
| **Load Testing** | 50 concurrent analyst sessions, 3 disputes/minute sustained, p95 latency <800ms for tool calls |
| **Security Tests** | JWT replay tests, forced logout, guardrail bypass attempts, privilege escalation attempts |
| **Monitoring** | CloudWatch dashboards: session duration, queue backlog, SLA timers, PCI guardrail triggers, escalation ageing |
| **Alerting** | PagerDuty alerts for: specialist queue >20 pending, manager queue >10 pending, auth failures >5/min, PCI violations |

---

## Success Metrics (Updated)

| Metric | Target | Measurement |
|--------|--------|-------------|
| Avg call handling time | ≤15 min | Session start-to-submit timestamps |
| Dispute filing completion | >85% | Sessions that reach `dp_xxx` |
| PCI violations blocked | 100% | Guardrail trigger count |
| Specialist transfer acknowledgement | 95% <4 business hours | Specialist queue metrics |
| Manager escalation resolution | 90% <1 business day | Manager queue metrics |
| Average conversation turns | <5 | Messages per dispute |
| Time to file dispute | <3 min of analyst data entry | Chat timestamps |

---

## Risk Mitigation (Updated)

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Auth misconfiguration | Medium | High | Week 0 gate + RS256 monitoring, auto-rotation blacklists |
| Specialist backlog | Medium | High | SLA dashboards, auto-alert to ops, fallback to manual call transfer |
| Manager escalation stall | Medium | High | Dual-channel notifications + daily review |
| PCI data leak | Low | Critical | Multi-layer guardrails, audit logging, pen test |
| LLM hallucination | Medium | High | Tool-first responses, schema validation |

---

## File Structure (MVP)

```
dispute-schema/
├── mcp-server/
│   ├── package.json
│   ├── tsconfig.json
│   ├── src/
│   │   ├── index.ts
│   │   ├── tools/
│   │   │   ├── file-dispute.ts
│   │   │   ├── check-status.ts
│   │   │   ├── add-evidence.ts
│   │   │   └── compliance-deadline.ts
│   │   ├── guardrails/pci-compliance.ts
│   │   └── auth/
│   │       ├── bank-auth-service.ts
│   │       ├── jwt-validator.ts
│   │       └── user-context.ts
│   └── tests/
├── chatbot/
│   ├── dialogue/
│   ├── nlg/templates/
│   ├── session/dynamodb-store.ts
│   └── services/BankAuthService.ts
├── compliance/reg_e_timelines.ts
└── aws-integration/
    ├── openapi.yaml
    └── step-functions.asl.json
```

---

## Current Implementation Status

| Component | Location | Status |
|-----------|----------|--------|
| Bank SAML SSO integration | `mcp-server/src/auth/`, `chatbot/services/` | ⚠️ Pending Week 0 gate |
| Specialist routing queues | `eventbridge/` + DynamoDB views | ⚠️ Pending |
| Manager console + alerts | `ops/manager-console/` | ⚠️ Pending |
| PCI guardrails | `mcp-server/src/guardrails/pci-compliance.ts` | ✅ Complete |
| MCP core schemas/types | `mcp-server/src/types.ts` | ✅ Complete |

---

*Document Version: 3.0*
*Created: December 2024 (updated January 2025 session)*
*Related Documents:*
- `agentic_chatbot_implementation_plan.md`
- `banking-transaction-dispute-resolution-system.plan.md`
- `mvp-bank-auth-integrated-plan.md`
- `lesson-18/dispute-schema/plan/mvp-agentic-chatbot-synthesized-plan.md` (v2)




