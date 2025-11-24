"""Tests for protected context identification logic.

TDD RED Phase: These tests should fail until backend/sessions/protected_context.py is implemented.
"""

import pytest

from backend.sessions.protected_context import identify_protected_context


def test_should_identify_initial_objectives_as_protected() -> None:
    """Test that Turn 0 events are marked as protected."""
    event = {
        "turn": 0,
        "role": "user",
        "content": "I want to learn about karma yoga from the Bhagavad Gita",
        "event_type": "initial_objective",
    }
    result = identify_protected_context(event)
    assert result["is_protected"] is True
    assert "initial objective" in result["reason"].lower()


def test_should_identify_explicit_constraints_as_protected() -> None:
    """Test that constraint events are marked as protected."""
    event = {
        "turn": 5,
        "role": "user",
        "content": "Please only use Swami Sivananda's commentary",
        "event_type": "constraint",
    }
    result = identify_protected_context(event)
    assert result["is_protected"] is True
    assert "constraint" in result["reason"].lower()


def test_should_not_protect_casual_conversation() -> None:
    """Test that acknowledgments are not protected."""
    event = {
        "turn": 10,
        "role": "user",
        "content": "Thanks, that's helpful",
        "event_type": "acknowledgment",
    }
    result = identify_protected_context(event)
    assert result["is_protected"] is False
    assert "not critical" in result["reason"].lower() or "casual" in result["reason"].lower()


def test_should_protect_auth_checkpoints() -> None:
    """Test that authentication events are protected."""
    event = {
        "turn": 2,
        "role": "system",
        "content": "User authentication confirmed",
        "event_type": "auth_checkpoint",
    }
    result = identify_protected_context(event)
    assert result["is_protected"] is True
    assert "auth" in result["reason"].lower() or "security" in result["reason"].lower()


def test_should_raise_error_for_non_dict_event() -> None:
    """Test that TypeError is raised when event is not a dict."""
    with pytest.raises(TypeError, match="event must be a dict"):
        identify_protected_context("not a dict")


def test_should_raise_error_for_missing_required_fields() -> None:
    """Test that ValueError is raised when event is missing required fields."""
    # Missing 'event_type' field
    event = {"turn": 0, "role": "user", "content": "test"}

    with pytest.raises(ValueError, match="event missing required fields"):
        identify_protected_context(event)


def test_should_not_protect_unknown_event_types() -> None:
    """Test that unknown event types are not protected."""
    event = {"turn": 5, "role": "user", "content": "Some content", "event_type": "unknown_type"}

    result = identify_protected_context(event)

    assert result["is_protected"] is False
    assert "not identified as critical" in result["reason"]
