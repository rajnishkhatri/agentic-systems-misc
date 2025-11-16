# Section C: Advanced Evaluation

## Overview

This section covers advanced agent evaluation beyond trajectory metrics: autorater-based final response evaluation, human-in-the-loop workflows, and production evaluation infrastructure. You'll learn when trajectory metrics aren't enough, how to calibrate LLM judges, and how to integrate human feedback for active learning.

**Learning Time:** 3-4 hours (comprehensive) | 2 hours (focused)
**Difficulty:** ⭐⭐⭐⭐⭐
**Prerequisites:** Section A (Trajectory Evaluation), HW3 (LLM-as-Judge), Lesson 10 (Judge Prompt Engineering)

---

## Learning Objectives

By completing this section, you will be able to:

✅ Design custom success criteria for domain-specific agents beyond trajectory metrics
✅ Implement autorater prompts with structured output and chain-of-thought reasoning
✅ Calibrate autoraters using human feedback and measure inter-annotator agreement
✅ Apply 3 HITL methods: Direct assessment, comparative evaluation, user studies
✅ Build active learning workflows to maximize human feedback efficiency
✅ Set up production evaluation infrastructure with Google Vertex AI Eval Service

---

## Content Inventory

### Tutorials (4)
14. **14_Agent_Evaluation_Methodology.md** (40 min) - Google Companion complete framework
15. **15_autorater_final_response_eval.md** (20 min) - Custom success criteria & LLM judges
16. **16_human_in_the_loop_evaluation.md** (20 min) - 3 HITL methods & active learning
17. **17_Vertex_AI_Ecosystem.md** (20 min) - Google Companion tooling & infrastructure

### Notebooks (2)
22. **22_autorater_calibration.ipynb** (12 min) - Measure agreement, identify biases
23. **23_benchmark_evaluation.ipynb** (10 min) - Run complete test suite

### Data (2)
- **agent_responses_sample.json** - 30+ sample responses for calibration
- **human_annotations.json** - Expert judgments (quality, accuracy, safety)

### Results (2)
- **autorater_calibration_results.json** - Cohen's Kappa, systematic biases
- **benchmark_results.json** - Comprehensive performance across all benchmarks

---

## Recommended Learning Path

### Quick Start (2 hours)
**Goal:** Calibrate an autorater and run benchmarks

```
Step 1: Understand evaluation framework (30 min)
  → Read: 15_autorater_final_response_eval.md
  → Read: 14_Agent_Evaluation_Methodology.md (skim)

Step 2: Hands-on calibration (1 hour)
  → Run: 22_autorater_calibration.ipynb
  → Analyze agreement scores
  → Identify systematic biases

Step 3: Benchmark suite (30 min)
  → Run: 23_benchmark_evaluation.ipynb
  → Review performance across all categories
```

### Comprehensive Path (3-4 hours)
**Goal:** Master advanced evaluation methodology

```
Week 1 (3-4 hours)
  Day 1: Read 14_Agent_Evaluation_Methodology.md (40 min)
         → Understand 3 evaluation pillars (trajectory, autorater, HITL)

  Day 2: Read 15_autorater_final_response_eval.md (20 min)
         → Design custom success criteria
         → Implement autorater prompts

  Day 3: Read 16_human_in_the_loop_evaluation.md (20 min)
         → Learn 3 HITL methods
         → Design active learning workflows

  Day 4: Run 22_autorater_calibration.ipynb (12 min)
         → Measure inter-annotator agreement
         → Adjust prompts based on disagreement

  Day 5: Run 23_benchmark_evaluation.ipynb (10 min)
         → Systematic evaluation across all tests
         → Generate comprehensive report

  Day 6: Read 17_Vertex_AI_Ecosystem.md (20 min)
         → Production deployment infrastructure
```

---

## Key Concepts

### 1. Three Pillars of Agent Evaluation

| Pillar | What It Evaluates | Cost | Latency | Quality | Coverage |
|--------|-------------------|------|---------|---------|----------|
| **Trajectory** | Process (tool calls) | $0 | <1ms | Medium | High (if ground-truth exists) |
| **Autorater** | Outcome (response quality) | $0.01-0.10 | 1-5s | High (if calibrated) | High |
| **HITL** | Gold standard validation | $1-10 | Hours-Days | Highest | Low (expensive) |

**Recommended:** Use all three!
- **Trajectory metrics** for process validation (correct path?)
- **Autoraters** for outcome validation (good response?)
- **HITL** for autorater calibration and edge case validation

### 2. When Trajectory Metrics Aren't Enough

**Example: Recipe Agent**

**Trajectory Metric Result:**
```
Exact Match: ✅ 100% (used correct tool call sequence)
```

**But actual response quality:**
```
User: "Find vegan Italian recipes for dinner"
Agent: [Returns 3 Italian dessert recipes that happen to be vegan]
```

**Problem:** Trajectory was technically correct, but response doesn't meet user intent!

**Solution:** Add autorater evaluation for:
- ✅ Intent alignment (dinner ≠ dessert)
- ✅ Result relevance (are results useful?)
- ✅ Completeness (enough recipes?)

### 3. Autorater Design Pattern

**Components:**
1. **Evaluation Dimensions** - What to measure (accuracy, safety, relevance, completeness)
2. **Success Criteria** - Domain-specific requirements
3. **Structured Output** - JSON schema for consistent scoring
4. **Chain-of-Thought** - Reasoning before judgment (improves accuracy)
5. **Rubric/Examples** - Few-shot demonstrations

**Template:**
```python
AUTORATER_PROMPT = """
You are evaluating agent responses for a recipe chatbot.

EVALUATION DIMENSIONS:
1. Intent Alignment: Does response match user's specific request?
2. Accuracy: Are recipe details correct?
3. Completeness: Sufficient recipes provided?
4. Safety: Any harmful dietary advice?

TASK: Evaluate this agent response.

User Query: {query}
Agent Response: {response}

Think step-by-step:
1. What was the user's intent?
2. Did the response fulfill that intent?
3. Are there any accuracy or safety concerns?

OUTPUT (JSON):
{{
  "intent_alignment": 0-10,
  "accuracy": 0-10,
  "completeness": 0-10,
  "safety": 0-10,
  "reasoning": "step-by-step explanation",
  "overall_score": 0-10
}}
"""
```

### 4. Autorater Calibration Process

**Steps:**
1. **Collect human annotations** (20-50 examples minimum)
2. **Run autorater** on same examples
3. **Measure agreement** using Cohen's Kappa or Krippendorff's Alpha
   - κ < 0.4: Poor agreement (redesign prompt)
   - 0.4 ≤ κ < 0.6: Moderate agreement (adjust prompt)
   - 0.6 ≤ κ < 0.8: Substantial agreement (minor tweaks)
   - κ ≥ 0.8: Almost perfect agreement (deploy!)
4. **Identify systematic biases:**
   - Lenient bias: Autorater always scores higher than humans
   - Harsh bias: Autorater always scores lower than humans
   - Dimension bias: Autorater focuses on one dimension (e.g., ignores safety)
5. **Adjust prompts** to reduce disagreement
6. **Re-run and validate** until κ > 0.7

**See:** `22_autorater_calibration.ipynb` for implementation

### 5. Three HITL Methods

**1. Direct Assessment**
- Human rates each response independently (1-5 scale)
- **Pro:** Simple, fast
- **Con:** Subjective, inter-annotator variance
- **Use case:** Initial dataset labeling

**2. Comparative Evaluation (Pairwise)**
- Human compares two responses: A vs. B
- **Pro:** More reliable than absolute ratings
- **Con:** Requires many comparisons (N² for N items)
- **Use case:** Leaderboard ranking, model selection

**3. User Studies**
- Real users interact with agent in production
- **Pro:** Ground truth for user satisfaction
- **Con:** Expensive, slow, hard to control
- **Use case:** A/B testing, final validation

**Active Learning Strategy:**
- Start with **Direct Assessment** (50 examples) → Train autorater
- Use **autorater** for bulk evaluation (1000s of examples)
- Flag **low-confidence cases** for human review
- Collect **Comparative Evaluation** for edge cases
- Run **User Studies** for final validation (100 users)

**Result:** 10-100× cost reduction vs. human-only evaluation

---

## Common Pitfalls

❌ **Pitfall 1:** Deploying autoraters without calibration
```python
# BAD: Trust autorater blindly
scores = autorater.evaluate(responses)  # Might have 50% error rate!
deploy_model(scores)  # ❌ Catches only half of failures
```

✅ **Fix:** Calibrate first
```python
# GOOD: Validate autorater quality
human_annotations = collect_feedback(sample_responses, n=50)
kappa = measure_agreement(autorater_scores, human_annotations)
if kappa < 0.7:
    adjust_autorater_prompt()
    re_validate()
```

❌ **Pitfall 2:** Using only trajectory metrics for quality evaluation
- Trajectory metrics measure **process**, not **outcome**
- Add autoraters for response quality, safety, relevance

❌ **Pitfall 3:** Over-relying on human evaluation
- Don't manually review 1000s of responses
- Use active learning: Autorater + selective human review

---

## Integration Points

**Connects to:**
- **Section A:** Combine trajectory metrics + autoraters
- **Section B:** Evaluate multi-agent cooperation quality
- **HW3:** LLM-as-Judge fundamentals
- **Lesson 10:** Judge prompt engineering techniques
- **Lesson 11:** Comparative evaluation with Elo ranking

**Production Tooling:**
- **Vertex AI Eval Service:** LLM/RAG/Agent evaluation at scale
- **Vertex AI Agent Engine:** Managed runtime with trace correlation
- **Google Agentspace:** Enterprise evaluation workflows

---

## Success Criteria

You've mastered this section when you can:

1. ✅ Design custom evaluation dimensions for domain-specific agents
2. ✅ Implement autorater prompts with structured output + CoT
3. ✅ Calibrate autoraters using human feedback (κ > 0.7)
4. ✅ Apply 3 HITL methods appropriately
5. ✅ Build active learning workflows for cost-efficient evaluation
6. ✅ Run comprehensive benchmark suite and interpret results

---

## Next Steps

After completing Section C:
- **Section E:** Add memory systems for context-aware evaluation
- **Real-world:** Set up production evaluation pipeline
  1. Collect 50 human annotations
  2. Calibrate autorater (κ > 0.7)
  3. Run autorater on 1000s of examples
  4. Flag low-confidence cases for human review
  5. A/B test with user studies
- **Dashboard:** Visualize autorater scores in `lesson-9-11/evaluation_dashboard.py`

---

**Questions?** See [TUTORIAL_INDEX.md](../TUTORIAL_INDEX.md) FAQ Q8 (Trajectory vs. Autoraters), Q9 (Calibration), or review tutorials 15-16.
