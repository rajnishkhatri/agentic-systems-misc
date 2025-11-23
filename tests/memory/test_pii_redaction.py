"""Tests for PII redaction in memory extraction (TDD RED Phase).

Test email, phone, name, location redaction while preserving Gita context.
"""

import pytest


def test_should_redact_email_addresses() -> None:
    """Test that email addresses are detected and redacted."""
    from backend.memory.pii_redaction import PIIRedactor

    redactor = PIIRedactor()
    text = "My email is john.doe@example.com and you can reach me there."

    redacted_text, pii_found = redactor.redact(text)

    assert "[EMAIL_REDACTED]" in redacted_text
    assert "john.doe@example.com" not in redacted_text
    assert pii_found is True


def test_should_redact_phone_numbers() -> None:
    """Test that phone numbers are detected and redacted."""
    from backend.memory.pii_redaction import PIIRedactor

    redactor = PIIRedactor()
    text = "Call me at 555-123-4567 or (555) 987-6543."

    redacted_text, pii_found = redactor.redact(text)

    assert "[PHONE_REDACTED]" in redacted_text
    assert "555-123-4567" not in redacted_text
    assert "(555) 987-6543" not in redacted_text
    assert pii_found is True


def test_should_redact_full_names() -> None:
    """Test that full names are detected and redacted."""
    from backend.memory.pii_redaction import PIIRedactor

    redactor = PIIRedactor()
    text = "My name is John Smith and I live in California."

    redacted_text, pii_found = redactor.redact(text)

    assert "[NAME_REDACTED]" in redacted_text
    assert "John Smith" not in redacted_text
    assert pii_found is True


def test_should_redact_locations() -> None:
    """Test that location information is detected and redacted."""
    from backend.memory.pii_redaction import PIIRedactor

    redactor = PIIRedactor()
    text = "I live in San Francisco, California at 123 Main Street."

    redacted_text, pii_found = redactor.redact(text)

    assert "[LOCATION_REDACTED]" in redacted_text
    assert pii_found is True


def test_should_not_redact_false_positives() -> None:
    """Test that Gita character names and terms are not redacted."""
    from backend.memory.pii_redaction import PIIRedactor

    redactor = PIIRedactor()

    # Character names from Bhagavad Gita
    text1 = "Arjuna asked Krishna about karma yoga."
    redacted1, pii_found1 = redactor.redact(text1)
    assert "Arjuna" in redacted1  # Should NOT be redacted
    assert "Krishna" in redacted1  # Should NOT be redacted
    assert pii_found1 is False

    # Philosophical terms
    text2 = "The concept of karma is central to the teaching."
    redacted2, pii_found2 = redactor.redact(text2)
    assert "karma" in redacted2  # Should NOT be redacted
    assert pii_found2 is False


def test_should_preserve_sentence_structure() -> None:
    """Test that redacted text remains grammatically correct."""
    from backend.memory.pii_redaction import PIIRedactor

    redactor = PIIRedactor()
    text = "John Smith called from 555-1234 asking about karma yoga."

    redacted_text, pii_found = redactor.redact(text)

    # Should still be readable
    assert redacted_text.endswith(".")  # Sentence ending preserved
    assert "karma yoga" in redacted_text  # Content preserved
    assert "[NAME_REDACTED]" in redacted_text
    assert "[PHONE_REDACTED]" in redacted_text
    assert pii_found is True


def test_should_return_pii_found_flag() -> None:
    """Test that redact() returns tuple (redacted_text, pii_found: bool)."""
    from backend.memory.pii_redaction import PIIRedactor

    redactor = PIIRedactor()

    # Text with PII
    text_with_pii = "Email me at test@example.com"
    redacted1, pii_found1 = redactor.redact(text_with_pii)
    assert isinstance(redacted1, str)
    assert isinstance(pii_found1, bool)
    assert pii_found1 is True

    # Text without PII
    text_without_pii = "Krishna taught Arjuna about dharma and karma."
    redacted2, pii_found2 = redactor.redact(text_without_pii)
    assert isinstance(redacted2, str)
    assert isinstance(pii_found2, bool)
    assert pii_found2 is False


def test_should_integrate_with_provenance() -> None:
    """Test extract_memory_with_pii_redaction integration function."""
    from backend.memory.pii_redaction import extract_memory_with_pii_redaction

    text = "John Smith (john@example.com) prefers Swami Sivananda's commentary on karma yoga."

    redacted_text, provenance = extract_memory_with_pii_redaction(
        text=text,
        source_session_id="session_123",
        confidence_score=0.8,
        validation_status="agent_inferred"
    )

    # Check redaction happened
    assert "[NAME_REDACTED]" in redacted_text
    assert "[EMAIL_REDACTED]" in redacted_text
    assert "karma yoga" in redacted_text

    # Check provenance created
    assert provenance.source_session_id == "session_123"
    assert provenance.memory_id.startswith("mem_")
    # Confidence should be lowered due to PII detection
    assert provenance.confidence_score < 0.8


def test_should_generate_unique_memory_ids() -> None:
    """Test that generate_uuid creates unique IDs."""
    from backend.memory.pii_redaction import generate_uuid

    id1 = generate_uuid()
    id2 = generate_uuid()

    assert id1.startswith("mem_")
    assert id2.startswith("mem_")
    assert id1 != id2  # Should be unique
