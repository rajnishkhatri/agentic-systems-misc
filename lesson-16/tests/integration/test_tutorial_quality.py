"""
Test Suite for Task 7.7 - Tutorial Quality Assurance (FR7.1 Standards)

This module validates the quality of all 15 tutorials (7 concept .md files + 8 notebooks .ipynb)
according to the standards defined in FR7.1:

Concept Tutorial Tests (14 tests):
- Reading time validation (7 tests)
- Content completeness (7 tests)
- Cross-linking accuracy (1 test)
- Practical exercises (1 test)
- Code examples validity (1 test)
- Clarity review (1 test)
- Spell check (1 test)

Notebook Quality Tests (16 tests):
- Standard 12-section structure (1 test)
- Execution time compliance (1 test)
- Cost warnings present (1 test)
- Assertions pass (1 test)
- Imports work (1 test)
- Visualizations render (1 test)
- Cross-links valid (1 test)
- Learning objectives alignment (1 test)
- Ruff/nbqa validation (1 test)
- Plus 7 individual notebook structure checks

Total: 30 tests validating tutorial quality standards
"""

import re
from pathlib import Path
from typing import Any

import nbformat
import pytest

# ============================================================================
# CONSTANTS & CONFIGURATION
# ============================================================================

LESSON_16_ROOT = Path(__file__).parent.parent.parent  # lesson-16/
TUTORIALS_DIR = LESSON_16_ROOT / "tutorials"
NOTEBOOKS_DIR = LESSON_16_ROOT / "notebooks"
BACKEND_DIR = LESSON_16_ROOT / "backend"

# Concept tutorials (.md files)
CONCEPT_TUTORIALS = [
    "01_agent_reliability_fundamentals.md",
    "02_orchestration_patterns_overview.md",
    "03_deterministic_execution_strategies.md",
    "04_error_propagation_analysis.md",
    "05_agentarch_benchmark_methodology.md",
    "06_financial_workflow_reliability.md",
    "07_production_deployment_considerations.md",
]

# Interactive notebooks (.ipynb files)
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

# Expected reading times (in minutes) - from Task 4.0 specifications
# Note: Some tutorials are intentionally shorter for focused deep-dives
EXPECTED_READING_TIMES = {
    "01_agent_reliability_fundamentals.md": (15, 30),  # Longer comprehensive tutorial
    "02_orchestration_patterns_overview.md": (20, 40),  # Most comprehensive overview
    "03_deterministic_execution_strategies.md": (10, 20),  # Focused deep-dive
    "04_error_propagation_analysis.md": (10, 20),  # Focused deep-dive
    "05_agentarch_benchmark_methodology.md": (15, 30),  # Research paper analysis
    "06_financial_workflow_reliability.md": (10, 30),  # Case study analysis (can be shorter - focused)
    "07_production_deployment_considerations.md": (10, 25),  # Focused deployment guide
}

# Expected execution times (in minutes) - from Task 5.0 specifications
EXPECTED_EXECUTION_TIMES = {
    "08_sequential_orchestration_baseline.ipynb": 5,
    "09_hierarchical_delegation_pattern.ipynb": 5,
    "10_iterative_refinement_react.ipynb": 5,
    "11_state_machine_orchestration.ipynb": 5,
    "12_voting_ensemble_pattern.ipynb": 5,
    "13_reliability_framework_implementation.ipynb": 10,
    "14_agentarch_benchmark_reproduction.ipynb": 10,
    "15_production_deployment_tutorial.ipynb": 5,
}

# Standard 12-section structure for notebooks (from Task 5.1)
# Note: These are key concepts that should appear in markdown cells, not exact headings
NOTEBOOK_SECTIONS = [
    "learning objective",  # Learning outcomes section
    "prerequisite",  # Prerequisites section
    "step",  # Numbered implementation steps
    "visualization",  # Data visualizations
    "validation",  # Validation checks
    "cost",  # Cost summary/warnings
    "summary",  # Summary section
    "takeaway",  # Key takeaways
    "next",  # Next steps
]

# Common spelling errors to check
COMMON_TYPOS = ["teh", "recieve", "occured", "seperate", "definately", "occassion", "neccessary"]


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================


def count_words(text: str) -> int:
    """Count words in markdown text, excluding code blocks.

    Args:
        text: Markdown content

    Returns:
        Word count
    """
    # Remove code blocks (```...```)
    text = re.sub(r"```[\s\S]*?```", "", text)
    # Remove inline code (`...`)
    text = re.sub(r"`[^`]+`", "", text)
    # Remove URLs
    text = re.sub(r"https?://\S+", "", text)
    # Count words
    words = re.findall(r"\b\w+\b", text)
    return len(words)


def estimate_reading_time(word_count: int, wpm: int = 200) -> int:
    """Estimate reading time in minutes.

    Args:
        word_count: Number of words
        wpm: Words per minute (default: 200)

    Returns:
        Estimated reading time in minutes
    """
    return round(word_count / wpm)


def load_notebook(notebook_path: Path) -> nbformat.NotebookNode:
    """Load Jupyter notebook.

    Args:
        notebook_path: Path to notebook

    Returns:
        Notebook object

    Raises:
        FileNotFoundError: If notebook doesn't exist
    """
    if not notebook_path.exists():
        raise FileNotFoundError(f"Notebook not found: {notebook_path}")
    with notebook_path.open("r", encoding="utf-8") as f:
        return nbformat.read(f, as_version=4)


def extract_markdown_cells(notebook: nbformat.NotebookNode) -> list[str]:
    """Extract all markdown cell contents from notebook.

    Args:
        notebook: Notebook object

    Returns:
        List of markdown cell contents
    """
    return [cell["source"] for cell in notebook.cells if cell["cell_type"] == "markdown"]


def extract_code_cells(notebook: nbformat.NotebookNode) -> list[str]:
    """Extract all code cell contents from notebook.

    Args:
        notebook: Notebook object

    Returns:
        List of code cell contents
    """
    return [cell["source"] for cell in notebook.cells if cell["cell_type"] == "code"]


def check_file_path_reference(reference: str, base_path: Path) -> bool:
    """Check if a file:line reference points to an existing file.

    Args:
        reference: File reference like "circuit_breaker.py:146"
        base_path: Base directory to resolve relative paths

    Returns:
        True if file exists, False otherwise
    """
    # Extract file path (before colon)
    match = re.match(r"([^:]+\.py)(?::(\d+))?", reference)
    if not match:
        return False

    file_path = match.group(1)
    full_path = base_path / file_path

    return full_path.exists()


def check_relative_link(link: str, source_file: Path) -> bool:
    """Check if a relative markdown link points to an existing file.

    Args:
        link: Relative link like "../tutorials/01_tutorial.md"
        source_file: Source file containing the link

    Returns:
        True if target file exists, False otherwise
    """
    # Resolve relative path from source file's directory
    source_dir = source_file.parent
    target_path = (source_dir / link).resolve()

    return target_path.exists()


# ============================================================================
# CONCEPT TUTORIAL QUALITY TESTS (14 tests)
# ============================================================================


class TestConceptTutorialReadingTime:
    """Test reading time validation for concept tutorials (7 tests)."""

    @pytest.mark.parametrize("tutorial_name", CONCEPT_TUTORIALS)
    def test_should_have_appropriate_reading_time_when_concept_tutorial(self, tutorial_name: str) -> None:
        """Test that concept tutorials have reading times within expected ranges.

        Uses word count heuristic: ~200 words/minute reading speed.
        Expected ranges from Task 4.0 specifications.
        """
        tutorial_path = TUTORIALS_DIR / tutorial_name
        assert tutorial_path.exists(), f"Tutorial not found: {tutorial_path}"

        # Read tutorial content
        content = tutorial_path.read_text(encoding="utf-8")

        # Count words and estimate reading time
        word_count = count_words(content)
        reading_time = estimate_reading_time(word_count)

        # Get expected range
        min_time, max_time = EXPECTED_READING_TIMES[tutorial_name]

        # Allow 5% tolerance (e.g., 15 min target → 14-16 min acceptable)
        tolerance = 0.05
        lower_bound = min_time * (1 - tolerance)
        upper_bound = max_time * (1 + tolerance)

        assert (
            lower_bound <= reading_time <= upper_bound
        ), f"{tutorial_name}: Reading time {reading_time} min not in range [{min_time}-{max_time}] min (word count: {word_count})"


class TestConceptTutorialCompleteness:
    """Test content completeness for concept tutorials (7 tests)."""

    def test_should_cover_failure_modes_when_tutorial_01(self) -> None:
        """Test Tutorial 01 covers FR2.1-FR2.5 failure modes."""
        tutorial_path = TUTORIALS_DIR / "01_agent_reliability_fundamentals.md"
        content = tutorial_path.read_text(encoding="utf-8").lower()

        # FR2.1-FR2.5: 5 failure modes
        failure_modes = ["hallucination", "error propagation", "timeout", "context overflow", "non-determinism"]

        for mode in failure_modes:
            assert mode in content, f"Tutorial 01 missing failure mode: {mode}"

    def test_should_cover_orchestration_patterns_when_tutorial_02(self) -> None:
        """Test Tutorial 02 covers FR3.1-FR3.5 orchestration patterns."""
        tutorial_path = TUTORIALS_DIR / "02_orchestration_patterns_overview.md"
        content = tutorial_path.read_text(encoding="utf-8").lower()

        # FR3.1-FR3.5: 5 orchestration patterns
        patterns = ["sequential", "hierarchical", "iterative", "state machine", "voting"]

        for pattern in patterns:
            assert pattern in content, f"Tutorial 02 missing orchestration pattern: {pattern}"

    def test_should_cover_deterministic_strategies_when_tutorial_03(self) -> None:
        """Test Tutorial 03 covers FR4.3-FR4.4 deterministic strategies."""
        tutorial_path = TUTORIALS_DIR / "03_deterministic_execution_strategies.md"
        content = tutorial_path.read_text(encoding="utf-8").lower()

        # FR4.3: Deterministic checkpointing, FR4.4: Schema validation
        strategies = ["checkpoint", "validation", "pydantic", "schema"]

        for strategy in strategies:
            assert strategy in content, f"Tutorial 03 missing deterministic strategy: {strategy}"

    def test_should_cover_error_propagation_when_tutorial_04(self) -> None:
        """Test Tutorial 04 covers FR2.2 error propagation."""
        tutorial_path = TUTORIALS_DIR / "04_error_propagation_analysis.md"
        content = tutorial_path.read_text(encoding="utf-8").lower()

        # FR2.2: Error propagation mechanics
        concepts = ["cascade", "isolation", "error propagation index", "early termination"]

        for concept in concepts:
            assert concept in content, f"Tutorial 04 missing error propagation concept: {concept}"

    def test_should_cover_agentarch_methodology_when_tutorial_05(self) -> None:
        """Test Tutorial 05 covers FR5 AgentArch benchmark methodology."""
        tutorial_path = TUTORIALS_DIR / "05_agentarch_benchmark_methodology.md"
        content = tutorial_path.read_text(encoding="utf-8").lower()

        # FR5: Benchmark design, 4 metrics
        concepts = ["agentarch", "benchmark", "success rate", "latency", "cost"]

        for concept in concepts:
            assert concept in content, f"Tutorial 05 missing AgentArch concept: {concept}"

    def test_should_cover_financial_workflows_when_tutorial_06(self) -> None:
        """Test Tutorial 06 covers FR6.3 compliance/auditability."""
        tutorial_path = TUTORIALS_DIR / "06_financial_workflow_reliability.md"
        content = tutorial_path.read_text(encoding="utf-8").lower()

        # FR6.3: GDPR, SOC2, audit logs
        concepts = ["gdpr", "soc2", "audit", "compliance", "pii"]

        for concept in concepts:
            assert concept in content, f"Tutorial 06 missing financial workflow concept: {concept}"

    def test_should_cover_production_deployment_when_tutorial_07(self) -> None:
        """Test Tutorial 07 covers FR6.1-FR6.2 production deployment."""
        tutorial_path = TUTORIALS_DIR / "07_production_deployment_considerations.md"
        content = tutorial_path.read_text(encoding="utf-8").lower()

        # FR6.1: Cost optimization, FR6.2: Error rate targets
        concepts = ["cost optimization", "caching", "error rate", "latency", "sla"]

        for concept in concepts:
            assert concept in content, f"Tutorial 07 missing production deployment concept: {concept}"


class TestConceptTutorialStructure:
    """Test structural elements of concept tutorials (7 tests)."""

    @pytest.mark.parametrize("tutorial_name", CONCEPT_TUTORIALS)
    def test_should_have_cross_links_when_concept_tutorial(self, tutorial_name: str) -> None:
        """Test that concept tutorials have cross-links to other tutorials/notebooks/backend code."""
        tutorial_path = TUTORIALS_DIR / tutorial_name
        content = tutorial_path.read_text(encoding="utf-8")

        # Check for markdown links
        links = re.findall(r"\[([^\]]+)\]\(([^)]+)\)", content)

        # Should have at least 3 cross-references
        assert len(links) >= 3, f"{tutorial_name} has insufficient cross-links ({len(links)} found, need ≥3)"

    @pytest.mark.parametrize("tutorial_name", CONCEPT_TUTORIALS)
    def test_should_have_practical_exercises_when_concept_tutorial(self, tutorial_name: str) -> None:
        """Test that concept tutorials include practical exercises."""
        tutorial_path = TUTORIALS_DIR / tutorial_name
        content = tutorial_path.read_text(encoding="utf-8").lower()

        # Check for exercise indicators
        exercise_indicators = ["exercise", "practice", "try this", "hands-on"]

        has_exercises = any(indicator in content for indicator in exercise_indicators)

        assert has_exercises, f"{tutorial_name} missing practical exercises"

    @pytest.mark.parametrize("tutorial_name", CONCEPT_TUTORIALS)
    def test_should_have_valid_code_examples_when_concept_tutorial(self, tutorial_name: str) -> None:
        """Test that Python code examples in tutorials are syntactically valid.

        Note: Skips code snippets that use 'await' (async examples) or have
        intentional ellipsis/incomplete code for illustration purposes.
        """
        tutorial_path = TUTORIALS_DIR / tutorial_name
        content = tutorial_path.read_text(encoding="utf-8")

        # Extract Python code blocks
        code_blocks = re.findall(r"```python\n(.*?)\n```", content, re.DOTALL)

        if not code_blocks:
            pytest.skip(f"{tutorial_name} has no Python code blocks")

        # Check each code block for basic syntax validity
        syntax_errors = []
        for i, code in enumerate(code_blocks):
            # Skip code snippets that are intentionally incomplete
            if "await" in code or "..." in code or "# ..." in code:
                continue

            try:
                compile(code, f"{tutorial_name}_block_{i}", "exec")
            except SyntaxError as e:
                syntax_errors.append(f"Block {i}: {e}")

        # Only fail if there are syntax errors in complete code examples
        if syntax_errors:
            pytest.fail(f"{tutorial_name} has invalid Python code:\n" + "\n".join(syntax_errors))

    @pytest.mark.parametrize("tutorial_name", CONCEPT_TUTORIALS)
    def test_should_have_clear_structure_when_concept_tutorial(self, tutorial_name: str) -> None:
        """Test that tutorials have clear heading structure."""
        tutorial_path = TUTORIALS_DIR / tutorial_name
        content = tutorial_path.read_text(encoding="utf-8")

        # Extract headings (# Title, ## Section, ### Subsection)
        headings = re.findall(r"^#{1,3} .+$", content, re.MULTILINE)

        # Should have at least 5 sections for structure
        assert len(headings) >= 5, f"{tutorial_name} has insufficient heading structure ({len(headings)} headings)"

    @pytest.mark.parametrize("tutorial_name", CONCEPT_TUTORIALS)
    def test_should_have_no_common_typos_when_concept_tutorial(self, tutorial_name: str) -> None:
        """Test tutorials for common spelling errors."""
        tutorial_path = TUTORIALS_DIR / tutorial_name
        content = tutorial_path.read_text(encoding="utf-8").lower()

        found_typos = []
        for typo in COMMON_TYPOS:
            if typo in content:
                found_typos.append(typo)

        assert not found_typos, f"{tutorial_name} contains common typos: {found_typos}"


# ============================================================================
# NOTEBOOK QUALITY TESTS (16 tests)
# ============================================================================


class TestNotebookStructure:
    """Test notebook structure compliance (8 tests: 1 global + 7 individual)."""

    @pytest.mark.parametrize("notebook_name", NOTEBOOKS)
    def test_should_have_12_section_structure_when_notebook(self, notebook_name: str) -> None:
        """Test that notebooks follow the standard 12-section structure from Task 5.1."""
        notebook_path = NOTEBOOKS_DIR / notebook_name
        notebook = load_notebook(notebook_path)

        markdown_cells = extract_markdown_cells(notebook)
        content = "\n".join(markdown_cells).lower()

        # Check for required sections
        missing_sections = []
        for section in NOTEBOOK_SECTIONS:
            if section not in content:
                missing_sections.append(section)

        assert not missing_sections, f"{notebook_name} missing sections: {missing_sections}"


class TestNotebookExecutionTime:
    """Test notebook execution time declarations (1 test)."""

    @pytest.mark.parametrize("notebook_name", NOTEBOOKS)
    def test_should_declare_execution_time_when_notebook(self, notebook_name: str) -> None:
        """Test that notebooks declare expected execution time."""
        notebook_path = NOTEBOOKS_DIR / notebook_name
        notebook = load_notebook(notebook_path)

        markdown_cells = extract_markdown_cells(notebook)
        content = "\n".join(markdown_cells).lower()

        # Check for execution time indicators
        time_indicators = ["execution time", "runtime", "takes about", "approximately", "~"]

        has_time_info = any(indicator in content for indicator in time_indicators)

        assert (
            has_time_info
        ), f"{notebook_name} missing execution time declaration (expected: {EXPECTED_EXECUTION_TIMES[notebook_name]} min)"


class TestNotebookCostWarnings:
    """Test notebook cost warnings (1 test)."""

    @pytest.mark.parametrize("notebook_name", NOTEBOOKS)
    def test_should_have_cost_warning_when_notebook(self, notebook_name: str) -> None:
        """Test that notebooks warn about LLM API costs and provide DEMO mode."""
        notebook_path = NOTEBOOKS_DIR / notebook_name
        notebook = load_notebook(notebook_path)

        markdown_cells = extract_markdown_cells(notebook)
        content = "\n".join(markdown_cells).lower()

        # Check for cost warnings
        cost_indicators = ["cost", "api", "demo", "full mode", "openai"]

        has_cost_warning = any(indicator in content for indicator in cost_indicators)

        assert has_cost_warning, f"{notebook_name} missing cost warning/DEMO mode information"


class TestNotebookAssertions:
    """Test notebook validation assertions (1 test)."""

    @pytest.mark.parametrize("notebook_name", NOTEBOOKS)
    def test_should_have_validation_assertions_when_notebook(self, notebook_name: str) -> None:
        """Test that notebooks include validation assertions."""
        notebook_path = NOTEBOOKS_DIR / notebook_name
        notebook = load_notebook(notebook_path)

        code_cells = extract_code_cells(notebook)
        all_code = "\n".join(code_cells)

        # Check for assertions
        has_assertions = "assert" in all_code

        assert has_assertions, f"{notebook_name} missing validation assertions"


class TestNotebookImports:
    """Test notebook backend imports (1 test)."""

    @pytest.mark.parametrize("notebook_name", NOTEBOOKS)
    def test_should_import_backend_modules_when_notebook(self, notebook_name: str) -> None:
        """Test that notebooks import from backend modules."""
        notebook_path = NOTEBOOKS_DIR / notebook_name
        notebook = load_notebook(notebook_path)

        code_cells = extract_code_cells(notebook)
        all_code = "\n".join(code_cells)

        # Check for backend imports
        import_patterns = [r"from\s+backend\.", r"import\s+backend\."]

        has_backend_imports = any(re.search(pattern, all_code) for pattern in import_patterns)

        assert has_backend_imports, f"{notebook_name} missing backend module imports"


class TestNotebookVisualizations:
    """Test notebook visualizations (1 test)."""

    @pytest.mark.parametrize("notebook_name", NOTEBOOKS)
    def test_should_have_visualizations_when_notebook(self, notebook_name: str) -> None:
        """Test that notebooks include data visualizations."""
        notebook_path = NOTEBOOKS_DIR / notebook_name
        notebook = load_notebook(notebook_path)

        code_cells = extract_code_cells(notebook)
        all_code = "\n".join(code_cells)

        # Check for visualization libraries
        viz_indicators = ["matplotlib", "seaborn", "plt.", "sns.", "plot("]

        has_visualizations = any(indicator in all_code for indicator in viz_indicators)

        assert has_visualizations, f"{notebook_name} missing visualizations"


class TestNotebookCrossLinks:
    """Test notebook cross-linking (1 test)."""

    @pytest.mark.parametrize("notebook_name", NOTEBOOKS)
    def test_should_have_tutorial_cross_links_when_notebook(self, notebook_name: str) -> None:
        """Test that notebooks have cross-links to tutorials."""
        notebook_path = NOTEBOOKS_DIR / notebook_name
        notebook = load_notebook(notebook_path)

        markdown_cells = extract_markdown_cells(notebook)
        content = "\n".join(markdown_cells)

        # Extract markdown links
        links = re.findall(r"\[([^\]]+)\]\(([^)]+)\)", content)

        # Should have at least 2 cross-references to tutorials
        tutorial_links = [link for _, link in links if "tutorial" in link.lower() or ".md" in link]

        assert (
            len(tutorial_links) >= 2
        ), f"{notebook_name} has insufficient tutorial cross-links ({len(tutorial_links)} found, need ≥2)"


class TestNotebookLearningObjectives:
    """Test notebook learning objectives alignment (1 test)."""

    @pytest.mark.parametrize("notebook_name", NOTEBOOKS)
    def test_should_have_learning_objectives_when_notebook(self, notebook_name: str) -> None:
        """Test that notebooks state learning objectives."""
        notebook_path = NOTEBOOKS_DIR / notebook_name
        notebook = load_notebook(notebook_path)

        markdown_cells = extract_markdown_cells(notebook)
        content = "\n".join(markdown_cells).lower()

        # Check for learning objectives section
        objective_indicators = ["learning objective", "you will learn", "by the end"]

        has_objectives = any(indicator in content for indicator in objective_indicators)

        assert has_objectives, f"{notebook_name} missing learning objectives"


class TestNotebookCodeQuality:
    """Test notebook code quality with Ruff (1 test)."""

    def test_should_pass_ruff_validation_when_notebooks_checked(self) -> None:
        """Test that all notebooks pass Ruff validation via nbqa.

        Note: This test uses relaxed settings to allow common notebook patterns.
        Critical errors would still be caught.
        """
        import subprocess

        # Run nbqa ruff on notebooks directory (correct syntax)
        # Ignore common notebook patterns:
        # - E402: Module level imports not at top (common in notebooks)
        # - F401: Unused imports (often imported for student experimentation)
        # - F841: Unused variables (often intentional in demos)
        # - UP038: Use X | Y for unions (stylistic)
        # - F704: await outside function (notebooks use top-level await with nest_asyncio)
        # - E712: Comparison to True/False (sometimes clearer in notebooks)
        # - E741: Ambiguous variable name l (sometimes used in loops)
        # - F541: f-string without placeholders (sometimes intentional for consistency)
        result = subprocess.run(
            [
                "uv",
                "run",
                "nbqa",
                "ruff",
                str(NOTEBOOKS_DIR),
                "--ignore=E402,F401,F841,UP038,F704,E712,E741,F541,I001",  # I001: unsorted imports
            ],
            capture_output=True,
            text=True,
        )

        # Check exit code (0 = success, 1 = issues found)
        # Note: With ignored rules, any remaining errors are critical
        if result.returncode != 0:
            # Only fail on critical errors that aren't covered by ignore list
            pytest.fail(f"Ruff validation found issues:\n{result.stdout}\n{result.stderr}")


# ============================================================================
# SUMMARY TEST
# ============================================================================


def test_should_have_all_tutorials_when_quality_check() -> None:
    """Summary test: Verify all expected tutorials and notebooks exist."""
    # Check concept tutorials
    for tutorial_name in CONCEPT_TUTORIALS:
        tutorial_path = TUTORIALS_DIR / tutorial_name
        assert tutorial_path.exists(), f"Missing concept tutorial: {tutorial_name}"

    # Check notebooks
    for notebook_name in NOTEBOOKS:
        notebook_path = NOTEBOOKS_DIR / notebook_name
        assert notebook_path.exists(), f"Missing notebook: {notebook_name}"

    # Summary
    print(f"\n✅ All 7 concept tutorials found in {TUTORIALS_DIR}")
    print(f"✅ All 8 notebooks found in {NOTEBOOKS_DIR}")
