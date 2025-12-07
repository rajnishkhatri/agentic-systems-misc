# Dispute Schema - Detailed Explanation

## Overview

The dispute schema is a comprehensive, API-first data model for managing payment disputes (chargebacks) across multiple payment networks. It's designed following Stripe's design patterns and supports:

- **50+ data fields** in a single JSON payload
- **Multiple payment methods** (card, PayPal, Klarna, Affirm, Afterpay, bank transfer, ACH debit)
- **Network-specific reason codes** (Visa, Mastercard, Amex, Discover)
- **Enhanced evidence programs** (Visa Compelling Evidence 3.0)
- **27 evidence fields** with character and file size limits
- **Comprehensive eligibility detection** for advanced dispute resolution programs

---

## 1. Core Dispute Object

### Required Fields

```typescript
{
  id: string;              // Pattern: ^dp_[a-zA-Z0-9]{24}$ (e.g., "dp_1NxQkL2eZvKYlo2CXr5EPQmR")
  object: "dispute";       // Constant string identifying the object type
  amount: number;          // Disputed amount in smallest currency unit (cents for USD)
  currency: string;        // ISO 4217 three-letter code (e.g., "usd", "eur", "gbp")
  status: DisputeStatus;   // Current status of the dispute
  reason: DisputeReason;   // Reason given by cardholder
  created: number;         // Unix timestamp when dispute was created
}
```

### Optional Core Fields

- **`charge`**: ID of the charge being disputed (pattern: `^ch_[a-zA-Z0-9]{24}$`)
- **`payment_intent`**: ID of PaymentIntent if applicable
- **`transaction_amount`**: Original transaction amount (before partial dispute)
- **`transaction_date`**: Unix timestamp of original transaction
- **`is_charge_refundable`**: Whether the charge can still be refunded
- **`livemode`**: `true` for live mode, `false` for test mode
- **`metadata`**: Key-value pairs (max 50 keys, 500 chars per value)
- **`network_reason_code`**: Card network's reason code (e.g., "10.4", "4837", "F29")

---

## 2. Dispute Statuses

The schema supports 8 different status values that represent the dispute lifecycle:

```typescript
type DisputeStatus =
  | 'needs_response'        // Requires merchant to submit evidence
  | 'under_review'          // Evidence submitted, being reviewed
  | 'won'                   // Dispute resolved in merchant's favor
  | 'lost'                  // Dispute resolved in cardholder's favor
  | 'warning_needs_response'// Early warning requiring response
  | 'warning_under_review'  // Early warning under review
  | 'warning_closed'        // Early warning closed
  | 'charge_refunded';      // Charge has been refunded
```

### Status Flow
```
needs_response → under_review → won/lost
     ↓
warning_needs_response → warning_under_review → warning_closed
```

---

## 3. Dispute Reasons

8 standardized reason categories that map to network-specific reason codes:

```typescript
type DisputeReason =
  | 'credit_not_processed'    // Credit/refund not processed
  | 'duplicate'               // Duplicate charge
  | 'fraudulent'              // Unauthorized/fraudulent transaction
  | 'general'                 // General dispute
  | 'product_not_received'    // Product/service not delivered
  | 'product_unacceptable'    // Product/service not as described
  | 'subscription_canceled'   // Recurring subscription canceled
  | 'unrecognized';           // Transaction not recognized
```

---

## 4. Evidence System

The evidence object contains **27 fields** for submitting proof to respond to disputes.

### Text Evidence Fields (18 fields)
- Combined character limit: **150,000 characters**
- Fields include:
  - `access_activity_log` - Server logs showing digital product access (max 20K chars)
  - `billing_address` - Customer billing address (max 5K chars)
  - `cancellation_policy_disclosure` - How/when policy was shown (max 20K chars)
  - `cancellation_rebuttal` - Justification for subscription charge (max 20K chars)
  - `customer_email_address` - Customer email (max 254 chars, email format)
  - `customer_name` - Customer name (max 500 chars)
  - `customer_purchase_ip` - IP address used for purchase
  - `duplicate_charge_explanation` - Difference between charges (max 20K chars)
  - `duplicate_charge_id` - ID of prior duplicate charge
  - `product_description` - Description of product/service (max 20K chars)
  - `refund_policy_disclosure` - Refund policy disclosure (max 20K chars)
  - `refund_refusal_explanation` - Why refund not provided (max 20K chars)
  - `service_date` - Date service was received/began (max 500 chars)
  - `shipping_address` - Physical shipping address (max 5K chars)
  - `shipping_carrier` - Delivery service (e.g., FedEx, UPS) (max 500 chars)
  - `shipping_date` - Shipment date (max 500 chars)
  - `shipping_tracking_number` - Tracking number (max 500 chars)
  - `uncategorized_text` - Additional evidence (max 20K chars)

### File Evidence Fields (9 fields)
- Combined file size limit: **4.5 MB**
- Fields contain File IDs (not raw files):
  - `cancellation_policy` - Subscription cancellation policy document
  - `customer_communication` - Communication with customer
  - `customer_signature` - Customer signature document
  - `duplicate_charge_documentation` - Documentation for duplicate charge
  - `receipt` - Receipt or charge confirmation
  - `refund_policy` - Refund policy document
  - `service_documentation` - Proof service was provided
  - `shipping_documentation` - Proof of shipment/delivery
  - `uncategorized_file` - Additional evidence files

### Evidence Validation

The schema provides helper functions:
- `calculateEvidenceTextLength()` - Count total characters in text fields
- `validateEvidenceTextLimit()` - Verify within 150K character limit

---

## 5. Evidence Details

Tracks evidence submission requirements and deadlines:

```typescript
{
  due_by: number | null;              // Unix timestamp deadline for evidence
  has_evidence: boolean;               // Whether any evidence provided
  past_due: boolean;                   // Whether deadline has passed
  submission_count: number;            // Number of times evidence submitted
  enhanced_eligibility?: { ... }       // Eligibility for enhanced programs
}
```

---

## 6. Enhanced Evidence (Visa CE 3.0)

### Visa Compelling Evidence 3.0

A specialized program for Visa fraud disputes (reason code 10.4) that allows merchants to submit compelling evidence of legitimate transactions.

#### Requirements:
- Minimum **2 prior undisputed transactions**
- Transactions must be **120-365 days old**
- Must match customer identifiers (email, IP, device fingerprint, account ID)
- Maximum **5 prior transactions** can be submitted

#### Structure:

```typescript
{
  visa_compelling_evidence_3: {
    disputed_transaction: {
      customer_account_id?: string;
      customer_device_fingerprint?: string;
      customer_device_id?: string;
      customer_email_address?: string;  // Required
      customer_purchase_ip?: string;     // Required
      merchandise_or_services?: 'merchandise' | 'services';
      product_description?: string;      // Max 500 chars
      shipping_address?: Address;
    },
    prior_undisputed_transactions: [     // Min 2, max 5
      {
        charge: string;                  // Required - prior charge ID
        customer_account_id?: string;
        customer_device_fingerprint?: string;
        customer_device_id?: string;
        customer_email_address?: string;
        customer_purchase_ip?: string;
        product_description?: string;
        shipping_address?: Address;
      }
    ]
  }
}
```

#### Eligibility Status:

```typescript
type CE3Status = 'qualified' | 'requires_action' | 'not_qualified';
```

#### Required Actions:

If status is `requires_action`, the system identifies missing requirements:

```typescript
type CE3RequiredAction =
  | 'missing_customer_identifiers'
  | 'missing_prior_undisputed_transactions'
  | 'missing_merchandise_or_services'
  | 'missing_disputed_transaction_description'
  | 'missing_customer_email_address'
  | 'missing_customer_purchase_ip'
  | 'transactions_too_recent'    // Less than 120 days old
  | 'transactions_too_old';      // More than 365 days old
```

---

## 7. Payment Method Details

Supports multiple payment methods with type-specific details:

### Card Details

```typescript
{
  type: 'card',
  card: {
    brand: 'visa' | 'mastercard' | 'amex' | 'discover' | 'diners' | 'jcb' | 'unionpay';
    case_type: 'chargeback' | 'inquiry' | 'pre_arbitration' | 'arbitration' | 'compliance';
    network_reason_code?: string;    // Network-specific code
    last4?: string;                  // Last 4 digits (pattern: ^[0-9]{4}$)
    exp_month?: number;              // 1-12
    exp_year?: number;
    fingerprint?: string;            // Unique card identifier
    funding?: 'credit' | 'debit' | 'prepaid' | 'unknown';
    country?: string;                // ISO 3166-1 alpha-2 (e.g., "US")
    issuer?: string;                 // Card issuing bank
  }
}
```

### PayPal Details

```typescript
{
  type: 'paypal',
  paypal: {
    case_id?: string;
    dispute_type?: 'inquiry' | 'chargeback' | 'unauthorized';
    reason_code?: string;
  }
}
```

### Other Payment Methods

Also supports:
- `klarna` - Buy now, pay later
- `affirm` - Installment payments
- `afterpay` - Split payments
- `bank_transfer` - Bank transfers
- `ach_debit` - ACH debits

---

## 8. Network Reason Codes

The schema includes comprehensive mappings for reason codes across major card networks:

### Visa Reason Codes (10.x, 11.x, 12.x, 13.x series)

Examples:
- **10.4**: Other Fraud - Card Absent Environment → `fraudulent` (Visa CE 3.0 eligible)
- **13.1**: Merchandise/Services Not Received → `product_not_received`
- **13.2**: Cancelled Recurring Transaction → `subscription_canceled`
- **12.6.1**: Duplicate Processing → `duplicate`

### Mastercard Reason Codes (4xxx series)

Examples:
- **4837**: No Cardholder Authorization → `fraudulent`
- **4855**: Goods or Services Not Provided → `product_not_received`
- **4834**: Duplicate Processing → `duplicate`

### American Express Reason Codes (alphanumeric)

Examples:
- **F29**: Card Not Present → `fraudulent`
- **C08**: Goods/Services Not Received → `product_not_received`
- **P08**: Duplicate Charge → `duplicate`

### Discover Reason Codes (alphanumeric)

Examples:
- **UA02**: Fraud - Card Not Present Transaction → `fraudulent`
- **RG**: Non-Receipt of Goods or Services → `product_not_received`
- **DP**: Duplicate Processing → `duplicate`

### Reason Code Utilities

The schema provides helper functions:

```typescript
// Look up reason code details
lookupReasonCode(network: CardBrand, code: string): ReasonCodeInfo | null

// Get all reason codes for a category
getReasonCodesByCategory(category: DisputeReason): ReasonCodeInfo[]

// Get recommended evidence fields for a category
getRecommendedEvidence(category: DisputeReason): string[]

// Check if Visa CE 3.0 eligible
isVisaCE3ReasonCode(code: string): boolean
```

---

## 9. Balance Transactions

Tracks financial impact of disputes through balance transactions:

```typescript
{
  id: string;                    // Pattern: ^txn_[a-zA-Z0-9]{24}$
  amount: number;                // Transaction amount (can be negative)
  currency: string;
  type: BalanceTransactionType;
  created: number;               // Unix timestamp
  fee: number;                   // Fee amount
  net: number;                   // Net amount after fees
  description?: string;
}
```

### Transaction Types:

```typescript
type BalanceTransactionType =
  | 'dispute'              // Initial dispute withdrawal
  | 'dispute_reversal'     // Dispute won - funds returned
  | 'dispute_fee'          // Dispute fee charged
  | 'dispute_fee_refund';  // Dispute fee refunded (when won)
```

### Example Flow:

1. **Dispute created**: `type: 'dispute'` - amount: -$150.00, fee: -$15.00, net: -$165.00
2. **Dispute won**: `type: 'dispute_reversal'` - amount: $150.00, net: $150.00
3. **Fee refunded**: `type: 'dispute_fee_refund'` - amount: $15.00, net: $15.00

---

## 10. Enhanced Eligibility

Tracks eligibility for advanced dispute resolution programs:

### Visa Compelling Evidence 3.0 Eligibility

```typescript
{
  status: 'qualified' | 'requires_action' | 'not_qualified';
  required_actions?: CE3RequiredAction[];
  partner_rejected_details?: object | null;
}
```

### Visa Compliance

```typescript
{
  status: 'fee_acknowledged' | 'fee_pending';
  fee_amount?: number;
}
```

### Mastercard Arbitration

```typescript
{
  status: 'eligible' | 'not_eligible' | 'pending';
}
```

---

## 11. Address Object

Standardized address structure used in enhanced evidence:

```typescript
{
  line1?: string;
  line2?: string;
  city?: string;
  state?: string;
  postal_code?: string;
  country?: string;        // ISO 3166-1 alpha-2 (e.g., "US")
}
```

---

## 12. Validation Constants

The schema defines important validation limits:

```typescript
EVIDENCE_TEXT_LIMIT = 150_000;              // Total text characters
EVIDENCE_FILE_SIZE_LIMIT = 4_500_000;       // 4.5 MB total file size
MASTERCARD_PAGE_LIMIT = 19;                 // Mastercard document page limit
CE3_TRANSACTION_MIN_AGE_DAYS = 120;         // Minimum age for prior transactions
CE3_TRANSACTION_MAX_AGE_DAYS = 365;         // Maximum age for prior transactions
CE3_MIN_PRIOR_TRANSACTIONS = 2;             // Minimum prior transactions required
```

---

## 13. Recommended Evidence by Category

The schema includes evidence recommendations for each dispute reason:

### Fraudulent Disputes
- Customer purchase IP
- Customer email address
- Customer signature
- Access activity logs
- Receipt
- Shipping documentation (if applicable)

### Product Not Received
- Shipping documentation
- Shipping tracking number
- Shipping carrier
- Shipping date
- Shipping address
- Customer communication

### Product Unacceptable
- Product description
- Customer communication
- Refund policy
- Refund policy disclosure
- Receipt

### Duplicate Charges
- Duplicate charge ID
- Duplicate charge explanation
- Duplicate charge documentation
- Receipt

### Subscription Canceled
- Cancellation policy
- Cancellation policy disclosure
- Cancellation rebuttal
- Customer communication
- Access activity logs

### Credit Not Processed
- Refund policy
- Refund policy disclosure
- Refund refusal explanation
- Customer communication

---

## 14. Example Use Cases

### Example 1: Fraud Dispute with Visa CE 3.0

A Visa dispute with reason code 10.4 (fraudulent) can use CE 3.0 if:
- Has 2+ prior transactions 120-365 days old
- Matching customer identifiers (email, IP, device)
- Provides disputed transaction details

The system automatically checks eligibility and provides `required_actions` if not qualified.

### Example 2: Product Not Received

For Visa reason code 13.1:
- Submit shipping documentation
- Provide tracking number
- Show delivery confirmation
- Include customer communication

### Example 3: Subscription Dispute

For recurring billing disputes:
- Show cancellation policy disclosure
- Provide cancellation rebuttal
- Submit access activity logs showing service usage
- Include customer communication history

---

## 15. Data Flow

1. **Dispute Created**: Card network initiates dispute
   - Status: `needs_response`
   - `evidence_details.due_by` set
   - `evidence_details.has_evidence`: false

2. **Evidence Submission**: Merchant provides evidence
   - `evidence` object populated
   - `evidence_details.has_evidence`: true
   - `evidence_details.submission_count` incremented

3. **Enhanced Eligibility Check**: System evaluates for CE 3.0
   - Checks prior transactions
   - Validates customer identifiers
   - Sets `enhanced_eligibility.visa_compelling_evidence_3.status`

4. **Review Process**: Status changes to `under_review`
   - Network reviews evidence
   - May request additional information

5. **Resolution**: Status becomes `won` or `lost`
   - If won: balance transaction reversal created
   - Fee may be refunded
   - Final status set

---

## 16. Schema Files Structure

```
dispute-schema/
├── dispute.schema.json       # JSON Schema validation
├── dispute_types.ts          # TypeScript type definitions
├── network_reason_codes.ts   # Reason code mappings & utilities
├── index.ts                  # Main export file
├── examples.json             # Example dispute objects
├── iso8583_mapping.ts        # ISO 8583 Data Element mapping
├── network_integration/      # API payloads for Visa/Mastercard
└── compliance/               # Regulatory timeline logic
```

---

## 17. Key Design Principles

1. **API-First**: Designed for REST API usage with clear structure
2. **Network Agnostic**: Unified interface supporting multiple card networks
3. **Extensible**: Easy to add new payment methods or evidence fields
4. **Validation**: Built-in validation with clear error messages
5. **Type Safety**: Full TypeScript support with strict types
6. **Comprehensive**: Covers all major dispute scenarios and evidence types

---

## 18. Best Practices

### Evidence Submission
- Submit evidence as early as possible (before deadline)
- Use recommended evidence fields for each dispute reason
- Keep text evidence concise and focused
- Use file evidence for documents that can't be summarized

### Visa CE 3.0
- Maintain customer transaction history (120-365 days)
- Store customer identifiers (email, IP, device fingerprint)
- Match identifiers consistently across transactions
- Submit minimum 2 prior transactions, up to 5

### Network Reason Codes
- Use `lookupReasonCode()` to understand dispute details
- Check `getRecommendedEvidence()` for required fields
- Verify eligibility for enhanced programs

### Validation
- Check `validateEvidenceTextLimit()` before submission
- Verify file sizes before upload
- Validate CE 3.0 transaction age requirements
- Check `evidence_details.past_due` before submitting

---

## 19. Integration & Compliance

The schema includes extensions for network integration and regulatory compliance:

### ISO 8583 Mapping
- Maps schema fields to ISO 8583 Data Elements (DE) for legacy switch integration.
- See `iso8583_mapping.ts` for DE definitions (e.g., `DE 25` for Reason Code).

### Network API Payloads
- **Visa VROL**: Types for `SubmitDisputeQuestionnaire` including CE 3.0 data.
- **Mastercom**: Types for `CreateChargeback` claims.
- See `network_integration/` directory.

### Compliance Logic (Reg E/Z)
- Automated timeline calculation for US Regulations E & Z.
- State machine logic for Provisional Credit (10 days) and Investigation (45/90 days).
- See `compliance/reg_e_timelines.ts`.

---

This schema provides a complete, production-ready system for managing payment disputes across multiple networks with comprehensive evidence tracking and advanced resolution programs.
