"""State machine orchestrators for dispute workflow.

This module contains:
- dispute_state.py: DisputeState enum (CLASSIFY, GATHER, VALIDATE, SUBMIT, MONITOR)
- transitions.py: State transition rules and guards
- dispute_orchestrator.py: StateMachineOrchestrator subclass (from lesson-16)
- evidence_gatherer.py: Hierarchical gatherer using ThreadPoolExecutor
"""
