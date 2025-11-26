# Design Decisions: Lesson 16 - Agent Reliability

This document records resolutions to all Open Questions (OQ1-OQ7) from the PRD to ensure traceability and justify implementation choices.

---

## OQ1: Tutorial Granularity

**Question:** Should tutorials be 15-30 min (broader) or 5-10 min (focused)?

**Decision:** **15-30 minutes per tutorial with focused deep-dives where needed**

**Rationale:**
- Complex topics (agent reliability, orchestration patterns) require comprehensive explanation
- 15-30 min allows for theory + examples + exercises in a single sitting
- Implemented 7 concept tutorials:
  - Tutorial 01: 27 min (Agent Reliability Fundamentals)
  - Tutorial 02: 36 min (Orchestration Patterns Overview - comprehensive survey)
  - Tutorial 03: 24 min (Deterministic Execution Strategies)
  - Tutorial 04: 30 min (Error Propagation Analysis)
  - Tutorial 05: 26 min (AgentArch Benchmark Methodology)
  - Tutorial 06: 29 min (Financial Workflow Reliability)
  - Tutorial 07: 23 min (Production Deployment Considerations)
- Tutorial 02 is longer (36 min) as it provides comprehensive overview of all 5 patterns
- Tutorials 06-07 are shorter (23-29 min) as focused case studies
- Reading time calculated at ~200 words/min with 5% tolerance

**Trade-offs:**
- ✅ Single session mastery of complete concepts
- ✅ Better retention with cohesive narrative
- ❌ Longer initial time commitment
- ❌ Less granular for quick reference

**Mitigation:**
- TUTORIAL_INDEX.md provides quick navigation to specific sections
- Interactive notebooks (5 min execution) for hands-on practice
- Visual diagrams for quick reference

---

## OQ2: Notebook Execution Modes

**Question:** Should notebooks default to DEMO (fast, $0) or FULL (real LLM calls, costly)?

**Decision:** **DEMO mode by default with clear FULL mode toggle**

**Rationale:**
- Students should learn without financial barriers
- DEMO mode uses mock agents with deterministic outputs
- All 8 notebooks (08-15) implement dual-mode execution:
  ```python
  # Cell 1: Configuration
  USE_DEMO_MODE = True  # Toggle: True = $0 learning, False = real LLM calls
  ESTIMATED_COST_FULL_MODE = "$0.50"  # Transparent cost disclosure
  ```
- DEMO mode benefits:
  - Instant execution (<5 seconds vs. 30+ seconds)
  - Reproducible results (no API rate limits, no stochastic variation)
  - Zero cost for iterative learning
  - Deterministic outputs for assertion validation
- FULL mode benefits:
  - Real LLM behavior (temperature, prompt sensitivity)
  - Production-representative metrics
  - Cost-benefit analysis validation

**Trade-offs:**
- ✅ Accessible learning ($0 barrier)
- ✅ Faster iteration (5 sec vs. 30 sec)
- ✅ Reproducible (CI/CD friendly)
- ❌ Mock behavior may differ from real LLMs
- ❌ Students must manually toggle for production testing

**Mitigation:**
- Every notebook includes cost warning and toggle instructions
- Cost summary section shows savings: "DEMO mode: $0 saved (vs. $0.50 FULL mode)"
- Validation sections work in both modes
- Documentation recommends DEMO first, then FULL for production readiness

---

## OQ3: Dataset Size

**Question:** Should datasets be 100 tasks (fast iteration) or 300 tasks (research-grade)?

**Decision:** **100 tasks per dataset with 300-task generation capability**

**Rationale:**
- 100 tasks sufficient for pedagogical validation (<5 min notebook execution)
- 300 tasks needed for statistical significance in research (AgentArch reproduction)
- Implemented hybrid approach:
  - **Default datasets:** 100 tasks each (invoices_100.json, transactions_100.json, reconciliation_100.json)
  - **Benchmark framework:** Supports 300+ tasks via FinancialTaskGenerator
  - **Cached results:** Pre-computed 100-task results for <10 min notebook execution (OQ7 solution)
- 100 tasks provide:
  - Adequate challenge distribution (±5% target rates achieved)
  - Fast notebook execution (<5 min target met)
  - Sufficient diversity (30+ unique vendors, 43+ unique merchants)
- 300 tasks provide:
  - Statistical power (95% confidence intervals via bootstrapping)
  - Research reproducibility (±15% tolerance on AgentArch metrics)
  - Production-representative evaluation

**Trade-offs:**
- ✅ Fast learning with 100 tasks
- ✅ Research-grade option with 300 tasks
- ✅ Flexible scaling via generator
- ❌ Must regenerate datasets for 300-task benchmark
- ❌ Cached results needed to meet <10 min target

**Mitigation:**
- data_generation/ module supports count parameter: `generate_invoice_dataset(count=300)`
- Regeneration commands documented in data/README.md
- Cached results strategy in Notebook 14 (USE_CACHED_RESULTS toggle)
- Seed-based reproducibility ensures consistency across runs

---

## OQ4: Error Rate Targets

**Question:** Should error rates be universal (5%) or task-specific?

**Decision:** **Task-specific error rate targets based on domain complexity**

**Rationale:**
- Different financial workflows have different inherent difficulty and risk tolerance
- Implemented targets:
  - **Invoice processing: <5% error rate** (high-volume, low-risk, automatable)
  - **Fraud detection: <10% error rate** (class imbalance, ambiguous patterns, higher acceptable FP rate)
  - **Account reconciliation: <8% error rate** (date mismatches, rounding errors, manual review acceptable)
- Justification:
  - Invoice processing is well-structured with clear validation rules → strict 5% target
  - Fraud detection has 10% fraud rate in dataset + ambiguous patterns → relaxed 10% target
  - Reconciliation has temporal/numerical ambiguity → moderate 8% target
- Validated in test_e2e_workflows.py (tests E2E.1, E2E.6, E2E.11)

**Trade-offs:**
- ✅ Realistic targets aligned with domain constraints
- ✅ Flexibility for risk tolerance (low-stakes vs. high-stakes)
- ✅ Matches industry practices
- ❌ More complex to document and track
- ❌ No single universal benchmark

**Mitigation:**
- Clear documentation in Tutorial 01 (Reliability Fundamentals)
- Error rate targets documented in data/DATASET_SUMMARY.json metadata
- Production monitoring dashboard (Tutorial 07) tracks task-specific thresholds
- E2E tests validate each workflow independently

---

## OQ5: Diagram Export Format

**Question:** Should diagrams be Mermaid-only (maintainable) or PNG exports (complex diagrams)?

**Decision:** **Mermaid primary + PNG exports for complex diagrams (>10 nodes)**

**Rationale:**
- Mermaid advantages:
  - Maintainable (text-based, version control friendly)
  - GitHub native rendering
  - No external dependencies
- PNG advantages:
  - Consistent rendering across platforms
  - Supports complex diagrams (error propagation cascade, reliability architecture)
  - High resolution for presentations
- Implemented strategy:
  - All 5 diagrams have .mmd source files (reliability_failure_modes_taxonomy.mmd, orchestration_pattern_selection.mmd, error_propagation_cascade.mmd, reliability_framework_architecture.mmd, agentarch_benchmark_results.mmd)
  - Complex diagrams (3+) exported to PNG/SVG using mmdc:
    ```bash
    npx -p @mermaid-js/mermaid-cli mmdc -i diagram.mmd -o diagram.png -w 2400 -H 1800 -b transparent
    ```
  - Documentation references .mmd files (source of truth)
  - Notebooks use .png for consistency

**Trade-offs:**
- ✅ Version control friendly (.mmd text files)
- ✅ Consistent rendering (PNG exports)
- ✅ Dual format flexibility
- ❌ Manual export step required
- ❌ PNG files increase repo size

**Mitigation:**
- Export commands documented in diagrams/README.md
- CI/CD can automate PNG generation (optional)
- Only complex diagrams exported (3-4 PNGs vs. 5 Mermaid sources)
- Transparent background for light/dark mode compatibility

---

## OQ6: Test Coverage Targets

**Question:** Should coverage target be 90% (achievable) or 95% (strict)?

**Decision:** **≥90% line coverage with ≥85% branch coverage**

**Rationale:**
- 90% line coverage is industry standard for production code
- 95% coverage often requires testing trivial code (getters, setters, __repr__)
- Achieved coverage:
  - backend/reliability/: 93% coverage (verified in Task 2.10)
  - backend/orchestrators/: 94% coverage (verified in Task 3.9)
  - backend/benchmarks/: 94% coverage (verified in Task 6.13)
  - Overall backend/: 94% average coverage
- Branch coverage (85% target) ensures error handling paths tested
- Validated via: `pytest --cov=lesson-16/backend --cov-report=term --cov-fail-under=90`

**Trade-offs:**
- ✅ Achievable without testing trivial code
- ✅ Focuses on meaningful code paths
- ✅ Balances quality vs. diminishing returns
- ❌ 5-10% uncovered code may hide bugs
- ❌ Edge cases might be missed

**Mitigation:**
- Manual review of uncovered lines (logged in coverage reports)
- Branch coverage (85%) ensures error paths tested
- Integration tests cover cross-module scenarios missed by unit tests
- Success metrics (SM3) validate quality beyond coverage numbers

---

## OQ7: Benchmark Execution Time

**Question:** How to achieve <10 min benchmark execution when 300 tasks with real LLMs takes 30+ min?

**Decision:** **Cached results strategy with USE_CACHED_RESULTS toggle**

**Rationale:**
- Problem: Running 300 tasks × 5 orchestrators × real LLM calls = 30+ minutes
- Solution: Pre-compute results and cache as JSON
- Implementation (Notebook 14):
  ```python
  # Cell 1: Configuration
  USE_CACHED_RESULTS = True  # Default: load pre-computed results (<1 second)
  # Set to False to re-run benchmark with real LLM calls (~30 min, ~$0.50)

  if USE_CACHED_RESULTS:
      results = load_cached_results("cache/benchmark_results_100tasks.json")  # <1s
  else:
      results = run_benchmark(orchestrators, task_suite, seed=42)  # ~30 min
  ```
- Cached results validated:
  - JSON format with all 4 metrics (success rate, EPI, latency, cost)
  - Timestamp and metadata (task_count, seed, patterns)
  - Integrity validated in test_sm4_sm5_validation.py (SM4.12)
- Students can:
  - Learn instantly with cached results (default)
  - Re-run with 10 tasks (~$0.10, ~3 min) for experimentation
  - Re-run with 300 tasks (~$0.50, ~30 min) for research reproduction

**Trade-offs:**
- ✅ <10 min notebook execution (meets requirement)
- ✅ Zero cost for learning (cached results)
- ✅ Research reproducibility (can re-run with same seed)
- ❌ Cached results may diverge from live API behavior
- ❌ Must regenerate cache if datasets/code change

**Mitigation:**
- Notebook 14 includes cache validation checks (timestamp, task_count)
- Warning if cached results >30 days old
- Regeneration instructions: `python -m lesson_16.backend.benchmarks.runner --tasks 300 --seed 42`
- Test suite (Task 7.10) validates cache load <1s

---

## Summary: Key Design Decisions

| OQ | Question | Decision | Primary Driver |
|----|----------|----------|----------------|
| OQ1 | Tutorial length | 15-30 min comprehensive | Topic complexity requires cohesive explanation |
| OQ2 | Notebook mode | DEMO default + FULL toggle | Zero-cost learning accessibility |
| OQ3 | Dataset size | 100 tasks + 300 capability | Fast iteration + research-grade option |
| OQ4 | Error rate targets | Task-specific (5%/10%/8%) | Domain complexity and risk tolerance |
| OQ5 | Diagram format | Mermaid + PNG exports | Maintainability + rendering consistency |
| OQ6 | Test coverage | ≥90% line, ≥85% branch | Industry standard vs. diminishing returns |
| OQ7 | Benchmark execution | Cached results strategy | <10 min requirement with research reproducibility |

---

## Implementation Status

**All OQ decisions implemented and validated:**

- ✅ OQ1: 7 tutorials with reading times 23-36 min (verified in test_tutorial_quality.py)
- ✅ OQ2: 8 notebooks with DEMO/FULL toggle (verified in test_sm2_sm3_validation.py)
- ✅ OQ3: 3 datasets with 100 tasks + FinancialTaskGenerator(count=300) (verified in test_dataset_validation.py)
- ✅ OQ4: Task-specific error rates validated (verified in test_e2e_workflows.py tests E2E.1/E2E.6/E2E.11)
- ✅ OQ5: 5 Mermaid diagrams + 3 PNG exports (verified in test_diagram_validation.py)
- ✅ OQ6: 94% average coverage (verified in test_sm2_sm3_validation.py)
- ✅ OQ7: Cached results load <1s (verified in test_sm4_sm5_validation.py SM4.12)

**Production Readiness:** All decisions align with FR (Functional Requirements) and DC (Design Constraints) from the PRD.

**Last Updated:** 2025-11-26

**Contributors:** Claude Code (AI Dev Tasks Workflow)
