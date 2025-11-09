# Lesson 10: AI-as-Judge Mastery & Production Patterns

## Overview

This lesson covers AI-as-Judge evaluation methodology and production engineering patterns. You'll learn to engineer effective judge prompts, detect and mitigate biases, and implement production-grade judge systems with proper abstraction and testing.

---

## Prerequisites

- Completion of HW3 and Lesson 9
- Understanding of prompt engineering fundamentals
- Python 3.10+ with Jupyter notebook support
- OpenAI API key (required for all notebooks)

---

## Learning Time

**Total:** ~4-5 hours
- Reading: 25-30 minutes (1 comprehensive guide)
- Template review: 30-40 minutes (15 judge templates)
- Hands-on: 15-20 minutes (2 interactive notebooks)
- Exercises: 2-3 hours (optional)

---

## Setup

### 1. Install Dependencies

```bash
# Ensure you're in the project root
pip install -r requirements.txt

# All dependencies should already be installed from Lesson 9
# Verify installation
python -c "import openai; print('OpenAI SDK installed')"
```

### 2. Configure Environment

```bash
# Ensure .env exists with OpenAI API key
# Required for all notebooks in this lesson
cat .env | grep OPENAI_API_KEY

# If not set:
echo "OPENAI_API_KEY=sk-..." >> .env
```

### 3. Verify Backend Access

```python
# Test that backend imports work
from backend.ai_judge_framework import BaseJudge, DietaryAdherenceJudge
print("Backend modules accessible")
```

---

## Cost Estimate

| Notebook | Mode | API Calls | Estimated Cost |
|----------|------|-----------|----------------|
| Judge Prompt Engineering | DEMO | 5 criteria × 5 queries × GPT-4o-mini | $0.30-0.50 |
| Judge Prompt Engineering | FULL | 5 criteria × 25 queries × GPT-4o | $1.50-2.50 |
| Judge Bias Detection | DEMO | 3 bias types × 10 pairs × GPT-4o-mini | $0.50-1.00 |
| Judge Bias Detection | FULL | 3 bias types × 30 pairs × GPT-4o | $2.00-3.00 |

**Total (DEMO mode):** $0.80-1.50
**Total (FULL mode):** $3.50-5.50

**💡 Tip:** Always start with DEMO mode to understand notebooks before running FULL mode.

---

## Quick Start

### Recommended Learning Path

1. **Start here:** Read [`TUTORIAL_INDEX.md`](TUTORIAL_INDEX.md) for navigation and learning objectives
2. **Concept tutorial:** Read `ai_judge_production_guide.md` (25-30 min)
3. **Template review:** Browse 15 judge templates in `templates/judge_prompts/` (30-40 min)
   - Focus on templates relevant to your use case
   - Note the structure: role → task → criteria → scoring → examples
4. **Hands-on practice:** Run both notebooks in DEMO mode:
   - `judge_prompt_engineering_tutorial.ipynb` (8-10 min)
   - `judge_bias_detection_tutorial.ipynb` (<5 min)
5. **Build your judge:** Customize a template for your specific evaluation task
6. **Validate:** Calculate TPR/TNR on manually labeled validation set

---

## Files in This Lesson

### Tutorials
- `TUTORIAL_INDEX.md` - Navigation hub
- `ai_judge_production_guide.md` - Comprehensive judge engineering guide

### Notebooks
- `judge_prompt_engineering_tutorial.ipynb` - Engineer judges for 5 criteria, test scoring systems
- `judge_bias_detection_tutorial.ipynb` - Detect self-bias, position bias, verbosity bias

### Templates (15 reusable judge prompts)

#### Safety & Correctness
- `templates/judge_prompts/dietary_adherence_judge.txt`
- `templates/judge_prompts/factual_correctness_judge.txt`
- `templates/judge_prompts/toxicity_detection_judge.txt`
- `templates/judge_prompts/hallucination_detection_judge.txt`
- `templates/judge_prompts/safety_judge.txt`

#### Quality & Coherence
- `templates/judge_prompts/coherence_judge.txt`
- `templates/judge_prompts/helpfulness_judge.txt`
- `templates/judge_prompts/response_length_appropriateness_judge.txt`
- `templates/judge_prompts/creativity_judge.txt`

#### Verification & Analysis
- `templates/judge_prompts/substantiation_judge.txt`
- `templates/judge_prompts/citation_quality_judge.txt`
- `templates/judge_prompts/contradiction_detection_judge.txt`
- `templates/judge_prompts/instruction_following_judge.txt`
- `templates/judge_prompts/cultural_sensitivity_judge.txt`
- `templates/judge_prompts/code_quality_judge.txt`

### Diagrams
- `diagrams/judge_decision_tree.mmd` - Which judge type to use (will be generated)
- `diagrams/judge_bias_patterns.png` - Bias visualization (will be generated)

---

## Key Learning Outcomes

After completing this lesson, you will:
- ✅ Engineer production-ready judge prompts for diverse criteria
- ✅ Detect and mitigate common judge biases
- ✅ Select appropriate judge models based on cost-quality trade-offs
- ✅ Implement reusable judge abstractions (BaseJudge pattern)
- ✅ Measure judge quality using TPR/TNR and confusion matrices
- ✅ Apply few-shot learning and chain-of-thought to improve judges

---

## Reusable Components

### BaseJudge Abstraction

This lesson introduces a reusable judge framework in `backend/ai_judge_framework.py`:

```python
from backend.ai_judge_framework import BaseJudge, GenericCriteriaJudge

# Create a custom judge
judge = GenericCriteriaJudge(
    criterion="helpfulness",
    prompt_template="templates/judge_prompts/helpfulness_judge.txt",
    model="gpt-4o-mini"
)

# Evaluate a response
result = judge.evaluate(
    query="How do I make carbonara?",
    response="Carbonara requires eggs, cheese, guanciale...",
    context=None  # Optional
)

print(result.verdict)  # True/False
print(result.score)    # 0-1 or Likert scale
print(result.reasoning)  # Explanation
```

**Three concrete implementations:**
1. `DietaryAdherenceJudge` - From HW3, refactored
2. `SubstantiationJudge` - From Lesson 4, refactored
3. `GenericCriteriaJudge` - Flexible template-based judge

---

## Testing Your Understanding

### Self-Check Questions

1. What are the three most common judge biases and how do you detect them?
2. When should you use GPT-4o vs GPT-4o-mini for judging?
3. What's the difference between TPR and TNR? Which is more important for safety-critical applications?
4. Why is few-shot prompting often essential for judges but not for generative tasks?

**Answers:** See FAQ in TUTORIAL_INDEX.md

---

## Next Steps

After completing Lesson 10:
- ✅ **Move to Lesson 11:** Learn comparative evaluation and leaderboard ranking
- ✅ **Refactor existing judges:** Migrate HW3/Lesson 4 judges to use BaseJudge abstraction
- ✅ **Build custom judges:** Create judges for your specific evaluation criteria
- ✅ **Validate thoroughly:** Always calculate TPR/TNR on labeled validation set before production use

👉 [Lesson 11: Comparative Evaluation & Leaderboards](../lesson-11/README.md)
👉 [Evaluation Dashboard](../lesson-9-11/README.md)

---

## Troubleshooting

### Common Issues

**"OpenAI API key not found"**
```bash
# Verify .env exists and contains key
cat .env | grep OPENAI_API_KEY

# If missing, add it
echo "OPENAI_API_KEY=sk-..." >> .env
```

**"Rate limit exceeded"**
```python
# In notebook, reduce DEMO_MODE queries or add delays
import time
time.sleep(1)  # Between API calls
```

**"Judge returns inconsistent results"**
- Add few-shot examples to stabilize behavior
- Increase temperature from 0.0 to 0.3 if too deterministic
- Test with multiple runs and aggregate (majority vote)

**"Low TPR (missing failures)"**
- Add failure examples to few-shot prompt
- Make criteria more explicit
- Use more capable model (GPT-4o instead of GPT-4o-mini)
- Add chain-of-thought reasoning

**"Low TNR (too many false alarms)"**
- Add success examples to few-shot prompt
- Tighten criteria language
- Adjust threshold if using continuous scores

---

## Support

- **Questions?** See FAQ in [TUTORIAL_INDEX.md](TUTORIAL_INDEX.md)
- **Issues?** Check troubleshooting section above
- **Template requests?** Open an issue to request new judge templates
- **Feedback?** Contribute improvements to existing templates

---

## ⚠️ Important Reminders

1. **Always start with DEMO mode** to avoid unexpected costs
2. **Validate judges with ground truth** before production use (calculate TPR/TNR)
3. **Test for biases systematically** (position, verbosity, self-preference)
4. **Version your prompts** - track which version was used for each evaluation
5. **Monitor costs** - GPT-4o judge calls add up quickly at scale

---

**Last Updated:** 2025-11-09
**Estimated Completion Time:** 4-5 hours
**Difficulty:** Intermediate to Advanced
