---
name: genai-safeguards
description: Framework-agnostic safeguard patterns for GenAI applications. Use when building LLM-powered systems that need risk mitigation, hallucination detection, content safety, or controlled generation. Patterns include Template Generation (pre-reviewed templates for high-volume comms), Assembled Reformat (two-phase content for accuracy), Self-Check (confidence scoring via logprobs), and Guardrails (input/output protection chains). Triggers on terms like safeguards, guardrails, hallucination detection, content safety, template generation, risk mitigation, PII protection, or when building production GenAI systems.
---

# GenAI Safeguards

Four production-ready patterns for building safer GenAI applications. Each pattern addresses specific risk profiles and can be composed together.

## Pattern Selection

| Risk Profile | Pattern | Use When |
|-------------|---------|----------|
| High-volume customer comms | **Template Generation** | Brand risk high, volume makes per-item review impossible |
| Accurate content presentation | **Assembled Reformat** | Facts must be grounded, presentation must be appealing |
| Factual response validation | **Self-Check** | Need confidence scores, hallucination detection |
| Comprehensive protection | **Guardrails** | Security, PII, content moderation, alignment |

## Quick Decision Tree

```
Is content customer-facing with brand risk?
├─ Yes → Can you enumerate all variations?
│        ├─ Yes → Template Generation (Pattern 29)
│        └─ No  → Assembled Reformat (Pattern 30)
└─ No  → Is factual accuracy critical?
         ├─ Yes → Self-Check (Pattern 31)
         └─ No  → Do you need input/output protection?
                  └─ Yes → Guardrails (Pattern 32)
```

## Pattern References

Load the appropriate reference based on your use case:

- **Template Generation**: See [references/template-generation.md](references/template-generation.md) for pre-reviewed template workflows
- **Assembled Reformat**: See [references/assembled-reformat.md](references/assembled-reformat.md) for two-phase content creation
- **Self-Check**: See [references/self-check.md](references/self-check.md) for confidence scoring and hallucination detection
- **Guardrails**: See [references/guardrails.md](references/guardrails.md) for input/output protection chains

## Scripts

Utility functions invokable by any agent:

| Script | Purpose |
|--------|---------|
| `scripts/template_manager.py` | Template CRUD, placeholder replacement, validation |
| `scripts/content_assembler.py` | Data assembly + reformat pipeline |
| `scripts/confidence_scorer.py` | Logprob analysis, perplexity calculation |
| `scripts/guardrail_chain.py` | Composable scanner chain framework |

## Composition Patterns

Patterns can be layered for defense-in-depth:

```
User Input → Guardrails (input) → Template Generation → Guardrails (output) → User
User Input → Guardrails (input) → Assembled Reformat → Self-Check → Guardrails (output) → User
```

## Integration Points

All patterns expose standard interfaces for orchestration frameworks:

```python
# Standard pattern interface
class SafeguardPattern:
    def validate(self, input: Any) -> ValidationResult
    def execute(self, input: Any) -> ExecutionResult
    def get_confidence(self) -> float  # 0.0-1.0
```

Compatible with LangChain, LangGraph, LlamaIndex, or direct API calls.
