#!/usr/bin/env python3
"""
Generate HTML report for DSPy distillation traces.

Usage:
    python generate_trace_report.py --file teacher --output report.html
    python generate_trace_report.py --file fine_tuning --output fine_tuning_report.html
"""

import json
import argparse
from pathlib import Path
from typing import Dict, Any, List, Optional
from collections import Counter
from datetime import datetime
import html

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


def get_category_color(category: str) -> str:
    """Get color for category badge."""
    colors = {
        "fraudulent": "#dc3545",
        "general": "#17a2b8",
        "product_not_received": "#ffc107",
        "duplicate": "#fd7e14",
        "subscription_canceled": "#6f42c1",
        "product_unacceptable": "#e83e8c",
        "credit_not_processed": "#20c997",
        "unrecognized": "#6c757d",
    }
    return colors.get(category, "#6c757d")


def get_status_class(status: str) -> str:
    """Get CSS class for status."""
    status_map = {
        "accepted": "status-pass",
        "rejected": "status-fail",
        "parse_error": "status-error",
        "correct": "status-pass",
        "incorrect": "status-fail",
    }
    return status_map.get(status, "")


def get_row_class(status: str) -> str:
    """Get CSS class for table row."""
    status_map = {
        "accepted": "row-pass",
        "rejected": "row-fail",
        "parse_error": "row-error",
        "correct": "row-pass",
        "incorrect": "row-fail",
    }
    return status_map.get(status, "")


def extract_description(trace: Dict) -> str:
    """Extract dispute description from trace."""
    # For teacher traces
    if "messages" in trace:
        try:
            user_msg = trace["messages"][1]["content"]
            # Extract description from prompt
            if "Dispute Description to Analyze" in user_msg:
                parts = user_msg.split('"""')
                if len(parts) >= 2:
                    return parts[1].strip()
        except (KeyError, IndexError):
            pass
    
    # For student eval, might have description field
    if "description" in trace:
        return trace["description"]
    
    return "N/A"


def extract_branch_info(trace: Dict) -> Dict[str, Any]:
    """Extract branch analysis information from trace."""
    branch_info = {
        "branch_a": {"conclusion": "N/A", "evidence_for": [], "evidence_against": []},
        "branch_b": {"complaint_type": "N/A", "evidence": []},
        "branch_c": {"persona": "N/A", "evidence": []},
        "synthesis": {"agreement": 0.0, "rule": None, "reasoning": ""},
        "category": "N/A",
        "confidence": 0.0,
        "confidence_rationale": ""
    }
    
    # Try to get from teacher_output
    if "teacher_output" in trace:
        output = trace["teacher_output"]
        
        if "branch_a" in output:
            branch_info["branch_a"] = {
                "conclusion": output["branch_a"].get("conclusion", "N/A"),
                "evidence_for": output["branch_a"].get("evidence_for_acknowledgment", []),
                "evidence_against": output["branch_a"].get("evidence_against_acknowledgment", [])
            }
        
        if "branch_b" in output:
            branch_info["branch_b"] = {
                "complaint_type": output["branch_b"].get("complaint_type", "N/A"),
                "evidence": output["branch_b"].get("evidence", [])
            }
        
        if "branch_c" in output:
            branch_info["branch_c"] = {
                "persona": output["branch_c"].get("persona", "N/A"),
                "evidence": output["branch_c"].get("evidence", [])
            }
        
        if "synthesis" in output:
            synth = output["synthesis"]
            branch_info["synthesis"] = {
                "agreement": synth.get("branch_agreement", 0.0),
                "rule": synth.get("priority_rule_applied"),
                "reasoning": synth.get("reasoning", "")
            }
        
        branch_info["category"] = output.get("category", "N/A")
        branch_info["confidence"] = output.get("confidence", 0.0)
        branch_info["confidence_rationale"] = output.get("confidence_rationale", "")
    
    # Try to get from messages (fine-tuning format)
    elif "messages" in trace:
        try:
            assistant_content = trace["messages"][-1]["content"]
            if isinstance(assistant_content, str):
                parsed = json.loads(assistant_content)
                if "branch_a" in parsed:
                    branch_info["branch_a"] = {
                        "conclusion": parsed["branch_a"].get("conclusion", "N/A"),
                        "evidence_for": parsed["branch_a"].get("evidence_for_acknowledgment", []),
                        "evidence_against": parsed["branch_a"].get("evidence_against_acknowledgment", [])
                    }
                if "branch_b" in parsed:
                    branch_info["branch_b"] = {
                        "complaint_type": parsed["branch_b"].get("complaint_type", "N/A"),
                        "evidence": parsed["branch_b"].get("evidence", [])
                    }
                if "branch_c" in parsed:
                    branch_info["branch_c"] = {
                        "persona": parsed["branch_c"].get("persona", "N/A"),
                        "evidence": parsed["branch_c"].get("evidence", [])
                    }
                if "synthesis" in parsed:
                    synth = parsed["synthesis"]
                    branch_info["synthesis"] = {
                        "agreement": synth.get("branch_agreement", 0.0),
                        "rule": synth.get("priority_rule_applied"),
                        "reasoning": synth.get("reasoning", "")
                    }
                branch_info["category"] = parsed.get("category", "N/A")
                branch_info["confidence"] = parsed.get("confidence", 0.0)
                branch_info["confidence_rationale"] = parsed.get("confidence_rationale", "")
        except (json.JSONDecodeError, KeyError, IndexError):
            pass
    
    return branch_info


def load_training_data() -> Dict[str, str]:
    """Load training data and create mapping from dispute_id to description."""
    train_file = DATA_DIR / "distillation_train.json"
    description_map = {}
    
    if train_file.exists():
        try:
            with open(train_file, 'r', encoding='utf-8') as f:
                training_data = json.load(f)
                for item in training_data:
                    dispute_id = item.get("dispute_id")
                    description = item.get("description")
                    if dispute_id and description:
                        description_map[dispute_id] = description
        except Exception as e:
            print(f"Warning: Could not load training data: {e}")
    
    return description_map


def generate_teacher_report(traces: List[Dict], output_path: Path):
    """Generate HTML report for teacher traces."""
    
    # Load description mapping
    description_map = load_training_data()
    
    # Calculate statistics
    total = len(traces)
    status_counts = Counter(t.get("status") for t in traces)
    accepted = [t for t in traces if t.get("status") == "accepted"]
    rejected = [t for t in traces if t.get("status") == "rejected"]
    parse_errors = [t for t in traces if t.get("status") == "parse_error"]
    
    # Category distribution
    categories = Counter()
    for t in accepted:
        cat = t.get("teacher_output", {}).get("category")
        if cat:
            categories[cat] += 1
    
    # Rejection reasons
    rejection_reasons = Counter()
    for t in rejected:
        reasons = t.get("rejection_reasons", [])
        for reason in reasons:
            # Extract main reason (before colon if present)
            main_reason = reason.split(":")[0] if ":" in reason else reason
            rejection_reasons[main_reason] += 1
    
    acceptance_rate = (len(accepted) / total * 100) if total > 0 else 0
    
    # Generate HTML
    html_content = f"""<!DOCTYPE html>
<html>
<head>
    <title>DSPy Distillation Teacher Traces Report</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; color: #333; }}
        .container {{ max-width: 1400px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        h1, h2, h3 {{ color: #2c3e50; }}
        .subtitle {{ color: #6c757d; font-size: 14px; margin-top: -15px; margin-bottom: 20px; }}

        .dashboard {{ display: flex; gap: 20px; margin-bottom: 30px; flex-wrap: wrap; }}
        .card {{ flex: 1; min-width: 200px; background: #f8f9fa; padding: 20px; border-radius: 6px; border: 1px solid #e9ecef; }}
        .card-highlight {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; }}
        .card-highlight .stat-label {{ color: rgba(255,255,255,0.8); }}
        .stat-value {{ font-size: 24px; font-weight: bold; color: #2c3e50; }}
        .card-highlight .stat-value {{ color: white; }}
        .stat-label {{ color: #6c757d; font-size: 14px; text-transform: uppercase; letter-spacing: 0.5px; }}

        table {{ width: 100%; border-collapse: collapse; margin-top: 20px; font-size: 14px; }}
        th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #eee; }}
        th {{ background: #f8f9fa; font-weight: 600; color: #495057; position: sticky; top: 0; }}

        .status-pass {{ color: #28a745; font-weight: bold; }}
        .status-fail {{ color: #dc3545; font-weight: bold; }}
        .status-error {{ color: #fd7e14; font-weight: bold; }}

        .row-pass {{ background-color: #f8fff9; }}
        .row-fail {{ background-color: #fff8f8; cursor: pointer; }}
        .row-fail:hover {{ background-color: #ffeef0; }}
        .row-error {{ background-color: #fff5e6; cursor: pointer; }}
        .row-error:hover {{ background-color: #fff8e6; }}

        .trace-detail {{ display: none; background: #fafafa; padding: 20px; border-top: 1px solid #eee; }}

        .branch-analysis {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 15px; margin-bottom: 20px; }}
        .branch-card {{ background: #fff; padding: 15px; border-radius: 6px; border: 1px solid #e9ecef; }}
        .branch-card h4 {{ margin: 0 0 10px 0; font-size: 14px; color: #495057; display: flex; align-items: center; gap: 8px; }}
        .branch-icon {{ width: 24px; height: 24px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 12px; font-weight: bold; color: white; }}
        .branch-a {{ background: #17a2b8; }}
        .branch-b {{ background: #28a745; }}
        .branch-c {{ background: #fd7e14; }}
        .branch-conclusion {{ font-size: 16px; font-weight: bold; color: #2c3e50; margin-bottom: 8px; }}
        .branch-evidence {{ font-size: 12px; color: #6c757d; }}

        .synthesis-box {{ background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%); padding: 15px; border-radius: 6px; margin-bottom: 20px; }}
        .synthesis-box h4 {{ margin: 0 0 10px 0; }}
        .agreement-bar {{ height: 8px; background: #dee2e6; border-radius: 4px; overflow: hidden; margin: 10px 0; }}
        .agreement-fill {{ height: 100%; border-radius: 4px; transition: width 0.3s; }}
        .agreement-high {{ background: #28a745; }}
        .agreement-medium {{ background: #ffc107; }}
        .agreement-low {{ background: #dc3545; }}

        .trace-step {{ margin-bottom: 15px; border-left: 3px solid #dee2e6; padding-left: 15px; }}
        .trace-step h4 {{ margin: 0 0 10px 0; font-size: 16px; }}

        .prompt-box, .response-box {{ background: #fff; padding: 10px; border: 1px solid #eee; border-radius: 4px; font-family: monospace; white-space: pre-wrap; margin-top: 5px; font-size: 12px; max-height: 300px; overflow-y: auto; }}
        .label {{ font-weight: bold; font-size: 12px; color: #666; display: block; margin-bottom: 4px; margin-top: 10px; }}

        .filter-bar {{ margin-bottom: 20px; display: flex; gap: 10px; flex-wrap: wrap; }}
        .filter-btn {{ padding: 8px 16px; border: 1px solid #ddd; background: white; border-radius: 20px; cursor: pointer; font-size: 13px; }}
        .filter-btn.active {{ background: #2c3e50; color: white; border-color: #2c3e50; }}

        .diff-container {{ display: flex; gap: 20px; margin-bottom: 20px; }}
        .diff-col {{ flex: 1; background: #fff; padding: 15px; border-radius: 4px; border: 1px solid #eee; }}
        .diff-col h3 {{ margin-top: 0; font-size: 14px; color: #666; border-bottom: 1px solid #eee; padding-bottom: 5px; }}
        .mismatch {{ color: #dc3545; font-weight: bold; }}
        .match {{ color: #28a745; font-weight: bold; }}

        .category-badge {{ display: inline-block; padding: 2px 8px; border-radius: 4px; font-size: 11px; font-weight: bold; color: white; }}

        .legend {{ display: flex; gap: 20px; margin-bottom: 20px; font-size: 13px; }}
        .legend-item {{ display: flex; align-items: center; gap: 5px; }}
        .legend-dot {{ width: 12px; height: 12px; border-radius: 50%; }}
    </style>
    <script>
        function toggleTrace(id) {{
            const row = document.getElementById('trace-' + id);
            if (row.style.display === 'none') {{
                row.style.display = 'table-row';
            }} else {{
                row.style.display = 'none';
            }}
        }}

        function filterRows(type) {{
            const rows = document.querySelectorAll('.case-row');
            const traceRows = document.querySelectorAll('.trace-detail');

            traceRows.forEach(row => row.style.display = 'none');

            rows.forEach(row => {{
                if (type === 'all' || row.classList.contains(type)) {{
                    row.style.display = 'table-row';
                }} else {{
                    row.style.display = 'none';
                }}
            }});

            document.querySelectorAll('.filter-btn').forEach(btn => btn.classList.remove('active'));
            document.getElementById('btn-' + type).classList.add('active');
        }}
    </script>
</head>
<body>
    <div class="container">
        <h1>DSPy Distillation Teacher Traces Report</h1>
        <p class="subtitle">Teacher Model: Claude Opus 4.5 | Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>

        <div class="dashboard">
            <div class="card card-highlight">
                <div class="stat-value">{acceptance_rate:.1f}%</div>
                <div class="stat-label">Acceptance Rate</div>
                <div style="margin-top: 10px; font-size: 13px;">
                    {len(accepted)} / {total} Accepted
                </div>
            </div>
            <div class="card">
                <div class="stat-value">{len(accepted)}</div>
                <div class="stat-label">Accepted Traces</div>
            </div>
            <div class="card">
                <div class="stat-value">{len(rejected)}</div>
                <div class="stat-label">Rejected Traces</div>
            </div>
            <div class="card">
                <div class="stat-value">{len(parse_errors)}</div>
                <div class="stat-label">Parse Errors</div>
            </div>
        </div>

        <div class="legend">
            <div class="legend-item"><span class="legend-dot branch-a"></span> Branch A: Acknowledgment</div>
            <div class="legend-item"><span class="legend-dot branch-b"></span> Branch B: Complaint Type</div>
            <div class="legend-item"><span class="legend-dot branch-c"></span> Branch C: Persona</div>
        </div>

        <div class="filter-bar">
            <button id="btn-all" class="filter-btn active" onclick="filterRows('all')">All Traces ({total})</button>
            <button id="btn-status-pass" class="filter-btn" onclick="filterRows('status-pass')">Accepted ({len(accepted)})</button>
            <button id="btn-status-fail" class="filter-btn" onclick="filterRows('status-fail')">Rejected ({len(rejected)})</button>
            <button id="btn-status-error" class="filter-btn" onclick="filterRows('status-error')">Parse Errors ({len(parse_errors)})</button>
        </div>

        <table>
            <thead>
                <tr>
                    <th>ID</th>
                    <th>Status</th>
                    <th>Category</th>
                    <th>Ground Truth</th>
                    <th>Branches (A/B/C)</th>
                    <th>Conf.</th>
                    <th>Action</th>
                </tr>
            </thead>
            <tbody>
"""
    
    # Generate table rows
    for idx, trace in enumerate(traces):
        dispute_id = trace.get("dispute_id", f"trace_{idx}")
        status = trace.get("status", "unknown")
        status_class = get_status_class(status)
        row_class = get_row_class(status)
        
        # Get branch info
        branch_info = extract_branch_info(trace)
        category = branch_info["category"]
        confidence = branch_info["confidence"]
        
        # Ground truth
        gt = trace.get("ground_truth", {})
        gt_category = gt.get("category", "N/A")
        gt_group = gt.get("group", "N/A")
        
        # Branch summary
        branch_a_short = branch_info["branch_a"]["conclusion"][:3].upper() if branch_info["branch_a"]["conclusion"] != "N/A" else "N/A"
        branch_b_short = branch_info["branch_b"]["complaint_type"][:3].upper() if branch_info["branch_b"]["complaint_type"] != "N/A" else "N/A"
        branch_c_short = branch_info["branch_c"]["persona"][:3].upper() if branch_info["branch_c"]["persona"] != "N/A" else "N/A"
        branch_summary = f"{branch_a_short}/{branch_b_short}/{branch_c_short}"
        
        # Category match
        category_match = "match" if category == gt_category else "mismatch"
        category_display = f'<span class="{category_match}">{category}</span>' if category != "N/A" else "N/A"
        
        # Rejection reasons
        rejection_reasons = trace.get("rejection_reasons", [])
        rejection_display = "<br>".join(html.escape(str(r)) for r in rejection_reasons[:2])
        if len(rejection_reasons) > 2:
            rejection_display += f"<br>... and {len(rejection_reasons) - 2} more"
        
        # Get description
        description = description_map.get(dispute_id, "N/A")
        
        html_content += f"""
            <tr class="case-row {row_class} status-{status_class.replace('status-', '')}" onclick="toggleTrace({idx})">
                <td>{html.escape(dispute_id)}</td>
                <td class="{status_class}">{status.upper()}</td>
                <td>{category_display}</td>
                <td>{html.escape(gt_category)}</td>
                <td>{branch_summary}</td>
                <td>{confidence:.2f}</td>
                <td><button style="padding: 2px 8px; font-size: 12px;">View</button></td>
            </tr>
            <tr id="trace-{idx}" class="trace-detail" style="display: none;">
                <td colspan="7">
                    <div style="margin-bottom: 20px;">
                        <strong>Dispute ID:</strong> {html.escape(dispute_id)}<br>
                        <strong>Status:</strong> <span class="{status_class}">{status.upper()}</span><br>
                        {f'<strong>Rejection Reasons:</strong><br><div style="color: #dc3545; margin-top: 5px;">{rejection_display}</div>' if rejection_reasons else ''}
                    </div>
                    <div style="margin-bottom: 20px;">
                        <strong>Description:</strong><br>
                        <div style="background: #fff; padding: 10px; border: 1px solid #eee; margin-top: 5px;">{html.escape(description)}</div>
                    </div>
"""
        
        # Add branch analysis if available
        if branch_info["branch_a"]["conclusion"] != "N/A":
            agreement = branch_info["synthesis"]["agreement"]
            agreement_class = "agreement-high" if agreement >= 0.9 else "agreement-medium" if agreement >= 0.75 else "agreement-low"
            
            html_content += f"""
                    <h3>Tree-of-Thought Branch Analysis</h3>
                    <div class="branch-analysis">
                        <div class="branch-card">
                            <h4><span class="branch-icon branch-a">A</span> Transaction Acknowledgment</h4>
                            <div class="branch-conclusion">{html.escape(str(branch_info["branch_a"]["conclusion"]))}</div>
                            <div class="branch-evidence">
                                <strong>For:</strong> {", ".join(html.escape(str(e)) for e in branch_info["branch_a"]["evidence_for"][:3])}<br>
                                <strong>Against:</strong> {", ".join(html.escape(str(e)) for e in branch_info["branch_a"]["evidence_against"][:3])}
                            </div>
                        </div>
                        <div class="branch-card">
                            <h4><span class="branch-icon branch-b">B</span> Complaint Specifics</h4>
                            <div class="branch-conclusion">{html.escape(str(branch_info["branch_b"]["complaint_type"]))}</div>
                            <div class="branch-evidence">
                                <strong>Evidence:</strong> {", ".join(html.escape(str(e)) for e in branch_info["branch_b"]["evidence"][:3])}
                            </div>
                        </div>
                        <div class="branch-card">
                            <h4><span class="branch-icon branch-c">C</span> User Persona</h4>
                            <div class="branch-conclusion">{html.escape(str(branch_info["branch_c"]["persona"]))}</div>
                            <div class="branch-evidence">
                                <strong>Evidence:</strong> {", ".join(html.escape(str(e)) for e in branch_info["branch_c"]["evidence"][:3])}
                            </div>
                        </div>
                    </div>

                    <div class="synthesis-box">
                        <h4>Branch Synthesis</h4>
                        <div>
                            <strong>Agreement Score:</strong> {agreement:.2f}
                            <div class="agreement-bar">
                                <div class="agreement-fill {agreement_class}" style="width: {agreement * 100:.1f}%"></div>
                            </div>
                        </div>
                        <div><strong>Priority Rule Applied:</strong> {html.escape(str(branch_info["synthesis"]["rule"])) if branch_info["synthesis"]["rule"] else "None"}</div>
                        <div style="margin-top: 10px;"><strong>Reasoning:</strong><br>{html.escape(branch_info["synthesis"]["reasoning"][:500])}{"..." if len(branch_info["synthesis"]["reasoning"]) > 500 else ""}</div>
                    </div>
"""
        
        # Add comparison
        html_content += f"""
                    <div class="diff-container">
                        <div class="diff-col">
                            <h3>Ground Truth</h3>
                            <div>Category: {html.escape(gt_category)}</div>
                            <div>Group: {html.escape(str(gt_group))}</div>
                        </div>
                        <div class="diff-col">
                            <h3>Teacher Output</h3>
                            <div class="{category_match}">Category: {html.escape(category)}</div>
                            <div>Confidence: {confidence:.2f}</div>
                            <div style="margin-top: 10px;"><strong>Confidence Rationale:</strong><br>{html.escape(branch_info["confidence_rationale"][:300])}{"..." if len(branch_info["confidence_rationale"]) > 300 else ""}</div>
                        </div>
                    </div>
"""
        
        # Add raw trace data
        if "teacher_output" in trace:
            html_content += f"""
                    <h3>Raw Teacher Output</h3>
                    <div class="response-box">{html.escape(json.dumps(trace["teacher_output"], indent=2))}</div>
"""
        
        html_content += """
                </td>
            </tr>
"""
    
    html_content += """
            </tbody>
        </table>
    </div>
</body>
</html>
"""
    
    output_path.write_text(html_content, encoding='utf-8')
    print(f"Generated report: {output_path}")


def main():
    parser = argparse.ArgumentParser(description="Generate HTML report from JSONL traces")
    parser.add_argument(
        "--file",
        choices=["teacher", "fine_tuning", "student_eval"],
        required=True,
        help="Type of trace file to process"
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Output HTML file path"
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
    
    # Determine output path
    if args.output:
        output_path = args.output
    else:
        output_path = DATA_DIR / f"{args.file}_trace_report.html"
    
    # Generate report
    if args.file == "teacher":
        generate_teacher_report(traces, output_path)
    else:
        print(f"Report generation for {args.file} not yet implemented")
        print("Use --file teacher for now")


if __name__ == "__main__":
    main()

