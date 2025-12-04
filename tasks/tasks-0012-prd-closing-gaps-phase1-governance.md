# Tasks: Closing the Gaps - Phase 1: Governance Layer

**PRD Reference:** [`tasks/0012-prd-closing-gaps-phase1-governance.md`](0012-prd-closing-gaps-phase1-governance.md)
**Created:** December 2024
**Status:** Ready for Implementation

---

## Relevant Files

### Source Files
- `lesson-18/closing_the_gaps/governance/prompt_security.py` - PromptSecurityGuard implementation with multi-layer detection
- `lesson-18/closing_the_gaps/governance/hitl_controller.py` - HITLController with tiered oversight logic
- `lesson-18/closing_the_gaps/governance/__init__.py` - Module exports (update existing)
- `lesson-18/closing_the_gaps/config/security.yaml` - Configuration file for thresholds and patterns
- `lesson-18/closing_the_gaps/config/injection_patterns.json` - Custom injection patterns (hot-reloadable)
- `lesson-18/closing_the_gaps/migrations/001_governance_tables.sql` - PostgreSQL schema migration

### Test Files
- `lesson-18/closing_the_gaps/tests/test_prompt_security.py` - TDD tests for PromptSecurityGuard
- `lesson-18/closing_the_gaps/tests/test_hitl_controller.py` - TDD tests for HITLController
- `lesson-18/closing_the_gaps/tests/test_governance_integration.py` - Integration tests
- `lesson-18/closing_the_gaps/tests/conftest.py` - Pytest fixtures for governance tests

### Tutorial Files
- `lesson-18/closing_the_gaps/tutorials/01_prompt_security_quickstart.md` - 15-min quick-start guide
- `lesson-18/closing_the_gaps/tutorials/02_hitl_controller_quickstart.md` - 15-min quick-start guide
- `lesson-18/closing_the_gaps/tutorials/TUTORIAL_INDEX.md` - Tutorial index (update)

### Existing Files to Reference
- `lesson-18/closing_the_gaps/evaluation/base_evaluator.py` - BaseEvaluator ABC pattern to follow
- `lesson-18/closing_the_gaps/DESIGN.md` - High-level design document
- `tests/memory/test_pii_redaction.py` - TDD test pattern example
- `backend/memory/pii_redaction.py` - Similar regex-based detection pattern

### Notes

- Unit tests should be placed in `lesson-18/closing_the_gaps/tests/` directory
- Use `pytest lesson-18/closing_the_gaps/tests/` to run governance tests
- Follow TDD workflow: RED (failing test) → GREEN (minimal pass) → REFACTOR
- All tests should use `test_should_*` naming convention per project patterns

---

## Tasks

- [x] 1.0 Implement PromptSecurityGuard Component
  - [x] 1.1 Create `ScanResult` Pydantic model with fields: `is_safe`, `threat_type`, `confidence`, `matched_patterns`, `sanitized_input`, `scan_duration_ms`
  - [x] 1.2 Write TDD tests for Layer 1 pattern matching (instruction override, role hijack, prompt leak, delimiter injection, jailbreak patterns)
  - [x] 1.3 Implement `scan_input()` method with Layer 1 regex pattern matching (<5ms target)
  - [x] 1.4 Write TDD tests for Layer 2 structural analysis (role override detection, instruction delimiter detection)
  - [x] 1.5 Implement Layer 2 structural analysis methods: `contains_role_override()`, `contains_instruction_delimiter()`
  - [x] 1.6 Write TDD tests for `scan_agent_output()` method (agent-to-agent security)
  - [x] 1.7 Implement `scan_agent_output()` to prevent prompt infection propagation between agents
  - [x] 1.8 Implement `sanitize()` method to remove threats while preserving user intent
  - [x] 1.9 Implement `add_pattern()` for runtime pattern addition and `get_threat_stats()` for metrics
  - [x] 1.10 Add input validation: TypeError for non-string input, ValueError for input exceeding 10KB max length
  - [x] 1.11 Implement hot-reloadable pattern loading from JSON config file

- [x] 2.0 Implement HITLController Component
  - [x] 2.1 Create `OversightTier` enum with TIER_1_HIGH, TIER_2_MEDIUM, TIER_3_LOW values
  - [x] 2.2 Create `InterruptDecision` Pydantic model with fields: `should_interrupt`, `reason`, `tier`, `confidence`, `amount`, `dispute_type`, `timestamp`, `decision_id`
  - [x] 2.3 Write TDD tests for Tier 1 actions (SAR filing, payment blocking, account closure) - must always interrupt
  - [x] 2.4 Implement `should_interrupt()` with Tier 1 classification logic for high-risk actions
  - [x] 2.5 Write TDD tests for Tier 2 triggers (low confidence <0.85, high amount >$10K, high-risk dispute types)
  - [x] 2.6 Implement Tier 2 classification logic with configurable thresholds
  - [x] 2.7 Write TDD tests for Tier 3 actions (info lookup, low-value disputes with high confidence) - logged only
  - [x] 2.8 Implement Tier 3 classification and `get_tier()` method
  - [x] 2.9 Write TDD tests for `request_human_review()` - should create review request and return UUID
  - [x] 2.10 Implement `request_human_review()` with context packaging and review_id generation
  - [x] 2.11 Implement `record_human_decision()` for capturing reviewer approval/rejection
  - [x] 2.12 Implement `get_escalation_stats()` for reporting escalation rates by tier
  - [x] 2.13 Add input validation: TypeError for non-float confidence, ValueError for confidence not in [0.0, 1.0]

- [x] 3.0 Create PostgreSQL Database Schemas
  - [x] 3.1 Create `security_events` table schema with columns: id, timestamp, input_hash, input_length, is_safe, threat_type, confidence, matched_patterns, scan_duration_ms, session_id, user_id, agent_id, scanner_version
  - [x] 3.2 Add indexes for security_events: timestamp, threat_type, session_id
  - [x] 3.3 Create monthly partitioning for security_events table (performance optimization)
  - [x] 3.4 Create `hitl_decisions` table schema with columns: id, decision_id, timestamp, should_interrupt, reason, tier, confidence, amount, dispute_type, action_type, session_id, agent_id
  - [x] 3.5 Add indexes for hitl_decisions: timestamp, tier, dispute_type
  - [x] 3.6 Create `hitl_reviews` table schema with columns: id, review_id, decision_id (FK), created_at, context (JSONB), reviewed_at, approved, reviewer_id, notes, status
  - [x] 3.7 Add indexes for hitl_reviews: status, decision_id
  - [x] 3.8 Write migration script with CREATE TABLE statements and proper constraints

- [x] 4.0 Integrate with Existing Framework
  - [x] 4.1 Create `config/security.yaml` with prompt_security and hitl_controller configuration sections
  - [x] 4.2 Create `config/injection_patterns.json` with default OWASP LLM Top 10 patterns
  - [x] 4.3 Implement configuration loader to read YAML and JSON config files
  - [x] 4.4 Add async PostgreSQL logging to PromptSecurityGuard (non-blocking, <100ms target)
  - [x] 4.5 Add async PostgreSQL logging to HITLController for decisions and reviews
  - [x] 4.6 Integrate PromptSecurityGuard with BlackBoxRecorder for SECURITY_BLOCK and AGENT_HANDOFF events
  - [x] 4.7 Integrate HITLController with BlackBoxRecorder for HITL_REQUESTED and HITL_APPROVED/REJECTED events
  - [x] 4.8 Update `governance/__init__.py` to export all new classes and enums
  - [x] 4.9 Write integration tests verifying end-to-end flow: input → security scan → HITL check → logging
  - [x] 4.10 Add environment variable support for threshold overrides (HITL_CONFIDENCE_THRESHOLD, HITL_AMOUNT_THRESHOLD)

- [x] 5.0 Write Quick-Start Tutorials
  - [x] 5.1 Create `01_prompt_security_quickstart.md` with 5-minute setup section
  - [x] 5.2 Add basic usage examples: scan_input(), testing injection detection, adding custom patterns
  - [x] 5.3 Add learning objectives and "Next Steps" section referencing DESIGN.md and OWASP LLM Top 10
  - [x] 5.4 Create `02_hitl_controller_quickstart.md` with 5-minute setup section
  - [x] 5.5 Add basic usage examples: should_interrupt(), tier classification, configuring thresholds
  - [x] 5.6 Add learning objectives and "Next Steps" section referencing regulatory requirements (SR 11-7, EU AI Act)
  - [x] 5.7 Update `tutorials/TUTORIAL_INDEX.md` with links to new tutorials
  - [x] 5.8 Add code examples with expected outputs and assertions for both tutorials

---

## Success Criteria

| Metric | Target | Validation Method |
|--------|--------|-------------------|
| Injection detection rate | ≥95% | Run test suite against OWASP patterns |
| False positive rate | ≤2% | Test with legitimate dispute queries |
| HITL Tier 1 compliance | 100% | All SAR/blocking actions require approval |
| p99 scan latency | <100ms | Benchmark tests with timing assertions |
| Audit coverage | 100% | Verify all decisions have DB records |

---

## Dependencies

- **Phase 1.1 (PromptSecurityGuard)** can be developed independently
- **Phase 1.2 (HITLController)** can be developed independently
- **Phase 1.3 (Database)** should be completed before Phase 1.4 integration
- **Phase 1.4 (Integration)** requires Phase 1.1, 1.2, and 1.3
- **Phase 1.5 (Tutorials)** requires Phase 1.1 and 1.2 implementations

---

*Generated from PRD: 0012-prd-closing-gaps-phase1-governance.md*

