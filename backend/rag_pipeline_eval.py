"""RAG Pipeline Evaluator - End-to-End RAG Evaluation (Lesson 13).

This module provides comprehensive RAG pipeline evaluation combining:
- Retrieval quality metrics (Recall@k, Precision, MRR) from HW4
- Generation quality metrics (attribution, hallucination, utilization) from Lesson 13
- Failure mode identification (RETRIEVAL_FAILURE vs GENERATION_FAILURE)

Integrates with:
- HW4 retrieval metrics (BM25, Recall@k)
- Lesson 12 hybrid retrieval evaluation
- Lesson 13 generation evaluation classes

Following TDD-GREEN phase: Minimal implementation to pass tests.
"""

from typing import Any

from backend.rag_generation_eval import (
    AttributionDetector,
    ContextUtilizationScorer,
    HallucinationDetector,
)


class RAGPipelineEvaluator:
    """End-to-end RAG pipeline evaluator combining retrieval and generation metrics.

    This class integrates:
    1. Retrieval evaluation: Precision, Recall@k, MRR (from HW4)
    2. Generation evaluation: Attribution, Hallucination, Context Utilization (from Lesson 13)
    3. Failure mode identification: Pinpoint whether failures are in retrieval or generation

    Attributes:
        attribution_detector: AttributionDetector instance for claim verification
        hallucination_detector: HallucinationDetector for intrinsic/extrinsic detection
        utilization_scorer: ContextUtilizationScorer for measuring doc usage
    """

    def __init__(self) -> None:
        """Initialize RAG pipeline evaluator with generation eval components."""
        self.attribution_detector = AttributionDetector()
        self.hallucination_detector = HallucinationDetector()
        self.utilization_scorer = ContextUtilizationScorer()

    def evaluate_retrieval(self, test_case: dict[str, Any]) -> dict[str, float]:
        """Evaluate retrieval quality: Precision, Recall@k, MRR.

        Args:
            test_case: Test case with retrieved_docs and relevant_docs

        Returns:
            Dictionary with retrieval metrics (precision, recall_at_k, mrr)
        """
        retrieved_docs = test_case.get("retrieved_docs", [])
        relevant_docs = test_case.get("relevant_docs", [])

        if not retrieved_docs or not relevant_docs:
            return {"precision": 0.0, "recall_at_k": 0.0, "mrr": 0.0}

        # Calculate precision: % of retrieved docs that are relevant
        relevant_retrieved = sum(1 for doc in retrieved_docs if doc in relevant_docs)
        precision = relevant_retrieved / len(retrieved_docs) if retrieved_docs else 0.0

        # Calculate recall@k: % of relevant docs that were retrieved
        recall_at_k = relevant_retrieved / len(relevant_docs) if relevant_docs else 0.0

        # Calculate MRR (Mean Reciprocal Rank): 1/rank of first relevant doc
        mrr = 0.0
        for i, doc in enumerate(retrieved_docs):
            if doc in relevant_docs:
                mrr = 1.0 / (i + 1)
                break

        return {"precision": precision, "recall_at_k": recall_at_k, "mrr": mrr}

    def evaluate_generation(self, test_case: dict[str, Any]) -> dict[str, Any]:
        """Evaluate generation quality: Attribution, Hallucination, Context Utilization.

        Args:
            test_case: Test case with query, context, and response

        Returns:
            Dictionary with generation metrics (attribution_rate, hallucination_type, context_utilization)
        """
        context = test_case.get("context", [])
        response = test_case.get("response", "")

        if not response or not context:
            return {
                "attribution_rate": 0.0,
                "hallucination_type": "EXTRINSIC",
                "context_utilization": {},
            }

        # 1. Measure attribution
        claims = self.attribution_detector.extract_claims(response)
        attribution_result = self.attribution_detector.verify_attribution(claims, context)
        attribution_rate = (
            sum(attribution_result["attribution_scores"]) / len(attribution_result["attribution_scores"])
            if attribution_result["attribution_scores"]
            else 0.0
        )

        # 2. Detect hallucinations
        hallucination_type = self.hallucination_detector.classify_hallucination_type(response, context)

        # 3. Measure context utilization
        context_utilization = self.utilization_scorer.measure_utilization(response, context)

        return {
            "attribution_rate": attribution_rate,
            "hallucination_type": hallucination_type,
            "context_utilization": context_utilization,
        }

    def evaluate_pipeline(self, test_case: dict[str, Any]) -> dict[str, Any]:
        """Evaluate complete RAG pipeline (retrieval + generation).

        Args:
            test_case: Complete test case with all fields

        Returns:
            Dictionary with retrieval, generation, and overall_score metrics

        Raises:
            TypeError: If test_case is not a dict
            ValueError: If test_case missing required fields
        """
        # Step 1: Type checking
        if not isinstance(test_case, dict):
            raise TypeError("test_case must be a dict")

        # Step 2: Validate required fields
        required_fields = ["query", "context", "response"]
        missing_fields = [field for field in required_fields if field not in test_case]
        if missing_fields:
            raise ValueError(f"test_case must contain: {', '.join(missing_fields)}")

        # Step 3: Evaluate retrieval (if retrieval data present)
        retrieval_metrics = {}
        if "retrieved_docs" in test_case and "relevant_docs" in test_case:
            retrieval_metrics = self.evaluate_retrieval(test_case)

        # Step 4: Evaluate generation
        generation_metrics = self.evaluate_generation(test_case)

        # Step 5: Calculate overall score
        overall_score = self._calculate_overall_score(retrieval_metrics, generation_metrics)

        # Step 6: Return complete metrics
        return {
            "retrieval": retrieval_metrics,
            "generation": generation_metrics,
            "overall_score": overall_score,
        }

    def identify_failure_mode(self, test_case: dict[str, Any]) -> str:
        """Identify where RAG pipeline failed: RETRIEVAL_FAILURE, GENERATION_FAILURE, or NONE.

        Args:
            test_case: Test case with pipeline evaluation results

        Returns:
            One of: "RETRIEVAL_FAILURE", "GENERATION_FAILURE", "NONE"
        """
        # Evaluate pipeline
        metrics = self.evaluate_pipeline(test_case)

        retrieval_metrics = metrics.get("retrieval", {})
        generation_metrics = metrics.get("generation", {})

        # Check retrieval quality
        recall = retrieval_metrics.get("recall_at_k", 1.0)
        precision = retrieval_metrics.get("precision", 1.0)
        retrieval_failed = recall < 0.5 or precision < 0.3

        # Check generation quality
        hallucination_type = generation_metrics.get("hallucination_type", "NONE")
        attribution_rate = generation_metrics.get("attribution_rate", 1.0)
        generation_failed = hallucination_type != "NONE" or attribution_rate < 0.5

        # Identify failure mode
        if retrieval_failed:
            return "RETRIEVAL_FAILURE"
        elif generation_failed:
            return "GENERATION_FAILURE"
        else:
            return "NONE"

    def evaluate_batch(self, test_cases: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Evaluate multiple test cases in batch.

        Args:
            test_cases: List of test cases to evaluate

        Returns:
            List of evaluation results (one per test case)
        """
        results = []
        for test_case in test_cases:
            try:
                result = self.evaluate_pipeline(test_case)
                results.append(result)
            except (TypeError, ValueError) as e:
                # Log error but continue with other test cases
                results.append({"error": str(e), "test_case_id": test_case.get("id", "unknown")})

        return results

    def generate_report(self, batch_results: list[dict[str, Any]]) -> dict[str, Any]:
        """Generate evaluation report with summary statistics.

        Args:
            batch_results: Results from evaluate_batch()

        Returns:
            Dictionary with summary statistics and detailed results
        """
        # Filter out error results
        valid_results = [r for r in batch_results if "error" not in r]

        if not valid_results:
            return {"summary": {"error": "No valid results to summarize"}, "results": batch_results}

        # Calculate summary statistics
        avg_recall = (
            sum(r["retrieval"].get("recall_at_k", 0) for r in valid_results if r.get("retrieval"))
            / len(valid_results)
            if valid_results
            else 0.0
        )

        avg_attribution = (
            sum(r["generation"].get("attribution_rate", 0) for r in valid_results if r.get("generation"))
            / len(valid_results)
            if valid_results
            else 0.0
        )

        avg_overall = (
            sum(r.get("overall_score", 0) for r in valid_results) / len(valid_results) if valid_results else 0.0
        )

        # Count hallucination types
        hallucination_counts = {"NONE": 0, "INTRINSIC": 0, "EXTRINSIC": 0}
        for result in valid_results:
            halluc_type = result.get("generation", {}).get("hallucination_type", "NONE")
            if halluc_type in hallucination_counts:
                hallucination_counts[halluc_type] += 1

        return {
            "summary": {
                "total_cases": len(batch_results),
                "valid_cases": len(valid_results),
                "avg_retrieval_recall": avg_recall,
                "avg_attribution_rate": avg_attribution,
                "avg_overall_score": avg_overall,
                "hallucination_counts": hallucination_counts,
            },
            "results": batch_results,
        }

    def _calculate_overall_score(
        self, retrieval_metrics: dict[str, float], generation_metrics: dict[str, Any]
    ) -> float:
        """Calculate weighted overall score combining retrieval and generation.

        Args:
            retrieval_metrics: Retrieval quality metrics
            generation_metrics: Generation quality metrics

        Returns:
            Overall score from 0.0 to 1.0
        """
        # Weights: retrieval 40%, generation 60% (generation more critical for user experience)
        retrieval_weight = 0.4
        generation_weight = 0.6

        # Calculate retrieval score (average of precision and recall)
        retrieval_score = 0.0
        if retrieval_metrics:
            precision = retrieval_metrics.get("precision", 0.0)
            recall = retrieval_metrics.get("recall_at_k", 0.0)
            retrieval_score = (precision + recall) / 2.0

        # Calculate generation score (attribution rate, penalize hallucinations)
        attribution_rate = generation_metrics.get("attribution_rate", 0.0)
        hallucination_type = generation_metrics.get("hallucination_type", "NONE")

        # Penalize hallucinations
        hallucination_penalty = 0.0
        if hallucination_type == "INTRINSIC":
            hallucination_penalty = 0.3  # Severe penalty for contradictions
        elif hallucination_type == "EXTRINSIC":
            hallucination_penalty = 0.1  # Moderate penalty for extra info

        generation_score = max(0.0, attribution_rate - hallucination_penalty)

        # Calculate weighted overall score
        overall_score = (retrieval_weight * retrieval_score) + (generation_weight * generation_score)

        return round(overall_score, 3)