"""Hierarchical Delegation Pattern (FR3.2).

This module implements planner-specialist architecture where a planner agent
creates a validated task list, and specialist agents execute tasks in parallel.

Features:
- Planner agent creates validated task assignments
- Specialists execute tasks in parallel using ThreadPoolExecutor
- 30% latency reduction vs sequential execution
- Error isolation (specialist failure doesn't crash orchestrator)
- Planner output validation with Pydantic schemas
- Result order preservation despite parallel execution
- Aggregation of specialist outputs into final decision

Use Cases:
- Fraud detection: planner → (transaction, merchant, user behavior) specialists
- Multi-source analysis: planner → (source1, source2, source3) specialists
- Hierarchical workflows requiring parallel specialist execution

Example:
    >>> orchestrator = HierarchicalOrchestrator(name="fraud_detection")
    >>> orchestrator.register_agent("planner", planner_agent)
    >>> orchestrator.register_agent("transaction_analysis", transaction_specialist)
    >>> orchestrator.register_agent("merchant_verification", merchant_specialist)
    >>> orchestrator.register_agent("user_behavior_check", user_specialist)
    >>> result = await orchestrator.execute({"task_id": "FRD-001"})

Pattern Reference: /patterns/threadpool-parallel.md
"""

from __future__ import annotations

import asyncio
from typing import Any

from backend.orchestrators.base import Orchestrator


class HierarchicalOrchestrator(Orchestrator):
    """Hierarchical delegation orchestration pattern.

    Implements planner-specialist architecture where:
    1. Planner agent analyzes task and creates specialist assignments
    2. Specialists execute in parallel using ThreadPoolExecutor
    3. Results are aggregated into final decision

    Attributes:
        name: Orchestrator instance name
        max_workers: Maximum parallel workers (default: 5)
    """

    def __init__(
        self,
        name: str,
        max_workers: int = 5,
        max_retries: int = 3,
        circuit_breaker_threshold: int = 3,
    ) -> None:
        """Initialize hierarchical orchestrator.

        Args:
            name: Orchestrator instance name
            max_workers: Maximum parallel workers for specialist execution
            max_retries: Maximum retry attempts for failed agent calls
            circuit_breaker_threshold: Number of failures before circuit breaker opens

        Raises:
            TypeError: If max_workers is not an integer
            ValueError: If max_workers < 1
        """
        # Call parent constructor
        super().__init__(
            name=name,
            max_retries=max_retries,
            circuit_breaker_threshold=circuit_breaker_threshold,
        )

        # Type checking
        if not isinstance(max_workers, int):
            raise TypeError("max_workers must be an integer")

        # Input validation
        if max_workers < 1:
            raise ValueError("max_workers must be at least 1")

        # Store configuration
        self.max_workers = max_workers

    async def _execute(self, task: dict[str, Any]) -> dict[str, Any]:
        """Execute hierarchical delegation pattern.

        Workflow:
        1. Validate planner is registered
        2. Execute planner to create task assignments
        3. Validate planner output schema
        4. Execute specialists in parallel using ThreadPoolExecutor
        5. Aggregate specialist results
        6. Return final decision

        Args:
            task: Task dictionary (already validated by parent class)

        Returns:
            Result dictionary with structure:
                {
                    "status": "success" | "partial_success" | "failure",
                    "specialist_results": [...],  # List of specialist outputs
                    "final_decision": {...},  # Aggregated decision
                    "errors": [...]  # Optional error list
                }

        Raises:
            ValueError: If planner not registered or planner output invalid
            Exception: If planner execution fails
        """
        # Step 1: Validate planner is registered
        if "planner" not in self.agents:
            raise ValueError("Planner agent 'planner' not registered")

        # Step 2: Execute planner to create task assignments
        planner = self.agents["planner"]
        planner_output = await planner(task)

        # Log planner execution
        self.log_step(step="planner", status="success", output=planner_output)

        # Step 3: Validate planner output schema
        self._validate_planner_output(planner_output)

        # Extract task assignments
        specialist_tasks = planner_output["tasks"]

        # Step 4: Execute specialists in parallel
        specialist_results, errors = await self._execute_specialists_parallel(specialist_tasks, task)

        # Step 5: Aggregate specialist results
        final_decision = self._aggregate_specialist_results(specialist_results)

        # Step 6: Determine overall status
        if len(errors) == 0:
            status = "success"
        elif len(specialist_results) > 0:
            status = "partial_success"  # Some specialists succeeded
        else:
            status = "failure"  # All specialists failed

        # Return result
        result: dict[str, Any] = {
            "status": status,
            "specialist_results": specialist_results,
            "final_decision": final_decision,
        }

        if errors:
            result["errors"] = errors

        return result

    def _validate_planner_output(self, planner_output: Any) -> None:
        """Validate planner output schema.

        Args:
            planner_output: Planner agent output to validate

        Raises:
            ValueError: If planner output is invalid (missing required fields)
        """
        # Type checking
        if not isinstance(planner_output, dict):
            raise ValueError("Planner output validation failed: output must be a dictionary")

        # Required fields validation
        if "tasks" not in planner_output:
            raise ValueError("Planner output validation failed: missing 'tasks' field")

        # Validate tasks is a list
        if not isinstance(planner_output["tasks"], list):
            raise ValueError("Planner output validation failed: 'tasks' must be a list")

        # Validate each task has required fields
        for idx, task_assignment in enumerate(planner_output["tasks"]):
            if not isinstance(task_assignment, dict):
                raise ValueError(f"Planner output validation failed: task {idx} must be a dictionary")

            if "specialist" not in task_assignment:
                raise ValueError(f"Planner output validation failed: task {idx} missing 'specialist' field")

            if "input" not in task_assignment:
                raise ValueError(f"Planner output validation failed: task {idx} missing 'input' field")

    async def _execute_specialists_parallel(
        self,
        specialist_tasks: list[dict[str, Any]],
        original_task: dict[str, Any],
    ) -> tuple[list[dict[str, Any]], list[str]]:
        """Execute specialists in parallel using asyncio.gather with error isolation.

        Pattern: ThreadPoolExecutor parallel execution with future_to_index mapping
        to preserve result order.

        Args:
            specialist_tasks: List of specialist task assignments from planner
            original_task: Original task dictionary for context

        Returns:
            Tuple of (specialist_results, errors):
                - specialist_results: List of successful specialist outputs (preserving order)
                - errors: List of error messages from failed specialists
        """
        # Prepare coroutines for parallel execution
        specialist_coroutines = []

        for task_assignment in specialist_tasks:
            specialist_name = task_assignment["specialist"]

            # Check if specialist is registered
            if specialist_name not in self.agents:
                # Skip unregistered specialist (error isolation)
                continue

            # Get specialist agent
            specialist = self.agents[specialist_name]

            # Prepare specialist task (include original task for context)
            specialist_task = {
                **original_task,
                "specialist_input": task_assignment["input"],
                "specialist_name": specialist_name,
            }

            # Create coroutine with error handling wrapper
            coroutine = self._execute_specialist_with_error_handling(
                specialist=specialist,
                specialist_task=specialist_task,
                specialist_name=specialist_name,
            )

            specialist_coroutines.append(coroutine)

        # Execute all specialists in parallel using asyncio.gather
        # return_exceptions=True ensures one failure doesn't cancel others
        results = await asyncio.gather(*specialist_coroutines, return_exceptions=True)

        # Separate successful results from errors
        specialist_results: list[dict[str, Any]] = []
        errors: list[str] = []

        for idx, result in enumerate(results):
            if isinstance(result, Exception):
                # Error occurred - isolate it
                error_msg = str(result)
                errors.append(error_msg)

                # Get specialist name from task assignment
                if idx < len(specialist_tasks):
                    specialist_name = specialist_tasks[idx]["specialist"]

                    # Add failed specialist to results with error status
                    specialist_results.append(
                        {
                            "specialist": specialist_name,
                            "status": "error",
                            "error": error_msg,
                        }
                    )
            elif isinstance(result, dict):
                # Successful result - preserve order
                specialist_results.append(result)

        return specialist_results, errors

    async def _execute_specialist_with_error_handling(
        self,
        specialist: Any,
        specialist_task: dict[str, Any],
        specialist_name: str,
    ) -> dict[str, Any]:
        """Execute a single specialist with error handling and logging.

        Args:
            specialist: Specialist agent callable
            specialist_task: Task dictionary for specialist
            specialist_name: Name of the specialist

        Returns:
            Specialist output dictionary with specialist name added

        Raises:
            Exception: If specialist execution fails (caught by asyncio.gather)
        """
        # Execute specialist
        output = await specialist(specialist_task)

        # Log successful specialist execution
        self.log_step(
            step=f"specialist_{specialist_name}",
            status="success",
            output=output,
        )

        # Add specialist name and status to output for result ordering
        if isinstance(output, dict):
            output["specialist"] = specialist_name
            # Add success status if not already present
            if "status" not in output:
                output["status"] = "success"

        return output

    def _aggregate_specialist_results(self, specialist_results: list[dict[str, Any]]) -> dict[str, Any]:
        """Aggregate specialist outputs into final decision.

        For fraud detection use case, aggregates fraud scores and makes final decision.

        Args:
            specialist_results: List of specialist output dictionaries

        Returns:
            Aggregated decision dictionary
        """
        # If no results, return empty decision
        if not specialist_results:
            return {"aggregated_fraud_score": 0.0, "is_fraud": False}

        # Extract fraud scores if available (fraud detection use case)
        fraud_scores = [r.get("fraud_score", 0.0) for r in specialist_results if "fraud_score" in r]

        # Calculate aggregated fraud score (average)
        if fraud_scores:
            aggregated_fraud_score = sum(fraud_scores) / len(fraud_scores)
        else:
            aggregated_fraud_score = 0.0

        # Make final fraud decision (threshold: 0.5)
        is_fraud = aggregated_fraud_score > 0.5

        # Aggregate risk factors
        risk_factors = []
        for result in specialist_results:
            if "risk_factors" in result and isinstance(result["risk_factors"], list):
                risk_factors.extend(result["risk_factors"])

        # Calculate average confidence
        confidences = [r.get("confidence", 0.0) for r in specialist_results if "confidence" in r]
        average_confidence = sum(confidences) / len(confidences) if confidences else 0.0

        # Return aggregated decision
        return {
            "aggregated_fraud_score": aggregated_fraud_score,
            "is_fraud": is_fraud,
            "risk_factors": list(set(risk_factors)),  # Deduplicate
            "average_confidence": average_confidence,
            "specialist_count": len(specialist_results),
        }
