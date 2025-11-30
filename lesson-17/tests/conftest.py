"""Pytest configuration and fixtures for lesson-17 tests.

Provides common fixtures for testing explainability components.
"""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path

import pytest

# Add lesson-17 to path for imports
lesson17_path = Path(__file__).parent.parent
if str(lesson17_path) not in sys.path:
    sys.path.insert(0, str(lesson17_path))


@pytest.fixture
def temp_dir() -> Path:
    """Create a temporary directory for test data."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def sample_workflow_id() -> str:
    """Provide a sample workflow ID."""
    return "test-workflow-001"

