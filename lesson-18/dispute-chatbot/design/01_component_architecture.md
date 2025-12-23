# Component Architecture: Merchant Dispute Resolution Chatbot

**Document ID:** design/01_component_architecture
**Version:** 1.0.0
**Last Updated:** 2025-12-08
**Status:** Phase 0 Foundation

---

## 1. Overview

### Purpose

This document defines the 5 major components of the Merchant Dispute Resolution Agentic Chatbot, their responsibilities, interfaces, and interactions.

### Major Components

| # | Component | Responsibility | Pattern |
|---|-----------|----------------|---------|
| 1 | State Machine Orchestrator | Compliance-critical phase transitions | StateMachineOrchestrator |
| 2 | Hierarchical Evidence Gatherer | Parallel specialist agents for evidence collection | HierarchicalOrchestrator |
| 3 | LLM Judge Panel | Real-time evidence quality validation | Synchronous Panel |
| 4 | Explainability Layer | Audit compliance via 4 pillars | lesson-17 Framework |
| 5 | Network Translation | Internal schema → Visa VROL format | Adapter Pattern |

### Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                              CHAINLIT UI LAYER                                           │
│                                                                                          │
│  ┌─────────────────────────────────────────────────────────────────────────────────┐    │
│  │  @cl.on_chat_start    @cl.on_message    cl.Step()    cl.Element()               │    │
│  └─────────────────────────────────────────────────────────────────────────────────┘    │
│                                          │                                               │
└──────────────────────────────────────────┼───────────────────────────────────────────────┘
                                           │
                                           ▼
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                    1. STATE MACHINE ORCHESTRATOR                                         │
├─────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                          │
│   ┌─────────┐    ┌──────────────┐    ┌──────────┐    ┌────────┐    ┌─────────┐         │
│   │CLASSIFY │───►│GATHER_EVIDENCE│───►│ VALIDATE │───►│ SUBMIT │───►│ MONITOR │         │
│   └─────────┘    └───────┬──────┘    └─────┬────┘    └────┬───┘    └─────────┘         │
│                          │                 │              │                              │
│                          ▼                 ▼              ▼                              │
│   Phase Handlers:   gather_evidence   validate.py   submit.py                           │
│   - classify.py     handler               │                                              │
│                          │                 │                                              │
└──────────────────────────┼─────────────────┼──────────────────────────────────────────────┘
                           │                 │
                           ▼                 ▼
┌──────────────────────────────────────┐  ┌────────────────────────────────────────────────┐
│  2. HIERARCHICAL EVIDENCE GATHERER   │  │            3. LLM JUDGE PANEL                  │
├──────────────────────────────────────┤  ├────────────────────────────────────────────────┤
│                                      │  │                                                │
│  ┌─────────────────────────────────┐ │  │  ┌─────────────┐ ┌─────────────┐ ┌───────────┐│
│  │       Planner Agent             │ │  │  │  Evidence   │ │ Fabrication │ │ Dispute   ││
│  │    (routing_model)              │ │  │  │  Quality    │ │ Detection   │ │ Validity  ││
│  └───────────┬─────────────────────┘ │  │  │  Judge      │ │ Judge       │ │ Judge     ││
│              │                       │  │  │             │ │             │ │           ││
│    ┌─────────┼─────────┐             │  │  │ Threshold:  │ │ Threshold:  │ │ Threshold:││
│    │         │         │             │  │  │   0.8       │ │   0.95      │ │   0.7     ││
│    ▼         ▼         ▼             │  │  │ Blocking:   │ │ Blocking:   │ │ Blocking: ││
│  ┌────┐   ┌────┐   ┌────────┐       │  │  │   YES       │ │   YES       │ │   NO      ││
│  │Txn │   │Ship│   │Customer│       │  │  └─────────────┘ └─────────────┘ └───────────┘│
│  │Spec│   │Spec│   │  Spec  │       │  │                                                │
│  └────┘   └────┘   └────────┘       │  │  Uses: LLMService.complete_structured()        │
│  (default_model, ThreadPoolExecutor)│  │        with Pydantic response models           │
│                                      │  │                                                │
└──────────────────────────────────────┘  └────────────────────────────────────────────────┘
                           │                               │
                           └───────────────┬───────────────┘
                                           │
                                           ▼
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                        4. EXPLAINABILITY LAYER                                           │
├─────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                          │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐     │
│  │   BlackBox      │  │   AgentFacts    │  │   GuardRails    │  │  PhaseLogger    │     │
│  │   Recorder      │  │                 │  │                 │  │                 │     │
│  ├─────────────────┤  ├─────────────────┤  ├─────────────────┤  ├─────────────────┤     │
│  │ Post-incident   │  │ Agent version/  │  │ PCI compliance, │  │ Decision        │     │
│  │ analysis of     │  │ capability      │  │ PII detection,  │  │ rationale per   │     │
│  │ lost disputes   │  │ verification    │  │ evidence valid. │  │ phase           │     │
│  ├─────────────────┤  ├─────────────────┤  ├─────────────────┤  ├─────────────────┤     │
│  │ Retention:      │  │ Stores:         │  │ Validates:      │  │ Retention:      │     │
│  │ 90 days → S3    │  │ Model version,  │  │ All I/O for PAN │  │ 1 year →        │     │
│  │                 │  │ prompt hash     │  │ and PII         │  │ TimescaleDB     │     │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘  └─────────────────┘     │
│                                                                                          │
│  Reference: lesson-17/TUTORIAL_INDEX.md                                                  │
│                                                                                          │
└─────────────────────────────────────────────────────────────────────────────────────────┘
                                           │
                                           ▼
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                        5. NETWORK TRANSLATION LAYER                                      │
├─────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                          │
│  ┌─────────────────────────────────────────────────────────────────────────────────┐    │
│  │                      Internal Dispute Schema                                     │    │
│  │                      (Pydantic models, unified format)                          │    │
│  └───────────────────────────────────┬─────────────────────────────────────────────┘    │
│                                      │                                                   │
│                                      ▼                                                   │
│  ┌─────────────────────────────────────────────────────────────────────────────────┐    │
│  │                      Visa VROL Translator                                        │    │
│  │                      (Adapter Pattern)                                           │    │
│  ├─────────────────────────────────────────────────────────────────────────────────┤    │
│  │  - Maps internal evidence fields → VROL specification                           │    │
│  │  - Handles fraud 10.4 and PNR 13.1 payload structures                           │    │
│  │  - Retry logic: 3x exponential backoff (1s, 2s, 4s)                             │    │
│  └───────────────────────────────────┬─────────────────────────────────────────────┘    │
│                                      │                                                   │
│                                      ▼                                                   │
│  ┌─────────────────────────────────────────────────────────────────────────────────┐    │
│  │                      Mock Visa API (Phase 1)                                     │    │
│  │                      Real Visa VROL API (Phase 3)                               │    │
│  └─────────────────────────────────────────────────────────────────────────────────┘    │
│                                                                                          │
└─────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Component Details

### 2.1 State Machine Orchestrator

**Responsibility:** Manages compliance-critical phase transitions for dispute resolution workflow.

**Pattern:** StateMachineOrchestrator (from lesson-16)

**Reference:** `lesson-16/backend/orchestrators/state_machine.py`

#### States

| State | Entry Criteria | Exit Criteria | On Entry |
|-------|---------------|---------------|----------|
| `CLASSIFY` | Dispute ID received | Reason code determined | Parse dispute, calculate deadline |
| `GATHER_EVIDENCE` | Reason code known | Evidence package complete | Delegate to Hierarchical Gatherer |
| `VALIDATE` | Evidence gathered | All blocking judges pass | Run Judge Panel |
| `SUBMIT` | Validation passed | Network acknowledgment | Translate and submit |
| `MONITOR` | Submitted | Resolution received | Poll for decision |

#### Terminal States

| State | Trigger | Action |
|-------|---------|--------|
| `RESOLVED_WON` | Network decision: merchant | Update merchant win rate |
| `RESOLVED_LOST` | Network decision: cardholder | Log for analysis |
| `ESCALATED` | Judge failure or timeout | Create human review ticket |
| `EXPIRED` | Deadline passed | Archive with reason |

#### State Transition Diagram

```
                              ┌─────────────┐
                              │   CLASSIFY  │
                              └──────┬──────┘
                                     │ reason_code_determined
                                     ▼
                            ┌──────────────────┐
                 ┌──────────│ GATHER_EVIDENCE  │──────────┐
                 │          └────────┬─────────┘          │
                 │                   │ evidence_complete   │
                 │                   ▼                     │
                 │            ┌──────────────┐            │
                 │   ┌────────│   VALIDATE   │────────┐   │
                 │   │        └──────┬───────┘        │   │
                 │   │               │ judges_passed   │   │
                 │   │               ▼                 │   │
                 │   │         ┌──────────┐           │   │
                 │   │         │  SUBMIT  │           │   │
                 │   │         └────┬─────┘           │   │
                 │   │              │ acknowledged     │   │
                 │   │              ▼                  │   │
                 │   │         ┌──────────┐           │   │
                 │   │         │  MONITOR │           │   │
                 │   │         └────┬─────┘           │   │
                 │   │              │                  │   │
           ┌─────┴───┴──────┬──────┴──────┬──────────┴───┴─────┐
           │                │             │                     │
           ▼                ▼             ▼                     ▼
    ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
    │ RESOLVED_WON │ │ RESOLVED_LOST│ │  ESCALATED   │ │   EXPIRED    │
    └──────────────┘ └──────────────┘ └──────────────┘ └──────────────┘
```

#### Interface

```python
class DisputeStateMachine:
    """State machine for compliance-critical dispute workflow."""

    def __init__(
        self,
        dispute_id: str,
        redis_client: Redis,
        explainability: ExplainabilityLayer,
    ) -> None:
        """Initialize with state recovery from Redis."""

    async def transition(self, event: str, data: dict[str, Any]) -> DisputeState:
        """Transition to next state if valid, or raise InvalidTransitionError."""

    async def get_state(self) -> DisputeState:
        """Get current state with full context."""

    async def recover(self) -> DisputeState:
        """Recover state from Redis after container restart."""

    def get_valid_transitions(self) -> list[str]:
        """Return valid transitions from current state."""
```

#### Files

| File | Purpose |
|------|---------|
| `backend/orchestrators/dispute_state.py` | DisputeState enum and constants |
| `backend/orchestrators/transitions.py` | Transition rules and validators |
| `backend/orchestrators/dispute_orchestrator.py` | Main StateMachine implementation |
| `backend/phases/classify.py` | CLASSIFY phase handler |
| `backend/phases/gather_evidence.py` | GATHER_EVIDENCE phase handler |
| `backend/phases/validate.py` | VALIDATE phase handler |
| `backend/phases/submit.py` | SUBMIT phase handler |
| `backend/phases/monitor.py` | MONITOR phase handler |

---

### 2.2 Hierarchical Evidence Gatherer

**Responsibility:** Parallel evidence collection using specialist agents for CE 3.0 qualification.

**Pattern:** HierarchicalOrchestrator (from lesson-16)

**Reference:** `lesson-16/backend/orchestrators/hierarchical.py`

#### Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        PLANNER AGENT                                         │
│                        (routing_model for cost efficiency)                   │
├─────────────────────────────────────────────────────────────────────────────┤
│  Responsibilities:                                                           │
│  - Analyze dispute type (fraud 10.4 vs PNR 13.1)                            │
│  - Determine required evidence based on reason code                          │
│  - Create execution plan for specialists                                     │
│  - Aggregate specialist results into evidence package                        │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
            ┌───────────────────────┼───────────────────────┐
            │                       │                       │
            ▼                       ▼                       ▼
┌─────────────────────┐  ┌─────────────────────┐  ┌─────────────────────┐
│ TRANSACTION         │  │ SHIPPING            │  │ CUSTOMER HISTORY    │
│ SPECIALIST          │  │ SPECIALIST          │  │ SPECIALIST          │
├─────────────────────┤  ├─────────────────────┤  ├─────────────────────┤
│ Model: default_model│  │ Model: default_model│  │ Model: default_model│
│                     │  │                     │  │                     │
│ Retrieves:          │  │ Retrieves:          │  │ Retrieves:          │
│ - Prior undisputed  │  │ - Tracking numbers  │  │ - Device fingerprint│
│   transactions      │  │ - Proof of delivery │  │ - IP address        │
│ - CE 3.0 qualifying │  │ - Delivery photos   │  │ - Email match       │
│   history           │  │ - Signature images  │  │ - Shipping address  │
│                     │  │                     │  │   match             │
│ Sources:            │  │ Sources:            │  │                     │
│ - Stripe/Square API │  │ - FedEx API         │  │ Sources:            │
│ - Internal records  │  │ - UPS API           │  │ - Platform data     │
│                     │  │ - USPS API          │  │ - Authentication    │
│                     │  │                     │  │   logs              │
└─────────────────────┘  └─────────────────────┘  └─────────────────────┘
            │                       │                       │
            └───────────────────────┼───────────────────────┘
                                    │
                                    ▼
                    ┌─────────────────────────────┐
                    │     EVIDENCE PACKAGE        │
                    │     (Merged + Validated)    │
                    └─────────────────────────────┘
```

#### Parallel Execution

Uses `ThreadPoolExecutor` for I/O-bound specialist execution:

```python
from concurrent.futures import ThreadPoolExecutor, as_completed

class HierarchicalEvidenceGatherer:
    """Parallel evidence collection with specialist agents."""

    def __init__(
        self,
        llm_service: LLMService,
        max_workers: int = 3,
    ) -> None:
        self.planner = EvidencePlannerAgent(llm_service)
        self.specialists = [
            TransactionSpecialist(llm_service),
            ShippingSpecialist(llm_service),
            CustomerHistorySpecialist(llm_service),
        ]
        self.max_workers = max_workers

    async def gather(
        self,
        dispute: Dispute,
        context: dict[str, Any],
    ) -> EvidencePackage:
        """Gather evidence in parallel from all specialists."""

        # Plan which specialists to invoke
        plan = await self.planner.create_plan(dispute)

        # Execute specialists in parallel
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_specialist = {
                executor.submit(spec.gather, dispute, plan): spec
                for spec in self.specialists
                if spec.type in plan.required_evidence
            }

            results = []
            for future in as_completed(future_to_specialist):
                spec = future_to_specialist[future]
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    # Log failure but continue with other specialists
                    logger.error(f"{spec.type} failed: {e}")

        # Assemble package with completeness scoring
        return self._assemble_package(results, plan)
```

#### CE 3.0 Qualification Logic

```python
def check_ce3_eligibility(evidence: EvidencePackage) -> CE3Result:
    """Check if evidence qualifies for Compelling Evidence 3.0.

    Requirements:
    1. ≥2 prior undisputed transactions
    2. Within 120 days of disputed transaction
    3. At least 2 matching signals:
       - Device fingerprint
       - IP address
       - Email address
       - Shipping address
    """
    prior_txns = evidence.prior_transactions
    if len(prior_txns) < 2:
        return CE3Result(eligible=False, reason="Need ≥2 prior transactions")

    # Check time window
    for txn in prior_txns:
        if txn.date > dispute.transaction_date - timedelta(days=120):
            continue
        prior_txns.remove(txn)

    if len(prior_txns) < 2:
        return CE3Result(eligible=False, reason="Prior txns outside 120-day window")

    # Count matching signals
    matching_signals = sum([
        evidence.device_fingerprint_match,
        evidence.ip_address_match,
        evidence.email_match,
        evidence.shipping_address_match,
    ])

    if matching_signals < 2:
        return CE3Result(
            eligible=False,
            reason=f"Only {matching_signals}/2 matching signals",
        )

    return CE3Result(eligible=True, prior_transactions=prior_txns)
```

#### Files

| File | Purpose |
|------|---------|
| `backend/orchestrators/evidence_gatherer.py` | Main HierarchicalEvidenceGatherer |
| `backend/agents/evidence_planner.py` | Planner agent (routing_model) |
| `backend/agents/transaction_specialist.py` | CE 3.0 transaction retrieval |
| `backend/agents/shipping_specialist.py` | Shipping evidence (FedEx/UPS) |
| `backend/agents/customer_specialist.py` | Customer matching signals |

---

### 2.3 LLM Judge Panel

**Responsibility:** Real-time evidence validation with 3 synchronized judges.

**Pattern:** Synchronous Panel (from lesson-10)

**Reference:** `lesson-10/ai_judge_production_guide.md`

#### Judge Specifications

| Judge | Dimension | Threshold | Blocking | Latency SLA |
|-------|-----------|-----------|----------|-------------|
| Evidence Quality | Sufficient for network? | 0.8 | Yes | <800ms P95 |
| Fabrication Detection | Agent hallucinations? | 0.95 | Yes | <800ms P95 |
| Dispute Validity | Legitimate defense? | 0.7 | No (warning) | <800ms P95 |

#### Judge Flow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          VALIDATE PHASE                                      │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                          JUDGE PANEL                                         │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│   Evidence Package                                                           │
│         │                                                                    │
│         ├──────────────────┬──────────────────┬──────────────────┐          │
│         │                  │                  │                  │          │
│         ▼                  ▼                  ▼                  ▼          │
│  ┌─────────────┐   ┌─────────────┐   ┌─────────────┐                       │
│  │  Evidence   │   │ Fabrication │   │  Dispute    │                       │
│  │  Quality    │   │ Detection   │   │  Validity   │                       │
│  │   Judge     │   │   Judge     │   │   Judge     │                       │
│  └──────┬──────┘   └──────┬──────┘   └──────┬──────┘                       │
│         │                  │                  │                             │
│         ▼                  ▼                  ▼                             │
│    JudgeScore         JudgeScore         JudgeScore                        │
│  ┌─────────────┐   ┌─────────────┐   ┌─────────────┐                       │
│  │score: 0.85  │   │score: 0.99  │   │score: 0.72  │                       │
│  │reasoning:   │   │reasoning:   │   │reasoning:   │                       │
│  │"..."        │   │"..."        │   │"..."        │                       │
│  │gaps: []     │   │gaps: []     │   │gaps: []     │                       │
│  └─────────────┘   └─────────────┘   └─────────────┘                       │
│         │                  │                  │                             │
│         └──────────────────┴──────────────────┘                             │
│                            │                                                 │
│                            ▼                                                 │
│                   ┌─────────────────┐                                       │
│                   │  Panel Result   │                                       │
│                   │  passed: true   │                                       │
│                   │  warnings: [    │                                       │
│                   │    validity...  │                                       │
│                   │  ]              │                                       │
│                   └─────────────────┘                                       │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

#### Pydantic Response Models

```python
from pydantic import BaseModel, Field

class JudgeScore(BaseModel):
    """Structured judge response for type-safe evaluation."""
    score: float = Field(ge=0.0, le=1.0, description="Quality score 0-1")
    reasoning: str = Field(description="Detailed reasoning for score")
    evidence_gaps: list[str] = Field(default_factory=list)
    confidence: float = Field(ge=0.0, le=1.0, default=0.9)

class EvidenceQualityResult(JudgeScore):
    """Evidence quality judge specific fields."""
    completeness_score: float = Field(ge=0.0, le=1.0)
    relevance_score: float = Field(ge=0.0, le=1.0)
    missing_evidence: list[str] = Field(default_factory=list)

class FabricationResult(JudgeScore):
    """Fabrication detection judge specific fields."""
    fabricated_items: list[str] = Field(default_factory=list)
    verification_status: dict[str, bool] = Field(default_factory=dict)
```

#### Judge Implementation Pattern

```python
from utils.llm_service import get_default_service

class EvidenceQualityJudge:
    """Judge for evidence sufficiency evaluation."""

    def __init__(self) -> None:
        self.service = get_default_service()
        self.threshold = 0.8
        self.is_blocking = True

    async def evaluate(
        self,
        evidence: EvidencePackage,
        dispute: Dispute,
    ) -> EvidenceQualityResult:
        """Evaluate evidence quality with structured output."""

        prompt = self._build_prompt(evidence, dispute)

        result = await self.service.complete_structured(
            prompt=prompt,
            response_model=EvidenceQualityResult,
            model=self.service.judge_model,
        )

        return result

    def passes(self, result: EvidenceQualityResult) -> bool:
        """Check if result meets threshold."""
        return result.score >= self.threshold
```

#### Panel Orchestration

```python
class JudgePanel:
    """Orchestrate 3 judges for evidence validation."""

    def __init__(self, cost_tracker: CostTracker | None = None) -> None:
        self.judges = [
            EvidenceQualityJudge(),      # Blocking
            FabricationDetectionJudge(), # Blocking
            DisputeValidityJudge(),      # Warning only
        ]
        self.cost_tracker = cost_tracker

    async def evaluate(
        self,
        evidence: EvidencePackage,
        dispute: Dispute,
    ) -> PanelResult:
        """Run all judges and aggregate results."""

        results = {}
        blocking_failures = []
        warnings = []

        for judge in self.judges:
            result = await judge.evaluate(evidence, dispute)
            results[judge.name] = result

            if not judge.passes(result):
                if judge.is_blocking:
                    blocking_failures.append(judge.name)
                else:
                    warnings.append(judge.name)

        return PanelResult(
            passed=len(blocking_failures) == 0,
            results=results,
            blocking_failures=blocking_failures,
            warnings=warnings,
        )
```

#### Files

| File | Purpose |
|------|---------|
| `backend/judges/schemas.py` | Pydantic models for judge responses |
| `backend/judges/evidence_quality.py` | Evidence Quality Judge |
| `backend/judges/fabrication_detection.py` | Fabrication Detection Judge |
| `backend/judges/dispute_validity.py` | Dispute Validity Judge |
| `backend/judges/judge_panel.py` | Panel orchestrator |

---

### 2.4 Explainability Layer

**Responsibility:** Audit compliance through 4 pillars for regulatory requirements.

**Pattern:** 4-Pillar Framework (from lesson-17)

**Reference:** `lesson-17/TUTORIAL_INDEX.md`

#### Pillar Overview

| Pillar | Component | Purpose | Storage | Retention |
|--------|-----------|---------|---------|-----------|
| **Recording** | BlackBoxRecorder | Post-incident analysis | S3 | 90 days |
| **Identity** | AgentFacts | Version/capability audit | PostgreSQL | 1 year |
| **Validation** | GuardRails | PCI/PII compliance | TimescaleDB | 7 years |
| **Reasoning** | PhaseLogger | Decision rationale | TimescaleDB | 1 year |

#### Integration Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        EXPLAINABILITY LAYER                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────────┐│
│  │                      ExplainabilityManager                               ││
│  │                                                                          ││
│  │  @contextmanager                                                         ││
│  │  def trace_phase(phase: str, dispute_id: str):                          ││
│  │      """Context manager for phase-level tracing."""                     ││
│  │                                                                          ││
│  │  def record_agent_call(agent: str, input: dict, output: dict):          ││
│  │      """Record agent invocation to BlackBox."""                         ││
│  │                                                                          ││
│  │  def validate_pci(data: dict) -> ValidationResult:                      ││
│  │      """Run GuardRails PCI/PII scan."""                                 ││
│  │                                                                          ││
│  │  def log_decision(phase: str, decision: str, rationale: str):           ││
│  │      """Log decision with PhaseLogger."""                               ││
│  │                                                                          ││
│  └─────────────────────────────────────────────────────────────────────────┘│
│                                                                              │
│  ┌───────────────┐ ┌───────────────┐ ┌───────────────┐ ┌───────────────┐    │
│  │  BlackBox     │ │  AgentFacts   │ │  GuardRails   │ │ PhaseLogger   │    │
│  │  Recorder     │ │               │ │               │ │               │    │
│  ├───────────────┤ ├───────────────┤ ├───────────────┤ ├───────────────┤    │
│  │ Records:      │ │ Stores:       │ │ Validates:    │ │ Logs:         │    │
│  │ - Agent I/O   │ │ - Model ver.  │ │ - No PAN      │ │ - Phase entry │    │
│  │ - Timestamps  │ │ - Prompt hash │ │ - PII redact  │ │ - Decisions   │    │
│  │ - Latency     │ │ - Capabilities│ │ - Input/output│ │ - Rationale   │    │
│  │ - Errors      │ │ - Calibration │ │ - WAF rules   │ │ - Transitions │    │
│  └───────┬───────┘ └───────┬───────┘ └───────┬───────┘ └───────┬───────┘    │
│          │                 │                 │                 │            │
│          ▼                 ▼                 ▼                 ▼            │
│       S3 Bucket       PostgreSQL       TimescaleDB       TimescaleDB       │
│       (90 days)       (1 year)         (7 years)         (1 year)          │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

#### Usage Pattern

```python
from explainability import ExplainabilityManager

explainability = ExplainabilityManager(
    blackbox_bucket="dispute-blackbox",
    timescale_conn=timescale_client,
    postgres_conn=postgres_client,
)

# Phase-level tracing
async with explainability.trace_phase("GATHER_EVIDENCE", dispute.id) as trace:
    # All operations within this context are recorded

    # Record agent invocation
    explainability.record_agent_call(
        agent="TransactionSpecialist",
        input={"dispute_id": dispute.id},
        output={"transactions": results},
    )

    # Validate PCI compliance
    validation = explainability.validate_pci(evidence_package)
    if validation.has_pii:
        raise PCIViolationError(validation.violations)

    # Log decision with rationale
    explainability.log_decision(
        phase="GATHER_EVIDENCE",
        decision="proceed_to_validate",
        rationale="Evidence package complete with CE 3.0 qualification",
    )
```

#### Audit Export

```python
def export_audit_log(
    dispute_id: str,
    format: str = "json",
) -> str:
    """Export full audit trail for compliance review.

    Returns JSON with:
    - All BlackBox recordings for this dispute
    - AgentFacts for all agents involved
    - GuardRails validations with timestamps
    - PhaseLogger decision chain
    """
```

#### Files

| File | Purpose |
|------|---------|
| `backend/explainability/manager.py` | ExplainabilityManager orchestrator |
| `backend/explainability/blackbox.py` | BlackBoxRecorder integration |
| `backend/explainability/agent_facts.py` | AgentFacts integration |
| `backend/explainability/guardrails.py` | GuardRails PCI/PII validators |
| `backend/explainability/phase_logger.py` | PhaseLogger integration |
| `backend/explainability/export.py` | Audit log export functionality |

---

### 2.5 Network Translation Layer

**Responsibility:** Transform internal dispute schema to network-specific formats (Visa VROL).

**Pattern:** Adapter Pattern

#### Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    NETWORK TRANSLATION LAYER                                 │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────────┐│
│  │                    Internal Dispute Schema                               ││
│  │                    (backend/schemas/dispute_schema.py)                   ││
│  ├─────────────────────────────────────────────────────────────────────────┤│
│  │  class InternalDispute(BaseModel):                                      ││
│  │      dispute_id: str                                                    ││
│  │      reason_code: ReasonCode                                            ││
│  │      evidence: EvidencePackage                                          ││
│  │      merchant: MerchantInfo                                             ││
│  │      ce3_data: CE3Data | None                                           ││
│  │      validation_results: PanelResult                                    ││
│  └─────────────────────────────────────────────────────────────────────────┘│
│                                    │                                         │
│                                    ▼                                         │
│  ┌─────────────────────────────────────────────────────────────────────────┐│
│  │                    NetworkAdapter (ABC)                                  ││
│  ├─────────────────────────────────────────────────────────────────────────┤│
│  │  @abstractmethod                                                        ││
│  │  def translate(dispute: InternalDispute) -> NetworkPayload              ││
│  │                                                                          ││
│  │  @abstractmethod                                                        ││
│  │  async def submit(payload: NetworkPayload) -> SubmissionResult          ││
│  │                                                                          ││
│  │  @abstractmethod                                                        ││
│  │  async def poll_status(case_id: str) -> ResolutionStatus                ││
│  └─────────────────────────────────────────────────────────────────────────┘│
│                                    │                                         │
│              ┌─────────────────────┴─────────────────────┐                  │
│              │                                           │                  │
│              ▼                                           ▼                  │
│  ┌───────────────────────────┐           ┌───────────────────────────┐      │
│  │    VisaVROLAdapter        │           │   MastercardAdapter       │      │
│  │    (Phase 1 MVP)          │           │   (Phase 2)               │      │
│  ├───────────────────────────┤           ├───────────────────────────┤      │
│  │ Handles:                  │           │ Handles:                  │      │
│  │ - Fraud 10.4 payload      │           │ - Fraud 4837 payload      │      │
│  │ - PNR 13.1 payload        │           │ - PNR 4853 payload        │      │
│  │ - VROL field mapping      │           │ - MC field mapping        │      │
│  └────────────┬──────────────┘           └───────────────────────────┘      │
│               │                                                              │
│               ▼                                                              │
│  ┌───────────────────────────┐                                              │
│  │    MockVisaAPI            │                                              │
│  │    (Phase 1 Testing)      │                                              │
│  ├───────────────────────────┤                                              │
│  │ Simulates:                │                                              │
│  │ - VROL acceptance         │                                              │
│  │ - Case ID generation      │                                              │
│  │ - Resolution responses    │                                              │
│  │ - Error scenarios         │                                              │
│  └───────────────────────────┘                                              │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

#### VROL Field Mapping

| Internal Field | VROL Field (10.4 Fraud) | VROL Field (13.1 PNR) |
|----------------|------------------------|----------------------|
| `dispute_id` | `arn` | `arn` |
| `transaction_date` | `transactionDate` | `transactionDate` |
| `amount` | `disputeAmount` | `disputeAmount` |
| `ce3_data.prior_txns` | `compellingEvidence.priorTransactions` | N/A |
| `ce3_data.device_fingerprint` | `compellingEvidence.deviceFingerprint` | N/A |
| `evidence.tracking_number` | N/A | `shippingEvidence.trackingNumber` |
| `evidence.proof_of_delivery` | N/A | `shippingEvidence.deliveryProof` |
| `evidence.signature_image` | N/A | `shippingEvidence.signature` |

#### Retry Logic

```python
class VisaVROLAdapter(NetworkAdapter):
    """Adapter for Visa VROL submissions."""

    MAX_RETRIES = 3
    BACKOFF_SECONDS = [1, 2, 4]  # Exponential backoff

    async def submit(self, payload: VROLPayload) -> SubmissionResult:
        """Submit to VROL with retry logic."""

        for attempt, delay in enumerate(self.BACKOFF_SECONDS):
            try:
                response = await self._send_request(payload)
                return SubmissionResult(
                    success=True,
                    case_id=response.case_id,
                    acknowledged_at=response.timestamp,
                )
            except NetworkTimeoutError:
                if attempt < self.MAX_RETRIES - 1:
                    await asyncio.sleep(delay)
                    continue
                raise SubmissionFailedError("Max retries exceeded")
            except VROLValidationError as e:
                # Don't retry validation errors
                return SubmissionResult(
                    success=False,
                    error=str(e),
                )
```

#### Files

| File | Purpose |
|------|---------|
| `backend/schemas/dispute_schema.py` | Internal unified schema |
| `backend/adapters/base.py` | NetworkAdapter ABC |
| `backend/adapters/visa_vrol.py` | Visa VROL translator |
| `backend/adapters/visa_mock.py` | Mock API for testing |
| `backend/adapters/mastercard.py` | Mastercard adapter (Phase 2) |

---

## 3. Component Dependencies

### Dependency Graph

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          DEPENDENCY FLOW                                     │
└─────────────────────────────────────────────────────────────────────────────┘

  ┌─────────────────┐
  │   Chainlit UI   │
  └────────┬────────┘
           │ depends on
           ▼
  ┌─────────────────┐     ┌─────────────────┐
  │  State Machine  │────►│ Explainability  │
  │  Orchestrator   │     │    Layer        │
  └────────┬────────┘     └─────────────────┘
           │ delegates to              ▲
           ▼                           │ used by all
  ┌─────────────────┐     ┌────────────┴──────────────┐
  │  Hierarchical   │────►│                           │
  │  Evidence       │     │                           │
  │  Gatherer       │     │                           │
  └────────┬────────┘     │                           │
           │              │                           │
           ▼              │                           │
  ┌─────────────────┐     │                           │
  │   LLM Judge     │────►│                           │
  │     Panel       │     │                           │
  └────────┬────────┘     └───────────────────────────┘
           │
           ▼
  ┌─────────────────┐
  │    Network      │
  │   Translation   │
  └─────────────────┘
```

### Shared Services

| Service | Used By | Purpose |
|---------|---------|---------|
| `LLMService` | All LLM-using components | Unified LLM access |
| `ExplainabilityManager` | All components | Audit logging |
| `Redis` | State Machine, Session | State persistence |
| `PostgreSQL` | All domain entities | Primary data store |
| `S3` | BlackBox, Evidence | Document storage |
| `TimescaleDB` | AuditLog | Time-series logs |

---

## 4. LLMService Integration

### Model Assignment

| Component | Model | Method | Rationale |
|-----------|-------|--------|-----------|
| DisputeClassifier | `routing_model` | `complete()` | Quick classification |
| EvidencePlanner | `routing_model` | `complete()` | Cost-efficient planning |
| TransactionSpecialist | `default_model` | `complete()` | Complex analysis |
| ShippingSpecialist | `default_model` | `complete()` | Document extraction |
| CustomerSpecialist | `default_model` | `complete()` | Pattern matching |
| EvidenceQualityJudge | `judge_model` | `complete_structured()` | Type-safe scoring |
| FabricationDetectionJudge | `judge_model` | `complete_structured()` | Type-safe detection |
| DisputeValidityJudge | `judge_model` | `complete_structured()` | Type-safe validation |

### Cost Tracking

```python
# Session-level cost tracking
from utils.llm_service import get_default_service, CostTracker

tracker = CostTracker()
service = get_default_service()
service.set_cost_tracker(tracker)

# After dispute resolution
costs = tracker.summary()
# {"total_cost": 0.0234, "costs_by_model": {...}, "call_count": 15}
```

---

## 5. Version History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0.0 | 2025-12-08 | Claude | Initial component architecture for Phase 1 MVP |

---

## 6. References

- PRD Section 3: Strategic Approach (Major Components)
- PRD Section 6: Functional Requirements (FR-1 through FR-6)
- PRD Section 9: Technical Considerations
- Domain Model: `design/02_domain_model.md`
- System Context: `design/00_system_context.md`
- lesson-16: Orchestrator Patterns
- lesson-17: Explainability Framework
- lesson-10: AI Judge Production Guide
