"""TDD Tests for V9 RAG Classification Phase.

Tests cover:
- Phase 1: Feature flags and graceful fallback
- Phase 2: RAG metrics and observability
- Phase 3: Confidence calibration
- Phase 4: Precedent diversity check
"""

from __future__ import annotations

import os
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

# We'll import after we create the module
# from backend.phases.classify_v9_rag import (...)


class TestPhase1FeatureFlagsAndFallback:
    """Tests for Task 1.1 and 1.2: RAG feature flags and graceful fallback."""

    def test_should_respect_rag_enabled_flag_when_true(self) -> None:
        """RAG should be enabled when CLASSIFY_RAG_ENABLED=true."""
        with patch.dict(os.environ, {"CLASSIFY_RAG_ENABLED": "true"}):
            # Re-import to pick up new env
            from backend.phases import classify_v9_rag
            import importlib
            importlib.reload(classify_v9_rag)
            assert classify_v9_rag.RAG_ENABLED is True

    def test_should_respect_rag_enabled_flag_when_false(self) -> None:
        """RAG should be disabled when CLASSIFY_RAG_ENABLED=false."""
        with patch.dict(os.environ, {"CLASSIFY_RAG_ENABLED": "false"}):
            from backend.phases import classify_v9_rag
            import importlib
            importlib.reload(classify_v9_rag)
            assert classify_v9_rag.RAG_ENABLED is False

    def test_should_use_configurable_top_k(self) -> None:
        """RAG_TOP_K should be configurable via environment."""
        with patch.dict(os.environ, {"CLASSIFY_RAG_TOP_K": "5"}):
            from backend.phases import classify_v9_rag
            import importlib
            importlib.reload(classify_v9_rag)
            assert classify_v9_rag.RAG_TOP_K == 5

    def test_should_use_configurable_threshold(self) -> None:
        """RAG_SIMILARITY_THRESHOLD should be configurable via environment."""
        with patch.dict(os.environ, {"CLASSIFY_RAG_THRESHOLD": "0.5"}):
            from backend.phases import classify_v9_rag
            import importlib
            importlib.reload(classify_v9_rag)
            assert classify_v9_rag.RAG_SIMILARITY_THRESHOLD == 0.5

    def test_should_continue_without_rag_when_store_missing(self) -> None:
        """Classification should continue gracefully when vector store is missing."""
        from backend.phases.classify_v9_rag import get_rag_retriever_safe

        with patch("backend.phases.classify_v9_rag.get_rag_retriever") as mock_get:
            mock_get.side_effect = FileNotFoundError("Vector store not found")
            result = get_rag_retriever_safe()
            assert result is None

    def test_should_disable_rag_via_env_var(self) -> None:
        """get_rag_retriever_safe should return None when RAG disabled."""
        from backend.phases.classify_v9_rag import get_rag_retriever_safe

        with patch("backend.phases.classify_v9_rag.RAG_ENABLED", False):
            result = get_rag_retriever_safe()
            assert result is None


class TestPhase2RAGMetrics:
    """Tests for Task 2.1 and 2.2: RAG metrics and observability."""

    def test_should_compute_rag_metrics_correctly(self) -> None:
        """RAGMetrics should compute aggregates from retrieved examples."""
        from backend.phases.classify_v9_rag import RAGMetrics

        metrics = RAGMetrics(
            enabled=True,
            precedents_retrieved=3,
            top_similarity=0.92,
            avg_similarity=0.85,
            precedent_categories=["fraudulent", "fraudulent", "general"],
            retrieval_time_ms=45.3,
            high_confidence_match=True,
        )

        assert metrics.enabled is True
        assert metrics.precedents_retrieved == 3
        assert metrics.top_similarity == 0.92
        assert metrics.avg_similarity == 0.85
        assert len(metrics.precedent_categories) == 3
        assert metrics.high_confidence_match is True

    def test_should_handle_empty_retrieval(self) -> None:
        """RAGMetrics should handle no retrieved examples gracefully."""
        from backend.phases.classify_v9_rag import RAGMetrics

        metrics = RAGMetrics(enabled=True, precedents_retrieved=0)

        assert metrics.precedents_retrieved == 0
        assert metrics.top_similarity == 0.0
        assert metrics.avg_similarity == 0.0
        assert metrics.precedent_categories == []
        assert metrics.high_confidence_match is False

    def test_should_build_rag_metrics_from_examples(self) -> None:
        """build_rag_metrics should correctly aggregate example data."""
        from backend.phases.classify_v9_rag import build_rag_metrics

        examples = [
            {"category": "fraudulent", "similarity_score": 0.92},
            {"category": "fraudulent", "similarity_score": 0.88},
            {"category": "general", "similarity_score": 0.75},
        ]

        metrics = build_rag_metrics(
            examples=examples,
            retrieval_time_ms=50.0,
            rag_enabled=True,
            high_confidence_threshold=0.85,
        )

        assert metrics.enabled is True
        assert metrics.precedents_retrieved == 3
        assert metrics.top_similarity == 0.92
        assert abs(metrics.avg_similarity - 0.85) < 0.01
        assert metrics.precedent_categories == ["fraudulent", "fraudulent", "general"]
        assert metrics.retrieval_time_ms == 50.0
        assert metrics.high_confidence_match is True  # 0.92 > 0.85

    def test_should_track_retrieval_latency(self) -> None:
        """Retrieval time should be tracked in metrics."""
        from backend.phases.classify_v9_rag import build_rag_metrics

        examples = [{"category": "general", "similarity_score": 0.6}]
        metrics = build_rag_metrics(
            examples=examples,
            retrieval_time_ms=123.45,
            rag_enabled=True,
            high_confidence_threshold=0.85,
        )

        assert metrics.retrieval_time_ms == 123.45


class TestPhase3ConfidenceCalibration:
    """Tests for Task 3.1 and 3.2: Confidence calibration."""

    def test_should_boost_confidence_when_precedent_agrees(self) -> None:
        """Confidence should increase when high-similarity precedent agrees."""
        from backend.phases.classify_v9_rag import calibrate_confidence, RAGMetrics

        rag_metrics = RAGMetrics(
            enabled=True,
            precedents_retrieved=1,
            top_similarity=0.90,
            avg_similarity=0.90,
            precedent_categories=["fraudulent"],
            retrieval_time_ms=50.0,
            high_confidence_match=True,
        )

        adjusted, reason = calibrate_confidence(
            base_confidence=0.80,
            rag_metrics=rag_metrics,
            precedent_agreement=True,
        )

        assert abs(adjusted - 0.85) < 0.001  # 0.80 + 0.05
        assert "+0.05" in reason

    def test_should_penalize_confidence_when_precedent_disagrees(self) -> None:
        """Confidence should decrease when high-similarity precedent disagrees."""
        from backend.phases.classify_v9_rag import calibrate_confidence, RAGMetrics

        rag_metrics = RAGMetrics(
            enabled=True,
            precedents_retrieved=1,
            top_similarity=0.90,
            avg_similarity=0.90,
            precedent_categories=["fraudulent"],
            retrieval_time_ms=50.0,
            high_confidence_match=True,
        )

        adjusted, reason = calibrate_confidence(
            base_confidence=0.80,
            rag_metrics=rag_metrics,
            precedent_agreement=False,
        )

        assert abs(adjusted - 0.70) < 0.001  # 0.80 - 0.10
        assert "-0.10" in reason
        assert "disagrees" in reason.lower()

    def test_should_boost_for_unanimous_precedents(self) -> None:
        """Confidence should boost when all precedents agree on category."""
        from backend.phases.classify_v9_rag import calibrate_confidence, RAGMetrics

        rag_metrics = RAGMetrics(
            enabled=True,
            precedents_retrieved=3,
            top_similarity=0.75,  # Below high threshold
            avg_similarity=0.72,
            precedent_categories=["general", "general", "general"],
            retrieval_time_ms=50.0,
            high_confidence_match=False,
        )

        adjusted, reason = calibrate_confidence(
            base_confidence=0.80,
            rag_metrics=rag_metrics,
            precedent_agreement=True,
        )

        assert abs(adjusted - 0.83) < 0.001  # 0.80 + 0.03 (unanimous precedents)
        assert "+0.03" in reason

    def test_should_clamp_confidence_to_valid_range(self) -> None:
        """Confidence should never exceed 1.0 or go below 0.0."""
        from backend.phases.classify_v9_rag import calibrate_confidence, RAGMetrics

        rag_metrics = RAGMetrics(
            enabled=True,
            precedents_retrieved=3,
            top_similarity=0.95,
            avg_similarity=0.92,
            precedent_categories=["fraudulent", "fraudulent", "fraudulent"],
            retrieval_time_ms=50.0,
            high_confidence_match=True,
        )

        # Test upper bound
        adjusted_high, _ = calibrate_confidence(
            base_confidence=0.98,
            rag_metrics=rag_metrics,
            precedent_agreement=True,
        )
        assert adjusted_high <= 1.0

        # Test lower bound (create disagreement scenario)
        adjusted_low, _ = calibrate_confidence(
            base_confidence=0.05,
            rag_metrics=rag_metrics,
            precedent_agreement=False,
        )
        assert adjusted_low >= 0.0

    def test_should_not_adjust_when_no_rag_signals(self) -> None:
        """No adjustment when RAG disabled or no precedents."""
        from backend.phases.classify_v9_rag import calibrate_confidence, RAGMetrics

        rag_metrics = RAGMetrics(
            enabled=False,
            precedents_retrieved=0,
        )

        adjusted, reason = calibrate_confidence(
            base_confidence=0.80,
            rag_metrics=rag_metrics,
            precedent_agreement=True,
        )

        assert adjusted == 0.80
        assert "No adjustment" in reason


class TestPhase4PrecedentDiversity:
    """Tests for Task 4.1: Precedent diversity check."""

    def test_should_detect_low_diversity_precedents(self) -> None:
        """Should warn when all precedents are similar and same category."""
        from backend.phases.classify_v9_rag import check_precedent_diversity

        examples = [
            {"category": "fraudulent", "similarity_score": 0.92},
            {"category": "fraudulent", "similarity_score": 0.91},
            {"category": "fraudulent", "similarity_score": 0.90},
        ]

        result = check_precedent_diversity(examples)

        assert result["is_diverse"] is False
        assert result["unique_categories"] == 1
        assert result["warning"] is not None
        assert "bias" in result["warning"].lower()

    def test_should_accept_diverse_precedents(self) -> None:
        """Should accept when precedents have different categories."""
        from backend.phases.classify_v9_rag import check_precedent_diversity

        examples = [
            {"category": "fraudulent", "similarity_score": 0.92},
            {"category": "general", "similarity_score": 0.85},
            {"category": "duplicate", "similarity_score": 0.78},
        ]

        result = check_precedent_diversity(examples)

        assert result["is_diverse"] is True
        assert result["unique_categories"] == 3
        assert result["warning"] is None

    def test_should_accept_single_precedent(self) -> None:
        """Single precedent should be considered diverse (no comparison possible)."""
        from backend.phases.classify_v9_rag import check_precedent_diversity

        examples = [{"category": "fraudulent", "similarity_score": 0.92}]

        result = check_precedent_diversity(examples)

        assert result["is_diverse"] is True
        assert result["unique_categories"] == 1
        assert result["warning"] is None

    def test_should_accept_same_category_with_spread(self) -> None:
        """Same category with high similarity spread is acceptable."""
        from backend.phases.classify_v9_rag import check_precedent_diversity

        examples = [
            {"category": "fraudulent", "similarity_score": 0.92},
            {"category": "fraudulent", "similarity_score": 0.70},
        ]

        result = check_precedent_diversity(examples)

        # Spread is 0.22 which is >= 0.1
        assert result["is_diverse"] is True
        assert result["similarity_spread"] == 0.22


class TestClassifyDisputeV9RAG:
    """Integration tests for classify_dispute_v9_rag function."""

    @pytest.fixture
    def mock_llm_service(self) -> MagicMock:
        """Create mock LLM service."""
        service = MagicMock()
        service.complete_structured = AsyncMock()
        return service

    @pytest.fixture
    def sample_task(self) -> dict[str, Any]:
        """Sample dispute task."""
        return {
            "dispute_id": "test-001",
            "description": "I was charged $50 but the item was only $30",
            "current_date": "2025-01-15",
        }

    @pytest.mark.asyncio
    async def test_should_include_rag_metrics_in_output(
        self, mock_llm_service: MagicMock, sample_task: dict[str, Any]
    ) -> None:
        """Output should include rag_metrics with all required fields."""
        from backend.phases.classify_v9_rag import (
            classify_dispute_v9_rag,
            CategoryResultV9Rag,
            BranchAResult,
            BranchBResult,
            BranchCResult,
            SynthesisResult,
        )

        # Mock category result
        mock_category = CategoryResultV9Rag(
            branch_a=BranchAResult(
                evidence_for_acknowledgment=["charged $50"],
                evidence_against_acknowledgment=[],
                conclusion="acknowledged",
            ),
            branch_b=BranchBResult(
                complaint_type="amount",
                evidence=["$50 vs $30"],
            ),
            branch_c=BranchCResult(
                persona="neutral",
                evidence=[],
            ),
            synthesis=SynthesisResult(
                branch_agreement=0.9,
                priority_rule_applied="Rule 1: Specifics Override Denial",
                reasoning="Amount complaint suggests general category",
            ),
            category="general",
            reason_code_group="authorization",
            confidence=0.85,
            confidence_rationale="High branch agreement",
        )

        mock_code_result = MagicMock()
        mock_code_result.reason_code = "10.1"
        mock_code_result.confidence = 0.9
        mock_code_result.reasoning = "Selected based on amount dispute"

        mock_llm_service.complete_structured.side_effect = [mock_category, mock_code_result]

        with patch("backend.phases.classify_v9_rag.get_default_service", return_value=mock_llm_service):
            with patch("backend.phases.classify_v9_rag.get_rag_retriever_safe", return_value=None):
                result = await classify_dispute_v9_rag(sample_task)

        assert "rag_metrics" in result
        rag_metrics = result["rag_metrics"]
        assert "enabled" in rag_metrics
        assert "precedents_retrieved" in rag_metrics
        assert "top_similarity" in rag_metrics
        assert "retrieval_time_ms" in rag_metrics

    @pytest.mark.asyncio
    async def test_should_include_confidence_adjustment_in_output(
        self, mock_llm_service: MagicMock, sample_task: dict[str, Any]
    ) -> None:
        """Output should include confidence adjustment details."""
        from backend.phases.classify_v9_rag import (
            classify_dispute_v9_rag,
            CategoryResultV9Rag,
            BranchAResult,
            BranchBResult,
            BranchCResult,
            SynthesisResult,
        )

        mock_category = CategoryResultV9Rag(
            branch_a=BranchAResult(
                evidence_for_acknowledgment=[],
                evidence_against_acknowledgment=["never authorized"],
                conclusion="denied",
            ),
            branch_b=BranchBResult(
                complaint_type="unspecified",
                evidence=[],
            ),
            branch_c=BranchCResult(
                persona="accusatory",
                evidence=["never authorized"],
            ),
            synthesis=SynthesisResult(
                branch_agreement=0.9,
                priority_rule_applied=None,
                reasoning="Clear fraud indication",
            ),
            category="fraudulent",
            reason_code_group="fraud",
            confidence=0.85,
            confidence_rationale="Strong denial signals",
        )

        mock_code_result = MagicMock()
        mock_code_result.reason_code = "10.4"
        mock_code_result.confidence = 0.9
        mock_code_result.reasoning = "Fraud category"

        mock_llm_service.complete_structured.side_effect = [mock_category, mock_code_result]

        with patch("backend.phases.classify_v9_rag.get_default_service", return_value=mock_llm_service):
            with patch("backend.phases.classify_v9_rag.get_rag_retriever_safe", return_value=None):
                result = await classify_dispute_v9_rag(sample_task)

        assert "confidence_adjustment" in result
        assert "confidence_adjustment_reason" in result

    @pytest.mark.asyncio
    async def test_should_work_when_rag_disabled(
        self, mock_llm_service: MagicMock, sample_task: dict[str, Any]
    ) -> None:
        """Classification should work normally when RAG is disabled."""
        from backend.phases.classify_v9_rag import (
            classify_dispute_v9_rag,
            CategoryResultV9Rag,
            BranchAResult,
            BranchBResult,
            BranchCResult,
            SynthesisResult,
        )

        mock_category = CategoryResultV9Rag(
            branch_a=BranchAResult(
                evidence_for_acknowledgment=["my order"],
                evidence_against_acknowledgment=[],
                conclusion="acknowledged",
            ),
            branch_b=BranchBResult(
                complaint_type="delivery",
                evidence=["never arrived"],
            ),
            branch_c=BranchCResult(
                persona="frustrated",
                evidence=["still waiting"],
            ),
            synthesis=SynthesisResult(
                branch_agreement=0.95,
                priority_rule_applied="Rule 2: Delivery Signals Non-Receipt",
                reasoning="Delivery complaint with acknowledgment",
            ),
            category="product_not_received",
            reason_code_group="cardholder_disputes",
            confidence=0.9,
            confidence_rationale="Clear delivery issue",
        )

        mock_code_result = MagicMock()
        mock_code_result.reason_code = "13.1"
        mock_code_result.confidence = 0.9
        mock_code_result.reasoning = "Product not received"

        mock_llm_service.complete_structured.side_effect = [mock_category, mock_code_result]

        with patch("backend.phases.classify_v9_rag.get_default_service", return_value=mock_llm_service):
            with patch("backend.phases.classify_v9_rag.RAG_ENABLED", False):
                result = await classify_dispute_v9_rag(sample_task)

        assert result["category"] == "product_not_received"
        assert result["rag_metrics"]["enabled"] is False
