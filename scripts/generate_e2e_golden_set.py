import json
import os
import re
import hashlib
from pathlib import Path

import copy

# Paths
BASE_DIR = Path("lesson-18/dispute-chatbot/synthetic_data/phase1")
GOLDEN_SET_DIR = BASE_DIR / "golden_set"
EVIDENCE_DIR = BASE_DIR / "evidence"

CLASSIFICATION_FILE = GOLDEN_SET_DIR / "natural_language_classification.json"
TRANSACTIONS_FILE = EVIDENCE_DIR / "transaction_histories.json"
SHIPPING_FILE = EVIDENCE_DIR / "shipping_records.json"
CUSTOMER_FILE = EVIDENCE_DIR / "customer_profiles.json"
OUTPUT_FILE = GOLDEN_SET_DIR / "e2e_evaluation_set.json"

def load_data():
    """
    Loads the classification and evidence datasets.
    """
    print(f"Loading data from {BASE_DIR}...")
    
    try:
        with open(CLASSIFICATION_FILE, 'r') as f:
            classification_data = json.load(f)
        print(f"Loaded {len(classification_data)} classification records.")

        with open(TRANSACTIONS_FILE, 'r') as f:
            transactions_data = json.load(f)
        print(f"Loaded {len(transactions_data)} transaction histories.")
        
        with open(SHIPPING_FILE, 'r') as f:
            shipping_data = json.load(f)
        print(f"Loaded {len(shipping_data)} shipping records.")

        with open(CUSTOMER_FILE, 'r') as f:
            customer_data = json.load(f)
        print(f"Loaded {len(customer_data)} customer profiles.")
        
        return classification_data, transactions_data, shipping_data, customer_data

    except FileNotFoundError as e:
        print(f"Error loading files: {e}")
        return None, None, None, None

def extract_semantic_features(text):
    """
    Extracts semantic features like Amount and Merchant from the complaint text.
    """
    features = {}
    
    # 1. Extract Amount (e.g., "$45.50", "500 USD", "$ 100")
    # Matches $ followed by digits and optional decimals
    amount_match = re.search(r'\$\s?(\d+(?:\.\d{2})?)', text)
    if amount_match:
        try:
            features['amount'] = float(amount_match.group(1))
        except ValueError:
            pass
    
    # 2. Extract Merchant (Heuristic: "at [Merchant]", "from [Merchant]")
    # Improved: Matches Capitalized Words (Title Case) possibly separated by spaces
    merchant_match = re.search(r'(?:at|from)\s+([A-Z][a-zA-Z0-9\']+(?:\s+[A-Z][a-zA-Z0-9\']+)*)', text)
    if merchant_match:
        # cleanup trailing punctuation if picked up
        merchant = merchant_match.group(1).strip(" .,?!")
        # heuristic: avoid common non-merchants if they appear capitalized (simple stoplist)
        if merchant.lower() not in ["my", "the", "a", "an"]:
            features['merchant'] = merchant

    return features

def patch_evidence(evidence_record, features, reason_code):
    """
    Patches the evidence record with semantic features and logic requirements.
    """
    record = copy.deepcopy(evidence_record)
    
    # 1. Patch Transaction (Target the first one or most relevant)
    if record.get('ce3_transactions') and len(record['ce3_transactions']) > 0:
        txn = record['ce3_transactions'][0]
        
        if 'amount' in features:
            txn['amount'] = features['amount']
            
        if 'merchant' in features:
            # Assuming 'description' holds the merchant name in this dataset schema
            txn['description'] = features['merchant']
            
    # 2. Patch Shipping for 13.1 (Merchandise Not Received)
    # Logic: If user claims not received, evidence should show "Delivered" (conflict) 
    # or "In Transit" (happy path for claim?). 
    # PRD says: "ensure shipping_evidence shows 'Delivered' (to test the conflict) or 'In Transit'"
    # We will default to "Delivered" to simulate a valid evidence gathering that requires adjudication.
    if reason_code == '13.1':
        if not record.get('shipping'):
             record['shipping'] = {
                "carrier": "FedEx",
                "tracking_number": "TRK-GEN-" + hashlib.md5(record.get('dispute_id', '').encode()).hexdigest()[:8],
                "status": "Delivered",
                "delivery_date": "2025-01-15T10:00:00Z"
            }
        else:
            record['shipping']['status'] = "Delivered"

    return record

def link_and_generate():
    """
    Main logic to combine classification and evidence into a golden set.
    """
    classification_data, transactions_data, shipping_data, customer_data = load_data()
    
    if not classification_data or not transactions_data:
        print("Failed to load required data.")
        return

    output_dataset = []
    
    # Use transactions_data as the pool for base evidence
    evidence_pool = transactions_data
    
    for item in classification_data:
        dispute_id = item.get('dispute_id')
        description = item.get('description', '')
        reason_code = item.get('true_reason_code')
        
        # 1. Deterministic Selection
        # hash(dispute_id) % len(pool)
        h = hashlib.sha256(dispute_id.encode()).hexdigest()
        idx = int(h, 16) % len(evidence_pool)
        base_evidence = evidence_pool[idx]
        
        # 2. Extract Features
        features = extract_semantic_features(description)
        
        # 3. Patch Evidence
        patched_evidence = patch_evidence(base_evidence, features, reason_code)
        
        # 4. Construct Test Case
        # Ensure we keep the original dispute_id in the evidence so they link up in the runner
        patched_evidence['dispute_id'] = dispute_id
        
        test_case = {
            "input_dispute_id": dispute_id,
            "input_description": description,
            "expected_classification": {
                "reason_code": reason_code,
                "variation_type": item.get('variation_type')
            },
            "expected_evidence": patched_evidence,
            "extracted_features": features  # For debugging/verification
        }
        
        output_dataset.append(test_case)
        
    # Save to file
    print(f"Generating {len(output_dataset)} test cases...")
    with open(OUTPUT_FILE, 'w') as f:
        json.dump(output_dataset, f, indent=2)
    print(f"Saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    link_and_generate()

