import asyncio
import sys
import os
import json
import datetime
import logging
from typing import List, Dict, Any
from dataclasses import dataclass
from collections import defaultdict
import pandas as pd

# Adjust path to include the project root (lesson-18/dispute-chatbot)
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.insert(0, project_root)

# Import backend modules
try:
    from backend.phases.classify import classify_dispute
    from utils.llm_service import get_default_service
except ImportError as e:
    print(f"Error importing modules: {e}")
    sys.exit(1)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

DATASET_PATH = os.path.join(project_root, "synthetic_data/phase1/golden_set/natural_language_classification.json")
RESULTS_PATH = os.path.join(project_root, "qualitative/phase1/natural_language_results.csv")

class NaturalLanguageTester:
    def __init__(self, concurrency: int = 5):
        self.semaphore = asyncio.Semaphore(concurrency)
        self.results = []
        self.variation_stats = defaultdict(lambda: {"total": 0, "passed": 0})

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
                result = await classify_dispute(task_input)
                
                # Evaluation
                # For network: exact match
                network_match = result["network"] == case["network"]
                
                # For reason code: exact match
                code_match = result["reason_code"] == case["true_reason_code"]
                
                # For category: exact match
                category_match = result["category"] == case["category"]
                
                status = "PASS" if network_match and code_match else "FAIL"
                
                # Track stats
                self.variation_stats[variation_type]["total"] += 1
                if status == "PASS":
                    self.variation_stats[variation_type]["passed"] += 1

                self.results.append({
                    "dispute_id": dispute_id,
                    "variation_type": variation_type,
                    "status": status,
                    "expected_network": case["network"],
                    "actual_network": result["network"],
                    "network_match": network_match,
                    "expected_category": case["category"],
                    "actual_category": result["category"],
                    "category_match": category_match,
                    "expected_code": case["true_reason_code"],
                    "actual_code": result["reason_code"],
                    "code_match": code_match,
                    "confidence": result.get("classification_confidence", 0.0),
                    "reasoning": result.get("classification_reasoning", ""),
                    "description": case["description"]
                })
                
            except Exception as e:
                logger.error(f"Case {dispute_id} failed: {e}")
                self.results.append({
                    "dispute_id": dispute_id,
                    "variation_type": variation_type,
                    "status": "ERROR",
                    "error": str(e),
                    "description": case["description"]
                })
                self.variation_stats[variation_type]["total"] += 1

    async def run_all(self):
        if not os.path.exists(DATASET_PATH):
            logger.error(f"Dataset not found at {DATASET_PATH}")
            return

        with open(DATASET_PATH, 'r') as f:
            test_cases = json.load(f)
            
        logger.info(f"Loaded {len(test_cases)} test cases.")
        
        tasks = [self.run_case(case) for case in test_cases]
        await asyncio.gather(*tasks)

    def print_summary(self):
        print("\n" + "="*60)
        print(f"NATURAL LANGUAGE TEST SUMMARY")
        print("="*60)
        print(f"{'Variation':<15} | {'Total':<8} | {'Passed':<8} | {'Rate':<8}")
        print("-" * 60)
        
        total_cases = 0
        total_passed = 0
        
        for variation, stats in self.variation_stats.items():
            rate = (stats["passed"] / stats["total"]) * 100 if stats["total"] > 0 else 0
            print(f"{variation:<15} | {stats['total']:<8} | {stats['passed']:<8} | {rate:.1f}%")
            
            total_cases += stats["total"]
            total_passed += stats["passed"]
            
        print("-" * 60)
        total_rate = (total_passed / total_cases) * 100 if total_cases > 0 else 0
        print(f"{'TOTAL':<15} | {total_cases:<8} | {total_passed:<8} | {total_rate:.1f}%")
        print("="*60)

    def save_results(self):
        os.makedirs(os.path.dirname(RESULTS_PATH), exist_ok=True)
        df = pd.DataFrame(self.results)
        df.to_csv(RESULTS_PATH, index=False)
        print(f"\nDetailed CSV results saved to {RESULTS_PATH}")

async def main():
    tester = NaturalLanguageTester(concurrency=10)
    await tester.run_all()
    tester.print_summary()
    tester.save_results()

if __name__ == "__main__":
    asyncio.run(main())


