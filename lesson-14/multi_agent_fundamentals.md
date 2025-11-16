# Multi-Agent Fundamentals

**Reading Time:** 25-30 minutes
**Prerequisites:** Basic understanding of LLMs and single-agent systems
**Learning Objectives:**

- Understand what multi-agent systems are and why they matter
- Compare multi-agent vs. single-agent architectures
- Identify 4 core agent types and their responsibilities
- Explore 9 architectural components of multi-agent systems
- Design a multi-agent system for real-world use cases

---

## Introduction: What Are Multi-Agent Systems?

Multi-agent systems represent a **paradigm shift** from traditional single-agent workflows. Instead of relying on one generalist LLM to handle all aspects of a task, we assemble a **team of specialized agents** that collaborate to achieve complex objectives.

**Key Principle:**
Break down complex problems into distinct tasks handled by specialized agents, each operating with defined roles and interacting dynamically to optimize decision-making.

**Real-World Analogy:**
Think of building a house. You don't hire one person to do everything—you hire a team:

- **Architect** (Planner Agent): Designs blueprint and coordinates workflow
- **Contractor** (Manager Agent): Delegates tasks to specialists
- **Electrician, Plumber, Carpenter** (Execution Agents): Specialized workers
- **Building Inspector** (Evaluator Agent): Validates quality and compliance

Multi-agent systems apply this same principle to AI workflows.

---

## Multi-Agent vs. Single-Agent Systems

### Single-Agent System

**Characteristics:**

- One LLM handles all aspects of a task
- Monolithic architecture
- General-purpose capabilities

**Limitations:**

- **Limited specialization depth**: Jack of all trades, master of none
- **Harder to optimize** for specific domains
- **Single point of failure**: If the agent fails, the entire system fails
- **Difficult to scale**: Can't add new capabilities without retraining

**Example Workflow:**

```
User Query → Single LLM Agent → Response
```

### Multi-Agent System

**Definition:**
Multiple independent entities (agents), each with its own:

- Unique role and context
- Potentially different LLM (e.g., GPT-4 for planning, Claude for reasoning, Gemini for search)
- Specialized capabilities (domain expertise, tool access)
- Communication protocol for collaboration

**Example Workflow:**

```
User Query → Classifier Agent → Routing Decision
                ├── Domain Expert Agent 1
                ├── Domain Expert Agent 2
                └── Synthesis Agent → Response
```

---

## Six Advantages of Multi-Agent Systems

### 1. Enhanced Accuracy

**How:** Agents can **cross-check** each other's work through consensus mechanisms.

**Why It Matters:**

- Multiple perspectives reduce individual model biases
- Hallucinations can be caught by validator agents
- Majority voting or weighted consensus improves reliability

**Example:**

```python
# Three agents analyze financial risk
agent_a_risk_score = 0.72  # GPT-4
agent_b_risk_score = 0.68  # Claude
agent_c_risk_score = 0.75  # Gemini

# Consensus mechanism
average_risk = sum([agent_a_risk_score, agent_b_risk_score, agent_c_risk_score]) / 3
# Result: 0.717 (more reliable than single agent)
```

### 2. Improved Efficiency

**How:** Agents work in **parallel** on independent subtasks.

**Why It Matters:**

- Faster task completion (10-task workflow can run 10 tasks simultaneously)
- Resource optimization (use powerful models only when needed)
- Better cost management (cheap models for simple tasks, expensive models for complex reasoning)

**Example:**

```python
# Sequential (Single-Agent): 10 seconds total
task1 (2s) → task2 (3s) → task3 (5s)

# Parallel (Multi-Agent): 5 seconds total (limited by slowest task)
├── task1 (2s) ┐
├── task2 (3s) ├→ Combine results
└── task3 (5s) ┘
```

### 3. Better Handling of Complex Tasks

**How:** Large tasks broken into smaller, **manageable subtasks**.

**Why It Matters:**

- Each agent focuses on specific aspect (depth of expertise)
- Reduces cognitive load on any single model
- Enables specialized domain knowledge

**Example: Legal Document Analysis**

```
Complex Legal Query
    ├── Precedent Search Agent → Find relevant case law
    ├── Contract Analysis Agent → Identify key clauses
    ├── Compliance Agent → Check regulatory requirements
    └── Synthesis Agent → Generate comprehensive legal memo
```

### 4. Increased Scalability

**How:** Easily add more agents with new capabilities.

**Why It Matters:**

- Horizontal scaling without retraining base models
- Modular architecture (plug-and-play new agents)
- Can handle growing domains without system redesign

**Example:**

```python
# Add new capability without touching existing agents
agent_registry = {
    "legal": LegalAgent(),
    "financial": FinancialAgent(),
    "medical": MedicalAgent(),  # NEW: Just added medical domain
}
```

### 5. Improved Fault Tolerance

**How:** If one agent fails, others can **take over responsibilities**.

**Why It Matters:**

- Redundancy for critical functions
- Graceful degradation (partial functionality instead of total failure)
- System remains operational during agent maintenance

**Example:**

```python
def get_weather(location: str) -> dict:
    try:
        return primary_weather_agent.fetch(location)
    except AgentUnavailableError:
        # Fallback to backup agent
        return backup_weather_agent.fetch(location)
```

### 6. Reduced Hallucinations and Bias

**How:** Combining perspectives from multiple agents.

**Why It Matters:**

- Cross-validation of outputs (one agent checks another)
- Diverse training data reduces model-specific biases
- More reliable and trustworthy results

**Example:**

```python
# Agent A generates response
response = generation_agent.create_answer(query)

# Agent B validates for hallucinations
validation = validator_agent.check_hallucination(
    response=response,
    source_documents=context
)

if validation["has_hallucination"]:
    # Reject and regenerate
    response = generation_agent.create_answer(query, feedback=validation["issues"])
```

---

## Agent Types by Function

Multi-agent systems typically include four core agent types, each with specialized responsibilities.

### 1. Planner Agents

**Responsibility:** Breaking down high-level objectives into structured sub-tasks.

**Capabilities:**

- **Task decomposition**: Convert complex goal into actionable steps
- **Dependency analysis**: Determine which tasks must happen first
- **Resource allocation**: Assign tasks to appropriate agents

**Example: Company Retreat Planning**

```
User Goal: "Plan a company retreat for 50 employees in June"

Planner Agent Output:
1. Determine budget and headcount → Finance Agent
2. Research venue options in target location → Research Agent
3. Survey employee preferences (activities, dietary) → Survey Agent
4. Book venue and catering (depends on steps 1-3) → Booking Agent
5. Create detailed itinerary → Coordination Agent
6. Send invitations and collect RSVPs → Communication Agent
```

**Code Example:**

```python
class PlannerAgent:
    def decompose_task(self, goal: str) -> list[dict]:
        """Break complex goal into subtasks with dependencies."""
        prompt = f"""
        Goal: {goal}

        Create a task breakdown with:
        1. Task description
        2. Assigned agent type
        3. Dependencies (which tasks must complete first)
        4. Estimated duration
        """
        plan = self.llm.generate(prompt)
        return self._parse_plan(plan)
```

### 2. Retriever Agents

**Responsibility:** Optimize knowledge acquisition by dynamically fetching relevant data.

**Capabilities:**

- **Semantic search** across knowledge bases
- **API calls** to external data sources
- **Query refinement and expansion** (if initial search fails)
- **Source selection** (which database/API to use for this query)

**Example: Agentic RAG (see Lesson 14 Topic 4)**

Traditional RAG retrieves documents once. Agentic RAG uses retriever agents to **iteratively refine searches** until sufficient context is found.

**Code Example:**

```python
class RetrieverAgent:
    def retrieve_with_refinement(self, query: str, min_relevance: float = 0.7) -> list:
        """Iteratively refine search until high-quality results found."""
        results = self.semantic_search(query)

        if self._avg_relevance(results) < min_relevance:
            # Expand query and retry
            expanded_query = self._expand_query(query)
            results = self.semantic_search(expanded_query)

        return results

    def _expand_query(self, query: str) -> str:
        """Use LLM to generate query variations."""
        prompt = f"Generate 3 alternative phrasings for: {query}"
        variations = self.llm.generate(prompt)
        return " OR ".join(variations)
```

### 3. Execution Agents

**Responsibility:** Perform computations, generate responses, or interact with APIs.

**Capabilities:**

- **Data processing and transformation** (filter, aggregate, format)
- **API invocation** (CRUD operations on databases/services)
- **Response generation** (text, code, visualizations)
- **Workflow execution** (multi-step operations)

**Example: Payment Processing Agent**

```python
class PaymentExecutionAgent:
    def process_payment(self, order: dict) -> dict:
        """Execute payment transaction with validation."""
        # Step 1: Validate input
        if not self._validate_order(order):
            raise ValueError("Invalid order data")

        # Step 2: Calculate total with tax
        total = self._calculate_total(order["items"], order["tax_rate"])

        # Step 3: Call payment API
        payment_result = self.payment_api.charge(
            amount=total,
            customer_id=order["customer_id"],
            method=order["payment_method"]
        )

        # Step 4: Update database
        self.db.create_transaction(payment_result)

        return payment_result
```

### 4. Evaluator Agents

**Responsibility:** Monitor and validate responses for coherence and alignment with objectives.

**Capabilities:**

- **Quality assessment** (accuracy, relevance, completeness)
- **Hallucination detection** (claims not supported by sources)
- **Bias checking** (detect unfair or prejudiced outputs)
- **Confidence scoring** (how certain is the agent about its answer)

**Example: LLM-as-a-Judge (see Lesson 14 Topic 2)**

```python
class EvaluatorAgent:
    def validate_response(self, response: str, context: list[str]) -> dict:
        """Check if response is accurate and faithful to sources."""
        prompt = f"""
        Response: {response}
        Source Documents: {context}

        Evaluate:
        1. Accuracy: Are all claims correct? (0-10)
        2. Attribution: Is every claim supported by sources? (0-10)
        3. Hallucination: Any unsupported claims? (Yes/No with examples)
        4. Completeness: Does it answer the question fully? (0-10)
        5. Confidence: How certain are you? (0-1)
        """
        evaluation = self.llm.generate(prompt)
        return self._parse_evaluation(evaluation)
```

---

## Nine Architectural Components of Multi-Agent Systems

Every robust multi-agent system includes these core architectural elements.

### 1. Interaction Wrapper

**Purpose:** Interface between agent and environment (users, systems, APIs).

**Responsibilities:**

- Manage communication (input/output)
- Adapt to various modalities (text, voice, images, video)
- Protocol handling (HTTP, gRPC, WebSocket)

**Example: Chainlit UI Wrapper**

```python
import chainlit as cl

class ChainlitInteractionWrapper:
    """Wrap agent with Chainlit UI for chat interface."""

    @cl.on_message
    async def handle_message(self, message: str):
        """Receive user input and return agent response."""
        # Convert chat message to agent input format
        agent_input = self._format_input(message)

        # Call agent
        agent_output = await self.agent.process(agent_input)

        # Convert agent output to chat message
        response = self._format_output(agent_output)

        # Send to user
        await cl.Message(content=response).send()
```

**Multi-Modal Example:**

```python
class MultiModalWrapper:
    """Handle text, voice, and image inputs."""

    def process_input(self, input_data: dict) -> dict:
        if input_data["type"] == "text":
            return self._handle_text(input_data["content"])
        elif input_data["type"] == "voice":
            # Transcribe audio to text
            text = self.speech_to_text(input_data["audio"])
            return self._handle_text(text)
        elif input_data["type"] == "image":
            # Extract image features
            description = self.vision_model.describe(input_data["image"])
            return self._handle_text(description)
```

### 2. Memory Management

**Purpose:** Maintain state across interactions and learn from past experiences.

#### Memory in Multi-Agent Systems

In multi-agent architectures, memory can be **shared** (centralized knowledge base accessible to all agents) or **private** (each agent maintains independent memory stores). The choice profoundly impacts coordination, performance, and cost.

**Shared Memory Architecture:**

- All agents query the same vector database (e.g., Chroma) for semantic/episodic memory
- **Advantages:** Consistent knowledge, reduced duplication, easier synchronization
- **Trade-offs:** Contention for resources, potential coupling between agents, requires coordination protocol
- **Example:** Bhagavad Gita chatbot uses shared semantic memory (verse embeddings) across all agents—Query Classifier, Retrieval Agent, and Synthesis Agent all access the same Chroma collection to ensure consistent verse references

**Private Memory Architecture:**

- Each agent maintains its own memory store (isolated working memory, specialized knowledge bases)
- **Advantages:** No coordination overhead, agents can specialize without conflicts, parallel scaling
- **Trade-offs:** Knowledge duplication, risk of inconsistency, harder to share learned insights
- **Example:** In the travel planning exercise below, each specialist agent (FlightSearchAgent, HotelSearchAgent) maintains private caches of API results to avoid re-querying expensive endpoints, while sharing a common long-term user preference database

**Hybrid Approach (Recommended):**
Most production systems use **hybrid memory**: shared semantic/episodic stores for common knowledge, private working memory per agent/session. For instance, a customer support system shares the product documentation vector DB (semantic memory) but keeps each customer's conversation history isolated (working memory) to prevent cross-contamination and maintain privacy.

**Three Types of Memory:**

#### Short-Term Memory (Working Memory)

- **Purpose:** Immediate context for current task
- **Scope:** Single session or conversation
- **Examples:** Current conversation history, API cache, session state

```python
class ShortTermMemory:
    def __init__(self):
        self.session_state = {}
        self.conversation_history = []
        self.cache = {}

    def add_message(self, role: str, content: str):
        """Add to conversation history."""
        self.conversation_history.append({
            "role": role,
            "content": content,
            "timestamp": datetime.now()
        })

    def get_context(self, max_messages: int = 10) -> list:
        """Get recent conversation for LLM context."""
        return self.conversation_history[-max_messages:]
```

#### Long-Term Memory (Persistent Knowledge)

- **Purpose:** Learned patterns and experiences
- **Scope:** Cross-session, persistent storage
- **Examples:** User profiles, learned skills, reference data

```python
class LongTermMemory:
    def __init__(self, db_path: str):
        self.db = Database(db_path)

    def store_user_preference(self, user_id: str, key: str, value: Any):
        """Save user preference to persistent storage."""
        self.db.upsert("user_profiles", {
            "user_id": user_id,
            "preferences": {key: value}
        })

    def retrieve_user_profile(self, user_id: str) -> dict:
        """Load user profile from database."""
        return self.db.query("user_profiles", {"user_id": user_id})
```

#### Reflection (Memory Promotion)

- **Purpose:** Decide which short-term items to promote to long-term
- **Examples:** Frequent preferences → User profile, Common errors → Skills

```python
class MemoryReflection:
    def reflect(self, short_term: ShortTermMemory, long_term: LongTermMemory):
        """Promote frequent short-term items to long-term storage."""
        # Count preference mentions in session
        preference_counts = self._count_preferences(short_term)

        for pref, count in preference_counts.items():
            if count >= 3:  # Mentioned 3+ times
                # Promote to long-term memory
                long_term.store_user_preference(
                    user_id=short_term.session_state["user_id"],
                    key=pref["key"],
                    value=pref["value"]
                )
```

#### Vector Database for Multi-Agent Memory

Production multi-agent systems typically use **vector databases** (Chroma, Pinecone, Weaviate) for scalable semantic and episodic memory. Here's how to initialize a shared memory store accessible to all agents:

```python
from pathlib import Path
import chromadb
from chromadb.config import Settings
from typing import Any

class MultiAgentMemoryStore:
    """Shared vector database for multi-agent semantic/episodic memory.

    Supports metadata filtering so agents can query their own episodic memory
    or shared semantic knowledge without interference.
    """

    def __init__(self, db_path: str):
        """Initialize persistent Chroma client.

        Args:
            db_path: Path to persistent storage directory

        Raises:
            ValueError: If db_path is empty
            OSError: If db_path cannot be created
        """
        # Step 1: Input validation (defensive)
        if not db_path:
            raise ValueError("db_path cannot be empty")

        # Step 2: Set up storage path
        storage_path = Path(db_path)
        storage_path.mkdir(parents=True, exist_ok=True)

        # Step 3: Initialize Chroma client
        self.client = chromadb.PersistentClient(
            path=str(storage_path),
            settings=Settings(
                anonymized_telemetry=False,  # Privacy
                allow_reset=True  # Allow cleanup in dev/test
            )
        )

        # Step 4: Create/get shared collection
        self.collection = self.client.get_or_create_collection(
            name="multi_agent_memory",
            metadata={"description": "Shared episodic and semantic memory"}
        )

    def store_episodic_memory(
        self,
        agent_id: str,
        event: str,
        outcome: dict[str, Any]
    ) -> None:
        """Store agent's past experience for future reference.

        Args:
            agent_id: Unique agent identifier (e.g., "planner_agent_001")
            event: Description of event (e.g., "Attempted booking flight LAX->NYC")
            outcome: Result metadata (success, error, cost, latency)

        Raises:
            TypeError: If outcome is not a dict
        """
        if not isinstance(outcome, dict):
            raise TypeError("outcome must be a dict")

        self.collection.add(
            documents=[event],
            metadatas=[{
                "agent_id": agent_id,
                "memory_type": "episodic",
                **outcome  # Include success, error, timestamp, etc.
            }],
            ids=[f"{agent_id}_{hash(event)}"]
        )

    def retrieve_similar_experiences(
        self,
        query: str,
        agent_id: str | None = None,
        n_results: int = 5
    ) -> list[dict]:
        """Retrieve similar past experiences for reasoning.

        Args:
            query: Description of current situation
            agent_id: Filter to specific agent's memory (None = all agents)
            n_results: Number of similar experiences to retrieve

        Returns:
            List of similar experiences with metadata
        """
        where_filter = {"memory_type": "episodic"}
        if agent_id:
            where_filter["agent_id"] = agent_id

        results = self.collection.query(
            query_texts=[query],
            n_results=n_results,
            where=where_filter
        )

        return results

# Usage Example: Multi-Agent System with Shared Memory
memory_store = MultiAgentMemoryStore(db_path="./data/agent_memory")

# Agent 1: Planner stores decision outcome
memory_store.store_episodic_memory(
    agent_id="planner_agent",
    event="Chose hierarchical pattern for 10-task workflow",
    outcome={"success": True, "completion_time_sec": 45.2, "cost_usd": 0.12}
)

# Agent 2: Similar agent retrieves past decisions
similar_cases = memory_store.retrieve_similar_experiences(
    query="How to organize 8-task workflow?",
    agent_id="planner_agent",  # Filter to planner's own experiences
    n_results=3
)
# Returns: Previous hierarchical vs sequential pattern decisions
```

**When to Use Vector DB vs In-Memory Storage:**

- **Vector DB (Chroma, Pinecone):** Large-scale systems (>10K memories), semantic search required, multi-session persistence
- **In-Memory (dict, list):** Small-scale prototypes (<100 memories), session-only memory, no semantic search needed
- **Decision Matrix:** See [Memory Systems Fundamentals](memory_systems_fundamentals.md#vector-db-decision-matrix-tasks-14a14d) for full comparison

**Deep Dive: Memory Systems Implementation**

To master memory systems in multi-agent architectures, follow this learning path:

1. **[Memory Systems Fundamentals](memory_systems_fundamentals.md)** (~30-35 min)
   - Understand 5 memory types (working, episodic, semantic, procedural, parametric)
   - Learn vector database decision matrix (Chroma, Pinecone, Weaviate, Qdrant, Milvus, pgvector)
   - Study Search-o1 reasoning pattern with memory integration

2. **[Context Engineering Guide](context_engineering_guide.md)** (~25-30 min)
   - Optimize context selection (re-ranking, MMR, business rules)
   - Implement context compression for cost reduction (ROI: $24 → $12 → $4.80)
   - Master context ordering strategies (combat lost-in-the-middle effect)

3. **[Memory Systems Implementation Notebook](memory_systems_implementation.ipynb)** (~45 min DEMO mode, ~3 hours FULL mode)
   - Hands-on Chroma setup with lesson-14 datasets
   - Implement working memory management (trimming, summarization)
   - Build Search-o1 pattern with token overhead tracking
   - Practice MMR selection and compression ROI calculation

**Estimated Total Learning Time:** 4-5 hours

### 3. Cognitive Functionality

**Purpose:** Enable reasoning, planning, and self-correction.

**Underpinned by:**

- **Chain-of-Thought (CoT)**: Step-by-step reasoning
- **ReAct**: Reasoning + Acting in interleaved fashion
- **Planner subsystem**: Decompose complex tasks

**Capabilities:**

- Self-correction (detect and fix mistakes)
- User intent refinement (ask clarifying questions)
- Multi-step problem solving

**Chain-of-Thought Example:**

```python
class CognitiveAgent:
    def solve_with_cot(self, problem: str) -> str:
        """Use chain-of-thought reasoning."""
        prompt = f"""
        Problem: {problem}

        Let's solve this step by step:
        1. Understand what's being asked
        2. Identify relevant information
        3. Break down the solution approach
        4. Execute each step
        5. Verify the answer

        Think through each step before answering.
        """
        return self.llm.generate(prompt)
```

**ReAct Pattern Example:**

```python
class ReActAgent:
    def process(self, query: str) -> str:
        """Interleave reasoning and action."""
        thought = self._think(query)  # Reasoning step

        if self._needs_tool(thought):
            tool_result = self._act(thought)  # Action step
            thought = self._think(f"Tool returned: {tool_result}")  # Reason about result

        return self._generate_response(thought)
```

### 4. Tool Integration

**Purpose:** Enable agents to use external tools, expanding capabilities beyond NLP.

**Components:**

- **Tool registry**: Available tools and their descriptions
- **Dynamic discovery**: Find new tools at runtime
- **Tool RAG**: Retrieve relevant tools based on task context

**Tool Registry Example:**

```python
class ToolRegistry:
    def __init__(self):
        self.tools = {}

    def register(self, name: str, tool: callable, description: str):
        """Add tool to registry."""
        self.tools[name] = {
            "function": tool,
            "description": description,
            "parameters": self._extract_params(tool)
        }

    def discover(self, task_description: str) -> list:
        """Find relevant tools using semantic search."""
        # Use RAG to match task to tool descriptions
        tool_embeddings = self._embed_descriptions()
        task_embedding = self._embed(task_description)

        similarities = cosine_similarity(task_embedding, tool_embeddings)
        return [self.tools[name] for name in similarities.top_k(3)]

# Usage
registry = ToolRegistry()
registry.register(
    name="get_weather",
    tool=weather_api.fetch,
    description="Fetch current weather for a location"
)
registry.register(
    name="book_flight",
    tool=airline_api.book,
    description="Book a flight ticket"
)

# Agent discovers tools dynamically
relevant_tools = registry.discover("I need to check the weather in Paris")
# Returns: [get_weather]
```

### 5. Flow / Routing

**Purpose:** Govern connections and task distribution between agents.

**Mechanisms:**

#### Delegation (Background Task)

- Manager assigns task to worker agent
- Worker runs in background, returns result later

```python
class ManagerAgent:
    def delegate_task(self, task: dict, worker: Agent):
        """Assign task to background worker."""
        task_id = self._create_task_id()
        self.task_queue.add(task_id, task, worker)
        return task_id  # Return immediately, don't wait

    def get_result(self, task_id: str) -> dict:
        """Retrieve result when ready."""
        return self.task_queue.get_result(task_id)
```

#### Handoff (Transfer Conversation)

- Transfer user interaction to another agent
- Includes conversation context

```python
class GeneralAgent:
    def handle_query(self, query: str, user_id: str):
        """Route to specialist if needed."""
        domain = self._classify_domain(query)

        if domain == "finance":
            # Handoff to finance specialist
            return self._handoff_to_agent(
                target_agent=finance_agent,
                context=self.memory.get_context(user_id),
                query=query
            )
        else:
            # Handle directly
            return self.generate_response(query)
```

#### Agent-as-Tool

- Use another agent like a function call
- No conversation transfer, just get result

```python
class OrchestratorAgent:
    def process(self, query: str) -> str:
        """Use other agents as tools."""
        # Step 1: Use research agent as tool
        research_results = self.research_agent.search(query)

        # Step 2: Use analysis agent as tool
        analysis = self.analysis_agent.analyze(research_results)

        # Step 3: Synthesize final response
        return self.generate_response(analysis)
```

### 6. Feedback Loops / Reinforcement Learning

**Purpose:** Enable continuous learning and adaptation.

**Mechanisms for Gen AI Agents:**

- Process interaction outcomes (user ratings, success metrics)
- Refine decision-making strategies
- Incorporate past performance into future decisions
- **Note:** Rarely traditional RL training; usually prompt refinement

**Example: User Feedback Integration**

```python
class FeedbackLoop:
    def __init__(self):
        self.feedback_db = Database("feedback.db")

    def collect_feedback(self, interaction_id: str, rating: int, comments: str):
        """Store user feedback."""
        self.feedback_db.insert({
            "interaction_id": interaction_id,
            "rating": rating,
            "comments": comments,
            "timestamp": datetime.now()
        })

    def analyze_patterns(self) -> dict:
        """Find common patterns in low-rated responses."""
        low_rated = self.feedback_db.query("rating < 3")

        # Extract common issues
        issues = self._cluster_comments(low_rated["comments"])
        return {
            "common_issues": issues,
            "suggested_improvements": self._generate_fixes(issues)
        }

    def adapt_strategy(self):
        """Adjust prompts based on feedback."""
        patterns = self.analyze_patterns()
        for issue in patterns["common_issues"]:
            # Update system prompt to address issue
            self.agent.update_prompt(issue["fix"])
```

### 7. Agent Communication Protocol

**Purpose:** Structured communication among agents for consensus and collaboration.

**Key Features:**

- **Message format**: Standardized structure (JSON, Protocol Buffers)
- **Task sharing**: Assign work between agents
- **Knowledge sharing**: Share learned insights
- **Consensus mechanisms**: Agree on decisions (voting, weighted average)

**Message Format Example:**

```python
from dataclasses import dataclass
from enum import Enum

class MessageType(Enum):
    TASK_ASSIGNMENT = "task_assignment"
    RESULT = "result"
    QUERY = "query"
    CONSENSUS_REQUEST = "consensus_request"

@dataclass
class AgentMessage:
    from_agent: str
    to_agent: str
    message_type: MessageType
    task_id: str
    payload: dict
    timestamp: datetime

# Usage
message = AgentMessage(
    from_agent="planner_agent",
    to_agent="research_agent",
    message_type=MessageType.TASK_ASSIGNMENT,
    task_id="research_001",
    payload={
        "query": "Find top 5 hotels in Paris under $200/night",
        "deadline": "2025-02-15T10:00:00Z"
    },
    timestamp=datetime.now()
)
```

**Consensus Mechanism Example:**

```python
class ConsensusProtocol:
    def vote(self, agents: list[Agent], decision: str) -> bool:
        """Majority voting among agents."""
        votes = [agent.evaluate(decision) for agent in agents]
        approve_count = sum(1 for vote in votes if vote == "approve")
        return approve_count > len(agents) / 2

    def weighted_consensus(self, agent_outputs: dict[str, float]) -> float:
        """Weighted average based on agent confidence."""
        weights = {agent: output["confidence"] for agent, output in agent_outputs.items()}
        total_weight = sum(weights.values())

        weighted_sum = sum(
            output["value"] * weights[agent]
            for agent, output in agent_outputs.items()
        )

        return weighted_sum / total_weight
```

### 8. Remote Agent Communication

**Purpose:** Enable collaboration between agents across different organizations or systems.

**Requirements:**

- **Asynchronous tasks**: Durable task state (survive restarts)
- **Notifications**: Update users while offline
- **Negotiation**: Support for bringing user into session
- **UX capabilities**: Align on supported interactions (text, voice, files)

**Example: Cross-Organization Agent Communication**

```python
class RemoteAgentClient:
    def __init__(self, remote_url: str, api_key: str):
        self.remote_url = remote_url
        self.api_key = api_key
        self.task_store = PersistentTaskStore()  # Survive restarts

    def delegate_remote_task(self, task: dict) -> str:
        """Send task to agent in another organization."""
        task_id = self._generate_task_id()

        # Store task state locally (durable)
        self.task_store.save(task_id, {
            "status": "pending",
            "task": task,
            "remote_url": self.remote_url,
            "created_at": datetime.now()
        })

        # Send to remote agent
        response = requests.post(
            f"{self.remote_url}/tasks",
            json={"task_id": task_id, "task": task},
            headers={"Authorization": f"Bearer {self.api_key}"}
        )

        return task_id

    def check_status(self, task_id: str) -> dict:
        """Check if remote task completed."""
        response = requests.get(
            f"{self.remote_url}/tasks/{task_id}",
            headers={"Authorization": f"Bearer {self.api_key}"}
        )

        # Update local state
        self.task_store.update(task_id, response.json())
        return response.json()
```

### 9. Agent & Tool Registry (Mesh)

**Purpose:** Manage discovery, registration, and selection from large pool of tools/agents.

**Components:**

- **Ontology**: Taxonomy of capabilities (categories, tags)
- **Descriptions**: What each agent/tool does
- **Requirements**: Input/output formats, dependencies
- **Performance Metrics**: Success rates, latency, cost

**Use Case:** Agent needs to choose which tool/agent to use from a "mesh" of 100+ options.

**Example: Agent Mesh Registry**

```python
from dataclasses import dataclass

@dataclass
class AgentMetadata:
    name: str
    capabilities: list[str]
    description: str
    input_format: dict
    output_format: dict
    performance_metrics: dict
    cost_per_call: float

class AgentMeshRegistry:
    def __init__(self):
        self.agents = {}

    def register(self, metadata: AgentMetadata):
        """Add agent to mesh."""
        self.agents[metadata.name] = metadata

    def discover(self, required_capability: str, max_cost: float = None) -> list:
        """Find agents matching criteria."""
        candidates = [
            agent for agent in self.agents.values()
            if required_capability in agent.capabilities
        ]

        if max_cost:
            candidates = [a for a in candidates if a.cost_per_call <= max_cost]

        # Sort by performance (success rate * speed)
        candidates.sort(
            key=lambda a: a.performance_metrics["success_rate"] / a.performance_metrics["avg_latency_ms"],
            reverse=True
        )

        return candidates

# Usage
registry = AgentMeshRegistry()

registry.register(AgentMetadata(
    name="weather_agent",
    capabilities=["weather_forecast", "climate_data"],
    description="Provides weather information",
    input_format={"location": "string", "date": "ISO8601"},
    output_format={"temperature": "float", "conditions": "string"},
    performance_metrics={"success_rate": 0.98, "avg_latency_ms": 120},
    cost_per_call=0.001
))

registry.register(AgentMetadata(
    name="flight_booking_agent",
    capabilities=["flight_search", "booking"],
    description="Searches and books flights",
    input_format={"origin": "string", "destination": "string", "date": "ISO8601"},
    output_format={"flights": "list", "booking_id": "string"},
    performance_metrics={"success_rate": 0.95, "avg_latency_ms": 350},
    cost_per_call=0.005
))

# Find best weather agent under $0.002
best_weather_agent = registry.discover("weather_forecast", max_cost=0.002)[0]
```

---

## Practical Exercise: Design a Travel Planning Multi-Agent System

**Scenario:**
Build a multi-agent system that helps users plan international trips.

**Requirements:**

1. Handle complex queries like "Plan a 10-day trip to Japan in April for 2 adults with $5,000 budget"
2. Coordinate multiple aspects: flights, hotels, activities, budget tracking
3. Provide personalized recommendations based on user preferences
4. Validate feasibility and suggest alternatives if constraints can't be met

**Your Task:**

### Step 1: Identify Agent Types

For each agent type (Planner, Retriever, Execution, Evaluator), define:

- What specific agents do you need?
- What are their responsibilities?
- What tools do they need access to?

**Example Answer:**

```
Planner Agents:
- ItineraryPlannerAgent: Break trip into daily plans with activities
- BudgetPlannerAgent: Allocate budget across categories

Retriever Agents:
- FlightSearchAgent: Query flight APIs (Amadeus, Skyscanner)
- HotelSearchAgent: Search accommodation (Booking.com, Airbnb)
- ActivityResearchAgent: Find attractions, restaurants (Google Places, TripAdvisor)

Execution Agents:
- BookingAgent: Execute reservations (flights, hotels)
- NotificationAgent: Send confirmations and reminders
- PaymentAgent: Process payments securely

Evaluator Agents:
- FeasibilityValidator: Check if plan fits budget and time constraints
- PreferenceMatchScorer: Rate how well plan matches user preferences
- RiskAssessor: Identify potential issues (visa requirements, travel advisories)
```

### Step 2: Design Communication Flow

Choose a multi-agent pattern (Sequential, Hierarchical, Collaborative, or Competitive) and justify your choice.

**Example Answer:**

```
Pattern: Hierarchical (Manager-Worker)

Why: Trip planning requires:
- Central coordination (budget, timeline)
- Parallel execution (search flights + hotels simultaneously)
- Strategic decisions (if budget exceeded, which to reduce?)

Flow:
1. User Query → ItineraryPlannerAgent (Manager)
2. Manager delegates in parallel:
   ├── FlightSearchAgent → Find flight options
   ├── HotelSearchAgent → Find accommodation
   └── ActivityResearchAgent → Find activities
3. Manager collects results
4. BudgetPlannerAgent → Check total cost
5. If over budget:
   - FeasibilityValidator → Suggest cheaper alternatives
   - Loop back to step 2 with constraints
6. PreferenceMatchScorer → Rate final plan
7. Return plan to user for approval
```

### Step 3: Map Architectural Components

For each of the 9 architectural components, describe how it applies to your system.

**Example Answer:**

```
1. Interaction Wrapper: Chainlit chat UI + voice input (mobile app)

2. Memory Management:
   - Short-term: Current trip planning session
   - Long-term: User profile (preferred airlines, dietary restrictions, past trips)
   - Reflection: If user books beach vacation 3 times → Add "beach preference" to profile

3. Cognitive Functionality:
   - CoT: "Let's check budget: flights $1200 + hotels $1500 + activities $800 = $3500 (within $5000)"
   - ReAct: If flight search fails → Expand date range and retry

4. Tool Integration:
   - Registry: Amadeus API, Booking.com API, Google Places API
   - Tool RAG: "Need accommodation" → Retrieve hotel search tools

5. Flow/Routing:
   - Delegation: Manager → Workers (parallel searches)
   - Handoff: If user asks visa question → Transfer to VisaAgent

6. Feedback Loops:
   - Collect ratings after trip
   - If user rates trip 5★ → Promote preferences to long-term memory

7. Agent Communication Protocol:
   - Message format: JSON with task_id, agent_id, payload
   - Consensus: If multiple hotel options, agents vote on best match

8. Remote Communication:
   - Amadeus API (external service)
   - Async: Send booking request, poll for confirmation

9. Agent & Tool Registry:
   - Mesh: 50+ travel APIs registered
   - Discovery: "Need flights" → Find agents with "flight_search" capability
   - Metrics: Track API success rate, latency, cost
```

### Step 4: Identify Challenges

What could go wrong? How would you handle:

- Budget constraints (plan exceeds $5,000)
- API failures (Booking.com down)
- Conflicting preferences (user wants luxury hotel + budget trip)
- Time constraints (must plan in <60 seconds)

**Example Answers:**

```
Challenge 1: Budget Overrun
Solution:
- FeasibilityValidator detects total > $5000
- BudgetPlannerAgent suggests: "Reduce hotel from 5★ to 4★ saves $800"
- Loop: Re-search with lower hotel tier

Challenge 2: API Failure (Booking.com down)
Solution:
- HotelSearchAgent catches BookingAPIError
- Fallback to Airbnb API
- If all APIs fail, return cached results from last 24h

Challenge 3: Conflicting Preferences
Solution:
- PreferenceMatchScorer detects conflict
- Ask user: "Luxury hotels exceed budget. Prioritize: (A) Stay within budget or (B) Extend budget?"
- Adjust constraints based on user input

Challenge 4: Time Constraints
Solution:
- Set timeouts: FlightSearchAgent max 15s, HotelSearchAgent max 15s
- Parallel execution: All searches run simultaneously (not sequential)
- If timeout → Return partial results: "Found flights and hotels, still searching activities..."
```

---

## Summary

**What You Learned:**

1. **Multi-agent systems** assemble specialized agents (like a team of experts) instead of relying on one generalist
2. **Six advantages**: Enhanced accuracy, improved efficiency, better handling of complex tasks, increased scalability, improved fault tolerance, reduced hallucinations
3. **Four agent types**: Planner (decompose), Retriever (search), Execution (act), Evaluator (validate)
4. **Nine architectural components**:
   - Interaction Wrapper (UI/API interface)
   - Memory Management (short-term, long-term, reflection)
   - Cognitive Functionality (CoT, ReAct, planning)
   - Tool Integration (registry, discovery, RAG)
   - Flow/Routing (delegation, handoff, agent-as-tool)
   - Feedback Loops (learn from outcomes)
   - Agent Communication Protocol (message format, consensus)
   - Remote Communication (async tasks, cross-org collaboration)
   - Agent & Tool Registry (mesh, discovery, metrics)

**Next Steps:**

- **Learn design patterns**: Read `multi_agent_design_patterns.md` to understand when to use Sequential, Hierarchical, Collaborative, or Competitive patterns
- **Explore challenges**: Read `multi_agent_challenges_evaluation.md` to learn about task allocation, coordination, and debugging
- **Hands-on practice**: Complete `multi_agent_patterns_comparison.ipynb` to compare pattern performance
- **Real-world case study**: Explore `automotive_ai_case_study.ipynb` to see 5 specialized agents coordinating in autonomous vehicles

**Key Takeaway:**
Multi-agent systems are like orchestrating a symphony—each instrument (agent) plays a specialized part, and the conductor (orchestrator or communication protocol) ensures harmony. The result is richer, more reliable, and more scalable than any single instrument could achieve alone.

---

**Related Tutorials:**

- [Multi-Agent Design Patterns](multi_agent_design_patterns.md) - When to use each coordination pattern
- [Multi-Agent Challenges & Evaluation](multi_agent_challenges_evaluation.md) - Debugging and metrics
- [Automotive AI Case Study](automotive_ai_case_study.ipynb) - Real-world implementation

**References:**

- Google's "Agents Companion" Whitepaper (February 2025)
- Topic 03: Multi-Agent Architectures
