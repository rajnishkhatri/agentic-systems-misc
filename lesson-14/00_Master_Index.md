# Agents Companion - Master Topic Index

**Source:** Google's "Agents Companion" Whitepaper (February 2025)
**Authors:** Antonio Gulli, Lavi Nigam, Julia Wiesinger, Vladimir Vuskovic, Irina Sigler, Ivan Nardini, Nicolas Stroppa, Sokratis Kartakis, Narek Saribekyan, Anant Nawalgaria, Alan Bount

**Date Extracted:** 2025-11-14
**Original Document**: 76 pages, 776 lines

---

## Purpose

This index provides structured access to all topics from Google's "Agents Companion" whitepaper, organized into 8 focused documents for easier navigation and learning.

---

## Document Overview

### Classification Analysis
[AgentCompanion_Summary_Analysis.md](AgentCompanion_Summary_Analysis.md) - Comprehensive topic classification with complexity ratings and learning paths

### Original Source
[lesson-14/AgentCompanion.txt](lesson-14/AgentCompanion.txt) - Full 76-page whitepaper (plain text)

---

## Topic Files

### [01: AgentOps & Operations](01_AgentOps_Operations.md)
**Complexity:** ⭐⭐⭐⭐ | **Reading Time:** 20-25 min

**Key Concepts:**
- DevOps → MLOps → FMOps → AgentOps evolution
- Agent Success Metrics (business KPIs, goal completion, telemetry)
- Observability (high-level KPIs + detailed traces)
- Metrics-driven development and A/B testing

**When to Read:**
- First topic for understanding agent operationalization
- Before deploying agents to production
- When setting up monitoring and evaluation infrastructure

**Related Topics:** All topics (foundational)

---

### [02: Agent Evaluation Methodology](02_Agent_Evaluation_Methodology.md)
**Complexity:** ⭐⭐⭐⭐⭐ | **Reading Time:** 30-40 min

**Key Concepts:**
- Assessing Agent Capabilities (benchmarks: BFCL, τ-bench, PlanBench, AgentBench)
- Trajectory Evaluation (6 metrics: exact match, in-order, any-order, precision, recall, single-tool)
- Final Response Evaluation (autoraters, LLM-as-a-Judge)
- Human-in-the-Loop Evaluation (direct assessment, comparative, user studies)

**When to Read:**
- After understanding AgentOps (Topic 1)
- Before implementing automated evaluation
- When designing agent testing strategies

**Related Topics:** Topic 1 (metrics), Topic 3 (multi-agent eval), Topic 7 (case studies)

---

### [03: Multi-Agent Architectures](03_Multi_Agent_Architectures.md)
**Complexity:** ⭐⭐⭐⭐⭐ | **Reading Time:** 35-45 min

**Key Concepts:**
- Agent Types (Planner, Retriever, Execution, Evaluator)
- Design Patterns (Sequential, Hierarchical, Collaborative, Competitive)
- 9 Core Components (memory, cognition, tools, routing, communication, registry)
- 6 Challenges (task communication, allocation, coordination, context, cost, complexity)
- Multi-Agent Evaluation (cooperation, planning, utilization, scalability)

**When to Read:**
- After single-agent basics (Topic 1-2)
- Before designing complex multi-agent systems
- When scaling from single to multiple agents

**Related Topics:** Topic 2 (evaluation), Topic 6 (contracts), Topic 7 (case studies)

---

### [04: Agentic RAG](04_Agentic_RAG.md)
**Complexity:** ⭐⭐⭐⭐ | **Reading Time:** 25-35 min

**Key Concepts:**
- Traditional RAG vs. Agentic RAG (static vs. iterative)
- 4 Innovations (query expansion, multi-step reasoning, adaptive sources, validation)
- Search Optimization (6 techniques: chunking, metadata, embeddings, vector DB, rankers, grounding)
- Google Tools (Vertex AI Search, RAG Engine, Search Builder APIs)

**When to Read:**
- After understanding agents basics (Topic 1)
- Before implementing RAG systems
- When optimizing existing RAG performance

**Related Topics:** Topic 1 (observability), Topic 2 (eval), Topic 3 (retriever agents), Topic 5 (Agentspace)

---

### [05: Enterprise Applications](05_Enterprise_Applications.md)
**Complexity:** ⭐⭐⭐ | **Reading Time:** 25-30 min

**Key Concepts:**
- Agent Types (Assistants vs. Automation Agents)
- Knowledge Workers as Agent Fleet Managers
- Google Agentspace (enterprise search, custom agents, workflow automation)
- NotebookLM Enterprise (research synthesis, AI audio summaries)
- Security (RBAC, VPC, IAM, SSO)

**When to Read:**
- After understanding agent basics (Topic 1-2)
- Before deploying enterprise agents
- When evaluating Google Cloud agent platforms

**Related Topics:** Topic 1 (AgentOps), Topic 3 (multi-agent), Topic 4 (RAG), Topic 8 (Vertex AI)

---

### [06: Contract-Based Agents](06_Contract_Based_Agents.md)
**Complexity:** ⭐⭐⭐⭐⭐ | **Reading Time:** 30-40 min

**Key Concepts:**
- Problem with Simple Agent Interface (underspecification)
- Contract Components (task, deliverables, scope, cost, duration, reporting)
- Contract Lifecycle (negotiation → execution → feedback)
- Execution Strategy (generate multiple solutions, validate, iterate)
- Subcontracts (task decomposition with uniform processing)
- Cost Negotiation (relative priority, resource allocation)

**When to Read:**
- After multi-agent architectures (Topic 3)
- Before tackling high-stakes, complex tasks
- When agents need formal specifications

**Related Topics:** Topic 2 (evaluation of contracts), Topic 3 (multi-agent coordination), Topic 5 (enterprise)

---

### [07: Case Studies](07_Case_Studies.md)
**Complexity:** ⭐⭐⭐⭐ | **Reading Time:** 25-30 min

**Key Concepts:**
- **Google Co-Scientist** (generate-debate-evolve approach, liver fibrosis study)
- **Automotive AI** (5 specialized agents, 5 coordination patterns)
  - Agents: Navigation, Media, Message, Car Manual, General Knowledge
  - Patterns: Hierarchical, Diamond, Peer-to-Peer, Collaborative, Adaptive Loop
- Hybrid Deployment (on-device + cloud)
- Response Moderation (Rephraser Agent)

**When to Read:**
- After understanding patterns (Topic 3)
- When designing real-world multi-agent systems
- For concrete examples of theory in practice

**Related Topics:** Topic 2 (evaluation examples), Topic 3 (patterns in action), Topic 1 (production monitoring)

---

### [08: Vertex AI Ecosystem](08_Vertex_AI_Ecosystem.md)
**Complexity:** ⭐⭐⭐ | **Reading Time:** 15-20 min

**Key Concepts:**
- Vertex AI Agent Builder (no-code to full-code)
- Vertex AI Agent Engine (managed runtime, session, trace, eval)
- Vertex AI Eval Service (LLM/RAG/Agent evaluation at scale)
- Tool Portfolio (Search, Databases, API Integrations, Apigee)
- Gemini Family (multimodal, long-context, function calling)
- Security & Compliance (VPC, IAM, SOC 2, HIPAA, GDPR)

**When to Read:**
- After understanding agent development (Topic 1-3)
- Before choosing agent infrastructure
- When implementing with Google Cloud

**Related Topics:** Topic 1 (AgentOps tooling), Topic 2 (Eval Service), Topic 4 (RAG tools), Topic 5 (Agentspace)

---

## Learning Paths

### Path 1: Foundations → Advanced (Linear)
**Duration:** 8-10 hours (deep study)

```
01 AgentOps → 02 Evaluation → 03 Multi-Agent → 04 Agentic RAG
    ↓
05 Enterprise → 06 Contracts → 07 Case Studies → 08 Vertex AI
```

**Best For:** Comprehensive understanding, building production agents

---

### Path 2: Practical Implementation (Hands-On)
**Duration:** 4-6 hours (focused study)

```
01 AgentOps → 02 Evaluation → 08 Vertex AI
    ↓
04 Agentic RAG (if building RAG systems)
OR
03 Multi-Agent (if building multi-agent systems)
    ↓
07 Case Studies (real-world examples)
```

**Best For:** Developers starting with Google Cloud, practical implementation

---

### Path 3: Executive Overview (High-Level)
**Duration:** 2-3 hours (strategic understanding)

```
01 AgentOps (Intro + Key Metrics)
    ↓
05 Enterprise Applications (business value)
    ↓
07 Case Studies (automotive AI, co-scientist)
    ↓
06 Contracts (high-stakes agents)
```

**Best For:** Decision-makers, architects, non-technical stakeholders

---

### Path 4: Evaluation Specialist (Deep Dive)
**Duration:** 3-4 hours (evaluation focus)

```
02 Evaluation Methodology (core techniques)
    ↓
01 AgentOps (metrics & observability)
    ↓
03 Multi-Agent (evaluation complexity)
    ↓
08 Vertex AI (Eval Service tooling)
```

**Best For:** QA engineers, ML engineers focused on evaluation

---

### Path 5: Multi-Agent Systems (Architecture Focus)
**Duration:** 4-5 hours (architecture deep dive)

```
03 Multi-Agent Architectures (patterns & components)
    ↓
07 Case Studies (automotive AI patterns)
    ↓
06 Contract-Based Agents (task coordination)
    ↓
01 AgentOps + 02 Evaluation (monitoring & testing)
```

**Best For:** System architects, multi-agent system designers

---

## Quick Reference Tables

### Complexity Ratings

| Topic | Complexity | Prerequisites | Reading Time |
|-------|-----------|---------------|--------------|
| 01: AgentOps | ⭐⭐⭐⭐ | None | 20-25 min |
| 02: Evaluation | ⭐⭐⭐⭐⭐ | Topic 1 | 30-40 min |
| 03: Multi-Agent | ⭐⭐⭐⭐⭐ | Topics 1-2 | 35-45 min |
| 04: Agentic RAG | ⭐⭐⭐⭐ | Topic 1 | 25-35 min |
| 05: Enterprise | ⭐⭐⭐ | Topics 1-2 | 25-30 min |
| 06: Contracts | ⭐⭐⭐⭐⭐ | Topics 1-3 | 30-40 min |
| 07: Case Studies | ⭐⭐⭐⭐ | Topics 2-3 | 25-30 min |
| 08: Vertex AI | ⭐⭐⭐ | Topics 1-2 | 15-20 min |

---

### Topic Dependencies

```
           01 AgentOps (Foundational)
                 ↓
        ┌────────┴────────┐
        ↓                 ↓
    02 Evaluation    04 Agentic RAG
        ↓                 ↓
    03 Multi-Agent    05 Enterprise
        ↓                 ↓
    06 Contracts      08 Vertex AI
        ↓
    07 Case Studies
```

---

### Use Case → Topic Mapping

| Use Case | Recommended Topics (Priority Order) |
|----------|-------------------------------------|
| **Building first agent** | 01 → 08 → 02 → 04 or 03 |
| **Optimizing RAG system** | 04 → 01 → 02 → 08 |
| **Multi-agent system** | 03 → 07 → 06 → 01 → 02 |
| **Enterprise deployment** | 05 → 01 → 08 → 02 |
| **High-stakes agents** | 06 → 02 → 01 → 05 |
| **Agent evaluation** | 02 → 01 → 08 → 03 |
| **Google Cloud implementation** | 08 → 01 → 02 → 04 or 05 |

---

## Key Takeaways by Topic

### 01: AgentOps
- Business metrics are your north star
- High-level KPIs + detailed traces for observability
- A/B testing drives improvement

### 02: Evaluation
- Three components: Capabilities, Trajectory, Response
- Trajectory: 6 metrics (exact match, precision, recall, etc.)
- Human-in-the-loop validates automation

### 03: Multi-Agent
- Specialization improves quality, efficiency, scalability
- Four patterns: Sequential, Hierarchical, Collaborative, Competitive
- Nine core components (memory, tools, routing, registry, etc.)

### 04: Agentic RAG
- Four innovations: query expansion, multi-step reasoning, adaptive sources, validation
- Optimize search BEFORE adding agents (6 techniques)
- Use Vertex AI Search for turnkey solution

### 05: Enterprise
- Two agent types: Assistants (interactive) + Automation (background)
- Knowledge workers become agent fleet managers
- Agentspace provides unified search + custom agents

### 06: Contracts
- Formal specifications prevent underspecification failures
- Lifecycle: Negotiation → Execution (with validation) → Feedback
- Subcontracts decompose complex tasks with uniform processing

### 07: Case Studies
- Co-Scientist: Generate-debate-evolve for scientific research
- Automotive AI: 5 agents × 5 patterns in production
- On-device + cloud hybrid ensures resilience

### 08: Vertex AI
- Agent Engine: Managed runtime with session, trace, eval services
- Eval Service: Production-grade evaluation at scale
- Gemini: Multimodal, long-context, native function calling

---

## Additional Resources

### Academic Papers
- ReAct (Shafran et al., 2022) - Reasoning + Acting
- Chain-of-Thought (Wei et al., 2023) - Step-by-step reasoning
- Tree of Thoughts (Yao et al., 2023) - Deliberate problem solving
- AgentBench (Liu et al., 2023) - Holistic agent evaluation
- Agent-as-a-Judge (Zhuge et al., 2024) - Automated trajectory evaluation

### Google Products
- [Vertex AI Agent Builder](https://cloud.google.com/vertex-ai)
- [Google Agentspace](https://cloud.google.com/agentspace)
- [NotebookLM Enterprise](https://cloud.google.com/agentspace/notebooklm-enterprise)
- [Vertex AI Search](https://cloud.google.com/enterprise-search)
- [Vertex AI Eval Service](https://cloud.google.com/vertex-ai/generative-ai/docs/models/evaluation-agents)

### Code Repositories
- [Beginner/Intermediate Samples](https://github.com/GoogleCloudPlatform/generative-ai)
- [Advanced Samples](https://github.com/GoogleCloudPlatform/applied-ai-engineering-samples)
- [Evaluation Notebooks](https://github.com/GoogleCloudPlatform/generative-ai/blob/main/gemini/evaluation/)

---

## Document Statistics

**Original Whitepaper:**
- Total Pages: 76
- Total Lines: 776
- Figures: 18 (diagrams, charts, screenshots)
- Tables: 4
- References: 41 (academic papers, product docs, blog posts)
- Publication Date: February 2025
- Target Audience: Software engineers, AI/ML developers, enterprise architects

**Topic Extraction:**
- Total Topic Files: 8
- Total Reading Time: ~3.5-5 hours (all topics)
- Complexity Range: ⭐⭐⭐ to ⭐⭐⭐⭐⭐
- Total Word Count: ~35,000 words (across all topics)

---

## How to Use This Index

### For Self-Study
1. Choose a learning path based on your role (developer, architect, executive, specialist)
2. Read topics in recommended order
3. Refer to cross-links for deeper understanding
4. Use code repositories for hands-on practice

### For Team Training
1. Assign topics based on team roles:
   - **Developers**: Path 2 (Practical Implementation)
   - **Architects**: Path 5 (Multi-Agent Systems)
   - **QA/Eval**: Path 4 (Evaluation Specialist)
   - **Leadership**: Path 3 (Executive Overview)
2. Schedule weekly reading + discussion sessions
3. Run hands-on labs with code samples after each topic

### For Reference
1. Use topic tables to quickly find relevant content
2. Use case mapping to jump to applicable topics
3. Follow cross-links between topics for deeper dives

---

## Version History

**v1.0** (2025-11-14)
- Initial extraction from "Agents Companion" whitepaper
- 8 topic files created
- Master index with 5 learning paths
- Quick reference tables added

---

**Extracted By:** Claude Code
**Extraction Date:** 2025-11-14
**Source Document:** Google's "Agents Companion" (February 2025)
**Total Extraction Time:** ~2 hours

---

**Feedback & Contributions:**
This is a living document. If you find errors or have suggestions for improvement:
- Open an issue in the repository
- Submit a pull request with corrections
- Email the course instructor

---

**Happy Learning! 🤖**
