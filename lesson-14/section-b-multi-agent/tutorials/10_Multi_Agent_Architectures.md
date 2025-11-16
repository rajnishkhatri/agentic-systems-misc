# Multi-Agent Architectures

**Source:** Google's "Agents Companion" Whitepaper (February 2025)
**Topic Complexity:** ⭐⭐⭐⭐⭐
**Lines:** 182-286 from original document

---

## Overview

Multi-agent systems are a paradigm shift from single-agent workflows, where **multiple specialized agents collaborate** to achieve complex objectives. Think of it as assembling a **team of experts** rather than relying on one generalist.

**Key Principle**: Break down complex problems into distinct tasks handled by specialized agents, each operating with defined roles and interacting dynamically to optimize decision-making.

---

## Multi-Agent vs. Single-Agent Systems

### Single-Agent System

**Characteristics**:
- One LLM handles all aspects of a task
- Monolithic architecture
- General-purpose capabilities

**Limitations**:
- Limited specialization depth
- Harder to optimize for specific domains
- Single point of failure
- Difficult to scale

### Multi-Agent System

**Definition**: Multiple independent entities (agents), each with its own:
- Unique role and context
- Potentially different LLM
- Specialized capabilities
- Communication protocol for collaboration

**Advantages** (over single-agent):

#### 1. Enhanced Accuracy
- Agents can **cross-check** each other's work
- Multiple perspectives reduce individual model biases
- Consensus mechanisms improve reliability

#### 2. Improved Efficiency
- Agents work in **parallel**
- Faster task completion
- Resource optimization (use powerful models only when needed)

#### 3. Better Handling of Complex Tasks
- Large tasks broken into smaller, **manageable subtasks**
- Each agent focuses on specific aspect
- Specialized expertise per domain

#### 4. Increased Scalability
- Easily add more agents with new capabilities
- Horizontal scaling without retraining base models
- Modular architecture

#### 5. Improved Fault Tolerance
- If one agent fails, others can **take over responsibilities**
- Redundancy for critical functions
- Graceful degradation

#### 6. Reduced Hallucinations and Bias
- Combining perspectives from multiple agents
- Cross-validation of outputs
- More reliable and trustworthy results

---

## Understanding Multi-Agent Architectures

### Core Principles

#### 1. Modularity
- Each agent is a self-contained unit
- Clear interfaces and responsibilities
- Easier to develop, test, and maintain

#### 2. Collaboration
- Agents communicate and share information
- Dynamic coordination based on task requirements
- Consensus-building for complex decisions

#### 3. Hierarchy
- Structured relationships between agents
- Manager-worker patterns
- Delegation and orchestration

---

## Agent Types by Function

### 1. Planner Agents

**Responsibility**: Breaking down high-level objectives into structured sub-tasks.

**Capabilities**:
- Task decomposition
- Dependency analysis (which tasks must happen first)
- Resource allocation (assign tasks to appropriate agents)

**Example**:
```
User Goal: "Plan a company retreat"

Planner Agent Output:
1. Determine budget and headcount → Finance Agent
2. Research venue options → Research Agent
3. Survey employee preferences → Survey Agent
4. Book venue and catering → Booking Agent
5. Create itinerary → Coordination Agent
```

### 2. Retriever Agents

**Responsibility**: Optimize knowledge acquisition by dynamically fetching relevant data.

**Capabilities**:
- Semantic search across knowledge bases
- API calls to external data sources
- Query refinement and expansion
- Source selection (which database/API to use)

**Example**: Agentic RAG (see Topic 4) where retriever agents iteratively refine searches.

### 3. Execution Agents

**Responsibility**: Perform computations, generate responses, or interact with APIs.

**Capabilities**:
- Data processing and transformation
- API invocation (CRUD operations)
- Response generation (text, code, visualizations)
- Workflow execution

**Example**: Agent that processes payment transactions or generates code snippets.

### 4. Evaluator Agents

**Responsibility**: Monitor and validate responses for coherence and alignment with objectives.

**Capabilities**:
- Quality assessment (accuracy, relevance, completeness)
- Hallucination detection
- Bias checking
- Confidence scoring

**Example**: LLM-as-a-Judge (see Topic 2) validating another agent's output.

---

## Multi-Agent Design Patterns

### Pattern Comparison Table

| Pattern | Description | Example | Key Benefit |
|---------|-------------|---------|-------------|
| **Sequential** | Agents work in linear order, passing output to next agent | Assembly line manufacturing | Simple coordination, clear dependencies |
| **Hierarchical** | Manager agent coordinates workflow, delegates to worker agents | Corporate org structure (leader-follower) | Centralized decision-making, clear responsibility |
| **Collaborative** | Agents share information/resources to achieve common goal | Research team working on project | Leverages diverse expertise, creative problem-solving |
| **Competitive** | Agents compete to achieve best outcome, strongest result selected | Multiple agents propose solutions, best one chosen | Quality through competition, diverse approaches |

### When to Use Each Pattern

#### Sequential Pattern

**Use When**:
- Tasks have strict dependencies (A must complete before B)
- Each step requires output from previous step
- Linear workflow is natural fit

**Example Workflow**:
```
User Query → Classification Agent → Retrieval Agent → Synthesis Agent → Validator Agent → User Response
```

**Trade-offs**:
- ✅ Simple to implement and debug
- ✅ Clear accountability (know which step failed)
- ❌ Slowest pattern (no parallelization)
- ❌ Bottleneck if one agent is slow

#### Hierarchical Pattern

**Use When**:
- Complex tasks need central coordination
- Strategic decisions required (which agents to use)
- Different expertise needed for subtasks

**Example Workflow**:
```
Manager Agent receives query
    ↓
Determines strategy and delegates:
    ├── Worker Agent 1: Financial analysis
    ├── Worker Agent 2: Market research
    └── Worker Agent 3: Competitive intelligence
    ↓
Manager Agent synthesizes results
```

**Trade-offs**:
- ✅ Centralized control and oversight
- ✅ Can parallelize subtasks
- ✅ Clear escalation path for failures
- ❌ Manager agent is single point of failure
- ❌ Requires sophisticated orchestration logic

#### Collaborative Pattern

**Use When**:
- No single agent has complete information
- Multiple perspectives improve outcome
- Creative problem-solving needed

**Example Workflow**:
```
Shared workspace (conversation thread or shared state)
    ↑↓
Agent 1 contributes domain expertise
    ↑↓
Agent 2 adds complementary insights
    ↑↓
Agent 3 validates and refines
    ↑↓
Consensus or merged response
```

**Trade-offs**:
- ✅ Leverages diverse expertise
- ✅ Cross-validation improves quality
- ✅ Robust to individual agent failures
- ❌ Coordination complexity
- ❌ Potential for conflicting outputs
- ❌ Higher latency (multiple rounds of communication)

#### Competitive Pattern

**Use When**:
- Multiple valid approaches exist
- Quality is more important than speed
- Want to avoid single-model bias

**Example Workflow**:
```
User query sent to multiple agents in parallel
    ├── Agent A generates response (approach 1)
    ├── Agent B generates response (approach 2)
    └── Agent C generates response (approach 3)
    ↓
Evaluator Agent selects best response or merges best elements
```

**Trade-offs**:
- ✅ Quality through diversity
- ✅ Avoids single-point failure
- ✅ Can parallelize for speed
- ❌ Higher cost (multiple LLM calls)
- ❌ Need robust evaluation to select winner

---

## Important Components of Agents

### Architectural Elements

#### 1. Interaction Wrapper

**Purpose**: Interface between agent and environment.

**Responsibilities**:
- Manage communication (input/output)
- Adapt to various modalities (text, voice, images)
- Protocol handling (HTTP, gRPC, WebSocket)

**Example**: Chainlit UI for chatbots, API endpoints for programmatic access.

#### 2. Memory Management

**Short-Term Memory**:
- Working memory for immediate context
- Session state (current conversation)
- Cache (recent API results)

**Long-Term Memory**:
- Learned patterns and experiences
- Episodes (past interactions)
- Examples (few-shot learning data)
- Skills (learned procedures)
- Reference data (knowledge base)

**Reflection**:
- Decide which short-term items to promote to long-term
- Example: User preference (short-term) → User profile (long-term)
- Sharing: Can memory be shared across agents, tasks, or sessions?

**Example**:
```python
# Short-term: Session state
session_memory = {
    "user_id": "123",
    "conversation_history": [...],
    "current_topic": "travel booking"
}

# Long-term: User profile
user_profile = {
    "preferences": {"airlines": ["Delta", "United"]},
    "past_bookings": [...],
    "loyalty_programs": [...]
}

# Reflection: Promote frequent preference to profile
if session_memory["hotel_preference"] appears 3+ times:
    user_profile["preferences"]["hotels"].append(...)
```

#### 3. Cognitive Functionality

**Underpinned by**:
- **Chain-of-Thought (CoT)**: Step-by-step reasoning
- **ReAct**: Reasoning + Acting in interleaved fashion
- **Planner subsystem**: Decompose complex tasks

**Capabilities**:
- Self-correction (detect and fix mistakes)
- User intent refinement (ask clarifying questions)
- Multi-step problem solving

**Example**: Agent realizes query is ambiguous → Asks clarifying question before proceeding.

#### 4. Tool Integration

**Purpose**: Enable agents to use external tools, expanding capabilities beyond NLP.

**Components**:
- **Tool registry**: Available tools and their descriptions
- **Dynamic discovery**: Find new tools at runtime
- **Tool RAG**: Retrieve relevant tools based on task context

**Example Tools**:
- APIs (database queries, web services)
- Functions (code execution, calculations)
- Data stores (vector databases, document stores)

**Example**:
```python
tool_registry = {
    "get_weather": {
        "description": "Fetch current weather for a location",
        "parameters": {"location": "string"},
        "endpoint": "https://api.weather.com/..."
    },
    "book_flight": {
        "description": "Book a flight ticket",
        "parameters": {"origin": "string", "destination": "string", "date": "string"},
        "endpoint": "https://api.airline.com/..."
    }
}
```

#### 5. Flow / Routing

**Purpose**: Govern connections with other agents.

**Mechanisms**:
- **Delegation**: Assign task to background agent
- **Handoff**: Transfer user interaction to another agent
- **Agent-as-Tool**: Use another agent like a function call

**Dynamic Capabilities**:
- Neighbor discovery (find available agents)
- Efficient communication (minimize latency)

**Example**:
```
User asks financial question
    ↓
General Agent detects domain mismatch
    ↓
Handoff to Finance Agent (transfers conversation context)
    ↓
Finance Agent continues conversation with user
```

#### 6. Feedback Loops / Reinforcement Learning

**Purpose**: Enable continuous learning and adaptation.

**Mechanisms** (for Gen AI agents):
- Process interaction outcomes
- Refine decision-making strategies
- Incorporate past performance into future decisions
- **Note**: Rarely traditional RL training for Gen AI agents

**Example**:
```
Agent receives low user rating (👎)
    ↓
Log interaction and rating
    ↓
Analyze common patterns in low-rated responses
    ↓
Adjust prompt or strategy for similar future queries
```

#### 7. Agent Communication Protocol

**Purpose**: Structured communication among agents for consensus and collaboration.

**Key Features**:
- **Message format**: Standardized structure (JSON, Protocol Buffers)
- **Task sharing**: Assign work between agents
- **Knowledge sharing**: Share learned insights
- **Consensus mechanisms**: Agree on decisions (voting, weighted average)

**Example Message**:
```json
{
  "from": "planner_agent",
  "to": "research_agent",
  "task_id": "research_001",
  "action": "delegate",
  "payload": {
    "query": "Find top 5 hotels in Paris under $200/night",
    "deadline": "2025-02-15T10:00:00Z"
  }
}
```

#### 8. Remote Agent Communication

**Challenge**: Agents across different organizations or systems.

**Requirements**:
- **Asynchronous tasks**: Durable task state (survive restarts)
- **Notifications**: Update users while offline
- **Negotiation**: Support for bringing user into session
- **UX capabilities**: Align on supported interactions (text, voice, files)

**Example**: Agent A (Company A) delegates task to Agent B (Company B) → Task status persists even if Agent A's system restarts.

#### 9. Agent & Tool Registry (Mesh)

**Purpose**: Manage discovery, registration, and selection from large pool of tools/agents.

**Components**:
- **Ontology**: Taxonomy of capabilities (categories, tags)
- **Descriptions**: What each agent/tool does
- **Requirements**: Input/output formats, dependencies
- **Performance Metrics**: Success rates, latency, cost

**Use Case**: Agent needs to choose which tool/agent to use from a "mesh" of 100+ options.

**Example**:
```yaml
agent_mesh:
  - name: "weather_agent"
    capabilities: ["weather_forecast", "climate_data"]
    performance:
      avg_latency_ms: 120
      success_rate: 0.98
    cost_per_call: 0.001
  - name: "flight_booking_agent"
    capabilities: ["flight_search", "booking", "cancellation"]
    performance:
      avg_latency_ms: 350
      success_rate: 0.95
    cost_per_call: 0.05
```

---

## Challenges in Multi-Agent Systems

### 1. Task Communication

**Problem**: Most frameworks use **messages**, not **structured async tasks**.

**Consequence**:
- Difficult to track task state (pending, in-progress, completed)
- No built-in retry or timeout handling
- Hard to resume tasks after failures

**Solution**: Use task-based communication (see Topic 6: Contract-Based Agents).

### 2. Task Allocation

**Problem**: Efficiently dividing complex tasks among agents.

**Challenges**:
- How to decompose task optimally?
- Which agent is best suited for each subtask?
- Feedback loops often left to developers to implement

**Solution**: Planner agents with task allocation algorithms, feedback loops for continuous improvement.

### 3. Coordinating Reasoning

**Problem**: Getting agents to **debate and reason together** effectively.

**Challenges**:
- Conflicting outputs from different agents
- No built-in consensus mechanisms
- Requires sophisticated coordination

**Solution**: Collaborative patterns with evaluator agents, voting mechanisms, or weighted averaging.

### 4. Managing Context

**Problem**: Keeping track of information, tasks, and conversations across agents.

**Challenges**:
- Context can grow large (token limits)
- What context is relevant for each agent?
- How to maintain context across handoffs?

**Solution**: Shared memory systems, context summarization, selective context passing.

### 5. Time and Cost

**Problem**: Multi-agent interactions are computationally **expensive**.

**Consequences**:
- Higher runtime costs (multiple LLM calls)
- Increased user latency (sequential dependencies)

**Solution**: Optimize for parallelization, use cheaper models for simple tasks, cache results.

### 6. Complexity

**Problem**: System-level complexity increases (like microservices).

**Challenges**:
- More components to develop and maintain
- Distributed debugging is harder
- Inter-agent communication can fail

**Solution**: Strong observability (see Topic 1: AgentOps), clear interfaces, comprehensive testing.

---

## Multi-Agent Evaluation

### Extending Single-Agent Evaluation

**Good News**: Multi-agent evaluation is a **clear progression** from single-agent evaluation.

**Unchanged**:
- **Agent Success Metrics** (business KPIs, goals, critical tasks)
- **Application Telemetry** (latency, errors)
- **Trace Instrumentation** (debugging complex interactions)

**Same Best Practices**:
- **Evaluating Trajectories** (now includes actions across multiple agents)
- **Evaluating Final Response** (single answer returned to user)

**Scalability**: Drill down and evaluate **each agent in isolation** AND **system as a whole**.

### Multi-Agent-Specific Evaluation Questions

#### 1. Cooperation and Coordination

**Question**: How well do agents work together to achieve common goals?

**Metrics**:
- Task completion rate (% goals achieved)
- Coordination efficiency (# communication rounds needed)
- Conflict resolution success (% disagreements resolved)

**Example**:
```
Measure: Did agents successfully collaborate to book a trip?
- Planner created valid itinerary?
- Booking agent completed reservations?
- Validator confirmed all details?
```

#### 2. Planning and Task Assignment

**Questions**:
- Did we come up with the right plan?
- Did we stick to the plan?
- Did child agents deviate from main plan?
- Did agents get lost in a "cul-de-sac" (stuck in loop)?

**Metrics**:
- Plan adherence (% tasks completed as planned)
- Deviation analysis (unplanned actions taken)
- Deadlock detection (agents stuck in loops)

**Example**:
```
Planner: "Research Agent, find 5 hotels"
Research Agent: Returns 3 hotels (deviation)
    ↓
Did we detect deviation?
Did we adapt plan or fail?
```

#### 3. Agent Utilization

**Questions**:
- How effectively do agents select the right agent?
- Do they choose correct mode (tool use, delegation, transfer)?

**Metrics**:
- Agent selection accuracy (% correct agent chosen)
- Mode selection accuracy (% correct interaction type)
- Resource utilization (% time agents are busy vs. idle)

**Example**:
```
User query: "What's the weather?"
Correct: Use weather_agent as tool
Incorrect: Delegate to general_knowledge_agent
```

#### 4. Scalability

**Questions**:
- Does quality improve as more agents are added?
- Does latency decrease (parallelization working)?
- Are we being more efficient or less efficient?

**Metrics**:
- Quality vs. # agents (accuracy, completeness)
- Latency vs. # agents (should decrease with parallelization)
- Cost efficiency (cost per task vs. # agents)

**Example**:
```
1 agent: 10s latency, 80% accuracy
3 agents (parallel): 6s latency, 90% accuracy ✅
3 agents (sequential): 25s latency, 90% accuracy ❌
```

### Multi-Agent Trajectory Evaluation

**Same metrics as single-agent** (see Topic 2):
- Exact match, in-order match, any-order match
- Precision, recall, single-tool use

**Difference**: Trajectory now spans **multiple agents**.

**Example Trajectory**:
```
1. Orchestrator Agent: Classify query as "booking"
2. Planner Agent: Decompose into [search, select, book]
3. Search Agent: Retrieve flight options
4. User Selection Agent: Present options to user
5. Booking Agent: Complete reservation
6. Validator Agent: Confirm booking details
```

**Evaluation**:
- Did each agent perform expected action?
- Were handoffs clean (context preserved)?
- Was the sequence optimal (no unnecessary steps)?

---

## Design Best Practices

### 1. Start Simple, Then Scale

**Approach**:
1. Build single-agent baseline
2. Identify bottlenecks or quality gaps
3. Add specialized agents only where needed
4. Measure impact of each new agent

**Anti-pattern**: Building multi-agent system from scratch without baseline.

### 2. Clear Agent Boundaries

**Principle**: Each agent should have **one clear responsibility**.

**Good Example**:
- Search Agent: Only searches, doesn't synthesize
- Synthesis Agent: Only synthesizes, doesn't search

**Bad Example**:
- "SmartAgent": Searches, synthesizes, validates, and books (too much responsibility)

### 3. Instrument Everything

**Requirements**:
- Log all inter-agent communications
- Track timing for each agent
- Capture errors and retries
- Record handoffs and context transfers

**Benefit**: Enables debugging and optimization (see Topic 1: AgentOps).

### 4. Design for Failure

**Assumptions**:
- Agents will fail (LLM API errors, tool failures)
- Communication will fail (network issues)
- Agents will produce incorrect outputs

**Strategies**:
- Retry logic with exponential backoff
- Fallback agents (if primary fails, use backup)
- Graceful degradation (partial results if complete solution unavailable)
- Timeout handling (don't wait forever)

**Example**:
```python
try:
    result = specialized_agent.execute(task)
except AgentError:
    result = fallback_general_agent.execute(task)  # Fallback
```

### 5. Optimize Communication

**Strategies**:
- **Minimize context passing**: Only send relevant information
- **Batch requests**: Combine multiple tasks in one message
- **Async communication**: Don't block on slow agents
- **Cache results**: Avoid redundant calls

**Example**:
```python
# Bad: Passing entire conversation history to every agent
agent.execute(task, context=full_conversation_history)  # 10K tokens

# Good: Passing only relevant context
agent.execute(task, context=recent_relevant_turns)  # 500 tokens
```

---

## Real-World Multi-Agent Architectures

See **Topic 7: Case Studies** for detailed examples:
- **Google Co-Scientist**: Scientific research multi-agent system
- **Automotive AI**: Hierarchical, diamond, peer-to-peer, collaborative, and adaptive loop patterns

---

## Key Takeaways

1. **Multi-agent systems** offer enhanced accuracy, efficiency, scalability, and fault tolerance
2. **Four main design patterns**: Sequential, Hierarchical, Collaborative, Competitive
3. **Agent types by function**: Planner, Retriever, Execution, Evaluator
4. **Nine critical components**: Interaction wrapper, memory, cognition, tools, routing, feedback, communication, remote communication, registry
5. **Six key challenges**: Task communication, allocation, coordination, context management, cost, complexity
6. **Multi-agent evaluation** extends single-agent evaluation with cooperation, planning, utilization, and scalability metrics
7. **Best practices**: Start simple, clear boundaries, instrument everything, design for failure, optimize communication

---

## Related Topics

- **Topic 1**: AgentOps & Operations (observability for multi-agent systems)
- **Topic 2**: Agent Evaluation Methodology (trajectory and response evaluation)
- **Topic 4**: Agentic RAG (retriever agents in action)
- **Topic 6**: Contract-Based Agents (task-based communication)
- **Topic 7**: Case Studies (real-world multi-agent examples)

---

## References

- Figure 7: Multi-agent topologies from LangGraph documentation
- Figure 8: User interacting with self-coordinating agents
- Table 2: Multi-agent system types comparison
- LangChain Multi-Agent Workflows: https://blog.langchain.dev/langgraph-multi-agent-workflows/
- LangGraph Multi-Agent Concepts: https://langchain-ai.github.io/langgraph/concepts/multi_agent/

---

**Next Topic**: [Agentic RAG](04_Agentic_RAG.md)
