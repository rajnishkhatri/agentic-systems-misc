"""Tests for memory provenance tracking (TDD RED Phase).

Test provenance metadata, confidence evolution, and audit log generation.
"""

import pytest
from datetime import datetime


def test_should_create_provenance_with_required_fields() -> None:
    """Test that MemoryProvenance is created with all required fields."""
    from backend.memory.provenance import MemoryProvenance

    provenance = MemoryProvenance(
        memory_id="mem_123",
        source_session_id="session_456",
        extraction_timestamp=datetime.now(),
        confidence_score=0.85,
        validation_status="agent_inferred"
    )

    assert provenance.memory_id == "mem_123"
    assert provenance.source_session_id == "session_456"
    assert provenance.extraction_timestamp is not None
    assert provenance.confidence_score == 0.85
    assert provenance.validation_status == "agent_inferred"


def test_should_track_confidence_evolution() -> None:
    """Test that confidence history is tracked correctly."""
    from backend.memory.provenance import MemoryProvenance

    provenance = MemoryProvenance(
        memory_id="mem_123",
        source_session_id="session_456",
        extraction_timestamp=datetime.now(),
        confidence_score=0.7,
        validation_status="agent_inferred"
    )

    # Add confidence updates
    provenance.add_confidence_update(0.8, "Confirmed by user in session_789")
    provenance.add_confidence_update(0.9, "Reinforced by multiple interactions")

    assert len(provenance.confidence_history) == 3  # Initial + 2 updates
    assert provenance.confidence_score == 0.9  # Latest score


def test_should_enforce_user_confirmed_higher_than_inferred() -> None:
    """Test that user_confirmed status boosts effective confidence."""
    from backend.memory.provenance import MemoryProvenance

    # Agent inferred memory
    inferred = MemoryProvenance(
        memory_id="mem_1",
        source_session_id="session_1",
        extraction_timestamp=datetime.now(),
        confidence_score=0.7,
        validation_status="agent_inferred"
    )

    # User confirmed memory with same score
    confirmed = MemoryProvenance(
        memory_id="mem_2",
        source_session_id="session_2",
        extraction_timestamp=datetime.now(),
        confidence_score=0.7,
        validation_status="user_confirmed"
    )

    # Effective confidence should be higher for user_confirmed
    assert confirmed.effective_confidence > inferred.effective_confidence


def test_should_calculate_confidence_trend() -> None:
    """Test confidence trend detection (increasing, decreasing, stable, insufficient_data)."""
    from backend.memory.provenance import MemoryProvenance

    # Increasing trend
    increasing = MemoryProvenance(
        memory_id="mem_1",
        source_session_id="session_1",
        extraction_timestamp=datetime.now(),
        confidence_score=0.5,
        validation_status="agent_inferred"
    )
    increasing.add_confidence_update(0.7, "First boost")
    increasing.add_confidence_update(0.9, "Second boost")

    assert increasing.confidence_trend == "increasing"

    # Decreasing trend
    decreasing = MemoryProvenance(
        memory_id="mem_2",
        source_session_id="session_2",
        extraction_timestamp=datetime.now(),
        confidence_score=0.9,
        validation_status="agent_inferred"
    )
    decreasing.add_confidence_update(0.7, "First drop")
    decreasing.add_confidence_update(0.5, "Second drop")

    assert decreasing.confidence_trend == "decreasing"

    # Stable trend
    stable = MemoryProvenance(
        memory_id="mem_3",
        source_session_id="session_3",
        extraction_timestamp=datetime.now(),
        confidence_score=0.8,
        validation_status="agent_inferred"
    )
    stable.add_confidence_update(0.81, "Slight change")

    assert stable.confidence_trend == "stable"

    # Insufficient data
    insufficient = MemoryProvenance(
        memory_id="mem_4",
        source_session_id="session_4",
        extraction_timestamp=datetime.now(),
        confidence_score=0.7,
        validation_status="agent_inferred"
    )

    assert insufficient.confidence_trend == "insufficient_data"


def test_should_export_audit_log() -> None:
    """Test that to_audit_log() returns dict with lineage, trustworthiness, compliance fields."""
    from backend.memory.provenance import MemoryProvenance

    provenance = MemoryProvenance(
        memory_id="mem_123",
        source_session_id="session_456",
        extraction_timestamp=datetime.now(),
        confidence_score=0.85,
        validation_status="user_confirmed"
    )
    provenance.add_confidence_update(0.9, "Reinforced")

    audit_log = provenance.to_audit_log()

    # Check lineage fields
    assert "memory_id" in audit_log
    assert "source_session_id" in audit_log
    assert "extraction_timestamp" in audit_log

    # Check trustworthiness fields
    assert "confidence_score" in audit_log
    assert "effective_confidence" in audit_log
    assert "confidence_trend" in audit_log
    assert "validation_status" in audit_log

    # Check compliance fields
    assert "confidence_history" in audit_log
    assert isinstance(audit_log["confidence_history"], list)


def test_should_raise_error_for_invalid_confidence_score() -> None:
    """Test that ValueError is raised for confidence score outside [0.0, 1.0]."""
    from backend.memory.provenance import MemoryProvenance

    # Score > 1.0
    with pytest.raises(ValueError, match="confidence_score must be between 0.0 and 1.0"):
        MemoryProvenance(
            memory_id="mem_1",
            source_session_id="session_1",
            extraction_timestamp=datetime.now(),
            confidence_score=1.5,
            validation_status="agent_inferred"
        )

    # Score < 0.0
    with pytest.raises(ValueError, match="confidence_score must be between 0.0 and 1.0"):
        MemoryProvenance(
            memory_id="mem_2",
            source_session_id="session_2",
            extraction_timestamp=datetime.now(),
            confidence_score=-0.1,
            validation_status="agent_inferred"
        )


def test_should_raise_error_for_invalid_validation_status() -> None:
    """Test that ValueError is raised for invalid validation_status."""
    from backend.memory.provenance import MemoryProvenance

    with pytest.raises(ValueError, match="validation_status must be one of"):
        MemoryProvenance(
            memory_id="mem_1",
            source_session_id="session_1",
            extraction_timestamp=datetime.now(),
            confidence_score=0.8,
            validation_status="invalid_status"
        )
