import json
import os
import sys
from collections import Counter

# Adjust path to include the project root
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.insert(0, project_root)

# Configuration
JSON_PATH = os.path.join(project_root, "qualitative/phase1/natural_language_trace_results_v4.json")
HTML_PATH = os.path.join(project_root, "qualitative/phase1/natural_language_report_v4_trace.html")

def generate_report():
    if not os.path.exists(JSON_PATH):
        print(f"Error: Results JSON not found at {JSON_PATH}")
        return

    with open(JSON_PATH, 'r') as f:
        results = json.load(f)

    # Statistics
    total = len(results)
    passed = sum(1 for r in results if r.get("status") == "PASS")
    pass_rate = (passed / total * 100) if total > 0 else 0
    
    variation_stats = Counter()
    variation_totals = Counter()

    for r in results:
        # Extract variation from dispute_id if not present in case (e.g. gen_amex_A01_ambiguous -> ambiguous)
        var_type = "unknown"
        if "case" in r and "variation_type" in r["case"]:
            var_type = r["case"]["variation_type"]
        elif "case" in r and "dispute_id" in r["case"]:
            parts = r["case"]["dispute_id"].split("_")
            if len(parts) > 0:
                var_type = parts[-1]
        
        variation_totals[var_type] += 1
        if r.get("status") == "PASS":
            variation_stats[var_type] += 1

    # HTML Generation
    html = f"""<!DOCTYPE html>
<html>
<head>
    <title>Dispute Classification V4 Trace Report</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; color: #333; }}
        .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        h1, h2, h3 {{ color: #2c3e50; }}
        .dashboard {{ display: flex; gap: 20px; margin-bottom: 30px; }}
        .card {{ flex: 1; background: #f8f9fa; padding: 20px; border-radius: 6px; border: 1px solid #e9ecef; }}
        .stat-value {{ font-size: 24px; font-weight: bold; color: #2c3e50; }}
        .stat-label {{ color: #6c757d; font-size: 14px; text-transform: uppercase; letter-spacing: 0.5px; }}
        
        table {{ width: 100%; border-collapse: collapse; margin-top: 20px; font-size: 14px; }}
        th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #eee; }}
        th {{ background: #f8f9fa; font-weight: 600; color: #495057; }}
        
        .status-pass {{ color: #28a745; font-weight: bold; }}
        .status-fail {{ color: #dc3545; font-weight: bold; }}
        
        .row-pass {{ background-color: #f8fff9; }}
        .row-fail {{ background-color: #fff8f8; cursor: pointer; }}
        .row-fail:hover {{ background-color: #ffeef0; }}
        
        .trace-detail {{ display: none; background: #fafafa; padding: 20px; border-top: 1px solid #eee; }}
        
        .trace-step {{ margin-bottom: 15px; border-left: 3px solid #dee2e6; padding-left: 15px; }}
        .trace-step h4 {{ margin: 0 0 10px 0; font-size: 16px; }}
        
        .prompt-box, .response-box {{ background: #fff; padding: 10px; border: 1px solid #eee; border-radius: 4px; font-family: monospace; white-space: pre-wrap; margin-top: 5px; font-size: 12px; max-height: 300px; overflow-y: auto; }}
        .label {{ font-weight: bold; font-size: 12px; color: #666; display: block; margin-bottom: 4px; margin-top: 10px; }}
        
        .filter-bar {{ margin-bottom: 20px; }}
        .filter-btn {{ padding: 8px 16px; border: 1px solid #ddd; background: white; border-radius: 20px; cursor: pointer; margin-right: 10px; font-size: 13px; }}
        .filter-btn.active {{ background: #2c3e50; color: white; border-color: #2c3e50; }}
        
        .diff-container {{ display: flex; gap: 20px; margin-bottom: 20px; }}
        .diff-col {{ flex: 1; background: #fff; padding: 15px; border-radius: 4px; border: 1px solid #eee; }}
        .diff-col h3 {{ margin-top: 0; font-size: 14px; color: #666; border-bottom: 1px solid #eee; padding-bottom: 5px; }}
        .mismatch {{ color: #dc3545; font-weight: bold; }}
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
        <h1>Dispute Classification V4 Trace Report</h1>
        
        <div class="dashboard">
            <div class="card">
                <div class="stat-value">{pass_rate:.1f}%</div>
                <div class="stat-label">Correction Rate (on {total} failures)</div>
                <div style="margin-top: 10px; font-size: 13px;">
                    {passed} / {total} Passed
                </div>
            </div>
            <div class="card">
                <div class="stat-label">Performance by Persona</div>
                <div style="margin-top: 10px;">
    """
    
    for var_type, count in variation_totals.items():
        var_pass = variation_stats[var_type]
        var_rate = (var_pass / count * 100) if count > 0 else 0
        html += f"<div><strong>{var_type.title()}:</strong> {var_rate:.1f}% ({var_pass}/{count})</div>"

    html += """
                </div>
            </div>
        </div>

        <div class="filter-bar">
            <button id="btn-all" class="filter-btn active" onclick="filterRows('all')">All Cases</button>
            <button id="btn-pass" class="filter-btn" onclick="filterRows('status-pass')">Passed</button>
            <button id="btn-fail" class="filter-btn" onclick="filterRows('status-fail')">Failed</button>
        </div>

        <table>
            <thead>
                <tr>
                    <th>ID</th>
                    <th>Persona</th>
                    <th>Status</th>
                    <th>Expected</th>
                    <th>Actual (V4)</th>
                    <th>Action</th>
                </tr>
            </thead>
            <tbody>
    """

    for i, r in enumerate(results):
        case = r["case"]
        dispute_id = case["dispute_id"]
        
        # Determine persona
        persona = "unknown"
        if "variation_type" in case:
            persona = case["variation_type"]
        else:
            parts = dispute_id.split("_")
            if len(parts) > 0:
                persona = parts[-1]
                
        status = r["status"]
        status_class = "status-pass" if status == "PASS" else "status-fail"
        row_class = "row-pass" if status == "PASS" else "row-fail"
        
        expected = case["expected_category"]
        actual = r["result"]["category"]
        
        actual_display = f'<span class="{"" if status == "PASS" else "mismatch"}">{actual}</span>'

        html += f"""
            <tr class="case-row {row_class} {status_class}" onclick="toggleTrace({i})">
                <td>{dispute_id}</td>
                <td>{persona}</td>
                <td class="{status_class}">{status}</td>
                <td>{expected}</td>
                <td>{actual_display}</td>
                <td><button style="padding: 2px 8px; font-size: 12px;">View Trace</button></td>
            </tr>
            <tr id="trace-{i}" class="trace-detail" style="display: none;">
                <td colspan="6">
                    <div style="margin-bottom: 20px;">
                        <strong>Description:</strong><br>
                        <div style="background: #fff; padding: 10px; border: 1px solid #eee; margin-top: 5px;">{case['description']}</div>
                    </div>
                    
                    <div class="diff-container">
                        <div class="diff-col">
                            <h3>Expected</h3>
                            <div>Category: {expected}</div>
                        </div>
                        <div class="diff-col">
                            <h3>Actual (V4)</h3>
                            <div class="{"" if status == "PASS" else "mismatch"}">Category: {actual}</div>
                            <div>Reasoning (Analysis): {r['result']['reasoning']}</div>
                        </div>
                    </div>
                    
                    <h3>Execution Trace</h3>
        """
        
        if "trace" in r and "steps" in r["trace"]:
            for step in r["trace"]["steps"]:
                html += f"""<div class="trace-step"><h4>Step: {step.get('step', 'unknown')}</h4>
                        <div class="label">Prompt:</div>
                        <div class="prompt-box">{step.get('prompt', '')}</div>
                        <div class="label">LLM Response:</div>
                        <div class="response-box">{step.get('llm_response', '')}</div>
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

    with open(HTML_PATH, 'w') as f:
        f.write(html)
    
    print(f"Report generated at {HTML_PATH}")

if __name__ == "__main__":
    generate_report()

