"""Abstract base class for orchestration patterns.

This module provides the Orchestrator ABC that defines the common interface
and shared functionality for all orchestration pattern implementations.

The base class provides:
- Agent registration and management
- Result aggregation across multiple agents
- Execution logging and tracing
- Integration hooks for reliability components (retry, circuit breaker)
- Input validation

All subclasses must implement the abstract execute() method.
"""

from __future__ import annotations

import time
from abc import ABC, abstractmethod
from collections.abc import Callable
from typing import Any, cast

from backend.reliability.circuit_breaker import CircuitBreaker
from backend.reliability.retry import retry_with_backoff


class Orchestrator(ABC):
    """Abstract base class for all orchestration pattern implementations.

    Provides common functionality:
    - Agent registration and management
    - Result aggregation
    - Execution logging
    - Retry logic integration
    - Circuit breaker integration
    - Input validation

    Subclasses must implement:
    - execute(): Core orchestration logic
    """

    def __init__(self, name: str, max_retries: int = 3, circuit_breaker_threshold: int = 3) -> None:
        """Initialize orchestrator with defensive validation.

        Args:
            name: Orchestrator instance name
            max_retries: Maximum retry attempts for failed agent calls
            circuit_breaker_threshold: Number of failures before circuit breaker opens (default: 3)

        Raises:
            TypeError: If name is not a string
            ValueError: If name is empty or retries/threshold invalid
        """
        # Step 1: Type checking (defensive)
        if not isinstance(name, str):
            raise TypeError("name must be a string")
        if not isinstance(max_retries, int):
            raise TypeError("max_retries must be an integer")
        if not isinstance(circuit_breaker_threshold, int):
            raise TypeError("circuit_breaker_threshold must be an integer")

        # Step 2: Input validation (defensive)
        if not name.strip():
            raise ValueError("name cannot be empty")
        if max_retries < 1:
            raise ValueError("max_retries must be at least 1")
        if circuit_breaker_threshold < 1:
            raise ValueError("circuit_breaker_threshold must be at least 1")

        # Step 3: Initialize shared attributes
        self.name = name
        self.max_retries = max_retries
        self.agents: dict[str, Callable[..., Any]] = {}
        self.execution_log: list[dict[str, Any]] = []

        # Initialize reliability components
        self.circuit_breaker = CircuitBreaker(
            failure_threshold=circuit_breaker_threshold,
            timeout=2.0,  # 2 seconds before half-open state (test-friendly)
        )

    def register_agent(self, agent_name: str, agent: Callable[..., Any]) -> None:
        """Register a named agent for orchestration.

        Args:
            agent_name: Name to identify the agent
            agent: Callable agent (function or async function)

        Raises:
            TypeError: If agent_name is not a string or agent is not callable
            ValueError: If agent_name is empty or already registered
        """
        # Type checking
        if not isinstance(agent_name, str):
            raise TypeError("agent_name must be a string")
        if not callable(agent):
            raise TypeError("agent must be callable")

        # Input validation
        if not agent_name.strip():
            raise ValueError("agent_name cannot be empty")
        if agent_name in self.agents:
            raise ValueError(f"Agent '{agent_name}' is already registered")

        # Register agent
        self.agents[agent_name] = agent

    def aggregate_results(self, results: list[dict[str, Any]]) -> dict[str, Any]:
        """Aggregate results from multiple agents.

        Args:
            results: List of agent result dictionaries

        Returns:
            Aggregated results with statistics

        Raises:
            TypeError: If results is not a list
            ValueError: If results is empty
        """
        # Type checking
        if not isinstance(results, list):
            raise TypeError("results must be a list")

        # Input validation
        if not results:
            raise ValueError("results cannot be empty")

        # Count successful and failed agents
        successful = sum(1 for r in results if r.get("status") == "success")
        failed = len(results) - successful

        # Aggregate results
        aggregated = {
            "results": results,
            "total_agents": len(results),
            "successful_agents": successful,
            "failed_agents": failed,
            "success_rate": successful / len(results) if results else 0.0,
        }

        return aggregated

    def log_step(self, step: str, status: str, output: Any = None, error: str | None = None) -> None:
        """Log an execution step.

        Args:
            step: Name of the execution step
            status: Status (success, failure, pending)
            output: Optional output data
            error: Optional error message

        Raises:
            TypeError: If step or status is not a string
            ValueError: If step or status is empty
        """
        # Type checking
        if not isinstance(step, str):
            raise TypeError("step must be a string")
        if not isinstance(status, str):
            raise TypeError("status must be a string")

        # Input validation
        if not step.strip():
            raise ValueError("step cannot be empty")
        if not status.strip():
            raise ValueError("status cannot be empty")

        # Create log entry
        log_entry = {
            "step": step,
            "status": status,
            "timestamp": time.time(),
            "output": output,
        }

        if error is not None:
            log_entry["error"] = error

        # Add to execution log
        self.execution_log.append(log_entry)

    async def with_retry(self, agent: Callable[..., Any], task: dict[str, Any]) -> dict[str, Any]:
        """Execute agent with retry logic.

        Integration hook for reliability framework retry component.

        Args:
            agent: Agent callable to execute
            task: Task dictionary to pass to agent

        Returns:
            Agent result dictionary

        Raises:
            Exception: If all retry attempts fail
        """
        # Use retry wrapper from reliability framework
        result = await retry_with_backoff(
            agent,
            task,
            max_retries=self.max_retries,
            initial_delay=1.0,
            max_delay=10.0,
            jitter=True,
        )
        return cast(dict[str, Any], result)

    async def with_circuit_breaker(self, agent: Callable[..., Any], task: dict[str, Any]) -> dict[str, Any]:
        """Execute agent with circuit breaker protection.

        Integration hook for reliability framework circuit breaker component.

        Args:
            agent: Agent callable to execute
            task: Task dictionary to pass to agent

        Returns:
            Agent result dictionary

        Raises:
            RuntimeError: If circuit breaker is OPEN
            Exception: If agent execution fails
        """
        # Use circuit breaker from reliability framework
        async def _agent_call() -> dict[str, Any]:
            result = await agent(task)
            return cast(dict[str, Any], result)

        result = await self.circuit_breaker.call(_agent_call)
        return cast(dict[str, Any], result)

    def _validate_task(self, task: Any) -> None:
        """Validate task input before execution.

        Args:
            task: Task to validate

        Raises:
            TypeError: If task is not a dictionary
            ValueError: If task is missing required fields
        """
        # Type checking
        if not isinstance(task, dict):
            raise TypeError("task must be a dictionary")

        # Input validation
        if "task_id" not in task:
            raise ValueError("task must contain 'task_id'")

    async def execute(self, task: dict[str, Any]) -> dict[str, Any]:
        """Execute orchestration pattern on task. Validates input, then calls _execute().

        This method performs input validation and delegates to _execute() for actual orchestration.
        Subclasses must implement _execute() instead of overriding this method.

        Args:
            task: Task dictionary with at least task_id field

        Returns:
            Result dictionary with status and output

        Raises:
            TypeError: If task is not a dictionary
            ValueError: If task is missing required fields
        """
        # Validate task input (defensive)
        self._validate_task(task)

        # Delegate to subclass implementation
        return await self._execute(task)

    @abstractmethod
    async def _execute(self, task: dict[str, Any]) -> dict[str, Any]:
        """Execute orchestration logic. Subclasses must implement.

        Args:
            task: Validated task dictionary

        Returns:
            Result dictionary with status and output

        Raises:
            NotImplementedError: If subclass doesn't implement
        """
        pass

