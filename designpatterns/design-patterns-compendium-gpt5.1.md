# Design Patterns Compendium (gpt5.1)

Consolidated from `designpatterns/` sources: `ai_code_agent_design_patterns.md`, `code-agent-decision-matrix*.md`, `content_style_control_patterns.md`, `SKILL_extending_llm_capabilities.md`, `eval_skills.md`, `addressing-constraints-patterns/`, `enablingagentstotakeaction/`, `files/` (RAG/Chunking), and `genai-safeguards/`.

## How to Use (Pólya-aligned)
- **Understand** the task intent, risk, scope, data trust level, and required outputs.  
- **Plan** by picking a primary pattern (table below) and safeguards; note constraints and success checks.  
- **Tasks**: break into retrieval/prep → orchestration → generation → verification → reporting.  
- **Execute** following pattern-specific constraints and guardrails; cite sources.  
- **Reflect**: verify against checklists; capture gaps/assumptions for next runs.

## Quick Selection Matrix
| Need | Primary Pattern(s) | Key Constraints / Checks | Anti-Patterns |
|------|-------------------|---------------------------|---------------|
| Codebase answers, multi-file context | Index-Aware Retrieval (HyCE, query expansion, hybrid, graph RAG) | Maintain version metadata; rerank; compress context; disambiguate symbols | Using single search mode; ignoring branch/freshness |
| Improve retrieval quality | Code Context Postprocessing (rerank, compression) | Keep imports for compressed chunks; detect duplicates | Blindly stuffing whole files |
| Safe code generation | Trustworthy Gen (scope check, citations, guardrails, corrective/self-RAG) | Block dangerous ops; run syntax/style/tests; cite sources | Free-form code without validation or citations |
| Complex code understanding | Deep Code Search (search-think-generate loop, gap ID, multi-hop) | Track gaps; stop when complete | One-shot reading without evaluation |
| Content style control | Logits Masking / Grammar / Style Transfer / Reverse Neutralization / Content Optimization (DPO) | Grammar/BNF when rules; logit masking needs logprobs; DPO requires solid evaluator | “Beg for compliance”; zero-shot style for brand-critical |
| Extend LLM capability | CoT / Few-shot CoT / ToT / Adapter Tuning / Evol-Instruct | ToT = high latency; adapters for style/format; instruction tuning for new task | ToT for simple tasks; adapters for new knowledge |
| Agentic orchestration | Tool Calling, Code Execution, ReAct, Router, Sequential, Multiagent (hier/peer/market) | Limit tools (≤10); sandbox code; add timeouts | Unbounded ReAct loops; monolithic agents |
| Security-critical actions | Action-Selector, Plan-Then-Execute, Dual-LLM, Map-Reduce, Code-Then-Execute, Context-Minimization | Whitelist actions; separate trusted/untrusted; no tool feedback to unprivileged LLM | Letting untrusted data reach tool-enabled LLM |
| RAG correctness | RAG patterns (Basic→Semantic→Index-at-Scale), Chunking strategies | Hybrid BM25+semantic; right-size chunks w/ overlap; metadata; freshness filters | Embedding-only retrieval for codes; no overlap; no metadata |
| Reliability & eval | LLM-as-Judge, Reflection loops, Dependency Injection, Prompt Optimization | Different model for judging; bounded iterations; injectable providers; datasets for prompts | Self-judging; infinite reflection; hardcoded LLMs/prompts |
| Multiagent robustness | Failure taxonomy (role drift, withholding, resets, cascades, hallucinations) + debugging workflow | Role boundaries, info-sharing protocol, completion checklist, validation gates | No trace/logs; no max_turns; no verification agent |

## Pattern Capsules (usage → constraints → decisions → anti-patterns)

### Code Retrieval & Generation
- **Index-Aware Retrieval**: use HyCE, query expansion, hybrid search, and code graph RAG when queries differ from code terms or need relational context. Keep branch/version metadata; rerank for task relevance; disambiguate symbols; compress context retaining imports.  
- **Code Context Postprocessing**: rerank by usefulness, compress to relevant spans, detect same-name collisions, filter by branch/freshness. Avoid dumping whole files.  
- **Trustworthy Generation**: scope/out-of-scope detection, citation requirement, guardrails (pre/post), corrective/self-RAG loops. Block dangerous patterns; run syntax/style/tests; cite sources. Anti: free-form code or retries without checks.  
- **Deep Code Search**: iterative search→think→generate→evaluate with gap tracking and multi-hop queries. Stop when evaluation says complete. Anti: single-pass read of large codebases.
- **Code Evaluation Metrics**: syntax, style, relevance, grounding, completeness; weighted scoring encouraged.

### Content Style Control
- **Logits Masking** (strict, needs logprobs): enforce vocab/format at sampling; plan backtracking for dead ends. Anti: try-and-retry if >10% need regen.  
- **Grammar / Structured Output**: BNF/JSON/dataclass; choose BNF when rules are rich/dynamic; dataclass when simpler. Anti: “please follow JSON” without constraints.  
- **Style Transfer**: few-shot/fine-tune with I/O pairs; validate example quality/coverage.  
- **Reverse Neutralization**: neutralize styled samples → flip for training; ensure neutral form preserves meaning (emb similarity).  
- **Content Optimization (DPO)**: generate pairs → evaluate → preference tune; evaluator quality is the risk; monitor for metric gaming.

### LLM Capability Extension
- **CoT** (zero/few-shot/auto): for stepwise reasoning; use few-shot on small models; anti: zero-shot on weak models for math.  
- **Tree of Thoughts**: multi-path exploration; beam/branch scoring; expect 30–50 calls; avoid for simple tasks/low-latency.  
- **Adapter Tuning**: 100–10k examples for style/format; not for new knowledge.  
- **Evol-Instruct**: generate & filter instruction datasets for new capabilities; requires eval filter; high effort.  
- **Anti-patterns**: Using adapters for knowledge; ToT for trivial tasks; instruction tuning for mere style.

### Agentic Orchestration Patterns
- **Tool Calling**: clear schemas, enums, docstrings; limit tools; timeouts; descriptive errors; integrate MCP when multi-provider.  
- **Code Execution**: sandboxed, validate before run, forbid dangerous ops, resource limits, reflection on errors.  
- **ReAct**: interleave think/act/observe; set max iterations; termination criteria.  
- **Router**: classify to specialized agents; deterministic (temp=0) structured routing.  
- **Sequential Workflow**: explicit stages, handoff keys, processors; good for linear pipelines.  
- **Multiagent Collaboration**: choose hierarchy (manager/worker), peer review panel, or market auction based on coordination need. Set max_turns, summaries, role prompts.

### Security & Safeguards
- **Prompt-Injection Defenses**: Action-Selector (no tool feedback), Plan-Then-Execute (immutable plan), Dual-LLM (trusted vs sandboxed), Map-Reduce (untrusted docs stay isolated), Code-Then-Execute (LLM writes code; code processes data), Context-Minimization (strip original prompt later).  
- **Validation**: Pydantic/validators for tool args; SQL allow-list; forbid destructive ops.  
- **Sandboxing**: container or resource-limited execution; no network; CPU/mem/time caps.  
- **Audit Logging**: structured logs for prompts/guards/feedback/tool calls.  
- **GenAI Safeguards**: Template Generation (pre-reviewed), Assembled Reformat (two-phase factual→format), Self-Check (confidence/logprob), Guardrails (I/O protection chain); compose input→pattern→output guardrails.

### Reliability, Evaluation, and Prompt Ops
- **LLM-as-Judge**: rubric-based scoring, bias mitigation (different model, pairwise, jury), structured outputs. Anti: single 1–10 score or self-judging.  
- **Reflection Loops**: bounded iterations, critique history, alternate generator/critic models; code reflection includes syntax/tests/style checks. Anti: unbounded retries.  
- **Dependency Injection**: protocols for LLM/providers/tools/evaluators; mock/replay for tests; factory per env. Anti: hardcoded clients/global state.  
- **Prompt Optimization**: externalized templates with versions/metadata; DSPy-style bootstrap/evolution; CI gating with datasets; avoid scattered literals and subjective tweaks without eval set.

### RAG & Chunking Patterns
- **RAG Ladder**: Basic (BM25) → Semantic → Index-at-Scale → Index-Aware Retrieval → Node Postprocessing → Trustworthy Gen → Deep Search.  
- **Chunking Strategies**: length+overlap (general), sentence (instructions), paragraph (legal), doc-structure (MD/HTML), semantic-shift, hierarchical (RAPTOR), table-specific (row/window). Keep 10–20% overlap; preserve metadata.  
- **Decision Matrices**: retrieval method (BM25 vs semantic vs hybrid), chunking by doc type, RAG vs full-context choice, embedding model selection.  
- **Troubleshooting**: vocab mismatch (add semantic/expansion), irrelevant chunks (rerank/metadata), exact codes (BM25), hallucinations (explicit context-only + citations), contradiction (timestamp/authority filters), latency/cost (cache, ANN, smaller models).

### Code-Agent Decision Rules (from decision-matrix)
- **Classify tasks** (bug/feature/refactor/review/migration/investigation).  
- **Clarify** when ambiguous, destructive, security, or breaking-change risks; batch questions.  
- **Scope** rules: small/medium/large/critical → plan depth and approvals.  
- **Quality**: follow existing patterns, style guides, keep changes minimal, complexity thresholds.  
- **Error/Test/Doc/Security/Communication**: retry budgets, test triggers, doc updates, hard/soft stops, progress/assumption reporting, context priority.  
- **Caching & Guardrails**: cache deterministic ops; run guardrails in parallel; log prompts/guards/feedback.

### Multiagent Failure Modes & Debugging
- **Specification**: role confusion, instruction drift, premature termination → stronger roles, reminders, completion checklist.  
- **Interagent**: withholding, conversation resets, reasoning-action mismatch → sharing protocol, context summaries, structured outputs.  
- **Verification**: cascading errors, hallucinations → validation gates, citation/verification agent.  
- **Debug Workflow**: capture full trace, binary-search failing step, reproduce deterministically, add validation gates and checkpoints.

## Consolidation Checklists
- **Before execution**: choose pattern + safeguards; define success criteria, iteration limits, tool limits, sandboxing, logging, citation requirement.  
- **During**: enforce validation (args/code), apply rerank/compression, track gaps, apply guardrails in parallel.  
- **After**: verify outputs vs criteria; run reflection; record assumptions, unresolved gaps, and candidate improvements.

## Residual Risks / Gaps
- Style control requires provider logprobs for logits masking.  
- Instruction tuning/Evol-Instruct need curated evaluators—high effort.  
- ToT / multiagent patterns carry latency and coordination risk; set budgets.  
- External data/tool calls demand environment-specific security not covered here (network, secrets management).

