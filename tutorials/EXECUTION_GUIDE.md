# Tutorial Execution Guide

**Last Updated:** 2025-10-30
**Maintained by:** AI Evaluation Course Team

This guide provides comprehensive setup instructions and execution details for all interactive tutorials in the AI Evaluation course.

---

## Table of Contents

- [Prerequisites](#prerequisites)
- [Environment Setup](#environment-setup)
- [Cost Overview](#cost-overview)
- [Tutorial Execution Times](#tutorial-execution-times)
- [DEMO vs FULL Mode](#demo-vs-full-mode)
- [Troubleshooting](#troubleshooting)
- [API Rate Limits](#api-rate-limits)
- [Data Requirements](#data-requirements)

---

## Prerequisites

### System Requirements

- **Python:** 3.11+ (tested on 3.11, 3.12)
- **Operating System:** macOS, Linux, or Windows with WSL
- **Memory:** 4GB RAM minimum (8GB recommended)
- **Disk Space:** 2GB free space for dependencies and data

### Required Software

```bash
# Check Python version
python --version  # Should show 3.11 or higher

# Install uv (fast Python package manager)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Verify installation
uv --version
```

### API Keys Required

All interactive tutorials require at least one LLM API key:

1. **OpenAI API Key** (primary - used in most tutorials)
   - Sign up: https://platform.openai.com/signup
   - Get API key: https://platform.openai.com/api-keys
   - Models used: `gpt-4o`, `gpt-4o-mini`

2. **Anthropic API Key** (optional - for some tutorials)
   - Sign up: https://console.anthropic.com/
   - Get API key: https://console.anthropic.com/settings/keys
   - Models used: `claude-3-5-sonnet-20241022`

---

## Environment Setup

### 1. Clone or Navigate to Repository

```bash
cd /path/to/recipe-chatbot
```

### 2. Create Virtual Environment

```bash
# Using uv (recommended)
uv venv

# Activate virtual environment
source .venv/bin/activate  # macOS/Linux
# or
.venv\Scripts\activate  # Windows
```

### 3. Install Dependencies

```bash
# Install all project dependencies
uv pip install -e .

# Verify installation
python -c "import litellm; import pandas; print('✓ Dependencies installed')"
```

### 4. Configure API Keys

Create a `.env` file in the project root:

```bash
# Copy template
cp env.example .env

# Edit with your API keys
nano .env  # or use any text editor
```

**Required `.env` contents:**

```bash
# OpenAI (required for most tutorials)
OPENAI_API_KEY=sk-...

# Anthropic (optional)
ANTHROPIC_API_KEY=sk-ant-...

# LangSmith (optional - for tracing)
LANGCHAIN_API_KEY=lsv2_pt_...
LANGCHAIN_TRACING_V2=true
LANGCHAIN_PROJECT=recipe-chatbot
```

### 5. Verify Setup

```bash
# Test API connection
python -c "from dotenv import load_dotenv; import os; load_dotenv(); print('OpenAI Key:', 'Found' if os.getenv('OPENAI_API_KEY') else 'Missing')"

# Launch Jupyter (if using notebooks)
jupyter lab
```

---

## Cost Overview

### Total Cost Estimates (All Tutorials)

| Mode | Total Cost | Time Investment |
|------|------------|-----------------|
| **DEMO MODE (all tutorials)** | **$1.50 - 3.00** | **~30-45 minutes** |
| **FULL MODE (all tutorials)** | **$8.00 - 15.00** | **~2-3 hours** |

**Recommendation:** Start with DEMO MODE for all tutorials to learn the workflow, then run FULL MODE selectively for production datasets.

### Per-Tutorial Cost Breakdown

#### Homework 2: Error Analysis

| Tutorial | DEMO Cost | DEMO Time | FULL Cost | FULL Time |
|----------|-----------|-----------|-----------|-----------|
| Dimension Generation | $0.05-0.10 | 1-2 min | $0.20-0.40 | 5-10 min |

**Total HW2:** $0.05-0.10 (DEMO) | $0.20-0.40 (FULL)

---

#### Homework 3: LLM-as-Judge

| Tutorial | DEMO Cost | DEMO Time | FULL Cost | FULL Time |
|----------|-----------|-----------|-----------|-----------|
| Data Labeling | $0 (pre-labeled) | 15-20 min | $2-8* | 30-60 min |
| Judge Development | $0.30-0.50 | 1-2 min | $0.80-1.50 | 3-5 min |

**Total HW3:** $0.30-0.50 (DEMO) | $2.80-9.50 (FULL)

*Cost only if generating new labels with `scripts/label_data.py`

---

#### Homework 4: RAG Evaluation

| Tutorial | DEMO Cost | DEMO Time | FULL Cost | FULL Time |
|----------|-----------|-----------|-----------|-----------|
| Synthetic Query Generation | $0.05-0.15 | 1-2 min | $1.50-2.00 | 3-5 min |

**Total HW4:** $0.05-0.15 (DEMO) | $1.50-2.00 (FULL)

---

#### Lesson 4: Substantiation Evaluation

| Tutorial | DEMO Cost | DEMO Time | FULL Cost | FULL Time |
|----------|-----------|-----------|-----------|-----------|
| Parallel Labeling | $0.05-0.10 | 10-15 sec | $0.50-1.00 | 5-8 min |
| Judge Evaluation Pipeline | $0.10-0.30 | 30-60 sec | $1.00-2.00 | 5-10 min |

**Total Lesson 4:** $0.15-0.40 (DEMO) | $1.50-3.00 (FULL)

---

#### Homework 5 & Lessons 7-8 (No API Costs)

These tutorials use **local data only** - no API calls required:
- HW5: Heatmap Visualization (uses local JSON)
- Lesson 7: Trace Inspection (CSV conversion only)
- Lesson 8: Spam Classification (pre-computed predictions)

**Cost:** $0 | **Time:** 5-15 minutes each

---

## Tutorial Execution Times

### Quick Reference Table

| Tutorial | Location | DEMO Time | FULL Time | API Calls |
|----------|----------|-----------|-----------|-----------|
| **Dimension Generation** | `homeworks/hw2/` | 1-2 min | 5-10 min | Yes |
| **Data Labeling** | `homeworks/hw3/` | 15-20 min | 30-60 min | Optional* |
| **Judge Development** | `homeworks/hw3/` | 1-2 min | 3-5 min | Yes |
| **Synthetic Query Gen** | `homeworks/hw4/` | 1-2 min | 3-5 min | Yes |
| **Heatmap Visualization** | `homeworks/hw5/` | 5-10 min | 5-10 min | No |
| **Parallel Labeling** | `lesson-4/` | 10-15 sec | 5-8 min | Yes |
| **Judge Evaluation** | `lesson-4/` | 30-60 sec | 5-10 min | Yes |
| **Trace Inspection** | `lesson-7/` | 10-15 min | 10-15 min | No |
| **Spam Classification** | `lesson-8/` | 5-10 min | 5-10 min | No |

*Uses pre-labeled data in demo; run `scripts/label_data.py` for new labels (~$2-8)

---

## DEMO vs FULL Mode

All API-heavy notebooks include a **configuration cell** that controls execution mode.

### What is DEMO Mode?

**DEMO MODE** is the **default setting** designed for:
- ✅ Learning the tutorial workflow safely
- ✅ Minimizing API costs during exploration
- ✅ Quick execution for testing setup
- ✅ Classroom demonstrations

**Characteristics:**
- Uses **small sample sizes** (5-20 examples)
- **Total cost: <$0.50** per tutorial
- **Execution time: <2 minutes** per tutorial
- **All features functional** - just smaller scale

### What is FULL Mode?

**FULL MODE** is for **production use** when you need:
- 📊 Complete evaluation datasets (100+ queries)
- 📊 Comprehensive test coverage
- 📊 Statistical significance in metrics
- 📊 Final results for reporting

**Characteristics:**
- Uses **full dataset sizes** (100-200 examples)
- **Total cost: $1-2** per tutorial
- **Execution time: 5-15 minutes** per tutorial
- **Production-ready results**

### How to Switch Modes

Look for the **configuration cell** at the top of each notebook:

```python
# ========================================
# CONFIGURATION: Demo vs Full Mode
# ========================================

# Set DEMO_MODE = False for full dataset
DEMO_MODE = True  # Default: Quick demo for tutorial

if DEMO_MODE:
    NUM_EXAMPLES = 10
    print("🚀 DEMO MODE: Cost ~$0.10 | Time ~1 min")
else:
    NUM_EXAMPLES = 100
    print("📊 FULL MODE: Cost ~$1.50 | Time ~5 min")
```

**To switch:** Change `DEMO_MODE = True` to `DEMO_MODE = False`, then **restart kernel** and re-run notebook.

---

## Troubleshooting

### Common Issues

#### 1. API Key Not Found

**Error:**
```
ValueError: OPENAI_API_KEY not found in environment
```

**Solution:**
```bash
# Verify .env file exists
ls -la .env

# Check contents
cat .env | grep OPENAI_API_KEY

# Reload environment
source .venv/bin/activate
python -c "from dotenv import load_dotenv; load_dotenv(); import os; print(os.getenv('OPENAI_API_KEY'))"
```

#### 2. Module Not Found

**Error:**
```
ModuleNotFoundError: No module named 'litellm'
```

**Solution:**
```bash
# Verify virtual environment is activated
which python  # Should show .venv path

# Reinstall dependencies
uv pip install -e .

# Check specific package
uv pip list | grep litellm
```

#### 3. Notebook Kernel Issues

**Error:**
```
Kernel died unexpectedly
```

**Solution:**
```bash
# Install ipykernel in virtual environment
uv pip install ipykernel

# Register kernel
python -m ipykernel install --user --name=recipe-chatbot

# Restart Jupyter and select "recipe-chatbot" kernel
```

#### 4. API Rate Limits

**Error:**
```
RateLimitError: You exceeded your current quota
```

**Solution:**
1. **Check usage:** Visit https://platform.openai.com/usage
2. **Reduce concurrency:** Lower `max_workers` in parallel processing cells
3. **Switch models:** Use `gpt-4o-mini` instead of `gpt-4o` (10x cheaper)
4. **Enable retry logic:** Already built into tutorials with exponential backoff

#### 5. Data File Not Found

**Error:**
```
FileNotFoundError: data/train_set.csv
```

**Solution:**
- **Check prerequisites:** Previous tutorials must be completed first
- **Run setup scripts:** `python scripts/generate_traces.py` or similar
- **Verify path:** Ensure notebook is run from correct directory

```bash
# Check current directory
pwd

# Should be: /path/to/recipe-chatbot
# If not, cd to project root
```

---

## API Rate Limits

### OpenAI Rate Limits (as of 2024)

| Tier | RPM (Requests/Min) | TPM (Tokens/Min) | Daily Spend |
|------|---------------------|------------------|-------------|
| Free | 3 | 40,000 | $5/day |
| Tier 1 | 500 | 200,000 | $100/day |
| Tier 2 | 5,000 | 2,000,000 | $500/day |

**Our tutorials use:**
- **Parallel workers:** 5-20 concurrent requests
- **Average tokens per request:** 500-1000
- **Recommended tier:** Tier 1 or higher for FULL MODE

### Optimization Strategies

1. **Use DEMO MODE first** - Verify setup before scaling
2. **Reduce `max_workers`** - If hitting rate limits, reduce concurrency:
   ```python
   # In parallel processing cells
   max_workers = 5  # Reduce from 10 or 20
   ```
3. **Add delays** - Insert sleep between batches:
   ```python
   import time
   time.sleep(1)  # Wait 1 second between requests
   ```
4. **Use cheaper models** - Switch to `gpt-4o-mini`:
   ```python
   model = "gpt-4o-mini"  # Instead of "gpt-4o"
   ```

---

## Data Requirements

### File Locations and Dependencies

| Tutorial | Required Input | Generated Output | Dependency |
|----------|----------------|------------------|------------|
| **Dimension Generation** | `.env` (API key) | `synthetic_queries.csv` | None |
| **Data Labeling** | `raw_traces.csv` | `train_set.csv`, `dev_set.csv`, `test_set.csv` | `scripts/generate_traces.py` |
| **Judge Development** | `train/dev/test_set.csv` | `judge_prompt.txt`, `dev_evaluation_results.csv` | Data Labeling Tutorial |
| **Synthetic Query Gen** | `processed_recipes.json` | `synthetic_queries.json` | `scripts/process_recipes.py` |
| **Parallel Labeling** | `nurtureboss_traces.json` | `nurtureboss_traces_labeled.json` | `clean_logs.py` |
| **Judge Evaluation** | `nurtureboss_traces_labeled.json` | `dev_metrics.json` | Parallel Labeling Tutorial |
| **Heatmap Visualization** | `data/labeled_traces.json` | Matplotlib plots | Labeling complete |

### Preparing Data Files

Most tutorials include **sample data** in the repository. For production use:

1. **Generate new traces:**
   ```bash
   python scripts/generate_traces.py --num_queries 100
   ```

2. **Process recipes:**
   ```bash
   python scripts/process_recipes.py --input Gita/recipes.json --output data/processed_recipes.json
   ```

3. **Label data (if needed):**
   ```bash
   python scripts/label_data.py --input data/raw_traces.csv --output data/labeled_traces.csv --num_samples 150
   ```

---

## Best Practices

### 1. Start with DEMO MODE

**Always run tutorials in DEMO MODE first:**
- Verify setup is correct
- Understand the workflow
- Check output quality
- Estimate actual costs

### 2. Monitor Costs

**Track spending as you go:**
```bash
# Check OpenAI usage dashboard frequently
# https://platform.openai.com/usage

# Set up billing alerts in OpenAI console
# Recommended: $10 alert threshold
```

### 3. Save Intermediate Results

**Checkpoint frequently:**
- All notebooks auto-save outputs to disk
- Copy important results to backup location
- Don't re-run expensive cells unnecessarily

### 4. Use Version Control

**Commit notebook outputs:**
```bash
# Save executed notebooks
git add homeworks/*/tutorials/*.ipynb
git commit -m "chore: save tutorial execution results"
```

### 5. Read Error Messages

**Tutorials include detailed error handling:**
- Assertion failures explain what went wrong
- Validation cells catch common mistakes
- Cost warnings prevent overspending

---

## Quick Start Checklist

Use this checklist for each new tutorial:

- [ ] Virtual environment activated
- [ ] Dependencies installed (`uv pip install -e .`)
- [ ] `.env` file configured with API key
- [ ] API key verified with test script
- [ ] Prerequisite tutorials completed (if any)
- [ ] Required data files present
- [ ] Notebook opened in Jupyter Lab
- [ ] Kernel selected (recipe-chatbot)
- [ ] DEMO_MODE = True (for first run)
- [ ] Read cost warning in first cell
- [ ] Execute cells sequentially

---

## Support and Resources

### Documentation

- [Main README](../README.md) - Project overview
- [CLAUDE.md](../CLAUDE.md) - Development guidelines
- [Tutorial Index Files](../homeworks/) - Per-assignment navigation

### Video Walkthroughs

- [HW2 Code Walkthrough](https://youtu.be/h9oAAAYnGx4)
- [Open & Axial Coding](https://youtu.be/AKg27L4E0M8)

### Getting Help

1. **Check error messages** - Most include fix suggestions
2. **Review troubleshooting section** above
3. **Search repository issues** - May be a known problem
4. **Ask in course forum** - Instructors and TAs available

---

## Appendix: Full Cost Table

### Complete Tutorial Cost Summary

| Tutorial | File | DEMO Cost | FULL Cost | Notes |
|----------|------|-----------|-----------|-------|
| **HW2: Dimension Generation** | `dimension_generation_tutorial.ipynb` | $0.05-0.10 | $0.20-0.40 | 5-15 tuples |
| **HW3: Data Labeling** | `data_labeling_tutorial.ipynb` | $0 | $2-8 | Pre-labeled demo data |
| **HW3: Judge Development** | `judge_development_tutorial.ipynb` | $0.30-0.50 | $0.80-1.50 | 20-40 examples |
| **HW4: Synthetic Queries** | `synthetic_query_generation_tutorial.ipynb` | $0.05-0.15 | $1.50-2.00 | 10-100 recipes |
| **HW5: Heatmap Viz** | `heatmap_visualization_tutorial.ipynb` | $0 | $0 | Local data only |
| **Lesson 4: Parallel Labeling** | `parallel_labeling_tutorial.ipynb` | $0.05-0.10 | $0.50-1.00 | 5-200 traces |
| **Lesson 4: Judge Eval** | `judge_evaluation_pipeline_tutorial.ipynb` | $0.10-0.30 | $1.00-2.00 | 20-150 traces |
| **Lesson 7: Trace Inspection** | N/A (concept tutorials only) | $0 | $0 | No API calls |
| **Lesson 8: Spam Classification** | `spam_classification_tutorial.ipynb` | $0 | $0 | Pre-computed data |

**Grand Total:** **$0.55-1.05** (DEMO) | **$6.00-15.90** (FULL)

---

**Guide Version:** 1.0
**Last Updated:** 2025-10-30
**Maintained By:** AI Evaluation Course Team

For updates or corrections, please submit a pull request or contact the course staff.
