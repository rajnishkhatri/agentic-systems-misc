# PRD: Advanced RAG & Agent Evaluation Tutorial System (Lessons 12-14)

## Introduction/Overview

This PRD defines the development of a comprehensive **Advanced RAG & Agent Evaluation Tutorial System** consisting of three lesson-based deep-dive tutorials (Lessons 12, 13, 14) that systematically teach advanced RAG and agent evaluation techniques, **supplementing** (not duplicating) existing Lessons 9-11 and HW1-5.

**Major Update (2025-11-14)**: Lesson 14 significantly expanded to integrate Google's **AgentCompanion whitepaper** (February 2025), covering production-grade agent evaluation methodologies, multi-agent architectures, agentic RAG patterns, and real-world case studies (Automotive AI, Google Co-Scientist).

### Problem Statement

Current evaluation education covers foundational metrics (Lessons 9-11) and basic RAG retrieval (HW4), but lacks coverage of:
- **Advanced retrieval patterns**: Semantic search, hybrid retrieval, chunking optimization
- **RAG generation quality**: Attribution detection, hallucination in RAG systems, context utilization
- **Agent evaluation methodology**: Trajectory evaluation, autoraters, public benchmarks (BFCL, PlanBench, AgentBench)
- **Multi-agent architectures**: 11 core components, 5 coordination patterns (hierarchical, diamond, peer-to-peer, collaborative, adaptive loop)
- **Agentic RAG**: Context-aware query expansion, multi-step reasoning, adaptive source selection, validation agents
- **AgentOps**: DevOps → MLOps → AgentOps progression, observability, metrics-driven development
- **Production patterns**: Contextual retrieval, reranking, end-to-end evaluation, enterprise deployment
- **Real-world case studies**: Automotive AI with 5 specialized agents, Google Co-Scientist multi-agent research system

Students need production-ready evaluation frameworks for modern RAG and agent systems that bridge theory to practice with real case studies.

### Goal

Build a **three-lesson tutorial system** that teaches advanced RAG and agent evaluation techniques, providing students with:
1. **Hybrid retrieval expertise**: Combining BM25 + embeddings for 10-15% performance improvement
2. **RAG generation evaluation**: Attribution, hallucination, and faithfulness detection
3. **Agent evaluation mastery**: Trajectory evaluation (6 metrics), autoraters, public benchmarks, human-in-the-loop
4. **Multi-agent system design**: 5 coordination patterns with hands-on automotive AI case study
5. **Agentic RAG implementation**: Query expansion, multi-step reasoning, validation agents, search optimization
6. **Enterprise deployment**: Google Agentspace, NotebookLM, contract-based agents, AgentOps principles

---

## Goals

1. **Zero Duplication**: Supplement existing HW4 (BM25, Recall@k) and Lessons 9-11 (perplexity, judges, comparative eval) with NEW content only
2. **Production Patterns**: Teach industry-standard RAG and agent evaluation techniques from Google AgentCompanion whitepaper
3. **Practical Integration**: Extend existing workspace evaluation utilities with advanced techniques
4. **Cost Efficiency**: All interactive notebooks execute in <$25 total (Lesson 14 expanded with 8 new notebooks)
5. **Cross-Domain Testing**: Use recipe corpus + Bhagavad Gita Q&A + automotive AI scenarios for robust evaluation
6. **Reusable Frameworks**: Create evaluation template library for RAG generation and agents
7. **Agent Evaluation Mastery**: Implement 6 trajectory metrics, autoraters, and public benchmark evaluations (BFCL, PlanBench)
8. **Multi-Agent Expertise**: Build 5 coordination patterns with real automotive AI case study
9. **Agentic RAG Implementation**: Deploy query expansion, multi-step reasoning, and validation agents
10. **Enterprise Readiness**: Cover AgentOps, observability, Google Agentspace, contract-based agents
11. **Case Study Learning**: Hands-on experience with Google Co-Scientist and Automotive AI architectures
12. **Theory-to-Practice**: Bridge academic research (AgentCompanion) with practical recipe bot implementation

---

## User Stories

### Story 1: ML Engineer Building Production RAG System
**As an** ML engineer deploying a RAG system to production
**I want to** evaluate attribution, hallucination, and context utilization
**So that** I can ensure my LLM responses are grounded in retrieved documents

**Acceptance Criteria**:
- Can detect 80%+ of attribution failures (LLM not citing sources)
- Can measure hallucination rate (claims not in context)
- Can track context utilization (which docs LLM actually uses)
- Can implement end-to-end RAG pipeline evaluation in 2 hours

### Story 2: Researcher Comparing Retrieval Strategies
**As a** researcher comparing BM25 vs semantic vs hybrid retrieval
**I want to** measure context precision/recall and implement hybrid search
**So that** I can optimize retrieval for my domain with scientific rigor

**Acceptance Criteria**:
- Can implement semantic retrieval with embeddings (OpenAI/Cohere)
- Can combine BM25 + semantic with Reciprocal Rank Fusion (RRF)
- Can achieve 10-15% Recall@5 improvement over BM25 alone
- Can evaluate chunking strategies (character/sentence/paragraph/recursive)
- Can measure context precision/recall using AI judges

### Story 3: AI Engineer Validating Agent Systems (EXPANDED with AgentCompanion)
**As an** AI engineer building autonomous agents
**I want to** validate agent planning, tool calls, trajectories, and final responses using production-grade evaluation frameworks
**So that** I can catch 85%+ of agent failures before production deployment and implement AgentOps best practices

**Acceptance Criteria**:
- Can validate agent plans (tool selection, parameter correctness, goal achievement)
- Can measure tool call accuracy (invalid tools, wrong parameters)
- **Can evaluate trajectories using 6 metrics** (exact match, in-order, any-order, precision, recall, single-tool)
- **Can build and calibrate autoraters** for final response evaluation (goal achievement, accuracy, tone)
- **Can evaluate agents against public benchmarks** (BFCL tool calling, PlanBench planning)
- Can implement ReAct/Reflexion patterns with evaluation
- Can build multi-agent orchestration with memory management
- Can profile agent efficiency (cost, latency, steps to completion)
- **Can implement AgentOps**: observability, traces, business KPIs, human feedback loops

### Story 4: Multi-Agent System Architect (NEW - from AgentCompanion)
**As a** multi-agent system architect
**I want to** design and implement specialized agents with coordination patterns for complex domains
**So that** I can build production systems like automotive AI or research assistants with measurable performance

**Acceptance Criteria**:
- **Can implement 5 coordination patterns**: Hierarchical, Diamond, Peer-to-Peer, Collaborative, Adaptive Loop
- **Can build specialized agents** with distinct roles (Planner, Retriever, Execution, Evaluator)
- **Can design agent architectures** with 11 core components (Memory, Cognitive, Tools, Flow/Routing, Communication, Registry)
- **Can evaluate multi-agent systems**: cooperation, task assignment, agent utilization, scalability
- **Can implement automotive AI case study** (5 specialized agents + orchestrator)
- **Can apply agentic RAG** with query expansion, multi-step reasoning, validation agents
- **Can optimize search before agents**: semantic chunking, metadata, rankers, grounding checks
- Can measure pattern performance (accuracy, latency, cost) and select optimal pattern for use case

### Story 5: Enterprise AI/ML Platform Engineer (NEW - from AgentCompanion)
**As an** enterprise AI/ML platform engineer
**I want to** deploy agent systems with enterprise security, observability, and contract-based specifications
**So that** I can scale AI across organization with governance and reliability

**Acceptance Criteria**:
- **Can implement AgentOps pipeline**: version control, CI/CD, automated testing, logging, metrics
- **Can deploy with enterprise security**: SSO, RBAC, VPC Service Controls, IAM integration
- **Can build contract-based agents** with negotiation, execution, feedback, subcontracts
- **Can integrate Google Agentspace** features (multi-modal search, blended RAG, knowledge graphs)
- **Can deploy NotebookLM Enterprise** for research assistance with audio summaries
- **Can implement observability**: traces with OpenTelemetry, business KPIs, goal completion tracking
- **Can distinguish agent types**: Assistants (user-interactive) vs. Automation agents (background)
- Can manage agent fleets with monitoring UX for orchestration and task assignment

### Story 6: Course Student Learning Advanced Evaluation (EXPANDED)
**As a** student completing Lessons 9-11
**I want to** learn RAG generation and agent evaluation techniques from industry-leading research (Google AgentCompanion)
**So that** I can evaluate modern AI systems beyond basic retrieval metrics and build production-ready multi-agent systems

**Acceptance Criteria**:
- Lesson 12 teaches hybrid retrieval patterns NOT in HW4
- Lesson 13 teaches RAG generation evaluation NEVER covered before
- **Lesson 14 teaches comprehensive agent evaluation** (trajectory metrics, autoraters, benchmarks, multi-agent patterns, agentic RAG, AgentOps)
- **Can learn from real case studies**: Automotive AI (5 agents), Google Co-Scientist (research multi-agent system)
- **Can implement 13 concept tutorials, 10 notebooks, 6 backend modules** across Lesson 14 alone
- All lessons integrate with existing backend modules
- **Total execution cost <$25 for full hands-on experience** (expanded from $15 due to 8 new Lesson 14 notebooks)

---

## Functional Requirements

### Lesson 12: Hybrid Retrieval & Context Quality

#### FR-L12.1: Concept Tutorials (Markdown)
The system **must** provide the following markdown tutorials:

- `embedding_based_retrieval.md` (reading time: 20-25 min)
  - Semantic search fundamentals: embeddings vs lexical
  - Vector databases and similarity search
  - k-NN (exact) vs ANN (approximate) algorithms
  - Popular vector search methods: FAISS, HNSW, LSH, Annoy
  - When semantic retrieval outperforms BM25
  - Cost and latency considerations

- `hybrid_search_strategies.md` (reading time: 18-22 min)
  - Combining term-based and semantic retrieval
  - Reciprocal Rank Fusion (RRF) algorithm
  - Two-stage reranking patterns
  - Sequential vs parallel retrieval
  - Tuning hybrid search weights (alpha parameter)
  - When hybrid search is worth the complexity

- `context_quality_evaluation.md` (reading time: 20-25 min)
  - Context precision vs context recall
  - Chunking strategy impact on retrieval
  - Contextual retrieval (Anthropic's chunk augmentation)
  - Overlap strategies for chunk boundaries
  - Chunk size optimization experiments
  - Evaluating chunking with AI judges

#### FR-L12.2: Interactive Notebooks (Jupyter)
The system **must** provide the following executable notebooks:

- `hybrid_search_comparison.ipynb`
  - Compare BM25, semantic, and hybrid retrieval
  - Implement RRF fusion for hybrid ranking
  - Measure Recall@1/3/5 for each method
  - Cost analysis (BM25 free, embeddings $0.0001/1k tokens)
  - Execution time: <8 minutes, Cost: $1.50-2.50 (FULL), $0.30-0.50 (DEMO)

- `chunking_optimization.ipynb`
  - Test 5 chunking strategies (character/sentence/paragraph/recursive/semantic)
  - Measure retrieval performance per strategy
  - Analyze chunk size vs retrieval quality
  - Identify optimal chunking for recipe + Gita domains
  - Execution time: <5 minutes, Cost: $1.00-1.50 (FULL), $0.20-0.30 (DEMO)

#### FR-L12.3: Reference Implementation
The system **must** provide `backend/semantic_retrieval.py` with:
- `generate_embeddings(texts: list[str], model: str = "text-embedding-3-small") -> np.ndarray`
- `build_vector_index(embeddings: np.ndarray, method: str = "faiss") -> VectorIndex`
- `semantic_search(query_embedding: np.ndarray, index: VectorIndex, k: int = 5) -> list[tuple[int, float]]`
- `hybrid_search(query: str, bm25_index, vector_index, alpha: float = 0.5) -> list[int]`
- `reciprocal_rank_fusion(rankings: list[list[tuple[int, float]]], k: int = 60) -> list[int]`
- All functions with defensive coding (type hints, input validation, docstrings)

The system **must** provide `backend/context_judges.py` with:
- `ContextPrecisionJudge` - Evaluates retrieved document relevance
- `ContextRecallJudge` - Measures coverage of relevant documents
- Uses GPT-4o-mini with few-shot examples
- Returns precision/recall scores with confidence

#### FR-L12.4: Visual Diagrams
The system **must** provide:
- `diagrams/hybrid_search_architecture.mmd` - RRF fusion workflow
- `diagrams/chunking_strategies_comparison.png` - Visual comparison of 5 strategies
- `diagrams/contextual_retrieval_anthropic.mmd` - Anthropic's chunk augmentation method

---

### Lesson 13: RAG Generation & Attribution

#### FR-L13.1: Concept Tutorials (Markdown)
The system **must** provide:

- `attribution_evaluation.md` (reading time: 22-25 min)
  - What is attribution in RAG systems?
  - Grounding vs citation vs substantiation
  - Detecting unattributed claims in LLM responses
  - Extracting claims and matching to source documents
  - Attribution vs hallucination distinction
  - Measuring attribution rate with AI judges

- `hallucination_detection_rag.md` (reading time: 20-25 min)
  - RAG-specific hallucinations vs pure LLM hallucinations
  - Intrinsic hallucinations (contradict context)
  - Extrinsic hallucinations (not in context, but not contradicting)
  - Context-aware hallucination detection
  - Faithfulness measurement techniques
  - Building hallucination detection judges

- `end_to_end_rag_eval.md` (reading time: 18-22 min)
  - Holistic RAG evaluation: retrieval + generation
  - Component-wise vs end-to-end evaluation
  - Failure mode taxonomy: retrieval vs generation failures
  - Context utilization measurement
  - Answer correctness vs answer quality
  - Production monitoring strategies for RAG

#### FR-L13.2: Interactive Notebooks (Jupyter)
The system **must** provide:

- `attribution_detection.ipynb`
  - Extract claims from LLM responses
  - Match claims to retrieved documents
  - Binary classification: ATTRIBUTED vs UNATTRIBUTED
  - Measure attribution rate on 200 Gita Q&A examples
  - Judges provide evidence quotes
  - Execution time: <7 minutes, Cost: $2.00-3.00 (FULL), $0.40-0.60 (DEMO)

- `context_utilization.ipynb`
  - Generate LLM response with context vs without context
  - Measure semantic similarity between response and each retrieved doc
  - Classify docs: USED (>0.7 similarity) vs IGNORED (<0.3)
  - Identify which retrieved documents LLM actually references
  - Execution time: <6 minutes, Cost: $1.50-2.50 (FULL), $0.30-0.50 (DEMO)

#### FR-L13.3: Evaluation Test Suite
The system **must** provide `data/rag_evaluation_suite.json` with 500 test cases:
- **200 from Bhagavad Gita Q&A**: `{query, context (verse text), answer, labels}`
- **200 from recipe corpus**: `{query, context (recipe), answer, labels}`
- **100 adversarial cases**: Designed to test hallucination detection

Each test case includes labels:
- `is_attributed`: PASS/FAIL (answer cites context correctly)
- `is_context_relevant`: PASS/FAIL (context matches query)
- `context_utilization`: USED/IGNORED (LLM uses vs ignores context)
- `hallucination_type`: NONE | INTRINSIC | EXTRINSIC

#### FR-L13.4: Reference Implementation
The system **must** provide `backend/rag_generation_eval.py` with:
- `AttributionDetector` class:
  - `extract_claims(response: str) -> list[str]`
  - `verify_attribution(claims: list[str], context: list[str]) -> dict[str, bool]`
  - `calculate_attribution_rate(results: list[dict]) -> float`

- `HallucinationDetector` class:
  - `detect_intrinsic_hallucination(response: str, context: list[str]) -> bool`
  - `detect_extrinsic_hallucination(response: str, context: list[str]) -> bool`
  - `classify_hallucination_type(response: str, context: list[str]) -> str`

- `ContextUtilizationScorer` class:
  - `measure_utilization(response: str, contexts: list[str]) -> dict[int, float]`
  - `classify_usage(similarity: float) -> str`  # USED | PARTIAL | IGNORED

The system **must** provide `backend/rag_pipeline_eval.py` with:
- `RAGPipelineEvaluator` class for end-to-end evaluation
- Combines retrieval metrics (from HW4) + generation metrics (attribution, hallucination)
- Returns unified report: retrieval quality + generation quality

#### FR-L13.5: Visual Diagrams
The system **must** provide:
- `diagrams/attribution_detection_workflow.mmd` - Claim extraction → verification
- `diagrams/rag_failure_taxonomy.png` - Retrieval vs generation failure modes
- `diagrams/context_utilization_heatmap.mmd` - Which docs LLM uses

---

### Lesson 14: Agent Evaluation & Multi-Agent Systems (EXPANDED from AgentCompanion)

> ⚠️ **CRITICAL DUPLICATION WARNING (2025-11-14):**
>
> **ALREADY COMPLETED** (DO NOT re-implement):
> - ✅ 3 concept tutorials (Group E: Original Lesson 14 Content)
> - ✅ 2 interactive notebooks (Group D: Original Notebooks)
> - ✅ 2 backend modules (Module 5-6: agent_evaluation.py, multi_agent_framework.py)
> - ✅ 3 benchmarks (Original Benchmarks: planning/tool_call/efficiency)
> - ✅ 3 diagrams (Group F: react_agent_workflow, multi_agent_orchestration, failure_modes_taxonomy)
>
> **Completed in:** Task 3.0 (2025-11-12 to 2025-11-13)
> **Evidence:** lesson-14/ directory contains 10,698 lines of existing content
> **Analysis:** tasks/DUPLICATION_ANALYSIS_L14.md
>
> **IMPLEMENT ONLY:** Groups A-D (AgentCompanion expansion) = 11 NEW tutorials, 8 NEW notebooks, 4 NEW backend modules, 10 NEW datasets, 32 NEW diagrams

**Scope Expansion**: This lesson now comprehensively covers advanced agent evaluation methodologies, multi-agent architectures, agentic RAG patterns, and real-world case studies from Google's AgentCompanion whitepaper (February 2025).

#### FR-L14.1: Concept Tutorials (Markdown)
The system **must** provide the following tutorials:

**Group A: Agent Evaluation Methodology** (NEW - from AgentCompanion Lines 96-181)

- `agent_evaluation_fundamentals.md` (reading time: 25-30 min)
  - AgentOps: DevOps → MLOps → AgentOps progression
  - Agent Success Metrics: business KPIs, goal completion, critical tasks
  - Observability: traces, telemetry, human feedback (👍👎)
  - Evaluation components: capabilities, trajectory, final response
  - Public benchmarks: BFCL (tool calling), τ-bench, PlanBench, AgentBench
  - When to use holistic vs. specialized benchmarks

- `trajectory_evaluation_techniques.md` (reading time: 20-25 min)
  - What is trajectory evaluation? (path of actions before user response)
  - Six ground-truth-based metrics:
    1. **Exact match**: Perfect trajectory replication (rigid)
    2. **In-order match**: Core steps in sequence + extra actions allowed
    3. **Any-order match**: All actions present, order irrelevant
    4. **Precision**: % relevant tool calls in predicted trajectory
    5. **Recall**: % essential tool calls captured from reference
    6. **Single-tool use**: Specific action presence verification
  - Reference trajectory requirements and limitations
  - Advanced: Agent-as-a-Judge for trajectory evaluation (2024 research)
  - Radar charts for multi-metric trajectory analysis

- `autorater_final_response_eval.md` (reading time: 18-22 min)
  - LLM-as-a-Judge for agent goal achievement
  - Custom success criteria design (accuracy, tone, style, domain-specific)
  - Autorater prompt engineering for agent outputs
  - Comparing autorater vs. human vs. automated metrics
  - When to use each evaluation method (table from AgentCompanion)
  - Calibrating autoraters with human feedback

- `human_in_the_loop_evaluation.md` (reading time: 18-22 min)
  - When human evaluation is essential (subjectivity, creativity, nuance)
  - Three evaluation methods:
    1. Direct assessment (expert scoring)
    2. Comparative evaluation (vs. other agents/iterations)
    3. User studies (behavior, usability, effectiveness)
  - Evaluating the evaluator: calibrating automated systems
  - Balancing cost, speed, and quality in evaluation
  - Integration with production monitoring

**Group B: Multi-Agent Architectures** (NEW - from AgentCompanion Lines 182-286)

> **SCOPE CLARIFICATION:**
> - `multi_agent_orchestration.md` ✅ **ALREADY EXISTS** - Covers PVE pattern implementation (Planner-Validator-Executor)
> - `multi_agent_fundamentals.md` ❌ **NEW** - Covers 11 core components (Memory, Cognitive, Tools, Flow/Routing, etc.)
> - `multi_agent_design_patterns.md` ❌ **NEW** - Covers 5 coordination patterns (Hierarchical, Diamond, Peer-to-Peer, Collaborative, Adaptive Loop)
>
> These 3 tutorials are **complementary**, not overlapping. Existing tutorial focuses on PVE implementation, new tutorials cover architectural components and coordination patterns.

- `multi_agent_fundamentals.md` (reading time: 25-30 min)
  - Multi-agent definition: team of specialized agents vs. monolithic systems
  - Advantages: accuracy, efficiency, scalability, fault tolerance, reduced hallucinations
  - Agent roles: Planner, Retriever, Execution, Evaluator agents
  - Core components (11 subsystems):
    - Interaction Wrapper (environment interface)
    - Memory Management (short-term cache/sessions, long-term episodes/skills, reflection)
    - Cognitive Functionality (CoT, ReAct, planning, self-correction)
    - Tool Integration (dynamic registries, "Tool RAG")
    - Flow/Routing (delegation, handoff, agent-as-tool)
    - Feedback Loops (performance-driven refinement, not traditional RL)
    - Agent Communication (A2A protocol for consensus)
    - Remote Agent Communication (async tasks, notifications, UX support)
    - Agent & Tool Registry (mesh: ontology, capabilities, performance metrics)
  - Component interaction diagrams

- `multi_agent_design_patterns.md` (reading time: 25-30 min)
  - Four fundamental patterns (table from AgentCompanion):
    1. **Sequential**: Linear task handoff (assembly line)
    2. **Hierarchical**: Manager delegates to workers (leader-follower)
    3. **Collaborative**: Shared resources, common goal (research team)
    4. **Competitive**: Competition for optimal outcome (Overcooked-AI game)
  - Five automotive AI patterns (from case study):
    1. **Hierarchical**: Orchestrator routes queries to specialists
    2. **Diamond**: Response moderation/rephrasing before user delivery
    3. **Peer-to-Peer**: Agent handoff on misclassification recovery
    4. **Collaborative**: Response Mixer combines multiple specialist outputs
    5. **Adaptive Loop**: Iterative query refinement until success
  - Pattern selection criteria and business impact
  - LangGraph topology diagrams (from AgentCompanion Fig 7)

- `multi_agent_challenges_evaluation.md` (reading time: 20-25 min)
  - Six key challenges:
    1. Task Communication (message-based vs. structured async tasks)
    2. Task Allocation (efficient division, feedback loops)
    3. Coordinating Reasoning (debate, consensus mechanisms)
    4. Managing Context (information/conversation tracking)
    5. Time & Cost (computational expense, user latency)
    6. Complexity (microservice-like system-level complexity)
  - Multi-agent evaluation: unique considerations
    - Cooperation & coordination effectiveness
    - Planning & task assignment adherence
    - Agent utilization (tool use, delegation, transfer)
    - Scalability (quality improvement vs. latency reduction)
  - Trajectory evaluation across multiple agents

**Group C: Agentic RAG** (NEW - from AgentCompanion Lines 287-327)

- `agentic_rag_evolution.md` (reading time: 22-25 min)
  - Traditional RAG limitations: static approach fails on ambiguous/multi-step queries
  - Agentic RAG definition: autonomous retrieval agents with iterative reasoning
  - Four core innovations:
    1. **Context-Aware Query Expansion**: Multiple query refinements vs. single pass
    2. **Multi-Step Reasoning**: Decompose complex queries, retrieve sequentially
    3. **Adaptive Source Selection**: Dynamic knowledge source selection (not just vector DB)
    4. **Validation & Correction**: Evaluator agents cross-check for hallucinations
  - Advantages: improved accuracy, explainability, adaptability
  - Use cases: legal research, scientific discovery, business intelligence
  - Vectorize.io agentic RAG diagram (Fig 9 from AgentCompanion)

- `search_optimization_for_rag.md` (reading time: 20-25 min)
  - Why optimize search before introducing agents (recall improvements)
  - Six optimization techniques:
    1. **Parse & Chunk**: Vertex AI Layout Parser (semantic chunking, heading hierarchy)
    2. **Metadata Enrichment**: Synonyms, keywords, authors, dates, tags (boost/bury/filter)
    3. **Fine-Tune Embeddings**: Domain-specific representations, search adaptors
    4. **Faster Vector DB**: Vertex AI Vector Search (speed + quality tradeoff)
    5. **Rankers**: Re-rank top results from approximate search
    6. **Check Grounding**: Ensure phrase citability to retrieved chunks
  - Vertex AI Search architecture diagram (Fig 10)
  - RAG Engine Python interface (LlamaIndex-like)
  - Vertex AI Search Builder APIs integration

**Group D: Enterprise Agent Applications** (NEW - from AgentCompanion Lines 328-388)

- `enterprise_agent_types_patterns.md` (reading time: 20-25 min)
  - Two agent types in enterprise:
    1. **Assistants**: User-interactive, synchronous/async (meeting scheduler, code writer, research agent)
    2. **Automation Agents**: Background event listeners (backend ops, testing, notifications)
  - Knowledge worker evolution: invoking agents → managing agent fleets
  - Manager of agents UX: orchestration, monitoring, task assignment
  - Novel interfaces for virtual team management
  - Google Agentspace overview

- `agentspace_notebooklm_enterprise.md` (reading time: 22-25 min)
  - **Google Agentspace** features:
    - Multi-modal search across enterprise data (unstructured + structured)
    - Built-in trust: SSO, RBAC, VPC Service Controls, IAM
    - Universal connectivity (SaaS platforms, on-demand refresh)
    - Blended RAG, knowledge graphs, semantic understanding
    - Scalability (geographic, linguistic, peak usage)
    - Security: Google Cloud secure-by-design infrastructure
  - **NotebookLM Enterprise** features:
    - Research assistant for complex information synthesis
    - AI-generated audio summaries (TTS with prosody control)
    - Enterprise-grade security/privacy
    - Plus tier: increased storage, sophisticated analysis tools
  - **Agentspace Enterprise Plus**:
    - Custom AI agents for business functions
    - Multi-step workflow automation
    - Centralized agent gallery and discovery
    - ML model integration with proprietary data

**Group E: Original Lesson 14 Content** ⚠️ **ALREADY COMPLETED - SKIP IMPLEMENTATION**

> **IMPLEMENTATION NOTE (2025-11-14):**
> The following 3 tutorials were completed in **Task 3.0** (2025-11-12) and are already integrated into `lesson-14/`.
> **DO NOT re-implement** these tutorials.
>
> **Evidence:**
> - ✅ `lesson-14/agent_planning_evaluation.md` (1,089 lines, 33KB)
> - ✅ `lesson-14/react_reflexion_patterns.md` (1,364 lines, 42KB)
> - ✅ `lesson-14/multi_agent_orchestration.md` (1,308 lines, 40KB)
>
> **Cross-Reference:** lesson-14/TUTORIAL_INDEX.md, lesson-14/README.md
> **Analysis:** tasks/DUPLICATION_ANALYSIS_L14.md

- ~~`agent_planning_evaluation.md`~~ ✅ **EXISTS** (reading time: 22-25 min)
  - Agent definition: environment + actions + planner
  - Planning validation metrics
  - Tool selection accuracy (valid tool chosen?)
  - Parameter validation (correct # and types?)
  - Goal achievement measurement
  - Plan efficiency (excessive steps?)
  - Planning failure modes

- ~~`react_reflexion_patterns.md`~~ ✅ **EXISTS** (reading time: 20-25 min)
  - ReAct: Reasoning + Action interleaving
  - Thought → Action → Observation loop
  - Reflexion: Evaluator + Self-Reflection modules
  - When reflection improves agent performance
  - Measuring reflection quality
  - Cost and latency trade-offs

- ~~`multi_agent_orchestration.md`~~ ✅ **EXISTS** (reading time: 18-22 min)
  - Multi-agent architecture patterns
  - Planner + Validator + Executor decomposition
  - Communication protocols between agents
  - Memory management: short-term vs long-term
  - Memory strategies: FIFO, summarization, reflection
  - Orchestration evaluation metrics

#### FR-L14.2: Interactive Notebooks (Jupyter)
The system **must** provide the following executable notebooks:

**Group A: Agent Evaluation in Practice** (NEW)

- `trajectory_evaluation_tutorial.ipynb`
  - Implement 6 trajectory evaluation metrics (exact, in-order, any-order, precision, recall, single-tool)
  - Create reference trajectories for recipe bot agent tasks
  - Generate agent traces and compare against reference
  - Visualize trajectory comparison with radar charts
  - Calculate trajectory similarity scores
  - Identify trajectory deviations and optimization opportunities
  - Execution time: <8 minutes, Cost: $1.50-2.50 (FULL), $0.30-0.50 (DEMO)

- `autorater_response_evaluation.ipynb`
  - Build LLM-as-a-Judge autoraters for recipe bot responses
  - Define custom success criteria (accuracy, tone, cultural sensitivity)
  - Prompt engineering for agent output evaluation
  - Compare autorater scores vs. human labels (100 examples)
  - Calibrate autorater thresholds based on human feedback
  - Generate evaluation report with confidence scores
  - Execution time: <7 minutes, Cost: $2.00-3.00 (FULL), $0.40-0.60 (DEMO)

- `public_benchmark_evaluation.ipynb`
  - Evaluate recipe bot agent on standardized benchmarks
  - Tool calling accuracy (BFCL-style evaluation)
  - Planning capability (PlanBench-style tasks)
  - Multi-turn conversation handling (AgentBench subset)
  - Generate benchmark report card with pass/fail breakdown
  - Identify capability gaps vs. public leaderboard agents
  - Execution time: <10 minutes, Cost: $2.50-3.50 (FULL), $0.50-0.70 (DEMO)

**Group B: Multi-Agent Systems Implementation** (NEW)

- `multi_agent_pattern_comparison.ipynb`
  - Implement 5 coordination patterns for recipe bot:
    1. Hierarchical (orchestrator routes to specialists)
    2. Diamond (response rephrasing agent)
    3. Peer-to-peer (agent handoff on misclassification)
    4. Collaborative (response mixer combines outputs)
    5. Adaptive loop (iterative query refinement)
  - Measure performance of each pattern (accuracy, latency, cost)
  - Visualize agent interaction flows
  - Pattern selection decision tree
  - Execution time: <12 minutes, Cost: $3.00-4.00 (FULL), $0.60-0.80 (DEMO)

- `automotive_ai_case_study.ipynb`
  - Recreate automotive AI multi-agent system (simplified)
  - 5 specialized agents: Navigation, Media Search, Message Composition, Car Manual, General Knowledge
  - Implement orchestrator with routing logic
  - Test 20 real-world automotive queries
  - Measure routing accuracy and agent utilization
  - Analyze multi-agent trajectory (which agents were involved?)
  - Execution time: <10 minutes, Cost: $2.00-3.00 (FULL), $0.40-0.60 (DEMO)

**Group C: Agentic RAG** (NEW)

- `agentic_rag_implementation.ipynb`
  - Build agentic RAG system for recipe bot
  - Implement context-aware query expansion (generate 3 query variations)
  - Multi-step reasoning: decompose complex queries into sub-questions
  - Adaptive source selection: choose between recipe DB, Gita corpus, web search
  - Validation agent: cross-check responses for hallucinations
  - Compare agentic RAG vs. traditional RAG (accuracy, latency, cost)
  - Execution time: <10 minutes, Cost: $2.50-3.50 (FULL), $0.50-0.70 (DEMO)

- `search_optimization_before_agents.ipynb`
  - Baseline: traditional RAG with basic chunking
  - Apply 6 optimization techniques sequentially:
    1. Semantic chunking (vs. character-based)
    2. Metadata enrichment (add tags, keywords)
    3. Fine-tuned embeddings (domain-specific)
    4. Ranker for re-ranking top-k results
    5. Grounding check (citation verification)
  - Measure Recall@5 improvement after each optimization
  - Final: add agentic layer and measure additional gain
  - Execution time: <8 minutes, Cost: $1.50-2.50 (FULL), $0.30-0.50 (DEMO)

**Group D: Original Lesson 14 Notebooks** ⚠️ **ALREADY COMPLETED - SKIP IMPLEMENTATION**

> **IMPLEMENTATION NOTE (2025-11-14):**
> The following 2 notebooks were completed in **Task 3.0** (2025-11-13) and are already integrated into `lesson-14/`.
> **DO NOT re-implement** these notebooks.
>
> **Evidence:**
> - ✅ `lesson-14/react_agent_implementation.ipynb` (1,054 lines, 32KB)
> - ✅ `lesson-14/agent_failure_analysis.ipynb` (1,060 lines, 32KB)
> - ✅ Test variants also exist: `react_agent_implementation_test.ipynb`, `agent_failure_analysis_test.ipynb`
>
> **Cross-Reference:** lesson-14/TUTORIAL_INDEX.md
> **Analysis:** tasks/DUPLICATION_ANALYSIS_L14.md

- ~~`react_agent_implementation.ipynb`~~ ✅ **EXISTS**
  - Build ReAct agent for recipe bot queries
  - Implement Thought → Action → Observation loop
  - Measure: success rate, avg steps to success, reflection quality
  - Compare with baseline (no reflection)
  - Execution time: <10 minutes, Cost: $2.50-3.50 (FULL), $0.50-0.70 (DEMO)

- ~~`agent_failure_analysis.ipynb`~~ ✅ **EXISTS**
  - Planning failures: invalid tools, wrong parameters, goal failures
  - Tool failures: correct tool but wrong output
  - Efficiency failures: excessive cost/latency/steps
  - Systematic evaluation of failure modes
  - Execution time: <7 minutes, Cost: $1.50-2.50 (FULL), $0.30-0.50 (DEMO)

#### FR-L14.3: Reference Implementation
The system **must** provide the following backend modules:

**Module 1: `backend/trajectory_evaluation.py`** (NEW)

- `TrajectoryEvaluator` class:
  - `exact_match(predicted: list[str], reference: list[str]) -> bool`
    - Perfect trajectory replication check
  - `in_order_match(predicted: list[str], reference: list[str]) -> dict[str, Any]`
    - Returns: `{matched: bool, extra_actions: list[str], match_rate: float}`
  - `any_order_match(predicted: list[str], reference: list[str]) -> dict[str, Any]`
    - Returns: `{matched: bool, missing: list[str], extra: list[str]}`
  - `precision(predicted: list[str], reference: list[str]) -> float`
    - % of predicted actions that are in reference
  - `recall(predicted: list[str], reference: list[str]) -> float`
    - % of reference actions captured in predicted
  - `single_tool_use(trajectory: list[str], tool_name: str) -> bool`
    - Check if specific tool was used
  - `evaluate_all_metrics(predicted: list[str], reference: list[str]) -> dict[str, Any]`
    - Returns comprehensive report with all 6 metrics

- `TrajectoryVisualizer` class:
  - `generate_radar_chart(metrics: dict[str, float]) -> matplotlib.Figure`
    - Creates radar chart for multi-metric visualization
  - `generate_trajectory_diff(predicted: list[str], reference: list[str]) -> str`
    - Returns colored diff output (green=match, red=missing, yellow=extra)

**Module 2: `backend/autorater_framework.py`** (NEW)

- `AutoraterBase` abstract class:
  - `evaluate(response: str, criteria: dict[str, str]) -> dict[str, Any]`
    - Returns: `{score: float, reasoning: str, confidence: float}`
  - `calibrate(human_labels: list[dict], threshold: float = 0.7)`
    - Adjust scoring based on human feedback

- `AgentResponseAutorater` class (extends `AutoraterBase`):
  - `__init__(model: str = "gpt-4o-mini", criteria: dict[str, str])`
  - `evaluate_goal_achievement(response: str, goal: str) -> dict[str, Any]`
  - `evaluate_accuracy(response: str, ground_truth: str) -> dict[str, Any]`
  - `evaluate_tone(response: str, desired_tone: str) -> dict[str, Any]`
  - `batch_evaluate(responses: list[str], criteria: dict) -> list[dict]`

- `BenchmarkEvaluator` class:
  - `evaluate_tool_calling(agent_traces: list[dict]) -> dict[str, float]`
    - BFCL-style evaluation: tool selection accuracy, parameter correctness
  - `evaluate_planning(agent_traces: list[dict]) -> dict[str, float]`
    - PlanBench-style: plan quality, goal achievement, efficiency
  - `generate_benchmark_report(results: dict) -> str`
    - Markdown report with pass/fail breakdown

**Module 3: `backend/multi_agent_patterns.py`** (NEW)

- `PatternBase` abstract class:
  - `route(query: str, context: dict) -> str`
    - Returns agent name to handle query
  - `execute(query: str, context: dict) -> dict[str, Any]`
    - Execute pattern and return result

- `HierarchicalPattern` class (extends `PatternBase`):
  - Orchestrator routes to specialized agents
  - `register_specialist(agent: BaseAgent, domain: str)`
  - `classify_query(query: str) -> str`
    - Returns domain classification

- `DiamondPattern` class (extends `PatternBase`):
  - Response moderation/rephrasing layer
  - `set_rephraser_agent(agent: BaseAgent)`
  - `apply_moderation(raw_response: str, context: dict) -> str`

- `PeerToPeerPattern` class (extends `PatternBase`):
  - Agent handoff on misclassification
  - `allow_handoff(from_agent: str, to_agent: str, condition: Callable)`
  - `detect_misclassification(response: str, confidence: float) -> bool`

- `CollaborativePattern` class (extends `PatternBase`):
  - Response mixer combines multiple outputs
  - `add_contributor(agent: BaseAgent, weight: float)`
  - `mix_responses(responses: list[str], weights: list[float]) -> str`

- `AdaptiveLoopPattern` class (extends `PatternBase`):
  - Iterative query refinement
  - `refine_query(original: str, feedback: str, iteration: int) -> str`
  - `set_max_iterations(max_iter: int)`
  - `check_success_criteria(result: dict) -> bool`

**Module 4: `backend/agentic_rag.py`** (NEW)

- `AgenticRAG` class:
  - `__init__(retriever: Callable, generator: Callable, validator: Callable)`
  - `expand_query(query: str, num_variants: int = 3) -> list[str]`
    - Context-aware query expansion
  - `decompose_query(query: str) -> list[str]`
    - Multi-step reasoning: break into sub-questions
  - `select_source(query: str, available_sources: list[str]) -> str`
    - Adaptive source selection
  - `validate_response(response: str, context: list[str]) -> dict[str, Any]`
    - Cross-check for hallucinations, grounding
  - `retrieve_with_reasoning(query: str) -> dict[str, Any]`
    - Full agentic RAG pipeline

- `SearchOptimizer` class:
  - `semantic_chunk(text: str, max_chunk_size: int = 512) -> list[str]`
  - `enrich_metadata(chunks: list[str]) -> list[dict]`
    - Add synonyms, keywords, tags
  - `rerank_results(query: str, results: list[dict], top_k: int = 5) -> list[dict]`
  - `check_grounding(response: str, sources: list[str]) -> dict[str, Any]`
    - Returns: `{is_grounded: bool, citations: list[str], ungrounded_claims: list[str]}`

**Module 5: `backend/agent_evaluation.py`** ⚠️ **ALREADY COMPLETED - SKIP IMPLEMENTATION**

> **IMPLEMENTATION NOTE (2025-11-14):**
> This module was completed in **Task 3.10-3.11** (2025-11-12) and is already integrated.
> **DO NOT re-implement** this module.
>
> **Evidence:**
> - ✅ `backend/agent_evaluation.py` (exists with all required classes)
> - ✅ `tests/test_agent_evaluation.py` (40+ tests, >90% coverage)
>
> **Cross-Reference:** backend/agent_evaluation.py:1-50
> **Analysis:** tasks/DUPLICATION_ANALYSIS_L14.md

- ~~`PlanningValidator` class~~ ✅ **EXISTS**:
  - `validate_tool_existence(plan: list[dict], tool_inventory: list[str]) -> dict`
  - `validate_parameters(tool_call: dict, tool_schema: dict) -> bool`
  - `validate_parameter_values(tool_call: dict) -> dict`
  - `check_goal_achievement(plan: list[dict], goal: str) -> bool`
  - Returns validation report with specific failures

- ~~`ToolCallAccuracyMeasurer` class~~ ✅ **EXISTS**:
  - `measure_tool_selection_accuracy(traces: list[dict]) -> float`
  - `measure_parameter_accuracy(traces: list[dict]) -> float`
  - `identify_problematic_tools(traces: list[dict]) -> dict[str, float]`

**Module 6: `backend/multi_agent_framework.py`** ⚠️ **ALREADY COMPLETED - SKIP IMPLEMENTATION**

> **IMPLEMENTATION NOTE (2025-11-14):**
> This module was completed in **Task 3.12** (2025-11-12) and is already integrated.
> **DO NOT re-implement** this module.
>
> **Evidence:**
> - ✅ `backend/multi_agent_framework.py` (exists with all required classes)
> - ✅ `tests/test_multi_agent_framework.py` (30+ tests, >90% coverage)
>
> **Cross-Reference:** backend/multi_agent_framework.py:1-50
> **Analysis:** tasks/DUPLICATION_ANALYSIS_L14.md

- `BaseAgent` abstract class:
  - `process(input: dict, context: dict) -> dict`
  - `update_memory(information: dict)`
  - `retrieve_memory(query: str) -> list[dict]`

- Concrete implementations:
  - `PlannerAgent`: Generates high-level plans
  - `ValidatorAgent`: Checks plan quality before execution
  - `ExecutorAgent`: Executes validated plans
  - `MemoryManager`: Handles short-term/long-term memory

- `MultiAgentOrchestrator` class:
  - `register_agent(agent: BaseAgent, role: str)`
  - `execute_workflow(task: str) -> dict`
  - `track_agent_interactions() -> list[dict]`

**All modules must follow:**
- Defensive coding: 5-step function pattern (type check, validation, edge cases, main logic, return)
- Type hints for all functions
- Comprehensive docstrings (Google style)
- Input validation with descriptive exceptions
- Test coverage >90%

#### FR-L14.4: Agent Benchmarks & Case Study Datasets
The system **must** provide the following evaluation datasets:

**Original Benchmarks** ⚠️ **ALREADY COMPLETED - SKIP IMPLEMENTATION**

> **IMPLEMENTATION NOTE (2025-11-14):**
> The following 3 benchmarks were completed in **Task 3.0** (2025-11-12 to 2025-11-13) and exist in `lesson-14/data/`.
> **DO NOT re-implement** these datasets.
>
> **Evidence:**
> - ✅ `lesson-14/data/agent_planning_benchmark.json` (100 cases, 86KB)
> - ✅ `lesson-14/data/agent_tool_call_benchmark.json` (150 cases, 69KB)
> - ✅ `lesson-14/data/agent_efficiency_benchmark.json` (100 cases, 60KB)
>
> **Cross-Reference:** lesson-14/data/
> **Analysis:** tasks/DUPLICATION_ANALYSIS_L14.md

- ~~`data/agent_planning_benchmark.json`~~ ✅ **EXISTS** - 100 tasks with gold plans
- ~~`data/agent_tool_call_benchmark.json`~~ ✅ **EXISTS** - 150 tool call validation cases
- ~~`data/agent_efficiency_benchmark.json`~~ ✅ **EXISTS** - 50 multi-step tasks with cost/latency budgets

**Trajectory Evaluation Datasets** (NEW)
- `data/trajectory_references.json` - 200 reference trajectories for recipe bot tasks
  - Each entry: `{task_id, query, reference_trajectory: list[str], expected_outcome: str}`
  - Categories: recipe lookup (50), cooking advice (50), ingredient substitution (50), cultural context (50)
- `data/trajectory_test_set.json` - 100 agent traces to evaluate
  - Each entry: `{task_id, query, predicted_trajectory: list[str], actual_outcome: str}`
  - For testing trajectory evaluation metrics

**Autorater Calibration Datasets** (NEW)
- `data/autorater_calibration.json` - 100 agent responses with human labels
  - Each entry: `{response_id, query, agent_response, human_score: float, human_reasoning: str, labels: dict}`
  - Labels include: goal_achieved (bool), accuracy (1-5), tone_appropriate (bool), culturally_sensitive (bool)
  - Use for calibrating autorater thresholds

**Public Benchmark Adaptations** (NEW)
- `data/tool_calling_benchmark.json` - 75 BFCL-style tool calling test cases
  - Adapted for recipe bot domain
  - Each entry: `{query, available_tools: list[dict], expected_tool: str, expected_params: dict, gold_output: str}`
- `data/planning_benchmark.json` - 50 PlanBench-style planning tasks
  - Multi-step recipe tasks requiring planning
  - Each entry: `{task_description, goal, constraints: list[str], gold_plan: list[dict], success_criteria: dict}`

**Multi-Agent Pattern Datasets** (NEW)
- `data/multi_agent_test_queries.json` - 100 queries for pattern comparison
  - Categories: simple (25), multi-domain (25), ambiguous (25), complex (25)
  - Each entry: `{query, expected_pattern: str, primary_agent: str, secondary_agents: list[str], expected_trajectory: list[str]}`

**Automotive AI Case Study Dataset** (NEW)
- `data/automotive_queries.json` - 20 real-world automotive AI test queries
  - Derived from AgentCompanion case study (lines 495-655)
  - 5 specialized agent domains:
    1. Conversational Navigation (5 queries): "Find sushi restaurant nearby", "What are good restaurants on route to Munich?"
    2. Conversational Media Search (5 queries): "Play upbeat driving music", "Who sounds like John Coltrane?"
    3. Message Composition (5 queries): "Tell Alex I'm running late", "Let team know I'm stuck in traffic"
    4. Car Manual Agent (3 queries): "How do I turn off lane-keeping assist?", "Where is tire pressure monitor?"
    5. General Knowledge Agent (2 queries): "Tell me about Salzburg", "What is aquaplaning?"
  - Each entry: `{query, expected_agent: str, expected_response_type: str, context: dict, pattern_used: str}`

**Agentic RAG Datasets** (NEW)
- `data/agentic_rag_test_set.json` - 50 complex queries requiring agentic RAG
  - Categories: ambiguous (15), multi-step (15), multi-source (10), contradictory (10)
  - Each entry: `{query, query_variants: list[str], sub_questions: list[str], expected_sources: list[str], gold_response: str, grounding_check: dict}`
- `data/search_optimization_baseline.json` - 30 queries with baseline RAG results
  - Used to measure improvement from each optimization technique
  - Each entry: `{query, baseline_recall@5: float, semantic_chunking_recall: float, metadata_recall: float, ranker_recall: float, final_agentic_recall: float}`

**Enterprise Case Study Datasets** (NEW)
- `data/enterprise_agent_tasks.json` - 40 enterprise automation scenarios
  - Assistant agents (20): meeting scheduling, code writing, research, data analysis
  - Automation agents (20): monitoring, testing, notifications, workflow triggers
  - Each entry: `{task, agent_type: str, expected_workflow: list[str], success_criteria: dict, cost_budget: float, latency_budget: float}`

**Dataset Quality Standards:**
- All datasets must include metadata: creation_date, source, version, total_count
- JSON format with schema validation
- Include train/validation/test splits where applicable (70/15/15)
- Provide dataset statistics and distribution analysis in accompanying README.md

#### FR-L14.5: Visual Diagrams
The system **must** provide the following Mermaid diagrams and visualizations:

**Group A: Agent Evaluation Methodology Diagrams** (NEW)

- `diagrams/agentops_evolution.mmd` - DevOps → MLOps → GenAIOps → AgentOps progression
  - Show dependency relationships and additional capabilities at each level
  - Include: PromptOps, RAGOps, AgentOps subcategories

- `diagrams/agent_evaluation_components.mmd` - Three evaluation components flowchart
  - Capabilities assessment (public benchmarks)
  - Trajectory evaluation (6 metrics)
  - Final response evaluation (autoraters)
  - Show how components feed into comprehensive evaluation

- `diagrams/trajectory_metrics_comparison.png` - Radar chart example
  - Visualize all 6 trajectory metrics for sample agent traces
  - Based on AgentCompanion Figure 6 (radar chart)

- `diagrams/evaluation_method_tradeoffs.mmd` - Decision tree
  - When to use: Human evaluation vs. LLM-as-Judge vs. Automated metrics
  - Include criteria: subjectivity needs, scale, cost, speed
  - Based on AgentCompanion Table 1

- `diagrams/observability_architecture.mmd` - Cloud Observability integration
  - Show traces, spans, metrics collection
  - OpenTelemetry integration for agents
  - Based on AgentCompanion Figure 3

**Group B: Multi-Agent Architecture Diagrams** (NEW)

- `diagrams/multi_agent_components.mmd` - 11 core component subsystems
  - Interaction Wrapper, Memory Management, Cognitive Functionality
  - Tool Integration, Flow/Routing, Feedback Loops
  - Agent Communication, Remote Communication, Registry
  - Based on AgentCompanion lines 240-258

- `diagrams/multi_agent_topologies.mmd` - Four fundamental patterns
  - Sequential (assembly line flow)
  - Hierarchical (manager-worker tree)
  - Collaborative (shared resources mesh)
  - Competitive (tournament bracket)
  - Based on AgentCompanion Figure 7 and Table 2

- `diagrams/hierarchical_pattern.mmd` - Orchestrator routing workflow
  - Query → Orchestrator → Specialist Agent → Response
  - Show classification logic and routing decision
  - Based on AgentCompanion Figure 15

- `diagrams/diamond_pattern.mmd` - Response moderation workflow
  - Agent → Raw Response → Rephraser Agent → User
  - Show tone/style transformation
  - Include before/after example
  - Based on AgentCompanion Figure 16

- `diagrams/peer_to_peer_pattern.mmd` - Agent handoff on misclassification
  - Show detection of routing error and handoff to correct agent
  - Include confidence thresholds
  - Based on AgentCompanion Figure 17

- `diagrams/collaborative_pattern.mmd` - Response Mixer architecture
  - Multiple specialist agents → Response Mixer → Combined response
  - Show weighting and merging logic
  - Based on AgentCompanion Figure 18

- `diagrams/adaptive_loop_pattern.mmd` - Iterative query refinement
  - Query → Agent → Success Check → (Refine or Return)
  - Show iteration counter and max iterations
  - Include success criteria checks

- `diagrams/automotive_ai_architecture.png` - Full automotive AI system
  - 5 specialized agents (Navigation, Media, Message, Car Manual, General Knowledge)
  - Orchestrator with routing logic
  - Show all 5 coordination patterns in use
  - Color-coded agent domains

**Group C: Agentic RAG Diagrams** (NEW)

- `diagrams/agentic_rag_workflow.mmd` - Full agentic RAG pipeline
  - Query → Expand → Decompose → Select Source → Retrieve → Validate → Respond
  - Show 4 core innovations highlighted
  - Based on AgentCompanion Figure 9

- `diagrams/traditional_vs_agentic_rag.png` - Side-by-side comparison
  - Left: Static RAG (single retrieval pass)
  - Right: Agentic RAG (iterative with reasoning)
  - Highlight failure cases for traditional RAG

- `diagrams/search_optimization_pipeline.mmd` - 6 optimization techniques
  - Parse & Chunk → Metadata → Fine-tune Embeddings → Vector DB → Ranker → Grounding
  - Show Recall@5 improvement at each stage
  - Based on AgentCompanion Figure 10

- `diagrams/vertex_ai_search_architecture.mmd` - Vertex AI Search components
  - Show Search Builder APIs, RAG Engine, Vector Search integration
  - Include: Layout Parser, Semantic Chunker, Ranker

**Group D: Enterprise Applications Diagrams** (NEW)

- `diagrams/enterprise_agent_types.mmd` - Assistants vs. Automation agents
  - Show synchronous/async assistants (top row)
  - Show background automation agents (bottom row)
  - Include use case examples for each

- `diagrams/knowledge_worker_evolution.mmd` - Timeline diagram
  - Past: Invoking single agents
  - Present: Managing agent fleets
  - Future: Virtual team management UX
  - Show increasing complexity and capability

- `diagrams/agentspace_architecture.mmd` - Google Agentspace features
  - Multi-modal search, Blended RAG, Knowledge graphs
  - Security layer (SSO, RBAC, VPC, IAM)
  - Universal connectivity to SaaS platforms
  - Based on AgentCompanion Figure 12

- `diagrams/notebooklm_workflow.mmd` - NotebookLM Enterprise workflow
  - Upload sources → Synthesize → Query → Audio summary generation
  - Show TTS with prosody control
  - Based on AgentCompanion Figure 11

- `diagrams/contract_lifecycle.mmd` - Contract-based agents lifecycle
  - Negotiation → Execution → Feedback → Subcontracts
  - Show contract fields and iteration messaging
  - Based on AgentCompanion Figure 13 and Tables 3-4

**Group E: Case Study Diagrams** (NEW)

- `diagrams/co_scientist_workflow.mmd` - Google Co-Scientist architecture
  - Generate → Debate → Evolve loop
  - 4 agent types: Data Processing, Hypothesis Generators, Validation, Collaboration
  - Based on AgentCompanion Figure 14

- `diagrams/automotive_agents_detailed.mmd` - Individual agent architectures
  - Flowcharts for each of 5 specialized agents
  - Show input/output, tools, decision logic

**Group F: Original Lesson 14 Diagrams** ⚠️ **ALREADY COMPLETED - SKIP IMPLEMENTATION**

> **IMPLEMENTATION NOTE (2025-11-14):**
> The following 3 diagrams were completed in **Task 3.0** (2025-11-12) and exist in `lesson-14/diagrams/`.
> **DO NOT re-implement** these diagrams.
>
> **Evidence:**
> - ✅ `lesson-14/diagrams/react_agent_workflow.mmd` (7KB)
> - ✅ `lesson-14/diagrams/multi_agent_orchestration.mmd` (11KB) - Note: .mmd format, not .png
> - ✅ `lesson-14/diagrams/agent_failure_modes_taxonomy.mmd` (17KB)
>
> **Cross-Reference:** lesson-14/diagrams/
> **Analysis:** tasks/DUPLICATION_ANALYSIS_L14.md

- ~~`diagrams/react_agent_workflow.mmd`~~ ✅ **EXISTS** - Thought-Action-Observation loop
- ~~`diagrams/multi_agent_orchestration.mmd`~~ ✅ **EXISTS** - Planner-Validator-Executor architecture (Note: .mmd, not .png)
- ~~`diagrams/agent_failure_modes_taxonomy.mmd`~~ ✅ **EXISTS** - Planning/Tool/Efficiency failures

**Diagram Quality Standards:**
- Use Mermaid (.mmd) for GitHub rendering where possible
- Export to PNG for complex diagrams (>15 nodes or requiring custom styling)
- Include descriptive captions for all diagrams
- Color-coding: Blue (agents), Green (success paths), Red (failures), Yellow (decision points)
- Ensure diagrams are understandable without reading code
- Maximum width: 1200px for PNG exports
- Include source .mmd file even if PNG is provided

---

### Cross-Lesson: Integration & Dashboard

#### FR-DASH.1: Unified RAG & Agent Dashboard
The system **must** extend `lesson-9-11/evaluation_dashboard.py` with:

**New RAG Metrics Section:**
- **Hybrid Retrieval**: BM25 vs Semantic vs Hybrid Recall@k comparison
- **Context Quality**: Precision/Recall scores for retrieved documents
- **Attribution Rate**: % of responses properly attributed to sources
- **Hallucination Rate**: % of responses with intrinsic/extrinsic hallucinations
- **Context Utilization**: Heatmap showing which docs LLM uses

**New Agent Metrics Section:**
- **Planning Accuracy**: % of valid plans (tool/parameter validation)
- **Tool Call Accuracy**: % of correct tool selections and parameters
- **Goal Achievement**: % of tasks successfully completed
- **Reflection Quality**: ReAct/Reflexion effectiveness scores
- **Efficiency Metrics**: Avg cost, latency, steps per task

#### FR-DASH.2: Cross-Lesson Comparison
The dashboard **must** provide:
- **Retrieval Comparison**: HW4 BM25 baseline vs Lesson 12 hybrid search
- **Generation Comparison**: No context vs RAG with attribution tracking
- **Agent Comparison**: No reflection vs ReAct vs Reflexion patterns

---

### Cross-Lesson: Tutorial Infrastructure

#### FR-INFRA.1: TUTORIAL_INDEX.md for Each Lesson
Each lesson **must** have (matching Lessons 9-11 format):
- Learning objectives (5-7 bullet points)
- Prerequisites (what to complete first)
- Recommended learning path (flowchart)
- Tutorial list with reading/execution times and costs
- Key concepts (3-5 explanations)
- Common pitfalls (5-7 warnings)
- FAQ (5-7 questions)
- Next steps and connections to other tutorials

#### FR-INFRA.2: Notebook Quality Standards
All notebooks **must**:
- Execute in <10 minutes (or provide "Quick Run" option)
- Include cost warnings at top with DEMO vs FULL mode options
- Use assertions for automated validation (e.g., `assert attribution_rate > 0.7`)
- Provide clear markdown explanations between code cells
- Export results to JSON for dashboard integration
- Handle API errors gracefully with retry logic
- Follow TDD patterns from CLAUDE.md

#### FR-INFRA.3: Diagram Standards
All diagrams **must**:
- Use Mermaid (.mmd) for GitHub rendering
- Export to PNG for complex diagrams (>10 nodes)
- Include descriptive captions
- Be understandable without reading code

---

## Non-Goals (Out of Scope)

1. **BM25 Implementation**: Already covered in HW4
2. **Basic Recall@k Metrics**: Already covered in HW4
3. **Query Rewriting Basics**: Already covered in HW4 (optional)
4. **State Transition Matrices**: Already covered in HW5
5. **Perplexity Calculation**: Already covered in Lesson 9
6. **Basic LLM-as-Judge**: Already covered in HW3 and Lesson 10
7. **Comparative Evaluation/Elo**: Already covered in Lesson 11
8. **Vector Database Comparisons**: Will use FAISS, but not compare vendors
9. **Embedding Model Fine-Tuning**: Will use existing OpenAI/Cohere APIs
10. **Production Deployment**: Focus on evaluation methodology, not Kubernetes/Docker
11. **Multi-Modal RAG**: Focus on text evaluation only
12. **Real-Time Streaming**: Dashboard refreshes periodically, not live WebSocket

---

## Design Considerations

### UI/UX Requirements
- Dashboard extends existing `lesson-9-11/evaluation_dashboard.py`
- New tabs: "Hybrid Retrieval", "RAG Generation", "Agent Systems"
- Responsive design for 1920x1080 and 1366x768 resolutions
- Dark mode support (MonsterUI default theme)
- Keyboard shortcuts: `r` for refresh, `e` for export, `f` for filter

### Tutorial Navigation
- Cross-linking between tutorials via Markdown links
- Breadcrumb navigation in TUTORIAL_INDEX.md
- "Prerequisites" section at top of each tutorial
- "Next Steps" section at bottom with logical progression
- Reference back to HW4/HW5/Lessons 9-11 where relevant

### Code Style
- Follow project's TDD and defensive coding standards (CLAUDE.md)
- Ruff formatting, line length 120 characters
- Type hints for all functions
- Docstrings following Google style
- Test coverage >90% for reference implementations
- 5-step defensive function pattern from CLAUDE.md

---

## Technical Considerations

### Dependencies
**New libraries to add to pyproject.toml**:
- `openai` (already present) - For embeddings API
- `faiss-cpu` - For vector similarity search
- `scikit-learn` (already present) - For cosine similarity
- `sentence-transformers` - Optional, for local embedding generation
- `numpy` (already present) - For vector operations
- All other dependencies already present in project

### Performance Considerations
- **Embedding Generation**: Batch 100 texts per API call
- **Vector Search**: Use FAISS with HNSW index for speed
- **Parallel Processing**: ThreadPoolExecutor (32 workers) for judges
- **Caching**: Save embeddings to avoid regeneration
- **Dashboard**: Paginate results (20 per page)

### Integration Points
- **Extend** `backend/retrieval.py` (from HW4) with semantic + hybrid methods
- **Extend** `backend/query_rewrite_agent.py` (from HW4) for agent patterns
- **Integrate** with `backend/evaluation_utils.py` from Lessons 9-11
- **Reuse** judge patterns from `backend/ai_judge_framework.py` (Lesson 10)
- **Dashboard** ingests JSON from `lesson-12/results/`, `lesson-13/results/`, `lesson-14/results/`

### Data Requirements

**Bhagavad Gita Q&A Dataset:**
- Location: `/Users/rajnishkhatri/Documents/recipe-chatbot/Gita/Bhagavad-Gita-QA/`
- File: `English/english.csv` (3,501 rows)
- Columns: `chapter_no, verse_no, question, answer`
- Use 200 Q&A pairs for RAG evaluation test suite

**Recipe Corpus:**
- Already processed in HW4: `homeworks/hw4/data/processed_recipes.json`
- Use 200 recipes for RAG evaluation test suite

**Agent Traces:**
- Generate from recipe chatbot interactions
- Synthetic benchmarks for planning/tool failures

---

## Success Metrics

### Learning Outcomes (Measured via Post-Tutorial Surveys)
- 90% of students understand when to use hybrid search vs BM25 alone
- 85% of students can implement attribution detection for RAG systems
- 80% of students can validate agent planning and tool calls
- 75% of students successfully implement ReAct pattern with evaluation

### Code Quality (Automated Checks)
- 100% of reference implementations pass Ruff formatting
- >90% test coverage for all modules in `backend/`
- All notebooks execute without errors in <10 minutes
- All tests pass with TDD pattern (RED → GREEN → REFACTOR)

### Tutorial Engagement (Analytics)
- Average completion time: 6-9 hours for full deep-dive (3 lessons)
- 70% of students complete at least 2 of 3 lessons
- 50% of students complete all 3 lessons

### Performance Improvements (Measured on Test Sets)
- **Hybrid Search**: 10-15% Recall@5 improvement over BM25 baseline
- **Attribution Detection**: 80%+ accuracy on RAG test suite (500 cases)
- **Planning Validation**: 85%+ accuracy on agent benchmarks (100 tasks)

### Cost Efficiency (Budget Tracking)
- Total notebook execution cost: $10-15 for FULL mode across all 3 lessons
- DEMO mode enables exploration for <$3 total (<$1 per lesson)
- Dashboard operates at $0 (no API calls)

---

## Open Questions

1. **Embedding Provider**: OpenAI `text-embedding-3-small` (fastest, cheapest) or Cohere `embed-english-v3.0` (better quality)?
   - **Decision needed by**: Before implementing Lesson 12
   - **Recommendation**: OpenAI for cost, provide optional Cohere comparison

2. **Vector Database**: FAISS (local, fast) or managed solution (Pinecone, Weaviate)?
   - **Decision needed by**: Before implementing Lesson 12
   - **Recommendation**: FAISS for simplicity, mention managed options in tutorial

3. **Attribution Judge Approach**: Rule-based (exact matching) or LLM-based (semantic matching)?
   - **Decision needed by**: Before implementing Lesson 13
   - **Recommendation**: Hybrid approach - rules for exact citations, LLM for semantic grounding

4. **Agent Framework**: Build from scratch or integrate LangGraph/CrewAI?
   - **Decision needed by**: Before implementing Lesson 14
   - **Recommendation**: Build minimal framework for educational clarity, show integration paths

5. **Test Data Generation**: Manual labeling or GPT-4o automated with review?
   - **Decision needed by**: Before creating RAG evaluation suite
   - **Recommendation**: GPT-4o for 400 examples, manually review 100 edge cases

6. **Dashboard Framework**: Extend existing FastHTML or migrate to Streamlit?
   - **Decision needed by**: Before dashboard implementation
   - **Recommendation**: Extend FastHTML for consistency with Lessons 9-11

---

## Timeline & Milestones

### Phase 1: Lesson 12 - Hybrid Retrieval (Week 1)
**Day 1-2**: Directory structure, TUTORIAL_INDEX.md, concept tutorials
- `embedding_based_retrieval.md`
- `hybrid_search_strategies.md`
- `context_quality_evaluation.md`

**Day 3-4**: Interactive notebooks
- `hybrid_search_comparison.ipynb`
- `chunking_optimization.ipynb`

**Day 5-6**: Backend implementation
- `backend/semantic_retrieval.py`
- `backend/context_judges.py`

**Day 7**: Testing, diagrams, validation
- Create Mermaid diagrams
- Write tests for semantic_retrieval.py
- Validate notebooks execute correctly

**Milestone**: Lesson 12 complete with 10-15% Recall@5 improvement demonstrated

---

### Phase 2: Lesson 13 - RAG Generation (Week 2)
**Day 8-9**: Concept tutorials
- `attribution_evaluation.md`
- `hallucination_detection_rag.md`
- `end_to_end_rag_eval.md`

**Day 10-11**: Test suite generation
- Extract 200 Gita Q&A samples
- Extract 200 recipe samples
- Generate 100 adversarial cases
- Label all 500 cases (attribution, hallucination, utilization)

**Day 12-13**: Interactive notebooks
- `attribution_detection.ipynb`
- `context_utilization.ipynb`

**Day 14**: Backend implementation
- `backend/rag_generation_eval.py`
- `backend/rag_pipeline_eval.py`
- Write tests, create diagrams

**Milestone**: Lesson 13 complete with 80%+ attribution detection accuracy

---

### Phase 3: Lesson 14 - Agents (Week 3)
**Day 15-16**: Concept tutorials
- `agent_planning_evaluation.md`
- `react_reflexion_patterns.md`
- `multi_agent_orchestration.md`

**Day 17-18**: Agent benchmarks
- `agent_planning_benchmark.json` (100 tasks)
- `agent_tool_call_benchmark.json` (150 cases)
- `agent_efficiency_benchmark.json` (50 tasks)

**Day 19-20**: Interactive notebooks
- `react_agent_implementation.ipynb`
- `agent_failure_analysis.ipynb`

**Day 21**: Backend implementation
- `backend/agent_evaluation.py`
- `backend/multi_agent_framework.py`
- Write tests, create diagrams

**Milestone**: Lesson 14 complete with 85%+ planning validation accuracy

---

### Phase 4: Integration & Dashboard (Week 4)
**Day 22-24**: Dashboard extension
- Extend `evaluation_dashboard.py` with RAG metrics
- Add agent metrics visualization
- Integrate Lessons 12-14 results

**Day 25-26**: Cross-lesson testing
- Test navigation between tutorials
- Update CLAUDE.md with new patterns
- Create TUTORIAL_CHANGELOG.md entries

**Day 27**: Documentation review
- Final validation, cost auditing
- Update README.md
- Write integration guide

**Day 28**: Quality assurance
- All tests passing (>90% coverage)
- All notebooks execute successfully
- Dashboard displays all metrics correctly
- Documentation complete

**Milestone**: Complete tutorial system delivered, fully integrated

---

## Appendix A: File Structure

```
recipe-chatbot/
├── lesson-12/
│   ├── TUTORIAL_INDEX.md
│   ├── README.md
│   ├── embedding_based_retrieval.md
│   ├── hybrid_search_strategies.md
│   ├── context_quality_evaluation.md
│   ├── hybrid_search_comparison.ipynb
│   ├── chunking_optimization.ipynb
│   ├── diagrams/
│   │   ├── hybrid_search_architecture.mmd
│   │   ├── chunking_strategies_comparison.png
│   │   └── contextual_retrieval_anthropic.mmd
│   └── results/
│       ├── hybrid_search_results.json
│       └── chunking_comparison.json
├── lesson-13/
│   ├── TUTORIAL_INDEX.md
│   ├── README.md
│   ├── attribution_evaluation.md
│   ├── hallucination_detection_rag.md
│   ├── end_to_end_rag_eval.md
│   ├── attribution_detection.ipynb
│   ├── context_utilization.ipynb
│   ├── diagrams/
│   │   ├── attribution_detection_workflow.mmd
│   │   ├── rag_failure_taxonomy.png
│   │   └── context_utilization_heatmap.mmd
│   ├── data/
│   │   └── rag_evaluation_suite.json  # 500 test cases
│   └── results/
│       ├── attribution_results.json
│       └── hallucination_analysis.json
├── lesson-14/  # EXPANDED with AgentCompanion Integration
│   ├── TUTORIAL_INDEX.md
│   ├── README.md
│   │
│   ├── # Group A: Agent Evaluation Methodology (4 tutorials)
│   ├── agent_evaluation_fundamentals.md         # NEW
│   ├── trajectory_evaluation_techniques.md      # NEW
│   ├── autorater_final_response_eval.md         # NEW
│   ├── human_in_the_loop_evaluation.md          # NEW
│   │
│   ├── # Group B: Multi-Agent Architectures (3 tutorials)
│   ├── multi_agent_fundamentals.md              # NEW
│   ├── multi_agent_design_patterns.md           # NEW
│   ├── multi_agent_challenges_evaluation.md     # NEW
│   │
│   ├── # Group C: Agentic RAG (2 tutorials)
│   ├── agentic_rag_evolution.md                 # NEW
│   ├── search_optimization_for_rag.md           # NEW
│   │
│   ├── # Group D: Enterprise Applications (2 tutorials)
│   ├── enterprise_agent_types_patterns.md       # NEW
│   ├── agentspace_notebooklm_enterprise.md      # NEW
│   │
│   ├── # Group E: Original Content (3 tutorials - RETAINED)
│   ├── agent_planning_evaluation.md
│   ├── react_reflexion_patterns.md
│   ├── multi_agent_orchestration.md
│   │
│   ├── # Interactive Notebooks (10 total)
│   ├── trajectory_evaluation_tutorial.ipynb      # NEW
│   ├── autorater_response_evaluation.ipynb       # NEW
│   ├── public_benchmark_evaluation.ipynb         # NEW
│   ├── multi_agent_pattern_comparison.ipynb      # NEW
│   ├── automotive_ai_case_study.ipynb            # NEW
│   ├── agentic_rag_implementation.ipynb          # NEW
│   ├── search_optimization_before_agents.ipynb   # NEW
│   ├── react_agent_implementation.ipynb          # RETAINED
│   ├── agent_failure_analysis.ipynb              # RETAINED
│   ├── agent_failure_analysis_test.ipynb         # EXISTING (already created)
│   │
│   ├── diagrams/  # 35+ diagrams
│   │   ├── # Group A: Agent Evaluation Diagrams (5)
│   │   ├── agentops_evolution.mmd               # NEW
│   │   ├── agent_evaluation_components.mmd      # NEW
│   │   ├── trajectory_metrics_comparison.png    # NEW
│   │   ├── evaluation_method_tradeoffs.mmd      # NEW
│   │   ├── observability_architecture.mmd       # NEW
│   │   │
│   │   ├── # Group B: Multi-Agent Architecture Diagrams (9)
│   │   ├── multi_agent_components.mmd           # NEW
│   │   ├── multi_agent_topologies.mmd           # NEW
│   │   ├── hierarchical_pattern.mmd             # NEW
│   │   ├── diamond_pattern.mmd                  # NEW
│   │   ├── peer_to_peer_pattern.mmd             # NEW
│   │   ├── collaborative_pattern.mmd            # NEW
│   │   ├── adaptive_loop_pattern.mmd            # NEW
│   │   ├── automotive_ai_architecture.png       # NEW
│   │   ├── automotive_agents_detailed.mmd       # NEW
│   │   │
│   │   ├── # Group C: Agentic RAG Diagrams (4)
│   │   ├── agentic_rag_workflow.mmd             # NEW
│   │   ├── traditional_vs_agentic_rag.png       # NEW
│   │   ├── search_optimization_pipeline.mmd     # NEW
│   │   ├── vertex_ai_search_architecture.mmd    # NEW
│   │   │
│   │   ├── # Group D: Enterprise Diagrams (5)
│   │   ├── enterprise_agent_types.mmd           # NEW
│   │   ├── knowledge_worker_evolution.mmd       # NEW
│   │   ├── agentspace_architecture.mmd          # NEW
│   │   ├── notebooklm_workflow.mmd              # NEW
│   │   ├── contract_lifecycle.mmd               # NEW
│   │   │
│   │   ├── # Group E: Case Study Diagrams (2)
│   │   ├── co_scientist_workflow.mmd            # NEW
│   │   ├── automotive_agents_detailed.mmd       # NEW
│   │   │
│   │   ├── # Group F: Original Diagrams (3 - RETAINED)
│   │   ├── react_agent_workflow.mmd
│   │   ├── multi_agent_orchestration.png
│   │   └── agent_failure_modes_taxonomy.mmd
│   │
│   ├── data/  # 9 comprehensive datasets
│   │   ├── # Original Benchmarks (3)
│   │   ├── agent_planning_benchmark.json
│   │   ├── agent_tool_call_benchmark.json
│   │   ├── agent_efficiency_benchmark.json
│   │   │
│   │   ├── # Trajectory Evaluation (2)
│   │   ├── trajectory_references.json           # NEW (200 references)
│   │   ├── trajectory_test_set.json             # NEW (100 traces)
│   │   │
│   │   ├── # Autorater & Benchmarks (3)
│   │   ├── autorater_calibration.json           # NEW (100 human-labeled)
│   │   ├── tool_calling_benchmark.json          # NEW (75 BFCL-style)
│   │   ├── planning_benchmark.json              # NEW (50 PlanBench-style)
│   │   │
│   │   ├── # Multi-Agent & Case Studies (4)
│   │   ├── multi_agent_test_queries.json        # NEW (100 queries)
│   │   ├── automotive_queries.json              # NEW (20 real-world)
│   │   ├── agentic_rag_test_set.json            # NEW (50 complex)
│   │   ├── search_optimization_baseline.json    # NEW (30 queries)
│   │   │
│   │   ├── # Enterprise (1)
│   │   └── enterprise_agent_tasks.json          # NEW (40 scenarios)
│   │
│   └── results/
│       ├── planning_validation.json
│       ├── agent_performance.json
│       ├── trajectory_evaluation_results.json   # NEW
│       ├── autorater_scores.json                # NEW
│       ├── benchmark_report.json                # NEW
│       ├── multi_agent_pattern_results.json     # NEW
│       ├── automotive_ai_results.json           # NEW
│       └── agentic_rag_results.json             # NEW
├── backend/
│   ├── # Lesson 12 Modules (2)
│   ├── semantic_retrieval.py        # NEW (Lesson 12)
│   ├── context_judges.py            # NEW (Lesson 12)
│   │
│   ├── # Lesson 13 Modules (2)
│   ├── rag_generation_eval.py       # NEW (Lesson 13)
│   ├── rag_pipeline_eval.py         # NEW (Lesson 13)
│   │
│   ├── # Lesson 14 Modules (6 - EXPANDED with AgentCompanion)
│   ├── trajectory_evaluation.py     # NEW (AgentCompanion)
│   ├── autorater_framework.py       # NEW (AgentCompanion)
│   ├── multi_agent_patterns.py      # NEW (AgentCompanion)
│   ├── agentic_rag.py               # NEW (AgentCompanion)
│   ├── agent_evaluation.py          # NEW (Original Lesson 14)
│   ├── multi_agent_framework.py     # NEW (Original Lesson 14)
│   │
│   ├── # Extended Modules
│   ├── retrieval.py                 # EXTENDED from HW4
│   └── query_rewrite_agent.py       # EXTENDED from HW4
│
├── tests/
│   ├── # Lesson 12 Tests (2)
│   ├── test_semantic_retrieval.py   # NEW
│   ├── test_context_judges.py       # NEW
│   │
│   ├── # Lesson 13 Tests (2)
│   ├── test_rag_generation_eval.py  # NEW
│   ├── test_rag_pipeline_eval.py    # NEW
│   │
│   ├── # Lesson 14 Tests (6 - EXPANDED)
│   ├── test_trajectory_evaluation.py    # NEW (AgentCompanion)
│   ├── test_autorater_framework.py      # NEW (AgentCompanion)
│   ├── test_multi_agent_patterns.py     # NEW (AgentCompanion)
│   ├── test_agentic_rag.py              # NEW (AgentCompanion)
│   ├── test_agent_evaluation.py         # NEW (Original)
│   └── test_multi_agent_framework.py    # NEW (Original)
├── Gita/
│   ├── Bhagavad-Gita-QA/
│   │   └── English/
│   │       └── english.csv          # 3,501 Q&A pairs
│   └── Bhagwat-Gita-Infinity/
│       └── slok/                    # 737 verse JSON files
└── lesson-9-11/
    └── evaluation_dashboard.py      # EXTENDED with L12-14 metrics
```

---

## Appendix B: Coverage Map - What's NEW vs Existing

### Lesson 12: Hybrid Retrieval (NEW)

| Topic | Already Covered? | New Content |
|-------|------------------|-------------|
| **BM25 Basics** | ✅ HW4 | - |
| **Recall@k, MRR** | ✅ HW4 | - |
| **Semantic Search** | ❌ | ✅ Embeddings, vector databases, k-NN/ANN |
| **Hybrid Search** | ❌ | ✅ RRF fusion, two-stage reranking |
| **Context Precision/Recall** | ❌ | ✅ AI judges for document relevance |
| **Chunking Strategies** | ❌ | ✅ Character/sentence/paragraph/recursive/semantic |
| **Contextual Retrieval** | ❌ | ✅ Anthropic's chunk augmentation |

### Lesson 13: RAG Generation (100% NEW)

| Topic | Already Covered? | New Content |
|-------|------------------|-------------|
| **Attribution Detection** | ❌ | ✅ LLM cites sources correctly? |
| **Hallucination in RAG** | ❌ | ✅ Context-grounded vs fabricated |
| **Context Utilization** | ❌ | ✅ LLM uses vs ignores docs |
| **Answer Faithfulness** | ❌ | ✅ Response accuracy to context |
| **End-to-End RAG Eval** | ❌ | ✅ Retrieval + generation holistic |

### Lesson 14: Agent Systems (Extends HW5)

| Topic | Already Covered? | New Content |
|-------|------------------|-------------|
| **State Transitions** | ✅ HW5 | - |
| **Planning Validation** | ❌ | ✅ Tool/parameter/goal validation |
| **Tool Call Accuracy** | ❌ | ✅ Invalid tools, wrong parameters |
| **ReAct Pattern** | ❌ | ✅ Thought-Action-Observation loop |
| **Reflexion Pattern** | ❌ | ✅ Evaluator + self-reflection |
| **Multi-Agent** | ❌ | ✅ Planner-Validator-Executor |
| **Memory Management** | ❌ | ✅ Short/long-term, FIFO, summarization |
| **Efficiency Profiling** | ❌ | ✅ Cost/latency/steps tracking |

---

## Appendix C: Example Tutorial Navigation Flow

### Beginner Path (Skip Advanced Retrieval, 5-6 hours)
```
1. Complete Lesson 13 TUTORIAL_INDEX.md (5 min)
2. Read attribution_evaluation.md (20 min)
3. Run attribution_detection.ipynb DEMO mode (7 min, $0.40)
4. Complete Lesson 14 TUTORIAL_INDEX.md (5 min)
5. Read react_reflexion_patterns.md (20 min)
6. Run react_agent_implementation.ipynb DEMO mode (10 min, $0.50)
7. View results in dashboard (30 min)
```

### Advanced Path (Complete Deep-Dive, 8-10 hours)
```
1. Complete Lesson 12 in full (2-3 hours)
   - Read all 3 concept tutorials
   - Execute both notebooks FULL mode
   - Achieve 10-15% Recall@5 improvement
2. Complete Lesson 13 in full (2-3 hours)
   - Read all 3 concept tutorials
   - Execute both notebooks FULL mode
   - Achieve 80%+ attribution detection accuracy
3. Complete Lesson 14 in full (2-3 hours)
   - Read all 3 concept tutorials
   - Execute both notebooks FULL mode
   - Achieve 85%+ planning validation accuracy
4. Integrate all via dashboard (1-2 hours)
   - Run extended evaluation_dashboard.py
   - Export comprehensive report
   - Analyze cross-lesson insights
```

---

## Appendix D: Budget Breakdown

### Lesson 12: Hybrid Retrieval
**DEMO Mode:**
- Hybrid search comparison (20 queries): $0.30-0.50
- Chunking optimization (10 recipes): $0.20-0.30
- **Total DEMO**: $0.50-0.80

**FULL Mode:**
- Hybrid search comparison (100 queries): $1.50-2.50
- Chunking optimization (50 recipes): $1.00-1.50
- **Total FULL**: $2.50-4.00

### Lesson 13: RAG Generation
**DEMO Mode:**
- Attribution detection (20 examples): $0.40-0.60
- Context utilization (20 examples): $0.30-0.50
- **Total DEMO**: $0.70-1.10

**FULL Mode:**
- Attribution detection (200 examples): $2.00-3.00
- Context utilization (200 examples): $1.50-2.50
- **Total FULL**: $3.50-5.50

### Lesson 14: Agent Evaluation & Multi-Agent Systems (EXPANDED)

**DEMO Mode (10 notebooks):**

*Group A: Agent Evaluation (3 notebooks)*
- Trajectory evaluation (20 agent traces): $0.30-0.50
- Autorater response evaluation (20 responses): $0.40-0.60
- Public benchmark evaluation (10 tasks): $0.50-0.70

*Group B: Multi-Agent Systems (2 notebooks)*
- Multi-agent pattern comparison (5 queries × 5 patterns): $0.60-0.80
- Automotive AI case study (10 queries): $0.40-0.60

*Group C: Agentic RAG (2 notebooks)*
- Agentic RAG implementation (10 queries): $0.50-0.70
- Search optimization before agents (5 queries): $0.30-0.50

*Group D: Original Notebooks (2 notebooks)*
- ReAct implementation (10 tasks): $0.50-0.70
- Failure analysis (10 cases): $0.30-0.50

**Total DEMO**: $3.80-5.60

**FULL Mode (10 notebooks):**

*Group A: Agent Evaluation (3 notebooks)*
- Trajectory evaluation (100 agent traces): $1.50-2.50
- Autorater response evaluation (100 responses): $2.00-3.00
- Public benchmark evaluation (75 tasks): $2.50-3.50

*Group B: Multi-Agent Systems (2 notebooks)*
- Multi-agent pattern comparison (20 queries × 5 patterns): $3.00-4.00
- Automotive AI case study (20 queries): $2.00-3.00

*Group C: Agentic RAG (2 notebooks)*
- Agentic RAG implementation (50 queries): $2.50-3.50
- Search optimization before agents (30 queries): $1.50-2.50

*Group D: Original Notebooks (2 notebooks)*
- ReAct implementation (50 tasks): $2.50-3.50
- Failure analysis (50 cases): $1.50-2.50

**Total FULL**: $19.00-28.00

### Overall Budget (UPDATED)
- **DEMO Mode Total**: $5.00-7.50 (all 3 lessons) - *Lesson 14 expansion adds ~$3.00-4.50*
- **FULL Mode Total**: $25.00-37.50 (all 3 lessons) - *Lesson 14 expansion adds ~$15.00-22.00*
- **Dashboard**: $0 (no API calls, reads from JSON)

**Budget Justification for Lesson 14 Expansion:**
- 8 new notebooks added (was 2, now 10 total)
- AgentCompanion integration brings production-grade evaluation techniques
- Real-world case studies (Automotive AI, Google Co-Scientist) require additional test queries
- Multi-agent pattern comparison requires testing 5 patterns across multiple query types
- Public benchmark evaluation (BFCL, PlanBench) requires processing 75-150 test cases
- Comprehensive trajectory evaluation across 100+ agent traces
- Cost efficiency maintained: ~$2-3 per notebook in FULL mode, <$1 in DEMO mode

---

**PRD Status**: ✅ Ready for Task Generation (UPDATED 2025-11-14 with AgentCompanion Integration + Duplication Warnings)
**Next Step**: Use `@generate-tasks.md` to break this PRD into actionable task list

**Estimated Implementation**: ⚠️ **REVISED: 4-5 weeks (28-35 days)** with 1 developer
  - *Original estimate: 6-7 weeks (42-49 days)*
  - *Duplication savings: ~1.5-2.5 weeks (18 existing files, 10,698 lines already complete)*
  - **NEW content only (excluding duplicates):**
    - 11 NEW concept tutorials (3 already exist, 11 to create)
    - 8 NEW notebooks (2 already exist, 8 to create)
    - 4 NEW backend modules (2 already exist, 4 to create)
    - 10 NEW datasets (3 already exist, 10 to create)
    - 32 NEW diagrams (3 already exist, 32 to create)
  - **Effort breakdown:**
    - Lessons 12-13: ~2 weeks (unchanged)
    - Lesson 14 NEW content only: ~2-3 weeks (down from 4-5 weeks)

**Total Tutorial Execution Cost**: $25-38 (FULL mode), $5-8 (DEMO mode)
  - *Lesson 14 DUPLICATE notebooks (~$4-6): Already executed, $0 additional cost*
  - *Lesson 14 NEW notebooks (~$16-22): Budgeted in estimate*

**Key Innovation**: First tutorial system integrating Google AgentCompanion (Feb 2025) with hands-on recipe bot implementation

**Duplication Analysis**: See tasks/DUPLICATION_ANALYSIS_L14.md for complete evidence and recommendations

---

## Lesson 14 Scope Summary (AgentCompanion Expansion)

### Content Overview (TOTAL vs NEW)

**Total Content in PRD:**
- **14 concept tutorials** (11 NEW + 3 ✅ EXIST)
- **10 interactive notebooks** (8 NEW + 2 ✅ EXIST)
- **6 backend modules** (4 NEW + 2 ✅ EXIST)
- **13 comprehensive datasets** (10 NEW + 3 ✅ EXIST)
- **35 visual diagrams** (32 NEW + 3 ✅ EXIST)
- **Real case studies**: Automotive AI (5 agents, 5 patterns), Google Co-Scientist
- **Production frameworks**: AgentOps, observability, enterprise security, contract-based agents

**NEW Content to Implement (AgentCompanion Expansion):**
- ✅ 11 concept tutorials (Groups A-D: Evaluation, Multi-Agent, Agentic RAG, Enterprise)
- ✅ 8 interactive notebooks (Groups A-C: Trajectory, Autorater, Benchmarks, Patterns, Case Studies, Agentic RAG)
- ✅ 4 backend modules (trajectory_evaluation, autorater_framework, multi_agent_patterns, agentic_rag)
- ✅ 10 datasets (trajectory refs/test, autorater calibration, benchmarks, case studies)
- ✅ 32 diagrams (AgentOps, multi-agent topologies, agentic RAG, enterprise, case studies)

**EXISTING Content (DO NOT re-implement):**
- ⚠️ 3 concept tutorials (Group E: agent_planning_evaluation, react_reflexion_patterns, multi_agent_orchestration)
- ⚠️ 2 notebooks (Group D: react_agent_implementation, agent_failure_analysis)
- ⚠️ 2 backend modules (agent_evaluation, multi_agent_framework)
- ⚠️ 3 datasets (agent_planning/tool_call/efficiency_benchmark.json)
- ⚠️ 3 diagrams (react_agent_workflow, multi_agent_orchestration, failure_modes_taxonomy)

### What's NEW from AgentCompanion Integration

**Agent Evaluation Methodology (Lines 96-181):**
- ✅ 6 trajectory evaluation metrics (exact, in-order, any-order, precision, recall, single-tool)
- ✅ Autoraters for final response evaluation (LLM-as-Judge)
- ✅ Public benchmarks (BFCL tool calling, PlanBench planning, AgentBench holistic)
- ✅ Human-in-the-loop evaluation (3 methods: direct, comparative, user studies)
- ✅ AgentOps: DevOps → MLOps → AgentOps progression
- ✅ Observability: traces, telemetry, business KPIs, human feedback loops

**Multi-Agent Architectures (Lines 182-286):**
- ✅ 11 core components (Memory, Cognitive, Tools, Flow/Routing, Communication, Registry, etc.)
- ✅ 4 fundamental patterns (Sequential, Hierarchical, Collaborative, Competitive)
- ✅ 5 automotive AI patterns (Hierarchical, Diamond, Peer-to-Peer, Collaborative, Adaptive Loop)
- ✅ Multi-agent evaluation (cooperation, task assignment, agent utilization, scalability)
- ✅ 6 challenges (task communication, allocation, reasoning, context, time/cost, complexity)

**Agentic RAG (Lines 287-327):**
- ✅ Context-aware query expansion (multi-variant queries)
- ✅ Multi-step reasoning (query decomposition into sub-questions)
- ✅ Adaptive source selection (dynamic knowledge source choice)
- ✅ Validation & correction (cross-check for hallucinations)
- ✅ Search optimization (6 techniques: parse/chunk, metadata, fine-tune, ranker, grounding)

**Real-World Case Studies:**
- ✅ Automotive AI (5 specialized agents: Navigation, Media, Message, Car Manual, General Knowledge)
- ✅ Google Co-Scientist (Generate → Debate → Evolve research system)
- ✅ 20 real-world automotive queries with expected agents and patterns

**Enterprise Applications (Lines 328-388):**
- ✅ Agent types: Assistants (user-interactive) vs. Automation (background)
- ✅ Google Agentspace (multi-modal search, blended RAG, enterprise security)
- ✅ NotebookLM Enterprise (research synthesis, audio summaries, TTS with prosody)
- ✅ Contract-based agents (negotiation, execution, feedback, subcontracts)
- ✅ Knowledge worker evolution (invoking agents → managing fleets)

### Integration with Existing Content

**Supplements (NOT Duplicates):**
- HW4: BM25 basics → **NEW**: Agentic RAG, search optimization
- HW5: State transitions → **NEW**: Multi-agent orchestration patterns
- Lesson 9: Perplexity, exact metrics → **NEW**: Trajectory evaluation (6 metrics)
- Lesson 10: LLM-as-Judge basics → **NEW**: Autoraters for agents, calibration
- Lesson 11: Comparative eval → **NEW**: Multi-agent pattern comparison

**Extends Existing Tutorials:**
- Original Lesson 14 (3 tutorials, 2 notebooks) → **EXPANDED** to 13 tutorials, 10 notebooks
- Retained all original content: ReAct/Reflexion, planning validation, failure analysis
- Added production-grade evaluation frameworks from Google research

### Learning Outcomes

**After completing expanded Lesson 14, students can:**
1. ✅ Implement 6 trajectory evaluation metrics for agent debugging
2. ✅ Build and calibrate autoraters for final response evaluation
3. ✅ Evaluate agents against public benchmarks (BFCL, PlanBench)
4. ✅ Design multi-agent systems with 5 coordination patterns
5. ✅ Build automotive AI case study with 5 specialized agents
6. ✅ Implement agentic RAG with query expansion and validation
7. ✅ Optimize search before agents (6 techniques for Recall improvement)
8. ✅ Deploy agents with AgentOps (observability, traces, KPIs)
9. ✅ Understand enterprise deployment (Agentspace, NotebookLM, security)
10. ✅ Build contract-based agents for high-stakes tasks

### Unique Value Proposition

**Why This Tutorial System is Unique:**
1. **Theory-to-Practice**: Bridges Google AgentCompanion research with hands-on recipe bot implementation
2. **Real Case Studies**: Automotive AI and Co-Scientist from actual production systems
3. **Comprehensive Evaluation**: 6 trajectory metrics + autoraters + public benchmarks
4. **Production Patterns**: AgentOps, observability, enterprise security from Google Cloud
5. **Cost Efficient**: 10 notebooks execute for <$28 in FULL mode, <$6 in DEMO mode
6. **Zero Duplication**: Supplements existing Lessons 9-11 and HW1-5 with NEW content only
7. **Cross-Domain**: Recipe bot + Bhagavad Gita + automotive AI for robust learning
