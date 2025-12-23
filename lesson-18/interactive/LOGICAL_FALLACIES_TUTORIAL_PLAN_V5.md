# Plan: Logical Fallacies Deep Dive Tutorial for AI Engineers (V5)

**Created:** 2025-12-23
**Updated:** 2025-12-23 (V5 - Strict Data Extraction & Tailwind Config)
**Source Analysis:** `logical-fallacies-focused.jsx`, `polya-analysis.md`, lesson-18 context, **homeworks/HW1-5 evaluation methodologies**
**Status:** Planning Phase

---

## Version History

| Version | Date | Key Changes |
|---------|------|-------------|
| V1 | 2025-12-23 | Initial plan with Pólya 5-Phase framework, 16 fallacies |
| V2 | 2025-12-23 | Added HW evaluation method mappings, Phase 6 counter-practice |
| V3 | 2025-12-23 | JSX component integration, single source of truth architecture |
| V4 | 2025-12-23 | JSX-compatible visual diagram components (7 new) |
| **V5** | 2025-12-23 | **Strict data extraction to JSON, Tailwind animation config** |

---

## Overview

Create a comprehensive tutorial system teaching **16 logical fallacies** critical for AI professionals, using the **Pólya 5-Phase Framework** and grounded with real examples from the lesson-18 dispute chatbot project.

**V2 Enhancement:** Explicit integration with homework evaluation methodologies that directly counter these fallacies.

**V3 Enhancement:** Tight integration with `logical-fallacies-focused.jsx` as the single source of truth for fallacy definitions, examples, red flags, and counters.

**V4 Enhancement:** Seven JSX-compatible visual diagram components using Tailwind CSS and inline SVG (zero external dependencies).

**V5 Enhancement:** Strict data extraction to JSON files + Tailwind animation configuration. All hardcoded data in V4 component specs moved to `data/` directory with utility functions for extraction.

---

## V5 Key Enhancement: Strict Data Extraction

### Problem Identified

V4 component specifications contain **hardcoded inline data** that violates the single source of truth principle stated in V3/V4:

| Component | Hardcoded Data | V4 Lines | Items |
|-----------|---------------|----------|-------|
| `DetectionDecisionTree.jsx` | `const decisionTree = {...}` | 202-278 | 12 nodes |
| `HWCounterMapping.jsx` | `const mappings = [...]` | 409-420 | 11 |
| `PolyaPhaseFlow.jsx` | `const phases = [...]` | 532-587 | 6 |
| `RedFlagGlossary.jsx` | `const allFlags = [...]` | 717-768 | 50+ |
| `WorkedExampleBreakdown.jsx` | `const examples = [...]` | 883-929 | 4 |
| `AntiPatternPipeline.jsx` | `const antiPatterns = [...]` | 1110-1153 | 7 |

**Total: 90+ hardcoded items across 6 components**

### Solution: Extended JSON Data Files

#### 1. `data/fallacies-data.json` (Enhanced from V3)

```json
{
  "version": "1.0.0",
  "contexts": {
    "Evaluating AI Claims": {
      "color": "indigo",
      "intro": "Common fallacies in AI product pitches, research papers, and vendor demos",
      "fallacies": [
        {
          "id": "cherry-picked-benchmarks",
          "name": "Cherry-Picked Benchmarks",
          "type": "Hasty Generalization",
          "definition": "Selecting only favorable metrics while ignoring failures or edge cases.",
          "example": "\"Our model achieves 95% accuracy!\" (on a curated test set, while production accuracy is 67%)",
          "redFlags": ["Single metric emphasis", "No error analysis", "Vague 'internal testing'"],
          "counter": "Ask: 'What's the performance on adversarial cases? Can I see the confusion matrix?'",
          "hwCounter": {
            "hw": "HW3",
            "method": "Confusion Matrix (TPR + TNR)",
            "fileRef": "homeworks/hw3/scripts/evaluate_judge.py:138-144"
          }
        }
      ]
    },
    "Interview Discussions": {
      "color": "emerald",
      "intro": "Fallacies to spot (and avoid) when discussing technical decisions and experience",
      "fallacies": []
    }
  },
  "metadata": {
    "totalFallacies": 16,
    "totalRedFlags": 48,
    "contexts": ["Evaluating AI Claims", "Interview Discussions"]
  }
}
```

#### 2. `data/decision-tree.json` (New)

```json
{
  "version": "1.0.0",
  "description": "Interactive flowchart for fallacy identification",
  "nodes": {
    "start": {
      "question": "What type of claim is being made?",
      "options": [
        { "label": "AI capability/performance", "next": "ai_claims" },
        { "label": "Past decisions/experience", "next": "interview" }
      ]
    },
    "ai_claims": {
      "question": "What aspect is emphasized?",
      "options": [
        { "label": "Metrics/benchmarks", "next": "metrics" },
        { "label": "Scale/size", "next": "scale" },
        { "label": "Human-like abilities", "next": "anthropo" },
        { "label": "Success stories", "next": "survivorship" }
      ]
    },
    "metrics": {
      "question": "Are limitations disclosed?",
      "options": [
        { "label": "No error analysis shown", "result": "Cherry-Picked Benchmarks" },
        { "label": "Demo only, no production data", "result": "Demo-to-Production Leap" },
        { "label": "Before/after without controls", "result": "Correlation as Causation" }
      ]
    },
    "scale": {
      "question": "Is scale tied to specific capability?",
      "options": [
        { "label": "No, just 'handles anything'", "result": "Appeal to Scale" },
        { "label": "Claims inevitable progress", "result": "AGI Slippery Slope" }
      ]
    },
    "anthropo": {
      "question": "What terms are used?",
      "options": [
        { "label": "'Understands', 'thinks', 'knows'", "result": "Anthropomorphization" }
      ]
    },
    "survivorship": {
      "question": "Are failures mentioned?",
      "options": [
        { "label": "Only success stories", "result": "Survivorship in Case Studies" }
      ]
    },
    "interview": {
      "question": "What is being discussed?",
      "options": [
        { "label": "Judging past outcomes", "next": "outcomes" },
        { "label": "Technical approach", "next": "tech_approach" },
        { "label": "Experience claims", "next": "experience" }
      ]
    },
    "outcomes": {
      "question": "How is success defined?",
      "options": [
        { "label": "By results, ignoring context", "result": "Outcome Bias" },
        { "label": "Criteria changed after the fact", "result": "Moving Goalposts" }
      ]
    },
    "tech_approach": {
      "question": "How is the approach justified?",
      "options": [
        { "label": "Company prestige cited", "result": "Appeal to Big Tech" },
        { "label": "Familiarity, not fit", "result": "Technology Hammer" },
        { "label": "Only two options presented", "result": "False Dichotomy: Build vs. Buy" }
      ]
    },
    "experience": {
      "question": "How is contribution described?",
      "options": [
        { "label": "Vague ownership ('led', 'architected')", "result": "Resume Inflation" },
        { "label": "Past teams criticized unfairly", "result": "Straw Man on Past Decisions" },
        { "label": "Only recent work valued", "result": "Recency Bias" },
        { "label": "Must be hands-on OR strategic", "result": "False Expertise Dichotomy" }
      ]
    }
  }
}
```

#### 3. `data/worked-examples.json` (New)

```json
{
  "version": "1.0.0",
  "description": "Annotated claim examples for WorkedExampleBreakdown component",
  "examples": [
    {
      "id": 1,
      "claim": "Our model achieves 95% accuracy on internal benchmarks.",
      "fallacyId": "cherry-picked-benchmarks",
      "fallacyName": "Cherry-Picked Benchmarks",
      "annotations": [
        { "text": "95% accuracy", "type": "metric", "issue": "Single metric - no TPR/TNR breakdown" },
        { "text": "internal benchmarks", "type": "source", "issue": "Vague testing - no external validation" }
      ],
      "counter": "Ask: 'What's the performance on adversarial cases? Can I see the confusion matrix?'",
      "redFlags": ["Single metric emphasis", "Vague 'internal testing'"]
    },
    {
      "id": 2,
      "claim": "With 70B parameters trained on the entire internet, it can handle anything.",
      "fallacyId": "appeal-to-scale",
      "fallacyName": "Appeal to Scale",
      "annotations": [
        { "text": "70B parameters", "type": "scale", "issue": "Parameter count ≠ task performance" },
        { "text": "entire internet", "type": "scale", "issue": "Data quantity ≠ quality" },
        { "text": "handle anything", "type": "overpromise", "issue": "Unverifiable universal claim" }
      ],
      "counter": "Ask: 'What specific capability does that scale enable for MY use case?'",
      "redFlags": ["Parameter counts as proof", "Training data size = capability"]
    },
    {
      "id": 3,
      "claim": "The model understands context and reasons about your business needs.",
      "fallacyId": "anthropomorphization",
      "fallacyName": "Anthropomorphization",
      "annotations": [
        { "text": "understands", "type": "anthropo", "issue": "Human cognitive term - implies comprehension" },
        { "text": "reasons about", "type": "anthropo", "issue": "Suggests deliberate thought process" }
      ],
      "counter": "Reframe: 'What specific mechanism produces this behavior? How does it fail?'",
      "redFlags": ["'Understands'", "'Thinks'", "'Knows'"]
    },
    {
      "id": 4,
      "claim": "At Google we did it this way, so that's the right approach.",
      "fallacyId": "appeal-to-big-tech",
      "fallacyName": "Appeal to Big Tech",
      "annotations": [
        { "text": "At Google", "type": "authority", "issue": "Company prestige ≠ universal applicability" },
        { "text": "the right approach", "type": "absolute", "issue": "No context consideration" }
      ],
      "counter": "Ask: 'How would that approach need to adapt for our scale/constraints?'",
      "redFlags": ["Company name-dropping", "Assuming transferability"]
    }
  ],
  "annotationTypes": {
    "metric": { "color": "bg-red-200 border-red-400", "label": "Metric Issue" },
    "source": { "color": "bg-yellow-200 border-yellow-400", "label": "Source Issue" },
    "scale": { "color": "bg-purple-200 border-purple-400", "label": "Scale Issue" },
    "overpromise": { "color": "bg-orange-200 border-orange-400", "label": "Overpromise" },
    "anthropo": { "color": "bg-blue-200 border-blue-400", "label": "Anthropomorphization" },
    "authority": { "color": "bg-pink-200 border-pink-400", "label": "Authority Appeal" },
    "absolute": { "color": "bg-amber-200 border-amber-400", "label": "Absolute Claim" }
  }
}
```

#### 4. `data/anti-patterns.json` (New)

```json
{
  "version": "1.0.0",
  "description": "Evaluation anti-patterns mapped to fallacies and counter-methods",
  "antiPatterns": [
    {
      "id": 1,
      "antiPattern": { "name": "Only Reporting Accuracy", "icon": "📊", "description": "Reporting '95% accuracy' without TPR/TNR breakdown" },
      "fallacy": { "name": "Cherry-Picked Benchmarks", "type": "Hasty Generalization" },
      "counter": { "method": "Confusion Matrix", "hw": "HW3", "metric": "TPR + TNR" }
    },
    {
      "id": 2,
      "antiPattern": { "name": "Using Dev Set for Final Eval", "icon": "🔄", "description": "Iterating 20x on dev set, reporting as final" },
      "fallacy": { "name": "Demo-to-Production Leap", "type": "Hasty Generalization" },
      "counter": { "method": "Test Set + CI", "hw": "HW3", "metric": "95% Confidence Intervals" }
    },
    {
      "id": 3,
      "antiPattern": { "name": "Post-Hoc Metric Selection", "icon": "📈", "description": "Choosing metrics after seeing results" },
      "fallacy": { "name": "Moving Goalposts", "type": "Moving Goalposts" },
      "counter": { "method": "Pre-defined Thresholds", "hw": "HW3", "metric": "TPR/TNR targets" }
    },
    {
      "id": 4,
      "antiPattern": { "name": "Citing Model Size", "icon": "📦", "description": "'70B parameters trained on entire internet'" },
      "fallacy": { "name": "Appeal to Scale", "type": "Appeal to Authority" },
      "counter": { "method": "MRR Evaluation", "hw": "HW4", "metric": "Ranking quality" }
    },
    {
      "id": 5,
      "antiPattern": { "name": "Misattributing Failures", "icon": "🎯", "description": "'Search is broken' without LLM query check" },
      "fallacy": { "name": "Correlation as Causation", "type": "Post Hoc" },
      "counter": { "method": "Transition Matrices", "hw": "HW5", "metric": "LLM vs Tool attribution" }
    },
    {
      "id": 6,
      "antiPattern": { "name": "Showcasing Only Successes", "icon": "🏆", "description": "5 success stories, hiding 20 failures" },
      "fallacy": { "name": "Survivorship Bias", "type": "Cherry Picking" },
      "counter": { "method": "Open Coding", "hw": "HW2", "metric": "Systematic review" }
    },
    {
      "id": 7,
      "antiPattern": { "name": "Point Estimates Only", "icon": "📍", "description": "'Success rate: 87.3%' without CI" },
      "fallacy": { "name": "False Certainty", "type": "Demo-to-Production Leap" },
      "counter": { "method": "Bootstrap CI", "hw": "HW3", "metric": "95% Confidence Interval" }
    }
  ],
  "hwColors": {
    "HW2": { "bg": "bg-yellow-100", "border": "border-yellow-400", "text": "text-yellow-800" },
    "HW3": { "bg": "bg-red-100", "border": "border-red-400", "text": "text-red-800" },
    "HW4": { "bg": "bg-purple-100", "border": "border-purple-400", "text": "text-purple-800" },
    "HW5": { "bg": "bg-orange-100", "border": "border-orange-400", "text": "text-orange-800" }
  }
}
```

#### 5. `data/polya-phases.json` (New)

```json
{
  "version": "1.0.0",
  "description": "Pólya 6-phase detection framework",
  "phases": [
    {
      "number": 1,
      "name": "UNDERSTAND",
      "icon": "🔍",
      "duration": "~3 min",
      "description": "Comprehend the fallacy definition and red flags",
      "outputs": ["Definition clarity", "Red flag checklist", "AI engineer relevance"],
      "questions": ["What is the unknown?", "What are the data?", "What is the condition?"]
    },
    {
      "number": 2,
      "name": "PLAN",
      "icon": "📋",
      "duration": "~3 min",
      "description": "Select detection strategy and identify related patterns",
      "outputs": ["Related fallacies", "Strategic approach", "Heuristic selection"],
      "questions": ["Have you seen this before?", "What heuristic applies?"]
    },
    {
      "number": 3,
      "name": "TASKS",
      "icon": "✅",
      "duration": "~5 min",
      "description": "Break down detection into specific, verifiable steps",
      "outputs": ["Claim type identification", "Red flag spotting", "Counter-questions"],
      "questions": ["What are the specific steps?", "How will you verify each?"]
    },
    {
      "number": 4,
      "name": "EXECUTE",
      "icon": "⚡",
      "duration": "~5 min",
      "description": "Apply detection to worked examples",
      "outputs": ["Claim analysis", "Red flag matches", "Counter-response formulation"],
      "questions": ["Is each step correct?", "Did anything unexpected happen?"]
    },
    {
      "number": 5,
      "name": "REFLECT",
      "icon": "💭",
      "duration": "~4 min",
      "description": "Extract lessons and generalize patterns",
      "outputs": ["Key takeaways", "Pattern connections", "Self-assessment"],
      "questions": ["Does it satisfy requirements?", "Can this generalize?"]
    },
    {
      "number": 6,
      "name": "COUNTER",
      "icon": "🛡️",
      "duration": "~3 min",
      "description": "Apply HW evaluation method as counter-practice",
      "outputs": ["HW method reference", "Code example", "Application scenarios"],
      "questions": ["Which HW method counters this?", "When to apply?"]
    }
  ],
  "totalDuration": "~23 min"
}
```

#### 6. `data/hw-counter-methods.json` (Derived, for quick lookup)

```json
{
  "version": "1.0.0",
  "description": "Quick lookup: Fallacy → HW counter-method",
  "mappings": [
    { "fallacy": "Cherry-Picked Benchmarks", "hw": "HW3", "method": "Confusion Matrix (TPR + TNR)", "color": "red" },
    { "fallacy": "Demo-to-Production Leap", "hw": "HW3", "method": "95% Confidence Intervals", "color": "red" },
    { "fallacy": "Correlation as Causation", "hw": "HW5", "method": "Transition Matrices", "color": "orange" },
    { "fallacy": "Survivorship Bias", "hw": "HW2", "method": "Open/Axial Coding", "color": "yellow" },
    { "fallacy": "Appeal to Scale", "hw": "HW4", "method": "MRR + Baselines", "color": "purple" },
    { "fallacy": "Outcome Bias", "hw": "HW3", "method": "Bias Correction Formula", "color": "red" },
    { "fallacy": "Moving Goalposts", "hw": "HW3", "method": "Pre-defined Thresholds", "color": "red" },
    { "fallacy": "Technology Hammer", "hw": "HW4", "method": "Baseline Comparisons", "color": "purple" },
    { "fallacy": "Resume Inflation", "hw": "HW2", "method": "Axial Coding", "color": "yellow" },
    { "fallacy": "Straw Man on Past Decisions", "hw": "HW2", "method": "Document Context", "color": "yellow" },
    { "fallacy": "Recency Bias", "hw": "HW5", "method": "Full Trace Analysis", "color": "orange" }
  ],
  "hwColors": {
    "HW2": "bg-yellow-100 border-yellow-400 text-yellow-800",
    "HW3": "bg-red-100 border-red-400 text-red-800",
    "HW4": "bg-purple-100 border-purple-400 text-purple-800",
    "HW5": "bg-orange-100 border-orange-400 text-orange-800"
  }
}
```

### Utility Functions: `utils/dataHelpers.js`

```javascript
// utils/dataHelpers.js
// Utility functions for extracting and transforming fallacy data
// All functions use fallacies-data.json as single source of truth

/**
 * Extract all red flags from fallacies data
 * @param {Object} data - Fallacies data object (defaults to imported JSON)
 * @returns {Array<{flag: string, fallacy: string, type: string, context: string}>}
 */
export function extractRedFlags(data) {
  const flags = [];
  Object.entries(data.contexts).forEach(([contextName, context]) => {
    context.fallacies.forEach(fallacy => {
      fallacy.redFlags.forEach(flag => {
        flags.push({
          flag,
          fallacy: fallacy.name,
          type: fallacy.type,
          context: contextName,
        });
      });
    });
  });
  return flags;
}

/**
 * Group fallacies by their logical fallacy type
 * @param {Object} data - Fallacies data object
 * @returns {Object<string, Array>} - Fallacies grouped by type
 */
export function groupFallaciesByType(data) {
  const groups = {};
  Object.entries(data.contexts).forEach(([contextName, context]) => {
    context.fallacies.forEach(f => {
      if (!groups[f.type]) groups[f.type] = [];
      groups[f.type].push({ ...f, context: contextName });
    });
  });
  return groups;
}

/**
 * Get HW counter-method mappings from fallacies
 * @param {Object} data - Fallacies data object
 * @returns {Array<{fallacy: string, hw: string, method: string, color: string}>}
 */
export function extractHWMappings(data) {
  const mappings = [];
  const hwColors = { HW2: 'yellow', HW3: 'red', HW4: 'purple', HW5: 'orange' };

  Object.values(data.contexts).forEach(context => {
    context.fallacies.forEach(f => {
      if (f.hwCounter) {
        mappings.push({
          fallacy: f.name,
          hw: f.hwCounter.hw,
          method: f.hwCounter.method,
          color: hwColors[f.hwCounter.hw] || 'slate'
        });
      }
    });
  });
  return mappings;
}

/**
 * Find fallacy by ID
 * @param {string} id - Fallacy ID (e.g., 'cherry-picked-benchmarks')
 * @param {Object} data - Fallacies data object
 * @returns {Object|null} - Fallacy object or null if not found
 */
export function getFallacyById(id, data) {
  for (const context of Object.values(data.contexts)) {
    const found = context.fallacies.find(f => f.id === id);
    if (found) return found;
  }
  return null;
}

/**
 * Get all fallacies as flat array
 * @param {Object} data - Fallacies data object
 * @returns {Array} - All fallacies with context info
 */
export function getAllFallacies(data) {
  const all = [];
  Object.entries(data.contexts).forEach(([contextName, context]) => {
    context.fallacies.forEach(f => {
      all.push({ ...f, context: contextName });
    });
  });
  return all;
}
```

---

## V5 Key Enhancement: Tailwind Animation Configuration

### Problem Identified

Components use `animate-fadeIn` (V4 lines 635, 1031, 1051) and `animate-pulse` (line 328) without providing Tailwind config. The `animate-pulse` is built-in, but `animate-fadeIn` requires custom configuration.

**Existing JSX also uses `animate-fadeIn`** (`logical-fallacies-focused.jsx:302`).

### Solution: `tailwind.config.js`

```javascript
// lesson-18/interactive/logical-fallacies/tailwind.config.js
/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './logical-fallacies-focused.jsx',
    './components/**/*.{js,jsx}',
  ],
  theme: {
    extend: {
      animation: {
        fadeIn: 'fadeIn 0.3s ease-in-out',
        slideUp: 'slideUp 0.3s ease-out',
        scaleIn: 'scaleIn 0.2s ease-out',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0', transform: 'translateY(-10px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        slideUp: {
          '0%': { opacity: '0', transform: 'translateY(20px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        scaleIn: {
          '0%': { opacity: '0', transform: 'scale(0.95)' },
          '100%': { opacity: '1', transform: 'scale(1)' },
        },
      },
    },
  },
  plugins: [],
};
```

### Animation Usage Reference

| Animation Class | Use Case | Components |
|----------------|----------|------------|
| `animate-fadeIn` | Reveal answers, expand details | All 7 diagram components, main JSX |
| `animate-slideUp` | Toast notifications, alerts | Result cards |
| `animate-scaleIn` | Modal/card entrance | Tooltip popups |
| `animate-pulse` | Loading indicators (built-in) | Progress dots in DecisionTree |

---

## V3 Key Enhancement: JSX Component Integration

### Architecture Principle: Single Source of Truth

The `logical-fallacies-focused.jsx` component contains the canonical definitions for all 16 fallacies. Rather than duplicating this data in markdown tutorials, we:

1. **Extract to shared JSON** - Export fallacy data to `data/fallacies-data.json` for both JSX and tutorials
2. **Bidirectional linking** - JSX links to deep-dive tutorials; tutorials reference JSX for quick review
3. **Extend, don't duplicate** - Tutorials add Pólya phases, grounding examples, and HW connections

### Data Flow Architecture (V5 Updated)

```
┌─────────────────────────────────────────────────────────────────┐
│                    data/fallacies-data.json                     │
│  (Single Source of Truth: definitions, examples, red flags)     │
└─────────────────────────┬───────────────────────────────────────┘
                          │
          ┌───────────────┼───────────────┐
          ▼               ▼               ▼
┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
│ logical-fallacies│ │ Markdown        │ │ Jupyter         │
│ -focused.jsx    │ │ Tutorials       │ │ Notebook        │
│ (Interactive UI)│ │ (Deep Dives)    │ │ (Exercises)     │
└────────┬────────┘ └────────┬────────┘ └────────┬────────┘
         │                   │                   │
         ▼                   ▼                   ▼
┌─────────────────────────────────────────────────────────────────┐
│                    utils/dataHelpers.js                         │
│  (extractRedFlags, groupByType, extractHWMappings, getFallacyById)│
└─────────────────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────────┐
│                    7 Diagram Components                         │
│  (All import from data/ and utils/, zero hardcoded data)        │
└─────────────────────────────────────────────────────────────────┘
```

### Integration Files (V5 Updated)

| File | Purpose | Consumers |
|------|---------|-----------|
| `data/fallacies-data.json` | Canonical fallacy definitions with hwCounter | JSX, Tutorials, Notebook, All Diagrams |
| `data/decision-tree.json` | Decision tree navigation structure | DetectionDecisionTree.jsx |
| `data/worked-examples.json` | Annotated claim examples | WorkedExampleBreakdown.jsx |
| `data/anti-patterns.json` | Evaluation anti-patterns | AntiPatternPipeline.jsx |
| `data/polya-phases.json` | Pólya 6-phase definitions | PolyaPhaseFlow.jsx |
| `data/hw-counter-methods.json` | Quick lookup for HW mappings | HWCounterMapping.jsx, Tutorials |
| `data/tutorial-links.json` | Maps fallacy names → tutorial file paths | JSX (for "Learn More" links) |
| `utils/dataHelpers.js` | Data extraction utilities | All diagram components |
| `tailwind.config.js` | Animation definitions | All components |

---

## V4 Key Enhancement: JSX-Compatible Visual Diagrams

### Design Principles

1. **Zero External Dependencies** - All diagrams use Tailwind CSS + inline SVG only
2. **Data-Driven** - Components consume JSON data via `utils/dataHelpers.js`
3. **Interactive** - State-driven highlighting, filtering, and navigation
4. **Responsive** - Mobile-friendly layouts with Tailwind breakpoints
5. **Accessible** - Proper ARIA labels, keyboard navigation

### Diagram Component Inventory (7 Components)

| # | Component | Visualization Type | Data Source | Purpose |
|---|-----------|-------------------|-------------|---------|
| 1 | `FallacyTaxonomy.jsx` | Hierarchical grid | `groupFallaciesByType()` | Classify fallacies by type |
| 2 | `DetectionDecisionTree.jsx` | Interactive SVG flowchart | `decision-tree.json` | Guide fallacy identification |
| 3 | `HWCounterMapping.jsx` | Sankey-style connections | `extractHWMappings()` | Show fallacy → HW method links |
| 4 | `PolyaPhaseFlow.jsx` | Horizontal stepper | `polya-phases.json` | Visualize 6-phase detection process |
| 5 | `RedFlagGlossary.jsx` | Filterable card grid | `extractRedFlags()` | Quick reference for red flags |
| 6 | `WorkedExampleBreakdown.jsx` | Annotated text | `worked-examples.json` | Analyze claims with tooltips |
| 7 | `AntiPatternPipeline.jsx` | Three-column flow | `anti-patterns.json` | Anti-Pattern → Fallacy → Counter |

---

## Diagram Component Specifications (V5 - Data Import Pattern)

### Component Template (V5 Pattern)

All components follow this import pattern:

```jsx
// ComponentName.jsx - V5 Pattern
import React, { useState, useMemo } from 'react';

// Option A: Import JSON directly
import dataFromJson from '../data/relevant-data.json';

// Option B: Import utility function
import { extractRelevantData } from '../utils/dataHelpers';
import fallaciesData from '../data/fallacies-data.json';

export default function ComponentName() {
  // Extract data using utility (memoized for performance)
  const data = useMemo(() => extractRelevantData(fallaciesData), []);

  // Or use JSON directly
  const data = dataFromJson.items;

  // ... rest of component logic (no hardcoded arrays)
}
```

### 1. FallacyTaxonomy.jsx (V5)

**Purpose:** Hierarchical visualization of all 16 fallacies grouped by logical type.

**Data Source:** `utils/dataHelpers.js` → `groupFallaciesByType()`

```jsx
// FallacyTaxonomy.jsx - V5 (imports from utils)
import React, { useState, useMemo } from 'react';
import { groupFallaciesByType } from '../utils/dataHelpers';
import fallaciesData from '../data/fallacies-data.json';

const typeColors = {
  "Hasty Generalization": "bg-red-100 border-red-300",
  "Appeal to Authority": "bg-purple-100 border-purple-300",
  "Post Hoc": "bg-orange-100 border-orange-300",
  "Equivocation": "bg-blue-100 border-blue-300",
  "False Dichotomy": "bg-green-100 border-green-300",
  "Cherry Picking": "bg-yellow-100 border-yellow-300",
  "Slippery Slope": "bg-pink-100 border-pink-300",
  "Straw Man": "bg-cyan-100 border-cyan-300",
  "Moving Goalposts": "bg-amber-100 border-amber-300",
  "False Cause": "bg-lime-100 border-lime-300",
};

export default function FallacyTaxonomy() {
  const [expandedType, setExpandedType] = useState(null);

  // Extract from single source of truth
  const groups = useMemo(() => groupFallaciesByType(fallaciesData), []);

  return (
    <div className="p-4">
      <h2 className="text-xl font-bold mb-4">Fallacy Taxonomy</h2>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {Object.entries(groups).map(([type, fallacies]) => (
          <div
            key={type}
            className={`rounded-xl border-2 p-4 cursor-pointer transition-all ${
              typeColors[type] || "bg-slate-100 border-slate-300"
            } ${expandedType === type ? "ring-2 ring-offset-2 ring-slate-500" : ""}`}
            onClick={() => setExpandedType(expandedType === type ? null : type)}
          >
            <div className="flex justify-between items-center">
              <h3 className="font-semibold">{type}</h3>
              <span className="text-sm text-slate-500">
                {fallacies.length} fallac{fallacies.length === 1 ? 'y' : 'ies'}
              </span>
            </div>

            {expandedType === type && (
              <ul className="mt-3 space-y-2 animate-fadeIn">
                {fallacies.map(f => (
                  <li key={f.name} className="text-sm">
                    <span className="font-medium">{f.name}</span>
                    <span className="text-slate-500 ml-2">({f.context})</span>
                  </li>
                ))}
              </ul>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
```

### 2. DetectionDecisionTree.jsx (V5)

**Purpose:** Interactive flowchart guiding users through fallacy identification.

**Data Source:** `data/decision-tree.json`

```jsx
// DetectionDecisionTree.jsx - V5 (imports from JSON)
import React, { useState } from 'react';
import decisionTreeData from '../data/decision-tree.json';

export default function DetectionDecisionTree() {
  const [currentNode, setCurrentNode] = useState('start');
  const [history, setHistory] = useState([]);
  const [result, setResult] = useState(null);

  const decisionTree = decisionTreeData.nodes;
  const node = decisionTree[currentNode];

  const handleOption = (option) => {
    if (option.result) {
      setResult(option.result);
    } else if (option.next) {
      setHistory([...history, currentNode]);
      setCurrentNode(option.next);
    }
  };

  const handleBack = () => {
    if (history.length > 0) {
      const newHistory = [...history];
      const prevNode = newHistory.pop();
      setHistory(newHistory);
      setCurrentNode(prevNode);
      setResult(null);
    }
  };

  const handleReset = () => {
    setCurrentNode('start');
    setHistory([]);
    setResult(null);
  };

  return (
    <div className="p-6 max-w-2xl mx-auto">
      <h2 className="text-xl font-bold mb-4">🌳 Fallacy Detection Decision Tree</h2>

      {/* Progress indicator */}
      <div className="flex items-center gap-2 mb-6 text-sm text-slate-500">
        <span>Start</span>
        {history.map((_, i) => (
          <React.Fragment key={i}>
            <span>→</span>
            <span className="w-2 h-2 bg-slate-400 rounded-full" />
          </React.Fragment>
        ))}
        {!result && (
          <>
            <span>→</span>
            <span className="w-3 h-3 bg-indigo-500 rounded-full animate-pulse" />
          </>
        )}
      </div>

      {result ? (
        /* Result card */
        <div className="bg-emerald-50 border-2 border-emerald-300 rounded-xl p-6 animate-fadeIn">
          <p className="text-sm text-emerald-600 font-semibold uppercase tracking-wide mb-2">
            🎯 Detected Fallacy
          </p>
          <h3 className="text-2xl font-bold text-slate-800 mb-4">{result}</h3>
          <div className="flex gap-3">
            <button
              onClick={handleBack}
              className="px-4 py-2 bg-white border border-slate-200 rounded-lg text-sm hover:bg-slate-50"
            >
              ← Back
            </button>
            <button
              onClick={handleReset}
              className="px-4 py-2 bg-indigo-500 text-white rounded-lg text-sm hover:bg-indigo-600"
            >
              Start Over
            </button>
          </div>
        </div>
      ) : (
        /* Question card */
        <div className="bg-white border border-slate-200 rounded-xl shadow-sm">
          <div className="p-5 border-b border-slate-100">
            <p className="text-lg font-medium text-slate-800">{node.question}</p>
          </div>
          <div className="p-4 space-y-2">
            {node.options.map((option, i) => (
              <button
                key={i}
                onClick={() => handleOption(option)}
                className="w-full text-left px-4 py-3 bg-slate-50 hover:bg-indigo-50 rounded-lg transition-colors border border-transparent hover:border-indigo-200"
              >
                {option.label}
              </button>
            ))}
          </div>
          {history.length > 0 && (
            <div className="px-4 pb-4">
              <button
                onClick={handleBack}
                className="text-sm text-slate-500 hover:text-slate-700"
              >
                ← Back to previous question
              </button>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
```

### 3. HWCounterMapping.jsx (V5)

**Purpose:** Visualize connections between fallacies and HW evaluation methods.

**Data Source:** `data/hw-counter-methods.json` OR `utils/dataHelpers.js` → `extractHWMappings()`

```jsx
// HWCounterMapping.jsx - V5 (imports from JSON)
import React, { useState } from 'react';
import hwData from '../data/hw-counter-methods.json';

export default function HWCounterMapping() {
  const [activeMapping, setActiveMapping] = useState(null);

  const mappings = hwData.mappings;
  const hwColors = hwData.hwColors;

  return (
    <div className="p-6">
      <h2 className="text-xl font-bold mb-2">🔗 Fallacy ↔ HW Counter-Method Mapping</h2>
      <p className="text-slate-500 text-sm mb-6">
        Hover over a fallacy to see which homework evaluation method counters it.
      </p>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Left: Fallacies */}
        <div className="space-y-2">
          <h3 className="font-semibold text-slate-600 mb-3">Logical Fallacies</h3>
          {mappings.map((m, i) => (
            <div
              key={i}
              onMouseEnter={() => setActiveMapping(i)}
              onMouseLeave={() => setActiveMapping(null)}
              className={`px-4 py-2 rounded-lg border transition-all cursor-pointer ${
                activeMapping === i
                  ? "bg-indigo-100 border-indigo-400 shadow-md"
                  : "bg-white border-slate-200 hover:border-slate-300"
              }`}
            >
              <span className="text-sm font-medium">{m.fallacy}</span>
            </div>
          ))}
        </div>

        {/* Center: Connection indicator */}
        <div className="hidden lg:flex items-center justify-center">
          {activeMapping !== null ? (
            <div className="flex flex-col items-center gap-2">
              <div className="text-4xl">→</div>
              <div className={`px-3 py-1 rounded-full text-xs font-semibold ${
                hwColors[mappings[activeMapping].hw]
              }`}>
                {mappings[activeMapping].hw}
              </div>
              <div className="text-4xl">→</div>
            </div>
          ) : (
            <div className="text-slate-300 text-sm text-center">
              Hover over a fallacy<br />to see connection
            </div>
          )}
        </div>

        {/* Right: Methods */}
        <div className="space-y-2">
          <h3 className="font-semibold text-slate-600 mb-3">Counter-Methods</h3>
          {mappings.map((m, i) => (
            <div
              key={i}
              className={`px-4 py-2 rounded-lg border transition-all ${
                activeMapping === i
                  ? `${hwColors[m.hw]} shadow-md`
                  : "bg-slate-50 border-slate-200 text-slate-400"
              }`}
            >
              <span className="text-sm font-medium">{m.method}</span>
              <span className={`ml-2 text-xs ${activeMapping === i ? "" : "opacity-50"}`}>
                ({m.hw})
              </span>
            </div>
          ))}
        </div>
      </div>

      {/* Legend */}
      <div className="mt-8 flex flex-wrap gap-3 justify-center">
        {Object.entries(hwColors).map(([hw, classes]) => (
          <div key={hw} className={`px-3 py-1 rounded-full text-xs font-semibold border ${classes}`}>
            {hw}
          </div>
        ))}
      </div>
    </div>
  );
}
```

### 4. PolyaPhaseFlow.jsx (V5)

**Purpose:** Visualize the 6-phase detection process.

**Data Source:** `data/polya-phases.json`

```jsx
// PolyaPhaseFlow.jsx - V5 (imports from JSON)
import React, { useState } from 'react';
import phasesData from '../data/polya-phases.json';

export default function PolyaPhaseFlow() {
  const [activePhase, setActivePhase] = useState(null);

  const phases = phasesData.phases;

  return (
    <div className="p-6">
      <h2 className="text-xl font-bold mb-2">📊 Pólya 6-Phase Detection Flow</h2>
      <p className="text-slate-500 text-sm mb-6">
        Click a phase to see details. Total time: {phasesData.totalDuration} per fallacy tutorial.
      </p>

      {/* Horizontal flow */}
      <div className="flex items-start gap-2 overflow-x-auto pb-4">
        {phases.map((phase, i) => (
          <React.Fragment key={phase.number}>
            {/* Phase node */}
            <div
              onClick={() => setActivePhase(activePhase === i ? null : i)}
              className={`flex-shrink-0 w-32 cursor-pointer transition-all ${
                activePhase === i ? "scale-105" : "hover:scale-102"
              }`}
            >
              <div
                className={`rounded-xl p-4 text-center border-2 transition-all ${
                  activePhase === i
                    ? "bg-indigo-100 border-indigo-400 shadow-lg"
                    : "bg-white border-slate-200 hover:border-slate-300"
                }`}
              >
                <div className="text-2xl mb-1">{phase.icon}</div>
                <div className="font-semibold text-sm">{phase.name}</div>
                <div className="text-xs text-slate-500">{phase.duration}</div>
              </div>
            </div>

            {/* Arrow between phases */}
            {i < phases.length - 1 && (
              <div className="flex-shrink-0 flex items-center h-20 text-slate-300">
                →
              </div>
            )}
          </React.Fragment>
        ))}
      </div>

      {/* Expanded details */}
      {activePhase !== null && (
        <div className="mt-6 bg-white rounded-xl border border-slate-200 p-6 animate-fadeIn">
          <div className="flex items-center gap-3 mb-4">
            <span className="text-3xl">{phases[activePhase].icon}</span>
            <div>
              <h3 className="font-bold text-lg">
                Phase {phases[activePhase].number}: {phases[activePhase].name}
              </h3>
              <p className="text-slate-500 text-sm">{phases[activePhase].description}</p>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="bg-slate-50 rounded-lg p-4">
              <h4 className="font-semibold text-sm text-slate-600 mb-2">📝 Outputs</h4>
              <ul className="space-y-1">
                {phases[activePhase].outputs.map((output, i) => (
                  <li key={i} className="text-sm flex items-center gap-2">
                    <span className="w-1.5 h-1.5 bg-indigo-500 rounded-full" />
                    {output}
                  </li>
                ))}
              </ul>
            </div>
            <div className="bg-slate-50 rounded-lg p-4">
              <h4 className="font-semibold text-sm text-slate-600 mb-2">❓ Key Questions</h4>
              <ul className="space-y-1">
                {phases[activePhase].questions.map((q, i) => (
                  <li key={i} className="text-sm italic text-slate-600">"{q}"</li>
                ))}
              </ul>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
```

### 5. RedFlagGlossary.jsx (V5)

**Purpose:** Filterable quick reference for all red flag patterns.

**Data Source:** `utils/dataHelpers.js` → `extractRedFlags()`

```jsx
// RedFlagGlossary.jsx - V5 (imports from utils)
import React, { useState, useMemo } from 'react';
import { extractRedFlags } from '../utils/dataHelpers';
import fallaciesData from '../data/fallacies-data.json';

export default function RedFlagGlossary() {
  const [filterContext, setFilterContext] = useState('all');
  const [searchTerm, setSearchTerm] = useState('');

  // Extract from single source of truth
  const allFlags = useMemo(() => extractRedFlags(fallaciesData), []);

  const filteredFlags = useMemo(() => {
    return allFlags.filter(f => {
      const matchesContext = filterContext === 'all' || f.context === filterContext;
      const matchesSearch = searchTerm === '' ||
        f.flag.toLowerCase().includes(searchTerm.toLowerCase()) ||
        f.fallacy.toLowerCase().includes(searchTerm.toLowerCase());
      return matchesContext && matchesSearch;
    });
  }, [allFlags, filterContext, searchTerm]);

  return (
    <div className="p-6">
      <h2 className="text-xl font-bold mb-2">🚩 Red Flag Glossary</h2>
      <p className="text-slate-500 text-sm mb-4">
        {allFlags.length} red flags across {fallaciesData.metadata.totalFallacies} fallacies. Filter by context or search.
      </p>

      {/* Filters */}
      <div className="flex flex-wrap gap-3 mb-6">
        <div className="flex gap-2">
          <button
            onClick={() => setFilterContext('all')}
            className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-all ${
              filterContext === 'all'
                ? "bg-slate-800 text-white"
                : "bg-slate-100 text-slate-600 hover:bg-slate-200"
            }`}
          >
            All ({allFlags.length})
          </button>
          <button
            onClick={() => setFilterContext('Evaluating AI Claims')}
            className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-all ${
              filterContext === 'Evaluating AI Claims'
                ? "bg-indigo-500 text-white"
                : "bg-indigo-50 text-indigo-600 hover:bg-indigo-100"
            }`}
          >
            AI Claims
          </button>
          <button
            onClick={() => setFilterContext('Interview Discussions')}
            className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-all ${
              filterContext === 'Interview Discussions'
                ? "bg-emerald-500 text-white"
                : "bg-emerald-50 text-emerald-600 hover:bg-emerald-100"
            }`}
          >
            Interviews
          </button>
        </div>
        <input
          type="text"
          placeholder="Search red flags..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          className="px-3 py-1.5 border border-slate-200 rounded-lg text-sm flex-1 min-w-48"
        />
      </div>

      {/* Flag cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
        {filteredFlags.map((f, i) => (
          <div
            key={i}
            className={`p-3 rounded-lg border ${
              f.context === 'Evaluating AI Claims'
                ? "bg-indigo-50 border-indigo-200"
                : "bg-emerald-50 border-emerald-200"
            }`}
          >
            <div className="flex items-start gap-2">
              <span className="text-red-500">🚩</span>
              <div>
                <p className="font-medium text-sm">{f.flag}</p>
                <p className="text-xs text-slate-500 mt-1">
                  → {f.fallacy}
                </p>
              </div>
            </div>
          </div>
        ))}
      </div>

      {filteredFlags.length === 0 && (
        <div className="text-center py-8 text-slate-400">
          No red flags match your filters.
        </div>
      )}
    </div>
  );
}
```

### 6. WorkedExampleBreakdown.jsx (V5)

**Purpose:** Interactive analysis of fallacious claims with annotations.

**Data Source:** `data/worked-examples.json`

```jsx
// WorkedExampleBreakdown.jsx - V5 (imports from JSON)
import React, { useState } from 'react';
import examplesData from '../data/worked-examples.json';

export default function WorkedExampleBreakdown() {
  const [selectedExample, setSelectedExample] = useState(0);
  const [hoveredAnnotation, setHoveredAnnotation] = useState(null);
  const [showAnalysis, setShowAnalysis] = useState(false);

  const examples = examplesData.examples;
  const annotationColors = examplesData.annotationTypes;
  const example = examples[selectedExample];

  // Render claim with highlighted annotations
  const renderAnnotatedClaim = () => {
    let claimText = example.claim;
    const parts = [];
    let lastIndex = 0;

    // Sort annotations by position in string
    const sortedAnnotations = [...example.annotations].sort((a, b) => {
      return claimText.indexOf(a.text) - claimText.indexOf(b.text);
    });

    sortedAnnotations.forEach((ann, i) => {
      const startIdx = claimText.indexOf(ann.text, lastIndex);
      if (startIdx === -1) return;

      // Add text before annotation
      if (startIdx > lastIndex) {
        parts.push(
          <span key={`text-${i}`}>{claimText.slice(lastIndex, startIdx)}</span>
        );
      }

      // Add annotated text
      const colorClass = annotationColors[ann.type]?.color || "bg-slate-200 border-slate-400";
      parts.push(
        <span
          key={`ann-${i}`}
          className={`px-1 rounded border-b-2 cursor-help transition-all ${colorClass} ${
            hoveredAnnotation === i ? "ring-2 ring-offset-1 ring-slate-500" : ""
          }`}
          onMouseEnter={() => setHoveredAnnotation(i)}
          onMouseLeave={() => setHoveredAnnotation(null)}
        >
          {ann.text}
        </span>
      );

      lastIndex = startIdx + ann.text.length;
    });

    // Add remaining text
    if (lastIndex < claimText.length) {
      parts.push(<span key="text-end">{claimText.slice(lastIndex)}</span>);
    }

    return parts;
  };

  return (
    <div className="p-6 max-w-3xl mx-auto">
      <h2 className="text-xl font-bold mb-2">🔬 Worked Example Breakdown</h2>
      <p className="text-slate-500 text-sm mb-6">
        Hover over highlighted phrases to see why they're problematic.
      </p>

      {/* Example selector */}
      <div className="flex gap-2 mb-6 overflow-x-auto pb-2">
        {examples.map((ex, i) => (
          <button
            key={ex.id}
            onClick={() => { setSelectedExample(i); setShowAnalysis(false); setHoveredAnnotation(null); }}
            className={`px-4 py-2 rounded-lg text-sm font-medium whitespace-nowrap transition-all ${
              selectedExample === i
                ? "bg-slate-800 text-white"
                : "bg-slate-100 text-slate-600 hover:bg-slate-200"
            }`}
          >
            {ex.fallacyName}
          </button>
        ))}
      </div>

      {/* Claim card */}
      <div className="bg-amber-50 border-2 border-amber-200 rounded-xl p-6 mb-4">
        <p className="text-xs font-semibold text-amber-600 uppercase tracking-wide mb-2">
          Fallacious Claim
        </p>
        <p className="text-xl text-slate-800 leading-relaxed">
          "{renderAnnotatedClaim()}"
        </p>
      </div>

      {/* Annotation tooltip */}
      {hoveredAnnotation !== null && (
        <div className="bg-slate-800 text-white rounded-lg p-4 mb-4 animate-fadeIn">
          <p className="text-sm font-semibold mb-1">
            ⚠️ {example.annotations[hoveredAnnotation].text}
          </p>
          <p className="text-sm text-slate-300">
            {example.annotations[hoveredAnnotation].issue}
          </p>
        </div>
      )}

      {/* Show analysis button */}
      <button
        onClick={() => setShowAnalysis(!showAnalysis)}
        className="w-full py-3 bg-indigo-500 text-white rounded-lg font-medium hover:bg-indigo-600 transition-colors mb-4"
      >
        {showAnalysis ? "Hide Analysis" : "Show Full Analysis"}
      </button>

      {/* Full analysis */}
      {showAnalysis && (
        <div className="space-y-4 animate-fadeIn">
          {/* Detected fallacy */}
          <div className="bg-white border border-slate-200 rounded-lg p-4">
            <p className="text-xs font-semibold text-slate-500 uppercase mb-1">🎯 Detected Fallacy</p>
            <p className="font-bold text-lg">{example.fallacyName}</p>
          </div>

          {/* Red flags matched */}
          <div className="bg-rose-50 border border-rose-200 rounded-lg p-4">
            <p className="text-xs font-semibold text-rose-600 uppercase mb-2">🚩 Red Flags Matched</p>
            <div className="flex flex-wrap gap-2">
              {example.redFlags.map((flag, i) => (
                <span
                  key={i}
                  className="text-sm bg-white border border-rose-200 text-rose-700 px-2 py-1 rounded"
                >
                  {flag}
                </span>
              ))}
            </div>
          </div>

          {/* Counter response */}
          <div className="bg-emerald-50 border border-emerald-200 rounded-lg p-4">
            <p className="text-xs font-semibold text-emerald-600 uppercase mb-1">💬 Counter Response</p>
            <p className="font-medium text-slate-800">{example.counter}</p>
          </div>
        </div>
      )}
    </div>
  );
}
```

### 7. AntiPatternPipeline.jsx (V5)

**Purpose:** Show the flow from evaluation anti-pattern → fallacy → counter-method.

**Data Source:** `data/anti-patterns.json`

```jsx
// AntiPatternPipeline.jsx - V5 (imports from JSON)
import React, { useState } from 'react';
import antiPatternsData from '../data/anti-patterns.json';

export default function AntiPatternPipeline() {
  const [selectedPattern, setSelectedPattern] = useState(null);

  const antiPatterns = antiPatternsData.antiPatterns;
  const hwColors = antiPatternsData.hwColors;

  const getFallacyExplanation = (type) => {
    const explanations = {
      "Hasty Generalization": "draws broad conclusions from limited evidence",
      "Moving Goalposts": "redefines success criteria after the fact",
      "Appeal to Authority": "substitutes prestige for evidence",
      "Post Hoc": "confuses correlation with causation",
      "Cherry Picking": "selectively presents favorable evidence",
    };
    return explanations[type] || "uses flawed reasoning";
  };

  return (
    <div className="p-6">
      <h2 className="text-xl font-bold mb-2">🔄 Anti-Pattern → Fallacy → Counter Pipeline</h2>
      <p className="text-slate-500 text-sm mb-6">
        Click a row to see the full transformation from evaluation mistake to rigorous counter-method.
      </p>

      {/* Header row */}
      <div className="hidden lg:grid lg:grid-cols-7 gap-2 mb-4 text-sm font-semibold text-slate-600">
        <div className="col-span-2">Anti-Pattern</div>
        <div className="col-span-1 text-center">→</div>
        <div className="col-span-2">Fallacy</div>
        <div className="col-span-1 text-center">→</div>
        <div className="col-span-1">Counter</div>
      </div>

      {/* Pipeline rows */}
      <div className="space-y-3">
        {antiPatterns.map((item) => (
          <div
            key={item.id}
            onClick={() => setSelectedPattern(selectedPattern === item.id ? null : item.id)}
            className={`rounded-xl border-2 p-4 cursor-pointer transition-all ${
              selectedPattern === item.id
                ? "border-indigo-400 bg-indigo-50 shadow-lg"
                : "border-slate-200 bg-white hover:border-slate-300"
            }`}
          >
            {/* Compact row */}
            <div className="grid grid-cols-1 lg:grid-cols-7 gap-4 items-center">
              {/* Anti-Pattern */}
              <div className="col-span-2 flex items-center gap-3">
                <span className="text-2xl">{item.antiPattern.icon}</span>
                <div>
                  <p className="font-semibold text-sm">{item.antiPattern.name}</p>
                  <p className="text-xs text-slate-500 lg:hidden">{item.antiPattern.description}</p>
                </div>
              </div>

              {/* Arrow 1 */}
              <div className="hidden lg:block col-span-1 text-center text-slate-400 text-xl">
                →
              </div>

              {/* Fallacy */}
              <div className="col-span-2">
                <p className="font-semibold text-sm text-rose-700">{item.fallacy.name}</p>
                <p className="text-xs text-slate-500">{item.fallacy.type}</p>
              </div>

              {/* Arrow 2 */}
              <div className="hidden lg:block col-span-1 text-center text-slate-400 text-xl">
                →
              </div>

              {/* Counter */}
              <div className="col-span-1">
                <span className={`inline-block px-2 py-1 rounded text-xs font-semibold ${
                  hwColors[item.counter.hw].bg
                } ${hwColors[item.counter.hw].text}`}>
                  {item.counter.hw}: {item.counter.method}
                </span>
              </div>
            </div>

            {/* Expanded details */}
            {selectedPattern === item.id && (
              <div className="mt-4 pt-4 border-t border-slate-200 grid grid-cols-1 md:grid-cols-3 gap-4 animate-fadeIn">
                <div className="bg-slate-50 rounded-lg p-3">
                  <p className="text-xs font-semibold text-slate-500 uppercase mb-1">The Mistake</p>
                  <p className="text-sm">{item.antiPattern.description}</p>
                </div>
                <div className="bg-rose-50 rounded-lg p-3">
                  <p className="text-xs font-semibold text-rose-600 uppercase mb-1">Why It's Flawed</p>
                  <p className="text-sm">
                    This is a form of <strong>{item.fallacy.type}</strong> because it {getFallacyExplanation(item.fallacy.type)}.
                  </p>
                </div>
                <div className={`rounded-lg p-3 ${hwColors[item.counter.hw].bg}`}>
                  <p className={`text-xs font-semibold uppercase mb-1 ${hwColors[item.counter.hw].text}`}>
                    Counter-Method ({item.counter.hw})
                  </p>
                  <p className="text-sm">
                    Use <strong>{item.counter.method}</strong> to ensure <strong>{item.counter.metric}</strong>.
                  </p>
                </div>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
```

---

## Updated File Structure (V5)

```
lesson-18/interactive/logical-fallacies/
├── logical-fallacies-focused.jsx        # Main component (imports from JSON)
├── tailwind.config.js                   # Animation definitions
├── data/                                # Single source of truth
│   ├── fallacies-data.json             # Canonical fallacy definitions (enhanced)
│   ├── decision-tree.json              # Decision tree structure
│   ├── worked-examples.json            # Annotated claim examples
│   ├── anti-patterns.json              # Evaluation anti-patterns
│   ├── polya-phases.json               # Pólya phase definitions
│   ├── hw-counter-methods.json         # Fallacy → HW mappings (quick lookup)
│   └── tutorial-links.json             # Fallacy → tutorial paths
├── utils/                               # Data extraction utilities
│   └── dataHelpers.js                  # extractRedFlags, groupByType, etc.
├── components/
│   ├── FallacyTaxonomy.jsx             # Uses: groupFallaciesByType()
│   ├── DetectionDecisionTree.jsx        # Uses: decision-tree.json
│   ├── HWCounterMapping.jsx             # Uses: hw-counter-methods.json
│   ├── PolyaPhaseFlow.jsx              # Uses: polya-phases.json
│   ├── RedFlagGlossary.jsx             # Uses: extractRedFlags()
│   ├── WorkedExampleBreakdown.jsx       # Uses: worked-examples.json
│   └── AntiPatternPipeline.jsx          # Uses: anti-patterns.json
├── tutorials/
│   ├── TUTORIAL_INDEX.md               # Navigation hub
│   ├── 01_foundations.md               # Introduction + Pólya framework
│   ├── 02_evaluating_ai_claims/
│   │   ├── cherry_picked_benchmarks.md
│   │   ├── anthropomorphization.md
│   │   ├── appeal_to_scale.md
│   │   ├── demo_to_production_leap.md
│   │   ├── false_dichotomy_build_buy.md
│   │   ├── agi_slippery_slope.md
│   │   ├── survivorship_case_studies.md
│   │   └── correlation_as_causation.md
│   ├── 03_interview_discussions/
│   │   ├── outcome_bias.md
│   │   ├── resume_inflation.md
│   │   ├── technology_hammer.md
│   │   ├── appeal_to_big_tech.md
│   │   ├── straw_man_decisions.md
│   │   ├── moving_goalposts.md
│   │   ├── false_expertise_dichotomy.md
│   │   └── recency_bias.md
│   ├── 04_synthesis.md                 # Cross-cutting patterns + HW mapping
│   └── 05_evaluation_anti_patterns.md  # Evaluation mistakes as fallacies
└── notebooks/
    └── 01_fallacy_detection.ipynb      # 6 exercises (3 original + 3 HW-based)
```

---

## Main Component Integration (V5)

Update `logical-fallacies-focused.jsx` to include tabbed navigation:

```jsx
// logical-fallacies-focused.jsx - V5 with diagram tabs and JSON imports
import React, { useState } from 'react';
import fallaciesData from './data/fallacies-data.json';
import FallacyTaxonomy from './components/FallacyTaxonomy';
import DetectionDecisionTree from './components/DetectionDecisionTree';
import HWCounterMapping from './components/HWCounterMapping';
import PolyaPhaseFlow from './components/PolyaPhaseFlow';
import RedFlagGlossary from './components/RedFlagGlossary';
import WorkedExampleBreakdown from './components/WorkedExampleBreakdown';
import AntiPatternPipeline from './components/AntiPatternPipeline';

// Use imported JSON instead of inline contexts object
const contexts = fallaciesData.contexts;

const views = [
  { id: 'reference', label: '📖 Reference', icon: '📖' },
  { id: 'taxonomy', label: '🗂️ Taxonomy', icon: '🗂️' },
  { id: 'decision-tree', label: '🌳 Decision Tree', icon: '🌳' },
  { id: 'hw-mapping', label: '🔗 HW Mapping', icon: '🔗' },
  { id: 'polya-flow', label: '📊 Pólya Flow', icon: '📊' },
  { id: 'red-flags', label: '🚩 Red Flags', icon: '🚩' },
  { id: 'examples', label: '🔬 Examples', icon: '🔬' },
  { id: 'anti-patterns', label: '🔄 Anti-Patterns', icon: '🔄' },
  { id: 'quiz', label: '🎯 Quiz', icon: '🎯' },
];

export default function FocusedFallaciesExplorer() {
  const [view, setView] = useState('reference');
  // ... existing state for reference view and quiz ...

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 p-6">
      <div className="max-w-5xl mx-auto">
        {/* Header */}
        <div className="flex items-center justify-between mb-2">
          <h1 className="text-2xl font-bold text-slate-800">
            Logical Fallacies for AI Professionals
          </h1>
        </div>
        <p className="text-slate-600 mb-4">
          Spot weak reasoning in AI evaluations and technical interviews
        </p>

        {/* View tabs - scrollable on mobile */}
        <div className="flex gap-2 mb-6 overflow-x-auto pb-2">
          {views.map((v) => (
            <button
              key={v.id}
              onClick={() => setView(v.id)}
              className={`px-4 py-2 rounded-lg text-sm font-medium whitespace-nowrap transition-all ${
                view === v.id
                  ? "bg-slate-800 text-white shadow-md"
                  : "bg-white border border-slate-200 text-slate-600 hover:border-slate-300"
              }`}
            >
              {v.label}
            </button>
          ))}
        </div>

        {/* Conditional rendering based on view */}
        {view === 'reference' && <ExistingReferenceView contexts={contexts} />}
        {view === 'taxonomy' && <FallacyTaxonomy />}
        {view === 'decision-tree' && <DetectionDecisionTree />}
        {view === 'hw-mapping' && <HWCounterMapping />}
        {view === 'polya-flow' && <PolyaPhaseFlow />}
        {view === 'red-flags' && <RedFlagGlossary />}
        {view === 'examples' && <WorkedExampleBreakdown />}
        {view === 'anti-patterns' && <AntiPatternPipeline />}
        {view === 'quiz' && <ExistingQuizMode contexts={contexts} />}
      </div>
    </div>
  );
}
```

---

## V2 Content (Preserved)

### Fallacy ↔ Evaluation Method Integration

| HW | Evaluation Method | Fallacy It Counters | Why It Works |
|----|-------------------|---------------------|--------------|
| HW2 | Open/Axial Coding | Survivorship Bias | Systematic review prevents cherry-picked success stories |
| HW3 | TPR/TNR + Confusion Matrix | Cherry-Picked Benchmarks | Must report all 4 quadrants, not just accuracy |
| HW3 | 95% Confidence Intervals | Demo-to-Production Leap | Quantifies uncertainty, prevents false certainty |
| HW3 | Bias Correction (judgy) | Outcome Bias | Corrects for systematic errors in judgment |
| HW4 | Recall@k at multiple k values | Cherry-Picked Benchmarks | Shows full curve, not just favorable cutoffs |
| HW4 | MRR (Mean Reciprocal Rank) | Appeal to Scale | Quality of ranking > quantity of results |
| HW5 | Transition Matrices | Correlation as Causation | Proper attribution (LLM vs Tool failure) |

### Fallacies Inventory (from logical-fallacies-focused.jsx)

#### Context 1: Evaluating AI Claims (8 fallacies)

| # | Fallacy Name | Type | Definition | HW Counter-Method |
|---|-------------|------|------------|-------------------|
| 1 | Cherry-Picked Benchmarks | Hasty Generalization | Selecting only favorable metrics while ignoring failures or edge cases | HW3: Full confusion matrix |
| 2 | Anthropomorphization | Equivocation | Using human cognitive terms that imply capabilities the AI doesn't have | HW2: Failure taxonomy (document actual behaviors) |
| 3 | Appeal to Scale | Appeal to Authority | Claiming quality because of large parameters, data, or compute | HW4: MRR shows quality ≠ quantity |
| 4 | Demo-to-Production Leap | Hasty Generalization | Assuming curated demo performance reflects real-world reliability | HW3: Confidence intervals |
| 5 | False Dichotomy: Build vs. Buy | False Dichotomy | Presenting only two extreme options when hybrid approaches exist | HW4: BM25 vs Vector vs Hybrid |
| 6 | AGI Slippery Slope | Slippery Slope | Claiming current capabilities inevitably lead to transformative AI | (No direct HW counter) |
| 7 | Survivorship in Case Studies | Cherry Picking | Showcasing only successful implementations, hiding failures | HW2: Open coding (systematic review) |
| 8 | Correlation as Causation | Post Hoc | Attributing outcomes to AI when other factors contributed | HW5: Transition matrices |

#### Context 2: Interview Discussions (8 fallacies)

| # | Fallacy Name | Type | Definition | HW Counter-Method |
|---|-------------|------|------------|-------------------|
| 1 | Outcome Bias | Post Hoc | Judging decisions by results rather than the reasoning process | HW3: Bias correction formula |
| 2 | Resume Inflation Detection | Equivocation | Vague ownership claims that obscure actual contribution | HW2: Axial coding (precise categorization) |
| 3 | Technology Hammer | False Cause | Advocating a technology because of familiarity, not fit | HW4: Baseline comparisons |
| 4 | Appeal to Big Tech | Appeal to Authority | Citing employer prestige as proof of technical judgment | (No direct HW counter) |
| 5 | Straw Man on Past Decisions | Straw Man | Mischaracterizing previous team decisions to make yourself look better | HW2: Document original context |
| 6 | Moving Goalposts on Success | Moving Goalposts | Redefining success metrics after the fact | HW3: Pre-define TPR/TNR thresholds |
| 7 | False Expertise Dichotomy | False Dichotomy | Claiming you must be either hands-on OR strategic, not both | (No direct HW counter) |
| 8 | Recency Bias | Hasty Generalization | Overweighting recent experience while discounting relevant past work | HW5: Full trace analysis |

---

## Pólya 6-Phase Framework (V2 Enhanced)

| Phase | Pólya Mapping | Core Purpose | Primary Output | Duration |
|-------|---------------|--------------|----------------|----------|
| **Understand** | Phase 1 | Comprehend requirements, context, constraints | Problem definition | ~3 min |
| **Plan** | Phase 2a | Select strategic approach, identify patterns | Solution strategy | ~3 min |
| **Tasks** | Phase 2b | Decompose into specific, executable subtasks | Task breakdown | ~5 min |
| **Execute** | Phase 3 | Implement with verification at each step | Working solution | ~5 min |
| **Reflect** | Phase 4 | Validate, extract lessons, generalize | Lessons learned | ~4 min |
| **Counter** | Phase 5 (NEW) | Apply HW evaluation method | Counter-practice | ~3 min |

---

## Implementation Sequence (V5 Updated)

### Phase 1: Data Extraction & Config (Day 1) ⭐ NEW

1. ✅ Create this planning document (V5)
2. Extract `contexts` from `logical-fallacies-focused.jsx` → `data/fallacies-data.json`
3. Add `hwCounter` field to each fallacy in JSON (from V2 mapping table)
4. Create `data/decision-tree.json` from V4 embedded structure
5. Create `data/worked-examples.json` from V4 embedded structure
6. Create `data/anti-patterns.json` from V4 embedded structure
7. Create `data/polya-phases.json` from V4 embedded structure
8. Create `data/hw-counter-methods.json` (derived quick lookup)
9. Create `utils/dataHelpers.js` with 5 utility functions
10. Create `tailwind.config.js` with animation definitions

### Phase 2: Diagram Components (Days 2-3)

11. Implement diagram components (import from JSON, no hardcoded data):
    - `RedFlagGlossary.jsx` (uses extractRedFlags())
    - `DetectionDecisionTree.jsx` (uses decision-tree.json)
    - `FallacyTaxonomy.jsx` (uses groupFallaciesByType())
    - `HWCounterMapping.jsx` (uses hw-counter-methods.json)
    - `PolyaPhaseFlow.jsx` (uses polya-phases.json)
    - `WorkedExampleBreakdown.jsx` (uses worked-examples.json)
    - `AntiPatternPipeline.jsx` (uses anti-patterns.json)

### Phase 3: Main Component Integration (Day 4)

12. Update `logical-fallacies-focused.jsx` to import from `data/fallacies-data.json`
13. Add tabbed navigation for all views
14. Import and conditionally render all diagram components
15. Add "Deep Dive" links to tutorial files

### Phase 4: Tutorials (Days 5-7)

16. Create `TUTORIAL_INDEX.md` with learning objectives and paths
17. Write `01_foundations.md` introducing Pólya framework
18. Write 8 "Evaluating AI Claims" tutorials with Phase 6
19. Write 8 "Interview Discussions" tutorials with Phase 6
20. Create `04_synthesis.md` with cross-cutting patterns
21. Create `05_evaluation_anti_patterns.md`

### Phase 5: Interactive & Polish (Day 8)

22. Build `01_fallacy_detection.ipynb` with 6 exercises
23. Update `data/tutorial-links.json` with actual paths
24. Test all diagram interactions
25. Cross-link tutorials ↔ JSX ↔ notebook

---

## Quality Standards (V5 Updated)

| Criterion | Target |
|-----------|--------|
| Reading time per tutorial | 18-23 minutes (6 phases) |
| Pólya phase compliance | All 6 phases present |
| Grounding examples | Real lesson-18 data |
| HW counter-method | Referenced with file:line for 12+ fallacies |
| Counter-questions | Actionable, professional tone |
| Code parallels | Defensive coding analogies + HW code snippets |
| Self-assessment | 3 questions per tutorial |
| **Diagram interactivity** | Click/hover feedback on all 7 components |
| **Mobile responsiveness** | Diagrams work on tablet (768px+) |
| **Zero external deps** | Tailwind + inline SVG only |
| **No hardcoded data** | All components import from `data/` or `utils/` |
| **Animation config** | `animate-fadeIn` defined in tailwind.config.js |

---

## Estimated Deliverables (V5 Updated)

| Item | Count | Time Each | Total |
|------|-------|-----------|-------|
| **Data extraction (JSON files)** | **7** | **30 min** | **3.5 hours** |
| **Utility functions** | **1** | **45 min** | **45 min** |
| **Tailwind config** | **1** | **15 min** | **15 min** |
| Diagram components (import data) | 7 | 1 hour | 7 hours |
| Main component integration | 1 | 2 hours | 2 hours |
| Navigation index | 1 | 30 min | 30 min |
| Foundation tutorial | 1 | 45 min | 45 min |
| Fallacy tutorials (with Phase 6) | 16 | 60 min | 16 hours |
| Synthesis document | 1 | 1.5 hours | 1.5 hours |
| Evaluation anti-patterns | 1 | 1.5 hours | 1.5 hours |
| Interactive notebook | 1 | 3 hours | 3 hours |
| **Total** | **38 files** | - | **~35 hours** |

**Note:** Component time reduced from 1.5h (V4) to 1h (V5) because data is pre-extracted. Net reduction: -2 hours from V4.

---

## Validation Checklist (V5)

After implementation:

- [ ] No `const ... = [` with >5 items in component specs
- [ ] All components import from `../data/` or `../utils/`
- [ ] `animate-fadeIn` defined in tailwind.config.js
- [ ] Each JSON file has `version` field
- [ ] Utility functions have JSDoc comments
- [ ] `fallacies-data.json` has `hwCounter` for 12+ fallacies
- [ ] `data/tutorial-links.json` points to actual tutorial files

---

## References

### Original Sources
- **Source JSX:** `lesson-18/interactive/logical-fallacies-focused.jsx`
- **Pólya Framework:** `ai-dev-tasks/polya-analysis.md`
- **Failure Taxonomy:** `lesson-18/dispute-chatbot/qualitative/phase1/failure_taxonomy.md`
- **Design Patterns:** `lesson-18/dispute-schema/explanation/design_patterns_deep_dive_narration.md`
- **Classification Failures:** `lesson-18/dispute-chatbot/qualitative/phase1/classification_failure_taxonomy.md`

### V2 Additional Sources (Homework Integration)
- **Evaluation Methodology Report:** `homeworks/EVALUATION_METHODOLOGY_RESEARCH_REPORT.md`
- **HW2 Failure Taxonomy:** `homeworks/hw2/failure_mode_taxonomy.md`
- **HW3 LLM-as-Judge:** `homeworks/hw3/llm_judge_concepts.md`
- **HW3 Bias Correction:** `homeworks/hw3/bias_correction_tutorial.md`
- **HW4 Retrieval Metrics:** `homeworks/hw4/retrieval_metrics_tutorial.md`
- **HW5 Transition Analysis:** `homeworks/hw5/transition_analysis_concepts.md`

### V4 Additional Sources (JSX Integration)
- **React Docs:** Component composition patterns
- **Tailwind CSS:** Utility-first styling
- **SVG:** Inline graphics for diagrams

### V5 Additional Sources (Data Architecture)
- **JSON Schema:** Data file versioning
- **ES6 Modules:** Import/export patterns for utilities

---

## Changelog

### V5 (2025-12-23)
- **BREAKING:** All hardcoded data moved to `data/` JSON files
- Added `utils/dataHelpers.js` with 5 utility functions
- Added `tailwind.config.js` with `animate-fadeIn`, `animate-slideUp`, `animate-scaleIn`
- Updated all 7 component specifications to import from JSON
- Added `data/` directory: 7 JSON files for single source of truth
- Extended `fallacies-data.json` schema with `hwCounter` field
- Revised time estimates (net reduction: -2 hours due to cleaner data flow)
- Added V5 Validation Checklist

### V4 (2025-12-23)
- Added 7 JSX-compatible visual diagram components
- Full component specifications with code examples
- Updated file structure with `components/` directory
- Main component integration with tabbed navigation
- Revised time estimates (+13 hours for diagrams)
- Zero external dependency constraint (Tailwind + SVG only)

### V3 (2025-12-23)
- JSX component integration architecture
- Single source of truth with `fallacies-data.json`
- Bidirectional linking (JSX ↔ tutorials)

### V2 (2025-12-23)
- Added Fallacy ↔ HW Evaluation Method mapping table
- Added Phase 6 (Evaluation Counter-Practice) to tutorial template
- Added new section `05_evaluation_anti_patterns.md`
- Enhanced notebook with 3 new HW-based exercises

### V1 (2025-12-23)
- Initial plan with Pólya 5-Phase framework
- 16 fallacies across 2 contexts
- Lesson-18 grounding examples
