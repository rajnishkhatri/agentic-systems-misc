# Composable App Tutorials - Quick Start Guide

**Welcome!** This directory contains comprehensive tutorials for building production-ready multi-agent systems using composable design patterns.

---

## 🚀 5-Minute Quick Start

### 1. Install Dependencies
```bash
cd composable_app/
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure API Key
```bash
# Copy example environment file
cp keys.env.example keys.env

# Edit keys.env and add your Gemini API key
# Get your key at: https://makersuite.google.com/app/apikey
nano keys.env  # or use your preferred editor
```

Add this line to `keys.env`:
```
GEMINI_API_KEY=AIza...your_key_here
```

### 3. Verify Setup
```bash
# Test command-line interface
python3 -m cmdline_app
# Try queries like: "Battle of the Bulge" or "Solve: x + 3 = 5"

# Or launch web interface
python3 -m streamlit run streamlit_app.py
```

### 4. Start Learning
Open [`TUTORIAL_INDEX.md`](../TUTORIAL_INDEX.md) and choose your learning path!

---

## 📚 Tutorial Structure

```
tutorials/
├── README.md                          # This file (quick start)
├── concepts/                          # Theory & architecture (50%)
│   ├── multi_agent_workflow.md        # System overview
│   ├── reflection_pattern.md          # Pattern 18: Revision
│   ├── horizontal_services.md         # Guardrails, memory, eval
│   ├── prompt_engineering.md          # Jinja2 + personas
│   └── architecture_deep_dive.md      # DI, observability
├── notebooks/                         # Interactive code (40%)
│   ├── rag_pattern_tutorial.ipynb     # Pattern 6: RAG
│   ├── llm_as_judge_tutorial.ipynb    # Pattern 17: Guardrails
│   ├── multi_agent_pattern.ipynb      # Pattern 23: ReviewerPanel
│   ├── evaluation_tutorial.ipynb      # Using evals.log
│   └── advanced_patterns.ipynb        # Optimization
└── diagrams/                          # Visual aids (10%)
    ├── workflow.mmd / .png             # System workflow
    ├── rag_flow.mmd / .png             # RAG architecture
    └── reviewer_panel.mmd / .png       # ReviewerPanel
```

---

## 🎯 Learning Paths

### Beginner (6-8 hours)
**Goal**: Understand multi-agent architecture and core patterns

1. [Multi-Agent Workflow](concepts/multi_agent_workflow.md) (15 min)
2. [RAG Pattern](notebooks/rag_pattern_tutorial.ipynb) (25 min)
3. [LLM-as-Judge](notebooks/llm_as_judge_tutorial.ipynb) (25 min)
4. [Horizontal Services](concepts/horizontal_services.md) (20 min)
5. [Prompt Engineering](concepts/prompt_engineering.md) (25 min)

### Pattern Specialist (8-10 hours)
**Goal**: Master all 8 composable design patterns

Complete Beginner path, then:
6. [Reflection Pattern](concepts/reflection_pattern.md) (20 min)
7. [Multi-Agent Pattern](notebooks/multi_agent_pattern.ipynb) (30 min)
8. [Architecture Deep Dive](concepts/architecture_deep_dive.md) (30 min)

### Production Engineer (10-12 hours)
**Goal**: Deploy optimized, production-ready systems

Complete Pattern Specialist path, then:
9. [Evaluation Tutorial](notebooks/evaluation_tutorial.ipynb) (30 min)
10. [Advanced Patterns](notebooks/advanced_patterns.ipynb) (35 min)
11. Performance profiling and observability sections

---

## 💻 Running Jupyter Notebooks

### Option 1: Jupyter Lab (Recommended)
```bash
pip install jupyterlab
jupyter lab
# Navigate to composable_app/tutorials/notebooks/
```

### Option 2: VS Code
1. Install [Jupyter extension](https://marketplace.visualstudio.com/items?itemName=ms-toolsai.jupyter)
2. Open `.ipynb` file
3. Select Python kernel from virtual environment

### Option 3: Jupyter Notebook
```bash
pip install notebook
jupyter notebook
# Navigate to notebooks directory
```

### Troubleshooting Notebooks

**Kernel crashes on startup**:
```bash
pip install nest-asyncio
# Add to first cell: import nest_asyncio; nest_asyncio.apply()
```

**Import errors**:
```bash
# Ensure virtual environment is activated
source venv/bin/activate
pip install -r requirements.txt
```

**API key not found**:
```bash
# Verify keys.env exists and is correctly formatted
cat keys.env | grep GEMINI_API_KEY
```

---

## 💰 API Costs

**Total for all notebooks**: ~$0.30-0.60

| Notebook | Estimated Cost | API Calls |
|----------|---------------|-----------|
| RAG Pattern | $0.02-0.05 | 3-5 queries |
| LLM-as-Judge | $0.05-0.10 | 5-8 guardrail checks |
| Multi-Agent | $0.20-0.40 | 6 reviewers × 2-3 articles |
| Evaluation | Free | Reads logs only |
| Advanced | Varies | Optional provider testing |

**Cost Reduction Tips**:
- Run notebooks with pre-executed outputs (read without executing)
- Use `SMALL_MODEL` for experimentation: `utils/llms.py` → `gemini-2.5-flash-lite`
- Limit RAG retrieval: `similarity_top_k=1` instead of `3`
- Cache results: Save notebook after first run

---

## 📖 Tutorial Features

### Every Tutorial Includes:
- ✅ **Prerequisites**: Required knowledge and setup
- ✅ **Estimated time**: Realistic completion time
- ✅ **Learning objectives**: What you'll learn
- ✅ **Common Pitfalls**: Debugging tips and solutions
- ✅ **Self-Assessment**: Questions with answers
- ✅ **Book references**: Links to pattern chapters

### Notebook-Specific Features:
- ⚠️ **Cost warnings**: API usage estimates upfront
- 🔧 **Setup cells**: Imports, API validation, path setup
- 📊 **Live outputs**: Pre-executed cells with results
- 💡 **Inline explanations**: Code comments for every section

---

## 🔗 Related Documentation

- **[TUTORIAL_INDEX.md](../TUTORIAL_INDEX.md)** - Complete tutorial catalog with learning paths
- **[TUTORIAL_CHANGELOG.md](../TUTORIAL_CHANGELOG.md)** - Tutorial maintenance log
- **[ARCHITECTURE.md](../ARCHITECTURE.md)** - System design and patterns
- **[API_REFERENCE.md](../API_REFERENCE.md)** - Complete API documentation
- **[README.md](../README.md)** - Main application documentation

---

## 🛠️ Troubleshooting

### Common Setup Issues

#### "GEMINI_API_KEY not found"
**Solution**:
```bash
# Check if keys.env exists
ls -la keys.env

# Verify API key is set
cat keys.env | grep GEMINI_API_KEY

# If missing, create from example
cp keys.env.example keys.env
# Then edit keys.env and add: GEMINI_API_KEY=AIza...
```

#### "No module named 'pydantic_ai'"
**Solution**:
```bash
pip install --upgrade pydantic-ai
```

#### "No module named 'llama_index.embeddings.google_genai'"
**Solution**:
```bash
pip install --upgrade llama-index-embeddings-google-genai
```

#### Vector index not found (RAG tutorial)
**Solution**:
```bash
# Check if index exists
ls -la composable_app/data/*vector_store.json

# If missing, create index (requires book PDF)
python -m composable_app.data.create_index

# Or use sample index (if provided)
cp composable_app/data/sample_vector_store.json composable_app/data/default__vector_store.json
```

#### Notebook kernel not starting
**Solution**:
```bash
# Ensure virtual environment kernel is installed
pip install ipykernel
python -m ipykernel install --user --name=venv --display-name "Composable App (venv)"

# In Jupyter, select kernel: Kernel → Change Kernel → "Composable App (venv)"
```

---

## 🎓 Learning Tips

### For Concept Tutorials (.md)
1. **Read actively**: Take notes on key patterns
2. **Click code links**: Explore referenced implementation
3. **Try Common Pitfalls**: Intentionally trigger errors to learn debugging
4. **Answer self-assessment**: Check understanding before moving on

### For Jupyter Notebooks (.ipynb)
1. **Execute sequentially**: Run cells top-to-bottom (don't skip)
2. **Modify parameters**: Experiment with different values
3. **Read outputs carefully**: Understand what LLM returns
4. **Check costs**: Monitor API usage as you go
5. **Save your work**: Export modified notebooks for reference

### For Diagrams
1. **Start with visuals**: Understand workflow before code
2. **Reference during coding**: Keep diagrams open while reading tutorials
3. **Use Mermaid editor**: Modify diagrams at [mermaid.live](https://mermaid.live/)

---

## 🤝 Contributing

Found an issue or want to improve tutorials?

1. **Report Issues**: [GitHub Issues](https://github.com/lakshmanok/generative-ai-design-patterns/issues)
2. **Check Changelog**: See [TUTORIAL_CHANGELOG.md](../TUTORIAL_CHANGELOG.md) for known issues
3. **Contributing Guide**: See [CONTRIBUTING.md](../../CONTRIBUTING.md)

**Common Contributions**:
- Fixing typos or unclear explanations
- Adding Common Pitfalls from your experience
- Improving code examples
- Creating additional exercises

---

## 📚 Book Reference

These tutorials complement:

**[Generative AI Design Patterns](https://www.oreilly.com/library/view/generative-ai-design/9781098159337/)**
By Valliappa Lakshmanan and Martin Hapke
O'Reilly Media, October 2025

The `composable_app/` is the reference implementation for Chapter 10 (Multi-Agent Systems) and demonstrates 8+ patterns from throughout the book.

---

## 📊 Tutorial Completion Tracking

Track your progress:

- [ ] Completed Beginner Path (6-8 hours)
- [ ] Completed Pattern Specialist Path (8-10 hours)
- [ ] Completed Production Engineer Path (10-12 hours)
- [ ] Built a custom multi-agent system
- [ ] Adapted patterns to my own project

---

## 🎯 After Completing Tutorials

### Next Steps
1. **Adapt to your domain**: Apply patterns to legal, medical, code review agents
2. **Extend the system**: Add ScienceWriter, LiteratureWriter
3. **Optimize for production**: Cost monitoring, A/B testing, distillation
4. **Share your work**: Publish on GitHub, write blog posts

### Additional Resources
- [Pydantic AI Documentation](https://ai.pydantic.dev) - LLM-agnostic framework
- [LlamaIndex Documentation](https://docs.llamaindex.ai) - RAG implementation
- [O'Reilly Learning Platform](https://learning.oreilly.com/) - Full book access

---

**Ready to start?** Open [TUTORIAL_INDEX.md](../TUTORIAL_INDEX.md) and begin your learning journey!

**Questions?** See troubleshooting above or check [TUTORIAL_INDEX.md#getting-help](../TUTORIAL_INDEX.md#-troubleshooting)

---

**Version**: 1.0
**Created**: 2025-11-04
**Estimated Setup Time**: 5 minutes
**Total Learning Time**: 6-12 hours (all paths)
