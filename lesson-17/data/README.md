# Lesson 17: Synthetic Datasets for Explainability Framework

This directory contains synthetic datasets for the Lesson 17 explainability framework tutorials.

## Dataset Overview

| Dataset | File(s) | Records | Purpose |
|---------|---------|---------|---------|
| PII Examples | `pii_examples_50.json` | 50 | GuardRails PII detection testing (Tutorial 4) |
| Agent Metadata | `agent_metadata_10.json` | 10 | AgentFacts governance demos (Tutorial 3) |
| Workflow Traces | `workflows/*.json` | 5 | BlackBoxRecorder debugging (Tutorial 2) |
| Research Workflows | `research_workflows/*.json` | 10 | PhaseLogger demos (Tutorial 5) |
| Parameter Logs | `parameter_substitutions_20.json` | 20 | Debugging & audit (Tutorial 6) |

## Generated Data Characteristics

### PII Examples (`pii_examples_50.json`)

50 text samples with embedded PII for testing GuardRails validation:

| PII Type | Count | Pattern |
|----------|-------|---------|
| SSN | 8 | `XXX-XX-XXXX` |
| Credit Card | 8 | `XXXX-XXXX-XXXX-XXXX` |
| Email | 8 | `user@domain.com` |
| Phone | 8 | `+1-XXX-XXX-XXXX` |
| Medical Record Number | 6 | `MRN-XXXXXXXX` |
| Passport | 6 | `PXXXXXXXX` |
| Driver's License | 6 | `DL-XX-XXXXXXX` |

Each example includes:
- Gold labels (`pii_types`, `pii_spans`)
- Expected redacted output
- Context type (healthcare, financial, customer_service, etc.)

### Agent Metadata (`agent_metadata_10.json`)

10 agent profiles following the AgentFacts schema:

1. **Invoice Extractor** - OCR + field extraction
2. **Fraud Detector** - ML model + rule-based
3. **Diagnosis Generator** - Multi-modal LLM for healthcare
4. **Contract Reviewer** - Legal entity recognition
5. **Research Assistant** - Literature search + summarization
6. **Data Validator** - Schema validation
7. **Report Generator** - Document synthesis
8. **Anomaly Detector** - Time-series analysis
9. **Sentiment Analyzer** - NLP classification
10. **Recommendation Engine** - Collaborative filtering

Each agent includes:
- Capabilities with input/output schemas
- Latency SLAs (P50, P95)
- Cost estimates per call
- Policies (rate limits, approval requirements, data access)
- SHA256 signature hash for tamper detection

### Workflow Traces (`workflows/`)

5 multi-agent workflow traces for BlackBoxRecorder demos:

| Workflow | Agents | Outcome | Use Case |
|----------|--------|---------|----------|
| Invoice Processing | 3 | Cascade Failure | Debugging parameter changes |
| Fraud Detection | 2 | Success | Normal workflow tracking |
| Research Workflow | 4 | Success | Multi-phase collaboration |
| Healthcare Diagnosis | 5 | Pending Approval | Human-in-the-loop |
| Contract Review | 3 | Manual Review | Risk escalation |

Each trace includes:
- TaskPlan with steps and dependencies
- Collaborator join/leave events
- Parameter substitutions with justifications
- Execution events (8 event types)

### Research Workflows (`research_workflows/`)

10 research paper generation workflows for PhaseLogger demos:

- Phases: PLANNING → LITERATURE_REVIEW → DATA_COLLECTION → EXPERIMENT → VALIDATION → REPORTING
- Decisions with alternatives, rationale, and confidence scores
- Artifacts with metadata (size, format, location)
- Mix of outcomes: 7 successful, 3 failed

### Parameter Substitutions (`parameter_substitutions_20.json`)

20 parameter change events for debugging demos:

Parameters covered:
- `confidence_threshold`
- `model_version`
- `temperature`
- `max_tokens`
- `retry_attempts`
- `timeout_seconds`
- `batch_size`
- `fraud_threshold`

Each event includes:
- Before/after values
- Justification
- Impact metrics (success rate delta, latency impact, cost impact)
- Root cause correlation for negative impacts
- Recommendations

## Regenerating Datasets

To regenerate all datasets with the same seed:

```bash
cd lesson-17
python scripts/generate_datasets.py --seed 42
```

To use a different seed for variation:

```bash
python scripts/generate_datasets.py --seed 123
```

## Validating Datasets

To validate all datasets against Pydantic schemas:

```bash
cd lesson-17
python scripts/validate_datasets.py
```

## Schema Compatibility

All datasets are compatible with the Pydantic models in:
- `backend/explainability/agent_facts.py` - AgentFacts, Capability, Policy
- `backend/explainability/black_box.py` - TaskPlan, TraceEvent, ExecutionTrace
- `backend/explainability/phase_logger.py` - Decision, Artifact, PhaseOutcome
- `backend/explainability/guardrails.py` - Constraint, ValidationResult

## Reusing Lesson 16 Data

The following Lesson 16 datasets can be used with Lesson 17 tutorials:

| Lesson 16 Data | Lesson 17 Use |
|----------------|---------------|
| `invoices_100.json` | Tutorial 2 (BlackBoxRecorder) - Invoice workflow input |
| `transactions_100.json` | Tutorial 6 (Combining Components) - Fraud pipeline |
| `reconciliation_100.json` | Tutorial 7 (Integration) - Reliability + Explainability |

## Quality Standards

All synthetic data:
- ✅ Deterministically reproducible (seed=42)
- ✅ Passes Pydantic schema validation
- ✅ Includes gold labels for testing
- ✅ Uses realistic domain-specific values
- ✅ Privacy-safe (no real PII)

---

**Generated:** See `DATASET_SUMMARY.json` for timestamp
**Version:** 1.0
**Seed:** 42

