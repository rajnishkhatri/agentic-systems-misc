# PRD: Merchant Dispute Resolution Agentic Chatbot

**Document ID:** 0014-prd-merchant-dispute-chatbot
**Version:** 1.2.0
**Created:** 2025-12-05
**Updated:** 2025-12-05
**Status:** Draft

---

> **Pólya Methodology Notes (Retrospective)**
>
> This PRD was enhanced to align with the Pólya-based PRD creation process (see `.claude/create-prd.md`):
> - **GATE 1 (Understanding)**: Problem validated via domain research (CE 3.0, Reg E/Z, $60B market)
> - **GATE 2 (Approach)**: Strategy validated as Decomposition + Working Backward (see Section 3)
> - **GATE 3 (PRD Review)**: Document reviewed and sections 3, 5, 7, 11 added for template compliance
>
> **v1.2.0 Enhancement (Synthetic Data First Methodology):**
> - **Data-Driven Development**: Each phase now starts with synthetic data generation (Section 12)
> - **LLM Eval Integration**: Judges configured as acceptance criteria with calibration gates
> - **Full Explainability**: 4 pillars (BlackBox, AgentFacts, GuardRails, PhaseLogger) mandatory per phase
> - **Eval-Driven Workflow**: PR gates require passing LLM judges + explainability trace capture

---

## 1. Introduction/Overview

### Problem Statement

Merchants lose **$60 billion annually** to payment disputes (chargebacks, claims, reversals). The dispute resolution process is fundamentally an information asymmetry problem where merchants must respond with:
- Precise transaction details matching network records
- Evidence categorized into 27 specific fields
- Documentation within strict deadlines (14 days for evidence, Reg E/Z timelines)

### Solution

An **Agentic Dispute Resolution Chatbot** that helps merchants defend against chargebacks by:
- Gathering evidence efficiently (CE 3.0 for Visa, network-specific formats)
- Meeting strict regulatory deadlines
- Building compelling evidence packages that win disputes
- Providing full explainability for compliance audits

### Scope (Phase 1 MVP)

- **Network:** Visa only (Phase 2 adds Mastercard)
- **Dispute Types:** Fraud (10.4) + Product Not Received (13.1)
- **Target:** Small to enterprise merchants

---

## 2. Goals

| # | Goal | Target | Measurement |
|---|------|--------|-------------|
| G1 | Dispute win rate | >60% | Won disputes / Total disputed (vs 40% industry baseline) |
| G2 | Evidence submission time | <5 min | Agent conversation duration |
| G3 | Tool call latency | <800ms P95 | CloudWatch metrics |
| G4 | Judge approval rate | >90% | Synchronous judge pass rate |
| G5 | PCI compliance | 100% | Zero PII in logs |
| G6 | CE 3.0 qualification rate | >70% | Qualifying disputes / Fraud disputes |

---

## 3. Strategic Approach

### Chosen Strategy: Design-First + Decomposition + Working Backward

**Rationale**: Following Pólya's principle of "understanding before solving," we begin with Phase 0 (Design & Architecture) to establish the big picture. The dispute resolution workflow has clear, sequential phases (CLASSIFY → GATHER → VALIDATE → SUBMIT → MONITOR) that map naturally to a **State Machine** pattern. Within the GATHER phase, parallel evidence collection benefits from **Hierarchical Delegation**. We work backward from the 60% win rate goal to determine required evidence quality thresholds.

### Pólya Heuristics Applied

| Heuristic | Phase | Application |
|-----------|-------|-------------|
| **Understand First** | Phase 0 | Domain model, stakeholder interviews, spike work before any code |
| **Decomposition** | Phase 0→1 | Break dispute workflow into 5 discrete state machine phases with clear entry/exit criteria |
| **Simplification** | Phase 1 | Visa-only removes network translation complexity; 2 dispute types vs. full catalog |
| **Working Backward** | Phase 0→1 | Start from 60% win rate → derive judge thresholds (0.8 evidence, 0.95 fabrication) → determine evidence requirements |
| **Analogy** | Phase 0 | CE 3.0 evidence patterns similar to prior Visa dispute systems; adapt existing hierarchical orchestrator pattern |
| **Auxiliary Problem** | Phase 0 Spikes | Solve VROL parsing, judge latency, CE 3.0 matching as separate problems first |

### Development Flow (Pólya-Aligned)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    PÓLYA-ALIGNED DEVELOPMENT FLOW                            │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐  │
│  │ UNDERSTAND  │───▶│    PLAN     │───▶│   EXECUTE   │───▶│   REFLECT   │  │
│  │  (Phase 0)  │    │  (Phase 0)  │    │(Phases 1-3) │    │  (Ongoing)  │  │
│  └─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘  │
│        │                  │                  │                  │          │
│        ▼                  ▼                  ▼                  ▼          │
│   Domain model       ADRs, API         TDD + SDF          Judge drift     │
│   Stakeholders       contracts         Eval-driven        recalibration   │
│   Spike work         Architecture      BlackBox traces    Win rate review │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Major Components

1. **State Machine Orchestrator** - Manages compliance-critical phase transitions
2. **Hierarchical Evidence Gatherer** - Parallel specialist agents for transaction, shipping, customer data
3. **LLM Judge Panel** - 3 synchronous judges for real-time quality validation
4. **Explainability Layer** - 4 pillars (BlackBox, AgentFacts, GuardRails, PhaseLogger) for audit compliance
5. **Network Translation** - Unified internal schema → Visa VROL format

### Key Risk Mitigation Strategy

Primary risk is **LLM hallucination** fabricating evidence. Mitigation:
- Fabrication Detection Judge with 0.95 threshold (blocking)
- Schema validation against known evidence field types
- Human escalation when any judge fails

---

## 4. User Stories

### US-1: Small Business Owner (Fraud Dispute)
**As a** small business owner,
**I want** help gathering evidence for a fraud dispute,
**So that** I can recover my $150 and avoid dispute fees.

**Acceptance Criteria:**
- Chatbot identifies prior undisputed transactions for CE 3.0 qualification
- Evidence package generated within 5 minutes
- All PII redacted from audit logs

### US-2: E-commerce Manager (Product Not Received)
**As an** e-commerce manager,
**I want** to respond to "product not received" disputes with shipping proof,
**So that** I can prove delivery and win the dispute.

**Acceptance Criteria:**
- Chatbot retrieves FedEx/UPS tracking and POD automatically
- Shipping evidence formatted per Visa requirements
- Deadline alerts sent 7, 3, and 1 days before evidence due

### US-3: Operations Lead (Compliance)
**As an** operations lead,
**I want** complete audit trails for all dispute decisions,
**So that** I can demonstrate Reg E/Z compliance to auditors.

**Acceptance Criteria:**
- All 4 explainability pillars active and logging
- Phase transitions captured with rationale
- Exportable audit logs in JSON format

---

## 5. Non-Goals (Out of Scope)

The following are explicitly **not** in scope for Phase 1 MVP:

| Non-Goal | Rationale | Future Phase |
|----------|-----------|--------------|
| Mastercard integration | Reduces network translation complexity | Phase 2 |
| Subscription Canceled (13.2) disputes | Lower volume, different evidence pattern | Phase 2 |
| Multi-language support | English-only simplifies NLP validation | Phase 3+ |
| Human agent handoff UI | Focus on automation first | Phase 2 |
| Direct network API integration | Use REST facade for testability | Phase 3 |
| Batch dispute processing | Single-dispute flow for MVP | Phase 2 |
| Mobile-optimized interface | Desktop/API-first approach | Phase 3 |
| Historical dispute analytics | Focus on resolution, not reporting | Phase 2 |

---

## 6. Functional Requirements

### FR-1: State Machine Orchestration

The chatbot SHALL use a **State Machine** pattern for compliance-critical dispute phases:

```
CLASSIFY → GATHER_EVIDENCE → VALIDATE → SUBMIT → MONITOR
```

| Phase | Entry Criteria | Exit Criteria | Transition Trigger |
|-------|---------------|---------------|-------------------|
| CLASSIFY | Dispute ID received | Reason code determined | Classification complete |
| GATHER_EVIDENCE | Reason code known | Evidence package complete | All specialists return |
| VALIDATE | Evidence gathered | All judges pass | Judge scores > threshold |
| SUBMIT | Validation passed | Network acknowledgment | Submission confirmed |
| MONITOR | Submitted | Resolution received | Network decision |

**Reference:** [StateMachineOrchestrator](../lesson-16/backend/orchestrators/state_machine.py)

### FR-2: MCP Tools (4 Core)

| Tool | Purpose | Input | Output |
|------|---------|-------|--------|
| `classify_dispute` | Determine reason code, network | `dispute_id` | `{reason_code, network, deadline}` |
| `gather_evidence` | Parallel specialist agents | `dispute_id, evidence_type` | `{evidence_package}` |
| `validate_evidence` | Run 3 LLM judges | `dispute_id` | `{judge_scores, pass/fail}` |
| `submit_dispute` | Network-specific payload | `dispute_id` | `{submission_id, status}` |

### FR-3: Hierarchical Evidence Gathering

Within the GATHER_EVIDENCE phase, use **Hierarchical Delegation** for parallel execution:

```
Planner Agent
    ├── Transaction Specialist: Prior undisputed transactions for CE 3.0
    ├── Shipping Specialist: Tracking, POD, delivery photos
    └── Customer History Specialist: Email match, device fingerprint, IP
```

**Reference:** [HierarchicalOrchestrator](../lesson-16/backend/orchestrators/hierarchical.py)

### FR-4: LLM Judge Strategy (Synchronous)

Real-time evaluation during conversation with 3 judges:

| Judge | Dimension | Threshold | Blocking? |
|-------|-----------|-----------|-----------|
| Evidence Quality | Is evidence sufficient for network? | 0.8 | Yes |
| Fabrication Detection | Did agent invent details? | 0.95 | Yes |
| Dispute Validity | Is this a legitimate defense? | 0.7 | No (warning) |

**Reference:** [AI Judge Production Guide](../lesson-10/ai_judge_production_guide.md)

### FR-5: Explainability (4 Pillars)

All 4 pillars from [lesson-17](../lesson-17/TUTORIAL_INDEX.md) SHALL be mandatory:

| Pillar | Component | Application |
|--------|-----------|-------------|
| **Recording** | BlackBoxRecorder | Post-incident analysis of lost disputes |
| **Identity** | AgentFacts | Agent version/capability verification for audit |
| **Validation** | GuardRails | PCI compliance, PII detection, evidence validation |
| **Reasoning** | PhaseLogger | Track decisions per dispute phase with rationale |

### FR-6: Chainlit Interactive UI

The chatbot SHALL use Chainlit for the merchant-facing interface:

| Requirement | Description |
|-------------|-------------|
| FR-6.1 | Each phase SHALL render as a collapsible `cl.Step()` |
| FR-6.2 | Tool calls SHALL display input/output within nested steps |
| FR-6.3 | Evidence items SHALL appear in sidebar as `cl.Element()` |
| FR-6.4 | Judge scores SHALL stream in real-time during validation |
| FR-6.5 | Session state SHALL persist using `cl.user_session` |
| FR-6.6 | Explainability pillar data SHALL be viewable in a side panel |

---

## 7. Design Considerations

### Conversation Flow

The chatbot should complete evidence gathering in **≤5 conversational turns**:

| Turn | Purpose | Example |
|------|---------|---------|
| 1 | Greeting + Dispute ID input | "Welcome! Please enter your dispute ID or transaction reference." |
| 2 | Classification confirmation | "I see this is a fraud dispute (10.4). I'll gather evidence to prove cardholder authorization." |
| 3 | Evidence summary + gaps | "I found 3 prior transactions, shipping proof, and device match. Missing: customer email confirmation. Can you provide?" |
| 4 | Validation result | "Evidence package ready. Quality score: 0.87. Fabrication check: passed. Ready to submit?" |
| 5 | Submission confirmation | "Submitted to Visa. Case ID: VIS-2024-12345. Deadline: Dec 19, 2024. I'll monitor for updates." |

### Progressive Disclosure

- **Don't ask for data already in system**: If transaction ID maps to known merchant records, auto-populate
- **Show evidence as gathered**: Real-time updates as specialists complete
- **Explain judge decisions**: "Fabrication check passed because all evidence traces to source records"

### Error States and Recovery

| Error State | User Message | System Action |
|-------------|--------------|---------------|
| Network timeout | "Visa system is slow. Retrying..." | Exponential backoff (1s, 2s, 4s) |
| Judge failure | "I need human review for this evidence. Escalating to your dispute team." | Create escalation ticket with context |
| Missing evidence | "To strengthen your case, I need [specific item]. Where can I find this?" | Guided prompt for missing field |
| Invalid dispute ID | "I couldn't find dispute #XYZ. Please check the ID or enter the transaction date." | Offer alternative lookup methods |
| Deadline warning | "⚠️ Evidence deadline is in 3 days. Priority: complete submission today." | Escalate urgency in UI |

### Accessibility Requirements

- All conversation text must be screen-reader compatible
- Color-coded status indicators must have text alternatives
- Keyboard navigation for all actions
- Maximum response time: 3 seconds for user feedback

### Chainlit UI Architecture

**Phase Visualization with Steps API:**
- Each of the 5 phases (CLASSIFY → GATHER → VALIDATE → SUBMIT → MONITOR) renders as a collapsible Step
- Tool calls display inline with inputs/outputs
- Real-time streaming for evidence gathering progress

**UI Components:**

| Component | Purpose | Chainlit Feature |
|-----------|---------|------------------|
| Phase Step | Show current phase with status | `cl.Step()` with `status` |
| Tool Call Display | Visualize MCP tool invocations | `cl.Step(type="tool")` |
| Evidence Sidebar | Display gathered evidence items | `cl.Element(display="side")` |
| Explainability Panel | Live BlackBox/AgentFacts view | Custom React component |
| Progress Indicator | Phase completion percentage | `cl.Message()` streaming |

**Conversation Flow Mapping:**

| Turn | Chainlit Rendering |
|------|-------------------|
| 1: Greeting | `cl.Message()` + initial prompt |
| 2: Classification | `cl.Step("CLASSIFY")` with reason code |
| 3: Evidence Summary | Nested `cl.Step()` for each specialist |
| 4: Validation | `cl.Step("VALIDATE")` with judge scores |
| 5: Submission | `cl.Step("SUBMIT")` + confirmation |

---

## 8. Non-Functional Requirements

### NFR-1: PCI-DSS v4.0 Compliance
- No Primary Account Number (PAN) storage
- Tokenized card references only (last4 + fingerprint)
- GuardRails PII detection on all inputs/outputs
- WAF rules to block PAN in query strings

### NFR-2: Latency Requirements
- Tool call latency: <800ms P95
- End-to-end evidence gathering: <5 minutes
- State transition: <100ms

### NFR-3: Explainability Requirements
- All 4 pillars mandatory (BlackBox, AgentFacts, GuardRails, PhaseLogger)
- 100% audit completeness for state transitions
- Exportable logs in JSON format

### NFR-4: Eval-Driven Development
- TDD with eval metrics as acceptance criteria
- Judge scores gate phase transitions
- Minimum 90% judge approval rate for release

---

## 9. Technical Considerations

### Orchestration Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    STATE MACHINE ORCHESTRATOR                            │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  CLASSIFY ──► GATHER_EVIDENCE ──► VALIDATE ──► SUBMIT ──► MONITOR       │
│                     │                                                    │
│                     ▼                                                    │
│          ┌─────────────────────────────────────┐                        │
│          │   HIERARCHICAL ORCHESTRATOR         │                        │
│          │                                     │                        │
│          │   Planner ──┬── Transaction Spec.   │                        │
│          │             ├── Shipping Spec.      │                        │
│          │             └── Customer Spec.      │                        │
│          └─────────────────────────────────────┘                        │
│                                                                          │
│  [BlackBox] [AgentFacts] [GuardRails] [PhaseLogger]                     │
└─────────────────────────────────────────────────────────────────────────┘
```

### Patterns Integration

| Pattern | Source | Application |
|---------|--------|-------------|
| TDD Workflow | [patterns/tdd-workflow.md](../patterns/tdd-workflow.md) | Eval metrics as acceptance criteria |
| ThreadPoolExecutor | [patterns/threadpool-parallel.md](../patterns/threadpool-parallel.md) | Parallel evidence gathering |
| Abstract Base Class | [patterns/abstract-base-class.md](../patterns/abstract-base-class.md) | Pluggable agent implementations |
| Sessions | [patterns/sessions-tutorial.md](../patterns/sessions-tutorial.md) | Multi-turn conversation state |
| Memory | [patterns/memory-tutorial.md](../patterns/memory-tutorial.md) | Long-term merchant context |

### Composable LLM Architecture (LiteLLM)

All LLM interactions SHALL use the centralized `LLMService` from `utils/llm_service.py`:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    COMPOSABLE LLM ARCHITECTURE                               │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                    LLMService (Singleton)                            │    │
│  │                                                                      │    │
│  │  Models:                                                             │    │
│  │  ├── default_model (LLM_DEFAULT_MODEL) → General completions        │    │
│  │  ├── judge_model (LLM_JUDGE_MODEL) → Structured output for judges   │    │
│  │  └── routing_model (LLM_ROUTING_MODEL) → Cheap routing decisions    │    │
│  │                                                                      │    │
│  │  Features:                                                           │    │
│  │  ├── Disk caching (LLM_CACHE_TYPE=disk) → Dev cost savings          │    │
│  │  ├── CostTracker → Monitor costs per model                          │    │
│  │  ├── Logprobs → Confidence-based cascade patterns                   │    │
│  │  └── Pydantic structured output → Type-safe judge responses         │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                          │                                                   │
│            ┌─────────────┼─────────────┬─────────────┐                      │
│            ▼             ▼             ▼             ▼                      │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐           │
│  │  Planner    │ │  Specialists│ │   Judges    │ │  Classifier │           │
│  │  Agent      │ │  (Parallel) │ │  (Panel)    │ │             │           │
│  │             │ │             │ │             │ │             │           │
│  │ complete()  │ │ complete()  │ │ complete_   │ │ complete()  │           │
│  │ routing_    │ │ default_    │ │ structured()│ │ routing_    │           │
│  │ model       │ │ model       │ │ judge_model │ │ model       │           │
│  └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘           │
│                                                                              │
│  Environment Variables (.env):                                               │
│  ├── LLM_DEFAULT_MODEL=gpt-4o      # General completions                    │
│  ├── LLM_JUDGE_MODEL=gpt-4o        # Evaluation/judge tasks                 │
│  ├── LLM_ROUTING_MODEL=gpt-4o-mini # Cheap routing decisions                │
│  └── LLM_CACHE_TYPE=disk           # disk | redis | none                    │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

#### LLMService Usage by Component

| Component | Method | Model | Purpose |
|-----------|--------|-------|---------|
| DisputeClassifier | `complete()` | routing_model | Quick dispute type routing |
| EvidencePlanner | `complete()` | routing_model | Plan evidence collection |
| TransactionSpecialist | `complete()` | default_model | Analyze transaction patterns |
| ShippingSpecialist | `complete()` | default_model | Extract shipping evidence |
| CustomerSpecialist | `complete()` | default_model | Match customer signals |
| EvidenceQualityJudge | `complete_structured()` | judge_model | Score evidence (Pydantic) |
| FabricationDetectionJudge | `complete_structured()` | judge_model | Detect hallucinations (Pydantic) |
| DisputeValidityJudge | `complete_structured()` | judge_model | Validate dispute (Pydantic) |

#### Cost Tracking Integration

```python
from utils.llm_service import get_default_service, CostTracker

# Create tracker for session-level cost monitoring
tracker = CostTracker()
service = LLMService(cost_tracker=tracker)

# After dispute resolution
costs = tracker.summary()
# {
#   "total_cost": 0.0234,
#   "costs_by_model": {"gpt-4o": 0.02, "gpt-4o-mini": 0.0034},
#   "call_count": 15
# }
```

#### Structured Output for Judges (Pydantic)

```python
from pydantic import BaseModel
from utils.llm_service import get_default_service

class JudgeScore(BaseModel):
    score: float  # 0.0 - 1.0
    reasoning: str
    evidence_gaps: list[str]
    confidence: float

service = get_default_service()
result = await service.complete_structured(
    messages=[{"role": "user", "content": judge_prompt}],
    response_model=JudgeScore,
    # Uses judge_model by default
)
# result is type-safe JudgeScore instance
```

#### Logprobs for Confidence-Based Cascading

```python
# Low-confidence routing triggers escalation to stronger model
result = await service.complete(
    messages=messages,
    model=service.routing_model,
    logprobs=True,
    top_logprobs=10
)

# Check confidence for cascade decision
if result.logprobs and max_confidence(result.logprobs) < 0.7:
    # Escalate to stronger model
    result = await service.complete(messages=messages, model=service.default_model)
```

#### Anti-Patterns (DO NOT USE)

**IMPORTANT**: All LLM calls in lesson-18 MUST use `LLMService`. The following patterns are **prohibited**:

```python
# ❌ WRONG: Direct litellm import (no caching, no cost tracking, no model abstraction)
from litellm import completion
MODEL_NAME = "gpt-4o-mini"  # Hardcoded model name
response = completion(model=MODEL_NAME, messages=messages)

# ❌ WRONG: Direct openai import (vendor lock-in)
from openai import OpenAI
client = OpenAI()
response = client.chat.completions.create(...)
```

**Correct Pattern:**

```python
# ✅ CORRECT: Use LLMService singleton
from utils.llm_service import get_default_service

service = get_default_service()

# For specialists (analysis tasks):
result = await service.complete(messages=messages)  # Uses default_model

# For classifiers (cheap routing):
result = await service.complete(messages=messages, model=service.routing_model)

# For judges (structured output):
result = await service.complete_structured(messages=messages, response_model=JudgeResult)
```

**Rationale:**
1. **Provider agnostic**: Switch between OpenAI, Anthropic, Azure, etc. via env vars
2. **Cost tracking**: Automatic cost monitoring across all LLM calls
3. **Caching**: Disk/Redis caching for development cost savings
4. **Consistency**: All components use same retry logic, timeouts, error handling
5. **Testability**: Mock `get_default_service()` for unit tests

### Chainlit Frontend Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    CHAINLIT FRONTEND ARCHITECTURE                            │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                    CHAINLIT APP (app.py)                             │    │
│  │                                                                      │    │
│  │  @cl.on_chat_start    → Initialize session, show welcome             │    │
│  │  @cl.on_message       → Route to State Machine Orchestrator          │    │
│  │  @cl.step decorator   → Wrap each phase for visualization            │    │
│  │  @cl.action_callback  → Handle user confirmations (submit/edit)      │    │
│  │                                                                      │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                          │                                                   │
│                          ▼                                                   │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │              PHASE STEP WRAPPER (chainlit_phases.py)                 │    │
│  │                                                                      │    │
│  │  async def classify_step(dispute_id: str) -> cl.Step                 │    │
│  │  async def gather_step(dispute_id: str) -> cl.Step                   │    │
│  │  async def validate_step(evidence: dict) -> cl.Step                  │    │
│  │  async def submit_step(package: dict) -> cl.Step                     │    │
│  │  async def monitor_step(case_id: str) -> cl.Step                     │    │
│  │                                                                      │    │
│  │  Each step:                                                          │    │
│  │  - Creates cl.Step() with phase name                                 │    │
│  │  - Calls State Machine phase handler                                 │    │
│  │  - Streams tool call outputs in nested steps                         │    │
│  │  - Logs to BlackBoxRecorder                                          │    │
│  │  - Updates PhaseLogger with rationale                                │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                          │                                                   │
│                          ▼                                                   │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │           EXISTING BACKEND (State Machine + Explainability)          │    │
│  │                                                                      │    │
│  │  StateMachineOrchestrator (lesson-16)                                │    │
│  │  BlackBox, AgentFacts, GuardRails, PhaseLogger (lesson-17)           │    │
│  │  LLM Judges (lesson-10)                                              │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Network Translation Layer

Unified internal schema translates to network-specific formats:

| Internal Field | Visa VROL | Mastercard |
|---------------|-----------|------------|
| `reason_code` | `disputeCondition` | `reasonCode` |
| `amount` | `disputeAmount` | `claimAmount` |
| `currency` | `disputeCurrency` | `claimCurrencyCode` (numeric) |

---

## 10. Success Metrics

| Metric | Target | Industry Baseline | Measurement |
|--------|--------|-------------------|-------------|
| Dispute win rate | >60% | 40% | Won / Total |
| CE 3.0 qualification rate | >70% | N/A | Qualifying / Fraud disputes |
| Evidence completeness | >95% | 60% | Fields filled / Required |
| Time to evidence | <5 min | 20+ min manual | Conversation duration |
| Judge approval rate | >90% | N/A | Pass / Total validations |

---

## 11. Validation Checkpoints

Implementation verification points for quality assurance:

### Phase 0 Design Checkpoints (Weeks 0-2)

| Checkpoint | Gate | Trigger | Validation Criteria | Failure Action |
|------------|------|---------|---------------------|----------------|
| CP0.1 | Domain Model | Week 0 complete | All 7 entities documented with relationships and business rules | Schedule domain expert session |
| CP0.2 | API Contracts | API specs drafted | OpenAPI specs complete with examples; consumer review passed | Iterate with frontend team |
| CP0.3 | Architecture | ADRs documented | All 6 ADRs have decisions, rationale, and trade-offs | Architecture review session |
| CP0.4 | Spikes | Week 2 mid-point | All 5 spikes completed; no blocking issues; findings documented | Extend spike or re-scope Phase 1 |
| CP0.5 | Security | Security review | PCI compliance mapped; PII handling documented; no gaps | Security remediation sprint |
| CP0.6 | Stakeholder | Phase 0 end | All gates passed; stakeholder sign-off obtained | Address blockers, re-review |

### Phase 1-3 Runtime Checkpoints

| Checkpoint | Phase | Trigger | Validation Criteria | Failure Action |
|------------|-------|---------|---------------------|----------------|
| CP1 | CLASSIFY | Reason code extracted | Code matches Visa 10.x or 13.x pattern; deadline calculated | Escalate to human classifier |
| CP2 | GATHER | Evidence package assembled | All required fields for reason code populated; sources attached | List missing fields, prompt merchant |
| CP3 | VALIDATE | Judges executed | All 3 judges return scores; blocking judges ≥ threshold | Log failure reason, escalate |
| CP4 | SUBMIT | Network response received | HTTP 2xx from VROL; case ID assigned | Retry with backoff, then escalate |
| CP5 | MONITOR | Resolution received | Final status (won/lost) recorded | Alert operations team |
| CP6 | Weekly | Batch calibration | Win rate trends match judge predictions ±10% | Trigger judge recalibration |

### Implementation Verification Questions (Pólya Phase 4)

At each checkpoint, developers should verify:

1. **Does the result make sense?** Does the reason code match the dispute description?
2. **Can we verify the evidence?** Can each evidence item be traced to a source record?
3. **Did we use all the data?** Are there merchant records we didn't check?
4. **What could go wrong?** What edge cases might break this checkpoint?

---

## 12. Data-Driven Development Methodology

> **Core Principle:** Each phase begins with synthetic data generation, enabling LLM eval-driven development and full explainability from day one.

### Methodology: Synthetic Data First (SDF)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    SYNTHETIC DATA FIRST (SDF) METHODOLOGY                    │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│   For EACH Phase:                                                            │
│                                                                              │
│   ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐  │
│   │  1. DESIGN  │───▶│  2. SYNTH   │───▶│  3. EVAL    │───▶│  4. BUILD   │  │
│   │   DATA      │    │   GENERATE  │    │   SETUP     │    │   ITERATE   │  │
│   └─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘  │
│         │                  │                  │                  │          │
│         ▼                  ▼                  ▼                  ▼          │
│   Define schemas     Generate test      LLM judges as      TDD with eval   │
│   & edge cases       data covering      acceptance         metrics as      │
│                      100% scenarios     criteria           pass/fail       │
│                                                                              │
│   ────────────────────────────────────────────────────────────────────────  │
│                                                                              │
│   KEY ARTIFACTS per Phase:                                                   │
│   • synthetic_data/{phase}/disputes.json     - Test dispute scenarios       │
│   • synthetic_data/{phase}/evidence.json     - Evidence packages            │
│   • synthetic_data/{phase}/conversations.json - Multi-turn dialogues        │
│   • evals/{phase}/judge_prompts.yaml         - LLM judge configurations     │
│   • evals/{phase}/golden_set.json            - Human-labeled ground truth   │
│   • explainability/{phase}/traces/           - BlackBox recordings          │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### SDF Workflow per Phase

| Step | Activity | Output | Gate |
|------|----------|--------|------|
| **1. Data Design** | Define schemas, edge cases, failure modes | Data specification doc | Schema review |
| **2. Synthetic Generation** | Generate 100-500 test cases per scenario | `synthetic_data/{phase}/` | Coverage check (100% scenario coverage) |
| **3. Eval Setup** | Configure LLM judges with golden set | `evals/{phase}/` | Judge calibration (κ > 0.8 with human labels) |
| **4. Build & Iterate** | TDD with eval metrics as acceptance | Working code + passing evals | All judges pass thresholds |

### LLM Eval Integration Requirements

| Eval Type | Purpose | Threshold | Frequency |
|-----------|---------|-----------|-----------|
| **Unit Evals** | Test individual agent outputs | Pass/Fail | Every PR |
| **Integration Evals** | Test phase transitions | >90% success | Daily CI |
| **Golden Set Evals** | Compare against human labels | κ > 0.8 | Weekly |
| **Regression Evals** | Catch quality degradation | No >5% drop | Every release |
| **A/B Evals** | Compare model/prompt variants | Statistical significance | Before deployment |

### Explainability Requirements (Mandatory per Phase)

Each phase MUST capture:

| Pillar | What to Capture | Storage | Retention |
|--------|-----------------|---------|-----------|
| **BlackBox** | Full input/output traces for every agent call | S3 JSON | 90 days |
| **AgentFacts** | Agent version, model, prompt hash, capabilities | PostgreSQL | Permanent |
| **GuardRails** | PII detection events, validation failures | CloudWatch | 30 days |
| **PhaseLogger** | Decision rationale at each state transition | TimescaleDB | 1 year |

### Synthetic Data Quality Criteria

| Criterion | Requirement | Validation |
|-----------|-------------|------------|
| **Diversity** | Cover all reason codes, merchant types, amounts | Automated coverage report |
| **Realism** | Pass domain expert review (dispute analyst) | Manual review of 10% sample |
| **Edge Cases** | Include 20% adversarial/boundary cases | Edge case checklist |
| **PII Safety** | Zero real PII (use Faker with custom providers) | PII scanner pre-commit hook |
| **Reproducibility** | Seeded random generation | Same seed → same data |

### Qualitative Analysis Framework (Grounded Theory Integration)

> **Core Principle:** Before quantitative metrics, apply qualitative coding to discover emergent failure patterns. Don't force observations into predetermined categories. This methodology is adapted from [HW1-HW2 Qualitative Methods](../homeworks/hw2/error_analysis_concepts.md).

#### The Open Coding → Axial Coding → Taxonomy Workflow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│              QUALITATIVE ANALYSIS WORKFLOW (per Phase)                       │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│   ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐  │
│   │ 1. COLLECT  │───▶│ 2. OPEN     │───▶│ 3. AXIAL    │───▶│ 4. BUILD    │  │
│   │   TRACES    │    │   CODING    │    │   CODING    │    │   TAXONOMY  │  │
│   └─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘  │
│         │                  │                  │                  │          │
│         ▼                  ▼                  ▼                  ▼          │
│   Gather domain       Review without      Group codes into    Formal failure│
│   artifacts &         preconceptions      3-7 categories      mode docs     │
│   conversation        Let patterns        Define hierarchy    with examples │
│   traces              EMERGE              & relationships                   │
│                                                                              │
│   KEY ARTIFACTS per Phase:                                                   │
│   • qualitative/{phase}/open_codes.csv        - Raw observations            │
│   • qualitative/{phase}/axial_categories.md   - Grouped patterns            │
│   • qualitative/{phase}/failure_taxonomy.md   - Formal failure modes        │
│   • qualitative/{phase}/saturation_log.md     - When new patterns stopped   │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

#### Open Coding Requirements per Phase

| Phase | Data Source | Target Traces | Time Investment | Saturation Goal |
|-------|-------------|---------------|-----------------|-----------------|
| **Phase 0** | Domain interviews, regulatory docs, case studies | 30-50 documents | 8-10 hours | <1 new domain concept per 10 docs |
| **Phase 1** | Synthetic dispute conversations | 50-100 traces | 4-6 hours | <1 new failure pattern per 20 traces |
| **Phase 2** | Network-specific edge cases | 30-50 traces | 3-4 hours | MC patterns fully cataloged |
| **Phase 3** | Platform integration errors | 30-50 webhook traces | 3-4 hours | Integration failures understood |

**Open Coding Process:**
1. **No preconceptions** - Do NOT start with predetermined failure categories
2. **Descriptive labels** - Use specific codes like `deadline_miscalculation`, not `error`
3. **Note both failures AND successes** - Understand what's working, not just what's broken
4. **5-10 minutes per trace** - Thorough review, not surface-level scanning

#### Axial Coding Targets

| Criteria | Requirement | Validation |
|----------|-------------|------------|
| **Category Count** | 3-7 top-level categories | Too few (<3) = too broad; Too many (>10) = diluted focus |
| **Mutual Exclusivity** | Categories conceptually distinct | New team member can classify without ambiguity |
| **Collective Exhaustion** | Cover 80%+ of observed patterns | Audit: sample 20 traces, all should map to taxonomy |
| **Hierarchy Support** | Sub-categories when needed | Max 2 levels deep |

**Axial Coding Process:**
1. **Review all open codes** - Spread them out, look for clusters
2. **Group similar codes** - "deadline_missed" + "14_day_violation" → "Timeline Compliance"
3. **Name each category** - 3-7 word descriptive title
4. **Define relationships** - Which categories often co-occur? Which are mutually exclusive?

#### Failure Mode Taxonomy Template

Each failure mode MUST include:

```markdown
### Failure Mode: [Title] (3-7 words)

**Definition:** [One testable sentence describing when this failure occurs]

**Illustrative Examples:**
1. *Dispute ID*: [ID from trace]
   *Issue*: [What went wrong, specific to this trace]

2. *Dispute ID*: [ID from trace]
   *Issue*: [What went wrong, specific to this trace]

**Frequency:** [Common/Occasional/Rare] - based on open coding counts
**Severity:** [Critical/High/Medium/Low]
**Blocking:** [Yes/No] - Does this block phase transition?
**Proposed Fix:** [Concrete intervention: prompt update, guardrail, judge, etc.]
**LLM Judge Mapping:** [Which judge detects this? Threshold?]
```

#### Dispute Domain Dimensions (for Query Diversity)

| Dimension | Values | Coverage Target |
|-----------|--------|-----------------|
| **Reason Code** | 10.4 (Fraud), 13.1 (PNR), 13.2 (Subscription) | All values tested ≥20% each |
| **Amount Range** | <$50, $50-500, $500-5K, >$5K | Each range ≥15% |
| **Evidence Completeness** | Complete, Partial (50-80%), Missing (<50%) | Equal distribution |
| **Merchant Type** | Small business (<$1M/yr), Mid-market, Enterprise | Each ≥20% |
| **Deadline Pressure** | Comfortable (>7 days), Moderate (3-7 days), Urgent (<3 days) | Each ≥20% |
| **Query Style** | Direct command, Question, Conversational, Multi-turn | Mix all styles |
| **CE 3.0 Eligibility** | Qualified, Near-miss (2/3 criteria), Disqualified | Each ≥20% |

#### Edge Cases (Mandatory 20% Coverage)

| Edge Case Type | Example Scenarios |
|----------------|-------------------|
| **Conflicting Evidence** | Transaction shows fraud + customer device history shows legitimate purchase |
| **Ambiguous Classification** | Dispute could be fraud (10.4) OR product not received (13.1) |
| **Expired Deadline** | Past 14-day evidence window, must escalate |
| **CE 3.0 Near-Miss** | Has 2 of 3 qualifying transactions, borderline eligibility |
| **Conflicting Constraints** | "Quick resolution" but missing critical evidence requiring merchant outreach |
| **Multi-Network Ambiguity** | BIN lookup returns uncertain network (Phase 2+) |
| **PII in Evidence** | Merchant provides evidence containing unredacted PAN |

#### Saturation Criteria (Exit Gates)

| Phase | Saturation Metric | Exit Criteria | What "Saturation" Means |
|-------|-------------------|---------------|-------------------------|
| Phase 0 | New domain concepts per 10 documents | <1 new concept in last 10 docs reviewed | Stop discovering new domain terms, regulations, or dispute patterns |
| Phase 1 | New failure modes per 20 conversation traces | <1 new failure mode in last 20 traces | All major chatbot failure patterns identified |
| Phase 2 | Network-specific patterns | Full MC catalog, no unknowns | Mastercard-specific edge cases fully documented |
| Phase 3 | Platform integration patterns | All webhook error types documented | Stripe/Square normalization failures cataloged |

**Definition of Saturation (from Grounded Theory):** The point at which additional analysis yields diminishing returns—no new meaningful patterns emerge from reviewing additional traces. This is NOT "we ran out of time" but "we've seen enough to know the shape of the problem."

**Saturation Fallback:** If saturation is not reached after the maximum iteration cap (50 documents for Phase 0, 100 traces for Phase 1), escalate to domain expert for assessment. The expert should determine whether to (1) continue with extended analysis, (2) accept current taxonomy as sufficient, or (3) identify gaps requiring targeted data collection.

#### Integration with LLM Judges

Each failure mode discovered through qualitative analysis maps to an LLM judge:

| Failure Mode Category | Corresponding Judge | Threshold | Blocking? |
|-----------------------|---------------------|-----------|-----------|
| Evidence Fabrication | Fabrication Detection Judge | 0.95 | Yes |
| Compliance Violations | GuardRails (PII, Deadline) | Pass/Fail | Yes |
| Classification Errors | Dispute Validity Judge | 0.7 | No (warning) |
| Evidence Quality Gaps | Evidence Quality Judge | 0.8 | Yes |
| User Intent Misalignment | Evidence Quality Judge | 0.8 | Yes |

**Workflow:** Qualitative coding (HW2) → Failure taxonomy → Judge configuration (HW3) → Automated evaluation

---

## 13. Risk Mitigation

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| LLM hallucination | Medium | High | Sync judges, schema validation, Fabrication Detection Judge |
| PCI data leak | Low | Critical | GuardRails PII detection, no PAN storage, WAF rules |
| Judge drift over time | Medium | Medium | Memory provenance for calibration, periodic revalidation |
| Network API changes | Low | Medium | Abstract translator layer, version pinning |
| Deadline miss | Medium | High | Multi-tier alerts (7, 3, 1 day), escalation workflow |

---

## 13. Phased Rollout Strategy

### Phase 0: Design & Architecture Foundation (Weeks 0-2)

> **Pólya Principle:** "Understand the problem completely before attempting to solve it."
>
> Phase 0 establishes the **big picture** through comprehensive design documentation. No synthetic data generation or code writing occurs until all Phase 0 gates pass.

#### Purpose

Before any synthetic data or code, establish a **complete architectural understanding** that all subsequent phases build upon. This prevents costly pivots during implementation and ensures alignment between domain experts, architects, and developers.

#### Design Document Structure

```
design/
├── 00_system_context.md           # Where chatbot fits in merchant ecosystem
├── 01_component_architecture.md   # Detailed component breakdown with responsibilities
├── 02_domain_model.md             # Entities, relationships, business rules
├── 03_sequence_diagrams/          # Key workflow interactions
│   ├── happy_path_fraud_10.4.mmd  # Fraud dispute resolution flow
│   ├── happy_path_pnr_13.1.mmd    # Product Not Received flow
│   ├── error_recovery.mmd         # Timeout, judge failure, retry handling
│   ├── escalation_flow.mmd        # Human handoff workflow
│   └── ce3_qualification.mmd      # CE 3.0 evidence matching logic
├── 04_api_specifications/
│   ├── mcp_tools.yaml             # OpenAPI for 4 MCP tools
│   ├── internal_events.yaml       # Event schemas between components
│   ├── network_payloads.yaml      # Visa VROL request/response formats
│   └── conversation_protocol.yaml # Chatbot message format, turn structure
├── 05_data_architecture.md        # Storage, data flows, retention policies
├── 06_security_architecture.md    # Auth, PCI compliance, PII handling
└── 07_observability_strategy.md   # Metrics, logging, alerting, dashboards
```

#### Domain Model (Critical Foundation)

| Entity | Key Attributes | Relationships | Business Rules |
|--------|---------------|---------------|----------------|
| `Dispute` | id, status, reason_code, deadline, network, amount | has_many Evidence, belongs_to Merchant | deadline = dispute_date + 14 days |
| `Evidence` | type, source, timestamp, quality_score, hash | belongs_to Dispute, validated_by Judge | source must be verifiable |
| `Merchant` | id, platform, tier, settings, win_rate | has_many Disputes | tier affects priority |
| `Judge` | type, threshold, model_version, prompt_hash | validates Evidence | blocking judges gate transitions |
| `Submission` | network_case_id, payload, response, status | belongs_to Dispute | one submission per dispute |
| `AuditLog` | pillar, event, trace_id, timestamp, data | belongs_to Dispute | immutable, 1-year retention |
| `Conversation` | session_id, turns, state, merchant_id | belongs_to Dispute | max 5 turns target |

**Entity Relationship Diagram:**

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         DOMAIN MODEL (PHASE 0)                               │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│   ┌────────────┐         ┌────────────┐         ┌────────────┐              │
│   │  Merchant  │ 1    *  │  Dispute   │ 1    *  │  Evidence  │              │
│   │            │────────▶│            │────────▶│            │              │
│   │ id         │         │ id         │         │ id         │              │
│   │ platform   │         │ status     │         │ type       │              │
│   │ tier       │         │ reason_code│         │ source     │              │
│   │ win_rate   │         │ deadline   │         │ quality    │              │
│   └────────────┘         │ amount     │         │ hash       │              │
│                          └─────┬──────┘         └─────┬──────┘              │
│                                │                      │                      │
│                                │ 1                    │ *                    │
│                                ▼                      ▼                      │
│                          ┌────────────┐         ┌────────────┐              │
│                          │ Submission │         │   Judge    │              │
│                          │            │         │            │              │
│                          │ case_id    │         │ type       │              │
│                          │ payload    │         │ threshold  │              │
│                          │ response   │         │ model_ver  │              │
│                          └────────────┘         └────────────┘              │
│                                │                      │                      │
│                                │ *                    │ *                    │
│                                ▼                      ▼                      │
│                          ┌─────────────────────────────────┐                │
│                          │           AuditLog              │                │
│                          │ (BlackBox + AgentFacts +        │                │
│                          │  GuardRails + PhaseLogger)      │                │
│                          └─────────────────────────────────┘                │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

#### Architecture Decision Records (ADRs)

| ADR | Question | Decision | Rationale | Trade-offs |
|-----|----------|----------|-----------|------------|
| ADR-001 | State Machine vs DAG orchestration? | **State Machine** | Compliance-critical phases need strict ordering; regulatory audit trail requires deterministic flow | Less flexible than DAG, but disputes have fixed workflow |
| ADR-002 | Sync vs Async judges? | **Synchronous** | Real-time feedback essential for merchant UX; blocking judges prevent bad submissions | Higher latency per turn, but <800ms P95 achievable |
| ADR-003 | Evidence storage strategy? | **S3 + PostgreSQL metadata** | Documents in S3 (cheap, durable, versioned), queryable metadata in Postgres | Two systems to maintain, but clean separation |
| ADR-004 | Network translation design? | **Adapter pattern** | Clean separation allows adding Mastercard without core changes; testable in isolation | Additional abstraction layer, but worth it |
| ADR-005 | Conversation state storage? | **Chainlit `cl.user_session` + Redis fallback** | Chainlit provides native session management; Redis for persistence across restarts | Chainlit dependency, but perfect fit for multi-turn dispute workflow |
| ADR-006 | Explainability storage? | **Separate TimescaleDB** | Time-series queries for audit; don't pollute main DB; supports retention policies | Another database, but specialized for purpose |
| ADR-007 | LLM provider abstraction? | **LiteLLM via `utils/llm_service.py`** | Provider-agnostic API; disk caching for dev cost savings; CostTracker for monitoring; Pydantic structured output for type-safe judges; logprobs for confidence-based cascading | Additional abstraction layer, but enables A/B testing, provider failover, and unified cost tracking |

#### Integration Map

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         PHASE 0: INTEGRATION MAP                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  INTERNAL DEPENDENCIES (from course materials):                              │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │ lesson-16/backend/orchestrators/                                     │    │
│  │   ├── state_machine.py → StateMachineOrchestrator (base class)      │    │
│  │   └── hierarchical.py → HierarchicalOrchestrator (evidence gather)   │    │
│  │                                                                      │    │
│  │ lesson-17/backend/                                                   │    │
│  │   ├── blackbox_recorder.py → BlackBoxRecorder                        │    │
│  │   ├── agent_facts.py → AgentFacts                                    │    │
│  │   ├── guardrails.py → GuardRails (PII detection)                     │    │
│  │   └── phase_logger.py → PhaseLogger                                  │    │
│  │                                                                      │    │
│  │ lesson-10/backend/                                                   │    │
│  │   └── ai_judge.py → LLM Judge framework                              │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                              │
│  EXTERNAL DEPENDENCIES:                                                      │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │ Network APIs:                                                        │    │
│  │   ├── Visa VROL (mock in Phase 1, real integration Phase 3)          │    │
│  │   └── Mastercard Connect (Phase 2)                                   │    │
│  │                                                                      │    │
│  │ Platform APIs (Phase 3):                                             │    │
│  │   ├── Stripe Webhooks (dispute.created, dispute.updated)             │    │
│  │   └── Square API (disputes endpoint)                                 │    │
│  │                                                                      │    │
│  │ LLM Providers:                                                       │    │
│  │   ├── OpenAI (gpt-4o for judges, gpt-4o-mini for routing)            │    │
│  │   └── Anthropic Claude (backup provider, A/B testing)                │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                              │
│  INFRASTRUCTURE REQUIREMENTS:                                                │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │ ├── PostgreSQL 15+ (disputes, merchants, submissions)                │    │
│  │ ├── Redis 7+ (sessions, evidence cache, rate limiting)               │    │
│  │ ├── S3/MinIO (evidence documents, BlackBox traces)                   │    │
│  │ ├── TimescaleDB (PhaseLogger, analytics time-series)                 │    │
│  │ └── Docker Compose (local dev) / ECS Fargate (production)            │    │
│  │                                                                      │    │
│  │ Minimum Resources (Dev):                                             │    │
│  │   CPU: 4 cores | RAM: 8GB | Storage: 50GB                            │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

#### Risk Analysis & Spike Work

Before Phase 1 begins, complete these spikes to de-risk unknowns:

| Spike ID | Risk | Likelihood | Impact | Spike Objective | Success Criteria | Duration |
|----------|------|------------|--------|-----------------|------------------|----------|
| SPIKE-001 | Visa VROL format complexity | High | High | Parse 10 real VROL examples, validate schema assumptions | Schema covers 95% of fraud/PNR fields | 2 days |
| SPIKE-002 | Judge latency > 800ms P95 | Medium | High | Benchmark 3 judge prompts with timing under load | All judges <800ms P95 at 10 QPS | 2 days |
| SPIKE-003 | CE 3.0 matching accuracy | Medium | Medium | Prototype transaction matching algorithm | >95% match rate on 50 test cases | 3 days |
| SPIKE-004 | GuardRails PII false positives | Low | Medium | Test PII detection on dispute domain vocabulary | <5% false positive rate on dispute terms | 1 day |
| SPIKE-005 | State machine recovery | Medium | High | Test state recovery after container restart | 100% state recovery from Redis | 1 day |

**Spike Output Format:**
```
spikes/
├── SPIKE-001_vrol_schema/
│   ├── README.md           # Findings and recommendations
│   ├── sample_payloads/    # Anonymized VROL examples
│   └── schema_analysis.py  # Validation script
├── SPIKE-002_judge_latency/
│   ├── README.md
│   ├── benchmark_results.json
│   └── prompt_optimizations.md
└── ...
```

#### Phase 0 Validation Gates

| Gate | Validation | Reviewer | Exit Criteria | Artifacts |
|------|------------|----------|---------------|-----------|
| **Gate 0.1** | Domain model complete | Domain expert (dispute analyst) | All 7 entities documented, relationships validated, business rules captured | `design/02_domain_model.md` |
| **Gate 0.2** | API contracts reviewed | Tech lead + frontend consumer | OpenAPI specs validated, no ambiguity, examples provided | `design/04_api_specifications/` |
| **Gate 0.3** | Architecture approved | Senior engineer | All 6 ADRs documented, trade-offs explicit, risks identified | `design/ADRs/` |
| **Gate 0.4** | Spikes completed | Engineering team | All 5 spikes completed, no blocking issues, recommendations documented | `spikes/` |
| **Gate 0.5** | Security review passed | Security engineer | PCI compliance approach validated, PII handling documented | `design/06_security_architecture.md` |
| **Gate 0.6** | Stakeholder sign-off | Product owner | Design aligns with business goals, timeline accepted | Sign-off document |
| **Gate 0.7** | Domain Open Coding complete | Domain expert + Engineering | Saturation reached (<1 new concept/10 docs), taxonomy covers 80%+ patterns | `qualitative/phase0/` |

#### Phase 0.7: Domain Open Coding (Week 2)

> **Grounded Theory Integration:** Apply qualitative coding methodology to discover emergent domain patterns before building synthetic data schemas.

**Purpose:** Use open coding and axial coding to systematically understand the dispute domain, ensuring synthetic data generation is grounded in real domain patterns rather than assumed categories.

**Process:**

**Step 1: Open Coding (8-10 hours)**
- Review 30-50 domain artifacts:
  - Dispute case studies (anonymized real disputes)
  - Regulatory documents (Reg E, Reg Z, network rules)
  - Merchant interview transcripts
  - CE 3.0 documentation
  - Existing dispute system logs
- Assign descriptive labels without preconceived categories:
  - `evidence_timing_critical` - Evidence order matters for win rate
  - `ce3_ip_matching` - IP consistency across transactions
  - `14_day_regulatory_cliff` - Hard deadline with no exceptions
  - `merchant_tier_treatment` - Network treats merchants differently by volume
- Take notes on **both patterns AND exceptions**

**Step 2: Axial Coding (2-3 hours)**
- Group open codes into 5-7 domain categories:

```
Category: Evidence Authenticity
  ├── Document verification requirements
  ├── Timestamp consistency rules
  └── Signature validation patterns

Category: Timeline Compliance
  ├── Reg E 10-day provisional credit
  ├── Reg Z 60-day billing error
  ├── Network-specific deadlines (14 days Visa)
  └── Extension request patterns

Category: CE 3.0 Qualification
  ├── Transaction matching criteria
  ├── IP/device consistency signals
  ├── Velocity pattern analysis
  └── Near-miss handling

Category: Network-Specific Patterns
  ├── Visa VROL field mappings
  ├── Mastercard Connect differences
  └── BIN routing edge cases

Category: Failure Patterns (Emergent)
  ├── [Patterns that emerge from analysis]
  └── [Not predetermined]
```

**Step 3: Domain Taxonomy Output**

```
qualitative/phase0/
├── open_codes.csv               # All observations with source references
├── axial_categories.md          # Grouped patterns with relationships
├── domain_taxonomy.md           # Formal domain category definitions
├── saturation_log.md            # When new patterns stopped emerging
└── synthetic_data_implications.md  # How taxonomy informs data generation
```

**Saturation Criteria:**
- Reviewed 30+ documents AND
- Last 10 documents yielded <1 new domain concept AND
- Domain expert validates taxonomy covers 80%+ of known patterns

**Gate 0.7 Exit Criteria:**
- [ ] Open coding complete on 30+ domain artifacts
- [ ] Axial coding produced 5-7 domain categories
- [ ] Domain taxonomy reviewed by dispute analyst
- [ ] Saturation documented and validated
- [ ] Synthetic data implications documented

#### Phase 0 Timeline

| Week | Focus Area | Activities | Deliverables | Gate |
|------|------------|------------|--------------|------|
| **Week 0** | Domain Understanding | Stakeholder interviews, domain expert sessions, existing system analysis | Domain model, business rules doc, user journey maps | Gate 0.1 |
| **Week 1** | Architecture Design | Component design, API specs, ADR drafting, sequence diagrams | ADD sections 00-04, ADR-001 to ADR-006 | Gate 0.2, 0.3 |
| **Week 2** | Validation & Risk | Spike execution, security review, **Domain Open Coding**, stakeholder sign-off | Spike results, security doc, **domain taxonomy**, all gate sign-offs | Gate 0.4, 0.5, 0.6, **0.7** |

#### Phase 0 → Phase 1 Handoff

Phase 0 outputs become Phase 1 inputs:

```
Phase 0 Output                         →  Phase 1 Input
──────────────────────────────────────────────────────────────────────────
Domain model (02_domain_model.md)      →  Synthetic data schemas (Pydantic models)
API specifications (04_api_specs/)     →  MCP tool implementations
Sequence diagrams (03_sequence/)       →  State machine transition logic
ADR decisions                          →  Implementation constraints & patterns
Spike results                          →  Known patterns, anti-patterns, benchmarks
Security architecture                  →  GuardRails configuration, PII rules
Component architecture                 →  Module structure, interface contracts
Domain taxonomy (qualitative/phase0/)  →  Failure mode categories, edge case dimensions
Open codes (open_codes.csv)            →  Synthetic data scenarios & edge cases
```

#### Phase 0 Checklist

```
□ Domain Model
  ├── □ All 7 entities defined with attributes
  ├── □ Entity relationships documented
  ├── □ Business rules captured
  └── □ Domain expert review completed

□ Architecture
  ├── □ System context diagram
  ├── □ Component architecture diagram
  ├── □ All 6 ADRs documented
  └── □ Integration map validated

□ API Contracts
  ├── □ 4 MCP tools specified (OpenAPI)
  ├── □ Internal event schemas defined
  ├── □ Network payload formats documented
  └── □ Consumer review completed

□ Sequence Diagrams
  ├── □ Happy path (fraud 10.4)
  ├── □ Happy path (PNR 13.1)
  ├── □ Error recovery flows
  ├── □ Escalation flow
  └── □ CE 3.0 qualification flow

□ Risk Mitigation
  ├── □ SPIKE-001: VROL schema analysis
  ├── □ SPIKE-002: Judge latency benchmark
  ├── □ SPIKE-003: CE 3.0 matching prototype
  ├── □ SPIKE-004: PII detection validation
  └── □ SPIKE-005: State recovery test

□ Security & Compliance
  ├── □ PCI-DSS v4.0 requirements mapped
  ├── □ PII handling strategy documented
  ├── □ Security review passed
  └── □ Audit trail requirements defined

□ Domain Open Coding (Grounded Theory)
  ├── □ 30+ domain artifacts reviewed with open coding
  ├── □ Open codes documented (qualitative/phase0/open_codes.csv)
  ├── □ Axial coding produced 5-7 domain categories
  ├── □ Domain taxonomy documented (qualitative/phase0/domain_taxonomy.md)
  ├── □ Saturation reached (<1 new concept per 10 docs)
  ├── □ Saturation log documented (qualitative/phase0/saturation_log.md)
  └── □ Synthetic data implications documented

□ Sign-offs
  ├── □ Gate 0.1: Domain model
  ├── □ Gate 0.2: API contracts
  ├── □ Gate 0.3: Architecture
  ├── □ Gate 0.4: Spikes
  ├── □ Gate 0.5: Security
  ├── □ Gate 0.6: Stakeholder
  └── □ Gate 0.7: Domain Open Coding (saturation + taxonomy)
```

---

### Phase 0.5: Chainlit UI Foundation (Week 2.5-3)

> **Purpose:** Establish interactive frontend before Phase 1 implementation, enabling developers to visualize I/O during development.

#### Deliverables

| Item | Description |
|------|-------------|
| `app.py` | Chainlit entry point with `@cl.on_chat_start`, `@cl.on_message` |
| `chainlit_phases.py` | Phase step wrappers with `@cl.step` decorator |
| `chainlit_tools.py` | Tool call visualization for 4 MCP tools |
| `.chainlit/config.toml` | UI configuration (theme, features) |
| `public/` | Custom CSS/assets for dispute branding |

#### File Structure

```
lesson-18/dispute-chatbot/
├── app.py                    # Chainlit entry point
├── chainlit_phases.py        # Phase step wrappers
├── chainlit_tools.py         # Tool visualization
├── chainlit_explainability.py # 4-pillar sidebar
├── .chainlit/
│   └── config.toml           # UI configuration
├── public/
│   └── dispute_theme.css     # Custom styling
└── backend/                  # Links to existing lesson-16/17 code
```

#### Phase 0.5 Gate

- [ ] `chainlit run app.py` starts without errors
- [ ] Welcome message displays on chat start
- [ ] Mock phase steps render correctly (CLASSIFY → MONITOR)
- [ ] Tool calls display with input/output
- [ ] Explainability sidebar shows placeholder data

---

### Phase 1: Core MVP (Weeks 3-10)

#### Step 0: Synthetic Data Generation (Week 3)

**Before any code is written**, generate synthetic data for Phase 1:

```
synthetic_data/phase1/
├── disputes/
│   ├── fraud_10.4_cases.json          # 200 fraud dispute scenarios
│   ├── pnr_13.1_cases.json            # 200 product not received scenarios
│   └── edge_cases.json                 # 100 adversarial/boundary cases
├── evidence/
│   ├── transaction_histories.json      # Prior undisputed transactions (CE 3.0)
│   ├── shipping_records.json           # FedEx/UPS tracking, POD
│   ├── customer_profiles.json          # Device fingerprints, IP, email match
│   └── incomplete_evidence.json        # Partial evidence for gap detection
├── conversations/
│   ├── happy_path_dialogues.json       # 50 successful resolution flows
│   ├── error_recovery_dialogues.json   # 30 error/retry scenarios
│   └── escalation_dialogues.json       # 20 human handoff scenarios
└── golden_set/
    ├── classification_labels.json      # Human-labeled reason code mappings
    ├── evidence_quality_scores.json    # Human-rated evidence packages
    └── fabrication_examples.json       # Known hallucination patterns
```

**Synthetic Data Schemas:**

```python
# Dispute Schema (Phase 1)
class SyntheticDispute(BaseModel):
    dispute_id: str                     # DIS-{uuid}
    network: Literal["visa"]            # Phase 1: Visa only
    reason_code: Literal["10.4", "13.1"]
    amount: Decimal                     # Range: $10 - $10,000
    currency: str = "USD"
    merchant: SyntheticMerchant
    cardholder: SyntheticCardholder     # Faker-generated, zero real PII
    transaction_date: datetime
    dispute_date: datetime
    deadline: datetime                  # +14 days from dispute_date
    expected_outcome: Literal["win", "lose", "escalate"]
    evidence_completeness: float        # 0.0 - 1.0

# Evidence Package Schema
class SyntheticEvidence(BaseModel):
    dispute_id: str
    ce3_transactions: list[Transaction] # 2-5 prior undisputed txns
    shipping: ShippingRecord | None
    customer_signals: CustomerSignals
    documents: list[Document]           # PDFs, images (synthetic)
    expected_quality_score: float       # Ground truth for judge calibration
```

**Eval Configuration (Phase 1):**

```yaml
# evals/phase1/judge_config.yaml
judges:
  evidence_quality:
    model: gpt-4o
    threshold: 0.8
    prompt_template: evidence_quality_v1.jinja2
    calibration_set: golden_set/evidence_quality_scores.json

  fabrication_detection:
    model: gpt-4o
    threshold: 0.95
    prompt_template: fabrication_detection_v1.jinja2
    calibration_set: golden_set/fabrication_examples.json

  dispute_validity:
    model: gpt-4o-mini  # Non-blocking, can use smaller model
    threshold: 0.7
    prompt_template: dispute_validity_v1.jinja2

eval_schedule:
  pr_checks: [evidence_quality, fabrication_detection]
  nightly: [dispute_validity, regression_suite]
  weekly: [golden_set_calibration]
```

**Phase 1 Gate:** Cannot proceed to implementation until:
- [ ] 500 synthetic disputes generated with 100% schema validation
- [ ] 100 golden set examples human-labeled (3 annotators, κ > 0.8)
- [ ] All 3 judges calibrated with >85% agreement on golden set
- [ ] Explainability schema defined (BlackBox, AgentFacts)
- [ ] **Phase 1 Failure Taxonomy complete** (via open/axial coding on synthetic conversations)

#### Step 0.5: Failure Taxonomy Development (Week 3-4)

> **Grounded Theory Integration:** After generating synthetic conversations, apply open coding and axial coding to discover emergent chatbot failure patterns before building judges and guardrails.

**Purpose:** Use qualitative analysis to identify actual failure modes from synthetic conversation traces, ensuring LLM judges are configured to catch real patterns rather than assumed failures.

**Process:**

**Step 1: Open Coding of Synthetic Conversations (3-4 hours)**
- Review 50-100 synthetic conversation traces
- Assign descriptive labels without preconceived failure categories:
  - `hallucinated_transaction` - Agent invented a transaction not in evidence
  - `deadline_arithmetic_error` - Calculated 14-day deadline incorrectly
  - `ce3_false_positive` - Incorrectly qualified dispute for CE 3.0
  - `pii_in_response` - Response contained unredacted PAN/SSN
  - `wrong_reason_code` - Classified fraud as PNR or vice versa
  - `evidence_gap_ignored` - Proceeded without required evidence
  - `merchant_confusion` - Response unclear about next steps

**Step 2: Axial Coding into Failure Categories (2 hours)**
- Group open codes into 5-7 failure mode categories:

```
Category: Evidence Fabrication
  ├── hallucinated_transaction
  ├── invented_shipping_proof
  └── fabricated_customer_signals

Category: Compliance Violations
  ├── deadline_arithmetic_error
  ├── pii_in_response
  └── regulatory_deadline_missed

Category: Classification Errors
  ├── wrong_reason_code
  ├── network_misidentification
  └── ce3_false_positive / ce3_false_negative

Category: Evidence Quality Gaps
  ├── evidence_gap_ignored
  ├── incomplete_package_submitted
  └── wrong_evidence_type

Category: User Experience Failures
  ├── merchant_confusion
  ├── excessive_turns
  └── unclear_next_steps
```

**Step 3: Failure Taxonomy Document**

```
qualitative/phase1/
├── open_codes.csv               # All observations: trace_id, code, quote, severity
├── axial_categories.md          # Grouped failure patterns
├── failure_taxonomy.md          # Formal failure mode definitions (template below)
├── saturation_log.md            # When new patterns stopped emerging
└── judge_mapping.md             # Which failures map to which judges
```

**Failure Mode Template (for each mode):**

```markdown
### Failure Mode: Evidence Fabrication

**Definition:** Agent generates evidence details (transactions, shipping records, customer signals) not traceable to source data provided in the conversation.

**Illustrative Examples:**
1. *Trace ID*: SYNTH-042
   *Issue*: Agent claimed "cardholder made 5 undisputed purchases in August" when only 3 transactions existed in evidence

2. *Trace ID*: SYNTH-089
   *Issue*: Agent referenced "FedEx tracking #1234567890" which was never provided by merchant

**Frequency:** 15% of traces (12/80 reviewed)
**Severity:** Critical
**Blocking:** Yes - cannot submit fabricated evidence to networks
**Proposed Fix:** Fabrication Detection Judge with 0.95 threshold
**LLM Judge:** `fabrication_detection` - Compare agent output against source evidence
```

**Saturation Criteria:**
- Reviewed 50+ synthetic conversation traces AND
- Last 20 traces yielded <1 new failure pattern AND
- Team can classify new traces without ambiguity

**Phase 1 Step 0.5 Exit Criteria:**
- [ ] Open coding complete on 50+ synthetic conversation traces
- [ ] Axial coding produced 5-7 failure mode categories
- [ ] Each failure mode has formal definition + 2 examples
- [ ] Failure modes mapped to corresponding LLM judges
- [ ] Saturation documented and validated
- [ ] Judge thresholds aligned with failure severity

**Integration with LLM Judges:**

| Failure Mode | Judge | Threshold | Rationale |
|--------------|-------|-----------|-----------|
| Evidence Fabrication | Fabrication Detection | 0.95 | Critical - must catch nearly all |
| Compliance Violations | GuardRails (PII) | Pass/Fail | Binary - either violates or doesn't |
| Compliance Violations | GuardRails (Deadline) | Pass/Fail | Binary - must be accurate |
| Classification Errors | Dispute Validity | 0.7 | Non-blocking warning |
| Evidence Quality Gaps | Evidence Quality | 0.8 | Blocking - insufficient evidence |
| User Experience | Not judged | N/A | Addressed via prompt engineering |

#### Architecture Design

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         PHASE 1: CORE MVP ARCHITECTURE                       │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌─────────────┐     ┌─────────────────────────────────────────────────┐   │
│  │   Merchant  │────▶│              CHATBOT INTERFACE                   │   │
│  │   (Web UI)  │◀────│         (REST API / WebSocket)                   │   │
│  └─────────────┘     └─────────────────────────────────────────────────┘   │
│                                        │                                     │
│                                        ▼                                     │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │                    STATE MACHINE ORCHESTRATOR                         │  │
│  │  ┌──────────┐  ┌──────────────┐  ┌──────────┐  ┌────────┐  ┌───────┐ │  │
│  │  │ CLASSIFY │─▶│GATHER_EVIDENCE│─▶│ VALIDATE │─▶│ SUBMIT │─▶│MONITOR│ │  │
│  │  └──────────┘  └──────────────┘  └──────────┘  └────────┘  └───────┘ │  │
│  └──────────────────────────────────────────────────────────────────────┘  │
│                          │                    │                             │
│            ┌─────────────┘                    └──────────────┐              │
│            ▼                                                 ▼              │
│  ┌───────────────────────────┐              ┌────────────────────────────┐ │
│  │  HIERARCHICAL GATHERER    │              │     LLM JUDGE PANEL        │ │
│  │  ┌─────────────────────┐  │              │  ┌────────┐ ┌───────────┐  │ │
│  │  │   Planner Agent     │  │              │  │Evidence│ │Fabrication│  │ │
│  │  │        │            │  │              │  │Quality │ │ Detection │  │ │
│  │  │  ┌─────┼─────┐      │  │              │  │ (0.8)  │ │  (0.95)   │  │ │
│  │  │  ▼     ▼     ▼      │  │              │  └────────┘ └───────────┘  │ │
│  │  │ Txn  Ship  Cust     │  │              │  ┌────────────────────┐    │ │
│  │  │ Spec Spec  Spec     │  │              │  │ Dispute Validity   │    │ │
│  │  └─────────────────────┘  │              │  │      (0.7)         │    │ │
│  └───────────────────────────┘              │  └────────────────────┘    │ │
│                                             └────────────────────────────┘ │
│                                                                              │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │                     EXPLAINABILITY LAYER                              │  │
│  │  ┌──────────┐  ┌───────────┐  ┌───────────┐  ┌───────────────────┐   │  │
│  │  │BlackBox  │  │AgentFacts │  │GuardRails │  │   PhaseLogger     │   │  │
│  │  │Recorder  │  │(Identity) │  │(PCI/PII)  │  │  (Reasoning)      │   │  │
│  │  └──────────┘  └───────────┘  └───────────┘  └───────────────────┘   │  │
│  └──────────────────────────────────────────────────────────────────────┘  │
│                                        │                                     │
│                                        ▼                                     │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │                    VISA NETWORK ADAPTER                               │  │
│  │           Internal Schema ──▶ VROL Format ──▶ Visa API                │  │
│  └──────────────────────────────────────────────────────────────────────┘  │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘

Data Stores:
┌────────────────┐  ┌────────────────┐  ┌────────────────┐
│  PostgreSQL    │  │   Redis        │  │  S3 Evidence   │
│  (Disputes)    │  │  (Sessions)    │  │   (Documents)  │
└────────────────┘  └────────────────┘  └────────────────┘
```

#### Deliverables
- Visa network only
- Fraud (10.4) and Product Not Received (13.1) reason codes
- State Machine orchestration with 5 phases
- All 4 explainability pillars
- 3 synchronous LLM judges

#### Phase 1 Eval Metrics (Exit Criteria)

| Metric | Target | Measurement |
|--------|--------|-------------|
| Synthetic test pass rate | 100% | All 500 synthetic disputes process without error |
| Judge calibration κ | >0.8 | Cohen's kappa vs golden set |
| Evidence quality judge accuracy | >90% | Precision/recall on golden set |
| Fabrication detection recall | >99% | Must catch all known hallucination patterns |
| Explainability coverage | 100% | All agent calls have BlackBox traces |
| State transition logging | 100% | PhaseLogger captures every transition |

#### Phase 1 Explainability Checkpoints

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    PHASE 1 EXPLAINABILITY AUDIT TRAIL                        │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  CLASSIFY Phase:                                                             │
│  ├── BlackBox: Input dispute → Output reason code + confidence               │
│  ├── AgentFacts: Classifier model version, prompt hash                       │
│  └── PhaseLogger: "Classified as 10.4 because [rationale]"                   │
│                                                                              │
│  GATHER_EVIDENCE Phase:                                                      │
│  ├── BlackBox: Each specialist input/output with timing                      │
│  ├── AgentFacts: Specialist versions, data sources queried                   │
│  ├── GuardRails: PII scan results (PASS/FAIL per field)                      │
│  └── PhaseLogger: "Found 3 CE 3.0 txns, missing shipping POD"                │
│                                                                              │
│  VALIDATE Phase:                                                             │
│  ├── BlackBox: Evidence package → Judge scores                               │
│  ├── AgentFacts: Judge model versions, prompt hashes                         │
│  └── PhaseLogger: "Evidence quality: 0.87, Fabrication: PASS (0.98)"         │
│                                                                              │
│  SUBMIT Phase:                                                               │
│  ├── BlackBox: Internal schema → VROL payload → Network response             │
│  ├── GuardRails: Final PII/PCI check before submission                       │
│  └── PhaseLogger: "Submitted to VROL, Case ID: VIS-2024-12345"               │
│                                                                              │
│  MONITOR Phase:                                                              │
│  ├── BlackBox: Polling history, status transitions                           │
│  └── PhaseLogger: "Won at 2024-12-15, actual outcome matches prediction"     │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

### Phase 2: Network Expansion (Weeks 11-14)

#### Step 0: Synthetic Data Generation (Week 11)

**Before Phase 2 implementation**, extend synthetic data:

```
synthetic_data/phase2/
├── disputes/
│   ├── mastercard_4837_fraud.json      # 150 MC fraud scenarios
│   ├── mastercard_4855_pnr.json        # 150 MC product not received
│   ├── visa_13.2_subscription.json     # 100 subscription canceled
│   └── cross_network_edge_cases.json   # 50 BIN routing edge cases
├── evidence/
│   ├── mc_specific_evidence.json       # Mastercard-specific fields
│   ├── subscription_cancellation.json  # Cancellation proof, terms
│   └── batch_processing_sets.json      # 10 batches of 100 disputes each
├── conversations/
│   ├── network_selection_dialogues.json # "Is this Visa or Mastercard?"
│   ├── batch_status_dialogues.json     # Bulk processing conversations
│   └── subscription_dispute_flows.json  # Subscription-specific flows
└── golden_set/
    ├── network_routing_labels.json     # BIN → Network mapping validation
    ├── mc_evidence_quality.json        # MC-specific evidence scoring
    └── subscription_validity.json      # Subscription dispute ground truth
```

**Phase 2 Incremental Eval Setup:**

```yaml
# evals/phase2/judge_config.yaml (extends phase1)
judges:
  network_router:
    model: gpt-4o-mini
    threshold: 0.99  # Critical: must correctly route
    prompt_template: network_routing_v1.jinja2
    calibration_set: golden_set/network_routing_labels.json

  subscription_validity:
    model: gpt-4o
    threshold: 0.75
    prompt_template: subscription_validity_v1.jinja2
    calibration_set: golden_set/subscription_validity.json

eval_schedule:
  pr_checks: [network_router, evidence_quality, fabrication_detection]
  nightly: [batch_throughput_test, cross_network_regression]
  weekly: [mc_golden_set_calibration]
```

**Phase 2 Gate:** Cannot proceed to implementation until:
- [ ] 400 new synthetic disputes (MC + subscription) with schema validation
- [ ] Network routing golden set: 100 examples, 99.5% accuracy target
- [ ] Batch processing test data: 10 batches × 100 disputes
- [ ] MC-specific judge calibrated (κ > 0.8)

#### Architecture Design

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    PHASE 2: NETWORK EXPANSION ARCHITECTURE                   │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                    MULTI-NETWORK ROUTER                              │    │
│  │                                                                      │    │
│  │   Dispute ──▶ Network Detection ──┬──▶ Visa Pipeline (Phase 1)      │    │
│  │              (BIN lookup)         │                                  │    │
│  │                                   └──▶ Mastercard Pipeline (NEW)    │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                        │                                     │
│                    ┌───────────────────┴───────────────────┐                │
│                    ▼                                       ▼                │
│  ┌─────────────────────────────────┐  ┌─────────────────────────────────┐  │
│  │      VISA ORCHESTRATOR          │  │   MASTERCARD ORCHESTRATOR       │  │
│  │  (State Machine - unchanged)    │  │   (State Machine - new)         │  │
│  │                                 │  │                                 │  │
│  │  Reason Codes: 10.4, 13.1, 13.2 │  │  Reason Codes: 4837, 4855, 4841 │  │
│  └─────────────────────────────────┘  └─────────────────────────────────┘  │
│                    │                                       │                │
│                    └───────────────────┬───────────────────┘                │
│                                        ▼                                     │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │              OPTIMIZED HIERARCHICAL GATHERER                          │  │
│  │                                                                       │  │
│  │  ┌─────────────────────────────────────────────────────────────────┐ │  │
│  │  │                    Planner Agent                                 │ │  │
│  │  │    ┌────────────┬────────────┬────────────┬────────────┐        │ │  │
│  │  │    ▼            ▼            ▼            ▼            ▼        │ │  │
│  │  │  Txn Spec   Ship Spec   Cust Spec   Email Spec   Device Spec   │ │  │
│  │  │  (cached)   (parallel)  (parallel)  (NEW)        (NEW)         │ │  │
│  │  └─────────────────────────────────────────────────────────────────┘ │  │
│  │                                                                       │  │
│  │  Optimizations:                                                       │  │
│  │  • Transaction cache (TTL: 24h) for repeated lookups                  │  │
│  │  • Parallel specialist execution with ThreadPoolExecutor              │  │
│  │  • Early termination when sufficient evidence gathered                │  │
│  └──────────────────────────────────────────────────────────────────────┘  │
│                                                                              │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │                    BATCH PROCESSING ENGINE                            │  │
│  │                                                                       │  │
│  │   Dispute Queue ──▶ Priority Scheduler ──▶ Worker Pool (N=10)        │  │
│  │                            │                                          │  │
│  │                     ┌──────┴──────┐                                   │  │
│  │                     ▼             ▼                                   │  │
│  │              [Urgent: <3 days] [Normal: >3 days]                      │  │
│  │                                                                       │  │
│  │   SLA: Process 100 disputes/hour for high-volume merchants            │  │
│  └──────────────────────────────────────────────────────────────────────┘  │
│                                                                              │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │                    NETWORK TRANSLATION LAYER                          │  │
│  │                                                                       │  │
│  │   Internal Schema ──┬──▶ VROL Format (Visa)                           │  │
│  │                     │                                                 │  │
│  │                     └──▶ Mastercard Connect Format (NEW)              │  │
│  │                                                                       │  │
│  │   Field Mappings:                                                     │  │
│  │   • reason_code → disputeCondition (Visa) / reasonCode (MC)           │  │
│  │   • amount → disputeAmount (Visa) / claimAmount (MC)                  │  │
│  │   • currency → disputeCurrency (Visa) / claimCurrencyCode (MC)        │  │
│  └──────────────────────────────────────────────────────────────────────┘  │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

#### Deliverables
- Add Mastercard (reason codes 4837, 4855)
- Add Subscription Canceled (13.2) dispute type
- Hierarchical evidence gathering optimization
- Batch processing for high-volume merchants

#### Phase 2 Eval Metrics (Exit Criteria)

| Metric | Target | Measurement |
|--------|--------|-------------|
| Network routing accuracy | >99.5% | BIN → Network classification |
| MC pipeline pass rate | 100% | All MC synthetic disputes process correctly |
| Batch throughput | 100 disputes/hour | Worker pool processing rate |
| Cross-network regression | 0% | No degradation on Phase 1 Visa tests |
| Subscription dispute accuracy | >85% | Judge agreement on subscription cases |

#### Phase 2 Explainability Additions

```
Additional Traces for Phase 2:
├── NetworkRouter traces: BIN lookup → Network decision → Confidence
├── BatchProcessor traces: Queue position, worker assignment, timing
├── CacheHit traces: Transaction cache utilization metrics
└── CrossNetwork traces: Field mapping transformations (Internal → MC)
```

---

### Phase 3: Platform Integration (Weeks 15-18)

#### Step 0: Synthetic Data Generation (Week 15)

**Before Phase 3 implementation**, generate platform-specific data:

```
synthetic_data/phase3/
├── platform_events/
│   ├── stripe_webhooks.json            # 200 Stripe dispute.created events
│   ├── square_api_responses.json       # 200 Square dispute payloads
│   └── platform_edge_cases.json        # 50 malformed/incomplete events
├── analytics/
│   ├── historical_disputes.json        # 1000 disputes with outcomes (for analytics)
│   ├── win_rate_trends.json            # Time-series win rate data
│   └── merchant_performance.json       # Per-merchant metrics
├── notifications/
│   ├── deadline_scenarios.json         # 7, 3, 1 day deadline triggers
│   ├── alert_templates.json            # Email/SMS/Slack content
│   └── escalation_paths.json           # Routing rules for alerts
├── dashboard/
│   ├── merchant_sessions.json          # Dashboard interaction flows
│   ├── filter_combinations.json        # Search/filter test cases
│   └── visualization_data.json         # Chart rendering data
└── golden_set/
    ├── stripe_normalization.json       # Stripe → Internal schema mapping
    ├── square_normalization.json       # Square → Internal schema mapping
    └── analytics_accuracy.json         # Ground truth for dashboard metrics
```

**Phase 3 Eval Setup:**

```yaml
# evals/phase3/judge_config.yaml
judges:
  platform_normalizer:
    model: gpt-4o-mini
    threshold: 0.99  # Schema mapping must be exact
    prompt_template: platform_normalization_v1.jinja2
    calibration_set: golden_set/stripe_normalization.json

  analytics_accuracy:
    type: deterministic  # Not LLM - exact calculation check
    tolerance: 0.001  # Win rate must be accurate to 0.1%
    calibration_set: golden_set/analytics_accuracy.json

eval_schedule:
  pr_checks: [platform_normalizer, full_regression]
  nightly: [analytics_accuracy, notification_delivery]
  weekly: [end_to_end_platform_test]
```

**Phase 3 Gate:** Cannot proceed to implementation until:
- [ ] 400 platform event synthetic data (Stripe + Square)
- [ ] Analytics golden set: 100 merchant-period combinations
- [ ] Notification delivery test harness configured
- [ ] Dashboard E2E test data prepared

#### Architecture Design

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                  PHASE 3: PLATFORM INTEGRATION ARCHITECTURE                  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │                    PLATFORM CONNECTOR HUB                             │   │
│  │                                                                       │   │
│  │   ┌─────────────┐   ┌─────────────┐   ┌─────────────┐   ┌─────────┐  │   │
│  │   │   Stripe    │   │   Square    │   │  PayPal     │   │  Custom │  │   │
│  │   │  Webhooks   │   │    API      │   │  (Future)   │   │   API   │  │   │
│  │   └──────┬──────┘   └──────┬──────┘   └──────┬──────┘   └────┬────┘  │   │
│  │          │                 │                 │               │       │   │
│  │          └────────────┬────┴────────────┬────┘               │       │   │
│  │                       ▼                 ▼                    ▼       │   │
│  │              ┌─────────────────────────────────────────────────┐     │   │
│  │              │         UNIFIED DISPUTE INGESTION               │     │   │
│  │              │                                                 │     │   │
│  │              │  Platform Event ──▶ Normalize ──▶ Enrich ──▶ Queue   │   │
│  │              │                                                 │     │   │
│  │              │  Normalizations:                                │     │   │
│  │              │  • Stripe: dispute.created → Internal Schema    │     │   │
│  │              │  • Square: dispute.state.changed → Internal     │     │   │
│  │              │  • PayPal: PP-D-* → Internal Schema             │     │   │
│  │              └─────────────────────────────────────────────────┘     │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
│                                        │                                     │
│                                        ▼                                     │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │                    DISPUTE PROCESSING ENGINE                          │   │
│  │                     (Phase 1 + Phase 2 combined)                      │   │
│  │                                                                       │   │
│  │   Multi-Network Router ──▶ State Machine ──▶ Evidence ──▶ Submit     │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
│                                        │                                     │
│                                        ▼                                     │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │                    ANALYTICS & DASHBOARD                              │   │
│  │                                                                       │   │
│  │  ┌─────────────────────────────────────────────────────────────────┐ │   │
│  │  │                    METRICS PIPELINE                              │ │   │
│  │  │                                                                  │ │   │
│  │  │  Event Stream ──▶ Aggregator ──▶ TimescaleDB ──▶ Grafana        │ │   │
│  │  │                                                                  │ │   │
│  │  │  Metrics:                                                        │ │   │
│  │  │  • Win rate by reason code, network, merchant                    │ │   │
│  │  │  • Evidence gathering latency (P50, P95, P99)                    │ │   │
│  │  │  • Judge accuracy vs actual outcomes                             │ │   │
│  │  │  • CE 3.0 qualification rate trends                              │ │   │
│  │  └─────────────────────────────────────────────────────────────────┘ │   │
│  │                                                                       │   │
│  │  ┌─────────────────────────────────────────────────────────────────┐ │   │
│  │  │                    MERCHANT DASHBOARD                            │ │   │
│  │  │                                                                  │ │   │
│  │  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐           │ │   │
│  │  │  │  Overview    │  │  Disputes    │  │  Analytics   │           │ │   │
│  │  │  │  • Active    │  │  • In Progress│  │  • Win Rate  │           │ │   │
│  │  │  │  • Won/Lost  │  │  • Evidence   │  │  • Trends    │           │ │   │
│  │  │  │  • Pending   │  │  • Deadlines  │  │  • Insights  │           │ │   │
│  │  │  └──────────────┘  └──────────────┘  └──────────────┘           │ │   │
│  │  │                                                                  │ │   │
│  │  │  Tech Stack: React + TailwindCSS + Chart.js                      │ │   │
│  │  └─────────────────────────────────────────────────────────────────┘ │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │                    NOTIFICATION ENGINE                                │   │
│  │                                                                       │   │
│  │   Event Triggers:                                                     │   │
│  │   • Deadline approaching (7, 3, 1 day) → Email + SMS + Slack          │   │
│  │   • Dispute resolved → Email with outcome summary                     │   │
│  │   • Judge failure → Slack alert to operations                         │   │
│  │   • Win rate drop >10% → Executive alert                              │   │
│  │                                                                       │   │
│  │   Integrations: SendGrid, Twilio, Slack Webhooks                      │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘

Data Architecture (Full System):
┌────────────────┐  ┌────────────────┐  ┌────────────────┐  ┌────────────────┐
│  PostgreSQL    │  │   Redis        │  │  S3 Evidence   │  │  TimescaleDB   │
│  (Disputes)    │  │  (Sessions)    │  │   (Documents)  │  │  (Analytics)   │
└────────────────┘  └────────────────┘  └────────────────┘  └────────────────┘
```

#### Deliverables
- Stripe webhook integration
- Square API connector
- Batch dispute processing
- Dashboard and analytics

#### Phase 3 Eval Metrics (Exit Criteria)

| Metric | Target | Measurement |
|--------|--------|-------------|
| Platform normalization accuracy | >99% | Stripe/Square → Internal schema |
| Analytics dashboard accuracy | >99.9% | Win rate calculations vs ground truth |
| Notification delivery rate | >99% | All deadline alerts sent on time |
| E2E latency (platform → resolution) | <30 min | Webhook received to evidence submitted |
| Full regression pass rate | 100% | All Phase 1 + Phase 2 tests still pass |

#### Phase 3 Explainability Additions

```
Additional Traces for Phase 3:
├── PlatformIngestion traces: Webhook/API → Normalization → Queue
├── Analytics traces: Query → Aggregation → Visualization
├── Notification traces: Trigger → Template → Delivery status
└── Dashboard traces: User action → Backend query → Response
```

---

## 14. Development Methodology Summary

### Prerequisites: Phase 0 Design Gates

> **Critical:** No synthetic data generation or implementation code begins until ALL Phase 0 gates pass.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    METHODOLOGY SEQUENCE                                      │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│   PHASE 0: DESIGN (Weeks 0-2)                                               │
│   ├── Domain model → Gate 0.1                                               │
│   ├── API contracts → Gate 0.2                                              │
│   ├── Architecture (ADRs) → Gate 0.3                                        │
│   ├── Spikes → Gate 0.4                                                     │
│   ├── Security → Gate 0.5                                                   │
│   └── Stakeholder sign-off → Gate 0.6                                       │
│                    │                                                         │
│                    ▼ ALL GATES PASS                                         │
│                                                                              │
│   PHASES 1-3: SYNTHETIC DATA FIRST (SDF)                                    │
│   ├── Generate synthetic data from Phase 0 schemas                          │
│   ├── Configure LLM judges from Phase 0 API contracts                       │
│   ├── Implement using Phase 0 ADR decisions                                 │
│   └── Validate against Phase 0 spike findings                               │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

**Phase 0 Outputs Used in SDF:**
| Phase 0 Artifact | SDF Usage |
|------------------|-----------|
| Domain model entities | Pydantic schemas for synthetic data |
| API specifications | Judge evaluation criteria |
| Sequence diagrams | Test case scenarios |
| Spike results | Edge case generation |
| Security architecture | PII rules for synthetic data |

---

### Synthetic Data First (SDF) Checklist

```
For EVERY Phase:

□ Week N (Start):
  ├── Define data schemas for new functionality
  ├── Generate synthetic test data (100-500 cases)
  ├── Create golden set with human labels
  └── Configure LLM judges with calibration

□ Week N+1 to N+X (Implementation):
  ├── TDD with eval metrics as acceptance criteria
  ├── Every PR runs LLM judges (blocking on failure)
  ├── BlackBox traces for all new agent calls
  └── PhaseLogger captures all decision points

□ Week N+X (Exit):
  ├── 100% synthetic test pass rate
  ├── Judge calibration κ > 0.8
  ├── Explainability coverage 100%
  └── Regression tests still pass
```

### Eval-Driven Development Flow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    EVAL-DRIVEN DEVELOPMENT WORKFLOW                          │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│   Developer writes code                                                      │
│         │                                                                    │
│         ▼                                                                    │
│   ┌─────────────┐     ┌─────────────┐     ┌─────────────┐                   │
│   │  Unit Tests │────▶│  LLM Evals  │────▶│  BlackBox   │                   │
│   │  (pytest)   │     │  (judges)   │     │  Capture    │                   │
│   └─────────────┘     └─────────────┘     └─────────────┘                   │
│         │                   │                   │                            │
│         │                   │                   │                            │
│         ▼                   ▼                   ▼                            │
│   ┌─────────────────────────────────────────────────────────────────────┐   │
│   │                         PR GATE                                      │   │
│   │                                                                      │   │
│   │  ✓ pytest passes (100%)                                              │   │
│   │  ✓ Evidence Quality Judge > 0.8                                      │   │
│   │  ✓ Fabrication Detection > 0.95                                      │   │
│   │  ✓ BlackBox traces captured                                          │   │
│   │  ✓ No regression on existing evals                                   │   │
│   └─────────────────────────────────────────────────────────────────────┘   │
│                                    │                                         │
│                          All pass? │                                         │
│                    ┌───────────────┴───────────────┐                        │
│                    │                               │                        │
│                    ▼                               ▼                        │
│              ┌──────────┐                    ┌──────────┐                   │
│              │  MERGE   │                    │  BLOCK   │                   │
│              │  to main │                    │  + Debug │                   │
│              └──────────┘                    └──────────┘                   │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Explainability Audit Readiness

At any point, the system MUST be able to answer:

| Question | Source | Example Query |
|----------|--------|---------------|
| "What did the agent decide?" | PhaseLogger | `SELECT decision, rationale FROM phase_logs WHERE dispute_id = ?` |
| "What data did it see?" | BlackBox | `SELECT input, output FROM blackbox WHERE session_id = ?` |
| "Which model made this decision?" | AgentFacts | `SELECT model_version, prompt_hash FROM agent_facts WHERE agent_id = ?` |
| "Was PII properly handled?" | GuardRails | `SELECT scan_result, fields_redacted FROM guardrails_log WHERE dispute_id = ?` |
| "Can we reproduce this decision?" | All pillars | Replay BlackBox input through same AgentFacts configuration |

---

## 15. Comprehensive LLM Evaluation Methodology (Homework Adaptation)

> **Source:** This section adapts evaluation methodologies from the LLM Evaluation course homeworks (HW1-HW5) to the dispute chatbot context. See [EVALUATION_METHODOLOGY_RESEARCH_REPORT.md](../homeworks/EVALUATION_METHODOLOGY_RESEARCH_REPORT.md) for full methodology documentation.

### Evaluation Philosophy: Qualitative → Quantitative → Statistical

```
┌─────────────────────────────────────────────────────────────────────────────┐
│              EVALUATION METHODOLOGY PROGRESSION                              │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│   HW2 Methods           HW3 Methods           HW4 Methods      HW5 Methods  │
│   (Qualitative)         (Quantitative)        (Retrieval)      (Agent)      │
│                                                                              │
│   Open/Axial Coding  →  LLM-as-Judge      →  Recall@k/MRR  →  Transition   │
│   Failure Taxonomy      TPR/TNR/Bias         BM25 Ranking      Matrices     │
│                         Correction                                           │
│                                                                              │
│   UNDERSTAND         →  MEASURE AT SCALE →  ISOLATE RETRIEVAL → DEBUG AGENT │
│   failures              with confidence     bottlenecks         pipeline    │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 15.1 HW1 Adaptation: System Prompt Engineering for Dispute Domain

**Technique:** Define clear bot role, behavioral rules, output format, and safety boundaries.

**Application to Dispute Chatbot:**

| HW1 Concept | Dispute Chatbot Application |
|-------------|----------------------------|
| **Role Definition** | "You are a dispute resolution specialist helping merchants defend against chargebacks. You have expertise in Visa CE 3.0 requirements and Reg E/Z compliance." |
| **Behavioral Rules (Always)** | Always verify evidence sources; Always calculate deadlines from dispute date; Always check CE 3.0 eligibility for fraud disputes |
| **Behavioral Rules (Never)** | Never fabricate transaction details; Never store unredacted PANs; Never submit evidence past deadline |
| **Output Format** | Structured evidence packages with required fields per reason code |
| **Safety Clauses** | Escalate to human when judge confidence <0.7; Redact all PII before logging |

**Query Diversity Dimensions for Dispute Domain:**

| Dimension | Values | Coverage Target |
|-----------|--------|-----------------|
| **Reason Code** | 10.4 (Fraud), 13.1 (PNR), 13.2 (Subscription) | Each ≥20% |
| **Amount Range** | <$50, $50-500, $500-5K, >$5K | Each ≥15% |
| **Merchant Type** | Small business, Mid-market, Enterprise | Each ≥20% |
| **Evidence Completeness** | Complete, Partial (50-80%), Missing (<50%) | Equal distribution |
| **CE 3.0 Eligibility** | Qualified, Near-miss, Disqualified | Each ≥20% |
| **Deadline Pressure** | Comfortable (>7d), Moderate (3-7d), Urgent (<3d) | Each ≥20% |

**Artifacts:**
```
prompts/
├── system_prompt_v1.md           # Initial dispute specialist prompt
├── system_prompt_v2.md           # Refined after open coding
├── query_diversity_matrix.csv    # 100+ test queries across dimensions
└── prompt_iteration_log.md       # What changed between versions
```

---

### 15.2 HW2 Adaptation: Error Analysis with Open/Axial Coding

**Technique:** Discover failure patterns through qualitative coding before quantifying them.

**Application to Dispute Chatbot:**

#### Open Coding Protocol (First 50-100 Traces)

```
For each dispute conversation trace:
1. Read WITHOUT preconceived failure categories
2. Assign descriptive labels to observations:
   - `hallucinated_transaction` - Agent invented a transaction
   - `deadline_arithmetic_error` - Calculated 14-day deadline wrong
   - `ce3_false_positive` - Incorrectly qualified for CE 3.0
   - `pii_in_response` - Unredacted PAN/SSN in output
   - `wrong_reason_code` - Classified fraud as PNR
   - `evidence_gap_ignored` - Proceeded without required evidence
   - `merchant_confusion` - Unclear next steps for merchant
3. Note both FAILURES and SUCCESSES
4. Spend 5-10 minutes per trace
```

#### Axial Coding → Failure Taxonomy

| Category | Open Codes Grouped | Frequency | Severity | Blocking? |
|----------|-------------------|-----------|----------|-----------|
| **Evidence Fabrication** | hallucinated_transaction, invented_shipping_proof, fabricated_customer_signals | 15% | Critical | Yes |
| **Compliance Violations** | deadline_arithmetic_error, pii_in_response, regulatory_deadline_missed | 10% | Critical | Yes |
| **Classification Errors** | wrong_reason_code, network_misidentification, ce3_false_positive | 12% | High | Warning |
| **Evidence Quality Gaps** | evidence_gap_ignored, incomplete_package_submitted, wrong_evidence_type | 20% | High | Yes |
| **User Experience Failures** | merchant_confusion, excessive_turns, unclear_next_steps | 18% | Medium | No |

#### Failure Mode Template (per HW2)

```markdown
### Failure Mode: Evidence Fabrication

**Definition:** Agent generates evidence details (transactions, shipping records,
customer signals) not traceable to source data provided in the conversation.

**Illustrative Examples:**
1. *Dispute ID*: SYNTH-042
   *Issue*: Agent claimed "cardholder made 5 undisputed purchases in August"
   when only 3 transactions existed in evidence

2. *Dispute ID*: SYNTH-089
   *Issue*: Agent referenced "FedEx tracking #1234567890" which was never
   provided by merchant

**Frequency:** 15% of traces (12/80 reviewed)
**Severity:** Critical
**Blocking:** Yes - cannot submit fabricated evidence to networks
**Proposed Fix:** Fabrication Detection Judge with 0.95 threshold
**LLM Judge Mapping:** fabrication_detection - Compare agent output against source evidence
```

**Saturation Criteria:** Stop open coding when <1 new pattern per 20 traces reviewed.

**Artifacts:**
```
qualitative/phase1/
├── open_codes.csv                # trace_id, code, quote, severity
├── axial_categories.md           # Grouped patterns
├── failure_taxonomy.md           # Formal failure mode definitions
├── saturation_log.md             # When new patterns stopped
└── judge_mapping.md              # Failure mode → Judge mapping
```

---

### 15.3 HW3 Adaptation: LLM-as-Judge with Bias Correction

**Technique:** Automated evaluation with statistical correction for judge imperfections.

**Application to Dispute Chatbot:**

#### Judge Configuration

| Judge | Evaluates | Threshold | TPR Target | TNR Target | Blocking? |
|-------|-----------|-----------|------------|------------|-----------|
| **Evidence Quality** | Is evidence sufficient for network win? | 0.8 | ≥0.90 | ≥0.85 | Yes |
| **Fabrication Detection** | Did agent invent details? | 0.95 | ≥0.99 | ≥0.90 | Yes |
| **Dispute Validity** | Is this a legitimate defense? | 0.7 | ≥0.85 | ≥0.80 | No (warning) |

#### Data Splitting Strategy (per HW3)

```
Golden Set: 150 human-labeled dispute conversations

Split:
├── Train (15%): 22 examples → Few-shot examples for judge prompt
├── Dev (40%): 60 examples → Iterative prompt refinement
└── Test (45%): 68 examples → Final TPR/TNR calculation (NEVER touch during dev)
```

#### Judge Prompt Development Workflow

```
1. Start with baseline prompt (from failure taxonomy definitions)
2. Select few-shot examples from Train set (1 PASS : 3 FAIL ratio)
3. Run on Dev set, calculate TPR/TNR
4. Iterate prompt based on false positive/negative analysis
5. STOP when Dev TPR ≥ 0.85 AND Dev TNR ≥ 0.85
6. Lock prompt, run ONCE on Test set for final metrics
7. Apply bias correction formula
```

#### Bias Correction Formula (judgy library)

```python
# From HW3 bias_correction_tutorial.md
from judgy import BiasCorrector

# Test set results
tpr = 0.90  # True Positive Rate from test set
tnr = 0.85  # True Negative Rate from test set

# Production evaluation (1000 unlabeled disputes)
p_obs = 0.80  # Judge says 80% pass

# Corrected rate
corrector = BiasCorrector(tpr=tpr, tnr=tnr)
theta_hat = corrector.correct(p_obs)
# θ̂ = (0.80 + 0.85 - 1) / (0.90 + 0.85 - 1) = 0.65 / 0.75 = 0.867

# Result: True pass rate is 86.7%, not 80%
# Judge was too strict (low TPR), missed some passing cases
```

#### 95% Confidence Interval (Bootstrap)

```python
import numpy as np

# Bootstrap 10,000 resamples
results = [1] * 867 + [0] * 133  # Based on corrected rate
bootstrap_rates = []
for _ in range(10000):
    resample = np.random.choice(results, size=len(results), replace=True)
    bootstrap_rates.append(np.mean(resample))

ci_lower = np.percentile(bootstrap_rates, 2.5)
ci_upper = np.percentile(bootstrap_rates, 97.5)

# Report: "Corrected Success Rate: 86.7%, 95% CI: [84.2%, 89.1%]"
```

**Artifacts:**
```
evals/phase1/
├── judge_prompts/
│   ├── evidence_quality_v1.jinja2
│   ├── fabrication_detection_v1.jinja2
│   └── dispute_validity_v1.jinja2
├── golden_set/
│   ├── train_set.json (22 examples)
│   ├── dev_set.json (60 examples)
│   └── test_set.json (68 examples)
├── results/
│   ├── dev_metrics.json           # TPR/TNR during development
│   ├── test_metrics.json          # Final TPR/TNR (run once)
│   ├── production_evaluation.json # Corrected rates + CI
│   └── confusion_matrix.png       # Visual analysis
└── judge_config.yaml              # Thresholds, model, schedule
```

---

### 15.4 HW4 Adaptation: RAG Evaluation for Evidence Retrieval

**Technique:** Evaluate retrieval separately from generation using Recall@k and MRR.

**Application to Dispute Chatbot:**

#### Evidence Retrieval Evaluation

The chatbot retrieves evidence from multiple sources (transaction DB, shipping records, customer profiles). Evaluate each retrieval path:

| Retrieval Source | Metric | Target | Rationale |
|-----------------|--------|--------|-----------|
| **Transaction History** | Recall@3 | ≥85% | Must find prior undisputed transactions for CE 3.0 |
| **Shipping Records** | Recall@1 | ≥90% | POD lookup should be exact |
| **Customer Profiles** | Recall@5 | ≥80% | Device/IP matching allows some flexibility |

#### Synthetic Query Generation (per HW4)

```python
# Two-step salient fact extraction
# Step 1: Extract key facts from dispute data
facts = extract_salient_facts(dispute_record)
# ["Transaction on 2024-10-15 for $127.50", "Shipping via FedEx #1234567890",
#  "IP address 192.168.1.1 matches 3 prior purchases"]

# Step 2: Generate natural language queries
queries = generate_queries_from_facts(facts)
# ["Find transactions from October 2024", "Show FedEx tracking proof",
#  "Check if IP address has purchase history"]
```

#### BM25 Baseline vs Enhanced Retrieval

| Retrieval Method | Recall@5 | MRR | Latency |
|-----------------|----------|-----|---------|
| **Baseline BM25** | 72% | 0.58 | 50ms |
| **BM25 + Query Rewrite** | 83% | 0.71 | 150ms |
| **Semantic (embeddings)** | 88% | 0.76 | 200ms |
| **Hybrid (BM25 + Semantic)** | 91% | 0.82 | 250ms |

**Decision:** Use Hybrid retrieval for CE 3.0 matching (high accuracy required), BM25 for general evidence lookup (speed priority).

#### MRR Calculation for Evidence Ranking

```python
# For each evidence query, record rank of correct evidence
ranks = [1, 2, 1, 5, 3, 1, 2, 1, 3, 10]  # 10 queries

mrr = sum(1/r for r in ranks) / len(ranks)
# MRR = (1 + 0.5 + 1 + 0.2 + 0.33 + 1 + 0.5 + 1 + 0.33 + 0.1) / 10
# MRR = 0.60

# Interpretation: On average, correct evidence appears around rank 1.67
```

**Artifacts:**
```
retrieval/
├── synthetic_queries/
│   ├── transaction_queries.json (100 queries)
│   ├── shipping_queries.json (100 queries)
│   └── customer_queries.json (100 queries)
├── baselines/
│   ├── bm25_results.json
│   ├── semantic_results.json
│   └── hybrid_results.json
├── metrics/
│   ├── recall_at_k.json
│   ├── mrr_by_source.json
│   └── latency_distribution.json
└── analysis/
    ├── query_type_breakdown.md    # Which query types fail?
    └── retrieval_failure_cases.md # Why did retrieval miss?
```

---

### 15.5 HW5 Adaptation: Agent Failure Analysis with Transition Matrices

**Technique:** State-based analysis to identify bottlenecks in multi-step agent pipelines.

**Application to Dispute Chatbot:**

#### State Machine States (10 States)

| State | Type | Description |
|-------|------|-------------|
| `ParseDispute` | LLM | Extract dispute details from merchant input |
| `ClassifyReason` | LLM | Determine reason code (10.4, 13.1, etc.) |
| `PlanEvidence` | LLM | Decide which specialists to invoke |
| `GatherTransaction` | Tool | Retrieve prior transaction history |
| `GatherShipping` | Tool | Retrieve shipping/POD records |
| `GatherCustomer` | Tool | Retrieve customer signals (IP, device) |
| `ValidateEvidence` | LLM | Run 3 LLM judges |
| `FormatSubmission` | Tool | Translate to VROL format |
| `SubmitNetwork` | Tool | Send to Visa API |
| `ConfirmMerchant` | System | Deliver result to merchant |

#### Failure Transition Matrix Construction

```
For each failing trace:
1. Identify last successful state
2. Identify first failing state
3. Record transition (last_success → first_failure)
4. Count frequencies
```

**Example Transition Matrix (100 Failure Traces):**

```
                    First Failure →
              Parse  Class  Plan  GatherT  GatherS  Validate  Format  Submit
Last     ┌────────────────────────────────────────────────────────────────────┐
Success  │                                                                     │
↓        │                                                                     │
Parse    │   0      3      0       0        0         0        0       0       │
Class    │   0      0      5       0        0         0        0       0       │
Plan     │   0      0      0      12        8         0        0       0       │
GatherT  │   0      0      0       0        0        15        0       0       │
GatherS  │   0      0      0       0        0        22        0       0       │  ← Bottleneck!
GatherC  │   0      0      0       0        0        18        0       0       │
Validate │   0      0      0       0        0         0        7       0       │
Format   │   0      0      0       0        0         0        0      10       │
         └────────────────────────────────────────────────────────────────────┘
```

#### Bottleneck Analysis

**Column Sum (Which State Fails Most?):**
- `ValidateEvidence`: 55 failures (55%) → **Primary bottleneck**
- `GatherTransaction`: 12 failures (12%)
- `SubmitNetwork`: 10 failures (10%)

**Row Analysis (After Which State?):**
- After `GatherShipping`: 22 failures → Shipping evidence often insufficient
- After `GatherCustomer`: 18 failures → Customer signals incomplete

**Diagnosis:**
```
Primary Issue: ValidateEvidence fails 55% of the time
  └── Root cause: Shipping evidence quality too low
      └── GatherShipping returns incomplete POD data
          └── Fix: Improve shipping API integration, add retry logic
```

#### LLM vs Tool Failure Attribution

| Transition | Count | LLM/Tool | Root Cause | Fix |
|------------|-------|----------|------------|-----|
| Plan → GatherT | 12 | LLM | Planner generates invalid query | Improve few-shot examples |
| GatherS → Validate | 22 | Tool | Shipping API returns empty | Add fallback carrier lookup |
| GatherC → Validate | 18 | Tool | Customer DB missing records | Expand data sources |
| Format → Submit | 10 | Tool | VROL format validation fails | Fix field mapping |

#### Heatmap Visualization

```python
import seaborn as sns
import matplotlib.pyplot as plt

# Create heatmap with sequential colormap
fig, ax = plt.subplots(figsize=(12, 10))
sns.heatmap(
    transition_matrix,
    annot=True,
    fmt="d",
    cmap="YlOrRd",  # Sequential: yellow (low) → red (high)
    xticklabels=states,
    yticklabels=states,
    ax=ax
)
ax.set_xlabel("First Failing State")
ax.set_ylabel("Last Successful State")
ax.set_title("Dispute Chatbot Failure Transition Matrix (n=100)")
plt.savefig("results/failure_transition_heatmap.png", dpi=150)
```

**Artifacts:**
```
agent_analysis/
├── labeled_traces.json           # 100+ traces with failure labels
├── transition_matrix.csv         # Raw count matrix
├── heatmap.png                   # Visual bottleneck identification
├── column_analysis.md            # Which states fail most
├── row_analysis.md               # After which states do failures occur
├── llm_vs_tool_attribution.md    # Root cause breakdown
└── improvement_recommendations.md # Prioritized fixes
```

---

### 15.6 Integrated Evaluation Schedule

| Frequency | Evaluation | Method | Threshold | Action on Failure |
|-----------|------------|--------|-----------|-------------------|
| **Every PR** | Unit tests | pytest | 100% pass | Block merge |
| **Every PR** | LLM Judges (blocking) | HW3 TPR/TNR | Evidence >0.8, Fabrication >0.95 | Block merge |
| **Daily CI** | Integration tests | HW5 transition analysis | <10% failure rate | Alert, don't block |
| **Daily CI** | Retrieval metrics | HW4 Recall@5 | >85% | Alert, don't block |
| **Weekly** | Judge calibration | HW3 κ vs golden set | κ >0.8 | Recalibrate judge |
| **Weekly** | Transition matrix rebuild | HW5 | N/A (informational) | Update bottleneck priorities |
| **Monthly** | Win rate vs judge prediction | HW3 bias drift | Within ±10% | Recalibrate thresholds |
| **Quarterly** | Open coding refresh | HW2 | New patterns <10% | Update failure taxonomy |

### 15.7 Evaluation Dashboard Metrics

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    EVALUATION DASHBOARD (Lessons 9-11 Style)                  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌─────────────────────┐  ┌─────────────────────┐  ┌─────────────────────┐  │
│  │  Judge Performance  │  │  Retrieval Metrics  │  │  Agent Pipeline     │  │
│  │                     │  │                     │  │                     │  │
│  │  Evidence: 0.87     │  │  Recall@1: 72%      │  │  Success Rate: 85%  │  │
│  │  Fabrication: 0.96  │  │  Recall@5: 91%      │  │  Bottleneck:        │  │
│  │  Validity: 0.82     │  │  MRR: 0.68          │  │  ValidateEvidence   │  │
│  │                     │  │                     │  │  (55% of failures)  │  │
│  │  TPR/TNR: 0.90/0.85 │  │  Latency P95: 150ms │  │                     │  │
│  └─────────────────────┘  └─────────────────────┘  └─────────────────────┘  │
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │  Win Rate Trend (Judge vs Actual)                                    │    │
│  │                                                                      │    │
│  │  100%│                                                               │    │
│  │      │        ╭──╮                                                   │    │
│  │   80%│──────╱    ╲──────── Judge Predicted (corrected)               │    │
│  │      │    ╱        ╲                                                 │    │
│  │   60%│──╱            ╲──────────── Actual Win Rate                   │    │
│  │      │                                                               │    │
│  │   40%│                                                               │    │
│  │      └──────────────────────────────────────────────────             │    │
│  │       W1    W2    W3    W4    W5    W6    W7    W8                   │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                              │
│  ⚠️ Alert: Judge predicted 85%, actual 72% (gap >10%) → Recalibrate!         │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 15.8 E2E Evaluation Workflow (CI/CD Integration)

The following diagram shows how HW1-HW5 evaluation methods integrate into the CI/CD pipeline:

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                    E2E EVALUATION WORKFLOW (HW1-HW5 in CI/CD)                            │
├─────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                          │
│  DEVELOPMENT PHASE                                                                       │
│  ════════════════                                                                        │
│                                                                                          │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐                                  │
│  │   HW1       │    │   HW2       │    │   HW3       │                                  │
│  │ System      │───▶│ Open/Axial  │───▶│ Judge       │                                  │
│  │ Prompt      │    │ Coding      │    │ Calibration │                                  │
│  │ Engineering │    │             │    │             │                                  │
│  └─────────────┘    └─────────────┘    └─────────────┘                                  │
│        │                  │                  │                                          │
│        ▼                  ▼                  ▼                                          │
│  prompts/           qualitative/       evals/phase1/                                    │
│  system_prompt.md   failure_taxonomy   golden_set/                                      │
│  query_diversity    .md                judge_prompts/                                   │
│                                                                                          │
│  ═══════════════════════════════════════════════════════════════════════════════════    │
│                                                                                          │
│  PR-LEVEL CHECKS (Every Commit)                                                          │
│  ══════════════════════════════                                                          │
│                                                                                          │
│  ┌─────────────────────────────────────────────────────────────────────────────────┐    │
│  │  git push → GitHub Actions                                                       │    │
│  │                                                                                  │    │
│  │  ┌──────────┐   ┌──────────────┐   ┌──────────────┐   ┌──────────────┐          │    │
│  │  │ pytest   │   │ HW3 Judges   │   │ HW4 Recall@k │   │ Ruff/Types   │          │    │
│  │  │ Unit     │──▶│ (Blocking)   │──▶│ (Warning)    │──▶│ Lint         │          │    │
│  │  │ Tests    │   │              │   │              │   │              │          │    │
│  │  └──────────┘   └──────────────┘   └──────────────┘   └──────────────┘          │    │
│  │       │               │                  │                  │                   │    │
│  │       ▼               ▼                  ▼                  ▼                   │    │
│  │  100% pass      Evidence >0.8      Recall@5 >85%      0 errors               │    │
│  │                 Fabrication >0.95   MRR >0.6                                    │    │
│  │                                                                                  │    │
│  │  ════════════════════════════════════════════════════════════════════════════   │    │
│  │  GATE: All checks pass → PR can merge                                           │    │
│  └─────────────────────────────────────────────────────────────────────────────────┘    │
│                                                                                          │
│  ═══════════════════════════════════════════════════════════════════════════════════    │
│                                                                                          │
│  DAILY CI (Scheduled - 2:00 AM UTC)                                                      │
│  ══════════════════════════════════                                                      │
│                                                                                          │
│  ┌─────────────────────────────────────────────────────────────────────────────────┐    │
│  │                                                                                  │    │
│  │  ┌──────────────┐   ┌──────────────┐   ┌──────────────┐                         │    │
│  │  │ HW5          │   │ HW4          │   │ Integration  │                         │    │
│  │  │ Transition   │   │ Retrieval    │   │ Tests        │                         │    │
│  │  │ Matrix       │   │ Benchmark    │   │ (E2E)        │                         │    │
│  │  └──────────────┘   └──────────────┘   └──────────────┘                         │    │
│  │        │                  │                  │                                   │    │
│  │        ▼                  ▼                  ▼                                   │    │
│  │  Rebuild matrix     Run 300 queries    10 dispute flows                         │    │
│  │  from last 24h      across 3 sources   end-to-end                               │    │
│  │  traces                                                                          │    │
│  │                                                                                  │    │
│  │  Output: agent_analysis/transition_matrix.csv                                   │    │
│  │          retrieval/metrics/daily_recall.json                                    │    │
│  │          Slack alert if failure_rate >10%                                       │    │
│  │                                                                                  │    │
│  └─────────────────────────────────────────────────────────────────────────────────┘    │
│                                                                                          │
│  ═══════════════════════════════════════════════════════════════════════════════════    │
│                                                                                          │
│  WEEKLY CALIBRATION (Scheduled - Sunday 6:00 AM UTC)                                     │
│  ═══════════════════════════════════════════════════                                     │
│                                                                                          │
│  ┌─────────────────────────────────────────────────────────────────────────────────┐    │
│  │                                                                                  │    │
│  │  ┌──────────────────────────────────────────────────────────────────────────┐   │    │
│  │  │  HW3 Judge Recalibration Pipeline                                        │   │    │
│  │  │                                                                          │   │    │
│  │  │  1. Sample 50 new traces from production                                 │   │    │
│  │  │  2. Human label (via Label Studio)                                       │   │    │
│  │  │  3. Calculate κ (Cohen's Kappa) vs existing golden set                   │   │    │
│  │  │  4. If κ <0.8 → Flag for judge prompt revision                          │   │    │
│  │  │  5. Update TPR/TNR estimates                                             │   │    │
│  │  │  6. Recalculate bias correction coefficients                             │   │    │
│  │  │                                                                          │   │    │
│  │  └──────────────────────────────────────────────────────────────────────────┘   │    │
│  │                                                                                  │    │
│  │  Output: evals/phase1/results/weekly_calibration_YYYYMMDD.json                  │    │
│  │          JIRA ticket if κ drift detected                                        │    │
│  │                                                                                  │    │
│  └─────────────────────────────────────────────────────────────────────────────────┘    │
│                                                                                          │
│  ═══════════════════════════════════════════════════════════════════════════════════    │
│                                                                                          │
│  MONTHLY WIN RATE VALIDATION                                                             │
│  ═══════════════════════════                                                             │
│                                                                                          │
│  ┌─────────────────────────────────────────────────────────────────────────────────┐    │
│  │                                                                                  │    │
│  │  ┌────────────────┐         ┌────────────────┐         ┌────────────────┐       │    │
│  │  │ Judge          │         │ Network        │         │ Bias           │       │    │
│  │  │ Predictions    │────────▶│ Outcomes       │────────▶│ Recalibration  │       │    │
│  │  │ (corrected)    │ Compare │ (actual wins)  │         │                │       │    │
│  │  └────────────────┘         └────────────────┘         └────────────────┘       │    │
│  │                                                                                  │    │
│  │  If |predicted - actual| >10%:                                                  │    │
│  │    → Recalibrate thresholds                                                     │    │
│  │    → Review judge prompts                                                       │    │
│  │    → Update bias correction formula                                             │    │
│  │                                                                                  │    │
│  └─────────────────────────────────────────────────────────────────────────────────┘    │
│                                                                                          │
│  ═══════════════════════════════════════════════════════════════════════════════════    │
│                                                                                          │
│  QUARTERLY TAXONOMY REFRESH (HW2)                                                        │
│  ════════════════════════════════                                                        │
│                                                                                          │
│  ┌─────────────────────────────────────────────────────────────────────────────────┐    │
│  │                                                                                  │    │
│  │  1. Sample 100 traces from past 3 months (stratified by reason code)            │    │
│  │  2. Re-run open coding (blind to existing taxonomy)                             │    │
│  │  3. Count new failure patterns discovered                                       │    │
│  │  4. If new patterns >10%:                                                       │    │
│  │     → Update failure_taxonomy.md                                                │    │
│  │     → Create new judge dimensions if needed                                     │    │
│  │     → Expand golden set with new failure types                                  │    │
│  │                                                                                  │    │
│  └─────────────────────────────────────────────────────────────────────────────────┘    │
│                                                                                          │
└─────────────────────────────────────────────────────────────────────────────────────────┘

Legend:
  ───▶  Sequential dependency
  HW1   Prompt Engineering (prompts/, query diversity)
  HW2   Open/Axial Coding (qualitative/, failure taxonomy)
  HW3   LLM-as-Judge (evals/, golden set, bias correction)
  HW4   RAG Evaluation (retrieval/, Recall@k, MRR)
  HW5   Agent Pipeline (agent_analysis/, transition matrices)
```

**GitHub Actions Workflow Reference:**

```yaml
# .github/workflows/dispute-eval.yml
name: Dispute Chatbot Evaluation

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]
  schedule:
    - cron: '0 2 * * *'    # Daily at 2:00 AM UTC
    - cron: '0 6 * * 0'    # Weekly Sunday at 6:00 AM UTC

jobs:
  pr-checks:
    if: github.event_name == 'pull_request'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Run Unit Tests
        run: pytest tests/ -v --cov=src --cov-fail-under=90
      - name: Run LLM Judges (HW3)
        run: python evals/run_judges.py --blocking
      - name: Run Retrieval Benchmark (HW4)
        run: python retrieval/benchmark.py --warn-only

  daily-analysis:
    if: github.event.schedule == '0 2 * * *'
    runs-on: ubuntu-latest
    steps:
      - name: Rebuild Transition Matrix (HW5)
        run: python agent_analysis/build_matrix.py --last-24h
      - name: Run Retrieval Benchmark (HW4)
        run: python retrieval/benchmark.py --full
      - name: Alert on Regression
        run: python scripts/check_regression.py

  weekly-calibration:
    if: github.event.schedule == '0 6 * * 0'
    runs-on: ubuntu-latest
    steps:
      - name: Judge Calibration (HW3)
        run: python evals/calibrate_judges.py --sample=50
```

---

## 16. Open Questions

| # | Question | Status | Decision |
|---|----------|--------|----------|
| Q1 | Network scope for Phase 1 | Resolved | Visa only |
| Q2 | Priority dispute types | Resolved | Fraud (10.4) + PNR (13.1) |
| Q3 | Integration strategy | Resolved | Standalone with REST API |
| Q4 | Human escalation workflow | Open | TBD based on pilot feedback |
| Q5 | Multi-language support | Deferred | English only for v1 |
| Q6 | Evaluation methodology integration | Resolved | HW1-HW5 methods adapted (Section 15) |

---

## Appendix A: Key File References

- [deep_dive_real_world_cases.md](../lesson-18/dispute-schema/explanation/deep_dive_real_world_cases.md) - Domain context, $60B problem
- [mvp-agentic-chatbot-synthesized-plan.v3.md](../lesson-18/dispute-schema/plan/mvp-agentic-chatbot-synthesized-plan.v3.md) - Existing MVP plan (bank analyst focus)
- [02_orchestration_patterns_overview.md](../lesson-16/tutorials/02_orchestration_patterns_overview.md) - Pattern decision tree
- [01_explainability_fundamentals.md](../lesson-17/tutorials/01_explainability_fundamentals.md) - 4 pillars framework
- [EVALUATION_METHODOLOGY_RESEARCH_REPORT.md](../homeworks/EVALUATION_METHODOLOGY_RESEARCH_REPORT.md) - Full HW1-HW5 methodology documentation

---

## Appendix B: Dispute Reason Code Reference

| Scenario | Visa | Mastercard | Phase 1? |
|----------|------|------------|----------|
| Fraud (CNP) | 10.4 | 4837 | Yes |
| Product Not Received | 13.1 | 4855 | Yes |
| Subscription Canceled | 13.2 | 4841 | Phase 2 |
| Duplicate | 12.6.1 | 4834 | Phase 2 |
| Credit Not Processed | 13.6 | 4853 | Phase 2 |

---

**Document End**

