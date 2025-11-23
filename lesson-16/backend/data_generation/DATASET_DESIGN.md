# Dataset Design Specifications

This document defines the JSON schemas, challenge distribution targets, and gold label formats for the three financial datasets used in Lesson 16 benchmarking.

## Overview

**Purpose:** Generate realistic synthetic financial datasets for evaluating agent orchestration patterns on real-world business scenarios.

**Total Dataset Size:** 300 tasks
- 100 invoice processing tasks
- 100 fraud detection tasks
- 100 account reconciliation tasks

**Reproducibility:** All datasets use seed-based random generation for deterministic output across runs.

---

## 1. Invoice Processing Dataset

**File:** `data/invoices_100.json`

**Use Case:** Extract vendor information, validate amounts, route for approval

**Challenge Types:**
- OCR errors (15%): Vendor name typos, amount misreads
- Missing fields (10%): Missing invoice_id, date, or line_items
- Duplicate invoices (8%): Same invoice submitted multiple times

### JSON Schema

```json
{
  "type": "object",
  "required": ["invoice_id", "vendor", "amount", "date", "line_items", "status"],
  "properties": {
    "invoice_id": {
      "type": "string",
      "pattern": "^INV-\\d{4}-\\d{3}$",
      "description": "Unique invoice identifier (format: INV-YYYY-NNN)"
    },
    "vendor": {
      "type": "string",
      "minLength": 1,
      "description": "Vendor/supplier name (may contain OCR errors in 15% of cases)"
    },
    "amount": {
      "type": "number",
      "minimum": 10.0,
      "maximum": 50000.0,
      "description": "Total invoice amount in USD"
    },
    "date": {
      "type": "string",
      "format": "date",
      "pattern": "^\\d{4}-\\d{2}-\\d{2}$",
      "description": "Invoice date (YYYY-MM-DD)"
    },
    "line_items": {
      "type": "array",
      "minItems": 1,
      "items": {
        "type": "object",
        "required": ["description", "quantity", "unit_price"],
        "properties": {
          "description": {"type": "string"},
          "quantity": {"type": "integer", "minimum": 1},
          "unit_price": {"type": "number", "minimum": 0}
        }
      },
      "description": "List of invoice line items"
    },
    "status": {
      "type": "string",
      "enum": ["pending", "approved", "rejected"],
      "description": "Current invoice status"
    },
    "challenge_type": {
      "type": "string",
      "enum": ["clean", "ocr_error", "missing_field", "duplicate"],
      "description": "Type of challenge injected for testing"
    },
    "gold_label": {
      "type": "object",
      "required": ["correct_vendor", "correct_amount", "approval_route"],
      "properties": {
        "correct_vendor": {"type": "string"},
        "correct_amount": {"type": "number"},
        "approval_route": {"type": "string", "enum": ["manager", "finance", "auto_approve"]}
      },
      "description": "Ground truth for evaluation"
    }
  }
}
```

### Challenge Distribution

| Challenge Type | Target % | Count (n=100) |
|----------------|----------|---------------|
| Clean (no issues) | 67% | 67 |
| OCR errors | 15% | 15 |
| Missing fields | 10% | 10 |
| Duplicate invoices | 8% | 8 |

### Gold Labels

**Format:**
```json
{
  "correct_vendor": "Acme Corp",  // Canonical vendor name
  "correct_amount": 1500.00,      // Correct total amount
  "approval_route": "manager"     // Expected routing: manager (<$10K), finance (≥$10K), auto_approve (<$500)
}
```

**Validation Rules:**
- Amounts >$10,000 → finance approval
- Amounts $500-$10,000 → manager approval
- Amounts <$500 → auto-approve

---

## 2. Fraud Detection Dataset

**File:** `data/transactions_100.json`

**Use Case:** Detect fraudulent transactions using multiple signals

**Challenge Types:**
- Fraud imbalance (10% fraud rate)
- Ambiguous patterns (20%): Borderline cases requiring human review
- High-value transactions (>$10K subset for voting ensemble testing)

### JSON Schema

```json
{
  "type": "object",
  "required": ["transaction_id", "merchant", "amount", "timestamp", "user_id", "fraud_label"],
  "properties": {
    "transaction_id": {
      "type": "string",
      "pattern": "^TXN-\\d{5}$",
      "description": "Unique transaction identifier (format: TXN-NNNNN)"
    },
    "merchant": {
      "type": "string",
      "minLength": 1,
      "description": "Merchant name (≥40 unique merchants)"
    },
    "amount": {
      "type": "number",
      "minimum": 1.0,
      "maximum": 100000.0,
      "description": "Transaction amount in USD (log-normal distribution)"
    },
    "timestamp": {
      "type": "string",
      "format": "date-time",
      "description": "Transaction timestamp (ISO 8601 format)"
    },
    "user_id": {
      "type": "string",
      "description": "User/cardholder identifier"
    },
    "user_behavior": {
      "type": "object",
      "properties": {
        "avg_transaction_amount": {"type": "number"},
        "transaction_frequency": {"type": "integer"},
        "account_age_days": {"type": "integer"}
      },
      "description": "User behavior features for fraud detection"
    },
    "fraud_label": {
      "type": "boolean",
      "description": "Gold label: true = fraud, false = legitimate"
    },
    "fraud_type": {
      "type": "string",
      "enum": ["stolen_card", "account_takeover", "synthetic_fraud", null],
      "description": "Type of fraud (null if legitimate transaction)"
    },
    "confidence": {
      "type": "number",
      "minimum": 0.0,
      "maximum": 1.0,
      "description": "Ground truth confidence score"
    },
    "challenge_type": {
      "type": "string",
      "enum": ["clean", "ambiguous", "high_value"],
      "description": "Type of challenge for testing"
    }
  }
}
```

### Challenge Distribution

| Challenge Type | Target % | Count (n=100) |
|----------------|----------|---------------|
| Legitimate (clean) | 70% | 70 |
| Fraud (10% overall) | 10% | 10 |
| - Stolen card | 40% of fraud | 4 |
| - Account takeover | 35% of fraud | 3-4 |
| - Synthetic fraud | 25% of fraud | 2-3 |
| Ambiguous patterns | 20% | 20 |
| High-value (>$10K) | ~15% | 15 |

### Gold Labels

**Format:**
```json
{
  "fraud_label": true,           // Ground truth: fraud or legitimate
  "fraud_type": "stolen_card",   // Type of fraud (null if legitimate)
  "confidence": 0.95,            // Confidence in label (0.0-1.0)
  "expected_action": "block"     // Expected action: approve, review, block
}
```

---

## 3. Account Reconciliation Dataset

**File:** `data/reconciliation_100.json`

**Use Case:** Match bank transactions to ledger entries, resolve discrepancies

**Challenge Types:**
- Date mismatches (25%): Posting date ≠ transaction date (1-3 business days)
- Amount rounding (20%): Small differences ($1234.56 vs $1234.50)
- Duplicate entries (15%): Same transaction recorded multiple times
- Missing counterparty (18%): Bank transaction with no ledger match

### JSON Schema

```json
{
  "type": "object",
  "required": ["reconciliation_id", "bank_transactions", "ledger_entries", "expected_matches"],
  "properties": {
    "reconciliation_id": {
      "type": "string",
      "pattern": "^REC-\\d{3}$",
      "description": "Unique reconciliation task identifier (format: REC-NNN)"
    },
    "bank_transactions": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["transaction_id", "date", "amount", "description"],
        "properties": {
          "transaction_id": {"type": "string"},
          "date": {"type": "string", "format": "date"},
          "amount": {"type": "number"},
          "description": {"type": "string"}
        }
      },
      "description": "List of bank transactions to reconcile"
    },
    "ledger_entries": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["entry_id", "posting_date", "amount", "account"],
        "properties": {
          "entry_id": {"type": "string"},
          "posting_date": {"type": "string", "format": "date"},
          "amount": {"type": "number"},
          "account": {"type": "string"}
        }
      },
      "description": "List of ledger entries to reconcile"
    },
    "expected_matches": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["bank_id", "ledger_id"],
        "properties": {
          "bank_id": {"type": "string"},
          "ledger_id": {"type": "string"},
          "match_quality": {
            "type": "string",
            "enum": ["perfect", "date_mismatch", "amount_rounding"]
          }
        }
      },
      "description": "Gold labels: expected bank-ledger matches"
    },
    "reconciliation_status": {
      "type": "string",
      "enum": ["perfect_match", "resolvable_with_logic", "manual_review_required"],
      "description": "Expected reconciliation outcome"
    },
    "difficulty": {
      "type": "string",
      "enum": ["easy", "medium", "hard"],
      "description": "Task difficulty level"
    },
    "challenge_types": {
      "type": "array",
      "items": {
        "type": "string",
        "enum": ["date_mismatch", "amount_rounding", "duplicate_entry", "missing_counterparty"]
      },
      "description": "List of challenges present in this task"
    }
  }
}
```

### Challenge Distribution

| Challenge Type | Target % | Count (n=100) |
|----------------|----------|---------------|
| Date mismatch (1-3 days) | 25% | 25 |
| Amount rounding (<$0.50 diff) | 20% | 20 |
| Duplicate entries | 15% | 15 |
| Missing counterparty | 18% | 18 |
| Clean (perfect match) | 22% | 22 |

### Difficulty Distribution

| Difficulty | Target % | Count (n=100) | Characteristics |
|------------|----------|---------------|-----------------|
| Easy | 20% | 20 | Perfect matches, no discrepancies |
| Medium | 50% | 50 | 1-2 challenges, resolvable with logic |
| Hard | 30% | 30 | 3+ challenges, manual review likely required |

### Gold Labels

**Format:**
```json
{
  "expected_matches": [
    {
      "bank_id": "BANK-001",
      "ledger_id": "LED-001",
      "match_quality": "date_mismatch"  // perfect, date_mismatch, amount_rounding
    }
  ],
  "reconciliation_status": "resolvable_with_logic",  // perfect_match, resolvable, manual_review
  "discrepancy_amount": 0.50,  // Total unreconciled amount
  "resolution_strategy": "apply_date_tolerance"  // Recommended resolution approach
}
```

---

## Data Generation Guidelines

### Reproducibility Requirements

1. **Seed-Based Generation:** All datasets must accept a `seed` parameter for reproducible randomness
2. **Same Input → Same Output:** Identical seed values must produce identical datasets across runs
3. **Version Tracking:** Include `generation_date`, `version`, and `schema_version` in dataset metadata

### Statistical Properties

1. **Amount Distributions:**
   - Invoice amounts: Log-normal distribution, median ~$5,000
   - Transaction amounts: Log-normal distribution, long tail for fraud detection
   - Reconciliation amounts: Normal distribution, median ~$2,000

2. **Date Distributions:**
   - Uniform distribution over 2024 calendar year
   - Business days only for bank transactions (exclude weekends/holidays)

3. **Vendor/Merchant Diversity:**
   - Invoices: ≥30 unique vendors
   - Transactions: ≥40 unique merchants
   - Follow Zipf's law: Few vendors/merchants appear frequently, long tail of rare ones

### Edge Cases to Include

1. **Boundary Values:**
   - $0.00 amounts (edge case for validation)
   - Maximum amounts ($50K invoices, $100K transactions)
   - Single line item invoices

2. **Special Characters:**
   - Vendor names with apostrophes: "Joe's Hardware"
   - Ampersands: "Smith & Associates"
   - Periods/abbreviations: "Corp.", "Ltd."

3. **Temporal Edge Cases:**
   - Same-day multi-transactions
   - Cross-month reconciliation (Dec 31 → Jan 1)
   - Future-dated invoices (for validation testing)

---

## Validation Checklist

Before finalizing datasets, verify:

- [ ] All 3 datasets schema-compliant (pass JSON Schema validation)
- [ ] Challenge distribution within ±5% of targets
- [ ] No duplicate IDs across datasets
- [ ] Gold labels 100% accurate (verified by deterministic checks)
- [ ] Reproducibility: Same seed generates identical output across 3 runs
- [ ] Statistical properties match specifications (log-normal, uniform)
- [ ] Edge case coverage: $0 amounts, future dates, special characters
- [ ] Cross-dataset consistency: No overlapping IDs
- [ ] Human readability: Spot-check 10 samples for plausibility
- [ ] Metadata present: generation_date, version, schema_version, challenge_distribution

---

## Usage Examples

### Generate Invoice Dataset

```python
from backend.data_generation.invoices import generate_invoice_dataset

# Generate 100 invoices with seed 42 for reproducibility
invoices = generate_invoice_dataset(count=100, seed=42)

# Save to file
import json
with open("data/invoices_100.json", "w") as f:
    json.dump({
        "metadata": {
            "generation_date": "2024-11-23",
            "version": "1.0",
            "schema_version": "1.0",
            "total_count": len(invoices),
            "challenge_distribution": {
                "clean": 67,
                "ocr_error": 15,
                "missing_field": 10,
                "duplicate": 8
            }
        },
        "invoices": invoices
    }, f, indent=2)
```

### Validate Dataset

```python
from backend.data_generation import validate_json_schema

# Load schema
with open("backend/data_generation/schemas/invoice_schema.json") as f:
    schema = json.load(f)

# Validate each invoice
for invoice in invoices:
    is_valid, errors = validate_json_schema(invoice, schema)
    if not is_valid:
        print(f"Validation errors for {invoice['invoice_id']}: {errors}")
```

---

## References

- Task 6.2: Invoice Dataset Generation (DC2.1)
- Task 6.3: Transaction Dataset Generation (DC2.2)
- Task 6.4: Reconciliation Dataset Generation (DC2.3)
- Task 6.5: Dataset Quality Validation
