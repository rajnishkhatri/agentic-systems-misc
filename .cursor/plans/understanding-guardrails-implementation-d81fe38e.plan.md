<!-- d81fe38e-6809-4be0-93c1-96b7a225b3c7 641998d3-58dc-451a-865f-18047fe6ebb7 -->
# Understanding GuardRails Implementation

This plan breaks down the understanding of `guardrails.py` into three focused tasks: data-driven analysis, demo exploration, and architectural integration.

## Task 1: Understand Functionality Through Data

**Objective:** Analyze how guardrails.py works with real data from the `data/` folder.

**Files to examine:**

- `data/pii_examples_50.json` - 50 examples with PII (SSN, credit cards, emails, phones) for testing PII detection
- `data/agent_metadata_10.json` - Agent metadata that may use guardrails for validation
- `data/workflows/*.json` - Workflow traces that may include guardrail validation results
- `data/DATASET_SUMMARY.json` - Dataset statistics and structure

**Key analysis points:**

1. **PII Detection Patterns:**

                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                - Map PII types in `pii_examples_50.json` to `BuiltInValidators.check_pii()` regex patterns
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                - Understand how `no_pii()` constraint detects: SSN (`\d{3}-\d{2}-\d{4}`), credit cards, emails, phones
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                - Trace validation flow: input → constraint → ValidationEntry → ValidationResult

2. **Data Structure Mapping:**

                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                - How workflow traces structure data for guardrail validation
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                - How agent metadata defines validation requirements
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                - Schema compatibility with Pydantic models in guardrails.py

3. **Validation Scenarios:**

                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                - Identify test cases: valid outputs, missing fields, PII violations, format errors
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                - Map data examples to constraint types: length_check, required_fields, json_parseable, etc.

## Task 2: Understand Through Demo Implementation

**Objective:** Trace the actual execution flow through the notebook demo and cached validation traces.

**Files to examine:**

- `notebooks/03_guardrails_validation_traces.ipynb` - Complete demo with 10 cells showing:
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                - Basic guardrail creation and validation
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                - Constraint creation with severity levels
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                - PII detection with real data
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                - Built-in validators demo
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                - Combined validators
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                - PromptGuardRail for LLM outputs
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                - Validation trace analysis
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                - Trace export functionality
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                - Documentation generation

- `cache/guardrails_demo/validation_trace.json` - Exported trace with 50 validation entries showing:
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                - Constraint execution results
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                - Pass/fail patterns
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                - Input excerpts for failed validations
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                - Timestamp sequencing

**Key execution flow to trace:**

1. **GuardRail Creation:**
   ```
   GuardRail(name, description, constraints, on_fail_default)
   → Constraint(name, check_fn, params, severity, on_fail)
   → BuiltInValidators factory methods (no_pii, length_check, etc.)
   ```

2. **Validation Execution:**
   ```
   GuardRailValidator.validate(input_data, guardrail)
   → _run_constraint() for each constraint
   → BuiltInValidators.check_*() methods
   → ValidationEntry creation
   → ValidationResult aggregation
   ```

3. **Trace Generation:**
   ```
   validator._trace.append(entry) for each validation
   → validator.get_validation_trace()
   → validator.export_trace(filepath)
   ```

4. **PromptGuardRail Flow:**
   ```
   validate_prompt_output(output_string, PromptGuardRail)
   → JSON parsing attempt
   → Required field checking
   → Constraint execution
   → ValidationResult with LLM-specific metadata
   ```


## Task 3: Understand Through Architecture & End-to-End Integration

**Objective:** Understand how guardrails.py fits into the lesson-17 explainability framework and the complete end-to-end flow: BlackBox → AgentFacts → GuardRails.

**Architecture files:**

- `diagrams/explainability_architecture.mmd` - Component relationships
- `README.md` - Framework overview and integration points
- `backend/explainability/__init__.py` - Module exports
- `backend/explainability/policy_bridge.py` - Integration bridge between AgentFacts and GuardRails
- `tutorials/02_black_box_recording_debugging.md` - Integration examples

**End-to-End Integration Flow:**

### Flow 1: BlackBox → GuardRails Integration

**Pattern:** `ValidatedWorkflowExecutor` (from tutorials)

```
1. BlackBoxRecorder records workflow start
   └─> record_task_plan(), record_collaborators()

2. Agent executes step
   └─> step_fn(input_data) → output

3. GuardRailValidator validates output
   └─> validator.validate(output, guardrail) → ValidationResult

4. BlackBoxRecorder logs validation as DECISION event
   └─> add_trace_event(EventType.DECISION, {
         guardrail_name, is_valid, total_errors,
         constraint_results: [entry.constraint_name, passed, message]
       })

5. Handle validation result:
   - REJECT → Record ERROR event, raise ValidationError
   - LOG → Record WARNING event, continue
   - ESCALATE → Record DECISION event, queue for review
   - FIX → Record DECISION event, apply fix, continue

6. Export black box with validation traces
   └─> export_black_box() includes all validation results
```

**Key Integration Points:**

- `TraceEvent.metadata` contains full `ValidationResult` data
- `EventType.DECISION` used for validation outcomes
- Validation failures recorded as `EventType.ERROR` with detailed constraint results

### Flow 2: AgentFacts → GuardRails Integration

**Pattern:** `policy_bridge.py` converts policies to guardrails

```
1. AgentFacts Registry stores agent with policies
   └─> AgentFacts.policies: [Policy(policy_type="data_access", ...)]

2. PolicyBridge converts Policy → GuardRail
   └─> policy_to_guardrail(policy) → GuardRail | None
   
   Conversion rules:
   - data_access + pii_handling_mode="redact" 
     → GuardRail with no_pii constraint
   - approval_required 
     → GuardRail with required_fields(["approval_id"])
   - rate_limit 
     → None (requires external enforcement)

3. GuardRailValidator enforces converted policies
   └─> enforce_agent_policies(agent_id, registry, validator, output_data)
       → [(policy_name, passed, message), ...]

4. Results logged to both systems:
   - AgentFacts: Audit trail of policy checks
   - GuardRails: Validation trace entries
```

**Key Integration Points:**

- `policy_bridge.policy_to_guardrail()` - Conversion function
- `policy_bridge.enforce_agent_policies()` - End-to-end enforcement
- AgentFacts declares WHAT policies exist
- GuardRails enforces WHETHER output complies

### Flow 3: Complete End-to-End Flow

**Full Integration Pattern:**

```
┌─────────────────────────────────────────────────────────────┐
│ STEP 1: Agent Registration (AgentFacts)                      │
├─────────────────────────────────────────────────────────────┤
│ registry.register(AgentFacts(                                │
│   agent_id="invoice-extractor-v2",                          │
│   policies=[                                                │
│     Policy(policy_type="data_access",                       │
│            constraints={"pii_handling_mode": "redact"})     │
│   ]                                                         │
│ ))                                                          │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│ STEP 2: Workflow Execution Setup (BlackBox)                 │
├─────────────────────────────────────────────────────────────┤
│ recorder = BlackBoxRecorder(workflow_id, storage_path)      │
│ recorder.record_task_plan(task_id, TaskPlan(...))           │
│ recorder.record_collaborators(task_id, [agent_info])        │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│ STEP 3: Policy → GuardRail Conversion (PolicyBridge)       │
├─────────────────────────────────────────────────────────────┤
│ agent = registry.get("invoice-extractor-v2")               │
│ policy = agent.get_active_policies()[0]                     │
│ guardrail = policy_to_guardrail(policy)                     │
│   → GuardRail(name="data_access_hipaa-001",                 │
│              constraints=[no_pii_constraint])              │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│ STEP 4: Agent Execution with Validation                     │
├─────────────────────────────────────────────────────────────┤
│ executor = ValidatedWorkflowExecutor(workflow_id, ...)        │
│ output = executor.execute_step_with_validation(             │
│   step_id, agent_id, step_fn, input_data, guardrail        │
│ )                                                            │
│                                                              │
│ Internal flow:                                               │
│   1. recorder.add_trace_event(STEP_START)                    │
│   2. output = step_fn(input_data)                            │
│   3. validation_result = validator.validate(output, guardrail)│
│   4. recorder.add_trace_event(DECISION, {validation_result}) │
│   5. if not valid: handle_failure(action)                     │
│   6. recorder.add_trace_event(STEP_END)                       │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│ STEP 5: Audit & Compliance Export                           │
├─────────────────────────────────────────────────────────────┤
│ recorder.export_black_box(task_id, audit_path)             │
│   → Contains: task_plan, collaborators, parameter_logs,     │
│              execution_trace (with validation events)       │
│                                                              │
│ validator.export_trace(trace_path)                          │
│   → Contains: all ValidationEntry records                   │
│                                                              │
│ registry.export_for_audit([agent_id], compliance_path)     │
│   → Contains: agent metadata, policies, signatures          │
└─────────────────────────────────────────────────────────────┘
```

**Integration points to map:**

1. **Component Relationships:**

                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                - **BlackBoxRecorder** ← logs validation results from GuardRails
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                - **AgentFacts** → declares policies → **PolicyBridge** → converts to **GuardRails**
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                - **GuardRails** → validates outputs → results logged to **BlackBoxRecorder**
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                - **PhaseLogger** → can track validation phases (VALIDATION phase)

2. **Design Patterns:**

                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                - **Bridge Pattern**: `policy_bridge.py` bridges AgentFacts (declaration) and GuardRails (enforcement)
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                - **Executor Pattern**: `ValidatedWorkflowExecutor` orchestrates recording + validation
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                - **Declarative Validation**: GuardRails inspired by Guardrails AI
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                - **Pydantic BaseModel**: Type safety across all components
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                - **Result[T,E] Pattern**: ValidationResult as success/failure container

3. **Core Classes Hierarchy:**
   ```
   AgentFacts (BaseModel)
   └─> Policy (BaseModel)
       └─> [via policy_bridge.policy_to_guardrail()]
           └─> GuardRail (BaseModel)
               └─> PromptGuardRail (extends GuardRail)
                   └─> [used by] GuardRailValidator
                       └─> ValidationResult (BaseModel)
                           └─> [logged to] BlackBoxRecorder
                               └─> TraceEvent (BaseModel)
   ```

4. **Data Flow:**
   ```
   Agent Registration (AgentFacts)
   ↓
   Policy Declaration (AgentFacts.policies)
   ↓
   Policy → GuardRail Conversion (policy_bridge)
   ↓
   Workflow Execution (BlackBoxRecorder records start)
   ↓
   Agent Output
   ↓
   GuardRail Validation (GuardRailValidator)
   ↓
   ValidationResult
   ↓
   BlackBoxRecorder logs DECISION event (with validation metadata)
   ↓
   Export: BlackBox JSON + Validation Trace JSON + AgentFacts Audit
   ```

5. **Failure Handling:**

                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                - **FailAction enum**: REJECT, FIX, ESCALATE, LOG, RETRY
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                - **Severity levels**: ERROR (blocking), WARNING (non-blocking), INFO (audit)
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                - **Action determination**: `on_fail_default` in GuardRail, per-constraint `on_fail`
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                - **Integration**: Failures logged to BlackBoxRecorder as ERROR or DECISION events

**Key architectural decisions:**

- **Separation of Concerns**: 
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                - AgentFacts = WHAT policies should exist (declaration)
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                - GuardRails = WHETHER output complies (enforcement)
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                - BlackBox = WHAT happened (recording)
- **Bridge Pattern**: PolicyBridge converts between declaration and enforcement
- **Extensibility**: Custom constraints via `check_fn` string lookup
- **Traceability**: Every validation creates audit trail entries in both systems
- **Documentation**: Self-documenting via `document()` method

**Lesson-16 Integration:**

- Reuses Pydantic validation patterns
- Similar to `InvoiceExtraction`/`FraudDetection` validators but with trace generation
- Uses `Result[T,E]` concept (ValidationResult as success/failure container)
- BlackBoxRecorder extends AuditLogger patterns from lesson-16

### To-dos

- [ ] Analyze data files (pii_examples_50.json, workflows, agent_metadata) to understand how guardrails.py validates real data, map PII patterns to check_pii() implementation, and trace validation scenarios
- [ ] Trace execution flow through notebook demo (03_guardrails_validation_traces.ipynb) and validation_trace.json, understanding GuardRail creation, validation execution, trace generation, and PromptGuardRail flow
- [ ] Map guardrails.py architecture: component relationships, design patterns, class hierarchy, data flow, failure handling, and integration with lesson-16 and other explainability components