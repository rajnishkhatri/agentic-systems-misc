"""Integration tests for the Gather Evidence Phase (Phase 2)."""

import pytest
import asyncio
from typing import Dict, Any

from backend.phases.gather_evidence import gather_evidence
from backend.phases.evidence_models import EvidencePackage, CE3QualificationResult

@pytest.mark.asyncio
async def test_ce3_qualification_success():
    """Test CE 3.0 Qualification with a qualified candidate."""
    task = {
        "reason_code": "10.4",
        "dispute_id": "D-TEST-SUCCESS",
        "account_id": "ACC_NORMAL",
        "customer_id": "CUST_MATCH"
    }
    
    result = await gather_evidence(task)
    
    assert isinstance(result, EvidencePackage)
    assert result.reason_code == "10.4"
    assert result.plan.strategy == "CE_3_0_QUALIFICATION"
    
    # Check Evidence Presence
    assert result.transaction_evidence is not None
    assert result.customer_evidence is not None
    assert result.shipping_evidence is None # Not requested
    
    # Check CE 3.0 Specifics
    assert result.ce3_result is not None
    assert result.ce3_result.qualified is True
    assert "Qualified" in result.ce3_result.reason
    assert result.ce3_result.prior_transaction_count >= 2
    assert result.ce3_result.matching_signal_count >= 2


@pytest.mark.asyncio
async def test_ce3_qualification_failure_history():
    """Test CE 3.0 Qualification failure due to insufficient history."""
    task = {
        "reason_code": "10.4",
        "dispute_id": "D-TEST-FAIL-HIST",
        "account_id": "ACC_EMPTY", # No history
        "customer_id": "CUST_MATCH"
    }
    
    result = await gather_evidence(task)
    
    assert result.ce3_result is not None
    assert result.ce3_result.qualified is False
    assert "Insufficient history" in result.ce3_result.reason
    assert result.ce3_result.prior_transaction_count == 0


@pytest.mark.asyncio
async def test_ce3_qualification_failure_signal():
    """Test CE 3.0 Qualification failure due to weak signal (insufficient matches)."""
    task = {
        "reason_code": "10.4",
        "dispute_id": "D-TEST-FAIL-SIG",
        "account_id": "ACC_NORMAL",
        "customer_id": "CUST_WEAK" # Only email
    }
    
    result = await gather_evidence(task)
    
    assert result.ce3_result is not None
    assert result.ce3_result.qualified is False
    assert "Insufficient matching signals" in result.ce3_result.reason
    assert result.ce3_result.matching_signal_count < 2


@pytest.mark.asyncio
async def test_pnr_13_1_shipping_delivered():
    """Test Merchandise Not Received logic."""
    task = {
        "reason_code": "13.1",
        "dispute_id": "D-TEST-PNR",
        "tracking_number": "TRK_DELIVERED"
    }
    
    result = await gather_evidence(task)
    
    assert result.plan.strategy == "PNR_13_1_PROOF"
    assert result.shipping_evidence is not None
    assert result.shipping_evidence.status == "DELIVERED"
    assert result.shipping_evidence.pod_signature_url is not None


@pytest.mark.asyncio
async def test_missing_reason_code():
    """Test error handling for missing input."""
    task = {"dispute_id": "bad_task"}
    
    with pytest.raises(ValueError, match="reason_code"):
        await gather_evidence(task)

