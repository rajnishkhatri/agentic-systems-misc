# DynamoDB Schema Design for Dispute Management

## Overview

This document defines the DynamoDB table design for the AWS-integrated dispute management system. The design follows single-table patterns optimized for the access patterns required by the dispute schema.

---

## Table: `disputes`

### Table Configuration

| Setting | Value |
|---------|-------|
| Table Name | `disputes-{environment}` |
| Billing Mode | PAY_PER_REQUEST (on-demand) |
| Point-in-time Recovery | Enabled |
| Encryption | AWS-managed KMS |
| Stream | Enabled (NEW_AND_OLD_IMAGES) |

### Key Schema

| Attribute | Type | Key |
|-----------|------|-----|
| `PK` | String | Partition Key |
| `SK` | String | Sort Key |

### Global Secondary Indexes

| Index Name | Partition Key | Sort Key | Projection | Purpose |
|------------|---------------|----------|------------|---------|
| `GSI1-ChargeIndex` | `GSI1PK` | `GSI1SK` | ALL | Lookup by charge_id |
| `GSI2-StatusIndex` | `GSI2PK` | `GSI2SK` | ALL | Filter by status + created |
| `GSI3-DeadlineIndex` | `GSI3PK` | `GSI3SK` | KEYS_ONLY | Deadline monitoring |
| `GSI4-PaymentIntentIndex` | `GSI4PK` | - | KEYS_ONLY | Lookup by payment_intent |

---

## Item Types

### 1. Dispute Metadata Item

Primary item storing core dispute data.

```typescript
{
  // Keys
  PK: "DISPUTE#dp_1NxQkL2eZvKYlo2CXr5EPQmR",
  SK: "METADATA",

  // GSI Keys
  GSI1PK: "CHARGE#ch_1NxQkL2eZvKYlo2CXr5EPQmR",
  GSI1SK: "DISPUTE#dp_1NxQkL2eZvKYlo2CXr5EPQmR",
  GSI2PK: "STATUS#needs_response",
  GSI2SK: 1699900800,  // created timestamp
  GSI3PK: "DEADLINE",
  GSI3SK: 1700505600,  // due_by timestamp
  GSI4PK: "PI#pi_1NxQkL2eZvKYlo2CXr5EPQmR",

  // Core Fields (from dispute schema)
  id: "dp_1NxQkL2eZvKYlo2CXr5EPQmR",
  object: "dispute",
  amount: 15000,
  currency: "usd",
  status: "needs_response",
  reason: "fraudulent",
  created: 1699900800,
  charge: "ch_1NxQkL2eZvKYlo2CXr5EPQmR",
  payment_intent: "pi_1NxQkL2eZvKYlo2CXr5EPQmR",
  transaction_amount: 15000,
  transaction_date: 1699814400,
  is_charge_refundable: false,
  livemode: true,
  network_reason_code: "10.4",

  // Evidence Details (embedded)
  evidence_details: {
    due_by: 1700505600,
    has_evidence: false,
    past_due: false,
    submission_count: 0,
    enhanced_eligibility: {
      visa_compelling_evidence_3: {
        status: "requires_action",
        required_actions: ["missing_prior_undisputed_transactions"]
      }
    }
  },

  // Payment Method Details (embedded)
  payment_method_details: {
    type: "card",
    card: {
      brand: "visa",
      case_type: "chargeback",
      network_reason_code: "10.4",
      last4: "4242",
      funding: "credit"
    }
  },

  // Metadata (user-defined)
  metadata: {
    order_id: "ord_12345",
    customer_segment: "premium"
  },

  // DynamoDB metadata
  _entityType: "DISPUTE",
  _version: 1,
  _createdAt: "2024-11-13T12:00:00Z",
  _updatedAt: "2024-11-13T12:00:00Z",
  _ttl: null  // No TTL for disputes (2-year retention)
}
```

### 2. Evidence Item

Separate item for evidence when total size exceeds embedding threshold (100KB).

```typescript
{
  // Keys
  PK: "DISPUTE#dp_1NxQkL2eZvKYlo2CXr5EPQmR",
  SK: "EVIDENCE",

  // Text Evidence Fields
  access_activity_log: "2024-11-01 10:00:00 - User logged in from IP 192.168.1.1...",
  billing_address: "123 Main St, San Francisco, CA 94102, US",
  customer_email_address: "customer@example.com",
  customer_name: "John Doe",
  customer_purchase_ip: "192.168.1.1",
  product_description: "Premium subscription - 1 year access to platform features",
  // ... other text fields

  // File Evidence Fields (S3 references)
  receipt: "file_1NxQkL2eZvKYlo2CXr5EPQmR",
  shipping_documentation: "file_2MxQkL2eZvKYlo2CXr5EPQmS",
  customer_communication: "file_3OxQkL2eZvKYlo2CXr5EPQmT",
  // ... other file fields

  // Validation metadata
  _totalTextLength: 45230,
  _fileCount: 3,
  _lastSubmissionAt: "2024-11-14T09:30:00Z",
  _entityType: "EVIDENCE"
}
```

### 3. Balance Transaction Items

Track financial impact of disputes.

```typescript
{
  // Keys
  PK: "DISPUTE#dp_1NxQkL2eZvKYlo2CXr5EPQmR",
  SK: "BALANCE_TXN#txn_1NxQkL2eZvKYlo2CXr5EPQmR",

  // Balance Transaction Fields
  id: "txn_1NxQkL2eZvKYlo2CXr5EPQmR",
  amount: -15000,
  currency: "usd",
  type: "dispute",
  created: 1699900800,
  fee: -1500,
  net: -16500,
  description: "Dispute dp_1NxQkL2eZvKYlo2CXr5EPQmR",

  _entityType: "BALANCE_TRANSACTION"
}
```

### 4. Enhanced Evidence (Visa CE 3.0) Item

```typescript
{
  // Keys
  PK: "DISPUTE#dp_1NxQkL2eZvKYlo2CXr5EPQmR",
  SK: "CE3_EVIDENCE",

  // Disputed Transaction
  disputed_transaction: {
    customer_account_id: "acct_12345",
    customer_device_fingerprint: "fp_abc123def456",
    customer_device_id: "dev_xyz789",
    customer_email_address: "customer@example.com",
    customer_purchase_ip: "192.168.1.1",
    merchandise_or_services: "merchandise",
    product_description: "Premium wireless headphones",
    shipping_address: {
      line1: "123 Main St",
      city: "San Francisco",
      state: "CA",
      postal_code: "94102",
      country: "US"
    }
  },

  // Prior Undisputed Transactions (references)
  prior_undisputed_transactions: [
    "ch_prior1_abc123",
    "ch_prior2_def456",
    "ch_prior3_ghi789"
  ],

  _entityType: "CE3_EVIDENCE"
}
```

### 5. Workflow State Item

Track Step Functions execution state.

```typescript
{
  // Keys
  PK: "DISPUTE#dp_1NxQkL2eZvKYlo2CXr5EPQmR",
  SK: "WORKFLOW",

  // Step Functions metadata
  executionArn: "arn:aws:states:us-east-1:123456789:execution:DisputeWorkflow:dp_xxx",
  currentState: "WaitForEvidence",
  startedAt: "2024-11-13T12:00:00Z",
  lastUpdatedAt: "2024-11-13T12:05:00Z",

  // State history
  stateHistory: [
    { state: "ValidateDispute", timestamp: "2024-11-13T12:00:01Z", status: "succeeded" },
    { state: "CreateCase", timestamp: "2024-11-13T12:00:02Z", status: "succeeded" },
    { state: "CheckCE3Eligibility", timestamp: "2024-11-13T12:00:03Z", status: "succeeded" },
    { state: "WaitForEvidence", timestamp: "2024-11-13T12:00:04Z", status: "running" }
  ],

  _entityType: "WORKFLOW"
}
```

---

## Table: `prior-transactions`

Stores customer transaction history for Visa CE 3.0 eligibility checks.

### Table Configuration

| Setting | Value |
|---------|-------|
| Table Name | `prior-transactions-{environment}` |
| Billing Mode | PAY_PER_REQUEST |
| TTL | Enabled (400-day retention) |

### Key Schema

| Attribute | Type | Key |
|-----------|------|-----|
| `PK` | String | Partition Key |
| `SK` | String | Sort Key |

### Global Secondary Indexes

| Index Name | Partition Key | Sort Key | Purpose |
|------------|---------------|----------|---------|
| `GSI1-IPIndex` | `customer_purchase_ip` | `transaction_date` | Lookup by IP |
| `GSI2-DeviceIndex` | `customer_device_fingerprint` | `transaction_date` | Lookup by device |

### Item Structure

```typescript
{
  // Keys - Primary lookup by email
  PK: "EMAIL#customer@example.com",
  SK: "TXN#1699900800#ch_1NxQkL2eZvKYlo2CXr5EPQmR",

  // Transaction identifiers
  charge_id: "ch_1NxQkL2eZvKYlo2CXr5EPQmR",
  payment_intent_id: "pi_1NxQkL2eZvKYlo2CXr5EPQmR",

  // Customer identifiers (for CE 3.0 matching)
  customer_email_address: "customer@example.com",
  customer_purchase_ip: "192.168.1.1",
  customer_device_fingerprint: "fp_abc123def456",
  customer_device_id: "dev_xyz789",
  customer_account_id: "acct_12345",

  // Transaction details
  transaction_date: 1699900800,
  amount: 15000,
  currency: "usd",
  product_description: "Premium subscription",
  merchandise_or_services: "services",

  // Shipping (if applicable)
  shipping_address: {
    line1: "123 Main St",
    city: "San Francisco",
    state: "CA",
    postal_code: "94102",
    country: "US"
  },

  // Dispute status
  disputed: false,
  dispute_id: null,

  // TTL - 400 days from transaction date (covers 365-day CE3 window + buffer)
  _ttl: 1734436800,
  _entityType: "PRIOR_TRANSACTION"
}
```

---

## Access Patterns

### Pattern 1: Get Dispute by ID

```typescript
// Query
{
  TableName: "disputes",
  KeyConditionExpression: "PK = :pk AND SK = :sk",
  ExpressionAttributeValues: {
    ":pk": "DISPUTE#dp_xxx",
    ":sk": "METADATA"
  }
}
```

### Pattern 2: Get Dispute with All Items

```typescript
// Query all items for a dispute
{
  TableName: "disputes",
  KeyConditionExpression: "PK = :pk",
  ExpressionAttributeValues: {
    ":pk": "DISPUTE#dp_xxx"
  }
}
// Returns: METADATA, EVIDENCE, BALANCE_TXN#*, CE3_EVIDENCE, WORKFLOW
```

### Pattern 3: List Disputes by Status

```typescript
// Query GSI2
{
  TableName: "disputes",
  IndexName: "GSI2-StatusIndex",
  KeyConditionExpression: "GSI2PK = :status",
  ExpressionAttributeValues: {
    ":status": "STATUS#needs_response"
  },
  ScanIndexForward: false  // Newest first
}
```

### Pattern 4: Find Disputes by Charge

```typescript
// Query GSI1
{
  TableName: "disputes",
  IndexName: "GSI1-ChargeIndex",
  KeyConditionExpression: "GSI1PK = :charge",
  ExpressionAttributeValues: {
    ":charge": "CHARGE#ch_xxx"
  }
}
```

### Pattern 5: Find Past-Due Disputes

```typescript
// Query GSI3 with deadline filter
{
  TableName: "disputes",
  IndexName: "GSI3-DeadlineIndex",
  KeyConditionExpression: "GSI3PK = :deadline AND GSI3SK < :now",
  ExpressionAttributeValues: {
    ":deadline": "DEADLINE",
    ":now": Math.floor(Date.now() / 1000)
  }
}
```

### Pattern 6: Get Prior Transactions for CE 3.0

```typescript
// Query prior-transactions table
// Get transactions from 120-365 days ago for a customer email
const now = Math.floor(Date.now() / 1000);
const minDate = now - (365 * 24 * 60 * 60);  // 365 days ago
const maxDate = now - (120 * 24 * 60 * 60);  // 120 days ago

{
  TableName: "prior-transactions",
  KeyConditionExpression: "PK = :email AND SK BETWEEN :minSK AND :maxSK",
  FilterExpression: "disputed = :false",
  ExpressionAttributeValues: {
    ":email": "EMAIL#customer@example.com",
    ":minSK": `TXN#${minDate}`,
    ":maxSK": `TXN#${maxDate}`,
    ":false": false
  }
}
```

---

## DynamoDB Streams Integration

### Stream Configuration

```typescript
{
  StreamSpecification: {
    StreamEnabled: true,
    StreamViewType: "NEW_AND_OLD_IMAGES"
  }
}
```

### Stream Processor Lambda Triggers

| Event Type | Action |
|------------|--------|
| INSERT (DISPUTE METADATA) | Publish `dispute.created` to EventBridge |
| MODIFY (status change) | Publish `dispute.status_changed` to EventBridge |
| MODIFY (evidence added) | Publish `dispute.evidence_submitted` to EventBridge |
| INSERT (BALANCE_TXN) | Publish `balance_transaction.created` to EventBridge |

---

## CloudFormation Template Snippet

```yaml
Resources:
  DisputesTable:
    Type: AWS::DynamoDB::Table
    Properties:
      TableName: !Sub "disputes-${Environment}"
      BillingMode: PAY_PER_REQUEST
      PointInTimeRecoverySpecification:
        PointInTimeRecoveryEnabled: true
      SSESpecification:
        SSEEnabled: true
        SSEType: KMS
      StreamSpecification:
        StreamViewType: NEW_AND_OLD_IMAGES

      AttributeDefinitions:
        - AttributeName: PK
          AttributeType: S
        - AttributeName: SK
          AttributeType: S
        - AttributeName: GSI1PK
          AttributeType: S
        - AttributeName: GSI1SK
          AttributeType: S
        - AttributeName: GSI2PK
          AttributeType: S
        - AttributeName: GSI2SK
          AttributeType: N
        - AttributeName: GSI3PK
          AttributeType: S
        - AttributeName: GSI3SK
          AttributeType: N
        - AttributeName: GSI4PK
          AttributeType: S

      KeySchema:
        - AttributeName: PK
          KeyType: HASH
        - AttributeName: SK
          KeyType: RANGE

      GlobalSecondaryIndexes:
        - IndexName: GSI1-ChargeIndex
          KeySchema:
            - AttributeName: GSI1PK
              KeyType: HASH
            - AttributeName: GSI1SK
              KeyType: RANGE
          Projection:
            ProjectionType: ALL

        - IndexName: GSI2-StatusIndex
          KeySchema:
            - AttributeName: GSI2PK
              KeyType: HASH
            - AttributeName: GSI2SK
              KeyType: RANGE
          Projection:
            ProjectionType: ALL

        - IndexName: GSI3-DeadlineIndex
          KeySchema:
            - AttributeName: GSI3PK
              KeyType: HASH
            - AttributeName: GSI3SK
              KeyType: RANGE
          Projection:
            ProjectionType: KEYS_ONLY

        - IndexName: GSI4-PaymentIntentIndex
          KeySchema:
            - AttributeName: GSI4PK
              KeyType: HASH
          Projection:
            ProjectionType: KEYS_ONLY

  PriorTransactionsTable:
    Type: AWS::DynamoDB::Table
    Properties:
      TableName: !Sub "prior-transactions-${Environment}"
      BillingMode: PAY_PER_REQUEST
      TimeToLiveSpecification:
        AttributeName: _ttl
        Enabled: true

      AttributeDefinitions:
        - AttributeName: PK
          AttributeType: S
        - AttributeName: SK
          AttributeType: S
        - AttributeName: customer_purchase_ip
          AttributeType: S
        - AttributeName: customer_device_fingerprint
          AttributeType: S
        - AttributeName: transaction_date
          AttributeType: N

      KeySchema:
        - AttributeName: PK
          KeyType: HASH
        - AttributeName: SK
          KeyType: RANGE

      GlobalSecondaryIndexes:
        - IndexName: GSI1-IPIndex
          KeySchema:
            - AttributeName: customer_purchase_ip
              KeyType: HASH
            - AttributeName: transaction_date
              KeyType: RANGE
          Projection:
            ProjectionType: ALL

        - IndexName: GSI2-DeviceIndex
          KeySchema:
            - AttributeName: customer_device_fingerprint
              KeyType: HASH
            - AttributeName: transaction_date
              KeyType: RANGE
          Projection:
            ProjectionType: ALL
```

---

## Capacity Planning

### Estimated Item Sizes

| Item Type | Avg Size | Max Size |
|-----------|----------|----------|
| METADATA | 2 KB | 10 KB |
| EVIDENCE | 50 KB | 400 KB |
| BALANCE_TXN | 0.5 KB | 1 KB |
| CE3_EVIDENCE | 5 KB | 20 KB |
| WORKFLOW | 2 KB | 10 KB |
| PRIOR_TRANSACTION | 1 KB | 3 KB |

### Cost Estimation (1M disputes/month)

| Operation | Count/Month | WCU/RCU | Est. Cost |
|-----------|-------------|---------|-----------|
| Create dispute | 1M | 2 WCU each | ~$1.25 |
| Update status | 3M | 2 WCU each | ~$3.75 |
| Read dispute | 10M | 1 RCU each | ~$1.25 |
| Query by status | 5M | 10 RCU avg | ~$6.25 |
| **Total** | - | - | **~$15-20/mo** |

*Note: On-demand pricing, actual costs vary by region and usage patterns.*

---

## Security Considerations

1. **Encryption**: All data encrypted at rest using AWS-managed KMS keys
2. **IAM Policies**: Least-privilege access per Lambda function
3. **VPC Endpoints**: DynamoDB accessed via VPC endpoint (no internet traversal)
4. **PII Handling**: Customer email/IP stored in separate table with shorter TTL
5. **Audit Trail**: DynamoDB Streams + CloudTrail for all operations
