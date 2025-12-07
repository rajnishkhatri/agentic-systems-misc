# Detailed Plan: National US Bank Adoption of Dispute Schema System

## Executive Summary

The dispute schema system is **70% production-ready** for national bank deployment. This plan outlines the complete roadmap to achieve full bank adoption, addressing gaps in issuer-side handling, regulatory compliance, legacy integration, and scale requirements.

---

## Part 1: Current State Analysis

### What's Ready (70%)

| Component | Status | Bank Suitability |
|-----------|--------|------------------|
| Core Dispute Schema | ✅ Complete | Stripe-proven structure, 50+ fields |
| Evidence Management | ✅ Complete | 27 evidence categories, file limits enforced |
| Visa VROL Translation | ✅ Complete | CE 3.0 qualification logic |
| Reg E/Z Deadline Tracking | ✅ Complete | 10/30/45/90 day calculations |
| AWS Step Functions Orchestration | ✅ Complete | State machine for full lifecycle |
| Balance Transaction Ledger | ✅ Complete | Event-sourced financial tracking |
| PCI DSS Tokenization | ✅ Complete | No PAN storage, fingerprint-based matching |

### What's Missing (30%)

| Gap | Impact | Priority |
|-----|--------|----------|
| Issuer-Side Dispute Handling | Banks see both sides; current design is merchant-only | **Critical** |
| Mastercom Full Integration | ~30% of card volume | **High** |
| Mainframe/Core Banking Adapters | Banks run on Fiserv/FIS/Jack Henry | **Critical** |
| OCC/Fed Regulatory Reporting | Examination readiness | **High** |
| Amex/Discover Complete Support | ~15% of card volume | **Medium** |
| Disaster Recovery Architecture | Regulatory requirement | **High** |
| Multi-Tenancy (Subsidiaries) | Large banks have multiple entities | **Medium** |

---

## Part 2: Bank-Specific Requirements

### 2.1 Dual-Role Architecture

Banks operate as **both issuer and acquirer**:

```
┌─────────────────────────────────────────────────────────────────────┐
│                    BANK DUAL-ROLE DISPUTE FLOW                      │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ISSUER ROLE (Cardholder's Bank)                                    │
│  ├── Receive cardholder complaint                                   │
│  ├── Investigate transaction legitimacy                             │
│  ├── Issue provisional credit (Reg E: 10 days)                      │
│  ├── Submit dispute to network                                      │
│  └── Process merchant response                                      │
│                                                                      │
│  ACQUIRER ROLE (Merchant's Bank)                                    │
│  ├── Receive dispute notification from network                      │
│  ├── Forward to merchant                                            │
│  ├── Collect and validate merchant evidence                         │
│  ├── Submit representment to network                                │
│  └── Process network decision                                       │
│                                                                      │
│  INTERNAL DISPUTES (Both Parties Bank with Same Institution)        │
│  ├── Cardholder and merchant both customers                         │
│  ├── Internal adjudication possible                                 │
│  └── Network involvement only if escalated                          │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

### 2.2 Regulatory Examination Requirements

| Regulation | Requirement | System Support Needed |
|------------|-------------|----------------------|
| Reg E (Debit) | Written investigation results within 3 days of decision | Letter generation module |
| Reg E (Debit) | Provisional credit within 10 business days | Automated GL posting |
| Reg Z (Credit) | Acknowledgment within 30 days | Customer notification system |
| OCC Guidance | Dispute ratio monitoring and reporting | Dashboard + alerts |
| BSA/AML | Suspicious pattern detection | Fraud analytics integration |
| UDAAP | Fair treatment documentation | Audit trail completeness |

### 2.3 Core Banking Integration Points

```
┌─────────────────────────────────────────────────────────────────────┐
│                    CORE BANKING INTEGRATION MAP                     │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  FISERV DNA/Precision                                               │
│  ├── Account inquiry (balance, status, history)                     │
│  ├── GL posting (provisional credits, reversals)                    │
│  ├── Customer master (contact info, preferences)                    │
│  └── Transaction history (original charge lookup)                   │
│                                                                      │
│  FIS HORIZON/IBS                                                    │
│  ├── Card management system                                         │
│  ├── Authorization history                                          │
│  ├── Fraud scoring integration                                      │
│  └── Statement generation                                           │
│                                                                      │
│  JACK HENRY SILVERLAKE/EPISYS                                       │
│  ├── Core account processing                                        │
│  ├── Item processing                                                │
│  └── Regulatory reporting feeds                                     │
│                                                                      │
│  CARD PROCESSORS                                                    │
│  ├── TSYS/Global Payments                                           │
│  ├── First Data (Fiserv)                                            │
│  └── Worldpay (FIS)                                                 │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Part 3: Implementation Phases

### Phase 1: Foundation (Weeks 1-12)

#### 1.1 Issuer-Side Schema Extension (Weeks 1-4)

**Objective**: Extend dispute schema to support bank's issuer role

**Deliverables**:
- `IssuerDispute` interface extending base `Dispute`
- Cardholder complaint intake workflow
- Provisional credit automation
- Investigation tracking states

**Schema Additions**:
```typescript
interface IssuerDispute extends Dispute {
  role: 'issuer';
  cardholder_complaint: {
    received_date: number;
    complaint_channel: 'phone' | 'branch' | 'online' | 'mail';
    complaint_narrative: string;
    claimed_fraud_date?: number;
  };
  provisional_credit: {
    required: boolean;
    issued: boolean;
    issued_date?: number;
    amount: number;
    gl_reference?: string;
  };
  investigation: {
    assigned_to?: string;
    started_date?: number;
    completed_date?: number;
    finding: 'valid_dispute' | 'invalid_dispute' | 'pending';
    documentation: string[];
  };
  customer_notification: {
    acknowledgment_sent: boolean;
    acknowledgment_date?: number;
    resolution_letter_sent: boolean;
    resolution_letter_date?: number;
  };
}
```

#### 1.2 Mastercom Full Integration (Weeks 3-6)

**Objective**: Complete Mastercard dispute handling

**Deliverables**:
- Mastercom API client implementation
- Reason code mapping (4837, 4853, 4855, etc.)
- Chargeback and representment flows
- Arbitration support

**Key Mastercom Endpoints**:
| Endpoint | Purpose |
|----------|---------|
| `/cases` | Create/retrieve dispute cases |
| `/chargebacks` | Submit/respond to chargebacks |
| `/retrievals` | Handle retrieval requests |
| `/fees` | Process network fees |

#### 1.3 Core Banking Adapter Framework (Weeks 5-10)

**Objective**: Create abstraction layer for core banking integration

**Deliverables**:
- `CoreBankingAdapter` interface
- Fiserv DNA/Precision implementation
- FIS Horizon implementation
- GL posting automation

**Adapter Interface**:
```typescript
interface CoreBankingAdapter {
  // Account Operations
  getAccountDetails(accountId: string): Promise<AccountDetails>;
  getTransactionHistory(accountId: string, dateRange: DateRange): Promise<Transaction[]>;

  // Financial Operations
  postProvisionalCredit(accountId: string, amount: number, reference: string): Promise<GLEntry>;
  reverseProvisionalCredit(glReference: string): Promise<GLEntry>;
  postFinalAdjustment(accountId: string, amount: number, type: 'credit' | 'debit'): Promise<GLEntry>;

  // Customer Operations
  getCustomerProfile(customerId: string): Promise<CustomerProfile>;
  sendNotification(customerId: string, template: string, data: object): Promise<void>;
}
```

#### 1.4 Regulatory Reporting Module (Weeks 8-12)

**Objective**: Build OCC/Fed examination-ready reporting

**Deliverables**:
- Dispute volume and ratio dashboards
- Reg E/Z compliance tracking reports
- Aging analysis (disputes by days outstanding)
- Resolution outcome analysis
- Audit trail export capability

**Report Types**:
| Report | Frequency | Audience |
|--------|-----------|----------|
| Dispute Ratio Trend | Daily | Operations, Risk |
| Reg E Compliance Status | Daily | Compliance |
| Provisional Credit Aging | Daily | Finance |
| Resolution Outcomes | Weekly | Management |
| Examiner Package | On-demand | Regulators |

---

### Phase 2: Scale & Compliance (Weeks 13-20)

#### 2.1 Multi-Region AWS Deployment (Weeks 13-15)

**Objective**: Achieve high availability and disaster recovery

**Architecture**:
```
┌─────────────────────────────────────────────────────────────────────┐
│                    MULTI-REGION ARCHITECTURE                        │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  PRIMARY: us-east-1 (N. Virginia)                                   │
│  ├── API Gateway + Lambda                                           │
│  ├── Step Functions (dispute workflows)                             │
│  ├── DynamoDB (Global Table - Primary)                              │
│  ├── S3 (Evidence storage - Cross-region replication)               │
│  └── EventBridge (Event distribution)                               │
│                                                                      │
│  SECONDARY: us-west-2 (Oregon)                                      │
│  ├── API Gateway + Lambda (Standby)                                 │
│  ├── Step Functions (Standby)                                       │
│  ├── DynamoDB (Global Table - Replica)                              │
│  ├── S3 (Evidence storage - Replica)                                │
│  └── EventBridge (Event distribution)                               │
│                                                                      │
│  FAILOVER: Route 53 Health Checks + Automatic DNS Failover          │
│                                                                      │
│  RPO: 1 second (DynamoDB Global Tables)                             │
│  RTO: 5 minutes (DNS propagation + Lambda cold start)               │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

#### 2.2 Performance Testing & Optimization (Weeks 14-17)

**Objective**: Validate 100K+ disputes/day throughput

**Test Scenarios**:
| Scenario | Target | Method |
|----------|--------|--------|
| Sustained load | 100K disputes/day (1.16/sec avg) | Load test |
| Peak load | 500 disputes/minute | Spike test |
| Evidence upload | 10K concurrent uploads | Stress test |
| Network timeout | 90-day workflow survival | Longevity test |
| Failover | <5 min RTO | Chaos engineering |

**Performance Targets**:
- API response time: p99 < 200ms
- Evidence processing: p99 < 30 seconds
- Deadline calculation: p99 < 50ms
- Dashboard queries: p99 < 2 seconds

#### 2.3 Security & Compliance Certification (Weeks 16-20)

**Objective**: Achieve SOC 2 Type II readiness

**Controls Required**:
| Control Area | Requirement | Implementation |
|--------------|-------------|----------------|
| Access Control | Role-based access | IAM + Cognito |
| Encryption | At-rest and in-transit | KMS + TLS 1.3 |
| Audit Logging | All access logged | CloudTrail + CloudWatch |
| Data Retention | 7-year retention | S3 lifecycle + Glacier |
| Incident Response | Documented procedures | Runbooks + PagerDuty |
| Vulnerability Management | Regular scanning | Inspector + GuardDuty |

**PCI DSS Validation**:
- Confirm no PAN storage (tokenization only)
- WAF rules blocking PAN in URLs
- Network segmentation for CDE
- Penetration test execution

---

### Phase 3: Optimization (Weeks 21-30)

#### 3.1 ML-Based Win Rate Prediction (Weeks 21-24)

**Objective**: Predict dispute outcomes to prioritize response efforts

**Model Features**:
- Historical win rate by reason code
- Evidence completeness score
- Customer dispute history
- Transaction characteristics
- CE 3.0 eligibility

**Model Output**:
```typescript
interface WinPrediction {
  dispute_id: string;
  predicted_outcome: 'win' | 'loss';
  confidence: number;  // 0.0 - 1.0
  key_factors: string[];
  recommended_actions: string[];
  evidence_gaps: string[];
}
```

#### 3.2 Pre-Dispute Resolution Integration (Weeks 23-26)

**Objective**: Stop disputes before they become chargebacks

**Integrations**:
| Service | Provider | Benefit |
|---------|----------|---------|
| Order Insight | Verifi (Visa) | Real-time merchant data to issuers |
| Consumer Clarity | Ethoca (Mastercard) | Transaction context before dispute |
| Rapid Dispute Resolution | Verifi | Automated refunds for eligible disputes |

**Expected Impact**:
- 15-25% reduction in disputes reaching chargeback
- Improved customer satisfaction
- Lower operational costs

#### 3.3 Automated Evidence Generation (Weeks 25-28)

**Objective**: Auto-populate evidence from bank systems

**Data Sources**:
| Evidence Type | Source System | Automation |
|---------------|---------------|------------|
| Transaction details | Core banking | API pull |
| Authorization data | Card processor | API pull |
| Customer communication | CRM/Salesforce | API pull |
| Delivery confirmation | Merchant integration | Webhook |
| Device fingerprint | Fraud system | API pull |

#### 3.4 Real-Time Fraud Feedback Loop (Weeks 27-30)

**Objective**: Use dispute outcomes to improve fraud detection

**Flow**:
```
Dispute Outcome → Fraud Model Retraining → Authorization Rules Update
       ↓
   - Lost disputes flagged as confirmed fraud
   - Won disputes flagged as false positives
   - Pattern analysis for new fraud vectors
```

---

## Part 4: Risk Mitigation

### Technical Risks

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Mainframe integration delays | High | High | Start early, use middleware (MuleSoft/Boomi) |
| Performance bottlenecks at scale | Medium | High | Load test early, design for horizontal scaling |
| Network API changes | Medium | Medium | Abstract network layer, monitor for updates |
| Data migration errors | Medium | High | Parallel run period, reconciliation checks |

### Operational Risks

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Staff training gaps | High | Medium | Phased rollout, comprehensive training program |
| Process change resistance | Medium | Medium | Executive sponsorship, change management |
| Vendor dependency | Medium | Medium | Multi-vendor strategy, contract SLAs |

### Regulatory Risks

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Examination findings | Medium | High | Pre-examination self-assessment |
| Reg E deadline violations | Low | Critical | Automated enforcement, escalation alerts |
| BSA/AML gaps | Low | Critical | Suspicious activity flagging integration |

---

## Part 5: Success Metrics & KPIs

### Operational Metrics

| Metric | Current State | Target | Timeline |
|--------|---------------|--------|----------|
| Dispute processing time | Unknown | <4 hours | Phase 1 |
| Evidence submission rate | Unknown | >95% before deadline | Phase 1 |
| Automation rate | 0% | >60% auto-resolved | Phase 3 |
| Manual review queue | N/A | <500/day | Phase 2 |

### Financial Metrics

| Metric | Current State | Target | Timeline |
|--------|---------------|--------|----------|
| Dispute win rate | Unknown | >65% | Phase 2 |
| Cost per dispute | Unknown | <$5 operational cost | Phase 3 |
| Loss reduction | Baseline TBD | 20% reduction | Phase 3 |
| Provisional credit aging | Unknown | <10 days average | Phase 1 |

### Compliance Metrics

| Metric | Target | Timeline |
|--------|--------|----------|
| Reg E deadline compliance | 100% | Phase 1 |
| Reg Z deadline compliance | 100% | Phase 1 |
| Dispute ratio | <0.9% (Visa threshold) | Ongoing |
| Examination findings | Zero material findings | Phase 2 |

---

## Part 6: Resource Requirements

### Team Structure

| Role | Count | Phase | Responsibility |
|------|-------|-------|----------------|
| Technical Lead | 1 | All | Architecture, integration decisions |
| Backend Engineers | 3-4 | All | Core development |
| DevOps/SRE | 1-2 | All | Infrastructure, monitoring |
| QA Engineers | 2 | All | Testing, validation |
| Business Analyst | 1 | All | Requirements, UAT coordination |
| Project Manager | 1 | All | Timeline, stakeholder management |
| Compliance SME | 1 | Phase 1-2 | Regulatory requirements |
| Core Banking SME | 1 | Phase 1 | Mainframe integration |

### Technology Stack

| Component | Technology | Cost Model |
|-----------|------------|------------|
| Compute | AWS Lambda | Pay-per-invocation |
| Orchestration | AWS Step Functions | Pay-per-transition |
| Database | DynamoDB Global Tables | Pay-per-request + storage |
| Storage | S3 + Glacier | Pay-per-GB |
| Messaging | EventBridge + SQS | Pay-per-message |
| Monitoring | CloudWatch + X-Ray | Pay-per-metric/trace |
| Security | WAF + GuardDuty + Inspector | Monthly subscription |

### Estimated Costs

| Phase | Duration | Development Cost | AWS Infrastructure |
|-------|----------|------------------|-------------------|
| Phase 1 | 12 weeks | $400K-600K | $5K-10K/month |
| Phase 2 | 8 weeks | $250K-350K | $15K-25K/month |
| Phase 3 | 10 weeks | $300K-400K | $25K-40K/month |
| **Total** | **30 weeks** | **$950K-1.35M** | **$45K-75K/month** |

---

## Part 7: Governance & Decision Points

### Phase Gate Reviews

| Gate | Timing | Go/No-Go Criteria |
|------|--------|-------------------|
| Gate 1 | End of Week 4 | Issuer schema approved, Mastercom design complete |
| Gate 2 | End of Week 10 | Core banking adapter functional, test environment ready |
| Gate 3 | End of Week 12 | Phase 1 UAT complete, regulatory reports validated |
| Gate 4 | End of Week 17 | Performance targets met, DR tested |
| Gate 5 | End of Week 20 | SOC 2 readiness confirmed, production cutover approved |
| Gate 6 | End of Week 30 | ML models deployed, optimization targets achieved |

### Stakeholder RACI

| Decision | Responsible | Accountable | Consulted | Informed |
|----------|-------------|-------------|-----------|----------|
| Architecture changes | Tech Lead | CTO | Compliance | Business |
| Regulatory interpretation | Compliance | CCO | Legal | Tech |
| Vendor selection | Procurement | CFO | Tech, Compliance | Business |
| Go-live approval | PM | COO | All | Board |
| Incident response | SRE | CTO | Compliance | Business |

---

## Part 8: Polya-Style Feasibility Analysis

### 8.1 Have you seen this problem before?

**Yes.** This problem class is well-established:

- **Payment network dispute handling** - Visa's VROL, Mastercard's Mastercom operational for decades
- **Regulatory compliance automation** - Reg E/Reg Z deadline tracking mirrors CFPB enforcement patterns
- **Evidence-based adjudication systems** - Similar to insurance claims processing

**Key Precedents:**
| System | Similarity | Lessons |
|--------|------------|---------|
| Stripe's Dispute API | Direct inspiration | Proven at scale (millions/year) |
| Chargebacks911 | Third-party management | Win rate optimization |
| Verifi (Visa) | Network-native prevention | CE 3.0 patterns |

### 8.2 Related Problems & Theorems

- **State Machine Theory** - Disputes are FSMs with deterministic transitions
- **CAP Theorem** - Current design favors consistency (Step Functions + DynamoDB strong reads)
- **Event Sourcing** - `balance_transactions` is event-sourced ledger
- **Bayesian Decision Theory** - "uncertain" → "human review" implements optimal decision-making

### 8.3 Restatements of the Problem

1. **Operational**: Can we process 100K+ disputes/day with <200ms p99 latency?
2. **Regulatory**: Does this produce sufficient audit trails for OCC examination?
3. **Financial**: Will this reduce dispute losses below 0.9% Visa threshold?
4. **Integration**: Can this connect to legacy core banking without mainframe replacement?

### 8.4 Feasibility Scorecard

```
┌─────────────────────────────────────────────────────────────────────┐
│                    FEASIBILITY SCORECARD                            │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  READY NOW (70%)                                                     │
│  ├── Core dispute schema            ████████████████████ 100%       │
│  ├── Evidence management            ████████████████████ 100%       │
│  ├── Deadline tracking              ████████████████████ 100%       │
│  ├── Visa VROL support              ████████████████░░░░  80%       │
│  ├── AWS orchestration              ████████████████████ 100%       │
│  └── Balance transactions           ████████████████████ 100%       │
│                                                                      │
│  NEEDS WORK (30%)                                                    │
│  ├── Mastercom full integration     ████████░░░░░░░░░░░░  40%       │
│  ├── Issuer-side handling           ░░░░░░░░░░░░░░░░░░░░   0%       │
│  ├── Mainframe adapters             ████░░░░░░░░░░░░░░░░  20%       │
│  ├── Regulatory reporting           ░░░░░░░░░░░░░░░░░░░░   0%       │
│  └── Disaster recovery              ████████░░░░░░░░░░░░  40%       │
│                                                                      │
│  OVERALL BANK READINESS:            ████████████████░░░░  70%       │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Conclusion

This plan provides a comprehensive roadmap for adapting the dispute schema system for national US bank deployment. The 30-week timeline balances thoroughness with urgency, prioritizing regulatory compliance and operational stability.

**Key Success Factors**:
1. Early engagement with core banking teams
2. Parallel development of issuer and acquirer capabilities
3. Continuous compliance validation
4. Performance testing before scale commitment
5. Phased rollout with clear go/no-go gates

---

*Document Version: 1.0*
*Created: December 2024*
*Related Documents: `deep_dive_real_world_cases.md`, `SCHEMA_EXPLANATION.md`, `schema_narrative.md`*
