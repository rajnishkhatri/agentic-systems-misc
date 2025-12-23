"""LiteLLM-based LLM Service with caching, cost tracking, and structured output support.

This module provides a unified interface for LLM interactions across the project,
supporting multiple providers (OpenAI, Anthropic, etc.) through LiteLLM's provider-agnostic API.

Key Features:
- Async completion with `acompletion()`
- Disk caching for development cost savings
- Cost tracking per request
- Structured output (Pydantic) support for judges
- Logprobs for confidence-based cascading

Example usage:
    from utils.llm_service import LLMService, get_default_service

    # Get singleton service
    service = get_default_service()

    # Simple completion
    response = await service.complete(
        messages=[{"role": "user", "content": "Hello!"}],
        model="gpt-4o-mini"
    )

    # Structured output with Pydantic
    from pydantic import BaseModel

    class JudgeResult(BaseModel):
        score: str
        reason: str

    result = await service.complete_structured(
        messages=[{"role": "user", "content": prompt}],
        response_model=JudgeResult,
        model="gpt-4o"
    )
"""

from __future__ import annotations

import json
import logging
import os
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, TypeVar

import litellm
from dotenv import load_dotenv
from litellm import Cache, acompletion, completion, model_cost
from pydantic import BaseModel

if TYPE_CHECKING:
    from litellm.types.utils import ModelResponse

# Load environment variables
load_dotenv()

# Configure logging
logger = logging.getLogger(__name__)

# Type variable for Pydantic models
T = TypeVar("T", bound=BaseModel)


@dataclass
class CompletionResult:
    """Result from an LLM completion with metadata."""

    content: str
    model: str
    input_tokens: int
    output_tokens: int
    cost: float
    logprobs: list[dict[str, Any]] | None = None
    raw_response: Any = None


@dataclass
class CostTracker:
    """Track cumulative costs across multiple LLM calls."""

    total_cost: float = 0.0
    total_input_tokens: int = 0
    total_output_tokens: int = 0
    call_count: int = 0
    costs_by_model: dict[str, float] = field(default_factory=dict)

    def record(self, result: CompletionResult) -> None:
        """Record a completion result in the tracker."""
        self.total_cost += result.cost
        self.total_input_tokens += result.input_tokens
        self.total_output_tokens += result.output_tokens
        self.call_count += 1
        self.costs_by_model[result.model] = self.costs_by_model.get(result.model, 0.0) + result.cost

    def summary(self) -> dict[str, Any]:
        """Return a summary of tracked costs."""
        return {
            "total_cost": self.total_cost,
            "total_input_tokens": self.total_input_tokens,
            "total_output_tokens": self.total_output_tokens,
            "call_count": self.call_count,
            "costs_by_model": self.costs_by_model,
        }


class LLMService:
    """Provider-agnostic LLM service using LiteLLM.

    Attributes:
        default_model: Default model for completions
        judge_model: Model for judge/evaluation tasks
        routing_model: Cheaper model for routing decisions
        cache_enabled: Whether disk caching is enabled
        cost_tracker: Optional tracker for cumulative costs
    """

    def __init__(
        self,
        default_model: str | None = None,
        judge_model: str | None = None,
        routing_model: str | None = None,
        cache_type: str | None = None,
        cost_tracker: CostTracker | None = None,
    ) -> None:
        """Initialize the LLM service.

        Args:
            default_model: Default model for completions (env: LLM_DEFAULT_MODEL)
            judge_model: Model for judge tasks (env: LLM_JUDGE_MODEL)
            routing_model: Cheaper model for routing (env: LLM_ROUTING_MODEL)
            cache_type: Cache type - "disk", "redis", or None (env: LLM_CACHE_TYPE)
            cost_tracker: Optional cost tracker for monitoring
        """
        # Step 1: Type validation
        if default_model is not None and not isinstance(default_model, str):
            raise TypeError("default_model must be a string")
        if judge_model is not None and not isinstance(judge_model, str):
            raise TypeError("judge_model must be a string")
        if routing_model is not None and not isinstance(routing_model, str):
            raise TypeError("routing_model must be a string")
        if cache_type is not None and not isinstance(cache_type, str):
            raise TypeError("cache_type must be a string")

        # Step 2: Set models from args or environment
        self.default_model = default_model or os.environ.get("LLM_DEFAULT_MODEL", "gpt-4o")
        self.judge_model = judge_model or os.environ.get("LLM_JUDGE_MODEL", "gpt-4o")
        self.routing_model = routing_model or os.environ.get("LLM_ROUTING_MODEL", "gpt-4o-mini")

        # Step 3: Configure caching
        cache_type_resolved = cache_type or os.environ.get("LLM_CACHE_TYPE", "disk")
        self.cache_enabled = cache_type_resolved in ("disk", "redis")

        if self.cache_enabled:
            litellm.cache = Cache(type=cache_type_resolved)
            logger.info(f"LLM caching enabled: {cache_type_resolved}")

        # Step 4: Set up cost tracking
        self.cost_tracker = cost_tracker

    def _calculate_cost(self, model: str, input_tokens: int, output_tokens: int) -> float:
        """Calculate the cost for a completion.

        Args:
            model: Model name
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens

        Returns:
            Cost in USD
        """
        try:
            cost_info = model_cost.get(model, {})
            input_cost_per_token = cost_info.get("input_cost_per_token", 0.0)
            output_cost_per_token = cost_info.get("output_cost_per_token", 0.0)
            return input_cost_per_token * input_tokens + output_cost_per_token * output_tokens
        except Exception:
            logger.warning(f"Could not calculate cost for model: {model}")
            return 0.0

    def _extract_logprobs(self, response: ModelResponse) -> list[dict[str, Any]] | None:
        """Extract logprobs from response if available."""
        try:
            choice = response.choices[0]
            if hasattr(choice, "logprobs") and choice.logprobs:
                content_logprobs = choice.logprobs.get("content", [])
                return [
                    {item.token: item.logprob for item in lp.top_logprobs} for lp in content_logprobs if lp.top_logprobs
                ]
        except (AttributeError, IndexError, KeyError):
            pass
        return None

    def _build_result(self, response: ModelResponse) -> CompletionResult:
        """Build a CompletionResult from a LiteLLM response."""
        model = response.model
        content = response.choices[0].message.content or ""
        input_tokens = response.usage.prompt_tokens
        output_tokens = response.usage.completion_tokens
        cost = self._calculate_cost(model, input_tokens, output_tokens)
        logprobs = self._extract_logprobs(response)

        result = CompletionResult(
            content=content,
            model=model,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cost=cost,
            logprobs=logprobs,
            raw_response=response,
        )

        if self.cost_tracker:
            self.cost_tracker.record(result)

        return result

    async def complete(
        self,
        messages: list[dict[str, str]],
        model: str | None = None,
        temperature: float = 0.0,
        max_tokens: int | None = None,
        logprobs: bool = False,
        top_logprobs: int = 10,
        caching: bool = True,
        timeout: float = 30.0,
        num_retries: int = 3,
        **kwargs: Any,
    ) -> CompletionResult:
        """Async LLM completion.

        Args:
            messages: Chat messages in OpenAI format
            model: Model to use (defaults to default_model)
            temperature: Sampling temperature (0.0 for deterministic)
            max_tokens: Maximum tokens in response
            logprobs: Whether to return logprobs
            top_logprobs: Number of top logprobs to return
            caching: Whether to use caching
            timeout: Request timeout in seconds
            num_retries: Number of retries on failure
            **kwargs: Additional arguments to pass to LiteLLM

        Returns:
            CompletionResult with content and metadata

        Raises:
            TypeError: If messages is not a list
            ValueError: If messages is empty
        """
        # Step 1: Type validation
        if not isinstance(messages, list):
            raise TypeError("messages must be a list")

        # Step 2: Input validation
        if len(messages) == 0:
            raise ValueError("messages cannot be empty")

        # Step 3: Build request
        model_to_use = model or self.default_model

        request_kwargs: dict[str, Any] = {
            "model": model_to_use,
            "messages": messages,
            "temperature": temperature,
            "num_retries": num_retries,
            "timeout": timeout,
            "caching": caching and self.cache_enabled,
        }

        if max_tokens:
            request_kwargs["max_tokens"] = max_tokens

        if logprobs:
            request_kwargs["logprobs"] = True
            request_kwargs["top_logprobs"] = top_logprobs

        request_kwargs.update(kwargs)

        # Step 4: Make request
        response = await acompletion(**request_kwargs)

        # Step 5: Build and return result
        return self._build_result(response)

    def complete_sync(
        self,
        messages: list[dict[str, str]],
        model: str | None = None,
        temperature: float = 0.0,
        max_tokens: int | None = None,
        logprobs: bool = False,
        top_logprobs: int = 10,
        caching: bool = True,
        timeout: float = 30.0,
        num_retries: int = 3,
        **kwargs: Any,
    ) -> CompletionResult:
        """Synchronous LLM completion.

        Same parameters as complete() but runs synchronously.
        """
        # Step 1: Type validation
        if not isinstance(messages, list):
            raise TypeError("messages must be a list")

        # Step 2: Input validation
        if len(messages) == 0:
            raise ValueError("messages cannot be empty")

        # Step 3: Build request
        model_to_use = model or self.default_model

        request_kwargs: dict[str, Any] = {
            "model": model_to_use,
            "messages": messages,
            "temperature": temperature,
            "num_retries": num_retries,
            "timeout": timeout,
            "caching": caching and self.cache_enabled,
        }

        if max_tokens:
            request_kwargs["max_tokens"] = max_tokens

        if logprobs:
            request_kwargs["logprobs"] = True
            request_kwargs["top_logprobs"] = top_logprobs

        request_kwargs.update(kwargs)

        # Step 4: Make request
        response = completion(**request_kwargs)

        # Step 5: Build and return result
        return self._build_result(response)

    async def complete_structured(
        self,
        messages: list[dict[str, str]],
        response_model: type[T],
        model: str | None = None,
        temperature: float = 0.0,
        timeout: float = 30.0,
        num_retries: int = 3,
        **kwargs: Any,
    ) -> T:
        """Async completion with structured Pydantic output.

        Args:
            messages: Chat messages in OpenAI format
            response_model: Pydantic model class for response
            model: Model to use (defaults to judge_model for structured output)
            temperature: Sampling temperature
            timeout: Request timeout in seconds
            num_retries: Number of retries on failure
            **kwargs: Additional arguments to pass to LiteLLM

        Returns:
            Parsed Pydantic model instance

        Raises:
            TypeError: If messages is not a list or response_model is not a Pydantic model
            ValueError: If messages is empty or response cannot be parsed
        """
        # Step 1: Type validation
        if not isinstance(messages, list):
            raise TypeError("messages must be a list")
        if not (isinstance(response_model, type) and issubclass(response_model, BaseModel)):
            raise TypeError("response_model must be a Pydantic BaseModel subclass")

        # Step 2: Input validation
        if len(messages) == 0:
            raise ValueError("messages cannot be empty")

        # Step 3: Build request (use judge_model by default for structured output)
        model_to_use = model or self.judge_model

        response = await acompletion(
            model=model_to_use,
            messages=messages,
            temperature=temperature,
            num_retries=num_retries,
            timeout=timeout,
            caching=self.cache_enabled,
            response_format=response_model,
            **kwargs,
        )

        # Step 4: Parse response
        content = response.choices[0].message.content
        try:
            parsed = response_model(**json.loads(content))
        except (json.JSONDecodeError, TypeError) as e:
            raise ValueError(f"Failed to parse response as {response_model.__name__}: {e}") from e

        # Step 5: Track cost
        if self.cost_tracker:
            model_name = response.model
            input_tokens = response.usage.prompt_tokens
            output_tokens = response.usage.completion_tokens
            cost = self._calculate_cost(model_name, input_tokens, output_tokens)
            result = CompletionResult(
                content=content,
                model=model_name,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                cost=cost,
            )
            self.cost_tracker.record(result)

        return parsed

    def complete_structured_sync(
        self,
        messages: list[dict[str, str]],
        response_model: type[T],
        model: str | None = None,
        temperature: float = 0.0,
        timeout: float = 30.0,
        num_retries: int = 3,
        **kwargs: Any,
    ) -> T:
        """Synchronous completion with structured Pydantic output.

        Same parameters as complete_structured() but runs synchronously.
        """
        # Step 1: Type validation
        if not isinstance(messages, list):
            raise TypeError("messages must be a list")
        if not (isinstance(response_model, type) and issubclass(response_model, BaseModel)):
            raise TypeError("response_model must be a Pydantic BaseModel subclass")

        # Step 2: Input validation
        if len(messages) == 0:
            raise ValueError("messages cannot be empty")

        # Step 3: Build request
        model_to_use = model or self.judge_model

        response = completion(
            model=model_to_use,
            messages=messages,
            temperature=temperature,
            num_retries=num_retries,
            timeout=timeout,
            caching=self.cache_enabled,
            response_format=response_model,
            **kwargs,
        )

        # Step 4: Parse response
        content = response.choices[0].message.content
        try:
            parsed = response_model(**json.loads(content))
        except (json.JSONDecodeError, TypeError) as e:
            raise ValueError(f"Failed to parse response as {response_model.__name__}: {e}") from e

        # Step 5: Track cost
        if self.cost_tracker:
            model_name = response.model
            input_tokens = response.usage.prompt_tokens
            output_tokens = response.usage.completion_tokens
            cost = self._calculate_cost(model_name, input_tokens, output_tokens)
            result = CompletionResult(
                content=content,
                model=model_name,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                cost=cost,
            )
            self.cost_tracker.record(result)

        return parsed


# Singleton instance
_default_service: LLMService | None = None


def get_default_service() -> LLMService:
    """Get or create the default LLMService singleton."""
    global _default_service
    if _default_service is None:
        _default_service = LLMService()
    return _default_service


def reset_default_service() -> None:
    """Reset the default service (useful for testing)."""
    global _default_service
    _default_service = None
