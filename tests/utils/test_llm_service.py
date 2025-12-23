"""Tests for LLMService - TDD tests for the LiteLLM wrapper.

Test naming convention: test_should_[expected_result]_when_[condition]()
"""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from pydantic import BaseModel

from utils.llm_service import (
    CompletionResult,
    CostTracker,
    LLMService,
    get_default_service,
    reset_default_service,
)

# =============================================================================
# Test Fixtures
# =============================================================================


class MockUsage:
    """Mock LiteLLM usage object."""

    def __init__(self, prompt_tokens: int = 10, completion_tokens: int = 5):
        self.prompt_tokens = prompt_tokens
        self.completion_tokens = completion_tokens


class MockMessage:
    """Mock LiteLLM message object."""

    def __init__(self, content: str = "Test response"):
        self.content = content


class MockChoice:
    """Mock LiteLLM choice object."""

    def __init__(self, content: str = "Test response", logprobs: dict | None = None):
        self.message = MockMessage(content)
        self.logprobs = logprobs


class MockResponse:
    """Mock LiteLLM response object."""

    def __init__(
        self,
        content: str = "Test response",
        model: str = "gpt-4o-mini",
        prompt_tokens: int = 10,
        completion_tokens: int = 5,
        logprobs: dict | None = None,
    ):
        self.model = model
        self.choices = [MockChoice(content, logprobs)]
        self.usage = MockUsage(prompt_tokens, completion_tokens)


class JudgeResult(BaseModel):
    """Test Pydantic model for structured output tests."""

    score: str
    reason: str


@pytest.fixture
def mock_response() -> MockResponse:
    """Create a mock LiteLLM response."""
    return MockResponse()


@pytest.fixture
def llm_service() -> LLMService:
    """Create a fresh LLMService instance for testing."""
    # Disable caching for tests
    return LLMService(cache_type="none")


@pytest.fixture(autouse=True)
def reset_singleton():
    """Reset the singleton before each test."""
    reset_default_service()
    yield
    reset_default_service()


# =============================================================================
# LLMService Initialization Tests
# =============================================================================


def test_should_use_default_models_when_no_args_provided() -> None:
    """Test that default models are set from environment or hardcoded defaults."""
    service = LLMService(cache_type="none")
    assert service.default_model is not None
    assert service.judge_model is not None
    assert service.routing_model is not None


def test_should_use_provided_models_when_args_given() -> None:
    """Test that provided model names override defaults."""
    service = LLMService(
        default_model="claude-3-opus-20240229",
        judge_model="gpt-4o",
        routing_model="gpt-4o-mini",
        cache_type="none",
    )
    assert service.default_model == "claude-3-opus-20240229"
    assert service.judge_model == "gpt-4o"
    assert service.routing_model == "gpt-4o-mini"


def test_should_raise_type_error_when_default_model_not_string() -> None:
    """Test that non-string default_model raises TypeError."""
    with pytest.raises(TypeError, match="default_model must be a string"):
        LLMService(default_model=123)  # type: ignore


def test_should_raise_type_error_when_judge_model_not_string() -> None:
    """Test that non-string judge_model raises TypeError."""
    with pytest.raises(TypeError, match="judge_model must be a string"):
        LLMService(judge_model=["gpt-4o"])  # type: ignore


def test_should_raise_type_error_when_routing_model_not_string() -> None:
    """Test that non-string routing_model raises TypeError."""
    with pytest.raises(TypeError, match="routing_model must be a string"):
        LLMService(routing_model={"model": "gpt-4o-mini"})  # type: ignore


def test_should_raise_type_error_when_cache_type_not_string() -> None:
    """Test that non-string cache_type raises TypeError."""
    with pytest.raises(TypeError, match="cache_type must be a string"):
        LLMService(cache_type=True)  # type: ignore


def test_should_enable_cache_when_disk_type() -> None:
    """Test that disk cache type enables caching."""
    with patch("utils.llm_service.Cache"):
        service = LLMService(cache_type="disk")
        assert service.cache_enabled is True


def test_should_disable_cache_when_none_type() -> None:
    """Test that 'none' cache type disables caching."""
    service = LLMService(cache_type="none")
    assert service.cache_enabled is False


# =============================================================================
# CostTracker Tests
# =============================================================================


def test_should_track_single_completion_cost() -> None:
    """Test that CostTracker records a single completion correctly."""
    tracker = CostTracker()
    result = CompletionResult(
        content="test",
        model="gpt-4o-mini",
        input_tokens=100,
        output_tokens=50,
        cost=0.0015,
    )
    tracker.record(result)

    assert tracker.total_cost == 0.0015
    assert tracker.total_input_tokens == 100
    assert tracker.total_output_tokens == 50
    assert tracker.call_count == 1
    assert tracker.costs_by_model["gpt-4o-mini"] == 0.0015


def test_should_accumulate_costs_across_multiple_completions() -> None:
    """Test that CostTracker accumulates costs correctly."""
    tracker = CostTracker()

    result1 = CompletionResult(content="a", model="gpt-4o-mini", input_tokens=100, output_tokens=50, cost=0.001)
    result2 = CompletionResult(content="b", model="gpt-4o", input_tokens=200, output_tokens=100, cost=0.01)

    tracker.record(result1)
    tracker.record(result2)

    assert tracker.total_cost == 0.011
    assert tracker.total_input_tokens == 300
    assert tracker.total_output_tokens == 150
    assert tracker.call_count == 2
    assert tracker.costs_by_model["gpt-4o-mini"] == 0.001
    assert tracker.costs_by_model["gpt-4o"] == 0.01


def test_should_return_correct_summary() -> None:
    """Test that CostTracker.summary() returns correct data."""
    tracker = CostTracker()
    result = CompletionResult(content="test", model="gpt-4o", input_tokens=50, output_tokens=25, cost=0.005)
    tracker.record(result)

    summary = tracker.summary()

    assert summary["total_cost"] == 0.005
    assert summary["total_input_tokens"] == 50
    assert summary["total_output_tokens"] == 25
    assert summary["call_count"] == 1
    assert summary["costs_by_model"]["gpt-4o"] == 0.005


# =============================================================================
# Synchronous Completion Tests
# =============================================================================


def test_should_raise_type_error_when_messages_not_list(llm_service: LLMService) -> None:
    """Test that non-list messages raises TypeError."""
    with pytest.raises(TypeError, match="messages must be a list"):
        llm_service.complete_sync("not a list")  # type: ignore


def test_should_raise_value_error_when_messages_empty(llm_service: LLMService) -> None:
    """Test that empty messages raises ValueError."""
    with pytest.raises(ValueError, match="messages cannot be empty"):
        llm_service.complete_sync([])


@patch("utils.llm_service.completion")
def test_should_return_completion_result_when_valid_request(
    mock_completion: MagicMock, llm_service: LLMService
) -> None:
    """Test successful synchronous completion."""
    mock_completion.return_value = MockResponse(
        content="Hello!", model="gpt-4o-mini", prompt_tokens=5, completion_tokens=2
    )

    result = llm_service.complete_sync(messages=[{"role": "user", "content": "Hi"}])

    assert isinstance(result, CompletionResult)
    assert result.content == "Hello!"
    assert result.model == "gpt-4o-mini"
    assert result.input_tokens == 5
    assert result.output_tokens == 2


@patch("utils.llm_service.completion")
def test_should_use_default_model_when_model_not_specified(mock_completion: MagicMock) -> None:
    """Test that default model is used when not specified."""
    service = LLMService(default_model="gpt-4o", cache_type="none")
    mock_completion.return_value = MockResponse()

    service.complete_sync(messages=[{"role": "user", "content": "test"}])

    call_kwargs = mock_completion.call_args.kwargs
    assert call_kwargs["model"] == "gpt-4o"


@patch("utils.llm_service.completion")
def test_should_pass_logprobs_when_requested(mock_completion: MagicMock, llm_service: LLMService) -> None:
    """Test that logprobs parameter is passed correctly."""
    mock_completion.return_value = MockResponse()

    llm_service.complete_sync(messages=[{"role": "user", "content": "test"}], logprobs=True, top_logprobs=5)

    call_kwargs = mock_completion.call_args.kwargs
    assert call_kwargs["logprobs"] is True
    assert call_kwargs["top_logprobs"] == 5


@patch("utils.llm_service.completion")
def test_should_track_cost_when_tracker_provided(mock_completion: MagicMock) -> None:
    """Test that cost is tracked when CostTracker is provided."""
    tracker = CostTracker()
    service = LLMService(cache_type="none", cost_tracker=tracker)
    mock_completion.return_value = MockResponse(prompt_tokens=100, completion_tokens=50)

    service.complete_sync(messages=[{"role": "user", "content": "test"}])

    assert tracker.call_count == 1
    assert tracker.total_input_tokens == 100
    assert tracker.total_output_tokens == 50


# =============================================================================
# Async Completion Tests
# =============================================================================


@pytest.mark.asyncio
async def test_should_raise_type_error_when_async_messages_not_list(llm_service: LLMService) -> None:
    """Test that non-list messages raises TypeError in async."""
    with pytest.raises(TypeError, match="messages must be a list"):
        await llm_service.complete("not a list")  # type: ignore


@pytest.mark.asyncio
async def test_should_raise_value_error_when_async_messages_empty(llm_service: LLMService) -> None:
    """Test that empty messages raises ValueError in async."""
    with pytest.raises(ValueError, match="messages cannot be empty"):
        await llm_service.complete([])


@pytest.mark.asyncio
@patch("utils.llm_service.acompletion")
async def test_should_return_completion_result_when_async_valid_request(
    mock_acompletion: AsyncMock, llm_service: LLMService
) -> None:
    """Test successful async completion."""
    mock_acompletion.return_value = MockResponse(
        content="Async hello!", model="gpt-4o", prompt_tokens=10, completion_tokens=3
    )

    result = await llm_service.complete(messages=[{"role": "user", "content": "Hello async"}])

    assert isinstance(result, CompletionResult)
    assert result.content == "Async hello!"
    assert result.model == "gpt-4o"


# =============================================================================
# Structured Output Tests
# =============================================================================


def test_should_raise_type_error_when_structured_messages_not_list(llm_service: LLMService) -> None:
    """Test that non-list messages raises TypeError for structured output."""
    with pytest.raises(TypeError, match="messages must be a list"):
        llm_service.complete_structured_sync("not a list", JudgeResult)  # type: ignore


def test_should_raise_type_error_when_response_model_not_pydantic(llm_service: LLMService) -> None:
    """Test that non-Pydantic response_model raises TypeError."""
    with pytest.raises(TypeError, match="response_model must be a Pydantic BaseModel subclass"):
        llm_service.complete_structured_sync([{"role": "user", "content": "test"}], dict)  # type: ignore


def test_should_raise_value_error_when_structured_messages_empty(llm_service: LLMService) -> None:
    """Test that empty messages raises ValueError for structured output."""
    with pytest.raises(ValueError, match="messages cannot be empty"):
        llm_service.complete_structured_sync([], JudgeResult)


@patch("utils.llm_service.completion")
def test_should_parse_pydantic_response_when_valid_json(mock_completion: MagicMock, llm_service: LLMService) -> None:
    """Test successful Pydantic parsing of structured response."""
    mock_completion.return_value = MockResponse(
        content='{"score": "PASS", "reason": "All good"}',
        model="gpt-4o",
    )

    result = llm_service.complete_structured_sync(
        messages=[{"role": "user", "content": "Evaluate this"}],
        response_model=JudgeResult,
    )

    assert isinstance(result, JudgeResult)
    assert result.score == "PASS"
    assert result.reason == "All good"


@patch("utils.llm_service.completion")
def test_should_raise_value_error_when_invalid_json_response(
    mock_completion: MagicMock, llm_service: LLMService
) -> None:
    """Test that invalid JSON raises ValueError."""
    mock_completion.return_value = MockResponse(content="not valid json", model="gpt-4o")

    with pytest.raises(ValueError, match="Failed to parse response"):
        llm_service.complete_structured_sync(
            messages=[{"role": "user", "content": "test"}],
            response_model=JudgeResult,
        )


@patch("utils.llm_service.completion")
def test_should_use_judge_model_for_structured_output(mock_completion: MagicMock) -> None:
    """Test that judge_model is used by default for structured output."""
    service = LLMService(judge_model="gpt-4o", cache_type="none")
    mock_completion.return_value = MockResponse(content='{"score": "PASS", "reason": "ok"}')

    service.complete_structured_sync(
        messages=[{"role": "user", "content": "test"}],
        response_model=JudgeResult,
    )

    call_kwargs = mock_completion.call_args.kwargs
    assert call_kwargs["model"] == "gpt-4o"


# =============================================================================
# Async Structured Output Tests
# =============================================================================


@pytest.mark.asyncio
async def test_should_raise_type_error_when_async_structured_messages_not_list(llm_service: LLMService) -> None:
    """Test that non-list messages raises TypeError for async structured output."""
    with pytest.raises(TypeError, match="messages must be a list"):
        await llm_service.complete_structured("not a list", JudgeResult)  # type: ignore


@pytest.mark.asyncio
async def test_should_raise_type_error_when_async_response_model_not_pydantic(llm_service: LLMService) -> None:
    """Test that non-Pydantic response_model raises TypeError for async."""
    with pytest.raises(TypeError, match="response_model must be a Pydantic BaseModel subclass"):
        await llm_service.complete_structured([{"role": "user", "content": "test"}], str)  # type: ignore


@pytest.mark.asyncio
@patch("utils.llm_service.acompletion")
async def test_should_parse_pydantic_response_when_async_valid_json(
    mock_acompletion: AsyncMock, llm_service: LLMService
) -> None:
    """Test successful async Pydantic parsing."""
    mock_acompletion.return_value = MockResponse(
        content='{"score": "FAIL", "reason": "Issues found"}',
        model="gpt-4o",
    )

    result = await llm_service.complete_structured(
        messages=[{"role": "user", "content": "Evaluate"}],
        response_model=JudgeResult,
    )

    assert isinstance(result, JudgeResult)
    assert result.score == "FAIL"
    assert result.reason == "Issues found"


# =============================================================================
# Singleton Tests
# =============================================================================


@patch("utils.llm_service.Cache")
def test_should_return_same_instance_for_default_service(mock_cache: MagicMock) -> None:
    """Test that get_default_service returns the same singleton."""
    service1 = get_default_service()
    service2 = get_default_service()
    assert service1 is service2


@patch("utils.llm_service.Cache")
def test_should_create_new_instance_after_reset(mock_cache: MagicMock) -> None:
    """Test that reset_default_service creates a new instance."""
    service1 = get_default_service()
    reset_default_service()
    service2 = get_default_service()
    assert service1 is not service2


# =============================================================================
# CompletionResult Tests
# =============================================================================


def test_should_store_all_fields_in_completion_result() -> None:
    """Test that CompletionResult stores all provided fields."""
    result = CompletionResult(
        content="test content",
        model="gpt-4o-mini",
        input_tokens=100,
        output_tokens=50,
        cost=0.001,
        logprobs=[{"token": -0.5}],
        raw_response={"test": "data"},
    )

    assert result.content == "test content"
    assert result.model == "gpt-4o-mini"
    assert result.input_tokens == 100
    assert result.output_tokens == 50
    assert result.cost == 0.001
    assert result.logprobs == [{"token": -0.5}]
    assert result.raw_response == {"test": "data"}


def test_should_have_optional_fields_as_none() -> None:
    """Test that optional fields default to None."""
    result = CompletionResult(
        content="test",
        model="gpt-4o",
        input_tokens=10,
        output_tokens=5,
        cost=0.0,
    )

    assert result.logprobs is None
    assert result.raw_response is None
