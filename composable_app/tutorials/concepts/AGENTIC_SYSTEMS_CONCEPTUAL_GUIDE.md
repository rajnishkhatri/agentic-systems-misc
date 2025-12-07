# Agentic Systems Conceptual Guide

> A comprehensive reference for AI assistants designing and building agentic systems

---

## Table of Contents

1. [Core Architecture Patterns](#1-core-architecture-patterns)
2. [Agent Design Patterns](#2-agent-design-patterns)
3. [Horizontal Services (Cross-Cutting Concerns)](#3-horizontal-services-cross-cutting-concerns)
4. [Multi-Agent Orchestration](#4-multi-agent-orchestration)
5. [Memory and State Management](#5-memory-and-state-management)
6. [Guardrails and Safety](#6-guardrails-and-safety)
7. [RAG (Retrieval Augmented Generation)](#7-rag-retrieval-augmented-generation)
8. [Reflection and Self-Improvement](#8-reflection-and-self-improvement)
9. [Evaluation and Observability](#9-evaluation-and-observability)
10. [Design Trade-offs and Decision Framework](#10-design-trade-offs-and-decision-framework)
11. [Common Pitfalls and Solutions](#11-common-pitfalls-and-solutions)
12. [Quick Reference Cheatsheet](#12-quick-reference-cheatsheet)

---

## 1. Core Architecture Patterns

### 1.1 Dependency Injection (DI)

**What**: A design pattern where objects receive their dependencies from external sources rather than creating them internally.

**Core Principle**: "Depend on abstractions, not concretions" (Dependency Inversion Principle)

```python
# ❌ Without DI (tight coupling)
class ArticleGenerator:
    def __init__(self):
        self.llm = Gemini(api_key="...hardcoded...")
        self.database = PostgreSQL("localhost")

# ✅ With DI (loose coupling)
class ArticleGenerator:
    def __init__(self, llm: LLMInterface, database: DatabaseInterface):
        self.llm = llm
        self.database = database
```

**Benefits**:
| Benefit | Without DI | With DI |
|---------|-----------|---------|
| **Testing** | Must call real APIs ($$$, slow, flaky) | Mock dependencies (free, fast, deterministic) |
| **Provider switch** | Edit 10+ files | Edit 1 config file |
| **New agent type** | Modify UI, workflow, tests | Implement interface, done |
| **Parallel development** | Teams block each other | Teams work independently |
| **Migration** | Big-bang rewrite (risky) | Gradual migration (safe) |

---

### 1.2 Abstract Base Classes (ABC)

**What**: Define contracts that all implementations must honor.

```python
from abc import ABC, abstractmethod

class AbstractAgent(ABC):
    @abstractmethod
    async def process(self, input: str) -> Output:
        """All agents must implement this method."""
        pass

    @abstractmethod
    def get_output_type(self) -> str:
        """Define what type of output this agent produces."""
        pass
```

**Why ABC over regular class?**
- **Compile-time enforcement**: Missing implementations caught at instantiation, not runtime
- **IDE support**: Autocomplete and type hints
- **Contract clarity**: Clear what subclasses must implement

```python
# Without ABC: Fails at runtime
class BrokenAgent:
    pass  # Missing process()

agent = BrokenAgent()  # No error!
await agent.process("input")  # RuntimeError

# With ABC: Fails at instantiation
class BrokenAgent(AbstractAgent):
    pass  # Missing process()

agent = BrokenAgent()  # TypeError: Can't instantiate abstract class
```

---

### 1.3 Factory Pattern

**What**: Centralized object creation based on runtime conditions.

```python
class AgentFactory:
    @staticmethod
    def create_agent(agent_type: AgentType) -> AbstractAgent:
        match agent_type:
            case AgentType.MATH:
                return MathAgent()
            case AgentType.RESEARCH:
                return ResearchAgent()
            case AgentType.CODE:
                return CodeAgent()
            case _:
                return GeneralAgent()
```

**Benefits**:
- **DRY**: Creation logic exists in one place
- **Single Responsibility**: Factory handles creation, agents handle processing
- **Maintainability**: Adding new agents = edit factory only
- **Consistency**: All code uses same creation logic

**Variations**:
```python
# Dictionary mapping (more flexible)
class AgentFactory:
    _agents = {
        AgentType.MATH: MathAgent,
        AgentType.RESEARCH: ResearchAgent,
        AgentType.CODE: CodeAgent,
    }

    @staticmethod
    def create_agent(agent_type: AgentType) -> AbstractAgent:
        agent_class = AgentFactory._agents.get(agent_type, GeneralAgent)
        return agent_class()
```

---

### 1.4 Template Method Pattern

**What**: Define workflow skeleton in base class, let subclasses implement specific steps.

```python
class AbstractAgent(ABC):
    # Template method (concrete) - defines workflow
    async def execute(self, input: str) -> Output:
        # Step 1: Prepare context
        context = await self.prepare_context(input)
        
        # Step 2: Generate (abstract - subclasses implement)
        result = await self.generate(input, context)
        
        # Step 3: Log for evaluation
        await self.log_result(result)
        
        return result

    async def prepare_context(self, input: str) -> dict:
        """Shared implementation for all agents."""
        return {"memories": self.memory.search(input)}

    @abstractmethod
    async def generate(self, input: str, context: dict) -> Output:
        """Subclasses implement specific generation logic."""
        pass
```

**Benefits**:
- **Consistency**: All agents follow same workflow
- **DRY**: Shared logic (context prep, logging) in one place
- **Extensibility**: Subclasses only implement "variable parts"

---

## 2. Agent Design Patterns

### 2.1 Single-Purpose Agent

**What**: Each agent does one thing well.

```python
class SummarizerAgent(AbstractAgent):
    """Only summarizes content - does not analyze or transform."""
    
    async def process(self, text: str) -> Summary:
        return await self.llm.run(f"Summarize: {text}")
```

### 2.2 Specialist Agent

**What**: Agent with domain expertise and specialized system prompt.

```python
class MathAgent(AbstractAgent):
    def __init__(self):
        self.system_prompt = PromptService.render("math_expert_prompt")
        self.agent = Agent(
            llm_model,
            system_prompt=self.system_prompt,
            output_type=MathSolution
        )

    def get_output_type(self) -> str:
        return "detailed solution with step-by-step explanation"
```

### 2.3 Reviewer Agent (Critic Pattern)

**What**: Agent that evaluates and provides feedback on other agents' outputs.

```python
class ReviewerAgent(AbstractAgent):
    """Provides structured critique of generated content."""
    
    def __init__(self, persona: str):
        self.system_prompt = f"""You are a {persona}.
        Review content for:
        - Accuracy
        - Clarity
        - Completeness
        Provide specific, actionable feedback."""

    async def review(self, content: Output) -> Review:
        return await self.agent.run(f"Review: {content}")
```

### 2.4 Orchestrator Agent

**What**: Agent that coordinates multiple other agents.

```python
class OrchestratorAgent:
    def __init__(self, agents: list[AbstractAgent], reviewer: ReviewerPanel):
        self.agents = agents
        self.reviewer = reviewer

    async def process(self, input: str) -> Output:
        # Select appropriate agent
        agent = await self.select_agent(input)
        
        # Generate initial output
        draft = await agent.process(input)
        
        # Get review feedback
        feedback = await self.reviewer.review(draft)
        
        # Revise based on feedback
        final = await agent.revise(draft, feedback)
        
        return final
```

---

## 3. Horizontal Services (Cross-Cutting Concerns)

### 3.1 Overview

**What**: Shared utilities that support multiple agents and workflows.

```
┌─────────────────────────────────────────────────────────────┐
│                     LLM Application                          │
│                                                              │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │ Agent 1  │  │ Agent 2  │  │ Agent 3  │  │ Agent 4  │   │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘   │
│       │             │              │             │          │
│       └─────────────┴──────────────┴─────────────┘          │
│                          │                                   │
│              ┌───────────▼──────────────┐                   │
│              │  Horizontal Services     │                   │
│              │  ┌────────────────────┐  │                   │
│              │  │ Prompt Service     │  │ Jinja2 templates │
│              │  └────────────────────┘  │                   │
│              │  ┌────────────────────┐  │                   │
│              │  │ Guardrails         │  │ LLM-as-judge     │
│              │  └────────────────────┘  │                   │
│              │  ┌────────────────────┐  │                   │
│              │  │ Long-term Memory   │  │ Vector search    │
│              │  └────────────────────┘  │                   │
│              │  ┌────────────────────┐  │                   │
│              │  │ Evaluation Logs    │  │ JSON logging     │
│              │  └────────────────────┘  │                   │
│              └─────────────────────────┘                   │
└─────────────────────────────────────────────────────────────┘
```

**Benefits**:
- ✅ Shared utilities used by all agents
- ✅ Single source of truth
- ✅ Fix once, benefit everywhere
- ✅ Easy to test and mock

---

### 3.2 Prompt Service

**What**: Jinja2 template rendering for LLM prompts.

**Why**: Separate prompts from code for easier iteration and version control.

```python
class PromptService:
    @staticmethod
    def render_prompt(prompt_name: str, **variables) -> str:
        env = Environment(loader=FileSystemLoader("prompts"))
        template = env.get_template(f"{prompt_name}.j2")
        prompt = template.render(**variables)
        logger.info(prompt, extra={"prompt_name": prompt_name, **variables})
        return prompt
```

**Template example** (`agent_system_prompt.j2`):
```jinja2
You are a {{ agent_type }} specialist.

Your task is to {{ task_description }}.

{% if additional_context %}
Additional context:
{{ additional_context }}
{% endif %}

Output format: {{ output_format }}
```

**Benefits**:
- 🔄 Rapid iteration (change prompts without code changes)
- 🧪 A/B testing (compare prompt versions)
- 📝 Version control (track prompt changes in Git)
- 🔍 Debugging (see exact prompts in logs)

---

### 3.3 Guardrails Service

**What**: Input/output validation using LLMs as judges.

```python
class InputGuardrail:
    def __init__(self, name: str, accept_condition: str):
        self.system_prompt = PromptService.render_prompt(
            "guardrail_prompt",
            accept_condition=accept_condition
        )
        self.agent = Agent(
            llms.SMALL_MODEL,  # Fast & cheap for boolean decisions
            output_type=bool,
            system_prompt=self.system_prompt
        )

    async def is_acceptable(self, input: str, raise_exception: bool = False) -> bool:
        result = await self.agent.run(input)
        
        if raise_exception and not result.output:
            raise GuardrailException(f"Validation failed: {input}")
        
        return result.output
```

**Best Practices**:
```python
# Layered validation (combine rule-based + LLM)
async def validate_input(text: str) -> bool:
    # Layer 1: Fast rule-based pre-filter
    if len(text) > 10000 or contains_profanity(text):
        return False
    
    # Layer 2: LLM judge for nuanced validation
    return await guardrail.is_acceptable(text)
```

**Effective Accept Conditions**:
- ✅ "Query is appropriate for educational content"
- ✅ "Text does not contain personally identifiable information"
- ❌ "Query is good" (too vague)
- ❌ "Rate from 1-10" (use LLM-as-judge instead)

---

### 3.4 Evaluation Service

**What**: Structured logging of all LLM interactions for analysis.

```python
class Evals:
    async def record_ai_response(
        self,
        stage: str,
        ai_input: dict,
        ai_response: Any
    ) -> None:
        record = {
            "timestamp": datetime.utcnow().isoformat(),
            "stage": stage,
            "input": ai_input,
            "output": ai_response.dict() if hasattr(ai_response, 'dict') else str(ai_response)
        }
        logger.info(json.dumps(record))
```

**Benefits**:
- 🔍 Debug why specific outputs were generated
- 📊 Analyze patterns across interactions
- 🎯 Track which prompts produce best results
- 📈 Collect training data for fine-tuning

---

## 4. Multi-Agent Orchestration

### 4.1 Parallel Execution

**What**: Run independent agents concurrently for speed.

```python
# ❌ Sequential: 30 seconds (6 agents × 5s each)
for agent in agents:
    result = await agent.process(input)

# ✅ Parallel: 5 seconds (max of all agents)
results = await asyncio.gather(
    *[agent.process(input) for agent in agents]
)
```

**When to use**:
- Multiple reviewers evaluating same content
- Batch processing independent requests
- Multi-perspective analysis

### 4.2 Sequential Pipeline

**What**: Chain agents where output of one feeds into next.

```python
class Pipeline:
    def __init__(self, stages: list[AbstractAgent]):
        self.stages = stages

    async def process(self, input: str) -> Output:
        current = input
        for stage in self.stages:
            current = await stage.process(current)
        return current

# Usage
pipeline = Pipeline([
    ResearchAgent(),
    SummarizerAgent(),
    FormatterAgent()
])
result = await pipeline.process(query)
```

### 4.3 Reviewer Panel (Multi-Perspective)

**What**: Multiple reviewers with different personas provide diverse feedback.

```python
class ReviewerPanel:
    def __init__(self):
        self.reviewers = [
            ReviewerAgent(persona="Technical expert"),
            ReviewerAgent(persona="End user advocate"),
            ReviewerAgent(persona="Quality assurance"),
            ReviewerAgent(persona="Accessibility specialist"),
        ]
        self.secretary = SecretaryAgent()

    async def review(self, content: Output) -> str:
        # Parallel review
        reviews = await asyncio.gather(
            *[r.review(content) for r in self.reviewers]
        )
        
        # Consolidate into actionable feedback
        consolidated = await self.secretary.consolidate(reviews)
        return consolidated
```

### 4.4 Task Assignment / Routing

**What**: Classify input and route to appropriate specialist agent.

```python
class TaskRouter:
    def __init__(self, classifier: Agent, factory: AgentFactory):
        self.classifier = classifier
        self.factory = factory

    async def route(self, input: str) -> AbstractAgent:
        # Classify the task
        task_type = await self.classifier.run(input)
        
        # Create appropriate agent
        agent = self.factory.create_agent(task_type.output)
        
        return agent
```

---

## 5. Memory and State Management

### 5.1 Long-term Memory Architecture

**What**: Persistent storage and semantic retrieval of agent interactions.

```python
class LongTermMemory:
    def __init__(self, vector_store: VectorStore, embedder: Embedder):
        self.vector_store = vector_store
        self.embedder = embedder

    def add_memory(self, content: str, metadata: dict) -> str:
        embedding = self.embedder.embed(content)
        memory_id = self.vector_store.add(embedding, content, metadata)
        return memory_id

    def search(self, query: str, limit: int = 3) -> list[str]:
        query_embedding = self.embedder.embed(query)
        results = self.vector_store.search(query_embedding, limit)
        return [r.content for r in results]
```

### 5.2 Memory Integration in Agents

```python
class MemoryEnabledAgent(AbstractAgent):
    async def process(self, input: str) -> Output:
        # Retrieve relevant memories
        memories = self.memory.search(f"Processing: {input}")
        
        # Include in prompt context
        prompt = PromptService.render_prompt(
            "agent_prompt",
            input=input,
            memories="\n".join(memories)
        )
        
        return await self.agent.run(prompt)
```

### 5.3 Memory Lifecycle

```
1. SEARCH   → Query memory for relevant context
2. RETRIEVE → Get top-k semantically similar memories
3. INJECT   → Add to prompt as additional_instructions
4. GENERATE → LLM uses memories when generating
5. EXTRACT  → Identify learnings from interaction
6. STORE    → Save new memories for future use
```

### 5.4 Memory Categories

```python
# Writing preferences
add_memory("Use active voice and bullet points", {"category": "style"})

# Domain knowledge
add_memory("API rate limits: 1000 req/min", {"category": "technical"})

# Feedback incorporation
add_memory("Previous output was too verbose", {"category": "feedback"})

# User preferences (per-user)
add_memory("User prefers concise responses", {"category": "preference", "user_id": "user_123"})
```

---

## 6. Guardrails and Safety

### 6.1 Input Validation

```python
# Pre-processing validation
guardrail = InputGuardrail(
    name="content_safety",
    accept_condition="Content is appropriate and safe for processing"
)

async def process_with_guardrail(input: str) -> Output:
    # Validate first
    await guardrail.is_acceptable(input, raise_exception=True)
    
    # Then process
    return await agent.process(input)
```

### 6.2 Output Validation

```python
class OutputGuardrail:
    async def validate(self, output: Output) -> ValidationResult:
        checks = await asyncio.gather(
            self.check_factuality(output),
            self.check_safety(output),
            self.check_format(output)
        )
        return ValidationResult(passed=all(checks), details=checks)
```

### 6.3 PII Detection

```python
pii_guardrail = InputGuardrail(
    name="pii_detection",
    accept_condition="""The text does not contain:
    - Social Security Numbers
    - Credit card numbers
    - Full names with context
    - Home addresses
    - Phone numbers
    """
)
```

### 6.4 Domain-Specific Validation

```python
# Medical content
medical_guardrail = InputGuardrail(
    name="medical_safety",
    accept_condition="Query does not request medical diagnosis or treatment advice"
)

# Financial content
financial_guardrail = InputGuardrail(
    name="financial_safety",
    accept_condition="Content does not provide specific investment recommendations"
)
```

---

## 7. RAG (Retrieval Augmented Generation)

### 7.1 Basic RAG Pattern

```python
class RAGAgent(AbstractAgent):
    def __init__(self, retriever: VectorRetriever):
        self.retriever = retriever

    async def process(self, query: str) -> Output:
        # 1. Retrieve relevant documents
        docs = self.retriever.retrieve(query, top_k=5)
        
        # 2. Build context
        context = "\n\n".join([doc.content for doc in docs])
        
        # 3. Generate with context
        prompt = PromptService.render_prompt(
            "rag_prompt",
            query=query,
            context=context
        )
        
        return await self.agent.run(prompt)
```

### 7.2 RAG Prompt Template

```jinja2
Answer the question based on the provided context.
If the context doesn't contain enough information, say so.

CONTEXT:
{{ context }}

QUESTION: {{ query }}

ANSWER:
```

### 7.3 Advanced RAG Patterns

```python
# Hybrid search (semantic + keyword)
class HybridRetriever:
    def retrieve(self, query: str) -> list[Document]:
        semantic_results = self.vector_store.search(query)
        keyword_results = self.keyword_index.search(query)
        return self.rerank(semantic_results + keyword_results)

# Multi-step retrieval
class IterativeRAG:
    async def process(self, query: str) -> Output:
        # Initial retrieval
        docs = self.retriever.retrieve(query)
        
        # Generate follow-up questions
        follow_ups = await self.generate_follow_ups(query, docs)
        
        # Additional retrieval
        for follow_up in follow_ups:
            docs += self.retriever.retrieve(follow_up)
        
        # Final generation
        return await self.generate(query, docs)
```

---

## 8. Reflection and Self-Improvement

### 8.1 Reflection Pattern

**What**: Agent reviews and improves its own output based on feedback.

```
┌─────────────────────────────────────────────────────┐
│  1. INITIAL GENERATION                              │
│  Agent.generate(input)                              │
│  → Creates first version                            │
└─────────────────────────────────────────────────────┘
                       ↓
┌─────────────────────────────────────────────────────┐
│  2. REVIEW (Multi-Agent or Self-Review)             │
│  ReviewerPanel.review(draft)                        │
│  → Provides structured critique                     │
└─────────────────────────────────────────────────────┘
                       ↓
┌─────────────────────────────────────────────────────┐
│  3. REFLECTION & REVISION                           │
│  Agent.revise(draft, feedback)                      │
│  → Generates improved version addressing feedback   │
└─────────────────────────────────────────────────────┘
                       ↓
                 FINAL OUTPUT
```

### 8.2 Revision Implementation

```python
async def revise(
    self,
    original_input: str,
    initial_draft: Output,
    feedback: str
) -> Output:
    # Search memories for revision guidance
    memories = self.memory.search(f"Revising: {original_input}")
    
    prompt = PromptService.render_prompt(
        "revision_prompt",
        original_input=original_input,
        initial_draft=initial_draft,
        feedback=feedback,
        guidance=memories
    )
    
    revised = await self.agent.run(prompt)
    
    # Log for evaluation
    await self.evals.record("revision", {
        "input": original_input,
        "draft": initial_draft,
        "feedback": feedback,
        "revised": revised
    })
    
    return revised
```

### 8.3 Revision Prompt Template

```jinja2
Update the following output based on feedback.
Address the concerns to the extent possible.
Maintain the original requirements: {{ requirements }}.

ORIGINAL INPUT: {{ original_input }}

INITIAL DRAFT:
{{ initial_draft }}

FEEDBACK:
{{ feedback }}

{% if guidance %}
LESSONS FROM PAST REVISIONS:
{{ guidance }}
{% endif %}

REVISED OUTPUT:
```

### 8.4 Multi-Round Reflection

```python
async def iterative_revise(
    self,
    input: str,
    max_rounds: int = 3,
    quality_threshold: float = 0.9
) -> Output:
    output = await self.generate(input)
    
    for round in range(max_rounds):
        # Get feedback
        feedback = await self.reviewer.review(output)
        
        # Evaluate quality
        quality = await self.evaluate_quality(output, feedback)
        
        if quality >= quality_threshold:
            break
        
        # Revise
        output = await self.revise(input, output, feedback)
    
    return output
```

### 8.5 Memory-Enhanced Reflection

```python
async def revise_with_learning(self, input: str, draft: Output, feedback: str) -> Output:
    # Perform revision
    revised = await self.revise(input, draft, feedback)
    
    # Extract lessons learned
    lesson = await self.extract_lesson(draft, revised, feedback)
    
    # Store for future
    if lesson:
        self.memory.add_memory(lesson, {"category": "revision_learning"})
    
    return revised
```

---

## 9. Evaluation and Observability

### 9.1 Structured Logging

```python
# Log format (JSON lines)
{
    "timestamp": "2025-01-05T10:30:45.123Z",
    "stage": "generation",
    "agent": "MathAgent",
    "input": {...},
    "output": {...},
    "latency_ms": 1234,
    "token_usage": {"input": 500, "output": 200}
}
```

### 9.2 LLM-as-Judge Evaluation

```python
class QualityEvaluator:
    async def evaluate(self, output: Output, criteria: list[str]) -> EvalResult:
        prompt = PromptService.render_prompt(
            "evaluation_prompt",
            output=output,
            criteria=criteria
        )
        
        result = await self.judge_agent.run(prompt)
        return result.output
```

### 9.3 Human Feedback Integration

```python
def record_human_feedback(
    target: str,
    ai_input: Any,
    ai_response: Any,
    human_choice: Any,
    metadata: dict = None
) -> None:
    """Log when humans override or modify AI decisions."""
    record = {
        "timestamp": datetime.utcnow().isoformat(),
        "target": target,
        "ai_input": ai_input,
        "ai_response": ai_response,
        "human_choice": human_choice,
        "agreement": ai_response == human_choice,
        "metadata": metadata
    }
    logger.info(json.dumps(record))
```

### 9.4 Key Metrics to Track

| Metric | Description | Use Case |
|--------|-------------|----------|
| **Latency** | Time per operation | Performance optimization |
| **Token Usage** | Input/output tokens | Cost management |
| **Quality Score** | LLM-as-judge rating | Output quality tracking |
| **Guardrail Pass Rate** | % inputs passing validation | Safety monitoring |
| **Human Override Rate** | % AI decisions changed by humans | Trust calibration |
| **Revision Count** | Rounds needed to reach quality threshold | Efficiency tracking |

---

## 10. Design Trade-offs and Decision Framework

### 10.1 When to Use Dependency Injection

| Use DI When | Use Simple Code When |
|-------------|----------------------|
| Multiple implementations | One implementation |
| High testability needs | Manual testing OK |
| Code reused 3+ places | One-off script |
| Frequent changes expected | Stable, rarely changes |
| Team of 2+ developers | Solo developer |
| Production system | Prototype/PoC |

### 10.2 When to Use Async

| Use Async When | Use Sync When |
|----------------|---------------|
| Parallel operations (multi-agent) | Single sequential operation |
| High concurrency (100+ req/s) | Low volume |
| I/O-bound operations | CPU-bound operations |

### 10.3 When to Use Factory Pattern

| Use Factory When | Use Direct Instantiation When |
|------------------|-------------------------------|
| Creation logic used in 2+ places | Only one place creates objects |
| Runtime selection between types | Single implementation |
| Adding new types is expected | Types are fixed |

### 10.4 When to Use Memory

| Use Memory When | Skip Memory When |
|-----------------|------------------|
| Personalization needed | Stateless requests |
| Learning from feedback | One-time interactions |
| Multi-session context | Single-session use |
| User preferences matter | Generic responses OK |

### 10.5 When to Use RAG

| Use RAG When | Skip RAG When |
|--------------|---------------|
| External knowledge needed | LLM knowledge sufficient |
| Frequently updated information | Static knowledge |
| Domain-specific content | General knowledge |
| Reducing hallucination critical | Hallucination tolerable |

---

## 11. Common Pitfalls and Solutions

### 11.1 Liskov Substitution Principle Violations

**❌ Problem**: Subclass throws exception for inherited method
```python
class ReadOnlyAgent(AbstractAgent):
    async def revise(self, prompt: str) -> Output:
        raise NotImplementedError("Cannot revise")  # Breaks callers expecting revision
```

**✅ Solution**: Use separate interfaces or provide meaningful default
```python
class AbstractGenerator(ABC):
    @abstractmethod
    async def generate(self, input: str) -> Output: pass

class AbstractWriter(AbstractGenerator):
    @abstractmethod
    async def revise(self, prompt: str) -> Output: pass

# ReadOnlyAgent only implements AbstractGenerator
```

### 11.2 Ignoring Reviewer Feedback

**❌ Problem**: LLM revises but doesn't address feedback
```python
# Feedback: "Add mathematical formula"
# Bad revision: Just rephrases without adding formula
```

**✅ Solution**: Make feedback requirements explicit
```python
prompt = f"""Revise this content. 
You MUST address ALL issues marked as [CRITICAL].
You SHOULD address issues marked as [IMPORTANT].
{categorized_feedback}
"""
```

### 11.3 Over-Revision (Quality Degradation)

**❌ Problem**: Multiple rounds make output worse
```
Round 0: Score 0.70
Round 1: Score 0.85 ✓
Round 2: Score 0.82 ⚠️
Round 3: Score 0.65 ❌
```

**✅ Solution**: Implement convergence detection
```python
def should_stop_revising(history: list[Output]) -> bool:
    if len(history) < 3:
        return False
    
    scores = [score(output) for output in history[-3:]]
    improvement = scores[-1] - scores[-2]
    
    return improvement < 0.05 or scores[-1] < scores[-2]
```

### 11.4 Token Limit Exceeded

**❌ Problem**: Prompt too long (draft + feedback + memories)

**✅ Solution**: Strategic truncation
```python
def prepare_prompt(draft: str, feedback: str, memories: list, max_tokens: int = 3000):
    budget = {
        "instructions": 500,
        "draft": 1500,
        "feedback": 800,
        "memories": 200
    }
    
    return {
        "draft": truncate(draft, budget["draft"]),
        "feedback": prioritize_and_truncate(feedback, budget["feedback"]),
        "memories": memories[:3]  # Top 3 only
    }
```

### 11.5 Conflicting Feedback Paralysis

**❌ Problem**: Opposite feedback from different reviewers

**✅ Solution**: Conflict resolution rules in prompt
```python
prompt = f"""Revise based on feedback.

CONFLICT RESOLUTION:
1. Subject matter experts take priority for factual content
2. For style conflicts, defer to primary stakeholder
3. If consensus impossible, note the tradeoff made

{feedback}
"""
```

### 11.6 Tight Coupling to LLM Provider

**❌ Problem**: Hardcoded LLM client in agents
```python
class Agent:
    def __init__(self):
        self.llm = OpenAI(api_key="...")  # Can't switch providers
```

**✅ Solution**: Inject through abstraction
```python
class Agent:
    def __init__(self, llm: LLMInterface):
        self.llm = llm  # Any provider works

# Configuration in one place
llm = create_llm(provider="openai")  # or "anthropic", "gemini"
agent = Agent(llm=llm)
```

---

## 12. Quick Reference Cheatsheet

### Architecture Patterns

| Pattern | Use When | Example |
|---------|----------|---------|
| **DI** | Multiple implementations, testing needed | `Agent(llm: LLMInterface)` |
| **Factory** | Runtime selection, DRY creation | `AgentFactory.create(type)` |
| **Template Method** | Fixed workflow, variable implementation | `execute()` calls abstract `generate()` |
| **Strategy** | Swappable algorithms | Inject different generation strategies |

### Agent Patterns

| Pattern | Use When | Example |
|---------|----------|---------|
| **Single-Purpose** | One clear responsibility | SummarizerAgent |
| **Specialist** | Domain expertise needed | MathAgent, CodeAgent |
| **Reviewer** | Quality feedback needed | ReviewerPanel |
| **Orchestrator** | Coordinate multiple agents | TaskRouter |

### Service Patterns

| Service | Purpose | Key Method |
|---------|---------|------------|
| **PromptService** | Template rendering | `render_prompt(name, **vars)` |
| **Guardrails** | Input/output validation | `is_acceptable(input)` |
| **Memory** | Persistent state | `add()`, `search()` |
| **Evals** | Logging & tracking | `record_ai_response()` |

### Async Patterns

```python
# Parallel execution
results = await asyncio.gather(*[agent.process(input) for agent in agents])

# Parallel with guardrail
_, result = await asyncio.gather(
    guardrail.is_acceptable(input, raise_exception=True),
    agent.process(input)
)

# Sequential pipeline
for stage in stages:
    output = await stage.process(output)
```

### Memory Query Patterns

```python
# Writing task
memories = memory.search(f"{agent_type}, generate {topic}")

# Revision task
memories = memory.search(f"{agent_type}, revise {topic}")

# User-specific
memories = memory.search(query, user_id=user_id)
```

### Prompt Template Patterns

```jinja2
{# Variable substitution #}
{{ variable }}

{# Conditionals #}
{% if condition %}...{% endif %}

{# Loops #}
{% for item in items %}{{ item }}{% endfor %}

{# Structured sections #}
** BEGIN {{ section_name }} **
{{ content }}
** END {{ section_name }} **
```

---

## Conclusion

This guide provides a comprehensive reference for designing and implementing agentic systems. The key principles are:

1. **Composability**: Build systems from well-defined, single-purpose components
2. **Abstraction**: Depend on interfaces, not implementations
3. **Observability**: Log everything for debugging and improvement
4. **Safety**: Validate inputs and outputs with guardrails
5. **Memory**: Enable learning and personalization across sessions
6. **Reflection**: Improve outputs through structured feedback and revision

When in doubt, start simple and add complexity only when needed. The best architecture is one that solves today's problems while remaining flexible for tomorrow's requirements.

