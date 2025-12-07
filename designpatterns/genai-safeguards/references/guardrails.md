# Guardrails (Pattern 32)

Layers of protection code around LLM inputs, outputs, retrieved context, and tool parameters. Catchall pattern for security, privacy, content moderation, and alignment.

## When to Use

- Application is exposed to untrusted inputs (public-facing)
- PII or sensitive data flows through the system
- Regulatory compliance required (HIPAA, GDPR, PCI-DSS, SOX)
- Brand/reputation risk from inappropriate outputs
- Adversarial attacks are a concern (prompt injection, jailbreaking)

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         USER INPUT                              │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│               INPUT GUARDRAILS                                  │
│  [PII Detection] [Injection Detection] [Toxicity] [Banned Topics]│
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│               RETRIEVAL GUARDRAILS                              │
│  [Relevance Filter] [Source Validation] [Conflict Detection]    │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                    LLM / AGENT CORE                             │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│               TOOL GUARDRAILS                                   │
│  [Parameter Validation] [Permission Check] [Rate Limiting]      │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│               OUTPUT GUARDRAILS                                 │
│  [PII Redaction] [Toxicity] [Factual Grounding] [Brand Alignment]│
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                         USER OUTPUT                             │
└─────────────────────────────────────────────────────────────────┘
```

## Implementation

### Core Guardrail Interface

```python
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Optional, List
from enum import Enum

class GuardrailAction(Enum):
    ALLOW = "allow"           # Pass through unchanged
    SANITIZE = "sanitize"     # Modify and pass
    BLOCK = "block"           # Stop processing
    FLAG = "flag"             # Allow but flag for review

@dataclass
class GuardrailResult:
    action: GuardrailAction
    original_input: Any
    sanitized_output: Any
    triggered: bool
    guardrail_type: str
    details: Optional[dict] = None
    risk_score: float = 0.0

class Guardrail(ABC):
    """Base class for all guardrails."""
    
    @property
    @abstractmethod
    def name(self) -> str:
        pass
    
    @abstractmethod
    def scan(self, input_data: Any) -> GuardrailResult:
        pass

class GuardrailChain:
    """Execute multiple guardrails in sequence."""
    
    def __init__(self, guardrails: List[Guardrail]):
        self.guardrails = guardrails
    
    def execute(self, input_data: Any) -> dict:
        current = input_data
        results = []
        
        for guardrail in self.guardrails:
            result = guardrail.scan(current)
            results.append(result)
            
            if result.action == GuardrailAction.BLOCK:
                return {
                    "action": "blocked",
                    "blocked_by": guardrail.name,
                    "results": results,
                    "final_output": None
                }
            
            current = result.sanitized_output
        
        return {
            "action": "allowed",
            "results": results,
            "final_output": current,
            "flags": [r for r in results if r.action == GuardrailAction.FLAG]
        }
```

### Input Guardrails

#### PII Detection

```python
import re
from typing import Dict, List

class PIIGuardrail(Guardrail):
    """Detect and optionally redact PII."""
    
    name = "pii_detection"
    
    # Patterns for common PII types
    PATTERNS = {
        "ssn": r"\b\d{3}-\d{2}-\d{4}\b",
        "credit_card": r"\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b",
        "email": r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
        "phone": r"\b\d{3}[-.]?\d{3}[-.]?\d{4}\b",
        "ip_address": r"\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b",
    }
    
    def __init__(self, redact: bool = True, block_on: List[str] = None):
        self.redact = redact
        self.block_on = block_on or ["ssn", "credit_card"]
    
    def scan(self, input_data: str) -> GuardrailResult:
        detected = {}
        sanitized = input_data
        
        for pii_type, pattern in self.PATTERNS.items():
            matches = re.findall(pattern, input_data)
            if matches:
                detected[pii_type] = len(matches)
                if self.redact:
                    sanitized = re.sub(pattern, f"[REDACTED_{pii_type.upper()}]", sanitized)
        
        # Determine action
        blocked_types = [t for t in detected.keys() if t in self.block_on]
        
        if blocked_types:
            action = GuardrailAction.BLOCK
        elif detected:
            action = GuardrailAction.SANITIZE if self.redact else GuardrailAction.FLAG
        else:
            action = GuardrailAction.ALLOW
        
        return GuardrailResult(
            action=action,
            original_input=input_data,
            sanitized_output=sanitized,
            triggered=bool(detected),
            guardrail_type=self.name,
            details={"detected_pii": detected},
            risk_score=len(detected) * 0.2
        )
```

#### Prompt Injection Detection

```python
class PromptInjectionGuardrail(Guardrail):
    """Detect prompt injection attempts."""
    
    name = "prompt_injection"
    
    INJECTION_PATTERNS = [
        r"ignore\s+(previous|above|all)\s+instructions",
        r"disregard\s+(previous|above|all)",
        r"forget\s+(everything|what|your)",
        r"you\s+are\s+now\s+a",
        r"new\s+instructions?:",
        r"system\s*:\s*",
        r"<\|.*?\|>",  # Special tokens
        r"\[INST\]|\[/INST\]",  # Llama format
        r"Human:|Assistant:",  # Anthropic format
    ]
    
    def __init__(self, threshold: float = 0.5):
        self.threshold = threshold
        self._compiled = [re.compile(p, re.IGNORECASE) for p in self.INJECTION_PATTERNS]
    
    def scan(self, input_data: str) -> GuardrailResult:
        matches = []
        for i, pattern in enumerate(self._compiled):
            if pattern.search(input_data):
                matches.append(self.INJECTION_PATTERNS[i])
        
        risk_score = min(1.0, len(matches) * 0.3)
        
        return GuardrailResult(
            action=GuardrailAction.BLOCK if risk_score >= self.threshold else GuardrailAction.ALLOW,
            original_input=input_data,
            sanitized_output=input_data,
            triggered=bool(matches),
            guardrail_type=self.name,
            details={"matched_patterns": matches},
            risk_score=risk_score
        )
```

#### Banned Topics

```python
class BannedTopicsGuardrail(Guardrail):
    """Block queries on banned topics using LLM classification."""
    
    name = "banned_topics"
    
    def __init__(self, topics: List[str], llm_client):
        self.topics = topics
        self.llm = llm_client
    
    def scan(self, input_data: str) -> GuardrailResult:
        prompt = f"""
Analyze if this text touches on any of these banned topics: {self.topics}

Text: {input_data}

Respond with ONLY a JSON object:
{{"is_banned": true/false, "matched_topic": "topic_name or null", "confidence": 0.0-1.0}}
"""
        response = self.llm.complete(prompt, temperature=0)
        result = json.loads(response)
        
        return GuardrailResult(
            action=GuardrailAction.BLOCK if result["is_banned"] else GuardrailAction.ALLOW,
            original_input=input_data,
            sanitized_output=input_data,
            triggered=result["is_banned"],
            guardrail_type=self.name,
            details=result,
            risk_score=result.get("confidence", 0.0)
        )
```

### Output Guardrails

#### Factual Grounding Check

```python
class GroundingGuardrail(Guardrail):
    """Verify output is grounded in provided context."""
    
    name = "factual_grounding"
    
    def __init__(self, llm_client):
        self.llm = llm_client
    
    def scan(self, input_data: dict) -> GuardrailResult:
        """
        input_data should contain:
        - "context": The source material
        - "response": The LLM's response to verify
        """
        context = input_data.get("context", "")
        response = input_data.get("response", "")
        
        prompt = f"""
Compare the response to the source context.
Identify any claims in the response NOT supported by the context.

Context:
{context}

Response:
{response}

Return JSON:
{{"is_grounded": true/false, "unsupported_claims": ["claim1", "claim2"], "confidence": 0.0-1.0}}
"""
        result = json.loads(self.llm.complete(prompt, temperature=0))
        
        return GuardrailResult(
            action=GuardrailAction.FLAG if not result["is_grounded"] else GuardrailAction.ALLOW,
            original_input=input_data,
            sanitized_output=input_data,
            triggered=not result["is_grounded"],
            guardrail_type=self.name,
            details=result,
            risk_score=1.0 - result.get("confidence", 0.0)
        )
```

#### Toxicity Filter

```python
class ToxicityGuardrail(Guardrail):
    """Filter toxic or harmful content."""
    
    name = "toxicity"
    
    def __init__(self, model_path: str = "unitary/unbiased-toxic-roberta", threshold: float = 0.5):
        from transformers import pipeline
        self.classifier = pipeline("text-classification", model=model_path)
        self.threshold = threshold
    
    def scan(self, input_data: str) -> GuardrailResult:
        result = self.classifier(input_data)[0]
        
        is_toxic = result["label"] == "toxic" and result["score"] > self.threshold
        
        return GuardrailResult(
            action=GuardrailAction.BLOCK if is_toxic else GuardrailAction.ALLOW,
            original_input=input_data,
            sanitized_output=input_data,
            triggered=is_toxic,
            guardrail_type=self.name,
            details={"label": result["label"], "score": result["score"]},
            risk_score=result["score"] if result["label"] == "toxic" else 0.0
        )
```

### Tool Guardrails

```python
class ToolParameterGuardrail(Guardrail):
    """Validate tool parameters before execution."""
    
    name = "tool_parameters"
    
    def __init__(self, tool_policies: Dict[str, dict]):
        """
        tool_policies format:
        {
            "database_query": {
                "allowed_tables": ["products", "orders"],
                "blocked_operations": ["DELETE", "DROP", "TRUNCATE"]
            },
            "file_access": {
                "allowed_paths": ["/data/public/"],
                "blocked_extensions": [".exe", ".sh"]
            }
        }
        """
        self.policies = tool_policies
    
    def scan(self, input_data: dict) -> GuardrailResult:
        """
        input_data should contain:
        - "tool_name": Name of the tool
        - "parameters": Tool parameters to validate
        """
        tool_name = input_data.get("tool_name")
        params = input_data.get("parameters", {})
        
        policy = self.policies.get(tool_name)
        if not policy:
            return GuardrailResult(
                action=GuardrailAction.ALLOW,
                original_input=input_data,
                sanitized_output=input_data,
                triggered=False,
                guardrail_type=self.name
            )
        
        violations = self._check_policy(params, policy)
        
        return GuardrailResult(
            action=GuardrailAction.BLOCK if violations else GuardrailAction.ALLOW,
            original_input=input_data,
            sanitized_output=input_data,
            triggered=bool(violations),
            guardrail_type=self.name,
            details={"violations": violations},
            risk_score=len(violations) * 0.5
        )
    
    def _check_policy(self, params: dict, policy: dict) -> List[str]:
        violations = []
        
        # Check SQL operations
        if "blocked_operations" in policy:
            query = str(params.get("query", "")).upper()
            for op in policy["blocked_operations"]:
                if op in query:
                    violations.append(f"Blocked SQL operation: {op}")
        
        # Check file paths
        if "allowed_paths" in policy:
            path = params.get("path", "")
            if not any(path.startswith(p) for p in policy["allowed_paths"]):
                violations.append(f"Path not in allowed list: {path}")
        
        return violations
```

### Complete Pipeline Example

```python
def create_rag_guardrail_chain(llm_client) -> dict:
    """Create guardrail chains for a RAG application."""
    
    input_chain = GuardrailChain([
        PIIGuardrail(redact=True, block_on=["ssn", "credit_card"]),
        PromptInjectionGuardrail(threshold=0.5),
        BannedTopicsGuardrail(
            topics=["competitor pricing", "legal advice", "medical diagnosis"],
            llm_client=llm_client
        ),
    ])
    
    output_chain = GuardrailChain([
        PIIGuardrail(redact=True),  # Redact any PII in output
        ToxicityGuardrail(threshold=0.7),
    ])
    
    return {
        "input": input_chain,
        "output": output_chain
    }

# Usage in RAG pipeline
def guarded_rag_query(query: str, retriever, llm, guardrails: dict):
    # Input guardrails
    input_result = guardrails["input"].execute(query)
    if input_result["action"] == "blocked":
        return {"error": f"Query blocked by {input_result['blocked_by']}"}
    
    sanitized_query = input_result["final_output"]
    
    # RAG retrieval and generation
    chunks = retriever.retrieve(sanitized_query)
    response = llm.generate(chunks, sanitized_query)
    
    # Output guardrails
    output_result = guardrails["output"].execute(response)
    if output_result["action"] == "blocked":
        return {"error": "Response blocked by content filter"}
    
    return {
        "response": output_result["final_output"],
        "flags": output_result.get("flags", [])
    }
```

## Async Parallel Execution

For latency-sensitive applications, run guardrails in parallel:

```python
import asyncio

async def parallel_guardrails(input_data: str, llm_task, guardrails: GuardrailChain):
    """Run guardrails in parallel with LLM call."""
    
    async def run_guardrails():
        return guardrails.execute(input_data)
    
    try:
        guardrail_result, llm_result = await asyncio.gather(
            run_guardrails(),
            llm_task(input_data)
        )
        
        if guardrail_result["action"] == "blocked":
            raise GuardrailTriggered(guardrail_result["blocked_by"])
        
        return llm_result
        
    except GuardrailTriggered:
        # LLM result discarded
        raise
```

## Regulatory Compliance Mapping

| Regulation | Relevant Guardrails |
|------------|---------------------|
| GDPR | PII Detection, Data Retention |
| HIPAA | PHI Detection, Access Logging |
| PCI-DSS | Credit Card Detection, Encryption |
| SOX | Audit Logging, Access Control |
| FFIEC | Financial Data Protection |

## Performance Considerations

| Guardrail Type | Latency | When to Use |
|---------------|---------|-------------|
| Regex-based | < 1ms | Always (PII patterns) |
| SLM classifier | 10-50ms | High-risk inputs |
| LLM-as-Judge | 100-500ms | Complex decisions |

Recommendation: Layer guardrails from fast → slow, exit early on blocks.
