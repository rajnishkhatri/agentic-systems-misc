import unittest
from dispute_classifier import DisputeClassifier

class TestDisputeClassifier(unittest.TestCase):
    
    def setUp(self):
        self.classifier = DisputeClassifier()
        
    def test_fraud_classification(self):
        text = "I never authorized this transaction. My card was stolen."
        result = self.classifier.classify_dispute(text)
        self.assertEqual(result['reason'], 'fraudulent')
        self.assertGreaterEqual(result['confidence'], 0.6)
        self.assertEqual(result['network_reason_code_suggestion']['visa'], '10.4')

    def test_product_not_received(self):
        text = "I ordered headphones two weeks ago and the package never arrived."
        result = self.classifier.classify_dispute(text)
        self.assertEqual(result['reason'], 'product_not_received')
        self.assertEqual(result['network_reason_code_suggestion']['visa'], '13.1')

    def test_subscription_cancellation(self):
        text = "Please stop charging me. I cancelled this membership."
        context = {'is_recurring': True}
        result = self.classifier.classify_dispute(text, context)
        self.assertEqual(result['reason'], 'subscription_canceled')
        # Context boosting should help confidence
        self.assertGreaterEqual(result['confidence'], 0.7)

    def test_duplicate_charge(self):
        text = "I see two identical charges for $50 on the same day."
        context = {'potential_duplicate': True}
        result = self.classifier.classify_dispute(text, context)
        self.assertEqual(result['reason'], 'duplicate')
        # Strong signal from context
        self.assertGreaterEqual(result['confidence'], 0.8)

    def test_ambiguous_text(self):
        text = "I am unhappy with this transaction."
        result = self.classifier.classify_dispute(text)
        # Should probably default to general or have low confidence if no keywords match well
        # In our simple prototype, "unhappy" isn't a keyword, so it might go to 'general'
        self.assertEqual(result['reason'], 'general')
        self.assertLess(result['confidence'], 0.4)

    def test_mixed_signals(self):
        # "fraud" keyword vs "subscription" keyword
        text = "This subscription charge is fraud! I never signed up."
        context = {'is_recurring': True}
        result = self.classifier.classify_dispute(text, context)
        # "fraud" and "subscription" both hit.
        # "is_recurring" context adds 0.5 to subscription.
        # "fraud" (fraud) vs "subscription" (subscription_canceled)
        # Ideally subscription_canceled wins because of context boost if keywords are tied.
        # 'subscription' matches 1 keyword. 'fraud' matches 1 keyword.
        # Context adds 0.5 to subscription. So subscription wins.
        self.assertEqual(result['reason'], 'subscription_canceled')

if __name__ == '__main__':
    unittest.main()
