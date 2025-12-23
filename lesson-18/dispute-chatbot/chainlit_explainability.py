import chainlit as cl
from typing import Dict, Any, List
import json

async def render_blackbox_trace(trace_data: Dict[str, Any]):
    """
    Renders the BlackBox trace (input/output/timing) in the sidebar or as an expandable element.
    """
    content = json.dumps(trace_data, indent=2)
    await cl.Message(
        content=f"**BlackBox Trace**\n```json\n{content}\n```",
        author="BlackBox",
        elements=[
            cl.Text(name="blackbox_trace", content=content, display="side", language="json")
        ]
    ).send()

async def render_agent_facts(agent_metadata: Dict[str, Any]):
    """
    Renders AgentFacts (identity, model version, capabilities).
    """
    content = f"""
    **Agent Identity Verified**
    - **Model**: {agent_metadata.get('model', 'unknown')}
    - **Version**: {agent_metadata.get('version', 'unknown')}
    - **Capabilities**: {', '.join(agent_metadata.get('capabilities', []))}
    """
    await cl.Message(
        content=content,
        author="AgentFacts",
        elements=[
            cl.Text(name="agent_facts", content=json.dumps(agent_metadata, indent=2), display="side", language="json")
        ]
    ).send()

async def render_guardrails_status(validation_results: Dict[str, Any]):
    """
    Renders GuardRails validation status (PII detection, etc.).
    """
    status = "✅ PASS" if validation_results.get("passed", False) else "❌ FAIL"
    content = f"**GuardRails Status**: {status}\n\nIssues: {validation_results.get('issues', 'None')}"
    
    await cl.Message(
        content=content,
        author="GuardRails",
         elements=[
            cl.Text(name="guardrails_log", content=json.dumps(validation_results, indent=2), display="side", language="json")
        ]
    ).send()

async def render_phase_rationale(phase: str, rationale: str):
    """
    Renders PhaseLogger rationale for a specific phase transition.
    """
    await cl.Message(
        content=f"**Phase Transition: {phase}**\n\n> {rationale}",
        author="PhaseLogger"
    ).send()

