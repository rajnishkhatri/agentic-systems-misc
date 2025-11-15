# Task 0.1: agents_memory.txt Citation Reference

**Purpose:** Extract terminology, memory types, and key concepts with exact line numbers for use in Tasks 1.0-6.0.

**Source:** `lesson-14/agents_memory.txt` (516 lines)

---

## 1. Five Memory Types Definitions

### 1.1 Working Memory (Short-Term)
**Lines 22-23:**
> "Working memory is a type of short-term memory that is typically defined as a system with limited capacity that temporarily holds information that we need for things like decision-making and reasoning. For LLMs, it is typically data that persists across LLM calls. More specifically, it is the chat history of the LLM that is being stored in memory and continuously fed back to the LLM."

**Key Characteristics:**
- Limited capacity
- Persists across LLM calls
- Chat history storage
- Continuously fed back to LLM

**Lines 44-48 - Flamingo Example:**
> "In practice, this is the conversation history of the LLM, which serves as context for generating responses. Illustrated in Figure 4-5, they are generally formatted as messages demonstrating the differences between system prompts, the user's query, and the LLM's answer. It is a conversation where the user tells something about themselves, namely that they love flamingos."

**Lines 46-48 - Key Insight:**
> "The query ('What is my favorite animal?') does not trigger the LLM to recall the past on its own. Rather, it is provided with the entire conversation history, which contains the relevant information, namely that the user loves flamingos. In other words, the LLM does not truly 'remember' past conversations but is instead told what the conversation was by explicitly inserting it into the prompt."

---

### 1.2 Episodic Memory (Long-Term)
**Lines 26-28:**
> "Episodic memory: Involves remembering specific events and experiences from one's past (e.g., your last birthday party). For agents, this typically involves specific actions the agent has taken thus far and their outcomes."

**Key Characteristics:**
- Remembers specific events/experiences
- Agent actions and outcomes
- Past traces and states

**Lines 85-86 - Storage:**
> "Long-term memory typically involves maintaining one or more external databases that can be queried to extract additional information. This can contain information about previous traces or states of the agent (episodic memory)..."

---

### 1.3 Semantic Memory (Long-Term)
**Lines 29-31:**
> "Semantic memory: Involves remembering knowledge about the world (e.g., the capital of France). For agents, this may involve querying an external database like Wikipedia or the codebase that you are working on."

**Key Characteristics:**
- World knowledge
- External databases (Wikipedia, codebase, etc.)
- Information unrelated to agent's behavior

**Lines 85-86 - Context:**
> "...or information unrelated to the agent's behavior but about the context of your application instead (semantic memory), like your organization's documents."

---

### 1.4 Procedural Memory (Long-Term)
**Lines 32-34:**
> "Procedural memory: Involves remembering patterns of how to do things (e.g., writing code in Python). For agents, this can be information hidden in its parameters (also called parametric memory) or the system prompt, which persists across calls."

**Key Characteristics:**
- Patterns and procedures
- System prompt
- Persists across calls
- Can overlap with parametric memory

**Lines 198-200 - Context Engineering Perspective:**
> "System prompt: The core context and rules for the agent, which define how it should behave (procedural memory)."

---

### 1.5 Parametric Memory (Model Weights)
**Lines 37-39:**
> "As briefly mentioned previously, we can also consider the type of memory that the model already has, parametric memory. Without any memory modules, LLMs are trained to a certain extent to retain information. If you ask an LLM what the capital of France is, most LLMs will correctly remember that it is Paris. The answer is therefore contained within the parameters of the model and attempts to retrieve it."

**Key Characteristics:**
- Information stored in model parameters
- Training-derived knowledge
- Not stable (cannot guarantee retention)
- Not explicitly retrievable

**Lines 39-40 - Limitations:**
> "Although a relatively new field, it is technically possible to instill information into an LLM through supervised fine-tuning. Note that this is not a stable method, as we are not entirely sure beforehand which information gets retained explicitly and which information is incorrectly reconstructed."

---

## 2. Short-Term vs Long-Term Memory Distinction

### 2.1 Short-Term Memory Characteristics

**Lines 42-44:**
> "Short-term memory in Agents is the information it has about recent interactions, typically the ongoing conversations with the user or the behavior of the LLM. In practice, this is the conversation history of the LLM, which serves as context for generating responses."

**Lines 50-53 - Context Window Constraint:**
> "Most LLMs have a limited context window, which is the number of tokens that the LLM can process both and combine both the input and the output tokens as seen in Figure 4-7. In this example, a short query and answer are given which total 13 tokens out of a potential 8,192."

**Lines 58-59 - Overflow Problem:**
> "However, as the conversation history grows, so do the number of tokens. Eventually, and as shown in Figure 4-9, if the conversation history gets too large, it will not fit within the context windows."

---

### 2.2 Long-Term Memory Characteristics

**Lines 83-86:**
> "As the conversation history grows and the actions that an agent has taken, so does the need for long-term memory. Long-term memory typically involves maintaining one or more external databases that can be queried to extract additional information. This can contain information about previous traces or states of the agent (episodic memory) or information unrelated to the agent's behavior but about the context of your application instead (semantic memory), like your organization's documents."

**Key Differences:**
- **Short-term:** Conversation history, limited capacity, token-bounded
- **Long-term:** External databases, queryable, scalable storage

---

## 3. Short-Term Memory Management Techniques

### 3.1 FIFO Trimming (First-In-First-Out)

**Lines 65-66:**
> "The first technique for efficient short-term memory is rather straightforward: trimming the messages as they grow. Whenever the number of messages grows too large for the LLM's context window to handle, we can decide to simply remove the first few interactions until it fits that window."

**Lines 66:**
> "Seen in Figure 4-10, this might remove quite a lot of information that may or may not be relevant to future queries."

**Pros:**
- Simple to implement
- Predictable behavior

**Cons:**
- May lose critical early context
- No intelligence in what's removed

---

### 3.2 Rolling Summarization

**Lines 68-69:**
> "Instead, a common technique is to employ another LLM to summarize the conversation history. After each conversation turn, the same or another LLM will summarize it and add it to the full summary of the conversation (Figure 4-11)."

**Lines 71-72:**
> "As illustrated in Figure 4-12, the created summary will be shown together with the query for the LLM to answer. This summary might still fill the context window over time as summaries are stacked on one another, but it is much slower than filling the context window with the raw conversation history."

**Lines 76-77 - Variants:**
> "Stacking summaries is not the only method of summarization. Instead of adding a summary of the most recent query/answer pair each time, you can instead summarize the conversation history of the last 5 conversations. Likewise, you can decide to maintain one summary and ask the LLM to update it after each conversation."

**Pros:**
- Preserves semantic meaning
- Slower context window growth
- Flexible implementation (stacked vs. updated summary)

**Cons:**
- Requires additional LLM calls
- May lose specific details

---

### 3.3 Token Budget Management

**Lines 63:**
> "Moreover, the more information put in the prompt, the more difficult it will be for the LLM to attend to everything."

**Lines 81-82:**
> "Although it may seem straightforward, maintaining the conversation history can be a difficult task and requires understanding what is important: the entire history, the recent history, or a summarized variant? For short conversations, maintaining the entire history would work, but that might not be the case for long sequences of actions."

**Key Principle:**
- Balance between context completeness and LLM attention
- Different strategies for different conversation lengths

---

## 4. Long-Term Memory Patterns

### 4.1 MemoryBank (RAG with Forgetting Curve)

**Lines 105-108:**
> "An interesting take on RAG for ChatBots is MemoryBank, a mechanism that allows LLMs to recall relevant memories as a long-term mechanism (external database) rather than a short-term mechanism (conversation history). Its experiences through conversations are stored in a separate database that allows the LLM to retrieve relevant memories. What sets it apart from regular RAG is that this memory is continuously updated to selectively preserve memory through an updating mechanism."

**Lines 109-110 - Forgetting Curve:**
> "This mechanism allows the MemoryBank to forget and reinforce memory inspired by the Ebbinghaus Forgetting Curve theory, which is a curve demonstrating the pace at which we tend to forget. The curve is often shown as being exponential, resulting in a loss of half of what we learn each day."

**Lines 110-111 - Spaced Repetition:**
> "A common way to prevent forgetting what you learnt, for instance when preparing for exams, is to actively recall the learned information frequently. This is referred to as spaced repetition, which tends to decrease the pace at which knowledge is forgotten."

**Lines 112-113 - Memory Decay:**
> "MemoryBank borrows from this theory and frequently updates the long-term memory of an LLM based on which pieces of knowledge are (not) accessed. Specifically, this means that when a memory item is retrieved and used during conversations, it will persist longer in the MemoryBank. However, if the memory item hasn't been retrieved for a while, then there is a chance the memory will be removed entirely."

**Lines 114-119 - Memory Types in MemoryBank:**
> "The authors use a few variants of memory (Figure 4-17):
> - Conversation history — Raw multi-turn conversations
> - Summaries of past events — These are generated by an LLM based on the conversation history
> - User's portrait — The personality traits and emotions of the user as summarized by the LLM based on the conversation history"

**Lines 120-121 - Retrieval Process:**
> "The summaries and conversation turns are embedded so that they can easily be retrieved. The user portrait is dynamically updated and always passed as additional context. Figure 4-18 shows a full overview of this pipeline. When a query is created, it is embedded, and related conversation turns and summaries are retrieved, together with the user portrait."

**When to Use:**
- Chatbots with long-term user relationships
- Applications needing adaptive memory management
- Systems where memory relevance changes over time

---

### 4.2 A-MEM (Zettelkasten-Inspired Agentic Memory)

**Lines 146-148:**
> "An interesting approach to agentic RAG is A-MEM, an agentic memory system derived from the notetaking method known as Zettelkasten. Zettelkasten approaches note-taking as having three important components, namely atomicity, hypertextual notes, and personalization."

**Lines 150-151 - Atomicity:**
> "Atomicity means that each Zettel (a note) should only contain one unit of knowledge, referred to as an atom. This note could, for example, contain a brief description of how memory works in agentic systems."

**Lines 152-154 - Hypertextual Notes:**
> "Then, hypertextual notes refer to the idea that all notes refer to each other and may explain or expand on each other's content. For instance, the previously created note can be connected to another note that has some information about RAG. Since both are memory systems, they are likely to be related."

**Lines 155-162 - Memory Structure:**
> "In the context of agents, each note contains the following information and can be considered a piece of memory:
> - The original interaction with the environment (i.e., one turn)
> - The timestamp of the interaction
> - LLM-generated keywords that capture key concepts
> - LLM-generated tags to categorize the interaction
> - LLM-generated contextual description
>
> By focusing on a single unit, namely a single interaction, A-MEM adheres to the principle of atomicity."

**Lines 164-165 - Embedding Strategy:**
> "Then, all pieces of information are embedded so that they can be used to later on easily retrieve related information. Note that all information, except for the timestamp, is concatenated so that a single embedding is created for the entire note/memory (Figure 4-23)."

**Lines 167-169 - Linking Process:**
> "Interestingly, the authors use this generated note embedding as one of the main IDs of the note. To link this note to other memories, they run a similarity search between this note's embeddings and all other memories and extract the top-k memories. After doing so, the LLM is asked to decide which of these candidate memories should be linked to the newly added memory."

**Lines 169-170 - Evolutionary Updates:**
> "After the memory is added and linked to other memories, the LLM is prompted to update the LLM-generated tags, keywords, and description based on the newly added memory. This results in an evolutionary approach where newly added memories are linked to older memories, which are in turn updated to be in line with the newly added memories."

**When to Use:**
- Knowledge management systems
- Research assistants
- Applications with interconnected concepts
- Long-running projects requiring memory evolution

---

### 4.3 Search-o1 (RAG During Reasoning)

**Lines 176-179:**
> "A recent approach to agentic RAG is search-o1, a method that attempts to retrieve relevant context and put it throughout the reasoning traces to enhance the reasoning LLM's capabilities further. Instead of autonomously searching for relevant information and using it in the prompt of the model, the information can be searched and retrieved during the LLM's reasoning process."

**Lines 179-180 - Token-Based Search:**
> "The Agent is instructed to use the `<|begin_search_query|>` and `<|end_search_query|>` tokens to start a search and then use the `<|begin_search_result|>` and `<|end_search_result|>` tokens to indicate what the retrieved information is."

**Lines 181-182 - Dynamic Refinement:**
> "By enabling RAG during reasoning, the model can iteratively refine its reasoning process until it is confident in the final result. This dynamic approach is different from regular agentic RAG because it can be done autonomously within a single call rather than iterating over calls."

**Lines 183-184 - Reason-in-Documents Module:**
> "A downside to simply embedding documents within the reasoning traces is that the retrieved documents can be quite large and often contain irrelevant information and may therefore disrupt the reasoning flow. To solve this issue, the authors extend the reasoning agentic RAG by incorporating a Reason-in-Documents module."

**Lines 184-185 - Context Compression:**
> "Using the search query, retrieved documents, and reasoning trace, this module attempts to condense all information into focused reasoning steps. The agent's same reasoning LLM is used to process the retrieved documents to align with the model's specific reasoning traces."

**Lines 190-193 - Example Usage:**
> "For instance, when given the query 'Why are flamingos pink?', it will search for relevant information in Wikipedia during its reasoning process. The first result it finds mentions that it is due to specific pigments in their specific diet. It will use that information during its reasoning until it needs further clarification. For instance, a second call to a different external database (e.g., ArXiv) will clarify that the specific pigments are carotenoid pigments, which are commonly found in brine shrimp."

**Lines 192-193 - Key Advantage:**
> "This iterative process of querying information and compressing it within its reasoning process allows the model to reason about information when it is retrieved rather than stuffing all potential relevant information in the context."

**When to Use:**
- Complex reasoning tasks requiring external knowledge
- Research-oriented queries
- Multi-hop reasoning across knowledge sources
- Applications where context needs to be dynamically refined

---

## 5. Context Engineering (Lines 194-243)

### 5.1 Definition and Scope

**Lines 196-209 - Context Components:**
> "However, there might be more forms of context that we could give to the Agent, like:
>
> - **System prompt:** The core context and rules for the agent, which define how it should behave (procedural memory).
> - **Conversation history:** Both the conversation between the user and assistant, but also the LLM's internal thoughts (working memory).
> - **Past experiences:** Storing specific events, actions, or observations from tool use or user-related facts (episodic memory).
> - **Retrieved information:** External information that is typically stored in a vector database and accessed through RAG-like techniques (semantic memory).
>
> This is not an exhaustive list, however. As the fields of LLMs and Agents grow, so do the sources of information that we could give to them."

**Lines 210-211:**
> "As such, we can provide the Agent with all kinds of information sources to produce the answer that we want. As illustrated in Figure 4-27, the user's query or prompt is a subset of the LLM's entire context."

**Lines 213-214 - LLM as Function:**
> "This context is given to the LLM, which in turn produces a list of tokens. As such, we can view an LLM as a function that takes several tokens (context), processes them, and outputs tokens."

**Lines 214-217 - Two Optimization Paths:**
> "To optimize the output tokens for a given task, we can either optimize the LLM itself by training or fine-tuning it, or we can optimize the input, namely the context (Figure 4-28)."

**Lines 216-217 - Formal Definition:**
> "The act of optimizing input tokens so they produce the best possible output is called context engineering. Formally, it is finding the best context such that it maximizes the quality of the LLM's output for a given task."

---

### 5.2 Why Context Engineering Matters

**Lines 221-225 - Long Context Limitations:**
> "Context windows have grown larger, to the point where Google's Gemini 1.5 already reached a context window of a million tokens in February 2024. It would be natural to conclude that context engineering means attempting to fill up this humongous context window with all kinds of information that relates to the task at hand. Moreover, there would be no more need for RAG since the context window is large enough to potentially hold your entire database."

**Lines 230-232 - RULER Benchmark Findings:**
> "The RULER paper, for instance, demonstrated models that performed well on the Needle In A Haystack test, all showed significant performance drops as the context length increased when applied to the RULER benchmark. Many others (e.g., 14 and 15) found similar results and concluded that arbitrarily filling up the context window of LLMs would hurt performance."

**Lines 232:**
> "Some even called it 'context rot', showcasing the importance of adding quality information."

**Lines 234-235 - Cost and Latency:**
> "Cost and latency are other reasons for managing the context window. You could theoretically stuff everything in a 2-million token context length, like your entire external database, the full conversation history, some additional examples, etc. However, the Agent's LLM has to process all these tokens, which significantly reduces latency."

**Lines 235:**
> "Costs also increase, considering more VRAM is needed when you increase the context length. Just dumping everything in the context is, therefore, a recipe for failure."

---

### 5.3 Context Engineering Principles

**Lines 236-238 - Three Dimensions:**
> "With context engineering, we aim to optimize the model's context window with the right information, at the right place, and in the right format. It is the act of giving the LLM the appropriate context without overwhelming it."

**Lines 238-239 - Strategic Placement:**
> "As such, and as shown in Figure 4-31, it is not about filling up the context window, but strategically choosing and placing information."

**Lines 239-240 - Balance:**
> "You do not want too much or too irrelevant information as the costs of compute go up and the performance goes down. Likewise, if you give the LLM too little context and in an inefficient form, it will operate without having a good understanding of the context."

**Lines 240-241 - Architectural Challenge:**
> "It is a careful balance of providing just enough relevant information to the LLM to have it perform optimally. In other words, context engineering is much of an architectural problem that needs to be solved with lots of moving parts, like efficiently tracking, storing, and retrieving all existing and created information."

**Lines 241-243 - Dynamic Memory Techniques:**
> "To help with context engineering, existing techniques for handling memory that focus on efficiency can be used. MemoryBank, for instance, dynamically adjusts the importance of memories and only keeps those that are truly important for the conversation history. Likewise, Search-o1 compresses the retrieved context and only gives back the relevant components without any noise."

---

## 6. Context Optimization Strategies

### 6.1 Context Tracking and Storage

**Lines 387-410 - What to Track:**
> "Although it may seem obvious at first, there are many types of information you can track:
>
> **Agent behavior:**
> - Tool usage by the agent (and any sub-agents)
> - Tool outputs and intermediate results
> - Interactions between (sub-)agents
> - Internal reasoning steps
> - Conversation history
> - Failures/successes
>
> **User behavior:**
> - User intent (explicit requests and goals)
> - User feedback (edits, approvals, rejections)
>
> **Knowledge sources:**
> - Snapshots of your proprietary database(s) for reproducibility and auditing
> - External documents (RAG, APIs, etc.)
> - Structured artifacts like PLAN.md, REQUIREMENTS.md, etc.
>
> **System-level:**
> - Configuration (LLM hyperparameters, available tools, etc.)
> - Policies (guardrails, constraints, etc.)"

---

### 6.2 Context Selection (Re-ranking)

**Lines 414-419 - Document Retrieval Problem:**
> "In RAG, the input documents are typically split into smaller parts, such as sentences or paragraphs, to isolate the information they contain and keep it to a single subject. However, when you then run a RAG pipeline, you typically get a collection of documents in return. For example, if we search a vector database for the 'causes of climate change,' the system might return documents about greenhouse gases, industrial activity, and deforestation. Although those documents might not directly answer our question, they are related."

**Lines 419-421 - Re-ranking:**
> "To improve this process, we can use a re-ranker to refine the set of documents that were retrieved. This technique, often a language model, takes in both the query and retrieved documents to re-rank the retrieved documents based on their relevance to the query and to each other (see Figure 4-32)."

**Lines 421-422 - Benefits:**
> "By providing the re-ranker with additional context (all retrieved documents), it can operate on far fewer documents than if we were to give it the entire database. Moreover, after the results have been re-ranked according to their relevance, we can choose to only keep the most relevant documents."

---

### 6.3 Context Compression

**Lines 426-430 - Summarization:**
> "The goal of context engineering is to find a balance between what you put in the context and how much. As such, compressing the context as much as possible is an important strategy for optimizing the context. A common way to handle compression is what we discussed at the beginning of this chapter, using an LLM to create summaries of your conversation history. As we explored in Search-o1, we can even compress the output of the RAG pipeline using an LLM to summarize the retrieved documents."

**Lines 431-433 - Maximal Marginal Relevance (MMR):**
> "Another method of compressing the context is by reducing redundancy. Even with a re-ranker, the top 5 most relevant results might all contain very similar documents. Together, they are not bigger than the sum of their parts but smaller instead because they contain similar information. As such, we do not only want the most relevant documents, but in a way that they are still documents that each contain a new piece of information."

**Lines 434-442 - MMR Process:**
> "A common technique to use, whether they are the output documents of your RAG pipeline or other pieces of retrieved information, is called Maximal Marginal Relevance (MMR). This technique uses a precalculated relevance vector and redundancy matrix to balance the diversity of documents.
>
> First, the similarity between the retrieved document and query embeddings is calculated. This results in a relevance vector which has a value per document to indicate how similar/relevant the given document is to the query (see Figure 4-33).
>
> Second, the similarity between the retrieved documents is likewise calculated to construct a similarity matrix called the redundancy matrix. This matrix is used to potentially discard documents that are too similar to the ones we had already chosen (see Figure 4-34)."

---

### 6.4 Context Ordering (Lost-in-the-Middle)

**Lines 450-453 - Position Effects:**
> "The order of the context is vital to the performance of your agent. Early research into the position of important information in prompts found that LLMs have a tendency to pay more attention to the beginning and end of a prompt. As a result, they often end up losing information in the middle, which they call the 'lost-in-the-middle' phenomenon."

**Lines 455-456 - Human Analogy:**
> "This tendency to focus on the beginning and end of prompts is similar to human behavior. The serial-position effect states that people generally recall the first (primacy effect) and last (recency effect) items in a series best, whereas the middle items are recalled worst."

**Key Takeaway:**
- Place critical information at the beginning or end of context
- Avoid burying important context in the middle
- Consider human-like attention patterns in LLMs

---

## 7. Context as Specification (Lines 457-466)

**Lines 457-461 - Shift in Mindset:**
> "Arguably, one of the most important things about context engineering is that it requires a shift in mindset. The context that is given to the agent can be seen as a tool for communication. Not just for the agent, but to the people that you work with. More specifically, the context that you give to the agent, including the query, PLAN.md, REQUIREMENTS.md, codebase, etc., all serve as a tool to communicate what your intention is. For example, when you allow a coding agent to fully create a PR on its own, it does not suffice to go through the code itself to check whether everything is there. The initial query, PLAN.md, etc., all serve as the initial specification of the PR and should be tracked as well."

**Lines 462-464 - Intention Tracking:**
> "As such, we can view the context of the agent as the specification of your feature. As agents are becoming more autonomous, it is important to track the intention of their behavior through the context that is given. Where we would view prompt engineering as user-facing, context engineering is a much more developer-oriented tool and requires careful communication of why the agent is executing certain tasks. The answer to the 'why' starts with the user's intention."

**Lines 464-465 - Importance of Input:**
> "Think about it like this: how strange it is that we tend to throw away the input to our function (the LLM) and only keep track of the output! Not only for reproducibility, but also for communication, it allows you to understand why the agent has chosen certain tools, executions, and outputs. Moreover, this transparency of intention also serves as a great tool for debugging your agent."

**Lines 465-466 - Domain Specificity:**
> "Context, as the specification, brings about significant potential for domain-specific industries. The context that you give an agent changes drastically between use cases and applications. Health care requires a completely different context than law, for instance. As such, there is not a single framework for context engineering and instead requires developers to consider their domain-specific knowledge sources, like patient data in health care and research papers in academia."

---

## 8. Summary Table: Memory Types Quick Reference

| Memory Type | Duration | Storage Location | Lines | Example Use Case |
|-------------|----------|------------------|-------|------------------|
| **Working Memory** | Short-term | Conversation history | 22-23 | Recent chat turns |
| **Episodic Memory** | Long-term | External database | 26-28 | Agent action history |
| **Semantic Memory** | Long-term | Vector database | 29-31 | Wikipedia, codebase |
| **Procedural Memory** | Persistent | System prompt | 32-34 | Behavior rules |
| **Parametric Memory** | Permanent | Model weights | 37-39 | Training knowledge |

---

## 9. Summary Table: Memory Management Techniques

| Technique | Type | Lines | When to Use | Trade-offs |
|-----------|------|-------|-------------|------------|
| **FIFO Trimming** | Short-term | 65-66 | Simple chatbots | May lose critical context |
| **Rolling Summarization** | Short-term | 68-72 | Long conversations | Requires LLM calls |
| **MemoryBank** | Long-term | 105-121 | Chatbots with user relationships | Complex implementation |
| **A-MEM** | Long-term | 146-170 | Knowledge management | High initial setup cost |
| **Search-o1** | Long-term | 176-193 | Reasoning tasks | Requires reasoning-capable LLMs |

---

## 10. Key Terminology Glossary

| Term | Definition | Lines |
|------|------------|-------|
| **Context Window** | Number of tokens LLM can process (input + output) | 50-53 |
| **Context Rot** | Performance degradation when context is too large | 232 |
| **Spaced Repetition** | Reinforcing memory through periodic recall | 110-111 |
| **Ebbinghaus Forgetting Curve** | Exponential memory decay over time | 109-110 |
| **Zettelkasten** | Note-taking method with atomic, linked notes | 146-148 |
| **Atomicity** | Each memory unit contains one piece of knowledge | 150-151 |
| **Hypertextual Notes** | Interconnected notes that reference each other | 152-154 |
| **Reason-in-Documents** | Processing retrieved docs to fit reasoning traces | 183-185 |
| **MMR (Maximal Marginal Relevance)** | Balance relevance and diversity in retrieval | 434-442 |
| **Lost-in-the-Middle** | LLMs lose info in middle of context | 450-453 |
| **Primacy Effect** | Better recall of items at the beginning | 455-456 |
| **Recency Effect** | Better recall of items at the end | 455-456 |

---

## 11. Cross-References for Tutorial Writing

**For Task 1.0 (memory_systems_fundamentals.md):**
- Use lines 22-23 for working memory definition
- Use lines 26-34 for long-term memory types
- Use lines 65-77 for short-term management techniques
- Use lines 105-193 for long-term patterns (MemoryBank, A-MEM, Search-o1)

**For Task 2.0 (context_engineering_tutorial.md):**
- Use lines 194-243 for context engineering overview
- Use lines 387-410 for context tracking
- Use lines 414-422 for re-ranking
- Use lines 426-442 for compression techniques
- Use lines 450-456 for ordering strategies
- Use lines 457-466 for "context as specification" philosophy

**For Task 3.0 (memory_patterns_notebook.ipynb):**
- Implement FIFO trimming (lines 65-66)
- Implement rolling summarization (lines 68-77)
- Demonstrate token budget management (lines 50-63)

**For Task 5.0 (backend/memory_systems.py):**
- Implement `calculate_token_usage()` based on lines 50-53
- Implement `fifo_trim()` based on lines 65-66
- Implement `rolling_summarize()` based on lines 68-77
- Add docstrings citing specific line numbers

---

## 12. Validation Checklist for Task 1.0

Use this checklist when validating `memory_systems_fundamentals.md`:

- [ ] Five memory types defined (lines 22-23, 26-34, 37-39)
- [ ] Flamingo example cited (lines 44-48)
- [ ] Short-term techniques explained (lines 65-77)
- [ ] MemoryBank cited (lines 105-121)
- [ ] A-MEM cited (lines 146-170)
- [ ] Search-o1 cited (lines 176-193)
- [ ] Context engineering overview (lines 194-243)
- [ ] All line numbers verified manually
- [ ] Cross-references match file structure

---

**Document Status:** ✅ Complete
**Lines Analyzed:** 516/516 (100%)
**Citations Extracted:** 50+ with exact line numbers
**Next Step:** Proceed to Task 0.2 (COMPASS metrics extraction)
