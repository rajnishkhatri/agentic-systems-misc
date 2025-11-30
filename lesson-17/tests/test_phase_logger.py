"""Tests for PhaseLogger - Multi-phase workflow logging.

Tests the PhaseLogger implementation including:
- Phase lifecycle (start, end)
- Decision logging with reasoning
- Artifact tracking
- Error logging
- Workflow summary generation
- Mermaid visualization
"""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

import pytest

import sys
from pathlib import Path

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.explainability.phase_logger import (
    Artifact,
    Decision,
    PhaseLogger,
    PhaseOutcome,
    PhaseSummary,
    WorkflowPhase,
)


class TestWorkflowPhaseEnum:
    """Tests for WorkflowPhase enum."""

    def test_all_phases_exist(self) -> None:
        """Test all expected phases exist."""
        assert WorkflowPhase.PLANNING.value == "planning"
        assert WorkflowPhase.LITERATURE_REVIEW.value == "literature_review"
        assert WorkflowPhase.DATA_COLLECTION.value == "data_collection"
        assert WorkflowPhase.EXECUTION.value == "execution"
        assert WorkflowPhase.EXPERIMENT.value == "experiment"
        assert WorkflowPhase.VALIDATION.value == "validation"
        assert WorkflowPhase.REPORTING.value == "reporting"
        assert WorkflowPhase.COMPLETED.value == "completed"
        assert WorkflowPhase.FAILED.value == "failed"


class TestDecisionModel:
    """Tests for Decision Pydantic model."""

    def test_create_decision(self) -> None:
        """Test creating a valid decision."""
        decision = Decision(
            decision_id="dec-001",
            decision="Use GPT-4 for extraction",
            reasoning="Higher accuracy needed for financial data",
            alternatives_considered=["GPT-3.5", "Claude"],
            selected_because="Best performance on financial extraction benchmarks",
            confidence=0.9,
            agent_id="planner",
            reversible=True,
            phase=WorkflowPhase.PLANNING,
        )
        assert decision.decision_id == "dec-001"
        assert len(decision.alternatives_considered) == 2
        assert decision.confidence == 0.9

    def test_decision_defaults(self) -> None:
        """Test decision default values."""
        decision = Decision(
            decision_id="dec-001",
            decision="Test decision",
            reasoning="Test reasoning",
        )
        assert decision.alternatives_considered == []
        assert decision.confidence == 1.0
        assert decision.reversible is True
        assert decision.phase is None


class TestArtifactModel:
    """Tests for Artifact Pydantic model."""

    def test_create_artifact(self) -> None:
        """Test creating a valid artifact."""
        artifact = Artifact(
            artifact_id="art-001",
            name="extraction_results",
            path="/output/results.json",
            artifact_type="file",
            phase=WorkflowPhase.EXECUTION,
            metadata={"format": "json", "size_bytes": 1024},
        )
        assert artifact.artifact_id == "art-001"
        assert artifact.artifact_type == "file"


class TestPhaseOutcomeModel:
    """Tests for PhaseOutcome Pydantic model."""

    def test_create_phase_outcome(self) -> None:
        """Test creating a valid phase outcome."""
        from datetime import UTC, datetime, timedelta

        start = datetime.now(UTC)
        end = start + timedelta(seconds=10)

        outcome = PhaseOutcome(
            phase=WorkflowPhase.PLANNING,
            status="success",
            start_time=start,
            end_time=end,
            duration_ms=10000,
            decisions_made=3,
            artifacts_produced=["plan.json"],
            errors=[],
        )
        assert outcome.phase == WorkflowPhase.PLANNING
        assert outcome.status == "success"
        assert outcome.decisions_made == 3


class TestPhaseSummaryModel:
    """Tests for PhaseSummary Pydantic model."""

    def test_create_phase_summary(self) -> None:
        """Test creating a valid phase summary."""
        summary = PhaseSummary(
            workflow_id="test-001",
            total_phases=3,
            completed_phases=2,
            total_decisions=5,
            total_duration_ms=30000,
            overall_status="partial",
        )
        assert summary.workflow_id == "test-001"
        assert summary.completed_phases == 2


class TestPhaseLogger:
    """Tests for PhaseLogger class."""

    @pytest.fixture
    def temp_storage(self) -> Path:
        """Create temporary storage directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)

    @pytest.fixture
    def logger(self, temp_storage: Path) -> PhaseLogger:
        """Create a PhaseLogger instance."""
        return PhaseLogger(workflow_id="test-workflow", storage_path=temp_storage)

    def test_init_creates_directories(self, temp_storage: Path) -> None:
        """Test initialization creates required directories."""
        logger = PhaseLogger(workflow_id="test", storage_path=temp_storage)
        assert logger._logs_path.exists()

    def test_init_validates_workflow_id(self, temp_storage: Path) -> None:
        """Test initialization validates workflow_id."""
        with pytest.raises(ValueError, match="cannot be empty"):
            PhaseLogger(workflow_id="  ", storage_path=temp_storage)

    def test_init_validates_types(self, temp_storage: Path) -> None:
        """Test initialization validates argument types."""
        with pytest.raises(TypeError, match="must be a string"):
            PhaseLogger(workflow_id=123, storage_path=temp_storage)  # type: ignore

        with pytest.raises(TypeError, match="must be a Path"):
            PhaseLogger(workflow_id="test", storage_path="/tmp")  # type: ignore

    def test_start_phase(self, logger: PhaseLogger) -> None:
        """Test starting a phase."""
        logger.start_phase(WorkflowPhase.PLANNING)
        assert logger.get_current_phase() == WorkflowPhase.PLANNING

    def test_start_phase_while_active_rejected(self, logger: PhaseLogger) -> None:
        """Test starting a phase while another is active is rejected."""
        logger.start_phase(WorkflowPhase.PLANNING)

        with pytest.raises(ValueError, match="still in progress"):
            logger.start_phase(WorkflowPhase.EXECUTION)

    def test_log_decision(self, logger: PhaseLogger) -> None:
        """Test logging a decision."""
        logger.start_phase(WorkflowPhase.PLANNING)

        decision = logger.log_decision(
            decision="Use GPT-4",
            reasoning="Higher accuracy",
            alternatives=["GPT-3.5", "Claude"],
            selected_because="Best benchmarks",
            confidence=0.9,
            agent_id="planner",
        )

        assert decision.decision == "Use GPT-4"
        assert decision.phase == WorkflowPhase.PLANNING

        decisions = logger.get_phase_decisions(WorkflowPhase.PLANNING)
        assert len(decisions) == 1

    def test_log_decision_without_phase_rejected(self, logger: PhaseLogger) -> None:
        """Test logging decision without active phase is rejected."""
        with pytest.raises(ValueError, match="No phase in progress"):
            logger.log_decision(
                decision="Test",
                reasoning="Test",
            )

    def test_log_artifact(self, logger: PhaseLogger, temp_storage: Path) -> None:
        """Test logging an artifact."""
        logger.start_phase(WorkflowPhase.EXECUTION)

        artifact = logger.log_artifact(
            artifact_name="results",
            artifact_path=temp_storage / "results.json",
            artifact_type="file",
            metadata={"format": "json"},
        )

        assert artifact.name == "results"
        assert artifact.phase == WorkflowPhase.EXECUTION

        artifacts = logger.get_phase_artifacts(WorkflowPhase.EXECUTION)
        assert len(artifacts) == 1

    def test_log_error(self, logger: PhaseLogger) -> None:
        """Test logging an error."""
        logger.start_phase(WorkflowPhase.VALIDATION)

        logger.log_error("Validation failed", recoverable=True)
        logger.log_error("Critical failure", recoverable=False)

        # End phase to check errors
        outcome = logger.end_phase("failure")
        assert len(outcome.errors) == 2
        assert "[recoverable]" in outcome.errors[0]
        assert "[fatal]" in outcome.errors[1]

    def test_end_phase(self, logger: PhaseLogger) -> None:
        """Test ending a phase."""
        logger.start_phase(WorkflowPhase.PLANNING)
        logger.log_decision("Test decision", "Test reasoning")

        outcome = logger.end_phase("success")

        assert outcome.phase == WorkflowPhase.PLANNING
        assert outcome.status == "success"
        assert outcome.decisions_made == 1
        assert logger.get_current_phase() is None

    def test_end_phase_without_active_rejected(self, logger: PhaseLogger) -> None:
        """Test ending phase without active phase is rejected."""
        with pytest.raises(ValueError, match="No phase in progress"):
            logger.end_phase()

    def test_get_phase_summary(self, logger: PhaseLogger) -> None:
        """Test getting workflow phase summary."""
        # Execute multiple phases
        logger.start_phase(WorkflowPhase.PLANNING)
        logger.log_decision("Plan decision", "Reasoning")
        logger.end_phase("success")

        logger.start_phase(WorkflowPhase.EXECUTION)
        logger.log_decision("Exec decision 1", "Reasoning")
        logger.log_decision("Exec decision 2", "Reasoning")
        logger.end_phase("success")

        summary = logger.get_phase_summary()

        assert summary.workflow_id == "test-workflow"
        assert summary.total_phases == 2
        assert summary.completed_phases == 2
        assert summary.total_decisions == 3
        assert summary.overall_status == "success"

    def test_export_workflow_log(self, logger: PhaseLogger, temp_storage: Path) -> None:
        """Test exporting workflow log."""
        logger.start_phase(WorkflowPhase.PLANNING)
        logger.log_decision("Test", "Reasoning")
        logger.end_phase("success")

        export_path = temp_storage / "workflow_log.json"
        logger.export_workflow_log(export_path)

        assert export_path.exists()

        with open(export_path) as f:
            data = json.load(f)

        assert data["workflow_id"] == "test-workflow"
        assert "summary" in data
        assert "decisions" in data

    def test_visualize_workflow(self, logger: PhaseLogger) -> None:
        """Test generating Mermaid visualization."""
        logger.start_phase(WorkflowPhase.PLANNING)
        logger.log_decision("Decision 1", "Reason")
        logger.end_phase("success")

        logger.start_phase(WorkflowPhase.EXECUTION)
        logger.end_phase("failure")

        mermaid = logger.visualize_workflow()

        assert "graph TD" in mermaid
        assert "planning" in mermaid
        assert "execution" in mermaid
        assert "fill:#90EE90" in mermaid  # Success color
        assert "fill:#FFB6C1" in mermaid  # Failure color


class TestPhaseLoggerEdgeCases:
    """Edge case tests for PhaseLogger."""

    @pytest.fixture
    def temp_storage(self) -> Path:
        """Create temporary storage directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)

    def test_get_decisions_nonexistent_phase(self, temp_storage: Path) -> None:
        """Test getting decisions for a phase that was never started."""
        logger = PhaseLogger(workflow_id="test", storage_path=temp_storage)
        decisions = logger.get_phase_decisions(WorkflowPhase.PLANNING)
        assert decisions == []

    def test_get_artifacts_nonexistent_phase(self, temp_storage: Path) -> None:
        """Test getting artifacts for a phase that was never started."""
        logger = PhaseLogger(workflow_id="test", storage_path=temp_storage)
        artifacts = logger.get_phase_artifacts(WorkflowPhase.PLANNING)
        assert artifacts == []

    def test_empty_workflow_summary(self, temp_storage: Path) -> None:
        """Test summary for workflow with no phases."""
        logger = PhaseLogger(workflow_id="test", storage_path=temp_storage)
        summary = logger.get_phase_summary()

        assert summary.total_phases == 0
        assert summary.total_decisions == 0
        assert summary.overall_status == "in_progress"

    def test_partial_workflow_status(self, temp_storage: Path) -> None:
        """Test workflow status with partial phase completion."""
        logger = PhaseLogger(workflow_id="test", storage_path=temp_storage)

        logger.start_phase(WorkflowPhase.PLANNING)
        logger.end_phase("success")

        logger.start_phase(WorkflowPhase.EXECUTION)
        logger.end_phase("partial")

        summary = logger.get_phase_summary()
        assert summary.overall_status == "partial"

    def test_failed_workflow_status(self, temp_storage: Path) -> None:
        """Test workflow status when a phase fails."""
        logger = PhaseLogger(workflow_id="test", storage_path=temp_storage)

        logger.start_phase(WorkflowPhase.PLANNING)
        logger.end_phase("success")

        logger.start_phase(WorkflowPhase.EXECUTION)
        logger.end_phase("failure")

        summary = logger.get_phase_summary()
        assert summary.overall_status == "failure"

