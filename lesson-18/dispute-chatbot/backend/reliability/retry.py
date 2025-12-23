"""Retry logic with exponential backoff and jitter for agent reliability.

This module implements FR4.1: Retry Logic with Exponential Backoff.

Key features:
- Async retry wrapper for agent calls
- Exponential backoff with jitter to avoid thundering herd
- Configurable max retries, base delay, and exponential base
- Defensive input validation
- Type-safe implementation

Usage:
    from lesson_16.backend.reliability.retry import retry_with_backoff

    # Retry an agent call up to 3 times
    result = await retry_with_backoff(
        agent_function,
        max_retries=3,
        base_delay=1.0,
        exponential_base=2,
    )
"""

from __future__ import annotations

import asyncio
import random
from collections.abc import Awaitable, Callable
from typing import Any, TypeVar

T = TypeVar("T")


async def retry_with_backoff(
    func: Callable[..., Awaitable[T]],
    *args: Any,
    max_retries: int = 3,
    base_delay: float = 1.0,
    exponential_base: float = 2.0,
    jitter: bool = True,
    **kwargs: Any,
) -> T:
    """Retry an async function with exponential backoff and jitter.

    Args:
        func: Async function to retry
        *args: Positional arguments to pass to func
        max_retries: Maximum number of retry attempts (default: 3)
        base_delay: Base delay in seconds for exponential backoff (default: 1.0)
        exponential_base: Base for exponential calculation (default: 2.0)
        jitter: Whether to add random jitter to delays (default: True)
        **kwargs: Keyword arguments to pass to func

    Returns:
        Result from successful function call

    Raises:
        TypeError: If max_retries is not an integer
        ValueError: If max_retries is negative
        Exception: Re-raises the last exception if all retries are exhausted

    Example:
        >>> async def flaky_api_call():
        ...     # May fail intermittently
        ...     return await external_api.fetch()
        >>> result = await retry_with_backoff(flaky_api_call, max_retries=5)
    """
    # Step 1: Type checking (defensive)
    if not isinstance(max_retries, int):
        raise TypeError("max_retries must be an integer")

    # Step 2: Input validation (defensive)
    if max_retries < 0:
        raise ValueError("max_retries must be non-negative")

    if base_delay < 0:
        raise ValueError("base_delay must be non-negative")

    if exponential_base <= 0:
        raise ValueError("exponential_base must be positive")

    # Step 3: Retry logic with exponential backoff
    last_exception: Exception | None = None

    for attempt in range(max_retries + 1):  # Initial attempt + retries
        try:
            # Attempt to call the function
            result = await func(*args, **kwargs)
            return result

        except Exception as e:
            last_exception = e

            # If this was the last attempt, raise the exception
            if attempt == max_retries:
                raise

            # Calculate delay with exponential backoff
            delay = base_delay * (exponential_base ** attempt)

            # Add jitter: random value between 0 and delay
            if jitter:
                delay = random.uniform(0, delay)

            # Wait before retrying
            await asyncio.sleep(delay)

    # This should never be reached, but satisfies type checker
    if last_exception:
        raise last_exception

    raise RuntimeError("Retry logic failed unexpectedly")

