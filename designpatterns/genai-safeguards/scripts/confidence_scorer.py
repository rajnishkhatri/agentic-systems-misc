#!/usr/bin/env python3
"""
Confidence Scorer - Utility functions for Self-Check pattern.
Framework-agnostic, invokable by any agent.

Uses token probabilities (logprobs) to detect potential hallucinations
and assign confidence scores to LLM outputs.

Usage:
    from confidence_scorer import ConfidenceScorer, ConfidencePolicy
    
    scorer = ConfidenceScorer(openai_client)
    result = scorer.score(prompt)
    
    if result.perplexity > 5.0:
        print("Low confidence - potential hallucination")
"""

import math
import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Protocol, Callable
from enum import Enum


# ============================================================================
# Data Models
# ============================================================================

@dataclass
class TokenInfo:
    """Information about a single generated token."""
    token: str
    logprob: float
    probability: float
    position: int
    alternatives: List[Dict[str, float]] = field(default_factory=list)
    
    @property
    def is_low_confidence(self) -> bool:
        """Token probability below 50%."""
        return self.probability < 0.5
    
    @property
    def entropy(self) -> float:
        """Entropy across alternatives (higher = more uncertain)."""
        if not self.alternatives:
            return 0.0
        probs = [self.probability] + [a["probability"] for a in self.alternatives]
        return -sum(p * math.log(p + 1e-10) for p in probs if p > 0)


@dataclass
class LowConfidenceSpan:
    """A contiguous span of low-confidence tokens."""
    start_idx: int
    end_idx: int
    tokens: List[str]
    text: str
    min_probability: float
    mean_probability: float
    alternatives: List[Dict[str, float]]


@dataclass
class ConfidenceResult:
    """Complete confidence analysis result."""
    response_text: str
    tokens: List[TokenInfo]
    
    # Aggregate metrics
    min_probability: float
    mean_probability: float
    perplexity: float
    
    # Flagged regions
    low_confidence_spans: List[LowConfidenceSpan]
    
    # Field-level scores (for structured output)
    field_scores: Optional[Dict[str, float]] = None
    
    # Policy evaluation
    policy_result: Optional[Dict[str, Any]] = None
    
    @property
    def is_confident(self) -> bool:
        """Quick check - True if no major confidence issues."""
        return (
            self.min_probability > 0.3 and
            self.mean_probability > 0.5 and
            self.perplexity < 8.0 and
            len(self.low_confidence_spans) == 0
        )
    
    @property
    def confidence_score(self) -> float:
        """Single 0-1 confidence score."""
        # Weighted combination of metrics
        return (
            0.3 * self.min_probability +
            0.4 * self.mean_probability +
            0.3 * max(0, 1 - self.perplexity / 10)
        )


# ============================================================================
# Confidence Policies
# ============================================================================

class ConfidenceLevel(Enum):
    """Predefined confidence levels."""
    STRICT = "strict"
    MODERATE = "moderate"
    LENIENT = "lenient"


@dataclass
class ConfidencePolicy:
    """
    Define confidence thresholds for different use cases.
    
    Usage:
        policy = ConfidencePolicy.strict()
        result = policy.evaluate(confidence_result)
    """
    name: str
    min_token_threshold: float      # Flag if any token below this
    mean_threshold: float           # Flag if mean below this
    perplexity_threshold: float     # Flag if perplexity above this
    max_low_confidence_spans: int   # Flag if more spans than this
    
    def evaluate(self, result: ConfidenceResult) -> Dict[str, Any]:
        """Evaluate a confidence result against this policy."""
        flags = []
        
        if result.min_probability < self.min_token_threshold:
            flags.append({
                "type": "low_token",
                "message": f"Token probability {result.min_probability:.3f} below threshold {self.min_token_threshold}",
                "severity": "high" if result.min_probability < 0.2 else "medium"
            })
        
        if result.mean_probability < self.mean_threshold:
            flags.append({
                "type": "low_mean",
                "message": f"Mean probability {result.mean_probability:.3f} below threshold {self.mean_threshold}",
                "severity": "medium"
            })
        
        if result.perplexity > self.perplexity_threshold:
            flags.append({
                "type": "high_perplexity",
                "message": f"Perplexity {result.perplexity:.2f} above threshold {self.perplexity_threshold}",
                "severity": "medium"
            })
        
        if len(result.low_confidence_spans) > self.max_low_confidence_spans:
            flags.append({
                "type": "many_low_confidence_spans",
                "message": f"{len(result.low_confidence_spans)} low confidence spans (max: {self.max_low_confidence_spans})",
                "severity": "high"
            })
        
        return {
            "policy": self.name,
            "is_confident": len(flags) == 0,
            "flags": flags,
            "recommendation": self._get_recommendation(flags)
        }
    
    def _get_recommendation(self, flags: List[Dict]) -> str:
        if not flags:
            return "Output appears reliable"
        
        high_severity = [f for f in flags if f.get("severity") == "high"]
        if high_severity:
            return "Manual review recommended - significant uncertainty detected"
        return "Exercise caution - moderate uncertainty detected"
    
    @classmethod
    def strict(cls) -> "ConfidencePolicy":
        """Strict policy for critical applications (finance, healthcare)."""
        return cls(
            name="strict",
            min_token_threshold=0.7,
            mean_threshold=0.8,
            perplexity_threshold=2.0,
            max_low_confidence_spans=0
        )
    
    @classmethod
    def moderate(cls) -> "ConfidencePolicy":
        """Moderate policy for general business use."""
        return cls(
            name="moderate",
            min_token_threshold=0.5,
            mean_threshold=0.6,
            perplexity_threshold=4.0,
            max_low_confidence_spans=2
        )
    
    @classmethod
    def lenient(cls) -> "ConfidencePolicy":
        """Lenient policy for creative or exploratory tasks."""
        return cls(
            name="lenient",
            min_token_threshold=0.3,
            mean_threshold=0.5,
            perplexity_threshold=8.0,
            max_low_confidence_spans=5
        )


# ============================================================================
# Main Confidence Scorer
# ============================================================================

class ConfidenceScorer:
    """
    Main class for confidence scoring using logprobs.
    
    Usage:
        scorer = ConfidenceScorer(openai_client)
        result = scorer.score("What year was Atatürk born?")
        print(f"Confidence: {result.confidence_score:.2f}")
        print(f"Low confidence spans: {result.low_confidence_spans}")
    """
    
    def __init__(
        self,
        llm_client,
        model: str = "gpt-4o-mini",
        top_logprobs: int = 5,
        default_policy: Optional[ConfidencePolicy] = None
    ):
        """
        Args:
            llm_client: OpenAI-compatible client
            model: Model to use
            top_logprobs: Number of alternative tokens to request
            default_policy: Policy to apply automatically
        """
        self.client = llm_client
        self.model = model
        self.top_logprobs = top_logprobs
        self.default_policy = default_policy or ConfidencePolicy.moderate()
    
    def score(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        policy: Optional[ConfidencePolicy] = None,
        field_patterns: Optional[Dict[str, str]] = None
    ) -> ConfidenceResult:
        """
        Get LLM response with confidence scores.
        
        Args:
            prompt: User prompt
            system_prompt: Optional system prompt
            policy: Confidence policy to evaluate against
            field_patterns: Regex patterns to score specific fields
        
        Returns:
            ConfidenceResult with full analysis
        """
        # Build messages
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        # Call API with logprobs
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            logprobs=True,
            top_logprobs=self.top_logprobs
        )
        
        response_text = response.choices[0].message.content
        logprobs_data = response.choices[0].logprobs
        
        # Parse tokens
        tokens = self._parse_tokens(logprobs_data)
        
        # Calculate metrics
        result = self._analyze(response_text, tokens)
        
        # Score specific fields if patterns provided
        if field_patterns:
            result.field_scores = self._score_fields(result, field_patterns)
        
        # Apply policy
        active_policy = policy or self.default_policy
        result.policy_result = active_policy.evaluate(result)
        
        return result
    
    def _parse_tokens(self, logprobs_data) -> List[TokenInfo]:
        """Parse token information from API response."""
        tokens = []
        
        for i, token_info in enumerate(logprobs_data.content):
            prob = math.exp(token_info.logprob)
            
            alternatives = []
            if token_info.top_logprobs:
                for alt in token_info.top_logprobs:
                    if alt.token != token_info.token:
                        alternatives.append({
                            "token": alt.token,
                            "logprob": alt.logprob,
                            "probability": math.exp(alt.logprob)
                        })
            
            tokens.append(TokenInfo(
                token=token_info.token,
                logprob=token_info.logprob,
                probability=prob,
                position=i,
                alternatives=alternatives
            ))
        
        return tokens
    
    def _analyze(self, response_text: str, tokens: List[TokenInfo]) -> ConfidenceResult:
        """Compute confidence metrics from tokens."""
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
        avg_logprob = sum(logprobs) / len(logprobs)
        perplexity = math.exp(-avg_logprob)
        
        # Find low-confidence spans
        low_confidence_spans = self._find_low_confidence_spans(tokens)
        
        return ConfidenceResult(
            response_text=response_text,
            tokens=tokens,
            min_probability=min(probs),
            mean_probability=sum(probs) / len(probs),
            perplexity=perplexity,
            low_confidence_spans=low_confidence_spans
        )
    
    def _find_low_confidence_spans(
        self,
        tokens: List[TokenInfo],
        threshold: float = 0.5
    ) -> List[LowConfidenceSpan]:
        """Find contiguous spans of low-confidence tokens."""
        spans = []
        current_tokens = []
        current_start = None
        
        for i, token in enumerate(tokens):
            if token.probability < threshold:
                if current_start is None:
                    current_start = i
                current_tokens.append(token)
            else:
                if current_tokens:
                    spans.append(self._create_span(current_start, i, current_tokens))
                current_tokens = []
                current_start = None
        
        # Close any open span
        if current_tokens:
            spans.append(self._create_span(current_start, len(tokens), current_tokens))
        
        # Filter out likely false positives
        return self._filter_false_positives(spans)
    
    def _create_span(
        self,
        start: int,
        end: int,
        tokens: List[TokenInfo]
    ) -> LowConfidenceSpan:
        """Create a LowConfidenceSpan from tokens."""
        probs = [t.probability for t in tokens]
        all_alternatives = []
        for t in tokens:
            all_alternatives.extend(t.alternatives[:2])
        
        return LowConfidenceSpan(
            start_idx=start,
            end_idx=end,
            tokens=[t.token for t in tokens],
            text="".join(t.token for t in tokens),
            min_probability=min(probs),
            mean_probability=sum(probs) / len(probs),
            alternatives=all_alternatives[:5]
        )
    
    def _filter_false_positives(
        self,
        spans: List[LowConfidenceSpan]
    ) -> List[LowConfidenceSpan]:
        """Filter out likely false positive spans."""
        filtered = []
        
        # Common structural tokens that often have low probability
        structural_patterns = {
            "The", "A", "An", "In", "On", "At", "To", "For",
            "is", "are", "was", "were", "be", "been",
            ":", ",", ".", "!", "?", "\n", " "
        }
        
        for span in spans:
            text = span.text.strip()
            
            # Skip if it's at position 0 (sentence start has many options)
            if span.start_idx == 0 and len(span.tokens) <= 2:
                continue
            
            # Skip if it's just structural tokens
            if text in structural_patterns:
                continue
            
            # Skip very short spans of common words
            if len(text) <= 3 and span.min_probability > 0.3:
                continue
            
            filtered.append(span)
        
        return filtered
    
    def _score_fields(
        self,
        result: ConfidenceResult,
        field_patterns: Dict[str, str]
    ) -> Dict[str, float]:
        """Score confidence for specific fields in structured output."""
        field_scores = {}
        full_text = result.response_text
        
        for field_name, pattern in field_patterns.items():
            match = re.search(pattern, full_text)
            if not match:
                field_scores[field_name] = 0.0
                continue
            
            # Find tokens corresponding to the match
            start_char = match.start()
            end_char = match.end()
            
            # Build character position map
            char_pos = 0
            field_tokens = []
            for token in result.tokens:
                token_start = char_pos
                token_end = char_pos + len(token.token)
                
                # Check if token overlaps with field
                if token_end > start_char and token_start < end_char:
                    field_tokens.append(token)
                
                char_pos = token_end
            
            if field_tokens:
                field_scores[field_name] = min(t.probability for t in field_tokens)
            else:
                field_scores[field_name] = 1.0
        
        return field_scores


# ============================================================================
# Sampling-Based Validation (for providers without logprobs)
# ============================================================================

class SamplingValidator:
    """
    Validate confidence by generating multiple samples and comparing.
    Use when logprobs are not available (e.g., Anthropic).
    """
    
    def __init__(
        self,
        llm_client,
        embedding_fn: Optional[Callable[[str], List[float]]] = None
    ):
        """
        Args:
            llm_client: LLM client with complete() method
            embedding_fn: Function to get embeddings for similarity comparison
        """
        self.client = llm_client
        self.get_embedding = embedding_fn
    
    def validate(
        self,
        prompt: str,
        num_samples: int = 3,
        similarity_threshold: float = 0.9
    ) -> Dict[str, Any]:
        """
        Generate multiple responses and check agreement.
        
        Args:
            prompt: The prompt to validate
            num_samples: Number of samples to generate
            similarity_threshold: Threshold for considering responses consistent
        
        Returns:
            Validation result with consistency score
        """
        responses = []
        for _ in range(num_samples):
            response = self.client.complete(prompt)
            responses.append(response)
        
        if self.get_embedding:
            return self._embedding_validation(responses, similarity_threshold)
        else:
            return self._text_validation(responses)
    
    def _embedding_validation(
        self,
        responses: List[str],
        threshold: float
    ) -> Dict[str, Any]:
        """Validate using embedding similarity."""
        embeddings = [self.get_embedding(r) for r in responses]
        
        # Calculate pairwise similarities
        similarities = []
        for i in range(len(embeddings)):
            for j in range(i + 1, len(embeddings)):
                sim = self._cosine_similarity(embeddings[i], embeddings[j])
                similarities.append(sim)
        
        mean_similarity = sum(similarities) / len(similarities) if similarities else 0
        
        return {
            "responses": responses,
            "num_samples": len(responses),
            "mean_similarity": mean_similarity,
            "is_consistent": mean_similarity >= threshold,
            "confidence_estimate": mean_similarity,
            "recommendation": "trust" if mean_similarity >= threshold else "verify"
        }
    
    def _text_validation(self, responses: List[str]) -> Dict[str, Any]:
        """Simple text-based validation without embeddings."""
        # Check for exact matches
        unique_responses = set(responses)
        agreement_ratio = 1 - (len(unique_responses) - 1) / len(responses)
        
        # Find common substrings
        if len(responses) >= 2:
            common = self._longest_common_substring(responses[0], responses[1])
            common_ratio = len(common) / max(len(responses[0]), len(responses[1]))
        else:
            common_ratio = 1.0
        
        confidence = (agreement_ratio + common_ratio) / 2
        
        return {
            "responses": responses,
            "num_samples": len(responses),
            "unique_responses": len(unique_responses),
            "agreement_ratio": agreement_ratio,
            "confidence_estimate": confidence,
            "is_consistent": confidence >= 0.7,
            "recommendation": "trust" if confidence >= 0.7 else "verify"
        }
    
    @staticmethod
    def _cosine_similarity(a: List[float], b: List[float]) -> float:
        """Calculate cosine similarity between two vectors."""
        dot = sum(x * y for x, y in zip(a, b))
        norm_a = math.sqrt(sum(x * x for x in a))
        norm_b = math.sqrt(sum(x * x for x in b))
        return dot / (norm_a * norm_b) if norm_a and norm_b else 0
    
    @staticmethod
    def _longest_common_substring(s1: str, s2: str) -> str:
        """Find longest common substring."""
        m, n = len(s1), len(s2)
        dp = [[0] * (n + 1) for _ in range(m + 1)]
        max_len, end_pos = 0, 0
        
        for i in range(1, m + 1):
            for j in range(1, n + 1):
                if s1[i-1] == s2[j-1]:
                    dp[i][j] = dp[i-1][j-1] + 1
                    if dp[i][j] > max_len:
                        max_len = dp[i][j]
                        end_pos = i
        
        return s1[end_pos - max_len:end_pos]


# ============================================================================
# Convenience Functions
# ============================================================================

def quick_confidence_check(
    client,
    prompt: str,
    threshold: float = 0.5
) -> Dict[str, Any]:
    """
    Quick confidence check without full scorer setup.
    
    Usage:
        result = quick_confidence_check(openai_client, "What is 2+2?")
        if result["is_confident"]:
            print(result["response"])
    """
    scorer = ConfidenceScorer(client)
    result = scorer.score(prompt)
    
    return {
        "response": result.response_text,
        "is_confident": result.is_confident,
        "confidence_score": result.confidence_score,
        "perplexity": result.perplexity,
        "low_confidence_spans": [
            {"text": s.text, "probability": s.min_probability}
            for s in result.low_confidence_spans
        ]
    }


if __name__ == "__main__":
    print("Confidence Scorer initialized.")
    print("Use ConfidenceScorer(client).score(prompt) or quick_confidence_check()")
