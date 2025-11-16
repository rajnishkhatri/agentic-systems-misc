# Agent Evaluation Fundamentals

**Reading Time:** 25-30 minutes
**Prerequisites:** Understanding of AI agents, LLM capabilities, basic MLOps concepts
**Learning Outcomes:** Understand AgentOps evolution, agent success metrics, observability architecture, and the three pillars of agent evaluation

---

## Table of Contents

1. [Introduction: Why Agent Evaluation is Different](#1-introduction-why-agent-evaluation-is-different)
2. [The Evolution to AgentOps](#2-the-evolution-to-agentops)
3. [Defining Agent Success: Metrics That Matter](#3-defining-agent-success-metrics-that-matter)
4. [Observability & Instrumentation](#4-observability--instrumentation)
5. [The Three Pillars of Agent Evaluation](#5-the-three-pillars-of-agent-evaluation)
6. [Public Benchmarks: Starting Point for Capability Assessment](#6-public-benchmarks-starting-point-for-capability-assessment)
7. [Metrics-Driven Development for Agents](#7-metrics-driven-development-for-agents)
8. [Production Readiness Framework](#8-production-readiness-framework)
9. [Practical Exercises](#9-practical-exercises)
10. [Key Takeaways](#10-key-takeaways)

---

## 1. Introduction: Why Agent Evaluation is Different

### The Fundamental Challenge

**Traditional Software (Deterministic)**:
- ✅ Does exactly what you tell it to do
- ✅ Predictable behavior across runs
- ✅ Edge cases can be enumerated and tested
- ✅ Unit tests provide high confidence

**AI Agents (Non-Deterministic)**:
- ⚠️ Can do much more than explicitly programmed (LLMs trained on vast data)
- ⚠️ Behavior varies across identical inputs
- ⚠️ Edge cases are nearly impossible to enumerate
- ⚠️ Traditional testing provides limited confidence

### Why This Matters

Consider this scenario:

```
User Query: "Book a flight to Paris next week"

Agent A (Traditional Chatbot):
- Follows predefined decision tree
- Fails if query doesn't match templates
- Predictable failure modes

Agent B (LLM-Powered Agent):
- Understands intent through language model
- Calls flight API, checks calendar, compares prices
- Can handle variations ("next week", "in 7 days", "this coming Tuesday")
- BUT: May misinterpret edge cases unpredictably
```

**The Consequence**: Instrumentation of high-level metrics is **critical** for agent observability because:
1. You cannot predict all failure modes
2. Agents inherit behaviors from LLM, tools, and orchestration
3. Production is where real-world complexity emerges

---

## 2. The Evolution to AgentOps

### 2.1 The Ops Progression

Understanding AgentOps requires understanding its predecessors:

```
┌─────────────────────────────────────────────────────────────────┐
│                      THE OPS EVOLUTION                          │
└─────────────────────────────────────────────────────────────────┘

DevOps (2000s)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• Focus: Deterministic software applications
• Key Practices: CI/CD, IaC, monitoring, version control
• Challenge: Scaling software deployment

                    ↓

MLOps (2010s)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• Focus: Machine learning model lifecycle
• Key Distinction: Output is NON-DETERMINISTIC and data-dependent
• Challenge: "Garbage in, garbage out" - data quality is critical
• New Practices: Model versioning, A/B testing, drift detection

                    ↓

FMOps (Foundation Model Ops, 2020s)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• Focus: Pre-trained or fine-tuned foundation models
• Challenge: Managing large models, fine-tuning pipelines

                    ↓

GenAIOps (2023+)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
├── PromptOps: Prompt storage, lineage, optimization
├── RAGOps: Retrieval process (chunking, vectorization, re-ranking)
│             + Generation process (prompt augmentation, grounding)
└── AgentOps: Agent operationalization (tools, orchestration, memory)
```

### 2.2 What Makes AgentOps Unique?

**AgentOps extends RAGOps and PromptOps with**:

| Component | Description | Example |
|-----------|-------------|---------|
| **Tool Management** | Internal/external tool integrations | API connectors, database clients, calculators |
| **Agent Brain Prompt** | Goal, profile, instructions | "You are a travel assistant. Your goal is to..." |
| **Orchestration Layer** | Multi-step reasoning, planning, reflection | ReAct, Plan-and-Solve, Tree-of-Thoughts |
| **Memory Management** | Short-term and long-term memory | Conversation history, user preferences |
| **Task Decomposition** | Breaking complex goals into subtasks | "Book flight" → [search flights, compare prices, select, pay] |

### 2.3 AgentOps Does NOT Replace DevOps/MLOps

**Critical Principle**: AgentOps **builds upon** DevOps and MLOps foundations.

**You still need** (from DevOps/MLOps):
- ✅ API design (authentication, secret management, security, privacy)
- ✅ Exception handling (throttling, quotas, scalability)
- ✅ Version control (code, prompts, agent configurations)
- ✅ CI/CD (automated deployments for agents)
- ✅ Testing (unit, integration, end-to-end tests)
- ✅ Logging (structured logging for debugging)
- ✅ Security (data protection, compliance)

### 2.4 People + Processes + Technology

All "Ops" are about the **harmonious blend**:

```
    People                Processes              Technology
    ──────                ─────────              ──────────
• Team structure       • Workflows            • Tools & platforms
• Expertise           • Best practices        • Infrastructure
• Collaboration       • Feedback loops        • Automation
• Training            • Review cycles         • Monitoring systems
```

**Critical Insight**: Successful AgentOps extends beyond technology. You must consider:
- Customer's operational model
- Existing business units
- Organizational structure
- Integration into business workflows

---

## 3. Defining Agent Success: Metrics That Matter

### 3.1 The North Star Thought Experiment

**Before implementing detailed agent evaluation**, answer this:

> **Imagine an A/B experiment in production**:
> - **Treatment arm**: Users get your new agent
> - **Control arm**: Users do NOT get the agent (baseline experience)
>
> **Questions**:
> 1. What metrics determine if the treatment arm is better?
> 2. What metrics determine ROI for the project?
> 3. Is it goal accomplishment? Sales totals? User journey completion?

**Why this matters**: Without business-level KPIs, you'll optimize for the wrong things.

### 3.2 The Four Tiers of Agent Metrics

```
Tier 1: Business Metrics (North Star)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• Revenue impact ($)
• User engagement (DAU, retention)
• Conversion rates (%)
• Customer satisfaction (NPS, CSAT)

        ↓ (leads to)

Tier 2: Goal-Level Metrics
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• Goal completion rate: % of successfully completed objectives
• Critical task success: Independently measured sub-tasks
• Critical user interactions: Key touchpoints in user journey

        ↓ (measured via)

Tier 3: Application Telemetry
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• Latency: Response time, processing time
• Errors: Error rates, types, frequency
• Attempts vs. Successes: Success rates over time
• Throughput: Requests per second

        ↓ (enhanced by)

Tier 4: Human Feedback
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• 👍👎 thumbs up/down
• User feedback forms
• End-user feedback (consumer systems)
• Employee feedback (internal tools)
• QA tester reviews
• Domain expert reviews
```

### 3.3 Why Human Feedback Matters

**Simple feedback mechanisms provide high signal** for understanding where agents excel and where they need improvement.

**Example Implementation**:

```python
# After agent response in UI
response = agent.execute(user_query)

# Simple feedback collection
feedback_widget = {
    "thumbs_up": "✅ Helpful",
    "thumbs_down": "❌ Not helpful",
    "report_issue": "⚠️ Report problem"
}

# Store feedback with metadata
save_feedback(
    query=user_query,
    response=response,
    user_rating=user_click,  # "thumbs_up" or "thumbs_down"
    timestamp=now(),
    agent_version="v1.2.3"
)

# Aggregate for insights
# - 👍 rate by query type
# - 👎 patterns (what causes dissatisfaction?)
# - Correlate with goal completion rates
```

**Why this works**:
- Low friction (single click)
- High volume (every interaction can be rated)
- Clear signal (users know when agents fail)
- Actionable (correlate 👎 with specific agent behaviors)

---

## 4. Observability & Instrumentation

### 4.1 Two Types of Observability

**Agent observability requires two complementary approaches**:

```
┌───────────────────────────────────────────────────────────────┐
│               HIGH-LEVEL OBSERVABILITY (KPIs)                 │
│  Purpose: Monitor trends, identify macro-level issues         │
├───────────────────────────────────────────────────────────────┤
│  Dashboard Metrics:                                           │
│  • Business metrics (revenue, engagement)                     │
│  • Goal completion rates (% successful tasks)                 │
│  • Critical task success rates (sub-task completion)          │
│  • Application telemetry (latency, errors, throughput)        │
│                                                               │
│  Use Case: "Our agent's goal completion rate dropped 15%     │
│             this week. What changed?"                         │
└───────────────────────────────────────────────────────────────┘

                            ↓ (when KPIs show problems, drill down)

┌───────────────────────────────────────────────────────────────┐
│              DETAILED OBSERVABILITY (TRACES)                  │
│  Purpose: Debug specific issues, understand inner workings    │
├───────────────────────────────────────────────────────────────┤
│  Trace Logging:                                               │
│  • Every internal step logged                                 │
│  • Not just critical tasks - ALL agent actions                │
│  • OpenTelemetry spans for agents and tools                   │
│                                                               │
│  Use Case: "Why did the agent call the wrong API for this    │
│             specific query?"                                  │
│                                                               │
│  Example Trace:                                               │
│    [12:34:56] User query received                             │
│    [12:34:57] Query classifier: "flight_booking"              │
│    [12:34:58] Flight search API called (200 OK, 1.2s)         │
│    [12:35:00] LLM synthesis (500 tokens, 0.8s)                │
│    [12:35:01] Response returned to user                       │
│    Total: 5.0s                                                │
└───────────────────────────────────────────────────────────────┘
```

### 4.2 Key Principle: Metrics vs. Traces

**You rarely measure every internal step as metrics.**

Instead:
1. **Track high-level KPIs in dashboards** (always on, aggregated view)
2. **Use detailed traces for debugging** when KPIs show problems (drill-down analysis)

**Why?**
- High-cardinality metrics (every tool call, every token) are expensive to store/query
- Dashboards become cluttered and unusable
- Traces provide context that metrics cannot (e.g., "What was the exact prompt?")

### 4.3 Instrumentation Example

**Python Implementation**:

```python
from opentelemetry import trace
from datetime import datetime

# High-level KPI tracking
class AgentMetrics:
    def __init__(self):
        self.goals_completed = 0
        self.goals_failed = 0
        self.latencies = []
        self.errors = []

    def record_goal(self, success: bool, latency: float) -> None:
        if success:
            self.goals_completed += 1
        else:
            self.goals_failed += 1
        self.latencies.append(latency)

    def goal_completion_rate(self) -> float:
        total = self.goals_completed + self.goals_failed
        return self.goals_completed / total if total > 0 else 0.0

# Detailed trace logging
tracer = trace.get_tracer(__name__)

def execute_agent(query: str) -> str:
    start_time = datetime.now()

    with tracer.start_as_current_span("agent_execution") as span:
        span.set_attribute("query", query)

        # Step 1: Classify query
        with tracer.start_as_current_span("query_classification"):
            query_type = classify_query(query)
            span.set_attribute("query_type", query_type)

        # Step 2: Execute tools
        with tracer.start_as_current_span("tool_execution"):
            tool_results = execute_tools(query_type)
            span.set_attribute("tools_used", len(tool_results))

        # Step 3: Synthesize response
        with tracer.start_as_current_span("llm_synthesis"):
            response = synthesize_response(query, tool_results)
            span.set_attribute("response_length", len(response))

        # Record high-level metric
        latency = (datetime.now() - start_time).total_seconds()
        metrics.record_goal(success=True, latency=latency)

        return response
```

**Result**:
- **Dashboard** shows: "Goal completion rate: 87%, avg latency: 3.2s"
- **Trace** shows: Detailed steps for specific failed queries

---

## 5. The Three Pillars of Agent Evaluation

**Agent evaluation requires a deeper understanding than evaluating generative models alone.**

```
┌─────────────────────────────────────────────────────────────────┐
│                  AGENT EVALUATION FRAMEWORK                     │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   Pillar 1: Assessing Agent Capabilities                        │
│   ─────────────────────────────────────────                    │
│   • Public benchmarks (BFCL, τ-bench, PlanBench, AgentBench)   │
│   • Core abilities: tool calling, planning, reasoning           │
│   • Baseline capability assessment                              │
│   • Inherited behaviors from LLM + tools + orchestration        │
│                                                                 │
│                        ↓                                        │
│                                                                 │
│   Pillar 2: Evaluating Trajectory and Tool Use                  │
│   ───────────────────────────────────────────                  │
│   • The STEPS taken to reach the goal                           │
│   • Tool selection and invocation correctness                   │
│   • Trajectory metrics: exact match, in-order match, precision  │
│   • Efficiency: number of steps, redundant actions              │
│                                                                 │
│                        ↓                                        │
│                                                                 │
│   Pillar 3: Evaluating the Final Response                       │
│   ──────────────────────────────────────────                   │
│   • Output quality: accuracy, relevance, completeness           │
│   • Autoraters (LLM-as-Judge) for subjective criteria           │
│   • Human evaluation for high-stakes tasks                      │
│   • Traditional NLG metrics (BLEU, ROUGE, semantic similarity)  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 5.1 Why Three Pillars?

**Analogy: Evaluating a Chef**

| Aspect | Chef | AI Agent |
|--------|------|----------|
| **Capabilities** | Knife skills, recipe knowledge, kitchen experience | LLM reasoning, tool availability, planning ability |
| **Process** | Cooking technique, ingredient selection, timing | Trajectory: tools called, sequence of actions |
| **Final Dish** | Taste, presentation, satisfaction | Response quality, accuracy, user satisfaction |

**You wouldn't evaluate a chef only on the final dish** - you also care about:
- Can they use kitchen tools correctly? (capabilities)
- Did they follow food safety protocols? (process/trajectory)
- Does the dish taste good? (final output)

**Same for agents**: All three pillars are necessary for comprehensive evaluation.

### 5.2 Inherited Behaviors

**Agents inherit behaviors from all components**:

```
┌─────────────────────────────────────────────────────────────────┐
│                    AGENT BEHAVIOR SOURCES                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  LLM Capabilities                                               │
│  ├── Reasoning ability (chain-of-thought, planning)             │
│  ├── Language understanding (query interpretation)              │
│  ├── World knowledge (factual accuracy)                         │
│  └── Instruction following (prompt adherence)                   │
│                                                                 │
│  Tool Integrations                                              │
│  ├── API reliability (uptime, error rates)                      │
│  ├── Data quality (accuracy of retrieved information)           │
│  ├── Latency (response time of external services)              │
│  └── Authorization (access control, permissions)                │
│                                                                 │
│  Orchestration Logic                                            │
│  ├── Prompt engineering (agent brain prompt design)             │
│  ├── Flow control (how steps are sequenced)                     │
│  ├── Error handling (retries, fallbacks)                        │
│  └── Memory management (context retention)                      │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

**Consequence**: You cannot evaluate agents in isolation. You must:
1. Understand which component caused a failure
2. Test each component independently when possible
3. Use end-to-end evaluation for real-world validation

---

## 6. Public Benchmarks: Starting Point for Capability Assessment

### 6.1 Why Start with Public Benchmarks?

**Before evaluating your specific use case**, leverage public benchmarks to:
1. Understand what's possible with current LLMs
2. Identify common pitfalls and failure modes
3. Establish baseline capability assessment
4. Compare different LLMs for your agent

### 6.2 Benchmark Categories

#### Tool Calling Benchmarks

| Benchmark | Purpose | What It Measures | Use Case |
|-----------|---------|------------------|----------|
| **BFCL** (Berkeley Function-Calling Leaderboard) | Tool selection and invocation | Ability to select appropriate tools, correct argument passing | Choosing LLM for multi-tool agents |
| **τ-bench** (Tau-bench) | Tool calling across diverse scenarios | Failure modes in tool invocation | Understanding edge cases |

**Example**: Your agent needs to call a `book_flight(origin, destination, date)` API. BFCL tells you if Claude 3.5 Sonnet is better than GPT-4 at:
- Selecting the right tool
- Passing correct arguments
- Handling ambiguous inputs

#### Planning & Reasoning Benchmarks

| Benchmark | Purpose | What It Measures |
|-----------|---------|------------------|
| **PlanBench** | Planning and reasoning across domains | Decomposition, sequencing, constraint handling |

**Example**: Your agent needs to "Plan a 3-day trip to Paris under $2000 budget". PlanBench tells you if your LLM can:
- Decompose the goal into subtasks (flights, hotels, activities)
- Sequence actions correctly (book flights before hotels)
- Handle constraints (stay within budget)

#### Holistic Agent Benchmarks

| Benchmark | Purpose | Limitation |
|-----------|---------|------------|
| **AgentBench** | End-to-end performance across multiple scenarios | May test capabilities your agent doesn't implement |

**When to use**: If your agent is a general-purpose assistant. Less useful for specialized agents (e.g., SQL query agent).

#### Specialized Domain Benchmarks

| Benchmark | Domain | Use Case |
|-----------|--------|----------|
| **DBAStep** (Adyen Data Analyst Leaderboard) | Data analysis | Evaluating SQL generation agents |

**When to use**: If your domain aligns with the benchmark's focus.

### 6.3 Public Benchmark Limitations

**Valuable for**:
- ✅ Understanding what's possible
- ✅ Identifying common pitfalls
- ✅ Baseline capability assessment
- ✅ LLM comparison for agent selection

**NOT sufficient for**:
- ❌ Production use-case validation
- ❌ Domain-specific evaluation
- ❌ Real-world performance prediction
- ❌ Business metric optimization

**Action**: Use public benchmarks as **starting point**, then build **use-case-specific evaluation**.

---

## 7. Metrics-Driven Development for Agents

### 7.1 The A/B Experimentation Mindset

**Process**:

```
Step 1: Define Success Metrics
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• Business metrics (revenue, engagement)
• Agent-specific metrics (goal completion, tool accuracy)
• User satisfaction (NPS, 👍👎 rate)

            ↓

Step 2: Deploy Treatment vs. Control
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• Control: Baseline (existing solution or no agent)
• Treatment: New agent (your implementation)
• Split: 50/50 or 90/10 (safer for unproven agents)

            ↓

Step 3: Measure & Compare
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• Goal completion rates (treatment vs. control)
• Critical task success (sub-task completion)
• User engagement (session length, return rate)
• Business outcomes (sales, conversions)

            ↓

Step 4: Iterate Based on Data
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• If treatment wins: Roll out to 100%
• If treatment loses: Analyze traces, identify issues, fix, re-test
• If unclear: Extend experiment duration, increase sample size
```

### 7.2 Continuous Improvement Loop

```
1. Instrument Metrics
   ├── Add logging for KPIs
   ├── Set up dashboards
   └── Enable trace collection
        ↓
2. Collect Data (Production + Testing)
   ├── Production traffic (real users)
   ├── Synthetic testing (automated evaluation)
   └── Human evaluations (QA, domain experts)
        ↓
3. Analyze Results (Dashboards + Traces)
   ├── Identify trends (goal completion over time)
   ├── Detect anomalies (sudden drop in success rate)
   └── Drill down into failures (trace analysis)
        ↓
4. Identify Improvements (Manual + Automated Evaluation)
   ├── What queries are failing? (trajectory analysis)
   ├── Are responses high quality? (autorater evaluation)
   └── What do users dislike? (👎 feedback analysis)
        ↓
5. Deploy Changes (A/B Testing)
   ├── Update prompts, tools, or orchestration
   ├── Test treatment vs. control
   └── Measure impact on metrics
        ↓
   (Repeat continuously)
```

**Key Insight**: This is a **never-ending loop**. Agent performance degrades over time due to:
- Data drift (user queries change)
- API changes (tools break)
- Model updates (LLM behavior shifts)

**Continuous monitoring and iteration are essential.**

---

## 8. Production Readiness Framework

### 8.1 The Checklist

**Before deploying agents to production**, ensure you have:

#### Business Metrics ✅
- [ ] North star metric defined (revenue, engagement, etc.)
- [ ] Goal completion tracking instrumented
- [ ] Critical tasks identified and measured
- [ ] ROI measurement plan in place

#### Agent Metrics ✅
- [ ] Latency tracking for all agent components
- [ ] Error logging with categorization
- [ ] Success/failure rates tracked
- [ ] Human feedback mechanisms (👍👎, forms)

#### Observability ✅
- [ ] Dashboard for high-level KPIs
- [ ] Trace logging for all agent actions
- [ ] Alerts for critical failures
- [ ] Manual testing plan for edge cases

#### Infrastructure ✅
- [ ] DevOps/MLOps foundations in place
- [ ] API security (authentication, throttling, quotas)
- [ ] CI/CD for agent deployments
- [ ] Version control for prompts and agent configs

#### Automated Evaluation ✅
- [ ] Trajectory evaluation setup (covered in next tutorial)
- [ ] Final response evaluation setup (covered in Tutorial 4.3)
- [ ] Human-in-the-loop validation process (covered in Tutorial 4.4)

### 8.2 Risk Mitigation Strategies

**For high-stakes applications** (financial transactions, medical advice, legal assistance):

| Risk | Mitigation Strategy |
|------|---------------------|
| **Agent makes incorrect decision** | Human-in-the-loop approval for critical actions |
| **Tool invocation fails** | Retries with exponential backoff, fallback to simpler tools |
| **Response is harmful** | Content filtering, safety classifiers before output |
| **Latency exceeds SLA** | Timeout thresholds, fast-path for simple queries |
| **Data leakage** | Prompt injection detection, input sanitization |

---

## 9. Practical Exercises

### Exercise 1: Define Your North Star Metric

**Task**: Imagine you're building an AI agent for customer support at an e-commerce company.

**Questions**:
1. What is your north star business metric?
2. What goal-level metrics would you track?
3. What application telemetry would you instrument?
4. How would you collect human feedback?

<details>
<summary>Click to see example answers</summary>

**North Star Metric**: **Customer Satisfaction (CSAT)** - % of customers rating support interaction as "Satisfied" or "Very Satisfied"

**Goal-Level Metrics**:
- Issue resolution rate (% of tickets resolved without human escalation)
- First-contact resolution (% resolved in single interaction)
- Time to resolution (minutes from query to resolution)

**Application Telemetry**:
- Latency (time to first response, total interaction time)
- Error rate (API failures, tool invocation errors)
- Escalation rate (% of conversations escalated to human)

**Human Feedback**:
- Post-interaction survey: "Was your issue resolved?" (Yes/No)
- 👍👎 after each agent response
- Optional free-text feedback for 👎 ratings

</details>

---

### Exercise 2: Design an Observability Architecture

**Task**: You're building a travel booking agent. Design a two-tier observability system.

**Requirements**:
1. High-level KPIs for a dashboard (what would you monitor daily?)
2. Detailed traces (what information would you log for debugging?)
3. When would you drill down from KPIs to traces?

<details>
<summary>Click to see example answers</summary>

**High-Level KPIs (Dashboard)**:
- Booking completion rate (% of queries resulting in successful bookings)
- Average booking latency (time from query to confirmation)
- Booking error rate (% of failed bookings)
- User satisfaction (👍👎 ratio, post-booking survey CSAT)
- Revenue per session (total booking value / number of sessions)

**Detailed Traces (Logging)**:
- User query (sanitized for PII)
- Query classification ("flight_search", "hotel_booking", "itinerary_planning")
- Tools called (APIs invoked, arguments passed)
- Tool responses (status codes, data returned)
- LLM prompts and completions (full context)
- Latency breakdown (per tool, per LLM call)
- Final response to user

**When to Drill Down**:
- **Scenario 1**: Dashboard shows booking error rate increased from 5% to 15% overnight
  - **Action**: Filter traces by error status, identify common failure pattern (e.g., flight API returning 500 errors)
- **Scenario 2**: User reports "Agent booked wrong dates"
  - **Action**: Pull trace for that session, examine query parsing and tool arguments
- **Scenario 3**: Latency spiked above 10 seconds
  - **Action**: Analyze trace timing breakdown, identify slow component (e.g., hotel search API)

</details>

---

### Exercise 3: Public Benchmark Selection

**Task**: You're building the following agents. For each, identify which public benchmark(s) would be most useful for initial capability assessment.

**Agents**:
1. SQL query generation agent (converts natural language to SQL)
2. Multi-step research assistant (searches web, synthesizes information)
3. Customer service chatbot (handles FAQs, routes to human agents)

<details>
<summary>Click to see example answers</summary>

1. **SQL query generation agent**:
   - **Primary**: DBAStep (Adyen Data Analyst Leaderboard) - directly evaluates SQL generation
   - **Secondary**: PlanBench - for multi-table query planning

2. **Multi-step research assistant**:
   - **Primary**: AgentBench - end-to-end evaluation of research tasks
   - **Secondary**: BFCL - for tool calling (web search API, database lookup)
   - **Tertiary**: PlanBench - for decomposing research questions into subtasks

3. **Customer service chatbot**:
   - **Primary**: τ-bench - tool calling for ticket systems, knowledge bases
   - **Secondary**: Traditional conversational AI metrics (turn-level success, CSAT)
   - **Note**: Public benchmarks less useful here - build domain-specific evaluation with real customer queries

</details>

---

## 10. Key Takeaways

### Core Principles

1. **AgentOps builds on DevOps/MLOps** - Don't skip the foundations (CI/CD, security, version control)

2. **Business metrics are your north star** - Start with ROI, not just agent metrics (revenue > goal completion > tool accuracy)

3. **Instrumentation is critical** - High-level KPIs (dashboards) + detailed traces (debugging)

4. **Human feedback matters** - Simple 👍👎 provides high signal for identifying failures

5. **Metrics-driven development** - A/B test everything, iterate based on data (continuous improvement loop)

6. **People + Processes + Technology** - Success requires all three (not just better prompts)

7. **Non-determinism is the challenge** - Agents are harder to validate than traditional software (cannot enumerate all edge cases)

### The Three Pillars of Agent Evaluation

| Pillar | Focus | Methods |
|--------|-------|---------|
| **1. Capabilities** | What the agent CAN do | Public benchmarks, inherited behaviors assessment |
| **2. Trajectory** | What the agent DOES (steps taken) | Trajectory metrics, tool invocation correctness |
| **3. Final Response** | What the agent PRODUCES (output quality) | Autoraters, human evaluation, NLG metrics |

### Next Steps

- **Tutorial 4.2**: Trajectory Evaluation Techniques (6 metrics for evaluating agent steps)
- **Tutorial 4.3**: Autorater & Final Response Evaluation (LLM-as-Judge for output quality)
- **Tutorial 4.4**: Human-in-the-Loop Evaluation (when and how to involve humans)

---

## References

**Source Material**:
- Google's "Agents Companion" Whitepaper (February 2025)
- Topic 01: AgentOps & Operations (pages 9-13, lines 47-96)
- Topic 02: Agent Evaluation Methodology (pages 13-20, lines 96-181)

**Additional Reading**:
- Sokratis Kartakis, 2024. "GenAI in Production: MLOps or GenAIOps?"
- Sokratis Kartakis, 2024. "GenAIOps, Operationalize Generative AI, A Practical Guide"
- Berkeley Function-Calling Leaderboard: https://gorilla.cs.berkeley.edu/blogs/8_berkeley_function_calling_leaderboard.html
- Karthik Narasimhan et al., 2024. "τ-bench: Tool Calling Evaluation"
- Karthik Valmeekam et al., 2023. "PlanBench: Planning and Reasoning Benchmark"
- Xiao Liu et al., 2023. "AgentBench: Holistic Agent Evaluation"
- Martin Iglesias et al., 2025. "DBAStep: Adyen Data Analyst Leaderboard"

---

**Tutorial Version:** 1.0
**Last Updated:** 2025-11-14
**Part of:** Lesson 14 - Agent Planning & Orchestration (Group A)
