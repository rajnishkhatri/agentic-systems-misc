"""Tests for RAG Pipeline Evaluator (Lesson 13).

TDD-RED Phase: Tests for end-to-end RAG evaluation combining retrieval + generation metrics.

Test Naming Convention: test_should_[expected_result]_when_[condition]
"""

from unittest.mock import MagicMock, patch

import pytest

from backend.rag_pipeline_eval import RAGPipelineEvaluator


# =============================================================================
# RAGPipelineEvaluator Tests
# =============================================================================


class TestRAGPipelineEvaluator:
    """Test suite for end-to-end RAG pipeline evaluator."""

    def test_should_initialize_with_default_config(self) -> None:
        """Test initialization with default configuration."""
        evaluator = RAGPipelineEvaluator()

        assert evaluator is not None
        assert hasattr(evaluator, "evaluate_pipeline")

    def test_should_evaluate_retrieval_quality_when_given_test_case(self) -> None:
        """Test retrieval quality evaluation (Recall@k, MRR, Precision)."""
        evaluator = RAGPipelineEvaluator()

        test_case = {
            "query": "What is dharma?",
            "retrieved_docs": ["Doc about dharma", "Doc about karma", "Irrelevant doc"],
            "relevant_docs": ["Doc about dharma"],
        }

        retrieval_metrics = evaluator.evaluate_retrieval(test_case)

        assert isinstance(retrieval_metrics, dict)
        assert "recall_at_k" in retrieval_metrics
        assert "precision" in retrieval_metrics
        assert "mrr" in retrieval_metrics

    def test_should_evaluate_generation_quality_when_given_response(self) -> None:
        """Test generation quality evaluation (attribution, hallucination, utilization)."""
        evaluator = RAGPipelineEvaluator()

        test_case = {
            "query": "What is dharma?",
            "context": ["Dharma means duty and righteousness."],
            "response": "Dharma means duty.",
        }

        generation_metrics = evaluator.evaluate_generation(test_case)

        assert isinstance(generation_metrics, dict)
        assert "attribution_rate" in generation_metrics
        assert "hallucination_type" in generation_metrics
        assert "context_utilization" in generation_metrics

    def test_should_evaluate_end_to_end_pipeline(self) -> None:
        """Test complete RAG pipeline evaluation (retrieval + generation)."""
        evaluator = RAGPipelineEvaluator()

        test_case = {
            "query": "What is dharma?",
            "retrieved_docs": ["Doc about dharma"],
            "relevant_docs": ["Doc about dharma"],
            "context": ["Dharma means duty and righteousness."],
            "response": "Dharma means duty.",
        }

        pipeline_metrics = evaluator.evaluate_pipeline(test_case)

        assert isinstance(pipeline_metrics, dict)
        assert "retrieval" in pipeline_metrics
        assert "generation" in pipeline_metrics
        assert "overall_score" in pipeline_metrics

    def test_should_calculate_overall_score_combining_metrics(self) -> None:
        """Test overall score calculation (weighted combination of retrieval + generation)."""
        evaluator = RAGPipelineEvaluator()

        retrieval_metrics = {"recall_at_k": 0.8, "precision": 0.6}
        generation_metrics = {"attribution_rate": 0.9, "hallucination_type": "NONE"}

        overall_score = evaluator._calculate_overall_score(retrieval_metrics, generation_metrics)

        assert isinstance(overall_score, float)
        assert 0.0 <= overall_score <= 1.0

    def test_should_identify_failure_mode_when_retrieval_fails(self) -> None:
        """Test identifying failure mode when retrieval is poor."""
        evaluator = RAGPipelineEvaluator()

        test_case = {
            "query": "What is dharma?",
            "retrieved_docs": ["Irrelevant doc 1", "Irrelevant doc 2"],
            "relevant_docs": ["Doc about dharma"],
            "context": ["Unrelated content"],
            "response": "I don't know what dharma is.",
        }

        failure_mode = evaluator.identify_failure_mode(test_case)

        assert failure_mode == "RETRIEVAL_FAILURE"

    def test_should_identify_failure_mode_when_generation_hallucinates(self) -> None:
        """Test identifying failure mode when generation hallucinates."""
        evaluator = RAGPipelineEvaluator()

        test_case = {
            "query": "What is dharma?",
            "retrieved_docs": ["Doc about dharma"],
            "relevant_docs": ["Doc about dharma"],
            "context": ["Dharma means duty."],
            "response": "Dharma means pleasure and wealth.",  # Hallucination
        }

        failure_mode = evaluator.identify_failure_mode(test_case)

        assert failure_mode == "GENERATION_FAILURE"

    def test_should_identify_no_failure_when_pipeline_works_correctly(self) -> None:
        """Test no failure when both retrieval and generation are good."""
        evaluator = RAGPipelineEvaluator()

        test_case = {
            "query": "What is dharma?",
            "retrieved_docs": ["Doc about dharma"],
            "relevant_docs": ["Doc about dharma"],
            "context": ["Dharma means duty and righteousness."],
            "response": "Dharma means duty and righteousness.",
        }

        failure_mode = evaluator.identify_failure_mode(test_case)

        assert failure_mode == "NONE"

    def test_should_raise_error_when_test_case_missing_required_fields(self) -> None:
        """Test validation of required test case fields."""
        evaluator = RAGPipelineEvaluator()

        incomplete_test_case = {"query": "What is dharma?"}  # Missing other fields

        with pytest.raises(ValueError, match="test_case must contain"):
            evaluator.evaluate_pipeline(incomplete_test_case)

    def test_should_raise_error_when_test_case_not_dict(self) -> None:
        """Test type validation for test_case parameter."""
        evaluator = RAGPipelineEvaluator()

        with pytest.raises(TypeError, match="test_case must be a dict"):
            evaluator.evaluate_pipeline("not a dict")  # type: ignore

    def test_should_handle_batch_evaluation_of_multiple_test_cases(self) -> None:
        """Test evaluating multiple test cases in batch."""
        evaluator = RAGPipelineEvaluator()

        test_cases = [
            {
                "query": "What is dharma?",
                "retrieved_docs": ["Doc about dharma"],
                "relevant_docs": ["Doc about dharma"],
                "context": ["Dharma means duty."],
                "response": "Dharma means duty.",
            },
            {
                "query": "What is karma?",
                "retrieved_docs": ["Doc about karma"],
                "relevant_docs": ["Doc about karma"],
                "context": ["Karma means action."],
                "response": "Karma means action.",
            },
        ]

        batch_results = evaluator.evaluate_batch(test_cases)

        assert isinstance(batch_results, list)
        assert len(batch_results) == 2
        assert all("retrieval" in result for result in batch_results)
        assert all("generation" in result for result in batch_results)

    def test_should_generate_evaluation_report_with_summary_statistics(self) -> None:
        """Test generating evaluation report with aggregate statistics."""
        evaluator = RAGPipelineEvaluator()

        batch_results = [
            {"retrieval": {"recall_at_k": 0.8}, "generation": {"attribution_rate": 0.9}, "overall_score": 0.85},
            {"retrieval": {"recall_at_k": 0.6}, "generation": {"attribution_rate": 0.7}, "overall_score": 0.65},
        ]

        report = evaluator.generate_report(batch_results)

        assert isinstance(report, dict)
        assert "summary" in report
        assert "avg_retrieval_recall" in report["summary"]
        assert "avg_attribution_rate" in report["summary"]
        assert "avg_overall_score" in report["summary"]

    def test_should_integrate_with_hw4_retrieval_metrics(self) -> None:
        """Test integration with existing HW4 BM25 retrieval metrics."""
        evaluator = RAGPipelineEvaluator()

        # Simulate HW4-style test case with BM25 results
        test_case = {
            "query": "chocolate chip cookies recipe",
            "retrieved_docs": ["Recipe 1", "Recipe 2", "Recipe 3"],
            "relevant_docs": ["Recipe 1"],
            "bm25_scores": [10.5, 7.2, 3.1],
            "context": ["Recipe 1: Mix flour, sugar, butter..."],
            "response": "To make cookies, mix flour, sugar, and butter.",
        }

        pipeline_metrics = evaluator.evaluate_pipeline(test_case)

        # Should include BM25-specific metrics from HW4
        assert "retrieval" in pipeline_metrics
        assert isinstance(pipeline_metrics["retrieval"], dict)

    def test_should_calculate_context_precision_for_retrieved_docs(self) -> None:
        """Test context precision calculation (% of retrieved docs that are relevant)."""
        evaluator = RAGPipelineEvaluator()

        test_case = {
            "query": "What is dharma?",
            "retrieved_docs": ["Relevant doc", "Irrelevant doc", "Another irrelevant"],
            "relevant_docs": ["Relevant doc"],
        }

        retrieval_metrics = evaluator.evaluate_retrieval(test_case)

        assert "precision" in retrieval_metrics
        # Expected: 1/3 = 0.333...
        assert retrieval_metrics["precision"] == pytest.approx(0.333, rel=0.01)

    def test_should_calculate_context_recall_for_retrieved_docs(self) -> None:
        """Test context recall calculation (% of relevant docs that were retrieved)."""
        evaluator = RAGPipelineEvaluator()

        test_case = {
            "query": "What is dharma?",
            "retrieved_docs": ["Relevant doc 1", "Irrelevant doc"],
            "relevant_docs": ["Relevant doc 1", "Relevant doc 2"],
        }

        retrieval_metrics = evaluator.evaluate_retrieval(test_case)

        assert "recall_at_k" in retrieval_metrics
        # Expected: 1/2 = 0.5
        assert retrieval_metrics["recall_at_k"] == pytest.approx(0.5, rel=0.01)


# =============================================================================
# Integration Tests with RAG Generation Eval
# =============================================================================


class TestRAGPipelineIntegration:
    """Integration tests between RAGPipelineEvaluator and RAG generation eval module."""

    def test_should_use_attribution_detector_for_generation_metrics(self) -> None:
        """Test that pipeline uses AttributionDetector internally."""
        evaluator = RAGPipelineEvaluator()

        test_case = {
            "query": "What is dharma?",
            "context": ["Dharma means duty."],
            "response": "Dharma means duty.",
        }

        with patch("backend.rag_pipeline_eval.AttributionDetector") as mock_detector:
            mock_instance = MagicMock()
            mock_instance.extract_claims.return_value = ["Dharma means duty"]
            mock_instance.verify_attribution.return_value = {"attribution_scores": [True]}
            mock_detector.return_value = mock_instance

            generation_metrics = evaluator.evaluate_generation(test_case)

            # Should have called AttributionDetector methods
            assert "attribution_rate" in generation_metrics

    def test_should_use_hallucination_detector_for_generation_metrics(self) -> None:
        """Test that pipeline uses HallucinationDetector internally."""
        evaluator = RAGPipelineEvaluator()

        test_case = {
            "query": "What is dharma?",
            "context": ["Dharma means duty."],
            "response": "Dharma means pleasure.",  # Hallucination
        }

        with patch("backend.rag_pipeline_eval.HallucinationDetector") as mock_detector:
            mock_instance = MagicMock()
            mock_instance.classify_hallucination_type.return_value = "INTRINSIC"
            mock_detector.return_value = mock_instance

            generation_metrics = evaluator.evaluate_generation(test_case)

            # Should have called HallucinationDetector methods
            assert generation_metrics["hallucination_type"] == "INTRINSIC"

    def test_should_use_context_utilization_scorer_for_generation_metrics(self) -> None:
        """Test that pipeline uses ContextUtilizationScorer internally."""
        evaluator = RAGPipelineEvaluator()

        test_case = {
            "query": "What is dharma?",
            "context": ["Dharma means duty.", "Karma means action."],
            "response": "Dharma means duty.",
        }

        with patch("backend.rag_pipeline_eval.ContextUtilizationScorer") as mock_scorer:
            mock_instance = MagicMock()
            mock_instance.measure_utilization.return_value = {0: 0.9, 1: 0.2}
            mock_scorer.return_value = mock_instance

            generation_metrics = evaluator.evaluate_generation(test_case)

            # Should have called ContextUtilizationScorer methods
            assert "context_utilization" in generation_metrics


# =============================================================================
# Pytest Fixtures
# =============================================================================


@pytest.fixture
def sample_rag_test_case() -> dict:
    """Sample complete RAG test case for pipeline evaluation."""
    return {
        "id": "test_001",
        "query": "What is the main teaching of the Bhagavad Gita?",
        "retrieved_docs": [
            "The Bhagavad Gita teaches dharma, karma, and moksha.",
            "The Mahabharata is an epic about a great war.",
            "Ancient Indian philosophy covers many topics.",
        ],
        "relevant_docs": ["The Bhagavad Gita teaches dharma, karma, and moksha."],
        "context": ["The Bhagavad Gita teaches dharma, karma, and moksha."],
        "response": "The main teaching is dharma (duty), karma (action), and moksha (liberation).",
        "labels": {
            "is_attributed": True,
            "is_context_relevant": True,
            "context_utilization": "USED",
            "hallucination_type": "NONE",
        },
    }


@pytest.fixture
def rag_pipeline_evaluator() -> RAGPipelineEvaluator:
    """Fixture for RAGPipelineEvaluator instance."""
    return RAGPipelineEvaluator()
