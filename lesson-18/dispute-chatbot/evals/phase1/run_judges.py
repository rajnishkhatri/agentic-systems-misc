#!/usr/bin/env python3
"""Judge Runner Script for Phase 1 Qualitative Validation.

Executes LLM judges on test cases and records pass/fail results.
Updates judge_revalidation_checklist.md and saturation_log.md with results.

Usage:
    python run_judges.py [--dry-run] [--fabrication-only] [--evidence-only]
    
Requirements:
    - OPENAI_API_KEY environment variable set
    - Run from dispute-chatbot directory or set PYTHONPATH
"""

import argparse
import asyncio
import json
import os
import sys
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from jinja2 import Environment, FileSystemLoader
from openai import AsyncOpenAI

# Load environment variables
load_dotenv()

# Paths
SCRIPT_DIR = Path(__file__).parent
DISPUTE_CHATBOT_DIR = SCRIPT_DIR.parent.parent
PROMPTS_DIR = SCRIPT_DIR / "prompts"
GOLDEN_SET_DIR = DISPUTE_CHATBOT_DIR / "synthetic_data" / "phase1" / "golden_set"
CONVERSATIONS_DIR = DISPUTE_CHATBOT_DIR / "synthetic_data" / "phase1" / "conversations"
QUALITATIVE_DIR = DISPUTE_CHATBOT_DIR / "qualitative" / "phase1"
RESULTS_DIR = SCRIPT_DIR / "results"

# Ensure results directory exists
RESULTS_DIR.mkdir(exist_ok=True)

# Jinja2 environment
jinja_env = Environment(loader=FileSystemLoader(PROMPTS_DIR))


@dataclass
class JudgeResult:
    """Result from a single judge evaluation."""
    case_id: str
    judge_name: str
    passed: bool
    score: float | None = None
    reasoning: str = ""
    raw_response: dict = field(default_factory=dict)
    error: str | None = None


@dataclass
class JudgeRunSummary:
    """Summary of all judge runs."""
    judge_name: str
    total_cases: int = 0
    passed: int = 0
    failed: int = 0
    errors: int = 0
    results: list[JudgeResult] = field(default_factory=list)
    threshold: float = 0.0
    
    @property
    def pass_rate(self) -> float:
        if self.total_cases == 0:
            return 0.0
        return self.passed / self.total_cases
    
    @property
    def false_negatives(self) -> int:
        """Cases that should have failed but passed."""
        return sum(1 for r in self.results 
                   if r.passed and r.raw_response.get("expected_fail", False))
    
    @property
    def false_positives(self) -> int:
        """Cases that should have passed but failed."""
        return sum(1 for r in self.results 
                   if not r.passed and r.raw_response.get("expected_pass", False))


class BaseJudge:
    """Base class for LLM judges."""
    
    def __init__(self, client: AsyncOpenAI, model: str = "gpt-4o"):
        self.client = client
        self.model = model
        self.threshold = 0.5
        self.is_blocking = True
    
    async def evaluate(self, case: dict) -> JudgeResult:
        raise NotImplementedError


class FabricationDetectionJudge(BaseJudge):
    """Detects fabricated evidence in agent outputs."""
    
    def __init__(self, client: AsyncOpenAI, model: str = "gpt-4o"):
        super().__init__(client, model)
        self.threshold = 0.95  # High threshold - must be very confident it's clean
        self.template = jinja_env.get_template("fabrication_detection.j2")
    
    async def evaluate(self, case: dict) -> JudgeResult:
        """Evaluate a fabrication test case."""
        case_id = case.get("id", "unknown")
        
        try:
            # Build prompt from template
            prompt = self.template.render(
                dispute_reason=case.get("category", "unknown"),
                evidence_package=json.dumps(case.get("input_evidence", {}), indent=2)
            )
            
            # Add the agent output to evaluate
            full_prompt = f"""{prompt}

AGENT OUTPUT TO EVALUATE:
{case.get("agent_output", "")}

Evaluate if the agent output contains any fabricated information not supported by the evidence package above.
"""
            
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": full_prompt}],
                response_format={"type": "json_object"},
                temperature=0.0
            )
            
            result_text = response.choices[0].message.content
            result_json = json.loads(result_text)
            
            fabrication_prob = result_json.get("fabrication_probability", 0.0)
            is_clean = result_json.get("is_clean", fabrication_prob < 0.05)
            
            # For fabrication cases: passed = correctly detected fabrication (high prob)
            # For valid cases: passed = correctly identified as clean (low prob)
            expected_fabricated = case.get("is_fabricated", False)
            
            if expected_fabricated:
                # Should detect fabrication (high probability)
                passed = fabrication_prob >= 0.5  # Detected as fabricated
            else:
                # Should be clean (low probability)
                passed = is_clean
            
            return JudgeResult(
                case_id=case_id,
                judge_name="FabricationDetectionJudge",
                passed=passed,
                score=1.0 - fabrication_prob if not expected_fabricated else fabrication_prob,
                reasoning=result_json.get("reason", ""),
                raw_response={
                    **result_json,
                    "expected_fabricated": expected_fabricated,
                    "expected_pass": not expected_fabricated,
                    "expected_fail": expected_fabricated
                }
            )
            
        except Exception as e:
            return JudgeResult(
                case_id=case_id,
                judge_name="FabricationDetectionJudge",
                passed=False,
                error=str(e)
            )


class EvidenceQualityJudge(BaseJudge):
    """Evaluates evidence quality and completeness."""
    
    def __init__(self, client: AsyncOpenAI, model: str = "gpt-4o"):
        super().__init__(client, model)
        self.threshold = 0.80
        self.template = jinja_env.get_template("evidence_quality.j2")
    
    async def evaluate(self, case: dict) -> JudgeResult:
        """Evaluate evidence quality for a dispute trace."""
        case_id = case.get("trace_id", "unknown")
        
        try:
            # Extract evidence from the trace
            evidence = self._extract_evidence(case)
            dispute_reason = case.get("category", "dispute")
            
            prompt = self.template.render(
                dispute_reason=dispute_reason,
                evidence_package=json.dumps(evidence, indent=2)
            )
            
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"},
                temperature=0.0
            )
            
            result_text = response.choices[0].message.content
            result_json = json.loads(result_text)
            
            score = result_json.get("score", 0.0)
            meets_threshold = result_json.get("meets_threshold", score >= self.threshold)
            
            # Expected outcome based on test case
            expected_failure = case.get("expected_failure_mode") in [
                "evidence_quality", "evidence_contradiction"
            ]
            
            return JudgeResult(
                case_id=case_id,
                judge_name="EvidenceQualityJudge",
                passed=meets_threshold,
                score=score,
                reasoning=result_json.get("reason", ""),
                raw_response={
                    **result_json,
                    "expected_low_quality": expected_failure,
                    "expected_pass": not expected_failure,
                    "expected_fail": expected_failure
                }
            )
            
        except Exception as e:
            return JudgeResult(
                case_id=case_id,
                judge_name="EvidenceQualityJudge",
                passed=False,
                error=str(e)
            )
    
    def _extract_evidence(self, trace: dict) -> dict:
        """Extract evidence from a conversation trace."""
        evidence = {}
        for turn in trace.get("turns", []):
            if turn.get("role") == "tool" and "tool_output" in turn:
                output = turn["tool_output"]
                if isinstance(output, dict):
                    evidence.update(output)
        return evidence


class DisputeValidityJudge(BaseJudge):
    """Validates dispute headers and transaction details."""
    
    def __init__(self, client: AsyncOpenAI, model: str = "gpt-4o-mini"):
        super().__init__(client, model)
        self.threshold = 0.70
        self.is_blocking = False  # Non-blocking, warning only
        self.template = jinja_env.get_template("dispute_validity.j2")
    
    async def evaluate(self, case: dict) -> JudgeResult:
        """Evaluate dispute validity."""
        case_id = case.get("trace_id", "unknown")
        
        try:
            # Build dispute header from trace
            dispute_header = {
                "dispute_id": case.get("dispute_id", "unknown"),
                "category": case.get("category", "unknown"),
                "response_due_date": "2025-01-15"  # Example
            }
            
            transaction_details = self._extract_transaction(case)
            
            prompt = self.template.render(
                dispute_header=json.dumps(dispute_header, indent=2),
                transaction_details=json.dumps(transaction_details, indent=2),
                current_date="2025-12-09"
            )
            
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"},
                temperature=0.0
            )
            
            result_text = response.choices[0].message.content
            result_json = json.loads(result_text)
            
            is_valid = result_json.get("is_valid", False)
            warning_level = result_json.get("warning_level", "LOW")
            
            return JudgeResult(
                case_id=case_id,
                judge_name="DisputeValidityJudge",
                passed=is_valid,
                score=1.0 if is_valid else 0.0,
                reasoning=result_json.get("reason", ""),
                raw_response=result_json
            )
            
        except Exception as e:
            return JudgeResult(
                case_id=case_id,
                judge_name="DisputeValidityJudge",
                passed=False,
                error=str(e)
            )
    
    def _extract_transaction(self, trace: dict) -> dict:
        """Extract transaction details from trace."""
        # Parse from user messages
        for turn in trace.get("turns", []):
            if turn.get("role") == "user":
                content = turn.get("content", "")
                if "$" in content:
                    return {"raw_text": content}
        return {}


class GuardRailsChecker:
    """Non-LLM regex/rule-based compliance checker."""
    
    PAN_PATTERN = r"\b(?:4[0-9]{12}(?:[0-9]{3})?|5[1-5][0-9]{14}|3[47][0-9]{13})\b"
    SSN_PATTERN = r"\b\d{3}-\d{2}-\d{4}\b"
    
    def check(self, case: dict) -> JudgeResult:
        """Check for PII/PCI violations."""
        import re
        
        case_id = case.get("trace_id", "unknown")
        violations = []
        
        # Check all text content in trace
        for turn in case.get("turns", []):
            content = str(turn.get("content", ""))
            
            if re.search(self.PAN_PATTERN, content):
                violations.append(f"PAN detected in {turn.get('role')} turn")
            
            if re.search(self.SSN_PATTERN, content):
                violations.append(f"SSN detected in {turn.get('role')} turn")
        
        # Check if violations were properly handled (redacted in response)
        handled = any(
            "[SECURITY NOTICE" in str(turn.get("content", ""))
            for turn in case.get("turns", [])
            if turn.get("role") == "assistant"
        )
        
        passed = len(violations) == 0 or handled
        
        return JudgeResult(
            case_id=case_id,
            judge_name="GuardRails",
            passed=passed,
            score=1.0 if passed else 0.0,
            reasoning=f"Violations: {violations}, Handled: {handled}" if violations else "No PII detected",
            raw_response={"violations": violations, "handled": handled}
        )


async def run_fabrication_judge(client: AsyncOpenAI, dry_run: bool = False) -> JudgeRunSummary:
    """Run fabrication detection on golden set."""
    print("\n" + "="*60)
    print("FABRICATION DETECTION JUDGE")
    print("="*60)
    
    # Load fabrication examples
    fab_file = GOLDEN_SET_DIR / "fabrication_examples.json"
    with open(fab_file) as f:
        cases = json.load(f)
    
    print(f"Loaded {len(cases)} cases from {fab_file.name}")
    
    summary = JudgeRunSummary(
        judge_name="FabricationDetectionJudge",
        total_cases=len(cases),
        threshold=0.95
    )
    
    if dry_run:
        print("[DRY RUN] Would evaluate:")
        for case in cases:
            print(f"  - {case['id']}: {case['category']} (is_fabricated={case.get('is_fabricated', '?')})")
        return summary
    
    judge = FabricationDetectionJudge(client)
    
    for case in cases:
        print(f"\nEvaluating {case['id']}...", end=" ")
        result = await judge.evaluate(case)
        summary.results.append(result)
        
        if result.error:
            summary.errors += 1
            print(f"ERROR: {result.error}")
        elif result.passed:
            summary.passed += 1
            print(f"✓ PASS (score={result.score:.2f})")
        else:
            summary.failed += 1
            print(f"✗ FAIL (score={result.score:.2f})")
        
        # Rate limiting
        await asyncio.sleep(0.5)
    
    return summary


async def run_evidence_quality_judge(
    client: AsyncOpenAI, 
    trace_ids: list[str],
    dry_run: bool = False
) -> JudgeRunSummary:
    """Run evidence quality judge on specific traces."""
    print("\n" + "="*60)
    print("EVIDENCE QUALITY JUDGE")
    print("="*60)
    
    # Load boundary cases
    boundary_file = CONVERSATIONS_DIR / "boundary_case_dialogues.json"
    with open(boundary_file) as f:
        all_cases = json.load(f)
    
    # Filter to requested trace IDs
    cases = [c for c in all_cases if c["trace_id"] in trace_ids]
    print(f"Loaded {len(cases)} cases from {boundary_file.name}")
    
    summary = JudgeRunSummary(
        judge_name="EvidenceQualityJudge",
        total_cases=len(cases),
        threshold=0.80
    )
    
    if dry_run:
        print("[DRY RUN] Would evaluate:")
        for case in cases:
            print(f"  - {case['trace_id']}: {case['category']}")
        return summary
    
    judge = EvidenceQualityJudge(client)
    
    for case in cases:
        print(f"\nEvaluating {case['trace_id']}...", end=" ")
        result = await judge.evaluate(case)
        summary.results.append(result)
        
        if result.error:
            summary.errors += 1
            print(f"ERROR: {result.error}")
        elif result.passed:
            summary.passed += 1
            print(f"✓ PASS (score={result.score:.2f})")
        else:
            summary.failed += 1
            print(f"✗ FAIL (score={result.score:.2f})")
        
        await asyncio.sleep(0.5)
    
    return summary


async def run_dispute_validity_judge(
    client: AsyncOpenAI,
    trace_ids: list[str],
    dry_run: bool = False
) -> JudgeRunSummary:
    """Run dispute validity judge (non-blocking)."""
    print("\n" + "="*60)
    print("DISPUTE VALIDITY JUDGE (Non-blocking)")
    print("="*60)
    
    boundary_file = CONVERSATIONS_DIR / "boundary_case_dialogues.json"
    with open(boundary_file) as f:
        all_cases = json.load(f)
    
    cases = [c for c in all_cases if c["trace_id"] in trace_ids]
    print(f"Loaded {len(cases)} cases")
    
    summary = JudgeRunSummary(
        judge_name="DisputeValidityJudge",
        total_cases=len(cases),
        threshold=0.70
    )
    
    if dry_run:
        print("[DRY RUN] Would evaluate:")
        for case in cases:
            print(f"  - {case['trace_id']}: {case['category']}")
        return summary
    
    judge = DisputeValidityJudge(client)
    
    for case in cases:
        print(f"\nEvaluating {case['trace_id']}...", end=" ")
        result = await judge.evaluate(case)
        summary.results.append(result)
        
        if result.error:
            summary.errors += 1
            print(f"ERROR: {result.error}")
        else:
            status = "✓ VALID" if result.passed else "⚠ WARNING"
            print(f"{status}")
        
        await asyncio.sleep(0.3)
    
    return summary


def run_guardrails_check(trace_ids: list[str]) -> JudgeRunSummary:
    """Run guardrails compliance check (no LLM needed)."""
    print("\n" + "="*60)
    print("GUARDRAILS COMPLIANCE CHECK")
    print("="*60)
    
    boundary_file = CONVERSATIONS_DIR / "boundary_case_dialogues.json"
    with open(boundary_file) as f:
        all_cases = json.load(f)
    
    cases = [c for c in all_cases if c["trace_id"] in trace_ids]
    print(f"Checking {len(cases)} cases")
    
    summary = JudgeRunSummary(
        judge_name="GuardRails",
        total_cases=len(cases),
        threshold=1.0  # Pass/Fail
    )
    
    checker = GuardRailsChecker()
    
    for case in cases:
        print(f"\nChecking {case['trace_id']}...", end=" ")
        result = checker.check(case)
        summary.results.append(result)
        
        if result.passed:
            summary.passed += 1
            print(f"✓ PASS")
        else:
            summary.failed += 1
            print(f"✗ FAIL - {result.reasoning}")
    
    return summary


def save_results(summaries: list[JudgeRunSummary], output_file: Path):
    """Save results to JSON file."""
    output = {
        "timestamp": datetime.now().isoformat(),
        "judges": {}
    }
    
    for summary in summaries:
        output["judges"][summary.judge_name] = {
            "total_cases": summary.total_cases,
            "passed": summary.passed,
            "failed": summary.failed,
            "errors": summary.errors,
            "pass_rate": summary.pass_rate,
            "threshold": summary.threshold,
            "false_negatives": summary.false_negatives,
            "false_positives": summary.false_positives,
            "results": [
                {
                    "case_id": r.case_id,
                    "passed": r.passed,
                    "score": r.score,
                    "reasoning": r.reasoning,
                    "error": r.error
                }
                for r in summary.results
            ]
        }
    
    with open(output_file, "w") as f:
        json.dump(output, f, indent=2)
    
    print(f"\nResults saved to: {output_file}")


def print_summary(summaries: list[JudgeRunSummary]):
    """Print final summary report."""
    print("\n" + "="*60)
    print("JUDGE VALIDATION SUMMARY")
    print("="*60)
    
    for summary in summaries:
        print(f"\n{summary.judge_name}:")
        print(f"  Total Cases: {summary.total_cases}")
        print(f"  Passed: {summary.passed}")
        print(f"  Failed: {summary.failed}")
        print(f"  Errors: {summary.errors}")
        print(f"  Pass Rate: {summary.pass_rate:.1%}")
        print(f"  Threshold: {summary.threshold}")
        
        if summary.judge_name == "FabricationDetectionJudge":
            print(f"  False Negatives: {summary.false_negatives}")
            print(f"  False Positives: {summary.false_positives}")
    
    print("\n" + "-"*60)
    print("UPDATE CHECKLIST:")
    print("-"*60)
    
    for summary in summaries:
        status = "✓ OK" if summary.errors == 0 and summary.pass_rate >= 0.8 else "⚠ REVIEW"
        print(f"  [{status}] {summary.judge_name}: {summary.pass_rate:.1%} pass rate")


def generate_checklist_update(summaries: list[JudgeRunSummary]) -> str:
    """Generate markdown to update judge_revalidation_checklist.md."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    
    lines = [
        f"\n## Results (Generated {timestamp})\n"
    ]
    
    for summary in summaries:
        lines.append(f"### {summary.judge_name}")
        lines.append(f"- Pass rate: {summary.pass_rate:.1%} ({summary.passed}/{summary.total_cases})")
        
        if summary.judge_name == "FabricationDetectionJudge":
            lines.append(f"- False negatives: {summary.false_negatives}")
            lines.append(f"- False positives: {summary.false_positives}")
        
        lines.append(f"- Errors: {summary.errors}")
        lines.append(f"- Threshold: {summary.threshold}")
        
        # Individual results
        lines.append("\n| Case ID | Passed | Score | Notes |")
        lines.append("|---------|--------|-------|-------|")
        for r in summary.results:
            status = "✓" if r.passed else "✗"
            score = f"{r.score:.2f}" if r.score is not None else "N/A"
            notes = r.error if r.error else r.reasoning[:50] + "..." if len(r.reasoning) > 50 else r.reasoning
            lines.append(f"| {r.case_id} | {status} | {score} | {notes} |")
        
        lines.append("")
    
    return "\n".join(lines)


async def main():
    parser = argparse.ArgumentParser(description="Run LLM judges for Phase 1 validation")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be evaluated without calling LLM")
    parser.add_argument("--fabrication-only", action="store_true", help="Only run fabrication judge")
    parser.add_argument("--evidence-only", action="store_true", help="Only run evidence quality judge")
    parser.add_argument("--all", action="store_true", help="Run all judges including optional ones")
    args = parser.parse_args()
    
    # Check API key
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key and not args.dry_run:
        print("ERROR: OPENAI_API_KEY not set. Use --dry-run to test without API calls.")
        sys.exit(1)
    
    client = AsyncOpenAI(api_key=api_key) if api_key else None
    
    summaries = []
    
    # Define test cases
    evidence_quality_cases = ["TRC-BC-002", "TRC-BC-008", "TRC-BC-012"]
    dispute_validity_cases = ["TRC-BC-001", "TRC-BC-005", "TRC-BC-011"]
    guardrails_cases = ["TRC-BC-003", "TRC-BC-009"]
    
    # Run judges based on flags
    if not args.evidence_only:
        summary = await run_fabrication_judge(client, dry_run=args.dry_run)
        summaries.append(summary)
    
    if not args.fabrication_only:
        summary = await run_evidence_quality_judge(
            client, evidence_quality_cases, dry_run=args.dry_run
        )
        summaries.append(summary)
    
    if args.all:
        summary = await run_dispute_validity_judge(
            client, dispute_validity_cases, dry_run=args.dry_run
        )
        summaries.append(summary)
        
        summary = run_guardrails_check(guardrails_cases)
        summaries.append(summary)
    
    # Print summary
    if not args.dry_run:
        print_summary(summaries)
        
        # Save results
        output_file = RESULTS_DIR / f"judge_run_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        save_results(summaries, output_file)
        
        # Generate checklist update
        checklist_update = generate_checklist_update(summaries)
        checklist_file = RESULTS_DIR / "checklist_update.md"
        with open(checklist_file, "w") as f:
            f.write(checklist_update)
        print(f"\nChecklist update template saved to: {checklist_file}")


if __name__ == "__main__":
    asyncio.run(main())

