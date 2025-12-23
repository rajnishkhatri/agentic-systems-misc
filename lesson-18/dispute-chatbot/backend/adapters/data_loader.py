import json
import os
from typing import Dict, Any, Optional, List

class DataLoader:
    """Singleton data loader for synthetic evidence files."""

    _instance = None
    _data_loaded = False
    
    _transactions: Dict[str, Any] = {}
    _shipping: Dict[str, Any] = {}
    _customers: Dict[str, Any] = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DataLoader, cls).__new__(cls)
        return cls._instance

    def ensure_loaded(self):
        """Load data if not already loaded."""
        if self._data_loaded:
            return

        base_path = "lesson-18/dispute-chatbot/synthetic_data/phase1/evidence"
        
        # Load Transaction History
        try:
            with open(os.path.join(base_path, "transaction_histories.json"), 'r') as f:
                data = json.load(f)
                self._transactions = {item['dispute_id']: item for item in data}
        except FileNotFoundError:
            print(f"Warning: Transaction history file not found at {base_path}")

        # Load Shipping Records
        try:
            with open(os.path.join(base_path, "shipping_records.json"), 'r') as f:
                data = json.load(f)
                self._shipping = {item['dispute_id']: item for item in data}
        except FileNotFoundError:
            print(f"Warning: Shipping records file not found at {base_path}")

        # Load Customer Profiles
        try:
            with open(os.path.join(base_path, "customer_profiles.json"), 'r') as f:
                data = json.load(f)
                self._customers = {item['dispute_id']: item for item in data}
        except FileNotFoundError:
            print(f"Warning: Customer profiles file not found at {base_path}")

        self._data_loaded = True

    def get_transaction_evidence(self, dispute_id: str) -> Optional[Dict[str, Any]]:
        """Get transaction evidence for a dispute ID."""
        self.ensure_loaded()
        return self._transactions.get(dispute_id)

    def get_shipping_evidence(self, dispute_id: str) -> Optional[Dict[str, Any]]:
        """Get shipping evidence for a dispute ID."""
        self.ensure_loaded()
        return self._shipping.get(dispute_id)

    def get_customer_evidence(self, dispute_id: str) -> Optional[Dict[str, Any]]:
        """Get customer evidence for a dispute ID."""
        self.ensure_loaded()
        return self._customers.get(dispute_id)

    def get_shipping_by_tracking(self, tracking_number: str) -> Optional[Dict[str, Any]]:
        """Lookup shipping evidence by tracking number (slow scan)."""
        self.ensure_loaded()
        # This is inefficient but acceptable for prototype scale
        for item in self._shipping.values():
            if item.get('shipping') and item['shipping'].get('tracking_number') == tracking_number:
                return item
        return None

