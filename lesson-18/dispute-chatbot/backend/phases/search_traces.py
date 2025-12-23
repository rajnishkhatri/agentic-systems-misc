#!/usr/bin/env python3
"""
Search and analyze JSONL trace files from DSPy distillation and prompt tuning.

Usage:
    python search_traces.py --file teacher_trace_log.jsonl --status accepted
    python search_traces.py --file fine_tuning_dataset.jsonl --category fraudulent
    python search_traces.py --file teacher_trace_log.jsonl --search "Reason Code Group"
    python search_traces.py --file teacher_trace_log.jsonl --stats
"""

import json
import argparse
from pathlib import Path
from typing import Dict, Any, List, Optional
from collections import Counter

BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "distillation_data"

TRACE_FILES = {
    "teacher": DATA_DIR / "teacher_trace_log.jsonl",
    "fine_tuning": DATA_DIR / "fine_tuning_dataset.jsonl",
    "student_eval": DATA_DIR / "student_evaluation_log.jsonl",
}


def load_jsonl(filepath: Path) -> List[Dict[str, Any]]:
    """Load JSONL file and return list of JSON objects."""
    if not filepath.exists():
        print(f"File not found: {filepath}")
        return []
    
    traces = []
    with open(filepath, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                traces.append(json.loads(line))
            except json.JSONDecodeError as e:
                print(f"Warning: Failed to parse line {line_num} in {filepath}: {e}")
    
    return traces


def search_by_status(traces: List[Dict], status: str) -> List[Dict]:
    """Filter traces by status (accepted, rejected, parse_error)."""
    return [t for t in traces if t.get("status") == status]


def search_by_category(traces: List[Dict], category: str) -> List[Dict]:
    """Filter traces by category (works for teacher traces and fine-tuning dataset)."""
    results = []
    for trace in traces:
        # Check teacher_output category
        if "teacher_output" in trace:
            if trace["teacher_output"].get("category") == category:
                results.append(trace)
        # Check ground_truth category
        elif "ground_truth" in trace:
            if trace["ground_truth"].get("category") == category:
                results.append(trace)
        # Check messages format (fine-tuning dataset)
        elif "messages" in trace:
            try:
                assistant_content = trace["messages"][-1]["content"]
                if isinstance(assistant_content, str):
                    parsed = json.loads(assistant_content)
                    if parsed.get("category") == category:
                        results.append(trace)
            except (json.JSONDecodeError, KeyError, IndexError):
                pass
        # Check predicted category (student eval)
        elif "predicted" in trace:
            if trace["predicted"] == category:
                results.append(trace)
    
    return results


def search_text(traces: List[Dict], query: str, case_sensitive: bool = False) -> List[Dict]:
    """Search for text in trace content."""
    query_lower = query if case_sensitive else query.lower()
    results = []
    
    for trace in traces:
        # Convert trace to string for searching
        trace_str = json.dumps(trace, ensure_ascii=False)
        if not case_sensitive:
            trace_str = trace_str.lower()
        
        if query_lower in trace_str:
            results.append(trace)
    
    return results


def get_statistics(traces: List[Dict], file_type: str) -> Dict[str, Any]:
    """Generate statistics about traces."""
    stats = {
        "total": len(traces),
    }
    
    if file_type == "teacher":
        # Status distribution
        statuses = Counter(t.get("status") for t in traces)
        stats["status"] = dict(statuses)
        
        # Category distribution (from accepted traces)
        accepted = [t for t in traces if t.get("status") == "accepted"]
        categories = Counter()
        for t in accepted:
            cat = t.get("teacher_output", {}).get("category")
            if cat:
                categories[cat] += 1
        stats["categories"] = dict(categories)
        
        # Rejection reasons
        rejected = [t for t in traces if t.get("status") == "rejected"]
        rejection_reasons = []
        for t in rejected:
            reasons = t.get("rejection_reasons", [])
            rejection_reasons.extend(reasons)
        stats["rejection_reasons"] = Counter(rejection_reasons)
        
    elif file_type == "fine_tuning":
        # Count examples
        stats["examples"] = len(traces)
        
        # Category distribution
        categories = Counter()
        for t in traces:
            try:
                assistant_content = t["messages"][-1]["content"]
                if isinstance(assistant_content, str):
                    parsed = json.loads(assistant_content)
                    cat = parsed.get("category")
                    if cat:
                        categories[cat] += 1
            except (json.JSONDecodeError, KeyError, IndexError):
                pass
        stats["categories"] = dict(categories)
        
    elif file_type == "student_eval":
        # Accuracy stats
        correct = sum(1 for t in traces if t.get("is_correct", False))
        stats["accuracy"] = correct / len(traces) if traces else 0
        stats["correct"] = correct
        stats["total"] = len(traces)
        
        # Category distribution
        predicted = Counter(t.get("predicted") for t in traces)
        ground_truth = Counter(t.get("ground_truth") for t in traces)
        stats["predicted_categories"] = dict(predicted)
        stats["ground_truth_categories"] = dict(ground_truth)
    
    return stats


def print_trace(trace: Dict, index: Optional[int] = None):
    """Pretty print a trace."""
    if index is not None:
        print(f"\n{'='*80}")
        print(f"Trace #{index + 1}")
        print(f"{'='*80}")
    
    # Print key fields
    if "dispute_id" in trace:
        print(f"Dispute ID: {trace['dispute_id']}")
    
    if "status" in trace:
        print(f"Status: {trace['status']}")
        if trace['status'] == "rejected" and "rejection_reasons" in trace:
            print(f"Rejection Reasons: {trace['rejection_reasons']}")
    
    if "teacher_output" in trace:
        output = trace["teacher_output"]
        print(f"Category: {output.get('category')}")
        if "synthesis" in output:
            reasoning = output["synthesis"].get("reasoning", "")
            if "Reason Code Group" in reasoning:
                print(f"Reason Code Group: Found in reasoning")
            print(f"Reasoning: {reasoning[:200]}..." if len(reasoning) > 200 else f"Reasoning: {reasoning}")
    
    if "ground_truth" in trace:
        gt = trace["ground_truth"]
        print(f"Ground Truth - Category: {gt.get('category')}, Group: {gt.get('group')}")
    
    if "predicted" in trace:
        print(f"Predicted: {trace['predicted']}")
        print(f"Ground Truth: {trace['ground_truth']}")
        print(f"Correct: {trace['is_correct']}")
        if "reasoning" in trace:
            print(f"Reasoning: {trace['reasoning'][:200]}..." if len(trace['reasoning']) > 200 else f"Reasoning: {trace['reasoning']}")


def main():
    parser = argparse.ArgumentParser(description="Search JSONL trace files from DSPy distillation")
    parser.add_argument(
        "--file",
        choices=["teacher", "fine_tuning", "student_eval"],
        required=True,
        help="Type of trace file to search"
    )
    parser.add_argument(
        "--status",
        choices=["accepted", "rejected", "parse_error"],
        help="Filter by status (for teacher traces)"
    )
    parser.add_argument(
        "--category",
        help="Filter by category"
    )
    parser.add_argument(
        "--search",
        help="Search for text in trace content"
    )
    parser.add_argument(
        "--stats",
        action="store_true",
        help="Show statistics about traces"
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=10,
        help="Limit number of results to display (default: 10)"
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Show all results (ignore limit)"
    )
    
    args = parser.parse_args()
    
    # Load traces
    filepath = TRACE_FILES[args.file]
    print(f"Loading traces from: {filepath}")
    traces = load_jsonl(filepath)
    
    if not traces:
        print("No traces found.")
        return
    
    print(f"Loaded {len(traces)} traces")
    
    # Apply filters
    filtered = traces
    
    if args.status:
        filtered = search_by_status(filtered, args.status)
        print(f"Filtered by status '{args.status}': {len(filtered)} traces")
    
    if args.category:
        filtered = search_by_category(filtered, args.category)
        print(f"Filtered by category '{args.category}': {len(filtered)} traces")
    
    if args.search:
        filtered = search_text(filtered, args.search)
        print(f"Filtered by search '{args.search}': {len(filtered)} traces")
    
    # Show statistics
    if args.stats:
        stats = get_statistics(traces, args.file)
        print("\n" + "="*80)
        print("STATISTICS")
        print("="*80)
        print(json.dumps(stats, indent=2))
        return
    
    # Display results
    if not filtered:
        print("No traces match the filters.")
        return
    
    print(f"\nShowing {len(filtered) if args.all else min(len(filtered), args.limit)} of {len(filtered)} matching traces:")
    
    display_count = len(filtered) if args.all else min(len(filtered), args.limit)
    for i, trace in enumerate(filtered[:display_count]):
        print_trace(trace, i)
    
    if len(filtered) > display_count:
        print(f"\n... and {len(filtered) - display_count} more traces (use --all to show all)")


if __name__ == "__main__":
    main()

