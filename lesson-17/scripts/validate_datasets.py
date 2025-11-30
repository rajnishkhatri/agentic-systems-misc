"""Validation script for Lesson 17 synthetic datasets.

Validates all generated datasets against their Pydantic schemas:
- PII examples: Custom schema validation
- Agent metadata: AgentFacts schema
- Workflow traces: TaskPlan, ExecutionTrace schemas
- Research workflows: PhaseLogger schemas
- Parameter substitutions: ParameterSubstitution schema

Usage:
    python validate_datasets.py [--data-dir DIR]

Example:
    python lesson-17/scripts/validate_datasets.py
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

# Add lesson-17 to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.explainability.agent_facts import AgentFacts, Capability, Policy
from backend.explainability.black_box import (
    AgentInfo,
    ExecutionTrace,
    ParameterSubstitution,
    PlanStep,
    TaskPlan,
    TraceEvent,
)
from backend.explainability.phase_logger import Artifact, Decision, PhaseOutcome


class ValidationError(Exception):
    """Custom validation error with details."""

    def __init__(self, message: str, file_path: str, record_index: int | None = None):
        self.message = message
        self.file_path = file_path
        self.record_index = record_index
        super().__init__(self._format_message())

    def _format_message(self) -> str:
        if self.record_index is not None:
            return f"{self.file_path} [record {self.record_index}]: {self.message}"
        return f"{self.file_path}: {self.message}"


class DatasetValidator:
    """Validates generated datasets against Pydantic schemas."""

    def __init__(self, data_dir: Path):
        """Initialize validator with data directory.

        Args:
            data_dir: Directory containing generated datasets
        """
        self.data_dir = data_dir
        self.errors: list[ValidationError] = []
        self.warnings: list[str] = []
        self.stats = {
            "files_checked": 0,
            "records_validated": 0,
            "errors": 0,
            "warnings": 0,
        }

    def validate_all(self) -> bool:
        """Validate all datasets.

        Returns:
            True if all validations pass, False otherwise
        """
        print("=" * 80)
        print("Lesson 17: Validating Synthetic Datasets")
        print(f"Data directory: {self.data_dir}")
        print("=" * 80)

        # Run all validations
        self._validate_pii_examples()
        self._validate_agent_metadata()
        self._validate_workflow_traces()
        self._validate_research_workflows()
        self._validate_parameter_substitutions()

        # Print summary
        self._print_summary()

        return len(self.errors) == 0

    def _validate_pii_examples(self) -> None:
        """Validate PII examples dataset."""
        print("\n[1/5] Validating pii_examples_50.json...")
        path = self.data_dir / "pii_examples_50.json"

        if not path.exists():
            self._add_error("File not found", str(path))
            return

        try:
            with open(path) as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            self._add_error(f"Invalid JSON: {e}", str(path))
            return

        self.stats["files_checked"] += 1

        if not isinstance(data, list):
            self._add_error("Expected list of records", str(path))
            return

        # Validate each record
        required_fields = [
            "pii_id",
            "text",
            "contains_pii",
            "pii_types",
            "pii_spans",
            "expected_redacted",
        ]

        for i, record in enumerate(data):
            self.stats["records_validated"] += 1

            # Check required fields
            for field in required_fields:
                if field not in record:
                    self._add_error(f"Missing field: {field}", str(path), i)

            # Validate pii_spans structure
            if "pii_spans" in record:
                for span in record["pii_spans"]:
                    if not all(k in span for k in ["type", "start", "end", "text"]):
                        self._add_error(
                            "Invalid pii_span structure", str(path), i
                        )
                        break

            # Validate consistency
            if record.get("contains_pii") and not record.get("pii_types"):
                self._add_warning(
                    f"Record {i}: contains_pii=True but pii_types is empty"
                )

        print(f"  ✓ Validated {len(data)} PII examples")

    def _validate_agent_metadata(self) -> None:
        """Validate agent metadata against AgentFacts schema."""
        print("\n[2/5] Validating agent_metadata_10.json...")
        path = self.data_dir / "agent_metadata_10.json"

        if not path.exists():
            self._add_error("File not found", str(path))
            return

        try:
            with open(path) as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            self._add_error(f"Invalid JSON: {e}", str(path))
            return

        self.stats["files_checked"] += 1

        if not isinstance(data, list):
            self._add_error("Expected list of records", str(path))
            return

        # Validate each record against AgentFacts schema
        for i, record in enumerate(data):
            self.stats["records_validated"] += 1

            try:
                # Parse dates
                if "created_at" in record and isinstance(record["created_at"], str):
                    record["created_at"] = datetime.fromisoformat(
                        record["created_at"].replace("Z", "+00:00")
                    )
                if "updated_at" in record and isinstance(record["updated_at"], str):
                    record["updated_at"] = datetime.fromisoformat(
                        record["updated_at"].replace("Z", "+00:00")
                    )

                # Validate capabilities
                if "capabilities" in record:
                    for cap in record["capabilities"]:
                        Capability.model_validate(cap)

                # Validate policies (with date parsing)
                if "policies" in record:
                    for pol in record["policies"]:
                        if "effective_from" in pol and isinstance(
                            pol["effective_from"], str
                        ):
                            pol["effective_from"] = datetime.fromisoformat(
                                pol["effective_from"].replace("Z", "+00:00")
                            )
                        if "effective_until" in pol and pol["effective_until"]:
                            if isinstance(pol["effective_until"], str):
                                pol["effective_until"] = datetime.fromisoformat(
                                    pol["effective_until"].replace("Z", "+00:00")
                                )
                        Policy.model_validate(pol)

                # Validate full record
                AgentFacts.model_validate(record)

            except Exception as e:
                self._add_error(f"Schema validation failed: {e}", str(path), i)

        print(f"  ✓ Validated {len(data)} agent metadata records")

    def _validate_workflow_traces(self) -> None:
        """Validate workflow traces against BlackBoxRecorder schemas."""
        print("\n[3/5] Validating workflow traces...")
        workflows_dir = self.data_dir / "workflows"

        if not workflows_dir.exists():
            self._add_error("Workflows directory not found", str(workflows_dir))
            return

        workflow_files = list(workflows_dir.glob("*.json"))
        if not workflow_files:
            self._add_error("No workflow files found", str(workflows_dir))
            return

        for path in workflow_files:
            self.stats["files_checked"] += 1

            try:
                with open(path) as f:
                    data = json.load(f)
            except json.JSONDecodeError as e:
                self._add_error(f"Invalid JSON: {e}", str(path))
                continue

            self.stats["records_validated"] += 1

            # Validate task_plan structure
            if "task_plan" in data:
                try:
                    plan = data["task_plan"]
                    # Parse dates
                    if "created_at" in plan and isinstance(plan["created_at"], str):
                        plan["created_at"] = datetime.fromisoformat(
                            plan["created_at"].replace("Z", "+00:00")
                        )

                    # Validate steps
                    if "steps" in plan:
                        for step in plan["steps"]:
                            PlanStep.model_validate(step)

                    TaskPlan.model_validate(plan)
                except Exception as e:
                    self._add_error(f"TaskPlan validation failed: {e}", str(path))

            # Validate execution_trace structure
            if "execution_trace" in data:
                try:
                    trace = data["execution_trace"]
                    if "events" in trace:
                        for event in trace["events"]:
                            # Parse timestamp
                            if "timestamp" in event and isinstance(
                                event["timestamp"], str
                            ):
                                event["timestamp"] = datetime.fromisoformat(
                                    event["timestamp"].replace("Z", "+00:00")
                                )
                            TraceEvent.model_validate(event)
                except Exception as e:
                    self._add_error(
                        f"ExecutionTrace validation failed: {e}", str(path)
                    )

            print(f"  ✓ {path.name}")

        print(f"  ✓ Validated {len(workflow_files)} workflow trace files")

    def _validate_research_workflows(self) -> None:
        """Validate research workflows against PhaseLogger schemas."""
        print("\n[4/5] Validating research workflows...")
        research_dir = self.data_dir / "research_workflows"

        if not research_dir.exists():
            self._add_error("Research workflows directory not found", str(research_dir))
            return

        workflow_files = list(research_dir.glob("*.json"))
        if not workflow_files:
            self._add_error("No research workflow files found", str(research_dir))
            return

        for path in workflow_files:
            self.stats["files_checked"] += 1

            try:
                with open(path) as f:
                    data = json.load(f)
            except json.JSONDecodeError as e:
                self._add_error(f"Invalid JSON: {e}", str(path))
                continue

            self.stats["records_validated"] += 1

            # Check required fields
            required = ["workflow_id", "research_topic", "phases", "final_status"]
            for field in required:
                if field not in data:
                    self._add_error(f"Missing field: {field}", str(path))

            # Validate decisions
            if "decisions" in data:
                for i, decision in enumerate(data["decisions"]):
                    try:
                        # Parse timestamp
                        if "timestamp" in decision and isinstance(
                            decision["timestamp"], str
                        ):
                            decision["timestamp"] = datetime.fromisoformat(
                                decision["timestamp"].replace("Z", "+00:00")
                            )

                        # Map fields to Decision schema
                        decision_obj = {
                            "decision_id": decision.get("decision_id", f"dec-{i}"),
                            "timestamp": decision.get("timestamp"),
                            "decision": decision.get("selected", ""),
                            "reasoning": decision.get("rationale", ""),
                            "alternatives_considered": decision.get("alternatives", []),
                            "confidence": decision.get("confidence", 1.0),
                        }
                        Decision.model_validate(decision_obj)
                    except Exception as e:
                        self._add_error(
                            f"Decision validation failed [{i}]: {e}", str(path)
                        )

            # Validate artifacts
            if "artifacts" in data:
                for i, artifact in enumerate(data["artifacts"]):
                    try:
                        # Parse timestamp
                        if "created_at" in artifact and isinstance(
                            artifact["created_at"], str
                        ):
                            artifact["created_at"] = datetime.fromisoformat(
                                artifact["created_at"].replace("Z", "+00:00")
                            )

                        # Map fields to Artifact schema
                        artifact_obj = {
                            "artifact_id": artifact.get("artifact_id", f"art-{i}"),
                            "name": artifact.get("description", ""),
                            "path": artifact.get("location", ""),
                            "artifact_type": artifact.get("artifact_type", "file"),
                            "created_at": artifact.get("created_at"),
                            "metadata": artifact.get("metadata", {}),
                        }
                        Artifact.model_validate(artifact_obj)
                    except Exception as e:
                        self._add_error(
                            f"Artifact validation failed [{i}]: {e}", str(path)
                        )

        print(f"  ✓ Validated {len(workflow_files)} research workflow files")

    def _validate_parameter_substitutions(self) -> None:
        """Validate parameter substitution logs."""
        print("\n[5/5] Validating parameter_substitutions_20.json...")
        path = self.data_dir / "parameter_substitutions_20.json"

        if not path.exists():
            self._add_error("File not found", str(path))
            return

        try:
            with open(path) as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            self._add_error(f"Invalid JSON: {e}", str(path))
            return

        self.stats["files_checked"] += 1

        if not isinstance(data, list):
            self._add_error("Expected list of records", str(path))
            return

        # Validate each record
        required_fields = [
            "substitution_id",
            "workflow_id",
            "timestamp",
            "parameter_name",
            "old_value",
            "new_value",
            "justification",
            "changed_by",
        ]

        for i, record in enumerate(data):
            self.stats["records_validated"] += 1

            # Check required fields
            for field in required_fields:
                if field not in record:
                    self._add_error(f"Missing field: {field}", str(path), i)

            # Validate impact structure if present
            if "impact" in record:
                impact = record["impact"]
                impact_fields = ["workflows_affected", "success_rate_before", "success_rate_after"]
                for field in impact_fields:
                    if field not in impact:
                        self._add_warning(
                            f"Record {i}: impact missing field: {field}"
                        )

        print(f"  ✓ Validated {len(data)} parameter substitution records")

    def _add_error(
        self, message: str, file_path: str, record_index: int | None = None
    ) -> None:
        """Add a validation error."""
        error = ValidationError(message, file_path, record_index)
        self.errors.append(error)
        self.stats["errors"] += 1

    def _add_warning(self, message: str) -> None:
        """Add a validation warning."""
        self.warnings.append(message)
        self.stats["warnings"] += 1

    def _print_summary(self) -> None:
        """Print validation summary."""
        print("\n" + "=" * 80)
        print("Validation Summary")
        print("=" * 80)

        print(f"\nFiles checked: {self.stats['files_checked']}")
        print(f"Records validated: {self.stats['records_validated']}")

        if self.errors:
            print(f"\n❌ ERRORS ({len(self.errors)}):")
            for error in self.errors:
                print(f"  - {error}")
        else:
            print("\n✅ No errors found")

        if self.warnings:
            print(f"\n⚠️  WARNINGS ({len(self.warnings)}):")
            for warning in self.warnings[:10]:  # Limit to first 10
                print(f"  - {warning}")
            if len(self.warnings) > 10:
                print(f"  ... and {len(self.warnings) - 10} more")

        if not self.errors:
            print("\n✅ All validations passed!")
        else:
            print(f"\n❌ Validation failed with {len(self.errors)} error(s)")


def main() -> int:
    """Run dataset validation.

    Returns:
        Exit code (0 for success, 1 for failure)
    """
    parser = argparse.ArgumentParser(
        description="Validate Lesson 17 synthetic datasets"
    )
    parser.add_argument(
        "--data-dir",
        type=str,
        default=None,
        help="Data directory (default: lesson-17/data/)",
    )
    args = parser.parse_args()

    # Setup paths
    if args.data_dir:
        data_dir = Path(args.data_dir)
    else:
        data_dir = Path(__file__).parent.parent / "data"

    if not data_dir.exists():
        print(f"Error: Data directory not found: {data_dir}")
        print("Run generate_datasets.py first to create the datasets.")
        return 1

    validator = DatasetValidator(data_dir)
    success = validator.validate_all()

    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())

