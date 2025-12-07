# Multiagent Failure Modes & Debugging

Based on empirical analysis showing 40-80% task failure rates in complex multiagent systems.

## Failure Taxonomy

### Category 1: Specification Issues

Failures from system design, not execution.

#### 1.1 Role Confusion

**Symptom**: Agent acts outside defined scope, overlaps with other agents.

**Example**:
```
Researcher Agent: "I'll write up the final report with recommendations..."
[Should only research, not write recommendations]
```

**Diagnosis**:
```python
# Check if output contains keywords outside agent's role
def detect_role_confusion(agent_name: str, output: str, role_keywords: dict):
    agent_scope = role_keywords[agent_name]
    other_scopes = set()
    for name, keywords in role_keywords.items():
        if name != agent_name:
            other_scopes.update(keywords)
    
    violations = [kw for kw in other_scopes if kw.lower() in output.lower()]
    return violations

# Example usage
role_keywords = {
    "researcher": ["data", "source", "reference", "study"],
    "analyst": ["insight", "trend", "recommendation", "conclusion"],
    "writer": ["draft", "paragraph", "prose", "narrative"]
}
```

**Fix**: Strengthen system prompts with explicit boundaries.

```python
system_prompt = """You are ONLY a researcher.
YOUR SCOPE: Find facts, cite sources, report data
NOT YOUR SCOPE: Analysis, recommendations, writing prose
If asked to do something outside your scope, respond:
"That's outside my role. Please route to [appropriate agent]."
"""
```

#### 1.2 Instruction Drift

**Symptom**: Agent forgets instructions over long conversations.

**Diagnosis**:
```python
def detect_instruction_drift(conversation: list, original_instructions: str):
    """Check if recent outputs align with original instructions."""
    recent = conversation[-3:]  # Last 3 turns
    
    instruction_keywords = extract_keywords(original_instructions)
    
    drift_score = 0
    for turn in recent:
        turn_keywords = extract_keywords(turn["content"])
        overlap = len(instruction_keywords & turn_keywords) / len(instruction_keywords)
        drift_score += (1 - overlap)
    
    return drift_score / len(recent)  # 0 = no drift, 1 = complete drift
```

**Fix**: Inject instruction reminders periodically.

```python
def add_instruction_reminder(messages: list, system_prompt: str, frequency: int = 5):
    """Add reminders every N turns."""
    if len(messages) % frequency == 0:
        messages.append({
            "role": "system",
            "content": f"REMINDER: {system_prompt[:500]}"
        })
    return messages
```

#### 1.3 Premature Termination

**Symptom**: Task ends before completion, missing steps.

**Diagnosis**:
```python
def check_completion(expected_outputs: list, actual_outputs: dict) -> dict:
    """Verify all expected outputs were produced."""
    missing = []
    incomplete = []
    
    for output in expected_outputs:
        if output not in actual_outputs:
            missing.append(output)
        elif not validate_output(actual_outputs[output]):
            incomplete.append(output)
    
    return {
        "complete": len(missing) == 0 and len(incomplete) == 0,
        "missing": missing,
        "incomplete": incomplete
    }
```

**Fix**: Add explicit completion checklist.

```python
COMPLETION_CHECKLIST = """
Before finishing, verify:
[ ] All subtasks addressed
[ ] Output format matches specification
[ ] No unanswered questions remain
[ ] Summary provided

If any unchecked, continue working. Do not terminate early.
"""
```

---

### Category 2: Interagent Misalignment

Failures from agent interactions.

#### 2.1 Information Withholding

**Symptom**: Agent has relevant info but doesn't share it.

**Example**:
```
Agent A: "I found the customer's order history."
Agent B: "What are their preferences?" 
Agent A: "I recommend we proceed." [Doesn't share the order data]
```

**Diagnosis**:
```python
def detect_withholding(agent_outputs: dict, query_history: list):
    """Check if agents answered queries with available info."""
    issues = []
    
    for query in query_history:
        # Find which agent was asked
        asked_agent = query["to"]
        question = query["content"]
        
        # Check if that agent has relevant info
        agent_knowledge = extract_entities(agent_outputs.get(asked_agent, ""))
        question_entities = extract_entities(question)
        
        overlap = agent_knowledge & question_entities
        if overlap and not any(e in query.get("response", "") for e in overlap):
            issues.append({
                "agent": asked_agent,
                "had_info": list(overlap),
                "query": question
            })
    
    return issues
```

**Fix**: Require explicit information sharing protocol.

```python
system_prompt_addition = """
INFORMATION SHARING PROTOCOL:
When another agent asks a question:
1. Check if you have ANY relevant information
2. Share ALL relevant data, not just your conclusion
3. Format: "Relevant info: [data]. My interpretation: [analysis]"
"""
```

#### 2.2 Conversation Reset

**Symptom**: Context suddenly lost, agent restarts from scratch.

**Diagnosis**:
```python
def detect_reset(conversation: list) -> list:
    """Find conversation reset points."""
    reset_indicators = [
        "let's start over",
        "to begin",
        "first, let me",
        "hello",  # Greeting mid-conversation
        "how can i help"
    ]
    
    resets = []
    for i, turn in enumerate(conversation):
        if i == 0:
            continue
        content = turn.get("content", "").lower()
        for indicator in reset_indicators:
            if indicator in content:
                resets.append({"turn": i, "indicator": indicator})
    
    return resets
```

**Fix**: Include conversation summary in each turn.

```python
def add_context_summary(messages: list, max_summary_length: int = 500) -> list:
    """Prepend conversation summary to maintain context."""
    if len(messages) < 3:
        return messages
    
    # Generate summary of prior turns
    prior_content = " ".join([m["content"] for m in messages[:-1]])
    summary = summarize(prior_content, max_length=max_summary_length)
    
    # Inject as system message
    return [
        {"role": "system", "content": f"CONVERSATION CONTEXT: {summary}"},
        *messages
    ]
```

#### 2.3 Reasoning-Action Mismatch

**Symptom**: Agent's stated reasoning doesn't match actions taken.

**Example**:
```
Agent: "The data shows we should reject this. Therefore, I approve the request."
```

**Diagnosis**:
```python
def check_reasoning_action_alignment(output: str) -> dict:
    """Detect misalignment between reasoning and conclusion."""
    
    # Extract reasoning section
    reasoning_indicators = ["because", "since", "the data shows", "therefore"]
    action_indicators = ["I will", "I recommend", "approved", "rejected", "decision:"]
    
    reasoning = extract_section(output, reasoning_indicators)
    action = extract_section(output, action_indicators)
    
    # Check sentiment alignment
    reasoning_sentiment = analyze_sentiment(reasoning)  # positive/negative/neutral
    action_sentiment = analyze_sentiment(action)
    
    return {
        "aligned": reasoning_sentiment == action_sentiment,
        "reasoning_sentiment": reasoning_sentiment,
        "action_sentiment": action_sentiment,
        "reasoning_excerpt": reasoning[:200],
        "action_excerpt": action[:200]
    }
```

**Fix**: Require explicit reasoning chain.

```python
structured_output_schema = """
Output must be JSON:
{
    "observations": ["fact1", "fact2"],
    "reasoning": "step-by-step logic",
    "conclusion": "derived from reasoning",
    "action": "must align with conclusion"
}
"""
```

---

### Category 3: Task Verification Failures

Failures to detect/correct errors.

#### 3.1 Cascading Errors

**Symptom**: Early mistake propagates through entire workflow.

**Diagnosis**:
```python
def trace_error_propagation(workflow_log: list) -> dict:
    """Find where errors originated and how they spread."""
    
    # Find first error
    first_error = None
    for i, step in enumerate(workflow_log):
        if step.get("validation", {}).get("errors"):
            first_error = {"step": i, "errors": step["validation"]["errors"]}
            break
    
    if not first_error:
        return {"cascade": False}
    
    # Trace downstream impact
    affected_steps = []
    error_content = str(first_error["errors"])
    
    for step in workflow_log[first_error["step"] + 1:]:
        if any(e in step.get("input", "") for e in first_error["errors"]):
            affected_steps.append(step["name"])
    
    return {
        "cascade": True,
        "origin": first_error,
        "affected_downstream": affected_steps
    }
```

**Fix**: Add validation gates between steps.

```python
class ValidationGate:
    def __init__(self, validators: list):
        self.validators = validators
    
    def check(self, output: dict, step_name: str) -> dict:
        errors = []
        for validator in self.validators:
            result = validator(output)
            if not result["valid"]:
                errors.append(result["error"])
        
        if errors:
            return {
                "proceed": False,
                "step": step_name,
                "errors": errors,
                "recommendation": "Retry step or escalate to human"
            }
        return {"proceed": True}

# Usage in workflow
gate = ValidationGate([
    check_not_empty,
    check_format,
    check_no_contradictions
])

result = agent1.run(input)
validation = gate.check(result, "agent1_output")
if not validation["proceed"]:
    result = retry_with_feedback(agent1, input, validation["errors"])
```

#### 3.2 Undetected Hallucinations

**Symptom**: Agent produces plausible but false information.

**Diagnosis**:
```python
def check_for_hallucinations(output: str, sources: list) -> dict:
    """Cross-reference claims against sources."""
    
    # Extract factual claims
    claims = extract_claims(output)  # "X is Y", "In 2023, Z happened"
    
    unverified = []
    for claim in claims:
        # Search sources for supporting evidence
        found_support = False
        for source in sources:
            if verify_claim(claim, source):
                found_support = True
                break
        
        if not found_support:
            unverified.append(claim)
    
    return {
        "total_claims": len(claims),
        "unverified": unverified,
        "hallucination_rate": len(unverified) / len(claims) if claims else 0
    }
```

**Fix**: Require citations, add verification agent.

```python
verification_agent_prompt = """You are a fact-checker.
For each claim in the content:
1. Search provided sources for evidence
2. Mark as VERIFIED (with source) or UNVERIFIED
3. For UNVERIFIED claims, search web if allowed

Output format:
- Claim: "..."
  Status: VERIFIED | UNVERIFIED
  Source: [citation] | "No source found"
"""
```

---

## Debugging Workflow

### Step 1: Capture Full Trace

```python
class MultiagentDebugger:
    def __init__(self):
        self.trace = []
    
    def log_step(self, agent: str, input: str, output: str, 
                 tools_called: list = None, metadata: dict = None):
        self.trace.append({
            "timestamp": datetime.utcnow().isoformat(),
            "agent": agent,
            "input_preview": input[:500],
            "output_preview": output[:500],
            "input_tokens": count_tokens(input),
            "output_tokens": count_tokens(output),
            "tools_called": tools_called or [],
            "metadata": metadata or {}
        })
    
    def analyze(self) -> dict:
        """Run all diagnostic checks."""
        return {
            "role_confusion": [detect_role_confusion(s) for s in self.trace],
            "resets": detect_reset([{"content": s["output_preview"]} for s in self.trace]),
            "token_usage": sum(s["input_tokens"] + s["output_tokens"] for s in self.trace),
            "tool_call_frequency": Counter(
                tool for s in self.trace for tool in s["tools_called"]
            )
        }
    
    def export_for_review(self, path: str):
        """Export trace for manual review."""
        with open(path, "w") as f:
            for step in self.trace:
                f.write(f"\n{'='*60}\n")
                f.write(f"Agent: {step['agent']}\n")
                f.write(f"Input:\n{step['input_preview']}\n")
                f.write(f"Output:\n{step['output_preview']}\n")
                if step['tools_called']:
                    f.write(f"Tools: {step['tools_called']}\n")
```

### Step 2: Isolate Failing Component

```python
def binary_search_failure(workflow: list, test_fn: callable) -> int:
    """Find which step introduced the failure."""
    
    def test_partial(end_idx: int) -> bool:
        partial_result = run_workflow(workflow[:end_idx])
        return test_fn(partial_result)
    
    left, right = 0, len(workflow)
    while left < right:
        mid = (left + right) // 2
        if test_partial(mid):
            left = mid + 1
        else:
            right = mid
    
    return left - 1  # Last successful step
```

### Step 3: Reproduce in Isolation

```python
def reproduce_step(agent_config: dict, input_snapshot: str, 
                   seed: int = 42) -> dict:
    """Reproduce single step deterministically."""
    
    # Set seed for reproducibility
    import random
    random.seed(seed)
    
    agent = create_agent(**agent_config, temperature=0)
    outputs = []
    
    # Run multiple times to check consistency
    for _ in range(3):
        output = agent.run(input_snapshot)
        outputs.append(output)
    
    return {
        "outputs": outputs,
        "consistent": len(set(outputs)) == 1,
        "variations": list(set(outputs))
    }
```

---

## Mitigation Strategies Summary

| Failure Mode | Quick Fix | Robust Fix |
|--------------|-----------|------------|
| Role confusion | Clearer system prompt | Add role validator agent |
| Instruction drift | Periodic reminders | Shorter context windows |
| Premature termination | Completion checklist | External workflow manager |
| Information withholding | Sharing protocol | Shared memory/blackboard |
| Conversation reset | Context summaries | Persistent state store |
| Reasoning-action mismatch | Structured output | Chain-of-thought validation |
| Cascading errors | Validation gates | Checkpoint & rollback |
| Hallucinations | Citation requirements | Verification agent |
