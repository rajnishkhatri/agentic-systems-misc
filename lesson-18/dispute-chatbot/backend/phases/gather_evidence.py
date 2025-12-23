"""GATHER_EVIDENCE Phase Handler (FR3).

Delegates evidence collection to hierarchical specialist agents and aggregates results.
"""

import asyncio
from typing import Any, Dict, List
from datetime import datetime

from backend.phases.evidence_models import (
    EvidencePlan,
    EvidenceType,
    SpecialistType,
    EvidencePackage,
    TransactionEvidence,
    CustomerEvidence,
    ShippingEvidence,
    CE3QualificationResult,
    SpecialistResult
)
from backend.adapters.specialists import (
    TransactionSpecialist,
    CustomerSpecialist,
    ShippingSpecialist
)


class EvidencePlanner:
    """Determines the evidence gathering strategy based on the reason code."""
    
    @staticmethod
    def create_plan(reason_code: str) -> EvidencePlan:
        """Create an evidence plan based on the reason code.
        
        Args:
            reason_code: The dispute reason code (e.g. "10.4", "13.1").
            
        Returns:
            EvidencePlan object.
        """
        # Fraud - Card Absent Environment
        if reason_code == "10.4":
            return EvidencePlan(
                strategy="CE_3_0_QUALIFICATION",
                required_evidence=[
                    EvidenceType.TRANSACTION_HISTORY,
                    EvidenceType.DEVICE_LOGS
                ],
                specialists=[
                    SpecialistType.TRANSACTION,
                    SpecialistType.CUSTOMER
                ]
            )
            
        # Merchandise Not Received
        elif reason_code == "13.1":
            return EvidencePlan(
                strategy="PNR_13_1_PROOF",
                required_evidence=[
                    EvidenceType.SHIPPING_DETAILS,
                    EvidenceType.PROOF_OF_DELIVERY
                ],
                specialists=[
                    SpecialistType.SHIPPING
                ]
            )
            
        # Default / Fallback
        else:
            return EvidencePlan(
                strategy="BASIC_GATHERING",
                required_evidence=[EvidenceType.TRANSACTION_HISTORY],
                specialists=[SpecialistType.TRANSACTION]
            )


def validate_ce3_eligibility(
    tx_evidence: TransactionEvidence, 
    cust_evidence: CustomerEvidence
) -> CE3QualificationResult:
    """Check eligibility for Compelling Evidence 3.0 (Visa CE 3.0).
    
    Logic (Simplified):
    1. Must have at least 2 undisputed transactions > 120 days old (Mocked as just count > 1 for now).
    2. Must match at least 2 data elements (IP, Device, ID, etc).
    """
    
    # 1. Check Transaction History
    # In a real system, we'd check dates and dispute status.
    # Here, we just check if we found enough history.
    prior_tx_count = tx_evidence.total_found
    
    # 2. Check Data Signals
    # We count how many fields in the signal are present (non-None).
    # In a real system, we'd match these against the disputed transaction's data.
    matched_signals: List[str] = []
    if cust_evidence.signal:
        if cust_evidence.signal.ip_address:
            matched_signals.append("IP_ADDRESS")
        if cust_evidence.signal.device_id:
            matched_signals.append("DEVICE_ID")
        if cust_evidence.signal.email:
            matched_signals.append("EMAIL")
        if cust_evidence.signal.phone:
            matched_signals.append("PHONE")
        if cust_evidence.signal.shipping_address:
            matched_signals.append("SHIPPING_ADDRESS")
            
    matching_count = len(matched_signals)
    
    # Qualification Logic
    qualified = (prior_tx_count >= 2) and (matching_count >= 2)
    
    reason = "Qualified for CE 3.0" if qualified else "Not Qualified"
    if not qualified:
        reasons = []
        if prior_tx_count < 2:
            reasons.append(f"Insufficient history ({prior_tx_count} < 2)")
        if matching_count < 2:
            reasons.append(f"Insufficient matching signals ({matching_count} < 2)")
        reason = "; ".join(reasons)

    return CE3QualificationResult(
        qualified=qualified,
        reason=reason,
        prior_transaction_count=prior_tx_count,
        matching_signal_count=matching_count,
        matched_signals=matched_signals
    )


async def gather_evidence(task: dict[str, Any]) -> EvidencePackage:
    """Execute the GATHER_EVIDENCE phase.

    Args:
        task: Task dictionary containing 'reason_code' and optional 'dispute_id'.

    Returns:
        EvidencePackage with all gathered data.

    Raises:
        TypeError: If task is not a dictionary.
        ValueError: If 'reason_code' is missing.
    """
    # Step 1: Type checking
    if not isinstance(task, dict):
        raise TypeError("task must be a dictionary")

    # Step 2: Input validation
    reason_code = task.get("reason_code")
    if not reason_code:
        raise ValueError("task must contain 'reason_code'")
        
    dispute_id = task.get("dispute_id", "UNKNOWN_DISPUTE")
    
    # Extract identifiers for mocking purposes (in real app, these come from context)
    account_id = task.get("account_id", "ACC_NORMAL")
    customer_id = task.get("customer_id", "CUST_MATCH")
    tracking_number = task.get("tracking_number", "TRK_DELIVERED")

    # Step 3: Create Plan
    plan = EvidencePlanner.create_plan(reason_code)
    
    # Step 4: Execute Plan (Parallel)
    # Instantiate specialists
    tx_specialist = TransactionSpecialist()
    cust_specialist = CustomerSpecialist()
    ship_specialist = ShippingSpecialist()
    
    # Prepare tasks
    async_tasks = []
    task_map = {} # Map future to specialist type
    
    if SpecialistType.TRANSACTION in plan.specialists:
        t = asyncio.create_task(tx_specialist.get_history(account_id, dispute_id=dispute_id))
        async_tasks.append(t)
        task_map[t] = SpecialistType.TRANSACTION
        
    if SpecialistType.CUSTOMER in plan.specialists:
        t = asyncio.create_task(cust_specialist.get_signals(customer_id, dispute_id=dispute_id))
        async_tasks.append(t)
        task_map[t] = SpecialistType.CUSTOMER
        
    if SpecialistType.SHIPPING in plan.specialists:
        t = asyncio.create_task(ship_specialist.get_tracking(tracking_number, dispute_id=dispute_id))
        async_tasks.append(t)
        task_map[t] = SpecialistType.SHIPPING
        
    # Wait for all
    results = await asyncio.gather(*async_tasks, return_exceptions=True)
    
    # Step 5: Process Results
    tx_evidence: TransactionEvidence = None
    cust_evidence: CustomerEvidence = None
    ship_evidence: ShippingEvidence = None
    
    for i, result in enumerate(results):
        original_task = async_tasks[i]
        spec_type = task_map[original_task]
        
        if isinstance(result, Exception):
            # Handle crash
            print(f"Error executing specialist {spec_type}: {result}")
            continue
            
        if spec_type == SpecialistType.TRANSACTION:
            tx_evidence = result
        elif spec_type == SpecialistType.CUSTOMER:
            cust_evidence = result
        elif spec_type == SpecialistType.SHIPPING:
            ship_evidence = result

    # Step 6: Post-Processing Logic (e.g. CE 3.0 Check)
    ce3_result = None
    if plan.strategy == "CE_3_0_QUALIFICATION":
        # We need both TX and CUST evidence to validate
        if tx_evidence and cust_evidence and tx_evidence.success and cust_evidence.success:
            ce3_result = validate_ce3_eligibility(tx_evidence, cust_evidence)
    
    # Step 7: Calculate Completeness
    # Simple score: gathered / planned
    planned_count = len(plan.specialists)
    gathered_count = 0
    if tx_evidence: gathered_count += 1
    if cust_evidence: gathered_count += 1
    if ship_evidence: gathered_count += 1
    
    completeness = gathered_count / planned_count if planned_count > 0 else 0.0

    # Step 8: Build Package
    package = EvidencePackage(
        dispute_id=dispute_id,
        reason_code=reason_code,
        plan=plan,
        transaction_evidence=tx_evidence,
        customer_evidence=cust_evidence,
        shipping_evidence=ship_evidence,
        ce3_result=ce3_result,
        completeness_score=completeness,
        gathered_at=datetime.now().isoformat()
    )
    
    return package
