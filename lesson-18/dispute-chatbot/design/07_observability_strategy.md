# 07_Observability_Strategy

**Version:** 1.0
**Status:** Approved
**Date:** 2025-12-09

---

## 1. Overview

The Observability Strategy ensures that the Chatbot's performance, reliability, and business impact are measurable and transparent. It focuses on correlating system metrics (latency, errors) with business outcomes (win rates) and AI specific behaviors (hallucinations, judge scores).

## 2. Success Metrics (KPIs)

We track three categories of metrics, aligned with PRD Goals (G1-G6):

### 2.1 Business Metrics
| Metric | Target | Definition | Source |
|--------|--------|------------|--------|
| **Win Rate** | >60% | Disputes resolved in merchant's favor / Total closed disputes | PhaseLogger/VROL |
| **Evidence Completeness** | >95% | Percentage of required fields populated before submission | EvidenceGatherer |
| **CE 3.0 Qual Rate** | >70% | Fraud disputes eligible for Compelling Evidence 3.0 | TransactionSpecialist |

### 2.2 System Metrics
| Metric | Target | Definition | Source |
|--------|--------|------------|--------|
| **Evidence Gathering Time** | <5 min | End-to-end duration of GATHER_EVIDENCE phase | PhaseLogger |
| **Tool Latency** | <800ms P95 | Time for MCP tool execution | BlackBox |
| **Availability** | 99.9% | API uptime | Load Balancer / Health Check |

### 2.3 AI Quality Metrics
| Metric | Target | Definition | Source |
|--------|--------|------------|--------|
| **Judge Approval Rate** | >90% | First-pass validation success by LLM Judges | JudgePanel |
| **Fabrication Rate** | <1% | Detected hallucinations by FabricationJudge | JudgePanel |
| **GuardRails Blocks** | <5% | Valid inputs blocked by over-aggressive filters | GuardRails |

## 3. Logging Architecture (The 4 Pillars)

We implement the 4-Pillar Explainability framework mandated in ADR-006.

### 3.1 BlackBox (Raw Traces)
- **Purpose**: Debugging and granular replay.
- **Content**: Full request/response bodies, prompts, tool outputs.
- **Storage**: JSON blobs in TimescaleDB (short-term) -> S3 (archive).
- **PII**: **Redacted**.

### 3.2 AgentFacts (Identity)
- **Purpose**: Provenance and reproducibility.
- **Content**: Model ID (e.g., `gpt-4o-2024-05-13`), Prompt Hash, System Prompt Version.
- **Storage**: Linked to every Dispute and BlackBox trace.

### 3.3 GuardRails (Safety)
- **Purpose**: Compliance audit.
- **Content**: Validation results (Pass/Fail), specific rule violations (e.g., "PII Detected: Credit Card").
- **Storage**: High-retention audit logs.

### 3.4 PhaseLogger (Reasoning)
- **Purpose**: Business logic transparency.
- **Content**: Human-readable rationale for state transitions. 
    - *Example*: "Transitioned to SUBMIT because Evidence Quality Score (0.85) > Threshold (0.80)."
- **Storage**: Structured logs queryable by Dispute ID.

## 4. Monitoring & Alerting

### 4.1 Alerting Rules

| Severity | Condition | Notification Channel | Response SLA |
|----------|-----------|----------------------|--------------|
| **P1 (Critical)** | System Down / API 500s > 1% | PagerDuty (On-call) | 15 min |
| **P1 (Critical)** | PII Leak Detected in Logs | Security Team | 15 min |
| **P2 (High)** | Win Rate drops < 50% (7d avg) | Slack (#dispute-ops) | 4 hours |
| **P2 (High)** | Deadline < 24h & Not Submitted | Email (Merchant) + Slack | 2 hours |
| **P3 (Info)** | New Dispute Created | Dashboard | N/A |

### 4.2 Health Checks
- `/health`: Simple connectivity check (DB, Redis).
- `/health/deep`: Functional check (simulated VROL ping, LLM connectivity).

## 5. Dashboards

### 5.1 Merchant Dashboard (Chainlit Sidebar)
- **Current Status**: Active phase (e.g., "Gathering Evidence").
- **Evidence Health**: % Complete, missing items list.
- **Win Probability**: Estimated based on judge scores.

### 5.2 Operations Dashboard (Grafana)
- **Real-time Pipeline**: Number of disputes in each state (CLASSIFY, GATHER, VALIDATE).
- **LLM Cost Tracking**: Daily spend vs budget.
- **Latency Heatmap**: Tool execution times.
- **Judge Disagreement**: Cases where Human Review differed from AI Judge.

## 6. Log Retention
- **Operational Logs**: 30 days.
- **Audit Trails**: 7 years (archived to cold storage after 1 year).

