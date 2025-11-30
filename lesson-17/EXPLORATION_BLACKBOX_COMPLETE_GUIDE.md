# BlackBox Recording System: A Complete End-to-End Guide

Let me explain the BlackBox recording system as if you're learning about it for the first time, building up from basics to the complete picture.

---

## Part 1: The Problem We're Solving

### The Debugging Nightmare Scenario

Imagine you're running an AI system that processes invoices automatically. It has multiple AI agents working together:

```
📄 Invoice comes in → 🤖 OCR Agent extracts text → 🤖 Extraction Agent finds vendor/amount
→ 🤖 Validation Agent checks database → 🤖 Approval Agent routes for approval → ✅ Done
```

One day, invoices stop getting approved. You get a support ticket:
> "47 invoices stuck! They're not making it past validation!"

**Without BlackBox Recording:**
- ❓ Which step failed?
- ❓ What were the inputs to that step?
- ❓ Did someone change a configuration?
- ❓ Were the right agents running?
- ❓ Can we reproduce this?

You're left guessing, checking scattered logs, and hoping to reproduce the issue.

**With BlackBox Recording:**
- ✅ Export complete recording of failed workflow
- ✅ Replay events in chronological order
- ✅ See exact parameter change that caused failure
- ✅ Understand which agent made what decision
- ✅ Root cause identified in minutes, not hours

---

## Part 2: The Aviation Analogy (Why "BlackBox"?)

### How Airplane Black Boxes Work

When an airplane crashes, investigators retrieve the "black box" (actually bright orange). It contains:

1. **Flight Data Recorder (FDR)**: Records hundreds of parameters
   - Altitude, speed, heading, engine temperature, control positions
   - Captured every fraction of a second
   - Helps investigators understand *what* happened

2. **Cockpit Voice Recorder (CVR)**: Records all cockpit audio
   - Pilot conversations, ATC communications, alarms
   - Helps investigators understand *why* decisions were made

### Mapping to AI Agent Systems

The BlackBox Recorder is the same concept for multi-agent workflows:

| Aviation | AI Agents | Captured By |
|----------|-----------|-------------|
| **FDR: Flight parameters** | Step timing, input/output hashes, agent states | `ExecutionTrace` |
| **CVR: Pilot decisions** | Agent reasoning, alternatives considered | `TraceEvent(DECISION)` |
| **Flight plan** | Intended workflow steps, dependencies | `TaskPlan` |
| **Crew manifest** | Which agents participated, their capabilities | `AgentInfo` |
| **Control changes** | Parameter modifications during execution | `ParameterSubstitution` |

---

## Part 3: The Four Core Data Types

The BlackBox system captures four distinct types of information:

### 1. TaskPlan - "What We Intended to Do"

Think of this as the flight plan before takeoff. It defines:
- **Steps**: The sequence of actions (OCR → Extract → Validate → Approve)
- **Dependencies**: "Can't validate until extraction completes"
- **Rollback Points**: Safe positions to recover from ("If validation fails, retry from extraction")
- **Timeouts**: Maximum duration for each step

**Example:**
```python
TaskPlan(
    plan_id="plan-invoice-001",
    task_id="process-invoice-12345",
    steps=[
        PlanStep(
            step_id="step-1-ocr",
            description="Extract text from invoice PDF",
            agent_id="ocr-agent-v2",
            expected_inputs=["invoice_pdf"],
            expected_outputs=["raw_text", "confidence_score"],
            timeout_seconds=60,
            is_critical=True,  # If this fails, stop workflow
            order=1
        ),
        PlanStep(
            step_id="step-2-extract",
            description="Extract vendor name and amount",
            agent_id="extraction-agent-v3",
            expected_inputs=["raw_text"],
            expected_outputs=["vendor_name", "amount"],
            timeout_seconds=45,
            is_critical=True,
            order=2
        )
    ],
    dependencies={
        "step-2-extract": ["step-1-ocr"]  # Extract depends on OCR
    },
    rollback_points=["step-1-ocr"]  # Can safely restart from here
)
```

**Why This Matters:**
When debugging, you compare the *plan* (what should have happened) vs. the *trace* (what actually happened). Deviations point to the problem.

### 2. AgentInfo - "Who Participated"

Records which agents were active during the workflow:

```python
AgentInfo(
    agent_id="extraction-agent-v3",
    agent_name="Invoice Field Extractor",
    role="extraction",
    joined_at=datetime.now(UTC),
    capabilities=["invoice_parsing", "receipt_parsing", "po_parsing"]
)
```

**Why This Matters:**
- **Version tracking**: "Was the correct agent version running?"
- **Capability check**: "Did the agent have the required capability?"
- **Timeline**: "When did this agent join?"

### 3. ParameterSubstitution - "What Configuration Changed"

This is often the smoking gun in failure investigations! Logs every parameter change:

```python
ParameterSubstitution(
    param_name="confidence_threshold",
    old_value="0.8",
    new_value="0.95",
    reason="Compliance team requested higher accuracy for Q4 audit",
    timestamp=datetime(2024, 11, 27, 14, 0, 10),
    agent_id="extraction-agent-v3"
)
```

**Real-World Impact:**
In the invoice processing failure, this parameter change was the root cause:
- Threshold changed from 0.8 → 0.95
- Extraction output had confidence 0.92
- Validation agent rejected results (0.92 < 0.95)
- 47 invoices stuck!

### 4. ExecutionTrace - "What Actually Happened"

The complete minute-by-minute chronicle of execution. Contains a sequence of `TraceEvent` objects:

**The 9 Event Types:**

| Event Type | Symbol | When It's Used |
|------------|--------|----------------|
| `STEP_START` | ▶ | Step begins execution |
| `STEP_END` | ■ | Step completes (success or failure) |
| `DECISION` | ◆ | Agent makes a choice with reasoning |
| `ERROR` | ✗ | Failure or exception occurs |
| `CHECKPOINT` | 💾 | State snapshot saved for recovery |
| `PARAMETER_CHANGE` | ⚙ | Configuration modified during execution |
| `COLLABORATOR_JOIN` | → | Agent enters the workflow |
| `COLLABORATOR_LEAVE` | ← | Agent exits the workflow |
| `ROLLBACK` | 🔄 | Recovery attempt (rolling back to checkpoint) |

**Example Event Sequence:**
```
14:00:00  ▶ STEP_START: extract_vendor (agent: invoice-extractor-v2)
14:00:05  ◆ DECISION: "Use GPT-4 for OCR correction"
             Alternatives: [GPT-3.5, Claude, Rule-based]
             Reason: "Higher accuracy needed for noisy scans"
14:00:10  ⚙ PARAMETER_CHANGE: confidence_threshold 0.8 → 0.95  ← ROOT CAUSE!
14:00:11  💾 CHECKPOINT: Saved state {vendor: "Acme Corp", amount: 4523.50}
14:00:12  ■ STEP_END: extract_vendor (success, confidence: 0.92)
14:00:12  ▶ STEP_START: validate_amount (agent: invoice-validator-v1)
14:00:15  ✗ ERROR: ValidationError "Confidence 0.92 < threshold 0.95"
14:00:18  ■ STEP_END: validate_amount (failed)
```

---

## Part 4: How Data Flows Through the System

### The Recording Lifecycle

```
┌─────────────────────────────────────────────────────────────────┐
│                    BLACKBOX RECORDING LIFECYCLE                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  1. INITIALIZATION                                               │
│     ┌──────────────────────────────────────┐                    │
│     │  recorder = BlackBoxRecorder(        │                    │
│     │    workflow_id="invoice-001",        │                    │
│     │    storage_path=Path("cache/")       │                    │
│     │  )                                   │                    │
│     └──────────────┬───────────────────────┘                    │
│                    │                                             │
│                    ▼                                             │
│  2. RECORDING (During Workflow Execution)                        │
│     ┌──────────────────────────────────────┐                    │
│     │  recorder.record_task_plan(...)      │ → disk: task_plan.json
│     │  recorder.record_collaborators(...)  │ → disk: collaborators.json
│     │  recorder.record_parameter_substitution(...) │ → disk: params.json
│     │  recorder.add_trace_event(...)       │ → disk: trace.json
│     │  recorder.add_trace_event(...)       │ (append more events)
│     └──────────────┬───────────────────────┘                    │
│                    │                                             │
│                    ▼                                             │
│  3. PERSISTENCE                                                  │
│     cache/black_box_recordings/invoice-001/                      │
│         ├── task-abc_plan.json         (~2-5 KB)                │
│         ├── task-abc_collaborators.json (~1-3 KB)               │
│         ├── task-abc_params.json        (~0.5-2 KB)             │
│         └── task-abc_trace.json         (~5-50 KB)              │
│                    │                                             │
│                    ▼                                             │
│  4. EXPORT (When Investigation Needed)                           │
│     ┌──────────────────────────────────────┐                    │
│     │  recorder.export_black_box(          │                    │
│     │    "task-abc",                       │                    │
│     │    Path("incidents/blackbox.json")   │                    │
│     │  )                                   │                    │
│     └──────────────┬───────────────────────┘                    │
│                    │                                             │
│                    ▼                                             │
│     incidents/blackbox.json (comprehensive single-file export)   │
│     Contains: plan + collaborators + params + trace + all events│
│                    │                                             │
│                    ▼                                             │
│  5. INVESTIGATION (Post-Incident Analysis)                       │
│     ┌──────────────────────────────────────┐                    │
│     │  for event in recorder.replay(...):  │                    │
│     │      # Chronological event replay    │                    │
│     │      analyze_event(event)            │                    │
│     └──────────────────────────────────────┘                    │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Storage Architecture

```
cache/
└── black_box_recordings/
    ├── workflow-001/           # Each workflow gets its own directory
    │   ├── task-abc_plan.json
    │   ├── task-abc_collaborators.json
    │   ├── task-abc_params.json
    │   └── task-abc_trace.json
    ├── workflow-002/
    │   └── ...
    └── workflow-003/
        └── ...
```

**Storage Estimates:**
- Simple workflow: ~10-60 KB per workflow
- Complex workflow: ~500 KB per workflow
- 1000 workflows/day × 30 days × 100 KB = ~3 GB/month

---

## Part 5: Complete Example - Invoice Processing Failure

Let me walk you through a complete debugging session using the BlackBox system.

### The Scenario

**Time:** 2024-11-27, 14:05 UTC
**Report:** "Invoice processing stopped working! 47 invoices stuck at validation!"
**Workflow ID:** `invoice-processing-001`

### Step 1: Export the Black Box

```python
from pathlib import Path
from backend.explainability.black_box import BlackBoxRecorder

# Connect to the recorder (data already persists on disk)
recorder = BlackBoxRecorder(
    workflow_id="invoice-processing-001",
    storage_path=Path("cache/")
)

# Export everything to a single file
export_path = Path("incidents/2024-11-27/invoice-001-blackbox.json")
recorder.export_black_box("process-invoice", export_path)
print(f"✓ Black box exported to: {export_path}")
```

**What gets exported:**
```json
{
  "workflow_id": "invoice-processing-001",
  "task_id": "process-invoice",
  "exported_at": "2024-11-27T14:05:00Z",
  "task_plan": {...},           // Intended execution plan
  "collaborators": [...],       // Agents that participated
  "parameter_substitutions": [...],  // Config changes
  "execution_trace": {...},     // Complete event history
  "all_events": [...]           // All events combined
}
```

### Step 2: Replay Events Chronologically

```python
# Replay all events in time order
for event in recorder.replay("process-invoice"):
    timestamp = event.timestamp.strftime("%H:%M:%S")
    print(f"[{timestamp}] {event.event_type}")
```

**Output reveals the timeline:**
```
[14:00:00] ▶ STEP_START: extract_vendor
[14:00:00] → COLLABORATOR_JOIN: invoice-extractor-v2
[14:00:05] ◆ DECISION: "Use GPT-4 for OCR correction"
[14:00:10] ⚙ PARAMETER_CHANGE: confidence_threshold 0.8 → 0.95  ⚠️
[14:00:11] 💾 CHECKPOINT: State saved
[14:00:12] ■ STEP_END: extract_vendor (confidence: 0.92)
[14:00:12] ← COLLABORATOR_LEAVE: invoice-extractor-v2
[14:00:12] ▶ STEP_START: validate_amount
[14:00:12] → COLLABORATOR_JOIN: invoice-validator-v1
[14:00:15] ✗ ERROR: "Confidence threshold too high (0.95) - no valid results"
[14:00:18] ■ STEP_END: validate_amount (FAILED)
[14:00:18] ← COLLABORATOR_LEAVE: invoice-validator-v1
```

### Step 3: Identify Anomalies

**Anomaly 1: Parameter Changed During Execution**
```python
# Look at parameter substitutions
params = recorder._parameter_subs.get("process-invoice", [])
for sub in params:
    print(f"⚙️ {sub.param_name}: {sub.old_value} → {sub.new_value}")
    print(f"   Reason: {sub.reason}")
    print(f"   Changed by: {sub.agent_id}")
```

**Output:**
```
⚙️ confidence_threshold: 0.8 → 0.95
   Reason: Compliance team requested higher accuracy for Q4 audit
   Changed by: extraction-agent-v3
```

**Anomaly 2: Output Confidence Below New Threshold**

The extraction step completed with `confidence: 0.92`, but the new threshold was `0.95`. All validation candidates were filtered out!

### Step 4: Root Cause Analysis

```
┌─────────────────────────────────────────────────────────────────┐
│                    CASCADE FAILURE CHAIN                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ROOT CAUSE (14:00:10)                                          │
│  ⚙️ Parameter change: confidence_threshold 0.8 → 0.95           │
│  Agent: extraction-agent-v3                                     │
│  Justification: "Compliance team request"                       │
│                                                                  │
│  ↓                                                               │
│                                                                  │
│  IMMEDIATE EFFECT (14:00:12)                                    │
│  Extraction output: confidence = 0.92                           │
│  New threshold: 0.95                                            │
│  Gap: 0.03 (output doesn't meet requirement!)                   │
│                                                                  │
│  ↓                                                               │
│                                                                  │
│  PROPAGATION (14:00:15)                                         │
│  ✗ Validation agent receives confidence=0.92, threshold=0.95    │
│  All validation candidates filtered (none meet threshold)       │
│  Empty result set → ValidationError                             │
│                                                                  │
│  ↓                                                               │
│                                                                  │
│  BUSINESS IMPACT                                                │
│  • Workflow terminated with status=failed                       │
│  • Invoice INV-2024-1234 ($4,523.50) not processed             │
│  • 47 invoices queued behind it                                 │
│  • Payment delays affecting vendor relationships                │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Step 5: The Fix

**Problem:** Parameter change created impossible condition (output confidence can never be ≥0.95 with current model).

**Solution 1: Add Parameter Validation Guard**
```python
from backend.explainability.guardrails import GuardRails, Constraint

parameter_guard = GuardRails()
parameter_guard.add_constraint(
    Constraint(
        name="confidence_threshold_sanity",
        validator="value_in_range",
        parameters={"min": 0.0, "max": 0.9},  # Cap at 90%
        fail_action="reject",
        message="Threshold cannot exceed 0.9 (current model max confidence is ~0.93)"
    )
)

# Before applying parameter change:
result = parameter_guard.validate({"confidence_threshold": 0.95})
if not result.passed:
    print(f"❌ Blocked: {result.violations[0].message}")
    # Prevents the bad configuration from being applied!
```

**Solution 2: Make Error Recoverable with Rollback**
```python
try:
    validation_result = validator.validate(extraction_output)
except ValidationError as e:
    if "threshold" in str(e).lower():
        # Record rollback event
        recorder.add_trace_event(task_id, TraceEvent(
            event_type=EventType.ROLLBACK,
            agent_id="workflow-orchestrator",
            metadata={
                "rollback_reason": "Threshold error - attempting recovery",
                "rollback_to_checkpoint": "chk-001",
                "recovery_action": "Restore original confidence_threshold=0.8"
            }
        ))

        # Restore parameter and retry
        confidence_threshold = 0.8
        validation_result = validator.validate(extraction_output)
```

---

## Part 6: Using the BlackBox Recorder (API Guide)

### Initialization

```python
from pathlib import Path
from backend.explainability.black_box import BlackBoxRecorder

recorder = BlackBoxRecorder(
    workflow_id="my-workflow-001",  # Unique workflow identifier
    storage_path=Path("cache/")     # Where recordings are stored
)
```

**What happens:**
- Creates directory: `cache/black_box_recordings/my-workflow-001/`
- Initializes in-memory stores for current session
- Ready to start recording

### Recording Data

**1. Record the Task Plan (Before Execution)**
```python
from backend.explainability.black_box import TaskPlan, PlanStep

plan = TaskPlan(
    plan_id="plan-001",
    task_id="my-task",
    steps=[
        PlanStep(step_id="step-1", description="Extract data", agent_id="agent-1", order=1),
        PlanStep(step_id="step-2", description="Validate data", agent_id="agent-2", order=2)
    ],
    dependencies={"step-2": ["step-1"]},
    rollback_points=["step-1"]
)

recorder.record_task_plan("my-task", plan)
```

**2. Record Collaborating Agents**
```python
from backend.explainability.black_box import AgentInfo
from datetime import datetime, UTC

agents = [
    AgentInfo(
        agent_id="agent-1",
        agent_name="Data Extractor",
        role="extraction",
        joined_at=datetime.now(UTC),
        capabilities=["pdf_parsing", "ocr"]
    ),
    AgentInfo(
        agent_id="agent-2",
        agent_name="Data Validator",
        role="validation",
        joined_at=datetime.now(UTC),
        capabilities=["schema_validation", "duplicate_check"]
    )
]

recorder.record_collaborators("my-task", agents)
```

**3. Record Parameter Changes**
```python
recorder.record_parameter_substitution(
    task_id="my-task",
    param="max_retries",
    old_val=3,
    new_val=5,
    reason="Increased for flaky external API",
    agent_id="agent-1"
)
```

**4. Record Execution Events**
```python
from backend.explainability.black_box import TraceEvent, EventType
from datetime import datetime, UTC

# Step starts
recorder.add_trace_event("my-task", TraceEvent(
    event_id="evt-001",
    event_type=EventType.STEP_START,
    agent_id="agent-1",
    step_id="step-1",
    metadata={"input_size": 1024}
))

# Agent makes a decision
recorder.add_trace_event("my-task", TraceEvent(
    event_id="evt-002",
    event_type=EventType.DECISION,
    agent_id="agent-1",
    step_id="step-1",
    metadata={
        "decision": "Use OCR for handwritten text",
        "alternatives": ["Rule-based extraction", "Skip section"],
        "reasoning": "Detected handwritten notes in margin"
    }
))

# Checkpoint saved
recorder.add_trace_event("my-task", TraceEvent(
    event_id="evt-003",
    event_type=EventType.CHECKPOINT,
    agent_id="agent-1",
    step_id="step-1",
    metadata={
        "checkpoint_id": "chk-001",
        "state": {"pages_processed": 5, "partial_data": {...}}
    }
))

# Step completes
recorder.add_trace_event("my-task", TraceEvent(
    event_id="evt-004",
    event_type=EventType.STEP_END,
    agent_id="agent-1",
    step_id="step-1",
    duration_ms=3500,
    input_hash=BlackBoxRecorder.compute_hash(input_data),
    output_hash=BlackBoxRecorder.compute_hash(output_data),
    metadata={"success": True}
))
```

### Exporting and Replaying

**Export to Single File**
```python
recorder.export_black_box(
    "my-task",
    Path("incidents/my-task-blackbox.json")
)
```

**Replay Events Chronologically**
```python
for event in recorder.replay("my-task"):
    print(f"[{event.timestamp}] {event.event_type}: {event.data}")
```

### Retrieving Specific Data

```python
# Get task plan
plan = recorder.get_task_plan("my-task")
print(f"Plan has {len(plan.steps)} steps")

# Get collaborators
agents = recorder.get_collaborators("my-task")
print(f"Agents: {[a.agent_name for a in agents]}")

# Get execution trace
trace = recorder.get_execution_trace("my-task")
print(f"Final outcome: {trace.final_outcome}")
print(f"Total events: {len(trace.events)}")
```

---

## Part 7: Best Practices

### When to Create Checkpoints

**✅ DO checkpoint:**
- After expensive operations (API calls, LLM inference)
- Before risky operations (external service calls)
- At workflow phase boundaries (extraction → validation)
- After parameter changes
- After each step in short workflows (<5 steps)

**❌ DON'T checkpoint:**
- Every few seconds (storage bloat)
- During atomic operations (partial state is useless)
- When state is invalid (would checkpoint an error)
- Every iteration of loops (use summary checkpoints instead)

### Rollback Point Placement

**✅ Safe rollback points:**
- After database READ operations
- After idempotent WRITE operations (upserts)
- Before external API calls
- At consistent state boundaries (transaction commits)

**❌ Unsafe rollback points:**
- After non-idempotent WRITE operations (might duplicate)
- Mid-transaction (partial state)
- After payment operations (might double-charge)

### Storage Management

**Retention Policy Example:**
- **Failed workflows**: Keep 90 days (need for investigation)
- **Successful workflows**: Keep 7 days (enough for spot checks)
- **Compliance-critical**: Keep 7 years (regulatory requirement)

**Storage Optimization:**
- Compress old recordings with gzip (70-80% reduction)
- Archive to cheaper storage (S3 Glacier) after 30 days
- Sample successful workflows if >1000/day

---

## Part 8: Key Takeaways

### What Makes BlackBox Powerful

1. **Complete Chronicle**: Every decision, parameter change, and event captured
2. **Chronological Replay**: Understand exactly what happened, in order
3. **Root Cause Clarity**: Parameter changes linked to errors with timestamps
4. **Compliance Ready**: Tamper-evident audit trails with SHA256 hashes
5. **Fast Debugging**: Minutes to root cause instead of hours

### Real-World Benefits

| Before BlackBox | After BlackBox |
|-----------------|----------------|
| ❓ "Which step failed?" | ✅ See exact step in timeline |
| ❓ "Did config change?" | ✅ All parameter changes logged with justification |
| ❓ "Can we reproduce?" | ✅ Export recording, replay anywhere |
| ⏱️ Hours to debug | ⏱️ Minutes to root cause |
| 🤔 Guessing from logs | 📊 Data-driven investigation |

### When to Use BlackBox

**Essential for:**
- Production multi-agent systems
- Compliance-regulated workflows (healthcare, finance)
- High-stakes decisions (financial approval, medical diagnosis)
- Complex debugging scenarios (cascade failures)

**Optional for:**
- Simple single-agent tasks
- Development/testing environments
- Workflows with full external logging

---

## Summary: The BlackBox Mental Model

Think of the BlackBox Recorder as your multi-agent workflow's **comprehensive flight recorder**:

1. **Before takeoff** (initialization):
   - Define flight plan → `TaskPlan`
   - List crew → `AgentInfo`

2. **During flight** (execution):
   - Record all instrument readings → `TraceEvent` (STEP_START, STEP_END)
   - Record all crew decisions → `TraceEvent` (DECISION)
   - Record any control changes → `ParameterSubstitution`
   - Save state snapshots → `TraceEvent` (CHECKPOINT)
   - Log any problems → `TraceEvent` (ERROR)

3. **After landing/crash** (investigation):
   - Export complete recording → `export_black_box()`
   - Replay in chronological order → `replay()`
   - Identify root cause → Compare plan vs. trace, find parameter changes
   - Implement fixes → Add guards, improve rollback

Just like aviation accident investigators can reconstruct every moment of a flight, you can reconstruct every moment of your AI workflow—making debugging systematic, data-driven, and fast.

---

## References

- **Implementation**: `lesson-17/backend/explainability/black_box.py`
- **Tutorial**: `lesson-17/tutorials/02_black_box_recording_debugging.md`
- **Interactive Demo**: `lesson-17/notebooks/01_black_box_recording_demo.ipynb`
- **Storage Location**: `lesson-17/cache/black_box_recordings/`
