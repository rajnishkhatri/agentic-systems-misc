# Context Engineering: Mastering Sessions and Memory for AI Agents

The true intelligence of AI agents doesn't come from the model itself—it comes from how developers assemble the context around it. This November 2025 whitepaper from Google engineers Kimberly Milam and Antonio Gulli presents a transformative framework for building stateful, personalized, and persistent AI systems through sophisticated context management. **The central insight: bigger models aren't enough**. Without proper context engineering to decide what to keep, forget, compress, and inject, agents cannot reason reliably over long interactions or deliver true personalization. The whitepaper introduces a comprehensive architecture treating context as critical infrastructure rather than background noise, fundamentally shifting how developers build production-ready AI agents.

Context engineering represents the evolution beyond static prompt engineering. While prompting tells a model what to do, context engineering provides everything needed to do it intelligently. The whitepaper frames this through two interconnected pillars—**Sessions** (the agent's short-term working memory) and **Memory** (the agent's long-term persistent knowledge)—and demonstrates how their synergy transforms reactive chatbots into adaptive, context-aware companions. This framework has rapidly become essential reading for anyone building AI agents in 2025, with adoption across major frameworks like LangGraph, ADK, and CrewAI.

## Foundations: What context engineering actually means

Context engineering is the process of dynamically managing information within an LLM's context window to enable stateful, intelligent agents. Unlike prompt engineering, which focuses on crafting optimal instructions, **context engineering addresses the entire payload**: system instructions, tool definitions, memories, conversation history, and external data dynamically constructed based on the user, conversation, and environment.

Think of it as preparing a gourmet meal. Prompt engineering gives the chef a recipe—they might prepare something decent with available ingredients. Context engineering provides the recipe, all necessary ingredients, proper tools, and optimal working conditions. The goal: ensure the model has no more and no less than the most relevant information to complete its task.

### The operating system metaphor

Andrej Karpathy crystallized the conceptual shift by describing LLMs as "a new kind of operating system." The LLM serves as the CPU, and its **context window functions as RAM**—the model's working memory. Just as an operating system curates what fits into CPU RAM, context engineering plays a similar role: the delicate art and science of filling the context window with precisely the right information for each step.

This analogy reveals fundamental constraints. Context windows have limited capacity to handle various information sources (instructions, knowledge, tools, history). As the window grows beyond 30,000-100,000 tokens depending on the model, performance degrades through several failure modes: context poisoning (errors compounding), context distraction (over-focusing on history rather than reasoning), context confusion (too many tools degrading decisions), and context clash (contradictory information derailing reasoning).

### The context management loop

The whitepaper describes context engineering as a continuous cycle with five key phases. First, the **agent fetches context** from various sources (session storage, memory databases, RAG systems, tool outputs). Second, **context is prepared** when the agent framework constructs the full prompt for the LLM call. Third, **the LLM and tools are invoked** iteratively until generating the final response. Fourth, the **final response is generated** for the user. Fifth, **context is uploaded** to persistent storage for future turns.

At the heart of this cycle live two components: **Sessions** manage turn-by-turn state of a single conversation (like a workbench with project materials), while **Memory** provides long-term persistence across multiple sessions (like a meticulously organized filing cabinet). This architectural separation enables sophisticated agents that remember, learn, and personalize while managing the fundamental challenge of ever-growing conversation histories that can exceed context windows and degrade model performance.

## Sessions: The agent's real-time workspace

A Session is the container for one conversation—a chronological log of events and temporary state that grounds every turn. The whitepaper uses a compelling analogy: **Sessions are your desk while working on a project**, cluttered with notes, drafts, and active materials you're currently using. When you finish the project, you tidy up and file the important bits into long-term storage.

### Anatomy of a session

Sessions contain two fundamental components. **Events** form the building blocks of conversation: every user input, agent response, tool call, and tool output logged chronologically. This immutable append-only log preserves the complete interaction history. **State** represents structured working data—a scratchpad or working memory containing variables, shopping carts, plans, or task progress that the agent actively manipulates.

For example, in a customer support session, events would capture the entire dialogue: "User: My laptop has a red blinking light. Agent: Let me check your warranty status. ToolCall: query_warranty(laptop_id). ToolOutput: {warranty_active: true, expires: 2026-03-15}. Agent: Your warranty is active. Let's troubleshoot..." Meanwhile, state might store: `{customer_id: 12345, device: "laptop", issue: "red_light", warranty_status: "active"}`.

This dual structure enables agents to maintain coherence across turns while preserving both the conversational flow and structured data needed for reasoning. **Sessions are temporary, noisy, and eventually too large**—which is precisely why memory systems become essential.

### Multi-agent session architectures

In multi-agent systems where multiple specialized agents collaborate, session management becomes critical for coordination. The whitepaper describes two primary approaches: **shared unified history** and **separate individual histories**.

In the **shared unified history model**, all agents read and write to the same chronological log—one central conversation history appended in order. This approach works best for tightly coupled, collaborative tasks where agents need full visibility into each other's actions. For instance, in a research assistant with specialized sub-agents for literature review, data analysis, and report writing, the shared history ensures each agent understands what others have discovered.

The **separate individual histories method** gives each agent its own private conversation log, functioning as black boxes to other agents. This isolation works well for loosely coupled tasks or when agents handle sensitive information that shouldn't be shared. The trade-off: agents must communicate explicitly through defined interfaces rather than inferring from shared context.

The whitepaper emphasizes that session history represents the **permanent, unabridged transcript**, while context represents the **information payload sent to the LLM in a single turn**. This distinction becomes crucial when managing long conversations.

### Production considerations for sessions

Deploying sessions in production requires evolution from simple in-memory logs to robust enterprise-grade services. The whitepaper identifies three critical areas: **Security and privacy** demands protecting sensitive information with proper authentication, authorization, encryption, and user isolation. **Data integrity and lifecycle management** requires clear rules for storage and maintenance—sessions shouldn't live forever; time-to-live (TTL) policies, automatic archival, and GDPR-compliant deletion become essential. **Performance and scalability** means handling thousands of concurrent sessions with low latency, requiring distributed storage systems, caching strategies, and efficient serialization.

Major frameworks implement these requirements differently. Google's Agent Engine Sessions API provides managed session storage with built-in security and scalability. LangGraph uses checkpointing to persist agent state across all steps. OpenAI's Agents SDK offers session management with configurable persistence backends.

### Managing long context conversations

As conversations grow, token usage increases linearly, creating cascading problems: **context window limits** (every LLM has maximum capacity), **API costs** (providers charge per token sent and received), **latency** (more text takes longer to process), and **quality degradation** (performance decreases with excessive tokens through "context rot").

The whitepaper presents several strategies for managing this challenge:

**Summarization and compression** periodically condense older conversation portions into compact summaries. Claude Code's "auto-compact" feature exemplifies this: when context reaches 95% capacity, the system summarizes the full trajectory while preserving critical objectives and decisions. The challenge lies in avoiding information loss—aggressive summarization can drop crucial details needed for later reasoning.

**Strategic trimming** removes less relevant portions based on heuristics. Simple approaches drop oldest messages; sophisticated methods use relevance scoring to selectively prune. The whitepaper warns that trimming protected context (like initial objectives or key constraints) can cause catastrophic failures where agents lose track of their purpose.

**Turn cadence limits** restrict the number of turns before triggering compression. Through experimentation and analyzing conversation distributions, developers determine optimal thresholds. One approach: use an LLM to evaluate conversations, identifying tasks per conversation and calculating average turns needed per task, then setting compression triggers accordingly.

**Offloading and external storage** moves token-heavy content outside the context window. Tool outputs, large documents, or intermediate results get stored in files or databases, with only summaries or metadata remaining in context. The key insight: **reversible compression**—storing URLs not webpage content, file paths not full files—enables retrieving originals when needed while achieving 100:1 compression ratios.

## Memory: The engine of personalization

Where sessions end, memory begins. Memory is the **decoupled system for long-term persistence**, capturing and consolidating key information across multiple sessions. The whitepaper presents memory not as saved chat history but as **LLM-curated, consolidated, and structured knowledge that evolves over time**, enabling continuity across sessions while reducing context window costs.

The analogy: Memory is the **climate-controlled filing cabinet** with organized, preserved knowledge, while sessions are the cluttered desk with current work materials. This distinction proves fundamental to sophisticated agent design.

### Memory vs. RAG: A critical distinction

The whitepaper draws a sharp line between Memory and Retrieval-Augmented Generation (RAG), two complementary but distinct capabilities:

**RAG acts as the research librarian**—a static, factual role accessing general knowledge from documents. RAG makes agents experts on facts by retrieving relevant information from large corpora. It's document-centric, typically using pre-existing knowledge bases, and retrieves based on semantic similarity to the current query.

**Memory acts as the personal assistant**—a dynamic, user-specific role extracting and consolidating facts from dialogue itself. Memory makes agents experts on the user by learning preferences, facts, and patterns from interactions. It's conversation-derived, continuously updated through agent interactions, and enables true personalization.

For example, RAG retrieves "AWS Lambda supports Python, Node.js, Java..." from documentation. Memory retrieves "Teva prefers AWS examples, dislikes theoretical explanations, works in e-commerce" from past conversations. Together, they create agents that are both knowledgeable (RAG) and personalized (Memory).

### Types and taxonomy of memory

The whitepaper categorizes memories along multiple dimensions. By **information type**, memories split into **Declarative Memory** (facts, figures, events the agent can explicitly declare: "User prefers dark mode") and **Procedural Memory** (skills, workflows, learned patterns: "When debugging, first check logs, then reproduce locally").

By **creation mechanism**, memories emerge as **Explicit** (user directly commands: "Remember I'm allergic to peanuts") or **Implicit** (agent infers and extracts without direct command: extracting preferred communication style from interaction patterns). By **scope**, memories can be **User-Level** (personalized to individuals), **Session-Level** (compacted summaries of long conversations), or **Application-Level** (shared knowledge accessible to all users, like learned best practices).

Multi-modal memory extends beyond text to handle images, videos, and audio. The whitepaper emphasizes distinguishing **source-derived data** (metadata about media: "user uploaded vacation photo on 2025-11-15") from **content-derived data** (understanding the media itself: "photo shows beach sunset with two people").

### Memory organization patterns

After creating memories, developers must decide organizational structure. The whitepaper presents three primary patterns:

**The Collections Pattern** organizes multiple self-contained, natural language memories for each user. Each memory represents a distinct event, summary, or observation stored independently. This approach enables fine-grained retrieval but requires sophisticated selection mechanisms to find relevant memories among potentially thousands. Example structure: `[{content: "User prefers concise responses", metadata: {confidence: 0.95, created: "2025-11-01"}}, {content: "User is building e-commerce platform", metadata: {confidence: 0.98, created: "2025-11-15"}}]`

**The Structured User Profile** maintains core facts organized like a contact card, continuously updated with new stable information. This approach provides quick access to essential user data but requires more rigid schemas. Example: `{preferences: {response_style: "concise", code_language: "Python"}, context: {current_project: "e-commerce", tech_stack: ["AWS", "React"]}, history: {sessions_count: 47, last_interaction: "2025-11-20"}}`

**The Rolling Summary** consolidates all information into a single evolving memory representing the entire user-agent relationship. This compact approach minimizes retrieval complexity but risks information loss during consolidation. Example: "Teva is an experienced engineer building an e-commerce platform using AWS and React. Prefers concise, code-heavy responses with minimal theory. Currently focused on optimizing checkout flow latency. Has 47 prior sessions, with strong expertise in distributed systems."

The choice depends on use case complexity, retrieval requirements, and acceptable trade-offs between granularity and simplicity.

### Storage architectures

Memories require persistent storage with efficient retrieval capabilities. **Vector databases** represent the most common approach, enabling retrieval based on semantic similarity rather than exact keywords. Each memory gets embedded into high-dimensional vector space, allowing queries like "user's technology preferences" to retrieve related memories even without exact keyword matches. Popular implementations include Pinecone, Weaviate, ChromaDB, and FAISS.

**Knowledge graphs** store memories as networks of entities (nodes) and relationships (edges). This structure excels at representing complex interconnections. For example, representing "User built Project A using Technology B" as a graph with nodes (User, Project A, Technology B) and edges (built, uses) enables graph traversal queries that discover indirect relationships: "What technologies does this user have experience with?" A **hybrid approach** combines both: vectors for semantic search, graphs for relationship traversal.

Each memory follows a consistent structure: `{content: "Natural language fact or observation", metadata: {confidence_score: 0.0-1.0, source_session_id: "...", created_timestamp: "...", last_updated: "...", lineage: "...", tags: []}}`. The metadata proves critical for **provenance tracking**—maintaining detailed records of origin and history enabling agents to critically evaluate memory quality and trustworthiness.

## The memory generation pipeline

Memory generation is an **LLM-driven ETL (Extract, Transform, Load) pipeline** that autonomously transforms raw conversational data into structured, meaningful insights. This active processing distinguishes memory managers from passive databases or RAG engines—the system decides when to add, update, or merge memories using LLM intelligence.

### Extraction: Signal from noise

Memory extraction answers a fundamental question: **What information in this conversation is meaningful enough to become a memory?** This isn't simple summarization but targeted, intelligent filtering designed to separate signal from conversational noise.

The extraction process uses programmatic guardrails and carefully constructed instructions guiding an LLM through the decision. **Topic definitions** (formal schemas or natural language descriptions) specify what constitutes meaningful information for the agent's purpose. **Few-shot prompting** shows the LLM examples of input text and ideal structured memory output. **Extraction criteria** might include: user preferences, factual statements about the user, important decisions, procedural insights (what worked/failed), and domain-specific facts.

For example, from the conversation "I prefer getting summaries in bullet points. By the way, it's raining today," extraction would capture the preference but likely ignore the weather comment (unless the agent specifically tracks environmental context). The output: `{type: "preference", content: "User prefers summaries formatted as bullet points", confidence: 0.95}`.

### Consolidation: Creating coherence

Consolidation represents the **most sophisticated stage in the memory lifecycle**, transforming a collection of extracted facts into a curated understanding of the user. It addresses critical problems: **information duplication** (same fact mentioned multiple times), **conflicting information** (user initially prefers X, later switches to Y), **information evolution** (facts that change over time), and **relevance decay** (outdated information no longer applicable).

The consolidation process is an **LLM-driven workflow** comparing current memories with new information to decide: **Update** (merge new insight into existing memory, updating confidence and timestamp), **Create** (add genuinely new information as a separate memory), or **Delete** (remove outdated or contradicted information).

For example, consider existing memory: `"User prefers Python"` and new extraction: `"User now primarily uses TypeScript"`. The consolidation LLM might update: `"User previously preferred Python but now primarily uses TypeScript"` or create separate memories: `{content: "User has Python experience", confidence: 0.8}` and `{content: "User currently uses TypeScript", confidence: 0.95}`, depending on the organization pattern and domain requirements.

### Provenance and trust

For reliable decisions, agents must critically evaluate memory quality. This trustworthiness derives from **memory provenance**—detailed records of origin and history analogous to Git version control. Each memory tracks: **source session** (which conversation generated it), **extraction timestamp**, **last consolidation**, **confidence score evolution**, **modification history**, and **supporting evidence links**.

Provenance enables agents to reason about memory reliability: recently confirmed memories get higher weight, memories from successful sessions receive trust boosts, contradicted memories get depreciated or removed, and memories with low confidence might trigger validation requests to users.

### Triggering memory generation

A critical architectural decision: **when should memory generation occur?** The whitepaper presents several strategies:

**Session Completion**: Trigger extraction and consolidation at the end of multi-turn sessions. This batch approach minimizes LLM calls but delays availability. Works well for clearly bounded conversations.

**Turn Cadence**: Generate memories after a specific number of turns (e.g., every 10 turns). Provides regular updates without per-turn overhead. The optimal cadence requires experimentation based on conversation characteristics.

**Real-Time**: Extract after every turn for immediate availability. Highest memory freshness but highest cost and latency impact. Suitable for critical applications where personalization must be instant.

**Explicit Command**: Users directly instruct the agent to remember something. Guarantees user control but limits passive learning. Best combined with other methods.

**Memory-as-a-Tool (Most Sophisticated)**: Expose memory generation as a tool the agent can invoke. The tool definition specifies what types of information should be considered meaningful, and the agent analyzes conversations to decide when to call the tool. This approach gives agents intelligent autonomy: generating memories when truly valuable, avoiding unnecessary extractions.

Example Memory-as-a-Tool definition:
```json
{
  "name": "create_memory",
  "description": "Store important user preferences, facts, or insights for future conversations",
  "parameters": {
    "content": "Natural language description of the fact or insight",
    "type": "preference | fact | procedural | contextual",
    "confidence": "0.0 to 1.0 indicating certainty"
  },
  "when_to_use": "When user explicitly states a preference, shares important personal/project information, or when you learn something that would be valuable in future interactions"
}
```

## Memory retrieval and inference

Once memories exist, agents need mechanisms to select and inject relevant memories at runtime. **Memory retrieval** proves just as critical as generation—injecting irrelevant memories confuses models, while missing crucial memories breaks personalization.

### Retrieval strategies

The retrieval strategy depends heavily on memory organization. For **Structured User Profiles**, retrieval is straightforward: load the entire profile at session start since it's compact and always relevant. For **Collections** with potentially thousands of memories, sophisticated selection becomes essential.

The whitepaper identifies three key questions driving retrieval: **Relevance** (Is this memory related to the current conversation?), **Recency** (How recently was this memory created or confirmed?), and **Importance** (How critical is this memory to the current task?). These factors combine into retrieval scores: `retrieval_score = w1 * semantic_similarity + w2 * recency_factor + w3 * importance_weight`, where weights are tuned based on application needs.

**Semantic similarity** uses vector embeddings to compare the current query or conversation context with memory embeddings. **Recency factors** might exponentially decay: memories from the last week get weight 1.0, last month 0.8, last year 0.5. **Importance weights** come from metadata: user-confirmed memories get higher importance than agent-inferred ones, memories frequently accessed get boosted, memories leading to successful outcomes gain importance.

Advanced retrieval combines multiple techniques. Windsurf's approach uses **embedding search** for semantic similarity, **keyword matching** (grep) for exact matches, **knowledge graph traversal** for relationship-based retrieval, and **AST parsing** for code structure. This multi-technique approach achieves 3× better accuracy than any single method.

### Retrieval timing: Proactive vs. reactive

**Proactive retrieval** automatically loads relevant memories at the start of every turn. The system predicts what might be needed based on conversation context. This approach ensures memories are available when needed but increases token usage and latency. Suitable when memory sets are small or when missing memories would severely degrade experience.

**Reactive retrieval (Memory-as-a-Tool)** gives agents a tool to query memories on demand. The agent decides when memory lookup is needed based on the conversation. This approach minimizes unnecessary token usage but requires sophisticated agent reasoning to recognize when memories would help. The tool might look like:

```json
{
  "name": "search_memories",
  "description": "Search user memories for relevant preferences, facts, or context",
  "parameters": {
    "query": "Natural language query describing what to search for",
    "memory_types": ["preference", "fact", "procedural"],
    "limit": "Maximum number of memories to retrieve"
  }
}
```

### Inference: Injecting memories into context

Once retrieved, memories must be positioned within the context window. The whitepaper discusses two primary approaches:

**Appending to system instructions** keeps the history clean and frames memories as foundational context for the entire interaction. This method works well for stable facts and preferences that apply universally. Example system prompt structure:
```
You are a helpful coding assistant.

User Profile:
- Prefers Python and AWS
- Currently building an e-commerce platform
- Values concise responses with code examples

Now help the user with their request...
```

**Injecting into dialogue** inserts memories directly into the turn-by-turn conversation. This approach provides temporal context (when facts were learned) but risks **dialog injection** where the model mistakes memories as actual conversation turns, leading to confusion. To mitigate, clearly mark injected memories with special formatting:

```
[SYSTEM MEMORY: User prefers Python]

User: How should I implement the authentication flow?