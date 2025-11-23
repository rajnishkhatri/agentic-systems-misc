# Task List: Context Engineering Critical Success Factors

**Generated from:** `0010-implementation-plan-context-engineering-critical-success-factors.md`
**Date:** 2025-11-22

## Relevant Files

### New Files to Create

**Phase 1: Terminology and Diagrams**
- `google-context/TERMINOLOGY.md` - Critical distinctions reference guide (Session vs. Context, Memory vs. RAG, Proactive vs. Reactive)
- `google-context/diagrams/session_vs_context.mmd` - Session History vs. Context Window diagram
- `google-context/diagrams/memory_vs_rag.mmd` - Memory vs. RAG comparison diagram
- `google-context/diagrams/proactive_vs_reactive.mmd` - Retrieval strategy comparison diagram

**Phase 2: Session Management and Context Protection**
- `backend/sessions/__init__.py` - Sessions module initialization
- `backend/sessions/protected_context.py` - Protected context identification logic
- `backend/sessions/context_compressor.py` - Context compression with protection
- `backend/sessions/gita_session.py` - Bhagavad Gita session management implementation
- `tests/sessions/__init__.py` - Sessions test module initialization
- `tests/sessions/test_protected_context.py` - Protected context tests (TDD)
- `tests/sessions/test_context_compressor.py` - Context compressor tests (TDD)
- `tests/sessions/test_long_conversation.py` - Multi-turn conversation tests (50-100 turns)

**Phase 3: Memory Provenance and PII Protection**
- `backend/memory/__init__.py` - Memory module initialization
- `backend/memory/provenance.py` - Provenance data model and confidence tracking
- `backend/memory/pii_redaction.py` - PII redaction for spiritual/personal context
- `tests/memory/__init__.py` - Memory test module initialization
- `tests/memory/test_provenance.py` - Provenance tracking tests (TDD)
- `tests/memory/test_pii_redaction.py` - PII redaction tests (TDD)

**Phase 4: Pattern Library and Documentation**
- `patterns/context-engineering-sessions.md` - Sessions pattern documentation
- `patterns/context-engineering-memory.md` - Memory pattern documentation
- `google-context/TUTORIAL_INDEX.md` - Context engineering tutorial navigation hub

### Files to Modify

- `patterns/README.md` - Add 2 new patterns to pattern library catalog
- `CLAUDE.md` - Add Context Engineering Principles section after Quality Standards

### Notes

- **TDD Approach:** All implementation files (Phase 2 & 3) must follow RED→GREEN→REFACTOR workflow
- **Test Naming:** Use pattern `test_should_[result]_when_[condition]()` for all tests
- **Defensive Coding:** Type hints, input validation, error handling mandatory for all functions
- **Mermaid Diagrams:** Export to SVG for complex diagrams (>10 nodes) using `mmdc` command
- **Cross-Linking:** All documentation must link to related tutorials and patterns
- **Test Execution:** Run `pytest tests/sessions/` or `pytest tests/memory/` for module-specific tests
- **Code Coverage:** Target ≥90% coverage for all new modules

---

## Tasks

### Phase 1: Terminology and Visual Foundation (Days 1-2)

- [x] 1.0 Create Terminology Reference System
  - [x] 1.1 Create `google-context/TERMINOLOGY.md` with 6 critical distinctions (Session History vs. Context Window, Memory vs. RAG, Proactive vs. Reactive Retrieval, Events Log vs. Session State, Compression vs. Truncation, Protected vs. Compressible Context)
  - [x] 1.2 Add side-by-side comparison tables for each distinction with "Wrong vs. Right" examples
  - [x] 1.3 Include Bhagavad Gita chatbot-specific examples (e.g., "User prefers Swami Sivananda translations" as Memory, "Chapter 3 discusses karma yoga" as RAG)
  - [x] 1.4 Create directory `google-context/diagrams/`
  - [x] 1.5 Create `google-context/diagrams/session_vs_context.mmd` - Mermaid diagram showing Session History (50 turns, 50K tokens) → Context Window (protected + recent + memories, 8K tokens) with compression at 95% trigger
  - [x] 1.6 Create `google-context/diagrams/memory_vs_rag.mmd` - Visual comparison: Memory (personal assistant, user-specific) vs. RAG (research librarian, general knowledge)
  - [x] 1.7 Create `google-context/diagrams/proactive_vs_reactive.mmd` - Decision tree: Proactive (auto-load, higher tokens, no misses) vs. Reactive (agent tool call, lower tokens, requires smart agent)
  - [x] 1.8 Export all 3 Mermaid diagrams to SVG using `mmdc` command: `mmdc -i diagram.mmd -o diagram.svg`
  - [x] 1.9 Embed SVG diagrams in `TERMINOLOGY.md` with markdown image tags
  - [x] 1.10 Add quiz at end of `TERMINOLOGY.md`: "Given scenario X, which is Session History and which is Context Window?"
  - [x] 1.11 Update `patterns/tdd-workflow.md` to reference TERMINOLOGY.md in "When to Use" section
  - [x] 1.12 Update `patterns/abstract-base-class.md` to reference TERMINOLOGY.md for Memory vs. RAG distinction
  - [x] 1.13 Link `TERMINOLOGY.md` from `google-context/context_engineering_tutorial.md` introduction (SKIPPED - tutorial file doesn't exist yet, will be created in later phase)

**Estimated Time:** 7 hours
**Deliverables:** TERMINOLOGY.md (150 lines), 3 Mermaid diagrams with SVG exports, pattern library updates

---

### Phase 2: Session Management and Context Protection (Days 3-5)

- [ ] 2.0 Implement Session Management and Context Protection
  - [ ] 2.1 **TDD RED Phase:** Create `tests/sessions/__init__.py` (empty)
  - [ ] 2.2 **TDD RED Phase:** Create `tests/sessions/test_protected_context.py` with failing tests:
    - [ ] 2.2.1 `test_should_identify_initial_objectives_as_protected()` - Turn 0 events marked protected
    - [ ] 2.2.2 `test_should_identify_explicit_constraints_as_protected()` - Constraint events marked protected
    - [ ] 2.2.3 `test_should_not_protect_casual_conversation()` - Acknowledgments not protected
    - [ ] 2.2.4 `test_should_protect_auth_checkpoints()` - Authentication events protected
  - [ ] 2.3 **TDD RED Phase:** Run `pytest tests/sessions/test_protected_context.py` - confirm all tests fail with ImportError
  - [ ] 2.4 **TDD GREEN Phase:** Create `backend/sessions/__init__.py` with module exports
  - [ ] 2.5 **TDD GREEN Phase:** Create `backend/sessions/protected_context.py` with `identify_protected_context(event: dict) -> dict` function (type hints, input validation, returns `{"is_protected": bool, "reason": str}`)
  - [ ] 2.6 **TDD GREEN Phase:** Run `pytest tests/sessions/test_protected_context.py` - confirm all tests pass
  - [ ] 2.7 **TDD REFACTOR Phase:** Add docstrings with Args/Returns/Raises to `protected_context.py`
  - [ ] 2.8 **TDD RED Phase:** Create `tests/sessions/test_context_compressor.py` with failing tests:
    - [ ] 2.8.1 `test_should_trigger_compression_at_95_percent_capacity()` - Compression triggers at 7600/8000 tokens
    - [ ] 2.8.2 `test_should_not_trigger_compression_below_95_percent()` - No compression at 7400/8000 tokens
    - [ ] 2.8.3 `test_should_preserve_protected_events_during_compression()` - Protected indices intact after compression
    - [ ] 2.8.4 `test_should_compress_non_protected_events()` - Non-protected events summarized
    - [ ] 2.8.5 `test_should_raise_error_for_invalid_trigger_threshold()` - ValueError for threshold > 1.0 or < 0.0
  - [ ] 2.9 **TDD RED Phase:** Run `pytest tests/sessions/test_context_compressor.py` - confirm all tests fail
  - [ ] 2.10 **TDD GREEN Phase:** Create `backend/sessions/context_compressor.py` with `ContextCompressor` class (PRD lines 182-265: `__init__`, `should_compress`, `compress`, `_count_tokens`, `_summarize_events` methods)
  - [ ] 2.11 **TDD GREEN Phase:** Run `pytest tests/sessions/test_context_compressor.py` - confirm all tests pass
  - [ ] 2.12 **TDD REFACTOR Phase:** Add defensive coding - type hints, ValueError for invalid thresholds, TypeError for non-list events
  - [ ] 2.13 **TDD RED Phase:** Create `tests/sessions/test_long_conversation.py` with multi-turn tests:
    - [ ] 2.13.1 `test_should_preserve_objectives_in_50_turn_conversation()` - Initial objective survives 50 turns
    - [ ] 2.13.2 `test_should_handle_multiple_compressions_in_100_turns()` - 2-3 compression cycles
    - [ ] 2.13.3 `test_should_reject_compression_with_all_protected()` - Error when no compressible events
  - [ ] 2.14 **TDD RED Phase:** Run `pytest tests/sessions/test_long_conversation.py` - confirm tests fail
  - [ ] 2.15 **TDD GREEN Phase:** Create `backend/sessions/gita_session.py` with `GitaSession` class (events log, state scratchpad, `append_event()`, `get_context_window()` methods)
  - [ ] 2.16 **TDD GREEN Phase:** Run `pytest tests/sessions/test_long_conversation.py` - confirm all tests pass
  - [ ] 2.17 **TDD REFACTOR Phase:** Performance optimization - ensure compression completes in <2 seconds for 100 turns
  - [ ] 2.18 Run full session module test suite: `pytest tests/sessions/ -v --cov=backend/sessions --cov-report=term-missing`
  - [ ] 2.19 Verify ≥90% test coverage for all session modules

**Estimated Time:** 15 hours
**Deliverables:** 3 Python modules (protected_context.py, context_compressor.py, gita_session.py), 3 test files with 15+ tests, 100% pass rate

---

### Phase 3: Memory Provenance and PII Protection (Days 6-7)

- [ ] 3.0 Implement Memory Provenance Tracking System
  - [ ] 3.1 **TDD RED Phase:** Create `tests/memory/__init__.py` (empty)
  - [ ] 3.2 **TDD RED Phase:** Create `tests/memory/test_provenance.py` with failing tests:
    - [ ] 3.2.1 `test_should_create_provenance_with_required_fields()` - All fields present (memory_id, source_session_id, extraction_timestamp, confidence_score, validation_status)
    - [ ] 3.2.2 `test_should_track_confidence_evolution()` - Confidence history appends correctly
    - [ ] 3.2.3 `test_should_enforce_user_confirmed_higher_than_inferred()` - `effective_confidence` property boost for user_confirmed
    - [ ] 3.2.4 `test_should_calculate_confidence_trend()` - Trend detection (increasing, decreasing, stable, insufficient_data)
    - [ ] 3.2.5 `test_should_export_audit_log()` - `to_audit_log()` returns dict with lineage, trustworthiness, compliance fields
    - [ ] 3.2.6 `test_should_raise_error_for_invalid_confidence_score()` - ValueError for score > 1.0 or < 0.0
    - [ ] 3.2.7 `test_should_raise_error_for_invalid_validation_status()` - ValueError for status not in {agent_inferred, user_confirmed, disputed}
  - [ ] 3.3 **TDD RED Phase:** Run `pytest tests/memory/test_provenance.py` - confirm all tests fail
  - [ ] 3.4 **TDD GREEN Phase:** Create `backend/memory/__init__.py` with module exports
  - [ ] 3.5 **TDD GREEN Phase:** Create `backend/memory/provenance.py` with `MemoryProvenance` dataclass (PRD lines 415-530: all fields, `__post_init__`, `add_confidence_update`, properties, `to_audit_log`)
  - [ ] 3.6 **TDD GREEN Phase:** Run `pytest tests/memory/test_provenance.py` - confirm all tests pass
  - [ ] 3.7 **TDD REFACTOR Phase:** Add defensive coding - validate confidence_score range in `__post_init__`, validate validation_status enum
  - [ ] 3.8 **TDD RED Phase:** Create `tests/memory/test_pii_redaction.py` with failing tests:
    - [ ] 3.8.1 `test_should_redact_email_addresses()` - Email pattern detected and replaced with [EMAIL_REDACTED]
    - [ ] 3.8.2 `test_should_redact_phone_numbers()` - Phone pattern detected and replaced with [PHONE_REDACTED]
    - [ ] 3.8.3 `test_should_redact_full_names()` - Name pattern detected and replaced with [NAME_REDACTED]
    - [ ] 3.8.4 `test_should_redact_locations()` - Location pattern detected and replaced with [LOCATION_REDACTED]
    - [ ] 3.8.5 `test_should_not_redact_false_positives()` - "Arjuna" (character name) not redacted, "karma" not flagged
    - [ ] 3.8.6 `test_should_preserve_sentence_structure()` - Redacted text remains grammatically correct
    - [ ] 3.8.7 `test_should_return_pii_found_flag()` - Returns tuple (redacted_text, pii_found: bool)
  - [ ] 3.9 **TDD RED Phase:** Run `pytest tests/memory/test_pii_redaction.py` - confirm all tests fail
  - [ ] 3.10 **TDD GREEN Phase:** Create `backend/memory/pii_redaction.py` with `PIIRedactor` class (PRD lines 546-615: regex patterns, `redact()` method)
  - [ ] 3.11 **TDD GREEN Phase:** Add `extract_memory_with_pii_redaction()` function integrating PIIRedactor with MemoryProvenance
  - [ ] 3.12 **TDD GREEN Phase:** Run `pytest tests/memory/test_pii_redaction.py` - confirm all tests pass
  - [ ] 3.13 **TDD REFACTOR Phase:** Add helper function `generate_uuid()` for memory_id generation (import from `uuid` module)
  - [ ] 3.14 Run full memory module test suite: `pytest tests/memory/ -v --cov=backend/memory --cov-report=term-missing`
  - [ ] 3.15 Verify ≥90% test coverage for all memory modules

**Estimated Time:** 12 hours
**Deliverables:** 2 Python modules (provenance.py, pii_redaction.py), 2 test files with 14+ tests, 100% pass rate, audit log integration

---

### Phase 4: Pattern Library and Documentation (Days 8-10)

- [ ] 4.0 Create Pattern Library Documentation
  - [ ] 4.1 Create `patterns/context-engineering-sessions.md` following standard pattern template:
    - [ ] 4.1.1 Add metadata: Complexity ⭐⭐⭐, Use Case "Managing stateful multi-turn conversations"
    - [ ] 4.1.2 Write "Pattern Overview" section explaining Sessions = short-term workspace (events log + session state)
    - [ ] 4.1.3 Add "Terminology Foundation" section linking to `TERMINOLOGY.md#session-vs-context` and `TERMINOLOGY.md#protected-context`
    - [ ] 4.1.4 Write "Code Template" section with `GitaSession` class example (PRD lines 656-682)
    - [ ] 4.1.5 Add "Real Example from Codebase" section with file:line references (e.g., `backend/sessions/gita_session.py:12-89`)
    - [ ] 4.1.6 Write "Common Pitfalls" section with ❌ anti-pattern (sending entire session history) and ✅ correct pattern (compress and curate)
    - [ ] 4.1.7 Add "Integration with Defensive Coding" section emphasizing type hints, input validation, error handling
    - [ ] 4.1.8 Write "Testing Strategy" section with TDD example: `test_should_preserve_objectives_after_compression()`
    - [ ] 4.1.9 Add "When to Use This Pattern" section with ✅ use cases and ❌ don't use cases
  - [ ] 4.2 Create `patterns/context-engineering-memory.md` following standard pattern template:
    - [ ] 4.2.1 Add metadata: Complexity ⭐⭐⭐⭐, Use Case "Long-term persistence of user preferences and learning patterns"
    - [ ] 4.2.2 Write "Pattern Overview" section explaining Memory = consolidated knowledge across sessions
    - [ ] 4.2.3 Add "Terminology Foundation" section linking to `TERMINOLOGY.md#memory-vs-rag`
    - [ ] 4.2.4 Write "Code Template" section with memory extraction, consolidation, retrieval examples
    - [ ] 4.2.5 Add "Provenance Tracking (Critical Success Factor #3)" section with mandatory fields (source_session_id, confidence_score, validation_status)
    - [ ] 4.2.6 Write "Confidence Evolution" subsection explaining boost/penalty rules
    - [ ] 4.2.7 Add "PII Redaction (Mandatory for Spiritual/Personal Context)" section with `PIIRedactor` example
    - [ ] 4.2.8 Write "Common Pitfalls" section with ❌ anti-pattern (treating memory as saved chat) and ✅ correct pattern (extract signal from noise)
    - [ ] 4.2.9 Add "Real Example from Codebase" section with file:line references
  - [ ] 4.3 Create `google-context/TUTORIAL_INDEX.md` with comprehensive navigation:
    - [ ] 4.3.1 Write "Overview" section with core thesis: "Bigger models aren't enough. Intelligence emerges from orchestration."
    - [ ] 4.3.2 Add "Prerequisites" section listing required knowledge and ⚠️ CRITICAL reminder to read TERMINOLOGY.md first
    - [ ] 4.3.3 Write "Learning Path 1: Quick Start (30 minutes)" with 3 steps: TERMINOLOGY.md (10 min), diagrams (10 min), case study (10 min)
    - [ ] 4.3.4 Write "Learning Path 2: Implementation-Focused (2-3 hours)" with 4 steps: Path 1, pattern guides, code templates, implement
    - [ ] 4.3.5 Write "Learning Path 3: Full Mastery (4-6 hours)" with 4 steps: Path 2, deep-dive tutorials, advanced topics, case study analysis
    - [ ] 4.3.6 Create "Files" table with columns: File, Type, Lines, Purpose, Estimated Reading Time
    - [ ] 4.3.7 Write "Critical Success Factors" section highlighting 3 factors: terminology clarity, context protection, provenance tracking
    - [ ] 4.3.8 Add "Integration with Course" table mapping Lessons 9-11, 12, 16 with status (🔄 Planned, 📝 To Create)
    - [ ] 4.3.9 Write "Common Pitfalls" section with 3 pitfalls (PRD lines 963-1001): sending entire history, treating memory as saved chat, ignoring provenance
    - [ ] 4.3.10 Add "Real-World Applications" section with 3 examples: Bhagavad Gita Chatbot, Banking Fraud Dispute, Healthcare Triage
    - [ ] 4.3.11 Write "FAQs" section answering 4 questions (when to use sessions vs. memory, when to compress, what if protected context compressed, how to test)
    - [ ] 4.3.12 Add "Next Steps" checklist with 5 action items
  - [ ] 4.4 Update `patterns/README.md`:
    - [ ] 4.4.1 Add "Context Engineering: Sessions" pattern to catalog table (Complexity ⭐⭐⭐, Use Case, Link to `context-engineering-sessions.md`)
    - [ ] 4.4.2 Add "Context Engineering: Memory" pattern to catalog table (Complexity ⭐⭐⭐⭐, Use Case, Link to `context-engineering-memory.md`)
    - [ ] 4.4.3 Update pattern count in introduction (from 3 to 5 patterns)
  - [ ] 4.5 Update `CLAUDE.md`:
    - [ ] 4.5.1 Insert "Context Engineering Principles" section after "Quality Standards" (after line ~150)
    - [ ] 4.5.2 Add "Core Concepts" subsection with core thesis quote
    - [ ] 4.5.3 Add "Critical Distinctions" subsection with 3 distinctions (Session History vs. Context Window, Memory vs. RAG, Proactive vs. Reactive)
    - [ ] 4.5.4 Add "Protected Context Pattern" subsection with code example: `identify_protected_context()`
    - [ ] 4.5.5 Add "Memory Provenance (Mandatory)" subsection with metadata example and confidence evolution rules
    - [ ] 4.5.6 Add "PII Redaction for Spiritual Context" subsection with `PIIRedactor` example
    - [ ] 4.5.7 Add "Implementation Checklist" with 7 items
    - [ ] 4.5.8 Add "Learning Resources" subsection linking to TUTORIAL_INDEX.md, patterns, case study, diagrams
  - [ ] 4.6 Cross-link all documentation files (verify links work with relative paths)

**Estimated Time:** 17 hours
**Deliverables:** 2 pattern files, TUTORIAL_INDEX.md (200+ lines), updates to README.md and CLAUDE.md

---

### Phase 5: Integration Testing and Quality Validation

- [ ] 5.0 Integration Testing and Quality Validation
  - [ ] 5.1 Run full test suite: `pytest tests/ -v --cov=backend --cov-report=html --cov-report=term-missing`
  - [ ] 5.2 Verify ≥90% test coverage for `backend/sessions/` module
  - [ ] 5.3 Verify ≥90% test coverage for `backend/memory/` module
  - [ ] 5.4 Run Ruff formatting: `ruff format backend/sessions/ backend/memory/ tests/sessions/ tests/memory/`
  - [ ] 5.5 Run Ruff linting: `ruff check backend/sessions/ backend/memory/ tests/sessions/ tests/memory/ --fix`
  - [ ] 5.6 Verify all functions have type hints: `grep -r "def.*->" backend/sessions/ backend/memory/ | wc -l` should equal total function count
  - [ ] 5.7 Verify all functions have docstrings: Check all public functions have Args/Returns/Raises documentation
  - [ ] 5.8 Test end-to-end workflow: Create GitaSession → add 50 turns → trigger compression → verify protected context preserved
  - [ ] 5.9 Test end-to-end workflow: Extract memory → apply PII redaction → create provenance → update confidence → export audit log
  - [ ] 5.10 Performance validation: Run 100-turn conversation test and verify compression completes in <2 seconds
  - [ ] 5.11 Validate all Mermaid diagrams render correctly on GitHub: Push to branch and check preview
  - [ ] 5.12 Validate all documentation links work: Click through all relative path links in TUTORIAL_INDEX.md, patterns, TERMINOLOGY.md
  - [ ] 5.13 Generate test coverage report and review missing lines: `open htmlcov/index.html`
  - [ ] 5.14 Create summary report: Document test pass rate, coverage %, performance benchmarks, file count, total lines of code

**Estimated Time:** 8 hours
**Deliverables:** ≥90% test coverage, 100% test pass rate, Ruff-compliant code, validated documentation, performance benchmarks
