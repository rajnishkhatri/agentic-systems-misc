# AgentOps & Operations

**Source:** Google's "Agents Companion" Whitepaper (February 2025)
**Topic Complexity:** ⭐⭐⭐⭐
**Lines:** 47-96 from original document

---

## Overview

AgentOps is a subcategory of GenAIOps focused on the efficient operationalization of AI agents from proof-of-concept to production. It extends MLOps and DevOps practices with agent-specific capabilities.

---

## The Ops Evolution

### DevOps → MLOps → AgentOps Progression

```
DevOps (Deterministic Software)
    ↓
MLOps (Non-deterministic ML Models)
    ↓
FMOps (Foundation Models)
    ↓
GenAIOps
    ├── PromptOps (Prompt management)
    ├── RAGOps (Retrieval-augmented generation)
    └── AgentOps (Agent operationalization)
```

### Key Definitions

**DevOps**: Practice of efficiently productionizing deterministic software applications through integration of people, processes, and technology.

**MLOps**: Builds on DevOps, focuses on ML model productionization. Key distinction: output is non-deterministic and data-dependent ("garbage in, garbage out").

**FMOps**: Expands MLOps for pre-trained or fine-tuned foundation models.

**PromptOps**: Operationalizing prompts with capabilities for:
- Prompt storage and lineage
- Metadata management (evaluation scores)
- Centralized template registry
- Prompt optimization

**RAGOps**: Efficient operationalization of RAG solutions with:
- **Retrieval process**: Data cleaning, chunking, vectorization, similarity search, re-ranking
- **Generation process**: Prompt augmentation and grounding

**AgentOps**: Efficient operationalization of agents with additional components:
- Internal/external tool management
- Agent brain prompt (goal, profile, instructions)
- Orchestration layer
- Memory management
- Task decomposition

---

## Core AgentOps Principles

### 1. Foundation Dependencies

**AgentOps does NOT replace DevOps/MLOps** - it builds upon them:

- **API Design**: Authentication, secret management, security, privacy
- **Exception Handling**: Throttling, quotas, scalability
- **Version Control**: Code, prompts, and agent configurations
- **CI/CD**: Automated deployments for agents
- **Testing**: Unit, integration, and end-to-end tests
- **Logging**: Structured logging for debugging
- **Security**: Data protection and compliance

### 2. People, Processes, Technology

All "Ops" are about the **harmonious blend** of:
- **People**: Team structure, expertise, collaboration
- **Processes**: Workflows, best practices, feedback loops
- **Technology**: Tools, platforms, infrastructure

**Critical Insight**: Successful Ops extends beyond technology. Must consider:
- Customer's operational model
- Existing business units
- Organizational structure
- Integration into business workflows

---

## Agent Success Metrics

### North Star Metrics

Before implementing detailed agent evaluation, define **business-level KPIs**:

**Thought Experiment**: Set up an A/B experiment in production:
- **Treatment arm**: Gets your new agent
- **Control arm**: Does not

**Questions to answer**:
1. What metrics determine if treatment arm is better?
2. What metrics determine ROI for the project?
3. Is it goal accomplishment, sales totals, or critical user journey steps?

### Metric Categories

#### 1. Business Metrics (North Star)
- Revenue impact
- User engagement
- Conversion rates
- Customer satisfaction (NPS, CSAT)

#### 2. Goal-Level Metrics
- **Goal completion rate**: % of successfully completed objectives
- **Critical task success**: Independently measured sub-tasks
- **Critical user interactions**: Key touchpoints in user journey

#### 3. Application Telemetry (Standard Software Metrics)
- **Latency**: Response time, processing time
- **Errors**: Error rates, types, frequency
- **Attempts vs. Successes**: Success rates over time
- **Throughput**: Requests per second

#### 4. Human Feedback
- 👍👎 thumbs up/down
- User feedback forms
- End-user feedback (consumer systems)
- Employee feedback (internal tools)
- QA tester reviews
- Domain expert reviews

**Why human feedback matters**: Simple feedback mechanisms provide high signal for understanding where agents excel and where they need improvement.

---

## Observability & Instrumentation

### High-Level Observability (KPIs)

**Dashboard Metrics**: Aggregate view of agent performance
- Business metrics
- Goal completion rates
- Critical task success rates
- Application telemetry

**Use Case**: Monitor trends, identify macro-level issues, track ROI

### Detailed Observability (Traces)

**Trace Logging**: Capture all inner workings of the agent
- Every internal step logged
- Not just critical tasks and user interactions
- OpenTelemetry spans for agents and tools

**Use Case**: Debug specific issues when metrics or manual testing show problems

**Example**: Cloud Observability trace diagram showing:
- Agent orchestration steps
- Tool invocations
- LLM API calls
- Timing for each component

**Key Principle**: You rarely measure every internal step as metrics. Instead:
1. Track high-level KPIs in dashboards
2. Use detailed traces for debugging when KPIs show problems

---

## AgentOps vs. Traditional Software Ops

### Why AgentOps is More Important for Agents

**Deterministic Code**:
- Does only what you tell it to do
- Predictable behavior
- Easier to validate

**AI Agents**:
- Can do much more (LLMs trained on huge data)
- Non-deterministic behavior
- Harder to predict edge cases

**Consequence**: Instrumentation of high-level metrics is **critical** for agent observability.

---

## Metrics-Driven Development

### A/B Experimentation for Agents

**Process**:
1. Define success metrics (business + agent-specific)
2. Deploy treatment (new agent) vs. control (baseline)
3. Measure:
   - Goal completion rates
   - Critical task success
   - User engagement
   - Business outcomes
4. Iterate based on data

### Continuous Improvement Loop

```
1. Instrument Metrics
    ↓
2. Collect Data (Production + Testing)
    ↓
3. Analyze Results (Dashboards + Traces)
    ↓
4. Identify Improvements (Manual + Automated Evaluation)
    ↓
5. Deploy Changes (A/B Testing)
    ↓
(Repeat)
```

---

## Production Readiness Checklist

### Before Deploying Agents to Production

#### Business Metrics
- [ ] North star metric defined (revenue, engagement, etc.)
- [ ] Goal completion tracking instrumented
- [ ] Critical tasks identified and measured
- [ ] ROI measurement plan in place

#### Agent Metrics
- [ ] Latency tracking for all agent components
- [ ] Error logging with categorization
- [ ] Success/failure rates tracked
- [ ] Human feedback mechanisms (👍👎, forms)

#### Observability
- [ ] Dashboard for high-level KPIs
- [ ] Trace logging for all agent actions
- [ ] Alerts for critical failures
- [ ] Manual testing plan for edge cases

#### Infrastructure
- [ ] DevOps/MLOps foundations in place
- [ ] API security (authentication, throttling, quotas)
- [ ] CI/CD for agent deployments
- [ ] Version control for prompts and agent configs

#### Automated Evaluation (See Topic 2)
- [ ] Trajectory evaluation setup
- [ ] Final response evaluation setup
- [ ] Human-in-the-loop validation process

---

## Key Takeaways

1. **AgentOps builds on DevOps/MLOps** - Don't skip the foundations
2. **Business metrics are your north star** - Start with ROI, not just agent metrics
3. **Instrumentation is critical** - High-level KPIs + detailed traces
4. **Human feedback matters** - Simple 👍👎 provides high signal
5. **Metrics-driven development** - A/B test everything, iterate based on data
6. **People + Processes + Technology** - Success requires all three
7. **Non-determinism is the challenge** - Agents are harder to validate than traditional software

---

## Related Topics

- **Topic 2**: Agent Evaluation Methodology (trajectory, response, capabilities)
- **Topic 3**: Multi-Agent Architectures (evaluation complexity increases)
- **Topic 6**: Contract-Based Agents (formal specifications for high-stakes tasks)
- **Topic 9**: Vertex AI Ecosystem (Google's AgentOps tooling)

---

## References

- Figure 1: Relationship between DevOps, MLOps, and AgentOps (page 9)
- Figure 2: Ops as blend of people, processes, technology (page 11)
- Figure 3: Cloud Observability trace example (page 13)
- Sokratis Kartakis, 2024. "GenAI in Production: MLOps or GenAIOps?"
- Sokratis Kartakis, 2024. "GenAIOps, Operationalize Generative AI, A Practical Guide"

---

**Next Topic**: [Agent Evaluation Methodology](02_Agent_Evaluation_Methodology.md)
