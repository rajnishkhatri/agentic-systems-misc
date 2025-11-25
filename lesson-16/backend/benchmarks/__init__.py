"""
AgentArch Benchmark Suite for Orchestration Pattern Evaluation

This module provides tools for evaluating orchestration patterns using the AgentArch
benchmark methodology from research literature.

Components:
- financial_tasks: Generate 300 synthetic financial tasks (invoices, fraud, reconciliation)
- metrics: 4 evaluation metrics (success rate, cost efficiency, latency, error recovery)
- runner: Benchmark execution engine for comparing 5 orchestration patterns

Dataset Structure:
    - 100 invoice processing tasks (validation → extraction → quality check)
    - 100 fraud detection tasks (transaction analysis → merchant analysis → geo analysis)
    - 100 account reconciliation tasks (data matching with iterative refinement)

Metrics:
    1. Task Success Rate: % of tasks completed correctly
    2. Cost Efficiency: Average cost per task ($/task)
    3. Latency: P50/P95 latency in seconds
    4. Error Recovery Rate: % of failures successfully recovered via retry/fallback

Usage:
    import sys
    sys.path.insert(0, 'lesson-16')
    from backend.benchmarks import BenchmarkRunner, FinancialTaskGenerator, MetricsCalculator

    # Generate financial task suite
    generator = FinancialTaskGenerator()
    generator.load_datasets()
    tasks = generator.generate_task_suite(count=30, strategy="random", seed=42)

    # Run benchmark
    from backend.orchestrators import SequentialOrchestrator, HierarchicalOrchestrator
    runner = BenchmarkRunner(
        orchestrators={"sequential": SequentialOrchestrator(), "hierarchical": HierarchicalOrchestrator()},
        default_timeout=60
    )
    results = runner.run_benchmark(tasks=tasks, patterns=["sequential", "hierarchical"])

    # Calculate metrics
    calculator = MetricsCalculator()
    task_success_rate = calculator.calculate_task_success_rate(predictions, gold_labels)
"""

# Benchmark suite implemented in Task 6.0
from .financial_tasks import FinancialTaskGenerator
from .metrics import (
    OPENAI_PRICING,
    APICall,
    CostSummary,
    LatencyDistribution,
    MetricsCalculator,
    WorkflowStep,
    WorkflowTrace,
)
from .runner import (
    BenchmarkResults,
    BenchmarkRunner,
    FailingOrchestrator,
    MockAgent,
    PatternMetrics,
    PatternResult,
    StatisticalAnalysis,
)

__all__ = [
    "FinancialTaskGenerator",
    "MetricsCalculator",
    "OPENAI_PRICING",
    "APICall",
    "CostSummary",
    "LatencyDistribution",
    "WorkflowStep",
    "WorkflowTrace",
    "BenchmarkRunner",
    "BenchmarkResults",
    "PatternResult",
    "PatternMetrics",
    "StatisticalAnalysis",
    "MockAgent",
    "FailingOrchestrator",
]
