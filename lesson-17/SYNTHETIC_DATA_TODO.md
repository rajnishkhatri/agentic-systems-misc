# Lesson 17: Synthetic Data Requirements for Tutorial Creation

**Generated:** 2025-11-27
**Purpose:** Identify and generate mock/synthetic data needed for Lesson 17 explainability framework tutorials
**Status:** Planning Phase (P0 Tutorials - Critical Priority)

---

## Executive Summary

### Current State Analysis

**Lesson 16 Data (EXISTING - 300 tasks):**
- ✅ `invoices_100.json` - 100 invoices with OCR errors, missing fields, duplicates
- ✅ `transactions_100.json` - 100 transactions with 10% fraud rate, ambiguous patterns
- ✅ `reconciliation_100.json` - 100 reconciliation tasks with date mismatches, rounding errors
- ✅ Checkpoint files from reliability framework (sequential, state machine, reliability_framework)
- ✅ Audit logs from reliability testing

**Reusability Assessment:** 70% of Lesson 17 tutorial needs can be met with existing Lesson 16 data with minor adaptations.

**Data Gaps (NEED TO GENERATE):**
- ❌ Healthcare patient records (de-identified) for HIPAA case study (P2.1)
- ❌ Legal contract samples for contract review case study (P2.3)
- ❌ Research workflow artifacts (papers, datasets, models) for PhaseLogger demos
- ❌ Extended PII examples (beyond SSN/credit card - add medical IDs, passport numbers)
- ❌ Multi-agent collaboration traces (agent join/leave events)
- ❌ Compliance export formats (HIPAA audit trail, SOX report templates)

---

## Data Reusability Matrix

### ✅ Lesson 16 Data → Lesson 17 Tutorial Mapping

| Lesson 16 Data | Lesson 17 Tutorial Use | Adaptation Needed |
|---------------|------------------------|-------------------|
| **invoices_100.json** | Tutorial 2 (BlackBoxRecorder) - Invoice processing cascade failure | ✅ READY - Use as-is for 3-agent workflow (Extractor→Validator→Approver) |
| **transactions_100.json** | Tutorial 6 (Combining Components) - Fraud detection pipeline | ✅ READY - Perfect for end-to-end example with all 4 components |
| **transactions_100.json** | Case Study 2 (P2.2) - Financial Fraud (SOX Compliance) | ✅ READY - Already has fraud labels, confidence scores |
| **reconciliation_100.json** | Tutorial 7 (Integration with Lesson 16) - Resilient + Explainable workflow | ✅ READY - Shows retry, circuit breaker with explainability |
| **checkpoint files** | Tutorial 2 (BlackBoxRecorder) - Rollback point examples | ✅ READY - Already has checkpoint structure from lesson-16 |
| **audit_logs** | Tutorial 3 (AgentFacts) - Audit trail examples | ⚠️ ADAPT - Need to add signature verification, policy checks |

### ❌ Data Gaps Requiring Generation

| Tutorial/Case Study | Missing Data | Priority | Estimated Size | Complexity |
|---------------------|--------------|----------|----------------|------------|
| **Tutorial 4 (GuardRails)** | Extended PII examples (medical IDs, passport, driver's license) | P0 | 50 examples | ⭐ Low |
| **Tutorial 5 (PhaseLogger)** | Research workflow artifacts (papers, datasets, models) | P1 | 10 workflows | ⭐⭐ Medium |
| **Case Study 1 (P2.1)** | Healthcare patient records (de-identified) for HIPAA | P2 | 30 patients, 5 agents | ⭐⭐⭐ High |
| **Case Study 3 (P2.3)** | Legal contract samples (employment, NDA, service agreements) | P2 | 20 contracts | ⭐⭐⭐ High |
| **Tutorial 3 (AgentFacts)** | Agent metadata with capabilities, policies, signatures | P0 | 10 agents | ⭐⭐ Medium |
| **Tutorial 2 (BlackBoxRecorder)** | Multi-agent collaboration traces (agent join/leave events) | P0 | 5 workflows | ⭐⭐ Medium |
| **Tutorial 6 (Combining)** | Parameter substitution logs (model changes, threshold adjustments) | P1 | 20 events | ⭐ Low |
| **Case Studies** | Compliance export formats (HIPAA audit trail, SOX report templates) | P2 | 3 templates | ⭐⭐ Medium |

---

## Detailed Data Generation Tasks

### P0 (CRITICAL - Blocking Tutorial 1-4)

#### P0.1: Extended PII Examples for GuardRails (Tutorial 4)

**Purpose:** Demonstrate all 7 PII types in built-in validators

**Requirements:**
- 50 synthetic text samples containing PII
- Must include:
  - ✅ SSN (already in Lesson 16): `123-45-6789`
  - ✅ Credit card (already in Lesson 16): `4532-1234-5678-9010`
  - ✅ Email (already in Lesson 16): `john.doe@example.com`
  - ✅ Phone (already in Lesson 16): `+1-555-123-4567`
  - ❌ **NEW:** Medical record numbers: `MRN-12345678`
  - ❌ **NEW:** Passport numbers: `P12345678`
  - ❌ **NEW:** Driver's license: `DL-CA-D1234567`
- Realistic context (customer service chats, medical reports, financial applications)
- Gold labels for PII detection accuracy testing

**Schema:**
```json
{
  "pii_id": "PII-001",
  "text": "Patient John Doe (MRN-12345678) presented with...",
  "contains_pii": true,
  "pii_types": ["name", "medical_record_number"],
  "pii_spans": [
    {"type": "name", "start": 8, "end": 16, "text": "John Doe"},
    {"type": "medical_record_number", "start": 18, "end": 30, "text": "MRN-12345678"}
  ],
  "expected_redacted": "Patient [REDACTED] ([REDACTED]) presented with..."
}
```

**Output File:** `lesson-17/data/pii_examples_50.json`
**Estimated Effort:** 2 hours (manual creation + regex testing)

---

#### P0.2: Agent Metadata Examples for AgentFacts (Tutorial 3)

**Purpose:** Showcase capability declarations, policy management, signature verification

**Requirements:**
- 10 synthetic agent metadata records
- Must represent diverse agent types:
  - Invoice Extractor (OCR + field extraction)
  - Fraud Detector (ML model + rule-based)
  - Diagnosis Generator (multi-modal LLM)
  - Contract Reviewer (legal entity recognition)
  - Research Assistant (literature search + summarization)
- Include:
  - Capabilities with input/output schemas, latency SLAs, cost estimates
  - Policies (rate limits, approval requirements, data access controls)
  - Cryptographic signatures (SHA256)
  - Version history (v1.0, v1.1, v2.0)

**Schema (AgentFacts):**
```json
{
  "agent_id": "fraud-detector-v2",
  "agent_name": "Fraud Detection Agent",
  "owner": "security-team",
  "version": "2.0.0",
  "created_at": "2025-01-15T10:00:00Z",
  "updated_at": "2025-11-27T14:30:00Z",
  "capabilities": [
    {
      "capability_id": "score_transaction",
      "name": "Score Transaction Fraud Risk",
      "description": "Analyzes transaction patterns for fraud indicators",
      "input_schema": {
        "type": "object",
        "properties": {
          "transaction": {"type": "object"}
        }
      },
      "output_schema": {
        "type": "object",
        "properties": {
          "fraud_score": {"type": "number"},
          "reasoning": {"type": "string"}
        }
      },
      "latency_p50_ms": 350,
      "latency_p95_ms": 500,
      "cost_per_call_usd": 0.01
    }
  ],
  "policies": [
    {
      "policy_id": "rate_limit",
      "rate_limit_per_minute": 1000,
      "max_concurrent_requests": 50
    },
    {
      "policy_id": "approval",
      "requires_human_approval": true,
      "approval_threshold_amount": 10000
    },
    {
      "policy_id": "data_access",
      "allowed_data_sources": ["transaction_db", "user_behavior_db"],
      "pii_handling_mode": "redact"
    }
  ],
  "signature_hash": "a3f5b8c9d2e1f4a6b7c8d9e0f1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0"
}
```

**Output File:** `lesson-17/data/agent_metadata_10.json`
**Estimated Effort:** 3 hours (schema design + 10 agent profiles + signature generation)

---

#### P0.3: Multi-Agent Collaboration Traces for BlackBoxRecorder (Tutorial 2)

**Purpose:** Demonstrate agent join/leave events, parameter substitutions, cascade failures

**Requirements:**
- 5 synthetic multi-agent workflow traces
- Scenarios:
  1. **Invoice Processing (3 agents):** Extractor → Validator → Approver
  2. **Fraud Detection (2 agents):** Scorer → Escalator
  3. **Research Workflow (4 agents):** Searcher → Summarizer → Synthesizer → Reviewer
  4. **Healthcare Diagnosis (5 agents):** Symptom Analyzer → Lab Interpreter → Diagnosis Generator → Treatment Recommender → Human Approver
  5. **Contract Review (3 agents):** Clause Extractor → Risk Assessor → Compliance Checker

- Must include:
  - Task plan with steps and dependencies
  - Collaborator list with agent join/leave timestamps
  - Parameter substitutions (model version, confidence threshold, temperature)
  - Execution traces (STEP_START, STEP_END, DECISION, ERROR, CHECKPOINT)
  - Cascade failure example (agent 2 fails → agent 3 never starts)

**Schema (ExecutionTrace):**
```json
{
  "workflow_id": "invoice-processing-001",
  "task_plan": {
    "task_id": "invoice-processing-001",
    "steps": [
      {"step_id": "extract_vendor", "depends_on": [], "agent_id": "extractor-v1"},
      {"step_id": "validate_amount", "depends_on": ["extract_vendor"], "agent_id": "validator-v1"},
      {"step_id": "approve_invoice", "depends_on": ["validate_amount"], "agent_id": "approver-v1"}
    ]
  },
  "collaborators": [
    {
      "agent_id": "extractor-v1",
      "agent_name": "Invoice Extractor",
      "role": "extraction",
      "joined_at": "2025-11-27T14:00:00Z",
      "left_at": "2025-11-27T14:00:12Z"
    },
    {
      "agent_id": "validator-v1",
      "agent_name": "Amount Validator",
      "role": "validation",
      "joined_at": "2025-11-27T14:00:12Z",
      "left_at": "2025-11-27T14:00:18Z"
    }
  ],
  "parameter_substitutions": [
    {
      "timestamp": "2025-11-27T14:00:10Z",
      "parameter_name": "confidence_threshold",
      "old_value": 0.8,
      "new_value": 0.95,
      "justification": "Reduce false positives per compliance team request",
      "changed_by": "extractor-v1"
    }
  ],
  "execution_events": [
    {
      "event_id": "evt-001",
      "event_type": "STEP_START",
      "step_id": "extract_vendor",
      "timestamp": "2025-11-27T14:00:00Z",
      "agent_id": "extractor-v1"
    },
    {
      "event_id": "evt-002",
      "event_type": "DECISION",
      "step_id": "extract_vendor",
      "timestamp": "2025-11-27T14:00:05Z",
      "agent_id": "extractor-v1",
      "metadata": {
        "decision": "Use GPT-4 for OCR correction",
        "alternatives": ["GPT-3.5", "Claude"],
        "rationale": "Higher accuracy needed for noisy scans"
      }
    },
    {
      "event_id": "evt-003",
      "event_type": "STEP_END",
      "step_id": "extract_vendor",
      "timestamp": "2025-11-27T14:00:12Z",
      "agent_id": "extractor-v1",
      "success": true,
      "duration_ms": 12000
    },
    {
      "event_id": "evt-004",
      "event_type": "STEP_START",
      "step_id": "validate_amount",
      "timestamp": "2025-11-27T14:00:12Z",
      "agent_id": "validator-v1"
    },
    {
      "event_id": "evt-005",
      "event_type": "ERROR",
      "step_id": "validate_amount",
      "timestamp": "2025-11-27T14:00:15Z",
      "agent_id": "validator-v1",
      "error_message": "Confidence threshold too high (0.95) - no valid results",
      "is_recoverable": false
    },
    {
      "event_id": "evt-006",
      "event_type": "STEP_END",
      "step_id": "validate_amount",
      "timestamp": "2025-11-27T14:00:18Z",
      "agent_id": "validator-v1",
      "success": false,
      "duration_ms": 6000
    }
  ],
  "outcome": {
    "status": "failed",
    "reason": "Cascade failure: validator crashed after parameter change",
    "root_cause": "Parameter substitution (confidence_threshold: 0.8 → 0.95) caused empty validation results"
  }
}
```

**Output Files:**
- `lesson-17/data/workflows/invoice_processing_trace.json`
- `lesson-17/data/workflows/fraud_detection_trace.json`
- `lesson-17/data/workflows/research_workflow_trace.json`
- `lesson-17/data/workflows/healthcare_diagnosis_trace.json`
- `lesson-17/data/workflows/contract_review_trace.json`

**Estimated Effort:** 4 hours (5 workflows × ~50 events each)

---

### P1 (HIGH PRIORITY - Advanced Tutorials)

#### P1.1: Research Workflow Artifacts for PhaseLogger (Tutorial 5)

**Purpose:** Demonstrate phase-based logging for research reproducibility

**Requirements:**
- 10 synthetic research workflows
- Phases: PLANNING → LITERATURE_REVIEW → DATA_COLLECTION → EXPERIMENT → VALIDATION → REPORTING → COMPLETED
- Artifacts:
  - Literature review summaries (markdown)
  - Datasets (CSV metadata: rows, columns, size)
  - Trained models (JSON metadata: architecture, accuracy, checkpoints)
  - Generated reports (PDF metadata: pages, citations)
  - Visualizations (PNG metadata: dimensions, type)
- Decisions:
  - Research question selection (alternatives, rationale, confidence)
  - Model architecture selection (GPT-4 vs Claude vs Gemini)
  - Hyperparameter tuning (learning rate, batch size, epochs)
- Errors:
  - Recoverable: Data download timeout → retry
  - Fatal: Model training crash (OOM error) → workflow FAILED

**Schema (WorkflowSummary):**
```json
{
  "workflow_id": "research-paper-gen-001",
  "workflow_type": "research_paper_generation",
  "start_time": "2025-11-01T09:00:00Z",
  "end_time": "2025-11-15T17:30:00Z",
  "total_duration_hours": 344.5,
  "phases": [
    {
      "phase_id": "planning",
      "phase_type": "PLANNING",
      "start_time": "2025-11-01T09:00:00Z",
      "end_time": "2025-11-01T15:00:00Z",
      "duration_hours": 6.0,
      "outcome": {
        "status": "success",
        "summary": "Research question and methodology defined"
      }
    },
    {
      "phase_id": "literature_review",
      "phase_type": "LITERATURE_REVIEW",
      "start_time": "2025-11-02T09:00:00Z",
      "end_time": "2025-11-05T17:00:00Z",
      "duration_hours": 80.0,
      "outcome": {
        "status": "success",
        "summary": "47 papers reviewed, 12 key findings identified"
      }
    },
    {
      "phase_id": "experiment",
      "phase_type": "EXPERIMENT",
      "start_time": "2025-11-10T09:00:00Z",
      "end_time": "2025-11-12T14:30:00Z",
      "duration_hours": 53.5,
      "outcome": {
        "status": "failed",
        "summary": "Model training crashed (OOM error)",
        "error": {
          "message": "CUDA out of memory: tried to allocate 20.00 GiB",
          "stack_trace": "...",
          "is_recoverable": false
        }
      }
    }
  ],
  "decisions": [
    {
      "decision_id": "research_question",
      "timestamp": "2025-11-01T10:30:00Z",
      "phase": "PLANNING",
      "description": "Select research question for study",
      "alternatives": [
        "Q1: LLM scaling laws and emergent abilities",
        "Q2: Agent reliability in multi-step workflows",
        "Q3: RAG optimization for domain-specific knowledge"
      ],
      "selected": "Q2: Agent reliability in multi-step workflows",
      "rationale": "High industry demand, clear evaluation metrics available, builds on Lesson 16 work",
      "confidence": 0.9
    },
    {
      "decision_id": "model_selection",
      "timestamp": "2025-11-10T09:15:00Z",
      "phase": "EXPERIMENT",
      "description": "Choose LLM for experiment",
      "alternatives": ["GPT-4", "Claude Sonnet", "Gemini Pro"],
      "selected": "Claude Sonnet",
      "rationale": "Best cost/performance ratio for 10K token context windows",
      "confidence": 0.85
    }
  ],
  "artifacts": [
    {
      "artifact_id": "lit_review",
      "artifact_type": "document",
      "phase": "LITERATURE_REVIEW",
      "description": "Literature review summary (47 papers)",
      "metadata": {
        "format": "markdown",
        "size_kb": 125,
        "papers_reviewed": 47,
        "key_findings": 12
      },
      "location": "artifacts/lit_review.md",
      "created_at": "2025-11-05T17:00:00Z"
    },
    {
      "artifact_id": "trained_model_v1",
      "artifact_type": "model",
      "phase": "EXPERIMENT",
      "description": "Fine-tuned GPT-3.5 for agent workflow prediction",
      "metadata": {
        "format": "safetensors",
        "size_mb": 1024,
        "architecture": "GPT-3.5-turbo",
        "accuracy": 0.92,
        "training_epochs": 5,
        "checkpoint": "epoch_3"
      },
      "location": "s3://models/gita-qa-v1",
      "created_at": "2025-11-12T12:00:00Z"
    }
  ],
  "final_status": "failed",
  "failure_reason": "Model training OOM error (unrecoverable)"
}
```

**Output Files:**
- `lesson-17/data/research_workflows/` (10 workflow JSON files)
- `lesson-17/data/research_workflows/README.md` (documentation)

**Estimated Effort:** 5 hours (10 workflows × 4-8 phases each)

---

#### P1.2: Parameter Substitution Logs for Tutorial 6 (Combining Components)

**Purpose:** Show how parameter changes affect workflow outcomes (debugging aid)

**Requirements:**
- 20 synthetic parameter change events
- Parameters:
  - Model version (GPT-3.5 → GPT-4)
  - Confidence threshold (0.8 → 0.95)
  - Temperature (0.7 → 0.3)
  - Max tokens (512 → 1024)
  - Retry attempts (3 → 5)
- Include:
  - Before/after values
  - Justification (why changed)
  - Changed by (agent_id or user_id)
  - Impact on workflow (success/failure correlation)

**Schema (ParameterSubstitution):**
```json
{
  "substitution_id": "param-sub-001",
  "workflow_id": "fraud-pipeline-001",
  "timestamp": "2025-11-27T14:30:00Z",
  "parameter_name": "fraud_threshold",
  "old_value": 0.75,
  "new_value": 0.85,
  "justification": "Reduce false positives per compliance team request (SOX audit)",
  "changed_by": "user_admin",
  "change_reason": "compliance_requirement",
  "impact": {
    "workflows_affected": 127,
    "success_rate_before": 0.94,
    "success_rate_after": 0.89,
    "false_positive_rate_before": 0.12,
    "false_positive_rate_after": 0.05,
    "root_cause_of_failures": "Threshold too high → empty results → cascade failures"
  }
}
```

**Output File:** `lesson-17/data/parameter_substitutions_20.json`
**Estimated Effort:** 2 hours

---

### P2 (MEDIUM PRIORITY - Case Studies)

#### P2.1: Healthcare Patient Records for HIPAA Case Study

**Purpose:** Demonstrate healthcare agent governance with HIPAA compliance

**Requirements:**
- 30 synthetic de-identified patient records
- 5 specialist agents (Symptom Analyzer, Lab Interpreter, Diagnosis Generator, Treatment Recommender, Human Approver)
- Must include:
  - Patient demographics (age, gender) - NO real names/IDs
  - Medical history (conditions, medications, allergies)
  - Lab results (vitals, bloodwork, imaging)
  - Diagnosis workflow traces (which agent accessed which data)
  - Human approval checkpoints (high-risk diagnoses)
  - HIPAA audit trail (access logs, consent tracking)

**Schema (PatientRecord - De-Identified):**
```json
{
  "patient_id": "PATIENT-ANON-001",
  "demographics": {
    "age": 45,
    "gender": "F",
    "ethnicity": "Caucasian"
  },
  "medical_history": {
    "conditions": ["Type 2 Diabetes", "Hypertension"],
    "medications": ["Metformin 500mg", "Lisinopril 10mg"],
    "allergies": ["Penicillin"]
  },
  "lab_results": {
    "vitals": {
      "blood_pressure": "145/92",
      "heart_rate": 78,
      "temperature": 98.6
    },
    "bloodwork": {
      "hba1c": 7.2,
      "fasting_glucose": 145,
      "cholesterol": 210
    }
  },
  "diagnosis_workflow": {
    "workflow_id": "diagnosis-001",
    "agents_involved": [
      {
        "agent_id": "symptom-analyzer-v1",
        "accessed_at": "2025-11-27T09:00:00Z",
        "data_accessed": ["demographics", "medical_history"],
        "consent_verified": true
      },
      {
        "agent_id": "lab-interpreter-v1",
        "accessed_at": "2025-11-27T09:05:00Z",
        "data_accessed": ["lab_results"],
        "consent_verified": true
      },
      {
        "agent_id": "diagnosis-generator-v1",
        "accessed_at": "2025-11-27T09:10:00Z",
        "data_accessed": ["medical_history", "lab_results"],
        "consent_verified": true
      }
    ],
    "diagnosis": {
      "condition": "Poorly controlled Type 2 Diabetes",
      "confidence": 0.92,
      "requires_human_approval": true,
      "approved_by": "dr_smith",
      "approved_at": "2025-11-27T10:00:00Z"
    }
  },
  "hipaa_audit_trail": [
    {
      "timestamp": "2025-11-27T09:00:00Z",
      "action": "READ",
      "agent_id": "symptom-analyzer-v1",
      "data_fields": ["demographics", "medical_history"],
      "consent_id": "consent-001",
      "user_id": "dr_smith"
    }
  ]
}
```

**Output Files:**
- `lesson-17/data/case_studies/healthcare/patients_30.json`
- `lesson-17/data/case_studies/healthcare/agents_5.json`
- `lesson-17/data/case_studies/healthcare/hipaa_audit_template.json`

**Estimated Effort:** 6 hours (HIPAA compliance research + 30 patient records + audit trail)

---

#### P2.2: Legal Contract Samples for Contract Review Case Study

**Purpose:** Demonstrate legal discovery exports and clause extraction validation

**Requirements:**
- 20 synthetic legal contracts (employment, NDA, service agreements)
- Must include:
  - Contract text (simplified for demo - 5-10 clauses each)
  - Clause extraction targets (clause type, risk level, extracted text)
  - Multi-agent workflow (Clause Extractor → Risk Assessor → Compliance Checker)
  - Discovery export format (legal-standard JSON)
  - Workflow replay capability (timeline visualization)

**Schema (LegalContract):**
```json
{
  "contract_id": "CONTRACT-001",
  "contract_type": "employment_agreement",
  "parties": ["Employer: Acme Corp", "Employee: Jane Doe"],
  "effective_date": "2025-01-01",
  "clauses": [
    {
      "clause_id": "clause-001",
      "clause_type": "compensation",
      "clause_text": "Employee shall receive an annual salary of $120,000, payable in bi-weekly installments.",
      "risk_level": "low",
      "compliance_notes": "Standard compensation clause, no red flags"
    },
    {
      "clause_id": "clause-002",
      "clause_type": "non_compete",
      "clause_text": "Employee agrees not to engage in competing business activities for 2 years after termination within 100-mile radius.",
      "risk_level": "high",
      "compliance_notes": "Non-compete may be unenforceable in California (overly broad geographic restriction)"
    },
    {
      "clause_id": "clause-003",
      "clause_type": "intellectual_property",
      "clause_text": "All work product created during employment shall be the exclusive property of Employer.",
      "risk_level": "medium",
      "compliance_notes": "Standard IP assignment, but ensure employee inventions exclusion is clear"
    }
  ],
  "review_workflow": {
    "workflow_id": "review-001",
    "phases": [
      {
        "phase": "CLAUSE_EXTRACTION",
        "agent_id": "clause-extractor-v1",
        "extracted_clauses": 3,
        "duration_ms": 5000
      },
      {
        "phase": "RISK_ASSESSMENT",
        "agent_id": "risk-assessor-v1",
        "high_risk_clauses": 1,
        "duration_ms": 3000
      },
      {
        "phase": "COMPLIANCE_CHECK",
        "agent_id": "compliance-checker-v1",
        "violations_found": 0,
        "duration_ms": 2000
      }
    ],
    "final_status": "manual_review_required",
    "reason": "High-risk non-compete clause detected"
  },
  "discovery_export": {
    "export_id": "discovery-001",
    "export_date": "2025-11-27T12:00:00Z",
    "format": "legal_discovery_json_v1",
    "metadata": {
      "case_number": "CV-2025-001",
      "producing_party": "Acme Corp",
      "requesting_party": "Jane Doe",
      "privilege_log_included": false
    }
  }
}
```

**Output Files:**
- `lesson-17/data/case_studies/legal/contracts_20.json`
- `lesson-17/data/case_studies/legal/discovery_export_template.json`

**Estimated Effort:** 5 hours (legal research + 20 contracts + discovery format)

---

#### P2.3: Compliance Export Templates

**Purpose:** Provide HIPAA/SOX audit trail export formats for case studies

**Requirements:**
- 3 compliance export templates:
  1. HIPAA audit trail (healthcare case study)
  2. SOX audit trail (financial fraud case study)
  3. Legal discovery export (contract review case study)
- Must follow industry standards (simplified for demo)

**Schema (HIPAA Audit Trail):**
```json
{
  "audit_id": "HIPAA-AUDIT-2025-Q4",
  "organization": "Example Healthcare System",
  "audit_period": {
    "start_date": "2025-10-01",
    "end_date": "2025-12-31"
  },
  "scope": "All AI agent access to protected health information (PHI)",
  "agent_registry": [
    {
      "agent_id": "symptom-analyzer-v1",
      "agent_name": "Symptom Analysis Agent",
      "phi_access_approved": true,
      "approval_date": "2025-09-15",
      "data_sources_allowed": ["patient_db"],
      "pii_handling_mode": "redact"
    }
  ],
  "access_logs": [
    {
      "timestamp": "2025-11-27T09:00:00Z",
      "agent_id": "symptom-analyzer-v1",
      "action": "READ",
      "patient_id": "PATIENT-ANON-001",
      "data_fields": ["demographics", "medical_history"],
      "consent_verified": true,
      "user_id": "dr_smith"
    }
  ],
  "violations": [],
  "compliance_status": "PASS",
  "auditor": "HIPAA Compliance Team",
  "audit_date": "2025-12-15"
}
```

**Output Files:**
- `lesson-17/data/compliance_templates/hipaa_audit_template.json`
- `lesson-17/data/compliance_templates/sox_audit_template.json`
- `lesson-17/data/compliance_templates/legal_discovery_template.json`

**Estimated Effort:** 3 hours (compliance research + 3 templates)

---

## Data Generation Workflow

### Phase 1: Immediate Needs (P0 - 9 hours)

**Week 1:**
- [ ] P0.1: Extended PII examples (2h)
- [ ] P0.2: Agent metadata (3h)
- [ ] P0.3: Multi-agent collaboration traces (4h)

**Outcome:** Tutorials 1-4 (P0 Critical Priority) can be written with complete examples

---

### Phase 2: Advanced Tutorials (P1 - 7 hours)

**Week 2:**
- [ ] P1.1: Research workflow artifacts (5h)
- [ ] P1.2: Parameter substitution logs (2h)

**Outcome:** Tutorials 5-7 (P1 High Priority) have realistic examples

---

### Phase 3: Case Studies (P2 - 14 hours)

**Week 3:**
- [ ] P2.1: Healthcare patient records (6h)
- [ ] P2.2: Legal contract samples (5h)
- [ ] P2.3: Compliance export templates (3h)

**Outcome:** Case Studies 1-3 (P2 Medium Priority) demonstrate real-world ROI

---

## Data Directory Structure

```
lesson-17/
├── data/
│   ├── README.md                          # This file
│   ├── DATASET_SUMMARY.json               # Metadata for all datasets
│   │
│   ├── pii_examples_50.json               # P0.1 - Extended PII examples
│   ├── agent_metadata_10.json             # P0.2 - Agent metadata
│   │
│   ├── workflows/                         # P0.3 - Multi-agent traces
│   │   ├── invoice_processing_trace.json
│   │   ├── fraud_detection_trace.json
│   │   ├── research_workflow_trace.json
│   │   ├── healthcare_diagnosis_trace.json
│   │   └── contract_review_trace.json
│   │
│   ├── research_workflows/                # P1.1 - Research artifacts
│   │   ├── README.md
│   │   ├── workflow_001.json
│   │   ├── workflow_002.json
│   │   └── ... (10 total)
│   │
│   ├── parameter_substitutions_20.json    # P1.2 - Parameter logs
│   │
│   ├── case_studies/                      # P2 - Case study data
│   │   ├── healthcare/
│   │   │   ├── patients_30.json
│   │   │   ├── agents_5.json
│   │   │   └── hipaa_audit_template.json
│   │   ├── legal/
│   │   │   ├── contracts_20.json
│   │   │   └── discovery_export_template.json
│   │   └── README.md
│   │
│   └── compliance_templates/              # P2.3 - Compliance exports
│       ├── hipaa_audit_template.json
│       ├── sox_audit_template.json
│       └── legal_discovery_template.json
```

---

## Quality Standards

### All Synthetic Data Must:
- ✅ **Be realistic** (domain experts should find it plausible)
- ✅ **Follow JSON schemas** (100% parseable, no syntax errors)
- ✅ **Include gold labels** (expected outputs for validation)
- ✅ **Be privacy-safe** (no real PII, all data de-identified)
- ✅ **Be reproducible** (seed-based generation where applicable)
- ✅ **Be documented** (README.md with schema descriptions)

### Validation Checklist:
- [ ] JSON files parse without errors
- [ ] Schemas match implementation (Pydantic models)
- [ ] Examples cover common, edge, and error cases
- [ ] PII examples include both positive and negative cases
- [ ] Compliance templates follow industry standards (simplified)
- [ ] All file paths are relative to lesson-17/ root

---

## Reusable Patterns from Lesson 16

### Pattern 1: Deterministic Generation with Seeds
```python
import random
import json

def generate_pii_examples(count: int = 50, seed: int = 42) -> list[dict]:
    random.seed(seed)
    # ... generation logic ...
    return examples

# Reproducible across runs
examples = generate_pii_examples(count=50, seed=42)
```

### Pattern 2: Challenge Injection (from Lesson 16)
```python
# Inject challenges at target distribution
target_pii_rate = 0.3  # 30% of examples contain PII
pii_count = int(count * target_pii_rate)
# Ensure exactly 15 examples have PII (for count=50)
```

### Pattern 3: Gold Label Generation
```python
# Every example must have verification gold label
example = {
    "text": "...",
    "contains_pii": True,
    "pii_types": ["ssn", "email"],
    "expected_redacted": "..."
}
```

---

## Estimated Total Effort

| Phase | Priority | Hours | Tasks |
|-------|----------|-------|-------|
| Phase 1: P0 (Immediate) | Critical | 9h | PII examples, agent metadata, multi-agent traces |
| Phase 2: P1 (Advanced) | High | 7h | Research workflows, parameter logs |
| Phase 3: P2 (Case Studies) | Medium | 14h | Healthcare, legal, compliance |
| **TOTAL** | | **30h** | **12 data generation tasks** |

**MVP (P0 only):** 9 hours → Tutorials 1-4 complete
**Complete (P0-P2):** 30 hours → All tutorials + case studies complete

---

## Next Steps

1. **Review this document** with stakeholders (confirm data needs)
2. **Execute Phase 1 (P0)** - Generate critical data for Tutorials 1-4
3. **Validate schemas** - Ensure generated data matches implementation
4. **Write Tutorial 1** - Use P0 data for examples
5. **Iterate** - Generate P1/P2 data as tutorials progress

---

**Maintained by:** AI Evaluation Course Team
**Last Updated:** 2025-11-27
**Version:** 1.0
