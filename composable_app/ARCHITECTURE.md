# Composable App Architecture

This document describes the architecture of the multi-agent content writing system, a reference implementation demonstrating enterprise GenAI patterns.

## Table of Contents
- [Overview](#overview)
- [Architecture Principles](#architecture-principles)
- [System Components](#system-components)
- [Data Flow](#data-flow)
- [Design Patterns](#design-patterns)
- [Extension Points](#extension-points)

## Overview

The Composable App is a **multi-agent content writing system** that demonstrates how to build production-ready GenAI applications using composable patterns. It generates educational content on various topics (history, math, GenAI) through a workflow involving specialized writer agents and a review panel.

**Key characteristics:**
- **LLM-agnostic**: Uses Pydantic AI for provider abstraction
- **Pattern-based**: Implements 8+ design patterns from the book
- **Cloud-ready**: Dockerized, deployable to Cloud Run/Fargate
- **Observable**: Structured logging for monitoring and evaluation

## Architecture Principles

### 1. Separation of Concerns
```
agents/     - Agent implementations (writers, reviewers, task assigner)
utils/      - Horizontal services (LLMs, prompts, guardrails, memory)
pages/      - UI workflow steps (Streamlit)
prompts/    - Jinja2 templates for all prompts
data/       - Vector index for RAG
```

### 2. Dependency Injection (Pattern 19)
All agents depend on abstractions, not concrete implementations:

```python
class AbstractWriter(ABC):
    @abstractmethod
    async def write_response(self, topic: str, prompt: str) -> Article:
        pass

    @abstractmethod
    async def revise_response(self, prompt: str) -> Article:
        pass
```

This enables:
- Easy testing with mock implementations
- Switching between writer types at runtime
- Independent development of components

### 3. Prompt as Configuration (Pattern 25)
Prompts are externalized as Jinja2 templates, not hardcoded:

```python
# agents/generic_writer_agent.py:61
prompt = PromptService.render_prompt(
    "AbstractWriter_write_about",
    content_type=self.get_content_type(),
    topic=topic,
    additional_instructions=ltm.search_relevant_memories(...)
)
```

Benefits:
- Non-engineers can modify prompts
- Version control for prompt changes
- A/B testing different prompts

### 4. Observability First
All horizontal services log inputs/outputs:

```json
// logs/prompts.json - All prompt I/O
// logs/guards.json  - Guardrail decisions
// logs/evals.log    - Evaluation data for training
```

## System Components

### Core Agents

#### 1. TaskAssigner (`agents/task_assigner.py`)
**Role**: Query classification and writer routing

**Flow**:
```
User Query → Input Guardrail → Classifier → Writer Assignment
                    ↓ reject
                Error Message
```

**Implementation**:
```python
class TaskAssigner:
    async def assign_writer(self, topic: str) -> Writer:
        # Pattern 32: Guardrails
        if not await self.guardrail.is_acceptable(topic):
            raise ValueError("Topic violates content policy")

        # Classification
        result = await self.agent.run(topic)
        return Writer[result.output]
```

**Located at**: `composable_app/agents/task_assigner.py:1-76`

#### 2. AbstractWriter & Specialized Writers (`agents/generic_writer_agent.py`)

**Writer Types**:
- **MathWriter**: Detailed mathematical solutions
- **HistoryWriter**: 2-paragraph historical content
- **GenAIWriter**: RAG-enhanced (uses book as knowledge base)
- **GeneralistWriter**: General topics

**Workflow**:
```
write_about() → [Memory retrieval] → write_response() → Article
revise_article() → [Memory + Review] → revise_response() → Revised Article
```

**RAG Implementation** (GenAIWriter):
```python
# agents/generic_writer_agent.py:151-162
async def write_response(self, topic: str, prompt: str) -> Article:
    # Pattern 6: Semantic RAG
    nodes = self.retriever.retrieve(topic)
    prompt += f"\n**INFORMATION YOU CAN USE**\n{nodes}"

    result = await self.agent.run(prompt)
    article = result.output

    # Add citations (Pattern 11: Trustworthy Generation)
    pages = [str(node.metadata['bbox'][0]['page']) for node in nodes]
    article = replace(article, full_text=article.full_text + f"\nSee pages: {', '.join(pages)}")
    return article
```

**Located at**: `composable_app/agents/generic_writer_agent.py:1-179`

#### 3. ReviewerPanel (`agents/reviewer_panel.py`)

**Panel composition**:
- **Specialist reviewers**: Math, Grammar, District representative
- **Adversarial reviewers**: Conservative parent, Liberal parent, School admin

**Pattern 23: Multi-agent collaboration**:
```python
async def review_in_parallel(self, article: Article) -> list[Review]:
    tasks = [reviewer.review(article) for reviewer in self.reviewers]
    return await asyncio.gather(*tasks)
```

### Horizontal Services (`utils/`)

#### 1. LLM Configuration (`utils/llms.py`)
**Purpose**: Centralized model configuration

```python
BEST_MODEL = "gemini-2.0-flash"       # High quality
DEFAULT_MODEL = "gemini-2.0-flash"    # Balanced
SMALL_MODEL = "gemini-2.5-flash-lite-preview-06-17"  # Low latency
EMBED_MODEL = "text-embedding-004"    # Embeddings
```

**Safety settings**:
- Temperature: 0.25 (consistency over creativity)
- Gemini safety: BLOCK_ONLY_HIGH (allows most content)

#### 2. Prompt Service (`utils/prompt_service.py`)
**Purpose**: Jinja2 template rendering with logging

```python
PromptService.render_prompt(
    "AbstractWriter_write_about",
    content_type="2 paragraphs",
    topic="Battle of Bulge",
    additional_instructions="..."
)
```

All renders logged to `logs/prompts.json`.

#### 3. Guardrails (`utils/guardrails.py`)
**Purpose**: Input validation using LLM-as-judge (Pattern 17)

```python
guardrail = InputGuardrail(
    name="content_policy",
    accept_condition="The topic is appropriate for K-12 education"
)

is_safe = await guardrail.is_acceptable(user_input, raise_exception=True)
```

Logs all decisions to `logs/guards.json`.

#### 4. Long-term Memory (`utils/long_term_memory.py`)
**Purpose**: Personalization via conversation history (Pattern 28)

```python
# Store feedback
ltm.add_memory("User prefers concise explanations")

# Retrieve relevant memories
context = ltm.search_relevant_memories("Writing style for math content")
```

#### 5. Evaluation Recording (`utils/save_for_eval.py`)
**Purpose**: Collect data for model improvement

```python
await evals.record_ai_response(
    "initial_draft",
    ai_input=prompt_vars,
    ai_response=result
)
```

Enables post-training of smaller models.

#### 6. Human Feedback (`utils/human_feedback.py`)
**Purpose**: Human-in-the-loop for critical decisions

Used in Streamlit workflow for writer assignment approval.

## Data Flow

### Content Generation Workflow

```
┌──────────────┐
│ User enters  │
│ topic query  │
└──────┬───────┘
       │
       ▼
┌──────────────────────────┐
│ TaskAssigner             │
│ - Input guardrail check  │  ◄── Pattern 32: Guardrails
│ - Classify topic         │
│ - Select writer type     │
└──────┬───────────────────┘
       │
       ▼
┌──────────────────────────┐
│ Writer (e.g., History)   │
│ - Retrieve memories      │  ◄── Pattern 28: Memory
│ - [GenAI: RAG retrieval] │  ◄── Pattern 6: RAG
│ - Generate draft         │
└──────┬───────────────────┘
       │
       ▼
┌──────────────────────────┐
│ ReviewerPanel            │
│ - Parallel reviews       │  ◄── Pattern 23: Multi-agent
│ - Specialists + Adversaries │
└──────┬───────────────────┘
       │
       ▼
┌──────────────────────────┐
│ Secretary consolidates   │
│ review feedback          │
└──────┬───────────────────┘
       │
       ▼
┌──────────────────────────┐
│ Writer revises article   │
│ based on feedback        │  ◄── Pattern 18: Reflection
└──────┬───────────────────┘
       │
       ▼
┌──────────────────────────┐
│ Final article output     │
└──────────────────────────┘
```

### RAG Data Flow (GenAIWriter)

```
┌─────────────┐
│ Book PDF    │
└─────┬───────┘
      │
      ▼
┌─────────────────────┐
│ OpenParse           │
│ - Extract text      │
│ - Parse structure   │
│ - Create chunks     │
└─────┬───────────────┘
      │
      ▼
┌─────────────────────┐
│ LlamaIndex          │
│ - Generate embeddings│
│ - Build vector index│
└─────┬───────────────┘
      │
      ▼
┌─────────────────────┐
│ Persistent Storage  │
│ data/               │
│ - vector_store.json │
│ - docstore.json     │
│ - index_store.json  │
└─────────────────────┘

Query time:
User Query → Embed → Similarity Search → Top 3 nodes → Context + Prompt → LLM
```

## Design Patterns

### Pattern Implementations

| Pattern # | Pattern Name | Location | Description |
|-----------|-------------|----------|-------------|
| 6 | Basic RAG | `agents/generic_writer_agent.py:142-165` | GenAIWriter uses book as knowledge base |
| 17 | LLM-as-Judge | `utils/guardrails.py:14-43` | Input validation via boolean LLM calls |
| 18 | Reflection | `agents/generic_writer_agent.py:74-89` | Revision based on panel feedback |
| 19 | Dependency Injection | `agents/generic_writer_agent.py:38-58` | AbstractWriter interface |
| 23 | Multi-agent | `agents/reviewer_panel.py` | Parallel reviewers with different personas |
| 25 | Prompt Caching | `utils/prompt_service.py` | Template-based prompt management |
| 28 | Long-term Memory | `utils/long_term_memory.py` | Conversation history retrieval |
| 32 | Guardrails | `utils/guardrails.py` | Input/output validation |

### Pattern Interactions

**Example: GenAIWriter combines 4 patterns**:

```python
# Pattern 19: Dependency Injection
class GenAIWriter(ZeroshotWriter):  # Extends abstract interface

    async def write_response(self, topic: str, prompt: str) -> Article:
        # Pattern 6: RAG
        nodes = self.retriever.retrieve(topic)

        # Pattern 25: Prompt Caching (via template)
        prompt = PromptService.render_prompt(...)

        # Pattern 28: Memory
        context = ltm.search_relevant_memories(...)

        result = await self.agent.run(prompt)
        return result.output
```

## Extension Points

### Adding a New Writer

1. **Define writer enum** in `agents/generic_writer_agent.py`:
```python
class Writer(AutoName):
    SCIENCE_WRITER = auto()
```

2. **Create writer class**:
```python
class ScienceWriter(ZeroshotWriter):
    def __init__(self):
        super().__init__(Writer.SCIENCE_WRITER)

    def get_content_type(self) -> str:
        return "detailed scientific explanation"
```

3. **Add system prompt**: `prompts/science_writer_system_prompt.j2`

4. **Update factory**:
```python
class WriterFactory:
    @staticmethod
    def create_writer(writer: Writer) -> AbstractWriter:
        match writer:
            case Writer.SCIENCE_WRITER.name:
                return ScienceWriter()
            # ...
```

5. **Update TaskAssigner** classification prompt to include new writer type

### Adding a New Reviewer

1. **Create system prompt**: `prompts/[role]_system_prompt.j2`

2. **Add to ReviewerPanel** in `agents/reviewer_panel.py`:
```python
self.reviewers.append(
    ReviewerAgent("Fact Checker", "fact_checker_system_prompt")
)
```

### Switching LLM Providers

**Current**: Gemini via Pydantic AI

**To add OpenAI**:
```python
# utils/llms.py
PROVIDER = os.getenv("LLM_PROVIDER", "gemini")

if PROVIDER == "openai":
    BEST_MODEL = "gpt-4o"
    DEFAULT_MODEL = "gpt-4o-mini"
    SMALL_MODEL = "gpt-4o-mini"
elif PROVIDER == "anthropic":
    BEST_MODEL = "claude-3-5-sonnet-20241022"
    # ...
```

Pydantic AI handles provider differences automatically.

### Adding Custom Guardrails

**Example: Toxicity check**:
```python
toxicity_guard = InputGuardrail(
    name="toxicity",
    accept_condition="The text contains no toxic, hateful, or offensive language"
)

# Chain multiple guardrails
async def validate_input(text: str) -> bool:
    policy_ok = await content_policy_guard.is_acceptable(text)
    toxicity_ok = await toxicity_guard.is_acceptable(text)
    return policy_ok and toxicity_ok
```

### Integrating External Memory (mem0ai)

**Replace** `utils/long_term_memory.py` implementation:
```python
from mem0 import Memory

memory = Memory()

def add_memory(text: str):
    memory.add(text, user_id="session_123")

def search_relevant_memories(query: str) -> str:
    results = memory.search(query, user_id="session_123")
    return "\n".join([r["text"] for r in results])
```

## Deployment Architecture

### Local Development
```
Streamlit UI (port 8501)
    ↓
Python App
    ↓
Gemini API (HTTPS)
```

### Cloud Run (Production)
```
User → HTTPS → Cloud Run Container
                    ↓
                Pydantic AI
                    ↓
                Gemini API

Environment:
- GEMINI_API_KEY (via Secret Manager)
- PORT=8080
- LOG_LEVEL=INFO
```

### Monitoring Stack (Future)
```
App → Pydantic Logfire → Dashboard
    → logs/*.json → BigQuery → Looker
```

## Performance Considerations

### Latency Optimization
- **Parallel reviews**: `asyncio.gather()` for ReviewerPanel
- **Small model for guardrails**: Uses fast model (gemini-2.5-flash-lite)
- **Prompt caching**: Template reuse reduces prompt tokens

### Cost Optimization
- **Temperature 0.25**: Reduces retry needs
- **Small models where appropriate**: Guardrails don't need reasoning
- **Structured logging**: Post-train cheaper SLMs from data

### Scalability
- **Stateless design**: Each request is independent
- **Cloud Run autoscaling**: 0 to N instances
- **Vector index**: Pre-computed, no runtime indexing

## Security

### API Key Management
```bash
# Development
keys.env (git-ignored)

# Production
Cloud Secret Manager → Environment variables
```

### Input Validation
- Guardrails reject policy violations
- Type checking on all inputs
- LLM safety settings enabled

### Output Validation
- Structured outputs (Pydantic models)
- Citation tracking (Pattern 11)
- Review process catches hallucinations

## Testing Strategy (Recommended)

### Unit Tests
```python
# tests/test_task_assigner.py
async def test_should_reject_inappropriate_topic():
    assigner = TaskAssigner()
    with pytest.raises(ValueError):
        await assigner.assign_writer("inappropriate content")
```

### Integration Tests
```python
# tests/test_workflow.py
async def test_should_generate_article_end_to_end():
    writer = WriterFactory.create_writer(Writer.HISTORIAN)
    article = await writer.write_about("Battle of Bulge")
    assert len(article.full_text) > 100
    assert "Battle" in article.title
```

### Evaluation
```python
# evals/test_quality.py
async def test_should_meet_quality_thresholds():
    # Use logged eval data
    df = pd.read_json("logs/evals.log", lines=True)

    # LLM-as-judge evaluation
    scores = await evaluate_batch(df["ai_response"])
    assert scores["accuracy"].mean() > 0.85
```

## Further Reading

- [Composable App README](README.md) - Setup and deployment
- [Generative AI Design Patterns book](../README.md) - Full pattern catalog
- [Pydantic AI docs](https://ai.pydantic.dev) - Framework reference
- [LlamaIndex docs](https://docs.llamaindex.ai) - RAG implementation

---

**Questions?** Open an issue or see [CONTRIBUTING.md](../CONTRIBUTING.md)
