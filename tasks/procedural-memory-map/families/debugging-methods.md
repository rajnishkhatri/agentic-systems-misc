# Debugging Methods Family

**When to use this family**: System has known issues, need root cause analysis, production incident response, bottleneck identification

---

## Overview

Debugging methods help **diagnose and fix failures** in LLM systems. Use when:
- ✅ System produces incorrect outputs
- ✅ Need to identify where pipeline breaks
- ✅ Want to prioritize which failures to fix
- ✅ Investigating production incidents

---

## Techniques in This Family

### 1. Data Preprocessing (Lesson 4)
**Purpose**: Clean raw logs into structured format

**Common issues handled**:
- Malformed JSON in CSV cells
- Escaped quotes and special characters
- Nested data structures
- Missing or incomplete fields

**Output**: Clean JSON traces ready for analysis

---

### 2. Trace Inspection (Lesson 7)
**Purpose**: Manual review of conversation traces

**When to use**:
- Investigating specific user-reported issues
- Understanding edge cases
- Validating automated analysis
- Safety-critical failure review

**Workflow**:
```
Raw logs → CSV conversion → Spreadsheet review → Annotation → Analysis
```

---

### 3. State-Based Modeling (HW5)
**Purpose**: Model multi-step agent as state machine

**Process**:
1. Identify all states in pipeline
2. Define transitions (normal flow)
3. Document what each state does
4. Identify possible failure points

**Example** (Recipe agent):
```
States:
1. ParseRequest (LLM) → Interpret user message
2. PlanToolCalls (LLM) → Decide which tools
3. GenRecipeArgs (LLM) → Construct search arguments
4. GetRecipes (Tool) → Execute search
5. ComposeResponse (LLM) → Draft answer
6. DeliverResponse (System) → Send to user

Transitions:
ParseRequest → PlanToolCalls → GenRecipeArgs → GetRecipes → ComposeResponse → DeliverResponse
```

---

### 4. Transition Matrix Analysis (HW5)
**Purpose**: Identify where agent pipeline fails most often

**Data structure**: Matrix where cell (i,j) = # of failures transitioning from state i to state j

**Analysis**:
```
Row sums: Which successful state precedes most failures
Column sums: Which failing state occurs most often (bottleneck) ✅
Cell values: Specific problematic transitions
```

**Example**:
```
                First Failure →
           Parse  Plan  GenRec  GetRec  Compose
Last     ┌─────────────────────────────────────┐
Success  │                                     │
  ↓      │                                     │
Parse    │   0     3      0       0       0   │
Plan     │   0     0      5       0       2   │
GenRec   │   0     0      0      22       0   │ ← High frequency
GetRec   │   0     0      0       0       8   │
         └─────────────────────────────────────┘
```

**Insight**: GenRec → GetRec transition fails 22 times → Recipe search tool issues

---

### 5. Bottleneck Identification (HW5)
**Purpose**: Prioritize which states to fix

**Method**:
```
1. Sum column values (total failures per state)
2. Identify top 2-3 bottleneck states
3. Distinguish LLM vs Tool failures
4. Propose targeted improvements
```

**Example analysis**:
```
GetRecipes: 30 failures (22 from GenRec, 8 from GetRec)
→ Root cause: Recipe search tool returns empty results
→ Proposed fix: Improve query fallback handling, better error messages

ComposeResponse: 10 failures
→ Root cause: LLM struggles with conflicting requirements
→ Proposed fix: Add constraint validation before composition
```

---

## Debugging Workflow

### Phase 1: Symptom Identification
```
User reports: "Bot suggested non-vegan recipe for vegan query"
↓
Reproduce: Run query, confirm failure
↓
Classify: Dietary restriction violation
```

### Phase 2: Trace Collection
```
1. Export traces with similar symptoms (e.g., dietary violations)
2. Convert to CSV for review (Lesson 7)
3. Sample 10-20 traces for manual inspection
```

### Phase 3: Pattern Analysis
```
Manual review (Lesson 7):
- All failures occur after recipe retrieval
- Tool returns recipes without dietary metadata
- LLM cannot filter by restrictions

Hypothesis: Retrieval tool missing dietary filter parameter
```

### Phase 4: Root Cause Confirmation
```
If agent pipeline:
  → Build transition matrix (HW5)
  → Identify bottleneck state
  → Review tool implementation

If retrieval system:
  → Measure Recall@k (HW4)
  → Analyze failed queries
  → Check vocabulary mismatch

If response quality:
  → Use substantiation evaluation (Lesson 4)
  → Check for hallucinations
```

### Phase 5: Fix & Validate
```
1. Implement fix (e.g., add dietary filter to tool)
2. Re-run test queries
3. Measure improvement (before/after metrics)
4. Deploy to production
5. Monitor for regression
```

---

## Debugging Techniques by Problem Type

### Problem: Agent Returns Wrong Answer

**Technique**: Substantiation Evaluation (Lesson 4)

**Check**:
- Are claims grounded in tool outputs?
- Is agent hallucinating information?
- Is tool returning incorrect data?

**Example**:
```
User: "Is apartment A11 available?"
Tool output: {"id": "A11", "available": true}
Agent: "Yes, A11 is available with a balcony"
                                  ↑
                            UNSUBSTANTIATED (balcony not in tool output)
```

---

### Problem: Agent Fails Frequently

**Technique**: Transition Matrix Analysis (HW5)

**Steps**:
1. Collect 100+ failure traces
2. Build transition matrix
3. Identify bottleneck state (highest column sum)
4. Review code for that state
5. Fix and validate

---

### Problem: Retrieval Returns Irrelevant Results

**Technique**: Error Pattern Analysis + Query Rewrite (HW4)

**Steps**:
1. Measure Recall@k on failed queries
2. Identify patterns (e.g., all failures use rare vocabulary)
3. Test query rewrite strategies
4. Measure improvement

---

### Problem: User Reports Specific Issue

**Technique**: Trace Inspection (Lesson 7)

**Steps**:
1. Export specific trace
2. Convert to readable format (CSV)
3. Manual review of conversation + tool calls
4. Identify exact failure point
5. Check if isolated incident or systemic pattern

---

## Root Cause Categories

### 1. LLM Failures
**Symptoms**: Wrong argument generation, poor prompt following

**Debugging**:
- Review LLM outputs in traces
- Check prompt clarity
- Test with different temperatures
- Try few-shot examples

**Fix**: Improve prompts, add validation, use better model

---

### 2. Tool Failures
**Symptoms**: Empty results, errors, timeouts

**Debugging**:
- Check tool API responses in traces
- Verify arguments are valid
- Test tool independently
- Check API rate limits/quotas

**Fix**: Improve error handling, add retries, validate arguments before calling

---

### 3. Retrieval Failures
**Symptoms**: Low Recall@k, wrong documents

**Debugging**:
- Measure Recall@k on failed queries
- Analyze vocabulary mismatch
- Check document preprocessing

**Fix**: Query rewrite, hybrid retrieval, reranking

---

### 4. Logic Errors
**Symptoms**: Correct data, wrong conclusion

**Debugging**:
- Review reasoning steps in traces
- Check for contradictory constraints
- Test edge cases

**Fix**: Add validation logic, improve prompt reasoning, use chain-of-thought

---

## Debugging Anti-Patterns

### ❌ Only Looking at Failures
**Problem**: Missing why some queries succeed

**Solution**: Review successful traces too, identify differences

### ❌ No Baseline Metrics
**Problem**: Don't know if "10 failures" is bad (10% or 0.1%?)

**Solution**: Always measure baseline success rate first

### ❌ Fixing Symptoms, Not Root Cause
**Problem**: Patching individual failures without understanding pattern

**Solution**: Use transition matrices or error pattern analysis

### ❌ No Validation After Fix
**Problem**: Assuming fix works without testing

**Solution**: Re-run failed queries, measure improvement quantitatively

---

## Trace Inspection Best Practices

### What to Look For

**In user messages**:
- Ambiguity or contradictory requirements
- Rare vocabulary or domain-specific terms
- Edge cases (e.g., "vegan cheeseburger")

**In tool calls**:
- Are arguments valid?
- Are results relevant?
- Are errors handled gracefully?

**In agent responses**:
- Do they address user query?
- Are claims substantiated by tool outputs?
- Is formatting appropriate?

### Annotation Template

```csv
trace_id, failure_mode, root_cause, severity, proposed_fix
trace_001, dietary_violation, tool_missing_filter, high, add_dietary_param
trace_002, retrieval_empty, rare_vocabulary, medium, query_rewrite
trace_003, logic_error, contradictory_constraints, low, add_validation
```

---

## Integration with Other Families

### Debugging → Qualitative
1. Trace inspection identifies patterns
2. Open coding (HW2) structures findings
3. Build failure taxonomy

### Debugging → Quantitative
1. Transition matrix provides frequencies
2. Calculate failure rates per state
3. Prioritize by impact (frequency × severity)

### Debugging → Automated Evaluation
1. Identify failure modes through debugging
2. Create labeled dataset
3. Build LLM-as-Judge (HW3) for monitoring

---

## Real-World Example

**Scenario**: Recipe agent failing on dietary restriction queries

### Step 1: Symptom
```
User reports: "Bot suggested honey for vegan recipe"
Reproduced: Yes, failure confirmed
```

### Step 2: Trace Collection
```
Collected 50 traces with dietary restriction queries
Converted to CSV (Lesson 7)
Manual review of 10 traces
```

### Step 3: Pattern Analysis
```
Finding: All 8 vegan failures occur after GetRecipes tool call
Tool returns recipes without dietary metadata
LLM cannot filter based on restrictions
```

### Step 4: Transition Matrix (HW5)
```
Built matrix from 100 failure traces:
GenRecipeArgs → GetRecipes: 22 failures (highest)
Bottleneck identified: Recipe retrieval tool
```

### Step 5: Root Cause
```
Reviewed tool implementation:
- search_recipes(query, limit=5)
- Missing parameter: dietary_restrictions

Root cause: Tool API doesn't support dietary filtering
```

### Step 6: Fix Options
```
Option A: Add dietary parameter to tool API
  Effort: High (backend changes)
  Impact: Solves problem at source ✅

Option B: Post-filter results in LLM
  Effort: Low (prompt change)
  Impact: Unreliable (LLM might miss violations)

Option C: Pre-filter with keyword matching
  Effort: Medium
  Impact: Brittle (misses synonyms)

Decision: Option A (worth the effort)
```

### Step 7: Validation
```
After fix:
- Re-tested 50 dietary queries
- Before: 8/10 vegan queries failed (80% failure)
- After: 0/10 vegan queries failed (0% failure) ✅
- Deployed to production
```

### Step 8: Monitoring
```
Set up weekly check:
- Sample 100 dietary queries
- Measure with substantiation judge (Lesson 4)
- Alert if failure rate >5%
```

---

## Debugging Checklist

**Before fixing**:
- [ ] Reproduced failure consistently
- [ ] Collected 10-20 traces showing issue
- [ ] Identified pattern (not isolated incident)
- [ ] Measured baseline failure rate
- [ ] Formed hypothesis about root cause

**During fix**:
- [ ] Implemented minimal fix (not over-engineering)
- [ ] Added tests for failure case
- [ ] Validated fix on collected traces

**After fix**:
- [ ] Re-measured failure rate (quantitative improvement)
- [ ] Deployed to staging first
- [ ] Set up monitoring for regression
- [ ] Documented root cause and fix

---

## Further Reading

**From tutorials**:
- [HW5: Transition Matrix Analysis](../../homeworks/hw5/TUTORIAL_INDEX.md)
- [Lesson 4: Substantiation Evaluation](../../lesson-4/TUTORIAL_INDEX.md)
- [Lesson 7: Trace Inspection](../../lesson-7/TUTORIAL_INDEX.md)
- [HW2: Error Pattern Coding](../../homeworks/hw2/TUTORIAL_INDEX.md)

**Debugging principles**:
- "The Pragmatic Programmer" (Hunt & Thomas)
- "Debugging" (Agans, 2006)
