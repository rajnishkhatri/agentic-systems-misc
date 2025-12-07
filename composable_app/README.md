## Composable Patterns Application Architecture
You can use this as an example to build a multi-agent system using
simple composable patterns in an LLM- and cloud-agnostic way and
using primarily OSS components.

## 📚 Documentation

- **[TUTORIAL_INDEX.md](TUTORIAL_INDEX.md)** - 🎓 **Start here!** Comprehensive tutorials for learning multi-agent patterns
- **[ARCHITECTURE.md](ARCHITECTURE.md)** - System design, patterns, data flow, and extension points
- **[API_REFERENCE.md](API_REFERENCE.md)** - Complete API documentation for all modules
- **[README.md](README.md)** (this file) - Setup, deployment, and quick start

## Design
Use Pydantic AI for LLM-agnosticity
* Build: https://ai.pydantic.dev/multi-agent-applications/
* Prompt management (Jinja2): https://github.com/pydantic/pydantic-ai/issues/921#issuecomment-2813030935
* Logging: https://docs.python.org/3/library/logging.html

We control these horizontal services and make sure to log inputs and outputs so that we can post-train a SLM later
* Guardrails: see utils/guardrails.py (uses LLM-as-Judge approach) and agents/task_assigner.py for example usage
* Human feedback: see utils/human_feedback.py and pages/1_AssignToWriter.py for example usage
* Eval: see utils/save_for_eval.py and agents/task_assigner.py for example usage
* Memory: see utils/long_term_memory.py and pages/2_CreateDraft.py for example usage

Use commercial off-the-shelf (COTS) tools for monitoring, memory and optionally for guardrails and evaluation:
* Monitoring: https://pydantic.dev/logfire
* Memory: https://github.com/mem0ai/mem0
* Guardrails: https://github.com/guardrails-ai/guardrails (optional: Toxicity, etc. as second layer)

## How to run it locally
Clone the repo and make sure you don't check in your .env file by mistake
```
git clone https://github.com/lakshmanok/generative-ai-design-patterns/
cd generative-ai-design-patterns/composable_app 
```

Create a `.env` file and add your OpenAI API key:
```
OPENAI_API_KEY=sk-...
```

----
### Step-by-step: Get an OpenAI API key
1. Go to the OpenAI API page
👉 https://platform.openai.com/api-keys

2. Sign in with your OpenAI account
Make sure you have credits available in your account.

3. Click "Create new secret key" and copy it
⚠️ **Important**: Save the key immediately - you won't be able to see it again!
---

Install the packages using `uv` (recommended):
```bash
# Install uv if you don't have it
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install dependencies
uv sync
```

Or using traditional pip/venv:
```bash
python3 -m venv venv
source venv/bin/activate
python3 -m pip install -r requirements.txt 
```

Try out the command-line app:
```bash
# Make sure you're in the composable_app directory
cd composable_app

# Using uv
uv run python -m cmdline_app

# Or with traditional setup
python3 -m cmdline_app 
```

Suggested topics:
* Battle of the Bulge
* Solve: x=3 = 5

Try out the GUI interface:
```bash
# Make sure you're in the composable_app directory
cd composable_app

# Using uv (you may see a warning about VIRTUAL_ENV - this is harmless)
uv run streamlit run streamlit_app.py

# If you want to suppress the warning, unset VIRTUAL_ENV first:
unset VIRTUAL_ENV && uv run streamlit run streamlit_app.py

# Or with traditional setup
python3 -m streamlit run streamlit_app.py 
```

Check out the logs, configured in logging.json to save only the prompt texts:
``` cat evals.log ```

### Run containerized app locally
`docker build -t composable-app . && docker run -p 8080:8080 -e OPENAI_API_KEY=your-key composable-app`. 

Replace `your-key` with your actual OpenAI API key.

## How to deploy application as a webapp
This is a Dockerized application; you can deploy it on
a serverless platform such as AWS Farsight or Google Cloud Run.

### Google Cloud Run
Before running the `deploy_to_cloud_run.sh` script, run the following commands to ensure everything is set up:

1. Authenticate with Google Cloud:
```
gcloud auth login
```

2. If the default project selected by auth login is incorrect, set your project:
```
gcloud config set project YOUR_PROJECT_ID
```

3. Set your region:
```
gcloud config set compute/region YOUR_REGION
```
Replace `YOUR_REGION` with your actual region (e.g., `us-central1`).

4. Enable required services:
```
gcloud services enable run.googleapis.com cloudbuild.googleapis.com artifactregistry.googleapis.com
```

5. Create the Artifact Registry repository (if not already created):
```
gcloud artifacts repositories create composable-app-repo --repository-format=docker --location=$(gcloud config get compute/region)
```

6. After these steps, you can run:
```
OPENAI_API_KEY=your-key bash deploy_to_cloud_run.sh
```

<b>Notes</b>
1. If you run the script as `./deploy_to_cloud_run.sh` and get a "Permission denied" or similar error, you can fix this by running: `chmod +x deploy_to_cloud_run.sh`. You will also need the API key set in your environment.
2. For greater security, you can keep your OpenAI API key in the Google Cloud Secret Manager and change utils/llms.py accordingly.


## How it works
The workflow (left) of this application and lifecycle (right) of how it is improved over time are depicted below:
![k12_workflow](k12_content_writing_workflow.png)

All the prompts are in the prompts directory.
Look at the prompts and correlate them with the diagram above.

The code itself involves hooking up the workflow and using the right data structures.

A longer description is in Chapter 10 of the book Generative AI Design Patterns by Lakshmanan and Hapke, to be published October 2025

---

## 🎓 Learning the Patterns

**New to multi-agent systems?** Check out our comprehensive tutorial system:

👉 **[Start with TUTORIAL_INDEX.md](TUTORIAL_INDEX.md)** 👈

**Quick Links**:
- [Multi-Agent Workflow Tutorial](tutorials/concepts/multi_agent_workflow.md) - System overview (15 min)
- [RAG Pattern Tutorial](tutorials/notebooks/rag_pattern_tutorial.ipynb) - Hands-on LlamaIndex (25 min)
- [Complete Tutorial List](TUTORIAL_INDEX.md#-complete-tutorial-list) - All 10 tutorials

**What You'll Learn**:
- Build multi-agent systems with TaskAssigner, Writers, and ReviewerPanel
- Implement 8+ design patterns (RAG, LLM-as-Judge, Reflection, Multi-agent, etc.)
- Master horizontal services (guardrails, memory, evaluation, prompts)
- Optimize for production (cost, latency, observability)

**Total Learning Time**: 6-12 hours | **API Costs**: ~$0.30-0.60

