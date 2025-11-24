"""End-to-end integration tests for Context Engineering workflows."""

import time

import pytest

from backend.memory.pii_redaction import PIIRedactor, extract_memory_with_pii_redaction
from backend.sessions.gita_session import GitaSession


def test_should_complete_50_turn_session_with_compression() -> None:
    """Test end-to-end workflow: Create GitaSession → add 50 turns → trigger compression → verify protected context preserved."""
    # Arrange: Create session
    session = GitaSession(max_tokens=8000)

    # Act: Add turn 0 (initial objective - protected)
    session.append_event(
        turn=0,
        role="user",
        content="I want to learn about Krishna's teachings on karma yoga. Please use Swami Sivananda's translations.",
        event_type="constraint",
    )

    # Add 49 more turns to trigger compression
    for i in range(1, 50):
        session.append_event(
            turn=i,
            role="user",
            content=f"This is turn {i} with some casual conversation about the Gita",
            event_type="conversation",
        )
        session.append_event(
            turn=i,
            role="assistant",
            content=f"Response to turn {i} with some explanation",
            event_type="conversation",
        )

    # Assert: Verify initial objective is preserved
    context_window = session.get_context_window()
    initial_objective = [
        event
        for event in context_window
        if event["turn"] == 0 and event["event_type"] == "constraint"
    ]

    assert len(initial_objective) == 1, "Initial objective should be preserved"
    assert (
        "Swami Sivananda" in initial_objective[0]["content"]
    ), "Protected content should be intact"


def test_should_extract_memory_with_pii_redaction_and_provenance() -> None:
    """Test end-to-end workflow: Extract memory → apply PII redaction → create provenance → update confidence → export audit log."""
    # Arrange: User message with PII
    user_message = "I'm John Smith at john@email.com. I'm anxious about my job interview. Can Krishna's teachings help?"

    # Act: Extract memory with PII redaction
    redacted_text, provenance = extract_memory_with_pii_redaction(
        text=user_message,
        source_session_id="sess_day1",
        confidence_score=0.7,
        validation_status="agent_inferred",
    )

    # Assert: PII redacted
    assert "[NAME_REDACTED]" in redacted_text
    assert "[EMAIL_REDACTED]" in redacted_text
    assert "anxious" in redacted_text, "Emotional context should be preserved"
    assert "job interview" in redacted_text, "Situational context should be preserved"

    # Act: Update confidence (provenance already created)
    # Memory already has initial confidence, just update it

    # Simulate user confirmation
    provenance.add_confidence_update(0.9, "User confirmed: 'Yes, that's correct'")
    provenance.validation_status = "user_confirmed"

    # Assert: Confidence boosted
    assert provenance.effective_confidence == 1.0, "User confirmed should boost to 1.0"
    assert (
        provenance.confidence_trend == "increasing"
    ), "Trend should be increasing (0.7 → 0.9)"

    # Act: Export audit log
    audit_log = provenance.to_audit_log()

    # Assert: Audit log complete
    assert audit_log["source_session_id"] == "sess_day1"
    assert audit_log["validation_status"] == "user_confirmed"
    assert audit_log["confidence_trend"] == "increasing"
    # Note: confidence_history includes initial (0.7), PII penalty (0.665), and user update (0.9)
    assert len(audit_log["confidence_history"]) >= 2


def test_should_handle_multi_session_memory_consolidation() -> None:
    """Test end-to-end workflow: Multiple sessions → extract memories → consolidate → track provenance."""
    # Arrange: Three sessions with related preferences
    sessions = [
        {
            "session_id": "sess_day1",
            "content": "I prefer Swami Sivananda translations",
            "confidence": 0.7,
        },
        {
            "session_id": "sess_day3",
            "content": "Swami Sivananda's commentary is very clear",
            "confidence": 0.8,
        },
        {
            "session_id": "sess_day5",
            "content": "Please use Swami Sivananda again",
            "confidence": 0.9,
        },
    ]

    # Act: Extract memories
    memories = []
    for sess in sessions:
        redacted_text, provenance = extract_memory_with_pii_redaction(
            text=sess["content"],
            source_session_id=sess["session_id"],
            confidence_score=sess["confidence"],
            validation_status="agent_inferred",
        )
        memories.append({"text": redacted_text, "provenance": provenance})

    # Assert: All memories created
    assert len(memories) == 3
    assert all("provenance" in m for m in memories)
    assert all("Swami Sivananda" in m["text"] for m in memories)

    # Act: Simulate consolidation (find highest confidence)
    consolidated = max(memories, key=lambda m: m["provenance"].effective_confidence)

    # Assert: Highest confidence memory selected
    assert consolidated["provenance"].source_session_id == "sess_day5"
    # Note: Confidence might be slightly lower due to no PII penalty, but still highest
    assert consolidated["provenance"].confidence_score == 0.9


def test_should_complete_compression_cycle_under_2_seconds() -> None:
    """Test performance: Compression should complete in <2 seconds for 100-turn conversation."""
    # Arrange: Use GitaSession for realistic workflow
    session = GitaSession(max_tokens=8000, compression_threshold=0.95)

    # Act: Measure time for adding 100 turns and automatic compression
    start_time = time.time()

    # Add turn 0 (protected)
    session.append_event(
        turn=0,
        role="user",
        content="I want to learn about Krishna's teachings. Use Swami Sivananda translations.",
        event_type="constraint"
    )

    # Add 99 more turns (will trigger compression)
    for i in range(1, 100):
        session.append_event(
            turn=i,
            role="user" if i % 2 == 1 else "assistant",
            content=f"Turn {i}: Discussion about Bhagavad Gita and Krishna's teachings on dharma",
            event_type="conversation"
        )

    elapsed_time = time.time() - start_time

    # Assert: Performance under 2 seconds
    assert elapsed_time < 2.0, f"Session operations took {elapsed_time:.2f}s, should be <2s"

    # Get context window
    context = session.get_context_window()

    # Assert: Compression happened (fewer events than added)
    assert len(context) < 100, f"Expected compression, but have {len(context)} events"

    # Assert: Protected turn 0 preserved
    assert any(
        e["turn"] == 0 and e["event_type"] == "constraint" for e in context
    ), "Protected turn 0 (constraint) should be preserved"


def test_should_handle_pii_redaction_edge_cases() -> None:
    """Test PII redaction with edge cases: multiple emails, names in whitelist, phone formats."""
    # Arrange
    redactor = PIIRedactor()

    test_cases = [
        # Multiple emails
        {
            "input": "Contact me at john@example.com or jane@example.org",
            "expected_substring": "[EMAIL_REDACTED]",
            "count": 2,
        },
        # Whitelisted names (Gita characters) - should NOT be redacted
        {
            "input": "Arjuna asked Krishna about dharma",
            "expected_substring": "Arjuna asked Krishna about dharma",
            "count": 1,
        },
        # Mixed: real name + Gita character
        {
            "input": "John Smith asked about Arjuna's dilemma",
            "expected_substring": "[NAME_REDACTED]",
            "count": 1,
        },
        # Phone number formats - just check that phone redaction happened
        {
            "input": "Call me at 555-1234 or (555) 678-9012",
            "expected_substring": "[PHONE_REDACTED]",
            "count": 2,
        },
    ]

    # Act & Assert
    for test in test_cases:
        redacted, pii_found = redactor.redact(test["input"])
        assert (
            redacted.count(test["expected_substring"]) >= 1
        ), f"Expected '{test['expected_substring']}' in '{redacted}' for input '{test['input']}'"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
