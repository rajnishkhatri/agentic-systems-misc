"""
TDD-RED Phase: Tests for context_judges.py

AI judges to evaluate context precision and recall for retrieval systems.
"""

import json
from unittest.mock import Mock, patch

import pytest


# Test: ContextPrecisionJudge class
def test_should_return_precision_score_when_judging_retrieved_chunks() -> None:
    """Test that ContextPrecisionJudge returns precision score."""
    from backend.context_judges import ContextPrecisionJudge

    judge = ContextPrecisionJudge()
    query = "What is karma yoga?"
    chunks = [
        "Karma yoga is the yoga of selfless action.",
        "The Bhagavad Gita teaches dharma.",
        "How to make naan bread.",
    ]

    with patch("backend.context_judges.OpenAI") as mock_openai:
        mock_client = Mock()
        mock_openai.return_value = mock_client

        mock_response = Mock()
        mock_response.choices = [
            Mock(
                message=Mock(
                    content=json.dumps(
                        {
                            "chunk_1": "RELEVANT",
                            "chunk_2": "RELEVANT",
                            "chunk_3": "IRRELEVANT",
                        }
                    )
                )
            )
        ]
        mock_client.chat.completions.create.return_value = mock_response

        result = judge.evaluate(query, chunks)

        assert "precision" in result
        assert result["precision"] == 2 / 3  # 2 relevant out of 3
        assert "labels" in result


def test_should_raise_typeerror_when_query_not_string() -> None:
    """Test that ContextPrecisionJudge raises TypeError for non-string query."""
    from backend.context_judges import ContextPrecisionJudge

    judge = ContextPrecisionJudge()

    with pytest.raises(TypeError, match="query must be a string"):
        judge.evaluate(123, ["chunk1"])


def test_should_raise_typeerror_when_chunks_not_list() -> None:
    """Test that ContextPrecisionJudge raises TypeError for non-list chunks."""
    from backend.context_judges import ContextPrecisionJudge

    judge = ContextPrecisionJudge()

    with pytest.raises(TypeError, match="chunks must be a list"):
        judge.evaluate("query", "not a list")


def test_should_raise_valueerror_when_chunks_list_empty() -> None:
    """Test that ContextPrecisionJudge raises ValueError for empty chunks."""
    from backend.context_judges import ContextPrecisionJudge

    judge = ContextPrecisionJudge()

    with pytest.raises(ValueError, match="chunks list cannot be empty"):
        judge.evaluate("query", [])


def test_should_use_custom_model_when_specified() -> None:
    """Test that ContextPrecisionJudge uses specified model."""
    from backend.context_judges import ContextPrecisionJudge

    judge = ContextPrecisionJudge(model="gpt-4o")
    query = "test query"
    chunks = ["chunk1"]

    with patch("backend.context_judges.OpenAI") as mock_openai:
        mock_client = Mock()
        mock_openai.return_value = mock_client

        mock_response = Mock()
        mock_response.choices = [
            Mock(message=Mock(content=json.dumps({"chunk_1": "RELEVANT"})))
        ]
        mock_client.chat.completions.create.return_value = mock_response

        judge.evaluate(query, chunks)

        call_kwargs = mock_client.chat.completions.create.call_args[1]
        assert call_kwargs["model"] == "gpt-4o"


def test_should_handle_all_relevant_chunks() -> None:
    """Test that ContextPrecisionJudge handles all relevant chunks (precision=1.0)."""
    from backend.context_judges import ContextPrecisionJudge

    judge = ContextPrecisionJudge()
    query = "What is dharma?"
    chunks = ["Dharma is duty.", "Dharma is righteousness."]

    with patch("backend.context_judges.OpenAI") as mock_openai:
        mock_client = Mock()
        mock_openai.return_value = mock_client

        mock_response = Mock()
        mock_response.choices = [
            Mock(
                message=Mock(
                    content=json.dumps({"chunk_1": "RELEVANT", "chunk_2": "RELEVANT"})
                )
            )
        ]
        mock_client.chat.completions.create.return_value = mock_response

        result = judge.evaluate(query, chunks)

        assert result["precision"] == 1.0


def test_should_handle_all_irrelevant_chunks() -> None:
    """Test that ContextPrecisionJudge handles all irrelevant chunks (precision=0.0)."""
    from backend.context_judges import ContextPrecisionJudge

    judge = ContextPrecisionJudge()
    query = "What is karma?"
    chunks = ["Recipe for bread.", "Weather forecast."]

    with patch("backend.context_judges.OpenAI") as mock_openai:
        mock_client = Mock()
        mock_openai.return_value = mock_client

        mock_response = Mock()
        mock_response.choices = [
            Mock(
                message=Mock(
                    content=json.dumps(
                        {"chunk_1": "IRRELEVANT", "chunk_2": "IRRELEVANT"}
                    )
                )
            )
        ]
        mock_client.chat.completions.create.return_value = mock_response

        result = judge.evaluate(query, chunks)

        assert result["precision"] == 0.0


# Test: ContextRecallJudge class
def test_should_return_recall_score_when_comparing_to_ground_truth() -> None:
    """Test that ContextRecallJudge returns recall score."""
    from backend.context_judges import ContextRecallJudge

    judge = ContextRecallJudge()
    query = "What is karma yoga?"
    retrieved_chunks = ["Karma yoga is selfless action.", "Dharma is duty."]
    relevant_passages = ["Karma yoga passage 1", "Karma yoga passage 2"]

    with patch("backend.context_judges.OpenAI") as mock_openai:
        mock_client = Mock()
        mock_openai.return_value = mock_client

        mock_response = Mock()
        mock_response.choices = [
            Mock(
                message=Mock(
                    content=json.dumps({"covered_passages": [1, 2], "recall": 1.0})
                )
            )
        ]
        mock_client.chat.completions.create.return_value = mock_response

        result = judge.evaluate(query, retrieved_chunks, relevant_passages)

        assert "recall" in result
        assert result["recall"] == 1.0
        assert "covered_passages" in result


def test_should_raise_typeerror_when_relevant_passages_not_list() -> None:
    """Test that ContextRecallJudge raises TypeError for non-list relevant_passages."""
    from backend.context_judges import ContextRecallJudge

    judge = ContextRecallJudge()

    with pytest.raises(TypeError, match="relevant_passages must be a list"):
        judge.evaluate("query", ["chunk1"], "not a list")


def test_should_raise_valueerror_when_relevant_passages_empty() -> None:
    """Test that ContextRecallJudge raises ValueError for empty relevant_passages."""
    from backend.context_judges import ContextRecallJudge

    judge = ContextRecallJudge()

    with pytest.raises(ValueError, match="relevant_passages list cannot be empty"):
        judge.evaluate("query", ["chunk1"], [])


def test_should_handle_partial_recall() -> None:
    """Test that ContextRecallJudge handles partial recall (not all passages covered)."""
    from backend.context_judges import ContextRecallJudge

    judge = ContextRecallJudge()
    query = "What is dharma?"
    retrieved_chunks = ["Dharma is duty."]
    relevant_passages = ["Passage 1 about duty", "Passage 2 about righteousness"]

    with patch("backend.context_judges.OpenAI") as mock_openai:
        mock_client = Mock()
        mock_openai.return_value = mock_client

        mock_response = Mock()
        mock_response.choices = [
            Mock(message=Mock(content=json.dumps({"covered_passages": [1], "recall": 0.5})))
        ]
        mock_client.chat.completions.create.return_value = mock_response

        result = judge.evaluate(query, retrieved_chunks, relevant_passages)

        assert result["recall"] == 0.5
        assert len(result["covered_passages"]) == 1


def test_should_handle_zero_recall() -> None:
    """Test that ContextRecallJudge handles zero recall (no passages covered)."""
    from backend.context_judges import ContextRecallJudge

    judge = ContextRecallJudge()
    query = "What is karma?"
    retrieved_chunks = ["Recipe for bread."]
    relevant_passages = ["Karma passage 1", "Karma passage 2"]

    with patch("backend.context_judges.OpenAI") as mock_openai:
        mock_client = Mock()
        mock_openai.return_value = mock_client

        mock_response = Mock()
        mock_response.choices = [
            Mock(message=Mock(content=json.dumps({"covered_passages": [], "recall": 0.0})))
        ]
        mock_client.chat.completions.create.return_value = mock_response

        result = judge.evaluate(query, retrieved_chunks, relevant_passages)

        assert result["recall"] == 0.0
        assert len(result["covered_passages"]) == 0


def test_should_use_temperature_zero_for_consistency() -> None:
    """Test that judges use temperature=0 for consistent results."""
    from backend.context_judges import ContextPrecisionJudge

    judge = ContextPrecisionJudge()
    query = "test"
    chunks = ["chunk1"]

    with patch("backend.context_judges.OpenAI") as mock_openai:
        mock_client = Mock()
        mock_openai.return_value = mock_client

        mock_response = Mock()
        mock_response.choices = [
            Mock(message=Mock(content=json.dumps({"chunk_1": "RELEVANT"})))
        ]
        mock_client.chat.completions.create.return_value = mock_response

        judge.evaluate(query, chunks)

        call_kwargs = mock_client.chat.completions.create.call_args[1]
        assert call_kwargs["temperature"] == 0


def test_should_request_json_response_format() -> None:
    """Test that judges request JSON response format."""
    from backend.context_judges import ContextPrecisionJudge

    judge = ContextPrecisionJudge()
    query = "test"
    chunks = ["chunk1"]

    with patch("backend.context_judges.OpenAI") as mock_openai:
        mock_client = Mock()
        mock_openai.return_value = mock_client

        mock_response = Mock()
        mock_response.choices = [
            Mock(message=Mock(content=json.dumps({"chunk_1": "RELEVANT"})))
        ]
        mock_client.chat.completions.create.return_value = mock_response

        judge.evaluate(query, chunks)

        call_kwargs = mock_client.chat.completions.create.call_args[1]
        assert call_kwargs["response_format"] == {"type": "json_object"}
