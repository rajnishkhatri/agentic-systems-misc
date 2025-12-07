"""PromptSecurityGuard - Defense against prompt injection attacks.

This module implements Gap 9 from the Closing the Gaps framework,
providing multi-layer defense against prompt injection attacks in
multi-agent bank dispute systems.

Architecture:
    Layer 1 - Pattern Matching (<5ms): Regex-based detection of known patterns
    Layer 2 - Structural Analysis (<20ms): Detection of role overrides and delimiters
    Layer 3 - LLM Guard (optional, <500ms): Advanced ML-based detection

Security Patterns Covered (OWASP LLM Top 10):
    - Instruction override (ignore previous, disregard prior)
    - Role hijacking (you are now, act as, pretend)
    - Prompt leakage (show prompt, reveal instructions)
    - Delimiter injection (```system, [INST], <|im_start|>)
    - Jailbreak attempts (DAN mode, developer mode)

Example:
    >>> guard = PromptSecurityGuard()
    >>> result = guard.scan_input("Ignore previous instructions")
    >>> print(result.is_safe)  # False
    >>> print(result.threat_type)  # "instruction_override"
"""

from __future__ import annotations

import hashlib
import json
import re
import time
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field


class ScanResult(BaseModel):
    """Result of a security scan.

    Attributes:
        is_safe: Whether the input passed security checks
        threat_type: Type of threat detected (None if safe)
        confidence: Confidence score for the detection (0.0-1.0)
        matched_patterns: List of pattern names that matched
        sanitized_input: Input with threats removed (if possible)
        scan_duration_ms: Time taken for the scan in milliseconds
    """

    is_safe: bool
    threat_type: str | None
    confidence: float = Field(ge=0.0, le=1.0)
    matched_patterns: list[str]
    sanitized_input: str | None
    scan_duration_ms: float


# Default injection patterns per OWASP LLM Top 10
INJECTION_PATTERNS: dict[str, list[str]] = {
    # Direct instruction override
    "instruction_override": [
        r"ignore\s+(all\s+)?(previous\s+)?instructions?",
        r"ignore\s+(your|the)\s+instructions?",
        r"disregard\s+(all\s+)?(prior\s+)?(instructions?|context|safety\s+guidelines?)",
        r"forget\s+(everything|what)\s+(you|I)\s+(said|told)",
        r"override\s+(your|the)\s+(programming|instructions?)",
    ],
    # Role hijacking
    "role_hijack": [
        r"you\s+are\s+now\s+",
        r"act\s+as\s+(if\s+you\s+are\s+)?",
        r"pretend\s+(to\s+be|you('re|\s+are))",
        r"from\s+now\s+on\s+you('re|\s+are)",
    ],
    # System prompt extraction
    "prompt_leak": [
        r"(show|reveal|print|output)\s+(me\s+)?(your|the)\s+(system\s+)?prompt",
        r"(show|reveal|print|output)\s+(me\s+)?(your|the)\s+instructions?",
        r"what\s+(are|is)\s+your\s+(instructions?|system\s+prompt)",
        r"repeat\s+(back\s+)?(your|the)\s+instructions?",
    ],
    # Delimiter injection
    "delimiter_injection": [
        r"```\s*system",
        r"\[INST\]",
        r"<\|im_start\|>",
        r"Human:\s*.*\s*Assistant:",
    ],
    # Jailbreak attempts
    "jailbreak": [
        r"DAN\s+mode",
        r"developer\s+mode\s+(enabled|activated|for)",
        r"(no|without)\s+(ethical|safety)\s+(guidelines|restrictions)",
    ],
}


class PromptSecurityGuard:
    """Defense against prompt injection attacks per Gap 9.

    Implements multi-layer defense:
        - Layer 1: Fast regex pattern matching (<5ms)
        - Layer 2: Structural analysis for role overrides (<20ms)
        - Layer 3: Optional LLM-based detection (<500ms)

    Attributes:
        _patterns: Dictionary of threat_type -> compiled regex patterns
        _enable_llm_guard: Whether to use LLM for advanced detection
        _log_to_db: Whether to log scans to PostgreSQL
        _max_input_length: Maximum allowed input length in bytes
        _threat_stats: Running count of detected threats by type

    Example:
        >>> guard = PromptSecurityGuard()
        >>> result = guard.scan_input("What is my dispute status?")
        >>> assert result.is_safe is True
    """

    def __init__(
        self,
        patterns_file: str | None = None,
        enable_llm_guard: bool = False,
        log_to_db: bool = True,
    ) -> None:
        """Initialize security guard.

        Args:
            patterns_file: Path to JSON file with custom patterns
            enable_llm_guard: Use LLM for advanced detection (slower, more accurate)
            log_to_db: Log all scans to PostgreSQL
        """
        self._enable_llm_guard = enable_llm_guard
        self._log_to_db = log_to_db
        self._max_input_length = 10240  # 10KB

        # Load patterns
        self._patterns = self._load_patterns(patterns_file)

        # Initialize threat statistics
        self._threat_stats: dict[str, int] = {}

    def _load_patterns(
        self, patterns_file: str | None
    ) -> dict[str, list[re.Pattern[str]]]:
        """Load and compile regex patterns.

        Args:
            patterns_file: Optional path to JSON file with custom patterns

        Returns:
            Dictionary mapping threat types to compiled regex patterns
        """
        patterns = INJECTION_PATTERNS.copy()

        # Load custom patterns from file if provided
        if patterns_file:
            path = Path(patterns_file)
            if path.exists():
                with open(path) as f:
                    custom_patterns = json.load(f)
                    for threat_type, pattern_list in custom_patterns.items():
                        if threat_type in patterns:
                            patterns[threat_type].extend(pattern_list)
                        else:
                            patterns[threat_type] = pattern_list

        # Compile all patterns
        compiled: dict[str, list[re.Pattern[str]]] = {}
        for threat_type, pattern_list in patterns.items():
            compiled[threat_type] = [
                re.compile(p, re.IGNORECASE) for p in pattern_list
            ]

        return compiled

    def scan_input(
        self, user_input: str, context: dict[str, Any] | None = None
    ) -> ScanResult:
        """Scan user input for security threats.

        Multi-layer detection:
            1. Pattern matching (fast, <5ms)
            2. Structural analysis (medium, <20ms)
            3. LLM guard if enabled (slow, <500ms)

        Args:
            user_input: Raw user input string
            context: Optional context (e.g., session_id, user_id)

        Returns:
            ScanResult with safety determination

        Raises:
            TypeError: If user_input is not a string
            ValueError: If user_input exceeds max length (10KB)
        """
        start_time = time.perf_counter()

        # Input validation
        if not isinstance(user_input, str):
            raise TypeError("user_input must be a string")

        if len(user_input.encode("utf-8")) > self._max_input_length:
            raise ValueError(
                f"user_input exceeds max length ({self._max_input_length} bytes)"
            )

        # Handle empty input
        if not user_input.strip():
            return ScanResult(
                is_safe=True,
                threat_type=None,
                confidence=1.0,
                matched_patterns=[],
                sanitized_input=user_input,
                scan_duration_ms=self._elapsed_ms(start_time),
            )

        # Layer 1: Pattern matching
        result = self._layer1_pattern_match(user_input)
        if not result.is_safe:
            result.scan_duration_ms = self._elapsed_ms(start_time)
            self._record_threat(result.threat_type)
            self._log_scan(user_input, result, context)
            return result

        # Layer 2: Structural analysis
        result = self._layer2_structural_analysis(user_input)
        if not result.is_safe:
            result.scan_duration_ms = self._elapsed_ms(start_time)
            self._record_threat(result.threat_type)
            self._log_scan(user_input, result, context)
            return result

        # Layer 3: LLM guard (optional)
        if self._enable_llm_guard:
            result = self._layer3_llm_guard(user_input)
            if not result.is_safe:
                result.scan_duration_ms = self._elapsed_ms(start_time)
                self._record_threat(result.threat_type)
                self._log_scan(user_input, result, context)
                return result

        # All layers passed
        result = ScanResult(
            is_safe=True,
            threat_type=None,
            confidence=1.0,
            matched_patterns=[],
            sanitized_input=user_input,
            scan_duration_ms=self._elapsed_ms(start_time),
        )
        self._log_scan(user_input, result, context)
        return result

    def scan_agent_output(self, agent_id: str, output: str) -> ScanResult:
        """Scan agent output before handoff to next agent.

        Prevents prompt infection from propagating across agents.
        Uses the same detection layers as scan_input().

        Args:
            agent_id: Identifier of the agent producing output
            output: Agent's output string to scan

        Returns:
            ScanResult with safety determination
        """
        context = {"agent_id": agent_id, "scan_type": "agent_output"}
        return self.scan_input(output, context)

    def sanitize(self, user_input: str) -> str:
        """Remove detected threats from input while preserving intent.

        Attempts to extract legitimate content from potentially
        malicious input. If the entire input is malicious, returns
        empty string or blocking marker.

        Args:
            user_input: Raw user input string

        Returns:
            Sanitized string (may be empty if entirely malicious)
        """
        if not isinstance(user_input, str):
            return ""

        # First check if input is safe - if not, try to sanitize
        scan_result = self._layer1_pattern_match(user_input)

        sanitized = user_input

        # Remove all matched patterns
        for threat_type, patterns in self._patterns.items():
            for pattern in patterns:
                # Replace matches with empty string
                sanitized = pattern.sub("", sanitized)

        # Also remove common malicious phrases not in patterns
        malicious_phrases = [
            r"and\s+reveal\s+\w+",
            r"and\s+show\s+\w+",
            r"and\s+tell\s+me\s+\w+",
        ]
        for phrase in malicious_phrases:
            sanitized = re.sub(phrase, "", sanitized, flags=re.IGNORECASE)

        # Clean up whitespace
        sanitized = " ".join(sanitized.split())

        # If input was detected as malicious and nothing meaningful remains
        if not scan_result.is_safe:
            # Check if anything meaningful remains after sanitization
            # Remove common filler words for the check
            meaningful = re.sub(r"\b(and|the|a|an|to|for|is|are|was|were)\b", "", sanitized, flags=re.IGNORECASE)
            meaningful = " ".join(meaningful.split())
            if len(meaningful.strip()) < 5:
                return ""

        # If nothing meaningful remains, return empty
        if not sanitized.strip() or len(sanitized.strip()) < 3:
            return ""

        return sanitized

    def add_pattern(self, pattern: str, threat_type: str) -> None:
        """Add new detection pattern at runtime.

        Args:
            pattern: Regex pattern string
            threat_type: Category for this threat
        """
        compiled = re.compile(pattern, re.IGNORECASE)

        if threat_type in self._patterns:
            self._patterns[threat_type].append(compiled)
        else:
            self._patterns[threat_type] = [compiled]

    def get_threat_stats(self) -> dict[str, int]:
        """Get counts of detected threats by type.

        Returns:
            Dictionary mapping threat types to detection counts
        """
        return self._threat_stats.copy()

    def _layer1_pattern_match(self, user_input: str) -> ScanResult:
        """Layer 1: Fast regex pattern matching.

        Target latency: <5ms

        Args:
            user_input: Input to scan

        Returns:
            ScanResult (is_safe=True if no patterns match)
        """
        input_lower = user_input.lower()

        for threat_type, patterns in self._patterns.items():
            matched_pattern_names = []
            for pattern in patterns:
                if pattern.search(input_lower):
                    matched_pattern_names.append(pattern.pattern)

            if matched_pattern_names:
                return ScanResult(
                    is_safe=False,
                    threat_type=threat_type,
                    confidence=0.95,
                    matched_patterns=matched_pattern_names,
                    sanitized_input=None,
                    scan_duration_ms=0,  # Will be set by caller
                )

        return ScanResult(
            is_safe=True,
            threat_type=None,
            confidence=1.0,
            matched_patterns=[],
            sanitized_input=user_input,
            scan_duration_ms=0,
        )

    def _layer2_structural_analysis(self, user_input: str) -> ScanResult:
        """Layer 2: Structural analysis for complex attacks.

        Target latency: <20ms

        Detects:
            - Role override structures
            - Instruction delimiter patterns
            - Multi-line injection attempts

        Args:
            user_input: Input to analyze

        Returns:
            ScanResult (is_safe=True if no structural issues found)
        """
        # Check for role override structures
        if self._contains_role_override(user_input):
            return ScanResult(
                is_safe=False,
                threat_type="role_hijack",
                confidence=0.85,
                matched_patterns=["structural_role_override"],
                sanitized_input=None,
                scan_duration_ms=0,
            )

        # Check for instruction delimiter structures
        if self._contains_instruction_delimiter(user_input):
            return ScanResult(
                is_safe=False,
                threat_type="delimiter_injection",
                confidence=0.90,
                matched_patterns=["structural_delimiter"],
                sanitized_input=None,
                scan_duration_ms=0,
            )

        return ScanResult(
            is_safe=True,
            threat_type=None,
            confidence=1.0,
            matched_patterns=[],
            sanitized_input=user_input,
            scan_duration_ms=0,
        )

    def _contains_role_override(self, text: str) -> bool:
        """Check for role override structural patterns.

        Args:
            text: Text to analyze

        Returns:
            True if role override structure detected
        """
        # Patterns that indicate role override attempts
        role_patterns = [
            r"from\s+now\s+on.*you('re|\s+are)",
            r"for\s+the\s+rest\s+of.*conversation.*you",
            r"new\s+identity.*you\s+are",
        ]

        text_lower = text.lower()
        for pattern in role_patterns:
            if re.search(pattern, text_lower, re.IGNORECASE):
                return True

        return False

    def _contains_instruction_delimiter(self, text: str) -> bool:
        """Check for instruction delimiter injection.

        Args:
            text: Text to analyze

        Returns:
            True if instruction delimiter detected
        """
        # Common delimiters used in various LLM formats
        delimiter_patterns = [
            r"<\|.*\|>",  # OpenAI format
            r"\[/?INST\]",  # Llama format
            r"###\s*(System|Human|Assistant)",  # Markdown format
            r"<(system|user|assistant)>",  # XML-style
        ]

        for pattern in delimiter_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return True

        return False

    def _layer3_llm_guard(self, user_input: str) -> ScanResult:
        """Layer 3: LLM-based advanced detection.

        Target latency: <500ms

        Uses an LLM to classify input as potentially malicious.
        Only called if enable_llm_guard=True.

        Args:
            user_input: Input to analyze

        Returns:
            ScanResult from LLM classification
        """
        # Placeholder for LLM integration
        # In production, this would call an LLM with a classification prompt
        return ScanResult(
            is_safe=True,
            threat_type=None,
            confidence=1.0,
            matched_patterns=[],
            sanitized_input=user_input,
            scan_duration_ms=0,
        )

    def _record_threat(self, threat_type: str | None) -> None:
        """Record threat detection for statistics.

        Args:
            threat_type: Type of threat detected
        """
        if threat_type:
            self._threat_stats[threat_type] = self._threat_stats.get(threat_type, 0) + 1

    def _log_scan(
        self,
        user_input: str,
        result: ScanResult,
        context: dict[str, Any] | None,
    ) -> None:
        """Log scan result to database.

        Args:
            user_input: Original input (will be hashed)
            result: Scan result
            context: Optional context information
        """
        if not self._log_to_db:
            return

        # In production, this would write to PostgreSQL
        # For now, we just prepare the data structure
        _log_data = {
            "input_hash": hashlib.sha256(user_input.encode()).hexdigest(),
            "input_length": len(user_input),
            "is_safe": result.is_safe,
            "threat_type": result.threat_type,
            "confidence": result.confidence,
            "matched_patterns": result.matched_patterns,
            "scan_duration_ms": result.scan_duration_ms,
            "context": context or {},
        }
        # TODO: Async write to PostgreSQL

    @staticmethod
    def _elapsed_ms(start_time: float) -> float:
        """Calculate elapsed time in milliseconds.

        Args:
            start_time: Start time from time.perf_counter()

        Returns:
            Elapsed time in milliseconds
        """
        return (time.perf_counter() - start_time) * 1000

