# Closing the Gaps - Tutorial Index

**Phase 1: Governance Layer**
**Version:** 1.0
**Updated:** December 2024

---

## Overview

This tutorial series covers the Governance Layer of the "Closing the Gaps" framework, focusing on security and regulatory compliance for multi-agent bank dispute systems.

---

## Quick-Start Tutorials (~15 min each)

### 1. [PromptSecurityGuard Quick-Start](01_prompt_security_quickstart.md)

**Gap Addressed:** Gap 9 - Prompt Injection Defense

Learn how to:
- Understand prompt injection attack vectors
- Configure multi-layer security scanning
- Detect OWASP LLM Top 10 threats
- Add custom detection patterns
- Implement agent-to-agent security

**Prerequisites:** Basic Python knowledge

**Key Topics:**
- ScanResult model
- Pattern matching (Layer 1)
- Structural analysis (Layer 2)
- Input sanitization
- Threat statistics

---

### 2. [HITLController Quick-Start](02_hitl_controller_quickstart.md)

**Gap Addressed:** Gap 6 - Human-in-the-Loop Oversight

Learn how to:
- Understand the three-tier oversight model
- Configure confidence and amount thresholds
- Classify actions into appropriate tiers
- Implement the human review workflow
- Meet regulatory compliance (SR 11-7, EU AI Act)

**Prerequisites:** Basic Python knowledge

**Key Topics:**
- OversightTier enum (Tier 1, 2, 3)
- InterruptDecision model
- Tier classification logic
- Human review workflow
- Escalation monitoring

---

## Learning Path

```
                 ┌─────────────────────────────────┐
                 │     Start Here                  │
                 │  PromptSecurityGuard (~15 min)  │
                 └───────────────┬─────────────────┘
                                 │
                                 ▼
                 ┌─────────────────────────────────┐
                 │     Next                        │
                 │  HITLController (~15 min)       │
                 └───────────────┬─────────────────┘
                                 │
                                 ▼
                 ┌─────────────────────────────────┐
                 │     Integration                 │
                 │  Combined Workflow (see below)  │
                 └─────────────────────────────────┘
```

---

## Combined Workflow Example

After completing both tutorials, here's how the components work together:

```python
from closing_the_gaps.governance import (
    PromptSecurityGuard,
    HITLController,
)

def process_dispute_request(user_input: str, dispute_context: dict) -> dict:
    """
    Complete governance flow:
    1. Security scan (PromptSecurityGuard)
    2. HITL check (HITLController)
    3. Process or escalate
    """
    guard = PromptSecurityGuard()
    hitl = HITLController()

    # Step 1: Security scan
    scan_result = guard.scan_input(user_input)
    if not scan_result.is_safe:
        return {
            "status": "BLOCKED",
            "reason": f"Security threat: {scan_result.threat_type}",
        }

    # Step 2: HITL check
    decision = hitl.should_interrupt(
        confidence=dispute_context["ai_confidence"],
        amount=dispute_context.get("amount"),
        dispute_type=dispute_context["type"],
        action_type=dispute_context.get("action"),
    )

    # Step 3: Route based on decision
    if decision.should_interrupt:
        review_id = hitl.request_human_review(decision, dispute_context)
        return {
            "status": "PENDING_REVIEW",
            "review_id": review_id,
            "tier": decision.tier.value,
        }

    return {
        "status": "AUTO_PROCESSED",
        "tier": decision.tier.value,
    }
```

---

## Reference Documentation

| Document | Description |
|----------|-------------|
| [PRD](../../tasks/0012-prd-closing-gaps-phase1-governance.md) | Product Requirements Document |
| [DESIGN.md](../DESIGN.md) | High-Level Design Document |
| [API Contracts](../governance/) | Source code with docstrings |
| [Configuration](../config/security.yaml) | Configuration reference |

---

## Running Tests

Verify your understanding by running the test suite:

```bash
# Run all governance tests
pytest lesson-18/closing_the_gaps/tests/ -v

# Run specific component tests
pytest lesson-18/closing_the_gaps/tests/test_prompt_security.py -v
pytest lesson-18/closing_the_gaps/tests/test_hitl_controller.py -v

# Run integration tests
pytest lesson-18/closing_the_gaps/tests/test_governance_integration.py -v
```

---

## External Resources

### Regulatory References
- [Federal Reserve SR 11-7](https://www.federalreserve.gov/supervisionreg/srletters/sr1107.htm) - Model Risk Management
- [EU AI Act](https://artificialintelligenceact.eu/) - Artificial Intelligence Act
- [FFIEC Guidance](https://www.ffiec.gov/) - Federal Financial Institutions Examination Council

### Security References
- [OWASP LLM Top 10](https://owasp.org/www-project-top-10-for-large-language-model-applications/) - LLM Security Threats
- [Prompt Injection Attacks](https://simonwillison.net/series/prompt-injection/) - Simon Willison's Research

### Industry Frameworks
- [Sardine AI](https://www.sardine.ai/) - Tiered Oversight Model Reference

---

## Feedback

Found an issue or have a suggestion? Check the test files for expected behavior:
- `tests/test_prompt_security.py`
- `tests/test_hitl_controller.py`
- `tests/test_governance_integration.py`

---

*Tutorial Index Version: 1.0 | Created: December 2024*

