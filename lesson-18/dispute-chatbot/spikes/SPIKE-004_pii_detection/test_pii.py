import re

class MockGuardRails:
    def detect(self, text):
        findings = []
        # Credit Card (Simple Luhn-like or just 13-19 digits)
        # Visa, MasterCard, etc. usually 16 digits.
        # ARN is 23 digits.
        # If our regex is loose (e.g. \d{16}), it might match inside ARN.
        cc_pattern = r'\b(?:\d{4}[- ]?){3}\d{4}\b|\b\d{16}\b' 
        if re.search(cc_pattern, text):
            findings.append("CREDIT_CARD")
            
        # Email
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        if re.search(email_pattern, text):
            findings.append("EMAIL_ADDRESS")
            
        # Phone (US)
        phone_pattern = r'\b(?:\+?1[-. ]?)?\(?([0-9]{3})\)?[-. ]?([0-9]{3})[-. ]?([0-9]{4})\b'
        if re.search(phone_pattern, text):
            findings.append("PHONE_NUMBER")
            
        return findings

def run_test():
    guard = MockGuardRails()
    
    # 1. Dispute Domain Vocabulary (Should NOT be flagged)
    dispute_terms = [
        "Chargeback",
        "Reason Code 10.4",
        "Compelling Evidence 3.0",
        "Product Not Received",
        "ARN 74027740010000000000001", # 23 digits
        "Case ID VIS-2024-12345678",
        "Merchant ID MERCH123456789",
        "Authorization Code A12345",
        "Transaction Date 2024-11-15",
        "Response Due Date 2024-12-15"
    ]
    
    # 2. Actual PII (Should be flagged)
    pii_examples = [
        "john.doe@example.com",
        "4111 1111 1111 1111", # Valid CC format
        "4111111111111111", # Valid CC format (no spaces)
        "555-0123", # Phone
        "(555) 555-0199" # Phone
    ]
    
    print("--- Testing Dispute Terms (False Positives) ---")
    fp_count = 0
    for term in dispute_terms:
        findings = guard.detect(term)
        if findings:
            print(f"FAIL: '{term}' flagged as {findings}")
            fp_count += 1
        else:
            # print(f"PASS: '{term}'")
            pass
            
    fp_rate = fp_count / len(dispute_terms)
    print(f"\nFalse Positive Rate: {fp_rate:.1%} ({fp_count}/{len(dispute_terms)})")
    
    print("\n--- Testing PII (True Positives) ---")
    tp_count = 0
    for term in pii_examples:
        findings = guard.detect(term)
        if findings:
            # print(f"PASS: '{term}' detected as {findings}")
            tp_count += 1
        else:
            print(f"FAIL: '{term}' NOT detected")
            
    tp_rate = tp_count / len(pii_examples)
    print(f"\nTrue Positive Rate: {tp_rate:.1%} ({tp_count}/{len(pii_examples)})")
    
    if fp_rate < 0.05:
        print("\nSUCCESS: False positive rate < 5%")
    else:
        print("\nFAILURE: False positive rate >= 5%")

if __name__ == "__main__":
    run_test()

