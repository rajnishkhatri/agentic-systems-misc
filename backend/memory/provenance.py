"""Memory provenance tracking for audit and trustworthiness.

This module implements provenance metadata for memory entries, tracking:
- Source lineage (which session extracted this memory)
- Confidence evolution over time
- Validation status (agent_inferred vs. user_confirmed)
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Literal


@dataclass
class MemoryProvenance:
    """Provenance metadata for a memory entry.

    Tracks lineage, confidence evolution, and validation status for audit
    and trustworthiness assessment.
    """

    memory_id: str
    source_session_id: str
    extraction_timestamp: datetime
    confidence_score: float
    validation_status: Literal["agent_inferred", "user_confirmed", "disputed"]
    confidence_history: list[dict[str, float | str]] = field(default_factory=list)

    def __post_init__(self) -> None:
        """Validate fields and initialize confidence history.

        Raises:
            ValueError: If confidence_score or validation_status are invalid
        """
        # Step 1: Validate confidence_score range (defensive)
        if not (0.0 <= self.confidence_score <= 1.0):
            raise ValueError("confidence_score must be between 0.0 and 1.0")

        # Step 2: Validate validation_status enum (defensive)
        valid_statuses = {"agent_inferred", "user_confirmed", "disputed"}
        if self.validation_status not in valid_statuses:
            raise ValueError(f"validation_status must be one of {valid_statuses}, got '{self.validation_status}'")

        # Step 3: Initialize confidence history with initial entry
        if not self.confidence_history:
            self.confidence_history = [
                {
                    "score": self.confidence_score,
                    "timestamp": self.extraction_timestamp.isoformat(),
                    "reason": "Initial extraction",
                }
            ]

    def add_confidence_update(self, new_score: float, reason: str) -> None:
        """Add a confidence update to the history.

        Args:
            new_score: New confidence score (0.0-1.0)
            reason: Human-readable reason for the update

        Raises:
            ValueError: If new_score is outside [0.0, 1.0]
        """
        # Step 1: Validate new score (defensive)
        if not (0.0 <= new_score <= 1.0):
            raise ValueError("new_score must be between 0.0 and 1.0")

        # Step 2: Update current score
        self.confidence_score = new_score

        # Step 3: Append to history
        self.confidence_history.append({"score": new_score, "timestamp": datetime.now().isoformat(), "reason": reason})

    @property
    def effective_confidence(self) -> float:
        """Calculate effective confidence with validation status boost.

        User-confirmed memories get a 0.1 boost (capped at 1.0).
        Disputed memories get a 0.2 penalty (floored at 0.0).

        Returns:
            Adjusted confidence score
        """
        if self.validation_status == "user_confirmed":
            return min(1.0, self.confidence_score + 0.1)
        elif self.validation_status == "disputed":
            return max(0.0, self.confidence_score - 0.2)
        else:  # agent_inferred
            return self.confidence_score

    @property
    def confidence_trend(self) -> Literal["increasing", "decreasing", "stable", "insufficient_data"]:
        """Detect trend in confidence evolution.

        Returns:
            Trend classification based on confidence history
        """
        # Need at least 2 entries to detect trend
        if len(self.confidence_history) < 2:
            return "insufficient_data"

        # Compare first and last scores
        first_score = self.confidence_history[0]["score"]
        last_score = self.confidence_history[-1]["score"]
        delta = last_score - first_score

        # Thresholds for trend detection
        if delta > 0.1:
            return "increasing"
        elif delta < -0.1:
            return "decreasing"
        else:
            return "stable"

    def to_audit_log(self) -> dict[str, any]:
        """Export provenance to audit log format.

        Returns:
            Dictionary with lineage, trustworthiness, and compliance fields
        """
        return {
            # Lineage fields
            "memory_id": self.memory_id,
            "source_session_id": self.source_session_id,
            "extraction_timestamp": self.extraction_timestamp.isoformat(),
            # Trustworthiness fields
            "confidence_score": self.confidence_score,
            "effective_confidence": self.effective_confidence,
            "confidence_trend": self.confidence_trend,
            "validation_status": self.validation_status,
            # Compliance fields
            "confidence_history": self.confidence_history,
        }
