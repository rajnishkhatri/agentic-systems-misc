# Lesson 16 Datasets: Financial Task Suite

**Generated:** Task 6.0 (2025-11-24)
**Purpose:** 300 synthetic financial tasks for evaluating agent orchestration patterns
**Quality:** 100% schema-compliant, deterministic generation with seed=42

---

## Overview

This directory contains 3 synthetic financial datasets (100 tasks each) designed for the **AgentArch benchmark** reproduction in Lesson 16. The datasets represent realistic financial workflows with controlled challenge injection to test agent reliability.

**Total Tasks:** 300 (100 invoices + 100 transactions + 100 reconciliations)

**Use Cases:**
- Evaluate 5 orchestration patterns (Sequential, Hierarchical, Iterative, State Machine, Voting)
- Measure 4 metrics (task success rate, error propagation index, latency P50/P95, cost)
- Test reliability components (retry, circuit breaker, checkpointing, validation, isolation)
- Train students on production agent evaluation methodology

---

## Datasets

### 1. Invoice Processing Tasks
**File:** `invoices_100.json`
**Size:** 57 KB
**Task Count:** 100

**Description:**
Invoice extraction and validation workflow testing OCR error handling, missing field detection, and duplicate invoice prevention.

**Workflow:** Extract vendor → Validate amount → Route for approval

**Challenge Distribution:**
| Challenge Type | Count | Percentage |
|---------------|-------|------------|
| OCR Errors (vendor name typos) | 13 | 13% |
| Missing Fields (amount/status) | 13 | 13% |
| Duplicate Invoices | 11 | 11% |
| Valid Invoices | 68 | 68% |

**Schema:**
```json
{
  "invoice_id": "INV-2024-001",
  "vendor": "TechSolutions Ltd",
  "amount": 1234.56,
  "date": "2024-01-15",
  "line_items": [
    {"description": "Software License", "quantity": 10, "unit_price": 123.45}
  ],
  "status": "approved",
  "has_ocr_error": false,
  "has_missing_fields": false,
  "is_duplicate": false,
  "gold_label": {
    "is_valid": true,
    "reason": "valid"
  }
}
```

**Gold Labels:**
- `is_valid`: Boolean indicating whether invoice should be processed
- `reason`: "valid" | "ocr_error" | "missing_required_fields" | "duplicate_invoice"

**Statistics:**
- Vendor diversity: 30 unique vendors
- Amount range: $21.72 to $7,435.91
- Median amount: $703.62
- Date range: January 2024 to December 2024

---

### 2. Fraud Detection Tasks
**File:** `transactions_100.json`
**Size:** 26.67 KB
**Task Count:** 100

**Description:**
Transaction fraud detection testing imbalanced classification, ambiguous patterns, and high-value transaction handling.

**Workflow:** Transaction analysis → Merchant verification → User behavior check

**Challenge Distribution:**
| Challenge Type | Count | Percentage |
|---------------|-------|------------|
| Fraud Transactions | 10 | 10% |
| - Stolen Card | 5 | 5% |
| - Account Takeover | 3 | 3% |
| - Synthetic Fraud | 2 | 2% |
| Ambiguous Patterns (confidence 0.4-0.6) | 15 | 15% |
| High-Value Transactions (>$10K) | 10 | 10% |
| Legitimate Transactions | 90 | 90% |

**Schema:**
```json
{
  "transaction_id": "TXN-00001",
  "merchant": "Amazon",
  "amount": 127.99,
  "timestamp": "2024-01-15T14:32:00Z",
  "user_id": "user_1234",
  "user_behavior": {
    "transaction_count_24h": 3,
    "avg_transaction_amount": 85.50,
    "account_age_days": 365
  },
  "fraud_label": false,
  "fraud_type": null,
  "gold_label_confidence": 0.95
}
```

**Gold Labels:**
- `fraud_label`: Boolean indicating fraud (true) or legitimate (false)
- `fraud_type`: "stolen_card" | "account_takeover" | "synthetic_fraud" | null
- `gold_label_confidence`: Float 0.0-1.0 (ambiguous if 0.4-0.6)

**Statistics:**
- Merchant diversity: 43 unique merchants (Amazon, PayPal, Stripe, etc.)
- Amount range: $3.92 to $31,869.79
- Fraud rate: 10.0% (exact target)
- Ambiguous rate: 15.0% (within 20% target)

---

### 3. Account Reconciliation Tasks
**File:** `reconciliation_100.json`
**Size:** 262.74 KB
**Task Count:** 100

**Description:**
Bank transaction to ledger entry matching testing date mismatches, amount rounding errors, duplicate entries, and missing counterparties.

**Workflow:** Match bank transactions → Validate amounts → Flag discrepancies

**Challenge Distribution:**
| Challenge Type | Count | Percentage |
|---------------|-------|------------|
| Date Mismatches (posting ≠ transaction date) | 25 | 25% |
| Amount Rounding Errors ($1234.56 vs $1234.50) | 20 | 20% |
| Duplicate Entries (multiple ledger records) | 15 | 15% |
| Missing Counterparty (unmatched bank transaction) | 18 | 18% |
| Perfect Match | 54 | 54% |

**Reconciliation Status:**
| Status | Count | Description |
|--------|-------|-------------|
| perfect_match | 54 | All transactions match exactly |
| resolvable_with_logic | 31 | Resolvable with date tolerance or rounding |
| manual_review_required | 15 | Requires human intervention |

**Schema:**
```json
{
  "reconciliation_id": "REC-00001",
  "bank_transactions": [
    {
      "transaction_id": "BANK-00001-000",
      "date": "2024-01-15",
      "amount": 1234.56,
      "counterparty": "Acme Corp",
      "description": "Invoice payment"
    }
  ],
  "ledger_entries": [
    {
      "entry_id": "LED-00001-000",
      "posting_date": "2024-01-15",
      "amount": 1234.56,
      "account": "1000-12"
    }
  ],
  "expected_matches": [
    {"bank_id": "BANK-00001-000", "ledger_id": "LED-00001-000"}
  ],
  "reconciliation_status": "perfect_match",
  "discrepancy_amount": 0.0,
  "challenge_types": []
}
```

**Gold Labels:**
- `expected_matches`: List of correct bank_id → ledger_id mappings
- `reconciliation_status`: "perfect_match" | "resolvable_with_logic" | "manual_review_required"
- `discrepancy_amount`: Total unmatched amount ($0 to $482.96)
- `challenge_types`: List of challenges present in this task

**Statistics:**
- Average transactions per reconciliation: 5.2
- Date mismatch range: 1-3 days
- Amount rounding range: $0.01 to $1.00
- Discrepancy amount P95: $184.62

---

## Dataset Generation

### Reproducibility

All datasets are **deterministically generated** using `seed=42`:

```python
from pathlib import Path
from backend.data_generation.invoices import generate_invoice_dataset
from backend.data_generation.transactions import generate_transaction_dataset
from backend.data_generation.reconciliation import generate_reconciliation_dataset

# Generate 100 invoices (reproducible)
invoices = generate_invoice_dataset(count=100, seed=42)

# Generate 100 transactions (10% fraud rate)
transactions = generate_transaction_dataset(count=100, fraud_rate=0.10, seed=42)

# Generate 100 reconciliations (mixed difficulty)
reconciliations = generate_reconciliation_dataset(count=100, difficulty="mixed", seed=42)
```

**Verification:** Running generation with `seed=42` produces **identical results** across runs.

### Regeneration Commands

To regenerate datasets with different parameters:

```bash
# From repository root
cd lesson-16

# Regenerate invoices with different OCR error rate (20%)
python -c "
from backend.data_generation.invoices import generate_invoice_dataset
import json
invoices = generate_invoice_dataset(count=100, seed=99)
with open('data/invoices_100_v2.json', 'w') as f:
    json.dump(invoices, f, indent=2)
"

# Regenerate transactions with 20% fraud rate
python -c "
from backend.data_generation.transactions import generate_transaction_dataset
import json
txns = generate_transaction_dataset(count=100, fraud_rate=0.20, seed=99)
with open('data/transactions_100_v2.json', 'w') as f:
    json.dump(txns, f, indent=2)
"

# Regenerate hard-only reconciliations
python -c "
from backend.data_generation.reconciliation import generate_reconciliation_dataset
import json
recs = generate_reconciliation_dataset(count=100, difficulty='hard', seed=99)
with open('data/reconciliation_100_v2.json', 'w') as f:
    json.dump(recs, f, indent=2)
"
```

---

## Usage in Notebooks

### Loading Datasets

**Method 1: Direct JSON Loading (Notebooks 08-12, 15)**

```python
import json
from pathlib import Path

# Load invoice dataset
data_dir = Path("../data")
with open(data_dir / "invoices_100.json") as f:
    invoice_data = json.load(f)

# Extract array from metadata-wrapped format
if "metadata" in invoice_data:
    invoices = invoice_data["data"]
else:
    invoices = invoice_data

# Sample 10 invoices for demo
sample_invoices = invoices[:10]
```

**Method 2: FinancialTaskGenerator (Notebook 14 - Benchmark)**

```python
from backend.benchmarks import FinancialTaskGenerator

generator = FinancialTaskGenerator()
data_dir = Path("../data")
generator.load_datasets(data_dir)

# Generate mixed task suite (30 tasks: ~10 invoice + ~10 fraud + ~10 reconciliation)
tasks = generator.generate_task_suite(count=30, strategy="random", seed=42)

# Filter by task type
invoice_tasks = generator.filter_tasks(tasks, task_type="invoice_processing")
fraud_tasks = generator.filter_tasks(tasks, task_type="fraud_detection")
```

### Task Wrapper Structure

`FinancialTaskGenerator` wraps raw dataset entries in a standard format:

```python
{
  "task_id": "INV-2024-001",
  "task_type": "invoice_processing",  # or "fraud_detection" or "account_reconciliation"
  "input_data": { ... },  # Raw dataset entry
  "gold_label": { ... },  # Expected output for evaluation
  "difficulty": "medium",  # "easy" | "medium" | "hard" (optional)
  "challenge_types": ["ocr_error"]  # List of challenges in this task
}
```

---

## Quality Validation

### Schema Compliance
- ✅ **100% of tasks** pass JSON schema validation
- ✅ All required fields present (invoice_id, vendor, amount, etc.)
- ✅ Data types correct (strings, numbers, booleans, dates)

### Challenge Distribution
- ✅ **±2% of target distribution** (better than ±5% requirement)
  - Invoice OCR errors: 13% (target: 15% ±5%)
  - Transaction fraud rate: 10.0% (target: 10% ±0.5%)
  - Reconciliation date mismatches: 25% (target: 25% ±5%)

### Gold Label Accuracy
- ✅ **100% accurate** (deterministic generation rules)
  - Invoice validation: Checks vendor in database, amount >0, required fields present
  - Fraud detection: Rule-based labels (high amount + new account = fraud)
  - Reconciliation: Exact matching algorithm for expected_matches

### Statistical Properties
- ✅ **Log-normal amount distribution** (realistic financial data)
- ✅ **Uniform date distribution** (covers full year 2024)
- ✅ **Diverse vendor/merchant names** (30-43 unique entities)

---

## Dataset Metadata

See `DATASET_SUMMARY.json` for comprehensive statistics:

```json
{
  "generation_date": "2025-11-24",
  "version": "1.0",
  "schema_version": "1.0",
  "datasets": {
    "invoices": {
      "count": 100,
      "vendor_diversity": 30,
      "challenge_distribution": {
        "ocr_errors": 13,
        "missing_fields": 13,
        "duplicates": 11
      },
      "amount_statistics": {
        "min": 21.72,
        "median": 703.62,
        "max": 7435.91
      }
    },
    "transactions": {
      "count": 100,
      "merchant_diversity": 43,
      "fraud_rate": 0.10,
      "fraud_type_distribution": {
        "stolen_card": 5,
        "account_takeover": 3,
        "synthetic_fraud": 2
      },
      "ambiguous_patterns": 15,
      "high_value_transactions": 10
    },
    "reconciliations": {
      "count": 100,
      "challenge_distribution": {
        "date_mismatch": 25,
        "amount_rounding": 20,
        "duplicate_entries": 15,
        "missing_counterparty": 18
      },
      "status_distribution": {
        "perfect_match": 54,
        "resolvable_with_logic": 31,
        "manual_review_required": 15
      },
      "discrepancy_statistics": {
        "min": 0.0,
        "median": 42.8,
        "max": 482.96
      }
    }
  }
}
```

---

## Troubleshooting

### Issue: Dataset file not found
**Error:** `FileNotFoundError: Data directory not found: lesson-16/data`

**Solution:** Ensure you're running from repository root:
```bash
cd /path/to/recipe-chatbot
python lesson-16/notebooks/14_agentarch_benchmark_reproduction.ipynb
```

Or adjust path in notebook:
```python
data_dir = Path(__file__).parent.parent / "data"  # Adjust to your location
```

### Issue: Metadata wrapper confusion
**Error:** `KeyError: 'invoice_id'` when accessing dataset

**Solution:** Check if dataset has metadata wrapper:
```python
import json
with open("data/invoices_100.json") as f:
    data = json.load(f)

# Check structure
if "metadata" in data:
    invoices = data["data"]  # Extract array
else:
    invoices = data  # Already an array
```

### Issue: Task count mismatch (28 instead of 30)
**Behavior:** `generate_task_suite(count=30)` returns 28 tasks

**Explanation:** **This is correct behavior.** Deduplication removes invalid invoices (duplicates marked in gold labels). Use larger count or disable filtering:
```python
# Generate extra to account for filtering
tasks = generator.generate_task_suite(count=35, strategy="random", seed=42)
tasks = tasks[:30]  # Take first 30
```

---

## Related Documentation

- **Tutorials:**
  - [Tutorial 05: AgentArch Benchmark Methodology](../tutorials/05_agentarch_benchmark_methodology.md) - Dataset design rationale
  - [Tutorial 06: Financial Workflow Reliability](../tutorials/06_financial_workflow_reliability.md) - Domain challenges

- **Notebooks:**
  - [Notebook 08-12](../notebooks/) - Use datasets for pattern evaluation
  - [Notebook 14: AgentArch Benchmark Reproduction](../notebooks/14_agentarch_benchmark_reproduction.ipynb) - Full benchmark with all 300 tasks

- **Backend Code:**
  - `backend/data_generation/invoices.py` - Invoice generation implementation
  - `backend/data_generation/transactions.py` - Transaction generation implementation
  - `backend/data_generation/reconciliation.py` - Reconciliation generation implementation
  - `backend/benchmarks/financial_tasks.py` - FinancialTaskGenerator wrapper

---

**Maintained by:** AI Evaluation Course Team
**Last Updated:** 2025-11-24
**Version:** 1.0
