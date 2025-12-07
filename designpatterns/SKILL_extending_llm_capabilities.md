# SKILL.md: Extending LLM Capabilities

## Overview

This skill provides patterns for extending foundational model capabilities beyond their pretraining. Use these patterns when a model fails at tasks due to training data gaps, requires multi-step reasoning, or needs domain-specific customization.

---

## Pattern Selection Decision Tree

```
Task fails with standard prompting?
├── Model gives "lazy" or incomplete responses
│   └── Use: Zero-shot CoT (add "think step-by-step")
├── Model applies wrong logic or hallucinates reasoning
│   └── Use: Few-shot CoT (provide example reasoning chains)
├── Task requires exploring multiple solution paths
│   └── Use: Tree of Thoughts (ToT)
├── Need consistent style/format adaptation (100-1000 examples available)
│   └── Use: Adapter Tuning (LoRA/QLoRA)
├── Need to teach entirely new complex task (1000+ examples needed)
│   └── Use: Evol-Instruct + Instruction Tuning
└── Model lacks factual knowledge
    └── Do NOT use these patterns. Use RAG instead.
```

---

## Pattern 1: Chain of Thought (CoT)

### When to Apply
- Mathematical calculations requiring intermediate steps
- Logical deductions with multiple conditions
- Sequential reasoning tasks
- Model jumps directly to wrong answers without showing work

### Implementation

#### Variant A: Zero-shot CoT
Append trigger phrase to prompt. No examples needed.

```python
prompt = f"{user_query}\n\nThink step-by-step."
# Alternative triggers: "Let's work through this systematically."
#                       "Break this down into steps."
```

**Effectiveness**: Works best on frontier models. Less effective on small/local models.

#### Variant B: Few-shot CoT
Provide 1-3 demonstration examples showing reasoning chains before the actual query.

```python
prompt = f"""
Example 1:
Q: {example_question_1}
A: 
Step 1: {reasoning_step_1}
Step 2: {reasoning_step_2}
Step 3: {reasoning_step_3}
Answer: {final_answer_1}

Example 2:
Q: {example_question_2}
A:
Step 1: {reasoning_step_1}
...

Q: {actual_query}
"""
```

**Key implementation notes**:
- Examples must demonstrate the exact reasoning pattern you want
- Model will mimic the step structure (number of steps, format)
- More effective than Zero-shot when model lacks pretrained capability for task

#### Variant C: Auto-CoT
Dynamically select demonstration examples from an example store.

```python
# 1. Build example store (offline)
example_store = VectorDatabase()
for question in question_bank:
    # Generate reasoning chain via Zero-shot CoT
    answer = model.generate(f"{question}\nThink step-by-step.")
    # Validate correctness
    if passes_consistency_checks(answer) and is_correct(answer):
        example_store.add(question, answer)

# 2. At inference time
def get_demonstrations(query, k=5):
    similar_examples = example_store.similarity_search(query, k=k)
    return format_as_few_shot_prompt(similar_examples, query)
```

### Limitations
- Does NOT fix data gaps (model doesn't know facts)
- Does NOT work for non-sequential logic (cyclical dependencies, optimization across scenarios)
- Consider using Tool Calling for calculations to avoid arithmetic hallucinations

---

## Pattern 2: Tree of Thoughts (ToT)

### When to Apply
- Task requires exploring multiple solution approaches
- Single reasoning path likely leads to suboptimal solutions
- Problem benefits from backtracking when approach fails
- Strategic planning, creative writing, multi-constraint optimization

### Architecture

```
[Problem] 
    ├── [Thought 1] (score: 0.75) ──► [Thought 1.1] ──► [Thought 1.1.1] ✓
    │                              └── [Thought 1.2] ✗ (pruned)
    ├── [Thought 2] (score: 0.60) ──► (explored but lower priority)
    └── [Thought 3] (score: 0.35) ✗ (pruned early)
```

### Implementation

```python
import heapq
import json
from typing import List

class TreeOfThoughts:
    def __init__(self, model, beam_width=3, max_steps=4, 
                 num_thoughts_per_step=3):
        self.model = model
        self.beam_width = beam_width  # Top-K paths to maintain
        self.max_steps = max_steps
        self.num_thoughts = num_thoughts_per_step
    
    def generate_thoughts(self, state: str, step: int) -> List[str]:
        """Generate diverse next steps from current state."""
        prompt = f"""{state}
        Generate {self.num_thoughts} distinct and diverse next steps 
        for step {step} of {self.max_steps}.
        Make each thought meaningfully different.
        Return as JSON list of strings."""
        return json.loads(self.model.generate(prompt))
    
    def evaluate_state(self, state: str, problem: str) -> float:
        """Score path promise on 0-1 scale."""
        prompt = f"""
        Problem: {problem}
        Reasoning path: {state}
        
        Score 0-100 on: Correctness, Progress, Insight, Potential.
        Return only the integer score."""
        score = int(self.model.generate(prompt)) / 100.0
        return score
    
    def solve(self, problem: str) -> str:
        beam = [(0, problem, [], 0)]  # (neg_score, state, path, step)
        best_solutions = []
        
        while beam:
            candidates = []
            for neg_score, state, path, step in beam:
                if step >= self.max_steps:
                    best_solutions.append((-neg_score, state, path))
                    continue
                    
                thoughts = self.generate_thoughts(state, step + 1)
                for thought in thoughts:
                    new_state = f"{state}\nStep {step+1}: {thought}"
                    new_path = path + [thought]
                    new_score = self.evaluate_state(new_state, problem)
                    
                    # Early termination on high-confidence solution
                    if new_score > 0.9:
                        best_solutions.append((new_score, new_state, new_path))
                    else:
                        candidates.append((-new_score, new_state, new_path, step+1))
            
            # Beam search: keep top-K
            beam = heapq.nsmallest(self.beam_width, candidates)
        
        # Generate final summary from best path
        best = max(best_solutions, key=lambda x: x[0])
        return self.summarize_solution(problem, best[1])
    
    def summarize_solution(self, problem: str, final_state: str) -> str:
        """Generate concise solution from reasoning path."""
        prompt = f"""
        Problem: {problem}
        Complete reasoning path: {final_state}
        
        Provide a concise summary of the solution."""
        return self.model.generate(prompt)
```

### Cost/Latency Considerations
- Requires `O(beam_width × num_thoughts × max_steps)` LLM calls
- Typical: 30-50 API calls per problem
- Latency: 1-3 minutes depending on model speed
- **Optimization**: Parallelize thought generation within each level

### When NOT to Use
- Simple factual queries
- Tasks where CoT suffices
- Real-time latency requirements (<5s)
- Problems solvable with single reasoning chain

---

## Pattern 3: Adapter Tuning (LoRA/QLoRA)

### When to Apply
- Need consistent output style/format
- Have 100-10,000 input-output example pairs
- Task is similar to model's pretrained capabilities (not new knowledge)
- Cost/latency constraints require smaller model
- On-premise/edge deployment requirements

### What Adapter Tuning Does NOT Do
- ❌ Teach new vocabulary or jargon (use continued pretraining)
- ❌ Add new factual knowledge (use RAG)
- ❌ Enable fundamentally new capabilities (use instruction tuning)

### Implementation

```python
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
from peft import LoraConfig
from trl import SFTTrainer, SFTConfig

# 1. Load quantized base model
model = AutoModelForCausalLM.from_pretrained(
    "model-id",
    quantization_config=BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_use_double_quant=True,
        bnb_4bit_quant_type="nf4",
    )
)

# 2. Configure adapter layers
peft_config = LoraConfig(
    r=16,                    # Rank: higher = more parameters, needs more data
    lora_alpha=16,           # Scaling factor (typically equal to r)
    lora_dropout=0.05,
    target_modules="all-linear",
    task_type="CAUSAL_LM",
)

# 3. Prepare training data as messages
training_data = [
    {
        "messages": [
            {"role": "system", "content": "System prompt"},
            {"role": "user", "content": input_text},
            {"role": "assistant", "content": desired_output}
        ]
    }
    for input_text, desired_output in examples
]

# 4. Train
trainer = SFTTrainer(
    model=model,
    args=SFTConfig(
        output_dir="./adapter-model",
        num_train_epochs=1,        # Usually 1-3 epochs
        learning_rate=2e-4,        # Low learning rate preserves base capabilities
        per_device_train_batch_size=4,
    ),
    train_dataset=training_data,
    peft_config=peft_config,
)
trainer.train()
trainer.save_model()
```

### Inference

```python
from transformers import AutoModelForCausalLM, AutoTokenizer

# Load adapter (automatically loads base model too)
model = AutoModelForCausalLM.from_pretrained("./adapter-model")
tokenizer = AutoTokenizer.from_pretrained("./adapter-model")

# Use normally
inputs = tokenizer(prompt, return_tensors="pt")
outputs = model.generate(**inputs)
```

### Hyperparameter Guidelines

| Dataset Size | Rank (r) | Epochs | Learning Rate |
|-------------|----------|--------|---------------|
| 100-500     | 8        | 1      | 1e-4          |
| 500-2000    | 16       | 1-2    | 2e-4          |
| 2000-10000  | 32       | 2-3    | 2e-4          |

---

## Pattern 4: Evol-Instruct (Dataset Generation for Instruction Tuning)

### When to Apply
- Need to teach model complex enterprise/domain-specific tasks
- Have few seed examples but need thousands for training
- Task is genuinely new (not in model's pretraining)
- Can afford higher development cost for specialized capability

### Pipeline

```
Seed Instructions (10-100)
        │
        ▼
[Step 1: Evolve Instructions] ──► 10x expansion
        │
        ▼
[Step 2: Generate Answers] ──► Teacher model or expert
        │
        ▼
[Step 3: Evaluate & Filter] ──► Quality threshold
        │
        ▼
[Step 4: Instruction Tuning] ──► SFT on filtered dataset
```

### Step 1: Evolve Instructions

```python
def evolve_instruction(model, instruction: str, evolution_type: str) -> list[str]:
    prompts = {
        "deepen": f"""
            Rewrite this instruction to be harder by adding:
            - Constraints based on realistic conditions
            - Hypothetical complications
            Original: {instruction}
            Generate 3 harder versions as a JSON list.""",
        
        "concretize": f"""
            Make this instruction more concrete by:
            - Asking for specific counts ("3 reasons why")
            - Requesting explicit steps
            - Asking about specific outcomes
            Original: {instruction}
            Generate 3 more concrete versions as a JSON list.""",
        
        "combine": f"""
            Combine these two instructions into a single complex instruction:
            1. {instruction}
            2. {{another_instruction}}
            Return the combined instruction."""
    }
    
    return model.generate(prompts[evolution_type])
```

### Step 2: Generate Answers

Choose strategy based on domain:

```python
# Option A: Teacher model (most common)
def generate_answer_teacher(frontier_model, instruction: str, context: str = None) -> str:
    prompt = f"""
    Context: {context if context else "Use your knowledge."}
    
    Question: {instruction}
    
    Provide a thorough, accurate answer in 2-3 sentences.
    """
    return frontier_model.generate(prompt)  # Use most capable model

# Option B: Reflection loop (for verifiable tasks like code/math)
def generate_answer_reflection(model, evaluator, instruction: str, max_attempts: int = 3) -> str:
    for attempt in range(max_attempts):
        answer = model.generate(instruction)
        evaluation = evaluator.check(answer)  # Compiler, test suite, etc.
        if evaluation.passed:
            return answer
        instruction = f"{instruction}\n\nPrevious attempt failed: {evaluation.error}\nTry again."
    return None  # Discard if all attempts fail

# Option C: RAG-augmented (when knowledge base exists)
def generate_answer_rag(model, vector_store, instruction: str) -> str:
    relevant_docs = vector_store.search(instruction)
    return model.generate(f"Using these sources:\n{relevant_docs}\n\nAnswer: {instruction}")
```

### Step 3: Evaluate and Filter

```python
import json

def evaluate_example(model, question: str, answer: str) -> tuple[int, str]:
    prompt = f"""
    Evaluate this Q&A pair for training data quality.
    
    Question: {question}
    Answer: {answer}
    
    Score 1-5 where:
    1 = Obvious, wrong, or generic
    5 = Genuinely insightful and accurate
    
    Return JSON: {{"score": int, "explanation": str}}
    """
    result = json.loads(model.generate(prompt))
    return result["score"], result["explanation"]

# Filter to high-quality examples only
def filter_dataset(model, dataset: list[dict]) -> list[dict]:
    return [
        ex for ex in dataset 
        if evaluate_example(model, ex["question"], ex["answer"])[0] >= 4
    ]
```

### Step 4: Instruction Tuning

```python
from unsloth import FastLanguageModel, UnslothTrainingArguments

# Load model
model, tokenizer = FastLanguageModel.from_pretrained(
    model_name="unsloth/Meta-Llama-3.1-8B-bnb-4bit",
    max_seq_length=4096,
    load_in_4bit=True,
)

# For instruction tuning, must include gate_proj, embed_tokens, lm_head
model = FastLanguageModel.get_peft_model(
    model,
    r=16,
    target_modules=[
        "q_proj", "k_proj", "v_proj", "o_proj",
        "gate_proj",           # Required for instruction tuning
        "up_proj", "down_proj",
        "embed_tokens",        # Required for new task learning
        "lm_head",             # Required for new task learning
    ],
    lora_alpha=32,
    use_rslora=True,
)

# Different learning rates for different layer types
training_args = UnslothTrainingArguments(
    output_dir="./instruction-tuned-model",
    num_train_epochs=3,        # More epochs needed than adapter tuning
    learning_rate=1e-4,
    embedding_learning_rate=2.5e-5,  # Lower for embeddings
    gradient_accumulation_steps=64,
    per_device_train_batch_size=2,
)
```

### Dataset Size Guidelines

| Model Size | Minimum Examples | Recommended |
|-----------|------------------|-------------|
| 1B        | 10,000          | 20,000+     |
| 7B        | 5,000           | 10,000+     |
| 13B+      | 2,000           | 5,000+      |

---

## Quick Reference: Pattern Selection

| Symptom | Pattern | Implementation Effort |
|---------|---------|----------------------|
| Model skips reasoning steps | Zero-shot CoT | Low (prompt change) |
| Model uses wrong logic | Few-shot CoT | Low (add examples to prompt) |
| Need dynamic example selection | Auto-CoT | Medium (build example store) |
| Problem needs path exploration | ToT | Medium-High (orchestration code) |
| Need consistent output format | Adapter Tuning | Medium (training pipeline) |
| Need entirely new capability | Evol-Instruct | High (dataset + training) |
| Model lacks facts | **Use RAG, not these patterns** | - |

---

## Anti-Patterns

1. **Using Adapter Tuning for new knowledge** → Use RAG instead
2. **Using ToT for simple queries** → Wastes 30-50x compute
3. **Instruction tuning for style changes** → Adapter tuning is 10x cheaper
4. **Skipping evaluation in Evol-Instruct** → Garbage in, garbage out
5. **Zero-shot CoT on small models** → Use Few-shot CoT instead

---

## Maintenance Note

Set calendar reminder: Check every 6 months if CoT/ToT patterns are still needed as frontier models improve. Human-written demonstration examples add maintenance overhead—remove them when possible to reduce token costs and simplify prompts.

---

## References

### Chain of Thought (CoT)

- **Wei et al. (2022)** - Introduced CoT prompting. Showed that few step-by-step examples enable LLMs to solve arithmetic, common sense, and symbolic reasoning more accurately.
- **Kojima et al. (2022)** - Demonstrated Zero-shot CoT. Showed reasoning steps can be elicited by simply adding "think step-by-step" without examples.
- **Zhang et al. (2022)** - Introduced Auto-CoT with two key innovations: sampling questions with diversity and generating reasoning chains using Zero-shot CoT to populate example stores.

### Tree of Thoughts (ToT)

- **Yao et al. (2023)** - "Tree of Thoughts: Deliberate Problem Solving with Large Language Models". Detailed description of ToT concept and implementation.
- **Muennighoff et al. (2025)** - Proposed wait-injection (budget forcing) as a simpler alternative that injects "Wait" when model attempts to terminate, forcing reevaluation.

### Adapter Tuning / LoRA

- **Houlsby et al. (2019)** - Introduced Sequential Adapter architecture for parameter-efficient fine-tuning.
- **Wei et al. (2021)** - Showed improvements in developing assistant models with improved zero-shot performance across unseen tasks.
- **Li and Liang (2021)** - Demonstrated prefix tuning achieves performance comparable to full fine-tuning with small fraction of trainable parameters.
- **Lester et al. (2021)** - Showed prompt tuning matches full fine-tuning for billion-parameter models while requiring only small task-specific prompts.
- **Xu et al. (2023)** - Comprehensive review of PeFT methods comparing parameter efficiency and memory efficiency.
- **Dettmers et al. (2023)** - Introduced QLoRA (Quantization-aware Low-Rank Adaptation), now the most commonly used adapter tuning technique.
- **Biderman et al. (2024)** - Analyzed LoRA behavior: "learns less and forgets less" compared to full fine-tuning.

### Evol-Instruct / Instruction Tuning

- **Xu et al. (2023)** - "WizardLM" paper. Introduced the Evol-Instruct concept for generating instruction-tuning datasets.
- **Luo et al. (2025)** - "WizardCoder" paper. Demonstrated domain-specific application of Evol-Instruct for code generation.
- **Gunasekar et al. (2023)** - "Textbooks Are All You Need". Demonstrated that small models trained on high-quality curated data outperform larger models on unorganized datasets.
- **Zhang et al. (2023)** - Survey paper on instruction tuning, covering state of the field.

### Production Implementations

- **Invisible + Allen & Overy (2025)** - Applied CoT to legal applications.
- **K2view** - Implemented CoT reasoning in GenAI Data Fusion platform for enterprise chatbots with real-time data integration.
- **Fractional AI + Change.org** - Used Adapter Tuning to fine-tune GPT-3.5 for content moderation using human moderation decisions as training data.
