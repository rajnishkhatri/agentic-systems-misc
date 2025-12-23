import json
import os
import sys
from collections import Counter

# Adjust path to include the project root
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.insert(0, project_root)

JSON_PATH = os.path.join(project_root, "qualitative/phase1/natural_language_trace_results.json")
HTML_PATH = os.path.join(project_root, "qualitative/phase1/natural_language_report_v2_trace.html")

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
    failure_stages = Counter()

    for r in results:
        var_type = r.get("case", {}).get("variation_type", "unknown")
        variation_totals[var_type] += 1
        if r.get("status") == "PASS":
            variation_stats[var_type] += 1
        else:
            stage = r.get("failure_stage")
            if stage:
                failure_stages[stage] += 1

    # HTML Generation
    html = f"""<!DOCTYPE html>
<html>
<head>
    <title>Dispute Classification V2 - Trace Report</title>
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
        .status-error {{ color: #fd7e14; font-weight: bold; }}
        
        .row-pass {{ background-color: #f8fff9; }}
        .row-fail {{ background-color: #fff8f8; cursor: pointer; }}
        .row-fail:hover {{ background-color: #ffeef0; }}
        
        .trace-detail {{ display: none; background: #fafafa; padding: 20px; border-top: 1px solid #eee; }}
        .trace-detail.active {{ display: table-row; }}
        
        .trace-step {{ margin-bottom: 15px; border-left: 3px solid #dee2e6; padding-left: 15px; }}
        .trace-step h4 {{ margin: 0 0 10px 0; font-size: 16px; }}
        
        .prompt-box, .response-box {{ background: #fff; padding: 10px; border: 1px solid #eee; border-radius: 4px; font-family: monospace; white-space: pre-wrap; margin-top: 5px; font-size: 12px; max-height: 300px; overflow-y: auto; }}
        .label {{ font-weight: bold; font-size: 12px; color: #666; display: block; margin-bottom: 4px; }}
        
        .diff-container {{ display: flex; gap: 20px; margin-bottom: 15px; }}
        .diff-col {{ flex: 1; }}
        .mismatch {{ background-color: #ffe6e6; padding: 2px 5px; border-radius: 3px; color: #dc3545; }}
        
        .filter-bar {{ margin-bottom: 20px; }}
        button {{ padding: 8px 16px; margin-right: 10px; cursor: pointer; background: #e9ecef; border: none; border-radius: 4px; }}
        button.active {{ background: #007bff; color: white; }}
    </style>
    <script>
        function toggleTrace(id) {{
            const row = document.getElementById('trace-' + id);
            if (row.style.display === 'none' || !row.style.display) {{
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
            
            // Update buttons
            document.querySelectorAll('.filter-btn').forEach(btn => btn.classList.remove('active'));
            document.getElementById('btn-' + type).classList.add('active');
        }}
    </script>
</head>
<body>
    <div class="container">
        <h1>Dispute Classification V2 Analysis</h1>
        
        <div class="dashboard">
            <div class="card">
                <div class="stat-value">{pass_rate:.1f}%</div>
                <div class="stat-label">Overall Pass Rate</div>
                <div style="margin-top: 10px; font-size: 13px;">
                    {passed} / {total} Passed
                </div>
            </div>
            <div class="card">
                <div class="stat-label">Performance by Persona</div>
                <div style="margin-top: 10px;">
    """
    
    for var_type, count in variation_totals.items():
        rate = (variation_stats[var_type] / count * 100) if count > 0 else 0
        html += f"<div><strong>{var_type.title()}:</strong> {rate:.1f}%</div>"
        
    html += """
                </div>
            </div>
            <div class="card">
                <div class="stat-label">Failure Stages</div>
                <div style="margin-top: 10px;">
    """
    
    for stage, count in failure_stages.items():
        percentage = (count / (total - passed) * 100) if (total - passed) > 0 else 0
        html += f"<div><strong>{stage}:</strong> {count} ({percentage:.1f}%)</div>"
        
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
                    <th>Network</th>
                    <th>Code</th>
                    <th>Confidence</th>
                    <th>Action</th>
                </tr>
            </thead>
            <tbody>
    """

    for i, r in enumerate(results):
        case = r.get("case", {})
        result = r.get("result", {})
        status = r.get("status", "UNKNOWN")
        trace = r.get("trace", {})
        
        status_cls = "status-pass" if status == "PASS" else "status-fail"
        row_cls = "row-pass status-pass" if status == "PASS" else "row-fail status-fail"
        
        # Comparison logic
        exp_net = case.get("network")
        act_net = result.get("network")
        net_cls = "mismatch" if exp_net != act_net else ""
        
        exp_code = case.get("true_reason_code")
        act_code = result.get("reason_code")
        code_cls = "mismatch" if exp_code != act_code else ""
        
        # Escaping
        description = case.get('description', '').replace('<', '&lt;').replace('>', '&gt;')
        
        html += f"""
            <tr class="case-row {row_cls}" onclick="toggleTrace({i})">
                <td>{case.get('dispute_id')}</td>
                <td>{case.get('variation_type')}</td>
                <td class="{status_cls}">{status}</td>
                <td><span class="{net_cls}">{act_net}</span> <small>(exp: {exp_net})</small></td>
                <td><span class="{code_cls}">{act_code}</span> <small>(exp: {exp_code})</small></td>
                <td>{result.get('classification_confidence', 0.0)}</td>
                <td><button style="padding: 2px 8px; font-size: 12px;">View Trace</button></td>
            </tr>
            <tr id="trace-{i}" class="trace-detail" style="display: none;">
                <td colspan="7">
                    <div style="margin-bottom: 20px;">
                        <strong>Description:</strong><br>
                        <div style="background: #fff; padding: 10px; border: 1px solid #eee; margin-top: 5px;">{description}</div>
                    </div>
                    
                    <div class="diff-container">
                        <div class="diff-col">
                            <h3>Expected</h3>
                            <div>Network: {exp_net}</div>
                            <div>Category: {case.get('category')}</div>
                            <div>Code: {exp_code}</div>
                        </div>
                        <div class="diff-col">
                            <h3>Actual</h3>
                            <div class="{net_cls}">Network: {act_net}</div>
                            <div class="{'mismatch' if result.get('category') != case.get('category') else ''}">Category: {result.get('category')}</div>
                            <div class="{code_cls}">Code: {act_code}</div>
                        </div>
                    </div>
                    
                    <h3>Execution Trace</h3>
        """
        
        # Render Trace Steps
        if "steps" in trace:
            for step in trace["steps"]:
                step_name = step.get("step")
                html += f'<div class="trace-step"><h4>Step: {step_name}</h4>'
                
                if step_name == "identify_network":
                    html += f"<div>Detected: <strong>{step.get('network')}</strong> (Source: {step.get('source')})</div>"
                elif step_name == "detect_network_family":
                    html += f"<div>Family Signal: {step.get('family')}</div>"
                elif step_name == "keyword_hint":
                    html += f"<div>Hint Applied: {json.dumps(step.get('hint'), indent=2)}</div>"
                elif step_name == "identify_category" or step_name == "select_code":
                    prompt = step.get('prompt', '').replace('<', '&lt;').replace('>', '&gt;')
                    raw_resp = step.get('raw_response', '').replace('<', '&lt;').replace('>', '&gt;')
                    
                    html += f"""
                        <div class="label">Prompt:</div>
                        <div class="prompt-box">{prompt}</div>
                        <div class="label">LLM Response:</div>
                        <div class="response-box">{raw_resp}</div>
                        <div class="label">Parsed Output:</div>
                        <div class="response-box">{json.dumps(step.get('parsed_output'), indent=2)}</div>
                    """
                elif step_name == "fallback_search":
                    html += f"<div>{step.get('message')}</div>"
                    
                html += "</div>"
        
        if "error" in trace:
             html += f'<div class="trace-step" style="border-color: red;"><h4>Error</h4><div class="response-box" style="color: red;">{trace["error"]}</div></div>'

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

