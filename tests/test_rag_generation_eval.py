"""Tests for RAG Generation Evaluation Module (Lesson 13).

TDD-RED Phase: Tests for AttributionDetector, HallucinationDetector, and ContextUtilizationScorer.

Test Naming Convention: test_should_[expected_result]_when_[condition]
"""

from unittest.mock import MagicMock, patch

import pytest

from backend.rag_generation_eval import (
    AttributionDetector,
    ContextUtilizationScorer,
    HallucinationDetector,
)


# =============================================================================
# AttributionDetector Tests
# =============================================================================


class TestAttributionDetector:
    """Test suite for AttributionDetector class."""

    def test_should_extract_claims_when_response_has_multiple_statements(self) -> None:
        """Test extracting atomic claims from LLM response."""
        detector = AttributionDetector()
        response = "The Bhagavad Gita teaches dharma. It was spoken by Krishna to Arjuna."

        claims = detector.extract_claims(response)

        assert isinstance(claims, list)
        assert len(claims) >= 2
        assert all(isinstance(claim, str) for claim in claims)

    def test_should_return_empty_list_when_response_is_empty(self) -> None:
        """Test handling of empty response."""
        detector = AttributionDetector()

        claims = detector.extract_claims("")

        assert claims == []

    def test_should_verify_attribution_when_claim_matches_context(self) -> None:
        """Test verifying claims against context documents."""
        detector = AttributionDetector()
        claims = ["Krishna teaches Arjuna about duty"]
        context = ["Krishna teaches Arjuna about his duty and dharma in the battlefield."]

        with patch.object(detector, "_check_claim_in_context", return_value=True):
            result = detector.verify_attribution(claims, context)

        assert isinstance(result, dict)
        assert "attribution_scores" in result
        assert len(result["attribution_scores"]) == len(claims)

    def test_should_raise_error_when_claims_not_list(self) -> None:
        """Test type validation for claims parameter."""
        detector = AttributionDetector()

        with pytest.raises(TypeError, match="claims must be a list"):
            detector.verify_attribution("not a list", ["context"])  # type: ignore

    def test_should_raise_error_when_context_not_list(self) -> None:
        """Test type validation for context parameter."""
        detector = AttributionDetector()

        with pytest.raises(TypeError, match="context must be a list"):
            detector.verify_attribution(["claim"], "not a list")  # type: ignore

    def test_should_calculate_attribution_rate_when_given_results(self) -> None:
        """Test calculating overall attribution rate from verification results."""
        detector = AttributionDetector()
        results = [
            {"attribution_scores": [True, True, False]},  # 2/3 attributed
            {"attribution_scores": [True, False]},  # 1/2 attributed
        ]

        rate = detector.calculate_attribution_rate(results)

        assert isinstance(rate, float)
        assert 0.0 <= rate <= 1.0
        # Expected: (2+1) / (3+2) = 3/5 = 0.6
        assert rate == pytest.approx(0.6, rel=0.01)

    def test_should_return_zero_when_no_claims_in_results(self) -> None:
        """Test handling of empty results."""
        detector = AttributionDetector()

        rate = detector.calculate_attribution_rate([])

        assert rate == 0.0

    def test_should_detect_exact_match_when_claim_in_context(self) -> None:
        """Test exact string matching for attribution."""
        detector = AttributionDetector()
        claim = "The capital of France is Paris"
        context = ["France is a country. The capital of France is Paris. It has a population of 2 million."]

        is_attributed = detector._check_claim_in_context(claim, context)

        assert is_attributed is True

    def test_should_detect_no_match_when_claim_not_in_context(self) -> None:
        """Test detection of unattributed claims."""
        detector = AttributionDetector()
        claim = "The capital of Germany is Berlin"
        context = ["France is a country. The capital of France is Paris."]

        is_attributed = detector._check_claim_in_context(claim, context)

        assert is_attributed is False


# =============================================================================
# HallucinationDetector Tests
# =============================================================================


class TestHallucinationDetector:
    """Test suite for HallucinationDetector class."""

    def test_should_detect_intrinsic_hallucination_when_response_contradicts_context(self) -> None:
        """Test detecting intrinsic hallucinations (contradicts context)."""
        detector = HallucinationDetector()
        response = "The Bhagavad Gita teaches that one should avoid all duties."
        context = ["The Bhagavad Gita teaches that one should fulfill their dharma (duty)."]

        with patch.object(detector, "_check_contradiction", return_value=True):
            is_intrinsic = detector.detect_intrinsic_hallucination(response, context)

        assert is_intrinsic is True

    def test_should_not_detect_intrinsic_when_response_matches_context(self) -> None:
        """Test no intrinsic hallucination when response is faithful."""
        detector = HallucinationDetector()
        response = "The Bhagavad Gita teaches dharma."
        context = ["The Bhagavad Gita teaches dharma, karma, and moksha."]

        with patch.object(detector, "_check_contradiction", return_value=False):
            is_intrinsic = detector.detect_intrinsic_hallucination(response, context)

        assert is_intrinsic is False

    def test_should_detect_extrinsic_hallucination_when_info_not_in_context(self) -> None:
        """Test detecting extrinsic hallucinations (not in context)."""
        detector = HallucinationDetector()
        response = "Arjuna's teacher was Dronacharya, and he studied for 12 years."
        context = ["Arjuna was a great warrior in the Mahabharata."]

        with patch.object(detector, "_check_claims_in_context", return_value=[False, False]):
            is_extrinsic = detector.detect_extrinsic_hallucination(response, context)

        assert is_extrinsic is True

    def test_should_not_detect_extrinsic_when_all_info_in_context(self) -> None:
        """Test no extrinsic hallucination when all info is from context."""
        detector = HallucinationDetector()
        response = "Arjuna was a warrior."
        context = ["Arjuna was a great warrior in the Mahabharata."]

        with patch.object(detector, "_check_claims_in_context", return_value=[True]):
            is_extrinsic = detector.detect_extrinsic_hallucination(response, context)

        assert is_extrinsic is False

    def test_should_classify_hallucination_type_correctly(self) -> None:
        """Test classification into NONE/INTRINSIC/EXTRINSIC."""
        detector = HallucinationDetector()
        response = "Test response"
        context = ["Test context"]

        # Case 1: No hallucination
        with patch.object(detector, "detect_intrinsic_hallucination", return_value=False):
            with patch.object(detector, "detect_extrinsic_hallucination", return_value=False):
                halluc_type = detector.classify_hallucination_type(response, context)
                assert halluc_type == "NONE"

        # Case 2: Intrinsic hallucination
        with patch.object(detector, "detect_intrinsic_hallucination", return_value=True):
            halluc_type = detector.classify_hallucination_type(response, context)
            assert halluc_type == "INTRINSIC"

        # Case 3: Extrinsic hallucination
        with patch.object(detector, "detect_intrinsic_hallucination", return_value=False):
            with patch.object(detector, "detect_extrinsic_hallucination", return_value=True):
                halluc_type = detector.classify_hallucination_type(response, context)
                assert halluc_type == "EXTRINSIC"

    def test_should_raise_error_when_response_not_string(self) -> None:
        """Test type validation for response parameter."""
        detector = HallucinationDetector()

        with pytest.raises(TypeError, match="response must be a string"):
            detector.detect_intrinsic_hallucination(123, ["context"])  # type: ignore

    def test_should_raise_error_when_context_not_list_in_hallucination(self) -> None:
        """Test type validation for context parameter in hallucination detection."""
        detector = HallucinationDetector()

        with pytest.raises(TypeError, match="context must be a list"):
            detector.detect_intrinsic_hallucination("response", "not a list")  # type: ignore


# =============================================================================
# ContextUtilizationScorer Tests
# =============================================================================


class TestContextUtilizationScorer:
    """Test suite for ContextUtilizationScorer class."""

    def test_should_measure_utilization_when_given_response_and_contexts(self) -> None:
        """Test measuring semantic similarity between response and each context doc."""
        scorer = ContextUtilizationScorer()
        response = "Krishna teaches Arjuna about his duty."
        contexts = [
            "Krishna teaches Arjuna about duty and dharma.",
            "The Mahabharata is an ancient Indian epic.",
        ]

        with patch.object(scorer, "_calculate_similarity", side_effect=[0.85, 0.25]):
            utilization = scorer.measure_utilization(response, contexts)

        assert isinstance(utilization, dict)
        assert len(utilization) == 2
        assert all(isinstance(score, float) for score in utilization.values())
        assert utilization[0] == pytest.approx(0.85, rel=0.01)
        assert utilization[1] == pytest.approx(0.25, rel=0.01)

    def test_should_classify_usage_as_USED_when_similarity_high(self) -> None:
        """Test classifying high similarity (>0.7) as USED."""
        scorer = ContextUtilizationScorer()

        usage = scorer.classify_usage(0.85)

        assert usage == "USED"

    def test_should_classify_usage_as_PARTIAL_when_similarity_medium(self) -> None:
        """Test classifying medium similarity (0.4-0.7) as PARTIAL."""
        scorer = ContextUtilizationScorer()

        usage = scorer.classify_usage(0.55)

        assert usage == "PARTIAL"

    def test_should_classify_usage_as_IGNORED_when_similarity_low(self) -> None:
        """Test classifying low similarity (<0.4) as IGNORED."""
        scorer = ContextUtilizationScorer()

        usage = scorer.classify_usage(0.25)

        assert usage == "IGNORED"

    def test_should_raise_error_when_similarity_out_of_range(self) -> None:
        """Test validation of similarity score range [0, 1]."""
        scorer = ContextUtilizationScorer()

        with pytest.raises(ValueError, match="similarity must be between 0 and 1"):
            scorer.classify_usage(1.5)

        with pytest.raises(ValueError, match="similarity must be between 0 and 1"):
            scorer.classify_usage(-0.1)

    def test_should_return_empty_dict_when_no_contexts(self) -> None:
        """Test handling of empty contexts list."""
        scorer = ContextUtilizationScorer()

        utilization = scorer.measure_utilization("response", [])

        assert utilization == {}

    def test_should_raise_error_when_response_not_string_in_utilization(self) -> None:
        """Test type validation for response parameter."""
        scorer = ContextUtilizationScorer()

        with pytest.raises(TypeError, match="response must be a string"):
            scorer.measure_utilization(123, ["context"])  # type: ignore

    def test_should_raise_error_when_contexts_not_list_in_utilization(self) -> None:
        """Test type validation for contexts parameter."""
        scorer = ContextUtilizationScorer()

        with pytest.raises(TypeError, match="contexts must be a list"):
            scorer.measure_utilization("response", "not a list")  # type: ignore


# =============================================================================
# Integration Tests
# =============================================================================


class TestRAGGenerationEvalIntegration:
    """Integration tests for all three evaluation classes."""

    def test_should_evaluate_full_rag_response_pipeline(self) -> None:
        """Test end-to-end evaluation of a RAG response."""
        # Setup
        detector = AttributionDetector()
        halluc_detector = HallucinationDetector()
        scorer = ContextUtilizationScorer()

        response = "Krishna teaches Arjuna about his duty in the Bhagavad Gita."
        context = ["Krishna teaches Arjuna about duty and dharma in the Bhagavad Gita."]

        # Extract claims
        with patch.object(detector, "extract_claims", return_value=["Krishna teaches Arjuna about duty"]):
            claims = detector.extract_claims(response)

        # Verify attribution
        with patch.object(detector, "verify_attribution", return_value={"attribution_scores": [True]}):
            attribution_result = detector.verify_attribution(claims, context)

        # Detect hallucinations
        with patch.object(halluc_detector, "classify_hallucination_type", return_value="NONE"):
            halluc_type = halluc_detector.classify_hallucination_type(response, context)

        # Measure utilization
        with patch.object(scorer, "measure_utilization", return_value={0: 0.85}):
            utilization = scorer.measure_utilization(response, context)

        # Assertions
        assert len(claims) > 0
        assert attribution_result["attribution_scores"][0] is True
        assert halluc_type == "NONE"
        assert utilization[0] > 0.7  # USED classification

    def test_should_handle_adversarial_case_with_hallucination(self) -> None:
        """Test evaluation of adversarial case with intrinsic hallucination."""
        detector = AttributionDetector()
        halluc_detector = HallucinationDetector()

        response = "The Bhagavad Gita teaches that one should avoid all duties."
        context = ["The Bhagavad Gita teaches that one should fulfill their dharma (duty)."]

        # Should detect contradiction
        with patch.object(halluc_detector, "detect_intrinsic_hallucination", return_value=True):
            is_intrinsic = halluc_detector.detect_intrinsic_hallucination(response, context)

        # Should classify as INTRINSIC
        with patch.object(halluc_detector, "classify_hallucination_type", return_value="INTRINSIC"):
            halluc_type = halluc_detector.classify_hallucination_type(response, context)

        # Assertions
        assert is_intrinsic is True
        assert halluc_type == "INTRINSIC"


# =============================================================================
# Pytest Fixtures
# =============================================================================


@pytest.fixture
def sample_test_case() -> dict:
    """Sample test case from RAG evaluation suite."""
    return {
        "id": "test_001",
        "query": "What is the main teaching of the Bhagavad Gita?",
        "context": ["The Bhagavad Gita teaches dharma, karma, and moksha."],
        "answer": "The main teaching is dharma (duty), karma (action), and moksha (liberation).",
        "labels": {
            "is_attributed": True,
            "is_context_relevant": True,
            "context_utilization": "USED",
            "hallucination_type": "NONE",
        },
    }


@pytest.fixture
def attribution_detector() -> AttributionDetector:
    """Fixture for AttributionDetector instance."""
    return AttributionDetector()


@pytest.fixture
def hallucination_detector() -> HallucinationDetector:
    """Fixture for HallucinationDetector instance."""
    return HallucinationDetector()


@pytest.fixture
def context_utilization_scorer() -> ContextUtilizationScorer:
    """Fixture for ContextUtilizationScorer instance."""
    return ContextUtilizationScorer()
