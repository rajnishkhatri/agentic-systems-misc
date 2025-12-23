# AI Design Patterns Comprehensive Guide

> A unified reference for all AI design patterns: usage guidelines, constraints, decision matrices, and anti-patterns.

---

## Table of Contents

1. [Pattern Catalog](#pattern-catalog)
2. [Decision Matrices](#decision-matrices)
3. [Pattern Details](#pattern-details)
4. [Anti-Patterns](#anti-patterns)
5. [Pattern Combinations](#pattern-combinations)
6. [Framework-Specific Guidance](#framework-specific-guidance)

---

## Pattern Catalog

### Quick Reference by Category

#### Code Agent Patterns
| Pattern | Purpose | Complexity |
|---------|---------|------------|
| Index-Aware Code Retrieval | Find code using semantic + keyword search | Medium |
| Code Context Postprocessing | Filter and rank retrieved code chunks | Low |
| Trustworthy Code Generation | Generate code with citations and validation | Medium |
| Deep Code Search | Multi-hop iterative code exploration | High |
| Code Evaluation Metrics | Self-assessment for code quality | Low |

#### Agentic Action Patterns
| Pattern | Purpose | Complexity |
|---------|---------|------------|
| Tool Calling | LLM invokes external functions/APIs | Medium |
| Code Execution | LLM generates DSL/code for execution | Medium |
| ReAct | Reasoning + Acting loop | Medium-High |
| Router | Route requests to specialized agents | Low-Medium |
| Sequential Workflow | Linear multi-step processing | Low |
| Multiagent Collaboration | Multiple agents working together | High |

#### Content Control Patterns
| Pattern | Purpose | Complexity |
|---------|---------|------------|
| Logits Masking | Enforce rules via token probability control | High |
| Grammar | Constrain output to schema/format | Medium |
| Style Transfer | Convert content to desired style | Medium |
| Reverse Neutralization | Generate styled content from neutral form | High |
| Content Optimization | Optimize content via preference tuning | High |

#### Capability Extension Patterns
| Pattern | Purpose | Complexity |
|---------|---------|------------|
| Chain of Thought (CoT) | Step-by-step reasoning | Low |
| Tree of Thoughts (ToT) | Multi-path reasoning exploration | High |
| Adapter Tuning (LoRA) | Fine-tune for style/format | Medium |
| Evol-Instruct | Generate training data for new tasks | High |

#### Reliability Patterns
| Pattern | Purpose | Complexity |
|---------|---------|------------|
| LLM-as-Judge | Systematic evaluation with rubrics | Medium |
| Reflection | Iterative self-critique loops | Medium |
| Dependency Injection | Mockable, testable components | Low |
| Prompt Optimization | Systematic prompt refinement | Medium |

#### Safeguard Patterns
| Pattern | Purpose | Complexity |
|---------|---------|------------|
| Template Generation | Pre-reviewed templates for high volume | Medium |
| Assembled Reformat | Two-phase: assemble facts + reformat | Medium |
| Self-Check | Confidence scoring via logprobs | Low |
| Guardrails | Input/output protection chains | Medium |

#### Security Patterns
| Pattern | Purpose | Complexity |
|---------|---------|------------|
| Action-Selector | Whitelist actions, no tool feedback | Low |
| Plan-Then-Execute | Fixed plan, no deviation | Medium |
| Dual-LLM | Separate privileged and sandboxed LLMs | High |
| Map-Reduce | Isolate untrusted data processing | High |
| Code-Then-Execute | LLM writes code, code processes data | Medium |
| Context Minimization | Remove unnecessary context between steps | Low |

---

## Decision Matrices

### Matrix 1: Agentic Action Selection

```
Need real-time data or API calls?
    └─▶ Tool Calling

Need to generate code/queries (SQL, graphs)?
    └─▶ Code Execution

Need reasoning between action steps?
    └─▶ ReAct

Need to route to specialized handlers?
    └─▶ Router

Need linear multi-step processing?
    └─▶ Sequential Workflow

Need multiple perspectives or expertise?
    └─▶ Multiagent Collaboration

Need dynamic capability-based assignment?
    └─▶ Market-Based Auction
```

### Matrix 2: Content Style Control Selection

```
Need to control LLM output style?
│
├─► Rules can be expressed programmatically?
│   ├─► Yes, and I have logprobs access → LOGITS MASKING
│   └─► Yes, as schema/format → GRAMMAR
│
├─► I have example input-output pairs?
│   └─► Yes → STYLE TRANSFER (few-shot or fine-tune)
│
├─► I have styled examples but no inputs?
│   └─► Yes → REVERSE NEUTRALIZATION
│
└─► I don't know what makes content "good"?
    └─► Yes → CONTENT OPTIMIZATION (DPO)
```

### Matrix 3: Capability Extension Selection

```
Task fails with standard prompting?
├── Model gives "lazy" or incomplete responses
│   └── Use: Zero-shot CoT (add "think step-by-step")
├── Model applies wrong logic or hallucinates reasoning
│   └── Use: Few-shot CoT (provide example reasoning chains)
├── Task requires exploring multiple solution paths
│   └── Use: Tree of Thoughts (ToT)
├── Need consistent style/format adaptation (100-1000 examples available)
│   └── Use: Adapter Tuning (LoRA/QLoRA)
├── Need to teach entirely new complex task (1000+ examples needed)
│   └── Use: Evol-Instruct + Instruction Tuning
└── Model lacks factual knowledge
    └── Do NOT use these patterns. Use RAG instead.
```

### Matrix 4: Safeguard Pattern Selection

```
Is content customer-facing with brand risk?
├─ Yes → Can you enumerate all variations?
│        ├─ Yes → Template Generation (Pattern 29)
│        └─ No  → Assembled Reformat (Pattern 30)
└─ No  → Is factual accuracy critical?
         ├─ Yes → Self-Check (Pattern 31)
         └─ No  → Do you need input/output protection?
                  └─ Yes → Guardrails (Pattern 32)
```

### Matrix 5: Security Pattern Selection

```
High security requirements?
│
├─▶ [No feedback to LLM?] ─▶ Action-Selector
├─▶ [Fixed plan needed?] ─▶ Plan-Then-Execute
├─▶ [Untrusted data?] ─▶ Dual-LLM or Map-Reduce
└─▶ [Minimize attack surface?] ─▶ Context-Minimization
```

### Matrix 6: Multiagent Architecture Selection

| Architecture | When to Use | Coordination |
|--------------|-------------|--------------|
| **Sequential/Chain** | Linear dependencies, each step feeds next | Implicit (output→input) |
| **Router** | Different specialists for different inputs | Classifier selects agent |
| **Hierarchical** | Complex tasks needing decomposition | Manager delegates to workers |
| **Peer-to-peer** | Need consensus, multiple perspectives | Voting/discussion |
| **Market-based** | Dynamic resource allocation | Auction/bidding |

---

## Pattern Details

### Code Agent Patterns

#### Pattern: Index-Aware Code Retrieval

**When to Use:**
- Query uses different terminology than codebase
- Answer requires understanding relationships across multiple files
- Fine-grained details buried in large code chunks
- Holistic interpretation across modules needed

**Key Techniques:**
1. Hypothetical Code Embedding (HyCE) - Generate hypothetical solution before searching
2. Query Expansion - Expand with domain terminology, aliases, related concepts
3. Hybrid Code Search - Combine keyword (BM25) + semantic (embeddings)
4. Code Graph RAG - Use AST and dependency graphs

**Constraints:**
- Requires AST parsing infrastructure
- Graph construction overhead for large codebases
- Hybrid search requires tuning alpha parameter (0.2-0.8)

**Implementation Checklist:**
- [ ] Build AST-based code graph
- [ ] Implement hybrid search (keyword + semantic)
- [ ] Add query expansion for domain terms
- [ ] Index function calls, imports, class hierarchies

**Anti-Patterns:**
- ❌ Pure semantic search for exact function names (use keyword)
- ❌ Ignoring AST relationships (misses related code)
- ❌ Single retrieval pass for complex queries (use multi-hop)

---

#### Pattern: Code Context Postprocessing

**When to Use:**
- Retrieved chunks may be similar but not relevant
- Code contains noise (comments, dead code, boilerplate)
- Multiple functions with same name (ambiguity)
- Code from conflicting versions or branches

**Key Techniques:**
1. Code Relevance Reranking - Score chunks on task relevance
2. Code Contextual Compression - Extract only relevant portions
3. Symbol Disambiguation - Detect same-name conflicts
4. Version/Branch Filtering - Ensure correct version

**Constraints:**
- Reranking adds latency (LLM call per chunk)
- Compression may lose necessary context
- Disambiguation requires cross-file analysis

**Anti-Patterns:**
- ❌ Using raw embedding similarity without reranking
- ❌ Including entire files when only functions needed
- ❌ Not checking for symbol conflicts

---

#### Pattern: Trustworthy Code Generation

**When to Use:**
- Code must match codebase style
- Need to prevent hallucinated APIs
- Critical error handling required
- Code quality standards must be met

**Key Techniques:**
1. Out-of-Scope Detection - Recognize when task is outside capabilities
2. Code Citations - Link generated code to source references
3. Code Guardrails - Validate before execution
4. Corrective Code RAG - Evaluate and augment context if insufficient
5. Self-Reflective Code Generation - Critique and refine iteratively

**Constraints:**
- Citations require source tracking infrastructure
- Guardrails add validation overhead
- Self-reflection increases token usage

**Anti-Patterns:**
- ❌ Generating code without checking if APIs exist
- ❌ No validation before execution
- ❌ Single-shot generation for complex code
- ❌ Ignoring codebase patterns

---

### Agentic Action Patterns

#### Pattern: Tool Calling

**When to Use:**
- LLM needs real-time data (weather, stocks, news)
- Integration with enterprise APIs (CRM, ERP, databases)
- Personalization from user workspaces (email, calendar)
- Calculations requiring external solvers

**Implementation Approaches:**
- **Native Function Calling**: Maximum control, single provider
- **MCP (Model Context Protocol)**: Multi-provider, shared tools

**Constraints:**
- Keep tool count < 10 per agent (accuracy degrades)
- Requires comprehensive docstrings
- Error handling must enable Reflection pattern
- Tool descriptions consume context tokens

**Best Practices:**
1. Self-descriptive function names
2. Type safety with enums and Pydantic models
3. Descriptive error messages
4. Deterministic data (don't make model fill in known data)

**Anti-Patterns:**
- ❌ Too many tools (>10) overloading the model
- ❌ Vague parameter descriptions
- ❌ Missing type hints and constraints
- ❌ Not handling API failures gracefully

---

#### Pattern: Code Execution

**When to Use:**
- Generating visualizations (Matplotlib, Plotly, Mermaid)
- Database queries (SQL, GraphQL)
- Image manipulation (ImageMagick, PIL)
- Complex calculations requiring programmatic logic

**Constraints:**
- **Always sandbox** - Use containers, VMs, or restricted environments
- Set resource limits (CPU, memory, time)
- Validate before execute (syntax check)
- Prefer constrained DSLs over general-purpose languages

**Security Requirements:**
- Sandboxed execution environment
- Resource limits (timeout, memory, CPU)
- Input validation (forbidden patterns)
- No network access for untrusted code

**Anti-Patterns:**
- ❌ Executing code without sandboxing
- ❌ No resource limits (DoS risk)
- ❌ Using general Python instead of constrained DSLs
- ❌ Not validating generated code before execution

---

#### Pattern: ReAct (Reasoning + Acting)

**When to Use:**
- Multi-step tasks requiring reasoning between actions
- Tasks where tool results influence next steps
- Complex problem-solving with feedback loops

**Architecture:**
```
THINK → ACT → OBSERVE → (repeat until answer)
```

**Constraints:**
- Requires max iteration limit (prevent infinite loops)
- Each iteration adds latency
- Tool results must be formatted for LLM consumption

**Anti-Patterns:**
- ❌ No maximum iterations (infinite loop risk)
- ❌ Not checking completion criteria
- ❌ Ignoring tool errors in reasoning

---

#### Pattern: Multiagent Collaboration

**When to Use:**
- Complex reasoning requiring multiple perspectives
- Tasks requiring specialized domain expertise
- Adversarial verification (red team/blue team)
- Collaborative content creation

**Architecture Options:**
1. **Hierarchical (Executive-Worker)**: Manager delegates to specialists
2. **Peer-to-Peer**: Equal agents collaborate
3. **Market-Based**: Dynamic task assignment via auction

**Constraints:**
- High token usage (multiple agents)
- Coordination overhead
- 40-80% task failure rate in complex systems (design for degradation)
- Requires explicit handoff protocols

**Common Failure Modes:**
- Role confusion (agent acts outside scope)
- Instruction drift (forgets instructions)
- Information withholding (doesn't share critical data)
- Conversation reset (context lost)
- Cascading errors (early mistake propagates)

**Anti-Patterns:**
- ❌ No role boundaries (agents overlap)
- ❌ No completion criteria (premature termination)
- ❌ No context summaries (conversation resets)
- ❌ Synchronous chains when parallel possible

---

### Content Control Patterns

#### Pattern: Logits Masking

**When to Use:**
- Branding: Enforce brand-specific vocabulary
- Accuracy: Prevent repetition of invoice IDs or amounts
- Compliance: Exclude competitor mentions
- Stylebook: Enforce citation formats

**Constraints:**
- Requires access to logprobs (Claude doesn't provide; OpenAI, Google, Meta do)
- Latency: Each sequence requires client-model communication
- Dead ends: If no continuation meets rules, must backtrack or refuse
- Best for locally hosted models

**Anti-Patterns:**
- ❌ "Try-and-try-again" approach (>10% regeneration needed)
- ❌ No backtracking logic for complex rules
- ❌ Masking too aggressively (no valid continuations)

---

#### Pattern: Grammar

**When to Use:**
- Output must conform to data format
- Structured output required (JSON, XML, etc.)
- Enforcing specific schemas

**Implementation Options:**
1. **BNF Grammar**: Most flexible, requires logprobs
2. **JSON Mode**: Simplest, universal support
3. **Structured Output with Dataclass**: Best balance

**Constraints:**
- Complex nested structures increase dead-end probability
- Over-restrictive grammar forces incorrect outputs
- Endless whitespace loops when no valid tokens exist

**Anti-Patterns:**
- ❌ Begging for compliance instead of using grammar
- ❌ Over-restrictive grammar (forces wrong outputs)
- ❌ No escape hatch for uncertainty

---

#### Pattern: Style Transfer

**When to Use:**
- Style is nuanced and hard to express as rules
- Have example input-output pairs
- Need to adapt content to different audiences

**Approaches:**
- **Few-Shot Learning** (1-10 examples): Quick, works for simple styles
- **Fine-Tuning** (100-1000+ examples): Higher fidelity, faster inference

**Constraints:**
- Requires curated example pairs
- Fine-tuning needs training infrastructure
- More examples → longer latency (few-shot)

**Anti-Patterns:**
- ❌ Zero-shot learning for style tasks (often fails)
- ❌ Too many examples → confusion, contradictions
- ❌ Examples don't match desired style

---

#### Pattern: Reverse Neutralization

**When to Use:**
- Have examples of styled content but no input-output pairs
- Need to generate styled content on new topics
- Legal text, personal style, brand voice

**Process:**
1. Neutralize styled content → generates "input"
2. Reverse pairs → styled becomes "output"
3. Fine-tune on reversed pairs
4. Inference: Generate neutral → fine-tuned model converts to style

**Constraints:**
- Requires two LLM calls at inference
- Neutralization prompt must be repeatable
- Content preservation must be validated

**Anti-Patterns:**
- ❌ Subjective neutralization prompts (not repeatable)
- ❌ Not validating content preservation
- ❌ Using wrong neutral form

---

#### Pattern: Content Optimization

**When to Use:**
- Don't know which style factors matter
- Have evaluator (human, automated, or LLM-as-judge)
- Need to optimize toward performance metrics

**Process:**
1. Generate pairs of content
2. Compare using evaluator → pick winner
3. Create preference dataset
4. DPO training → deploy tuned model

**Constraints:**
- Requires evaluation method (most important step)
- Bad evaluator creates model that games metrics
- Content must be producible by model being trained

**Anti-Patterns:**
- ❌ Optimizing for wrong metric (engagement time → confusing content)
- ❌ Bad evaluator (garbage in, garbage out)
- ❌ Using bigger LLM for generation, smaller for training (distribution mismatch)

---

### Capability Extension Patterns

#### Pattern: Chain of Thought (CoT)

**When to Use:**
- Mathematical calculations requiring intermediate steps
- Logical deductions with multiple conditions
- Sequential reasoning tasks
- Model jumps directly to wrong answers

**Variants:**
- **Zero-shot CoT**: Append "think step-by-step" (works best on frontier models)
- **Few-shot CoT**: Provide 1-3 demonstration examples
- **Auto-CoT**: Dynamically select examples from store

**Constraints:**
- Does NOT fix data gaps (model doesn't know facts)
- Does NOT work for non-sequential logic
- Less effective on small/local models

**Anti-Patterns:**
- ❌ Using CoT for factual knowledge gaps (use RAG)
- ❌ Zero-shot CoT on small models (use few-shot)
- ❌ Too many examples (confusion)

---

#### Pattern: Tree of Thoughts (ToT)

**When to Use:**
- Task requires exploring multiple solution approaches
- Single reasoning path likely leads to suboptimal solutions
- Problem benefits from backtracking
- Strategic planning, creative writing, multi-constraint optimization

**Constraints:**
- Requires `O(beam_width × num_thoughts × max_steps)` LLM calls
- Typical: 30-50 API calls per problem
- Latency: 1-3 minutes depending on model speed
- High cost

**When NOT to Use:**
- Simple factual queries
- Tasks where CoT suffices
- Real-time latency requirements (<5s)
- Problems solvable with single reasoning chain

**Anti-Patterns:**
- ❌ Using ToT for simple queries (wastes 30-50x compute)
- ❌ No early termination on high-confidence solutions
- ❌ Too narrow beam width (misses good paths)

---

#### Pattern: Adapter Tuning (LoRA/QLoRA)

**When to Use:**
- Need consistent output style/format
- Have 100-10,000 input-output example pairs
- Task is similar to model's pretrained capabilities
- Cost/latency constraints require smaller model

**What It Does NOT Do:**
- ❌ Teach new vocabulary or jargon (use continued pretraining)
- ❌ Add new factual knowledge (use RAG)
- ❌ Enable fundamentally new capabilities (use instruction tuning)

**Constraints:**
- Requires training infrastructure
- Dataset size determines rank (r) parameter
- Fine-tuning takes time and compute

**Anti-Patterns:**
- ❌ Using adapter tuning for new knowledge (use RAG)
- ❌ Too high rank for small dataset (overfitting)
- ❌ Too low rank for large dataset (underfitting)

---

#### Pattern: Evol-Instruct

**When to Use:**
- Need to teach model complex enterprise/domain-specific tasks
- Have few seed examples but need thousands for training
- Task is genuinely new (not in model's pretraining)
- Can afford higher development cost

**Process:**
1. Evolve instructions (deepen, concretize, combine)
2. Generate answers (teacher model, reflection, or RAG)
3. Evaluate and filter (quality threshold)
4. Instruction tuning (SFT on filtered dataset)

**Constraints:**
- Requires 2,000-20,000 examples depending on model size
- High development cost
- Quality of seed examples critical

**Anti-Patterns:**
- ❌ Skipping evaluation step (garbage in, garbage out)
- ❌ Using same model for evolution and training (distribution mismatch)
- ❌ Too few seed examples (poor diversity)

---

### Reliability Patterns

#### Pattern: LLM-as-Judge

**When to Use:**
- Need systematic evaluation with custom rubrics
- Manual "vibe checking" insufficient
- Multiple quality dimensions to assess
- RAG systems need relevance scoring

**Key Components:**
1. Structured scoring rubric (Pydantic models)
2. Judge function with temperature=0 for consistency
3. Bias mitigation (different model, pairwise comparison, polling)

**Constraints:**
- Adds +1 LLM call (latency and cost)
- Requires rubric design expertise
- Coarse scores (1-5) more consistent than fine-grained

**Anti-Patterns:**
- ❌ Single aggregate score without criteria
- ❌ Fine-grained scores (1-100) increase inconsistency
- ❌ Same model evaluating its own output (self-bias)
- ❌ No calibration anchors in rubric

---

#### Pattern: Reflection

**When to Use:**
- Single-shot LLM calls produce errors
- High error rates in generated content
- User feedback loops could be automated
- Code generation without validation
- Content requires iterative refinement

**Architecture:**
```
Generate → Evaluate → Critique → Refine → (repeat until threshold)
```

**Constraints:**
- Requires max iterations (prevent infinite loops)
- Adds +N LLM calls (100-300% cost increase)
- Not suitable for real-time requirements

**Anti-Patterns:**
- ❌ No maximum iterations (infinite loop risk)
- ❌ Same model for generation and critique (self-bias)
- ❌ Not preserving critique history
- ❌ Too high threshold (never converges)

---

#### Pattern: Dependency Injection

**When to Use:**
- LLM calls hardcoded inside business logic
- Tests that make real API calls
- Difficulty testing individual pipeline steps
- Need to swap models without code changes
- Flaky tests due to LLM nondeterminism

**Key Components:**
1. Protocols/Interfaces for LLM providers
2. Injectable pipeline components
3. Test doubles (mocks, recording, replay)

**Constraints:**
- Adds abstraction layer (minimal overhead)
- Requires interface design upfront
- More code to maintain

**Anti-Patterns:**
- ❌ Hardcoded LLM client inside function
- ❌ Global state for configuration
- ❌ Tests that hit real APIs
- ❌ No factory pattern for different environments

---

#### Pattern: Prompt Optimization

**When to Use:**
- Prompts embedded as string literals
- Frequent prompt tweaking after model updates
- Inconsistent output quality across inputs
- Manual A/B testing of prompt variations

**Approaches:**
1. **Best-of-N**: Generate N variations, evaluate, return best
2. **Few-shot Bootstrap**: Try different example combinations
3. **Instruction Evolution**: Mutate instructions iteratively

**Constraints:**
- Requires evaluation dataset
- Optimization runs at build-time (not runtime)
- Needs systematic approach (not ad-hoc tweaking)

**Anti-Patterns:**
- ❌ Hardcoded prompts scattered in code
- ❌ Manual prompt versioning via comments
- ❌ No evaluation dataset
- ❌ Optimizing without objective measure

---

### Safeguard Patterns

#### Pattern: Template Generation

**When to Use:**
- High-volume customer communications (thousands/day)
- Brand risk from hallucinated content unacceptable
- Variations are enumerable (< 10,000)
- Human review per-item cost-prohibitive

**Process:**
1. Enumerate variations (offline)
2. LLM generate templates with placeholders
3. Human review (one-time)
4. Store in database
5. Inference: Retrieve template → replace placeholders (no LLM call)

**Constraints:**
- Variations must be enumerable
- Requires one-time human review
- Placeholders must be deterministic
- Storage scales with variation count

**Anti-Patterns:**
- ❌ Using for non-enumerable variations (use Assembled Reformat)
- ❌ No human review (brand risk)
- ❌ Placeholders not clearly marked
- ❌ Too many variations (>10,000) → infeasible review

---

#### Pattern: Assembled Reformat

**When to Use:**
- Content must be factually accurate
- Presentation must be appealing
- Too many variations for Template Generation
- Source data exists in structured form

**Process:**
1. **Assemble**: Extract facts deterministically (DB, OCR, RAG)
2. **Reformat**: LLM rewrites for presentation (lower hallucination risk)

**Key Insight:**
Reformatting has lower hallucination rates than generation-from-scratch because facts are provided in context.

**Constraints:**
- Requires structured data source
- Two-phase adds latency
- Validation needed to ensure facts preserved

**Anti-Patterns:**
- ❌ Generating facts instead of extracting
- ❌ Not validating facts preserved in reformat
- ❌ High temperature in reformat phase (increases hallucination)

---

#### Pattern: Self-Check

**When to Use:**
- Factual accuracy critical (finance, healthcare, legal)
- Structured data extraction from documents
- RAG systems with potentially conflicting chunks
- Hallucination cost > confidence-check cost

**Core Insight:**
LLMs emit lower probability tokens when "guessing" vs "knowing". Use logprobs to detect potential hallucinations.

**Constraints:**
- Requires logprobs access (OpenAI, Google, Meta; not Claude)
- False positives possible (low prob ≠ hallucination)
- Needs threshold tuning per use case

**Fallback for Non-Logprob Providers:**
Use sampling-based validation (generate N samples, check consistency).

**Anti-Patterns:**
- ❌ Treating all low-probability tokens as hallucinations
- ❌ No false positive mitigation
- ❌ Same threshold for all use cases

---

#### Pattern: Guardrails

**When to Use:**
- Application exposed to untrusted inputs
- PII or sensitive data flows through system
- Regulatory compliance required
- Brand/reputation risk from inappropriate outputs
- Adversarial attacks concern

**Guardrail Types:**
1. **Input**: PII detection, prompt injection, banned topics
2. **Retrieval**: Relevance filter, source validation
3. **Tool**: Parameter validation, permission checks
4. **Output**: PII redaction, toxicity, factual grounding

**Constraints:**
- Adds latency (regex: <1ms, LLM: 100-500ms)
- Requires tuning thresholds
- May have false positives/negatives

**Anti-Patterns:**
- ❌ No guardrails on public-facing systems
- ❌ Only input guardrails (miss output issues)
- ❌ Too strict thresholds (blocks legitimate use)
- ❌ No monitoring of guardrail triggers

---

### Security Patterns

#### Pattern: Action-Selector

**When to Use:**
- High-risk actions (payments, deletions)
- Need whitelist of allowed actions
- No tool feedback should reach agent

**Architecture:**
- Predefined action set
- LLM selects action + params
- Execute WITHOUT returning result to LLM
- Format result with static template

**Constraints:**
- Limited flexibility (only predefined actions)
- No adaptive behavior based on results

**Anti-Patterns:**
- ❌ Returning tool results to LLM (prompt injection risk)
- ❌ Too many allowed actions (harder to secure)

---

#### Pattern: Plan-Then-Execute

**When to Use:**
- Predictable workflows
- Deviations unacceptable
- Need fixed plan upfront

**Architecture:**
1. LLM creates immutable plan
2. Execute plan mechanically (no LLM re-evaluation)
3. Format results (optional LLM, isolated)

**Constraints:**
- No adaptation to unexpected results
- Plan must be complete upfront

**Anti-Patterns:**
- ❌ Modifying plan during execution
- ❌ LLM re-evaluating after each step

---

#### Pattern: Dual-LLM

**When to Use:**
- Processing untrusted data (emails, user uploads)
- Need separation of concerns
- Mixed trust data sources

**Architecture:**
- **Privileged LLM**: Plans, has tool access, processes trusted input
- **Sandboxed LLM**: No tools, processes untrusted data only
- Privileged executes plan with sanitized data

**Constraints:**
- Requires two LLM instances
- Higher latency and cost
- Complex architecture

**Anti-Patterns:**
- ❌ Privileged LLM processing untrusted data
- ❌ Sandboxed LLM having tool access

---

#### Pattern: Context Minimization

**When to Use:**
- Multi-step chains where early injection could propagate
- Need to minimize attack surface
- Original prompt contains sensitive info

**Process:**
- Remove original user prompt after initial processing
- Only pass structured output between steps
- Minimize context at each stage

**Constraints:**
- May lose necessary context
- Requires careful design of handoffs

**Anti-Patterns:**
- ❌ Passing full conversation history to each step
- ❌ Including original prompt in later steps

---

## Anti-Patterns

### General Anti-Patterns

| Anti-Pattern | Problem | Solution |
|--------------|---------|----------|
| **No evaluation set** | Can't measure improvements | Create 50+ test queries with labels |
| **Optimizing blindly** | Might make things worse | A/B test changes |
| **One-size-fits-all** | Different content needs different treatment | Content-aware approach |
| **Ignoring metadata** | Lose filtering capability | Always preserve source info |
| **No monitoring** | Issues go undetected | Log scores, latency, errors |
| **Hardcoded prompts** | Hard to optimize and version | Externalize to registry |
| **Same model for generation and evaluation** | Self-bias | Use different models |
| **No maximum iterations** | Infinite loops | Always set bounds |
| **Too many tools** | Accuracy degrades | Keep < 10 per agent |
| **No sandboxing** | Security risk | Always sandbox code execution |

### Pattern-Specific Anti-Patterns

#### Code Agent Anti-Patterns
- ❌ Pure semantic search for exact function names → Use hybrid search
- ❌ Single retrieval pass for complex queries → Use multi-hop
- ❌ Generating code without checking APIs exist → Add validation
- ❌ No citations → Link to source patterns

#### Agentic Action Anti-Patterns
- ❌ Too many tools (>10) → Split into specialized agents
- ❌ Unvalidated code execution → Always sandbox + validate
- ❌ Infinite ReAct loops → Set max iterations + completion criteria
- ❌ No human escape → Add escalation path

#### Content Control Anti-Patterns
- ❌ "Try-and-try-again" for logits masking → Use backtracking
- ❌ Begging for compliance → Use grammar constraints
- ❌ Zero-shot for style → Use few-shot or fine-tuning
- ❌ Optimizing for wrong metric → Align evaluator with objectives

#### Capability Extension Anti-Patterns
- ❌ Using CoT for factual gaps → Use RAG
- ❌ Using ToT for simple queries → Wastes compute
- ❌ Adapter tuning for new knowledge → Use RAG
- ❌ Skipping evaluation in Evol-Instruct → Garbage in, garbage out

#### Reliability Anti-Patterns
- ❌ Fine-grained scores (1-100) → Use coarse (1-5)
- ❌ No critique history → Preserve for context
- ❌ Hardcoded LLM clients → Use dependency injection
- ❌ No evaluation dataset → Create one

#### Safeguard Anti-Patterns
- ❌ Template generation for non-enumerable → Use Assembled Reformat
- ❌ Generating facts → Extract deterministically
- ❌ No false positive mitigation → Filter common cases
- ❌ Only input guardrails → Add output guardrails

#### Security Anti-Patterns
- ❌ Returning tool results to LLM → Use Action-Selector
- ❌ Privileged LLM processing untrusted data → Use Dual-LLM
- ❌ Passing full history → Use Context Minimization
- ❌ No validation → Validate all inputs

### Multiagent System Anti-Patterns

| Anti-Pattern | Symptom | Mitigation |
|--------------|---------|------------|
| **Role confusion** | Agent acts outside scope | Stronger system prompts, role validator |
| **Instruction drift** | Forgets instructions | Periodic reminders, shorter context |
| **Premature termination** | Stops before complete | Completion checklist, external manager |
| **Information withholding** | Doesn't share critical data | Sharing protocol, shared memory |
| **Conversation reset** | Context lost | Context summaries, persistent state |
| **Reasoning-action mismatch** | Says X, does Y | Structured output, chain-of-thought validation |
| **Cascading errors** | Early mistake propagates | Validation gates, checkpoint & rollback |
| **Hallucinations** | Plausible but false info | Citation requirements, verification agent |

---

## Pattern Combinations

### Common Compositions

#### Research Assistant
```
Router (classify) → ReAct (search) → Review Panel → Output (format)
```

#### Data Analysis Pipeline
```
Code Gen → Execute (sandbox) → Validate (review) → Visualize (code)
```

#### Secure Enterprise Agent
```
Dual-LLM (sanitize) → Plan-Then-Execute → Human Review → Execute (action)
```

#### High-Volume Customer Comms
```
Guardrails (input) → Template Generation → Guardrails (output) → User
```

#### Accurate Content Pipeline
```
Guardrails (input) → Assembled Reformat → Self-Check → Guardrails (output) → User
```

### Layering Safeguards

For defense-in-depth, layer multiple safeguard patterns:

```
User Input
  ↓
[Input Guardrails] (PII, injection, banned topics)
  ↓
[Template Generation OR Assembled Reformat]
  ↓
[Self-Check] (confidence scoring)
  ↓
[Output Guardrails] (PII redaction, toxicity, grounding)
  ↓
User Output
```

### Reliability Stack

```
Dependency Injection (testability)
  ↓
Prompt Optimization (quality)
  ↓
LLM-as-Judge (evaluation)
  ↓
Reflection (iterative improvement)
```

---

## Framework-Specific Guidance

### LangGraph

**Best For:** Complex workflows, state machines

**Pattern Support:**
- ✅ Tool Calling (via MCP adapter)
- ✅ Multiagent (graph-based)
- ✅ Sequential Workflow (StateGraph)
- ✅ ReAct (create_react_agent)

**Example:**
```python
from langgraph.graph import StateGraph
from langgraph.prebuilt import create_react_agent

agent = create_react_agent(
    "anthropic:claude-sonnet-4-20250514",
    tools=mcp_client.get_tools()
)
```

### PydanticAI

**Best For:** Type-safe, structured outputs

**Pattern Support:**
- ✅ Tool Calling (native + MCP)
- ✅ Multiagent (A2A export)
- ✅ Dependency Injection (native deps_type)
- ✅ Structured Output (result_type)

**Example:**
```python
from pydantic_ai import Agent

agent = Agent(
    model,
    deps_type=MyDependencies,  # Injectable
    result_type=MyResult       # Structured
)
```

### CrewAI

**Best For:** Role-based collaboration

**Pattern Support:**
- ✅ Multiagent (built-in)
- ✅ Tool Calling (native)
- ✅ Sequential Workflow (tasks)

**Example:**
```python
from crewai import Agent, Task, Crew

crew = Crew(
    agents=[researcher, analyst, writer],
    tasks=[research_task, analysis_task, writing_task]
)
```

### AG2/AutoGen

**Best For:** Conversational agents

**Pattern Support:**
- ✅ Multiagent (built-in)
- ✅ Tool Calling (native)
- ✅ Conversational Reflection

**Example:**
```python
from autogen import ConversableAgent

manager = ConversableAgent(
    name="manager",
    system_message="Coordinate team..."
)
```

### DSPy

**Best For:** Prompt optimization, systematic LLM pipelines

**Pattern Support:**
- ✅ Prompt Optimization (BootstrapFewShot)
- ✅ Reflection (ChainOfThought)
- ✅ Structured I/O (Signatures)

**Example:**
```python
import dspy

class MySignature(dspy.Signature):
    input_text: str = dspy.InputField()
    output: MyOutputClass = dspy.OutputField()

chain = dspy.ChainOfThought(MySignature)
```

---

## Quick Reference Tables

### Pattern Selection by Symptom

| Symptom | Pattern | Implementation Effort |
|---------|---------|----------------------|
| Model skips reasoning steps | Zero-shot CoT | Low (prompt change) |
| Model uses wrong logic | Few-shot CoT | Low (add examples) |
| Need dynamic example selection | Auto-CoT | Medium (build store) |
| Problem needs path exploration | ToT | Medium-High (orchestration) |
| Need consistent output format | Adapter Tuning | Medium (training) |
| Need entirely new capability | Evol-Instruct | High (dataset + training) |
| Model lacks facts | **Use RAG, not these patterns** | - |
| High error rates | Reflection | Medium (loop implementation) |
| Inconsistent quality | Prompt Optimization | Medium (systematic approach) |
| Untrusted inputs | Guardrails | Medium (chain setup) |
| High-volume comms | Template Generation | Medium (review workflow) |
| Need accurate facts | Assembled Reformat | Medium (two-phase) |
| Need confidence scores | Self-Check | Low (logprobs) |

### Complexity vs. Benefit Matrix

| Pattern | Complexity | Benefit | When Worth It |
|---------|-----------|---------|---------------|
| Zero-shot CoT | Low | Medium | Always try first |
| Few-shot CoT | Low | High | When zero-shot fails |
| Tool Calling | Medium | High | Need external data/APIs |
| Code Execution | Medium | High | Need DSL generation |
| ReAct | Medium-High | High | Multi-step reasoning |
| ToT | High | Medium-High | Complex exploration needed |
| Adapter Tuning | Medium | High | Have 100+ examples |
| Evol-Instruct | High | High | New complex task |
| Reflection | Medium | High | Quality critical |
| Guardrails | Medium | Critical | Public-facing or sensitive |
| Template Generation | Medium | High | High volume, enumerable |
| Assembled Reformat | Medium | High | Accuracy critical |
| Self-Check | Low | Medium | Factual accuracy needed |
| Multiagent | High | High | Complex multi-perspective tasks |

### Cost Considerations

| Pattern | Token Usage | Cost Optimization |
|---------|-------------|-------------------|
| Tool Calling | Low-Medium | Minimize tool descriptions |
| Code Execution | Medium | Use smaller models for code gen |
| ReAct | Medium-High | Limit max iterations |
| Sequential | Medium | Minimize context passing |
| Multiagent | High | Use smaller models for workers |
| Review Panel | Very High | Limit rounds, use summaries |
| Reflection | +100-300% | Set max iterations, early exit |
| ToT | Very High (30-50 calls) | Only for complex problems |
| LLM-as-Judge | +50-100% | Use smaller model for judge |
| Self-Check | +0% (logprobs) | No additional cost |

### Latency Considerations

| Pattern | Typical Latency | Optimization |
|---------|----------------|--------------|
| Tool Calling (1 tool) | 2-5 seconds | Cache common queries |
| ReAct (3-5 steps) | 10-30 seconds | Parallelize independent tools |
| Sequential (3 steps) | 6-15 seconds | Combine simple steps |
| Multiagent (3 agents) | 15-45 seconds | Run in parallel where possible |
| Review Panel (5 agents) | 30-90 seconds | Limit discussion rounds |
| Reflection (3 iterations) | +200-300% | Early exit on threshold |
| ToT | 1-3 minutes | Parallelize thought generation |
| Guardrails (regex) | <1ms | Layer fast → slow |
| Guardrails (LLM) | 100-500ms | Run in parallel with generation |

---

## Implementation Checklists

### Pre-Implementation Checklist

- [ ] Identified primary pattern for use case
- [ ] Documented tool requirements (if applicable)
- [ ] Defined success criteria
- [ ] Planned failure modes and recovery
- [ ] Chose security patterns (if needed)
- [ ] Assessed cost and latency constraints
- [ ] Identified evaluation method

### Pattern-Specific Checklists

#### Tool Calling
- [ ] Tool count < 10 per agent
- [ ] Comprehensive docstrings
- [ ] Type hints and constraints
- [ ] Error handling for Reflection integration
- [ ] Timeout limits set

#### Code Execution
- [ ] Sandbox environment configured
- [ ] Resource limits set (CPU, memory, time)
- [ ] Pre-execution validation
- [ ] Reflection loop for errors
- [ ] Security patterns in place

#### Multiagent
- [ ] Role boundaries defined
- [ ] Completion criteria specified
- [ ] Context management strategy
- [ ] Failure recovery plan
- [ ] Human escalation path

#### Guardrails
- [ ] Input guardrails configured
- [ ] Output guardrails configured
- [ ] Tool guardrails (if applicable)
- [ ] Thresholds tuned
- [ ] Monitoring for triggers

#### Template Generation
- [ ] Variations enumerated
- [ ] Placeholders defined
- [ ] Review workflow established
- [ ] Storage solution chosen
- [ ] Validation checks in place

### Production Readiness Checklist

- [ ] All patterns have max iteration limits
- [ ] Error handling implemented
- [ ] Logging and monitoring set up
- [ ] Tests written (unit + integration)
- [ ] Documentation complete
- [ ] Performance benchmarks met
- [ ] Security review completed
- [ ] Cost estimates validated
- [ ] Latency requirements met
- [ ] Human-in-the-loop paths defined (if needed)

---

## References and Further Reading

### Key Papers and Sources

- **ReAct**: Yao et al. (2022) - Synergizing Reasoning and Acting
- **CoT**: Wei et al. (2022) - Chain-of-Thought Prompting
- **ToT**: Yao et al. (2023) - Tree of Thoughts
- **LoRA**: Dettmers et al. (2023) - QLoRA
- **Evol-Instruct**: Xu et al. (2023) - WizardLM
- **Reflection**: Shinn et al. (2023) - Reflexion
- **DSPy**: Khattab et al. (2023) - Compiling Declarative Language Model Calls
- **Security**: Beurer-Kellner et al. (2025) - Securing LLM Agents
- **Multiagent Failures**: Cemri et al. (2025) - Why Multiagent Systems Fail

### Framework Documentation

- LangGraph: https://langchain-ai.github.io/langgraph/
- PydanticAI: https://ai.pydantic.dev/
- CrewAI: https://docs.crewai.com/
- AG2/AutoGen: https://microsoft.github.io/autogen/
- DSPy: https://dspy-docs.vercel.app/

---

## Version History

- **v1.0** (2025-01-XX): Initial comprehensive guide
  - Extracted patterns from designpatterns/ folder
  - Created decision matrices
  - Documented constraints and anti-patterns
  - Added framework-specific guidance

---

*This guide synthesizes patterns from multiple sources in the designpatterns/ folder. For detailed implementation examples, refer to the original pattern files.*




















