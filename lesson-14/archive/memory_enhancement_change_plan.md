# Lesson 14 Memory Enhancements – Implementation Plan

This document translates the approved PRD into actionable edits across Lesson 14. Every change must reference canonical sources (`agents_memory.txt`, Compass Artifact suite) rather than restating their prose.

## 1. Theoretical Content Updates

### 1.1 `lesson-14/TUTORIAL_INDEX.md`
- **New “Memory Systems Track” subsection** after existing “Multi-Agent Specialist” path.
- Include three steps:
  1. Read `agents_memory.txt` (theory primer) – link directly.
  2. Read new `memory_systems_tutorial.md` – outline learning objectives (layered memory, context engineering, decision matrices).
  3. Run `memory_systems_demo.ipynb` before revisiting `react_agent_implementation.ipynb` to observe memory impact.
- Add estimated time (2.5–3 hours) and prerequisites (basic ReAct familiarity).
- Reference Compass Artifact lines (vector DB matrix, cost optimization, guardrails) via bullet “Strategic References” callout.

### 1.2 `lesson-14/memory_systems_tutorial.md` (new file)
- **Structure:**
  1. Overview & learning objectives (point back to `agents_memory.txt` for definitions).
  2. Layered memory architecture table (Working/Episodic/Semantic/Procedural) with usage notes for Planner/Validator/Executor agents.
  3. Context engineering lifecycle (Selection → Compression → Ordering) summarizing “context rot,” citing `agents_memory.txt`.
  4. Decision aids:
     - Vector DB selection matrix (summarize Compass Artifact table; include cross-link).
     - Memory pattern comparison (MemoryBank vs A-MEM vs Search-o1) with recommended use cases and links back to Compass Artifact + `agents_memory.txt`.
  5. Safety & Cost guardrails (tie to Compass Artifact guardrail stack + cost reduction examples).
  6. Implementation checklist bridging into backend/notebook tasks.
- **Anti-duplication:** Use “See also” callouts pointing to paragraph ranges instead of copying text. Limit to synthesized bullet summaries.

### 1.3 `lesson-14/multi_agent_design_patterns.md`
- Add “Scaling Memory in Multi-Agent Systems” section after existing scaling guidelines:
  - Outline 2-4/5-10/10-20/20+ agent tiers referencing Compass Artifact scaling notes.
  - For each tier, specify memory coordination strategy (centralized cache, shared vector DB, specialized retrieval agents).
  - Call out real deployment examples (Klarna supervisor, Microsoft AutoGen) with references to Compass Artifact case studies.
- Insert cross-link to `memory_systems_tutorial.md` for deeper strategy guidance.

### 1.4 Optional Diagram Enhancements
- If additional visuals are required, extend `lesson-14/diagrams/pattern_decision_tree.mmd` with a “Memory Strategy” branch referencing MemoryBank/A-MEM/Search-o1 selection heuristics. Reuse existing color palette.

## 2. Hands-On Assets

### 2.1 `lesson-14/memory_systems_demo.ipynb` (new notebook)
- **Execution toggles:** Reuse `EXECUTION_MODE` pattern (DEMO vs FULL) with clear runtime/cost notes; default to offline simulation.
- **Sections:**
  1. Setup & configuration (choose memory backend: InMemory, VectorStub, RedisMock; set decay/compression toggles).
  2. Dataset load: reuse `data/trajectory_test_set.json` and `data/trajectory_references.json` for episodic event streams.
  3. Memory pipeline demos:
     - Working memory rollover with trimming vs summarization.
     - MemoryBank-inspired decay (simulate Ebbinghaus curve) with adjustable retention strength.
     - A-MEM-inspired note linking (embed + neighbor retrieval using deterministic cosine similarity via `sklearn` to avoid external calls).
     - Search-o1-inspired “reason in documents” step injecting retrieved snippets mid-plan.
  4. Context engineering lab: toggle LLMLingua-style compression (use placeholder summarizer) and show token counts.
  5. Safety & guardrails: run rule-based filters before writes + guardrail log (pass/fail counts).
  6. Metrics export: `results/memory_demo_metrics.json` capturing token savings, hit rate, guardrail pass %, cost estimates.
- **Dependencies:** Only standard Python libs + existing repo utilities (avoid new pip installs unless already in requirements).

### 2.2 Backend hooks (`backend/multi_agent_framework.py` + helpers)
- Introduce `MemoryStore` protocol/base class with methods `write(event)`, `read(query)`, `decay()`, `stats()`.
- Implement adapters:
  - `InMemoryStore` (existing behavior).
  - `VectorStoreStub` (simulated ANN lookup using cosine similarity over embeddings produced via deterministic hashing or optional sentence-transformers if available).
  - `RedisCacheStub` (LRU-style dictionary with TTL).
- Extend `MemoryManager` to:
  - Accept configuration dict describing active layers (working, episodic, semantic).
  - Emit instrumentation events (hit/miss counters, guardrail flags) consumable by notebooks.
- Add guardrail hooks (callable list) invoked before persisting or retrieving entries; default include a simple “dietary restriction” check for recipe chatbot example.
- Provide docstrings referencing sections of `memory_systems_tutorial.md`.

### 2.3 Results / Evaluation Integration
- Update `lesson-14/results/README` (if present) or add a short note describing new JSON schema (metrics for compression, guardrails, hit rate).
- Ensure `evaluation_dashboard.py` (if reused) can read the new schema or document manual inspection steps.

## 3. Validation & Duplication Controls
- Add review checklist (in PR description template or separate doc) ensuring:
  - Each new section includes “Source References” callout.
  - No more than two consecutive sentences mirror `agents_memory.txt` wording.
  - New assets reuse existing datasets and do not introduce redundant JSON.
- Schedule smoke tests:
  - Run `memory_systems_demo.ipynb` in DEMO mode (<5 min, zero cost).
  - Execute targeted unit tests for new `MemoryStore` classes (add to `tests/test_multi_agent_framework.py`).
- Stakeholder sign-off: Curriculum maintainer confirms alignment with Compass Artifact, and QA verifies guardrail coverage.

_Prepared: 2025-11-15_

