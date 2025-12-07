# Chunking Strategies Deep Dive

Detailed guidance for selecting and implementing document chunking approaches.

## Strategy Comparison Matrix

| Strategy | Best For | Chunk Size Control | Context Preservation | Implementation Complexity |
|----------|----------|-------------------|---------------------|--------------------------|
| Length-based | Uniform processing | Precise | Poor at boundaries | Low |
| Length + overlap | General purpose | Precise | Good | Low |
| Sentence-based | Instructional content | Approximate | Moderate | Low |
| Paragraph-based | Structured docs | Variable | Good | Low |
| Document-structure | Markdown/HTML | Variable | Excellent | Medium |
| Semantic shift | Diverse topics | Variable | Excellent | High |
| Hierarchical (RAPTOR) | Long documents | Multi-level | Excellent | High |

## Length-Based Chunking

### Simple Fixed Length
```python
def chunk_by_length(text, chunk_size=500):
    return [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]
```

**Problem**: Breaks mid-sentence, mid-word

### With Overlap
```python
def chunk_with_overlap(text, chunk_size=500, overlap=50):
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start = end - overlap
    return chunks
```

**Overlap sizing**: 10-20% of chunk_size typically optimal

## Sentence-Based Chunking

```python
from llama_index.core.node_parser import SentenceSplitter

node_parser = SentenceSplitter(
    chunk_size=200,      # Target size in characters
    chunk_overlap=20     # Overlap between chunks
)
nodes = node_parser.get_nodes_from_documents([document])
```

**Behavior**: Accumulates complete sentences until threshold, respects sentence boundaries

**Best for**: Technical manuals, how-to guides, FAQ content

## Paragraph-Based Chunking

```python
def chunk_by_paragraph(text):
    # Split on double newlines (standard paragraph separator)
    paragraphs = text.split('\n\n')
    return [p.strip() for p in paragraphs if p.strip()]
```

**Best for**: Essays, reports, legal documents with natural paragraph structure

## Document-Structure Chunking

For Markdown:
```python
def chunk_markdown_by_headers(text, level=2):
    """Split on ## headers"""
    pattern = r'^#{' + str(level) + r'}\s+'
    sections = re.split(pattern, text, flags=re.MULTILINE)
    return [s.strip() for s in sections if s.strip()]
```

For HTML:
```python
from bs4 import BeautifulSoup

def chunk_html_by_sections(html):
    soup = BeautifulSoup(html, 'html.parser')
    sections = soup.find_all(['section', 'article', 'div'])
    return [section.get_text() for section in sections]
```

## Semantic Shift Detection

Uses embeddings to find natural topic boundaries:

```python
from sentence_transformers import SentenceTransformer
import numpy as np

def find_semantic_boundaries(sentences, threshold=0.5):
    model = SentenceTransformer('all-MiniLM-L6-v2')
    embeddings = model.encode(sentences)
    
    boundaries = [0]
    for i in range(1, len(embeddings)):
        similarity = np.dot(embeddings[i-1], embeddings[i]) / (
            np.linalg.norm(embeddings[i-1]) * np.linalg.norm(embeddings[i])
        )
        if similarity < threshold:
            boundaries.append(i)
    
    return boundaries
```

**Tuning**: Lower threshold = more chunks, higher = fewer chunks

## Hierarchical Chunking (RAPTOR)

Multi-level abstraction for long documents:

```
Level 0: Original chunks (200-500 chars)
    ↓ cluster similar chunks
Level 1: Cluster summaries (broader topics)
    ↓ cluster summaries
Level 2: Section summaries (high-level themes)
    ↓ cluster
Level 3: Document summary (root)
```

**Retrieval**: Traverse tree from root, following most similar branches

**Use case**: Books, research papers, comprehensive documentation

## Table-Specific Chunking

### Entire Table (Small Tables)
```python
def table_to_text(df):
    return df.to_markdown()
```

### Row-Based (Independent Rows)
```python
def chunk_table_by_rows(df, include_headers=True):
    chunks = []
    headers = df.columns.tolist()
    for _, row in df.iterrows():
        if include_headers:
            chunk = "\n".join([f"{h}: {v}" for h, v in zip(headers, row)])
        else:
            chunk = "\n".join([str(v) for v in row])
        chunks.append(chunk)
    return chunks
```

### Sliding Window (Large Tables)
```python
def chunk_table_sliding(df, window_size=10, overlap=2):
    chunks = []
    for i in range(0, len(df), window_size - overlap):
        window = df.iloc[i:i+window_size]
        chunks.append(window.to_markdown())
    return chunks
```

## Chunk Size Guidelines

| Content Type | Recommended Size | Rationale |
|--------------|------------------|-----------|
| Dense technical | 200-300 chars | High information density |
| Narrative text | 500-800 chars | Maintain story flow |
| Code | Function/class level | Logical units |
| Tables | 5-15 rows | Balance context vs. specificity |
| Q&A pairs | 1 pair per chunk | Natural atomic unit |

## Quality Checks

After chunking, verify:
1. No truncated sentences at boundaries
2. Metadata preserved and attached
3. Overlap working correctly
4. Average chunk size within target range
5. No empty chunks generated
