import asyncio
import sys
import os
import json
import logging
from collections import defaultdict
from typing import Dict, Any

# Adjust path to include the project root
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.insert(0, project_root)

# Import backend modules
try:
    from backend.phases.classify_v2_trace import classify_dispute_v2_trace
except ImportError as e:
    print(f"Error importing modules: {e}")
    sys.exit(1)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

DATASET_PATH = os.path.join(project_root, "synthetic_data/phase1/golden_set/natural_language_classification.json")
OUTPUT_PATH = os.path.join(project_root, "qualitative/phase1/natural_language_trace_results.json")

class NaturalLanguageTraceTester:
    def __init__(self, concurrency: int = 5):
        self.semaphore = asyncio.Semaphore(concurrency)
        self.results = []
        self.stats = defaultdict(lambda: {"total": 0, "passed": 0})

    async def run_case(self, case: Dict[str, Any]):
        async with self.semaphore:
            dispute_id = case["dispute_id"]
            variation_type = case.get("variation_type", "unknown")
            
            logger.info(f"Running {variation_type} case: {dispute_id}...")
            
            task_input = {
                "dispute_id": dispute_id,
                "description": case["description"],
                "current_date": "2023-10-27"
            }

            try:
                result, trace = await classify_dispute_v2_trace(task_input)
                
                # Evaluation
                expected_network = case["network"]
                expected_category = case["category"]
                expected_code = case["true_reason_code"]
                
                actual_network = result["network"]
                actual_category = result["category"]
                actual_code = result["reason_code"]
                
                network_match = actual_network == expected_network
                # category_match: strictly checking if the identified category matches the expected one
                category_match = actual_category == expected_category
                code_match = actual_code == expected_code
                
                status = "PASS" if (network_match and code_match) else "FAIL"
                
                # Determine failure stage
                failure_stage = None
                if not network_match:
                    failure_stage = "FAILURE_NETWORK"
                elif not category_match:
                    # Note: We flag category mismatch, but if code matches, it's less critical. 
                    # However, strictly speaking, it's a deviation in flow.
                    failure_stage = "FAILURE_CATEGORY"
                elif not code_match:
                    failure_stage = "FAILURE_CODE"
                
                # Track stats
                self.stats[variation_type]["total"] += 1
                if status == "PASS":
                    self.stats[variation_type]["passed"] += 1

                self.results.append({
                    "case": case,
                    "result": result,
                    "trace": trace,
                    "status": status,
                    "failure_stage": failure_stage,
                    "metrics": {
                        "network_match": network_match,
                        "category_match": category_match,
                        "code_match": code_match
                    }
                })
                
            except Exception as e:
                logger.error(f"Case {dispute_id} failed: {e}", exc_info=True)
                self.results.append({
                    "case": case,
                    "status": "ERROR",
                    "error": str(e),
                    "trace": {"error": str(e)}
                })
                self.stats[variation_type]["total"] += 1

    async def run_all(self):
        if not os.path.exists(DATASET_PATH):
            logger.error(f"Dataset not found at {DATASET_PATH}")
            return

        with open(DATASET_PATH, 'r') as f:
            test_cases = json.load(f)
            
        logger.info(f"Loaded {len(test_cases)} test cases.")
        
        tasks = [self.run_case(case) for case in test_cases]
        await asyncio.gather(*tasks)

    def save_results(self):
        os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
        with open(OUTPUT_PATH, 'w') as f:
            json.dump(self.results, f, indent=2)
        print(f"\nTrace results saved to {OUTPUT_PATH}")

    def print_summary(self):
        print("\n" + "="*60)
        print(f"TRACE TEST SUMMARY (V2)")
        print("="*60)
        print(f"{'Variation':<15} | {'Total':<8} | {'Passed':<8} | {'Rate':<8}")
        print("-" * 60)
        
        total_cases = 0
        total_passed = 0
        
        for variation, stats in self.stats.items():
            rate = (stats["passed"] / stats["total"]) * 100 if stats["total"] > 0 else 0
            print(f"{variation:<15} | {stats['total']:<8} | {stats['passed']:<8} | {rate:.1f}%")
            
            total_cases += stats["total"]
            total_passed += stats["passed"]
            
        print("-" * 60)
        total_rate = (total_passed / total_cases) * 100 if total_cases > 0 else 0
        print(f"{'TOTAL':<15} | {total_cases:<8} | {total_passed:<8} | {total_rate:.1f}%")
        print("="*60)

async def main():
    tester = NaturalLanguageTraceTester(concurrency=10)
    await tester.run_all()
    tester.print_summary()
    tester.save_results()

if __name__ == "__main__":
    asyncio.run(main())

