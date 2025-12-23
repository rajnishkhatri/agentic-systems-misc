import json
import os
import sys

# Define paths
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
DATASET_PATH = os.path.join(project_root, "synthetic_data/phase1/golden_set/natural_language_classification.json")

def inject_network_context():
    print(f"Loading dataset from: {DATASET_PATH}")
    
    if not os.path.exists(DATASET_PATH):
        print("Error: Dataset file not found.")
        sys.exit(1)
        
    try:
        with open(DATASET_PATH, 'r') as f:
            data = json.load(f)
            
        print(f"Loaded {len(data)} records.")
        
        modified_count = 0
        for item in data:
            network = item.get("network")
            description = item.get("description")
            
            if network and description:
                # Check if network context is already present to avoid double injection
                network_context = f"(Network: {network.title()})"
                if network_context not in description:
                    item["description"] = f"{description} {network_context}"
                    modified_count += 1
        
        print(f"Modified {modified_count} records.")
        
        with open(DATASET_PATH, 'w') as f:
            json.dump(data, f, indent=2)
            
        print("Successfully saved updated dataset.")
        
    except Exception as e:
        print(f"An error occurred: {e}")
        sys.exit(1)

if __name__ == "__main__":
    inject_network_context()

