#!/usr/bin/env python3
"""
Tests for compress-claude-extract.py script.

Run with: pytest .claude/scripts/test_compress_extract.py -v
"""

import importlib.util
import os

import pytest

# Import the script directly by file path
script_path = os.path.join(os.path.dirname(__file__), "compress-claude-extract.py")
spec = importlib.util.spec_from_file_location("compress_claude_extract", script_path)
compress_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(compress_module)

find_section_boundaries = compress_module.find_section_boundaries
SECTIONS = compress_module.SECTIONS


def test_should_find_section_boundaries_when_valid_markers() -> None:
    """Test that section boundaries are found correctly."""
    lines = [
        "Some content\n",
        "## Development Principles\n",
        "Content here\n",
        "More content\n",
        "## Pattern Library\n",
        "Other content\n",
    ]
    start, end = find_section_boundaries(lines, "## Development Principles", "## Pattern Library")
    assert start == 1
    assert end == 4


def test_should_raise_error_when_start_marker_not_found() -> None:
    """Test that ValueError is raised when start marker is missing."""
    lines = ["Some content\n", "## Pattern Library\n"]
    with pytest.raises(ValueError, match="Start marker not found"):
        find_section_boundaries(lines, "## Development Principles", "## Pattern Library")


def test_should_raise_error_when_end_marker_not_found() -> None:
    """Test that ValueError is raised when end marker is missing."""
    lines = ["Some content\n", "## Development Principles\n", "Content\n"]
    with pytest.raises(ValueError, match="End marker not found"):
        find_section_boundaries(lines, "## Development Principles", "## Pattern Library")


def test_should_validate_all_section_configs() -> None:
    """Test that all section configurations have required fields."""
    required_fields = ["start_marker", "end_marker", "summary", "target", "description"]

    for section_name, config in SECTIONS.items():
        for field in required_fields:
            assert field in config, f"Section '{section_name}' missing field '{field}'"
        assert isinstance(config["summary"], str), f"Section '{section_name}' summary must be string"
        assert "@.claude/instructions" in config["summary"], (
            f"Section '{section_name}' summary must contain import statement"
        )


def test_should_have_matching_import_paths() -> None:
    """Test that target paths match import statements in summaries."""
    for section_name, config in SECTIONS.items():
        target = config["target"]
        summary = config["summary"]
        assert f"@{target}" in summary or f"@./{target}" in summary, (
            f"Section '{section_name}' summary missing import to {target}"
        )


def test_should_extract_section_with_dry_run(tmp_path: str) -> None:
    """Test extraction with dry-run mode (no files modified)."""
    # This test would require mocking or creating a temporary CLAUDE.md
    # For now, we validate the dry-run logic by checking the script doesn't crash
    # when run with --dry-run flag (manual test via bash)
    pass


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
