# Quick-Start: HITLController

**Time to Complete:** ~15 minutes
**Difficulty:** Beginner
**Prerequisites:** Basic Python knowledge, understanding of regulatory compliance concepts

---

## Learning Objectives

By the end of this tutorial, you will be able to:

1. Understand the three-tier oversight model for AI systems
2. Configure HITLController with appropriate thresholds
3. Determine when human review is required
4. Implement the human review workflow
5. Meet regulatory compliance requirements (SR 11-7, EU AI Act)

---

## Why Human-in-the-Loop Matters

Financial regulations require human oversight for high-risk AI decisions:

| Regulation | Requirement |
|------------|-------------|
| **Federal Reserve SR 11-7** | Evaluation, monitoring, outcomes analysis for AI/ML models |
| **EU AI Act Article 14** | Human oversight capabilities for high-risk AI systems |
| **FFIEC Guidance** | Effective challenge and independent review of model outputs |

HITLController implements the **Sardine AI tiered oversight model**:

```
                    ┌───────────────┐
                    │   AI Decision │
                    └───────┬───────┘
                            │
            ┌───────────────┼───────────────┐
            │               │               │
            ▼               ▼               ▼
    ┌───────────────┐ ┌───────────────┐ ┌───────────────┐
    │   TIER 1      │ │   TIER 2      │ │   TIER 3      │
    │  Full HITL    │ │ Sample-based  │ │  Logged Only  │
    │  (Required)   │ │   (10%)       │ │   (Audit)     │
    └───────────────┘ └───────────────┘ └───────────────┘
         SAR            Fraud Triage      Knowledge Search
         Block Payment  High-Value        Status Lookup
         Close Account  Low Confidence    FAQ Response
```

---

## 5-Minute Setup

### Step 1: Import the Module

```python
from closing_the_gaps.governance import (
    HITLController,
    OversightTier,
    InterruptDecision,
)
```

### Step 2: Initialize with Your Thresholds

```python
# Basic initialization (uses defaults)
controller = HITLController()

# Or with custom thresholds
controller = HITLController(
    confidence_threshold=0.85,  # Below this → interrupt
    amount_threshold=10000.0,   # Above this → interrupt
    default_tier=OversightTier.TIER_2_MEDIUM,
    log_to_db=True,
)
```

### Step 3: Check If Interrupt Needed

```python
decision = controller.should_interrupt(
    confidence=0.72,
    amount=15000,
    dispute_type="fraud"
)

if decision.should_interrupt:
    print(f"Human review required: {decision.reason}")
```

---

## Understanding the Three Tiers

### Tier 1: Full Human Review (Always Required)

Actions that **always** require human approval:

```python
# These actions ALWAYS trigger Tier 1
tier_1_actions = [
    "sar_filing",      # Suspicious Activity Report
    "payment_block",   # Block a payment
    "account_close",   # Recommend account closure
]

controller = HITLController()

# Even with 99% confidence, SAR filing requires human
decision = controller.should_interrupt(
    confidence=0.99,
    amount=100.0,
    dispute_type="general",
    action_type="sar_filing"
)

assert decision.should_interrupt is True
assert decision.tier == OversightTier.TIER_1_HIGH
print(f"Reason: {decision.reason}")
# "Tier 1 action (sar_filing) requires human approval"
```

### Tier 2: Conditional Review (Based on Risk Factors)

Review triggered by:
- Confidence below threshold (default: 0.85)
- Amount above threshold (default: $10,000)
- High-risk dispute types (fraud, identity theft)

```python
controller = HITLController(
    confidence_threshold=0.85,
    amount_threshold=10000.0
)

# Low confidence triggers review
decision = controller.should_interrupt(
    confidence=0.72,  # Below 0.85
    amount=500.0,
    dispute_type="billing_error"
)
assert decision.should_interrupt is True
assert decision.tier == OversightTier.TIER_2_MEDIUM
print(f"Reason: {decision.reason}")
# "Confidence 0.72 below threshold 0.85"

# High amount triggers review
decision = controller.should_interrupt(
    confidence=0.92,  # Above threshold
    amount=15000.0,   # Above $10,000
    dispute_type="billing_error"
)
assert decision.should_interrupt is True
print(f"Reason: {decision.reason}")
# "Amount $15,000.00 exceeds threshold $10,000.00"
```

### Tier 3: Logged Only (No Interrupt)

Low-risk actions that are logged but don't interrupt:

```python
controller = HITLController()

# Info lookup - no interrupt needed
decision = controller.should_interrupt(
    confidence=0.95,
    amount=None,
    dispute_type="general",
    action_type="info_lookup"
)
assert decision.should_interrupt is False
assert decision.tier == OversightTier.TIER_3_LOW

# Low-value, high-confidence billing error
decision = controller.should_interrupt(
    confidence=0.95,
    amount=50.0,
    dispute_type="billing_error"
)
assert decision.should_interrupt is False
assert decision.tier == OversightTier.TIER_3_LOW
```

---

## Tier Classification Matrix

| Action Type | Dispute Type | Amount | Confidence | Tier | Interrupt? |
|-------------|--------------|--------|------------|------|------------|
| `sar_filing` | * | * | * | **TIER 1** | ✅ Always |
| `payment_block` | * | * | * | **TIER 1** | ✅ Always |
| `account_close` | * | * | * | **TIER 1** | ✅ Always |
| `refund_approve` | fraud | >$10K | <0.85 | **TIER 1** | ✅ Yes |
| `refund_approve` | fraud | >$10K | ≥0.85 | **TIER 2** | ✅ Yes |
| `refund_approve` | billing_error | ≤$10K | ≥0.85 | **TIER 3** | ❌ No |
| `info_lookup` | * | * | * | **TIER 3** | ❌ No |

---

## Human Review Workflow

### Step 1: Get Interrupt Decision

```python
decision = controller.should_interrupt(
    confidence=0.72,
    amount=15000.0,
    dispute_type="fraud"
)

if not decision.should_interrupt:
    # Proceed with automated processing
    process_automatically(dispute)
    return
```

### Step 2: Request Human Review

```python
# Prepare context for reviewer
context = {
    "dispute_id": "DSP-12345",
    "customer_id": "CUST-001",
    "transaction": {
        "amount": 15000.0,
        "merchant": "Suspicious Merchant Inc.",
        "date": "2024-12-01",
        "location": "Unknown Country",
    },
    "ai_analysis": {
        "fraud_score": 0.72,
        "risk_factors": ["unusual_location", "high_amount"],
        "recommendation": "Review before approval",
    },
}

review_id = controller.request_human_review(decision, context)
print(f"Review requested: {review_id}")
```

### Step 3: Wait for Human Decision

```python
# In production, this would be handled by a review queue/UI
# The agent workflow pauses here until human responds

# When human reviews...
```

### Step 4: Record Human Decision

```python
# Human approves
controller.record_human_decision(
    review_id=review_id,
    approved=True,
    reviewer_id="REVIEWER-001",
    notes="Verified with customer via phone. Transaction legitimate."
)

# Or human rejects
controller.record_human_decision(
    review_id=review_id,
    approved=False,
    reviewer_id="REVIEWER-001",
    notes="Confirmed fraudulent. Block transaction and notify customer."
)
```

---

## Complete Example

```python
from closing_the_gaps.governance import HITLController, OversightTier

def process_dispute(dispute: dict) -> str:
    """Process dispute with HITL oversight."""
    controller = HITLController()

    # Step 1: Check if human review needed
    decision = controller.should_interrupt(
        confidence=dispute["ai_confidence"],
        amount=dispute["amount"],
        dispute_type=dispute["type"],
        action_type=dispute.get("action"),
    )

    # Step 2: Log the decision (always happens)
    print(f"Tier: {decision.tier.value}")
    print(f"Interrupt: {decision.should_interrupt}")
    print(f"Reason: {decision.reason}")

    # Step 3: Handle based on tier
    if decision.should_interrupt:
        # Request human review
        review_id = controller.request_human_review(
            decision,
            context={"dispute": dispute}
        )
        return f"PENDING_REVIEW:{review_id}"
    else:
        # Automated processing
        return f"AUTO_PROCESSED:{dispute['id']}"


# Test cases
disputes = [
    # Tier 3: Auto-process
    {
        "id": "DSP-001",
        "ai_confidence": 0.95,
        "amount": 50.0,
        "type": "billing_error",
    },
    # Tier 2: Needs review (low confidence)
    {
        "id": "DSP-002",
        "ai_confidence": 0.72,
        "amount": 500.0,
        "type": "billing_error",
    },
    # Tier 1: Needs review (SAR filing)
    {
        "id": "DSP-003",
        "ai_confidence": 0.99,
        "amount": 100.0,
        "type": "fraud",
        "action": "sar_filing",
    },
]

for dispute in disputes:
    result = process_dispute(dispute)
    print(f"{dispute['id']}: {result}\n")
```

Expected output:

```
Tier: tier_3
Interrupt: False
Reason: Automated processing allowed
DSP-001: AUTO_PROCESSED:DSP-001

Tier: tier_2
Interrupt: True
Reason: Confidence 0.72 below threshold 0.85
DSP-002: PENDING_REVIEW:<uuid>

Tier: tier_1
Interrupt: True
Reason: Tier 1 action (sar_filing) requires human approval
DSP-003: PENDING_REVIEW:<uuid>
```

---

## Configuring Thresholds

### Via Code

```python
controller = HITLController(
    confidence_threshold=0.90,  # More conservative
    amount_threshold=5000.0,    # Lower threshold
)
```

### Via Environment Variables

```bash
export HITL_CONFIDENCE_THRESHOLD=0.90
export HITL_AMOUNT_THRESHOLD=5000.0
```

```python
# Will use environment variables if set
from closing_the_gaps.config import load_config, get_hitl_config

config = load_config()
hitl_config = get_hitl_config(config)
print(hitl_config.confidence_threshold)  # 0.90
```

---

## Monitoring Escalation Rates

Track how often decisions are escalated:

```python
controller = HITLController()

# Process some decisions
for _ in range(100):
    controller.should_interrupt(
        confidence=0.72,
        amount=500.0,
        dispute_type="general"
    )

stats = controller.get_escalation_stats()
print(f"Total decisions: {stats['total_decisions']}")
print(f"Tier breakdown: {stats['tier_counts']}")
print(f"Interrupt rate: {stats['interrupt_rate']:.1%}")
```

---

## Regulatory Compliance Checklist

| Requirement | Implementation | Status |
|-------------|---------------|--------|
| SR 11-7: Evaluation | Tier classification logged | ✅ |
| SR 11-7: Monitoring | `get_escalation_stats()` | ✅ |
| SR 11-7: Outcomes | Human decisions recorded | ✅ |
| EU AI Act: Oversight | Tier 1 always interrupts | ✅ |
| EU AI Act: Intervention | `record_human_decision()` | ✅ |
| Audit Trail | All decisions logged with UUID | ✅ |

---

## Next Steps

1. **Read the PRD**: `tasks/0012-prd-closing-gaps-phase1-governance.md`
2. **Review DESIGN.md**: `lesson-18/closing_the_gaps/DESIGN.md`
3. **Study Regulations**:
   - Federal Reserve SR 11-7
   - EU AI Act Article 14
4. **Explore PromptSecurityGuard**: `tutorials/01_prompt_security_quickstart.md`

---

## Troubleshooting

### Too Many Escalations

If everything is being escalated:

1. Check confidence threshold - may be too high
2. Verify dispute type classification
3. Review amount threshold against your transaction volume

```python
# Debug: See why decision was made
decision = controller.should_interrupt(...)
print(f"Tier: {decision.tier}")
print(f"Reason: {decision.reason}")
```

### Compliance Audit Questions

For auditors asking "why was this decision made?":

```python
# Every decision has a unique ID and timestamp
print(f"Decision ID: {decision.decision_id}")
print(f"Timestamp: {decision.timestamp}")
print(f"Tier: {decision.tier}")
print(f"Reason: {decision.reason}")
```

---

*Tutorial Version: 1.0 | Created: December 2024*

