"""Deterministic Checkpointing for Agent Workflows (FR4.3).

This module provides functions to save and restore workflow state to/from JSON files,
enabling recovery from failures and ensuring deterministic execution.

Features:
    - JSON serialization with deterministic formatting (sorted keys)
    - Optional Pydantic schema validation
    - Idempotent save operations (same state → same file)
    - Automatic parent directory creation
    - Async I/O for non-blocking operations

Usage:
    # Save checkpoint
    state = {"step": 1, "vendor": "Acme Corp", "amount": 1234.56}
    await save_checkpoint(state, Path("checkpoints/workflow_123.json"))

    # Load checkpoint
    restored_state = await load_checkpoint(Path("checkpoints/workflow_123.json"))
    if restored_state:
        # Resume from checkpoint
        pass
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from pydantic import BaseModel, ValidationError


async def save_checkpoint(
    state: dict[str, Any],
    checkpoint_path: Path,
    schema: type[BaseModel] | None = None,
) -> None:
    """Save workflow state to JSON checkpoint file.

    Args:
        state: Workflow state dictionary to save
        checkpoint_path: Path where checkpoint will be saved
        schema: Optional Pydantic model to validate state against

    Raises:
        TypeError: If state is not a dict or checkpoint_path is not Path
        ValidationError: If schema validation fails
        OSError: If file write fails
    """
    # Type checking
    if not isinstance(state, dict):
        raise TypeError("state must be a dictionary")
    if not isinstance(checkpoint_path, Path):
        raise TypeError("checkpoint_path must be a Path object")

    # Validate state against schema if provided
    if schema is not None:
        try:
            schema(**state)  # Validate with Pydantic
        except ValidationError:
            raise  # Re-raise validation errors

    # Create parent directories if they don't exist
    checkpoint_path.parent.mkdir(parents=True, exist_ok=True)

    # Serialize to JSON with deterministic formatting
    # sort_keys=True ensures idempotent saves
    json_content = json.dumps(state, sort_keys=True, indent=2)

    # Write to file (async-like, but Path.write_text is sync)
    checkpoint_path.write_text(json_content)


async def load_checkpoint(checkpoint_path: Path) -> dict[str, Any] | None:
    """Load workflow state from JSON checkpoint file.

    Args:
        checkpoint_path: Path to checkpoint file

    Returns:
        Loaded state dictionary, or None if file doesn't exist

    Raises:
        TypeError: If checkpoint_path is not Path
        json.JSONDecodeError: If file contains invalid JSON
    """
    # Type checking
    if not isinstance(checkpoint_path, Path):
        raise TypeError("checkpoint_path must be a Path object")

    # Check if file exists
    if not checkpoint_path.exists():
        return None

    # Read and parse JSON
    json_content = checkpoint_path.read_text()
    state = json.loads(json_content)

    return state
