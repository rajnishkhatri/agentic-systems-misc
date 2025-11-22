"""Error isolation for agent reliability (FR4.5).

This module implements the Result[T, E] type pattern for preventing agent failures
from crashing the orchestrator. It provides:

- Result type with Success and Failure variants
- safe_agent_call wrapper that catches exceptions
- Critical vs optional agent distinction support

Key Features:
- Type-safe error handling with generic Result[T, E]
- Exception isolation prevents cascade failures
- Orchestrator can continue even if agents fail
- Supports critical vs optional agent workflows

Example:
    >>> result = await safe_agent_call(agent, agent_name="validator", input_data={})
    >>> if result.is_success():
    ...     data = result.unwrap()
    ... else:
    ...     print(f"Agent failed: {result.error}")
"""

from __future__ import annotations

from typing import Any, Generic, TypeVar

T = TypeVar("T")
E = TypeVar("E", bound=Exception)


class Result(Generic[T, E]):
    """Result type representing either Success or Failure.

    This is a Rust-inspired Result type that prevents exceptions from propagating
    and allows orchestrators to handle agent failures gracefully.

    Attributes:
        value: The success value (None if failure)
        error: The error (None if success)

    Example:
        >>> success = Result.success({"data": "extracted"})
        >>> success.unwrap()  # Returns {"data": "extracted"}
        >>>
        >>> failure = Result.failure(ValueError("Parse error"))
        >>> failure.is_failure()  # Returns True
    """

    def __init__(self, value: T | None = None, error: E | None = None) -> None:
        """Initialize Result with either value or error.

        Args:
            value: Success value (mutually exclusive with error)
            error: Error instance (mutually exclusive with value)

        Raises:
            ValueError: If both value and error are provided or neither is provided
        """
        if (value is None and error is None) or (value is not None and error is not None):
            raise ValueError("Result must have exactly one of value or error")

        self.value = value
        self.error = error

    @classmethod
    def success(cls, value: T) -> Result[T, E]:
        """Create a Success result.

        Args:
            value: The success value

        Returns:
            Result instance representing success
        """
        return cls(value=value, error=None)

    @classmethod
    def failure(cls, error: E) -> Result[T, E]:
        """Create a Failure result.

        Args:
            error: The error instance

        Returns:
            Result instance representing failure
        """
        return cls(value=None, error=error)

    def is_success(self) -> bool:
        """Check if result is success.

        Returns:
            True if success, False if failure
        """
        return self.error is None

    def is_failure(self) -> bool:
        """Check if result is failure.

        Returns:
            True if failure, False if success
        """
        return self.error is not None

    def unwrap(self) -> T:
        """Unwrap success value or raise if failure.

        Returns:
            The success value

        Raises:
            ValueError: If result is a Failure
        """
        if self.is_failure():
            raise ValueError(f"Cannot unwrap Failure: {self.error}")
        return self.value  # type: ignore

    def unwrap_or(self, default: T) -> T:
        """Unwrap success value or return default if failure.

        Args:
            default: Default value to return if failure

        Returns:
            Success value if success, default if failure
        """
        if self.is_success():
            return self.value  # type: ignore
        return default


async def safe_agent_call(
    agent: Any,
    agent_name: str,
    input_data: dict[str, Any],
    **kwargs: Any,
) -> Result[Any, Exception]:
    """Call agent with exception isolation.

    Wraps agent calls to prevent exceptions from propagating to the orchestrator.
    Returns a Result type that can be inspected safely.

    Args:
        agent: Async callable agent function
        agent_name: Name of the agent (for logging/debugging)
        input_data: Input data to pass to agent
        **kwargs: Additional keyword arguments to pass to agent

    Returns:
        Result[Any, Exception]: Success with agent output or Failure with exception

    Example:
        >>> result = await safe_agent_call(validator_agent, "validator", {"invoice": data})
        >>> if result.is_success():
        ...     validated_data = result.unwrap()
        ... else:
        ...     logger.error(f"Validator failed: {result.error}")
    """
    # Step 1: Type checking (defensive)
    if not isinstance(agent_name, str):
        raise TypeError("agent_name must be a string")
    if not isinstance(input_data, dict):
        raise TypeError("input_data must be a dict")

    # Step 2: Try to call agent with exception isolation
    try:
        output = await agent(input_data, **kwargs)
        return Result.success(output)
    except Exception as e:
        # Isolate the exception - don't let it propagate
        return Result.failure(e)
