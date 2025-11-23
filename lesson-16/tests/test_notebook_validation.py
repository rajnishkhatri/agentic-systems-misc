"""
Tests for notebook validation infrastructure (Task 5.1).

Tests validate that the notebook validation script correctly checks:
- Notebook structure (12 sections)
- Import statements
- Cross-links
- Execution time
- Overall validation logic
"""

import json
import sys
from pathlib import Path
from typing import Any

import pytest

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from validate_notebook import (
    check_cross_links,
    check_imports,
    check_structure,
    load_notebook,
    validate_notebook,
)


@pytest.fixture
def temp_notebook_dir(tmp_path: Path) -> Path:
    """Create temporary directory for test notebooks."""
    notebook_dir = tmp_path / "notebooks"
    notebook_dir.mkdir()
    return notebook_dir


@pytest.fixture
def minimal_valid_notebook() -> dict[str, Any]:
    """Create minimal valid notebook structure."""
    return {
        "cells": [
            {
                "cell_type": "markdown",
                "source": ["# Test Notebook\n", "\n", "## Learning Objectives\n", "\n", "1. Learn things\n"],
            },
            {
                "cell_type": "markdown",
                "source": ["## Prerequisites\n", "\n", "- Basic Python\n"],
            },
            {
                "cell_type": "code",
                "source": ["import os\n", "import sys\n"],
            },
            {
                "cell_type": "markdown",
                "source": ["## Step 1: First Step\n"],
            },
            {
                "cell_type": "code",
                "source": ["result = 1 + 1\n", "assert result == 2\n"],
            },
            {
                "cell_type": "markdown",
                "source": ["## Step 2: Second Step\n"],
            },
            {
                "cell_type": "code",
                "source": ["print('Step 2')\n"],
            },
            {
                "cell_type": "markdown",
                "source": ["## Step 3: Third Step\n"],
            },
            {
                "cell_type": "code",
                "source": ["print('Step 3')\n"],
            },
            {
                "cell_type": "markdown",
                "source": ["## Visualization\n"],
            },
            {
                "cell_type": "code",
                "source": ["import matplotlib.pyplot as plt\n", "plt.show()\n"],
            },
            {
                "cell_type": "markdown",
                "source": ["## Validation\n"],
            },
            {
                "cell_type": "code",
                "source": ["assert True\n"],
            },
            {
                "cell_type": "markdown",
                "source": ["## Summary and Key Takeaways\n", "\n", "We learned things.\n"],
            },
            {
                "cell_type": "markdown",
                "source": ["## Next Steps\n", "\n", "Continue learning.\n"],
            },
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


# Test 1: Notebook structure validation
def test_should_pass_structure_checks_when_all_sections_present(minimal_valid_notebook: dict[str, Any]) -> None:
    """Test that notebook with all required sections passes structure checks."""
    checks = check_structure(minimal_valid_notebook)

    # Verify all checks exist
    assert "has_markdown_cells" in checks
    assert "has_code_cells" in checks
    assert "has_title" in checks
    assert "has_learning_objectives" in checks
    assert "has_prerequisites" in checks
    assert "has_setup" in checks
    assert "has_steps" in checks
    assert "has_visualization" in checks
    assert "has_validation" in checks
    assert "has_summary" in checks
    assert "has_next_steps" in checks
    assert "has_metadata" in checks

    # Verify all pass
    assert all(checks.values()), f"Some checks failed: {[k for k, v in checks.items() if not v]}"


def test_should_fail_structure_checks_when_sections_missing() -> None:
    """Test that notebook with missing sections fails structure checks."""
    incomplete_notebook = {
        "cells": [
            {
                "cell_type": "code",
                "source": ["print('hello')\n"],
            }
        ],
        "metadata": {},
    }

    checks = check_structure(incomplete_notebook)

    # Should fail most checks
    assert not checks["has_markdown_cells"]
    assert not checks["has_title"]
    assert not checks["has_learning_objectives"]
    assert not checks["has_prerequisites"]
    assert not checks["has_steps"]
    assert not checks["has_summary"]
    assert not checks["has_next_steps"]


# Test 2: Import statement detection
def test_should_detect_imports_when_present(minimal_valid_notebook: dict[str, Any]) -> None:
    """Test that import statements are correctly detected."""
    checks = check_imports(minimal_valid_notebook)

    assert checks["has_imports"] is True
    assert checks["import_count"] > 0


def test_should_detect_backend_imports_when_present() -> None:
    """Test that lesson-16 backend imports are detected."""
    notebook = {
        "cells": [
            {
                "cell_type": "code",
                "source": ["from lesson_16.backend.orchestrators import SequentialOrchestrator\n"],
            }
        ]
    }

    checks = check_imports(notebook)

    assert checks["has_backend_imports"] is True


def test_should_count_zero_imports_when_none_present() -> None:
    """Test that notebooks without imports return zero count."""
    notebook = {
        "cells": [
            {
                "cell_type": "code",
                "source": ["print('no imports here')\n"],
            }
        ]
    }

    checks = check_imports(notebook)

    assert checks["import_count"] == 0
    assert checks["has_imports"] is False


# Test 3: Cross-link validation
def test_should_validate_cross_links_when_targets_exist(temp_notebook_dir: Path) -> None:
    """Test that cross-links to existing files are validated correctly."""
    # Create target file
    target_file = temp_notebook_dir.parent / "tutorials" / "test.md"
    target_file.parent.mkdir(exist_ok=True)
    target_file.write_text("# Test Tutorial")

    # Create notebook with link
    notebook_path = temp_notebook_dir / "test.ipynb"
    notebook = {
        "cells": [
            {
                "cell_type": "markdown",
                "source": ["See [tutorial](../tutorials/test.md) for details.\n"],
            }
        ]
    }

    with open(notebook_path, "w") as f:
        json.dump(notebook, f)

    # Load and check
    loaded_notebook = load_notebook(notebook_path)
    checks = check_cross_links(loaded_notebook, notebook_path)

    assert checks["total_links"] == 1
    assert checks["valid_links"] == 1
    assert len(checks["broken_links"]) == 0


def test_should_detect_broken_links_when_targets_missing(temp_notebook_dir: Path) -> None:
    """Test that broken cross-links are detected."""
    notebook_path = temp_notebook_dir / "test.ipynb"
    notebook = {
        "cells": [
            {
                "cell_type": "markdown",
                "source": ["See [missing](../tutorials/missing.md) for details.\n"],
            }
        ]
    }

    with open(notebook_path, "w") as f:
        json.dump(notebook, f)

    loaded_notebook = load_notebook(notebook_path)
    checks = check_cross_links(loaded_notebook, notebook_path)

    assert checks["total_links"] == 1
    assert checks["valid_links"] == 0
    assert len(checks["broken_links"]) == 1
    assert checks["broken_links"][0]["path"] == "../tutorials/missing.md"


def test_should_skip_external_urls_in_cross_link_validation(temp_notebook_dir: Path) -> None:
    """Test that external URLs are not validated as file paths."""
    notebook_path = temp_notebook_dir / "test.ipynb"
    notebook = {
        "cells": [
            {
                "cell_type": "markdown",
                "source": [
                    "Visit [GitHub](https://github.com) and [docs](https://example.com).\n",
                    "Also see [local](./file.md).\n",
                ],
            }
        ]
    }

    with open(notebook_path, "w") as f:
        json.dump(notebook, f)

    loaded_notebook = load_notebook(notebook_path)
    checks = check_cross_links(loaded_notebook, notebook_path)

    # Should only count local link (file.md)
    assert checks["total_links"] == 1
    assert checks["valid_links"] == 0  # file.md doesn't exist


# Test 4: Notebook loading
def test_should_load_notebook_when_valid_json(temp_notebook_dir: Path, minimal_valid_notebook: dict[str, Any]) -> None:
    """Test that valid notebooks load correctly."""
    notebook_path = temp_notebook_dir / "valid.ipynb"

    with open(notebook_path, "w") as f:
        json.dump(minimal_valid_notebook, f)

    loaded = load_notebook(notebook_path)

    assert "cells" in loaded
    assert "metadata" in loaded
    assert len(loaded["cells"]) == len(minimal_valid_notebook["cells"])


def test_should_raise_error_when_notebook_not_found() -> None:
    """Test that loading non-existent notebook raises FileNotFoundError."""
    with pytest.raises(FileNotFoundError, match="Notebook not found"):
        load_notebook(Path("/nonexistent/notebook.ipynb"))


def test_should_raise_error_when_invalid_json(temp_notebook_dir: Path) -> None:
    """Test that invalid JSON raises ValueError."""
    notebook_path = temp_notebook_dir / "invalid.ipynb"

    with open(notebook_path, "w") as f:
        f.write("not valid json{")

    with pytest.raises(ValueError, match="Invalid notebook JSON"):
        load_notebook(notebook_path)


# Test 5: Overall validation integration
def test_should_pass_validation_when_notebook_meets_all_criteria(
    temp_notebook_dir: Path, minimal_valid_notebook: dict[str, Any]
) -> None:
    """Test that notebook meeting all criteria passes overall validation."""
    notebook_path = temp_notebook_dir / "complete.ipynb"

    with open(notebook_path, "w") as f:
        json.dump(minimal_valid_notebook, f)

    results = validate_notebook(notebook_path, execute=False)

    assert results["overall_pass"] is True
    assert all(results["structure"].values())
    assert results["imports"]["has_imports"] is True


def test_should_fail_validation_when_structure_incomplete(temp_notebook_dir: Path) -> None:
    """Test that notebook with incomplete structure fails validation."""
    incomplete_notebook = {
        "cells": [
            {
                "cell_type": "code",
                "source": ["print('incomplete')\n"],
            }
        ],
        "metadata": {},
    }

    notebook_path = temp_notebook_dir / "incomplete.ipynb"

    with open(notebook_path, "w") as f:
        json.dump(incomplete_notebook, f)

    results = validate_notebook(notebook_path, execute=False)

    assert results["overall_pass"] is False


def test_should_return_detailed_results_when_validating(
    temp_notebook_dir: Path, minimal_valid_notebook: dict[str, Any]
) -> None:
    """Test that validation returns detailed results for all checks."""
    notebook_path = temp_notebook_dir / "test.ipynb"

    with open(notebook_path, "w") as f:
        json.dump(minimal_valid_notebook, f)

    results = validate_notebook(notebook_path, execute=False)

    # Verify all result sections present
    assert "notebook" in results
    assert "structure" in results
    assert "imports" in results
    assert "cross_links" in results
    assert "execution" in results
    assert "overall_pass" in results

    # Verify structure details
    assert isinstance(results["structure"], dict)
    assert len(results["structure"]) >= 12  # At least 12 structure checks

    # Verify import details
    assert "import_count" in results["imports"]
    assert "has_imports" in results["imports"]

    # Verify cross-link details
    assert "total_links" in results["cross_links"]
    assert "valid_links" in results["cross_links"]
    assert "broken_links" in results["cross_links"]
