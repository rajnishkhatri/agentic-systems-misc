"""Tests for BlackBoxRecorder - Aviation-style flight recorder.

Tests the complete black box recording functionality including:
- Task plan recording and persistence
- Collaborator tracking
- Parameter substitution logging
- Execution trace recording
- Export and replay functionality
"""

from __future__ import annotations

import json
import tempfile
from datetime import UTC, datetime
from pathlib import Path

import pytest

import sys
from pathlib import Path

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.explainability.black_box import (
    AgentInfo,
    BlackBoxRecorder,
    EventType,
    ExecutionTrace,
    PlanStep,
    TaskPlan,
    TraceEvent,
)


class TestTaskPlanModel:
    """Tests for TaskPlan Pydantic model."""

    def test_create_task_plan(self) -> None:
        """Test creating a valid task plan."""
        plan = TaskPlan(
            plan_id="plan-001",
            task_id="task-001",
            steps=[
                PlanStep(
                    step_id="step-1",
                    description="Extract vendor",
                    agent_id="extractor",
                    expected_inputs=["invoice_text"],
                    expected_outputs=["vendor_name"],
                )
            ],
            dependencies={"step-2": ["step-1"]},
            rollback_points=["step-1"],
        )
        assert plan.plan_id == "plan-001"
        assert len(plan.steps) == 1
        assert plan.steps[0].is_critical is True

    def test_plan_step_defaults(self) -> None:
        """Test PlanStep default values."""
        step = PlanStep(
            step_id="step-1",
            description="Test step",
            agent_id="agent-1",
        )
        assert step.timeout_seconds == 300
        assert step.is_critical is True
        assert step.order == 0
        assert step.expected_inputs == []


class TestAgentInfo:
    """Tests for AgentInfo model."""

    def test_create_agent_info(self) -> None:
        """Test creating agent info."""
        agent = AgentInfo(
            agent_id="agent-001",
            agent_name="Invoice Extractor",
            role="extractor",
            capabilities=["extract_vendor", "extract_amount"],
        )
        assert agent.agent_id == "agent-001"
        assert len(agent.capabilities) == 2


class TestExecutionTrace:
    """Tests for ExecutionTrace model."""

    def test_create_execution_trace(self) -> None:
        """Test creating an execution trace."""
        trace = ExecutionTrace(
            trace_id="trace-001",
            task_id="task-001",
            events=[
                TraceEvent(
                    event_id="evt-1",
                    event_type=EventType.STEP_START,
                    agent_id="extractor",
                    step_id="step-1",
                )
            ],
        )
        assert trace.trace_id == "trace-001"
        assert len(trace.events) == 1
        assert trace.final_outcome is None

    def test_trace_event_types(self) -> None:
        """Test all event types can be created."""
        for event_type in EventType:
            event = TraceEvent(
                event_id=f"evt-{event_type.value}",
                event_type=event_type,
            )
            assert event.event_type == event_type


class TestBlackBoxRecorder:
    """Tests for BlackBoxRecorder class."""

    @pytest.fixture
    def temp_storage(self) -> Path:
        """Create temporary storage directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)

    @pytest.fixture
    def recorder(self, temp_storage: Path) -> BlackBoxRecorder:
        """Create a BlackBoxRecorder instance."""
        return BlackBoxRecorder(workflow_id="test-workflow", storage_path=temp_storage)

    def test_init_creates_directories(self, temp_storage: Path) -> None:
        """Test initialization creates required directories."""
        recorder = BlackBoxRecorder(workflow_id="test", storage_path=temp_storage)
        assert recorder._recordings_path.exists()

    def test_init_validates_workflow_id(self, temp_storage: Path) -> None:
        """Test initialization validates workflow_id."""
        with pytest.raises(ValueError, match="cannot be empty"):
            BlackBoxRecorder(workflow_id="  ", storage_path=temp_storage)

    def test_init_validates_types(self, temp_storage: Path) -> None:
        """Test initialization validates argument types."""
        with pytest.raises(TypeError, match="must be a string"):
            BlackBoxRecorder(workflow_id=123, storage_path=temp_storage)  # type: ignore

        with pytest.raises(TypeError, match="must be a Path"):
            BlackBoxRecorder(workflow_id="test", storage_path="/tmp")  # type: ignore

    def test_record_task_plan(self, recorder: BlackBoxRecorder) -> None:
        """Test recording a task plan."""
        plan = TaskPlan(
            plan_id="plan-001",
            task_id="task-001",
            steps=[
                PlanStep(
                    step_id="step-1",
                    description="Test step",
                    agent_id="agent-1",
                )
            ],
        )
        recorder.record_task_plan("task-001", plan)

        # Verify in memory
        assert recorder.get_task_plan("task-001") == plan

        # Verify persisted
        plan_file = recorder._recordings_path / "task-001_plan.json"
        assert plan_file.exists()

    def test_record_collaborators(self, recorder: BlackBoxRecorder) -> None:
        """Test recording collaborators."""
        agents = [
            AgentInfo(
                agent_id="agent-1",
                agent_name="Extractor",
                role="extractor",
            ),
            AgentInfo(
                agent_id="agent-2",
                agent_name="Validator",
                role="validator",
            ),
        ]
        recorder.record_collaborators("task-001", agents)

        # Verify in memory
        assert len(recorder.get_collaborators("task-001")) == 2

        # Verify persisted
        collab_file = recorder._recordings_path / "task-001_collaborators.json"
        assert collab_file.exists()

    def test_record_parameter_substitution(self, recorder: BlackBoxRecorder) -> None:
        """Test recording parameter substitutions."""
        recorder.record_parameter_substitution(
            task_id="task-001",
            param="model_name",
            old_val="gpt-3.5",
            new_val="gpt-4",
            reason="Higher accuracy needed",
            agent_id="planner",
        )

        # Verify persisted
        params_file = recorder._recordings_path / "task-001_params.json"
        assert params_file.exists()

        with open(params_file) as f:
            data = json.load(f)
        assert len(data) == 1
        assert data[0]["param_name"] == "model_name"
        assert data[0]["old_value"] == "gpt-3.5"
        assert data[0]["new_value"] == "gpt-4"

    def test_record_execution_trace(self, recorder: BlackBoxRecorder) -> None:
        """Test recording execution traces."""
        trace = ExecutionTrace(
            trace_id="trace-001",
            task_id="task-001",
            events=[
                TraceEvent(
                    event_id="evt-1",
                    event_type=EventType.STEP_START,
                    agent_id="extractor",
                    step_id="step-1",
                )
            ],
            final_outcome="success",
        )
        recorder.record_execution_trace("task-001", trace)

        # Verify in memory
        assert recorder.get_execution_trace("task-001") == trace

        # Verify persisted
        trace_file = recorder._recordings_path / "task-001_trace.json"
        assert trace_file.exists()

    def test_add_trace_event(self, recorder: BlackBoxRecorder) -> None:
        """Test adding individual trace events."""
        event1 = TraceEvent(
            event_id="evt-1",
            event_type=EventType.STEP_START,
            agent_id="extractor",
        )
        recorder.add_trace_event("task-001", event1)

        event2 = TraceEvent(
            event_id="evt-2",
            event_type=EventType.STEP_END,
            agent_id="extractor",
            duration_ms=150,
        )
        recorder.add_trace_event("task-001", event2)

        trace = recorder.get_execution_trace("task-001")
        assert trace is not None
        assert len(trace.events) == 2

    def test_export_black_box(self, recorder: BlackBoxRecorder, temp_storage: Path) -> None:
        """Test exporting black box data."""
        # Record various data
        plan = TaskPlan(
            plan_id="plan-001",
            task_id="task-001",
            steps=[PlanStep(step_id="s1", description="Test", agent_id="a1")],
        )
        recorder.record_task_plan("task-001", plan)
        recorder.record_collaborators(
            "task-001",
            [AgentInfo(agent_id="a1", agent_name="Agent 1", role="test")],
        )
        recorder.record_parameter_substitution(
            "task-001", "param1", "old", "new", "reason"
        )

        # Export
        export_path = temp_storage / "export" / "blackbox.json"
        recorder.export_black_box("task-001", export_path)

        assert export_path.exists()

        with open(export_path) as f:
            data = json.load(f)

        assert data["workflow_id"] == "test-workflow"
        assert data["task_id"] == "task-001"
        assert data["task_plan"] is not None
        assert len(data["collaborators"]) == 1
        assert len(data["parameter_substitutions"]) == 1

    def test_replay(self, recorder: BlackBoxRecorder) -> None:
        """Test replaying recorded events."""
        # Record some events
        recorder.record_task_plan(
            "task-001",
            TaskPlan(plan_id="p1", task_id="task-001", steps=[]),
        )
        recorder.record_collaborators(
            "task-001",
            [AgentInfo(agent_id="a1", agent_name="Agent", role="test")],
        )

        # Replay
        events = list(recorder.replay("task-001"))
        assert len(events) >= 2

    def test_compute_hash(self) -> None:
        """Test hash computation for integrity verification."""
        hash1 = BlackBoxRecorder.compute_hash({"key": "value"})
        hash2 = BlackBoxRecorder.compute_hash({"key": "value"})
        hash3 = BlackBoxRecorder.compute_hash({"key": "different"})

        assert hash1 == hash2  # Same data = same hash
        assert hash1 != hash3  # Different data = different hash
        assert len(hash1) == 64  # SHA256 produces 64 hex characters


class TestBlackBoxRecorderEdgeCases:
    """Edge case tests for BlackBoxRecorder."""

    @pytest.fixture
    def temp_storage(self) -> Path:
        """Create temporary storage directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)

    def test_get_nonexistent_task_plan(self, temp_storage: Path) -> None:
        """Test getting a task plan that doesn't exist."""
        recorder = BlackBoxRecorder(workflow_id="test", storage_path=temp_storage)
        assert recorder.get_task_plan("nonexistent") is None

    def test_get_nonexistent_collaborators(self, temp_storage: Path) -> None:
        """Test getting collaborators that don't exist."""
        recorder = BlackBoxRecorder(workflow_id="test", storage_path=temp_storage)
        assert recorder.get_collaborators("nonexistent") == []

    def test_empty_task_id_rejected(self, temp_storage: Path) -> None:
        """Test empty task_id is rejected."""
        recorder = BlackBoxRecorder(workflow_id="test", storage_path=temp_storage)

        with pytest.raises(ValueError, match="cannot be empty"):
            recorder.record_task_plan(
                "  ",
                TaskPlan(plan_id="p1", task_id="t1", steps=[]),
            )

