import json
import csv
import os
import random
from collections import Counter
from sklearn.model_selection import train_test_split

def load_catalog(catalog_path):
    reason_code_map = {}
    with open(catalog_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            code = row.get('reason_code')
            group = row.get('reason_code_group')
            if code and group:
                reason_code_map[code] = group
    return reason_code_map

def prepare_data():
    # Use absolute paths or relative to workspace root
    # Assuming script is run from project root or we can find files relative to this script
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # backend/phases -> ... -> lesson-18
    # lesson-18/dispute-chatbot/backend/phases
    
    # Resolving paths relative to workspace root (assuming CWD is workspace root)
    base_dir = "lesson-18"
    catalog_path = os.path.join(base_dir, "dispute-schema/reason_codes_catalog.csv")
    json_path = os.path.join(base_dir, "dispute-chatbot/synthetic_data/phase1/golden_set/natural_language_classification_v2.json")
    output_dir = os.path.join(base_dir, "dispute-chatbot/synthetic_data/phase1/dspy")
    
    # Check if files exist
    if not os.path.exists(catalog_path):
        print(f"Error: Catalog file not found at {catalog_path}")
        return
    if not os.path.exists(json_path):
        print(f"Error: Data file not found at {json_path}")
        return
        
    os.makedirs(output_dir, exist_ok=True)
    
    print(f"Loading catalog from {catalog_path}...")
    reason_code_map = load_catalog(catalog_path)
    print(f"Loaded {len(reason_code_map)} reason codes.")
    
    print(f"Loading data from {json_path}...")
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    print(f"Original records: {len(data)}")
    
    processed_data = []
    missing_codes = set()
    
    for item in data:
        code = item.get('true_reason_code')
        if code in reason_code_map:
            new_category = reason_code_map[code]
            
            # Map specific reason_code_groups if needed
            # For now, we use the CSV 'reason_code_group' directly.
            
            # Create a simplified DSPy example structure or keep full
            # We keep full but ensure 'category' is the target label
            item['original_category'] = item['category']
            item['category'] = new_category
            processed_data.append(item)
        else:
            if code:
                missing_codes.add(code)
            
    if missing_codes:
        print(f"Warning: {len(missing_codes)} reason codes not found in catalog: {missing_codes}")
        
    print(f"Processed records: {len(processed_data)}")
    
    labels = [item['category'] for item in processed_data]
    
    print("\nOverall Distribution:")
    dist_all = Counter(labels)
    for k, v in dist_all.most_common():
        print(f"  {k}: {v}")

    # Remove classes with < 2 samples for stratified split or fall back to random split
    valid_indices = [i for i, label in enumerate(labels) if dist_all[label] >= 2]
    if len(valid_indices) < len(labels):
        print(f"\nWarning: Removing {len(labels) - len(valid_indices)} items with unique labels for splitting purposes (or handle differently).")
        # For now, let's just proceed with random split if stratification fails, 
        # or we can just try stratified and if it fails, catch it (which we did).
    
    # Stratified split: 80% Train, 10% Dev, 10% Test
    # 1. Split 80% Train vs 20% Temp
    try:
        train_data, temp_data, train_labels, temp_labels = train_test_split(
            processed_data, labels, test_size=0.2, stratify=labels, random_state=42
        )
        
        # 2. Split Temp into 50% Dev (10% total) and 50% Test (10% total)
        # We need to ensure temp_labels also has >= 2 per class for the second split
        # This is tricky with small datasets. 
        # If a class has 2 items, 1 goes to train, 1 to temp. 
        # Then splitting temp (1 item) will fail stratification.
        
        # Strategy: Ensure minimal samples for Dev/Test. 
        # If class count < 5, maybe just put in Train? Or duplicate?
        
        dev_data, test_data = train_test_split(
            temp_data, test_size=0.5, stratify=temp_labels, random_state=42
        )
    except ValueError as e:
        print(f"Error during splitting (likely class imbalance for stratification): {e}")
        print("Falling back to non-stratified split.")
        train_data, temp_data = train_test_split(processed_data, test_size=0.2, random_state=42)
        dev_data, test_data = train_test_split(temp_data, test_size=0.5, random_state=42)
    
    print(f"Train set: {len(train_data)}")
    print(f"Dev set: {len(dev_data)}")
    print(f"Test set: {len(test_data)}")
    
    def save_json(data, filename):
        path = os.path.join(output_dir, filename)
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
        print(f"Saved {path}")

    save_json(train_data, "train.json")
    save_json(dev_data, "dev.json")
    save_json(test_data, "test.json")
    
    print("\nTrain Distribution:")
    dist = Counter([d['category'] for d in train_data])
    for k, v in dist.most_common():
        print(f"  {k}: {v}")

if __name__ == "__main__":
    prepare_data()

