# Polya-Style Analysis: Agentic Bank Dispute Chatbot Plan

## 1. Have You Seen This Problem Before?

**Yes.** This is a classic **"wrap existing API with conversational AI"** pattern. Similar implementations:

- **Stripe's dispute dashboard** → Already provides the domain model this plan borrows
- **Banking chatbots** (Bank of America's Erica, Capital One's Eno) → Same regulatory compliance challenges
- **Enterprise MCP implementations** → Salesforce, Zendesk integrations with Claude

**Key insight**: The 70% backend readiness claim is accurate—the dispute schema is mature.

---

## 2. Related Problems & Useful Theorems

| Related Pattern | Application Here |
|-----------------|------------------|
| **State Machine for Dialogue** | Dispute lifecycle (needs_response → under_review → won/lost) maps directly to conversation states |
| **Command Pattern** | Each MCP tool is a command wrapping API calls |
| **Facade Pattern** | MCP layer simplifies complex Step Functions workflow |
| **PCI DSS Tokenization** | Already solved in `dispute_types.ts:118-160` |

**Theorem equivalent**: The existing OpenAPI spec (`openapi.yaml:938 lines`) serves as a formal specification—MCP tools are essentially typed function wrappers.

---

## 3. The Unknown: What's Actually Hard?

The true unknowns aren't in the plan's Phase 1-2, but in:

1. **Slot-filling ambiguity**: "I see a weird charge" → which of 50 transactions?
2. **Multi-intent turns**: "Check my dispute AND file a new one"
3. **Error recovery**: What happens when the LLM hallucinates a dispute_id?

---

## 4. Related Solved Problems to Borrow From

| Solved Problem | Borrowable Element |
|----------------|-------------------|
| **Stripe CLI** | Argument validation, error messages |
| **AWS Step Functions ASL** | Already exists at `step-functions.asl.json` |
| **Reg E timeline calculator** | `reg_e_timelines.ts` is complete—just wrap it |

**Recommendation**: The `fraud_detector.py` (80% complete) can be called directly via MCP rather than reimplementing.

---

## 5. Auxiliary Elements to Introduce

The plan is missing:

| Missing Element | Why Needed |
|-----------------|-----------|
| **Idempotency keys** | Prevent duplicate dispute filing on retry |
| **Conversation summarization** | Long sessions exceed context limits |
| **Rollback mechanism** | If evidence submission fails mid-way |
| **Rate limiting per customer** | Prevent abuse of fraud_score tool |

---

## 6. Restating the Problem Differently

**Current framing**: "Build a chatbot with 6 tools"

**Better framing**: "Create a typed RPC layer that translates natural language into validated API calls with regulatory guardrails"

This reframe clarifies:
- The LLM is just a parser/generator
- The MCP tools are the actual interface
- Validation happens at the tool layer, not the LLM layer

---

## 7. More Accessible Related Problems

| Simpler Version | What It Teaches |
|-----------------|-----------------|
| **Single-tool bot** (just `check_status`) | Proves the MCP→API path works |
| **CLI instead of chat** | Validates tool schemas without LLM complexity |
| **Mock LLM responses** | Test tool layer independently |

**Recommendation**: Build Phase 1 tools as a CLI first, then add LLM.

---

## 8. Solving Part of the Problem

The plan can be decomposed:

| Phase | Scope | Timeline |
|-------|-------|----------|
| Week 1 | `file_dispute` + `check_status` only | Covers 60% of use cases |
| Week 2 | Add `compliance_deadline` | Regulatory requirement |
| Week 3-4 | Evidence and transaction lookup | Full feature set |

This gets an MVP faster than the proposed 10-14 weeks.

---

## 9. Deriving Useful Insights from the Data

From the architecture diagram and tool specs:

- **6 tools × ~50 lines each = ~300 lines** of core MCP code
- **PCI guardrails**: ~100 lines (regex + Luhn)
- **NLG templates**: 4 templates × ~30 lines = ~120 lines

**Total new code for MVP**: ~600-800 lines, not a massive undertaking.

---

## 10. Did the Plan Use All Data?

**Underutilized assets**:

| Asset | Current Use | Potential |
|-------|-------------|-----------|
| `dispute_classifier.py` | Mentioned but not integrated | Could pre-classify intent before LLM |
| `visa_vrol_types.ts` (80%) | Listed but not in tools | Add `get_network_status` tool |
| Balance transactions ledger | Not mentioned in tools | Add `get_credit_history` tool |

**Missing condition**: The plan doesn't address **partial disputes** (disputing $100 of a $500 charge), though the schema supports it via `amount_cents`.

---

## Summary Recommendations

1. **Reduce scope**: Start with 3 tools (file, check, deadline) → MVP in 4-6 weeks
2. **Add CLI mode**: Validate tools without LLM dependency
3. **Borrow more**: Reuse `fraud_detector.py` directly instead of wrapping
4. **Address the hard parts earlier**: Slot-filling and multi-intent resolution in Week 3, not Phase 2
5. **Missing safeguards**: Add idempotency, rate limiting, conversation summarization

---

*Analysis Date: December 2024*
*Method: Polya's Problem-Solving Heuristics*
*Related Document: `agentic_chatbot_implementation_plan.md`*
