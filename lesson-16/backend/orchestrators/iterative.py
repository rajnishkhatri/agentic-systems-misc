"""Iterative Refinement Orchestration Pattern (FR3.3 - ReAct/Reflexion).

This module implements an action-reflection-refinement loop where an agent
iteratively improves its output based on reflection feedback.

Features:
- Action-reflection-refinement loop (ReAct/Reflexion pattern)
- Max iteration limits (configurable 3-5 iterations)
- Progress validation between iterations
- Convergence detection (stops when criteria met)
- Reflection context passing to subsequent iterations
- Complete iteration history tracking

Use Cases:
- Account reconciliation: iteratively resolve date mismatches and rounding errors
- Document refinement: improve quality through reflection
- Problem solving: refine solutions based on feedback

Pattern:
    For each iteration (up to max_iterations):
        1. ACTION: Execute agent on task
        2. REFLECTION: Agent analyzes output and generates reflection
        3. REFINEMENT: Pass reflection to next iteration as context
        4. CONVERGENCE CHECK: Stop if criteria met (e.g., discrepancy < threshold)

Example:
    >>> orchestrator = IterativeOrchestrator(
    ...     name="account_reconciliation",
    ...     max_iterations=5,
    ...     convergence_threshold=0.01
    ... )
    >>> orchestrator.register_agent("reconciliation_agent", agent)
    >>> result = await orchestrator.execute({"task_id": "REC-001"})
    >>> print(f"Converged: {result['converged']}, Iterations: {len(result['iterations'])}")
"""

from __future__ import annotations

from typing import Any

from backend.orchestrators.base import Orchestrator


class IterativeOrchestrator(Orchestrator):
    """Iterative refinement orchestration pattern using ReAct/Reflexion loop.

    Executes an agent repeatedly, passing reflection feedback to improve results.
    Stops when convergence criteria met or max iterations reached.

    Attributes:
        name: Orchestrator instance name
        max_iterations: Maximum number of refinement iterations (default: 3)
        convergence_threshold: Convergence threshold for discrepancy (default: 1.0)
    """

    def __init__(
        self,
        name: str,
        max_iterations: int = 3,
        convergence_threshold: float = 1.0,
        max_retries: int = 3,
        circuit_breaker_threshold: int = 3,
    ) -> None:
        """Initialize iterative orchestrator.

        Args:
            name: Orchestrator instance name
            max_iterations: Maximum number of refinement iterations (3-5 recommended)
            convergence_threshold: Threshold for convergence detection (default: 1.0)
            max_retries: Maximum retry attempts for failed agent calls
            circuit_breaker_threshold: Number of failures before circuit breaker opens

        Raises:
            TypeError: If max_iterations is not int or threshold is not float
            ValueError: If max_iterations < 1 or threshold < 0
        """
        # Call parent constructor
        super().__init__(
            name=name,
            max_retries=max_retries,
            circuit_breaker_threshold=circuit_breaker_threshold,
        )

        # Type checking (defensive)
        if not isinstance(max_iterations, int):
            raise TypeError("max_iterations must be an integer")
        if not isinstance(convergence_threshold, int | float):
            raise TypeError("convergence_threshold must be a number")

        # Input validation (defensive)
        if max_iterations < 1:
            raise ValueError("max_iterations must be at least 1")
        if convergence_threshold < 0:
            raise ValueError("convergence_threshold must be non-negative")

        # Store configuration
        self.max_iterations = max_iterations
        self.convergence_threshold = convergence_threshold
        self.iteration_history: list[dict[str, Any]] = []

    async def _execute(self, task: dict[str, Any]) -> dict[str, Any]:
        """Execute iterative refinement loop with action-reflection-refinement.

        Implements ReAct/Reflexion pattern:
        1. ACTION: Execute agent on task
        2. REFLECTION: Agent generates reflection on output
        3. REFINEMENT: Pass reflection to next iteration
        4. CONVERGENCE CHECK: Stop if criteria met

        Workflow:
        1. Validate agent registered
        2. Initialize iteration tracking
        3. For each iteration (up to max_iterations):
           a. Prepare task with reflection context
           b. Execute agent (ACTION)
           c. Extract reflection (REFLECTION)
           d. Check convergence (early stop if converged)
           e. Track iteration history
           f. Pass reflection to next iteration (REFINEMENT)
        4. Return result with convergence status

        Args:
            task: Task dictionary (already validated by parent class)

        Returns:
            Result dictionary with structure:
                {
                    "status": "success",
                    "converged": True | False,
                    "iterations": [...],  # List of iteration results
                    "final_discrepancy": float,
                    "resolution_status": str,  # From last iteration
                    "total_iterations": int
                }

        Raises:
            ValueError: If no agents registered
            Exception: If agent execution fails
        """
        # Step 1: Input validation (defensive)
        if not self.agents:
            raise ValueError("No agents registered")

        # Get the refinement agent (typically named "reconciliation_agent", "refinement_agent", etc.)
        # For flexibility, use the first registered agent
        agent_name = list(self.agents.keys())[0]
        agent = self.agents[agent_name]

        # Step 2: Initialize iteration tracking
        self.iteration_history = []
        previous_reflection: str | None = None
        converged = False
        final_discrepancy = float("inf")
        resolution_status = "not_started"

        # Step 3: Execute refinement loop
        for iteration_num in range(1, self.max_iterations + 1):
            # Prepare task for agent (include reflection context)
            agent_task = self._prepare_iteration_task(task, previous_reflection, iteration_num)

            # Execute agent (ACTION phase)
            try:
                output = await agent(agent_task)
            except Exception as e:
                # Log failure and re-raise
                self.log_step(
                    step=f"iteration_{iteration_num}",
                    status="failure",
                    error=str(e),
                )
                raise

            # Log successful iteration
            self.log_step(
                step=f"iteration_{iteration_num}",
                status="success",
                output=output,
            )

            # Track iteration history
            iteration_result = {
                "iteration": iteration_num,
                **output,  # Include all agent output fields
            }
            self.iteration_history.append(iteration_result)

            # Extract reflection for next iteration (REFLECTION phase)
            previous_reflection = output.get("reflection", "")

            # Extract discrepancy and status for convergence check
            final_discrepancy = output.get("discrepancy_amount", float("inf"))
            resolution_status = output.get("resolution_status", "in_progress")

            # Check convergence (CONVERGENCE CHECK)
            if self._check_convergence(output):
                converged = True
                break  # Early stop - convergence achieved

        # Step 4: Return result with convergence status
        return {
            "status": "success",
            "converged": converged,
            "iterations": self.iteration_history,
            "final_discrepancy": final_discrepancy,
            "resolution_status": resolution_status,
            "total_iterations": len(self.iteration_history),
        }

    def _prepare_iteration_task(
        self,
        original_task: dict[str, Any],
        previous_reflection: str | None,
        iteration_num: int,
    ) -> dict[str, Any]:
        """Prepare task dictionary for iteration with reflection context.

        Args:
            original_task: Original task dictionary
            previous_reflection: Reflection from previous iteration (or None for first)
            iteration_num: Current iteration number

        Returns:
            Task dictionary with reflection context
        """
        # Copy original task to avoid mutation
        agent_task = original_task.copy()

        # Add iteration context
        agent_task["iteration"] = iteration_num

        # Add previous reflection if available (REFINEMENT - pass context to next iteration)
        if previous_reflection is not None:
            agent_task["previous_reflection"] = previous_reflection

        return agent_task

    def _check_convergence(self, output: dict[str, Any]) -> bool:
        """Check if output meets convergence criteria.

        Convergence is achieved when discrepancy_amount < convergence_threshold.

        Args:
            output: Agent output dictionary

        Returns:
            True if converged, False otherwise
        """
        # Check for discrepancy_amount field
        if "discrepancy_amount" not in output:
            return False

        # Get discrepancy value
        discrepancy = output["discrepancy_amount"]

        # Type check
        if not isinstance(discrepancy, int | float):
            return False

        # Check convergence threshold
        return discrepancy < self.convergence_threshold
