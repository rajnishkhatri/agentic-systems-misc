# Multi-Agent Design Patterns

**Reading Time:** 22-28 minutes
**Prerequisites:** Understanding of multi-agent fundamentals
**Learning Objectives:**
- Master 4 core multi-agent design patterns (Sequential, Hierarchical, Collaborative, Competitive)
- Understand when to use each pattern based on task requirements
- Explore real-world automotive AI implementations of each pattern
- Analyze trade-offs: latency, cost, quality, complexity
- Apply pattern selection to real-world scenarios

---

## Introduction: Why Design Patterns Matter

Just as you wouldn't use a hammer for every carpentry task, you shouldn't use the same multi-agent pattern for every problem. The **right coordination strategy** depends on:

- **Task structure**: Sequential dependencies vs. parallelizable subtasks
- **Quality requirements**: Speed vs. accuracy vs. cost
- **Failure tolerance**: Can you afford a single point of failure?
- **Resource constraints**: Budget, latency limits, API rate limits

This tutorial covers **4 fundamental patterns** that solve 90% of real-world multi-agent coordination challenges.

---

## Pattern Comparison Overview

| Pattern | Coordination Style | Communication | Latency | Cost | Quality | Best For |
|---------|-------------------|---------------|---------|------|---------|----------|
| **Sequential** | Linear pipeline | One-way (A→B→C) | Slow ❌ | Low ✅ | Good | Tasks with strict dependencies |
| **Hierarchical** | Manager-Worker | Top-down delegation | Medium | Medium | Very Good ✅ | Complex tasks needing central coordination |
| **Collaborative** | Peer-to-Peer | Multi-directional | High ❌ | High ❌ | Excellent ✅ | Creative problem-solving, diverse expertise |
| **Competitive** | Parallel + Selection | Independent racing | Medium | High ❌ | Excellent ✅ | Quality-critical tasks, avoiding single-model bias |

---

## Pattern 1: Sequential (Pipeline)

### Description

Agents work in **linear order**, each passing output to the next agent. Think assembly line manufacturing.

**Workflow:**
```
Input → Agent 1 → Agent 2 → Agent 3 → Output
```

### When to Use

**Use Sequential When:**
- ✅ Tasks have **strict dependencies** (A must complete before B can start)
- ✅ Each step requires output from previous step
- ✅ Linear workflow is natural fit (e.g., ETL pipelines, RAG systems)
- ✅ **Simplicity matters** more than speed

**Avoid Sequential When:**
- ❌ Subtasks can run in parallel
- ❌ Latency is critical (can't afford waiting for each step)
- ❌ Any agent failure should not block entire pipeline

### Example: RAG Pipeline

```
User Query
    ↓
Classification Agent (determine query type: factual, opinion, procedural)
    ↓
Retrieval Agent (fetch relevant documents based on query type)
    ↓
Synthesis Agent (generate answer from documents)
    ↓
Validator Agent (check for hallucinations)
    ↓
User Response
```

**Code Example:**

```python
class SequentialPipeline:
    def __init__(self):
        self.agents = [
            ClassificationAgent(),
            RetrievalAgent(),
            SynthesisAgent(),
            ValidatorAgent()
        ]

    def execute(self, query: str) -> dict:
        """Execute agents in strict order."""
        state = {"query": query}

        for agent in self.agents:
            # Each agent modifies state
            state = agent.process(state)

            # If any agent fails, pipeline stops
            if state.get("error"):
                return state

        return state

# Usage
pipeline = SequentialPipeline()
result = pipeline.execute("What is the capital of France?")

# State evolution:
# Step 1: {"query": "What is the capital of France?", "type": "factual"}
# Step 2: {"query": ..., "type": "factual", "documents": [...]}
# Step 3: {"query": ..., "documents": [...], "answer": "Paris is the capital of France."}
# Step 4: {"query": ..., "answer": ..., "is_valid": True, "confidence": 0.95}
```

### Trade-offs

**Advantages:**
- ✅ **Simple to implement and debug**: Linear control flow
- ✅ **Clear accountability**: Easy to identify which step failed
- ✅ **Deterministic**: Same input always follows same path
- ✅ **Low coordination overhead**: No complex communication

**Disadvantages:**
- ❌ **Slowest pattern**: No parallelization (latency = sum of all agents)
- ❌ **Bottleneck risk**: One slow agent blocks entire pipeline
- ❌ **Single point of failure**: If Agent 2 fails, Agents 3-4 never run
- ❌ **Inflexible**: Hard to skip steps or change order dynamically

**Performance Metrics:**
```
Latency: Agent1 (2s) + Agent2 (3s) + Agent3 (5s) + Agent4 (1s) = 11s total
Cost: 4 LLM calls
Failure Rate: If any agent fails (e.g., 5% each) → 1 - (0.95^4) = 18.5% pipeline failure
```

---

## Pattern 2: Hierarchical (Manager-Worker)

### Description

**Manager agent** coordinates workflow, delegates to **worker agents**, and synthesizes results. Think corporate org structure with leader-follower dynamics.

**Workflow:**
```
User Query → Manager Agent
                ↓
    Determines strategy and delegates:
        ├── Worker Agent 1 (runs in parallel)
        ├── Worker Agent 2 (runs in parallel)
        └── Worker Agent 3 (runs in parallel)
                ↓
    Manager Agent synthesizes results → Response
```

### When to Use

**Use Hierarchical When:**
- ✅ **Complex tasks** need central coordination
- ✅ **Strategic decisions** required (which agents to involve, in what order)
- ✅ **Different expertise** needed for subtasks
- ✅ **Parallel execution** possible for independent subtasks
- ✅ Need to **synthesize diverse outputs** into coherent response

**Avoid Hierarchical When:**
- ❌ Manager agent becomes bottleneck (single point of failure)
- ❌ Overhead of coordination exceeds benefits
- ❌ Tasks are simple enough for sequential processing

### Example 1: Financial Analysis

```
User Query: "Should I invest in Tesla stock?"

Manager Agent analyzes query:
    - Requires financial data, market trends, competitive analysis
    - Delegates to 3 specialist agents in parallel:

    ├── Financial Data Agent: "Fetch Tesla's P/E ratio, revenue growth, debt levels"
    ├── Market Trends Agent: "Analyze EV industry growth, regulatory changes"
    └── Competitive Intelligence Agent: "Compare Tesla vs. competitors (Ford, GM, Rivian)"

Manager Agent waits for all results (2-3 seconds)

Manager Agent synthesizes:
    "Tesla's P/E ratio is high (67 vs. industry avg 15), but revenue growth is strong (24% YoY).
     EV market is growing rapidly (12% CAGR), and Tesla leads in market share (18%).
     However, competition is intensifying with Ford's F-150 Lightning and GM's Ultium platform.
     Recommendation: Moderate risk, suitable for growth-focused portfolios."
```

**Code Example:**

```python
from concurrent.futures import ThreadPoolExecutor, as_completed

class HierarchicalOrchestrator:
    def __init__(self):
        self.workers = {
            "financial": FinancialDataAgent(),
            "market": MarketTrendsAgent(),
            "competitive": CompetitiveIntelligenceAgent()
        }

    def execute(self, query: str) -> dict:
        """Manager delegates to workers in parallel."""
        # Step 1: Manager determines strategy
        strategy = self._plan_strategy(query)

        # Step 2: Delegate to workers in parallel
        worker_results = self._delegate_parallel(strategy)

        # Step 3: Manager synthesizes results
        final_response = self._synthesize(worker_results)

        return final_response

    def _delegate_parallel(self, strategy: dict) -> dict:
        """Run worker agents in parallel using ThreadPool."""
        results = {}

        with ThreadPoolExecutor(max_workers=3) as executor:
            # Submit all tasks
            future_to_agent = {
                executor.submit(self.workers[agent_name].process, task): agent_name
                for agent_name, task in strategy["tasks"].items()
            }

            # Collect results as they complete
            for future in as_completed(future_to_agent):
                agent_name = future_to_agent[future]
                try:
                    results[agent_name] = future.result()
                except Exception as e:
                    results[agent_name] = {"error": str(e)}

        return results

    def _synthesize(self, worker_results: dict) -> dict:
        """Manager combines worker outputs."""
        prompt = f"""
        You are a financial advisor synthesizing analysis from specialists:

        Financial Data: {worker_results['financial']}
        Market Trends: {worker_results['market']}
        Competitive Analysis: {worker_results['competitive']}

        Provide a coherent investment recommendation.
        """
        return self.manager_llm.generate(prompt)
```

### Example 2: Automotive AI (Orchestrator Agent)

**Real-World Case Study:** In-car assistant for autonomous vehicles.

**Scenario:** User asks "Is there a service area ahead with clean toilets?"

```
User Query → Orchestrator Agent (Manager)
                ↓
    Analyzes query: Needs navigation + facility ratings
                ↓
    Delegates to specialized agents:
        ├── Navigation Agent: "Find service areas within 50 km on current route"
        ├── Facility Ratings Agent: "Get cleanliness ratings for those service areas"
        └── POI Agent: "Get amenities (restaurants, shops) at those locations"
                ↓
    Orchestrator combines results:
    "Aire de Waremme, 20 km ahead on E19. Renovated last year, good facility ratings.
     Has Paul bakery and quick-service restaurant."
```

**Multi-Turn Context Switching:**

```
Turn 1: User asks about service areas → Orchestrator → Navigation Agent
Turn 2: User asks "Will it rain at my destination?" → Orchestrator switches to Weather Agent
Turn 3: User asks "How do I handle aquaplaning?" → Orchestrator switches to Car Manual Agent
```

**Key Feature:** Manager maintains conversation context across turns and routes to appropriate specialists.

### Trade-offs

**Advantages:**
- ✅ **Centralized control and oversight**: Manager makes strategic decisions
- ✅ **Parallel execution**: Workers run simultaneously (latency = max(worker times), not sum)
- ✅ **Clear escalation path**: If worker fails, manager can retry or use fallback
- ✅ **Flexible routing**: Manager can choose which workers to involve based on query

**Disadvantages:**
- ❌ **Manager is single point of failure**: If manager crashes, entire system fails
- ❌ **Sophisticated orchestration logic required**: Manager must understand worker capabilities
- ❌ **Manager overhead**: Extra LLM call for planning + synthesis
- ❌ **Worker coordination complexity**: Must handle partial failures, timeouts

**Performance Metrics:**
```
Latency: Manager Plan (1s) + max(Worker1: 2s, Worker2: 3s, Worker3: 2s) + Manager Synthesis (2s) = 6s
         vs. Sequential: 1s + 2s + 3s + 2s + 2s = 10s (40% faster!)
Cost: 1 manager plan + 3 workers + 1 synthesis = 5 LLM calls
Failure Handling: If Worker2 fails, manager can still synthesize from Workers 1 & 3
```

---

## Pattern 3: Collaborative (Shared Workspace)

### Description

Agents **share information and resources** to achieve a common goal. Think research team working together on a project with bidirectional communication.

**Workflow:**
```
Shared Workspace (conversation thread or shared state)
    ↑↓
Agent 1 contributes domain expertise
    ↑↓
Agent 2 adds complementary insights
    ↑↓
Agent 3 validates and refines
    ↑↓
Consensus or merged response
```

### When to Use

**Use Collaborative When:**
- ✅ **No single agent has complete information**
- ✅ **Multiple perspectives improve outcome** (e.g., creative writing, scientific research)
- ✅ **Cross-validation needed** (agents check each other's work)
- ✅ **Creative problem-solving** required
- ✅ **Consensus-building** improves quality over individual outputs

**Avoid Collaborative When:**
- ❌ Simple tasks where one agent suffices
- ❌ Latency is critical (collaboration requires multiple rounds)
- ❌ Agents might produce conflicting outputs that are hard to reconcile

### Example 1: Response Mixer (Automotive AI)

**Scenario:** User asks "How do I handle aquaplaning?"

**Step 1:** Three agents contribute independently to shared workspace

```python
shared_workspace = {
    "query": "How do I handle aquaplaning?",
    "contributions": []
}

# Agent 1: Car Manual Agent
shared_workspace["contributions"].append({
    "agent": "car_manual",
    "content": "Your Audi has ESC (Electronic Stability Control) and ABS to help prevent aquaplaning.",
    "confidence": 0.9
})

# Agent 2: General Knowledge Agent
shared_workspace["contributions"].append({
    "agent": "knowledge",
    "content": "Aquaplaning occurs when tires lose contact with road due to water buildup between tire and road surface.",
    "confidence": 0.95
})

# Agent 3: Safety Tips Agent
shared_workspace["contributions"].append({
    "agent": "safety",
    "content": "Ease off accelerator, avoid sudden braking/steering, gently steer in desired direction.",
    "confidence": 0.92
})
```

**Step 2:** Response Mixer Agent synthesizes

```python
class ResponseMixerAgent:
    def synthesize(self, workspace: dict) -> str:
        """Combine contributions into coherent response."""
        prompt = f"""
        Combine these expert contributions into a helpful, coherent response:

        {workspace["contributions"]}

        Requirements:
        - Integrate all key points
        - Maintain logical flow (what → why → how)
        - Avoid redundancy
        - Use natural language (not list format)
        """
        return self.llm.generate(prompt)

# Final Response:
"If you experience aquaplaning (when tires lose contact with road due to water),
ease off accelerator, avoid sudden braking/steering, and gently steer in desired direction.
Your Audi's ESC and ABS will help maintain control, but proper technique is essential."
```

### Example 2: Scientific Research Collaboration

**Scenario:** Multi-agent system for drug discovery

```
Research Question: "Is Compound X effective against melanoma?"

Agent 1 (Literature Review): Searches PubMed for studies on Compound X
Agent 2 (Molecular Analysis): Analyzes chemical structure for anti-cancer properties
Agent 3 (Clinical Trials): Checks ongoing/completed trials with Compound X
Agent 4 (Statistical Analysis): Evaluates study quality and effect sizes

Shared Workspace (iterative refinement):
Round 1: Each agent shares initial findings
Round 2: Agents challenge each other's interpretations (peer review)
Round 3: Agents reach consensus or flag disagreements
Round 4: Final report highlights strong evidence, weak evidence, and knowledge gaps
```

**Code Example:**

```python
class CollaborativeResearch:
    def __init__(self):
        self.agents = [
            LiteratureReviewAgent(),
            MolecularAnalysisAgent(),
            ClinicalTrialsAgent(),
            StatisticalAgent()
        ]
        self.workspace = {"findings": [], "challenges": [], "consensus": {}}

    def execute(self, query: str, max_rounds: int = 3) -> dict:
        """Iterative collaboration with peer review."""
        self.workspace["query"] = query

        for round_num in range(max_rounds):
            # Round 1: Initial contributions
            if round_num == 0:
                for agent in self.agents:
                    finding = agent.research(query)
                    self.workspace["findings"].append(finding)

            # Round 2+: Agents review each other's work
            else:
                for agent in self.agents:
                    critique = agent.review(self.workspace["findings"])
                    self.workspace["challenges"].append(critique)

                # Update findings based on critiques
                self._refine_findings()

        # Final consensus
        self.workspace["consensus"] = self._build_consensus()
        return self.workspace

    def _build_consensus(self) -> dict:
        """Identify areas of agreement and disagreement."""
        prompt = f"""
        Based on these findings and peer reviews:
        {self.workspace["findings"]}
        {self.workspace["challenges"]}

        Identify:
        1. Strong evidence (all agents agree)
        2. Weak evidence (conflicting interpretations)
        3. Knowledge gaps (insufficient data)
        """
        return self.consensus_agent.generate(prompt)
```

### Trade-offs

**Advantages:**
- ✅ **Leverages diverse expertise**: Each agent brings unique knowledge
- ✅ **Cross-validation improves quality**: Agents catch each other's errors
- ✅ **Robust to individual agent failures**: If one agent fails, others compensate
- ✅ **Creative problem-solving**: Diverse perspectives spark innovation

**Disadvantages:**
- ❌ **Coordination complexity**: Managing shared state across agents
- ❌ **Potential for conflicting outputs**: Agents may disagree (need conflict resolution)
- ❌ **Higher latency**: Multiple rounds of communication (3-5 rounds typical)
- ❌ **Higher cost**: More LLM calls than sequential or hierarchical

**Performance Metrics:**
```
Latency: 3 rounds × (agent contributions + synthesis) = 9-12s
Cost: 3 agents × 3 rounds + 3 synthesis calls = 12 LLM calls
Quality: Higher accuracy/completeness due to cross-validation
```

---

## Pattern 4: Competitive (Parallel + Selection)

### Description

Multiple agents work **independently in parallel** to solve the same task. An **evaluator agent** selects the best response or merges best elements. Think competitive bidding.

**Workflow:**
```
User Query → Broadcast to all agents
    ├── Agent A (approach 1)
    ├── Agent B (approach 2)
    └── Agent C (approach 3)
        ↓
Evaluator Agent selects best or merges
        ↓
User Response
```

### When to Use

**Use Competitive When:**
- ✅ **Multiple valid approaches exist** (no single "right" way)
- ✅ **Quality is more important than speed or cost**
- ✅ **Want to avoid single-model bias** (diversify across LLMs)
- ✅ **Need robustness** (if one agent hallucinates, others can catch it)
- ✅ **High-stakes decisions** (legal advice, medical diagnosis, financial recommendations)

**Avoid Competitive When:**
- ❌ Budget is tight (multiple agents = high cost)
- ❌ Latency is critical (evaluation adds overhead)
- ❌ Task is simple enough that one agent suffices

### Example 1: Diamond Pattern (Response Moderation)

**Automotive AI Example:** Rephrasing technical car manual language for drivers

```
User Query: "Why is my tire pressure warning light on?"

Car Manual Agent (raw technical response):
"Tire pressure monitoring system alert indicates one or more tires have fallen below
recommended inflation pressure of 2.2 bar. Affected tire at 1.8 bar (-18.75%).
Prolonged driving with underinflated tires decreases fuel efficiency, reduces tire
longevity, and compromises handling. Proceed to service station to reinflate per specifications."

                ↓
    Rephraser Agent (moderates for user-friendliness):

"Your front right tire is a bit low (1.8 bar). Safe to keep driving, but add air at next
petrol station. Low pressure affects fuel economy and tire wear. Want help finding a
nearby place to fill up?"
```

**Key Benefit:** Technical accuracy (from manual) + User-friendly language (from rephraser)

### Example 2: Multi-Model Competitive Analysis

**Scenario:** Legal contract review (high-stakes task)

```python
class CompetitiveContractReview:
    def __init__(self):
        self.agents = [
            LegalAgent(model="gpt-4"),
            LegalAgent(model="claude-3-opus"),
            LegalAgent(model="gemini-pro")
        ]
        self.evaluator = EvaluatorAgent()

    def review_contract(self, contract_text: str) -> dict:
        """Multiple agents review independently, evaluator selects best."""
        # Step 1: All agents analyze in parallel
        reviews = []
        with ThreadPoolExecutor(max_workers=3) as executor:
            futures = [
                executor.submit(agent.review, contract_text)
                for agent in self.agents
            ]
            reviews = [future.result() for future in futures]

        # Step 2: Evaluator selects best response
        evaluation = self.evaluator.select_best(reviews, criteria=[
            "completeness",  # Identified all risks?
            "accuracy",      # Legal analysis correct?
            "clarity"        # Easy to understand?
        ])

        return {
            "best_review": evaluation["best"],
            "all_reviews": reviews,
            "confidence": evaluation["confidence"]
        }
```

### Example 3: Creative Writing

**Scenario:** Generate marketing copy for a product

```
Query: "Write a tagline for eco-friendly water bottle"

Agent A (GPT-4): "Hydration that heals the planet"
Agent B (Claude): "Sip sustainably, live responsibly"
Agent C (Gemini): "Pure water, pure conscience"

Evaluator Agent (analyzes):
- Memorability: A (8/10), B (7/10), C (9/10)
- Brand alignment: A (9/10), B (8/10), C (7/10)
- Emotional appeal: A (7/10), B (9/10), C (8/10)

Winner: Agent A (highest overall score)
Alternative: Merge best elements → "Sip sustainably, heal the planet"
```

### Trade-offs

**Advantages:**
- ✅ **Quality through diversity**: Multiple approaches reduce risk of poor output
- ✅ **Avoids single-point failure**: If one agent hallucinates, others compensate
- ✅ **Can parallelize for speed**: Agents run simultaneously
- ✅ **Model-agnostic**: Mix different LLMs (GPT, Claude, Gemini) for best results

**Disadvantages:**
- ❌ **Higher cost**: 3-5× more LLM calls than single-agent
- ❌ **Need robust evaluation**: Selecting "best" is non-trivial (requires LLM-as-Judge)
- ❌ **Evaluation overhead**: Extra latency for judging + potential synthesis
- ❌ **Diminishing returns**: 5 agents rarely outperform 3 agents enough to justify cost

**Performance Metrics:**
```
Latency: max(Agent A: 4s, Agent B: 3s, Agent C: 5s) + Evaluator: 2s = 7s
         (vs. single agent: 4s, only 75% slower but much higher quality)
Cost: 3 agents + 1 evaluator = 4 LLM calls (vs. 1 for single agent)
Quality: 20-30% higher accuracy in high-stakes tasks (based on Google case studies)
```

---

## Pattern 5: Adaptive Loop (Iterative Refinement)

### Description

Agent **iteratively refines** its approach until satisfactory results are achieved. Think search query expansion.

**Workflow:**
```
Initial Query → Agent processes
    ↓
Check if results meet threshold
    ├── YES → Return results
    └── NO → Refine approach and retry (loop)
```

### When to Use

**Use Adaptive Loop When:**
- ✅ **Initial approach might fail** (e.g., search returns 0 results)
- ✅ **Iterative refinement improves quality** (e.g., query expansion, hypothesis testing)
- ✅ **Feedback loop available** (can measure result quality)
- ✅ **Willing to trade latency for quality**

### Example: Restaurant Search (Automotive AI)

**Scenario:** User asks "Find a nice Italian restaurant with vegan options"

```
Loop 1: Search "Italian restaurants vegan" → 0 results
    ↓
Loop 2: Expand to "Italian restaurants vegetarian options" → 2 results (low relevance)
    ↓
Loop 3: Broaden to "Italian restaurants" + filter for plant-based menu mentions → 5 results
    ↓
Loop 4: Fallback: "Vegan restaurants" + filter for Italian cuisine → 3 results
    ↓
Agent presents best matches from all loops with explanation:
"Found 5 Italian restaurants with plant-based options, plus 3 vegan restaurants
serving Italian cuisine. Top pick: Cucina Verde (Italian-vegan fusion, 4.8★ rating)."
```

**Code Example:**

```python
class AdaptiveSearchAgent:
    def search_with_refinement(self, query: str, max_loops: int = 4) -> list:
        """Iteratively refine search until good results found."""
        results = []
        refinements = self._generate_refinements(query)

        for loop_num, refined_query in enumerate(refinements[:max_loops]):
            loop_results = self._execute_search(refined_query)

            # Check if results meet quality threshold
            avg_relevance = self._calculate_relevance(loop_results, query)

            if avg_relevance >= 0.7:
                # Good enough, stop looping
                return loop_results

            # Accumulate results for final selection
            results.extend(loop_results)

        # Return best results across all loops
        return self._rank_results(results)[:10]

    def _generate_refinements(self, query: str) -> list[str]:
        """Use LLM to generate query variations."""
        prompt = f"""
        Original query: "{query}"

        Generate 4 search variations from most specific to most general:
        1. Exact match (narrow)
        2. Slight relaxation (remove one constraint)
        3. Broader search (keep main intent)
        4. Fallback (alternative approach)
        """
        return self.llm.generate(prompt).split("\n")
```

---

## Pattern Selection Decision Tree

**How to choose the right pattern for your use case:**

```
Start: What is your primary constraint?

├── Constraint: SIMPLICITY (easy to implement/debug)
│   → Use Sequential Pattern
│   Example: Basic RAG pipeline, ETL workflows
│
├── Constraint: LATENCY (must be fast)
│   ├── Can subtasks run in parallel?
│   │   ├── YES + need central coordination → Hierarchical Pattern
│   │   │   Example: Financial analysis with 3 specialists
│   │   └── YES + independent tasks → Competitive Pattern (if quality critical)
│   │       Example: Multi-model contract review
│   └── NO (strict dependencies) → Sequential Pattern (optimize each agent)
│
├── Constraint: QUALITY (accuracy is critical)
│   ├── Need diverse perspectives? → Collaborative Pattern
│   │   Example: Scientific research, creative writing
│   └── Want to avoid single-model bias? → Competitive Pattern
│       Example: High-stakes legal/medical decisions
│
├── Constraint: COST (limited budget)
│   → Use Sequential or Hierarchical (avoid Collaborative/Competitive)
│   Optimization: Use smaller models for simple tasks, large models for complex reasoning
│
└── Constraint: ADAPTABILITY (handle failures gracefully)
    ├── Initial approach might fail? → Adaptive Loop Pattern
    │   Example: Search query expansion
    └── Need fallback agents? → Hierarchical with redundancy
        Example: Primary weather API + backup APIs
```

---

## Real-World Pattern Combinations

Most production systems **combine multiple patterns** for optimal results.

### Example: Automotive AI Assistant (All 5 Patterns)

```
User Interaction Layer
    ↓
Orchestrator Agent (Hierarchical - central routing)
    ↓
├── Simple queries → Sequential (Navigation Agent → Response)
│
├── Complex queries → Hierarchical (delegate to specialists in parallel)
│   Example: "Plan route with charging stations"
│   ├── Navigation Agent
│   ├── EV Charging API Agent
│   └── Traffic Prediction Agent
│
├── Safety-critical queries → Competitive (multiple agents + validator)
│   Example: "How do I handle aquaplaning?"
│   ├── Car Manual Agent
│   ├── Safety Tips Agent
│   └── Validator Agent selects best
│
├── Ambiguous queries → Adaptive Loop (refine search)
│   Example: "Find Italian restaurant vegan options"
│   Loop 1: Exact match → Loop 2: Relaxed → Loop 3: Fallback
│
└── Multi-domain queries → Collaborative (Response Mixer)
    Example: "Service area with toilets and food"
    ├── Navigation Agent (location)
    ├── Facility Ratings Agent (cleanliness)
    └── POI Agent (amenities)
    Response Mixer combines all
```

---

## Cost-Quality-Latency Trade-off Analysis

**Scenario:** Answering a complex user query

| Pattern | Latency | Cost (LLM calls) | Quality | Complexity |
|---------|---------|------------------|---------|------------|
| **Sequential** (4 agents) | 10s | 4 | 75% | Low |
| **Hierarchical** (1 manager + 3 workers) | 6s | 5 | 85% | Medium |
| **Collaborative** (3 agents, 3 rounds) | 12s | 12 | 90% | High |
| **Competitive** (3 agents + evaluator) | 7s | 4 | 92% | Medium |
| **Adaptive Loop** (avg 2.5 loops) | 8s | 2.5 | 80% | Medium |

**Key Insights:**
1. **Sequential** is cheapest but slowest and lowest quality
2. **Hierarchical** is best balance for most use cases (good quality, reasonable latency/cost)
3. **Collaborative** achieves highest quality but at high latency/cost (use sparingly)
4. **Competitive** is best for quality-critical tasks where budget allows
5. **Adaptive Loop** is efficient when initial queries often fail

---

## Practical Exercise: Design a Customer Support Multi-Agent System

**Scenario:**
You're building a customer support chatbot for an e-commerce platform. It must handle:
- Order status inquiries
- Product recommendations
- Technical troubleshooting
- Refund requests

**Your Task:**

### Step 1: Choose Patterns for Each Query Type

For each query type, select the most appropriate pattern and justify:

1. **Order Status:** "Where is my order?"
   - Pattern: _______________
   - Justification: _______________

2. **Product Recommendation:** "I need a gift for a 10-year-old who likes science"
   - Pattern: _______________
   - Justification: _______________

3. **Technical Troubleshooting:** "My headphones won't charge"
   - Pattern: _______________
   - Justification: _______________

4. **Refund Request:** "I want to return a defective item"
   - Pattern: _______________
   - Justification: _______________

**Example Answers:**

```
1. Order Status:
   Pattern: Sequential
   Justification: Simple linear workflow:
   - Authenticate user → Query order database → Format response
   - Fast, cheap, no need for multiple perspectives

2. Product Recommendation:
   Pattern: Collaborative
   Justification: Multiple perspectives improve quality:
   - Agent 1: Analyze user profile and past purchases
   - Agent 2: Search product catalog for science toys
   - Agent 3: Check inventory and pricing
   - Synthesize personalized recommendations

3. Technical Troubleshooting:
   Pattern: Adaptive Loop
   Justification: Diagnosis requires iterative refinement:
   - Loop 1: Check common issues (cable, power source)
   - Loop 2: If not resolved, ask diagnostic questions
   - Loop 3: Search knowledge base for similar cases
   - Loop 4: Escalate to human agent if needed

4. Refund Request:
   Pattern: Hierarchical
   Justification: Requires policy checks + multiple actions:
   - Manager Agent: Check refund eligibility (purchase date, condition)
   - Worker Agents (parallel):
     ├── Inventory Agent: Check if return accepted
     ├── Payment Agent: Calculate refund amount
     └── Shipping Agent: Generate return label
   - Manager: Synthesize response with next steps
```

### Step 2: Design the Overall Architecture

Combine patterns into a unified system:

```
User Query → Classification Agent
    ↓
Router (Hierarchical Orchestrator)
    ├── "Order status" → Sequential Pipeline
    ├── "Product recommendation" → Collaborative Team
    ├── "Troubleshooting" → Adaptive Loop
    └── "Refund request" → Hierarchical Workflow
```

### Step 3: Identify Failure Modes

What could go wrong? How would you handle:
- Database timeout (order status query)
- Conflicting recommendations (product agents disagree)
- User provides incomplete info (troubleshooting)
- Refund policy violation (user ineligible)

---

## Summary

**What You Learned:**

1. **4 Core Patterns**:
   - **Sequential**: Linear pipeline, simple but slow
   - **Hierarchical**: Manager-worker, best general-purpose pattern
   - **Collaborative**: Shared workspace, highest quality but expensive
   - **Competitive**: Parallel + selection, quality through diversity

2. **When to Use Each Pattern**:
   - Sequential: Strict dependencies, simplicity matters
   - Hierarchical: Complex tasks, central coordination, parallel subtasks
   - Collaborative: Diverse expertise, creative problem-solving
   - Competitive: Quality-critical, avoid single-model bias

3. **Real-World Combinations**:
   - Production systems mix patterns (Automotive AI uses all 5)
   - Router/Orchestrator selects pattern based on query type

4. **Trade-off Analysis**:
   - Sequential: Cheap, slow, low quality
   - Hierarchical: Best balance (quality, latency, cost)
   - Collaborative/Competitive: High quality, high cost

**Next Steps:**

- **Learn challenges**: Read `multi_agent_challenges_evaluation.md` for debugging, coordination, and evaluation strategies
- **Hands-on practice**: Complete `multi_agent_patterns_comparison.ipynb` to benchmark patterns on same tasks
- **Case study**: Explore `automotive_ai_case_study.ipynb` to see 5 patterns in production

**Key Takeaway:**
There is no "best" pattern—only the right pattern for your constraints. Master when to use each, and you'll build robust, efficient, high-quality multi-agent systems.

---

**Related Tutorials:**
- [Multi-Agent Fundamentals](multi_agent_fundamentals.md) - Core concepts and architectural components
- [Multi-Agent Challenges & Evaluation](multi_agent_challenges_evaluation.md) - Debugging and metrics
- [Automotive AI Case Study](automotive_ai_case_study.ipynb) - Real-world pattern implementation

**References:**
- Google's "Agents Companion" Whitepaper (February 2025)
- Topic 03: Multi-Agent Architectures (lines 156-241)
- Topic 07: Case Studies - Automotive AI (lines 116-209)
