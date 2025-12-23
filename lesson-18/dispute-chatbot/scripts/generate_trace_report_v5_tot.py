"""Generate HTML trace report for V5-ToT classification results.

This script generates an interactive HTML report comparing V5-ToT results
with V4 baseline, including branch analysis visualization.
"""

import json
import os
import sys
from collections import Counter
from pathlib import Path

# Configuration
project_root = Path(__file__).parent.parent
JSON_PATH = project_root / "qualitative" / "phase1" / "natural_language_trace_results_v5_tot.json"
V4_JSON_PATH = project_root / "qualitative" / "phase1" / "natural_language_trace_results_v4.json"
HTML_PATH = project_root / "qualitative" / "phase1" / "natural_language_report_v5_tot_trace.html"


def load_v4_results() -> dict:
    """Load V4 results for comparison."""
    v4_by_id = {}
    if V4_JSON_PATH.exists():
        with open(V4_JSON_PATH, "r") as f:
            v4_results = json.load(f)
            for r in v4_results:
                dispute_id = r["case"]["dispute_id"]
                v4_by_id[dispute_id] = {
                    "category": r["result"]["category"],
                    "status": r["status"],
                    "reasoning": r["result"].get("reasoning", ""),
                }
    return v4_by_id


def generate_report():
    """Generate the HTML trace report."""
    if not JSON_PATH.exists():
        print(f"Error: Results JSON not found at {JSON_PATH}")
        print("Run evaluate_v5_tot_trace.py first to generate results.")
        return

    with open(JSON_PATH, "r") as f:
        results = json.load(f)

    # Load V4 for comparison
    v4_by_id = load_v4_results()

    # Statistics
    total = len(results)
    passed = sum(1 for r in results if r.get("status") == "PASS")
    errors = sum(1 for r in results if r.get("status") == "ERROR")
    pass_rate = (passed / total * 100) if total > 0 else 0

    # Per-persona stats
    variation_stats = Counter()
    variation_totals = Counter()

    for r in results:
        if r.get("status") == "ERROR":
            continue
        var_type = r["case"].get("variation_type", "unknown")
        if var_type == "unknown":
            parts = r["case"]["dispute_id"].split("_")
            if len(parts) > 0:
                var_type = parts[-1]
        variation_totals[var_type] += 1
        if r.get("status") == "PASS":
            variation_stats[var_type] += 1

    # Branch conflict stats
    total_conflicts = sum(
        1 for r in results
        if r.get("branch_analysis") and r["branch_analysis"].get("conflict")
    )
    conflicts_resolved = sum(
        1 for r in results
        if r.get("branch_analysis") and r["branch_analysis"].get("conflict") and r["status"] == "PASS"
    )

    # V4 comparison
    v4_passed = sum(1 for r in v4_by_id.values() if r["status"] == "PASS") if v4_by_id else 0
    v4_total = len(v4_by_id) if v4_by_id else 0
    v4_rate = (v4_passed / v4_total * 100) if v4_total > 0 else 0

    # Calculate improvement
    improvement = pass_rate - v4_rate if v4_rate > 0 else 0
    improvement_class = "improvement-positive" if improvement > 0 else "improvement-negative" if improvement < 0 else ""

    # Get model used
    model_used = results[0].get("model", "unknown") if results else "unknown"

    # HTML Generation
    html = f"""<!DOCTYPE html>
<html>
<head>
    <title>Dispute Classification V5-ToT Trace Report</title>
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

        .improvement-positive {{ color: #28a745; }}
        .improvement-negative {{ color: #dc3545; }}

        table {{ width: 100%; border-collapse: collapse; margin-top: 20px; font-size: 14px; }}
        th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #eee; }}
        th {{ background: #f8f9fa; font-weight: 600; color: #495057; position: sticky; top: 0; }}

        .status-pass {{ color: #28a745; font-weight: bold; }}
        .status-fail {{ color: #dc3545; font-weight: bold; }}
        .status-error {{ color: #fd7e14; font-weight: bold; }}

        .row-pass {{ background-color: #f8fff9; }}
        .row-fail {{ background-color: #fff8f8; cursor: pointer; }}
        .row-fail:hover {{ background-color: #ffeef0; }}
        .row-error {{ background-color: #fff5e6; }}

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

        .conflict-badge {{ display: inline-block; padding: 2px 8px; border-radius: 4px; font-size: 11px; font-weight: bold; background: #dc3545; color: white; margin-left: 10px; }}
        .conflict-resolved {{ background: #28a745; }}

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

        .v4-comparison {{ background: #e9ecef; padding: 10px; border-radius: 4px; margin-top: 10px; font-size: 13px; }}
        .v4-comparison .improved {{ color: #28a745; }}
        .v4-comparison .regressed {{ color: #dc3545; }}
        .v4-comparison .same {{ color: #6c757d; }}

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

            // Hide all trace rows first
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

        function filterByPersona(persona) {{
            const rows = document.querySelectorAll('.case-row');
            const traceRows = document.querySelectorAll('.trace-detail');

            traceRows.forEach(row => row.style.display = 'none');

            rows.forEach(row => {{
                if (persona === 'all' || row.dataset.persona === persona) {{
                    row.style.display = 'table-row';
                }} else {{
                    row.style.display = 'none';
                }}
            }});

            document.querySelectorAll('.persona-btn').forEach(btn => btn.classList.remove('active'));
            event.target.classList.add('active');
        }}
    </script>
</head>
<body>
    <div class="container">
        <h1>Dispute Classification V5-ToT Trace Report</h1>
        <p class="subtitle">Tree-of-Thought Analysis with Branch Synthesis | Model: {model_used}</p>

        <div class="dashboard">
            <div class="card card-highlight">
                <div class="stat-value">{pass_rate:.1f}%</div>
                <div class="stat-label">V5-ToT Correction Rate</div>
                <div style="margin-top: 10px; font-size: 13px;">
                    {passed} / {total} Passed
                </div>
            </div>
            <div class="card">
                <div class="stat-value">{v4_rate:.1f}%</div>
                <div class="stat-label">V4 Baseline</div>
                <div style="margin-top: 10px; font-size: 13px; {improvement_class}">
                    {"+" if improvement > 0 else ""}{improvement:.1f}% vs V4
                </div>
            </div>
            <div class="card">
                <div class="stat-label">Performance by Persona</div>
                <div style="margin-top: 10px;">
    """

    for var_type, count in sorted(variation_totals.items()):
        var_pass = variation_stats[var_type]
        var_rate = (var_pass / count * 100) if count > 0 else 0
        html += f'<div><strong>{var_type.title()}:</strong> {var_rate:.1f}% ({var_pass}/{count})</div>'

    html += f"""
                </div>
            </div>
            <div class="card">
                <div class="stat-label">Branch Conflicts</div>
                <div style="margin-top: 10px;">
                    <div><strong>Detected:</strong> {total_conflicts}</div>
                    <div><strong>Resolved Correctly:</strong> {conflicts_resolved}</div>
                    {f'<div><strong>Resolution Rate:</strong> {conflicts_resolved/total_conflicts*100:.0f}%</div>' if total_conflicts > 0 else ''}
                </div>
            </div>
        </div>

        <div class="legend">
            <div class="legend-item"><span class="legend-dot branch-a"></span> Branch A: Acknowledgment</div>
            <div class="legend-item"><span class="legend-dot branch-b"></span> Branch B: Complaint Type</div>
            <div class="legend-item"><span class="legend-dot branch-c"></span> Branch C: Persona</div>
        </div>

        <div class="filter-bar">
            <button id="btn-all" class="filter-btn active" onclick="filterRows('all')">All Cases ({total})</button>
            <button id="btn-status-pass" class="filter-btn" onclick="filterRows('status-pass')">Passed ({passed})</button>
            <button id="btn-status-fail" class="filter-btn" onclick="filterRows('status-fail')">Failed ({total - passed - errors})</button>
            {f'<button id="btn-status-error" class="filter-btn" onclick="filterRows(\"status-error\")">Errors ({errors})</button>' if errors > 0 else ''}
        </div>

        <div class="filter-bar">
            <span style="padding: 8px 0; color: #6c757d;">By Persona:</span>
            <button class="filter-btn persona-btn active" onclick="filterByPersona('all')">All</button>
    """

    for var_type in sorted(variation_totals.keys()):
        html += f'<button class="filter-btn persona-btn" onclick="filterByPersona(\'{var_type}\')">{var_type.title()}</button>'

    html += """
        </div>

        <table>
            <thead>
                <tr>
                    <th>ID</th>
                    <th>Persona</th>
                    <th>Status</th>
                    <th>Expected</th>
                    <th>V5-ToT</th>
                    <th>V4</th>
                    <th>Branches (A/B/C)</th>
                    <th>Conf.</th>
                    <th>Action</th>
                </tr>
            </thead>
            <tbody>
    """

    for i, r in enumerate(results):
        case = r["case"]
        dispute_id = case["dispute_id"]

        # Determine persona
        persona = case.get("variation_type", "unknown")
        if persona == "unknown":
            parts = dispute_id.split("_")
            if len(parts) > 0:
                persona = parts[-1]

        status = r["status"]
        status_class = "status-pass" if status == "PASS" else "status-error" if status == "ERROR" else "status-fail"
        row_class = "row-pass" if status == "PASS" else "row-error" if status == "ERROR" else "row-fail"

        expected = case["expected_category"]
        actual = r["result"]["category"]
        confidence = r["result"].get("confidence", 0)

        # V4 comparison
        v4_data = v4_by_id.get(dispute_id, {})
        v4_category = v4_data.get("category", "N/A")
        v4_status = v4_data.get("status", "N/A")

        # Improvement indicator
        v5_correct = status == "PASS"
        v4_correct = v4_status == "PASS"
        if v5_correct and not v4_correct:
            v4_indicator = '<span class="improved">IMPROVED</span>'
        elif not v5_correct and v4_correct:
            v4_indicator = '<span class="regressed">REGRESSED</span>'
        else:
            v4_indicator = '<span class="same">SAME</span>'

        # Branch summary
        branch_a = "?"
        branch_b = "?"
        branch_c = "?"
        has_conflict = False

        if r.get("branch_analysis"):
            ba = r["branch_analysis"]
            branch_a = ba.get("branch_a", {}).get("conclusion", "?")[:3].upper()
            branch_b = ba.get("branch_b", {}).get("complaint_type", "?")[:3].upper()
            branch_c = ba.get("branch_c", {}).get("persona", "?")[:3].upper()
            has_conflict = ba.get("conflict") is not None

        conflict_badge = '<span class="conflict-badge">CONFLICT</span>' if has_conflict else ''

        actual_display = f'<span class="{"" if status == "PASS" else "mismatch"}">{actual}</span>'

        html += f"""
            <tr class="case-row {row_class} {status_class}" data-persona="{persona}" onclick="toggleTrace({i})">
                <td>{dispute_id}</td>
                <td>{persona}</td>
                <td class="{status_class}">{status}</td>
                <td>{expected}</td>
                <td>{actual_display}</td>
                <td>{v4_category}</td>
                <td>{branch_a}/{branch_b}/{branch_c}{conflict_badge}</td>
                <td>{confidence:.2f}</td>
                <td><button style="padding: 2px 8px; font-size: 12px;">View</button></td>
            </tr>
            <tr id="trace-{i}" class="trace-detail" style="display: none;">
                <td colspan="9">
                    <div style="margin-bottom: 20px;">
                        <strong>Description:</strong><br>
                        <div style="background: #fff; padding: 10px; border: 1px solid #eee; margin-top: 5px;">{case['description']}</div>
                    </div>
        """

        # Branch Analysis Section
        if r.get("branch_analysis"):
            ba = r["branch_analysis"]
            branch_agreement = ba.get("synthesis", {}).get("branch_agreement", 0)
            priority_rule = ba.get("synthesis", {}).get("priority_rule_applied", "None")
            conflict = ba.get("conflict")

            agreement_class = "agreement-high" if branch_agreement >= 0.85 else "agreement-medium" if branch_agreement >= 0.70 else "agreement-low"

            html += f"""
                    <h3>Tree-of-Thought Branch Analysis</h3>
                    <div class="branch-analysis">
                        <div class="branch-card">
                            <h4><span class="branch-icon branch-a">A</span> Transaction Acknowledgment</h4>
                            <div class="branch-conclusion">{ba.get('branch_a', {}).get('conclusion', 'N/A').title()}</div>
                            <div class="branch-evidence">
                                <strong>For:</strong> {', '.join(ba.get('branch_a', {}).get('evidence_for', [])[:3]) or 'None'}<br>
                                <strong>Against:</strong> {', '.join(ba.get('branch_a', {}).get('evidence_against', [])[:3]) or 'None'}
                            </div>
                        </div>
                        <div class="branch-card">
                            <h4><span class="branch-icon branch-b">B</span> Complaint Specifics</h4>
                            <div class="branch-conclusion">{ba.get('branch_b', {}).get('complaint_type', 'N/A').title()}</div>
                            <div class="branch-evidence">
                                <strong>Evidence:</strong> {', '.join(ba.get('branch_b', {}).get('evidence', [])[:3]) or 'None'}
                            </div>
                        </div>
                        <div class="branch-card">
                            <h4><span class="branch-icon branch-c">C</span> User Persona</h4>
                            <div class="branch-conclusion">{ba.get('branch_c', {}).get('persona', 'N/A').title()}</div>
                            <div class="branch-evidence">
                                <strong>Evidence:</strong> {', '.join(ba.get('branch_c', {}).get('evidence', [])[:3]) or 'None'}
                            </div>
                        </div>
                    </div>

                    <div class="synthesis-box">
                        <h4>Branch Synthesis</h4>
                        <div>
                            <strong>Agreement Score:</strong> {branch_agreement:.2f}
                            <div class="agreement-bar">
                                <div class="agreement-fill {agreement_class}" style="width: {branch_agreement * 100}%"></div>
                            </div>
                        </div>
                        <div><strong>Priority Rule Applied:</strong> {priority_rule or 'None'}</div>
            """

            if conflict:
                conflict_resolved = status == "PASS"
                badge_class = "conflict-resolved" if conflict_resolved else ""
                html += f"""
                        <div style="margin-top: 10px;">
                            <span class="conflict-badge {badge_class}">CONFLICT: {conflict.get('type', 'unknown')}</span>
                            <span style="margin-left: 10px;">Resolution: {conflict.get('resolution', 'N/A')}</span>
                        </div>
                """

            html += """
                    </div>
            """

        # V4 Comparison
        html += f"""
                    <div class="diff-container">
                        <div class="diff-col">
                            <h3>Expected</h3>
                            <div>Category: {expected}</div>
                        </div>
                        <div class="diff-col">
                            <h3>V5-ToT Result</h3>
                            <div class="{"" if status == "PASS" else "mismatch"}">Category: {actual}</div>
                            <div><strong>Reasoning:</strong> {r['result'].get('reasoning', 'N/A')}</div>
                            <div><strong>Confidence Rationale:</strong> {r['result'].get('confidence_rationale', 'N/A')}</div>
                        </div>
                        <div class="diff-col">
                            <h3>V4 Comparison</h3>
                            <div>Category: {v4_category}</div>
                            <div>Status: {v4_status}</div>
                            <div class="v4-comparison">{v4_indicator}</div>
                        </div>
                    </div>
        """

        # Execution Trace
        html += """
                    <h3>Execution Trace</h3>
        """

        if "trace" in r and "steps" in r["trace"]:
            for step in r["trace"]["steps"]:
                html += f"""<div class="trace-step"><h4>Step: {step.get('step', 'unknown')}</h4>
                        <div class="label">Model: {step.get('model', 'unknown')}</div>
                        <div class="label">Prompt:</div>
                        <div class="prompt-box">{_escape_html(step.get('prompt', ''))}</div>
                        <div class="label">LLM Response:</div>
                        <div class="response-box">{_escape_html(step.get('llm_response', ''))}</div>
                    </div>"""

        html += """
                </td>
            </tr>
        """

    html += """
            </tbody>
        </table>
    </div>
</body>
</html>
    """

    with open(HTML_PATH, "w") as f:
        f.write(html)

    print(f"Report generated at {HTML_PATH}")
    print(f"\nSummary:")
    print(f"  V5-ToT: {pass_rate:.1f}% ({passed}/{total})")
    print(f"  V4:     {v4_rate:.1f}% ({v4_passed}/{v4_total})")
    print(f"  Change: {'+'if improvement > 0 else ''}{improvement:.1f}%")


def _escape_html(text: str) -> str:
    """Escape HTML special characters."""
    if not text:
        return ""
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&#39;")
    )


if __name__ == "__main__":
    generate_report()
