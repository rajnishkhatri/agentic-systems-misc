# PRD: Lesson 17 - Agent Explainability Framework Tutorials (MVP)

**Document Version:** 1.0  
**Created:** 2025-11-27  
**Status:** Draft  
**Source:** lesson-17/NEXT_PHASE_TODO.md  

---

## 1. Introduction/Overview

### Problem Statement

Lesson 17's Agent Explainability Framework has a **complete technical implementation** (2,689 lines of production code, 94 passing tests) but a **critical tutorial content gap**. The `tutorials/` directory is empty, meaning enterprise developers cannot learn when, why, or how to use the framework effectively.

### Current State

| Aspect | Status |
|--------|--------|
| Production Code | ✅ Complete (4 components, 2,689 lines) |
| Test Coverage | ✅ 94/94 tests passing (100%) |
| Interactive Notebooks | ⚠️ 3/4 complete (Phase Logger missing) |
| Concept Tutorials | ❌ 0/7 (tutorials/ directory empty) |

### Solution

Create MVP tutorial content consisting of:
- **4 core concept tutorials** covering each framework component
- **1 interactive notebook** for the missing Phase Logger component
- **Decision tree** for component selection guidance

### Target Audience

**Primary:** Enterprise development teams who need:
- Compliance audit trails (HIPAA, SOX, GDPR)
- Multi-agent governance and cost attribution
- Post-incident debugging and root cause analysis
- Output validation and PII detection

**Secondary:** Junior-to-intermediate developers learning AI agent observability patterns.

---

## 2. Goals

### Primary Goals

| Goal ID | Description | Success Metric |
|---------|-------------|----------------|
| G1 | Enable developers to understand explainability fundamentals | Tutorial 1 published, <25 min reading time |
| G2 | Teach BlackBox recording for post-incident debugging | Tutorial 2 published with case study |
| G3 | Demonstrate AgentFacts for enterprise governance | Tutorial 3 published with HIPAA example |
| G4 | Enable PII detection and output validation | Tutorial 4 published with all 7 validators |
| G5 | Complete 4/4 interactive notebook demos | Phase Logger notebook functional |

### Success Criteria

- All 4 tutorials pass quality gates (code tested, diagrams render, <30 min read time)
- Phase Logger notebook executes without errors in <5 minutes
- TUTORIAL_INDEX.md updated with learning paths
- All cross-links between tutorials verified

---

## 3. User Stories

### Enterprise Compliance Team

**US-1:** As a **compliance officer**, I want to understand which explainability component provides audit trails, so that I can ensure our AI agents meet HIPAA/SOX requirements.

**US-2:** As a **compliance officer**, I want to export agent activity logs in a compliance-ready format, so that I can provide evidence during regulatory audits.

### DevOps/SRE Team

**US-3:** As a **DevOps engineer**, I want to replay agent execution traces after failures, so that I can identify root causes of cascade failures in multi-agent workflows.

**US-4:** As a **DevOps engineer**, I want to track parameter changes across agent executions, so that I can correlate configuration drift with incident timelines.

### Development Team

**US-5:** As a **developer**, I want to validate agent outputs for PII before they reach users, so that I can prevent data leakage and maintain user privacy.

**US-6:** As a **developer**, I want a decision tree to choose the right explainability component, so that I don't over-engineer simple observability requirements.

---

## 4. Functional Requirements

### 4.1 Tutorial 1 - Explainability Fundamentals

**File:** `lesson-17/tutorials/01_explainability_fundamentals.md`

| Req ID | Requirement | Priority |
|--------|-------------|----------|
| T1-01 | Define AI agent explainability and differentiate from model interpretability (LIME, SHAP) | Must |
| T1-02 | Explain the four pillars: Recording, Identity, Validation, Reasoning | Must |
| T1-03 | Map each pillar to a framework component (BlackBox, AgentFacts, GuardRails, PhaseLogger) | Must |
| T1-04 | Include decision tree diagram (Mermaid) for component selection | Must |
| T1-05 | Provide 3+ real-world scenarios (Healthcare, Finance, Legal) | Must |
| T1-06 | Cross-link to Tutorials 2-4 for deep-dives | Must |
| T1-07 | Reading time must be <25 minutes | Must |

### 4.2 Tutorial 2 - BlackBox Recording for Debugging

**File:** `lesson-17/tutorials/02_black_box_recording_debugging.md`

| Req ID | Requirement | Priority |
|--------|-------------|----------|
| T2-01 | Explain aviation black box analogy and parallels to multi-agent systems | Must |
| T2-02 | Document all recordable data types: TaskPlan, AgentInfo, ParameterSubstitution, ExecutionTrace | Must |
| T2-03 | Explain all 8 event types: STEP_START, STEP_END, DECISION, ERROR, CHECKPOINT, PARAMETER_CHANGE, COLLABORATOR_JOIN, COLLABORATOR_LEAVE, ROLLBACK | Must |
| T2-04 | Provide post-incident analysis workflow (export → replay → analyze) | Must |
| T2-05 | Include case study: Multi-agent invoice processing failure with timeline diagram | Must |
| T2-06 | Document best practices: checkpoints, rollback points, storage management | Must |
| T2-07 | Show integration with GuardRails (validation + recording) | Should |
| T2-08 | Cross-link to notebook `01_black_box_recording_demo.ipynb` | Must |

### 4.3 Tutorial 3 - AgentFacts for Governance

**File:** `lesson-17/tutorials/03_agentfacts_governance.md`

| Req ID | Requirement | Priority |
|--------|-------------|----------|
| T3-01 | Explain why agent identity matters: multi-tenancy, compliance, cost attribution, model lineage | Must |
| T3-02 | Document Capability declarations: input/output schemas, cost estimation, latency SLAs | Must |
| T3-03 | Document Policy management: rate limits, approval requirements, time-based policies, data access controls | Must |
| T3-04 | Explain signature verification (SHA256) for tamper detection | Must |
| T3-05 | Include signature verification flow diagram (Mermaid) | Must |
| T3-06 | Document audit trail export for compliance (HIPAA/SOX format) | Must |
| T3-07 | Include case study: Healthcare agent governance with HIPAA compliance | Must |
| T3-08 | Cross-link to notebook `02_agent_facts_verification.ipynb` | Must |

### 4.4 Tutorial 4 - GuardRails for Validation & PII Detection

**File:** `lesson-17/tutorials/04_guardrails_validation_pii.md`

| Req ID | Requirement | Priority |
|--------|-------------|----------|
| T4-01 | Explain declarative validation philosophy (vs. imperative) | Must |
| T4-02 | Document all 7 built-in validators: length, regex, PII, confidence, required fields, JSON, value lists | Must |
| T4-03 | Provide code examples for each built-in validator | Must |
| T4-04 | Explain custom validator creation with domain-specific example | Must |
| T4-05 | Document all 5 failure actions: REJECT, FIX, ESCALATE, LOG, RETRY | Must |
| T4-06 | Include failure action decision matrix table | Must |
| T4-07 | Explain validation traces for debugging | Must |
| T4-08 | Include case study: PII redaction in customer service chatbot | Must |
| T4-09 | Test all PII patterns: SSN, credit card, email, phone | Must |
| T4-10 | Cross-link to notebook `03_guardrails_validation_traces.ipynb` | Must |

### 4.5 Phase Logger Notebook

**File:** `lesson-17/notebooks/04_phase_logger_workflow.ipynb`

| Req ID | Requirement | Priority |
|--------|-------------|----------|
| N1-01 | Setup cell with imports and PhaseLogger initialization | Must |
| N1-02 | Demonstrate phase lifecycle: start → log → add artifact → end | Must |
| N1-03 | Show at least 4 of 9 workflow phases (PLANNING, LITERATURE_REVIEW, EXPERIMENT, REPORTING) | Must |
| N1-04 | Demonstrate decision logging with alternatives and rationale | Must |
| N1-05 | Demonstrate artifact tracking with metadata | Must |
| N1-06 | Show error handling: recoverable and fatal errors | Must |
| N1-07 | Generate Mermaid workflow diagram | Must |
| N1-08 | Display summary statistics (phases, decisions, artifacts, errors) | Must |
| N1-09 | Total execution time must be <5 minutes | Must |
| N1-10 | Include markdown explanations between code cells | Must |

---

## 5. Non-Goals (Out of Scope for MVP)

The following items are explicitly **NOT included** in this MVP phase:

| Item | Reason | Future Phase |
|------|--------|--------------|
| Tutorial 5: Phase Logging for Multi-Stage Workflows | P1 priority, depends on MVP completion | Phase 2 |
| Tutorial 6: Combining Components for Full Observability | P1 priority, requires all component tutorials | Phase 2 |
| Tutorial 7: Integration with Lesson 16 Reliability Framework | P1 priority, cross-lesson dependency | Phase 2 |
| Decision Tree / Cheat Sheet (standalone) | P1 priority, included in Tutorial 1 for MVP | Phase 2 |
| Case Study 1: Healthcare Diagnosis Agent (HIPAA) | P2 priority, extended example | Phase 3 |
| Case Study 2: Financial Fraud Detection (SOX) | P2 priority, extended example | Phase 3 |
| Case Study 3: Legal Contract Review (Discovery) | P2 priority, extended example | Phase 3 |
| Test naming convention refactor | P3 priority, optional polish | Phase 3 |

---

## 6. Design Considerations

### Tutorial Structure

Each tutorial should follow this consistent structure:

```
1. Introduction (2-3 min read)
   - What and why
   - When to use this component
   
2. Core Concepts (5-10 min read)
   - Key classes and data structures
   - Code examples with explanations
   
3. Practical Application (5-7 min read)
   - Step-by-step workflow
   - Common patterns
   
4. Case Study (3-5 min read)
   - Real-world scenario
   - Problem → Solution → Outcome
   
5. Best Practices (2-3 min read)
   - Dos and don'ts
   - Performance considerations
   
6. Cross-References
   - Related tutorials
   - Interactive notebook link
```

### Diagram Requirements

| Tutorial | Required Diagram | Format |
|----------|-----------------|--------|
| Tutorial 1 | Component decision tree | Mermaid flowchart |
| Tutorial 2 | Post-incident analysis workflow | Mermaid sequence |
| Tutorial 3 | Signature verification flow | Mermaid flowchart |
| Tutorial 4 | Validation workflow | Mermaid flowchart |

### Code Example Standards

- All code examples must be **tested** before inclusion
- Use realistic data (de-identified for healthcare/finance examples)
- Include imports and context for copy-paste usability
- Follow existing codebase patterns from `lesson-17/backend/explainability/`

---

## 7. Technical Considerations

### Dependencies

| Component | Source Location |
|-----------|-----------------|
| BlackBoxRecorder | `lesson-17/backend/explainability/black_box.py` |
| AgentFacts/Registry | `lesson-17/backend/explainability/agent_facts.py` |
| GuardRails/Validators | `lesson-17/backend/explainability/guardrails.py` |
| PhaseLogger | `lesson-17/backend/explainability/phase_logger.py` |

### Existing Notebooks for Reference

| Notebook | Status | Path |
|----------|--------|------|
| BlackBox Demo | ✅ Complete | `lesson-17/notebooks/01_black_box_recording_demo.ipynb` |
| AgentFacts Demo | ✅ Complete | `lesson-17/notebooks/02_agent_facts_verification.ipynb` |
| GuardRails Demo | ✅ Complete | `lesson-17/notebooks/03_guardrails_validation_traces.ipynb` |
| PhaseLogger Demo | ❌ Missing | `lesson-17/notebooks/04_phase_logger_workflow.ipynb` |

### Integration Points

- Tutorials should reference existing test files for additional examples:
  - `lesson-17/tests/test_black_box.py` (18 tests)
  - `lesson-17/tests/test_agent_facts.py` (26 tests)
  - `lesson-17/tests/test_guardrails.py` (24 tests)
  - `lesson-17/tests/test_phase_logger.py` (26 tests)

- Architecture diagram available at: `lesson-17/diagrams/explainability_architecture.svg`

---

## 8. Success Metrics

### Quantitative Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Tutorial reading time | <25 min each | Word count / 200 WPM |
| Notebook execution time | <5 min | Jupyter timing |
| Code example success rate | 100% | All examples execute without errors |
| Cross-link coverage | 100% | All tutorials link to related content |
| Diagram render success | 100% | Mermaid + PNG export validates |

### Qualitative Metrics

| Metric | Target | Evaluation |
|--------|--------|------------|
| Enterprise applicability | High | Case studies address real compliance needs |
| Beginner accessibility | Medium-High | Junior developers can follow tutorials |
| Copy-paste usability | High | Code examples work with minimal modification |

### Completion Checklist

**Per Tutorial:**
- [ ] Outline reviewed
- [ ] All code examples tested
- [ ] Diagrams render correctly
- [ ] Reading time measured
- [ ] Cross-links added
- [ ] Added to TUTORIAL_INDEX.md

**Phase Logger Notebook:**
- [ ] All cells execute without errors
- [ ] Execution time <5 minutes
- [ ] Mermaid diagram renders
- [ ] Markdown explanations between code cells

---

## 9. Open Questions

| ID | Question | Impact | Status |
|----|----------|--------|--------|
| Q1 | Should tutorials include video walkthroughs in addition to written content? | Medium - affects effort estimate | Open |
| Q2 | What de-identified sample data should be used for healthcare/finance examples? | High - affects realism of case studies | Open |
| Q3 | Should we add a glossary of terms (e.g., "audit trail", "tamper detection")? | Low - nice-to-have for beginners | Open |
| Q4 | Who will perform peer review of tutorials before publishing? | Medium - affects quality gates | Open |
| Q5 | Should tutorials include exercises or just demonstrations? | Medium - affects engagement | Open |

---

## Appendix A: File Structure

```
lesson-17/
├── tutorials/                          # NEW: Tutorial content
│   ├── 01_explainability_fundamentals.md
│   ├── 02_black_box_recording_debugging.md
│   ├── 03_agentfacts_governance.md
│   └── 04_guardrails_validation_pii.md
├── notebooks/
│   ├── 01_black_box_recording_demo.ipynb      # Existing
│   ├── 02_agent_facts_verification.ipynb      # Existing
│   ├── 03_guardrails_validation_traces.ipynb  # Existing
│   └── 04_phase_logger_workflow.ipynb         # NEW
├── backend/explainability/                     # Existing implementation
├── tests/                                      # Existing tests (94 passing)
├── TUTORIAL_INDEX.md                           # UPDATE with new tutorials
└── README.md                                   # UPDATE with tutorial links
```

---

## Appendix B: Estimated Effort

| Item | Estimated Hours | Notes |
|------|-----------------|-------|
| Tutorial 1: Explainability Fundamentals | 4-6 | Foundation, includes decision tree |
| Tutorial 2: BlackBox Recording | 4-5 | Case study + workflow diagram |
| Tutorial 3: AgentFacts Governance | 4-5 | Signature verification + HIPAA example |
| Tutorial 4: GuardRails Validation | 4-5 | 7 validators + PII case study |
| Phase Logger Notebook | 2-3 | 15-20 cells, realistic workflow |
| **Total MVP** | **18-24 hours** | |

---

## Appendix C: Related Documents

- Source TODO: [lesson-17/NEXT_PHASE_TODO.md](../lesson-17/NEXT_PHASE_TODO.md)
- Reflection: [lesson-17/REFLECTION.md](../lesson-17/REFLECTION.md)
- Architecture: [lesson-17/diagrams/explainability_architecture.svg](../lesson-17/diagrams/explainability_architecture.svg)
- PRD Template: [.claude/create-prd.md](../.claude/create-prd.md)

---

**End of PRD**

