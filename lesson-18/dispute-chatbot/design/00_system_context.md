# System Context: Merchant Dispute Resolution Chatbot

**Document ID:** design/00_system_context
**Version:** 1.0.0
**Last Updated:** 2025-12-08
**Status:** Phase 0 Foundation

---

## 1. Overview

### Purpose

This document defines the system context for the Merchant Dispute Resolution Agentic Chatbot, showing how it fits within the broader merchant payment ecosystem. It identifies:

- **External actors** who interact with the system
- **External systems** the chatbot integrates with
- **System boundary** defining what's in/out of scope
- **Data flows** between components

### Scope

- **Network:** Visa only (Phase 1 MVP)
- **Dispute Types:** Fraud (10.4), Product Not Received (13.1)
- **Target Users:** Small business to enterprise merchants

---

## 2. System Context Diagram

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                              MERCHANT ECOSYSTEM                                          │
│                                                                                          │
│  ┌─────────────┐                                                    ┌─────────────┐     │
│  │             │                                                    │             │     │
│  │  Merchant   │◄──────── Dispute notifications ────────────────────│  Card       │     │
│  │  (User)     │                                                    │  Network    │     │
│  │             │                                                    │  (Visa)     │     │
│  └──────┬──────┘                                                    └──────▲──────┘     │
│         │                                                                  │            │
│         │ Chat interface                                                   │            │
│         │ (Chainlit UI)                                                    │ VROL API   │
│         │                                                                  │            │
│         ▼                                                                  │            │
│  ┌──────────────────────────────────────────────────────────────────┐      │            │
│  │                                                                  │      │            │
│  │              DISPUTE RESOLUTION AGENTIC CHATBOT                  │      │            │
│  │                                                                  │      │            │
│  │  ┌────────────────────────────────────────────────────────────┐  │      │            │
│  │  │                  STATE MACHINE ORCHESTRATOR                 │  │      │            │
│  │  │                                                             │  │      │            │
│  │  │   CLASSIFY ──► GATHER ──► VALIDATE ──► SUBMIT ──► MONITOR  │  │      │            │
│  │  │                   │                       │                 │  │      │            │
│  │  └───────────────────┼───────────────────────┼─────────────────┘  │      │            │
│  │                      │                       │                    │      │            │
│  │  ┌───────────────────▼───────────────────┐   │                    │      │            │
│  │  │    HIERARCHICAL EVIDENCE GATHERER     │   │                    │      │            │
│  │  │                                       │   │                    │      │            │
│  │  │  Planner ──┬── Transaction Specialist │   │                    │      │            │
│  │  │            ├── Shipping Specialist    │   │                    │      │            │
│  │  │            └── Customer Specialist    │   │                    │      │            │
│  │  └───────────────────────────────────────┘   │                    │      │            │
│  │                                              │                    │      │            │
│  │  ┌───────────────────────────────────────────▼──────────────┐     │      │            │
│  │  │                    LLM JUDGE PANEL                        │     │      │            │
│  │  │                                                           │     │      │            │
│  │  │  Evidence Quality │ Fabrication Detection │ Dispute Valid │     │      │            │
│  │  │     (0.8 block)   │    (0.95 block)       │ (0.7 warn)    │     │      │            │
│  │  └───────────────────────────────────────────────────────────┘     │      │            │
│  │                                                                    │      │            │
│  │  ┌────────────────────────────────────────────────────────────┐    │      │            │
│  │  │                 EXPLAINABILITY LAYER                        │    │      │            │
│  │  │                                                             │    │      │            │
│  │  │  [BlackBox] [AgentFacts] [GuardRails] [PhaseLogger]         │    │      │            │
│  │  └────────────────────────────────────────────────────────────┘    │      │            │
│  │                                                                    │      │            │
│  │  ┌────────────────────────────────────────────────────────────┐    │      │            │
│  │  │              NETWORK TRANSLATION LAYER                      │────┼──────┘            │
│  │  │                                                             │    │                   │
│  │  │  Internal Schema ──► Visa VROL Translator ──► VROL Payload  │    │                   │
│  │  └────────────────────────────────────────────────────────────┘    │                   │
│  │                                                                    │                   │
│  └────────────────────────────────────────────────────────────────────┘                   │
│         │              │              │               │                                   │
│         │              │              │               │                                   │
│         ▼              ▼              ▼               ▼                                   │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐                         │
│  │  Payment    │ │  Shipping   │ │  LLM        │ │  Storage    │                         │
│  │  Platform   │ │  Carriers   │ │  Provider   │ │  Services   │                         │
│  │             │ │             │ │             │ │             │                         │
│  │  Stripe     │ │  FedEx      │ │  OpenAI     │ │  Redis      │                         │
│  │  Square     │ │  UPS        │ │  (LiteLLM)  │ │  S3         │                         │
│  │  Shopify    │ │  USPS       │ │             │ │  TimescaleDB│                         │
│  └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘                         │
│                                                                                          │
└─────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. External Actors

### 3.1 Merchant (Primary User)

The merchant is the primary user of the dispute resolution chatbot.

| Attribute | Description |
|-----------|-------------|
| **Role** | Business owner or operations staff defending against disputes |
| **Tiers** | Small Business, Mid-Market, Enterprise |
| **Interactions** | Chat UI, evidence upload, submission confirmation |
| **Goals** | Win disputes, minimize revenue loss, meet deadlines |
| **Channels** | Chainlit web interface (desktop-first) |

**User Journey:**
1. Receives dispute notification from payment platform
2. Initiates chat with dispute ID
3. Reviews gathered evidence and fills gaps
4. Confirms submission to card network
5. Monitors for resolution

### 3.2 Compliance Auditor (Secondary User)

| Attribute | Description |
|-----------|-------------|
| **Role** | Internal or external auditor reviewing dispute handling |
| **Interactions** | Read-only access to explainability data and audit logs |
| **Goals** | Verify Reg E/Z compliance, PCI adherence |
| **Channels** | Audit log export (JSON), dashboard view |

### 3.3 Operations Lead (Secondary User)

| Attribute | Description |
|-----------|-------------|
| **Role** | Manages dispute team and handles escalations |
| **Interactions** | Escalation queue, performance metrics |
| **Goals** | Minimize escalations, maintain SLAs |
| **Channels** | Admin dashboard, escalation notifications |

---

## 4. External Systems

### 4.1 Card Networks

| System | Integration Type | Purpose | Phase |
|--------|-----------------|---------|-------|
| **Visa VROL** | REST API (Mock for Phase 1) | Submit dispute responses, receive decisions | Phase 1 |
| Mastercard | REST API | Future network expansion | Phase 2 |

**Data Exchange with Visa:**
- **Inbound:** Dispute notifications (via payment platform webhook)
- **Outbound:** VROL-formatted evidence packages
- **Response:** Case ID, status updates, final resolution

### 4.2 Payment Platforms

| Platform | Integration | Data Retrieved |
|----------|-------------|----------------|
| **Stripe** | API | Transaction details, merchant ID, customer data |
| **Square** | API | Transaction records, refund history |
| **Shopify** | API | Order data, fulfillment records |
| **Adyen** | API | Payment authorization logs |
| **Direct Visa Merchants** | Manual entry | Limited integration |

### 4.3 Shipping Carriers

| Carrier | Integration | Data Retrieved |
|---------|-------------|----------------|
| **FedEx** | API | Tracking status, POD, delivery photos |
| **UPS** | API | Tracking history, signature images |
| **USPS** | API | Tracking status, delivery confirmation |
| **DHL** | API | International tracking (Phase 2) |

### 4.4 LLM Provider

| Service | Purpose | Integration |
|---------|---------|-------------|
| **OpenAI** (via LiteLLM) | Agent completions, judge evaluations | REST API |
| **Anthropic** | Alternative provider (failover) | REST API |

**Model Configuration:**
- `LLM_DEFAULT_MODEL`: gpt-4o (specialists)
- `LLM_JUDGE_MODEL`: gpt-4o (structured evaluation)
- `LLM_ROUTING_MODEL`: gpt-4o-mini (cheap routing)

### 4.5 Storage Services

| Service | Purpose | Data Stored |
|---------|---------|-------------|
| **Redis** | Session state, conversation persistence | `cl.user_session` state |
| **Amazon S3** | Evidence documents, BlackBox recordings | Evidence files, audit traces |
| **TimescaleDB** | Audit logs (time-series) | AuditLog entries (7-year retention) |
| **PostgreSQL** | Domain entities | Dispute, Merchant, Evidence, etc. |

---

## 5. System Boundary

### 5.1 In Scope (Phase 1 MVP)

| Component | Description |
|-----------|-------------|
| Chainlit Chat UI | Merchant-facing conversational interface |
| State Machine Orchestrator | 5-phase dispute workflow (CLASSIFY → MONITOR) |
| Hierarchical Evidence Gatherer | Parallel specialist agents for evidence collection |
| LLM Judge Panel | 3 synchronous judges for real-time validation |
| Explainability Layer | 4 pillars (BlackBox, AgentFacts, GuardRails, PhaseLogger) |
| Visa VROL Translator | Internal schema → VROL format conversion |
| Mock Visa API | Simulated network for testing |

### 5.2 Out of Scope (Future Phases)

| Component | Deferred To | Rationale |
|-----------|-------------|-----------|
| Mastercard integration | Phase 2 | Focus on single network first |
| Human agent handoff UI | Phase 2 | Automation-first approach |
| Mobile interface | Phase 3 | Desktop-first |
| Batch dispute processing | Phase 2 | Single-dispute flow for MVP |
| Historical analytics dashboard | Phase 2 | Focus on resolution, not reporting |
| Direct network API | Phase 3 | REST facade for testability |

---

## 6. Data Flows

### 6.1 Happy Path Flow

```
┌─────────┐     ┌──────────────┐     ┌─────────────┐     ┌──────────────┐     ┌────────────┐
│Merchant │────►│   CLASSIFY   │────►│   GATHER    │────►│   VALIDATE   │────►│   SUBMIT   │
│         │     │              │     │             │     │              │     │            │
│ Dispute │     │ Reason code  │     │ Evidence    │     │ Judge scores │     │ VROL       │
│ ID      │     │ Deadline     │     │ package     │     │ Pass/Fail    │     │ payload    │
└─────────┘     └──────────────┘     └─────────────┘     └──────────────┘     └────────────┘
                                            │                   │                    │
                                            ▼                   ▼                    ▼
                                     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
                                     │  Payment    │     │    LLM      │     │   Visa      │
                                     │  Platform   │     │  Provider   │     │   VROL      │
                                     │  Shipping   │     │             │     │             │
                                     │  Carriers   │     │             │     │             │
                                     └─────────────┘     └─────────────┘     └─────────────┘
```

### 6.2 Data Flow Matrix

| Source | Destination | Data | Trigger | Security |
|--------|-------------|------|---------|----------|
| Merchant | Chatbot | Dispute ID, evidence uploads | Chat message | TLS, session auth |
| Payment Platform | Chatbot | Transaction details, CE 3.0 history | API call | OAuth 2.0 |
| Shipping Carrier | Chatbot | Tracking, POD, photos | API call | API key |
| Chatbot | LLM Provider | Prompts, evidence for eval | API call | API key, no PII |
| Chatbot | Visa VROL | VROL-formatted payload | API call | mTLS, PCI DSS |
| Visa VROL | Chatbot | Case ID, resolution | Webhook/poll | mTLS |
| Chatbot | S3 | Evidence documents, BlackBox | Write | IAM, encryption |
| Chatbot | Redis | Session state | Read/write | VPC, encryption |
| Chatbot | TimescaleDB | Audit logs | Append | VPC, encryption |

### 6.3 Notification Flows

| Event | Recipient | Channel | Timing |
|-------|-----------|---------|--------|
| Dispute received | Merchant | Email, in-app | Immediate |
| Evidence deadline | Merchant | Email, SMS | 7, 3, 1 days before |
| Submission confirmed | Merchant | In-chat | Immediate |
| Resolution received | Merchant | Email, in-app | Immediate |
| Escalation required | Operations Lead | Slack, email | Immediate |

---

## 7. Integration Points

### 7.1 Inbound Integrations

| Integration | Protocol | Authentication | Rate Limit |
|-------------|----------|----------------|------------|
| Chainlit UI → Chatbot | WebSocket | Session token | 100 msg/min |
| Payment Platform Webhook | HTTPS POST | Webhook signature | 1000/min |
| Admin Dashboard → Chatbot | REST | JWT | 100/min |

### 7.2 Outbound Integrations

| Integration | Protocol | Authentication | Retry Policy |
|-------------|----------|----------------|--------------|
| Chatbot → Stripe/Square | REST | OAuth 2.0 | 3x exponential |
| Chatbot → FedEx/UPS | REST | API key | 3x exponential |
| Chatbot → OpenAI | REST | API key | 3x exponential |
| Chatbot → Visa VROL | REST (mock) | mTLS | 3x (1s, 2s, 4s) |
| Chatbot → S3 | AWS SDK | IAM role | 3x exponential |
| Chatbot → Redis | Redis protocol | Password | Reconnect |

---

## 8. Security Context

### 8.1 Trust Boundaries

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           INTERNET (Untrusted)                               │
│                                                                              │
│  ┌─────────────┐                                         ┌─────────────┐    │
│  │  Merchant   │                                         │  Card       │    │
│  │  Browser    │                                         │  Network    │    │
│  └──────┬──────┘                                         └──────┬──────┘    │
│         │                                                       │           │
└─────────┼───────────────────────────────────────────────────────┼───────────┘
          │ TLS 1.3                                        mTLS   │
          │                                                       │
┌─────────┼───────────────────────────────────────────────────────┼───────────┐
│         ▼                                                       ▼           │
│  ┌─────────────┐            VPC (Trusted)             ┌─────────────┐       │
│  │    WAF      │                                      │   VROL      │       │
│  │  (PAN block)│                                      │   Gateway   │       │
│  └──────┬──────┘                                      └──────┬──────┘       │
│         │                                                    │              │
│         ▼                                                    ▼              │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │                     DISPUTE CHATBOT (Private Subnet)                  │   │
│  │                                                                       │   │
│  │  ┌───────────────┐  ┌───────────────┐  ┌───────────────────────────┐ │   │
│  │  │  GuardRails   │  │  PII Redactor │  │   Explainability Layer    │ │   │
│  │  │  (PCI scan)   │  │  (all logs)   │  │   (audit trail)           │ │   │
│  │  └───────────────┘  └───────────────┘  └───────────────────────────┘ │   │
│  │                                                                       │   │
│  └───────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘
```

### 8.2 Security Requirements Mapping

| Requirement | Implementation | Verification |
|-------------|----------------|--------------|
| PCI-DSS v4.0 | No PAN storage, tokenized references | GuardRails scan |
| PII Protection | Redaction in logs, encrypted at rest | Audit log review |
| Session Security | Redis encryption, 30-min timeout | Session tests |
| API Security | OAuth 2.0, mTLS for Visa | Integration tests |
| Audit Trail | Immutable TimescaleDB logs | 100% trace coverage |

---

## 9. Deployment Context

### 9.1 Infrastructure Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           AWS DEPLOYMENT                                     │
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                          PUBLIC SUBNET                               │    │
│  │                                                                      │    │
│  │  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐              │    │
│  │  │     ALB     │    │     WAF     │    │  CloudFront │              │    │
│  │  │             │    │  (PAN block)│    │  (static)   │              │    │
│  │  └──────┬──────┘    └──────┬──────┘    └─────────────┘              │    │
│  │         │                  │                                         │    │
│  └─────────┼──────────────────┼─────────────────────────────────────────┘    │
│            │                  │                                              │
│  ┌─────────┼──────────────────┼─────────────────────────────────────────┐    │
│  │         ▼                  ▼          PRIVATE SUBNET                 │    │
│  │                                                                      │    │
│  │  ┌─────────────────────────────────────────────────────────────┐    │    │
│  │  │                    ECS FARGATE CLUSTER                       │    │    │
│  │  │                                                              │    │    │
│  │  │  ┌───────────────┐  ┌───────────────┐  ┌───────────────┐    │    │    │
│  │  │  │   Chainlit    │  │   Worker      │  │   Scheduler   │    │    │    │
│  │  │  │   Service     │  │   Service     │  │   (deadlines) │    │    │    │
│  │  │  │   (Chatbot)   │  │   (Async)     │  │               │    │    │    │
│  │  │  └───────────────┘  └───────────────┘  └───────────────┘    │    │    │
│  │  │                                                              │    │    │
│  │  └──────────────────────────────────────────────────────────────┘    │    │
│  │                                                                      │    │
│  │  ┌───────────────┐  ┌───────────────┐  ┌───────────────┐            │    │
│  │  │   RDS         │  │   ElastiCache │  │   S3          │            │    │
│  │  │   PostgreSQL  │  │   Redis       │  │   (evidence)  │            │    │
│  │  └───────────────┘  └───────────────┘  └───────────────┘            │    │
│  │                                                                      │    │
│  │  ┌───────────────┐                                                   │    │
│  │  │  TimescaleDB  │                                                   │    │
│  │  │  (audit logs) │                                                   │    │
│  │  └───────────────┘                                                   │    │
│  │                                                                      │    │
│  └──────────────────────────────────────────────────────────────────────┘    │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘
```

### 9.2 Environment Configuration

| Environment | Purpose | LLM Cache | Mock Visa |
|-------------|---------|-----------|-----------|
| Development | Local development | Disk | Yes |
| Staging | Integration testing | Redis | Yes |
| Production | Live merchant traffic | Redis | No |

---

## 10. Version History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0.0 | 2025-12-08 | Claude | Initial system context for Phase 1 MVP |

---

## 11. References

- PRD Section 9: Technical Considerations (Orchestration Architecture)
- PRD Section 3: Strategic Approach (Major Components)
- PRD Section 8: Non-Functional Requirements (Security, Latency)
- Domain Model: `design/02_domain_model.md`
- Lesson 16: Orchestrator Patterns
- Lesson 17: Explainability Framework
