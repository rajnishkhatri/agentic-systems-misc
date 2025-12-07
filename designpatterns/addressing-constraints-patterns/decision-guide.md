# Pattern Selection Decision Guide

## Decision Flowchart

Use this flowchart to select the right pattern for your use case.

```
START: What does your AI system need to do?
│
├─▶ [Access external data/APIs?]
│   │
│   ├─▶ YES ─▶ [Is it a simple function call?]
│   │         │
│   │         ├─▶ YES ─▶ ★ TOOL CALLING (Pattern 21)
│   │         │         └─▶ Use MCP for standardization
│   │         │
│   │         └─▶ NO ─▶ [Needs DSL (SQL, graphs)?]
│   │                   │
│   │                   ├─▶ YES ─▶ ★ CODE EXECUTION (Pattern 22)
│   │                   │         └─▶ Use sandbox + validation
│   │                   │
│   │                   └─▶ NO ─▶ [Multiple reasoning steps?]
│   │                             │
│   │                             └─▶ YES ─▶ ★ ReAct
│   │                                       └─▶ Tool Calling + CoT
│   │
│   └─▶ NO ─▶ [Multiple specialized domains?]
│             │
│             ├─▶ YES ─▶ [Need to route requests?]
│             │         │
│             │         ├─▶ YES ─▶ ★ ROUTER PATTERN
│             │         │         └─▶ Classifier + Specialized Agents
│             │         │
│             │         └─▶ NO ─▶ [Need multiple perspectives?]
│             │                   │
│             │                   ├─▶ YES ─▶ ★ MULTIAGENT COLLABORATION
│             │                   │         │
│             │                   │         ├─▶ [Hierarchy needed?] ─▶ Executive-Worker
│             │                   │         ├─▶ [Equal voices?] ─▶ Peer-to-Peer
│             │                   │         └─▶ [Dynamic assignment?] ─▶ Market-Based
│             │                   │
│             │                   └─▶ NO ─▶ [Linear dependencies?]
│             │                             │
│             │                             └─▶ YES ─▶ ★ SEQUENTIAL WORKFLOW
│             │
│             └─▶ NO ─▶ [Standard LLM response sufficient]
│                       └─▶ No agentic pattern needed
│
└─▶ [High security requirements?]
    │
    ├─▶ YES ─▶ Choose security pattern:
    │         │
    │         ├─▶ [No feedback to LLM?] ─▶ Action-Selector
    │         ├─▶ [Fixed plan needed?] ─▶ Plan-Then-Execute
    │         ├─▶ [Untrusted data?] ─▶ Dual-LLM or Map-Reduce
    │         └─▶ [Minimize attack surface?] ─▶ Context-Minimization
    │
    └─▶ NO ─▶ Continue with standard pattern
```

## Quick Reference Matrix

| Your Need | Primary Pattern | Secondary Patterns | Complexity |
|-----------|-----------------|-------------------|------------|
| Real-time data (weather, stocks) | Tool Calling | ReAct | Low |
| Database queries | Code Execution | Tool Calling | Medium |
| Graph/chart generation | Code Execution | - | Medium |
| Multi-step reasoning | ReAct | Tool Calling + CoT | Medium |
| Domain routing | Router | - | Low |
| Linear processing | Sequential Workflow | - | Low |
| Multiple perspectives | Multiagent (Peer) | Review Panel | High |
| Task delegation | Multiagent (Hierarchical) | Executive-Worker | High |
| Dynamic assignment | Multiagent (Market) | Auction | High |
| Untrusted input handling | Dual-LLM | Map-Reduce | High |
| Maximum security | Plan-Then-Execute | Action-Selector | High |

## Pattern Combinations

### Common Combinations

```
┌─────────────────────────────────────────────────────────────┐
│ RESEARCH ASSISTANT                                          │
│ ┌─────────┐   ┌─────────┐   ┌─────────┐   ┌─────────┐      │
│ │ Router  │──▶│  ReAct  │──▶│ Review  │──▶│ Output  │      │
│ │(classify)│  │(search) │   │ Panel   │   │(format) │      │
│ └─────────┘   └─────────┘   └─────────┘   └─────────┘      │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ DATA ANALYSIS PIPELINE                                       │
│ ┌─────────┐   ┌─────────┐   ┌─────────┐   ┌─────────┐      │
│ │  Code   │──▶│ Execute │──▶│Validate │──▶│Visualize│      │
│ │  Gen    │   │(sandbox)│   │(review) │   │ (code)  │      │
│ └─────────┘   └─────────┘   └─────────┘   └─────────┘      │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ SECURE ENTERPRISE AGENT                                      │
│ ┌─────────┐   ┌─────────┐   ┌─────────┐   ┌─────────┐      │
│ │Dual-LLM │──▶│Plan-Then│──▶│ Human   │──▶│Execute  │      │
│ │(sanitize)│  │-Execute │   │ Review  │   │(action) │      │
│ └─────────┘   └─────────┘   └─────────┘   └─────────┘      │
└─────────────────────────────────────────────────────────────┘
```

## Anti-Patterns to Avoid

| Anti-Pattern | Problem | Solution |
|--------------|---------|----------|
| Too Many Tools | Model accuracy drops with >10 tools | Use Router to split into specialized agents |
| Unvalidated Code | Security risk, crashes | Always sandbox + validate before execute |
| Infinite ReAct Loops | Never terminates | Set max iterations + completion criteria |
| Oversharing Context | Prompt injection risk | Use Context Minimization |
| No Human Escape | Can't recover from errors | Add Human-in-the-Loop escalation |
| Monolithic Agents | Hard to debug, maintain | Decompose into specialized agents |
| Synchronous Chains | Slow execution | Parallelize independent steps |

## Latency Considerations

| Pattern | Typical Latency | Optimization |
|---------|-----------------|--------------|
| Tool Calling (1 tool) | 2-5 seconds | Cache common queries |
| ReAct (3-5 steps) | 10-30 seconds | Parallelize independent tools |
| Sequential (3 steps) | 6-15 seconds | Combine simple steps |
| Multiagent (3 agents) | 15-45 seconds | Run in parallel where possible |
| Review Panel (5 agents) | 30-90 seconds | Limit discussion rounds |

## Cost Considerations

| Pattern | Token Usage | Cost Optimization |
|---------|-------------|-------------------|
| Tool Calling | Low-Medium | Minimize tool descriptions |
| Code Execution | Medium | Use smaller models for code gen |
| ReAct | Medium-High | Limit max iterations |
| Sequential | Medium | Minimize context passing |
| Multiagent | High | Use smaller models for workers |
| Review Panel | Very High | Limit rounds, use summaries |

## Pattern Selection by Use Case

### Customer Service Bot
```
Primary: Router → Specialized Agents
Secondary: Tool Calling (CRM, Orders)
Security: Action-Selector (limit actions)
Human: Escalation for complex issues
```

### Code Generation Assistant
```
Primary: Code Execution
Secondary: ReAct (for research)
Security: Sandbox + Validation
Human: Review for production code
```

### Research & Analysis
```
Primary: ReAct (search + reason)
Secondary: Review Panel (quality)
Security: Context Minimization
Human: Final approval
```

### Content Creation Pipeline
```
Primary: Sequential Workflow
Secondary: Review Panel
Security: Standard (low risk)
Human: Editorial review
```

### Enterprise Automation
```
Primary: Multiagent (Hierarchical)
Secondary: Tool Calling (APIs)
Security: Dual-LLM + Plan-Then-Execute
Human: Approval for high-stakes actions
```

## Failure Recovery Strategies

| Failure Type | Detection | Recovery |
|--------------|-----------|----------|
| Tool timeout | Async timeout | Retry with backoff |
| Code execution error | Exit code ≠ 0 | Reflection → retry |
| Agent disagreement | Voting deadlock | Escalate to human |
| Context overflow | Token count | Summarize + continue |
| Infinite loop | Iteration count | Force termination |
| Injection detected | Pattern matching | Reject + log |

## Implementation Checklist

### Before Building
- [ ] Identified primary pattern for use case
- [ ] Documented tool requirements
- [ ] Defined success criteria
- [ ] Planned failure modes
- [ ] Chose security patterns

### During Development
- [ ] Implemented with framework (LangGraph, AG2, etc.)
- [ ] Added timeout limits
- [ ] Implemented retry logic
- [ ] Added logging for debugging
- [ ] Created test cases

### Before Deployment
- [ ] Load tested multiagent coordination
- [ ] Tested prompt injection defenses
- [ ] Verified human escalation works
- [ ] Documented failure recovery
- [ ] Set up monitoring
