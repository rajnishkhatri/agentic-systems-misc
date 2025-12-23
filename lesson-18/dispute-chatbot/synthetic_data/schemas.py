from typing import List, Literal, Optional
from decimal import Decimal
from datetime import datetime
from pydantic import BaseModel, Field

# --- Sub-models ---

class SyntheticMerchant(BaseModel):
    id: str
    name: str
    mcc: str
    descriptor: str

class SyntheticCardholder(BaseModel):
    id: str
    name: str  # Faker generated
    email: str
    phone: Optional[str] = None
    billing_address: Optional[str] = None

class Transaction(BaseModel):
    """Represents a prior transaction for CE 3.0 matching"""
    transaction_id: str
    date: datetime
    amount: Decimal
    currency: str = "USD"
    description: str
    ip_address: Optional[str] = None
    device_id: Optional[str] = None
    avs_response: Optional[str] = None
    cvv_response: Optional[str] = None

class ShippingRecord(BaseModel):
    tracking_number: str
    carrier: str
    shipped_date: datetime
    delivery_date: Optional[datetime] = None
    signed_by: Optional[str] = None
    shipping_address: str
    status: Literal["delivered", "in_transit", "exception", "unknown"]

class CustomerSignals(BaseModel):
    ip_address: str
    device_id: str
    account_age_days: int
    prior_purchases_count: int
    email_verified: bool
    phone_verified: bool


class CustomerProfile(BaseModel):
    """Full customer profile for CE 3.0 matching and fraud analysis.

    Task 6.7: Generate customer profiles (device fingerprint, IP, email match)
    """
    customer_id: str = Field(..., description="Format: CUST-{uuid}")
    dispute_id: str = Field(..., description="Associated dispute ID")

    # Identity signals
    email: str
    email_domain: str
    email_verified: bool
    phone: Optional[str] = None
    phone_verified: bool = False

    # Device fingerprint signals
    device_id: str
    device_type: Literal["mobile", "desktop", "tablet"]
    browser: str
    os: str
    screen_resolution: str

    # Network signals
    ip_address: str
    ip_country: str
    ip_city: str
    is_vpn: bool = False
    is_proxy: bool = False

    # Account history signals
    account_created_date: datetime
    account_age_days: int
    prior_purchases_count: int
    prior_disputes_count: int = 0
    lifetime_value: Decimal = Field(default=Decimal("0.00"))

    # CE 3.0 matching signals (from prior transactions)
    matching_ip_count: int = Field(default=0, ge=0, description="Prior txns with same IP")
    matching_device_count: int = Field(default=0, ge=0, description="Prior txns with same device")
    matching_email_count: int = Field(default=0, ge=0, description="Prior txns with same email")
    matching_address_count: int = Field(default=0, ge=0, description="Prior txns with same billing address")

    # Risk indicators
    risk_score: float = Field(default=0.0, ge=0.0, le=1.0, description="0=low risk, 1=high risk")
    is_first_time_customer: bool = False
    has_chargeback_history: bool = False

class Document(BaseModel):
    id: str
    type: Literal["receipt", "proof_of_delivery", "terms_and_conditions", "communication", "other"]
    filename: str
    url: str # Mock URL
    content_summary: str

# --- Main Models ---

class SyntheticDispute(BaseModel):
    dispute_id: str = Field(..., description="Format: DIS-{uuid}")
    network: Literal["visa"] = "visa"
    reason_code: Literal["10.4", "13.1"]
    amount: Decimal = Field(..., ge=10, le=10000)
    currency: str = "USD"
    merchant: SyntheticMerchant
    cardholder: SyntheticCardholder
    transaction_date: datetime
    dispute_date: datetime
    deadline: datetime
    expected_outcome: Literal["win", "lose", "escalate"]
    evidence_completeness: float = Field(..., ge=0.0, le=1.0)

class SyntheticEvidence(BaseModel):
    dispute_id: str
    ce3_transactions: List[Transaction] = Field(default_factory=list)
    shipping: Optional[ShippingRecord] = None
    customer_signals: CustomerSignals
    documents: List[Document] = Field(default_factory=list)
    expected_quality_score: float = Field(..., ge=0.0, le=1.0)

class ConversationTurn(BaseModel):
    role: Literal["user", "assistant", "tool"]
    content: str
    tool_name: Optional[str] = None
    tool_input: Optional[str] = None
    tool_output: Optional[str] = None

class ConversationTrace(BaseModel):
    trace_id: str
    dispute_id: str
    turns: List[ConversationTurn]
    final_state: str
    success: bool
    failure_reason: Optional[str] = None

