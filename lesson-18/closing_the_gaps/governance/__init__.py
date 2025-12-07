"""Governance Layer for Closing the Gaps.

This module provides governance components (Gaps 6, 9, 10):
    - HITLController: Human-in-the-loop oversight per regulations
    - PromptSecurityGuard: Prompt injection defense
    - AntiPatternDetector: Common failure mode detection (future)

Regulatory References:
    - Federal Reserve SR 11-7: AI model risk management
    - EU AI Act Article 14: Human oversight requirements
    - OWASP LLM Top 10 2025: Security threat mitigation
"""

from .hitl_controller import HITLController, InterruptDecision, OversightTier
from .prompt_security import PromptSecurityGuard, ScanResult

__all__ = [
    # Security (Gap 9)
    "PromptSecurityGuard",
    "ScanResult",
    # Human-in-the-Loop (Gap 6)
    "HITLController",
    "OversightTier",
    "InterruptDecision",
]
