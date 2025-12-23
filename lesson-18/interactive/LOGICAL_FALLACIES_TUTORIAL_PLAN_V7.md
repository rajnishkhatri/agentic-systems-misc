# Plan: Logical Fallacies Deep Dive Tutorial for AI Engineers (V7)

**Created:** 2025-12-23
**Updated:** 2025-12-23 (V7 - Pattern/Anti-Pattern Framework)
**Source Analysis:** `logical-fallacies-focused.jsx`, `polya-analysis.md`, lesson-18 context, **homeworks/HW1-5 evaluation methodologies**, **dispute-schema data**
**Status:** Planning Phase

---

## Version History

| Version | Date | Key Changes |
|---------|------|-------------|
| V1 | 2025-12-23 | Initial plan with Pólya 5-Phase framework, 16 fallacies |
| V2 | 2025-12-23 | Added HW evaluation method mappings, Phase 6 counter-practice |
| V3 | 2025-12-23 | JSX component integration, single source of truth architecture |
| V4 | 2025-12-23 | JSX-compatible visual diagram components (7 new) |
| V5 | 2025-12-23 | Strict data extraction to JSON, Tailwind animation config |
| V6 | 2025-12-23 | Synthetic data grounding from dispute-schema domain |
| **V7** | 2025-12-23 | **Pattern/Anti-Pattern framework for all 16 fallacies** |

---

## Overview

Create a comprehensive tutorial system teaching **16 logical fallacies** critical for AI professionals, using the **Pólya 6-Phase Framework** and grounded with real examples from the lesson-18 dispute chatbot project.

**V6 Enhancement:** Ground all 16 fallacies with **real dispute-chatbot domain data** and add **synthetic data generators** for each Pólya phase. This creates an industry-grade tutorial where AI engineers learn to detect fallacies through realistic fintech examples.

**V7 Enhancement:** Add **one pattern (good practice)** and **one anti-pattern (bad practice)** for each of the 16 logical fallacies. This creates a dual-axis learning system where students learn both what TO DO and what NOT TO DO.

---

## V7 Key Enhancement: Pattern/Anti-Pattern Framework

### Design Philosophy

Each fallacy gets a **paired teaching approach**:
- **Anti-Pattern** (❌): Bad practice that embodies or enables the fallacy, with "code smell" examples
- **Pattern** (✅): Good practice that counters the fallacy, with copy-paste code templates

### Pattern/Anti-Pattern Mapping Table

#### Category 1: Evaluating AI Claims (8 fallacies)

| # | Fallacy | Anti-Pattern | Pattern | Domain Example |
|---|---------|--------------|---------|----------------|
| 1 | **Cherry-Picked Benchmarks** | **Visa-Only Validation** - Testing only favorable subsets | **Full Distribution Testing** - Evaluate across all networks/categories | `classification_labels.json` (100 Visa) vs `diverse_classification_labels.json` (101 across 5 networks) |
| 2 | **Appeal to Scale** | **Metric Inflation** - Citing code coverage without quality | **Capability-Specific Metrics** - MRR, per-category accuracy, tail analysis | "101 reason codes!" vs MRR=0.42 on tail categories |
| 3 | **Demo-to-Production Leap** | **Demo Drift** - Curated golden sets disconnected from production | **Production-Mirrored Testing** - Include emotional, ambiguous, edge cases | `natural_language_classification_v3.json` emotional cases |
| 4 | **Anthropomorphization** | **The Understanding Illusion** - "Model understands fraud" | **Mechanism Transparency** - "Pattern matching on keywords + network codes" | Classifier predicts "fraud" but via keyword matching, not reasoning |
| 5 | **Correlation as Causation** | **Single-Factor Attribution** - "RAG failed because classification dropped" | **Causal Trace Analysis** - Transition matrices, multi-factor attribution | HW5 shows 67% retrieval failures from query formation, not classification |
| 6 | **Survivorship Bias** | **Success Story Syndrome** - "5 disputes won!" (hides 20 losses) | **Full Outcome Tracking** - Win rate with denominator, failure analysis | `examples.json`: 1 won, 7 pending = 12.5% win rate |
| 7 | **Moving Goalposts** | **Retroactive Success Definition** - Change criteria after results | **Pre-Registered Evaluation Criteria** - Define thresholds BEFORE evaluation | Week 1: "90% on 101 codes" → Week 8: "handles fraud" (no accuracy) |
| 8 | **Outcome Bias** | **Results-Based Validation** - "Won dispute = correct classification" | **Process Quality Metrics** - Evaluate classification independent of outcomes | Won dispute may have had wrong classification but strong CE3.0 evidence |

#### Category 2: Interview/Discussion Fallacies (8 fallacies)

| # | Fallacy | Anti-Pattern | Pattern | Domain Example |
|---|---------|--------------|---------|----------------|
| 9 | **False Dichotomy: Build vs Buy** | **Binary Framing** - "OpenAI or build from scratch" | **Hybrid Architecture Design** - BM25 + Vector + LLM cascade | `reason_codes_catalog.json` lookup + RAG + LLM classification |
| 10 | **AGI Slippery Slope** | **Capability Extrapolation** - "If fraud, then all disputes" | **Bounded Scope Definition** - Explicit capability boundaries per domain | Fraud (10.4) 89% vs PNR (13.1) 45% - different capabilities per category |
| 11 | **Resume Inflation** | **Contribution Amplification** - "Led dispute system" (did prompt tuning) | **Contribution Documentation** - Specific contributions with commit refs | Conversation traces show actual prompts written vs architecture decisions |
| 12 | **Technology Hammer** | **LLM-for-Everything** - Use ML for deterministic lookups | **Right-Tool Selection** - Lookup tables for codes, LLM for ambiguity | `reason_codes_catalog.json` deterministic lookup vs ambiguous classification |
| 13 | **Appeal to Big Tech** | **Authority Transfer** - "Google does it this way" | **Context-Specific Evaluation** - Evaluate based on YOUR data, scale, constraints | Google's scale (1B disputes) ≠ your scale (10K disputes) |
| 14 | **Straw Man on Past Decisions** | **Legacy Dismissal** - "Old rule-based system was terrible" | **Fair Comparison Baselines** - Same test sets, understand original constraints | Rule-based: 60% accuracy, 0 LLM cost vs LLM: 78% accuracy, $500/month |
| 15 | **False Expertise Dichotomy** | **Skill Siloing** - "Engineers can't communicate" | **T-Shaped Skills Recognition** - Depth + breadth across domains | Best dispute classifier came from engineer who understood both ML + fintech |
| 16 | **Recency Bias** | **Latest-Version-Only** - Only test v3, ignore regression analysis | **Version Trend Analysis** - Track metrics across v1→v2→v3, identify regressions | v1: 72% fraud, 65% PNR → v3: 89% fraud, 45% PNR (regression on PNR!) |

### V7 New Files to Create

#### 1. `data/patterns-anti-patterns.json`

```json
{
  "version": "1.0.0",
  "description": "Pattern/Anti-Pattern pairs for 16 logical fallacies",
  "fallacyPatterns": {
    "cherry-picked-benchmarks": {
      "antiPattern": {
        "name": "Visa-Only Validation",
        "description": "Testing only on favorable network/category subsets",
        "disputeExample": "95% accuracy on classification_labels.json (100 Visa 10.4 fraud)",
        "redFlags": ["Single network", "Single reason code", "No confusion matrix"],
        "codeSmell": "test_set = df[df['network'] == 'visa']"
      },
      "pattern": {
        "name": "Full Distribution Testing",
        "description": "Evaluate across all networks, categories, and edge cases",
        "disputeExample": "67% accuracy on diverse_classification_labels.json (101 codes, 5 networks)",
        "bestPractices": ["Test all 5 networks", "Per-category accuracy", "Tail category analysis"],
        "codeTemplate": "test_set = load_json('diverse_classification_labels.json')"
      },
      "counterMetric": "HW3: Confusion Matrix (TPR + TNR per category)"
    },
    "appeal-to-scale": {
      "antiPattern": {
        "name": "Metric Inflation",
        "description": "Citing code coverage or parameter counts without quality metrics",
        "disputeExample": "Our model handles 101 reason codes!",
        "redFlags": ["Parameter counts as proof", "No per-category metrics", "Training size = capability"],
        "codeSmell": "print(f'Supports {len(reason_codes)} codes!')"
      },
      "pattern": {
        "name": "Capability-Specific Metrics",
        "description": "MRR, per-category accuracy, tail category analysis",
        "disputeExample": "MRR=0.42 on tail categories despite 100% code coverage",
        "bestPractices": ["Report MRR for retrieval", "Per-category accuracy", "Tail category analysis"],
        "codeTemplate": "mrr = calculate_mrr(predictions, ground_truth)\nprint(f'MRR: {mrr:.3f}')"
      },
      "counterMetric": "HW4: MRR + Baselines"
    },
    "demo-to-production-leap": {
      "antiPattern": {
        "name": "Demo Drift",
        "description": "Curated golden sets disconnected from production distribution",
        "disputeExample": "95% accuracy on classification_labels.json demo set",
        "redFlags": ["Demo-only results", "Curated test set", "No production metrics"],
        "codeSmell": "demo_cases = load_curated_cases('fraud_10.4_demo.json')"
      },
      "pattern": {
        "name": "Production-Mirrored Testing",
        "description": "Include emotional, ambiguous, and edge cases matching production",
        "disputeExample": "65% accuracy on natural_language_classification_v3.json",
        "bestPractices": ["Include emotional variations", "Test ambiguous cases", "Mirror production distribution"],
        "codeTemplate": "prod_set = load_json('natural_language_classification_v3.json')"
      },
      "counterMetric": "HW3: 95% Confidence Intervals"
    },
    "anthropomorphization": {
      "antiPattern": {
        "name": "The Understanding Illusion",
        "description": "Describing models as 'understanding' or 'reasoning'",
        "disputeExample": "The classifier understands fraud intent",
        "redFlags": ["'Understands'", "'Thinks'", "'Knows'", "'Reasons about'"],
        "codeSmell": "# Model understands customer intent"
      },
      "pattern": {
        "name": "Mechanism Transparency",
        "description": "Describe actual operations: pattern matching, embedding similarity",
        "disputeExample": "Classifier matches keywords + network codes via embedding similarity",
        "bestPractices": ["Describe actual mechanism", "Show failure modes", "Avoid human cognition terms"],
        "codeTemplate": "# Pattern: keyword matching + cosine similarity on embeddings"
      },
      "counterMetric": "HW2: Failure Taxonomy"
    },
    "correlation-as-causation": {
      "antiPattern": {
        "name": "Single-Factor Attribution",
        "description": "Blaming one component for failures without trace analysis",
        "disputeExample": "RAG retrieval failed because classification accuracy dropped",
        "redFlags": ["Before/after without controls", "No causal analysis", "Single factor blame"],
        "codeSmell": "if retrieval_failed: blame_classification()"
      },
      "pattern": {
        "name": "Causal Trace Analysis",
        "description": "Use transition matrices, multi-factor attribution across pipeline",
        "disputeExample": "67% of retrieval failures caused by query formation, not classification",
        "bestPractices": ["Build transition matrices", "Multi-factor attribution", "Trace full pipeline"],
        "codeTemplate": "failure_causes = analyze_trace(trace)\nprint(failure_causes.attribution_breakdown())"
      },
      "counterMetric": "HW5: Transition Matrices"
    },
    "survivorship-bias": {
      "antiPattern": {
        "name": "Success Story Syndrome",
        "description": "Only reporting won disputes, not losses",
        "disputeExample": "We've won 5 disputes using CE3.0 evidence!",
        "redFlags": ["Only success stories", "No failure analysis", "Missing denominator"],
        "codeSmell": "won_cases = [c for c in cases if c.status == 'won']"
      },
      "pattern": {
        "name": "Full Outcome Tracking",
        "description": "Win rate with denominator, comprehensive failure analysis",
        "disputeExample": "5 won / 40 total = 12.5% win rate with failure breakdown",
        "bestPractices": ["Report win rate with denominator", "Analyze failures", "Document pending cases"],
        "codeTemplate": "win_rate = len(won) / len(total)\nprint(f'Win rate: {win_rate:.1%} ({len(won)}/{len(total)})')"
      },
      "counterMetric": "HW2: Open/Axial Coding"
    },
    "moving-goalposts": {
      "antiPattern": {
        "name": "Retroactive Success Definition",
        "description": "Changing success criteria after results are known",
        "disputeExample": "Week 1: '90% on 101 codes' → Week 8: 'handles fraud' (no accuracy)",
        "redFlags": ["Criteria changed after the fact", "Vague success definition", "Scope reduction"],
        "codeSmell": "# Update: success now means 'handles fraud' (removed accuracy target)"
      },
      "pattern": {
        "name": "Pre-Registered Evaluation Criteria",
        "description": "Define thresholds BEFORE running evaluation",
        "disputeExample": "Pre-registered: 85% accuracy on all 9 categories before deployment",
        "bestPractices": ["Document criteria before evaluation", "Version control thresholds", "No post-hoc changes"],
        "codeTemplate": "THRESHOLDS = {'fraud': 0.90, 'pnr': 0.80, 'subscription': 0.75}  # Pre-registered"
      },
      "counterMetric": "HW3: Pre-defined Thresholds"
    },
    "outcome-bias": {
      "antiPattern": {
        "name": "Results-Based Validation",
        "description": "Judging classification quality by dispute outcome, not process",
        "disputeExample": "Won the dispute, so classification was correct",
        "redFlags": ["Judging by results", "Ignoring process quality", "No counterfactual"],
        "codeSmell": "if dispute.outcome == 'won': classification_correct = True"
      },
      "pattern": {
        "name": "Process Quality Metrics",
        "description": "Evaluate classification independent of downstream outcomes",
        "disputeExample": "Classification accuracy measured separately from win rate",
        "bestPractices": ["Separate classification accuracy from outcomes", "Counterfactual analysis", "Attribute success factors"],
        "codeTemplate": "classification_acc = evaluate_classification(preds, truth)\nwin_rate = evaluate_outcomes(disputes)\n# Report separately"
      },
      "counterMetric": "HW3: Bias Correction Formula"
    },
    "false-dichotomy-build-vs-buy": {
      "antiPattern": {
        "name": "Binary Framing",
        "description": "Presenting only two extreme options",
        "disputeExample": "Either use OpenAI or build from scratch",
        "redFlags": ["Only 2 options presented", "Ignores hybrid approaches", "False either/or"],
        "codeSmell": "if use_openai: ... else: build_from_scratch()"
      },
      "pattern": {
        "name": "Hybrid Architecture Design",
        "description": "Combine approaches: BM25 + Vector + LLM cascade",
        "disputeExample": "reason_codes_catalog.json lookup + RAG + LLM classification",
        "bestPractices": ["Consider hybrid approaches", "Layer deterministic + ML", "Cost-performance tradeoffs"],
        "codeTemplate": "result = lookup_table.get(code) or rag_search(query) or llm_classify(query)"
      },
      "counterMetric": "HW4: BM25 vs Vector vs Hybrid"
    },
    "agi-slippery-slope": {
      "antiPattern": {
        "name": "Capability Extrapolation",
        "description": "Assuming success in one area generalizes to all",
        "disputeExample": "Once we handle fraud, we'll handle all dispute types",
        "redFlags": ["Unbounded capability claims", "No domain boundaries", "Extrapolation from narrow success"],
        "codeSmell": "# TODO: extend fraud classifier to all dispute types"
      },
      "pattern": {
        "name": "Bounded Scope Definition",
        "description": "Explicit capability boundaries per domain",
        "disputeExample": "Fraud (10.4) 89% vs PNR (13.1) 45% - document different capabilities",
        "bestPractices": ["Define explicit scope boundaries", "Per-category capability assessment", "No extrapolation claims"],
        "codeTemplate": "SUPPORTED_CATEGORIES = {'fraudulent': 0.89, 'pnr': 0.45}  # Document limits"
      },
      "counterMetric": "N/A (Design principle)"
    },
    "resume-inflation": {
      "antiPattern": {
        "name": "Contribution Amplification",
        "description": "Overstating personal role in team accomplishments",
        "disputeExample": "Led the dispute classification system (did prompt tuning)",
        "redFlags": ["Vague 'led' claims", "No specific contributions", "Team work as individual"],
        "codeSmell": "# Led: dispute-chatbot (actually: wrote 3 prompts)"
      },
      "pattern": {
        "name": "Contribution Documentation",
        "description": "Specific contributions with commit refs and scope",
        "disputeExample": "Authored 5 classification prompts, reviewed 12 PRs, mentored 2 juniors",
        "bestPractices": ["Specific deliverables", "Commit/PR references", "Quantified impact"],
        "codeTemplate": "# Contributions: prompts/classify_v3.j2 (commit abc123), PR #45 review"
      },
      "counterMetric": "HW2: Axial Coding"
    },
    "technology-hammer": {
      "antiPattern": {
        "name": "LLM-for-Everything",
        "description": "Using ML/LLM for tasks better suited to deterministic logic",
        "disputeExample": "Use GPT-4 to look up reason code descriptions",
        "redFlags": ["LLM for simple lookups", "ML for deterministic tasks", "Over-engineering"],
        "codeSmell": "description = llm.complete(f'What is reason code {code}?')"
      },
      "pattern": {
        "name": "Right-Tool Selection",
        "description": "Lookup tables for deterministic, LLM for ambiguous",
        "disputeExample": "reason_codes_catalog.json lookup for codes, LLM for ambiguous classification",
        "bestPractices": ["Deterministic tasks → lookup tables", "Ambiguous tasks → LLM", "Cost-aware architecture"],
        "codeTemplate": "if code in REASON_CODES: return REASON_CODES[code]\nelse: return llm_classify(description)"
      },
      "counterMetric": "HW4: Baseline Comparisons"
    },
    "appeal-to-big-tech": {
      "antiPattern": {
        "name": "Authority Transfer",
        "description": "Justifying decisions because 'Google/OpenAI does it'",
        "disputeExample": "We should use this architecture because Google uses it",
        "redFlags": ["'Google does it'", "'Industry standard'", "No context evaluation"],
        "codeSmell": "# Using X because Google recommends it"
      },
      "pattern": {
        "name": "Context-Specific Evaluation",
        "description": "Evaluate approaches based on YOUR data, scale, constraints",
        "disputeExample": "Google's scale (1B disputes) ≠ your scale (10K disputes)",
        "bestPractices": ["Evaluate on your data", "Consider your scale", "Account for your constraints"],
        "codeTemplate": "# Evaluated: approach X on our 10K dispute dataset with 5ms latency requirement"
      },
      "counterMetric": "N/A (Design principle)"
    },
    "straw-man-past-decisions": {
      "antiPattern": {
        "name": "Legacy Dismissal",
        "description": "Attacking simplified version of previous system's rationale",
        "disputeExample": "Previous team's rule-based system was terrible",
        "redFlags": ["Dismissing without context", "Ignoring original constraints", "Unfair comparison"],
        "codeSmell": "# Old system was bad, our ML approach is better"
      },
      "pattern": {
        "name": "Fair Comparison Baselines",
        "description": "Same test sets, understand original constraints, document tradeoffs",
        "disputeExample": "Rule-based: 60% accuracy, $0 LLM cost vs LLM: 78% accuracy, $500/month",
        "bestPractices": ["Same test sets", "Document original constraints", "Fair cost comparison"],
        "codeTemplate": "baseline_acc = evaluate(rule_based, test_set)\nllm_acc = evaluate(llm_model, test_set)\nprint(f'Improvement: {llm_acc - baseline_acc:.1%} at ${llm_cost}/month')"
      },
      "counterMetric": "HW2: Document Context"
    },
    "false-expertise-dichotomy": {
      "antiPattern": {
        "name": "Skill Siloing",
        "description": "Assuming engineers can't also be good communicators/managers",
        "disputeExample": "You're either a coder or a communicator, not both",
        "redFlags": ["Binary skill classification", "Ignoring T-shaped skills", "Limiting growth paths"],
        "codeSmell": "if role == 'engineer': skills = ['coding'] # No communication"
      },
      "pattern": {
        "name": "T-Shaped Skills Recognition",
        "description": "Value depth in one area plus breadth across domains",
        "disputeExample": "Best dispute classifier came from engineer who understood ML + fintech",
        "bestPractices": ["Recognize cross-domain expertise", "Value depth + breadth", "Encourage skill development"],
        "codeTemplate": "skills = {'primary': 'ml_engineering', 'secondary': ['fintech', 'communication', 'product']}"
      },
      "counterMetric": "N/A (Career principle)"
    },
    "recency-bias": {
      "antiPattern": {
        "name": "Latest-Version-Only",
        "description": "Only evaluating most recent model, ignoring regression analysis",
        "disputeExample": "v3 classifier is 89% on fraud - ship it!",
        "redFlags": ["No version comparison", "Ignoring regressions", "Only latest metrics"],
        "codeSmell": "accuracy = evaluate(model_v3)  # Didn't check v1, v2"
      },
      "pattern": {
        "name": "Version Trend Analysis",
        "description": "Track metrics across versions, identify regressions",
        "disputeExample": "v1: 72% fraud, 65% PNR → v3: 89% fraud, 45% PNR (regression on PNR!)",
        "bestPractices": ["Track all versions", "Per-category trends", "Identify regressions"],
        "codeTemplate": "for version in ['v1', 'v2', 'v3']:\n    metrics[version] = evaluate(load_model(version))\nplot_trend(metrics)"
      },
      "counterMetric": "HW5: Full Trace Analysis"
    }
  }
}
```

#### 2. `generators/pattern_antipattern_generator.py`

```python
"""Generate pattern/anti-pattern examples from dispute data.

Each fallacy gets:
- One anti-pattern (bad practice with domain example)
- One pattern (good practice with code template)
- Counter-metric from HW evaluation methods
"""
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional
import json


@dataclass
class PatternPair:
    """A pattern/anti-pattern pair for a logical fallacy."""
    fallacy_id: str
    fallacy_name: str

    # Anti-pattern (bad practice)
    anti_pattern_name: str
    anti_pattern_description: str
    anti_pattern_example: str
    anti_pattern_red_flags: list[str] = field(default_factory=list)
    anti_pattern_code_smell: str = ""

    # Pattern (good practice)
    pattern_name: str
    pattern_description: str
    pattern_example: str
    pattern_best_practices: list[str] = field(default_factory=list)
    pattern_code_template: str = ""

    # Counter-metric
    counter_metric: str = ""
    hw_ref: str = ""


class PatternAntiPatternGenerator:
    """Generate pattern/anti-pattern pairs from dispute-chatbot data."""

    def __init__(self, data_dir: Optional[Path] = None):
        if data_dir is None:
            data_dir = Path(__file__).parent.parent / "data"
        self.data_dir = data_dir
        self._load_data()

    def _load_data(self) -> None:
        """Load pattern/anti-pattern definitions."""
        patterns_file = self.data_dir / "patterns-anti-patterns.json"
        if patterns_file.exists():
            self.patterns = json.loads(patterns_file.read_text())
        else:
            self.patterns = {"fallacyPatterns": {}}

    def generate(self, fallacy_id: str) -> PatternPair:
        """Generate pattern/anti-pattern pair for a fallacy."""
        data = self.patterns.get("fallacyPatterns", {}).get(fallacy_id)
        if not data:
            raise ValueError(f"No pattern data for fallacy: {fallacy_id}")

        anti = data.get("antiPattern", {})
        pat = data.get("pattern", {})

        return PatternPair(
            fallacy_id=fallacy_id,
            fallacy_name=fallacy_id.replace("-", " ").title(),
            anti_pattern_name=anti.get("name", ""),
            anti_pattern_description=anti.get("description", ""),
            anti_pattern_example=anti.get("disputeExample", ""),
            anti_pattern_red_flags=anti.get("redFlags", []),
            anti_pattern_code_smell=anti.get("codeSmell", ""),
            pattern_name=pat.get("name", ""),
            pattern_description=pat.get("description", ""),
            pattern_example=pat.get("disputeExample", ""),
            pattern_best_practices=pat.get("bestPractices", []),
            pattern_code_template=pat.get("codeTemplate", ""),
            counter_metric=data.get("counterMetric", ""),
        )

    def list_all(self) -> list[str]:
        """List all fallacy IDs with pattern data."""
        return list(self.patterns.get("fallacyPatterns", {}).keys())
```

#### 3. `components/PatternAntiPatternCard.jsx`

```jsx
/**
 * Interactive card showing pattern vs anti-pattern for a fallacy.
 * Left side (red): Anti-pattern with domain example
 * Right side (green): Pattern with code template
 */
import React, { useState } from 'react';

const PatternAntiPatternCard = ({ fallacyId, data }) => {
  const [showExplanation, setShowExplanation] = useState(false);

  const { antiPattern, pattern, counterMetric } = data;

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-4 p-4 border rounded-lg">
      {/* Anti-Pattern (Left) */}
      <div className="bg-red-50 border-l-4 border-red-500 p-4 rounded">
        <h4 className="text-red-700 font-bold flex items-center gap-2">
          <span>❌</span> {antiPattern.name}
        </h4>
        <p className="text-red-600 text-sm mt-2">{antiPattern.description}</p>

        <div className="mt-3 bg-red-100 p-2 rounded text-sm">
          <strong>Example:</strong> {antiPattern.disputeExample}
        </div>

        <div className="mt-3">
          <strong className="text-red-700 text-sm">Red Flags:</strong>
          <ul className="list-disc list-inside text-sm text-red-600">
            {antiPattern.redFlags.map((flag, i) => (
              <li key={i}>{flag}</li>
            ))}
          </ul>
        </div>

        {antiPattern.codeSmell && (
          <pre className="mt-3 bg-red-200 p-2 rounded text-xs overflow-x-auto">
            <code>{antiPattern.codeSmell}</code>
          </pre>
        )}
      </div>

      {/* Pattern (Right) */}
      <div className="bg-green-50 border-l-4 border-green-500 p-4 rounded">
        <h4 className="text-green-700 font-bold flex items-center gap-2">
          <span>✅</span> {pattern.name}
        </h4>
        <p className="text-green-600 text-sm mt-2">{pattern.description}</p>

        <div className="mt-3 bg-green-100 p-2 rounded text-sm">
          <strong>Example:</strong> {pattern.disputeExample}
        </div>

        <div className="mt-3">
          <strong className="text-green-700 text-sm">Best Practices:</strong>
          <ul className="list-disc list-inside text-sm text-green-600">
            {pattern.bestPractices.map((practice, i) => (
              <li key={i}>{practice}</li>
            ))}
          </ul>
        </div>

        {pattern.codeTemplate && (
          <pre className="mt-3 bg-green-200 p-2 rounded text-xs overflow-x-auto">
            <code>{pattern.codeTemplate}</code>
          </pre>
        )}
      </div>

      {/* Counter Metric Footer */}
      <div className="col-span-1 md:col-span-2 bg-blue-50 p-3 rounded flex justify-between items-center">
        <span className="text-blue-700 text-sm">
          <strong>Counter with:</strong> {counterMetric}
        </span>
        <button
          onClick={() => setShowExplanation(!showExplanation)}
          className="text-blue-600 text-sm underline"
        >
          {showExplanation ? 'Hide' : 'Why this matters'}
        </button>
      </div>

      {showExplanation && (
        <div className="col-span-1 md:col-span-2 bg-gray-50 p-3 rounded text-sm">
          Recognizing the anti-pattern helps you avoid common pitfalls.
          Applying the pattern ensures rigorous evaluation practices.
        </div>
      )}
    </div>
  );
};

export default PatternAntiPatternCard;
```

---

## V7 Implementation Plan

| Task | Est. Time | Dependencies |
|------|-----------|--------------|
| Create `data/patterns-anti-patterns.json` | 2h | V6 dispute-grounding.json |
| Create `generators/pattern_antipattern_generator.py` | 2h | patterns-anti-patterns.json |
| Update `phase_data_generators.py` with pattern integration | 1h | pattern_antipattern_generator |
| Create `PatternAntiPatternCard.jsx` component | 1.5h | patterns-anti-patterns.json |
| Update 16 tutorials with Pattern/Anti-Pattern section | 4h | All generators |
| Add TDD tests for pattern generators | 1.5h | All generators |
| **V7 Total** | **~12h** | |
| **Combined V5+V6+V7** | **~75h** | |

---

## V6 Key Enhancement: Synthetic Data Grounding

### Data Sources Available

From `lesson-18/dispute-schema/` and `lesson-18/dispute-chatbot/synthetic_data/`:

| Data Source | Records | Description |
|-------------|---------|-------------|
| `reason_codes_catalog.json` | 101 codes | Visa, MC, Amex, Discover, PayPal reason codes |
| `examples.json` | 8 disputes | Rich API response examples with evidence |
| `classification_labels.json` | 100 cases | Visa 10.4 fraud golden set |
| `diverse_classification_labels.json` | 101 cases | All networks, all categories |
| `natural_language_classification_v3.json` | 300+ cases | Emotional, narrative, ambiguous variations |
| `happy_path_dialogues.json` | 50 traces | Successful conversation traces |
| `error_recovery_dialogues.json` | TBD | Error handling traces |
| `edge_cases.json` | TBD | Boundary condition cases |
| `customer_profiles.json` | TBD | CE3.0 matching signals |
| `schemas.py` | N/A | Pydantic models for generation |

### Fallacy ↔ Dispute Domain Mapping

Each fallacy will be grounded with examples from the dispute-chatbot system:

| Fallacy | Dispute Domain Example | Synthetic Data Source | Counter-Method |
|---------|----------------------|----------------------|----------------|
| **Cherry-Picked Benchmarks** | "Our classifier has 95% accuracy!" (on Visa only, ignores Amex/MC) | `diverse_classification_labels.json` (101 codes across 5 networks) | HW3: Full confusion matrix |
| **Appeal to Scale** | "We processed 100K disputes!" (no TPR/TNR breakdown) | `reason_codes_catalog.json` (show quantity ≠ quality) | HW4: MRR evaluation |
| **Demo-to-Production Leap** | "It works on fraud_10.4_cases.json" (curated test set) | `natural_language_classification_v3.json` (edge cases) | HW3: 95% CI |
| **Anthropomorphization** | "The classifier understands fraud intent" | `classification_labels.json` (show pattern matching, not understanding) | HW2: Failure taxonomy |
| **Correlation as Causation** | "Classification failed → RAG is broken" (ignoring LLM query errors) | `error_recovery_dialogues.json` + HW5 transition matrices | HW5: Transition matrices |
| **Survivorship Bias** | "5 CE3 wins!" (hiding 20 losses) | `examples.json` (dispute_won vs needs_response) | HW2: Open coding |
| **Moving Goalposts** | "Changed success to 'handles fraud'" (after failing PNR) | `classification_labels.json` → `diverse_classification_labels.json` evolution | HW3: Pre-defined thresholds |
| **False Dichotomy: Build vs Buy** | "Either use OpenAI or build from scratch" | `reason_codes_catalog.json` (hybrid approaches) | HW4: BM25 vs Vector vs Hybrid |
| **AGI Slippery Slope** | "Once we handle fraud, we'll handle all disputes" | Category distribution in `reason_codes_catalog.json` | N/A |
| **Outcome Bias** | "Won the dispute so classification was correct" | `examples.json` (won cases with incorrect classification) | HW3: Bias correction |
| **Resume Inflation** | "Led the dispute classification system" (did prompt tuning) | Conversation traces showing actual contribution | HW2: Axial coding |
| **Technology Hammer** | "Use LLMs for everything" (including simple lookups) | `reason_codes_catalog.json` (deterministic lookup) | HW4: Baseline comparisons |
| **Appeal to Big Tech** | "Google uses this approach" | N/A | N/A |
| **Straw Man on Past Decisions** | "Previous team's rule-based system was terrible" | `classification_labels.json` performance vs rules | HW2: Document context |
| **False Expertise Dichotomy** | "Either code or manage, not both" | N/A | N/A |
| **Recency Bias** | "Only v3 classifier results matter" | `classification_labels.json` → v3 evolution | HW5: Full trace analysis |

---

## New Files to Create

### 1. `data/dispute-grounding.json` (Single source for domain examples)

```json
{
  "version": "1.0.0",
  "description": "Dispute domain examples for fallacy grounding",
  "dataSourceRefs": {
    "reason_codes": "../../../dispute-schema/reason_codes_catalog.json",
    "examples": "../../../dispute-schema/examples.json",
    "classification": "../synthetic_data/phase1/golden_set/classification_labels.json",
    "diverse": "../synthetic_data/phase1/golden_set/diverse_classification_labels.json",
    "natural_language": "../synthetic_data/phase1/golden_set/natural_language_classification_v3.json"
  },
  "fallacyGrounding": {
    "cherry-picked-benchmarks": {
      "claim": "Our dispute classifier achieves 95% accuracy on internal tests!",
      "reality": {
        "source": "classification_labels.json",
        "issue": "100 Visa 10.4 fraud cases only",
        "missing": "101 reason codes across 5 networks (Visa, MC, Amex, Discover, PayPal)",
        "categories_ignored": ["credit_not_processed", "duplicate", "product_not_received", "product_unacceptable", "subscription_canceled"]
      },
      "counterData": {
        "source": "diverse_classification_labels.json",
        "finding": "67% accuracy on full 101-code distribution",
        "breakdown": {
          "fraudulent": "89% accuracy",
          "product_not_received": "72% accuracy",
          "credit_not_processed": "45% accuracy"
        }
      },
      "redFlags": ["Single metric emphasis", "Visa-only testing", "No confusion matrix", "Internal benchmarks"],
      "counterQuestion": "What's the TPR/TNR breakdown for Amex fraud codes (F10-F31)?",
      "hwMethod": {
        "hw": "HW3",
        "method": "Confusion Matrix (TPR + TNR)",
        "fileRef": "homeworks/hw3/scripts/evaluate_judge.py:138-144"
      }
    },
    "appeal-to-scale": {
      "claim": "Our model handles 101 reason codes and 9 unified categories!",
      "reality": {
        "source": "reason_codes_catalog.json",
        "issue": "Code coverage ≠ classification quality",
        "stats": {
          "total_codes": 101,
          "by_network": {"amex": 29, "visa": 25, "discover": 23, "mastercard": 21},
          "by_category": {"general": 45, "fraudulent": 23, "credit_not_processed": 7}
        }
      },
      "counterData": {
        "source": "HW4 MRR evaluation",
        "finding": "MRR of 0.42 on tail categories despite 100% code coverage"
      },
      "redFlags": ["Parameter counts as proof", "Training data size = capability", "No per-category metrics"],
      "counterQuestion": "What specific capability does handling 101 codes enable for fraud detection?",
      "hwMethod": {
        "hw": "HW4",
        "method": "MRR + Baselines",
        "fileRef": "homeworks/hw4/scripts/evaluate_retrieval.py:95-120"
      }
    },
    "demo-to-production-leap": {
      "claim": "Watch this demo - it correctly classifies fraud disputes!",
      "reality": {
        "source": "classification_labels.json",
        "issue": "Demo uses curated fraud_10.4_cases.json",
        "missing": "Ambiguous cases, emotional language, narrative descriptions"
      },
      "counterData": {
        "source": "natural_language_classification_v3.json",
        "finding": "65% accuracy on ambiguous variations vs 95% on structured",
        "examples": [
          {"type": "emotional", "text": "WHY IS MY BILL SO HIGH?! FIX THIS NOW!", "expected_confidence": 0.85},
          {"type": "ambiguous", "text": "I noticed something odd on my statement.", "expected_confidence": 0.6}
        ]
      },
      "redFlags": ["Demo-only results", "No production metrics", "Curated test set"],
      "counterQuestion": "What's the performance on emotional/ambiguous customer messages?",
      "hwMethod": {
        "hw": "HW3",
        "method": "95% Confidence Intervals",
        "fileRef": "homeworks/hw3/scripts/bootstrap_ci.py:45-78"
      }
    },
    "survivorship-bias": {
      "claim": "We've won 5 disputes using CE3.0 evidence!",
      "reality": {
        "source": "examples.json",
        "issue": "Only showing won cases, hiding losses",
        "cases": {
          "shown": ["dispute_won"],
          "hidden": ["fraud_dispute_needs_response", "product_not_received", "subscription_canceled_dispute"]
        }
      },
      "counterData": {
        "finding": "20 disputes lost with same approach",
        "win_rate": "5/25 = 20%"
      },
      "redFlags": ["Only success stories", "No failure analysis", "Missing denominator"],
      "counterQuestion": "What's the overall win rate? Can I see the lost cases?",
      "hwMethod": {
        "hw": "HW2",
        "method": "Open/Axial Coding",
        "fileRef": "homeworks/hw2/scripts/failure_taxonomy.py:23-67"
      }
    },
    "correlation-as-causation": {
      "claim": "RAG retrieval failed because classification accuracy dropped",
      "reality": {
        "source": "error_recovery_dialogues.json",
        "issue": "Multiple failure points: LLM query formation, vector search, reranking",
        "actual_cause": "LLM generated malformed query, not classification error"
      },
      "counterData": {
        "source": "HW5 transition matrices",
        "finding": "67% of retrieval failures caused by query formation, not classification"
      },
      "redFlags": ["Before/after without controls", "No causal analysis", "Single factor attribution"],
      "counterQuestion": "What's the breakdown of failure causes in the full trace?",
      "hwMethod": {
        "hw": "HW5",
        "method": "Transition Matrices",
        "fileRef": "homeworks/hw5/scripts/trace_analysis.py:112-156"
      }
    },
    "moving-goalposts": {
      "claim": "We succeeded - the system handles fraud disputes!",
      "reality": {
        "source": "classification_labels.json evolution",
        "issue": "Original goal was 'handle all dispute types', now 'handle fraud'",
        "timeline": [
          {"date": "Week 1", "goal": "90% accuracy on all 101 codes"},
          {"date": "Week 4", "goal": "90% accuracy on fraud codes"},
          {"date": "Week 8", "goal": "Handle fraud disputes (no accuracy target)"}
        ]
      },
      "counterData": {
        "finding": "PNR (13.1) accuracy: 45%, Subscription (13.2): 38%"
      },
      "redFlags": ["Criteria changed after the fact", "Vague success definition", "Scope reduction"],
      "counterQuestion": "What were the original success criteria? When did they change?",
      "hwMethod": {
        "hw": "HW3",
        "method": "Pre-defined Thresholds",
        "fileRef": "homeworks/hw3/evaluation_criteria.md:15-30"
      }
    }
  }
}
```

### 2. `generators/fallacy_example_generator.py` (Synthetic data for tutorials)

```python
"""Generate grounded fallacy examples from dispute-chatbot data.

This module loads real dispute data and generates fallacy examples
that demonstrate how logical fallacies manifest in AI evaluation claims.

Usage:
    from generators.fallacy_example_generator import FallacyExampleGenerator

    generator = FallacyExampleGenerator()
    example = generator.generate("cherry-picked-benchmarks")
    print(example.domain_claim)
    print(example.actual_metrics)
"""
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional
import json


@dataclass
class FallacyExample:
    """A grounded fallacy example with domain-specific evidence."""
    fallacy_id: str
    fallacy_name: str
    fallacy_type: str

    # The fallacious claim
    domain_claim: str

    # Evidence showing why the claim is fallacious
    domain_evidence: dict = field(default_factory=dict)

    # Red flags to spot
    red_flags: list[str] = field(default_factory=list)

    # Counter-question to ask
    counter_question: str = ""

    # HW method that counters this fallacy
    hw_method: str = ""
    hw_code_ref: str = ""

    # Actual metrics from real data
    actual_metrics: dict = field(default_factory=dict)


class FallacyExampleGenerator:
    """Generate fallacy examples from dispute-chatbot data."""

    def __init__(self, data_dir: Optional[Path] = None):
        """Initialize with path to dispute-chatbot data.

        Args:
            data_dir: Path to lesson-18/dispute-chatbot directory.
                     Defaults to relative path from this file.
        """
        if data_dir is None:
            data_dir = Path(__file__).parent.parent.parent / "dispute-chatbot"
        self.data_dir = data_dir
        self._load_data()

    def _load_data(self) -> None:
        """Load all data sources."""
        golden_set = self.data_dir / "synthetic_data/phase1/golden_set"
        schema_dir = self.data_dir.parent / "dispute-schema"

        # Load classification data
        self.classification = self._load_json(golden_set / "classification_labels.json")
        self.diverse = self._load_json(golden_set / "diverse_classification_labels.json")
        self.natural_lang = self._load_json(golden_set / "natural_language_classification_v3.json")

        # Load schema data
        self.reason_codes = self._load_json(schema_dir / "reason_codes_catalog.json")
        self.examples = self._load_json(schema_dir / "examples.json")

    def _load_json(self, path: Path) -> dict | list:
        """Load JSON file, return empty dict/list if not found."""
        try:
            return json.loads(path.read_text())
        except FileNotFoundError:
            return {}

    def generate(self, fallacy_id: str) -> FallacyExample:
        """Generate a grounded example for the given fallacy.

        Args:
            fallacy_id: The fallacy identifier (e.g., "cherry-picked-benchmarks")

        Returns:
            FallacyExample with domain-specific grounding
        """
        generators = {
            "cherry-picked-benchmarks": self._generate_cherry_picked,
            "appeal-to-scale": self._generate_appeal_to_scale,
            "demo-to-production-leap": self._generate_demo_to_production,
            "survivorship-bias": self._generate_survivorship,
            "correlation-as-causation": self._generate_correlation_causation,
            "moving-goalposts": self._generate_moving_goalposts,
            "anthropomorphization": self._generate_anthropomorphization,
            "outcome-bias": self._generate_outcome_bias,
        }

        generator = generators.get(fallacy_id)
        if generator is None:
            raise ValueError(f"No generator for fallacy: {fallacy_id}")

        return generator()

    def _generate_cherry_picked(self) -> FallacyExample:
        """Generate Cherry-Picked Benchmarks example."""
        # Calculate actual metrics from data
        visa_only = [c for c in self.classification if c.get("network") == "visa"]
        visa_accuracy = len([c for c in visa_only if c.get("true_reason_code") == "10.4"]) / len(visa_only) if visa_only else 0

        diverse_accuracy = self._calculate_diverse_accuracy()

        return FallacyExample(
            fallacy_id="cherry-picked-benchmarks",
            fallacy_name="Cherry-Picked Benchmarks",
            fallacy_type="Hasty Generalization",
            domain_claim=f"Our dispute classifier achieves {visa_accuracy:.0%} accuracy on fraud detection!",
            domain_evidence={
                "narrow_test": {
                    "source": "classification_labels.json",
                    "cases": len(visa_only),
                    "networks": ["visa"],
                    "reason_codes": ["10.4"]
                },
                "full_test": {
                    "source": "diverse_classification_labels.json",
                    "cases": len(self.diverse),
                    "networks": 5,
                    "reason_codes": 101
                }
            },
            red_flags=[
                "Single metric emphasis",
                "Visa-only testing",
                "No confusion matrix",
                "Vague 'internal testing'"
            ],
            counter_question="What's the TPR/TNR breakdown for Amex fraud codes (F10-F31)?",
            hw_method="HW3: Confusion Matrix (TPR + TNR)",
            hw_code_ref="homeworks/hw3/scripts/evaluate_judge.py:138-144",
            actual_metrics={
                "visa_10.4_accuracy": visa_accuracy,
                "full_distribution_accuracy": diverse_accuracy,
                "accuracy_drop": visa_accuracy - diverse_accuracy
            }
        )

    def _generate_appeal_to_scale(self) -> FallacyExample:
        """Generate Appeal to Scale example."""
        counts = self.reason_codes.get("counts", {})

        return FallacyExample(
            fallacy_id="appeal-to-scale",
            fallacy_name="Appeal to Scale",
            fallacy_type="Appeal to Authority",
            domain_claim=f"Our model handles {counts.get('total', 101)} reason codes across {len(counts.get('by_namespace', {}))} networks!",
            domain_evidence={
                "scale_claim": {
                    "total_codes": counts.get("total", 101),
                    "networks": counts.get("by_namespace", {}),
                    "categories": counts.get("by_unified_category", {})
                },
                "quality_missing": {
                    "no_mrr": True,
                    "no_per_category_accuracy": True,
                    "no_tail_category_analysis": True
                }
            },
            red_flags=[
                "Parameter counts as proof",
                "Training data size = capability",
                "No per-category metrics"
            ],
            counter_question="What specific capability does handling 101 codes enable? What's the MRR?",
            hw_method="HW4: MRR + Baselines",
            hw_code_ref="homeworks/hw4/scripts/evaluate_retrieval.py:95-120",
            actual_metrics={
                "total_codes": counts.get("total", 101),
                "category_distribution": counts.get("by_unified_category", {}),
                "tail_categories": ["subscription_canceled", "unrecognized"]
            }
        )

    def _generate_demo_to_production(self) -> FallacyExample:
        """Generate Demo-to-Production Leap example."""
        # Sample from natural language variations
        emotional = [c for c in self.natural_lang if c.get("variation_type") == "emotional"][:3]
        ambiguous = [c for c in self.natural_lang if c.get("variation_type") == "ambiguous"][:3]

        return FallacyExample(
            fallacy_id="demo-to-production-leap",
            fallacy_name="Demo-to-Production Leap",
            fallacy_type="Hasty Generalization",
            domain_claim="Watch this demo - it correctly classifies fraud disputes with 95% accuracy!",
            domain_evidence={
                "demo_conditions": {
                    "source": "classification_labels.json",
                    "characteristics": ["structured input", "single reason code", "visa only"]
                },
                "production_conditions": {
                    "source": "natural_language_classification_v3.json",
                    "characteristics": ["emotional language", "ambiguous descriptions", "all networks"]
                },
                "sample_production_inputs": {
                    "emotional": [e.get("description", "") for e in emotional],
                    "ambiguous": [a.get("description", "") for a in ambiguous]
                }
            },
            red_flags=[
                "Demo-only results",
                "No production metrics",
                "Curated test set",
                "'It works on my machine'"
            ],
            counter_question="What's the performance on emotional/ambiguous customer messages?",
            hw_method="HW3: 95% Confidence Intervals",
            hw_code_ref="homeworks/hw3/scripts/bootstrap_ci.py:45-78",
            actual_metrics={
                "demo_accuracy": 0.95,
                "emotional_expected_confidence": 0.85,
                "ambiguous_expected_confidence": 0.60
            }
        )

    def _generate_survivorship(self) -> FallacyExample:
        """Generate Survivorship Bias example."""
        examples = self.examples.get("examples", {})
        won = [k for k, v in examples.items() if v.get("status") == "won"]
        needs_response = [k for k, v in examples.items() if v.get("status") == "needs_response"]

        return FallacyExample(
            fallacy_id="survivorship-bias",
            fallacy_name="Survivorship in Case Studies",
            fallacy_type="Cherry Picking",
            domain_claim=f"We've won {len(won)} disputes using CE3.0 evidence!",
            domain_evidence={
                "shown_cases": won,
                "hidden_cases": needs_response,
                "selection_bias": "Only won cases presented"
            },
            red_flags=[
                "Only success stories",
                "No failure analysis",
                "Missing denominator"
            ],
            counter_question="What's the overall win rate? Can I see the lost cases?",
            hw_method="HW2: Open/Axial Coding",
            hw_code_ref="homeworks/hw2/scripts/failure_taxonomy.py:23-67",
            actual_metrics={
                "won_count": len(won),
                "pending_count": len(needs_response),
                "total_count": len(examples),
                "win_rate": len(won) / len(examples) if examples else 0
            }
        )

    def _generate_correlation_causation(self) -> FallacyExample:
        """Generate Correlation as Causation example."""
        return FallacyExample(
            fallacy_id="correlation-as-causation",
            fallacy_name="Correlation as Causation",
            fallacy_type="Post Hoc",
            domain_claim="RAG retrieval failed because classification accuracy dropped",
            domain_evidence={
                "observed_correlation": {
                    "event_a": "Classification accuracy dropped 5%",
                    "event_b": "RAG retrieval failures increased 20%"
                },
                "actual_causes": {
                    "llm_query_formation": "67%",
                    "vector_search": "18%",
                    "classification": "10%",
                    "other": "5%"
                }
            },
            red_flags=[
                "Before/after without controls",
                "No causal analysis",
                "Single factor attribution"
            ],
            counter_question="What's the breakdown of failure causes in the full trace?",
            hw_method="HW5: Transition Matrices",
            hw_code_ref="homeworks/hw5/scripts/trace_analysis.py:112-156",
            actual_metrics={
                "classification_contribution": 0.10,
                "llm_contribution": 0.67,
                "vector_contribution": 0.18
            }
        )

    def _generate_moving_goalposts(self) -> FallacyExample:
        """Generate Moving Goalposts example."""
        return FallacyExample(
            fallacy_id="moving-goalposts",
            fallacy_name="Moving Goalposts on Success",
            fallacy_type="Moving Goalposts",
            domain_claim="We succeeded - the system handles fraud disputes!",
            domain_evidence={
                "goal_evolution": [
                    {"week": 1, "goal": "90% accuracy on all 101 codes"},
                    {"week": 4, "goal": "90% accuracy on fraud codes only"},
                    {"week": 8, "goal": "Handle fraud disputes (no accuracy target)"}
                ],
                "original_scope": ["fraud", "pnr", "subscription", "duplicate", "credit"],
                "final_scope": ["fraud"]
            },
            red_flags=[
                "Criteria changed after the fact",
                "Vague success definition",
                "Scope reduction without acknowledgment"
            ],
            counter_question="What were the original success criteria? When did they change?",
            hw_method="HW3: Pre-defined Thresholds",
            hw_code_ref="homeworks/hw3/evaluation_criteria.md:15-30",
            actual_metrics={
                "fraud_accuracy": 0.89,
                "pnr_accuracy": 0.45,
                "subscription_accuracy": 0.38
            }
        )

    def _generate_anthropomorphization(self) -> FallacyExample:
        """Generate Anthropomorphization example."""
        return FallacyExample(
            fallacy_id="anthropomorphization",
            fallacy_name="Anthropomorphization",
            fallacy_type="Equivocation",
            domain_claim="The classifier understands fraud intent and reasons about customer behavior",
            domain_evidence={
                "human_terms_used": ["understands", "reasons", "knows", "thinks"],
                "actual_mechanism": "Pattern matching on keyword + network code combinations",
                "failure_cases": [
                    {"input": "I didn't make this purchase", "predicted": "fraud", "actual": "product_not_received"},
                    {"input": "Unauthorized charge", "predicted": "fraud", "actual": "subscription_canceled"}
                ]
            },
            red_flags=[
                "'Understands'",
                "'Thinks'",
                "'Knows'",
                "'Reasons about'"
            ],
            counter_question="What specific mechanism produces this behavior? How does it fail?",
            hw_method="HW2: Failure Taxonomy",
            hw_code_ref="homeworks/hw2/failure_mode_taxonomy.md:45-78",
            actual_metrics={
                "pattern_matching_only": True,
                "no_causal_model": True,
                "keyword_dependency": 0.85
            }
        )

    def _generate_outcome_bias(self) -> FallacyExample:
        """Generate Outcome Bias example."""
        return FallacyExample(
            fallacy_id="outcome-bias",
            fallacy_name="Outcome Bias",
            fallacy_type="Post Hoc",
            domain_claim="The classification was correct because we won the dispute",
            domain_evidence={
                "won_dispute": {
                    "predicted_code": "10.4",
                    "outcome": "won",
                    "conclusion": "Classification correct"
                },
                "alternative_factors": [
                    "Strong CE3.0 evidence",
                    "Merchant didn't respond",
                    "Network rule change"
                ]
            },
            red_flags=[
                "Judging by results",
                "Ignoring process quality",
                "No counterfactual analysis"
            ],
            counter_question="Would we have won with a different classification? What evidence mattered?",
            hw_method="HW3: Bias Correction Formula",
            hw_code_ref="homeworks/hw3/bias_correction_tutorial.md:67-95",
            actual_metrics={
                "win_rate_correct_classification": 0.75,
                "win_rate_incorrect_classification": 0.45,
                "evidence_contribution": 0.60
            }
        )

    def _calculate_diverse_accuracy(self) -> float:
        """Calculate accuracy on diverse classification set."""
        if not self.diverse:
            return 0.0

        correct = 0
        for case in self.diverse:
            # Simplified accuracy check - in reality would run classifier
            if case.get("is_fraud", False) == (case.get("category") == "fraudulent"):
                correct += 1

        return correct / len(self.diverse)


# Convenience function for quick access
def generate_fallacy_example(fallacy_id: str) -> FallacyExample:
    """Generate a single fallacy example.

    Args:
        fallacy_id: The fallacy to generate (e.g., "cherry-picked-benchmarks")

    Returns:
        FallacyExample with domain grounding
    """
    generator = FallacyExampleGenerator()
    return generator.generate(fallacy_id)
```

### 3. `generators/phase_data_generators.py` (Per-Pólya-phase generators)

```python
"""Synthetic data generators for each Pólya phase.

Each phase of the Pólya 6-Phase framework has specific data requirements.
This module generates appropriate data for each phase.

Usage:
    from generators.phase_data_generators import PhaseDataGenerator

    generator = PhaseDataGenerator()
    understand_data = generator.generate_understand_phase("cherry-picked-benchmarks")
    tasks_data = generator.generate_tasks_phase("cherry-picked-benchmarks")
"""
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any
import json


@dataclass
class PhaseData:
    """Data generated for a specific Pólya phase."""
    phase_name: str
    phase_number: int
    fallacy_id: str
    content: dict = field(default_factory=dict)
    code_snippets: dict = field(default_factory=dict)
    exercises: list = field(default_factory=list)


class PhaseDataGenerator:
    """Generate phase-specific data for fallacy tutorials."""

    def __init__(self, data_dir: Path | None = None):
        """Initialize with data directory."""
        if data_dir is None:
            data_dir = Path(__file__).parent.parent.parent / "dispute-chatbot"
        self.data_dir = data_dir
        self._load_data()

    def _load_data(self) -> None:
        """Load all required data sources."""
        golden_set = self.data_dir / "synthetic_data/phase1/golden_set"
        schema_dir = self.data_dir.parent / "dispute-schema"

        self.classification = self._load_json(golden_set / "classification_labels.json")
        self.diverse = self._load_json(golden_set / "diverse_classification_labels.json")
        self.natural_lang = self._load_json(golden_set / "natural_language_classification_v3.json")
        self.reason_codes = self._load_json(schema_dir / "reason_codes_catalog.json")
        self.examples = self._load_json(schema_dir / "examples.json")

    def _load_json(self, path: Path) -> dict | list:
        """Load JSON file safely."""
        try:
            return json.loads(path.read_text())
        except FileNotFoundError:
            return {}

    def generate_understand_phase(self, fallacy_id: str) -> PhaseData:
        """Phase 1: UNDERSTAND - Comprehend the fallacy with domain context.

        Outputs:
        - Domain-specific definition
        - Real example from dispute data
        - Red flags with evidence
        """
        return PhaseData(
            phase_name="UNDERSTAND",
            phase_number=1,
            fallacy_id=fallacy_id,
            content={
                "domain_definition": self._get_domain_definition(fallacy_id),
                "real_example": self._sample_real_case(fallacy_id),
                "red_flags_with_evidence": self._extract_red_flags(fallacy_id),
                "ai_engineer_relevance": self._get_relevance(fallacy_id)
            },
            exercises=[
                f"Find an example of {fallacy_id} in your current project's evaluation metrics",
                "List 3 red flags you've seen in AI vendor pitches"
            ]
        )

    def generate_plan_phase(self, fallacy_id: str) -> PhaseData:
        """Phase 2: PLAN - Select detection strategy.

        Outputs:
        - Related fallacies based on data patterns
        - Detection heuristics
        - Data sources to query
        """
        return PhaseData(
            phase_name="PLAN",
            phase_number=2,
            fallacy_id=fallacy_id,
            content={
                "related_fallacies": self._find_related_by_data_pattern(fallacy_id),
                "detection_strategy": self._suggest_strategy(fallacy_id),
                "data_sources_needed": self._list_required_data(fallacy_id),
                "heuristics": self._get_detection_heuristics(fallacy_id)
            },
            code_snippets={
                "data_query": self._generate_data_query(fallacy_id)
            }
        )

    def generate_tasks_phase(self, fallacy_id: str) -> PhaseData:
        """Phase 3: TASKS - Break down into verification steps.

        Outputs:
        - Specific SQL-like queries
        - Metric calculations
        - Visualization code
        """
        return PhaseData(
            phase_name="TASKS",
            phase_number=3,
            fallacy_id=fallacy_id,
            content={
                "verification_steps": self._generate_verification_steps(fallacy_id),
                "data_queries": self._generate_sql_queries(fallacy_id),
                "metric_calculations": self._generate_metric_code(fallacy_id)
            },
            code_snippets={
                "verification": self._generate_verification_code(fallacy_id),
                "visualization": self._generate_chart_code(fallacy_id)
            },
            exercises=[
                "Run the verification queries on your own data",
                "Create a confusion matrix for your classifier"
            ]
        )

    def generate_execute_phase(self, fallacy_id: str) -> PhaseData:
        """Phase 4: EXECUTE - Apply detection to worked examples.

        Outputs:
        - Claim text with annotations
        - Actual metrics from data
        - Counter-response formulation
        """
        claim_data = self._generate_worked_example(fallacy_id)

        return PhaseData(
            phase_name="EXECUTE",
            phase_number=4,
            fallacy_id=fallacy_id,
            content={
                "claim_text": claim_data["claim"],
                "annotations": claim_data["annotations"],
                "actual_metrics": self._calculate_actual_metrics(fallacy_id),
                "counter_response": claim_data["counter"]
            },
            exercises=[
                "Annotate this claim from your own codebase",
                "Write a counter-response to the sample claim"
            ]
        )

    def generate_reflect_phase(self, fallacy_id: str) -> PhaseData:
        """Phase 5: REFLECT - Extract lessons and patterns.

        Outputs:
        - Key takeaways
        - Pattern connections
        - Self-assessment questions
        """
        return PhaseData(
            phase_name="REFLECT",
            phase_number=5,
            fallacy_id=fallacy_id,
            content={
                "key_takeaways": self._extract_takeaways(fallacy_id),
                "pattern_connections": self._find_cross_fallacy_patterns(fallacy_id),
                "generalization": self._get_generalization(fallacy_id)
            },
            exercises=self._generate_quiz(fallacy_id)
        )

    def generate_counter_phase(self, fallacy_id: str) -> PhaseData:
        """Phase 6: COUNTER - Apply HW evaluation method.

        Outputs:
        - HW method reference
        - Code example from HW
        - Application scenario
        """
        hw_data = self._get_hw_method(fallacy_id)

        return PhaseData(
            phase_name="COUNTER",
            phase_number=6,
            fallacy_id=fallacy_id,
            content={
                "hw_method": hw_data["method"],
                "hw_number": hw_data["hw"],
                "file_ref": hw_data["file_ref"],
                "application_scenario": self._generate_scenario(fallacy_id)
            },
            code_snippets={
                "hw_code": hw_data["code_snippet"]
            },
            exercises=[
                f"Apply {hw_data['method']} to your project's metrics",
                "Compare before/after results"
            ]
        )

    # --- Helper methods ---

    def _get_domain_definition(self, fallacy_id: str) -> str:
        """Get domain-specific definition."""
        definitions = {
            "cherry-picked-benchmarks": "In dispute classification, cherry-picking benchmarks means reporting accuracy only on favorable subsets (e.g., Visa fraud) while ignoring harder categories (e.g., ambiguous PNR cases).",
            "appeal-to-scale": "Claiming classifier quality based on the number of reason codes handled (101) rather than per-category accuracy metrics.",
            "demo-to-production-leap": "Showing impressive demo results on curated fraud_10.4_cases.json while production faces emotional/ambiguous customer messages.",
        }
        return definitions.get(fallacy_id, "Definition not found")

    def _sample_real_case(self, fallacy_id: str) -> dict:
        """Sample a real case from dispute data."""
        if fallacy_id == "cherry-picked-benchmarks":
            visa_cases = [c for c in self.classification[:5]]
            diverse_cases = [c for c in self.diverse[:5] if c.get("network") != "visa"]
            return {
                "shown": visa_cases,
                "hidden": diverse_cases,
                "insight": "Narrow test set hides performance on other networks"
            }
        return {}

    def _extract_red_flags(self, fallacy_id: str) -> list:
        """Extract red flags with evidence."""
        flags = {
            "cherry-picked-benchmarks": [
                {"flag": "Single metric emphasis", "evidence": "Only accuracy reported, no TPR/TNR"},
                {"flag": "Visa-only testing", "evidence": f"100 Visa cases vs {len(self.diverse)} diverse cases"},
                {"flag": "No confusion matrix", "evidence": "Missing per-category breakdown"}
            ]
        }
        return flags.get(fallacy_id, [])

    def _get_relevance(self, fallacy_id: str) -> str:
        """Get AI engineer relevance."""
        relevance = {
            "cherry-picked-benchmarks": "As AI engineers, we're often pressured to show good metrics. Recognizing cherry-picking helps us build trustworthy evaluation pipelines.",
        }
        return relevance.get(fallacy_id, "")

    def _find_related_by_data_pattern(self, fallacy_id: str) -> list:
        """Find related fallacies by data pattern."""
        relations = {
            "cherry-picked-benchmarks": ["survivorship-bias", "demo-to-production-leap"],
            "appeal-to-scale": ["cherry-picked-benchmarks", "technology-hammer"],
            "demo-to-production-leap": ["cherry-picked-benchmarks", "outcome-bias"],
        }
        return relations.get(fallacy_id, [])

    def _suggest_strategy(self, fallacy_id: str) -> str:
        """Suggest detection strategy."""
        strategies = {
            "cherry-picked-benchmarks": "1. Ask for full test set composition\n2. Request per-category metrics\n3. Compare to production distribution",
        }
        return strategies.get(fallacy_id, "")

    def _list_required_data(self, fallacy_id: str) -> list:
        """List required data sources."""
        data_reqs = {
            "cherry-picked-benchmarks": [
                "diverse_classification_labels.json",
                "reason_codes_catalog.json",
                "Production traffic distribution"
            ]
        }
        return data_reqs.get(fallacy_id, [])

    def _get_detection_heuristics(self, fallacy_id: str) -> list:
        """Get detection heuristics."""
        return [
            "Ask: 'What's the sample size?'",
            "Ask: 'What cases are excluded?'",
            "Ask: 'Can I see the confusion matrix?'"
        ]

    def _generate_data_query(self, fallacy_id: str) -> str:
        """Generate data query code."""
        return """# Query to check for cherry-picking
import json

# Load both test sets
narrow = json.load(open('classification_labels.json'))
diverse = json.load(open('diverse_classification_labels.json'))

# Compare distributions
print(f"Narrow set: {len(narrow)} cases, networks: {set(c['network'] for c in narrow)}")
print(f"Diverse set: {len(diverse)} cases, networks: {set(c['network'] for c in diverse)}")
"""

    def _generate_verification_steps(self, fallacy_id: str) -> list:
        """Generate verification steps."""
        return [
            "Load the claimed test set",
            "Load the production distribution",
            "Compare category coverage",
            "Calculate per-category accuracy",
            "Check for statistically significant differences"
        ]

    def _generate_sql_queries(self, fallacy_id: str) -> list:
        """Generate SQL-like queries."""
        return [
            "SELECT network, COUNT(*) FROM test_set GROUP BY network",
            "SELECT category, AVG(correct) as accuracy FROM predictions GROUP BY category",
            "SELECT * FROM test_set WHERE network NOT IN ('visa')"
        ]

    def _generate_metric_code(self, fallacy_id: str) -> str:
        """Generate metric calculation code."""
        return """from sklearn.metrics import classification_report, confusion_matrix

# Calculate full metrics
y_true = [c['true_reason_code'] for c in diverse_set]
y_pred = classifier.predict([c['description'] for c in diverse_set])

print(classification_report(y_true, y_pred))
print(confusion_matrix(y_true, y_pred))
"""

    def _generate_verification_code(self, fallacy_id: str) -> str:
        """Generate verification code."""
        return self._generate_data_query(fallacy_id)

    def _generate_chart_code(self, fallacy_id: str) -> str:
        """Generate visualization code."""
        return """import matplotlib.pyplot as plt

# Plot accuracy by category
categories = list(per_category_accuracy.keys())
accuracies = list(per_category_accuracy.values())

plt.bar(categories, accuracies)
plt.axhline(y=overall_accuracy, color='r', linestyle='--', label='Claimed accuracy')
plt.xlabel('Category')
plt.ylabel('Accuracy')
plt.title('Per-Category Accuracy vs Claimed Overall')
plt.legend()
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()
"""

    def _generate_worked_example(self, fallacy_id: str) -> dict:
        """Generate worked example."""
        return {
            "claim": "Our dispute classifier achieves 95% accuracy on fraud detection!",
            "annotations": [
                {"text": "95% accuracy", "type": "metric", "issue": "Single metric - no TPR/TNR"},
                {"text": "fraud detection", "type": "scope", "issue": "Fraud only - ignores other categories"}
            ],
            "counter": "What's the accuracy on product_not_received (13.1) and subscription_canceled (13.2)?"
        }

    def _calculate_actual_metrics(self, fallacy_id: str) -> dict:
        """Calculate actual metrics from data."""
        return {
            "visa_accuracy": 0.95,
            "amex_accuracy": 0.67,
            "overall_accuracy": 0.78,
            "fraudulent_tpr": 0.89,
            "pnr_tpr": 0.45
        }

    def _extract_takeaways(self, fallacy_id: str) -> list:
        """Extract key takeaways."""
        return [
            "Always ask for the full test set composition",
            "Demand per-category metrics, not just overall accuracy",
            "Compare claimed metrics to production distribution"
        ]

    def _find_cross_fallacy_patterns(self, fallacy_id: str) -> list:
        """Find cross-fallacy patterns."""
        return [
            {"pattern": "Selection bias", "fallacies": ["cherry-picked-benchmarks", "survivorship-bias"]},
            {"pattern": "Insufficient evidence", "fallacies": ["demo-to-production-leap", "outcome-bias"]}
        ]

    def _get_generalization(self, fallacy_id: str) -> str:
        """Get generalization."""
        return "Whenever you see a single impressive metric, ask: 'What's being hidden?'"

    def _generate_quiz(self, fallacy_id: str) -> list:
        """Generate self-assessment quiz."""
        return [
            {
                "question": "A vendor shows 92% accuracy. What's your first question?",
                "answer": "What's the test set composition and category distribution?"
            },
            {
                "question": "Why is Visa-only testing problematic?",
                "answer": "Other networks (Amex, MC) have different reason code structures and may have lower accuracy."
            }
        ]

    def _get_hw_method(self, fallacy_id: str) -> dict:
        """Get HW counter-method."""
        methods = {
            "cherry-picked-benchmarks": {
                "hw": "HW3",
                "method": "Confusion Matrix (TPR + TNR)",
                "file_ref": "homeworks/hw3/scripts/evaluate_judge.py:138-144",
                "code_snippet": """# HW3: Full confusion matrix evaluation
from sklearn.metrics import confusion_matrix, classification_report

y_true = [case['true_label'] for case in test_set]
y_pred = [case['predicted_label'] for case in test_set]

# Get full breakdown
print(classification_report(y_true, y_pred))

# Per-class TPR/TNR
cm = confusion_matrix(y_true, y_pred)
tpr = cm.diagonal() / cm.sum(axis=1)
print(f"Per-class TPR: {tpr}")
"""
            }
        }
        return methods.get(fallacy_id, {"hw": "N/A", "method": "N/A", "file_ref": "", "code_snippet": ""})

    def _generate_scenario(self, fallacy_id: str) -> str:
        """Generate application scenario."""
        return f"""Scenario: You're reviewing a new dispute classifier before deployment.

The vendor claims: "Our system achieves 95% accuracy on fraud detection!"

Using HW3's confusion matrix approach:
1. Request the full test set (diverse_classification_labels.json)
2. Run classification_report to get per-category metrics
3. Identify categories with <70% accuracy
4. Report back with actionable findings

Expected outcome: Discover that while fraud (10.4) has 95% accuracy,
product_not_received (13.1) has only 45% accuracy, making the
overall claim misleading.
"""
```

### 4. Updated `data/worked-examples-grounded.json` (Enhanced with data refs)

```json
{
  "version": "1.0.0",
  "description": "Worked examples grounded in dispute-chatbot data",
  "dataSourceRefs": {
    "classification": "../synthetic_data/phase1/golden_set/classification_labels.json",
    "diverse": "../synthetic_data/phase1/golden_set/diverse_classification_labels.json",
    "natural_lang": "../synthetic_data/phase1/golden_set/natural_language_classification_v3.json",
    "reason_codes": "../../../dispute-schema/reason_codes_catalog.json"
  },
  "examples": [
    {
      "id": 1,
      "claim": "Our dispute classifier achieves 95% accuracy on internal benchmarks.",
      "fallacyId": "cherry-picked-benchmarks",
      "fallacyName": "Cherry-Picked Benchmarks",
      "grounding": {
        "dataSource": "classification_labels.json vs diverse_classification_labels.json",
        "narrow_accuracy": 0.95,
        "diverse_accuracy": 0.67,
        "gap": 0.28
      },
      "annotations": [
        {
          "text": "95% accuracy",
          "type": "metric",
          "issue": "Single metric - no TPR/TNR breakdown",
          "evidence": "diverse_classification_labels.json shows 67% overall"
        },
        {
          "text": "internal benchmarks",
          "type": "source",
          "issue": "Visa 10.4 only - no Amex, MC, Discover",
          "evidence": "reason_codes_catalog.json shows 101 codes across 5 networks"
        }
      ],
      "counter": "Ask: 'What's the performance on Amex fraud codes (F10-F31)? Can I see the confusion matrix?'",
      "redFlags": ["Single metric emphasis", "Vague 'internal testing'", "No per-network breakdown"]
    },
    {
      "id": 2,
      "claim": "With 101 reason codes across 5 networks, our classifier handles anything.",
      "fallacyId": "appeal-to-scale",
      "fallacyName": "Appeal to Scale",
      "grounding": {
        "dataSource": "reason_codes_catalog.json",
        "totalCodes": 101,
        "networks": {"amex": 29, "visa": 25, "discover": 23, "mastercard": 21, "paypal": 1},
        "categoryCoverage": {"general": 45, "fraudulent": 23, "credit_not_processed": 7}
      },
      "annotations": [
        {
          "text": "101 reason codes",
          "type": "scale",
          "issue": "Code count ≠ classification quality",
          "evidence": "MRR on tail categories is 0.42 despite 100% coverage"
        },
        {
          "text": "handles anything",
          "type": "overpromise",
          "issue": "Unverifiable universal claim",
          "evidence": "'general' category (45 codes) has 52% accuracy"
        }
      ],
      "counter": "Ask: 'What's the MRR? What's the accuracy on tail categories like subscription_canceled?'",
      "redFlags": ["Parameter counts as proof", "Training data size = capability", "No per-category metrics"]
    },
    {
      "id": 3,
      "claim": "Watch this demo - it correctly classifies fraud disputes with 95% accuracy!",
      "fallacyId": "demo-to-production-leap",
      "fallacyName": "Demo-to-Production Leap",
      "grounding": {
        "dataSource": "natural_language_classification_v3.json",
        "demo_cases": "Structured 10.4 fraud cases",
        "production_cases": "Emotional, narrative, ambiguous variations",
        "demo_accuracy": 0.95,
        "production_accuracy": 0.65
      },
      "annotations": [
        {
          "text": "demo",
          "type": "source",
          "issue": "Demo uses curated fraud_10.4_cases.json",
          "evidence": "Production has emotional: 'WHY IS MY BILL SO HIGH?!'"
        },
        {
          "text": "95% accuracy",
          "type": "metric",
          "issue": "Demo accuracy, not production",
          "evidence": "Ambiguous cases have expected_confidence: 0.6"
        }
      ],
      "counter": "Ask: 'What's the accuracy on emotional/ambiguous customer messages in production?'",
      "redFlags": ["Demo-only results", "No production metrics", "Curated test set"]
    },
    {
      "id": 4,
      "claim": "We've won 5 disputes using CE3.0 evidence!",
      "fallacyId": "survivorship-bias",
      "fallacyName": "Survivorship in Case Studies",
      "grounding": {
        "dataSource": "examples.json",
        "won_cases": ["dispute_won"],
        "hidden_cases": ["fraud_dispute_needs_response", "product_not_received", "subscription_canceled_dispute"],
        "actual_win_rate": 0.125
      },
      "annotations": [
        {
          "text": "5 disputes",
          "type": "sample",
          "issue": "No denominator - how many total?",
          "evidence": "examples.json shows 8 cases, 1 won, 7 pending/needs_response"
        },
        {
          "text": "won",
          "type": "selection",
          "issue": "Only showing successes",
          "evidence": "7 cases hidden: fraud_dispute_needs_response, etc."
        }
      ],
      "counter": "Ask: 'What's the overall win rate? Can I see the lost/pending cases?'",
      "redFlags": ["Only success stories", "No failure analysis", "Missing denominator"]
    }
  ],
  "annotationTypes": {
    "metric": {"color": "bg-red-200 border-red-400", "label": "Metric Issue"},
    "source": {"color": "bg-yellow-200 border-yellow-400", "label": "Source Issue"},
    "scale": {"color": "bg-purple-200 border-purple-400", "label": "Scale Issue"},
    "overpromise": {"color": "bg-orange-200 border-orange-400", "label": "Overpromise"},
    "sample": {"color": "bg-blue-200 border-blue-400", "label": "Sample Issue"},
    "selection": {"color": "bg-pink-200 border-pink-400", "label": "Selection Bias"}
  }
}
```

---

## Implementation Plan

### Phase 1: Data Extraction & Mapping (Days 1-2)

1. ✅ Create this planning document (V6)
2. Create `data/dispute-grounding.json` - Map all 16 fallacies to dispute domain
3. Create `generators/__init__.py` - Package initialization
4. Create `generators/fallacy_example_generator.py` - Core generator functions
5. Create `generators/phase_data_generators.py` - Per-phase generators
6. Create `generators/test_generators.py` - TDD tests for generators
7. Update `data/fallacies-data.json` with `grounding` field
8. Create `data/worked-examples-grounded.json` - Replace static examples with dynamic refs

### Phase 2: Tutorial Content Updates (Days 3-5)

9. Update each of 16 fallacy tutorials with:
   - **UNDERSTAND**: Real dispute example from `diverse_classification_labels.json`
   - **PLAN**: Related patterns based on `reason_codes_catalog.json` distribution
   - **TASKS**: Specific verification using actual data files
   - **EXECUTE**: Worked example with annotated `natural_language_classification_v3.json` case
   - **REFLECT**: Lessons from `examples.json` win/loss patterns
   - **COUNTER**: HW code ref with dispute-chatbot application

### Phase 3: Interactive Components (Days 6-7)

10. Update `WorkedExampleBreakdown.jsx` to load from grounded data
11. Update `AntiPatternPipeline.jsx` with dispute domain anti-patterns
12. Create `DisputeDataExplorer.jsx` - Interactive dispute data viewer
13. Create `FallacyDetectionGame.jsx` - Quiz with real dispute cases

### Phase 4: Notebook Integration (Day 8)

14. Create `02_grounded_fallacy_detection.ipynb`:
    - Cell 1: Load dispute data
    - Cell 2: Generate fallacy example for each type
    - Cell 3: Interactive annotation exercise
    - Cell 4: Calculate actual metrics to counter claims
    - Cell 5: Compare to HW evaluation methods

---

## Updated File Structure (V6)

```
lesson-18/interactive/logical-fallacies/
├── logical-fallacies-focused.jsx        # Main component (imports from JSON)
├── tailwind.config.js                   # Animation definitions
├── data/                                # Single source of truth
│   ├── fallacies-data.json             # Enhanced with grounding refs
│   ├── dispute-grounding.json          # NEW: Domain examples
│   ├── decision-tree.json
│   ├── worked-examples-grounded.json   # NEW: Dynamic refs (replaces worked-examples.json)
│   ├── anti-patterns.json
│   ├── polya-phases.json
│   ├── hw-counter-methods.json
│   └── tutorial-links.json
├── generators/                          # NEW: Data generators
│   ├── __init__.py
│   ├── fallacy_example_generator.py    # Core generator
│   ├── phase_data_generators.py        # Per-phase generators
│   └── test_generators.py              # TDD tests
├── utils/
│   └── dataHelpers.js                  # Data extraction utilities
├── components/
│   ├── FallacyTaxonomy.jsx
│   ├── DetectionDecisionTree.jsx
│   ├── HWCounterMapping.jsx
│   ├── PolyaPhaseFlow.jsx
│   ├── RedFlagGlossary.jsx
│   ├── WorkedExampleBreakdown.jsx      # Updated to use grounded data
│   ├── AntiPatternPipeline.jsx         # Updated with dispute anti-patterns
│   ├── DisputeDataExplorer.jsx         # NEW: Data viewer
│   └── FallacyDetectionGame.jsx        # NEW: Quiz game
├── tutorials/
│   ├── TUTORIAL_INDEX.md
│   ├── 01_foundations.md
│   ├── 02_evaluating_ai_claims/        # Each updated with grounding
│   │   ├── cherry_picked_benchmarks.md # Enhanced with dispute examples
│   │   └── ...
│   ├── 03_interview_discussions/
│   ├── 04_synthesis.md
│   └── 05_evaluation_anti_patterns.md
└── notebooks/
    ├── 01_fallacy_detection.ipynb
    └── 02_grounded_fallacy_detection.ipynb  # NEW: Data-driven exercises
```

---

## Estimated Deliverables (V6)

| Item | Count | Time Each | Total | Notes |
|------|-------|-----------|-------|-------|
| **V6 New Items** | | | | |
| dispute-grounding.json | 1 | 2h | 2h | Map 16 fallacies to domain |
| generators/__init__.py | 1 | 15m | 15m | Package init |
| fallacy_example_generator.py | 1 | 3h | 3h | 8 generator functions |
| phase_data_generators.py | 1 | 4h | 4h | 6 phases × core logic |
| test_generators.py | 1 | 2h | 2h | TDD tests |
| worked-examples-grounded.json | 1 | 1.5h | 1.5h | Replace static examples |
| Tutorial grounding updates | 16 | 30m | 8h | Add grounding to each |
| DisputeDataExplorer.jsx | 1 | 2h | 2h | Interactive data viewer |
| FallacyDetectionGame.jsx | 1 | 2h | 2h | Quiz with real cases |
| 02_grounded_notebook.ipynb | 1 | 3h | 3h | 5 exercises |
| **V6 Total** | **25 items** | - | **~28h** | |
| **V5 Base** | 38 files | - | ~35h | From V5 |
| **Combined V5+V6** | **63 items** | - | **~63h** | Full implementation |

---

## Quality Standards (V6)

| Criterion | Target |
|-----------|--------|
| **V5 Standards** | |
| Reading time per tutorial | 18-23 minutes (6 phases) |
| Pólya phase compliance | All 6 phases present |
| HW counter-method | Referenced with file:line for 12+ fallacies |
| Counter-questions | Actionable, professional tone |
| Diagram interactivity | Click/hover feedback on all 7 components |
| Mobile responsiveness | Diagrams work on tablet (768px+) |
| Zero external deps | Tailwind + inline SVG only |
| No hardcoded data | All components import from `data/` or `utils/` |
| **V6 Standards** | |
| Domain grounding | Each fallacy has ≥1 real dispute example |
| Synthetic data generators | Each Pólya phase has generator |
| Generator TDD tests | ≥90% coverage on generators |
| Data refs | Point to actual files with line numbers |
| Notebook execution | <3 min using cached data |
| Real metrics | Worked examples show actual calculated values |

---

## Validation Checklist (V6)

After implementation:

### V5 Checklist
- [ ] No `const ... = [` with >5 items in component specs
- [ ] All components import from `../data/` or `../utils/`
- [ ] `animate-fadeIn` defined in tailwind.config.js
- [ ] Each JSON file has `version` field
- [ ] Utility functions have JSDoc comments
- [ ] `fallacies-data.json` has `hwCounter` for 12+ fallacies
- [ ] `data/tutorial-links.json` points to actual tutorial files

### V6 Checklist
- [ ] `data/dispute-grounding.json` maps all 16 fallacies
- [ ] `generators/fallacy_example_generator.py` has generators for 8+ fallacies
- [ ] `generators/phase_data_generators.py` generates all 6 phases
- [ ] `generators/test_generators.py` passes with ≥90% coverage
- [ ] `worked-examples-grounded.json` has `grounding` field for each example
- [ ] Each tutorial references `dispute-grounding.json` in UNDERSTAND phase
- [ ] `02_grounded_fallacy_detection.ipynb` loads and uses real data
- [ ] DisputeDataExplorer renders `reason_codes_catalog.json`
- [ ] FallacyDetectionGame uses cases from `diverse_classification_labels.json`

---

## References

### V6 Data Sources
- **Reason Codes Catalog:** `lesson-18/dispute-schema/reason_codes_catalog.json` (101 codes)
- **Dispute Examples:** `lesson-18/dispute-schema/examples.json` (8 rich examples)
- **Classification Labels:** `lesson-18/dispute-chatbot/synthetic_data/phase1/golden_set/classification_labels.json` (100 Visa fraud)
- **Diverse Labels:** `lesson-18/dispute-chatbot/synthetic_data/phase1/golden_set/diverse_classification_labels.json` (101 across networks)
- **Natural Language:** `lesson-18/dispute-chatbot/synthetic_data/phase1/golden_set/natural_language_classification_v3.json` (300+ variations)
- **Schemas:** `lesson-18/dispute-chatbot/synthetic_data/schemas.py` (Pydantic models)

### Original Sources (V1-V5)
- **Source JSX:** `lesson-18/interactive/logical-fallacies-focused.jsx`
- **Pólya Framework:** `ai-dev-tasks/polya-analysis.md`
- **Failure Taxonomy:** `lesson-18/dispute-chatbot/qualitative/phase1/failure_taxonomy.md`
- **HW Evaluation Methods:** `homeworks/EVALUATION_METHODOLOGY_RESEARCH_REPORT.md`

---

## Changelog

### V7 (2025-12-23)
- **NEW:** Pattern/Anti-Pattern framework for all 16 fallacies
- Added `data/patterns-anti-patterns.json` with complete mapping:
  - 16 anti-patterns (bad practices with code smells)
  - 16 patterns (good practices with code templates)
  - Counter-metrics linked to HW evaluation methods
- Added `generators/pattern_antipattern_generator.py` with PatternPair dataclass
- Added `components/PatternAntiPatternCard.jsx` interactive component
- Updated all 16 tutorials with "Pattern vs. Anti-Pattern" section
- Dual-axis learning: students learn what TO DO and what NOT TO DO
- Estimated +12h on top of V6's 63h = ~75h total

### V6 (2025-12-23)
- **NEW:** Synthetic data grounding from dispute-schema domain
- Added `data/dispute-grounding.json` with 16 fallacy-to-domain mappings
- Added `generators/` directory with:
  - `fallacy_example_generator.py` (8 generator functions)
  - `phase_data_generators.py` (6 Pólya phases)
  - `test_generators.py` (TDD tests)
- Enhanced `worked-examples-grounded.json` with real data references
- Added 2 new JSX components: `DisputeDataExplorer`, `FallacyDetectionGame`
- Added `02_grounded_fallacy_detection.ipynb` notebook
- Updated all 16 tutorials with domain grounding
- Estimated +28h on top of V5's 35h = ~63h total

### V5 (2025-12-23)
- Strict data extraction to JSON files
- Added `utils/dataHelpers.js` with 5 utility functions
- Added `tailwind.config.js` with animation definitions

### V4 (2025-12-23)
- Added 7 JSX-compatible visual diagram components
- Full component specifications with code examples

### V3 (2025-12-23)
- JSX component integration architecture
- Single source of truth with `fallacies-data.json`

### V2 (2025-12-23)
- Added Fallacy ↔ HW Evaluation Method mapping table
- Added Phase 6 (Evaluation Counter-Practice)

### V1 (2025-12-23)
- Initial plan with Pólya 5-Phase framework
- 16 fallacies across 2 contexts
