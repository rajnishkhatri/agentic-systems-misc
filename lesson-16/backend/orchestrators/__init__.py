"""
Orchestration Patterns for Multi-Agent Systems

This module provides 5 orchestration patterns with an abstract base class:
- BaseOrchestrator - Abstract base class with shared functionality
- SequentialOrchestrator - Chain-of-thought processing (simple, cheap, baseline)
- HierarchicalOrchestrator - Planner-specialist delegation (complex task decomposition)
- IterativeOrchestrator - ReAct/Reflexion with self-correction (refinable errors)
- StateMachineOrchestrator - Deterministic FSM (compliance, auditability)
- VotingOrchestrator - Ensemble consensus (high-stakes decisions)

Pattern Selection Decision Tree:
    1. Is determinism mandatory (compliance)? → StateMachineOrchestrator
    2. High-stakes decision (fraud, medical)? → VotingOrchestrator
    3. Requires specialized expertise per subtask? → HierarchicalOrchestrator
    4. Errors correctable through iteration? → IterativeOrchestrator
    5. Default: SequentialOrchestrator (simplest, cheapest)

Usage:
    from lesson16.backend.orchestrators import SequentialOrchestrator

    orchestrator = SequentialOrchestrator(agents=[agent1, agent2, agent3])
    result = await orchestrator.execute(task)
"""

# Task 3.2: Base Orchestrator ABC implemented
from .base import Orchestrator

# Task 3.3-3.7: Pattern implementations (to be completed)
# from .sequential import SequentialOrchestrator
# from .hierarchical import HierarchicalOrchestrator
# from .iterative import IterativeOrchestrator
# from .state_machine import StateMachineOrchestrator
# from .voting import VotingOrchestrator

__all__ = [
    "Orchestrator",
    # "SequentialOrchestrator",
    # "HierarchicalOrchestrator",
    # "IterativeOrchestrator",
    # "StateMachineOrchestrator",
    # "VotingOrchestrator",
]
