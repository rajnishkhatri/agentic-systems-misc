# Aggregated Design Patterns for GenAI Systems

This document consolidates design patterns for AI agents, content generation, safeguards, and RAG systems.

---

## 1. AI Code Agent Patterns

### Index-Aware Code Retrieval
**Usage**: Use when queries use different terminology than codebase, require cross-file relationships, or fine-grained details. Components include Hypothetical Code Embedding (HyCE), Query Expansion, Hybrid Code Search, and Code Graph RAG.
**Constraints**: Requires building AST-based code graphs or maintaining vector indices. Hybrid search requires tuning alpha parameter.
**Decision Matrix**:
- `alpha=0.2`: Searching for specific function/class names (Keyword heavy).
- `alpha=0.5`: Finding implementations of a concept.
- `alpha=0.8`: Exploring "how does this work" questions (Semantic heavy).
**Anti-patterns**: Relying solely on semantic search for exact symbol lookups; ignoring graph relationships in complex architectures.

### Code Context Postprocessing
**Usage**: Refine retrieved code chunks to remove noise and improve relevance. Techniques include Code Relevance Reranking, Contextual Compression, Symbol Disambiguation, and Version Filtering.
**Constraints**: Adds latency due to LLM-based reranking or compression steps.
**Decision Matrix**:
- Use Reranking when retrieved chunks are similar but vary in task relevance.
- Use Compression when context window is limited or noise is high.
**Anti-patterns**: Passing raw, large files to context without filtering; assuming retrieved chunks from different versions are compatible.

### Trustworthy Code Generation
**Usage**: Generate code that matches codebase style and avoids hallucinations. Techniques: Out-of-Scope Detection, Code Citations, Code Guardrails, Corrective Code RAG, Self-Reflective Generation.
**Constraints**: Requires defining "in-scope" boundaries and potentially maintaining a separate validation step/model.
**Decision Matrix**:
- Use Guardrails for security-critical generation.
- Use Citations when traceability to source patterns is required.
**Anti-patterns**: Generating code without checking for existing APIs; executing generated code without sandboxing or validation; ignoring "out of scope" signals.

### Deep Code Search (Agentic Code Exploration)
**Usage**: For complex tasks requiring multi-file understanding or architectural mental models. Uses an Iterative Search-Think-Generate Loop.
**Constraints**: High latency and token cost due to iterative loops.
**Decision Matrix**:
- Use for "Explain this codebase" or "Complex architecture" tasks.
- Skip for simple bug fixes or single-file edits.
**Anti-patterns**: Infinite loops without convergence criteria; failing to update "gaps" in understanding during iteration.

---

## 2. Content Style & Control Patterns

### Logits Masking
**Usage**: Enforce strict rules (branding, compliance, formatting) by zeroing out probabilities of invalid tokens during sampling.
**Constraints**: Requires access to model logprobs (often not available in closed APIs). Adds latency per token.
**Decision Matrix**:
- Use when rules can be expressed programmatically and strict enforcement is required.
**Anti-patterns**: "Try-and-try-again" (generate -> check -> retry) for high-probability failure cases.

### Grammar
**Usage**: Constrain output to a formal grammar (BNF) or schema (JSON, Pydantic).
**Constraints**: Can increase refusal rates if grammar is too restrictive.
**Decision Matrix**:
- Use BNF/Pydantic when output must be machine-readable or strictly structured.
- Use Pydantic/Dataclass for easier implementation vs BNF.
**Anti-patterns**: Prompting "Please answer YES or NO" without structural constraints; over-constraining grammar leading to "endless whitespace" loops.

### Style Transfer
**Usage**: Convert content to a specific style using examples (Few-Shot or Fine-Tuning).
**Constraints**: Few-shot uses context window; Fine-tuning requires data curation and training infrastructure.
**Decision Matrix**:
- Use Few-Shot for 1-10 examples.
- Use Fine-Tuning for 100+ examples or when latency/cost of long prompts is prohibitive.
**Anti-patterns**: Zero-shot prompting for nuanced style requirements (model reverts to generic "marketing" tone).

### Reverse Neutralization
**Usage**: Generate specific style when no input-output pairs exist. Neutralize styled content to create synthetic inputs, then train model to reverse the process.
**Constraints**: Requires a capable foundation model to perform neutralization.
**Decision Matrix**:
- Use when you have examples of the target style but no "source" content to train mapping.
**Anti-patterns**: Using a poor neutralizer that loses semantic meaning; failing to validate content preservation.

### Content Optimization
**Usage**: Optimize style via preference tuning (DPO) when explicit style rules are unknown.
**Constraints**: Requires an evaluator (human or automated) to rank pairs.
**Decision Matrix**:
- Use when "good" is defined by outcome metrics (e.g., click-through rate) rather than static rules.
**Anti-patterns**: Optimizing against a flawed evaluator (gaming the metric); ignoring "in-distribution" requirements for training data.

---

## 3. Reliability & Evaluation Patterns

### LLM-as-Judge
**Usage**: systematic evaluation using LLMs with custom scoring rubrics.
**Constraints**: Judges can be biased (self-preference, leniency).
**Decision Matrix**:
- Use for qualitative assessments where rule-based metrics fail.
- Use pairwise comparison to reduce leniency bias.
**Anti-patterns**: Using the same model to judge its own output; using single aggregate scores without criteria; hardcoding pass/fail thresholds without justification.

### Reflection
**Usage**: Iterative self-critique and refinement loops to improve output quality.
**Constraints**: Increases latency and cost (N calls).
**Decision Matrix**:
- Use for complex code generation, reasoning tasks, or high-stakes content.
- Use `max_iterations` to prevent infinite loops.
**Anti-patterns**: Infinite loops; critique by the same model instance without context isolation (sycophancy); failing to preserve critique history.

### Dependency Injection
**Usage**: Decouple LLM logic from business logic to enable testing and model swapping.
**Constraints**: Requires architectural boilerplate (interfaces/protocols).
**Decision Matrix**:
- Use for production systems requiring unit testing and model agility.
**Anti-patterns**: Hardcoding LLM clients inside business functions; making real API calls during unit tests.

### Prompt Optimization
**Usage**: Systematically refine prompts using datasets and evaluators (DSPy-style).
**Constraints**: Requires evaluation dataset and metric. Build-time cost.
**Decision Matrix**:
- Use when prompt performance is brittle or needs improvement across a distribution of inputs.
**Anti-patterns**: Manual "vibes-based" prompt tweaking; optimizing without a holdout test set.

---

## 4. Agentic & Workflow Patterns

### Tool Calling
**Usage**: Enable LLM to invoke external APIs for real-time data or actions.
**Constraints**: Model accuracy degrades with >10 tools.
**Decision Matrix**:
- Use for real-time data, calculations, or system actions.
- Use Router pattern if tools > 10.
**Anti-patterns**: Vague tool descriptions; side-effects in "read-only" tools; overloading model with too many tools.

### Code Execution
**Usage**: LLM generates DSL/code (SQL, Python, Graphviz) executed in a sandbox.
**Constraints**: Security risks; requires robust sandboxing (Docker/WASM).
**Decision Matrix**:
- Use for precise math, data analysis, or generating visual assets (charts/graphs).
**Anti-patterns**: Executing code without sandboxing; using general-purpose languages when a restricted DSL would suffice.

### ReAct (Reasoning + Acting)
**Usage**: Interleave reasoning and tool use for multi-step problems.
**Constraints**: High latency; can get stuck in loops.
**Decision Matrix**:
- Use for tasks requiring exploration or where next steps depend on previous results.
**Anti-patterns**: Infinite loops (set max steps); simple tasks that could be solved with one call.

### Router
**Usage**: Classify and direct requests to specialized agents or workflows.
**Constraints**: Router accuracy becomes the bottleneck.
**Decision Matrix**:
- Use when domain scope is broad and specialized prompts/tools are needed for sub-domains.
**Anti-patterns**: Routing everything through a single monolithic agent; ambiguous routing criteria.

### Sequential Workflow
**Usage**: Linear chain of steps where output of A is input to B.
**Constraints**: Error propagation (garbage in, garbage out).
**Decision Matrix**:
- Use for predictable, multi-stage transformations (e.g., Research -> Draft -> Edit).
**Anti-patterns**: Using ReAct for strictly linear processes (unnecessary overhead).

### Multiagent Collaboration
**Usage**: Orchestrate multiple specialized agents (Hierarchical, Peer-to-Peer, or Market-based).
**Constraints**: High complexity; coordination overhead; high token cost.
**Decision Matrix**:
- Use for complex tasks requiring distinct personas/expertise (e.g., "Red Team" vs "Blue Team").
**Anti-patterns**: "Role drift" where agents ignore their persona; circular conversations without progress (requires termination conditions).

---

## 5. Security & Safeguard Patterns

### Action-Selector
**Usage**: Whitelist allowed actions; no feedback loop to agent.
**Constraints**: Limits agent autonomy.
**Decision Matrix**:
- Use for high-risk actions (payments, deletions).
**Anti-patterns**: Allowing agent to define parameters without validation.

### Plan-Then-Execute
**Usage**: Create fixed plan upfront, then execute mechanically.
**Constraints**: Cannot adapt to runtime errors/feedback.
**Decision Matrix**:
- Use for predictable workflows where deviation risks security.
**Anti-patterns**: Allowing the "Execute" phase to replan or use LLM judgment.

### Dual-LLM / Map-Reduce (Security)
**Usage**: Isolate untrusted data processing (Unprivileged LLM) from tool usage (Privileged LLM).
**Constraints**: Increased cost/latency (2+ calls).
**Decision Matrix**:
- Use when processing untrusted user content (emails, uploads).
**Anti-patterns**: Passing raw untrusted content to the Privileged LLM.

### Context-Minimization
**Usage**: Strip original prompts/context from subsequent steps to prevent injection propagation.
**Constraints**: May lose helpful context.
**Decision Matrix**:
- Use in multi-step chains where initial input might contain prompt injections.
**Anti-patterns**: Passing full conversation history to privileged tools unnecessarily.

### Guardrails (Input/Output)
**Usage**: Layers of protection (PII, Toxicity, Topic) around LLM.
**Constraints**: Latency; false positives.
**Decision Matrix**:
- Always use PII/Injection detection for public apps.
- Use Output guardrails for brand safety.
**Anti-patterns**: Relying solely on prompt instructions for safety; ignoring false positive rates.

---

## 6. GenAI Safeguard Patterns (Content Production)

### Template Generation
**Usage**: Pre-generate templates with placeholders -> Human Review -> Deterministic Fill.
**Constraints**: Finite variations; strictly static structure.
**Decision Matrix**:
- Use for high-volume, high-risk communications (e.g., customer service emails).
- Use when variations < 10,000.
**Anti-patterns**: Using for highly personalized/unique content (use Assembled Reformat).

### Assembled Reformat
**Usage**: Phase 1: Assemble facts (deterministic). Phase 2: Reformat/Rewrite (LLM).
**Constraints**: Requires structured data sources.
**Decision Matrix**:
- Use when facts must be accurate but presentation needs fluency (e.g., product pages).
**Anti-patterns**: Allowing Phase 2 to add new information (hallucination risk).

### Self-Check
**Usage**: Use logprobs/entropy to detect potential hallucinations.
**Constraints**: Requires model access to logprobs.
**Decision Matrix**:
- Use for factual validation when external ground truth is missing.
**Anti-patterns**: Trusting low-confidence outputs without verification.

---

## 7. Extending Capabilities

### Chain of Thought (CoT)
**Usage**: "Think step-by-step" to improve reasoning.
**Constraints**: Increased token output.
**Decision Matrix**:
- Use Zero-shot CoT for quick wins.
- Use Few-shot CoT for complex logic patterns.
**Anti-patterns**: Using CoT for simple fact retrieval (wasteful).

### Tree of Thoughts (ToT)
**Usage**: Explore multiple solution paths; backtrack if needed.
**Constraints**: Very high cost (30-50x calls). High latency.
**Decision Matrix**:
- Use for strategic planning, complex puzzles, or creative exploration.
**Anti-patterns**: Using for linear tasks suitable for CoT.

### Adapter Tuning (LoRA)
**Usage**: Adapt style/format with 100+ examples.
**Constraints**: Does not teach new facts.
**Decision Matrix**:
- Use for consistent formatting/tone.
**Anti-patterns**: Using LoRA to teach knowledge (use RAG).

---

## 8. RAG Knowledge Patterns

### Basic RAG
**Usage**: Retrieve chunks -> Generate answer.
**Constraints**: Poor performance on synonyms or complex queries.
**Decision Matrix**:
- Use for simple factual retrieval.
**Anti-patterns**: Retrieving without reranking; tiny chunks without context.

### Semantic Indexing
**Usage**: Embedding-based retrieval for conceptual matching.
**Constraints**: Can miss exact keywords (e.g., part numbers).
**Decision Matrix**:
- Use hybrid (Keyword + Semantic) for best results.
**Anti-patterns**: Using semantic search alone for ID/SKU lookups.

### Indexing at Scale
**Usage**: Handling metadata, freshness, and updates.
**Constraints**: Infrastructure complexity.
**Decision Matrix**:
- Use when knowledge base changes frequently or requires filtering (permissions, dates).
**Anti-patterns**: Full re-indexing for small updates; ignoring temporal contradictions.

---

## 9. Data Processing Patterns (Chunking)

### Length-Based Chunking
**Usage**: Split text by fixed character/token count with overlap.
**Constraints**: Breaks context at arbitrary points (mid-sentence).
**Decision Matrix**:
- Use for uniform processing or when content lacks structure.
**Anti-patterns**: Zero overlap (loses boundary context).

### Sentence/Paragraph Chunking
**Usage**: Split by sentence boundaries or paragraph breaks.
**Constraints**: Variable chunk sizes may complicate batching.
**Decision Matrix**:
- Use for instructional content or prose where sentence integrity matters.
**Anti-patterns**: Forcing fixed length on paragraph chunks (breaking them again).

### Semantic Chunking
**Usage**: Use embedding similarity to find topic boundaries.
**Constraints**: Computationally expensive (embedding every sentence).
**Decision Matrix**:
- Use for diverse transcripts or unstructured text with distinct topics.
**Anti-patterns**: Using on homogeneous text where similarity doesn't vary.

### Hierarchical Chunking (RAPTOR)
**Usage**: Recursively summarize and cluster chunks for multi-level retrieval.
**Constraints**: High complexity and token cost for summarization.
**Decision Matrix**:
- Use for long documents (books, papers) requiring holistic understanding.
**Anti-patterns**: Using for short documents (<10 pages).
