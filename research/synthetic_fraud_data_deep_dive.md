# Synthetic Data Generation for Fraud Detection Testing
## A Deep Dive Based on Stripe Radar Architecture

---

## Executive Summary

This research document provides a comprehensive framework for generating synthetic data to test fraud detection systems modeled after Stripe Radar's 1,000+ transaction characteristics. Stripe Radar processes over $1.4 trillion annually with sub-100ms latency and a 0.1% false positive rate, making it an ideal blueprint for synthetic data generation strategies.

The document covers eight core signal categories: Card Characteristics, Device Fingerprinting, Behavioral Signals, Network Intelligence, Transaction Characteristics, Velocity Metrics, Identity Verification, and Network-Wide Signals. For each category, we provide realistic data distributions, generation algorithms, fraud pattern simulation techniques, and Python implementation code.

**Key Objectives:**
- Enable comprehensive testing of ML/LLM-based fraud detection models
- Simulate realistic fraud scenarios based on production patterns
- Create statistically representative datasets that mirror real-world distributions
- Support A/B testing between traditional ML and foundation model approaches

---

## Table of Contents

1. [Card Characteristics](#1-card-characteristics)
2. [Device Fingerprinting](#2-device-fingerprinting)
3. [Behavioral Signals](#3-behavioral-signals)
4. [Network Intelligence](#4-network-intelligence)
5. [Transaction Characteristics](#5-transaction-characteristics)
6. [Velocity and Frequency Metrics](#6-velocity-and-frequency-metrics)
7. [Identity Verification Signals](#7-identity-verification-signals)
8. [Network-Wide Signals](#8-network-wide-signals)
9. [Integrated Synthetic Dataset Generator](#9-integrated-synthetic-dataset-generator)
10. [Testing Scenarios and Validation](#10-testing-scenarios-and-validation)

---

## 1. Card Characteristics

### 1.1 Overview

Card characteristics form the foundational layer of fraud detection, with the BIN (Bank Identification Number) alone providing signals about issuer risk, geographic patterns, and card product types. Stripe evaluates card attributes as primary features in their multi-branch DNN architecture.

### 1.2 Data Elements and Realistic Distributions

#### BIN (Bank Identification Number) Patterns

The first 6-8 digits of a card number identify the issuing institution and card type.

```python
import random
import numpy as np
from dataclasses import dataclass
from typing import Optional, List, Dict
from datetime import datetime, timedelta
from enum import Enum

class CardBrand(Enum):
    VISA = "visa"
    MASTERCARD = "mastercard"
    AMEX = "amex"
    DISCOVER = "discover"
    JCB = "jcb"
    UNIONPAY = "unionpay"
    DINERS = "diners"

class CardType(Enum):
    CREDIT = "credit"
    DEBIT = "debit"
    PREPAID = "prepaid"

class RiskLevel(Enum):
    LOW = "low"
    MEDIUM = "medium"
    ELEVATED = "elevated"
    HIGH = "high"
    HIGHEST = "highest"

@dataclass
class BINProfile:
    """BIN (Bank Identification Number) profile with associated risk signals"""
    bin_prefix: str
    brand: CardBrand
    card_type: CardType
    issuing_country: str
    issuing_bank: str
    risk_score: float  # 0-100
    prepaid_reloadable: bool = False
    virtual_card: bool = False
    
# Realistic BIN database with risk profiles
BIN_DATABASE = {
    # US Visa - Major Banks (Low Risk)
    "424242": BINProfile("424242", CardBrand.VISA, CardType.CREDIT, "US", "Test Bank USA", 15.0),
    "400000": BINProfile("400000", CardBrand.VISA, CardType.CREDIT, "US", "Chase Bank", 12.0),
    "411111": BINProfile("411111", CardBrand.VISA, CardType.CREDIT, "US", "Bank of America", 10.0),
    "400056": BINProfile("400056", CardBrand.VISA, CardType.DEBIT, "US", "Wells Fargo", 8.0),
    
    # US Mastercard (Low Risk)
    "555555": BINProfile("555555", CardBrand.MASTERCARD, CardType.CREDIT, "US", "Citibank", 12.0),
    "222300": BINProfile("222300", CardBrand.MASTERCARD, CardType.CREDIT, "US", "Capital One", 14.0),
    "520082": BINProfile("520082", CardBrand.MASTERCARD, CardType.DEBIT, "US", "PNC Bank", 9.0),
    
    # Prepaid Cards (Higher Risk)
    "510510": BINProfile("510510", CardBrand.MASTERCARD, CardType.PREPAID, "US", "Green Dot", 55.0, True, False),
    "414720": BINProfile("414720", CardBrand.VISA, CardType.PREPAID, "US", "NetSpend", 60.0, True, False),
    
    # Virtual Cards (Elevated Risk)
    "428485": BINProfile("428485", CardBrand.VISA, CardType.CREDIT, "US", "Privacy.com", 45.0, False, True),
    
    # International - High Risk Regions
    "400000": BINProfile("400032", CardBrand.VISA, CardType.CREDIT, "RU", "Sberbank", 75.0),
    "400001": BINProfile("400001", CardBrand.VISA, CardType.CREDIT, "NG", "GTBank", 70.0),
    "400011": BINProfile("400011", CardBrand.VISA, CardType.CREDIT, "BY", "Belarusbank", 72.0),
    
    # International - Medium Risk
    "400076": BINProfile("400076", CardBrand.VISA, CardType.CREDIT, "BR", "Itau", 35.0),
    "400004": BINProfile("400004", CardBrand.VISA, CardType.CREDIT, "MX", "BBVA Mexico", 30.0),
    "400048": BINProfile("400048", CardBrand.VISA, CardType.CREDIT, "IN", "HDFC Bank", 28.0),
    
    # International - Low Risk (EU/UK/AU)
    "400082": BINProfile("400082", CardBrand.VISA, CardType.CREDIT, "GB", "Barclays", 12.0),
    "400002": BINProfile("400002", CardBrand.VISA, CardType.CREDIT, "DE", "Deutsche Bank", 10.0),
    "400003": BINProfile("400003", CardBrand.VISA, CardType.CREDIT, "AU", "Commonwealth", 11.0),
    "400025": BINProfile("400025", CardBrand.VISA, CardType.CREDIT, "FR", "BNP Paribas", 10.0),
    
    # Amex
    "378282": BINProfile("378282", CardBrand.AMEX, CardType.CREDIT, "US", "American Express", 15.0),
    "371449": BINProfile("371449", CardBrand.AMEX, CardType.CREDIT, "US", "American Express", 15.0),
    
    # Discover
    "601111": BINProfile("601111", CardBrand.DISCOVER, CardType.CREDIT, "US", "Discover", 18.0),
    "601198": BINProfile("601198", CardBrand.DISCOVER, CardType.DEBIT, "US", "Discover", 16.0),
}

# Brand distribution based on market share
BRAND_DISTRIBUTION = {
    CardBrand.VISA: 0.52,
    CardBrand.MASTERCARD: 0.30,
    CardBrand.AMEX: 0.10,
    CardBrand.DISCOVER: 0.05,
    CardBrand.JCB: 0.02,
    CardBrand.UNIONPAY: 0.01,
}

# Card type distribution
CARD_TYPE_DISTRIBUTION = {
    CardType.CREDIT: 0.55,
    CardType.DEBIT: 0.40,
    CardType.PREPAID: 0.05,
}

# Fraud scenario distributions
FRAUD_CARD_TYPE_DISTRIBUTION = {
    CardType.CREDIT: 0.35,
    CardType.DEBIT: 0.25,
    CardType.PREPAID: 0.40,  # Prepaid over-represented in fraud
}
```

#### Card Number Generation with Luhn Validation

```python
def luhn_checksum(card_number: str) -> int:
    """Calculate Luhn checksum for card validation"""
    def digits_of(n):
        return [int(d) for d in str(n)]
    
    digits = digits_of(card_number)
    odd_digits = digits[-1::-2]
    even_digits = digits[-2::-2]
    
    checksum = sum(odd_digits)
    for d in even_digits:
        checksum += sum(digits_of(d * 2))
    return checksum % 10

def generate_valid_card_number(bin_prefix: str, length: int = 16) -> str:
    """Generate a valid card number with Luhn checksum"""
    # Generate random digits for middle portion
    remaining_length = length - len(bin_prefix) - 1
    middle_digits = ''.join([str(random.randint(0, 9)) for _ in range(remaining_length)])
    
    # Calculate check digit
    partial_number = bin_prefix + middle_digits
    check_digit = (10 - luhn_checksum(partial_number + '0')) % 10
    
    return partial_number + str(check_digit)

@dataclass
class SyntheticCard:
    """Complete synthetic card with all characteristics"""
    card_number: str
    bin_profile: BINProfile
    expiry_month: int
    expiry_year: int
    cvv: str
    cardholder_name: str
    days_until_expiry: int
    is_expired: bool
    expiry_proximity_risk: float  # Higher for cards expiring soon
    
    @property
    def card_last_four(self) -> str:
        return self.card_number[-4:]
    
    @property
    def masked_number(self) -> str:
        return f"{'*' * 12}{self.card_last_four}"

class CardCharacteristicsGenerator:
    """Generator for synthetic card characteristics"""
    
    def __init__(self, fraud_mode: bool = False):
        self.fraud_mode = fraud_mode
        self.bin_database = BIN_DATABASE
        
    def _select_bin(self) -> BINProfile:
        """Select a BIN based on distribution and fraud mode"""
        bins = list(self.bin_database.values())
        
        if self.fraud_mode:
            # Bias toward higher risk BINs
            weights = [max(0.1, bin.risk_score / 100) for bin in bins]
        else:
            # Normal distribution with bias toward low risk
            weights = [max(0.1, 1 - (bin.risk_score / 100)) for bin in bins]
        
        total_weight = sum(weights)
        weights = [w / total_weight for w in weights]
        
        return random.choices(bins, weights=weights)[0]
    
    def _generate_expiry(self) -> tuple:
        """Generate expiry date with realistic distribution"""
        now = datetime.now()
        
        if self.fraud_mode:
            # Fraudulent cards often use soon-to-expire or recently issued cards
            if random.random() < 0.3:
                # 30% chance of card expiring within 3 months
                months_ahead = random.randint(1, 3)
            else:
                months_ahead = random.randint(4, 36)
        else:
            # Normal distribution: most cards have 2-4 years validity
            months_ahead = random.randint(6, 48)
        
        expiry_date = now + timedelta(days=months_ahead * 30)
        return expiry_date.month, expiry_date.year
    
    def _generate_cardholder_name(self, is_fraud: bool = False) -> str:
        """Generate realistic cardholder names"""
        first_names = ["John", "Jane", "Michael", "Sarah", "David", "Emily", 
                       "Robert", "Lisa", "William", "Jennifer", "James", "Maria"]
        last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia",
                     "Miller", "Davis", "Rodriguez", "Martinez", "Hernandez", "Lopez"]
        
        if is_fraud and random.random() < 0.2:
            # Fraudsters sometimes use obviously fake names
            return random.choice(["Test User", "Card Holder", "John Doe", "Jane Doe"])
        
        return f"{random.choice(first_names)} {random.choice(last_names)}"
    
    def generate_card(self) -> SyntheticCard:
        """Generate a complete synthetic card"""
        bin_profile = self._select_bin()
        card_number = generate_valid_card_number(
            bin_profile.bin_prefix,
            length=15 if bin_profile.brand == CardBrand.AMEX else 16
        )
        
        expiry_month, expiry_year = self._generate_expiry()
        
        # Calculate days until expiry
        now = datetime.now()
        expiry_date = datetime(expiry_year, expiry_month, 28)
        days_until_expiry = (expiry_date - now).days
        is_expired = days_until_expiry < 0
        
        # Calculate expiry proximity risk
        if days_until_expiry < 0:
            expiry_proximity_risk = 80.0  # Expired
        elif days_until_expiry < 30:
            expiry_proximity_risk = 60.0
        elif days_until_expiry < 90:
            expiry_proximity_risk = 40.0
        elif days_until_expiry < 180:
            expiry_proximity_risk = 20.0
        else:
            expiry_proximity_risk = 5.0
        
        # Generate CVV
        cvv_length = 4 if bin_profile.brand == CardBrand.AMEX else 3
        cvv = ''.join([str(random.randint(0, 9)) for _ in range(cvv_length)])
        
        return SyntheticCard(
            card_number=card_number,
            bin_profile=bin_profile,
            expiry_month=expiry_month,
            expiry_year=expiry_year,
            cvv=cvv,
            cardholder_name=self._generate_cardholder_name(self.fraud_mode),
            days_until_expiry=days_until_expiry,
            is_expired=is_expired,
            expiry_proximity_risk=expiry_proximity_risk
        )

# Stripe Test Card Mappings for Integration Testing
STRIPE_TEST_CARDS = {
    # Standard Success Cards
    "visa_success": "4242424242424242",
    "visa_debit": "4000056655665556",
    "mastercard_success": "5555555555554444",
    "mastercard_2series": "2223003122003222",
    "mastercard_debit": "5200828282828210",
    "mastercard_prepaid": "5105105105105100",
    "amex_success": "378282246310005",
    "discover_success": "6011111111111117",
    
    # Decline Cards
    "generic_decline": "4000000000000002",
    "insufficient_funds": "4000000000009995",
    "lost_card": "4000000000009987",
    "stolen_card": "4000000000009979",
    "expired_card": "4000000000000069",
    "incorrect_cvc": "4000000000000127",
    "processing_error": "4000000000000119",
    "velocity_exceeded": "4000000000006975",
    
    # Fraud Prevention Cards
    "always_blocked": "4100000000000019",
    "highest_risk": "4000000000004954",
    "elevated_risk": "4000000000009235",
    "cvc_check_fail": "4000000000000101",
    "postal_code_fail": "4000000000000036",
    
    # Dispute Cards
    "fraudulent_dispute": "4000000000000259",
    "product_not_received": "4000000000002685",
    "inquiry": "4000000000001976",
    "early_fraud_warning": "4000000000005423",
    
    # 3D Secure Cards
    "3ds_required": "4000000000003220",
    "3ds_required_declined": "4000008400001629",
    "3ds_supported": "4000000000003055",
    
    # International Cards by Country
    "card_us": "4242424242424242",
    "card_gb": "4000008260000000",
    "card_de": "4000002760000016",
    "card_fr": "4000002500000003",
    "card_au": "4000000360000006",
    "card_jp": "4000003920000003",
    "card_br": "4000000760000002",
    "card_in": "4000003560000008",
}
```

### 1.3 Fraud Pattern Simulation for Cards

```python
class CardFraudPatternGenerator:
    """Generate cards matching known fraud patterns"""
    
    @staticmethod
    def card_testing_attack(num_cards: int = 50) -> List[SyntheticCard]:
        """Simulate card testing attack pattern
        
        Pattern: Fraudsters test many cards with small amounts
        to identify which cards are active.
        """
        generator = CardCharacteristicsGenerator(fraud_mode=True)
        cards = []
        
        # Use prepaid and virtual cards heavily
        for _ in range(num_cards):
            card = generator.generate_card()
            # Card testing often uses cards from same BIN range
            if random.random() < 0.6:
                # Cluster around specific BINs
                card.bin_profile = random.choice([
                    bin_p for bin_p in BIN_DATABASE.values() 
                    if bin_p.card_type == CardType.PREPAID
                ])
            cards.append(card)
        
        return cards
    
    @staticmethod
    def stolen_card_batch(base_bin: str = "424242", num_cards: int = 20) -> List[SyntheticCard]:
        """Simulate a batch of stolen cards from same breach
        
        Pattern: Cards from same bank/region compromised together
        """
        cards = []
        base_profile = BIN_DATABASE.get(base_bin, list(BIN_DATABASE.values())[0])
        
        for _ in range(num_cards):
            card_number = generate_valid_card_number(base_profile.bin_prefix)
            
            # Similar expiry dates (same issuance batch)
            base_month = random.randint(1, 12)
            base_year = datetime.now().year + random.randint(1, 3)
            
            now = datetime.now()
            expiry_date = datetime(base_year, base_month, 28)
            days_until_expiry = (expiry_date - now).days
            
            cards.append(SyntheticCard(
                card_number=card_number,
                bin_profile=base_profile,
                expiry_month=base_month + random.randint(-1, 1),
                expiry_year=base_year,
                cvv=''.join([str(random.randint(0, 9)) for _ in range(3)]),
                cardholder_name=f"Cardholder {random.randint(1000, 9999)}",
                days_until_expiry=days_until_expiry,
                is_expired=days_until_expiry < 0,
                expiry_proximity_risk=20.0
            ))
        
        return cards
    
    @staticmethod
    def cross_border_fraud_cards(num_cards: int = 10) -> List[SyntheticCard]:
        """Generate cards for cross-border fraud simulation
        
        Pattern: High-risk country cards used in low-risk merchant country
        """
        high_risk_countries = ["RU", "NG", "BY", "VN", "PH"]
        high_risk_bins = [
            bin_p for bin_p in BIN_DATABASE.values() 
            if bin_p.issuing_country in high_risk_countries
        ]
        
        if not high_risk_bins:
            # Fallback to high risk score bins
            high_risk_bins = [
                bin_p for bin_p in BIN_DATABASE.values() 
                if bin_p.risk_score > 50
            ]
        
        generator = CardCharacteristicsGenerator(fraud_mode=True)
        cards = []
        
        for _ in range(num_cards):
            card = generator.generate_card()
            if high_risk_bins:
                card.bin_profile = random.choice(high_risk_bins)
            cards.append(card)
        
        return cards
```

---

## 2. Device Fingerprinting

### 2.1 Overview

Device fingerprinting creates unique identifiers by collecting hardware, software, and behavioral attributes from user devices. Stripe's Radar uses these signals to detect device manipulation, emulators, and suspicious device patterns.

### 2.2 Data Elements and Generation

```python
import hashlib
import json
from typing import Dict, Any

@dataclass
class BrowserFingerprint:
    """Browser-level fingerprint attributes"""
    user_agent: str
    browser_name: str
    browser_version: str
    browser_language: str
    browser_languages: List[str]
    cookies_enabled: bool
    do_not_track: bool
    
@dataclass  
class ScreenFingerprint:
    """Screen and display attributes"""
    screen_width: int
    screen_height: int
    available_width: int
    available_height: int
    color_depth: int
    pixel_ratio: float
    
@dataclass
class CanvasFingerprint:
    """Canvas and WebGL fingerprinting data"""
    canvas_hash: str
    webgl_vendor: str
    webgl_renderer: str
    webgl_version: str
    webgl_extensions: List[str]
    
@dataclass
class SystemFingerprint:
    """System-level attributes"""
    platform: str
    os_name: str
    os_version: str
    cpu_class: str
    hardware_concurrency: int
    device_memory: float
    max_touch_points: int
    
@dataclass
class PluginFingerprint:
    """Browser plugins and fonts"""
    plugins: List[str]
    installed_fonts: List[str]
    fonts_hash: str
    
@dataclass
class DeviceFingerprint:
    """Complete device fingerprint"""
    fingerprint_id: str
    browser: BrowserFingerprint
    screen: ScreenFingerprint
    canvas: CanvasFingerprint
    system: SystemFingerprint
    plugins: PluginFingerprint
    timezone: str
    timezone_offset: int
    session_storage: bool
    local_storage: bool
    indexed_db: bool
    add_behavior: bool
    open_database: bool
    is_incognito: bool
    is_bot: bool
    is_emulator: bool
    is_vm: bool
    risk_score: float

class DeviceFingerprintGenerator:
    """Generate realistic device fingerprints"""
    
    # User agent templates by device type
    USER_AGENTS = {
        "chrome_windows": [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 11.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        ],
        "chrome_mac": [
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        ],
        "safari_mac": [
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15",
        ],
        "firefox_windows": [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
        ],
        "chrome_mobile": [
            "Mozilla/5.0 (Linux; Android 14; Pixel 7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36",
            "Mozilla/5.0 (Linux; Android 13; SM-S918B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36",
        ],
        "safari_ios": [
            "Mozilla/5.0 (iPhone; CPU iPhone OS 17_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Mobile/15E148 Safari/604.1",
        ],
        # Bot/Fraud indicators
        "headless_chrome": [
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) HeadlessChrome/120.0.0.0 Safari/537.36",
        ],
        "phantomjs": [
            "Mozilla/5.0 (Unknown; Linux x86_64) AppleWebKit/538.1 (KHTML, like Gecko) PhantomJS/2.1.1 Safari/538.1",
        ],
    }
    
    # Common screen resolutions with market share
    SCREEN_RESOLUTIONS = [
        {"width": 1920, "height": 1080, "weight": 0.25},
        {"width": 1366, "height": 768, "weight": 0.15},
        {"width": 1536, "height": 864, "weight": 0.10},
        {"width": 1440, "height": 900, "weight": 0.08},
        {"width": 2560, "height": 1440, "weight": 0.08},
        {"width": 1680, "height": 1050, "weight": 0.05},
        {"width": 3840, "height": 2160, "weight": 0.05},  # 4K
        {"width": 390, "height": 844, "weight": 0.10},   # iPhone
        {"width": 412, "height": 915, "weight": 0.08},   # Android
        {"width": 414, "height": 896, "weight": 0.06},   # iPhone 11
    ]
    
    # WebGL renderers (GPU identification)
    WEBGL_RENDERERS = {
        "nvidia": [
            "ANGLE (NVIDIA GeForce RTX 4090 Direct3D11 vs_5_0 ps_5_0)",
            "ANGLE (NVIDIA GeForce RTX 3080 Direct3D11 vs_5_0 ps_5_0)",
            "ANGLE (NVIDIA GeForce GTX 1660 Ti Direct3D11 vs_5_0 ps_5_0)",
        ],
        "amd": [
            "ANGLE (AMD Radeon RX 7900 XTX Direct3D11 vs_5_0 ps_5_0)",
            "ANGLE (AMD Radeon RX 6800 XT Direct3D11 vs_5_0 ps_5_0)",
        ],
        "intel": [
            "ANGLE (Intel(R) UHD Graphics 630 Direct3D11 vs_5_0 ps_5_0)",
            "ANGLE (Intel(R) Iris(R) Xe Graphics Direct3D11 vs_5_0 ps_5_0)",
        ],
        "apple": [
            "Apple GPU",
            "Apple M1",
            "Apple M2",
            "Apple M3",
        ],
        "vm_suspicious": [
            "VMware SVGA 3D",
            "VirtualBox Graphics Adapter",
            "llvmpipe (LLVM 12.0.0, 256 bits)",  # Software renderer
        ],
    }
    
    # Common timezone offsets
    TIMEZONES = [
        {"name": "America/New_York", "offset": -300, "weight": 0.15},
        {"name": "America/Chicago", "offset": -360, "weight": 0.10},
        {"name": "America/Los_Angeles", "offset": -480, "weight": 0.12},
        {"name": "Europe/London", "offset": 0, "weight": 0.08},
        {"name": "Europe/Paris", "offset": 60, "weight": 0.05},
        {"name": "Europe/Berlin", "offset": 60, "weight": 0.05},
        {"name": "Asia/Tokyo", "offset": 540, "weight": 0.05},
        {"name": "Asia/Shanghai", "offset": 480, "weight": 0.04},
        {"name": "Asia/Kolkata", "offset": 330, "weight": 0.04},
        {"name": "Australia/Sydney", "offset": 660, "weight": 0.03},
    ]
    
    # Common fonts for fingerprinting
    COMMON_FONTS = [
        "Arial", "Arial Black", "Calibri", "Cambria", "Century Gothic",
        "Comic Sans MS", "Consolas", "Courier New", "Georgia", "Helvetica",
        "Impact", "Lucida Console", "Microsoft Sans Serif", "Palatino Linotype",
        "Segoe UI", "Tahoma", "Times New Roman", "Trebuchet MS", "Verdana",
    ]
    
    def __init__(self, fraud_mode: bool = False):
        self.fraud_mode = fraud_mode
        
    def _generate_browser_fingerprint(self, ua_category: str) -> BrowserFingerprint:
        """Generate browser-specific fingerprint"""
        user_agent = random.choice(self.USER_AGENTS.get(ua_category, self.USER_AGENTS["chrome_windows"]))
        
        # Parse browser info from user agent
        browser_name = "Chrome"
        browser_version = "120.0.0.0"
        if "Firefox" in user_agent:
            browser_name = "Firefox"
            browser_version = "121.0"
        elif "Safari" in user_agent and "Chrome" not in user_agent:
            browser_name = "Safari"
            browser_version = "17.1"
            
        languages = ["en-US", "en"]
        if random.random() < 0.3:
            languages = random.choice([
                ["en-GB", "en"],
                ["de-DE", "de", "en"],
                ["fr-FR", "fr", "en"],
                ["es-ES", "es", "en"],
                ["ja-JP", "ja", "en"],
            ])
            
        return BrowserFingerprint(
            user_agent=user_agent,
            browser_name=browser_name,
            browser_version=browser_version,
            browser_language=languages[0],
            browser_languages=languages,
            cookies_enabled=random.random() > 0.02,  # 98% have cookies enabled
            do_not_track=random.random() < 0.15,
        )
    
    def _generate_screen_fingerprint(self, is_mobile: bool = False) -> ScreenFingerprint:
        """Generate screen/display fingerprint"""
        resolutions = self.SCREEN_RESOLUTIONS.copy()
        
        if is_mobile:
            resolutions = [r for r in resolutions if r["width"] < 600]
        else:
            resolutions = [r for r in resolutions if r["width"] >= 1024]
            
        if not resolutions:
            resolutions = self.SCREEN_RESOLUTIONS
            
        weights = [r["weight"] for r in resolutions]
        total = sum(weights)
        weights = [w/total for w in weights]
        
        resolution = random.choices(resolutions, weights=weights)[0]
        
        return ScreenFingerprint(
            screen_width=resolution["width"],
            screen_height=resolution["height"],
            available_width=resolution["width"],
            available_height=resolution["height"] - random.randint(30, 100),  # Taskbar
            color_depth=random.choice([24, 32]),
            pixel_ratio=random.choice([1.0, 1.25, 1.5, 2.0, 3.0]),
        )
    
    def _generate_canvas_fingerprint(self, is_suspicious: bool = False) -> CanvasFingerprint:
        """Generate canvas/WebGL fingerprint"""
        
        if is_suspicious:
            renderer_category = "vm_suspicious"
        else:
            renderer_category = random.choice(["nvidia", "amd", "intel", "apple"])
            
        renderers = self.WEBGL_RENDERERS.get(renderer_category, self.WEBGL_RENDERERS["intel"])
        renderer = random.choice(renderers)
        
        # Generate deterministic canvas hash
        canvas_data = f"{renderer}_{random.randint(10000, 99999)}"
        canvas_hash = hashlib.md5(canvas_data.encode()).hexdigest()[:16]
        
        return CanvasFingerprint(
            canvas_hash=canvas_hash,
            webgl_vendor="Google Inc." if "ANGLE" in renderer else "Apple Inc.",
            webgl_renderer=renderer,
            webgl_version="WebGL 2.0",
            webgl_extensions=[
                "ANGLE_instanced_arrays",
                "EXT_blend_minmax", 
                "EXT_color_buffer_half_float",
                "OES_texture_float",
                "WEBGL_compressed_texture_s3tc",
            ][:random.randint(3, 5)],
        )
    
    def _generate_system_fingerprint(self, ua_category: str) -> SystemFingerprint:
        """Generate system-level fingerprint"""
        
        if "windows" in ua_category:
            platform = "Win32"
            os_name = "Windows"
            os_version = random.choice(["10", "11"])
        elif "mac" in ua_category:
            platform = "MacIntel"
            os_name = "macOS"
            os_version = random.choice(["10.15.7", "14.1", "13.5"])
        elif "mobile" in ua_category or "ios" in ua_category:
            platform = random.choice(["iPhone", "Linux armv8l"])
            os_name = "iOS" if "iPhone" in platform else "Android"
            os_version = "17.1" if os_name == "iOS" else "14"
        else:
            platform = "Linux x86_64"
            os_name = "Linux"
            os_version = "5.15"
            
        return SystemFingerprint(
            platform=platform,
            os_name=os_name,
            os_version=os_version,
            cpu_class="x64" if "x86_64" in platform or platform == "Win32" else "ARM",
            hardware_concurrency=random.choice([4, 6, 8, 12, 16]),
            device_memory=random.choice([4.0, 8.0, 16.0, 32.0]),
            max_touch_points=10 if "mobile" in ua_category or "ios" in ua_category else 0,
        )
    
    def _generate_plugin_fingerprint(self) -> PluginFingerprint:
        """Generate browser plugins and fonts fingerprint"""
        plugins = []
        if random.random() > 0.3:
            plugins = random.sample([
                "Chrome PDF Plugin",
                "Chrome PDF Viewer", 
                "Chromium PDF Viewer",
            ], k=random.randint(1, 2))
            
        num_fonts = random.randint(10, len(self.COMMON_FONTS))
        fonts = random.sample(self.COMMON_FONTS, k=num_fonts)
        fonts_hash = hashlib.md5(",".join(sorted(fonts)).encode()).hexdigest()[:12]
        
        return PluginFingerprint(
            plugins=plugins,
            installed_fonts=fonts,
            fonts_hash=fonts_hash,
        )
    
    def _calculate_risk_score(self, fingerprint: Dict[str, Any]) -> float:
        """Calculate device risk score based on fingerprint attributes"""
        risk = 0.0
        
        # Headless browser detection
        if "headless" in fingerprint.get("user_agent", "").lower():
            risk += 40
            
        # VM/Emulator detection
        if fingerprint.get("is_vm", False):
            risk += 30
        if fingerprint.get("is_emulator", False):
            risk += 35
            
        # Incognito mode
        if fingerprint.get("is_incognito", False):
            risk += 15
            
        # Missing features (bot indicator)
        if not fingerprint.get("cookies_enabled", True):
            risk += 20
        if not fingerprint.get("local_storage", True):
            risk += 15
            
        # Suspicious screen size
        if fingerprint.get("screen_width", 1920) < 100:
            risk += 25
            
        # Timezone mismatch detection would happen at network layer
        
        return min(100.0, risk)
    
    def generate(self) -> DeviceFingerprint:
        """Generate a complete device fingerprint"""
        
        # Select device type
        if self.fraud_mode and random.random() < 0.3:
            # Fraudsters often use headless browsers or emulators
            ua_category = random.choice(["headless_chrome", "phantomjs"])
            is_suspicious = True
        else:
            ua_category = random.choices(
                ["chrome_windows", "chrome_mac", "chrome_mobile", "safari_mac", "safari_ios", "firefox_windows"],
                weights=[0.35, 0.15, 0.20, 0.10, 0.12, 0.08]
            )[0]
            is_suspicious = self.fraud_mode and random.random() < 0.2
            
        is_mobile = "mobile" in ua_category or "ios" in ua_category
        
        browser = self._generate_browser_fingerprint(ua_category)
        screen = self._generate_screen_fingerprint(is_mobile)
        canvas = self._generate_canvas_fingerprint(is_suspicious)
        system = self._generate_system_fingerprint(ua_category)
        plugins = self._generate_plugin_fingerprint()
        
        # Timezone selection
        timezone_data = random.choices(
            self.TIMEZONES,
            weights=[t["weight"] for t in self.TIMEZONES]
        )[0]
        
        # Detect suspicious attributes
        is_vm = "VMware" in canvas.webgl_renderer or "VirtualBox" in canvas.webgl_renderer
        is_emulator = "llvmpipe" in canvas.webgl_renderer
        is_bot = "headless" in ua_category or "phantomjs" in ua_category
        is_incognito = random.random() < (0.15 if self.fraud_mode else 0.05)
        
        # Generate fingerprint ID
        fp_data = f"{browser.user_agent}_{screen.screen_width}_{canvas.canvas_hash}_{plugins.fonts_hash}"
        fingerprint_id = hashlib.sha256(fp_data.encode()).hexdigest()[:32]
        
        fingerprint = DeviceFingerprint(
            fingerprint_id=fingerprint_id,
            browser=browser,
            screen=screen,
            canvas=canvas,
            system=system,
            plugins=plugins,
            timezone=timezone_data["name"],
            timezone_offset=timezone_data["offset"],
            session_storage=not is_bot,
            local_storage=not is_bot,
            indexed_db=not is_bot,
            add_behavior=False,
            open_database=random.random() > 0.3,
            is_incognito=is_incognito,
            is_bot=is_bot,
            is_emulator=is_emulator,
            is_vm=is_vm,
            risk_score=0.0,  # Will be calculated
        )
        
        # Calculate risk score
        fp_dict = {
            "user_agent": browser.user_agent,
            "is_vm": is_vm,
            "is_emulator": is_emulator,
            "is_incognito": is_incognito,
            "cookies_enabled": browser.cookies_enabled,
            "local_storage": fingerprint.local_storage,
            "screen_width": screen.screen_width,
        }
        fingerprint.risk_score = self._calculate_risk_score(fp_dict)
        
        return fingerprint
```

### 2.3 Fraud Pattern Simulation for Devices

```python
class DeviceFraudPatternGenerator:
    """Generate device fingerprints matching known fraud patterns"""
    
    @staticmethod
    def device_farm_fingerprints(num_devices: int = 20) -> List[DeviceFingerprint]:
        """Simulate device farm with similar characteristics
        
        Pattern: Multiple "different" devices with suspiciously similar attributes
        """
        generator = DeviceFingerprintGenerator(fraud_mode=True)
        devices = []
        
        # Generate base device
        base_device = generator.generate()
        
        for i in range(num_devices):
            device = generator.generate()
            
            # Make devices suspiciously similar (same GPU, similar fonts)
            device.canvas = base_device.canvas
            device.plugins.fonts_hash = base_device.plugins.fonts_hash
            
            # Slightly vary other attributes
            device.screen.screen_width = base_device.screen.screen_width + random.randint(-10, 10)
            device.screen.screen_height = base_device.screen.screen_height + random.randint(-10, 10)
            
            # Recalculate fingerprint ID
            fp_data = f"{device.browser.user_agent}_{device.screen.screen_width}_{device.canvas.canvas_hash}"
            device.fingerprint_id = hashlib.sha256(fp_data.encode()).hexdigest()[:32]
            
            device.risk_score = min(100, device.risk_score + 30)  # Device farm penalty
            devices.append(device)
            
        return devices
    
    @staticmethod
    def emulator_fingerprints(num_devices: int = 10) -> List[DeviceFingerprint]:
        """Generate emulator/VM device fingerprints
        
        Pattern: Automated fraud using Android emulators or browser automation
        """
        devices = []
        
        for _ in range(num_devices):
            generator = DeviceFingerprintGenerator(fraud_mode=True)
            device = generator.generate()
            
            # Override with emulator characteristics
            device.canvas.webgl_renderer = random.choice([
                "llvmpipe (LLVM 12.0.0, 256 bits)",
                "VMware SVGA 3D",
                "VirtualBox Graphics Adapter",
                "Android Emulator OpenGL ES Translator",
            ])
            device.is_emulator = True
            device.is_vm = True
            device.system.hardware_concurrency = 2  # Limited CPU cores
            device.system.device_memory = 2.0  # Limited memory
            device.risk_score = 85.0
            
            devices.append(device)
            
        return devices
    
    @staticmethod
    def antidetect_browser_fingerprints(num_devices: int = 10) -> List[DeviceFingerprint]:
        """Generate anti-detect browser fingerprints
        
        Pattern: Fraudsters use tools like Multilogin, GoLogin to spoof fingerprints
        """
        devices = []
        
        for _ in range(num_devices):
            generator = DeviceFingerprintGenerator(fraud_mode=False)  # Try to look normal
            device = generator.generate()
            
            # Anti-detect browsers often have inconsistent attributes
            # e.g., Mac user agent with Windows plugins
            if random.random() < 0.6:
                device.browser.user_agent = random.choice(
                    DeviceFingerprintGenerator.USER_AGENTS["chrome_mac"]
                )
                device.system.platform = "Win32"  # Mismatch!
                device.risk_score = 55.0
            
            # Unusual timezone for claimed location
            if random.random() < 0.4:
                device.timezone = "Asia/Shanghai"
                device.timezone_offset = 480
                device.risk_score += 20
                
            devices.append(device)
            
        return devices
```

---

## 3. Behavioral Signals

### 3.1 Overview

Behavioral signals capture how users interact with checkout pages, including mouse movements, typing patterns, and navigation behavior. These signals are extremely difficult to spoof and form a critical layer in modern fraud detection.

### 3.2 Data Elements and Generation

```python
from dataclasses import dataclass, field
from typing import List, Tuple
import math

@dataclass
class MouseMovement:
    """Single mouse movement event"""
    x: int
    y: int
    timestamp_ms: int
    velocity: float
    acceleration: float
    
@dataclass
class KeystrokeEvent:
    """Single keystroke timing event"""
    key: str
    key_down_time: int
    key_up_time: int
    dwell_time: int  # How long key was held
    flight_time: int  # Time since last key
    
@dataclass
class MousePattern:
    """Aggregated mouse movement patterns"""
    movements: List[MouseMovement]
    total_distance: float
    average_velocity: float
    max_velocity: float
    num_direction_changes: int
    straightness_ratio: float  # Actual vs straight-line distance
    idle_time_ms: int
    
@dataclass
class TypingPattern:
    """Aggregated typing pattern analysis"""
    keystrokes: List[KeystrokeEvent]
    average_dwell_time: float
    average_flight_time: float
    wpm: float  # Words per minute
    error_rate: float
    copy_paste_detected: bool
    autofill_detected: bool
    
@dataclass
class NavigationPattern:
    """User navigation behavior"""
    page_load_time_ms: int
    time_to_first_input_ms: int
    time_on_checkout_page_ms: int
    scroll_depth_percent: float
    num_form_field_focuses: int
    form_field_order: List[str]  # Order fields were filled
    tab_switches: int
    back_button_pressed: bool
    
@dataclass
class BehavioralFingerprint:
    """Complete behavioral fingerprint"""
    session_id: str
    mouse_pattern: MousePattern
    typing_pattern: TypingPattern
    navigation_pattern: NavigationPattern
    touch_events: List[dict]  # For mobile
    risk_score: float
    is_bot_likely: bool
    is_automated: bool

class BehavioralSignalGenerator:
    """Generate realistic behavioral signals"""
    
    def __init__(self, fraud_mode: bool = False, is_mobile: bool = False):
        self.fraud_mode = fraud_mode
        self.is_mobile = is_mobile
        
    def _generate_human_mouse_movements(self, 
                                         start: Tuple[int, int], 
                                         end: Tuple[int, int],
                                         num_points: int = 20) -> List[MouseMovement]:
        """Generate human-like mouse movements using Bezier curves"""
        movements = []
        
        # Add random control points for natural curve
        ctrl1 = (
            start[0] + random.randint(-50, 50),
            start[1] + random.randint(-30, 30)
        )
        ctrl2 = (
            end[0] + random.randint(-50, 50),
            end[1] + random.randint(-30, 30)
        )
        
        prev_point = start
        prev_time = 0
        prev_velocity = 0
        
        for i in range(num_points):
            t = i / (num_points - 1)
            
            # Cubic Bezier curve
            x = int(
                (1-t)**3 * start[0] +
                3 * (1-t)**2 * t * ctrl1[0] +
                3 * (1-t) * t**2 * ctrl2[0] +
                t**3 * end[0]
            )
            y = int(
                (1-t)**3 * start[1] +
                3 * (1-t)**2 * t * ctrl1[1] +
                3 * (1-t) * t**2 * ctrl2[1] +
                t**3 * end[1]
            )
            
            # Add some noise for human-like jitter
            x += random.randint(-2, 2)
            y += random.randint(-2, 2)
            
            # Calculate timing with variable speed
            base_interval = random.randint(10, 30)  # 10-30ms between points
            
            # Slower at start and end (acceleration/deceleration)
            if t < 0.2 or t > 0.8:
                base_interval = int(base_interval * 1.5)
                
            timestamp = prev_time + base_interval
            
            # Calculate velocity
            distance = math.sqrt((x - prev_point[0])**2 + (y - prev_point[1])**2)
            time_delta = max(1, timestamp - prev_time)
            velocity = distance / time_delta * 1000  # pixels per second
            
            # Calculate acceleration
            acceleration = (velocity - prev_velocity) / time_delta * 1000
            
            movements.append(MouseMovement(
                x=x,
                y=y,
                timestamp_ms=timestamp,
                velocity=velocity,
                acceleration=acceleration
            ))
            
            prev_point = (x, y)
            prev_time = timestamp
            prev_velocity = velocity
            
        return movements
    
    def _generate_bot_mouse_movements(self,
                                       start: Tuple[int, int],
                                       end: Tuple[int, int],
                                       num_points: int = 5) -> List[MouseMovement]:
        """Generate bot-like straight-line mouse movements"""
        movements = []
        
        for i in range(num_points):
            t = i / (num_points - 1)
            
            # Perfect straight line
            x = int(start[0] + t * (end[0] - start[0]))
            y = int(start[1] + t * (end[1] - start[1]))
            
            # Perfectly even timing
            timestamp = i * 20  # Exactly 20ms intervals
            
            # Constant velocity
            velocity = 500.0  # Constant
            acceleration = 0.0  # No acceleration
            
            movements.append(MouseMovement(
                x=x,
                y=y,
                timestamp_ms=timestamp,
                velocity=velocity,
                acceleration=acceleration
            ))
            
        return movements
    
    def _generate_mouse_pattern(self) -> MousePattern:
        """Generate complete mouse movement pattern for checkout flow"""
        all_movements = []
        
        # Simulate mouse movements through checkout
        checkout_elements = [
            (100, 200),   # Email field
            (100, 260),   # Card number field
            (100, 320),   # Expiry field
            (200, 320),   # CVV field
            (100, 380),   # Name field
            (150, 450),   # Submit button
        ]
        
        current_pos = (random.randint(0, 500), random.randint(0, 200))
        
        for target in checkout_elements:
            if self.fraud_mode and random.random() < 0.4:
                movements = self._generate_bot_mouse_movements(current_pos, target)
            else:
                movements = self._generate_human_mouse_movements(current_pos, target)
            
            # Add offset to timestamps
            if all_movements:
                time_offset = all_movements[-1].timestamp_ms + random.randint(100, 500)
                for m in movements:
                    m.timestamp_ms += time_offset
                    
            all_movements.extend(movements)
            current_pos = target
            
        # Calculate aggregate metrics
        total_distance = 0
        velocities = []
        direction_changes = 0
        prev_direction = None
        
        for i in range(1, len(all_movements)):
            curr = all_movements[i]
            prev = all_movements[i-1]
            
            dx = curr.x - prev.x
            dy = curr.y - prev.y
            distance = math.sqrt(dx**2 + dy**2)
            total_distance += distance
            velocities.append(curr.velocity)
            
            # Count direction changes
            if dx != 0 or dy != 0:
                direction = math.atan2(dy, dx)
                if prev_direction is not None:
                    if abs(direction - prev_direction) > 0.5:  # ~30 degree change
                        direction_changes += 1
                prev_direction = direction
                
        # Calculate straightness ratio
        start = (all_movements[0].x, all_movements[0].y)
        end = (all_movements[-1].x, all_movements[-1].y)
        straight_distance = math.sqrt((end[0]-start[0])**2 + (end[1]-start[1])**2)
        straightness_ratio = straight_distance / max(1, total_distance)
        
        # Calculate idle time (gaps > 1 second)
        idle_time = 0
        for i in range(1, len(all_movements)):
            gap = all_movements[i].timestamp_ms - all_movements[i-1].timestamp_ms
            if gap > 1000:
                idle_time += gap - 1000
                
        return MousePattern(
            movements=all_movements,
            total_distance=total_distance,
            average_velocity=np.mean(velocities) if velocities else 0,
            max_velocity=max(velocities) if velocities else 0,
            num_direction_changes=direction_changes,
            straightness_ratio=straightness_ratio,
            idle_time_ms=idle_time,
        )
    
    def _generate_human_typing(self, text: str) -> List[KeystrokeEvent]:
        """Generate human-like typing patterns"""
        keystrokes = []
        
        current_time = 0
        prev_key_up = 0
        
        for i, char in enumerate(text):
            # Variable flight time (time between keys)
            if i == 0:
                flight_time = 0
            else:
                # Faster for common bigrams
                base_flight = random.randint(80, 200)
                # Slower for shifts (uppercase, symbols)
                if char.isupper() or char in "!@#$%^&*()":
                    base_flight = int(base_flight * 1.5)
                flight_time = base_flight + random.randint(-20, 20)
            
            key_down = prev_key_up + flight_time
            
            # Dwell time (how long key is pressed)
            dwell_time = random.randint(50, 150)
            
            key_up = key_down + dwell_time
            
            keystrokes.append(KeystrokeEvent(
                key=char,
                key_down_time=key_down,
                key_up_time=key_up,
                dwell_time=dwell_time,
                flight_time=flight_time,
            ))
            
            prev_key_up = key_up
            
        return keystrokes
    
    def _generate_bot_typing(self, text: str) -> List[KeystrokeEvent]:
        """Generate bot-like typing patterns (too consistent)"""
        keystrokes = []
        
        current_time = 0
        
        for char in text:
            # Perfectly consistent timing
            flight_time = 50  # Exactly 50ms between keys
            dwell_time = 30   # Exactly 30ms key hold
            
            key_down = current_time + flight_time
            key_up = key_down + dwell_time
            
            keystrokes.append(KeystrokeEvent(
                key=char,
                key_down_time=key_down,
                key_up_time=key_up,
                dwell_time=dwell_time,
                flight_time=flight_time,
            ))
            
            current_time = key_up
            
        return keystrokes
    
    def _generate_typing_pattern(self) -> TypingPattern:
        """Generate complete typing pattern for form filling"""
        
        # Simulate typing card number, name, etc.
        card_number = "4242424242424242"
        cardholder_name = "John Smith"
        
        if self.fraud_mode and random.random() < 0.5:
            # Bot typing
            card_keystrokes = self._generate_bot_typing(card_number)
            name_keystrokes = self._generate_bot_typing(cardholder_name)
            copy_paste = random.random() < 0.3  # Bots often paste
        else:
            card_keystrokes = self._generate_human_typing(card_number)
            name_keystrokes = self._generate_human_typing(cardholder_name)
            copy_paste = random.random() < 0.05  # Humans rarely paste
            
        all_keystrokes = card_keystrokes + name_keystrokes
        
        # Calculate metrics
        dwell_times = [k.dwell_time for k in all_keystrokes]
        flight_times = [k.flight_time for k in all_keystrokes if k.flight_time > 0]
        
        total_time_ms = all_keystrokes[-1].key_up_time if all_keystrokes else 1
        num_chars = len(all_keystrokes)
        wpm = (num_chars / 5) / (total_time_ms / 60000) if total_time_ms > 0 else 0
        
        return TypingPattern(
            keystrokes=all_keystrokes,
            average_dwell_time=np.mean(dwell_times) if dwell_times else 0,
            average_flight_time=np.mean(flight_times) if flight_times else 0,
            wpm=wpm,
            error_rate=random.uniform(0, 0.05) if not self.fraud_mode else 0,  # Bots don't make errors
            copy_paste_detected=copy_paste,
            autofill_detected=random.random() < (0.1 if self.fraud_mode else 0.3),
        )
    
    def _generate_navigation_pattern(self) -> NavigationPattern:
        """Generate navigation behavior pattern"""
        
        if self.fraud_mode:
            # Fraudsters often rush through checkout
            time_on_checkout = random.randint(5000, 30000)  # 5-30 seconds
            time_to_first_input = random.randint(100, 1000)  # Very fast
            scroll_depth = random.uniform(0.1, 0.5)  # Don't scroll much
        else:
            # Normal users take time
            time_on_checkout = random.randint(30000, 180000)  # 30s - 3min
            time_to_first_input = random.randint(2000, 10000)  # 2-10 seconds
            scroll_depth = random.uniform(0.7, 1.0)  # Scroll through page
            
        # Form field order
        normal_order = ["email", "card_number", "expiry", "cvv", "name", "postal_code"]
        
        if self.fraud_mode and random.random() < 0.3:
            # Unusual field order (e.g., filling CVV first)
            field_order = random.sample(normal_order, len(normal_order))
        else:
            # Normal order with maybe one swap
            field_order = normal_order.copy()
            if random.random() < 0.2:
                i, j = random.sample(range(len(field_order)), 2)
                field_order[i], field_order[j] = field_order[j], field_order[i]
                
        return NavigationPattern(
            page_load_time_ms=random.randint(500, 3000),
            time_to_first_input_ms=time_to_first_input,
            time_on_checkout_page_ms=time_on_checkout,
            scroll_depth_percent=scroll_depth,
            num_form_field_focuses=random.randint(6, 15),
            form_field_order=field_order,
            tab_switches=random.randint(0, 3) if not self.fraud_mode else random.randint(0, 1),
            back_button_pressed=random.random() < 0.1,
        )
    
    def generate(self) -> BehavioralFingerprint:
        """Generate complete behavioral fingerprint"""
        
        mouse_pattern = self._generate_mouse_pattern()
        typing_pattern = self._generate_typing_pattern()
        navigation_pattern = self._generate_navigation_pattern()
        
        # Calculate risk score
        risk_score = 0.0
        
        # Bot indicators from mouse
        if mouse_pattern.straightness_ratio > 0.95:
            risk_score += 25  # Too straight
        if mouse_pattern.num_direction_changes < 5:
            risk_score += 20  # Too few direction changes
        if mouse_pattern.average_velocity > 1500:
            risk_score += 15  # Superhuman speed
            
        # Bot indicators from typing
        if typing_pattern.error_rate == 0:
            risk_score += 10  # Humans make mistakes
        if typing_pattern.wpm > 150:
            risk_score += 20  # Superhuman typing
        if typing_pattern.copy_paste_detected:
            risk_score += 15
            
        # Variance check (bots are too consistent)
        dwell_variance = np.var([k.dwell_time for k in typing_pattern.keystrokes]) if typing_pattern.keystrokes else 0
        if dwell_variance < 100:
            risk_score += 20  # Too consistent
            
        # Navigation indicators
        if navigation_pattern.time_on_checkout_page_ms < 10000:
            risk_score += 15  # Too fast
        if navigation_pattern.scroll_depth_percent < 0.3:
            risk_score += 10
            
        is_bot_likely = risk_score > 50
        is_automated = risk_score > 70
        
        return BehavioralFingerprint(
            session_id=hashlib.md5(str(random.random()).encode()).hexdigest()[:16],
            mouse_pattern=mouse_pattern,
            typing_pattern=typing_pattern,
            navigation_pattern=navigation_pattern,
            touch_events=[],  # Populated for mobile
            risk_score=min(100, risk_score),
            is_bot_likely=is_bot_likely,
            is_automated=is_automated,
        )
```

---

## 4. Network Intelligence

### 4.1 Overview

Network signals provide crucial context about transaction origin, including IP geolocation, proxy/VPN detection, and reputation data from network-wide patterns.

### 4.2 Data Elements and Generation

```python
import ipaddress

@dataclass
class IPGeolocation:
    """IP geolocation data"""
    ip_address: str
    country_code: str
    country_name: str
    region: str
    city: str
    postal_code: str
    latitude: float
    longitude: float
    timezone: str
    isp: str
    organization: str
    asn: int
    asn_name: str
    
@dataclass
class NetworkReputation:
    """Network reputation signals"""
    is_proxy: bool
    is_vpn: bool
    is_tor: bool
    is_datacenter: bool
    is_residential: bool
    is_mobile: bool
    reputation_score: float  # 0-100, higher is riskier
    abuse_reports: int
    last_abuse_date: Optional[datetime]
    
@dataclass
class NetworkVelocity:
    """Network velocity metrics from Stripe network"""
    transactions_last_hour: int
    transactions_last_day: int
    unique_cards_last_hour: int
    unique_cards_last_day: int
    unique_emails_last_hour: int
    decline_rate_last_day: float
    fraud_rate_historical: float
    
@dataclass
class NetworkIntelligence:
    """Complete network intelligence profile"""
    geolocation: IPGeolocation
    reputation: NetworkReputation
    velocity: NetworkVelocity
    historical_risk_score: float
    is_known_fraud_ip: bool
    card_country_match: bool
    timezone_match: bool

class NetworkIntelligenceGenerator:
    """Generate synthetic network intelligence data"""
    
    # IP ranges by type
    IP_PROFILES = {
        "us_residential": {
            "ranges": ["24.0.0.0/8", "71.0.0.0/8", "98.0.0.0/8", "174.0.0.0/8"],
            "countries": ["US"],
            "is_residential": True,
            "risk_base": 10,
        },
        "us_datacenter": {
            "ranges": ["54.0.0.0/8", "52.0.0.0/8", "35.0.0.0/8"],  # AWS-like
            "countries": ["US"],
            "is_datacenter": True,
            "risk_base": 45,
        },
        "eu_residential": {
            "ranges": ["82.0.0.0/8", "87.0.0.0/8", "92.0.0.0/8"],
            "countries": ["GB", "DE", "FR", "NL"],
            "is_residential": True,
            "risk_base": 12,
        },
        "high_risk_country": {
            "ranges": ["176.0.0.0/8", "185.0.0.0/8", "195.0.0.0/8"],
            "countries": ["RU", "NG", "BY", "UA"],
            "is_residential": True,
            "risk_base": 60,
        },
        "tor_exit": {
            "ranges": ["185.220.0.0/16", "198.96.0.0/16"],
            "countries": ["DE", "NL", "FR", "RO"],
            "is_tor": True,
            "risk_base": 80,
        },
        "vpn_commercial": {
            "ranges": ["104.238.0.0/16", "209.222.0.0/16"],
            "countries": ["US", "GB", "NL", "CH"],
            "is_vpn": True,
            "risk_base": 50,
        },
        "mobile_carrier": {
            "ranges": ["166.137.0.0/16", "174.240.0.0/16"],
            "countries": ["US"],
            "is_mobile": True,
            "risk_base": 15,
        },
    }
    
    # ISP database
    ISPS = {
        "US": [
            {"name": "Comcast Cable", "asn": 7922, "risk": 10},
            {"name": "AT&T Internet", "asn": 7018, "risk": 10},
            {"name": "Verizon Fios", "asn": 701, "risk": 10},
            {"name": "Charter Communications", "asn": 20115, "risk": 12},
            {"name": "Amazon AWS", "asn": 16509, "risk": 40},
            {"name": "Google Cloud", "asn": 15169, "risk": 40},
        ],
        "GB": [
            {"name": "British Telecom", "asn": 2856, "risk": 10},
            {"name": "Virgin Media", "asn": 5089, "risk": 12},
        ],
        "RU": [
            {"name": "Rostelecom", "asn": 12389, "risk": 55},
            {"name": "MTS", "asn": 8359, "risk": 50},
        ],
    }
    
    # City database for geolocation
    CITIES = {
        "US": [
            {"city": "New York", "region": "NY", "lat": 40.7128, "lon": -74.0060, "tz": "America/New_York", "postal": "10001"},
            {"city": "Los Angeles", "region": "CA", "lat": 34.0522, "lon": -118.2437, "tz": "America/Los_Angeles", "postal": "90001"},
            {"city": "Chicago", "region": "IL", "lat": 41.8781, "lon": -87.6298, "tz": "America/Chicago", "postal": "60601"},
            {"city": "Houston", "region": "TX", "lat": 29.7604, "lon": -95.3698, "tz": "America/Chicago", "postal": "77001"},
            {"city": "Phoenix", "region": "AZ", "lat": 33.4484, "lon": -112.0740, "tz": "America/Phoenix", "postal": "85001"},
        ],
        "GB": [
            {"city": "London", "region": "England", "lat": 51.5074, "lon": -0.1278, "tz": "Europe/London", "postal": "EC1A"},
            {"city": "Manchester", "region": "England", "lat": 53.4808, "lon": -2.2426, "tz": "Europe/London", "postal": "M1"},
        ],
        "RU": [
            {"city": "Moscow", "region": "Moscow", "lat": 55.7558, "lon": 37.6173, "tz": "Europe/Moscow", "postal": "101000"},
            {"city": "Saint Petersburg", "region": "Saint Petersburg", "lat": 59.9311, "lon": 30.3609, "tz": "Europe/Moscow", "postal": "190000"},
        ],
    }
    
    def __init__(self, fraud_mode: bool = False):
        self.fraud_mode = fraud_mode
        
    def _generate_ip_from_range(self, cidr: str) -> str:
        """Generate random IP from CIDR range"""
        network = ipaddress.ip_network(cidr)
        # Get random IP from network
        random_ip = random.randint(int(network.network_address), int(network.broadcast_address))
        return str(ipaddress.ip_address(random_ip))
    
    def _generate_geolocation(self, ip_profile: dict) -> IPGeolocation:
        """Generate geolocation data for IP"""
        country = random.choice(ip_profile.get("countries", ["US"]))
        cities = self.CITIES.get(country, self.CITIES["US"])
        city_data = random.choice(cities)
        
        isps = self.ISPS.get(country, self.ISPS["US"])
        isp_data = random.choice(isps)
        
        cidr = random.choice(ip_profile.get("ranges", ["24.0.0.0/8"]))
        ip_address = self._generate_ip_from_range(cidr)
        
        country_names = {
            "US": "United States",
            "GB": "United Kingdom", 
            "DE": "Germany",
            "FR": "France",
            "RU": "Russia",
            "NG": "Nigeria",
            "BY": "Belarus",
        }
        
        return IPGeolocation(
            ip_address=ip_address,
            country_code=country,
            country_name=country_names.get(country, country),
            region=city_data["region"],
            city=city_data["city"],
            postal_code=city_data["postal"],
            latitude=city_data["lat"] + random.uniform(-0.1, 0.1),
            longitude=city_data["lon"] + random.uniform(-0.1, 0.1),
            timezone=city_data["tz"],
            isp=isp_data["name"],
            organization=isp_data["name"],
            asn=isp_data["asn"],
            asn_name=f"AS{isp_data['asn']} {isp_data['name']}",
        )
    
    def _generate_reputation(self, ip_profile: dict) -> NetworkReputation:
        """Generate network reputation signals"""
        base_risk = ip_profile.get("risk_base", 20)
        
        if self.fraud_mode:
            base_risk += random.randint(10, 30)
            
        abuse_reports = 0
        last_abuse = None
        
        if base_risk > 50:
            abuse_reports = random.randint(1, 20)
            last_abuse = datetime.now() - timedelta(days=random.randint(1, 90))
            
        return NetworkReputation(
            is_proxy=ip_profile.get("is_proxy", False),
            is_vpn=ip_profile.get("is_vpn", False),
            is_tor=ip_profile.get("is_tor", False),
            is_datacenter=ip_profile.get("is_datacenter", False),
            is_residential=ip_profile.get("is_residential", False),
            is_mobile=ip_profile.get("is_mobile", False),
            reputation_score=min(100, base_risk + random.randint(-10, 10)),
            abuse_reports=abuse_reports,
            last_abuse_date=last_abuse,
        )
    
    def _generate_velocity(self, is_high_velocity: bool = False) -> NetworkVelocity:
        """Generate network velocity metrics"""
        
        if is_high_velocity or (self.fraud_mode and random.random() < 0.4):
            # High velocity - suspicious
            return NetworkVelocity(
                transactions_last_hour=random.randint(50, 200),
                transactions_last_day=random.randint(500, 2000),
                unique_cards_last_hour=random.randint(30, 100),
                unique_cards_last_day=random.randint(200, 500),
                unique_emails_last_hour=random.randint(20, 80),
                decline_rate_last_day=random.uniform(0.3, 0.7),
                fraud_rate_historical=random.uniform(0.05, 0.20),
            )
        else:
            # Normal velocity
            return NetworkVelocity(
                transactions_last_hour=random.randint(0, 5),
                transactions_last_day=random.randint(0, 20),
                unique_cards_last_hour=random.randint(0, 3),
                unique_cards_last_day=random.randint(0, 10),
                unique_emails_last_hour=random.randint(0, 3),
                decline_rate_last_day=random.uniform(0.01, 0.10),
                fraud_rate_historical=random.uniform(0.001, 0.01),
            )
    
    def generate(self, card_country: str = "US") -> NetworkIntelligence:
        """Generate complete network intelligence"""
        
        # Select IP profile
        if self.fraud_mode:
            profile_weights = {
                "us_residential": 0.2,
                "us_datacenter": 0.15,
                "high_risk_country": 0.25,
                "tor_exit": 0.15,
                "vpn_commercial": 0.20,
                "mobile_carrier": 0.05,
            }
        else:
            profile_weights = {
                "us_residential": 0.50,
                "us_datacenter": 0.05,
                "eu_residential": 0.15,
                "high_risk_country": 0.02,
                "tor_exit": 0.01,
                "vpn_commercial": 0.07,
                "mobile_carrier": 0.20,
            }
            
        profile_name = random.choices(
            list(profile_weights.keys()),
            weights=list(profile_weights.values())
        )[0]
        
        profile = self.IP_PROFILES[profile_name]
        
        geolocation = self._generate_geolocation(profile)
        reputation = self._generate_reputation(profile)
        velocity = self._generate_velocity()
        
        # Calculate matches
        card_country_match = geolocation.country_code == card_country
        
        # Calculate historical risk
        historical_risk = reputation.reputation_score
        
        if velocity.fraud_rate_historical > 0.05:
            historical_risk += 20
        if velocity.decline_rate_last_day > 0.3:
            historical_risk += 15
        if not card_country_match:
            historical_risk += 18  # Country mismatch
            
        return NetworkIntelligence(
            geolocation=geolocation,
            reputation=reputation,
            velocity=velocity,
            historical_risk_score=min(100, historical_risk),
            is_known_fraud_ip=reputation.reputation_score > 70,
            card_country_match=card_country_match,
            timezone_match=True,  # Would check against device timezone
        )
```

---

## 5. Transaction Characteristics

### 5.1 Overview

Transaction-level attributes include amount, currency, merchant category, and transaction type. These characteristics, when combined with historical patterns, provide strong fraud signals.

### 5.2 Data Elements and Generation

```python
class MerchantCategory(Enum):
    """Merchant Category Codes (MCC) - subset of common categories"""
    ELECTRONICS = "5732"
    DIGITAL_GOODS = "5818"
    GAMBLING = "7995"
    DATING = "7273"
    CRYPTO = "6051"
    JEWELRY = "5944"
    AIRLINES = "3000"
    HOTELS = "7011"
    GROCERY = "5411"
    GAS_STATION = "5541"
    RESTAURANT = "5812"
    FAST_FOOD = "5814"
    SUBSCRIPTION = "5968"
    SOFTWARE = "5734"
    CHARITY = "8398"

@dataclass
class TransactionCharacteristics:
    """Complete transaction characteristics"""
    amount: float
    currency: str
    mcc: str
    mcc_description: str
    transaction_type: str  # "card_present", "card_not_present"
    is_recurring: bool
    is_cross_border: bool
    is_3ds_authenticated: bool
    installment_count: Optional[int]
    merchant_name: str
    merchant_country: str
    descriptor: str
    metadata: Dict[str, Any]
    risk_score: float

class TransactionGenerator:
    """Generate synthetic transaction characteristics"""
    
    # MCC risk profiles
    MCC_RISK = {
        "5732": {"name": "Electronics Stores", "base_risk": 25, "avg_amount": 350},
        "5818": {"name": "Digital Goods", "base_risk": 35, "avg_amount": 50},
        "7995": {"name": "Gambling", "base_risk": 60, "avg_amount": 200},
        "7273": {"name": "Dating Services", "base_risk": 45, "avg_amount": 30},
        "6051": {"name": "Cryptocurrency", "base_risk": 70, "avg_amount": 500},
        "5944": {"name": "Jewelry Stores", "base_risk": 40, "avg_amount": 800},
        "3000": {"name": "Airlines", "base_risk": 20, "avg_amount": 450},
        "7011": {"name": "Hotels", "base_risk": 18, "avg_amount": 250},
        "5411": {"name": "Grocery Stores", "base_risk": 8, "avg_amount": 75},
        "5541": {"name": "Gas Stations", "base_risk": 15, "avg_amount": 50},
        "5812": {"name": "Restaurants", "base_risk": 10, "avg_amount": 45},
        "5814": {"name": "Fast Food", "base_risk": 8, "avg_amount": 15},
        "5968": {"name": "Subscription Services", "base_risk": 20, "avg_amount": 15},
        "5734": {"name": "Computer Software", "base_risk": 30, "avg_amount": 100},
        "8398": {"name": "Charitable Organizations", "base_risk": 35, "avg_amount": 50},
    }
    
    # Currency distribution
    CURRENCIES = {
        "USD": 0.60,
        "EUR": 0.15,
        "GBP": 0.10,
        "CAD": 0.05,
        "AUD": 0.03,
        "JPY": 0.02,
        "INR": 0.02,
        "BRL": 0.02,
        "MXN": 0.01,
    }
    
    def __init__(self, fraud_mode: bool = False):
        self.fraud_mode = fraud_mode
        
    def _generate_amount(self, mcc: str) -> float:
        """Generate transaction amount based on MCC"""
        mcc_profile = self.MCC_RISK.get(mcc, {"avg_amount": 100})
        avg_amount = mcc_profile["avg_amount"]
        
        if self.fraud_mode:
            # Fraud patterns
            pattern = random.choice(["card_testing", "high_value", "round_number"])
            
            if pattern == "card_testing":
                # Small amounts for testing
                return round(random.uniform(0.50, 5.00), 2)
            elif pattern == "high_value":
                # Attempt to extract maximum value
                return round(avg_amount * random.uniform(3.0, 10.0), 2)
            else:
                # Round numbers are suspicious
                return float(random.choice([100, 200, 500, 1000, 2000]))
        else:
            # Normal distribution around average
            amount = avg_amount * random.uniform(0.3, 2.5)
            # Add cents for realism
            return round(amount + random.uniform(0, 0.99), 2)
    
    def _select_mcc(self) -> str:
        """Select MCC based on fraud mode"""
        mccs = list(self.MCC_RISK.keys())
        
        if self.fraud_mode:
            # Weight toward high-risk MCCs
            weights = [self.MCC_RISK[m]["base_risk"] / 100 for m in mccs]
        else:
            # More uniform distribution
            weights = [1.0 for _ in mccs]
            
        total = sum(weights)
        weights = [w / total for w in weights]
        
        return random.choices(mccs, weights=weights)[0]
    
    def generate(self, 
                 card_country: str = "US",
                 merchant_country: str = "US") -> TransactionCharacteristics:
        """Generate complete transaction characteristics"""
        
        mcc = self._select_mcc()
        mcc_profile = self.MCC_RISK[mcc]
        
        amount = self._generate_amount(mcc)
        
        # Currency based on merchant country
        if merchant_country in ["US", "CA", "MX"]:
            currency = "USD" if merchant_country == "US" else random.choice(["USD", "CAD", "MXN"])
        elif merchant_country in ["GB"]:
            currency = "GBP"
        elif merchant_country in ["DE", "FR", "IT", "ES", "NL"]:
            currency = "EUR"
        else:
            currency = random.choices(
                list(self.CURRENCIES.keys()),
                weights=list(self.CURRENCIES.values())
            )[0]
            
        # Transaction type
        if mcc in ["5411", "5541", "5812", "5814"]:  # In-person typical
            transaction_type = "card_present" if random.random() < 0.7 else "card_not_present"
        else:
            transaction_type = "card_not_present"
            
        is_cross_border = card_country != merchant_country
        
        # 3DS authentication
        is_3ds = random.random() < (0.3 if not self.fraud_mode else 0.1)
        
        # Recurring
        is_recurring = mcc in ["5968", "5734"] and random.random() < 0.4
        
        # Calculate risk
        risk_score = mcc_profile["base_risk"]
        
        # Amount anomaly
        if amount > mcc_profile["avg_amount"] * 3:
            risk_score += 20
        if amount < 5:  # Card testing
            risk_score += 15
            
        # Cross-border
        if is_cross_border:
            risk_score += 18
            
        # Round amount
        if amount == int(amount):
            risk_score += 8
            
        # No 3DS
        if not is_3ds and transaction_type == "card_not_present":
            risk_score += 10
            
        # Generate merchant name
        merchant_names = {
            "5732": ["Best Buy", "Amazon Electronics", "Newegg"],
            "5818": ["Steam", "PlayStation Store", "App Store"],
            "7995": ["DraftKings", "FanDuel", "MGM Online"],
            "5411": ["Whole Foods", "Kroger", "Safeway"],
            "5812": ["Olive Garden", "Chipotle", "Local Restaurant"],
        }
        merchant_name = random.choice(merchant_names.get(mcc, [f"Merchant_{mcc}"]))
        
        return TransactionCharacteristics(
            amount=amount,
            currency=currency,
            mcc=mcc,
            mcc_description=mcc_profile["name"],
            transaction_type=transaction_type,
            is_recurring=is_recurring,
            is_cross_border=is_cross_border,
            is_3ds_authenticated=is_3ds,
            installment_count=None,
            merchant_name=merchant_name,
            merchant_country=merchant_country,
            descriptor=f"{merchant_name[:15].upper()}*{mcc}",
            metadata={},
            risk_score=min(100, risk_score),
        )
```

---

## 6. Velocity and Frequency Metrics

### 6.1 Overview

Velocity metrics track the rate of activity across multiple dimensions: cards per email, transactions per IP, failed attempts, and spending patterns. These signals are critical for detecting coordinated attacks.

### 6.2 Data Elements and Generation

```python
@dataclass
class VelocityMetrics:
    """Complete velocity and frequency metrics"""
    # Card velocity
    cards_per_email_hourly: int
    cards_per_email_daily: int
    cards_per_email_weekly: int
    
    # Transaction velocity  
    transactions_per_ip_hourly: int
    transactions_per_ip_daily: int
    transactions_per_card_hourly: int
    transactions_per_card_daily: int
    
    # Failure velocity
    failed_attempts_per_card_hourly: int
    failed_attempts_per_card_daily: int
    failed_attempts_per_ip_hourly: int
    
    # Amount velocity
    amount_sum_hourly: float
    amount_sum_daily: float
    amount_avg_daily: float
    amount_velocity_ratio: float  # Current vs. historical average
    
    # Account velocity
    new_accounts_per_ip_daily: int
    new_accounts_per_device_daily: int
    
    # Risk calculations
    velocity_risk_score: float
    is_card_testing_pattern: bool
    is_enumeration_attack: bool
    is_velocity_abuse: bool

class VelocityGenerator:
    """Generate synthetic velocity metrics"""
    
    def __init__(self, fraud_mode: bool = False):
        self.fraud_mode = fraud_mode
        
    def generate(self, 
                 transaction_amount: float = 100.0,
                 is_card_testing: bool = False) -> VelocityMetrics:
        """Generate velocity metrics"""
        
        if self.fraud_mode:
            if is_card_testing or random.random() < 0.3:
                # Card testing attack pattern
                return self._generate_card_testing_velocity()
            elif random.random() < 0.3:
                # Enumeration attack
                return self._generate_enumeration_velocity()
            else:
                # General fraud velocity
                return self._generate_fraud_velocity(transaction_amount)
        else:
            return self._generate_normal_velocity(transaction_amount)
    
    def _generate_card_testing_velocity(self) -> VelocityMetrics:
        """Generate card testing attack velocity pattern"""
        # High card count, small amounts, many failures
        return VelocityMetrics(
            cards_per_email_hourly=random.randint(10, 50),
            cards_per_email_daily=random.randint(50, 200),
            cards_per_email_weekly=random.randint(200, 500),
            transactions_per_ip_hourly=random.randint(20, 100),
            transactions_per_ip_daily=random.randint(100, 500),
            transactions_per_card_hourly=random.randint(1, 3),
            transactions_per_card_daily=random.randint(1, 5),
            failed_attempts_per_card_hourly=random.randint(1, 3),
            failed_attempts_per_card_daily=random.randint(2, 10),
            failed_attempts_per_ip_hourly=random.randint(20, 80),
            amount_sum_hourly=random.uniform(10, 100),
            amount_sum_daily=random.uniform(50, 500),
            amount_avg_daily=random.uniform(1, 5),  # Small amounts
            amount_velocity_ratio=0.2,  # Below normal
            new_accounts_per_ip_daily=random.randint(5, 20),
            new_accounts_per_device_daily=random.randint(3, 10),
            velocity_risk_score=85.0,
            is_card_testing_pattern=True,
            is_enumeration_attack=False,
            is_velocity_abuse=True,
        )
    
    def _generate_enumeration_velocity(self) -> VelocityMetrics:
        """Generate BIN enumeration attack velocity"""
        # Sequential card numbers, high failure rate
        return VelocityMetrics(
            cards_per_email_hourly=random.randint(50, 200),
            cards_per_email_daily=random.randint(500, 2000),
            cards_per_email_weekly=random.randint(2000, 5000),
            transactions_per_ip_hourly=random.randint(100, 500),
            transactions_per_ip_daily=random.randint(1000, 5000),
            transactions_per_card_hourly=1,  # One attempt per card
            transactions_per_card_daily=1,
            failed_attempts_per_card_hourly=1,
            failed_attempts_per_card_daily=1,
            failed_attempts_per_ip_hourly=random.randint(80, 400),  # High failure
            amount_sum_hourly=random.uniform(50, 500),
            amount_sum_daily=random.uniform(500, 5000),
            amount_avg_daily=random.uniform(1, 2),  # $1-2 test amounts
            amount_velocity_ratio=0.1,
            new_accounts_per_ip_daily=random.randint(50, 200),
            new_accounts_per_device_daily=random.randint(20, 100),
            velocity_risk_score=95.0,
            is_card_testing_pattern=False,
            is_enumeration_attack=True,
            is_velocity_abuse=True,
        )
    
    def _generate_fraud_velocity(self, amount: float) -> VelocityMetrics:
        """Generate general fraud velocity pattern"""
        return VelocityMetrics(
            cards_per_email_hourly=random.randint(2, 10),
            cards_per_email_daily=random.randint(5, 30),
            cards_per_email_weekly=random.randint(15, 50),
            transactions_per_ip_hourly=random.randint(5, 20),
            transactions_per_ip_daily=random.randint(20, 80),
            transactions_per_card_hourly=random.randint(2, 5),
            transactions_per_card_daily=random.randint(5, 15),
            failed_attempts_per_card_hourly=random.randint(1, 3),
            failed_attempts_per_card_daily=random.randint(2, 8),
            failed_attempts_per_ip_hourly=random.randint(3, 15),
            amount_sum_hourly=amount * random.uniform(3, 10),
            amount_sum_daily=amount * random.uniform(10, 30),
            amount_avg_daily=amount * random.uniform(0.8, 1.5),
            amount_velocity_ratio=random.uniform(2.0, 5.0),  # Above normal
            new_accounts_per_ip_daily=random.randint(1, 5),
            new_accounts_per_device_daily=random.randint(1, 3),
            velocity_risk_score=60.0,
            is_card_testing_pattern=False,
            is_enumeration_attack=False,
            is_velocity_abuse=True,
        )
    
    def _generate_normal_velocity(self, amount: float) -> VelocityMetrics:
        """Generate normal user velocity pattern"""
        return VelocityMetrics(
            cards_per_email_hourly=random.randint(0, 1),
            cards_per_email_daily=random.randint(0, 2),
            cards_per_email_weekly=random.randint(1, 3),
            transactions_per_ip_hourly=random.randint(0, 3),
            transactions_per_ip_daily=random.randint(1, 10),
            transactions_per_card_hourly=random.randint(0, 2),
            transactions_per_card_daily=random.randint(1, 5),
            failed_attempts_per_card_hourly=0,
            failed_attempts_per_card_daily=random.randint(0, 1),
            failed_attempts_per_ip_hourly=random.randint(0, 1),
            amount_sum_hourly=amount,
            amount_sum_daily=amount * random.uniform(1, 3),
            amount_avg_daily=amount * random.uniform(0.7, 1.3),
            amount_velocity_ratio=random.uniform(0.8, 1.2),
            new_accounts_per_ip_daily=random.randint(0, 1),
            new_accounts_per_device_daily=0,
            velocity_risk_score=random.uniform(5, 20),
            is_card_testing_pattern=False,
            is_enumeration_attack=False,
            is_velocity_abuse=False,
        )
```

---

## 7. Identity Verification Signals

### 7.1 Overview

Identity verification signals compare provided information against card network data and detect mismatches that indicate fraud, such as AVS failures, disposable emails, and name mismatches.

### 7.2 Data Elements and Generation

```python
class AVSResult(Enum):
    """Address Verification System result codes"""
    MATCH = "Y"  # Address and postal code match
    PARTIAL_MATCH_ADDRESS = "A"  # Address matches, postal doesn't
    PARTIAL_MATCH_POSTAL = "Z"  # Postal matches, address doesn't
    NO_MATCH = "N"  # Neither match
    NOT_SUPPORTED = "S"  # Issuer doesn't support AVS
    UNAVAILABLE = "U"  # System unavailable
    NOT_PROVIDED = "G"  # Global/International, not supported

class CVVResult(Enum):
    """CVV verification result codes"""
    MATCH = "M"
    NO_MATCH = "N"
    NOT_PROCESSED = "P"
    NOT_PROVIDED = "S"
    ISSUER_NOT_CERTIFIED = "U"

@dataclass
class IdentityVerification:
    """Complete identity verification signals"""
    # AVS results
    avs_result: AVSResult
    avs_address_line1_check: str
    avs_postal_code_check: str
    
    # CVV result
    cvv_result: CVVResult
    
    # Name verification
    cardholder_name: str
    email_name_match_score: float  # 0-1
    shipping_name_match_score: float
    
    # Address verification
    billing_address: Dict[str, str]
    shipping_address: Optional[Dict[str, str]]
    billing_shipping_match: bool
    
    # Email signals
    email: str
    email_domain: str
    is_disposable_email: bool
    is_free_email: bool
    email_age_days: int
    email_domain_reputation: float  # 0-100
    
    # Phone signals
    phone: Optional[str]
    phone_carrier: Optional[str]
    is_voip: bool
    phone_country_match: bool
    
    # Combined risk
    identity_risk_score: float

class IdentityVerificationGenerator:
    """Generate synthetic identity verification data"""
    
    DISPOSABLE_EMAIL_DOMAINS = [
        "tempmail.com", "guerrillamail.com", "10minutemail.com",
        "mailinator.com", "throwaway.email", "temp-mail.org",
        "fakemailgenerator.com", "yopmail.com", "trashmail.com",
    ]
    
    FREE_EMAIL_DOMAINS = [
        "gmail.com", "yahoo.com", "hotmail.com", "outlook.com",
        "aol.com", "icloud.com", "protonmail.com", "mail.com",
    ]
    
    CORPORATE_EMAIL_DOMAINS = [
        "company.com", "business.org", "enterprise.net", "corp.io",
    ]
    
    def __init__(self, fraud_mode: bool = False):
        self.fraud_mode = fraud_mode
        
    def _generate_email(self, cardholder_name: str) -> Tuple[str, str]:
        """Generate email address"""
        name_parts = cardholder_name.lower().split()
        
        if self.fraud_mode:
            if random.random() < 0.25:
                # Disposable email
                domain = random.choice(self.DISPOSABLE_EMAIL_DOMAINS)
                local = f"user{random.randint(100000, 999999)}"
            elif random.random() < 0.5:
                # Random free email (doesn't match name)
                domain = random.choice(self.FREE_EMAIL_DOMAINS)
                local = f"random{random.randint(1000, 9999)}"
            else:
                # Normal-looking email
                domain = random.choice(self.FREE_EMAIL_DOMAINS)
                local = f"{name_parts[0]}{random.randint(1, 99)}"
        else:
            domain = random.choice(self.FREE_EMAIL_DOMAINS + self.CORPORATE_EMAIL_DOMAINS)
            local_patterns = [
                f"{name_parts[0]}.{name_parts[-1]}" if len(name_parts) > 1 else name_parts[0],
                f"{name_parts[0][0]}{name_parts[-1]}" if len(name_parts) > 1 else name_parts[0],
                f"{name_parts[0]}{random.randint(1, 99)}",
            ]
            local = random.choice(local_patterns)
            
        return f"{local}@{domain}", domain
    
    def _calculate_name_match(self, name1: str, name2: str) -> float:
        """Calculate name similarity score"""
        # Simplified string matching
        name1_parts = set(name1.lower().split())
        name2_parts = set(name2.lower().split())
        
        if not name1_parts or not name2_parts:
            return 0.0
            
        intersection = len(name1_parts & name2_parts)
        union = len(name1_parts | name2_parts)
        
        return intersection / union if union > 0 else 0.0
    
    def _generate_address(self, country: str = "US") -> Dict[str, str]:
        """Generate address"""
        us_streets = ["Main St", "Oak Ave", "Elm St", "Park Blvd", "1st Ave", "2nd St"]
        us_cities = ["Springfield", "Franklin", "Clinton", "Madison", "Georgetown"]
        us_states = ["CA", "NY", "TX", "FL", "IL", "PA", "OH", "GA", "NC", "MI"]
        
        if country == "US":
            return {
                "line1": f"{random.randint(100, 9999)} {random.choice(us_streets)}",
                "line2": "" if random.random() > 0.3 else f"Apt {random.randint(1, 500)}",
                "city": random.choice(us_cities),
                "state": random.choice(us_states),
                "postal_code": f"{random.randint(10000, 99999)}",
                "country": "US",
            }
        else:
            return {
                "line1": f"{random.randint(1, 500)} High Street",
                "city": "London",
                "postal_code": "SW1A 1AA",
                "country": country,
            }
    
    def generate(self, 
                 cardholder_name: str = "John Smith",
                 card_country: str = "US") -> IdentityVerification:
        """Generate complete identity verification signals"""
        
        email, email_domain = self._generate_email(cardholder_name)
        
        # Determine if disposable
        is_disposable = email_domain in self.DISPOSABLE_EMAIL_DOMAINS
        is_free = email_domain in self.FREE_EMAIL_DOMAINS
        
        # Email age
        if is_disposable:
            email_age = random.randint(0, 7)  # Very new
        elif self.fraud_mode:
            email_age = random.randint(0, 90)
        else:
            email_age = random.randint(180, 3650)  # 6 months to 10 years
            
        # Email name match
        email_local = email.split("@")[0]
        email_name_match = self._calculate_name_match(cardholder_name, email_local)
        
        # Generate addresses
        billing_address = self._generate_address(card_country)
        
        # Shipping address
        if self.fraud_mode and random.random() < 0.4:
            # Different shipping address
            shipping_address = self._generate_address(card_country)
            billing_shipping_match = False
        elif random.random() < 0.2:
            # Different shipping for legitimate reasons
            shipping_address = self._generate_address(card_country)
            billing_shipping_match = random.random() < 0.3
        else:
            shipping_address = billing_address.copy()
            billing_shipping_match = True
            
        # AVS results
        if self.fraud_mode:
            avs_result = random.choices(
                [AVSResult.NO_MATCH, AVSResult.PARTIAL_MATCH_ADDRESS, AVSResult.MATCH],
                weights=[0.4, 0.3, 0.3]
            )[0]
        else:
            avs_result = random.choices(
                [AVSResult.MATCH, AVSResult.PARTIAL_MATCH_POSTAL, AVSResult.NO_MATCH],
                weights=[0.75, 0.15, 0.10]
            )[0]
            
        # CVV results
        if self.fraud_mode:
            cvv_result = random.choices(
                [CVVResult.NO_MATCH, CVVResult.MATCH],
                weights=[0.3, 0.7]
            )[0]
        else:
            cvv_result = random.choices(
                [CVVResult.MATCH, CVVResult.NOT_PROCESSED],
                weights=[0.95, 0.05]
            )[0]
            
        # Calculate risk score
        risk_score = 0.0
        
        if is_disposable:
            risk_score += 40
        elif is_free:
            risk_score += 5
            
        if email_age < 30:
            risk_score += 20
        elif email_age < 180:
            risk_score += 10
            
        if email_name_match < 0.3:
            risk_score += 15
            
        if avs_result == AVSResult.NO_MATCH:
            risk_score += 25
        elif avs_result == AVSResult.PARTIAL_MATCH_ADDRESS:
            risk_score += 12
            
        if cvv_result == CVVResult.NO_MATCH:
            risk_score += 30
            
        if not billing_shipping_match:
            risk_score += 15
            
        return IdentityVerification(
            avs_result=avs_result,
            avs_address_line1_check="pass" if avs_result in [AVSResult.MATCH, AVSResult.PARTIAL_MATCH_ADDRESS] else "fail",
            avs_postal_code_check="pass" if avs_result in [AVSResult.MATCH, AVSResult.PARTIAL_MATCH_POSTAL] else "fail",
            cvv_result=cvv_result,
            cardholder_name=cardholder_name,
            email_name_match_score=email_name_match,
            shipping_name_match_score=email_name_match * random.uniform(0.9, 1.0),
            billing_address=billing_address,
            shipping_address=shipping_address,
            billing_shipping_match=billing_shipping_match,
            email=email,
            email_domain=email_domain,
            is_disposable_email=is_disposable,
            is_free_email=is_free,
            email_age_days=email_age,
            email_domain_reputation=20.0 if is_disposable else (50.0 if is_free else 80.0),
            phone=None,
            phone_carrier=None,
            is_voip=False,
            phone_country_match=True,
            identity_risk_score=min(100, risk_score),
        )
```

---

## 8. Network-Wide Signals

### 8.1 Overview

Network-wide signals leverage Stripe's position as a payment processor to identify cards that have been involved in fraud across their merchant network, including TC40/SAFE reports and cross-merchant patterns.

### 8.2 Data Elements and Generation

```python
@dataclass
class NetworkWideSignals:
    """Network-wide fraud signals from payment processor network"""
    # Fraud reports
    has_tc40_report: bool  # Visa fraud report
    tc40_report_date: Optional[datetime]
    has_safe_report: bool  # Mastercard fraud report
    safe_report_date: Optional[datetime]
    
    # Early warnings
    has_early_fraud_warning: bool
    efw_date: Optional[datetime]
    efw_reason: Optional[str]
    
    # Cross-merchant signals
    card_seen_on_network: bool
    card_first_seen_date: Optional[datetime]
    card_merchant_count: int
    card_successful_txn_count: int
    card_declined_txn_count: int
    card_disputed_txn_count: int
    
    # Email signals across network
    email_seen_on_network: bool
    email_card_count: int
    email_merchant_count: int
    email_fraud_rate: float
    
    # Device signals across network
    device_seen_on_network: bool
    device_card_count: int
    device_email_count: int
    device_fraud_rate: float
    
    # Combined signals
    network_risk_score: float
    is_known_fraudulent_card: bool
    is_known_fraudulent_device: bool
    is_known_fraudulent_email: bool

class NetworkWideSignalGenerator:
    """Generate synthetic network-wide signals"""
    
    EFW_REASONS = [
        "Card reported stolen",
        "Card reported lost",
        "Account takeover suspected",
        "Cardholder claims fraud",
        "Unusual transaction pattern",
    ]
    
    def __init__(self, fraud_mode: bool = False):
        self.fraud_mode = fraud_mode
        
    def generate(self,
                 card_age_days: int = 365,
                 email_age_days: int = 365) -> NetworkWideSignals:
        """Generate network-wide signals"""
        
        now = datetime.now()
        
        if self.fraud_mode:
            return self._generate_fraudulent_signals(now, card_age_days)
        else:
            return self._generate_legitimate_signals(now, card_age_days)
    
    def _generate_fraudulent_signals(self, now: datetime, card_age_days: int) -> NetworkWideSignals:
        """Generate signals for known fraudulent entities"""
        
        # TC40/SAFE reports
        has_tc40 = random.random() < 0.4
        has_safe = random.random() < 0.35
        has_efw = random.random() < 0.3
        
        # Cross-merchant signals - card used fraudulently elsewhere
        card_seen = random.random() < 0.7
        if card_seen:
            card_first_seen = now - timedelta(days=random.randint(1, card_age_days))
            merchant_count = random.randint(1, 10)
            successful = random.randint(0, 20)
            declined = random.randint(5, 50)
            disputed = random.randint(1, 10)
        else:
            card_first_seen = None
            merchant_count = 0
            successful = 0
            declined = 0
            disputed = 0
            
        # Email signals
        email_seen = True
        email_card_count = random.randint(5, 30)  # Many cards on one email
        email_merchant_count = random.randint(3, 15)
        email_fraud_rate = random.uniform(0.1, 0.5)
        
        # Device signals
        device_seen = True
        device_card_count = random.randint(10, 50)  # Many cards on one device
        device_email_count = random.randint(5, 20)
        device_fraud_rate = random.uniform(0.15, 0.6)
        
        # Network risk calculation
        risk_score = 50.0
        if has_tc40 or has_safe:
            risk_score += 30
        if has_efw:
            risk_score += 20
        if email_fraud_rate > 0.2:
            risk_score += 15
        if device_fraud_rate > 0.2:
            risk_score += 15
        if disputed > 2:
            risk_score += 10
            
        return NetworkWideSignals(
            has_tc40_report=has_tc40,
            tc40_report_date=now - timedelta(days=random.randint(1, 30)) if has_tc40 else None,
            has_safe_report=has_safe,
            safe_report_date=now - timedelta(days=random.randint(1, 30)) if has_safe else None,
            has_early_fraud_warning=has_efw,
            efw_date=now - timedelta(days=random.randint(1, 14)) if has_efw else None,
            efw_reason=random.choice(self.EFW_REASONS) if has_efw else None,
            card_seen_on_network=card_seen,
            card_first_seen_date=card_first_seen,
            card_merchant_count=merchant_count,
            card_successful_txn_count=successful,
            card_declined_txn_count=declined,
            card_disputed_txn_count=disputed,
            email_seen_on_network=email_seen,
            email_card_count=email_card_count,
            email_merchant_count=email_merchant_count,
            email_fraud_rate=email_fraud_rate,
            device_seen_on_network=device_seen,
            device_card_count=device_card_count,
            device_email_count=device_email_count,
            device_fraud_rate=device_fraud_rate,
            network_risk_score=min(100, risk_score),
            is_known_fraudulent_card=has_tc40 or has_safe or disputed > 2,
            is_known_fraudulent_device=device_fraud_rate > 0.3,
            is_known_fraudulent_email=email_fraud_rate > 0.3,
        )
    
    def _generate_legitimate_signals(self, now: datetime, card_age_days: int) -> NetworkWideSignals:
        """Generate signals for legitimate transactions"""
        
        # No fraud reports
        has_tc40 = False
        has_safe = False
        has_efw = False
        
        # Card seen on network with good history
        card_seen = random.random() < 0.6
        if card_seen:
            card_first_seen = now - timedelta(days=random.randint(30, card_age_days))
            merchant_count = random.randint(1, 10)
            successful = random.randint(5, 100)
            declined = random.randint(0, 5)
            disputed = random.randint(0, 1)
        else:
            card_first_seen = None
            merchant_count = 0
            successful = 0
            declined = 0
            disputed = 0
            
        # Email with normal patterns
        email_seen = random.random() < 0.5
        email_card_count = random.randint(1, 3)
        email_merchant_count = random.randint(1, 5)
        email_fraud_rate = random.uniform(0.0, 0.02)
        
        # Device with normal patterns
        device_seen = random.random() < 0.4
        device_card_count = random.randint(1, 3)
        device_email_count = random.randint(1, 2)
        device_fraud_rate = random.uniform(0.0, 0.01)
        
        # Low risk score
        risk_score = random.uniform(5, 20)
        
        return NetworkWideSignals(
            has_tc40_report=has_tc40,
            tc40_report_date=None,
            has_safe_report=has_safe,
            safe_report_date=None,
            has_early_fraud_warning=has_efw,
            efw_date=None,
            efw_reason=None,
            card_seen_on_network=card_seen,
            card_first_seen_date=card_first_seen,
            card_merchant_count=merchant_count,
            card_successful_txn_count=successful,
            card_declined_txn_count=declined,
            card_disputed_txn_count=disputed,
            email_seen_on_network=email_seen,
            email_card_count=email_card_count,
            email_merchant_count=email_merchant_count,
            email_fraud_rate=email_fraud_rate,
            device_seen_on_network=device_seen,
            device_card_count=device_card_count,
            device_email_count=device_email_count,
            device_fraud_rate=device_fraud_rate,
            network_risk_score=risk_score,
            is_known_fraudulent_card=False,
            is_known_fraudulent_device=False,
            is_known_fraudulent_email=False,
        )
```

---

## 9. Integrated Synthetic Dataset Generator

### 9.1 Complete Transaction Generator

```python
@dataclass
class SyntheticTransaction:
    """Complete synthetic transaction with all signal categories"""
    transaction_id: str
    timestamp: datetime
    
    # Core components
    card: SyntheticCard
    device: DeviceFingerprint
    behavior: BehavioralFingerprint
    network: NetworkIntelligence
    transaction: TransactionCharacteristics
    velocity: VelocityMetrics
    identity: IdentityVerification
    network_wide: NetworkWideSignals
    
    # Labels
    is_fraud: bool
    fraud_type: Optional[str]
    
    # Aggregated scores
    total_risk_score: float
    risk_level: RiskLevel
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for export"""
        return {
            "transaction_id": self.transaction_id,
            "timestamp": self.timestamp.isoformat(),
            "is_fraud": self.is_fraud,
            "fraud_type": self.fraud_type,
            "total_risk_score": self.total_risk_score,
            "risk_level": self.risk_level.value,
            
            # Card features
            "card_brand": self.card.bin_profile.brand.value,
            "card_type": self.card.bin_profile.card_type.value,
            "card_country": self.card.bin_profile.issuing_country,
            "card_risk_score": self.card.bin_profile.risk_score,
            "card_expiry_risk": self.card.expiry_proximity_risk,
            "is_prepaid": self.card.bin_profile.card_type == CardType.PREPAID,
            
            # Device features
            "device_id": self.device.fingerprint_id,
            "device_is_bot": self.device.is_bot,
            "device_is_emulator": self.device.is_emulator,
            "device_is_vm": self.device.is_vm,
            "device_is_incognito": self.device.is_incognito,
            "device_risk_score": self.device.risk_score,
            
            # Behavior features
            "behavior_is_bot_likely": self.behavior.is_bot_likely,
            "behavior_is_automated": self.behavior.is_automated,
            "behavior_risk_score": self.behavior.risk_score,
            "mouse_straightness": self.behavior.mouse_pattern.straightness_ratio,
            "typing_wpm": self.behavior.typing_pattern.wpm,
            "copy_paste_detected": self.behavior.typing_pattern.copy_paste_detected,
            "time_on_page_ms": self.behavior.navigation_pattern.time_on_checkout_page_ms,
            
            # Network features
            "ip_country": self.network.geolocation.country_code,
            "ip_is_vpn": self.network.reputation.is_vpn,
            "ip_is_tor": self.network.reputation.is_tor,
            "ip_is_proxy": self.network.reputation.is_proxy,
            "ip_is_datacenter": self.network.reputation.is_datacenter,
            "ip_reputation_score": self.network.reputation.reputation_score,
            "card_country_match": self.network.card_country_match,
            
            # Transaction features
            "amount": self.transaction.amount,
            "currency": self.transaction.currency,
            "mcc": self.transaction.mcc,
            "is_cross_border": self.transaction.is_cross_border,
            "is_3ds": self.transaction.is_3ds_authenticated,
            "transaction_risk_score": self.transaction.risk_score,
            
            # Velocity features
            "cards_per_email_hourly": self.velocity.cards_per_email_hourly,
            "transactions_per_ip_hourly": self.velocity.transactions_per_ip_hourly,
            "failed_attempts_per_card": self.velocity.failed_attempts_per_card_daily,
            "is_card_testing": self.velocity.is_card_testing_pattern,
            "is_velocity_abuse": self.velocity.is_velocity_abuse,
            "velocity_risk_score": self.velocity.velocity_risk_score,
            
            # Identity features
            "avs_result": self.identity.avs_result.value,
            "cvv_result": self.identity.cvv_result.value,
            "is_disposable_email": self.identity.is_disposable_email,
            "email_age_days": self.identity.email_age_days,
            "billing_shipping_match": self.identity.billing_shipping_match,
            "identity_risk_score": self.identity.identity_risk_score,
            
            # Network-wide features
            "has_fraud_report": self.network_wide.has_tc40_report or self.network_wide.has_safe_report,
            "has_early_fraud_warning": self.network_wide.has_early_fraud_warning,
            "email_fraud_rate": self.network_wide.email_fraud_rate,
            "device_fraud_rate": self.network_wide.device_fraud_rate,
            "network_risk_score": self.network_wide.network_risk_score,
        }

class SyntheticDatasetGenerator:
    """Generate complete synthetic datasets for fraud detection"""
    
    FRAUD_TYPES = [
        "card_testing",
        "stolen_card",
        "account_takeover",
        "friendly_fraud",
        "synthetic_identity",
        "card_not_present",
        "cross_border",
    ]
    
    def __init__(self, fraud_rate: float = 0.01):
        """
        Initialize generator.
        
        Args:
            fraud_rate: Target fraud rate (default 0.01 = 1%)
        """
        self.fraud_rate = fraud_rate
        
    def _generate_transaction(self, is_fraud: bool, fraud_type: Optional[str] = None) -> SyntheticTransaction:
        """Generate a single synthetic transaction"""
        
        # Initialize generators
        card_gen = CardCharacteristicsGenerator(fraud_mode=is_fraud)
        device_gen = DeviceFingerprintGenerator(fraud_mode=is_fraud)
        behavior_gen = BehavioralSignalGenerator(fraud_mode=is_fraud)
        
        # Generate card first (needed for country matching)
        card = card_gen.generate_card()
        card_country = card.bin_profile.issuing_country
        
        # Generate other components
        network_gen = NetworkIntelligenceGenerator(fraud_mode=is_fraud)
        network = network_gen.generate(card_country=card_country)
        
        txn_gen = TransactionGenerator(fraud_mode=is_fraud)
        transaction = txn_gen.generate(
            card_country=card_country,
            merchant_country="US"  # Assume US merchant
        )
        
        velocity_gen = VelocityGenerator(fraud_mode=is_fraud)
        velocity = velocity_gen.generate(
            transaction_amount=transaction.amount,
            is_card_testing=fraud_type == "card_testing" if fraud_type else False
        )
        
        identity_gen = IdentityVerificationGenerator(fraud_mode=is_fraud)
        identity = identity_gen.generate(
            cardholder_name=card.cardholder_name,
            card_country=card_country
        )
        
        network_wide_gen = NetworkWideSignalGenerator(fraud_mode=is_fraud)
        network_wide = network_wide_gen.generate(
            card_age_days=max(1, card.days_until_expiry + 365)
        )
        
        device = device_gen.generate()
        behavior = behavior_gen.generate()
        
        # Calculate total risk score (weighted average)
        weights = {
            "card": 0.10,
            "device": 0.12,
            "behavior": 0.15,
            "network": 0.13,
            "transaction": 0.10,
            "velocity": 0.15,
            "identity": 0.12,
            "network_wide": 0.13,
        }
        
        total_risk = (
            weights["card"] * card.bin_profile.risk_score +
            weights["device"] * device.risk_score +
            weights["behavior"] * behavior.risk_score +
            weights["network"] * network.historical_risk_score +
            weights["transaction"] * transaction.risk_score +
            weights["velocity"] * velocity.velocity_risk_score +
            weights["identity"] * identity.identity_risk_score +
            weights["network_wide"] * network_wide.network_risk_score
        )
        
        # Determine risk level
        if total_risk < 20:
            risk_level = RiskLevel.LOW
        elif total_risk < 40:
            risk_level = RiskLevel.MEDIUM
        elif total_risk < 60:
            risk_level = RiskLevel.ELEVATED
        elif total_risk < 80:
            risk_level = RiskLevel.HIGH
        else:
            risk_level = RiskLevel.HIGHEST
            
        return SyntheticTransaction(
            transaction_id=hashlib.md5(str(random.random()).encode()).hexdigest()[:24],
            timestamp=datetime.now() - timedelta(
                days=random.randint(0, 365),
                hours=random.randint(0, 23),
                minutes=random.randint(0, 59)
            ),
            card=card,
            device=device,
            behavior=behavior,
            network=network,
            transaction=transaction,
            velocity=velocity,
            identity=identity,
            network_wide=network_wide,
            is_fraud=is_fraud,
            fraud_type=fraud_type,
            total_risk_score=total_risk,
            risk_level=risk_level,
        )
    
    def generate_dataset(self, 
                        num_transactions: int,
                        include_edge_cases: bool = True) -> List[SyntheticTransaction]:
        """Generate a complete synthetic dataset"""
        
        transactions = []
        num_fraud = int(num_transactions * self.fraud_rate)
        num_legitimate = num_transactions - num_fraud
        
        print(f"Generating {num_transactions} transactions ({num_fraud} fraud, {num_legitimate} legitimate)...")
        
        # Generate legitimate transactions
        for _ in range(num_legitimate):
            txn = self._generate_transaction(is_fraud=False)
            transactions.append(txn)
            
        # Generate fraud transactions with varied types
        for i in range(num_fraud):
            fraud_type = random.choice(self.FRAUD_TYPES)
            txn = self._generate_transaction(is_fraud=True, fraud_type=fraud_type)
            transactions.append(txn)
            
        # Add edge cases if requested
        if include_edge_cases:
            edge_cases = self._generate_edge_cases()
            transactions.extend(edge_cases)
            
        # Shuffle
        random.shuffle(transactions)
        
        return transactions
    
    def _generate_edge_cases(self) -> List[SyntheticTransaction]:
        """Generate edge case transactions for testing"""
        edge_cases = []
        
        # Edge case 1: High-value legitimate transaction
        txn = self._generate_transaction(is_fraud=False)
        txn.transaction.amount = 5000.00  # High value
        txn.fraud_type = None
        edge_cases.append(txn)
        
        # Edge case 2: First-time user, legitimate
        txn = self._generate_transaction(is_fraud=False)
        txn.network_wide.card_seen_on_network = False
        txn.network_wide.email_seen_on_network = False
        txn.identity.email_age_days = 7  # New email
        edge_cases.append(txn)
        
        # Edge case 3: VPN user, legitimate (privacy-conscious)
        txn = self._generate_transaction(is_fraud=False)
        txn.network.reputation.is_vpn = True
        edge_cases.append(txn)
        
        # Edge case 4: International traveler, legitimate
        txn = self._generate_transaction(is_fraud=False)
        txn.network.card_country_match = False
        txn.transaction.is_cross_border = True
        edge_cases.append(txn)
        
        # Edge case 5: Card testing attempt (fraud)
        txn = self._generate_transaction(is_fraud=True, fraud_type="card_testing")
        txn.transaction.amount = 1.00
        txn.velocity.is_card_testing_pattern = True
        edge_cases.append(txn)
        
        return edge_cases
    
    def export_to_dataframe(self, transactions: List[SyntheticTransaction]):
        """Export transactions to pandas DataFrame"""
        import pandas as pd
        
        records = [txn.to_dict() for txn in transactions]
        df = pd.DataFrame(records)
        
        return df
    
    def export_to_json(self, transactions: List[SyntheticTransaction], filepath: str):
        """Export transactions to JSON file"""
        records = [txn.to_dict() for txn in transactions]
        
        with open(filepath, 'w') as f:
            json.dump(records, f, indent=2, default=str)
            
        print(f"Exported {len(transactions)} transactions to {filepath}")
```

---

## 10. Testing Scenarios and Validation

### 10.1 Common Fraud Scenarios

```python
class FraudScenarioGenerator:
    """Generate specific fraud scenarios for testing"""
    
    @staticmethod
    def card_testing_attack(num_transactions: int = 100) -> List[SyntheticTransaction]:
        """
        Generate card testing attack scenario.
        
        Pattern: 
        - Many small transactions
        - High failure rate
        - Sequential card numbers
        - Same IP/device
        """
        generator = SyntheticDatasetGenerator(fraud_rate=1.0)
        transactions = []
        
        # Generate shared device and network for attack
        device_gen = DeviceFingerprintGenerator(fraud_mode=True)
        shared_device = device_gen.generate()
        
        network_gen = NetworkIntelligenceGenerator(fraud_mode=True)
        shared_network = network_gen.generate()
        
        for i in range(num_transactions):
            txn = generator._generate_transaction(is_fraud=True, fraud_type="card_testing")
            
            # Override with shared device/network
            txn.device = shared_device
            txn.network = shared_network
            
            # Small test amounts
            txn.transaction.amount = random.choice([0.50, 1.00, 1.50, 2.00])
            
            # High velocity
            txn.velocity.cards_per_email_hourly = 50
            txn.velocity.is_card_testing_pattern = True
            
            transactions.append(txn)
            
        return transactions
    
    @staticmethod
    def account_takeover_attack() -> List[SyntheticTransaction]:
        """
        Generate account takeover scenario.
        
        Pattern:
        - Legitimate account history
        - Sudden behavior change
        - New device
        - Different location
        """
        transactions = []
        
        # First: Historical legitimate transactions
        legit_gen = SyntheticDatasetGenerator(fraud_rate=0.0)
        for _ in range(10):
            txn = legit_gen._generate_transaction(is_fraud=False)
            txn.timestamp = datetime.now() - timedelta(days=random.randint(30, 365))
            transactions.append(txn)
            
        # Then: ATO attack
        fraud_gen = SyntheticDatasetGenerator(fraud_rate=1.0)
        for _ in range(5):
            txn = fraud_gen._generate_transaction(is_fraud=True, fraud_type="account_takeover")
            
            # Use same card as legitimate transactions
            txn.card = transactions[0].card
            
            # But different device and location
            txn.device.is_bot = False  # Trying to look legitimate
            txn.network.geolocation.country_code = "RU"  # Different country
            txn.network.card_country_match = False
            
            # Higher amounts
            txn.transaction.amount *= 5
            
            txn.timestamp = datetime.now() - timedelta(hours=random.randint(1, 24))
            transactions.append(txn)
            
        return transactions
    
    @staticmethod
    def friendly_fraud_scenario() -> List[SyntheticTransaction]:
        """
        Generate friendly fraud scenario.
        
        Pattern:
        - Completely legitimate-looking transaction
        - Later disputed as fraud
        """
        transactions = []
        
        generator = SyntheticDatasetGenerator(fraud_rate=0.0)
        
        for _ in range(5):
            txn = generator._generate_transaction(is_fraud=False)
            
            # Mark as fraud retrospectively
            txn.is_fraud = True
            txn.fraud_type = "friendly_fraud"
            
            # All signals look legitimate
            txn.network_wide.has_tc40_report = False
            txn.network_wide.has_early_fraud_warning = False
            
            transactions.append(txn)
            
        return transactions

# Example usage
if __name__ == "__main__":
    # Generate a complete dataset
    generator = SyntheticDatasetGenerator(fraud_rate=0.01)  # 1% fraud rate
    
    # Generate 10,000 transactions
    transactions = generator.generate_dataset(
        num_transactions=10000,
        include_edge_cases=True
    )
    
    # Export to DataFrame
    df = generator.export_to_dataframe(transactions)
    print(f"Generated dataset shape: {df.shape}")
    print(f"Fraud rate: {df['is_fraud'].mean():.2%}")
    print(f"\nFraud type distribution:")
    print(df[df['is_fraud']]['fraud_type'].value_counts())
    
    # Export to JSON
    generator.export_to_json(transactions[:100], "sample_transactions.json")
    
    # Generate specific scenarios
    card_testing = FraudScenarioGenerator.card_testing_attack(100)
    ato_scenario = FraudScenarioGenerator.account_takeover_attack()
    friendly_fraud = FraudScenarioGenerator.friendly_fraud_scenario()
    
    print(f"\nGenerated {len(card_testing)} card testing transactions")
    print(f"Generated {len(ato_scenario)} ATO scenario transactions")
    print(f"Generated {len(friendly_fraud)} friendly fraud transactions")
```

### 10.2 Validation and Quality Checks

```python
class DatasetValidator:
    """Validate synthetic dataset quality"""
    
    @staticmethod
    def validate_distributions(df) -> Dict[str, Any]:
        """Check that distributions match expected patterns"""
        validations = {}
        
        # Fraud rate check
        fraud_rate = df['is_fraud'].mean()
        validations['fraud_rate'] = {
            'value': fraud_rate,
            'expected_range': (0.005, 0.05),
            'passed': 0.005 <= fraud_rate <= 0.05
        }
        
        # Card brand distribution
        brand_dist = df['card_brand'].value_counts(normalize=True)
        validations['visa_share'] = {
            'value': brand_dist.get('visa', 0),
            'expected_range': (0.4, 0.6),
            'passed': 0.4 <= brand_dist.get('visa', 0) <= 0.6
        }
        
        # Risk score distribution
        avg_fraud_risk = df[df['is_fraud']]['total_risk_score'].mean()
        avg_legit_risk = df[~df['is_fraud']]['total_risk_score'].mean()
        
        validations['risk_separation'] = {
            'fraud_avg': avg_fraud_risk,
            'legit_avg': avg_legit_risk,
            'separation': avg_fraud_risk - avg_legit_risk,
            'passed': avg_fraud_risk > avg_legit_risk + 20
        }
        
        return validations
    
    @staticmethod
    def check_feature_correlations(df) -> Dict[str, float]:
        """Check correlations between features and fraud label"""
        import pandas as pd
        
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        correlations = {}
        
        for col in numeric_cols:
            if col != 'is_fraud':
                corr = df[col].corr(df['is_fraud'].astype(int))
                correlations[col] = corr
                
        # Sort by absolute correlation
        sorted_corrs = dict(sorted(
            correlations.items(), 
            key=lambda x: abs(x[1]), 
            reverse=True
        ))
        
        return sorted_corrs
```

---

## References

1. **Stripe Documentation**: https://docs.stripe.com/testing
2. **Stripe Radar Documentation**: https://docs.stripe.com/radar
3. **Stripe Engineering Blog**: "How we built it: Stripe Radar" (March 2023)
4. **Stripe Sessions 2024**: "A Blueprint for AI Acceleration"
5. **Stripe Sessions 2025**: Payments Foundation Model Announcement
6. **Card Network Standards**: Visa TC40, Mastercard SAFE specifications
7. **Industry Standards**: PCI DSS, EMV 3-D Secure specifications

---

## Appendix: Stripe Test Card Reference

### Success Cards
| Card Number | Brand | Type |
|-------------|-------|------|
| 4242424242424242 | Visa | Credit |
| 5555555555554444 | Mastercard | Credit |
| 378282246310005 | Amex | Credit |
| 6011111111111117 | Discover | Credit |

### Fraud Testing Cards
| Card Number | Scenario |
|-------------|----------|
| 4100000000000019 | Always blocked (highest risk) |
| 4000000000004954 | Highest risk level |
| 4000000000009235 | Elevated risk level |
| 4000000000000101 | CVC check fails |
| 4000000000000036 | Postal code check fails |

### Decline Cards
| Card Number | Decline Reason |
|-------------|----------------|
| 4000000000000002 | Generic decline |
| 4000000000009995 | Insufficient funds |
| 4000000000009987 | Lost card |
| 4000000000009979 | Stolen card |

### Dispute Cards
| Card Number | Dispute Type |
|-------------|--------------|
| 4000000000000259 | Fraudulent dispute |
| 4000000000002685 | Product not received |
| 4000000000005423 | Early fraud warning |

---

*Document Version: 1.0*
*Generated: December 2025*
*Author: AI Research Assistant*
