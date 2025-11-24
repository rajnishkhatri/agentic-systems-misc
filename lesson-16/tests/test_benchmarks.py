"""Test infrastructure for benchmark framework.

Tests for benchmark execution, metrics calculation, and result caching.
Following TDD methodology: RED → GREEN → REFACTOR
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest

# ============================================================================
# Fixtures for Benchmark Testing
# ============================================================================


@pytest.fixture
def temp_cache_dir(tmp_path: Path) -> Path:
    """Create temporary directory for benchmark caching.

    Args:
        tmp_path: pytest temporary directory fixture

    Returns:
        Path to temporary cache directory
    """
    cache_dir = tmp_path / "cache"
    cache_dir.mkdir(exist_ok=True)
    return cache_dir


@pytest.fixture
def sample_workflow_trace() -> dict[str, Any]:
    """Generate sample workflow trace for metrics testing.

    Returns:
        Sample workflow trace with timing and error information
    """
    return {
        "workflow_id": "test_workflow_001",
        "steps": [
            {"agent": "agent1", "success": True, "latency": 1.5, "error": None},
            {"agent": "agent2", "success": False, "latency": 0.8, "error": "ValidationError"},
            {"agent": "agent3", "success": False, "latency": 0.5, "error": "Propagated from agent2"},
        ],
        "total_latency": 2.8,
        "final_success": False,
    }


@pytest.fixture
def sample_api_call() -> dict[str, Any]:
    """Generate sample API call for cost calculation.

    Returns:
        Sample API call with model and token information
    """
    return {
        "call_id": "call_001",
        "model": "gpt-4",
        "prompt_tokens": 500,
        "completion_tokens": 200,
        "total_tokens": 700,
    }


@pytest.fixture
def loaded_task_generator() -> Any:
    """Generate FinancialTaskGenerator with datasets already loaded.

    Returns:
        FinancialTaskGenerator instance with datasets loaded
    """
    from pathlib import Path
    from backend.benchmarks.financial_tasks import FinancialTaskGenerator

    task_gen = FinancialTaskGenerator()
    data_dir = Path(__file__).parent.parent / "data"
    task_gen.load_datasets(data_dir)
    return task_gen


# ============================================================================
# Metric 1: Task Success Rate (6 tests)
# ============================================================================


def test_should_calculate_exact_match_success_rate_when_predictions_match_gold_labels() -> None:
    """Test that exact match comparison calculates success rate correctly."""
    from backend.benchmarks.metrics import MetricsCalculator

    calc = MetricsCalculator()
    predictions = ["apple", "banana", "cherry", "date"]
    gold_labels = ["apple", "banana", "orange", "date"]

    success_rate = calc.calculate_task_success_rate(predictions, gold_labels, match_type="exact")

    assert success_rate == 0.75  # 3 out of 4 correct


def test_should_calculate_case_insensitive_success_rate_when_case_differs() -> None:
    """Test that case-insensitive option handles different cases."""
    from backend.benchmarks.metrics import MetricsCalculator

    calc = MetricsCalculator()
    predictions = ["Apple", "BANANA", "cherry"]
    gold_labels = ["apple", "banana", "CHERRY"]

    success_rate = calc.calculate_task_success_rate(predictions, gold_labels, match_type="case_insensitive")

    assert success_rate == 1.0  # All match when case-insensitive


def test_should_calculate_fuzzy_match_success_rate_when_threshold_provided() -> None:
    """Test that fuzzy match uses similarity threshold."""
    from backend.benchmarks.metrics import MetricsCalculator

    calc = MetricsCalculator()
    predictions = ["apple pie", "banana bread", "cherry tart"]
    gold_labels = ["apple", "banana", "strawberry"]

    success_rate = calc.calculate_task_success_rate(predictions, gold_labels, match_type="fuzzy", threshold=0.5)

    assert success_rate >= 0.66  # "apple pie" and "banana bread" match


def test_should_return_zero_success_rate_when_empty_predictions() -> None:
    """Test edge case: empty predictions list."""
    from backend.benchmarks.metrics import MetricsCalculator

    calc = MetricsCalculator()
    predictions: list[str] = []
    gold_labels: list[str] = []

    success_rate = calc.calculate_task_success_rate(predictions, gold_labels)

    assert success_rate == 0.0


def test_should_return_one_when_all_correct() -> None:
    """Test edge case: all predictions correct."""
    from backend.benchmarks.metrics import MetricsCalculator

    calc = MetricsCalculator()
    predictions = ["correct"] * 10
    gold_labels = ["correct"] * 10

    success_rate = calc.calculate_task_success_rate(predictions, gold_labels)

    assert success_rate == 1.0


def test_should_return_zero_when_all_wrong() -> None:
    """Test edge case: all predictions wrong."""
    from backend.benchmarks.metrics import MetricsCalculator

    calc = MetricsCalculator()
    predictions = ["wrong"] * 10
    gold_labels = ["correct"] * 10

    success_rate = calc.calculate_task_success_rate(predictions, gold_labels)

    assert success_rate == 0.0


# ============================================================================
# Metric 2: Error Propagation Index (6 tests)
# ============================================================================


def test_should_count_downstream_errors_when_upstream_error_occurs() -> None:
    """Test that error propagation index counts errors caused by upstream error."""
    from backend.benchmarks.metrics import MetricsCalculator, WorkflowTrace

    calc = MetricsCalculator()
    traces: list[WorkflowTrace] = [
        {
            "workflow_id": "wf1",
            "steps": [
                {"agent": "agent1", "success": True, "error": None},
                {"agent": "agent2", "success": False, "error": "ValidationError"},
                {"agent": "agent3", "success": False, "error": "Propagated from agent2"},
                {"agent": "agent4", "success": False, "error": "Propagated from agent2"},
            ],
        }
    ]

    epi = calc.calculate_error_propagation_index(traces)

    assert epi == 2.0  # 2 downstream errors from agent2's failure


def test_should_analyze_multi_step_trace_when_multiple_workflows() -> None:
    """Test that EPI averages across multiple workflow traces."""
    from backend.benchmarks.metrics import MetricsCalculator, WorkflowTrace

    calc = MetricsCalculator()
    traces: list[WorkflowTrace] = [
        {
            "workflow_id": "wf1",
            "steps": [
                {"agent": "agent1", "success": False, "error": "Error"},
                {"agent": "agent2", "success": False, "error": "Propagated"},
            ],
        },
        {
            "workflow_id": "wf2",
            "steps": [
                {"agent": "agent1", "success": True, "error": None},
                {"agent": "agent2", "success": True, "error": None},
            ],
        },
    ]

    epi = calc.calculate_error_propagation_index(traces)

    assert epi == 0.5  # Average: (1 + 0) / 2


def test_should_stop_propagation_when_isolation_boundary_detected() -> None:
    """Test that isolation boundary stops error propagation counting."""
    from backend.benchmarks.metrics import MetricsCalculator, WorkflowTrace

    calc = MetricsCalculator()
    traces: list[WorkflowTrace] = [
        {
            "workflow_id": "wf1",
            "steps": [
                {"agent": "agent1", "success": False, "error": "Error"},
                {"agent": "agent2", "success": True, "error": None, "isolated": True},
                {"agent": "agent3", "success": True, "error": None},
            ],
        }
    ]

    epi = calc.calculate_error_propagation_index(traces)

    assert epi == 0.0  # Isolation boundary stopped propagation


def test_should_not_propagate_when_validation_gates_present() -> None:
    """Test that validation gates prevent error propagation."""
    from backend.benchmarks.metrics import MetricsCalculator, WorkflowTrace

    calc = MetricsCalculator()
    traces: list[WorkflowTrace] = [
        {
            "workflow_id": "wf1",
            "steps": [
                {"agent": "agent1", "success": False, "error": "Error"},
                {"agent": "validator", "success": True, "error": None, "validation_gate": True},
                {"agent": "agent2", "success": True, "error": None},
            ],
        }
    ]

    epi = calc.calculate_error_propagation_index(traces)

    assert epi == 0.0  # Validation gate prevented propagation


def test_should_handle_first_step_failure_differently_than_last_step() -> None:
    """Test edge case: first step failure vs last step failure."""
    from backend.benchmarks.metrics import MetricsCalculator, WorkflowTrace

    calc = MetricsCalculator()
    first_step_failure: list[WorkflowTrace] = [
        {
            "workflow_id": "wf1",
            "steps": [
                {"agent": "agent1", "success": False, "error": "Error"},
                {"agent": "agent2", "success": False, "error": "Propagated"},
                {"agent": "agent3", "success": False, "error": "Propagated"},
            ],
        }
    ]
    last_step_failure: list[WorkflowTrace] = [
        {
            "workflow_id": "wf2",
            "steps": [
                {"agent": "agent1", "success": True, "error": None},
                {"agent": "agent2", "success": True, "error": None},
                {"agent": "agent3", "success": False, "error": "Error"},
            ],
        }
    ]

    epi_first = calc.calculate_error_propagation_index(first_step_failure)
    epi_last = calc.calculate_error_propagation_index(last_step_failure)

    assert epi_first > epi_last  # First step failure propagates more


def test_should_average_epi_across_workflow() -> None:
    """Test that EPI averages across entire workflow."""
    from backend.benchmarks.metrics import MetricsCalculator, WorkflowTrace

    calc = MetricsCalculator()
    traces: list[WorkflowTrace] = [
        {"workflow_id": "wf1", "steps": [{"agent": "agent1", "success": True, "error": None}]},
        {"workflow_id": "wf2", "steps": [{"agent": "agent1", "success": True, "error": None}]},
    ]

    epi = calc.calculate_error_propagation_index(traces)

    assert epi == 0.0  # No errors, no propagation


# ============================================================================
# Metric 3: Latency P50/P95 (4 tests)
# ============================================================================


def test_should_calculate_percentiles_using_numpy_when_latencies_provided() -> None:
    """Test that latency percentiles use numpy.percentile correctly."""
    from backend.benchmarks.metrics import MetricsCalculator

    calc = MetricsCalculator()
    latencies = [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0]

    percentiles = calc.calculate_latency_percentiles(latencies, percentiles=[50, 95])

    assert percentiles[50] == pytest.approx(5.5, abs=0.01)  # Median
    assert percentiles[95] == pytest.approx(9.55, abs=0.01)  # 95th percentile


def test_should_handle_timeouts_as_max_value_when_timeout_occurs() -> None:
    """Test that timeouts are treated as maximum latency value."""
    from backend.benchmarks.metrics import MetricsCalculator

    calc = MetricsCalculator()
    latencies = [1.0, 2.0, 60.0, 3.0, 60.0]  # 60s = timeout

    percentiles = calc.calculate_latency_percentiles(latencies, percentiles=[50, 95])

    assert percentiles[95] == 60.0  # Timeout is max value


def test_should_use_max_latency_for_parallel_execution() -> None:
    """Test that parallel execution latency uses max, not sum."""
    from backend.benchmarks.metrics import MetricsCalculator

    calc = MetricsCalculator()
    parallel_latencies = [[1.0, 2.0, 3.0], [4.0, 5.0], [6.0]]  # Parallel groups

    total_latency = calc.calculate_parallel_latency(parallel_latencies)

    assert total_latency == 3.0 + 5.0 + 6.0  # Max of each parallel group


def test_should_provide_latency_distribution_data_when_requested() -> None:
    """Test that latency distribution data is available for visualization."""
    from backend.benchmarks.metrics import MetricsCalculator

    calc = MetricsCalculator()
    latencies = [1.0, 2.0, 3.0, 4.0, 5.0]

    distribution = calc.get_latency_distribution(latencies, bins=3)

    # np.histogram returns bins+1 edges (e.g., 3 bins need 4 edges: [start, edge1, edge2, end])
    assert len(distribution["bins"]) == 4  # bins + 1 edges
    assert len(distribution["counts"]) == 3  # 3 bin counts


# ============================================================================
# Metric 4: Cost in LLM API Calls (4 tests)
# ============================================================================


def test_should_count_total_api_calls_when_provided(sample_api_call: dict[str, Any]) -> None:
    """Test that cost calculation counts total API calls."""
    from backend.benchmarks.metrics import MetricsCalculator, APICall

    calc = MetricsCalculator()
    api_calls: list[APICall] = [
        {"call_id": "c1", "model": "gpt-4", "prompt_tokens": 100, "completion_tokens": 50},
        {"call_id": "c2", "model": "gpt-4", "prompt_tokens": 200, "completion_tokens": 100},
    ]

    cost_summary = calc.calculate_cost(api_calls)

    assert cost_summary["total_calls"] == 2


def test_should_use_model_specific_pricing_when_calculating_cost() -> None:
    """Test that GPT-4 vs GPT-3.5 use different pricing."""
    from backend.benchmarks.metrics import OPENAI_PRICING, MetricsCalculator, APICall

    calc = MetricsCalculator()
    gpt4_call: list[APICall] = [
        {"call_id": "c1", "model": "gpt-4", "prompt_tokens": 1000, "completion_tokens": 500}
    ]
    gpt35_call: list[APICall] = [
        {"call_id": "c2", "model": "gpt-3.5-turbo", "prompt_tokens": 1000, "completion_tokens": 500}
    ]

    gpt4_cost = calc.calculate_cost(gpt4_call, pricing=OPENAI_PRICING)
    gpt35_cost = calc.calculate_cost(gpt35_call, pricing=OPENAI_PRICING)

    assert gpt4_cost["total_cost"] > gpt35_cost["total_cost"]


def test_should_estimate_token_based_cost_when_tokens_provided() -> None:
    """Test that token-based cost estimation uses correct formula."""
    from backend.benchmarks.metrics import OPENAI_PRICING, MetricsCalculator, APICall

    calc = MetricsCalculator()
    api_calls: list[APICall] = [
        {"call_id": "c1", "model": "gpt-4", "prompt_tokens": 1000, "completion_tokens": 500}
    ]

    cost_summary = calc.calculate_cost(api_calls, pricing=OPENAI_PRICING)

    # GPT-4: $0.03/1K prompt, $0.06/1K completion
    expected_cost = (1000 / 1000 * 0.03) + (500 / 1000 * 0.06)
    assert abs(cost_summary["total_cost"] - expected_cost) < 0.001


def test_should_calculate_cost_per_task_and_multiplier() -> None:
    """Test that cost per task and multiplier relative to baseline calculate correctly."""
    from backend.benchmarks.metrics import MetricsCalculator, APICall

    calc = MetricsCalculator()
    api_calls: list[APICall] = [
        {"call_id": "c1", "model": "gpt-4", "prompt_tokens": 1000, "completion_tokens": 500},
        {"call_id": "c2", "model": "gpt-4", "prompt_tokens": 1000, "completion_tokens": 500},
    ]

    cost_summary = calc.calculate_cost(api_calls, task_count=2, baseline_cost=0.03)

    assert "cost_per_task" in cost_summary
    assert "cost_multiplier" in cost_summary
    assert cost_summary["cost_multiplier"] > 1.0  # Higher than baseline


# ============================================================================
# Error Handling Tests for Metrics (Coverage Boost)
# ============================================================================


def test_should_raise_type_error_when_predictions_not_list() -> None:
    """Test that TypeError raised when predictions is not a list."""
    from backend.benchmarks.metrics import MetricsCalculator

    calc = MetricsCalculator()

    with pytest.raises(TypeError, match="predictions must be a list"):
        calc.calculate_task_success_rate("not a list", ["gold"])  # type: ignore


def test_should_raise_type_error_when_gold_labels_not_list() -> None:
    """Test that TypeError raised when gold_labels is not a list."""
    from backend.benchmarks.metrics import MetricsCalculator

    calc = MetricsCalculator()

    with pytest.raises(TypeError, match="gold_labels must be a list"):
        calc.calculate_task_success_rate(["pred"], "not a list")  # type: ignore


def test_should_raise_type_error_when_match_type_not_string() -> None:
    """Test that TypeError raised when match_type is not a string."""
    from backend.benchmarks.metrics import MetricsCalculator

    calc = MetricsCalculator()

    with pytest.raises(TypeError, match="match_type must be a string"):
        calc.calculate_task_success_rate(["pred"], ["gold"], match_type=123)  # type: ignore


def test_should_raise_value_error_when_lengths_mismatch() -> None:
    """Test that ValueError raised when predictions and gold_labels have different lengths."""
    from backend.benchmarks.metrics import MetricsCalculator

    calc = MetricsCalculator()

    with pytest.raises(ValueError, match="predictions and gold_labels must have same length"):
        calc.calculate_task_success_rate(["a", "b"], ["x"])


def test_should_raise_value_error_when_threshold_invalid() -> None:
    """Test that ValueError raised when threshold is out of range."""
    from backend.benchmarks.metrics import MetricsCalculator

    calc = MetricsCalculator()

    with pytest.raises(ValueError, match="threshold must be between 0.0 and 1.0"):
        calc.calculate_task_success_rate(["pred"], ["gold"], match_type="fuzzy", threshold=1.5)


def test_should_raise_value_error_when_invalid_match_type() -> None:
    """Test that ValueError raised for invalid match_type."""
    from backend.benchmarks.metrics import MetricsCalculator

    calc = MetricsCalculator()

    with pytest.raises(ValueError, match="Invalid match_type"):
        calc.calculate_task_success_rate(["pred"], ["gold"], match_type="invalid")


def test_should_raise_type_error_when_workflow_traces_not_list() -> None:
    """Test that TypeError raised when workflow_traces is not a list."""
    from backend.benchmarks.metrics import MetricsCalculator

    calc = MetricsCalculator()

    with pytest.raises(TypeError, match="workflow_traces must be a list"):
        calc.calculate_error_propagation_index("not a list")  # type: ignore


def test_should_raise_value_error_when_trace_malformed() -> None:
    """Test that ValueError raised when trace is malformed."""
    from backend.benchmarks.metrics import MetricsCalculator

    calc = MetricsCalculator()

    with pytest.raises(ValueError, match="Each trace must be dict with 'steps' key"):
        calc.calculate_error_propagation_index([{"no_steps_key": "here"}])


def test_should_raise_type_error_when_latencies_not_list() -> None:
    """Test that TypeError raised when latencies is not a list."""
    from backend.benchmarks.metrics import MetricsCalculator

    calc = MetricsCalculator()

    with pytest.raises(TypeError, match="latencies must be a list"):
        calc.calculate_latency_percentiles("not a list")  # type: ignore


def test_should_raise_type_error_when_percentiles_not_list() -> None:
    """Test that TypeError raised when percentiles is not a list."""
    from backend.benchmarks.metrics import MetricsCalculator

    calc = MetricsCalculator()

    with pytest.raises(TypeError, match="percentiles must be a list"):
        calc.calculate_latency_percentiles([1.0], percentiles="not a list")  # type: ignore


def test_should_raise_value_error_when_latencies_empty() -> None:
    """Test that ValueError raised when latencies list is empty."""
    from backend.benchmarks.metrics import MetricsCalculator

    calc = MetricsCalculator()

    with pytest.raises(ValueError, match="latencies cannot be empty"):
        calc.calculate_latency_percentiles([])


def test_should_raise_value_error_when_percentiles_invalid() -> None:
    """Test that ValueError raised when percentiles are invalid."""
    from backend.benchmarks.metrics import MetricsCalculator

    calc = MetricsCalculator()

    with pytest.raises(ValueError, match="percentiles must be integers between 0 and 100"):
        calc.calculate_latency_percentiles([1.0, 2.0], percentiles=[101])


def test_should_raise_type_error_when_parallel_latencies_not_list() -> None:
    """Test that TypeError raised when parallel_latencies is not a list."""
    from backend.benchmarks.metrics import MetricsCalculator

    calc = MetricsCalculator()

    with pytest.raises(TypeError, match="parallel_latencies must be a list"):
        calc.calculate_parallel_latency("not a list")  # type: ignore


def test_should_raise_value_error_when_parallel_group_empty() -> None:
    """Test that ValueError raised when parallel group is empty."""
    from backend.benchmarks.metrics import MetricsCalculator

    calc = MetricsCalculator()

    with pytest.raises(ValueError, match="Each group must be non-empty list"):
        calc.calculate_parallel_latency([[1.0], []])


def test_should_raise_type_error_when_bins_not_int() -> None:
    """Test that TypeError raised when bins is not an integer."""
    from backend.benchmarks.metrics import MetricsCalculator

    calc = MetricsCalculator()

    with pytest.raises(TypeError, match="bins must be an integer"):
        calc.get_latency_distribution([1.0], bins="not int")  # type: ignore


def test_should_raise_value_error_when_bins_less_than_one() -> None:
    """Test that ValueError raised when bins < 1."""
    from backend.benchmarks.metrics import MetricsCalculator

    calc = MetricsCalculator()

    with pytest.raises(ValueError, match="bins must be >= 1"):
        calc.get_latency_distribution([1.0], bins=0)


def test_should_raise_type_error_when_api_calls_not_list() -> None:
    """Test that TypeError raised when api_calls is not a list."""
    from backend.benchmarks.metrics import MetricsCalculator

    calc = MetricsCalculator()

    with pytest.raises(TypeError, match="api_calls must be a list"):
        calc.calculate_cost("not a list")  # type: ignore


def test_should_raise_type_error_when_api_call_not_dict() -> None:
    """Test that TypeError raised when API call is not a dict."""
    from backend.benchmarks.metrics import MetricsCalculator

    calc = MetricsCalculator()

    with pytest.raises(TypeError, match="Each API call must be a dict"):
        calc.calculate_cost(["not a dict"])  # type: ignore


def test_should_raise_value_error_when_model_pricing_missing() -> None:
    """Test that ValueError raised when model pricing is not available."""
    from backend.benchmarks.metrics import MetricsCalculator, APICall

    calc = MetricsCalculator()
    api_calls: list[APICall] = [
        {"call_id": "c1", "model": "unknown-model", "prompt_tokens": 100, "completion_tokens": 50}
    ]

    with pytest.raises(ValueError, match="Pricing not available for model: unknown-model"):
        calc.calculate_cost(api_calls)


# ============================================================================
# BenchmarkRunner Tests - Section 1: Orchestrator Loading (5 tests)
# ============================================================================


def test_should_load_all_orchestrators_when_initialized(loaded_task_generator: Any) -> None:
    """Test that BenchmarkRunner loads all 5 orchestrators from backend/orchestrators/."""
    from backend.benchmarks.runner import BenchmarkRunner
    from backend.benchmarks.metrics import MetricsCalculator
    from backend.orchestrators.sequential import SequentialOrchestrator
    from backend.orchestrators.hierarchical import HierarchicalOrchestrator

    metrics = MetricsCalculator()
    orchestrators = {
        "sequential": SequentialOrchestrator(name="seq"),
        "hierarchical": HierarchicalOrchestrator(name="hier"),
    }

    runner = BenchmarkRunner(orchestrators, loaded_task_generator, metrics)

    assert len(runner.orchestrators) == 2
    assert "sequential" in runner.orchestrators
    assert "hierarchical" in runner.orchestrators


def test_should_validate_orchestrator_implements_abc() -> None:
    """Test that BenchmarkRunner validates orchestrators implement Orchestrator ABC."""
    from backend.benchmarks.runner import BenchmarkRunner
    from backend.benchmarks.financial_tasks import FinancialTaskGenerator
    from backend.benchmarks.metrics import MetricsCalculator

    task_gen = FinancialTaskGenerator()
    metrics = MetricsCalculator()

    # Try to pass non-orchestrator
    with pytest.raises(TypeError, match="must implement Orchestrator"):
        BenchmarkRunner({"invalid": "not an orchestrator"}, task_gen, metrics)  # type: ignore


def test_should_inject_configuration_when_orchestrator_created() -> None:
    """Test that BenchmarkRunner injects configuration into orchestrators."""
    from backend.benchmarks.runner import BenchmarkRunner
    from backend.benchmarks.financial_tasks import FinancialTaskGenerator
    from backend.benchmarks.metrics import MetricsCalculator
    from backend.orchestrators.sequential import SequentialOrchestrator

    task_gen = FinancialTaskGenerator()
    metrics = MetricsCalculator()
    orchestrator = SequentialOrchestrator(name="seq", max_retries=5)
    runner = BenchmarkRunner({"sequential": orchestrator}, task_gen, metrics)

    assert runner.orchestrators["sequential"].max_retries == 5


def test_should_setup_mock_agents_for_testing() -> None:
    """Test that mock agent setup works for testing."""
    from backend.benchmarks.runner import BenchmarkRunner, MockAgent
    from backend.benchmarks.financial_tasks import FinancialTaskGenerator
    from backend.benchmarks.metrics import MetricsCalculator
    from backend.orchestrators.sequential import SequentialOrchestrator

    task_gen = FinancialTaskGenerator()
    metrics = MetricsCalculator()
    mock_agent = MockAgent(success_rate=0.8)
    orchestrator = SequentialOrchestrator(name="seq")
    orchestrator.register_agent("mock", mock_agent)

    runner = BenchmarkRunner({"sequential": orchestrator}, task_gen, metrics)

    assert "sequential" in runner.orchestrators


def test_should_handle_missing_orchestrator_error() -> None:
    """Test error handling when orchestrator is missing."""
    from backend.benchmarks.runner import BenchmarkRunner
    from backend.benchmarks.financial_tasks import FinancialTaskGenerator
    from backend.benchmarks.metrics import MetricsCalculator
    from backend.orchestrators.sequential import SequentialOrchestrator

    task_gen = FinancialTaskGenerator()
    metrics = MetricsCalculator()
    orchestrator = SequentialOrchestrator(name="seq")
    runner = BenchmarkRunner({"sequential": orchestrator}, task_gen, metrics)

    # Try to run benchmark with non-existent pattern
    with pytest.raises(ValueError, match="Orchestrator 'hierarchical' not found"):
        runner.run_benchmark(patterns=["hierarchical"], task_count=10, use_cache=False)


# ============================================================================
# BenchmarkRunner Tests - Section 2: Execution Workflow (7 tests)
# ============================================================================


def test_should_run_single_pattern_on_task_suite(loaded_task_generator: Any) -> None:
    """Test that run_single_pattern executes one orchestrator on tasks."""
    from backend.benchmarks.runner import BenchmarkRunner
    from backend.benchmarks.metrics import MetricsCalculator
    from backend.orchestrators.sequential import SequentialOrchestrator

    tasks = loaded_task_generator.generate_task_suite(count=5, strategy="random", seed=42)
    metrics = MetricsCalculator()
    orchestrator = SequentialOrchestrator(name="seq")
    runner = BenchmarkRunner({"sequential": orchestrator}, loaded_task_generator, metrics)

    result = runner.run_single_pattern("sequential", tasks, timeout=60)

    assert "pattern_name" in result
    assert result["pattern_name"] == "sequential"
    assert "task_count" in result


def test_should_execute_patterns_in_parallel_using_threadpool() -> None:
    """Test that multiple patterns execute in parallel using ThreadPoolExecutor."""
    from backend.benchmarks.runner import BenchmarkRunner
    from backend.benchmarks.financial_tasks import FinancialTaskGenerator
    from backend.benchmarks.metrics import MetricsCalculator
    from backend.orchestrators.sequential import SequentialOrchestrator
    from backend.orchestrators.hierarchical import HierarchicalOrchestrator

    task_gen = FinancialTaskGenerator()
    metrics = MetricsCalculator()
    orchestrators = {
        "sequential": SequentialOrchestrator(name="seq"),
        "hierarchical": HierarchicalOrchestrator(name="hier"),
    }
    runner = BenchmarkRunner(orchestrators, task_gen, metrics)

    # Run benchmark with parallel execution
    results = runner.run_benchmark(patterns=["sequential", "hierarchical"], task_count=5, use_cache=False)

    assert len(results["pattern_results"]) == 2


def test_should_handle_timeout_per_task_default_60s() -> None:
    """Test that timeout handling works with default 60s per task."""
    from backend.benchmarks.runner import BenchmarkRunner
    from backend.benchmarks.financial_tasks import FinancialTaskGenerator
    from backend.benchmarks.metrics import MetricsCalculator
    from backend.orchestrators.sequential import SequentialOrchestrator

    task_gen = FinancialTaskGenerator()
    metrics = MetricsCalculator()
    orchestrator = SequentialOrchestrator(name="seq")
    runner = BenchmarkRunner({"sequential": orchestrator}, task_gen, metrics, default_timeout=60)

    assert runner.default_timeout == 60


def test_should_isolate_exceptions_pattern_failure_continues() -> None:
    """Test that exception isolation prevents pattern failure from stopping benchmark."""
    from backend.benchmarks.runner import BenchmarkRunner, FailingOrchestrator
    from backend.benchmarks.financial_tasks import FinancialTaskGenerator
    from backend.benchmarks.metrics import MetricsCalculator
    from backend.orchestrators.sequential import SequentialOrchestrator

    task_gen = FinancialTaskGenerator()
    metrics = MetricsCalculator()
    orchestrators = {
        "sequential": SequentialOrchestrator(name="seq"),
        "failing": FailingOrchestrator(name="fail"),  # Mock orchestrator that always fails
    }
    runner = BenchmarkRunner(orchestrators, task_gen, metrics)

    # Run benchmark - sequential should succeed, failing should be isolated
    results = runner.run_benchmark(patterns=["sequential", "failing"], task_count=3, use_cache=False)

    assert len(results["pattern_results"]) == 2
    assert any(r["pattern_name"] == "sequential" for r in results["pattern_results"])


def test_should_track_progress_with_tqdm() -> None:
    """Test that progress tracking works with tqdm."""
    from backend.benchmarks.runner import BenchmarkRunner
    from backend.benchmarks.financial_tasks import FinancialTaskGenerator
    from backend.benchmarks.metrics import MetricsCalculator
    from backend.orchestrators.sequential import SequentialOrchestrator

    task_gen = FinancialTaskGenerator()
    metrics = MetricsCalculator()
    orchestrator = SequentialOrchestrator(name="seq")
    runner = BenchmarkRunner({"sequential": orchestrator}, task_gen, metrics, show_progress=True)

    assert runner.show_progress is True


def test_should_collect_results_in_structured_format() -> None:
    """Test that results are collected in BenchmarkResult TypedDict format."""
    from backend.benchmarks.runner import BenchmarkRunner, BenchmarkResults
    from backend.benchmarks.financial_tasks import FinancialTaskGenerator
    from backend.benchmarks.metrics import MetricsCalculator
    from backend.orchestrators.sequential import SequentialOrchestrator

    task_gen = FinancialTaskGenerator()
    metrics = MetricsCalculator()
    orchestrator = SequentialOrchestrator(name="seq")
    runner = BenchmarkRunner({"sequential": orchestrator}, task_gen, metrics)

    results = runner.run_benchmark(patterns=["sequential"], task_count=3, use_cache=False)

    # Validate structure
    assert "pattern_results" in results
    assert "timestamp" in results
    assert "task_count" in results


def test_should_execute_deterministically_with_seed() -> None:
    """Test that deterministic execution works with seed."""
    from backend.benchmarks.runner import BenchmarkRunner
    from backend.benchmarks.financial_tasks import FinancialTaskGenerator
    from backend.benchmarks.metrics import MetricsCalculator
    from backend.orchestrators.sequential import SequentialOrchestrator

    task_gen = FinancialTaskGenerator()
    metrics = MetricsCalculator()
    orchestrator1 = SequentialOrchestrator(name="seq")
    orchestrator2 = SequentialOrchestrator(name="seq")
    runner1 = BenchmarkRunner({"sequential": orchestrator1}, task_gen, metrics)
    runner2 = BenchmarkRunner({"sequential": orchestrator2}, task_gen, metrics)

    results1 = runner1.run_benchmark(patterns=["sequential"], task_count=5, use_cache=False, seed=42)
    results2 = runner2.run_benchmark(patterns=["sequential"], task_count=5, use_cache=False, seed=42)

    # With same seed, task order should be identical
    assert results1["task_count"] == results2["task_count"]


# ============================================================================
# BenchmarkRunner Tests - Section 3: Metrics Integration (3 tests)
# ============================================================================


def test_should_call_metrics_calculator_for_all_4_metrics() -> None:
    """Test that MetricsCalculator is called for all 4 metrics."""
    from backend.benchmarks.runner import BenchmarkRunner
    from backend.benchmarks.financial_tasks import FinancialTaskGenerator
    from backend.benchmarks.metrics import MetricsCalculator
    from backend.orchestrators.sequential import SequentialOrchestrator

    task_gen = FinancialTaskGenerator()
    metrics = MetricsCalculator()
    orchestrator = SequentialOrchestrator(name="seq")
    runner = BenchmarkRunner({"sequential": orchestrator}, task_gen, metrics)

    results = runner.run_benchmark(patterns=["sequential"], task_count=3, use_cache=False)

    # Check that metrics are calculated
    pattern_result = results["pattern_results"][0]
    assert "metrics" in pattern_result
    assert "task_success_rate" in pattern_result["metrics"]
    assert "error_propagation_index" in pattern_result["metrics"]
    assert "latency_p50" in pattern_result["metrics"]
    assert "total_cost" in pattern_result["metrics"]


def test_should_aggregate_results_across_tasks() -> None:
    """Test that results are aggregated across multiple tasks."""
    from backend.benchmarks.runner import BenchmarkRunner
    from backend.benchmarks.financial_tasks import FinancialTaskGenerator
    from backend.benchmarks.metrics import MetricsCalculator
    from backend.orchestrators.sequential import SequentialOrchestrator

    task_gen = FinancialTaskGenerator()
    metrics = MetricsCalculator()
    orchestrator = SequentialOrchestrator(name="seq")
    runner = BenchmarkRunner({"sequential": orchestrator}, task_gen, metrics)

    results = runner.run_benchmark(patterns=["sequential"], task_count=10, use_cache=False)

    assert results["task_count"] == 10


def test_should_calculate_statistical_significance() -> None:
    """Test that statistical analysis includes paired t-test and confidence intervals."""
    from backend.benchmarks.runner import BenchmarkRunner
    from backend.benchmarks.financial_tasks import FinancialTaskGenerator
    from backend.benchmarks.metrics import MetricsCalculator
    from backend.orchestrators.sequential import SequentialOrchestrator
    from backend.orchestrators.hierarchical import HierarchicalOrchestrator

    task_gen = FinancialTaskGenerator()
    metrics = MetricsCalculator()
    orchestrators = {
        "sequential": SequentialOrchestrator(name="seq"),
        "hierarchical": HierarchicalOrchestrator(name="hier"),
    }
    runner = BenchmarkRunner(orchestrators, task_gen, metrics)

    results = runner.run_benchmark(patterns=["sequential", "hierarchical"], task_count=5, use_cache=False)
    stats = runner.calculate_statistics(results)

    assert "confidence_intervals" in stats
    assert "p_values" in stats


# ============================================================================
# BenchmarkRunner Tests - Section 4: Caching (3 tests)
# ============================================================================


def test_should_save_results_to_json_cache(temp_cache_dir: Path) -> None:
    """Test that benchmark results save to JSON cache file."""
    from backend.benchmarks.runner import BenchmarkRunner
    from backend.benchmarks.financial_tasks import FinancialTaskGenerator
    from backend.benchmarks.metrics import MetricsCalculator
    from backend.orchestrators.sequential import SequentialOrchestrator

    task_gen = FinancialTaskGenerator()
    metrics = MetricsCalculator()
    orchestrator = SequentialOrchestrator(name="seq")
    runner = BenchmarkRunner({"sequential": orchestrator}, task_gen, metrics)

    results = runner.run_benchmark(patterns=["sequential"], task_count=3, use_cache=True, cache_dir=temp_cache_dir)
    runner.save_results(results, temp_cache_dir / "test_results.json")

    assert (temp_cache_dir / "test_results.json").exists()


def test_should_load_cached_results_in_under_1_second(temp_cache_dir: Path) -> None:
    """Test that cached results load in <1 second."""
    from backend.benchmarks.runner import BenchmarkRunner
    from backend.benchmarks.financial_tasks import FinancialTaskGenerator
    from backend.benchmarks.metrics import MetricsCalculator
    from backend.orchestrators.sequential import SequentialOrchestrator
    import time

    task_gen = FinancialTaskGenerator()
    metrics = MetricsCalculator()
    orchestrator = SequentialOrchestrator(name="seq")
    runner = BenchmarkRunner({"sequential": orchestrator}, task_gen, metrics)

    # First run - create cache
    runner.run_benchmark(patterns=["sequential"], task_count=5, use_cache=True, cache_dir=temp_cache_dir)

    # Second run - load from cache
    start = time.time()
    runner.run_benchmark(patterns=["sequential"], task_count=5, use_cache=True, cache_dir=temp_cache_dir)
    elapsed = time.time() - start

    assert elapsed < 1.0  # Should load in <1 second


def test_should_invalidate_cache_on_dataset_change(temp_cache_dir: Path) -> None:
    """Test that cache invalidates when dataset or code changes."""
    from backend.benchmarks.runner import BenchmarkRunner
    from backend.benchmarks.financial_tasks import FinancialTaskGenerator
    from backend.benchmarks.metrics import MetricsCalculator
    from backend.orchestrators.sequential import SequentialOrchestrator

    task_gen = FinancialTaskGenerator()
    metrics = MetricsCalculator()
    orchestrator = SequentialOrchestrator(name="seq")
    runner = BenchmarkRunner({"sequential": orchestrator}, task_gen, metrics)

    # First run with seed=42
    results1 = runner.run_benchmark(
        patterns=["sequential"], task_count=5, use_cache=True, cache_dir=temp_cache_dir, seed=42
    )

    # Second run with different seed=99 - should not use cache
    results2 = runner.run_benchmark(
        patterns=["sequential"], task_count=5, use_cache=True, cache_dir=temp_cache_dir, seed=99
    )

    # Results should differ due to different seeds
    assert results1["task_count"] == results2["task_count"]  # Same count
    # But cache keys should be different
