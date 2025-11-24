"""
Tests for lesson-14/memory_systems_implementation.ipynb helper functions

Following TDD: Write tests FIRST, then implement to make them pass.
Test naming convention: test_should_[result]_when_[condition]
"""

import json

# Module under test will be implemented after these tests pass
# These will be defined in the notebook and imported for testing
import sys
from pathlib import Path

import pytest

# Add lesson-14 to path for import
sys.path.insert(0, str(Path(__file__).parent.parent / "lesson-14"))

from memory_systems_helpers import (
    calculate_compression_roi,
    calculate_mmr_score,
    calculate_search_o1_overhead,
    count_tokens,
    export_results_json,
    select_documents_mmr,
    simulate_summarization,
    trim_conversation_history,
    validate_execution_mode,
)


class TestConfigurationValidation:
    """Test execution mode configuration validation."""

    def test_should_accept_demo_mode_when_uppercase(self) -> None:
        """Test that DEMO mode is valid."""
        # Given: DEMO mode string
        mode = "DEMO"

        # When: validating mode
        is_valid = validate_execution_mode(mode)

        # Then: should be valid
        assert is_valid is True

    def test_should_accept_full_mode_when_uppercase(self) -> None:
        """Test that FULL mode is valid."""
        # Given: FULL mode string
        mode = "FULL"

        # When: validating mode
        is_valid = validate_execution_mode(mode)

        # Then: should be valid
        assert is_valid is True

    def test_should_reject_invalid_mode(self) -> None:
        """Test that invalid mode raises ValueError."""
        # Given: invalid mode
        mode = "INVALID"

        # When/Then: should raise ValueError
        with pytest.raises(ValueError, match="EXECUTION_MODE must be 'DEMO' or 'FULL'"):
            validate_execution_mode(mode, raise_on_invalid=True)

    def test_should_reject_lowercase_mode(self) -> None:
        """Test that lowercase mode raises ValueError."""
        # Given: lowercase mode
        mode = "demo"

        # When/Then: should raise ValueError
        with pytest.raises(ValueError, match="EXECUTION_MODE must be 'DEMO' or 'FULL'"):
            validate_execution_mode(mode, raise_on_invalid=True)

    def test_should_raise_error_when_mode_not_string(self) -> None:
        """Test that non-string mode raises TypeError."""
        # Given: non-string mode
        mode = 123

        # When/Then: should raise TypeError
        with pytest.raises(TypeError, match="mode must be a string"):
            validate_execution_mode(mode)


class TestMMRCalculations:
    """Test Maximum Marginal Relevance (MMR) calculations."""

    def test_should_calculate_mmr_score_when_lambda_0(self) -> None:
        """Test MMR with lambda=0 (pure relevance)."""
        # Given: relevance score and max redundancy
        relevance = 0.9
        max_redundancy = 0.7
        lambda_param = 0.0

        # When: calculating MMR score
        mmr_score = calculate_mmr_score(relevance, max_redundancy, lambda_param)

        # Then: should return pure relevance (lambda=0 ignores diversity)
        assert abs(mmr_score - 0.9) < 0.001, f"Expected 0.9, got {mmr_score}"

    def test_should_calculate_mmr_score_when_lambda_1(self) -> None:
        """Test MMR with lambda=1 (pure diversity)."""
        # Given: relevance score and max redundancy
        relevance = 0.9
        max_redundancy = 0.7
        lambda_param = 1.0

        # When: calculating MMR score
        mmr_score = calculate_mmr_score(relevance, max_redundancy, lambda_param)

        # Then: should prioritize diversity ((1-1) * 0.9 - 1.0 * 0.7 = -0.7)
        expected = (1 - 1.0) * 0.9 - 1.0 * 0.7
        assert abs(mmr_score - expected) < 0.001, f"Expected {expected}, got {mmr_score}"

    def test_should_calculate_mmr_score_when_lambda_05(self) -> None:
        """Test MMR with lambda=0.5 (balanced)."""
        # Given: relevance score and max redundancy
        relevance = 0.8
        max_redundancy = 0.6
        lambda_param = 0.5

        # When: calculating MMR score
        mmr_score = calculate_mmr_score(relevance, max_redundancy, lambda_param)

        # Then: should balance relevance and diversity ((1-0.5) * 0.8 - 0.5 * 0.6 = 0.1)
        expected = (1 - 0.5) * 0.8 - 0.5 * 0.6
        assert abs(mmr_score - expected) < 0.001, f"Expected {expected}, got {mmr_score}"

    def test_should_raise_error_when_lambda_out_of_range(self) -> None:
        """Test that lambda outside [0, 1] raises ValueError."""
        # Given: invalid lambda
        relevance = 0.8
        max_redundancy = 0.6
        lambda_param = 1.5

        # When/Then: should raise ValueError
        with pytest.raises(ValueError, match="lambda_param must be in range \\[0, 1\\]"):
            calculate_mmr_score(relevance, max_redundancy, lambda_param)

    def test_should_raise_error_when_inputs_not_numeric(self) -> None:
        """Test that non-numeric inputs raise TypeError."""
        # Given: non-numeric input
        relevance = "0.8"
        max_redundancy = 0.6
        lambda_param = 0.5

        # When/Then: should raise TypeError
        with pytest.raises(TypeError, match="All inputs must be numeric"):
            calculate_mmr_score(relevance, max_redundancy, lambda_param)

    def test_should_raise_error_when_relevance_out_of_range(self) -> None:
        """Test that relevance outside [0, 1] raises ValueError."""
        # Given: relevance > 1
        relevance = 1.5
        max_redundancy = 0.6
        lambda_param = 0.5

        # When/Then: should raise ValueError
        with pytest.raises(ValueError, match="relevance must be in range \\[0, 1\\]"):
            calculate_mmr_score(relevance, max_redundancy, lambda_param)

    def test_should_raise_error_when_max_redundancy_out_of_range(self) -> None:
        """Test that max_redundancy outside [0, 1] raises ValueError."""
        # Given: max_redundancy > 1
        relevance = 0.8
        max_redundancy = 1.5
        lambda_param = 0.5

        # When/Then: should raise ValueError
        with pytest.raises(ValueError, match="max_redundancy must be in range \\[0, 1\\]"):
            calculate_mmr_score(relevance, max_redundancy, lambda_param)

    def test_should_select_top_k_documents_with_mmr(self) -> None:
        """Test MMR document selection returns correct count."""
        # Given: query embedding, document embeddings, and k
        query_embedding = [0.5, 0.5, 0.5]
        doc_embeddings = [
            [0.9, 0.1, 0.0],  # High relevance
            [0.8, 0.2, 0.0],  # Medium relevance, similar to first
            [0.1, 0.1, 0.8],  # Low relevance, diverse
            [0.7, 0.3, 0.0],  # Medium relevance, similar to first two
            [0.0, 0.0, 1.0],  # Low relevance, very diverse
        ]
        k = 3
        lambda_param = 0.5

        # When: selecting documents with MMR
        selected_indices = select_documents_mmr(
            query_embedding, doc_embeddings, k, lambda_param
        )

        # Then: should return exactly k documents
        assert len(selected_indices) == k, f"Expected {k} documents, got {len(selected_indices)}"
        # Then: should return valid indices
        assert all(0 <= idx < len(doc_embeddings) for idx in selected_indices)

    def test_should_raise_error_when_k_exceeds_documents(self) -> None:
        """Test that k > num_documents raises ValueError."""
        # Given: 3 documents but k=5
        query_embedding = [0.5, 0.5, 0.5]
        doc_embeddings = [[0.9, 0.1, 0.0], [0.8, 0.2, 0.0], [0.1, 0.1, 0.8]]
        k = 5
        lambda_param = 0.5

        # When/Then: should raise ValueError
        with pytest.raises(ValueError, match="k cannot exceed number of documents"):
            select_documents_mmr(query_embedding, doc_embeddings, k, lambda_param)

    def test_should_raise_error_when_empty_documents(self) -> None:
        """Test that empty documents list raises ValueError."""
        # Given: empty documents
        query_embedding = [0.5, 0.5, 0.5]
        doc_embeddings = []
        k = 3
        lambda_param = 0.5

        # When/Then: should raise ValueError
        with pytest.raises(ValueError, match="documents cannot be empty"):
            select_documents_mmr(query_embedding, doc_embeddings, k, lambda_param)

    def test_should_raise_error_when_query_embedding_not_list(self) -> None:
        """Test that non-list query_embedding raises TypeError."""
        # Given: non-list query_embedding
        query_embedding = "invalid"
        doc_embeddings = [[0.9, 0.1, 0.0]]
        k = 1
        lambda_param = 0.5

        # When/Then: should raise TypeError
        with pytest.raises(TypeError, match="query_embedding must be a list"):
            select_documents_mmr(query_embedding, doc_embeddings, k, lambda_param)

    def test_should_raise_error_when_doc_embeddings_not_list(self) -> None:
        """Test that non-list doc_embeddings raises TypeError."""
        # Given: non-list doc_embeddings
        query_embedding = [0.5, 0.5, 0.5]
        doc_embeddings = "invalid"
        k = 1
        lambda_param = 0.5

        # When/Then: should raise TypeError
        with pytest.raises(TypeError, match="doc_embeddings must be a list"):
            select_documents_mmr(query_embedding, doc_embeddings, k, lambda_param)

    def test_should_raise_error_when_k_not_integer(self) -> None:
        """Test that non-integer k raises TypeError."""
        # Given: non-integer k
        query_embedding = [0.5, 0.5, 0.5]
        doc_embeddings = [[0.9, 0.1, 0.0]]
        k = "3"
        lambda_param = 0.5

        # When/Then: should raise TypeError
        with pytest.raises(TypeError, match="k must be an integer"):
            select_documents_mmr(query_embedding, doc_embeddings, k, lambda_param)

    def test_should_raise_error_when_k_negative(self) -> None:
        """Test that k <= 0 raises ValueError."""
        # Given: k = 0
        query_embedding = [0.5, 0.5, 0.5]
        doc_embeddings = [[0.9, 0.1, 0.0]]
        k = 0
        lambda_param = 0.5

        # When/Then: should raise ValueError
        with pytest.raises(ValueError, match="k must be positive"):
            select_documents_mmr(query_embedding, doc_embeddings, k, lambda_param)


class TestTokenCounting:
    """Test token counting utility."""

    def test_should_count_tokens_for_simple_text(self) -> None:
        """Test token counting for simple English text."""
        # Given: simple text
        text = "Hello, world!"

        # When: counting tokens
        token_count = count_tokens(text)

        # Then: should return reasonable count (tiktoken ~3-4 tokens)
        assert 2 <= token_count <= 5, f"Expected 2-5 tokens, got {token_count}"

    def test_should_count_tokens_for_empty_string(self) -> None:
        """Test token counting for empty string."""
        # Given: empty string
        text = ""

        # When: counting tokens
        token_count = count_tokens(text)

        # Then: should return 0
        assert token_count == 0

    def test_should_count_tokens_for_long_text(self) -> None:
        """Test token counting for longer text."""
        # Given: longer text (100 words)
        text = " ".join(["word"] * 100)

        # When: counting tokens
        token_count = count_tokens(text)

        # Then: should return approximately 100 tokens (might vary with encoding)
        assert 80 <= token_count <= 120, f"Expected ~100 tokens, got {token_count}"

    def test_should_raise_error_when_text_not_string(self) -> None:
        """Test that non-string input raises TypeError."""
        # Given: non-string input
        text = 12345

        # When/Then: should raise TypeError
        with pytest.raises(TypeError, match="text must be a string"):
            count_tokens(text)


class TestConversationTrimming:
    """Test conversation history trimming."""

    def test_should_trim_to_max_tokens(self) -> None:
        """Test trimming conversation to max tokens."""
        # Given: conversation history and low max tokens
        messages = [
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi there!"},
            {"role": "user", "content": "How are you doing today? I hope everything is going well."},
            {"role": "assistant", "content": "I'm doing well, thank you for asking! How can I help you?"},
        ]
        max_tokens = 10  # Low limit to force trimming

        # When: trimming conversation
        trimmed = trim_conversation_history(messages, max_tokens)

        # Then: total tokens should be <= max_tokens
        total_tokens = sum(count_tokens(msg["content"]) for msg in trimmed)
        assert total_tokens <= max_tokens, f"Exceeded max tokens: {total_tokens} > {max_tokens}"
        # Then: should keep most recent messages
        assert len(trimmed) < len(messages), "Should have removed some messages"

    def test_should_preserve_all_when_under_limit(self) -> None:
        """Test that all messages preserved when under token limit."""
        # Given: short conversation and high max tokens
        messages = [
            {"role": "user", "content": "Hi"},
            {"role": "assistant", "content": "Hello"},
        ]
        max_tokens = 1000

        # When: trimming conversation
        trimmed = trim_conversation_history(messages, max_tokens)

        # Then: should preserve all messages
        assert len(trimmed) == len(messages), "Should preserve all messages under limit"

    def test_should_raise_error_when_max_tokens_negative(self) -> None:
        """Test that negative max_tokens raises ValueError."""
        # Given: negative max_tokens
        messages = [{"role": "user", "content": "Hello"}]
        max_tokens = -10

        # When/Then: should raise ValueError
        with pytest.raises(ValueError, match="max_tokens must be positive"):
            trim_conversation_history(messages, max_tokens)

    def test_should_raise_error_when_messages_empty(self) -> None:
        """Test that empty messages list raises ValueError."""
        # Given: empty messages
        messages = []
        max_tokens = 100

        # When/Then: should raise ValueError
        with pytest.raises(ValueError, match="messages cannot be empty"):
            trim_conversation_history(messages, max_tokens)

    def test_should_raise_error_when_messages_not_list(self) -> None:
        """Test that non-list messages raises TypeError."""
        # Given: non-list messages
        messages = "not a list"
        max_tokens = 100

        # When/Then: should raise TypeError
        with pytest.raises(TypeError, match="messages must be a list"):
            trim_conversation_history(messages, max_tokens)

    def test_should_raise_error_when_max_tokens_not_integer(self) -> None:
        """Test that non-integer max_tokens raises TypeError."""
        # Given: non-integer max_tokens
        messages = [{"role": "user", "content": "Hello"}]
        max_tokens = "100"

        # When/Then: should raise TypeError
        with pytest.raises(TypeError, match="max_tokens must be an integer"):
            trim_conversation_history(messages, max_tokens)


class TestSummarizationSimulation:
    """Test conversation summarization simulation."""

    def test_should_reduce_tokens_by_compression_ratio(self) -> None:
        """Test that summarization reduces tokens by expected ratio."""
        # Given: conversation and compression ratio
        messages = [
            {"role": "user", "content": "Hello, how are you today?"},
            {"role": "assistant", "content": "I'm doing well, thank you for asking!"},
            {"role": "user", "content": "What's the weather like?"},
        ]
        compression_ratio = 0.5

        # When: simulating summarization
        summary, original_tokens, summary_tokens = simulate_summarization(
            messages, compression_ratio
        )

        # Then: summary tokens should be ~50% of original
        expected_tokens = int(original_tokens * compression_ratio)
        assert abs(summary_tokens - expected_tokens) <= 2, (
            f"Expected ~{expected_tokens} tokens, got {summary_tokens}"
        )

    def test_should_return_summary_dict_with_metadata(self) -> None:
        """Test that summarization returns proper structure."""
        # Given: conversation
        messages = [{"role": "user", "content": "Hello"}]
        compression_ratio = 0.5

        # When: simulating summarization
        summary, original_tokens, summary_tokens = simulate_summarization(
            messages, compression_ratio
        )

        # Then: should return dict with required keys
        assert isinstance(summary, dict), "Summary should be a dict"
        assert "role" in summary, "Summary should have 'role' key"
        assert "content" in summary, "Summary should have 'content' key"
        assert summary["role"] == "system", "Summary role should be 'system'"

    def test_should_raise_error_when_compression_ratio_invalid(self) -> None:
        """Test that compression ratio outside (0, 1) raises ValueError."""
        # Given: invalid compression ratio
        messages = [{"role": "user", "content": "Hello"}]
        compression_ratio = 1.5

        # When/Then: should raise ValueError
        with pytest.raises(ValueError, match="compression_ratio must be in range \\(0, 1\\)"):
            simulate_summarization(messages, compression_ratio)

    def test_should_raise_error_when_messages_not_list_in_summarization(self) -> None:
        """Test that non-list messages raises TypeError in summarization."""
        # Given: non-list messages
        messages = "not a list"
        compression_ratio = 0.5

        # When/Then: should raise TypeError
        with pytest.raises(TypeError, match="messages must be a list"):
            simulate_summarization(messages, compression_ratio)

    def test_should_raise_error_when_compression_ratio_not_numeric(self) -> None:
        """Test that non-numeric compression_ratio raises TypeError."""
        # Given: non-numeric compression_ratio
        messages = [{"role": "user", "content": "Hello"}]
        compression_ratio = "0.5"

        # When/Then: should raise TypeError
        with pytest.raises(TypeError, match="compression_ratio must be numeric"):
            simulate_summarization(messages, compression_ratio)

    def test_should_raise_error_when_messages_empty_in_summarization(self) -> None:
        """Test that empty messages raises ValueError in summarization."""
        # Given: empty messages
        messages = []
        compression_ratio = 0.5

        # When/Then: should raise ValueError
        with pytest.raises(ValueError, match="messages cannot be empty"):
            simulate_summarization(messages, compression_ratio)


class TestSearchO1Overhead:
    """Test Search-o1 pattern overhead calculations."""

    def test_should_calculate_total_overhead(self) -> None:
        """Test calculation of total Search-o1 overhead."""
        # Given: search, retrieval, and condensation token counts
        search_tokens = 100
        retrieval_tokens = 500
        condensation_tokens = 150

        # When: calculating overhead
        overhead_metrics = calculate_search_o1_overhead(
            search_tokens, retrieval_tokens, condensation_tokens
        )

        # Then: total overhead should be sum of all
        expected_total = 100 + 500 + 150
        assert overhead_metrics["total_overhead"] == expected_total
        assert overhead_metrics["search_tokens"] == search_tokens
        assert overhead_metrics["retrieval_tokens"] == retrieval_tokens
        assert overhead_metrics["condensation_tokens"] == condensation_tokens

    def test_should_calculate_overhead_percentage(self) -> None:
        """Test overhead percentage calculation."""
        # Given: overhead and baseline tokens
        search_tokens = 50
        retrieval_tokens = 200
        condensation_tokens = 50
        baseline_tokens = 300

        # When: calculating overhead
        overhead_metrics = calculate_search_o1_overhead(
            search_tokens, retrieval_tokens, condensation_tokens, baseline_tokens
        )

        # Then: overhead percentage should be (300 / 300) * 100 = 100%
        expected_pct = (300 / 300) * 100
        assert abs(overhead_metrics["overhead_percentage"] - expected_pct) < 0.1

    def test_should_raise_error_when_negative_tokens(self) -> None:
        """Test that negative token counts raise ValueError."""
        # Given: negative token count
        search_tokens = -10
        retrieval_tokens = 100
        condensation_tokens = 50

        # When/Then: should raise ValueError
        with pytest.raises(ValueError, match="Token counts must be non-negative"):
            calculate_search_o1_overhead(search_tokens, retrieval_tokens, condensation_tokens)

    def test_should_raise_error_when_token_counts_not_integers(self) -> None:
        """Test that non-integer token counts raise TypeError."""
        # Given: non-integer token count
        search_tokens = "50"
        retrieval_tokens = 100
        condensation_tokens = 50

        # When/Then: should raise TypeError
        with pytest.raises(TypeError, match="Token counts must be integers"):
            calculate_search_o1_overhead(search_tokens, retrieval_tokens, condensation_tokens)

    def test_should_raise_error_when_baseline_tokens_negative(self) -> None:
        """Test that negative baseline_tokens raises ValueError."""
        # Given: negative baseline_tokens
        search_tokens = 50
        retrieval_tokens = 100
        condensation_tokens = 50
        baseline_tokens = -100

        # When/Then: should raise ValueError
        with pytest.raises(ValueError, match="baseline_tokens must be non-negative"):
            calculate_search_o1_overhead(search_tokens, retrieval_tokens, condensation_tokens, baseline_tokens)


class TestCompressionROI:
    """Test compression ROI calculations."""

    def test_should_calculate_roi_with_cost_savings(self) -> None:
        """Test ROI calculation with compression."""
        # Given: token counts and pricing
        original_tokens = 10000
        compressed_tokens = 2000
        cost_per_1k_tokens = 0.03  # $0.03 per 1K tokens

        # When: calculating ROI
        roi_metrics = calculate_compression_roi(
            original_tokens, compressed_tokens, cost_per_1k_tokens
        )

        # Then: should calculate correct savings
        original_cost = (10000 / 1000) * 0.03  # $0.30
        compressed_cost = (2000 / 1000) * 0.03  # $0.06
        expected_savings = original_cost - compressed_cost  # $0.24
        assert abs(roi_metrics["cost_savings"] - expected_savings) < 0.001
        assert abs(roi_metrics["original_cost"] - original_cost) < 0.001
        assert abs(roi_metrics["compressed_cost"] - compressed_cost) < 0.001

    def test_should_calculate_compression_ratio(self) -> None:
        """Test compression ratio calculation."""
        # Given: token counts
        original_tokens = 1000
        compressed_tokens = 250
        cost_per_1k_tokens = 0.03

        # When: calculating ROI
        roi_metrics = calculate_compression_roi(
            original_tokens, compressed_tokens, cost_per_1k_tokens
        )

        # Then: compression ratio should be 0.25 (250/1000)
        expected_ratio = 250 / 1000
        assert abs(roi_metrics["compression_ratio"] - expected_ratio) < 0.001

    def test_should_raise_error_when_compressed_exceeds_original(self) -> None:
        """Test that compressed > original raises ValueError."""
        # Given: compressed tokens > original
        original_tokens = 100
        compressed_tokens = 200
        cost_per_1k_tokens = 0.03

        # When/Then: should raise ValueError
        with pytest.raises(ValueError, match="compressed_tokens cannot exceed original_tokens"):
            calculate_compression_roi(original_tokens, compressed_tokens, cost_per_1k_tokens)

    def test_should_raise_error_when_token_counts_not_integers_in_roi(self) -> None:
        """Test that non-integer token counts raise TypeError in ROI."""
        # Given: non-integer token count
        original_tokens = "1000"
        compressed_tokens = 250
        cost_per_1k_tokens = 0.03

        # When/Then: should raise TypeError
        with pytest.raises(TypeError, match="Token counts must be integers"):
            calculate_compression_roi(original_tokens, compressed_tokens, cost_per_1k_tokens)

    def test_should_raise_error_when_cost_per_1k_not_numeric(self) -> None:
        """Test that non-numeric cost_per_1k_tokens raises TypeError."""
        # Given: non-numeric cost
        original_tokens = 1000
        compressed_tokens = 250
        cost_per_1k_tokens = "0.03"

        # When/Then: should raise TypeError
        with pytest.raises(TypeError, match="cost_per_1k_tokens must be numeric"):
            calculate_compression_roi(original_tokens, compressed_tokens, cost_per_1k_tokens)

    def test_should_raise_error_when_tokens_negative_in_roi(self) -> None:
        """Test that negative tokens raise ValueError in ROI."""
        # Given: negative tokens
        original_tokens = -1000
        compressed_tokens = 250
        cost_per_1k_tokens = 0.03

        # When/Then: should raise ValueError
        with pytest.raises(ValueError, match="Token counts must be non-negative"):
            calculate_compression_roi(original_tokens, compressed_tokens, cost_per_1k_tokens)

    def test_should_raise_error_when_cost_negative_in_roi(self) -> None:
        """Test that negative cost raises ValueError in ROI."""
        # Given: negative cost
        original_tokens = 1000
        compressed_tokens = 250
        cost_per_1k_tokens = -0.03

        # When/Then: should raise ValueError
        with pytest.raises(ValueError, match="cost_per_1k_tokens must be non-negative"):
            calculate_compression_roi(original_tokens, compressed_tokens, cost_per_1k_tokens)


class TestJSONExport:
    """Test JSON export functionality."""

    def test_should_export_valid_json_schema(self) -> None:
        """Test that exported JSON matches dashboard schema."""
        # Given: metrics data
        summary_stats = {
            "mmr_relevance": {"mean": 0.85, "std": 0.12},
            "compression_ratio": {"mean": 0.45, "std": 0.08},
        }
        radar_data = {
            "labels": ["mmr_relevance", "compression_ratio"],
            "values": [0.85, 0.45],
        }
        detailed_results = [
            {"test_id": 1, "mmr_score": 0.9, "compression": 0.5},
            {"test_id": 2, "mmr_score": 0.8, "compression": 0.4},
        ]
        execution_mode = "DEMO"

        # When: exporting to JSON
        output_path = Path("/tmp/test_memory_results.json")
        export_results_json(
            output_path,
            summary_stats,
            radar_data,
            detailed_results,
            execution_mode,
        )

        # Then: should create valid JSON file
        assert output_path.exists(), "JSON file should exist"
        with open(output_path) as f:
            data = json.load(f)
        assert data["version"] == "1.0"
        assert data["execution_mode"] == "DEMO"
        assert "created" in data
        assert "summary_statistics" in data
        assert "radar_chart_data" in data
        assert "detailed_results" in data

        # Cleanup
        output_path.unlink()

    def test_should_raise_error_when_output_path_invalid(self) -> None:
        """Test that invalid output path raises error."""
        # Given: invalid output path
        output_path = Path("/invalid/nonexistent/path/results.json")
        summary_stats = {}
        radar_data = {"labels": [], "values": []}
        detailed_results = []
        execution_mode = "DEMO"

        # When/Then: should raise error
        with pytest.raises((OSError, FileNotFoundError)):
            export_results_json(
                output_path,
                summary_stats,
                radar_data,
                detailed_results,
                execution_mode,
            )

    def test_should_validate_summary_statistics_structure(self) -> None:
        """Test that summary statistics must have mean/std."""
        # Given: invalid summary stats (missing std)
        summary_stats = {"mmr_relevance": {"mean": 0.85}}  # Missing 'std'
        radar_data = {"labels": ["mmr_relevance"], "values": [0.85]}
        detailed_results = []
        execution_mode = "DEMO"
        output_path = Path("/tmp/test_invalid.json")

        # When/Then: should raise ValueError
        with pytest.raises(ValueError, match="must contain 'mean' and 'std'"):
            export_results_json(
                output_path,
                summary_stats,
                radar_data,
                detailed_results,
                execution_mode,
            )

    def test_should_raise_error_when_output_path_not_path_object(self) -> None:
        """Test that non-Path output_path raises TypeError."""
        # Given: string instead of Path
        output_path = "/tmp/test.json"
        summary_stats = {"metric": {"mean": 0.85, "std": 0.12}}
        radar_data = {"labels": ["metric"], "values": [0.85]}
        detailed_results = []
        execution_mode = "DEMO"

        # When/Then: should raise TypeError
        with pytest.raises(TypeError, match="output_path must be a Path object"):
            export_results_json(output_path, summary_stats, radar_data, detailed_results, execution_mode)

    def test_should_raise_error_when_summary_stats_not_dict(self) -> None:
        """Test that non-dict summary_statistics raises TypeError."""
        # Given: list instead of dict
        output_path = Path("/tmp/test.json")
        summary_stats = []
        radar_data = {"labels": [], "values": []}
        detailed_results = []
        execution_mode = "DEMO"

        # When/Then: should raise TypeError
        with pytest.raises(TypeError, match="summary_statistics must be a dict"):
            export_results_json(output_path, summary_stats, radar_data, detailed_results, execution_mode)

    def test_should_raise_error_when_radar_data_not_dict(self) -> None:
        """Test that non-dict radar_chart_data raises TypeError."""
        # Given: list instead of dict
        output_path = Path("/tmp/test.json")
        summary_stats = {}
        radar_data = []
        detailed_results = []
        execution_mode = "DEMO"

        # When/Then: should raise TypeError
        with pytest.raises(TypeError, match="radar_chart_data must be a dict"):
            export_results_json(output_path, summary_stats, radar_data, detailed_results, execution_mode)

    def test_should_raise_error_when_detailed_results_not_list(self) -> None:
        """Test that non-list detailed_results raises TypeError."""
        # Given: dict instead of list
        output_path = Path("/tmp/test.json")
        summary_stats = {}
        radar_data = {"labels": [], "values": []}
        detailed_results = {}
        execution_mode = "DEMO"

        # When/Then: should raise TypeError
        with pytest.raises(TypeError, match="detailed_results must be a list"):
            export_results_json(output_path, summary_stats, radar_data, detailed_results, execution_mode)

    def test_should_raise_error_when_execution_mode_not_string(self) -> None:
        """Test that non-string execution_mode raises TypeError."""
        # Given: int instead of string
        output_path = Path("/tmp/test.json")
        summary_stats = {}
        radar_data = {"labels": [], "values": []}
        detailed_results = []
        execution_mode = 123

        # When/Then: should raise TypeError
        with pytest.raises(TypeError, match="execution_mode must be a string"):
            export_results_json(output_path, summary_stats, radar_data, detailed_results, execution_mode)

    def test_should_raise_error_when_radar_data_missing_labels(self) -> None:
        """Test that radar_chart_data without labels raises ValueError."""
        # Given: radar_data missing 'labels'
        output_path = Path("/tmp/test.json")
        summary_stats = {}
        radar_data = {"values": [0.85]}  # Missing 'labels'
        detailed_results = []
        execution_mode = "DEMO"

        # When/Then: should raise ValueError
        with pytest.raises(ValueError, match="radar_chart_data must contain 'labels' and 'values' keys"):
            export_results_json(output_path, summary_stats, radar_data, detailed_results, execution_mode)
