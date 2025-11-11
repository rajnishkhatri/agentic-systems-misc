# Attribution Evaluation in RAG Systems

**Reading Time:** 22-25 minutes
**Prerequisites:** [Lesson 12: Hybrid Retrieval](../lesson-12/TUTORIAL_INDEX.md), [HW4: RAG Evaluation Basics](../homeworks/hw4/TUTORIAL_INDEX.md)
**Next Steps:** [Hallucination Detection](./hallucination_detection_rag.md), [End-to-End RAG Evaluation](./end_to_end_rag_eval.md)

---

## Table of Contents

1. [Introduction](#introduction)
2. [What is Attribution in RAG?](#what-is-attribution-in-rag)
3. [Attribution vs Related Concepts](#attribution-vs-related-concepts)
4. [The Attribution Challenge](#the-attribution-challenge)
5. [Detecting Unattributed Claims](#detecting-unattributed-claims)
6. [Claim Extraction and Matching](#claim-extraction-and-matching)
7. [Measuring Attribution Rate](#measuring-attribution-rate)
8. [Practical Implementation](#practical-implementation)
9. [Common Pitfalls](#common-pitfalls)
10. [Real-World Applications](#real-world-applications)

---

## Introduction

Retrieval-Augmented Generation (RAG) systems promise to ground LLM responses in retrieved documents, reducing hallucinations and improving factual accuracy. However, **just because an LLM has access to relevant context doesn't guarantee it will actually use that context** in its response.

**Attribution evaluation** answers a critical question: *Does the LLM's response correctly cite and derive from the retrieved documents?*

In this tutorial, you'll learn:
- How to detect when an LLM makes unattributed claims
- The difference between attribution, grounding, citation, and substantiation
- Techniques for extracting and verifying claims against source documents
- How to build automated attribution detection systems
- When attribution failures indicate retrieval vs generation problems

---

## What is Attribution in RAG?

**Attribution** is the property that every factual claim in an LLM's response can be traced back to specific passages in the retrieved documents.

### Formal Definition

Given:
- **Query** `q`: User's question
- **Retrieved Context** `C = {d₁, d₂, ..., dₙ}`: Set of retrieved documents
- **LLM Response** `r`: Generated answer

A response `r` is **attributed** if and only if:
1. Every factual claim in `r` has supporting evidence in `C`
2. The LLM correctly identifies which documents support each claim
3. No information in `r` comes from the LLM's parametric memory alone

### Example: Attributed vs Unattributed Responses

**Query:** "What are the main ingredients in traditional Italian carbonara?"

**Retrieved Context:**
```
[Doc 1]: Traditional carbonara uses eggs, Pecorino Romano cheese,
guanciale (cured pork jowl), and black pepper. No cream is used
in authentic recipes.

[Doc 2]: Many American adaptations add cream, peas, or bacon
instead of guanciale.
```

**Attributed Response:**
> "According to traditional Italian recipes, carbonara contains eggs,
> Pecorino Romano cheese, guanciale (cured pork jowl), and black pepper
> (Source: Doc 1). Importantly, authentic carbonara does not include
> cream (Source: Doc 1)."

**Unattributed Response:**
> "Carbonara is made with eggs, Pecorino Romano, guanciale, and pepper.
> The dish originated in Rome in the 1940s, likely created by coal miners
> who needed a hearty meal."

**Why is the second response unattributed?**
- The historical claims (Rome, 1940s, coal miners) are NOT in the retrieved context
- The LLM is drawing from its parametric knowledge, not the provided documents
- While potentially accurate, this violates the RAG contract: **responses should derive only from retrieved context**

---

## Attribution vs Related Concepts

Attribution is often confused with related evaluation criteria. Let's clarify:

### 1. Attribution vs Grounding

**Grounding:** Response is factually consistent with context (no contradictions)

**Attribution:** Response explicitly derives from context with traceable sources

**Key Difference:**
```
Context: "Paris is the capital of France."

Grounded but NOT Attributed:
"France has a capital city known for the Eiffel Tower."
(True, no contradiction, but doesn't cite the source)

Attributed:
"Paris is the capital of France (Source: provided document)."
(Explicitly traces claim to source)
```

### 2. Attribution vs Citation

**Citation:** Adding source labels like "(Source: Doc 2)"

**Attribution:** **Substantive** correspondence between claims and sources

**Key Difference:**
```
Context: "The recipe requires 3 eggs."

Citation without Attribution:
"You need 5 eggs for this recipe (Source: Doc 1)."
(Has citation marker but WRONG information)

Attribution with Citation:
"You need 3 eggs (Source: Doc 1)."
(Correct information + source label)
```

**Lesson:** Citation markers are necessary but NOT sufficient for attribution.

### 3. Attribution vs Substantiation

**Substantiation (HW4 definition):** Response is supported by some external source (may not be in retrieved docs)

**Attribution:** Response is supported specifically by **provided retrieved documents**

**Key Difference:**
```
Query: "What is the boiling point of water?"
Retrieved Context: [empty or irrelevant documents]

Substantiated but NOT Attributed:
"Water boils at 100°C at sea level."
(True fact, substantiated by physics, but NOT in retrieved docs)

Neither Substantiated NOR Attributed:
"Water boils at 80°C."
(Incorrect and unsupported)
```

### Summary Table

| Property | Must be in Context? | Must be Correct? | Requires Citation? |
|----------|-------------------|------------------|-------------------|
| **Grounding** | Yes (no contradiction) | N/A | No |
| **Citation** | No | No | Yes |
| **Substantiation** | No (any source) | Yes | No |
| **Attribution** | Yes (retrieved docs) | Yes | Recommended |

---

## The Attribution Challenge

Why is attribution evaluation difficult?

### Challenge 1: Implicit Claims

LLMs often make claims without explicit statements:

```
Context: "Recipe serves 4-6 people."

Response: "This is a great recipe for a small dinner party."

Claim: "Small dinner party" implies 4-6 people
Is this attributed? YES (implicit but derivable)
```

### Challenge 2: Paraphrasing

LLMs rephrase context rather than quoting directly:

```
Context: "Bake at 375°F for 45 minutes until golden brown."

Response: "Cook in a preheated oven at medium-high heat for
approximately three-quarters of an hour until the surface
achieves a golden color."

Is this attributed? YES (paraphrased but accurate)
```

### Challenge 3: Multi-Document Synthesis

Claims may combine information from multiple sources:

```
Context:
[Doc 1]: "Carbonara uses guanciale."
[Doc 2]: "Guanciale is cured pork jowl."

Response: "Carbonara uses cured pork jowl."

Is this attributed? YES (synthesizes Doc 1 + Doc 2)
```

### Challenge 4: Partial Attribution

Some claims are attributed, others are not:

```
Context: "The Bhagavad Gita has 18 chapters."

Response: "The Bhagavad Gita, composed around 200 BCE,
contains 18 chapters and teaches the path of dharma."

Attribution Analysis:
✅ "18 chapters" → ATTRIBUTED (in context)
❌ "composed around 200 BCE" → NOT ATTRIBUTED (not in context)
❌ "teaches path of dharma" → NOT ATTRIBUTED (not in context)

Overall: PARTIALLY ATTRIBUTED (33% attributed)
```

---

## Detecting Unattributed Claims

### Step 1: Claim Extraction

Break response into atomic factual claims:

**Response:**
> "Traditional carbonara, originating from Rome, uses guanciale instead of bacon,
> which provides a richer flavor. The dish became popular after World War II."

**Extracted Claims:**
1. "Traditional carbonara originates from Rome"
2. "Carbonara uses guanciale instead of bacon"
3. "Guanciale provides a richer flavor than bacon"
4. "The dish became popular after World War II"

### Step 2: Claim Classification

For each claim, determine:
- **ATTRIBUTED:** Directly supported by retrieved context
- **UNATTRIBUTED:** Not found in retrieved context
- **CONTRADICTED:** Contradicts retrieved context
- **AMBIGUOUS:** Unclear if supported

### Step 3: Evidence Matching

For attributed claims, identify supporting passages:

```python
Claim: "Carbonara uses guanciale instead of bacon"
Evidence: [Doc 1, Sentence 1] "Traditional carbonara uses guanciale
(cured pork jowl), not bacon."
Match Type: EXACT_MATCH
```

### Automated Detection Approaches

#### Approach 1: Lexical Matching (Fast, Brittle)
```python
def check_attribution_lexical(claim: str, context: list[str]) -> bool:
    # Tokenize claim into keywords
    keywords = extract_keywords(claim)

    # Check if majority of keywords appear in context
    for doc in context:
        if overlap_ratio(keywords, doc) > 0.7:
            return True
    return False
```

**Pros:** Fast, no API calls
**Cons:** Misses paraphrasing, synonyms, negations

#### Approach 2: Semantic Similarity (Better)
```python
def check_attribution_semantic(claim: str, context: list[str]) -> bool:
    claim_embedding = get_embedding(claim)

    for doc in context:
        doc_embedding = get_embedding(doc)
        similarity = cosine_similarity(claim_embedding, doc_embedding)

        if similarity > 0.85:  # High threshold for attribution
            return True
    return False
```

**Pros:** Handles paraphrasing, semantic equivalence
**Cons:** False positives for related but different claims

#### Approach 3: LLM-as-Judge (Most Accurate)
```python
def check_attribution_llm(claim: str, context: list[str]) -> dict:
    prompt = f"""
Given the following context documents:
{format_context(context)}

Determine if this claim is attributed to the context:
Claim: "{claim}"

Answer:
- YES if the claim is directly supported by the context
- NO if the claim is not found in the context
- CONTRADICTED if the claim contradicts the context

Provide:
1. Verdict: YES/NO/CONTRADICTED
2. Evidence: Quote the supporting passage (if YES)
3. Explanation: Brief reasoning
"""

    response = llm_call(prompt)
    return parse_attribution_response(response)
```

**Pros:** Handles nuance, multi-hop reasoning, partial matches
**Cons:** Expensive, slower, requires prompt engineering

---

## Claim Extraction and Matching

### Claim Extraction Techniques

#### 1. Sentence Splitting (Naive)
```python
claims = response.split('.')  # Too coarse
```
**Problem:** Multiple claims per sentence, incomplete claims

#### 2. Dependency Parsing (Better)
```python
import spacy
nlp = spacy.load("en_core_web_sm")

def extract_claims_spacy(text: str) -> list[str]:
    doc = nlp(text)
    claims = []

    for sent in doc.sents:
        # Extract subject-verb-object triples
        for token in sent:
            if token.dep_ == "ROOT":  # Main verb
                subject = [t for t in token.children if t.dep_ == "nsubj"]
                obj = [t for t in token.children if t.dep_ in ["dobj", "attr"]]

                if subject and obj:
                    claim = f"{subject[0].text} {token.text} {obj[0].text}"
                    claims.append(claim)

    return claims
```

#### 3. LLM-Based Extraction (Most Robust)
```python
def extract_claims_llm(response: str) -> list[str]:
    prompt = f"""
Extract all factual claims from this response.
Each claim should be:
- Atomic (one fact per claim)
- Self-contained (understandable without context)
- Falsifiable (can be verified)

Response: "{response}"

Output as JSON list: ["claim1", "claim2", ...]
"""

    return json.loads(llm_call(prompt))
```

**Example:**

Input:
> "The Bhagavad Gita, a 700-verse Hindu scripture, is part of the
> Mahabharata and presents a conversation between Prince Arjuna
> and Lord Krishna on the battlefield of Kurukshetra."

Extracted Claims:
1. "The Bhagavad Gita is a Hindu scripture"
2. "The Bhagavad Gita has 700 verses"
3. "The Bhagavad Gita is part of the Mahabharata"
4. "The Bhagavad Gita presents a conversation between Arjuna and Krishna"
5. "Arjuna is a prince"
6. "The conversation occurs on the battlefield of Kurukshetra"

### Matching Claims to Evidence

Once claims are extracted, match each to context passages:

```python
def match_claim_to_evidence(
    claim: str,
    context_docs: list[str],
    threshold: float = 0.85
) -> dict:
    """
    Match claim to supporting evidence in context.

    Returns:
        {
            "attributed": bool,
            "evidence_doc_id": int or None,
            "evidence_text": str or None,
            "confidence": float,
            "match_type": "EXACT" | "PARAPHRASE" | "INFERENCE" | "NONE"
        }
    """
    best_match = {"confidence": 0.0, "match_type": "NONE"}

    for i, doc in enumerate(context_docs):
        # Check exact match first
        if claim.lower() in doc.lower():
            return {
                "attributed": True,
                "evidence_doc_id": i,
                "evidence_text": doc,
                "confidence": 1.0,
                "match_type": "EXACT"
            }

        # Check semantic similarity
        similarity = semantic_similarity(claim, doc)
        if similarity > threshold and similarity > best_match["confidence"]:
            best_match = {
                "attributed": True,
                "evidence_doc_id": i,
                "evidence_text": doc,
                "confidence": similarity,
                "match_type": "PARAPHRASE"
            }

    if best_match["confidence"] >= threshold:
        return best_match
    else:
        return {"attributed": False, "match_type": "NONE"}
```

---

## Measuring Attribution Rate

### Metric 1: Claim-Level Attribution Rate

**Formula:**
```
Attribution Rate = (# Attributed Claims) / (Total # Claims)
```

**Example:**
```
Response: "Traditional carbonara uses eggs, cheese, guanciale, and pepper.
The dish was invented in 1944 by Italian chef Renato Gualandi."

Extracted Claims:
1. "Carbonara uses eggs" → ATTRIBUTED
2. "Carbonara uses cheese" → ATTRIBUTED
3. "Carbonara uses guanciale" → ATTRIBUTED
4. "Carbonara uses pepper" → ATTRIBUTED
5. "Invented in 1944" → NOT ATTRIBUTED
6. "Invented by Renato Gualandi" → NOT ATTRIBUTED

Attribution Rate = 4/6 = 66.7%
```

### Metric 2: Weighted Attribution Score

Weights claims by importance:

```python
def weighted_attribution_score(claims: list[dict]) -> float:
    """
    Calculate weighted attribution score.

    claims: [
        {"text": str, "attributed": bool, "importance": float},
        ...
    ]
    """
    total_weight = sum(c["importance"] for c in claims)
    attributed_weight = sum(
        c["importance"] for c in claims if c["attributed"]
    )

    return attributed_weight / total_weight if total_weight > 0 else 0.0
```

**Use Case:** Prioritize key facts over minor details

### Metric 3: Document Coverage

How many retrieved documents are actually used?

```python
def document_coverage(claims: list[dict], num_docs: int) -> float:
    """
    Measure how many retrieved docs contributed to attributed claims.

    Returns fraction of docs with at least one attributed claim.
    """
    used_docs = set(
        claim["evidence_doc_id"]
        for claim in claims
        if claim["attributed"]
    )

    return len(used_docs) / num_docs if num_docs > 0 else 0.0
```

**Interpretation:**
- **Low coverage (< 30%):** LLM ignoring most retrieved docs
- **Medium coverage (30-70%):** Selective document usage
- **High coverage (> 70%):** LLM synthesizing across all docs

### Metric 4: Attribution Precision and Recall

**Precision:** Of claims LLM makes, how many are attributed?
```
Precision = (True Attributed Claims) / (Total Claims)
```

**Recall:** Of facts in context, how many appear in response?
```
Recall = (Attributed Claims) / (All Facts in Context)
```

**Example:**
```
Context Facts: [A, B, C, D, E]  (5 facts in retrieved docs)
Response Claims: [A, B, F, G]   (4 claims in LLM response)
Attributed: [A, B]              (2 claims with evidence)

Precision = 2/4 = 50%  (Half of LLM's claims are attributed)
Recall = 2/5 = 40%     (LLM only used 2 of 5 available facts)
```

---

## Practical Implementation

### Building an Attribution Detector

```python
from typing import List, Dict, Any
import openai

class AttributionDetector:
    def __init__(self, model: str = "gpt-4o-mini"):
        self.model = model

    def extract_claims(self, response: str) -> List[str]:
        """Extract atomic factual claims from LLM response."""
        prompt = f"""
Extract all factual claims from this response.
Rules:
- One claim per line
- Atomic (single fact)
- Self-contained
- No opinions/subjective statements

Response: "{response}"

Claims:
"""
        result = openai.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.0
        )

        claims_text = result.choices[0].message.content
        return [c.strip() for c in claims_text.strip().split('\n') if c.strip()]

    def verify_attribution(
        self,
        claims: List[str],
        context: List[str]
    ) -> Dict[str, Any]:
        """Verify which claims are attributed to context."""
        results = []

        for claim in claims:
            prompt = f"""
Context Documents:
{self._format_context(context)}

Claim: "{claim}"

Is this claim attributed to the context? Answer:
- ATTRIBUTED: Claim is directly supported by context
- UNATTRIBUTED: Claim not found in context
- CONTRADICTED: Claim contradicts context

Respond in JSON:
{{
    "verdict": "ATTRIBUTED" | "UNATTRIBUTED" | "CONTRADICTED",
    "evidence": "quote from context" or null,
    "confidence": 0.0-1.0
}}
"""

            result = openai.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.0
            )

            attribution = json.loads(result.choices[0].message.content)
            results.append({
                "claim": claim,
                **attribution
            })

        return {
            "claims": results,
            "attribution_rate": self._calculate_rate(results),
            "num_claims": len(claims),
            "num_attributed": sum(1 for r in results if r["verdict"] == "ATTRIBUTED")
        }

    def _format_context(self, docs: List[str]) -> str:
        return "\n\n".join(f"[Doc {i+1}]: {doc}" for i, doc in enumerate(docs))

    def _calculate_rate(self, results: List[dict]) -> float:
        if not results:
            return 0.0
        attributed = sum(1 for r in results if r["verdict"] == "ATTRIBUTED")
        return attributed / len(results)
```

### Usage Example

```python
detector = AttributionDetector()

query = "What ingredients are in carbonara?"
retrieved_context = [
    "Traditional carbonara uses eggs, Pecorino Romano, guanciale, and pepper.",
    "Do not add cream to authentic carbonara."
]
llm_response = """
Carbonara is made with eggs, Pecorino cheese, guanciale (Italian cured pork),
and black pepper. The dish originated in Rome in the 1940s and does not
traditionally include cream.
"""

# Step 1: Extract claims
claims = detector.extract_claims(llm_response)
print(f"Extracted {len(claims)} claims")

# Step 2: Verify attribution
results = detector.verify_attribution(claims, retrieved_context)

print(f"\nAttribution Rate: {results['attribution_rate']:.1%}")
print(f"Attributed: {results['num_attributed']}/{results['num_claims']} claims\n")

for claim_result in results['claims']:
    print(f"Claim: {claim_result['claim']}")
    print(f"  Verdict: {claim_result['verdict']}")
    if claim_result['evidence']:
        print(f"  Evidence: {claim_result['evidence'][:100]}...")
    print()
```

**Output:**
```
Extracted 5 claims

Attribution Rate: 60.0%
Attributed: 3/5 claims

Claim: Carbonara is made with eggs, Pecorino cheese, guanciale, and pepper
  Verdict: ATTRIBUTED
  Evidence: Traditional carbonara uses eggs, Pecorino Romano, guanciale, and pepper.

Claim: Guanciale is Italian cured pork
  Verdict: UNATTRIBUTED

Claim: The dish originated in Rome in the 1940s
  Verdict: UNATTRIBUTED

Claim: Carbonara does not traditionally include cream
  Verdict: ATTRIBUTED
  Evidence: Do not add cream to authentic carbonara.
```

---

## Common Pitfalls

### Pitfall 1: Over-Strict Attribution

**Problem:** Rejecting paraphrased or inferred claims

```
Context: "Bake at 375°F for 45 minutes."
Response: "Cook in oven at 375 degrees for three-quarters of an hour."

❌ BAD: Mark as UNATTRIBUTED (too strict)
✅ GOOD: Mark as ATTRIBUTED (valid paraphrase)
```

**Solution:** Use semantic similarity, not just exact matching

### Pitfall 2: Ignoring Multi-Hop Reasoning

**Problem:** Missing claims that synthesize multiple documents

```
Context:
[Doc 1]: "Carbonara uses guanciale."
[Doc 2]: "Guanciale is cured pork jowl."

Response: "Carbonara contains cured pork jowl."

❌ BAD: Mark as UNATTRIBUTED (not in any single doc)
✅ GOOD: Mark as ATTRIBUTED (valid inference from Doc1 + Doc2)
```

**Solution:** Check for multi-document support, not just single-document

### Pitfall 3: False Attribution from Hallucinated Citations

**Problem:** LLM adds citation markers to incorrect information

```
Context: "Recipe uses 2 cups flour."
Response: "Use 3 cups flour (Source: Doc 1)."

❌ BAD: Accept as ATTRIBUTED because it has citation marker
✅ GOOD: Mark as UNATTRIBUTED/CONTRADICTED (wrong quantity)
```

**Solution:** Verify claim content matches source, not just presence of citation marker

### Pitfall 4: Confusing Attribution with Correctness

**Problem:** Marking factually true claims as attributed when they're not in context

```
Query: "What is the capital of France?"
Context: [irrelevant recipe documents]
Response: "Paris is the capital of France."

❌ BAD: Mark as ATTRIBUTED because it's factually true
✅ GOOD: Mark as UNATTRIBUTED (not in retrieved context)
```

**Solution:** Attribution is about **provenance** (where did info come from?), not correctness

### Pitfall 5: Not Measuring Partial Attribution

**Problem:** Binary attribution (all-or-nothing) misses partial success

```
Response with 8/10 claims attributed:

❌ BAD: Mark entire response as FAIL
✅ GOOD: Report 80% attribution rate, identify unattributed claims
```

**Solution:** Calculate attribution rate per claim, report fine-grained metrics

---

## Real-World Applications

### Use Case 1: Medical Q&A Systems

**Requirement:** Every medical claim must trace to peer-reviewed sources

```python
# High-stakes domain requires >95% attribution
results = detector.verify_attribution(claims, medical_papers)

if results['attribution_rate'] < 0.95:
    # Reject response, flag for human review
    return {"status": "REJECTED", "reason": "Insufficient attribution"}
```

### Use Case 2: Legal Document Analysis

**Requirement:** Responses cite specific legal precedents

```python
# Extract claims and verify against case law
for claim in claims:
    if claim['verdict'] != 'ATTRIBUTED':
        # Require attorney to manually verify claim
        flag_for_review(claim)
```

### Use Case 3: Customer Support Chatbots

**Requirement:** Answers derive from company knowledge base

```python
# Monitor attribution rate over time
if weekly_attribution_rate < 0.75:
    # Alert: chatbot is relying too much on parametric knowledge
    send_alert("Low attribution rate: Update knowledge base")
```

### Use Case 4: Educational Tutoring Systems

**Requirement:** Explanations reference curriculum materials

```python
# Track which curriculum documents are used
coverage = document_coverage(claims, curriculum_docs)

if coverage < 0.5:
    # Tutor is not using provided materials effectively
    log_warning("Low curriculum coverage")
```

---

## Practical Exercise

**Task:** Implement an attribution evaluator for the recipe chatbot.

**Dataset:** Use `homeworks/hw4/data/processed_recipes.json`

**Steps:**
1. Generate 20 recipe Q&A pairs with retrieval
2. Extract claims from each LLM response
3. Verify attribution against retrieved recipe documents
4. Calculate attribution rate across all 20 responses
5. Identify common patterns in unattributed claims

**Success Criteria:**
- Attribution rate > 80% indicates good RAG system
- Low attribution rate (< 60%) suggests:
  - Poor retrieval (irrelevant docs)
  - LLM over-relying on parametric knowledge
  - Prompt needs explicit "use only provided context" instruction

**Code Starter:**
```python
from backend.rag_generation_eval import AttributionDetector
import json

# Load recipes
with open("homeworks/hw4/data/processed_recipes.json") as f:
    recipes = json.load(f)

# Initialize detector
detector = AttributionDetector()

# Evaluate 20 Q&A pairs
results = []
for i in range(20):
    query = generate_query(recipes[i])
    retrieved_docs = retrieve_recipes(query, k=3)
    response = llm_generate(query, retrieved_docs)

    # Check attribution
    claims = detector.extract_claims(response)
    attribution = detector.verify_attribution(claims, retrieved_docs)

    results.append(attribution)

# Calculate aggregate metrics
avg_attribution_rate = sum(r['attribution_rate'] for r in results) / len(results)
print(f"Average Attribution Rate: {avg_attribution_rate:.1%}")
```

---

## Summary

**Key Takeaways:**

1. **Attribution ≠ Correctness:** A response can be factually true but unattributed (not in context)

2. **Claim Extraction is Hard:** Use LLM-based extraction for best results, handle atomic claims

3. **Matching Requires Semantic Understanding:** Exact string matching fails on paraphrasing and inference

4. **Measure Fine-Grained Attribution:** Report per-claim attribution rate, not binary pass/fail

5. **Attribution Failures Indicate System Problems:**
   - Low attribution → Poor retrieval or over-reliance on parametric memory
   - High attribution → Good RAG system grounding

6. **Domain-Specific Thresholds:**
   - High-stakes (medical, legal): >95% attribution required
   - General Q&A: >80% attribution acceptable
   - Casual chatbots: >60% attribution sufficient

**Next Steps:**
- [Hallucination Detection in RAG](./hallucination_detection_rag.md): Learn to distinguish intrinsic vs extrinsic hallucinations
- [End-to-End RAG Evaluation](./end_to_end_rag_eval.md): Combine retrieval + generation metrics
- [Interactive Notebook](./attribution_detection.ipynb): Hands-on attribution evaluation on Bhagavad Gita Q&A

---

**Further Reading:**

- [Anthropic: Evaluating RAG Systems](https://www.anthropic.com/research/evaluating-rag)
- [RAGAS Framework: Attribution Metrics](https://docs.ragas.io/en/latest/concepts/metrics/attribution.html)
- [Google: Attributed QA Systems](https://ai.google/research/pubs/pub50836)
- [MS MARCO Attribution Dataset](https://microsoft.github.io/msmarco/)

---

*Tutorial maintained as part of [Lesson 13: RAG Generation & Attribution](./TUTORIAL_INDEX.md)*
