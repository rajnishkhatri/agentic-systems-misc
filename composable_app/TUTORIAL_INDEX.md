# Composable App Tutorial System

**Welcome to the Composable Multi-Agent Tutorial Series!**

This tutorial system provides comprehensive, hands-on learning for building production-ready multi-agent systems using composable design patterns. You'll learn to implement 8+ GenAI patterns through a working K-12 content writing application.

> **Book Reference**: These tutorials complement [*Generative AI Design Patterns*](https://www.oreilly.com/library/view/generative-ai-design/9781098159337/) by Lakshmanan and Hapke (O'Reilly, October 2025). The `composable_app/` serves as the reference implementation for Chapter 10 and related pattern chapters.

---

## 📚 What You'll Learn

- **Build multi-agent systems** with task routing, specialized agents, and review panels
- **Implement 8+ design patterns** including RAG, LLM-as-Judge, Reflection, Multi-agent collaboration
- **Master horizontal services** for guardrails, memory, evaluation, and prompt management
- **Evaluate and optimize** agent performance with quantitative metrics
- **Design effective prompts** using Jinja2 templates and persona engineering
- **Deploy production systems** with cost optimization and observability

---

## 🎯 Target Audience

- **Self-directed developers** learning multi-agent systems independently
- **Junior developers** (0-2 years) transitioning to GenAI applications
- **Mid-level developers** (3-5 years) building production agent systems

**Prerequisites**: Intermediate Python, basic LLM prompting, minimal Pydantic AI familiarity

---

## 🚀 Quick Start

### Setup (5 minutes)
```bash
cd composable_app/
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Configure API key
cp keys.env.example keys.env
# Edit keys.env and add your GEMINI_API_KEY
```

### Run the Application
```bash
# Command-line interface
python3 -m cmdline_app

# Web interface (Streamlit)
python3 -m streamlit run streamlit_app.py
```

### Start Learning
1. Read **[Multi-Agent Workflow](tutorials/concepts/multi_agent_workflow.md)** (15 min)
2. Try **[RAG Pattern Tutorial](tutorials/notebooks/rag_pattern_tutorial.ipynb)** (25 min)
3. Follow the learning paths below based on your goals

---

## 📖 Learning Paths

### Path 1: Complete Beginner (6-8 hours)
**Goal**: Understand multi-agent architecture and core patterns

1. **[Multi-Agent Workflow](tutorials/concepts/multi_agent_workflow.md)** (15 min)
   - End-to-end system overview
   - TaskAssigner → Writer → ReviewerPanel → Revision flow

2. **[RAG Pattern Tutorial](tutorials/notebooks/rag_pattern_tutorial.ipynb)** (25 min)
   - Pattern 6: Retrieval-Augmented Generation
   - LlamaIndex vector store with semantic search
   - Citation tracking

3. **[LLM-as-Judge Tutorial](tutorials/notebooks/llm_as_judge_tutorial.ipynb)** (25 min)
   - Pattern 17 & 32: Guardrails
   - InputGuardrail implementation
   - Boolean judge design

4. **[Horizontal Services](tutorials/concepts/horizontal_services.md)** (20 min)
   - Prompt service, guardrails, memory, evaluation
   - Integration points in agents

5. **[Prompt Engineering](tutorials/concepts/prompt_engineering.md)** (25 min)
   - Pattern 25: Jinja2 templates
   - 6 reviewer persona design (specialist + adversarial)

**Outcome**: Build a simple multi-agent system with RAG and guardrails

---

### Path 2: Pattern Specialist (8-10 hours)
**Goal**: Deep dive into all 8 composable design patterns

**Core Patterns** (covered in Path 1):
- ✅ Pattern 6: RAG (Tutorial: `rag_pattern_tutorial.ipynb`)
- ✅ Pattern 17: LLM-as-Judge (Tutorial: `llm_as_judge_tutorial.ipynb`)
- ✅ Pattern 25: Prompt Caching (Tutorial: `prompt_engineering.md`)
- ✅ Pattern 32: Guardrails (Tutorial: `llm_as_judge_tutorial.ipynb`)

**Additional Patterns**:

6. **[Reflection Pattern](tutorials/concepts/reflection_pattern.md)** (20 min)
   - Pattern 18: Writer revision workflow
   - Incorporating panel feedback into prompts
   - Iterative improvement strategies

7. **[Multi-Agent Pattern](tutorials/notebooks/multi_agent_pattern.ipynb)** (30 min)
   - Pattern 23: Parallel ReviewerPanel
   - Specialist vs. adversarial reviewers
   - asyncio.gather() for concurrency

8. **[Architecture Deep Dive](tutorials/concepts/architecture_deep_dive.md)** (30 min)
   - Pattern 19: Dependency Injection
   - AbstractWriter interface design
   - Adding new writers and reviewers

9. **[Long-term Memory](tutorials/concepts/horizontal_services.md#long-term-memory)** (15 min)
   - Pattern 28: Memory integration
   - Personalization via conversation history

**Outcome**: Implement all 8 patterns in your own projects

---

### Path 3: Production Engineer (10-12 hours)
**Goal**: Deploy optimized, production-ready agent systems

**Prerequisites**: Complete Path 1 or Path 2

10. **[Evaluation Tutorial](tutorials/notebooks/evaluation_tutorial.ipynb)** (30 min)
    - Using `evals.log` for improvement
    - Keyword quality metrics with embeddings
    - LLM-as-judge evaluation design

11. **[Advanced Patterns](tutorials/notebooks/advanced_patterns.ipynb)** (35 min)
    - LLM provider switching (Gemini → OpenAI/Anthropic)
    - Cost and latency optimization
    - Temperature tuning and model selection

12. **[Architecture Deep Dive](tutorials/concepts/architecture_deep_dive.md#observability)** (25 min)
    - Structured logging (prompts.json, guards.json, evals.log)
    - Debugging with log analysis
    - Pydantic Logfire integration

13. **[Performance Profiling](tutorials/notebooks/multi_agent_pattern.ipynb#performance)** (20 min)
    - Sequential vs. parallel execution
    - Bottleneck identification
    - asyncio.gather() optimization

**Outcome**: Deploy production systems with monitoring and cost control

---

## 📋 Complete Tutorial List

### Concept Tutorials (.md) - Theory & Architecture

| Tutorial | Time | Topics | Book Chapter |
|----------|------|--------|--------------|
| **[Multi-Agent Workflow](tutorials/concepts/multi_agent_workflow.md)** | 15 min | End-to-end system overview | Ch. 10 |
| **[Reflection Pattern](tutorials/concepts/reflection_pattern.md)** | 20 min | Pattern 18: Writer revision | Ch. 18 |
| **[Horizontal Services](tutorials/concepts/horizontal_services.md)** | 20 min | Guardrails, memory, eval, prompts | Ch. 17, 25, 28 |
| **[Prompt Engineering](tutorials/concepts/prompt_engineering.md)** | 25 min | Pattern 25: Jinja2 + personas | Ch. 25 |
| **[Architecture Deep Dive](tutorials/concepts/architecture_deep_dive.md)** | 30 min | Pattern 19: DI, observability | Ch. 19 |

### Interactive Notebooks (.ipynb) - Hands-On Code

| Tutorial | Time | Cost | Topics | Book Chapter |
|----------|------|------|--------|--------------|
| **[RAG Pattern](tutorials/notebooks/rag_pattern_tutorial.ipynb)** | 25 min | $0.02-0.05 | Pattern 6: LlamaIndex, semantic search | Ch. 6 |
| **[LLM-as-Judge](tutorials/notebooks/llm_as_judge_tutorial.ipynb)** | 25 min | $0.05-0.10 | Pattern 17 & 32: Guardrails | Ch. 17, 32 |
| **[Multi-Agent](tutorials/notebooks/multi_agent_pattern.ipynb)** | 30 min | $0.20-0.40 | Pattern 23: ReviewerPanel, parallelism | Ch. 23 |
| **[Evaluation](tutorials/notebooks/evaluation_tutorial.ipynb)** | 30 min | Free | Using evals.log, metrics design | - |
| **[Advanced Patterns](tutorials/notebooks/advanced_patterns.ipynb)** | 35 min | Varies | Provider switching, optimization | - |

**Total Tutorial Time**: 6-12 hours (depending on path)
**Total API Costs**: $0.30-0.60 (for all notebooks)

---

## 🎨 Visual Diagrams

Located in `tutorials/diagrams/`:

- **[Workflow Diagram](tutorials/diagrams/workflow.png)** - TaskAssigner → Writer → ReviewerPanel → Revision
- **[RAG Flow](tutorials/diagrams/rag_flow.png)** - PDF → Embeddings → Vector Store → Retrieval
- **[ReviewerPanel Architecture](tutorials/diagrams/reviewer_panel.png)** - 6 parallel reviewers with asyncio.gather()

---

## 📊 Tutorial Format Distribution

- **50% Concept Tutorials** (.md): Theory, architecture, design decisions
- **40% Interactive Notebooks** (.ipynb): Executable code with live outputs
- **10% Visual Diagrams** (Mermaid/PNG): Workflow and architecture visualizations

---

## 🔗 Book Chapter Mapping

| Pattern # | Pattern Name | Tutorial | Book Chapter |
|-----------|--------------|----------|--------------|
| 6 | Basic RAG | [rag_pattern_tutorial.ipynb](tutorials/notebooks/rag_pattern_tutorial.ipynb) | Ch. 6 (pp. 142-165) |
| 17 | LLM-as-Judge | [llm_as_judge_tutorial.ipynb](tutorials/notebooks/llm_as_judge_tutorial.ipynb) | Ch. 17 |
| 18 | Reflection | [reflection_pattern.md](tutorials/concepts/reflection_pattern.md) | Ch. 18 |
| 19 | Dependency Injection | [architecture_deep_dive.md](tutorials/concepts/architecture_deep_dive.md) | Ch. 19 |
| 23 | Multi-agent | [multi_agent_pattern.ipynb](tutorials/notebooks/multi_agent_pattern.ipynb) | Ch. 23 |
| 25 | Prompt Caching | [prompt_engineering.md](tutorials/concepts/prompt_engineering.md) | Ch. 25 |
| 28 | Long-term Memory | [horizontal_services.md](tutorials/concepts/horizontal_services.md) | Ch. 28 |
| 32 | Guardrails | [llm_as_judge_tutorial.ipynb](tutorials/notebooks/llm_as_judge_tutorial.ipynb) | Ch. 32 |

**Book**: [*Generative AI Design Patterns*](https://www.oreilly.com/library/view/generative-ai-design/9781098159337/) by Valliappa Lakshmanan and Martin Hapke, O'Reilly Media (October 2025)

---

## 🛠️ Tutorial Features

### Self-Contained Setup
Each tutorial includes:
- Prerequisites and required packages
- API key configuration instructions
- Cost estimates (for notebooks with LLM calls)
- Setup cells with imports and validation

### Common Pitfalls
Every tutorial has a **Common Pitfalls** section addressing:
- ❌ Frequent errors (ImportError, API key issues)
- ⚠️ Performance warnings (using wrong model size)
- 💡 Optimization tips (caching, parallelism)

### Self-Assessment
Tutorials conclude with:
- Concept check questions
- Implementation challenges
- Design trade-off discussions
- Answers provided for immediate feedback

---

## 💰 Cost Transparency

**API Costs for All Notebooks**: ~$0.30-0.60 total

- RAG Pattern: $0.02-0.05 (3-5 queries)
- LLM-as-Judge: $0.05-0.10 (guardrail demos)
- Multi-Agent: $0.20-0.40 (6 reviewers)
- Evaluation: Free (reads logs only)
- Advanced Patterns: Varies (provider testing optional)

**Cost Reduction Tips**:
- Use `SMALL_MODEL` for experimentation (`gemini-2.5-flash-lite`)
- Run notebooks with pre-executed outputs (cached versions)
- Limit top-k in RAG retrieval (use 1-3 instead of 5-10)

---

## 🔧 Troubleshooting

### Common Setup Issues

**❌ "GEMINI_API_KEY not found"**
```bash
# Ensure keys.env exists and has your API key
cat keys.env | grep GEMINI_API_KEY
# Should show: GEMINI_API_KEY=AIza...
```

**❌ "No module named 'pydantic_ai'"**
```bash
pip install --upgrade pydantic-ai
```

**❌ "No module named 'llama_index.embeddings.google_genai'"**
```bash
pip install --upgrade llama-index-embeddings-google-genai
```

**❌ Notebook kernel crashes**
```bash
# Use nest-asyncio for Jupyter compatibility
pip install nest-asyncio
# Add to notebook: import nest_asyncio; nest_asyncio.apply()
```

### Getting Help

- **GitHub Issues**: [Report tutorial issues](https://github.com/lakshmanok/generative-ai-design-patterns/issues)
- **Documentation**: See [ARCHITECTURE.md](ARCHITECTURE.md) and [API_REFERENCE.md](API_REFERENCE.md)
- **Book Support**: [O'Reilly Learning Platform](https://learning.oreilly.com/)

---

## 📝 Tutorial Maintenance

Tutorials are kept in sync with code changes. See [TUTORIAL_CHANGELOG.md](TUTORIAL_CHANGELOG.md) for update history.

**Reporting Issues**:
- Tutorial execution errors
- Outdated code references
- Missing explanations
- Broken links

**Contributing**: We welcome tutorial improvements! See [CONTRIBUTING.md](../CONTRIBUTING.md) for guidelines.

---

## 🎓 After Completing Tutorials

### Next Steps
1. **Adapt to your domain**: Apply patterns to legal, medical, or code review agents
2. **Extend the system**: Add new writers (ScienceWriter, LiteratureWriter)
3. **Optimize for production**: Implement cost monitoring, A/B testing, model distillation
4. **Share your work**: Publish your multi-agent system on GitHub

### Related Resources
- **[Pydantic AI Documentation](https://ai.pydantic.dev)** - LLM-agnostic framework
- **[LlamaIndex Documentation](https://docs.llamaindex.ai)** - RAG implementation
- **[Generative AI Design Patterns Book](https://www.oreilly.com/library/view/generative-ai-design/9781098159337/)** - Complete pattern catalog

---

## 📄 Tutorial System Metadata

- **Version**: 1.0
- **Created**: 2025-11-04
- **Total Tutorials**: 10 (5 concepts + 5 notebooks)
- **Estimated Completion**: 6-12 hours (all paths)
- **Target Completion**: Q1 2026
- **Maintainer**: AI Design Patterns Tutorial Team

---

**Ready to start learning?** Begin with [Multi-Agent Workflow](tutorials/concepts/multi_agent_workflow.md) or choose a learning path above!
