import json
import os
import random
import uuid
from datetime import datetime, timedelta
from decimal import Decimal
from typing import List, Optional

from pydantic import BaseModel
from faker import Faker
from schemas import (
    SyntheticDispute, SyntheticEvidence, SyntheticMerchant, SyntheticCardholder,
    Transaction, ShippingRecord, CustomerSignals, CustomerProfile, Document,
    ConversationTrace, ConversationTurn
)

fake = Faker()

# Configuration - use absolute path relative to this file's location
_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(_SCRIPT_DIR, "phase1")
DISPUTES_DIR = os.path.join(OUTPUT_DIR, "disputes")
EVIDENCE_DIR = os.path.join(OUTPUT_DIR, "evidence")
CONVERSATIONS_DIR = os.path.join(OUTPUT_DIR, "conversations")
GOLDEN_SET_DIR = os.path.join(OUTPUT_DIR, "golden_set")

class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super(DecimalEncoder, self).default(obj)

def save_json(data: List[BaseModel], filename: str):
    # Convert Pydantic models to dicts
    json_data = [item.model_dump() for item in data]
    with open(filename, 'w') as f:
        json.dump(json_data, f, cls=DecimalEncoder, indent=2)
    print(f"Saved {len(data)} records to {filename}")

# --- Generators ---

def generate_merchant() -> SyntheticMerchant:
    return SyntheticMerchant(
        id=f"MER-{uuid.uuid4().hex[:8]}",
        name=fake.company(),
        mcc=fake.random_element(elements=["5311", "5732", "5942", "7311"]),
        descriptor=fake.company_suffix().upper() + " STORE"
    )

def generate_cardholder() -> SyntheticCardholder:
    return SyntheticCardholder(
        id=f"CUST-{uuid.uuid4().hex[:8]}",
        name=fake.name(),
        email=fake.email(),
        phone=fake.phone_number(),
        billing_address=fake.address()
    )

def generate_transaction(date: datetime, amount: Decimal) -> Transaction:
    return Transaction(
        transaction_id=f"TXN-{uuid.uuid4().hex[:12]}",
        date=date,
        amount=amount,
        description="Purchase",
        ip_address=fake.ipv4(),
        device_id=f"DEV-{uuid.uuid4().hex[:8]}",
        avs_response="Y",
        cvv_response="M"
    )

def generate_customer_signals(ip: str) -> CustomerSignals:
    return CustomerSignals(
        ip_address=ip,
        device_id=f"DEV-{uuid.uuid4().hex[:8]}",
        account_age_days=random.randint(30, 1000),
        prior_purchases_count=random.randint(0, 50),
        email_verified=True,
        phone_verified=random.choice([True, False])
    )

def generate_shipping(date: datetime, address: str) -> ShippingRecord:
    status = random.choices(["delivered", "in_transit", "exception"], weights=[0.8, 0.1, 0.1])[0]
    return ShippingRecord(
        tracking_number=fake.bothify(text="1Z##################"),
        carrier=random.choice(["UPS", "FedEx", "USPS"]),
        shipped_date=date + timedelta(days=1),
        delivery_date=date + timedelta(days=random.randint(2, 5)) if status == "delivered" else None,
        signed_by=fake.name() if status == "delivered" else None,
        shipping_address=address,
        status=status
    )


def generate_customer_profile(
    dispute_id: str,
    cardholder: SyntheticCardholder,
    customer_signals: CustomerSignals,
    ce3_transactions: List[Transaction],
    expected_outcome: str
) -> CustomerProfile:
    """Generate a full customer profile with CE 3.0 matching signals.

    Task 6.7: Generate customer profiles (device fingerprint, IP, email match)

    Args:
        dispute_id: Associated dispute ID
        cardholder: Cardholder info from dispute
        customer_signals: Basic signals already generated
        ce3_transactions: Prior transactions for CE 3.0 matching
        expected_outcome: win/lose/escalate to influence risk profile

    Returns:
        CustomerProfile with device fingerprint, IP, and email match data
    """
    email = cardholder.email
    email_domain = email.split("@")[1] if "@" in email else "unknown.com"

    # Device fingerprint generation
    device_types = ["mobile", "desktop", "tablet"]
    browsers = ["Chrome", "Safari", "Firefox", "Edge", "Samsung Internet"]
    operating_systems = ["Windows 10", "Windows 11", "macOS", "iOS", "Android", "Linux"]
    resolutions = ["1920x1080", "1366x768", "2560x1440", "1440x900", "375x812", "414x896"]

    # Account history
    account_age = customer_signals.account_age_days
    account_created = datetime.now() - timedelta(days=account_age)
    prior_purchases = customer_signals.prior_purchases_count

    # CE 3.0 matching - count how many prior transactions match on each signal
    ip_match = sum(1 for t in ce3_transactions if t.ip_address == customer_signals.ip_address)
    device_match = sum(1 for t in ce3_transactions if t.device_id == customer_signals.device_id)
    # Email matches would be all prior transactions (same customer)
    email_match = len(ce3_transactions)
    # Address match - simplified, assume all match billing address
    address_match = len(ce3_transactions)

    # Risk scoring based on expected outcome
    if expected_outcome == "win":
        # Low risk - legitimate customer with good history
        risk_score = random.uniform(0.0, 0.3)
        is_first_time = False
        has_chargeback = False
        prior_disputes = 0
    elif expected_outcome == "lose":
        # Higher risk - suspicious patterns
        risk_score = random.uniform(0.5, 0.9)
        is_first_time = random.choice([True, False])
        has_chargeback = random.choice([True, False])
        prior_disputes = random.randint(0, 3)
    else:  # escalate
        # Medium risk - unclear signals
        risk_score = random.uniform(0.3, 0.6)
        is_first_time = random.choice([True, False])
        has_chargeback = False
        prior_disputes = random.randint(0, 1)

    # VPN/Proxy detection - more common in fraud cases
    is_vpn = random.random() < 0.3 if expected_outcome == "lose" else random.random() < 0.05
    is_proxy = random.random() < 0.2 if expected_outcome == "lose" else random.random() < 0.02

    return CustomerProfile(
        customer_id=cardholder.id,
        dispute_id=dispute_id,
        email=email,
        email_domain=email_domain,
        email_verified=customer_signals.email_verified,
        phone=cardholder.phone,
        phone_verified=customer_signals.phone_verified,
        device_id=customer_signals.device_id,
        device_type=random.choice(device_types),
        browser=random.choice(browsers),
        os=random.choice(operating_systems),
        screen_resolution=random.choice(resolutions),
        ip_address=customer_signals.ip_address,
        ip_country=fake.country_code(),
        ip_city=fake.city(),
        is_vpn=is_vpn,
        is_proxy=is_proxy,
        account_created_date=account_created,
        account_age_days=account_age,
        prior_purchases_count=prior_purchases,
        prior_disputes_count=prior_disputes,
        lifetime_value=Decimal(random.uniform(100, 10000)).quantize(Decimal("0.01")),
        matching_ip_count=ip_match,
        matching_device_count=device_match,
        matching_email_count=email_match,
        matching_address_count=address_match,
        risk_score=round(risk_score, 2),
        is_first_time_customer=is_first_time,
        has_chargeback_history=has_chargeback
    )

def generate_dispute(
    reason_code: str,
    outcome: str = "win",
    is_edge_case: bool = False
) -> tuple[SyntheticDispute, SyntheticEvidence, CustomerProfile]:

    merchant = generate_merchant()
    cardholder = generate_cardholder()

    dispute_date = datetime.now() - timedelta(days=random.randint(1, 30))
    transaction_date = dispute_date - timedelta(days=random.randint(1, 60))
    deadline = dispute_date + timedelta(days=14)
    amount = Decimal(random.uniform(10, 5000)).quantize(Decimal("0.01"))

    dispute_id = f"DIS-{uuid.uuid4().hex[:8]}"

    # Evidence generation logic
    ce3_txns = []
    shipping = None
    documents = []

    completeness = 1.0
    quality_score = 0.9 if outcome == "win" else 0.4

    if reason_code == "10.4": # Fraud
        # If win, need prior transactions (CE 3.0)
        if outcome == "win" and not is_edge_case:
            for _ in range(random.randint(2, 5)):
                ce3_txns.append(generate_transaction(
                    date=transaction_date - timedelta(days=random.randint(10, 365)),
                    amount=Decimal(random.uniform(5, 200)).quantize(Decimal("0.01"))
                ))
        elif outcome == "lose":
            ce3_txns = [] # No prior history

    elif reason_code == "13.1": # PNR
        # If win, need shipping proof
        if outcome == "win":
            shipping = generate_shipping(transaction_date, cardholder.billing_address)
            documents.append(Document(
                id=f"DOC-{uuid.uuid4().hex[:6]}",
                type="proof_of_delivery",
                filename="pod.pdf",
                url="http://mock-s3/pod.pdf",
                content_summary="Proof of delivery signed by customer"
            ))
        elif outcome == "lose":
            shipping = None # No shipping proof
            completeness = 0.4

    if is_edge_case:
        # Generate edge cases like missing critical evidence but claiming win
        if random.random() < 0.5:
            completeness = 0.6
            quality_score = 0.5
            outcome = "lose" # Force lose on bad evidence

    # Generate customer signals first
    customer_signals = generate_customer_signals(fake.ipv4())

    dispute = SyntheticDispute(
        dispute_id=dispute_id,
        network="visa",
        reason_code=reason_code,
        amount=amount,
        merchant=merchant,
        cardholder=cardholder,
        transaction_date=transaction_date,
        dispute_date=dispute_date,
        deadline=deadline,
        expected_outcome=outcome,
        evidence_completeness=completeness
    )

    evidence = SyntheticEvidence(
        dispute_id=dispute_id,
        ce3_transactions=ce3_txns,
        shipping=shipping,
        customer_signals=customer_signals,
        documents=documents,
        expected_quality_score=quality_score
    )

    # Generate full customer profile (Task 6.7)
    customer_profile = generate_customer_profile(
        dispute_id=dispute_id,
        cardholder=cardholder,
        customer_signals=customer_signals,
        ce3_transactions=ce3_txns,
        expected_outcome=outcome
    )

    return dispute, evidence, customer_profile

# --- Main Generation Functions ---

def generate_disputes_and_evidence():
    disputes_10_4 = []
    evidence_10_4 = []
    profiles_10_4 = []

    disputes_13_1 = []
    evidence_13_1 = []
    profiles_13_1 = []

    edge_cases = []
    edge_evidence = []
    edge_profiles = []

    # 200 Fraud 10.4 (Mix of win/lose)
    for _ in range(200):
        outcome = random.choices(["win", "lose"], weights=[0.7, 0.3])[0]
        d, e, p = generate_dispute("10.4", outcome)
        disputes_10_4.append(d)
        evidence_10_4.append(e)
        profiles_10_4.append(p)

    # 200 PNR 13.1
    for _ in range(200):
        outcome = random.choices(["win", "lose"], weights=[0.7, 0.3])[0]
        d, e, p = generate_dispute("13.1", outcome)
        disputes_13_1.append(d)
        evidence_13_1.append(e)
        profiles_13_1.append(p)

    # 100 Edge Cases
    for _ in range(100):
        reason = random.choice(["10.4", "13.1"])
        d, e, p = generate_dispute(reason, is_edge_case=True)
        edge_cases.append(d)
        edge_evidence.append(e)
        edge_profiles.append(p)

    # Save disputes
    save_json(disputes_10_4, os.path.join(DISPUTES_DIR, "fraud_10.4_cases.json"))
    save_json(disputes_13_1, os.path.join(DISPUTES_DIR, "pnr_13.1_cases.json"))
    save_json(edge_cases, os.path.join(DISPUTES_DIR, "edge_cases.json"))

    # Save evidence
    save_json(evidence_10_4, os.path.join(EVIDENCE_DIR, "transaction_histories.json"))
    save_json(evidence_13_1, os.path.join(EVIDENCE_DIR, "shipping_records.json"))
    save_json(edge_evidence, os.path.join(EVIDENCE_DIR, "incomplete_evidence.json"))

    # Save customer profiles (Task 6.7)
    all_profiles = profiles_10_4 + profiles_13_1
    save_json(all_profiles, os.path.join(EVIDENCE_DIR, "customer_profiles.json"))

    return (
        disputes_10_4 + disputes_13_1 + edge_cases,
        evidence_10_4 + evidence_13_1 + edge_evidence,
        all_profiles + edge_profiles
    )

def generate_conversations():
    # Placeholder for conversation generation - simplified for now
    happy_paths = []
    for _ in range(50):
        trace_id = f"TRC-{uuid.uuid4().hex[:8]}"
        dispute_id = f"DIS-{uuid.uuid4().hex[:8]}"
        happy_paths.append(ConversationTrace(
            trace_id=trace_id,
            dispute_id=dispute_id,
            turns=[
                ConversationTurn(role="user", content=f"I have a dispute {dispute_id}"),
                ConversationTurn(role="assistant", content="I found it. It's a fraud dispute."),
                ConversationTurn(role="user", content="Here is the evidence."),
                ConversationTurn(role="assistant", content="Evidence gathered. Submitting."),
                ConversationTurn(role="assistant", content="Submitted successfully.")
            ],
            final_state="SUBMITTED",
            success=True
        ))
    
    save_json(happy_paths, os.path.join(CONVERSATIONS_DIR, "happy_path_dialogues.json"))

    # Error Recovery Dialogues
    error_dialogues = []
    for _ in range(30):
        trace_id = f"TRC-{uuid.uuid4().hex[:8]}"
        dispute_id = f"DIS-{uuid.uuid4().hex[:8]}"
        error_dialogues.append(ConversationTrace(
            trace_id=trace_id,
            dispute_id=dispute_id,
            turns=[
                ConversationTurn(role="user", content=f"Dispute {dispute_id}"),
                ConversationTurn(role="assistant", content="Checking status..."),
                ConversationTurn(role="tool", content="Tool call failed", tool_name="check_status", tool_output="TimeoutError"),
                ConversationTurn(role="assistant", content="System is slow. Retrying..."),
                ConversationTurn(role="tool", content="Tool call succeeded", tool_name="check_status", tool_output="Status: OPEN"),
                ConversationTurn(role="assistant", content="Found it. Status is OPEN.")
            ],
            final_state="RECOVERED",
            success=True
        ))
    save_json(error_dialogues, os.path.join(CONVERSATIONS_DIR, "error_recovery_dialogues.json"))

    # Escalation Dialogues
    escalation_dialogues = []
    for _ in range(20):
        trace_id = f"TRC-{uuid.uuid4().hex[:8]}"
        dispute_id = f"DIS-{uuid.uuid4().hex[:8]}"
        escalation_dialogues.append(ConversationTrace(
            trace_id=trace_id,
            dispute_id=dispute_id,
            turns=[
                ConversationTurn(role="user", content=f"Dispute {dispute_id}"),
                ConversationTurn(role="assistant", content="I see this is a complex case. The evidence is contradictory."),
                ConversationTurn(role="user", content="I need a human to look at this."),
                ConversationTurn(role="assistant", content="Escalating to human agent. Ticket #ESC-123 created.")
            ],
            final_state="ESCALATED",
            success=False,
            failure_reason="Human Requested"
        ))
    save_json(escalation_dialogues, os.path.join(CONVERSATIONS_DIR, "escalation_dialogues.json"))

def generate_golden_sets(all_disputes, all_evidence):
    # Classification Labels
    labels = []
    for d in all_disputes[:100]: # First 100 as golden set
        labels.append({
            "dispute_id": d.dispute_id,
            "description": f"Customer claims {d.reason_code} for amount {d.amount}",
            "true_reason_code": d.reason_code,
            "network": d.network
        })
    with open(os.path.join(GOLDEN_SET_DIR, "classification_labels.json"), 'w') as f:
        json.dump(labels, f, indent=2, cls=DecimalEncoder)

    # Evidence Quality Scores
    scores = []
    for e in all_evidence[:100]:
        scores.append({
            "dispute_id": e.dispute_id,
            "expected_score": e.expected_quality_score,
            "completeness": 1.0 if e.expected_quality_score > 0.8 else 0.5 # Simplified logic
        })
    with open(os.path.join(GOLDEN_SET_DIR, "evidence_quality_scores.json"), 'w') as f:
        json.dump(scores, f, indent=2, cls=DecimalEncoder)

    # Fabrication Examples (Static for now as hard to generate programmatically)
    fab_examples = [
        {
            "input_evidence": {},
            "agent_output": "The customer signed for the package on Dec 5th.",
            "is_fabricated": True,
            "reason": "No shipping record in evidence"
        },
        {
            "input_evidence": {"shipping": {"status": "delivered"}},
            "agent_output": "The package was delivered.",
            "is_fabricated": False,
            "reason": "Supported by evidence"
        }
    ]
    with open(os.path.join(GOLDEN_SET_DIR, "fabrication_examples.json"), 'w') as f:
        json.dump(fab_examples, f, indent=2)

def ensure_directories():
    """Create output directories if they don't exist."""
    os.makedirs(DISPUTES_DIR, exist_ok=True)
    os.makedirs(EVIDENCE_DIR, exist_ok=True)
    os.makedirs(CONVERSATIONS_DIR, exist_ok=True)
    os.makedirs(GOLDEN_SET_DIR, exist_ok=True)


if __name__ == "__main__":
    print("Generating synthetic data...")
    ensure_directories()
    all_disputes, all_evidence, all_profiles = generate_disputes_and_evidence()
    generate_conversations()
    generate_golden_sets(all_disputes, all_evidence)
    print(f"Generated {len(all_profiles)} customer profiles")
    print("Done.")

