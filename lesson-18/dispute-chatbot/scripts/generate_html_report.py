import pandas as pd
import os
import sys

# Adjust path to include the project root
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.insert(0, project_root)

CSV_PATH = os.path.join(project_root, "qualitative/phase1/natural_language_results.csv")
HTML_PATH = os.path.join(project_root, "qualitative/phase1/natural_language_report_v2.html")

def generate_html_report():
    if not os.path.exists(CSV_PATH):
        print(f"Error: Results CSV not found at {CSV_PATH}")
        return

    df = pd.read_csv(CSV_PATH)
    
    # Calculate stats
    total = len(df)
    passed = len(df[df['status'] == 'PASS'])
    pass_rate = (passed / total * 100) if total > 0 else 0
    
    # Stats by variation
    stats = df.groupby('variation_type')['status'].apply(lambda x: (x == 'PASS').mean() * 100).reset_index()
    stats.columns = ['Variation', 'Pass Rate (%)']
    stats['Pass Rate (%)'] = stats['Pass Rate (%)'].round(1)
    
    # Generate HTML content
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Natural Language Classification Test Report</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; color: #333; }}
            h1 {{ color: #2c3e50; }}
            .summary {{ background: #f8f9fa; padding: 20px; border-radius: 5px; margin-bottom: 20px; }}
            .stats-table, .details-table {{ width: 100%; border-collapse: collapse; margin-bottom: 20px; }}
            th, td {{ padding: 10px; border: 1px solid #ddd; text-align: left; }}
            th {{ background-color: #f2f2f2; }}
            .pass {{ color: green; font-weight: bold; }}
            .fail {{ color: red; font-weight: bold; }}
            .row-fail {{ background-color: #fff0f0; }}
            .row-pass {{ background-color: #f0fff0; }}
        </style>
    </head>
    <body>
        <h1>Natural Language Classification Test Report</h1>
        
        <div class="summary">
            <h2>Summary</h2>
            <p><strong>Total Cases:</strong> {total}</p>
            <p><strong>Passed:</strong> {passed}</p>
            <p><strong>Overall Pass Rate:</strong> {pass_rate:.1f}%</p>
        </div>

        <h2>Performance by Persona</h2>
        <table class="stats-table">
            <tr>
                <th>Variation</th>
                <th>Pass Rate</th>
            </tr>
    """
    
    for _, row in stats.iterrows():
        html_content += f"""
            <tr>
                <td>{row['Variation'].title()}</td>
                <td>{row['Pass Rate (%)']}%</td>
            </tr>
        """
        
    html_content += """
        </table>

        <h2>Detailed Results</h2>
        <table class="details-table">
            <tr>
                <th>ID</th>
                <th>Variation</th>
                <th>Status</th>
                <th>Description</th>
                <th>Expected vs Actual (Network)</th>
                <th>Expected vs Actual (Code)</th>
                <th>Confidence</th>
            </tr>
    """
    
    for _, row in df.iterrows():
        row_class = "row-pass" if row['status'] == 'PASS' else "row-fail"
        status_class = "pass" if row['status'] == 'PASS' else "fail"
        
        html_content += f"""
            <tr class="{row_class}">
                <td>{row['dispute_id']}</td>
                <td>{row['variation_type']}</td>
                <td class="{status_class}">{row['status']}</td>
                <td>{row['description']}</td>
                <td>{row['expected_network']} vs {row['actual_network']}</td>
                <td>{row['expected_code']} vs {row['actual_code']}</td>
                <td>{row['confidence']}</td>
            </tr>
        """
        
    html_content += """
        </table>
    </body>
    </html>
    """
    
    with open(HTML_PATH, 'w') as f:
        f.write(html_content)
        
    print(f"HTML report generated at: {HTML_PATH}")

if __name__ == "__main__":
    generate_html_report()

