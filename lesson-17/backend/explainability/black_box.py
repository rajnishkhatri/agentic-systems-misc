"""Black Box Recorder - Aviation-style flight recorder for agent workflows.

This module provides comprehensive recording of agent activities for post-incident
analysis, debugging, and compliance auditing. Inspired by aviation "black boxes,"
it captures:

- Task plans with steps, dependencies, and rollback points
- Collaborator lists (which agents participated)
- Parameter substitution logs (before/after values with reasoning)
- Complete execution traces with decision points and outcomes

Builds on:
- lesson-16/backend/reliability/audit_log.py - Extends AuditLogger patterns
- lesson-16/backend/reliability/checkpoint.py - Reuses persistence patterns

Example:
    >>> recorder = BlackBoxRecorder(workflow_id="invoice-001", storage_path=Path("cache/"))
    >>> recorder.record_task_plan("task-1", TaskPlan(...))
    >>> recorder.record_collaborators("task-1", [AgentInfo(...)])
    >>> recorder.record_execution_trace("task-1", ExecutionTrace(...))
    >>> recorder.export_black_box("task-1", Path("audit/task-1-blackbox.json"))
"""

from __future__ import annotations

import hashlib
import json
from collections.abc import Iterator
from datetime import UTC, datetime
from enum import Enum
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field


class EventType(str, Enum):
    """Types of events that can be recorded in the black box."""

    STEP_START = "step_start"
    STEP_END = "step_end"
    DECISION = "decision"
    ERROR = "error"
    CHECKPOINT = "checkpoint"
    PARAMETER_CHANGE = "parameter_change"
    COLLABORATOR_JOIN = "collaborator_join"
    COLLABORATOR_LEAVE = "collaborator_leave"
    ROLLBACK = "rollback"
    TASK_PLAN = "task_plan"


class PlanStep(BaseModel):
    """Individual step in a task plan.

    Attributes:
        step_id: Unique identifier for this step
        description: Human-readable description of the step
        agent_id: ID of the agent responsible for this step
        expected_inputs: List of expected input field names
        expected_outputs: List of expected output field names
        timeout_seconds: Maximum execution time for this step
        is_critical: If True, failure stops the entire workflow
        order: Execution order (for sequential steps)
    """

    step_id: str
    description: str
    agent_id: str
    expected_inputs: list[str] = Field(default_factory=list)
    expected_outputs: list[str] = Field(default_factory=list)
    timeout_seconds: int = 300
    is_critical: bool = True
    order: int = 0

    class Config:
        extra = "forbid"


class TaskPlan(BaseModel):
    """Persisted task plan with steps, dependencies, and rollback points.

    Attributes:
        plan_id: Unique identifier for this plan
        task_id: ID of the task this plan is for
        created_at: Timestamp when plan was created
        steps: List of plan steps to execute
        dependencies: Mapping of step_id to list of dependent step_ids
        rollback_points: List of step_ids that can be safely rolled back to
        metadata: Additional plan metadata
    """

    plan_id: str
    task_id: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    steps: list[PlanStep] = Field(default_factory=list)
    dependencies: dict[str, list[str]] = Field(default_factory=dict)
    rollback_points: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)

    class Config:
        extra = "forbid"


class AgentInfo(BaseModel):
    """Information about an agent collaborating in a workflow.

    Attributes:
        agent_id: Unique identifier for the agent
        agent_name: Human-readable name
        role: Role in the workflow (e.g., "extractor", "validator")
        joined_at: When the agent joined the workflow
        capabilities: List of capability names this agent provides
    """

    agent_id: str
    agent_name: str
    role: str
    joined_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    capabilities: list[str] = Field(default_factory=list)

    class Config:
        extra = "forbid"


class TraceEvent(BaseModel):
    """Single event in an execution trace.

    Attributes:
        event_id: Unique identifier for this event
        timestamp: When the event occurred
        event_type: Type of event (step_start, step_end, decision, error, etc.)
        agent_id: ID of the agent involved (if applicable)
        step_id: ID of the step involved (if applicable)
        input_hash: SHA256 hash of inputs for integrity verification
        output_hash: SHA256 hash of outputs (if applicable)
        duration_ms: Duration in milliseconds (if applicable)
        metadata: Additional event data
    """

    event_id: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))
    event_type: EventType
    agent_id: str | None = None
    step_id: str | None = None
    input_hash: str | None = None
    output_hash: str | None = None
    duration_ms: int | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)

    class Config:
        extra = "forbid"


class ExecutionTrace(BaseModel):
    """Complete execution history with decision points and outcomes.

    Attributes:
        trace_id: Unique identifier for this trace
        task_id: ID of the task being traced
        start_time: When execution started
        end_time: When execution ended (None if still running)
        events: List of trace events in chronological order
        final_outcome: Final status (success, failure, timeout, cancelled)
        error_chain: List of error messages for cascade failure analysis
    """

    trace_id: str
    task_id: str
    start_time: datetime = Field(default_factory=lambda: datetime.now(UTC))
    end_time: datetime | None = None
    events: list[TraceEvent] = Field(default_factory=list)
    final_outcome: str | None = None
    error_chain: list[str] | None = None

    class Config:
        extra = "forbid"


class ParameterSubstitution(BaseModel):
    """Record of a parameter value change.

    Attributes:
        param_name: Name of the parameter that changed
        old_value: Previous value (serialized to string)
        new_value: New value (serialized to string)
        reason: Why the change was made
        timestamp: When the change occurred
        agent_id: Agent that made the change (if applicable)
    """

    param_name: str
    old_value: str
    new_value: str
    reason: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))
    agent_id: str | None = None

    class Config:
        extra = "forbid"


class RecordedEvent(BaseModel):
    """Wrapper for any recorded event in the black box.

    Attributes:
        event_type: Type of recorded event
        timestamp: When it was recorded
        data: The actual event data
    """

    event_type: str
    timestamp: datetime
    data: dict[str, Any]


class BlackBoxRecorder:
    """Aviation-style flight recorder for agent workflows.

    Captures comprehensive records of all workflow activities for:
    - Post-incident analysis and debugging
    - Compliance auditing
    - Workflow replay and analysis
    - Cascade failure investigation

    Extends patterns from lesson-16 AuditLogger for structured logging
    and checkpoint.py for persistence.

    Attributes:
        workflow_id: Unique identifier for the workflow being recorded
        storage_path: Path where recordings are stored
    """

    def __init__(self, workflow_id: str, storage_path: Path) -> None:
        """Initialize the black box recorder.

        Args:
            workflow_id: Unique identifier for the workflow
            storage_path: Directory path for storing recordings

        Raises:
            TypeError: If workflow_id is not a string or storage_path is not a Path
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
        self._recordings_path = storage_path / "black_box_recordings" / workflow_id

        # Ensure storage directory exists
        self._recordings_path.mkdir(parents=True, exist_ok=True)

        # In-memory stores for current session
        self._task_plans: dict[str, TaskPlan] = {}
        self._collaborators: dict[str, list[AgentInfo]] = {}
        self._parameter_subs: dict[str, list[ParameterSubstitution]] = {}
        self._execution_traces: dict[str, ExecutionTrace] = {}
        self._all_events: list[RecordedEvent] = []

    def record_task_plan(self, task_id: str, plan: TaskPlan) -> None:
        """Persist a task plan with steps, dependencies, and rollback points.

        Args:
            task_id: Unique identifier for the task
            plan: The task plan to record

        Raises:
            TypeError: If arguments are wrong type
            ValueError: If task_id is empty
        """
        if not isinstance(task_id, str):
            raise TypeError("task_id must be a string")
        if not isinstance(plan, TaskPlan):
            raise TypeError("plan must be a TaskPlan")
        if not task_id.strip():
            raise ValueError("task_id cannot be empty")

        self._task_plans[task_id] = plan

        # Record as event
        event = RecordedEvent(
            event_type=EventType.TASK_PLAN.value,
            timestamp=datetime.now(UTC),
            data=plan.model_dump(mode="json"),
        )
        self._all_events.append(event)

        # Persist to disk
        self._persist_task_plan(task_id, plan)

    def record_collaborators(self, task_id: str, agents: list[AgentInfo]) -> None:
        """Record which agents participated in a task.

        Args:
            task_id: Unique identifier for the task
            agents: List of agents collaborating on this task

        Raises:
            TypeError: If arguments are wrong type
            ValueError: If task_id is empty
        """
        if not isinstance(task_id, str):
            raise TypeError("task_id must be a string")
        if not isinstance(agents, list):
            raise TypeError("agents must be a list")
        if not task_id.strip():
            raise ValueError("task_id cannot be empty")

        self._collaborators[task_id] = agents

        # Record join events for each agent
        for agent in agents:
            event = RecordedEvent(
                event_type=EventType.COLLABORATOR_JOIN.value,
                timestamp=agent.joined_at,
                data=agent.model_dump(mode="json"),
            )
            self._all_events.append(event)

        # Persist to disk
        self._persist_collaborators(task_id, agents)

    def record_parameter_substitution(
        self,
        task_id: str,
        param: str,
        old_val: Any,
        new_val: Any,
        reason: str,
        agent_id: str | None = None,
    ) -> None:
        """Log a parameter change with before/after values and justification.

        Args:
            task_id: Unique identifier for the task
            param: Name of the parameter that changed
            old_val: Previous value
            new_val: New value
            reason: Why the change was made
            agent_id: Agent that made the change (optional)

        Raises:
            TypeError: If arguments are wrong type
            ValueError: If task_id or param is empty
        """
        if not isinstance(task_id, str):
            raise TypeError("task_id must be a string")
        if not isinstance(param, str):
            raise TypeError("param must be a string")
        if not isinstance(reason, str):
            raise TypeError("reason must be a string")
        if not task_id.strip():
            raise ValueError("task_id cannot be empty")
        if not param.strip():
            raise ValueError("param cannot be empty")

        substitution = ParameterSubstitution(
            param_name=param,
            old_value=str(old_val),
            new_value=str(new_val),
            reason=reason,
            agent_id=agent_id,
        )

        if task_id not in self._parameter_subs:
            self._parameter_subs[task_id] = []
        self._parameter_subs[task_id].append(substitution)

        # Record as event
        event = RecordedEvent(
            event_type=EventType.PARAMETER_CHANGE.value,
            timestamp=substitution.timestamp,
            data=substitution.model_dump(mode="json"),
        )
        self._all_events.append(event)

        # Persist to disk
        self._persist_parameter_substitutions(task_id)

    def record_execution_trace(self, task_id: str, trace: ExecutionTrace) -> None:
        """Store complete execution history with decision points.

        Args:
            task_id: Unique identifier for the task
            trace: The execution trace to record

        Raises:
            TypeError: If arguments are wrong type
            ValueError: If task_id is empty
        """
        if not isinstance(task_id, str):
            raise TypeError("task_id must be a string")
        if not isinstance(trace, ExecutionTrace):
            raise TypeError("trace must be an ExecutionTrace")
        if not task_id.strip():
            raise ValueError("task_id cannot be empty")

        self._execution_traces[task_id] = trace

        # Record trace events
        for trace_event in trace.events:
            event = RecordedEvent(
                event_type=f"trace_{trace_event.event_type.value}",
                timestamp=trace_event.timestamp,
                data=trace_event.model_dump(mode="json"),
            )
            self._all_events.append(event)

        # Persist to disk
        self._persist_execution_trace(task_id, trace)

    def add_trace_event(self, task_id: str, event: TraceEvent) -> None:
        """Add a single event to an existing execution trace.

        Args:
            task_id: Unique identifier for the task
            event: The trace event to add

        Raises:
            TypeError: If arguments are wrong type
            ValueError: If task_id is empty or trace doesn't exist
        """
        if not isinstance(task_id, str):
            raise TypeError("task_id must be a string")
        if not isinstance(event, TraceEvent):
            raise TypeError("event must be a TraceEvent")
        if not task_id.strip():
            raise ValueError("task_id cannot be empty")

        if task_id not in self._execution_traces:
            # Create new trace if doesn't exist
            self._execution_traces[task_id] = ExecutionTrace(
                trace_id=f"trace-{task_id}-{datetime.now(UTC).isoformat()}",
                task_id=task_id,
            )

        self._execution_traces[task_id].events.append(event)

        # Record as event
        recorded = RecordedEvent(
            event_type=f"trace_{event.event_type.value}",
            timestamp=event.timestamp,
            data=event.model_dump(mode="json"),
        )
        self._all_events.append(recorded)

        # Persist to disk
        self._persist_execution_trace(task_id, self._execution_traces[task_id])

    def export_black_box(self, task_id: str, filepath: Path) -> None:
        """Export all recordings for a task to a single JSON file.

        Creates a comprehensive export containing:
        - Task plan
        - Collaborator list
        - Parameter substitutions
        - Execution trace
        - All recorded events

        Args:
            task_id: Unique identifier for the task
            filepath: Path where the export file should be written

        Raises:
            TypeError: If arguments are wrong type
            ValueError: If task_id is empty
        """
        if not isinstance(task_id, str):
            raise TypeError("task_id must be a string")
        if not isinstance(filepath, Path):
            raise TypeError("filepath must be a Path")
        if not task_id.strip():
            raise ValueError("task_id cannot be empty")

        export_data = {
            "workflow_id": self.workflow_id,
            "task_id": task_id,
            "exported_at": datetime.now(UTC).isoformat(),
            "task_plan": (
                self._task_plans[task_id].model_dump(mode="json")
                if task_id in self._task_plans
                else None
            ),
            "collaborators": (
                [a.model_dump(mode="json") for a in self._collaborators[task_id]]
                if task_id in self._collaborators
                else []
            ),
            "parameter_substitutions": (
                [s.model_dump(mode="json") for s in self._parameter_subs[task_id]]
                if task_id in self._parameter_subs
                else []
            ),
            "execution_trace": (
                self._execution_traces[task_id].model_dump(mode="json")
                if task_id in self._execution_traces
                else None
            ),
            "all_events": [e.model_dump(mode="json") for e in self._all_events],
        }

        # Ensure parent directory exists
        filepath.parent.mkdir(parents=True, exist_ok=True)

        with open(filepath, "w") as f:
            json.dump(export_data, f, indent=2, default=str)

    def replay(self, task_id: str) -> Iterator[RecordedEvent]:
        """Replay recorded events for debugging/analysis.

        Yields events in chronological order for the specified task.

        Args:
            task_id: Unique identifier for the task

        Yields:
            RecordedEvent instances in chronological order

        Raises:
            TypeError: If task_id is wrong type
            ValueError: If task_id is empty
        """
        if not isinstance(task_id, str):
            raise TypeError("task_id must be a string")
        if not task_id.strip():
            raise ValueError("task_id cannot be empty")

        # Load from disk if not in memory
        self._load_from_disk(task_id)

        # Sort all events by timestamp
        sorted_events = sorted(self._all_events, key=lambda e: e.timestamp)

        for event in sorted_events:
            yield event

    def get_task_plan(self, task_id: str) -> TaskPlan | None:
        """Get the task plan for a specific task.

        Args:
            task_id: Unique identifier for the task

        Returns:
            TaskPlan if found, None otherwise
        """
        return self._task_plans.get(task_id)

    def get_collaborators(self, task_id: str) -> list[AgentInfo]:
        """Get the collaborators for a specific task.

        Args:
            task_id: Unique identifier for the task

        Returns:
            List of AgentInfo (empty if none found)
        """
        return self._collaborators.get(task_id, [])

    def get_execution_trace(self, task_id: str) -> ExecutionTrace | None:
        """Get the execution trace for a specific task.

        Args:
            task_id: Unique identifier for the task

        Returns:
            ExecutionTrace if found, None otherwise
        """
        return self._execution_traces.get(task_id)

    @staticmethod
    def compute_hash(data: Any) -> str:
        """Compute SHA256 hash of data for integrity verification.

        Args:
            data: Data to hash (will be JSON serialized)

        Returns:
            Hex string of SHA256 hash
        """
        serialized = json.dumps(data, sort_keys=True, default=str)
        return hashlib.sha256(serialized.encode()).hexdigest()

    # Private persistence methods

    def _persist_task_plan(self, task_id: str, plan: TaskPlan) -> None:
        """Persist task plan to disk."""
        filepath = self._recordings_path / f"{task_id}_plan.json"
        with open(filepath, "w") as f:
            json.dump(plan.model_dump(mode="json"), f, indent=2, default=str)

    def _persist_collaborators(self, task_id: str, agents: list[AgentInfo]) -> None:
        """Persist collaborators to disk."""
        filepath = self._recordings_path / f"{task_id}_collaborators.json"
        with open(filepath, "w") as f:
            json.dump([a.model_dump(mode="json") for a in agents], f, indent=2, default=str)

    def _persist_parameter_substitutions(self, task_id: str) -> None:
        """Persist parameter substitutions to disk."""
        filepath = self._recordings_path / f"{task_id}_params.json"
        subs = self._parameter_subs.get(task_id, [])
        with open(filepath, "w") as f:
            json.dump([s.model_dump(mode="json") for s in subs], f, indent=2, default=str)

    def _persist_execution_trace(self, task_id: str, trace: ExecutionTrace) -> None:
        """Persist execution trace to disk."""
        filepath = self._recordings_path / f"{task_id}_trace.json"
        with open(filepath, "w") as f:
            json.dump(trace.model_dump(mode="json"), f, indent=2, default=str)

    def _load_from_disk(self, task_id: str) -> None:
        """Load recordings from disk for a task."""
        # Load task plan
        plan_path = self._recordings_path / f"{task_id}_plan.json"
        if plan_path.exists() and task_id not in self._task_plans:
            with open(plan_path) as f:
                data = json.load(f)
                self._task_plans[task_id] = TaskPlan(**data)

        # Load collaborators
        collab_path = self._recordings_path / f"{task_id}_collaborators.json"
        if collab_path.exists() and task_id not in self._collaborators:
            with open(collab_path) as f:
                data = json.load(f)
                self._collaborators[task_id] = [AgentInfo(**a) for a in data]

        # Load parameter substitutions
        params_path = self._recordings_path / f"{task_id}_params.json"
        if params_path.exists() and task_id not in self._parameter_subs:
            with open(params_path) as f:
                data = json.load(f)
                self._parameter_subs[task_id] = [ParameterSubstitution(**s) for s in data]

        # Load execution trace
        trace_path = self._recordings_path / f"{task_id}_trace.json"
        if trace_path.exists() and task_id not in self._execution_traces:
            with open(trace_path) as f:
                data = json.load(f)
                self._execution_traces[task_id] = ExecutionTrace(**data)

