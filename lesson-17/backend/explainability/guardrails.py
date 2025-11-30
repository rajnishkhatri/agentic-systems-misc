"""Declarative GuardRails - Validators with trace generation.

This module provides Guardrails-style declarative validators that document
prompt structures, constraints, and validation results for agent transparency.

Inspired by:
- Guardrails AI (github.com/ShreyaR/guardrails)
- lesson-16/backend/reliability/validation.py - Pydantic patterns
- lesson-16/backend/reliability/isolation.py - Result[T,E] type

Key Features:
- Declarative constraint definitions
- Rich validation traces for debugging
- Prompt structure documentation
- Multiple failure handling strategies

Example:
    >>> validator = GuardRailValidator()
    >>> guardrail = GuardRail(
    ...     name="invoice_extraction",
    ...     description="Validates invoice extraction output",
    ...     constraints=[BuiltInValidators.length_check(1, 1000)]
    ... )
    >>> result = validator.validate({"vendor": "Acme"}, guardrail)
    >>> print(result.is_valid)
"""

from __future__ import annotations

import hashlib
import json
import re
from datetime import UTC, datetime
from enum import Enum
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field, ValidationError


class FailAction(str, Enum):
    """Actions to take when validation fails."""

    REJECT = "reject"  # Reject output entirely
    FIX = "fix"  # Attempt automatic fix
    ESCALATE = "escalate"  # Escalate to human review
    LOG = "log"  # Log and continue (non-blocking)
    RETRY = "retry"  # Retry with modified prompt


class Severity(str, Enum):
    """Severity levels for validation constraints."""

    ERROR = "error"  # Must pass for valid output
    WARNING = "warning"  # Should pass but not blocking
    INFO = "info"  # Informational only


class Constraint(BaseModel):
    """Single validation constraint.

    Defines a validation rule with its parameters and failure handling.

    Attributes:
        name: Unique name for this constraint
        description: Human-readable description
        check_fn: Name of the validation function to use
        params: Parameters for the validation function
        severity: How severe a failure is (error, warning, info)
        on_fail: Action to take on failure
    """

    name: str
    description: str
    check_fn: str
    params: dict[str, Any] = Field(default_factory=dict)
    severity: Severity = Severity.ERROR
    on_fail: FailAction = FailAction.REJECT

    class Config:
        extra = "forbid"


class ValidationEntry(BaseModel):
    """Single validation result entry.

    Records the outcome of checking one constraint.

    Attributes:
        constraint_name: Name of the constraint checked
        passed: Whether the constraint passed
        message: Descriptive message about the result
        severity: Severity level of this constraint
        timestamp: When validation occurred
        input_excerpt: Relevant portion of input (for debugging)
        fix_applied: Description of fix if any was applied
    """

    constraint_name: str
    passed: bool
    message: str
    severity: Severity
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))
    input_excerpt: str | None = None
    fix_applied: str | None = None

    class Config:
        extra = "forbid"


class ValidationResult(BaseModel):
    """Complete validation result with trace.

    Aggregates all constraint checks for a single validation run.

    Attributes:
        guardrail_name: Name of the guardrail used
        input_hash: SHA256 hash of input for integrity
        is_valid: Whether overall validation passed
        entries: List of individual constraint results
        total_errors: Count of ERROR severity failures
        total_warnings: Count of WARNING severity failures
        validation_time_ms: Time taken to validate in milliseconds
        action_taken: Final action taken based on results
    """

    guardrail_name: str
    input_hash: str
    is_valid: bool
    entries: list[ValidationEntry] = Field(default_factory=list)
    total_errors: int = 0
    total_warnings: int = 0
    validation_time_ms: int = 0
    action_taken: FailAction | None = None

    class Config:
        extra = "forbid"


class GuardRail(BaseModel):
    """Declarative validator with documentation and trace generation.

    Defines a set of constraints that should be checked against inputs,
    with configurable failure handling.

    Attributes:
        name: Unique name for this guardrail
        description: Human-readable description
        version: Version string for this guardrail
        schema: Optional Pydantic model for structural validation
        constraints: List of constraints to check
        on_fail_default: Default action when constraints fail
    """

    name: str
    description: str
    version: str = "1.0.0"
    schema_name: str | None = None  # Name of Pydantic model (for documentation)
    constraints: list[Constraint] = Field(default_factory=list)
    on_fail_default: FailAction = FailAction.REJECT

    class Config:
        extra = "forbid"
        arbitrary_types_allowed = True

    def document(self) -> str:
        """Generate human-readable documentation of the guardrail.

        Returns:
            Markdown-formatted documentation string
        """
        doc = f"# {self.name}\n\n"
        doc += f"**Version:** {self.version}\n\n"
        doc += f"**Description:** {self.description}\n\n"

        if self.schema_name:
            doc += f"**Schema:** `{self.schema_name}`\n\n"

        if self.constraints:
            doc += "## Constraints\n\n"
            for c in self.constraints:
                doc += f"### {c.name}\n"
                doc += f"- **Description:** {c.description}\n"
                doc += f"- **Severity:** {c.severity.value}\n"
                doc += f"- **On Fail:** {c.on_fail.value}\n"
                if c.params:
                    doc += f"- **Params:** `{json.dumps(c.params)}`\n"
                doc += "\n"

        return doc


class PromptGuardRail(GuardRail):
    """Documents prompt structure and constraints for transparency.

    Extends GuardRail with prompt-specific fields for documenting
    LLM prompt expectations.

    Attributes:
        prompt_template: Template string showing prompt structure
        required_fields: Fields that must be present in output
        optional_fields: Fields that may be present
        example_valid_output: Example of valid output
        example_invalid_output: Example of invalid output
    """

    prompt_template: str = ""
    required_fields: list[str] = Field(default_factory=list)
    optional_fields: list[str] = Field(default_factory=list)
    example_valid_output: str = ""
    example_invalid_output: str = ""

    def document(self) -> str:
        """Generate documentation including prompt structure.

        Returns:
            Markdown-formatted documentation string
        """
        doc = super().document()

        if self.prompt_template:
            doc += "## Prompt Template\n\n"
            doc += f"```\n{self.prompt_template}\n```\n\n"

        if self.required_fields:
            doc += "## Required Fields\n\n"
            for field in self.required_fields:
                doc += f"- `{field}`\n"
            doc += "\n"

        if self.optional_fields:
            doc += "## Optional Fields\n\n"
            for field in self.optional_fields:
                doc += f"- `{field}`\n"
            doc += "\n"

        if self.example_valid_output:
            doc += "## Example Valid Output\n\n"
            doc += f"```json\n{self.example_valid_output}\n```\n\n"

        if self.example_invalid_output:
            doc += "## Example Invalid Output\n\n"
            doc += f"```json\n{self.example_invalid_output}\n```\n\n"

        return doc


class GuardRailValidator:
    """Executes guardrails and produces rich validation traces.

    Provides validation execution with detailed trace generation
    for debugging and auditing.

    Attributes:
        _trace: List of validation entries from all validations
        _schemas: Registry of Pydantic schemas for structural validation
    """

    def __init__(self) -> None:
        """Initialize validator with empty trace."""
        self._trace: list[ValidationEntry] = []
        self._schemas: dict[str, type[BaseModel]] = {}

    def register_schema(self, name: str, schema: type[BaseModel]) -> None:
        """Register a Pydantic schema for structural validation.

        Args:
            name: Name to register the schema under
            schema: Pydantic BaseModel class
        """
        self._schemas[name] = schema

    def validate(
        self, input_data: dict[str, Any], guardrail: GuardRail
    ) -> ValidationResult:
        """Validate input against guardrail, returning detailed result.

        Args:
            input_data: Dictionary of input data to validate
            guardrail: GuardRail defining constraints to check

        Returns:
            ValidationResult with detailed trace

        Raises:
            TypeError: If arguments are wrong type
        """
        if not isinstance(input_data, dict):
            raise TypeError("input_data must be a dictionary")
        if not isinstance(guardrail, GuardRail):
            raise TypeError("guardrail must be a GuardRail instance")

        start_time = datetime.now(UTC)
        entries: list[ValidationEntry] = []
        errors = 0
        warnings = 0

        # Compute input hash
        input_hash = self._compute_hash(input_data)

        # Schema validation if specified
        if guardrail.schema_name and guardrail.schema_name in self._schemas:
            schema = self._schemas[guardrail.schema_name]
            entry = self._validate_schema(input_data, schema)
            entries.append(entry)
            self._trace.append(entry)
            if not entry.passed:
                if entry.severity == Severity.ERROR:
                    errors += 1
                elif entry.severity == Severity.WARNING:
                    warnings += 1

        # Run each constraint
        for constraint in guardrail.constraints:
            entry = self._run_constraint(input_data, constraint)
            entries.append(entry)
            self._trace.append(entry)

            if not entry.passed:
                if constraint.severity == Severity.ERROR:
                    errors += 1
                elif constraint.severity == Severity.WARNING:
                    warnings += 1

        # Calculate timing
        end_time = datetime.now(UTC)
        duration_ms = int((end_time - start_time).total_seconds() * 1000)

        # Determine if valid (no errors)
        is_valid = errors == 0

        # Determine action
        action = None if is_valid else guardrail.on_fail_default

        return ValidationResult(
            guardrail_name=guardrail.name,
            input_hash=input_hash,
            is_valid=is_valid,
            entries=entries,
            total_errors=errors,
            total_warnings=warnings,
            validation_time_ms=duration_ms,
            action_taken=action,
        )

    def validate_prompt_output(
        self, output: str, guardrail: PromptGuardRail
    ) -> ValidationResult:
        """Validate LLM output against prompt guardrail.

        Args:
            output: String output from LLM
            guardrail: PromptGuardRail with prompt-specific constraints

        Returns:
            ValidationResult with detailed trace

        Raises:
            TypeError: If arguments are wrong type
        """
        if not isinstance(output, str):
            raise TypeError("output must be a string")
        if not isinstance(guardrail, PromptGuardRail):
            raise TypeError("guardrail must be a PromptGuardRail instance")

        start_time = datetime.now(UTC)
        entries: list[ValidationEntry] = []
        errors = 0
        warnings = 0

        input_hash = self._compute_hash({"output": output})

        # Check required fields if output is JSON
        try:
            output_data = json.loads(output)
            if isinstance(output_data, dict):
                for field in guardrail.required_fields:
                    entry = ValidationEntry(
                        constraint_name=f"required_field_{field}",
                        passed=field in output_data,
                        message=(
                            f"Required field '{field}' is present"
                            if field in output_data
                            else f"Required field '{field}' is missing"
                        ),
                        severity=Severity.ERROR,
                        input_excerpt=output[:100] if len(output) > 100 else output,
                    )
                    entries.append(entry)
                    self._trace.append(entry)
                    if not entry.passed:
                        errors += 1
        except json.JSONDecodeError:
            # Not JSON, skip field checking
            pass

        # Run constraints
        for constraint in guardrail.constraints:
            entry = self._run_constraint({"output": output}, constraint)
            entries.append(entry)
            self._trace.append(entry)

            if not entry.passed:
                if constraint.severity == Severity.ERROR:
                    errors += 1
                elif constraint.severity == Severity.WARNING:
                    warnings += 1

        end_time = datetime.now(UTC)
        duration_ms = int((end_time - start_time).total_seconds() * 1000)

        is_valid = errors == 0
        action = None if is_valid else guardrail.on_fail_default

        return ValidationResult(
            guardrail_name=guardrail.name,
            input_hash=input_hash,
            is_valid=is_valid,
            entries=entries,
            total_errors=errors,
            total_warnings=warnings,
            validation_time_ms=duration_ms,
            action_taken=action,
        )

    def get_validation_trace(self) -> list[ValidationEntry]:
        """Get all validation entries from current session.

        Returns:
            List of ValidationEntry in chronological order
        """
        return self._trace.copy()

    def clear_trace(self) -> None:
        """Clear the validation trace."""
        self._trace.clear()

    def export_trace(self, filepath: Path) -> None:
        """Export validation trace to JSON file.

        Args:
            filepath: Path where trace should be written

        Raises:
            TypeError: If filepath is not a Path
        """
        if not isinstance(filepath, Path):
            raise TypeError("filepath must be a Path")

        filepath.parent.mkdir(parents=True, exist_ok=True)

        export_data = {
            "exported_at": datetime.now(UTC).isoformat(),
            "entry_count": len(self._trace),
            "entries": [e.model_dump(mode="json") for e in self._trace],
        }

        with open(filepath, "w") as f:
            json.dump(export_data, f, indent=2, default=str)

    def _validate_schema(
        self, data: dict[str, Any], schema: type[BaseModel]
    ) -> ValidationEntry:
        """Validate data against a Pydantic schema.

        Args:
            data: Data to validate
            schema: Pydantic model class

        Returns:
            ValidationEntry with result
        """
        try:
            schema(**data)
            return ValidationEntry(
                constraint_name=f"schema_{schema.__name__}",
                passed=True,
                message=f"Data matches schema {schema.__name__}",
                severity=Severity.ERROR,
            )
        except ValidationError as e:
            return ValidationEntry(
                constraint_name=f"schema_{schema.__name__}",
                passed=False,
                message=f"Schema validation failed: {str(e)}",
                severity=Severity.ERROR,
                input_excerpt=str(data)[:200],
            )

    def _run_constraint(
        self, data: dict[str, Any], constraint: Constraint
    ) -> ValidationEntry:
        """Run a single constraint check.

        Args:
            data: Data to validate
            constraint: Constraint to check

        Returns:
            ValidationEntry with result
        """
        check_fn = getattr(BuiltInValidators, f"check_{constraint.check_fn}", None)

        if check_fn is None:
            return ValidationEntry(
                constraint_name=constraint.name,
                passed=False,
                message=f"Unknown check function: {constraint.check_fn}",
                severity=constraint.severity,
            )

        try:
            passed, message = check_fn(data, **constraint.params)
            return ValidationEntry(
                constraint_name=constraint.name,
                passed=passed,
                message=message,
                severity=constraint.severity,
                input_excerpt=str(data)[:200] if not passed else None,
            )
        except Exception as e:
            return ValidationEntry(
                constraint_name=constraint.name,
                passed=False,
                message=f"Check failed with error: {str(e)}",
                severity=constraint.severity,
                input_excerpt=str(data)[:200],
            )

    @staticmethod
    def _compute_hash(data: Any) -> str:
        """Compute SHA256 hash of data.

        Args:
            data: Data to hash

        Returns:
            Hex string of hash
        """
        serialized = json.dumps(data, sort_keys=True, default=str)
        return hashlib.sha256(serialized.encode()).hexdigest()


class BuiltInValidators:
    """Collection of common validators.

    Provides factory methods for creating common constraints and
    static check methods for validation execution.
    """

    @staticmethod
    def length_check(min_len: int = 0, max_len: int = 10000) -> Constraint:
        """Create constraint to validate string length.

        Args:
            min_len: Minimum allowed length
            max_len: Maximum allowed length

        Returns:
            Constraint configured for length checking
        """
        return Constraint(
            name="length_check",
            description=f"String length must be between {min_len} and {max_len}",
            check_fn="length",
            params={"min_len": min_len, "max_len": max_len},
            severity=Severity.ERROR,
        )

    @staticmethod
    def check_length(
        data: dict[str, Any], min_len: int = 0, max_len: int = 10000, field: str = "output"
    ) -> tuple[bool, str]:
        """Check string length is within bounds.

        Args:
            data: Data containing field to check
            min_len: Minimum allowed length
            max_len: Maximum allowed length
            field: Field name to check

        Returns:
            Tuple of (passed, message)
        """
        value = data.get(field, "")
        if not isinstance(value, str):
            value = str(value)

        length = len(value)
        if length < min_len:
            return False, f"Length {length} is below minimum {min_len}"
        if length > max_len:
            return False, f"Length {length} exceeds maximum {max_len}"
        return True, f"Length {length} is within bounds [{min_len}, {max_len}]"

    @staticmethod
    def regex_match(pattern: str) -> Constraint:
        """Create constraint to validate regex pattern match.

        Args:
            pattern: Regex pattern to match

        Returns:
            Constraint configured for regex matching
        """
        return Constraint(
            name="regex_match",
            description=f"Value must match pattern: {pattern}",
            check_fn="regex",
            params={"pattern": pattern},
            severity=Severity.ERROR,
        )

    @staticmethod
    def check_regex(
        data: dict[str, Any], pattern: str, field: str = "output"
    ) -> tuple[bool, str]:
        """Check value matches regex pattern.

        Args:
            data: Data containing field to check
            pattern: Regex pattern
            field: Field name to check

        Returns:
            Tuple of (passed, message)
        """
        value = str(data.get(field, ""))
        if re.search(pattern, value):
            return True, f"Value matches pattern '{pattern}'"
        return False, f"Value does not match pattern '{pattern}'"

    @staticmethod
    def no_pii() -> Constraint:
        """Create constraint to check for PII.

        Returns:
            Constraint configured for PII detection
        """
        return Constraint(
            name="no_pii",
            description="Output must not contain PII (SSN, credit card, etc.)",
            check_fn="pii",
            params={},
            severity=Severity.ERROR,
        )

    @staticmethod
    def check_pii(data: dict[str, Any], field: str = "output") -> tuple[bool, str]:
        """Check for presence of PII patterns.

        Args:
            data: Data containing field to check
            field: Field name to check

        Returns:
            Tuple of (passed, message)
        """
        value = str(data.get(field, ""))

        # SSN pattern: XXX-XX-XXXX
        ssn_pattern = r"\b\d{3}-\d{2}-\d{4}\b"
        if re.search(ssn_pattern, value):
            return False, "Potential SSN detected"

        # Credit card pattern: 16 digits with optional separators
        cc_pattern = r"\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b"
        if re.search(cc_pattern, value):
            return False, "Potential credit card number detected"

        # Email pattern
        email_pattern = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"
        if re.search(email_pattern, value):
            return False, "Email address detected"

        # Phone pattern
        phone_pattern = r"\b\+?1?[-.\s]?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b"
        if re.search(phone_pattern, value):
            return False, "Potential phone number detected"

        return True, "No PII patterns detected"

    @staticmethod
    def confidence_range(min_conf: float = 0.0, max_conf: float = 1.0) -> Constraint:
        """Create constraint to validate confidence score range.

        Args:
            min_conf: Minimum confidence value
            max_conf: Maximum confidence value

        Returns:
            Constraint configured for confidence checking
        """
        return Constraint(
            name="confidence_range",
            description=f"Confidence must be between {min_conf} and {max_conf}",
            check_fn="confidence",
            params={"min_conf": min_conf, "max_conf": max_conf},
            severity=Severity.ERROR,
        )

    @staticmethod
    def check_confidence(
        data: dict[str, Any], min_conf: float = 0.0, max_conf: float = 1.0, field: str = "confidence"
    ) -> tuple[bool, str]:
        """Check confidence score is within range.

        Args:
            data: Data containing confidence field
            min_conf: Minimum confidence
            max_conf: Maximum confidence
            field: Field name containing confidence

        Returns:
            Tuple of (passed, message)
        """
        value = data.get(field)
        if value is None:
            return False, f"Missing {field} field"

        try:
            conf = float(value)
        except (TypeError, ValueError):
            return False, f"Cannot convert {field} to float"

        if conf < min_conf:
            return False, f"Confidence {conf} is below minimum {min_conf}"
        if conf > max_conf:
            return False, f"Confidence {conf} exceeds maximum {max_conf}"
        return True, f"Confidence {conf} is within range [{min_conf}, {max_conf}]"

    @staticmethod
    def required_fields(fields: list[str]) -> Constraint:
        """Create constraint to check required fields exist.

        Args:
            fields: List of required field names

        Returns:
            Constraint configured for field checking
        """
        return Constraint(
            name="required_fields",
            description=f"Required fields: {', '.join(fields)}",
            check_fn="required",
            params={"fields": fields},
            severity=Severity.ERROR,
        )

    @staticmethod
    def check_required(
        data: dict[str, Any], fields: list[str]
    ) -> tuple[bool, str]:
        """Check all required fields are present.

        Args:
            data: Data to check
            fields: Required field names

        Returns:
            Tuple of (passed, message)
        """
        missing = [f for f in fields if f not in data]
        if missing:
            return False, f"Missing required fields: {', '.join(missing)}"
        return True, "All required fields present"

    @staticmethod
    def json_parseable() -> Constraint:
        """Create constraint to check value is valid JSON.

        Returns:
            Constraint configured for JSON checking
        """
        return Constraint(
            name="json_parseable",
            description="Output must be valid JSON",
            check_fn="json",
            params={},
            severity=Severity.ERROR,
        )

    @staticmethod
    def check_json(data: dict[str, Any], field: str = "output") -> tuple[bool, str]:
        """Check value is valid JSON.

        Args:
            data: Data containing field to check
            field: Field name to check

        Returns:
            Tuple of (passed, message)
        """
        value = data.get(field, "")
        if not isinstance(value, str):
            return True, "Value is already parsed (not a string)"

        try:
            json.loads(value)
            return True, "Valid JSON"
        except json.JSONDecodeError as e:
            return False, f"Invalid JSON: {str(e)}"

    @staticmethod
    def value_in_list(allowed_values: list[Any], field: str = "output") -> Constraint:
        """Create constraint to check value is in allowed list.

        Args:
            allowed_values: List of allowed values
            field: Field to check

        Returns:
            Constraint configured for value checking
        """
        return Constraint(
            name="value_in_list",
            description=f"Value must be one of: {allowed_values}",
            check_fn="in_list",
            params={"allowed_values": allowed_values, "field": field},
            severity=Severity.ERROR,
        )

    @staticmethod
    def check_in_list(
        data: dict[str, Any], allowed_values: list[Any], field: str = "output"
    ) -> tuple[bool, str]:
        """Check value is in allowed list.

        Args:
            data: Data containing field to check
            allowed_values: Allowed values
            field: Field name to check

        Returns:
            Tuple of (passed, message)
        """
        value = data.get(field)
        if value in allowed_values:
            return True, f"Value '{value}' is in allowed list"
        return False, f"Value '{value}' is not in allowed list: {allowed_values}"

    @staticmethod
    def always_pass(message: str = "Logging constraint") -> Constraint:
        """Create constraint that always passes (for logging/audit purposes).

        Useful for constraints that should log but never block execution,
        such as audit logging requirements in data_access policies.

        Args:
            message: Message to include in validation result

        Returns:
            Constraint configured to always pass
        """
        return Constraint(
            name="always_pass",
            description=message,
            check_fn="always_pass",
            params={"message": message},
            severity=Severity.INFO,
            on_fail=FailAction.LOG,
        )

    @staticmethod
    def check_always_pass(
        data: dict[str, Any], message: str = "Logging constraint"
    ) -> tuple[bool, str]:
        """Check that always passes (for logging purposes).

        Args:
            data: Data (ignored)
            message: Message to return

        Returns:
            Tuple of (True, message)
        """
        return True, message

