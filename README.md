# Recipe Chatbot - AI Evaluations Course

This repository contains a complete AI evaluations course built around a Recipe Chatbot. Through 5 progressive homework assignments, you'll learn practical techniques for evaluating and improving AI systems.

## Quick Start

1. **Clone & Setup**
   ```bash
   git clone https://github.com/ai-evals-course/recipe-chatbot.git
   cd recipe-chatbot
   uv sync  # Installs dependencies and creates virtual environment
   ```

2. **Configure Environment**
   ```bash
   cp env.example .env
   # Edit .env to add your model and API keys
   ```

3. **Run the Chatbot**
   ```bash
   uv run uvicorn backend.main:app --reload
   # Open http://127.0.0.1:8000
   ```

## Development with uv

This project uses [uv](https://docs.astral.sh/uv/) for fast Python package management and virtual environment handling.

### Key Commands

- **Install dependencies**: `uv sync`
- **Run the chatbot**: `uv run uvicorn backend.main:app --reload`
- **Run tests**: `uv run pytest tests/`
- **Add new dependency**: `uv add package-name`
- **Add dev dependency**: `uv add --dev package-name`
- **Run any script**: `uv run python script.py`

### Benefits of uv

- ⚡ **Fast**: 10-100x faster than pip
- 🔒 **Reliable**: Deterministic dependency resolution
- 🎯 **Simple**: Single tool for virtual envs, dependencies, and running code
- 📦 **Modern**: Built-in support for pyproject.toml and modern Python packaging

## Course Overview

### Homework Progression

1. **HW1: Basic Prompt Engineering** (`homeworks/hw1/`)
   - Write system prompts and expand test queries
   - Walkthrough: See HW2 walkthrough for HW1 content

2. **HW2: Error Analysis & Failure Taxonomy** (`homeworks/hw2/`)
   - Systematic error analysis and failure mode identification
   - **Interactive Walkthrough**:
      - Code: `homeworks/hw2/hw2_solution_walkthrough.ipynb`
      - [video 1](https://youtu.be/h9oAAAYnGx4?si=fWxN3NtpSbdD55cW): walkthrough of code
      - [video 2](https://youtu.be/AKg27L4E0M8) : open & axial coding walkthrough

3. **HW3: LLM-as-Judge Evaluation** (`homeworks/hw3/`)
   - Automated evaluation using the `judgy` library
   - **Interactive Walkthrough**:
      - Code: `homeworks/hw3/hw3_walkthrough.ipynb`
      - [video](https://youtu.be/1d5aNfslwHg): walkthrough of solution

4. **HW4: RAG/Retrieval Evaluation** (`homeworks/hw4/`)
   - BM25 retrieval system with synthetic query generation
   - **Interactive Walkthroughs**: 
     - `homeworks/hw4/hw4_walkthrough.py` (Marimo)
     - [video](https://youtu.be/GMShL5iC8aY): walkthrough of solution

5. **HW5: Agent Failure Analysis** (`homeworks/hw5/`)
   - Analyze conversation traces and failure patterns
   - **Interactive Walkthroughs**:
      - `homeworks/hw5/hw5_walkthrough.py` (Marimo)
      - [video](https://youtu.be/z1oISsDUKLA) 

### Key Features

- **Backend**: FastAPI with LiteLLM (multi-provider LLM support)
- **Frontend**: Simple chat interface with conversation history
- **Annotation Tool**: FastHTML-based interface for manual evaluation (`annotation/`)
- **Retrieval**: BM25-based recipe search (`backend/retrieval.py`)
- **Query Rewriting**: LLM-powered query optimization (`backend/query_rewrite_agent.py`)
- **Evaluation Tools**: Automated metrics, bias correction, and analysis scripts

## Project Structure

```
recipe-chatbot/
├── backend/               # FastAPI app & core logic
├── frontend/              # Chat UI (HTML/CSS/JS)
├── homeworks/             # 5 progressive assignments
│   ├── hw1/              # Prompt engineering
│   ├── hw2/              # Error analysis (with walkthrough)
│   ├── hw3/              # LLM-as-Judge (with walkthrough)
│   ├── hw4/              # Retrieval eval (with walkthroughs)
│   └── hw5/              # Agent analysis
├── annotation/            # Manual annotation tools
├── scripts/               # Utility scripts
├── data/                  # Datasets and queries
└── results/               # Evaluation outputs
```

## Running Homework Scripts

Each homework includes complete pipelines. For example:

**HW3 Pipeline:**
```bash
cd homeworks/hw3
python scripts/generate_traces.py
python scripts/label_data.py
python scripts/develop_judge.py
python scripts/evaluate_judge.py
```

**HW4 Pipeline:**
```bash
cd homeworks/hw4
python scripts/process_recipes.py
python scripts/generate_queries.py
python scripts/evaluate_retrieval.py
# Optional: python scripts/evaluate_retrieval_with_agent.py
```

## Additional Resources

- **Annotation Interface**: Run `python annotation/annotation.py` for manual evaluation
- **Bulk Testing**: Use `python scripts/bulk_test.py` to test multiple queries
- **Trace Analysis**: All conversations saved as JSON for analysis

## Environment Variables

Configure your `.env` file with:
- `MODEL_NAME`: LLM model for chatbot (e.g., `openai/gpt-5-chat-latest`, `anthropic/claude-3-sonnet-20240229`)
- `MODEL_NAME_JUDGE`: LLM model for judge, which can be smaller than the chatbot model (e.g., `openai/gpt-5-mini`, `anthropic/claude-3-haiku-20240307`)
- API keys: `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, etc.

See [LiteLLM docs](https://docs.litellm.ai/docs/providers) for supported providers.

## Tutorials

📚 **Comprehensive tutorial system available!** Each homework and lesson now includes detailed tutorials, interactive notebooks, and visual diagrams.

### Homework Tutorials
- **[HW1: Prompt Engineering](homeworks/hw1/TUTORIAL_INDEX.md)** - System prompts and query diversity
- **[HW2: Error Analysis](homeworks/hw2/TUTORIAL_INDEX.md)** - Open/axial coding, failure taxonomies
- **[HW3: LLM-as-Judge](homeworks/hw3/TUTORIAL_INDEX.md)** - Automated evaluation with bias correction
- **[HW4: RAG Evaluation](homeworks/hw4/TUTORIAL_INDEX.md)** - BM25 retrieval and synthetic queries
- **[HW5: Agent Failure Analysis](homeworks/hw5/TUTORIAL_INDEX.md)** - Transition matrices and heatmaps

### Lesson Tutorials
- **[Lesson 4: Substantiation Evaluation](lesson-4/TUTORIAL_INDEX.md)** - Detecting unsubstantiated claims
- **[Lesson 7: Trace Inspection](lesson-7/TUTORIAL_INDEX.md)** - Manual annotation workflows
- **[Lesson 8: Model Cascades](lesson-8/TUTORIAL_INDEX.md)** - Cost optimization with confidence routing
- **[Lesson 9: Evaluation Fundamentals & Exact Methods](lesson-9/TUTORIAL_INDEX.md)** - Perplexity, BLEU, semantic similarity
- **[Lesson 10: AI-as-Judge Mastery & Production Patterns](lesson-10/TUTORIAL_INDEX.md)** - Judge engineering and bias detection
- **[Lesson 11: Comparative Evaluation & Leaderboards](lesson-11/TUTORIAL_INDEX.md)** - Elo and Bradley-Terry ranking systems
- **[Lesson 16: Agent Reliability - Enterprise Patterns](lesson-16/TUTORIAL_INDEX.md)** - Multi-agent orchestration, reliability framework, production deployment

### Cross-Lesson Resources
- **[Evaluation Dashboard (Lessons 9-11)](lesson-9-11/README.md)** - Unified metrics visualization across all evaluation methods

Each tutorial index includes:
- ✅ Learning objectives and prerequisites
- ✅ Recommended learning paths
- ✅ Interactive notebooks and visualizations
- ✅ Common pitfalls and FAQs
- ✅ Real-world applications

## Course Philosophy

This course emphasizes:
- **Practical experience** over theory
- **Systematic evaluation** over "vibes"
- **Progressive complexity** - each homework builds on previous work
- **Industry-standard techniques** for real-world AI evaluation
