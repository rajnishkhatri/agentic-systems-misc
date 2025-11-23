"""PII redaction for spiritual/personal context in memories.

This module provides PII (Personally Identifiable Information) redaction
for memory extraction, while preserving Bhagavad Gita character names and
philosophical terms.
"""

import re
import uuid
from datetime import datetime

from backend.memory.provenance import MemoryProvenance


class PIIRedactor:
    """Redact PII from text while preserving Gita-specific context.

    Uses regex patterns to detect emails, phones, names, and locations.
    Maintains a whitelist of Bhagavad Gita characters and terms to avoid
    false positives.
    """

    def __init__(self) -> None:
        """Initialize PII redactor with regex patterns and whitelist."""
        # Step 1: Define PII regex patterns
        self.email_pattern = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b")
        # Phone pattern: matches 7-digit (555-1234) and 10-digit formats
        self.phone_pattern = re.compile(
            r"\b(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3,4}[-.\s]?\d{4}\b|"
            r"\b\d{3}[-.\s]?\d{4}\b"
        )

        # Name pattern: Capitalized word followed by capitalized word (with optional middle initial)
        self.name_pattern = re.compile(r"\b[A-Z][a-z]+ (?:[A-Z]\. )?[A-Z][a-z]+\b")

        # Location pattern: Common city/state patterns (simplified)
        self.location_pattern = re.compile(
            r"\b\d+\s+[A-Z][a-z]+\s+(?:Street|St|Avenue|Ave|Road|Rd|Boulevard|Blvd|Drive|Dr|Lane|Ln)\b|"
            r"\b(?:San Francisco|Los Angeles|New York|California|Texas|Florida)\b",
            re.IGNORECASE,
        )

        # Step 2: Create whitelist for Gita characters and terms
        self.whitelist = {
            # Characters
            "Arjuna",
            "Krishna",
            "Sanjaya",
            "Dhritarashtra",
            "Yudhishthira",
            "Bhima",
            "Nakula",
            "Sahadeva",
            "Draupadi",
            "Karna",
            "Duryodhana",
            "Drona",
            "Bhishma",
            # Commentators and scholars
            "Swami Sivananda",
            "Swami Chinmayananda",
            "Swami Prabhupada",
            "Adi Shankaracharya",
            # Philosophical terms
            "Brahman",
            "Atman",
            "Karma",
            "Dharma",
            "Yoga",
            "Bhakti",
            "Jnana",
            "Raja",
            "Hatha",
        }

    def redact(self, text: str) -> tuple[str, bool]:
        """Redact PII from text.

        Args:
            text: Input text potentially containing PII

        Returns:
            Tuple of (redacted_text, pii_found)
        """
        # Step 1: Track if PII was found
        pii_found = False
        redacted_text = text

        # Step 2: Redact emails
        if self.email_pattern.search(redacted_text):
            redacted_text = self.email_pattern.sub("[EMAIL_REDACTED]", redacted_text)
            pii_found = True

        # Step 3: Redact phone numbers
        if self.phone_pattern.search(redacted_text):
            redacted_text = self.phone_pattern.sub("[PHONE_REDACTED]", redacted_text)
            pii_found = True

        # Step 4: Redact locations
        if self.location_pattern.search(redacted_text):
            redacted_text = self.location_pattern.sub("[LOCATION_REDACTED]", redacted_text)
            pii_found = True

        # Step 5: Redact names (with whitelist check)
        name_matches = self.name_pattern.findall(redacted_text)
        for name in name_matches:
            # Check if name is in whitelist
            if name not in self.whitelist:
                redacted_text = redacted_text.replace(name, "[NAME_REDACTED]")
                pii_found = True

        # Step 6: Return result
        return redacted_text, pii_found


def extract_memory_with_pii_redaction(
    text: str, source_session_id: str, confidence_score: float = 0.7, validation_status: str = "agent_inferred"
) -> tuple[str, MemoryProvenance]:
    """Extract memory with PII redaction and provenance tracking.

    Args:
        text: Memory content to extract
        source_session_id: ID of session where memory was extracted
        confidence_score: Initial confidence score (0.0-1.0)
        validation_status: Validation status (agent_inferred, user_confirmed, disputed)

    Returns:
        Tuple of (redacted_text, provenance)
    """
    # Step 1: Redact PII
    redactor = PIIRedactor()
    redacted_text, pii_found = redactor.redact(text)

    # Step 2: Create provenance
    memory_id = generate_uuid()
    provenance = MemoryProvenance(
        memory_id=memory_id,
        source_session_id=source_session_id,
        extraction_timestamp=datetime.now(),
        confidence_score=confidence_score,
        validation_status=validation_status,
    )

    # Step 3: If PII was found, lower confidence slightly
    if pii_found:
        provenance.add_confidence_update(
            confidence_score * 0.95, "PII detected and redacted - slight confidence penalty"
        )

    return redacted_text, provenance


def generate_uuid() -> str:
    """Generate a unique memory ID.

    Returns:
        UUID string in format mem_<uuid4>
    """
    return f"mem_{uuid.uuid4().hex[:12]}"
