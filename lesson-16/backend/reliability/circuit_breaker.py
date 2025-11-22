"""Circuit Breaker Pattern for Agent Reliability (FR4.2).

This module implements the Circuit Breaker pattern to prevent cascading failures
by stopping calls to failing services and allowing them time to recover.

State Machine:
    CLOSED: Normal operation, all calls pass through
    OPEN: Service failing, reject all calls immediately
    HALF_OPEN: Testing recovery, allow one call to test service

Transitions:
    CLOSED → OPEN: After failure_threshold consecutive failures
    OPEN → HALF_OPEN: After timeout period expires
    HALF_OPEN → CLOSED: If test call succeeds
    HALF_OPEN → OPEN: If test call fails

Usage:
    circuit_breaker = CircuitBreaker(failure_threshold=5, timeout=60.0)
    result = await circuit_breaker.call(agent_function)
"""

from __future__ import annotations

import time
from collections.abc import Awaitable, Callable
from typing import Any, Literal


class CircuitBreakerOpenError(Exception):
    """Raised when circuit breaker rejects a call in OPEN state."""

    pass


class CircuitBreaker:
    """Circuit breaker to prevent cascading failures.

    Implements a state machine (CLOSED → OPEN → HALF_OPEN) to protect
    against repeated calls to failing services.

    Attributes:
        failure_threshold: Number of consecutive failures before opening
        timeout: Seconds to wait before attempting recovery (HALF_OPEN)
        fallback: Optional function to call when circuit is OPEN
        state: Current state (CLOSED, OPEN, HALF_OPEN)
        failure_count: Number of consecutive failures
        last_failure_time: Timestamp of last failure
    """

    def __init__(
        self,
        failure_threshold: int,
        timeout: float,
        fallback: Callable[[], Any] | None = None,
    ) -> None:
        """Initialize circuit breaker.

        Args:
            failure_threshold: Number of failures before opening circuit
            timeout: Seconds to wait in OPEN state before trying HALF_OPEN
            fallback: Optional function returning fallback value when OPEN

        Raises:
            TypeError: If parameters are wrong type
            ValueError: If parameters are invalid
        """
        # Type checking
        if not isinstance(failure_threshold, int):
            raise TypeError("failure_threshold must be an integer")
        if not isinstance(timeout, int | float):
            raise TypeError("timeout must be a number")

        # Input validation
        if failure_threshold < 1:
            raise ValueError("failure_threshold must be positive")
        if timeout <= 0:
            raise ValueError("timeout must be positive")

        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.fallback = fallback
        self.state: Literal["CLOSED", "OPEN", "HALF_OPEN"] = "CLOSED"
        self.failure_count = 0
        self.last_failure_time: float | None = None

    async def call(self, agent: Callable[..., Awaitable[Any]], *args: Any, **kwargs: Any) -> Any:
        """Execute agent call with circuit breaker protection.

        Args:
            agent: Async function to call
            *args: Positional arguments for agent
            **kwargs: Keyword arguments for agent

        Returns:
            Result from agent call or fallback value

        Raises:
            CircuitBreakerOpenError: If circuit is OPEN and no fallback provided
            Exception: Any exception raised by agent
        """
        # Check if we should transition from OPEN to HALF_OPEN
        if self.state == "OPEN":
            if self._should_attempt_reset():
                self.state = "HALF_OPEN"
            else:
                # Circuit is still open, use fallback or reject
                if self.fallback is not None:
                    return self.fallback()
                raise CircuitBreakerOpenError("Circuit breaker is OPEN")

        # Attempt the call
        try:
            result = await agent(*args, **kwargs)
            self._on_success()
            return result
        except Exception:
            self._on_failure()
            raise

    def _should_attempt_reset(self) -> bool:
        """Check if enough time has passed to try HALF_OPEN state.

        Returns:
            True if timeout period has elapsed
        """
        if self.last_failure_time is None:
            return False
        return time.time() - self.last_failure_time >= self.timeout

    def _on_success(self) -> None:
        """Handle successful call - reset to CLOSED state."""
        self.failure_count = 0
        self.state = "CLOSED"
        self.last_failure_time = None

    def _on_failure(self) -> None:
        """Handle failed call - increment counter and maybe open circuit."""
        self.failure_count += 1
        self.last_failure_time = time.time()

        # If we're in HALF_OPEN and fail, go back to OPEN
        if self.state == "HALF_OPEN":
            self.state = "OPEN"
        # If we've hit threshold failures, open the circuit
        elif self.failure_count >= self.failure_threshold:
            self.state = "OPEN"
