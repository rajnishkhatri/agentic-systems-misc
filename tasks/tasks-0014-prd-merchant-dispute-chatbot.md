# Task List: Merchant Dispute Resolution Agentic Chatbot

**Source PRD:** [0014-prd-merchant-dispute-chatbot.md](./0014-prd-merchant-dispute-chatbot.md)
**Generated:** 2025-12-07
**Strategy:** Decomposition + Working Backward (Pólya-based)

---

## Relevant Files

### Shared Infrastructure (Pre-existing)
- `utils/llm_service.py` - LiteLLM wrapper with LLMService class (singleton via `get_default_service()`)
- `tests/utils/test_llm_service.py` - 33 TDD tests for LLMService (all passing)
- `env.example` - Environment variables including LLM_DEFAULT_MODEL, LLM_JUDGE_MODEL, LLM_ROUTING_MODEL, LLM_CACHE_TYPE

### Phase 0: Design & Architecture
- `lesson-18/dispute-chatbot/design/00_system_context.md` - System context diagram
- `lesson-18/dispute-chatbot/design/01_component_architecture.md` - Component breakdown
- `lesson-18/dispute-chatbot/design/02_domain_model.md` - 7 domain entities
- `lesson-18/dispute-chatbot/design/02_domain_model.mmd` - Entity relationship diagram
- `lesson-18/dispute-chatbot/design/03_sequence_diagrams/*.mmd` - 5 workflow diagrams
- `lesson-18/dispute-chatbot/design/04_api_specifications/*.yaml` - OpenAPI specs
- `lesson-18/dispute-chatbot/design/05_data_architecture.md` - Storage and retention
- `lesson-18/dispute-chatbot/design/06_security_architecture.md` - PCI-DSS mapping
- `lesson-18/dispute-chatbot/design/07_observability_strategy.md` - Metrics and logging
- `lesson-18/dispute-chatbot/design/ADRs/ADR-001.md` through `ADR-006.md` - Architecture decisions
- `lesson-18/dispute-chatbot/spikes/SPIKE-001_vrol_schema/` - VROL schema analysis
- `lesson-18/dispute-chatbot/spikes/SPIKE-002_judge_latency/` - Judge benchmarks
- `lesson-18/dispute-chatbot/spikes/SPIKE-003_ce3_matching/` - CE 3.0 prototype
- `lesson-18/dispute-chatbot/spikes/SPIKE-004_pii_detection/` - PII validation
- `lesson-18/dispute-chatbot/spikes/SPIKE-005_state_recovery/` - State recovery test

### Phase 0.5: Chainlit UI Foundation
- `lesson-18/dispute-chatbot/app.py` - Chainlit entry point
- `lesson-18/dispute-chatbot/chainlit_phases.py` - Phase step wrappers
- `lesson-18/dispute-chatbot/chainlit_tools.py` - Tool visualization
- `lesson-18/dispute-chatbot/chainlit_explainability.py` - 4-pillar sidebar
- `lesson-18/dispute-chatbot/.chainlit/config.toml` - UI configuration
- `lesson-18/dispute-chatbot/public/dispute_theme.css` - Custom styling
- `lesson-18/dispute-chatbot/tests/test_chainlit_ui.py` - UI tests

### Phase 1: Synthetic Data & Evals
- `lesson-18/dispute-chatbot/synthetic_data/schemas.py` - Pydantic schemas
- `lesson-18/dispute-chatbot/synthetic_data/phase1/disputes/*.json` - 500 dispute scenarios
- `lesson-18/dispute-chatbot/synthetic_data/phase1/evidence/*.json` - Evidence packages
- `lesson-18/dispute-chatbot/synthetic_data/phase1/conversations/*.json` - Dialogue data
- `lesson-18/dispute-chatbot/synthetic_data/phase1/golden_set/*.json` - Human-labeled ground truth
- `lesson-18/dispute-chatbot/evals/phase1/judge_config.yaml` - Judge configuration
- `lesson-18/dispute-chatbot/evals/phase1/prompts/*.j2` - Judge templates
- `lesson-18/dispute-chatbot/evals/phase1/run_judges.py` - Judge runner script (FabricationDetection, EvidenceQuality, DisputeValidity, GuardRails)
- `lesson-18/dispute-chatbot/evals/phase1/calculate_irr.py` - Inter-rater reliability (κ) calculator
- `lesson-18/dispute-chatbot/evals/phase1/results/*.json` - Judge run results

### Phase 1: Qualitative Analysis (Failure Taxonomy)
- `lesson-18/dispute-chatbot/qualitative/phase1/open_codes.csv` - Open coding labels from 100+ traces
- `lesson-18/dispute-chatbot/qualitative/phase1/axial_categories.md` - 5 failure mode categories
- `lesson-18/dispute-chatbot/qualitative/phase1/failure_taxonomy.md` - Full taxonomy with examples, severity, red flags
- `lesson-18/dispute-chatbot/qualitative/phase1/judge_mapping.md` - Failure mode → Judge mapping with thresholds
- `lesson-18/dispute-chatbot/qualitative/phase1/saturation_log.md` - Saturation evidence, κ = 0.831 results
- `lesson-18/dispute-chatbot/qualitative/phase1/irr_sample.csv` - 20 traces with independent rater labels
- `lesson-18/dispute-chatbot/qualitative/phase1/judge_revalidation_checklist.md` - Judge validation results

### Phase 1: Backend Implementation
- `lesson-18/dispute-chatbot/backend/orchestrators/dispute_state.py` - State enum
- `lesson-18/dispute-chatbot/backend/orchestrators/transitions.py` - Transition rules
- `lesson-18/dispute-chatbot/backend/orchestrators/dispute_orchestrator.py` - State machine
- `lesson-18/dispute-chatbot/backend/orchestrators/evidence_gatherer.py` - Hierarchical gatherer
- `lesson-18/dispute-chatbot/backend/phases/classify.py` - CLASSIFY handler
- `lesson-18/dispute-chatbot/backend/phases/gather_evidence.py` - GATHER handler
- `lesson-18/dispute-chatbot/backend/phases/validate.py` - VALIDATE handler
- `lesson-18/dispute-chatbot/backend/phases/submit.py` - SUBMIT handler
- `lesson-18/dispute-chatbot/backend/phases/monitor.py` - MONITOR handler
- `lesson-18/dispute-chatbot/backend/agents/evidence_planner.py` - Planner agent
- `lesson-18/dispute-chatbot/backend/agents/transaction_specialist.py` - CE 3.0 specialist
- `lesson-18/dispute-chatbot/backend/agents/shipping_specialist.py` - Shipping specialist
- `lesson-18/dispute-chatbot/backend/agents/customer_specialist.py` - Customer specialist
- `lesson-18/dispute-chatbot/backend/judges/evidence_quality.py` - Quality judge
- `lesson-18/dispute-chatbot/backend/judges/fabrication_detection.py` - Fabrication judge
- `lesson-18/dispute-chatbot/backend/judges/dispute_validity.py` - Validity judge
- `lesson-18/dispute-chatbot/backend/judges/judge_panel.py` - Panel orchestrator
- `lesson-18/dispute-chatbot/backend/adapters/visa_vrol.py` - VROL translator
- `lesson-18/dispute-chatbot/backend/adapters/visa_mock.py` - Mock API
- `lesson-18/dispute-chatbot/backend/schemas/dispute_schema.py` - Internal schema

### Phase 1: Tests
- `lesson-18/dispute-chatbot/tests/test_dispute_orchestrator.py` - State machine tests
- `lesson-18/dispute-chatbot/tests/test_evidence_specialists.py` - Specialist tests
- `lesson-18/dispute-chatbot/tests/test_evidence_gatherer.py` - Gatherer tests
- `lesson-18/dispute-chatbot/tests/test_judges.py` - Judge tests
- `lesson-18/dispute-chatbot/tests/test_explainability.py` - Explainability tests
- `lesson-18/dispute-chatbot/tests/test_visa_adapter.py` - VROL translation tests
- `lesson-18/dispute-chatbot/tests/test_submission_flow.py` - E2E submission tests

---

## Notes

- **TDD Required**: All implementation tasks follow RED → GREEN → REFACTOR cycle
- **Gate Dependencies**: Phase 0 gates (0.1-0.6) must pass before Phase 0.5 begins; Phase 0.5 gate before Phase 1
- **Lesson Dependencies**: Import from lesson-16 (orchestrators), lesson-17 (explainability), lesson-10 (judges)
- **LLMService (MANDATORY)**: All LLM calls MUST use `utils/llm_service.py` via `get_default_service()` singleton
  - **DO NOT** use direct `from litellm import completion` (see PRD Section 9 Anti-Patterns)
  - **DO NOT** use direct `from openai import OpenAI` (vendor lock-in)
  - Judges: Use `complete_structured()` with Pydantic models for type-safe responses
  - Specialists: Use `complete()` with `default_model` for evidence analysis
  - Classifiers/Planners: Use `complete()` with `routing_model` for cost efficiency
  - Cost tracking: Instantiate `CostTracker` per session for monitoring
  - Benefits: Provider-agnostic, caching, cost tracking, consistent retry/timeout logic
- **Test Commands**: `pytest lesson-18/dispute-chatbot/tests/ -v --cov`
- **UI Command**: `chainlit run lesson-18/dispute-chatbot/app.py`

---

## Assumptions Made

- **Visa VROL API**: Using mock implementation for Phase 1; real integration deferred to Phase 3
- **LLM Provider**: Using LiteLLM via `utils/llm_service.py` with configurable models:
  - Default: `LLM_DEFAULT_MODEL=gpt-4o` for specialists
  - Judges: `LLM_JUDGE_MODEL=gpt-4o` for structured evaluation
  - Routing: `LLM_ROUTING_MODEL=gpt-4o-mini` for cheap classification
  - A/B testing: Provider failover via LiteLLM's unified API
- **Caching**: `LLM_CACHE_TYPE=disk` for development cost savings; `redis` for production
- **Golden Set Labeling**: Assumes access to 3 annotators for inter-rater reliability (κ > 0.8). Annotators should have dispute domain expertise (financial services or payment operations background). If 3 annotators unavailable, minimum 2 annotators with κ > 0.75 is acceptable for Phase 1 MVP.
- **Qualitative Analysis**: Domain expert availability required for saturation validation (Gate 0.7, Gate 6.17.6). Expert should have ≥2 years dispute resolution experience.
- **Redis Availability**: State recovery assumes Redis is configured and available
- **Chainlit Version**: Assumes Chainlit ≥1.0 with Steps API support

---

## Tasks

### Phase 0: Design & Architecture Foundation (Weeks 0-2)

- [ ] 1.0 Phase 0: Domain Model & Architecture Foundation (Week 0-1)
  - [x] 1.1 Create `lesson-18/dispute-chatbot/design/` directory structure
        Input: PRD Section 13 structure | Output: Directory tree | Verify: `ls -R` shows all folders
  - [x] 1.2 Document Domain Model with 7 entities (Dispute, Evidence, Merchant, Judge, Submission, AuditLog, Conversation)
        Input: PRD Section 13 entity table | Output: `design/02_domain_model.md` | Verify: All relationships and business rules captured
  - [x] 1.3 Create Entity Relationship Diagram in Mermaid
        Input: Domain model | Output: `design/02_domain_model.mmd` | Verify: Renders correctly, matches PRD diagram
  - [x] 1.4 Document System Context showing chatbot in merchant ecosystem
        Input: PRD integration map | Output: `design/00_system_context.md` | Verify: External dependencies listed
  - [x] 1.5 Create Component Architecture with responsibility breakdown
        Input: PRD Section 9 architecture | Output: `design/01_component_architecture.md` | Verify: All 5 major components documented
  - [ ] 1.6 **Gate 0.1 Validation**: Domain model reviewed by domain expert
        Input: All design docs | Output: Gate sign-off | Verify: Checklist in PRD Section 13 complete

- [ ] 2.0 Phase 0: API Contracts & Sequence Diagrams (Week 1)
  - [x] 2.1 Define OpenAPI spec for 4 MCP tools (classify_dispute, gather_evidence, validate_evidence, submit_dispute)
        Input: PRD FR-2 | Output: `design/04_api_specifications/mcp_tools.yaml` | Verify: Valid OpenAPI 3.0, examples included
  - [x] 2.2 Define internal event schemas between components
        Input: Component architecture | Output: `design/04_api_specifications/internal_events.yaml` | Verify: All state transitions covered
  - [x] 2.3 Document Visa VROL request/response formats
        Input: SPIKE-001 findings | Output: `design/04_api_specifications/network_payloads.yaml` | Verify: Covers fraud 10.4 and PNR 13.1
  - [x] 2.4 Create conversation protocol schema (turn structure, message format)
        Input: PRD Section 7 conversation flow | Output: `design/04_api_specifications/conversation_protocol.yaml` | Verify: 5-turn flow documented
  - [x] 2.5 Create sequence diagram: Happy path Fraud 10.4
        Input: PRD workflow | Output: `design/03_sequence_diagrams/happy_path_fraud_10.4.mmd` | Verify: All 5 phases shown
  - [x] 2.6 Create sequence diagram: Happy path PNR 13.1
        Input: PRD workflow | Output: `design/03_sequence_diagrams/happy_path_pnr_13.1.mmd` | Verify: Shipping evidence flow included
  - [x] 2.7 Create sequence diagram: Error recovery (timeout, judge failure, retry)
        Input: PRD Section 7 error states | Output: `design/03_sequence_diagrams/error_recovery.mmd` | Verify: Exponential backoff shown
  - [x] 2.8 Create sequence diagram: Escalation flow (human handoff)
        Input: PRD escalation requirements | Output: `design/03_sequence_diagrams/escalation_flow.mmd` | Verify: Context preservation shown
  - [x] 2.9 Create sequence diagram: CE 3.0 qualification logic
        Input: PRD CE 3.0 requirements | Output: `design/03_sequence_diagrams/ce3_qualification.mmd` | Verify: Prior transaction matching shown
  - [ ] 2.10 **Gate 0.2 Validation**: API contracts reviewed by tech lead + frontend consumer
        Input: All API specs | Output: Gate sign-off | Verify: No ambiguity, examples provided

- [ ] 3.0 Phase 0: Risk Mitigation Spikes (Week 2)
  - [x] 3.1 SPIKE-001: Parse 10 real/mock VROL examples, validate schema assumptions
        Input: VROL documentation | Output: `spikes/SPIKE-001_vrol_schema/README.md` | Verify: Schema covers 95% of fraud/PNR fields
  - [x] 3.2 SPIKE-002: Benchmark 3 judge prompts with timing under load
        Input: Judge prompt drafts | Output: `spikes/SPIKE-002_judge_latency/benchmark_results.json` | Verify: All judges <800ms P95 at 10 QPS
  - [x] 3.3 SPIKE-003: Prototype CE 3.0 transaction matching algorithm
        Input: Transaction data schema | Output: `spikes/SPIKE-003_ce3_matching/` | Verify: >95% match rate on 50 test cases
  - [x] 3.4 SPIKE-004: Test GuardRails PII detection on dispute domain vocabulary
        Input: Dispute-specific terms | Output: `spikes/SPIKE-004_pii_detection/README.md` | Verify: <5% false positive rate
  - [x] 3.5 SPIKE-005: Test state machine recovery after container restart
        Input: Redis state storage | Output: `spikes/SPIKE-005_state_recovery/README.md` | Verify: 100% state recovery
  - [x] 3.6 Document all 6 ADRs (State Machine, Sync Judges, Evidence Storage, Network Translation, Session Storage, Explainability Storage)
        Input: PRD ADR table | Output: `design/ADRs/ADR-001.md` through `ADR-006.md` | Verify: Decision, rationale, trade-offs documented
  - [x] 3.7 **Gate 0.3 & 0.4 Validation**: Architecture approved, all spikes completed
        Input: ADRs + spike results | Output: Gate sign-off | Verify: No blocking issues

- [ ] 4.0 Phase 0: Security & Stakeholder Sign-off (Week 2)
  - [ ] 4.1 Document Security Architecture (PCI-DSS v4.0 mapping, PII handling)
        Input: PRD NFR-1 | Output: `design/06_security_architecture.md` | Verify: All PCI requirements mapped
  - [ ] 4.2 Document Data Architecture (storage, data flows, retention policies)
        Input: PRD data stores | Output: `design/05_data_architecture.md` | Verify: 90-day BlackBox, 1-year PhaseLogger retention
  - [ ] 4.3 Document Observability Strategy (metrics, logging, alerting, dashboards)
        Input: PRD NFR requirements | Output: `design/07_observability_strategy.md` | Verify: All success metrics measurable
  - [ ] 4.4 **Gate 0.5 Validation**: Security review passed
        Input: Security architecture | Output: Gate sign-off | Verify: PCI compliance validated
  - [ ] 4.5 **Gate 0.6 Validation**: Stakeholder sign-off obtained
        Input: All Phase 0 artifacts | Output: Sign-off document | Verify: Product owner approval

- [ ] 4.6 Phase 0.7: Domain Open Coding (Week 2)
  - [ ] 4.6.1 Review 30+ domain artifacts with open coding (8-10 hours)
        Input: Dispute case studies, regulatory docs, CE 3.0 docs | Output: `qualitative/phase0/open_codes.csv` | Verify: Descriptive labels, no preconceived categories
  - [ ] 4.6.2 Perform axial coding into 5-7 domain categories
        Input: Open codes | Output: `qualitative/phase0/axial_categories.md` | Verify: Mutual exclusivity, collective exhaustion
  - [ ] 4.6.3 Document domain taxonomy with relationships
        Input: Axial categories | Output: `qualitative/phase0/domain_taxonomy.md` | Verify: Covers Evidence Authenticity, Timeline Compliance, CE 3.0 Qualification, Network Patterns
  - [ ] 4.6.4 Document saturation log and validate with domain expert
        Input: Open coding sessions | Output: `qualitative/phase0/saturation_log.md` | Verify: <1 new concept per 10 docs OR escalate after 50 docs
  - [ ] 4.6.5 Document synthetic data implications
        Input: Domain taxonomy | Output: `qualitative/phase0/synthetic_data_implications.md` | Verify: Maps taxonomy to data generation requirements
  - [ ] 4.6.6 **Gate 0.7 Validation**: Domain taxonomy covers 80%+ patterns
        Input: All qualitative artifacts | Output: Gate sign-off | Verify: Domain expert validates taxonomy completeness

---

### Phase 0.5: Chainlit UI Foundation (Week 2.5-3)

- [ ] 5.0 Phase 0.5: Chainlit UI Foundation (Week 2.5-3)
  - [x] 5.1 Create `lesson-18/dispute-chatbot/` directory structure with app.py entry point
        Input: PRD Section 13 file structure | Output: Directory with app.py, .chainlit/ | Verify: `chainlit run app.py` starts without errors
  - [x] 5.2 Configure `.chainlit/config.toml` with UI settings (theme, features)
        Input: Chainlit documentation | Output: `.chainlit/config.toml` | Verify: Custom theme loads
  - [x] 5.3 Implement `@cl.on_chat_start` handler with welcome message and session initialization
        Input: PRD conversation flow Turn 1 | Output: `app.py` handler | Verify: Welcome message displays on chat start
  - [x] 5.4 Implement `@cl.on_message` router to State Machine Orchestrator (mock)
        Input: API contracts | Output: `app.py` handler | Verify: Messages route correctly
  - [x] 5.5 Create `chainlit_phases.py` with phase step wrappers using `@cl.step` decorator
        Input: PRD 5 phases | Output: `chainlit_phases.py` | Verify: Mock phase steps render correctly (CLASSIFY → MONITOR)
  - [x] 5.6 Create `chainlit_tools.py` for tool call visualization (4 MCP tools)
        Input: MCP tool specs | Output: `chainlit_tools.py` | Verify: Tool calls display with input/output
  - [x] 5.7 Create `chainlit_explainability.py` for 4-pillar sidebar display
        Input: Explainability schemas | Output: `chainlit_explainability.py` | Verify: Placeholder data renders in sidebar
  - [x] 5.8 Add custom CSS for dispute branding in `public/dispute_theme.css`
        Input: UI requirements | Output: `public/dispute_theme.css` | Verify: Theme applies correctly
  - [x] 5.9 Write tests for Chainlit components
        Input: UI components | Output: `tests/test_chainlit_ui.py` | Verify: All UI handlers covered
  - [x] 5.10 **Phase 0.5 Gate**: UI foundation validated
        Input: All UI components | Output: Gate checklist | Verify: All 5 gate items from PRD pass

---

### Phase 1: Core MVP (Weeks 3-10)

- [x] 6.0 Phase 1: Synthetic Data Generation & Eval Setup (Week 3)
  - [x] 6.1 Create Pydantic schemas for SyntheticDispute and SyntheticEvidence
        Input: PRD Section 12 schemas | Output: `synthetic_data/schemas.py` | Verify: Schema validation passes
  - [x] 6.2 Generate 200 fraud (10.4) dispute scenarios using Faker
        Input: Dispute schema | Output: `synthetic_data/phase1/disputes/fraud_10.4_cases.json` | Verify: Zero real PII, schema valid
  - [x] 6.3 Generate 200 product not received (13.1) dispute scenarios
        Input: Dispute schema | Output: `synthetic_data/phase1/disputes/pnr_13.1_cases.json` | Verify: Includes shipping data
  - [x] 6.4 Generate 100 adversarial/boundary edge cases
        Input: Edge case checklist | Output: `synthetic_data/phase1/disputes/edge_cases.json` | Verify: 20% of total dataset
  - [x] 6.5 Generate CE 3.0 transaction histories (2-5 prior undisputed txns per dispute)
        Input: Transaction schema | Output: `synthetic_data/phase1/evidence/transaction_histories.json` | Verify: Matches dispute merchant
  - [x] 6.6 Generate shipping records (FedEx/UPS tracking, POD)
        Input: Shipping schema | Output: `synthetic_data/phase1/evidence/shipping_records.json` | Verify: Covers PNR cases
  - [x] 6.7 Generate customer profiles (device fingerprint, IP, email match)
        Input: Customer schema | Output: `synthetic_data/phase1/evidence/customer_profiles.json` | Verify: Faker-generated
  - [x] 6.8 Generate incomplete evidence packages for gap detection testing
        Input: Evidence schema | Output: `synthetic_data/phase1/evidence/incomplete_evidence.json` | Verify: Various missing fields
  - [x] 6.9 Generate 50 happy path conversation dialogues
        Input: PRD conversation flow | Output: `synthetic_data/phase1/conversations/happy_path_dialogues.json` | Verify: 5-turn format
  - [x] 6.10 Generate 30 error recovery and 20 escalation dialogues
        Input: PRD error states | Output: `synthetic_data/phase1/conversations/` | Verify: Covers all error types
  - [x] 6.11 Create human-labeled golden set: 100 classification labels
        Input: Disputes | Output: `synthetic_data/phase1/golden_set/classification_labels.json` | Verify: 3 annotators, κ > 0.8
  - [x] 6.12 Create human-labeled golden set: 100 evidence quality scores
        Input: Evidence packages | Output: `synthetic_data/phase1/golden_set/evidence_quality_scores.json` | Verify: κ > 0.8
  - [x] 6.13 Create known fabrication examples for hallucination detection
        Input: Hallucination patterns | Output: `synthetic_data/phase1/golden_set/fabrication_examples.json` | Verify: Clear ground truth
  - [x] 6.14 Configure LLM judges with calibration (evidence_quality, fabrication_detection, dispute_validity)
        Input: PRD FR-4 | Output: `evals/phase1/judge_config.yaml` | Verify: Thresholds match PRD (0.8, 0.95, 0.7)
  - [x] 6.15 Write judge prompt templates (Jinja2)
        Input: Judge requirements | Output: `evals/phase1/prompts/` | Verify: All 3 judges templated
  - [x] 6.16 **Phase 1 Data Gate**: Synthetic data validated, judges calibrated
        Input: All data + judges | Output: Gate checklist | Verify: 500 disputes, κ > 0.8, >85% judge agreement

- [x] 6.17 Step 0.5: Failure Taxonomy Development (Week 3-4) ✅ COMPLETE
  - [x] 6.17.1 Open coding on 50+ synthetic conversation traces (3-4 hours)
        Input: Synthetic conversations | Output: `qualitative/phase1/open_codes.csv` | Verify: Descriptive labels (hallucinated_transaction, deadline_arithmetic_error, etc.)
        **DONE:** 100+ traces reviewed, 6 patterns identified
  - [x] 6.17.2 Axial coding into 5-7 failure mode categories
        Input: Open codes | Output: `qualitative/phase1/axial_categories.md` | Verify: Evidence Fabrication, Compliance Violations, Classification Errors, Evidence Quality Gaps, UX Failures
        **DONE:** 5 categories documented with relationships
  - [x] 6.17.3 Document failure taxonomy with examples
        Input: Axial categories | Output: `qualitative/phase1/failure_taxonomy.md` | Verify: Each mode has definition + 2 examples + severity + blocking status
        **DONE:** 5 failure modes with red flags, examples, severity, judge mapping
  - [x] 6.17.4 Map failure modes to LLM judges with thresholds
        Input: Failure taxonomy | Output: `qualitative/phase1/judge_mapping.md` | Verify: Fabrication→0.95, Compliance→Pass/Fail, Classification→0.7, Quality→0.8
        **DONE:** All 4 judges mapped with thresholds and blocking behavior
  - [x] 6.17.5 Document saturation log
        Input: Open coding sessions | Output: `qualitative/phase1/saturation_log.md` | Verify: <1 new pattern per 20 traces OR escalate after 100 traces
        **DONE:** Saturation reached, κ = 0.831 (almost perfect agreement)
  - [x] 6.17.6 **Failure Taxonomy Gate**: All failure modes mapped to judges ✅ PASSED
        Input: All qualitative artifacts | Output: Gate sign-off | Verify: Team can classify new traces without ambiguity
        **DONE:** κ = 0.831 exceeds 0.75 threshold, all judges validated via `evals/phase1/run_judges.py`

- [ ] 7.0 Phase 1: State Machine Orchestrator Implementation (Week 4-5)
  - [x] 7.1 Create DisputeState enum with 5 states (CLASSIFY, GATHER_EVIDENCE, VALIDATE, SUBMIT, MONITOR)
        Input: PRD FR-1 | Output: `backend/orchestrators/dispute_state.py` | Verify: All states with entry/exit criteria
  - [x] 7.2 Define state transition rules with entry/exit criteria
        Input: PRD state table | Output: `backend/orchestrators/transitions.py` | Verify: All transitions documented
  - [x] 7.3 Implement DisputeStateMachine extending lesson-16 StateMachineOrchestrator
        Input: lesson-16 base class | Output: `backend/orchestrators/dispute_orchestrator.py` | Verify: Inherits correctly
  - [x] 7.4 Implement CLASSIFY phase handler using `LLMService.complete()` with routing_model (reason code extraction, deadline calculation)
        Input: API contract | Output: `backend/phases/classify.py` | Verify: Handles 10.4 and 13.1, uses `complete(model=service.routing_model)` for cost efficiency
  - [x] 7.5 Implement GATHER_EVIDENCE phase handler (delegates to hierarchical gatherer)
        Input: API contract | Output: `backend/phases/gather_evidence.py` | Verify: Calls specialist agents
  - [x] 7.6 Implement VALIDATE phase handler (runs 3 judges)
        Input: API contract | Output: `backend/phases/validate.py` | Verify: Blocking judges gate transition
  - [x] 7.7 Implement SUBMIT phase handler (calls network adapter)
        Input: API contract | Output: `backend/phases/submit.py` | Verify: Returns case ID
  - [x] 7.8 Implement MONITOR phase handler (polls for resolution)
        Input: API contract | Output: `backend/phases/monitor.py` | Verify: Tracks won/lost status
  - [ ] 7.9 Implement state recovery from Redis after restart
        Input: SPIKE-005 findings | Output: Recovery logic | Verify: 100% state recovery
  - [x] 7.10 Write comprehensive tests for state machine (TDD)
        Input: State machine | Output: `tests/test_dispute_orchestrator.py` | Verify: All transitions covered, 90%+ coverage
  - [x] 7.11 Integrate with Chainlit phase steps
        Input: chainlit_phases.py | Output: Updated UI | Verify: Phase transitions visible in UI

- [ ] 8.0 Phase 1: Hierarchical Evidence Gathering (Week 5-6)
  - [ ] 8.1 Implement EvidencePlannerAgent using `LLMService.complete()` with routing_model
        Input: lesson-16 hierarchical pattern | Output: `backend/agents/evidence_planner.py` | Verify: Uses `get_default_service().complete(model=service.routing_model)` for cost efficiency
  - [ ] 8.2 Implement TransactionSpecialist using `LLMService.complete()` with default_model
        Input: CE 3.0 requirements | Output: `backend/agents/transaction_specialist.py` | Verify: Returns 2-5 qualifying txns, uses `complete()` for analysis
  - [ ] 8.3 Implement ShippingSpecialist using `LLMService.complete()` with default_model
        Input: Shipping data sources | Output: `backend/agents/shipping_specialist.py` | Verify: Handles FedEx/UPS, uses `complete()` for extraction
  - [ ] 8.4 Implement CustomerHistorySpecialist using `LLMService.complete()` with default_model
        Input: Customer data sources | Output: `backend/agents/customer_specialist.py` | Verify: Returns matching signals, uses `complete()` for pattern matching
  - [ ] 8.5 Implement HierarchicalEvidenceGatherer using ThreadPoolExecutor for parallel execution
        Input: Specialists | Output: `backend/orchestrators/evidence_gatherer.py` | Verify: Parallel execution confirmed, shared LLMService singleton
  - [ ] 8.6 Implement evidence package assembly with completeness scoring
        Input: Specialist outputs | Output: Evidence package | Verify: All required fields for reason code populated
  - [ ] 8.7 Implement gap detection and merchant prompting for missing evidence
        Input: Incomplete package | Output: Gap list + prompt | Verify: Lists specific missing fields
  - [ ] 8.8 Write tests for all specialists (TDD) with mocked LLMService
        Input: Specialists | Output: `tests/test_evidence_specialists.py` | Verify: Each specialist covered, mock `complete()` calls
  - [ ] 8.9 Write tests for evidence gatherer (TDD)
        Input: Gatherer | Output: `tests/test_evidence_gatherer.py` | Verify: Parallel execution, assembly tested
  - [ ] 8.10 Integrate with Chainlit nested steps for real-time progress
        Input: UI components | Output: Updated UI | Verify: Specialist progress visible

- [ ] 9.0 Phase 1: LLM Judge Panel Implementation (Week 6-7)
  - [ ] 9.1 Define Pydantic models for judge responses (JudgeScore, EvidenceQualityResult, FabricationResult)
        Input: PRD FR-4 | Output: `backend/judges/schemas.py` | Verify: Type-safe score, reasoning, evidence_gaps fields
  - [ ] 9.2 Implement EvidenceQualityJudge using `LLMService.complete_structured()` (threshold 0.8, blocking)
        Input: Judge config, schemas.py | Output: `backend/judges/evidence_quality.py` | Verify: Uses `get_default_service().complete_structured()` with judge_model
  - [ ] 9.3 Implement FabricationDetectionJudge using `LLMService.complete_structured()` (threshold 0.95, blocking)
        Input: Judge config, schemas.py | Output: `backend/judges/fabrication_detection.py` | Verify: >99% recall on golden set, Pydantic response
  - [ ] 9.4 Implement DisputeValidityJudge using `LLMService.complete_structured()` (threshold 0.7, non-blocking warning)
        Input: Judge config, schemas.py | Output: `backend/judges/dispute_validity.py` | Verify: Returns warning, not block
  - [ ] 9.5 Implement JudgePanel orchestrator with CostTracker integration
        Input: Individual judges | Output: `backend/judges/judge_panel.py` | Verify: Tracks costs per judge, respects blocking behavior
  - [ ] 9.6 Implement judge latency optimization (<800ms P95)
        Input: SPIKE-002 findings | Output: Optimized prompts | Verify: Benchmark confirms <800ms
  - [ ] 9.7 Calibrate judges against golden set (κ > 0.8)
        Input: Golden set | Output: Calibration report | Verify: All judges meet threshold
  - [ ] 9.8 Implement human escalation workflow when blocking judge fails
        Input: PRD escalation flow | Output: Escalation handler | Verify: Creates ticket with context
  - [ ] 9.9 Write tests for each judge (TDD) with mocked LLMService
        Input: Judges | Output: `tests/test_judges.py` | Verify: Each judge covered, mock `complete_structured()` calls
  - [ ] 9.10 Integrate with Chainlit real-time score streaming
        Input: UI components | Output: Updated UI | Verify: Scores stream during validation

- [ ] 10.0 Phase 1: Explainability Integration (Week 7-8)
  - [ ] 10.1 Integrate BlackBoxRecorder for all agent calls (input/output with timing)
        Input: lesson-17 BlackBoxRecorder | Output: Recording hooks | Verify: All calls captured to S3
  - [ ] 10.2 Integrate AgentFacts for agent version/capability verification
        Input: lesson-17 AgentFacts | Output: Agent metadata | Verify: Model version, prompt hash captured
  - [ ] 10.3 Integrate GuardRails for PCI compliance and PII detection
        Input: lesson-17 GuardRails | Output: Validation hooks | Verify: PII scan on all inputs/outputs
  - [ ] 10.4 Integrate PhaseLogger for decision rationale at each state transition
        Input: lesson-17 PhaseLogger | Output: Logging hooks | Verify: Rationale captured for each phase
  - [ ] 10.5 Implement audit log export in JSON format
        Input: Explainability data | Output: Export function | Verify: Compliant format for auditors
  - [ ] 10.6 Create explainability dashboard in Chainlit sidebar
        Input: chainlit_explainability.py | Output: Live sidebar | Verify: All 4 pillars visible
  - [ ] 10.7 Write tests for explainability integration
        Input: Explainability components | Output: `tests/test_explainability.py` | Verify: 100% coverage requirement met
  - [ ] 10.8 Validate 100% audit completeness for state transitions
        Input: Test runs | Output: Completeness report | Verify: No gaps in logging

- [ ] 11.0 Phase 1: Visa Network Adapter & Submission (Week 8-9)
  - [ ] 11.1 Implement internal dispute schema (unified format)
        Input: Domain model | Output: `backend/schemas/dispute_schema.py` | Verify: Covers all evidence fields
  - [ ] 11.2 Implement Visa VROL translator (internal → VROL format)
        Input: SPIKE-001 schema | Output: `backend/adapters/visa_vrol.py` | Verify: All field mappings correct
  - [ ] 11.3 Implement mock Visa API client for testing
        Input: VROL format | Output: `backend/adapters/visa_mock.py` | Verify: Simulates real responses
  - [ ] 11.4 Implement submission retry logic with exponential backoff
        Input: PRD error states | Output: Retry handler | Verify: 1s, 2s, 4s backoff
  - [ ] 11.5 Implement submission confirmation and case ID extraction
        Input: VROL response | Output: Submission result | Verify: Case ID returned
  - [ ] 11.6 Implement deadline alert system (7, 3, 1 day notifications)
        Input: PRD notification requirements | Output: Alert handler | Verify: Alerts trigger correctly
  - [ ] 11.7 Write tests for VROL translation
        Input: Translator | Output: `tests/test_visa_adapter.py` | Verify: All field mappings tested
  - [ ] 11.8 Write integration tests for submission flow
        Input: Full flow | Output: `tests/test_submission_flow.py` | Verify: End-to-end with mock API

- [ ] 12.0 Phase 1: Integration Testing & Validation (Week 9-10)
  - [ ] 12.1 Run all 500 synthetic disputes through full pipeline
        Input: Synthetic data | Output: Test results | Verify: 100% process without error
  - [ ] 12.2 Validate judge calibration against golden set
        Input: Golden set | Output: Calibration report | Verify: κ > 0.8 for all judges
  - [ ] 12.3 Validate evidence quality judge accuracy (>90% precision/recall)
        Input: Golden set | Output: Accuracy report | Verify: Meets threshold
  - [ ] 12.4 Validate fabrication detection recall (>99%)
        Input: Fabrication examples | Output: Recall report | Verify: Catches all known patterns
  - [ ] 12.5 Validate explainability coverage (100% BlackBox traces)
        Input: Test runs | Output: Coverage report | Verify: All agent calls have traces
  - [ ] 12.6 Validate PhaseLogger captures every state transition
        Input: Test runs | Output: Transition log | Verify: 100% transition logging
  - [ ] 12.7 Run end-to-end Chainlit UI test with sample disputes
        Input: UI + backend | Output: E2E test results | Verify: Full conversation flow works
  - [ ] 12.8 Performance benchmark: Tool call latency <800ms P95
        Input: Load test | Output: Latency report | Verify: P95 < 800ms
  - [ ] 12.9 Performance benchmark: Evidence gathering <5 minutes
        Input: Complex disputes | Output: Timing report | Verify: <5 min for all cases
  - [ ] 12.10 Create Phase 1 MVP release documentation
        Input: All artifacts | Output: `docs/phase1_release.md` | Verify: Installation, usage, known limitations
  - [ ] 12.11 **Phase 1 Exit Gate**: All eval metrics pass
        Input: All validation reports | Output: Gate sign-off | Verify: Table in PRD Section 13 satisfied

---

## Summary

| Phase | Tasks | Sub-tasks | Duration |
|-------|-------|-----------|----------|
| Phase 0: Design & Architecture | 5 | 28 | Weeks 0-2 |
| Phase 0.5: Chainlit UI | 1 | 10 | Week 2.5-3 |
| Phase 1: Core MVP | 8 | 76 | Weeks 3-10 |
| **Total** | **14** | **114** | **10 weeks** |

**Note:** Phase 1 includes LLMService integration via `utils/llm_service.py` (pre-existing, 33 TDD tests passing).

**Qualitative Analysis Tasks Added:**
- Task 4.6: Phase 0.7 Domain Open Coding (6 sub-tasks) - Pending
- Task 6.17: Step 0.5 Failure Taxonomy Development (6 sub-tasks) - ✅ **COMPLETE** (κ=0.831)

---

## Validation Matrix

| PRD Requirement | Task Coverage | Gate | Status |
|-----------------|---------------|------|--------|
| FR-1: State Machine | 7.1-7.11 | 12.11 | **7.1-7.8, 7.10-7.11 ✅** |
| FR-2: MCP Tools | 2.1, 7.4-7.8 | 0.2 | Pending |
| FR-3: Hierarchical Gathering | 8.1-8.10 | 12.11 | Pending |
| FR-4: LLM Judges | 9.1-9.10, 6.17.4 | 12.2-12.4, 6.17.6 | **6.17.6 ✅** |
| FR-5: Explainability | 10.1-10.8 | 12.5-12.6 | Pending |
| FR-6: Chainlit UI | 5.1-5.10 | 5.10 | ✅ Done |
| NFR-1: PCI Compliance | 4.1, 10.3 | 0.5 | Pending |
| NFR-2: Latency | 9.6, 12.8-12.9 | 12.11 | Pending |
| NFR-3: Explainability | 10.1-10.8 | 12.5-12.6 | Pending |
| NFR-4: Eval-Driven | 6.1-6.17, 12.1-12.11 | 6.16, 6.17.6, 12.11 | **6.16 ✅, 6.17.6 ✅** |
| NFR-5: Qualitative Analysis | 4.6.1-4.6.6, 6.17.1-6.17.6 | 0.7, 6.17.6 | **6.17.6 ✅** (κ=0.831) |
| ADR-007: LLM Provider | 7.4, 8.1-8.4, 9.1-9.5 | Pre-validated | ✅ Done |
