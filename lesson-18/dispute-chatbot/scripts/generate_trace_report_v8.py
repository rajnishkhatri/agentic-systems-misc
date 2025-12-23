"""Generate HTML trace report for V8 RAG classification results.

Compares V8 RAG results against the "V7 Baseline" (which is V6 traces re-scored against V3 Golden Set).
"""

import json
from collections import Counter
from pathlib import Path

# Configuration
project_root = Path(__file__).parent.parent

# V8 RAG Results (Target)
V8_TRACE_JSON_PATH = project_root / "qualitative" / "phase1" / "natural_language_trace_results_v8_rag.json"

# V6 Trace Results (Source for Baseline)
V6_TRACE_JSON_PATH = project_root / "qualitative" / "phase1" / "natural_language_trace_results_v6.json"

# Golden Set V3 (Ground Truth for Baseline)
GOLDEN_V3_PATH = project_root / "synthetic_data" / "phase1" / "golden_set" / "natural_language_classification_v3.json"

# Output report
HTML_PATH = project_root / "qualitative" / "phase1" / "natural_language_report_v8_rag_trace.html"


def _escape_html(text: str) -> str:
    """Escape HTML special characters."""
    if not text:
        return ""
    return (
        str(text).replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&#39;")
    )


def _load_golden_v3() -> dict:
    """Load Golden Set V3 as lookup by dispute_id."""
    if not GOLDEN_V3_PATH.exists():
        raise FileNotFoundError(f"Golden Set V3 not found at {GOLDEN_V3_PATH}")
    with open(GOLDEN_V3_PATH, "r", encoding="utf-8") as f:
        golden = json.load(f)
    return {item["dispute_id"]: item for item in golden}


def _build_v7_baseline(v6_results: list[dict], golden_v3_lookup: dict) -> dict:
    """Build V7 baseline lookup (status/prediction) by re-scoring V6 traces against Golden V3."""
    baseline = {}
    
    aliases = {
        "fraud": "fraudulent",
        "unauthorized": "fraudulent",
        "authorization": "general",
        "processing_errors": "general",
        "processing_error": "general",
        "processing": "general",
        "duplicate_charge": "duplicate",
        "billing_error": "general",
        "discrepancy": "general",
        "subscription_cancelled": "subscription_canceled",
        "refund_not_processed": "credit_not_processed",
        "refund_not_received": "credit_not_processed",
        "product_not_as_described": "product_unacceptable",
        "unknown": "unrecognized"
    }

    for r in v6_results:
        case = r.get("case", {})
        dispute_id = case.get("dispute_id")
        if not dispute_id:
            continue
            
        golden_case = golden_v3_lookup.get(dispute_id)
        if not golden_case:
            continue
            
        expected_v3 = golden_case.get("category", "")
        expected_norm = expected_v3.lower().strip().replace(" ", "_").replace("-", "_")
        expected_norm = aliases.get(expected_norm, expected_norm)
        
        prediction = (r.get("result") or {}).get("category", "N/A")
        
        status = "PASS" if prediction == expected_norm else "FAIL"
        
        baseline[dispute_id] = {
            "status": status,
            "prediction": prediction,
            "expected_v3": expected_v3,
            "reasoning": (r.get("result") or {}).get("reasoning", "")
        }
    return baseline


def generate_report() -> None:
    """Generate the V8 HTML trace report."""
    if not V8_TRACE_JSON_PATH.exists():
        print(f"Error: V8 Results JSON not found at {V8_TRACE_JSON_PATH}")
        return
        
    if not V6_TRACE_JSON_PATH.exists():
        print(f"Error: V6 Results JSON not found at {V6_TRACE_JSON_PATH}")
        return

    with open(V8_TRACE_JSON_PATH, "r", encoding="utf-8") as f:
        v8_results = json.load(f)

    with open(V6_TRACE_JSON_PATH, "r", encoding="utf-8") as f:
        v6_results = json.load(f)

    golden_v3_lookup = _load_golden_v3()
    v7_baseline = _build_v7_baseline(v6_results, golden_v3_lookup)

    # Statistics (V8)
    total = len(v8_results)
    passed = sum(1 for r in v8_results if r.get("status") == "PASS")
    errors = sum(1 for r in v8_results if r.get("status") == "ERROR")
    pass_rate = (passed / total * 100) if total > 0 else 0

    # Per-persona stats
    variation_stats = Counter()
    variation_totals = Counter()
    for r in v8_results:
        if r.get("status") == "ERROR":
            continue
        var_type = r["case"].get("variation_type", "unknown")
        variation_totals[var_type] += 1
        if r.get("status") == "PASS":
            variation_stats[var_type] += 1

    # Branch conflict stats
    total_conflicts = sum(
        1 for r in v8_results
        if r.get("branch_conflict")
    )
    conflicts_resolved = sum(
        1 for r in v8_results
        if r.get("branch_conflict") and r["status"] == "PASS"
    )

    # V7 Baseline stats (on the subset present in V8 results)
    baseline_passed = 0
    baseline_total = 0
    
    for r in v8_results:
        dispute_id = r["case"]["dispute_id"]
        if dispute_id in v7_baseline:
            baseline_total += 1
            if v7_baseline[dispute_id]["status"] == "PASS":
                baseline_passed += 1
    
    baseline_rate = (baseline_passed / baseline_total * 100) if baseline_total > 0 else 0
    improvement = pass_rate - baseline_rate
    improvement_class = "improvement-positive" if improvement > 0 else "improvement-negative" if improvement < 0 else ""

    model_used = v8_results[0].get("model", "unknown") if v8_results else "unknown"

    # HTML Generation
    html = f"""<!DOCTYPE html>
<html>
<head>
    <title>Dispute Classification V8 RAG Trace Report</title>
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

        .v7-comparison {{ background: #e9ecef; padding: 10px; border-radius: 4px; margin-top: 10px; font-size: 13px; }}
        .v7-comparison .improved {{ color: #28a745; }}
        .v7-comparison .regressed {{ color: #dc3545; }}
        .v7-comparison .same {{ color: #6c757d; }}

        .legend {{ display: flex; gap: 20px; margin-bottom: 20px; font-size: 13px; }}
        .legend-item {{ display: flex; align-items: center; gap: 5px; }}
        .legend-dot {{ width: 12px; height: 12px; border-radius: 50%; }}
        
        .rag-examples {{ background: #fff; padding: 10px; border: 1px solid #b8daff; border-radius: 4px; margin-top: 10px; }}
        .rag-example-item {{ padding: 8px; border-bottom: 1px solid #eee; font-size: 12px; }}
        .rag-example-item:last-child {{ border-bottom: none; }}
        
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
        <h1>Dispute Classification V8 RAG Trace Report</h1>
        <p class="subtitle">RAG + Tree-of-Thought Analysis | Model: {model_used} | Ground Truth: Golden Set V3</p>

        <div class="dashboard">
            <div class="card card-highlight">
                <div class="stat-value">{pass_rate:.1f}%</div>
                <div class="stat-label">V8 Accuracy</div>
                <div style="margin-top: 10px; font-size: 13px;">
                    {passed} / {total} Passed
                </div>
            </div>
            <div class="card">
                <div class="stat-value">{baseline_rate:.1f}%</div>
                <div class="stat-label">V7 Baseline (Rescored)</div>
                <div style="margin-top: 10px; font-size: 13px; {improvement_class}">
                    {"+" if improvement > 0 else ""}{improvement:.1f}% vs V7
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
    """

    if errors > 0:
        html += f"""            <button id="btn-status-error" class="filter-btn" onclick="filterRows('status-error')">Errors ({errors})</button>
    """

    html += """
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
                    <th>Expected (V3)</th>
                    <th>V8 RAG</th>
                    <th>V7 Baseline</th>
                    <th>Branches (A/B/C)</th>
                    <th>Conf.</th>
                    <th>Code</th>
                    <th>Code Conf.</th>
                    <th>Action</th>
                </tr>
            </thead>
            <tbody>
    """

    for i, r in enumerate(v8_results):
        case = r["case"]
        dispute_id = case["dispute_id"]

        persona = case.get("variation_type", "unknown")
        status_v8 = r.get("status", "N/A")
        status_class = "status-pass" if status_v8 == "PASS" else "status-error" if status_v8 == "ERROR" else "status-fail"
        row_class = "row-pass" if status_v8 == "PASS" else "row-error" if status_v8 == "ERROR" else "row-fail"

        expected_v3 = case.get("expected_category", "N/A")
        expected_code = case.get("true_reason_code", "N/A")  # Get true reason code
        actual = (r.get("result") or {}).get("category", "N/A")
        confidence = (r.get("result") or {}).get("confidence", 0)
        
        # Code Selection Data
        selected_code = (r.get("result") or {}).get("selected_code", "N/A")
        code_conf = (r.get("result") or {}).get("code_confidence", 0)
        code_reasoning = (r.get("result") or {}).get("code_reasoning", "N/A")

        # Baseline Data
        baseline_data = v7_baseline.get(dispute_id, {})
        baseline_status = baseline_data.get("status", "N/A")
        baseline_pred = baseline_data.get("prediction", "N/A")

        # Improvement indicator
        v8_correct = status_v8 == "PASS"
        v7_correct = baseline_status == "PASS"
        if v8_correct and not v7_correct:
            v7_indicator = '<span class="improved">IMPROVED</span>'
        elif not v8_correct and v7_correct:
            v7_indicator = '<span class="regressed">REGRESSED</span>'
        else:
            v7_indicator = '<span class="same">SAME</span>'

        # Branch summary
        branch_a = "?"
        branch_b = "?"
        branch_c = "?"
        has_conflict = False

        if r.get("branch_analysis"):
            ba = r["branch_analysis"]
            branch_a = ba.get("branch_a_conclusion", "?")[:3].upper()
            branch_b = ba.get("branch_b_complaint", "?")[:3].upper()
            branch_c = ba.get("branch_c_persona", "?")[:3].upper()
            has_conflict = r.get("branch_conflict") is not None

        conflict_badge = '<span class="conflict-badge">CONFLICT</span>' if has_conflict else ''
        actual_display = f'<span class="{"" if status_v8 == "PASS" else "mismatch"}">{actual}</span>'

        html += f"""
            <tr class="case-row {row_class} {status_class}" data-persona="{persona}" onclick="toggleTrace({i})">
                <td>{dispute_id}</td>
                <td>{persona}</td>
                <td class="{status_class}">{status_v8}</td>
                <td>{expected_v3}</td>
                <td>{actual_display}</td>
                <td>{baseline_status} ({baseline_pred})</td>
                <td>{branch_a}/{branch_b}/{branch_c}{conflict_badge}</td>
                <td>{confidence:.2f}</td>
                <td>{selected_code}</td>
                <td>{code_conf:.2f}</td>
                <td><button style="padding: 2px 8px; font-size: 12px;">View</button></td>
            </tr>
            <tr id="trace-{i}" class="trace-detail" style="display: none;">
                <td colspan="11">
                    <div style="margin-bottom: 20px;">
                        <strong>Description:</strong><br>
                        <div style="background: #fff; padding: 10px; border: 1px solid #eee; margin-top: 5px;">{_escape_html(case.get('description', ''))}</div>
                    </div>
        """

        # Branch Analysis Section
        if r.get("result"):
            res = r["result"]
            # Note: The trace result structure might vary, we extracted summaries but the full details might be in the parsed output inside trace or not easily accessible if not saved.
            # But we saved branch analysis summary. Let's look at the parsed_output in trace steps if available for details.
            
            trace_steps = r.get("trace", {}).get("steps", [])
            # First step is usually Identify Category V8
            id_step = trace_steps[0] if trace_steps else {}
            parsed = id_step.get("parsed_output", {})
            
            # If we have parsed output, we can show details.
            if parsed:
                ba_full = parsed # It matches CategoryResultV8Rag structure
                
                branch_agreement = parsed.get("synthesis", {}).get("branch_agreement", 0)
                priority_rule = parsed.get("synthesis", {}).get("priority_rule_applied", "None")
                
                agreement_class = "agreement-high" if branch_agreement >= 0.85 else "agreement-medium" if branch_agreement >= 0.70 else "agreement-low"

                html += f"""
                    <h3>Tree-of-Thought Branch Analysis</h3>
                    <div class="branch-analysis">
                        <div class="branch-card">
                            <h4><span class="branch-icon branch-a">A</span> Transaction Acknowledgment</h4>
                            <div class="branch-conclusion">{parsed.get('branch_a', {}).get('conclusion', 'N/A').title()}</div>
                            <div class="branch-evidence">
                                <strong>For:</strong> {', '.join(parsed.get('branch_a', {}).get('evidence_for_acknowledgment', [])[:3]) or 'None'}<br>
                                <strong>Against:</strong> {', '.join(parsed.get('branch_a', {}).get('evidence_against_acknowledgment', [])[:3]) or 'None'}
                            </div>
                        </div>
                        <div class="branch-card">
                            <h4><span class="branch-icon branch-b">B</span> Complaint Specifics</h4>
                            <div class="branch-conclusion">{parsed.get('branch_b', {}).get('complaint_type', 'N/A').title()}</div>
                            <div class="branch-evidence">
                                <strong>Evidence:</strong> {', '.join(parsed.get('branch_b', {}).get('evidence', [])[:3]) or 'None'}
                            </div>
                        </div>
                        <div class="branch-card">
                            <h4><span class="branch-icon branch-c">C</span> User Persona</h4>
                            <div class="branch-conclusion">{parsed.get('branch_c', {}).get('persona', 'N/A').title()}</div>
                            <div class="branch-evidence">
                                <strong>Evidence:</strong> {', '.join(parsed.get('branch_c', {}).get('evidence', [])[:3]) or 'None'}
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
                    </div>
                """
        
        if r.get("branch_conflict"):
            conflict = r["branch_conflict"]
            conflict_resolved = status_v8 == "PASS"
            badge_class = "conflict-resolved" if conflict_resolved else ""
            html += f"""
                    <div style="margin-top: 10px; margin-bottom: 20px;">
                        <span class="conflict-badge {badge_class}">CONFLICT: {conflict.get('type', 'unknown')}</span>
                        <span style="margin-left: 10px;">Resolution: {conflict.get('resolution', 'N/A')}</span>
                    </div>
            """

        golden_meta = r.get("case", {})
        change_reason = golden_meta.get("category_change_reason") or ""
        prev_cat = golden_meta.get("category_v3_previous") or ""

        change_html = ""
        if prev_cat or change_reason:
            change_html = f"""
                            <div class="change-note" style="background: #e8f4ff; border: 1px solid #90caf9; padding: 10px 15px; border-radius: 6px; margin-top: 10px; font-size: 13px;">
                                <div><strong>Golden V3 Metadata</strong></div>
                                {f"<div>Previous: <code>{_escape_html(prev_cat)}</code></div>" if prev_cat else ""}
                                {f"<div>Change reason: {_escape_html(change_reason)}</div>" if change_reason else ""}
                            </div>
            """

        html += f"""
                    <div class="diff-container">
                        <div class="diff-col">
                            <h3>Expected (Golden V3)</h3>
                            <div><strong>Ground Truth:</strong> {expected_v3}</div>
                            {change_html}
                        </div>
                        <div class="diff-col">
                            <h3>V8 RAG Result</h3>
                            <div class="{"" if status_v8 == "PASS" else "mismatch"}">Category: {actual}</div>
                            <div><strong>Reasoning:</strong> {_escape_html((r.get('result') or {}).get('reasoning', 'N/A'))}</div>
                            <div><strong>Confidence Rationale:</strong> {_escape_html((r.get('result') or {}).get('confidence_rationale', 'N/A'))}</div>
                        </div>
                        <div class="diff-col">
                            <h3>V7 Baseline Comparison</h3>
                            <div>Status: {baseline_status}</div>
                            <div>Prediction: {baseline_pred}</div>
                            <div class="v7-comparison">{v7_indicator}</div>
                        </div>
                    </div>
        """
        
        html += f"""
                    <div style="background: #fff; padding: 15px; border-radius: 4px; border: 1px solid #eee; margin-bottom: 20px;">
                        <h3 style="margin-top: 0; font-size: 14px; color: #666; border-bottom: 1px solid #eee; padding-bottom: 5px;">Code Selection</h3>
                        <div style="display: flex; gap: 20px;">
                             <div style="flex: 1;"><strong>Expected Code:</strong> {expected_code}</div>
                             <div style="flex: 1;"><strong>Predicted Code:</strong> {selected_code}</div>
                             <div style="flex: 1;"><strong>Confidence:</strong> {code_conf:.2f}</div>
                        </div>
                        <div style="margin-top: 10px;"><strong>Reasoning:</strong> {_escape_html(code_reasoning)}</div>
                    </div>
        """

        # RAG Examples
        trace_steps = r.get("trace", {}).get("steps", [])
        if trace_steps:
            # Assumes 1st step is classification which has retrieved examples
            examples = trace_steps[0].get("retrieved_examples", [])
            if examples:
                html += """<h3>RAG Context (Retrieved Examples)</h3><div class="rag-examples">"""
                for ex in examples:
                    # Depending on how examples are returned (strings or dicts)
                    # The retriever usually returns strings or dicts. Assuming dicts or objects with 'page_content' or similar
                    # If string:
                    ex_text = str(ex)
                    # If dict
                    if isinstance(ex, dict):
                        # Use full description or content
                        ex_text = ex.get("description", ex.get("page_content", str(ex)))
                        # Add similarity score if available
                        if "similarity_score" in ex:
                            ex_text = f"[Score: {ex['similarity_score']:.3f}] {ex_text}"
                        
                    html += f"""<div class="rag-example-item">{_escape_html(ex_text)}</div>"""
                html += "</div>"

        # Execution Trace
        html += """
                    <h3>Execution Trace</h3>
        """

        if trace_steps:
            for step in trace_steps:
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

    with open(HTML_PATH, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"Report generated at {HTML_PATH}")
    print("\nSummary:")
    print(f"  V8 RAG: {pass_rate:.1f}% ({passed}/{total})")
    print(f"  V7 Baseline: {baseline_rate:.1f}% ({baseline_passed}/{baseline_total})")
    print(f"  Change: {'+' if improvement > 0 else ''}{improvement:.1f}%")


if __name__ == "__main__":
    generate_report()
