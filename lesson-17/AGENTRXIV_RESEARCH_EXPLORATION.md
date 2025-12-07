# AgentRxiv Research Exploration

**Date:** 2025-11-30
**Purpose:** Document the research source for PhaseLogger component

---

## PhaseLogger Research Source

The **PhaseLogger** in lesson-17 is inspired by **AgentRxiv**, which is a real research paper:

| Attribute | Value |
|-----------|-------|
| **Paper Title** | "AgentRxiv: Towards Collaborative Autonomous Research" |
| **arXiv ID** | **arXiv:2503.18102** |
| **Authors** | Samuel Schmidgall, Michael Moor |
| **Website** | [agentrxiv.github.io](https://agentrxiv.github.io/) |
| **PDF** | [agentrxiv.github.io/resources/agentrxiv.pdf](https://agentrxiv.github.io/resources/agentrxiv.pdf) |

---

## Key Workflow Phases from AgentRxiv

AgentRxiv is built on **Agent Laboratory**, which automates research through **three core phases**:

1. **Literature Review** - Agents review and retrieve prior research
2. **Experimentation** - Agents conduct experiments
3. **Report Writing** - Agents generate research reports

### AgentRxiv Architecture

- Centralized preprint server for autonomous research agents
- Enables collaborative, cumulative knowledge sharing
- Modeled after arXiv, bioRxiv, and medRxiv
- Agents can upload and retrieve research papers asynchronously

### Performance Results

- 11.4% relative improvement over baseline on MATH-500
- Baseline accuracy: 70.2% → Peak accuracy: 78.2% (with collaborative agents)
- Without AgentRxiv access: performance plateaued at 73.4–73.8%

---

## How Lesson-17 Adapts This

The PhaseLogger extends AgentRxiv's 3-phase model to **9 phases** (`phase_logger.py:36`):

```
PLANNING → LITERATURE_REVIEW → DATA_COLLECTION → EXECUTION →
EXPERIMENT → VALIDATION → REPORTING → COMPLETED → FAILED
```

### Phase Mapping

| AgentRxiv Phase | Lesson-17 PhaseLogger |
|-----------------|----------------------|
| Literature Review | `LITERATURE_REVIEW` |
| Experimentation | `EXPERIMENT`, `EXECUTION` |
| Report Writing | `REPORTING` |
| (Extended) | `PLANNING`, `DATA_COLLECTION`, `VALIDATION` |
| (Terminal states) | `COMPLETED`, `FAILED` |

---

## Research Citations in Lesson-17

| Component | Research Source | Reference |
|-----------|----------------|-----------|
| **PhaseLogger** | AgentRxiv | arXiv:2503.18102 |
| **AgentFacts** | AgentFacts paper | arXiv:2506.13794 * |
| **GuardRails** | Guardrails AI | [github.com/ShreyaR/guardrails](https://github.com/ShreyaR/guardrails) |

\* Note: The arXiv:2506.13794 citation uses a future date format (June 2025). See `articles/agent-facts-critique.md` for discussion.

---

## Code References

### PhaseLogger Implementation

- **File:** `lesson-17/backend/explainability/phase_logger.py`
- **Lines 3-7:** Module docstring with AgentRxiv reference
- **Lines 36-46:** `WorkflowPhase` enum with 9 phases
- **Line 167:** Class docstring mentioning AgentRxiv inspiration

### Documentation References

| File | Line | Content |
|------|------|---------|
| `README.md` | 22 | AgentRxiv PDF link |
| `REFLECTION.md` | 12 | Research alignment mention |
| `TUTORIAL_INDEX.md` | 197 | External references table |
| `plan/agent-explainability-framework.md` | 9 | Key research references |
| `__init__.py` | 13 | Module-level citation |

---

## Key Insights

### Why AgentRxiv Matters for PhaseLogger

1. **Research Reproducibility** - Phase-based logging enables tracking of multi-step research workflows
2. **Decision Provenance** - Records why decisions were made at each phase
3. **Collaborative Debugging** - Enables post-hoc analysis of autonomous agent behavior
4. **Compliance Auditing** - JSON exports for regulatory requirements

### Design Decision: 9 Phases vs 3 Phases

The extension from 3 to 9 phases provides:

- **Finer granularity** for complex workflows beyond research
- **Explicit terminal states** (COMPLETED, FAILED) for state machine correctness
- **Separation of concerns** (DATA_COLLECTION vs EXPERIMENT)
- **Planning phase** for upfront workflow design

---

## References

1. Schmidgall, S., & Moor, M. (2025). *AgentRxiv: Towards Collaborative Autonomous Research*. arXiv:2503.18102. https://arxiv.org/abs/2503.18102

2. AgentRxiv Website: https://agentrxiv.github.io/

3. Agent Laboratory Framework (underlying AgentRxiv): Coordinates LLM agents through Literature Review → Experimentation → Report Writing phases.

---

**End of Exploration**
