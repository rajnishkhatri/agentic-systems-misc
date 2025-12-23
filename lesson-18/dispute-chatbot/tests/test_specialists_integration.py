import pytest
import asyncio
from backend.phases.gather_evidence import gather_evidence
from backend.phases.evidence_models import EvidencePackage, SpecialistType
from backend.adapters.data_loader import DataLoader

@pytest.mark.asyncio
async def test_gather_evidence_synthetic_ce3():
    """Test gathering evidence for a synthetic CE 3.0 dispute (DIS-1756e678)."""
    
    # This dispute has transaction history and customer signals
    task = {
        "reason_code": "10.4", # CE 3.0
        "dispute_id": "DIS-1756e678",
        "account_id": "ACC_IGNORED", # Should use dispute_id lookup
        "customer_id": "CUST_IGNORED"
    }
    
    package = await gather_evidence(task)
    
    assert isinstance(package, EvidencePackage)
    assert package.dispute_id == "DIS-1756e678"
    assert package.plan.strategy == "CE_3_0_QUALIFICATION"
    
    # Check Transaction Evidence
    assert package.transaction_evidence is not None
    assert package.transaction_evidence.success is True
    # In synthetic data, this dispute has 3 transactions
    # Based on snippet read earlier: TXN-e4c0469ee649, TXN-4bc4e3f77fe6, TXN-49375a8aa78d
    assert len(package.transaction_evidence.transactions) == 3
    assert package.transaction_evidence.transactions[0].transaction_id == "TXN-e4c0469ee649"
    
    # Check Customer Evidence
    assert package.customer_evidence is not None
    assert package.customer_evidence.success is True
    assert package.customer_evidence.signal is not None
    # From customer_profiles.json snippet for DIS-1756e678
    assert package.customer_evidence.signal.email == "nashkristine@example.com"
    assert package.customer_evidence.signal.ip_address == "44.165.152.173"

    # Check CE 3.0 Result
    # Should be qualified if logic holds (has history and matching signals?)
    # The validate_ce3_eligibility logic checks for >= 2 tx and >= 2 matching signals
    # Since we are not passing the "disputed transaction" to match against in this phase yet, 
    # the validation logic in gather_evidence.py (lines 96-107) checks if signal fields are PRESENT.
    # It counts "matched_signals" based on non-null fields in signal object (simplified logic in code).
    # DIS-1756e678 has email, phone, ip, device. So matched_signals count should be high.
    if package.ce3_result:
        assert package.ce3_result.qualified is True
        assert package.ce3_result.prior_transaction_count >= 2

@pytest.mark.asyncio
async def test_gather_evidence_synthetic_shipping():
    """Test gathering evidence for a synthetic Shipping dispute (DIS-5be6963a)."""
    
    # This dispute has shipping info
    task = {
        "reason_code": "13.1", # Merchandise Not Received
        "dispute_id": "DIS-5be6963a",
        "tracking_number": "TRK_IGNORED"
    }
    
    package = await gather_evidence(task)
    
    assert package.dispute_id == "DIS-5be6963a"
    assert package.plan.strategy == "PNR_13_1_PROOF"
    
    # Check Shipping Evidence
    assert package.shipping_evidence is not None
    assert package.shipping_evidence.success is True
    # From shipping_records.json snippet for DIS-5be6963a
    assert package.shipping_evidence.tracking_number == "1Z890891345768990323"
    assert package.shipping_evidence.carrier == "UPS"
    assert package.shipping_evidence.status == "DELIVERED"
    
    # Check POD
    # Snippet showed a POD document
    assert package.shipping_evidence.pod_signature_url == "http://mock-s3/pod.pdf"

