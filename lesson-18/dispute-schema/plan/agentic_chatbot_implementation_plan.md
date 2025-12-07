# Agentic Bank Dispute Chatbot Implementation Plan

## Executive Summary

This document outlines the implementation plan for building an agentic chatbot for bank dispute management using the existing `dispute-schema` system as the backend. The chatbot will enable customers to file disputes, check status, add evidence, and receive regulatory compliance guidance through natural language.

**Feasibility Score: 85% Viable**
**Timeline to MVP: 10-14 weeks**
**Current Backend Readiness: 70%**

---

## Part 1: Current System Analysis

### 1.1 What Exists (Strengths)

| Component | File Location | Status | Description |
|-----------|---------------|--------|-------------|
| Core Dispute Schema | `dispute.schema.json`, `dispute_types.ts` | 100% | 50+ fields, Stripe-style API |
| Evidence Management | `dispute_types.ts:251-282` | 100% | 27 evidence fields, limits enforced |
| Visa VROL Translation | `network_integration/visa_vrol_types.ts` | 80% | CE 3.0 qualification logic |
| Mastercom Integration | `network_integration/mastercom_types.ts` | 40% | Basic types defined |
| Reg E/Z Compliance | `compliance/reg_e_timelines.ts` | 100% | 10/30/45/90 day calculations |
| AWS Step Functions | `aws-integration/step-functions.asl.json` | 100% | 767-line workflow |
| REST API Spec | `aws-integration/openapi.yaml` | 100% | 938-line OpenAPI 3.0 |
| Dispute Classifier | `ai-ml/classification/dispute_classifier.py` | 80% | NLP-based classification |
| Fraud Detector | `ai-ml/fraud/fraud_detector.py` | 80% | Heuristic scoring |
| Balance Transactions | `dispute_types.ts:236-245` | 100% | Event-sourced ledger |
| PCI Tokenization | `dispute_types.ts:118-160` | 100% | No PAN storage |

### 1.2 What's Missing for Chatbot

| Component | Required For | Priority |
|-----------|--------------|----------|
| MCP Tool Layer | LLM function calling | **Critical** |
| Dialogue State Manager | Multi-turn conversations | **Critical** |
| Intent Recognition Enhancement | Better complaint parsing | High |
| NLG Response Templates | Human-readable responses | **Critical** |
| Session Persistence | Chat history | High |
| PCI Guardrails for Chat | Block card numbers in chat | **Critical** |
| Escalation Triggers | Hand-off to human agents | Medium |

---

## Part 2: Architecture Design

### 2.1 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    AGENTIC BANK DISPUTE CHATBOT                              │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌─────────────┐     ┌─────────────────┐     ┌─────────────────────────┐   │
│  │   CUSTOMER  │────▶│  CHAT GATEWAY   │────▶│    LLM ORCHESTRATOR    │   │
│  │  (Mobile/   │     │  (WebSocket/    │     │  (Claude/GPT + MCP)    │   │
│  │   Web/IVR)  │     │   API Gateway)  │     │                         │   │
│  └─────────────┘     └─────────────────┘     └───────────┬─────────────┘   │
│                                                          │                  │
│                             ┌─────────────────────────────┼─────────────┐   │
│                             │                             ▼             │   │
│                             │    ┌───────────────────────────────────┐  │   │
│                             │    │         MCP TOOL LAYER            │  │   │
│                             │    │                                    │  │   │
│                             │    │  ┌────────────┐  ┌────────────┐   │  │   │
│                             │    │  │check_status│  │file_dispute│   │  │   │
│                             │    │  └────────────┘  └────────────┘   │  │   │
│                             │    │  ┌────────────┐  ┌────────────┐   │  │   │
│                             │    │  │add_evidence│  │get_deadline│   │  │   │
│                             │    │  └────────────┘  └────────────┘   │  │   │
│                             │    │  ┌────────────┐  ┌────────────┐   │  │   │
│                             │    │  │lookup_txn  │  │fraud_score │   │  │   │
│                             │    │  └────────────┘  └────────────┘   │  │   │
│                             │    │                                    │  │   │
│                             │    └─────────────────┬─────────────────┘  │   │
│                             │                      │                    │   │
│                             └──────────────────────┼────────────────────┘   │
│                                                    │                        │
│  ┌─────────────────────────────────────────────────┼───────────────────────┐│
│  │                      EXISTING DISPUTE-SCHEMA BACKEND                    ││
│  │                                                 │                       ││
│  │  ┌──────────────┐    ┌──────────────┐    ┌─────┴──────┐               ││
│  │  │  Dispute     │◀──▶│   Step       │◀──▶│  REST API  │               ││
│  │  │  Schema      │    │  Functions   │    │  Gateway   │               ││
│  │  │  (Types)     │    │  (Workflow)  │    │            │               ││
│  │  └──────────────┘    └──────────────┘    └────────────┘               ││
│  │         │                   │                   │                      ││
│  │  ┌──────┴──────┐     ┌──────┴──────┐    ┌──────┴──────┐              ││
│  │  │  DynamoDB   │     │  Classifier │    │   Network   │              ││
│  │  │  (Storage)  │     │  + Fraud    │    │   Adapters  │              ││
│  │  │             │     │   Detector  │    │   (VROL,    │              ││
│  │  │             │     │             │    │  Mastercom) │              ││
│  │  └─────────────┘     └─────────────┘    └─────────────┘              ││
│  │                                                                       ││
│  └───────────────────────────────────────────────────────────────────────┘│
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 2.2 Component Details

#### 2.2.1 Chat Gateway
- **Technology**: AWS API Gateway WebSocket / AppSync
- **Features**:
  - Session management
  - Rate limiting
  - Customer authentication (Cognito integration)
  - Message queuing for async processing

#### 2.2.2 LLM Orchestrator
- **Technology**: Claude (Anthropic) or GPT-4 with MCP
- **Responsibilities**:
  - Intent recognition
  - Entity extraction
  - Tool selection
  - Response generation
  - Conversation memory

#### 2.2.3 MCP Tool Layer
Six core tools wrapping the dispute REST API:

| Tool | Description | Maps to API |
|------|-------------|-------------|
| `file_dispute` | Create new dispute | POST /disputes |
| `check_dispute_status` | Query dispute state | GET /disputes/{id} |
| `get_compliance_deadline` | Reg E/Z timeline | Lambda: deadline-calculator |
| `add_evidence` | Submit evidence | POST /disputes/{id}/evidence |
| `lookup_transaction` | Find transactions | Core banking adapter |
| `fraud_score` | Risk assessment | fraud_detector.py |

---

## Part 3: MCP Tool Specifications

### 3.1 file_dispute

**Purpose**: Create a new dispute for a transaction

**Input Schema**:
```json
{
  "type": "object",
  "properties": {
    "charge_id": {
      "type": "string",
      "pattern": "^ch_[a-zA-Z0-9]{24}$",
      "description": "Transaction/charge ID to dispute"
    },
    "reason": {
      "type": "string",
      "enum": ["fraudulent", "product_not_received", "duplicate", "product_unacceptable", "subscription_canceled", "credit_not_processed", "unrecognized", "general"],
      "description": "Category of the dispute"
    },
    "complaint_narrative": {
      "type": "string",
      "maxLength": 5000,
      "description": "Customer's description of the issue"
    },
    "amount_cents": {
      "type": "integer",
      "description": "Optional partial dispute amount"
    }
  },
  "required": ["charge_id", "reason"]
}
```

**Output**:
```json
{
  "success": true,
  "dispute_id": "dp_abc123xyz...",
  "status": "needs_response",
  "evidence_due_by": 1735689600,
  "evidence_due_by_human": "January 1, 2025",
  "provisional_credit_eligible": true,
  "provisional_credit_deadline_days": 10,
  "message": "Your dispute has been filed successfully. For debit cards, provisional credit will be issued within 10 business days if investigation is ongoing."
}
```

### 3.2 check_dispute_status

**Purpose**: Get current status of an existing dispute

**Input Schema**:
```json
{
  "type": "object",
  "properties": {
    "dispute_id": {
      "type": "string",
      "pattern": "^dp_[a-zA-Z0-9]{24}$"
    }
  },
  "required": ["dispute_id"]
}
```

**Output**:
```json
{
  "dispute_id": "dp_abc123xyz...",
  "status": "under_review",
  "reason": "fraudulent",
  "amount_cents": 24789,
  "currency": "usd",
  "created_at": 1733097600,
  "evidence_submitted": true,
  "evidence_due_by": 1735689600,
  "past_due": false,
  "network_reason_code": "10.4",
  "resolution_message": "Your dispute is currently under review by Visa. A decision is typically made within 45-90 days."
}
```

### 3.3 get_compliance_deadline

**Purpose**: Calculate regulatory deadlines (Reg E/Z)

**Input Schema**:
```json
{
  "type": "object",
  "properties": {
    "dispute_id": { "type": "string" },
    "card_type": {
      "type": "string",
      "enum": ["debit", "credit", "prepaid"]
    },
    "dispute_created_at": { "type": "integer" },
    "is_new_account": { "type": "boolean", "default": false },
    "is_foreign_transaction": { "type": "boolean", "default": false }
  },
  "required": ["card_type"]
}
```

**Output**:
```json
{
  "regulation": "Reg E",
  "deadlines": [
    {
      "label": "Provisional Credit Deadline",
      "due_date": 1733875200,
      "due_date_human": "December 11, 2024",
      "days_from_now": 8,
      "action_required": "provisional_credit",
      "regulation": "Reg E"
    },
    {
      "label": "Investigation Deadline",
      "due_date": 1740960000,
      "due_date_human": "March 2, 2025",
      "days_from_now": 90,
      "action_required": "resolution",
      "regulation": "Reg E"
    }
  ],
  "summary": "Under Regulation E, you must receive provisional credit within 10 business days. The investigation must be completed within 90 days for new accounts or foreign transactions.",
  "urgent_action_required": false
}
```

### 3.4 add_evidence

**Purpose**: Add evidence to support a dispute

**Input Schema**:
```json
{
  "type": "object",
  "properties": {
    "dispute_id": { "type": "string" },
    "evidence_type": {
      "type": "string",
      "enum": [
        "access_activity_log",
        "billing_address",
        "cancellation_policy_disclosure",
        "customer_communication",
        "customer_email_address",
        "customer_name",
        "customer_purchase_ip",
        "product_description",
        "shipping_documentation",
        "shipping_tracking_number",
        "uncategorized_text"
      ]
    },
    "content": { "type": "string", "maxLength": 20000 },
    "submit_to_network": { "type": "boolean", "default": false }
  },
  "required": ["dispute_id", "evidence_type", "content"]
}
```

### 3.5 lookup_transaction

**Purpose**: Search for transactions by criteria

**Input Schema**:
```json
{
  "type": "object",
  "properties": {
    "account_id": { "type": "string" },
    "date_from": { "type": "string", "format": "date" },
    "date_to": { "type": "string", "format": "date" },
    "amount_cents": { "type": "integer" },
    "amount_tolerance_cents": { "type": "integer", "default": 0 },
    "merchant_name": { "type": "string" },
    "limit": { "type": "integer", "default": 10, "maximum": 50 }
  }
}
```

### 3.6 fraud_score

**Purpose**: Assess fraud risk of a transaction/dispute

**Input Schema**:
```json
{
  "type": "object",
  "properties": {
    "transaction_id": { "type": "string" },
    "amount_cents": { "type": "integer" },
    "merchant_category_code": { "type": "string" },
    "is_card_present": { "type": "boolean", "default": true },
    "distance_from_home_miles": { "type": "number", "default": 0 },
    "account_age_days": { "type": "integer", "default": 365 },
    "disputes_last_90_days": { "type": "integer", "default": 0 }
  },
  "required": ["amount_cents"]
}
```

---

## Part 4: PCI DSS Guardrails

### 4.1 Requirements

The chatbot MUST prevent cardholder data (CHD) exposure:

| Data Element | Detection | Action |
|--------------|-----------|--------|
| PAN (Card Number) | Regex + Luhn validation | Block input, warn user |
| CVV/CVC | Pattern matching | Block input, warn user |
| PIN | Pattern matching | Block input, warn user |
| Full Track Data | Pattern matching | Block input, warn user |

### 4.2 Implementation Approach

1. **Input Validation Layer**: Check all user inputs for PAN patterns before processing
2. **Luhn Algorithm**: Validate detected numbers are actual card numbers (reduce false positives)
3. **Output Sanitization**: Redact any sensitive data before returning to chat
4. **Audit Logging**: Log all blocked attempts (without the actual data) for security review

### 4.3 User Guidance

When sensitive data is detected:
```
"For your security, please never share your full card number, CVV code, or PIN in chat.
If you need to reference a card, please use only the last 4 digits (e.g., card ending in 4532)."
```

---

## Part 5: Conversation Flow Design

### 5.1 Intent Categories

| Intent | Trigger Examples | Primary Tool |
|--------|------------------|--------------|
| `dispute.file` | "I want to dispute a charge", "fraudulent transaction" | `file_dispute` |
| `dispute.status` | "Check my dispute status", "what's happening with my case" | `check_dispute_status` |
| `dispute.deadline` | "When is provisional credit due", "regulatory deadline" | `get_compliance_deadline` |
| `dispute.evidence` | "Add evidence", "I have proof" | `add_evidence` |
| `transaction.lookup` | "Find a charge", "I see a charge for $X" | `lookup_transaction` |
| `risk.assess` | "Is this fraud", "suspicious transaction" | `fraud_score` |
| `escalate.human` | "Talk to a person", "speak to agent" | Handoff trigger |

### 5.2 Sample Conversation Flows

#### Flow 1: Fraud Dispute Filing

```
Customer: "I see a charge for $247.89 from Amazon that I didn't make"

[Agent Reasoning]
1. Intent: dispute.file (fraudulent)
2. Entities: amount=$247.89, merchant="Amazon"
3. Tool calls needed:
   a. lookup_transaction(amount=24789, merchant_name="Amazon")
   b. file_dispute(charge_id, reason="fraudulent")
   c. get_compliance_deadline(card_type)

Agent: "I found a charge of $247.89 from 'AMZN MKTP US' on November 15th.
I've filed a fraud dispute (Case #dp_1NxQkL2eZvKYlo2CXr5EPQmR) for this transaction.

Since this is on your debit card, you're protected by Regulation E:
- Provisional credit of $247.89 will be issued within 10 business days
- Investigation will be completed within 45-90 days
- You'll receive written notification of the outcome

Is there anything else you need help with regarding this dispute?"

Customer: "Can I add that I was out of the country when this happened?"

[Agent Reasoning]
1. Intent: dispute.evidence
2. Tool: add_evidence(dispute_id, evidence_type="uncategorized_text", content=...)

Agent: "I've added your statement to the evidence. This travel information can support
your fraud claim. Would you like to provide any additional evidence, such as:
- Travel itinerary or boarding passes
- Bank statements showing other transactions from your trip location
- Any communication with Amazon about this order?"
```

#### Flow 2: Dispute Status Check

```
Customer: "What's happening with my dispute from last week?"

[Agent Reasoning]
1. Intent: dispute.status
2. Need to look up recent disputes for this customer

Agent: "I found your dispute filed on December 1st for $1,104.24 (Case #dp_abc123).

Current Status: Under Review
- Your evidence was submitted successfully
- The case is being reviewed by Visa
- Expected resolution: Within 30-45 days

Next Steps:
- No action required from you at this time
- You'll be notified when a decision is made
- Provisional credit of $1,104.24 was issued on December 8th

Would you like more details about this case?"
```

---

## Part 6: Implementation Phases

### Phase 1: MCP Tool Layer (2-3 weeks)

#### Week 1-2
- [ ] Create `mcp-server/` directory structure
- [ ] Define TypeScript types for all tools
- [ ] Implement `file_dispute` tool
- [ ] Implement `check_dispute_status` tool

#### Week 2-3
- [ ] Implement `get_compliance_deadline` tool
- [ ] Implement `add_evidence` tool
- [ ] Implement `lookup_transaction` tool
- [ ] Implement `fraud_score` tool
- [ ] Add PCI DSS guardrails

### Phase 2: Conversation Engine (3-4 weeks)

#### Week 4-5
- [ ] Create dialogue state manager
- [ ] Implement session persistence (DynamoDB)
- [ ] Build intent classification enhancement

#### Week 5-6
- [ ] Implement slot-filling workflows for dispute intake
- [ ] Create conversation templates
- [ ] Build entity extraction for amounts, dates, merchants

#### Week 6-7
- [ ] Create NLG templates for all dispute statuses
- [ ] Implement Reg E/Z explanation templates
- [ ] Build evidence guidance responses

### Phase 3: Integration & Testing (2-3 weeks)

#### Week 8-9
- [ ] Connect MCP server to LLM orchestrator
- [ ] Integrate with existing Step Functions workflows
- [ ] Implement human escalation triggers

#### Week 9-10
- [ ] End-to-end testing
- [ ] PCI DSS compliance testing
- [ ] Load testing
- [ ] Security review

### Phase 4: Bank Customization (3-4 weeks)

#### Week 11-12
- [ ] Core banking adapter for transaction lookup
- [ ] Customer authentication integration
- [ ] Bank-specific branding and messaging

#### Week 12-14
- [ ] UAT with bank staff
- [ ] Pilot with limited customer group
- [ ] Documentation and training materials

---

## Part 7: File Structure

```
dispute-schema/
├── mcp-server/                          # NEW: MCP server for chatbot
│   ├── package.json
│   ├── tsconfig.json
│   ├── src/
│   │   ├── index.ts                     # MCP server entry point
│   │   ├── types.ts                     # Input/output types
│   │   ├── tools/
│   │   │   ├── file-dispute.ts
│   │   │   ├── check-status.ts
│   │   │   ├── compliance-deadline.ts
│   │   │   ├── add-evidence.ts
│   │   │   ├── lookup-transaction.ts
│   │   │   └── fraud-score.ts
│   │   └── guardrails/
│   │       └── pci-compliance.ts        # PAN/CVV detection
│   └── tests/
│       ├── tools.test.ts
│       └── guardrails.test.ts
│
├── chatbot/                             # NEW: Conversation engine
│   ├── dialogue/
│   │   ├── state-manager.ts
│   │   ├── slot-filling.ts
│   │   └── session-store.ts
│   ├── nlg/
│   │   ├── templates/
│   │   │   ├── dispute-filed.md
│   │   │   ├── status-update.md
│   │   │   ├── deadline-explanation.md
│   │   │   └── evidence-guidance.md
│   │   └── renderer.ts
│   └── intents/
│       ├── dispute-intents.ts
│       └── escalation-triggers.ts
│
├── ai-ml/                               # EXISTING
│   ├── classification/
│   │   └── dispute_classifier.py
│   └── fraud/
│       └── fraud_detector.py
│
├── aws-integration/                     # EXISTING
│   ├── step-functions.asl.json
│   ├── openapi.yaml
│   └── ...
│
└── compliance/                          # EXISTING
    └── reg_e_timelines.ts
```

---

## Part 8: Success Metrics

### Chatbot Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Intent Recognition Accuracy | >90% | Manual review sample |
| Dispute Filing Success Rate | >95% | Tool completion rate |
| Average Resolution Time | <3 minutes | Time to dispute creation |
| Customer Satisfaction | >4.0/5.0 | Post-chat survey |
| Escalation Rate | <15% | Human handoff frequency |
| PCI Violation Attempts Blocked | 100% | Guardrail trigger rate |

### Operational Metrics

| Metric | Target | Timeline |
|--------|--------|----------|
| Chatbot Adoption Rate | >30% of disputes | 6 months post-launch |
| Cost per Dispute (Chat) | <$2 operational | vs $5 phone/email |
| First Contact Resolution | >70% | Single session completion |
| After-Hours Coverage | 100% | 24/7 availability |

---

## Part 9: Risk Mitigation

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| PCI DSS violations | Low | Critical | Multi-layer guardrails, audit logging |
| LLM hallucinations | Medium | High | Schema validation, fact-checking |
| Reg E deadline missed | Low | Critical | Direct workflow integration |
| Customer frustration | Medium | Medium | Clear escalation paths |
| Authentication bypass | Low | Critical | MFA, session binding |
| High latency | Medium | Medium | Caching, connection pooling |

---

## Part 10: Dependencies

### External Dependencies

| Service | Purpose | Fallback |
|---------|---------|----------|
| Claude/GPT API | LLM orchestration | Alternative model |
| AWS Step Functions | Workflow execution | Lambda direct |
| DynamoDB | Session & dispute storage | Aurora PostgreSQL |
| Cognito | Authentication | Auth0 |

### Internal Dependencies

| Component | Depends On | Critical Path |
|-----------|------------|---------------|
| MCP Tools | OpenAPI endpoints | Yes |
| Dialogue Manager | Session Store | Yes |
| NLG Templates | Dispute Schema Types | No |
| Fraud Score | fraud_detector.py | No |
| Compliance Deadline | reg_e_timelines.ts | Yes |

---

## Appendix A: Sample NLG Templates

### Dispute Filed (Fraud)

```markdown
I've filed a fraud dispute for the {{amount}} charge from {{merchant_name}} on {{transaction_date}}.

**Case Number**: {{dispute_id}}
**Status**: Filed

**What happens next**:
{{#if is_debit}}
Under Regulation E, you're entitled to provisional credit within 10 business days if the investigation takes longer.
{{else}}
Under Regulation Z, the bank will investigate and respond within 90 days.
{{/if}}

**Your next steps**:
- No immediate action required
- Keep any evidence related to this transaction
- You'll receive written notification of the outcome

Would you like to add any evidence to strengthen your case?
```

### Status Update

```markdown
Here's the current status of your dispute:

**Case**: {{dispute_id}}
**Amount**: {{amount}}
**Merchant**: {{merchant_name}}
**Status**: {{status_human}}

{{#switch status}}
  {{#case "needs_response"}}
  Evidence is needed by {{evidence_due_by_human}} ({{days_remaining}} days).
  {{/case}}
  {{#case "under_review"}}
  Your case is being reviewed. Decision expected within {{days_to_resolution}} days.
  {{/case}}
  {{#case "won"}}
  Great news! The dispute was resolved in your favor. {{amount}} has been credited to your account.
  {{/case}}
  {{#case "lost"}}
  The dispute was not resolved in your favor. {{reason_explanation}}
  {{/case}}
{{/switch}}
```

---

## Appendix B: Regulatory Reference

### Regulation E (Electronic Fund Transfer Act) - Debit Cards

| Timeline | Requirement |
|----------|-------------|
| 10 business days | Provisional credit if investigation ongoing |
| 45 days | Standard investigation deadline |
| 90 days | Extended deadline (new accounts, foreign, POS) |
| 3 business days | Written results after decision |

### Regulation Z (Truth in Lending Act) - Credit Cards

| Timeline | Requirement |
|----------|-------------|
| 30 days | Acknowledge receipt in writing |
| 90 days | Complete investigation (2 billing cycles max) |
| No provisional credit required | Unlike Reg E |

---

*Document Version: 1.0*
*Created: December 2024*
*Related Documents: `deep_dive_real_world_cases_v2.md`, `national_bank_adoption_plan.md`*
