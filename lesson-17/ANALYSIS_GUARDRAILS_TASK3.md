# Task 3: Understanding GuardRails Architecture & End-to-End Integration

## Overview
This document maps the architecture of `guardrails.py`, its design patterns, class hierarchy, data flow, failure handling, and complete end-to-end integration with BlackBox and AgentFacts components.

## 1. Component Relationships

### Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    Lesson-17 Explainability Framework        │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────┐      ┌──────────────┐      ┌───────────┐ │
│  │  AgentFacts  │─────▶│ PolicyBridge │─────▶│ GuardRails│ │
│  │  (Declaration)│      │  (Conversion)│      │(Enforcement)│ │
│  └──────┬───────┘      └──────────────┘      └─────┬─────┘ │
│         │                                            │       │
│         │                                            ▼       │
│         │                                    ┌─────────────┐ │
│         │                                    │ Validation  │ │
│         │                                    │   Result    │ │
│         │                                    └──────┬──────┘ │
│         │                                           │        │
│         ▼                                           ▼        │
│  ┌──────────────┐                          ┌─────────────┐ │
│  │ BlackBox     │◀─────────────────────────│ TraceEvent  │ │
│  │ Recorder     │                          │ (DECISION)  │ │
│  │ (Recording)  │                          └─────────────┘ │
│  └──────────────┘                                           │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### Integration Points

1. **AgentFacts → GuardRails** (via PolicyBridge)
   - **Purpose**: Convert declarative policies to runtime constraints
   - **Function**: `policy_to_guardrail(policy: Policy) -> GuardRail | None`
   - **Flow**: Policy declaration → Policy conversion → GuardRail creation

2. **GuardRails → BlackBoxRecorder**
   - **Purpose**: Log validation results for audit trails
   - **Pattern**: `ValidatedWorkflowExecutor` orchestrates both
   - **Flow**: Validation execution → ValidationResult → TraceEvent (DECISION) → BlackBox recording

3. **BlackBoxRecorder → GuardRails**
   - **Purpose**: Record validation events in execution traces
   - **Event Type**: `EventType.DECISION` with validation metadata
   - **Flow**: Validation → Result → Event creation → Trace storage

## 2. Design Patterns

### 2.1 Bridge Pattern: PolicyBridge

**Purpose**: Decouple policy declaration (AgentFacts) from enforcement (GuardRails)

**Implementation**:
```python
# Declaration Layer (AgentFacts)
policy = Policy(
    policy_type="data_access",
    constraints={"pii_handling_mode": "redact"}
)

# Bridge Layer (PolicyBridge)
guardrail = policy_to_guardrail(policy)
# → GuardRail(
#     name="data_access_hipaa-001",
#     constraints=[Constraint(check_fn="pii", ...)]
#   )

# Enforcement Layer (GuardRails)
result = validator.validate(output_data, guardrail)
```

**Benefits**:
- Policies can be declared before enforcement is implemented
- Enables "audit mode" where policies are logged but not enforced
- Clear separation between "what should happen" and "what did happen"

### 2.2 Executor Pattern: ValidatedWorkflowExecutor

**Purpose**: Orchestrate workflow execution with integrated validation and recording

**Structure**:
```python
class ValidatedWorkflowExecutor:
    def __init__(self, workflow_id: str, storage_path: Path):
        self.recorder = BlackBoxRecorder(...)  # Recording
        self.validator = GuardRailValidator()  # Validation
    
    def execute_step_with_validation(...):
        # 1. Record start
        # 2. Execute step
        # 3. Validate output
        # 4. Record validation result
        # 5. Handle failure actions
        # 6. Record completion
```

**Flow**:
```
Step Start (BlackBox)
  ↓
Agent Execution
  ↓
Validation (GuardRails)
  ↓
Validation Result
  ↓
Decision Event (BlackBox) ← Contains ValidationResult metadata
  ↓
Failure Handling (if needed)
  ↓
Step End (BlackBox)
```

### 2.3 Factory Pattern: BuiltInValidators

**Purpose**: Create reusable Constraint objects with consistent configurations

**Implementation**:
```python
class BuiltInValidators:
    @staticmethod
    def no_pii() -> Constraint:
        return Constraint(
            name="no_pii",
            check_fn="pii",
            ...
        )
    
    @staticmethod
    def check_pii(data, field="output") -> tuple[bool, str]:
        # Actual validation logic
        ...
```

**Usage**:
```python
# Factory method creates constraint
constraint = BuiltInValidators.no_pii()

# Check method executes validation
passed, message = BuiltInValidators.check_pii(data)
```

### 2.4 Result Pattern: ValidationResult

**Purpose**: Encapsulate validation outcomes (similar to `Result[T,E]` from lesson-16)

**Structure**:
```python
class ValidationResult(BaseModel):
    is_valid: bool  # Success/failure indicator
    entries: list[ValidationEntry]  # Detailed results
    total_errors: int
    total_warnings: int
    action_taken: FailAction | None  # What to do on failure
```

**Benefits**:
- Type-safe error handling
- Rich trace information
- Actionable failure metadata

## 3. Class Hierarchy

### Complete Class Structure

```
BaseModel (Pydantic)
│
├── Constraint
│   ├── name: str
│   ├── check_fn: str
│   ├── params: dict[str, Any]
│   ├── severity: Severity
│   └── on_fail: FailAction
│
├── ValidationEntry
│   ├── constraint_name: str
│   ├── passed: bool
│   ├── message: str
│   ├── severity: Severity
│   ├── timestamp: datetime
│   ├── input_excerpt: str | None
│   └── fix_applied: str | None
│
├── ValidationResult
│   ├── guardrail_name: str
│   ├── input_hash: str
│   ├── is_valid: bool
│   ├── entries: list[ValidationEntry]
│   ├── total_errors: int
│   ├── total_warnings: int
│   ├── validation_time_ms: int
│   └── action_taken: FailAction | None
│
├── GuardRail
│   ├── name: str
│   ├── description: str
│   ├── version: str
│   ├── schema_name: str | None
│   ├── constraints: list[Constraint]
│   ├── on_fail_default: FailAction
│   └── document() -> str  # Self-documentation
│
└── PromptGuardRail (extends GuardRail)
    ├── prompt_template: str
    ├── required_fields: list[str]
    ├── optional_fields: list[str]
    ├── example_valid_output: str
    ├── example_invalid_output: str
    └── document() -> str  # Extended documentation

GuardRailValidator (Executor)
├── _trace: list[ValidationEntry]
├── _schemas: dict[str, type[BaseModel]]
├── register_schema(name, schema)
├── validate(input_data, guardrail) -> ValidationResult
├── validate_prompt_output(output, guardrail) -> ValidationResult
├── get_validation_trace() -> list[ValidationEntry]
├── clear_trace()
└── export_trace(filepath)

BuiltInValidators (Static Factory + Check Methods)
├── Factory Methods (return Constraint):
│   ├── no_pii() -> Constraint
│   ├── length_check(min, max) -> Constraint
│   ├── regex_match(pattern) -> Constraint
│   ├── confidence_range(min, max) -> Constraint
│   ├── required_fields(fields) -> Constraint
│   ├── json_parseable() -> Constraint
│   ├── value_in_list(values) -> Constraint
│   └── always_pass(message) -> Constraint
│
└── Check Methods (return tuple[bool, str]):
    ├── check_pii(data, field) -> (bool, str)
    ├── check_length(data, min_len, max_len, field) -> (bool, str)
    ├── check_regex(data, pattern, field) -> (bool, str)
    ├── check_confidence(data, min_conf, max_conf, field) -> (bool, str)
    ├── check_required(data, fields) -> (bool, str)
    ├── check_json(data, field) -> (bool, str)
    ├── check_in_list(data, allowed_values, field) -> (bool, str)
    └── check_always_pass(data, message) -> (bool, str)

Enums
├── FailAction
│   ├── REJECT
│   ├── FIX
│   ├── ESCALATE
│   ├── LOG
│   └── RETRY
│
└── Severity
    ├── ERROR
    ├── WARNING
    └── INFO
```

## 4. Data Flow

### 4.1 Complete End-to-End Flow

```
┌─────────────────────────────────────────────────────────────┐
│ STEP 1: Agent Registration (AgentFacts)                      │
├─────────────────────────────────────────────────────────────┤
│ registry = AgentFactsRegistry(storage_path)                  │
│                                                              │
│ agent_facts = AgentFacts(                                    │
│     agent_id="invoice-extractor-v2",                        │
│     policies=[                                              │
│         Policy(                                             │
│             policy_id="hipaa-001",                          │
│             policy_type="data_access",                      │
│             constraints={"pii_handling_mode": "redact"}     │
│         )                                                   │
│     ]                                                       │
│ )                                                           │
│                                                              │
│ registry.register(agent_facts)                              │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│ STEP 2: Workflow Setup (BlackBox)                           │
├─────────────────────────────────────────────────────────────┤
│ recorder = BlackBoxRecorder(                                │
│     workflow_id="invoice-extraction-001",                │
│     storage_path=Path("cache/")                             │
│ )                                                           │
│                                                              │
│ recorder.record_task_plan(task_id, TaskPlan(...))          │
│ recorder.record_collaborators(task_id, [agent_info])        │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│ STEP 3: Policy → GuardRail Conversion (PolicyBridge)       │
├─────────────────────────────────────────────────────────────┤
│ agent = registry.get("invoice-extractor-v2")               │
│ policy = agent.get_active_policies()[0]                     │
│                                                              │
│ guardrail = policy_to_guardrail(policy)                     │
│ # Returns:                                                  │
│ # GuardRail(                                                │
│ #     name="data_access_hipaa-001",                         │
│ #     constraints=[                                         │
│ #         Constraint(                                       │
│ #             name="no_pii_in_output",                      │
│ #             check_fn="pii",                               │
│ #             on_fail=FailAction.FIX                        │
│ #         )                                                 │
│ #     ]                                                     │
│ # )                                                         │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│ STEP 4: Workflow Execution with Validation                  │
├─────────────────────────────────────────────────────────────┤
│ executor = ValidatedWorkflowExecutor(                       │
│     workflow_id="invoice-extraction-001",                   │
│     storage_path=Path("cache/")                             │
│ )                                                           │
│                                                              │
│ output = executor.execute_step_with_validation(            │
│     step_id="extract-invoice",                             │
│     agent_id="invoice-extractor-v2",                        │
│     step_fn=extract_invoice,                               │
│     input_data={"invoice_text": "..."},                    │
│     guardrail=guardrail                                    │
│ )                                                           │
│                                                              │
│ Internal Execution:                                         │
│   1. recorder.add_trace_event(STEP_START)                   │
│   2. output = step_fn(input_data)                          │
│   3. validation_result = validator.validate(output, guardrail)│
│      └─> For each constraint:                              │
│          * _run_constraint(data, constraint)               │
│          * Get check function: BuiltInValidators.check_*    │
│          * Execute: check_fn(data, **params)               │
│          * Create ValidationEntry                           │
│          * Append to entries and _trace                     │
│      └─> Aggregate: is_valid, total_errors, action_taken   │
│   4. recorder.add_trace_event(DECISION, {                  │
│        "guardrail_name": guardrail.name,                    │
│        "is_valid": validation_result.is_valid,             │
│        "total_errors": validation_result.total_errors,     │
│        "constraint_results": [...]                         │
│      })                                                     │
│   5. if not valid: handle_failure(action)                   │
│   6. recorder.add_trace_event(STEP_END)                    │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│ STEP 5: Audit & Compliance Export                           │
├─────────────────────────────────────────────────────────────┤
│ # Export BlackBox with validation events                    │
│ recorder.export_black_box(task_id, audit_path)             │
│ # Contains:                                                  │
│ # - task_plan                                                │
│ # - collaborators                                            │
│ # - parameter_substitutions                                  │
│ # - execution_trace (with DECISION events containing         │
│ #   validation results)                                      │
│                                                              │
│ # Export validation trace                                   │
│ validator.export_trace(trace_path)                          │
│ # Contains:                                                  │
│ # - exported_at timestamp                                    │
│ # - entry_count                                              │
│ # - entries: [all ValidationEntry objects]                  │
│                                                              │
│ # Export AgentFacts for compliance                          │
│ registry.export_for_audit([agent_id], compliance_path)     │
│ # Contains:                                                  │
│ # - agent metadata                                           │
│ # - policies                                                 │
│ # - signatures                                               │
└─────────────────────────────────────────────────────────────┘
```

### 4.2 Validation Execution Flow (Detailed)

```
validator.validate(input_data, guardrail)
│
├─> 1. Type checking
│   └─> Raises TypeError if invalid types
│
├─> 2. Start timer
│   └─> start_time = datetime.now(UTC)
│
├─> 3. Compute input hash
│   └─> input_hash = SHA256(json.dumps(input_data, sort_keys=True))
│
├─> 4. Schema validation (if schema_name specified)
│   └─> if guardrail.schema_name in validator._schemas:
│       └─> schema = validator._schemas[guardrail.schema_name]
│       └─> _validate_schema(input_data, schema)
│           └─> try: schema(**input_data)
│           └─> except ValidationError: create failed ValidationEntry
│
├─> 5. Constraint execution loop
│   └─> for constraint in guardrail.constraints:
│       │
│       ├─> _run_constraint(input_data, constraint)
│       │   │
│       │   ├─> Get check function
│       │   │   └─> check_fn = getattr(BuiltInValidators, f"check_{constraint.check_fn}")
│       │   │
│       │   ├─> Execute check function
│       │   │   └─> passed, message = check_fn(input_data, **constraint.params)
│       │   │
│       │   └─> Create ValidationEntry
│       │       └─> ValidationEntry(
│       │           constraint_name=constraint.name,
│       │           passed=passed,
│       │           message=message,
│       │           severity=constraint.severity,
│       │           input_excerpt=str(input_data)[:200] if not passed else None
│       │       )
│       │
│       ├─> Append to entries list
│       │
│       └─> Append to validator._trace
│
├─> 6. Aggregate results
│   ├─> errors = count(entries where not passed and severity=ERROR)
│   ├─> warnings = count(entries where not passed and severity=WARNING)
│   ├─> is_valid = (errors == 0)
│   └─> action_taken = None if is_valid else guardrail.on_fail_default
│
├─> 7. Calculate duration
│   └─> duration_ms = int((end_time - start_time).total_seconds() * 1000)
│
└─> 8. Return ValidationResult
    └─> ValidationResult(
        guardrail_name=guardrail.name,
        input_hash=input_hash,
        is_valid=is_valid,
        entries=entries,
        total_errors=errors,
        total_warnings=warnings,
        validation_time_ms=duration_ms,
        action_taken=action_taken
    )
```

## 5. Failure Handling

### 5.1 FailAction Enum

```python
class FailAction(str, Enum):
    REJECT = "reject"      # Reject output entirely (raise exception)
    FIX = "fix"            # Attempt automatic fix (future: auto-redaction)
    ESCALATE = "escalate"  # Escalate to human review (queue for approval)
    LOG = "log"            # Log and continue (non-blocking warning)
    RETRY = "retry"        # Retry with modified prompt (future: prompt engineering)
```

### 5.2 Severity Levels

```python
class Severity(str, Enum):
    ERROR = "error"      # Must pass for valid output (blocks if fails)
    WARNING = "warning"  # Should pass but not blocking (logs warning)
    INFO = "info"        # Informational only (audit logging)
```

### 5.3 Failure Handling Flow

```
Validation Result: is_valid = False
│
├─> Determine action
│   └─> action = validation_result.action_taken or guardrail.on_fail_default
│
├─> REJECT Action
│   └─> if action == FailAction.REJECT:
│       ├─> BlackBoxRecorder.add_trace_event(ERROR, {
│       │       "error_type": "ValidationError",
│       │       "error_message": f"{total_errors} errors",
│       │       "validation_result": validation_result
│       │   })
│       └─> raise ValidationError(f"Validation failed: {total_errors} errors")
│
├─> LOG Action
│   └─> if action == FailAction.LOG:
│       ├─> BlackBoxRecorder.add_trace_event(ERROR, {
│       │       "error_type": "ValidationWarning",
│       │       "error_message": "Validation failed but continuing",
│       │       "validation_result": validation_result
│       │   })
│       └─> Continue execution (non-blocking)
│
├─> ESCALATE Action
│   └─> if action == FailAction.ESCALATE:
│       ├─> BlackBoxRecorder.add_trace_event(DECISION, {
│       │       "decision": "escalate_for_review",
│       │       "validation_result": validation_result
│       │   })
│       └─> queue_for_human_review(output, validation_result)
│
└─> FIX Action (Future)
    └─> if action == FailAction.FIX:
        ├─> Apply automatic fix (e.g., PII redaction)
        ├─> BlackBoxRecorder.add_trace_event(DECISION, {
        │       "decision": "auto_fix_applied",
        │       "fix_description": "...",
        │       "validation_result": validation_result
        │   })
        └─> Continue with fixed output
```

### 5.4 Integration with BlackBoxRecorder

**Validation failures are logged as events:**

```python
# Successful validation
recorder.add_trace_event(task_id, TraceEvent(
    event_type=EventType.DECISION,
    metadata={
        "decision": "output_validation",
        "guardrail_name": guardrail.name,
        "is_valid": True,
        "total_errors": 0
    }
))

# Failed validation (REJECT)
recorder.add_trace_event(task_id, TraceEvent(
    event_type=EventType.ERROR,
    metadata={
        "error_type": "ValidationError",
        "error_message": "Validation failed: 1 errors",
        "guardrail_name": guardrail.name,
        "constraint_results": [
            {
                "name": "no_pii",
                "passed": False,
                "message": "Potential SSN detected",
                "severity": "error"
            }
        ]
    }
))
```

## 6. Integration Patterns

### 6.1 AgentFacts → GuardRails Integration

**Pattern**: Policy declaration to enforcement conversion

```python
# 1. Agent registered with policies
agent = AgentFacts(
    agent_id="diagnosis-generator-v1",
    policies=[
        Policy(
            policy_type="data_access",
            constraints={"pii_handling_mode": "redact"}
        )
    ]
)
registry.register(agent)

# 2. Policy converted to GuardRail
guardrail = policy_to_guardrail(agent.get_active_policies()[0])
# → GuardRail with no_pii constraint

# 3. Output validated against guardrail
result = validator.validate(diagnosis_output, guardrail)

# 4. Results logged to both systems
registry.verify(agent_id)  # AgentFacts integrity check
validator.export_trace(trace_path)  # GuardRails trace
```

### 6.2 BlackBox → GuardRails Integration

**Pattern**: ValidatedWorkflowExecutor orchestrates both

```python
# 1. Executor initializes both components
executor = ValidatedWorkflowExecutor(workflow_id, storage_path)
# → executor.recorder = BlackBoxRecorder(...)
# → executor.validator = GuardRailValidator()

# 2. Execution with validation
output = executor.execute_step_with_validation(
    step_id, agent_id, step_fn, input_data, guardrail
)

# 3. Internal flow:
#    a. recorder.add_trace_event(STEP_START)
#    b. output = step_fn(input_data)
#    c. validation_result = validator.validate(output, guardrail)
#    d. recorder.add_trace_event(DECISION, {validation_result metadata})
#    e. if not valid: handle_failure(action)
#    f. recorder.add_trace_event(STEP_END)

# 4. Export includes both
recorder.export_black_box(task_id, audit_path)
# → Contains execution trace with validation events
validator.export_trace(trace_path)
# → Contains all validation entries
```

### 6.3 Complete Integration Example

```python
from pathlib import Path
from backend.explainability import (
    AgentFactsRegistry, AgentFacts, Policy,
    BlackBoxRecorder,
    GuardRailValidator, GuardRail, BuiltInValidators,
    policy_to_guardrail
)

# STEP 1: Register agent with policies
registry = AgentFactsRegistry(Path("cache/agent_facts"))
agent = AgentFacts(
    agent_id="invoice-extractor-v2",
    policies=[
        Policy(
            policy_id="hipaa-001",
            policy_type="data_access",
            constraints={"pii_handling_mode": "redact"}
        )
    ]
)
registry.register(agent)

# STEP 2: Setup workflow recording
recorder = BlackBoxRecorder(
    workflow_id="invoice-extraction-001",
    storage_path=Path("cache/")
)
recorder.record_task_plan(task_id, TaskPlan(...))

# STEP 3: Convert policy to guardrail
agent = registry.get("invoice-extractor-v2")
policy = agent.get_active_policies()[0]
guardrail = policy_to_guardrail(policy)

# STEP 4: Execute with validation
validator = GuardRailValidator()
output = extract_invoice(input_data)
result = validator.validate(output, guardrail)

# STEP 5: Record validation result
recorder.add_trace_event(task_id, TraceEvent(
    event_type=EventType.DECISION,
    metadata={
        "guardrail_name": guardrail.name,
        "is_valid": result.is_valid,
        "total_errors": result.total_errors,
        "constraint_results": [
            {
                "name": entry.constraint_name,
                "passed": entry.passed,
                "message": entry.message
            }
            for entry in result.entries
        ]
    }
))

# STEP 6: Export for audit
recorder.export_black_box(task_id, Path("audit/blackbox.json"))
validator.export_trace(Path("audit/validation_trace.json"))
registry.export_for_audit(["invoice-extractor-v2"], Path("audit/agent_facts.json"))
```

## 7. Key Architectural Decisions

### 7.1 Separation of Concerns

- **AgentFacts**: Declares WHAT policies should exist (declaration layer)
- **GuardRails**: Enforces WHETHER output complies (enforcement layer)
- **BlackBox**: Records WHAT happened (recording layer)
- **PolicyBridge**: Converts between declaration and enforcement (bridge layer)

### 7.2 Extensibility

- **Custom Constraints**: Via `check_fn` string lookup in `BuiltInValidators`
- **Schema Registration**: `validator.register_schema()` for structural validation
- **Custom Fail Actions**: Extend `FailAction` enum for new behaviors
- **PromptGuardRail**: Extends base GuardRail for LLM-specific needs

### 7.3 Traceability

- **Every validation** creates `ValidationEntry` objects
- **All entries** accumulated in `validator._trace`
- **Trace export** provides complete audit trail
- **BlackBox integration** logs validation results as events

### 7.4 Self-Documentation

- **GuardRail.document()**: Generates markdown documentation
- **PromptGuardRail.document()**: Includes prompt templates and examples
- **Constraint descriptions**: Human-readable explanations
- **Policy metadata**: Stored in AgentFacts for compliance

## 8. Lesson-16 Integration

### 8.1 Reused Patterns

1. **Pydantic BaseModel**: All data structures use Pydantic for type safety
2. **Result[T,E] Pattern**: `ValidationResult` encapsulates success/failure
3. **AuditLogger Patterns**: BlackBoxRecorder extends AuditLogger concepts
4. **Checkpoint Persistence**: Reuses checkpoint save/load patterns

### 8.2 Similar Components

- **InvoiceExtraction/FraudDetection validators** (lesson-16) → **GuardRails** (lesson-17)
  - Both validate outputs
  - GuardRails adds trace generation and declarative constraints
  
- **AuditLogger** (lesson-16) → **BlackBoxRecorder** (lesson-17)
  - Both log events
  - BlackBoxRecorder adds task plans, collaborators, parameter logs

### 8.3 Design Evolution

- **Lesson-16**: Focus on reliability (retries, isolation, checkpoints)
- **Lesson-17**: Focus on explainability (transparency, audit trails, governance)
- **Integration**: Lesson-17 builds on lesson-16 patterns while adding new capabilities

## 9. Summary

The GuardRails implementation provides:

1. **Declarative Validation**: Constraints defined as data structures
2. **Rich Traces**: Every validation creates detailed audit entries
3. **Policy Integration**: Automatic conversion from AgentFacts policies
4. **BlackBox Integration**: Validation results logged in execution traces
5. **Self-Documentation**: Guardrails generate their own documentation
6. **Extensibility**: Custom constraints and fail actions
7. **Type Safety**: Pydantic models throughout
8. **Compliance Ready**: Complete audit trails for regulated industries

The end-to-end flow enables:
- **Declaration**: Policies defined in AgentFacts
- **Conversion**: Policies converted to GuardRails via PolicyBridge
- **Enforcement**: Runtime validation of agent outputs
- **Recording**: Results logged to BlackBoxRecorder
- **Audit**: Complete export for compliance and debugging
