"""Sequential Orchestration Pattern (FR3.1).

This module implements linear chain execution where agents execute one after another.
Each step's output becomes input for the next step.

Features:
- Linear chain execution (agent1 → agent2 → agent3)
- Checkpointing after each step for recovery
- Early termination on validation failures
- State passing between steps
- Execution logging and tracing

Use Cases:
- Invoice processing: extract → validate → route for approval
- Document workflows with dependent steps
- Workflows requiring audit trails

Example:
    >>> orchestrator = SequentialOrchestrator(name="invoice_workflow")
    >>> orchestrator.register_agent("extractor", extract_agent)
    >>> orchestrator.register_agent("validator", validate_agent)
    >>> orchestrator.register_agent("router", routing_agent)
    >>> result = await orchestrator.execute({"task_id": "INV-001"})
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from backend.orchestrators.base import Orchestrator
from backend.reliability.checkpoint import save_checkpoint


class SequentialOrchestrator(Orchestrator):
    """Sequential orchestration pattern executing agents in linear chain.

    Inherits from Orchestrator ABC and implements sequential execution logic.
    Each agent's output is passed to the next agent in the registered order.

    Attributes:
        name: Orchestrator instance name
        checkpoint_dir: Optional directory for saving checkpoints
        validate_steps: Whether to validate outputs and enable early termination
    """

    def __init__(
        self,
        name: str,
        checkpoint_dir: Path | None = None,
        validate_steps: bool = False,
        max_retries: int = 3,
        circuit_breaker_threshold: int = 3,
    ) -> None:
        """Initialize sequential orchestrator.

        Args:
            name: Orchestrator instance name
            checkpoint_dir: Optional directory for checkpoint storage
            validate_steps: Whether to validate outputs between steps
            max_retries: Maximum retry attempts for failed agent calls
            circuit_breaker_threshold: Number of failures before circuit breaker opens

        Raises:
            TypeError: If checkpoint_dir is not Path or None
            ValueError: If name is empty
        """
        # Call parent constructor
        super().__init__(
            name=name,
            max_retries=max_retries,
            circuit_breaker_threshold=circuit_breaker_threshold,
        )

        # Type checking
        if checkpoint_dir is not None and not isinstance(checkpoint_dir, Path):
            raise TypeError("checkpoint_dir must be Path or None")

        # Store configuration
        self.checkpoint_dir = checkpoint_dir
        self.validate_steps = validate_steps
        self.current_step = 0

        # Create checkpoint directory if provided
        if self.checkpoint_dir is not None:
            self.checkpoint_dir.mkdir(parents=True, exist_ok=True)

    async def _execute(self, task: dict[str, Any]) -> dict[str, Any]:
        """Execute agents sequentially in registered order.

        Implements linear chain execution pattern where each agent's output
        becomes input for the next agent. Supports checkpointing, early termination
        on validation failures, and comprehensive execution logging.

        Workflow:
        1. Validate agents are registered
        2. Initialize workflow state
        3. For each agent in order:
           a. Prepare task with previous output
           b. Execute agent
           c. Log execution step
           d. Save checkpoint (if configured)
           e. Check validation (early termination if failed)
           f. Pass output to next agent
        4. Return aggregated result

        Args:
            task: Task dictionary (already validated by parent class)
                  Must contain at least 'task_id' field

        Returns:
            Result dictionary with structure:
                {
                    "status": "success" | "validation_failed",
                    "steps": [...],  # List of step results
                    "final_output": {...},  # Last agent's output
                    "error": "...",  # Optional error message
                    "validation_errors": [...]  # Optional validation errors
                }

        Raises:
            ValueError: If no agents registered
            Exception: If any agent execution fails (propagates from agent)
        """
        # Step 1: Input validation (defensive)
        if not self.agents:
            raise ValueError("No agents registered")

        # Step 2: Initialize workflow state
        task_id = task["task_id"]  # Already validated by parent
        workflow_state: dict[str, Any] = {
            "task_id": task_id,
            "current_step": 0,
            "steps_completed": [],
            "steps": [],
        }

        # Step 3: Execute agents in registration order
        agent_names = list(self.agents.keys())
        previous_output: dict[str, Any] | None = None

        for step_index, agent_name in enumerate(agent_names):
            self.current_step = step_index

            # Get agent callable
            agent = self.agents[agent_name]

            # Prepare task for agent (include context from previous steps)
            agent_task = self._prepare_agent_task(task, previous_output)

            # Execute agent with error handling
            try:
                output = await self._execute_agent_step(
                    agent=agent,
                    agent_task=agent_task,
                    agent_name=agent_name,
                    step_index=step_index,
                )

                # Store step result
                step_result = {
                    "step": step_index,
                    "agent": agent_name,
                    "status": "success",
                    "output": output,
                }
                workflow_state["steps"].append(step_result)
                workflow_state["steps_completed"].append(agent_name)
                workflow_state["current_step"] = step_index + 1

                # Save checkpoint if configured (for recovery)
                if self.checkpoint_dir is not None:
                    await self._save_step_checkpoint(task_id, step_index, workflow_state)

                # Check for validation failure (early termination)
                validation_result = self._check_validation(output)
                if validation_result is not None:
                    # Early termination - validation failed
                    return {
                        "status": "validation_failed",
                        "error": validation_result["error"],
                        "validation_errors": validation_result["validation_errors"],
                        "steps": workflow_state["steps"],
                        "final_output": output,
                    }

                # Update previous output for next step
                previous_output = output

            except Exception as e:
                # Log failure step
                self.log_step(
                    step=f"{agent_name}_{step_index}",
                    status="failure",
                    error=str(e),
                )

                # Re-raise exception (let caller handle recovery)
                raise

        # Step 4: Return successful result
        return {
            "status": "success",
            "steps": workflow_state["steps"],
            "final_output": previous_output if previous_output is not None else {},
        }

    def _prepare_agent_task(
        self,
        original_task: dict[str, Any],
        previous_output: dict[str, Any] | None,
    ) -> dict[str, Any]:
        """Prepare task dictionary for agent execution.

        Combines original task with previous agent's output to provide context.

        Args:
            original_task: Original task dictionary
            previous_output: Previous agent's output (or None for first agent)

        Returns:
            Task dictionary with previous output included
        """
        # Copy original task to avoid mutation
        agent_task = original_task.copy()

        # Add previous output if available
        if previous_output is not None:
            agent_task["previous_output"] = previous_output

            # Also merge dict outputs to top level for backwards compatibility
            if isinstance(previous_output, dict):
                # Add extracted_data key if previous output looks like extraction
                if any(k in previous_output for k in ["vendor_name", "invoice_number", "total_amount"]):
                    agent_task["extracted_data"] = previous_output
                else:
                    agent_task.update(previous_output)

        return agent_task

    async def _execute_agent_step(
        self,
        agent: Any,
        agent_task: dict[str, Any],
        agent_name: str,
        step_index: int,
    ) -> dict[str, Any]:
        """Execute a single agent step with logging.

        Args:
            agent: Agent callable to execute
            agent_task: Task dictionary to pass to agent
            agent_name: Name of the agent
            step_index: Step index in workflow

        Returns:
            Agent output dictionary

        Raises:
            Exception: If agent execution fails
        """
        # Execute agent
        output = await agent(agent_task)

        # Log successful step
        self.log_step(
            step=f"{agent_name}_{step_index}",
            status="success",
            output=output,
        )

        return output

    async def _save_step_checkpoint(
        self,
        task_id: str,
        step_index: int,
        workflow_state: dict[str, Any],
    ) -> None:
        """Save checkpoint after step completion.

        Args:
            task_id: Task identifier
            step_index: Current step index
            workflow_state: Workflow state to checkpoint

        Raises:
            OSError: If checkpoint save fails
        """
        if self.checkpoint_dir is None:
            return

        checkpoint_path = self.checkpoint_dir / f"{task_id}_step_{step_index}.json"
        await save_checkpoint(workflow_state, checkpoint_path)

    def _check_validation(self, output: Any) -> dict[str, Any] | None:
        """Check if output indicates validation failure.

        Args:
            output: Agent output to check

        Returns:
            Validation error dict if validation failed, None otherwise
        """
        # Skip validation check if not enabled
        if not self.validate_steps:
            return None

        # Only check dict outputs
        if not isinstance(output, dict):
            return None

        # Check for validation failure flag
        if output.get("is_valid") is False:
            return {
                "error": "Validation failed",
                "validation_errors": output.get("validation_errors", []),
            }

        return None
