"""Tests for Lesson 16 diagrams (Task 6.6-6.10).

Tests validate:
1. Diagram files exist
2. Valid Mermaid syntax
3. Content completeness (all failure modes, patterns, components)
4. Cross-references to tutorials and backend code
"""

import re
from pathlib import Path

import pytest


# Test fixtures
@pytest.fixture
def diagrams_dir() -> Path:
    """Return path to diagrams directory."""
    return Path(__file__).parent.parent / "diagrams"


@pytest.fixture
def failure_modes_diagram(diagrams_dir: Path) -> Path:
    """Return path to failure modes taxonomy diagram."""
    return diagrams_dir / "reliability_failure_modes_taxonomy.mmd"


@pytest.fixture
def orchestration_pattern_diagram(diagrams_dir: Path) -> Path:
    """Return path to orchestration pattern selection diagram."""
    return diagrams_dir / "orchestration_pattern_selection.mmd"


# ============================================================================
# Task 6.6: Diagram 1 - Failure Modes Taxonomy (3 tests)
# ============================================================================


def test_should_have_failure_modes_diagram_file_when_checking_existence(
    failure_modes_diagram: Path,
) -> None:
    """Test that failure modes taxonomy diagram file exists."""
    assert failure_modes_diagram.exists(), f"Diagram file not found: {failure_modes_diagram}"
    assert failure_modes_diagram.is_file(), f"Path is not a file: {failure_modes_diagram}"
    assert failure_modes_diagram.stat().st_size > 0, "Diagram file is empty"


def test_should_have_valid_mermaid_syntax_when_parsing_failure_modes_diagram(
    failure_modes_diagram: Path,
) -> None:
    """Test that failure modes diagram has valid Mermaid syntax.

    Validates:
    - Starts with 'graph TD' declaration
    - Has node definitions with [] or {} brackets
    - Has arrow connections (-->)
    - Has styling class definitions
    """
    content = failure_modes_diagram.read_text()

    # Check for graph declaration
    assert re.search(r"graph\s+TD", content), "Missing 'graph TD' declaration"

    # Check for node definitions
    node_pattern = r"[A-Z][A-Za-z0-9_]*\[.+?\]|\{.+?\}"
    nodes = re.findall(node_pattern, content)
    assert len(nodes) > 10, f"Expected >10 nodes, found {len(nodes)}"

    # Check for arrow connections
    arrow_pattern = r"-->"
    arrows = re.findall(arrow_pattern, content)
    assert len(arrows) > 10, f"Expected >10 arrows, found {len(arrows)}"

    # Check for styling classes
    assert "classDef symptom" in content, "Missing symptom class definition"
    assert "classDef cause" in content, "Missing cause class definition"
    assert "classDef mitigation" in content, "Missing mitigation class definition"
    assert "classDef reference" in content, "Missing reference class definition"


def test_should_contain_all_5_failure_modes_when_validating_content(
    failure_modes_diagram: Path,
) -> None:
    """Test that diagram contains all 5 failure modes from FR2.1-FR2.5.

    Required failure modes:
    - FR2.1: Hallucinations
    - FR2.2: Error Propagation
    - FR2.3: Timeout
    - FR2.4: Context Overflow
    - FR2.5: Non-Determinism
    """
    content = failure_modes_diagram.read_text()

    # Check for all 5 failure mode sections
    failure_modes = {
        "FR2.1: Hallucinations": ["Hallucination", "Schema Validation", "Pydantic"],
        "FR2.2: Error Propagation": ["Error Propagation", "EPI", "Error Isolation"],
        "FR2.3: Timeout": ["Timeout", "Circuit Breaker", "Retry", "Backoff"],
        "FR2.4: Context Overflow": ["Context Overflow", "Compression", "Chunking"],
        "FR2.5: Non-Determinism": ["Non-Determinism", "temperature", "Checkpointing"],
    }

    for failure_mode, keywords in failure_modes.items():
        # Check comment section exists
        assert (
            failure_mode in content
        ), f"Missing failure mode section: {failure_mode}"

        # Check at least 2 keywords present
        found_keywords = sum(1 for keyword in keywords if keyword in content)
        assert (
            found_keywords >= 2
        ), f"Missing keywords for {failure_mode}: expected ≥2, found {found_keywords}"

    # Check for cross-references to tutorials
    tutorial_refs = [
        "03_deterministic_execution_strategies.md",
        "04_error_propagation_analysis.md",
    ]
    for ref in tutorial_refs:
        assert ref in content, f"Missing tutorial reference: {ref}"

    # Check for backend code reference
    assert "backend/reliability/" in content, "Missing backend code reference"


# ============================================================================
# Helper tests for PNG export (Task 6.6 requirement)
# ============================================================================


def test_should_have_png_export_when_diagram_is_complex(
    diagrams_dir: Path,
    failure_modes_diagram: Path,
) -> None:
    """Test that PNG export exists for complex diagram (>10 nodes).

    Task 6.6 requires PNG export for complexity >10 nodes.
    """
    png_file = diagrams_dir / "reliability_failure_modes_taxonomy.png"

    # Count nodes in diagram
    content = failure_modes_diagram.read_text()
    node_pattern = r"[A-Z][A-Za-z0-9_]*\[.+?\]|\{.+?\}"
    nodes = re.findall(node_pattern, content)

    if len(nodes) > 10:
        assert png_file.exists(), f"PNG export required for {len(nodes)} nodes (>10)"
        assert png_file.stat().st_size > 0, "PNG file is empty"
    else:
        pytest.skip(f"Diagram has {len(nodes)} nodes (≤10), PNG export not required")


# ============================================================================
# Task 6.7: Diagram 2 - Orchestration Pattern Selection (4 tests)
# ============================================================================


def test_should_have_orchestration_pattern_diagram_file_when_checking_existence(
    orchestration_pattern_diagram: Path,
) -> None:
    """Test that orchestration pattern selection diagram file exists (Task 6.7 Test 1)."""
    assert orchestration_pattern_diagram.exists(), f"Diagram file not found: {orchestration_pattern_diagram}"
    assert orchestration_pattern_diagram.is_file(), f"Path is not a file: {orchestration_pattern_diagram}"
    assert orchestration_pattern_diagram.stat().st_size > 0, "Diagram file is empty"


def test_should_have_valid_mermaid_syntax_when_parsing_orchestration_diagram(
    orchestration_pattern_diagram: Path,
) -> None:
    """Test that orchestration pattern diagram has valid Mermaid syntax (Task 6.7 Test 2).

    Validates:
    - Starts with 'graph TD' declaration
    - Has decision diamond nodes {}
    - Has pattern box nodes []
    - Has arrow connections with labels
    - Has styling class definitions
    """
    content = orchestration_pattern_diagram.read_text()

    # Check for graph declaration
    assert re.search(r"graph\s+TD", content), "Missing 'graph TD' declaration"

    # Check for decision nodes (diamonds)
    decision_pattern = r"[A-Z][A-Za-z0-9_]*\{.+?\}"
    decisions = re.findall(decision_pattern, content)
    assert len(decisions) >= 7, f"Expected ≥7 decision nodes, found {len(decisions)}"

    # Check for pattern nodes (boxes)
    pattern_pattern = r"[A-Z][A-Za-z0-9_]*\[.+?\]"
    patterns = re.findall(pattern_pattern, content)
    assert len(patterns) >= 20, f"Expected ≥20 pattern nodes, found {len(patterns)}"

    # Check for arrow connections with labels
    labeled_arrow_pattern = r"-->\|.+?\|"
    labeled_arrows = re.findall(labeled_arrow_pattern, content)
    assert len(labeled_arrows) >= 10, f"Expected ≥10 labeled arrows, found {len(labeled_arrows)}"

    # Check for styling classes
    assert "classDef requirement" in content, "Missing requirement class definition"
    assert "classDef decision" in content, "Missing decision class definition"
    assert "classDef pattern" in content, "Missing pattern class definition"


def test_should_contain_all_5_orchestration_patterns_when_validating_content(
    orchestration_pattern_diagram: Path,
) -> None:
    """Test that diagram contains all 5 orchestration patterns (Task 6.7 Test 3).

    Required patterns (FR3.1-FR3.5):
    - Sequential
    - Hierarchical
    - Iterative (ReAct/Reflexion)
    - State Machine
    - Voting/Ensemble
    """
    content = orchestration_pattern_diagram.read_text()

    # Check for all 5 patterns
    patterns = {
        "Sequential": ["Sequential Pattern", "1× baseline", "70%"],
        "Hierarchical": ["Hierarchical", "Parallel", "8s", "1.3×"],
        "Iterative": ["Iterative", "ReAct", "2.1×", "18s"],
        "State Machine": ["State Machine", "FSM", "85%", "1.1×"],
        "Voting": ["Voting", "Ensemble", "90%", "5×"],
    }

    for pattern_name, keywords in patterns.items():
        # Check at least 2 keywords present
        found_keywords = sum(1 for keyword in keywords if keyword in content)
        assert (
            found_keywords >= 2
        ), f"Missing keywords for {pattern_name}: expected ≥2, found {found_keywords}"

    # Check for pattern comparison table
    assert "Pattern Comparison Table" in content, "Missing pattern comparison table"

    # Check for cross-references to notebooks
    notebook_refs = [
        "notebooks/08_sequential_orchestration_baseline.ipynb",
        "notebooks/09_hierarchical_delegation_pattern.ipynb",
        "notebooks/10_iterative_refinement_react.ipynb",
        "notebooks/11_state_machine_orchestration.ipynb",
        "notebooks/12_voting_ensemble_pattern.ipynb",
    ]
    for ref in notebook_refs:
        assert ref in content, f"Missing notebook reference: {ref}"


def test_should_contain_all_7_requirement_paths_when_validating_decision_tree(
    orchestration_pattern_diagram: Path,
) -> None:
    """Test that diagram contains all 7 business requirement paths (Task 6.7 Test 4).

    Required paths (DC3 decision tree):
    1. Minimize Latency (<5s SLA) → Hierarchical
    2. Minimize Cost (budget-constrained) → Sequential
    3. Maximize Reliability (>95% success) → State Machine/Voting
    4. Handle Ambiguous Inputs → Iterative Refinement
    5. Audit Trail Required (compliance) → State Machine
    6. High-Stakes Decisions (fraud >$10K) → Voting
    7. Deterministic Outputs (regression tests) → State Machine
    """
    content = orchestration_pattern_diagram.read_text()

    # Check for all 7 requirement paths
    requirement_paths = {
        "Path 1: Minimize Latency": ["Latency", "SLA", "5s", "Hierarchical"],
        "Path 2: Minimize Cost": ["Cost", "Budget", "Sequential"],
        "Path 3: Maximize Reliability": ["Reliability", "95%", "Voting", "State Machine"],
        "Path 4: Handle Ambiguous Inputs": ["Ambiguous", "Iterative", "ReAct"],
        "Path 5: Audit Trail Required": ["Audit", "Compliance", "State Machine"],
        "Path 6: High-Stakes Decisions": ["High-Stakes", "Fraud", "$10K", "Voting"],
        "Path 7: Deterministic Outputs": ["Deterministic", "Regression", "State Machine"],
    }

    for path_name, keywords in requirement_paths.items():
        # Check comment section exists
        assert path_name in content, f"Missing requirement path: {path_name}"

        # Check at least 2 keywords present
        found_keywords = sum(1 for keyword in keywords if keyword in content)
        assert (
            found_keywords >= 2
        ), f"Missing keywords for {path_name}: expected ≥2, found {found_keywords}"

    # Verify pattern comparison table has all required columns
    table_columns = ["Success (%)", "Latency P50", "Cost (×)", "Best Use Case"]
    for column in table_columns:
        assert column in content, f"Missing column in comparison table: {column}"

    # Check PNG export exists for complex diagram
    png_file = orchestration_pattern_diagram.parent / "orchestration_pattern_selection.png"
    node_pattern = r"[A-Z][A-Za-z0-9_]*\[.+?\]|\{.+?\}"
    nodes = re.findall(node_pattern, content)
    if len(nodes) > 10:
        assert png_file.exists(), f"PNG export required for {len(nodes)} nodes (>10)"
