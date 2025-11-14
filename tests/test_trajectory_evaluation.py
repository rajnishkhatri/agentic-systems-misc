"""Tests for trajectory evaluation module.

This module tests the TrajectoryEvaluator and TrajectoryVisualizer classes
that implement 6 trajectory metrics for agent evaluation:
- exact_match: Exact sequence match (strictest)
- in_order_match: Actions appear in order (extras allowed)
- any_order_match: All actions present (order irrelevant)
- precision: Fraction of predicted actions that are correct
- recall: Fraction of reference actions found
- single_tool_use: Efficiency penalty for excessive tool use

Test Pattern: test_should_[result]_when_[condition]()
Following TDD: RED → GREEN → REFACTOR
"""

import pytest
from backend.trajectory_evaluation import TrajectoryEvaluator, TrajectoryVisualizer


class TestTrajectoryEvaluatorExactMatch:
    """Test exact_match metric (all actions match in exact order)."""

    def test_should_return_1_when_trajectories_identical(self) -> None:
        """Test that identical trajectories return perfect score."""
        evaluator = TrajectoryEvaluator()
        reference = ["search", "read", "answer"]
        predicted = ["search", "read", "answer"]
        assert evaluator.exact_match(reference, predicted) == 1.0

    def test_should_return_0_when_actions_different(self) -> None:
        """Test that different actions return zero score."""
        evaluator = TrajectoryEvaluator()
        reference = ["search", "read", "answer"]
        predicted = ["query", "fetch", "respond"]
        assert evaluator.exact_match(reference, predicted) == 0.0

    def test_should_return_0_when_same_actions_wrong_order(self) -> None:
        """Test that correct actions in wrong order return zero."""
        evaluator = TrajectoryEvaluator()
        reference = ["search", "read", "answer"]
        predicted = ["read", "search", "answer"]
        assert evaluator.exact_match(reference, predicted) == 0.0

    def test_should_return_1_when_both_empty(self) -> None:
        """Test that empty trajectories return perfect score."""
        evaluator = TrajectoryEvaluator()
        reference = []
        predicted = []
        assert evaluator.exact_match(reference, predicted) == 1.0

    def test_should_return_0_when_lengths_differ(self) -> None:
        """Test that different length trajectories return zero."""
        evaluator = TrajectoryEvaluator()
        reference = ["search", "read"]
        predicted = ["search", "read", "answer"]
        assert evaluator.exact_match(reference, predicted) == 0.0


class TestTrajectoryEvaluatorInOrderMatch:
    """Test in_order_match metric (actions appear in order, extras allowed)."""

    def test_should_return_1_when_exact_match(self) -> None:
        """Test that exact match returns perfect score."""
        evaluator = TrajectoryEvaluator()
        reference = ["search", "read", "answer"]
        predicted = ["search", "read", "answer"]
        assert evaluator.in_order_match(reference, predicted) == 1.0

    def test_should_return_1_when_actions_in_order_with_extras(self) -> None:
        """Test that in-order actions with extras return perfect score."""
        evaluator = TrajectoryEvaluator()
        reference = ["search", "read", "answer"]
        predicted = ["validate", "search", "filter", "read", "verify", "answer"]
        assert evaluator.in_order_match(reference, predicted) == 1.0

    def test_should_return_0_when_actions_out_of_order(self) -> None:
        """Test that out-of-order actions return zero."""
        evaluator = TrajectoryEvaluator()
        reference = ["search", "read", "answer"]
        predicted = ["read", "search", "answer"]
        assert evaluator.in_order_match(reference, predicted) == 0.0

    def test_should_return_1_when_subset_in_order(self) -> None:
        """Test that subset of actions in order returns perfect score."""
        evaluator = TrajectoryEvaluator()
        reference = ["search", "read"]
        predicted = ["search", "filter", "read", "answer"]
        assert evaluator.in_order_match(reference, predicted) == 1.0

    def test_should_return_0_when_predicted_empty(self) -> None:
        """Test that empty predicted trajectory returns zero when reference not empty."""
        evaluator = TrajectoryEvaluator()
        reference = ["search", "read"]
        predicted = []
        assert evaluator.in_order_match(reference, predicted) == 0.0


class TestTrajectoryEvaluatorAnyOrderMatch:
    """Test any_order_match metric (all actions present, order irrelevant)."""

    def test_should_return_1_when_all_actions_present(self) -> None:
        """Test that all actions present returns perfect score regardless of order."""
        evaluator = TrajectoryEvaluator()
        reference = ["search", "read", "answer"]
        predicted = ["answer", "search", "read"]
        assert evaluator.any_order_match(reference, predicted) == 1.0

    def test_should_return_0_when_missing_actions(self) -> None:
        """Test that missing actions return zero."""
        evaluator = TrajectoryEvaluator()
        reference = ["search", "read", "answer"]
        predicted = ["search", "read"]
        assert evaluator.any_order_match(reference, predicted) == 0.0

    def test_should_return_1_when_all_present_with_extras(self) -> None:
        """Test that all actions present with extras returns perfect score."""
        evaluator = TrajectoryEvaluator()
        reference = ["search", "read", "answer"]
        predicted = ["validate", "search", "filter", "read", "answer", "verify"]
        assert evaluator.any_order_match(reference, predicted) == 1.0

    def test_should_handle_duplicate_actions(self) -> None:
        """Test that duplicate actions are handled correctly."""
        evaluator = TrajectoryEvaluator()
        reference = ["search", "search", "answer"]
        predicted = ["search", "answer"]
        # Should return 0.0 because predicted missing one "search"
        assert evaluator.any_order_match(reference, predicted) == 0.0


class TestTrajectoryEvaluatorPrecision:
    """Test precision metric (fraction of predicted actions correct)."""

    def test_should_return_1_when_all_predictions_correct(self) -> None:
        """Test that all correct predictions return perfect precision."""
        evaluator = TrajectoryEvaluator()
        reference = ["search", "read", "answer"]
        predicted = ["search", "read", "answer"]
        assert evaluator.precision(reference, predicted) == 1.0

    def test_should_return_0_5_when_half_correct(self) -> None:
        """Test that half correct predictions return 0.5 precision."""
        evaluator = TrajectoryEvaluator()
        reference = ["search", "read", "answer"]
        predicted = ["search", "read", "verify", "filter"]
        # 2 correct out of 4 predicted = 0.5
        assert evaluator.precision(reference, predicted) == 0.5

    def test_should_return_0_when_none_correct(self) -> None:
        """Test that no correct predictions return zero precision."""
        evaluator = TrajectoryEvaluator()
        reference = ["search", "read", "answer"]
        predicted = ["query", "fetch", "respond"]
        assert evaluator.precision(reference, predicted) == 0.0

    def test_should_return_0_when_predicted_empty(self) -> None:
        """Test that empty predicted trajectory returns zero precision."""
        evaluator = TrajectoryEvaluator()
        reference = ["search", "read", "answer"]
        predicted = []
        assert evaluator.precision(reference, predicted) == 0.0

    def test_should_penalize_extra_predictions(self) -> None:
        """Test that extra incorrect predictions lower precision."""
        evaluator = TrajectoryEvaluator()
        reference = ["search", "read"]
        predicted = ["search", "read", "extra1", "extra2", "extra3"]
        # 2 correct out of 5 predicted = 0.4
        assert evaluator.precision(reference, predicted) == 0.4


class TestTrajectoryEvaluatorRecall:
    """Test recall metric (fraction of reference actions found)."""

    def test_should_return_1_when_all_reference_found(self) -> None:
        """Test that all reference actions found returns perfect recall."""
        evaluator = TrajectoryEvaluator()
        reference = ["search", "read", "answer"]
        predicted = ["search", "read", "answer", "extra"]
        assert evaluator.recall(reference, predicted) == 1.0

    def test_should_return_0_5_when_half_reference_found(self) -> None:
        """Test that half reference actions found return 0.5 recall."""
        evaluator = TrajectoryEvaluator()
        reference = ["search", "read", "answer", "verify"]
        predicted = ["search", "read"]
        # 2 found out of 4 reference = 0.5
        assert evaluator.recall(reference, predicted) == 0.5

    def test_should_return_0_when_none_found(self) -> None:
        """Test that no reference actions found return zero recall."""
        evaluator = TrajectoryEvaluator()
        reference = ["search", "read", "answer"]
        predicted = ["query", "fetch", "respond"]
        assert evaluator.recall(reference, predicted) == 0.0

    def test_should_return_1_when_reference_empty(self) -> None:
        """Test that empty reference returns perfect recall (undefined case)."""
        evaluator = TrajectoryEvaluator()
        reference = []
        predicted = ["search", "read"]
        # No reference to miss = perfect recall
        assert evaluator.recall(reference, predicted) == 1.0

    def test_should_measure_partial_coverage(self) -> None:
        """Test that partial coverage returns proportional recall."""
        evaluator = TrajectoryEvaluator()
        reference = ["search", "read", "answer", "verify", "respond"]
        predicted = ["search", "answer", "respond"]
        # 3 found out of 5 reference = 0.6
        assert evaluator.recall(reference, predicted) == 0.6


class TestTrajectoryEvaluatorSingleToolUse:
    """Test single_tool_use metric (efficiency penalty for excessive tool calls)."""

    def test_should_return_1_when_minimal_tool_use(self) -> None:
        """Test that minimal tool use returns perfect efficiency score."""
        evaluator = TrajectoryEvaluator()
        reference = ["search", "read", "answer"]
        predicted = ["search", "read", "answer"]
        assert evaluator.single_tool_use(reference, predicted) == 1.0

    def test_should_penalize_excessive_tool_use(self) -> None:
        """Test that excessive tool use returns penalty score < 1.0."""
        evaluator = TrajectoryEvaluator()
        reference = ["search", "read", "answer"]
        predicted = ["search", "search", "search", "read", "read", "answer"]
        # Penalty for 6 predicted vs 3 reference
        score = evaluator.single_tool_use(reference, predicted)
        assert score < 1.0
        assert score > 0.0

    def test_should_calculate_efficiency_ratio(self) -> None:
        """Test that efficiency is calculated as reference_length / predicted_length."""
        evaluator = TrajectoryEvaluator()
        reference = ["search", "read", "answer"]  # 3 actions
        predicted = ["search", "filter", "read", "verify", "answer", "log"]  # 6 actions
        # Efficiency = 3 / 6 = 0.5
        assert evaluator.single_tool_use(reference, predicted) == 0.5

    def test_should_handle_empty_trajectories(self) -> None:
        """Test that empty trajectories return sensible efficiency score."""
        evaluator = TrajectoryEvaluator()
        reference = []
        predicted = []
        # Empty trajectories = perfect efficiency
        assert evaluator.single_tool_use(reference, predicted) == 1.0


class TestTrajectoryVisualizer:
    """Test visualization utilities."""

    def test_should_generate_radar_chart_data(self) -> None:
        """Test that radar chart data structure is generated correctly."""
        visualizer = TrajectoryVisualizer()
        metrics = {
            "exact_match": 0.0,
            "in_order_match": 1.0,
            "any_order_match": 1.0,
            "precision": 0.8,
            "recall": 0.9,
            "single_tool_use": 0.7,
        }
        chart_data = visualizer.generate_radar_chart(metrics)
        assert "labels" in chart_data
        assert "values" in chart_data
        assert len(chart_data["labels"]) == 6
        assert len(chart_data["values"]) == 6

    def test_should_format_comparison_table(self) -> None:
        """Test that comparison table is formatted correctly."""
        visualizer = TrajectoryVisualizer()
        reference = ["search", "read", "answer"]
        predicted = ["search", "filter", "read", "answer"]
        metrics = {
            "exact_match": 0.0,
            "precision": 0.75,
            "recall": 1.0,
        }
        table = visualizer.format_comparison_table(reference, predicted, metrics)
        assert isinstance(table, str)
        assert "search" in table
        assert "0.75" in table or "75" in table

    def test_should_handle_missing_metrics(self) -> None:
        """Test that missing metrics are handled gracefully."""
        visualizer = TrajectoryVisualizer()
        metrics = {
            "exact_match": 0.5,
            "precision": 0.8,
            # Missing other metrics
        }
        chart_data = visualizer.generate_radar_chart(metrics)
        # Should not crash, should fill missing with 0.0 or skip
        assert chart_data is not None

    def test_should_handle_all_zeros(self) -> None:
        """Test that all-zero metrics are handled correctly."""
        visualizer = TrajectoryVisualizer()
        metrics = {
            "exact_match": 0.0,
            "in_order_match": 0.0,
            "any_order_match": 0.0,
            "precision": 0.0,
            "recall": 0.0,
            "single_tool_use": 0.0,
        }
        chart_data = visualizer.generate_radar_chart(metrics)
        assert all(v == 0.0 for v in chart_data["values"])


class TestDefensiveCoding:
    """Test input validation and error handling."""

    def test_should_raise_error_when_reference_not_list(self) -> None:
        """Test that non-list reference raises TypeError."""
        evaluator = TrajectoryEvaluator()
        with pytest.raises(TypeError, match="reference must be a list"):
            evaluator.exact_match("not a list", ["search"])

    def test_should_raise_error_when_predicted_not_list(self) -> None:
        """Test that non-list predicted raises TypeError."""
        evaluator = TrajectoryEvaluator()
        with pytest.raises(TypeError, match="predicted must be a list"):
            evaluator.exact_match(["search"], "not a list")

    def test_should_raise_error_when_actions_not_strings(self) -> None:
        """Test that non-string actions raise ValueError."""
        evaluator = TrajectoryEvaluator()
        with pytest.raises(ValueError, match="must contain only strings"):
            evaluator.exact_match(["search", 123], ["search"])
