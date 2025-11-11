# Hallucination Detection in RAG Systems

**Reading Time:** 20-25 minutes
**Prerequisites:** [Attribution Evaluation](./attribution_evaluation.md), [Lesson 10: AI-as-Judge](../lesson-10/TUTORIAL_INDEX.md)
**Next Steps:** [End-to-End RAG Evaluation](./end_to_end_rag_eval.md), [Context Utilization Notebook](./context_utilization.ipynb)

---

## Table of Contents

1. [Introduction](#introduction)
2. [What Makes RAG Hallucinations Different?](#what-makes-rag-hallucinations-different)
3. [Taxonomy of RAG Hallucinations](#taxonomy-of-rag-hallucinations)
4. [Intrinsic Hallucinations](#intrinsic-hallucinations)
5. [Extrinsic Hallucinations](#extrinsic-hallucinations)
6. [Context-Aware Detection](#context-aware-detection)
7. [Faithfulness Measurement](#faithfulness-measurement)
8. [Building Hallucination Judges](#building-hallucination-judges)
9. [Mitigation Strategies](#mitigation-strategies)
10. [Real-World Case Studies](#real-world-case-studies)

---

## Introduction

Retrieval-Augmented Generation (RAG) was designed to reduce LLM hallucinations by grounding responses in retrieved documents. However, **RAG systems don't eliminate hallucinations—they transform them**.

In this tutorial, you'll learn:
- How RAG hallucinations differ from standard LLM hallucinations
- The distinction between intrinsic and extrinsic hallucinations
- Techniques for detecting context-aware hallucinations
- How to measure faithfulness to retrieved documents
- Practical approaches to building hallucination detection systems

**Critical Insight:** In RAG systems, **context is both the solution and a new source of failure**. The LLM can hallucinate by:
1. **Contradicting the context** (intrinsic hallucination)
2. **Ignoring the context** (extrinsic hallucination)
3. **Misinterpreting the context** (distortion)

---

## What Makes RAG Hallucinations Different?

### Standard LLM Hallucinations

**Definition:** LLM generates plausible but incorrect information from parametric memory.

**Example:**
```
Query: "Who won the 2024 Nobel Prize in Literature?"
LLM Response: "Kazuo Ishiguro won the 2024 Nobel Prize in Literature."
```

**Problem:** Factually incorrect (Ishiguro won in 2017), but sounds plausible.

**Detection:** External fact-checking against knowledge bases.

---

### RAG Hallucinations

**Definition:** LLM generates information that is inconsistent with or unsupported by the **provided retrieved context**, regardless of factual correctness.

**Example:**
```
Query: "How long should I bake the cake?"

Retrieved Context:
"Preheat oven to 350°F. Bake for 25-30 minutes until a toothpick
inserted in center comes out clean."

RAG Response:
"Bake the cake at 350°F for 45 minutes until golden brown on top."
```

**Problem:** Contradicts context (25-30 min → 45 min), even if 45 min might work in reality.

**Detection:** Compare response to retrieved context, not external knowledge.

---

### Key Differences

| Aspect | Standard Hallucination | RAG Hallucination |
|--------|----------------------|-------------------|
| **Source** | Parametric memory | Context vs parametric conflict |
| **Detection** | External fact-check | Context comparison |
| **Evaluation** | Absolute correctness | Faithfulness to context |
| **Severity** | Always problematic | Depends on context quality |
| **Mitigation** | Better training data | Better retrieval + prompts |

**Unique RAG Challenge:** A response can be:
- **Factually correct but contextually hallucinated** (LLM knows the answer, ignores context)
- **Factually incorrect but contextually faithful** (Context is wrong, LLM follows it)

**Which is worse?** In RAG systems, **contextual hallucination is worse** because:
1. Users trust RAG to cite sources
2. Debugging requires knowing what the LLM actually used
3. Legal/medical domains require provenance, not just correctness

---

## Taxonomy of RAG Hallucinations

### The Three Types

```
┌─────────────────────────────────────────┐
│         RAG Hallucinations              │
├─────────────────────────────────────────┤
│                                         │
│  1. INTRINSIC (Contradicts Context)     │
│     └─> Directly conflicts with docs   │
│                                         │
│  2. EXTRINSIC (Not in Context)          │
│     ├─> UNATTRIBUTED: Info from LLM    │
│     └─> UNSUPPORTED: Plausible but ∅   │
│                                         │
│  3. DISTORTION (Misinterprets Context)  │
│     ├─> OVERSTATEMENT: Too strong      │
│     ├─> UNDERSTATEMENT: Too weak       │
│     └─> CONFLATION: Mixes distinct facts│
│                                         │
└─────────────────────────────────────────┘
```

### Classification Decision Tree

```
Given response claim and context:

Is claim found in context?
├─ YES → Is meaning preserved accurately?
│         ├─ YES → ✅ FAITHFUL
│         └─ NO  → ❌ DISTORTION
│
└─ NO  → Does claim contradict context?
          ├─ YES → ❌ INTRINSIC HALLUCINATION
          └─ NO  → ❌ EXTRINSIC HALLUCINATION
```

---

## Intrinsic Hallucinations

**Definition:** Claims that **directly contradict** information in the retrieved context.

### Examples

#### Example 1: Factual Contradiction

```
Context: "The Bhagavad Gita has 18 chapters."
Response: "The Bhagavad Gita contains 16 chapters."

Type: INTRINSIC (contradicts quantity)
Severity: HIGH (objectively verifiable error)
```

#### Example 2: Negation Error

```
Context: "Traditional carbonara does NOT use cream."
Response: "Authentic carbonara recipes include heavy cream."

Type: INTRINSIC (contradicts negation)
Severity: HIGH (reverses key instruction)
```

#### Example 3: Numerical Mismatch

```
Context: "Bake at 350°F for 25 minutes."
Response: "Set your oven to 400°F and bake for 25 minutes."

Type: INTRINSIC (temperature contradicts context)
Severity: HIGH (could ruin recipe)
```

#### Example 4: Temporal Contradiction

```
Context: "This verse appears in Chapter 2, Verse 47."
Response: "This teaching is found in Chapter 3, Verse 47."

Type: INTRINSIC (wrong chapter reference)
Severity: MEDIUM (misleads user on source location)
```

### Detection Approach: Contradiction Checking

```python
def detect_intrinsic_hallucination(
    response: str,
    context: list[str]
) -> dict:
    """
    Detect contradictions between response and context.

    Returns:
        {
            "has_contradiction": bool,
            "contradicted_claims": list[dict],
            "severity": "HIGH" | "MEDIUM" | "LOW"
        }
    """
    prompt = f"""
You are a contradiction detector. Compare the response to the context.

Context:
{format_context(context)}

Response:
{response}

Identify any claims in the response that CONTRADICT the context.
A contradiction means the response directly conflicts with context
(e.g., different numbers, opposite statements, negations).

Output JSON:
{{
    "contradictions": [
        {{
            "response_claim": "extracted claim from response",
            "context_claim": "contradicted claim from context",
            "contradiction_type": "FACTUAL" | "NUMERICAL" | "NEGATION" | "TEMPORAL",
            "severity": "HIGH" | "MEDIUM" | "LOW"
        }}
    ],
    "has_contradiction": bool
}}
"""

    result = llm_call(prompt, temperature=0.0)
    return json.loads(result)
```

### Why Intrinsic Hallucinations Occur

1. **Poor Context Understanding:** LLM misreads numbers, dates, or negations
2. **Overconfidence in Parametric Memory:** LLM "knows" a different answer and ignores context
3. **Instruction Following Failure:** Prompt doesn't emphasize "only use context"
4. **Context Truncation:** Relevant contradictory info is cut off due to token limits

---

## Extrinsic Hallucinations

**Definition:** Claims that are **not supported by** the retrieved context, but don't contradict it either.

### Examples

#### Example 1: Unsupported Elaboration

```
Context: "The Bhagavad Gita is a Hindu scripture."
Response: "The Bhagavad Gita, composed around 200 BCE, is a Hindu
scripture that teaches the path of dharma and was part of the oral
tradition before being written down."

Extrinsic Claims:
- "composed around 200 BCE" → NOT in context
- "teaches the path of dharma" → NOT in context
- "oral tradition" → NOT in context

Type: EXTRINSIC (plausible but unsupported)
Severity: MEDIUM (may be factually correct, but breaks RAG contract)
```

#### Example 2: Background Information

```
Context: "Carbonara uses guanciale, eggs, Pecorino Romano, and pepper."
Response: "Carbonara, a classic Roman pasta dish, uses guanciale
(which comes from pork jowl), eggs, Pecorino Romano, and pepper.
The dish became popular after World War II."

Extrinsic Claims:
- "classic Roman pasta dish" → NOT in context
- "guanciale comes from pork jowl" → NOT in context
- "became popular after WWII" → NOT in context

Type: EXTRINSIC (historical/culinary context not provided)
Severity: LOW (adds helpful context, may be correct)
```

#### Example 3: Inference Beyond Context

```
Context: "Preheat oven to 375°F. Bake for 30 minutes."
Response: "Preheat your oven to 375°F, which is a moderate-high
temperature suitable for baking. Bake for 30 minutes, checking
occasionally to avoid burning."

Extrinsic Claims:
- "moderate-high temperature" → Inference, not in context
- "suitable for baking" → Obvious but not stated
- "checking occasionally to avoid burning" → Not in context

Type: EXTRINSIC (reasonable inferences)
Severity: LOW (helpful additions)
```

### The Extrinsic Hallucination Dilemma

**Question:** Are extrinsic hallucinations always bad?

**Depends on the use case:**

| Use Case | Extrinsic Acceptable? | Reason |
|----------|----------------------|--------|
| **Medical Q&A** | ❌ NO | Must cite sources |
| **Legal Research** | ❌ NO | Provenance required |
| **Customer Support** | ✅ SOMETIMES | Helpful if accurate |
| **Educational Tutoring** | ✅ SOMETIMES | Background ok if clarified |
| **Casual Chatbot** | ✅ YES | User expects knowledge |

**Best Practice:** Distinguish in output:
```
Response:
"Carbonara uses guanciale, eggs, Pecorino, and pepper. [SOURCE: Recipe #123]

*Additional context (not from retrieved documents):*
Carbonara is a Roman dish that became popular after World War II."
```

### Detection Approach: Unsupported Claim Detection

```python
def detect_extrinsic_hallucination(
    response: str,
    context: list[str],
    allow_inferences: bool = False
) -> dict:
    """
    Detect claims in response not supported by context.

    Args:
        response: LLM-generated answer
        context: Retrieved documents
        allow_inferences: If True, accept reasonable inferences

    Returns:
        {
            "has_extrinsic": bool,
            "unsupported_claims": list[str],
            "severity": "HIGH" | "MEDIUM" | "LOW"
        }
    """
    prompt = f"""
Context:
{format_context(context)}

Response:
{response}

Identify claims in the response that are NOT supported by the context.
A claim is unsupported if it cannot be verified from the context.

{"Allow reasonable inferences (e.g., if context says 'bake 30 min', response can say 'takes half an hour')." if allow_inferences else "Do NOT allow inferences. Only accept claims explicitly in context."}

Output JSON:
{{
    "unsupported_claims": [
        {{
            "claim": "specific claim text",
            "reason": "why not supported",
            "severity": "HIGH" | "MEDIUM" | "LOW"
        }}
    ],
    "has_extrinsic": bool
}}
"""

    result = llm_call(prompt, temperature=0.0)
    return json.loads(result)
```

---

## Context-Aware Detection

### The Challenge: Same Response, Different Verdicts

Consider this response:
> "Paris is the capital of France and home to the Eiffel Tower."

**Scenario 1: High-Quality Context**
```
Context: "Paris, the capital of France, is home to the Eiffel Tower."
Verdict: ✅ FAITHFUL (fully supported)
```

**Scenario 2: Partial Context**
```
Context: "Paris is the capital of France."
Verdict: ⚠️ PARTIALLY FAITHFUL (capital ✅, Eiffel Tower ❌)
```

**Scenario 3: Irrelevant Context**
```
Context: "The Louvre Museum is located in Paris."
Verdict: ❌ EXTRINSIC HALLUCINATION (capital claim unsupported)
```

**Lesson:** Hallucination detection must be **context-aware**. The same response has different verdicts depending on what context was provided.

### Context Quality Impacts Detection

| Context Quality | Detection Challenge |
|----------------|-------------------|
| **High-quality, relevant** | Easy: Clear support or contradiction |
| **Partial, incomplete** | Medium: Some claims supported, some not |
| **Low-quality, irrelevant** | Hard: Most claims will be extrinsic |
| **Contradictory docs** | Very Hard: Context itself conflicts |

### Handling Contradictory Context

**Scenario:** Multiple retrieved docs contradict each other.

```
Query: "What is the ideal baking temperature?"

Context:
[Doc 1]: "Bake at 350°F for best results."
[Doc 2]: "Professional bakers use 375°F."
[Doc 3]: "Lower temperatures (325°F) prevent burning."

Response: "Bake at 350°F for best results."
```

**Question:** Is this faithful or hallucinated?

**Answer:** **FAITHFUL to Doc 1**, but:
- Ignores Doc 2 and Doc 3
- Could be seen as **selective attribution**

**Best Practice:** LLM should acknowledge contradictions:
```
Response: "Opinions vary: some sources recommend 350°F (Doc 1),
while others suggest 375°F (Doc 2) or 325°F (Doc 3). For best
results, try 350°F as a middle ground."
```

---

## Faithfulness Measurement

**Faithfulness:** The degree to which a response accurately represents the retrieved context without adding or distorting information.

### Faithfulness Score Formula

```
Faithfulness = (# Faithful Claims) / (Total # Claims)

Where:
- Faithful Claim: Supported by context, no distortion
- Unfaithful Claim: Intrinsic or extrinsic hallucination
```

### Faithfulness vs Attribution

| Metric | Definition | What It Measures |
|--------|-----------|------------------|
| **Attribution Rate** | % of claims with source evidence | Provenance tracking |
| **Faithfulness Score** | % of claims consistent with context | Distortion + hallucination |

**Example:**
```
Context: "Recipe uses 2 cups flour."

Response A: "Use 2 cups flour (Source: Recipe #5)."
- Attribution Rate: 100% (cited)
- Faithfulness: 100% (correct)

Response B: "Use 3 cups flour (Source: Recipe #5)."
- Attribution Rate: 100% (cited)
- Faithfulness: 0% (wrong quantity)

Response C: "Use 2 cups flour."
- Attribution Rate: 0% (no citation)
- Faithfulness: 100% (correct information)
```

**Takeaway:** High attribution rate doesn't guarantee faithfulness (see Response B).

### Measuring Faithfulness

```python
def calculate_faithfulness(
    response: str,
    context: list[str]
) -> dict:
    """
    Calculate faithfulness score: fraction of claims supported by context.

    Returns:
        {
            "faithfulness_score": float,  # 0.0-1.0
            "total_claims": int,
            "faithful_claims": int,
            "unfaithful_claims": list[dict]
        }
    """
    # Step 1: Extract claims
    claims = extract_claims(response)

    # Step 2: Check each claim against context
    results = []
    for claim in claims:
        intrinsic_check = detect_intrinsic_hallucination(claim, context)
        extrinsic_check = detect_extrinsic_hallucination(claim, context)

        is_faithful = (
            not intrinsic_check["has_contradiction"]
            and not extrinsic_check["has_extrinsic"]
        )

        results.append({
            "claim": claim,
            "faithful": is_faithful,
            "issues": {
                "intrinsic": intrinsic_check,
                "extrinsic": extrinsic_check
            }
        })

    # Step 3: Calculate score
    faithful_count = sum(1 for r in results if r["faithful"])
    faithfulness_score = faithful_count / len(claims) if claims else 0.0

    return {
        "faithfulness_score": faithfulness_score,
        "total_claims": len(claims),
        "faithful_claims": faithful_count,
        "unfaithful_claims": [r for r in results if not r["faithful"]]
    }
```

### Faithfulness Thresholds

| Score | Interpretation | Action |
|-------|---------------|--------|
| **> 0.95** | Excellent faithfulness | Production-ready |
| **0.85-0.95** | Good faithfulness | Monitor edge cases |
| **0.70-0.85** | Moderate issues | Improve prompts |
| **< 0.70** | Poor faithfulness | Debug retrieval + generation |

---

## Building Hallucination Judges

### Judge Design Principles

1. **Separate Intrinsic and Extrinsic Detection:** Different prompt patterns
2. **Provide Clear Definitions:** Explain contradiction vs unsupported
3. **Use Chain-of-Thought:** Ask judge to reason before verdict
4. **Request Evidence:** Judge must quote context to justify verdict
5. **Calibrate with Examples:** Few-shot examples improve accuracy

### Intrinsic Hallucination Judge

```python
INTRINSIC_JUDGE_PROMPT = """
You are a contradiction detection expert. Your task is to identify
whether a response CONTRADICTS the provided context.

DEFINITION: A contradiction occurs when the response makes a claim
that directly conflicts with information in the context (e.g.,
different numbers, opposite facts, reversed negations).

Context:
{context}

Response:
{response}

Instructions:
1. Extract all factual claims from the response
2. For each claim, check if it contradicts any statement in context
3. A contradiction is NOT the same as "information not found" -
   it must actively conflict

Output JSON:
{{
    "verdict": "FAITHFUL" | "CONTRADICTED",
    "contradictions": [
        {{
            "response_claim": "claim from response",
            "context_claim": "contradicted claim from context",
            "explanation": "why this is a contradiction"
        }}
    ],
    "confidence": 0.0-1.0
}}

Think step-by-step before answering.
"""

def intrinsic_judge(response: str, context: list[str]) -> dict:
    prompt = INTRINSIC_JUDGE_PROMPT.format(
        context=format_context(context),
        response=response
    )

    result = llm_call(prompt, model="gpt-4o-mini", temperature=0.0)
    return json.loads(result)
```

### Extrinsic Hallucination Judge

```python
EXTRINSIC_JUDGE_PROMPT = """
You are an evidence verification expert. Your task is to determine
if every claim in the response is SUPPORTED by the context.

DEFINITION: A claim is supported if it can be directly verified
from the context (exact quote or clear paraphrase). If a claim
cannot be verified from context, it is EXTRINSIC.

Context:
{context}

Response:
{response}

Instructions:
1. Extract all factual claims from the response
2. For each claim, find supporting evidence in context
3. If no supporting evidence exists, mark as EXTRINSIC
4. Do NOT mark obvious inferences as extrinsic (e.g., "30 minutes"
   and "half an hour" are equivalent)

Output JSON:
{{
    "verdict": "FULLY_SUPPORTED" | "PARTIALLY_SUPPORTED" | "UNSUPPORTED",
    "extrinsic_claims": [
        {{
            "claim": "unsupported claim",
            "reason": "why not in context"
        }}
    ],
    "support_rate": 0.0-1.0,  // fraction of claims supported
    "confidence": 0.0-1.0
}}

Think step-by-step before answering.
"""

def extrinsic_judge(response: str, context: list[str]) -> dict:
    prompt = EXTRINSIC_JUDGE_PROMPT.format(
        context=format_context(context),
        response=response
    )

    result = llm_call(prompt, model="gpt-4o-mini", temperature=0.0)
    return json.loads(result)
```

### Combined Hallucination Detector

```python
class HallucinationDetector:
    def __init__(self, model: str = "gpt-4o-mini"):
        self.model = model

    def detect(self, response: str, context: list[str]) -> dict:
        """
        Comprehensive hallucination detection.

        Returns:
            {
                "has_hallucination": bool,
                "faithfulness_score": float,
                "intrinsic_hallucination": dict,
                "extrinsic_hallucination": dict,
                "overall_verdict": "FAITHFUL" | "MINOR_ISSUES" | "MAJOR_ISSUES"
            }
        """
        # Run both judges
        intrinsic_result = intrinsic_judge(response, context)
        extrinsic_result = extrinsic_judge(response, context)

        # Determine overall verdict
        has_intrinsic = intrinsic_result["verdict"] == "CONTRADICTED"
        has_extrinsic = extrinsic_result["verdict"] != "FULLY_SUPPORTED"

        if has_intrinsic:
            overall = "MAJOR_ISSUES"
        elif has_extrinsic and extrinsic_result["support_rate"] < 0.7:
            overall = "MAJOR_ISSUES"
        elif has_extrinsic and extrinsic_result["support_rate"] < 0.9:
            overall = "MINOR_ISSUES"
        else:
            overall = "FAITHFUL"

        return {
            "has_hallucination": has_intrinsic or has_extrinsic,
            "faithfulness_score": extrinsic_result["support_rate"],
            "intrinsic_hallucination": intrinsic_result,
            "extrinsic_hallucination": extrinsic_result,
            "overall_verdict": overall
        }
```

---

## Mitigation Strategies

### Strategy 1: Prompt Engineering

**Add explicit faithfulness instructions:**

```python
SYSTEM_PROMPT = """
You are a helpful assistant that answers questions using ONLY
the provided context documents.

CRITICAL RULES:
1. Every claim must be supported by the context
2. Do NOT use information from your training data
3. If the context doesn't contain the answer, say "I cannot answer
   this based on the provided documents"
4. Do NOT contradict the context, even if you believe it's incorrect
5. Cite sources: [Doc 1], [Doc 2], etc.

If you are uncertain, say so. Do not guess or hallucinate.
"""
```

### Strategy 2: Constrained Decoding

**Limit generation to phrases in context:**

```python
# Extractive QA: Select span from context
response = extract_answer_span(context, query)

# Abstractive with constraints: Penalize out-of-context tokens
response = generate_with_constraint(
    query,
    context,
    constraint="high_overlap"  # Encourage copying from context
)
```

### Strategy 3: Self-Consistency Checking

**Ask LLM to verify its own response:**

```python
def self_check_hallucination(response: str, context: list[str]) -> dict:
    verification_prompt = f"""
    You previously generated this response:
    "{response}"

    Given this context:
    {format_context(context)}

    Does your response contain any claims NOT supported by the context?
    Be critical. Check for contradictions or unsupported information.

    Output JSON:
    {{
        "has_issues": bool,
        "issues": ["issue 1", "issue 2", ...],
        "corrected_response": "revised response" or null
    }}
    """

    result = llm_call(verification_prompt, temperature=0.0)
    return json.loads(result)
```

### Strategy 4: Retrieval Quality Filtering

**Prevent hallucinations by improving retrieval:**

```python
# Filter low-relevance documents before generation
filtered_docs = [
    doc for doc in retrieved_docs
    if relevance_score(query, doc) > 0.7
]

# Only generate if high-quality context available
if not filtered_docs:
    return "Insufficient information to answer this question."

response = llm_generate(query, filtered_docs)
```

### Strategy 5: Citation-Augmented Generation

**Force LLM to cite sources inline:**

```python
CITATION_PROMPT = """
Answer the question using the provided context. For every factual
claim, add a citation like [1], [2], [3] referring to the context
documents.

Context:
[1]: "Carbonara uses guanciale, eggs, Pecorino, and pepper."
[2]: "Do not add cream to authentic carbonara."

Question: {query}

Answer with inline citations:
"""

# Example output:
# "Traditional carbonara uses guanciale, eggs, Pecorino, and pepper [1],
#  and does not include cream [2]."
```

**Benefit:** Easier to verify claims (check each citation).

---

## Real-World Case Studies

### Case Study 1: Medical Q&A Hallucination

**System:** RAG-based medical chatbot answering patient questions

**Incident:**
```
Query: "What is the recommended dosage of aspirin for heart attack prevention?"

Retrieved Context:
"Low-dose aspirin (75-100mg daily) may be recommended for some patients
at high risk of cardiovascular events."

LLM Response:
"For heart attack prevention, take 325mg of aspirin daily."
```

**Analysis:**
- **Intrinsic Hallucination:** Response (325mg) contradicts context (75-100mg)
- **Severity:** HIGH (incorrect dosage could harm patient)
- **Root Cause:** LLM recalled common OTC aspirin dose (325mg) instead of using context

**Fix:**
- Added explicit constraint: "Use ONLY doses mentioned in context"
- Implemented verification step: Compare all numerical claims
- Added confidence score: Flag if LLM uncertain

**Outcome:** Hallucination rate reduced from 12% to 1.5%

---

### Case Study 2: Legal Document Hallucination

**System:** RAG for legal research (case law retrieval)

**Incident:**
```
Query: "Has the precedent in Roe v. Wade been overturned?"

Retrieved Context:
[2022 case law documents discussing legal implications]

LLM Response:
"Roe v. Wade was overturned in Dobbs v. Jackson (2022), but the
Court also ruled that states must provide exceptions for medical
emergencies and cases of rape or incest."
```

**Analysis:**
- **Extrinsic Hallucination:** Second clause (exceptions requirement) NOT in context
- **Severity:** HIGH (misinforms about legal requirements)
- **Root Cause:** LLM conflated common policy proposals with Court ruling

**Fix:**
- Implemented claim-level citation: Each claim must cite specific doc + paragraph
- Added human-in-the-loop verification for legal conclusions
- Separated factual claims (what Court ruled) from commentary (policy implications)

**Outcome:** All legal claims now require explicit citation, reducing hallucinations by 85%

---

### Case Study 3: Recipe Chatbot Extrinsic Hallucination

**System:** Recipe Q&A with RAG retrieval

**Incident:**
```
Query: "How do I make the sauce for this pasta?"

Retrieved Context:
"Combine 2 tbsp olive oil, 3 cloves garlic (minced), 1 can crushed
tomatoes. Simmer 20 minutes."

LLM Response:
"To make the sauce, sauté minced garlic in olive oil until fragrant,
then add crushed tomatoes and simmer. Season with salt, pepper, and
dried basil for authentic Italian flavor."
```

**Analysis:**
- **Extrinsic Hallucination:** "Season with salt, pepper, and dried basil" NOT in context
- **Severity:** LOW (reasonable addition, likely correct)
- **Root Cause:** LLM added common cooking knowledge

**Decision:** ACCEPTABLE (not all extrinsic hallucinations are bad)

**Approach:**
- Separate attributed facts from helpful suggestions:
  ```
  "Combine 2 tbsp olive oil, 3 cloves garlic (minced), and 1 can
  crushed tomatoes. Simmer 20 minutes. [Source: Recipe]

  *Suggested additions (not from recipe):*
  Season with salt, pepper, and basil for extra flavor."
  ```

**Outcome:** Users appreciate the transparency (93% satisfaction rate)

---

## Practical Exercise

**Task:** Build a hallucination detector for the Bhagavad Gita Q&A system.

**Dataset:** `/Gita/Bhagavad-Gita-QA/English/english.csv`

**Steps:**
1. Load 50 Q&A pairs
2. Retrieve relevant verses for each question
3. Generate LLM responses using RAG
4. Detect intrinsic and extrinsic hallucinations
5. Calculate faithfulness scores
6. Identify common hallucination patterns

**Success Criteria:**
- Faithfulness score > 0.90 (90% of claims faithful)
- Zero intrinsic hallucinations (no contradictions)
- Extrinsic hallucinations < 15% (some background ok)

**Code Starter:**
```python
from backend.rag_generation_eval import HallucinationDetector
import pandas as pd

# Load Gita Q&A
df = pd.read_csv("Gita/Bhagavad-Gita-QA/English/english.csv")

detector = HallucinationDetector()

results = []
for i in range(50):
    query = df.iloc[i]["question"]
    gold_answer = df.iloc[i]["answer"]

    # Retrieve verses
    retrieved_verses = retrieve_verses(query, k=3)

    # Generate RAG response
    rag_response = llm_generate(query, retrieved_verses)

    # Detect hallucinations
    result = detector.detect(rag_response, retrieved_verses)

    results.append({
        "query": query,
        "faithfulness_score": result["faithfulness_score"],
        "verdict": result["overall_verdict"],
        "issues": result
    })

# Analyze results
avg_faithfulness = sum(r["faithfulness_score"] for r in results) / len(results)
print(f"Average Faithfulness: {avg_faithfulness:.1%}")

# Identify patterns
major_issues = [r for r in results if r["verdict"] == "MAJOR_ISSUES"]
print(f"Major Issues: {len(major_issues)} / {len(results)}")
```

---

## Summary

**Key Takeaways:**

1. **RAG Transforms Hallucinations:** Context grounding reduces but doesn't eliminate hallucinations

2. **Two Types Matter Most:**
   - **Intrinsic:** Contradicts context (always bad)
   - **Extrinsic:** Not in context (situational)

3. **Faithfulness ≠ Correctness:** RAG systems prioritize faithfulness to context over absolute correctness

4. **Detection Requires Context Awareness:** Same response can be faithful or hallucinated depending on context quality

5. **Mitigation is Multi-Layered:**
   - Prompt engineering (explicit instructions)
   - Constrained decoding (limit to context)
   - Self-verification (LLM checks itself)
   - Retrieval filtering (better context quality)
   - Citation requirements (force provenance)

6. **Judge Design Matters:** Separate intrinsic and extrinsic judges, use Chain-of-Thought, request evidence

7. **Not All Extrinsic Hallucinations Are Bad:** In casual domains, helpful elaborations are acceptable if transparently labeled

**Next Steps:**
- [End-to-End RAG Evaluation](./end_to_end_rag_eval.md): Combine retrieval + generation metrics
- [Attribution Detection Notebook](./attribution_detection.ipynb): Hands-on claim extraction and verification
- [Context Utilization Notebook](./context_utilization.ipynb): Measure which docs LLM actually uses

---

**Further Reading:**

- [Survey of Hallucination in LLMs](https://arxiv.org/abs/2311.05232)
- [Faithfulness in Abstractive Summarization](https://arxiv.org/abs/2005.00661)
- [RAGAS: RAG Assessment Framework](https://docs.ragas.io/en/latest/concepts/metrics/faithfulness.html)
- [Anthropic: Reducing Hallucinations with Context Grounding](https://www.anthropic.com/research/reducing-hallucinations)

---

*Tutorial maintained as part of [Lesson 13: RAG Generation & Attribution](./TUTORIAL_INDEX.md)*
