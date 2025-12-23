# Domain Model: Merchant Dispute Resolution Chatbot

**Document ID:** design/02_domain_model
**Version:** 1.0.0
**Last Updated:** 2025-12-08
**Status:** Phase 0 Foundation

---

## 1. Overview

### Purpose

This document defines the core domain entities for the Merchant Dispute Resolution Agentic Chatbot. It serves as the foundation for:

- **Pydantic schemas** (`synthetic_data/schemas.py`) for synthetic data generation
- **Database tables** (`design/05_data_architecture.md`) for persistence
- **API contracts** (`design/04_api_specifications/`) for component interfaces
- **State machine transitions** for compliance-critical workflow

### Scope

- **Network:** Visa only (Phase 1 MVP)
- **Dispute Types:** Fraud (10.4), Product Not Received (13.1)
- **Entities:** 7 core domain entities

### Design Principles

1. **Immutability for Audit:** AuditLog entries are append-only
2. **Traceability:** All entities link to trace_id for debugging
3. **PCI Compliance:** No PAN/CVV storage; PII redacted in logs
4. **Deadline Awareness:** All date calculations follow Reg E/Z timelines

---

## 2. Entity Definitions

### 2.1 Dispute

The central entity representing a payment dispute initiated against a merchant.

#### Attributes

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `id` | `uuid` | Yes | Unique dispute identifier |
| `external_id` | `string` | No | Network-assigned case ID (e.g., Visa ARN) |
| `status` | `DisputeStatus` | Yes | Current workflow phase |
| `reason_code` | `ReasonCode` | Yes | Dispute classification |
| `network` | `Network` | Yes | Card network (Visa for Phase 1) |
| `amount` | `decimal` | Yes | Disputed transaction amount (USD) |
| `currency` | `string` | Yes | ISO 4217 currency code (default: USD) |
| `deadline` | `datetime` | Yes | Evidence submission deadline |
| `dispute_date` | `datetime` | Yes | Date dispute was filed |
| `transaction_id` | `string` | Yes | Original transaction reference |
| `transaction_date` | `datetime` | Yes | Original transaction timestamp |
| `merchant_id` | `uuid` | Yes | Foreign key to Merchant |
| `created_at` | `datetime` | Yes | Record creation timestamp |
| `updated_at` | `datetime` | Yes | Last modification timestamp |
| `ce3_eligible` | `boolean` | No | Compelling Evidence 3.0 qualification flag |
| `ce3_prior_transactions` | `list[string]` | No | IDs of qualifying prior transactions |

#### Enums

**DisputeStatus:**
```
CLASSIFY        # Initial classification phase
GATHER_EVIDENCE # Evidence collection in progress
VALIDATE        # Judge validation phase
SUBMIT          # Network submission phase
MONITOR         # Awaiting network decision
RESOLVED_WON    # Dispute won by merchant
RESOLVED_LOST   # Dispute won by cardholder
ESCALATED       # Human review required
EXPIRED         # Deadline passed without submission
```

**ReasonCode:**
```
FRAUD_10_4      # Fraud - Card Not Present
PNR_13_1        # Product Not Received
SUBSCRIPTION_13_2  # Subscription Canceled (Phase 2)
```

**Network:**
```
VISA            # Visa (Phase 1)
MASTERCARD      # Mastercard (Phase 2)
```

#### Business Rules

1. **Deadline Calculation:** `deadline = dispute_date + 14 days` (per Visa regulations)
2. **Status Transitions:** Must follow state machine: CLASSIFY → GATHER_EVIDENCE → VALIDATE → SUBMIT → MONITOR → RESOLVED_*
3. **CE 3.0 Eligibility:** Requires ≥2 prior undisputed transactions from same cardholder within 120 days
4. **Immutable Fields:** `id`, `dispute_date`, `transaction_id`, `merchant_id` cannot be modified after creation

#### Relationships

- **belongs_to** `Merchant` (N:1)
- **has_many** `Evidence` (1:N)
- **has_one** `Submission` (1:1)
- **has_one** `Conversation` (1:1)
- **has_many** `AuditLog` (1:N)

---

### 2.2 Evidence

Supporting documentation and data used to defend a dispute.

#### Attributes

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `id` | `uuid` | Yes | Unique evidence identifier |
| `dispute_id` | `uuid` | Yes | Foreign key to Dispute |
| `type` | `EvidenceType` | Yes | Category of evidence |
| `source` | `EvidenceSource` | Yes | Origin of evidence |
| `source_reference` | `string` | No | External reference (tracking #, transaction ID) |
| `content` | `json` | Yes | Structured evidence data |
| `file_path` | `string` | No | S3 path for document storage |
| `quality_score` | `float` | No | Judge-assigned quality (0.0-1.0) |
| `hash` | `string` | Yes | SHA-256 hash for integrity verification |
| `timestamp` | `datetime` | Yes | When evidence was collected |
| `validated_at` | `datetime` | No | When judge validation completed |
| `validated_by` | `uuid` | No | Foreign key to Judge that validated |
| `created_at` | `datetime` | Yes | Record creation timestamp |

#### Enums

**EvidenceType:**
```
# Transaction Evidence
PRIOR_TRANSACTION       # CE 3.0 qualifying transaction
TRANSACTION_RECEIPT     # Original transaction record
AUTHORIZATION_LOG       # Card authorization details

# Shipping Evidence
TRACKING_NUMBER         # Carrier tracking ID
PROOF_OF_DELIVERY       # POD document/signature
DELIVERY_PHOTO          # Photo confirmation

# Customer Evidence
DEVICE_FINGERPRINT      # Device identification data
IP_ADDRESS              # Transaction IP geolocation
EMAIL_MATCH             # Email consistency verification
CUSTOMER_COMMUNICATION  # Email/chat history with customer

# Other
MERCHANT_POLICY         # Return/refund policy documentation
CUSTOM                  # Other supporting evidence
```

**EvidenceSource:**
```
SYSTEM_AUTO             # Automatically retrieved from integrated systems
MERCHANT_PROVIDED       # Uploaded by merchant
CARRIER_API             # Retrieved from shipping carrier API
PLATFORM_API            # Retrieved from payment platform (Stripe/Square)
MANUAL_ENTRY            # Manually entered data
```

#### Business Rules

1. **Hash Verification:** `hash` must match SHA-256 of `content` to prevent tampering
2. **Source Verification:** `source` must be one of approved sources; MANUAL_ENTRY triggers additional validation
3. **Quality Threshold:** Evidence with `quality_score < 0.5` generates warning
4. **Timestamp Ordering:** `timestamp` must be ≤ `dispute_date` (evidence cannot post-date dispute)
5. **CE 3.0 Requirements:** PRIOR_TRANSACTION evidence must include matching device fingerprint OR IP OR email

#### Relationships

- **belongs_to** `Dispute` (N:1)
- **validated_by** `Judge` (N:1)

---

### 2.3 Merchant

The business entity defending against disputes.

#### Attributes

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `id` | `uuid` | Yes | Unique merchant identifier |
| `external_id` | `string` | No | Platform merchant ID (Stripe acct_xxx) |
| `name` | `string` | Yes | Business name |
| `platform` | `Platform` | Yes | Payment platform |
| `tier` | `MerchantTier` | Yes | Service tier (affects priority) |
| `industry` | `string` | No | Business category (MCC-based) |
| `mcc` | `string` | No | Merchant Category Code |
| `win_rate` | `float` | No | Historical dispute win rate (0.0-1.0) |
| `total_disputes` | `int` | No | Total disputes filed against merchant |
| `settings` | `json` | No | Merchant preferences and configurations |
| `created_at` | `datetime` | Yes | Record creation timestamp |
| `updated_at` | `datetime` | Yes | Last modification timestamp |

#### Enums

**Platform:**
```
DIRECT          # Direct Visa merchant
STRIPE          # Stripe payment processing
SQUARE          # Square payment processing
SHOPIFY         # Shopify Payments
ADYEN           # Adyen payment processing
OTHER           # Other payment processor
```

**MerchantTier:**
```
SMALL_BUSINESS  # < $1M annual revenue
MID_MARKET      # $1M - $50M annual revenue
ENTERPRISE      # > $50M annual revenue
```

#### Business Rules

1. **Tier Priority:** ENTERPRISE disputes processed with higher priority
2. **Win Rate Calculation:** `win_rate = RESOLVED_WON / (RESOLVED_WON + RESOLVED_LOST)`
3. **Settings Defaults:** Include notification preferences, auto-submit thresholds, escalation contacts

#### Relationships

- **has_many** `Dispute` (1:N)

---

### 2.4 Judge

LLM-based evaluation component that validates evidence quality and detects issues.

#### Attributes

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `id` | `uuid` | Yes | Unique judge identifier |
| `type` | `JudgeType` | Yes | Judge evaluation dimension |
| `name` | `string` | Yes | Human-readable judge name |
| `description` | `string` | No | Judge purpose description |
| `threshold` | `float` | Yes | Minimum passing score (0.0-1.0) |
| `is_blocking` | `boolean` | Yes | Does failure block phase transition? |
| `model_version` | `string` | Yes | LLM model identifier (e.g., gpt-4o) |
| `prompt_hash` | `string` | Yes | SHA-256 of prompt template for versioning |
| `prompt_template` | `string` | Yes | Judge prompt template |
| `created_at` | `datetime` | Yes | Record creation timestamp |
| `updated_at` | `datetime` | Yes | Last modification timestamp |
| `calibration_date` | `datetime` | No | Last calibration against golden set |
| `calibration_accuracy` | `float` | No | Accuracy on golden set (0.0-1.0) |

#### Enums

**JudgeType:**
```
EVIDENCE_QUALITY        # Is evidence sufficient for network submission?
FABRICATION_DETECTION   # Did agent fabricate/hallucinate evidence?
DISPUTE_VALIDITY        # Is this a legitimate defense strategy?
```

#### Business Rules

1. **Blocking vs Warning:**
   - `EVIDENCE_QUALITY` (threshold: 0.8) - **Blocking**
   - `FABRICATION_DETECTION` (threshold: 0.95) - **Blocking**
   - `DISPUTE_VALIDITY` (threshold: 0.7) - **Warning only**
2. **Prompt Versioning:** Any prompt change requires new `prompt_hash` and recalibration
3. **Calibration Requirement:** Judge must achieve ≥90% accuracy on golden set before production use
4. **Latency SLA:** All judges must complete evaluation in <800ms P95

#### Relationships

- **validates** `Evidence` (1:N)
- **recorded_in** `AuditLog` (1:N)

---

### 2.5 Submission

Network submission record for dispute response.

#### Attributes

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `id` | `uuid` | Yes | Unique submission identifier |
| `dispute_id` | `uuid` | Yes | Foreign key to Dispute |
| `network_case_id` | `string` | No | Network-assigned case ID |
| `status` | `SubmissionStatus` | Yes | Submission state |
| `payload` | `json` | Yes | VROL-formatted submission data |
| `payload_hash` | `string` | Yes | SHA-256 of payload for integrity |
| `response` | `json` | No | Network response data |
| `submitted_at` | `datetime` | No | Submission timestamp |
| `acknowledged_at` | `datetime` | No | Network acknowledgment timestamp |
| `resolved_at` | `datetime` | No | Final resolution timestamp |
| `resolution` | `Resolution` | No | Final dispute outcome |
| `retry_count` | `int` | Yes | Number of submission attempts |
| `last_error` | `string` | No | Most recent error message |
| `created_at` | `datetime` | Yes | Record creation timestamp |
| `updated_at` | `datetime` | Yes | Last modification timestamp |

#### Enums

**SubmissionStatus:**
```
PENDING         # Awaiting submission
SUBMITTED       # Sent to network
ACKNOWLEDGED    # Network confirmed receipt
UNDER_REVIEW    # Network reviewing
RESOLVED        # Final decision received
FAILED          # Submission failed (retry possible)
EXPIRED         # Deadline passed, cannot submit
```

**Resolution:**
```
WON             # Merchant won dispute
LOST            # Cardholder won dispute
WITHDRAWN       # Cardholder withdrew dispute
EXPIRED         # No decision (deadline passed)
```

#### Business Rules

1. **One Submission Per Dispute:** A dispute can have only one active submission
2. **Retry Logic:** Max 3 retries with exponential backoff (1s, 2s, 4s)
3. **Payload Immutability:** Once `status = SUBMITTED`, payload cannot be modified
4. **Deadline Enforcement:** Cannot submit if `NOW() > dispute.deadline`

#### Relationships

- **belongs_to** `Dispute` (1:1)

---

### 2.6 AuditLog

Immutable record of all system actions for compliance and debugging.

#### Attributes

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `id` | `uuid` | Yes | Unique log entry identifier |
| `dispute_id` | `uuid` | No | Foreign key to Dispute (if applicable) |
| `trace_id` | `string` | Yes | Distributed tracing identifier |
| `pillar` | `ExplainabilityPillar` | Yes | Which explainability component logged |
| `event` | `string` | Yes | Event type identifier |
| `severity` | `LogSeverity` | Yes | Log level |
| `timestamp` | `datetime` | Yes | Event timestamp (microsecond precision) |
| `data` | `json` | Yes | Event payload (PII redacted) |
| `agent_id` | `string` | No | Agent that generated the event |
| `session_id` | `string` | No | Conversation session ID |
| `user_id` | `string` | No | Merchant user ID (redacted) |

#### Enums

**ExplainabilityPillar:**
```
BLACKBOX        # BlackBoxRecorder - post-incident analysis
AGENT_FACTS     # AgentFacts - agent capability verification
GUARDRAILS      # GuardRails - PCI/PII validation
PHASE_LOGGER    # PhaseLogger - workflow reasoning
```

**LogSeverity:**
```
DEBUG           # Detailed debugging information
INFO            # General operational events
WARNING         # Potential issues (non-blocking)
ERROR           # Failures requiring attention
CRITICAL        # System-critical failures
```

#### Business Rules

1. **Immutability:** AuditLog entries cannot be modified or deleted
2. **Retention Policy:**
   - BlackBox: 90 days
   - PhaseLogger: 1 year
   - GuardRails violations: 7 years (PCI requirement)
3. **PII Redaction:** All PII (PAN, email, phone) must be redacted before logging
4. **Trace Correlation:** All entries for a request share the same `trace_id`
5. **Timestamp Precision:** Microsecond precision for ordering

#### Relationships

- **belongs_to** `Dispute` (N:1, optional)
- **recorded_by** `Judge` (N:1, optional)

---

### 2.7 Conversation

Multi-turn conversation session between chatbot and merchant.

#### Attributes

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `id` | `uuid` | Yes | Unique conversation identifier |
| `session_id` | `string` | Yes | Chainlit session identifier |
| `dispute_id` | `uuid` | No | Foreign key to Dispute (once identified) |
| `merchant_id` | `uuid` | Yes | Foreign key to Merchant |
| `state` | `ConversationState` | Yes | Current conversation phase |
| `turns` | `list[Turn]` | Yes | Ordered list of conversation turns |
| `turn_count` | `int` | Yes | Number of completed turns |
| `context` | `json` | Yes | Accumulated context for agent |
| `started_at` | `datetime` | Yes | Conversation start timestamp |
| `ended_at` | `datetime` | No | Conversation end timestamp |
| `outcome` | `ConversationOutcome` | No | Final conversation result |
| `created_at` | `datetime` | Yes | Record creation timestamp |
| `updated_at` | `datetime` | Yes | Last modification timestamp |

#### Nested Types

**Turn:**
```python
class Turn:
    turn_number: int          # 1-indexed turn number
    role: TurnRole            # USER or ASSISTANT
    content: str              # Message content
    timestamp: datetime       # Turn timestamp
    tool_calls: list[ToolCall]  # MCP tool invocations (if any)
    phase: DisputeStatus      # Dispute phase during this turn
```

**ToolCall:**
```python
class ToolCall:
    tool_name: str            # MCP tool name
    input: json               # Tool input parameters
    output: json              # Tool output
    duration_ms: int          # Execution time
    success: bool             # Whether call succeeded
```

#### Enums

**ConversationState:**
```
GREETING        # Initial greeting, awaiting dispute ID
CLASSIFYING     # Identifying dispute type
GATHERING       # Collecting evidence
VALIDATING      # Running judge validation
CONFIRMING      # Merchant confirming submission
SUBMITTING      # Sending to network
COMPLETED       # Conversation ended successfully
ESCALATED       # Handed off to human
ABANDONED       # User left without completing
```

**TurnRole:**
```
USER            # Merchant message
ASSISTANT       # Chatbot response
SYSTEM          # System notification
```

**ConversationOutcome:**
```
SUBMITTED       # Evidence submitted to network
ESCALATED       # Handed to human agent
ABANDONED       # User left mid-conversation
ERROR           # System error prevented completion
```

#### Business Rules

1. **Turn Limit:** Target ≤5 turns for happy path; warn at turn 7, escalate at turn 10
2. **Context Accumulation:** Each turn adds to `context` for next agent response
3. **State Persistence:** Conversation state survives container restarts (Redis backup)
4. **Session Timeout:** Conversations expire after 30 minutes of inactivity
5. **Tool Call Logging:** All MCP tool calls must be logged with timing

#### Relationships

- **belongs_to** `Dispute` (1:1)
- **belongs_to** `Merchant` (N:1)

---

## 3. Entity Relationship Diagram

See `design/02_domain_model.mmd` for the visual diagram.

### Relationship Summary

| From Entity | Relationship | To Entity | Cardinality | Notes |
|-------------|--------------|-----------|-------------|-------|
| Merchant | has_many | Dispute | 1:N | One merchant can have many disputes |
| Dispute | has_many | Evidence | 1:N | One dispute can have multiple evidence items |
| Dispute | has_one | Submission | 1:1 | One submission per dispute |
| Dispute | has_one | Conversation | 1:1 | One conversation per dispute |
| Dispute | has_many | AuditLog | 1:N | Many audit entries per dispute |
| Evidence | validated_by | Judge | N:1 | Judge validates multiple evidence items |
| Judge | recorded_in | AuditLog | 1:N | Judge actions logged |
| Conversation | belongs_to | Merchant | N:1 | Merchant has many conversations |

---

## 4. Business Rules Summary

### Cross-Entity Constraints

| Rule | Entities Involved | Constraint | Enforcement |
|------|-------------------|------------|-------------|
| BR-001 | Dispute, Submission | Cannot submit past deadline | Application + DB trigger |
| BR-002 | Dispute, Evidence | Evidence timestamp ≤ dispute_date | Application validation |
| BR-003 | Judge, Dispute | Blocking judges gate phase transitions | State machine logic |
| BR-004 | Evidence, AuditLog | Evidence hash changes must be logged | Application trigger |
| BR-005 | Conversation, Dispute | Conversation links to dispute once identified | Application logic |
| BR-006 | Merchant, Dispute | Win rate recalculated on resolution | Database trigger |

### Deadline Rules (Reg E/Z Compliance)

| Event | Deadline | Calculation |
|-------|----------|-------------|
| Evidence submission | 14 days | `dispute_date + 14 calendar days` |
| CE 3.0 prior transactions | 120 days | Must be within 120 days of dispute |
| Network response | 30 days | `submission_date + 30 business days` |

### CE 3.0 Qualification Rules

For a dispute to qualify for Compelling Evidence 3.0:

1. **Prior Transactions:** ≥2 undisputed transactions from same cardholder
2. **Time Window:** Within 120 days of disputed transaction
3. **Matching Criteria:** At least 2 of:
   - Same device fingerprint
   - Same IP address
   - Same email address
   - Same shipping address

---

## 5. Mapping to Implementation

### Pydantic Schema Mapping (Task 6.1)

| Entity | Pydantic Model | Location |
|--------|----------------|----------|
| Dispute | `SyntheticDispute` | `synthetic_data/schemas.py` |
| Evidence | `SyntheticEvidence` | `synthetic_data/schemas.py` |
| Merchant | `SyntheticMerchant` | `synthetic_data/schemas.py` |
| Judge | `JudgeConfig` | `judges/schemas.py` |
| Submission | `SubmissionPayload` | `schemas/submission.py` |
| AuditLog | `AuditEntry` | `utils/audit.py` |
| Conversation | `ConversationState` | `chainlit/state.py` |

### Database Table Mapping (Task 4.2)

| Entity | Primary Table | Secondary Tables |
|--------|--------------|------------------|
| Dispute | `disputes` | - |
| Evidence | `evidence` | `evidence_files` (S3 references) |
| Merchant | `merchants` | `merchant_settings` |
| Judge | `judges` | `judge_calibrations` |
| Submission | `submissions` | - |
| AuditLog | `audit_logs` (TimescaleDB) | - |
| Conversation | `conversations` | `conversation_turns` |

---

## 6. Version History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0.0 | 2025-12-08 | Claude | Initial domain model for Phase 1 MVP |

---

## 7. References

- PRD Section 13: Domain Model Table (lines 855-866)
- PRD Section 6: Functional Requirements (FR-1 through FR-6)
- PRD Section 7: Design Considerations
- Visa VROL Documentation (SPIKE-001)
- CE 3.0 Requirements (Visa Compelling Evidence 3.0 Program Guide)
