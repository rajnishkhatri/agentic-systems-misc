"""Generate comparison report between V8-RAG and V9-RAG classifiers.

Analyzes:
- Accuracy comparison
- Confidence calibration impact
- RAG hit rates and correlation with accuracy
- Category-level breakdown
"""

import json
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, List, Optional

project_root = Path(__file__).parent.parent


def load_trace_results(version: str) -> Optional[List[Dict[str, Any]]]:
    """Load trace results for a given version."""
    if version == "v8":
        path = project_root / "qualitative" / "phase1" / "natural_language_trace_results_v8_rag.json"
        if path.exists():
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
    elif version == "v9":
        path = project_root / "qualitative" / "phase1" / "natural_language_trace_results_v9_rag.json"
        if path.exists():
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
                # V9 wraps results in an object
                return data.get("results", data) if isinstance(data, dict) else data
    return None


def calculate_metrics(results: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Calculate evaluation metrics from results."""
    total = len(results)
    passed = sum(1 for r in results if r.get("status") == "PASS")
    failed = sum(1 for r in results if r.get("status") == "FAIL")
    errors = sum(1 for r in results if r.get("status") == "ERROR")

    # Category breakdown
    category_stats = defaultdict(lambda: {"correct": 0, "total": 0})
    for r in results:
        if r.get("status") in ["PASS", "FAIL"]:
            expected = r.get("case", {}).get("expected_category", "unknown")
            category_stats[expected]["total"] += 1
            if r.get("status") == "PASS":
                category_stats[expected]["correct"] += 1

    # Confidence stats
    confidences = []
    for r in results:
        if r.get("status") in ["PASS", "FAIL"]:
            conf = r.get("result", {}).get("confidence")
            if conf is None:
                conf = r.get("result", {}).get("adjusted_confidence")
            if conf is not None:
                confidences.append({
                    "value": conf,
                    "correct": r.get("status") == "PASS"
                })

    avg_confidence = sum(c["value"] for c in confidences) / len(confidences) if confidences else 0
    correct_conf = [c["value"] for c in confidences if c["correct"]]
    incorrect_conf = [c["value"] for c in confidences if not c["correct"]]

    return {
        "total": total,
        "passed": passed,
        "failed": failed,
        "errors": errors,
        "accuracy": passed / total if total > 0 else 0,
        "category_stats": dict(category_stats),
        "avg_confidence": avg_confidence,
        "avg_confidence_correct": sum(correct_conf) / len(correct_conf) if correct_conf else 0,
        "avg_confidence_incorrect": sum(incorrect_conf) / len(incorrect_conf) if incorrect_conf else 0,
    }


def analyze_v9_rag_metrics(results: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Analyze V9-specific RAG metrics."""
    rag_enabled_cases = 0
    total_precedents = 0
    total_similarity = 0
    high_conf_matches = 0
    precedent_agreements = 0
    precedent_disagreements = 0
    adjustments = []
    diversity_warnings = 0

    accuracy_by_rag = {"with_rag": {"correct": 0, "total": 0}, "without_rag": {"correct": 0, "total": 0}}
    accuracy_by_agreement = {"agree": {"correct": 0, "total": 0}, "disagree": {"correct": 0, "total": 0}}

    for r in results:
        if r.get("status") not in ["PASS", "FAIL"]:
            continue

        is_correct = r.get("status") == "PASS"
        rag_metrics = r.get("rag_metrics", {})

        if rag_metrics.get("enabled"):
            rag_enabled_cases += 1
            total_precedents += rag_metrics.get("precedents_retrieved", 0)
            total_similarity += rag_metrics.get("top_similarity", 0)
            if rag_metrics.get("high_confidence_match"):
                high_conf_matches += 1

            accuracy_by_rag["with_rag"]["total"] += 1
            if is_correct:
                accuracy_by_rag["with_rag"]["correct"] += 1

            prec_agreement = r.get("precedent_agreement", False)
            if prec_agreement:
                precedent_agreements += 1
                accuracy_by_agreement["agree"]["total"] += 1
                if is_correct:
                    accuracy_by_agreement["agree"]["correct"] += 1
            else:
                precedent_disagreements += 1
                accuracy_by_agreement["disagree"]["total"] += 1
                if is_correct:
                    accuracy_by_agreement["disagree"]["correct"] += 1
        else:
            accuracy_by_rag["without_rag"]["total"] += 1
            if is_correct:
                accuracy_by_rag["without_rag"]["correct"] += 1

        if r.get("precedent_diversity", {}).get("warning"):
            diversity_warnings += 1

        adj = r.get("result", {}).get("confidence_adjustment", 0)
        if adj != 0:
            adjustments.append(adj)

    return {
        "rag_enabled_cases": rag_enabled_cases,
        "avg_precedents": total_precedents / rag_enabled_cases if rag_enabled_cases else 0,
        "avg_top_similarity": total_similarity / rag_enabled_cases if rag_enabled_cases else 0,
        "high_confidence_matches": high_conf_matches,
        "precedent_agreements": precedent_agreements,
        "precedent_disagreements": precedent_disagreements,
        "diversity_warnings": diversity_warnings,
        "adjustment_count": len(adjustments),
        "avg_adjustment": sum(adjustments) / len(adjustments) if adjustments else 0,
        "accuracy_with_rag": accuracy_by_rag["with_rag"]["correct"] / accuracy_by_rag["with_rag"]["total"] if accuracy_by_rag["with_rag"]["total"] else 0,
        "accuracy_without_rag": accuracy_by_rag["without_rag"]["correct"] / accuracy_by_rag["without_rag"]["total"] if accuracy_by_rag["without_rag"]["total"] else 0,
        "accuracy_when_agree": accuracy_by_agreement["agree"]["correct"] / accuracy_by_agreement["agree"]["total"] if accuracy_by_agreement["agree"]["total"] else 0,
        "accuracy_when_disagree": accuracy_by_agreement["disagree"]["correct"] / accuracy_by_agreement["disagree"]["total"] if accuracy_by_agreement["disagree"]["total"] else 0,
    }


def generate_report() -> None:
    """Generate V8 vs V9 comparison report."""
    v8_results = load_trace_results("v8")
    v9_results = load_trace_results("v9")

    if not v8_results:
        print("V8 trace results not found. Run evaluate_v8_rag_trace.py first.")
        return

    if not v9_results:
        print("V9 trace results not found. Run evaluate_v9_rag_trace.py first.")
        return

    v8_metrics = calculate_metrics(v8_results)
    v9_metrics = calculate_metrics(v9_results)
    v9_rag = analyze_v9_rag_metrics(v9_results)

    print("=" * 70)
    print("V9-RAG vs V8-RAG Comparison Report")
    print("=" * 70)

    print("\n## Overall Accuracy")
    print("-" * 40)
    print(f"V8-RAG: {v8_metrics['passed']}/{v8_metrics['total']} ({v8_metrics['accuracy']*100:.1f}%)")
    print(f"V9-RAG: {v9_metrics['passed']}/{v9_metrics['total']} ({v9_metrics['accuracy']*100:.1f}%)")

    accuracy_delta = (v9_metrics['accuracy'] - v8_metrics['accuracy']) * 100
    delta_sign = "+" if accuracy_delta >= 0 else ""
    print(f"Delta: {delta_sign}{accuracy_delta:.1f}%")

    print("\n## Confidence Analysis")
    print("-" * 40)
    print(f"V8 Avg Confidence: {v8_metrics['avg_confidence']:.3f}")
    print(f"  - Correct predictions: {v8_metrics['avg_confidence_correct']:.3f}")
    print(f"  - Incorrect predictions: {v8_metrics['avg_confidence_incorrect']:.3f}")
    print(f"V9 Avg Confidence: {v9_metrics['avg_confidence']:.3f}")
    print(f"  - Correct predictions: {v9_metrics['avg_confidence_correct']:.3f}")
    print(f"  - Incorrect predictions: {v9_metrics['avg_confidence_incorrect']:.3f}")

    # Calibration improvement = larger gap between correct and incorrect
    v8_gap = v8_metrics['avg_confidence_correct'] - v8_metrics['avg_confidence_incorrect']
    v9_gap = v9_metrics['avg_confidence_correct'] - v9_metrics['avg_confidence_incorrect']
    print("\nCalibration (correct - incorrect):")
    print(f"  V8: {v8_gap:.3f}")
    print(f"  V9: {v9_gap:.3f}")

    print("\n## V9 RAG Metrics")
    print("-" * 40)
    print(f"Cases with RAG: {v9_rag['rag_enabled_cases']}")
    print(f"Avg precedents retrieved: {v9_rag['avg_precedents']:.2f}")
    print(f"Avg top similarity: {v9_rag['avg_top_similarity']:.3f}")
    print(f"High confidence matches: {v9_rag['high_confidence_matches']}")
    print(f"Diversity warnings: {v9_rag['diversity_warnings']}")

    print("\n## V9 Confidence Calibration Impact")
    print("-" * 40)
    print(f"Adjustments made: {v9_rag['adjustment_count']}")
    print(f"Avg adjustment: {v9_rag['avg_adjustment']:+.4f}")

    print("\n## V9 RAG Correlation with Accuracy")
    print("-" * 40)
    print(f"Accuracy WITH RAG: {v9_rag['accuracy_with_rag']*100:.1f}%")
    print(f"Accuracy WITHOUT RAG: {v9_rag['accuracy_without_rag']*100:.1f}%")
    print(f"Accuracy when precedent AGREES: {v9_rag['accuracy_when_agree']*100:.1f}%")
    print(f"Accuracy when precedent DISAGREES: {v9_rag['accuracy_when_disagree']*100:.1f}%")

    print("\n## Category-Level Comparison")
    print("-" * 40)

    all_categories = set(v8_metrics['category_stats'].keys()) | set(v9_metrics['category_stats'].keys())
    for cat in sorted(all_categories):
        v8_cat = v8_metrics['category_stats'].get(cat, {"correct": 0, "total": 0})
        v9_cat = v9_metrics['category_stats'].get(cat, {"correct": 0, "total": 0})

        v8_acc = v8_cat['correct'] / v8_cat['total'] * 100 if v8_cat['total'] else 0
        v9_acc = v9_cat['correct'] / v9_cat['total'] * 100 if v9_cat['total'] else 0

        print(f"{cat}:")
        print(f"  V8: {v8_cat['correct']}/{v8_cat['total']} ({v8_acc:.0f}%)")
        print(f"  V9: {v9_cat['correct']}/{v9_cat['total']} ({v9_acc:.0f}%)")

    print("\n" + "=" * 70)

    # Save report to file
    report_path = project_root / "qualitative" / "phase1" / "v9_vs_v8_comparison_report.json"
    report_data = {
        "v8_metrics": v8_metrics,
        "v9_metrics": v9_metrics,
        "v9_rag_analysis": v9_rag,
        "accuracy_delta": accuracy_delta,
        "calibration_improvement": v9_gap - v8_gap,
    }

    # Make category_stats JSON serializable
    report_data["v8_metrics"]["category_stats"] = dict(report_data["v8_metrics"]["category_stats"])
    report_data["v9_metrics"]["category_stats"] = dict(report_data["v9_metrics"]["category_stats"])

    with open(report_path, "w") as f:
        json.dump(report_data, f, indent=2)

    print(f"Report saved to {report_path}")


if __name__ == "__main__":
    generate_report()
