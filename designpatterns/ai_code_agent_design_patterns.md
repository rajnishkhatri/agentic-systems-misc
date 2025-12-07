# AI Code Agent Design Patterns
## Extracted from RAG System Architectures for Claude Code & Skill Enhancement

---

## Overview

This document distills design patterns from advanced RAG (Retrieval-Augmented Generation) systems and maps them to AI code agent capabilities. These patterns enhance code understanding, generation, debugging, and autonomous task execution.

---

## Pattern 1: Index-Aware Code Retrieval

### Problem
Code agents struggle when:
- The query uses different terminology than the codebase (e.g., "authentication" vs "OAuth2 flow")
- The answer requires understanding relationships across multiple files
- Fine-grained details are buried in large code chunks
- Holistic interpretation across modules is needed

### Solution Components

#### 1.1 Hypothetical Code Embedding (HyCE)
Generate a hypothetical code snippet or solution structure before searching the codebase.

```python
def create_hypothetical_code(query):
    """Generate what the solution MIGHT look like before searching."""
    prompt = f"""
    For this coding task: {query}
    Generate a plausible code structure/snippet that would solve it.
    Include function signatures, imports, and key logic patterns.
    """
    hypothetical = llm.generate(prompt)
    return search_codebase(hypothetical)  # Match against actual code
```

**Use Cases:**
- Finding implementation patterns when you know the goal but not the API
- Locating similar solutions in unfamiliar codebases
- Bridging between natural language descriptions and code patterns

#### 1.2 Query Expansion for Code Search
Expand queries with domain-specific terminology, aliases, and related concepts.

```python
def expand_code_query(query):
    prompt = f"""
    Expand this code search query with:
    - Common library names for this task
    - Alternative naming conventions (camelCase/snake_case)
    - Related design patterns
    - Framework-specific terminology
    
    Query: {query}
    """
    return llm.expand(prompt)
```

**Example Expansion:**
- Input: "how to handle user login"
- Output: "authentication, OAuth2, JWT, session management, passport.js, auth0, login handler, authenticate middleware, sign_in, user_session"

#### 1.3 Hybrid Code Search
Combine keyword matching (exact function names, imports) with semantic search (intent and meaning).

```python
def hybrid_code_search(query, alpha=0.4):
    """
    alpha=0.0: Pure keyword/AST matching
    alpha=1.0: Pure semantic embedding search
    """
    keyword_results = bm25_search(query)  # Exact matches
    semantic_results = vector_search(embed(query))  # Meaning matches
    return weighted_merge(keyword_results, semantic_results, alpha)
```

**When to Use:**
- `alpha=0.2`: Searching for specific function/class names
- `alpha=0.5`: Finding implementations of a concept
- `alpha=0.8`: Exploring "how does this work" questions

#### 1.4 Code Graph RAG
Use AST (Abstract Syntax Tree) and dependency graphs to retrieve related code.

```python
def graph_code_retrieval(entry_point):
    """
    Given a code chunk, retrieve:
    - Functions it calls
    - Functions that call it
    - Shared dependencies
    - Related test files
    """
    graph = build_dependency_graph(codebase)
    related_nodes = graph.get_neighbors(entry_point, depth=2)
    return expand_context(related_nodes)
```

**Graph Relationships to Index:**
- `imports` → module dependencies
- `calls` → function invocations
- `extends/implements` → class hierarchies
- `tests` → corresponding test files
- `config` → related configuration files

---

## Pattern 2: Code Context Postprocessing

### Problem
Retrieved code chunks may be:
- Similar but not relevant to the actual task
- Containing noise (comments, dead code, boilerplate)
- Ambiguous (multiple functions with same name)
- From conflicting versions or branches

### Solution Components

#### 2.1 Code Relevance Reranking
Score each retrieved chunk on task relevance, not just similarity.

```python
def rerank_code_chunks(query, chunks):
    """Use LLM to score relevance, not just embedding similarity."""
    scored = []
    for chunk in chunks:
        prompt = f"""
        Task: {query}
        Code: {chunk.text}
        
        Score 0-1: How useful is this code for completing the task?
        Consider: Does it solve the problem? Is it the right approach?
        """
        score = llm.score(prompt)
        scored.append((chunk, score))
    return sorted(scored, key=lambda x: x[1], reverse=True)
```

#### 2.2 Code Contextual Compression
Extract only the relevant portions from large files.

```python
def compress_code_context(query, code_file):
    """Extract only task-relevant code sections."""
    prompt = f"""
    Task: {query}
    Full File: {code_file}
    
    Extract ONLY the functions, classes, or sections relevant to this task.
    Preserve imports and type definitions they depend on.
    """
    return llm.extract(prompt)
```

**Benefits:**
- Reduces token usage in context window
- Focuses attention on relevant code
- Removes distracting boilerplate

#### 2.3 Symbol Disambiguation
Detect when retrieved code refers to different entities with the same name.

```python
@dataclass
class DisambiguationResult:
    is_ambiguous: bool
    symbol_name: str
    interpretations: list[str]  # e.g., ["utils.py:parse()", "helpers.py:parse()"]

def disambiguate_symbols(query, chunks):
    """Detect if chunks reference different entities with same name."""
    for i, chunk1 in enumerate(chunks):
        for chunk2 in chunks[i+1:]:
            result = llm.compare(f"""
            Do these code chunks refer to the SAME function/class or DIFFERENT ones?
            Chunk 1: {chunk1}
            Chunk 2: {chunk2}
            """)
            if result.is_ambiguous:
                return ask_clarification(result)
```

#### 2.4 Version/Branch Filtering
Ensure code from the correct version is used.

```python
def filter_by_version(chunks, target_branch="main"):
    """Filter out code from wrong branches or deprecated versions."""
    return [
        chunk for chunk in chunks
        if chunk.metadata.get("branch") == target_branch
        and not chunk.metadata.get("deprecated", False)
    ]
```

---

## Pattern 3: Trustworthy Code Generation

### Problem
Code agents can:
- Generate code that doesn't match the codebase style
- Hallucinate non-existent APIs or methods
- Produce outdated patterns
- Miss critical error handling

### Solution Components

#### 3.1 Out-of-Scope Detection
Recognize when a task is outside the agent's capabilities.

```python
def is_in_scope(query, knowledge_base):
    """
    Check if the codebase contains relevant patterns/APIs for this task.
    """
    signals = {
        "embedding_distance": check_min_similarity(query, knowledge_base),
        "has_related_code": bool(search_codebase(query)),
        "language_supported": detect_language(query) in SUPPORTED_LANGS,
    }
    
    if signals["embedding_distance"] < 0.3:
        return False, "No similar patterns found in codebase"
    return True, None
```

**Responses When Out of Scope:**
- "This codebase doesn't have examples of [X]. Would you like me to suggest an approach?"
- "I don't see [library] in your dependencies. Should I add it?"

#### 3.2 Code Citations
Link generated code to source references.

```python
def generate_with_citations(query, context_chunks):
    """Generate code with inline citations to source files."""
    response = llm.generate(f"""
    Generate code for: {query}
    
    Based on these existing patterns:
    {context_chunks}
    
    For each significant code block you generate, indicate which
    source file influenced that pattern using [source: filename:line].
    """)
    return postprocess_citations(response)
```

**Citation Format Examples:**
```python
# Based on: auth/middleware.py:45-67
def authenticate(request):
    # Pattern from: utils/validators.py:12
    if not validate_token(request.token):
        raise AuthError()
```

#### 3.3 Code Guardrails
Validate generated code before execution.

```python
class CodeGuardrails:
    def pre_generation(self, query):
        """Block dangerous operations before generation."""
        dangerous_patterns = ["rm -rf", "DROP TABLE", "eval(", "exec("]
        if any(p in query.lower() for p in dangerous_patterns):
            return False, "Potentially dangerous operation detected"
        return True, None
    
    def post_generation(self, code):
        """Validate generated code before execution."""
        checks = [
            self.syntax_check(code),
            self.security_scan(code),
            self.dependency_check(code),
            self.style_check(code),
        ]
        return all(checks)
```

**Guardrail Categories:**
| Stage | Check | Action |
|-------|-------|--------|
| Pre-retrieval | Dangerous query patterns | Block |
| Post-retrieval | Chunk freshness | Warn if >6 months old |
| Pre-generation | Security patterns | Filter |
| Post-generation | Syntax validity | Retry |
| Post-generation | Test execution | Validate |

#### 3.4 Corrective Code RAG (C-CodeRAG)
Evaluate retrieved context quality and augment if insufficient.

```python
def corrective_code_rag(query, initial_chunks):
    """
    1. Evaluate if retrieved code is sufficient
    2. If not, search additional sources
    3. Combine and generate
    """
    quality = evaluate_chunks(query, initial_chunks)
    
    if quality.score < 0.5:  # Insufficient
        # Augment with web search for patterns
        web_results = search_web(f"{query} code example")
        initial_chunks = combine(initial_chunks, web_results)
    
    elif quality.score < 0.8:  # Ambiguous
        # Decompose and search for sub-components
        sub_queries = decompose_query(query)
        for sq in sub_queries:
            initial_chunks.extend(search_codebase(sq))
    
    return generate(query, initial_chunks)
```

#### 3.5 Self-Reflective Code Generation (Self-CodeRAG)
Critique and refine generated code iteratively.

```python
def self_reflective_generate(query, max_iterations=3):
    """Generate, critique, and refine code iteratively."""
    code = initial_generate(query)
    
    for i in range(max_iterations):
        critique = llm.evaluate(f"""
        Task: {query}
        Generated Code: {code}
        
        Evaluate:
        1. Does this solve the problem correctly?
        2. Are there edge cases not handled?
        3. Does it follow the codebase patterns?
        4. Is error handling sufficient?
        
        If issues found, suggest specific fixes.
        """)
        
        if critique.is_satisfactory:
            break
        
        code = llm.refine(code, critique.suggestions)
    
    return code
```

---

## Pattern 4: Deep Code Search (Agentic Code Exploration)

### Problem
Complex coding tasks require:
- Multi-file understanding
- Iterative exploration of the codebase
- Connecting patterns across modules
- Building mental models of architecture

### Solution: Iterative Search-Think-Generate Loop

```
┌─────────────────────────────────────────────────────────┐
│                    DEEP CODE SEARCH                      │
├─────────────────────────────────────────────────────────┤
│                                                          │
│   ┌──────────┐    ┌──────────┐    ┌──────────┐          │
│   │  SEARCH  │───▶│  THINK   │───▶│ GENERATE │          │
│   └──────────┘    └──────────┘    └──────────┘          │
│        │               │               │                 │
│        │               ▼               │                 │
│        │        ┌──────────┐           │                 │
│        │        │ EVALUATE │           │                 │
│        │        └──────────┘           │                 │
│        │               │               │                 │
│        │◀──────────────┘               │                 │
│        │      (if gaps found)          │                 │
│        │                               │                 │
│        └───────────────────────────────┘                 │
│                    (iterate)                             │
└─────────────────────────────────────────────────────────┘
```

#### 4.1 Implementation

```python
@dataclass
class CodeExplorationState:
    query: str
    discovered_files: list[str]
    understanding: str  # Accumulated knowledge
    gaps: list[str]  # What we still need to find
    solution_draft: str

def deep_code_search(query: str, max_depth: int = 3) -> CodeExplorationState:
    state = CodeExplorationState(
        query=query,
        discovered_files=[],
        understanding="",
        gaps=[query],
        solution_draft=""
    )
    
    for depth in range(max_depth):
        # SEARCH: Find code relevant to current gaps
        for gap in state.gaps:
            chunks = hybrid_code_search(gap)
            chunks = rerank_code_chunks(gap, chunks)
            state.discovered_files.extend(chunks)
        
        # THINK: Update understanding and identify new gaps
        state.understanding = synthesize_understanding(
            state.query,
            state.discovered_files
        )
        state.gaps = identify_gaps(state.query, state.understanding)
        
        # GENERATE: Draft solution based on current understanding
        state.solution_draft = generate_solution(
            state.query,
            state.understanding
        )
        
        # EVALUATE: Check if solution is complete
        evaluation = evaluate_solution(state.query, state.solution_draft)
        if evaluation.is_complete:
            break
        
        # Update gaps based on evaluation
        state.gaps = evaluation.remaining_questions
    
    return state
```

#### 4.2 Gap Identification for Code

```python
def identify_code_gaps(query, current_understanding):
    """Identify what's still missing to complete the task."""
    prompt = f"""
    Original Task: {query}
    
    Current Understanding:
    {current_understanding}
    
    What information is still missing? Consider:
    1. Unresolved imports or dependencies
    2. Missing function implementations referenced but not found
    3. Configuration or environment requirements unclear
    4. Error handling patterns not discovered
    5. Test patterns not found
    
    Return a list of specific follow-up searches needed.
    """
    return llm.generate_list(prompt)
```

#### 4.3 Multi-Hop Code Reasoning

```python
def multi_hop_code_query(complex_query):
    """
    Break complex queries into sequential searches.
    
    Example: "How do I add a new API endpoint with authentication?"
    Hop 1: Find existing API endpoint patterns
    Hop 2: Find authentication middleware
    Hop 3: Find route registration patterns
    Hop 4: Find request validation patterns
    Hop 5: Synthesize into complete solution
    """
    hops = decompose_into_hops(complex_query)
    accumulated_context = []
    
    for hop in hops:
        # Use previous context to inform this search
        enhanced_query = enhance_with_context(hop, accumulated_context)
        results = search_codebase(enhanced_query)
        accumulated_context.extend(results)
    
    return synthesize_solution(complex_query, accumulated_context)
```

---

## Pattern 5: Code Evaluation Metrics

### For Code Agent Self-Assessment

| Metric | Description | Measurement |
|--------|-------------|-------------|
| **Syntax Validity** | Generated code parses correctly | AST parse success |
| **Style Conformance** | Matches codebase conventions | Linter score |
| **Functional Correctness** | Code does what was requested | Test pass rate |
| **Context Relevance** | Retrieved code was useful | LLM relevance score |
| **Hallucination Rate** | Non-existent APIs referenced | Static analysis |
| **Citation Accuracy** | Sources actually contain patterns | Cross-reference check |
| **Completeness** | All aspects of task addressed | Checklist coverage |

### Composite Evaluation Function

```python
def evaluate_code_generation(query, generated_code, context_used):
    scores = {
        "syntax": check_syntax(generated_code),
        "style": run_linter(generated_code),
        "relevance": llm_score_relevance(query, generated_code),
        "grounded": verify_apis_exist(generated_code, context_used),
        "complete": check_completeness(query, generated_code),
    }
    
    weights = {
        "syntax": 0.25,
        "style": 0.10,
        "relevance": 0.25,
        "grounded": 0.25,
        "complete": 0.15,
    }
    
    return sum(scores[k] * weights[k] for k in scores)
```

---

## Quick Reference: When to Apply Each Pattern

| Scenario | Primary Pattern | Key Technique |
|----------|-----------------|---------------|
| "Find similar code" | Index-Aware | HyCE + Graph RAG |
| "Explain this codebase" | Deep Search | Multi-hop exploration |
| "Fix this bug" | Postprocessing | Rerank + Compress |
| "Add new feature" | Trustworthy Gen | Citations + Self-RAG |
| "Refactor safely" | Guardrails | Pre/post validation |
| "Unknown library" | Out-of-scope | Detect + augment with web |
| "Complex architecture" | Deep Search | Iterative gap-filling |

---

## Implementation Checklist for Claude Code Skills

- [ ] **Indexing**: Build AST-based code graph for codebase
- [ ] **Hybrid Search**: Combine keyword + semantic for code lookup
- [ ] **Context Compression**: Extract only relevant code sections
- [ ] **Disambiguation**: Detect same-name conflicts across files
- [ ] **Version Awareness**: Track branch/version in chunk metadata
- [ ] **Citation System**: Link generated code to source patterns
- [ ] **Guardrails**: Pre/post generation safety checks
- [ ] **Self-Reflection**: Critique loop before finalizing code
- [ ] **Gap Detection**: Identify missing context iteratively
- [ ] **Evaluation Metrics**: Score generated code quality

---

## References

- Gao et al. (2022) - HyDE: Hypothetical Document Embeddings
- Peng et al. (2024) - Graph RAG Systems Survey
- Asai et al. (2023) - Self-RAG: Learning to Retrieve, Generate, and Critique
- Yan et al. (2024) - Corrective Retrieval Augmented Generation
- STORM (Stanford, 2024) - Deep Research for Long-Form Generation

---

*Document extracted and adapted from "Generative AI Design Patterns" Chapter 4: Adding Knowledge*
