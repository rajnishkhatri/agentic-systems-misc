"""Evaluation Framework for Closing the Gaps.

This module provides the evaluation layer (Gaps 1, 4, 7):
    - BaseEvaluator: Abstract base class for all evaluators
    - StatisticalEvaluator: Non-deterministic LLM output testing
    - ArchitectureJustifier: Single vs multi-agent decision
    - TradeoffAnalyzer: Fundamental limits documentation
"""

from .base_evaluator import BaseEvaluator, EvaluationResult

__all__ = [
    "BaseEvaluator",
    "EvaluationResult",
]
