# Tool Calling Implementation Templates

## MCP Server Template (Python)

```python
"""
MCP Server Template for Tool Calling Pattern
---------------------------------------------
Use this template to expose functions as tools that LLMs can invoke.
"""

from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, Field
from typing import Optional, List
from enum import Enum
from datetime import datetime
import httpx

# Initialize MCP server with a descriptive name
mcp = FastMCP("your_service_name")


# ============================================================================
# STEP 1: Define your data models (for type safety and clear contracts)
# ============================================================================

class StatusEnum(str, Enum):
    """Use enums to constrain valid values - helps LLM accuracy."""
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"


class RequestParams(BaseModel):
    """Input parameters for your tool."""
    query: str = Field(..., description="Search query string")
    limit: int = Field(default=10, ge=1, le=100, description="Max results (1-100)")
    filter_status: Optional[StatusEnum] = Field(
        default=None, 
        description="Filter by status: pending, completed, or failed"
    )


class ResponseItem(BaseModel):
    """Structured response from your tool."""
    id: str
    title: str
    status: StatusEnum
    created_at: datetime
    score: float


class ToolResponse(BaseModel):
    """Wrapper for tool responses with metadata."""
    success: bool
    items: List[ResponseItem]
    total_count: int
    message: Optional[str] = None


# ============================================================================
# STEP 2: Implement your tool functions
# ============================================================================

@mcp.tool()
async def search_items(
    query: str,
    limit: int = 10,
    filter_status: Optional[str] = None
) -> ToolResponse:
    """
    Search for items matching the given query.
    
    Use this tool when you need to find items based on keywords or filters.
    The search is case-insensitive and supports partial matching.
    
    Args:
        query: Search keywords (e.g., "quarterly report", "budget 2024")
        limit: Maximum number of results to return (default: 10, max: 100)
        filter_status: Optional filter - one of: pending, completed, failed
        
    Returns:
        ToolResponse containing matching items with their metadata
        
    Example:
        search_items("quarterly report", limit=5, filter_status="completed")
        Returns up to 5 completed items matching "quarterly report"
    """
    try:
        # Your actual implementation here
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://api.yourservice.com/search",
                params={
                    "q": query,
                    "limit": limit,
                    "status": filter_status
                }
            )
            response.raise_for_status()
            data = response.json()
            
        items = [ResponseItem(**item) for item in data["results"]]
        
        return ToolResponse(
            success=True,
            items=items,
            total_count=data["total"],
            message=f"Found {len(items)} items matching '{query}'"
        )
        
    except httpx.HTTPStatusError as e:
        return ToolResponse(
            success=False,
            items=[],
            total_count=0,
            message=f"API error: {e.response.status_code}"
        )
    except Exception as e:
        return ToolResponse(
            success=False,
            items=[],
            total_count=0,
            message=f"Error: {str(e)}"
        )


@mcp.tool()
async def create_item(
    title: str,
    description: str,
    priority: int = 1
) -> dict:
    """
    Create a new item with the specified details.
    
    Use this tool to create new entries in the system.
    
    Args:
        title: Item title (required, max 200 characters)
        description: Detailed description of the item
        priority: Priority level 1-5 (1=lowest, 5=highest, default: 1)
        
    Returns:
        dict with created item ID and confirmation message
        
    Example:
        create_item("Review Q3 Budget", "Analyze spending patterns", priority=3)
    """
    # Implementation
    return {
        "success": True,
        "item_id": "new_item_123",
        "message": f"Created item: {title}"
    }


@mcp.tool()
async def get_item_details(item_id: str) -> dict:
    """
    Retrieve detailed information about a specific item.
    
    Args:
        item_id: Unique identifier for the item (e.g., "item_123")
        
    Returns:
        Complete item details including metadata and history
    """
    # Implementation
    return {"id": item_id, "details": "..."}


# ============================================================================
# STEP 3: Run the server
# ============================================================================

if __name__ == "__main__":
    # For local development (same machine)
    # mcp.run(transport="stdio")
    
    # For network access (different machines/languages)
    mcp.run(transport="streamable-http")
```

## MCP Client Template (Python with LangGraph)

```python
"""
MCP Client Template with LangGraph ReAct Agent
-----------------------------------------------
Use this template to create agents that consume MCP tools.
"""

import asyncio
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import create_react_agent


async def create_agent_with_tools():
    """Create a ReAct agent connected to MCP servers."""
    
    # Configure MCP server connections
    mcp_config = {
        # Local server via stdio
        "local_service": {
            "command": "python",
            "args": ["/path/to/your_mcp_server.py"],
            "transport": "stdio",
        },
        # Remote server via HTTP
        "remote_service": {
            "url": "http://api.yourservice.com:8000/mcp",
            "transport": "streamable_http",
        },
        # Another remote service
        "analytics": {
            "url": "http://analytics.internal:8001/mcp",
            "transport": "streamable_http",
        }
    }
    
    async with MultiServerMCPClient(mcp_config) as client:
        # Create ReAct agent with all available tools
        agent = create_react_agent(
            model="anthropic:claude-sonnet-4-20250514",
            tools=client.get_tools(),
            prompt=SYSTEM_PROMPT
        )
        
        return agent, client


# System prompt for the agent
SYSTEM_PROMPT = """
You are a helpful assistant with access to specialized tools.

## Available Capabilities
- Search and retrieve items from the database
- Create new items with priorities
- Get detailed information about specific items

## Guidelines
1. Always confirm what the user needs before taking action
2. Use the most specific tool for the task
3. If a tool returns an error, explain what happened and suggest alternatives
4. Summarize results clearly and concisely

## Tool Usage Examples
- To find items: use search_items with relevant keywords
- To create items: use create_item with title and description
- To get details: use get_item_details with the item ID
"""


async def run_conversation():
    """Example conversation with the agent."""
    
    agent, client = await create_agent_with_tools()
    
    # Single query
    response = await agent.ainvoke({
        "messages": [{
            "role": "user",
            "content": "Find all completed quarterly reports from this year"
        }]
    })
    
    print(response["messages"][-1].content)
    
    # Multi-turn conversation
    conversation = []
    
    queries = [
        "What items are currently pending?",
        "Create a new high-priority item to review those pending items",
        "Show me the details of the item you just created"
    ]
    
    for query in queries:
        conversation.append({"role": "user", "content": query})
        response = await agent.ainvoke({"messages": conversation})
        assistant_message = response["messages"][-1]
        conversation.append({
            "role": "assistant", 
            "content": assistant_message.content
        })
        print(f"User: {query}")
        print(f"Agent: {assistant_message.content}\n")


if __name__ == "__main__":
    asyncio.run(run_conversation())
```

## OpenAI-Style Function Calling (For Comparison)

```python
"""
Direct Function Calling (OpenAI-style)
--------------------------------------
Lower-level implementation without MCP abstraction.
Use this when you need more control or MCP isn't available.
"""

import json
from openai import OpenAI

client = OpenAI()

# Define tools in OpenAI format
tools = [
    {
        "type": "function",
        "name": "search_items",
        "description": "Search for items matching keywords",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Search keywords"
                },
                "limit": {
                    "type": "integer",
                    "description": "Max results (1-100)",
                    "default": 10
                },
                "status": {
                    "type": "string",
                    "enum": ["pending", "completed", "failed"],
                    "description": "Filter by status"
                }
            },
            "required": ["query"]
        }
    }
]

# Your actual function implementations
def search_items(query: str, limit: int = 10, status: str = None) -> dict:
    """Actual search implementation."""
    # Your logic here
    return {"results": [], "total": 0}


# Map function names to implementations
FUNCTION_MAP = {
    "search_items": search_items,
}


def run_with_tools(user_message: str) -> str:
    """Complete flow: prompt → tool call → result → final response."""
    
    messages = [{"role": "user", "content": user_message}]
    
    # Step 1: Initial call - model may request tool use
    response = client.chat.completions.create(
        model="gpt-4.1",
        messages=messages,
        tools=tools,
    )
    
    assistant_message = response.choices[0].message
    
    # Step 2: Check if model wants to use a tool
    if assistant_message.tool_calls:
        messages.append(assistant_message)
        
        # Step 3: Execute each tool call
        for tool_call in assistant_message.tool_calls:
            function_name = tool_call.function.name
            function_args = json.loads(tool_call.function.arguments)
            
            # Execute the function
            function = FUNCTION_MAP.get(function_name)
            if function:
                result = function(**function_args)
            else:
                result = {"error": f"Unknown function: {function_name}"}
            
            # Step 4: Add result to messages
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": json.dumps(result)
            })
        
        # Step 5: Get final response with tool results
        final_response = client.chat.completions.create(
            model="gpt-4.1",
            messages=messages,
            tools=tools,
        )
        
        return final_response.choices[0].message.content
    
    # No tool call needed - return direct response
    return assistant_message.content


if __name__ == "__main__":
    result = run_with_tools("Find all pending items about budgets")
    print(result)
```
