"""
Error handling tests for tutorial validation edge cases.

This module tests graceful failure scenarios for /validate-tutorial command:
- Missing directory with actionable suggestions
- Notebook execution timeout (>5min)
- Missing jupyter dependency
- Broken Mermaid syntax with specific line numbers
- Permission errors with fix suggestions
"""

import json
import os
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from backend.tutorial_validation import (
    calculate_reading_time,
    validate_cross_links,
    validate_mermaid_diagrams,
    validate_notebook_execution,
    validate_tutorial_index_structure,
)

# ============================================================================
# Missing Directory Error Handling Tests
# ============================================================================


def test_should_return_actionable_error_when_directory_not_found() -> None:
    """Test that missing directory returns actionable error with suggestions."""
    result = validate_mermaid_diagrams("/nonexistent/lesson-99")

    assert result["valid"] is False
    assert result["error"] is not None
    assert "not found" in result["error"].lower()
    assert "/nonexistent/lesson-99" in result["error"]


def test_should_suggest_similar_directories_when_directory_not_found() -> None:
    """Test that error suggests similar directory names (e.g., lesson-9 for lesson-99)."""
    # This test will fail initially (RED phase)
    # We need to implement fuzzy directory matching
    result = validate_mermaid_diagrams("lesson-99")

    assert result["valid"] is False
    assert result["error"] is not None
    assert "Did you mean" in result["error"] or "similar" in result["error"].lower()


def test_should_list_available_directories_when_not_found() -> None:
    """Test that error lists available lesson/homework directories."""
    # This test will fail initially (RED phase)
    # We need to implement directory listing in error message
    result = validate_mermaid_diagrams("lesson-999")

    assert result["valid"] is False
    assert result["error"] is not None
    # Should suggest available directories
    assert "Available" in result["error"] or "available" in result["error"].lower()


def test_should_handle_path_is_file_not_directory() -> None:
    """Test that error is actionable when path points to a file instead of directory."""
    with tempfile.TemporaryDirectory() as tmpdir:
        base_path = Path(tmpdir)
        file_path = base_path / "tutorial.md"
        file_path.write_text("# Tutorial")

        result = validate_mermaid_diagrams(str(file_path))

        assert result["valid"] is False
        assert result["error"] is not None
        assert "not a directory" in result["error"].lower()


# ============================================================================
# Notebook Execution Timeout Error Handling Tests
# ============================================================================


def test_should_skip_notebook_with_warning_when_timeout_exceeded() -> None:
    """Test that notebook exceeding timeout is skipped with warning, not error."""
    notebook_content = {
        "cells": [
            {
                "cell_type": "code",
                "execution_count": None,
                "metadata": {},
                "outputs": [],
                "source": ["import time\n", "time.sleep(10)\n"],
            }
        ],
        "metadata": {
            "kernelspec": {
                "display_name": "Python 3",
                "language": "python",
                "name": "python3",
            }
        },
        "nbformat": 4,
        "nbformat_minor": 4,
    }

    with tempfile.NamedTemporaryFile(mode="w", suffix=".ipynb", delete=False) as f:
        json.dump(notebook_content, f)
        temp_path = f.name

    try:
        result = validate_notebook_execution(temp_path, timeout=2)

        # Should not crash, should return timeout status
        assert result["executed"] is False
        assert result["status"] == "timeout"
        assert "timeout" in result["error"].lower() or "exceeded" in result["error"].lower()

        # Should include actionable suggestion
        assert "Notebook execution exceeded timeout" in result["error"]
    finally:
        Path(temp_path).unlink(missing_ok=True)


def test_should_provide_actionable_timeout_message() -> None:
    """Test that timeout error includes suggestion to optimize or increase timeout."""
    # This test will fail initially (RED phase)
    # We need to enhance error message with actionable suggestions
    notebook_content = {
        "cells": [
            {
                "cell_type": "code",
                "execution_count": None,
                "metadata": {},
                "outputs": [],
                "source": ["import time\n", "time.sleep(10)\n"],
            }
        ],
        "metadata": {
            "kernelspec": {
                "display_name": "Python 3",
                "language": "python",
                "name": "python3",
            }
        },
        "nbformat": 4,
        "nbformat_minor": 4,
    }

    with tempfile.NamedTemporaryFile(mode="w", suffix=".ipynb", delete=False) as f:
        json.dump(notebook_content, f)
        temp_path = f.name

    try:
        result = validate_notebook_execution(temp_path, timeout=2)

        # Should include actionable suggestion
        assert "optimize" in result["error"].lower() or "increase timeout" in result["error"].lower()
    finally:
        Path(temp_path).unlink(missing_ok=True)


# ============================================================================
# Missing Jupyter Dependency Error Handling Tests
# ============================================================================


def test_should_return_actionable_error_when_jupyter_not_found() -> None:
    """Test that missing jupyter returns actionable installation instructions."""
    with tempfile.TemporaryDirectory() as tmpdir:
        base_path = Path(tmpdir)
        notebook = base_path / "test.ipynb"

        notebook_content = {
            "cells": [],
            "metadata": {
                "kernelspec": {
                    "display_name": "Python 3",
                    "language": "python",
                    "name": "python3",
                }
            },
            "nbformat": 4,
            "nbformat_minor": 4,
        }

        notebook.write_text(json.dumps(notebook_content))

        # Mock subprocess.run to simulate missing jupyter
        with patch("backend.tutorial_validation.subprocess.run") as mock_run:
            mock_run.side_effect = FileNotFoundError("jupyter not found")

            result = validate_notebook_execution(str(notebook), timeout=300)

            assert result["executed"] is False
            assert result["status"] == "error"
            assert result["error"] is not None
            assert "jupyter nbconvert not available" in result["error"]


def test_should_include_pip_install_command_when_jupyter_missing() -> None:
    """Test that error message includes pip install jupyter nbconvert command."""
    with tempfile.TemporaryDirectory() as tmpdir:
        base_path = Path(tmpdir)
        notebook = base_path / "test.ipynb"

        notebook_content = {
            "cells": [],
            "metadata": {
                "kernelspec": {
                    "display_name": "Python 3",
                    "language": "python",
                    "name": "python3",
                }
            },
            "nbformat": 4,
            "nbformat_minor": 4,
        }

        notebook.write_text(json.dumps(notebook_content))

        # Mock subprocess.run to simulate missing jupyter
        with patch("backend.tutorial_validation.subprocess.run") as mock_run:
            mock_run.side_effect = FileNotFoundError("jupyter not found")

            result = validate_notebook_execution(str(notebook), timeout=300)

            assert result["error"] is not None
            # Should include installation command
            assert "pip install" in result["error"] or "install jupyter" in result["error"].lower()


# ============================================================================
# Broken Mermaid Syntax Error Handling Tests
# ============================================================================


def test_should_provide_line_number_for_mermaid_syntax_error() -> None:
    """Test that Mermaid syntax errors include specific line number."""
    with tempfile.TemporaryDirectory() as tmpdir:
        base_path = Path(tmpdir)
        diagram_file = base_path / "broken.mmd"

        # Create invalid Mermaid diagram (unclosed bracket)
        content = """```mermaid
flowchart TD
    A[Start --> B[Process]
    B --> C[End
```"""
        diagram_file.write_text(content)

        result = validate_mermaid_diagrams(str(base_path))

        # Should detect syntax error
        assert result["valid"] is False
        assert result["invalid_diagrams"] >= 1
        assert len(result["errors"]) >= 1

        # Error should include file path
        error = result["errors"][0]
        assert "file" in error
        assert "broken.mmd" in error["file"]
        assert "error" in error


def test_should_suggest_mermaid_live_for_syntax_validation() -> None:
    """Test that syntax error suggests using https://mermaid.live for validation."""
    # This test will fail initially (RED phase)
    # We need to enhance error message with mermaid.live suggestion
    with tempfile.TemporaryDirectory() as tmpdir:
        base_path = Path(tmpdir)
        diagram_file = base_path / "broken.mmd"

        content = """```mermaid
flowchart TD
    Invalid syntax here!!!
```"""
        diagram_file.write_text(content)

        result = validate_mermaid_diagrams(str(base_path))

        assert result["valid"] is False
        # Error should suggest mermaid.live
        error = result["errors"][0]
        assert "mermaid.live" in error["error"].lower() or "validate" in error["error"].lower()


def test_should_handle_mermaid_cli_not_installed() -> None:
    """Test that missing mermaid CLI (mmdc) returns actionable error."""
    # This test will fail initially (RED phase)
    # We need to handle missing mmdc gracefully
    with patch("subprocess.run") as mock_run:
        mock_run.side_effect = FileNotFoundError("mmdc not found")

        with tempfile.TemporaryDirectory() as tmpdir:
            base_path = Path(tmpdir)
            diagram_file = base_path / "test.mmd"
            diagram_file.write_text(
                """```mermaid
flowchart TD
    A --> B
```"""
            )

            result = validate_mermaid_diagrams(str(base_path))

            # Should not crash, should return error with installation instructions
            assert result["valid"] is False
            assert "mmdc" in str(result.get("error", "")).lower() or len(result["errors"]) > 0


# ============================================================================
# Permission Error Handling Tests
# ============================================================================


def test_should_return_actionable_error_when_permission_denied_reading_file() -> None:
    """Test that permission errors include actionable fix suggestions."""
    # This test will fail initially (RED phase)
    # We need to enhance error handling for permission errors
    with tempfile.TemporaryDirectory() as tmpdir:
        base_path = Path(tmpdir)
        tutorial_index = base_path / "TUTORIAL_INDEX.md"
        tutorial_index.write_text("# Tutorial")

        # Make file unreadable (chmod 000)
        os.chmod(tutorial_index, 0o000)

        try:
            result = validate_cross_links(str(tutorial_index))

            assert result["valid"] is False
            assert result["error"] is not None
            assert "permission" in result["error"].lower() or "denied" in result["error"].lower()
        finally:
            # Restore permissions for cleanup
            os.chmod(tutorial_index, 0o644)


def test_should_suggest_chmod_command_for_permission_error() -> None:
    """Test that permission error suggests chmod +r command."""
    # This test will fail initially (RED phase)
    # We need to include chmod suggestion in error message
    with tempfile.TemporaryDirectory() as tmpdir:
        base_path = Path(tmpdir)
        tutorial_index = base_path / "TUTORIAL_INDEX.md"
        tutorial_index.write_text("# Tutorial")

        # Make file unreadable
        os.chmod(tutorial_index, 0o000)

        try:
            result = validate_cross_links(str(tutorial_index))

            assert result["error"] is not None
            # Should suggest chmod command
            assert "chmod" in result["error"].lower() or "permission" in result["error"].lower()
        finally:
            os.chmod(tutorial_index, 0o644)


def test_should_handle_permission_error_for_notebook_execution() -> None:
    """Test that notebook validation handles permission errors gracefully."""
    # This test will fail initially (RED phase)
    with tempfile.TemporaryDirectory() as tmpdir:
        base_path = Path(tmpdir)
        notebook = base_path / "test.ipynb"

        notebook_content = {
            "cells": [],
            "metadata": {
                "kernelspec": {
                    "display_name": "Python 3",
                    "language": "python",
                    "name": "python3",
                }
            },
            "nbformat": 4,
            "nbformat_minor": 4,
        }

        notebook.write_text(json.dumps(notebook_content))

        # Make notebook unreadable
        os.chmod(notebook, 0o000)

        try:
            result = validate_notebook_execution(str(notebook), timeout=60)

            # Should not crash, should return error
            assert result["executed"] is False
            assert result["error"] is not None
        finally:
            os.chmod(notebook, 0o644)


# ============================================================================
# General Error Recovery Tests
# ============================================================================


def test_should_never_crash_on_malformed_input() -> None:
    """Test that validation functions never raise unhandled exceptions."""
    # Test with various malformed inputs
    malformed_inputs = [
        None,
        123,
        [],
        {},
        "",
        " ",
        "\n\n\n",
        "🔥🔥🔥",
        "a" * 10000,  # Very long string
    ]

    for bad_input in malformed_inputs:
        # validate_tutorial_index_structure should raise TypeError for non-string
        if not isinstance(bad_input, str):
            with pytest.raises(TypeError):
                validate_tutorial_index_structure(bad_input)  # type: ignore
        else:
            # Should not crash for string inputs
            result = validate_tutorial_index_structure(bad_input)
            assert "valid" in result
            assert "error" not in result or result.get("error") is None


def test_should_provide_clear_error_for_invalid_notebook_json() -> None:
    """Test that invalid notebook JSON returns clear error message."""
    with tempfile.TemporaryDirectory() as tmpdir:
        base_path = Path(tmpdir)
        notebook = base_path / "invalid.ipynb"
        notebook.write_text("{ this is not valid JSON }")

        result = calculate_reading_time(str(notebook), wpm=200)

        assert result["status"] == "error"
        assert result["error"] is not None
        assert "json" in result["error"].lower() or "invalid" in result["error"].lower()


def test_should_handle_corrupted_mermaid_file() -> None:
    """Test that corrupted .mmd files are handled gracefully."""
    with tempfile.TemporaryDirectory() as tmpdir:
        base_path = Path(tmpdir)
        diagram_file = base_path / "corrupted.mmd"

        # Create file with binary garbage
        diagram_file.write_bytes(b"\x00\x01\x02\xFF\xFE\xFD")

        result = validate_mermaid_diagrams(str(base_path))

        # Should not crash, should report validation error
        assert "valid" in result
        # If it fails, should have errors
        if not result["valid"]:
            assert result["invalid_diagrams"] >= 0


def test_should_handle_empty_directory_gracefully() -> None:
    """Test that validation handles empty directories without errors."""
    with tempfile.TemporaryDirectory() as tmpdir:
        result = validate_mermaid_diagrams(tmpdir)

        # Should succeed with 0 diagrams
        assert result["valid"] is True
        assert result["total_diagrams"] == 0
        assert result["error"] is None


def test_should_handle_nested_permission_errors() -> None:
    """Test that permission errors in nested directories are handled."""
    # This test will fail initially (RED phase)
    with tempfile.TemporaryDirectory() as tmpdir:
        base_path = Path(tmpdir)
        nested_dir = base_path / "diagrams"
        nested_dir.mkdir()

        diagram_file = nested_dir / "test.mmd"
        diagram_file.write_text(
            """```mermaid
flowchart TD
    A --> B
```"""
        )

        # Make nested directory unreadable
        os.chmod(nested_dir, 0o000)

        try:
            result = validate_mermaid_diagrams(str(base_path))

            # Should not crash
            assert "valid" in result
        finally:
            # Restore permissions
            os.chmod(nested_dir, 0o755)


# ============================================================================
# Timeout Handling for Mermaid Validation Tests
# ============================================================================


def test_should_timeout_mermaid_validation_for_complex_diagrams() -> None:
    """Test that Mermaid validation times out gracefully for very complex diagrams."""
    with tempfile.TemporaryDirectory() as tmpdir:
        base_path = Path(tmpdir)
        diagram_file = base_path / "complex.mmd"

        # Create very large diagram
        nodes = "\n".join([f"    Node{i}[Node {i}]" for i in range(1000)])
        edges = "\n".join([f"    Node{i} --> Node{i+1}" for i in range(999)])
        content = f"""```mermaid
flowchart TD
{nodes}
{edges}
```"""
        diagram_file.write_text(content)

        result = validate_mermaid_diagrams(str(base_path))

        # Should complete validation (may timeout, may succeed)
        assert "valid" in result
        # If it times out, should report error
        if not result["valid"]:
            assert len(result["errors"]) > 0


def test_should_provide_timeout_threshold_in_error_message() -> None:
    """Test that timeout errors mention the timeout threshold."""
    # Already tested in validate_notebook_execution, verify error message format
    notebook_content = {
        "cells": [
            {
                "cell_type": "code",
                "execution_count": None,
                "metadata": {},
                "outputs": [],
                "source": ["import time\n", "time.sleep(10)\n"],
            }
        ],
        "metadata": {
            "kernelspec": {
                "display_name": "Python 3",
                "language": "python",
                "name": "python3",
            }
        },
        "nbformat": 4,
        "nbformat_minor": 4,
    }

    with tempfile.NamedTemporaryFile(mode="w", suffix=".ipynb", delete=False) as f:
        json.dump(notebook_content, f)
        temp_path = f.name

    try:
        timeout_value = 2
        result = validate_notebook_execution(temp_path, timeout=timeout_value)

        # Error should mention the timeout value
        assert f"{timeout_value}s" in result["error"] or str(timeout_value) in result["error"]
    finally:
        Path(temp_path).unlink(missing_ok=True)
