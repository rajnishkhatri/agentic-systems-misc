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
    from lesson16.backend.benchmarks import BenchmarkRunner, generate_financial_tasks

    tasks = generate_financial_tasks(task_type="invoice", count=100)
    runner = BenchmarkRunner(patterns=[seq, hier, iter, fsm, vote])
    results = await runner.run(tasks)
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
