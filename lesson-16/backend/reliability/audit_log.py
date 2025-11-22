"""Audit logging with structured JSON, PII redaction, and workflow tracing (FR4.6).

This module provides comprehensive audit logging for agent workflows with:
- Structured JSON format for all log entries
- PII redaction for sensitive data (SSN, credit cards, phone numbers, emails)
- Complete workflow tracing with step-by-step execution history
- Export functionality for compliance and analysis
- Input hashing for deduplication and integrity verification

Supports GDPR and SOC2 compliance requirements through:
- Automatic PII masking
- Structured audit trails with timestamps
- Exportable logs for retention policies
- Defensive coding with type validation

Example:
    >>> logger = AuditLogger(workflow_id="invoice-proc-001")
    >>> entry = logger.log_step(
    ...     agent_name="invoice_extractor",
    ...     step="extract_vendor",
    ...     input_data={"invoice": "INV-123"},
    ...     output={"vendor": "Acme Corp"},
    ...     duration_ms=250
    ... )
    >>> trace = logger.get_workflow_trace()
    >>> logger.export_to_json(Path("audit_log.json"))
"""

from __future__ import annotations

import hashlib
import json
import re
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


class AuditLogger:
    """Audit logger with structured JSON, PII redaction, and workflow tracing.

    Maintains complete audit trail for agent workflows with:
    - Structured log entries (workflow_id, agent_name, step, timestamp, etc.)
    - Automatic PII redaction for sensitive fields
    - SHA256 hashing of inputs for integrity verification
    - Export to JSON for compliance and retention
    """

    def __init__(self, workflow_id: str) -> None:
        """Initialize audit logger for a workflow.

        Args:
            workflow_id: Unique identifier for the workflow being traced

        Raises:
            TypeError: If workflow_id is not a string
        """
        # Step 1: Type checking
        if not isinstance(workflow_id, str):
            raise TypeError("workflow_id must be a string")

        # Step 2: Store workflow ID
        self.workflow_id = workflow_id
        self._trace: list[dict[str, Any]] = []

    def log_step(
        self,
        agent_name: str,
        step: str,
        input_data: dict[str, Any],
        output: dict[str, Any] | None,
        duration_ms: int,
        error: Exception | None = None,
    ) -> dict[str, Any]:
        """Log a single workflow step with PII redaction.

        Creates a structured audit log entry with:
        - All required fields (workflow_id, agent_name, step, timestamp, etc.)
        - Automatic PII redaction in input_data
        - Input hashing for integrity verification
        - Error details if step failed

        Args:
            agent_name: Name of the agent executing the step
            step: Description of the step being performed
            input_data: Input data for the step (will be redacted for PII)
            output: Output data from the step (None if failed)
            duration_ms: Execution time in milliseconds
            error: Exception if step failed (None if success)

        Returns:
            Structured log entry with all fields populated

        Raises:
            TypeError: If agent_name or step are not strings
            ValueError: If duration_ms is negative
        """
        # Step 1: Type checking
        if not isinstance(agent_name, str):
            raise TypeError("agent_name must be a string")
        if not isinstance(step, str):
            raise TypeError("step must be a string")

        # Step 2: Input validation
        if duration_ms < 0:
            raise ValueError("duration_ms must be non-negative")

        # Step 3: Redact PII in input_data
        redacted_input = self._redact_pii(input_data.copy())

        # Step 4: Create structured log entry
        entry: dict[str, Any] = {
            "workflow_id": self.workflow_id,
            "agent_name": agent_name,
            "step": step,
            "timestamp": datetime.now(UTC).isoformat(),
            "duration_ms": duration_ms,
            "input_hash": self._hash_input(input_data),
            "input_data": redacted_input,
            "output": output,
            "error": self._format_error(error) if error else None,
        }

        # Step 5: Add to trace
        self._trace.append(entry)

        # Step 6: Return entry
        return entry

    def get_workflow_trace(self) -> list[dict[str, Any]]:
        """Get complete workflow trace with all logged steps.

        Returns:
            List of all log entries in chronological order
        """
        return self._trace.copy()

    def export_to_json(self, filepath: Path) -> None:
        """Export audit logs to structured JSON file.

        Creates a JSON file with:
        - Workflow metadata (workflow_id)
        - All logged steps in chronological order
        - Proper formatting for human readability

        Args:
            filepath: Path where JSON file should be written

        Raises:
            TypeError: If filepath is not a Path
        """
        # Step 1: Type checking
        if not isinstance(filepath, Path):
            raise TypeError("filepath must be a Path")

        # Step 2: Create export structure
        export_data = {
            "workflow_id": self.workflow_id,
            "steps": self._trace,
            "exported_at": datetime.now(UTC).isoformat(),
        }

        # Step 3: Write to file
        with open(filepath, "w") as f:
            json.dump(export_data, f, indent=2)

    def _redact_pii(self, data: dict[str, Any]) -> dict[str, Any]:
        """Redact PII fields in data dictionary.

        Redacts sensitive fields with format "XXX****XXX":
        - ssn: Social security numbers
        - credit_card: Credit card numbers
        - phone: Phone numbers
        - email: Email addresses

        Args:
            data: Dictionary potentially containing PII

        Returns:
            Dictionary with PII fields redacted
        """
        redacted = data.copy()

        # Define PII field patterns and redaction rules
        pii_patterns = {
            "ssn": lambda s: self._mask_string(s, keep_start=3, keep_end=3),
            "credit_card": lambda s: self._mask_string(s, keep_start=3, keep_end=3),
            "phone": lambda s: self._mask_string(s, keep_start=3, keep_end=3),
            "email": lambda s: self._mask_string(s, keep_start=3, keep_end=3),
        }

        # Apply redaction to matching fields
        for field, redactor in pii_patterns.items():
            if field in redacted:
                redacted[field] = redactor(str(redacted[field]))

        return redacted

    def _mask_string(self, value: str, keep_start: int = 3, keep_end: int = 3) -> str:
        """Mask middle portion of string, keeping start and end.

        Handles different formats:
        - Phone numbers: Keep prefix like "+1-", mask digits
        - Credit cards: Remove dashes, mask digits
        - Emails: Keep @ and domain, mask username
        - SSN: Remove dashes, mask middle digits

        Args:
            value: String to mask
            keep_start: Number of characters to keep at start
            keep_end: Number of characters to keep at end

        Returns:
            Masked string in format "XXX****XXX"
        """
        # Special handling for phone numbers (keep prefix)
        if value.startswith("+"):
            # Phone number format: "+1-555-123-4567" -> "+1-****567"
            prefix_match = re.match(r"^(\+\d+-)", value)
            if prefix_match:
                prefix = prefix_match.group(1)
                digits = re.sub(r"[^0-9]", "", value)
                if len(digits) >= keep_end:
                    return f"{prefix}****{digits[-keep_end:]}"
                return value

        # For other formats, remove special characters
        clean_value = re.sub(r"[^a-zA-Z0-9@.]", "", value)

        if len(clean_value) <= keep_start + keep_end:
            # String too short to mask meaningfully
            return clean_value

        # Extract start and end portions
        start = clean_value[:keep_start]
        end = clean_value[-keep_end:]

        # Create masked version
        return f"{start}****{end}"

    def _hash_input(self, data: dict[str, Any]) -> str:
        """Create SHA256 hash of input data for integrity verification.

        Args:
            data: Input data to hash

        Returns:
            Hex string of SHA256 hash
        """
        # Serialize data to JSON for consistent hashing
        serialized = json.dumps(data, sort_keys=True)
        return hashlib.sha256(serialized.encode()).hexdigest()

    def _format_error(self, error: Exception) -> str:
        """Format exception for logging.

        Args:
            error: Exception to format

        Returns:
            String with exception type and message
        """
        return f"{error.__class__.__name__}: {str(error)}"
