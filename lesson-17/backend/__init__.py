"""Lesson 17: Agent Explainability Framework Backend.

This module provides production-grade explainability components for AI agents:

1. BlackBoxRecorder - Aviation-style persistent recording of agent activities
2. AgentFacts - Verifiable metadata standard for agent identity and capabilities
3. GuardRails - Declarative validators with trace generation
4. PhaseLogger - Multi-phase workflow logging with decision tracking

Usage:
    from lesson17.backend.explainability import (
        BlackBoxRecorder,
        AgentFacts,
        AgentFactsRegistry,
        GuardRail,
        GuardRailValidator,
        PhaseLogger,
    )
"""

