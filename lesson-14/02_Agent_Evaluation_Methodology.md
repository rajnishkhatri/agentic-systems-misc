# Agent Evaluation Methodology

**Source:** Google's "Agents Companion" Whitepaper (February 2025)
**Topic Complexity:** ⭐⭐⭐⭐⭐
**Lines:** 96-181 from original document

---

## Overview

Agent evaluation requires a **deeper understanding** than evaluating generative models alone. It encompasses three core components:
1. **Assessing Agent Capabilities** (benchmarks, core abilities)
2. **Evaluating Trajectory and Tool Use** (the steps taken)
3. **Evaluating the Final Response** (output quality)

**Key Principle**: Unlike traditional software testing, agents require both **automated evaluation** and **human-in-the-loop** validation due to their non-deterministic nature.

---

## 1. Assessing Agent Capabilities

### Public Benchmarks

Before evaluating specific use cases, leverage public benchmarks to understand core capabilities and limitations.

#### Tool Calling Benchmarks

**Berkeley Function-Calling Leaderboard (BFCL)**
- Measures ability to select and use appropriate tools
- Identifies common mistakes in tool invocation
- Reference: https://gorilla.cs.berkeley.edu/blogs/8_berkeley_function_calling_leaderboard.html

**τ-bench (Tau-bench)**
- Evaluates tool calling across diverse scenarios
- Outlines common failure modes
- Reference: Karthik Narasimhan et al., 2024

#### Planning & Reasoning Benchmarks

**PlanBench**
- Assesses planning and reasoning across domains
- Evaluates specific capabilities (decomposition, sequencing, constraint handling)
- Reference: Karthik Valmeekam et al., 2023

#### Holistic Agent Benchmarks

**AgentBench**
- End-to-end performance across multiple scenarios
- More realistic when scenario matches your use case
- Limitation: May test capabilities your agent doesn't implement
- Reference: Xiao Liu et al., 2023

#### Specialized Domain Benchmarks

**DBAStep (Adyen Data Analyst Leaderboard)**
- Targeted evaluation for specific use cases (data analysis)
- Useful if your domain aligns with benchmark
- Reference: Martin Iglesias et al., 2025

### Inherited Behaviors

**Agents inherit behaviors from all components**:
- LLM capabilities (reasoning, language understanding)
- Tool integrations (API reliability, data quality)
- Orchestration logic (prompt engineering, flow control)

**Traditional conversational design metrics still apply**:
- Turn-level success rates
- Dialog completion rates
- User satisfaction (CSAT)
- Task completion efficiency

### Public Benchmark Limitations

**Valuable for**:
- Understanding what's possible
- Identifying common pitfalls
- Baseline capability assessment

**Not sufficient for**:
- Production use-case validation
- Domain-specific evaluation
- Real-world performance prediction

**Action**: Use public benchmarks as starting point, then build use-case-specific evaluation.

---

## 2. Evaluating Trajectory and Tool Use

### What is a Trajectory?

**Definition**: The sequence of actions an agent takes before responding to the user.

**Example Trajectory**:
1. Compare user input with session history (disambiguation)
2. Lookup policy document (RAG retrieval)
3. Search knowledge base (vector search)
4. Invoke API to save ticket (tool use)
5. Generate response

### Why Evaluate Trajectories?

**Benefits**:
- **Debug agent behavior**: Identify errors or inefficiencies
- **Improve performance**: Optimize action sequences
- **Ensure correct tool use**: Validate agent is using right tools
- **Compare approaches**: Evaluate different orchestration strategies

**Use Case**: Particularly useful for **developers** building and refining agents.

### Six Ground-Truth-Based Trajectory Metrics

All metrics require a **reference trajectory** (expected sequence of actions).

#### 1. Exact Match

**Definition**: Agent's trajectory must **perfectly mirror** the ideal solution.

**Characteristics**:
- Most rigid metric
- No deviation allowed
- High precision, low flexibility

**When to use**:
- Critical workflows with strict compliance requirements
- Financial transactions
- Medical diagnosis steps

**Example**:
```
Reference: [authenticate, validate_balance, process_payment, send_receipt]
Agent:     [authenticate, validate_balance, process_payment, send_receipt]
Result:    ✅ Exact Match
```

#### 2. In-Order Match

**Definition**: Agent must complete **core steps in sequence**, but extra actions are allowed.

**Characteristics**:
- Maintains order requirement
- Permits additional (unpenalized) actions
- More flexible than exact match

**When to use**:
- Workflows with required sequence but optional steps
- Debugging where extra logging is acceptable

**Example**:
```
Reference: [search_product, add_to_cart, checkout]
Agent:     [search_product, log_search, add_to_cart, validate_stock, checkout]
Result:    ✅ In-Order Match (extra: log_search, validate_stock)
```

#### 3. Any-Order Match

**Definition**: Agent must include **all necessary actions**, but order doesn't matter.

**Characteristics**:
- Disregards sequence
- Allows extra steps
- Checks for action completeness

**When to use**:
- Parallel execution scenarios
- Independent task completion
- Order-agnostic workflows

**Example**:
```
Reference: [fetch_weather, fetch_news, fetch_calendar]
Agent:     [fetch_calendar, check_network, fetch_weather, fetch_news]
Result:    ✅ Any-Order Match (all actions present)
```

#### 4. Precision

**Definition**: % of agent's tool calls that are **relevant/correct** per reference trajectory.

**Formula**:
```
Precision = (Correct Tool Calls in Agent Trajectory) / (Total Tool Calls in Agent Trajectory)
```

**Characteristics**:
- Penalizes extra/incorrect actions
- High precision = low noise

**When to use**:
- Cost-sensitive applications (minimize API calls)
- Performance optimization (reduce latency)

**Example**:
```
Reference: [search_docs, summarize]
Agent:     [search_docs, search_web, summarize, log_result]
Precision: 2 correct / 4 total = 0.50 (50%)
```

#### 5. Recall

**Definition**: % of essential tool calls from reference trajectory **captured by agent**.

**Formula**:
```
Recall = (Essential Tool Calls Captured) / (Total Essential Tool Calls in Reference)
```

**Characteristics**:
- Penalizes missing actions
- High recall = complete coverage

**When to use**:
- Safety-critical applications (all steps required)
- Compliance workflows (complete audit trail)

**Example**:
```
Reference: [validate_user, check_permissions, execute_action, log_audit]
Agent:     [validate_user, execute_action, log_audit]
Recall:    3 captured / 4 essential = 0.75 (75%) - Missing: check_permissions
```

#### 6. Single-Tool Use

**Definition**: Checks if a **specific action** is within the agent's trajectory.

**Characteristics**:
- Binary metric (used or not)
- Tool-specific validation

**When to use**:
- Verify agent has learned to use particular tool
- A/B testing new tool integrations
- Monitoring tool adoption

**Example**:
```
Check: Did agent use "send_notification" tool?
Agent Trajectory: [process_request, update_database, send_notification]
Result: ✅ Yes (single-tool use confirmed)
```

### Trajectory Evaluation Best Practices

**1. Choose metrics based on use case**:
- Strict workflows → Exact Match
- Flexible workflows → In-Order or Any-Order Match
- Optimization → Precision & Recall

**2. Different lenses for analysis**:
- Not all metrics relevant to every situation
- Use multiple metrics for comprehensive view
- Example: High precision + low recall = agent is accurate but incomplete

**3. Radar Chart Visualization**:
- Plot multiple metrics simultaneously
- Identify strengths and weaknesses at a glance
- Compare different agent versions

**Example Radar Chart** (from document):
```
        Exact Match
              |
    Precision  ———  Recall
              |
      In-Order Match
              |
        Any-Order Match
```

### Limitations of Ground-Truth Trajectory Evaluation

**Requires reference trajectories**:
- Manual effort to create expected paths
- May not cover all valid approaches
- Assumes single "correct" path

**Future Direction: Agent-as-a-Judge**:
- Research advancing toward automated trajectory evaluation
- LLM evaluates if trajectory is reasonable (not just matching reference)
- Reference: Mingchen Zhuge et al., 2024. "Agent-as-a-Judge: Evaluate Agents with Agents"

---

## 3. Evaluating the Final Response

### The Core Question

**Does your agent achieve its goals?**

This is about **outcome quality**, not the path taken.

### Custom Success Criteria

Define **tailored metrics** for your specific use case:

**Retail Chatbot Example**:
- Accuracy: Does answer match product documentation?
- Relevance: Does response address customer question?
- Completeness: Are all aspects of question covered?

**Research Agent Example**:
- Summary quality: Are key findings captured?
- Tone: Is response appropriately formal/informal?
- Style: Does it match organizational voice?
- Citations: Are sources properly referenced?

### Autorater (LLM-as-a-Judge)

**Definition**: An LLM that evaluates responses against user-defined criteria.

**How it works**:
1. Input: Original prompt + generated response
2. Evaluation criteria: User-provided quality dimensions
3. Output: Scores/ratings for each criterion

**Key Success Factor**: **Precise criterion definitions**
- Absence of ground-truth requires clear specifications
- Pre-defined criteria in libraries are starting points
- Customize criteria for your domain

**Example Criteria**:
```python
evaluation_criteria = {
    "accuracy": "Does the response contain factually correct information from source documents?",
    "completeness": "Does the response address all parts of the user's question?",
    "tone": "Is the tone professional and empathetic?",
    "brevity": "Is the response concise without omitting key details?"
}
```

### Autorater Best Practices

**1. Start with library criteria, then customize**:
- Use pre-built criteria from evaluation frameworks
- Adapt to your domain (medical, legal, customer service)
- Iterate based on human validation

**2. Multi-dimensional evaluation**:
- Evaluate multiple aspects (accuracy, tone, style)
- Weight criteria by importance
- Aggregate scores for overall quality

**3. Validate autoraters with humans**:
- Compare LLM judgments to expert evaluations
- Calibrate thresholds based on business needs
- Track autorater agreement with humans over time

---

## 4. Human-in-the-Loop Evaluation

### Why Human Evaluation Matters

**Agent development is rapidly evolving**:
- Defining clear objectives is challenging
- Realistic environment design is complex
- Stochastic behavior requires interpretation
- Fairness and bias mitigation need human judgment

**Automated evaluation is powerful, but insufficient alone.**

### Key Benefits

#### 1. Subjectivity
- Evaluate qualities difficult to quantify:
  - Creativity
  - Common sense
  - Nuance
  - Cultural appropriateness

#### 2. Contextual Understanding
- Consider broader context of agent's actions
- Assess real-world implications
- Identify edge cases not in test data

#### 3. Iterative Improvement
- Provide insights for refining behavior
- Guide learning process with expert feedback
- Validate assumptions in automated evaluation

#### 4. Evaluating the Evaluator
- **Calibrate autoraters** with human feedback
- Ensure LLM-as-a-Judge aligns with human preferences
- Track agreement rates over time

### Human Evaluation Methods

#### 1. Direct Assessment
**Description**: Human experts directly rate/score agent performance.

**Process**:
- Define rating scale (1-5, Likert scale)
- Provide clear rubrics for each score
- Aggregate ratings across multiple evaluators

**Example**:
```
Rate the agent's response on a scale of 1-5:
1 = Completely incorrect or irrelevant
2 = Partially correct but missing key information
3 = Correct but could be improved
4 = Good response with minor issues
5 = Excellent, comprehensive, accurate response
```

#### 2. Comparative Evaluation
**Description**: Experts compare agent performance to other agents or previous iterations.

**Process**:
- Present responses from multiple agents side-by-side
- Ask evaluator to rank or choose best response
- Track improvement over versions

**Example**:
```
Which agent response is better for this query?
[ ] Agent A (Baseline)
[ ] Agent B (New Version)
[ ] Tie
```

**Use Cases**:
- A/B testing new agent versions
- Benchmarking against competitors
- Elo ranking systems (see Lesson 11)

#### 3. User Studies
**Description**: Participants interact with agent and provide feedback.

**Process**:
- Real-world usage scenarios
- Post-interaction surveys
- Usability metrics (task completion time, satisfaction)

**Metrics**:
- Behavior: Did users achieve their goals?
- Usability: Was the agent easy to use?
- Effectiveness: Did the agent solve the problem?
- Satisfaction: Would users use the agent again?

**Example**:
```
After using the agent to book a flight:
- How easy was it to complete your task? (1-10)
- Did the agent understand your requests? (Yes/No)
- Would you use this agent again? (Yes/No/Maybe)
- Any suggestions for improvement? (Free text)
```

### Balancing Automated and Human Evaluation

**Automated Evaluation**:
- **Strengths**: Scalable, efficient, consistent
- **Weaknesses**: Limited by metrics, may miss nuance
- **Use for**: Continuous monitoring, regression testing

**Human Evaluation**:
- **Strengths**: Captures nuance, subjective quality, context
- **Weaknesses**: Expensive, time-consuming, doesn't scale
- **Use for**: Calibration, edge cases, final validation

**Recommended Approach**:
1. Start with automated evaluation for continuous monitoring
2. Regularly validate with human evaluation (weekly/monthly)
3. Use human feedback to improve automated evaluators
4. Reserve human evaluation for high-stakes decisions

---

## Comparison: Evaluation Method Strengths & Weaknesses

| Method | Strengths | Weaknesses |
|--------|-----------|------------|
| **Human Evaluation** | Captures nuanced behavior, considers human factors, contextual understanding | Subjective, time-consuming, expensive, difficult to scale |
| **LLM-as-a-Judge** | Scalable, efficient, consistent, automates subjective evaluation | May overlook intermediate steps, limited by LLM capabilities, requires precise criteria |
| **Automated Metrics** | Objective, scalable, efficient, quantitative tracking | May not capture full capabilities, susceptible to gaming, requires ground-truth data |

---

## Advanced Topics in Agent Evaluation

### Process-Based Evaluation (Future Direction)

**Shift from outcomes to reasoning**:
- Understand **how** agent reached conclusion
- Validate intermediate steps, not just final answer
- Detect flawed reasoning that happened to produce correct output

**Example**: Agent provides correct answer but used faulty logic → Process-based eval catches this.

### AI-Assisted Evaluation

**Scaling evaluation with AI**:
- LLM-as-a-Judge for subjective criteria
- Automated trajectory analysis with agent evaluators
- Synthetic test case generation

**Benefit**: Combines scalability of automation with nuance of human evaluation.

### Real-World Evaluation Challenges

**Dynamic environments**:
- Agents operate in unpredictable settings
- Evaluation in controlled settings may not reflect production
- Need for **production monitoring** (see Topic 1: AgentOps)

**Multi-modal generations**:
- Images, audio, video require specialized evaluation
- Different metrics for each modality
- Cross-modal consistency evaluation

**Explainability & Interpretability**:
- Understanding **why** agent made decisions
- Providing deeper insights into behavior
- Building trust with stakeholders

### Standardized Benchmarks (Emerging)

**Trend**: Development of new benchmarks for objective agent comparison
- Cross-organization agent leaderboards
- Industry-specific benchmarks (healthcare, finance, legal)
- Open-source evaluation datasets

**Benefit**: Facilitates objective comparison between agents.

---

## Key Takeaways

1. **Agent evaluation has 3 components**: Capabilities (benchmarks), Trajectory (path), Response (output)
2. **Start with public benchmarks**: Understand core capabilities and common pitfalls
3. **Trajectory evaluation requires reference data**: Choose metrics based on use case (exact match, precision, recall)
4. **Autoraters need precise criteria**: Define evaluation dimensions clearly for LLM-as-a-Judge
5. **Human-in-the-loop is essential**: Validate automation, capture nuance, calibrate autoraters
6. **Balance automation and human eval**: Automated for scale, human for calibration and edge cases
7. **Process-based evaluation is the future**: Focus on reasoning, not just outcomes

---

## Practical Implementation Checklist

### For Developers

**Capability Assessment**:
- [ ] Identify relevant public benchmarks for your use case
- [ ] Run baseline capability tests (tool calling, planning)
- [ ] Document common failure modes from benchmarks

**Trajectory Evaluation**:
- [ ] Create reference trajectories for key user journeys
- [ ] Choose appropriate metrics (exact/in-order/any-order match)
- [ ] Instrument agent to log all actions (see Topic 1: Observability)
- [ ] Calculate precision/recall for tool usage

**Response Evaluation**:
- [ ] Define custom success criteria for your domain
- [ ] Set up autorater with clear evaluation dimensions
- [ ] Validate autorater judgments with human experts

**Human-in-the-Loop**:
- [ ] Design user study or expert evaluation protocol
- [ ] Collect human feedback on sample of agent outputs
- [ ] Compare human ratings to automated metrics
- [ ] Iterate on evaluation criteria based on feedback

---

## Related Topics

- **Topic 1**: AgentOps & Operations (metrics, observability, production monitoring)
- **Topic 3**: Multi-Agent Architectures (evaluation complexity in multi-agent systems)
- **Topic 7**: Case Studies - Automotive AI (real-world evaluation examples)
- **Topic 9**: Vertex AI Ecosystem (Google's evaluation tooling)

---

## References

- Berkeley Function-Calling Leaderboard (BFCL): https://gorilla.cs.berkeley.edu/blogs/8_berkeley_function_calling_leaderboard.html
- Karthik Narasimhan et al., 2024. "τ-bench"
- Karthik Valmeekam et al., 2023. "PlanBench"
- Xiao Liu et al., 2023. "AgentBench"
- Martin Iglesias et al., 2025. "DABStep"
- Mingchen Zhuge et al., 2024. "Agent-as-a-Judge: Evaluate Agents with Agents"
- LangSmith platform: https://docs.smith.langchain.com/evaluation/concepts#agents
- Figure 5: LangSmith diagram of final evaluation and trajectory
- Figure 6: Radar chart for trajectory evaluation
- Table 1: Evaluation method comparison (page 23)

---

**Next Topic**: [Multi-Agent Architectures](03_Multi_Agent_Architectures.md)
