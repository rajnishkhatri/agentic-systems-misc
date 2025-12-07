import datetime
from typing import Dict, List, Any, Tuple

class FraudDetector:
    """
    Prototype Fraud Detection Engine for Banking Disputes.
    Simulates an ML model using heuristic rules and weighted scoring.
    """

    def __init__(self):
        self.high_risk_mcc = ['5967', '7995', '4829', '6051']  # Direct Marketing, Gambling, Money Transfer
        self.max_transaction_amount = 10000.0
        self.velocity_threshold_count = 5  # Max transactions per day
        
    def analyze_transaction(self, transaction: Dict[str, Any], customer_history: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze a transaction and customer history to generate a fraud score.
        
        Args:
            transaction: Dict containing 'amount', 'mcc', 'date', 'is_card_present', 'distance_from_home'
            customer_history: Dict containing 'account_age_days', 'disputes_last_90_days', 'avg_transaction_amount'
            
        Returns:
            Dict with 'fraud_score' (0-100), 'risk_level', 'indicators'
        """
        score = 0.0
        indicators = []
        
        # 1. Amount Analysis
        amount = transaction.get('amount', 0.0)
        avg_amount = customer_history.get('avg_transaction_amount', 100.0)
        
        if amount > self.max_transaction_amount:
            score += 40
            indicators.append('HIGH_VALUE_TRANSACTION')
        elif amount > (avg_amount * 5):
            score += 20
            indicators.append('UNUSUAL_AMOUNT_FOR_CUSTOMER')
            
        # 2. Merchant Category Risk
        mcc = transaction.get('mcc', '')
        if mcc in self.high_risk_mcc:
            score += 30
            indicators.append('HIGH_RISK_MERCHANT_CATEGORY')
            
        # 3. Customer History
        recent_disputes = customer_history.get('disputes_last_90_days', 0)
        if recent_disputes > 3:
            score += 50
            indicators.append('FREQUENT_DISPUTER')
        elif recent_disputes > 0:
            score += 10
            
        account_age = customer_history.get('account_age_days', 365)
        if account_age < 30:
            score += 25
            indicators.append('NEW_ACCOUNT')
            
        # 4. Card Presence & Location
        is_card_present = transaction.get('is_card_present', True)
        distance = transaction.get('distance_from_home', 0)
        
        if not is_card_present:
            score += 10
            if distance > 500: # miles
                score += 15
                indicators.append('DISTANT_CNP_TRANSACTION')
        elif distance > 1000:
            score += 20
            indicators.append('DISTANT_TRANSACTION')

        # Normalize score
        final_score = min(100.0, max(0.0, score))
        
        return {
            'fraud_score': final_score,
            'risk_level': self._get_risk_level(final_score),
            'indicators': indicators,
            'timestamp': datetime.datetime.now().isoformat()
        }

    def _get_risk_level(self, score: float) -> str:
        if score < 30:
            return 'LOW'
        elif score < 70:
            return 'MEDIUM'
        elif score < 90:
            return 'HIGH'
        else:
            return 'CRITICAL'

if __name__ == "__main__":
    # Simple manual test
    detector = FraudDetector()
    
    txn = {
        'amount': 15000.0,
        'mcc': '7995', # Gambling
        'date': '2023-10-27',
        'is_card_present': False,
        'distance_from_home': 50
    }
    
    hist = {
        'account_age_days': 20,
        'disputes_last_90_days': 0,
        'avg_transaction_amount': 500.0
    }
    
    result = detector.analyze_transaction(txn, hist)
    print(f"Transaction Analysis Result:\n{result}")
