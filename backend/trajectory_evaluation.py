"""Trajectory evaluation module for agent performance measurement.

This module implements 6 trajectory metrics for evaluating agent behavior:
1. exact_match: Strict sequence match (all actions in exact order)
2. in_order_match: Actions appear in order (extras allowed)
3. any_order_match: All actions present (order irrelevant)
4. precision: Fraction of predicted actions that are correct
5. recall: Fraction of reference actions found in predicted
6. single_tool_use: Efficiency penalty for excessive tool calls

Usage:
    evaluator = TrajectoryEvaluator()
    score = evaluator.exact_match(reference, predicted)

    visualizer = TrajectoryVisualizer()
    chart = visualizer.generate_radar_chart(metrics)
"""

from collections import Counter
from typing import Any


class TrajectoryEvaluator:
    """Evaluates agent trajectories using 6 metrics.

    Attributes:
        None

    Methods:
        exact_match: Exact sequence match (strictest)
        in_order_match: Actions appear in order (extras allowed)
        any_order_match: All actions present (order irrelevant)
        precision: Fraction of predicted actions correct
        recall: Fraction of reference actions found
        single_tool_use: Efficiency penalty for excessive calls
    """

    def __init__(self) -> None:
        """Initialize TrajectoryEvaluator."""
        pass

    def _validate_inputs(self, reference: Any, predicted: Any) -> None:
        """Validate input types and values.

        Args:
            reference: Reference trajectory
            predicted: Predicted trajectory

        Raises:
            TypeError: If inputs are not lists
            ValueError: If lists don't contain only strings
        """
        # Step 1: Type checking
        if not isinstance(reference, list):
            raise TypeError("reference must be a list")
        if not isinstance(predicted, list):
            raise TypeError("predicted must be a list")

        # Step 2: Value validation
        if not all(isinstance(action, str) for action in reference):
            raise ValueError("reference must contain only strings")
        if not all(isinstance(action, str) for action in predicted):
            raise ValueError("predicted must contain only strings")

    def exact_match(self, reference: list[str], predicted: list[str]) -> float:
        """Calculate exact match score (1.0 if identical, else 0.0).

        Args:
            reference: Reference trajectory (ground truth)
            predicted: Predicted trajectory (agent output)

        Returns:
            1.0 if trajectories identical, 0.0 otherwise

        Raises:
            TypeError: If inputs are not lists
            ValueError: If lists don't contain only strings
        """
        # Step 1: Input validation
        self._validate_inputs(reference, predicted)

        # Step 2: Main logic
        if reference == predicted:
            return 1.0
        return 0.0

    def in_order_match(self, reference: list[str], predicted: list[str]) -> float:
        """Calculate in-order match score (1.0 if all actions appear in order).

        Actions must appear in the same order in predicted as in reference,
        but extra actions are allowed between them.

        Args:
            reference: Reference trajectory (ground truth)
            predicted: Predicted trajectory (agent output)

        Returns:
            1.0 if all reference actions appear in order, 0.0 otherwise

        Raises:
            TypeError: If inputs are not lists
            ValueError: If lists don't contain only strings
        """
        # Step 1: Input validation
        self._validate_inputs(reference, predicted)

        # Step 2: Edge cases
        if not reference:
            return 1.0  # Empty reference always matches
        if not predicted:
            return 0.0  # Empty predicted can't match non-empty reference

        # Step 3: Main logic - Check if reference is subsequence of predicted
        ref_idx = 0
        for action in predicted:
            if ref_idx < len(reference) and action == reference[ref_idx]:
                ref_idx += 1

        # Step 4: Return
        if ref_idx == len(reference):
            return 1.0  # All reference actions found in order
        return 0.0

    def any_order_match(self, reference: list[str], predicted: list[str]) -> float:
        """Calculate any-order match score (1.0 if all actions present).

        All reference actions must be present in predicted, but order doesn't matter.
        Handles duplicates correctly (if reference has 2 "search", predicted must too).

        Args:
            reference: Reference trajectory (ground truth)
            predicted: Predicted trajectory (agent output)

        Returns:
            1.0 if all reference actions present (including duplicates), 0.0 otherwise

        Raises:
            TypeError: If inputs are not lists
            ValueError: If lists don't contain only strings
        """
        # Step 1: Input validation
        self._validate_inputs(reference, predicted)

        # Step 2: Edge cases
        if not reference:
            return 1.0  # Empty reference always matches

        # Step 3: Main logic - Use Counter for multiset comparison
        ref_counter = Counter(reference)
        pred_counter = Counter(predicted)

        # Check if all reference actions (with counts) are in predicted
        for action, count in ref_counter.items():
            if pred_counter[action] < count:
                return 0.0  # Missing action or insufficient count

        # Step 4: Return
        return 1.0

    def precision(self, reference: list[str], predicted: list[str]) -> float:
        """Calculate precision (fraction of predicted actions that are correct).

        Precision = (# correct predictions) / (# total predictions)

        Args:
            reference: Reference trajectory (ground truth)
            predicted: Predicted trajectory (agent output)

        Returns:
            Precision score (0.0 to 1.0), 0.0 if predicted is empty

        Raises:
            TypeError: If inputs are not lists
            ValueError: If lists don't contain only strings
        """
        # Step 1: Input validation
        self._validate_inputs(reference, predicted)

        # Step 2: Edge case
        if not predicted:
            return 0.0  # No predictions = 0 precision

        # Step 3: Main logic - Count correct predictions (optimized with Counter)
        ref_counter = Counter(reference)
        pred_counter = Counter(predicted)

        # Optimize: sum in generator expression instead of loop
        correct_count = sum(
            min(pred_counter[action], ref_counter[action]) for action in pred_counter
        )

        # Step 4: Return
        return correct_count / len(predicted)

    def recall(self, reference: list[str], predicted: list[str]) -> float:
        """Calculate recall (fraction of reference actions found in predicted).

        Recall = (# reference actions found) / (# total reference actions)

        Args:
            reference: Reference trajectory (ground truth)
            predicted: Predicted trajectory (agent output)

        Returns:
            Recall score (0.0 to 1.0), 1.0 if reference is empty

        Raises:
            TypeError: If inputs are not lists
            ValueError: If lists don't contain only strings
        """
        # Step 1: Input validation
        self._validate_inputs(reference, predicted)

        # Step 2: Edge case
        if not reference:
            return 1.0  # No reference to miss = perfect recall

        # Step 3: Main logic - Count reference actions found (optimized with Counter)
        ref_counter = Counter(reference)
        pred_counter = Counter(predicted)

        # Optimize: sum in generator expression instead of loop
        found_count = sum(
            min(pred_counter[action], ref_counter[action]) for action in ref_counter
        )

        # Step 4: Return
        return found_count / len(reference)

    def single_tool_use(self, reference: list[str], predicted: list[str]) -> float:
        """Calculate efficiency score (penalty for excessive tool calls).

        Efficiency = reference_length / predicted_length
        Lower predicted length = higher efficiency (closer to 1.0)

        Args:
            reference: Reference trajectory (ground truth)
            predicted: Predicted trajectory (agent output)

        Returns:
            Efficiency score (0.0 to 1.0), 1.0 if both empty or predicted <= reference

        Raises:
            TypeError: If inputs are not lists
            ValueError: If lists don't contain only strings
        """
        # Step 1: Input validation
        self._validate_inputs(reference, predicted)

        # Step 2: Edge cases
        if not reference and not predicted:
            return 1.0  # Both empty = perfect efficiency
        if not predicted:
            return 0.0  # No predicted actions

        # Step 3: Main logic - Calculate efficiency ratio
        ref_length = len(reference)
        pred_length = len(predicted)

        if pred_length <= ref_length:
            return 1.0  # Equal or fewer actions = perfect efficiency

        # Step 4: Return
        return ref_length / pred_length


class TrajectoryVisualizer:
    """Visualizes trajectory evaluation metrics.

    Methods:
        generate_radar_chart: Create radar chart data structure
        format_comparison_table: Format trajectory comparison table
    """

    def __init__(self) -> None:
        """Initialize TrajectoryVisualizer."""
        pass

    def generate_radar_chart(
        self, metrics: dict[str, float]
    ) -> dict[str, list[str] | list[float]]:
        """Generate radar chart data structure for 6 trajectory metrics.

        Args:
            metrics: Dictionary with metric names and scores (0.0 to 1.0)

        Returns:
            Dictionary with "labels" (list[str]) and "values" (list[float]) keys for plotting

        Raises:
            TypeError: If metrics is not a dict
            ValueError: If metric values are not floats
        """
        # Step 1: Type checking
        if not isinstance(metrics, dict):
            raise TypeError("metrics must be a dict")

        # Step 2: Value validation
        for key, value in metrics.items():
            if not isinstance(key, str):
                raise ValueError("metric keys must be strings")
            if not isinstance(value, (int, float)):
                raise ValueError(f"metric value for '{key}' must be numeric")

        # Step 3: Define expected metrics in display order
        expected_metrics = [
            "exact_match",
            "in_order_match",
            "any_order_match",
            "precision",
            "recall",
            "single_tool_use",
        ]

        # Step 4: Extract values (default to 0.0 if missing)
        labels = []
        values = []
        for metric in expected_metrics:
            if metric in metrics:
                labels.append(metric)
                values.append(float(metrics[metric]))

        # Step 5: Return chart data
        return {"labels": labels, "values": values}

    def format_comparison_table(
        self, reference: list[str], predicted: list[str], metrics: dict[str, float]
    ) -> str:
        """Format trajectory comparison table for visual display.

        Args:
            reference: Reference trajectory (ground truth actions)
            predicted: Predicted trajectory (agent actions)
            metrics: Evaluation metrics (0.0 to 1.0 scores)

        Returns:
            Formatted string table with trajectory comparison and metrics

        Raises:
            TypeError: If inputs are not correct types
            ValueError: If lists don't contain only strings
        """
        # Step 1: Type checking
        if not isinstance(reference, list):
            raise TypeError("reference must be a list")
        if not isinstance(predicted, list):
            raise TypeError("predicted must be a list")
        if not isinstance(metrics, dict):
            raise TypeError("metrics must be a dict")

        # Step 2: Value validation
        if not all(isinstance(action, str) for action in reference):
            raise ValueError("reference must contain only strings")
        if not all(isinstance(action, str) for action in predicted):
            raise ValueError("predicted must contain only strings")

        # Step 3: Build table header
        table = "Trajectory Comparison\n"
        table += "=" * 50 + "\n"

        # Step 4: Add trajectories
        table += f"Reference:  {', '.join(reference)}\n"
        table += f"Predicted:  {', '.join(predicted)}\n"
        table += "-" * 50 + "\n"

        # Step 5: Add metrics
        table += "Metrics:\n"
        for metric, score in metrics.items():
            # Format score as percentage or decimal
            if score >= 0.01:
                table += f"  {metric}: {score:.2f}\n"
            else:
                table += f"  {metric}: {score}\n"

        # Step 6: Return
        return table
