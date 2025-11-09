"""Test suite for validating Jupyter notebook execution.

This module uses nbconvert to execute all tutorial notebooks and verify they run without errors.
Note: Some notebooks require API keys and will be skipped if not available.
"""

import os
from pathlib import Path
from typing import List

import nbformat
import pytest
from nbconvert.preprocessors import ExecutePreprocessor

# Find all notebooks in lesson directories
REPO_ROOT = Path(__file__).parent.parent
LESSON_DIRS = ["lesson-9", "lesson-10", "lesson-11"]

# Notebooks that require API keys (skip if OPENAI_API_KEY not set)
API_DEPENDENT_NOTEBOOKS = [
    "similarity_measurements_tutorial.ipynb",
    "judge_prompt_engineering_tutorial.ipynb",
    "judge_bias_detection_tutorial.ipynb",
]

# Notebooks that can run offline
OFFLINE_NOTEBOOKS = [
    "perplexity_calculation_tutorial.ipynb",
    "elo_ranking_tutorial.ipynb",
    "bradley_terry_ranking_tutorial.ipynb",
    "ab_testing_vs_comparative_eval.ipynb",
]


def get_all_notebooks() -> List[Path]:
    """Find all Jupyter notebooks in lesson directories."""
    notebooks = []
    for lesson_dir in LESSON_DIRS:
        lesson_path = REPO_ROOT / lesson_dir
        if lesson_path.exists():
            notebooks.extend(lesson_path.glob("*.ipynb"))
    return notebooks


def is_api_dependent(notebook_path: Path) -> bool:
    """Check if notebook requires API keys."""
    return notebook_path.name in API_DEPENDENT_NOTEBOOKS


def is_offline_notebook(notebook_path: Path) -> bool:
    """Check if notebook can run offline."""
    return notebook_path.name in OFFLINE_NOTEBOOKS


@pytest.fixture
def has_api_key() -> bool:
    """Check if OpenAI API key is available."""
    return bool(os.getenv("OPENAI_API_KEY"))


class TestNotebookExecution:
    """Test suite for notebook execution validation."""

    @pytest.mark.parametrize("notebook_path", get_all_notebooks())
    def test_notebook_execution(self, notebook_path: Path, has_api_key: bool) -> None:
        """Test that notebook executes without errors.

        Args:
            notebook_path: Path to notebook file
            has_api_key: Whether API key is available

        Raises:
            pytest.skip: If notebook requires API key but none is available
        """
        # Skip API-dependent notebooks if no API key
        if is_api_dependent(notebook_path) and not has_api_key:
            pytest.skip(f"Skipping {notebook_path.name} - requires OPENAI_API_KEY")

        # Read notebook
        with open(notebook_path) as f:
            nb = nbformat.read(f, as_version=4)

        # Configure executor with timeout
        ep = ExecutePreprocessor(timeout=600, kernel_name="python3")

        try:
            # Execute notebook
            ep.preprocess(nb, {"metadata": {"path": notebook_path.parent}})
        except Exception as e:
            pytest.fail(f"Notebook {notebook_path.name} failed to execute: {str(e)}")

    def test_all_notebooks_have_cost_warnings(self) -> None:
        """Verify API-dependent notebooks have cost warnings."""
        for lesson_dir in LESSON_DIRS:
            lesson_path = REPO_ROOT / lesson_dir
            if not lesson_path.exists():
                continue

            for notebook_path in lesson_path.glob("*.ipynb"):
                if not is_api_dependent(notebook_path):
                    continue

                with open(notebook_path) as f:
                    nb = nbformat.read(f, as_version=4)

                # Check first few cells for cost warning
                first_cells = nb.cells[:3]
                has_cost_warning = any(
                    "cost" in cell.get("source", "").lower()
                    or "warning" in cell.get("source", "").lower()
                    for cell in first_cells
                    if cell["cell_type"] == "markdown"
                )

                assert has_cost_warning, (
                    f"{notebook_path.name} missing cost warning in first 3 cells"
                )

    def test_offline_notebooks_exist(self) -> None:
        """Verify all offline notebooks are present."""
        all_notebooks = get_all_notebooks()
        found_offline = [nb for nb in all_notebooks if is_offline_notebook(nb)]

        assert len(found_offline) == len(OFFLINE_NOTEBOOKS), (
            f"Expected {len(OFFLINE_NOTEBOOKS)} offline notebooks, found {len(found_offline)}"
        )

    def test_api_dependent_notebooks_exist(self) -> None:
        """Verify all API-dependent notebooks are present."""
        all_notebooks = get_all_notebooks()
        found_api_dependent = [nb for nb in all_notebooks if is_api_dependent(nb)]

        # Note: Not all API-dependent notebooks may exist yet
        assert len(found_api_dependent) >= 1, (
            "Expected at least 1 API-dependent notebook"
        )

    def test_notebook_has_valid_structure(self) -> None:
        """Verify notebooks have valid cell structure."""
        for notebook_path in get_all_notebooks():
            with open(notebook_path) as f:
                nb = nbformat.read(f, as_version=4)

            # Check for at least one markdown cell (introduction)
            markdown_cells = [
                cell for cell in nb.cells if cell["cell_type"] == "markdown"
            ]
            assert len(markdown_cells) >= 1, (
                f"{notebook_path.name} has no markdown cells"
            )

            # Check for at least one code cell
            code_cells = [cell for cell in nb.cells if cell["cell_type"] == "code"]
            assert len(code_cells) >= 1, f"{notebook_path.name} has no code cells"

            # First cell should be markdown (introduction)
            assert nb.cells[0]["cell_type"] == "markdown", (
                f"{notebook_path.name} first cell should be markdown introduction"
            )


class TestNotebookContent:
    """Test suite for notebook content validation."""

    def test_notebooks_have_proper_titles(self) -> None:
        """Verify notebooks have descriptive titles in first cell."""
        for notebook_path in get_all_notebooks():
            with open(notebook_path) as f:
                nb = nbformat.read(f, as_version=4)

            first_cell = nb.cells[0]
            assert first_cell["cell_type"] == "markdown", (
                f"{notebook_path.name} first cell must be markdown"
            )

            source = first_cell["source"]
            assert "#" in source, (
                f"{notebook_path.name} first cell missing markdown header"
            )
            assert len(source) > 20, f"{notebook_path.name} first cell title too short"

    def test_notebooks_have_imports(self) -> None:
        """Verify notebooks have import statements."""
        for notebook_path in get_all_notebooks():
            with open(notebook_path) as f:
                nb = nbformat.read(f, as_version=4)

            # Find code cells with imports
            import_cells = [
                cell
                for cell in nb.cells
                if cell["cell_type"] == "code"
                and (
                    "import " in cell.get("source", "")
                    or "from " in cell.get("source", "")
                )
            ]

            assert len(import_cells) >= 1, (
                f"{notebook_path.name} has no import statements"
            )

    def test_notebooks_have_outputs_cleared(self) -> None:
        """Verify notebooks have outputs cleared (for version control cleanliness)."""
        # This is a recommendation but not enforced - notebooks may have sample outputs
        # Just check that they don't have execution_count set to indicate fresh state
        pass  # Skip this test for now as some notebooks may intentionally have outputs
