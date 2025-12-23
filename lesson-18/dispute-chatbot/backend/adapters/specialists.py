"""Mock adapters for Specialist Agents.

This module provides mock implementations of the specialist agents that retrieval
evidence from external systems.

Classes:
    TransactionSpecialist: Mocks the transaction history service.
    CustomerSpecialist: Mocks the customer profile and signals service.
    ShippingSpecialist: Mocks the shipping and delivery tracking service.
"""

import asyncio
import random
from typing import List, Optional
from datetime import datetime, timedelta

from backend.phases.evidence_models import (
    SpecialistType,
    TransactionEvidence,
    TransactionInfo,
    CustomerEvidence,
    CustomerSignal,
    ShippingEvidence,
    SpecialistResult
)
from backend.adapters.data_loader import DataLoader


class BaseSpecialist:
    """Base class for mock specialists."""
    
    def __init__(self, failure_rate: float = 0.0, latency_ms: int = 100):
        self.failure_rate = failure_rate
        self.latency_ms = latency_ms

    async def _simulate_latency(self):
        """Simulate network latency."""
        if self.latency_ms > 0:
            await asyncio.sleep(self.latency_ms / 1000.0)

    def _should_fail(self) -> bool:
        """Check if the call should simulate a failure."""
        if self.failure_rate > 0:
            return random.random() < self.failure_rate
        return False


class TransactionSpecialist(BaseSpecialist):
    """Mocks the Transaction History Service."""

    def __init__(self, failure_rate: float = 0.0, latency_ms: int = 100):
        super().__init__(failure_rate, latency_ms)

    async def get_history(self, account_id: str, days: int = 30, dispute_id: Optional[str] = None) -> TransactionEvidence:
        """Fetch transaction history for an account.
        
        Args:
            account_id: The account identifier.
            days: Number of days of history to fetch.
            dispute_id: Optional dispute ID to lookup synthetic data.
            
        Returns:
            TransactionEvidence object.
        """
        await self._simulate_latency()

        # Synthetic Data Lookup
        if dispute_id:
            loader = DataLoader()
            data = loader.get_transaction_evidence(dispute_id)
            if data:
                tx_list = []
                for t in data.get("ce3_transactions", []):
                    tx_list.append(TransactionInfo(
                        transaction_id=t.get("transaction_id", "unknown"),
                        date=t.get("date", datetime.now().isoformat()),
                        amount=float(t.get("amount", 0.0)),
                        currency=t.get("currency", "USD"),
                        description=t.get("description", "Unknown")
                    ))
                
                return TransactionEvidence(
                    success=True,
                    timestamp=datetime.now().isoformat(),
                    transactions=tx_list,
                    total_found=len(tx_list)
                )

        if self._should_fail() or account_id == "ACC_ERROR":
            return TransactionEvidence(
                success=False,
                error="Service unavailable",
                timestamp=datetime.now().isoformat()
            )

        # Mock Data Generation
        # For simplicity, we generate a fixed set of transactions based on the account_id
        # "ACC_FRAUD" -> Returns patterns indicative of fraud (high velocity)
        # "ACC_CLEAN" -> Returns normal patterns
        # Default -> Random mix
        
        transactions: List[TransactionInfo] = []
        now = datetime.now()
        
        if account_id == "ACC_EMPTY":
            pass # No transactions
            
        elif account_id == "ACC_FRAUD":
             # Generate many small transactions recently
             for i in range(5):
                 transactions.append(TransactionInfo(
                     transaction_id=f"tx_fraud_{i}",
                     date=(now - timedelta(days=i)).isoformat(),
                     amount=10.0 + i,
                     currency="USD",
                     description=f"Digital Service {i}"
                 ))
                 
        else: # Normal behavior
             transactions.append(TransactionInfo(
                 transaction_id="tx_norm_1",
                 date=(now - timedelta(days=5)).isoformat(),
                 amount=50.0,
                 currency="USD",
                 description="Grocery Store"
             ))
             transactions.append(TransactionInfo(
                 transaction_id="tx_norm_2",
                 date=(now - timedelta(days=15)).isoformat(),
                 amount=120.50,
                 currency="USD",
                 description="Electronics Shop"
             ))

        return TransactionEvidence(
            success=True,
            timestamp=datetime.now().isoformat(),
            transactions=transactions,
            total_found=len(transactions)
        )


class CustomerSpecialist(BaseSpecialist):
    """Mocks the Customer Data Service."""
    
    def __init__(self, failure_rate: float = 0.0, latency_ms: int = 100):
        super().__init__(failure_rate, latency_ms)

    async def get_signals(self, customer_id: str, dispute_id: Optional[str] = None) -> CustomerEvidence:
        """Fetch customer signals (IP, Device, etc)."""
        await self._simulate_latency()
        
        # Synthetic Data Lookup
        if dispute_id:
            loader = DataLoader()
            data = loader.get_customer_evidence(dispute_id)
            if data:
                signal = CustomerSignal(
                    ip_address=data.get("ip_address"),
                    device_id=data.get("device_id"),
                    email=data.get("email"),
                    phone=data.get("phone"),
                    # Note: shipping_address might be in shipping records, not always in profile
                )
                return CustomerEvidence(
                    success=True,
                    timestamp=datetime.now().isoformat(),
                    signal=signal
                )

        if self._should_fail() or customer_id == "CUST_ERROR":
            return CustomerEvidence(
                success=False,
                error="Customer service timeout",
                timestamp=datetime.now().isoformat()
            )
            
        # Mock Logic
        signal = CustomerSignal()
        
        if customer_id == "CUST_MATCH":
            # Matches typically expected values for CE 3.0
            signal = CustomerSignal(
                ip_address="192.168.1.1",
                device_id="dev_12345",
                email="user@example.com",
                phone="555-0100",
                shipping_address="123 Main St"
            )
        elif customer_id == "CUST_MISMATCH":
             # Missing or different data
             signal = CustomerSignal(
                ip_address="10.0.0.1",
                device_id="dev_99999", # Different device
                email="anon@example.com" 
             )
        elif customer_id == "CUST_WEAK":
             # Very few signals
             signal = CustomerSignal(
                email="anon@example.com"
             )
        else:
            # Default/Partial
             signal = CustomerSignal(
                email="user@example.com",
                phone="555-0100"
             )

        return CustomerEvidence(
            success=True,
            timestamp=datetime.now().isoformat(),
            signal=signal
        )


class ShippingSpecialist(BaseSpecialist):
    """Mocks the Shipping/Logistics Service."""
    
    def __init__(self, failure_rate: float = 0.0, latency_ms: int = 100):
        super().__init__(failure_rate, latency_ms)

    async def get_tracking(self, tracking_number: str, dispute_id: Optional[str] = None) -> ShippingEvidence:
        """Fetch shipping details and POD."""
        await self._simulate_latency()

        # Synthetic Data Lookup
        loader = DataLoader()
        data = None
        if dispute_id:
            data = loader.get_shipping_evidence(dispute_id)
        
        # Fallback to tracking number lookup if no dispute_id or not found
        if not data and tracking_number and tracking_number not in ["TRK_ERROR", "TRK_DELIVERED", "TRK_TRANSIT"]:
             data = loader.get_shipping_by_tracking(tracking_number)

        if data and data.get("shipping"):
            s = data["shipping"]
            # Extract POD from documents if available
            pod_url = next((d.get("url") for d in data.get("documents", []) if d.get("type") == "proof_of_delivery"), None)
            
            return ShippingEvidence(
                success=True,
                timestamp=datetime.now().isoformat(),
                tracking_number=s.get("tracking_number"),
                carrier=s.get("carrier"),
                status=s.get("status", "UNKNOWN").upper(),
                delivered_date=s.get("delivery_date"), # Note: key is delivery_date in JSON, delivered_date in model
                pod_signature_url=pod_url,
                delivery_address=s.get("shipping_address")
            )

        if self._should_fail() or tracking_number == "TRK_ERROR":
            return ShippingEvidence(
                success=False,
                error="Carrier API unavailable",
                timestamp=datetime.now().isoformat()
            )

        # Mock Logic
        ev = ShippingEvidence(
            success=True,
            timestamp=datetime.now().isoformat(),
            tracking_number=tracking_number
        )

        if tracking_number == "TRK_DELIVERED":
            ev.status = "DELIVERED"
            ev.carrier = "FedEx"
            ev.delivered_date = (datetime.now() - timedelta(days=2)).isoformat()
            ev.pod_signature_url = "https://mock.carrier.com/sig/123.jpg"
            ev.delivery_address = "123 Main St"
            
        elif tracking_number == "TRK_TRANSIT":
            ev.status = "IN_TRANSIT"
            ev.carrier = "UPS"
            
        else:
            ev.status = "UNKNOWN"

        return ev
