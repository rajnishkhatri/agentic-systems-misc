# Lesson 14 Memory Strategy Enhancements PRD

## 1. Introduction / Overview
Lesson 14 currently excels at planning, orchestration, and evaluation but treats memory as a supporting bullet. `agents_memory.txt` delivers deep theory, and the Compass Artifact outlines strategic tradeoffs, yet learners lack a guided path that connects those assets to concrete tutorials, demos, or production practices. This PRD defines the curriculum, documentation, and tooling enhancements required to elevate memory to a first-class pillar—working, episodic, semantic, and procedural layers—with explicit ties to safety, cost, and multi-agent scaling. All changes must reference existing canonical sources to avoid duplicating their content.

## 2. Goals
1. Provide learners with an end-to-end memory learning path (theory → strategy → practice) inside Lesson 14.
2. Deliver runnable assets that showcase memory pipelines (MemoryBank/A-MEM/Search-o1 inspired) plus context engineering techniques.
3. Embed production guardrails (safety, cost, observability) into memory workflows to mirror Compass Artifact recommendations.
4. Ensure every new asset cross-links (rather than repeats) `agents_memory.txt`, Compass Artifact, and existing diagrams to maintain a single source of truth.

## 3. User Stories
- As a curriculum maintainer, I want a reusable memory tutorial template so I can reference `agents_memory.txt` without copying its full text.
- As a practitioner running Lesson 14 notebooks, I want a demo that shows how working and long-term memory interact with the Planner/Validator/Executor stack so I can replicate it in production.
- As an enterprise architect, I want clear decision trees for memory store selection, guardrails, and cost controls so I can justify infrastructure choices to stakeholders.
- As a QA reviewer, I need acceptance criteria that confirm memory additions don’t duplicate existing tutorials but instead cross-link to canonical resources.

## 4. Functional Requirements
1. **Learning Path Integration** – Update `lesson-14/TUTORIAL_INDEX.md` with a “Memory Systems Track” that sequence-links: `agents_memory.txt` (theory) → new `memory_systems_tutorial.md` (strategy + implementation) → new/demo artifacts. Include estimated times and prerequisites.
2. **Memory Systems Tutorial** – Create `lesson-14/memory_systems_tutorial.md` summarizing (not repeating) key constructs from `agents_memory.txt` and Compass Artifact, covering:
   - Layered memory models (working/episodic/semantic/procedural) aligned with planner/validator/executor roles.
   - Context engineering lifecycle (selection, compression, ordering) with references to “context rot.”
   - Decision aids (vector DB matrix, MemoryBank vs A-MEM vs Search-o1) via deep links to Compass Artifact sections.
3. **Hands-On Demo Notebook** – Produce `lesson-14/memory_systems_demo.ipynb` (or equivalent) that:
   - Uses existing datasets (trajectory traces, planning benchmarks) to simulate memory writes/reads.
   - Demonstrates MemoryBank-style decay, A-MEM-style note linking, and context compression toggles (e.g., LLMLingua-inspired summarization).
   - Exposes metrics (hit rate, retained tokens, cost savings) and exports JSON for `results/`.
4. **Backend Enhancements** – Extend `backend/multi_agent_framework.py` (and/or helper modules) to support pluggable memory stores (in-memory dict, vector DB stub, Redis cache) plus instrumentation hooks for guardrails and cost accounting. Provide docstring references to new tutorial sections.
5. **Safety & Cost Hooks** – Document and (where practical) implement:
   - Guardrail checkpoints (constitutional prompts or filter hooks) for any retrieval/persistence step.
   - Cost dashboards (token/logging) showing before/after compression savings.
6. **Duplication Safeguards** – Each new artifact must include a “Source References” callout pointing to relevant sections of `agents_memory.txt` and Compass Artifact; reviewers should validate that no section copies more than two consecutive sentences from those sources.

## 5. Non-Goals
- Rewriting or abridging `agents_memory.txt` or Compass Artifact contents.
- Introducing new proprietary datasets beyond the existing Lesson 14 JSON suites.
- Building production-grade vector database integrations (stubs and mock adapters are sufficient).
- Overhauling the entire PVE architecture beyond what’s necessary to demonstrate memory hooks.

## 6. Design Considerations
- **Cross-link First:** Follow a “summarize + cite” approach; use callout boxes or footnotes that deep link into the canonical docs.
- **Modularity:** Memory features should be pluggable (feature flags or configuration blocks) so learners can enable/disable them when running notebooks in DEMO vs FULL mode.
- **Consistency:** Align terminology (e.g., “working memory” vs “short-term memory”) with `agents_memory.txt` to prevent terminology drift.
- **Accessibility:** Provide diagrams via existing Mermaid infrastructure (e.g., extend `diagrams/pattern_decision_tree.mmd` or add new ones) rather than embedding screenshots.

## 7. Technical Considerations
- Reuse existing `MemoryManager` constructs instead of creating parallel services; add interfaces or adapters for episodic/semantic stores.
- Notebook demos should default to offline-safe operations (no paid APIs) and match the DEMO/FULL switch pattern used in other Lesson 14 notebooks.
- For context compression, reference open-source tooling (LLMLingua or similar) but rely on deterministic summarization scripts unless API keys are provided.
- Logging should piggyback on the current results export format (JSON under `lesson-14/results/`) to stay compatible with `evaluation_dashboard.py`.

## 8. Success Metrics
- 100% of new/updated docs include explicit cross-links to `agents_memory.txt` and Compass Artifact (manual checklist).
- Memory demo notebook shows ≥50% token reduction when compression is enabled and reports the delta in exported metrics.
- Backend instrumentation surfaces memory hit-rate and guardrail pass/fail counts within 5 minutes of running the demo notebook.
- Curriculum reviewers confirm that the Memory Systems Track can be completed in ≤3 hours and bridges into existing planning/evaluation exercises without redundancy.

## 9. Open Questions
1. Which vector database (if any) should the pluggable adapter simulate by default (e.g., Pinecone-like interface vs pgvector)?  
2. Should cost/safety guardrails be implemented via existing evaluation notebooks or as a new consolidated dashboard?  
3. Are there enterprise partner requirements (e.g., Klarna case study assets) that must be referenced explicitly in the tutorials?

