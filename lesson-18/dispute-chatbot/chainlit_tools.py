import chainlit as cl
from typing import Dict, Any
import json

async def visualize_tool_call(tool_name: str, input_data: Dict[str, Any], output_data: Dict[str, Any]):
    """
    Visualizes an MCP tool call within a Chainlit step.
    """
    async with cl.Step(name=tool_name, type="tool") as step:
        step.input = json.dumps(input_data, indent=2)
        step.output = json.dumps(output_data, indent=2)
        # We don't explicitly send the step, exiting the context manager sends it.

