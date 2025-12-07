# Architecture Recommendation & Critical Reflection Analysis

## Bank Dispute Chatbot: Multi-Agent System Design

**Document Version:** 1.0
**Created:** December 2024
**Type:** Architecture Recommendation + Feasibility Critique
**Related:** `FEASIBILITY_ANALYSIS_LANGGRAPH_MULTIAGENT.md`

---

## Executive Summary

This document provides:
1. **Critical reflection** on the original feasibility analysis
2. **Research-backed assessment** of MCP vs Direct API patterns
3. **Revised architecture recommendation** with high-level design plan

**Key Finding:** The original feasibility assessment (85% confidence) is over-optimistic. Based on current research on multi-agent failure modes, MCP overhead, and hallucination propagation, we recommend a **Hybrid Streamlined Architecture** with 60-65% feasibility confidence.

---

# Part I: Critical Reflection Analysis

## 1. Gaps in Original Feasibility Assessment

### 1.1 Latency Risk Underestimation

| Original Claim | Research Reality |
|----------------|------------------|
| 200ms overhead budget | Production systems show 100ms → 6s latency creep |
| Parallel execution mitigates | Dependency chains prevent full parallelization |
| Not specified | MCP verbose logging: 200ms → 800ms overhead |

**Missing Analysis:**
- No cold-start latency for Lambda-based MCP servers
- No Redis state serialization cost modeling
- Assumed parallelism ignores agent dependencies

### 1.2 Absent Cost Modeling

| Original Claim | Research Reality |
|----------------|------------------|
| "$0.45 → $0.35" without justification | Multi-agent = 3-7x more LLM calls |
| No token budget | MCP workflows can use ~150,000 tokens vs ~2,000 optimized |

### 1.3 Hallucination Cascade Underestimation

| Original Mitigation | Research Finding |
|--------------------|------------------|
| Schema validation | Semantic hallucinations pass schema validation |
| Confidence > 0.7 threshold | LLMs are poorly calibrated; threshold is arbitrary |
| Not specified | Multi-agent hallucinations have longer propagation chains |

**Required:** Consultant-evaluator framework with dual-iteration (achieves 85.5% improvement)

### 1.4 Multi-Agent Failure Modes (MAST Framework)

| Failure Category | Original Coverage | Severity |
|------------------|-------------------|----------|
| **Misalignment** (agents work against each other) | Not mentioned | HIGH |
| **Ambiguity** (unclear handoff conditions) | Partially covered | MEDIUM |
| **Specification errors** (weak role definitions) | Partially covered | MEDIUM |
| **Termination gaps** (infinite loops, zombie states) | Not mentioned | HIGH |

### 1.5 Weak Verification Mechanism

> "Weak or inadequate verification mechanisms were a significant contributor to system failures... creating a universal verification mechanism remains challenging."
> — Multi-Agent LLM Failure Research (2024)

**Missing:**
- Agent contract testing
- Property-based testing for multi-agent consistency
- Regression testing strategy for prompt changes

---

## 2. MCP Tools vs Direct API Calls

### 2.1 Comprehensive Comparison

| Dimension | MCP Tools | Direct API Calls | Winner |
|-----------|-----------|------------------|--------|
| **Latency** | +100-800ms (JSON-RPC, roundtrip) | Minimal | Direct |
| **Token Usage** | Tool definitions consume context | No protocol overhead | Direct |
| **Standardization** | Universal interface | Custom per-integration | MCP |
| **Debugging** | 3 layers (agent→protocol→server) | Single function trace | Direct |
| **Security** | Centralized auth | Per-call auth | MCP |
| **Maintenance** | Add tools without code changes | Requires modification | MCP |
| **Vendor Flexibility** | Model-agnostic | Tied to implementation | MCP |
| **Ecosystem** | 1000s community servers | Build from scratch | MCP |
| **Scaling** | Token overhead grows | Linear | Direct |
| **Maturity** | New (Nov 2024) | Established | Direct |

### 2.2 MCP Pros

1. **Standardization**: "USB-C for AI"—implement once, reuse everywhere
2. **Modular Architecture**: Add/remove capabilities without agent changes
3. **Vendor Neutrality**: Works with Claude, GPT, open-source LLMs
4. **Security Centralization**: Host controls server access
5. **Growing Ecosystem**: SDKs in all major languages
6. **Separation of Concerns**: Tool logic decoupled from agent logic

### 2.3 MCP Cons

1. **Performance Overhead**: JSON-RPC serialization adds latency
2. **Token Bloat**: Tool definitions consume context window
3. **Security Vulnerabilities**: CVE-2025-53109 (sandbox escape), CVE-2025-49596 (RCE)
4. **Debugging Complexity**: Three layers to trace
5. **Maturity Risk**: Best practices still evolving
6. **Overkill for Simple Cases**: Direct calls more efficient

### 2.4 Decision Matrix for This System

| Component | Approach | Rationale |
|-----------|----------|-----------|
| Core Banking APIs | **Direct** | Performance-critical, stable interfaces |
| Compliance Checks | **Direct** | Low latency for deadline calculations |
| Fraud Detection | **MCP** | Model flexibility, standardization benefits |
| Evidence Analysis | **MCP** | Document processing ecosystem tools |
| External Integrations | **MCP** | Payment network standardization |

---

## 3. Revised Feasibility Scores

| Dimension | Original | Revised | Rationale |
|-----------|----------|---------|-----------|
| Technical Alignment | 9/10 | **6/10** | Latency, cost, scaling unvalidated |
| Architectural Coherence | 8/10 | **7/10** | MCP overhead; hybrid needed |
| Incremental Complexity | 7/10 | **5/10** | MAST failure modes unaddressed |
| Business Value | 9/10 | **7/10** | ROI depends on cost modeling |
| Risk Profile | 7/10 | **5/10** | Hallucination cascade, verification gaps |

**Revised Overall Feasibility: 60-65%** (down from 85%)

---

# Part II: Architecture Recommendation

## 1. Recommended Architecture: Hybrid Streamlined Multi-Agent

### 1.1 Design Philosophy

Instead of 7 specialized agents, we recommend **4 core agents** with the rest implemented as **sub-routines** (specialized prompts within agents). This balances specialization with coordination complexity.

### 1.2 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           BANK DISPUTE SYSTEM                                │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌──────────────┐     ┌─────────────────────────────────────────────────┐   │
│  │              │     │           WORKFLOW ORCHESTRATOR                  │   │
│  │   Customer   │────▶│         (LangGraph State Machine)               │   │
│  │   Interface  │     │                                                  │   │
│  │              │◀────│   State: NEW→INTAKE→PROCESS→REVIEW→RESOLVED     │   │
│  └──────────────┘     └─────────────────────────────────────────────────┘   │
│                                        │                                     │
│                    ┌───────────────────┼───────────────────┐                │
│                    ▼                   ▼                   ▼                │
│         ┌──────────────────┐ ┌──────────────────┐ ┌──────────────────┐     │
│         │  INTAKE AGENT    │ │  PROCESS AGENT   │ │  REVIEW AGENT    │     │
│         │                  │ │                  │ │                  │     │
│         │ • Classification │ │ • Evidence Eval  │ │ • Decision       │     │
│         │ • Validation     │ │ • Fraud Check    │ │ • Compliance     │     │
│         │ • Routing        │ │ • Analysis       │ │ • Escalation     │     │
│         └────────┬─────────┘ └────────┬─────────┘ └────────┬─────────┘     │
│                  │                    │                    │                │
│         ┌────────┴────────────────────┴────────────────────┴────────┐      │
│         │                    TOOL ROUTER                             │      │
│         │            (Hybrid MCP + Direct API)                       │      │
│         └────────┬────────────────────┬────────────────────┬────────┘      │
│                  │                    │                    │                │
│    ┌─────────────┴─────┐  ┌──────────┴──────────┐  ┌─────┴─────────────┐   │
│    │   DIRECT APIs     │  │    MCP SERVERS      │  │  VERIFICATION     │   │
│    │                   │  │                     │  │     LAYER         │   │
│    │ • Banking Core    │  │ • Fraud Detection   │  │                   │   │
│    │ • Compliance Calc │  │ • Evidence Analysis │  │ • Cross-Check     │   │
│    │ • Account Lookup  │  │ • Payment Networks  │  │ • Hallucination   │   │
│    │ • Status Update   │  │ • Geospatial        │  │   Detection       │   │
│    └───────────────────┘  └─────────────────────┘  └───────────────────┘   │
│                                                                              │
│    ┌─────────────────────────────────────────────────────────────────┐      │
│    │                      BACKEND SERVICES                            │      │
│    │  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐            │      │
│    │  │   RDS   │  │DynamoDB │  │   S3    │  │SageMaker│            │      │
│    │  │(Disputes)│  │ (State) │  │(Evidence)│ │ (Fraud) │            │      │
│    │  └─────────┘  └─────────┘  └─────────┘  └─────────┘            │      │
│    └─────────────────────────────────────────────────────────────────┘      │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 1.3 Agent Consolidation (7 → 4 Agents)

| Original 7 Agents | Consolidated 4 Agents | Implementation |
|-------------------|----------------------|----------------|
| IntakeAgent | **INTAKE AGENT** | Full agent |
| AnalysisAgent | **PROCESS AGENT** | Sub-routine: classification prompt |
| EvidenceAgent | **PROCESS AGENT** | Sub-routine: evidence eval prompt |
| FraudAgent | **PROCESS AGENT** | Sub-routine: fraud check prompt |
| DecisionAgent | **REVIEW AGENT** | Full agent |
| ComplianceAgent | **REVIEW AGENT** | Sub-routine: compliance prompt |
| EscalationAgent | **REVIEW AGENT** | Sub-routine: escalation prompt |
| (new) | **VERIFICATION AGENT** | Cross-checks other agents |

### 1.4 Verification Agent (New)

Critical addition to address hallucination cascade risk:

```python
class VerificationAgent:
    """
    Cross-checks outputs from other agents before state transitions.
    Implements consultant-evaluator pattern.
    """

    def verify_output(self, agent_output: AgentOutput) -> VerificationResult:
        """
        1. Schema validation (syntactic)
        2. Semantic validation (cross-reference with DB)
        3. Confidence calibration check
        4. Consistency check with previous agent outputs
        5. Hallucination detection via RAG grounding
        """
        pass

    def flag_for_human_review(self, output: AgentOutput, reason: str) -> None:
        """Mandatory human review for low-confidence or inconsistent outputs."""
        pass
```

---

## 2. State Machine Design

### 2.1 Workflow States

```
                    ┌─────────────────────────────────────────┐
                    │            STATE MACHINE                 │
                    └─────────────────────────────────────────┘
                                      │
        ┌─────────────────────────────┼─────────────────────────────┐
        ▼                             ▼                             ▼
   ┌─────────┐                  ┌──────────┐                  ┌──────────┐
   │   NEW   │─────────────────▶│  INTAKE  │─────────────────▶│ PROCESS  │
   └─────────┘                  └──────────┘                  └──────────┘
        │                             │                             │
        │ (invalid)                   │ (escalate)                  │
        ▼                             ▼                             ▼
   ┌─────────┐                  ┌──────────┐                  ┌──────────┐
   │ REJECTED│                  │ ESCALATED│◀─────────────────│  REVIEW  │
   └─────────┘                  └──────────┘                  └──────────┘
                                      │                             │
                                      │ (human decides)             │ (auto-resolve)
                                      ▼                             ▼
                                ┌──────────┐                  ┌──────────┐
                                │ RESOLVED │◀─────────────────│ APPROVED │
                                └──────────┘                  └──────────┘
```

### 2.2 State Transitions with Verification Gates

```python
from langgraph.graph import StateGraph, END
from typing import TypedDict, Literal

class DisputeState(TypedDict):
    # Core dispute data
    dispute_id: str
    customer_id: str
    amount_cents: int
    reason: str

    # Workflow state
    current_state: Literal["NEW", "INTAKE", "PROCESS", "REVIEW",
                          "ESCALATED", "APPROVED", "RESOLVED", "REJECTED"]

    # Agent outputs (verified)
    intake_output: dict | None
    process_output: dict | None
    review_output: dict | None

    # Verification tracking
    verification_score: float  # 0.0 - 1.0
    verification_flags: list[str]
    requires_human_review: bool

    # Context
    bank_user_context: dict
    trace_id: str


def build_dispute_workflow() -> StateGraph:
    """Build streamlined 4-agent workflow with verification gates."""

    workflow = StateGraph(DisputeState)

    # Add agent nodes
    workflow.add_node("intake", intake_agent_node)
    workflow.add_node("verify_intake", verification_agent_node)
    workflow.add_node("process", process_agent_node)
    workflow.add_node("verify_process", verification_agent_node)
    workflow.add_node("review", review_agent_node)
    workflow.add_node("verify_review", verification_agent_node)
    workflow.add_node("escalate", escalation_handler_node)
    workflow.add_node("resolve", resolution_handler_node)

    # Add edges with verification gates
    workflow.add_edge("intake", "verify_intake")
    workflow.add_conditional_edges(
        "verify_intake",
        verification_router,
        {
            "passed": "process",
            "failed": "escalate",
            "retry": "intake"
        }
    )

    workflow.add_edge("process", "verify_process")
    workflow.add_conditional_edges(
        "verify_process",
        verification_router,
        {
            "passed": "review",
            "failed": "escalate",
            "retry": "process"
        }
    )

    workflow.add_edge("review", "verify_review")
    workflow.add_conditional_edges(
        "verify_review",
        verification_router,
        {
            "passed": "resolve",
            "failed": "escalate",
            "retry": "review"
        }
    )

    workflow.add_edge("escalate", END)
    workflow.add_edge("resolve", END)

    return workflow.compile()
```

---

## 3. Tool Architecture (Hybrid MCP + Direct)

### 3.1 Tool Routing Layer

```python
from enum import Enum
from typing import Protocol

class ToolType(Enum):
    DIRECT = "direct"    # Performance-critical, stable APIs
    MCP = "mcp"          # Flexible, ecosystem tools


class ToolRouter:
    """Routes tool calls to appropriate backend (Direct or MCP)."""

    TOOL_MAPPING = {
        # Direct APIs (latency-critical)
        "file_dispute": ToolType.DIRECT,
        "check_status": ToolType.DIRECT,
        "get_deadline": ToolType.DIRECT,
        "update_status": ToolType.DIRECT,
        "validate_account": ToolType.DIRECT,

        # MCP Servers (flexibility-critical)
        "analyze_evidence": ToolType.MCP,
        "detect_fraud_patterns": ToolType.MCP,
        "risk_assessment": ToolType.MCP,
        "verify_location": ToolType.MCP,
        "check_payment_network": ToolType.MCP,
    }

    async def route(self, tool_name: str, params: dict) -> ToolResult:
        tool_type = self.TOOL_MAPPING.get(tool_name, ToolType.MCP)

        if tool_type == ToolType.DIRECT:
            return await self._call_direct(tool_name, params)
        else:
            return await self._call_mcp(tool_name, params)
```

### 3.2 MCP Server Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      MCP SERVERS                             │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────────┐  ┌──────────────────┐                 │
│  │  FRAUD MCP       │  │  EVIDENCE MCP    │                 │
│  │                  │  │                  │                 │
│  │ • detect_patterns│  │ • analyze_doc    │                 │
│  │ • risk_score     │  │ • extract_text   │                 │
│  │ • behavior_check │  │ • verify_receipt │                 │
│  │                  │  │ • classify_type  │                 │
│  │ Backend:         │  │                  │                 │
│  │ SageMaker ML     │  │ Backend:         │                 │
│  └──────────────────┘  │ Bedrock + S3     │                 │
│                        └──────────────────┘                 │
│                                                              │
│  ┌──────────────────┐  ┌──────────────────┐                 │
│  │  PAYMENT MCP     │  │  GEOSPATIAL MCP  │                 │
│  │                  │  │                  │                 │
│  │ • check_network  │  │ • verify_location│                 │
│  │ • validate_txn   │  │ • travel_analysis│                 │
│  │ • refund_status  │  │ • anomaly_detect │                 │
│  │                  │  │                  │                 │
│  │ Backend:         │  │ Backend:         │                 │
│  │ Visa/MC APIs     │  │ Bedrock + Maps   │                 │
│  └──────────────────┘  └──────────────────┘                 │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### 3.3 Direct API Implementation

```python
class DirectBankingAPI:
    """Direct API calls for performance-critical operations."""

    def __init__(self, db_connection: DatabaseConnection):
        self.db = db_connection
        self.compliance = ComplianceCalculator()

    async def file_dispute(
        self,
        customer_id: str,
        charge_id: str,
        reason: str,
        amount_cents: int
    ) -> DisputeResult:
        """Direct database call - no MCP overhead."""
        # Validate inputs
        if amount_cents <= 0:
            raise ValueError("amount_cents must be positive")

        # Direct DB insert
        dispute_id = await self.db.insert_dispute(
            customer_id=customer_id,
            charge_id=charge_id,
            reason=reason,
            amount_cents=amount_cents,
            status="NEW"
        )

        return DisputeResult(
            dispute_id=dispute_id,
            status="NEW",
            created_at=datetime.utcnow()
        )

    async def get_deadline(
        self,
        dispute_id: str,
        payment_method: str
    ) -> DeadlineResult:
        """Direct compliance calculation - latency critical."""
        dispute = await self.db.get_dispute(dispute_id)

        # Use pre-compiled Reg E/Z logic
        deadline = self.compliance.calculate_deadline(
            transaction_date=dispute.transaction_date,
            payment_method=payment_method,
            dispute_type=dispute.reason
        )

        return DeadlineResult(
            deadline=deadline,
            regulation=self.compliance.applicable_regulation,
            days_remaining=deadline - datetime.utcnow()
        )
```

---

## 4. Verification Layer Design

### 4.1 Hallucination Defense Pattern

```
┌─────────────────────────────────────────────────────────────┐
│              HALLUCINATION DEFENSE PIPELINE                  │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Agent Output                                                │
│       │                                                      │
│       ▼                                                      │
│  ┌─────────────┐                                            │
│  │   SCHEMA    │  Syntactic validation                      │
│  │ VALIDATION  │  (JSON schema, type checking)              │
│  └──────┬──────┘                                            │
│         │ PASS                                               │
│         ▼                                                    │
│  ┌─────────────┐                                            │
│  │  SEMANTIC   │  Cross-reference with database             │
│  │ VALIDATION  │  (Does this dispute exist? Correct amount?)│
│  └──────┬──────┘                                            │
│         │ PASS                                               │
│         ▼                                                    │
│  ┌─────────────┐                                            │
│  │CONSISTENCY  │  Compare with previous agent outputs       │
│  │   CHECK     │  (No contradictions in workflow?)          │
│  └──────┬──────┘                                            │
│         │ PASS                                               │
│         ▼                                                    │
│  ┌─────────────┐                                            │
│  │    RAG      │  Ground claims in authoritative sources    │
│  │ GROUNDING   │  (Reg E/Z documentation, policy docs)      │
│  └──────┬──────┘                                            │
│         │ PASS                                               │
│         ▼                                                    │
│  ┌─────────────┐                                            │
│  │ CONFIDENCE  │  Calibrated confidence threshold           │
│  │ CALIBRATION │  (Based on historical accuracy)            │
│  └──────┬──────┘                                            │
│         │                                                    │
│    ┌────┴────┐                                              │
│    ▼         ▼                                              │
│ [PASS]   [HUMAN REVIEW]                                     │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### 4.2 Verification Agent Implementation

```python
from dataclasses import dataclass
from enum import Enum

class VerificationStatus(Enum):
    PASSED = "passed"
    FAILED = "failed"
    NEEDS_HUMAN_REVIEW = "needs_human_review"
    RETRY = "retry"


@dataclass
class VerificationResult:
    status: VerificationStatus
    score: float  # 0.0 - 1.0
    flags: list[str]
    details: dict


class VerificationAgent:
    """
    Cross-checks agent outputs using consultant-evaluator pattern.
    Reduces hallucination cascade risk by 85%+ (per research).
    """

    def __init__(
        self,
        db: DatabaseConnection,
        rag_index: RAGIndex,
        confidence_threshold: float = 0.75
    ):
        self.db = db
        self.rag = rag_index
        self.threshold = confidence_threshold
        self.historical_accuracy = AccuracyTracker()

    async def verify(self, agent_output: AgentOutput) -> VerificationResult:
        """Multi-stage verification pipeline."""
        flags = []
        scores = []

        # Stage 1: Schema validation
        schema_valid = self._validate_schema(agent_output)
        if not schema_valid:
            return VerificationResult(
                status=VerificationStatus.FAILED,
                score=0.0,
                flags=["schema_invalid"],
                details={"stage": "schema"}
            )

        # Stage 2: Semantic validation
        semantic_score = await self._validate_semantics(agent_output)
        scores.append(semantic_score)
        if semantic_score < 0.5:
            flags.append("semantic_mismatch")

        # Stage 3: Consistency check
        consistency_score = await self._check_consistency(agent_output)
        scores.append(consistency_score)
        if consistency_score < 0.5:
            flags.append("inconsistent_with_history")

        # Stage 4: RAG grounding
        grounding_score = await self._ground_with_rag(agent_output)
        scores.append(grounding_score)
        if grounding_score < 0.5:
            flags.append("ungrounded_claims")

        # Stage 5: Confidence calibration
        calibrated_score = self._calibrate_confidence(
            raw_confidence=agent_output.confidence,
            agent_type=agent_output.agent_type
        )
        scores.append(calibrated_score)

        # Final score
        final_score = sum(scores) / len(scores)

        # Determine status
        if final_score >= self.threshold and not flags:
            status = VerificationStatus.PASSED
        elif final_score < 0.5 or len(flags) > 2:
            status = VerificationStatus.NEEDS_HUMAN_REVIEW
        else:
            status = VerificationStatus.RETRY

        return VerificationResult(
            status=status,
            score=final_score,
            flags=flags,
            details={
                "semantic": semantic_score,
                "consistency": consistency_score,
                "grounding": grounding_score,
                "calibrated_confidence": calibrated_score
            }
        )

    async def _validate_semantics(self, output: AgentOutput) -> float:
        """Cross-reference claims with database."""
        # Example: verify dispute exists and amounts match
        if "dispute_id" in output.data:
            dispute = await self.db.get_dispute(output.data["dispute_id"])
            if dispute is None:
                return 0.0
            if dispute.amount_cents != output.data.get("amount_cents"):
                return 0.3
        return 1.0

    async def _ground_with_rag(self, output: AgentOutput) -> float:
        """Ground regulatory claims in authoritative sources."""
        if "deadline" in output.data or "regulation" in output.data:
            sources = await self.rag.search(
                query=f"deadline {output.data.get('regulation', '')}",
                k=3
            )
            # Check if output aligns with sources
            alignment = self._compute_alignment(output, sources)
            return alignment
        return 1.0  # No regulatory claims to ground

    def _calibrate_confidence(
        self,
        raw_confidence: float,
        agent_type: str
    ) -> float:
        """Adjust confidence based on historical accuracy."""
        historical = self.historical_accuracy.get(agent_type)
        if historical is None:
            return raw_confidence * 0.8  # Conservative for unknown agents

        # Platt scaling approximation
        calibrated = raw_confidence * historical.accuracy_ratio
        return min(calibrated, 1.0)
```

---

## 5. Implementation Plan

### 5.1 Phased Approach (Revised)

| Phase | Duration | Deliverables | Go/No-Go Gate |
|-------|----------|--------------|---------------|
| **Phase 0: Validation** | Week 1 | Cost model, latency benchmark, MCP PoC | Cost < 2x MVP |
| **Phase 1: Foundation** | Weeks 2-3 | LangGraph skeleton, verification agent | Latency < 1.5s |
| **Phase 2: Core Agents** | Weeks 4-6 | Intake, Process, Review agents | Hallucination < 5% |
| **Phase 3: Hybrid Tools** | Weeks 7-8 | Direct APIs + MCP servers | All tools functional |
| **Phase 4: Integration** | Weeks 9-10 | Full workflow, shadow mode | Parity with MVP |
| **Phase 5: Optimization** | Weeks 11-12 | Latency tuning, cost reduction | Meet targets |

### 5.2 Critical Validation Gates

| Gate | Metric | Pass Threshold | Fail Action |
|------|--------|----------------|-------------|
| **Cost Gate** | Token usage vs MVP | < 2x increase | Reduce agents or prompts |
| **Latency Gate** | P95 end-to-end | < 1500ms | Optimize or reduce agents |
| **Hallucination Gate** | Cross-check failure rate | < 5% | Add verification stages |
| **MAST Gate** | Termination & alignment tests | 100% pass | Redesign state machine |
| **Parity Gate** | Same output as MVP | 99% match | Debug and fix |

### 5.3 Risk Mitigation Matrix

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Latency exceeds 2s | HIGH | HIGH | Reduce to 3 agents, optimize prompts |
| Cost > 3x MVP | MEDIUM | HIGH | Use smaller models for some agents |
| Hallucination cascade | MEDIUM | HIGH | Verification agent mandatory |
| MCP server instability | LOW | MEDIUM | Direct API fallback |
| MAST failures | MEDIUM | HIGH | Extensive state machine testing |

---

## 6. Success Metrics

### 6.1 Technical Metrics

| Metric | MVP Baseline | Target | Measurement |
|--------|--------------|--------|-------------|
| P95 Latency | 800ms | < 1500ms | End-to-end timing |
| Cost per dispute | $0.45 | < $0.90 | API + compute |
| Hallucination rate | N/A | < 2% | Verification failures |
| Human escalation | 20% | < 15% | Escalation count |
| System availability | 99.9% | 99.9% | Uptime |

### 6.2 Business Metrics

| Metric | MVP Baseline | Target | Measurement |
|--------|--------------|--------|-------------|
| Dispute resolution time | 22 min | < 18 min | Average time |
| Customer satisfaction | Baseline | +10% | Survey scores |
| Compliance accuracy | 99.5% | 99.9% | Audit results |
| Analyst productivity | Baseline | +25% | Cases per analyst |

---

## 7. Conclusion

### Key Recommendations

1. **Reduce agent count**: 7 → 4 agents to manage coordination complexity
2. **Add Verification Agent**: Critical for hallucination defense
3. **Hybrid tool architecture**: Direct APIs for performance, MCP for flexibility
4. **Validation-first approach**: Each phase has explicit go/no-go gates
5. **Conservative targets**: Accept higher latency/cost initially, optimize later

### Decision

| Recommendation | Confidence | Rationale |
|----------------|------------|-----------|
| **PROCEED WITH CAUTION** | 60-65% | Feasible with modifications; validate before committing |

### Next Steps

1. **Week 1**: Run Phase 0 validation (cost model + latency benchmark)
2. **Decision Point**: Go/No-Go based on validation results
3. **If GO**: Proceed with streamlined 4-agent architecture
4. **If NO-GO**: Evaluate single-agent with specialized prompts alternative

---

## Appendices

### Appendix A: Agent Prompt Templates

See `prompts/` directory for:
- `intake_agent_prompt.md`
- `process_agent_prompt.md`
- `review_agent_prompt.md`
- `verification_agent_prompt.md`

### Appendix B: MCP Server Specifications

See `mcp-servers/` directory for:
- `fraud_mcp_spec.json`
- `evidence_mcp_spec.json`
- `payment_mcp_spec.json`
- `geospatial_mcp_spec.json`

### Appendix C: Test Scenarios

See `tests/` directory for:
- `test_state_machine.py`
- `test_verification_pipeline.py`
- `test_hallucination_defense.py`
- `test_mast_compliance.py`

---

*Document Version: 1.0*
*Created: December 2024*
*Type: Architecture Recommendation + Critical Reflection*
*Methodology: Research-Backed Assessment + First Principles Design*

---

> *"Complexity is the enemy of execution. Simplify relentlessly while preserving essential capabilities."*
