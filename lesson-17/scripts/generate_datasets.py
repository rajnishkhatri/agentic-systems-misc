"""Master script to generate all synthetic datasets for Lesson 17.

Generates:
- pii_examples_50.json (50 PII detection examples)
- agent_metadata_10.json (10 agent profiles)
- workflows/ (5 multi-agent workflow traces)
- research_workflows/ (10 research workflow artifacts)
- parameter_substitutions_20.json (20 parameter change events)
- DATASET_SUMMARY.json (metadata for all datasets)

Usage:
    python generate_datasets.py [--seed SEED] [--output-dir DIR]

Example:
    python lesson-17/scripts/generate_datasets.py --seed 42
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import UTC, datetime
from pathlib import Path

# Add lesson-17 to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.generators.agent_metadata import generate_agent_metadata
from scripts.generators.parameter_logs import generate_parameter_logs
from scripts.generators.pii_examples import generate_pii_examples
from scripts.generators.research_workflows import generate_research_workflows
from scripts.generators.workflow_traces import generate_workflow_traces


def save_json(data: list | dict, path: Path, description: str) -> int:
    """Save data to JSON file and return file size.

    Args:
        data: Data to save
        path: Output file path
        description: Description for logging

    Returns:
        File size in bytes
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        json.dump(data, f, indent=2, default=str)

    size = path.stat().st_size
    print(f"  ✓ {description}: {path.name} ({size:,} bytes)")
    return size


def main() -> None:
    """Generate all datasets and save to data/ directory."""
    parser = argparse.ArgumentParser(
        description="Generate synthetic datasets for Lesson 17"
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Random seed for reproducibility (default: 42)",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default=None,
        help="Output directory (default: lesson-17/data/)",
    )
    args = parser.parse_args()

    # Setup paths
    if args.output_dir:
        data_dir = Path(args.output_dir)
    else:
        data_dir = Path(__file__).parent.parent / "data"

    data_dir.mkdir(parents=True, exist_ok=True)

    print("=" * 80)
    print("Lesson 17: Generating Explainability Datasets")
    print(f"Output directory: {data_dir}")
    print(f"Random seed: {args.seed}")
    print("=" * 80)

    # Track statistics for summary
    stats = {
        "generation_date": datetime.now(UTC).isoformat(),
        "version": "1.0",
        "schema_version": "1.0",
        "seed": args.seed,
        "datasets": {},
    }

    # ==========================================
    # P0 Critical Priority Datasets
    # ==========================================
    print("\n[P0 Critical Priority]")

    # 1. PII Examples (50)
    print("\n[1/5] Generating pii_examples_50.json...")
    pii_examples = generate_pii_examples(count=50, seed=args.seed)
    pii_path = data_dir / "pii_examples_50.json"
    pii_size = save_json(pii_examples, pii_path, "PII examples")

    # Count PII types
    pii_type_counts: dict[str, int] = {}
    for example in pii_examples:
        for pii_type in example.get("pii_types", []):
            pii_type_counts[pii_type] = pii_type_counts.get(pii_type, 0) + 1

    stats["datasets"]["pii_examples"] = {
        "count": len(pii_examples),
        "file_size_bytes": pii_size,
        "pii_type_distribution": pii_type_counts,
        "examples_with_pii": sum(1 for e in pii_examples if e.get("contains_pii", False)),
    }

    # 2. Agent Metadata (10)
    print("\n[2/5] Generating agent_metadata_10.json...")
    agent_metadata = generate_agent_metadata(count=10, seed=args.seed)
    agent_path = data_dir / "agent_metadata_10.json"
    agent_size = save_json(agent_metadata, agent_path, "Agent metadata")

    # Count capabilities and policies
    total_capabilities = sum(len(a.get("capabilities", [])) for a in agent_metadata)
    total_policies = sum(len(a.get("policies", [])) for a in agent_metadata)

    stats["datasets"]["agent_metadata"] = {
        "count": len(agent_metadata),
        "file_size_bytes": agent_size,
        "total_capabilities": total_capabilities,
        "total_policies": total_policies,
        "agents": [a["agent_id"] for a in agent_metadata],
    }

    # 3. Workflow Traces (5)
    print("\n[3/5] Generating workflow traces...")
    workflow_traces = generate_workflow_traces(count=5, seed=args.seed)
    workflows_dir = data_dir / "workflows"
    workflows_dir.mkdir(parents=True, exist_ok=True)

    workflow_stats = []
    total_workflow_size = 0
    for trace in workflow_traces:
        workflow_id = trace["workflow_id"]
        filename = f"{trace['workflow_type']}_trace.json"
        trace_path = workflows_dir / filename
        size = save_json(trace, trace_path, f"Workflow: {trace['workflow_type']}")
        total_workflow_size += size

        workflow_stats.append({
            "workflow_id": workflow_id,
            "workflow_type": trace["workflow_type"],
            "outcome": trace["outcome"]["status"],
            "agents_count": len(trace.get("collaborators", [])),
            "events_count": len(trace.get("execution_trace", {}).get("events", [])),
        })

    stats["datasets"]["workflow_traces"] = {
        "count": len(workflow_traces),
        "total_file_size_bytes": total_workflow_size,
        "outcome_distribution": {
            "success": sum(1 for w in workflow_stats if w["outcome"] == "success"),
            "failed": sum(1 for w in workflow_stats if w["outcome"] == "failed"),
            "pending": sum(1 for w in workflow_stats if "pending" in w["outcome"]),
            "manual_review": sum(1 for w in workflow_stats if "manual" in w["outcome"]),
        },
        "workflows": workflow_stats,
    }

    # ==========================================
    # P1 High Priority Datasets
    # ==========================================
    print("\n[P1 High Priority]")

    # 4. Research Workflows (10)
    print("\n[4/5] Generating research workflows...")
    research_workflows = generate_research_workflows(count=10, seed=args.seed)
    research_dir = data_dir / "research_workflows"
    research_dir.mkdir(parents=True, exist_ok=True)

    research_stats = []
    total_research_size = 0
    for workflow in research_workflows:
        workflow_id = workflow["workflow_id"]
        filename = f"{workflow_id}.json"
        workflow_path = research_dir / filename
        size = save_json(workflow, workflow_path, f"Research: {workflow_id}")
        total_research_size += size

        research_stats.append({
            "workflow_id": workflow_id,
            "topic": workflow["research_topic"],
            "status": workflow["final_status"],
            "phases_count": len(workflow.get("phases", [])),
            "decisions_count": len(workflow.get("decisions", [])),
            "artifacts_count": len(workflow.get("artifacts", [])),
        })

    stats["datasets"]["research_workflows"] = {
        "count": len(research_workflows),
        "total_file_size_bytes": total_research_size,
        "status_distribution": {
            "completed": sum(1 for w in research_stats if w["status"] == "completed"),
            "failed": sum(1 for w in research_stats if w["status"] == "failed"),
        },
        "total_decisions": sum(w["decisions_count"] for w in research_stats),
        "total_artifacts": sum(w["artifacts_count"] for w in research_stats),
        "workflows": research_stats,
    }

    # 5. Parameter Substitution Logs (20)
    print("\n[5/5] Generating parameter_substitutions_20.json...")
    parameter_logs = generate_parameter_logs(count=20, seed=args.seed)
    params_path = data_dir / "parameter_substitutions_20.json"
    params_size = save_json(parameter_logs, params_path, "Parameter logs")

    # Count by parameter name and impact
    param_name_counts: dict[str, int] = {}
    impact_counts: dict[str, int] = {}
    for log in parameter_logs:
        param_name = log.get("parameter_name", "unknown")
        param_name_counts[param_name] = param_name_counts.get(param_name, 0) + 1

        # Determine impact type from success rate delta
        impact = log.get("impact", {})
        delta = impact.get("success_rate_delta", 0)
        if delta > 0.01:
            impact_type = "positive"
        elif delta < -0.01:
            impact_type = "negative"
        else:
            impact_type = "neutral"
        impact_counts[impact_type] = impact_counts.get(impact_type, 0) + 1

    stats["datasets"]["parameter_substitutions"] = {
        "count": len(parameter_logs),
        "file_size_bytes": params_size,
        "parameter_distribution": param_name_counts,
        "impact_distribution": impact_counts,
    }

    # ==========================================
    # Generate DATASET_SUMMARY.json
    # ==========================================
    print("\n[Summary]")
    summary_path = data_dir / "DATASET_SUMMARY.json"
    summary_size = save_json(stats, summary_path, "Dataset summary")

    # Calculate totals
    total_records = (
        stats["datasets"]["pii_examples"]["count"]
        + stats["datasets"]["agent_metadata"]["count"]
        + stats["datasets"]["workflow_traces"]["count"]
        + stats["datasets"]["research_workflows"]["count"]
        + stats["datasets"]["parameter_substitutions"]["count"]
    )
    total_bytes = (
        stats["datasets"]["pii_examples"]["file_size_bytes"]
        + stats["datasets"]["agent_metadata"]["file_size_bytes"]
        + stats["datasets"]["workflow_traces"]["total_file_size_bytes"]
        + stats["datasets"]["research_workflows"]["total_file_size_bytes"]
        + stats["datasets"]["parameter_substitutions"]["file_size_bytes"]
        + summary_size
    )

    print("\n" + "=" * 80)
    print("Dataset generation complete!")
    print("=" * 80)
    print(f"\nTotal records generated: {total_records}")
    print(f"Total size: {total_bytes:,} bytes ({total_bytes / 1024:.1f} KB)")
    print(f"\nOutput directory: {data_dir}")
    print("\nGenerated files:")
    print("  - pii_examples_50.json")
    print("  - agent_metadata_10.json")
    print("  - workflows/ (5 files)")
    print("  - research_workflows/ (10 files)")
    print("  - parameter_substitutions_20.json")
    print("  - DATASET_SUMMARY.json")


if __name__ == "__main__":
    main()

