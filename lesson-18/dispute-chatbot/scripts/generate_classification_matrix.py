import json
import csv
from pathlib import Path
from collections import defaultdict

# Paths
# Script at: lesson-18/dispute-chatbot/scripts/generate_classification_matrix.py
# Root should be: lesson-18/
BASE_DIR = Path(__file__).resolve().parents[2] 
GOLDEN_SET_PATH = BASE_DIR / "dispute-chatbot/synthetic_data/phase1/golden_set/diverse_classification_labels.json"
CATALOG_PATH = BASE_DIR / "dispute-schema/reason_codes_catalog.csv"
OUTPUT_REPORT_PATH = BASE_DIR / "dispute-chatbot/qualitative/phase1/classification_coverage_matrix.md"

def load_catalog():
    catalog = {}
    with open(CATALOG_PATH, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Create a lookup key
            key = (row['Network'].lower(), row['reason_code'])
            catalog[key] = row
    return catalog

def generate_matrix():
    if not GOLDEN_SET_PATH.exists():
        print(f"Golden set not found at {GOLDEN_SET_PATH}")
        return

    with open(GOLDEN_SET_PATH, 'r', encoding='utf-8') as f:
        data = json.load(f)

    catalog = load_catalog()
    
    # Structure: Network -> Group -> [Rows]
    matrix = defaultdict(lambda: defaultdict(list))
    
    for case in data:
        network = case['network']
        reason_code = case['true_reason_code']
        
        # Look up catalog metadata
        cat_entry = catalog.get((network, reason_code))
        
        group = "Unknown"
        if cat_entry:
            group = cat_entry.get('reason_code_group', 'Unknown')
            
        matrix[network][group].append({
            "code": reason_code,
            "desc": case['description'],
            "category": case['category']
        })

    # Generate Markdown
    md_output = ["# Classification Coverage Matrix\n"]
    md_output.append(f"**Total Test Cases:** {len(data)}\n")
    
    # Sort networks for consistency
    for network in sorted(matrix.keys()):
        md_output.append(f"## Network: {network.title()}\n")
        
        groups = matrix[network]
        for group in sorted(groups.keys()):
            md_output.append(f"### Group: {group.replace('_', ' ').title()}\n")
            md_output.append("| Reason Code | Category | Test Description Sample |")
            md_output.append("|---|---|---|")
            
            for item in sorted(groups[group], key=lambda x: x['code']):
                # Truncate desc for table readability
                desc_snippet = item['desc'][:60] + "..." if len(item['desc']) > 60 else item['desc']
                md_output.append(f"| **{item['code']}** | {item['category']} | {desc_snippet} |")
            
            md_output.append("\n")
            
    # Write to file
    OUTPUT_REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_REPORT_PATH, 'w', encoding='utf-8') as f:
        f.write("\n".join(md_output))
        
    print(f"Matrix report generated at: {OUTPUT_REPORT_PATH}")

if __name__ == "__main__":
    generate_matrix()

