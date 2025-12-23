#!/usr/bin/env python3
"""Inter-Rater Reliability (IRR) Calculator for Phase 1 Qualitative Analysis.

This script:
1. Loads the 20 traces in irr_sample.csv
2. Uses an LLM as an "independent second rater" to classify each trace
3. Calculates Cohen's Kappa between rater1 and the LLM rater
4. Updates irr_sample.csv with the new labels
5. Reports κ and interpretation

Usage:
    python calculate_irr.py [--dry-run]

Requirements:
    - OPENAI_API_KEY environment variable set
"""

import argparse
import asyncio
import csv
import json
import os
from collections import Counter
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv
from openai import AsyncOpenAI

load_dotenv()

# Paths
SCRIPT_DIR = Path(__file__).parent
DISPUTE_CHATBOT_DIR = SCRIPT_DIR.parent.parent
CONVERSATIONS_DIR = DISPUTE_CHATBOT_DIR / "synthetic_data" / "phase1" / "conversations"
QUALITATIVE_DIR = DISPUTE_CHATBOT_DIR / "qualitative" / "phase1"
IRR_SAMPLE_FILE = QUALITATIVE_DIR / "irr_sample.csv"
RESULTS_DIR = SCRIPT_DIR / "results"

# Failure mode taxonomy (from failure_taxonomy.md)
FAILURE_MODES = [
    "classification_conflict",
    "classification_error", 
    "evidence_quality",
    "evidence_contradiction",
    "compliance_violation",
    "user_escalation",
    "network_timeout",
    "multi_dispute_confusion",
    "ce3_boundary",
    "successful_classification",  # Not a failure - happy path
]

CLASSIFICATION_PROMPT = """You are an expert QA analyst reviewing chatbot conversation traces for a dispute resolution system.

Your task is to classify the PRIMARY failure mode (or success mode) exhibited in the following conversation trace.

## Failure Mode Definitions:

1. **classification_conflict** - User provides conflicting information across turns, making classification ambiguous
2. **classification_error** - Agent shows uncertainty about reason code selection, or selects wrong reason code
3. **evidence_quality** - Evidence is incomplete, missing critical fields (e.g., no tracking_id)
4. **evidence_contradiction** - Direct contradiction between user claim and gathered evidence
5. **compliance_violation** - Regulatory deadline at risk, or PII/PCI data handling issues
6. **user_escalation** - User explicitly requests human agent, or repeated confusion triggers escalation
7. **network_timeout** - Tool failures, retries, service unavailable errors
8. **multi_dispute_confusion** - Multiple active disputes require disambiguation
9. **ce3_boundary** - CE 3.0 qualification at exact threshold boundary
10. **successful_classification** - Happy path: dispute classified and submitted successfully

## Conversation Trace:
{trace_json}

## Instructions:
Analyze the conversation and select the SINGLE most applicable failure mode from the list above.
Consider:
- What went wrong (or right) in this conversation?
- What is the primary issue the agent/user faced?
- What is the final_state and success flag?

Return ONLY a JSON object with this format:
{{
  "failure_mode": "<one of the 10 modes above>",
  "confidence": <float 0.0-1.0>,
  "reasoning": "<brief explanation>"
}}
"""


@dataclass
class IRRSample:
    trace_id: str
    expected_failure_mode: str
    rater1_label: str
    rater2_label: str
    notes: str


def load_irr_sample() -> list[IRRSample]:
    """Load the IRR sample CSV."""
    samples = []
    with open(IRR_SAMPLE_FILE, newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            samples.append(IRRSample(
                trace_id=row['trace_id'],
                expected_failure_mode=row['expected_failure_mode'],
                rater1_label=row['rater1_label'],
                rater2_label=row['rater2_label'],
                notes=row['notes']
            ))
    return samples


def load_all_traces() -> dict[str, dict]:
    """Load all conversation traces into a lookup dict."""
    traces = {}
    
    for file_name in [
        "boundary_case_dialogues.json",
        "escalation_dialogues.json", 
        "error_recovery_dialogues.json",
        "happy_path_dialogues.json"
    ]:
        file_path = CONVERSATIONS_DIR / file_name
        if file_path.exists():
            with open(file_path) as f:
                data = json.load(f)
                for trace in data:
                    traces[trace["trace_id"]] = trace
    
    return traces


async def classify_trace(client: AsyncOpenAI, trace: dict) -> tuple[str, float, str]:
    """Use LLM to independently classify a trace."""
    # Prepare a simplified trace for the prompt (remove nulls for readability)
    simplified_trace = {
        "trace_id": trace.get("trace_id"),
        "dispute_id": trace.get("dispute_id"),
        "turns": [
            {k: v for k, v in turn.items() if v is not None}
            for turn in trace.get("turns", [])
        ],
        "final_state": trace.get("final_state"),
        "success": trace.get("success"),
        "failure_reason": trace.get("failure_reason"),
    }
    
    # Add extra context from boundary cases
    if "expected_failure_mode" in trace:
        # Don't include this - we want independent classification!
        pass
    if "red_flags" in trace:
        simplified_trace["red_flags"] = trace["red_flags"]
    if "category" in trace:
        simplified_trace["category"] = trace["category"]
    
    prompt = CLASSIFICATION_PROMPT.format(
        trace_json=json.dumps(simplified_trace, indent=2)
    )
    
    response = await client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"},
        temperature=0.0  # Deterministic for reproducibility
    )
    
    result = json.loads(response.choices[0].message.content)
    
    return (
        result.get("failure_mode", "unknown"),
        result.get("confidence", 0.0),
        result.get("reasoning", "")
    )


def calculate_cohens_kappa(labels1: list[str], labels2: list[str]) -> float:
    """Calculate Cohen's Kappa for two raters.
    
    κ = (P_o - P_e) / (1 - P_e)
    
    where:
    - P_o = observed agreement (proportion of matching labels)
    - P_e = expected agreement by chance
    """
    if len(labels1) != len(labels2):
        raise ValueError("Label lists must have same length")
    
    n = len(labels1)
    if n == 0:
        return 0.0
    
    # Get all unique categories
    categories = list(set(labels1) | set(labels2))
    
    # Calculate observed agreement (P_o)
    agreements = sum(1 for l1, l2 in zip(labels1, labels2) if l1 == l2)
    p_o = agreements / n
    
    # Calculate expected agreement by chance (P_e)
    # P_e = sum over categories of (proportion_rater1 * proportion_rater2)
    count1 = Counter(labels1)
    count2 = Counter(labels2)
    
    p_e = sum(
        (count1.get(cat, 0) / n) * (count2.get(cat, 0) / n)
        for cat in categories
    )
    
    # Calculate kappa
    if p_e == 1.0:
        return 1.0 if p_o == 1.0 else 0.0
    
    kappa = (p_o - p_e) / (1 - p_e)
    return kappa


def interpret_kappa(kappa: float) -> str:
    """Interpret kappa value according to standard guidelines."""
    if kappa < 0:
        return "Poor (worse than chance)"
    elif kappa < 0.20:
        return "Slight agreement"
    elif kappa < 0.40:
        return "Fair agreement"
    elif kappa < 0.60:
        return "Moderate agreement"
    elif kappa < 0.80:
        return "Substantial agreement"
    else:
        return "Almost perfect agreement"


def save_updated_irr(samples: list[IRRSample], new_labels: dict[str, str]):
    """Save updated IRR sample with new rater2 labels."""
    output_file = QUALITATIVE_DIR / "irr_sample_updated.csv"
    
    with open(output_file, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['trace_id', 'expected_failure_mode', 'rater1_label', 'rater2_label', 'notes'])
        
        for sample in samples:
            new_label = new_labels.get(sample.trace_id, sample.rater2_label)
            writer.writerow([
                sample.trace_id,
                sample.expected_failure_mode,
                sample.rater1_label,
                new_label,
                sample.notes
            ])
    
    print(f"\nUpdated IRR sample saved to: {output_file}")
    return output_file


async def main():
    parser = argparse.ArgumentParser(description="Calculate Inter-Rater Reliability (κ)")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be classified without LLM calls")
    args = parser.parse_args()
    
    # Check API key
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key and not args.dry_run:
        print("ERROR: OPENAI_API_KEY not set. Use --dry-run to test without API calls.")
        return
    
    print("=" * 60)
    print("INTER-RATER RELIABILITY (κ) CALCULATION")
    print("=" * 60)
    
    # Load data
    samples = load_irr_sample()
    traces = load_all_traces()
    
    print(f"\nLoaded {len(samples)} IRR samples")
    print(f"Loaded {len(traces)} conversation traces")
    
    # Check which traces we have
    missing = [s.trace_id for s in samples if s.trace_id not in traces]
    if missing:
        print(f"\nWARNING: Missing traces: {missing}")
    
    if args.dry_run:
        print("\n[DRY RUN] Would classify these traces:")
        for sample in samples:
            has_trace = "✓" if sample.trace_id in traces else "✗"
            print(f"  {has_trace} {sample.trace_id}: {sample.rater1_label}")
        return
    
    # Initialize client
    client = AsyncOpenAI(api_key=api_key)
    
    # Classify each trace with LLM as "Rater 2"
    print("\n" + "-" * 60)
    print("CLASSIFYING TRACES (LLM as independent Rater 2)")
    print("-" * 60)
    
    new_labels = {}
    classifications = []
    
    for sample in samples:
        trace = traces.get(sample.trace_id)
        
        if not trace:
            print(f"\n{sample.trace_id}: SKIPPED (trace not found)")
            new_labels[sample.trace_id] = sample.rater1_label  # Keep original
            continue
        
        print(f"\nClassifying {sample.trace_id}...", end=" ")
        
        try:
            label, confidence, reasoning = await classify_trace(client, trace)
            new_labels[sample.trace_id] = label
            classifications.append({
                "trace_id": sample.trace_id,
                "rater1": sample.rater1_label,
                "rater2": label,
                "confidence": confidence,
                "reasoning": reasoning,
                "match": label == sample.rater1_label
            })
            
            match_symbol = "✓" if label == sample.rater1_label else "✗"
            print(f"{match_symbol} {label} (conf={confidence:.2f})")
            
            if label != sample.rater1_label:
                print(f"    Rater 1: {sample.rater1_label}")
                print(f"    Reason: {reasoning[:100]}...")
            
        except Exception as e:
            print(f"ERROR: {e}")
            new_labels[sample.trace_id] = sample.rater1_label
        
        # Rate limiting
        await asyncio.sleep(0.5)
    
    # Calculate Kappa
    print("\n" + "=" * 60)
    print("COHEN'S KAPPA CALCULATION")
    print("=" * 60)
    
    rater1_labels = [s.rater1_label for s in samples]
    rater2_labels = [new_labels.get(s.trace_id, s.rater1_label) for s in samples]
    
    kappa = calculate_cohens_kappa(rater1_labels, rater2_labels)
    interpretation = interpret_kappa(kappa)
    
    # Count agreements
    agreements = sum(1 for r1, r2 in zip(rater1_labels, rater2_labels) if r1 == r2)
    
    print(f"\nObserved Agreement: {agreements}/{len(samples)} ({agreements/len(samples):.1%})")
    print(f"Cohen's Kappa (κ): {kappa:.3f}")
    print(f"Interpretation: {interpretation}")
    
    # Detailed breakdown
    print("\n" + "-" * 60)
    print("DISAGREEMENT DETAILS")
    print("-" * 60)
    
    disagreements = [c for c in classifications if not c["match"]]
    if disagreements:
        print(f"\n{len(disagreements)} disagreements found:")
        for d in disagreements:
            print(f"\n  {d['trace_id']}:")
            print(f"    Rater 1: {d['rater1']}")
            print(f"    Rater 2 (LLM): {d['rater2']} (conf={d['confidence']:.2f})")
            print(f"    Reasoning: {d['reasoning'][:150]}...")
    else:
        print("\nNo disagreements - perfect agreement!")
    
    # Save results
    output_file = save_updated_irr(samples, new_labels)
    
    # Save detailed results JSON
    results_file = RESULTS_DIR / f"irr_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    results_file.parent.mkdir(exist_ok=True)
    
    with open(results_file, 'w') as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "total_samples": len(samples),
            "agreements": agreements,
            "disagreements": len(disagreements),
            "kappa": kappa,
            "interpretation": interpretation,
            "classifications": classifications
        }, f, indent=2)
    
    print(f"Detailed results saved to: {results_file}")
    
    # Summary for saturation log
    print("\n" + "=" * 60)
    print("SUMMARY FOR SATURATION LOG")
    print("=" * 60)
    print(f"""
## Inter-Rater Reliability (κ) Results

- **Date:** {datetime.now().strftime('%Y-%m-%d')}
- **Sample Size:** {len(samples)} traces
- **Rater 1:** Human analyst (original coding)
- **Rater 2:** GPT-4o (independent classification)

### Results
- **Observed Agreement:** {agreements}/{len(samples)} ({agreements/len(samples):.1%})
- **Cohen's Kappa (κ):** {kappa:.3f}
- **Interpretation:** {interpretation}

### Threshold Check
- **Required κ for gate closure:** ≥ 0.75 (substantial agreement)
- **Actual κ:** {kappa:.3f}
- **Status:** {'✅ PASS' if kappa >= 0.75 else '⚠️ NEEDS CALIBRATION' if kappa >= 0.60 else '❌ FAIL'}
""")
    
    # Recommendation
    if kappa >= 0.75:
        print("✅ κ meets threshold. Gate 6.17.5/6.17.6 can proceed.")
    elif kappa >= 0.60:
        print("⚠️ κ is substantial but below 0.75. Review disagreements and consider calibration session.")
    else:
        print("❌ κ below 0.60. Calibration session required before gate closure.")


if __name__ == "__main__":
    asyncio.run(main())

