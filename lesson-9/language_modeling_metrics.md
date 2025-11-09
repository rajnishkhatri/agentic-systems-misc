# Language Modeling Metrics: Perplexity, Cross-Entropy, and Beyond

**Reading Time:** 15-20 minutes
**Difficulty:** Intermediate
**Prerequisites:** Basic probability theory, understanding of logarithms and entropy

---

## Table of Contents

1. [Introduction](#introduction)
2. [Entropy and Information Content](#entropy-and-information-content)
3. [Cross-Entropy and Model Learning](#cross-entropy-and-model-learning)
4. [Perplexity: Calculation and Interpretation](#perplexity-calculation-and-interpretation)
5. [Bits-Per-Character (BPC) and Bits-Per-Byte (BPB)](#bits-per-character-bpc-and-bits-per-byte-bpb)
6. [When Perplexity is Misleading](#when-perplexity-is-misleading)
7. [Worked Example: GPT-2 Perplexity](#worked-example-gpt-2-perplexity)
8. [Practical Guidelines](#practical-guidelines)

---

## Introduction

**Perplexity** is the most common intrinsic metric for evaluating language models. It measures how "surprised" a model is by a sequence of text—lower perplexity means the model predicts the text more confidently.

But what does perplexity actually measure? Why do we use it? And when does it mislead us?

This tutorial builds intuition for:
- **Entropy:** Information content of language
- **Cross-entropy:** How well a model approximates true language distribution
- **Perplexity:** An interpretable transformation of cross-entropy
- **BPC/BPB:** Character-level equivalents
- **Pitfalls:** When perplexity doesn't correlate with model quality

By the end, you'll be able to calculate, interpret, and critically evaluate perplexity scores.

---

## Entropy and Information Content

### What is Entropy?

**Entropy** measures the average "surprise" or uncertainty in a probability distribution. High entropy = high uncertainty.

**Formula (Shannon Entropy):**

```
H(P) = -Σ P(x) log₂ P(x)
```

Where:
- `P(x)` = Probability of event `x`
- `log₂` = Logarithm base 2 (measures bits of information)

---

### Intuition: 2-Token Language vs 4-Token Language

**Example 1: 2-Token Language**

Imagine a language with only 2 words: "yes" and "no", each equally likely.

```
P("yes") = 0.5
P("no") = 0.5
```

**Entropy:**

```
H(P) = -[0.5 × log₂(0.5) + 0.5 × log₂(0.5)]
     = -[0.5 × (-1) + 0.5 × (-1)]
     = 1.0 bits
```

**Interpretation:** You need **1 bit** to encode each word (0 = "yes", 1 = "no").

---

**Example 2: 4-Token Language**

Now a language with 4 words: "yes", "no", "maybe", "unknown", equally likely.

```
P("yes") = 0.25
P("no") = 0.25
P("maybe") = 0.25
P("unknown") = 0.25
```

**Entropy:**

```
H(P) = -[4 × 0.25 × log₂(0.25)]
     = -[4 × 0.25 × (-2)]
     = 2.0 bits
```

**Interpretation:** You need **2 bits** to encode each word (00, 01, 10, 11).

---

### Key Insight

**Higher entropy = More uncertainty = More information per token**

For natural language:
- English has ~12-14 bits of entropy per word (estimated)
- This means you can't predict the next word perfectly—there's genuine uncertainty

**Relevance to LLMs:**
- A perfect language model would have entropy equal to true English (irreducible uncertainty)
- A bad model has higher entropy (more uncertainty than necessary)
- **Perplexity measures how close a model gets to optimal entropy**

---

## Cross-Entropy and Model Learning

### What is Cross-Entropy?

**Cross-entropy** measures the average number of bits needed to encode data from distribution `P` (true data) using distribution `Q` (model predictions).

**Formula:**

```
H(P, Q) = -Σ P(x) log₂ Q(x)
```

Where:
- `P(x)` = True probability of token `x` in real language
- `Q(x)` = Model's predicted probability of token `x`

---

### Intuition: Model Learning

Imagine teaching a language model to predict the next word in "The cat sat on the ___".

**True distribution (P):**
```
P("mat") = 0.6
P("floor") = 0.3
P("roof") = 0.1
```

**Untrained model (Q₁):**
```
Q₁("mat") = 0.33
Q₁("floor") = 0.33
Q₁("roof") = 0.34
```

**Cross-entropy (untrained):**

```
H(P, Q₁) = -[0.6 × log₂(0.33) + 0.3 × log₂(0.33) + 0.1 × log₂(0.34)]
         ≈ 1.58 bits
```

---

**Trained model (Q₂):**
```
Q₂("mat") = 0.7
Q₂("floor") = 0.25
Q₂("roof") = 0.05
```

**Cross-entropy (trained):**

```
H(P, Q₂) = -[0.6 × log₂(0.7) + 0.3 × log₂(0.25) + 0.1 × log₂(0.05)]
         ≈ 1.13 bits
```

**Improvement:** Cross-entropy decreased from 1.58 to 1.13 bits. The model learned to predict "mat" more confidently.

---

### KL Divergence: The Gap Between P and Q

**KL Divergence** measures how much extra bits are needed when using model Q instead of the optimal P:

```
KL(P || Q) = H(P, Q) - H(P)
```

Where:
- `H(P, Q)` = Cross-entropy (bits needed with model)
- `H(P)` = Entropy (optimal bits needed)

**Key Property:** KL divergence ≥ 0. It equals 0 only when Q perfectly matches P.

**Training Objective:**
- Minimize cross-entropy H(P, Q)
- Equivalently, minimize KL divergence KL(P || Q)
- Goal: Make model Q as close to true distribution P as possible

---

## Perplexity: Calculation and Interpretation

### Definition

**Perplexity** is the exponentiation of cross-entropy:

```
Perplexity = 2^(H(P, Q))
```

Or equivalently:

```
Perplexity = 2^(-1/N × Σ log₂ P(token_i | context))
```

Where:
- `N` = Number of tokens in the test sequence
- `P(token_i | context)` = Model's predicted probability of token `i` given previous tokens

---

### Why Perplexity?

**Problem:** Cross-entropy values are in "bits"—hard to interpret.
- Is 3.5 bits good or bad?
- How much better is 3.0 bits than 3.5 bits?

**Solution:** Perplexity converts to an intuitive scale:

> **Perplexity = The number of choices the model is uncertain between at each step**

---

### Interpretation Examples

**Perplexity = 2:**
- Model is as uncertain as flipping a coin (2 choices)
- Very low uncertainty

**Perplexity = 10:**
- Model is as uncertain as choosing uniformly from 10 options
- Moderate uncertainty

**Perplexity = 100:**
- Model is as uncertain as choosing uniformly from 100 options
- High uncertainty

**Perplexity = 50,000:**
- Model is guessing randomly from full vocabulary (typical vocab size)
- No learning

---

### Typical Perplexity Values

| Model | Dataset | Perplexity |
|-------|---------|------------|
| Random guessing | WikiText-2 | ~50,000 (vocab size) |
| Bigram model | WikiText-2 | ~500 |
| LSTM (2016) | WikiText-2 | ~100 |
| GPT-2 Small (117M) | WikiText-2 | ~29.4 |
| GPT-2 Medium (345M) | WikiText-2 | ~26.4 |
| GPT-2 Large (762M) | WikiText-2 | ~22.8 |
| GPT-2 XL (1.5B) | WikiText-2 | ~20.3 |
| GPT-3 (175B) | WikiText-2 | ~20.5 (estimated) |

**Observations:**
1. Perplexity decreases as models scale (better prediction)
2. Diminishing returns: GPT-2 Large → XL is smaller improvement than Small → Medium
3. GPT-3 doesn't improve much over GPT-2 XL on WikiText-2 (benchmark saturation)

---

### Conversion: Cross-Entropy ↔ Perplexity

**From Cross-Entropy to Perplexity:**

```
Perplexity = 2^(Cross-Entropy)
```

Example: If cross-entropy = 4.5 bits, then perplexity = 2^4.5 ≈ 22.6

**From Perplexity to Cross-Entropy:**

```
Cross-Entropy = log₂(Perplexity)
```

Example: If perplexity = 30, then cross-entropy = log₂(30) ≈ 4.9 bits

---

## Bits-Per-Character (BPC) and Bits-Per-Byte (BPB)

### Why BPC and BPB?

**Problem:** Perplexity depends on tokenization.
- GPT-2 uses Byte-Pair Encoding (BPE) with ~50k tokens
- LLaMA uses SentencePiece with ~32k tokens
- Comparing their perplexities is like comparing apples and oranges

**Solution:** Normalize to character or byte level for fair comparison.

---

### Bits-Per-Character (BPC)

**Definition:** Average cross-entropy per character:

```
BPC = Cross-Entropy (bits) × (Avg tokens per sequence) / (Avg characters per sequence)
```

**Interpretation:** How many bits needed to encode each character?

**Typical Values:**
- Random guessing: ~4.7 bits/char (26 letters + space + punctuation)
- LSTM (2016): ~1.3 BPC on enwik8
- GPT-2: ~0.93 BPC on enwik8
- GPT-3: ~0.76 BPC on enwik8 (estimated)

---

### Bits-Per-Byte (BPB)

**Definition:** Average cross-entropy per byte (UTF-8 encoded):

```
BPB = Cross-Entropy (bits) × (Avg tokens per sequence) / (Avg bytes per sequence)
```

**Use Case:** Multilingual models where character count varies by language.

**Conversion:**
- English: ~1 byte per character (ASCII)
- Chinese: ~3 bytes per character (UTF-8)
- Emoji: 4 bytes

**Why it Matters:** BPB is **tokenization-agnostic**—the ultimate fair comparison.

---

### Example: Comparing GPT-2 and LLaMA

**GPT-2 on WikiText-2:**
- Perplexity: 29.4
- Tokenizer: BPE (50k vocab, ~0.75 tokens/word)
- BPC: ~1.1

**LLaMA on WikiText-2:**
- Perplexity: 35.2 (higher!)
- Tokenizer: SentencePiece (32k vocab, ~1.0 tokens/word)
- BPC: ~1.0 (lower!)

**Conclusion:** LLaMA has higher perplexity but lower BPC. LLaMA is actually better when accounting for tokenization differences.

**Lesson:** Always compare BPC/BPB, not raw perplexity, across models with different tokenizers.

---

## When Perplexity is Misleading

Perplexity is a useful intrinsic metric, but it doesn't always correlate with **task performance** or **user satisfaction**. Here are cases where perplexity misleads:

### 1. Post-Training Collapse (RLHF)

**Observation:** Models trained with RLHF (Reinforcement Learning from Human Feedback) often have **higher perplexity** than base models.

**Example:**
- GPT-3 base: Perplexity ~20 on WikiText-2
- GPT-3 InstructGPT (RLHF): Perplexity ~28 on WikiText-2

**Why?**
- RLHF optimizes for human preferences (helpfulness, safety), not likelihood
- The model learns to refuse unsafe prompts ("I can't help with that")
- Refusals have low probability under the base distribution → higher perplexity

**Lesson:** **Higher perplexity ≠ worse model** after RLHF. Use task-specific metrics instead.

---

### 2. Quantization Effects

**Observation:** Quantizing a model (FP32 → INT8) often **increases perplexity** even if task performance is unchanged.

**Example:**
- Llama-2-7B (FP16): Perplexity 12.3 on C4
- Llama-2-7B (INT8): Perplexity 13.1 on C4
- Task accuracy: 83.2% (both)

**Why?**
- Quantization introduces rounding errors in probability estimates
- Perplexity is sensitive to small probability changes
- Task performance depends on argmax (top-1 prediction), not exact probabilities

**Lesson:** Validate task performance separately from perplexity when quantizing.

---

### 3. Data Contamination

**Observation:** Suspiciously low perplexity on a benchmark suggests **test set leakage** into training data.

**Detection Method:**
1. Calculate perplexity on benchmark (e.g., MMLU)
2. Calculate perplexity on held-out set (e.g., private test set)
3. Compare: If benchmark perplexity is much lower, suspect contamination

**Example:**
- GPT-2 on WikiText-2: Perplexity 29.4 (expected)
- GPT-2 on MMLU questions: Perplexity 8.2 (suspicious!)
- **Interpretation:** MMLU questions may have leaked into GPT-2 training data

**Threshold:** Perplexity < 10 on multiple-choice questions is a red flag.

---

### 4. Domain Mismatch

**Observation:** Perplexity varies dramatically across domains.

**Example (GPT-2 Medium):**

| Dataset | Perplexity |
|---------|------------|
| WikiText-2 (Wikipedia) | 26.4 |
| Penn Treebank (news) | 47.3 |
| Code (Python) | 68.2 |
| Medical records | 120.5 |

**Why?**
- Models trained on web text (Wikipedia, Reddit, books) have low perplexity on similar domains
- Out-of-distribution domains (medical, legal, code) have high perplexity
- **Perplexity measures distribution match, not general intelligence**

**Lesson:** Always report the **test set** when citing perplexity. "GPT-2 has perplexity 26" is incomplete without "on WikiText-2."

---

### 5. Long-Context Degradation

**Observation:** Perplexity increases as context length grows, even within the model's context window.

**Example (GPT-3, 2048-token context window):**

| Context Length | Perplexity |
|----------------|------------|
| 0-512 tokens | 18.2 |
| 512-1024 tokens | 22.1 |
| 1024-1536 tokens | 27.4 |
| 1536-2048 tokens | 34.8 |

**Why?**
- Attention patterns degrade at longer distances ("lost in the middle")
- Training data has more short documents than long documents
- Positional embeddings may not generalize to max context length

**Lesson:** Test perplexity at the **context lengths you'll use in production**, not just on short sequences.

---

## Worked Example: GPT-2 Perplexity

Let's calculate perplexity for GPT-2 Small on a short sequence.

### Test Sequence

```
"The cat sat on the mat."
```

**Tokens (GPT-2 BPE):** `["The", " cat", " sat", " on", " the", " mat", "."]` (7 tokens)

---

### Step 1: Get Token Probabilities

We query GPT-2 to predict each token given previous context:

| Token | Context | P(token | context) | log₂(P) |
|-------|---------|----------------------|---------|
| "The" | (start) | 0.08 | -3.64 |
| " cat" | "The" | 0.12 | -3.06 |
| " sat" | "The cat" | 0.18 | -2.47 |
| " on" | "The cat sat" | 0.35 | -1.51 |
| " the" | "The cat sat on" | 0.65 | -0.62 |
| " mat" | "The cat sat on the" | 0.42 | -1.25 |
| "." | "The cat sat on the mat" | 0.91 | -0.14 |

---

### Step 2: Calculate Cross-Entropy

```
Cross-Entropy = -1/N × Σ log₂ P(token_i | context)
              = -1/7 × [(-3.64) + (-3.06) + (-2.47) + (-1.51) + (-0.62) + (-1.25) + (-0.14)]
              = -1/7 × (-12.69)
              = 1.81 bits
```

---

### Step 3: Calculate Perplexity

```
Perplexity = 2^(Cross-Entropy)
           = 2^(1.81)
           = 3.52
```

---

### Interpretation

**Perplexity = 3.52** means GPT-2 is, on average, as uncertain as choosing uniformly from ~3.5 options at each token.

**Why so low?** This is a common phrase. For rare sequences, perplexity would be higher.

**Compare to Random:**
- Random model: Perplexity ≈ 50,000 (vocab size)
- GPT-2: Perplexity = 3.52
- GPT-2 is **14,200× more certain** than random guessing!

---

## Practical Guidelines

### When to Use Perplexity

✅ **Use perplexity for:**
1. **Comparing base models** (GPT-2 vs GPT-3 vs LLaMA)
2. **Tracking training progress** (perplexity should decrease)
3. **Hyperparameter tuning** (learning rate, batch size)
4. **Detecting data contamination** (suspicious low perplexity)
5. **Domain adaptation** (how well does model fit new domain?)

---

### When NOT to Use Perplexity

❌ **Don't use perplexity for:**
1. **Instruction-following models** (RLHF distorts perplexity)
2. **Task-specific evaluation** (classification, QA, summarization)
3. **Comparing across tokenizers** (use BPC/BPB instead)
4. **User satisfaction** (perplexity ≠ helpfulness)
5. **Safety evaluation** (perplexity doesn't detect harm)

---

### Best Practices

1. **Always report the test set:** "Perplexity 26.4 on WikiText-2"
2. **Use BPC/BPB for cross-model comparison:** Tokenization-agnostic
3. **Validate at production context lengths:** Don't just test on short sequences
4. **Check for contamination:** Compare benchmark perplexity to held-out perplexity
5. **Combine with task metrics:** Perplexity + accuracy + human eval

---

### Quick Reference Table

| Metric | Formula | Interpretation | Use Case |
|--------|---------|----------------|----------|
| **Entropy** | `-Σ P(x) log₂ P(x)` | Uncertainty in true distribution | Theoretical lower bound |
| **Cross-Entropy** | `-Σ P(x) log₂ Q(x)` | Bits needed with model Q | Training loss |
| **Perplexity** | `2^(Cross-Entropy)` | Effective vocabulary size | Intuitive quality metric |
| **BPC** | CE × tokens / characters | Bits per character | Fair comparison |
| **BPB** | CE × tokens / bytes | Bits per byte | Multilingual comparison |

---

## Summary

**Key Takeaways:**

1. **Entropy** measures uncertainty in language (irreducible)
2. **Cross-entropy** measures how well a model Q approximates true distribution P
3. **Perplexity** = 2^(cross-entropy) = effective vocabulary size at each step
4. **BPC/BPB** normalize for tokenization differences
5. **Perplexity is useful for base models** but misleading after RLHF, quantization, or on contaminated data

**Typical Values:**
- Great: Perplexity < 20 on WikiText-2
- Good: Perplexity 20-30
- Mediocre: Perplexity 30-50
- Bad: Perplexity > 100

**Next Steps:**
- **Run the notebook:** `perplexity_calculation_tutorial.ipynb` to calculate perplexity hands-on
- **Learn exact methods:** Read `exact_evaluation_methods.md` for BLEU, semantic similarity
- **Apply to your model:** Calculate perplexity on your recipe bot's responses

---

## References

1. **Shannon (1948):** "A Mathematical Theory of Communication" (introduced entropy)
2. **Brown et al. (2020):** "Language Models are Few-Shot Learners" (GPT-3 perplexity results)
3. **Merity et al. (2016):** "Pointer Sentinel Mixture Models" (WikiText-2 benchmark)
4. **Radford et al. (2019):** "Language Models are Unsupervised Multitask Learners" (GPT-2 perplexity results)

---

**Author:** AI Evaluation Course Team
**Last Updated:** 2025-11-09
**Estimated Reading Time:** 18 minutes
