import asyncio
import sys
import os
import json
import datetime
import logging
from typing import List, Dict, Any
from dataclasses import dataclass, asdict

# Adjust path to include the project root (lesson-18/dispute-chatbot)
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.append(project_root)

# Import backend modules
try:
    from backend.phases.classify import classify_dispute
    from utils.llm_service import get_default_service
except ImportError as e:
    print(f"Error importing modules: {e}")
    print(f"Current path: {sys.path}")
    sys.exit(1)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class TestScenario:
    id: str
    description: str
    expected_reason_code: str
    expected_network: str
    tags: List[str]

class HumanScriptGenerator:
    """Generates curated test scenarios based on open coding dimensions."""
    
    @staticmethod
    def get_scenarios() -> List[TestScenario]:
        return [
            # 1. Fraud Vector (Visa 10.4)
            TestScenario(
                id="fraud_01",
                description="I never signed up for this! My card was in my wallet the whole time. This $500 charge to 'TechServe' is a scam!",
                expected_reason_code="10.4",
                expected_network="visa",
                tags=["fraud", "visa", "emotional"]
            ),
            TestScenario(
                id="fraud_02",
                description="Unrecognized transaction on my statement. I don't know who 'Online Services Ltd' is.",
                expected_reason_code="10.4",
                expected_network="visa",
                tags=["fraud", "visa", "neutral"]
            ),
            TestScenario(
                id="fraud_03",
                description="My card was lost last weekend and I see these charges I definitely didn't make.",
                expected_reason_code="10.4",
                expected_network="visa",
                tags=["fraud", "visa", "lost_card"]
            ),
            TestScenario(
                id="fraud_04",
                description="Someone used my card number online. I still have the card but I didn't authorize this purchase.",
                expected_reason_code="10.4",
                expected_network="visa",
                tags=["fraud", "visa", "cnp"]
            ),

            # 2. Merchandise Vector (Visa 13.1)
            TestScenario(
                id="merch_01",
                description="I ordered a laptop on Oct 1st. Tracking says delivered but I have nothing. Seller is not responding.",
                expected_reason_code="13.1",
                expected_network="visa",
                tags=["product_not_received", "visa", "neutral"]
            ),
             TestScenario(
                id="merch_02",
                description="Package never arrived. It's been 3 weeks past the delivery date.",
                expected_reason_code="13.1",
                expected_network="visa",
                tags=["product_not_received", "visa", "late"]
            ),
            TestScenario(
                id="merch_03",
                description="I paid for next day shipping but the item hasn't even shipped yet. It's been 5 days.",
                expected_reason_code="13.1",
                expected_network="visa",
                tags=["product_not_received", "visa", "shipping"]
            ),

            # 3. Subscription Vector (Visa 13.2)
            TestScenario(
                id="sub_01",
                description="I canceled my gym membership two months ago in writing, but you guys keep charging me $50/month. Stop it!",
                expected_reason_code="13.2",
                expected_network="visa",
                tags=["subscription_canceled", "visa", "frustrated"]
            ),
            TestScenario(
                id="sub_02",
                description="This was supposed to be a free trial. I canceled before the 7 days were up but got charged anyway.",
                expected_reason_code="13.2",
                expected_network="visa",
                tags=["subscription_canceled", "visa", "trial"]
            ),
             TestScenario(
                id="sub_03",
                description="Recurring billing was cancelled on your website on Jan 15th. Why am I charged on Feb 1st?",
                expected_reason_code="13.2",
                expected_network="visa",
                tags=["subscription_canceled", "visa", "neutral"]
            ),

            # 4. Quality Vector (Visa 13.3)
            TestScenario(
                id="qual_01",
                description="The shoes arrived but the sole is peeling off. They are clearly used. I want a refund.",
                expected_reason_code="13.3",
                expected_network="visa",
                tags=["product_unacceptable", "visa", "damaged"]
            ),
            TestScenario(
                id="qual_02",
                description="Item description said 100% cotton but the shirt is synthetic polyester. Not what I ordered.",
                expected_reason_code="13.3",
                expected_network="visa",
                tags=["product_unacceptable", "visa", "misrepresentation"]
            ),
             TestScenario(
                id="qual_03",
                description="The vase arrived shattered in pieces. Poor packaging.",
                expected_reason_code="13.3",
                expected_network="visa",
                tags=["product_unacceptable", "visa", "broken"]
            ),

            # 5. Duplicate Vector (Visa 12.6)
            TestScenario(
                id="dup_01",
                description="I see two charges for the same amount on the same day. I only pushed the button once.",
                expected_reason_code="12.6.1", # Updated to specific code
                expected_network="visa",
                tags=["duplicate", "visa", "confused"]
            ),
            TestScenario(
                id="dup_02",
                description="Charged twice for the same meal at the restaurant.",
                expected_reason_code="12.6.1", # Updated to specific code
                expected_network="visa",
                tags=["duplicate", "visa", "neutral"]
            ),

            # 6. Credit Not Processed (Visa 13.6)
            TestScenario(
                id="credit_01",
                description="I returned the item and they sent me a credit receipt, but the refund hasn't appeared on my card after 10 days.",
                expected_reason_code="13.6", 
                expected_network="visa",
                tags=["credit_not_processed", "visa", "refund_missing"]
            ),

            # 7. Network Robustness
            TestScenario(
                id="net_mc_01",
                description="My Mastercard shows a transaction I didn't make.",
                expected_reason_code="4837", # Mastercard fraud code
                expected_network="mastercard",
                tags=["fraud", "mastercard", "robustness"]
            ),
            TestScenario(
                id="net_amex_01",
                description="I need to dispute a charge on my Amex card. The hotel overcharged me.",
                expected_reason_code="P05", # Updated to "Incorrect Charge Amount" which matches "overcharged"
                expected_network="amex",
                tags=["general", "amex", "robustness"]
            ),
            
            # 8. Ambiguity / General
             TestScenario(
                id="amb_01",
                description="I don't recognize this.",
                expected_reason_code="10.4", # Likely fraud default
                expected_network="visa", # Default
                tags=["unrecognized", "ambiguous"]
            ),
             TestScenario(
                id="amb_02",
                description="Charge error.",
                expected_reason_code="10.4", # Or general
                expected_network="visa",
                tags=["general", "ambiguous"]
            )
        ]

class StressTester:
    def __init__(self, concurrency: int = 5):
        self.semaphore = asyncio.Semaphore(concurrency)
        self.results = []

    async def run_scenario(self, scenario: TestScenario):
        async with self.semaphore:
            logger.info(f"Running scenario {scenario.id}...")
            start_time = datetime.datetime.now()
            
            task_input = {
                "dispute_id": f"disp_test_{scenario.id}",
                "description": scenario.description,
                "current_date": "2023-10-27" # Fixed date for deterministic testing
            }

            try:
                result = await classify_dispute(task_input)
                
                # Check results
                reason_match = result["reason_code"] == scenario.expected_reason_code
                network_match = result["network"] == scenario.expected_network.lower()
                
                # Handle partial matches or "good enough" for robustness tests if needed
                # For now, strict match
                
                status = "PASS" if reason_match and network_match else "FAIL"
                
                duration = (datetime.datetime.now() - start_time).total_seconds()
                
                self.results.append({
                    "id": scenario.id,
                    "status": status,
                    "description": scenario.description,
                    "expected_reason": scenario.expected_reason_code,
                    "actual_reason": result["reason_code"],
                    "expected_network": scenario.expected_network,
                    "actual_network": result["network"],
                    "confidence": result.get("classification_confidence"),
                    "reasoning": result.get("classification_reasoning"),
                    "duration": duration,
                    "tags": scenario.tags
                })
                
                logger.info(f"Scenario {scenario.id} finished: {status}")
                
            except Exception as e:
                logger.error(f"Scenario {scenario.id} failed with error: {e}")
                self.results.append({
                    "id": scenario.id,
                    "status": "ERROR",
                    "error": str(e),
                    "tags": scenario.tags
                })

    async def run_all(self, scenarios: List[TestScenario]):
        tasks = [self.run_scenario(s) for s in scenarios]
        await asyncio.gather(*tasks)

    def print_summary(self):
        print("\n" + "="*80)
        print(f"{'ID':<12} | {'Status':<6} | {'Exp Code':<8} | {'Act Code':<8} | {'Exp Net':<8} | {'Act Net':<8}")
        print("-" * 80)
        
        pass_count = 0
        total_count = len(self.results)
        
        for res in self.results:
            if res["status"] == "PASS":
                pass_count += 1
            
            print(f"{res.get('id'):<12} | {res.get('status'):<6} | "
                  f"{res.get('expected_reason', ''):<8} | {res.get('actual_reason', ''):<8} | "
                  f"{res.get('expected_network', ''):<8} | {res.get('actual_network', ''):<8}")

        print("="*80)
        print(f"Total Scenarios: {total_count}")
        print(f"Passed: {pass_count}")
        print(f"Failed: {total_count - pass_count}")
        if total_count > 0:
            print(f"Success Rate: {(pass_count/total_count)*100:.1f}%")
        
    def save_results(self, filename: str):
        with open(filename, 'w') as f:
            json.dump(self.results, f, indent=2)
        print(f"\nDetailed results saved to {filename}")

async def main():
    print("Starting Stress Test for Classification Phase...")
    
    # 1. Generate Scenarios
    scenarios = HumanScriptGenerator.get_scenarios()
    print(f"Generated {len(scenarios)} test scenarios.")
    
    # 2. Run Tests
    tester = StressTester(concurrency=5)
    await tester.run_all(scenarios)
    
    # 3. Report
    tester.print_summary()
    tester.save_results("test_results_classify.json")

if __name__ == "__main__":
    asyncio.run(main())

