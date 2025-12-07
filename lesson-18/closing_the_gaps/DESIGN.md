# Closing the Gaps: High-Level Design Document

## Evaluation & Explainability Framework for Multi-Agent Bank Dispute Systems

**Version:** 1.0
**Created:** December 2024
**Methodology:** Pólya's Problem-Solving Framework + First Principles Teaching
**Status:** Design Phase

---

## Executive Summary

This design creates an **evaluation and explainability framework** for multi-agent bank dispute systems that addresses the 10 critical gaps identified in the research document. The system leverages:

- **Pólya's 5-phase methodology** (Understand → Plan → Tasks → Execute → Reflect)
- **Existing patterns** (ABC, TDD, First Principles Teaching)
- **Lesson-17 explainability components** (BlackBoxRecorder, AgentFacts, GuardRails, PhaseLogger)

---

## 1. Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                      CLOSING THE GAPS SYSTEM ARCHITECTURE                   │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌────────────────────────────────────────────────────────────────────┐    │
│  │                    LAYER 1: EVALUATION FRAMEWORK                    │    │
│  │  (Addresses Gaps 1, 4, 7)                                          │    │
│  │                                                                     │    │
│  │  ┌─────────────┐  ┌─────────────────┐  ┌───────────────────────┐  │    │
│  │  │ BaseEval    │  │ NonDeterminism  │  │ Architecture          │  │    │
│  │  │ (ABC)       │──│ Evaluator       │──│ Justification         │  │    │
│  │  └─────────────┘  └─────────────────┘  └───────────────────────┘  │    │
│  │         │                                        │                 │    │
│  │         └────────────────────┬───────────────────┘                 │    │
│  │                              │                                     │    │
│  │                   ┌──────────┴──────────┐                          │    │
│  │                   │ Statistical Testing │                          │    │
│  │                   │ Framework           │                          │    │
│  │                   └─────────────────────┘                          │    │
│  └────────────────────────────────────────────────────────────────────┘    │
│                                                                             │
│  ┌────────────────────────────────────────────────────────────────────┐    │
│  │                    LAYER 2: EXPLAINABILITY LAYER                    │    │
│  │  (Addresses Gaps 6, 8, 9)                                          │    │
│  │                                                                     │    │
│  │  ┌─────────────┐  ┌─────────────────┐  ┌───────────────────────┐  │    │
│  │  │ BlackBox    │  │ PhaseLogger     │  │ GuardRailValidator    │  │    │
│  │  │ Recorder    │──│ (Pólya phases)  │──│ (Security + PII)      │  │    │
│  │  └─────────────┘  └─────────────────┘  └───────────────────────┘  │    │
│  │         │                 │                      │                 │    │
│  │         └─────────────────┼──────────────────────┘                 │    │
│  │                           │                                        │    │
│  │                ┌──────────┴──────────┐                             │    │
│  │                │ Observability Hub   │                             │    │
│  │                │ (Gap 8)             │                             │    │
│  │                └─────────────────────┘                             │    │
│  └────────────────────────────────────────────────────────────────────┘    │
│                                                                             │
│  ┌────────────────────────────────────────────────────────────────────┐    │
│  │                    LAYER 3: GOVERNANCE & OVERSIGHT                  │    │
│  │  (Addresses Gaps 2, 3, 5, 10)                                      │    │
│  │                                                                     │    │
│  │  ┌─────────────┐  ┌─────────────────┐  ┌───────────────────────┐  │    │
│  │  │ AgentFacts  │  │ PolicyBridge    │  │ Human-in-Loop         │  │    │
│  │  │ Registry    │──│ (Regulatory)    │──│ Controller            │  │    │
│  │  └─────────────┘  └─────────────────┘  └───────────────────────┘  │    │
│  │         │                 │                      │                 │    │
│  │         └─────────────────┼──────────────────────┘                 │    │
│  │                           │                                        │    │
│  │                ┌──────────┴──────────┐                             │    │
│  │                │ Anti-Pattern        │                             │    │
│  │                │ Detector (Gap 10)   │                             │    │
│  │                └─────────────────────┘                             │    │
│  └────────────────────────────────────────────────────────────────────┘    │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Gap-to-Component Mapping

| Gap | Problem | Solution Component | Pattern Used |
|-----|---------|-------------------|--------------|
| **Gap 1**: Architecture Justification | No proof multi-agent is needed | `ArchitectureJustifier` | Pólya's UNDERSTAND phase |
| **Gap 2**: Prerequisites | Missing LangGraph/MCP explanations | First Principles tutorials | First Principles Teaching |
| **Gap 3**: Failure Root Cause | Unknown why agents fail | `FailureTaxonomyAnalyzer` | MAST taxonomy + PhaseLogger |
| **Gap 4**: Trade-offs | Hidden fundamental limits | `TradeoffAnalyzer` | Statistical evaluation |
| **Gap 5**: Economics | No cost visibility | `CostTracker` | Token economics integration |
| **Gap 6**: Human-in-Loop | Regulatory requirement | `HITLController` | Tiered oversight model |
| **Gap 7**: Non-Deterministic Testing | LLM output variance | `StatisticalEvaluator` | ABC + DeepEval integration |
| **Gap 8**: Observability | Beyond traditional APM | `ObservabilityHub` | BlackBox + PhaseLogger |
| **Gap 9**: Security | Prompt injection threats | `PromptSecurityGuard` | GuardRails + PolicyBridge |
| **Gap 10**: Anti-Patterns | Common failure modes | `AntiPatternDetector` | Pattern matching + alerts |

---

## 3. Core Components Design

### 3.1 Evaluation Framework (ABC Pattern)

```python
from abc import ABC, abstractmethod
from typing import Any, Dict, List
from pydantic import BaseModel

class EvaluationResult(BaseModel):
    """Pydantic model for evaluation results."""
    evaluator_name: str
    is_valid: bool
    score: float  # 0.0 - 1.0
    confidence: float  # Statistical confidence
    samples_evaluated: int
    reasoning: str
    recommendations: list[str]

class BaseEvaluator(ABC):
    """Abstract base class for all gap evaluators.

    Applies ABC pattern from patterns/abstract-base-class.md
    with defensive initialization.
    """

    def __init__(self, config: dict[str, Any]):
        # Defensive validation (per TDD principles)
        if not isinstance(config, dict):
            raise TypeError("config must be a dictionary")

        required = ["name", "min_samples", "confidence_threshold"]
        missing = [k for k in required if k not in config]
        if missing:
            raise ValueError(f"Missing required config: {missing}")

        self.name = config["name"]
        self.min_samples = config["min_samples"]
        self.confidence_threshold = config["confidence_threshold"]

    @abstractmethod
    def evaluate(self, data: dict[str, Any]) -> EvaluationResult:
        """Run evaluation. Subclasses must implement."""
        pass

    @abstractmethod
    def explain(self, result: EvaluationResult) -> str:
        """Provide human-readable explanation. Required for explainability."""
        pass
```

### 3.2 Non-Determinism Evaluator (Gap 7)

**Design Decision**: Use **statistical testing** instead of exact matching, per research recommendation.

```python
class NonDeterminismEvaluator(BaseEvaluator):
    """Evaluates non-deterministic LLM outputs using statistical methods.

    Implements Gap 7 solution: Statistical testing for non-determinism.
    """

    def __init__(self, config: dict[str, Any]):
        super().__init__(config)
        self.runs_per_sample = config.get("runs_per_sample", 5)
        self.semantic_similarity_threshold = config.get("similarity_threshold", 0.85)

    def evaluate(self, data: dict[str, Any]) -> EvaluationResult:
        """
        Evaluate using:
        1. Multiple runs (5x minimum per sample)
        2. Semantic equivalence (embedding similarity)
        3. Property-based testing (assert properties, not strings)
        4. Statistical tolerance bands (95% pass rate)
        """
        # Implementation leverages ThreadPoolExecutor pattern
        # for parallel LLM calls
        pass

    def explain(self, result: EvaluationResult) -> str:
        """Generate First Principles explanation of variance."""
        # Uses First Principles Teaching pattern
        pass
```

### 3.3 Explainability Integration with Pólya Phases

**Design Decision**: Map Pólya's 5 phases to PhaseLogger workflow states.

```python
from lesson_17.backend.explainability import PhaseLogger, WorkflowPhase

class PolyaPhaseMapper:
    """Maps Pólya's methodology to PhaseLogger phases."""

    POLYA_TO_WORKFLOW = {
        "UNDERSTAND": WorkflowPhase.PLANNING,
        "PLAN": WorkflowPhase.PLANNING,
        "TASKS": WorkflowPhase.EXECUTION,
        "EXECUTE": WorkflowPhase.EXECUTION,
        "REFLECT": WorkflowPhase.VALIDATION,
    }

    def __init__(self, logger: PhaseLogger):
        self.logger = logger
        self.current_polya_phase = "UNDERSTAND"

    def transition_phase(self, new_phase: str, reasoning: str) -> None:
        """Transition with full audit trail per Gap 8."""
        self.logger.log_decision(
            decision_id=f"polya-{new_phase}",
            reasoning=reasoning,
            alternatives_considered=self._get_alternatives(new_phase),
            selected_option=new_phase,
        )
```

### 3.4 Human-in-the-Loop Controller (Gap 6)

**Design Decision**: Implement Sardine AI's **tiered oversight model** per regulatory requirements.

```python
from enum import Enum

class OversightTier(str, Enum):
    """Per Sardine AI's production-tested framework."""
    TIER_1_HIGH = "tier_1"      # SAR filing, payment blocking → Full HITL
    TIER_2_MEDIUM = "tier_2"    # Fraud triage, KYC → Sample-based review
    TIER_3_LOW = "tier_3"       # Knowledge search → Logged only

class HITLController:
    """Human-in-the-Loop Controller per Gap 6.

    Regulatory Requirements:
    - Federal Reserve SR 11-7: Evaluation, monitoring, outcomes analysis
    - EU AI Act Article 14: Four oversight models
    """

    def __init__(self, default_tier: OversightTier = OversightTier.TIER_2_MEDIUM):
        self.default_tier = default_tier
        self.interrupts_enabled = True

    def should_interrupt(
        self,
        confidence: float,
        amount: float,
        dispute_type: str
    ) -> tuple[bool, str]:
        """
        Determine if human review is needed.

        Returns:
            (should_interrupt, reason)
        """
        # Tier 1 always requires human
        if self._classify_tier(dispute_type) == OversightTier.TIER_1_HIGH:
            return True, "Tier 1 action requires human approval"

        # Low confidence or high value
        if confidence < 0.85:
            return True, f"Confidence {confidence:.2f} below threshold"
        if amount > 10000:
            return True, f"Amount ${amount:,.2f} exceeds HITL threshold"

        return False, "Automated processing allowed"
```

### 3.5 Security Guard (Gap 9)

**Design Decision**: Leverage GuardRails with **prompt injection detection** per OWASP LLM Top 10.

```python
class PromptSecurityGuard:
    """Defense against prompt injection attacks per Gap 9.

    Implements:
    - Chain-of-Agents Pipeline (Domain LLM → Guard Agent)
    - LLM Tagging (source: system, user, external, agent)
    - Input sanitization
    """

    INJECTION_PATTERNS = [
        r"ignore\s+previous\s+instructions",
        r"disregard\s+(all\s+)?prior",
        r"new\s+instructions\s*:",
        r"you\s+are\s+now\s+",
        r"act\s+as\s+if\s+",
    ]

    def __init__(self):
        self.validator = GuardRailValidator()
        self.guardrail = self._create_security_guardrail()

    def scan_input(self, user_input: str) -> tuple[bool, str]:
        """Scan for injection attacks before processing."""
        result = self.validator.validate(
            {"output": user_input},
            self.guardrail
        )
        return result.is_valid, result.entries[0].message if result.entries else ""
```

---

## 4. Data Flow (Following First Principles Pattern)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        DISPUTE PROCESSING FLOW                              │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  STEP 1: UNDERSTAND (Pólya Phase 1)                                        │
│  ├── PromptSecurityGuard.scan_input(dispute_data)                          │
│  ├── ArchitectureJustifier.is_multi_agent_needed()                         │
│  └── PhaseLogger.log_phase("PLANNING", "Understanding dispute")            │
│                         │                                                   │
│                         ▼                                                   │
│  STEP 2: PLAN (Pólya Phase 2)                                              │
│  ├── Select architecture: single_agent | multi_agent (Gap 1 decision)      │
│  ├── TradeoffAnalyzer.compute_cost_benefit()                               │
│  └── BlackBoxRecorder.record_task_plan(plan)                               │
│                         │                                                   │
│                         ▼                                                   │
│  STEP 3: EXECUTE (Pólya Phase 3)                                           │
│  ├── For each agent step:                                                  │
│  │   ├── BlackBoxRecorder.record_step_start()                              │
│  │   ├── GuardRailValidator.validate(output)                               │
│  │   ├── NonDeterminismEvaluator.evaluate() # Statistical testing          │
│  │   └── HITLController.should_interrupt() # Check oversight tier          │
│  └── ObservabilityHub.track_metrics() # Per-agent latency, tokens, etc.    │
│                         │                                                   │
│                         ▼                                                   │
│  STEP 4: REFLECT (Pólya Phase 4)                                           │
│  ├── AntiPatternDetector.check_for_patterns()                              │
│  ├── FailureTaxonomyAnalyzer.classify_failures() # MAST taxonomy           │
│  ├── CostTracker.generate_report()                                         │
│  └── PhaseLogger.complete_workflow()                                       │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 5. Key Design Decisions

### Decision 1: 3-Agent vs 7-Agent Architecture

**Problem**: Research shows 7 agents create 49 communication paths (O(n²)).

**Decision**: Default to **3-agent architecture** per research recommendation:
1. **Research/Analysis Agent** (read-heavy, parallelizable)
2. **Compliance Agent** (regulatory expertise)
3. **Resolution Agent** (single point of accountability)

**Rationale**:
- 2 handoff points instead of 6 (-67%)
- ~400ms latency reduction
- Clear accountability per agent
- Easier debugging and audit

### Decision 2: Statistical vs Exact Testing

**Problem**: LLMs show up to 15% variance even at temperature=0.

**Decision**: Implement **statistical testing framework**:
- 5x minimum runs per test case
- Semantic equivalence (embedding similarity > 0.85)
- Property-based assertions
- 95% tolerance bands

**Rationale**: Exact matching is fundamentally incompatible with LLM behavior.

### Decision 3: Verification Ground Truth

**Problem**: "Who verifies the verifier?" paradox.

**Decision**: Verify against **non-LLM ground truth** only:

| Verification Type | Ground Truth Source | Reliable? |
|-------------------|---------------------|-----------|
| Schema Validation | JSON Schema spec | ✅ Deterministic |
| Database Lookup | "Does dispute exist?" | ✅ Ground truth |
| Regulatory Rules | Pre-compiled calculator | ✅ Deterministic |
| External APIs | Carrier tracking | ✅ External ground truth |
| LLM checking LLM | Another model's opinion | ❌ Same hallucination risk |

### Decision 4: Observability Metrics

**Problem**: Traditional APM doesn't capture LLM-specific metrics.

**Decision**: Track **agent-specific metrics** per Gap 8:

**Per-Agent Metrics:**
- Latency (p50, p95, p99)
- Error rate
- Confidence distribution
- Token usage and cost
- Hallucination rate

**System-Wide Metrics:**
- End-to-end latency
- Escalation rate
- Verification rejection rate
- Agent disagreement rate

**Debugging Metrics:**
- Correlation ID propagation
- Handoff success/failure by agent pair
- Context loss measurement across hops

### Decision 5: Security-First Architecture

**Problem**: Prompt infection can propagate across agents like a virus.

**Decision**: Implement **defense-in-depth**:
1. **Input Layer**: PromptSecurityGuard scans all user input
2. **Agent Layer**: Each agent output scanned before handoff
3. **Output Layer**: Final response sanitized
4. **Audit Layer**: All security events logged to BlackBox

---

## 6. Integration Points

| Existing Component | Integration Strategy |
|-------------------|---------------------|
| `BlackBoxRecorder` | Use for STEP_START, STEP_END, DECISION events |
| `AgentFacts` | Register all agents with capabilities and policies |
| `GuardRails` | Add prompt injection detection constraints |
| `PhaseLogger` | Map Pólya phases to workflow phases |
| `PolicyBridge` | Connect regulatory policies to runtime enforcement |

---

## 7. Implementation Priority Matrix

| Priority | Gap | Component | Complexity | Rationale |
|----------|-----|-----------|------------|-----------|
| **P0** | Gap 9 | `PromptSecurityGuard` | Medium | Security is foundational |
| **P0** | Gap 6 | `HITLController` | Low | Regulatory requirement |
| **P1** | Gap 7 | `StatisticalEvaluator` | High | Core evaluation capability |
| **P1** | Gap 1 | `ArchitectureJustifier` | Medium | Prevents over-engineering |
| **P1** | Gap 4 | `TradeoffAnalyzer` | Low | Documents limits |
| **P2** | Gap 8 | `ObservabilityHub` | Medium | Enables debugging |
| **P2** | Gap 3 | `FailureTaxonomyAnalyzer` | High | MAST taxonomy implementation |
| **P3** | Gap 5 | `CostTracker` | Low | Economics visibility |
| **P3** | Gap 10 | `AntiPatternDetector` | Low | Pattern matching |

---

## 8. Proposed File Structure

```
closing_the_gaps/
├── __init__.py
├── DESIGN.md                      # This document
├── evaluation/
│   ├── __init__.py
│   ├── base_evaluator.py          # ABC pattern
│   ├── statistical_evaluator.py   # Gap 7
│   ├── architecture_justifier.py  # Gap 1
│   ├── tradeoff_analyzer.py       # Gap 4
│   └── failure_taxonomy.py        # Gap 3 (MAST)
├── explainability/
│   ├── __init__.py
│   ├── polya_mapper.py            # Pólya → PhaseLogger
│   ├── observability_hub.py       # Gap 8
│   └── cost_tracker.py            # Gap 5
├── governance/
│   ├── __init__.py
│   ├── hitl_controller.py         # Gap 6
│   ├── prompt_security.py         # Gap 9
│   └── anti_pattern_detector.py   # Gap 10
├── tests/
│   ├── __init__.py
│   ├── test_base_evaluator.py     # TDD tests
│   ├── test_hitl_controller.py
│   ├── test_prompt_security.py
│   ├── test_statistical_eval.py
│   └── conftest.py
└── tutorials/
    ├── TUTORIAL_INDEX.md
    ├── 01_evaluation_fundamentals.md    # First Principles
    ├── 02_non_determinism_testing.md
    ├── 03_hitl_implementation.md
    └── 04_security_guardrails.md
```

---

## 9. Testing Strategy

### TDD Approach (per CLAUDE.md principles)

1. **RED**: Write failing test first
2. **GREEN**: Minimal code to pass
3. **REFACTOR**: Improve with tests green

### Test Categories

| Category | Approach | Example |
|----------|----------|---------|
| **Unit Tests** | Property-based | "Output must contain dispute_id" |
| **Statistical Tests** | 5x runs, tolerance bands | 95% of runs must pass |
| **Integration Tests** | End-to-end flow | Dispute → Resolution with audit trail |
| **Chaos Tests** | Failure injection | Kill agent, verify graceful degradation |

### Test Naming Convention

```python
def test_should_detect_injection_when_ignore_previous_pattern():
    """Test that 'ignore previous instructions' triggers security alert."""
    pass

def test_should_interrupt_when_confidence_below_threshold():
    """Test HITL triggers on low confidence scores."""
    pass
```

---

## 10. References

### Source Documents
- `closing_the_gaps_first_principles.md` - Research synthesis (10 gaps)
- `ai-dev-tasks/polya-analysis.md` - Pólya methodology mapping

### Patterns Used
- `patterns/abstract-base-class.md` - ABC for evaluators
- `patterns/first-principles-teaching.md` - Tutorial structure
- `patterns/tdd-workflow.md` - Testing approach
- `patterns/threadpool-parallel.md` - Concurrent evaluation

### Lesson-17 Components
- `backend/explainability/black_box.py` - BlackBoxRecorder
- `backend/explainability/guardrails.py` - GuardRailValidator
- `backend/explainability/phase_logger.py` - PhaseLogger
- `backend/explainability/agent_facts.py` - AgentFacts
- `backend/explainability/policy_bridge.py` - PolicyBridge

---

## 11. Open Questions for Implementation

1. **DeepEval Integration**: Should we use DeepEval's `TaskCompletionMetric` directly or wrap it?

2. **Embedding Model**: Which embedding model for semantic similarity? (Options: OpenAI ada-002, sentence-transformers)

3. **Persistence**: Where to store evaluation results and audit trails? (Options: SQLite, PostgreSQL, file-based JSON)

4. **Real-time vs Batch**: Should evaluation run inline or as background job?

5. **Alert Thresholds**: What are the specific thresholds for each tier in HITL?

---

*Document Version: 1.0*
*Created: December 2024*
*Type: High-Level Design Document*
*Methodology: Pólya's Framework + First Principles Teaching Pattern*
