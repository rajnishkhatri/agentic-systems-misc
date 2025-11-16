# Context Engineering Guide: Cost & Latency Optimization for Agent Systems

**Reading Time:** 25-30 minutes
**Difficulty:** Intermediate
**Prerequisites:** Understanding of RAG, basic agent architecture, familiarity with [Memory Systems Fundamentals](memory_systems_fundamentals.md)

---

## Table of Contents

1. [Context Engineering vs Prompt Engineering](#context-engineering-vs-prompt-engineering)
2. [Context Selection Techniques](#context-selection-techniques)
3. [Context Compression Strategies](#context-compression-strategies)
4. [Context Ordering Strategies](#context-ordering-strategies)
5. [Context as Specification](#context-as-specification)
6. [Executable Example: MMR Selection](#executable-example-mmr-selection)
7. [Practical Exercises](#practical-exercises)
8. [Further Reading](#further-reading)

---

## Context Engineering vs Prompt Engineering

### What is Context Engineering?

**Context engineering** is the systematic optimization of *all* inputs to an LLM to maximize output quality while minimizing cost and latency. Unlike prompt engineering, which focuses solely on the user-facing query and system prompt, context engineering addresses the **entire context window**:

- System prompt (procedural memory)
- Conversation history (working memory)
- Past experiences (episodic memory)
- Retrieved information (semantic memory)
- Tool outputs and intermediate results

> **Source:** `agents_memory.txt` lines 194-243

**Formal Definition:**
Context engineering is finding the best context such that it maximizes the quality of the LLM's output for a given task, while managing cost and latency constraints *(agents_memory.txt:216-220)*.

### Why Context Engineering Matters: Cost & Latency Drivers

#### 1. **Cost Impact**

Modern LLM pricing is token-based. As context windows grow to 1M+ tokens (Google Gemini 1.5, Anthropic Claude 3.5), costs scale linearly:

**Example Cost Breakdown (GPT-4 Turbo):**
- Input: $0.01 per 1K tokens
- Output: $0.03 per 1K tokens

**Scenario:** Agent processes 100 queries/day with 50K context per query:
- Daily input tokens: 100 × 50K = 5M tokens
- Daily cost: 5M × ($0.01 / 1K) = **$50/day** = **$1,500/month**

**Without context optimization:** This cost is prohibitive for production.
**With context engineering:** Reduce to $300-500/month (60-80% savings).

> **Source:** Cost estimates aligned with COMPASS_ARTIFACT_ANALYSIS.md production deployment insights

#### 2. **Latency Impact**

Processing time increases with context length:

| Context Size | Processing Time (Claude 3.5) | User Experience |
|--------------|------------------------------|-----------------|
| 5K tokens    | ~0.5 seconds                 | ✅ Excellent     |
| 50K tokens   | ~2.5 seconds                 | ⚠️ Acceptable    |
| 200K tokens  | ~10 seconds                  | ❌ Poor          |
| 1M tokens    | ~50+ seconds                 | ❌ Unacceptable  |

> **Insight:** Every 10K tokens adds ~0.5s latency. For real-time applications (<2s response), context must stay under 30K tokens *(agents_memory.txt:234-239)*.

#### 3. **Performance Degradation**

Research shows that arbitrarily filling context windows **hurts performance**:

- **RULER Benchmark** *(agents_memory.txt:232)*: Models that performed well on "Needle in a Haystack" showed **significant performance drops** on multi-hop reasoning as context length increased.
- **"Context Rot"** phenomenon: Adding irrelevant information to context degrades output quality, even within the model's nominal context window *(agents_memory.txt:232)*.

**Key Principle:**
> "It is not about filling up the context window, but strategically choosing and placing information." *(agents_memory.txt:236-238)*

### Context Engineering vs Prompt Engineering

| Dimension | Prompt Engineering | Context Engineering |
|-----------|-------------------|---------------------|
| **Scope** | System prompt + user query | Entire context window |
| **Optimization Focus** | Query phrasing, instructions | Information selection, ordering, compression |
| **Primary Metrics** | Output quality, instruction following | Cost, latency, quality balance |
| **Tools** | Prompt templates, few-shot examples | RAG, summarization, re-ranking, caching |
| **User Visibility** | High (user writes prompts) | Low (automated/architectural) |
| **When to Use** | Refining behavior, task specification | Managing memory, scaling to production |

**Visual Analogy:**
- **Prompt Engineering:** Optimizing the *question* you ask
- **Context Engineering:** Optimizing the *entire library* you give the model to answer from

> **Source:** `agents_memory.txt` lines 216-220, 236-243

---

## Context Selection Techniques

Context selection determines **which information** enters the context window. The goal: maximize relevance while minimizing noise.

### 1. Re-Ranking

**Problem:** Semantic similarity (cosine distance) alone doesn't guarantee relevance to the specific query.

**Solution:** Re-ranker models take both the query AND retrieved documents to re-score based on query-document relevance.

**Popular Re-Rankers:**
- **Cross-Encoder Models:** BERT-based models (e.g., `ms-marco-MiniLM-L-12-v2`)
- **Cohere Rerank API:** Commercial re-ranking service
- **BGE Reranker:** Open-source alternative (BAAI)

**How It Works:**
1. Semantic search retrieves top-50 documents (broad recall)
2. Re-ranker scores all 50 based on query-document pairs
3. Select top-10 re-ranked documents (high precision)

**Trade-off:**
- ✅ **Improves relevance:** 15-30% accuracy gain on RAG tasks
- ❌ **Adds latency:** ~100-200ms for re-ranking 50 documents
- ❌ **Adds cost:** $0.002 per 1K document-query pairs (Cohere Rerank)

**When to Use:** High-stakes queries where relevance > latency (legal research, medical diagnosis).

### 2. Maximal Marginal Relevance (MMR)

**Problem:** Top-k semantic search returns redundant documents (e.g., 5 documents all saying "flamingos are pink due to carotenoids").

**Solution:** MMR balances **relevance** (similarity to query) and **diversity** (dissimilarity to already-selected documents).

**MMR Formula:**

```
MMR = argmax[d ∈ D \ S] [λ · Sim(d, Q) - (1 - λ) · max[s ∈ S] Sim(d, s)]
```

Where:
- `d`: Candidate document
- `D`: All retrieved documents
- `S`: Already-selected documents
- `Q`: Query
- `λ`: Diversity parameter (0 to 1)

**Lambda (λ) Tuning Guidance:**

| λ Value | Behavior | Use Case |
|---------|----------|----------|
| **λ = 0.0** | Pure diversity (ignores relevance) | ❌ Not recommended |
| **λ = 0.3** | High diversity, lower relevance | Exploratory research, brainstorming |
| **λ = 0.5** | Balanced relevance and diversity | **Default for most use cases** |
| **λ = 0.7** | High relevance, moderate diversity | Fact-checking, focused Q&A |
| **λ = 1.0** | Pure relevance (standard top-k) | When diversity doesn't matter |

**Recommendation:** Start with λ=0.5, tune based on evaluation metrics (see [interactive notebook](memory_systems_implementation.ipynb) for MMR implementation).

> **Cross-Reference:** See [Executable MMR Example](#executable-example-mmr-selection) below and notebook implementation.

### 3. Business Rules & Domain-Specific Filtering

**Problem:** Not all relevant documents are equally important for your domain.

**Solution:** Apply hard constraints and weighting rules based on domain knowledge.

**Examples:**

**Bhagavad Gita Chatbot:**
```python
# Prioritize original Sanskrit verses over commentary
if document.metadata.get("type") == "original_verse":
    relevance_score *= 1.5

# Filter out unverified translations
if document.metadata.get("verified") == False:
    continue  # Skip this document
```

**Medical AI Assistant:**
```python
# Only include peer-reviewed sources
if document.metadata.get("peer_reviewed") != True:
    continue

# Boost recent publications (recency bias)
years_old = 2025 - document.metadata.get("publication_year")
recency_weight = max(0.5, 1.0 - (years_old * 0.1))
relevance_score *= recency_weight
```

**When to Use:** Domains with clear quality hierarchies (medical, legal, religious texts).

### 4. Agent Specialization

**Problem:** A single agent with access to ALL knowledge sources becomes overwhelmed.

**Solution:** Create specialized agents, each with access to **only relevant subsets** of context.

**Multi-Agent Example:**

```python
# Recipe Chatbot with Specialized Agents

# Agent 1: Ingredient Substitution (only accesses ingredient DB)
ingredient_agent = Agent(
    knowledge_sources=["ingredient_compatibility.db", "substitution_rules.json"]
)

# Agent 2: Cooking Techniques (only accesses technique guides)
technique_agent = Agent(
    knowledge_sources=["cooking_techniques.md", "equipment_guides.md"]
)

# Agent 3: Dietary Restrictions (only accesses nutrition DB)
dietary_agent = Agent(
    knowledge_sources=["nutrition_facts.db", "allergen_database.json"]
)

# Orchestrator selects which agent(s) to invoke
orchestrator.route(user_query, agents=[ingredient_agent, technique_agent, dietary_agent])
```

**Benefits:**
- ✅ **Reduced context per agent:** 10K tokens each vs 30K for monolithic agent
- ✅ **Parallel execution:** 3 agents run concurrently (3× speed if I/O-bound)
- ✅ **Easier debugging:** Trace failures to specific agent

**When to Use:** Systems with >3 distinct knowledge domains *(agents_memory.txt:379)*.

---

## Context Compression Strategies

Context compression reduces **token count** of selected information without losing critical details.

### 1. Summarization

**Approach:** Use an LLM to condense conversation history or retrieved documents.

**Strategies:**
- **Extractive Summarization:** Select key sentences/phrases (fast, cheaper)
- **Abstractive Summarization:** Rewrite in concise form (slower, higher quality)

**Example (Conversation History):**

```python
# Original conversation history (1,200 tokens)
history = [
    {"role": "user", "content": "What are the health benefits of turmeric?"},
    {"role": "assistant", "content": "Turmeric contains curcumin, which has anti-inflammatory properties..."},
    # ... 10 more turns ...
]

# Summarized (300 tokens)
summary = llm.summarize(history)
# "User inquired about turmeric health benefits. Discussion covered curcumin's anti-inflammatory effects, dosage recommendations (500mg-2g daily), and interactions with blood thinners."
```

**Trade-off:**
- ✅ **75% token reduction** (1,200 → 300 tokens)
- ❌ **Summarization cost:** ~300 tokens output @ $0.03/1K = $0.009 per summarization
- ❌ **Information loss:** Nuances, specific phrasing lost

**When to Use:** Conversation history >2K tokens, latency-sensitive applications.

### 2. Deduplication

**Problem:** Retrieved documents often contain duplicate or near-duplicate content.

**Strategies:**

**Exact Deduplication:**
```python
seen_hashes = set()
unique_documents = []
for doc in retrieved_documents:
    doc_hash = hashlib.sha256(doc.content.encode()).hexdigest()
    if doc_hash not in seen_hashes:
        unique_documents.append(doc)
        seen_hashes.add(doc_hash)
```

**Semantic Deduplication (using embeddings):**
```python
# Remove documents with cosine similarity > 0.95 to each other
unique_documents = [retrieved_documents[0]]  # Start with first doc
for doc in retrieved_documents[1:]:
    similarities = [cosine_similarity(doc.embedding, u.embedding) for u in unique_documents]
    if max(similarities) < 0.95:  # Not a duplicate
        unique_documents.append(doc)
```

**Typical Impact:** 20-40% token reduction in RAG pipelines (e.g., 10 documents → 6-8 unique documents).

### 3. LLMLingua: Prompt Compression

**Overview:** LLMLingua uses a small language model to identify and remove non-essential tokens from prompts while preserving meaning.

**How It Works:**
1. Compute importance score for each token using a small LM (e.g., GPT-2)
2. Remove low-importance tokens (articles, filler words, redundant phrases)
3. Retain high-importance tokens (nouns, verbs, domain-specific terms)

**Example:**

```python
# Original prompt (87 tokens)
original = """
Please provide a detailed explanation of the Bhagavad Gita's teachings on dharma,
specifically focusing on Arjuna's dilemma in Chapter 2 and Krishna's response about
duty and righteousness. Include references to specific verses if possible.
"""

# LLMLingua compressed (42 tokens, 52% reduction)
compressed = """
Explain Bhagavad Gita teachings dharma. Focus Arjuna dilemma Chapter 2 Krishna
response duty righteousness. Include verse references.
"""
```

**Trade-off:**
- ✅ **50-70% token reduction** with minimal quality loss
- ❌ **Compression latency:** ~100-200ms per prompt
- ❌ **Quality risk:** Over-compression can lose critical context

**When to Use:** Repetitive prompts (chatbots, customer support), cost-critical applications.

> **Tool:** [LLMLingua GitHub](https://github.com/microsoft/LLMLingua)

### ROI Math: Context Compression Example

**Scenario:** Bhagavad Gita chatbot processes 100 queries/day with RAG.

**Baseline (No Optimization):**
- Query: 200 tokens
- Retrieved context: 8 documents × 1,500 tokens = 12,000 tokens
- Total input: 12,200 tokens
- Cost per query: 12.2K × ($0.01 / 1K) = **$0.122**
- **Monthly cost:** 100 queries/day × 30 days × $0.122 = **$366/month**

**Stage 1: Re-ranking + MMR (Reduce to 5 diverse documents):**
- Retrieved context: 5 documents × 1,500 tokens = 7,500 tokens
- Total input: 7,700 tokens
- Cost per query: 7.7K × ($0.01 / 1K) = **$0.077**
- **Monthly cost:** **$231/month** (37% savings)

**Stage 2: Add Deduplication (5 documents → 4 unique):**
- Retrieved context: 4 documents × 1,500 tokens = 6,000 tokens
- Total input: 6,200 tokens
- Cost per query: 6.2K × ($0.01 / 1K) = **$0.062**
- **Monthly cost:** **$186/month** (49% savings)

**Stage 3: Add LLMLingua Compression (50% reduction on documents):**
- Retrieved context: 4 documents × 750 tokens (compressed) = 3,000 tokens
- Total input: 3,200 tokens
- Cost per query: 3.2K × ($0.01 / 1K) = **$0.032**
- **Monthly cost:** **$96/month** (74% savings)

**Summary:**
- **Baseline:** $366/month
- **Optimized:** $96/month
- **Total Savings:** $270/month (74% reduction)
- **Annual Savings:** $3,240

> **Source:** ROI math grounded in COMPASS_ARTIFACT_ANALYSIS.md production deployment patterns

**Key Insight:** Compression ROI compounds. Each technique (selection, deduplication, compression) builds on the previous, leading to 70-80% total savings.

---

## Context Ordering Strategies

Where you place information in the context window significantly impacts LLM performance.

### The "Lost in the Middle" Phenomenon

**Research Finding:** LLMs pay more attention to the **beginning** (primacy effect) and **end** (recency effect) of prompts, while information in the middle is often "lost."

> **Source:** Liu et al., "Lost in the Middle: How Language Models Use Long Contexts" (2023), cited in `agents_memory.txt:452`

**Experimental Results:**

| Document Position | Retrieval Accuracy | Reasoning Performance |
|-------------------|--------------------|-----------------------|
| **Position 1 (start)** | 92% | 85% |
| **Position 5 (middle)** | 68% | 62% |
| **Position 10 (end)** | 89% | 81% |

**Interpretation:** The middle 40% of context contributes only ~60% performance, while start/end 20% each contribute ~90%.

### Primacy vs Recency Effects

**Primacy Effect:** Information presented first is recalled best (humans remember first items in a list).

**Recency Effect:** Information presented last is recalled well (humans remember recent items).

> **Source:** Serial-position effect research, cited in `agents_memory.txt:455`

**Implications for Context Ordering:**

**Good Ordering Strategy:**
1. **Start:** System prompt, task instructions, critical constraints
2. **Middle:** Supporting information, background context, less critical details
3. **End:** Most relevant retrieved documents, immediate conversation history, user query

**Bad Ordering Strategy:**
1. **Start:** User query (gets "lost" as context grows)
2. **Middle:** Critical instructions (often missed)
3. **End:** Background information (wastes high-attention position)

### Optimal Ordering Strategies

#### 1. **Importance-Based Ordering**

Rank context components by importance, place high-importance at boundaries:

```python
# Context construction with importance ranking
context = [
    system_prompt,           # Position 1 (primacy)
    task_instructions,       # Position 2
    # ... middle positions ...
    top_3_retrieved_docs,    # Positions N-3, N-2, N-1 (recency)
    recent_conversation,     # Position N-1
    user_query              # Position N (recency)
]
```

#### 2. **Interleaved Ordering**

Alternate between high-importance and low-importance information to avoid "dead zones":

```python
# Instead of: [system, doc1, doc2, doc3, doc4, doc5, query]
# Use interleaved: [system, doc1, doc3, doc5, doc2, doc4, query]
# High-importance: system, doc1, doc3, doc5, query (boundaries + distributed)
# Lower-importance: doc2, doc4 (middle)
```

#### 3. **Chunking with Summaries**

Summarize large context blocks and place summaries at boundaries:

```python
context = [
    system_prompt,
    "Summary of conversation history (last 10 turns): [...]",  # Boundary
    # ... detailed history in middle ...
    "Summary of retrieved documents: [...]",  # Boundary
    # ... full documents in middle ...
    user_query  # End boundary
]
```

### Practical Recommendations

| Use Case | Recommended Ordering | Rationale |
|----------|---------------------|-----------|
| **Q&A Chatbot** | System → Recent history → Retrieved docs → Query | Query at end (recency), docs before query (immediate relevance) |
| **Code Assistant** | System → Relevant code → Error messages → User request | Error messages at end (actionable), code before (context) |
| **Research Agent** | System → Search results → User refinements → Final query | Search results in middle (large), refinements at end (recent) |
| **Multi-Agent** | System → Agent roles → Shared memory → Current task | Current task at end (focus), roles at start (grounding) |

> **Visual Reference:** See [context_engineering_workflow diagram](diagrams/context_engineering_workflow.png) for ordering pipeline visualization.

---

## Context as Specification

Context engineering represents a fundamental shift in how we think about LLM inputs: **context is not just data, it's the specification of agent behavior**.

### 1. Domain Tailoring Through Context

**Principle:** Instead of training domain-specific models, provide domain-specific context.

**Example: Bhagavad Gita Chatbot**

**Traditional Approach (Expensive):**
- Fine-tune GPT-4 on 10,000 Gita Q&A pairs
- Cost: $500-2,000 (training) + $0.06/1K tokens (inference)

**Context Engineering Approach (Cost-Effective):**
```python
system_prompt = """
You are a Bhagavad Gita scholar with expertise in Sanskrit translations and philosophical commentary.

DOMAIN CONSTRAINTS:
- Only reference verses from the Bhagavad Gita (18 chapters, 700 verses)
- Prioritize original Sanskrit with transliteration
- Cite verse numbers (e.g., BG 2.47) for all claims
- When multiple interpretations exist, present 2-3 major schools of thought

KNOWLEDGE SOURCES:
- Retrieved verses and commentaries (provided below)
- Your parametric knowledge of Hindu philosophy

RESPONSE FORMAT:
1. Direct answer with verse citation
2. Sanskrit verse with transliteration
3. Explanation with philosophical context
4. Practical application (if relevant)
"""

# Domain-specific context
retrieved_context = retrieve_relevant_verses(user_query, top_k=5)
conversation_history = get_recent_history(turns=3)

# Full context specification
context = [
    {"role": "system", "content": system_prompt},
    *conversation_history,
    {"role": "system", "content": f"Relevant verses:\n{retrieved_context}"},
    {"role": "user", "content": user_query}
]
```

**Result:** Domain expert behavior without fine-tuning, at 1/10th the cost.

> **Source:** Context as specification principle from `agents_memory.txt:457-466`

### 2. Multi-Agent Coordination via Shared Context

**Problem:** Multiple agents need to coordinate without direct communication.

**Solution:** Use shared context as coordination mechanism.

**Example: Recipe Chatbot with 3 Agents**

```python
# Shared context (coordination layer)
shared_context = {
    "user_goal": "Make gluten-free chocolate cake",
    "dietary_restrictions": ["gluten-free", "dairy-free"],
    "available_ingredients": ["almond flour", "coconut oil", "cocoa powder"],
    "current_plan": "Step 1: Check ingredient compatibility → Step 2: Generate recipe → Step 3: Validate nutrition",
    "agent_states": {
        "ingredient_agent": "completed",
        "recipe_agent": "in_progress",
        "nutrition_agent": "pending"
    }
}

# Each agent receives shared context
recipe_agent_context = [
    {"role": "system", "content": "You are the Recipe Generation Agent."},
    {"role": "system", "content": f"Shared context: {json.dumps(shared_context)}"},
    {"role": "user", "content": "Generate recipe using compatible ingredients from shared context."}
]
```

**Benefits:**
- ✅ **No inter-agent messaging:** Reduced latency, simpler architecture
- ✅ **Stateful coordination:** Agents know what others have done
- ✅ **Auditable:** Shared context is the "source of truth"

> **Source:** Multi-agent coordination patterns from `agents_memory.txt:375-380`

### 3. Context as Debugging Tool

**Insight:** The context is the **specification** of why an agent made a decision. Logging context enables root-cause analysis.

**Example: Debugging Incorrect Output**

```python
# Bad practice: Only log output
logger.info(f"Agent response: {response}")

# Good practice: Log full context
logger.info({
    "timestamp": "2025-11-15T14:32:01Z",
    "user_query": user_query,
    "retrieved_documents": [doc.id for doc in retrieved_docs],
    "conversation_history_turns": len(conversation_history),
    "system_prompt_version": "v2.3",
    "agent_response": response,
    "total_input_tokens": count_tokens(context),
    "execution_time_ms": 1250
})
```

**Debugging Workflow:**
1. User reports incorrect answer
2. Retrieve logged context for that query
3. Identify issue:
   - Wrong documents retrieved? → Fix retrieval logic
   - System prompt ambiguous? → Refine prompt
   - Conversation history too long? → Adjust summarization threshold
4. Reproduce with exact same context → Verify fix

**Key Insight:** "How strange it is that we tend to throw away the input to our function (the LLM) and only keep track of the output!" *(agents_memory.txt:463)*

### 4. Transparency & Communication

**Principle:** Context engineering is developer-oriented, enabling communication of agent intent.

**Use Cases:**

**Code Review:**
```markdown
# PR Description
**User Intent (from logged context):**
- Query: "Refactor UserService to use dependency injection"
- Relevant codebase files: [UserService.java, DatabaseConfig.java]
- Conversation history: 3 turns discussing DI patterns

**Agent Context:**
- Retrieved 5 DI pattern examples from codebase
- Applied "constructor injection" pattern (most common in codebase)
- Preserved existing error handling logic
```

**Multi-Stakeholder Alignment:**
```python
# Context shared with non-technical stakeholders
stakeholder_context = {
    "business_goal": "Reduce customer support ticket volume by 30%",
    "agent_approach": "Multi-agent system: triage → knowledge retrieval → response generation",
    "knowledge_sources": ["FAQ database", "past ticket resolutions", "product documentation"],
    "guardrails": ["Escalate to human if confidence <80%", "Never promise refunds >$50"],
    "expected_metrics": {"ticket_deflection_rate": "≥40%", "customer_satisfaction": "≥4.5/5"}
}
```

**Benefit:** Context becomes shared language between developers, agents, and stakeholders.

> **Source:** Context as communication tool from `agents_memory.txt:458-466`

### 5. Citations and Grounding

**Pattern:** Include citation requirements in context to enforce grounding.

```python
system_prompt = """
CITATION REQUIREMENTS (MANDATORY):
- Every factual claim MUST include source reference
- Format: [Source: {document_id}, {line_number}]
- If information not in provided context, state "Information not available in knowledge base"

EXAMPLE:
Incorrect: "Turmeric reduces inflammation."
Correct: "Turmeric's active compound curcumin has anti-inflammatory properties [Source: health_db_2023.md, lines 45-47]."
"""
```

**Result:** Agents produce auditable, grounded outputs by design, reducing hallucination risk.

---

## Executable Example: MMR Selection

This example demonstrates Maximal Marginal Relevance (MMR) selection with explicit calculations.

### Scenario

**Query:** "Why are flamingos pink?"

**Retrieved Documents (5 total):**
1. "Flamingos are pink due to carotenoid pigments in their diet, primarily from algae and crustaceans."
2. "The pink coloration of flamingos comes from beta-carotene in brine shrimp and blue-green algae."
3. "Carotenoid pigments, particularly canthaxanthin, are metabolized and deposited in feathers, giving flamingos their pink hue."
4. "Flamingos are wading birds found in Africa, Asia, and the Americas, known for their distinctive pink plumage."
5. "The intensity of flamingo pink color varies by species and diet quality, with Caribbean flamingos being brightest."

### Step 1: Calculate Relevance Vector

Cosine similarity between query embedding and each document embedding (simulated):

| Document | Relevance Score (to Query) |
|----------|----------------------------|
| Doc 1    | 0.92                       |
| Doc 2    | 0.89                       |
| Doc 3    | 0.88                       |
| Doc 4    | 0.65                       |
| Doc 5    | 0.78                       |

**Relevance Vector:** `[0.92, 0.89, 0.88, 0.65, 0.78]`

### Step 2: Calculate Redundancy Matrix

Pairwise cosine similarity between documents (simulated):

|       | Doc 1 | Doc 2 | Doc 3 | Doc 4 | Doc 5 |
|-------|-------|-------|-------|-------|-------|
| Doc 1 | 1.00  | 0.94  | 0.91  | 0.45  | 0.72  |
| Doc 2 | 0.94  | 1.00  | 0.93  | 0.42  | 0.70  |
| Doc 3 | 0.91  | 0.93  | 1.00  | 0.40  | 0.68  |
| Doc 4 | 0.45  | 0.42  | 0.40  | 1.00  | 0.55  |
| Doc 5 | 0.72  | 0.70  | 0.68  | 0.55  | 1.00  |

**Observation:** Docs 1, 2, 3 are highly similar (0.91-0.94) - they all discuss carotenoids. Doc 4 is least similar (general info).

### Step 3: MMR Iteration with λ = 0.5

**Iteration 1 (Select first document):**
- **MMR Score = λ · Sim(d, Q)** (no selected documents yet)
- Doc 1: 0.5 × 0.92 = **0.46** ← **Winner**
- Doc 2: 0.5 × 0.89 = 0.445
- Doc 3: 0.5 × 0.88 = 0.44
- Doc 4: 0.5 × 0.65 = 0.325
- Doc 5: 0.5 × 0.78 = 0.39

**Selected:** {Doc 1}

**Iteration 2 (Select second document):**
- **MMR Score = λ · Sim(d, Q) - (1 - λ) · max[Sim(d, Doc 1)]**
- Doc 2: 0.5 × 0.89 - 0.5 × 0.94 = 0.445 - 0.47 = **-0.025**
- Doc 3: 0.5 × 0.88 - 0.5 × 0.91 = 0.44 - 0.455 = **-0.015**
- Doc 4: 0.5 × 0.65 - 0.5 × 0.45 = 0.325 - 0.225 = **0.10** ← **Winner**
- Doc 5: 0.5 × 0.78 - 0.5 × 0.72 = 0.39 - 0.36 = **0.03**

**Selected:** {Doc 1, Doc 4}

**Iteration 3 (Select third document):**
- **MMR Score = λ · Sim(d, Q) - (1 - λ) · max[Sim(d, Doc 1), Sim(d, Doc 4)]**
- Doc 2: 0.5 × 0.89 - 0.5 × max(0.94, 0.42) = 0.445 - 0.47 = **-0.025**
- Doc 3: 0.5 × 0.88 - 0.5 × max(0.91, 0.40) = 0.44 - 0.455 = **-0.015**
- Doc 5: 0.5 × 0.78 - 0.5 × max(0.72, 0.55) = 0.39 - 0.36 = **0.03** ← **Winner**

**Final Selection (Top 3):** {Doc 1, Doc 4, Doc 5}

**Result:**
- **Doc 1:** Direct answer (carotenoids in diet)
- **Doc 4:** Background context (flamingos are wading birds)
- **Doc 5:** Additional detail (color intensity varies)

**Without MMR (top-3 by relevance only):** {Doc 1, Doc 2, Doc 3} - all redundantly discuss carotenoids, missing diversity.

**With MMR:** {Doc 1, Doc 4, Doc 5} - carotenoid mechanism + background + variability.

### Lambda Tuning Comparison

**λ = 0.3 (High Diversity):**
- Final Selection: {Doc 1, Doc 4, Doc 5} (same as λ=0.5)
- Reasoning: Doc 4 heavily favored due to low similarity to others

**λ = 0.7 (High Relevance):**
- Iteration 2: Doc 5 selected instead of Doc 4 (0.5 × 0.78 - 0.3 × 0.72 = 0.39 - 0.216 = **0.174**)
- Final Selection: {Doc 1, Doc 5, Doc 3}
- Reasoning: Docs 3 and 5 still relevant, Doc 4 too low relevance

**λ = 1.0 (Pure Relevance, No Diversity):**
- Final Selection: {Doc 1, Doc 2, Doc 3}
- Reasoning: Standard top-k selection, redundant documents

**Recommendation:** For this query, λ=0.5 provides best balance (carotenoid answer + context + variability).

> **Interactive Notebook:** See [memory_systems_implementation.ipynb](memory_systems_implementation.ipynb) for executable MMR code with visualization.

---

## Practical Exercises

### Exercise 1: Context Selection Decision Tree

**Scenario:** You're building a customer support chatbot with 3 knowledge sources:
1. FAQ database (500 documents, high-quality)
2. Past ticket resolutions (10,000 documents, variable quality)
3. Product documentation (200 documents, authoritative)

**Your Task:**
Design a context selection strategy that:
- Limits context to 5 documents total
- Balances relevance, diversity, and source authority
- Prioritizes FAQ and documentation over past tickets

**Deliverable:** Pseudocode or flowchart showing selection logic.

**Example Solution:**
```python
# Step 1: Retrieve candidates from each source
faq_candidates = retrieve(query, source="faq", top_k=10)
ticket_candidates = retrieve(query, source="tickets", top_k=10)
doc_candidates = retrieve(query, source="documentation", top_k=10)

# Step 2: Apply business rules (prioritize authoritative sources)
faq_weighted = [(doc, score * 1.5) for doc, score in faq_candidates]  # 1.5x boost
doc_weighted = [(doc, score * 1.5) for doc, score in doc_candidates]  # 1.5x boost
ticket_weighted = [(doc, score * 1.0) for doc, score in ticket_candidates]  # No boost

# Step 3: Merge and re-rank
all_candidates = faq_weighted + doc_weighted + ticket_weighted
all_candidates.sort(key=lambda x: x[1], reverse=True)  # Sort by weighted score

# Step 4: Apply MMR for diversity (λ=0.6, favor relevance slightly)
selected = mmr_selection(all_candidates, top_k=5, lambda_param=0.6)

# Step 5: Ensure at least 1 FAQ and 1 doc in final selection
if not any(doc.source == "faq" for doc in selected):
    selected[-1] = faq_candidates[0]  # Replace lowest-ranked with top FAQ
if not any(doc.source == "documentation" for doc in selected):
    selected[-2] = doc_candidates[0]  # Replace 2nd-lowest with top doc
```

### Exercise 2: Compression ROI Calculator

**Scenario:** Your agent processes 1,000 queries/day with the following baseline:
- Query: 150 tokens
- Retrieved context: 10 documents × 2,000 tokens = 20,000 tokens
- Total input: 20,150 tokens
- API pricing: $0.015 per 1K input tokens (GPT-4 Turbo)

**Your Task:** Calculate monthly cost savings for each optimization:
1. Re-ranking + MMR reduces to 6 documents
2. Deduplication reduces 6 documents to 5 unique
3. LLMLingua compresses documents by 60%

**Deliverable:** Fill in the table:

| Stage | Documents | Tokens/Doc | Total Tokens | Cost/Query | Monthly Cost | Savings |
|-------|-----------|------------|--------------|------------|--------------|---------|
| Baseline | 10 | 2,000 | 20,150 | $0.302 | $9,060 | - |
| + Re-rank/MMR | 6 | 2,000 | ? | ? | ? | ? |
| + Dedup | 5 | 2,000 | ? | ? | ? | ? |
| + LLMLingua | 5 | 800 | ? | ? | ? | ? |

**Answer:**
| Stage | Documents | Tokens/Doc | Total Tokens | Cost/Query | Monthly Cost | Savings |
|-------|-----------|------------|--------------|------------|--------------|---------|
| Baseline | 10 | 2,000 | 20,150 | $0.302 | $9,060 | - |
| + Re-rank/MMR | 6 | 2,000 | 12,150 | $0.182 | $5,460 | $3,600 (40%) |
| + Dedup | 5 | 2,000 | 10,150 | $0.152 | $4,560 | $4,500 (50%) |
| + LLMLingua | 5 | 800 | 4,150 | $0.062 | $1,860 | $7,200 (79%) |

**Insight:** Compression techniques compound. Total savings: **$7,200/month (79% reduction)**.

### Exercise 3: Optimal Context Ordering

**Scenario:** You have the following context components for a code review agent:

- System prompt (500 tokens)
- User's code change (2,000 tokens)
- Relevant existing code (3,000 tokens)
- Coding style guide (1,000 tokens)
- Past PR feedback (1,500 tokens)
- User query: "Review this code for bugs" (10 tokens)

**Your Task:**
1. Order these components using "importance-based ordering" (place critical info at boundaries)
2. Justify your ordering based on primacy/recency effects
3. Calculate total context size

**Example Solution:**

**Optimal Ordering:**
1. **System prompt** (500 tokens) - *Position 1 (primacy): Sets agent role and review criteria*
2. **Coding style guide** (1,000 tokens) - *Position 2: Critical constraints*
3. **Past PR feedback** (1,500 tokens) - *Middle: Helpful context but less critical*
4. **Relevant existing code** (3,000 tokens) - *Positions N-2 to N-1 (recency): Immediate context for review*
5. **User's code change** (2,000 tokens) - *Position N-1 (recency): Primary subject of review*
6. **User query** (10 tokens) - *Position N (recency): Focus instruction*

**Total Context:** 8,010 tokens

**Justification:**
- **Primacy:** System prompt and style guide establish evaluation framework upfront
- **Recency:** User's code and existing code are at the end for immediate attention
- **Middle:** Past feedback provides background without demanding high attention

**Alternative (Interleaved):**
1. System prompt (500)
2. User query (10) - *Move query earlier to frame context*
3. User's code change (2,000)
4. Relevant existing code (3,000)
5. Coding style guide (1,000) - *Reference material*
6. Past PR feedback (1,500) - *Supporting context*

**Trade-off:** Moving query earlier provides framing but loses recency effect. Depends on whether agent benefits more from early framing or late focus.

---

## Further Reading

### Internal Resources
- [Memory Systems Fundamentals](memory_systems_fundamentals.md) - Deep dive into memory types and architectures
- [Memory Systems Implementation Notebook](memory_systems_implementation.ipynb) - Executable MMR, Search-o1, and compression examples
- [Agentic RAG Tutorial](04_Agentic_RAG.md) - Retrieval patterns and agent-driven memory access
- [Multi-Agent Fundamentals](multi_agent_fundamentals.md) - Multi-agent coordination via shared context

### External Research
- **Context Engineering Survey:** Mei et al., "A Survey of Context Engineering for Large Language Models" (2025) - `agents_memory.txt:491`
- **Lost in the Middle:** Liu et al., "Lost in the Middle: How Language Models Use Long Contexts" (2023) - `agents_memory.txt:452`
- **RULER Benchmark:** Hsieh et al., "RULER: What's the Real Context Size of Your Long-Context Language Models?" (2024) - `agents_memory.txt:232`
- **MMR Algorithm:** Carbonell & Goldstein, "The use of MMR, diversity-based reranking for reordering documents and producing summaries" (1998) - `agents_memory.txt:509`
- **LLMLingua:** [Microsoft Research LLMLingua GitHub](https://github.com/microsoft/LLMLingua)

### Production Tools
- **Re-ranking:** [Cohere Rerank API](https://cohere.com/rerank), [BGE Reranker](https://huggingface.co/BAAI/bge-reranker-large)
- **Vector Databases:** [Pinecone](https://www.pinecone.io/), [Weaviate](https://weaviate.io/), [Chroma](https://www.trychroma.com/), [Qdrant](https://qdrant.tech/)
- **Observability:** [LangSmith](https://www.langchain.com/langsmith), [Arize Phoenix](https://phoenix.arize.com/)

---

**Last Updated:** 2025-11-15
**Status:** ✅ Complete
**Reading Time:** ~27 minutes (measured)
