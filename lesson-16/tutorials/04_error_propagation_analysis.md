# Tutorial 04: Error Propagation Analysis

**Estimated Reading Time:** 18 minutes
**Prerequisites:**
- **Tutorial 01: Agent Reliability Fundamentals** (understanding of FR2.2 cascade failures)
- **Tutorial 03: Deterministic Execution Strategies** (recommended - validation gates)
- Basic understanding of multi-agent workflows
- Familiarity with error handling concepts

**Learning Objectives:**
- Understand cascade failure mechanics and how errors amplify through workflows
- Calculate Error Propagation Index (EPI) to measure failure impact
- Apply isolation techniques using Result[T,E] types to contain errors
- Distinguish between critical and optional agents for fault tolerance
- Implement early termination strategies to prevent cascade propagation
- Design isolation boundaries for production agent systems

**Related Resources:**
- **Previous Tutorial:** [Tutorial 03: Deterministic Execution Strategies](03_deterministic_execution_strategies.md)
- **Next Tutorial:** [Tutorial 05: AgentArch Benchmark Methodology](05_agentarch_benchmark_methodology.md)
- **Interactive Notebooks:**
  - [Notebook 13: Reliability Framework Implementation](../notebooks/13_reliability_framework_implementation.ipynb) - Hands-on error isolation demo
- **Backend Code:**
  - `backend/reliability/isolation.py:1-173` - Result[T,E] type and safe_agent_call implementation
  - `backend/orchestrators/hierarchical.py` - Error isolation in hierarchical delegation
- **Diagrams:**
  - Error Propagation Cascade (to be created in Task 6.8) - Sequence diagram showing cascade failure

---

## Table of Contents
1. [Introduction](#introduction)
2. [Core Concepts](#core-concepts)
3. [Cascade Failure Mechanics](#cascade-failure-mechanics)
4. [Error Propagation Index (EPI)](#error-propagation-index-epi)
5. [Isolation Technique 1: Result Types](#isolation-technique-1-result-types)
6. [Isolation Technique 2: Critical vs Optional Agents](#isolation-technique-2-critical-vs-optional-agents)
7. [Early Termination Strategies](#early-termination-strategies)
8. [Designing Isolation Boundaries](#designing-isolation-boundaries)
9. [Common Pitfalls](#common-pitfalls)
10. [Hands-On Exercises](#hands-on-exercises)
11. [Summary](#summary)
12. [Further Reading](#further-reading)

---

## Introduction

**What you'll learn:**
This tutorial explores how errors propagate through multi-agent workflows, amplifying from single-point failures into cascading system-wide breakdowns. You'll learn quantitative methods to measure propagation (Error Propagation Index), isolation techniques to contain failures (Result types, critical/optional agent distinction), and early termination strategies to prevent cascade amplification.

**Why this matters:**
A single hallucination in a 5-agent workflow can trigger 4 downstream errors, degrading end-to-end success from 95% (one agent) to 77% (five agents chained without isolation). Consider this production scenario:

**Without error isolation (cascade failure):**
```
Step 1: Extract vendor → "ACME" (hallucination, should be "Acme Corp") ❌
Step 2: Validate vendor → Database lookup fails (no "ACME") ❌
Step 3: Categorize expense → Uses "Unknown Vendor" category (wrong) ❌
Step 4: Calculate tax → Wrong jurisdiction (wrong category) ❌
Step 5: Route approval → Wrong manager (wrong department) ❌

Result: 1 upstream error → 4 downstream errors → EPI = 4.0
Total failure: All 5 agents produce incorrect outputs
```

**With error isolation (contained failure):**
```
Step 1: Extract vendor → "ACME" (hallucination)
Step 2: Validate vendor → Database lookup fails
         → Validation gate catches error
         → Early termination triggered ✓
         → Error logged with context
         → Human review flagged

Result: 1 upstream error → 0 downstream errors → EPI = 0.0
Controlled failure: Error contained, downstream agents never execute with bad data
```

**Real-world impact:**
A financial services company deploys an invoice processing workflow without error isolation. Over 30 days:
- **Day 1:** 92% success rate (50 invoices/day)
- **Day 15:** 85% success rate (volume increases to 200 invoices/day)
- **Day 30:** 73% success rate (same code, same prompts, statistical failures exposed at scale)

**Root cause analysis reveals:**
- 15% of failures are upstream hallucinations (Step 1 extraction errors)
- 85% of failures are cascade effects (Steps 2-5 failing due to corrupted inputs from Step 1)
- **Error Propagation Index: 5.67** (average 5.67 downstream errors per upstream failure)

After implementing error isolation (Result types, validation gates, early termination):
- **Day 31:** 94% success rate
- **Day 45:** 96% success rate (stable at scale)
- **Error Propagation Index: 0.3** (most failures contained before propagation)

This tutorial teaches you to build the second system—one that fails gracefully, contains errors, and maintains reliability at scale.

---

## Core Concepts

### Concept 1: Error Propagation in Multi-Agent Systems

**Definition:**
**Error propagation** is the process by which an error in one agent (upstream) causes failures in subsequent agents (downstream) that depend on its output. Propagation occurs when downstream agents:
1. **Accept invalid inputs without validation** (no guardrails)
2. **Process corrupted data as if valid** (silent corruption)
3. **Amplify errors through compounding inaccuracies** (multiplicative degradation)

**Key characteristics:**
- **Spatial propagation:** Errors spread across agents in the workflow
- **Temporal propagation:** Errors persist across workflow steps
- **Amplification:** One error triggers multiple downstream failures
- **Latency:** Observable symptoms appear far from root cause

**Example: Invoice Processing Cascade**

```python
# 5-agent sequential workflow without isolation
async def invoice_workflow_no_isolation(invoice_text: str) -> dict:
    """Process invoice through 5 agents (NO ERROR ISOLATION)."""

    # Step 1: Extract vendor name
    vendor = await extract_vendor(invoice_text)
    # Output: "ACME" (hallucination - should be "Acme Corp")

    # Step 2: Validate vendor against database
    vendor_id = await lookup_vendor(vendor)
    # Input: "ACME" (invalid)
    # Output: None (lookup failed, no "ACME" in database)
    # Error: Agent2 fails but workflow continues

    # Step 3: Categorize expense
    category = await categorize_expense(vendor_id)
    # Input: None (corrupted from Step 2)
    # Output: "Unknown" (wrong category, should be "Office Supplies")
    # Error: Agent3 produces wrong output due to corrupted input

    # Step 4: Calculate tax jurisdiction
    tax_rate = await calculate_tax(category)
    # Input: "Unknown" (corrupted from Step 3)
    # Output: 0.05 (wrong rate, should be 0.08 for "Office Supplies")
    # Error: Agent4 produces wrong output due to corrupted input

    # Step 5: Route for approval
    approver = await route_approval(vendor_id, category)
    # Input: None, "Unknown" (both corrupted)
    # Output: "Default Manager" (wrong approver)
    # Error: Agent5 produces wrong output due to corrupted inputs

    return {
        "vendor": vendor,           # ❌ Wrong
        "vendor_id": vendor_id,     # ❌ Wrong (None)
        "category": category,       # ❌ Wrong
        "tax_rate": tax_rate,       # ❌ Wrong
        "approver": approver,       # ❌ Wrong
    }
    # Final result: 5/5 fields incorrect due to cascade from Step 1
```

**Propagation path visualization:**

```
Agent1 ──[ACME]──> Agent2 ──[None]──> Agent3 ──[Unknown]──> Agent4 ──[0.05]──> Agent5
 ❌ Hallucination    ❌ Lookup fail    ❌ Wrong category   ❌ Wrong tax     ❌ Wrong approver

Error count: 1 + 1 + 1 + 1 + 1 = 5 total errors
Root cause: 1 error (Agent1 hallucination)
Cascaded errors: 4 errors (Agents 2-5 failed due to propagation)
Error Propagation Index (EPI) = 4 cascaded / 1 root cause = 4.0
```

**Why this matters:**
Without isolation, debugging becomes exponentially complex. You observe "wrong approver" (symptom at Step 5) but root cause is "vendor hallucination" (5 steps upstream). Traditional stack traces don't help—the error is data corruption, not code exceptions.

---

### Concept 2: Error Propagation Index (EPI)

**Definition:**
The **Error Propagation Index (EPI)** is a metric that quantifies how many downstream errors result from one upstream failure. It measures the **amplification effect** of cascade failures.

**Formula:**
```
EPI = (Total Errors - Root Cause Errors) / Root Cause Errors
    = Cascaded Errors / Root Cause Errors
```

**Interpretation:**
- **EPI = 0.0:** Perfect isolation (no propagation)
- **EPI = 1.0:** Each upstream error causes 1 downstream error
- **EPI = 4.0:** Each upstream error causes 4 downstream errors (5× total errors)
- **EPI > 5.0:** Severe cascade amplification (systemic failure)

**Example calculations:**

**Scenario 1: No isolation (sequential workflow, 5 agents)**
```
Workflow execution on 100 invoices:
- 10 extraction errors (Agent1 hallucinations)
- Each extraction error causes 4 downstream failures (Agents 2-5)
- Total errors: 10 root + (10 × 4 cascaded) = 50 errors

EPI = (50 - 10) / 10 = 40 / 10 = 4.0

Interpretation: Each upstream error cascades to 4 downstream errors
```

**Scenario 2: Validation gates (early termination after Agent1)**
```
Workflow execution on 100 invoices:
- 10 extraction errors (Agent1 hallucinations)
- Validation gate catches all errors → early termination
- Downstream agents never execute with invalid inputs
- Total errors: 10 root + 0 cascaded = 10 errors

EPI = (10 - 10) / 10 = 0 / 10 = 0.0

Interpretation: Zero propagation, perfect isolation
```

**Scenario 3: Partial isolation (critical agents fail-fast, optional agents continue)**
```
Workflow execution on 100 invoices:
- 10 vendor extraction errors (Agent1)
- 5 reach Agent2 (validation), fail-fast terminates 5 workflows
- 5 reach Agent3 (categorization - optional), produce degraded results
- Total errors: 10 root + 5 partial propagation = 15 errors

EPI = (15 - 10) / 10 = 5 / 10 = 0.5

Interpretation: 50% propagation, partial isolation
```

**Why EPI matters:**
EPI is a **success metric** for isolation effectiveness:
- Track EPI over time to detect degradation in error isolation
- Compare orchestration patterns by EPI (voting EPI ~0.3, sequential EPI ~4.0)
- Set reliability targets: "Reduce EPI from 4.0 to <0.5 by implementing validation gates"

**AgentArch Benchmark EPI targets (from FR5.3):**
- Sequential: EPI ~3.2 (poor isolation)
- Hierarchical: EPI ~1.8 (moderate isolation through parallel execution)
- Iterative: EPI ~1.2 (iterative refinement catches errors)
- State Machine: **EPI ~0.4** (validation on state transitions)
- Voting: **EPI ~0.3** (consensus filters errors)

---

### Concept 3: Isolation Boundaries

**Definition:**
An **isolation boundary** is an architectural decision point where you contain errors to prevent propagation. Isolation boundaries are implemented through:
1. **Validation gates:** Check outputs before passing to next agent
2. **Exception handlers:** Catch and contain errors without crashing
3. **Result types:** Explicit success/failure values instead of exceptions
4. **Critical/optional distinction:** Fail-fast for critical, degrade gracefully for optional

**Isolation boundary placement strategies:**

**Strategy 1: After every agent (maximum isolation, high overhead)**
```python
# Validation gate after each step
vendor = await extract_vendor(invoice_text)
validate_vendor(vendor)  # Boundary 1

vendor_id = await lookup_vendor(vendor)
validate_vendor_id(vendor_id)  # Boundary 2

category = await categorize_expense(vendor_id)
validate_category(category)  # Boundary 3
# ... and so on

# Pros: EPI ≈ 0.0 (zero propagation)
# Cons: Latency overhead, complex validation logic for every step
```

**Strategy 2: After critical agents only (balanced isolation/performance)**
```python
# Validation gates only for critical agents
vendor = await extract_vendor(invoice_text)
validate_vendor(vendor)  # Boundary 1: Critical (blocks workflow)

vendor_id = await lookup_vendor(vendor)
validate_vendor_id(vendor_id)  # Boundary 2: Critical (blocks workflow)

# No validation for optional agents (allow degradation)
category = await categorize_expense(vendor_id)  # Optional
tax_rate = await calculate_tax(category)        # Optional
approver = await route_approval(vendor_id, category)  # Critical
validate_approver(approver)  # Boundary 3

# Pros: Balanced EPI ~0.5, lower overhead
# Cons: Optional agents may still propagate errors to each other
```

**Strategy 3: At workflow boundaries only (minimal isolation)**
```python
# Validation only at workflow entry/exit
validate_input(invoice_text)  # Boundary 1: Entry

# No intermediate validation (agents propagate errors freely)
result = await full_workflow(invoice_text)

validate_output(result)  # Boundary 2: Exit

# Pros: Minimal overhead
# Cons: High EPI ~4.0, errors propagate through entire workflow
```

**Best practice:** Use **Strategy 2** (critical agents only) for production systems. Identify critical agents (where failure is unacceptable) and place validation boundaries immediately after them.

---

## Cascade Failure Mechanics

### How Errors Amplify Through Workflows

**Mechanism 1: Data Corruption Propagation**

When Agent N produces invalid output, Agent N+1 receives corrupted input and may:
1. **Crash** (exception thrown, workflow terminates)
2. **Produce garbage output** (invalid input → invalid output)
3. **Hallucinate** (LLM "fills in" missing data with invented values)

**Example:**

```python
# Agent1: Extract invoice amount
amount_str = await extract_amount(invoice_text)
# Output: "1,234.56" (string with comma - should be 1234.56 float)

# Agent2: Calculate tax (expects float)
tax = await calculate_tax(float(amount_str))
# ValueError: could not convert string to float: '1,234.56'
# Workflow crashes → cascade failure
```

**Mechanism 2: Multiplicative Accuracy Degradation**

When agents are chained, accuracy multiplies:
- Agent1: 95% accurate
- Agent2: 95% accurate (depends on Agent1 output)
- Agent3: 95% accurate (depends on Agent2 output)

**End-to-end accuracy:**
```
P(all correct) = 0.95 × 0.95 × 0.95 = 0.857 = 85.7%
Error rate = 1 - 0.857 = 14.3%
```

Chaining 5 agents at 95% each:
```
P(all correct) = 0.95^5 = 0.774 = 77.4%
Error rate = 22.6% (nearly 1 in 4 workflows fail)
```

**With 100% isolation** (errors don't propagate):
```
P(workflow succeeds) = 1 - P(any agent fails without recovery)
If we can retry or fallback, success rate → 95%+ even with failures
```

**Mechanism 3: Hidden Corruption (Silent Failures)**

Most dangerous: Agent N fails but produces plausible-looking output that downstream agents accept.

**Example:**

```python
# Agent1: Extract vendor name
vendor = await extract_vendor(invoice_text)
# Correct: "Acme Corporation"
# Hallucination: "Acme Corp" (close but not exact)

# Agent2: Lookup vendor ID in database
vendor_id = await lookup_vendor(vendor)
# Database has "Acme Corporation" but not "Acme Corp"
# Output: None (lookup failed)
# Silent failure: No exception raised, workflow continues with None

# Agent3: Get vendor payment terms
payment_terms = await get_payment_terms(vendor_id)
# Input: None
# LLM hallucinates: "Net 30" (default assumption, may be wrong)
# Silent failure: Plausible output, but incorrect

# Result: Invoice processed with wrong payment terms
# Discovered 60 days later when payment overdue
# Debugging nightmare: No logs indicate failure
```

**Prevention:** Always validate outputs against schemas (Tutorial 03) and use explicit Result types instead of None values.

---

### Cascade Failure Case Study: 5-Agent Invoice Workflow

**Workflow architecture:**
1. **Agent1 (Extractor):** Parse invoice PDF, extract vendor/amount/date
2. **Agent2 (Validator):** Check vendor exists in database
3. **Agent3 (Categorizer):** Assign expense category based on vendor
4. **Agent4 (Tax Calculator):** Calculate tax based on category + jurisdiction
5. **Agent5 (Router):** Route to appropriate approver based on amount + category

**Failure scenario trace:**

```
📄 Input: Invoice PDF from "Acme Corporation" for $1,234.56

Step 1: Agent1 (Extractor)
├─ Input: Raw PDF text
├─ LLM call: "Extract vendor, amount, date as JSON"
├─ Output: {"vendor": "ACME", "amount": 1234.56, "date": "2024-01-15"}
└─ ❌ ERROR: Vendor hallucination ("ACME" vs "Acme Corporation")

Step 2: Agent2 (Validator)
├─ Input: {"vendor": "ACME", ...}
├─ Database query: SELECT id FROM vendors WHERE name = 'ACME'
├─ Query result: None (no match)
└─ ❌ ERROR: Validation failed (propagated from Step 1)

Step 3: Agent3 (Categorizer)
├─ Input: {"vendor_id": None, ...}
├─ LLM call: "Categorize expense for unknown vendor"
├─ Output: {"category": "Miscellaneous"}
└─ ❌ ERROR: Wrong category (should be "Office Supplies", propagated from Step 2)

Step 4: Agent4 (Tax Calculator)
├─ Input: {"category": "Miscellaneous", ...}
├─ Tax lookup: Miscellaneous → 5% tax rate
├─ Output: {"tax": 61.73, "tax_rate": 0.05}
└─ ❌ ERROR: Wrong tax (should be 8% for Office Supplies = $98.76, propagated from Step 3)

Step 5: Agent5 (Router)
├─ Input: {"category": "Miscellaneous", "amount": 1234.56, ...}
├─ Routing logic: Miscellaneous < $5K → route to "General Manager"
├─ Output: {"approver": "General Manager"}
└─ ❌ ERROR: Wrong approver (should be "Purchasing Manager" for Office Supplies, propagated from Step 3)

📊 Final Result:
- Total errors: 5
- Root cause errors: 1 (Agent1 hallucination)
- Cascaded errors: 4 (Agents 2-5)
- Error Propagation Index: 4.0
- End-to-end success: ❌ FAIL (all 5 outputs incorrect)
```

**Error trace diagram:**

```
Agent1     Agent2         Agent3           Agent4          Agent5
[Extract] → [Validate] → [Categorize] → [Tax Calc] → [Route]
    ↓           ↓              ↓              ↓            ↓
  "ACME"      None      "Miscellaneous"   5% tax    "General Mgr"
    ❌          ❌             ❌              ❌            ❌
   Root     Cascade 1      Cascade 2     Cascade 3    Cascade 4
```

**Impact:**
- Invoice processed with wrong tax calculation ($37 underpayment)
- Routed to wrong approver (3-day delay)
- Compliance violation (wrong expense category in audit trail)
- Discovered only when vendor disputes payment

**Cost of cascade failure:**
- Financial: $37 tax underpayment
- Operational: 8 hours manual investigation
- Compliance: Audit flag requiring remediation

---

## Error Propagation Index (EPI)

### Calculating EPI: Step-by-Step

**Formula:**
```
EPI = (Total Errors - Root Cause Errors) / Root Cause Errors
```

**Step 1: Trace workflow execution and identify all errors**

Example from 100-invoice batch:
```
Invoice #1: Agent1 fails (extraction), Agents 2-5 cascade → 5 errors
Invoice #2: Agent1 fails, Agents 2-5 cascade → 5 errors
Invoice #3: Success → 0 errors
...
Invoice #23: Agent3 fails (categorization), Agents 4-5 cascade → 3 errors
...
Total errors across 100 invoices: 150 errors
```

**Step 2: Classify errors as root cause vs cascaded**

Root cause errors (agents that failed due to their own logic, not bad inputs):
- Invoice #1: Agent1 failure (root)
- Invoice #2: Agent1 failure (root)
- Invoice #23: Agent3 failure (root)
- ...
- Total root cause errors: 30

Cascaded errors (agents that failed due to bad inputs from upstream):
- Invoice #1: Agent2, Agent3, Agent4, Agent5 failures (4 cascaded)
- Invoice #2: Agent2, Agent3, Agent4, Agent5 failures (4 cascaded)
- Invoice #23: Agent4, Agent5 failures (2 cascaded)
- ...
- Total cascaded errors: 150 - 30 = 120

**Step 3: Calculate EPI**

```
EPI = 120 cascaded / 30 root cause = 4.0
```

**Interpretation:** On average, each root cause error triggers 4 downstream failures.

---

### EPI Across Orchestration Patterns

Different orchestration patterns have different EPI characteristics:

**Sequential Orchestration (worst EPI):**
```
Agent1 → Agent2 → Agent3 → Agent4 → Agent5
EPI ~3.2-4.0
Reason: Linear chain maximizes propagation distance
```

**Hierarchical Delegation (better EPI):**
```
         Planner
          /  |  \
    Agent1 Agent2 Agent3 (parallel)
EPI ~1.8
Reason: Parallel specialists isolated from each other
```

**State Machine (best EPI for validation-heavy workflows):**
```
State1 → [Validate] → State2 → [Validate] → State3
EPI ~0.4
Reason: Validation gates on every state transition
```

**Voting/Ensemble (best EPI for high-reliability):**
```
Agent1 ──┐
Agent2 ──┼──> Consensus Vote
Agent3 ──┘
EPI ~0.3
Reason: Majority vote filters outlier errors
```

**When to optimize for low EPI:**
- Financial workflows (errors = monetary loss)
- Compliance-critical systems (errors = audit failures)
- High-volume processing (errors compound at scale)

**When EPI matters less:**
- Prototype/exploratory systems
- Low-stakes workflows (errors easily corrected)
- Single-use workflows (not production scale)

---

## Isolation Technique 1: Result Types

### The Result[T, E] Pattern

**Problem with exceptions:**
Traditional Python exception handling doesn't isolate errors well in async agent workflows:

```python
# Exceptions crash the orchestrator
async def orchestrator(invoices):
    for invoice in invoices:
        vendor = await extract_vendor(invoice)  # Raises exception
        # Orchestrator crashes, remaining invoices never processed
```

**Solution: Result[T, E] type** (from `backend/reliability/isolation.py:32-131`)

Result type represents explicit success/failure values instead of throwing exceptions:

```python
from typing import Generic, TypeVar

T = TypeVar("T")  # Success type
E = TypeVar("E", bound=Exception)  # Error type

class Result(Generic[T, E]):
    """Result type representing either Success or Failure."""

    def __init__(self, value: T | None = None, error: E | None = None):
        if (value is None and error is None) or (value is not None and error is not None):
            raise ValueError("Result must have exactly one of value or error")
        self.value = value
        self.error = error

    @classmethod
    def success(cls, value: T) -> "Result[T, E]":
        """Create a Success result."""
        return cls(value=value, error=None)

    @classmethod
    def failure(cls, error: E) -> "Result[T, E]":
        """Create a Failure result."""
        return cls(value=None, error=error)

    def is_success(self) -> bool:
        """Check if result is success."""
        return self.error is None

    def is_failure(self) -> bool:
        """Check if result is failure."""
        return self.error is not None

    def unwrap(self) -> T:
        """Unwrap success value or raise if failure."""
        if self.is_failure():
            raise ValueError(f"Cannot unwrap Failure: {self.error}")
        return self.value

    def unwrap_or(self, default: T) -> T:
        """Unwrap success value or return default if failure."""
        return self.value if self.is_success() else default
```

**Usage in agent workflows:**

```python
# Wrap agent calls to return Result instead of raising exceptions
async def safe_agent_call(
    agent: Any,
    agent_name: str,
    input_data: dict[str, Any],
) -> Result[Any, Exception]:
    """Call agent with exception isolation."""
    try:
        output = await agent(input_data)
        return Result.success(output)
    except Exception as e:
        # Isolate the exception - don't let it propagate
        return Result.failure(e)
```

**Orchestrator with Result-based isolation:**

```python
async def orchestrator_with_isolation(invoices: list[str]) -> dict:
    """Process invoices with error isolation using Result types."""
    results = []
    errors = []

    for invoice in invoices:
        # Step 1: Extract vendor (isolated)
        vendor_result = await safe_agent_call(extract_vendor, "extractor", {"text": invoice})

        if vendor_result.is_failure():
            # Log error and continue to next invoice (no cascade)
            errors.append({"step": "extraction", "error": vendor_result.error})
            continue  # Early termination prevents cascade

        vendor = vendor_result.unwrap()

        # Step 2: Validate vendor (isolated)
        validation_result = await safe_agent_call(validate_vendor, "validator", {"vendor": vendor})

        if validation_result.is_failure():
            errors.append({"step": "validation", "error": validation_result.error})
            continue  # Early termination

        # Continue processing only if all critical steps succeed
        results.append({"vendor": vendor, "status": "success"})

    return {
        "success_count": len(results),
        "error_count": len(errors),
        "error_propagation_index": 0.0,  # Zero propagation with isolation
    }
```

**Benefits of Result types:**
- ✅ Errors are explicit values, not control flow (no hidden exceptions)
- ✅ Orchestrator doesn't crash when agents fail
- ✅ Type-safe error handling (TypeScript/Rust style in Python)
- ✅ Forces explicit error handling at every step
- ✅ Easy to log/aggregate errors for analysis

**Implementation in backend** (`backend/reliability/isolation.py:133-173`):

```python
async def safe_agent_call(
    agent: Any,
    agent_name: str,
    input_data: dict[str, Any],
    **kwargs: Any,
) -> Result[Any, Exception]:
    """Call agent with exception isolation.

    Example:
        >>> result = await safe_agent_call(validator_agent, "validator", {"invoice": data})
        >>> if result.is_success():
        ...     validated_data = result.unwrap()
        ... else:
        ...     logger.error(f"Validator failed: {result.error}")
    """
    # Type checking (defensive)
    if not isinstance(agent_name, str):
        raise TypeError("agent_name must be a string")
    if not isinstance(input_data, dict):
        raise TypeError("input_data must be a dict")

    # Try to call agent with exception isolation
    try:
        output = await agent(input_data, **kwargs)
        return Result.success(output)
    except Exception as e:
        # Isolate the exception - don't let it propagate
        return Result.failure(e)
```

---

## Isolation Technique 2: Critical vs Optional Agents

### Agent Classification Strategy

Not all agent failures are equally severe. **Critical agents** must succeed for the workflow to be valid, while **optional agents** can fail without invalidating the result (degraded quality is acceptable).

**Critical agents (fail-fast):**
- Failures block workflow progression
- Early termination triggered on failure
- Examples: extraction, validation, database lookups, payment authorization

**Optional agents (degrade gracefully):**
- Failures logged but workflow continues
- Degraded output acceptable (lower quality than ideal)
- Examples: categorization, enrichment, recommendations, summaries

**Example classification for invoice workflow:**

| Agent | Type | Failure Impact | Strategy |
|-------|------|----------------|----------|
| Extract vendor | Critical | Cannot process invoice without vendor | Fail-fast |
| Validate vendor | Critical | Wrong vendor = wrong payment account | Fail-fast |
| Extract amount | Critical | Cannot approve without amount | Fail-fast |
| Categorize expense | Optional | Wrong category = reporting inconvenience | Degrade |
| Calculate tax | Critical | Wrong tax = compliance violation | Fail-fast |
| Enrich with PO | Optional | Missing PO = manual lookup later | Degrade |
| Route approval | Critical | Wrong approver = unauthorized approval | Fail-fast |

**Implementation:**

```python
from enum import Enum

class AgentCriticality(Enum):
    CRITICAL = "critical"
    OPTIONAL = "optional"

async def orchestrator_with_criticality(invoice: dict) -> dict:
    """Orchestrator with critical/optional agent distinction."""
    result = {"status": "processing"}

    # Step 1: Extract vendor (CRITICAL)
    vendor_result = await safe_agent_call(extract_vendor, "extractor", invoice)
    if vendor_result.is_failure():
        # Critical failure - terminate workflow
        return {"status": "failed", "reason": "vendor_extraction_failed", "error": str(vendor_result.error)}
    result["vendor"] = vendor_result.unwrap()

    # Step 2: Validate vendor (CRITICAL)
    validation_result = await safe_agent_call(validate_vendor, "validator", result)
    if validation_result.is_failure():
        # Critical failure - terminate workflow
        return {"status": "failed", "reason": "vendor_validation_failed", "error": str(validation_result.error)}
    result["vendor_id"] = validation_result.unwrap()

    # Step 3: Categorize expense (OPTIONAL)
    category_result = await safe_agent_call(categorize_expense, "categorizer", result)
    if category_result.is_success():
        result["category"] = category_result.unwrap()
    else:
        # Optional failure - log and continue with default
        result["category"] = "Uncategorized"
        result["warnings"] = [f"Categorization failed: {category_result.error}"]

    # Step 4: Calculate tax (CRITICAL)
    tax_result = await safe_agent_call(calculate_tax, "tax_calculator", result)
    if tax_result.is_failure():
        # Critical failure - terminate workflow
        return {"status": "failed", "reason": "tax_calculation_failed", "error": str(tax_result.error)}
    result["tax"] = tax_result.unwrap()

    # Step 5: Enrich with PO (OPTIONAL)
    po_result = await safe_agent_call(lookup_po, "po_enricher", result)
    if po_result.is_success():
        result["purchase_order"] = po_result.unwrap()
    else:
        # Optional failure - workflow continues without PO
        result["purchase_order"] = None
        result.setdefault("warnings", []).append(f"PO lookup failed: {po_result.error}")

    result["status"] = "success"
    return result
```

**Error Propagation Index with critical/optional distinction:**

```
100 invoices processed:
- 10 critical failures (extraction/validation) → workflows terminated early
- 15 optional failures (categorization/enrichment) → workflows continue with degraded quality
- EPI calculation:
  - Root cause errors: 10 critical + 15 optional = 25
  - Cascaded errors: 0 (early termination prevents cascade from critical failures)
  - EPI = 0 / 25 = 0.0

Success rate: 90% (10 failed due to critical errors, 90 succeeded)
Degraded quality rate: 15% (some succeeded invoices have missing category/PO)
```

**Design principle:** Classify agents by **business impact of failure**, not technical implementation. Ask: "If this agent fails, is the workflow output still valid?"

---

## Early Termination Strategies

**Strategy 1: Validation Gates (Checkpoint Pattern)**

Place validation gates after critical agents to catch errors before propagation:

```python
async def workflow_with_validation_gates(invoice: dict) -> dict:
    """Workflow with validation gates after each critical agent."""

    # Gate 1: After extraction
    extraction = await extract_vendor(invoice)
    if not validate_extraction_schema(extraction):
        raise ValidationError("Extraction output invalid") # Early termination

    # Gate 2: After database lookup
    vendor_id = await lookup_vendor(extraction["vendor"])
    if vendor_id is None:
        raise ValidationError("Vendor not found in database")  # Early termination

    # Continue only if all gates pass
    return await process_invoice(extraction, vendor_id)
```

**Strategy 2: Circuit Breaker Pattern**

Stop processing after N consecutive failures to prevent resource waste:

```python
from collections import deque

class CircuitBreaker:
    def __init__(self, failure_threshold: int = 5):
        self.failure_threshold = failure_threshold
        self.recent_results = deque(maxlen=failure_threshold)
        self.state = "CLOSED"  # CLOSED = normal, OPEN = stop processing

    def record_result(self, success: bool):
        self.recent_results.append(success)
        if len(self.recent_results) == self.failure_threshold:
            if not any(self.recent_results):
                # All recent attempts failed - open circuit
                self.state = "OPEN"

    def should_allow_call(self) -> bool:
        return self.state == "CLOSED"

# Usage in orchestrator
circuit_breaker = CircuitBreaker(failure_threshold=5)

for invoice in invoices:
    if not circuit_breaker.should_allow_call():
        # Circuit open - stop processing to prevent cascade
        break

    result = await safe_agent_call(extract_vendor, "extractor", invoice)
    circuit_breaker.record_result(result.is_success())
```

**Strategy 3: Adaptive Termination (Cost-Based)**

Terminate if accumulated cost exceeds budget without proportional success:

```python
async def workflow_with_cost_termination(invoices: list[dict], cost_budget: float = 10.0):
    """Terminate early if cost/success ratio exceeds budget."""
    total_cost = 0.0
    success_count = 0

    for invoice in invoices:
        result = await safe_agent_call(extract_vendor, "extractor", invoice)
        total_cost += 0.05  # GPT-4 call cost

        if result.is_success():
            success_count += 1

        # Check if cost efficiency is acceptable
        if total_cost > 1.0:  # After initial warmup
            efficiency = success_count / total_cost if total_cost > 0 else 0
            if efficiency < 5.0:  # Require at least 5 successes per $1
                # Low efficiency - terminate to avoid wasting budget
                break

    return {"processed": success_count, "cost": total_cost}
```

---

## Designing Isolation Boundaries

### Isolation Boundary Design Checklist

**1. Identify critical agents** (where failure is unacceptable)
- Database operations (payment, authorization, compliance)
- External API calls (payment processing, identity verification)
- Business rule validation (amount limits, approval thresholds)

**2. Place validation gates immediately after critical agents**
- Schema validation (Pydantic models from Tutorial 03)
- Business rule validation (amount > 0, confidence in [0, 1])
- Database constraint validation (foreign key exists, unique constraint)

**3. Implement Result types for all agent calls**
- Wrap all agent calls in `safe_agent_call` to return `Result[T, E]`
- Force explicit error handling (no uncaught exceptions)

**4. Define early termination conditions**
- Critical agent failures → immediate workflow termination
- Optional agent failures → log warning, continue with degraded quality
- Circuit breaker threshold → stop processing after N consecutive failures

**5. Log isolation boundaries for debugging**
- Record which boundaries caught errors
- Trace error propagation paths (which agents failed due to upstream errors)
- Calculate EPI to measure isolation effectiveness

**Example: Production-Grade Isolation Boundary Design**

```python
# Isolation boundary implementation for invoice workflow
async def production_invoice_workflow(invoice: dict) -> dict:
    """Production workflow with comprehensive isolation boundaries."""

    # Boundary 1: Input validation
    if not validate_invoice_input(invoice):
        return {"status": "failed", "reason": "invalid_input", "epi": 0.0}

    # Boundary 2: After extraction (CRITICAL)
    extraction_result = await safe_agent_call(extract_vendor, "extractor", invoice)
    if extraction_result.is_failure():
        return {"status": "failed", "reason": "extraction_failed", "epi": 0.0}

    extraction = extraction_result.unwrap()

    # Validate extraction schema (Pydantic)
    try:
        validated_extraction = InvoiceExtraction(**extraction)
    except ValidationError as e:
        return {"status": "failed", "reason": "extraction_schema_invalid", "details": str(e), "epi": 0.0}

    # Boundary 3: After database lookup (CRITICAL)
    vendor_result = await safe_agent_call(lookup_vendor, "db_lookup", {"vendor": validated_extraction.vendor})
    if vendor_result.is_failure():
        return {"status": "failed", "reason": "vendor_lookup_failed", "epi": 0.0}

    # Boundary 4: After categorization (OPTIONAL - degrade gracefully)
    category_result = await safe_agent_call(categorize_expense, "categorizer", {"vendor_id": vendor_result.unwrap()})
    category = category_result.unwrap_or("Uncategorized")  # Default on failure

    # Boundary 5: After tax calculation (CRITICAL)
    tax_result = await safe_agent_call(calculate_tax, "tax_calc", {"category": category, "amount": validated_extraction.amount})
    if tax_result.is_failure():
        return {"status": "failed", "reason": "tax_calculation_failed", "epi": 0.0}

    # Success - all critical boundaries passed
    return {
        "status": "success",
        "vendor": validated_extraction.vendor,
        "vendor_id": vendor_result.unwrap(),
        "category": category,
        "tax": tax_result.unwrap(),
        "epi": 0.0,  # Zero propagation due to isolation boundaries
    }
```

**EPI for this design:** ~0.0 (all failures caught at isolation boundaries before propagation)

---

## Common Pitfalls

### Pitfall 1: Over-Isolating Optional Agents

**Problem:** Treating all agents as critical and terminating on any failure, even for optional enrichment agents.

```python
# ❌ WRONG: Terminate on optional agent failure
category = await categorize_expense(vendor_id)
if category is None:
    raise ValueError("Categorization failed")  # Terminates entire workflow
```

**Solution:** Allow optional agents to fail gracefully:

```python
# ✅ CORRECT: Continue with default for optional agent
category_result = await safe_agent_call(categorize_expense, "categorizer", {"vendor_id": vendor_id})
category = category_result.unwrap_or("Uncategorized")  # Default on failure
```

---

### Pitfall 2: Logging Errors Without Preventing Propagation

**Problem:** Logging errors but passing corrupted data to downstream agents.

```python
# ❌ WRONG: Log error but continue with None value
vendor_id = await lookup_vendor(vendor)
if vendor_id is None:
    logger.error("Vendor lookup failed")
    # Workflow continues with vendor_id=None → cascades to downstream agents
category = await categorize_expense(vendor_id)  # Fails due to None input
```

**Solution:** Log AND terminate early:

```python
# ✅ CORRECT: Log and terminate to prevent cascade
vendor_result = await safe_agent_call(lookup_vendor, "db_lookup", {"vendor": vendor})
if vendor_result.is_failure():
    logger.error(f"Vendor lookup failed: {vendor_result.error}")
    return {"status": "failed", "reason": "vendor_lookup_failed"}  # Early termination
```

---

### Pitfall 3: Ignoring EPI Metrics in Production

**Problem:** Not measuring or monitoring EPI, so isolation degradation goes unnoticed.

**Solution:** Track EPI as a key reliability metric:

```python
# ✅ CORRECT: Calculate and log EPI for monitoring
async def orchestrator_with_epi_tracking(invoices: list[dict]) -> dict:
    root_cause_errors = 0
    total_errors = 0

    for invoice in invoices:
        errors_before = total_errors

        # Process invoice (may generate errors)
        result = await process_invoice(invoice)

        errors_after = total_errors
        errors_in_workflow = errors_after - errors_before

        if errors_in_workflow > 0:
            root_cause_errors += 1  # At least one root cause
            # Remaining errors are cascaded

    cascaded_errors = total_errors - root_cause_errors
    epi = cascaded_errors / root_cause_errors if root_cause_errors > 0 else 0.0

    # Log EPI for monitoring
    logger.info(f"EPI: {epi:.2f}, Root: {root_cause_errors}, Cascaded: {cascaded_errors}")

    return {"epi": epi}
```

---

## Hands-On Exercises

### Exercise 1: Calculate EPI from Workflow Trace

**Scenario:** Given this workflow execution trace for 10 invoices, calculate the Error Propagation Index.

**Trace:**
```
Invoice 1: Agent1 ✓, Agent2 ✓, Agent3 ✓, Agent4 ✓, Agent5 ✓ (success)
Invoice 2: Agent1 ❌, Agent2 ❌, Agent3 ❌, Agent4 ❌, Agent5 ❌ (cascade from Agent1)
Invoice 3: Agent1 ✓, Agent2 ✓, Agent3 ✓, Agent4 ✓, Agent5 ✓ (success)
Invoice 4: Agent1 ✓, Agent2 ✓, Agent3 ❌, Agent4 ❌, Agent5 ❌ (cascade from Agent3)
Invoice 5: Agent1 ✓, Agent2 ✓, Agent3 ✓, Agent4 ✓, Agent5 ✓ (success)
Invoice 6: Agent1 ❌, Agent2 ❌, Agent3 ❌, Agent4 ❌, Agent5 ❌ (cascade from Agent1)
Invoice 7: Agent1 ✓, Agent2 ✓, Agent3 ✓, Agent4 ✓, Agent5 ✓ (success)
Invoice 8: Agent1 ✓, Agent2 ✓, Agent3 ✓, Agent4 ✓, Agent5 ✓ (success)
Invoice 9: Agent1 ✓, Agent2 ❌, Agent3 ❌, Agent4 ❌, Agent5 ❌ (cascade from Agent2)
Invoice 10: Agent1 ✓, Agent2 ✓, Agent3 ✓, Agent4 ✓, Agent5 ✓ (success)
```

**Tasks:**
1. Count total errors
2. Identify root cause errors (first failure in each workflow)
3. Count cascaded errors (failures caused by upstream errors)
4. Calculate EPI using formula: EPI = Cascaded / Root Cause

**Solution template:**
```python
# TODO: Count errors from trace
total_errors = 0
root_cause_errors = 0
cascaded_errors = 0

# Invoice 2: Root=1 (Agent1), Cascaded=4 (Agents 2-5)
# Invoice 4: Root=1 (Agent3), Cascaded=2 (Agents 4-5)
# ... continue for all invoices

epi = cascaded_errors / root_cause_errors if root_cause_errors > 0 else 0.0
print(f"EPI: {epi:.2f}")
```

---

### Exercise 2: Implement Result-Based Isolation

**Scenario:** Refactor this exception-based workflow to use Result types for error isolation.

**Original code (cascades errors):**
```python
async def workflow_without_isolation(invoice: dict) -> dict:
    """Workflow that crashes on any agent failure."""
    vendor = await extract_vendor(invoice)  # Raises exception
    vendor_id = await lookup_vendor(vendor)  # Never executes if extract_vendor fails
    category = await categorize_expense(vendor_id)
    return {"vendor_id": vendor_id, "category": category}
```

**Tasks:**
1. Implement `safe_agent_call` wrapper that returns `Result[T, E]`
2. Refactor workflow to use Result types
3. Add early termination on critical agent failures
4. Calculate EPI (should be 0.0 with proper isolation)

**Solution template:**
```python
async def safe_agent_call(agent, agent_name: str, input_data: dict) -> Result:
    # TODO: Implement Result-based wrapper
    pass

async def workflow_with_isolation(invoice: dict) -> dict:
    """Workflow with Result-based error isolation."""
    # TODO: Call extract_vendor with safe_agent_call
    # TODO: Check if result is success/failure
    # TODO: Terminate early on failure (prevent cascade)
    # TODO: Continue with remaining agents only if critical steps succeed
    pass
```

---

### Exercise 3: Design Isolation Boundaries

**Scenario:** Design isolation boundary placement for this 7-agent financial workflow. Classify each agent as critical/optional and specify where to place validation gates.

**Workflow:**
1. **Extract vendor name** from invoice PDF
2. **Validate vendor exists** in ERP database
3. **Extract invoice amount** from PDF
4. **Categorize expense** based on vendor type
5. **Lookup purchase order** (PO) to match invoice
6. **Calculate sales tax** based on jurisdiction
7. **Route to approver** based on amount threshold

**Tasks:**
1. Classify each agent as CRITICAL or OPTIONAL
2. Justify your classification based on business impact
3. Place validation gates (after which agents?)
4. Estimate expected EPI with your design

**Solution template:**
```python
# Agent classification
agents = {
    "extract_vendor": "???",      # CRITICAL or OPTIONAL? Why?
    "validate_vendor": "???",     # CRITICAL or OPTIONAL? Why?
    "extract_amount": "???",      # CRITICAL or OPTIONAL? Why?
    "categorize_expense": "???",  # CRITICAL or OPTIONAL? Why?
    "lookup_po": "???",           # CRITICAL or OPTIONAL? Why?
    "calculate_tax": "???",       # CRITICAL or OPTIONAL? Why?
    "route_approver": "???",      # CRITICAL or OPTIONAL? Why?
}

# Validation gate placement
validation_gates = [
    # TODO: List agents after which to place validation gates
    # Example: "After extract_vendor: validate schema with Pydantic"
]

# Expected EPI
expected_epi = 0.0  # TODO: Estimate based on your design
```

---

## Summary

**Key Takeaways:**

1. **Error propagation amplifies failures exponentially**
   - One upstream error can trigger 4-5 downstream errors in sequential workflows
   - Error Propagation Index (EPI) quantifies amplification: EPI = Cascaded Errors / Root Cause Errors
   - Without isolation: EPI ~3-4 for sequential workflows
   - With isolation: EPI ~0-0.5 for properly designed systems

2. **Result types prevent cascade failures**
   - Explicit Result[T, E] values instead of exceptions
   - Forces error handling at every step
   - Orchestrator doesn't crash when agents fail
   - Easy to aggregate and analyze errors

3. **Critical vs optional agent distinction enables graceful degradation**
   - Critical agents: Fail-fast, early termination prevents cascade
   - Optional agents: Degrade gracefully, use defaults on failure
   - Classification based on business impact, not technical implementation

4. **Early termination is key to preventing propagation**
   - Validation gates after critical agents catch errors before cascade
   - Circuit breaker stops processing after N consecutive failures
   - Cost-based termination prevents budget waste on failing workflows

5. **Isolation boundaries are architectural decisions**
   - Place after critical agents (extraction, validation, database operations)
   - Use Pydantic schema validation (Tutorial 03) at boundaries
   - Log boundary activations for debugging and EPI calculation
   - Monitor EPI as production reliability metric

**Production checklist:**
- ✅ Implement Result[T, E] type for all agent calls
- ✅ Classify agents as critical/optional based on business impact
- ✅ Place validation gates after critical agents
- ✅ Implement early termination on critical failures
- ✅ Use Pydantic schemas at isolation boundaries
- ✅ Log all errors with propagation trace
- ✅ Calculate and monitor EPI as reliability metric
- ✅ Set EPI targets (e.g., "Reduce EPI from 3.2 to <0.5")
- ✅ Test isolation with injected failures

**Next steps:**
- **Tutorial 05: AgentArch Benchmark Methodology** - Learn how to evaluate orchestration patterns by EPI and other metrics
- **Notebook 13: Reliability Framework Implementation** - Hands-on implementation of all isolation techniques
- **Error Propagation Cascade Diagram** (Task 6.8) - Visual trace of cascade failure mechanics

---

## Further Reading

**Error Propagation Research:**
- "Failure Modes in Production LLM Systems" - Statistical analysis of cascade failures
- AgentArch Paper (arXiv:2509.10769) - Error Propagation Index metric definition

**Result Type Patterns:**
- Rust Result<T, E> documentation - Original inspiration for error isolation
- Railway Oriented Programming - Functional approach to error handling

**Production Agent Reliability:**
- "Designing Fault-Tolerant Agent Systems" - Enterprise isolation patterns
- "LangGraph Error Handling" - Framework-specific isolation techniques

**Related Tutorials:**
- [Tutorial 01: Agent Reliability Fundamentals](01_agent_reliability_fundamentals.md) - Cascade failure introduction
- [Tutorial 03: Deterministic Execution Strategies](03_deterministic_execution_strategies.md) - Schema validation at boundaries
- [Tutorial 05: AgentArch Benchmark Methodology](05_agentarch_benchmark_methodology.md) - EPI measurement in benchmarks

**Backend Code:**
- `backend/reliability/isolation.py:1-173` - Result type implementation
- `backend/orchestrators/sequential.py` - Isolation in sequential workflows
- `backend/orchestrators/hierarchical.py` - Parallel execution isolation
- `backend/benchmarks/metrics.py` - EPI calculation implementation

**Interactive Notebooks:**
- [Notebook 13: Reliability Framework Implementation](../notebooks/13_reliability_framework_implementation.ipynb) - Complete isolation demo

---

**Navigation:**
- **← Previous:** [Tutorial 03: Deterministic Execution Strategies](03_deterministic_execution_strategies.md)
- **↑ Index:** [Tutorial Index](../TUTORIAL_INDEX.md)
- **→ Next:** [Tutorial 05: AgentArch Benchmark Methodology](05_agentarch_benchmark_methodology.md)

---

**Feedback:**
Found an issue or have suggestions? [Open an issue](https://github.com/anthropics/claude-code/issues) or contribute improvements!

**Last Updated:** 2025-11-23
**Version:** 1.0
**Lesson:** Lesson 16 - Agent Reliability
- [Notebook 14: AgentArch Benchmark Reproduction](../notebooks/14_agentarch_benchmark_reproduction.ipynb) - EPI across 5 orchestration patterns
