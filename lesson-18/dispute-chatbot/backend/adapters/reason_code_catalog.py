"""Reason Code Catalog Adapter.

Provides access to the standardized reason codes catalog.
"""
import csv
import logging
from pathlib import Path
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

class ReasonCodeCatalog:
    """Adapter for the reason codes catalog CSV."""

    def __init__(self, catalog_path: Optional[Path] = None):
        """Initialize the catalog adapter.
        
        Args:
            catalog_path: Path to the CSV catalog file. If None, attempts to locate it
                         relative to this file.
        """
        if catalog_path:
            self.catalog_path = catalog_path
        else:
            # Default location: ../../../dispute-schema/reason_codes_catalog.csv
            # based on: backend/adapters/reason_code_catalog.py
            base_dir = Path(__file__).parent.parent.parent.parent
            self.catalog_path = base_dir / "dispute-schema" / "reason_codes_catalog.csv"

        self._codes: Dict[str, List[Dict[str, str]]] = {}
        self._loaded = False

    def _load_catalog(self) -> None:
        """Load the catalog from CSV if not already loaded."""
        if self._loaded:
            return

        if not self.catalog_path.exists():
            logger.error(f"Reason code catalog not found at {self.catalog_path}")
            return

        try:
            with open(self.catalog_path, mode="r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    # Handle case-insensitive header matching or known variations
                    if "namespace" in row:
                        network = row["namespace"].lower()
                    elif "Network" in row:
                        network = row["Network"].lower()
                    elif "network" in row:
                        network = row["network"].lower()
                    else:
                        # Fallback or skip
                        continue
                        
                    if network not in self._codes:
                        self._codes[network] = []
                    
                    self._codes[network].append({
                        "code": row["reason_code"],
                        "description": row["description"],
                        "category": row["unified_category"]
                    })
            
            self._loaded = True
            logger.info(f"Loaded reason code catalog from {self.catalog_path}")
            
        except Exception as e:
            logger.error(f"Failed to load reason code catalog: {e}")
            raise

    def get_codes_for_network(self, network: str) -> List[Dict[str, str]]:
        """Get all reason codes for a specific network.

        Args:
            network: Network name (e.g., 'visa', 'mastercard')

        Returns:
            List of dictionaries containing code details.
        """
        self._load_catalog()
        return self._codes.get(network.lower(), [])

    def get_category_for_code(self, network: str, code: str) -> Optional[str]:
        """Get the unified category for a specific code.

        Args:
            network: Network name
            code: Reason code

        Returns:
            Unified category string or None if not found.
        """
        codes = self.get_codes_for_network(network)
        for entry in codes:
            if entry["code"] == code:
                return entry["category"]
        return None

    def get_codes_for_network_and_category(self, network: str, category: str) -> List[Dict[str, str]]:
        """Get reason codes for a specific network and unified category.

        Args:
            network: Network name (e.g., 'visa')
            category: Unified category (e.g., 'product_not_received')

        Returns:
            List of matching code dictionaries.
        """
        codes = self.get_codes_for_network(network)
        return [c for c in codes if c["category"] == category]

# Global instance for convenience
_catalog_instance = None

def get_reason_code_catalog() -> ReasonCodeCatalog:
    """Get or create the global catalog instance."""
    global _catalog_instance
    if _catalog_instance is None:
        _catalog_instance = ReasonCodeCatalog()
    return _catalog_instance

