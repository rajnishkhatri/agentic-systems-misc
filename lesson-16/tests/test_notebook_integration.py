"""Integration tests for Lesson 16 notebooks.

Tests verify that notebooks:
1. Can be loaded without errors
2. Have required structure (12-section template)
3. Have valid navigation links
4. Import backend modules correctly
5. Have cross-references to tutorials
6. Execute without errors (when run manually)
"""

import json
from pathlib import Path

import pytest


# Notebook paths
NOTEBOOKS_DIR = Path(__file__).parent.parent / "notebooks"
NOTEBOOKS = [
    "08_sequential_orchestration_baseline.ipynb",
    "09_hierarchical_delegation_pattern.ipynb",
    "10_iterative_refinement_react.ipynb",
    "11_state_machine_orchestration.ipynb",
    "12_voting_ensemble_pattern.ipynb",
    "13_reliability_framework_implementation.ipynb",
    "14_agentarch_benchmark_reproduction.ipynb",
    "15_production_deployment_tutorial.ipynb",
]


@pytest.fixture
def notebooks_dir() -> Path:
    """Fixture providing notebooks directory path."""
    return NOTEBOOKS_DIR


@pytest.mark.parametrize("notebook_name", NOTEBOOKS)
def test_should_load_notebook_without_errors_when_file_exists(notebook_name: str, notebooks_dir: Path) -> None:
    """Test that notebook file exists and can be loaded as valid JSON."""
    notebook_path = notebooks_dir / notebook_name
    assert notebook_path.exists(), f"Notebook not found: {notebook_name}"

    # Load notebook
    with open(notebook_path, "r", encoding="utf-8") as f:
        notebook = json.load(f)

    assert isinstance(notebook, dict), "Notebook must be a dict"
    assert "cells" in notebook, "Notebook must have 'cells' key"
    assert isinstance(notebook["cells"], list), "Cells must be a list"
    assert len(notebook["cells"]) > 0, "Notebook must have at least 1 cell"


@pytest.mark.parametrize("notebook_name", NOTEBOOKS)
def test_should_have_navigation_header_when_notebook_loaded(notebook_name: str, notebooks_dir: Path) -> None:
    """Test that notebook has navigation header in first cell."""
    notebook_path = notebooks_dir / notebook_name

    with open(notebook_path, "r", encoding="utf-8") as f:
        notebook = json.load(f)

    cells = notebook["cells"]
    first_cell = cells[0]

    # Check first cell is markdown
    assert first_cell["cell_type"] == "markdown", "First cell must be markdown for navigation"

    # Check navigation content
    source = "".join(first_cell.get("source", []))
    assert "Navigation" in source or "🏠" in source, "First cell must contain navigation"
    assert "TUTORIAL_INDEX" in source, "Navigation must link to TUTORIAL_INDEX"


@pytest.mark.parametrize("notebook_name", NOTEBOOKS)
def test_should_have_navigation_footer_when_notebook_loaded(notebook_name: str, notebooks_dir: Path) -> None:
    """Test that notebook has navigation footer in last cell."""
    notebook_path = notebooks_dir / notebook_name

    with open(notebook_path, "r", encoding="utf-8") as f:
        notebook = json.load(f)

    cells = notebook["cells"]
    last_cell = cells[-1]

    # Check last cell is markdown
    assert last_cell["cell_type"] == "markdown", "Last cell must be markdown for navigation"

    # Check navigation content
    source = "".join(last_cell.get("source", []))
    assert "Navigation" in source or "🏠" in source, "Last cell must contain navigation"


@pytest.mark.parametrize("notebook_name", NOTEBOOKS)
def test_should_have_learning_objectives_when_notebook_loaded(notebook_name: str, notebooks_dir: Path) -> None:
    """Test that notebook has Learning Objectives section."""
    notebook_path = notebooks_dir / notebook_name

    with open(notebook_path, "r", encoding="utf-8") as f:
        notebook = json.load(f)

    # Find Learning Objectives cell
    found_objectives = False
    for cell in notebook["cells"]:
        if cell["cell_type"] == "markdown":
            source = "".join(cell.get("source", []))
            if "Learning Objectives" in source or "Learning objectives" in source:
                found_objectives = True
                # Check it lists objectives
                assert "1." in source or "- " in source, "Learning objectives must be listed"
                break

    assert found_objectives, "Notebook must have Learning Objectives section"


@pytest.mark.parametrize("notebook_name", NOTEBOOKS)
def test_should_import_backend_modules_when_notebook_has_code_cells(notebook_name: str, notebooks_dir: Path) -> None:
    """Test that notebook imports from lesson-16 backend."""
    notebook_path = notebooks_dir / notebook_name

    with open(notebook_path, "r", encoding="utf-8") as f:
        notebook = json.load(f)

    # Find import statements
    found_backend_import = False
    for cell in notebook["cells"]:
        if cell["cell_type"] == "code":
            source = "".join(cell.get("source", []))
            if "from backend" in source or "import backend" in source:
                found_backend_import = True
                break

    # All notebooks should import backend (orchestrators or reliability)
    assert found_backend_import, f"{notebook_name} must import from backend"


@pytest.mark.parametrize("notebook_name", NOTEBOOKS)
def test_should_have_cost_summary_when_notebook_loaded(notebook_name: str, notebooks_dir: Path) -> None:
    """Test that notebook has Cost Summary section."""
    notebook_path = notebooks_dir / notebook_name

    with open(notebook_path, "r", encoding="utf-8") as f:
        notebook = json.load(f)

    # Find Cost Summary cell
    found_cost_summary = False
    for cell in notebook["cells"]:
        if cell["cell_type"] == "markdown":
            source = "".join(cell.get("source", []))
            if "Cost Summary" in source or "COST SUMMARY" in source:
                found_cost_summary = True
                break

    assert found_cost_summary, "Notebook must have Cost Summary section"


@pytest.mark.parametrize("notebook_name", NOTEBOOKS)
def test_should_have_summary_and_takeaways_when_notebook_loaded(notebook_name: str, notebooks_dir: Path) -> None:
    """Test that notebook has Summary and Key Takeaways section."""
    notebook_path = notebooks_dir / notebook_name

    with open(notebook_path, "r", encoding="utf-8") as f:
        notebook = json.load(f)

    # Find Summary section
    found_summary = False
    for cell in notebook["cells"]:
        if cell["cell_type"] == "markdown":
            source = "".join(cell.get("source", []))
            if "Summary" in source and ("Takeaways" in source or "learned" in source):
                found_summary = True
                # Check it has key insights
                assert "✅" in source or "**" in source, "Summary must highlight key points"
                break

    assert found_summary, "Notebook must have Summary and Key Takeaways section"


@pytest.mark.parametrize("notebook_name", NOTEBOOKS)
def test_should_have_next_steps_when_notebook_loaded(notebook_name: str, notebooks_dir: Path) -> None:
    """Test that notebook has Next Steps section with tutorial cross-links."""
    notebook_path = notebooks_dir / notebook_name

    with open(notebook_path, "r", encoding="utf-8") as f:
        notebook = json.load(f)

    # Find Next Steps section
    found_next_steps = False
    for cell in notebook["cells"]:
        if cell["cell_type"] == "markdown":
            source = "".join(cell.get("source", []))
            if "Next Steps" in source:
                found_next_steps = True
                # Check it has tutorial links
                assert "../tutorials/" in source or ".ipynb" in source, "Next Steps must have tutorial/notebook links"
                break

    assert found_next_steps, "Notebook must have Next Steps section"


# Execution time targets (in seconds)
NOTEBOOK_TIME_TARGETS = {
    "08_sequential_orchestration_baseline.ipynb": 300,
    "09_hierarchical_delegation_pattern.ipynb": 300,
    "10_iterative_refinement_react.ipynb": 300,
    "11_state_machine_orchestration.ipynb": 300,
    "12_voting_ensemble_pattern.ipynb": 300,
    "13_reliability_framework_implementation.ipynb": 600,
    "14_agentarch_benchmark_reproduction.ipynb": 600,
    "15_production_deployment_tutorial.ipynb": 300,
}


@pytest.mark.parametrize("notebook_name", NOTEBOOKS)
def test_should_declare_execution_time_target_when_notebook_loaded(notebook_name: str, notebooks_dir: Path) -> None:
    """Test that notebook declares execution time estimate in header."""
    notebook_path = notebooks_dir / notebook_name

    with open(notebook_path, "r", encoding="utf-8") as f:
        notebook = json.load(f)

    # Check first few cells for execution time
    found_time_estimate = False
    for cell in notebook["cells"][:5]:  # Check first 5 cells
        if cell["cell_type"] == "markdown":
            source = "".join(cell.get("source", []))
            if "Execution Time" in source or "execution time" in source or "minutes" in source:
                found_time_estimate = True
                break

    assert found_time_estimate, f"{notebook_name} must declare execution time estimate"


# Integration test for notebook dependency diagram
def test_should_have_notebook_dependency_diagram() -> None:
    """Test that notebook dependency diagram exists."""
    diagrams_dir = Path(__file__).parent.parent / "diagrams"
    diagram_path = diagrams_dir / "notebook_dependency_diagram.mmd"

    assert diagram_path.exists(), "Notebook dependency diagram must exist"

    # Validate it references all 8 notebooks
    with open(diagram_path, "r", encoding="utf-8") as f:
        content = f.read()

    for notebook_name in NOTEBOOKS:
        # Check notebook number is in diagram
        nb_num = notebook_name.split("_")[0]  # Extract "08", "09", etc.
        assert nb_num in content or notebook_name in content, f"Diagram must reference {notebook_name}"


# Integration test for TUTORIAL_INDEX updates
def test_should_have_updated_tutorial_index_with_notebooks() -> None:
    """Test that TUTORIAL_INDEX.md references all 8 notebooks."""
    tutorial_index_path = Path(__file__).parent.parent / "TUTORIAL_INDEX.md"

    assert tutorial_index_path.exists(), "TUTORIAL_INDEX.md must exist"

    with open(tutorial_index_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Check all notebooks are referenced
    for notebook_name in NOTEBOOKS:
        assert notebook_name in content, f"TUTORIAL_INDEX.md must reference {notebook_name}"

    # Check it has Interactive Notebooks section
    assert "Interactive Notebooks" in content or "## Notebooks" in content, "Must have notebooks section"
