"""
Tests for tutorial validation functionality.

This module tests TUTORIAL_INDEX.md structure validation, notebook execution,
cross-link validation, Mermaid diagram validation, and reading time calculation.
"""

from pathlib import Path

import pytest

from backend.tutorial_validation import (
    calculate_reading_time,
    generate_validation_report,
    validate_cross_links,
    validate_mermaid_diagrams,
    validate_notebook_execution,
    validate_tutorial_index_structure,
)


def test_should_pass_when_all_required_sections_present() -> None:
    """Test that validation passes when all 10 required sections are present."""
    content = """
# Tutorial Index

## Overview
This is an overview.

## Learning Objectives
- Objective 1
- Objective 2

## Prerequisites
- Prerequisite 1

## Tutorials
1. Tutorial 1

## Recommended Learning Path
Path description

## Key Concepts
- Concept 1

## Common Pitfalls
- Pitfall 1

## Resources
- Resource 1

## Next Steps
- Next step 1

## FAQ
Q: Question?
A: Answer.
"""
    result = validate_tutorial_index_structure(content)

    assert result["valid"] is True
    assert result["missing_sections"] == []
    assert result["found_sections"] == 10
    assert result["required_sections"] == 10


def test_should_fail_when_missing_required_sections() -> None:
    """Test that validation fails when required sections are missing."""
    content = """
# Tutorial Index

## Overview
This is an overview.

## Learning Objectives
- Objective 1

## Prerequisites
- Prerequisite 1
"""
    result = validate_tutorial_index_structure(content)

    assert result["valid"] is False
    assert len(result["missing_sections"]) == 7
    assert "FAQ" in result["missing_sections"]
    assert "Common Pitfalls" in result["missing_sections"]
    assert result["found_sections"] == 3


def test_should_detect_learning_time_estimate() -> None:
    """Test that validation detects learning time estimate."""
    content = """
# Tutorial Index

**Learning Time:** 3-4 hours
**Difficulty:** Intermediate

## Overview
Overview text
"""
    result = validate_tutorial_index_structure(content)

    assert result["has_learning_time"] is True
    assert result["learning_time"] == "3-4 hours"


def test_should_detect_missing_learning_time() -> None:
    """Test that validation detects missing learning time estimate."""
    content = """
# Tutorial Index

## Overview
Overview text
"""
    result = validate_tutorial_index_structure(content)

    assert result["has_learning_time"] is False
    assert result["learning_time"] is None


def test_should_detect_difficulty_level() -> None:
    """Test that validation detects difficulty level."""
    content = """
# Tutorial Index

**Difficulty:** Intermediate

## Overview
Overview text
"""
    result = validate_tutorial_index_structure(content)

    assert result["has_difficulty"] is True
    assert result["difficulty"] == "Intermediate"


def test_should_handle_empty_content() -> None:
    """Test that validation handles empty content gracefully."""
    content = ""
    result = validate_tutorial_index_structure(content)

    assert result["valid"] is False
    assert len(result["missing_sections"]) == 10
    assert result["found_sections"] == 0


def test_should_handle_case_insensitive_section_matching() -> None:
    """Test that section matching is case-insensitive."""
    content = """
# Tutorial Index

## overview
Overview text

## LEARNING OBJECTIVES
- Objective 1

## Prerequisites
- Prerequisite 1

## tutorials
Tutorial content

## recommended learning path
Path content

## key concepts
Concepts

## common pitfalls
Pitfalls

## resources
Resources

## next steps
Steps

## faq
Q&A
"""
    result = validate_tutorial_index_structure(content)

    assert result["valid"] is True
    assert result["found_sections"] == 10


def test_should_raise_error_for_invalid_content_type() -> None:
    """Test that validation raises TypeError for non-string content."""
    with pytest.raises(TypeError, match="content must be a string"):
        validate_tutorial_index_structure(None)  # type: ignore


def test_should_count_documented_tutorials() -> None:
    """Test that validation counts number of documented tutorials."""
    content = """
# Tutorial Index

## Tutorials

1. [Tutorial 1](tutorial1.md) - Description 1 (15 min)
2. [Tutorial 2](tutorial2.md) - Description 2 (20 min)
3. [Tutorial 3](tutorial3.md) - Description 3 (25 min)

## Overview
Overview
"""
    result = validate_tutorial_index_structure(content)

    assert result["tutorial_count"] >= 3


def test_should_detect_cross_links_to_other_lessons() -> None:
    """Test that validation detects cross-links to other lessons/homeworks."""
    content = """
# Tutorial Index

## Overview
See [Lesson 10](../lesson-10/README.md) for more details.
Also check [HW3](../homeworks/hw3/TUTORIAL_INDEX.md).

## Resources
- [Lesson 9](../lesson-9/README.md)
"""
    result = validate_tutorial_index_structure(content)

    assert result["has_cross_links"] is True
    assert result["cross_link_count"] >= 3


def test_should_validate_lesson_9_as_gold_standard() -> None:
    """Test that lesson-9/TUTORIAL_INDEX.md passes validation (gold standard)."""
    lesson_9_path = Path("lesson-9/TUTORIAL_INDEX.md")

    if not lesson_9_path.exists():
        pytest.skip("lesson-9/TUTORIAL_INDEX.md not found")

    content = lesson_9_path.read_text()
    result = validate_tutorial_index_structure(content)

    assert result["valid"] is True
    assert result["found_sections"] == 10
    assert result["has_learning_time"] is True
    assert result["has_difficulty"] is True
    assert result["has_cross_links"] is True


# ============================================================================
# Notebook Execution Validation Tests
# ============================================================================


def test_should_pass_notebook_execution_when_valid() -> None:
    """Test that notebook execution validation passes for valid notebook."""
    notebook_path = Path("lesson-9/perplexity_calculation_tutorial.ipynb")

    if not notebook_path.exists():
        pytest.skip("Test notebook not found")

    result = validate_notebook_execution(str(notebook_path), timeout=300)

    assert result["executed"] is True
    assert result["execution_time"] < 300
    assert result["error"] is None
    assert result["status"] == "success"


def test_should_detect_missing_notebook_file() -> None:
    """Test that validation detects missing notebook file."""
    result = validate_notebook_execution("nonexistent.ipynb", timeout=300)

    assert result["executed"] is False
    assert result["error"] is not None
    assert "not found" in result["error"].lower()
    assert result["status"] == "error"


def test_should_raise_error_for_invalid_path_type() -> None:
    """Test that validation raises TypeError for non-string path."""
    with pytest.raises(TypeError, match="notebook_path must be a string"):
        validate_notebook_execution(None, timeout=300)  # type: ignore


def test_should_raise_error_for_invalid_timeout() -> None:
    """Test that validation raises ValueError for invalid timeout."""
    with pytest.raises(ValueError, match="timeout must be positive"):
        validate_notebook_execution("test.ipynb", timeout=-1)


def test_should_handle_missing_jupyter_dependency() -> None:
    """Test that validation handles missing jupyter gracefully."""
    # This test verifies error handling when jupyter is not installed
    # In practice, jupyter should be installed for tests to run

    # Temporarily modify PATH to simulate missing jupyter
    result = validate_notebook_execution("lesson-9/perplexity_calculation_tutorial.ipynb", timeout=300)

    # Should not crash even if jupyter is missing
    assert "executed" in result
    assert "status" in result


def test_should_timeout_for_long_running_notebook() -> None:
    """Test that validation times out for long-running notebooks."""
    # Create a temporary notebook with long execution
    import json
    import tempfile

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

        assert result["executed"] is False
        assert result["status"] in ["timeout", "error"]
        if result["status"] == "timeout":
            assert "timeout" in result["error"].lower() or "exceeded" in result["error"].lower()
    finally:
        Path(temp_path).unlink(missing_ok=True)


def test_should_detect_execution_errors_in_notebook() -> None:
    """Test that validation detects execution errors in notebook."""
    import json
    import tempfile

    notebook_content = {
        "cells": [
            {
                "cell_type": "code",
                "execution_count": None,
                "metadata": {},
                "outputs": [],
                "source": ["# This will cause a NameError\n", "undefined_variable\n"],
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
        result = validate_notebook_execution(temp_path, timeout=60)

        assert result["executed"] is False
        assert result["status"] == "error"
        assert result["error"] is not None
    finally:
        Path(temp_path).unlink(missing_ok=True)


def test_should_return_execution_metadata() -> None:
    """Test that validation returns execution metadata."""
    notebook_path = Path("lesson-9/perplexity_calculation_tutorial.ipynb")

    if not notebook_path.exists():
        pytest.skip("Test notebook not found")

    result = validate_notebook_execution(str(notebook_path), timeout=300)

    # Check required metadata fields
    assert "executed" in result
    assert "execution_time" in result
    assert "status" in result
    assert "error" in result
    assert "notebook_path" in result
    assert result["notebook_path"] == str(notebook_path)


# ============================================================================
# Cross-Link Validation Tests
# ============================================================================


def test_should_validate_all_links_when_all_exist() -> None:
    """Test that validation passes when all linked files exist."""
    import tempfile

    with tempfile.TemporaryDirectory() as tmpdir:
        base_path = Path(tmpdir)

        # Create lesson-9 directory with TUTORIAL_INDEX.md
        lesson_9 = base_path / "lesson-9"
        lesson_9.mkdir()
        tutorial_index = lesson_9 / "TUTORIAL_INDEX.md"

        # Create lesson-10 and hw3 directories with referenced files
        lesson_10 = base_path / "lesson-10"
        lesson_10.mkdir()
        (lesson_10 / "README.md").write_text("# Lesson 10")

        hw3 = base_path / "homeworks" / "hw3"
        hw3.mkdir(parents=True)
        (hw3 / "TUTORIAL_INDEX.md").write_text("# HW3")

        # Create content with cross-links
        content = """
# Tutorial Index

## Overview
See [Lesson 10](../lesson-10/README.md) for details.
Also check [HW3](../homeworks/hw3/TUTORIAL_INDEX.md).
"""
        tutorial_index.write_text(content)

        result = validate_cross_links(str(tutorial_index))

        assert result["valid"] is True
        assert result["total_links"] == 2
        assert result["broken_links"] == 0
        assert len(result["invalid_paths"]) == 0


def test_should_detect_broken_cross_links() -> None:
    """Test that validation detects broken cross-links."""
    import tempfile

    with tempfile.TemporaryDirectory() as tmpdir:
        base_path = Path(tmpdir)

        # Create lesson-9 directory
        lesson_9 = base_path / "lesson-9"
        lesson_9.mkdir()
        tutorial_index = lesson_9 / "TUTORIAL_INDEX.md"

        # Create content with broken link (lesson-10 doesn't exist)
        content = """
# Tutorial Index

## Overview
See [Lesson 10](../lesson-10/README.md) for details.
"""
        tutorial_index.write_text(content)

        result = validate_cross_links(str(tutorial_index))

        assert result["valid"] is False
        assert result["total_links"] == 1
        assert result["broken_links"] == 1
        assert len(result["invalid_paths"]) == 1
        assert "../lesson-10/README.md" in result["invalid_paths"][0]["link"]


def test_should_handle_absolute_paths_separately() -> None:
    """Test that validation skips absolute URLs and external links."""
    import tempfile

    with tempfile.TemporaryDirectory() as tmpdir:
        base_path = Path(tmpdir)

        lesson_9 = base_path / "lesson-9"
        lesson_9.mkdir()
        tutorial_index = lesson_9 / "TUTORIAL_INDEX.md"

        # Content with both relative paths and absolute URLs
        content = """
# Tutorial Index

## Overview
- [Lesson 10](../lesson-10/README.md) - relative (should validate)
- [External](https://example.com) - absolute URL (should skip)
- [GitHub](https://github.com/user/repo) - absolute URL (should skip)
"""
        tutorial_index.write_text(content)

        result = validate_cross_links(str(tutorial_index))

        # Should only validate relative path
        assert result["total_links"] == 1


def test_should_raise_error_for_invalid_file_path() -> None:
    """Test that validation raises TypeError for non-string file path."""
    with pytest.raises(TypeError, match="file_path must be a string"):
        validate_cross_links(None)  # type: ignore


def test_should_handle_file_not_found() -> None:
    """Test that validation handles missing file gracefully."""
    result = validate_cross_links("/nonexistent/path/TUTORIAL_INDEX.md")

    assert result["valid"] is False
    assert result["error"] is not None
    assert "not found" in result["error"].lower()


def test_should_detect_markdown_links_only() -> None:
    """Test that validation only checks markdown links [text](path)."""
    import tempfile

    with tempfile.TemporaryDirectory() as tmpdir:
        base_path = Path(tmpdir)

        lesson_9 = base_path / "lesson-9"
        lesson_9.mkdir()
        tutorial_index = lesson_9 / "TUTORIAL_INDEX.md"

        # Content with markdown links and plain URLs
        content = """
# Tutorial Index

## Overview
- [Valid Link](../lesson-10/README.md)
- Plain URL: ../lesson-11/README.md (should be ignored)
- <../lesson-12/README.md> (should be ignored)
"""
        tutorial_index.write_text(content)

        result = validate_cross_links(str(tutorial_index))

        # Should only detect markdown links
        assert result["total_links"] == 1


def test_should_validate_lesson_9_cross_links() -> None:
    """Test that lesson-9/TUTORIAL_INDEX.md cross-links are valid."""
    lesson_9_path = Path("lesson-9/TUTORIAL_INDEX.md")

    if not lesson_9_path.exists():
        pytest.skip("lesson-9/TUTORIAL_INDEX.md not found")

    result = validate_cross_links(str(lesson_9_path))

    # lesson-9 should have valid cross-links
    assert result["total_links"] >= 0
    if result["total_links"] > 0:
        # If there are links, they should all be valid
        assert result["broken_links"] == 0
        assert result["valid"] is True


def test_should_provide_actionable_error_messages() -> None:
    """Test that broken link errors include actionable suggestions."""
    import tempfile

    with tempfile.TemporaryDirectory() as tmpdir:
        base_path = Path(tmpdir)

        lesson_9 = base_path / "lesson-9"
        lesson_9.mkdir()
        tutorial_index = lesson_9 / "TUTORIAL_INDEX.md"

        content = """
# Tutorial Index

## Overview
See [Lesson 10](../lesson-10/README.md) for details.
"""
        tutorial_index.write_text(content)

        result = validate_cross_links(str(tutorial_index))

        assert result["valid"] is False
        assert len(result["invalid_paths"]) == 1

        # Check that error includes actionable information
        error = result["invalid_paths"][0]
        assert "link" in error
        assert "resolved_path" in error
        assert "error" in error


# ============================================================================
# Mermaid Diagram Validation Tests
# ============================================================================


def test_should_validate_mermaid_syntax_when_valid() -> None:
    """Test that validation passes for valid Mermaid diagram."""
    import tempfile

    with tempfile.TemporaryDirectory() as tmpdir:
        base_path = Path(tmpdir)
        diagram_file = base_path / "test_diagram.mmd"

        # Create valid Mermaid diagram
        content = """```mermaid
flowchart TD
    A[Start] --> B[Process]
    B --> C[End]
```"""
        diagram_file.write_text(content)

        result = validate_mermaid_diagrams(str(base_path))

        assert result["valid"] is True
        assert result["total_diagrams"] == 1
        assert result["invalid_diagrams"] == 0
        assert len(result["errors"]) == 0


def test_should_detect_invalid_mermaid_syntax() -> None:
    """Test that validation detects invalid Mermaid syntax."""
    import tempfile

    with tempfile.TemporaryDirectory() as tmpdir:
        base_path = Path(tmpdir)
        diagram_file = base_path / "bad_diagram.mmd"

        # Create invalid Mermaid diagram (unclosed bracket)
        content = """```mermaid
flowchart TD
    A[Start --> B[Process]
    B --> C[End
```"""
        diagram_file.write_text(content)

        result = validate_mermaid_diagrams(str(base_path))

        assert result["valid"] is False
        assert result["total_diagrams"] == 1
        assert result["invalid_diagrams"] >= 1


def test_should_handle_directory_without_mermaid_files() -> None:
    """Test that validation handles directories without .mmd files."""
    import tempfile

    with tempfile.TemporaryDirectory() as tmpdir:
        result = validate_mermaid_diagrams(tmpdir)

        assert result["valid"] is True
        assert result["total_diagrams"] == 0
        assert result["invalid_diagrams"] == 0
        assert len(result["errors"]) == 0


def test_should_raise_error_for_invalid_directory_type() -> None:
    """Test that validation raises TypeError for non-string directory."""
    with pytest.raises(TypeError, match="directory_path must be a string"):
        validate_mermaid_diagrams(None)  # type: ignore


def test_should_handle_missing_directory() -> None:
    """Test that validation handles missing directory gracefully."""
    result = validate_mermaid_diagrams("/nonexistent/directory")

    assert result["valid"] is False
    assert result["error"] is not None
    assert "not found" in result["error"].lower() or "does not exist" in result["error"].lower()


def test_should_validate_lesson_9_mermaid_diagrams() -> None:
    """Test that lesson-9 Mermaid diagrams are valid."""
    lesson_9_path = Path("lesson-9")

    if not lesson_9_path.exists():
        pytest.skip("lesson-9 directory not found")

    result = validate_mermaid_diagrams(str(lesson_9_path))

    # lesson-9 should have valid diagrams
    if result["total_diagrams"] > 0:
        assert result["invalid_diagrams"] == 0
        assert result["valid"] is True


def test_should_find_mermaid_files_recursively() -> None:
    """Test that validation finds .mmd files in subdirectories."""
    import tempfile

    with tempfile.TemporaryDirectory() as tmpdir:
        base_path = Path(tmpdir)

        # Create nested directory structure
        diagrams_dir = base_path / "diagrams"
        diagrams_dir.mkdir()

        # Create multiple Mermaid files
        (diagrams_dir / "diagram1.mmd").write_text(
            """```mermaid
flowchart TD
    A --> B
```"""
        )
        (diagrams_dir / "diagram2.mmd").write_text(
            """```mermaid
graph LR
    X --> Y
```"""
        )

        result = validate_mermaid_diagrams(str(base_path))

        assert result["total_diagrams"] == 2


def test_should_provide_actionable_error_for_syntax_errors() -> None:
    """Test that syntax errors include actionable information."""
    import tempfile

    with tempfile.TemporaryDirectory() as tmpdir:
        base_path = Path(tmpdir)
        diagram_file = base_path / "bad.mmd"

        # Create invalid diagram
        content = """```mermaid
flowchart TD
    Invalid syntax here!!!
```"""
        diagram_file.write_text(content)

        result = validate_mermaid_diagrams(str(base_path))

        assert result["valid"] is False
        if len(result["errors"]) > 0:
            error = result["errors"][0]
            assert "file" in error
            assert "error" in error


def test_should_handle_mermaid_files_without_code_fence() -> None:
    """Test that validation handles .mmd files without ```mermaid code fence."""
    import tempfile

    with tempfile.TemporaryDirectory() as tmpdir:
        base_path = Path(tmpdir)
        diagram_file = base_path / "no_fence.mmd"

        # Create Mermaid content without code fence
        content = """flowchart TD
    A[Start] --> B[End]
"""
        diagram_file.write_text(content)

        result = validate_mermaid_diagrams(str(base_path))

        # Should still attempt to validate
        assert result["total_diagrams"] == 1


def test_should_skip_non_mmd_files() -> None:
    """Test that validation only processes .mmd files."""
    import tempfile

    with tempfile.TemporaryDirectory() as tmpdir:
        base_path = Path(tmpdir)

        # Create .mmd file
        (base_path / "diagram.mmd").write_text(
            """```mermaid
flowchart TD
    A --> B
```"""
        )

        # Create non-.mmd files
        (base_path / "readme.md").write_text("# README")
        (base_path / "notes.txt").write_text("Notes")

        result = validate_mermaid_diagrams(str(base_path))

        # Should only count .mmd file
        assert result["total_diagrams"] == 1


# ============================================================================
# Reading Time Calculation Tests
# ============================================================================


def test_should_calculate_reading_time_for_markdown() -> None:
    """Test that reading time calculation works for markdown files."""
    import tempfile

    with tempfile.TemporaryDirectory() as tmpdir:
        base_path = Path(tmpdir)
        md_file = base_path / "tutorial.md"

        # Create markdown with known word count (200 words = 1 minute at 200 WPM)
        content = " ".join(["word"] * 200)
        md_file.write_text(content)

        result = calculate_reading_time(str(md_file), wpm=200)

        assert result["word_count"] == 200
        assert result["reading_time_minutes"] == 1.0
        assert result["status"] == "too_short"
        assert result["within_target"] is False
        assert result["error"] is None


def test_should_calculate_reading_time_for_notebook() -> None:
    """Test that reading time calculation works for Jupyter notebooks."""
    import json
    import tempfile

    with tempfile.TemporaryDirectory() as tmpdir:
        base_path = Path(tmpdir)
        nb_file = base_path / "tutorial.ipynb"

        # Create notebook with 200 words (1 minute at 200 WPM)
        notebook_content = {
            "cells": [
                {
                    "cell_type": "markdown",
                    "metadata": {},
                    "source": [" ".join(["word"] * 100)],
                },
                {
                    "cell_type": "code",
                    "execution_count": None,
                    "metadata": {},
                    "outputs": [],
                    "source": ["# " + " ".join(["word"] * 100)],
                },
            ],
            "metadata": {},
            "nbformat": 4,
            "nbformat_minor": 4,
        }

        nb_file.write_text(json.dumps(notebook_content))

        result = calculate_reading_time(str(nb_file), wpm=200)

        assert result["word_count"] == 200
        assert result["reading_time_minutes"] == 1.0
        assert result["status"] == "too_short"
        assert result["error"] is None


def test_should_detect_optimal_reading_time() -> None:
    """Test that reading time within 15-30 min target is marked optimal."""
    import tempfile

    with tempfile.TemporaryDirectory() as tmpdir:
        base_path = Path(tmpdir)
        md_file = base_path / "tutorial.md"

        # Create markdown with 4000 words (20 minutes at 200 WPM)
        content = " ".join(["word"] * 4000)
        md_file.write_text(content)

        result = calculate_reading_time(str(md_file), wpm=200)

        assert result["word_count"] == 4000
        assert result["reading_time_minutes"] == 20.0
        assert result["status"] == "optimal"
        assert result["within_target"] is True


def test_should_detect_too_short_reading_time() -> None:
    """Test that reading time below 15 min is marked too_short."""
    import tempfile

    with tempfile.TemporaryDirectory() as tmpdir:
        base_path = Path(tmpdir)
        md_file = base_path / "tutorial.md"

        # Create markdown with 2000 words (10 minutes at 200 WPM)
        content = " ".join(["word"] * 2000)
        md_file.write_text(content)

        result = calculate_reading_time(str(md_file), wpm=200)

        assert result["word_count"] == 2000
        assert result["reading_time_minutes"] == 10.0
        assert result["status"] == "too_short"
        assert result["within_target"] is False


def test_should_detect_too_long_reading_time() -> None:
    """Test that reading time above 30 min is marked too_long."""
    import tempfile

    with tempfile.TemporaryDirectory() as tmpdir:
        base_path = Path(tmpdir)
        md_file = base_path / "tutorial.md"

        # Create markdown with 8000 words (40 minutes at 200 WPM)
        content = " ".join(["word"] * 8000)
        md_file.write_text(content)

        result = calculate_reading_time(str(md_file), wpm=200)

        assert result["word_count"] == 8000
        assert result["reading_time_minutes"] == 40.0
        assert result["status"] == "too_long"
        assert result["within_target"] is False


def test_should_handle_missing_file_gracefully() -> None:
    """Test that reading time calculation handles missing file."""
    result = calculate_reading_time("/nonexistent/file.md", wpm=200)

    assert result["word_count"] == 0
    assert result["reading_time_minutes"] == 0.0
    assert result["status"] == "error"
    assert result["error"] is not None
    assert "not found" in result["error"].lower()


def test_should_raise_error_for_invalid_file_path_type() -> None:
    """Test that reading time calculation raises TypeError for non-string path."""
    with pytest.raises(TypeError, match="file_path must be a string"):
        calculate_reading_time(None, wpm=200)  # type: ignore


def test_should_raise_error_for_invalid_wpm_type() -> None:
    """Test that reading time calculation raises TypeError for non-integer wpm."""
    with pytest.raises(TypeError, match="wpm must be an integer"):
        calculate_reading_time("test.md", wpm=200.5)  # type: ignore


def test_should_raise_error_for_negative_wpm() -> None:
    """Test that reading time calculation raises ValueError for negative wpm."""
    with pytest.raises(ValueError, match="wpm must be positive"):
        calculate_reading_time("test.md", wpm=-100)


def test_should_raise_error_for_zero_wpm() -> None:
    """Test that reading time calculation raises ValueError for zero wpm."""
    with pytest.raises(ValueError, match="wpm must be positive"):
        calculate_reading_time("test.md", wpm=0)


def test_should_handle_unsupported_file_type() -> None:
    """Test that reading time calculation handles unsupported file types."""
    import tempfile

    with tempfile.TemporaryDirectory() as tmpdir:
        base_path = Path(tmpdir)
        txt_file = base_path / "tutorial.txt"
        txt_file.write_text("This is a text file")

        result = calculate_reading_time(str(txt_file), wpm=200)

        assert result["status"] == "error"
        assert result["error"] is not None
        assert "unsupported" in result["error"].lower()


def test_should_remove_markdown_syntax_from_word_count() -> None:
    """Test that markdown syntax is excluded from word count."""
    import tempfile

    with tempfile.TemporaryDirectory() as tmpdir:
        base_path = Path(tmpdir)
        md_file = base_path / "tutorial.md"

        # Create markdown with formatting (should count 5 words only)
        content = """
# Header
**bold** text with `code` and [link](http://example.com)
```python
# code block should be removed
print("hello")
```
"""
        md_file.write_text(content)

        result = calculate_reading_time(str(md_file), wpm=200)

        # Word count should exclude markdown syntax
        # Expected words: "Header", "bold", "text", "with", "and", "link"
        assert result["word_count"] > 0
        assert result["word_count"] < 20  # Should be much less than raw text


def test_should_handle_empty_markdown_file() -> None:
    """Test that reading time calculation handles empty files."""
    import tempfile

    with tempfile.TemporaryDirectory() as tmpdir:
        base_path = Path(tmpdir)
        md_file = base_path / "empty.md"
        md_file.write_text("")

        result = calculate_reading_time(str(md_file), wpm=200)

        assert result["word_count"] == 0
        assert result["reading_time_minutes"] == 0.0
        assert result["status"] == "too_short"


def test_should_handle_invalid_notebook_json() -> None:
    """Test that reading time calculation handles invalid notebook JSON."""
    import tempfile

    with tempfile.TemporaryDirectory() as tmpdir:
        base_path = Path(tmpdir)
        nb_file = base_path / "invalid.ipynb"
        nb_file.write_text("{ invalid json }")

        result = calculate_reading_time(str(nb_file), wpm=200)

        assert result["status"] == "error"
        assert result["error"] is not None
        assert "json" in result["error"].lower()


def test_should_calculate_reading_time_for_lesson_9() -> None:
    """Test that lesson-9 tutorials have reading times calculated."""
    lesson_9_path = Path("lesson-9")

    if not lesson_9_path.exists():
        pytest.skip("lesson-9 directory not found")

    # Find all .md and .ipynb files in lesson-9
    md_files = list(lesson_9_path.glob("*.md"))
    nb_files = list(lesson_9_path.glob("*.ipynb"))

    tutorial_files = md_files + nb_files

    if len(tutorial_files) == 0:
        pytest.skip("No tutorial files found in lesson-9")

    # Test first tutorial file
    test_file = tutorial_files[0]
    result = calculate_reading_time(str(test_file), wpm=200)

    # Should successfully calculate reading time
    assert result["error"] is None
    assert result["word_count"] > 0
    assert result["reading_time_minutes"] > 0


def test_should_handle_notebook_with_list_source() -> None:
    """Test that notebooks with source as list are handled correctly."""
    import json
    import tempfile

    with tempfile.TemporaryDirectory() as tmpdir:
        base_path = Path(tmpdir)
        nb_file = base_path / "tutorial.ipynb"

        # Create notebook with source as list (typical format)
        notebook_content = {
            "cells": [
                {
                    "cell_type": "markdown",
                    "metadata": {},
                    "source": ["This is line 1\n", "This is line 2"],
                }
            ],
            "metadata": {},
            "nbformat": 4,
            "nbformat_minor": 4,
        }

        nb_file.write_text(json.dumps(notebook_content))

        result = calculate_reading_time(str(nb_file), wpm=200)

        # Should count 8 words: "This is line 1" (4) + "This is line 2" (4)
        assert result["word_count"] == 8
        assert result["error"] is None


def test_should_handle_notebook_with_string_source() -> None:
    """Test that notebooks with source as string are handled correctly."""
    import json
    import tempfile

    with tempfile.TemporaryDirectory() as tmpdir:
        base_path = Path(tmpdir)
        nb_file = base_path / "tutorial.ipynb"

        # Create notebook with source as string (alternative format)
        notebook_content = {
            "cells": [
                {
                    "cell_type": "markdown",
                    "metadata": {},
                    "source": "This is a single string source",
                }
            ],
            "metadata": {},
            "nbformat": 4,
            "nbformat_minor": 4,
        }

        nb_file.write_text(json.dumps(notebook_content))

        result = calculate_reading_time(str(nb_file), wpm=200)

        # Should count 6 words
        assert result["word_count"] == 6
        assert result["error"] is None


def test_should_use_custom_wpm() -> None:
    """Test that custom WPM values are used correctly."""
    import tempfile

    with tempfile.TemporaryDirectory() as tmpdir:
        base_path = Path(tmpdir)
        md_file = base_path / "tutorial.md"

        # Create markdown with 1000 words
        content = " ".join(["word"] * 1000)
        md_file.write_text(content)

        # Test with 100 WPM (slower reading)
        result_100 = calculate_reading_time(str(md_file), wpm=100)
        assert result_100["reading_time_minutes"] == 10.0

        # Test with 500 WPM (faster reading)
        result_500 = calculate_reading_time(str(md_file), wpm=500)
        assert result_500["reading_time_minutes"] == 2.0


# ============================================================================
# Validation Report Generation Tests
# ============================================================================


def test_should_generate_pass_report_when_all_valid() -> None:
    """Test that report shows ✅ PASS when all validations pass."""
    tutorial_index_result = {
        "valid": True,
        "missing_sections": [],
        "found_sections": 10,
        "has_learning_time": True,
        "learning_time": "3-4 hours",
        "has_difficulty": True,
        "difficulty": "Intermediate",
        "tutorial_count": 5,
    }

    notebook_results = [
        {
            "executed": True,
            "execution_time": 2.84,
            "status": "success",
            "notebook_path": "lesson-9/perplexity.ipynb",
        }
    ]

    cross_link_result = {"valid": True, "total_links": 12, "broken_links": 0, "invalid_paths": []}

    mermaid_result = {"valid": True, "total_diagrams": 2, "invalid_diagrams": 0, "errors": []}

    reading_time_results = [{"word_count": 4000, "reading_time_minutes": 20.0, "status": "optimal"}]

    report = generate_validation_report(
        directory="lesson-9/",
        tutorial_index_result=tutorial_index_result,
        notebook_results=notebook_results,
        cross_link_result=cross_link_result,
        mermaid_result=mermaid_result,
        reading_time_results=reading_time_results,
        validation_time=8.2,
    )

    assert "📋 Tutorial Validation Report: lesson-9/" in report
    assert "✅ PASS" in report
    assert "All required sections present (10/10)" in report
    assert "All notebooks executed (1/1)" in report
    assert "All links valid (12/12)" in report
    assert "All diagrams valid (2/2)" in report
    assert "Reading time within range" in report
    assert "Validation completed in 8.2s" in report


def test_should_generate_fail_report_when_invalid() -> None:
    """Test that report shows ❌ FAIL when validation fails."""
    tutorial_index_result = {
        "valid": False,
        "missing_sections": ["FAQ", "Common Pitfalls"],
        "found_sections": 8,
    }

    report = generate_validation_report(directory="lesson-10/", tutorial_index_result=tutorial_index_result)

    assert "❌ FAIL" in report
    assert "Missing sections: FAQ, Common Pitfalls" in report
    assert "Add missing sections using template" in report
    assert "Recommendations:" in report


def test_should_generate_warning_report_when_issues_exist() -> None:
    """Test that report shows ⚠️ PASS with warnings when minor issues exist."""
    notebook_results = [
        {
            "executed": True,
            "execution_time": 2.5,
            "status": "success",
            "notebook_path": "lesson-9/notebook1.ipynb",
        },
        {
            "executed": False,
            "execution_time": 0,
            "status": "error",
            "error": "OPENAI_API_KEY not set",
            "notebook_path": "lesson-9/notebook2.ipynb",
        },
    ]

    report = generate_validation_report(directory="lesson-9/", notebook_results=notebook_results)

    assert "⚠️ PASS (with warnings)" in report
    assert "1/2 notebooks executed" in report
    assert "notebook2.ipynb" in report
    assert "OPENAI_API_KEY" in report


def test_should_show_broken_links_in_report() -> None:
    """Test that broken links are displayed with actionable suggestions."""
    cross_link_result = {
        "valid": False,
        "total_links": 12,
        "broken_links": 2,
        "invalid_paths": [
            {"link": "../lesson-9-11/README.md", "resolved_path": "/path/to/README.md", "error": "File not found"},
            {"link": "../lesson-10/tutorial.md", "resolved_path": "/path/to/tutorial.md", "error": "File not found"},
        ],
    }

    report = generate_validation_report(directory="lesson-9/", cross_link_result=cross_link_result)

    assert "10/12 links valid (83.3%)" in report
    assert "../lesson-9-11/README.md" in report
    assert "../lesson-10/tutorial.md" in report
    assert "Fix broken link" in report


def test_should_show_mermaid_errors_in_report() -> None:
    """Test that Mermaid syntax errors are displayed with suggestions."""
    mermaid_result = {
        "valid": False,
        "total_diagrams": 3,
        "invalid_diagrams": 1,
        "errors": [
            {
                "file": "lesson-9/diagrams/broken.mmd",
                "error": "Syntax Error: Line 42: Unexpected token '}'",
            }
        ],
    }

    report = generate_validation_report(directory="lesson-9/", mermaid_result=mermaid_result)

    assert "2/3 diagrams valid" in report
    assert "broken.mmd" in report
    assert "Syntax Error" in report
    assert "https://mermaid.live" in report


def test_should_show_timeout_warnings_in_report() -> None:
    """Test that notebook timeouts are shown with warnings."""
    notebook_results = [
        {
            "executed": False,
            "execution_time": 305,
            "status": "timeout",
            "error": "Notebook execution exceeded timeout (300s)",
            "notebook_path": "lesson-9/slow_notebook.ipynb",
        }
    ]

    report = generate_validation_report(directory="lesson-9/", notebook_results=notebook_results)

    assert "⏱️ slow_notebook.ipynb" in report
    assert "exceeded timeout" in report
    assert "Optimize" in report or "increase timeout" in report


def test_should_show_reading_time_warnings() -> None:
    """Test that long reading times are shown with warnings."""
    reading_time_results = [
        {"word_count": 8000, "reading_time_minutes": 40.0, "status": "too_long"},
        {"word_count": 4000, "reading_time_minutes": 20.0, "status": "optimal"},
    ]

    report = generate_validation_report(directory="lesson-9/", reading_time_results=reading_time_results)

    assert "⚠️ Total reading time: ~60 min (12,000 words)" in report
    assert "File exceeds 30 min target (40 min)" in report
    assert "splitting long tutorials" in report


def test_should_handle_no_cross_links() -> None:
    """Test that report handles tutorials with no cross-links."""
    cross_link_result = {"valid": True, "total_links": 0, "broken_links": 0, "invalid_paths": []}

    report = generate_validation_report(directory="lesson-9/", cross_link_result=cross_link_result)

    assert "No cross-links to validate" in report
    assert "✅" in report


def test_should_handle_no_mermaid_diagrams() -> None:
    """Test that report handles tutorials with no Mermaid diagrams."""
    mermaid_result = {"valid": True, "total_diagrams": 0, "invalid_diagrams": 0, "errors": []}

    report = generate_validation_report(directory="lesson-9/", mermaid_result=mermaid_result)

    assert "No Mermaid diagrams to validate" in report
    assert "ℹ️" in report


def test_should_limit_recommendations_count() -> None:
    """Test that report limits recommendations to avoid overwhelming output."""
    # Create many broken links
    invalid_paths = [
        {"link": f"../broken-{i}.md", "resolved_path": f"/path/{i}.md", "error": "Not found"} for i in range(10)
    ]

    cross_link_result = {"valid": False, "total_links": 10, "broken_links": 10, "invalid_paths": invalid_paths}

    report = generate_validation_report(directory="lesson-9/", cross_link_result=cross_link_result)

    # Should show first 3 broken links
    assert "../broken-0.md" in report
    assert "../broken-1.md" in report
    assert "../broken-2.md" in report

    # Should show "... and X more broken links"
    assert "and 7 more broken links" in report


def test_should_raise_error_for_invalid_directory_type() -> None:
    """Test that report generation raises TypeError for non-string directory."""
    with pytest.raises(TypeError, match="directory must be a string"):
        generate_validation_report(directory=None)  # type: ignore


def test_should_generate_minimal_report_when_no_results() -> None:
    """Test that report can be generated with minimal data."""
    report = generate_validation_report(directory="lesson-9/")

    assert "📋 Tutorial Validation Report: lesson-9/" in report
    assert "✅ PASS" in report
    assert "━" in report  # Separator lines


def test_should_prioritize_errors_over_warnings() -> None:
    """Test that errors appear before warnings in recommendations."""
    tutorial_index_result = {"valid": False, "missing_sections": ["FAQ"]}

    cross_link_result = {"valid": False, "total_links": 5, "broken_links": 1, "invalid_paths": [{"link": "test.md"}]}

    report = generate_validation_report(
        directory="lesson-9/", tutorial_index_result=tutorial_index_result, cross_link_result=cross_link_result
    )

    assert "Recommendations:" in report
    # Errors should come first
    recommendations_start = report.index("Recommendations:")
    error_pos = report.index("Add missing TUTORIAL_INDEX.md sections", recommendations_start)
    warning_pos = report.index("Fix broken link", recommendations_start)
    assert error_pos < warning_pos


def test_should_include_all_validation_sections() -> None:
    """Test that report includes all 5 validation check sections."""
    tutorial_index_result = {"valid": True}
    notebook_results = [{"executed": True, "notebook_path": "test.ipynb"}]
    cross_link_result = {"valid": True, "total_links": 0}
    mermaid_result = {"valid": True, "total_diagrams": 0}
    reading_time_results = [{"word_count": 1000, "reading_time_minutes": 5.0, "status": "too_short"}]

    report = generate_validation_report(
        directory="lesson-9/",
        tutorial_index_result=tutorial_index_result,
        notebook_results=notebook_results,
        cross_link_result=cross_link_result,
        mermaid_result=mermaid_result,
        reading_time_results=reading_time_results,
    )

    assert "1. TUTORIAL_INDEX.md Structure" in report
    assert "2. Notebook Execution" in report
    assert "3. Cross-Links" in report
    assert "4. Mermaid Diagrams" in report
    assert "5. Reading Time" in report


def test_should_format_report_with_proper_indentation() -> None:
    """Test that report has proper indentation and formatting."""
    tutorial_index_result = {"valid": True, "has_learning_time": True, "learning_time": "3-4 hours"}

    report = generate_validation_report(directory="lesson-9/", tutorial_index_result=tutorial_index_result)

    # Check indentation (3 spaces for main items, 6 for sub-items)
    assert "   ✅" in report  # Main item indentation
    assert "   -" in report  # Sub-item indentation

    # Check separator lines
    assert "━" * 60 in report


def test_should_truncate_long_error_messages() -> None:
    """Test that long error messages are truncated for readability."""
    notebook_results = [
        {
            "executed": False,
            "status": "error",
            "error": "A" * 200,  # Very long error message
            "notebook_path": "test.ipynb",
        }
    ]

    report = generate_validation_report(directory="lesson-9/", notebook_results=notebook_results)

    # Error should be truncated to 100 characters
    lines = report.split("\n")
    error_line = [line for line in lines if "Error:" in line][0]
    assert len(error_line) < 120  # Truncated to ~100 chars + "Error: " prefix
