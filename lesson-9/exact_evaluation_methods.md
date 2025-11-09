# Exact Evaluation Methods: From String Matching to Semantic Similarity

**Reading Time:** 20-25 minutes
**Difficulty:** Intermediate
**Prerequisites:** Understanding of LLM evaluation challenges, basic NLP concepts

---

## Table of Contents

1. [Introduction](#introduction)
2. [Functional Correctness Evaluation](#functional-correctness-evaluation)
3. [Exact Match Evaluation](#exact-match-evaluation)
4. [Lexical Similarity](#lexical-similarity)
5. [Semantic Similarity](#semantic-similarity)
6. [Choosing the Right Evaluation Method](#choosing-the-right-evaluation-method)
7. [Comparison Table](#comparison-table)
8. [Practical Guidelines](#practical-guidelines)

---

## Introduction

When evaluating LLM outputs, we need methods beyond perplexity (which measures internal model confidence). We need to compare **generated text** against **reference text** (ground truth).

This tutorial covers four evaluation families:

1. **Functional correctness:** Does the output achieve its purpose? (e.g., does generated code run?)
2. **Exact match:** Are the strings identical?
3. **Lexical similarity:** Do they share the same words/n-grams? (BLEU, ROUGE, edit distance)
4. **Semantic similarity:** Do they mean the same thing? (embeddings, cosine similarity)

Each method has trade-offs between **strictness**, **cost**, and **semantic understanding**. By the end, you'll know which method to use for your specific task.

---

## Functional Correctness Evaluation

### What is Functional Correctness?

**Definition:** Does the generated output accomplish the intended task when executed?

**Key Insight:** For some tasks, **string matching is irrelevant**—we only care if the output works.

---

### Use Case: Code Generation

**Example Task:** Generate Python code to reverse a list.

**Reference Solution:**
```python
def reverse_list(lst):
    return lst[::-1]
```

**Model Output 1:**
```python
def reverse_list(lst):
    return list(reversed(lst))
```

**Model Output 2:**
```python
def reverse_list(lst):
    result = []
    for i in range(len(lst) - 1, -1, -1):
        result.append(lst[i])
    return result
```

**Exact Match:** Both fail (different strings)
**Functional Correctness:** Both pass (correct behavior)

---

### HumanEval Benchmark

**HumanEval** (OpenAI, 2021) evaluates code generation using functional correctness.

**Methodology:**
1. Provide 164 Python programming problems with docstrings
2. Generate code solutions with the LLM
3. Run unit tests to verify correctness
4. Report **pass@k**: Percentage of problems solved when generating k samples

**pass@k Metric:**
- **pass@1:** Single generation must be correct
- **pass@10:** At least 1 of 10 generations must be correct
- **pass@100:** At least 1 of 100 generations must be correct

**Why pass@k?** Code generation is stochastic—sampling multiple times increases success probability.

**Results (HumanEval):**

| Model | pass@1 | pass@10 | pass@100 |
|-------|--------|---------|----------|
| GPT-3 (175B, 2020) | 0% | 6.5% | - |
| Codex (12B, 2021) | 28.8% | 46.8% | 72.3% |
| GPT-4 (2023) | 67.0% | 82.0% | - |
| Claude 3.5 Sonnet (2024) | 92.0% | - | - |

**Observation:** pass@100 >> pass@1. Sampling multiple times dramatically improves success.

---

### Applying Functional Correctness

**When to use:**
- ✅ Code generation (Python, SQL, Bash)
- ✅ API call generation (verify API executes successfully)
- ✅ Math problem solving (check if final answer is numerically correct)
- ✅ Recipe bot (verify ingredient amounts are valid, steps are executable)

**When NOT to use:**
- ❌ Creative writing (no "correct" output)
- ❌ Summarization (multiple valid summaries)
- ❌ Translation (multiple valid translations)

---

## Exact Match Evaluation

### What is Exact Match?

**Definition:** Do the generated and reference strings match **exactly** (character-by-character)?

**Formula:**
```python
def exact_match(generated: str, reference: str) -> bool:
    return generated == reference
```

**Binary:** Either 100% match or 0% match. No partial credit.

---

### When Exact Match Works

**Use Case 1: Structured Output**

**Task:** Extract dates from text.

**Query:** "The meeting is on March 15, 2025."
**Expected:** "2025-03-15"
**Model Output:** "2025-03-15"
**Exact Match:** ✅ Pass

---

**Use Case 2: Classification**

**Task:** Sentiment classification.

**Query:** "This movie was amazing!"
**Expected:** "positive"
**Model Output:** "positive"
**Exact Match:** ✅ Pass

---

**Use Case 3: Factoid QA**

**Task:** Who wrote "1984"?

**Expected:** "George Orwell"
**Model Output:** "George Orwell"
**Exact Match:** ✅ Pass

---

### When Exact Match Fails

**Problem 1: Formatting Variations**

**Expected:** "George Orwell"
**Model Output:** "george orwell" (lowercase)
**Exact Match:** ❌ Fail (but semantically correct)

**Solution:** Normalize before comparison (lowercase, strip whitespace)

---

**Problem 2: Paraphrasing**

**Expected:** "George Orwell"
**Model Output:** "Eric Arthur Blair" (Orwell's birth name)
**Exact Match:** ❌ Fail (but factually correct)

**Solution:** Use semantic similarity or maintain alias list

---

**Problem 3: Natural Language**

**Task:** Recipe bot query.

**Query:** "Give me a vegan pasta recipe."

**Expected:** "Here's a vegan pasta recipe:\n1. Boil pasta\n2. Add tomato sauce\n..."
**Model Output:** "Sure! Here's a plant-based pasta dish:\n1. Boil the pasta\n2. Toss with marinara sauce\n..."

**Exact Match:** ❌ Fail (but both are valid responses)

**Solution:** Use lexical or semantic similarity

---

### Exact Match Best Practices

**Do:**
1. **Normalize inputs:** Lowercase, strip whitespace, remove punctuation
2. **Test on structured data:** IDs, codes, labels, JSON keys
3. **Use for regression testing:** Ensure refactoring doesn't break known cases

**Don't:**
1. **Apply to natural language:** Too strict for open-ended text
2. **Expect 100% accuracy:** Even humans disagree on "correct" answers
3. **Use alone:** Combine with other metrics

---

## Lexical Similarity

Lexical similarity measures **word-level overlap** without understanding meaning.

### 1. Fuzzy Matching (Edit Distance)

**Definition:** Measure how many character edits (insertions, deletions, substitutions) are needed to transform one string into another.

**Levenshtein Distance:**

Example:
- String 1: "kitten"
- String 2: "sitting"
- Operations: k→s, e→i, insert g (3 edits)
- Levenshtein Distance: 3

**Normalized Similarity:**
```python
similarity = 1 - (edit_distance / max(len(str1), len(str2)))
```

For "kitten" → "sitting":
```
similarity = 1 - (3 / 7) = 0.57 (57% similar)
```

---

**When to Use Fuzzy Matching:**
- ✅ Typo tolerance (user input validation)
- ✅ Name matching ("John Smith" vs "Jon Smith")
- ✅ Ingredient matching ("tomatoe" vs "tomato")

**Threshold Tuning:**
- **> 0.9:** Very similar (minor typos)
- **0.8-0.9:** Moderately similar (abbreviations)
- **< 0.8:** Different words

---

### 2. N-Gram Overlap (BLEU Score)

**BLEU (Bilingual Evaluation Understudy)** measures n-gram overlap between candidate and reference text. Originally designed for machine translation.

**Formula (simplified):**
```
BLEU = BP × exp(Σ w_n × log(precision_n))
```

Where:
- `precision_n` = Proportion of n-grams in candidate that appear in reference
- `w_n` = Weight for n-gram length (typically uniform)
- `BP` = Brevity penalty (penalizes short outputs)

---

**Example:**

**Reference:** "The cat sat on the mat"
**Candidate:** "The cat is on the mat"

**1-gram precision:** 5/6 tokens match (83%)
**2-gram precision:** 3/5 bigrams match (60%)
- Matches: "the cat", "on the", "the mat"
- Misses: "cat is", "is on"

**BLEU-2 Score:** ~0.70 (after geometric mean and brevity penalty)

---

**When to Use BLEU:**
- ✅ Machine translation
- ✅ Text summarization
- ✅ Paraphrase generation
- ✅ Recipe bot (comparing ingredient lists)

**When NOT to Use BLEU:**
- ❌ Creative writing (penalizes novel phrasing)
- ❌ Open-ended QA (many valid answers)
- ❌ Semantic correctness (ignores meaning)

---

**BLEU Limitations:**

**Problem 1: Ignores Semantics**

**Reference:** "The food was not bad"
**Candidate 1:** "The food was not good" (BLEU: 0.75)
**Candidate 2:** "The food was excellent" (BLEU: 0.20)

Candidate 1 has higher BLEU but is semantically further from the reference.

---

**Problem 2: Requires Multiple References**

Single-reference BLEU is unreliable. Best practice: 4+ references per test case.

**Example:**
- Reference 1: "The cat sat on the mat"
- Reference 2: "A cat was sitting on the mat"
- Reference 3: "On the mat sat the cat"
- Reference 4: "The mat had a cat sitting on it"

Model can match any reference, increasing robustness.

---

### 3. ROUGE (Recall-Oriented Understudy for Gisting Evaluation)

**ROUGE** is similar to BLEU but focuses on **recall** (what % of reference n-grams appear in candidate?).

**ROUGE-N:** N-gram recall
**ROUGE-L:** Longest common subsequence
**ROUGE-S:** Skip-bigram overlap

**Use Case:** Summarization (ensure key information is retained).

**BLEU vs ROUGE:**
- **BLEU:** Precision-focused (does candidate contain unnecessary words?)
- **ROUGE:** Recall-focused (does candidate miss important words?)

---

## Semantic Similarity

Semantic similarity measures **meaning equivalence** using embeddings.

### What are Embeddings?

**Embeddings** are dense vector representations of text in high-dimensional space (e.g., 768 or 1536 dimensions).

**Key Property:** Texts with similar meanings have embeddings that are close together.

**Example:**
- "The cat sat on the mat" → [0.23, -0.45, 0.67, ...]
- "A feline rested on the rug" → [0.25, -0.43, 0.69, ...] (close)
- "I like pizza" → [-0.12, 0.78, -0.34, ...] (far)

---

### Cosine Similarity

**Definition:** Measure the angle between two embedding vectors.

**Formula:**
```
cosine_similarity(A, B) = (A · B) / (||A|| × ||B||)
```

Where:
- `A · B` = Dot product of vectors A and B
- `||A||` = Magnitude (L2 norm) of vector A

**Range:** -1.0 (opposite) to 1.0 (identical)

**Typical Values:**
- **0.9-1.0:** Near-duplicates or paraphrases
- **0.7-0.9:** Semantically related (same topic)
- **0.5-0.7:** Loosely related
- **< 0.5:** Unrelated

---

### Example: Recipe Bot Evaluation

**Reference:** "To make vegan pasta, boil pasta and add tomato sauce."
**Candidate 1:** "For plant-based pasta, cook noodles and mix with marinara."
**Candidate 2:** "I recommend chicken parmesan with alfredo sauce."

**Lexical Similarity (BLEU):**
- Candidate 1: 0.15 (few exact matches)
- Candidate 2: 0.10 (also few matches)

**Semantic Similarity (embeddings):**
- Candidate 1: 0.87 (high—same recipe, different words)
- Candidate 2: 0.42 (low—different recipe)

**Winner:** Semantic similarity correctly identifies Candidate 1 as better.

---

### Popular Embedding Models

| Model | Dimensions | Speed | Quality | Cost |
|-------|------------|-------|---------|------|
| OpenAI `text-embedding-3-small` | 1536 | Fast | Good | $0.02/1M tokens |
| OpenAI `text-embedding-3-large` | 3072 | Medium | Excellent | $0.13/1M tokens |
| `sentence-transformers/all-MiniLM-L6-v2` | 384 | Very fast | Good | Free (local) |
| `sentence-transformers/all-mpnet-base-v2` | 768 | Fast | Better | Free (local) |

**Recommendation:**
- **Prototyping:** Use `all-MiniLM-L6-v2` (free, fast, good enough)
- **Production:** Use OpenAI `text-embedding-3-small` (cheap, high quality)
- **Maximum quality:** Use OpenAI `text-embedding-3-large`

---

### BERTScore

**BERTScore** (Zhang et al., 2020) computes token-level semantic similarity using BERT embeddings.

**Method:**
1. Embed each token in reference and candidate
2. Compute pairwise cosine similarity between all token pairs
3. Match each reference token to the most similar candidate token
4. Aggregate with Precision, Recall, F1

**Advantages over BLEU:**
- ✅ Captures paraphrasing ("car" ≈ "vehicle")
- ✅ Handles word order variations
- ✅ Works with single reference

**Disadvantages:**
- ❌ Slower (requires BERT inference)
- ❌ Still doesn't detect factual errors

**Use Case:** Evaluating summarization, translation, paraphrasing.

---

## Choosing the Right Evaluation Method

Use this decision tree to select the appropriate evaluation method:

### Decision Tree

```
START: What kind of task are you evaluating?

├─ Code generation / API calls
│  └─ Use FUNCTIONAL CORRECTNESS (run unit tests)

├─ Structured output (dates, IDs, classifications)
│  └─ Use EXACT MATCH (with normalization)

├─ Factoid QA with short answers
│  ├─ Multiple formats expected? (e.g., "US" vs "United States")
│  │  └─ Use FUZZY MATCH or SEMANTIC SIMILARITY
│  └─ Single format?
│     └─ Use EXACT MATCH

├─ Translation / Summarization
│  ├─ Have multiple references?
│  │  └─ Use BLEU or ROUGE
│  └─ Single reference?
│     └─ Use SEMANTIC SIMILARITY or BERTScore

├─ Open-ended QA / Chatbot
│  └─ Use SEMANTIC SIMILARITY (embeddings + cosine similarity)

├─ Recipe generation
│  ├─ Evaluating ingredient lists?
│  │  └─ Use FUZZY MATCH (handle typos)
│  └─ Evaluating full recipe?
│     └─ Use SEMANTIC SIMILARITY + AI-as-judge (for safety, dietary adherence)

└─ Creative writing
   └─ Use AI-AS-JUDGE or HUMAN EVALUATION
      (No automatic metric captures creativity well)
```

---

## Comparison Table

| Method | Pros | Cons | Use Case | Cost |
|--------|------|------|----------|------|
| **Functional Correctness** | Objective, tests actual purpose | Requires execution environment | Code, API calls, math | Low |
| **Exact Match** | Fast, deterministic, no ML needed | Too strict for natural language | Structured data, labels | Free |
| **Fuzzy Match** | Handles typos, minor variations | Threshold tuning required | Names, ingredients, typos | Free |
| **BLEU** | Industry standard, interpretable | Ignores semantics, needs multiple refs | Translation, summarization | Free |
| **ROUGE** | Recall-focused (catches missing info) | Still ignores semantics | Summarization | Free |
| **Semantic Similarity** | Captures meaning, single reference | Embedding API cost, slower | Open-ended QA, chatbots | $0.02-0.13/1M tokens |
| **BERTScore** | Token-level semantic matching | Slow (BERT inference), complex | Translation, paraphrasing | Medium (local GPU) |
| **AI-as-Judge** | Flexible, multi-dimensional | Expensive, slower, potential bias | Open-ended, safety, creativity | $0.50-5.00/1K evals |

---

## Practical Guidelines

### 1. Start Simple, Scale Up

**Iteration Phase:**
- Use exact match or BLEU for rapid prototyping
- Test on 20-50 examples

**Validation Phase:**
- Add semantic similarity for robustness
- Test on 100-200 examples

**Production Phase:**
- Combine semantic similarity + AI-as-judge
- Monitor on 1% of traffic continuously

---

### 2. Normalize Inputs

**Always normalize before comparison:**
```python
def normalize(text: str) -> str:
    text = text.lower()                  # Lowercase
    text = text.strip()                  # Remove leading/trailing whitespace
    text = re.sub(r'\s+', ' ', text)     # Collapse multiple spaces
    text = re.sub(r'[^\w\s]', '', text)  # Remove punctuation (optional)
    return text
```

**Example:**
- Before: "  Hello,  World!  "
- After: "hello world"

---

### 3. Use Multiple Metrics

**Bad:** Optimize for BLEU score alone → Models learn to game the metric

**Good:** Track multiple metrics:
- BLEU (lexical overlap)
- Semantic similarity (meaning)
- AI-as-judge (safety, helpfulness)
- User feedback (thumbs up/down)

**Example (Recipe Bot Dashboard):**
| Metric | Value |
|--------|-------|
| Exact match | 12% |
| Fuzzy match (threshold=0.8) | 47% |
| Semantic similarity (mean) | 0.81 |
| Dietary adherence (AI-judge) | 94% |
| Safety (AI-judge) | 99% |
| User thumbs up | 87% |

---

### 4. Validate with Human Evaluation

**Ground Truth:** Human evaluation is the gold standard.

**Process:**
1. Sample 100 random test cases
2. Have 3 annotators independently score each output (1-5 scale)
3. Calculate inter-annotator agreement (Krippendorff's alpha)
4. Compare automatic metrics (BLEU, semantic similarity) to human scores
5. Choose the metric that best correlates with human judgment

**Expected Correlation:**
- Exact match: Low correlation (~0.3) for open-ended tasks
- BLEU: Medium correlation (~0.5) for translation
- Semantic similarity: High correlation (~0.7-0.8) for QA

---

### 5. Threshold Tuning

For metrics that produce continuous scores (fuzzy match, semantic similarity), you need to choose a threshold.

**Method:**
1. Label 100 examples as "good" or "bad" (ground truth)
2. Compute metric scores for all 100 examples
3. Plot precision-recall curve
4. Choose threshold based on your priority:
   - **High precision:** Minimize false positives (threshold = 0.9)
   - **High recall:** Minimize false negatives (threshold = 0.7)
   - **Balanced:** F1-optimal threshold (typically ~0.8)

---

## Summary

**Key Takeaways:**

1. **No single metric is perfect**—combine multiple methods
2. **Exact match:** Fast but too strict for natural language
3. **BLEU/ROUGE:** Good for translation/summarization with multiple references
4. **Semantic similarity:** Best for open-ended tasks, captures meaning
5. **Functional correctness:** Essential for code and structured tasks
6. **Always normalize** inputs before comparison
7. **Validate metrics** against human judgment

**Recommended Stack (Recipe Bot):**
- **Regression testing:** Exact match on known Q&A pairs
- **Ingredient matching:** Fuzzy match (Levenshtein)
- **Recipe similarity:** Semantic similarity (OpenAI embeddings)
- **Dietary adherence:** AI-as-judge (Lesson 10)
- **User satisfaction:** Thumbs up/down + A/B testing (Lesson 11)

**Next Steps:**
- **Run notebooks:** `similarity_measurements_tutorial.ipynb` for hands-on practice
- **Read Lesson 10:** Learn AI-as-judge for multi-dimensional evaluation
- **Apply to your project:** Choose and implement appropriate metrics for your use case

---

## Related Tutorials

- [Evaluation Fundamentals](evaluation_fundamentals.md) - Challenges of evaluating foundation models
- [Language Modeling Metrics](language_modeling_metrics.md) - Perplexity and intrinsic quality metrics
- [Similarity Measurements Tutorial (Notebook)](similarity_measurements_tutorial.ipynb) - Implement exact, fuzzy, BLEU, semantic similarity
- [Lesson 10: AI-as-Judge Production Guide](../lesson-10/ai_judge_production_guide.md) - Evaluate subjective criteria beyond similarity
- [HW4: RAG Evaluation](../homeworks/hw4/TUTORIAL_INDEX.md) - Apply retrieval evaluation metrics

---

## References

1. **HumanEval:** Chen et al. (2021). "Evaluating Large Language Models Trained on Code"
2. **BLEU:** Papineni et al. (2002). "BLEU: a Method for Automatic Evaluation of Machine Translation"
3. **ROUGE:** Lin (2004). "ROUGE: A Package for Automatic Evaluation of Summaries"
4. **BERTScore:** Zhang et al. (2020). "BERTScore: Evaluating Text Generation with BERT"
5. **Levenshtein Distance:** Levenshtein (1966). "Binary codes capable of correcting deletions, insertions, and reversals"

---

**Author:** AI Evaluation Course Team
**Last Updated:** 2025-11-09
**Estimated Reading Time:** 22 minutes
