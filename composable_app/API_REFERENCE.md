# Composable App API Reference

Complete API reference for the composable app modules.

## Table of Contents
- [Agents](#agents)
- [Utils](#utils)
- [Data Models](#data-models)

---

## Agents

### `agents.article`

#### `Article`
Data model for generated content.

**Type**: `@dataclass`

**Attributes**:
- `full_text: str` - Full article text in Markdown format
- `title: str` - Article title suitable for target audience
- `key_lesson: str` - One-sentence summary of key learning point
- `index_keywords: list[str]` - Keywords for indexing

**Methods**:
```python
def to_markdown(self) -> str:
    """Convert article to formatted Markdown string.

    Returns:
        Formatted markdown with title, key lesson, details, and keywords
    """
```

**Usage**:
```python
from agents.article import Article

article = Article(
    full_text="Detailed content here...",
    title="The Battle of the Bulge",
    key_lesson="Last major German offensive of WWII",
    index_keywords=["WWII", "Ardennes", "1944"]
)

markdown = article.to_markdown()
```

**Location**: `composable_app/agents/article.py:6-23`

---

### `agents.generic_writer_agent`

#### `Writer` (Enum)
Enumeration of available writer types.

**Values**:
- `Writer.HISTORIAN` - Historical content (2 paragraphs)
- `Writer.MATH_WRITER` - Mathematical solutions (detailed)
- `Writer.GENAI_WRITER` - GenAI topics with RAG
- `Writer.GENERALIST` - General topics (short article)

**Usage**:
```python
from agents.generic_writer_agent import Writer

writer_type = Writer.HISTORIAN
```

#### `AbstractWriter` (ABC)
Abstract base class for all writer implementations.

**Methods**:
```python
async def write_about(self, topic: str) -> Article:
    """Generate initial article on given topic.

    Args:
        topic: The subject to write about

    Returns:
        Article object with generated content

    Workflow:
        1. Retrieve relevant memories
        2. Render prompt with topic and content type
        3. Call write_response()
        4. Record response for evaluation
    """

async def revise_article(
    self,
    topic: str,
    initial_draft: Article,
    panel_review: str
) -> Article:
    """Revise article based on review feedback.

    Args:
        topic: Original topic
        initial_draft: Previous version of article
        panel_review: Consolidated feedback from reviewers

    Returns:
        Revised Article object
    """

@abstractmethod
async def write_response(self, topic: str, prompt: str) -> Article:
    """Generate article (implementation-specific).

    Must be implemented by subclasses.
    """

@abstractmethod
async def revise_response(self, prompt: str) -> Article:
    """Revise article (implementation-specific).

    Must be implemented by subclasses.
    """

@abstractmethod
def get_content_type(self) -> str:
    """Return content type string (e.g., '2 paragraphs').

    Must be implemented by subclasses.
    """
```

**Location**: `composable_app/agents/generic_writer_agent.py:38-89`

#### `ZeroshotWriter`
Base implementation using zero-shot prompting.

**Constructor**:
```python
def __init__(self, writer: Writer):
    """Initialize zero-shot writer.

    Args:
        writer: Writer type enum value

    Creates:
        - System prompt from {writer.name}_system_prompt.j2
        - Pydantic AI agent with Article output type
    """
```

**Subclasses**:
- `MathWriter`: Detailed mathematical solutions
- `HistoryWriter`: 2-paragraph historical content
- `GeneralistWriter`: Short articles on general topics

**Location**: `composable_app/agents/generic_writer_agent.py:91-137`

#### `GenAIWriter`
RAG-enhanced writer for GenAI topics.

**Constructor**:
```python
def __init__(self):
    """Initialize GenAI writer with RAG capabilities.

    Sets up:
        - Google GenAI embeddings (text-embedding-004)
        - LlamaIndex vector store from data/
        - Retriever with top-k=3
    """
```

**Methods**:
```python
async def write_response(self, topic: str, prompt: str) -> Article:
    """Generate article with RAG augmentation.

    Workflow:
        1. Retrieve top-3 similar nodes from vector index
        2. Append nodes to prompt as context
        3. Generate article with LLM
        4. Add page citations to article

    Args:
        topic: Query for semantic retrieval
        prompt: Full prompt with instructions

    Returns:
        Article with citations (e.g., "See pages: 42, 87, 103")
    """
```

**Location**: `composable_app/agents/generic_writer_agent.py:142-165`

#### `WriterFactory`
Factory for creating writer instances.

**Methods**:
```python
@staticmethod
def create_writer(writer: Writer) -> AbstractWriter:
    """Create writer instance based on type.

    Args:
        writer: Writer enum value or name string

    Returns:
        Concrete writer instance (MathWriter, HistoryWriter, etc.)

    Example:
        writer = WriterFactory.create_writer(Writer.HISTORIAN)
        article = await writer.write_about("Battle of the Bulge")
    """
```

**Location**: `composable_app/agents/generic_writer_agent.py:167-179`

---

### `agents.task_assigner`

#### `TaskAssigner`
Query classification and writer routing agent.

**Constructor**:
```python
def __init__(self):
    """Initialize task assigner with guardrail.

    Creates:
        - Input guardrail for K-12 appropriateness
        - Classification agent (returns Writer enum name)
    """
```

**Methods**:
```python
async def assign_writer(self, topic: str) -> Writer:
    """Classify topic and assign appropriate writer.

    Args:
        topic: User query or topic

    Returns:
        Writer enum value (HISTORIAN, MATH_WRITER, etc.)

    Raises:
        ValueError: If topic violates content policy

    Workflow:
        1. Check input guardrail
        2. Classify topic with LLM
        3. Return Writer enum
        4. Record for evaluation
    """
```

**Usage**:
```python
from agents.task_assigner import TaskAssigner

assigner = TaskAssigner()
writer_type = await assigner.assign_writer("Battle of the Bulge")
# Returns: Writer.HISTORIAN
```

**Location**: `composable_app/agents/task_assigner.py:1-76`

---

### `agents.reviewer_panel`

#### `ReviewerAgent`
Individual reviewer with specific persona.

**Constructor**:
```python
def __init__(self, role: str, system_prompt_file: str):
    """Initialize reviewer agent.

    Args:
        role: Reviewer's role name (e.g., "Grammar Reviewer")
        system_prompt_file: Jinja2 template filename
    """
```

**Methods**:
```python
async def review(self, article: Article) -> str:
    """Review article and provide feedback.

    Args:
        article: Article to review

    Returns:
        String containing review feedback
    """
```

#### `ReviewerPanel`
Manages multiple reviewers for parallel review.

**Constructor**:
```python
def __init__(self):
    """Initialize review panel with default reviewers.

    Default reviewers:
        - Grammar Reviewer (specialist)
        - Math Reviewer (specialist)
        - District Representative (specialist)
        - Conservative Parent (adversarial)
        - Liberal Parent (adversarial)
        - School Administrator (adversarial)
    """
```

**Methods**:
```python
async def review_article(self, article: Article) -> str:
    """Conduct parallel review by all panel members.

    Args:
        article: Article to review

    Returns:
        Consolidated feedback from all reviewers

    Implementation:
        Uses asyncio.gather() for parallel execution
    """
```

**Usage**:
```python
from agents.reviewer_panel import ReviewerPanel

panel = ReviewerPanel()
feedback = await panel.review_article(article)
```

**Location**: `composable_app/agents/reviewer_panel.py`

---

## Utils

### `utils.llms`

#### Configuration Constants
```python
BEST_MODEL = "gemini-2.0-flash"          # Highest quality
DEFAULT_MODEL = "gemini-2.0-flash"       # Balanced
SMALL_MODEL = "gemini-2.5-flash-lite-preview-06-17"  # Fastest
EMBED_MODEL = "text-embedding-004"       # Embeddings
```

#### `default_model_settings()`
```python
def default_model_settings() -> GeminiModelSettings:
    """Get default model settings for Pydantic AI.

    Returns:
        GeminiModelSettings with:
            - temperature: 0.25 (consistent outputs)
            - safety_settings: BLOCK_ONLY_HIGH for dangerous content
    """
```

**Usage**:
```python
from utils import llms
from pydantic_ai import Agent

agent = Agent(
    llms.DEFAULT_MODEL,
    model_settings=llms.default_model_settings()
)
```

**Location**: `composable_app/utils/llms.py:1-36`

---

### `utils.prompt_service`

#### `PromptService`
Jinja2 template rendering service.

**Methods**:
```python
@staticmethod
def render_prompt(prompt_name: str, **variables: Any) -> str:
    """Render Jinja2 template with variables.

    Args:
        prompt_name: Template filename without .j2 extension
        **variables: Template variables

    Returns:
        Rendered prompt string

    Side effects:
        Logs prompt to logs/prompts.json with all variables

    Example:
        prompt = PromptService.render_prompt(
            "AbstractWriter_write_about",
            topic="WWII",
            content_type="2 paragraphs"
        )
    """
```

**Template Location**: `composable_app/prompts/`

**Naming Convention**: `{Agent}_{action}.j2`

**Examples**:
- `AbstractWriter_write_about.j2`
- `AbstractWriter_revise_article.j2`
- `TaskAssigner_assign_writer.j2`

**Location**: `composable_app/utils/prompt_service.py:1-27`

---

### `utils.guardrails`

#### `InputGuardrail`
LLM-based input validation (Pattern 17: LLM-as-Judge).

**Constructor**:
```python
def __init__(self, name: str, accept_condition: str):
    """Initialize input guardrail.

    Args:
        name: Guardrail identifier
        accept_condition: Condition text for acceptance
            (e.g., "The topic is appropriate for K-12 education")

    Creates:
        Agent that returns bool (True = accept, False = reject)
    """
```

**Methods**:
```python
async def is_acceptable(
    self,
    prompt: str,
    raise_exception: bool = False
) -> bool:
    """Check if input meets acceptance condition.

    Args:
        prompt: Input text to validate
        raise_exception: If True, raise InputGuardrailException on rejection

    Returns:
        True if acceptable, False otherwise

    Side effects:
        Logs decision to logs/guards.json
    """
```

**Usage**:
```python
from utils.guardrails import InputGuardrail, InputGuardrailException

guardrail = InputGuardrail(
    name="content_policy",
    accept_condition="The topic is appropriate for K-12 education"
)

try:
    is_safe = await guardrail.is_acceptable(user_input, raise_exception=True)
except InputGuardrailException as e:
    print(f"Input rejected: {e}")
```

**Location**: `composable_app/utils/guardrails.py:1-43`

---

### `utils.long_term_memory`

#### Functions

```python
def add_memory(text: str) -> None:
    """Store information for future retrieval.

    Args:
        text: Information to remember (e.g., user preferences)

    Example:
        add_memory("User prefers concise explanations")
    """

def search_relevant_memories(query: str) -> str:
    """Retrieve relevant past information.

    Args:
        query: Search query

    Returns:
        String containing relevant memories (empty if none)

    Example:
        context = search_relevant_memories("writing style for history")
    """
```

**Usage in Agents**:
```python
from utils import long_term_memory as ltm

# Add memory
ltm.add_memory("User feedback: Make math explanations more visual")

# Retrieve in prompt
additional_instructions = ltm.search_relevant_memories(
    f"{self.writer.name}, write about {topic}"
)
```

**Location**: `composable_app/utils/long_term_memory.py`

---

### `utils.save_for_eval`

#### Functions

```python
async def record_ai_response(
    stage: str,
    ai_input: dict[str, Any],
    ai_response: Any
) -> None:
    """Record AI interaction for evaluation.

    Args:
        stage: Workflow stage (e.g., "initial_draft", "revised_draft")
        ai_input: Dictionary with prompt variables
        ai_response: AI output (Article, Review, etc.)

    Side effects:
        Appends to logs/evals.log in JSON format

    Example:
        await evals.record_ai_response(
            "initial_draft",
            ai_input={"topic": "WWII", "content_type": "2 paragraphs"},
            ai_response=article
        )
    """
```

**Purpose**: Collect training data for smaller model distillation.

**Location**: `composable_app/utils/save_for_eval.py`

---

### `utils.human_feedback`

#### Functions

```python
async def request_approval(
    prompt: str,
    options: list[str] = ["Approve", "Reject"]
) -> str:
    """Request human decision in workflow.

    Args:
        prompt: Question to ask user
        options: List of valid responses

    Returns:
        Selected option string

    UI Integration:
        - Streamlit: Uses st.radio()
        - CLI: Uses input()
    """
```

**Usage**:
```python
from utils.human_feedback import request_approval

decision = await request_approval(
    f"Assign {writer_type.name} for this topic?",
    ["Yes", "No, choose different writer"]
)
```

**Location**: `composable_app/utils/human_feedback.py`

---

## Data Models

### Article Fields

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `full_text` | `str` | Markdown content | "The Battle of the Bulge was..." |
| `title` | `str` | Article title | "The Battle of the Bulge" |
| `key_lesson` | `str` | One-sentence summary | "Last major German offensive" |
| `index_keywords` | `list[str]` | Search keywords | ["WWII", "Ardennes", "1944"] |

### Writer Types

| Writer | Content Type | Use Case | RAG Enabled |
|--------|-------------|----------|-------------|
| `HISTORIAN` | 2 paragraphs | Historical topics | No |
| `MATH_WRITER` | Detailed solution | Math problems | No |
| `GENAI_WRITER` | 2 paragraphs | GenAI topics | Yes (book) |
| `GENERALIST` | Short article | General topics | No |

### Reviewer Roles

| Role | Type | Focus | System Prompt |
|------|------|-------|---------------|
| Grammar Reviewer | Specialist | Grammar, clarity | `grammar_reviewer_system_prompt.j2` |
| Math Reviewer | Specialist | Mathematical accuracy | `math_reviewer_system_prompt.j2` |
| District Rep | Specialist | Curriculum alignment | `district_rep_system_prompt.j2` |
| Conservative Parent | Adversarial | Traditional values | `conservative_parent_system_prompt.j2` |
| Liberal Parent | Adversarial | Progressive values | `liberal_parent_system_prompt.j2` |
| School Admin | Adversarial | Practical concerns | `school_admin_system_prompt.j2` |

---

## Error Handling

### Common Exceptions

```python
# Input validation failure
InputGuardrailException
    Raised when: Input violates guardrail condition
    Catch in: Task assignment, user input processing

# Pydantic AI errors
ModelRetry
    Raised when: LLM response doesn't match output schema
    Handled by: retries=2 in agent configuration

# API errors
ValueError
    Raised when: Missing API key, invalid configuration
    Check: Environment variables in keys.env
```

### Error Recovery Patterns

```python
# Retry with exponential backoff
from pydantic_ai import Agent

agent = Agent(
    llms.DEFAULT_MODEL,
    retries=2,  # Automatic retry on failure
    model_settings=llms.default_model_settings()
)

# Graceful degradation
try:
    article = await writer.write_about(topic)
except Exception as e:
    logger.error(f"Failed to generate article: {e}")
    # Fallback to simpler writer or cached response
```

---

## Logging

### Log Files

| File | Content | Logger Name |
|------|---------|-------------|
| `logs/prompts.json` | All prompt I/O | `utils.prompt_service` |
| `logs/guards.json` | Guardrail decisions | `utils.guardrails` |
| `logs/evals.log` | Evaluation data | `utils.save_for_eval` |

### Log Format

```json
{
  "timestamp": "2024-01-15T10:30:45Z",
  "level": "INFO",
  "logger": "utils.prompt_service",
  "message": "Rendered prompt",
  "extra": {
    "prompt_name": "AbstractWriter_write_about",
    "topic": "Battle of the Bulge",
    "content_type": "2 paragraphs"
  }
}
```

### Configuration

Logging configured in `logging.json`. See `composable_app/logging.json` for details.

---

## Examples

### Complete Workflow Example

```python
from agents.task_assigner import TaskAssigner
from agents.generic_writer_agent import WriterFactory
from agents.reviewer_panel import ReviewerPanel

# 1. Assign writer
assigner = TaskAssigner()
writer_type = await assigner.assign_writer("Battle of the Bulge")

# 2. Create writer instance
writer = WriterFactory.create_writer(writer_type)

# 3. Generate initial draft
article = await writer.write_about("Battle of the Bulge")

# 4. Review article
panel = ReviewerPanel()
feedback = await panel.review_article(article)

# 5. Revise based on feedback
final_article = await writer.revise_article(
    "Battle of the Bulge",
    article,
    feedback
)

# 6. Output
print(final_article.to_markdown())
```

### RAG Query Example

```python
from agents.generic_writer_agent import GenAIWriter

writer = GenAIWriter()
article = await writer.write_about("What is prompt caching?")

# Article includes:
# - Content from book pages about prompt caching
# - Citations: "See pages: 142, 143, 147"
```

### Custom Guardrail Example

```python
from utils.guardrails import InputGuardrail

# Create domain-specific guardrail
medical_guardrail = InputGuardrail(
    name="medical_compliance",
    accept_condition="The query does not request medical diagnosis or treatment advice"
)

is_safe = await medical_guardrail.is_acceptable(user_query)
```

---

## Performance Considerations

### Latency Optimization
- **Parallel reviews**: ReviewerPanel uses `asyncio.gather()`
- **Small models for guardrails**: Uses `SMALL_MODEL` for fast validation
- **Prompt caching**: Template reuse reduces token processing

### Cost Optimization
- **Temperature 0.25**: Reduces retry frequency
- **Appropriate model selection**: Small models for simple tasks
- **Structured outputs**: Reduces parsing errors and retries

### Scalability
- **Stateless agents**: Each request is independent
- **Async throughout**: Non-blocking I/O operations
- **Cloud-ready**: Designed for serverless deployment

---

## See Also

- [ARCHITECTURE.md](ARCHITECTURE.md) - System design overview
- [README.md](README.md) - Setup and deployment
- [CONTRIBUTING.md](../CONTRIBUTING.md) - Development guidelines
- [Pydantic AI Documentation](https://ai.pydantic.dev)
- [LlamaIndex Documentation](https://docs.llamaindex.ai)
