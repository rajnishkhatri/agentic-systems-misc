"""Closing the Gaps: Evaluation & Explainability Framework for Multi-Agent Systems.

This module addresses 10 critical gaps in multi-agent bank dispute systems,
leveraging Pólya's 5-phase methodology and existing explainability components.

Architecture:
    Layer 1 - Evaluation Framework (Gaps 1, 4, 7)
        - BaseEvaluator ABC
        - StatisticalEvaluator (non-deterministic testing)
        - ArchitectureJustifier (single vs multi-agent decision)
        - TradeoffAnalyzer (fundamental limits)

    Layer 2 - Explainability (Gaps 6, 8, 9)
        - PolyaPhaseMapper (Pólya → PhaseLogger)
        - ObservabilityHub (LLM-specific metrics)
        - PromptSecurityGuard (injection defense)

    Layer 3 - Governance (Gaps 2, 3, 5, 10)
        - HITLController (human-in-the-loop)
        - FailureTaxonomyAnalyzer (MAST taxonomy)
        - CostTracker (token economics)
        - AntiPatternDetector (failure mode detection)

Key Design Decisions:
    1. 3-agent architecture (not 7) per research recommendation
    2. Statistical testing for LLM variance (5x runs, semantic similarity)
    3. Verify against non-LLM ground truth only
    4. Map Pólya phases to PhaseLogger workflow states

References:
    - closing_the_gaps_first_principles.md - Research synthesis
    - ai-dev-tasks/polya-analysis.md - Pólya methodology
    - lesson-17/backend/explainability/ - Core components

Example:
    >>> from closing_the_gaps import StatisticalEvaluator, HITLController
    >>> evaluator = StatisticalEvaluator({"name": "dispute_eval", "min_samples": 5})
    >>> hitl = HITLController(default_tier=OversightTier.TIER_2_MEDIUM)
"""

__version__ = "1.0.0"

__all__ = [
    # Evaluation
    "BaseEvaluator",
    "EvaluationResult",
    "StatisticalEvaluator",
    "ArchitectureJustifier",
    "TradeoffAnalyzer",
    # Governance
    "HITLController",
    "OversightTier",
    "PromptSecurityGuard",
    "AntiPatternDetector",
    # Explainability
    "PolyaPhaseMapper",
    "ObservabilityHub",
    "CostTracker",
]


def __getattr__(name: str):
    """Lazy import mechanism to avoid circular dependencies."""
    if name in ("BaseEvaluator", "EvaluationResult"):
        from .evaluation.base_evaluator import BaseEvaluator, EvaluationResult
        return {"BaseEvaluator": BaseEvaluator, "EvaluationResult": EvaluationResult}[name]

    if name == "StatisticalEvaluator":
        from .evaluation.statistical_evaluator import StatisticalEvaluator
        return StatisticalEvaluator

    if name == "ArchitectureJustifier":
        from .evaluation.architecture_justifier import ArchitectureJustifier
        return ArchitectureJustifier

    if name in ("HITLController", "OversightTier"):
        from .governance.hitl_controller import HITLController, OversightTier
        return {"HITLController": HITLController, "OversightTier": OversightTier}[name]

    if name == "PromptSecurityGuard":
        from .governance.prompt_security import PromptSecurityGuard
        return PromptSecurityGuard

    if name == "PolyaPhaseMapper":
        from .explainability.polya_mapper import PolyaPhaseMapper
        return PolyaPhaseMapper

    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
