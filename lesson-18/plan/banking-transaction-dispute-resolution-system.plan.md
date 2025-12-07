<!-- banking-dispute-resolution-2025-12-02 -->
# Banking Transaction Dispute Resolution System - Complete Plan

## Overview

Design a comprehensive banking transaction dispute resolution system that handles disputes from multiple channels (screenshot, phone, email, mobile app, chatbot) with AI-powered orchestration, fraud detection, and compliance management.

## Problem Analysis (Polya's Framework)

### 1. What are the DATA?

**Known Data Points:**
- **Dispute Channels**: Screenshot (bank statement), Phone call (help desk), Email, Mobile app, Chatbot
- **Transaction Information Available**: Transaction ID, amount, date, vendor/merchant name, account number
- **Customer Information**: Customer ID, account details, authentication status
- **Dispute Reasons**: Unauthorized transaction, duplicate transaction, not approved by customer, vendor error, fraud, billing error, service not received

**Data Sources:**
- Bank statement screenshots/images
- Call center transcripts/recordings
- Email content and attachments
- Mobile app form submissions
- Chatbot conversation logs
- Core banking system (transaction records)
- Customer profile database
- Historical dispute records
- Fraud detection databases
- Merchant/vendor databases

### 2. What is the CONDITION?

**Functional Conditions:**
- System must accept disputes from 5 different channels
- System must validate customer identity and account ownership
- System must retrieve and analyze transaction details
- System must classify dispute type and reason
- System must determine if dispute is valid (fraud check, duplicate check, authorization verification)
- System must route disputes to appropriate resolution workflow
- System must provide status updates to customers
- System must maintain audit trail for compliance
- System must integrate with existing banking systems

**Non-Functional Conditions:**
- Security: PCI DSS, SOX, FFIEC compliance
- Performance: Process disputes within SLA (e.g., 24-48 hours)
- Scalability: Handle peak loads (e.g., 10,000+ disputes/day)
- Availability: 99.9% uptime
- Data Privacy: PII/PHI protection, GDPR compliance
- Auditability: Complete audit trail for regulatory requirements

### 3. Is it possible to satisfy the condition?

**YES** - Technically feasible with modern AI/ML, OCR, NLP, and workflow orchestration technologies.

### 4. Is the condition sufficient to determine the unknown?

**PARTIALLY SUFFICIENT** - Key unknowns identified in the detailed plan below.

### 5. Is the condition insufficient, redundant, or contradictory?

**INSUFFICIENT** - Missing business rules, integration specs, and regulatory variations.

---

## Regulatory Requirements

### Regulation E (Electronic Fund Transfer Act)
- **Consumer Reporting Window**: 60 days from statement date to report unauthorized/erroneous transactions
- **Initial Investigation**: 10 business days to investigate and resolve
- **Extended Investigation**: Up to 45 days if more time needed, but must provide provisional credit within 10 business days
- **Consumer Liability**: 
  - Report within 2 business days: $50 max liability
  - Report within 60 days: $500 max liability
  - After 60 days: Unlimited liability
- **Provisional Credit**: Required if investigation extends beyond 10 business days
- **Documentation**: Must provide terminal receipts and periodic statements
- **Applicability**: Consumer accounts only (not business/commercial)

### Fair Credit Billing Act (FCBA)
- **Consumer Reporting Window**: 60 days from statement date
- **Acknowledgment**: Issuer must acknowledge within 30 days
- **Resolution**: Within 2 billing cycles, not exceeding 90 days
- **Applicability**: Credit card billing errors

### Card Network Timeframes
**Visa**:
- Merchant response: 20 days
- Pre-arbitration: 20 days after merchant response
- Arbitration: 10 days to request

**Mastercard**:
- Merchant response: 45 days
- Additional information: 18 days
- Pre-arbitration: 45 days
- Arbitration: 45 days after decision

**American Express**:
- Merchant response: 20 days (firm reply-by date)

**Discover**:
- Ticket Retrieval: ~20 days
- Appeal steps: ~30 days

### FFIEC Requirements
- **Audit Trails**: Comprehensive logging of all transactions and actions
- **Risk Assessment**: Regular evaluation of vulnerabilities
- **Data Privacy**: GLBA compliance for customer data protection
- **Incident Response**: Documented plans for detection and response
- **Business Continuity**: Strategies for operational resilience
- **Vendor Risk Management**: Third-party compliance assessment

### PCI DSS Requirements
- **IDS/IPS**: Intrusion detection and prevention systems
- **Monitoring**: Continuous network monitoring and testing
- **Security Policy**: Formalized information security policies
- **Penalties**: $5,000-$100,000/month for non-compliance

---

## Business Rules & SLA Targets

### Dispute Resolution Timeframes (Recommended SLAs)
**Based on Priority**:
- **Critical** (Fraud, high-value): 4 hours initial response, 24 hours resolution
- **High** (Unauthorized, >$1000): 1 business day resolution
- **Medium** (Billing errors, duplicates): 3 business days resolution
- **Low** (Service issues, minor errors): 5 business days resolution

**Regulatory Compliance SLAs**:
- **Regulation E**: 10 business days (with provisional credit if extended)
- **FCBA**: 30 days acknowledgment, 90 days resolution
- **Card Networks**: Adhere to network-specific timeframes (20-45 days)

### Automated vs Manual Review Thresholds
**Auto-Approval Criteria**:
- Duplicate transaction confirmed (exact match)
- Unauthorized transaction with no authorization record
- Low fraud score (<30) AND low amount (<$100)
- Clear billing error (amount mismatch, merchant error)

**Auto-Denial Criteria**:
- High fraud score (>90) with strong evidence
- Transaction authorized with customer consent record
- Customer history shows pattern of false disputes (>5 in 6 months)
- Dispute outside regulatory timeframe (Reg E: >60 days)

**Manual Review Triggers**:
- Medium fraud score (30-70)
- High-value disputes (>$1000)
- Customer dispute history (3-5 disputes in 6 months)
- Complex cases requiring merchant communication
- Regulatory requirement (certain dispute types)
- System confidence < threshold (70%)

### Chargeback Reason Codes Mapping

**Unauthorized Transactions**:
- Visa: 10.4 (Card-Absent Environment)
- Mastercard: 4837 (No Cardholder Authorization)
- Amex: F24 (No Card Member Authorization)
- Discover: UA02 (Unauthorized Transaction)

**Duplicate Billing**:
- Visa: 12.6.1 (Duplicate Processing)
- Mastercard: 4834 (Point-of-Interaction Error)
- Amex: P08 (Duplicate Charge)
- Discover: DP01 (Duplicate Charge)

**Billing Errors**:
- Visa: 12.5 (Incorrect Amount)
- Mastercard: 4859 (Paid by Other Means)
- Amex: P05 (Incorrect Charge Amount)
- Discover: CD40 (Incorrect Transaction Amount)

### Dispute Type Classification Rules
1. **Unauthorized**: Customer claims no authorization
   - Check: Authorization records, 3D Secure, MFA logs
   - Auto-approve if: No authorization record found
   
2. **Duplicate**: Same transaction charged multiple times
   - Check: Transaction ID, amount, date proximity
   - Auto-approve if: Exact duplicate confirmed
   
3. **Not Approved**: Customer claims didn't approve
   - Check: Approval records, consent logs
   - Manual review: Required for high-value
   
4. **Billing Error**: Incorrect amount or merchant error
   - Check: Amount comparison, merchant records
   - Auto-approve if: Clear amount mismatch
   
5. **Service Not Received**: Product/service not delivered
   - Check: Delivery confirmation, merchant response
   - Manual review: Required (needs merchant communication)

### Fraud Detection Rules
- **Low Risk (0-30)**: Auto-approve if amount <$100
- **Medium Risk (31-70)**: Manual review required
- **High Risk (71-90)**: Fraud investigation team
- **Critical Risk (91-100)**: Immediate escalation, possible law enforcement

### Customer History Rules
- **First Dispute**: Standard processing
- **2-3 Disputes (6 months)**: Enhanced verification
- **4-5 Disputes (6 months)**: Manual review required
- **>5 Disputes (6 months)**: Fraud investigation, possible account review

### Amount-Based Rules
- **<$100**: Auto-process if low risk
- **$100-$500**: Standard processing
- **$500-$1000**: Enhanced verification
- **>$1000**: Manual review required
- **>$5000**: Executive approval required

---

## Integration Specifications

### Core Banking API Requirements
**Authentication**:
- OAuth 2.0 Client Credentials flow
- Token refresh mechanism
- IP whitelisting for production

**Endpoints Required**:
1. `GET /accounts/{accountId}/transactions/{transactionId}`
   - Returns: Transaction details, authorization info, merchant data
   - Response time: <500ms (p95)
   
2. `GET /accounts/{accountId}/transactions`
   - Query params: dateRange, limit, offset
   - Returns: Paginated transaction list
   
3. `POST /accounts/{accountId}/refunds`
   - Input: transactionId, amount, reason
   - Returns: refundId, status
   - Idempotency: Required (idempotency key)
   
4. `GET /customers/{customerId}/accounts`
   - Returns: Account list with status
   
5. `POST /accounts/{accountId}/verify`
   - Input: customerId, verification method
   - Returns: verification status, confidence

**Data Formats**:
- Request/Response: JSON
- Date format: ISO 8601
- Currency: ISO 4217 codes
- Amount: Decimal (2 decimal places)

**Error Handling**:
- HTTP status codes: 200, 400, 401, 403, 404, 429, 500, 503
- Retry logic: Exponential backoff (max 3 retries)
- Circuit breaker: Open after 5 failures in 60 seconds

### Card Network API Specifications

**Visa Chargeback API**:
- Base URL: `https://api.visa.com/chargebacks/v1`
- Authentication: API key + certificate
- Endpoints:
  - `POST /chargebacks` - Initiate chargeback
  - `GET /chargebacks/{id}` - Get status
  - `POST /chargebacks/{id}/representment` - Contest chargeback

**Mastercard Dispute API**:
- Base URL: `https://api.mastercard.com/disputes/v1`
- Authentication: OAuth 1.0a
- Endpoints:
  - `POST /disputes` - Create dispute
  - `GET /disputes/{id}` - Get dispute details
  - `POST /disputes/{id}/accept` - Accept dispute
  - `POST /disputes/{id}/contest` - Contest with evidence

**Rate Limiting**:
- Visa: 100 requests/minute
- Mastercard: 50 requests/minute
- Implement request queuing for rate limit compliance

### Notification Service Specifications

**Email Service (SendGrid)**:
- Templates required:
  - Dispute submitted confirmation
  - Status update notifications
  - Resolution notifications (approved/denied)
  - Document request
- Personalization variables: customer name, dispute ID, amount, status, resolution date
- Delivery tracking: Open rates, click rates, bounce handling

**SMS Service (Twilio)**:
- Message types:
  - Status updates (short)
  - Verification codes (OTP)
  - Urgent notifications
- Character limit: 160 characters
- Two-way SMS: Support for customer responses

**Push Notifications (SNS)**:
- Channels: Mobile app, web browser
- Payload: JSON with title, body, action URL
- Delivery: Real-time, with retry logic

---

## System Architecture

### Multi-Channel Input Layer
- **Screenshot Processing**: OCR service for bank statements, transaction extraction
- **Phone Call Processing**: Voice-to-text, intent extraction, call routing
- **Email Processing**: Email parsing, attachment handling, NLP for intent
- **Mobile App**: Form-based submission, image upload, structured data
- **Chatbot**: Conversational interface, natural language understanding

### Core Processing Layer
- **Dispute Intake Service**: Unified dispute creation from all channels
- **Identity Verification Service**: Validate customer and account ownership
- **Transaction Retrieval Service**: Fetch transaction details from core banking
- **Dispute Classification Service**: Categorize dispute type and reason
- **Fraud Detection Service**: ML-based fraud scoring
- **Duplicate Detection Service**: Identify duplicate disputes
- **Authorization Verification Service**: Check if transaction was authorized

### Orchestration Layer
- **Workflow Engine**: LangGraph-based state machine for dispute lifecycle
- **Routing Service**: Route disputes to appropriate workflow based on type/risk
- **Agent Orchestration**: Multi-agent system for different dispute aspects
- **Human-in-the-Loop**: Escalation to human agents when needed

### Resolution Layer
- **Automated Resolution**: Auto-approve/deny based on rules and ML confidence
- **Manual Review Queue**: Human agent review interface
- **Merchant Communication**: Automated merchant notification and response
- **Refund/Reversal Service**: Execute financial transactions
- **Chargeback Processing**: Integration with card networks

### Notification & Communication Layer
- **Status Update Service**: Notify customers of dispute status changes
- **Multi-channel Notification**: Email, SMS, push notifications, in-app
- **Customer Portal**: Self-service dispute tracking

### Data & Storage Layer
- **Dispute Database**: Store dispute records, status, history
- **Document Storage**: Screenshots, emails, call recordings
- **Transaction Cache**: Fast access to transaction data
- **Audit Log**: Complete audit trail for compliance
- **Analytics Warehouse**: For reporting and ML training

---

## Data Models

### Dispute Entity Schema (DynamoDB)
```typescript
interface Dispute {
  // Primary Keys
  disputeId: string;                    // UUID, Partition Key
  customerId: string;                    // GSI Partition Key
  accountId: string;                    // GSI Partition Key
  
  // Channel Information
  channel: 'screenshot' | 'phone' | 'email' | 'mobile' | 'chatbot';
  channelMetadata: {
    screenshot?: {
      imageUrl: string;                  // S3 URL
      ocrConfidence: number;              // 0-100
      extractedData: TransactionData;
    };
    phone?: {
      callId: string;
      transcriptUrl: string;              // S3 URL
      recordingUrl: string;              // S3 URL
      agentId?: string;
    };
    email?: {
      emailId: string;
      subject: string;
      body: string;
      attachments: string[];              // S3 URLs
    };
    mobile?: {
      appVersion: string;
      deviceId: string;
      formData: Record<string, any>;
    };
    chatbot?: {
      sessionId: string;
      conversationLog: Message[];
    };
  };
  
  // Transaction Information
  transactionId: string;
  transactionDetails: {
    amount: number;
    currency: string;
    date: string;                        // ISO 8601
    merchantName: string;
    merchantId?: string;
    category?: string;
    description: string;
    authorizationCode?: string;
    cardLast4?: string;
    cardType?: string;
  };
  
  // Dispute Classification
  disputeType: 'unauthorized' | 'duplicate' | 'not_approved' | 'billing_error' | 
               'service_not_received' | 'merchant_error' | 'fraud' | 'other';
  disputeReason: string;                 // Free text from customer
  disputeCategory: 'fraud' | 'error' | 'service' | 'authorization';
  
  // Status & Workflow
  status: 'submitted' | 'validating' | 'classifying' | 'investigating' | 
          'pending_merchant' | 'pending_review' | 'approved' | 'denied' | 
          'resolved' | 'closed' | 'cancelled';
  priority: 'low' | 'medium' | 'high' | 'critical';
  workflowId: string;                    // LangGraph workflow instance ID
  currentStep: string;                    // Current state in workflow
  
  // Risk & Fraud Assessment
  fraudScore: number;                    // 0-100, ML model output
  riskLevel: 'low' | 'medium' | 'high' | 'critical';
  fraudIndicators: string[];              // List of detected fraud patterns
  duplicateCheck: {
    isDuplicate: boolean;
    originalDisputeId?: string;
    similarityScore?: number;
  };
  
  // Resolution Information
  resolution?: {
    decision: 'approved' | 'denied' | 'partial' | 'merchant_responsible';
    decisionReason: string;
    decisionDate: string;
    decisionBy: string;                  // Agent ID or 'system'
    refundAmount?: number;
    refundDate?: string;
    chargebackId?: string;
    merchantResponse?: {
      received: boolean;
      responseDate?: string;
      responseText?: string;
    };
  };
  
  // Documents & Evidence
  documents: Array<{
    documentId: string;
    type: 'statement' | 'receipt' | 'email' | 'screenshot' | 'other';
    url: string;                         // S3 URL
    uploadedAt: string;
    verified: boolean;
  }>;
  
  // Timestamps
  submittedAt: string;                   // ISO 8601
  validatedAt?: string;
  classifiedAt?: string;
  investigatedAt?: string;
  resolvedAt?: string;
  closedAt?: string;
  slaDeadline: string;                   // Calculated based on priority
  
  // Audit & Compliance
  auditLog: Array<{
    timestamp: string;
    action: string;
    actor: string;                       // User ID or 'system'
    details: Record<string, any>;
  }>;
  
  // Metadata
  tags: string[];                        // For categorization and search
  notes: string;                         // Internal notes
  customerNotes: string[];               // Customer-visible notes
  ttl?: number;                          // DynamoDB TTL for auto-archival
}
```

### Dispute Lifecycle States (LangGraph)
1. **SUBMITTED** → Validate customer identity → **VALIDATING**
2. **VALIDATING** → Identity verified → **CLASSIFYING**
3. **VALIDATING** → Identity failed → **DENIED** (with reason)
4. **CLASSIFYING** → Classified → **INVESTIGATING**
5. **INVESTIGATING** → Low risk, auto-approve → **APPROVED**
6. **INVESTIGATING** → High risk → **PENDING_REVIEW**
7. **INVESTIGATING** → Needs merchant response → **PENDING_MERCHANT**
8. **PENDING_MERCHANT** → Merchant responded → **INVESTIGATING**
9. **PENDING_REVIEW** → Agent decision → **APPROVED** or **DENIED**
10. **APPROVED** → Refund processed → **RESOLVED**
11. **DENIED** → Customer notified → **CLOSED**
12. **RESOLVED** → All actions complete → **CLOSED**

---

## AI/ML Components

### OCR Model Requirements
- **Technology**: AWS Textract + Custom post-processing
- **Accuracy Target**: >95% for standard bank statements
- **Supported Formats**: PDF, PNG, JPG, JPEG
- **Extraction Fields**: Transaction date, amount, merchant name, description, account number, balance

### NLP for Intent Extraction
- **Technology**: AWS Comprehend + Custom fine-tuning
- **Capabilities**: Intent classification, entity extraction, sentiment analysis
- **Accuracy Target**: >90% for intent classification

### Fraud Detection Model
- **Algorithm**: XGBoost or Neural Network
- **Features**: Customer history, transaction patterns, behavioral anomalies
- **Performance Targets**: Precision >85%, Recall >90%, F1-Score >87%

### Dispute Classification Model
- **Algorithm**: BERT-based transformer (fine-tuned)
- **Classes**: 8 dispute types
- **Accuracy Target**: >92% classification accuracy

### Duplicate Detection Algorithm
- **Method**: Hybrid approach (exact match + fuzzy match)
- **Threshold**: >0.85 similarity = duplicate

---

## Compliance & Security

### PII/PHI Protection
- **Encryption**: At rest (KMS), in transit (TLS 1.3), field-level
- **Data Masking**: Logs, non-production, analytics
- **Access Control**: IAM roles, customer data isolation, RBAC for agents

### Audit Trail Requirements
- **What to Log**: All dispute actions, data access, system decisions, financial transactions, customer communications
- **Storage**: Immutable logs in CloudTrail, DynamoDB audit table, S3 Glacier for long-term
- **Retention**: 7 years for disputes, 10 years for audit logs

### Authentication & Authorization
- **Customer**: MFA for high-value disputes, JWT tokens, session management
- **Agent**: SAML SSO, RBAC, session timeout
- **API**: OAuth 2.0, API keys, rate limiting

### Data Retention Policies
- **Dispute Records**: 7 years after resolution
- **Documents**: 7 years, then archive to Glacier
- **Audit Logs**: 10 years
- **Analytics Data**: Aggregated data retained indefinitely

---

## Monitoring & Analytics

### Key Metrics
**Volume Metrics**:
- Disputes per day/hour by channel
- Disputes by type and status
- Peak load times

**Performance Metrics**:
- Average resolution time (by type, priority)
- SLA compliance rate
- Auto-resolution rate
- Time in each workflow state

**Quality Metrics**:
- Fraud detection accuracy (precision, recall)
- Classification accuracy
- Customer satisfaction scores
- Dispute reversal rate (appeals)

**Business Metrics**:
- Total refund amount
- Fraud loss prevented
- Cost per dispute resolution
- Channel adoption rates

### Dashboards
- **Executive Dashboard**: Overall volume, trends, performance vs. SLA, financial impact
- **Operations Dashboard**: Real-time queue, agent workload, SLA violations, system health
- **Fraud Dashboard**: Fraud detection performance, trends, high-risk disputes
- **Channel Performance Dashboard**: Disputes by channel, channel-specific metrics

### Alerting Rules
- **Critical Alerts**: SLA violation, high fraud score (>90), system errors (>5%), integration failures
- **Warning Alerts**: Queue backlog (>100), agent capacity, model degradation, unusual patterns

### Performance SLAs
**Resolution Time SLAs**:
- Low priority: 5 business days
- Medium priority: 3 business days
- High priority: 1 business day
- Critical: 4 hours

**System Performance SLAs**:
- API response time: <500ms (p95)
- OCR processing: <30 seconds
- Fraud scoring: <2 seconds
- System availability: 99.9%

---

## Implementation Roadmap

### Phase 1: Foundation (Weeks 1-4)
- Set up infrastructure (AWS services, DynamoDB, S3, Lambda)
- Implement authentication and authorization
- Create core data models
- Set up monitoring and logging

### Phase 2: Core Services (Weeks 5-8)
- Implement Dispute Intake Service
- Build Identity Verification Service
- Create Transaction Retrieval Service
- Implement Dispute Classification Service

### Phase 3: AI/ML Integration (Weeks 9-12)
- Integrate OCR service (Textract)
- Build fraud detection model
- Implement NLP for intent extraction
- Create duplicate detection algorithm

### Phase 4: Orchestration (Weeks 13-16)
- Implement LangGraph workflow engine
- Build routing logic
- Create agent orchestration
- Set up human-in-the-loop escalation

### Phase 5: Channel Processors (Weeks 17-20)
- Screenshot OCR processor
- Phone call processing (Transcribe + Comprehend)
- Email parser
- Mobile app API
- Chatbot integration

### Phase 6: Integration & Testing (Weeks 21-24)
- Core banking API integration
- Card network API integration
- Notification services integration
- End-to-end testing
- Performance testing

### Phase 7: Compliance & Security (Weeks 25-28)
- Implement audit trail
- Set up encryption and data masking
- Compliance validation
- Security testing

### Phase 8: Production Deployment (Weeks 29-32)
- Staged rollout
- Monitoring and alerting
- Documentation
- Training

---

## Todos

- [x] Gather missing business requirements: dispute resolution workflows, SLA targets, business rules, regulatory requirements, integration specifications
- [x] Design complete data models: Dispute entity, Transaction entity, Resolution entity, Audit log schema, Document storage schema
- [x] Create detailed architecture diagrams: system architecture, dispute lifecycle state machine, data flow diagram, integration architecture, decision tree for routing
- [x] Design channel-specific processors: Screenshot OCR service, Phone call processing (voice-to-text + NLP), Email parser, Mobile app API, Chatbot integration
- [x] Design core services: Dispute Intake Service, Identity Verification, Transaction Retrieval, Dispute Classification, Fraud Detection, Duplicate Detection, Authorization Verification
- [x] Design workflow orchestration: LangGraph state machine, routing logic, agent orchestration, human-in-the-loop escalation criteria
- [x] Design AI/ML components: OCR model requirements, NLP for intent extraction, fraud detection model (features, training data), dispute classification model, duplicate detection algorithm
- [x] Define integration specifications: Core banking API contracts, card network APIs, notification services, external fraud detection services
- [x] Design compliance and security: PII/PHI protection, audit trail requirements, authentication/authorization, data retention policies
- [x] Design monitoring and analytics: Key metrics, dashboards, alerting rules, performance SLAs

---

## Next Steps

1. **Create Visual Diagrams**: Architecture, data flow, state machines (Mermaid diagrams)
2. **Prototype Key Components**: OCR, fraud detection, classification models
3. **Create Test Scenarios**: Comprehensive test cases for all dispute types and channels
4. **Design API Specifications**: OpenAPI/Swagger specs for all endpoints
5. **Create Implementation Roadmap**: Phased rollout plan with dependencies
6. **Stakeholder Review**: Present plan to business, compliance, and technical teams
