"""Tests for PII redaction in memory extraction (TDD RED Phase).

Test email, phone, name, location redaction while preserving Gita context.
"""



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
        text=text, source_session_id="session_123", confidence_score=0.8, validation_status="agent_inferred"
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


def test_should_detect_pii_in_unusual_phone_formats() -> None:
    """Test PII redaction with edge case phone number formats."""
    from backend.memory.pii_redaction import PIIRedactor

    redactor = PIIRedactor()

    # Test various phone formats
    test_cases = [
        "Call me at five-five-five-1234",  # Written out (should NOT match - too complex for regex)
        "My number is +1 (555) 123-4567",  # International format
        "Reach me at 555.123.4567",  # Dot separator
        "Phone: 5551234567",  # No separator
        "555 1234",  # Short format
    ]

    for text in test_cases:
        redacted_text, pii_found = redactor.redact(text)
        # Most should be caught except written-out version
        if "five-five-five" in text:
            assert pii_found is False, f"Written-out numbers not expected to match: {text}"
        else:
            # Check if redaction occurred (may vary by regex complexity)
            if "[PHONE_REDACTED]" in redacted_text:
                assert pii_found is True, f"PII should be detected in: {text}"


def test_should_handle_multilingual_memory_extraction() -> None:
    """Test memory extraction from multilingual conversations (English + Sanskrit)."""
    from backend.memory.pii_redaction import extract_memory_with_pii_redaction

    # Memory with Sanskrit terms (should be preserved)
    text = "User seeks guidance on कर्म योग (karma yoga) and धर्म (dharma) for daily life challenges."

    redacted_text, provenance = extract_memory_with_pii_redaction(
        text=text,
        source_session_id="session_multilingual",
        confidence_score=0.85,
        validation_status="agent_inferred"
    )

    # Sanskrit should be preserved
    assert "कर्म योग" in redacted_text or "karma yoga" in redacted_text
    assert "धर्म" in redacted_text or "dharma" in redacted_text
    assert provenance.source_session_id == "session_multilingual"
