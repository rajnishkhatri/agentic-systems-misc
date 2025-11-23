# Tutorial 6: Financial Workflow Reliability

**Estimated Reading Time:** 20-25 minutes

## Learning Objectives

By the end of this tutorial, you will be able to:

1. Analyze real-world financial agent applications using the FinRobot case study
2. Design ERP integration guardrails for database validation, business rules, and approval routing
3. Implement compliance requirements: GDPR PII redaction, SOC2 audit logs, retention policies
4. Identify and mitigate domain-specific challenges in financial workflows
5. Build production-ready financial agents with enterprise-grade reliability

## Prerequisites

- Completion of [Tutorial 1: Agent Reliability Fundamentals](01_agent_reliability_fundamentals.md)
- Completion of [Tutorial 3: Deterministic Execution Strategies](03_deterministic_execution_strategies.md)
- Completion of [Tutorial 4: Error Propagation Analysis](04_error_propagation_analysis.md)
- Understanding of audit logging concepts
- Familiarity with financial workflows (invoices, fraud detection, reconciliation)

---

## 1. Introduction: Why Financial Workflows Are Special

Financial workflows present **unique reliability challenges** that go beyond typical AI applications:

### Critical Constraints

| Constraint | Requirement | Impact |
|------------|-------------|--------|
| **Regulatory Compliance** | GDPR, SOC2, PCI-DSS | Data handling, retention, auditability |
| **Zero Tolerance for Errors** | <0.1% error rate for payment amounts | Downstream financial impact |
| **Audit Trail Completeness** | 100% decision traceability | Legal and regulatory requirements |
| **Real-Time Business Rules** | Integration with ERP systems | Database lookups, approval routing |
| **Data Quality Issues** | OCR errors, missing fields, duplicates | Domain-specific error handling |

### Real-World Impact

**Example: Invoice Processing Agent Failure**

```
Agent Output: Invoice amount = $10,050.00 (hallucination)
Actual Amount: $1,050.00
Error: Misread OCR text "1,050" as "10,050"
Financial Impact: $9,000 overpayment
Root Cause: No database validation against purchase order
```

**Cost of Failure:**
- Direct financial loss: $9,000
- Vendor relationship damage
- Audit finding and compliance fine
- Engineering time to investigate and fix

**Prevention Strategy:** ERP integration guardrails (covered in Section 2)

---

## 2. FinRobot Case Study: Real-World Financial Agent Architecture

### 2.1 FinRobot Overview

**FinRobot** is a research project from the University of California demonstrating multi-agent systems for financial workflows. It provides:

- **12 financial agents**: Invoice processing, fraud detection, reconciliation, reporting
- **ERP integration**: SAP, Oracle, QuickBooks connectors
- **Compliance framework**: GDPR/SOC2 audit logging
- **Production deployment**: Handles 10K+ transactions/day

**Architecture Diagram:**

```
┌─────────────────────────────────────────────────────────────────┐
│                        FinRobot System                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐     │
│  │   Invoice    │    │    Fraud     │    │Reconciliation│     │
│  │  Processing  │    │  Detection   │    │    Agent     │     │
│  │    Agent     │    │    Agent     │    │              │     │
│  └──────┬───────┘    └──────┬───────┘    └──────┬───────┘     │
│         │                   │                   │              │
│         └───────────────────┴───────────────────┘              │
│                             │                                  │
│                   ┌─────────▼─────────┐                        │
│                   │  Reliability      │                        │
│                   │  Framework        │                        │
│                   │  (7 Components)   │                        │
│                   └─────────┬─────────┘                        │
│                             │                                  │
│         ┌───────────────────┼───────────────────┐              │
│         │                   │                   │              │
│  ┌──────▼───────┐   ┌──────▼──────┐   ┌────────▼──────┐       │
│  │ ERP Systems  │   │ Compliance  │   │ Audit Logging │       │
│  │ (SAP/Oracle) │   │  (GDPR/SOC2)│   │ (Elasticsearch)│       │
│  └──────────────┘   └─────────────┘   └───────────────┘       │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 2.2 Key Success Factors

**1. Database-Backed Validation**

All agent outputs are validated against ERP system data:

```python
# Invoice Processing: Validate vendor exists in ERP
def validate_vendor(vendor_name: str, erp_client: ERPClient) -> dict[str, Any]:
    """Validate vendor against ERP system database.

    Args:
        vendor_name: Vendor name extracted by agent
        erp_client: Connection to ERP system (SAP/Oracle)

    Returns:
        Validation result with vendor_id and business rules

    Raises:
        ValueError: If vendor not found in ERP
    """
    # Query ERP database
    vendor = erp_client.lookup_vendor(vendor_name)

    if not vendor:
        raise ValueError(f"Vendor '{vendor_name}' not found in ERP system")

    # Check vendor status
    if vendor["status"] != "ACTIVE":
        raise ValueError(f"Vendor '{vendor_name}' is {vendor['status']}, not ACTIVE")

    return {
        "vendor_id": vendor["vendor_id"],
        "vendor_name": vendor["canonical_name"],  # Use ERP canonical name
        "payment_terms": vendor["payment_terms"],
        "approval_limit": vendor["approval_limit"]
    }
```

**Impact:**
- Catches hallucinations: Agent outputs "ACME" but ERP has "ACME Corp" → normalized
- Enforces business rules: Inactive vendors rejected automatically
- Provides approval routing data: Payment terms determine approval workflow

**2. Deterministic Business Logic**

Critical decisions use deterministic rules, not LLM judgment:

```python
# Approval Routing: Deterministic based on amount and vendor
def route_invoice_for_approval(
    invoice_amount: float,
    vendor_id: str,
    erp_client: ERPClient
) -> dict[str, str]:
    """Determine approval routing using business rules (deterministic).

    Args:
        invoice_amount: Invoice amount in USD
        vendor_id: ERP vendor ID
        erp_client: Connection to ERP system

    Returns:
        Approval routing with approver and reason
    """
    vendor = erp_client.get_vendor(vendor_id)
    approval_limit = vendor["approval_limit"]

    # Deterministic routing rules
    if invoice_amount > 50000:
        return {
            "approver": "CFO",
            "reason": f"Amount ${invoice_amount:,.2f} exceeds $50K threshold"
        }
    elif invoice_amount > approval_limit:
        return {
            "approver": "FINANCE_MANAGER",
            "reason": f"Amount ${invoice_amount:,.2f} exceeds vendor limit ${approval_limit:,.2f}"
        }
    else:
        return {
            "approver": "DEPARTMENT_MANAGER",
            "reason": f"Amount ${invoice_amount:,.2f} within standard approval limit"
        }
```

**Why Deterministic?**
- **Auditability**: "Why was this routed to CFO?" → Clear rule-based answer
- **Consistency**: Same amount always routes to same approver
- **No Hallucinations**: LLMs cannot invent approval rules

**3. Complete Audit Trail**

Every agent decision is logged for compliance and debugging:

```python
# From backend/reliability/audit_log.py
from lesson_16.backend.reliability import AuditLogger

logger = AuditLogger(
    log_dir="logs/audit",
    retention_days=2555  # 7 years for SOC2 compliance
)

# Log invoice processing decision
logger.log_decision(
    workflow_id="invoice_20231115_0001",
    agent_name="InvoiceExtractorAgent",
    step="vendor_extraction",
    input_data={"ocr_text": "Invoice from ACME Corp..."},
    output_data={"vendor_name": "ACME Corp", "vendor_id": "V12345"},
    duration_ms=1250,
    metadata={
        "model": "gpt-4",
        "temperature": 0.0,
        "validation_status": "passed",
        "erp_lookup": True
    }
)
```

**See:** [backend/reliability/audit_log.py](../backend/reliability/audit_log.py:45-89) for full implementation.

---

## 3. ERP Integration Guardrails

### 3.1 Database Validation Pattern

**Problem:** Agents hallucinate vendor names, account numbers, cost centers.

**Solution:** Validate all extracted entities against ERP system database.

**Implementation:**

```python
from pydantic import BaseModel, field_validator

class InvoiceExtraction(BaseModel):
    """Pydantic schema with ERP validation."""
    vendor_name: str
    vendor_id: str | None = None  # Populated by ERP lookup
    invoice_amount: float
    cost_center: str

    @field_validator("vendor_name")
    @classmethod
    def validate_vendor_exists(cls, v: str) -> str:
        """Validate vendor exists in ERP system."""
        # In production, inject ERPClient via __init__ or context
        # Here we show validation logic
        if not v or len(v) < 3:
            raise ValueError("Vendor name too short")
        return v

    @field_validator("invoice_amount")
    @classmethod
    def validate_amount_positive(cls, v: float) -> float:
        """Validate invoice amount is positive."""
        if v <= 0:
            raise ValueError(f"Invoice amount must be positive, got {v}")
        return v

    @field_validator("cost_center")
    @classmethod
    def validate_cost_center_format(cls, v: str) -> str:
        """Validate cost center matches ERP format."""
        # Example: Cost centers are 4-digit codes
        if not v.isdigit() or len(v) != 4:
            raise ValueError(f"Cost center must be 4 digits, got '{v}'")
        return v

# Usage with ERP lookup
def extract_and_validate_invoice(ocr_text: str, erp_client: ERPClient) -> InvoiceExtraction:
    """Extract invoice data with ERP validation."""
    # Step 1: LLM extracts fields
    raw_extraction = llm_extract_invoice(ocr_text)  # Returns dict

    # Step 2: Pydantic validation (basic)
    invoice = InvoiceExtraction(**raw_extraction)

    # Step 3: ERP lookup and enrichment
    vendor = erp_client.lookup_vendor(invoice.vendor_name)
    if not vendor:
        raise ValueError(f"Vendor '{invoice.vendor_name}' not found in ERP")

    # Update with canonical ERP data
    invoice.vendor_id = vendor["vendor_id"]
    invoice.vendor_name = vendor["canonical_name"]  # Normalize spelling

    return invoice
```

**Error Prevention:**

| Without ERP Validation | With ERP Validation |
|------------------------|---------------------|
| Agent outputs "ACME" | Agent outputs "ACME" → ERP lookup → "ACME Corp" (canonical) |
| Hallucinated vendor "XYZ Ltd" accepted | Hallucinated "XYZ Ltd" → ERP lookup fails → ValueError raised |
| Duplicate vendor names (3 spellings) | All spellings normalized to ERP canonical name |

**See:** [Tutorial 3: Deterministic Execution Strategies](03_deterministic_execution_strategies.md#pydantic-schema-validation) for Pydantic validation patterns.

### 3.2 Business Rules Enforcement

**Problem:** Agents need to apply complex business logic (approval routing, payment terms, discount eligibility).

**Solution:** Encode business rules as deterministic Python functions, not LLM prompts.

**Example: Payment Terms Calculation**

```python
from datetime import datetime, timedelta

def calculate_payment_due_date(
    invoice_date: datetime,
    payment_terms: str,
    vendor_id: str,
    erp_client: ERPClient
) -> datetime:
    """Calculate payment due date using business rules.

    Args:
        invoice_date: Invoice date
        payment_terms: Payment terms code (e.g., "NET30", "2/10 NET30")
        vendor_id: ERP vendor ID
        erp_client: Connection to ERP system

    Returns:
        Payment due date

    Raises:
        ValueError: If payment terms invalid
    """
    # Validate payment terms against ERP
    vendor = erp_client.get_vendor(vendor_id)
    if payment_terms not in vendor["allowed_payment_terms"]:
        raise ValueError(
            f"Payment terms '{payment_terms}' not allowed for vendor {vendor_id}. "
            f"Allowed: {vendor['allowed_payment_terms']}"
        )

    # Business rules for payment terms
    if payment_terms == "NET30":
        return invoice_date + timedelta(days=30)
    elif payment_terms == "NET60":
        return invoice_date + timedelta(days=60)
    elif payment_terms.startswith("2/10"):
        # 2% discount if paid within 10 days, else NET30
        discount_date = invoice_date + timedelta(days=10)
        return discount_date  # Encourage early payment
    else:
        raise ValueError(f"Unknown payment terms: {payment_terms}")
```

**Why Not Use LLM?**

```python
# ❌ BAD: LLM calculates payment date (non-deterministic)
prompt = f"Invoice date is {invoice_date}. Payment terms are NET30. When is payment due?"
response = llm.generate(prompt)  # Might hallucinate: "In about a month" or "March 30"

# ✅ GOOD: Deterministic business logic
due_date = calculate_payment_due_date(invoice_date, "NET30", vendor_id, erp_client)
# Always returns: invoice_date + timedelta(days=30)
```

**Benefits:**
- **Deterministic**: Same inputs → same output every time
- **Auditable**: Code review can verify business rules
- **Testable**: Unit tests ensure rules are correct
- **Fast**: No LLM API call needed

### 3.3 Approval Routing Logic

**Problem:** Multi-level approval workflows with complex rules.

**Solution:** State machine orchestration with deterministic routing.

**Example: Three-Tier Approval Workflow**

```python
from enum import Enum

class ApprovalState(Enum):
    SUBMITTED = "submitted"
    MANAGER_REVIEW = "manager_review"
    FINANCE_REVIEW = "finance_review"
    CFO_REVIEW = "cfo_review"
    APPROVED = "approved"
    REJECTED = "rejected"

def determine_approval_route(
    invoice_amount: float,
    vendor_risk_level: str,
    department: str
) -> list[ApprovalState]:
    """Determine approval route based on business rules.

    Args:
        invoice_amount: Invoice amount in USD
        vendor_risk_level: Risk level from ERP (LOW, MEDIUM, HIGH)
        department: Department code

    Returns:
        List of approval states (in order)
    """
    route = [ApprovalState.SUBMITTED]

    # Rule 1: All invoices go to manager
    route.append(ApprovalState.MANAGER_REVIEW)

    # Rule 2: Amounts > $10K go to finance
    if invoice_amount > 10000:
        route.append(ApprovalState.FINANCE_REVIEW)

    # Rule 3: Amounts > $50K or HIGH risk go to CFO
    if invoice_amount > 50000 or vendor_risk_level == "HIGH":
        route.append(ApprovalState.CFO_REVIEW)

    route.append(ApprovalState.APPROVED)
    return route

# Usage
route = determine_approval_route(
    invoice_amount=75000,
    vendor_risk_level="MEDIUM",
    department="IT"
)
# Result: [SUBMITTED, MANAGER_REVIEW, FINANCE_REVIEW, CFO_REVIEW, APPROVED]
```

**Integration with State Machine Orchestrator:**

```python
from lesson_16.backend.orchestrators import StateMachineOrchestrator

# Define state machine with approval routing
orchestrator = StateMachineOrchestrator(
    initial_state=ApprovalState.SUBMITTED,
    states=route,
    transition_rules={
        ApprovalState.SUBMITTED: [ApprovalState.MANAGER_REVIEW],
        ApprovalState.MANAGER_REVIEW: [ApprovalState.FINANCE_REVIEW, ApprovalState.APPROVED],
        ApprovalState.FINANCE_REVIEW: [ApprovalState.CFO_REVIEW, ApprovalState.APPROVED],
        ApprovalState.CFO_REVIEW: [ApprovalState.APPROVED, ApprovalState.REJECTED]
    }
)

# Execute with deterministic checkpointing
result = orchestrator.execute(invoice_data)
```

**See:** [Tutorial 2: Orchestration Patterns Overview](02_orchestration_patterns_overview.md#state-machine-orchestration) for state machine details.

---

## 4. Compliance and Auditability

### 4.1 GDPR PII Redaction

**Requirement:** Personal Identifiable Information (PII) must be redacted from logs and audit trails.

**PII in Financial Workflows:**
- **Customer names**: "John Smith purchased $500 item"
- **Email addresses**: "Receipt sent to john@example.com"
- **Phone numbers**: "Contact vendor at 555-1234"
- **Account numbers**: "Charge to account 1234-5678-9012-3456"

**Implementation:**

```python
import re
from typing import Any

class PIIRedactor:
    """Redact PII from financial workflow logs."""

    def __init__(self) -> None:
        """Initialize PII patterns."""
        self.email_pattern = re.compile(
            r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        )
        self.phone_pattern = re.compile(
            r'\b(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3,4}[-.\s]?\d{4}\b'
        )
        self.account_pattern = re.compile(
            r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b'
        )

    def redact(self, text: str) -> tuple[str, bool]:
        """Redact PII from text.

        Args:
            text: Input text that may contain PII

        Returns:
            Tuple of (redacted_text, pii_found)
        """
        pii_found = False
        redacted = text

        # Redact emails
        if self.email_pattern.search(redacted):
            redacted = self.email_pattern.sub("[EMAIL_REDACTED]", redacted)
            pii_found = True

        # Redact phone numbers
        if self.phone_pattern.search(redacted):
            redacted = self.phone_pattern.sub("[PHONE_REDACTED]", redacted)
            pii_found = True

        # Redact account numbers (preserve last 4 digits)
        def mask_account(match: re.Match[str]) -> str:
            full_number = match.group(0).replace("-", "").replace(" ", "")
            return f"****-****-****-{full_number[-4:]}"

        if self.account_pattern.search(redacted):
            redacted = self.account_pattern.sub(mask_account, redacted)
            pii_found = True

        return redacted, pii_found

# Integration with audit logger
from lesson_16.backend.reliability import AuditLogger

class GDPRCompliantAuditLogger(AuditLogger):
    """Audit logger with automatic PII redaction."""

    def __init__(self, log_dir: str, retention_days: int = 2555) -> None:
        super().__init__(log_dir, retention_days)
        self.redactor = PIIRedactor()

    def log_decision(
        self,
        workflow_id: str,
        agent_name: str,
        step: str,
        input_data: dict[str, Any],
        output_data: dict[str, Any],
        **kwargs: Any
    ) -> None:
        """Log decision with automatic PII redaction."""
        # Redact input and output data
        input_str = str(input_data)
        output_str = str(output_data)

        redacted_input, input_pii = self.redactor.redact(input_str)
        redacted_output, output_pii = self.redactor.redact(output_str)

        # Add PII detection metadata
        kwargs["pii_detected"] = input_pii or output_pii
        kwargs["redaction_applied"] = True

        # Log with redacted data
        super().log_decision(
            workflow_id=workflow_id,
            agent_name=agent_name,
            step=step,
            input_data={"redacted": redacted_input},
            output_data={"redacted": redacted_output},
            **kwargs
        )
```

**Example:**

```python
# Before redaction
log_entry = {
    "input": "Process invoice for john@example.com, account 1234-5678-9012-3456",
    "output": "Invoice approved, receipt sent to john@example.com"
}

# After redaction
redacted_entry = {
    "input": "Process invoice for [EMAIL_REDACTED], account ****-****-****-3456",
    "output": "Invoice approved, receipt sent to [EMAIL_REDACTED]",
    "pii_detected": True,
    "redaction_applied": True
}
```

**See:** [backend/reliability/audit_log.py](../backend/reliability/audit_log.py:120-156) for PII redaction implementation.

### 4.2 SOC2 Audit Log Requirements

**SOC2 Trust Service Criteria (TSC):**

| Criteria | Requirement | Implementation |
|----------|-------------|----------------|
| **CC6.1** | Logical access controls | Who made what decision |
| **CC7.2** | System monitoring | All agent decisions logged |
| **CC7.3** | Change management | Audit trail for workflow changes |
| **CC8.1** | Data retention | 7-year retention for financial data |

**Mandatory Log Fields:**

```python
from dataclasses import dataclass
from datetime import datetime

@dataclass
class SOC2AuditLogEntry:
    """SOC2-compliant audit log entry."""

    # CC6.1: Logical access controls
    workflow_id: str  # Unique identifier for traceability
    agent_name: str   # Which agent made the decision
    user_id: str      # Who initiated the workflow
    timestamp: datetime  # When the decision was made

    # CC7.2: System monitoring
    step: str         # What step in the workflow
    input_hash: str   # SHA-256 hash of input (for integrity)
    output: dict[str, Any]  # Decision output
    duration_ms: int  # Performance monitoring

    # CC7.3: Change management
    model_version: str  # LLM model used (e.g., "gpt-4-0613")
    temperature: float  # Model parameters
    validation_status: str  # "passed" or "failed"

    # CC8.1: Data retention
    retention_category: str  # "financial" = 7 years, "operational" = 1 year

    # Error tracking
    error: str | None = None
    error_type: str | None = None
```

**Audit Trail Query Examples:**

```python
# Query 1: "Who approved invoice INV-2023-001?"
audit_logs = logger.query(
    workflow_id="invoice_20231115_0001",
    step="approval"
)
# Result: user_id="manager@example.com", agent_name="ApprovalAgent", timestamp="2023-11-15 14:30:00"

# Query 2: "Show all decisions made by FraudDetectionAgent in the last 24 hours"
audit_logs = logger.query(
    agent_name="FraudDetectionAgent",
    start_time=datetime.now() - timedelta(days=1)
)

# Query 3: "What inputs led to this approval decision?"
audit_logs = logger.query(
    workflow_id="invoice_20231115_0001",
    step="approval"
)
input_hash = audit_logs[0]["input_hash"]
# Use input_hash to retrieve original input from secure storage
```

### 4.3 Retention Policies

**Legal Requirements:**

| Data Type | Retention Period | Justification |
|-----------|------------------|---------------|
| **Financial transactions** | 7 years | SOC2, IRS, GDPR |
| **Audit logs** | 7 years | SOC2 compliance |
| **Operational logs** | 1 year | System monitoring |
| **PII data** | 30 days after deletion request | GDPR Article 17 (Right to Erasure) |

**Implementation:**

```python
from datetime import datetime, timedelta
from pathlib import Path
import json

class RetentionPolicyManager:
    """Manage log retention policies."""

    def __init__(self, log_dir: Path) -> None:
        self.log_dir = log_dir
        self.policies = {
            "financial": timedelta(days=2555),  # 7 years
            "operational": timedelta(days=365),  # 1 year
            "gdpr_deletion": timedelta(days=30)  # 30 days
        }

    def enforce_retention(self) -> dict[str, int]:
        """Enforce retention policies and delete expired logs.

        Returns:
            Statistics: files_deleted, files_retained
        """
        stats = {"files_deleted": 0, "files_retained": 0}

        for log_file in self.log_dir.glob("*.jsonl"):
            # Read log file metadata
            with open(log_file) as f:
                first_line = f.readline()
                entry = json.loads(first_line)

                retention_category = entry.get("retention_category", "operational")
                timestamp = datetime.fromisoformat(entry["timestamp"])

                # Check if expired
                retention_period = self.policies[retention_category]
                age = datetime.now() - timestamp

                if age > retention_period:
                    log_file.unlink()  # Delete expired log
                    stats["files_deleted"] += 1
                else:
                    stats["files_retained"] += 1

        return stats

# Scheduled execution (e.g., daily cron job)
# 0 0 * * * python -m lesson_16.backend.reliability.retention_policy
```

**GDPR Right to Erasure:**

```python
def process_gdpr_deletion_request(user_id: str, logger: AuditLogger) -> None:
    """Process GDPR deletion request for user data.

    Args:
        user_id: User ID to delete (e.g., email address)
        logger: Audit logger instance
    """
    # Step 1: Mark user data for deletion
    deletion_request = {
        "user_id": user_id,
        "requested_at": datetime.now(),
        "status": "pending",
        "deletion_deadline": datetime.now() + timedelta(days=30)
    }
    logger.log_gdpr_deletion(deletion_request)

    # Step 2: Redact user PII from audit logs
    logger.redact_user_pii(user_id)

    # Step 3: After 30 days, permanently delete
    # (Implemented via scheduled job checking deletion_deadline)
```

---

## 5. Domain-Specific Challenges in Financial Workflows

### 5.1 Invoice Processing: OCR Error Handling

**Challenge:** OCR engines misread invoice text, causing amount/vendor errors.

**Common OCR Errors:**

| Actual Text | OCR Output | Error Type |
|-------------|------------|------------|
| $1,050.00 | $10,050.00 | Extra digit |
| ACME Corp | ACM€ Corp | Special character misread |
| Invoice Date: 11/15/2023 | Invoice Date: 11/15/2O23 | Letter 'O' instead of zero |
| Account: 5001 | Account: 50O1 | Letter 'O' instead of zero |

**Mitigation Strategy 1: Database Cross-Validation**

```python
def validate_invoice_with_po(
    invoice_amount: float,
    vendor_id: str,
    invoice_number: str,
    erp_client: ERPClient
) -> dict[str, Any]:
    """Validate invoice against purchase order (PO).

    Args:
        invoice_amount: Amount extracted from OCR
        vendor_id: Vendor ID from ERP lookup
        invoice_number: Invoice number from OCR
        erp_client: ERP system client

    Returns:
        Validation result with discrepancy details

    Raises:
        ValueError: If discrepancy exceeds threshold
    """
    # Lookup purchase order
    po = erp_client.lookup_po_by_invoice(vendor_id, invoice_number)

    if not po:
        return {
            "validation_status": "warning",
            "message": "No matching PO found, manual review required"
        }

    # Check amount discrepancy
    po_amount = po["total_amount"]
    discrepancy = abs(invoice_amount - po_amount)
    discrepancy_pct = (discrepancy / po_amount) * 100

    # Tolerance: 1% or $10 (whichever is larger)
    tolerance = max(po_amount * 0.01, 10.0)

    if discrepancy > tolerance:
        raise ValueError(
            f"Invoice amount ${invoice_amount:,.2f} differs from PO amount "
            f"${po_amount:,.2f} by ${discrepancy:,.2f} ({discrepancy_pct:.1f}%). "
            f"Tolerance: ${tolerance:,.2f}"
        )

    return {
        "validation_status": "passed",
        "po_number": po["po_number"],
        "po_amount": po_amount,
        "discrepancy": discrepancy
    }
```

**Mitigation Strategy 2: Regex Validation for Common Patterns**

```python
import re

def validate_invoice_number_format(invoice_number: str, vendor_id: str) -> bool:
    """Validate invoice number matches vendor's expected format.

    Args:
        invoice_number: Invoice number from OCR
        vendor_id: Vendor ID from ERP

    Returns:
        True if format valid, False otherwise
    """
    # Vendor-specific invoice formats (from ERP configuration)
    vendor_formats = {
        "V12345": r"^INV-\d{6}$",  # ACME Corp: INV-123456
        "V67890": r"^[A-Z]{2}\d{8}$"  # Vendor2: AB12345678
    }

    pattern = vendor_formats.get(vendor_id)
    if not pattern:
        return True  # No format validation available

    return bool(re.match(pattern, invoice_number))
```

**Example Dataset (from data/invoices_100.json):**

```json
{
  "invoice_id": "INV-001",
  "vendor_name": "ACME Corp",
  "invoice_amount": 1050.00,
  "ocr_text": "Invoice from ACM€ Corp\nAmount: $10,050.00\nDate: 11/15/2O23",
  "challenges": ["ocr_error_amount", "ocr_error_vendor", "ocr_error_date"],
  "gold_label": {
    "vendor_name": "ACME Corp",
    "invoice_amount": 1050.00,
    "invoice_date": "2023-11-15"
  }
}
```

**See:** [data/invoices_100.json](../data/invoices_100.json) (created in Task 6.2).

### 5.2 Fraud Detection: Class Imbalance Handling

**Challenge:** Fraud is rare (1-5% of transactions), causing model bias toward "legitimate" predictions.

**Impact:**
- **High false negative rate**: Agent misses actual fraud (costly)
- **Agent confidence calibration**: 95% confidence on all "legitimate" predictions

**Class Distribution in Dataset:**

```
Legitimate transactions: 90% (90 out of 100)
Fraudulent transactions: 10% (10 out of 100)
```

**Mitigation Strategy 1: Confidence Thresholding**

```python
def classify_fraud_with_threshold(
    transaction: dict[str, Any],
    agent: FraudDetectionAgent,
    confidence_threshold: float = 0.7
) -> dict[str, Any]:
    """Classify fraud with confidence thresholding.

    Args:
        transaction: Transaction data
        agent: Fraud detection agent
        confidence_threshold: Minimum confidence for fraud classification

    Returns:
        Classification result with confidence score
    """
    # Agent predicts fraud probability
    prediction = agent.predict(transaction)

    fraud_probability = prediction["fraud_probability"]

    # Apply threshold
    if fraud_probability >= confidence_threshold:
        classification = "FRAUD"
    elif fraud_probability <= (1 - confidence_threshold):
        classification = "LEGITIMATE"
    else:
        classification = "MANUAL_REVIEW"  # Low confidence

    return {
        "classification": classification,
        "fraud_probability": fraud_probability,
        "confidence": max(fraud_probability, 1 - fraud_probability)
    }
```

**Mitigation Strategy 2: High-Value Transaction Escalation**

```python
def escalate_high_value_transactions(
    transaction: dict[str, Any],
    classification: dict[str, Any],
    amount_threshold: float = 10000.0
) -> dict[str, Any]:
    """Escalate high-value transactions to voting ensemble.

    Args:
        transaction: Transaction data
        classification: Initial classification result
        amount_threshold: Amount threshold for escalation (USD)

    Returns:
        Escalation decision
    """
    amount = transaction["amount"]

    # High-value transactions require consensus
    if amount >= amount_threshold:
        return {
            "escalated": True,
            "reason": f"Amount ${amount:,.2f} >= ${amount_threshold:,.2f}",
            "next_step": "voting_ensemble"
        }

    # Ambiguous predictions require manual review
    if classification["classification"] == "MANUAL_REVIEW":
        return {
            "escalated": True,
            "reason": f"Low confidence ({classification['confidence']:.2f})",
            "next_step": "manual_review_queue"
        }

    return {"escalated": False}
```

**Example Dataset (from data/transactions_100.json):**

```json
{
  "transaction_id": "TXN-00001",
  "amount": 15000.00,
  "merchant": "Electronics Store",
  "user_behavior": {
    "avg_transaction_amount": 200.00,
    "transactions_last_24h": 1
  },
  "fraud_label": "FRAUD",
  "fraud_type": "stolen_card",
  "challenges": ["high_value", "imbalance", "ambiguous_pattern"],
  "gold_label": {
    "fraud": true,
    "confidence": 0.85,
    "reason": "Amount 75× higher than user average"
  }
}
```

**See:** [data/transactions_100.json](../data/transactions_100.json) (created in Task 6.3).

### 5.3 Reconciliation: Date Mismatch Resolution

**Challenge:** Bank transaction dates ≠ ledger posting dates (1-3 business days difference).

**Example:**

```
Bank Transaction: 2023-11-13 | Amount: $1,234.56 | Merchant: Office Depot
Ledger Entry:     2023-11-15 | Amount: $1,234.56 | Vendor: Office Depot Inc.

Challenge: Same transaction, different dates and vendor name spelling
```

**Mitigation Strategy 1: Fuzzy Date Matching**

```python
from datetime import datetime, timedelta

def fuzzy_match_dates(
    bank_date: datetime,
    ledger_date: datetime,
    tolerance_days: int = 3
) -> dict[str, Any]:
    """Fuzzy match transaction dates with tolerance.

    Args:
        bank_date: Transaction date from bank statement
        ledger_date: Posting date from ledger
        tolerance_days: Maximum date difference in business days

    Returns:
        Match result with date difference
    """
    date_diff = abs((ledger_date - bank_date).days)

    if date_diff == 0:
        return {
            "match": "exact",
            "date_diff_days": 0,
            "confidence": 1.0
        }
    elif date_diff <= tolerance_days:
        return {
            "match": "fuzzy",
            "date_diff_days": date_diff,
            "confidence": 1.0 - (date_diff / tolerance_days) * 0.3  # 0.7-1.0
        }
    else:
        return {
            "match": "no_match",
            "date_diff_days": date_diff,
            "confidence": 0.0
        }
```

**Mitigation Strategy 2: Multi-Field Matching**

```python
from difflib import SequenceMatcher

def match_bank_to_ledger(
    bank_transaction: dict[str, Any],
    ledger_entry: dict[str, Any]
) -> dict[str, Any]:
    """Match bank transaction to ledger entry using multiple fields.

    Args:
        bank_transaction: Transaction from bank statement
        ledger_entry: Entry from accounting ledger

    Returns:
        Match result with confidence score
    """
    # Field 1: Amount (exact match required)
    amount_match = abs(bank_transaction["amount"] - ledger_entry["amount"]) < 0.01

    # Field 2: Merchant/Vendor (fuzzy string match)
    merchant_similarity = SequenceMatcher(
        None,
        bank_transaction["merchant"].lower(),
        ledger_entry["vendor"].lower()
    ).ratio()

    # Field 3: Date (fuzzy match within 3 days)
    date_match = fuzzy_match_dates(
        bank_transaction["date"],
        ledger_entry["date"],
        tolerance_days=3
    )

    # Combined confidence score
    if amount_match and merchant_similarity >= 0.8 and date_match["match"] in ["exact", "fuzzy"]:
        confidence = min(
            1.0,
            merchant_similarity * 0.5 + date_match["confidence"] * 0.5
        )
        return {
            "match": True,
            "confidence": confidence,
            "reconciliation_status": "matched",
            "details": {
                "amount_match": amount_match,
                "merchant_similarity": merchant_similarity,
                "date_match": date_match
            }
        }
    else:
        return {
            "match": False,
            "confidence": 0.0,
            "reconciliation_status": "manual_review",
            "reason": "Insufficient field matches"
        }
```

**Example Dataset (from data/reconciliation_100.json):**

```json
{
  "reconciliation_id": "RECON-001",
  "bank_transaction": {
    "date": "2023-11-13",
    "amount": 1234.56,
    "merchant": "Office Depot"
  },
  "ledger_entry": {
    "date": "2023-11-15",
    "amount": 1234.56,
    "vendor": "Office Depot Inc."
  },
  "challenges": ["date_mismatch_2_days", "vendor_name_variation"],
  "expected_match": true,
  "gold_label": {
    "reconciliation_status": "matched",
    "confidence": 0.92,
    "date_diff_days": 2,
    "merchant_similarity": 0.88
  }
}
```

**See:** [data/reconciliation_100.json](../data/reconciliation_100.json) (created in Task 6.4).

---

## 6. Production Deployment Patterns

### 6.1 Cost Optimization for Financial Agents

**Problem:** Financial workflows process thousands of transactions daily → high LLM API costs.

**Strategy 1: Model Cascades (GPT-3.5 Screening → GPT-4 Escalation)**

```python
def cascade_fraud_detection(
    transaction: dict[str, Any],
    screening_model: str = "gpt-3.5-turbo",
    escalation_model: str = "gpt-4"
) -> dict[str, Any]:
    """Use model cascade to reduce costs.

    Args:
        transaction: Transaction data
        screening_model: Fast, cheap model for initial screening
        escalation_model: Accurate, expensive model for complex cases

    Returns:
        Classification result with cost tracking
    """
    cost_tracker = {"screening_cost": 0.0, "escalation_cost": 0.0}

    # Step 1: Cheap model screens transaction
    screening_result = llm_classify(transaction, model=screening_model)
    cost_tracker["screening_cost"] = 0.002  # GPT-3.5: $0.002 per call

    # Step 2: If high confidence, accept screening result
    if screening_result["confidence"] >= 0.9:
        return {
            "classification": screening_result["classification"],
            "confidence": screening_result["confidence"],
            "model_used": screening_model,
            "total_cost": cost_tracker["screening_cost"]
        }

    # Step 3: Low confidence → escalate to expensive model
    escalation_result = llm_classify(transaction, model=escalation_model)
    cost_tracker["escalation_cost"] = 0.03  # GPT-4: $0.03 per call

    return {
        "classification": escalation_result["classification"],
        "confidence": escalation_result["confidence"],
        "model_used": escalation_model,
        "escalated": True,
        "total_cost": cost_tracker["screening_cost"] + cost_tracker["escalation_cost"]
    }
```

**Cost Savings:**

```
Without Cascade:
- 1000 transactions × GPT-4 ($0.03) = $30.00

With Cascade (70% high confidence in GPT-3.5):
- 700 transactions × GPT-3.5 ($0.002) = $1.40
- 300 transactions × (GPT-3.5 + GPT-4) = $9.60
- Total: $11.00
- Savings: 63% cost reduction
```

**Strategy 2: Redis Caching for Duplicate Queries**

```python
import redis
import hashlib
import json

class CachedFraudDetector:
    """Fraud detector with Redis caching."""

    def __init__(self, redis_client: redis.Redis, ttl: int = 86400) -> None:
        """Initialize with Redis client.

        Args:
            redis_client: Redis client instance
            ttl: Cache TTL in seconds (default: 24 hours)
        """
        self.redis = redis_client
        self.ttl = ttl

    def get_cache_key(self, transaction: dict[str, Any]) -> str:
        """Generate cache key from transaction data."""
        # Use deterministic fields only (exclude timestamp)
        cache_input = {
            "amount": transaction["amount"],
            "merchant": transaction["merchant"],
            "user_id": transaction["user_id"]
        }
        return hashlib.sha256(
            json.dumps(cache_input, sort_keys=True).encode()
        ).hexdigest()

    def classify(self, transaction: dict[str, Any]) -> dict[str, Any]:
        """Classify transaction with caching."""
        cache_key = self.get_cache_key(transaction)

        # Check cache
        cached_result = self.redis.get(cache_key)
        if cached_result:
            result = json.loads(cached_result)
            result["cache_hit"] = True
            return result

        # Cache miss → call LLM
        result = llm_classify(transaction)
        result["cache_hit"] = False

        # Store in cache
        self.redis.setex(cache_key, self.ttl, json.dumps(result))

        return result
```

**Cache Hit Rate Impact:**

```
Assumptions:
- 1000 transactions/day
- 40% are duplicate queries (same merchant, same amount)
- Cache TTL: 24 hours

With Caching:
- 600 LLM calls (60% cache miss)
- 400 cache hits (no LLM cost)
- Cost: 600 × $0.002 = $1.20
- Savings: 40% cost reduction
```

**See:** [Tutorial 7: Production Deployment Considerations](07_production_deployment_considerations.md) for comprehensive cost optimization strategies.

### 6.2 Error Rate Monitoring

**Requirement:** Monitor error rates and alert when thresholds exceeded.

**Implementation:**

```python
from collections import deque
from datetime import datetime

class ErrorRateMonitor:
    """Monitor agent error rates with rolling window."""

    def __init__(
        self,
        window_size: int = 100,
        alert_threshold: float = 0.05  # 5% error rate
    ) -> None:
        """Initialize monitor.

        Args:
            window_size: Number of recent tasks to track
            alert_threshold: Error rate threshold for alerts (0.0-1.0)
        """
        self.window_size = window_size
        self.alert_threshold = alert_threshold
        self.results = deque(maxlen=window_size)

    def record_result(self, success: bool, task_type: str) -> dict[str, Any]:
        """Record task result and check for alerts.

        Args:
            success: Whether task succeeded
            task_type: Type of task (invoice, fraud, reconciliation)

        Returns:
            Alert status and statistics
        """
        self.results.append({
            "success": success,
            "task_type": task_type,
            "timestamp": datetime.now()
        })

        # Calculate error rate
        total_tasks = len(self.results)
        errors = sum(1 for r in self.results if not r["success"])
        error_rate = errors / total_tasks if total_tasks > 0 else 0.0

        # Check alert threshold
        alert = error_rate > self.alert_threshold

        return {
            "alert": alert,
            "error_rate": error_rate,
            "total_tasks": total_tasks,
            "errors": errors,
            "window_size": self.window_size,
            "threshold": self.alert_threshold
        }

# Usage
monitor = ErrorRateMonitor(window_size=100, alert_threshold=0.05)

for task in tasks:
    result = process_task(task)
    status = monitor.record_result(result["success"], task["type"])

    if status["alert"]:
        send_alert(
            f"Error rate {status['error_rate']:.1%} exceeds threshold "
            f"{status['threshold']:.1%} in last {status['window_size']} tasks"
        )
```

**Task-Specific Error Targets (from OQ4 in PRD):**

| Task Type | Error Rate Target | Justification |
|-----------|-------------------|---------------|
| **Invoice Processing** | <5% | High accuracy for payment amounts |
| **Fraud Detection** | <10% | Class imbalance, ambiguous patterns |
| **Reconciliation** | <8% | Date mismatches, fuzzy matching |

---

## 7. Practical Exercises

### Exercise 1: Design Compliance Logging for Your Use Case

**Scenario:** You're building an agent that processes employee expense reports.

**Requirements:**
1. GDPR PII redaction (employee names, emails)
2. SOC2 audit trail (who approved, when, what amount)
3. 7-year retention for expenses >$1000, 1-year for others

**Tasks:**
1. Define the `ExpenseReportAuditLogEntry` dataclass with mandatory fields
2. Implement PII redaction for employee names and emails
3. Write a retention policy function that determines retention period based on expense amount
4. Create a query function to answer: "Who approved expenses >$5000 in Q4 2023?"

**Solution Template:**

```python
from dataclasses import dataclass
from datetime import datetime
import re

@dataclass
class ExpenseReportAuditLogEntry:
    # TODO: Add SOC2 mandatory fields
    workflow_id: str
    # ... (complete this)

class ExpensePIIRedactor:
    # TODO: Implement PII redaction for employee data
    pass

def determine_retention_period(expense_amount: float) -> int:
    # TODO: Return retention days based on amount
    pass
```

**Expected Output:**

```python
# Example log entry
entry = ExpenseReportAuditLogEntry(
    workflow_id="expense_2023_Q4_001",
    employee_id="EMP123",  # Not PII (ID, not name)
    approver_email="[EMAIL_REDACTED]",  # Redacted
    expense_amount=5500.00,
    timestamp=datetime(2023, 12, 15, 10, 30),
    retention_days=2555  # 7 years (amount >$1000)
)
```

### Exercise 2: Implement PII Redaction with Whitelisting

**Scenario:** Your financial agent logs transaction data that includes:
- Customer names (PII, should redact)
- Merchant names (NOT PII, should preserve)
- Account numbers (PII, should mask last 4 digits)

**Requirements:**
1. Redact customer names but preserve merchant names
2. Use a whitelist of known merchant names (e.g., "Amazon", "Walmart", "Target")
3. Mask account numbers showing only last 4 digits

**Tasks:**
1. Implement `WhitelistedPIIRedactor` class with merchant whitelist
2. Write tests for: customer name redacted, merchant name preserved, account masked
3. Handle edge case: "John's Hardware" (contains name "John" but is a merchant)

**Solution Template:**

```python
class WhitelistedPIIRedactor:
    def __init__(self, merchant_whitelist: list[str]) -> None:
        self.merchant_whitelist = set(merchant_whitelist)
        # TODO: Implement name and account patterns

    def redact(self, text: str) -> tuple[str, bool]:
        # TODO: Redact PII while preserving whitelisted merchants
        pass
```

**Test Cases:**

```python
redactor = WhitelistedPIIRedactor(
    merchant_whitelist=["Amazon", "Walmart", "John's Hardware"]
)

# Test 1: Customer name redacted, merchant preserved
text1 = "John Smith purchased from Amazon, account 1234-5678-9012-3456"
result1, pii_found1 = redactor.redact(text1)
# Expected: "[NAME_REDACTED] purchased from Amazon, account ****-****-****-3456"

# Test 2: Merchant name preserved even though it contains "John"
text2 = "Purchase at John's Hardware, account 9876-5432-1098-7654"
result2, pii_found2 = redactor.redact(text2)
# Expected: "Purchase at John's Hardware, account ****-****-****-7654"
```

### Exercise 3: Calculate Cost Savings from Model Cascades

**Scenario:** Your fraud detection system processes 5000 transactions/day.

**Current Setup:**
- All transactions use GPT-4 ($0.03 per call)
- Daily cost: 5000 × $0.03 = $150

**Proposed Cascade:**
- GPT-3.5 screening ($0.002 per call)
- If confidence <0.9, escalate to GPT-4 ($0.03 per call)
- Historical data shows 60% of transactions have GPT-3.5 confidence ≥0.9

**Tasks:**
1. Calculate daily cost with cascade strategy
2. Calculate monthly savings (30 days)
3. What if escalation rate is 50% instead of 40%? Recalculate savings.
4. At what escalation rate does the cascade strategy break even (same cost as GPT-4 only)?

**Solution Template:**

```python
def calculate_cascade_cost(
    transactions_per_day: int,
    screening_cost: float,
    escalation_cost: float,
    escalation_rate: float
) -> dict[str, float]:
    """Calculate daily cost with model cascade.

    Args:
        transactions_per_day: Number of transactions
        screening_cost: Cost per screening call (GPT-3.5)
        escalation_cost: Cost per escalation call (GPT-4)
        escalation_rate: Fraction of transactions escalated (0.0-1.0)

    Returns:
        Cost breakdown and savings
    """
    # TODO: Implement calculation
    pass

# Test
result = calculate_cascade_cost(
    transactions_per_day=5000,
    screening_cost=0.002,
    escalation_cost=0.03,
    escalation_rate=0.4
)
print(f"Daily cost: ${result['daily_cost']:.2f}")
print(f"Monthly savings: ${result['monthly_savings']:.2f}")
```

**Expected Output:**

```
Daily cost: $70.00
Monthly savings: $2,400.00
Break-even escalation rate: 93.3%
```

---

## 8. Summary

### Key Takeaways

1. **Financial workflows require ERP integration guardrails**
   - Database validation prevents hallucinations (vendor lookup, cost center verification)
   - Deterministic business rules for critical decisions (approval routing, payment terms)
   - Complete audit trail for compliance and debugging

2. **Compliance is non-negotiable**
   - GDPR PII redaction: Preserve business context, redact personal identifiers
   - SOC2 audit logs: Track who/what/when for all decisions
   - Retention policies: 7 years for financial data, 1 year for operational logs

3. **Domain-specific challenges require custom solutions**
   - Invoice OCR errors: Cross-validate with purchase orders
   - Fraud imbalance: Confidence thresholding, high-value escalation
   - Reconciliation date mismatches: Fuzzy date matching within 3-day window

4. **Production deployment balances cost, accuracy, and compliance**
   - Model cascades: 60%+ cost reduction (GPT-3.5 screening → GPT-4 escalation)
   - Redis caching: 40% cost reduction (24-hour TTL)
   - Error rate monitoring: Alert when >5% failure in rolling 100-task window

### Next Steps

1. **Explore Backend Implementation:**
   - [backend/reliability/audit_log.py](../backend/reliability/audit_log.py) - PII redaction, SOC2 logging
   - [backend/orchestrators/state_machine.py](../backend/orchestrators/state_machine.py) - Approval workflows

2. **Study Interactive Notebooks:**
   - Notebook 08: Sequential Invoice Processing (Task 5.2)
   - Notebook 09: Hierarchical Fraud Detection (Task 5.3)
   - Notebook 15: Production Deployment with Cost Optimization (Task 5.9)

3. **Deep Dive into Advanced Topics:**
   - [Tutorial 7: Production Deployment Considerations](07_production_deployment_considerations.md) - Cost optimization, latency SLAs, observability
   - [Tutorial 4: Error Propagation Analysis](04_error_propagation_analysis.md) - Error isolation in financial workflows

4. **Review Case Studies:**
   - FinRobot paper: [arXiv:2401.00910](https://arxiv.org/abs/2401.00910)
   - AgentArch benchmark: [Tutorial 5: AgentArch Benchmark Methodology](05_agentarch_benchmark_methodology.md)

---

## Common Pitfalls and Troubleshooting

### Pitfall 1: Using LLMs for Business Logic

**Problem:**

```python
# ❌ BAD: LLM calculates payment due date
prompt = f"Invoice date: {invoice_date}. Terms: NET30. When is payment due?"
due_date = llm.generate(prompt)  # Non-deterministic!
```

**Solution:**

```python
# ✅ GOOD: Deterministic business logic
due_date = invoice_date + timedelta(days=30)
```

**Why:** Business rules must be deterministic for auditability and consistency.

### Pitfall 2: Incomplete Audit Trails

**Problem:**

```python
# ❌ BAD: Missing critical metadata
audit_log = {
    "workflow_id": "invoice_001",
    "result": "approved"
}
```

**Solution:**

```python
# ✅ GOOD: Complete SOC2-compliant log
audit_log = {
    "workflow_id": "invoice_001",
    "agent_name": "ApprovalAgent",
    "user_id": "manager@example.com",
    "timestamp": datetime.now(),
    "input_hash": sha256(input_data),
    "output": {"decision": "approved", "amount": 5000.00},
    "model_version": "gpt-4-0613",
    "validation_status": "passed"
}
```

**Why:** SOC2 requires who/what/when/how for all decisions.

### Pitfall 3: Ignoring OCR Error Rates

**Problem:**

```python
# ❌ BAD: Trust OCR output directly
invoice_amount = ocr_extract_amount(invoice_image)
process_payment(invoice_amount)  # What if OCR misread?
```

**Solution:**

```python
# ✅ GOOD: Cross-validate with purchase order
invoice_amount = ocr_extract_amount(invoice_image)
validate_invoice_with_po(invoice_amount, vendor_id, erp_client)  # Raises ValueError if discrepancy
process_payment(invoice_amount)
```

**Why:** OCR errors can cause significant financial losses (10× amount errors common).

### Pitfall 4: Hardcoding Retention Policies

**Problem:**

```python
# ❌ BAD: Hardcoded retention
def delete_old_logs():
    for log in logs:
        if log.age > 365:  # Always 1 year
            delete(log)
```

**Solution:**

```python
# ✅ GOOD: Category-based retention
def delete_old_logs():
    for log in logs:
        retention_days = RETENTION_POLICIES[log.category]
        if log.age > retention_days:
            delete(log)
```

**Why:** Financial logs require 7 years (SOC2), operational logs only 1 year.

---

## FAQ

**Q1: How do I choose between database validation and LLM judgment?**

**A:** Use this decision tree:
- **Critical for compliance/financial impact?** → Database validation (deterministic)
- **Requires reasoning or ambiguity handling?** → LLM judgment with validation fallback
- **Example:** Vendor lookup = database, fraud suspicion scoring = LLM

---

**Q2: What's the difference between GDPR and SOC2 for audit logging?**

**A:**
- **GDPR (Privacy):** Redact PII, support deletion requests, 30-day response to erasure
- **SOC2 (Security):** Complete audit trail, 7-year retention, access controls
- **Both required:** Redact PII in SOC2 logs to satisfy GDPR

---

**Q3: How do I handle PII in error messages?**

**A:** Apply redaction before logging errors:

```python
try:
    process_invoice(customer_email="john@example.com")
except ValueError as e:
    error_message = str(e)
    redacted_error, _ = redactor.redact(error_message)
    logger.error(redacted_error)  # Logs "[EMAIL_REDACTED]" instead of "john@example.com"
```

---

**Q4: Should I use model cascades for all financial workflows?**

**A:** No, only for high-volume, low-stakes tasks:
- **Use cascades:** Fraud screening (5000 txns/day, 60% obvious cases)
- **Skip cascades:** CFO approval (10 txns/day, high stakes) → Always use GPT-4

---

**Q5: How do I test ERP integration in development?**

**A:** Use mock ERP client with fixture data:

```python
class MockERPClient:
    def __init__(self):
        self.vendors = {
            "V12345": {"vendor_id": "V12345", "canonical_name": "ACME Corp", "status": "ACTIVE"}
        }

    def lookup_vendor(self, vendor_name: str):
        # Fuzzy match against fixture data
        for vendor in self.vendors.values():
            if vendor["canonical_name"].lower() in vendor_name.lower():
                return vendor
        return None

# In tests
erp_client = MockERPClient()
result = validate_vendor("ACME", erp_client)
assert result["vendor_id"] == "V12345"
```

---

## Related Tutorials

### Prerequisites
- [Tutorial 1: Agent Reliability Fundamentals](01_agent_reliability_fundamentals.md) - 5 failure modes
- [Tutorial 3: Deterministic Execution Strategies](03_deterministic_execution_strategies.md) - Pydantic validation
- [Tutorial 4: Error Propagation Analysis](04_error_propagation_analysis.md) - Error isolation

### Next Steps
- [Tutorial 7: Production Deployment Considerations](07_production_deployment_considerations.md) - Cost optimization, monitoring
- Notebook 13: Reliability Framework Implementation (Task 5.7) - All 7 components integrated
- Notebook 15: Production Deployment Tutorial (Task 5.9) - Cost tracking, error monitoring, compliance

### Related Resources
- [backend/reliability/audit_log.py](../backend/reliability/audit_log.py) - Audit logging implementation
- [data/invoices_100.json](../data/invoices_100.json) - Invoice dataset with OCR challenges
- [data/transactions_100.json](../data/transactions_100.json) - Fraud detection dataset
- [data/reconciliation_100.json](../data/reconciliation_100.json) - Reconciliation dataset

---

**Reading Time:** 22 minutes | **Exercises:** 3 hands-on activities | **Difficulty:** Intermediate

---

**Navigation:**
- **← Previous:** [Tutorial 05: AgentArch Benchmark Methodology](05_agentarch_benchmark_methodology.md)
- **↑ Index:** [Tutorial Index](../TUTORIAL_INDEX.md)
- **→ Next:** [Tutorial 07: Production Deployment Considerations](07_production_deployment_considerations.md)

---

**Feedback:**
Found an issue or have suggestions? [Open an issue](https://github.com/anthropics/claude-code/issues) or contribute improvements!

**Last Updated:** 2025-11-23
**Version:** 1.0
**Lesson:** Lesson 16 - Agent Reliability

**Feedback:** Found an error or have suggestions? Open an issue in the course repository.
