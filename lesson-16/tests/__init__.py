"""
Test suite for Lesson 16: Agent Reliability & Orchestration Patterns

Test modules:
- test_reliability_components: Tests for 7 reliability components (retry, circuit breaker, etc.)
- test_orchestrators: Tests for 5 orchestration patterns
- test_benchmarks: Tests for benchmark suite (task generation, metrics, runner)
- test_financial_tasks: Tests for financial task generators

Test naming convention:
    test_should_[expected_result]_when_[condition]()

Example:
    def test_should_retry_3_times_when_transient_error() -> None:
        # Test retry logic with exponential backoff
        ...

Coverage target: ≥90% for all backend code
"""
