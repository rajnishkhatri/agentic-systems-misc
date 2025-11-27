# Lesson 17: Tutorial Index

## Agent Explainability Framework

This lesson provides comprehensive tools for AI agent transparency, auditing, and compliance.

---

## Tutorials

In-depth written tutorials covering each component of the explainability framework.

| Tutorial | Duration | Level | Description |
|----------|----------|-------|-------------|
| [01: Explainability Fundamentals](tutorials/01_explainability_fundamentals.md) | ~20 min | Beginner | Introduction to agent explainability, the four pillars (Recording, Identity, Validation, Reasoning), and component selection decision tree |
| [02: BlackBox Recording for Debugging](tutorials/02_black_box_recording_debugging.md) | ~25 min | Intermediate | Aviation black box analogy, all 9 event types, post-incident analysis workflow, and cascade failure case study |
| [03: AgentFacts for Governance](tutorials/03_agentfacts_governance.md) | ~25 min | Intermediate | Agent identity verification, capability declarations, policy management, SHA256 signature verification, and HIPAA compliance case study |
| [04: GuardRails for Validation and PII](tutorials/04_guardrails_validation_pii.md) | ~25 min | Intermediate | Declarative validation philosophy, all 7 built-in validators, custom validators, failure actions, and PII detection case study |

---

## Interactive Notebooks

| Notebook | Description | Key Concepts |
|----------|-------------|--------------|
| [01_black_box_recording_demo](notebooks/01_black_box_recording_demo.ipynb) | Black Box Recorder demo | Task plans, collaborators, traces |
| [02_agent_facts_verification](notebooks/02_agent_facts_verification.ipynb) | AgentFacts Registry demo | Signatures, capabilities, audit |
| [03_guardrails_validation_traces](notebooks/03_guardrails_validation_traces.ipynb) | GuardRails demo | Validators, traces, PII detection |
| [04_phase_logger_workflow](notebooks/04_phase_logger_workflow.ipynb) | PhaseLogger demo | Phase lifecycle, decisions, artifacts |

---

## Core Components

### 1. Black Box Recorder

**Purpose:** Aviation-style flight recorder for post-incident analysis

**Key Classes:**
- `BlackBoxRecorder` - Main recording interface
- `TaskPlan` - Persisted task plan with steps and dependencies
- `PlanStep` - Individual step definition
- `ExecutionTrace` - Complete execution history
- `TraceEvent` - Single event in a trace

**Use Cases:**
- Debugging cascade failures
- Compliance auditing
- Workflow replay and analysis

### 2. AgentFacts Registry

**Purpose:** Verifiable metadata standard for agent governance (arXiv:2506.13794)

**Key Classes:**
- `AgentFacts` - Verifiable agent metadata
- `AgentFactsRegistry` - Storage and discovery
- `Capability` - Agent capability declaration
- `Policy` - Operational policy definition

**Use Cases:**
- Agent identity verification
- Capability-based discovery
- Compliance exports

### 3. GuardRails

**Purpose:** Declarative validators with transparency (Guardrails AI-inspired)

**Key Classes:**
- `GuardRail` - Constraint collection
- `PromptGuardRail` - Prompt structure documentation
- `GuardRailValidator` - Validation executor
- `BuiltInValidators` - Common validators

**Use Cases:**
- Output validation
- PII detection
- Prompt documentation

### 4. Phase Logger

**Purpose:** Multi-phase workflow logging (AgentRxiv-inspired)

**Key Classes:**
- `PhaseLogger` - Phase lifecycle manager
- `WorkflowPhase` - Standard phases
- `Decision` - Logged decision with reasoning
- `PhaseSummary` - Workflow statistics

**Use Cases:**
- Research workflow tracking
- Decision audit trails
- Workflow visualization

---

## Learning Path

### Beginner (~1 hour)

Start here to understand the fundamentals of agent explainability.

1. **Read** [Tutorial 01: Explainability Fundamentals](tutorials/01_explainability_fundamentals.md) (~20 min)
   - Learn the four pillars: Recording, Identity, Validation, Reasoning
   - Understand when to use each component
   - Review real-world scenarios

2. **Practice** [01_black_box_recording_demo](notebooks/01_black_box_recording_demo.ipynb) (~15 min)
   - Create your first BlackBoxRecorder
   - Record task plans and trace events
   - Export and inspect recordings

### Intermediate (~2.5 hours)

Deep dive into each component with tutorials and hands-on notebooks.

1. **Read** [Tutorial 02: BlackBox Recording for Debugging](tutorials/02_black_box_recording_debugging.md) (~25 min)
   - Master all 9 event types
   - Learn post-incident analysis workflow
   - Study cascade failure case study

2. **Read** [Tutorial 03: AgentFacts for Governance](tutorials/03_agentfacts_governance.md) (~25 min)
   - Understand capability and policy declarations
   - Learn SHA256 signature verification
   - Study HIPAA compliance case study

3. **Practice** [02_agent_facts_verification](notebooks/02_agent_facts_verification.ipynb) (~15 min)
   - Register agents with capabilities
   - Verify signatures and detect tampering
   - Export audit trails

4. **Read** [Tutorial 04: GuardRails for Validation and PII](tutorials/04_guardrails_validation_pii.md) (~25 min)
   - Master all 7 built-in validators
   - Understand failure actions and decision matrix
   - Study PII detection case study

5. **Practice** [03_guardrails_validation_traces](notebooks/03_guardrails_validation_traces.ipynb) (~15 min)
   - Create guardrails with multiple constraints
   - Test PII detection patterns
   - Export validation traces

### Advanced (~1 hour)

Apply your knowledge to production scenarios.

1. **Practice** [04_phase_logger_workflow](notebooks/04_phase_logger_workflow.ipynb) (~15 min)
   - Track multi-phase research workflows
   - Log decisions with reasoning
   - Generate workflow visualizations

2. **Integration Projects**
   - Create custom validators for your domain
   - Integrate BlackBox with existing orchestrators (see Integration Points below)
   - Build compliance dashboards from exported audit data
   - Implement multi-component workflows combining all four pillars

---

## Integration Points

### With Lesson 16 Reliability Framework

```python
# Use black box with orchestrators
from backend.explainability.black_box import BlackBoxRecorder

class InstrumentedOrchestrator(Orchestrator):
    def __init__(self, ...):
        self.recorder = BlackBoxRecorder(...)
    
    async def execute(self, task):
        self.recorder.add_trace_event(...)
        result = await super().execute(task)
        self.recorder.add_trace_event(...)
        return result
```

### With Validation Schemas

```python
# Use guardrails with Pydantic schemas
from backend.explainability.guardrails import GuardRailValidator
from lesson16.backend.reliability.validation import InvoiceExtraction

validator = GuardRailValidator()
validator.register_schema("invoice", InvoiceExtraction)
```

---

## Research References

| Topic | Source | Link |
|-------|--------|------|
| AgentFacts | arXiv:2506.13794 | [Paper](https://arxiv.org/abs/2506.13794) |
| AgentRxiv | Research Environment | [PDF](https://agentrxiv.github.io/resources/agentrxiv.pdf) |
| Guardrails AI | GitHub | [Repository](https://github.com/ShreyaR/guardrails) |

---

## Related Resources

- [Lesson 16: Agent Reliability](../lesson-16/README.md)
- [Lesson 15: Enterprise Agents](../lesson-15/README.md)
- [Patterns: TDD Workflow](../patterns/tdd-workflow.md)

