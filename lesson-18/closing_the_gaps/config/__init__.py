"""Configuration module for Closing the Gaps framework.

This module provides configuration loading and management for:
    - PromptSecurityGuard settings
    - HITLController settings
    - Database connection settings
    - Observability settings

Configuration can be loaded from:
    - YAML files (security.yaml)
    - JSON files (injection_patterns.json)
    - Environment variables (for overrides)

Example:
    >>> from closing_the_gaps.config import load_config, get_security_config
    >>> config = load_config()
    >>> security_config = get_security_config(config)
"""

from .loader import (
    GovernanceConfig,
    HITLConfig,
    PromptSecurityConfig,
    get_config_path,
    get_hitl_config,
    get_security_config,
    load_config,
)

__all__ = [
    "load_config",
    "get_config_path",
    "get_security_config",
    "get_hitl_config",
    "GovernanceConfig",
    "PromptSecurityConfig",
    "HITLConfig",
]

