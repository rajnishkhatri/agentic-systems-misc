"""Fallback Strategies (FR4.7) for Agent Reliability Framework.

This module provides 4 fallback strategies for graceful degradation when agents fail:
1. CACHE: Return cached result from previous successful execution
2. DEFAULT: Return predefined default value
3. SKIP: Return None for optional agents (workflow continues)
4. HUMAN_IN_LOOP: Request human review for high-stakes decisions

Usage:
    # Cache fallback with TTL
    handler = FallbackHandler(strategy=FallbackStrategy.CACHE)
    handler.set_cache("invoice_123", {"vendor": "Acme"}, ttl_seconds=3600)
    result = handler.execute_with_fallback(extract_vendor, cache_key="invoice_123")

    # Default fallback for non-critical agents
    handler = FallbackHandler(
        strategy=FallbackStrategy.DEFAULT,
        default_value={"confidence": 0.0}
    )
    result = handler.execute_with_fallback(sentiment_analysis)

    # Skip fallback for optional agents
    handler = FallbackHandler(strategy=FallbackStrategy.SKIP)
    result = handler.execute_with_fallback(optional_enrichment)  # Returns None on failure

    # Human-in-loop for high-stakes decisions
    handler = FallbackHandler(strategy=FallbackStrategy.HUMAN_IN_LOOP)
    result = handler.execute_with_fallback(
        fraud_detection,
        task_data={"transaction_id": "TXN-999", "amount": 50000.00}
    )
"""

from __future__ import annotations

import time
from collections.abc import Callable
from enum import Enum
from typing import Any, TypeVar, cast

T = TypeVar("T")


class FallbackStrategy(Enum):
    """Fallback strategies for agent failure handling.

    Attributes:
        CACHE: Return cached result from previous successful execution
        DEFAULT: Return predefined default value
        SKIP: Return None (for optional agents)
        HUMAN_IN_LOOP: Request human review
    """

    CACHE = "cache"
    DEFAULT = "default"
    SKIP = "skip"
    HUMAN_IN_LOOP = "human_in_loop"


class FallbackHandler:
    """Handler for executing agents with fallback strategies on failure.

    This class implements graceful degradation patterns for agent reliability.
    It tracks metrics and provides different fallback behaviors based on strategy.

    Attributes:
        strategy: The fallback strategy to use
        default_value: Default value for DEFAULT strategy (required if strategy=DEFAULT)
        _cache: In-memory cache for CACHE strategy (key → (value, expiry_timestamp))
        _metrics: Tracking metrics for fallback behavior
    """

    def __init__(
        self,
        strategy: FallbackStrategy,
        default_value: Any | None = None,
    ) -> None:
        """Initialize fallback handler with strategy.

        Args:
            strategy: Fallback strategy to use
            default_value: Default value for DEFAULT strategy (required if strategy=DEFAULT)

        Raises:
            TypeError: If strategy is not a FallbackStrategy enum
            ValueError: If DEFAULT strategy used without default_value
        """
        # Step 1: Type checking
        if not isinstance(strategy, FallbackStrategy):
            raise TypeError("strategy must be FallbackStrategy enum")

        # Step 2: Input validation
        if strategy == FallbackStrategy.DEFAULT and default_value is None:
            raise ValueError("default_value required for DEFAULT strategy")

        # Step 3: Initialize attributes
        self.strategy = strategy
        self.default_value = default_value
        self._cache: dict[str, tuple[Any, float]] = {}
        self._metrics: dict[str, Any] = {
            "fallback_triggered": False,
            "fallback_source": None,
            "skipped": False,
            "human_review_requested": False,
        }

    def set_cache(self, key: str, value: Any, ttl_seconds: int = 3600) -> None:
        """Store value in cache with TTL.

        Args:
            key: Cache key
            value: Value to cache
            ttl_seconds: Time-to-live in seconds (default: 1 hour)

        Raises:
            TypeError: If key is not a string
            ValueError: If ttl_seconds is not positive
        """
        # Step 1: Type checking
        if not isinstance(key, str):
            raise TypeError("key must be a string")

        # Step 2: Input validation
        if ttl_seconds <= 0:
            raise ValueError("ttl_seconds must be positive")

        # Step 3: Store with expiry timestamp
        expiry_time = time.time() + ttl_seconds
        self._cache[key] = (value, expiry_time)

    def get_cache(self, key: str) -> T | dict[str, Any] | None:
        """Retrieve value from cache if not expired.

        Args:
            key: Cache key

        Returns:
            Cached value if exists and not expired, None otherwise
        """
        if key not in self._cache:
            return None

        value, expiry_time = self._cache[key]

        # Check if expired
        if time.time() > expiry_time:
            del self._cache[key]
            return None

        return cast(T | dict[str, Any] | None, value)

    def execute_with_fallback(
        self,
        agent_func: Callable[[], T],
        cache_key: str | None = None,
        task_data: dict[str, Any] | None = None,
    ) -> T | None | dict[str, Any]:
        """Execute agent function with fallback on failure.

        Args:
            agent_func: Agent function to execute
            cache_key: Cache key for CACHE strategy (optional)
            task_data: Task metadata for HUMAN_IN_LOOP strategy (optional)

        Returns:
            Agent result on success, fallback value on failure

        Raises:
            Exception: If fallback fails to provide graceful degradation
        """
        # Step 1: Try to execute agent
        try:
            result = agent_func()
            # Success - cache result if CACHE strategy
            if self.strategy == FallbackStrategy.CACHE and cache_key:
                self.set_cache(cache_key, result)
            return result

        except Exception as e:
            # Step 2: Agent failed - apply fallback strategy
            self._metrics["fallback_triggered"] = True

            if self.strategy == FallbackStrategy.CACHE:
                return self._apply_cache_fallback(cache_key, e)
            elif self.strategy == FallbackStrategy.DEFAULT:
                return self._apply_default_fallback()
            elif self.strategy == FallbackStrategy.SKIP:
                return self._apply_skip_fallback()
            elif self.strategy == FallbackStrategy.HUMAN_IN_LOOP:
                return self._apply_human_fallback(task_data, e)
            else:
                # Should never reach here due to enum constraint
                raise ValueError(f"Unknown fallback strategy: {self.strategy}")

    def _apply_cache_fallback(self, cache_key: str | None, error: Exception) -> T | dict[str, Any] | None:
        """Apply CACHE fallback strategy.

        Args:
            cache_key: Cache key to retrieve
            error: Original error from agent

        Returns:
            Cached value

        Raises:
            Exception: If cache miss (no graceful degradation possible)
        """
        self._metrics["fallback_source"] = "cache"

        if not cache_key:
            raise ValueError("cache_key required for CACHE fallback") from error

        cached_value = self.get_cache(cache_key)
        if cached_value is None:
            raise ValueError(f"Cache miss for key: {cache_key}") from error

        return cached_value

    def _apply_default_fallback(self) -> T | dict[str, Any] | None:
        """Apply DEFAULT fallback strategy.

        Returns:
            Predefined default value
        """
        self._metrics["fallback_source"] = "default"
        return self.default_value

    def _apply_skip_fallback(self) -> T | dict[str, Any] | None:
        """Apply SKIP fallback strategy.

        Returns:
            None (agent step skipped)
        """
        self._metrics["fallback_source"] = "skip"
        self._metrics["skipped"] = True
        return None

    def _apply_human_fallback(
        self, task_data: dict[str, Any] | None, error: Exception
    ) -> dict[str, Any]:
        """Apply HUMAN_IN_LOOP fallback strategy.

        Args:
            task_data: Task metadata for human review
            error: Original error from agent

        Returns:
            Review request dictionary with status and error details
        """
        self._metrics["fallback_source"] = "human_in_loop"
        self._metrics["human_review_requested"] = True

        return {
            "status": "pending_human_review",
            "task_data": task_data or {},
            "error": str(error),
            "error_type": type(error).__name__,
        }

    def get_metrics(self) -> dict[str, Any]:
        """Get fallback metrics.

        Returns:
            Dictionary with fallback tracking metrics
        """
        return self._metrics.copy()

    def reset_metrics(self) -> None:
        """Reset metrics for new execution."""
        self._metrics = {
            "fallback_triggered": False,
            "fallback_source": None,
            "skipped": False,
            "human_review_requested": False,
        }
