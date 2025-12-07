# Agentic Pattern Code Templates

Copy-paste templates for common implementations.

## Tool Calling Templates

### MCP Server Template (Python)

```python
#!/usr/bin/env python3
"""MCP Server Template - Replace placeholder implementations."""

from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, Field
from typing import Optional
import httpx

mcp = FastMCP("your-service-name")

# ============================================================
# TOOL 1: Simple function with validation
# ============================================================

@mcp.tool()
async def get_data(
    query: str = Field(description="Search query"),
    limit: int = Field(default=10, ge=1, le=100, description="Max results")
) -> str:
    """
    Fetch data from your service.
    
    Args:
        query: What to search for
        limit: Maximum number of results (1-100)
    
    Returns:
        JSON string of results
    """
    # TODO: Replace with actual implementation
    async with httpx.AsyncClient() as client:
        response = await client.get(
            "https://your-api.com/search",
            params={"q": query, "limit": limit}
        )
        return response.text

# ============================================================
# TOOL 2: Structured input/output
# ============================================================

class CreateItemInput(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    description: Optional[str] = None
    tags: list[str] = Field(default_factory=list)

class CreateItemOutput(BaseModel):
    id: str
    created: bool
    message: str

@mcp.tool()
async def create_item(input: CreateItemInput) -> CreateItemOutput:
    """
    Create a new item in the system.
    
    Args:
        input: Item details including name and optional description
    
    Returns:
        Creation result with ID and status
    """
    # TODO: Replace with actual implementation
    return CreateItemOutput(
        id="item_123",
        created=True,
        message=f"Created item: {input.name}"
    )

# ============================================================
# TOOL 3: With error handling
# ============================================================

class ToolError(Exception):
    """Custom error for tool failures."""
    pass

@mcp.tool()
async def risky_operation(target_id: str) -> str:
    """
    Perform operation that may fail.
    
    Args:
        target_id: ID of the target resource
    
    Returns:
        Success message or raises ToolError
    """
    try:
        # TODO: Your implementation
        if not target_id.startswith("valid_"):
            raise ToolError(f"Invalid target: {target_id}")
        return f"Operation succeeded on {target_id}"
    except ToolError:
        raise
    except Exception as e:
        raise ToolError(f"Unexpected error: {str(e)}")

# ============================================================
# RUN SERVER
# ============================================================

if __name__ == "__main__":
    import sys
    transport = sys.argv[1] if len(sys.argv) > 1 else "stdio"
    mcp.run(transport=transport)  # "stdio" or "streamable-http"
```

### MCP Client Template (LangGraph)

```python
#!/usr/bin/env python3
"""MCP Client with LangGraph ReAct Agent."""

import asyncio
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import create_react_agent

# ============================================================
# CONFIGURATION
# ============================================================

MCP_SERVERS = {
    # Local server via stdio
    "local_tools": {
        "command": "python",
        "args": ["/path/to/your_mcp_server.py", "stdio"],
        "transport": "stdio"
    },
    # Remote server via HTTP
    "remote_tools": {
        "url": "http://your-server:8000/mcp",
        "transport": "streamable_http"
    }
}

MODEL = "anthropic:claude-sonnet-4-20250514"  # or "openai:gpt-4.1"

SYSTEM_PROMPT = """You are a helpful assistant with access to tools.

When to use tools:
- Use get_data for information retrieval
- Use create_item when user wants to create something
- Ask clarifying questions if request is ambiguous

Always explain what you're doing before calling a tool.
"""

# ============================================================
# MAIN AGENT
# ============================================================

async def run_agent(user_query: str) -> str:
    async with MultiServerMCPClient(MCP_SERVERS) as client:
        agent = create_react_agent(
            MODEL,
            client.get_tools(),
            prompt=SYSTEM_PROMPT
        )
        
        result = await agent.ainvoke({
            "messages": [{"role": "user", "content": user_query}]
        })
        
        return result["messages"][-1].content

# ============================================================
# INTERACTIVE LOOP
# ============================================================

async def main():
    print("Agent ready. Type 'quit' to exit.\n")
    
    while True:
        query = input("You: ").strip()
        if query.lower() in ("quit", "exit", "q"):
            break
        if not query:
            continue
        
        try:
            response = await run_agent(query)
            print(f"\nAssistant: {response}\n")
        except Exception as e:
            print(f"\nError: {e}\n")

if __name__ == "__main__":
    asyncio.run(main())
```

---

## Code Execution Templates

### Sandboxed Python Executor

```python
#!/usr/bin/env python3
"""Safe execution of LLM-generated Python code."""

import ast
import subprocess
import tempfile
import os
from dataclasses import dataclass
from typing import Optional

# ============================================================
# CONFIGURATION
# ============================================================

FORBIDDEN_IMPORTS = {
    "os", "sys", "subprocess", "shutil", "pathlib",
    "socket", "urllib", "requests", "httpx",
    "pickle", "marshal", "shelve",
    "__builtins__"
}

FORBIDDEN_CALLS = {
    "eval", "exec", "compile", "open", "input",
    "__import__", "globals", "locals", "vars"
}

MAX_EXECUTION_TIME = 30  # seconds
MAX_MEMORY_MB = 256

# ============================================================
# VALIDATION
# ============================================================

@dataclass
class ValidationResult:
    valid: bool
    errors: list[str]

def validate_python_code(code: str) -> ValidationResult:
    """Static analysis of Python code for safety."""
    errors = []
    
    # Check syntax
    try:
        tree = ast.parse(code)
    except SyntaxError as e:
        return ValidationResult(False, [f"Syntax error: {e}"])
    
    # Walk AST to find dangerous patterns
    for node in ast.walk(tree):
        # Check imports
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name.split('.')[0] in FORBIDDEN_IMPORTS:
                    errors.append(f"Forbidden import: {alias.name}")
        
        if isinstance(node, ast.ImportFrom):
            if node.module and node.module.split('.')[0] in FORBIDDEN_IMPORTS:
                errors.append(f"Forbidden import from: {node.module}")
        
        # Check function calls
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name):
                if node.func.id in FORBIDDEN_CALLS:
                    errors.append(f"Forbidden call: {node.func.id}")
            elif isinstance(node.func, ast.Attribute):
                # Check for dangerous method calls like os.system
                if node.func.attr in {"system", "popen", "spawn"}:
                    errors.append(f"Forbidden method: {node.func.attr}")
    
    return ValidationResult(len(errors) == 0, errors)

# ============================================================
# EXECUTION
# ============================================================

@dataclass
class ExecutionResult:
    success: bool
    output: str
    error: Optional[str]
    execution_time: float

def execute_python_safely(code: str, timeout: int = MAX_EXECUTION_TIME) -> ExecutionResult:
    """Execute Python code in isolated subprocess."""
    
    # Validate first
    validation = validate_python_code(code)
    if not validation.valid:
        return ExecutionResult(
            success=False,
            output="",
            error=f"Validation failed: {'; '.join(validation.errors)}",
            execution_time=0
        )
    
    # Create temp file
    with tempfile.NamedTemporaryFile(
        mode='w', suffix='.py', delete=False
    ) as f:
        f.write(code)
        temp_path = f.name
    
    try:
        import time
        start = time.time()
        
        result = subprocess.run(
            ["python", temp_path],
            capture_output=True,
            text=True,
            timeout=timeout,
            env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"}
        )
        
        execution_time = time.time() - start
        
        return ExecutionResult(
            success=result.returncode == 0,
            output=result.stdout,
            error=result.stderr if result.returncode != 0 else None,
            execution_time=execution_time
        )
    
    except subprocess.TimeoutExpired:
        return ExecutionResult(
            success=False,
            output="",
            error=f"Execution timed out after {timeout}s",
            execution_time=timeout
        )
    
    finally:
        os.unlink(temp_path)

# ============================================================
# LLM INTEGRATION
# ============================================================

CODE_GEN_PROMPT = """Generate Python code to accomplish the task.

CONSTRAINTS:
- Use only standard library (no external packages)
- No file I/O, network, or system calls
- Code must be self-contained
- Print the result to stdout

TASK: {task}

Respond with ONLY the Python code, no explanations or markdown.
"""

async def generate_and_execute(task: str, llm) -> dict:
    """Generate code with LLM and execute safely."""
    
    # Generate code
    response = await llm.ainvoke(CODE_GEN_PROMPT.format(task=task))
    code = response.content.strip()
    
    # Remove markdown code blocks if present
    if code.startswith("```"):
        code = code.split("```")[1]
        if code.startswith("python"):
            code = code[6:]
    
    # Execute
    result = execute_python_safely(code)
    
    return {
        "code": code,
        "success": result.success,
        "output": result.output,
        "error": result.error
    }
```

### SQL Execution with Validation

```python
#!/usr/bin/env python3
"""Safe execution of LLM-generated SQL."""

import re
from dataclasses import dataclass
from typing import Optional
import sqlparse

# ============================================================
# CONFIGURATION
# ============================================================

ALLOWED_TABLES = {"users", "orders", "products", "reviews"}
ALLOWED_OPERATIONS = {"SELECT"}  # Extend as needed
MAX_ROWS = 1000

# ============================================================
# VALIDATION
# ============================================================

@dataclass
class SQLValidation:
    valid: bool
    query_type: Optional[str]
    tables: set
    errors: list[str]

def validate_sql(query: str) -> SQLValidation:
    """Validate SQL query for safety."""
    errors = []
    
    # Parse SQL
    try:
        parsed = sqlparse.parse(query)
        if not parsed:
            return SQLValidation(False, None, set(), ["Empty query"])
    except Exception as e:
        return SQLValidation(False, None, set(), [f"Parse error: {e}"])
    
    stmt = parsed[0]
    query_type = stmt.get_type()
    
    # Check operation type
    if query_type not in ALLOWED_OPERATIONS:
        errors.append(f"Operation not allowed: {query_type}")
    
    # Extract and validate tables
    tables = set()
    query_upper = query.upper()
    
    # Simple table extraction (production should use proper parser)
    from_match = re.search(r'\bFROM\s+(\w+)', query_upper)
    if from_match:
        tables.add(from_match.group(1).lower())
    
    join_matches = re.findall(r'\bJOIN\s+(\w+)', query_upper)
    tables.update(t.lower() for t in join_matches)
    
    unauthorized = tables - ALLOWED_TABLES
    if unauthorized:
        errors.append(f"Unauthorized tables: {unauthorized}")
    
    # Check for dangerous patterns
    dangerous_patterns = [
        (r';\s*\w', "Multiple statements not allowed"),
        (r'--', "SQL comments not allowed"),
        (r'/\*', "Block comments not allowed"),
        (r'\bUNION\b', "UNION not allowed"),
        (r'\bINTO\s+OUTFILE\b', "File operations not allowed"),
        (r'\bLOAD_FILE\b', "File operations not allowed"),
    ]
    
    for pattern, message in dangerous_patterns:
        if re.search(pattern, query, re.IGNORECASE):
            errors.append(message)
    
    return SQLValidation(
        valid=len(errors) == 0,
        query_type=query_type,
        tables=tables,
        errors=errors
    )

# ============================================================
# EXECUTION
# ============================================================

def execute_sql_safely(query: str, connection) -> dict:
    """Execute validated SQL query."""
    
    # Validate
    validation = validate_sql(query)
    if not validation.valid:
        return {
            "success": False,
            "error": "; ".join(validation.errors),
            "rows": []
        }
    
    # Add LIMIT if not present
    if "LIMIT" not in query.upper():
        query = f"{query.rstrip(';')} LIMIT {MAX_ROWS}"
    
    try:
        cursor = connection.cursor()
        cursor.execute(query)
        
        columns = [desc[0] for desc in cursor.description]
        rows = cursor.fetchall()
        
        return {
            "success": True,
            "columns": columns,
            "rows": [dict(zip(columns, row)) for row in rows],
            "row_count": len(rows)
        }
    
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "rows": []
        }
```

---

## Multiagent Templates

### Sequential Workflow (LangGraph)

```python
#!/usr/bin/env python3
"""Sequential multiagent workflow template."""

from typing import TypedDict, Annotated
from langgraph.graph import StateGraph, START, END
from langchain_anthropic import ChatAnthropic

# ============================================================
# STATE DEFINITION
# ============================================================

class WorkflowState(TypedDict):
    input: str
    research: str
    analysis: str
    draft: str
    review: str
    final: str

# ============================================================
# AGENTS
# ============================================================

llm = ChatAnthropic(model="claude-sonnet-4-20250514")

def researcher(state: WorkflowState) -> dict:
    """Gather information on the topic."""
    response = llm.invoke(
        f"Research the following topic thoroughly. "
        f"Provide facts, data, and sources.\n\n"
        f"Topic: {state['input']}"
    )
    return {"research": response.content}

def analyst(state: WorkflowState) -> dict:
    """Analyze research findings."""
    response = llm.invoke(
        f"Analyze these research findings. "
        f"Identify key insights and patterns.\n\n"
        f"Research:\n{state['research']}"
    )
    return {"analysis": response.content}

def writer(state: WorkflowState) -> dict:
    """Draft content based on analysis."""
    response = llm.invoke(
        f"Write a comprehensive draft based on this analysis.\n\n"
        f"Analysis:\n{state['analysis']}"
    )
    return {"draft": response.content}

def reviewer(state: WorkflowState) -> dict:
    """Review and provide feedback."""
    response = llm.invoke(
        f"Review this draft. Identify issues and suggest improvements.\n\n"
        f"Draft:\n{state['draft']}"
    )
    return {"review": response.content}

def finalizer(state: WorkflowState) -> dict:
    """Incorporate feedback into final version."""
    response = llm.invoke(
        f"Revise the draft incorporating this feedback.\n\n"
        f"Draft:\n{state['draft']}\n\n"
        f"Feedback:\n{state['review']}"
    )
    return {"final": response.content}

# ============================================================
# BUILD GRAPH
# ============================================================

def create_workflow():
    graph = StateGraph(WorkflowState)
    
    # Add nodes
    graph.add_node("researcher", researcher)
    graph.add_node("analyst", analyst)
    graph.add_node("writer", writer)
    graph.add_node("reviewer", reviewer)
    graph.add_node("finalizer", finalizer)
    
    # Add edges (sequential)
    graph.add_edge(START, "researcher")
    graph.add_edge("researcher", "analyst")
    graph.add_edge("analyst", "writer")
    graph.add_edge("writer", "reviewer")
    graph.add_edge("reviewer", "finalizer")
    graph.add_edge("finalizer", END)
    
    return graph.compile()

# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":
    workflow = create_workflow()
    result = workflow.invoke({"input": "Impact of AI on software development"})
    print(result["final"])
```

### Router Pattern

```python
#!/usr/bin/env python3
"""Router pattern for specialized agents."""

from pydantic import BaseModel
from typing import Literal
from langchain_anthropic import ChatAnthropic

# ============================================================
# ROUTE DECISION
# ============================================================

class RouteDecision(BaseModel):
    """Structured routing decision."""
    agent: Literal["technical", "creative", "analytical", "general"]
    confidence: float
    reasoning: str

llm = ChatAnthropic(model="claude-sonnet-4-20250514")

def route_query(query: str) -> RouteDecision:
    """Determine best agent for query."""
    
    router_llm = llm.with_structured_output(RouteDecision)
    
    return router_llm.invoke(
        f"""Classify this query and route to the best agent.

AGENTS:
- technical: Code, debugging, architecture, APIs, DevOps
- creative: Writing, design, brainstorming, marketing copy
- analytical: Data analysis, research, comparisons, reports
- general: Conversation, simple questions, clarifications

QUERY: {query}

Choose the single best agent."""
    )

# ============================================================
# SPECIALIZED AGENTS
# ============================================================

def technical_agent(query: str) -> str:
    response = llm.invoke(
        f"You are an expert software engineer. "
        f"Provide technical, implementation-focused answers.\n\n{query}"
    )
    return response.content

def creative_agent(query: str) -> str:
    response = llm.invoke(
        f"You are a creative professional. "
        f"Provide imaginative, engaging responses.\n\n{query}"
    )
    return response.content

def analytical_agent(query: str) -> str:
    response = llm.invoke(
        f"You are a data analyst. "
        f"Provide structured, evidence-based analysis.\n\n{query}"
    )
    return response.content

def general_agent(query: str) -> str:
    response = llm.invoke(query)
    return response.content

# ============================================================
# MAIN ROUTER
# ============================================================

AGENTS = {
    "technical": technical_agent,
    "creative": creative_agent,
    "analytical": analytical_agent,
    "general": general_agent
}

def handle_query(query: str, verbose: bool = False) -> str:
    """Route and handle query."""
    
    route = route_query(query)
    
    if verbose:
        print(f"Routing to: {route.agent} (confidence: {route.confidence:.2f})")
        print(f"Reasoning: {route.reasoning}")
    
    return AGENTS[route.agent](query)

# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":
    queries = [
        "How do I implement a binary search tree?",
        "Write a tagline for a coffee shop",
        "Compare the market share of AWS vs Azure",
        "What time is it?"
    ]
    
    for q in queries:
        print(f"\nQuery: {q}")
        print("-" * 40)
        response = handle_query(q, verbose=True)
        print(f"\nResponse: {response[:200]}...")
```

### Parallel Execution Pattern

```python
#!/usr/bin/env python3
"""Parallel agent execution for independent subtasks."""

import asyncio
from typing import TypedDict
from langchain_anthropic import ChatAnthropic

# ============================================================
# CONFIGURATION
# ============================================================

llm = ChatAnthropic(model="claude-sonnet-4-20250514")

class ParallelResult(TypedDict):
    agent: str
    result: str
    error: str | None

# ============================================================
# PARALLEL AGENTS
# ============================================================

async def run_agent(name: str, prompt: str) -> ParallelResult:
    """Run single agent asynchronously."""
    try:
        response = await llm.ainvoke(prompt)
        return ParallelResult(
            agent=name,
            result=response.content,
            error=None
        )
    except Exception as e:
        return ParallelResult(
            agent=name,
            result="",
            error=str(e)
        )

async def run_parallel_analysis(topic: str) -> dict:
    """Run multiple analysis perspectives in parallel."""
    
    agents = {
        "market": f"Analyze market trends for: {topic}",
        "technical": f"Analyze technical feasibility of: {topic}",
        "financial": f"Analyze financial implications of: {topic}",
        "risk": f"Analyze risks and challenges for: {topic}"
    }
    
    # Run all agents concurrently
    tasks = [
        run_agent(name, prompt) 
        for name, prompt in agents.items()
    ]
    
    results = await asyncio.gather(*tasks)
    
    # Aggregate results
    return {r["agent"]: r for r in results}

async def synthesize_results(results: dict, topic: str) -> str:
    """Combine parallel results into unified report."""
    
    sections = []
    for agent, result in results.items():
        if result["error"]:
            sections.append(f"## {agent.title()}\n*Error: {result['error']}*")
        else:
            sections.append(f"## {agent.title()}\n{result['result']}")
    
    combined = "\n\n".join(sections)
    
    response = await llm.ainvoke(
        f"Synthesize these perspectives into a cohesive executive summary.\n\n"
        f"Topic: {topic}\n\n"
        f"Perspectives:\n{combined}"
    )
    
    return response.content

# ============================================================
# RUN
# ============================================================

async def main():
    topic = "Adopting AI agents in enterprise software"
    
    print(f"Analyzing: {topic}")
    print("Running parallel analysis...")
    
    results = await run_parallel_analysis(topic)
    
    print("\nIndividual results:")
    for agent, result in results.items():
        status = "✓" if not result["error"] else "✗"
        print(f"  {status} {agent}")
    
    print("\nSynthesizing...")
    summary = await synthesize_results(results, topic)
    
    print("\n" + "=" * 60)
    print("EXECUTIVE SUMMARY")
    print("=" * 60)
    print(summary)

if __name__ == "__main__":
    asyncio.run(main())
```
