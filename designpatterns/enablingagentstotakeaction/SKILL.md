---
name: agentic-patterns
description: "Implementation patterns for building agentic AI systems. Use when working with: (1) Tool Calling - enabling LLMs to invoke external functions via MCP or native APIs, (2) Code Execution - having LLMs generate DSL/code executed in sandboxes, (3) Multiagent Collaboration - orchestrating multiple specialized agents. Applies to LangGraph, CrewAI, AG2, PydanticAI, or custom agent frameworks."
license: MIT
---

# Agentic AI Patterns

Patterns for enabling LLM applications to interact with the world: invoke tools, execute code, and collaborate as specialized agents.

## Pattern Selection

| Signal | Pattern | Rationale |
|--------|---------|-----------|
| Need real-time data, API calls, calculations | Tool Calling | Discrete function invocations |
| Need graphs, SQL, DSL output | Code Execution | LLM generates code for external system |
| Task requires multiple perspectives/expertise | Multiagent | Division of cognitive labor |
| Sequential steps with handoffs | Multiagent (hierarchical) | Prompt chaining or router |
| Parallel independent subtasks | Multiagent (peer) | Concurrent execution |

## Pattern 21: Tool Calling

### Core Mechanism

LLM emits special tokens → client extracts function + args → invokes function → returns result to LLM → LLM incorporates in response.

### Implementation Approaches

#### Option A: Native Function Calling (Low-level)

Use when: Maximum control needed, single LLM provider, simple tool set.

```python
# 1. Define tool schema
tools = [{
    "type": "function",
    "name": "book_flight",
    "description": "Books a flight using airline API",
    "parameters": {
        "type": "object",
        "properties": {
            "flight_code": {"type": "string", "description": "IATA code e.g. AA 123"},
            "departure_date": {"type": "string", "description": "YYYY-MM-DD"},
            "cabin_class": {"type": "string", "enum": ["economy", "business", "first"]}
        },
        "required": ["flight_code", "departure_date"]
    }
}]

# 2. Call model with tools
response = client.chat.completions.create(
    model="gpt-4.1",
    messages=[{"role": "user", "content": user_input}],
    tools=tools
)

# 3. Process tool calls
if response.choices[0].message.tool_calls:
    tool_call = response.choices[0].message.tool_calls[0]
    args = json.loads(tool_call.function.arguments)
    result = book_flight(**args)  # YOUR function
    
    # 4. Return result to model
    messages.append(response.choices[0].message)
    messages.append({
        "role": "tool",
        "tool_call_id": tool_call.id,
        "content": json.dumps(result)
    })
    final_response = client.chat.completions.create(
        model="gpt-4.1", messages=messages, tools=tools
    )
```

#### Option B: MCP (Model Context Protocol)

Use when: Multi-provider support needed, tools shared across projects, team collaboration.

**Server (expose tools):**

```python
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("my-tools")

@mcp.tool()
async def get_weather(latitude: float, longitude: float) -> str:
    """Fetches weather from National Weather Service API.
    
    Args:
        latitude: Geographic latitude (-90 to 90)
        longitude: Geographic longitude (-180 to 180)
    
    Returns:
        Weather forecast as JSON string
    """
    response = requests.get(f"https://api.weather.gov/points/{latitude},{longitude}")
    metadata = response.json()
    forecast_url = metadata["properties"]["forecast"]
    weather = requests.get(forecast_url).json()
    return json.dumps(weather["properties"]["periods"])

if __name__ == "__main__":
    mcp.run(transport="streamable-http")  # or "stdio" for local
```

**Client (consume tools):**

```python
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import create_react_agent

async with MultiServerMCPClient({
    "weather": {
        "url": "http://localhost:8000/mcp",
        "transport": "streamable_http"
    },
    "flights": {
        "command": "python",
        "args": ["/path/to/flight_tools.py"],
        "transport": "stdio"
    }
}) as client:
    agent = create_react_agent(
        "anthropic:claude-sonnet-4-20250514",
        client.get_tools()
    )
    result = await agent.ainvoke({"messages": [{"role": "user", "content": query}]})
```

### Tool Design Principles

1. **Self-descriptive naming**: `get_current_stock_price` not `fetch_data`
2. **Typed parameters with enums**: Constrain inputs for reliability
3. **Detailed docstrings**: LLM uses these to decide when/how to call
4. **Descriptive error messages**: Enable Reflection pattern for retry
5. **Limit to 3-10 tools**: Accuracy degrades with more

### Prompt Injection Defense

Select one or combine based on risk:

| Pattern | Description | Use When |
|---------|-------------|----------|
| Action-Selector | Predefined actions only, no tool feedback to agent | High-risk actions |
| Plan-Then-Execute | Fixed plan, no deviation despite tool results | Predictable workflows |
| Dual-LLM | Privileged planner + sandboxed executor | Mixed trust data |
| Context-Minimization | Strip original prompt from subsequent steps | Multi-step chains |

---

## Pattern 22: Code Execution

### Core Mechanism

User request → LLM generates DSL/code → sandbox executes → output returned.

### When to Use

- Database queries (SQL generation)
- Data visualization (Matplotlib, Mermaid)
- Image manipulation (ImageMagick commands)
- Complex calculations
- Any task with existing DSL

### Implementation

```python
import subprocess
import tempfile

def execute_code_safely(code: str, language: str, timeout: int = 30) -> dict:
    """Execute LLM-generated code in sandbox.
    
    Args:
        code: Generated code string
        language: "python", "sql", "mermaid", "graphviz"
        timeout: Max execution seconds
    
    Returns:
        {"success": bool, "output": str, "error": str}
    """
    with tempfile.NamedTemporaryFile(mode='w', suffix=get_ext(language), delete=False) as f:
        f.write(code)
        f.flush()
        
        try:
            if language == "python":
                result = subprocess.run(
                    ["python", f.name],
                    capture_output=True, text=True, timeout=timeout,
                    # SECURITY: Use container/sandbox in production
                )
            elif language == "graphviz":
                output_path = f.name.replace('.dot', '.png')
                result = subprocess.run(
                    ["dot", "-Tpng", f.name, "-o", output_path],
                    capture_output=True, text=True, timeout=timeout
                )
                return {"success": True, "output": output_path, "error": ""}
            # ... other languages
            
            return {
                "success": result.returncode == 0,
                "output": result.stdout,
                "error": result.stderr
            }
        except subprocess.TimeoutExpired:
            return {"success": False, "output": "", "error": "Timeout"}
```

### Code Generation Prompt Pattern

```python
system_prompt = """Generate {language} code to accomplish the task.

CONSTRAINTS:
- Output ONLY the code, no explanations
- Include error handling
- Use only standard library unless specified

EXAMPLE:
Task: Create bar chart of sales by region
Code:
```python
import matplotlib.pyplot as plt
data = {{"North": 100, "South": 150, "East": 120}}
plt.bar(data.keys(), data.values())
plt.savefig("output.png")
```
"""
```

### Validation Before Execution

```python
def validate_generated_code(code: str, language: str) -> tuple[bool, str]:
    """Pre-execution validation."""
    if language == "python":
        try:
            import ast
            ast.parse(code)
        except SyntaxError as e:
            return False, f"Syntax error: {e}"
        
        # Check for dangerous patterns
        dangerous = ["os.system", "subprocess", "eval(", "exec(", "__import__"]
        for pattern in dangerous:
            if pattern in code:
                return False, f"Forbidden pattern: {pattern}"
    
    elif language == "sql":
        # Prevent destructive operations
        forbidden = ["DROP", "DELETE", "TRUNCATE", "ALTER"]
        for kw in forbidden:
            if kw in code.upper():
                return False, f"Forbidden SQL: {kw}"
    
    return True, ""
```

### Reflection Loop for Code Errors

```python
async def generate_with_retry(task: str, max_attempts: int = 3) -> str:
    """Generate code with error-driven refinement."""
    code = await llm.generate(f"Write Python code to: {task}")
    
    for attempt in range(max_attempts):
        valid, error = validate_generated_code(code, "python")
        if not valid:
            code = await llm.generate(
                f"Fix this error in your code:\nError: {error}\nCode:\n{code}"
            )
            continue
            
        result = execute_code_safely(code, "python")
        if result["success"]:
            return result["output"]
        
        code = await llm.generate(
            f"Your code failed with:\n{result['error']}\nFix it:\n{code}"
        )
    
    raise RuntimeError(f"Failed after {max_attempts} attempts")
```

---

## Pattern 23: Multiagent Collaboration

### Architecture Selection

| Architecture | When to Use | Coordination |
|--------------|-------------|--------------|
| **Sequential/Chain** | Linear dependencies, each step feeds next | Implicit (output→input) |
| **Router** | Different specialists for different inputs | Classifier selects agent |
| **Hierarchical** | Complex tasks needing decomposition | Manager delegates to workers |
| **Peer-to-peer** | Need consensus, multiple perspectives | Voting/discussion |
| **Market-based** | Dynamic resource allocation | Auction/bidding |

### Sequential Workflow (LangGraph)

```python
from langgraph.graph import StateGraph, START, END
from typing import TypedDict

class State(TypedDict):
    topic: str
    draft: str
    review: str
    final: str

def researcher(state: State) -> State:
    """Research the topic."""
    result = llm.invoke(f"Research: {state['topic']}")
    return {"draft": result.content}

def reviewer(state: State) -> State:
    """Review and critique."""
    result = llm.invoke(f"Review this draft:\n{state['draft']}")
    return {"review": result.content}

def finalizer(state: State) -> State:
    """Incorporate feedback."""
    result = llm.invoke(
        f"Revise based on feedback:\nDraft: {state['draft']}\nFeedback: {state['review']}"
    )
    return {"final": result.content}

# Build graph
graph = StateGraph(State)
graph.add_node("researcher", researcher)
graph.add_node("reviewer", reviewer)
graph.add_node("finalizer", finalizer)
graph.add_edge(START, "researcher")
graph.add_edge("researcher", "reviewer")
graph.add_edge("reviewer", "finalizer")
graph.add_edge("finalizer", END)

app = graph.compile()
result = app.invoke({"topic": "Quantum computing basics"})
```

### Router Pattern

```python
from pydantic import BaseModel
from typing import Literal

class RouteDecision(BaseModel):
    agent: Literal["technical", "creative", "analytical"]
    reasoning: str

def route_query(query: str) -> str:
    """Route to specialized agent."""
    decision = llm.with_structured_output(RouteDecision).invoke(
        f"Classify this query for routing:\n{query}\n"
        "- technical: code, debugging, architecture\n"
        "- creative: writing, design, ideation\n"
        "- analytical: data analysis, research, comparison"
    )
    
    agents = {
        "technical": technical_agent,
        "creative": creative_agent,
        "analytical": analytical_agent
    }
    return agents[decision.agent].invoke(query)
```

### Hierarchical with Delegation (AG2/AutoGen)

```python
from autogen import ConversableAgent, LLMConfig

llm_config = LLMConfig(model="gpt-4.1", temperature=0.2)

# Manager agent
with llm_config:
    manager = ConversableAgent(
        name="project_manager",
        system_message="""You coordinate a team. For each task:
1. Break into subtasks
2. Assign to appropriate specialist
3. Synthesize results

Team: researcher (facts), analyst (insights), writer (prose)"""
    )
    
    researcher = ConversableAgent(
        name="researcher",
        system_message="You find facts and data. Be thorough and cite sources."
    )
    
    analyst = ConversableAgent(
        name="analyst", 
        system_message="You analyze data and extract insights. Be quantitative."
    )
    
    writer = ConversableAgent(
        name="writer",
        system_message="You write clear, engaging prose. Be concise."
    )

# Manager orchestrates
result = manager.initiate_chat(
    researcher,
    message="Research market size for AI agents in 2025"
)
```

### Peer-to-Peer with Voting (CrewAI)

```python
from crewai import Agent, Task, Crew

agents = [
    Agent(
        role="Security Reviewer",
        goal="Identify security vulnerabilities",
        backstory="Senior security engineer"
    ),
    Agent(
        role="Performance Reviewer", 
        goal="Identify performance issues",
        backstory="Systems performance expert"
    ),
    Agent(
        role="Maintainability Reviewer",
        goal="Assess code maintainability",
        backstory="Software architect focused on clean code"
    )
]

review_task = Task(
    description="Review this code and reach consensus on approval:\n{code}",
    expected_output="APPROVE or REJECT with unified reasoning",
    agents=agents  # All participate
)

crew = Crew(agents=agents, tasks=[review_task], process="hierarchical")
result = crew.kickoff(inputs={"code": code_to_review})
```

### Agent-to-Agent Protocol (A2A)

For cross-framework communication:

```python
# Server: Expose agent via A2A
from pydantic_ai import Agent
agent = Agent('anthropic:claude-sonnet-4-20250514', system_prompt="...")
app = agent.to_a2a()
# Run with: uvicorn app:app --port 8093

# Client: Call remote agent
from a2a_client import A2AClient
client = A2AClient("http://agent-server:8093")
result = await client.send_task({
    "message": {"role": "user", "parts": [{"text": "Analyze this..."}]}
})
```

---

## Common Failure Modes & Mitigations

### Tool Calling Failures

| Failure | Symptom | Mitigation |
|---------|---------|------------|
| Wrong tool selected | Irrelevant tool called | Improve tool descriptions, add few-shot examples |
| Bad arguments | Type errors, missing params | Use enums, add validation, structured output |
| Tool timeout | Hung requests | Set timeouts, implement retries |
| Prompt injection | Unexpected tool calls | Use defense patterns above |

### Multiagent Failures

| Failure | Symptom | Mitigation |
|---------|---------|------------|
| Infinite loops | Agents keep handing off | Add max_turns, termination conditions |
| Context loss | Agent forgets prior steps | Include summary in handoff |
| Role confusion | Agent acts outside scope | Stronger system prompts |
| Error propagation | Early error cascades | Add verification agents |

### Reliability Guidelines

1. **Start simple**: Single agent → sequential → complex only if needed
2. **Parallelize when possible**: Independent subtasks reduce latency
3. **Add human-in-the-loop**: For high-stakes decisions
4. **Implement observability**: Log all agent interactions
5. **Test adversarially**: Probe for prompt injection, edge cases
6. **Expect 40-80% task failure** in complex multiagent systems—design for graceful degradation

---

## Framework Quick Reference

| Framework | Best For | Tool Calling | Multiagent |
|-----------|----------|--------------|------------|
| **LangGraph** | Complex workflows, state machines | MCP adapter | Graph-based |
| **PydanticAI** | Type-safe, structured outputs | Native + MCP | A2A export |
| **CrewAI** | Role-based collaboration | Native | Built-in |
| **AG2/AutoGen** | Conversational agents | Native | Built-in |
| **LiteLLM** | Multi-provider abstraction | Unified API | Manual |

---

## Dependencies

```bash
# Core
pip install langchain langgraph pydantic-ai

# MCP
pip install mcp langchain-mcp-adapters

# Multiagent frameworks (pick one)
pip install crewai
pip install ag2

# Code execution sandbox
pip install docker  # For containerized execution
```
