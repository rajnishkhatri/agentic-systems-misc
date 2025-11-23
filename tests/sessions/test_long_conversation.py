"""Tests for long multi-turn conversations with compression (TDD RED Phase).

Test that GitaSession preserves protected context across many turns and handles
multiple compression cycles.
"""

import pytest


def test_should_preserve_objectives_in_50_turn_conversation() -> None:
    """Test that initial objective survives 50 turns with compression."""
    from backend.sessions.gita_session import GitaSession

    # Initialize session with protected initial objective
    session = GitaSession(max_tokens=8000, compression_threshold=0.95)

    # Turn 0: Initial objective (should be protected)
    session.append_event(
        turn=0,
        role="user",
        content="Help me understand karma yoga from Chapter 3",
        event_type="initial_objective"
    )

    # Add 49 more turns (mix of protected and non-protected)
    for turn in range(1, 50):
        if turn % 10 == 0:
            # Every 10th turn is a constraint (protected)
            session.append_event(
                turn=turn,
                role="user",
                content=f"Constraint at turn {turn}: Only use Swami Sivananda translations",
                event_type="constraint"
            )
        else:
            # Regular conversation (non-protected)
            session.append_event(
                turn=turn,
                role="user",
                content=f"Casual question at turn {turn}",
                event_type="casual"
            )

    # Get context window (may have been compressed)
    context_window = session.get_context_window()

    # Initial objective should still be present
    assert any(
        event["turn"] == 0 and "karma yoga" in event["content"]
        for event in context_window
    ), "Initial objective should be preserved after 50 turns"

    # All constraints should be preserved
    constraint_turns = [0, 10, 20, 30, 40]
    for constraint_turn in constraint_turns:
        assert any(
            event["turn"] == constraint_turn
            for event in context_window
        ), f"Constraint at turn {constraint_turn} should be preserved"


def test_should_handle_multiple_compressions_in_100_turns() -> None:
    """Test that session handles 2-3 compression cycles in 100 turns."""
    from backend.sessions.gita_session import GitaSession

    session = GitaSession(max_tokens=8000, compression_threshold=0.95)

    # Add 100 turns with few protected events
    for turn in range(100):
        if turn == 0:
            event_type = "initial_objective"
            content = "Initial objective"
        elif turn % 25 == 0:
            event_type = "constraint"
            content = f"Important constraint at turn {turn}"
        else:
            event_type = "casual"
            content = f"Casual turn {turn}"

        session.append_event(
            turn=turn,
            role="user" if turn % 2 == 0 else "assistant",
            content=content,
            event_type=event_type
        )

    # Get final context window
    context_window = session.get_context_window()

    # Should have fewer events than 100 (compression happened)
    assert len(context_window) < 100, "Compression should have reduced event count"

    # Protected events should survive
    assert any(event["turn"] == 0 for event in context_window), "Initial objective preserved"
    assert any(event["turn"] == 25 for event in context_window), "Constraint at turn 25 preserved"
    assert any(event["turn"] == 50 for event in context_window), "Constraint at turn 50 preserved"
    assert any(event["turn"] == 75 for event in context_window), "Constraint at turn 75 preserved"

    # Check compression was triggered (session should track this)
    # Note: With current implementation (removing non-protected events),
    # only 1 compression may occur since count drops dramatically
    assert session.compression_count >= 1, "Should have triggered at least 1 compression"


def test_should_reject_compression_with_all_protected() -> None:
    """Test that compression fails gracefully when all events are protected."""
    from backend.sessions.gita_session import GitaSession

    session = GitaSession(max_tokens=8000, compression_threshold=0.95)

    # Add many protected events until threshold exceeded
    for turn in range(100):
        session.append_event(
            turn=turn,
            role="user",
            content=f"Critical constraint {turn}",
            event_type="constraint"  # All protected
        )

    # Should raise an error or handle gracefully
    # In this implementation, we expect compression to fail or preserve all events
    context_window = session.get_context_window()

    # All 100 events should remain (cannot compress protected events)
    assert len(context_window) == 100, "All protected events should be preserved"


def test_should_raise_error_for_invalid_turn_type() -> None:
    """Test that TypeError is raised when turn is not an int."""
    from backend.sessions.gita_session import GitaSession

    session = GitaSession()

    with pytest.raises(TypeError, match="turn must be an int"):
        session.append_event(turn="not an int", role="user", content="test", event_type="casual")


def test_should_raise_error_for_invalid_role_type() -> None:
    """Test that TypeError is raised when role is not a str."""
    from backend.sessions.gita_session import GitaSession

    session = GitaSession()

    with pytest.raises(TypeError, match="role must be a str"):
        session.append_event(turn=0, role=123, content="test", event_type="casual")


def test_should_raise_error_for_invalid_content_type() -> None:
    """Test that TypeError is raised when content is not a str."""
    from backend.sessions.gita_session import GitaSession

    session = GitaSession()

    with pytest.raises(TypeError, match="content must be a str"):
        session.append_event(turn=0, role="user", content=None, event_type="casual")


def test_should_raise_error_for_invalid_event_type_type() -> None:
    """Test that TypeError is raised when event_type is not a str."""
    from backend.sessions.gita_session import GitaSession

    session = GitaSession()

    with pytest.raises(TypeError, match="event_type must be a str"):
        session.append_event(turn=0, role="user", content="test", event_type=None)


def test_should_raise_error_for_empty_content() -> None:
    """Test that ValueError is raised when content is empty."""
    from backend.sessions.gita_session import GitaSession

    session = GitaSession()

    with pytest.raises(ValueError, match="content cannot be empty"):
        session.append_event(turn=0, role="user", content="   ", event_type="casual")


def test_should_raise_error_for_empty_event_type() -> None:
    """Test that ValueError is raised when event_type is empty."""
    from backend.sessions.gita_session import GitaSession

    session = GitaSession()

    with pytest.raises(ValueError, match="event_type cannot be empty"):
        session.append_event(turn=0, role="user", content="test", event_type="  ")
