"""RAG Generation Evaluation Module (Lesson 13).

This module provides classes for evaluating RAG generation quality:
- AttributionDetector: Verifies if LLM responses properly cite sources
- HallucinationDetector: Detects intrinsic and extrinsic hallucinations
- ContextUtilizationScorer: Measures which context documents LLM actually uses

Following TDD-GREEN phase: Minimal implementation to pass tests.
"""

import re
from typing import Any


class AttributionDetector:
    """Detects whether LLM responses properly attribute claims to source context.

    Attribution means the LLM's response only contains information that can be
    traced back to the provided context documents.
    """

    def extract_claims(self, response: str) -> list[str]:
        """Extract atomic claims from LLM response.

        Args:
            response: LLM-generated text response

        Returns:
            List of atomic claims (individual factual statements)
        """
        if not response or not response.strip():
            return []

        # Simple sentence splitting for minimal implementation
        # In production, would use spaCy or more sophisticated NLP
        sentences = re.split(r"[.!?]+", response)
        claims = [s.strip() for s in sentences if s.strip()]

        return claims

    def verify_attribution(self, claims: list[str], context: list[str]) -> dict[str, Any]:
        """Verify if each claim can be attributed to context.

        Args:
            claims: List of atomic claims from LLM response
            context: List of source documents

        Returns:
            Dictionary with attribution_scores (list of bool)

        Raises:
            TypeError: If claims or context is not a list
        """
        # Step 1: Type checking (defensive coding)
        if not isinstance(claims, list):
            raise TypeError("claims must be a list")
        if not isinstance(context, list):
            raise TypeError("context must be a list")

        # Step 2: Verify each claim
        attribution_scores = []
        for claim in claims:
            is_attributed = self._check_claim_in_context(claim, context)
            attribution_scores.append(is_attributed)

        # Step 3: Return results
        return {"attribution_scores": attribution_scores}

    def calculate_attribution_rate(self, results: list[dict[str, Any]]) -> float:
        """Calculate overall attribution rate across multiple test cases.

        Args:
            results: List of verification results from verify_attribution()

        Returns:
            Attribution rate (0.0 to 1.0) = attributed_claims / total_claims
        """
        # Step 1: Handle empty input
        if not results:
            return 0.0

        # Step 2: Count attributed vs total claims
        total_claims = 0
        attributed_claims = 0

        for result in results:
            scores = result.get("attribution_scores", [])
            total_claims += len(scores)
            attributed_claims += sum(1 for score in scores if score)

        # Step 3: Calculate rate
        if total_claims == 0:
            return 0.0

        return attributed_claims / total_claims

    def _check_claim_in_context(self, claim: str, context: list[str]) -> bool:
        """Check if a claim can be found in any context document.

        Args:
            claim: Single atomic claim
            context: List of context documents

        Returns:
            True if claim is in context, False otherwise
        """
        # Simple exact substring matching for minimal implementation
        # In production, would use semantic similarity with embeddings
        claim_lower = claim.lower().strip()

        for doc in context:
            if claim_lower in doc.lower():
                return True

        return False


class HallucinationDetector:
    """Detects hallucinations in RAG system responses.

    Two types of hallucinations:
    - Intrinsic: Response contradicts the context
    - Extrinsic: Response contains info not in context (but not contradicting)
    """

    def detect_intrinsic_hallucination(self, response: str, context: list[str]) -> bool:
        """Detect intrinsic hallucinations (contradicts context).

        Args:
            response: LLM-generated response
            context: List of source documents

        Returns:
            True if response contradicts context, False otherwise

        Raises:
            TypeError: If response is not string or context is not list
        """
        # Step 1: Type checking
        if not isinstance(response, str):
            raise TypeError("response must be a string")
        if not isinstance(context, list):
            raise TypeError("context must be a list")

        # Step 2: Check for contradictions
        has_contradiction = self._check_contradiction(response, context)

        return has_contradiction

    def detect_extrinsic_hallucination(self, response: str, context: list[str]) -> bool:
        """Detect extrinsic hallucinations (info not in context).

        Args:
            response: LLM-generated response
            context: List of source documents

        Returns:
            True if response contains unverifiable claims, False otherwise

        Raises:
            TypeError: If response is not string or context is not list
        """
        # Step 1: Type checking
        if not isinstance(response, str):
            raise TypeError("response must be a string")
        if not isinstance(context, list):
            raise TypeError("context must be a list")

        # Step 2: Check if claims are in context
        claims_presence = self._check_claims_in_context(response, context)

        # Step 3: Extrinsic if any claim is not in context
        has_extrinsic = any(not present for present in claims_presence)

        return has_extrinsic

    def classify_hallucination_type(self, response: str, context: list[str]) -> str:
        """Classify hallucination type: NONE, INTRINSIC, or EXTRINSIC.

        Args:
            response: LLM-generated response
            context: List of source documents

        Returns:
            One of: "NONE", "INTRINSIC", "EXTRINSIC"
        """
        # Intrinsic takes precedence (more severe)
        if self.detect_intrinsic_hallucination(response, context):
            return "INTRINSIC"

        # Check for extrinsic
        if self.detect_extrinsic_hallucination(response, context):
            return "EXTRINSIC"

        # No hallucination detected
        return "NONE"

    def _check_contradiction(self, response: str, context: list[str]) -> bool:
        """Check if response contradicts any context document.

        Args:
            response: LLM response
            context: Source documents

        Returns:
            True if contradiction detected, False otherwise
        """
        # Minimal implementation: detect negation patterns
        # In production, would use NLI (Natural Language Inference) model
        negation_patterns = ["not", "never", "avoid", "should not", "don't", "doesn't"]

        response_lower = response.lower()
        has_negation = any(pattern in response_lower for pattern in negation_patterns)

        if not has_negation:
            return False

        # Check if negation contradicts context
        context_text = " ".join(context).lower()
        # Simple heuristic: if response has negation but context doesn't, might be contradiction
        context_has_positive = any(
            word in context_text for word in ["should", "must", "teaches", "recommends"]
        )

        return has_negation and context_has_positive

    def _check_claims_in_context(self, response: str, context: list[str]) -> list[bool]:
        """Check which claims from response are present in context.

        Args:
            response: LLM response
            context: Source documents

        Returns:
            List of booleans indicating presence of each claim
        """
        # Extract claims (simple sentence splitting)
        sentences = re.split(r"[.!?]+", response)
        claims = [s.strip() for s in sentences if s.strip()]

        # Check each claim
        presence = []
        context_text = " ".join(context).lower()

        for claim in claims:
            # Simple substring check
            claim_lower = claim.lower()
            is_present = claim_lower in context_text

            # Also check for key phrases
            key_words = claim_lower.split()
            if len(key_words) > 2:
                # At least 50% of words should be in context
                matching_words = sum(1 for word in key_words if word in context_text)
                is_present = is_present or (matching_words / len(key_words) >= 0.5)

            presence.append(is_present)

        return presence if presence else [False]


class ContextUtilizationScorer:
    """Measures which context documents the LLM actually uses in its response.

    Uses semantic similarity to determine if a retrieved document was:
    - USED (>0.7 similarity): LLM actively referenced this document
    - PARTIAL (0.4-0.7 similarity): LLM partially used this document
    - IGNORED (<0.4 similarity): LLM did not use this document
    """

    def measure_utilization(self, response: str, contexts: list[str]) -> dict[int, float]:
        """Measure semantic similarity between response and each context document.

        Args:
            response: LLM-generated response
            contexts: List of retrieved context documents

        Returns:
            Dictionary mapping context_index -> similarity_score (0.0 to 1.0)

        Raises:
            TypeError: If response is not string or contexts is not list
        """
        # Step 1: Type checking
        if not isinstance(response, str):
            raise TypeError("response must be a string")
        if not isinstance(contexts, list):
            raise TypeError("contexts must be a list")

        # Step 2: Handle empty contexts
        if not contexts:
            return {}

        # Step 3: Calculate similarity for each context
        utilization = {}
        for i, context in enumerate(contexts):
            similarity = self._calculate_similarity(response, context)
            utilization[i] = similarity

        return utilization

    def classify_usage(self, similarity: float) -> str:
        """Classify context usage based on similarity score.

        Args:
            similarity: Similarity score (0.0 to 1.0)

        Returns:
            One of: "USED", "PARTIAL", "IGNORED"

        Raises:
            ValueError: If similarity is not in range [0, 1]
        """
        # Step 1: Input validation
        if not (0.0 <= similarity <= 1.0):
            raise ValueError("similarity must be between 0 and 1")

        # Step 2: Classify based on thresholds
        if similarity > 0.7:
            return "USED"
        elif similarity >= 0.4:
            return "PARTIAL"
        else:
            return "IGNORED"

    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """Calculate semantic similarity between two texts.

        Args:
            text1: First text (typically LLM response)
            text2: Second text (typically context document)

        Returns:
            Similarity score from 0.0 (no similarity) to 1.0 (identical)
        """
        # Minimal implementation: Jaccard similarity on word sets
        # In production, would use embeddings (OpenAI, sentence-transformers)

        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())

        if not words1 or not words2:
            return 0.0

        intersection = words1.intersection(words2)
        union = words1.union(words2)

        jaccard_similarity = len(intersection) / len(union) if union else 0.0

        return jaccard_similarity
