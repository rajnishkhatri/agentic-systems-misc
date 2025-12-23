# Flow Diagrams: Merchant Dispute Resolution Chatbot

**Document ID:** design/01_flow_diagrams
**Version:** 1.0.0
**Last Updated:** 2025-12-08
**Status:** Phase 0 Foundation

---

## 1. Overview

This document provides visual representations of the system flows through sequence diagrams, state diagrams, and data flow diagrams. These complement the System Context document (00_system_context.md).

---

## 2. Main Dispute Resolution Sequence Diagram

### 2.1 Happy Path - End-to-End Flow

```mermaid
sequenceDiagram
    autonumber
    participant M as Merchant
    participant UI as Chainlit UI
    participant SM as State Machine<br/>Orchestrator
    participant HEG as Hierarchical<br/>Evidence Gatherer
    participant JP as LLM Judge<br/>Panel
    participant VT as VROL<br/>Translator
    participant VISA as Visa VROL<br/>(Mock)
    
    Note over M,VISA: Phase 1: CLASSIFY
    M->>UI: Enter dispute ID (e.g., "DIS-2025-001234")
    UI->>SM: Initiate dispute workflow
    SM->>SM: Classify dispute type
    SM-->>UI: "Dispute classified as Fraud (10.4)"
    UI-->>M: Display reason code & deadline
    
    Note over M,VISA: Phase 2: GATHER
    SM->>HEG: Start evidence gathering
    activate HEG
    
    par Parallel Specialist Agents
        HEG->>HEG: Transaction Specialist
        Note right of HEG: Query Stripe/Square
        HEG->>HEG: Shipping Specialist
        Note right of HEG: Query FedEx/UPS
        HEG->>HEG: Customer Specialist
        Note right of HEG: Analyze CE 3.0 history
    end
    
    HEG-->>SM: Evidence package assembled
    deactivate HEG
    
    SM-->>UI: Present gathered evidence
    UI-->>M: "We found 5 evidence items. Review?"
    M->>UI: Confirm or upload additional docs
    
    Note over M,VISA: Phase 3: VALIDATE
    SM->>JP: Evaluate evidence package
    activate JP
    
    par Synchronous Judge Evaluations
        JP->>JP: Evidence Quality Judge
        Note right of JP: Score: 0.85 (>0.8 threshold)
        JP->>JP: Fabrication Detection Judge
        Note right of JP: Score: 0.02 (<0.95 threshold)
        JP->>JP: Dispute Validity Judge
        Note right of JP: Score: 0.78 (>0.7 threshold)
    end
    
    JP-->>SM: All judges PASS
    deactivate JP
    
    SM-->>UI: Validation complete
    UI-->>M: "Evidence validated. Ready to submit?"
    M->>UI: Confirm submission
    
    Note over M,VISA: Phase 4: SUBMIT
    SM->>VT: Convert to VROL format
    VT->>VT: Map internal → VROL schema
    VT-->>SM: VROL payload ready
    
    SM->>VISA: Submit dispute response
    VISA-->>SM: Case ID: VROL-789456
    
    SM-->>UI: Submission confirmed
    UI-->>M: "Submitted! Case ID: VROL-789456"
    
    Note over M,VISA: Phase 5: MONITOR
    loop Every 4 hours
        SM->>VISA: Poll status
        VISA-->>SM: Status: PENDING_REVIEW
    end
    
    VISA->>SM: Resolution: MERCHANT_WIN
    SM-->>UI: Resolution received
    UI-->>M: "🎉 Dispute won! $1,250 credited"
```

---

## 3. State Machine Diagram

### 3.1 Dispute Workflow States

```mermaid
stateDiagram-v2
    [*] --> CLASSIFY: Dispute received
    
    CLASSIFY --> GATHER: Classification complete
    CLASSIFY --> ESCALATE: Classification failed
    
    GATHER --> VALIDATE: Evidence complete
    GATHER --> GATHER: More evidence needed
    GATHER --> ESCALATE: Deadline approaching (<24h)
    
    VALIDATE --> SUBMIT: All judges PASS
    VALIDATE --> GATHER: Judge FAIL (fixable)
    VALIDATE --> ESCALATE: Judge BLOCK (fabrication)
    
    SUBMIT --> MONITOR: Submission successful
    SUBMIT --> SUBMIT: Retry (network error)
    SUBMIT --> ESCALATE: Max retries exceeded
    
    MONITOR --> [*]: Resolution received
    MONITOR --> ESCALATE: SLA breach
    
    ESCALATE --> [*]: Human resolved
    
    note right of CLASSIFY
        Actions:
        - Parse dispute ID
        - Determine reason code
        - Calculate deadline
    end note
    
    note right of GATHER
        Actions:
        - Query payment platforms
        - Retrieve shipping data
        - Analyze customer history
    end note
    
    note right of VALIDATE
        Actions:
        - Run 3 judge evaluations
        - Score evidence quality
        - Check for fabrication
    end note
    
    note right of SUBMIT
        Actions:
        - Translate to VROL
        - Submit to Visa
        - Store confirmation
    end note
    
    note right of MONITOR
        Actions:
        - Poll for updates
        - Notify merchant
        - Record resolution
    end note
```

---

## 4. Hierarchical Evidence Gatherer Flow

### 4.1 Planner-Specialist Architecture

```mermaid
flowchart TB
    subgraph Orchestrator["State Machine Orchestrator"]
        SM[State Machine]
    end
    
    subgraph HEG["Hierarchical Evidence Gatherer"]
        P[Planner Agent]
        
        subgraph Specialists["Specialist Agents (Parallel)"]
            TS[Transaction<br/>Specialist]
            SS[Shipping<br/>Specialist]
            CS[Customer<br/>Specialist]
        end
        
        A[Aggregator]
    end
    
    subgraph External["External Systems"]
        PP[Payment Platforms<br/>Stripe/Square/Shopify]
        SC[Shipping Carriers<br/>FedEx/UPS/USPS]
        DB[(Internal DB<br/>Customer History)]
    end
    
    SM -->|"1. Request evidence<br/>for Dispute DIS-001"| P
    
    P -->|"2a. Plan: Need<br/>transaction proof"| TS
    P -->|"2b. Plan: Need<br/>delivery proof"| SS
    P -->|"2c. Plan: Need<br/>customer history"| CS
    
    TS -->|"3a. Query"| PP
    SS -->|"3b. Query"| SC
    CS -->|"3c. Query"| DB
    
    PP -->|"4a. Transaction data"| TS
    SC -->|"4b. Tracking/POD"| SS
    DB -->|"4c. CE 3.0 history"| CS
    
    TS -->|"5a. Evidence items"| A
    SS -->|"5b. Evidence items"| A
    CS -->|"5c. Evidence items"| A
    
    A -->|"6. Compiled<br/>evidence package"| SM
    
    style P fill:#e1f5fe
    style TS fill:#fff3e0
    style SS fill:#fff3e0
    style CS fill:#fff3e0
    style A fill:#e8f5e9
```

### 4.2 Evidence Gathering Sequence

```mermaid
sequenceDiagram
    autonumber
    participant SM as State Machine
    participant P as Planner
    participant TS as Transaction<br/>Specialist
    participant SS as Shipping<br/>Specialist
    participant CS as Customer<br/>Specialist
    participant A as Aggregator
    participant PP as Payment<br/>Platform
    participant SC as Shipping<br/>Carrier
    
    SM->>P: Gather evidence for Fraud (10.4)
    
    Note over P: Analyze dispute type<br/>& required evidence
    
    P->>P: Generate evidence plan
    
    par Parallel Evidence Collection
        P->>TS: Collect transaction proof
        TS->>PP: GET /transactions/{id}
        PP-->>TS: Transaction details
        TS->>PP: GET /authorization/{id}
        PP-->>TS: Authorization logs
        TS-->>A: TransactionEvidence
    and
        P->>SS: Collect delivery proof
        SS->>SC: GET /tracking/{number}
        SC-->>SS: Tracking history
        SS->>SC: GET /proof-of-delivery/{id}
        SC-->>SS: POD document
        SS-->>A: ShippingEvidence
    and
        P->>CS: Collect customer history
        CS->>CS: Query internal DB
        CS-->>A: CustomerEvidence
    end
    
    A->>A: Validate completeness
    A->>A: Check for conflicts
    A-->>SM: EvidencePackage
```

---

## 5. LLM Judge Panel Flow

### 5.1 Three-Judge Validation Architecture

```mermaid
flowchart TB
    subgraph Input["Input"]
        EP[Evidence Package]
    end
    
    subgraph JP["LLM Judge Panel"]
        subgraph J1["Evidence Quality Judge"]
            EQ[Evaluator]
            EQT{Score ≥ 0.8?}
        end
        
        subgraph J2["Fabrication Detection Judge"]
            FD[Detector]
            FDT{Score < 0.95?}
        end
        
        subgraph J3["Dispute Validity Judge"]
            DV[Validator]
            DVT{Score ≥ 0.7?}
        end
        
        AGG[Verdict<br/>Aggregator]
    end
    
    subgraph Output["Output"]
        PASS[✅ PASS<br/>Proceed to Submit]
        WARN[⚠️ WARN<br/>Review recommended]
        BLOCK[🛑 BLOCK<br/>Escalate to human]
    end
    
    EP --> EQ
    EP --> FD
    EP --> DV
    
    EQ --> EQT
    FD --> FDT
    DV --> DVT
    
    EQT -->|Yes| AGG
    EQT -->|No| AGG
    FDT -->|Yes| AGG
    FDT -->|No| AGG
    DVT -->|Yes| AGG
    DVT -->|No| AGG
    
    AGG -->|All Pass| PASS
    AGG -->|DV Fail Only| WARN
    AGG -->|EQ Fail or FD Fail| BLOCK
    
    style PASS fill:#c8e6c9
    style WARN fill:#fff9c4
    style BLOCK fill:#ffcdd2
```

### 5.2 Judge Evaluation Sequence

```mermaid
sequenceDiagram
    autonumber
    participant SM as State Machine
    participant JP as Judge Panel
    participant EQ as Evidence<br/>Quality Judge
    participant FD as Fabrication<br/>Judge
    participant DV as Validity<br/>Judge
    participant LLM as LLM Provider<br/>(OpenAI)
    
    SM->>JP: Validate evidence package
    
    Note over JP: Run all judges synchronously<br/>for real-time feedback
    
    par Parallel Judge Evaluations
        JP->>EQ: Evaluate quality
        EQ->>LLM: Structured prompt<br/>(quality criteria)
        LLM-->>EQ: {score: 0.85, reasoning: "..."}
        EQ-->>JP: PASS (0.85 ≥ 0.8)
    and
        JP->>FD: Check fabrication
        FD->>LLM: Structured prompt<br/>(fabrication signals)
        LLM-->>FD: {score: 0.02, reasoning: "..."}
        FD-->>JP: PASS (0.02 < 0.95)
    and
        JP->>DV: Validate dispute
        DV->>LLM: Structured prompt<br/>(validity criteria)
        LLM-->>DV: {score: 0.78, reasoning: "..."}
        DV-->>JP: PASS (0.78 ≥ 0.7)
    end
    
    JP->>JP: Aggregate verdicts
    JP-->>SM: ALL_PASS verdict
    
    Note over SM: Proceed to SUBMIT phase
```

---

## 6. Network Translation Flow

### 6.1 Internal Schema to VROL Conversion

```mermaid
flowchart LR
    subgraph Internal["Internal Domain Model"]
        D[Dispute]
        E[Evidence<br/>Package]
        M[Merchant]
        T[Transaction]
    end
    
    subgraph Translator["VROL Translator"]
        V[Validator]
        MAP[Field Mapper]
        ENC[Encoder]
    end
    
    subgraph VROL["Visa VROL Format"]
        VP[VROL Payload]
        subgraph Fields["VROL Fields"]
            F1[Dispute Condition<br/>Code]
            F2[Transaction<br/>Identifier]
            F3[Evidence<br/>Category Code]
            F4[Document<br/>References]
        end
    end
    
    D --> V
    E --> V
    M --> V
    T --> V
    
    V -->|Validated| MAP
    MAP -->|Mapped| ENC
    ENC --> VP
    
    VP --> F1
    VP --> F2
    VP --> F3
    VP --> F4
    
    style VP fill:#e3f2fd
```

### 6.2 VROL Submission Sequence

```mermaid
sequenceDiagram
    autonumber
    participant SM as State Machine
    participant VT as VROL Translator
    participant S3 as S3 Storage
    participant VISA as Visa VROL API
    participant EL as Explainability<br/>Layer
    
    SM->>VT: Submit dispute response
    
    Note over VT: Map internal fields<br/>to VROL schema
    
    VT->>VT: Validate required fields
    VT->>VT: Map reason code → VROL condition
    VT->>VT: Encode evidence documents
    
    VT->>S3: Upload evidence files
    S3-->>VT: Document URLs
    
    VT->>VT: Build VROL payload
    
    VT->>VISA: POST /disputes/{id}/response
    
    alt Success
        VISA-->>VT: 200 OK, Case ID: VROL-789456
        VT->>EL: Log submission success
        VT-->>SM: SubmissionResult(success)
    else Network Error
        VISA-->>VT: 503 Service Unavailable
        VT->>VT: Retry (1s, 2s, 4s)
        VT->>VISA: Retry POST
        VISA-->>VT: 200 OK
        VT-->>SM: SubmissionResult(success, retried)
    else Validation Error
        VISA-->>VT: 400 Bad Request
        VT->>EL: Log validation failure
        VT-->>SM: SubmissionResult(failure, errors)
    end
```

---

## 7. Explainability Layer Flow

### 7.1 Four Pillars Architecture

```mermaid
flowchart TB
    subgraph Events["System Events"]
        AE[Agent Events]
        JE[Judge Events]
        SE[State Events]
        UE[User Events]
    end
    
    subgraph EL["Explainability Layer"]
        subgraph BB["BlackBox Recorder"]
            BBR[Record all<br/>agent inputs/outputs]
        end
        
        subgraph AF["AgentFacts"]
            AFR[Capture agent<br/>assertions & decisions]
        end
        
        subgraph GR["GuardRails"]
            GRR[Log validation<br/>results & blocks]
        end
        
        subgraph PL["PhaseLogger"]
            PLR[Track state<br/>transitions & timing]
        end
    end
    
    subgraph Storage["Storage"]
        S3[(S3<br/>BlackBox)]
        TS[(TimescaleDB<br/>Audit Logs)]
        R[(Redis<br/>Session State)]
    end
    
    subgraph Output["Outputs"]
        AT[Audit Trail<br/>JSON Export]
        DB[Dashboard<br/>Metrics]
        AL[Alert<br/>Notifications]
    end
    
    AE --> BB
    JE --> BB
    AE --> AF
    JE --> GR
    SE --> PL
    UE --> PL
    
    BB --> S3
    AF --> TS
    GR --> TS
    PL --> R
    PL --> TS
    
    S3 --> AT
    TS --> AT
    TS --> DB
    GR --> AL
    
    style BB fill:#e3f2fd
    style AF fill:#e8f5e9
    style GR fill:#fff3e0
    style PL fill:#fce4ec
```

### 7.2 Audit Trail Generation Sequence

```mermaid
sequenceDiagram
    autonumber
    participant A as Agent
    participant EL as Explainability<br/>Layer
    participant BB as BlackBox
    participant AF as AgentFacts
    participant PL as PhaseLogger
    participant S3 as S3
    participant TS as TimescaleDB
    
    Note over A,TS: Every agent action is traced
    
    A->>EL: Agent executing action
    
    par Parallel Logging
        EL->>BB: Record input context
        BB->>S3: Store full context blob
    and
        EL->>AF: Record assertion
        AF->>TS: INSERT agent_fact
    and
        EL->>PL: Log phase entry
        PL->>TS: INSERT phase_log
    end
    
    A->>A: Execute action
    A->>EL: Action complete
    
    par Parallel Result Logging
        EL->>BB: Record output
        BB->>S3: Append to blob
    and
        EL->>AF: Record decision
        AF->>TS: INSERT agent_decision
    and
        EL->>PL: Log phase exit
        PL->>TS: UPDATE phase_log
    end
    
    Note over TS: 7-year retention policy
```

---

## 8. Error Handling & Escalation Flow

### 8.1 Escalation Decision Tree

```mermaid
flowchart TB
    subgraph Trigger["Escalation Triggers"]
        T1[Judge BLOCK<br/>Fabrication detected]
        T2[Deadline <24h<br/>Insufficient evidence]
        T3[Max retries<br/>exceeded]
        T4[Classification<br/>failed]
        T5[User requested<br/>human help]
    end
    
    subgraph Decision["Escalation Decision"]
        ED{Escalation<br/>Type?}
    end
    
    subgraph Actions["Escalation Actions"]
        A1[📧 Email ops team]
        A2[💬 Slack alert]
        A3[📋 Create ticket]
        A4[📞 Priority callback]
    end
    
    subgraph Queue["Escalation Queue"]
        Q1[Low Priority<br/>24h SLA]
        Q2[Medium Priority<br/>4h SLA]
        Q3[High Priority<br/>1h SLA]
        Q4[Critical<br/>Immediate]
    end
    
    T1 --> ED
    T2 --> ED
    T3 --> ED
    T4 --> ED
    T5 --> ED
    
    ED -->|Fabrication| Q4
    ED -->|Deadline| Q3
    ED -->|Retry fail| Q2
    ED -->|Classification| Q2
    ED -->|User request| Q1
    
    Q4 --> A1 & A2 & A4
    Q3 --> A1 & A2
    Q2 --> A1 & A3
    Q1 --> A3
    
    style Q4 fill:#ffcdd2
    style Q3 fill:#fff9c4
    style Q2 fill:#c8e6c9
    style Q1 fill:#e3f2fd
```

### 8.2 Retry & Recovery Sequence

```mermaid
sequenceDiagram
    autonumber
    participant SM as State Machine
    participant VT as VROL Translator
    participant VISA as Visa VROL API
    participant EL as Explainability<br/>Layer
    participant ESC as Escalation<br/>Handler
    
    SM->>VT: Submit to Visa
    
    loop Retry up to 3 times
        VT->>VISA: POST /disputes/response
        
        alt Success
            VISA-->>VT: 200 OK
            VT-->>SM: Success
            Note over SM: Continue to MONITOR
        else Transient Error (5xx)
            VISA-->>VT: 503 Service Unavailable
            VT->>EL: Log retry attempt
            VT->>VT: Wait (exponential backoff)
            Note over VT: Wait 1s, 2s, 4s
        else Permanent Error (4xx)
            VISA-->>VT: 400 Bad Request
            VT->>EL: Log permanent failure
            VT-->>SM: Failure (non-retryable)
            Note over SM: Handle error
        end
    end
    
    Note over VT: Max retries exceeded
    
    VT->>EL: Log max retries
    VT->>ESC: Trigger escalation
    ESC->>ESC: Create HIGH priority ticket
    ESC-->>SM: Escalation created
    
    SM->>SM: Transition to ESCALATE state
```

---

## 9. Data Flow Diagram

### 9.1 Complete Data Flow

```mermaid
flowchart TB
    subgraph Users["Users"]
        M[👤 Merchant]
        A[🔍 Auditor]
        O[👔 Ops Lead]
    end
    
    subgraph Chatbot["Dispute Resolution Chatbot"]
        UI[Chainlit UI]
        SM[State Machine]
        HEG[Evidence Gatherer]
        JP[Judge Panel]
        VT[VROL Translator]
        EL[Explainability Layer]
    end
    
    subgraph External["External Systems"]
        PP[Payment Platforms]
        SC[Shipping Carriers]
        LLM[LLM Provider]
        VISA[Visa VROL]
    end
    
    subgraph Storage["Storage"]
        R[(Redis)]
        S3[(S3)]
        TS[(TimescaleDB)]
        PG[(PostgreSQL)]
    end
    
    %% User flows
    M <-->|Chat messages| UI
    A -->|Audit queries| EL
    O -->|Escalation mgmt| SM
    
    %% Internal flows
    UI <--> SM
    SM <--> HEG
    SM <--> JP
    SM <--> VT
    SM --> EL
    HEG --> EL
    JP --> EL
    VT --> EL
    
    %% External flows
    HEG -->|Transaction queries| PP
    PP -->|Transaction data| HEG
    HEG -->|Tracking queries| SC
    SC -->|Tracking/POD| HEG
    JP -->|Judge prompts| LLM
    LLM -->|Evaluations| JP
    VT -->|VROL payload| VISA
    VISA -->|Case ID/Status| VT
    
    %% Storage flows
    UI <-->|Session state| R
    EL -->|BlackBox recordings| S3
    EL -->|Audit logs| TS
    SM <-->|Domain entities| PG
    VT -->|Evidence files| S3
```

---

## 10. Security Flow Diagram

### 10.1 Request Flow Through Security Layers

```mermaid
flowchart TB
    subgraph Internet["Internet (Untrusted)"]
        MB[Merchant Browser]
        VN[Visa Network]
    end
    
    subgraph Edge["Edge Layer"]
        WAF[WAF<br/>PAN Detection]
        CF[CloudFront<br/>DDoS Protection]
    end
    
    subgraph Gateway["Gateway Layer"]
        ALB[Application<br/>Load Balancer]
        AUTH[Authentication<br/>Service]
    end
    
    subgraph App["Application Layer (VPC)"]
        GR[GuardRails<br/>PCI Scan]
        PII[PII Redactor]
        CB[Chatbot Service]
        VG[VROL Gateway<br/>mTLS]
    end
    
    subgraph Data["Data Layer (Encrypted)"]
        R[(Redis<br/>TDE)]
        PG[(PostgreSQL<br/>TDE)]
        S3[(S3<br/>SSE-KMS)]
    end
    
    MB -->|TLS 1.3| CF
    CF --> WAF
    WAF -->|Clean traffic| ALB
    ALB --> AUTH
    AUTH -->|JWT token| GR
    GR -->|Validated| PII
    PII -->|Redacted| CB
    CB <--> R
    CB <--> PG
    CB <--> S3
    CB --> VG
    VG -->|mTLS| VN
    
    style WAF fill:#ffcdd2
    style GR fill:#fff3e0
    style PII fill:#e8f5e9
```

---

## 11. Deployment Flow

### 11.1 CI/CD Pipeline

```mermaid
flowchart LR
    subgraph Dev["Development"]
        C[Code Change]
        PR[Pull Request]
    end
    
    subgraph CI["Continuous Integration"]
        L[Lint & Format]
        UT[Unit Tests]
        IT[Integration Tests]
        SEC[Security Scan]
    end
    
    subgraph Build["Build"]
        D[Docker Build]
        P[Push to ECR]
    end
    
    subgraph CD["Continuous Deployment"]
        STG[Deploy to<br/>Staging]
        ST[Staging Tests]
        PROD[Deploy to<br/>Production]
    end
    
    subgraph Monitor["Monitoring"]
        M[Metrics]
        A[Alerts]
        R[Rollback]
    end
    
    C --> PR
    PR --> L
    L --> UT
    UT --> IT
    IT --> SEC
    SEC --> D
    D --> P
    P --> STG
    STG --> ST
    ST -->|Pass| PROD
    ST -->|Fail| R
    PROD --> M
    M --> A
    A -->|Critical| R
    
    style PROD fill:#c8e6c9
    style R fill:#ffcdd2
```

---

## 12. Version History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0.0 | 2025-12-08 | Claude | Initial flow diagrams document |

---

## 13. References

- System Context: `design/00_system_context.md`
- Domain Model: `design/02_domain_model.md` (pending)
- PRD: Merchant Dispute Resolution Chatbot PRD
- Lesson 16: Orchestrator Patterns
- Lesson 17: Explainability Framework

