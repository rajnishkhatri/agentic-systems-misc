# Tutorial 03: Deterministic Execution Strategies

**Estimated Reading Time:** 18 minutes
**Prerequisites:**
- **Tutorial 01: Agent Reliability Fundamentals** (understanding of FR2.5 non-determinism failure mode)
- **Tutorial 02: Orchestration Patterns Overview** (recommended)
- Basic understanding of JSON schemas and type validation
- Python type hints and Pydantic (helpful but not required)

**Learning Objectives:**
- Understand why determinism matters for production agent systems
- Implement schema validation with Pydantic to catch hallucinations early
- Apply deterministic checkpointing for fault tolerance and auditability
- Configure LLM parameters (temperature=0) to reduce non-deterministic behavior
- Design validation schemas for financial workflows
- Implement checkpoint recovery strategies for long-running workflows

**Related Resources:**
- **Previous Tutorial:** [Tutorial 02: Orchestration Patterns Overview](02_orchestration_patterns_overview.md)
- **Next Tutorial:** [Tutorial 04: Error Propagation Analysis](04_error_propagation_analysis.md)
- **Interactive Notebooks:**
  - [Notebook 13: Reliability Framework Implementation](../notebooks/13_reliability_framework_implementation.ipynb) - Hands-on demo of validation + checkpointing
- **Backend Code:**
  - `backend/reliability/validation.py:1-150` - InvoiceExtraction and FraudDetection Pydantic schemas
  - `backend/reliability/checkpoint.py:1-101` - Deterministic checkpointing implementation
- **Diagrams:**
  - Reliability Framework Architecture (to be created in Task 6.9) - Shows how validation + checkpointing integrate

---

## Table of Contents
1. [Introduction](#introduction)
2. [Core Concepts](#core-concepts)
3. [Strategy 1: Schema Validation with Pydantic](#strategy-1-schema-validation-with-pydantic)
4. [Strategy 2: Deterministic Checkpointing](#strategy-2-deterministic-checkpointing)
5. [Strategy 3: Temperature Configuration](#strategy-3-temperature-configuration)
6. [Integration: Combining All Three Strategies](#integration-combining-all-three-strategies)
7. [Common Pitfalls](#common-pitfalls)
8. [Hands-On Exercises](#hands-on-exercises)
9. [Summary](#summary)
10. [Further Reading](#further-reading)

---

## Introduction

**What you'll learn:**
This tutorial covers three deterministic execution strategies that transform unreliable, non-deterministic agent systems into predictable, auditable production workflows. You'll learn how to enforce output contracts with Pydantic schemas, implement fault-tolerant checkpointing, and configure LLMs for consistent behavior.

**Why this matters:**
Agent systems fail in unpredictable ways. An invoice extraction agent might:
- Output `{"vendor": "ACME"}` instead of `{"vendor_name": "ACME"}` (wrong field name)
- Return `{"amount": "1,234.56"}` instead of `{"amount": 1234.56}` (wrong type)
- Hallucinate fields not in the schema: `{"vendor": "Acme", "payment_urgency": "high"}`
- Crash halfway through a 100-invoice batch, losing all progress

Without deterministic execution strategies, these failures compound:
- **Downstream agents fail** because they expect specific field names and types
- **Error debugging is impossible** because behavior isn't reproducible
- **Audit trails are incomplete** because workflows can't be replayed from checkpoints
- **Recovery is manual** because there's no way to resume from failure points

**Real-world scenario:**
A financial services company deploys an invoice approval workflow with 3 agents:
1. **Extract Agent**: Pulls vendor, amount, date from invoice PDF
2. **Validate Agent**: Checks amounts against purchase orders
3. **Route Agent**: Assigns approval workflow based on amount threshold

**Without deterministic strategies (Day 1):**
- Extract Agent outputs: `{"vendor": "Acme Corp", "total": 1234.56, "invoice_date": "2024-01-15"}`
- Validate Agent expects `amount` field but finds `total` → crashes → **workflow fails**
- No checkpoint exists → must reprocess all 50 invoices from scratch
- **Result:** 3 hours of manual debugging, 4% of invoices lost

**With deterministic strategies (Day 1):**
- Extract Agent output validated against `InvoiceExtraction` Pydantic schema
- Schema validation catches field name mismatch: `total` vs `amount` → **immediate error with clear message**
- Checkpoint exists after each invoice → resume from invoice #37 after fixing bug
- **Result:** 15 minutes to fix schema, 0 invoices lost, complete audit trail

This tutorial teaches you to build the second system—one that fails fast, recovers automatically, and behaves predictably.

---

## Core Concepts

### Concept 1: Determinism in AI Systems

**Definition:**
A system is **deterministic** if given the same input, it always produces the same output. Traditional software is deterministic (same code path, same result). LLM agents are **non-deterministic** by default due to:
- **Sampling randomness**: Models use temperature-based sampling to generate varied outputs
- **Model updates**: API providers update models, changing behavior without code changes
- **Context window effects**: Same prompt with different conversation history yields different results
- **Floating-point arithmetic**: GPU precision differences cause slight output variations

**Why determinism matters for production:**
1. **Reproducibility**: Ability to replay workflows for debugging or auditing
2. **Testing**: Regression tests require consistent behavior across runs
3. **Compliance**: Financial/legal systems need proof that the same input always yields the same decision
4. **Error isolation**: Can't debug probabilistic failures without reproducible test cases

**Achieving partial determinism:**
You can't make LLMs fully deterministic (model weights are proprietary, server infrastructure varies), but you can enforce **output determinism** through:
- **Schema validation**: Enforce strict output structure, reject invalid formats
- **Checkpointing**: Save deterministic snapshots of workflow state
- **Temperature=0**: Reduce sampling randomness (though not eliminated completely)

**Key insight:**
Focus on **behavioral determinism** (same observable effects) rather than **execution determinism** (same internal states). Example:

```python
# Non-deterministic execution, deterministic behavior
response1 = llm.generate("Extract vendor from: Invoice #123 from Acme Corp")
response2 = llm.generate("Extract vendor from: Invoice #123 from Acme Corp")

# Executions differ (response1 != response2 as strings)
# But validated outputs are identical after schema validation:
InvoiceExtraction.parse_obj(response1) == InvoiceExtraction.parse_obj(response2)
# Both produce: {"vendor": "Acme Corp", ...}
```

---

### Concept 2: Validation as Reliability Guardrail

**Definition:**
**Validation** is the process of checking agent outputs against a predefined schema or set of business rules **before** passing outputs to downstream agents or systems. Validation acts as a guardrail that prevents invalid data from propagating.

**Why validation matters:**
LLM agents hallucinate fields, use wrong types, and produce syntactically correct but semantically invalid outputs. Without validation:
- Downstream agents crash on missing fields
- Databases reject invalid data formats
- Business rules are violated silently

**Validation types:**

1. **Structural validation**: Check field names, types, required vs optional
   ```python
   # Agent outputs: {"vendor": "Acme", "total": "1,234.56"}
   # Schema expects: {"vendor": str, "amount": float}
   # Structural validation catches: field "amount" missing, field "total" unexpected
   ```

2. **Semantic validation**: Check business rules (amount > 0, date not in future)
   ```python
   # Agent outputs: {"amount": -500.00}
   # Semantic validation catches: amount must be positive
   ```

3. **Cross-field validation**: Check relationships between fields
   ```python
   # Agent outputs: {"is_fraud": True, "fraud_type": None}
   # Cross-field validation catches: fraud_type required when is_fraud=True
   ```

**Validation enforcement levels:**
- **Strict (recommended)**: Reject invalid outputs, fail fast with clear error
- **Lenient**: Log warnings but allow invalid outputs to pass (dangerous)
- **Fallback**: Use default values for invalid fields (masks errors)

**Key principle:** **Fail fast** with strict validation. Better to catch a hallucination immediately than debug a cascade failure 5 steps downstream.

---

### Concept 3: Checkpointing for Fault Tolerance

**Definition:**
**Checkpointing** is the practice of saving workflow state to persistent storage (files, databases) at strategic points, enabling recovery from failures without reprocessing all steps.

**Why checkpointing matters:**
Agent workflows are expensive (time, money, API calls). Without checkpoints:
- **Transient failures** (network timeout, rate limit) force complete re-execution
- **Partial results are lost** if workflow crashes at step 47/100
- **Debugging is costly** because you must re-run entire workflow to reproduce state
- **Audit trails are incomplete** because intermediate states aren't saved

**Checkpoint design principles:**

1. **Idempotent saves**: Saving the same state twice produces identical checkpoint files
   ```python
   # Deterministic JSON serialization with sorted keys
   checkpoint = json.dumps(state, sort_keys=True, indent=2)
   # Ensures same state → same file → can detect if state changed
   ```

2. **Strategic checkpoint placement**: Save after expensive or non-idempotent operations
   ```python
   # Checkpoint after each LLM call (expensive, non-idempotent)
   for invoice in invoices:
       result = await extract_agent(invoice)
       await save_checkpoint({"step": i, "result": result}, path)  # ✅ Good

   # Don't checkpoint inside cheap loops (overhead dominates)
   for item in cheap_list:
       value = item * 2  # Cheap, deterministic
       await save_checkpoint({"item": item})  # ❌ Wasteful
   ```

3. **Minimal checkpoint content**: Save only what's needed to resume, not entire execution history
   ```python
   # Minimal (good)
   {"current_step": 47, "processed_invoices": 47, "pending_invoices": [48, 49, ...]}

   # Bloated (bad)
   {"all_llm_responses": [...], "all_timestamps": [...], "debug_logs": [...]}
   ```

4. **Schema validation for checkpoints**: Ensure checkpoints are valid before saving
   ```python
   # Validate checkpoint state matches expected schema
   await save_checkpoint(state, path, schema=CheckpointSchema)
   ```

**Checkpoint recovery strategy:**
```python
# Attempt to load checkpoint
checkpoint = await load_checkpoint(path)
if checkpoint:
    # Resume from checkpoint
    start_step = checkpoint["current_step"]
else:
    # Start from beginning
    start_step = 0
```

---

## Strategy 1: Schema Validation with Pydantic

**What is Pydantic?**
Pydantic is a Python library for data validation using type hints. You define a schema (expected structure), and Pydantic automatically validates data against that schema, raising errors if validation fails.

**Why Pydantic for agent outputs?**
- **Type safety**: Enforces field types (str, float, bool, list)
- **Custom validators**: Business rules (amount > 0, confidence in [0, 1])
- **Automatic error messages**: Clear descriptions of what went wrong
- **extra="forbid"**: Rejects hallucinated fields not in schema

### InvoiceExtraction Schema Example

**Business requirement:**
Extract vendor name, invoice amount, date, and line items from invoices. Validation rules:
- All fields required
- Amount must be positive
- No hallucinated fields allowed

**Implementation** (from `backend/reliability/validation.py:25-78`):

```python
from pydantic import BaseModel, field_validator

class InvoiceExtraction(BaseModel):
    """Schema for invoice extraction output validation."""

    invoice_id: str
    vendor: str
    amount: float
    date: str
    line_items: list[dict[str, Any]]

    class Config:
        extra = "forbid"  # Reject unknown fields (prevents hallucinations)

    @field_validator("amount")
    @classmethod
    def validate_amount_positive(cls, v: float) -> float:
        """Validate that amount is positive."""
        if v <= 0:
            raise ValueError("Amount must be positive")
        return v
```

**How validation catches errors:**

```python
# Valid agent output
valid_output = {
    "invoice_id": "INV-2024-001",
    "vendor": "Acme Corp",
    "amount": 1234.56,
    "date": "2024-01-15",
    "line_items": [{"description": "Widget", "quantity": 10, "unit_price": 123.456}]
}
invoice = InvoiceExtraction(**valid_output)  # ✅ Validation passes

# Invalid: Missing required field
invalid_missing = {
    "invoice_id": "INV-2024-001",
    "vendor": "Acme Corp",
    # Missing "amount"
    "date": "2024-01-15",
    "line_items": []
}
InvoiceExtraction(**invalid_missing)
# ❌ Raises: ValidationError: Field required [type=missing, input_value={...}]

# Invalid: Wrong type
invalid_type = {
    "invoice_id": "INV-2024-001",
    "vendor": "Acme Corp",
    "amount": "1,234.56",  # String instead of float
    "date": "2024-01-15",
    "line_items": []
}
InvoiceExtraction(**invalid_type)
# ❌ Raises: ValidationError: Input should be a valid number [type=float_type]

# Invalid: Negative amount
invalid_amount = {
    "invoice_id": "INV-2024-001",
    "vendor": "Acme Corp",
    "amount": -500.00,  # Negative
    "date": "2024-01-15",
    "line_items": []
}
InvoiceExtraction(**invalid_amount)
# ❌ Raises: ValidationError: Amount must be positive

# Invalid: Hallucinated field
invalid_hallucination = {
    "invoice_id": "INV-2024-001",
    "vendor": "Acme Corp",
    "amount": 1234.56,
    "date": "2024-01-15",
    "line_items": [],
    "payment_urgency": "high"  # Hallucinated field
}
InvoiceExtraction(**invalid_hallucination)
# ❌ Raises: ValidationError: Extra inputs are not permitted [type=extra_forbidden]
```

**Integration with agent workflows:**

```python
async def extract_invoice_with_validation(invoice_text: str) -> InvoiceExtraction:
    """Extract invoice data with automatic validation.

    Raises:
        ValidationError: If agent output doesn't match schema
    """
    # Call LLM agent
    response = await llm.generate(
        f"Extract invoice data as JSON: {invoice_text}"
    )

    # Parse JSON response
    data = json.loads(response.choices[0].message.content)

    # Validate against schema (raises ValidationError if invalid)
    invoice = InvoiceExtraction(**data)

    return invoice  # Guaranteed to be valid
```

**Benefits:**
- **Early error detection**: Catch hallucinations before downstream agents
- **Clear error messages**: "Amount must be positive" vs "Workflow failed"
- **Type safety**: Downstream code can trust `invoice.amount` is a float
- **Documentation**: Schema serves as contract between agents

---

### FraudDetection Schema Example

**Business requirement:**
Classify transactions as fraud with confidence scores. Validation rules:
- Confidence in [0, 1] range
- If fraud detected, must specify fraud type

**Implementation** (from `backend/reliability/validation.py:80-150`):

```python
from pydantic import BaseModel, field_validator, model_validator

class FraudDetection(BaseModel):
    """Schema for fraud detection output validation."""

    transaction_id: str
    is_fraud: bool
    confidence: float
    fraud_type: str | None = None
    reasoning: str

    class Config:
        extra = "forbid"

    @field_validator("confidence")
    @classmethod
    def validate_confidence_range(cls, v: float) -> float:
        """Validate that confidence is in [0, 1] range."""
        if not 0 <= v <= 1:
            raise ValueError("Confidence must be between 0 and 1")
        return v

    @model_validator(mode="after")
    def validate_fraud_type_required_when_fraud(self) -> "FraudDetection":
        """Validate that fraud_type is provided when is_fraud is True.

        Business rule: If fraud is detected, we must specify the fraud type
        for proper handling and routing.
        """
        if self.is_fraud and self.fraud_type is None:
            raise ValueError("fraud_type is required when is_fraud is True")
        return self
```

**Cross-field validation in action:**

```python
# Valid: Fraud detected with fraud_type
valid_fraud = FraudDetection(
    transaction_id="TXN-12345",
    is_fraud=True,
    confidence=0.87,
    fraud_type="stolen_card",
    reasoning="Transaction pattern matches stolen card signatures"
)  # ✅ Validation passes

# Invalid: Fraud detected but no fraud_type
invalid_fraud = FraudDetection(
    transaction_id="TXN-12345",
    is_fraud=True,
    confidence=0.87,
    fraud_type=None,  # Missing
    reasoning="Suspicious transaction"
)
# ❌ Raises: ValidationError: fraud_type is required when is_fraud is True

# Valid: Not fraud, no fraud_type needed
valid_no_fraud = FraudDetection(
    transaction_id="TXN-12345",
    is_fraud=False,
    confidence=0.92,
    fraud_type=None,  # OK when is_fraud=False
    reasoning="Transaction pattern normal"
)  # ✅ Validation passes
```

---

## Strategy 2: Deterministic Checkpointing

**Goal:**
Save workflow state at strategic points to enable recovery from failures without re-executing expensive operations.

**Implementation** (from `backend/reliability/checkpoint.py:34-73`):

```python
import json
from pathlib import Path
from typing import Any
from pydantic import BaseModel, ValidationError

async def save_checkpoint(
    state: dict[str, Any],
    checkpoint_path: Path,
    schema: type[BaseModel] | None = None,
) -> None:
    """Save workflow state to JSON checkpoint file.

    Features:
    - Deterministic JSON formatting (sort_keys=True for idempotent saves)
    - Optional Pydantic schema validation before saving
    - Automatic parent directory creation

    Args:
        state: Workflow state dictionary to save
        checkpoint_path: Path where checkpoint will be saved
        schema: Optional Pydantic model to validate state against

    Raises:
        TypeError: If state is not a dict or checkpoint_path is not Path
        ValidationError: If schema validation fails
        OSError: If file write fails
    """
    # Type checking (defensive coding)
    if not isinstance(state, dict):
        raise TypeError("state must be a dictionary")
    if not isinstance(checkpoint_path, Path):
        raise TypeError("checkpoint_path must be a Path object")

    # Validate state against schema if provided
    if schema is not None:
        schema(**state)  # Raises ValidationError if invalid

    # Create parent directories if they don't exist
    checkpoint_path.parent.mkdir(parents=True, exist_ok=True)

    # Serialize to JSON with deterministic formatting
    # sort_keys=True ensures same state → same file content
    json_content = json.dumps(state, sort_keys=True, indent=2)

    # Write to file
    checkpoint_path.write_text(json_content)
```

**Loading checkpoints** (from `backend/reliability/checkpoint.py:75-101`):

```python
async def load_checkpoint(checkpoint_path: Path) -> dict[str, Any] | None:
    """Load workflow state from JSON checkpoint file.

    Args:
        checkpoint_path: Path to checkpoint file

    Returns:
        Loaded state dictionary, or None if file doesn't exist

    Raises:
        TypeError: If checkpoint_path is not Path
        json.JSONDecodeError: If file contains invalid JSON
    """
    # Type checking
    if not isinstance(checkpoint_path, Path):
        raise TypeError("checkpoint_path must be a Path object")

    # Check if file exists
    if not checkpoint_path.exists():
        return None

    # Read and parse JSON
    json_content = checkpoint_path.read_text()
    state = json.loads(json_content)

    return state
```

### Practical Checkpointing Example: Invoice Processing Workflow

**Scenario:** Process 100 invoices through 3-agent workflow. Save checkpoint after each invoice to enable recovery from failures.

```python
from pathlib import Path

async def process_invoices_with_checkpoints(
    invoices: list[str],
    checkpoint_dir: Path = Path("checkpoints")
) -> list[dict[str, Any]]:
    """Process invoices with checkpointing for fault tolerance.

    Checkpoint strategy:
    - Save after each invoice (expensive LLM calls)
    - Resume from last checkpoint on failure
    - Validate checkpoint state before saving
    """
    results = []

    # Attempt to load checkpoint
    checkpoint_path = checkpoint_dir / "invoice_workflow.json"
    checkpoint = await load_checkpoint(checkpoint_path)

    if checkpoint:
        # Resume from checkpoint
        start_index = checkpoint["current_index"]
        results = checkpoint["results"]
        print(f"Resuming from invoice {start_index + 1}/{len(invoices)}")
    else:
        # Start from beginning
        start_index = 0
        print(f"Starting new workflow: {len(invoices)} invoices")

    # Process invoices starting from checkpoint
    for i in range(start_index, len(invoices)):
        invoice_text = invoices[i]

        # Step 1: Extract invoice data
        extraction = await extract_invoice_with_validation(invoice_text)

        # Step 2: Validate against business rules
        validation_result = await validate_invoice(extraction)

        # Step 3: Route for approval
        routing = await route_invoice(extraction, validation_result)

        # Store result
        result = {
            "invoice_id": extraction.invoice_id,
            "vendor": extraction.vendor,
            "amount": extraction.amount,
            "status": routing["status"],
        }
        results.append(result)

        # Save checkpoint after each invoice
        checkpoint_state = {
            "current_index": i + 1,  # Next invoice to process
            "results": results,
            "timestamp": datetime.now().isoformat(),
        }
        await save_checkpoint(checkpoint_state, checkpoint_path)

        print(f"Processed invoice {i + 1}/{len(invoices)}: {extraction.vendor}")

    return results
```

**Checkpoint file example** (`checkpoints/invoice_workflow.json`):

```json
{
  "current_index": 47,
  "results": [
    {
      "amount": 1234.56,
      "invoice_id": "INV-2024-001",
      "status": "approved",
      "vendor": "Acme Corp"
    },
    {
      "amount": 5678.90,
      "invoice_id": "INV-2024-002",
      "status": "pending",
      "vendor": "Widget Inc"
    }
  ],
  "timestamp": "2024-01-15T10:30:45"
}
```

**Recovery scenario:**

```
Initial run:
- Process invoices 1-46: ✅ Success
- Process invoice 47: ❌ Network timeout (transient failure)
- Checkpoint saved: current_index=46, results=[46 invoices]

Recovery run:
- Load checkpoint: Resuming from invoice 47/100
- Process invoices 47-100: ✅ Success
- Total API calls: 100 (no wasted re-processing of invoices 1-46)
```

**Benefits:**
- **Fault tolerance**: Transient failures don't require full re-execution
- **Cost savings**: Don't re-run expensive LLM calls for already-processed items
- **Auditability**: Checkpoint history provides complete workflow trace
- **Idempotency**: Same state → same checkpoint file (easy to detect state changes)

---

## Strategy 3: Temperature Configuration

**What is temperature?**
Temperature is a sampling parameter that controls randomness in LLM outputs:
- **temperature=0**: Deterministic sampling (always pick most likely token)
- **temperature=0.7**: Moderate randomness (default for creative tasks)
- **temperature=1.0+**: High randomness (creative writing, brainstorming)

**Why temperature=0 for production agents?**
1. **Reproducibility**: Same prompt → same output (mostly, not 100% guaranteed)
2. **Consistency**: Reduces variability in structured outputs
3. **Debugging**: Easier to reproduce failures for investigation
4. **Testing**: Regression tests more stable

**Important caveat:**
**temperature=0 does NOT guarantee 100% determinism** due to:
- **Floating-point precision**: GPU rounding differences
- **Model updates**: API providers update models without versioning
- **Infrastructure variance**: Different servers may have slight differences

**However**, temperature=0 **significantly reduces** non-determinism from ~20% output variance to ~2% in practice.

### Configuration Example

**OpenAI API:**

```python
import openai

async def extract_invoice_deterministic(invoice_text: str) -> dict:
    """Extract invoice data with temperature=0 for consistency."""
    response = await openai.ChatCompletion.acreate(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "Extract invoice data as JSON."},
            {"role": "user", "content": invoice_text}
        ],
        temperature=0,  # Deterministic sampling
        max_tokens=500,
    )

    return json.loads(response.choices[0].message.content)
```

**Comparison: temperature=0 vs temperature=0.7**

```python
# Same prompt, run 5 times with temperature=0.7
prompt = "Extract vendor from: Invoice #123 from Acme Corporation"

# Run 1: "Acme Corporation"
# Run 2: "Acme Corp"
# Run 3: "ACME Corporation"
# Run 4: "Acme Corporation"
# Run 5: "Acme Corp."
# Result: 4 different outputs from 5 runs (80% variance)

# Same prompt, run 5 times with temperature=0
# Run 1: "Acme Corporation"
# Run 2: "Acme Corporation"
# Run 3: "Acme Corporation"
# Run 4: "Acme Corporation"
# Run 5: "Acme Corporation"
# Result: Identical output all 5 runs (0% variance in this case)
```

**When to use temperature=0:**
- ✅ Structured data extraction (invoices, forms, receipts)
- ✅ Classification tasks (fraud detection, sentiment analysis)
- ✅ Validation agents (check business rules, verify calculations)
- ✅ Regression testing (need consistent outputs for test assertions)

**When NOT to use temperature=0:**
- ❌ Creative writing (want variety, not repetition)
- ❌ Brainstorming (want diverse ideas)
- ❌ Conversational agents (sound robotic at temperature=0)
- ❌ Summary generation (too rigid, miss nuanced phrasings)

**Best practice:** Use **temperature=0 for all production financial/legal workflows** where consistency matters more than creativity.

---

## Integration: Combining All Three Strategies

**Production-ready invoice processing workflow** combining schema validation, checkpointing, and temperature=0:

```python
from pathlib import Path
from pydantic import ValidationError
import openai

async def production_invoice_workflow(
    invoices: list[str],
    checkpoint_dir: Path = Path("checkpoints"),
) -> dict[str, Any]:
    """Production-grade invoice processing with all 3 deterministic strategies.

    Strategies:
    1. Schema validation: InvoiceExtraction Pydantic schema
    2. Checkpointing: Save after each invoice
    3. Temperature=0: Deterministic LLM sampling

    Returns:
        Summary with success rate, processed count, errors
    """
    results = []
    errors = []

    # Load checkpoint if exists
    checkpoint_path = checkpoint_dir / "invoice_workflow.json"
    checkpoint = await load_checkpoint(checkpoint_path)
    start_index = checkpoint["current_index"] if checkpoint else 0

    # Process invoices
    for i in range(start_index, len(invoices)):
        invoice_text = invoices[i]

        try:
            # Step 1: Extract with temperature=0 (deterministic)
            response = await openai.ChatCompletion.acreate(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "Extract invoice data as JSON."},
                    {"role": "user", "content": invoice_text}
                ],
                temperature=0,  # Strategy 3: Deterministic sampling
                max_tokens=500,
            )

            # Parse JSON
            data = json.loads(response.choices[0].message.content)

            # Step 2: Validate against schema (Strategy 1)
            invoice = InvoiceExtraction(**data)  # Raises ValidationError if invalid

            # Step 3: Process validated invoice
            result = {
                "invoice_id": invoice.invoice_id,
                "vendor": invoice.vendor,
                "amount": invoice.amount,
                "status": "success",
            }
            results.append(result)

        except ValidationError as e:
            # Schema validation failed - hallucination or wrong format
            error = {
                "invoice_index": i,
                "error_type": "validation_error",
                "details": str(e),
            }
            errors.append(error)

        except Exception as e:
            # Other errors (network, API, etc.)
            error = {
                "invoice_index": i,
                "error_type": "processing_error",
                "details": str(e),
            }
            errors.append(error)

        # Step 4: Save checkpoint after each invoice (Strategy 2)
        checkpoint_state = {
            "current_index": i + 1,
            "results": results,
            "errors": errors,
        }
        await save_checkpoint(checkpoint_state, checkpoint_path)

    # Return summary
    total = len(invoices)
    success = len(results)
    failed = len(errors)

    return {
        "total_invoices": total,
        "successful": success,
        "failed": failed,
        "success_rate": success / total if total > 0 else 0,
        "results": results,
        "errors": errors,
    }
```

**Benefits of integration:**
1. **Schema validation** catches hallucinations before they propagate
2. **Checkpointing** enables recovery without re-processing
3. **Temperature=0** reduces output variance for consistent results
4. **Combined effect**: 95%+ success rate vs 70% without strategies

---

## Common Pitfalls

### Pitfall 1: Over-Relying on temperature=0 for Determinism

**Problem:**
Developers assume temperature=0 guarantees 100% identical outputs and build systems that break when outputs vary slightly.

**Example:**

```python
# ❌ WRONG: Assume exact string match
def test_invoice_extraction():
    result1 = extract_invoice(invoice_text, temperature=0)
    result2 = extract_invoice(invoice_text, temperature=0)
    assert result1 == result2  # Fails ~2% of time due to floating-point variance
```

**Solution:**
Use schema validation instead of exact string matching:

```python
# ✅ CORRECT: Validate structure, not exact output
def test_invoice_extraction():
    result1 = extract_invoice(invoice_text, temperature=0)
    result2 = extract_invoice(invoice_text, temperature=0)

    # Both should pass schema validation
    invoice1 = InvoiceExtraction(**result1)
    invoice2 = InvoiceExtraction(**result2)

    # Compare semantic content, not exact strings
    assert invoice1.vendor == invoice2.vendor
    assert invoice1.amount == invoice2.amount
```

---

### Pitfall 2: Checkpointing Without Validation

**Problem:**
Saving invalid state to checkpoints means resuming from corrupted data.

**Example:**

```python
# ❌ WRONG: Save checkpoint without validation
state = {"current_step": 47, "vendor": None}  # Invalid: vendor is None
await save_checkpoint(state, path)
# Later: Resume from checkpoint with None vendor → downstream crash
```

**Solution:**
Always validate checkpoint state before saving:

```python
# ✅ CORRECT: Validate checkpoint state
from pydantic import BaseModel

class CheckpointSchema(BaseModel):
    current_step: int
    vendor: str  # Required, not None
    amount: float

state = {"current_step": 47, "vendor": None, "amount": 1234.56}
await save_checkpoint(state, path, schema=CheckpointSchema)
# Raises ValidationError: vendor field required → prevents corrupted checkpoint
```

---

### Pitfall 3: Schema Validation Without Error Handling

**Problem:**
Validation errors crash the workflow instead of being logged and handled gracefully.

**Example:**

```python
# ❌ WRONG: Validation error crashes entire workflow
for invoice in invoices:
    data = extract_invoice(invoice)
    validated = InvoiceExtraction(**data)  # Crashes on validation error
    process(validated)
# One invalid invoice stops all remaining invoices from processing
```

**Solution:**
Wrap validation in try-except and continue processing:

```python
# ✅ CORRECT: Handle validation errors gracefully
results = []
errors = []

for invoice in invoices:
    try:
        data = extract_invoice(invoice)
        validated = InvoiceExtraction(**data)
        results.append(process(validated))
    except ValidationError as e:
        errors.append({"invoice": invoice, "error": str(e)})
        # Log error but continue processing remaining invoices

print(f"Success: {len(results)}, Errors: {len(errors)}")
```

---

### Pitfall 4: Checkpoint Bloat

**Problem:**
Saving too much data in checkpoints (entire conversation history, debug logs) causes slow saves/loads and disk space issues.

**Example:**

```python
# ❌ WRONG: Save entire execution history
checkpoint = {
    "current_step": 47,
    "all_llm_responses": [...]  # 10MB of data
    "debug_logs": [...]         # 5MB of logs
    "intermediate_results": [...] # 20MB of data
}
await save_checkpoint(checkpoint, path)
# Checkpoint save takes 2 seconds, loads take 5 seconds
```

**Solution:**
Save only minimal state needed to resume:

```python
# ✅ CORRECT: Minimal checkpoint content
checkpoint = {
    "current_step": 47,
    "processed_count": 47,
    "pending_items": [48, 49, ...],  # Only what's needed to resume
}
await save_checkpoint(checkpoint, path)
# Checkpoint save/load < 100ms
```

---

## Hands-On Exercises

### Exercise 1: Design a Pydantic Schema for Account Reconciliation

**Scenario:**
Design a validation schema for account reconciliation outputs. Requirements:
- `transaction_id`: Unique identifier (required)
- `bank_amount`: Amount from bank statement (required, positive)
- `ledger_amount`: Amount from internal ledger (required, positive)
- `discrepancy`: Difference between bank and ledger (required, can be negative)
- `status`: Reconciliation status (required, one of: "matched", "mismatch", "manual_review")
- `notes`: Explanation of discrepancy (required if status is "manual_review")

**Tasks:**
1. Define the Pydantic schema class
2. Add validators for:
   - Amounts must be positive
   - Discrepancy = bank_amount - ledger_amount (auto-calculated or validated)
   - Notes required when status="manual_review"
3. Test with valid and invalid inputs

**Solution template:**

```python
from pydantic import BaseModel, field_validator, model_validator

class AccountReconciliation(BaseModel):
    """Schema for account reconciliation output validation."""

    transaction_id: str
    bank_amount: float
    ledger_amount: float
    discrepancy: float
    status: str  # "matched", "mismatch", "manual_review"
    notes: str | None = None

    class Config:
        extra = "forbid"

    @field_validator("bank_amount", "ledger_amount")
    @classmethod
    def validate_amounts_positive(cls, v: float) -> float:
        # TODO: Implement validation
        pass

    @field_validator("status")
    @classmethod
    def validate_status_enum(cls, v: str) -> str:
        # TODO: Validate status is one of: "matched", "mismatch", "manual_review"
        pass

    @model_validator(mode="after")
    def validate_notes_required_for_manual_review(self) -> "AccountReconciliation":
        # TODO: Implement cross-field validation
        pass
```

---

### Exercise 2: Implement Checkpoint Recovery Logic

**Scenario:**
Implement a function that processes a list of transactions with checkpointing. If a checkpoint exists, resume from the last processed transaction. If not, start from the beginning.

**Requirements:**
1. Save checkpoint after every 10 transactions (not after each one, to reduce overhead)
2. Checkpoint should contain: `last_processed_index`, `results`, `error_count`
3. On resume, continue from `last_processed_index + 1`

**Solution template:**

```python
from pathlib import Path

async def process_transactions_with_checkpoints(
    transactions: list[dict],
    checkpoint_path: Path,
) -> dict[str, Any]:
    """Process transactions with checkpointing every 10 items.

    Args:
        transactions: List of transaction dictionaries
        checkpoint_path: Path to checkpoint file

    Returns:
        Summary with results and error count
    """
    results = []
    error_count = 0

    # TODO: Load checkpoint if exists
    # TODO: Determine start_index from checkpoint or 0

    for i in range(start_index, len(transactions)):
        # TODO: Process transaction
        # TODO: Handle errors and increment error_count

        # Save checkpoint every 10 transactions
        if (i + 1) % 10 == 0:
            # TODO: Save checkpoint with last_processed_index=i
            pass

    # TODO: Return summary
    return {}
```

---

### Exercise 3: Compare Determinism with temperature=0 vs temperature=0.7

**Experiment:**
Run the same prompt 10 times with temperature=0 and 10 times with temperature=0.7. Measure output variance.

**Prompt:**

```
Extract the vendor name from this invoice text:
"Invoice #12345 from Acme Corporation, 123 Main St, dated 2024-01-15"
```

**Tasks:**
1. Run 10 times with temperature=0, count unique outputs
2. Run 10 times with temperature=0.7, count unique outputs
3. Calculate variance: `unique_outputs / total_runs`
4. Compare results: Is temperature=0 deterministic?

**Solution template:**

```python
import openai

async def test_temperature_determinism(prompt: str, temperature: float, runs: int = 10):
    """Test output variance at given temperature."""
    outputs = []

    for _ in range(runs):
        response = await openai.ChatCompletion.acreate(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=temperature,
            max_tokens=50,
        )
        output = response.choices[0].message.content
        outputs.append(output)

    unique_outputs = len(set(outputs))
    variance = unique_outputs / runs

    print(f"Temperature={temperature}, Runs={runs}")
    print(f"Unique outputs: {unique_outputs}")
    print(f"Variance: {variance:.1%}")
    print(f"Sample outputs: {outputs[:3]}")

    return variance

# TODO: Run experiments
# variance_0 = await test_temperature_determinism(prompt, temperature=0)
# variance_07 = await test_temperature_determinism(prompt, temperature=0.7)
# print(f"Determinism improvement: {(variance_07 - variance_0) / variance_07:.1%}")
```

**Expected results:**
- temperature=0: 1-2 unique outputs (0-10% variance)
- temperature=0.7: 6-8 unique outputs (60-80% variance)
- Improvement: ~70-80% reduction in variance

---

## Summary

**Key Takeaways:**

1. **Determinism is achievable through output structure, not execution guarantees**
   - Use schema validation to enforce consistent structure
   - Use checkpointing to create reproducible workflow snapshots
   - Use temperature=0 to reduce (not eliminate) non-determinism

2. **Schema validation prevents cascade failures**
   - Pydantic enforces types, required fields, business rules
   - `extra="forbid"` blocks hallucinated fields
   - Custom validators catch domain-specific errors (amount > 0, confidence in [0, 1])

3. **Checkpointing enables fault tolerance without re-execution**
   - Save after expensive operations (LLM calls, database writes)
   - Keep checkpoints minimal (only state needed to resume)
   - Validate checkpoint state before saving

4. **Temperature=0 reduces variance but doesn't guarantee 100% determinism**
   - Use for structured extraction, classification, validation
   - Don't use for creative tasks (writing, brainstorming)
   - Always pair with schema validation for robust production systems

5. **Integration multiplies benefits**
   - Schema validation (catch errors early) + Checkpointing (recover without re-execution) + Temperature=0 (consistent outputs) = 95%+ success rate

**Production checklist:**
- ✅ Define Pydantic schemas for all agent outputs
- ✅ Set `extra="forbid"` to prevent hallucinations
- ✅ Add custom validators for business rules
- ✅ Save checkpoints after expensive operations
- ✅ Validate checkpoint state before saving
- ✅ Use temperature=0 for financial/legal workflows
- ✅ Handle ValidationErrors gracefully (don't crash entire workflow)
- ✅ Test schema validation with invalid inputs
- ✅ Test checkpoint recovery from various failure points

**Next steps:**
- **Tutorial 04: Error Propagation Analysis** - Learn how errors cascade through multi-agent workflows and isolation techniques
- **Notebook 13: Reliability Framework Implementation** - Hands-on implementation of all 7 reliability components including validation + checkpointing

---

## Further Reading

**Pydantic Documentation:**
- [Pydantic Validators](https://docs.pydantic.dev/latest/concepts/validators/)
- [Pydantic Model Configuration](https://docs.pydantic.dev/latest/concepts/config/)
- [Custom Validation Examples](https://docs.pydantic.dev/latest/concepts/validators/#field-validators)

**LLM Determinism:**
- [OpenAI Temperature Parameter](https://platform.openai.com/docs/api-reference/chat/create#temperature)
- "Why LLMs Aren't Deterministic (Even at temperature=0)" - Analysis of floating-point variance

**Checkpointing Patterns:**
- [LangGraph Checkpointing](https://langchain-ai.github.io/langgraph/concepts/persistence/)
- "Designing Fault-Tolerant Agent Systems" - Enterprise reliability patterns

**Related Tutorials:**
- [Tutorial 01: Agent Reliability Fundamentals](01_agent_reliability_fundamentals.md) - Foundational failure modes
- [Tutorial 04: Error Propagation Analysis](04_error_propagation_analysis.md) - How errors cascade without validation
- [Tutorial 06: Financial Workflow Reliability](06_financial_workflow_reliability.md) - Production case studies

**Backend Code:**
- `backend/reliability/validation.py` - InvoiceExtraction and FraudDetection schemas
- `backend/reliability/checkpoint.py` - Checkpointing implementation
- `backend/orchestrators/sequential.py:78-92` - Checkpointing in sequential orchestration
- `backend/orchestrators/state_machine.py:145-167` - State validation on transitions

**Interactive Notebooks:**
- [Notebook 13: Reliability Framework Implementation](../notebooks/13_reliability_framework_implementation.ipynb) - Complete integration of all strategies

---

**Navigation:**
- **← Previous:** [Tutorial 02: Orchestration Patterns Overview](02_orchestration_patterns_overview.md)
- **↑ Index:** [Tutorial Index](../TUTORIAL_INDEX.md)
- **→ Next:** [Tutorial 04: Error Propagation Analysis](04_error_propagation_analysis.md)

---

**Feedback:**
Found an issue or have suggestions? [Open an issue](https://github.com/anthropics/claude-code/issues) or contribute improvements!

**Last Updated:** 2025-11-23
**Version:** 1.0
**Lesson:** Lesson 16 - Agent Reliability
