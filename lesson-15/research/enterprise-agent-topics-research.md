# Enterprise Agent Topics Research

## Micro Agents
- `lesson-15/enterprise-grade-agents.txt` defines MicroAgents as containerized LLM + tools + execution logic packaged as microservices so they inherit Kubernetes scaling, rolling updates, and fault isolation.
- **Enterprise Deep Research (EDR)** – [arXiv:2510.17797](https://arxiv.org/abs/2510.17797) – demonstrates a planner-plus-specialist-agent architecture deployed as streaming services; validates microservice packaging and elastic scaling for analytics workloads.
- **Azure AI Agent Service Enterprise Demo** – [github.com/Azure-Samples/azure-ai-agent-service-enterprise-demo](https://github.com/Azure-Samples/azure-ai-agent-service-enterprise-demo) – real-world sample that encapsulates GPT-4o logic, enterprise connectors, and Bing search inside a containerized agent with streaming outputs.
- **Enterprise-Grade-Agents-Course** – [github.com/The-Swarm-Corporation/Enterprise-Grade-Agents-Course](https://github.com/The-Swarm-Corporation/Enterprise-Grade-Agents-Course) – Swarms-based templates that treat each agent as a reusable deployable, reinforcing microservice-style development and CI/CD.

## Agent Security
- Core requirements from `enterprise-grade-agents.txt`: mTLS for mutual auth, OAuth2 for scoped authorization, centralized secrets, RBAC, and non-root containers on Kubernetes.
- **AgentFacts** – [arXiv:2506.13794](https://arxiv.org/abs/2506.13794) – proposes a "Know Your Agent" (KYA) metadata standard with cryptographically signed capability declarations so registries/governance systems can verify agent identity before granting access.
- **AI Agentic Workflows & Enterprise APIs** – [arXiv:2502.17443](https://arxiv.org/abs/2502.17443) – argues for zero-trust API gateways, dynamic scopes, and throttling tailored to autonomous agents, complementing mTLS/OAuth2 practices.
- **agents-towards-production** – [github.com/NirDiamant/agents-towards-production](https://github.com/NirDiamant/agents-towards-production) – hands-on tutorials wiring secrets managers, policy checks, and SOC-style audit logging into agent pipelines.

## Agent Reliability
- Textbook guidance: keep tasks small, use deterministic execution, orchestrate retries, and specialize agents to limit combinatorial error propagation.
- **AgentArch Benchmark** – [arXiv:2509.10769](https://arxiv.org/abs/2509.10769) – evaluates 18 orchestration/memory/tooling combinations, showing that architecture choices (not just LLM size) materially change task success rates.
- **FinRobot** – [arXiv summary](https://huggingface.co/papers/2506.01423) – enterprise ERP agents with deterministic guardrails cut processing time and reduce error rates in finance workflows, illustrating domain-specialized reliability controls.
- **Enterprise Deep Research** – [arXiv:2510.17797](https://arxiv.org/abs/2510.17797) – planner delegates atomic tasks to specialists with automated retries, reducing cascading hallucinations compared to monolithic prompts.

## Agent Explainability
- Plan advocates for persisted task plans, collaborator lists, parameter substitution logs, and execution traces akin to aviation "black boxes."
- **AgentFacts** extends explainability by exposing verifiable metadata (owner, capabilities, policies) that can be stored alongside plan artifacts for audits.
- **AgentRxiv** – [agentrxiv.github.io/resources/agentrxiv.pdf](https://agentrxiv.github.io/resources/agentrxiv.pdf) – multi-agent research environment that logs each phase (Literature Review → Experiment → Report) and every decision, proving explainability improves collaborative agent debugging.
- **Guardrails AI** – [github.com/ShreyaR/guardrails](https://github.com/ShreyaR/guardrails) – declarative schemas/validators that document prompt structures, constraints, and validation results, supplying rich traces for agent transparency.

## Agent Scalability
- `enterprise-grade-agents.txt` critiques single-process Python workflows; recommends distributed MicroAgents, registries, and orchestration protocols.
- **Blueprint Architecture for Compound AI** – [arXiv:2504.08148](https://arxiv.org/abs/2504.08148) – details agent/data registries, planners, and monitoring streams so thousands of agents can coordinate while sharing infrastructure primitives.
- **Enterprise Deep Research** – streaming multi-agent design that shards analytics workloads and supports continuous planning/execution, evidencing operational scalability.
- **Azure AI Agent Service demo** and **Enterprise-Grade-Agents-Course** provide code-level patterns for horizontal scaling, templates, and CI/CD automation for large fleets.

## Agent Discovery
- Plan highlights registries/marketplaces, discovery scoping rules (visibility + characteristics), and strict vs flexible naming conventions.
- **agents.txt standard** – [agentstxt.dev](https://agentstxt.dev/) – emerging open format (analogous to robots.txt) so websites/services publish machine-readable agent metadata for automated discovery.
- **AgentFacts** supplies signed metadata that registries can verify before listing agents, strengthening trust in discovery results.
- **Blueprint Architecture for Compound AI** – [arXiv:2504.08148](https://arxiv.org/abs/2504.08148) – includes discovery components (agent registries + characteristic filters) directly in its enterprise reference design.

## Agent Observability
- Source text calls for microservice-style logs, metrics, traces, and trace ID propagation across agent/tool hops.
- **Arize Phoenix** – [github.com/Arize-ai/phoenix](https://github.com/Arize-ai/phoenix) – open-source LLM observability platform ingesting traces (OpenTelemetry-compatible), surfacing token-level drift, embeddings, and feedback loops for troubleshooting agent behaviors.
- **OpenLLMetry** – [github.com/traceloop/openllmetry](https://github.com/traceloop/openllmetry) – auto-instruments LangChain/LlamaIndex pipelines to emit OpenTelemetry spans for prompts, tool calls, and downstream services, enabling end-to-end trace stitching.
- **agents-towards-production** repository contains Prometheus/Grafana wiring examples for agent error rates, latency, and conversation depth, aligning with required observability metrics.

## Agent Operability
- `enterprise-grade-agents.txt` mandates AgentOps: health probes, alerting, controlled rollouts, automated recovery, redaction, and compliance-aware auditing.
- **From Benchmarks to Business Impact: Deploying IBM Generalist Agent** – [arXiv:2510.23856](https://arxiv.org/abs/2510.23856) – describes IBM's production rollout of a generalist agent with staged deployments, policy reviews, and operational SLAs.
- **Towards Enterprise-Ready Computer Using Generalist Agent** – [arXiv:2503.01861](https://arxiv.org/abs/2503.01861) – documents iterative evaluation loops, incident response playbooks, and ops metrics required for enterprise agents.
- **Enterprise-Grade-Agents-Course** + **agents-towards-production** provide CI/CD blueprints, canary scripts, redact/anonymize hooks, and runbooks translating AgentOps theory into actionable practice.
