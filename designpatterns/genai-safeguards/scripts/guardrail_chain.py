#!/usr/bin/env python3
"""
Guardrail Chain - Composable safeguard framework for LLM applications.
Framework-agnostic, invokable by any agent.

Provides input/output protection for:
- PII detection and redaction
- Prompt injection detection
- Toxicity filtering
- Banned topic enforcement
- Content grounding validation

Usage:
    from guardrail_chain import GuardrailChain, PIIGuardrail, PromptInjectionGuardrail
    
    chain = GuardrailChain([
        PIIGuardrail(redact=True),
        PromptInjectionGuardrail(threshold=0.5),
    ])
    result = chain.execute(user_input)
"""

import re
import json
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional, Callable, Union
from enum import Enum


# ============================================================================
# Core Data Models
# ============================================================================

class GuardrailAction(Enum):
    """Action to take based on guardrail evaluation."""
    ALLOW = "allow"           # Pass through unchanged
    SANITIZE = "sanitize"     # Modify and pass
    BLOCK = "block"           # Stop processing
    FLAG = "flag"             # Allow but flag for review


class GuardrailSeverity(Enum):
    """Severity of guardrail trigger."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class GuardrailResult:
    """Result of a single guardrail evaluation."""
    guardrail_name: str
    action: GuardrailAction
    triggered: bool
    severity: GuardrailSeverity = GuardrailSeverity.LOW
    original_input: Any = None
    sanitized_output: Any = None
    details: Dict[str, Any] = field(default_factory=dict)
    risk_score: float = 0.0
    processing_time_ms: float = 0.0
    
    def to_dict(self) -> dict:
        return {
            "guardrail": self.guardrail_name,
            "action": self.action.value,
            "triggered": self.triggered,
            "severity": self.severity.value,
            "risk_score": self.risk_score,
            "details": self.details,
            "processing_time_ms": self.processing_time_ms
        }


@dataclass
class ChainResult:
    """Result of executing a guardrail chain."""
    action: str  # "allowed", "blocked", "sanitized"
    final_output: Any
    triggered_guardrails: List[str]
    all_results: List[GuardrailResult]
    flags: List[GuardrailResult]
    blocked_by: Optional[str] = None
    total_risk_score: float = 0.0
    total_processing_time_ms: float = 0.0
    
    def to_dict(self) -> dict:
        return {
            "action": self.action,
            "triggered_guardrails": self.triggered_guardrails,
            "blocked_by": self.blocked_by,
            "total_risk_score": self.total_risk_score,
            "total_processing_time_ms": self.total_processing_time_ms,
            "results": [r.to_dict() for r in self.all_results],
            "flags": [f.to_dict() for f in self.flags]
        }


# ============================================================================
# Base Guardrail Interface
# ============================================================================

class Guardrail(ABC):
    """Base class for all guardrails."""
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Unique identifier for this guardrail."""
        pass
    
    @abstractmethod
    def scan(self, input_data: Any) -> GuardrailResult:
        """Evaluate input against this guardrail."""
        pass
    
    def __repr__(self):
        return f"<{self.__class__.__name__}: {self.name}>"


# ============================================================================
# Input Guardrails
# ============================================================================

class PIIGuardrail(Guardrail):
    """
    Detect and optionally redact Personally Identifiable Information.
    
    Detects: SSN, credit cards, emails, phone numbers, IP addresses
    """
    
    name = "pii_detection"
    
    # Standard PII patterns
    PATTERNS = {
        "ssn": {
            "pattern": r"\b\d{3}-\d{2}-\d{4}\b",
            "severity": GuardrailSeverity.CRITICAL,
            "description": "Social Security Number"
        },
        "credit_card": {
            "pattern": r"\b(?:\d{4}[\s-]?){3}\d{4}\b",
            "severity": GuardrailSeverity.CRITICAL,
            "description": "Credit Card Number"
        },
        "email": {
            "pattern": r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
            "severity": GuardrailSeverity.MEDIUM,
            "description": "Email Address"
        },
        "phone": {
            "pattern": r"\b(?:\+1[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b",
            "severity": GuardrailSeverity.MEDIUM,
            "description": "Phone Number"
        },
        "ip_address": {
            "pattern": r"\b(?:\d{1,3}\.){3}\d{1,3}\b",
            "severity": GuardrailSeverity.LOW,
            "description": "IP Address"
        },
        "date_of_birth": {
            "pattern": r"\b(?:0?[1-9]|1[0-2])[/-](?:0?[1-9]|[12]\d|3[01])[/-](?:19|20)\d{2}\b",
            "severity": GuardrailSeverity.MEDIUM,
            "description": "Date of Birth"
        }
    }
    
    def __init__(
        self,
        redact: bool = True,
        block_on: Optional[List[str]] = None,
        custom_patterns: Optional[Dict[str, dict]] = None
    ):
        """
        Args:
            redact: If True, replace detected PII with [REDACTED_TYPE]
            block_on: List of PII types that should block (default: ssn, credit_card)
            custom_patterns: Additional patterns to detect
        """
        self.redact = redact
        self.block_on = block_on or ["ssn", "credit_card"]
        self.patterns = {**self.PATTERNS}
        if custom_patterns:
            self.patterns.update(custom_patterns)
    
    def scan(self, input_data: str) -> GuardrailResult:
        import time
        start = time.time()
        
        detected = {}
        sanitized = input_data
        max_severity = GuardrailSeverity.LOW
        
        for pii_type, config in self.patterns.items():
            matches = re.findall(config["pattern"], input_data)
            if matches:
                detected[pii_type] = {
                    "count": len(matches),
                    "description": config["description"]
                }
                
                # Track highest severity
                if config["severity"].value > max_severity.value:
                    max_severity = config["severity"]
                
                if self.redact:
                    sanitized = re.sub(
                        config["pattern"],
                        f"[REDACTED_{pii_type.upper()}]",
                        sanitized
                    )
        
        # Determine action
        blocked_types = [t for t in detected.keys() if t in self.block_on]
        
        if blocked_types:
            action = GuardrailAction.BLOCK
        elif detected and self.redact:
            action = GuardrailAction.SANITIZE
        elif detected:
            action = GuardrailAction.FLAG
        else:
            action = GuardrailAction.ALLOW
        
        processing_time = (time.time() - start) * 1000
        
        return GuardrailResult(
            guardrail_name=self.name,
            action=action,
            triggered=bool(detected),
            severity=max_severity,
            original_input=input_data,
            sanitized_output=sanitized,
            details={
                "detected_pii": detected,
                "blocked_types": blocked_types
            },
            risk_score=min(1.0, len(detected) * 0.25),
            processing_time_ms=processing_time
        )


class PromptInjectionGuardrail(Guardrail):
    """
    Detect prompt injection attempts.
    
    Catches: instruction override, role hijacking, delimiter injection
    """
    
    name = "prompt_injection"
    
    # Injection patterns with severity
    INJECTION_PATTERNS = [
        # Instruction override
        (r"ignore\s+(previous|above|all|prior|earlier)\s+(instructions?|prompts?|rules?)", GuardrailSeverity.HIGH),
        (r"disregard\s+(previous|above|all|prior|everything)", GuardrailSeverity.HIGH),
        (r"forget\s+(everything|what|your|all)", GuardrailSeverity.HIGH),
        (r"override\s+(previous|system|your)", GuardrailSeverity.HIGH),
        
        # Role hijacking
        (r"you\s+are\s+now\s+(a|an|the)", GuardrailSeverity.MEDIUM),
        (r"pretend\s+(to\s+be|you\s+are)", GuardrailSeverity.MEDIUM),
        (r"act\s+as\s+(if|a|an)", GuardrailSeverity.MEDIUM),
        (r"new\s+(persona|identity|role)", GuardrailSeverity.MEDIUM),
        
        # System prompt extraction
        (r"(show|reveal|display|print)\s+(me\s+)?(your|the|system)\s+(prompt|instructions)", GuardrailSeverity.MEDIUM),
        (r"what\s+(are|is)\s+your\s+(system|initial)\s+(prompt|instructions)", GuardrailSeverity.LOW),
        
        # Delimiter injection
        (r"<\|.*?\|>", GuardrailSeverity.HIGH),  # Special tokens
        (r"\[INST\]|\[/INST\]", GuardrailSeverity.HIGH),  # Llama format
        (r"Human:|Assistant:|System:", GuardrailSeverity.MEDIUM),  # Chat format
        (r"###\s*(Instruction|Response|System)", GuardrailSeverity.MEDIUM),
        
        # Code injection attempts
        (r"```(system|assistant|instruction)", GuardrailSeverity.MEDIUM),
        (r"<\/?(?:system|assistant|user)>", GuardrailSeverity.HIGH),
    ]
    
    def __init__(
        self,
        threshold: float = 0.5,
        custom_patterns: Optional[List[tuple]] = None
    ):
        """
        Args:
            threshold: Risk score threshold for blocking (0.0-1.0)
            custom_patterns: Additional (pattern, severity) tuples
        """
        self.threshold = threshold
        self.patterns = list(self.INJECTION_PATTERNS)
        if custom_patterns:
            self.patterns.extend(custom_patterns)
        
        # Compile patterns
        self._compiled = [
            (re.compile(p, re.IGNORECASE), s)
            for p, s in self.patterns
        ]
    
    def scan(self, input_data: str) -> GuardrailResult:
        import time
        start = time.time()
        
        matches = []
        max_severity = GuardrailSeverity.LOW
        
        for pattern, severity in self._compiled:
            found = pattern.findall(input_data)
            if found:
                matches.append({
                    "pattern": pattern.pattern,
                    "matches": found if isinstance(found[0], str) else [str(f) for f in found],
                    "severity": severity.value
                })
                if severity.value > max_severity.value:
                    max_severity = severity
        
        # Calculate risk score based on matches and severity
        risk_score = 0.0
        for match in matches:
            severity_weight = {
                "low": 0.1, "medium": 0.25, "high": 0.4, "critical": 0.5
            }
            risk_score += severity_weight.get(match["severity"], 0.1) * len(match["matches"])
        risk_score = min(1.0, risk_score)
        
        action = GuardrailAction.BLOCK if risk_score >= self.threshold else GuardrailAction.ALLOW
        if matches and action == GuardrailAction.ALLOW:
            action = GuardrailAction.FLAG
        
        processing_time = (time.time() - start) * 1000
        
        return GuardrailResult(
            guardrail_name=self.name,
            action=action,
            triggered=bool(matches),
            severity=max_severity,
            original_input=input_data,
            sanitized_output=input_data,  # Don't modify, just detect
            details={"matched_patterns": matches},
            risk_score=risk_score,
            processing_time_ms=processing_time
        )


class BannedTopicsGuardrail(Guardrail):
    """
    Block queries on banned topics using keyword matching or LLM classification.
    """
    
    name = "banned_topics"
    
    def __init__(
        self,
        topics: List[str],
        keywords: Optional[Dict[str, List[str]]] = None,
        llm_client=None,
        use_llm: bool = False
    ):
        """
        Args:
            topics: List of banned topic names
            keywords: Optional keyword lists per topic for fast matching
            llm_client: LLM client for classification (required if use_llm=True)
            use_llm: Use LLM for topic detection (slower but more accurate)
        """
        self.topics = topics
        self.keywords = keywords or {}
        self.llm = llm_client
        self.use_llm = use_llm and llm_client is not None
    
    def scan(self, input_data: str) -> GuardrailResult:
        import time
        start = time.time()
        
        if self.use_llm:
            result = self._llm_classification(input_data)
        else:
            result = self._keyword_matching(input_data)
        
        result.processing_time_ms = (time.time() - start) * 1000
        return result
    
    def _keyword_matching(self, input_data: str) -> GuardrailResult:
        """Fast keyword-based topic detection."""
        input_lower = input_data.lower()
        matched_topics = []
        
        for topic in self.topics:
            # Check topic name directly
            if topic.lower() in input_lower:
                matched_topics.append(topic)
                continue
            
            # Check keywords for topic
            topic_keywords = self.keywords.get(topic, [])
            for keyword in topic_keywords:
                if keyword.lower() in input_lower:
                    matched_topics.append(topic)
                    break
        
        is_banned = len(matched_topics) > 0
        
        return GuardrailResult(
            guardrail_name=self.name,
            action=GuardrailAction.BLOCK if is_banned else GuardrailAction.ALLOW,
            triggered=is_banned,
            severity=GuardrailSeverity.HIGH if is_banned else GuardrailSeverity.LOW,
            original_input=input_data,
            sanitized_output=input_data,
            details={
                "matched_topics": matched_topics,
                "method": "keyword"
            },
            risk_score=1.0 if is_banned else 0.0
        )
    
    def _llm_classification(self, input_data: str) -> GuardrailResult:
        """LLM-based topic classification."""
        prompt = f"""
Analyze if this text discusses any of these banned topics: {self.topics}

Text: {input_data}

Respond with ONLY a JSON object:
{{"is_banned": true/false, "matched_topics": ["topic1", "topic2"], "confidence": 0.0-1.0}}
"""
        
        try:
            response = self.llm.complete(prompt, temperature=0)
            # Parse JSON from response
            json_match = re.search(r'\{[^{}]*\}', response)
            if json_match:
                result = json.loads(json_match.group())
            else:
                result = {"is_banned": False, "matched_topics": [], "confidence": 0.0}
        except Exception as e:
            # Fallback to keyword matching on error
            return self._keyword_matching(input_data)
        
        is_banned = result.get("is_banned", False)
        
        return GuardrailResult(
            guardrail_name=self.name,
            action=GuardrailAction.BLOCK if is_banned else GuardrailAction.ALLOW,
            triggered=is_banned,
            severity=GuardrailSeverity.HIGH if is_banned else GuardrailSeverity.LOW,
            original_input=input_data,
            sanitized_output=input_data,
            details={
                "matched_topics": result.get("matched_topics", []),
                "confidence": result.get("confidence", 0.0),
                "method": "llm"
            },
            risk_score=result.get("confidence", 0.0) if is_banned else 0.0
        )


class ToxicityGuardrail(Guardrail):
    """
    Filter toxic or harmful content.
    
    Can use keyword matching or ML classifier.
    """
    
    name = "toxicity"
    
    # Basic toxic keyword patterns
    TOXIC_PATTERNS = [
        r"\b(kill|murder|harm)\s+(yourself|yourself|them|him|her)\b",
        r"\b(hate|despise)\s+(you|them|all)\b",
        # Add more patterns as needed
    ]
    
    def __init__(
        self,
        threshold: float = 0.5,
        use_ml: bool = False,
        model_name: str = "unitary/unbiased-toxic-roberta"
    ):
        """
        Args:
            threshold: Score threshold for blocking
            use_ml: Use ML classifier (requires transformers)
            model_name: HuggingFace model for classification
        """
        self.threshold = threshold
        self.use_ml = use_ml
        self.model_name = model_name
        self._classifier = None
        
        if use_ml:
            self._init_classifier()
    
    def _init_classifier(self):
        try:
            from transformers import pipeline
            self._classifier = pipeline("text-classification", model=self.model_name)
        except ImportError:
            self.use_ml = False
    
    def scan(self, input_data: str) -> GuardrailResult:
        import time
        start = time.time()
        
        if self.use_ml and self._classifier:
            result = self._ml_classification(input_data)
        else:
            result = self._pattern_matching(input_data)
        
        result.processing_time_ms = (time.time() - start) * 1000
        return result
    
    def _pattern_matching(self, input_data: str) -> GuardrailResult:
        """Simple pattern-based toxicity detection."""
        matches = []
        for pattern in self.TOXIC_PATTERNS:
            found = re.findall(pattern, input_data, re.IGNORECASE)
            if found:
                matches.extend(found)
        
        is_toxic = len(matches) > 0
        risk_score = min(1.0, len(matches) * 0.3)
        
        return GuardrailResult(
            guardrail_name=self.name,
            action=GuardrailAction.BLOCK if risk_score >= self.threshold else GuardrailAction.ALLOW,
            triggered=is_toxic,
            severity=GuardrailSeverity.HIGH if is_toxic else GuardrailSeverity.LOW,
            original_input=input_data,
            sanitized_output=input_data,
            details={"matched_patterns": matches, "method": "pattern"},
            risk_score=risk_score
        )
    
    def _ml_classification(self, input_data: str) -> GuardrailResult:
        """ML-based toxicity classification."""
        result = self._classifier(input_data[:512])[0]  # Truncate for model
        
        is_toxic = result["label"] == "toxic" and result["score"] > self.threshold
        
        return GuardrailResult(
            guardrail_name=self.name,
            action=GuardrailAction.BLOCK if is_toxic else GuardrailAction.ALLOW,
            triggered=is_toxic,
            severity=GuardrailSeverity.HIGH if is_toxic else GuardrailSeverity.LOW,
            original_input=input_data,
            sanitized_output=input_data,
            details={"label": result["label"], "score": result["score"], "method": "ml"},
            risk_score=result["score"] if result["label"] == "toxic" else 0.0
        )


# ============================================================================
# Output Guardrails
# ============================================================================

class GroundingGuardrail(Guardrail):
    """
    Verify output is grounded in provided context.
    Useful for RAG applications.
    """
    
    name = "factual_grounding"
    
    def __init__(self, llm_client):
        """
        Args:
            llm_client: LLM client for grounding verification
        """
        self.llm = llm_client
    
    def scan(self, input_data: Dict[str, str]) -> GuardrailResult:
        """
        Verify grounding.
        
        Args:
            input_data: {"context": "source text", "response": "LLM response"}
        """
        import time
        start = time.time()
        
        context = input_data.get("context", "")
        response = input_data.get("response", "")
        
        prompt = f"""
Compare the response to the source context.
Identify any claims in the response NOT supported by the context.

Context:
{context}

Response:
{response}

Return ONLY a JSON object:
{{"is_grounded": true/false, "unsupported_claims": ["claim1", "claim2"], "confidence": 0.0-1.0}}
"""
        
        try:
            llm_response = self.llm.complete(prompt, temperature=0)
            json_match = re.search(r'\{[^{}]*\}', llm_response, re.DOTALL)
            if json_match:
                result = json.loads(json_match.group())
            else:
                result = {"is_grounded": True, "unsupported_claims": [], "confidence": 0.5}
        except Exception:
            result = {"is_grounded": True, "unsupported_claims": [], "confidence": 0.0}
        
        is_grounded = result.get("is_grounded", True)
        processing_time = (time.time() - start) * 1000
        
        return GuardrailResult(
            guardrail_name=self.name,
            action=GuardrailAction.FLAG if not is_grounded else GuardrailAction.ALLOW,
            triggered=not is_grounded,
            severity=GuardrailSeverity.MEDIUM if not is_grounded else GuardrailSeverity.LOW,
            original_input=input_data,
            sanitized_output=input_data,
            details={
                "unsupported_claims": result.get("unsupported_claims", []),
                "confidence": result.get("confidence", 0.0)
            },
            risk_score=1.0 - result.get("confidence", 0.0) if not is_grounded else 0.0,
            processing_time_ms=processing_time
        )


# ============================================================================
# Guardrail Chain
# ============================================================================

class GuardrailChain:
    """
    Execute multiple guardrails in sequence.
    
    Usage:
        chain = GuardrailChain([
            PIIGuardrail(redact=True),
            PromptInjectionGuardrail(threshold=0.5),
            BannedTopicsGuardrail(topics=["politics", "religion"])
        ])
        result = chain.execute(user_input)
        
        if result.action == "blocked":
            return f"Blocked by {result.blocked_by}"
        else:
            proceed_with(result.final_output)
    """
    
    def __init__(
        self,
        guardrails: List[Guardrail],
        fail_fast: bool = True
    ):
        """
        Args:
            guardrails: List of guardrails to execute in order
            fail_fast: If True, stop on first BLOCK action
        """
        self.guardrails = guardrails
        self.fail_fast = fail_fast
    
    def execute(self, input_data: Any) -> ChainResult:
        """Execute all guardrails on input."""
        current = input_data
        results = []
        triggered = []
        flags = []
        blocked_by = None
        total_risk = 0.0
        total_time = 0.0
        
        for guardrail in self.guardrails:
            result = guardrail.scan(current)
            results.append(result)
            total_risk += result.risk_score
            total_time += result.processing_time_ms
            
            if result.triggered:
                triggered.append(guardrail.name)
            
            if result.action == GuardrailAction.BLOCK:
                blocked_by = guardrail.name
                if self.fail_fast:
                    break
            elif result.action == GuardrailAction.FLAG:
                flags.append(result)
            elif result.action == GuardrailAction.SANITIZE:
                current = result.sanitized_output
        
        # Determine overall action
        if blocked_by:
            action = "blocked"
        elif any(r.action == GuardrailAction.SANITIZE for r in results):
            action = "sanitized"
        else:
            action = "allowed"
        
        return ChainResult(
            action=action,
            final_output=current if action != "blocked" else None,
            triggered_guardrails=triggered,
            all_results=results,
            flags=flags,
            blocked_by=blocked_by,
            total_risk_score=min(1.0, total_risk),
            total_processing_time_ms=total_time
        )
    
    def add(self, guardrail: Guardrail) -> "GuardrailChain":
        """Add a guardrail to the chain."""
        self.guardrails.append(guardrail)
        return self
    
    def remove(self, name: str) -> "GuardrailChain":
        """Remove a guardrail by name."""
        self.guardrails = [g for g in self.guardrails if g.name != name]
        return self


# ============================================================================
# Preset Chains
# ============================================================================

def create_input_chain(
    llm_client=None,
    banned_topics: Optional[List[str]] = None
) -> GuardrailChain:
    """Create a standard input guardrail chain."""
    guardrails = [
        PIIGuardrail(redact=True, block_on=["ssn", "credit_card"]),
        PromptInjectionGuardrail(threshold=0.5),
    ]
    
    if banned_topics:
        guardrails.append(BannedTopicsGuardrail(
            topics=banned_topics,
            llm_client=llm_client,
            use_llm=llm_client is not None
        ))
    
    return GuardrailChain(guardrails)


def create_output_chain(llm_client=None) -> GuardrailChain:
    """Create a standard output guardrail chain."""
    guardrails = [
        PIIGuardrail(redact=True),  # Redact any PII in output
        ToxicityGuardrail(threshold=0.7),
    ]
    
    return GuardrailChain(guardrails)


def create_rag_chain(
    llm_client,
    banned_topics: Optional[List[str]] = None
) -> Dict[str, GuardrailChain]:
    """Create input and output chains for RAG applications."""
    return {
        "input": create_input_chain(llm_client, banned_topics),
        "output": create_output_chain(llm_client)
    }


# ============================================================================
# Convenience Functions
# ============================================================================

def quick_scan(
    input_data: str,
    check_pii: bool = True,
    check_injection: bool = True,
    check_toxicity: bool = False
) -> Dict[str, Any]:
    """
    Quick scan without full chain setup.
    
    Usage:
        result = quick_scan("user input here")
        if result["is_safe"]:
            proceed()
    """
    guardrails = []
    if check_pii:
        guardrails.append(PIIGuardrail(redact=False))
    if check_injection:
        guardrails.append(PromptInjectionGuardrail())
    if check_toxicity:
        guardrails.append(ToxicityGuardrail())
    
    chain = GuardrailChain(guardrails)
    result = chain.execute(input_data)
    
    return {
        "is_safe": result.action == "allowed",
        "action": result.action,
        "triggered": result.triggered_guardrails,
        "risk_score": result.total_risk_score,
        "details": [r.details for r in result.all_results if r.triggered]
    }


if __name__ == "__main__":
    print("Guardrail Chain initialized.")
    print("Use GuardrailChain([...]).execute(input) or quick_scan(input)")
