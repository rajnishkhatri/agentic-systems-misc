# Self-Check (Pattern 31)

Use token probabilities (logprobs) to detect potential hallucinations and assign confidence scores to LLM outputs.

## When to Use

- Factual accuracy is critical (finance, healthcare, legal)
- Structured data extraction from documents
- RAG systems with potentially conflicting chunks
- Any pipeline where hallucination cost > confidence-check cost

## Core Insight

LLMs emit lower probability tokens when "guessing" vs when "knowing". This signal can identify potential hallucinations without external validation.

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    LLM Response + Logprobs                      │
├─────────────────────────────────────────────────────────────────┤
│  Response: "John Cole Howard is a character from The Office"    │
│  Tokens:   ["John", "Cole", "Howard", "is", "a", "character"...]│
│  Logprobs: [-0.1,  -0.2,  -0.3,    -0.1, -0.2, -0.8,       ...] │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                    Confidence Analysis                          │
├─────────────────────────────────────────────────────────────────┤
│  Token "character": prob = e^(-0.8) = 0.45 ← LOW CONFIDENCE     │
│  Aggregate perplexity, identify low-confidence regions          │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                    Action                                       │
├─────────────────────────────────────────────────────────────────┤
│  Flag for review │ Regenerate │ Request human validation        │
└─────────────────────────────────────────────────────────────────┘
```

## Implementation

### Step 1: Request Logprobs from LLM

```python
import math
from dataclasses import dataclass
from typing import List, Optional
from openai import OpenAI

@dataclass
class TokenInfo:
    token: str
    logprob: float
    probability: float
    alternatives: List[dict]

@dataclass
class ConfidenceResult:
    response_text: str
    tokens: List[TokenInfo]
    min_probability: float
    mean_probability: float
    perplexity: float
    low_confidence_spans: List[dict]

def get_response_with_logprobs(
    client: OpenAI,
    prompt: str,
    model: str = "gpt-4o-mini",
    top_logprobs: int = 5
) -> ConfidenceResult:
    """Get LLM response with token probabilities."""
    
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        logprobs=True,
        top_logprobs=top_logprobs
    )
    
    response_text = response.choices[0].message.content
    logprobs_data = response.choices[0].logprobs
    
    tokens = []
    for token_info in logprobs_data.content:
        prob = math.exp(token_info.logprob)
        alternatives = [
            {"token": alt.token, "prob": math.exp(alt.logprob)}
            for alt in token_info.top_logprobs
            if alt.token != token_info.token
        ]
        tokens.append(TokenInfo(
            token=token_info.token,
            logprob=token_info.logprob,
            probability=prob,
            alternatives=alternatives
        ))
    
    return _analyze_confidence(response_text, tokens)
```

### Step 2: Analyze Confidence

```python
def _analyze_confidence(response_text: str, tokens: List[TokenInfo]) -> ConfidenceResult:
    """Compute confidence metrics from token probabilities."""
    
    if not tokens:
        return ConfidenceResult(
            response_text=response_text,
            tokens=[],
            min_probability=0.0,
            mean_probability=0.0,
            perplexity=float('inf'),
            low_confidence_spans=[]
        )
    
    probs = [t.probability for t in tokens]
    logprobs = [t.logprob for t in tokens]
    
    # Perplexity: geometric mean of inverse probabilities
    # Lower = more confident
    avg_logprob = sum(logprobs) / len(logprobs)
    perplexity = math.exp(-avg_logprob)
    
    # Identify low-confidence spans
    low_confidence_spans = _find_low_confidence_spans(tokens, threshold=0.5)
    
    return ConfidenceResult(
        response_text=response_text,
        tokens=tokens,
        min_probability=min(probs),
        mean_probability=sum(probs) / len(probs),
        perplexity=perplexity,
        low_confidence_spans=low_confidence_spans
    )

def _find_low_confidence_spans(
    tokens: List[TokenInfo], 
    threshold: float = 0.5
) -> List[dict]:
    """Find contiguous spans of low-confidence tokens."""
    
    spans = []
    current_span = None
    
    for i, token in enumerate(tokens):
        if token.probability < threshold:
            if current_span is None:
                current_span = {
                    "start_idx": i,
                    "tokens": [token.token],
                    "min_prob": token.probability,
                    "alternatives": token.alternatives[:3]
                }
            else:
                current_span["tokens"].append(token.token)
                current_span["min_prob"] = min(current_span["min_prob"], token.probability)
        else:
            if current_span is not None:
                current_span["end_idx"] = i
                current_span["text"] = "".join(current_span["tokens"])
                spans.append(current_span)
                current_span = None
    
    # Close any open span
    if current_span is not None:
        current_span["end_idx"] = len(tokens)
        current_span["text"] = "".join(current_span["tokens"])
        spans.append(current_span)
    
    return spans
```

### Step 3: Confidence Thresholds by Use Case

```python
@dataclass
class ConfidencePolicy:
    """Define confidence thresholds for different use cases."""
    
    name: str
    min_token_threshold: float  # Flag if any token below this
    mean_threshold: float       # Flag if mean below this
    perplexity_threshold: float # Flag if perplexity above this
    
    def evaluate(self, result: ConfidenceResult) -> dict:
        flags = []
        
        if result.min_probability < self.min_token_threshold:
            flags.append({
                "type": "low_token",
                "value": result.min_probability,
                "threshold": self.min_token_threshold
            })
        
        if result.mean_probability < self.mean_threshold:
            flags.append({
                "type": "low_mean",
                "value": result.mean_probability,
                "threshold": self.mean_threshold
            })
        
        if result.perplexity > self.perplexity_threshold:
            flags.append({
                "type": "high_perplexity",
                "value": result.perplexity,
                "threshold": self.perplexity_threshold
            })
        
        return {
            "policy": self.name,
            "is_confident": len(flags) == 0,
            "flags": flags,
            "low_confidence_spans": result.low_confidence_spans
        }

# Predefined policies
POLICIES = {
    "strict": ConfidencePolicy(
        name="strict",
        min_token_threshold=0.7,
        mean_threshold=0.8,
        perplexity_threshold=2.0
    ),
    "moderate": ConfidencePolicy(
        name="moderate",
        min_token_threshold=0.5,
        mean_threshold=0.6,
        perplexity_threshold=4.0
    ),
    "lenient": ConfidencePolicy(
        name="lenient",
        min_token_threshold=0.3,
        mean_threshold=0.5,
        perplexity_threshold=8.0
    )
}
```

### Step 4: Structured Output Confidence

For structured extraction, focus confidence checks on value tokens:

```python
import re
from typing import Dict

def score_structured_output(
    result: ConfidenceResult,
    field_patterns: Dict[str, str]
) -> Dict[str, float]:
    """Score confidence per field in structured output."""
    
    field_scores = {}
    full_text = result.response_text
    
    for field_name, pattern in field_patterns.items():
        match = re.search(pattern, full_text)
        if not match:
            field_scores[field_name] = 0.0
            continue
        
        # Find tokens that correspond to this field's value
        start_pos = match.start()
        end_pos = match.end()
        
        # Map character positions to token indices
        char_pos = 0
        field_tokens = []
        for token in result.tokens:
            token_end = char_pos + len(token.token)
            if char_pos >= start_pos and token_end <= end_pos:
                field_tokens.append(token)
            char_pos = token_end
        
        if field_tokens:
            field_scores[field_name] = min(t.probability for t in field_tokens)
        else:
            field_scores[field_name] = 1.0  # No specific tokens found
    
    return field_scores

# Example: Receipt parsing
RECEIPT_PATTERNS = {
    "billed_amount": r"billed.*?(\d+\.\d{2})",
    "tax": r"tax.*?(\d+\.\d{2})",
    "tip": r"tip.*?(\d+\.\d{2})",
    "total": r"total.*?(\d+\.\d{2})"
}
```

## False Positive Mitigation

Not all low-probability tokens indicate hallucination:

| Scenario | Low Prob Reason | Is Hallucination? |
|----------|-----------------|-------------------|
| "Atatürk was born in 1881" | Multiple valid phrasings | No |
| "The Office character Ed" | Actual uncertainty | Yes |
| Start of sentence | Many valid continuations | No |
| Rare proper nouns | Low training frequency | Maybe |

### Mitigation Strategies

```python
def mitigate_false_positives(result: ConfidenceResult) -> List[dict]:
    """Filter out likely false positive low-confidence spans."""
    
    filtered_spans = []
    
    for span in result.low_confidence_spans:
        # Skip sentence-initial tokens
        if span["start_idx"] == 0:
            continue
        
        # Skip common structural variations
        structural_patterns = ["The", "A", "An", "In", "On", "At"]
        if span["text"].strip() in structural_patterns:
            continue
        
        # Skip if alternatives are semantically equivalent
        if _alternatives_are_equivalent(span):
            continue
        
        filtered_spans.append(span)
    
    return filtered_spans

def _alternatives_are_equivalent(span: dict) -> bool:
    """Check if top alternatives would give same meaning."""
    # Use embeddings to compare semantic similarity
    # Simplified version: check for common equivalents
    equivalents = {
        "The": ["A", "This"],
        "is": ["was", "has been"],
        # ... more patterns
    }
    text = span["text"].strip()
    alts = [a["token"].strip() for a in span.get("alternatives", [])]
    return text in equivalents and all(a in equivalents.get(text, []) for a in alts)
```

## Sequence Generation for Validation

When low confidence detected, generate multiple sequences and compare:

```python
def validate_with_sampling(
    client: OpenAI,
    prompt: str,
    num_samples: int = 3,
    similarity_threshold: float = 0.9
) -> dict:
    """Generate multiple responses and check agreement."""
    
    responses = []
    for _ in range(num_samples):
        result = get_response_with_logprobs(client, prompt)
        responses.append(result.response_text)
    
    # Compare responses using embeddings
    embeddings = [get_embedding(r) for r in responses]
    
    # Calculate pairwise similarity
    similarities = []
    for i in range(len(embeddings)):
        for j in range(i + 1, len(embeddings)):
            sim = cosine_similarity(embeddings[i], embeddings[j])
            similarities.append(sim)
    
    mean_similarity = sum(similarities) / len(similarities)
    
    return {
        "responses": responses,
        "mean_similarity": mean_similarity,
        "is_consistent": mean_similarity >= similarity_threshold,
        "recommendation": "trust" if mean_similarity >= similarity_threshold else "verify"
    }
```

## Integration with RAG Conflict Detection

```python
def detect_rag_conflicts(
    chunks: List[str],
    query: str,
    client: OpenAI
) -> dict:
    """Detect if RAG chunks contain conflicting information."""
    
    # Generate response grounded in chunks
    context = "\n---\n".join(chunks)
    prompt = f"""Based on these sources, answer the question.
    
Sources:
{context}

Question: {query}

Answer:"""
    
    result = get_response_with_logprobs(client, prompt)
    
    # Low confidence may indicate conflicting sources
    if result.low_confidence_spans:
        return {
            "has_potential_conflicts": True,
            "confidence": result.mean_probability,
            "flagged_spans": result.low_confidence_spans,
            "recommendation": "Review source chunks for contradictions"
        }
    
    return {
        "has_potential_conflicts": False,
        "confidence": result.mean_probability
    }
```

## Provider Compatibility

| Provider | Logprobs Available | API Parameter |
|----------|-------------------|---------------|
| OpenAI | Yes | `logprobs=True, top_logprobs=5` |
| Anthropic | No | Use sampling-based validation instead |
| Google | Limited | `candidate_count` for alternatives |
| Azure OpenAI | Yes | Same as OpenAI |
| Local (Ollama) | Yes | Depends on model |

### Fallback for Non-Logprob Providers

```python
def confidence_without_logprobs(
    client,
    prompt: str,
    num_samples: int = 3
) -> float:
    """Estimate confidence via response consistency."""
    
    responses = [client.complete(prompt) for _ in range(num_samples)]
    
    # Use embedding similarity as proxy for confidence
    embeddings = [get_embedding(r) for r in responses]
    
    # High similarity across samples = high confidence
    similarities = []
    for i in range(len(embeddings)):
        for j in range(i + 1, len(embeddings)):
            similarities.append(cosine_similarity(embeddings[i], embeddings[j]))
    
    return sum(similarities) / len(similarities)
```
