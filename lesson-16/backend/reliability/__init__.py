"""
Reliability Components for Production Agent Systems

This module provides 7 reliability components for building production-grade agent systems:
1. RetryHandler - Exponential backoff retry logic with jitter
2. CircuitBreaker - Prevent cascade failures (CLOSED → OPEN → HALF_OPEN)
3. CheckpointManager - Deterministic checkpointing for stateful workflows
4. SchemaValidator - Pydantic-based output validation
5. ErrorIsolator - Contain failures, prevent error propagation
6. AuditLogger - Compliance-ready audit trails
7. FallbackStrategy - Graceful degradation (cache, simpler models, human-in-the-loop)

Usage:
    from lesson16.backend.reliability import RetryHandler, CircuitBreaker, CheckpointManager

    retry_handler = RetryHandler(max_retries=3, backoff_factor=2.0)
    circuit_breaker = CircuitBreaker(failure_threshold=5, timeout=60)
    checkpoint_mgr = CheckpointManager(storage_path="checkpoints/")
"""

# Task 2.0 Components - Progressive exports as modules are implemented
from .audit_log import AuditLogger
from .checkpoint import load_checkpoint, save_checkpoint
from .circuit_breaker import CircuitBreaker, CircuitBreakerOpenError
from .fallback import FallbackHandler, FallbackStrategy
from .isolation import Result, safe_agent_call
from .retry import retry_with_backoff
from .validation import FraudDetection, InvoiceExtraction

__all__ = [
    # Task 2.2 - Retry Logic (FR4.1)
    "retry_with_backoff",
    # Task 2.3 - Circuit Breaker (FR4.2)
    "CircuitBreaker",
    "CircuitBreakerOpenError",
    # Task 2.4 - Deterministic Checkpointing (FR4.3)
    "save_checkpoint",
    "load_checkpoint",
    # Task 2.5 - Output Validation Schemas (FR4.4)
    "InvoiceExtraction",
    "FraudDetection",
    # Task 2.6 - Error Isolation (FR4.5)
    "Result",
    "safe_agent_call",
    # Task 2.7 - Audit Logging (FR4.6)
    "AuditLogger",
    # Task 2.8 - Fallback Strategies (FR4.7)
    "FallbackStrategy",
    "FallbackHandler",
]
