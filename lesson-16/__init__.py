"""Lesson 16 - Agent Reliability: Enterprise Patterns for Multi-Agent Systems.

This lesson teaches enterprise-grade reliability patterns for multi-agent systems through:
- 7 concept tutorials covering reliability fundamentals to production deployment
- 8 interactive Jupyter notebooks with hands-on implementations
- Complete reliability framework with 7 components
- 5 orchestration patterns (sequential, hierarchical, iterative, state machine, voting)
- 3 synthetic financial datasets (invoices, fraud, reconciliation)
- 6 visual diagrams for learning
- Research-grade benchmark suite validated against AgentArch paper

Learning Outcomes:
- Build production-ready agent systems with ≥95% success rates
- Master 4 evaluation metrics (task success, error propagation, latency, cost)
- Implement 7 reliability components (retry, circuit breaker, checkpoint, etc.)
- Choose optimal orchestration patterns for business requirements
- Deploy agents with cost optimization and observability

Quick Start:
1. Read lesson-16/README.md for prerequisites and learning paths
2. Navigate lesson-16/TUTORIAL_INDEX.md for tutorial roadmap
3. Start with Tutorial 01 (Reliability Fundamentals) and Notebook 08 (Sequential baseline)
4. Progress through 3 learning paths: Foundation → Advanced → Production

See lesson-16/DELIVERABLES.md for complete manifest of all outputs.
"""

__version__ = "1.0.0"
__author__ = "AI Engineering Course Team"

# Public API exports for external use
from lesson_16.backend.reliability import (
    AuditLogger,
    CircuitBreaker,
    FallbackHandler,
    Result,
    retry_with_backoff,
    safe_agent_call,
    save_checkpoint,
    load_checkpoint,
)

from lesson_16.backend.orchestrators import (
    Orchestrator,
    SequentialOrchestrator,
    HierarchicalOrchestrator,
    IterativeOrchestrator,
    StateMachineOrchestrator,
    VotingOrchestrator,
)

from lesson_16.backend.benchmarks import (
    FinancialTaskGenerator,
    MetricsCalculator,
    BenchmarkRunner,
)

__all__ = [
    # Reliability components
    "AuditLogger",
    "CircuitBreaker",
    "FallbackHandler",
    "Result",
    "retry_with_backoff",
    "safe_agent_call",
    "save_checkpoint",
    "load_checkpoint",
    # Orchestrators
    "Orchestrator",
    "SequentialOrchestrator",
    "HierarchicalOrchestrator",
    "IterativeOrchestrator",
    "StateMachineOrchestrator",
    "VotingOrchestrator",
    # Benchmarks
    "FinancialTaskGenerator",
    "MetricsCalculator",
    "BenchmarkRunner",
]
