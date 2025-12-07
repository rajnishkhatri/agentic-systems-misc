import unittest
from fraud_detector import FraudDetector

class TestFraudDetector(unittest.TestCase):
    
    def setUp(self):
        self.detector = FraudDetector()
        
    def test_low_risk_transaction(self):
        txn = {
            'amount': 50.0,
            'mcc': '5411', # Grocery
            'is_card_present': True,
            'distance_from_home': 5
        }
        hist = {
            'account_age_days': 365,
            'disputes_last_90_days': 0,
            'avg_transaction_amount': 60.0
        }
        result = self.detector.analyze_transaction(txn, hist)
        self.assertEqual(result['risk_level'], 'LOW')
        self.assertLess(result['fraud_score'], 30)
        self.assertEqual(len(result['indicators']), 0)

    def test_high_value_transaction(self):
        txn = {
            'amount': 12000.0,
            'mcc': '5411',
            'is_card_present': True,
            'distance_from_home': 5
        }
        hist = {
            'account_age_days': 365,
            'disputes_last_90_days': 0,
            'avg_transaction_amount': 100.0
        }
        result = self.detector.analyze_transaction(txn, hist)
        self.assertIn('HIGH_VALUE_TRANSACTION', result['indicators'])
        self.assertGreaterEqual(result['fraud_score'], 40)

    def test_high_risk_merchant(self):
        txn = {
            'amount': 100.0,
            'mcc': '7995', # Gambling
            'is_card_present': False
        }
        hist = {
            'account_age_days': 365,
            'disputes_last_90_days': 0,
            'avg_transaction_amount': 100.0
        }
        result = self.detector.analyze_transaction(txn, hist)
        self.assertIn('HIGH_RISK_MERCHANT_CATEGORY', result['indicators'])
        self.assertGreaterEqual(result['fraud_score'], 30)

    def test_frequent_disputer(self):
        txn = {
            'amount': 100.0,
            'mcc': '5411',
            'is_card_present': True
        }
        hist = {
            'account_age_days': 365,
            'disputes_last_90_days': 4, # > 3
            'avg_transaction_amount': 100.0
        }
        result = self.detector.analyze_transaction(txn, hist)
        self.assertIn('FREQUENT_DISPUTER', result['indicators'])
        self.assertGreaterEqual(result['fraud_score'], 50)

    def test_new_account_risk(self):
        txn = {
            'amount': 100.0,
            'mcc': '5411',
            'is_card_present': True
        }
        hist = {
            'account_age_days': 15, # < 30
            'disputes_last_90_days': 0,
            'avg_transaction_amount': 100.0
        }
        result = self.detector.analyze_transaction(txn, hist)
        self.assertIn('NEW_ACCOUNT', result['indicators'])
        self.assertGreaterEqual(result['fraud_score'], 25)

    def test_combined_risk_factors(self):
        # New account + High Risk Merchant + Distant CNP
        txn = {
            'amount': 500.0,
            'mcc': '4829', # Money Transfer
            'is_card_present': False,
            'distance_from_home': 600
        }
        hist = {
            'account_age_days': 10,
            'disputes_last_90_days': 0,
            'avg_transaction_amount': 50.0
        }
        result = self.detector.analyze_transaction(txn, hist)
        # Risk factors:
        # New Account: +25
        # High Risk Merchant: +30
        # CNP: +10
        # Distant CNP: +15
        # Unusual amount: +20 (500 > 50*5)
        # Total expected: ~100
        self.assertIn('CRITICAL', result['risk_level'])
        self.assertGreaterEqual(result['fraud_score'], 90)

if __name__ == '__main__':
    unittest.main()
