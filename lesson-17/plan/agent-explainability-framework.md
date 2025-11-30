# Agent Explainability Framework (Lesson-17)

## Overview

Build a production-grade explainability framework for AI agents that provides complete audit trails, verifiable metadata, and declarative validation - enabling compliance, debugging, and trust in multi-agent systems.

**Key Research References:**
- **AgentFacts** - [arXiv:2506.13794](https://arxiv.org/abs/2506.13794) - Universal metadata standard with cryptographically-signed capability declarations
- **AgentRxiv** - [agentrxiv.github.io/resources/agentrxiv.pdf](https://agentrxiv.github.io/resources/agentrxiv.pdf) - Multi-agent research environment with phase-based logging
- **Guardrails AI** - [github.com/ShreyaR/guardrails](https://github.com/ShreyaR/guardrails) - Declarative schemas/validators for prompt transparency

## Architecture

Extend existing lesson-16 infrastructure:
- **Reuse**: `AuditLogger`, `save_checkpoint`/`load_checkpoint`, `Result[T,E]`, Pydantic validation schemas
- **New**: Black Box Recorder, AgentFacts registry, GuardRail validators, Phase-based workflow logger

---

## Component 1: Black Box Recorder

Aviation-style persistent recording of all agent activities for post-incident analysis.

### Files to Create
- `lesson-17/backend/explainability/black_box.py`

### Builds On
- `lesson-16/backend/reliability/audit_log.py` - Extend `AuditLogger` for richer traces
- `lesson-16/backend/reliability/checkpoint.py` - Reuse persistence patterns

### Key Classes

```python
class BlackBoxRecorder:
    """Aviation-style flight recorder for agent workflows."""
    
    def __init__(self, workflow_id: str, storage_path: Path) -> None:
        """Initialize recorder with workflow ID and storage location."""
    
    def record_task_plan(self, task_id: str, plan: TaskPlan) -> None:
        """Persist the task plan with steps, dependencies, and rollback points."""
    
    def record_collaborators(self, task_id: str, agents: list[AgentInfo]) -> None:
        """Record which agents participated in the workflow."""
    
    def record_parameter_substitution(
        self, task_id: str, param: str, old_val: Any, new_val: Any, reason: str
    ) -> None:
        """Log parameter changes with before/after values and justification."""
    
    def record_execution_trace(self, task_id: str, trace: ExecutionTrace) -> None:
        """Store complete execution history with decision points."""
    
    def export_black_box(self, task_id: str, filepath: Path) -> None:
        """Export all recordings for a task to a single JSON file."""
    
    def replay(self, task_id: str) -> Iterator[RecordedEvent]:
        """Replay recorded events for debugging/analysis."""


class TaskPlan(BaseModel):
    """Persisted task plan with steps, dependencies, and rollback points."""
    
    plan_id: str
    task_id: str
    created_at: datetime
    steps: list[PlanStep]
    dependencies: dict[str, list[str]]  # step_id -> dependent_step_ids
    rollback_points: list[str]  # step_ids that can be rolled back to
    metadata: dict[str, Any]


class PlanStep(BaseModel):
    """Individual step in a task plan."""
    
    step_id: str
    description: str
    agent_id: str
    expected_inputs: list[str]
    expected_outputs: list[str]
    timeout_seconds: int
    is_critical: bool  # If True, failure stops workflow


class ExecutionTrace(BaseModel):
    """Complete execution history with decision points and outcomes."""
    
    trace_id: str
    task_id: str
    start_time: datetime
    end_time: datetime | None
    events: list[TraceEvent]
    final_outcome: str  # success, failure, timeout, cancelled
    error_chain: list[str] | None  # For cascade failure analysis


class TraceEvent(BaseModel):
    """Single event in an execution trace."""
    
    event_id: str
    timestamp: datetime
    event_type: str  # step_start, step_end, decision, error, checkpoint
    agent_id: str | None
    step_id: str | None
    input_hash: str  # SHA256 of inputs for integrity
    output_hash: str | None
    duration_ms: int | None
    metadata: dict[str, Any]
```

---

## Component 2: AgentFacts Registry

Verifiable metadata standard for agent identity, capabilities, and policies (based on arXiv:2506.13794).

### Files to Create
- `lesson-17/backend/explainability/agent_facts.py`

### Builds On
- Pydantic schemas from `lesson-16/backend/reliability/validation.py`

### Key Classes

```python
class Capability(BaseModel):
    """Agent capability declaration."""
    
    name: str
    description: str
    input_schema: dict[str, Any]  # JSON Schema
    output_schema: dict[str, Any]
    estimated_latency_ms: int
    cost_per_call: float | None
    requires_approval: bool = False


class Policy(BaseModel):
    """Operational policy for an agent."""
    
    policy_id: str
    name: str
    description: str
    policy_type: str  # rate_limit, data_access, approval_required, etc.
    constraints: dict[str, Any]
    effective_from: datetime
    effective_until: datetime | None


class AgentFacts(BaseModel):
    """Verifiable agent metadata for audits and governance."""
    
    agent_id: str
    agent_name: str
    owner: str  # Team or individual responsible
    version: str
    description: str
    capabilities: list[Capability]
    policies: list[Policy]
    created_at: datetime
    updated_at: datetime
    signature_hash: str  # SHA256 for verification
    parent_agent_id: str | None  # For agent hierarchies
    
    class Config:
        extra = "forbid"  # Reject unknown fields
    
    def compute_signature(self) -> str:
        """Compute cryptographic hash of agent facts for verification."""
    
    def verify_signature(self) -> bool:
        """Verify the signature hash matches current state."""


class AgentFactsRegistry:
    """Registry for storing and verifying AgentFacts."""
    
    def __init__(self, storage_path: Path) -> None:
        """Initialize registry with storage location."""
    
    def register(self, agent_facts: AgentFacts) -> None:
        """Register agent facts, computing and storing signature."""
    
    def update(self, agent_id: str, updates: dict[str, Any]) -> AgentFacts:
        """Update agent facts, recomputing signature."""
    
    def verify(self, agent_id: str) -> bool:
        """Verify agent facts have not been tampered with."""
    
    def get(self, agent_id: str) -> AgentFacts | None:
        """Retrieve agent facts by ID."""
    
    def get_capabilities(self, agent_id: str) -> list[Capability]:
        """Get capabilities for an agent."""
    
    def get_policies(self, agent_id: str) -> list[Policy]:
        """Get policies for an agent."""
    
    def find_by_capability(self, capability_name: str) -> list[AgentFacts]:
        """Find agents with a specific capability."""
    
    def audit_trail(self, agent_id: str) -> list[AuditEntry]:
        """Get audit trail of all changes to agent facts."""
    
    def export_for_audit(self, agent_ids: list[str], filepath: Path) -> None:
        """Export agent facts for compliance audit."""
```

---

## Component 3: Declarative GuardRails

Guardrails-style validators that document prompt structures, constraints, and validation results.

### Files to Create
- `lesson-17/backend/explainability/guardrails.py`

### Builds On
- `lesson-16/backend/reliability/validation.py` - Extend Pydantic patterns
- `lesson-16/backend/reliability/isolation.py` - Reuse `Result[T,E]`

### Key Classes

```python
class FailAction(Enum):
    """Actions to take when validation fails."""
    
    REJECT = "reject"      # Reject output entirely
    FIX = "fix"            # Attempt automatic fix
    ESCALATE = "escalate"  # Escalate to human review
    LOG = "log"            # Log and continue (non-blocking)
    RETRY = "retry"        # Retry with modified prompt


class Constraint(BaseModel):
    """Single validation constraint."""
    
    name: str
    description: str
    check_fn: str  # Name of validation function
    params: dict[str, Any]
    severity: str  # error, warning, info
    on_fail: FailAction


class ValidationEntry(BaseModel):
    """Single validation result entry."""
    
    constraint_name: str
    passed: bool
    message: str
    severity: str
    timestamp: datetime
    input_excerpt: str | None  # Relevant portion of input
    fix_applied: str | None  # Description of fix if any


class ValidationResult(BaseModel):
    """Complete validation result with trace."""
    
    guardrail_name: str
    input_hash: str
    is_valid: bool
    entries: list[ValidationEntry]
    total_errors: int
    total_warnings: int
    validation_time_ms: int
    action_taken: FailAction


class GuardRail(BaseModel):
    """Declarative validator with documentation and trace generation."""
    
    name: str
    description: str
    version: str
    schema: type[BaseModel] | None  # Pydantic schema for structure
    constraints: list[Constraint]
    on_fail_default: FailAction = FailAction.REJECT
    
    class Config:
        arbitrary_types_allowed = True


class PromptGuardRail(GuardRail):
    """Documents prompt structure and constraints for transparency."""
    
    prompt_template: str
    required_fields: list[str]
    optional_fields: list[str]
    example_valid_output: str
    example_invalid_output: str
    
    def document(self) -> str:
        """Generate human-readable documentation of the guardrail."""


class GuardRailValidator:
    """Executes guardrails and produces rich validation traces."""
    
    def __init__(self) -> None:
        """Initialize validator with empty trace."""
        self._trace: list[ValidationEntry] = []
    
    def validate(
        self, input_data: dict[str, Any], guardrail: GuardRail
    ) -> ValidationResult:
        """Validate input against guardrail, returning detailed result."""
    
    def validate_prompt_output(
        self, output: str, guardrail: PromptGuardRail
    ) -> ValidationResult:
        """Validate LLM output against prompt guardrail."""
    
    def get_validation_trace(self) -> list[ValidationEntry]:
        """Get all validation entries from current session."""
    
    def clear_trace(self) -> None:
        """Clear the validation trace."""
    
    def export_trace(self, filepath: Path) -> None:
        """Export validation trace to JSON file."""


# Built-in validators (inspired by Guardrails AI)
class BuiltInValidators:
    """Collection of common validators."""
    
    @staticmethod
    def length_check(min_len: int, max_len: int) -> Constraint:
        """Validate string length is within bounds."""
    
    @staticmethod
    def regex_match(pattern: str) -> Constraint:
        """Validate string matches regex pattern."""
    
    @staticmethod
    def json_schema(schema: dict) -> Constraint:
        """Validate against JSON schema."""
    
    @staticmethod
    def no_pii() -> Constraint:
        """Check for PII (SSN, credit card, etc.)."""
    
    @staticmethod
    def confidence_range(min_conf: float, max_conf: float) -> Constraint:
        """Validate confidence score is within range."""
    
    @staticmethod
    def on_topic(allowed_topics: list[str]) -> Constraint:
        """Validate response is on-topic."""
    
    @staticmethod
    def no_hallucination(context: str) -> Constraint:
        """Check output is grounded in provided context."""
```

---

## Component 4: Phase-Based Workflow Logger

AgentRxiv-style logging for multi-phase workflows (Planning -> Execution -> Validation -> Reporting).

### Files to Create
- `lesson-17/backend/explainability/phase_logger.py`

### Builds On
- `lesson-16/backend/reliability/audit_log.py` - Extend logging
- `lesson-16/backend/orchestrators/base.py` - Integrate with orchestration

### Key Classes

```python
class WorkflowPhase(Enum):
    """Standard workflow phases (AgentRxiv-inspired)."""
    
    PLANNING = "planning"
    LITERATURE_REVIEW = "literature_review"  # For research workflows
    DATA_COLLECTION = "data_collection"
    EXECUTION = "execution"
    EXPERIMENT = "experiment"  # For research workflows
    VALIDATION = "validation"
    REPORTING = "reporting"
    COMPLETED = "completed"
    FAILED = "failed"


class Decision(BaseModel):
    """Logged decision with reasoning and alternatives."""
    
    decision_id: str
    timestamp: datetime
    decision: str
    reasoning: str
    alternatives_considered: list[str]
    selected_because: str
    confidence: float
    agent_id: str
    reversible: bool


class PhaseOutcome(BaseModel):
    """Outcome of a workflow phase."""
    
    phase: WorkflowPhase
    status: str  # success, failure, partial, skipped
    start_time: datetime
    end_time: datetime
    duration_ms: int
    decisions_made: int
    artifacts_produced: list[str]
    errors: list[str]
    next_phase: WorkflowPhase | None


class PhaseSummary(BaseModel):
    """Summary of all phases in a workflow."""
    
    workflow_id: str
    total_phases: int
    completed_phases: int
    total_decisions: int
    total_duration_ms: int
    phase_outcomes: list[PhaseOutcome]
    overall_status: str


class PhaseLogger:
    """Logs workflow phases with decisions and outcomes."""
    
    def __init__(self, workflow_id: str, storage_path: Path) -> None:
        """Initialize logger for a workflow."""
    
    def start_phase(self, phase: WorkflowPhase, metadata: dict | None = None) -> None:
        """Mark the start of a workflow phase."""
    
    def log_decision(
        self,
        decision: str,
        reasoning: str,
        alternatives: list[str],
        selected_because: str,
        confidence: float = 1.0,
        agent_id: str | None = None,
        reversible: bool = True,
    ) -> Decision:
        """Log a decision made during the current phase."""
    
    def log_artifact(self, artifact_name: str, artifact_path: Path) -> None:
        """Log an artifact produced during the current phase."""
    
    def log_error(self, error: str, recoverable: bool = True) -> None:
        """Log an error during the current phase."""
    
    def end_phase(self, status: str = "success") -> PhaseOutcome:
        """Mark the end of the current phase and return outcome."""
    
    def get_current_phase(self) -> WorkflowPhase | None:
        """Get the currently active phase."""
    
    def get_phase_decisions(self, phase: WorkflowPhase) -> list[Decision]:
        """Get all decisions made during a specific phase."""
    
    def get_phase_summary(self) -> PhaseSummary:
        """Get summary of all phases in the workflow."""
    
    def export_workflow_log(self, filepath: Path) -> None:
        """Export complete workflow log to JSON file."""
    
    def visualize_workflow(self) -> str:
        """Generate Mermaid diagram of workflow phases and decisions."""
```

---

## Directory Structure

```
lesson-17/
├── backend/
│   ├── __init__.py
│   └── explainability/
│       ├── __init__.py
│       ├── black_box.py          # Component 1: Black Box Recorder
│       ├── agent_facts.py        # Component 2: AgentFacts Registry
│       ├── guardrails.py         # Component 3: Declarative GuardRails
│       └── phase_logger.py       # Component 4: Phase-Based Logger
├── cache/
│   ├── black_box_recordings/     # Black box data storage
│   └── agent_facts_registry/     # AgentFacts storage
├── notebooks/
│   ├── 01_black_box_recording_demo.ipynb
│   ├── 02_agent_facts_verification.ipynb
│   └── 03_guardrails_validation_traces.ipynb
├── tutorials/
│   ├── 01_explainability_fundamentals.md
│   ├── 02_black_box_implementation.md
│   ├── 03_agent_facts_governance.md
│   └── 04_guardrails_transparency.md
├── tests/
│   ├── __init__.py
│   ├── test_black_box.py
│   ├── test_agent_facts.py
│   ├── test_guardrails.py
│   └── test_phase_logger.py
├── diagrams/
│   └── explainability_architecture.mmd
├── plan/
│   └── agent-explainability-framework.md  # This file
├── README.md
└── TUTORIAL_INDEX.md
```

---

## Integration Points

| New Component | Reuses From Lesson-16 |
|---------------|----------------------|
| BlackBoxRecorder | `AuditLogger` patterns, `save_checkpoint`/`load_checkpoint`, PII redaction (`_redact_pii`) |
| AgentFacts | Pydantic `BaseModel`, `extra="forbid"` pattern, field validators |
| GuardRails | `InvoiceExtraction`/`FraudDetection` schema patterns, `Result[T,E]` type |
| PhaseLogger | `AuditLogger.log_step()`, `execution_log` from orchestrators, workflow tracing |

---

## Implementation Order

### Phase 1: Setup (Est. 30 min)
- Create directory structure
- Create all `__init__.py` files
- Set up imports from lesson-16

### Phase 2: Black Box Recorder (Est. 2 hours)
- Implement `TaskPlan`, `PlanStep`, `ExecutionTrace`, `TraceEvent` models
- Implement `BlackBoxRecorder` class
- Add persistence to JSON files
- Write unit tests

### Phase 3: AgentFacts Registry (Est. 2 hours)
- Implement `Capability`, `Policy`, `AgentFacts` models
- Implement `AgentFactsRegistry` class
- Add signature computation and verification
- Write unit tests

### Phase 4: Declarative GuardRails (Est. 3 hours)
- Implement `Constraint`, `ValidationEntry`, `ValidationResult` models
- Implement `GuardRail` and `PromptGuardRail` classes
- Implement `GuardRailValidator` with built-in validators
- Write unit tests

### Phase 5: Phase-Based Logger (Est. 2 hours)
- Implement `WorkflowPhase`, `Decision`, `PhaseOutcome` models
- Implement `PhaseLogger` class
- Add Mermaid visualization
- Write unit tests

### Phase 6: Integration Tests (Est. 1 hour)
- Test components working together
- Test integration with lesson-16 reliability components

### Phase 7: Notebooks (Est. 2 hours)
- Create demo notebooks for each component
- Add practical examples

### Phase 8: Documentation (Est. 1 hour)
- Write README.md
- Write tutorials
- Create TUTORIAL_INDEX.md

---

## Success Criteria

1. **Black Box Recorder**: Can record and replay complete workflow executions
2. **AgentFacts**: Can register, verify, and audit agent metadata
3. **GuardRails**: Can validate outputs with rich traces for debugging
4. **PhaseLogger**: Can log multi-phase workflows with decision tracking
5. **All components**: Pass unit tests with >90% coverage
6. **Integration**: Components work with existing lesson-16 infrastructure

