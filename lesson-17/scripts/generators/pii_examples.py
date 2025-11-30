"""PII Examples Generator for GuardRails validation testing.

Generates 50 synthetic text samples containing various PII types:
- SSN (Social Security Numbers)
- Credit Card numbers
- Email addresses
- Phone numbers
- Medical Record Numbers (MRN)
- Passport numbers
- Driver's License numbers

Each example includes gold labels for validation testing:
- pii_spans: exact positions of PII in text
- expected_redacted: text with PII replaced by [REDACTED]
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any

from . import (
    COMPANY_NAMES,
    EMAIL_DOMAINS,
    FIRST_NAMES,
    LAST_NAMES,
    MEDICAL_CONDITIONS,
    US_STATES,
    BaseGenerator,
    generate_credit_card,
    generate_drivers_license,
    generate_email,
    generate_medical_record_number,
    generate_passport_number,
    generate_phone,
    generate_ssn,
)


@dataclass
class PIISpan:
    """Represents a PII span in text."""

    pii_type: str
    start: int
    end: int
    text: str

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "type": self.pii_type,
            "start": self.start,
            "end": self.end,
            "text": self.text,
        }


class PIIExamplesGenerator(BaseGenerator):
    """Generator for PII-containing text samples.

    Creates realistic text samples with embedded PII for testing
    GuardRails PII detection and redaction capabilities.
    """

    # Templates for different contexts
    CUSTOMER_SERVICE_TEMPLATES = [
        "Customer {name} called regarding account issues. Contact: {email}, Phone: {phone}.",
        "Please update billing for {name}. New card ending in {cc_last4}: {credit_card}.",
        "Account holder {name} verified identity with SSN ending in {ssn_last4}: {ssn}.",
        "User {name} requests password reset. Email: {email}, backup phone: {phone}.",
        "Refund processed for {name} to card {credit_card}. Confirmation sent to {email}.",
    ]

    MEDICAL_TEMPLATES = [
        "Patient {name} (MRN: {mrn}) presented with {condition}. Contact: {phone}.",
        "Lab results for {name}, Medical Record {mrn}: {lab_result}. Follow-up scheduled.",
        "Discharge summary: {name} (DOB redacted), MRN {mrn}. Diagnosis: {condition}.",
        "Prescription for {name} ({mrn}): Medication authorized. Pharmacy: {phone}.",
        "Insurance claim for patient {name}, MRN {mrn}. SSN: {ssn} for verification.",
    ]

    TRAVEL_TEMPLATES = [
        "Passport holder {name}, Passport #{passport}. Flight booking confirmed.",
        "Visa application: {name}, Passport {passport}, Contact: {email}.",
        "Travel insurance for {name}. Passport: {passport}, Emergency: {phone}.",
        "Hotel reservation: {name}, Passport #{passport}. Card: {credit_card}.",
        "Rental car booking: {name}, Driver's License: {drivers_license}.",
    ]

    FINANCIAL_TEMPLATES = [
        "Loan application: {name}, SSN {ssn}. Annual income verified.",
        "Wire transfer from {name}, account ending 4521. Recipient: {company}.",
        "Tax document for {name}, SSN: {ssn}. W-2 processed.",
        "Credit check authorized: {name}, SSN {ssn}, DOB redacted.",
        "Investment account opened: {name}. Contact: {email}, Phone: {phone}.",
    ]

    DMV_TEMPLATES = [
        "License renewal: {name}, DL# {drivers_license}. Address updated.",
        "Vehicle registration: {name}, Driver's License {drivers_license}.",
        "Ticket payment: {name}, License {drivers_license}. Card: {credit_card}.",
        "ID verification: {name}, DL# {drivers_license}, SSN {ssn}.",
        "Driving record request: {name}, License Number: {drivers_license}.",
    ]

    CLEAN_TEMPLATES = [
        "Meeting scheduled with the project team for quarterly review.",
        "The weather forecast shows sunny skies for the weekend.",
        "New product launch planned for Q2. Marketing team aligned.",
        "Server maintenance completed. All systems operational.",
        "Annual report published. Revenue increased by 15% YoY.",
        "Training session on data security best practices tomorrow at 2 PM.",
        "The conference will be held in Building A, Room 305.",
        "Please review the attached design documents before Friday.",
    ]

    def generate(self, count: int = 50) -> list[dict[str, Any]]:
        """Generate PII examples.

        Args:
            count: Number of examples to generate (default: 50)

        Returns:
            List of PII example dictionaries with gold labels
        """
        examples: list[dict[str, Any]] = []

        # Distribution: ensure coverage of all PII types
        # 8 examples each for: SSN, CC, Email, Phone (32 total)
        # 6 examples each for: MRN, Passport, DL (18 total)
        # Total: 50 examples

        pii_distribution = [
            ("ssn", 8),
            ("credit_card", 8),
            ("email", 8),
            ("phone", 8),
            ("medical_record_number", 6),
            ("passport", 6),
            ("drivers_license", 6),
        ]

        example_id = 0
        for pii_type, pii_count in pii_distribution:
            for _ in range(pii_count):
                example = self._generate_example_with_pii(example_id, pii_type)
                examples.append(example)
                example_id += 1

        # Shuffle to mix PII types
        self._random.shuffle(examples)

        # Re-number after shuffle
        for i, example in enumerate(examples):
            example["pii_id"] = f"PII-{i + 1:03d}"

        return examples

    def _generate_example_with_pii(
        self, example_id: int, primary_pii_type: str
    ) -> dict[str, Any]:
        """Generate a single example with specified PII type.

        Args:
            example_id: Sequential ID for the example
            primary_pii_type: Type of PII to include

        Returns:
            Example dictionary with text, spans, and expected redacted output
        """
        first_name = self.random_choice(FIRST_NAMES)
        last_name = self.random_choice(LAST_NAMES)
        full_name = f"{first_name} {last_name}"

        # Generate PII values
        pii_values = {
            "ssn": generate_ssn(self._random),
            "credit_card": generate_credit_card(self._random),
            "email": generate_email(self._random, first_name, last_name),
            "phone": generate_phone(self._random),
            "mrn": generate_medical_record_number(self._random),
            "passport": generate_passport_number(self._random),
            "drivers_license": generate_drivers_license(self._random),
        }

        # Select template based on PII type
        template, pii_types_in_template = self._select_template(primary_pii_type)

        # Build substitution dict
        subs = {
            "name": full_name,
            "company": self.random_choice(COMPANY_NAMES),
            "condition": self.random_choice(MEDICAL_CONDITIONS),
            "lab_result": "Normal ranges",
            "ssn": pii_values["ssn"],
            "ssn_last4": pii_values["ssn"][-4:],
            "credit_card": pii_values["credit_card"],
            "cc_last4": pii_values["credit_card"][-4:],
            "email": pii_values["email"],
            "phone": pii_values["phone"],
            "mrn": pii_values["mrn"],
            "passport": pii_values["passport"],
            "drivers_license": pii_values["drivers_license"],
        }

        # Generate text
        text = template.format(**subs)

        # Find PII spans
        spans = self._find_pii_spans(text, pii_values, full_name, pii_types_in_template)

        # Generate expected redacted text
        expected_redacted = self._generate_redacted_text(text, spans)

        # Determine all PII types present
        pii_types_present = list({span.pii_type for span in spans})

        return {
            "pii_id": f"PII-{example_id + 1:03d}",
            "text": text,
            "contains_pii": len(spans) > 0,
            "pii_types": pii_types_present,
            "pii_spans": [span.to_dict() for span in spans],
            "expected_redacted": expected_redacted,
            "context": self._get_context_type(primary_pii_type),
            "gold_label": {
                "primary_pii_type": primary_pii_type,
                "pii_count": len(spans),
                "should_flag": len(spans) > 0,
            },
        }

    def _select_template(self, pii_type: str) -> tuple[str, list[str]]:
        """Select appropriate template for PII type.

        Args:
            pii_type: Type of PII to include

        Returns:
            Tuple of (template string, list of PII types in template)
        """
        if pii_type == "ssn":
            templates = self.FINANCIAL_TEMPLATES + [self.CUSTOMER_SERVICE_TEMPLATES[2]]
            pii_types = ["ssn", "name"]
        elif pii_type == "credit_card":
            templates = [
                self.CUSTOMER_SERVICE_TEMPLATES[1],
                self.CUSTOMER_SERVICE_TEMPLATES[4],
                self.TRAVEL_TEMPLATES[3],
            ]
            pii_types = ["credit_card", "name", "email"]
        elif pii_type == "email":
            templates = [
                self.CUSTOMER_SERVICE_TEMPLATES[0],
                self.CUSTOMER_SERVICE_TEMPLATES[3],
                self.FINANCIAL_TEMPLATES[4],
            ]
            pii_types = ["email", "name", "phone"]
        elif pii_type == "phone":
            templates = [
                self.CUSTOMER_SERVICE_TEMPLATES[0],
                self.MEDICAL_TEMPLATES[0],
                self.TRAVEL_TEMPLATES[2],
            ]
            pii_types = ["phone", "name"]
        elif pii_type == "medical_record_number":
            templates = self.MEDICAL_TEMPLATES
            pii_types = ["medical_record_number", "name"]
        elif pii_type == "passport":
            templates = self.TRAVEL_TEMPLATES[:3]
            pii_types = ["passport", "name"]
        elif pii_type == "drivers_license":
            templates = self.DMV_TEMPLATES
            pii_types = ["drivers_license", "name"]
        else:
            templates = self.CLEAN_TEMPLATES
            pii_types = []

        return self.random_choice(templates), pii_types

    def _find_pii_spans(
        self,
        text: str,
        pii_values: dict[str, str],
        full_name: str,
        pii_types: list[str],
    ) -> list[PIISpan]:
        """Find all PII spans in text.

        Args:
            text: Text to search
            pii_values: Dictionary of PII values
            full_name: Full name to search for
            pii_types: List of PII types to look for

        Returns:
            List of PIISpan objects
        """
        spans: list[PIISpan] = []

        # Search for each PII value
        pii_searches = [
            ("ssn", pii_values["ssn"]),
            ("credit_card", pii_values["credit_card"]),
            ("email", pii_values["email"]),
            ("phone", pii_values["phone"]),
            ("medical_record_number", pii_values["mrn"]),
            ("passport", pii_values["passport"]),
            ("drivers_license", pii_values["drivers_license"]),
            ("name", full_name),
        ]

        for pii_type, value in pii_searches:
            # Use regex to find exact matches
            pattern = re.escape(value)
            for match in re.finditer(pattern, text):
                spans.append(
                    PIISpan(
                        pii_type=pii_type,
                        start=match.start(),
                        end=match.end(),
                        text=match.group(),
                    )
                )

        # Sort by start position
        spans.sort(key=lambda s: s.start)

        return spans

    def _generate_redacted_text(self, text: str, spans: list[PIISpan]) -> str:
        """Generate text with PII redacted.

        Args:
            text: Original text
            spans: List of PII spans to redact

        Returns:
            Text with [REDACTED] replacing PII
        """
        if not spans:
            return text

        # Sort spans by start position (descending) to replace from end
        sorted_spans = sorted(spans, key=lambda s: s.start, reverse=True)

        result = text
        for span in sorted_spans:
            result = result[: span.start] + "[REDACTED]" + result[span.end :]

        return result

    def _get_context_type(self, pii_type: str) -> str:
        """Get context type for PII type.

        Args:
            pii_type: Type of PII

        Returns:
            Context category string
        """
        context_map = {
            "ssn": "financial",
            "credit_card": "customer_service",
            "email": "customer_service",
            "phone": "customer_service",
            "medical_record_number": "healthcare",
            "passport": "travel",
            "drivers_license": "dmv",
        }
        return context_map.get(pii_type, "general")


def generate_pii_examples(count: int = 50, seed: int = 42) -> list[dict[str, Any]]:
    """Generate PII examples dataset.

    Args:
        count: Number of examples to generate
        seed: Random seed for reproducibility

    Returns:
        List of PII example dictionaries
    """
    generator = PIIExamplesGenerator(seed=seed)
    return generator.generate(count)

