"""Configuration loader for Closing the Gaps framework.

Loads configuration from YAML files and environment variables,
providing typed configuration objects for governance components.

Environment Variable Overrides:
    - HITL_CONFIDENCE_THRESHOLD: Override confidence threshold
    - HITL_AMOUNT_THRESHOLD: Override amount threshold
    - PROMPT_SECURITY_ENABLE_LLM_GUARD: Enable LLM guard
    - GOVERNANCE_LOG_TO_DB: Enable/disable database logging

Example:
    >>> config = load_config()
    >>> security = get_security_config(config)
    >>> print(security.max_input_length)  # 10240
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml


@dataclass
class PromptSecurityConfig:
    """Configuration for PromptSecurityGuard.

    Attributes:
        patterns_file: Path to custom patterns JSON file
        enable_llm_guard: Whether to use LLM for advanced detection
        max_input_length: Maximum allowed input length in bytes
        log_to_db: Whether to log scans to PostgreSQL
        layer_1_target_ms: Target latency for pattern matching
        layer_2_target_ms: Target latency for structural analysis
        min_confidence: Minimum confidence to flag as threat
    """

    patterns_file: str | None = None
    enable_llm_guard: bool = False
    max_input_length: int = 10240
    log_to_db: bool = True
    layer_1_target_ms: int = 5
    layer_2_target_ms: int = 20
    min_confidence: float = 0.80


@dataclass
class HITLConfig:
    """Configuration for HITLController.

    Attributes:
        default_tier: Default oversight tier for unclassified actions
        confidence_threshold: Below this, always interrupt
        amount_threshold: Above this amount, always interrupt
        log_to_db: Whether to log decisions to PostgreSQL
        tier_1_actions: Actions that always require Tier 1
        tier_3_actions: Actions that are Tier 3 (logged only)
        high_risk_dispute_types: Dispute types that trigger higher tiers
        sample_rate_tier_2: Sample rate for Tier 2 review
    """

    default_tier: str = "tier_2"
    confidence_threshold: float = 0.85
    amount_threshold: float = 10000.0
    log_to_db: bool = True
    tier_1_actions: list[str] = field(
        default_factory=lambda: [
            "sar_filing",
            "payment_block",
            "account_close",
            "fraud_escalation",
        ]
    )
    tier_3_actions: list[str] = field(
        default_factory=lambda: [
            "info_lookup",
            "status_lookup",
            "knowledge_search",
            "faq_response",
        ]
    )
    high_risk_dispute_types: list[str] = field(
        default_factory=lambda: [
            "fraud",
            "identity_theft",
            "money_laundering",
            "account_takeover",
        ]
    )
    sample_rate_tier_2: float = 0.10


@dataclass
class GovernanceConfig:
    """Combined configuration for governance layer.

    Attributes:
        prompt_security: PromptSecurityGuard configuration
        hitl: HITLController configuration
        raw_config: Original raw configuration dict
    """

    prompt_security: PromptSecurityConfig
    hitl: HITLConfig
    raw_config: dict[str, Any] = field(default_factory=dict)


def get_config_path(filename: str = "security.yaml") -> Path:
    """Get path to configuration file.

    Searches in order:
        1. Current directory
        2. Package config directory
        3. Environment variable GOVERNANCE_CONFIG_PATH

    Args:
        filename: Configuration filename

    Returns:
        Path to configuration file

    Raises:
        FileNotFoundError: If configuration file not found
    """
    # Check environment variable first
    env_path = os.environ.get("GOVERNANCE_CONFIG_PATH")
    if env_path:
        path = Path(env_path)
        if path.exists():
            return path

    # Check current directory
    current_dir_path = Path.cwd() / filename
    if current_dir_path.exists():
        return current_dir_path

    # Check package config directory
    package_config_path = Path(__file__).parent / filename
    if package_config_path.exists():
        return package_config_path

    # Check lesson-18 config directory
    lesson_config_path = Path(__file__).parent.parent / "config" / filename
    if lesson_config_path.exists():
        return lesson_config_path

    raise FileNotFoundError(
        f"Configuration file '{filename}' not found. "
        f"Searched: {current_dir_path}, {package_config_path}"
    )


def load_config(config_path: str | Path | None = None) -> GovernanceConfig:
    """Load governance configuration from YAML file.

    Loads configuration and applies environment variable overrides.

    Args:
        config_path: Optional path to configuration file.
                    If None, searches default locations.

    Returns:
        GovernanceConfig with all settings

    Example:
        >>> config = load_config()
        >>> print(config.hitl.confidence_threshold)
        0.85
    """
    # Load from file if path provided, otherwise use defaults
    raw_config: dict[str, Any] = {}

    if config_path:
        path = Path(config_path)
        if path.exists():
            with open(path) as f:
                raw_config = yaml.safe_load(f) or {}
    else:
        try:
            path = get_config_path()
            with open(path) as f:
                raw_config = yaml.safe_load(f) or {}
        except FileNotFoundError:
            # Use defaults if no config file found
            pass

    # Build configuration objects
    prompt_security = _build_security_config(raw_config)
    hitl = _build_hitl_config(raw_config)

    # Apply environment variable overrides
    _apply_env_overrides(prompt_security, hitl)

    return GovernanceConfig(
        prompt_security=prompt_security,
        hitl=hitl,
        raw_config=raw_config,
    )


def get_security_config(config: GovernanceConfig) -> PromptSecurityConfig:
    """Extract PromptSecurityConfig from GovernanceConfig.

    Args:
        config: Full governance configuration

    Returns:
        PromptSecurityConfig instance
    """
    return config.prompt_security


def get_hitl_config(config: GovernanceConfig) -> HITLConfig:
    """Extract HITLConfig from GovernanceConfig.

    Args:
        config: Full governance configuration

    Returns:
        HITLConfig instance
    """
    return config.hitl


def _build_security_config(raw_config: dict[str, Any]) -> PromptSecurityConfig:
    """Build PromptSecurityConfig from raw config dict."""
    security_section = raw_config.get("prompt_security", {})
    performance = security_section.get("performance", {})
    detection = security_section.get("detection", {})

    return PromptSecurityConfig(
        patterns_file=security_section.get("patterns_file"),
        enable_llm_guard=security_section.get("enable_llm_guard", False),
        max_input_length=security_section.get("max_input_length", 10240),
        log_to_db=security_section.get("log_to_db", True),
        layer_1_target_ms=performance.get("layer_1_target_ms", 5),
        layer_2_target_ms=performance.get("layer_2_target_ms", 20),
        min_confidence=detection.get("min_confidence", 0.80),
    )


def _build_hitl_config(raw_config: dict[str, Any]) -> HITLConfig:
    """Build HITLConfig from raw config dict."""
    hitl_section = raw_config.get("hitl_controller", {})

    return HITLConfig(
        default_tier=hitl_section.get("default_tier", "tier_2"),
        confidence_threshold=hitl_section.get("confidence_threshold", 0.85),
        amount_threshold=hitl_section.get("amount_threshold", 10000.0),
        log_to_db=hitl_section.get("log_to_db", True),
        tier_1_actions=hitl_section.get(
            "tier_1_actions",
            ["sar_filing", "payment_block", "account_close", "fraud_escalation"],
        ),
        tier_3_actions=hitl_section.get(
            "tier_3_actions",
            ["info_lookup", "status_lookup", "knowledge_search", "faq_response"],
        ),
        high_risk_dispute_types=hitl_section.get(
            "high_risk_dispute_types",
            ["fraud", "identity_theft", "money_laundering", "account_takeover"],
        ),
        sample_rate_tier_2=hitl_section.get("sample_rate_tier_2", 0.10),
    )


def _apply_env_overrides(
    security: PromptSecurityConfig,
    hitl: HITLConfig,
) -> None:
    """Apply environment variable overrides to configuration.

    Environment variables:
        - HITL_CONFIDENCE_THRESHOLD: float
        - HITL_AMOUNT_THRESHOLD: float
        - PROMPT_SECURITY_ENABLE_LLM_GUARD: bool (true/false)
        - PROMPT_SECURITY_MAX_INPUT_LENGTH: int
        - GOVERNANCE_LOG_TO_DB: bool (true/false)
    """
    # HITL overrides
    if env_val := os.environ.get("HITL_CONFIDENCE_THRESHOLD"):
        try:
            hitl.confidence_threshold = float(env_val)
        except ValueError:
            pass

    if env_val := os.environ.get("HITL_AMOUNT_THRESHOLD"):
        try:
            hitl.amount_threshold = float(env_val)
        except ValueError:
            pass

    # Security overrides
    if env_val := os.environ.get("PROMPT_SECURITY_ENABLE_LLM_GUARD"):
        security.enable_llm_guard = env_val.lower() in ("true", "1", "yes")

    if env_val := os.environ.get("PROMPT_SECURITY_MAX_INPUT_LENGTH"):
        try:
            security.max_input_length = int(env_val)
        except ValueError:
            pass

    # Global log override
    if env_val := os.environ.get("GOVERNANCE_LOG_TO_DB"):
        log_enabled = env_val.lower() in ("true", "1", "yes")
        security.log_to_db = log_enabled
        hitl.log_to_db = log_enabled

