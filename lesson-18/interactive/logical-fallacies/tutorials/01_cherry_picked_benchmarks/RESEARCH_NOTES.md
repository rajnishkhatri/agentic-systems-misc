# Research Notes: Cherry-Picked Benchmarks

**Generated:** 2025-12-23
**Focus:** Selection bias in AI evaluation and reporting.

## 1. Academic Sources (arXiv)

### Source 1.1: "Show Your Work"
- **Title:** Show Your Work: Improved Reporting of Experimental Results
- **Authors:** Dodge, J., Gururangan, S., Card, D., Schwartz, R., & Smith, N. A.
- **Date:** 2019
- **Citation:** arXiv:1909.03004 [cs.CL]
- **Relevance Score:** 5/5
- **Key Insight:** Reporting only the best result from a hyperparameter search (cherry-picking) without reporting the expected validation performance or computational budget creates a false impression of state-of-the-art performance.
- **Application to Tutorial:** Use this to explain *why* single-metric reporting is a red flag. It's not just "lucky", it's statistically manipulative.

### Source 1.2: "Deception in LLM Benchmarks" (General Concept)
- **Concept:** Benchmark Contamination / Leakage
- **Insight:** When test data appears in training data (common in large web scrapes), the model "memorizes" rather than "generalizes".
- **Relevance:** This is a form of unintentional cherry-picking where the "cherry" (good performance) is selected by the training process itself.

## 2. Industry Cases

### Source 2.1: Google Gemini "Hands-on" Demo (Dec 2023)
- **Event:** Google released a video showing Gemini interacting seamlessly with a user in real-time video.
- **The Reality:** The video was edited to speed up latency, and the model was actually prompted with still image frames and text, not live video.
- **Relevance Score:** 5/5
- **Fallacy Type:** Demo-to-Production Leap.
- **Key Insight:** "We created the demo to showcase the potential" is the standard defense for cherry-picking.
- **Application:** Use as the primary "Real World Example" in the UNDERSTAND phase.

## 3. GitHub / Open Source

### Source 3.1: "Open LLM Leaderboard" Discussions
- **Context:** Hugging Face Open LLM Leaderboard.
- **Issue:** Users submitting models finetuned specifically on the test set questions to game the leaderboard.
- **Relevance:** 4/5
- **Insight:** "Goodhart's Law": When a measure becomes a target, it ceases to be a good measure.
- **Application:** Connects to the "Metric Hacking" concept in the REFLECT phase.

## 4. Synthesis for Tutorial

| Phase | Concept | Source |
|-------|---------|--------|
| **1. Understand** | The Definition | Dodge et al. (2019) - "Reporting bias" |
| **1. Understand** | Real Example | Google Gemini Demo (2023) |
| **2. Plan** | Detection Strategy | Check for "Test Set Contamination" (General ML concept) |
| **5. Reflect** | Pattern Connection | Goodhart's Law (Leaderboard gaming) |

## 5. Vocabulary Bank
- **SOTA:** State-of-the-art (often claimed via cherry-picking).
- **Seed Hacking:** Running a model with 100 random seeds and reporting only the lucky one.
- **OOD:** Out-of-Distribution (where cherry-picked models fail).

