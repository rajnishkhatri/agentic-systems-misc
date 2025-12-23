import csv
import json
import os

def load_reason_code_mapping(csv_path):
    mapping = {}
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Create a key based on network and reason_code
            # The CSV has 'Network' and 'reason_code' columns
            key = (row['Network'].lower(), row['reason_code'])
            mapping[key] = row['reason_code_group']
    return mapping

def refine_labels(json_path, csv_path, output_path):
    print(f"Loading reason code catalog from {csv_path}...")
    reason_code_group_map = load_reason_code_mapping(csv_path)
    
    print(f"Loading classification data from {json_path}...")
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    modified_count = 0
    for entry in data:
        network = entry.get('network', '').lower()
        code = entry.get('true_reason_code')
        category = entry.get('category')
        
        # Look up reason_code_group using (network, code)
        # Note: CSV network names might differ slightly in casing, handled by .lower()
        # Some codes might not be in CSV, handle gracefully
        group = reason_code_group_map.get((network, code))
        
        original_category = category
        
        # Transformation Logic
        
        # 1. Authorization Fix
        if category == 'general' and group == 'authorization':
            entry['category'] = 'authorization'
            
        # 2. Incorrect Amount Fix
        elif code in ['P05', '12.5'] and category == 'general':
            entry['category'] = 'incorrect_amount'
            
        # 3. Credit Not Processed Fix
        elif code == '13.8' and category == 'general':
            entry['category'] = 'credit_not_processed'
            
        # 4. Processing Error Fix
        elif code == 'QUOTA_EXCEEDED' and category == '':
            entry['category'] = 'processing_error'
            
        if entry['category'] != original_category:
            modified_count += 1
            # print(f"Modified {entry['dispute_id']}: {original_category} -> {entry['category']} (Code: {code}, Group: {group})")

    print(f"Total entries modified: {modified_count}")
    
    print(f"Saving refined data to {output_path}...")
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)
    print("Done.")

if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    # Adjust paths relative to workspace root if running from root, or use absolute paths construction
    # Assuming script is run from workspace root
    workspace_root = os.getcwd()
    
    csv_path = os.path.join(workspace_root, 'lesson-18/dispute-schema/reason_codes_catalog.csv')
    json_path = os.path.join(workspace_root, 'lesson-18/dispute-chatbot/synthetic_data/phase1/golden_set/natural_language_classification.json')
    output_path = os.path.join(workspace_root, 'lesson-18/dispute-chatbot/synthetic_data/phase1/golden_set/natural_language_classification_v2.json')
    
    refine_labels(json_path, csv_path, output_path)

