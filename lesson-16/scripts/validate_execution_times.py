#!/usr/bin/env python3
"""Validate notebook execution times for Lesson 16.

Per Task 5.10 requirements:
- Notebooks 08-12, 15: <5 min execution
- Notebooks 13-14: <10 min execution

Uses `jupyter nbconvert --execute` with timeout.
"""

import subprocess
import time
from pathlib import Path


# Expected execution time limits
NOTEBOOK_TIME_LIMITS = {
    "08_sequential_orchestration_baseline.ipynb": 300,  # 5 min
    "09_hierarchical_delegation_pattern.ipynb": 300,
    "10_iterative_refinement_react.ipynb": 300,
    "11_state_machine_orchestration.ipynb": 300,
    "12_voting_ensemble_pattern.ipynb": 300,
    "13_reliability_framework_implementation.ipynb": 600,  # 10 min
    "14_agentarch_benchmark_reproduction.ipynb": 600,  # 10 min (cached mode)
    "15_production_deployment_tutorial.ipynb": 300,  # 5 min
}


def validate_notebook_execution(notebook_path: Path, timeout: int) -> dict:
    """Execute notebook and measure time.

    Args:
        notebook_path: Path to notebook
        timeout: Timeout in seconds

    Returns:
        Result dict with status, execution_time, and error (if any)
    """
    print(f"\n{'='*80}")
    print(f"Validating: {notebook_path.name}")
    print(f"Time limit: {timeout}s ({timeout/60:.1f} min)")
    print(f"{'='*80}")

    start_time = time.time()

    try:
        # Execute notebook with timeout
        result = subprocess.run(
            [
                "jupyter",
                "nbconvert",
                "--to",
                "notebook",
                "--execute",
                str(notebook_path),
                "--output",
                f"/tmp/{notebook_path.stem}_executed.ipynb",
                f"--ExecutePreprocessor.timeout={timeout}",
            ],
            capture_output=True,
            text=True,
            timeout=timeout + 30,  # Add buffer for subprocess
        )

        execution_time = time.time() - start_time

        if result.returncode == 0:
            status = "✅ PASS" if execution_time < timeout else "⚠️ SLOW"
            print(f"\n{status}: Executed in {execution_time:.1f}s / {timeout}s")
            return {
                "notebook": notebook_path.name,
                "status": "pass" if execution_time < timeout else "slow",
                "execution_time": execution_time,
                "time_limit": timeout,
                "error": None,
            }
        else:
            print(f"\n❌ FAIL: Execution failed")
            print(f"   Error: {result.stderr[:500]}")
            return {
                "notebook": notebook_path.name,
                "status": "fail",
                "execution_time": execution_time,
                "time_limit": timeout,
                "error": result.stderr[:500],
            }

    except subprocess.TimeoutExpired:
        execution_time = time.time() - start_time
        print(f"\n❌ TIMEOUT: Exceeded {timeout}s limit ({execution_time:.1f}s)")
        return {
            "notebook": notebook_path.name,
            "status": "timeout",
            "execution_time": execution_time,
            "time_limit": timeout,
            "error": f"Timeout after {timeout}s",
        }
    except Exception as e:
        execution_time = time.time() - start_time
        print(f"\n❌ ERROR: {e}")
        return {
            "notebook": notebook_path.name,
            "status": "error",
            "execution_time": execution_time,
            "time_limit": timeout,
            "error": str(e),
        }


def main() -> None:
    """Validate all notebook execution times."""
    notebooks_dir = Path(__file__).parent.parent / "notebooks"

    if not notebooks_dir.exists():
        print(f"❌ Notebooks directory not found: {notebooks_dir}")
        return

    print("\n" + "="*80)
    print("NOTEBOOK EXECUTION TIME VALIDATION")
    print("="*80)
    print("\nTarget execution times:")
    print("  - Notebooks 08-12, 15: <5 minutes")
    print("  - Notebooks 13-14: <10 minutes (with cached results)")
    print("\nNote: This will execute all notebooks. May take 30-60 minutes total.")
    print("="*80)

    results = []
    total_time = 0

    for notebook_name, timeout in NOTEBOOK_TIME_LIMITS.items():
        notebook_path = notebooks_dir / notebook_name

        if not notebook_path.exists():
            print(f"\n⚠️ Notebook not found: {notebook_name}, skipping...")
            continue

        result = validate_notebook_execution(notebook_path, timeout)
        results.append(result)
        total_time += result["execution_time"]

    # Summary
    print("\n" + "="*80)
    print("EXECUTION TIME VALIDATION SUMMARY")
    print("="*80)
    print(f"\nTotal execution time: {total_time:.1f}s ({total_time/60:.1f} min)")
    print(f"Notebooks tested: {len(results)}\n")

    # Status breakdown
    pass_count = sum(1 for r in results if r["status"] == "pass")
    slow_count = sum(1 for r in results if r["status"] == "slow")
    fail_count = sum(1 for r in results if r["status"] == "fail")
    timeout_count = sum(1 for r in results if r["status"] == "timeout")
    error_count = sum(1 for r in results if r["status"] == "error")

    print(f"✅ Pass: {pass_count}")
    print(f"⚠️ Slow (but executed): {slow_count}")
    print(f"❌ Fail: {fail_count}")
    print(f"❌ Timeout: {timeout_count}")
    print(f"❌ Error: {error_count}")

    # Detailed results
    print("\nDetailed results:")
    print(f"{'Notebook':<50} {'Time':>10} {'Limit':>10} {'Status':>10}")
    print("-" * 80)

    for r in results:
        time_str = f"{r['execution_time']:.1f}s"
        limit_str = f"{r['time_limit']}s"
        status_str = r['status'].upper()
        print(f"{r['notebook']:<50} {time_str:>10} {limit_str:>10} {status_str:>10}")

    # Overall validation
    all_passed = all(r["status"] in ["pass", "slow"] for r in results)

    print("\n" + "="*80)
    if all_passed:
        print("🎉 ALL NOTEBOOKS EXECUTED SUCCESSFULLY!")
        if slow_count > 0:
            print(f"   ⚠️ {slow_count} notebook(s) exceeded time limit but completed")
    else:
        print(f"⚠️ VALIDATION INCOMPLETE: {fail_count + timeout_count + error_count} notebook(s) failed")
    print("="*80)


if __name__ == "__main__":
    main()
