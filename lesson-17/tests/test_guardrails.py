"""Tests for GuardRails - Declarative validators with trace generation.

Tests the GuardRails implementation including:
- Constraint creation and validation
- GuardRail and PromptGuardRail models
- GuardRailValidator execution
- Built-in validators
- Validation trace generation
"""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

import pytest
from pydantic import BaseModel

import sys
from pathlib import Path

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.explainability.guardrails import (
    BuiltInValidators,
    Constraint,
    FailAction,
    GuardRail,
    GuardRailValidator,
    PromptGuardRail,
    Severity,
    ValidationEntry,
    ValidationResult,
)


class TestConstraintModel:
    """Tests for Constraint Pydantic model."""

    def test_create_constraint(self) -> None:
        """Test creating a valid constraint."""
        constraint = Constraint(
            name="length_check",
            description="Check string length",
            check_fn="length",
            params={"min_len": 1, "max_len": 100},
            severity=Severity.ERROR,
            on_fail=FailAction.REJECT,
        )
        assert constraint.name == "length_check"
        assert constraint.severity == Severity.ERROR

    def test_constraint_defaults(self) -> None:
        """Test constraint default values."""
        constraint = Constraint(
            name="test",
            description="Test",
            check_fn="test",
        )
        assert constraint.severity == Severity.ERROR
        assert constraint.on_fail == FailAction.REJECT
        assert constraint.params == {}


class TestValidationEntryModel:
    """Tests for ValidationEntry model."""

    def test_create_validation_entry(self) -> None:
        """Test creating a validation entry."""
        entry = ValidationEntry(
            constraint_name="test",
            passed=True,
            message="Validation passed",
            severity=Severity.ERROR,
        )
        assert entry.passed is True
        assert entry.fix_applied is None


class TestValidationResultModel:
    """Tests for ValidationResult model."""

    def test_create_validation_result(self) -> None:
        """Test creating a validation result."""
        result = ValidationResult(
            guardrail_name="test_guardrail",
            input_hash="abc123",
            is_valid=True,
            entries=[],
            total_errors=0,
            total_warnings=0,
            validation_time_ms=10,
        )
        assert result.is_valid is True
        assert result.action_taken is None


class TestGuardRailModel:
    """Tests for GuardRail Pydantic model."""

    def test_create_guardrail(self) -> None:
        """Test creating a valid guardrail."""
        guardrail = GuardRail(
            name="invoice_validator",
            description="Validates invoice extraction output",
            version="1.0.0",
            constraints=[
                Constraint(
                    name="required_fields",
                    description="Check required fields",
                    check_fn="required",
                    params={"fields": ["vendor", "amount"]},
                )
            ],
        )
        assert guardrail.name == "invoice_validator"
        assert len(guardrail.constraints) == 1

    def test_guardrail_document(self) -> None:
        """Test generating guardrail documentation."""
        guardrail = GuardRail(
            name="test_guardrail",
            description="A test guardrail",
            constraints=[
                Constraint(
                    name="length",
                    description="Check length",
                    check_fn="length",
                    params={"min_len": 1},
                )
            ],
        )
        doc = guardrail.document()

        assert "# test_guardrail" in doc
        assert "A test guardrail" in doc
        assert "## Constraints" in doc
        assert "### length" in doc


class TestPromptGuardRailModel:
    """Tests for PromptGuardRail model."""

    def test_create_prompt_guardrail(self) -> None:
        """Test creating a prompt guardrail."""
        guardrail = PromptGuardRail(
            name="extraction_prompt",
            description="Validates extraction prompt output",
            prompt_template="Extract the following from the invoice: {fields}",
            required_fields=["vendor", "amount"],
            optional_fields=["date"],
            example_valid_output='{"vendor": "Acme", "amount": 100}',
            example_invalid_output='{"vendor": ""}',
        )
        assert guardrail.prompt_template != ""
        assert len(guardrail.required_fields) == 2

    def test_prompt_guardrail_document(self) -> None:
        """Test generating prompt guardrail documentation."""
        guardrail = PromptGuardRail(
            name="test",
            description="Test",
            prompt_template="Test template",
            required_fields=["field1"],
            example_valid_output='{"field1": "value"}',
        )
        doc = guardrail.document()

        assert "## Prompt Template" in doc
        assert "## Required Fields" in doc
        assert "## Example Valid Output" in doc


class TestGuardRailValidator:
    """Tests for GuardRailValidator class."""

    @pytest.fixture
    def validator(self) -> GuardRailValidator:
        """Create a GuardRailValidator instance."""
        return GuardRailValidator()

    def test_validate_with_constraints(self, validator: GuardRailValidator) -> None:
        """Test validation with constraints."""
        guardrail = GuardRail(
            name="test",
            description="Test guardrail",
            constraints=[
                BuiltInValidators.length_check(min_len=1, max_len=100),
            ],
        )

        result = validator.validate({"output": "Hello World"}, guardrail)
        assert result.is_valid is True
        assert result.total_errors == 0

    def test_validate_failing_constraint(self, validator: GuardRailValidator) -> None:
        """Test validation with failing constraint."""
        guardrail = GuardRail(
            name="test",
            description="Test guardrail",
            constraints=[
                BuiltInValidators.length_check(min_len=100, max_len=200),
            ],
        )

        result = validator.validate({"output": "Short"}, guardrail)
        assert result.is_valid is False
        assert result.total_errors == 1
        assert result.action_taken == FailAction.REJECT

    def test_validate_with_schema(self, validator: GuardRailValidator) -> None:
        """Test validation with Pydantic schema."""

        class TestSchema(BaseModel):
            vendor: str
            amount: float

        validator.register_schema("TestSchema", TestSchema)

        guardrail = GuardRail(
            name="test",
            description="Test",
            schema_name="TestSchema",
        )

        # Valid data
        result = validator.validate({"vendor": "Acme", "amount": 100.0}, guardrail)
        assert result.is_valid is True

        # Invalid data
        result = validator.validate({"vendor": "Acme"}, guardrail)
        assert result.is_valid is False

    def test_validate_prompt_output(self, validator: GuardRailValidator) -> None:
        """Test validating LLM prompt output."""
        guardrail = PromptGuardRail(
            name="extraction",
            description="Test extraction",
            required_fields=["vendor", "amount"],
        )

        # Valid JSON with required fields
        result = validator.validate_prompt_output(
            '{"vendor": "Acme", "amount": 100}',
            guardrail,
        )
        assert result.is_valid is True

        # Missing required field
        result = validator.validate_prompt_output(
            '{"vendor": "Acme"}',
            guardrail,
        )
        assert result.is_valid is False

    def test_validation_trace(self, validator: GuardRailValidator) -> None:
        """Test validation trace is recorded."""
        guardrail = GuardRail(
            name="test",
            description="Test",
            constraints=[
                BuiltInValidators.length_check(min_len=1),
                BuiltInValidators.no_pii(),
            ],
        )

        validator.validate({"output": "Hello"}, guardrail)
        trace = validator.get_validation_trace()

        assert len(trace) == 2

    def test_clear_trace(self, validator: GuardRailValidator) -> None:
        """Test clearing validation trace."""
        guardrail = GuardRail(
            name="test",
            description="Test",
            constraints=[BuiltInValidators.length_check()],
        )

        validator.validate({"output": "test"}, guardrail)
        assert len(validator.get_validation_trace()) > 0

        validator.clear_trace()
        assert len(validator.get_validation_trace()) == 0

    def test_export_trace(self, validator: GuardRailValidator) -> None:
        """Test exporting validation trace."""
        guardrail = GuardRail(
            name="test",
            description="Test",
            constraints=[BuiltInValidators.length_check()],
        )

        validator.validate({"output": "test"}, guardrail)

        with tempfile.TemporaryDirectory() as tmpdir:
            export_path = Path(tmpdir) / "trace.json"
            validator.export_trace(export_path)

            assert export_path.exists()

            with open(export_path) as f:
                data = json.load(f)

            assert "entries" in data
            assert data["entry_count"] > 0


class TestBuiltInValidators:
    """Tests for BuiltInValidators collection."""

    def test_length_check(self) -> None:
        """Test length check validator."""
        constraint = BuiltInValidators.length_check(min_len=5, max_len=10)
        assert constraint.name == "length_check"
        assert constraint.params["min_len"] == 5

        # Test check function
        passed, msg = BuiltInValidators.check_length(
            {"output": "Hello"}, min_len=1, max_len=10
        )
        assert passed is True

        passed, msg = BuiltInValidators.check_length(
            {"output": "Hi"}, min_len=5, max_len=10
        )
        assert passed is False

    def test_regex_match(self) -> None:
        """Test regex match validator."""
        constraint = BuiltInValidators.regex_match(r"\d{3}-\d{4}")
        assert constraint.name == "regex_match"

        # Test check function
        passed, msg = BuiltInValidators.check_regex(
            {"output": "123-4567"}, pattern=r"\d{3}-\d{4}"
        )
        assert passed is True

        passed, msg = BuiltInValidators.check_regex(
            {"output": "invalid"}, pattern=r"\d{3}-\d{4}"
        )
        assert passed is False

    def test_no_pii(self) -> None:
        """Test PII detection validator."""
        constraint = BuiltInValidators.no_pii()
        assert constraint.name == "no_pii"

        # No PII
        passed, msg = BuiltInValidators.check_pii({"output": "Hello World"})
        assert passed is True

        # SSN detected
        passed, msg = BuiltInValidators.check_pii({"output": "SSN: 123-45-6789"})
        assert passed is False
        assert "SSN" in msg

        # Credit card detected
        passed, msg = BuiltInValidators.check_pii(
            {"output": "Card: 4111-1111-1111-1111"}
        )
        assert passed is False
        assert "credit card" in msg

        # Email detected
        passed, msg = BuiltInValidators.check_pii({"output": "Email: test@example.com"})
        assert passed is False
        assert "Email" in msg

    def test_confidence_range(self) -> None:
        """Test confidence range validator."""
        constraint = BuiltInValidators.confidence_range(0.0, 1.0)
        assert constraint.name == "confidence_range"

        # Valid confidence
        passed, msg = BuiltInValidators.check_confidence(
            {"confidence": 0.85}, min_conf=0.0, max_conf=1.0
        )
        assert passed is True

        # Below minimum
        passed, msg = BuiltInValidators.check_confidence(
            {"confidence": -0.1}, min_conf=0.0, max_conf=1.0
        )
        assert passed is False

        # Above maximum
        passed, msg = BuiltInValidators.check_confidence(
            {"confidence": 1.5}, min_conf=0.0, max_conf=1.0
        )
        assert passed is False

        # Missing field
        passed, msg = BuiltInValidators.check_confidence({}, min_conf=0.0, max_conf=1.0)
        assert passed is False

    def test_required_fields(self) -> None:
        """Test required fields validator."""
        constraint = BuiltInValidators.required_fields(["vendor", "amount"])
        assert constraint.name == "required_fields"

        # All fields present
        passed, msg = BuiltInValidators.check_required(
            {"vendor": "Acme", "amount": 100}, fields=["vendor", "amount"]
        )
        assert passed is True

        # Missing field
        passed, msg = BuiltInValidators.check_required(
            {"vendor": "Acme"}, fields=["vendor", "amount"]
        )
        assert passed is False
        assert "amount" in msg

    def test_json_parseable(self) -> None:
        """Test JSON parseable validator."""
        constraint = BuiltInValidators.json_parseable()
        assert constraint.name == "json_parseable"

        # Valid JSON
        passed, msg = BuiltInValidators.check_json({"output": '{"key": "value"}'})
        assert passed is True

        # Invalid JSON
        passed, msg = BuiltInValidators.check_json({"output": "not json"})
        assert passed is False

        # Already parsed (not a string)
        passed, msg = BuiltInValidators.check_json({"output": {"key": "value"}})
        assert passed is True

    def test_value_in_list(self) -> None:
        """Test value in list validator."""
        constraint = BuiltInValidators.value_in_list(["A", "B", "C"])
        assert constraint.name == "value_in_list"

        # Value in list
        passed, msg = BuiltInValidators.check_in_list(
            {"output": "A"}, allowed_values=["A", "B", "C"]
        )
        assert passed is True

        # Value not in list
        passed, msg = BuiltInValidators.check_in_list(
            {"output": "D"}, allowed_values=["A", "B", "C"]
        )
        assert passed is False


class TestFailActions:
    """Tests for FailAction enum."""

    def test_all_fail_actions(self) -> None:
        """Test all fail action values exist."""
        assert FailAction.REJECT.value == "reject"
        assert FailAction.FIX.value == "fix"
        assert FailAction.ESCALATE.value == "escalate"
        assert FailAction.LOG.value == "log"
        assert FailAction.RETRY.value == "retry"


class TestSeverityLevels:
    """Tests for Severity enum."""

    def test_all_severity_levels(self) -> None:
        """Test all severity level values exist."""
        assert Severity.ERROR.value == "error"
        assert Severity.WARNING.value == "warning"
        assert Severity.INFO.value == "info"

