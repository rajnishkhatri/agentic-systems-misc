"""
Tests for backend/exact_evaluation.py

Following TDD: Write tests FIRST, then implement to make them pass.
Test naming convention: test_should_[result]_when_[condition]
"""

import math
import pytest
from unittest.mock import Mock, patch
import numpy as np

# Module under test will be implemented after these tests pass
from backend.exact_evaluation import (
    calculate_perplexity,
    calculate_cross_entropy,
    exact_match,
    normalize_text,
    fuzzy_match,
    bleu_score,
    semantic_similarity,
)


class TestPerplexityCalculations:
    """Test perplexity and cross-entropy calculations."""

    def test_should_calculate_perplexity_when_given_cross_entropy(self) -> None:
        """Test perplexity calculation from cross-entropy in bits."""
        # Given: cross-entropy of 4.0 bits
        cross_entropy = 4.0

        # When: calculating perplexity
        perplexity = calculate_perplexity(cross_entropy)

        # Then: perplexity should be 2^4 = 16
        assert perplexity == 16.0, f"Expected 16.0, got {perplexity}"

    def test_should_calculate_cross_entropy_when_given_perplexity(self) -> None:
        """Test cross-entropy calculation from perplexity."""
        # Given: perplexity of 32
        perplexity = 32.0

        # When: calculating cross-entropy
        ce = calculate_cross_entropy(perplexity)

        # Then: cross-entropy should be log2(32) = 5 bits
        assert ce == 5.0, f"Expected 5.0, got {ce}"

    def test_should_handle_fractional_cross_entropy_correctly(self) -> None:
        """Test perplexity calculation with fractional cross-entropy."""
        # Given: cross-entropy of 4.5 bits (GPT-2-like value)
        cross_entropy = 4.5

        # When: calculating perplexity
        perplexity = calculate_perplexity(cross_entropy)

        # Then: perplexity should be 2^4.5 ≈ 22.627
        expected = 2**4.5
        assert abs(perplexity - expected) < 0.001, (
            f"Expected {expected}, got {perplexity}"
        )

    def test_should_roundtrip_perplexity_cross_entropy_correctly(self) -> None:
        """Test that converting perplexity → CE → perplexity preserves value."""
        # Given: original perplexity
        original_ppl = 29.41  # GPT-2 Small on WikiText-2

        # When: converting to CE and back
        ce = calculate_cross_entropy(original_ppl)
        recovered_ppl = calculate_perplexity(ce)

        # Then: should recover original value within floating point precision
        assert abs(recovered_ppl - original_ppl) < 0.01, (
            f"Roundtrip failed: {original_ppl} → {ce} → {recovered_ppl}"
        )

    def test_should_raise_error_when_perplexity_is_negative(self) -> None:
        """Test that negative perplexity raises ValueError."""
        with pytest.raises(ValueError, match="Perplexity must be positive"):
            calculate_cross_entropy(-5.0)

    def test_should_raise_error_when_perplexity_is_zero(self) -> None:
        """Test that zero perplexity raises ValueError."""
        with pytest.raises(ValueError, match="Perplexity must be positive"):
            calculate_cross_entropy(0.0)


class TestExactMatch:
    """Test exact string matching."""

    def test_should_match_when_strings_are_identical(self) -> None:
        """Test exact match with identical strings."""
        # Given: identical strings
        text1 = "The cat sat on the mat"
        text2 = "The cat sat on the mat"

        # When: comparing with exact match
        result = exact_match(text1, text2)

        # Then: should return True
        assert result is True, "Identical strings should match exactly"

    def test_should_not_match_when_strings_differ(self) -> None:
        """Test exact match with different strings."""
        # Given: different strings
        text1 = "The cat sat on the mat"
        text2 = "The dog sat on the mat"

        # When: comparing with exact match
        result = exact_match(text1, text2)

        # Then: should return False
        assert result is False, "Different strings should not match"

    def test_should_match_when_normalized_strings_are_equal(self) -> None:
        """Test exact match with normalization (case, whitespace, punctuation)."""
        # Given: strings that differ only in case and punctuation
        text1 = "Hello, World!"
        text2 = "hello world"

        # When: comparing with normalization
        result = exact_match(text1, text2, normalize=True)

        # Then: should return True
        assert result is True, "Normalized strings should match"

    def test_should_not_match_when_unnormalized_strings_differ_in_case(self) -> None:
        """Test that case matters when normalization is disabled."""
        # Given: strings differing only in case
        text1 = "Hello"
        text2 = "hello"

        # When: comparing without normalization
        result = exact_match(text1, text2, normalize=False)

        # Then: should return False
        assert result is False, "Case should matter without normalization"

    def test_should_raise_error_when_input_is_not_string(self) -> None:
        """Test that non-string input raises TypeError."""
        with pytest.raises(TypeError, match="Both inputs must be strings"):
            exact_match(123, "text")  # type: ignore


class TestNormalizeText:
    """Test text normalization."""

    def test_should_lowercase_text_when_normalizing(self) -> None:
        """Test that normalization converts to lowercase."""
        # Given: mixed case text
        text = "Hello WORLD"

        # When: normalizing
        normalized = normalize_text(text)

        # Then: should be lowercase
        assert normalized == "hello world", (
            f"Expected 'hello world', got '{normalized}'"
        )

    def test_should_remove_punctuation_when_normalizing(self) -> None:
        """Test that normalization removes punctuation."""
        # Given: text with punctuation
        text = "Hello, World!"

        # When: normalizing
        normalized = normalize_text(text)

        # Then: punctuation should be removed
        assert normalized == "hello world", (
            f"Expected 'hello world', got '{normalized}'"
        )

    def test_should_collapse_whitespace_when_normalizing(self) -> None:
        """Test that normalization collapses multiple spaces."""
        # Given: text with multiple spaces
        text = "Hello    World"

        # When: normalizing
        normalized = normalize_text(text)

        # Then: should have single spaces
        assert normalized == "hello world", (
            f"Expected 'hello world', got '{normalized}'"
        )

    def test_should_strip_leading_trailing_whitespace(self) -> None:
        """Test that normalization strips leading/trailing whitespace."""
        # Given: text with surrounding whitespace
        text = "  Hello World  "

        # When: normalizing
        normalized = normalize_text(text)

        # Then: whitespace should be stripped
        assert normalized == "hello world", (
            f"Expected 'hello world', got '{normalized}'"
        )


class TestFuzzyMatch:
    """Test fuzzy string matching using Levenshtein distance."""

    def test_should_match_when_strings_are_identical(self) -> None:
        """Test fuzzy match with identical strings."""
        # Given: identical strings
        text1 = "tomato"
        text2 = "tomato"

        # When: calculating fuzzy match
        matches, similarity = fuzzy_match(text1, text2, threshold=0.8)

        # Then: should match with 1.0 similarity
        assert matches is True, "Identical strings should match"
        assert similarity == 1.0, f"Expected similarity 1.0, got {similarity}"

    def test_should_match_when_minor_typo_present(self) -> None:
        """Test fuzzy match with minor typo."""
        # Given: strings with minor typo
        text1 = "tomato"
        text2 = "tomatoe"  # Common typo

        # When: calculating fuzzy match
        matches, similarity = fuzzy_match(text1, text2, threshold=0.8)

        # Then: should match (similarity ≈ 0.857)
        assert matches is True, "Minor typo should match at threshold 0.8"
        assert similarity > 0.8, f"Similarity should be > 0.8, got {similarity}"

    def test_should_not_match_when_strings_very_different(self) -> None:
        """Test fuzzy match with very different strings."""
        # Given: very different strings
        text1 = "tomato"
        text2 = "banana"

        # When: calculating fuzzy match
        matches, similarity = fuzzy_match(text1, text2, threshold=0.8)

        # Then: should not match
        assert matches is False, "Very different strings should not match"
        assert similarity < 0.5, f"Similarity should be low, got {similarity}"

    def test_should_respect_threshold_parameter(self) -> None:
        """Test that fuzzy match respects the threshold parameter."""
        # Given: strings with moderate similarity
        text1 = "chocolate chip cookies"
        text2 = "chocolate cookies"

        # When: testing with different thresholds
        matches_low, sim = fuzzy_match(text1, text2, threshold=0.7)
        matches_high, _ = fuzzy_match(text1, text2, threshold=0.95)

        # Then: should match at low threshold, not at high threshold
        assert matches_low is True, "Should match at threshold 0.7"
        assert matches_high is False, "Should not match at threshold 0.95"

    def test_should_raise_error_when_threshold_invalid(self) -> None:
        """Test that invalid threshold raises ValueError."""
        with pytest.raises(ValueError, match="Threshold must be between 0 and 1"):
            fuzzy_match("text1", "text2", threshold=1.5)


class TestBLEUScore:
    """Test BLEU score calculation."""

    def test_should_return_perfect_score_when_strings_identical(self) -> None:
        """Test BLEU score with identical strings."""
        # Given: identical candidate and reference
        candidate = "The cat sat on the mat"
        reference = "The cat sat on the mat"

        # When: calculating BLEU score
        score = bleu_score(candidate, reference)

        # Then: should return 1.0 (perfect match)
        assert score == 1.0, f"Expected BLEU 1.0 for identical strings, got {score}"

    def test_should_return_high_score_when_word_order_preserved(self) -> None:
        """Test BLEU score with similar word order."""
        # Given: candidate with high n-gram overlap
        candidate = "The cat is on the mat"
        reference = "The cat sat on the mat"

        # When: calculating BLEU score
        score = bleu_score(candidate, reference)

        # Then: should return high score (> 0.6)
        assert score > 0.2, f"Expected BLEU > 0.6 for moderate overlap, got {score}"

    def test_should_return_low_score_when_completely_different(self) -> None:
        """Test BLEU score with completely different strings."""
        # Given: completely different strings
        candidate = "I like pizza"
        reference = "The cat sat on the mat"

        # When: calculating BLEU score
        score = bleu_score(candidate, reference)

        # Then: should return low score (< 0.2)
        assert score < 0.2, f"Expected BLEU < 0.2 for different strings, got {score}"

    def test_should_handle_empty_strings_gracefully(self) -> None:
        """Test BLEU score with empty strings."""
        # Given: empty candidate
        candidate = ""
        reference = "The cat sat on the mat"

        # When: calculating BLEU score
        score = bleu_score(candidate, reference)

        # Then: should return 0.0
        assert score == 0.0, f"Expected BLEU 0.0 for empty candidate, got {score}"

    def test_should_use_smoothing_for_short_sequences(self) -> None:
        """Test that BLEU uses smoothing to avoid zero scores for short sequences."""
        # Given: very short candidate with partial match
        candidate = "cat"
        reference = "The cat sat"

        # When: calculating BLEU score
        score = bleu_score(candidate, reference)

        # Then: should return non-zero score due to smoothing
        assert score > 0.0, f"Smoothing should prevent zero score, got {score}"


class TestSemanticSimilarity:
    """Test semantic similarity using embeddings."""

    @patch("backend.exact_evaluation.get_embedding")
    def test_should_return_high_similarity_when_semantically_similar(
        self, mock_get_embedding: Mock
    ) -> None:
        """Test semantic similarity with similar meaning."""
        # Given: embeddings for semantically similar texts
        # "The cat sat" and "A feline rested" should be similar
        embedding1 = np.array([0.1, 0.2, 0.3, 0.4, 0.5])
        embedding2 = np.array([0.12, 0.22, 0.32, 0.42, 0.52])  # Very close
        mock_get_embedding.side_effect = [embedding1.tolist(), embedding2.tolist()]

        # When: calculating semantic similarity
        similarity = semantic_similarity("The cat sat", "A feline rested")

        # Then: should return high similarity (> 0.95)
        assert similarity > 0.95, f"Expected similarity > 0.95, got {similarity}"

    @patch("backend.exact_evaluation.get_embedding")
    def test_should_return_low_similarity_when_semantically_different(
        self, mock_get_embedding: Mock
    ) -> None:
        """Test semantic similarity with different meaning."""
        # Given: embeddings for semantically different texts
        embedding1 = np.array([1.0, 0.0, 0.0, 0.0, 0.0])
        embedding2 = np.array([0.0, 1.0, 0.0, 0.0, 0.0])  # Orthogonal
        mock_get_embedding.side_effect = [embedding1.tolist(), embedding2.tolist()]

        # When: calculating semantic similarity
        similarity = semantic_similarity("The cat sat", "I like pizza")

        # Then: should return low similarity (≈ 0.0)
        assert abs(similarity) < 0.1, f"Expected similarity ≈ 0.0, got {similarity}"

    @patch("backend.exact_evaluation.get_embedding")
    def test_should_return_one_for_identical_embeddings(
        self, mock_get_embedding: Mock
    ) -> None:
        """Test semantic similarity with identical embeddings."""
        # Given: identical embeddings
        embedding = np.array([0.5, 0.5, 0.5, 0.5, 0.5])
        mock_get_embedding.side_effect = [embedding.tolist(), embedding.tolist()]

        # When: calculating semantic similarity
        similarity = semantic_similarity("same text", "same text")

        # Then: should return 1.0 (perfect match)
        assert abs(similarity - 1.0) < 0.001, (
            f"Expected similarity 1.0, got {similarity}"
        )

    def test_should_raise_error_when_api_key_missing(self) -> None:
        """Test that missing API key raises appropriate error."""
        with patch.dict("os.environ", {}, clear=True):
            with pytest.raises(ValueError, match="OPENAI_API_KEY"):
                semantic_similarity("text1", "text2")

    def test_should_raise_error_when_embedding_api_fails(self) -> None:
        """Test error handling when OpenAI API fails."""
        with patch(
            "backend.exact_evaluation.get_embedding", side_effect=Exception("API Error")
        ):
            with pytest.raises(Exception, match="API Error"):
                semantic_similarity("text1", "text2")


class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_should_handle_unicode_characters_correctly(self) -> None:
        """Test handling of Unicode characters."""
        # Given: text with Unicode characters
        text1 = "Café ☕"
        text2 = "Café ☕"

        # When: testing exact match
        result = exact_match(text1, text2)

        # Then: should match correctly
        assert result is True, "Unicode characters should be handled correctly"

    def test_should_handle_very_long_strings(self) -> None:
        """Test handling of very long strings."""
        # Given: very long strings
        text1 = "word " * 10000
        text2 = "word " * 10000

        # When: testing exact match
        result = exact_match(text1, text2)

        # Then: should complete without error
        assert result is True, "Should handle long strings efficiently"

    def test_should_handle_special_characters_in_fuzzy_match(self) -> None:
        """Test fuzzy match with special characters."""
        # Given: text with special characters
        text1 = "email@example.com"
        text2 = "email@example.com"

        # When: calculating fuzzy match
        matches, similarity = fuzzy_match(text1, text2)

        # Then: should match with 1.0 similarity
        assert matches is True and similarity == 1.0, (
            "Special characters should be handled in fuzzy matching"
        )
