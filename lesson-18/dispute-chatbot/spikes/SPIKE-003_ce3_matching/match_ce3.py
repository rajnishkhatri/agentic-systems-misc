import json
from datetime import datetime, timedelta
from typing import List, Dict, Any, Tuple
import random
from dataclasses import dataclass

@dataclass
class Transaction:
    id: str
    date: datetime
    amount: float
    ip_address: str
    device_id: str
    email: str
    shipping_address: str
    undisputed: bool = True

class CE3Matcher:
    def __init__(self):
        pass

    def match(self, disputed_txn: Transaction, history: List[Transaction]) -> Dict[str, Any]:
        """
        Determine if CE 3.0 criteria are met.
        Criteria:
        1. At least 2 prior undisputed transactions.
        2. Within 120 - 365 days? No, PRD says "Within 120 days of disputed transaction". 
           (Visa rules actually say between 120 days and 365 days usually, but let's stick to the PRD: "120 days").
           Wait, usually CE 3.0 is "transactions that happened > 120 days ago"? 
           Or "transactions within the last year"?
           Let's check the PRD/Tasks text.
           Task 6.17.4 says nothing.
           Task 1036 in `network_payloads.yaml` (from SPIKE-001) says: "from 3 prior undisputed purchases within 120 days."
           So I will use "within 120 days PRIOR to the disputed transaction".
        3. At least 2 matching signals (IP, Device, Email, Shipping).
        """
        qualifying_txns = []
        
        for hist_txn in history:
            # Check 1: Undisputed
            if not hist_txn.undisputed:
                continue
            
            # Check 2: Date window (0 < diff <= 120 days)
            delta = disputed_txn.date - hist_txn.date
            if not (timedelta(days=0) < delta <= timedelta(days=120)):
                continue
            
            # Check 3: Matching Signals
            matches = []
            if hist_txn.ip_address == disputed_txn.ip_address:
                matches.append("ip_address")
            if hist_txn.device_id == disputed_txn.device_id:
                matches.append("device_id")
            if hist_txn.email == disputed_txn.email:
                matches.append("email")
            if hist_txn.shipping_address == disputed_txn.shipping_address:
                matches.append("shipping_address")
                
            if len(matches) >= 2:
                qualifying_txns.append({
                    "transaction_id": hist_txn.id,
                    "date": hist_txn.date.isoformat(),
                    "matching_signals": matches
                })
        
        eligible = len(qualifying_txns) >= 2
        return {
            "eligible": eligible,
            "qualifying_transactions": qualifying_txns,
            "count": len(qualifying_txns)
        }

def run_tests():
    matcher = CE3Matcher()
    results = []
    
    print("Running 50 synthetic test cases...")
    
    for i in range(50):
        # Generate base data
        base_date = datetime.now()
        base_ip = f"192.168.1.{random.randint(1, 255)}"
        base_device = f"dev_{random.randint(1000, 9999)}"
        base_email = f"user{i}@example.com"
        base_addr = f"{random.randint(1, 999)} Main St"
        
        disputed = Transaction(
            id=f"disputed_{i}",
            date=base_date,
            amount=100.0,
            ip_address=base_ip,
            device_id=base_device,
            email=base_email,
            shipping_address=base_addr
        )
        
        history = []
        # Case type: 
        # 0: Perfect match (2+ txns, all signals)
        # 1: Partial match (2+ txns, 2 signals)
        # 2: No match (0 txns)
        # 3: Insufficient signals (2+ txns, 1 signal)
        # 4: Old txns (>120 days)
        
        case_type = i % 5
        expected_eligible = False
        
        if case_type == 0: # Perfect
            expected_eligible = True
            for j in range(3):
                history.append(Transaction(
                    id=f"hist_{i}_{j}",
                    date=base_date - timedelta(days=random.randint(1, 110)),
                    amount=50.0,
                    ip_address=base_ip,
                    device_id=base_device,
                    email=base_email,
                    shipping_address=base_addr
                ))
                
        elif case_type == 1: # Partial signals (IP + Device)
            expected_eligible = True
            for j in range(2):
                history.append(Transaction(
                    id=f"hist_{i}_{j}",
                    date=base_date - timedelta(days=random.randint(1, 110)),
                    amount=50.0,
                    ip_address=base_ip,
                    device_id=base_device,
                    email="other@example.com",
                    shipping_address="Other St"
                ))

        elif case_type == 2: # No history
            expected_eligible = False
            
        elif case_type == 3: # Insufficient signals (Only IP)
            expected_eligible = False
            for j in range(3):
                history.append(Transaction(
                    id=f"hist_{i}_{j}",
                    date=base_date - timedelta(days=random.randint(1, 110)),
                    amount=50.0,
                    ip_address=base_ip,
                    device_id="dev_other",
                    email="other@example.com",
                    shipping_address="Other St"
                ))
                
        elif case_type == 4: # Old transactions
            expected_eligible = False
            for j in range(3):
                history.append(Transaction(
                    id=f"hist_{i}_{j}",
                    date=base_date - timedelta(days=random.randint(130, 200)),
                    amount=50.0,
                    ip_address=base_ip,
                    device_id=base_device,
                    email=base_email,
                    shipping_address=base_addr
                ))

        # Run Match
        result = matcher.match(disputed, history)
        
        pass_test = (result["eligible"] == expected_eligible)
        results.append(pass_test)
        
        if not pass_test:
            print(f"Failed Case {i} (Type {case_type}): Expected {expected_eligible}, Got {result['eligible']}")
            
    match_rate = sum(results) / len(results)
    print(f"\nMatch Rate: {match_rate * 100:.1f}% ({sum(results)}/{len(results)})")
    
    if match_rate >= 0.95:
        print("SUCCESS: Match rate > 95%")
    else:
        print("FAILURE: Match rate < 95%")

if __name__ == "__main__":
    run_tests()

