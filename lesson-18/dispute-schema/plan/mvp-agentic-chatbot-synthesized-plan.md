# Synthesized MVP Plan: Agentic Bank Dispute Chatbot

## Executive Summary

| Metric | Value |
|--------|-------|
| **Timeline** | 8 weeks (accelerated MVP) |
| **Backend Readiness** | 70% (leverage existing `dispute-schema`) |
| **Target STP Rate** | 50% (Phase 1), 70%+ (Phase 2) |
| **Primary Channel** | Chatbot (defer phone/email to v2) |
| **Critical Path** | MCP Tools → PCI Guardrails → Dialogue → Integration |

---

## Synthesis: What Each Plan Contributes

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         MVP SYNTHESIS MATRIX                                │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  AGENTIC CHATBOT PLAN          DISPUTE RESOLUTION PLAN       AWS ECOSYSTEM │
│  (Implementation Focus)        (Business Rules)              (Infrastructure)│
│         │                            │                             │        │
│  ┌──────▼──────┐              ┌──────▼──────┐              ┌──────▼──────┐ │
│  │ MCP Tools   │              │ Reg E/Z     │              │ Bedrock/    │ │
│  │ (6 tools)   │              │ Timelines   │              │ Claude API  │ │
│  │             │              │             │              │             │ │
│  │ PCI Guard-  │              │ Fraud Rules │              │ DynamoDB    │ │
│  │ rails       │              │ (30/70/90)  │              │ (Sessions)  │ │
│  │             │              │             │              │             │ │
│  │ NLG Temp-   │              │ SLA Targets │              │ Step Func-  │ │
│  │ lates       │              │ (4hr-5day)  │              │ tions       │ │
│  └──────┬──────┘              └──────┬──────┘              └──────┬──────┘ │
│         │                            │                             │        │
│         └────────────────────────────┼─────────────────────────────┘        │
│                                      │                                      │
│                              ┌───────▼───────┐                              │
│                              │   MVP SCOPE   │                              │
│                              │               │                              │
│                              │ • 4 MCP Tools │                              │
│                              │ • PCI Layer   │                              │
│                              │ • Basic NLG   │                              │
│                              │ • Reg E/Z     │                              │
│                              │ • DynamoDB    │                              │
│                              └───────────────┘                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## MVP Scope Definition

### In Scope (Must Have)

| Component | Source Plan | Rationale |
|-----------|-------------|-----------|
| **4 Core MCP Tools** | Agentic Chatbot | Minimum for dispute filing flow |
| **PCI Guardrails** | Agentic Chatbot | Compliance non-negotiable |
| **Reg E Deadline Calculator** | Dispute Resolution | Required for debit card disputes |
| **Basic Dialogue State** | Agentic Chatbot | Multi-turn conversations |
| **DynamoDB Session Store** | AWS Ecosystem | Proven pattern, low latency |
| **3 NLG Templates** | Agentic Chatbot | dispute-filed, status-update, deadline |

### Deferred to v2

| Component | Reason for Deferral |
|-----------|---------------------|
| Phone/Email channels | Chatbot proves value first |
| Visa VROL integration | Manual submission acceptable for MVP |
| Fraud ML model | Existing `fraud_detector.py` heuristics sufficient |
| Full 6 MCP tools | `lookup_transaction` and `fraud_score` can wait |
| Human escalation UI | Simple handoff notification first |

---

## MVP Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        MVP AGENTIC CHATBOT ARCHITECTURE                     │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  CUSTOMER                                                                   │
│     │                                                                       │
│     │  WebSocket / REST                                                     │
│     ▼                                                                       │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                        CHAT GATEWAY (API Gateway)                    │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────────┐  │   │
│  │  │   Cognito   │  │ Rate Limit  │  │     PCI INPUT FILTER        │  │   │
│  │  │   (Auth)    │  │  (100/min)  │  │  (Luhn + Regex + Block)     │  │   │
│  │  └─────────────┘  └─────────────┘  └─────────────────────────────┘  │   │
│  └───────────────────────────────┬─────────────────────────────────────┘   │
│                                  │                                          │
│                                  ▼                                          │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                     LLM ORCHESTRATOR (Lambda)                        │   │
│  │                                                                      │   │
│  │  ┌─────────────────┐    ┌─────────────────┐    ┌────────────────┐   │   │
│  │  │  Claude API     │    │  Dialogue State │    │  Session Store │   │   │
│  │  │  (Bedrock or    │◄──▶│  Manager        │◄──▶│  (DynamoDB)    │   │   │
│  │  │   Direct)       │    │                 │    │                │   │   │
│  │  └─────────────────┘    └─────────────────┘    └────────────────┘   │   │
│  │           │                                                          │   │
│  │           │ Tool Calls                                               │   │
│  │           ▼                                                          │   │
│  │  ┌─────────────────────────────────────────────────────────────┐    │   │
│  │  │                    MCP TOOL LAYER                            │    │   │
│  │  │                                                              │    │   │
│  │  │  ┌────────────────┐  ┌────────────────┐                     │    │   │
│  │  │  │  file_dispute  │  │  check_status  │   MVP: 4 Tools      │    │   │
│  │  │  │                │  │                │                     │    │   │
│  │  │  └───────┬────────┘  └───────┬────────┘                     │    │   │
│  │  │  ┌───────┴────────┐  ┌───────┴────────┐                     │    │   │
│  │  │  │  add_evidence  │  │ get_deadline   │                     │    │   │
│  │  │  │                │  │ (Reg E/Z)      │                     │    │   │
│  │  │  └───────┬────────┘  └───────┬────────┘                     │    │   │
│  │  │          │                   │                              │    │   │
│  │  └──────────┼───────────────────┼──────────────────────────────┘    │   │
│  └─────────────┼───────────────────┼───────────────────────────────────┘   │
│                │                   │                                        │
│                ▼                   ▼                                        │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                 EXISTING DISPUTE-SCHEMA BACKEND                      │   │
│  │                                                                      │   │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────────┐   │   │
│  │  │  REST API    │  │  Step        │  │  reg_e_timelines.ts      │   │   │
│  │  │  (OpenAPI)   │  │  Functions   │  │  (Compliance Calculator) │   │   │
│  │  └──────────────┘  └──────────────┘  └──────────────────────────┘   │   │
│  │                                                                      │   │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────────┐   │   │
│  │  │  DynamoDB    │  │  fraud_      │  │  dispute_classifier.py   │   │   │
│  │  │  (Disputes)  │  │  detector.py │  │  (NLP Classification)    │   │   │
│  │  └──────────────┘  └──────────────┘  └──────────────────────────┘   │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## MVP Implementation Timeline (8 Weeks)

### Week 1-2: MCP Tool Layer Foundation

```
Priority: CRITICAL
Deliverables:
├── mcp-server/
│   ├── src/
│   │   ├── index.ts              # MCP server entry
│   │   ├── tools/
│   │   │   ├── file-dispute.ts   # POST /disputes wrapper
│   │   │   ├── check-status.ts   # GET /disputes/{id} wrapper
│   │   │   ├── add-evidence.ts   # POST /disputes/{id}/evidence
│   │   │   └── compliance-deadline.ts  # reg_e_timelines.ts integration
│   │   └── guardrails/
│   │       └── pci-compliance.ts # Luhn + regex + blocking
│   └── tests/
│       ├── tools.test.ts
│       └── pci-guardrails.test.ts
```

**Key Decisions:**
- Use existing `dispute-schema/aws-integration/openapi.yaml` as contract
- Reuse `compliance/reg_e_timelines.ts` for deadline calculations
- PCI guardrails block input BEFORE LLM sees it

### Week 3-4: PCI Guardrails + Session Management

```
Priority: CRITICAL (Compliance)
Deliverables:
├── PCI Compliance Layer
│   ├── Input validation (pre-LLM)
│   │   ├── PAN detection: /\b(?:\d{4}[-\s]?){3}\d{4}\b/
│   │   ├── Luhn validation (reduce false positives)
│   │   ├── CVV detection: /\b\d{3,4}\b/ in context
│   │   └── Blocked response template
│   │
│   └── Output sanitization (post-LLM)
│       └── Redact any leaked PAN/CVV before response
│
├── Session Management (DynamoDB)
│   ├── Table: chatbot-sessions
│   │   ├── PK: sessionId (UUID)
│   │   ├── SK: timestamp
│   │   ├── customerId: string
│   │   ├── conversationHistory: Message[]
│   │   ├── currentDisputeId: string?
│   │   ├── slotFillingState: object
│   │   └── TTL: 24 hours
```

### Week 5-6: Dialogue Engine + NLG Templates

```
Priority: HIGH
Deliverables:
├── chatbot/
│   ├── dialogue/
│   │   ├── state-manager.ts      # Track conversation state
│   │   └── slot-filling.ts       # Collect missing info
│   │
│   └── nlg/
│       └── templates/
│           ├── dispute-filed.md       # Confirmation + next steps
│           ├── status-update.md       # Current state + timeline
│           └── deadline-explanation.md # Reg E/Z plain English
```

**Slot-Filling Flow for `file_dispute`:**
```
Required slots:
1. charge_id OR (amount + merchant_name + approximate_date)
2. reason (fraudulent | product_not_received | duplicate | ...)
3. complaint_narrative (optional but encouraged)

Collection strategy:
- If charge_id missing: "I can help you file a dispute. Do you have the
  transaction ID, or can you tell me the amount, merchant name, and
  approximate date?"
- If reason ambiguous: "What best describes the issue?
  1. I didn't authorize this transaction (fraud)
  2. I was charged twice (duplicate)
  3. I didn't receive what I paid for (product not received)
  4. Something else"
```

### Week 7: Integration + End-to-End Testing

```
Priority: HIGH
Deliverables:
├── Integration
│   ├── Connect MCP server to Claude API (Bedrock or direct)
│   ├── Wire to existing Step Functions workflow
│   ├── Implement escalation trigger (human handoff notification)
│   │
├── Testing
│   ├── Happy path: File dispute → Check status → Add evidence
│   ├── PCI test: Attempt to paste card number → Blocked
│   ├── Multi-turn: Slot filling over 3+ messages
│   ├── Edge cases: Invalid dispute ID, expired session
```

### Week 8: Security Review + Soft Launch

```
Priority: CRITICAL
Deliverables:
├── Security Review
│   ├── PCI DSS self-assessment (SAQ-A equivalent for chat)
│   ├── Penetration test (PAN injection attempts)
│   ├── Audit logging verification (CloudTrail)
│   │
├── Soft Launch
│   ├── Internal pilot (bank staff)
│   ├── Limited customer beta (100 users)
│   ├── Feedback collection mechanism
│   ├── Monitoring dashboards (CloudWatch)
```

---

## MCP Tool Specifications (MVP Subset)

### Tool 1: `file_dispute`

```typescript
// Input
interface FileDisputeInput {
  charge_id?: string;           // ch_xxx or lookup by criteria
  amount_cents?: number;        // For lookup if no charge_id
  merchant_name?: string;       // For lookup if no charge_id
  transaction_date?: string;    // ISO 8601
  reason: DisputeReason;        // fraudulent | duplicate | ...
  complaint_narrative?: string; // Customer's words
}

// Output
interface FileDisputeOutput {
  success: boolean;
  dispute_id: string;           // dp_xxx
  status: "needs_response";
  evidence_due_by: number;      // Unix timestamp
  evidence_due_by_human: string;
  provisional_credit: {
    eligible: boolean;
    deadline_days: number;      // 10 for Reg E
    amount_cents: number;
  };
  next_steps: string[];         // Plain English guidance
}
```

### Tool 2: `check_dispute_status`

```typescript
// Input
interface CheckStatusInput {
  dispute_id: string;           // dp_xxx
}

// Output
interface CheckStatusOutput {
  dispute_id: string;
  status: DisputeStatus;
  status_human: string;         // "Under review by Visa"
  created_at: number;
  amount_cents: number;
  merchant_name: string;
  evidence_submitted: boolean;
  days_until_deadline: number;
  provisional_credit_issued: boolean;
  resolution_message: string;   // NLG template output
}
```

### Tool 3: `get_compliance_deadline`

```typescript
// Input
interface GetDeadlineInput {
  dispute_id?: string;
  card_type: "debit" | "credit" | "prepaid";
  dispute_created_at?: number;
  is_new_account?: boolean;     // Extends Reg E to 90 days
  is_foreign_transaction?: boolean;
}

// Output
interface GetDeadlineOutput {
  regulation: "Reg E" | "Reg Z";
  deadlines: Array<{
    label: string;              // "Provisional Credit"
    due_date: number;
    due_date_human: string;
    days_from_now: number;
    action_required: string;
  }>;
  summary: string;              // Plain English explanation
  urgent: boolean;              // < 3 days to any deadline
}
```

### Tool 4: `add_evidence`

```typescript
// Input
interface AddEvidenceInput {
  dispute_id: string;
  evidence_type: EvidenceType;  // customer_communication | shipping_docs | ...
  content: string;              // Text content (max 20KB)
  submit_to_network?: boolean;  // Default false for MVP
}

// Output
interface AddEvidenceOutput {
  success: boolean;
  evidence_id: string;
  total_evidence_count: number;
  evidence_strength: "weak" | "moderate" | "strong";
  suggestions: string[];        // "Consider adding shipping tracking"
}
```

---

## Business Rules Integration (From Dispute Resolution Plan)

### Auto-Resolution Rules (MVP)

```typescript
// Simplified decision tree for MVP
function shouldAutoApprove(dispute: Dispute): boolean {
  // Auto-approve: Duplicate confirmed
  if (dispute.type === 'duplicate' && dispute.duplicateConfidence > 0.95) {
    return true;
  }

  // Auto-approve: Unauthorized + no auth record + low amount
  if (dispute.type === 'unauthorized' &&
      !dispute.authorizationRecordFound &&
      dispute.amountCents < 10000) { // < $100
    return true;
  }

  // Everything else: Manual review
  return false;
}

function shouldAutoDeny(dispute: Dispute): boolean {
  // Auto-deny: Outside Reg E window (60 days)
  if (daysSinceTransaction(dispute) > 60) {
    return true;
  }

  // Auto-deny: Excessive dispute history
  if (dispute.customerDisputeCount90Days > 5) {
    return true; // Flag for fraud investigation
  }

  return false;
}
```

### SLA Enforcement

| Priority | Initial Response | Resolution Target | Escalation |
|----------|-----------------|-------------------|------------|
| Critical (Fraud >$1000) | 4 hours | 24 hours | Auto-escalate |
| High (>$500) | 1 business day | 3 days | Day 2 warning |
| Medium | 1 business day | 5 days | Day 4 warning |
| Low (<$100) | 2 business days | 10 days | Day 8 warning |

---

## Success Metrics (MVP)

| Metric | Target | Measurement |
|--------|--------|-------------|
| Dispute filing completion | >80% | Sessions that result in dp_xxx |
| PCI violations blocked | 100% | Guardrail trigger count |
| Average conversation turns | <5 | Messages to dispute filed |
| Time to file dispute | <3 min | Session start to dp_xxx |
| User satisfaction | >3.5/5 | Post-chat survey |
| Escalation rate | <25% | Human handoff requests |

---

## Risk Mitigation

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| PCI data leak | Low | Critical | Multi-layer guardrails, audit logging, pen test |
| LLM hallucination (wrong deadlines) | Medium | High | Tool responses override LLM; schema validation |
| Session hijacking | Low | High | Cognito auth, session binding, IP validation |
| Backend API downtime | Low | Medium | Circuit breaker, graceful degradation message |
| Reg E deadline miscalculation | Low | Critical | Reuse proven `reg_e_timelines.ts`, unit tests |

---

## Post-MVP Roadmap (v2)

| Phase | Timeline | Features |
|-------|----------|----------|
| **v1.1** | +2 weeks | `lookup_transaction` tool, merchant name search |
| **v1.2** | +4 weeks | `fraud_score` tool, risk-based routing |
| **v2.0** | +8 weeks | Phone channel (Connect + Lex), email parsing |
| **v2.1** | +10 weeks | Visa VROL auto-submission |
| **v3.0** | +16 weeks | ML outcome prediction, proactive notifications |

---

## File Structure (MVP)

```
dispute-schema/
├── mcp-server/                          # NEW
│   ├── package.json
│   ├── tsconfig.json
│   ├── src/
│   │   ├── index.ts                     # MCP server entry
│   │   ├── tools/
│   │   │   ├── file-dispute.ts          # Week 1
│   │   │   ├── check-status.ts          # Week 1
│   │   │   ├── add-evidence.ts          # Week 2
│   │   │   └── compliance-deadline.ts   # Week 2
│   │   └── guardrails/
│   │       └── pci-compliance.ts        # Week 3
│   └── tests/
│
├── chatbot/                             # NEW
│   ├── dialogue/
│   │   ├── state-manager.ts             # Week 5
│   │   └── slot-filling.ts              # Week 5
│   ├── nlg/
│   │   └── templates/                   # Week 6
│   │       ├── dispute-filed.md
│   │       ├── status-update.md
│   │       └── deadline-explanation.md
│   └── session/
│       └── dynamodb-store.ts            # Week 4
│
├── compliance/                          # EXISTING (reuse)
│   └── reg_e_timelines.ts
│
├── ai-ml/                               # EXISTING (reuse)
│   └── classification/
│       └── dispute_classifier.py
│
└── aws-integration/                     # EXISTING (reuse)
    ├── openapi.yaml
    └── step-functions.asl.json
```

---

## Current Implementation Status

### Already Exists (70% Backend Readiness)

| Component | Location | Status |
|-----------|----------|--------|
| Dispute Types | `dispute_types.ts` | ✅ Complete |
| Reg E/Z Timelines | `compliance/reg_e_timelines.ts` | ✅ Complete |
| OpenAPI Spec | `aws-integration/openapi.yaml` | ✅ Complete |
| Step Functions | `aws-integration/step-functions.asl.json` | ✅ Complete |
| MCP Types | `mcp-server/src/types.ts` | ✅ Complete |
| PCI Guardrails | `mcp-server/src/guardrails/pci-compliance.ts` | ✅ Complete |

### Needs Implementation

| Component | Location | Priority |
|-----------|----------|----------|
| file-dispute.ts | `mcp-server/src/tools/` | Week 1 |
| check-status.ts | `mcp-server/src/tools/` | Week 1 |
| add-evidence.ts | `mcp-server/src/tools/` | Week 2 |
| compliance-deadline.ts | `mcp-server/src/tools/` | Week 2 |
| MCP Server Entry | `mcp-server/src/index.ts` | Week 2 |
| Dialogue Manager | `chatbot/dialogue/` | Week 5 |
| NLG Templates | `chatbot/nlg/templates/` | Week 6 |
| Session Store | `chatbot/session/` | Week 4 |
| Tests | `mcp-server/tests/` | Ongoing |

---

*Document Version: 1.0*
*Created: December 2024*
*Related Documents:*
- `agentic_chatbot_implementation_plan.md`
- `banking-transaction-dispute-resolution-system.plan.md`
- `aws-dispute-management-ecosystem-research.md`
