# SKILL: Content Style Control Patterns for GenAI Systems

> A comprehensive knowledge map for AI agentic assistants to control, constrain, and optimize the style of LLM-generated content.

---

## OVERVIEW

This skill covers five production-grade patterns for controlling LLM output style:

| Pattern | Control Mechanism | Enforcement Level | Use When |
|---------|-------------------|-------------------|----------|
| Logits Masking | Dynamic logic at sampling | Strict (client-side) | Rules require programmatic evaluation |
| Grammar | Structured rules/schema | Strict (server-side) | Output must conform to data format |
| Style Transfer | Example-based learning | Implicit | Style is nuanced, hard to express as rules |
| Reverse Neutralization | Intermediate neutral form | Implicit | No input-output pairs exist for desired style |
| Content Optimization | Preference tuning (DPO) | Optimized | Best style factors are unknown |

---

## PATTERN 1: LOGITS MASKING

### General Principle

Intercept LLM generation at the sampling stage to zero out probabilities of token continuations that violate specified rules. This provides strict enforcement by pruning non-conforming beams in beam search.

### Core Implementation

```python
class MyRulesLogitsProcessor(LogitsProcessor):
    def __init__(self, tokenizer, rules):
        self.tokenizer = tokenizer
        self.rules = rules
    
    def __call__(self, input_ids: torch.LongTensor, 
                 input_logits: torch.FloatTensor) -> torch.FloatTensor:
        output_logits = input_logits.clone()
        for idx, input_id in enumerate(input_ids):
            seq = self.tokenizer.decode(input_id)
            if not self.apply_rules(seq, self.rules):
                output_logits[idx] = -np.inf  # Zero out probability
        return output_logits
```

### When to Use

- **Branding**: Enforce brand-specific vocabulary (e.g., "sporty" for Item A, not "luxurious")
- **Accuracy**: Prevent repetition of invoice IDs or amounts in generated letters
- **Compliance**: Exclude competitor mentions when referencing customer case studies
- **Stylebook**: Enforce Chicago Manual of Style or APA citation format

### Sequence Selection vs. Regeneration

| Approach | Use When | Complexity |
|----------|----------|------------|
| Sequence Selection | Censoring leaves valid options | Simple |
| Sequence Regeneration | High probability all options get censored | Requires backtracking logic |

### Inspired Insight

> The "try-and-try-again" approach (generate → test → retry) is an **antipattern** that only works when <10% of responses need regeneration. Otherwise, multiple retries dramatically increase latency and may never converge.

### Caveats

1. **Model Access**: Requires access to logprobs (Claude doesn't provide; OpenAI, Google, Meta do)
2. **Latency**: Each sequence requires client-model communication; best for locally hosted models
3. **Dead Ends**: If no continuation meets rules, must backtrack or refuse

### Source Reference
> "The impact of Logits Masking is to prune nonconforming beams in beam search; this ensures that generated text conforms to specific rules." (Chapter 2, Pattern 1)

---

## PATTERN 2: GRAMMAR

### General Principle

Specify constraints as a formal grammar (BNF) or schema that the model framework applies server-side to constrain token generation. This is essentially Logits Masking performed by the model provider.

### Three Implementation Options

#### Option 1: BNF Grammar (Most Flexible)
```python
grammar_str = """
record ::= author separator title separator year
author ::= [a-zA-Z ]* | unk
title ::= [a-zA-Z ]* | unk  
year ::= [1-2][0-9][0-9][0-9] | unk
unk ::= "NULL"
separator ::= "|"
"""

grammar = IncrementalGrammarConstraint(grammar_str, "record", tokenizer)
grammar_processor = GrammarConstrainedLogitsProcessor(grammar)
```

#### Option 2: JSON Mode (Simplest)
```python
response = client.chat.completions.create(
    model=MODEL_ID,
    messages=input_message,
    response_format={"type": "json_object"}
)
```

#### Option 3: Structured Output with Dataclass (Best Balance)
```python
from dataclasses import dataclass
from enum import Enum

class CurrencyEnum(str, Enum):
    USD = 'USD'
    EUR = 'EUR'

@dataclass
class Invoice:
    purpose: str
    amount: float
    currency: CurrencyEnum = CurrencyEnum.USD
```

### Decision Matrix: BNF vs. Pydantic

| Factor | BNF | Pydantic/Dataclass |
|--------|-----|-------------------|
| Ease of use | Lower | Higher |
| Latency | Client-side (higher) | Server-side (lower) |
| Model support | Requires logprobs | Universal |
| Validation logic | Fully expressible | Limited to Enum |
| Dynamic rules | Yes | No |

### Inspired Insight

> **Don't Beg for Compliance**: Instead of prompting "Please do not add any extra formatting... Just answer 'YES' or 'NO'", use Grammar:
> ```python
> agent = Agent(model, result_type=Literal["YES", "NO"])
> ```

### Failure Modes

1. **Endless whitespace**: When no valid tokens exist, whitespace (often allowed) loops infinitely
2. **Increased refusals**: Complex nested structures increase dead-end probability
3. **Inaccurate results**: Over-restrictive grammar forces incorrect outputs

### Escape Hatch Pattern
```python
# Allow model to signal uncertainty
currency_rate: float | Literal["Unknown"]
```

### Source Reference
> "Grammar is a way of specifying a set of constraints in the form of a metasyntax to ensure that a model response conforms to that metasyntax." (Chapter 2, Pattern 2)

---

## PATTERN 3: STYLE TRANSFER

### General Principle

Use example input-output pairs to teach an LLM to convert content from a readily available form into a desired style. Works when style is nuanced and hard to express as rules.

### Two Approaches

#### Few-Shot Learning (1-10 examples)
```python
def generate_text(input_text: str) -> str:
    in_context_examples = [
        {"input_text": "The movie was fantastic!",
         "output_text": "The cinematography was exceptional..."},
        # ... more examples
    ]
    
    prompt = "Convert the following text into the following style:\n\n"
    for example in in_context_examples:
        prompt += f"Input: {example['input_text']}\nOutput: {example['output_text']}\n\n"
    prompt += f"Input: {input_text}\nOutput:"
```

#### Fine-Tuning (100-1000+ examples)
- Higher fidelity for complex vocabulary mappings
- Faster, cheaper inference (shorter prompts)
- Requires data curation, training expertise, LLMOps

### Use Cases

| Scenario | Source | Target |
|----------|--------|--------|
| Academic → Blog | Research papers | Engaging blog posts |
| Generic → Brand | Standard documentation | Warm, friendly tone |
| Platform Adaptation | LinkedIn post | Twitter/X thread |
| Expertise Calibration | Technical docs | Beginner/Expert versions |
| Notes → Email | Executive shorthand | Formal memo |

### Image Style Transfer Example

```python
from diffusers import StableDiffusionControlNetImg2ImgPipeline

# Use depth map as control image to preserve spatial relationships
depth_estimator = pipeline("depth-estimation")
depth_image = depth_estimator(image)["depth"]

output = pipe(
    prompt="Star Wars' Darth Vader with a red light saber",
    image=wanderer_image,
    control_image=wanderer_depth_map,
).images[0]
```

### Considerations

| Factor | Impact |
|--------|--------|
| Model size | Bigger models generalize better from examples |
| Context limits | Too many examples → confusion, contradictions |
| Inference speed | More examples → longer latency |

### Inspired Insight

> Zero-shot learning often fails for style tasks. The model knows *what* a marketing email looks like generically, but not *your* marketing style with *your* vocabulary and tone.

### Source Reference
> "The Style Transfer pattern allows you to teach a GenAI model to convert content in a readily available form into content in some desired style." (Chapter 2, Pattern 3)

---

## PATTERN 4: REVERSE NEUTRALIZATION

### General Principle

When you have examples of styled content but no input-output pairs, create them by:
1. Neutralizing your styled content → generates the "input"
2. Reversing the pairs → styled becomes "output"
3. Fine-tuning on reversed pairs
4. At inference: LLM generates neutral → fine-tuned model converts to style

### The Jujitsu Move

```
Training Phase:
  Styled Content → [Neutralization LLM] → Neutral Content
  Flip: Neutral (input) + Styled (output) = Training Pair
  
Inference Phase:
  User Prompt → [Foundation LLM] → Neutral Content → [Fine-tuned LLM] → Styled Output
```

### Implementation Flow

```python
# Step 1: Neutralize styled content
messages = [
    {'role': 'system', 
     'content': "Convert the given text into text understandable by a freshman college student."},
    {'role': 'user', 
     'content': f"Neutralize the tone from: {styled_legal_text}"}
]

# Step 2: Flip for training dataset
training_example = {
    "messages": [
        {"role": "system", "content": "Convert neutralized email into personalized email."},
        {"role": "user", "content": neutral_version},
        {"role": "assistant", "content": original_styled_version}
    ]
}

# Step 3: Fine-tune
# Step 4: Inference uses two LLM calls
```

### Use Cases

- **Legal Text**: Generate jurisdiction-specific legalese on new topics
- **Personal Style**: Generate emails in your voice on any subject
- **Brand Voice**: Apply brand personality to any content

### Choosing the Neutral Form

| Requirement | Why It Matters |
|-------------|----------------|
| Repeatable | Different LLMs should produce similar neutral forms |
| Content-preserving | Semantic meaning must survive neutralization |
| Generatable | Foundation model must be able to produce it |

### Validation Technique

```python
# Use embedding similarity to verify content preservation
from sentence_transformers import SentenceTransformer

model = SentenceTransformer('all-MiniLM-L6-v2')
original_emb = model.encode(original_text)
neutral_emb = model.encode(neutral_text)
similarity = cosine_similarity(original_emb, neutral_emb)
# Should be high (>0.8) if content preserved
```

### Inspired Insight

> The neutralization prompt matters enormously. "Communication between executives" and "reading level of a freshman" are subjective—verify that your LLM's "neutral" matches your application's definition.

### Source Reference
> "Reverse Neutralization allows you to generate content in some desired style... by using an intermediate neutral form that the GenAI model can readily generate." (Chapter 2, Pattern 4)

---

## PATTERN 5: CONTENT OPTIMIZATION

### General Principle

When you don't know which style factors matter, use preference tuning to optimize toward whatever performs best according to an evaluator. This "teaches to the test" in a positive way—the test must reflect reality.

### The Four Steps

```
Step 1: Generate pairs of content from same/similar prompts
Step 2: Compare pairs using evaluator → pick winner
Step 3: Create preference dataset {prompt, chosen, rejected}
Step 4: DPO training → deploy tuned model
```

### Step 1: Generating Pairs

| Method | Implementation | Variation Level |
|--------|---------------|-----------------|
| Repeated generation | Same prompt, temperature > 0 | Low |
| Change settings | Random temperature/top-p | Medium |
| Prompt rewriting | LLM rephrase or add follow-on question | High |

### Step 2: Evaluation Methods

| Method | Use When | Example |
|--------|----------|---------|
| Human labeling | User-facing, subjective quality | Panel selects preferred content |
| Automated evaluator | Measurable criteria exist | SQL execution time, code correctness |
| Outcome measurement | Real-world usage available | Click-through rate, conversion |
| LLM-as-Judge | Complex rubrics needed | Marketing 4Ps/3Cs framework |

### LLM-as-Judge Example

```python
@dataclass
class AdsComparison:
    ad_a_is_better_than_ad_b: bool
    reasoning: str

prompt = """
Compare the two ads for the same item. Criteria:
* Is it clear what's being sold? Age, brand, price, condition?
* Does it target the relevant audience?
* Is it concise (1-3 sentences max)?
* Does it include contact information?
* Is it truthful (item is used, not from manufacturer)?

ad_a: {ad_a}
ad_b: {ad_b}
"""
```

### Step 4: DPO Training

```python
from trl import DPOTrainer, DPOConfig

training_args = DPOConfig(output_dir="ContentOptimized-DPO")
trainer = DPOTrainer(
    model=model, 
    args=training_args,
    processing_class=tokenizer, 
    train_dataset=train_dataset
)
trainer.train()
trainer.save_model(training_args.output_dir)
```

### The In-Distribution Requirement

> Content generated for training must be producible by the model being trained. Solutions:
> - **Easy**: Use same LLM for generation and training
> - **Hard**: Generate with bigger LLM, then instruction-tune smaller model first

### Continuous Improvement Cycle

```
[Prompt Library] → Generate Pairs → Evaluate → DPO Train → [Tuned Model]
                         ↑                                      ↓
                         └──────── Use tuned model ────────────┘
```

Iterate until saturation. DeepSeek-R1 demonstrated this with easily verifiable problems.

### Inspired Insight

> **Evaluation is the most important step.** A bad evaluator creates a model that games metrics. If you optimize for engagement time, the LLM might produce deliberately confusing content. Always interpret metrics against true objectives.

### Source Reference
> "Content Optimization is a pattern that uses preference tuning to produce optimally performing content... Unlike optimization methods, in which optimization attempts to approximate an independent source of truth, this pattern attempts to hack the model to create content the evaluation method will consider great." (Chapter 2, Pattern 5)

---

## PATTERN SELECTION DECISION TREE

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

---

## CROSS-PATTERN CONNECTIONS

### Evaluation Framework Integration

These patterns connect to your LLM evaluation expertise:

| Pattern | Evaluation Hook |
|---------|-----------------|
| Logits Masking | Rule compliance rate, backtrack frequency |
| Grammar | Schema validation pass rate, constraint satisfaction |
| Style Transfer | Semantic similarity (original vs. styled), human preference |
| Reverse Neutralization | Content preservation score, style classifier accuracy |
| Content Optimization | Preference win rate, outcome metrics, judge calibration |

### Multi-Agent Orchestration

In multi-agent systems (like your LangGraph dispute resolution):

- **Grammar**: Enforce structured outputs between agents
- **Content Optimization**: Tune specialist agents for their specific tasks
- **Logits Masking**: Compliance agent enforcing regulatory vocabulary

### RAG System Integration

- **Grammar**: Ensure citations follow exact format
- **Style Transfer**: Adapt retrieved content to user expertise level
- **Content Optimization**: Optimize for Recall@k by tuning generation style

---

## IMPLEMENTATION CHECKLIST

### Pre-Implementation
- [ ] Define "good style" criteria (rules? examples? outcomes?)
- [ ] Assess model access (logprobs available?)
- [ ] Estimate volume (fine-tuning justified?)
- [ ] Identify evaluation method

### Pattern-Specific
- [ ] **Logits Masking**: Implement backtracking for complex rules
- [ ] **Grammar**: Test edge cases where no valid tokens exist
- [ ] **Style Transfer**: Verify example quality and diversity
- [ ] **Reverse Neutralization**: Validate content preservation in neutral form
- [ ] **Content Optimization**: Establish feedback loop for continuous improvement

### Production Readiness
- [ ] Latency benchmarks meet requirements
- [ ] Failure modes handled gracefully
- [ ] Monitoring for style drift
- [ ] A/B testing framework for ongoing optimization

---

## REFERENCES

| Concept | Citation |
|---------|----------|
| Invalid action masking | Vinyals et al. (2019), StarCraft II |
| Theoretical justification | Huang and Ontañόn (2020) |
| Grammar prompting | Wang et al. (2024) |
| Constrained decoding | Netz, Reimar, and Rumpe (2024) |
| Style transfer in images | Gatys, Ecker, and Bethge (2015) |
| Style transfer in text | Reif et al. (2021) |
| RLHF | Christiano et al. (2017), Ouyang et al. (2022) |
| DPO | Raifalov et al. (2023) |
| Back translation | Beddiar, Jahan, and Oussalah (2021) |

---

*Source: "Controlling Content Style" (Chapter 2), GenAI Patterns Book, retrieved February 2025*
