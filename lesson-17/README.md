# Lesson 17: Agent Explainability Framework

A comprehensive framework for AI agent transparency, auditing, and compliance.

## Overview

This lesson implements production-grade explainability components for AI agents, enabling:

- **Debugging**: Trace errors back to their source with black box recordings
- **Compliance**: Provide audit trails for regulated industries
- **Governance**: Verify agent identity and capabilities with AgentFacts
- **Transparency**: Document and validate agent outputs with GuardRails

## Research Background

This implementation is based on cutting-edge research:

| Concept | Source | Description |
|---------|--------|-------------|
| **Black Box Recording** | Aviation industry | Persisted task plans, collaborator lists, parameter logs, execution traces |
| **AgentFacts** | [arXiv:2506.13794](https://arxiv.org/abs/2506.13794) | Verifiable metadata with cryptographic signatures |
| **AgentRxiv** | [agentrxiv.github.io](https://agentrxiv.github.io/resources/agentrxiv.pdf) | Phase-based logging for multi-agent workflows |
| **Guardrails AI** | [github.com/ShreyaR/guardrails](https://github.com/ShreyaR/guardrails) | Declarative validators for prompt transparency |

## Components

### 1. Black Box Recorder (`black_box.py`)

Aviation-style flight recorder for agent workflows.

```python
from backend.explainability.black_box import BlackBoxRecorder, TaskPlan, PlanStep

recorder = BlackBoxRecorder(workflow_id="invoice-001", storage_path=Path("cache/"))
recorder.record_task_plan("task-1", TaskPlan(...))
recorder.record_collaborators("task-1", [AgentInfo(...)])
recorder.record_parameter_substitution("task-1", "model", "gpt-3.5", "gpt-4", "accuracy")
recorder.export_black_box("task-1", Path("audit/blackbox.json"))
```

**Features:**
- Task plan recording with steps and dependencies
- Collaborator tracking
- Parameter substitution logging
- Execution trace capture
- Export and replay functionality

### 2. AgentFacts Registry (`agent_facts.py`)

Verifiable agent metadata for governance and compliance.

```python
from backend.explainability.agent_facts import AgentFacts, AgentFactsRegistry, Capability

facts = AgentFacts(
    agent_id="extractor-v1",
    agent_name="Invoice Extractor",
    owner="finance-team",
    version="1.0.0",
    capabilities=[Capability(name="extract_vendor", description="...")]
)

registry = AgentFactsRegistry(storage_path=Path("cache/"))
registry.register(facts)
registry.verify("extractor-v1")  # Signature verification
registry.find_by_capability("extract_vendor")  # Discovery
```

**Features:**
- Cryptographic signature verification
- Capability declarations
- Policy management
- Agent discovery
- Audit trail tracking

### 3. GuardRails (`guardrails.py`)

Declarative validators with rich trace generation.

```python
from backend.explainability.guardrails import GuardRail, GuardRailValidator, BuiltInValidators

guardrail = GuardRail(
    name="invoice_validator",
    description="Validates invoice extraction",
    constraints=[
        BuiltInValidators.no_pii(),
        BuiltInValidators.required_fields(["vendor", "amount"]),
    ]
)

validator = GuardRailValidator()
result = validator.validate({"vendor": "Acme", "amount": 100}, guardrail)
print(f"Valid: {result.is_valid}, Errors: {result.total_errors}")
```

**Built-in Validators:**
- `length_check` - String length validation
- `regex_match` - Pattern matching
- `no_pii` - PII detection (SSN, credit cards, email, phone)
- `confidence_range` - Numeric range validation
- `required_fields` - Required field checking
- `json_parseable` - JSON validation
- `value_in_list` - Enum validation

### 4. Phase Logger (`phase_logger.py`)

Multi-phase workflow logging inspired by AgentRxiv.

```python
from backend.explainability.phase_logger import PhaseLogger, WorkflowPhase

logger = PhaseLogger(workflow_id="research-001", storage_path=Path("cache/"))
logger.start_phase(WorkflowPhase.PLANNING)
logger.log_decision("Use GPT-4", "Higher accuracy needed", alternatives=["GPT-3.5"])
logger.end_phase("success")

summary = logger.get_phase_summary()
mermaid = logger.visualize_workflow()
```

**Features:**
- Phase lifecycle management
- Decision logging with reasoning
- Artifact tracking
- Error logging
- Mermaid visualization

## Learning Resources

For in-depth learning, see the [**Tutorial Index**](TUTORIAL_INDEX.md) which includes:

| Tutorial | Level | Duration | Description |
|----------|-------|----------|-------------|
| [01: Explainability Fundamentals](tutorials/01_explainability_fundamentals.md) | Beginner | ~20 min | Four pillars of explainability, component selection |
| [02: BlackBox Recording](tutorials/02_black_box_recording_debugging.md) | Intermediate | ~25 min | Post-incident debugging workflow |
| [03: AgentFacts Governance](tutorials/03_agentfacts_governance.md) | Intermediate | ~25 min | Identity, signatures, compliance |
| [04: GuardRails Validation](tutorials/04_guardrails_validation_pii.md) | Intermediate | ~25 min | Validators, PII detection |

**Interactive Notebooks:**
- `01_black_box_recording_demo.ipynb` - Black Box Recorder hands-on
- `02_agent_facts_verification.ipynb` - AgentFacts Registry demo
- `03_guardrails_validation_traces.ipynb` - GuardRails validation
- `04_phase_logger_workflow.ipynb` - PhaseLogger workflow tracking

## Directory Structure

```
lesson-17/
├── backend/
│   ├── __init__.py
│   └── explainability/
│       ├── __init__.py
│       ├── black_box.py       # Black Box Recorder
│       ├── agent_facts.py     # AgentFacts Registry
│       ├── guardrails.py      # GuardRails Validators
│       └── phase_logger.py    # Phase Logger
├── tests/
│   ├── test_black_box.py
│   ├── test_agent_facts.py
│   ├── test_guardrails.py
│   └── test_phase_logger.py
├── tutorials/
│   ├── 01_explainability_fundamentals.md
│   ├── 02_black_box_recording_debugging.md
│   ├── 03_agentfacts_governance.md
│   └── 04_guardrails_validation_pii.md
├── notebooks/
│   ├── 01_black_box_recording_demo.ipynb
│   ├── 02_agent_facts_verification.ipynb
│   ├── 03_guardrails_validation_traces.ipynb
│   └── 04_phase_logger_workflow.ipynb
├── cache/                     # Runtime storage
├── plan/                      # Implementation plan
├── TUTORIAL_INDEX.md          # Learning path guide
└── README.md
```

## Integration with Lesson 16

This lesson builds on existing lesson-16 reliability infrastructure:

| Component | Reuses From Lesson-16 |
|-----------|----------------------|
| BlackBoxRecorder | `AuditLogger` patterns, `save_checkpoint`/`load_checkpoint` |
| AgentFacts | Pydantic `BaseModel`, `extra="forbid"` pattern |
| GuardRails | `InvoiceExtraction`/`FraudDetection` patterns, `Result[T,E]` |
| PhaseLogger | `AuditLogger.log_step()`, orchestrator patterns |

## Running Tests

```bash
cd lesson-17
python -m pytest tests/ -v
```

All 94 tests should pass.

## Quick Start

1. **Setup:**
```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path("lesson-17")))
```

2. **Record Agent Activity:**
```python
from backend.explainability.black_box import BlackBoxRecorder
recorder = BlackBoxRecorder("workflow-1", Path("cache/"))
# Record task plans, collaborators, traces...
```

3. **Register Agent Metadata:**
```python
from backend.explainability.agent_facts import AgentFacts, AgentFactsRegistry
registry = AgentFactsRegistry(Path("cache/"))
registry.register(AgentFacts(...))
```

4. **Validate Outputs:**
```python
from backend.explainability.guardrails import GuardRailValidator, GuardRail
validator = GuardRailValidator()
result = validator.validate(data, guardrail)
```

5. **Log Workflow Phases:**
```python
from backend.explainability.phase_logger import PhaseLogger, WorkflowPhase
logger = PhaseLogger("workflow-1", Path("cache/"))
logger.start_phase(WorkflowPhase.EXECUTION)
```

## License

MIT License - See repository root for details.

