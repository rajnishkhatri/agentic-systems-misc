import chainlit as cl
import asyncio
from typing import Dict, Any

from chainlit_explainability import (
    render_blackbox_trace,
    render_agent_facts,
    render_guardrails_status,
    render_phase_rationale
)
from chainlit_tools import visualize_tool_call

@cl.step(type="process")
async def classify_dispute_step(dispute_id: str) -> Dict[str, Any]:
    """
    Simulates the CLASSIFY phase.
    """
    await asyncio.sleep(1) # Simulate processing
    
    # Mock tool call
    tool_input = {"dispute_id": dispute_id}
    tool_output = {
        "reason_code": "10.4",
        "network": "visa",
        "deadline": "2025-01-15",
        "confidence": 0.95
    }
    await visualize_tool_call("classify_dispute", tool_input, tool_output)
    
    # Mock Explainability
    await render_phase_rationale("CLASSIFY", "Dispute classified as Fraud (10.4) based on reason code in input.")
    await render_blackbox_trace({"input": tool_input, "output": tool_output})
    
    return tool_output

@cl.step(type="process")
async def gather_evidence_step(classification_result: Dict[str, Any]) -> Dict[str, Any]:
    """
    Simulates the GATHER_EVIDENCE phase (Hierarchical).
    """
    await asyncio.sleep(1.5)
    
    # Mock parallel tool calls
    await visualize_tool_call("transaction_specialist", {"lookback_days": 90}, {"found_txns": 3})
    await visualize_tool_call("shipping_specialist", {"carrier": "fedex"}, {"pod_found": True})
    
    evidence_package = {
        "transactions": [{"id": "txn_1", "amount": 50.0}],
        "shipping": {"tracking": "12345"},
        "completeness": 0.9
    }
    
    await render_phase_rationale("GATHER_EVIDENCE", "Gathered 3 prior transactions and shipping POD.")
    await render_agent_facts({"model": "gpt-4o", "capabilities": ["transaction_analysis", "shipping_api"]})
    
    return evidence_package

@cl.step(type="process")
async def validate_evidence_step(evidence_package: Dict[str, Any]) -> Dict[str, Any]:
    """
    Simulates the VALIDATE phase (Judges).
    """
    await asyncio.sleep(1)
    
    judge_result = {
        "evidence_quality": 0.88,
        "fabrication_score": 0.99, # Pass > 0.95
        "passed": True
    }
    
    await visualize_tool_call("validate_evidence", {"evidence": evidence_package}, judge_result)
    await render_guardrails_status({"passed": True, "issues": None})
    
    return judge_result

@cl.step(type="process")
async def submit_dispute_step(validated_package: Dict[str, Any]) -> Dict[str, Any]:
    """
    Simulates the SUBMIT phase.
    """
    await asyncio.sleep(1)
    
    submission_result = {
        "case_id": "VIS-2025-9999",
        "status": "submitted"
    }
    
    await visualize_tool_call("submit_dispute", {"package_id": "pkg_123"}, submission_result)
    await render_phase_rationale("SUBMIT", f"Submitted to Visa VROL. Case ID: {submission_result['case_id']}")
    
    return submission_result

@cl.step(type="process")
async def monitor_dispute_step(case_id: str) -> Dict[str, Any]:
    """
    Simulates the MONITOR phase.
    """
    monitor_result = {"status": "pending_decision"}
    await visualize_tool_call("monitor_dispute", {"case_id": case_id}, monitor_result)
    return monitor_result

