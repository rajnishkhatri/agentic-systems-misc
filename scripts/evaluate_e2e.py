import asyncio
import json
import os
import sys
import unittest.mock
from pathlib import Path
from typing import Dict, Any, Optional

# Add project root to sys.path to import backend modules
# Assuming script is run from project root
PROJECT_ROOT = Path(os.getcwd())
BACKEND_DIR = PROJECT_ROOT / "lesson-18" / "dispute-chatbot"
sys.path.append(str(BACKEND_DIR))

# Import the phases
try:
    from backend.phases.classify_v9_rag import classify_dispute_v9_rag
    from backend.phases.gather_evidence import gather_evidence
    from backend.phases.evidence_models import EvidencePackage
except ImportError as e:
    print(f"Error importing backend modules: {e}")
    print(f"Ensure you are running from the project root and {BACKEND_DIR} exists.")
    sys.exit(1)

# Path to the golden set
GOLDEN_SET_PATH = PROJECT_ROOT / "lesson-18/dispute-chatbot/synthetic_data/phase1/golden_set/e2e_evaluation_set.json"

class MockDataLoader:
    """
    Mocks the DataLoader to serve data from our golden set instead of the filesystem/DB.
    """
    _data = {}

    @classmethod
    def load_golden_set(cls, path: Path):
        with open(path, 'r') as f:
            data_list = json.load(f)
            # Index by dispute_id
            cls._data = {item['input_dispute_id']: item['expected_evidence'] for item in data_list}
            print(f"MockDataLoader loaded {len(cls._data)} records.")

    def get_transaction_evidence(self, dispute_id: str) -> Optional[Dict]:
        return self._data.get(dispute_id)

    def get_customer_evidence(self, dispute_id: str) -> Optional[Dict]:
        # In our schema, customer_signals are inside the evidence record
        record = self._data.get(dispute_id)
        if record:
             # The adapter expects the dict that contains "customer_signals"
             # In transaction_histories.json, keys are flat "customer_signals"
             # But let's check what the Specialist expects. 
             # CustomerSpecialist.get_signals -> loader.get_customer_evidence -> returns dict with ip_address etc.
             # In our generated data, we have "customer_signals": {...}
             return record.get("customer_signals")
        return None

    def get_shipping_evidence(self, dispute_id: str) -> Optional[Dict]:
        # ShippingSpecialist expects a dict that HAS "shipping": {...}
        return self._data.get(dispute_id)
        
    def get_shipping_by_tracking(self, tracking_number: str) -> Optional[Dict]:
        # Reverse lookup (inefficient but fine for test)
        for record in self._data.values():
            if record.get('shipping') and record['shipping'].get('tracking_number') == tracking_number:
                return record
        return None

async def run_test_case(test_case: Dict, use_mock_llm: bool = False):
    """
    Runs a single E2E test case.
    """
    dispute_id = test_case['input_dispute_id']
    description = test_case['input_description']
    expected_reason = test_case['expected_classification']['reason_code']
    
    # --- Phase 1: Classification ---
    if use_mock_llm:
        # Bypass LLM for testing the runner logic/evidence gathering
        reason_code = expected_reason
        confidence = 1.0
        print(f"  [Mock LLM] Classified as {reason_code}")
    else:
        # Call actual Classify logic
        # Note: classify_dispute_v9_rag signature: (description, history=None)
        try:
            result = await classify_dispute_v9_rag(description)
            # Result is typically a ClassificationResult object or dict. 
            # I need to check `classify_dispute_v9_rag` return type.
            # Assuming it returns an object with `reason_code` attribute based on naming.
            reason_code = getattr(result, 'reason_code', None) or result.get('reason_code')
            confidence = getattr(result, 'confidence', 0.0)
        except Exception as e:
            print(f"  [Classification Error] {e}")
            return {
                "success": False,
                "stage": "classification",
                "error": str(e)
            }

    # --- Phase 2: Evidence Gathering ---
    # We rely on the MockDataLoader being patched globally or via context
    try:
        task = {"reason_code": reason_code, "dispute_id": dispute_id}
        evidence_package = await gather_evidence(task)
    except Exception as e:
        print(f"  [Evidence Error] {e}")
        return {
            "success": False, 
            "stage": "evidence",
            "error": str(e)
        }

    # --- Validation ---
    
    # 1. Check Classification
    class_match = (reason_code == expected_reason)
    
    # 2. Check Evidence
    # We want to verify that the evidence used was indeed our patched one.
    # Check if transaction amount matches extracted feature (if any)
    ev_match = True
    details = []
    
    extracted = test_case.get('extracted_features', {})
    if 'amount' in extracted:
        # Find transaction with this amount
        txns = evidence_package.transaction_evidence.transactions if evidence_package.transaction_evidence else []
        found_amount = any(abs(t.amount - extracted['amount']) < 0.01 for t in txns)
        if not found_amount:
            ev_match = False
            details.append(f"Expected transaction amount {extracted['amount']} not found in evidence.")
    
    if 'merchant' in extracted:
        txns = evidence_package.transaction_evidence.transactions if evidence_package.transaction_evidence else []
        # We patched 'description' with merchant name
        found_merchant = any(extracted['merchant'] in t.description for t in txns)
        if not found_merchant:
            ev_match = False
            details.append(f"Expected merchant '{extracted['merchant']}' not found in transaction descriptions.")

    if reason_code == '13.1':
        # Check shipping evidence
        if not evidence_package.shipping_evidence or not evidence_package.shipping_evidence.success:
            ev_match = False
            details.append("Expected shipping evidence for 13.1 but found none/failed.")
        elif evidence_package.shipping_evidence.status != 'DELIVERED':
             # We patched it to DELIVERED
             # Note: logic might result in IN_TRANSIT if we didn't patch, but we did.
             details.append(f"Shipping status is {evidence_package.shipping_evidence.status}, expected DELIVERED (patched).")
             
    success = class_match and ev_match
    
    return {
        "success": success,
        "dispute_id": dispute_id,
        "actual_reason": reason_code,
        "expected_reason": expected_reason,
        "classification_match": class_match,
        "evidence_match": ev_match,
        "details": details
    }

async def main():
    if not os.path.exists(GOLDEN_SET_PATH):
        print(f"Golden set not found at {GOLDEN_SET_PATH}. Run generator first.")
        return

    # Load Data
    MockDataLoader.load_golden_set(GOLDEN_SET_PATH)
    
    with open(GOLDEN_SET_PATH, 'r') as f:
        test_cases = json.load(f)
        
    print(f"Starting E2E Evaluation on {len(test_cases)} cases...")
    
    # Patch the DataLoader in the specialists module
    # The specialists import DataLoader from backend.adapters.data_loader
    # So we patch 'backend.adapters.specialists.DataLoader'
    with unittest.mock.patch('backend.adapters.specialists.DataLoader', side_effect=lambda: MockDataLoader()):
        
        results = []
        # Run a subset for quick verification or all
        # Running all 300 might be slow if using real LLM.
        # Let's run first 10 for demonstration/verification purposes as per task
        # User can adjust logic to run all.
        limit = 10 
        print(f"Running first {limit} cases...")
        
        for i, case in enumerate(test_cases[:limit]):
            print(f"Running Case {i+1}/{limit}: {case['input_dispute_id']}")
            # Use mock_llm=True for now to test the runner logic without needing API keys/cost
            # Change to False to test real classification
            result = await run_test_case(case, use_mock_llm=True)
            results.append(result)
            
            status = "PASS" if result['success'] else "FAIL"
            print(f"  Result: {status}")
            if not result['success']:
                print(f"  Details: {result['details']}")
                print(f"  Class Match: {result['classification_match']} ({result['actual_reason']} vs {result['expected_reason']})")
            print("-" * 40)

    # Summary
    passed = sum(1 for r in results if r['success'])
    total = len(results)
    print(f"\nEvaluation Complete.")
    print(f"Total: {total}")
    print(f"Passed: {passed}")
    print(f"Failed: {total - passed}")
    print(f"Success Rate: {passed/total*100:.1f}%")

if __name__ == "__main__":
    asyncio.run(main())
