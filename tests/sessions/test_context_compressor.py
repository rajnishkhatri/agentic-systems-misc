"""Tests for context compressor (TDD RED Phase).

Test compression triggering, protected context preservation, and edge cases.
"""

import pytest


def test_should_trigger_compression_at_95_percent_capacity() -> None:
    """Test that compression triggers at 7600/8000 tokens (95% capacity)."""
    from backend.sessions.context_compressor import ContextCompressor

    compressor = ContextCompressor(max_tokens=8000, trigger_threshold=0.95)
    events = [{"content": "x" * 100, "is_protected": False} for _ in range(76)]

    # Assuming ~100 tokens per event = 7600 tokens total
    assert compressor.should_compress(events) is True


def test_should_not_trigger_compression_below_95_percent() -> None:
    """Test that compression does not trigger at 7400/8000 tokens (92.5% capacity)."""
    from backend.sessions.context_compressor import ContextCompressor

    compressor = ContextCompressor(max_tokens=8000, trigger_threshold=0.95)
    events = [{"content": "x" * 100, "is_protected": False} for _ in range(74)]

    # Assuming ~100 tokens per event = 7400 tokens total (below threshold)
    assert compressor.should_compress(events) is False


def test_should_preserve_protected_events_during_compression() -> None:
    """Test that protected events remain intact after compression."""
    from backend.sessions.context_compressor import ContextCompressor

    compressor = ContextCompressor(max_tokens=8000, trigger_threshold=0.95)
    events = [
        {
            "turn": 0,
            "role": "user",
            "event_type": "initial_objective",
            "content": "Initial objective: Help me understand karma yoga",
            "is_protected": True,
        },
        {
            "turn": 1,
            "role": "assistant",
            "event_type": "casual",
            "content": "Sure, I can help with that",
            "is_protected": False,
        },
        {
            "turn": 2,
            "role": "user",
            "event_type": "question",
            "content": "What is karma?",
            "is_protected": False,
        },
        {
            "turn": 3,
            "role": "user",
            "event_type": "constraint",
            "content": "Important constraint: Only use Swami Sivananda translations",
            "is_protected": True,
        },
        {
            "turn": 4,
            "role": "assistant",
            "event_type": "acknowledgment",
            "content": "Understood",
            "is_protected": False,
        },
    ]

    compressed_events = compressor.compress(events)

    # Protected events at indices 0 and 3 should remain intact
    assert any(e["turn"] == 0 and "Initial objective" in e["content"] for e in compressed_events)
    assert any(e["turn"] == 3 and "Important constraint" in e["content"] for e in compressed_events)


def test_should_compress_non_protected_events() -> None:
    """Test that non-protected events are summarized during compression."""
    from backend.sessions.context_compressor import ContextCompressor

    compressor = ContextCompressor(max_tokens=8000, trigger_threshold=0.95)
    events = [
        {"turn": 0, "role": "user", "event_type": "initial_objective", "content": "Initial objective", "is_protected": True},
        {"turn": 1, "role": "user", "event_type": "casual", "content": "Casual conversation turn 1", "is_protected": False},
        {"turn": 2, "role": "assistant", "event_type": "casual", "content": "Casual conversation turn 2", "is_protected": False},
        {"turn": 3, "role": "user", "event_type": "clarification", "content": "Casual conversation turn 3", "is_protected": False},
    ]

    compressed_events = compressor.compress(events)

    # Total events should be less than original (compression happened)
    assert len(compressed_events) < len(events)
    # Protected event should still be present
    assert any(e["is_protected"] is True for e in compressed_events)
    summary_events = [e for e in compressed_events if e.get("event_type") == "compression_summary"]
    assert summary_events, "Expected a compression summary event to be emitted"
    summary = summary_events[0]
    assert summary["role"] == "system"
    assert summary["turn"] == 1
    assert summary["turn_range"] == [1, 3]
    assert "Turns" in summary["content"]
    assert summary.get("metadata", {}).get("event_count") == 3


def test_should_raise_error_for_invalid_trigger_threshold() -> None:
    """Test that ValueError is raised for invalid threshold values."""
    from backend.sessions.context_compressor import ContextCompressor

    # Threshold > 1.0 should raise ValueError
    with pytest.raises(ValueError, match="threshold must be between 0.0 and 1.0"):
        ContextCompressor(max_tokens=8000, trigger_threshold=1.5)

    # Threshold < 0.0 should raise ValueError
    with pytest.raises(ValueError, match="threshold must be between 0.0 and 1.0"):
        ContextCompressor(max_tokens=8000, trigger_threshold=-0.1)


def test_should_raise_error_for_non_list_events_in_should_compress() -> None:
    """Test that TypeError is raised when events is not a list in should_compress."""
    from backend.sessions.context_compressor import ContextCompressor

    compressor = ContextCompressor(max_tokens=8000, trigger_threshold=0.95)

    with pytest.raises(TypeError, match="events must be a list"):
        compressor.should_compress("not a list")


def test_should_raise_error_for_non_list_events_in_compress() -> None:
    """Test that TypeError is raised when events is not a list in compress."""
    from backend.sessions.context_compressor import ContextCompressor

    compressor = ContextCompressor(max_tokens=8000, trigger_threshold=0.95)

    with pytest.raises(TypeError, match="events must be a list"):
        compressor.compress({"not": "a list"})


def test_summary_event_contains_metadata_and_event_mix() -> None:
    """Summary events should include metadata for turn range and event mix."""
    from backend.sessions.context_compressor import ContextCompressor

    compressor = ContextCompressor(max_tokens=8000, trigger_threshold=0.95)
    events = [
        {"turn": 5, "role": "user", "content": "What about Chapter 3?", "event_type": "clarification", "is_protected": False},
        {"turn": 6, "role": "assistant", "content": "Explained karma yoga focus.", "event_type": "casual", "is_protected": False},
        {"turn": 7, "role": "user", "content": "Please stick to Sivananda commentary.", "event_type": "preference", "is_protected": False},
    ]

    summary_events = compressor.compress(events)
    assert len(summary_events) == 1
    summary = summary_events[0]

    assert summary["event_type"] == "compression_summary"
    assert summary["turn"] == 5
    assert summary["turn_range"] == [5, 7]
    assert summary["metadata"]["turn_range"] == [5, 7]
    assert summary["metadata"]["event_count"] == 3
    assert "Participants" in summary["content"]
    assert "Event mix" in summary["content"]
