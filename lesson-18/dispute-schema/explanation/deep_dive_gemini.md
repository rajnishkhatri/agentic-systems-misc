# Deep Dive: Real-World Dispute Scenarios & System Architecture

## Overview

This analysis explores the Dispute Schema system through the lens of real-world scenarios, illustrating how structured data serves as the primary defense for merchants against the $60 billion annual chargeback problem. By examining specific character-driven cases and the underlying technical architecture, we demonstrate how the schema translates complex banking regulations and network rules into actionable code.

---

## Part 1: The $60 Billion Problem (Context)

The payments industry faces a staggering challenge: approximately $60 billion is lost annually to chargebacks. For merchants, this is not just a cost of doing business but a threat to survival. With typical e-commerce margins hovering between 10-20%, a dispute rate of just 0.5-1% can destroy profitability.

A lost dispute incurs three distinct financial hits:
1.  **Revenue Loss**: The original transaction amount is returned to the cardholder.
2.  **COGS Loss**: The physical goods or services have already been provided and are rarely recovered.
3.  **Dispute Fee**: A non-refundable penalty (often $15-$50) charged by the acquirer.

The merchant's only scalable defense against this asymmetry is **structured data**. While human arbitration exists, the sheer volume of disputes means that automated systems—driven by schemas like `dispute.schema.json`—must handle the heavy lifting of evidence compilation and submission.

---

## Part 2: Real-World Case Study 1 - "I Didn't Buy This"

**Scenario:** Visa Reason Code 10.4 (Fraud - Card-Absent Environment)

### The Characters
*   **Sarah (Cardholder):** Notices a $150 charge for "TechGear Store" that she doesn't recognize.
*   **TechGear Store (Merchant):** A electronics retailer using the Dispute Schema.
*   **Chase Bank (Issuer):** Sarah's bank, initiating the dispute.

### The Journey
1.  **The Dispute:** Sarah files a dispute claiming fraud. Chase initiates a 10.4 dispute.
2.  **The Notification:** TechGear receives a webhook. The system identifies the reason code and checks for "Compelling Evidence 3.0" (CE 3.0) eligibility.
3.  **The Defense:** The schema logic kicks in. CE 3.0 rules state that if a merchant can prove the device or IP was used in *two prior undisputed transactions* (120+ days old), liability shifts back to the issuer.

### The Payload
The system queries historical data and constructs the following JSON payload to prove the link between Sarah and the device:

```json
{
  "enhanced_evidence": {
    "visa_compelling_evidence_3": {
      "disputed_transaction": {
        "customer_account_id": "acc_sarah_882",
        "customer_device_fingerprint": "dev_fp_x9923",
        "customer_purchase_ip": "24.12.100.22",
        "product_description": "Mechanical Keyboard K95"
      },
      "prior_undisputed_transactions": [
        {
          "charge": "ch_prev_101",
          "customer_account_id": "acc_sarah_882",
          "customer_device_fingerprint": "dev_fp_x9923",
          "customer_purchase_ip": "24.12.100.22",
          "date": "2023-05-15"
        },
        {
          "charge": "ch_prev_098",
          "customer_account_id": "acc_sarah_882",
          "customer_device_fingerprint": "dev_fp_x9923",
          "customer_purchase_ip": "24.12.100.22",
          "date": "2023-03-10"
        }
      ]
    }
  }
}
```

**Outcome:** By presenting machine-readable proof of prior history, TechGear wins the dispute automatically under the CE 3.0 program, saving the revenue and the dispute fee.

---

## Part 3: Real-World Case Study 2 - "My Package Never Arrived"

**Scenario:** Product Not Received (Visa 13.1)

### The Characters
*   **Robert (Cardholder):** Orders headphones but claims they never arrived.
*   **HeadphoneShop (Merchant):** Ships via FedEx with tracking.

### The Defense Strategy
Unlike fraud, identity is irrelevant here. The focus is on **logistics**. The system maps the incoming 13.1 code to the schema's `product_not_received` logic.

**Timeline Pressure:** The merchant typically has a strict 14-day window to respond.

### The Payload
The system pulls data from the shipping provider API to populate the evidence object:

```json
{
  "reason": "product_not_received",
  "evidence": {
    "shipping_carrier": "FedEx",
    "shipping_tracking_number": "123456789012",
    "shipping_date": "2023-11-01",
    "shipping_address": "123 Main St, Apt 4B, New York, NY",
    "shipping_documentation": "file_upload_id_123",
    "uncategorized_text": "Carrier confirms delivery to front porch on Nov 3rd at 2:00 PM."
  }
}
```

**Outcome:** The merchant wins by providing a direct link between the order address (AVS verified) and the carrier's delivery confirmation.

---

## Part 4: Real-World Case Study 3 - "I Cancelled My Subscription"

**Scenario:** Subscription Billing Dispute

### The Characters
*   **Emily (Subscriber):** Forgot to cancel her SaaS subscription and disputes the latest charge.
*   **SaaSCo (Merchant):** Provides a project management tool.

### The Complexity
Recurring billing disputes are difficult because the "product" is access. The merchant must prove that access was available and, ideally, utilized.

### The Payload
The `access_activity_log` field becomes the critical evidence, showing that Emily logged in after the billing date.

```json
{
  "reason": "subscription_canceled",
  "evidence": {
    "cancellation_policy_disclosure": "Terms accepted on signup (2023-01-15). 30-day notice required.",
    "access_activity_log": "User login detected on 2023-11-05 (5 days after billing). 14 file uploads recorded.",
    "service_documentation": "file_logs_export_pdf"
  }
}
```

**Outcome:** SaaSCo wins by demonstrating active consumption of the service during the disputed period, invalidating the claim that the service was unwanted or cancelled.

---

## Part 5: The Network Translation Layer

The `dispute.schema.json` acts as a "Rosetta Stone" for the payment ecosystem. A single dispute event from a merchant must be translated into different formats depending on the card network:

1.  **Visa (VROL):** Requires a specific questionnaire format (like the CE 3.0 fields shown above).
2.  **Mastercard (Mastercom):** Uses a different set of claim codes and document requirements.
3.  **Legacy Systems (ISO 8583):** Some banking backends still communicate via ISO 8583 messages. The schema's `amount` and `reason` fields must be mapped to specific data elements (e.g., Field 4 for Amount, Field 25 for Message Reason Code) to traverse these older rails.

This abstraction layer allows the merchant's engineering team to build against one schema while the system handles the complexity of network-specific protocols.

---

## Part 6: The Compliance Clock

Time is a critical dimension in dispute resolution, governed by federal regulations:

*   **Reg E (Debit):** Mandates strict timelines for provisional credit (10 days) and investigation (45-90 days).
*   **Reg Z (Credit):** Requires acknowledgment within 30 days and resolution within two billing cycles (max 90 days).

The system automatically calculates the `evidence_details.due_by` timestamp based on these regulations and the specific network rules. If a merchant misses this deadline, the dispute is an automatic loss ("expiry"). The architecture must prioritize queues based on these expiration timestamps to ensure no value is left on the table due to timeout.

---

## Part 7: The AWS Orchestration

The technical implementation relies on a robust AWS serverless architecture to handle the asynchronous nature of disputes:

1.  **EventBridge:** Orchestrates the flow of events. A "Dispute Created" event triggers the workflow.
2.  **Step Functions:** Manages the state machine (Wait for Evidence -> Validate -> Submit).
3.  **Textract:** Automatically extracts text from uploaded PDF receipts or shipping labels to populate schema fields.
4.  **Comprehend:** Analyzes the sentiment and key phrases in the cardholder's complaint text to better categorize the dispute reason if the code is ambiguous.
5.  **SageMaker A2I:** Provides a "Human-in-the-Loop" workflow. High-value or low-confidence disputes are routed to a human agent for review before submission to the network.

---

## Part 8: The Money Trail

A dispute triggers a complex sequence of ledger events:

1.  **Dispute Initiation:**
    *   Debit: Merchant Balance (Transaction Amount)
    *   Debit: Merchant Balance (Dispute Fee)
2.  **Dispute Win (Reversal):**
    *   Credit: Merchant Balance (Transaction Amount)
    *   Credit: Merchant Balance (Dispute Fee - depending on network rules)
3.  **Dispute Loss:**
    *   No movement (funds were already debited).

Visualizing this flow is crucial for reconciliation. The `balance_transactions` array in the schema tracks these movements, ensuring the finance team can audit the "Win vs. Loss" impact on the bottom line.

---

## Part 9: Security & Compliance Deep Dive

Handling dispute evidence requires strict adherence to **PCI DSS v4.0**:

*   **No PAN Storage:** The schema never stores the full Primary Account Number. It uses `last4`, `fingerprint`, or tokenized references (`tok_...`).
*   **Encryption:** All evidence files and PII (names, addresses) are encrypted at rest (e.g., using AWS KMS).
*   **Access Control:** Only authorized roles can access the full dispute details, preventing internal data leaks.

The "last4 + fingerprint" pattern allows the merchant to match transactions and prove identity without ever handling the sensitive raw card data that would increase compliance scope.

---

## Part 10: Winning Strategies

To maximize win rates, merchants should adopt specific strategies within the schema:

1.  **Reason Code Optimization:** Don't send generic evidence. If it's a `product_not_received` dispute, the `shipping_tracking_number` is mandatory. If it's `fraud`, prior history is key.
2.  **Speed:** Submit evidence as fast as possible. Early submission often leads to better outcomes and faster funds release.
3.  **Avoid Common Mistakes:**
    *   Missing signatures on delivery proof.
    *   Illegible receipts.
    *   Providing evidence for the wrong transaction amount.

By adhering to the structured requirements of the schema, merchants transform dispute response from a frantic reaction into a calculated, data-driven business process.
