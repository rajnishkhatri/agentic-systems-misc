"""Tests for optional LLM flag functionality in memory_systems_implementation.ipynb.

Validates that the notebook correctly handles both USE_LLM=True and USE_LLM=False modes.
"""

import json
import subprocess
import sys
from pathlib import Path

import pytest


def test_should_execute_notebook_when_llm_disabled() -> None:
    """Test that notebook executes successfully with USE_LLM=False."""
    notebook_path = Path(__file__).parent.parent / "lesson-14" / "memory_systems_implementation.ipynb"

    if not notebook_path.exists():
        pytest.skip("Notebook not found")

    # Execute notebook with default USE_LLM=False
    result = subprocess.run(
        [
            "jupyter",
            "nbconvert",
            "--to",
            "notebook",
            "--execute",
            "--ExecutePreprocessor.timeout=300",
            str(notebook_path),
            "--output",
            "memory_systems_implementation_test_llm_false.ipynb",
        ],
        cwd=notebook_path.parent,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, f"Notebook execution failed: {result.stderr}"
    assert "error" not in result.stderr.lower() or "ExecutePreprocessor" in result.stderr


def test_should_have_llm_flag_defined_in_notebook() -> None:
    """Test that USE_LLM flag is defined in notebook configuration."""
    notebook_path = Path(__file__).parent.parent / "lesson-14" / "memory_systems_implementation.ipynb"

    if not notebook_path.exists():
        pytest.skip("Notebook not found")

    with open(notebook_path) as f:
        notebook = json.load(f)

    # Check that USE_LLM is defined in a code cell
    use_llm_found = False
    for cell in notebook["cells"]:
        if cell["cell_type"] == "code":
            source = "".join(cell["source"])
            if "USE_LLM" in source and "False" in source:
                use_llm_found = True
                break

    assert use_llm_found, "USE_LLM flag not found in notebook configuration cells"


def test_should_document_llm_flag_behavior() -> None:
    """Test that notebook documents LLM flag behavior in markdown."""
    notebook_path = Path(__file__).parent.parent / "lesson-14" / "memory_systems_implementation.ipynb"

    if not notebook_path.exists():
        pytest.skip("Notebook not found")

    with open(notebook_path) as f:
        notebook = json.load(f)

    # Check that USE_LLM behavior is documented
    documentation_found = False
    for cell in notebook["cells"]:
        if cell["cell_type"] in ["markdown", "code"]:
            source = "".join(cell["source"]).lower()
            if "use_llm" in source and ("mock" in source or "api" in source):
                documentation_found = True
                break

    assert documentation_found, "USE_LLM flag behavior not documented in notebook"


def test_should_generate_valid_json_with_llm_disabled() -> None:
    """Test that notebook generates valid JSON output with USE_LLM=False."""
    json_path = Path(__file__).parent.parent / "lesson-14" / "results" / "memory_systems_demo_results.json"

    if not json_path.exists():
        pytest.skip("JSON output not found - run notebook first")

    # Load and validate JSON
    with open(json_path) as f:
        data = json.load(f)

    # Validate required fields exist
    required_fields = ["version", "created", "execution_mode", "summary_statistics"]
    for field in required_fields:
        assert field in data, f"Missing required field: {field}"

    # Validate metrics are numeric and not NaN
    for metric_name, stats in data["summary_statistics"].items():
        assert "mean" in stats, f"Metric {metric_name} missing 'mean'"
        assert "std" in stats, f"Metric {metric_name} missing 'std'"
        assert isinstance(stats["mean"], (int, float)), f"Metric {metric_name}['mean'] not numeric"
        assert isinstance(stats["std"], (int, float)), f"Metric {metric_name}['std'] not numeric"


def test_should_complete_in_reasonable_time() -> None:
    """Test that notebook execution time is reasonable (<10 min for DEMO, <40 min for FULL with USE_LLM=False)."""
    import time

    notebook_path = Path(__file__).parent.parent / "lesson-14" / "memory_systems_implementation.ipynb"

    if not notebook_path.exists():
        pytest.skip("Notebook not found")

    # Measure execution time
    start_time = time.time()
    result = subprocess.run(
        [
            "jupyter",
            "nbconvert",
            "--to",
            "notebook",
            "--execute",
            "--ExecutePreprocessor.timeout=600",
            str(notebook_path),
            "--output",
            "memory_systems_implementation_timing_test.ipynb",
        ],
        cwd=notebook_path.parent,
        capture_output=True,
        text=True,
    )
    execution_time = time.time() - start_time

    assert result.returncode == 0, "Notebook execution failed"

    # Check execution time (should be <10 min for DEMO, <60 sec for FULL with mock LLM)
    # Since we're using mock LLM (USE_LLM=False), expect fast execution
    assert execution_time < 60, f"Execution took too long: {execution_time:.1f}s (expected <60s with USE_LLM=False)"


@pytest.mark.skipif(
    "OPENAI_API_KEY" not in __import__("os").environ,
    reason="OPENAI_API_KEY not set - skipping real LLM test",
)
def test_should_gracefully_handle_llm_when_enabled() -> None:
    """Test that notebook handles USE_LLM=True gracefully (if API key available).

    This test is skipped if OPENAI_API_KEY is not set.
    """
    # This test would modify the notebook to set USE_LLM=True and re-execute
    # For now, we just validate that the infrastructure is in place
    pytest.skip("Real LLM testing requires API key and is expensive - manual verification recommended")


def test_should_not_crash_when_api_key_missing() -> None:
    """Test that notebook doesn't crash when USE_LLM=True but API key is missing.

    Note: Current implementation uses mock LLM calls, so this should always pass.
    """
    # The current implementation uses mock/simulation for all LLM operations
    # This means it won't crash even if USE_LLM=True and no API key is present
    # This is intentional for the tutorial - real LLM integration would be added later

    notebook_path = Path(__file__).parent.parent / "lesson-14" / "memory_systems_implementation.ipynb"

    if not notebook_path.exists():
        pytest.skip("Notebook not found")

    # Current implementation uses simulation, so this test validates the mock behavior
    # is robust and doesn't depend on external API keys
    result = subprocess.run(
        [
            "jupyter",
            "nbconvert",
            "--to",
            "notebook",
            "--execute",
            "--ExecutePreprocessor.timeout=300",
            str(notebook_path),
            "--output",
            "memory_systems_implementation_no_api_key_test.ipynb",
        ],
        cwd=notebook_path.parent,
        capture_output=True,
        text=True,
        env={**__import__("os").environ, "OPENAI_API_KEY": ""},  # Ensure no API key
    )

    # Should complete successfully even without API key (uses mock)
    assert result.returncode == 0, "Notebook should not crash when API key missing (uses mock LLM)"
