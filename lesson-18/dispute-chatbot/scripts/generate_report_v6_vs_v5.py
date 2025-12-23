"""Generate HTML comparison report for V6-MIPRO vs V5-ToT.

This script compares the results of the V6-MIPRO optimized prompt against the
V5-ToT baseline on the same subset of 50 examples.
"""

import json
import os
import sys
from pathlib import Path
from typing import Dict, List, Any

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

# Constants
V5_TRACE_PATH = project_root / "qualitative" / "phase1" / "natural_language_trace_results_v5_tot.json"
V6_TRACE_PATH = project_root / "qualitative" / "phase1" / "natural_language_trace_results_v6_mipro.json"
HTML_REPORT_PATH = project_root / "qualitative" / "phase1" / "natural_language_report_v6_mipro_vs_v5.html"

def load_results(path: Path) -> Dict[str, Any]:
    """Load results into a dictionary keyed by dispute_id."""
    if not path.exists():
        print(f"Error: File not found: {path}")
        return {}
    
    with open(path, "r") as f:
        data = json.load(f)
    
    results_map = {}
    for entry in data:
        case = entry.get("case", {})
        dispute_id = case.get("dispute_id")
        if dispute_id:
            results_map[dispute_id] = entry
    return results_map

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

def generate_report():
    print("Loading results...")
    v5_results = load_results(V5_TRACE_PATH)
    v6_results = load_results(V6_TRACE_PATH)
    
    if not v5_results or not v6_results:
        print("Missing result files. Aborting.")
        return

    # Find common dispute IDs (should be all of them if run correctly)
    common_ids = sorted(list(set(v5_results.keys()) & set(v6_results.keys())))
    print(f"Comparing {len(common_ids)} common cases.")

    # Calculate stats
    v5_passed = sum(1 for uid in common_ids if v5_results[uid]["status"] == "PASS")
    v6_passed = sum(1 for uid in common_ids if v6_results[uid]["status"] == "PASS")
    total = len(common_ids)
    
    v5_rate = (v5_passed / total * 100) if total > 0 else 0
    v6_rate = (v6_passed / total * 100) if total > 0 else 0
    improvement = v6_rate - v5_rate

    # HTML Generation
    html = f"""<!DOCTYPE html>
<html>
<head>
    <title>V6-MIPRO vs V5-ToT Comparison Report</title>
    <style>
        body {{ font-family: system-ui, -apple-system, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; color: #333; }}
        .container {{ max-width: 1400px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        .header {{ margin-bottom: 30px; border-bottom: 1px solid #eee; padding-bottom: 20px; }}
        h1 {{ margin: 0 0 10px 0; color: #2c3e50; }}
        .subtitle {{ color: #6c757d; font-size: 14px; margin: 0; }}
        
        .dashboard {{ display: flex; gap: 20px; margin-bottom: 30px; flex-wrap: wrap; }}
        .card {{ flex: 1; min-width: 200px; background: #f8f9fa; padding: 20px; border-radius: 8px; border: 1px solid #e9ecef; text-align: center; }}
        .card.highlight {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; }}
        .card.highlight .stat-label {{ color: rgba(255,255,255,0.8); }}
        .card.highlight .stat-val {{ color: white; }}
        
        .stat-val {{ font-size: 32px; font-weight: bold; margin-bottom: 5px; color: #2c3e50; }}
        .stat-label {{ font-size: 13px; text-transform: uppercase; letter-spacing: 0.5px; color: #6c757d; }}
        
        .improvement-positive {{ color: #28a745; }}
        .improvement-negative {{ color: #dc3545; }}
        
        table {{ width: 100%; border-collapse: collapse; font-size: 14px; margin-top: 20px; }}
        th {{ background: #f8f9fa; text-align: left; padding: 12px; font-weight: 600; color: #495057; border-bottom: 2px solid #dee2e6; }}
        td {{ padding: 12px; border-bottom: 1px solid #eee; vertical-align: top; }}
        tr:hover {{ background-color: #f8f9fa; }}
        
        .status-badge {{ padding: 4px 8px; border-radius: 4px; font-weight: bold; font-size: 11px; }}
        .status-PASS {{ background: #d4edda; color: #155724; }}
        .status-FAIL {{ background: #f8d7da; color: #721c24; }}
        .status-ERROR {{ background: #fff3cd; color: #856404; }}
        
        .comp-better {{ color: #28a745; font-weight: bold; }}
        .comp-worse {{ color: #dc3545; font-weight: bold; }}
        .comp-same {{ color: #6c757d; }}
        
        .detail-row {{ display: none; background: #fafafa; }}
        .detail-container {{ padding: 20px; display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }}
        .detail-box {{ background: white; padding: 15px; border-radius: 6px; border: 1px solid #eee; }}
        .detail-box h4 {{ margin-top: 0; color: #495057; font-size: 14px; border-bottom: 1px solid #eee; padding-bottom: 8px; }}
        
        pre {{ white-space: pre-wrap; font-family: monospace; font-size: 12px; background: #f8f9fa; padding: 10px; border-radius: 4px; margin: 0; }}
        
        .trace-step {{ margin-top: 15px; border-left: 3px solid #dee2e6; padding-left: 15px; }}
        .trace-label {{ font-weight: bold; font-size: 11px; color: #666; margin-top: 8px; display: block; }}
        .trace-content {{ font-family: monospace; font-size: 11px; background: #fff; padding: 8px; border: 1px solid #eee; max-height: 200px; overflow-y: auto; white-space: pre-wrap; }}

        .filter-bar {{ display: flex; gap: 10px; margin-bottom: 20px; }}
        .filter-btn {{ padding: 6px 12px; border: 1px solid #ced4da; background: white; border-radius: 4px; cursor: pointer; font-size: 13px; }}
        .filter-btn.active {{ background: #2c3e50; color: white; border-color: #2c3e50; }}
    </style>
    <script>
        function toggleDetail(id) {{
            const row = document.getElementById('detail-' + id);
            row.style.display = row.style.display === 'none' ? 'table-row' : 'none';
        }}
        
        function filterRows(type) {{
            const rows = document.querySelectorAll('.main-row');
            document.querySelectorAll('.detail-row').forEach(r => r.style.display = 'none');
            
            rows.forEach(row => {{
                if (type === 'all') {{
                    row.style.display = 'table-row';
                }} else if (type === 'improved') {{
                    row.style.display = row.classList.contains('improved') ? 'table-row' : 'none';
                }} else if (type === 'regressed') {{
                    row.style.display = row.classList.contains('regressed') ? 'table-row' : 'none';
                }} else if (type === 'failed') {{
                    row.style.display = row.classList.contains('failed') ? 'table-row' : 'none';
                }}
            }});
            
            document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
            document.getElementById('btn-' + type).classList.add('active');
        }}
    </script>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>V6-MIPRO vs V5-ToT Comparison</h1>
            <p class="subtitle">Comparing Optimized Prompt (GPT-4o) vs Baseline (Claude/GPT-4o) on 50 Failure Cases</p>
        </div>
        
        <div class="dashboard">
            <div class="card highlight">
                <div class="stat-val">{v6_rate:.1f}%</div>
                <div class="stat-label">V6-MIPRO Accuracy</div>
                <div style="font-size: 12px; margin-top: 5px;">{v6_passed}/{total} Passed</div>
            </div>
            <div class="card">
                <div class="stat-val">{v5_rate:.1f}%</div>
                <div class="stat-label">V5-ToT Accuracy</div>
                <div style="font-size: 12px; margin-top: 5px;">{v5_passed}/{total} Passed</div>
            </div>
            <div class="card">
                <div class="stat-val" style="color: {'#28a745' if improvement >= 0 else '#dc3545'}">{improvement:+.1f}%</div>
                <div class="stat-label">Improvement</div>
            </div>
        </div>
        
        <div class="filter-bar">
            <button id="btn-all" class="filter-btn active" onclick="filterRows('all')">All Cases</button>
            <button id="btn-improved" class="filter-btn" onclick="filterRows('improved')">Improved (V6 Pass, V5 Fail)</button>
            <button id="btn-regressed" class="filter-btn" onclick="filterRows('regressed')">Regressed (V6 Fail, V5 Pass)</button>
            <button id="btn-failed" class="filter-btn" onclick="filterRows('failed')">Both Failed</button>
        </div>
        
        <table>
            <thead>
                <tr>
                    <th>ID / Persona</th>
                    <th>Expected</th>
                    <th>V6-MIPRO (New)</th>
                    <th>V5-ToT (Base)</th>
                    <th>Comparison</th>
                    <th>Actions</th>
                </tr>
            </thead>
            <tbody>
    """
    
    for uid in common_ids:
        v5 = v5_results[uid]
        v6 = v6_results[uid]
        case = v6["case"]
        
        v5_status = v5.get("status", "ERROR")
        v6_status = v6.get("status", "ERROR")
        
        v5_cat = v5.get("result", {}).get("category", "N/A")
        v6_cat = v6.get("result", {}).get("category", "N/A")
        
        expected = case.get("expected_category", "N/A")
        persona = case.get("variation_type", "unknown")
        
        # Determine comparison state
        comp_html = ""
        row_class = ""
        
        if v6_status == "PASS" and v5_status != "PASS":
            comp_html = '<span class="comp-better">IMPROVED</span>'
            row_class = "improved"
        elif v6_status != "PASS" and v5_status == "PASS":
            comp_html = '<span class="comp-worse">REGRESSED</span>'
            row_class = "regressed"
        elif v6_status == "PASS" and v5_status == "PASS":
            comp_html = '<span class="comp-same">BOTH PASS</span>'
            row_class = "passed"
        else:
            comp_html = '<span class="comp-same">BOTH FAIL</span>'
            row_class = "failed"
            
        html += f"""
            <tr class="main-row {row_class}" id="row-{uid}">
                <td>
                    <div style="font-weight:bold;">{uid}</div>
                    <div style="font-size:12px; color:#666;">{persona}</div>
                </td>
                <td>{expected}</td>
                <td>
                    <span class="status-badge status-{v6_status}">{v6_cat}</span>
                </td>
                <td>
                    <span class="status-badge status-{v5_status}">{v5_cat}</span>
                </td>
                <td>{comp_html}</td>
                <td><button onclick="toggleDetail('{uid}')" class="filter-btn">View Details</button></td>
            </tr>
            <tr class="detail-row" id="detail-{uid}">
                <td colspan="6">
                    <div class="detail-container">
                        <div class="detail-box" style="grid-column: span 2;">
                            <h4>Description</h4>
                            <div style="font-size:13px; line-height:1.4;">{case.get('description', '')}</div>
                        </div>
                        
                        <!-- V6 Analysis -->
                        <div class="detail-box">
                            <h4>V6-MIPRO Analysis</h4>
                            <div style="margin-bottom:10px;">
                                <strong>Confidence:</strong> {v6.get('result', {}).get('confidence', 'N/A')}
                            </div>
                            <pre>{v6.get('result', {}).get('reasoning', 'No reasoning')}</pre>
                            
                            <!-- Trace for V6 -->
                            <h5 style="margin-top:15px; margin-bottom:5px; font-size:12px; color:#666;">Execution Trace</h5>
        """
        
        # Add V6 Trace
        if "trace" in v6 and "steps" in v6["trace"]:
            for step in v6["trace"]["steps"]:
                html += f"""
                            <div class="trace-step">
                                <div><strong>Step:</strong> {step.get('step', 'unknown')}</div>
                                <div><strong>Model:</strong> {step.get('model', 'unknown')}</div>
                                <span class="trace-label">Prompt:</span>
                                <div class="trace-content">{_escape_html(step.get('prompt', ''))}</div>
                                <span class="trace-label">Response:</span>
                                <div class="trace-content">{_escape_html(step.get('llm_response', ''))}</div>
                            </div>
                """
        
        html += """
                        </div>
                        
                        <!-- V5 Analysis -->
                        <div class="detail-box">
                            <h4>V5-ToT Analysis</h4>
                            <div style="margin-bottom:10px;">
                                <strong>Confidence:</strong> {v5.get('result', {}).get('confidence', 'N/A')}
                            </div>
                            <pre>{v5.get('result', {}).get('reasoning', 'No reasoning')}</pre>
                            
                            <!-- Trace for V5 -->
                            <h5 style="margin-top:15px; margin-bottom:5px; font-size:12px; color:#666;">Execution Trace</h5>
        """
        
        # Add V5 Trace
        if "trace" in v5 and "steps" in v5["trace"]:
            for step in v5["trace"]["steps"]:
                html += f"""
                            <div class="trace-step">
                                <div><strong>Step:</strong> {step.get('step', 'unknown')}</div>
                                <div><strong>Model:</strong> {step.get('model', 'unknown')}</div>
                                <span class="trace-label">Prompt:</span>
                                <div class="trace-content">{_escape_html(step.get('prompt', ''))}</div>
                                <span class="trace-label">Response:</span>
                                <div class="trace-content">{_escape_html(step.get('llm_response', ''))}</div>
                            </div>
                """

        html += """
                        </div>
                    </div>
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
    
    with open(HTML_REPORT_PATH, "w") as f:
        f.write(html)
    print(f"Report generated at {HTML_REPORT_PATH}")

if __name__ == "__main__":
    generate_report()
