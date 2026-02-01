# Companion Guide: Error Analysis Deep Dive (Open Coding, Axial Coding, Synthetic Data)

**Companion to:** `lesson-33/03_error_analysis_deep_dive.md`  
**Purpose:** Provide a practical, org-ready playbook for (1) open coding, (2) converting open codes to axial codes, and (3) dimension-based synthetic data generation—especially for teams using **LangSmith** traces.

---

## How to use this companion

- **If your org is new to qualitative coding:** start with **Open Coding (Practical + Origins)**, then go to **Open → Axial Conversion Framework**.
- **If you already have traces in LangSmith:** use **LangSmith Worksheet** to standardize annotation and evidence capture.
- **If you need data before production logs exist:** use **Dimension-Based Generation SOP** to create synthetic queries and materialize traces.

---

## Open Coding (deeper explanation)

### What open coding is (in plain language)

**Open coding** is the first-pass process of reading raw data (traces, transcripts, tickets) and writing **short observational labels** (“codes”) for what is happening—*what you see*, not *why you think it happened*.

In LLM app error analysis, open coding typically means:
- Read a full **trace** end-to-end.
- Identify the **first upstream failure** (the earliest meaningful deviation from user intent or system contract).
- Write a short, falsifiable note like: “Dropped budget constraint in tool args”.

### Where open coding came from (origin)

Open coding is rooted in **Grounded Theory**, a qualitative research methodology associated with:
- **Glaser & Strauss (1967)**: theory discovery from data via the **constant comparative method**
- **Strauss & Corbin**: formalized common terminology around **open / axial / selective** coding
- Later practitioners (e.g., **Charmaz**) emphasized practical techniques like **line-by-line coding**, **gerunds**, and **memoing**

Useful starting references (optional reading):
- Glaser & Strauss (1967), *The Discovery of Grounded Theory*: `https://api.taylorfrancis.com/content/books/mono/download?identifierName=doi&identifierValue=10.4324%2F9780203793206&type=googlepdf`
- Charmaz coding chapter PDF: `https://projects.iq.harvard.edu/files/socseniorthesis/files/charmaz_ch3_coding_grounded_theory.pdf`
- Saldaña excerpt (in vivo coding): `https://www.sfu.ca/~palys/Saldana-CodingManualForQualResearch-IntroToCodes&Coding.pdf`

### Why open coding helps (what it fixes)

- **Defeats confirmation bias:** you stop forcing traces into generic buckets (“hallucination”) and instead capture application-specific failures (“approved refund without policy grounding”).
- **Discovers “unknown unknowns”:** novel failure modes emerge that you did not anticipate.
- **Becomes actionable:** well-phrased open codes point to specific fixes (routing, tool schema validation, retrieval grounding, state tracking).

### Mechanics: how to write good open codes

**Rule 1: Code WHAT, memo WHY**
- Open code (WHAT): “Approved refund without policy grounding”
- Memo (WHY hypothesis): “Tool router skipping policy lookup”

**Rule 2: Prefer first-failure coding during taxonomy discovery**
Downstream symptoms often vanish after fixing the upstream error.

**Rule 3: Make codes falsifiable**
Another reviewer should be able to confirm the code using a small evidence snippet.

**Useful code styles (mix-and-match)**
- **Concrete error codes:** “Malformed JSON tool args”
- **Gerund/action codes:** “Relaxing constraints without approval”
- **In vivo codes:** use user’s phrase when it carries meaning (“quick and clean”)

---

## LangSmith-ready open coding worksheet (trace/run-tree friendly)

LangSmith traces are **run trees**. Your “trace_id” is usually the **root run id**, but the first failure often appears in a **child run** (LLM/tool/retriever).

### Recommended columns (spreadsheet or JSONL)

#### 1) Identity & pointers
- `project_name`
- `root_run_id`
- `root_run_url`
- `timestamp`
- `tags` (e.g., `prod`, `synthetic`, `refunds`, `tool-use`)
- `app_version` (git SHA; store in LangSmith metadata)

#### 2) Context
- `user_intent_short` (5–10 words)
- `trace_summary` (1–2 sentences)

#### 3) First failure localization (LangSmith-specific)
- `first_failure_run_id`
- `first_failure_run_name` (e.g., `Agent`, `Retriever`, `refund_policy_tool`)
- `first_failure_run_type` (`llm` / `tool` / `retriever` / `chain`)
- `first_failure_step` (choose one):
  - `intent_parse` / `planning` / `retrieval` / `tool_selection` / `tool_args` / `tool_execution` / `tool_result_use` / `response` / `safety`
- `evidence_snippet` (copy/paste minimal proof from run inputs/outputs/errors)

#### 4) Open code + severity
- `open_code_label` (5–15 words, observational)
- `severity`:
  - `S0` cosmetic
  - `S1` friction
  - `S2` wrong outcome / policy risk
  - `S3` unsafe / irreversible / high-cost
- `user_impact` (1 sentence)

#### 5) Memo (hypothesis → fix → regression)
- `memo_hypothesis`
- `memo_fix_idea`
- `memo_regression_test`

#### 6) Axial coding hooks (fill later)
- `axial_category`
- `subcategory` (optional)
- `pass_fail` (binary)
- `category_notes` (boundary conditions)

### Copy/paste CSV headers

```text
project_name,root_run_id,root_run_url,timestamp,tags,app_version,user_intent_short,trace_summary,first_failure_run_id,first_failure_run_name,first_failure_run_type,first_failure_step,evidence_snippet,open_code_label,severity,user_impact,memo_hypothesis,memo_fix_idea,memo_regression_test,axial_category,subcategory,pass_fail,category_notes
```

---

## Framework: converting Open Codes → Axial Coding (for a new org)

### Goal (what axial coding produces)

Axial coding converts many “messy” open codes into a **small set of stable categories** (“failure modes”), each with:
- clear definition
- pass/fail criteria
- boundaries (include/exclude rules)
- examples + evidence snippets
- typical fixes + regression tests

### Step-by-step conversion workflow

#### Step 1: Normalize open codes
- Merge synonyms (“ignored constraint” vs “dropped constraint”)
- Remove root-cause speculation from code labels
- Standardize format (recommended): **Verb + Object + Context**

Deliverable: a list of unique open codes + counts + example traces.

#### Step 2: Choose your grouping rule (recommendation: “same fix → same category”)
If two open codes are solved by the same intervention type, they likely belong together.

Deliverable: one sentence like “We cluster failures primarily by fix type.”

#### Step 3: Fast clustering pass
Cluster codes into piles without naming them yet.

Heuristics:
- If you can’t explain the difference between two piles in one sentence, merge them.
- If one pile implies two distinct fix paths, split it.

Deliverable: 8–20 rough clusters.

#### Step 4: Name categories + write one-line definitions
Names should be short noun phrases (e.g., “Constraint Violation”).

Deliverable: draft taxonomy list.

#### Step 5: Write binary criteria + boundaries (this creates agreement)
For each category, define:
- **Fail if** (2–5 bullets)
- **Pass if** (1–3 bullets)
- **Include**
- **Exclude** (near-misses that belong elsewhere)
- **Minimum evidence** (what snippet proves it)

Deliverable: a codebook page per category.

#### Step 6: Calibration round (10–20 traces, 2 annotators)
Measure disagreements, then refine definitions and boundaries until disagreements drop meaningfully.

Deliverable: taxonomy v1.0 that humans can apply consistently.

#### Step 7: Operationalize + govern
- Version the taxonomy (`taxonomy_v1.0`, `v1.1`, …)
- Keep a mapping when categories merge/split to preserve metric continuity
- Update on a schedule (weekly/biweekly), not ad hoc

### Axial category template (copy/paste)

- **Name**:
- **Definition (1 line)**:
- **System stage(s)**:
- **Fail if**:
  - ...
- **Pass if**:
  - ...
- **Include**:
  - ...
- **Exclude**:
  - ...
- **Example fail evidence snippet**:
- **Example pass evidence snippet**:
- **Typical fixes**:
- **Regression tests**:

### Common starter categories (use as clustering prompts, not mandatory buckets)

- Constraint Violation
- Tool Selection Error
- Tool Argument Error
- Tool Execution Failure
- Tool Result Misuse
- Retrieval Failure / Wrong Context (RAG)
- Ungrounded Claim / Policy Hallucination
- Format/Contract Failure (JSON/schema)
- State/Memory Failure
- Persona/Tone Mismatch
- Over-asking / Inefficiency
- Safety/Compliance Failure

---

## Dimension-Based Generation (synthetic data) — First Principles structured guide

This section mirrors the first-principles structure used in `lesson-28/first_principles_prompt.md`.

### 1) Baseline Summary

- **What it is:** generate synthetic queries by defining a small set of **dimensions**, sampling **tuples**, converting tuples to natural language, applying **quality gates**, and optionally executing them to materialize **traces**.
- **Why it exists:** production logs may be unavailable, narrow, or missing edge cases; synthetic data can rapidly bootstrap coverage and regressions.
- **Key terms:**
  - **Dimension**: axis of variation that changes behavior/failure likelihood
  - **Tuple**: one value from each dimension
  - **Quality gate**: filters/checks ensuring validity, diversity, privacy, realism

### 2) Assumption Audit

- “Random synthetic prompts will cover edge cases” → false; generators regress to typical outputs.
- “More synthetic data is always better” → false; duplicates/invalid cases inflate confidence.
- “If it sounds realistic, it’s good” → false; must verify tuple validity and coverage.

### 3) First Principles Map

```
AXIOM 1: Random sampling under-covers rare/high-impact regions.
AXIOM 2: Generators produce high-likelihood (typical) outputs unless constrained.
AXIOM 3: Evaluation quality depends on coverage + validity, not volume.
AXIOM 4: Datasets drift; without governance, comparisons become meaningless.
```

### 4) Mechanistic Model

Dimensions define a **coordinate system** for the input space. Tuples enforce **coverage** across that space. Realization turns tuples into **instances**. Quality gates enforce **trust**. Executing queries materializes **traces** for end-to-end evaluation. Error analysis feeds back into dimension refinement.

### 5) Boundary Conditions & Applications

- Best for: pre-launch, sparse logs, targeted edge-case testing, regression suites.
- Weak when: dimensions are poorly chosen, quality gates are skipped, or you tune directly on the same synthetic set.

### 6) Uncertainty Register

- optimal tuple count depends on system complexity
- dedupe thresholds are domain-specific
- realism vs stress-test balance must match product risk tolerance

---

## LangSmith SOP: dimension-based synthetic dataset generation (operational)

### Step 0: Define dataset purpose + version
- `dataset_name = <app>-synthetic-eval`
- `dataset_version = vYYYYMMDD.N`
- Write a 2-line dataset card: purpose + scope exclusions

### Step 1: Create a Dimension Catalog (3–6 dimensions)
Each dimension must be **high-variance** and **verifiable**.

Examples:
- task/feature, persona, scenario clarity, constraint load, risk level, tool complexity

### Step 2: Generate tuples with quotas (coverage policy)
Use a mix:
- **core** 60–70% (realistic distribution)
- **edge oversample** 20–30% (failure zones)
- **stress/adversarial** 5–10% (contradictions, empty results)

### Step 3: Tuple → query generation
Constraints:
- no “test case” language
- no PII / real identifiers
- tuple properties must be present (explicitly or intentionally implicitly)

### Step 4: Evolution pass (optional but recommended)
Add one or two transforms:
- ambiguity injection
- typo/noise injection
- multi-step composition
- tool stressors (“if none found, fallback to …”)

### Step 5: Quality gates (reject aggressively)
Minimum:
- dedupe (exact + semantic)
- tuple validity checks
- realism checks
- privacy/PII checks

### Step 6: Import into LangSmith dataset with metadata
Store tuple metadata per example (critical for slicing).

Recommended metadata:

```json
{
  "dataset_version": "v20260127.1",
  "source": "synthetic_dimension_based",
  "dimensions": {
    "task_type": "refund_policy",
    "persona": "novice",
    "scenario": "ambiguous",
    "constraint_load": "multi",
    "risk": "high",
    "tool_complexity": "multi_tool"
  },
  "generator": {
    "model": "<model>",
    "prompt_version": "p3",
    "temperature": 0.7
  },
  "evolution_ops": ["ambiguity_injection", "multi_step"]
}
```

### Step 7: Execute experiments (materialize traces)
Ensure runs capture:
- `app_version` (git SHA)
- `prompt_version`
- `env`
- `dataset_version`

### Step 8: Coverage audit + slice reporting
Report:
- counts by each dimension value
- counts by 2-way interactions (e.g., `task_type × scenario`)
- failure rates by slice once you add evaluators

### Step 9: Close the loop (error analysis → dimension update)
Open-code 20–50 traces from the experiment; add new values/dimensions for repeated novel failure zones; bump dataset version.

---

## Appendices

### A) Severity rubric (quick)
- **S0**: cosmetic
- **S1**: mild friction
- **S2**: wrong outcome / policy risk
- **S3**: unsafe / irreversible / high-cost

### B) “Good open code vs memo” examples

- Open code: “Relaxed budget constraint without approval”  
  Memo: “When tool returns empty, agent drops constraint; add explicit approval gate + regression tests.”

- Open code: “Answered refund eligibility without policy retrieval”  
  Memo: “Enforce policy tool call for refund decisions; require citation of clause in response.”

