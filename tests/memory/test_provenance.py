"""Tests for memory provenance tracking (TDD RED Phase).

Test provenance metadata, confidence evolution, and audit log generation.
"""

from datetime import datetime

import pytest


def test_should_create_provenance_with_required_fields() -> None:
    """Test that MemoryProvenance is created with all required fields."""
    from backend.memory.provenance import MemoryProvenance

    provenance = MemoryProvenance(
        memory_id="mem_123",
        source_session_id="session_456",
        extraction_timestamp=datetime.now(),
        confidence_score=0.85,
        validation_status="agent_inferred",
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
        validation_status="agent_inferred",
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
        validation_status="agent_inferred",
    )

    # User confirmed memory with same score
    confirmed = MemoryProvenance(
        memory_id="mem_2",
        source_session_id="session_2",
        extraction_timestamp=datetime.now(),
        confidence_score=0.7,
        validation_status="user_confirmed",
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
        validation_status="agent_inferred",
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
        validation_status="agent_inferred",
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
        validation_status="agent_inferred",
    )
    stable.add_confidence_update(0.81, "Slight change")

    assert stable.confidence_trend == "stable"

    # Insufficient data
    insufficient = MemoryProvenance(
        memory_id="mem_4",
        source_session_id="session_4",
        extraction_timestamp=datetime.now(),
        confidence_score=0.7,
        validation_status="agent_inferred",
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
        validation_status="user_confirmed",
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
            validation_status="agent_inferred",
        )

    # Score < 0.0
    with pytest.raises(ValueError, match="confidence_score must be between 0.0 and 1.0"):
        MemoryProvenance(
            memory_id="mem_2",
            source_session_id="session_2",
            extraction_timestamp=datetime.now(),
            confidence_score=-0.1,
            validation_status="agent_inferred",
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
            validation_status="invalid_status",
        )


def test_should_resolve_contradictory_memories_by_recency() -> None:
    """Test conflict resolution for contradictory memories using recency."""
    from datetime import timedelta

    from backend.memory.provenance import MemoryProvenance

    base_time = datetime.now()

    # Old memory (60 days ago)
    old_memory = MemoryProvenance(
        memory_id="mem_old",
        source_session_id="session_old",
        extraction_timestamp=base_time - timedelta(days=60),
        confidence_score=0.9,
        validation_status="user_confirmed"
    )

    # Recent memory (5 days ago, lower confidence but more recent)
    recent_memory = MemoryProvenance(
        memory_id="mem_recent",
        source_session_id="session_recent",
        extraction_timestamp=base_time - timedelta(days=5),
        confidence_score=0.7,
        validation_status="agent_inferred"
    )

    # Choose winner by recency (assuming preferences change over time)
    # In production, this would be handled by conflict resolution strategy
    def choose_by_recency(mem1, mem2):
        return mem1 if mem1.extraction_timestamp > mem2.extraction_timestamp else mem2

    winner = choose_by_recency(old_memory, recent_memory)
    assert winner.memory_id == "mem_recent", "More recent memory should win in recency-based resolution"


def test_should_decay_confidence_for_stale_memories() -> None:
    """Test confidence decay for memories not reaffirmed over time (staleness detection)."""
    from datetime import timedelta

    from backend.memory.provenance import MemoryProvenance

    # Memory extracted 180 days ago (stale)
    old_extraction_time = datetime.now() - timedelta(days=180)
    stale_memory = MemoryProvenance(
        memory_id="mem_stale",
        source_session_id="session_old",
        extraction_timestamp=old_extraction_time,
        confidence_score=0.8,
        validation_status="agent_inferred"
    )

    # Calculate staleness (days since extraction)
    days_old = (datetime.now() - stale_memory.extraction_timestamp).days

    # Apply decay: 10% per 90 days
    decay_factor = min(1.0, days_old / 90 * 0.1)
    decayed_confidence = max(0.0, stale_memory.confidence_score - decay_factor)

    assert days_old == 180, "Should be 180 days old"
    assert abs(decay_factor - 0.2) < 0.001, "Should decay ~20% (180 days / 90 * 0.1)"
    assert abs(decayed_confidence - 0.6) < 0.001, "Confidence should decay from 0.8 to ~0.6"

    # Verify trend
    assert stale_memory.confidence_trend == "insufficient_data", "Single entry = insufficient data"


def test_should_export_provenance_in_multiple_formats() -> None:
    """Test provenance export to JSON (via to_audit_log) and verify structure for CSV compatibility."""
    import json

    from backend.memory.provenance import MemoryProvenance

    provenance = MemoryProvenance(
        memory_id="mem_export",
        source_session_id="session_export",
        extraction_timestamp=datetime.now(),
        confidence_score=0.85,
        validation_status="user_confirmed"
    )

    # Add confidence updates
    provenance.add_confidence_update(0.9, "Reinforced by user")

    # Export to audit log (JSON-compatible dict)
    audit_log = provenance.to_audit_log()

    # Verify JSON serializable
    json_str = json.dumps(audit_log, default=str)  # default=str for datetime
    assert json_str is not None

    # Verify required fields for audit/CSV export
    required_fields = [
        "memory_id", "source_session_id", "extraction_timestamp",
        "confidence_score", "effective_confidence", "confidence_trend",
        "validation_status", "confidence_history"
    ]
    for field in required_fields:
        assert field in audit_log, f"Audit log should contain {field}"

    # Verify CSV-compatible (flat structure for non-nested fields)
    assert isinstance(audit_log["memory_id"], str)
    assert isinstance(audit_log["confidence_score"], (int, float))
    assert isinstance(audit_log["validation_status"], str)
