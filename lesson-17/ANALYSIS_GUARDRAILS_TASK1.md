# Task 1: Understanding GuardRails Through Data Analysis

## Overview
This document analyzes how `guardrails.py` works with real data from the `data/` folder, mapping PII detection patterns, understanding data structures, and tracing validation scenarios.

## 1. PII Detection Patterns Mapping

### PII Types in `pii_examples_50.json`

The dataset contains 50 examples with the following PII type distribution:
- **SSN**: 8 examples (pattern: `XXX-XX-XXXX`)
- **Credit Card**: 9 examples (pattern: `XXXX-XXXX-XXXX-XXXX`)
- **Email**: 18 examples (pattern: `user@domain.com`)
- **Phone**: 21 examples (pattern: `+1-XXX-XXX-XXXX` or variations)
- **Medical Record Number**: 9 examples (pattern: `MRN-XXXXXXXX`)
- **Passport**: 10 examples (pattern: `PXXXXXXXX`)
- **Driver's License**: 6 examples (pattern: `DL-XX-XXXXXXX`)
- **Name**: 50 examples (all examples contain names)

### Mapping to `BuiltInValidators.check_pii()` Implementation

The `check_pii()` method in `guardrails.py` (lines 649-681) uses regex patterns to detect PII:

#### 1. SSN Detection
```python
ssn_pattern = r"\b\d{3}-\d{2}-\d{4}\b"
```
- **Matches**: `490-86-8668`, `123-45-6789`
- **Example from data**: PII-001 contains "SSN 490-86-8668"
- **Validation flow**: 
  - Input: `{"output": "Loan application: John Gonzalez, SSN 490-86-8668..."}`
  - Pattern match → Returns `(False, "Potential SSN detected")`
  - Creates `ValidationEntry` with `passed=False`, `message="Potential SSN detected"`

#### 2. Credit Card Detection
```python
cc_pattern = r"\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b"
```
- **Matches**: `2403-8962-2133-9727`, `2403 8962 2133 9727`, `2403896221339727`
- **Example from data**: PII-002 contains "Card: 2403-8962-2133-9727"
- **Validation flow**:
  - Input: `{"output": "Hotel reservation: Mary Davis, Card: 2403-8962-2133-9727"}`
  - Pattern match → Returns `(False, "Potential credit card number detected")`

#### 3. Email Detection
```python
email_pattern = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"
```
- **Matches**: `matthewwilson@work.org`, `user@example.com`
- **Example from data**: PII-004 contains email addresses
- **Validation flow**:
  - Input: `{"output": "User Matthew Wilson requests password reset. Email: matthewwilson@work.org"}`
  - Pattern match → Returns `(False, "Email address detected")`

#### 4. Phone Number Detection
```python
phone_pattern = r"\b\+?1?[-.\s]?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b"
```
- **Matches**: `+1-765-351-8041`, `(765) 351-8041`, `765-351-8041`
- **Example from data**: Multiple examples contain phone numbers
- **Validation flow**:
  - Input: `{"output": "Contact: +1-765-351-8041"}`
  - Pattern match → Returns `(False, "Potential phone number detected")`

### Validation Flow Trace

For a PII detection validation:

```
1. Input Data
   {"output": "Loan application: John Gonzalez, SSN 490-86-8668. Annual income verified."}

2. GuardRailValidator.validate()
   └─> GuardRail with constraint: BuiltInValidators.no_pii()

3. _run_constraint()
   └─> Gets check_fn="pii" → BuiltInValidators.check_pii()

4. check_pii() execution
   └─> Checks SSN pattern: r"\b\d{3}-\d{2}-\d{4}\b"
   └─> Match found: "490-86-8668"
   └─> Returns: (False, "Potential SSN detected")

5. ValidationEntry creation
   {
     "constraint_name": "no_pii",
     "passed": false,
     "message": "Potential SSN detected",
     "severity": "error",
     "input_excerpt": "{'output': 'Loan application: John Gonzalez, SSN 490-86-8668...'}",
     "timestamp": "2025-11-27T18:23:56.919680Z"
   }

6. ValidationResult aggregation
   {
     "guardrail_name": "pii_detector",
     "is_valid": false,
     "total_errors": 1,
     "total_warnings": 0,
     "entries": [ValidationEntry(...)],
     "action_taken": "reject"
   }
```

## 2. Data Structure Mapping

### Workflow Traces Structure

The `invoice_processing_trace.json` shows how workflow data structures align with guardrail validation:

#### Task Plan Structure
```json
{
  "task_plan": {
    "steps": [
      {
        "step_id": "extract_vendor",
        "agent_id": "invoice-extractor-v2",
        "expected_outputs": ["vendor_name", "amount", "confidence"]
      }
    ]
  }
}
```

**GuardRail Validation Mapping:**
- `expected_outputs` → `required_fields` constraint
- `confidence` → `confidence_range` constraint
- Output data → Validated against `GuardRail` with multiple constraints

#### Execution Trace Events
```json
{
  "event_type": "decision",
  "metadata": {
    "decision": "output_validation",
    "guardrail_name": "invoice_extraction_output",
    "is_valid": true,
    "total_errors": 0,
    "constraint_results": [...]
  }
}
```

**Integration Point:**
- BlackBoxRecorder logs validation results as `DECISION` events
- `metadata` contains full `ValidationResult` structure
- Enables post-incident analysis of validation failures

### Agent Metadata Structure

The `agent_metadata_10.json` shows how agents define policies that can be converted to guardrails:

#### Policy Declaration
```json
{
  "agent_id": "invoice-extractor-v2",
  "policies": [
    {
      "policy_id": "invoice-extractor-v2-policy-002",
      "policy_type": "data_access",
      "constraints": {
        "allowed_fields": ["vendor_name", "invoice_number", "amount", "date"],
        "restricted_fields": ["bank_account", "routing_number"],
        "requires_encryption": true
      }
    }
  ]
}
```

**GuardRail Conversion (via `policy_bridge.py`):**
- `data_access` policy → Can convert to `GuardRail` with constraints
- `allowed_fields` → Could map to `required_fields` constraint
- `restricted_fields` → Could map to custom constraint checking field absence

#### Capability Output Schemas
```json
{
  "capabilities": [
    {
      "name": "extract_vendor",
      "output_schema": {
        "type": "object",
        "properties": {
          "vendor_name": {"type": "string"},
          "confidence": {"type": "number"}
        }
      }
    }
  ]
}
```

**GuardRail Schema Validation:**
- `output_schema` → Can be registered as Pydantic schema
- `GuardRail.schema_name` → References registered schema
- `GuardRailValidator.register_schema()` → Enables structural validation

## 3. Validation Scenarios

### Scenario 1: Valid Output (All Constraints Pass)

**Input Data:**
```json
{
  "vendor_name": "Acme Corporation",
  "invoice_number": "INV-2024-0042",
  "total_amount": 1250.00,
  "confidence": 0.95,
  "output": "Invoice from Acme Corporation, total $1,250.00"
}
```

**GuardRail:**
```python
GuardRail(
    name="invoice_extraction_v2",
    constraints=[
        BuiltInValidators.no_pii(),
        BuiltInValidators.required_fields(["vendor_name", "invoice_number", "total_amount"]),
        BuiltInValidators.confidence_range(min_conf=0.8, max_conf=1.0),
        BuiltInValidators.length_check(min_len=10, max_len=5000),
    ]
)
```

**Validation Result:**
- `no_pii`: ✅ Passed - "No PII patterns detected"
- `required_fields`: ✅ Passed - "All required fields present"
- `confidence_range`: ✅ Passed - "Confidence 0.95 is within range [0.8, 1.0]"
- `length_check`: ✅ Passed - "Length 46 is within bounds [10, 5000]"
- **Overall**: `is_valid=True`, `total_errors=0`

### Scenario 2: Missing Required Field

**Input Data:**
```json
{
  "vendor_name": "Tech Solutions",
  "total_amount": 500.00,
  "confidence": 0.88,
  "output": "Invoice from Tech Solutions"
}
```

**Validation Result:**
- `no_pii`: ✅ Passed
- `required_fields`: ❌ Failed - "Missing required fields: invoice_number"
- `confidence_range`: ✅ Passed
- `length_check`: ✅ Passed
- **Overall**: `is_valid=False`, `total_errors=1`, `action_taken="reject"`

### Scenario 3: PII Violation

**Input Data:**
```json
{
  "vendor_name": "Payroll Inc",
  "invoice_number": "INV-2024-0100",
  "total_amount": 2000.00,
  "confidence": 0.92,
  "output": "Employee SSN: 123-45-6789"
}
```

**Validation Result:**
- `no_pii`: ❌ Failed - "Potential SSN detected"
- `required_fields`: ✅ Passed
- `confidence_range`: ✅ Passed
- `length_check`: ✅ Passed
- **Overall**: `is_valid=False`, `total_errors=1`, `action_taken="reject"`

### Scenario 4: Low Confidence Score

**Input Data:**
```json
{
  "vendor_name": "Global Services",
  "invoice_number": "INV-2024-0099",
  "total_amount": 750.00,
  "confidence": 0.65,
  "output": "Invoice extraction uncertain"
}
```

**Validation Result:**
- `no_pii`: ✅ Passed
- `required_fields`: ✅ Passed
- `confidence_range`: ❌ Failed - "Confidence 0.65 is below minimum 0.8"
- `length_check`: ✅ Passed
- **Overall**: `is_valid=False`, `total_errors=1`, `action_taken="reject"`

### Scenario 5: Invalid JSON Format (PromptGuardRail)

**Input Data:**
```json
{
  "output": "This is not JSON at all"
}
```

**GuardRail:**
```python
PromptGuardRail(
    name="invoice_extraction_prompt",
    required_fields=["vendor_name", "invoice_number", "total_amount"],
    constraints=[BuiltInValidators.json_parseable()]
)
```

**Validation Result:**
- `json_parseable`: ❌ Failed - "Invalid JSON: Expecting value: line 1 column 1 (char 0)"
- **Overall**: `is_valid=False`, `total_errors=1`

## 4. Schema Compatibility

### Pydantic Model Alignment

All data structures in the `data/` folder are compatible with Pydantic models:

1. **PII Examples** → Can be validated with `check_pii()` constraint
2. **Agent Metadata** → Uses `AgentFacts` Pydantic model
3. **Workflow Traces** → Uses `TaskPlan`, `TraceEvent` Pydantic models
4. **Validation Results** → Uses `ValidationResult`, `ValidationEntry` Pydantic models

### Data Flow Compatibility

```
pii_examples_50.json
  └─> {"text": "..."} → GuardRailValidator.validate({"output": text}, guardrail)
      └─> ValidationResult

agent_metadata_10.json
  └─> AgentFacts.policies → policy_to_guardrail(policy)
      └─> GuardRail → GuardRailValidator.validate(output, guardrail)

workflows/*.json
  └─> execution_trace.events → Can include validation events
      └─> TraceEvent(event_type="decision", metadata={validation_result})
```

## 5. Key Insights

1. **PII Detection Coverage**: The `check_pii()` method covers 4 common PII types (SSN, credit card, email, phone) but the dataset includes 8 types. Medical records, passports, and driver's licenses are not detected by the current implementation.

2. **Data Structure Alignment**: Workflow traces can include validation results in `DECISION` events, enabling full audit trails.

3. **Policy-to-GuardRail Conversion**: Agent policies can be automatically converted to guardrails via `policy_bridge.py`, creating a seamless flow from policy declaration to enforcement.

4. **Validation Traceability**: Every validation creates detailed `ValidationEntry` records with timestamps, input excerpts, and constraint results, enabling comprehensive debugging and auditing.

5. **Schema Validation Integration**: Agent capability output schemas can be registered as Pydantic models for structural validation alongside constraint-based validation.
