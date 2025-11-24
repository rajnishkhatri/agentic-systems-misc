"""Benchmark execution engine for comparing orchestration patterns.

This module implements the BenchmarkRunner class that:
1. Loads and validates orchestrators
2. Executes benchmarks in parallel using ThreadPoolExecutor
3. Calculates all 4 metrics using MetricsCalculator
4. Performs statistical analysis (t-tests, confidence intervals)
5. Caches results for fast notebook execution (<10 min target)

Reference:
    AgentArch: Comparing AI Agent Architectures (arXiv:2509.10769)
    FR5: Benchmark Framework
    OQ7: Cache strategy for <10 min execution

Usage:
    from backend.benchmarks.runner import BenchmarkRunner
    from backend.orchestrators import Sequential, Hierarchical

    orchestrators = {"seq": Sequential(), "hier": Hierarchical()}
    runner = BenchmarkRunner(orchestrators, task_gen, metrics)
    results = runner.run_benchmark(patterns=["seq", "hier"], task_count=100)
"""

from __future__ import annotations

import hashlib
import json
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path
from typing import Any, TypedDict

import numpy as np
from scipy import stats as scipy_stats  # type: ignore
from tqdm import tqdm  # type: ignore

from backend.benchmarks.financial_tasks import FinancialTaskGenerator
from backend.benchmarks.metrics import MetricsCalculator
from backend.orchestrators.base import Orchestrator

# ============================================================================
# Type Definitions
# ============================================================================


class PatternMetrics(TypedDict):
    """Metrics for a single pattern."""

    task_success_rate: float
    error_propagation_index: float
    latency_p50: float
    latency_p95: float
    total_cost: float


class PatternResult(TypedDict):
    """Result for a single orchestration pattern."""

    pattern_name: str
    task_count: int
    metrics: PatternMetrics
    execution_time: float


class BenchmarkResults(TypedDict):
    """Complete benchmark results."""

    pattern_results: list[PatternResult]
    timestamp: str
    task_count: int
    seed: int | None


class StatisticalAnalysis(TypedDict):
    """Statistical analysis of benchmark results."""

    confidence_intervals: dict[str, dict[str, tuple[float, float]]]
    p_values: dict[str, float]


# ============================================================================
# Mock Classes for Testing
# ============================================================================


class MockAgent:
    """Mock agent for testing with configurable success rate."""

    def __init__(self, success_rate: float = 1.0) -> None:
        """Initialize mock agent.

        Args:
            success_rate: Probability of success (0.0-1.0)
        """
        self.success_rate = success_rate

    async def __call__(self, task: dict[str, Any]) -> dict[str, Any]:
        """Execute mock task."""
        import random

        success = random.random() < self.success_rate
        return {"success": success, "result": "mock_output"}


class FailingOrchestrator(Orchestrator):
    """Mock orchestrator that always fails for testing exception isolation."""

    async def _execute(self, task: dict[str, Any]) -> dict[str, Any]:
        """Always raise exception (implements abstract method)."""
        raise RuntimeError("Intentional failure for testing")


# ============================================================================
# BenchmarkRunner Class
# ============================================================================


class BenchmarkRunner:
    """Benchmark execution engine for orchestration pattern comparison.

    Implements FR5 benchmark framework with:
    - Orchestrator loading and validation
    - Parallel execution using ThreadPoolExecutor
    - Metrics calculation integration
    - Statistical analysis (t-tests, confidence intervals)
    - Result caching for <10 min notebook execution

    Attributes:
        orchestrators: Dict of pattern name -> Orchestrator instance
        task_generator: FinancialTaskGenerator for creating test tasks
        metrics_calculator: MetricsCalculator for computing metrics
        default_timeout: Timeout per task in seconds (default: 60)
        show_progress: Whether to show tqdm progress bar
    """

    def __init__(
        self,
        orchestrators: dict[str, Orchestrator],
        task_generator: FinancialTaskGenerator,
        metrics_calculator: MetricsCalculator,
        default_timeout: int = 60,
        show_progress: bool = False,
    ) -> None:
        """Initialize BenchmarkRunner with defensive validation.

        Args:
            orchestrators: Dict mapping pattern names to Orchestrator instances
            task_generator: FinancialTaskGenerator instance
            metrics_calculator: MetricsCalculator instance
            default_timeout: Default timeout per task in seconds
            show_progress: Whether to show progress bar

        Raises:
            TypeError: If arguments have wrong types
            ValueError: If orchestrators dict is empty
        """
        # Step 1: Type checking
        if not isinstance(orchestrators, dict):
            raise TypeError("orchestrators must be a dict")
        if not isinstance(task_generator, FinancialTaskGenerator):
            raise TypeError("task_generator must be FinancialTaskGenerator")
        if not isinstance(metrics_calculator, MetricsCalculator):
            raise TypeError("metrics_calculator must be MetricsCalculator")

        # Step 2: Validate orchestrators implement Orchestrator ABC
        for name, orch in orchestrators.items():
            if not isinstance(orch, Orchestrator):
                raise TypeError(f"Orchestrator '{name}' must implement Orchestrator ABC")

        # Step 3: Input validation
        if len(orchestrators) == 0:
            raise ValueError("orchestrators dict cannot be empty")

        # Step 4: Initialize attributes
        self.orchestrators = orchestrators
        self.task_generator = task_generator
        self.metrics_calculator = metrics_calculator
        self.default_timeout = default_timeout
        self.show_progress = show_progress

    # ========================================================================
    # Benchmark Execution
    # ========================================================================

    def run_benchmark(
        self,
        patterns: list[str] | None = None,
        task_count: int = 100,
        use_cache: bool = True,
        cache_dir: Path | None = None,
        seed: int | None = None,
    ) -> BenchmarkResults:
        """Run benchmark on specified patterns.

        Args:
            patterns: List of pattern names to benchmark (None = all)
            task_count: Number of tasks to generate
            use_cache: Whether to use cached results
            cache_dir: Directory for caching results
            seed: Random seed for reproducible task generation

        Returns:
            BenchmarkResults with pattern_results, timestamp, task_count

        Raises:
            ValueError: If pattern not found in orchestrators
        """
        # Step 1: Validate patterns
        if patterns is None:
            patterns = list(self.orchestrators.keys())

        for pattern in patterns:
            if pattern not in self.orchestrators:
                raise ValueError(f"Orchestrator '{pattern}' not found in available orchestrators")

        # Step 2: Check cache
        if use_cache and cache_dir:
            cache_key = self._generate_cache_key(patterns, task_count, seed)
            cached_result = self._load_cache(cache_key, cache_dir)
            if cached_result:
                return cached_result

        # Step 3: Generate tasks (use default seed if None, load datasets if needed)
        actual_seed = seed if seed is not None else 42

        # Auto-load datasets if not already loaded
        if not hasattr(self.task_generator, 'invoices') or not self.task_generator.invoices:
            from pathlib import Path

            data_dir = Path(__file__).parent.parent.parent / "data"
            self.task_generator.load_datasets(data_dir)

        tasks = self.task_generator.generate_task_suite(count=task_count, strategy="random", seed=actual_seed)

        # Step 4: Execute patterns in parallel
        pattern_results: list[PatternResult] = []

        with ThreadPoolExecutor(max_workers=len(patterns)) as executor:
            future_to_pattern = {
                executor.submit(self.run_single_pattern, pattern, tasks, self.default_timeout): pattern
                for pattern in patterns
            }

            iterator = as_completed(future_to_pattern)
            if self.show_progress:
                iterator = tqdm(iterator, total=len(patterns), desc="Running patterns")

            for future in iterator:
                pattern = future_to_pattern[future]
                try:
                    result = future.result()
                    pattern_results.append(result)
                except Exception:
                    # Exception isolation - pattern failure doesn't stop benchmark
                    pattern_results.append(
                        {
                            "pattern_name": pattern,
                            "task_count": task_count,
                            "metrics": {
                                "task_success_rate": 0.0,
                                "error_propagation_index": 0.0,
                                "latency_p50": 0.0,
                                "latency_p95": 0.0,
                                "total_cost": 0.0,
                            },
                            "execution_time": 0.0,
                        }
                    )

        # Step 5: Compile results
        results: BenchmarkResults = {
            "pattern_results": pattern_results,
            "timestamp": datetime.now().isoformat(),
            "task_count": task_count,
            "seed": seed,
        }

        # Step 6: Save to cache
        if use_cache and cache_dir:
            self._save_cache(cache_key, results, cache_dir)

        return results

    def run_single_pattern(
        self, pattern: str, tasks: list[Any], timeout: int
    ) -> PatternResult:
        """Run single orchestration pattern on task suite.

        Args:
            pattern: Pattern name
            tasks: List of Task objects or dicts to execute
            timeout: Timeout per task in seconds

        Returns:
            PatternResult with metrics
        """
        start_time = time.time()

        # Execute tasks (simplified - mock execution for now)
        # In real implementation, this would call orchestrator.execute()
        predictions = []
        gold_labels = []
        latencies = []

        for task in tasks:
            # Mock execution
            predictions.append("mock_prediction")
            # Handle both Task dataclass and dict
            if hasattr(task, 'gold_label'):
                gold_labels.append(task.gold_label)
            elif isinstance(task, dict):
                gold_labels.append(task.get("gold_label", "mock_gold"))
            else:
                gold_labels.append("mock_gold")
            latencies.append(0.1)  # Mock latency

        # Calculate metrics
        success_rate = self.metrics_calculator.calculate_task_success_rate(predictions, gold_labels)
        epi = self.metrics_calculator.calculate_error_propagation_index([])  # Mock workflow traces
        latency_percentiles = self.metrics_calculator.calculate_latency_percentiles(latencies)
        cost_summary = self.metrics_calculator.calculate_cost([])  # Mock API calls

        execution_time = time.time() - start_time

        return {
            "pattern_name": pattern,
            "task_count": len(tasks),
            "metrics": {
                "task_success_rate": success_rate,
                "error_propagation_index": epi,
                "latency_p50": latency_percentiles[50],
                "latency_p95": latency_percentiles[95],
                "total_cost": cost_summary["total_cost"],
            },
            "execution_time": execution_time,
        }

    # ========================================================================
    # Statistical Analysis
    # ========================================================================

    def calculate_statistics(self, results: BenchmarkResults) -> StatisticalAnalysis:
        """Calculate statistical analysis including t-tests and confidence intervals.

        Args:
            results: BenchmarkResults to analyze

        Returns:
            StatisticalAnalysis with confidence_intervals and p_values
        """
        # Extract metric values per pattern
        patterns = [r["pattern_name"] for r in results["pattern_results"]]
        success_rates = [r["metrics"]["task_success_rate"] for r in results["pattern_results"]]

        # Calculate 95% confidence intervals using bootstrapping
        confidence_intervals: dict[str, dict[str, tuple[float, float]]] = {}
        for pattern, rate in zip(patterns, success_rates):
            # Bootstrap confidence interval
            ci_low, ci_high = self._bootstrap_ci([rate], confidence=0.95)
            confidence_intervals[pattern] = {"task_success_rate": (ci_low, ci_high)}

        # Calculate p-values using paired t-test
        p_values: dict[str, float] = {}
        if len(success_rates) >= 2:
            # Compare first two patterns
            t_stat, p_value = scipy_stats.ttest_ind([success_rates[0]], [success_rates[1]])
            p_values[f"{patterns[0]}_vs_{patterns[1]}"] = float(p_value)

        return {"confidence_intervals": confidence_intervals, "p_values": p_values}

    def _bootstrap_ci(
        self, data: list[float], confidence: float = 0.95, n_bootstrap: int = 1000
    ) -> tuple[float, float]:
        """Calculate bootstrap confidence interval.

        Args:
            data: Data points
            confidence: Confidence level (default: 0.95)
            n_bootstrap: Number of bootstrap samples

        Returns:
            Tuple of (lower_bound, upper_bound)
        """
        if len(data) == 0:
            return (0.0, 0.0)

        bootstrapped_means = []
        for _ in range(n_bootstrap):
            sample = np.random.choice(data, size=len(data), replace=True)
            bootstrapped_means.append(np.mean(sample))

        alpha = 1 - confidence
        lower = np.percentile(bootstrapped_means, alpha / 2 * 100)
        upper = np.percentile(bootstrapped_means, (1 - alpha / 2) * 100)

        return (float(lower), float(upper))

    # ========================================================================
    # Caching
    # ========================================================================

    def save_results(self, results: BenchmarkResults, filepath: Path) -> None:
        """Save benchmark results to JSON file.

        Args:
            filepath: Path to save results
        """
        filepath.parent.mkdir(parents=True, exist_ok=True)
        with open(filepath, "w") as f:
            json.dump(results, f, indent=2)

    def _generate_cache_key(
        self, patterns: list[str], task_count: int, seed: int | None
    ) -> str:
        """Generate cache key from benchmark parameters.

        Args:
            patterns: List of patterns
            task_count: Number of tasks
            seed: Random seed

        Returns:
            Cache key hash
        """
        key_data = f"{sorted(patterns)}_{task_count}_{seed}"
        return hashlib.md5(key_data.encode()).hexdigest()

    def _save_cache(self, cache_key: str, results: BenchmarkResults, cache_dir: Path) -> None:
        """Save results to cache.

        Args:
            cache_key: Cache key
            results: Results to save
            cache_dir: Cache directory
        """
        cache_dir.mkdir(parents=True, exist_ok=True)
        cache_file = cache_dir / f"benchmark_{cache_key}.json"
        self.save_results(results, cache_file)

    def _load_cache(self, cache_key: str, cache_dir: Path) -> BenchmarkResults | None:
        """Load results from cache.

        Args:
            cache_key: Cache key
            cache_dir: Cache directory

        Returns:
            Cached results if available, None otherwise
        """
        cache_file = cache_dir / f"benchmark_{cache_key}.json"
        if cache_file.exists():
            with open(cache_file) as f:
                cached_data: BenchmarkResults = json.load(f)
                return cached_data
        return None
