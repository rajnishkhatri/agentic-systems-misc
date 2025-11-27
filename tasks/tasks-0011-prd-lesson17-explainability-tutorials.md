# Tasks: Lesson 17 - Agent Explainability Framework Tutorials

**Generated from:** [0011-prd-lesson17-explainability-tutorials.md](0011-prd-lesson17-explainability-tutorials.md)  
**Created:** 2025-11-27

---

## Relevant Files

### New Files to Create

- `lesson-17/tutorials/01_explainability_fundamentals.md` - Foundation tutorial covering the four pillars and component selection
- `lesson-17/tutorials/02_black_box_recording_debugging.md` - BlackBox Recorder tutorial with post-incident debugging workflow
- `lesson-17/tutorials/03_agentfacts_governance.md` - AgentFacts tutorial covering identity, signatures, and compliance
- `lesson-17/tutorials/04_guardrails_validation_pii.md` - GuardRails tutorial with all 7 validators and PII detection
- `lesson-17/notebooks/04_phase_logger_workflow.ipynb` - Interactive notebook demonstrating PhaseLogger component

### Existing Files to Reference

- `lesson-17/backend/explainability/black_box.py` - BlackBoxRecorder implementation (EventType, TaskPlan, ExecutionTrace)
- `lesson-17/backend/explainability/agent_facts.py` - AgentFacts and Registry implementation (Capability, Policy, signatures)
- `lesson-17/backend/explainability/guardrails.py` - GuardRails implementation (BuiltInValidators, FailAction, Constraint)
- `lesson-17/backend/explainability/phase_logger.py` - PhaseLogger implementation (WorkflowPhase, Decision, Artifact)
- `lesson-17/notebooks/01_black_box_recording_demo.ipynb` - Reference for notebook structure and patterns
- `lesson-17/notebooks/02_agent_facts_verification.ipynb` - Reference for notebook structure and patterns
- `lesson-17/notebooks/03_guardrails_validation_traces.ipynb` - Reference for notebook structure and patterns
- `lesson-17/data/workflows/invoice_processing_trace.json` - Sample data for case studies
- `lesson-17/tests/test_black_box.py` - Additional code examples (18 tests)
- `lesson-17/tests/test_agent_facts.py` - Additional code examples (26 tests)
- `lesson-17/tests/test_guardrails.py` - Additional code examples (24 tests)
- `lesson-17/tests/test_phase_logger.py` - Additional code examples (26 tests)

### Files to Update

- `lesson-17/TUTORIAL_INDEX.md` - Add new tutorials to index and learning paths

### Notes

- All code examples in tutorials must be tested before inclusion
- Follow existing notebook patterns from 01, 02, 03 notebooks
- Use realistic de-identified data for healthcare/finance examples
- Each tutorial should be <25 minutes reading time (~5000 words max)
- Notebook execution time must be <5 minutes total

---

## Tasks

- [x] 1.0 Create Tutorial 1: Explainability Fundamentals
  - [x] 1.1 Define AI agent explainability and differentiate from model interpretability (LIME, SHAP) with clear examples
  - [x] 1.2 Document the four pillars of explainability: Recording, Identity, Validation, Reasoning
  - [x] 1.3 Map each pillar to its framework component (BlackBox→Recording, AgentFacts→Identity, GuardRails→Validation, PhaseLogger→Reasoning)
  - [x] 1.4 Create Mermaid flowchart decision tree for component selection based on use case
  - [x] 1.5 Write 3+ real-world scenarios showing when to use each component (Healthcare compliance, Finance auditing, Legal discovery)
  - [x] 1.6 Add cross-links to Tutorials 2, 3, and 4 for deep-dives on each component
  - [x] 1.7 Verify reading time is <25 minutes (target ~4000 words)

- [ ] 2.0 Create Tutorial 2: BlackBox Recording for Debugging
  - [ ] 2.1 Explain aviation black box analogy and parallels to multi-agent systems (CVR/FDR mapping)
  - [ ] 2.2 Document all recordable data types: TaskPlan, AgentInfo, ParameterSubstitution, ExecutionTrace with code examples
  - [ ] 2.3 Document all 9 event types (STEP_START, STEP_END, DECISION, ERROR, CHECKPOINT, PARAMETER_CHANGE, COLLABORATOR_JOIN, COLLABORATOR_LEAVE, ROLLBACK) with use cases
  - [ ] 2.4 Create post-incident analysis workflow diagram (Mermaid sequence): export → replay → analyze
  - [ ] 2.5 Write case study: Multi-agent invoice processing cascade failure using data from `invoice_processing_trace.json`
  - [ ] 2.6 Document best practices: checkpoint frequency, rollback point placement, storage management
  - [ ] 2.7 Show integration pattern with GuardRails (validation + recording)
  - [ ] 2.8 Add cross-link to notebook `01_black_box_recording_demo.ipynb`

- [ ] 3.0 Create Tutorial 3: AgentFacts for Governance
  - [ ] 3.1 Explain why agent identity matters: multi-tenancy isolation, compliance attribution, cost tracking, model lineage
  - [ ] 3.2 Document Capability declarations: input/output schemas, cost estimation, latency SLAs, approval requirements
  - [ ] 3.3 Document Policy management: rate limits, approval workflows, time-based policies, data access controls
  - [ ] 3.4 Explain SHA256 signature verification for tamper detection with code walkthrough
  - [ ] 3.5 Create signature verification flow diagram (Mermaid flowchart)
  - [ ] 3.6 Document audit trail export formats for compliance (HIPAA/SOX structure)
  - [ ] 3.7 Write case study: Healthcare agent governance with HIPAA compliance requirements
  - [ ] 3.8 Add cross-link to notebook `02_agent_facts_verification.ipynb`

- [ ] 4.0 Create Tutorial 4: GuardRails for Validation and PII Detection
  - [ ] 4.1 Explain declarative validation philosophy vs imperative validation with comparison examples
  - [ ] 4.2 Document all 7 built-in validators with code examples: length_check, regex_match, no_pii, confidence_range, required_fields, json_parseable, value_in_list
  - [ ] 4.3 Provide code example for custom validator creation with domain-specific use case
  - [ ] 4.4 Document all 5 failure actions (REJECT, FIX, ESCALATE, LOG, RETRY) with decision matrix table
  - [ ] 4.5 Explain validation traces structure and how to use them for debugging
  - [ ] 4.6 Write case study: PII redaction in customer service chatbot (SSN, credit card, email, phone patterns)
  - [ ] 4.7 Test all PII detection patterns with sample data from `pii_examples_50.json`
  - [ ] 4.8 Add cross-link to notebook `03_guardrails_validation_traces.ipynb`

- [ ] 5.0 Create Phase Logger Notebook (04_phase_logger_workflow.ipynb)
  - [ ] 5.1 Create setup cell with imports and PhaseLogger initialization
  - [ ] 5.2 Demonstrate phase lifecycle: start_phase → log_decision → log_artifact → end_phase
  - [ ] 5.3 Show at least 4 of 7 active workflow phases (PLANNING, LITERATURE_REVIEW, DATA_COLLECTION, EXECUTION, EXPERIMENT, VALIDATION, REPORTING - excludes terminal states COMPLETED/FAILED)
  - [ ] 5.4 Demonstrate decision logging with alternatives_considered and selected_because reasoning
  - [ ] 5.5 Demonstrate artifact tracking with metadata (type, path, phase association)
  - [ ] 5.6 Show error handling: log recoverable errors vs fatal errors
  - [ ] 5.7 Generate and display Mermaid workflow diagram using visualize_workflow()
  - [ ] 5.8 Display summary statistics using get_phase_summary() (phases, decisions, artifacts, errors, duration)
  - [ ] 5.9 Add markdown explanations between all code cells
  - [ ] 5.10 Verify total execution time is <5 minutes

- [ ] 6.0 Update TUTORIAL_INDEX.md and Documentation
  - [ ] 6.1 Add all 4 tutorial entries to the Tutorials section with descriptions
  - [ ] 6.2 Update Learning Path section with tutorial progression (Beginner → Intermediate → Advanced)
  - [ ] 6.3 Add Phase Logger notebook to Interactive Notebooks table
  - [ ] 6.4 Verify all internal cross-links between tutorials work correctly
  - [ ] 6.5 Update README.md if needed to reference new tutorial content

