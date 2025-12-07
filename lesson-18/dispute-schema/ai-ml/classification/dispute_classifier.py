from typing import Dict, Any, List

class DisputeClassifier:
    """
    Prototype Dispute Classification Engine.
    Simulates an NLP model using keyword analysis and rule-based logic.
    """
    
    def __init__(self):
        self.keywords = {
            'fraudulent': ['fraud', 'unauthorized', 'didn\'t buy', 'stolen card', 'hack', 'unknown charge', 'identity theft'],
            'product_not_received': ['not received', 'never arrived', 'missing package', 'where is my order', 'lost in transit', 'shipping'],
            'product_unacceptable': ['damaged', 'broken', 'defective', 'not as described', 'wrong color', 'fake', 'counterfeit'],
            'subscription_canceled': ['cancel', 'subscription', 'recurring', 'monthly charge', 'membership', 'stop charging'],
            'duplicate': ['duplicate', 'charged twice', 'double charge', 'two times'],
            'credit_not_processed': ['refund', 'return', 'credit', 'money back', 'never refunded'],
            'unrecognized': ['recognize', 'who is this', 'what is this charge', 'forgot']
        }

    def classify_dispute(self, customer_complaint: str, transaction_details: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Classify a dispute based on customer complaint text and transaction context.
        
        Args:
            customer_complaint: The text description provided by the customer.
            transaction_details: Optional dict with transaction metadata (e.g., 'is_recurring').
            
        Returns:
            Dict with 'reason', 'confidence', 'network_reason_code_suggestion'
        """
        text = customer_complaint.lower()
        scores = {category: 0 for category in self.keywords}
        
        # 1. Keyword Matching
        for category, keywords in self.keywords.items():
            for keyword in keywords:
                if keyword in text:
                    scores[category] += 1
        
        # 2. Contextual Boosting
        if transaction_details:
            if transaction_details.get('is_recurring', False):
                scores['subscription_canceled'] += 0.5
            
            # If very recent transaction and identical amount exists (simulated check)
            if transaction_details.get('potential_duplicate', False):
                scores['duplicate'] += 2.0

        # 3. Determine Winner
        best_category = max(scores, key=scores.get)
        max_score = scores[best_category]
        
        confidence = min(0.99, 0.5 + (max_score * 0.1)) if max_score > 0 else 0.3
        
        if max_score == 0:
            best_category = 'general'
            confidence = 0.1

        return {
            'reason': best_category,
            'confidence': float(f"{confidence:.2f}"),
            'network_reason_code_suggestion': self._suggest_network_code(best_category)
        }

    def _suggest_network_code(self, reason: str) -> Dict[str, str]:
        # Simplified mapping based on Visa/Mastercard
        mapping = {
            'fraudulent': {'visa': '10.4', 'mastercard': '4837'},
            'product_not_received': {'visa': '13.1', 'mastercard': '4855'},
            'product_unacceptable': {'visa': '13.3', 'mastercard': '4853'},
            'subscription_canceled': {'visa': '13.2', 'mastercard': '4841'},
            'duplicate': {'visa': '12.6.1', 'mastercard': '4834'},
            'credit_not_processed': {'visa': '13.6', 'mastercard': '4860'},
            'unrecognized': {'visa': '10.5', 'mastercard': '4863'}, # Often falls under fraud
            'general': {'visa': 'N/A', 'mastercard': 'N/A'}
        }
        return mapping.get(reason, {'visa': 'Unknown', 'mastercard': 'Unknown'})

if __name__ == "__main__":
    classifier = DisputeClassifier()
    
    complaint = "I cancelled my netflix subscription last month but they still charged me."
    context = {'is_recurring': True}
    
    result = classifier.classify_dispute(complaint, context)
    print(f"Classification Result:\n{result}")
