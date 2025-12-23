import csv
import json
import random
from pathlib import Path
from typing import List, Dict

# Hardcoded absolute path to bypass resolution issues
# Workspace root: /Users/rajnishkhatri/Documents/recipe-chatbot
ROOT_DIR = Path("/Users/rajnishkhatri/Documents/recipe-chatbot")
CATALOG_PATH = ROOT_DIR / "lesson-18/dispute-schema/reason_codes_catalog.csv"
OUTPUT_PATH = ROOT_DIR / "lesson-18/dispute-chatbot/synthetic_data/phase1/golden_set/diverse_classification_labels.json"

# Helper to generate synthetic descriptions based on category/description
def generate_description(row: Dict[str, str]) -> str:
    desc = row['description']
    category = row['unified_category']
    network = row['Network']  # Note: Capitalized in CSV based on previous reads
    
    templates = {
        "fraudulent": [
            f"I did not make this transaction. It is fraud. ({desc})",
            "My card was stolen and used for this charge.",
            "I don't recognize this charge at all.",
            "Unauthorized transaction on my account."
        ],
        "product_not_received": [
            f"I ordered this but never received it. ({desc})",
            "The package never arrived.",
            "Tracking says delivered but I don't have it.",
            "It's been weeks and I still haven't gotten my order."
        ],
        "duplicate": [
            f"I was charged twice for the same thing. ({desc})",
            "This is a duplicate charge.",
            "I see two identical transactions on my statement."
        ],
        "subscription_canceled": [
            f"I canceled this subscription but was still charged. ({desc})",
            "Recurring billing should have stopped.",
            "I ended my membership last month."
        ],
        "product_unacceptable": [
            f"The item is damaged/defective. ({desc})",
            "This is not what I ordered.",
            "The quality is terrible and I want a refund.",
            "It arrived broken."
        ],
        "credit_not_processed": [
            f"I returned the item but haven't received my refund. ({desc})",
            "Where is my credit?",
            "Merchant promised a refund but I don't see it."
        ],
        "unrecognized": [
            f"I don't recall this transaction. ({desc})",
            "What is this charge for?",
            "I need more information about this."
        ],
        "general": [
            f"I am disputing this charge: {desc}",
            "This transaction is incorrect.",
            "There is an issue with this payment."
        ]
    }
    
    # Fallback to general if category not found
    options = templates.get(category, templates["general"])
    base_text = random.choice(options)
    
    # Add some network specificity occasionally
    if random.random() < 0.3:
        base_text += f" This is on my {network.title()} card."
        
    return base_text

def main():
    print(f"Checking catalog at: {CATALOG_PATH}")
    if not CATALOG_PATH.exists():
        print(f"Error: Catalog not found at {CATALOG_PATH}")
        return

    test_cases = []
    
    try:
        with open(CATALOG_PATH, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for i, row in enumerate(reader):
                # Skip rows with empty required fields
                if not row.get('reason_code') or not row.get('Network'):
                    continue
                    
                # Generate a test case for EACH row in the catalog to ensure full coverage
                case = {
                    "dispute_id": f"disp_diverse_{i:03d}",
                    "description": generate_description(row),
                    "true_reason_code": row['reason_code'],
                    "network": row['Network'].lower(),
                    "category": row['unified_category'],
                    # Is fraud if category is fraudulent
                    "is_fraud": row['unified_category'] == "fraudulent",
                    "expected_confidence": 0.90
                }
                test_cases.append(case)
                
        # Ensure output directory exists
        OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
        
        with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
            json.dump(test_cases, f, indent=2)
            
        print(f"Successfully generated {len(test_cases)} diverse test cases.")
        print(f"Saved to: {OUTPUT_PATH}")
        
    except Exception as e:
        print(f"Failed to generate dataset: {e}")

if __name__ == "__main__":
    main()

