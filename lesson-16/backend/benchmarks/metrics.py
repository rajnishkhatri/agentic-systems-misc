"""Evaluation metrics for AgentArch benchmark suite.

This module implements 4 core metrics for comparing orchestration patterns:
1. Task Success Rate: Percentage of tasks completed correctly
2. Error Propagation Index: Average downstream errors per upstream error
3. Latency Percentiles: P50/P95 latency distribution
4. Cost: Total LLM API call costs with model-specific pricing

Reference:
    AgentArch: Comparing AI Agent Architectures (arXiv:2509.10769)
    FR5.2: Metric Definitions

Usage:
    from lesson_16.backend.benchmarks.metrics import MetricsCalculator, OPENAI_PRICING

    calc = MetricsCalculator()
    success_rate = calc.calculate_task_success_rate(predictions, gold_labels)
    epi = calc.calculate_error_propagation_index(workflow_traces)
    latency = calc.calculate_latency_percentiles([1.5, 2.3, 5.7])
    cost = calc.calculate_cost(api_calls, pricing=OPENAI_PRICING)
"""

from __future__ import annotations

from difflib import SequenceMatcher
from typing import Any, TypedDict

import numpy as np

# ============================================================================
# Type Definitions
# ============================================================================


class WorkflowStep(TypedDict, total=False):
    """Single step in workflow execution trace.

    Attributes:
        agent: Name of agent executing this step
        success: Whether step succeeded
        error: Error message if failed, None otherwise
        isolated: Whether this step has isolation boundary
        validation_gate: Whether this step is validation gate
    """

    agent: str
    success: bool
    error: str | None
    isolated: bool
    validation_gate: bool


class WorkflowTrace(TypedDict):
    """Complete workflow execution trace.

    Attributes:
        workflow_id: Unique identifier for workflow
        steps: List of execution steps in order
    """

    workflow_id: str
    steps: list[WorkflowStep]


class APICall(TypedDict):
    """Single LLM API call record.

    Attributes:
        call_id: Unique identifier for API call
        model: Model name (e.g., "gpt-4", "gpt-3.5-turbo")
        prompt_tokens: Number of prompt tokens
        completion_tokens: Number of completion tokens
    """

    call_id: str
    model: str
    prompt_tokens: int
    completion_tokens: int


class CostSummary(TypedDict, total=False):
    """Cost calculation summary.

    Attributes:
        total_calls: Total number of API calls
        total_cost: Total cost in USD
        cost_per_task: Average cost per task
        cost_multiplier: Cost relative to baseline
    """

    total_calls: int
    total_cost: float
    cost_per_task: float
    cost_multiplier: float


class LatencyDistribution(TypedDict):
    """Latency distribution for visualization.

    Attributes:
        bins: Bin edges for histogram
        counts: Count in each bin
    """

    bins: list[float]
    counts: list[int]


# ============================================================================
# OpenAI Pricing (as of 2025)
# ============================================================================

OPENAI_PRICING: dict[str, dict[str, float]] = {
    "gpt-4": {
        "prompt": 0.03 / 1000,  # $0.03 per 1K tokens
        "completion": 0.06 / 1000,  # $0.06 per 1K tokens
    },
    "gpt-4-turbo": {
        "prompt": 0.01 / 1000,
        "completion": 0.03 / 1000,
    },
    "gpt-3.5-turbo": {
        "prompt": 0.0015 / 1000,  # $0.0015 per 1K tokens
        "completion": 0.002 / 1000,  # $0.002 per 1K tokens
    },
}


# ============================================================================
# MetricsCalculator Class
# ============================================================================


class MetricsCalculator:
    """Calculator for 4 core AgentArch benchmark metrics.

    This class implements all metrics with defensive coding:
    - Type validation on all inputs
    - Empty list handling
    - Edge case coverage (all correct, all wrong, timeouts)
    - Formulas documented in docstrings

    Metrics:
        1. Task Success Rate: % of predictions matching gold labels
        2. Error Propagation Index: Avg downstream errors per workflow
        3. Latency Percentiles: P50/P95 distribution
        4. Cost: Total USD cost with model-specific pricing
    """

    def __init__(self) -> None:
        """Initialize MetricsCalculator."""
        pass

    # ========================================================================
    # Metric 1: Task Success Rate
    # ========================================================================

    def calculate_task_success_rate(
        self,
        predictions: list[Any],
        gold_labels: list[Any],
        match_type: str = "exact",
        threshold: float = 0.8,
    ) -> float:
        """Calculate task success rate using various matching strategies.

        Formula:
            success_rate = (num_correct / total_predictions) * 100

        Args:
            predictions: List of predicted outputs
            gold_labels: List of ground truth labels
            match_type: Matching strategy ("exact", "case_insensitive", "fuzzy")
            threshold: Similarity threshold for fuzzy matching (0.0-1.0)

        Returns:
            Success rate as percentage (0.0-1.0)

        Raises:
            TypeError: If predictions/gold_labels not lists
            ValueError: If lengths don't match or threshold invalid
        """
        # Step 1: Type checking
        if not isinstance(predictions, list):
            raise TypeError("predictions must be a list")
        if not isinstance(gold_labels, list):
            raise TypeError("gold_labels must be a list")
        if not isinstance(match_type, str):
            raise TypeError("match_type must be a string")

        # Step 2: Input validation
        if len(predictions) != len(gold_labels):
            raise ValueError("predictions and gold_labels must have same length")
        if not 0.0 <= threshold <= 1.0:
            raise ValueError("threshold must be between 0.0 and 1.0")

        # Step 3: Edge case - empty lists
        if len(predictions) == 0:
            return 0.0

        # Step 4: Calculate matches based on strategy
        correct_count = 0
        for pred, gold in zip(predictions, gold_labels):
            if match_type == "exact":
                if pred == gold:
                    correct_count += 1
            elif match_type == "case_insensitive":
                if str(pred).lower() == str(gold).lower():
                    correct_count += 1
            elif match_type == "fuzzy":
                similarity = SequenceMatcher(None, str(pred), str(gold)).ratio()
                if similarity >= threshold:
                    correct_count += 1
            else:
                raise ValueError(f"Invalid match_type: {match_type}")

        # Step 5: Return success rate
        return correct_count / len(predictions)

    # ========================================================================
    # Metric 2: Error Propagation Index
    # ========================================================================

    def calculate_error_propagation_index(self, workflow_traces: list[WorkflowTrace]) -> float:
        """Calculate average error propagation index across workflows.

        Formula:
            EPI = avg(downstream_errors_per_workflow)
            downstream_errors = count of failures after first error (excluding first)

        Isolation boundaries and validation gates stop propagation counting.

        Args:
            workflow_traces: List of workflow execution traces

        Returns:
            Average downstream errors per workflow (0.0+)

        Raises:
            TypeError: If workflow_traces not a list
            ValueError: If workflow_traces empty or malformed
        """
        # Step 1: Type checking
        if not isinstance(workflow_traces, list):
            raise TypeError("workflow_traces must be a list")

        # Step 2: Edge case - empty traces
        if len(workflow_traces) == 0:
            return 0.0

        # Step 3: Calculate EPI for each workflow
        epi_values: list[float] = []

        for trace in workflow_traces:
            if not isinstance(trace, dict) or "steps" not in trace:
                raise ValueError("Each trace must be dict with 'steps' key")

            steps = trace["steps"]
            downstream_errors = 0
            first_error_occurred = False

            for step in steps:
                # Check for isolation boundary or validation gate
                if step.get("isolated") or step.get("validation_gate"):
                    # Reset error tracking - isolation stops propagation
                    first_error_occurred = False
                    continue

                # Count downstream errors (errors after first error)
                if not step["success"]:
                    if first_error_occurred:
                        downstream_errors += 1
                    else:
                        first_error_occurred = True

            epi_values.append(float(downstream_errors))

        # Step 4: Return average EPI
        return sum(epi_values) / len(epi_values) if epi_values else 0.0

    # ========================================================================
    # Metric 3: Latency Percentiles
    # ========================================================================

    def calculate_latency_percentiles(
        self, latencies: list[float], percentiles: list[int] | None = None
    ) -> dict[int, float]:
        """Calculate latency percentiles using numpy.

        Formula:
            P50 = median(latencies)
            P95 = 95th percentile(latencies)

        Args:
            latencies: List of latency values in seconds
            percentiles: List of percentile values (e.g., [50, 95])

        Returns:
            Dictionary mapping percentile -> latency value

        Raises:
            TypeError: If latencies not a list or contains non-numeric values
            ValueError: If latencies empty or percentiles invalid
        """
        # Step 1: Type checking
        if not isinstance(latencies, list):
            raise TypeError("latencies must be a list")
        if percentiles is None:
            percentiles = [50, 95]
        if not isinstance(percentiles, list):
            raise TypeError("percentiles must be a list")

        # Step 2: Input validation
        if len(latencies) == 0:
            raise ValueError("latencies cannot be empty")
        if any(not isinstance(p, int) or p < 0 or p > 100 for p in percentiles):
            raise ValueError("percentiles must be integers between 0 and 100")

        # Step 3: Calculate percentiles using numpy
        latency_array = np.array(latencies)
        result: dict[int, float] = {}

        for p in percentiles:
            result[p] = float(np.percentile(latency_array, p))

        # Step 4: Return percentile dictionary
        return result

    def calculate_parallel_latency(self, parallel_latencies: list[list[float]]) -> float:
        """Calculate total latency for parallel execution groups.

        For parallel execution, latency is MAX of concurrent operations,
        not SUM. Total latency is sum of max latencies per group.

        Args:
            parallel_latencies: List of latency groups (each group runs in parallel)

        Returns:
            Total latency in seconds

        Raises:
            TypeError: If parallel_latencies not list of lists
            ValueError: If any group empty
        """
        # Step 1: Type checking
        if not isinstance(parallel_latencies, list):
            raise TypeError("parallel_latencies must be a list")

        # Step 2: Input validation
        if len(parallel_latencies) == 0:
            return 0.0

        # Step 3: Calculate max per group, sum across groups
        total_latency = 0.0
        for group in parallel_latencies:
            if not isinstance(group, list) or len(group) == 0:
                raise ValueError("Each group must be non-empty list")
            total_latency += max(group)

        # Step 4: Return total latency
        return total_latency

    def get_latency_distribution(self, latencies: list[float], bins: int = 10) -> LatencyDistribution:
        """Get latency distribution data for visualization.

        Args:
            latencies: List of latency values
            bins: Number of histogram bins

        Returns:
            Dictionary with bin edges and counts

        Raises:
            TypeError: If latencies not a list
            ValueError: If bins < 1
        """
        # Step 1: Type checking
        if not isinstance(latencies, list):
            raise TypeError("latencies must be a list")
        if not isinstance(bins, int):
            raise TypeError("bins must be an integer")

        # Step 2: Input validation
        if bins < 1:
            raise ValueError("bins must be >= 1")
        if len(latencies) == 0:
            return {"bins": [], "counts": []}

        # Step 3: Calculate histogram
        counts, bin_edges = np.histogram(latencies, bins=bins)

        # Step 4: Return distribution
        return {
            "bins": bin_edges.tolist(),
            "counts": counts.tolist(),
        }

    # ========================================================================
    # Metric 4: Cost in LLM API Calls
    # ========================================================================

    def calculate_cost(
        self,
        api_calls: list[APICall],
        pricing: dict[str, dict[str, float]] | None = None,
        task_count: int | None = None,
        baseline_cost: float | None = None,
    ) -> CostSummary:
        """Calculate total cost of LLM API calls with model-specific pricing.

        Formula:
            cost = (prompt_tokens * prompt_price) + (completion_tokens * completion_price)
            total_cost = sum(cost for all calls)
            cost_per_task = total_cost / task_count
            cost_multiplier = cost_per_task / baseline_cost

        Args:
            api_calls: List of API call records
            pricing: Model pricing dict (defaults to OPENAI_PRICING)
            task_count: Number of tasks for per-task cost calculation
            baseline_cost: Baseline cost for multiplier calculation

        Returns:
            Cost summary with total_calls, total_cost, cost_per_task, cost_multiplier

        Raises:
            TypeError: If api_calls not a list
            ValueError: If pricing missing for model or negative costs
        """
        # Step 1: Type checking
        if not isinstance(api_calls, list):
            raise TypeError("api_calls must be a list")
        if pricing is None:
            pricing = OPENAI_PRICING

        # Step 2: Edge case - empty calls
        if len(api_calls) == 0:
            return {
                "total_calls": 0,
                "total_cost": 0.0,
                "cost_per_task": 0.0,
                "cost_multiplier": 0.0,
            }

        # Step 3: Calculate total cost
        total_cost = 0.0

        for call in api_calls:
            if not isinstance(call, dict):
                raise TypeError("Each API call must be a dict")

            model = call.get("model")
            prompt_tokens = call.get("prompt_tokens", 0)
            completion_tokens = call.get("completion_tokens", 0)

            if model not in pricing:
                raise ValueError(f"Pricing not available for model: {model}")

            model_pricing = pricing[model]
            call_cost = (prompt_tokens * model_pricing["prompt"]) + (
                completion_tokens * model_pricing["completion"]
            )
            total_cost += call_cost

        # Step 4: Calculate per-task metrics
        cost_summary: CostSummary = {
            "total_calls": len(api_calls),
            "total_cost": total_cost,
        }

        if task_count is not None and task_count > 0:
            cost_summary["cost_per_task"] = total_cost / task_count

            if baseline_cost is not None and baseline_cost > 0:
                cost_summary["cost_multiplier"] = cost_summary["cost_per_task"] / baseline_cost

        # Step 5: Return cost summary
        return cost_summary
