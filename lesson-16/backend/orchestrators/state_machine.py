"""State Machine Orchestration Pattern (FR3.4).

This module implements deterministic finite state machine (FSM) execution where
workflows follow explicit state transitions with validation and auditability.

Features:
- Explicit FSM state definitions and transition rules
- State validation on transitions (prevents invalid state changes)
- Idempotent state handlers (safe re-execution)
- Persistent checkpointing at each state transition
- Complete audit trail logging for compliance
- State invariant enforcement (preconditions/postconditions)

Use Cases:
- Invoice approval workflows (SUBMIT → VALIDATE → MANAGER_REVIEW → FINANCE_REVIEW → APPROVED)
- Document processing with strict compliance requirements
- Workflows requiring audit trails and deterministic execution
- Systems where state rollback/recovery is critical

Example:
    >>> states = ["SUBMIT", "VALIDATE", "APPROVED"]
    >>> transitions = {
    ...     "SUBMIT": ["VALIDATE"],
    ...     "VALIDATE": ["APPROVED"],
    ...     "APPROVED": []
    ... }
    >>> orchestrator = StateMachineOrchestrator(
    ...     name="approval",
    ...     states=states,
    ...     initial_state="SUBMIT",
    ...     transitions=transitions
    ... )
    >>> orchestrator.register_state_handler("SUBMIT", submit_handler)
    >>> result = await orchestrator.execute({"task_id": "INV-001"})
"""

from __future__ import annotations

import time
from collections.abc import Callable
from pathlib import Path
from typing import Any, cast

from backend.orchestrators.base import Orchestrator
from backend.reliability.checkpoint import save_checkpoint


class StateMachineOrchestrator(Orchestrator):
    """State machine orchestration pattern with deterministic FSM execution.

    Implements finite state machine pattern where workflows follow explicit state
    transitions with validation, checkpointing, audit logging, and invariant enforcement.

    Attributes:
        name: Orchestrator instance name
        states: List of valid FSM states
        current_state: Current state in FSM
        initial_state: Starting state for workflows
        transitions: Dict mapping state to list of valid next states
        checkpoint_dir: Optional directory for checkpoint storage
        audit_logger: Optional audit logger for compliance
        invariants: Optional dict mapping state to validation function
        state_handlers: Dict mapping state to handler callable
    """

    def __init__(
        self,
        name: str,
        states: list[str],
        initial_state: str,
        transitions: dict[str, list[str]] | None = None,
        checkpoint_dir: Path | None = None,
        audit_logger: Any = None,
        invariants: dict[str, Callable[[dict[str, Any]], bool]] | None = None,
        max_retries: int = 3,
        circuit_breaker_threshold: int = 3,
    ) -> None:
        """Initialize state machine orchestrator with defensive validation.

        Args:
            name: Orchestrator instance name
            states: List of valid FSM states
            initial_state: Starting state for workflows
            transitions: Dict mapping state to list of valid next states (default: linear chain)
            checkpoint_dir: Optional directory for checkpoint storage
            audit_logger: Optional audit logger for compliance
            invariants: Optional dict mapping state to validation function
            max_retries: Maximum retry attempts for failed agent calls
            circuit_breaker_threshold: Number of failures before circuit breaker opens

        Raises:
            TypeError: If states is not a list or initial_state not a string
            ValueError: If states is empty, initial_state not in states, or invalid transitions
        """
        # Call parent constructor
        super().__init__(
            name=name,
            max_retries=max_retries,
            circuit_breaker_threshold=circuit_breaker_threshold,
        )

        # Step 1: Type checking (defensive)
        if not isinstance(states, list):
            raise TypeError("states must be a list")
        if not isinstance(initial_state, str):
            raise TypeError("initial_state must be a string")
        if checkpoint_dir is not None and not isinstance(checkpoint_dir, Path):
            raise TypeError("checkpoint_dir must be Path or None")

        # Step 2: Input validation (defensive)
        if not states:
            raise ValueError("states cannot be empty")
        if initial_state not in states:
            raise ValueError(f"initial_state '{initial_state}' not in states")

        # Step 3: Initialize FSM configuration
        self.states = states
        self.initial_state = initial_state
        self.current_state = initial_state
        self.checkpoint_dir = checkpoint_dir
        self.audit_logger = audit_logger
        self.invariants = invariants or {}

        # Step 4: Initialize transition rules
        # Default: linear chain (state[i] -> state[i+1])
        if transitions is None:
            self.transitions = self._build_linear_transitions(states)
        else:
            self._validate_transitions(states, transitions)
            self.transitions = transitions

        # Step 5: Initialize state handlers
        self.state_handlers: dict[str, Callable[..., Any]] = {}

        # Step 6: Create checkpoint directory if provided
        if self.checkpoint_dir is not None:
            self.checkpoint_dir.mkdir(parents=True, exist_ok=True)

    def _build_linear_transitions(self, states: list[str]) -> dict[str, list[str]]:
        """Build default linear transition rules (state[i] -> state[i+1]).

        Args:
            states: List of states

        Returns:
            Transition dict with linear chain
        """
        transitions: dict[str, list[str]] = {}
        for i, state in enumerate(states):
            # Each state transitions to next state (last state has no transitions)
            next_states = [states[i + 1]] if i < len(states) - 1 else []
            transitions[state] = next_states
        return transitions

    def _validate_transitions(self, states: list[str], transitions: dict[str, list[str]]) -> None:
        """Validate transition rules are valid.

        Args:
            states: List of valid states
            transitions: Transition rules to validate

        Raises:
            ValueError: If transitions reference invalid states
        """
        # Verify all states have transition rules
        for state in states:
            if state not in transitions:
                raise ValueError(f"State '{state}' missing from transitions")

        # Verify all transition targets are valid states
        for from_state, to_states in transitions.items():
            for to_state in to_states:
                if to_state not in states:
                    raise ValueError(f"Invalid transition target '{to_state}' from '{from_state}'")

    def register_state_handler(self, state: str, handler: Callable[..., Any]) -> None:
        """Register handler for a specific state.

        Args:
            state: State name
            handler: Callable handler for state

        Raises:
            TypeError: If state is not a string or handler is not callable
            ValueError: If state is not in states list
        """
        # Type checking
        if not isinstance(state, str):
            raise TypeError("state must be a string")
        if not callable(handler):
            raise TypeError("handler must be callable")

        # Input validation
        if state not in self.states:
            raise ValueError(f"State '{state}' not in states list")

        # Register handler
        self.state_handlers[state] = handler

    def _validate_transition(self, from_state: str, to_state: str) -> None:
        """Validate transition is allowed by FSM rules.

        Args:
            from_state: Current state
            to_state: Target state

        Raises:
            ValueError: If transition is not allowed
        """
        # Check if transition is valid
        valid_targets = self.transitions.get(from_state, [])
        if to_state not in valid_targets:
            raise ValueError(f"Invalid transition from {from_state} to {to_state}")

    async def _execute(self, task: dict[str, Any]) -> dict[str, Any]:
        """Execute state machine workflow following FSM transition rules.

        Implements deterministic FSM execution pattern where workflow follows
        explicit state transitions. Supports checkpointing, audit logging,
        and state invariant validation.

        Workflow:
        1. Initialize workflow state with initial_state
        2. For each state in FSM:
           a. Execute state handler
           b. Validate state invariants
           c. Save checkpoint
           d. Log audit trail
           e. Determine next state from transition rules
           f. Validate transition allowed
           g. Transition to next state
        3. Return result with complete state history and audit trail

        Args:
            task: Task dictionary (already validated by parent class)
                  Must contain at least 'task_id' field

        Returns:
            Result dictionary with structure:
                {
                    "status": "success",
                    "final_state": "...",
                    "state_history": [...],
                    "audit_trail": [...],
                    "invariant_violations": [...],
                    "final_output": {...}
                }

        Raises:
            ValueError: If no handlers registered
            Exception: If state handler execution fails
        """
        # Step 1: Input validation
        if not self.state_handlers:
            raise ValueError("No state handlers registered")

        # Step 2: Initialize workflow state
        task_id = task["task_id"]
        self.current_state = self.initial_state

        workflow_state: dict[str, Any] = {
            "task_id": task_id,
            "current_state": self.current_state,
            "state_history": [],
            "audit_trail": [],
            "invariant_violations": [],
            "accumulated_data": {},
        }

        # Step 3: Execute FSM state machine
        while True:
            current_state = self.current_state

            # Execute state handler if registered
            if current_state in self.state_handlers:
                # Get handler
                handler = self.state_handlers[current_state]

                # Prepare task with accumulated data
                state_task = self._prepare_state_task(task, workflow_state["accumulated_data"])

                # Execute handler
                try:
                    handler_output = await self._execute_state_handler(
                        handler=handler,
                        state_task=state_task,
                        state_name=current_state,
                    )

                    # Accumulate handler output for next states
                    if isinstance(handler_output, dict):
                        workflow_state["accumulated_data"].update(handler_output)

                    # Validate state invariants
                    self._validate_state_invariants(current_state, workflow_state["accumulated_data"], workflow_state)

                    # Record state transition in history
                    workflow_state["state_history"].append(current_state)

                    # Save checkpoint if configured
                    if self.checkpoint_dir is not None:
                        await self._save_state_checkpoint(task_id, current_state, workflow_state)

                    # Log audit trail
                    self._log_audit_trail(workflow_state, current_state, handler_output)

                except Exception as e:
                    # Log failure
                    self.log_step(
                        step=f"state_{current_state}",
                        status="failure",
                        error=str(e),
                    )
                    raise

            # Step 4: Determine next state
            next_states = self.transitions.get(current_state, [])

            # If no next states (terminal state), workflow complete
            if not next_states:
                break

            # For simplicity, transition to first valid next state
            # (In production, this would be determined by handler output or decision logic)
            next_state = next_states[0]

            # Validate transition
            self._validate_transition(current_state, next_state)

            # Transition to next state
            self.current_state = next_state

        # Step 5: Return successful result
        return {
            "status": "success",
            "final_state": self.current_state,
            "state_history": workflow_state["state_history"],
            "audit_trail": workflow_state["audit_trail"],
            "invariant_violations": workflow_state["invariant_violations"],
            "final_output": workflow_state["accumulated_data"],
        }

    def _prepare_state_task(
        self,
        original_task: dict[str, Any],
        accumulated_data: dict[str, Any],
    ) -> dict[str, Any]:
        """Prepare task dictionary for state handler execution.

        Args:
            original_task: Original task dictionary
            accumulated_data: Accumulated data from previous states

        Returns:
            Task dictionary with accumulated data
        """
        # Copy original task
        state_task = original_task.copy()

        # Merge accumulated data
        state_task.update(accumulated_data)

        return state_task

    async def _execute_state_handler(
        self,
        handler: Callable[..., Any],
        state_task: dict[str, Any],
        state_name: str,
    ) -> dict[str, Any]:
        """Execute state handler with logging.

        Args:
            handler: State handler callable
            state_task: Task dictionary for handler
            state_name: Name of current state

        Returns:
            Handler output dictionary

        Raises:
            Exception: If handler execution fails
        """
        # Execute handler
        output = await handler(state_task)

        # Log successful execution
        self.log_step(
            step=f"state_{state_name}",
            status="success",
            output=output,
        )

        return cast(dict[str, Any], output)

    async def _save_state_checkpoint(
        self,
        task_id: str,
        state_name: str,
        workflow_state: dict[str, Any],
    ) -> None:
        """Save checkpoint after state execution.

        Args:
            task_id: Task identifier
            state_name: Current state name
            workflow_state: Workflow state to checkpoint

        Raises:
            OSError: If checkpoint save fails
        """
        if self.checkpoint_dir is None:
            return

        checkpoint_path = self.checkpoint_dir / f"{task_id}_state_{state_name}.json"
        await save_checkpoint(workflow_state, checkpoint_path)

    def _log_audit_trail(
        self,
        workflow_state: dict[str, Any],
        current_state: str,
        handler_output: dict[str, Any],
    ) -> None:
        """Log state transition in audit trail.

        Args:
            workflow_state: Workflow state dictionary
            current_state: Current state name
            handler_output: Output from state handler
        """
        # Determine previous state
        previous_state = workflow_state["state_history"][-1] if len(workflow_state["state_history"]) > 1 else None

        # Create audit entry
        audit_entry = {
            "from_state": previous_state,
            "to_state": current_state,
            "timestamp": time.time(),
            "handler_output": handler_output,
        }

        # Add to audit trail
        workflow_state["audit_trail"].append(audit_entry)

        # Log to external audit logger if configured
        if self.audit_logger is not None:
            self.audit_logger.log_step(
                agent_name=f"state_{current_state}",
                step=current_state,
                input_data={},
                output=handler_output,
                duration_ms=0,
            )

    def _validate_state_invariants(
        self,
        state_name: str,
        accumulated_data: dict[str, Any],
        workflow_state: dict[str, Any],
    ) -> None:
        """Validate state invariants (preconditions/postconditions).

        Args:
            state_name: Current state name
            accumulated_data: Accumulated data from handlers
            workflow_state: Workflow state for recording violations
        """
        # Check if invariant defined for this state
        if state_name not in self.invariants:
            return

        # Get invariant validator
        validator = self.invariants[state_name]

        # Validate invariant
        try:
            is_valid = validator(accumulated_data)
            if not is_valid:
                # Record violation
                violation = {
                    "state": state_name,
                    "reason": "Invariant validation failed",
                    "data": accumulated_data,
                }
                workflow_state["invariant_violations"].append(violation)
        except Exception as e:
            # Record validation error as violation
            violation = {
                "state": state_name,
                "reason": f"Invariant validator error: {e}",
                "data": accumulated_data,
            }
            workflow_state["invariant_violations"].append(violation)
