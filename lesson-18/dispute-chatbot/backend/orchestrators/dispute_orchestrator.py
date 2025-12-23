"""Dispute Resolution Orchestrator.

Combines the State Machine pattern with specific dispute phases.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Callable, cast

from backend.adapters.redis_store import RedisStore
from backend.orchestrators.dispute_state import DisputeState
from backend.orchestrators.state_machine import StateMachineOrchestrator
from backend.orchestrators.transitions import DISPUTE_TRANSITIONS
from backend.phases.classify import classify_dispute
from backend.phases.gather_evidence import gather_evidence
from backend.phases.monitor import monitor_dispute
from backend.phases.submit import submit_dispute
from backend.phases.validate import validate_evidence
from backend.reliability.retry import retry_with_backoff


class DisputeOrchestrator(StateMachineOrchestrator):
    """Orchestrator for the Merchant Dispute Resolution workflow.

    Manages the lifecycle of a dispute through CLASSIFY -> MONITOR phases.
    """

    def __init__(
        self,
        checkpoint_dir: Path | None = None,
        audit_logger: Any = None,
        redis_url: str | None = None
    ) -> None:
        """Initialize the dispute orchestrator.

        Args:
            checkpoint_dir: Directory to save state checkpoints
            audit_logger: Logger for explainability/compliance
            redis_url: Optional Redis URL for state persistence
        """
        # Initialize state machine with Dispute rules
        super().__init__(
            name="dispute_orchestrator",
            states=[s.value for s in DisputeState],
            initial_state=DisputeState.CLASSIFY.value,
            transitions=DISPUTE_TRANSITIONS,
            checkpoint_dir=checkpoint_dir,
            audit_logger=audit_logger
        )

        # Initialize Redis store
        self.redis_store = RedisStore(redis_url)

        # Register handlers for each phase
        self.register_state_handler(DisputeState.CLASSIFY.value, classify_dispute)
        self.register_state_handler(DisputeState.GATHER_EVIDENCE.value, gather_evidence)
        self.register_state_handler(DisputeState.VALIDATE.value, validate_evidence)
        self.register_state_handler(DisputeState.SUBMIT.value, submit_dispute)
        self.register_state_handler(DisputeState.MONITOR.value, monitor_dispute)

    def resolve_transition(self, current_state: str, context: dict[str, Any]) -> str:
        """Resolve next state transition dynamically based on phase outcomes.

        Args:
            current_state: Current state name
            context: Execution context (accumulated data)

        Returns:
            Next state name
        """
        # Validation Logic: If validation fails, escalate
        if current_state == DisputeState.VALIDATE.value:
            if context.get("validation_passed", False):
                return DisputeState.SUBMIT.value
            return DisputeState.ESCALATE.value

        # Submission Logic: If submission fails, escalate
        if current_state == DisputeState.SUBMIT.value:
            if context.get("submission_status") == "success":
                return DisputeState.MONITOR.value
            return DisputeState.ESCALATE.value

        # Default behavior (linear flow)
        return super().resolve_transition(current_state, context)

    async def _save_state_checkpoint(
        self,
        task_id: str,
        state_name: str,
        workflow_state: dict[str, Any],
    ) -> None:
        """Save checkpoint to Redis.

        Args:
            task_id: Task identifier
            state_name: Current state name
            workflow_state: Workflow state to checkpoint
        """
        # Save to Redis
        await self.redis_store.save_state(task_id, workflow_state)

        # Also save to file if configured (legacy/backup)
        if self.checkpoint_dir:
            await super()._save_state_checkpoint(task_id, state_name, workflow_state)

    async def load_state(self, task_id: str) -> dict[str, Any] | None:
        """Load workflow state from Redis or filesystem.

        Args:
            task_id: Task identifier

        Returns:
            State dictionary or None if not found
        """
        # Try Redis first
        state = await self.redis_store.load_state(task_id)
        if state:
            return state

        # Fallback to filesystem if configured
        if self.checkpoint_dir:
            return await super().load_state(task_id)

        return None

    async def _execute_state_handler(
        self,
        handler: Callable[..., Any],
        state_task: dict[str, Any],
        state_name: str,
    ) -> dict[str, Any]:
        """Execute state handler with retry logic for network-bound phases.

        Args:
            handler: State handler callable
            state_task: Task dictionary for handler
            state_name: Name of current state

        Returns:
            Handler output dictionary
        """
        # Configure retries for specific phases
        phases_to_retry = {
            DisputeState.CLASSIFY.value,
            DisputeState.GATHER_EVIDENCE.value,
            DisputeState.SUBMIT.value
        }

        if state_name in phases_to_retry:
            output = await retry_with_backoff(
                handler,
                state_task,
                max_retries=3,
                base_delay=1.0,
                exponential_base=2.0
            )
        else:
            output = await handler(state_task)

        # Log successful execution
        self.log_step(
            step=f"state_{state_name}",
            status="success",
            output=output,
        )

        return cast(dict[str, Any], output)

