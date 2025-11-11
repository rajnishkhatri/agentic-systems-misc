# Context Quality Evaluation: Chunking and Contextual Retrieval

**Reading Time**: 20-25 minutes
**Prerequisites**: `embedding_based_retrieval.md`, `hybrid_search_strategies.md`
**Learning Objective**: Optimize chunking strategies and evaluate context quality with AI judges

---

## Introduction

Retrieval quality depends not just on the **search algorithm** (BM25, semantic, hybrid), but also on **how documents are chunked** before indexing.

**Chunking** = Breaking large documents into smaller segments for retrieval.

**Why it matters**:
- **Too large chunks** (1000+ tokens): Contain irrelevant information, reduce precision
- **Too small chunks** (50 tokens): Lose context, increase false positives
- **Poor boundaries** (mid-sentence): Break semantic coherence

This tutorial covers:
1. Context precision vs. context recall
2. Chunking strategies (character, sentence, paragraph, recursive, semantic)
3. Contextual retrieval (Anthropic's chunk augmentation)
4. Evaluating chunking with AI judges

---

## Context Precision vs Context Recall

For RAG systems, we evaluate retrieval with two metrics:

### Context Precision

**Definition**: % of retrieved chunks that are relevant to the query.

```
Context Precision = (# relevant chunks in top-k) / k
```

**Example**:
- Query: "What is karma yoga?"
- Retrieved 5 chunks: [A, B, C, D, E]
- Relevant: A, B, D
- **Context Precision = 3/5 = 0.60**

**When it matters**: High-precision retrieval reduces noise in LLM context window (fewer irrelevant chunks = better generation quality).

### Context Recall

**Definition**: % of all relevant chunks that were retrieved.

```
Context Recall = (# relevant chunks retrieved) / (# total relevant chunks in corpus)
```

**Example**:
- Query: "What is karma yoga?"
- Total relevant chunks in corpus: 8
- Retrieved 5 chunks, 3 relevant: A, B, D
- **Context Recall = 3/8 = 0.375**

**When it matters**: High-recall retrieval ensures all relevant information is available to the LLM (no missing context).

### Trade-off

| Metric | Optimized By | Risk |
|--------|-------------|------|
| **Precision** | Smaller k, stricter thresholds | May miss relevant info (low recall) |
| **Recall** | Larger k, more lenient thresholds | Too much noise (low precision) |

**Goal**: Balance both with optimal chunking strategy and hybrid search.

---

## Chunking Strategy Impact on Retrieval

### Problem: Document Length Variability

**Recipe corpus example**:
- Short recipe: 200 tokens (1 chunk)
- Long recipe: 1500 tokens (needs splitting)
- Bhagavad Gita verse: 50 tokens (too small to split?)

**Challenge**: One-size-fits-all chunking (e.g., "500 tokens per chunk") may not work for all documents.

---

## Five Chunking Strategies

### 1. Fixed Character Length

**Method**: Split every N characters (e.g., 500 characters).

```python
def chunk_by_characters(text: str, chunk_size: int = 500) -> list[str]:
    chunks = []
    for i in range(0, len(text), chunk_size):
        chunks.append(text[i:i + chunk_size])
    return chunks
```

**Pros**: Simple, fast
**Cons**: Breaks mid-sentence, mid-word (destroys semantic coherence)

**Example**:
```
Text: "The Bhagavad Gita teaches dharma. Karma yoga is the path of selfless..."
Chunk 1: "The Bhagavad Gita teaches dharma. Karma yoga is the path of sel"
Chunk 2: "fless action without attachment to results."
```

❌ **Not recommended** (except for testing)

---

### 2. Sentence-Based Chunking

**Method**: Split at sentence boundaries, combine until reaching token limit.

```python
import nltk
nltk.download('punkt')

def chunk_by_sentences(text: str, max_tokens: int = 200) -> list[str]:
    sentences = nltk.sent_tokenize(text)
    chunks = []
    current_chunk = []
    current_tokens = 0

    for sentence in sentences:
        sentence_tokens = len(sentence.split())
        if current_tokens + sentence_tokens > max_tokens:
            chunks.append(" ".join(current_chunk))
            current_chunk = [sentence]
            current_tokens = sentence_tokens
        else:
            current_chunk.append(sentence)
            current_tokens += sentence_tokens

    if current_chunk:
        chunks.append(" ".join(current_chunk))

    return chunks
```

**Pros**: Preserves sentence boundaries (semantic coherence)
**Cons**: Sentences vary in length (some chunks may be too short or long)

**Best for**: General-purpose documents (recipes, articles)

---

### 3. Paragraph-Based Chunking

**Method**: Split at paragraph boundaries (`\n\n`), treat each paragraph as a chunk.

```python
def chunk_by_paragraphs(text: str) -> list[str]:
    paragraphs = text.split("\n\n")
    return [p.strip() for p in paragraphs if p.strip()]
```

**Pros**: Natural semantic boundaries (each paragraph = one idea)
**Cons**: Paragraphs vary widely in length (some too short, some too long)

**Best for**: Structured documents (Bhagavad Gita verses with commentaries, technical docs with headings)

---

### 4. Recursive Chunking (LangChain Method)

**Method**: Recursively split using multiple delimiters in order of preference.

```python
def chunk_recursive(text: str, max_tokens: int = 200, separators: list[str] = None) -> list[str]:
    if separators is None:
        separators = ["\n\n", "\n", ". ", " ", ""]  # Paragraph → sentence → word → char

    for separator in separators:
        if separator in text:
            parts = text.split(separator)
            chunks = []
            for part in parts:
                if len(part.split()) <= max_tokens:
                    chunks.append(part)
                else:
                    # Recursively split with next separator
                    chunks.extend(chunk_recursive(part, max_tokens, separators[separators.index(separator)+1:]))
            return chunks

    # Base case: return single chunk if no separators left
    return [text]
```

**Pros**: Balances semantic boundaries with size constraints
**Cons**: More complex implementation

**Best for**: Mixed content (long documents with paragraphs, lists, code blocks)

---

### 5. Semantic Chunking (AI-Powered)

**Method**: Use embeddings to detect topic shifts, split at boundaries.

```python
from openai import OpenAI
import numpy as np

client = OpenAI()

def chunk_semantic(text: str, threshold: float = 0.5) -> list[str]:
    sentences = nltk.sent_tokenize(text)

    # Embed all sentences
    embeddings = []
    for sentence in sentences:
        response = client.embeddings.create(model="text-embedding-3-small", input=sentence)
        embeddings.append(response.data[0].embedding)

    # Compute cosine similarity between adjacent sentences
    chunks = []
    current_chunk = [sentences[0]]

    for i in range(1, len(sentences)):
        similarity = np.dot(embeddings[i-1], embeddings[i]) / (
            np.linalg.norm(embeddings[i-1]) * np.linalg.norm(embeddings[i])
        )

        if similarity < threshold:  # Topic shift detected
            chunks.append(" ".join(current_chunk))
            current_chunk = [sentences[i]]
        else:
            current_chunk.append(sentences[i])

    if current_chunk:
        chunks.append(" ".join(current_chunk))

    return chunks
```

**Pros**: Most semantically coherent chunks (topic-aware)
**Cons**: Expensive (requires embedding every sentence), slower

**Best for**: Long documents where topic coherence is critical (research papers, legal docs)

---

## Chunking Strategy Comparison

| Strategy | Semantic Coherence | Cost | Speed | Best Use Case |
|----------|-------------------|------|-------|---------------|
| **Character** | ❌ Poor | $0 | Fast | Testing only |
| **Sentence** | ✅ Good | $0 | Fast | General documents |
| **Paragraph** | ✅ Excellent | $0 | Fast | Structured docs |
| **Recursive** | ✅ Good | $0 | Medium | Mixed content |
| **Semantic** | ✅✅ Excellent | $$$ | Slow | Critical applications |

**Recommendation for this course**: Use **sentence-based** for recipes, **paragraph-based** for Bhagavad Gita verses.

---

## Contextual Retrieval (Anthropic's Chunk Augmentation)

### Problem: Lost Context in Chunks

When a document is chunked, each chunk loses **document-level context**.

**Example**:
```
Original document: "Bhagavad Gita, Chapter 2, Verse 47:
'You have a right to perform your duty, but not to the fruits of action.'"

Chunk (after splitting): "'You have a right to perform your duty, but not to the fruits of action.'"
```

❌ **Problem**: The chunk doesn't mention it's from the Bhagavad Gita, Chapter 2, Verse 47.

If a user queries "What does the Gita say about duty?", the chunk may not match well because "Gita" isn't in the text.

### Solution: Chunk Augmentation

**Prepend context** to each chunk using LLM to generate a summary.

```python
from openai import OpenAI

client = OpenAI()

def augment_chunk(chunk: str, document_context: str) -> str:
    """
    Augment chunk with document-level context.

    Args:
        chunk: The text chunk to augment
        document_context: Document metadata (title, chapter, source)

    Returns:
        Augmented chunk with prepended context
    """
    prompt = f"""
    Document context: {document_context}

    Chunk: {chunk}

    Task: Prepend a brief 1-sentence context to the chunk that situates it within the document.

    Example:
    Document context: "Bhagavad Gita, Chapter 2 (Sankhya Yoga)"
    Chunk: "You have a right to perform your duty, but not to the fruits of action."
    Output: "In the Bhagavad Gita Chapter 2, verse 47 states: You have a right to perform your duty, but not to the fruits of action."

    Output the augmented chunk:
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )

    return response.choices[0].message.content.strip()
```

**Example output**:
```
"In the Bhagavad Gita Chapter 2, verse 47 states: You have a right to perform your duty, but not to the fruits of action."
```

### Benefits

✅ **Better retrieval**: Query "What does the Gita say about duty?" now matches "Bhagavad Gita" in augmented chunk
✅ **Better generation**: LLM has more context to generate accurate response
✅ **Source citation**: Easier to cite "Chapter 2, Verse 47" in response

### Cost

**For 10,000 chunks, 50 tokens each, using GPT-4o-mini**:
- Input: 10,000 × (50 chunk + 20 context) = 700K tokens
- Output: 10,000 × 60 tokens = 600K tokens
- **Total cost**: ~$0.10-0.20 (one-time, can cache)

**When to use**: High-stakes retrieval (legal, medical, religious texts) where context is critical.

---

## Overlap Strategies for Chunk Boundaries

### Problem: Information at Chunk Boundaries

If a sentence spans two chunks, it may be split awkwardly.

**Example**:
```
Chunk 1 (ends): "...and Arjuna asked Krishna about his duty"
Chunk 2 (starts): "Krishna replied that one must act without attachment..."
```

If a user queries "What did Krishna tell Arjuna about duty?", Chunk 1 mentions the question but not the answer. Chunk 2 has the answer but no context about the question.

### Solution: Overlapping Chunks

**Add overlap** (e.g., 50 tokens) between adjacent chunks.

```python
def chunk_with_overlap(text: str, chunk_size: int = 200, overlap: int = 50) -> list[str]:
    tokens = text.split()
    chunks = []

    for i in range(0, len(tokens), chunk_size - overlap):
        chunk = " ".join(tokens[i:i + chunk_size])
        chunks.append(chunk)

        if i + chunk_size >= len(tokens):
            break

    return chunks
```

**Example**:
```
Chunk 1: "...and Arjuna asked Krishna about his duty. Krishna replied that one must act..."
Chunk 2: "Krishna replied that one must act without attachment to results..."
```

Now both chunks contain the question-answer transition.

**Overlap size**:
- **Small overlap (20-50 tokens)**: Minimal redundancy, may miss boundary info
- **Large overlap (100-150 tokens)**: Better boundary coverage, but more storage and indexing cost

**Recommendation**: Use **50-token overlap** for sentence-based chunking.

---

## Chunk Size Optimization Experiments

### Methodology

1. **Prepare corpus**: 1000 documents (500 recipes + 500 Gita Q&A)
2. **Create variants**: Chunk sizes [100, 200, 300, 500, 1000 tokens]
3. **Index all variants**: Build separate indices for each chunk size
4. **Evaluate**: Measure Recall@5 on 100 validation queries

### Typical Results

| Chunk Size | Recall@5 | Context Precision | Storage Cost |
|-----------|----------|------------------|-------------|
| **100 tokens** | 0.65 | 0.58 | 1.0x |
| **200 tokens** | **0.78** | **0.71** | 0.5x |
| **300 tokens** | 0.76 | 0.69 | 0.33x |
| **500 tokens** | 0.72 | 0.65 | 0.2x |
| **1000 tokens** | 0.68 | 0.60 | 0.1x |

**Insight**: 200-300 tokens per chunk balances recall, precision, and cost.

**Domain-specific tuning**:
- **Short documents (recipes)**: 150-250 tokens
- **Long documents (research papers)**: 300-500 tokens
- **Verse-based texts (Gita)**: Paragraph-based (natural boundaries, ~100-200 tokens)

---

## Evaluating Chunking with AI Judges

Manual evaluation of chunking strategies is time-consuming. Use **AI judges** to automate.

### Context Precision Judge

**Task**: Given query and retrieved chunks, classify each chunk as RELEVANT or IRRELEVANT.

```python
from openai import OpenAI

client = OpenAI()

def judge_context_precision(query: str, chunks: list[str]) -> dict:
    """
    Evaluate context precision using GPT-4o-mini judge.

    Returns:
        dict with precision score and per-chunk relevance labels
    """
    prompt = f"""
    Query: {query}

    Retrieved Chunks:
    {chr(10).join([f"{i+1}. {chunk}" for i, chunk in enumerate(chunks)])}

    Task: For each chunk, classify as RELEVANT (contains information to answer query) or IRRELEVANT (unrelated).

    Output JSON:
    {{
        "chunk_1": "RELEVANT" or "IRRELEVANT",
        "chunk_2": "RELEVANT" or "IRRELEVANT",
        ...
    }}
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0,
        response_format={"type": "json_object"}
    )

    import json
    labels = json.loads(response.choices[0].message.content)
    relevant_count = sum(1 for v in labels.values() if v == "RELEVANT")
    precision = relevant_count / len(chunks)

    return {"precision": precision, "labels": labels}
```

### Context Recall Judge

**Task**: Given query, retrieved chunks, and ground-truth relevant passages, measure recall.

```python
def judge_context_recall(query: str, retrieved_chunks: list[str], relevant_passages: list[str]) -> float:
    """
    Evaluate context recall: How many relevant passages were retrieved?

    Args:
        query: User query
        retrieved_chunks: Chunks returned by retrieval system
        relevant_passages: Ground-truth relevant passages (from manual annotation)

    Returns:
        Recall score (0-1)
    """
    prompt = f"""
    Query: {query}

    Retrieved Chunks:
    {chr(10).join([f"{i+1}. {chunk}" for i, chunk in enumerate(retrieved_chunks)])}

    Ground-Truth Relevant Passages:
    {chr(10).join([f"{i+1}. {passage}" for i, passage in enumerate(relevant_passages)])}

    Task: Count how many of the ground-truth relevant passages are covered by the retrieved chunks (exact or paraphrased).

    Output JSON:
    {{
        "covered_passages": [list of passage numbers],
        "recall": <number of covered passages> / <total relevant passages>
    }}
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0,
        response_format={"type": "json_object"}
    )

    import json
    result = json.loads(response.choices[0].message.content)
    return result["recall"]
```

### Cost Considerations

**For 100 validation queries, 5 chunks per query**:
- Precision judge: 100 queries × $0.0002 = **$0.02**
- Recall judge: 100 queries × $0.0003 = **$0.03**
- **Total: ~$0.05** (negligible compared to manual evaluation time)

---

## Practical Workflow: Optimizing Chunking for Your Domain

### Step 1: Baseline (Sentence-Based, 200 Tokens)

```python
chunks = chunk_by_sentences(document, max_tokens=200)
```

### Step 2: Evaluate Baseline

```python
recall_at_5 = evaluate_retrieval(chunks, validation_queries)
print(f"Baseline Recall@5: {recall_at_5}")  # e.g., 0.68
```

### Step 3: Test Alternatives

```python
strategies = [
    ("paragraph", chunk_by_paragraphs(document)),
    ("recursive", chunk_recursive(document, max_tokens=200)),
    ("sentence_300", chunk_by_sentences(document, max_tokens=300)),
]

for name, chunks in strategies:
    recall = evaluate_retrieval(chunks, validation_queries)
    print(f"{name} Recall@5: {recall}")
```

### Step 4: Choose Best Strategy

Pick strategy with highest Recall@5 and acceptable precision.

### Step 5: Add Contextual Augmentation (Optional)

```python
augmented_chunks = [augment_chunk(chunk, document_metadata) for chunk in chunks]
```

### Step 6: Validate with AI Judges

```python
for query, relevant_docs in validation_set:
    retrieved = search(query, top_k=5)
    precision = judge_context_precision(query, retrieved)
    recall = judge_context_recall(query, retrieved, relevant_docs)
    print(f"Query: {query}, Precision: {precision}, Recall: {recall}")
```

---

## Common Pitfalls

1. **Using character-based chunking**: Almost always worse than sentence-based (destroys coherence).
2. **Ignoring domain structure**: Use paragraph-based for structured docs (Gita verses, recipes with sections).
3. **Not measuring context precision**: High recall with low precision = noisy LLM context.
4. **Forgetting overlap**: Boundary information may be lost without 50-token overlap.
5. **Over-optimizing on test set**: Use validation set for chunking experiments (avoid overfitting).

---

## Next Steps

1. **Hands-on**: Complete `lesson-12/chunking_optimization.ipynb` to test 5 chunking strategies.
2. **Integration**: Combine optimal chunking with hybrid search (Lesson 12 complete!).
3. **RAG Generation**: Proceed to Lesson 13 to evaluate attribution and hallucination in generated responses.

---

## Key Takeaways

✅ **Context precision** = % relevant chunks retrieved (reduce noise)
✅ **Context recall** = % all relevant info retrieved (avoid missing data)
✅ **Sentence-based chunking** (200-300 tokens) works for most use cases
✅ **Paragraph-based** for structured documents (Gita verses, technical docs)
✅ **Contextual augmentation** (Anthropic method) improves retrieval by 5-10%
✅ **50-token overlap** prevents information loss at chunk boundaries
✅ **AI judges** automate chunking evaluation (precision/recall measurement)

---

## Further Reading

- [Anthropic's Contextual Retrieval](https://www.anthropic.com/news/contextual-retrieval)
- [LangChain Recursive Text Splitter](https://python.langchain.com/docs/modules/data_connection/document_transformers/recursive_text_splitter)
- [LlamaIndex Chunking Strategies](https://docs.llamaindex.ai/en/stable/module_guides/loading/node_parsers/)
- OpenAI Embeddings for semantic chunking
