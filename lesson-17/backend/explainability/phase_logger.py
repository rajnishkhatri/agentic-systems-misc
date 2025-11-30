"""Phase-Based Workflow Logger - Multi-phase workflow logging.

This module provides AgentRxiv-style logging for multi-phase workflows,
tracking decisions and outcomes through each phase.

Inspired by:
- AgentRxiv (agentrxiv.github.io) - Phase-based research logging
- lesson-16/backend/reliability/audit_log.py - Structured logging
- lesson-16/backend/orchestrators/base.py - Orchestration integration

Key Features:
- Phase-based workflow tracking
- Decision logging with reasoning and alternatives
- Artifact tracking
- Mermaid diagram generation

Example:
    >>> logger = PhaseLogger(workflow_id="research-001", storage_path=Path("cache/"))
    >>> logger.start_phase(WorkflowPhase.PLANNING)
    >>> logger.log_decision("Use GPT-4", "Higher accuracy needed", ["GPT-3.5", "Claude"])
    >>> logger.end_phase("success")
"""

from __future__ import annotations

import json
from datetime import UTC, datetime
from enum import Enum
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field


class WorkflowPhase(str, Enum):
    """Standard workflow phases (AgentRxiv-inspired)."""

    PLANNING = "planning"
    LITERATURE_REVIEW = "literature_review"
    DATA_COLLECTION = "data_collection"
    EXECUTION = "execution"
    EXPERIMENT = "experiment"
    VALIDATION = "validation"
    REPORTING = "reporting"
    COMPLETED = "completed"
    FAILED = "failed"


class Decision(BaseModel):
    """Logged decision with reasoning and alternatives.

    Attributes:
        decision_id: Unique identifier
        timestamp: When decision was made
        decision: The decision that was made
        reasoning: Why this decision was made
        alternatives_considered: Other options considered
        selected_because: Why this option was selected over alternatives
        confidence: Confidence in the decision (0-1)
        agent_id: Agent that made the decision (if applicable)
        reversible: Whether this decision can be undone
        phase: Phase when decision was made
    """

    decision_id: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))
    decision: str
    reasoning: str
    alternatives_considered: list[str] = Field(default_factory=list)
    selected_because: str = ""
    confidence: float = 1.0
    agent_id: str | None = None
    reversible: bool = True
    phase: WorkflowPhase | None = None

    class Config:
        extra = "forbid"


class Artifact(BaseModel):
    """Record of an artifact produced during workflow.

    Attributes:
        artifact_id: Unique identifier
        name: Human-readable name
        path: File path where artifact is stored
        artifact_type: Type (file, data, model, etc.)
        created_at: When artifact was created
        phase: Phase when artifact was produced
        metadata: Additional artifact metadata
    """

    artifact_id: str
    name: str
    path: str
    artifact_type: str = "file"
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    phase: WorkflowPhase | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)

    class Config:
        extra = "forbid"


class PhaseOutcome(BaseModel):
    """Outcome of a workflow phase.

    Attributes:
        phase: The phase that completed
        status: Outcome status (success, failure, partial, skipped)
        start_time: When phase started
        end_time: When phase ended
        duration_ms: Duration in milliseconds
        decisions_made: Number of decisions during this phase
        artifacts_produced: List of artifact names produced
        errors: List of errors encountered
        next_phase: Suggested next phase (if any)
        metadata: Additional outcome metadata
    """

    phase: WorkflowPhase
    status: str
    start_time: datetime
    end_time: datetime
    duration_ms: int
    decisions_made: int = 0
    artifacts_produced: list[str] = Field(default_factory=list)
    errors: list[str] = Field(default_factory=list)
    next_phase: WorkflowPhase | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)

    class Config:
        extra = "forbid"


class PhaseSummary(BaseModel):
    """Summary of all phases in a workflow.

    Attributes:
        workflow_id: Unique identifier for the workflow
        total_phases: Total number of phases executed
        completed_phases: Number of phases completed successfully
        total_decisions: Total decisions made across all phases
        total_duration_ms: Total duration in milliseconds
        phase_outcomes: List of outcomes for each phase
        overall_status: Final workflow status
        created_at: When summary was generated
    """

    workflow_id: str
    total_phases: int
    completed_phases: int
    total_decisions: int
    total_duration_ms: int
    phase_outcomes: list[PhaseOutcome] = Field(default_factory=list)
    overall_status: str = "in_progress"
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    class Config:
        extra = "forbid"


class PhaseLogger:
    """Logs workflow phases with decisions and outcomes.

    Provides comprehensive phase-based logging for multi-step workflows,
    inspired by AgentRxiv's research environment logging.

    Attributes:
        workflow_id: Unique identifier for the workflow
        storage_path: Directory where logs are stored
    """

    def __init__(self, workflow_id: str, storage_path: Path) -> None:
        """Initialize logger for a workflow.

        Args:
            workflow_id: Unique identifier for the workflow
            storage_path: Directory for storing logs

        Raises:
            TypeError: If arguments are wrong type
            ValueError: If workflow_id is empty
        """
        if not isinstance(workflow_id, str):
            raise TypeError("workflow_id must be a string")
        if not isinstance(storage_path, Path):
            raise TypeError("storage_path must be a Path")
        if not workflow_id.strip():
            raise ValueError("workflow_id cannot be empty")

        self.workflow_id = workflow_id
        self.storage_path = storage_path
        self._logs_path = storage_path / "phase_logs" / workflow_id

        self._logs_path.mkdir(parents=True, exist_ok=True)

        self._current_phase: WorkflowPhase | None = None
        self._phase_start_time: datetime | None = None
        self._decisions: dict[WorkflowPhase, list[Decision]] = {}
        self._artifacts: dict[WorkflowPhase, list[Artifact]] = {}
        self._errors: dict[WorkflowPhase, list[str]] = {}
        self._outcomes: list[PhaseOutcome] = []
        self._decision_counter = 0
        self._artifact_counter = 0

    def start_phase(
        self, phase: WorkflowPhase, metadata: dict[str, Any] | None = None
    ) -> None:
        """Mark the start of a workflow phase.

        Args:
            phase: The phase to start
            metadata: Optional metadata for this phase

        Raises:
            TypeError: If phase is wrong type
            ValueError: If a phase is already in progress
        """
        if not isinstance(phase, WorkflowPhase):
            raise TypeError("phase must be a WorkflowPhase")
        if self._current_phase is not None:
            raise ValueError(
                f"Cannot start phase {phase.value}, "
                f"phase {self._current_phase.value} is still in progress"
            )

        self._current_phase = phase
        self._phase_start_time = datetime.now(UTC)
        self._decisions[phase] = []
        self._artifacts[phase] = []
        self._errors[phase] = []

        self._persist_phase_start(phase, metadata)

    def log_decision(
        self,
        decision: str,
        reasoning: str,
        alternatives: list[str] | None = None,
        selected_because: str = "",
        confidence: float = 1.0,
        agent_id: str | None = None,
        reversible: bool = True,
    ) -> Decision:
        """Log a decision made during the current phase.

        Args:
            decision: The decision that was made
            reasoning: Why this decision was made
            alternatives: Other options considered
            selected_because: Why this option was selected
            confidence: Confidence in the decision (0-1)
            agent_id: Agent that made the decision
            reversible: Whether decision can be undone

        Returns:
            The created Decision record

        Raises:
            ValueError: If no phase is in progress
        """
        if self._current_phase is None:
            raise ValueError("No phase in progress. Call start_phase first.")

        self._decision_counter += 1
        decision_record = Decision(
            decision_id=f"dec-{self.workflow_id}-{self._decision_counter}",
            decision=decision,
            reasoning=reasoning,
            alternatives_considered=alternatives or [],
            selected_because=selected_because,
            confidence=confidence,
            agent_id=agent_id,
            reversible=reversible,
            phase=self._current_phase,
        )

        self._decisions[self._current_phase].append(decision_record)
        self._persist_decision(decision_record)

        return decision_record

    def log_artifact(
        self,
        artifact_name: str,
        artifact_path: Path,
        artifact_type: str = "file",
        metadata: dict[str, Any] | None = None,
    ) -> Artifact:
        """Log an artifact produced during the current phase.

        Args:
            artifact_name: Human-readable name
            artifact_path: Path where artifact is stored
            artifact_type: Type of artifact
            metadata: Additional metadata

        Returns:
            The created Artifact record

        Raises:
            ValueError: If no phase in progress
        """
        if self._current_phase is None:
            raise ValueError("No phase in progress. Call start_phase first.")

        self._artifact_counter += 1
        artifact = Artifact(
            artifact_id=f"art-{self.workflow_id}-{self._artifact_counter}",
            name=artifact_name,
            path=str(artifact_path),
            artifact_type=artifact_type,
            phase=self._current_phase,
            metadata=metadata or {},
        )

        self._artifacts[self._current_phase].append(artifact)
        self._persist_artifact(artifact)

        return artifact

    def log_error(self, error: str, recoverable: bool = True) -> None:
        """Log an error during the current phase.

        Args:
            error: Error description
            recoverable: Whether workflow can continue

        Raises:
            ValueError: If no phase is in progress
        """
        if self._current_phase is None:
            raise ValueError("No phase in progress. Call start_phase first.")

        error_entry = f"[{'recoverable' if recoverable else 'fatal'}] {error}"
        self._errors[self._current_phase].append(error_entry)

    def end_phase(self, status: str = "success") -> PhaseOutcome:
        """Mark the end of the current phase and return outcome.

        Args:
            status: Outcome status (success, failure, partial, skipped)

        Returns:
            PhaseOutcome with phase results

        Raises:
            ValueError: If no phase is in progress
        """
        if self._current_phase is None:
            raise ValueError("No phase in progress.")
        if self._phase_start_time is None:
            raise ValueError("Phase start time not recorded.")

        end_time = datetime.now(UTC)
        duration_ms = int((end_time - self._phase_start_time).total_seconds() * 1000)

        outcome = PhaseOutcome(
            phase=self._current_phase,
            status=status,
            start_time=self._phase_start_time,
            end_time=end_time,
            duration_ms=duration_ms,
            decisions_made=len(self._decisions.get(self._current_phase, [])),
            artifacts_produced=[
                a.name for a in self._artifacts.get(self._current_phase, [])
            ],
            errors=self._errors.get(self._current_phase, []),
        )

        self._outcomes.append(outcome)
        self._persist_outcome(outcome)

        self._current_phase = None
        self._phase_start_time = None

        return outcome

    def get_current_phase(self) -> WorkflowPhase | None:
        """Get the currently active phase.

        Returns:
            Current phase or None if no phase is active
        """
        return self._current_phase

    def get_phase_decisions(self, phase: WorkflowPhase) -> list[Decision]:
        """Get all decisions made during a specific phase.

        Args:
            phase: Phase to get decisions for

        Returns:
            List of Decision records
        """
        return self._decisions.get(phase, [])

    def get_phase_artifacts(self, phase: WorkflowPhase) -> list[Artifact]:
        """Get all artifacts from a specific phase.

        Args:
            phase: Phase to get artifacts for

        Returns:
            List of Artifact records
        """
        return self._artifacts.get(phase, [])

    def get_phase_summary(self) -> PhaseSummary:
        """Get summary of all phases in the workflow.

        Returns:
            PhaseSummary with aggregated statistics
        """
        total_decisions = sum(len(d) for d in self._decisions.values())
        total_duration = sum(o.duration_ms for o in self._outcomes)
        completed = sum(1 for o in self._outcomes if o.status == "success")

        overall_status = "in_progress"
        if self._outcomes:
            if all(o.status == "success" for o in self._outcomes):
                overall_status = "success"
            elif any(o.status == "failure" for o in self._outcomes):
                overall_status = "failure"
            elif any(o.status == "partial" for o in self._outcomes):
                overall_status = "partial"

        return PhaseSummary(
            workflow_id=self.workflow_id,
            total_phases=len(self._outcomes),
            completed_phases=completed,
            total_decisions=total_decisions,
            total_duration_ms=total_duration,
            phase_outcomes=self._outcomes,
            overall_status=overall_status,
        )

    def export_workflow_log(self, filepath: Path) -> None:
        """Export complete workflow log to JSON file.

        Args:
            filepath: Path where log should be written

        Raises:
            TypeError: If filepath is not a Path
        """
        if not isinstance(filepath, Path):
            raise TypeError("filepath must be a Path")

        summary = self.get_phase_summary()

        export_data = {
            "workflow_id": self.workflow_id,
            "exported_at": datetime.now(UTC).isoformat(),
            "summary": summary.model_dump(mode="json"),
            "decisions": {
                phase.value: [d.model_dump(mode="json") for d in decisions]
                for phase, decisions in self._decisions.items()
            },
            "artifacts": {
                phase.value: [a.model_dump(mode="json") for a in artifacts]
                for phase, artifacts in self._artifacts.items()
            },
            "errors": {
                phase.value: errors for phase, errors in self._errors.items()
            },
        }

        filepath.parent.mkdir(parents=True, exist_ok=True)
        with open(filepath, "w") as f:
            json.dump(export_data, f, indent=2, default=str)

    def visualize_workflow(self) -> str:
        """Generate Mermaid diagram of workflow phases and decisions.

        Returns:
            Mermaid diagram as string
        """
        lines = ["graph TD"]

        # Add phase nodes
        for i, outcome in enumerate(self._outcomes):
            phase_id = f"phase{i}"
            status_icon = "✓" if outcome.status == "success" else "✗"
            lines.append(
                f"    {phase_id}[{outcome.phase.value} {status_icon}]"
            )

            # Connect to next phase
            if i < len(self._outcomes) - 1:
                next_id = f"phase{i + 1}"
                lines.append(f"    {phase_id} --> {next_id}")

            # Add decision count as note
            dec_count = outcome.decisions_made
            if dec_count > 0:
                lines.append(f"    {phase_id} -.- dec{i}[{dec_count} decisions]")

        # Add styling
        for i, outcome in enumerate(self._outcomes):
            phase_id = f"phase{i}"
            if outcome.status == "success":
                lines.append(f"    style {phase_id} fill:#90EE90")
            elif outcome.status == "failure":
                lines.append(f"    style {phase_id} fill:#FFB6C1")
            elif outcome.status == "partial":
                lines.append(f"    style {phase_id} fill:#FFE4B5")

        return "\n".join(lines)

    # Private persistence methods

    def _persist_phase_start(
        self, phase: WorkflowPhase, metadata: dict[str, Any] | None
    ) -> None:
        """Persist phase start event."""
        event = {
            "event": "phase_start",
            "phase": phase.value,
            "timestamp": datetime.now(UTC).isoformat(),
            "metadata": metadata or {},
        }
        self._append_to_log(event)

    def _persist_decision(self, decision: Decision) -> None:
        """Persist decision to log."""
        self._append_to_log({
            "event": "decision",
            "data": decision.model_dump(mode="json"),
        })

    def _persist_artifact(self, artifact: Artifact) -> None:
        """Persist artifact to log."""
        self._append_to_log({
            "event": "artifact",
            "data": artifact.model_dump(mode="json"),
        })

    def _persist_outcome(self, outcome: PhaseOutcome) -> None:
        """Persist phase outcome."""
        self._append_to_log({
            "event": "phase_end",
            "data": outcome.model_dump(mode="json"),
        })

    def _append_to_log(self, event: dict[str, Any]) -> None:
        """Append event to workflow log file."""
        log_file = self._logs_path / "workflow_log.jsonl"
        with open(log_file, "a") as f:
            f.write(json.dumps(event, default=str) + "\n")

