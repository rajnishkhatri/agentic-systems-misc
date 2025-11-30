# Task 2: Understanding GuardRails Through Demo Implementation

## Overview
This document traces the actual execution flow through the notebook demo (`03_guardrails_validation_traces.ipynb`) and the cached validation traces, understanding GuardRail creation, validation execution, trace generation, and PromptGuardRail flow.

## 1. GuardRail Creation Flow

### Cell 1: Basic GuardRail Creation

**Code:**
```python
guardrail = GuardRail(
    name="invoice_validator",
    description="Validates invoice extraction outputs",
    constraints=[
        BuiltInValidators.no_pii(),
        BuiltInValidators.required_fields(["vendor", "amount"]),
    ],
)
```

**Execution Flow:**
```
1. BuiltInValidators.no_pii()
   └─> Returns Constraint(
         name="no_pii",
         check_fn="pii",
         params={},
         severity=Severity.ERROR,
         on_fail=FailAction.REJECT
       )

2. BuiltInValidators.required_fields(["vendor", "amount"])
   └─> Returns Constraint(
         name="required_fields",
         check_fn="required",
         params={"fields": ["vendor", "amount"]},
         severity=Severity.ERROR,
         on_fail=FailAction.REJECT
       )

3. GuardRail instantiation
   └─> GuardRail(
         name="invoice_validator",
         description="...",
         constraints=[Constraint(...), Constraint(...)],
         on_fail_default=FailAction.REJECT
       )
```

**Result:**
- GuardRail object created with 2 constraints
- Validation: `is_valid=True`, `total_errors=0`

### Cell 2: Constraint Creation with Severity Levels

**Code:**
```python
ssn_check = Constraint(
    name="no_ssn",
    check_fn="pii",
    severity=Severity.ERROR,
    on_fail=FailAction.REJECT,
)

length_warning = Constraint(
    name="reasonable_length",
    check_fn="length",
    params={"min_len": 10, "max_len": 500},
    severity=Severity.WARNING,
    on_fail=FailAction.LOG,
)
```

**Key Insights:**
- **ERROR severity**: Blocks validation if fails
- **WARNING severity**: Logs but doesn't block
- **INFO severity**: Purely informational/audit

## 2. Validation Execution Flow

### Cell 3: PII Detection with Real Data

**Execution Flow:**
```
1. Load pii_examples_50.json
   └─> 50 examples loaded

2. Create PII guardrail
   guardrail = GuardRail(
       name="pii_detector",
       constraints=[BuiltInValidators.no_pii()],
       on_fail_default=FailAction.REJECT
   )

3. For each test sample:
   a. validator.validate({"output": sample["text"]}, guardrail)
   
   b. GuardRailValidator.validate() execution:
      - Computes input_hash: SHA256 of input_data
      - Iterates through constraints
      - For each constraint:
        * Calls _run_constraint(data, constraint)
        * Gets check_fn from constraint: "pii"
        * Looks up: BuiltInValidators.check_pii
        * Executes: check_pii(data, field="output")
        * Returns: (passed, message) tuple
        * Creates ValidationEntry:
          {
            constraint_name: "no_pii",
            passed: True/False,
            message: "No PII patterns detected" / "Potential SSN detected",
            severity: Severity.ERROR,
            timestamp: datetime.now(UTC),
            input_excerpt: str(data)[:200] if failed
          }
        * Appends to entries list
        * Appends to validator._trace
      
      - Aggregates results:
        * total_errors = count(entries where not passed and severity=ERROR)
        * total_warnings = count(entries where not passed and severity=WARNING)
        * is_valid = (total_errors == 0)
        * action_taken = None if valid, else guardrail.on_fail_default
      
      - Returns ValidationResult:
        {
          guardrail_name: "pii_detector",
          input_hash: "abc123...",
          is_valid: False,
          entries: [ValidationEntry(...)],
          total_errors: 1,
          total_warnings: 0,
          validation_time_ms: 5,
          action_taken: FailAction.REJECT
        }
```

**Example Results:**
- SSN detected: `is_valid=False`, message="Potential SSN detected"
- Credit card detected: `is_valid=False`, message="Potential credit card number detected"
- Email detected: `is_valid=False`, message="Email address detected"

### Cell 4: Built-in Validators Demo

**Length Check Flow:**
```
Input: {"output": "Hi"}  # len=2
Constraint: length_check(min_len=5, max_len=100)

Execution:
1. _run_constraint({"output": "Hi"}, length_constraint)
2. Gets check_fn="length" → BuiltInValidators.check_length()
3. check_length(data, min_len=5, max_len=100, field="output")
   - Gets value = data.get("output", "") = "Hi"
   - length = len("Hi") = 2
   - if length < min_len: return (False, "Length 2 is below minimum 5")
4. Creates ValidationEntry(passed=False, message="Length 2 is below minimum 5")
5. Returns ValidationResult(is_valid=False, total_errors=1)
```

**Regex Match Flow:**
```
Input: {"output": "INV-2024-0001"}
Constraint: regex_match(r"INV-\d{4}-\d{4}")

Execution:
1. check_regex(data, pattern=r"INV-\d{4}-\d{4}", field="output")
2. value = "INV-2024-0001"
3. re.search(pattern, value) → Match found
4. Returns (True, "Value matches pattern 'INV-\\d{4}-\\d{4}'")
```

**Confidence Range Flow:**
```
Input: {"confidence": 0.65}
Constraint: confidence_range(min_conf=0.7, max_conf=1.0)

Execution:
1. check_confidence(data, min_conf=0.7, max_conf=1.0, field="confidence")
2. value = data.get("confidence") = 0.65
3. conf = float(0.65) = 0.65
4. if conf < min_conf: return (False, "Confidence 0.65 is below minimum 0.7")
```

### Cell 5: Combined Validators

**Multi-Constraint Validation Flow:**
```
Input: {
  "vendor_name": "Acme Corporation",
  "invoice_number": "INV-2024-0042",
  "total_amount": 1250.00,
  "confidence": 0.95,
  "output": "Invoice from Acme Corporation, total $1,250.00"
}

GuardRail with 4 constraints:
1. no_pii()
2. required_fields(["vendor_name", "invoice_number", "total_amount"])
3. confidence_range(min_conf=0.8, max_conf=1.0)
4. length_check(min_len=10, max_len=5000)

Execution:
1. Schema validation (if schema_name specified) → Skip
2. Constraint 1: no_pii
   └─> check_pii() → (True, "No PII patterns detected")
   └─> ValidationEntry(passed=True)
3. Constraint 2: required_fields
   └─> check_required() → (True, "All required fields present")
   └─> ValidationEntry(passed=True)
4. Constraint 3: confidence_range
   └─> check_confidence() → (True, "Confidence 0.95 is within range [0.8, 1.0]")
   └─> ValidationEntry(passed=True)
5. Constraint 4: length_check
   └─> check_length() → (True, "Length 46 is within bounds [10, 5000]")
   └─> ValidationEntry(passed=True)

Aggregation:
- total_errors = 0 (all passed)
- is_valid = True
- action_taken = None
```

## 3. PromptGuardRail Flow

### Cell 6: PromptGuardRail for LLM Outputs

**Code:**
```python
prompt_guardrail = PromptGuardRail(
    name="invoice_extraction_prompt",
    required_fields=["vendor_name", "invoice_number", "total_amount"],
    constraints=[
        BuiltInValidators.json_parseable(),
        BuiltInValidators.no_pii(),
    ],
)
```

**Execution Flow:**
```
1. validator.validate_prompt_output(output_string, prompt_guardrail)

2. validate_prompt_output() execution:
   a. Computes input_hash: SHA256 of {"output": output_string}
   
   b. JSON parsing attempt:
      try:
          output_data = json.loads(output_string)
          if isinstance(output_data, dict):
              # Check required fields
              for field in guardrail.required_fields:
                  entry = ValidationEntry(
                      constraint_name=f"required_field_{field}",
                      passed=(field in output_data),
                      message=f"Required field '{field}' is {'present' if field in output_data else 'missing'}",
                      severity=Severity.ERROR,
                      input_excerpt=output_string[:100] if len(output_string) > 100 else output_string
                  )
                  entries.append(entry)
                  validator._trace.append(entry)
                  if not entry.passed:
                      errors += 1
      except json.JSONDecodeError:
          # Not JSON, skip field checking
          pass
   
   c. Run constraints:
      for constraint in guardrail.constraints:
          entry = _run_constraint({"output": output_string}, constraint)
          entries.append(entry)
          validator._trace.append(entry)
          if not entry.passed:
              if constraint.severity == Severity.ERROR:
                  errors += 1
              elif constraint.severity == Severity.WARNING:
                  warnings += 1
   
   d. Return ValidationResult

3. Example: Invalid JSON
   Input: "This is not JSON at all"
   
   Execution:
   - JSON parsing fails → json.JSONDecodeError
   - Skip required field checking
   - Run constraints:
     * json_parseable constraint:
       check_json({"output": "This is not JSON at all"}, field="output")
       └─> json.loads("This is not JSON at all") → JSONDecodeError
       └─> Returns (False, "Invalid JSON: Expecting value: line 1 column 1 (char 0)")
     * no_pii constraint:
       check_pii({"output": "This is not JSON at all"}) → (True, "No PII patterns detected")
   
   Result:
   - is_valid = False
   - total_errors = 1
   - action_taken = FailAction.REJECT
```

## 4. Trace Generation Flow

### Cell 7: Validation Trace Analysis

**Execution Flow:**
```
1. validator.get_validation_trace()
   └─> Returns validator._trace.copy()
       (List of all ValidationEntry objects from session)

2. Trace Statistics:
   - Total entries: 50
   - Passed: 33
   - Failed: 17
   - Pass rate: 66.0%

3. Constraint Frequency:
   - no_pii: 12 times
   - length_check: 7 times
   - confidence_range: 7 times
   - required_fields: 5 times
   - json_parseable: 4 times

4. Failed Validations Analysis:
   - Filter entries where passed=False
   - Group by constraint_name
   - Show recent failures with input excerpts
```

**Trace Structure:**
```python
validator._trace = [
    ValidationEntry(
        constraint_name="no_pii",
        passed=True,
        message="No PII patterns detected",
        severity=Severity.ERROR,
        timestamp=datetime(...),
        input_excerpt=None
    ),
    ValidationEntry(
        constraint_name="no_pii",
        passed=False,
        message="Potential SSN detected",
        severity=Severity.ERROR,
        timestamp=datetime(...),
        input_excerpt="{'output': 'Loan application: John Gonzalez, SSN 490-86-8668...'}"
    ),
    # ... 48 more entries
]
```

### Cell 8: Trace Export

**Execution Flow:**
```
1. validator.export_trace(filepath)

2. export_trace() execution:
   a. Creates export_data dictionary:
      {
          "exported_at": datetime.now(UTC).isoformat(),
          "entry_count": len(validator._trace),
          "entries": [e.model_dump(mode="json") for e in validator._trace]
      }
   
   b. Writes to JSON file:
      with open(filepath, "w") as f:
          json.dump(export_data, f, indent=2, default=str)
   
   c. File structure:
      {
          "exported_at": "2025-11-27T18:23:56.958174+00:00",
          "entry_count": 50,
          "entries": [
              {
                  "constraint_name": "no_pii",
                  "passed": true,
                  "message": "No PII patterns detected",
                  "severity": "error",
                  "timestamp": "2025-11-27T18:23:56.906696Z",
                  "input_excerpt": null,
                  "fix_applied": null
              },
              // ... 49 more entries
          ]
      }
```

**Key Features:**
- All ValidationEntry objects serialized to JSON
- Timestamps preserved in ISO format
- Input excerpts included for failed validations
- Enables audit trail and debugging

## 5. Documentation Generation Flow

### Cell 9 & 10: Self-Documentation

**Execution Flow:**
```
1. guardrail.document()

2. document() execution (GuardRail class):
   a. Builds markdown string:
      - Header: # {name}
      - Version: **Version:** {version}
      - Description: **Description:** {description}
      - Schema: **Schema:** `{schema_name}` (if present)
   
   b. Constraints section:
      for constraint in self.constraints:
          - ### {constraint.name}
          - **Description:** {constraint.description}
          - **Severity:** {constraint.severity.value}
          - **On Fail:** {constraint.on_fail.value}
          - **Params:** `{json.dumps(constraint.params)}` (if present)
   
   c. Returns markdown string

3. PromptGuardRail.document() (extends GuardRail):
   a. Calls super().document() for base documentation
   
   b. Adds prompt-specific sections:
      - Prompt Template (if prompt_template present)
      - Required Fields (if required_fields present)
      - Optional Fields (if optional_fields present)
      - Example Valid Output (if example_valid_output present)
      - Example Invalid Output (if example_invalid_output present)
   
   c. Returns extended markdown string
```

**Example Output:**
```markdown
# invoice_extraction_v2

**Version:** 2.0.0

**Description:** Validates invoice extraction agent outputs

## Constraints

### no_pii
- **Description:** Output must not contain PII (SSN, credit card, etc.)
- **Severity:** error
- **On Fail:** reject

### required_fields
- **Description:** Required fields: vendor_name, invoice_number, total_amount
- **Severity:** error
- **On Fail:** reject
- **Params:** `{"fields": ["vendor_name", "invoice_number", "total_amount"]}`
```

## 6. Complete Execution Sequence

### End-to-End Flow for One Validation

```
1. GuardRail Creation
   GuardRail(
       name="invoice_validator",
       constraints=[...]
   )
   ↓
2. GuardRailValidator Initialization
   validator = GuardRailValidator()
   validator._trace = []
   validator._schemas = {}
   ↓
3. Validation Call
   result = validator.validate(input_data, guardrail)
   ↓
4. Validation Execution
   a. Compute input_hash (SHA256)
   b. Start timer
   c. Schema validation (if schema_name specified)
   d. For each constraint:
      - _run_constraint(data, constraint)
      - Get check function: getattr(BuiltInValidators, f"check_{check_fn}")
      - Execute check function: check_fn(data, **params)
      - Create ValidationEntry
      - Append to entries list
      - Append to validator._trace
   e. Calculate duration
   f. Aggregate results (errors, warnings, is_valid)
   g. Determine action_taken
   ↓
5. Return ValidationResult
   ValidationResult(
       guardrail_name="invoice_validator",
       input_hash="abc123...",
       is_valid=True/False,
       entries=[...],
       total_errors=0,
       total_warnings=0,
       validation_time_ms=5,
       action_taken=None/FailAction.REJECT
   )
   ↓
6. Trace Accumulation
   validator._trace now contains all ValidationEntry objects
   ↓
7. Trace Export (optional)
   validator.export_trace(filepath)
   └─> Writes JSON file with all entries
```

## 7. Key Insights from Demo

1. **Trace Persistence**: The `validator._trace` list accumulates all validation entries across multiple validations, enabling session-wide analysis.

2. **Constraint Reusability**: BuiltInValidators provide factory methods that create reusable Constraint objects with consistent configurations.

3. **Severity Levels**: Different severity levels (ERROR, WARNING, INFO) allow fine-grained control over validation behavior without blocking execution.

4. **Input Excerpts**: Failed validations include `input_excerpt` fields (first 200 chars) for debugging, while passed validations omit them to save space.

5. **PromptGuardRail Specialization**: Extends base GuardRail with LLM-specific features (prompt templates, required/optional fields, examples) while maintaining compatibility with standard validation flow.

6. **Self-Documentation**: The `document()` method generates markdown documentation automatically, ensuring guardrails are self-describing and maintainable.

7. **Export Format**: Trace export uses JSON with ISO timestamps, making it easy to integrate with audit systems and analysis tools.
