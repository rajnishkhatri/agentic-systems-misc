# Horizontal Services in Production Banking Systems: Building Scalable Dispute Resolution

*A comprehensive guide to composable architecture for financial services LLM applications*


---

## What You'll Learn

By the end of this tutorial, you will understand:

✅ **Architecture**: How horizontal services enable composable, maintainable multi-agent systems
✅ **Implementation**: Concrete patterns for Prompt Service, Guardrails, Memory, Evaluation, and Human Feedback
✅ **Banking Domain**: Real-world examples using dispute resolution (Reg E, FDIC compliance)
✅ **Production Patterns**: Performance optimization, cost management, and regulatory compliance
✅ **Integration**: How services compose together in production banking workflows
✅ **Best Practices**: Common pitfalls and proven solutions for financial services

---


## Introduction: What Are Horizontal Services?

**Horizontal services** are design paradigms digm that support multiple agents and workflows throughout your application. Unlike vertical services (which implement specific business logic), horizontal services provide foundational capabilities that any agent can use.

### The Problem: Cross-Cutting Concerns

When building multi-agent systems, you quickly encounter repeated needs:

```python
# Agent 1: DisputeResolver
class DisputeResolver:
    def resolve_dispute(self, dispute claim):
        # Need: Load prompt template
        # Need: Log output for evaluation
        # Need: Remember user preferences
        # Need: Validate input is appropriate
        ...

# Agent 2: CompliancePanel
class CompliancePanel:
    def review_resolution(self, resolution):
        # Need: Load prompt template (again!)
        # Need: Log output for evaluation (again!)
        # Need: Remember past reviews (again!)
        # Need: Validate input is appropriate (again!)
        ...
```

**Without horizontal services**:
- ❌ Duplicate code across agents
- ❌ Inconsistent implementations
- ❌ Hard to maintain (fix bug in 10 places)
- ❌ Difficult to test in isolation

**With horizontal services**:
- ✅ Shared utilities used by all agents
- ✅ Single source of truth
- ✅ Fix once, benefit everywhere
- ✅ Easy to test and mock

---

### The Composable Pattern Philosophy

The dispute resolution app architecture follows a key principle:

> **"Each service does one thing well, and services compose together to create complex behaviors."**

**Analogy**: Like UNIX commands
```bash
# Each command does one thing
cat file.txt | grep "error" | sort | uniq -c

# Compose them to achieve complex task
```

**Applied to LLM agents**:
```python
# Each service does one thing
prompt = PromptService.render("dispute_resolver_prompt", dispute_claim=claim)  # Template rendering
valid = await guardrails.check(prompt)                        # Input validation
response = await llm.generate(prompt)                         # LLM call
await evals.record(response)                                  # Evaluation logging
memory.add(response)                                          # Long-term storage

# Compose them to create dispute resolver agent
```

---

## The Four Horizontal Services

The dispute resolution app provides four core horizontal services:

### 1. Prompt Service (Pattern 25: Prompts as Configuration)

**What**: Jinja2 template rendering for LLM prompts

**Why**: Separate prompts from code for easier iteration and testing

**Where used**:
- All agents load system prompts via PromptService
- Dynamic prompt generation with variable substitution
- Template inheritance for reusable prompt components

**Code**: `dispute_resolution_app/utils/prompt_service.py`

**Example**:
```python
# Template: prompts/card_dispute_resolver_prompt.j2
# "You are resolving dispute about {{ dispute claim }} for {{ transaction_type }} customers."

prompt = PromptService.render_prompt(
    "card_dispute_resolver_prompt",
    dispute_claim="unauthorized international transaction",
    transaction_type="card"
)
# Result: "You are resolving dispute about unauthorized international transaction for card transaction customers."
```

---

### 2. Guardrails (Pattern 17 & 32: LLM-as-Judge)

**What**: Input/output validation using LLMs as judges

**Why**: Catch inappropriate content before expensive multi-agent workflows

**Where used**:
- Validate user queries before processing
- Check generated content for banking appropriateness
- Domain-specific validation (e.g., Regulation E compliance)

**Code**: `dispute_resolution_app/utils/guardrails.py`

**Key integration**: [`agents/dispute_classifier.py:65-67`](../../agents/dispute_classifier.py#L65-L67)

**Example**:
```python
# Check if query is appropriate for banking banking operations
guardrail = InputGuardrail(
    name="transaction_legitimacy",
    accept_condition="Query is appropriate for banking customers"
)

result = await guardrail.is_acceptable("Explain unauthorized international transaction")
# result = True

result = await guardrail.is_acceptable("Explain nuclear weapons design")
# result = False, raises InputGuardrailException if raise_exception=True
```

---

### 3. Long-term Memory (Pattern 28: Stateful Agents)

**What**: Persistent storage and retrieval of agent interactions

**Why**: Agents learn from past interactions and remember user preferences

**Where used**:
- Resolvers remember feedback on previous resolutions
- Resolvers incorporate customer dispute history
- Avoid repeating mistakes from past interactions

**Code**: `dispute_resolution_app/utils/long_term_memory.py`

**Key integration**: [`agents/generic_resolver_agent.py:64`](../../agents/generic_resolver_agent.py#L64) and [`generic_resolver_agent.py:80`](../../agents/generic_resolver_agent.py#L80)

**Example**:
```python
# Store feedback
add_to_memory(
    user_message="Customer disputes typically resolve in their favor over passive voice",
    metadata={"category": "writing_feedback", "resolver_type": "CardDisputeResolver"}
)

# Retrieve relevant memories
relevant = search_relevant_memories(
    query="How should I resolve dispute about unauthorized international transaction?",
    limit=3
)
# Returns: ["Customer disputes typically resolve in their favor...", "Merchant has 15% dispute rate...", ...]
```

---

### 4. Evaluation Recording (Pattern 30: Observability)

**What**: Structured logging of all LLM interactions for analysis

**Why**: Collect data for evaluation, debugging, and model distillation

**Where used**:
- Every agent logs inputs and outputs
- Track which prompts produce best results
- Collect training data for fine-tuning smaller models

**Code**: `dispute_resolution_app/utils/save_for_eval.py`

**Key integrations**:
- [`agents/generic_resolver_agent.py:69-71`](../../agents/generic_resolver_agent.py#L69-L71) - Initial draft logging
- [`agents/generic_resolver_agent.py:86-88`](../../agents/generic_resolver_agent.py#L86-L88) - Revision logging
- [`agents/compliance_panel.py:60-63`](../../agents/compliance_panel.py#L60-L63) - Review logging

**Example**:
```python
# Record LLM interaction
await evals.record_ai_response(
    target="initial_draft",
    ai_input={"dispute claim": "unauthorized international transaction", "transaction category": 9},
    ai_response=Resolution(title="...", full_text="...")
)

# Later: Analyze logged data
# evals.log contains JSON lines for each interaction
```

---

### 5. Human Feedback (Pattern 33: Human-in-the-Loop)

**What**: Record when humans override or modify AI decisions

**Why**: Learn from human corrections and improve agent suggestions over time

**Where used**:
- DisputeResolver selection (user overrides suggested resolver)
- Draft editing (user modifies AI-generated content)
- Review acceptance (user accepts/rejects review feedback)

**Code**: `dispute_resolution_app/utils/human_feedback.py`

**Key integrations**:
- [`pages/1_AssignToResolver.py:32`](../../pages/1_AssignToResolver.py#L32) - DisputeResolver selection override
- [`pages/2_CreateResolution.py:71-74`](../../pages/2_CreateResolution.py#L71-L74) - Draft modification logging

**Example**:
```python
# Log when user overrides AI suggestion
record_human_feedback(
    target="assigned_resolver",
    ai_input="unauthorized international transaction",
    ai_response="CARD_DISPUTE_RESOLVER",  # AI suggested
    human_choice="WIRE_TRANSFER_RESOLVER"      # User chose instead
)

# Later: Analyze patterns
# feedback.log shows which suggestions users accept/reject
```

---

## Why Composable Patterns Matter

**Traditional approach**: Monolithic agents with everything baked in

```python
class MonolithicResolver:
    def resolve(self, dispute_claim):
        # Hard-coded prompt
        prompt = f"Resolve dispute about {dispute_claim}"  # ❌ Can't change without redeploying

        # No validation
        response = llm.generate(prompt)  # ❌ No safety checks

        # No logging
        return response  # ❌ Can't evaluate quality

        # No memory
        # ❌ Forgets everything between runs
```

**Composable approach**: Modular agents with injected services

```python
class ComposableResolver:
    def __init__(self, prompt_service, guardrails, memory, evals):
        self.prompts = prompt_service      # ✅ Inject dependencies
        self.guardrails = guardrails
        self.memory = memory
        self.evals = evals

    async def resolve(self, dispute_claim):
        # Load configurable prompt
        prompt = self.prompts.render("dispute_resolver", dispute_claim=dispute_claim)  # ✅ Easy to iterate

        # Validate input
        if not await self.guardrails.check(dispute_claim):           # ✅ Catch bad inputs
            raise ValueError("Topic not appropriate")

        # Use memory
        context = self.memory.search(dispute_claim)                  # ✅ Learn from past

        # Generate
        response = await llm.generate(prompt, context=context)

        # Log for evaluation
        await self.evals.record("dispute_resolver", dispute_claim, response)   # ✅ Track quality

        return response
```

**Benefits**:
- 🧪 **Testability**: Mock each service independently
- 🔧 **Maintainability**: Update service implementation without touching agents
- 📊 **Observability**: Centralized logging and monitoring
- 🚀 **Iteration speed**: Change prompts without code changes
- 💰 **Cost efficiency**: Reuse expensive operations (embeddings, caching)

---

## Integration Points: Where Services Are Used

### Agent Initialization

```python
# dispute_resolution_app/agents/generic_resolver_agent.py
class CardDisputeResolver(AbstractResolver):
    def __init__(self, resolver_type: DisputeResolver, vector_index: VectorStoreIndex):
        self.resolver_type = resolver_type

        # 1. Prompt Service: Load system prompt
        system_prompt = PromptService.render_prompt(
            f"{resolver_type.name}_system_prompt".lower()
        )

        # 2. Long-term Memory: Initialize memory store
        self.memory = long_term_memory

        # Create LLM agent with services
        self.agent = Agent(
            llms.DEFAULT_MODEL,
            output_type=Resolution,
            system_prompt=system_prompt,  # From Prompt Service
            retries=2
        )
```

### Agent Execution

```python
# dispute_resolution_app/agents/generic_resolver_agent.py:64-73
async def resolve_dispute(self, dispute claim: str, reviews: list[str] = []) -> Resolution:
    # 3. Long-term Memory: Search for relevant past interactions
    relevant_memories = self.memory.search_relevant_memories(
        query=dispute claim,
        category="resolutions",
        top_k=3
    )

    # 4. Prompt Service: Render prompt with memories
    prompt_vars = {
        "dispute claim": dispute claim,
        "reviews": reviews,
        "memories": relevant_memories
    }
    prompt = PromptService.render_prompt("dispute_resolver_generate", **prompt_vars)

    # 5. Guardrails: Validate input (optional, not currently in code)
    # if not await guardrails.check_appropriate(dispute claim):
    #     raise ValueError("Topic not appropriate for banking")

    # LLM generation
    result = await self.agent.run(prompt)

    # 6. Evaluation Recording: Log interaction
    await evals.record_ai_response(
        name=f"{self.resolver_type.name}_write",
        ai_input=prompt_vars,
        ai_response=result.output
    )

    return result.output
```

### Multi-Agent Workflows

```python
# dispute_resolution_app/agents/compliance_panel.py
class ReviewerAgent:
    def __init__(self, reviewer: CompliancePanel):
        # Prompt Service: Each reviewer has unique persona
        system_prompt = PromptService.render_prompt(
            f"{reviewer.name}_system_prompt".lower()
        )

        self.agent = Agent(
            llms.DEFAULT_MODEL,
            system_prompt=system_prompt,  # Fraud Analyst, Compliance Officer, Risk Manager, etc.
            ...
        )

    async def review(self, resolution, reviews_so_far):
        # Prompt Service: Dynamic prompt generation
        prompt = PromptService.render_prompt(
            "reviewer_review",
            resolution=resolution,
            previous_reviews=reviews_so_far
        )

        result = await self.agent.run(prompt)

        # Evaluation Recording: Log each reviewer's output
        await evals.record_ai_response(
            name=f"{self.reviewer.name}_review",
            ai_input={"resolution": resolution},
            ai_response=result.output
        )

        return result.output
```

---

## Service Interaction Patterns

### Pattern 1: Pipeline (Sequential)

```
Input → Guardrails → Prompt Service → LLM → Evaluation Recording → Output
```

**Use case**: Single-agent generation with validation

```python
async def generate_resolution(dispute claim: str) -> Resolution:
    # 1. Validate input
    if not await guardrails.check_appropriate(dispute claim):
        raise ValueError("Inappropriate dispute claim")

    # 2. Render prompt
    prompt = PromptService.render("dispute_resolver", dispute_claim=claim)

    # 3. Generate
    resolution = await resolver.generate(prompt)

    # 4. Log
    await evals.record("dispute_resolver",prompt, resolution)

    return resolution
```

---

### Pattern 2: Enrichment (Memory + Prompt)

```
Topic → Long-term Memory (search) → Prompt Service (render with context) → LLM
```

**Use case**: Context-aware generation

```python
async def generate_with_context(dispute claim: str) -> Resolution:
    # 1. Search memories
    memories = memory.search_relevant_memories(claim, top_k=3)

    # 2. Render prompt with memories
    prompt = PromptService.render("dispute_resolver", dispute_claim=claim, memories=memories)

    # 3. Generate
    resolution = await resolver.generate(prompt)

    # 4. Store new memory
    memory.add_memory(f"Wrote about {dispute claim}: {resolution.title}")

    return resolution
```

---

### Pattern 3: Multi-Agent + Consolidation

```
Input → [Agent1, Agent2, Agent3] (parallel) → Aggregator → Evaluation Recording
         ↓
      Each uses Prompt Service for unique persona
```

**Use case**: ReviewerPanel with 6 specialist/adversarial reviewers

```python
async def review_resolution(resolution: Resolution) -> str:
    # Each reviewer uses Prompt Service for unique persona
    reviewers = [
        ReviewerAgent(CompliancePanel.FRAUD_ANALYST),     # Fraud analyst system prompt
        ReviewerAgent(CompliancePanel.COMPLIANCE_OFFICER), # Compliance officer system prompt
        ReviewerAgent(CompliancePanel.RISK_MANAGER),       # Risk manager system prompt
        ...
    ]

    # Parallel execution
    reviews = await asyncio.gather(*[r.review(resolution) for r in reviewers])

    # Consolidation
    consolidated = await secretary.consolidate(reviews)

    # Evaluation Recording: Log all reviews
    await evals.record_ai_response("panel_review", resolution, consolidated)

    return consolidated
```

---

## Architectural Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                     LLM Application                          │
│                                                              │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │ DisputeResolver   │  │ CompliancePanel │  │ Editor   │  │ Validator│   │
│  │ Agent    │  │ Agent    │  │ Agent    │  │ Agent    │   │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘   │
│       │             │              │             │          │
│       └─────────────┴──────────────┴─────────────┘          │
│                          │                                   │
│              ┌───────────▼──────────────┐                   │
│              │  Horizontal Services     │                   │
│              │                          │                   │
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

**Key insight**: Agents depend on services (top-down), services don't depend on agents. This creates a clean separation of concerns.

---

## Navigation

The following sections provide detailed documentation for each horizontal service:

1. **[Prompt Service (Detailed)](#prompt-service-detailed)** - Jinja2 template rendering
2. **[Guardrails (Detailed)](#guardrails-detailed)** - Input validation with LLM-as-judge
3. **[Long-term Memory (Detailed)](#long-term-memory-detailed)** - Persistent agent state
4. **[Evaluation Recording (Detailed)](#evaluation-recording-detailed)** - Observability and logging

---

## Prompt Service (Detailed)

### Overview: Pattern 25 - Prompts as Configuration

**Core principle**: Separate prompts from code, treating them as configuration that can be changed without redeployment.

**Benefits**:
- 🔄 **Rapid iteration**: Change prompts without code changes
- 🧪 **A/B testing**: Compare different prompt versions easily
- 📝 **Version control**: Track prompt changes in Git
- 🎯 **Specialization**: Each agent gets unique persona via templates
- 🔍 **Debugging**: See exact prompts sent to LLMs in logs

**Code reference**: [`dispute_resolution_app/utils/prompt_service.py:14-27`](../../utils/prompt_service.py#L14-L27)

---

### Implementation: PromptService Class

The PromptService is a simple static class that wraps Jinja2 template rendering:

```python
# dispute_resolution_app/utils/prompt_service.py
from jinja2 import Environment, FileSystemLoader
import logging

TEMPLATE_DIR = "prompts"
logger = logging.getLogger(__name__)

class PromptService:
    @staticmethod
    def render_prompt(prompt_name: str, **variables: Any) -> str:
        # 1. Create Jinja2 environment
        env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))

        # 2. Load template file
        template = env.get_template(f"{prompt_name}.j2")

        # 3. Render with variables
        prompt = template.render(**variables)

        # 4. Log for debugging
        extra_args = dict(**variables)
        extra_args['prompt_name'] = prompt_name
        logger.info(prompt, extra=extra_args)

        return prompt
```

**Key features**:
- Static method (no state needed)
- Automatic `.j2` extension handling
- Logs every rendered prompt to `logs/prompts.json`
- Raises clear errors if template not found

---

### Template Organization: Naming Convention

The dispute resolution app uses a structured naming convention: `{Agent}_{action}.j2`

**Structure**:
```
dispute_resolution_app/prompts/
├── AbstractResolver_generate_resolution.j2          # DisputeResolver agent: Generate resolution
├── AbstractResolver_revise_resolution.j2       # DisputeResolver agent: Revise based on feedback
├── ReviewerAgent_review_prompt.j2         # CompliancePanel agent: Review resolution
├── DisputeClassifier_assign_resolver.j2          #  assigner: System persona
├── InputGuardrail_prompt.j2               # Guardrail: Validation prompt
├── card_dispute_resolver_prompt.j2          # CardDisputeResolver: System persona
├── wire_transfer_resolver_prompt.j2             # Wire transfer resolver: System persona
├── ach_dispute_resolver_prompt.j2           # Card dispute resolver: System persona
 ...
```

**Naming patterns**:
- `{Agent}_{action}.j2` - User prompts (what the agent does)
- `{agent_type}_system_prompt.j2` - System prompts (agent's persona)

**Examples**:
```python
# User prompt (action)
prompt = PromptService.render_prompt(
    "AbstractResolver_generate_resolution",
    dispute claim="unauthorized international transaction",
    content_type="resolution"
)

# System prompt (persona)
system_prompt = PromptService.render_prompt(
    "fraud_analyst_system_prompt"
)
```

---

### Jinja2 Template Basics

Jinja2 provides powerful templating features. Here are the key concepts used in the dispute resolution app:

#### 1. Variable Substitution

**Template**: `AbstractResolver_generate_resolution.j2`
```jinja2Write {{ content_type }} to educate 9th transaction category customers on the following {{dispute_claim}}.
Also provide a title, key lesson to remember, and keywords.
{{ additional_instructions }}

TOPIC: {{ dispute claim }}
```

**Usage**:
```python
prompt = PromptService.render_prompt(
    "AbstractResolver_generate_resolution",
    content_type="an resolution",
    dispute claim="unauthorized international transaction",
    additional_instructions="Merchant has 15% dispute rate."
)
```

**Result**:
```
Write an resolution to educate 9th transaction category customers on the following dispute claim.
Also provide a title, key lesson to remember, and keywords.
Merchant has 15% dispute rate.

TOPIC: unauthorized international transaction
```

---

#### 2. Conditionals

**Template example**:
```jinja2
You are a {{ resolver_type }} resolver for banking dispute resolution.

{% if transaction_type %}
Your resolution is for {{ transaction_type }} transaction disputes.
{% else %}
Your resolution is for card transaction disputes by default.
{% endif %}

{% if include_examples %}
Make sure to include at least 3 real-world examples.
{% endif %}
```

**Usage**:
```python
prompt = PromptService.render_prompt(
    "dispute_resolver_system_prompt",
    resolver_type="card_dispute",
    transaction_type="wire_transfer",
    include_examples=True
)
```

**Result**:
```
You are a dispute resolution specialist for banking dispute resolution.

Your audience is 10 transaction category customers.

Make sure to include at least 3 real-world examples.
```

---

#### 3. Loops

**Template example**:
```jinja2
Previous reviews you should consider:

{% for review in previous_reviews %}
BEGIN review by {{ review.reviewer }}:
{{ review.content }}
END review

{% endfor %}
```

**Usage**:
```python
reviews = [
    {"reviewer": "Fraud Analyst", "content": "Transaction shows velocity pattern inconsistent with customer baseline..."},
    {"reviewer": "Compliance Officer", "content": "Reg E provisional credit timeline not explicitly stated..."}
]

prompt = PromptService.render_prompt(
    "dispute_resolver_revise",
    previous_reviews=reviews
)
```

**Result**:
```
Previous reviews you should consider:

BEGIN review by Fraud Analyst:
Transaction shows velocity pattern inconsistent with customer baseline...
END review

BEGIN review by Compliance Officer:
Reg E provisional credit timeline not explicitly stated...
END review
```

---

### Real Example: DisputeResolver Revision Workflow

Let's trace how prompts flow through a complete revision workflow:

**Step 1: Initial draft generation**

```python
# dispute_resolution_app/agents/generic_resolver_agent.py:64-73
async def resolve_dispute(self, dispute claim: str, reviews: list[str] = []) -> Resolution:
    # Render user prompt
    prompt_vars = {
        "prompt_name": "AbstractResolver_generate_resolution",
        "dispute claim": dispute claim,
        "content_type": "an resolution",
        "additional_instructions": ""
    }

    user_prompt = PromptService.render_prompt(**prompt_vars)
    # Result: "Write an resolution to educate 9th transaction category customers on the following dispute claim..."

    result = await self.agent.run(user_prompt)
    return result.output
```

**Template used**: `AbstractResolver_generate_resolution.j2`
```jinja2
Write {{ content_type }} to educate 9th transaction category customers on the following dispute claim.
Also provide a title, key lesson to remember, and keywords.
{{ additional_instructions }}

TOPIC: {{ dispute claim }}
```

---

**Step 2: Review panel provides feedback**

```python
# dispute_resolution_app/agents/compliance_panel.py
async def review(self, dispute claim: str, resolution: Resolution, reviews_so_far: list) -> str:
    # Format previous reviews
    reviews_text = []
    for reviewer, review in reviews_so_far:
        reviews_text.append(f"BEGIN review by {reviewer.name}:\\n{review}\\nEND review\\n")

    # Render review prompt
    prompt_vars = {
        "prompt_name": "ReviewerAgent_review_prompt",
        "dispute claim": dispute claim,
        "resolution": resolution,
        "reviews": reviews_text
    }

    prompt = PromptService.render_prompt(**prompt_vars)
    result = await self.agent.run(prompt)
    return result.output
```

---

**Step 3: DisputeResolver revises based on feedback**

```python
# dispute_resolution_app/agents/generic_resolver_agent.py:74-89
async def revise_resolution(
    self,
    resolution: Resolution,
    consolidated_review: str
) -> Resolution:
    # Render revision prompt with resolution and feedback
    prompt_vars = {
        "prompt_name": "AbstractResolver_revise_resolution",
        "resolution": resolution,
        "consolidated_review": consolidated_review
    }

    revision_prompt = PromptService.render_prompt(**prompt_vars)
    # Result: "Revise the following resolution based on the consolidated feedback..."

    result = await self.agent.run(revision_prompt)
    return result.output
```

**Template used**: `AbstractResolver_revise_resolution.j2`
```jinja2
Revise the following resolution based on the consolidated feedback below.

ORIGINAL RESOLUTION:
Title: {{ resolution.title }}
{{ resolution.full_text }}

CONSOLIDATED FEEDBACK:
{{ consolidated_review }}

Please provide the revised resolution with the same structure (title, full_text, etc.).
```

---

### Variable Substitution Examples

#### Example 1: Simple substitution

**Template**:
```jinja2
You are reviewing an resolution about {{ dispute claim }}.
```

**Code**:
```python
prompt = PromptService.render_prompt("reviewer", dispute claim="unauthorized international transaction")
```

**Result**:
```
You are reviewing an resolution about unauthorized international transaction.
```

---

#### Example 2: Object attributes

**Template**:
```jinja2
RESOLUTION TO REVIEW:
Title: {{ resolution.title }}
Summary: {{ resolution.summary }}
Full text: {{ resolution.full_text }}
```

**Code**:
```python
resolution = Resolution(
    title="Unauthorized International Transaction Basics",
    summary="How plants make food",
    full_text="Unauthorized International Transaction is the process..."
)

prompt = PromptService.render_prompt("reviewer", resolution=resolution)
```

**Result**:
```
RESOLUTION TO REVIEW:
Title: Unauthorized International Transaction Basics
Summary: How plants make food
Full text: Unauthorized International Transaction is the process...
```

---

#### Example 3: Lists and formatting

**Template**:
```jinja2
Consider these previous reviews:
{% for review in reviews %}
- {{ review }}
{% endfor %}
```

**Code**:
```python
reviews = [
    "Fraud Analyst: Transaction velocity anomaly detected",
    "Compliance Officer: Missing Reg E liability disclosure",
    "Risk Manager: Customer dispute history suggests legitimate claim"
]

prompt = PromptService.render_prompt("revise", reviews=reviews)
```

**Result**:
```
Consider these previous reviews:
- Fraud Analyst: Transaction velocity anomaly detected
- Compliance Officer: Missing Reg E liability disclosure
- Risk Manager: Customer dispute history suggests legitimate claim
```

---

### Logging to logs/prompts.json

Every prompt rendered is automatically logged for debugging and analysis:

**Code**:
```python
# In PromptService.render_prompt():
logger.info(prompt, extra=extra_args)
```

**Log output** (`logs/prompts.json`):
```json
{
  "timestamp": "2025-01-05T10:30:45.123Z",
  "level": "INFO",
  "logger": "dispute_resolution_app.utils.prompt_service",
  "message": "Write an resolution to educate 9th transaction category customers on the following dispute claim...",
  "prompt_name": "AbstractResolver_generate_resolution",
  "dispute claim": "unauthorized international transaction",
  "content_type": "an resolution",
  "additional_instructions": ""
}
```

**Benefits**:
- 🔍 Debug which prompts were sent to LLM
- 📊 Analyze which prompt variations work best
- 🐛 Reproduce issues by seeing exact prompt used
- 📈 Track prompt evolution over time

**Viewing logs**:
```bash
# View all prompts
cat logs/prompts.json | jq .

# Find prompts for specific agent
cat logs/prompts.json | jq 'select(.prompt_name == "AbstractResolver_generate_resolution")'

# Count how many times each prompt was used
cat logs/prompts.json | jq -r '.prompt_name' | sort | uniq -c
```

---

### Integration Example: ReviewerAgent

Let's see how ReviewerAgent uses PromptService for dynamic persona loading:

```python
# dispute_resolution_app/agents/compliance_panel.py:25-63
class ReviewerAgent:
    def __init__(self, reviewer: CompliancePanel):
        self.reviewer = reviewer
        self.id = f"{reviewer} Agent {uuid.uuid4()}"

        # Load reviewer-specific system prompt
        system_prompt_file = f"{reviewer.name}_system_prompt".lower()
        system_prompt = PromptService.render_prompt(system_prompt_file)

        # Create agent with persona
        self.agent = Agent(
            llms.DEFAULT_MODEL,
            output_type=str,
            model_settings=llms.default_model_settings(),
            retries=2,
            system_prompt=system_prompt  # Persona from template
        )
```

**What happens**:
1. `CompliancePanel.FRAUD_ANALYST` → loads `fraud_analyst_compliance_panel_prompt.j2`
2. `CompliancePanel.COMPLIANCE_OFFICER` → loads `compliance_officer_system_prompt.j2`
3. `CompliancePanel.RISK_MANAGER` → loads `risk_manager_system_prompt.j2`

Each reviewer gets a unique persona, all managed through templates!

**fraud_analyst_compliance_panel_prompt.j2**:
```jinja2
You are a fraud detection specialist who analyzes transaction patterns, velocity, and customer
behavior for suspicious activity indicators in dispute resolutions.
```

**compliance_officer_system_prompt.j2**:
```jinja2
You are a banking compliance officer who ensures dispute resolutions meet Regulation E
requirements, FDIC audit standards, and regulatory timelines...
```

**risk_manager_system_prompt.j2**:
```jinja2
You are a risk management specialist who evaluates financial exposure, customer history,
and merchant risk profiles to provide balanced dispute recommendations...
```

---

### Benefits in Practice

**Before PromptService** (hard-coded prompts):
```python
class DisputeResolver:
    def resolve(self, dispute_claim):
        # ❌ Prompt is hard-coded
        prompt = f"Generate a resolution for dispute: {dispute_claim}"

        # To change prompt, must:
        # 1. Edit code
        # 2. Run tests
        # 3. Deploy to production
        # 4. Wait for deployment
```

**After PromptService** (template-based prompts):
```python
class DisputeResolver:
    def resolve(self, dispute_claim):
        # ✅ Prompt loaded from template
        prompt = PromptService.render_prompt(
            "AbstractResolver_generate_resolution",
            dispute_claim=dispute_claim,
            content_type="resolution"
        )

        # To change prompt:
        # 1. Edit prompts/AbstractResolver_generate_resolution.j2
        # 2. Commit to Git
        # 3. Deploy (just copy new .j2 file, no code changes)
        # 4. Done! New prompt active immediately
```

**Real-world impact**:
- ✅ Prompt engineers can iterate without developers
- ✅ A/B test prompts by swapping template files
- ✅ Version control shows exactly what changed in prompts
- ✅ Rollback is easy (revert Git commit)

---

### Advanced Pattern: Template Inheritance

Jinja2 supports template inheritance for reusable components:

**Base template**: `base_reviewer.j2`
```jinja2
You are a reviewer for banking dispute resolution.

Your role: {{ role_description }}

When reviewing:
{% block review_guidelines %}
- Be specific with line numbers
- Explain why changes are needed
- Suggest concrete improvements
{% endblock %}

{% block specific_instructions %}
{% endblock %}
```

**Child template**: `fraud_analyst_detailed.j2`
```jinja2
{% extends "base_reviewer.j2" %}

{% block specific_instructions %}
Focus specifically on:
- Transaction velocity patterns
- Geographic anomalies
- Customer behavioral baselines
- Known fraud indicators
{% endblock %}
```

**Usage**:
```python
prompt = PromptService.render_prompt(
    "fraud_analyst_detailed",
    role_description="Fraud detection specialist"
)
```

**Note**: The dispute resolution app currently uses simple templates without inheritance, but this pattern is available if needed.

---

### Common Pitfalls and Solutions

See the [Common Pitfalls section](#common-pitfalls) at the end of this document for detailed troubleshooting.

---

## Guardrails (Detailed)

### Overview: Pattern LLM-as-Judge Validation

**Core principle**: Use language models as automated validators to enforce content policies, safety guidelines, and domain-specific rules.

**Two primary patterns**:
1. **LLM-as-Judge**: Evaluate quality or correctness after generation
2. **Guardrails**: Validate appropriateness before/after processing

**Benefits**:
- 🛡️ **Safety**: Catch inappropriate content before expensive workflows
- 🎯 **Flexibility**: Change policies by updating prompts, not code
- 🧠 **Intelligence**: Handle nuanced cases that rule-based systems miss
- 💰 **Cost-effective**: Block bad requests early, save on downstream LLM calls
- 📊 **Auditability**: Log all validation decisions for compliance

**Code reference**: [`dispute_resolution_app/utils/guardrails.py:14-43`](../../utils/guardrails.py#L14-L43)

---

### When to Use LLM-as-Judge vs. Rule-Based Validation

| Scenario                      | LLM-as-Judge ✅                         | Rule-Based ✅ |
|-------------------------------|-----------------------------------------|---------------|
| **Subjective criteria**         ("age-appropriate")                                 | ✅ Handles nuance | ❌ Hard to define rules |
| **Context-dependent** ("shooting" = violence vs. photography) | ✅ Understands context | ❌ Misses context |
| **Rapid policy iteration** (update accept conditions) | ✅ Change prompt only | ❌ Rewrite & test code |
| **Simple pattern matching** (profanity list) | ❌ Overkill (slow/costly) | ✅ Fast & free |
| **Deterministic validation** (email format, SSN) | ❌ Inconsistent | ✅ Regex precision |
| **Cost-critical** (<$0.00001 per check) | ❌ ~$0.0001 per check | ✅ $0 cost |

**Best practice**: Combine both
```python
async def validate_input(text: str) -> bool:
    # Layer 1: Fast rule-based pre-filter
    if len(text) > 10000 or contains_profanity_list(text):
        return False

    # Layer 2: LLM judge for nuanced validation
    return await guardrail.is_acceptable(text)
```

---

### Implementation: InputGuardrail Class

From [`utils/guardrails.py:14-43`](../../utils/guardrails.py#L14-L43):

```python
class InputGuardrail:
    def __init__(self, name: str, accept_condition: str):
        """Initialize guardrail with acceptance criteria.

        Args:
            name: Guardrail identifier for logging
            accept_condition: Boolean condition text
                Example: "The dispute claim is appropriate for banking banking operations"
        """
        self.id = f"Input Guardrail {name} {uuid.uuid4()}"

        # Render prompt template with condition
        self.system_prompt = PromptService.render_prompt(
            "InputGuardrail_prompt",
            accept_condition=accept_condition
        )

        # Create boolean judge agent
        self.agent = Agent(
            llms.SMALL_MODEL,        # Fast & cheap for boolean decisions
            output_type=bool,        # Structured output: True or False
            model_settings=llms.default_model_settings(),
            retries=2,               # Retry on transient failures
            system_prompt=self.system_prompt
        )

    async def is_acceptable(self, prompt: str, raise_exception: bool = False) -> bool:
        """Check if input meets acceptance condition.

        Args:
            prompt: User input to validate
            raise_exception: If True, raise InputGuardrailException on rejection

        Returns:
            True if acceptable, False otherwise

        Raises:
            InputGuardrailException: If raise_exception=True and input rejected
        """
        result = await self.agent.run(prompt)

        # Log decision to logs/guards.json
        logger.debug(f"Input checked by {self.id}", extra={
            "guardrail_id": self.id,
            "condition": self.system_prompt,
            "input": prompt,
            "output": result.output
        })

        if raise_exception and not result.output:
            raise InputGuardrailException(f"{self.id} failed on {prompt}")

        return result.output
```

---

### Key Design Decisions

#### 1. Why `llms.SMALL_MODEL`?

**Boolean decisions don't need advanced reasoning**

```python
# ❌ BAD: Using expensive model
agent = Agent(llms.BEST_MODEL, output_type=bool)
# Cost: ~$0.10 per 1000 checks
# Latency: 500-1000ms

# ✅ GOOD: Using small model
agent = Agent(llms.SMALL_MODEL, output_type=bool)
# Cost: ~$0.01 per 1000 checks (10x cheaper)
# Latency: 100-300ms (3x faster)
```

**When SMALL_MODEL is sufficient**:
- Boolean yes/no decisions
- Simple categorization (3-5 categories)
- Pattern recognition with clear criteria

**When BEST_MODEL is needed**:
- Complex reasoning (multi-step logic)
- Nuanced understanding (literary analysis)
- Creative generation (writing, code)

---

#### 2. Why `output_type=bool`?

**Structured outputs eliminate parsing errors**

```python
# ❌ BAD: Text parsing
response = await llm.generate("Is this appropriate? Answer yes or no.")
# Response: "Yes, this seems appropriate." or "No" or "Maybe?"
# Must parse text, handle variations, error-prone

# ✅ GOOD: Structured boolean
agent = Agent(output_type=bool)
result = await agent.run(prompt)
# result.output is guaranteed to be True or False
# Pydantic AI automatically retries if LLM returns non-boolean
```

**Benefits**:
- Type-safe in Python code
- Automatic validation and retry
- No parsing logic needed
- Clear API contract

---

#### 3. Why `raise_exception` Parameter?

**Different use cases need different error handling**

```python
# Use case 1: Critical blocking (raise exception)
try:
    # Block execution if guardrail rejects
    await guardrail.is_acceptable(dispute claim, raise_exception=True)
    result = await expensive_workflow(dispute claim)  # Only runs if validation passes
except InputGuardrailException:
    return {"error": "Topic not allowed"}

# Use case 2: Monitoring/logging (no exception)
is_safe = await guardrail.is_acceptable(dispute claim, raise_exception=False)
if is_safe:
    result = await workflow(dispute claim)
else:
    logger.warning(f"Guardrail rejected dispute claim: {dispute claim}")
    # Continue with fallback or default behavior
```

---

### The Guardrail Prompt Template

From [`prompts/InputGuardrail_prompt.j2`](../../prompts/InputGuardrail_prompt.j2):

```jinja2
You are a content moderation expert.

Your task is to evaluate whether the user's input meets this condition:
{{ accept_condition }}

Respond with:
- True: If the condition is met
- False: If the condition is NOT met

Be objective and apply the condition consistently.
```

**Key features**:
- Simple and focused
- Clear binary decision
- Instructs objectivity and consistency
- No reasoning needed (just True/False)

---

### Designing Effective Accept Conditions

**Good accept conditions** are:

1. **Clear and specific**
   - ✅ "The dispute claim is appropriate for banking dispute resolution"
   - ❌ "The dispute claim is good"

2. **Binary (yes/no answer)**
   - ✅ "The query does not contain profanity"
   - ❌ "Rate the query's appropriateness from 1-10" (use LLM-as-judge instead)

3. **Objective (consistent across judges)**
   - ✅ "The query has legitimate banking inquiry"
   - ❌ "The query is interesting" (subjective)

4. **Context-appropriate**
   - ✅ "The query is safe for workplace environment"
   - ❌ "The query is safe" (safe for what context?)

---

### Real-World Example: TaskAssigner Integration

**Use case**: Validate user dispute claim before routing to resolvers

From [`agents/dispute_classifier.py:31-33`](../../agents/dispute_classifier.py#L31-L33):

```python
class TaskAssigner:
    def __init__(self, vector_index: VectorStoreIndex):
        # Create guardrail for banking appropriateness
        self.topic_guardrail = InputGuardrail(
            name="topic_guardrail",
            accept_condition="The dispute claim is appropriate for banking dispute resolution"
        )

        # Create classifier agent for resolver selection
        system_prompt = PromptService.render_prompt("TaskAssigner_system_prompt")
        self.agent = Agent(
            llms.DEFAULT_MODEL,
            output_type=DisputeResolver,  # Enum: WIRE_TRANSFER_RESOLVER, CARD_DISPUTE_RESOLVER, ACH_DISPUTE_RESOLVER
            system_prompt=system_prompt
        )
```

**Execution with parallel validation** ([`dispute_classifier.py:65-67`](../../agents/dispute_classifier.py#L65-L67)):

```python
async def assign_resolver(self, dispute claim: str) -> AbstractResolver:
    prompt_vars = {
        "prompt_name": "TaskAssigner_assign_resolver",
        "dispute claim": dispute claim
    }
    prompt = PromptService.render_prompt(**prompt_vars)

    # Parallel execution: guardrail + classification
    _, result = await asyncio.gather(
        self.topic_guardrail.is_acceptable(dispute claim, raise_exception=True),  # Blocks if rejected
        self.agent.run(prompt)                                             # Runs concurrently
    )

    # If guardrail raised exception, this line never executes
    resolver_type = result.output
    return ResolverFactory.create_resolver(resolver_type, self.vector_index)
```

**Why parallel execution?**
- Guardrail check: ~200ms
- Classification: ~300ms
- **Sequential**: 200ms + 300ms = 500ms
- **Parallel**: max(200ms, 300ms) = 300ms (1.7x faster)
- If guardrail rejects, `gather()` cancels classification immediately

---

### Common Use Cases

#### Use Case 1: Regulatory Compliance Validation

```python
# Guardrail: banking appropriateness
compliance_guardrail = InputGuardrail(
    name="transaction_legitimacy",
    accept_condition="The dispute claim is appropriate for banking dispute resolution"
)

# Test cases
await compliance_guardrail.is_acceptable("Wire Transfer Fraud")  # True (history)
await compliance_guardrail.is_acceptable("Unauthorized International Transaction")  # True (science)
await compliance_guardrail.is_acceptable("How to commit fraud")  # False (harmful)
await compliance_guardrail.is_acceptable("Malicious transaction")  # False (age-inappropriate)
```

**Why LLM judge?**
- "Wire Transfer Fraud" → Recognizes as legitimate banking operations despite war dispute claim
- "How to hack" → Recognizes harmful intent despite technical dispute claim
- Context matters, rules can't capture all cases

---

#### Use Case 2: Domain-Specific Validation

```python
# Guardrail: Fraud detection
medical_guardrail = InputGuardrail(
    name="medical_compliance",
    accept_condition="The query does not request medical diagnosis or treatment advice"
)

await medical_guardrail.is_acceptable("What is chargeback fraud?")  # True (educational)
await medical_guardrail.is_acceptable("Is this transaction fraudulent?")  # False (diagnosis)
await medical_guardrail.is_acceptable("Should I take insulin?")  # False (treatment advice)
```

---

#### Use Case 3: PII Detection

```python
# Guardrail: Personally identifiable information
pii_guardrail = InputGuardrail(
    name="no_pii",
    accept_condition="""The text does not contain personally identifiable information including:
    - Full names with context
    - Home addresses
    - Phone numbers
    - Social Security Numbers
    - Credit card numbers
    """
)

await pii_guardrail.is_acceptable("Alice and Bob are examples")  # True (generic)
await pii_guardrail.is_acceptable("My name is John Smith and I live at 123 Main St")  # False (PII)
```

---

#### Use Case 4: Multi-Guardrail Validation

**Parallel execution for speed**:

```python
# Create multiple guardrails
guardrails = [
    InputGuardrail("transaction_legitimacy", "Topic is appropriate for banking"),
    InputGuardrail("no_profanity", "Text does not contain profanity"),
    InputGuardrail("legitimate_inquiry", "Query has clear legitimate banking inquiry"),
]

# Parallel validation (all must pass)
dispute claim = "Explain unauthorized international transaction"

results = await asyncio.gather(
    *[guard.is_acceptable(dispute claim, raise_exception=True) for guard in guardrails]
)
# If any guardrail raises exception, processing stops immediately
# Otherwise, all results are True

print(f"All {len(guardrails)} guardrails passed!")
```

**Performance**:
- Sequential: 200ms × 3 = 600ms
- Parallel: max(200ms, 200ms, 200ms) = 200ms (3x faster)

---

### Logging and Observability

All guardrail decisions are automatically logged to `logs/guards.json`:

```json
{
  "timestamp": "2025-01-05T10:30:45.123Z",
  "level": "DEBUG",
  "logger": "dispute_resolution_app.utils.guardrails",
  "guardrail_id": "Input Guardrail topic_guardrail abc-123",
  "condition": "The dispute claim is appropriate for banking dispute resolution",
  "input": "Explain unauthorized international transaction",
  "output": true
}
```

**Benefits**:
- 🔍 Debug why specific queries were rejected
- 📊 Analyze false positive/negative rates
- 📈 Track policy effectiveness over time
- 🐛 Reproduce issues with exact inputs
- 🔒 Compliance audit trail

**Viewing logs**:
```bash
# View all guardrail decisions
cat logs/guards.json | jq .

# Find rejections
cat logs/guards.json | jq 'select(.output == false)'

# Count decisions by guardrail
cat logs/guards.json | jq -r '.guardrail_id' | sort | uniq -c
```

---

### Performance Optimization

#### Optimization 1: Use SMALL_MODEL

```python
# Default configuration (already optimal)
agent = Agent(llms.SMALL_MODEL, output_type=bool)
# Latency: 100-300ms
# Cost: $0.01 per 1000 checks
```

#### Optimization 2: Parallel Execution

```python
# Run guardrail + main task concurrently
validation_task = guardrail.is_acceptable(input, raise_exception=True)
processing_task = agent.run(input)

_, result = await asyncio.gather(validation_task, processing_task)
# Saves guardrail latency if both succeed
```

#### Optimization 3: Caching Frequent Queries

```python
from functools import lru_cache

class CachedGuardrail:
    def __init__(self, guardrail: InputGuardrail):
        self.guardrail = guardrail
        self.cache = {}

    async def is_acceptable(self, text: str, raise_exception: bool = False) -> bool:
        # Check cache first
        if text in self.cache:
            return self.cache[text]

        # Call guardrail
        result = await self.guardrail.is_acceptable(text, raise_exception)

        # Cache result
        self.cache[text] = result
        return result

# Use for repeated queries
cached_guard = CachedGuardrail(compliance_guardrail)
await cached_guard.is_acceptable("Unauthorized International Transaction")  # API call
await cached_guard.is_acceptable("Unauthorized International Transaction")  # Cache hit (instant)
```

---

### Common Pitfalls

#### ❌ Pitfall 1: Using BEST_MODEL for Boolean Decisions

**Problem**: Overkill for simple yes/no

```python
# ❌ BAD
agent = Agent(llms.BEST_MODEL, output_type=bool)
# 10x more expensive, 3x slower
```

**Solution**: Use SMALL_MODEL
```python
# ✅ GOOD
agent = Agent(llms.SMALL_MODEL, output_type=bool)
```

---

#### ❌ Pitfall 2: Vague Accept Conditions

**Problem**: Inconsistent behavior

```python
# ❌ BAD: Too vague
accept_condition = "The input is good quality"
# What is "good"? Results will be inconsistent
```

**Solution**: Be specific
```python
# ✅ GOOD: Clear criteria
accept_condition = "The query is a complete sentence with clear legitimate banking inquiry"
```

---

#### ❌ Pitfall 3: Missing Exception Handling

**Problem**: Crashes entire application

```python
# ❌ BAD: No try/catch
resolver = await assigner.assign_resolver(dispute claim)
# If guardrail rejects, app crashes
```

**Solution**: Handle gracefully
```python
# ✅ GOOD: Graceful handling
try:
    resolver = await assigner.assign_resolver(dispute claim)
except InputGuardrailException as e:
    logger.warning(f"Query rejected: {e}")
    return {"error": "Topic violates content policy"}
```

---

#### ❌ Pitfall 4: Not Logging Decisions

**Problem**: Can't debug rejections

**Solution**: InputGuardrail logs automatically
```python
# All decisions logged to logs/guards.json
# No additional code needed!
```

---

#### ❌ Pitfall 5: Assuming 100% Accuracy

**Problem**: LLMs can make mistakes

**Solution**: Monitor and combine with rules
```python
# Defense in depth
async def validate(text: str) -> bool:
    # Layer 1: Rule-based (profanity list)
    if contains_banned_words(text):
        return False

    # Layer 2: LLM judge (nuanced)
    return await guardrail.is_acceptable(text)
```

---

### Testing Guardrails

**Test with diverse examples**:

```python
import pytest

@pytest.mark.asyncio
async def test_compliance_guardrail_accepts_banking_topics():
    """Test that legitimate educational dispute claims pass validation."""
    guardrail = InputGuardrail(
        "k12_test",
        "The dispute claim is appropriate for banking banking operations"
    )

    # Should accept
    assert await guardrail.is_acceptable("Wire Transfer Fraud")
    assert await guardrail.is_acceptable("Unauthorized International Transaction")
    assert await guardrail.is_acceptable("Solving equations")

@pytest.mark.asyncio
async def test_compliance_guardrail_rejects_inappropriate_topics():
    """Test that inappropriate dispute claims are rejected."""
    guardrail = InputGuardrail(
        "k12_test",
        "The dispute claim is appropriate for banking banking operations"
    )

    # Should reject
    assert not await guardrail.is_acceptable("How to commit fraud")
    assert not await guardrail.is_acceptable("Explicit adult content")

@pytest.mark.asyncio
async def test_guardrail_raises_exception_when_configured():
    """Test exception mode for critical validation."""
    guardrail = InputGuardrail(
        "k12_test",
        "The dispute claim is appropriate for banking banking operations"
    )

    with pytest.raises(InputGuardrailException):
        await guardrail.is_acceptable("Inappropriate dispute claim", raise_exception=True)
```

---

### Advanced: Custom Guardrail Types

**Extending InputGuardrail for domain-specific needs**:

```python
class MultiCriteriaGuardrail(InputGuardrail):
    """Guardrail that checks multiple conditions."""

    def __init__(self, name: str, conditions: list[str]):
        # Combine conditions into single prompt
        combined = " AND ".join(conditions)
        super().__init__(name, combined)
        self.conditions = conditions

# Usage
multi_guard = MultiCriteriaGuardrail(
    "comprehensive_check",
    conditions=[
        "The dispute claim is appropriate for banking",
        "The query has legitimate banking inquiry",
        "The text does not contain profanity"
    ]
)
```

---

### Integration with Other Services

**Guardrails compose with other horizontal services**:

```python
async def safe_resolver_workflow(dispute claim: str) -> Resolution:
    # 1. Guardrails: Validate input
    if not await guardrail.is_acceptable(dispute claim):
        raise ValueError("Topic not allowed")

    # 2. Long-term Memory: Retrieve context
    memories = memory.search_relevant_memories(dispute claim, top_k=3)

    # 3. Prompt Service: Render prompt
    prompt = PromptService.render_prompt(
        "dispute_resolver_generate",
        dispute claim=dispute claim,
        memories=memories
    )

    # 4. Generate resolution
    resolution = await resolver.resolve_dispute(dispute claim)

    # 5. Evaluation Recording: Log output
    await evals.record_ai_response("dispute_resolver", prompt, resolution)

    return resolution
```

**Service interaction flow**:
```
Input → Guardrails (validate) → Memory (retrieve) → Prompts (render)
→ LLM (generate) → Guardrails (validate output) → Evals (log) → Output
```

---



## 🏦 Real-World Scenario 1: Unauthorized International Transaction

**Context**: Customer reports $2,500 charge from Morocco. They're based in Ohio, never traveled internationally this month.

**Business Requirements**:
- ✅ Regulation E compliance (provisional credit within 10 business days)
- ✅ Fraud pattern detection (is this legitimate or fraud?)
- ✅ Customer history analysis (does customer have prior disputes?)
- ✅ Audit trail for regulatory review

### Step-by-Step Workflow

This scenario demonstrates **all 5 horizontal services** working together:

#### 1. Input Validation (Guardrails)

```python
# dispute_resolution_app/utils/guardrails.py
from dispute_resolution_app.utils.guardrails import InputGuardrail

# Guardrail 1: Reg E Eligibility Check
reg_e_guardrail = InputGuardrail(
    name="reg_e_provisional_credit_eligibility",
    accept_condition="""The dispute meets Regulation E requirements for provisional credit:
    - Transaction occurred within 60 days of statement date
    - Transaction type is electronic (card, ACH, wire)
    - Customer reported in good faith
    - Amount is within normal dispute range ($0-$10,000)
    """
)

# Guardrail 2: PII Detection (ensure no sensitive data logged)
pii_guardrail = InputGuardrail(
    name="no_customer_pii",
    accept_condition="""The dispute claim does not contain:
    - Social Security Numbers
    - Full account numbers (last 4 digits OK)
    - Customer passwords or PINs
    - Home addresses
    """
)

# Apply guardrails
dispute_claim = {
    "customer_id": "CUST_78234",
    "transaction_id": "TXN_829475",
    "merchant": "Restaurant in Casablanca, Morocco",
    "amount": 2500.00,
    "currency": "USD",
    "date": "2025-01-03",
    "claim": "I did not authorize this charge. I have not traveled internationally."
}

# Parallel validation (fail fast if either fails)
import asyncio
is_reg_e_valid, no_pii = await asyncio.gather(
    reg_e_guardrail.is_acceptable(str(dispute_claim), raise_exception=True),
    pii_guardrail.is_acceptable(str(dispute_claim), raise_exception=True)
)
# ✅ Both pass: Transaction is within 60 days, no PII detected
```

**Guardrails outcome**: ✅ Proceed to resolution

---

#### 2. Memory Retrieval (Long-term Memory)

```python
# dispute_resolution_app/utils/long_term_memory.py
from dispute_resolution_app.utils.long_term_memory import search_relevant_memories

# Query 1: Similar fraud patterns
similar_disputes = search_relevant_memories(
    query=f"Unauthorized international charge Morocco {dispute_claim['merchant']}",
    category="fraud_patterns",
    limit=5
)

# Query 2: Customer dispute history
customer_history = search_relevant_memories(
    query=f"Customer {dispute_claim['customer_id']} dispute patterns",
    metadata_filter={"customer_id": dispute_claim['customer_id']},
    limit=10
)

# Results:
# similar_disputes = [
#     "5 prior disputes at this merchant - 80% fraud confirmed",
#     "Morocco restaurant charges - common card skimming location",
#     "Similar pattern: Customer in US, charge in Morocco same day"
# ]
#
# customer_history = [
#     "Customer opened account 3 years ago - excellent standing",
#     "0 prior disputes in customer history",
#     "Spending pattern: 95% domestic, 5% Canada"
# ]
```

**Memory outcome**: 🔴 High fraud indicators (merchant has 80% fraud rate, customer never traveled internationally)

---

#### 3. Prompt Rendering (Prompt Service)

```python
# dispute_resolution_app/utils/prompt_service.py
from dispute_resolution_app.utils.prompt_service import PromptService

# Prompt template: prompts/card_dispute_resolver_prompt.j2
prompt = PromptService.render_prompt(
    "card_dispute_resolver_system_prompt",
    dispute_claim=dispute_claim,
    fraud_indicators=similar_disputes,
    customer_history=customer_history,
    reg_e_context={
        "provisional_credit_required": True,
        "timeline": "10 business days",
        "customer_liability": "$50 if reported within 2 days, $500 if within 60 days"
    }
)

# Rendered prompt includes:
# """
# You are a card dispute resolution specialist.
#
# DISPUTE CLAIM:
# - Customer: CUST_78234
# - Transaction: $2,500 at Restaurant in Casablanca, Morocco
# - Customer claim: "I did not authorize this charge. I have not traveled internationally."
#
# FRAUD INDICATORS:
# - Merchant has 80% fraud confirmation rate
# - Morocco restaurant charges - common card skimming location
#
# CUSTOMER HISTORY:
# - 3 years, excellent standing, 0 prior disputes
# - Spending pattern: 95% domestic
#
# REGULATION E REQUIREMENTS:
# - Provisional credit required within 10 business days
# - Customer liability: $50 (reported within 2 days)
#
# Provide resolution recommendation: APPROVE / DENY / ESCALATE
# """
```

**Prompt outcome**: Context-rich prompt with fraud indicators + customer history

---

#### 4. LLM Generation + Evaluation Logging

```python
# dispute_resolution_app/utils/llms.py and save_for_eval.py
from dispute_resolution_app.utils.llms import BEST_MODEL
from dispute_resolution_app.utils.save_for_eval import Evals

# Generate resolution
from pydantic_ai import Agent

agent = Agent(BEST_MODEL, system_prompt=prompt)
resolution = await agent.run(f"Resolve dispute: {dispute_claim['transaction_id']}")

# Resolution output (structured):
# {
#     "dispute_id": "DISP_74839",
#     "verdict": "APPROVE",
#     "rationale": "High fraud indicators (merchant 80% fraud rate, customer never traveled internationally). "
#                  "Customer has excellent 3-year history with 0 prior disputes. Reg E requires provisional credit.",
#     "provisional_credit_amount": 2500.00,
#     "timeline": "10 business days",
#     "confidence_score": 0.94,
#     "customer_liability": 50.00,
#     "next_steps": "Issue provisional credit. Investigate merchant. File SAR if fraud confirmed."
# }

# Log for audit trail (Regulation E requirement)
evals = Evals(target="dispute_resolution")
await evals.record_ai_response(
    target="card_dispute_resolution",
    ai_input={
        "dispute_claim": dispute_claim,
        "fraud_indicators": similar_disputes,
        "customer_history": customer_history
    },
    ai_response=resolution
)
# ✅ Logged to evals.log with timestamp, model, input, output
```

**Evaluation outcome**: ✅ Audit trail created for regulatory review

---

#### 5. Human Review Trigger (Human Feedback)

```python
# dispute_resolution_app/utils/human_feedback.py
from dispute_resolution_app.utils.human_feedback import record_human_feedback

# High-value dispute ($2,500) triggers compliance officer review
if dispute_claim["amount"] > 1000:
    print(f"⚠️  High-value dispute (${dispute_claim['amount']}) - Compliance officer review required")

    # Compliance officer reviews AI recommendation
    # In production: Send to review queue, wait for officer decision

    # Officer decision:
    compliance_officer_decision = {
        "verdict": "APPROVE",  # Agrees with AI
        "notes": "Fraud indicators strong. Customer trustworthy. Approve provisional credit per Reg E.",
        "officer_id": "OFFICER_234",
        "timestamp": "2025-01-05T14:23:11Z"
    }

    # Log human feedback (override or confirmation)
    record_human_feedback(
        target="dispute_verdict",
        ai_input=dispute_claim,
        ai_response=resolution["verdict"],
        human_choice=compliance_officer_decision["verdict"],
        metadata={
            "officer_id": compliance_officer_decision["officer_id"],
            "notes": compliance_officer_decision["notes"],
            "agreement": resolution["verdict"] == compliance_officer_decision["verdict"]
        }
    )
    # ✅ Logged to feedback.log for pattern learning
```

**Human Feedback outcome**: ✅ Compliance officer confirmed AI decision (builds trust in system)

---

### Business Value Delivered

**Compliance**:
- ✅ Regulation E requirements met (provisional credit, timeline, liability)
- ✅ Audit trail for regulatory review (all decisions logged)
- ✅ Human oversight for high-value disputes

**Fraud Prevention**:
- ✅ Merchant fraud pattern detected (80% fraud rate)
- ✅ Customer spending anomaly identified (never traveled internationally)
- ✅ Provisional credit issued, merchant investigation initiated

**Customer Experience**:
- ✅ Fast resolution (10 business days vs. 45-90 day investigation)
- ✅ Customer liability limited ($50 vs. full $2,500)
- ✅ Transparent rationale provided

**Operational Efficiency**:
- ✅ Automated guardrail validation (200ms)
- ✅ Memory retrieval for pattern matching (150ms)
- ✅ Human review only for high-value cases (>$1,000)
- ✅ Total processing time: ~3 seconds (vs. 30 minutes manual review)

**Cost Savings**:
- LLM API call: ~$0.05
- Guardrails validation: ~$0.01
- Memory retrieval: ~$0.001
- Evaluation logging: negligible
- **Total cost per dispute**: ~$0.06 (vs. $15 manual review by analyst)

---

## Long-term Memory (Detailed)

### Overview: Pattern 28 - Stateful Agents

**Core principle**: Enable agents to learn from past interactions and maintain context across sessions through persistent memory storage and semantic retrieval.

**Key capabilities**:
1. **Memory Storage**: Add observations, feedback, and user preferences
2. **Semantic Search**: Retrieve relevant memories based on context
3. **User Context**: Maintain per-user memory profiles
4. **Cumulative Learning**: Agents improve over time by remembering past mistakes

**Benefits**:
- 🧠 **Personalization**: Agents adapt to individual user preferences
- 🔄 **Continuous improvement**: Learn from feedback without retraining
- 📚 **Context retention**: Remember past conversations and decisions
- 🎯 **Consistency**: Apply learned patterns across sessions
- 💡 **Knowledge accumulation**: Build up domain expertise over time

**Code reference**: [`dispute_resolution_app/utils/long_term_memory.py`](../../utils/long_term_memory.py)

**Technology**: Built on [mem0](https://mem0.ai/) for managed memory with vector embeddings

---

### Implementation: LongTermMemory Class

From [`utils/long_term_memory.py:11-54`](../../utils/long_term_memory.py#L11-L54):

```python
class LongTermMemory:
    def __init__(self, app_name: str = "dispute_resolution_app"):
        """Initialize memory store with vector database backend.

        Uses mem0 library with:
        - Chroma vector database for embeddings
        - Gemini for LLM-based memory processing
        - Gemini embeddings for semantic search
        """
        # Configure storage directory
        temp_dir = tempfile.mkdtemp(prefix=app_name)
        vectordb = os.path.join(temp_dir, "vectordb")

        # mem0 configuration
        config = {
            "vector_store": {
                "provider": "chroma",
                "config": {
                    "collection_name": app_name,
                    "path": vectordb,
                }
            },
            "llm": {
                "provider": "gemini",
                "config": {
                    "model": llms.DEFAULT_MODEL,
                    "temperature": 0.2,
                    "max_tokens": 1000,
                }
            },
            "embedder": {
                "provider": "gemini",
                "config": {
                    "model": "models/gemini-embedding-exp-03-07",
                    "embedding_dims": 1536
                }
            },
            "history_db_path": os.path.join(temp_dir, "history.db"),
        }

        self.memory = Memory.from_config(config)
```

**Key components**:
- **Vector store**: Chroma database for embedding storage
- **LLM**: Gemini for processing and structuring memories
- **Embedder**: Gemini embeddings (1536 dimensions) for semantic search
- **History DB**: SQLite database for conversation history

---

### Core API: add_to_memory() and search_relevant_memories()

#### Method 1: add_to_memory()

From [`utils/long_term_memory.py:55-72`](../../utils/long_term_memory.py#L55-L72):

```python
def add_to_memory(
    user_message: str,
    metadata: Dict,
    user_id: str = "default_user"
) -> Dict[str, Any]:
    """Store a memory for future retrieval.

    Args:
        user_message: The content to remember (observation, feedback, preference)
        metadata: Additional context (category, timestamp, source agent)
        user_id: User identifier for multi-user applications

    Returns:
        Dictionary with memory_id and status
    """
    messages = [
        {
            "role": "user",
            "content": user_message
        }
    ]
    result = self.memory.add(messages=messages, user_id=user_id, metadata=metadata)
    logger.debug(f"✓ Memory added for {user_id}: {result}")
    return result
```

**Usage example**:
```python
# Store writing style preference
add_to_memory(
    user_message="Customer disputes typically resolve in their favor over passive voice",
    metadata={
        "category": "writing_style",
        "resolver_type": "CardDisputeResolver",
        "timestamp": "2025-01-05T10:30:00Z"
    },
    user_id="compliance_officer_123"
)

# Store feedback on resolution
add_to_memory(
    user_message="Previous resolution about unauthorized international transaction was too complex. Use simpler language.",
    metadata={
        "category": "content_feedback",
        "dispute claim": "unauthorized international transaction",
        "resolution_id": "res_456"
    }
)
```

---

#### Method 2: search_relevant_memories()

From [`utils/long_term_memory.py:73-122`](../../utils/long_term_memory.py#L73-L122):

```python
def search_relevant_memories(
    query: str,
    user_id: str = "default_user",
    limit: int = 3
) -> List[str]:
    """Search for relevant memories using semantic similarity.

    Args:
        query: Search query describing the context
        user_id: User to search memories for
        limit: Maximum number of memories to return

    Returns:
        List of relevant memory strings, ordered by relevance
    """
    memories = mem0.search_relevant_memories(query, user_id, limit)
    return [m['memory'] for m in memories]
```

**Usage example**:
```python
# Retrieve context for writing task
memories = search_relevant_memories(
    query="CardDisputeResolver resolving dispute about unauthorized international transaction",
    limit=3
)
# Returns top 3 relevant memories:
# [
#   "Customer disputes typically resolve in their favor over passive voice",
#   "Previous resolution about unauthorized international transaction was too complex",
#   "Merchant has 15% dispute rate for 9th transaction category customers"
# ]
```

---

### How Semantic Search Works

**Under the hood**:

1. **Indexing** (when adding memory):
   ```
   User message → Gemini Embeddings → 1536-dim vector → Chroma database
   ```

2. **Retrieval** (when searching):
   ```
   Query → Gemini Embeddings → 1536-dim vector
   → Cosine similarity with stored vectors
   → Top-k most similar memories
   ```

**Why embeddings?**
- Captures semantic meaning, not just keywords
- "Active voice preferred" matches "Avoid passive constructions"
- "Too complex" matches "Use simpler language"

**Example**:
```python
# These queries return similar memories despite different wording
search_relevant_memories("How to resolve disputes effectively?")
search_relevant_memories("Tips for clear resolution statements?")
search_relevant_memories("Avoid ambiguous language in resolutions?")

# All retrieve: "Disputes require clear, unambiguous language explaining the resolution decision"
```

---

### Integration in AbstractResolver

**Use case 1: Writing initial draft**

From [`agents/generic_resolver_agent.py:59-72`](../../agents/generic_resolver_agent.py#L59-L72):

```python
async def resolve_dispute(self, dispute claim: str) -> Resolution:
    # Search memories for relevant context
    memories = ltm.search_relevant_memories(
        f"{self.resolver.name}, resolve dispute about {dispute claim}"
    )

    # Render prompt with memories included
    prompt_vars = {
        "prompt_name": "AbstractResolver_generate_resolution",
        "content_type": self.get_content_type(),
        "additional_instructions": memories,  # Inject memories into prompt
        "dispute claim": dispute claim
    }
    prompt = PromptService.render_prompt(**prompt_vars)

    # Generate resolution with context from past interactions
    result = await self.write_response(dispute claim, prompt)
    return result
```

**What happens**:
1. Query: `"CardDisputeResolver, resolve dispute about unauthorized international transaction"`
2. Retrieved memories:
   - "Customer disputes typically resolve in their favor"
   - "Previous unauthorized international transaction resolution was too complex"
   - "Merchant has 15% dispute rate for 9th transaction category"
3. Memories injected into prompt as `additional_instructions`
4. DisputeResolver generates resolution following learned preferences

---

**Use case 2: Revising resolution**

From [`agents/generic_resolver_agent.py:74-89`](../../agents/generic_resolver_agent.py#L74-L89):

```python
async def revise_resolution(
    self,
    dispute claim: str,
    initial_draft: Resolution,
    panel_review: str
) -> Resolution:
    # Search for revision-specific memories
    memories = ltm.search_relevant_memories(
        f"{self.resolver.name}, revise {dispute claim}"
    )

    prompt_vars = {
        "prompt_name": "AbstractResolver_revise_resolution",
        "dispute claim": dispute claim,
        "content_type": self.get_content_type(),
        "additional_instructions": memories,  # Past revision feedback
        "initial_draft": initial_draft.to_markdown(),
        "panel_review": panel_review
    }
    prompt = PromptService.render_prompt(**prompt_vars)

    result = await self.revise_response(prompt)
    return result
```

**Memory categories**:
- **Writing memories**: General style preferences
- **Revision memories**: How past revisions were received
- **Topic memories**: Subject-specific feedback

---

### Memory Lifecycle Example

**Scenario**: User requests resolutions on science dispute claims

**Session 1: First interaction**
```python
# User request
dispute claim = "Unauthorized International Transaction"

# DisputeResolver generates resolution (no memories yet)
resolution = await resolver.resolve_dispute(dispute claim)

# User provides feedback
feedback = "Too technical! Use simpler language for retail customers."

# Store feedback in memory
add_to_memory(
    user_message=feedback,
    metadata={"category": "content_feedback", "dispute_claim": dispute_claim}
)
```

**Session 2: Next day**
```python
# User requests another science resolution
dispute claim = "Cell division"

# DisputeResolver searches memories
memories = search_relevant_memories(f"CardDisputeResolver, resolve dispute about {dispute claim}")
# Returns: ["Too technical! Use simpler language for retail customers."]

# DisputeResolver generates resolution with learned context
resolution = await resolver.resolve_dispute(dispute claim)
# Resolution is now written in simpler language!
```

**Session 3: Learning accumulates**
```python
# More feedback after cell division resolution
add_to_memory(
    user_message="Great! Keep using active voice and bullet points.",
    metadata={"category": "writing_style"}
)

# Next resolution benefits from both memories
memories = search_relevant_memories("CardDisputeResolver, resolve dispute about DNA")
# Returns:
# - "Use simpler language for retail customers"
# - "Keep using active voice and bullet points"
```

---

### Use Cases

#### Use Case 1: User Preferences

**Store preferences once, apply forever**:

```python
# First interaction: User expresses preference
add_to_memory(
    user_message="I prefer resolutions with bullet points over long paragraphs",
    metadata={"category": "formatting_preference", "user_id": "compliance_officer_123"}
)

# All future resolutions automatically use bullet points
memories = search_relevant_memories("Generate resolution for compliance_officer_123")
# Memory retrieved and applied via additional_instructions
```

---

#### Use Case 2: Feedback Incorporation

**Learn from mistakes without retraining**:

```python
# Resolution rejected
add_to_memory(
    user_message="This resolution incorrectly stated provisional credit as 5 days. Reg E requires 10 business days.",
    metadata={"category": "compliance_correction", "error_type": "regulatory_requirement"}
)

# Future resolutions avoid the mistake
memories = search_relevant_memories("CardDisputeResolver, generate resolution")
# "Provisional credit must be provided within 10 business days per Reg E" is retrieved
```

---

#### Use Case 3: Topic-Specific Context

**Remember subject-matter nuances**:

```python
# Store domain knowledge
add_to_memory(
    user_message="When resolving dispute about Wire Transfer Fraud, include SWIFT trace details and beneficiary verification",
    metadata={"category": "topic_guidance", "subject": "wire_transfer"}
)

add_to_memory(
    user_message="ACH dispute resolutions should include transaction timeline and duplicate detection analysis",
    metadata={"category": "topic_guidance", "subject": "ach_payment"}
)

# WireTransferResolver gets specialized guidance
memories = search_relevant_memories("WIRE_TRANSFER_RESOLVER, resolve dispute about Wire Transfer Fraud")
# Returns: "Include SWIFT trace details and beneficiary verification"

# ACH dispute resolver gets duplicate detection guidance
memories = search_relevant_memories("ACH_DISPUTE_RESOLVER, resolve dispute about duplicate payment")
# Returns: "Include transaction timeline and duplicate detection analysis"
```

---

#### Use Case 4: Multi-User Personalization

**Separate memory profiles per user**:

```python
# ComplianceOfficer A prefers formal tone
add_to_memory(
    user_message="Use formal regulatory language",
    metadata={"category": "tone"},
    user_id="analyst_a"
)

# ComplianceOfficer B prefers casual tone
add_to_memory(
    user_message="Use clear, customer-friendly language",
    metadata={"category": "tone"},
    user_id="analyst_b"
)

# Each gets personalized resolutions
memories_a = search_relevant_memories("Generate resolution", user_id="analyst_a")
# Returns: "Use formal regulatory language"

memories_b = search_relevant_memories("Generate resolution", user_id="analyst_b")
# Returns: "Use clear, customer-friendly language"
```

---

### Memory-Enhanced Prompt Flow

**Without memory** (stateless):
```python
prompt = f"Write an resolution about {dispute claim} for 9th transaction category customers."
resolution = await resolver.generate(prompt)
# Generic output, no personalization
```

**With memory** (stateful):
```python
# Retrieve learned context
memories = search_relevant_memories(f"Resolve dispute about {dispute claim}")
# memories = [
#   "Customer disputes typically resolve in their favor",
#   "Use bullet points",
#   "Previous resolution on similar dispute claim was too long"
# ]

# Inject memories into prompt
prompt = f"""Write an resolution about {dispute claim} for 9th transaction category customers.

IMPORTANT CONTEXT FROM PAST INTERACTIONS:
{'\n'.join(memories)}

Apply these learnings to this resolution.
"""

resolution = await resolver.generate(prompt)
# Personalized output following learned patterns!
```

---

### Observability: Memory Logs

**Logging is automatic** via Python logging:

```python
# From long_term_memory.py:67
logger.debug(f"✓ Memory added for {user_id}: {result}")

# From long_term_memory.py:77-116
logger.debug(f"Searching memories for: '{query}'")
logger.debug(f"Found {len(processed_memories)} relevant memories")
```

**Example logs**:
```json
{
  "timestamp": "2025-01-05T10:30:00Z",
  "level": "DEBUG",
  "logger": "dispute_resolution_app.utils.long_term_memory",
  "message": "Searching memories for: 'CardDisputeResolver, resolve dispute about unauthorized international transaction'",
  "query": "CardDisputeResolver, resolve dispute about unauthorized international transaction",
  "user_id": "default_user"
}

{
  "timestamp": "2025-01-05T10:30:01Z",
  "level": "DEBUG",
  "message": "Found 3 relevant memories",
  "memories": [
    "Customer disputes typically resolve in their favor over passive voice",
    "Previous resolution about unauthorized international transaction was too complex",
    "Merchant has 15% dispute rate for 9th transaction category customers"
  ]
}
```

---

### Performance Considerations

#### Latency

**Memory operations add overhead**:
- `add_to_memory()`: ~200-500ms (embedding generation + database write)
- `search_relevant_memories()`: ~100-300ms (embedding + vector search)

**Optimization strategies**:

1. **Batch memory additions**:
```python
# ❌ BAD: Multiple sequential adds
for feedback in feedbacks:
    add_to_memory(feedback, metadata)
# Total: 500ms × 5 = 2500ms

# ✅ GOOD: Batch add (if mem0 supports)
add_memories_batch(feedbacks, metadata)
# Total: ~800ms
```

2. **Cache frequent queries**:
```python
from functools import lru_cache

@lru_cache(maxsize=100)
def cached_search(query: str, user_id: str = "default_user"):
    return search_relevant_memories(query, user_id)
```

3. **Parallel execution**:
```python
# Run memory search concurrently with other operations
memories_task = asyncio.create_task(
    search_relevant_memories_async(query)
)
other_task = asyncio.create_task(some_other_operation())

memories, other_result = await asyncio.gather(memories_task, other_task)
```

---

#### Storage

**Memory accumulates over time**:
- Each memory: ~100-200 bytes (text) + 1536 floats × 4 bytes = ~6KB
- 1000 memories ≈ 6MB
- 100,000 memories ≈ 600MB

**Management strategies**:
1. **Periodic cleanup**: Remove old, irrelevant memories
2. **User-based partitioning**: Separate databases per user
3. **Memory importance scoring**: Keep only high-value memories

---

### Future Enhancement: Replacing with mem0ai

**Current implementation** uses basic mem0 features. The dispute resolution app is designed to be upgraded to full mem0ai capabilities:

**Future capabilities**:
```python
# Advanced memory operations (not yet implemented)
memory.update(memory_id="mem_123", new_content="Updated preference")
memory.delete(memory_id="mem_456")  # Remove outdated memory
memory.search(query="...", filters={"category": "writing_style"})  # Filtered search
```

**Migration path**:
```python
# Current: Basic mem0
from mem0 import Memory

# Future: Full mem0ai platform
from mem0ai import MemoryClient

memory = MemoryClient(api_key=os.getenv("MEM0_API_KEY"))
# Hosted service with advanced features:
# - Automatic memory summarization
# - Conflict resolution
# - Memory versioning
# - Analytics dashboard
```

**See**: [mem0.ai documentation](https://docs.mem0.ai/)

---

### Common Pitfalls

#### ❌ Pitfall 1: Using Temporary Directory

**Problem**: Memories lost after restart

```python
# ❌ BAD: Current implementation
temp_dir = tempfile.mkdtemp(prefix=app_name)
# Memories deleted when program exits!
```

**Solution**: Use persistent directory
```python
# ✅ GOOD: Production configuration
memory_dir = os.path.expanduser("~/.dispute_resolution_app/memory")
os.makedirs(memory_dir, exist_ok=True)

config = {
    "vector_store": {
        "config": {
            "path": os.path.join(memory_dir, "vectordb")
        }
    },
    "history_db_path": os.path.join(memory_dir, "history.db")
}
```

**Note**: The dispute resolution app currently uses `tempfile.mkdtemp()` with a warning (see [`long_term_memory.py:14-15`](../../utils/long_term_memory.py#L14-L15)). This is intentional for demo purposes but should be changed for production.

---

#### ❌ Pitfall 2: Vague Memory Queries

**Problem**: Poor retrieval quality

```python
# ❌ BAD: Too vague
memories = search_relevant_memories("generate resolution")
# Returns: Random mix of unrelated memories
```

**Solution**: Be specific
```python
# ✅ GOOD: Specific context
memories = search_relevant_memories(
    f"{resolver.name}, resolve dispute about {dispute_claim} for {transaction_type}"
)
# Returns: Relevant memories for this exact context
```

---

#### ❌ Pitfall 3: Not Storing Context Metadata

**Problem**: Can't filter or analyze memories

```python
# ❌ BAD: No metadata
add_to_memory("Use active voice", metadata={})
# Can't filter by category, timestamp, or source
```

**Solution**: Rich metadata
```python
# ✅ GOOD: Comprehensive metadata
add_to_memory(
    "Use active voice",
    metadata={
        "category": "writing_style",
        "resolver_type": "CardDisputeResolver",
        "timestamp": datetime.now().isoformat(),
        "source": "user_feedback",
        "confidence": 0.9
    }
)
# Enables filtering, analytics, and debugging
```

---

#### ❌ Pitfall 4: Ignoring Retrieved Memories

**Problem**: Memories retrieved but not used

```python
# ❌ BAD: Search but don't use
memories = search_relevant_memories(query)
prompt = f"Resolve dispute about {dispute claim}"  # Memories not included!
```

**Solution**: Inject into prompt
```python
# ✅ GOOD: Use retrieved memories
memories = search_relevant_memories(query)
prompt = f"""Resolve dispute about {dispute claim}

Context from past interactions:
{'\n'.join(memories)}

Apply these guidelines.
"""
```

---

#### ❌ Pitfall 5: Memory Pollution

**Problem**: Storing low-quality or contradictory memories

```python
# ❌ BAD: Store everything
add_to_memory("Maybe try active voice?")  # Uncertain
add_to_memory("Use passive voice")  # Contradicts earlier preference!
```

**Solution**: Curate memories
```python
# ✅ GOOD: Filter and deduplicate
def add_quality_memory(message: str, metadata: Dict):
    # Check if contradicts existing memories
    existing = search_relevant_memories(message)
    if has_contradiction(existing, message):
        logger.warning(f"Contradictory memory: {message}")
        return

    # Only store high-confidence feedback
    if metadata.get("confidence", 0) > 0.7:
        add_to_memory(message, metadata)
```

---

### Testing Memory Integration

**Test memory storage and retrieval**:

```python
import pytest
from utils.long_term_memory import add_to_memory, search_relevant_memories

@pytest.mark.asyncio
async def test_memory_storage_and_retrieval():
    """Test that memories are stored and retrieved correctly."""
    # Add memory
    result = add_to_memory(
        "Customer disputes typically resolve in their favor",
        metadata={"category": "writing_style"},
        user_id="test_user"
    )

    assert "memory_id" in result or "id" in result

    # Search for memory
    memories = search_relevant_memories(
        "How should I write?",
        user_id="test_user"
    )

    assert len(memories) > 0
    assert "active voice" in memories[0].lower()

@pytest.mark.asyncio
async def test_memory_semantic_search():
    """Test that semantic search works (not just keyword matching)."""
    # Add memory with one phrasing
    add_to_memory(
        "User prefers resolutions to emphasize customer protection over fraud prevention",
        metadata={"category": "resolution_style"},
        user_id="test_user_2"
    )

    # Search with different phrasing
    memories = search_relevant_memories(
        "Should I use active or passive voice?",
        user_id="test_user_2"
    )

    # Semantic search should find relevant memory despite different wording
    assert len(memories) > 0
    assert "passive" in memories[0].lower()

@pytest.mark.asyncio
async def test_resolver_uses_memories():
    """Test that resolver integrates memories into prompts."""
    # Add writing preference
    add_to_memory(
        "Use bullet points for key concepts",
        metadata={"category": "formatting"},
        user_id="test_teacher"
    )

    # Create resolver and generate resolution
    resolver = ResolverFactory.create_resolver(DisputeResolver.CARD_DISPUTE_RESOLVER, vector_index)
    resolution = await resolver.resolve_dispute("Unauthorized International Transaction")

    # Check that memory context was used (via logs or prompt inspection)
    # This requires checking that search_relevant_memories was called
    # and memories were injected into prompt
```

---

### Integration with Other Services

**Memory composes naturally with other horizontal services**:

```python
async def enhanced_resolver_workflow(dispute claim: str) -> Resolution:
    # 1. Guardrails: Validate input
    if not await guardrail.is_acceptable(dispute claim):
        raise ValueError("Topic not allowed")

    # 2. Long-term Memory: Retrieve learned context
    memories = search_relevant_memories(f"Resolve dispute about {dispute claim}")

    # 3. Prompt Service: Render with memories
    prompt = PromptService.render_prompt(
        "dispute_resolver_generate",
        dispute claim=dispute claim,
        additional_instructions=memories  # Inject memories
    )

    # 4. Generate resolution
    resolution = await resolver.generate(prompt)

    # 5. Evaluation Recording: Log output
    await evals.record_ai_response("dispute_resolver", prompt, resolution)

    # 6. Long-term Memory: Store user feedback for future
    user_rating = await get_user_feedback(resolution)
    if user_rating < 3:
        add_to_memory(
            f"Resolution about {dispute claim} received low rating. User feedback: {user_rating}",
            metadata={"category": "quality_feedback", "rating": user_rating}
        )

    return resolution
```

**Memory feedback loop**:
```
Generate → Evaluate → Store Feedback → Retrieve Context → Generate Better
```

---

### Advanced Pattern: Memory-Guided Reflection

**Combine memory with reflection (Pattern 18)**:

```python
async def self_improving_resolver(dispute claim: str) -> Resolution:
    # Retrieve past mistakes
    past_errors = search_relevant_memories(
        f"Errors resolving dispute about {dispute claim}",
        limit=5
    )

    # Generate draft
    draft = await resolver.resolve_dispute(dispute claim)

    # Self-reflect using past errors as context
    reflection_prompt = f"""Review this draft resolution:
{draft.full_text}

Past errors to avoid:
{'\n'.join(past_errors)}

Does this draft repeat any past mistakes? If so, revise.
"""

    reflection = await critic.run(reflection_prompt)

    if reflection.has_errors:
        # Revise based on reflection
        revised = await resolver.revise_resolution(dispute claim, draft, reflection.feedback)
        return revised

    return draft
```

---

### Further Reading

- **Code reference**: [`utils/long_term_memory.py`](../../utils/long_term_memory.py)
- **Integration example**: [`agents/generic_resolver_agent.py:64`](../../agents/generic_resolver_agent.py#L64) and [`generic_resolver_agent.py:80`](../../agents/generic_resolver_agent.py#L80)
- **mem0 library**: [https://mem0.ai/](https://mem0.ai/)
- **Book chapter**: *Generative AI Design Patterns*, Chapter 28 (Stateful Agents)

---

## Evaluation Recording (Detailed)

### Overview: Pattern 30 - Observability

**Core principle**: Log all LLM interactions in a structured format to enable offline analysis, quality evaluation, and continuous improvement.

**Key capabilities**:
1. **Structured Logging**: Every agent interaction captured in JSON format
2. **Offline Analysis**: Evaluate quality metrics without live testing
3. **Training Data Collection**: Gather examples for fine-tuning smaller models
4. **Debugging**: Reproduce issues by examining exact inputs/outputs
5. **Cost Tracking**: Monitor token usage and API costs

**Benefits**:
- 📊 **Measurability**: Quantify agent performance with metrics
- 🐛 **Debuggability**: Trace failures to specific interactions
- 📈 **Continuous improvement**: Identify patterns to optimize
- 💰 **Cost optimization**: Detect expensive operations
- 🔬 **Experimentation**: A/B test prompts offline
- 🎓 **Model distillation**: Collect training data from large models

**Code reference**: [`dispute_resolution_app/utils/save_for_eval.py`](../../utils/save_for_eval.py)

**Technology**: Python's built-in `logging` module with JSON formatting

---

### Implementation: record_ai_response()

From [`utils/save_for_eval.py:5-11`](../../utils/save_for_eval.py#L5-L11):

```python
import logging

logger = logging.getLogger(__name__)

async def record_ai_response(target, ai_input, ai_response):
    """Record an AI interaction for evaluation.

    Args:
        target: Identifier for the operation (e.g., "initial_draft", "revision")
        ai_input: Input data (dict with dispute claim, prompts, context)
        ai_response: Output from LLM (Resolution, str, or structured data)
    """
    logger.info(f"AI Response", extra={
        "target": target,
        "ai_input": ai_input,
        "ai_response": ai_response,
    })
```

**Key design**:
- **Simple API**: Just 3 parameters (target, input, output)
- **Structured logging**: Uses Python's `extra` dict for JSON fields
- **Async-compatible**: Doesn't block agent execution
- **Automatic formatting**: Logging config handles JSON serialization

---

### Logging Configuration

From [`logging.json:43-67`](../../logging.json#L43-L67):

```json
{
  "handlers": {
    "evals": {
      "class": "logging.handlers.RotatingFileHandler",
      "level": "DEBUG",
      "formatter": "json",
      "filename": "evals.log",
      "maxBytes": 1024000,
      "backupCount": 2
    }
  },
  "loggers": {
    "utils.save_for_eval": {
      "handlers": ["evals"],
      "level": "DEBUG",
      "propagate": false
    }
  }
}
```

**Configuration features**:
- **RotatingFileHandler**: Auto-rotates when file reaches 1MB
- **JSON formatter**: Each line is valid JSON for easy parsing
- **Backup files**: Keeps 2 previous log files (evals.log.1, evals.log.2)
- **Isolated logger**: Only `utils.save_for_eval` writes to evals.log

---

### Log Format

**Example log entry** (evals.log):

```json
{
  "asctime": "2025-01-05 10:30:45,123",
  "levelname": "INFO",
  "name": "utils.save_for_eval",
  "message": "AI Response",
  "target": "initial_draft",
  "ai_input": {
    "prompt_name": "AbstractResolver_generate_resolution",
    "content_type": "an resolution",
    "additional_instructions": ["Use active voice", "Simple language"],
    "dispute claim": "unauthorized international transaction"
  },
  "ai_response": {
    "title": "Unauthorized International Transaction: How Plants Make Food",
    "summary": "Plants use sunlight to convert CO2 and water into glucose...",
    "full_text": "Unauthorized International Transaction is the process by which plants...",
    "key_lesson": "Plants are the producers in ecosystems",
    "index_keywords": ["unauthorized international transaction", "chloroplast", "glucose", "sunlight", "carbon dioxide"]
  }
}
```

**Fields explained**:
- `asctime`: Timestamp of interaction
- `target`: Operation identifier (for filtering)
- `ai_input`: Everything that went into the LLM
- `ai_response`: Complete output from the LLM

---

### Integration in Agents

#### Integration 1: DisputeResolver - Initial Draft

From [`agents/generic_resolver_agent.py:59-72`](../../agents/generic_resolver_agent.py#L59-L72):

```python
async def resolve_dispute(self, dispute claim: str) -> Resolution:
    # Prepare prompt variables
    prompt_vars = {
        "prompt_name": "AbstractResolver_generate_resolution",
        "content_type": self.get_content_type(),
        "additional_instructions": ltm.search_relevant_memories(f"{self.resolver.name}, resolve dispute about {dispute claim}"),
        "dispute claim": dispute claim
    }
    prompt = PromptService.render_prompt(**prompt_vars)

    # Generate resolution
    result = await self.write_response(dispute claim, prompt)

    # Log for evaluation
    await evals.record_ai_response(
        "initial_draft",
        ai_input=prompt_vars,
        ai_response=result
    )

    return result
```

**What's logged**:
- **Target**: `"initial_draft"` (identifies this as first version)
- **Input**: All prompt variables (dispute claim, content type, memories)
- **Output**: Complete Resolution object with all fields

---

#### Integration 2: DisputeResolver - Revision

From [`agents/generic_resolver_agent.py:74-89`](../../agents/generic_resolver_agent.py#L74-L89):

```python
async def revise_resolution(
    self,
    dispute claim: str,
    initial_draft: Resolution,
    panel_review: str
) -> Resolution:
    prompt_vars = {
        "prompt_name": "AbstractResolver_revise_resolution",
        "dispute claim": dispute claim,
        "content_type": self.get_content_type(),
        "additional_instructions": ltm.search_relevant_memories(f"{self.resolver.name}, revise {dispute claim}"),
        "initial_draft": initial_draft.to_markdown(),
        "panel_review": panel_review
    }
    prompt = PromptService.render_prompt(**prompt_vars)

    result = await self.revise_response(prompt)

    # Log revision
    await evals.record_ai_response(
        "revised_draft",
        ai_input=prompt_vars,
        ai_response=result
    )

    return result
```

**What's logged**:
- **Target**: `"revised_draft"` (distinguishes from initial draft)
- **Input**: Topic, initial draft text, panel reviews, memories
- **Output**: Revised Resolution object

**Why separate targets?**
- Filter initial vs. revised drafts
- Compare quality improvements
- Measure impact of review feedback

---

#### Integration 3: CompliancePanel - Individual Reviews

From [`agents/compliance_panel.py:52-63`](../../agents/compliance_panel.py#L52-L63):

```python
async def review(self, dispute claim: str, resolution: Resolution, reviews_so_far: list) -> str:
    # Format previous reviews
    reviews_text = []
    for reviewer, review in reviews_so_far:
        reviews_text.append(f"BEGIN review by {reviewer.name}:\n{review}\nEND review\n")

    # Generate review
    prompt_vars = {
        "prompt_name": "ReviewerAgent_review_prompt",
        "dispute claim": dispute claim,
        "resolution": resolution.to_markdown(),
        "reviews": "\n".join(reviews_text)
    }
    prompt = PromptService.render_prompt(**prompt_vars)
    result = await self.agent.run(prompt)

    # Log individual review
    await evals.record_ai_response(
        f"{self.reviewer.name}_review",
        ai_input=prompt_vars,
        ai_response=result.output
    )

    return result.output
```

**What's logged**:
- **Target**: `"FRAUD_ANALYST_review"`, `"COMPLIANCE_OFFICER_review"`, `"RISK_MANAGER_review"`, etc.
- **Input**: Dispute claim, resolution text, previous reviews
- **Output**: Review feedback string

---

#### Integration 4: Secretary - Consolidated Review

From [`agents/compliance_panel.py:88-96`](../../agents/compliance_panel.py#L88-L96):

```python
async def consolidate_reviews(self, reviews: list) -> str:
    """Consolidate all reviews into summary."""
    prompt_vars = {
        "prompt_name": "Secretary_consolidate_reviews",
        "reviews": reviews
    }
    prompt = PromptService.render_prompt(**prompt_vars)
    result = await self.agent.run(prompt)

    # Log consolidation
    await evals.record_ai_response(
        "consolidated_review",
        ai_input=prompt_vars,
        ai_response=result.output
    )

    return result.output
```

---

### Analyzing Logged Data

#### Reading evals.log

**Basic parsing**:

```python
import json

def get_records(target: str = "initial_draft"):
    """Read all records for a specific target."""
    records = []
    with open("evals.log") as f:
        for line in f:
            obj = json.loads(line)
            if obj['target'] == target:
                records.append(obj)
    return records

# Get all initial drafts
drafts = get_records("initial_draft")
print(f"Found {len(drafts)} initial drafts")

# Get all revisions
revisions = get_records("revised_draft")
print(f"Found {len(revisions)} revisions")
```

---

#### Example Evaluation: Keyword Quality

From [`evals/evaluate_keywords.py`](../../evals/evaluate_keywords.py):

This example shows how to evaluate the quality of keywords generated by resolvers.

**Step 1: Load records**

```python
from agents.resolution import Resolution

def get_records(target: str = "initial_draft"):
    records = []
    with open("evals.log") as f:
        for line in f:
            obj = json.loads(line)
            if obj['target'] == target:
                # Reconstruct Resolution object from logged string
                resolution = eval(obj['ai_response'])
                records.append(resolution)
    return records

resolutions = get_records("initial_draft")
```

**Step 2: Define evaluation metric**

```python
import numpy as np
from sentence_transformers import SentenceTransformer

def evaluate_keywords(keywords: List[str], embedding_model) -> float:
    """Evaluate keyword quality with two metrics:

    1. Ideal count: 5 keywords is optimal
    2. Diversity: Keywords should cover different concepts
    """
    # Metric 1: Penalize deviation from 5 keywords
    count_score = 1.0 - (np.abs(len(keywords) - 5) / 5.0)
    count_score = np.clip(count_score, 0.0, 1.0)

    # Metric 2: Diversity via embedding variance
    # More diverse keywords = higher variance
    embeds = [np.mean(embedding_model.encode(keyword)) for keyword in keywords]
    diversity_score = np.var(embeds)

    return count_score + diversity_score
```

**Step 3: Evaluate all resolutions**

```python
from scipy import stats

# Load embedding model
embed_model = SentenceTransformer('all-MiniLM-L6-v2')

# Evaluate each resolution
scores = []
for resolution in resolutions:
    score = evaluate_keywords(resolution.index_keywords, embed_model)
    print(f"{resolution.title}: {score:.2f}")
    scores.append(score)

# Statistical summary
summary = stats.describe(scores)
print(f"Mean: {summary.mean:.2f}, Std: {np.sqrt(summary.variance):.2f}")
print(f"Min: {summary.minmax[0]:.2f}, Max: {summary.minmax[1]:.2f}")
```

**Output example**:
```
Unauthorized International Transaction: How Plants Make Food: 1.23
Cell Division: The Process of Growth: 1.45
DNA Structure and Function: 0.98
...
Mean: 1.22, Std: 0.15
Min: 0.85, Max: 1.67
```

---

### Use Cases

#### Use Case 1: Quality Evaluation

**Measure response quality without human review**:

```python
def evaluate_resolution_quality(resolution: Resolution) -> dict:
    """Automated quality metrics."""
    return {
        "word_count": len(resolution.full_text.split()),
        "has_title": bool(resolution.title),
        "has_summary": bool(resolution.summary),
        "keyword_count": len(resolution.index_keywords),
        "has_lesson": bool(resolution.key_lesson),
        "completeness_score": sum([
            bool(resolution.title),
            bool(resolution.summary),
            bool(resolution.full_text),
            bool(resolution.key_lesson),
            len(resolution.index_keywords) >= 3
        ]) / 5.0
    }

# Evaluate all drafts
drafts = get_records("initial_draft")
for draft_log in drafts:
    resolution = eval(draft_log['ai_response'])
    quality = evaluate_resolution_quality(resolution)
    print(f"{resolution.title}: {quality['completeness_score']:.0%} complete")
```

---

#### Use Case 2: Prompt Effectiveness

**Compare which prompts produce better results**:

```python
def compare_prompts():
    """Compare quality by prompt type."""
    results = {}

    with open("evals.log") as f:
        for line in f:
            obj = json.loads(line)
            if obj['target'] == 'initial_draft':
                prompt_name = obj['ai_input']['prompt_name']
                resolution = eval(obj['ai_response'])

                if prompt_name not in results:
                    results[prompt_name] = []

                quality = evaluate_resolution_quality(resolution)
                results[prompt_name].append(quality['completeness_score'])

    # Statistical comparison
    for prompt_name, scores in results.items():
        print(f"{prompt_name}:")
        print(f"  Mean quality: {np.mean(scores):.2f}")
        print(f"  Std dev: {np.std(scores):.2f}")
        print(f"  Count: {len(scores)}")
```

---

#### Use Case 3: Cost Tracking

**Estimate token usage and API costs**:

```python
def estimate_costs():
    """Estimate costs from logged interactions."""
    total_tokens = 0
    operations = {}

    with open("evals.log") as f:
        for line in f:
            obj = json.loads(line)
            target = obj['target']

            # Rough token estimate (1 token ≈ 4 characters)
            input_text = str(obj['ai_input'])
            output_text = str(obj['ai_response'])

            input_tokens = len(input_text) // 4
            output_tokens = len(output_text) // 4
            total = input_tokens + output_tokens

            if target not in operations:
                operations[target] = {"count": 0, "tokens": 0}

            operations[target]['count'] += 1
            operations[target]['tokens'] += total
            total_tokens += total

    # Cost calculation (example rates)
    INPUT_COST_PER_1M = 0.075  # $0.075 per 1M input tokens
    OUTPUT_COST_PER_1M = 0.30  # $0.30 per 1M output tokens

    print("Cost Breakdown:")
    for target, stats in operations.items():
        cost = (stats['tokens'] / 1_000_000) * ((INPUT_COST_PER_1M + OUTPUT_COST_PER_1M) / 2)
        print(f"  {target}: {stats['count']} ops, {stats['tokens']:,} tokens, ${cost:.4f}")

    total_cost = (total_tokens / 1_000_000) * ((INPUT_COST_PER_1M + OUTPUT_COST_PER_1M) / 2)
    print(f"\nTotal: {total_tokens:,} tokens, ${total_cost:.2f}")
```

---

#### Use Case 4: Training Data Collection

**Collect high-quality examples for fine-tuning**:

```python
def collect_training_data(min_quality: float = 0.8):
    """Extract high-quality examples for model distillation."""
    training_examples = []

    drafts = get_records("initial_draft")
    for draft_log in drafts:
        resolution = eval(draft_log['ai_response'])
        quality = evaluate_resolution_quality(resolution)

        # Only collect high-quality examples
        if quality['completeness_score'] >= min_quality:
            training_examples.append({
                "input": draft_log['ai_input'],
                "output": resolution.to_markdown(),
                "metadata": {
                    "quality_score": quality['completeness_score'],
                    "timestamp": draft_log['asctime']
                }
            })

    print(f"Collected {len(training_examples)} high-quality examples")
    return training_examples

# Save for fine-tuning
import json
training_data = collect_training_data(min_quality=0.85)
with open("training_data.jsonl", "w") as f:
    for example in training_data:
        f.write(json.dumps(example) + "\n")
```

---

#### Use Case 5: Debugging Failures

**Reproduce and analyze failures**:

```python
def debug_failures():
    """Find and analyze failed interactions."""
    # Look for incomplete or error responses
    issues = []

    with open("evals.log") as f:
        for line in f:
            obj = json.loads(line)

            # Check for empty responses
            if not obj['ai_response'] or obj['ai_response'] == '{}':
                issues.append({
                    "type": "empty_response",
                    "target": obj['target'],
                    "input": obj['ai_input']
                })

            # Check for resolutions missing required fields
            if obj['target'] == 'initial_draft':
                try:
                    resolution = eval(obj['ai_response'])
                    if not resolution.title or not resolution.full_text:
                        issues.append({
                            "type": "incomplete_resolution",
                            "target": obj['target'],
                            "input": obj['ai_input'],
                            "missing": [
                                "title" if not resolution.title else None,
                                "full_text" if not resolution.full_text else None
                            ]
                        })
                except Exception as e:
                    issues.append({
                        "type": "parse_error",
                        "target": obj['target'],
                        "error": str(e)
                    })

    print(f"Found {len(issues)} issues:")
    for issue in issues[:10]:  # Show first 10
        print(f"  {issue['type']}: {issue['target']}")
```

---

### Performance Considerations

#### Overhead

**Logging adds minimal latency**:
- JSON serialization: ~1-5ms for typical Resolution object
- File write: ~1-2ms (async, non-blocking)
- **Total overhead**: ~2-7ms per operation (<1% of LLM call time)

**Why negligible**:
- Logging is async (doesn't block agent)
- File I/O buffered by OS
- JSON dumps is fast for simple objects

---

#### Storage

**Log file growth**:
- Average entry: ~500-1000 bytes (Resolution with full text)
- 1000 operations ≈ 0.5-1 MB
- Rotation at 1MB keeps active log small

**Management**:
```python
# Automatic rotation in logging.json
"maxBytes": 1024000,  # 1MB
"backupCount": 2       # Keep 2 old files

# Result: Max 3MB total (evals.log + evals.log.1 + evals.log.2)
```

---

### Common Pitfalls

#### ❌ Pitfall 1: Not Logging Inputs

**Problem**: Only logging outputs makes debugging hard

```python
# ❌ BAD: Missing input context
await evals.record_ai_response(
    "initial_draft",
    ai_input={},  # Empty!
    ai_response=resolution
)
```

**Solution**: Log complete input context
```python
# ✅ GOOD: Full context
await evals.record_ai_response(
    "initial_draft",
    ai_input=prompt_vars,  # Everything: dispute claim, memories, prompts
    ai_response=resolution
)
```

---

#### ❌ Pitfall 2: Inconsistent Target Names

**Problem**: Hard to filter logs

```python
# ❌ BAD: Inconsistent naming
await evals.record_ai_response("draft", ...)
await evals.record_ai_response("initial", ...)
await evals.record_ai_response("first_draft", ...)
# All mean the same thing!
```

**Solution**: Use consistent conventions
```python
# ✅ GOOD: Standard naming
TARGETS = {
    "INITIAL_DRAFT": "initial_draft",
    "REVISED_DRAFT": "revised_draft",
    "REVIEW": "{reviewer_name}_review",
    "CONSOLIDATED": "consolidated_review"
}

await evals.record_ai_response(TARGETS["INITIAL_DRAFT"], ...)
```

---

#### ❌ Pitfall 3: Logging Sensitive Data

**Problem**: PII or secrets in logs

```python
# ❌ BAD: Logging user data
await evals.record_ai_response(
    "draft",
    ai_input={"user_email": "compliance officer@bankingcorp.com", "api_key": "sk-..."},  # Oops!
    ai_response=resolution
)
```

**Solution**: Filter sensitive fields
```python
# ✅ GOOD: Sanitize inputs
def sanitize_input(data: dict) -> dict:
    """Remove sensitive fields before logging."""
    sensitive = ["api_key", "email", "password", "ssn"]
    return {k: v for k, v in data.items() if k not in sensitive}

await evals.record_ai_response(
    "draft",
    ai_input=sanitize_input(prompt_vars),
    ai_response=resolution
)
```

---

#### ❌ Pitfall 4: Not Rotating Logs

**Problem**: Log file grows unbounded

```python
# ❌ BAD: No rotation
"handlers": {
    "evals": {
        "class": "logging.FileHandler",  # Never rotates!
        "filename": "evals.log"
    }
}
# After months: evals.log is 10GB
```

**Solution**: Use RotatingFileHandler
```python
# ✅ GOOD: Automatic rotation
"handlers": {
    "evals": {
        "class": "logging.handlers.RotatingFileHandler",
        "maxBytes": 1024000,  # 1MB
        "backupCount": 2
    }
}
```

---

#### ❌ Pitfall 5: Blocking I/O

**Problem**: Synchronous logging blocks agent

```python
# ❌ BAD: Synchronous file write
def record_ai_response(target, ai_input, ai_response):
    with open("evals.log", "a") as f:  # Blocks!
        f.write(json.dumps(...))
```

**Solution**: Use logging library (async)
```python
# ✅ GOOD: Async logging
async def record_ai_response(target, ai_input, ai_response):
    logger.info("AI Response", extra={...})
    # Logging library handles async I/O
```

---

### Testing Evaluation Recording

**Test that logging works**:

```python
import pytest
import json
import os
from utils.save_for_eval import record_ai_response

@pytest.mark.asyncio
async def test_record_ai_response():
    """Test that AI responses are logged correctly."""
    # Record a test interaction
    await record_ai_response(
        target="test_draft",
        ai_input={"dispute claim": "test_topic"},
        ai_response={"output": "test_output"}
    )

    # Verify log entry
    assert os.path.exists("evals.log")

    with open("evals.log") as f:
        lines = f.readlines()
        last_entry = json.loads(lines[-1])

        assert last_entry['target'] == "test_draft"
        assert last_entry['ai_input']['dispute claim'] == "test_topic"
        assert last_entry['ai_response']['output'] == "test_output"

@pytest.mark.asyncio
async def test_log_rotation():
    """Test that logs rotate at max size."""
    # Write entries until rotation triggers
    for i in range(1000):
        await record_ai_response(
            f"test_{i}",
            ai_input={"data": "x" * 1000},  # 1KB per entry
            ai_response={"data": "y" * 1000}
        )

    # Check that backup file was created
    assert os.path.exists("evals.log.1")
```

---

### Integration with Other Services

**Evaluation Recording composes with all services**:

```python
async def full_workflow_with_logging(dispute claim: str) -> Resolution:
    # 1. Guardrails: Validate
    if not await guardrail.is_acceptable(dispute claim):
        # Log rejection
        await evals.record_ai_response(
            "guardrail_rejection",
            ai_input={"dispute claim": dispute claim},
            ai_response={"rejected": True, "reason": "inappropriate"}
        )
        raise ValueError("Topic rejected")

    # 2. Long-term Memory: Retrieve
    memories = search_relevant_memories(dispute claim)

    # 3. Prompt Service: Render
    prompt = PromptService.render_prompt("dispute_resolver", dispute_claim=claim, memories=memories)

    # 4. Generate resolution
    resolution = await resolver.resolve_dispute(dispute claim)

    # 5. Evaluation Recording: Log (already done in resolver.resolve_dispute())
    # Additional custom logging:
    await evals.record_ai_response(
        "workflow_complete",
        ai_input={"dispute claim": dispute claim, "memories_used": len(memories)},
        ai_response={"resolution_id": resolution.title, "word_count": len(resolution.full_text.split())}
    )

    return resolution
```

**Complete observability**:
```
Guardrail decision → evals.log (rejection)
Memory retrieval → (not logged, but could be)
Prompt rendering → prompts.log (separate file)
Resolution generation → evals.log (initial_draft)
Workflow completion → evals.log (workflow_complete)
```

---

### Advanced Pattern: LLM-as-Judge Evaluation

**Use LLM to evaluate logged outputs**:

```python
async def llm_judge_quality(resolution: Resolution) -> dict:
    """Use LLM to evaluate resolution quality."""
    judge_prompt = f"""Evaluate this resolution on a scale of 1-5:

Title: {resolution.title}
Content: {resolution.full_text}

Rate on:
1. Accuracy (1-5)
2. Clarity (1-5)
3. Completeness (1-5)
4. Age-appropriateness for 9th transaction category (1-5)

Return JSON: {{"accuracy": X, "clarity": X, "completeness": X, "age_appropriate": X}}
"""

    from pydantic_ai import Agent
    from utils import llms

    judge = Agent(llms.SMALL_MODEL, output_type=dict)
    result = await judge.run(judge_prompt)

    return result.output

# Batch evaluate all drafts
async def evaluate_all_drafts():
    drafts = get_records("initial_draft")

    for draft_log in drafts:
        resolution = eval(draft_log['ai_response'])
        scores = await llm_judge_quality(resolution)

        print(f"{resolution.title}:")
        print(f"  Accuracy: {scores['accuracy']}/5")
        print(f"  Clarity: {scores['clarity']}/5")
        print(f"  Completeness: {scores['completeness']}/5")
```

---

### Further Reading

- **Code reference**: [`utils/save_for_eval.py`](../../utils/save_for_eval.py)
- **Example evaluation**: [`evals/evaluate_keywords.py`](../../evals/evaluate_keywords.py)
- **Logging config**: [`logging.json`](../../logging.json)
- **Book chapter**: *Generative AI Design Patterns*, Chapter 30 (Observability)

---

## 🏦 Real-World Scenario 2: Wire Transfer Fraud Detection

**Context**: Customer initiates $50,000 wire transfer to unfamiliar account. Rush request outside normal business hours. Transaction flagged by fraud detection system.

**Business Requirements**:
- ✅ High-stakes decision (large amount + irreversible transaction)
- ✅ Multi-agent coordination (6 specialists review in parallel)
- ✅ Comprehensive audit trail (FDIC + Suspicious Activity Report requirements)
- ✅ Human oversight mandatory (>$10,000 threshold)

### Step-by-Step Workflow

This scenario demonstrates **Multi-Agent + Horizontal Services** for high-stakes decisions:

#### 1. Initial Fraud Detection (Guardrails)

```python
# dispute_resolution_app/utils/guardrails.py
from dispute_resolution_app.utils.guardrails import InputGuardrail

# Guardrail 1: Transaction Velocity Check
velocity_guardrail = InputGuardrail(
    name="transaction_velocity",
    accept_condition="""The transaction is within normal velocity limits:
    - Daily transfer limit not exceeded
    - Weekly transfer count within normal range
    - Transfer amount consistent with historical pattern
    """
)

# Guardrail 2: Fraud Threshold
fraud_threshold_guardrail = InputGuardrail(
    name="fraud_risk_threshold",
    accept_condition="""The transaction does not exhibit fraud indicators:
    - Recipient account is recognized or verified
    - Transfer timing is within normal business hours
    - Customer contact information is current
    - No recent account compromise indicators
    """
)

wire_transfer_request = {
    "customer_id": "CUST_92847",
    "amount": 50000.00,
    "recipient_account": "9284756291",
    "recipient_bank": "International Bank Ltd (Cayman Islands)",
    "recipient_name": "Global Investments LLC",
    "request_time": "2025-01-05T02:15:00Z",  # 2:15 AM
    "customer_note": "Urgent business investment opportunity",
    "historical_transfers_to_recipient": 0
}

# Parallel validation
velocity_ok, fraud_ok = await asyncio.gather(
    velocity_guardrail.is_acceptable(str(wire_transfer_request), raise_exception=False),
    fraud_threshold_guardrail.is_acceptable(str(wire_transfer_request), raise_exception=False)
)

# Results:
# velocity_ok = True (within daily limit)
# fraud_ok = False 🔴 (unfamiliar recipient, offshore bank, off-hours timing)
```

**Guardrails outcome**: 🔴 High fraud risk detected → Escalate to CompliancePanel

---

#### 2. Memory Retrieval for Pattern Analysis

```python
# dispute_resolution_app/utils/long_term_memory.py
from dispute_resolution_app.utils.long_term_memory import search_relevant_memories

# Query 1: Similar fraud patterns
similar_fraud = search_relevant_memories(
    query="Wire transfer Cayman Islands offshore urgent investment",
    category="fraud_patterns",
    limit=10
)

# Query 2: Customer history
customer_pattern = search_relevant_memories(
    query=f"Customer {wire_transfer_request['customer_id']} wire transfer history",
    metadata_filter={"customer_id": wire_transfer_request['customer_id']},
    limit=20
)

# Results:
# similar_fraud = [
#     "Cayman Islands wire transfers: 75% confirmed fraud",
#     "Urgent investment opportunities: 90% scam pattern",
#     "Off-hours large transfers: 65% unauthorized",
#     "Pattern: Customer pressured by scammer via phone/email"
# ]
#
# customer_pattern = [
#     "Customer age 68, retired, modest account balance",
#     "Historical transfers: 3 domestic, average $800",
#     "No prior international wires",
#     "Recent phone inquiry about 'protecting savings from inflation'"
# ]
```

**Memory outcome**: 🔴 **Critical fraud indicators** - Customer profile matches elder fraud pattern

---

#### 3. Multi-Agent CompliancePanel Review

```python
# dispute_resolution_app/agents/compliance_panel.py (Illustrative - based on reviewer_panel.py pattern)
from pydantic_ai import Agent, RunContext
from dispute_resolution_app.utils.prompt_service import PromptService

# 6 specialized agents review in parallel
compliance_panel = [
    {
        "name": "Fraud Analyst",
        "focus": "Detect fraud patterns, assess transaction risk score"
    },
    {
        "name": "Compliance Officer",
        "focus": "Verify regulatory requirements (BSA/AML, FDIC)"
    },
    {
        "name": "Risk Manager",
        "focus": "Assess financial risk, recommend mitigation"
    },
    {
        "name": "Legal Reviewer",
        "focus": "Identify legal liability, SAR filing requirements"
    },
    {
        "name": "Audit Specialist",
        "focus": "Ensure audit trail completeness"
    },
    {
        "name": "Customer Advocate",
        "focus": "Consider customer intent, investigate legitimacy"
    }
]

# Each specialist gets custom prompt
async def get_specialist_review(specialist, wire_request, fraud_indicators, customer_history):
    """Get individual specialist review."""
    prompt = PromptService.render_prompt(
        f"compliance_panel_{specialist['name'].lower().replace(' ', '_')}_prompt",
        wire_request=wire_request,
        fraud_indicators=fraud_indicators,
        customer_history=customer_history,
        specialist_focus=specialist['focus']
    )

    agent = Agent(llms.BEST_MODEL, system_prompt=prompt)
    review = await agent.run(f"Review wire transfer: {wire_request['amount']}")

    # Log each specialist review
    await evals.record_ai_response(
        target=f"compliance_panel_{specialist['name']}",
        ai_input={"wire_request": wire_request, "fraud_indicators": fraud_indicators},
        ai_response=review
    )

    return {
        "specialist": specialist['name'],
        "recommendation": review.recommendation,  # APPROVE / DENY / ESCALATE
        "confidence": review.confidence,
        "rationale": review.rationale
    }

# Run all 6 specialists in parallel
specialist_reviews = await asyncio.gather(
    *[get_specialist_review(s, wire_transfer_request, similar_fraud, customer_pattern)
      for s in compliance_panel]
)

# Results:
# [
#     {"specialist": "Fraud Analyst", "recommendation": "DENY", "confidence": 0.95,
#      "rationale": "Cayman Islands + unfamiliar recipient + off-hours = elder fraud pattern"},
#     {"specialist": "Compliance Officer", "recommendation": "DENY", "confidence": 0.92,
#      "rationale": "SAR filing required. Recommend customer contact verification"},
#     {"specialist": "Risk Manager", "recommendation": "DENY", "confidence": 0.88,
#      "rationale": "Risk exceeds tolerance. $50k loss exposure with high fraud probability"},
#     {"specialist": "Legal Reviewer", "recommendation": "DENY", "confidence": 0.90,
#      "rationale": "Potential liability if transfer proceeds. SAR + law enforcement notification"},
#     {"specialist": "Audit Specialist", "recommendation": "DENY", "confidence": 0.87,
#      "rationale": "Audit trail requires customer verification call recording"},
#     {"specialist": "Customer Advocate", "recommendation": "ESCALATE", "confidence": 0.75,
#      "rationale": "Contact customer directly to verify legitimacy. May be elder abuse"}
# ]
```

**Panel outcome**: **6/6 specialists recommend DENY** (5 DENY, 1 ESCALATE to customer contact)

---

#### 4. Secretary Agent Consolidation

```python
# Consolidate panel feedback
secretary_prompt = PromptService.render_prompt(
    "compliance_panel_secretary_prompt",
    specialist_reviews=specialist_reviews,
    wire_request=wire_transfer_request
)

secretary = Agent(llms.BEST_MODEL, system_prompt=secretary_prompt)
final_resolution = await secretary.run("Consolidate panel reviews and provide final recommendation")

# Final resolution:
# {
#     "verdict": "DENY",
#     "confidence": 0.92,
#     "unanimous": False,  # 5 DENY, 1 ESCALATE
#     "key_concerns": [
#         "Elder fraud pattern (68-year-old customer, offshore bank, urgent request)",
#         "Customer history: No prior international wires",
#         "Fraud indicators: 75% Cayman Islands transfers are fraud",
#         "SAR filing required per BSA/AML"
#     ],
#     "required_actions": [
#         "DENY transfer immediately",
#         "Contact customer via verified phone to confirm legitimacy",
#         "File Suspicious Activity Report (SAR)",
#         "Notify law enforcement if customer confirms coercion"
#     ],
#     "customer_communication": "We've placed a temporary hold on your wire transfer for security verification.
A fraud specialist will call you within 1 hour at your verified phone number to confirm this transaction."
# }

# Log final resolution
await evals.record_ai_response(
    target="compliance_panel_final_resolution",
    ai_input={
        "wire_request": wire_transfer_request,
        "specialist_reviews": specialist_reviews
    },
    ai_response=final_resolution
)
```

**Consolidation outcome**: ✅ Unanimous DENY recommendation with clear action plan

---

#### 5. Human Oversight (Mandatory for >$10k)

```python
# dispute_resolution_app/utils/human_feedback.py
from dispute_resolution_app.utils/human_feedback import record_human_feedback

# High-value transaction requires senior compliance officer approval
print(f"⚠️  MANDATORY REVIEW: Wire transfer ${wire_transfer_request['amount']:,}")
print(f"   Panel recommendation: {final_resolution['verdict']}")
print(f"   Fraud confidence: {final_resolution['confidence']*100:.0f}%")

# Senior compliance officer reviews AI panel decision
# In production: Escalate to senior officer, halt transaction pending review

senior_officer_decision = {
    "verdict": "DENY",  # Agrees with panel
    "additional_actions": [
        "Contact customer immediately via verified phone",
        "File SAR with FinCEN",
        "Flag account for 48-hour enhanced monitoring",
        "If customer confirms legitimacy, require in-person verification"
    ],
    "officer_id": "SENIOR_OFFICER_12",
    "timestamp": "2025-01-05T02:27:00Z",
    "notes": "Clear elder fraud pattern. Customer protection paramount. Initiate immediate customer contact."
}

# Log human feedback (override or confirmation)
record_human_feedback(
    target="wire_transfer_fraud_decision",
    ai_input=wire_transfer_request,
    ai_response=final_resolution["verdict"],
    human_choice=senior_officer_decision["verdict"],
    metadata={
        "officer_id": senior_officer_decision["officer_id"],
        "additional_actions": senior_officer_decision["additional_actions"],
        "agreement": True,  # Officer agrees with AI panel
        "fraud_confidence": final_resolution["confidence"]
    }
)

# ✅ Logged to feedback.log with full audit trail
```

**Human Oversight outcome**: ✅ Senior officer confirmed DENY decision, ordered immediate customer contact

---

### Business Value Delivered

**Fraud Prevention**:
- ✅ **$50,000 fraud prevented** (high confidence based on fraud patterns)
- ✅ Elder fraud pattern detected (68-year-old, offshore bank, urgent pressure)
- ✅ Customer protected from potential scam

**Regulatory Compliance**:
- ✅ SAR filing initiated (Bank Secrecy Act / Anti-Money Laundering)
- ✅ Complete audit trail for FDIC review
- ✅ Human oversight for high-stakes decision (>$10k)
- ✅ Law enforcement notification prepared

**Customer Protection**:
- ✅ Transaction halted within 12 minutes of request
- ✅ Proactive customer contact to verify legitimacy
- ✅ Account monitoring enhanced for 48 hours
- ✅ Clear communication to customer (security hold, fraud specialist callback)

**Operational Efficiency**:
- ✅ **6 specialists reviewed in parallel**: 3 minutes total (vs. 30 minutes sequential)
- ✅ Unanimous recommendation: High confidence for senior officer
- ✅ Automated SAR preparation: Reduces compliance officer workload
- ✅ Complete audit trail: Ready for regulatory inspection

**Cost Analysis**:
- Multi-agent coordination: 6 LLM calls × $0.05 = $0.30
- Guardrails validation: $0.02
- Memory retrieval: $0.01
- Secretary consolidation: $0.05
- **Total cost per high-risk wire**: ~$0.38 (vs. $50,000 fraud loss prevented)
- **ROI**: 131,000x cost-benefit ratio

**Key Insight**: Horizontal services enable **sophisticated multi-agent workflows** at production scale. CompliancePanel coordination (6 specialists) + evaluation logging + human oversight = comprehensive fraud prevention with full regulatory compliance.

---

## Human Feedback (Detailed)

### Overview: Pattern 33 - Human-in-the-Loop

**Core principle**: Capture human corrections and preferences when they override or modify AI decisions, enabling the system to learn from human expertise.

**Key capabilities**:
1. **Override Tracking**: Record when humans choose differently than AI suggests
2. **Modification Logging**: Track how humans edit AI-generated content
3. **Preference Learning**: Identify patterns in human corrections
4. **Quality Signals**: Use human choices as ground truth for evaluation
5. **Model Improvement**: Collect training data from human feedback

**Benefits**:
- 👤 **Human expertise**: Leverage domain knowledge to improve AI
- 🎯 **Better suggestions**: Learn which suggestions users accept/reject
- 📊 **Quality metrics**: Human choices indicate AI accuracy
- 🔄 **Continuous improvement**: System gets better with use
- 🧠 **Implicit feedback**: No explicit rating needed, actions speak
- 🛠️ **Debugging**: Understand where AI fails to match user expectations

**Code reference**: [`dispute_resolution_app/utils/human_feedback.py`](../../utils/human_feedback.py)

**Technology**: Python's `logging` module (same as Evaluation Recording)

---

### Implementation: record_human_feedback()

From [`utils/human_feedback.py:5-12`](../../utils/human_feedback.py#L5-L12):

```python
import logging

logger = logging.getLogger(__name__)

def record_human_feedback(target, ai_input, ai_response, human_choice):
    """Record when a human overrides or modifies an AI decision.

    Args:
        target: Identifier for the operation (e.g., "assigned_resolver", "initial_draft")
        ai_input: Original input that led to AI decision
        ai_response: What the AI produced/suggested
        human_choice: What the human chose/modified instead

    Example:
        # AI suggested GenAI DisputeResolver, user chose WireTransferResolver
        record_human_feedback(
            target="assigned_resolver",
            ai_input="unauthorized international transaction",
            ai_response="CARD_DISPUTE_RESOLVER",
            human_choice="WIRE_TRANSFER_RESOLVER"
        )
    """
    logger.info(f"HumanFeedback", extra={
        "target": target,
        "ai_input": ai_input,
        "ai": ai_response,
        "human": human_choice,
    })
```

**Key design**:
- **4 parameters**: Target, input, AI output, human choice
- **Parallel to evals**: Same pattern as `record_ai_response()`
- **Separate log file**: Goes to `feedback.log` (not `evals.log`)
- **Implicit feedback**: Records actions, not explicit ratings

---

### Logging Configuration

From [`logging.json:35-42, 68-72`](../../logging.json#L35-L42):

```json
{
  "handlers": {
    "feedback": {
      "class": "logging.handlers.RotatingFileHandler",
      "level": "DEBUG",
      "formatter": "json",
      "filename": "feedback.log",
      "maxBytes": 1024000,
      "backupCount": 2
    }
  },
  "loggers": {
    "utils.human_feedback": {
      "handlers": ["feedback"],
      "level": "DEBUG",
      "propagate": true
    }
  }
}
```

**Configuration features**:
- **Separate log file**: `feedback.log` (distinct from `evals.log`)
- **JSON formatted**: Same structure as evaluation logs
- **Rotating**: Auto-rotates at 1MB
- **Propagates**: Also logs to console for visibility

---

### Log Format

**Example log entry** (feedback.log):

```json
{
  "asctime": "2025-01-05 10:30:45,123",
  "levelname": "INFO",
  "name": "utils.human_feedback",
  "message": "HumanFeedback",
  "target": "assigned_resolver",
  "ai_input": "unauthorized international transaction",
  "ai": "CARD_DISPUTE_RESOLVER",
  "human": "WIRE_TRANSFER_RESOLVER"
}
```

**Fields explained**:
- `target`: What decision was being made
- `ai_input`: Context for the decision
- `ai`: What the AI suggested/generated
- `human`: What the human chose/modified

**Difference from evals.log**:
- **evals.log**: AI → output (no human involvement)
- **feedback.log**: AI → human override (human-in-the-loop)

---

### Integration in Streamlit UI

#### Integration 1: DisputeResolver Assignment Override

From [`pages/1_AssignToResolver.py:16-36`](../../pages/1_AssignToResolver.py#L16-L36):

```python
def assign_to_resolver():
    """Page where user selects resolver type for resolution."""
    dispute claim = st.session_state.dispute claim

    # AI suggests a resolver
    suggested_resolver = find_resolver(dispute claim)  # TaskAssigner suggests
    st.write(f"Suggested option is {suggested_resolver.name}")

    # User can override suggestion
    options = [resolver.name for resolver in list(DisputeResolver)]
    resolver_selection = st.selectbox(
        label="Choose DisputeResolver:",
        options=options,
        index=list(DisputeResolver).index(suggested_resolver)
    )

    if st.button("Next"):
        # Log if user chose differently
        if suggested_resolver.name != resolver_selection:
            record_human_feedback(
                target="assigned_resolver",
                ai_input=dispute claim,
                ai_response=suggested_resolver.name,
                human_choice=resolver_selection
            )

        # Continue with user's choice
        resolver = DisputeResolver(resolver_selection)
        st.session_state.resolver = ResolverFactory.create_resolver(resolver)
        st.switch_page("pages/2_CreateResolution.py")
```

**What's logged**:
- **Target**: `"assigned_resolver"`
- **AI input**: Topic (e.g., "unauthorized international transaction")
- **AI response**: Suggested resolver (e.g., "CARD_DISPUTE_RESOLVER")
- **Human choice**: User's selection (e.g., "WIRE_TRANSFER_RESOLVER")

**Only logs if override**: If user accepts suggestion, nothing is logged (implicit agreement)

---

#### Integration 2: Draft Modification

From [`pages/2_CreateResolution.py:24-76`](../../pages/2_CreateResolution.py#L24-L76):

```python
def write_draft():
    """Page where user reviews and edits AI-generated draft."""
    dispute_claim = st.session_state.dispute_claim
    resolver = st.session_state.resolver

    # AI generates draft
    ai_generated_draft = resolve_dispute(resolver.name(), dispute_claim)
    st.session_state.ai_generated_draft = ai_generated_draft
    st.session_state.draft = dataclasses.replace(ai_generated_draft)  # Editable copy

    # User can edit in text areas
    draft_title = st.text_area("Title", value=st.session_state.draft.title)
    draft_lesson = st.text_area("Lesson", value=st.session_state.draft.key_lesson)
    draft_text = st.text_area("Text", value=st.session_state.draft.full_text, height=400)
    draft_keywords = st.text_area("Keywords", value=keywords_to_string(st.session_state.draft))

    # User can also modify via chat
    with st.form("Modification form"):
        st.text_input(label="Modification instructions", key="modify_instruction")
        st.form_submit_button(label="Modify", on_click=modify_draft)

    if st.button("Next"):
        # Capture edits from UI
        st.session_state.draft.title = draft_title
        st.session_state.draft.key_lesson = draft_lesson
        st.session_state.draft.full_text = draft_text
        st.session_state.draft.index_keywords = draft_keywords.split('\n')

        # Log if user modified the draft
        if st.session_state.draft != st.session_state.ai_generated_draft:
            record_human_feedback(
                target="initial_draft",
                ai_input=dispute claim,
                ai_response=st.session_state.ai_generated_draft,
                human_choice=st.session_state.draft
            )

        st.switch_page("pages/3_PanelReview1.py")
```

**What's logged**:
- **Target**: `"initial_draft"`
- **AI input**: Topic
- **AI response**: Original AI-generated Resolution object
- **Human choice**: User-modified Resolution object

**Modification detection**: Compares original vs. edited using dataclass equality

---

### Use Cases

#### Use Case 1: Measuring AI Accuracy

**How often do users accept AI suggestions?**

```python
def calculate_acceptance_rate():
    """Measure how often users accept vs. override AI suggestions."""
    overrides = 0
    total_interactions = 0

    # Count overrides
    with open("feedback.log") as f:
        for line in f:
            obj = json.loads(line)
            if obj['target'] == 'assigned_resolver':
                overrides += 1

    # Count total AI suggestions (from evals.log)
    with open("evals.log") as f:
        for line in f:
            obj = json.loads(line)
            if obj['target'] == 'find_resolver':
                total_interactions += 1

    acceptance_rate = 1.0 - (overrides / total_interactions)
    print(f"Acceptance rate: {acceptance_rate:.1%}")
    print(f"Override rate: {(1 - acceptance_rate):.1%}")
    print(f"{overrides} overrides out of {total_interactions} suggestions")

# Example output:
# Acceptance rate: 73.5%
# Override rate: 26.5%
# 34 overrides out of 128 suggestions
```

---

#### Use Case 2: Learning User Preferences

**Which resolver types do users prefer for specific dispute claims?**

```python
def analyze_resolver_preferences():
    """Identify patterns in resolver selection overrides."""
    patterns = {}

    with open("feedback.log") as f:
        for line in f:
            obj = json.loads(line)
            if obj['target'] == 'assigned_resolver':
                dispute claim = obj['ai_input']
                ai_suggested = obj['ai']
                user_chose = obj['human']

                key = (dispute claim, ai_suggested, user_chose)
                patterns[key] = patterns.get(key, 0) + 1

    print("Top override patterns:")
    for (dispute claim, ai, human), count in sorted(patterns.items(), key=lambda x: x[1], reverse=True)[:10]:
        print(f"  {count}x: {dispute claim} → AI suggested {ai}, user chose {human}")

# Example output:
# Top override patterns:
#   12x: Wire Transfer Fraud → AI suggested CARD_DISPUTE_RESOLVER, user chose WIRE_TRANSFER_RESOLVER
#   8x: Unauthorized International Transaction → AI suggested CARD_DISPUTE_RESOLVER, user chose CARD_DISPUTE_RESOLVER (no override logged)
#   7x: Recurring Subscription Charge → AI suggested CARD_DISPUTE_RESOLVER, user chose ACH_DISPUTE_RESOLVER
#   ...
```

**Insight**: Users consistently prefer WIRE_TRANSFER_RESOLVER for international transaction disputes and ACH_DISPUTE_RESOLVER for recurring payment disputes, even when AI suggests CARD_DISPUTE_RESOLVER.

**Action**: Update TaskAssigner logic or training data to match user preferences.

---

#### Use Case 3: Identifying Common Edits

**What parts of resolutions do users edit most?**

```python
def analyze_draft_edits():
    """Identify which resolution fields users modify most often."""
    edit_stats = {
        "title": 0,
        "key_lesson": 0,
        "full_text": 0,
        "keywords": 0
    }
    total_edits = 0

    with open("feedback.log") as f:
        for line in f:
            obj = json.loads(line)
            if obj['target'] == 'initial_draft':
                ai_draft = eval(obj['ai'])
                human_draft = eval(obj['human'])

                total_edits += 1

                # Check which fields changed
                if ai_draft.title != human_draft.title:
                    edit_stats["title"] += 1
                if ai_draft.key_lesson != human_draft.key_lesson:
                    edit_stats["key_lesson"] += 1
                if ai_draft.full_text != human_draft.full_text:
                    edit_stats["full_text"] += 1
                if ai_draft.index_keywords != human_draft.index_keywords:
                    edit_stats["keywords"] += 1

    print(f"Out of {total_edits} edited drafts:")
    for field, count in sorted(edit_stats.items(), key=lambda x: x[1], reverse=True):
        print(f"  {field}: {count} edits ({count/total_edits:.1%})")

# Example output:
# Out of 45 edited drafts:
#   full_text: 42 edits (93.3%)
#   keywords: 28 edits (62.2%)
#   key_lesson: 15 edits (33.3%)
#   title: 8 edits (17.8%)
```

**Insight**: Users edit full_text most often, suggesting AI needs improvement in content generation. Keywords also frequently edited.

---

#### Use Case 4: Training Data from Corrections

**Collect human-corrected examples for fine-tuning**:

```python
def collect_corrected_examples():
    """Extract training data from human corrections."""
    training_pairs = []

    with open("feedback.log") as f:
        for line in f:
            obj = json.loads(line)
            if obj['target'] == 'initial_draft':
                ai_draft = eval(obj['ai'])
                human_draft = eval(obj['human'])

                # Create training example
                training_pairs.append({
                    "input": {
                        "dispute claim": obj['ai_input'],
                        "instruction": "Write an resolution for 9th transaction category customers"
                    },
                    "ai_output": ai_draft.full_text,
                    "human_correction": human_draft.full_text,
                    "metadata": {
                        "timestamp": obj['asctime'],
                        "edit_type": "full_rewrite" if len(human_draft.full_text) < len(ai_draft.full_text) * 0.5 else "refinement"
                    }
                })

    print(f"Collected {len(training_pairs)} human-corrected examples")
    return training_pairs

# Save for fine-tuning
corrections = collect_corrected_examples()
with open("human_corrections.jsonl", "w") as f:
    for pair in corrections:
        f.write(json.dumps(pair) + "\n")
```

**Use case**: Fine-tune model to generate content more aligned with human preferences.

---

#### Use Case 5: A/B Testing AI Improvements

**Compare acceptance rates before/after model update**:

```python
def compare_model_versions():
    """Compare user acceptance before and after model improvement."""
    # Split feedback by date (before/after model update)
    before_date = "2025-01-01"
    after_date = "2025-02-01"

    before_overrides = 0
    before_total = 0
    after_overrides = 0
    after_total = 0

    with open("feedback.log") as f:
        for line in f:
            obj = json.loads(line)
            if obj['target'] == 'assigned_resolver':
                timestamp = obj['asctime']

                if timestamp < before_date:
                    continue  # Too old
                elif timestamp < after_date:
                    before_overrides += 1
                    before_total += 1
                else:
                    after_overrides += 1
                    after_total += 1

    # Calculate acceptance rates
    before_acceptance = 1.0 - (before_overrides / max(before_total, 1))
    after_acceptance = 1.0 - (after_overrides / max(after_total, 1))

    print(f"Before update: {before_acceptance:.1%} acceptance rate")
    print(f"After update: {after_acceptance:.1%} acceptance rate")
    print(f"Improvement: {(after_acceptance - before_acceptance):.1%}")

# Example output:
# Before update: 68.2% acceptance rate
# After update: 78.5% acceptance rate
# Improvement: +10.3%
```

---

### Difference: Human Feedback vs. Evaluation Recording

| Aspect | Evaluation Recording | Human Feedback |
|--------|---------------------|----------------|
| **What's logged** | AI input → AI output | AI input → AI output → Human override |
| **Purpose** | Track all AI interactions | Track when humans disagree with AI |
| **Log file** | `evals.log` | `feedback.log` |
| **Frequency** | Every AI operation | Only when human overrides |
| **Use case** | Quality metrics, debugging | Preference learning, training data |
| **Example** | DisputeResolver generates resolution | User edits resolution |

**Relationship**:
- **Evaluation**: "What did the AI do?"
- **Feedback**: "Did the human accept it?"

**Combined analysis**:
```python
# Find AI outputs that were most often corrected
def find_problematic_outputs():
    """Identify AI outputs that users frequently override."""
    ai_outputs = {}  # target → list of outputs
    human_overrides = {}  # target → list of overrides

    # Load all AI outputs
    with open("evals.log") as f:
        for line in f:
            obj = json.loads(line)
            target = obj['target']
            if target not in ai_outputs:
                ai_outputs[target] = []
            ai_outputs[target].append(obj)

    # Load all human overrides
    with open("feedback.log") as f:
        for line in f:
            obj = json.loads(line)
            target = obj['target']
            if target not in human_overrides:
                human_overrides[target] = []
            human_overrides[target].append(obj)

    # Calculate override rate by target
    for target in ai_outputs:
        total = len(ai_outputs[target])
        overrides = len(human_overrides.get(target, []))
        override_rate = overrides / total if total > 0 else 0

        print(f"{target}: {override_rate:.1%} override rate ({overrides}/{total})")

# Example output:
# assigned_resolver: 26.5% override rate (34/128)
# initial_draft: 35.2% override rate (45/128)
```

---

### Integration with Long-term Memory

**Use human feedback to improve future suggestions**:

```python
# In pages/2_CreateResolution.py:45-56
def modify_draft():
    """User provides modification instructions via chat."""
    modify_instruction = st.session_state.modify_instruction

    # Revise resolution based on user feedback
    draft = patched_asyncio.run(
        resolver.revise_resolution(dispute claim, st.session_state.draft, modify_instruction)
    )

    # Store instruction in long-term memory
    # This will be retrieved in future writes!
    ltm.add_to_memory(modify_instruction, metadata={
        "dispute claim": dispute claim,
        "resolver": resolver.name()
    })

    st.session_state.draft = draft
```

**Feedback loop**:
```
User modifies draft
→ Instruction stored in Long-term Memory
→ Next resolution retrieves instruction
→ AI applies learned preference automatically
```

**Example**:
1. User writes: "Use more examples from real life"
2. Stored in memory
3. Next resolution automatically includes more examples
4. User satisfaction improves, fewer overrides

---

### Common Pitfalls

#### ❌ Pitfall 1: Logging Every Interaction

**Problem**: Logging too much noise

```python
# ❌ BAD: Log even when no override
if st.button("Next"):
    record_human_feedback(
        "assigned_resolver",
        dispute claim,
        suggested_resolver,
        resolver_selection  # Same as suggested!
    )
```

**Solution**: Only log overrides
```python
# ✅ GOOD: Only log if different
if st.button("Next"):
    if suggested_resolver.name != resolver_selection:
        record_human_feedback(...)
```

---

#### ❌ Pitfall 2: Not Capturing Original AI Output

**Problem**: Can't compare human vs. AI

```python
# ❌ BAD: Lost original AI output
st.session_state.draft = resolve_dispute(dispute claim)  # Overwrites original

if st.button("Next"):
    # Can't compare - original is lost!
    record_human_feedback("initial_draft", dispute claim, ???, current_draft)
```

**Solution**: Keep copy of original
```python
# ✅ GOOD: Preserve original
ai_generated_draft = resolve_dispute(dispute claim)
st.session_state.ai_generated_draft = ai_generated_draft  # Keep original
st.session_state.draft = dataclasses.replace(ai_generated_draft)  # Editable copy

if st.button("Next"):
    if st.session_state.draft != st.session_state.ai_generated_draft:
        record_human_feedback(
            "initial_draft",
            dispute claim,
            st.session_state.ai_generated_draft,  # Original
            st.session_state.draft  # Modified
        )
```

---

#### ❌ Pitfall 3: Not Acting on Feedback

**Problem**: Collecting feedback but not using it

```python
# ❌ BAD: Just logging, no action
record_human_feedback(...)
# Feedback sits in logs forever, never analyzed
```

**Solution**: Regularly analyze and act
```python
# ✅ GOOD: Scheduled analysis
# Weekly cron job:
def analyze_weekly_feedback():
    patterns = analyze_resolver_preferences()

    # Update model or logic based on patterns
    if patterns["prefer_historian_for_history"] > 0.8:
        # Update TaskAssigner to prefer WIRE_TRANSFER_RESOLVER for history dispute claims
        update_resolver_routing_rules(patterns)

    # Collect training data
    corrections = collect_corrected_examples()
    if len(corrections) >= 100:
        # Fine-tune model
        trigger_model_retraining(corrections)
```

---

#### ❌ Pitfall 4: No Feedback UI

**Problem**: Users can't provide feedback easily

```python
# ❌ BAD: No way to override
suggested_resolver = find_resolver(dispute claim)
st.write(f"Using {suggested_resolver}")  # User has no choice!
```

**Solution**: Always allow override
```python
# ✅ GOOD: Dropdown to override
suggested_resolver = find_resolver(dispute claim)
st.write(f"Suggested: {suggested_resolver}")

user_choice = st.selectbox(
    "Choose resolver:",
    options=all_resolvers,
    index=all_resolvers.index(suggested_resolver)
)
```

---

#### ❌ Pitfall 5: Privacy Violations

**Problem**: Logging user PII in feedback

```python
# ❌ BAD: User email in logs
record_human_feedback(
    "draft_edit",
    ai_input={"dispute claim": dispute claim, "user_email": "compliance officer@bankingcorp.com"},  # PII!
    ai_response=draft,
    human_choice=edited_draft
)
```

**Solution**: Sanitize before logging
```python
# ✅ GOOD: Remove PII
def sanitize_input(data):
    sensitive = ["email", "user_id", "ip_address"]
    return {k: v for k, v in data.items() if k not in sensitive}

record_human_feedback(
    "draft_edit",
    ai_input=sanitize_input(input_data),
    ai_response=draft,
    human_choice=edited_draft
)
```

---

### Testing Human Feedback

**Test feedback recording**:

```python
import pytest
from utils.human_feedback import record_human_feedback

def test_record_human_feedback():
    """Test that human feedback is logged correctly."""
    # Record feedback
    record_human_feedback(
        target="test_override",
        ai_input="test_input",
        ai_response="ai_choice",
        human_choice="human_choice"
    )

    # Verify log entry
    with open("feedback.log") as f:
        lines = f.readlines()
        last_entry = json.loads(lines[-1])

        assert last_entry['target'] == "test_override"
        assert last_entry['ai'] == "ai_choice"
        assert last_entry['human'] == "human_choice"

def test_override_detection():
    """Test that overrides are detected correctly."""
    ai_draft = Resolution(title="AI Title", full_text="AI content")
    human_draft = Resolution(title="Human Title", full_text="AI content")

    # Should detect title change
    assert ai_draft != human_draft

    # Should not detect if identical
    identical_draft = dataclasses.replace(ai_draft)
    assert ai_draft == identical_draft
```

---

### Advanced Pattern: Reinforcement Learning from Human Feedback (RLHF)

**Use human feedback for model training**:

```python
async def rlhf_training_pipeline():
    """Collect and prepare data for RLHF."""

    # Step 1: Collect human preferences
    preferences = []
    with open("feedback.log") as f:
        for line in f:
            obj = json.loads(line)
            if obj['target'] == 'initial_draft':
                preferences.append({
                    "prompt": obj['ai_input'],
                    "chosen": obj['human'],  # Human-corrected version
                    "rejected": obj['ai']     # Original AI version
                })

    # Step 2: Create preference dataset
    # Format: {"prompt": ..., "chosen": ..., "rejected": ...}
    with open("preference_data.jsonl", "w") as f:
        for pref in preferences:
            f.write(json.dumps(pref) + "\n")

    # Step 3: Train reward model
    # (Use external RLHF library like trl)
    # reward_model = train_reward_model(preference_data)

    # Step 4: Fine-tune policy with PPO
    # policy_model = train_policy_with_ppo(base_model, reward_model)

    print(f"Collected {len(preferences)} preference pairs for RLHF")
```

**This enables**:
- Model learns to prefer human-approved outputs
- Continuous improvement from user corrections
- Personalization to specific user preferences

---

### Further Reading

- **Code reference**: [`utils/human_feedback.py`](../../utils/human_feedback.py)
- **UI integration**: [`pages/1_AssignToResolver.py`](../../pages/1_AssignToResolver.py), [`pages/2_CreateResolution.py`](../../pages/2_CreateResolution.py)
- **Logging config**: [`logging.json`](../../logging.json)
- **Book chapter**: *Generative AI Design Patterns*, Chapter 33 (Human-in-the-Loop)
- **RLHF**: [Anthropic's RLHF paper](https://arxiv.org/abs/2204.05862)

---

## Integration Points: Where Services Are Used

This section maps where each horizontal service is used across the agent codebase, helping you understand the complete integration picture.

### Service Usage Matrix

| Agent / Component | Prompt Service | Guardrails | Long-term Memory | Evaluation Recording | Human Feedback |
|-------------------|----------------|------------|------------------|---------------------|----------------|
| **TaskAssigner** | ✅ System prompt<br>✅ Find resolver prompt<br>✅ Guardrail condition | ✅ Input validation | ❌ | ✅ DisputeResolver assignment | ❌ |
| **AbstractResolver** | ✅ Generate resolution prompt<br>✅ Revise prompt | ❌ | ✅ Generate context<br>✅ Revise context | ✅ Initial draft<br>✅ Revised draft | ❌ |
| **ZeroshotResolver** | ✅ System prompt | ❌ | ✅ (via AbstractResolver) | ✅ (via AbstractResolver) | ❌ |
| **ReviewerAgent** | ✅ System prompt<br>✅ Review prompt | ❌ | ❌ | ✅ Individual reviews | ❌ |
| **Secretary** | ✅ System prompt<br>✅ Consolidate prompt | ❌ | ❌ | ✅ Consolidated review | ❌ |
| **Streamlit UI** | ❌ | ❌ | ✅ User instructions | ❌ | ✅ DisputeResolver override<br>✅ Draft edits |

**Legend**:
- ✅ Used in this component
- ❌ Not used in this component

---

### 1. TaskAssigner Integration

**File**: [`agents/dispute_classifier.py`](../../agents/dispute_classifier.py)

**Services used**: Prompt Service, Guardrails, Evaluation Recording

#### Service Integration Points:

```python
class TaskAssigner:
    def __init__(self, vector_index: VectorStoreIndex):
        # 1. PROMPT SERVICE: Load system prompt
        system_prompt = PromptService.render_prompt("TaskAssigner_system_prompt")

        # 2. GUARDRAILS: Create input guardrail
        self.topic_guardrail = InputGuardrail(
            name="topic_guardrail",
            accept_condition=PromptService.render_prompt("TaskAssigner_input_guardrail")
        )

        # Create classifier agent
        self.agent = Agent(llms.DEFAULT_MODEL, output_type=DisputeResolver, system_prompt=system_prompt)

    async def find_resolver(self, dispute claim: str) -> DisputeResolver:
        # 3. PROMPT SERVICE: Render find resolver prompt
        prompt = PromptService.render_prompt(
            prompt_name="TaskAssigner_assign_resolver",
            dispute claim=dispute claim
        )

        # 4. GUARDRAILS + EVALUATION: Parallel validation and classification
        _, result = await asyncio.gather(
            self.topic_guardrail.is_acceptable(dispute claim, raise_exception=True),  # Guardrail
            self.agent.run(prompt)  # LLM call
        )

        # 5. EVALUATION RECORDING: Log assignment
        await evals.record_ai_response(
            "find_resolver",
            ai_input={"dispute claim": dispute claim},
            ai_response=result.output.name
        )

        return result.output
```

**Integration summary**:
- **Line 23**: System prompt via Prompt Service
- **Line 32**: Guardrail condition via Prompt Service
- **Line 61**: Find resolver prompt via Prompt Service
- **Line 66**: Input validation via Guardrails
- **Line 69**: Classification logging via Evaluation Recording

---

### 2. AbstractResolver Integration

**File**: [`agents/generic_resolver_agent.py`](../../agents/generic_resolver_agent.py)

**Services used**: Prompt Service, Long-term Memory, Evaluation Recording

#### Integration Point 1: Writing Initial Draft

```python
async def resolve_dispute(self, dispute claim: str) -> Resolution:
    # 1. LONG-TERM MEMORY: Retrieve relevant context
    memories = ltm.search_relevant_memories(f"{self.resolver.name}, resolve dispute about {dispute claim}")

    # 2. PROMPT SERVICE: Render prompt with memories
    prompt_vars = {
        "prompt_name": "AbstractResolver_generate_resolution",
        "content_type": self.get_content_type(),
        "additional_instructions": memories,  # Injected from memory
        "dispute claim": dispute claim
    }
    prompt = PromptService.render_prompt(**prompt_vars)

    # Generate resolution
    result = await self.write_response(dispute claim, prompt)

    # 3. EVALUATION RECORDING: Log initial draft
    await evals.record_ai_response(
        "initial_draft",
        ai_input=prompt_vars,
        ai_response=result
    )

    return result
```

**Integration summary**:
- **Line 64**: Memory retrieval via Long-term Memory
- **Line 67**: Prompt rendering via Prompt Service
- **Line 69-71**: Draft logging via Evaluation Recording

---

#### Integration Point 2: Revising Resolution

```python
async def revise_resolution(
    self,
    dispute claim: str,
    initial_draft: Resolution,
    panel_review: str
) -> Resolution:
    # 1. LONG-TERM MEMORY: Retrieve revision context
    memories = ltm.search_relevant_memories(f"{self.resolver.name}, revise {dispute claim}")

    # 2. PROMPT SERVICE: Render revision prompt
    prompt_vars = {
        "prompt_name": "AbstractResolver_revise_resolution",
        "dispute claim": dispute claim,
        "content_type": self.get_content_type(),
        "additional_instructions": memories,  # Revision-specific memories
        "initial_draft": initial_draft.to_markdown(),
        "panel_review": panel_review
    }
    prompt = PromptService.render_prompt(**prompt_vars)

    result = await self.revise_response(prompt)

    # 3. EVALUATION RECORDING: Log revision
    await evals.record_ai_response(
        "revised_draft",
        ai_input=prompt_vars,
        ai_response=result
    )

    return result
```

**Integration summary**:
- **Line 80**: Memory retrieval via Long-term Memory
- **Line 84**: Prompt rendering via Prompt Service
- **Line 86-88**: Revision logging via Evaluation Recording

---

### 3. ZeroshotResolver Integration

**File**: [`agents/generic_resolver_agent.py`](../../agents/generic_resolver_agent.py)

**Services used**: Prompt Service (plus inherited services from AbstractResolver)

```python
class ZeroshotResolver(AbstractResolver):
    def __init__(self, resolver: DisputeResolver):
        super().__init__(resolver)

        # PROMPT SERVICE: Load resolver-specific system prompt
        system_prompt_file = f"{self.resolver.name}_system_prompt".lower()
        system_prompt = PromptService.render_prompt(system_prompt_file)

        self.agent = Agent(
            llms.BEST_MODEL,
            output_type=Resolution,
            model_settings=llms.default_model_settings(),
            retries=2,
            system_prompt=system_prompt
        )
```

**Integration summary**:
- **Line 96**: System prompt via Prompt Service
- **Inherits**: Long-term Memory and Evaluation Recording from AbstractResolver

---

### 4. ReviewerAgent Integration

**File**: [`agents/compliance_panel.py`](../../agents/compliance_panel.py)

**Services used**: Prompt Service, Evaluation Recording

#### Integration Point 1: Individual Reviews

```python
class ReviewerAgent:
    def __init__(self, reviewer: CompliancePanel):
        self.reviewer = reviewer

        # PROMPT SERVICE: Load reviewer system prompt
        system_prompt_file = f"{self.reviewer.name}_reviewer_system_prompt"
        system_prompt = PromptService.render_prompt(system_prompt_file)

        self.agent = Agent(llms.BEST_MODEL, system_prompt=system_prompt)

    async def review(self, dispute claim: str, resolution: Resolution, reviews_so_far: list) -> str:
        # PROMPT SERVICE: Render review prompt
        prompt_vars = {
            "prompt_name": "ReviewerAgent_review_prompt",
            "dispute claim": dispute claim,
            "resolution": resolution.to_markdown(),
            "reviews": format_reviews(reviews_so_far)
        }
        prompt = PromptService.render_prompt(**prompt_vars)

        result = await self.agent.run(prompt)

        # EVALUATION RECORDING: Log review
        await evals.record_ai_response(
            f"{self.reviewer.name}_review",
            ai_input=prompt_vars,
            ai_response=result.output
        )

        return result.output
```

**Integration summary**:
- **Line 30**: System prompt via Prompt Service
- **Line 57**: Review prompt via Prompt Service
- **Line 60-63**: Review logging via Evaluation Recording

---

### 5. Secretary Integration

**File**: [`agents/compliance_panel.py`](../../agents/compliance_panel.py)

**Services used**: Prompt Service, Evaluation Recording

```python
class Secretary:
    def __init__(self):
        # PROMPT SERVICE: Load secretary system prompt
        system_prompt = PromptService.render_prompt("secretary_system_prompt")
        self.agent = Agent(llms.BEST_MODEL, system_prompt=system_prompt)

    async def consolidate_reviews(self, reviews: list) -> str:
        # PROMPT SERVICE: Render consolidation prompt
        prompt_vars = {
            "prompt_name": "Secretary_consolidate_reviews",
            "reviews": reviews
        }
        prompt = PromptService.render_prompt(**prompt_vars)

        result = await self.agent.run(prompt)

        # EVALUATION RECORDING: Log consolidated review
        await evals.record_ai_response(
            "consolidated_review",
            ai_input=prompt_vars,
            ai_response=result.output
        )

        return result.output
```

**Integration summary**:
- **Line 68**: System prompt via Prompt Service
- **Line 92**: Consolidation prompt via Prompt Service
- **Line 95-98**: Consolidated review logging via Evaluation Recording

---

### 6. Streamlit UI Integration

**Files**: [`pages/1_AssignToResolver.py`](../../pages/1_AssignToResolver.py), [`pages/2_CreateResolution.py`](../../pages/2_CreateResolution.py)

**Services used**: Long-term Memory, Human Feedback

#### Integration Point 1: DisputeResolver Assignment Override

```python
# pages/1_AssignToResolver.py
def assign_to_resolver():
    suggested_resolver = find_resolver(dispute claim)
    user_choice = st.selectbox("Choose DisputeResolver:", options=all_resolvers)

    if st.button("Next"):
        # HUMAN FEEDBACK: Log if user overrides
        if suggested_resolver.name != user_choice:
            record_human_feedback(
                target="assigned_resolver",
                ai_input=dispute claim,
                ai_response=suggested_resolver.name,
                human_choice=user_choice
            )
```

---

#### Integration Point 2: Draft Modification

```python
# pages/2_CreateResolution.py
def write_draft():
    # Generate AI draft
    ai_draft = resolve_dispute(resolver.name(), dispute_claim)
    st.session_state.ai_generated_draft = ai_draft

    # User edits draft
    draft_text = st.text_area("Text", value=ai_draft.full_text)

    # User provides chat instruction
    def modify_draft():
        instruction = st.session_state.modify_instruction

        # Revise with instruction
        draft = resolver.revise_resolution(dispute claim, current_draft, instruction)

        # LONG-TERM MEMORY: Store instruction for future
        ltm.add_to_memory(instruction, metadata={"dispute_claim": claim, "resolver": resolver.name()})

        st.session_state.draft = draft

    if st.button("Next"):
        # HUMAN FEEDBACK: Log if user edited draft
        if st.session_state.draft != ai_draft:
            record_human_feedback(
                target="initial_draft",
                ai_input=dispute claim,
                ai_response=ai_draft,
                human_choice=st.session_state.draft
            )
```

**Integration summary**:
- **Line 32**: DisputeResolver override via Human Feedback
- **Line 50-53**: Instruction storage via Long-term Memory
- **Line 71-74**: Draft edit via Human Feedback

---

### Complete Workflow: Service Call Sequence

**Example: User requests resolution on "Unauthorized International Transaction"**

```
1. TaskAssigner.find_resolver("Unauthorized International Transaction")
   ├─ Prompt Service: Load system prompt
   ├─ Prompt Service: Load guardrail condition
   ├─ Guardrails: Validate "Unauthorized International Transaction" is banking appropriate
   ├─ Prompt Service: Render find resolver prompt
   └─ Evaluation Recording: Log resolver assignment (CARD_DISPUTE_RESOLVER)

2. User overrides to WIRE_TRANSFER_RESOLVER (in Streamlit)
   └─ Human Feedback: Log override (CARD_DISPUTE_RESOLVER → WIRE_TRANSFER_RESOLVER)

3. AbstractResolver.resolve_dispute("Unauthorized International Transaction")
   ├─ Long-term Memory: Search for relevant memories
   ├─ Prompt Service: Render resolution prompt with memories
   └─ Evaluation Recording: Log initial draft

4. User provides instruction: "Use more examples"
   └─ Long-term Memory: Store instruction

5. AbstractResolver.revise_resolution(...)
   ├─ Long-term Memory: Search for revision memories (includes "Use more examples")
   ├─ Prompt Service: Render revise prompt
   └─ Evaluation Recording: Log revised draft

6. ReviewerPanel.review_resolution(...)
   ├─ [6 ReviewerAgents in parallel]
   │  ├─ Prompt Service: Load reviewer system prompts
   │  ├─ Prompt Service: Render review prompts
   │  └─ Evaluation Recording: Log 6 individual reviews
   └─ Secretary.consolidate_reviews(...)
      ├─ Prompt Service: Load secretary system prompt
      ├─ Prompt Service: Render consolidation prompt
      └─ Evaluation Recording: Log consolidated review

7. User edits final draft (in Streamlit)
   └─ Human Feedback: Log draft modifications
```

**Total service calls**:
- Prompt Service: ~20 calls
- Guardrails: 1 call
- Long-term Memory: 3 calls (2 searches, 1 storage)
- Evaluation Recording: 10 logs
- Human Feedback: 2 logs (if user overrides)

---

### Key Takeaways

1. **Prompt Service is ubiquitous**: Every agent uses it for system prompts and prompt rendering
2. **Guardrails are selective**: Only TaskAssigner validates input (cost optimization)
3. **Long-term Memory is resolver-specific**: Only resolvers retrieve and store context
4. **Evaluation Recording is universal**: Every agent operation is logged
5. **Human Feedback is UI-specific**: Only Streamlit pages record overrides

**Design principle**: Services are **opt-in** per agent based on needs, not forced globally.

---

## 🏦 Real-World Scenario 3: ACH Dispute - Duplicate Payment

**Context**: Customer reports duplicate charge from subscription service. Two identical $49.99 debits on same day from "StreamFlix Premium".

**Business Requirements**:
- ✅ Fast resolution (common, low-risk dispute type)
- ✅ Merchant history analysis (is this merchant prone to billing errors?)
- ✅ Memory-driven decision (leverage past dispute patterns)
- ✅ Customer communication (transparent rationale)

### Step-by-Step Workflow

This scenario demonstrates **Memory Service** as the primary driver for efficient dispute resolution:

#### 1. Initial Classification (Guardrails)

```python
# dispute_resolution_app/utils/guardrails.py
from dispute_resolution_app.utils.guardrails import InputGuardrail

# Guardrail: Duplicate charge detection
duplicate_guardrail = InputGuardrail(
    name="duplicate_charge_validation",
    accept_condition="""The dispute is a valid duplicate charge claim:
    - Two or more identical charges within 48 hours
    - Same merchant and amount
    - Customer reports only authorizing one payment
    - No evidence of multiple service activations
    """
)

ach_dispute = {
    "customer_id": "CUST_45123",
    "transaction_ids": ["ACH_9472831", "ACH_9472832"],
    "merchant": "StreamFlix Premium",
    "amount": 49.99,
    "charge_dates": ["2025-01-03", "2025-01-03"],
    "customer_claim": "I was charged twice for my monthly subscription. I only authorized one payment."
}

# Validation
is_duplicate = await duplicate_guardrail.is_acceptable(str(ach_dispute), raise_exception=True)
# ✅ Valid duplicate charge claim
```

**Guardrails outcome**: ✅ Valid duplicate charge dispute

---

#### 2. Merchant History Analysis (Long-term Memory)

```python
# dispute_resolution_app/utils/long_term_memory.py
from dispute_resolution_app.utils.long_term_memory import search_relevant_memories

# Query 1: Merchant dispute history
merchant_history = search_relevant_memories(
    query=f"StreamFlix Premium duplicate charge billing errors",
    category="merchant_patterns",
    limit=20
)

# Query 2: Similar duplicate charge resolutions
similar_duplicates = search_relevant_memories(
    query="Subscription service duplicate charge resolution",
    category="dispute_resolutions",
    limit=10
)

# Results:
# merchant_history = [
#     "StreamFlix Premium: 47 duplicate charge disputes in last 6 months",
#     "Merchant dispute rate: 15% (3x industry average of 5%)",
#     "Pattern: Billing system error causes duplicate ACH debits on renewal date",
#     "Merchant responsiveness: Refunds issued in 89% of disputes",
#     "Merchant cooperation: Proactive refund policy for duplicates"
# ]
#
# similar_duplicates = [
#     "Subscription duplicate charges: 95% approved in customer favor",
#     "Average resolution time: 3 business days",
#     "Standard remedy: Full refund of duplicate charge",
#     "Merchant accountability: Billing system errors documented"
# ]
```

**Memory outcome**: 🟢 **High-confidence approval** - Merchant has documented duplicate charge pattern (15% dispute rate)

---

#### 3. Automated Resolution (Prompt Service + LLM)

```python
# dispute_resolution_app/utils/prompt_service.py
from dispute_resolution_app.utils.prompt_service import PromptService
from pydantic_ai import Agent

# Simple prompt (merchant history provides strong signal)
prompt = PromptService.render_prompt(
    "ach_duplicate_charge_resolver_prompt",
    dispute_claim=ach_dispute,
    merchant_history=merchant_history,
    similar_resolutions=similar_duplicates
)

# Rendered prompt includes:
# """
# You are an ACH dispute resolution specialist.
#
# DISPUTE CLAIM:
# - Customer: CUST_45123
# - Merchant: StreamFlix Premium
# - Amount: $49.99 × 2 (duplicate charge)
# - Customer claim: "I was charged twice for my monthly subscription. I only authorized one payment."
#
# MERCHANT HISTORY:
# - StreamFlix Premium: 47 duplicate charge disputes in 6 months
# - Dispute rate: 15% (3x industry average)
# - Pattern: Billing system error on renewal dates
# - Merchant refund rate: 89%
#
# SIMILAR RESOLUTIONS:
# - Subscription duplicates: 95% approved
# - Standard remedy: Full refund
#
# Provide resolution: APPROVE / DENY / ESCALATE
# """

# Generate resolution
agent = Agent(llms.BEST_MODEL, system_prompt=prompt)
resolution = await agent.run(f"Resolve ACH dispute: {ach_dispute['transaction_ids']}")

# Resolution output:
# {
#     "dispute_id": "DISP_11249",
#     "verdict": "APPROVE",
#     "rationale": "Merchant has documented 15% duplicate charge rate with 47 disputes in 6 months. "
#                  "Customer claim is consistent with known billing system error pattern. "
#                  "Similar disputes approved in 95% of cases.",
#     "refund_amount": 49.99,
#     "timeline": "3 business days",
#     "confidence_score": 0.97,
#     "merchant_action": "Notify merchant of recurring billing system error. Recommend system audit.",
#     "customer_communication": "We've approved your duplicate charge dispute. You'll receive a $49.99 refund "
#                                "within 3 business days. We've notified the merchant of this recurring issue."
# }
```

**Resolution outcome**: ✅ **APPROVE** with 97% confidence (memory-driven decision)

---

#### 4. Evaluation Logging (Audit Trail)

```python
# dispute_resolution_app/utils/save_for_eval.py
from dispute_resolution_app.utils.save_for_eval import Evals

# Log resolution for audit
evals = Evals(target="ach_duplicate_dispute")
await evals.record_ai_response(
    target="ach_duplicate_charge_resolution",
    ai_input={
        "dispute_claim": ach_dispute,
        "merchant_history": merchant_history,
        "similar_resolutions": similar_duplicates
    },
    ai_response=resolution
)

# ✅ Logged for regulatory review and pattern analysis
```

**Evaluation outcome**: ✅ Complete audit trail created

---

#### 5. Memory Update (Pattern Learning)

```python
# dispute_resolution_app/utils/long_term_memory.py
from dispute_resolution_app.utils.long_term_memory import add_to_memory

# Store resolution for future pattern matching
add_to_memory(
    user_message=f"StreamFlix Premium duplicate charge dispute #{ach_dispute['transaction_ids'][0]}: "
                 f"APPROVED. Merchant billing system error pattern confirmed. "
                 f"Refund ${ach_dispute['amount']} issued.",
    metadata={
        "category": "dispute_resolutions",
        "merchant": "StreamFlix Premium",
        "dispute_type": "duplicate_charge",
        "verdict": "APPROVE",
        "refund_amount": ach_dispute['amount'],
        "merchant_dispute_count": 48,  # Increment counter
        "confidence": 0.97
    }
)

# Update merchant pattern statistics
add_to_memory(
    user_message=f"StreamFlix Premium: 48 total disputes, 15.2% dispute rate (updated), "
                 f"billing system error confirmed. Recommend merchant system audit.",
    metadata={
        "category": "merchant_patterns",
        "merchant": "StreamFlix Premium",
        "total_disputes": 48,
        "dispute_rate": 0.152,
        "pattern": "duplicate_charge_billing_error"
    }
)

# ✅ Memory updated - Future disputes will benefit from this resolution
```

**Memory Update outcome**: ✅ Pattern reinforced for faster future resolutions

---

### Business Value Delivered

**Operational Efficiency**:
- ✅ **Automated resolution**: 0 human intervention required (low-risk, high-confidence)
- ✅ **Fast processing**: 8 seconds total (vs. 15 minutes manual review)
- ✅ **Memory-driven**: 97% confidence from merchant history pattern
- ✅ **Scalable**: Can handle 1000s of similar disputes per day

**Customer Experience**:
- ✅ **Immediate resolution**: Customer notified within minutes
- ✅ **Transparent rationale**: Clear explanation (merchant billing error)
- ✅ **3-day refund**: Fast remedy

**Merchant Relations**:
- ✅ **Pattern identification**: 48 disputes = clear billing system issue
- ✅ **Proactive notification**: Merchant alerted to systemic problem
- ✅ **System audit recommendation**: Helps merchant fix root cause

**Cost Analysis**:
- LLM API call: ~$0.03 (simpler prompt, strong memory signal)
- Guardrails validation: ~$0.01
- Memory retrieval: ~$0.001
- Evaluation logging: negligible
- **Total cost per duplicate dispute**: ~$0.04 (vs. $5 manual review)
- **Savings at scale**: 1000 disputes/month = $4,960 saved ($5,000 - $40)

**Key Insight**: **Long-term Memory is a force multiplier**. Once patterns are established (e.g., StreamFlix's 15% dispute rate), future resolutions are:
- **Faster** (8 seconds vs. 15 minutes)
- **Cheaper** ($0.04 vs. $5)
- **More consistent** (97% confidence vs. variable human judgment)
- **Self-improving** (each resolution strengthens the pattern)

**Merchant System Impact**: After 48 disputes, system automatically flags StreamFlix for billing system audit → Root cause fix → Dispute rate drops from 15% to 2% → Customer satisfaction improves.

---

## Common Pitfalls (All Services)

This section consolidates common pitfalls across all five horizontal services.

### Service-Specific Pitfalls

See detailed pitfalls in each service section:
- [Prompt Service Pitfalls](#common-pitfalls-and-solutions)
- [Guardrails Pitfalls](#common-pitfalls-1)
- [Long-term Memory Pitfalls](#common-pitfalls-2)
- [Evaluation Recording Pitfalls](#common-pitfalls-3)
- [Human Feedback Pitfalls](#common-pitfalls-4)

---

## Self-Assessment Questions

### Question 1: Architecture Understanding

**Q**: Why are horizontal services separated from agent code?

<details>
<summary>Click for answer</summary>

**Answer**: Four key reasons:

1. **Reusability**: All agents use the same services (no duplication)
2. **Testability**: Services can be tested in isolation
3. **Maintainability**: Fix once, benefit everywhere
4. **Composability**: Services can be mixed and matched

**Example**:
- Without separation: 5 agents × 4 services = 20 implementations
- With separation: 4 service implementations, used by all agents

**Anti-pattern**:
```python
class DisputeResolver:
    def resolve(self):
        # Inline prompt loading - can't reuse
        with open("prompt.j2") as f:
            template = f.read()

        # Inline guardrail - can't reuse
        is_safe = await llm.run("Is this safe?")

        # Every agent reimplements!
```

**Good pattern**:
```python
class DisputeResolver:
    def resolve(self):
        prompt = PromptService.render("dispute_resolver")  # Reusable
        if not await guardrail.check(input):      # Reusable
            raise ValueError()
        # Clean, modular
```
</details>

---

### Question 2: Service Interaction

**Q**: In what order should services be used in a typical workflow?

<details>
<summary>Click for answer</summary>

**Answer**: Typical order:

1. **Guardrails** (input validation) → Block bad requests early
2. **Long-term Memory** (retrieve context) → Get personalization
3. **Prompt Service** (render with context) → Build final prompt
4. **LLM Generation** → Create output
5. **Guardrails** (output validation) → Ensure quality
6. **Evaluation Recording** (log) → Track for analysis
7. **Long-term Memory** (store feedback) → Learn for next time

**Why this order?**
- Guardrails first: Save costs by rejecting before LLM call
- Memory before prompts: Context informs prompt rendering
- Evaluation last: Capture complete interaction
- Memory last: Store feedback for future

**Exception**: Order can vary based on needs. For example, some apps skip output guardrails.
</details>

---

### Question 3: Performance Trade-offs

**Q**: Which service has the highest latency? How would you optimize it?

<details>
<summary>Click for answer</summary>

**Answer**: **Guardrails** typically has highest latency (~100-300ms per check).

**Why?**
- Requires LLM API call for each validation
- Even SMALL_MODEL takes 100-300ms

**Optimization strategies**:

1. **Parallel execution**:
```python
# Run guardrail + main task concurrently
validation, result = await asyncio.gather(
    guardrail.check(input),
    agent.run(input)
)
```

2. **Caching**:
```python
@lru_cache(maxsize=1000)
def cached_guardrail(text: str) -> bool:
    return guardrail.check(text)
```

3. **Rule-based pre-filter**:
```python
# Fast rule-based check first
if len(input) > 10000 or contains_profanity(input):
    return False  # 0ms

# Expensive LLM check only if needed
return await guardrail.check(input)  # 200ms
```

4. **Batch validation**:
```python
# Validate multiple inputs in one LLM call
results = await guardrail.check_batch([input1, input2, input3])
```

**Other services**:
- Memory search: ~100-200ms (vector search)
- Prompt rendering: ~1-5ms (negligible)
- Evaluation logging: ~2-7ms (negligible)
</details>

---

### Question 4: Production Deployment

**Q**: What configuration changes are needed for production?

<details>
<summary>Click for answer</summary>

**Answer**: Critical production changes:

1. **Long-term Memory: Use persistent directory**
```python
# ❌ Dev: Temporary directory
temp_dir = tempfile.mkdtemp()

# ✅ Prod: Persistent directory
memory_dir = os.path.expanduser("~/.dispute_resolution_app/memory")
```

2. **Logging: Increase rotation limits**
```python
# ❌ Dev: 1MB rotation
"maxBytes": 1024000

# ✅ Prod: 100MB rotation
"maxBytes": 104857600
```

3. **Guardrails: Add retry logic**
```python
# ✅ Prod: Handle API failures
retries = 3
for attempt in range(retries):
    try:
        return await guardrail.check(input)
    except APIError:
        if attempt == retries - 1:
            raise
        await asyncio.sleep(2 ** attempt)
```

4. **Evaluation: Add sensitive data filtering**
```python
def sanitize(data):
    sensitive = ["email", "api_key", "password"]
    return {k: v for k, v in data.items() if k not in sensitive}
```

5. **All services: Add monitoring**
```python
# Track latency, errors, usage
await record_metric("guardrail_latency", duration_ms)
await record_metric("memory_searches", count)
```
</details>

---

**Congratulations!** You've completed the Horizontal Services tutorial. You now understand how horizontal services enable reusable, testable, and maintainable multi-agent systems through composable architecture patterns.

---

**Related Tutorials**:
- [Prompt Engineering](prompt_engineering.md) - Deep dive into Jinja2 templates
- [Multi-Agent Pattern](../notebooks/multi_agent_pattern.ipynb) - ReviewerPanel using services
- [RAG Pattern](../notebooks/rag_pattern_tutorial.ipynb) - Retrieval with evaluation
- [Evaluation Tutorial](../notebooks/evaluation_tutorial.ipynb) - Analyzing evals.log

**Book Reference**: *Generative AI Design Patterns* (Lakshmanan & Hapke, 2025)
- Chapter 17: LLM-as-Judge
- Chapter 25: Prompt as Configuration
- Chapter 28: Stateful Agents
- Chapter 30: Observability
- Chapter 32: Guardrails
