#!/usr/bin/env python3
"""
Citation Verification Script for Lesson 14 Memory Systems Tutorials

Validates that all citations to agents_memory.txt are correct by:
1. Extracting citations from tutorial files
2. Reading the cited lines from agents_memory.txt
3. Verifying content matches the context
4. Generating verification report

Usage:
    python lesson-14/scripts/validate_citations.py
"""

from __future__ import annotations

import re
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Tuple


@dataclass
class Citation:
    """Represents a single citation to agents_memory.txt."""

    file: str
    line_number: int
    context: str
    cited_lines: str  # e.g., "194-243" or "22-23"
    topic: str


def extract_citations_from_file(file_path: Path) -> List[Citation]:
    """Extract all citations to agents_memory.txt from a markdown file.

    Args:
        file_path: Path to markdown file

    Returns:
        List of Citation objects found in the file

    Raises:
        FileNotFoundError: If file doesn't exist
    """
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    citations: List[Citation] = []
    # Updated pattern to catch both formats:
    # 1. agents_memory.txt lines 194-243
    # 2. (agents_memory.txt:216-220)
    # 3. agents_memory.txt:232
    patterns = [
        r"agents_memory\.txt[`:)\s]+lines?\s+(\d+(?:-\d+)?(?:,\s*\d+(?:-\d+)?)*)",  # Format 1
        r"agents_memory\.txt:(\d+(?:-\d+)?(?:,\s*\d+(?:-\d+)?)*)",  # Format 2 & 3
    ]

    with open(file_path, encoding="utf-8") as f:
        for line_num, line in enumerate(f, start=1):
            for pattern in patterns:
                matches = re.finditer(pattern, line, re.IGNORECASE)
                for match in matches:
                    cited_lines = match.group(1)
                    # Get surrounding context (50 chars before and after)
                    start = max(0, match.start() - 50)
                    end = min(len(line), match.end() + 50)
                    context = line[start:end].strip()

                    # Infer topic from context
                    topic = _infer_topic(context, line)

                    # Avoid duplicates from overlapping patterns
                    if not any(
                        c.line_number == line_num and c.cited_lines == cited_lines
                        for c in citations
                    ):
                        citations.append(
                            Citation(
                                file=file_path.name,
                                line_number=line_num,
                                context=context,
                                cited_lines=cited_lines,
                                topic=topic,
                            )
                        )

    return citations


def _infer_topic(context: str, full_line: str) -> str:
    """Infer topic from citation context.

    Args:
        context: Surrounding text
        full_line: Full line containing citation

    Returns:
        Inferred topic string
    """
    # Keywords to identify topics
    keywords = {
        "working memory": "Working Memory",
        "episodic": "Episodic Memory",
        "semantic": "Semantic Memory",
        "procedural": "Procedural Memory",
        "parametric": "Parametric Memory",
        "memorybank": "MemoryBank Pattern",
        "a-mem": "A-MEM Pattern",
        "search-o1": "Search-o1 Pattern",
        "context engineering": "Context Engineering",
        "lost in the middle": "Lost in the Middle",
        "ruler": "RULER Benchmark",
        "mmr": "MMR Algorithm",
        "trimming": "Conversation Trimming",
        "summarization": "Conversation Summarization",
        "rag": "RAG",
        "stateless": "LLM Statelessness",
    }

    text = (context + " " + full_line).lower()
    for keyword, topic in keywords.items():
        if keyword in text:
            return topic

    return "General Memory Concepts"


def verify_citation(
    citation: Citation, agents_memory_path: Path
) -> Tuple[bool, str, str]:
    """Verify a citation by reading the cited lines from agents_memory.txt.

    Args:
        citation: Citation to verify
        agents_memory_path: Path to agents_memory.txt

    Returns:
        Tuple of (is_valid, cited_content, verification_message)

    Raises:
        FileNotFoundError: If agents_memory.txt doesn't exist
        ValueError: If citation format is invalid
    """
    if not agents_memory_path.exists():
        raise FileNotFoundError(f"File not found: {agents_memory_path}")

    # Parse cited line ranges (e.g., "194-243" or "22-23, 42-71")
    line_ranges: List[Tuple[int, int]] = []
    parts = citation.cited_lines.split(",")

    for part in parts:
        part = part.strip()
        if "-" in part:
            start_str, end_str = part.split("-")
            start, end = int(start_str.strip()), int(end_str.strip())
        else:
            start = end = int(part.strip())

        if start < 1:
            raise ValueError(f"Invalid line number: {start} (must be >= 1)")
        if end < start:
            raise ValueError(f"Invalid range: {start}-{end} (end < start)")

        line_ranges.append((start, end))

    # Read cited lines
    with open(agents_memory_path, encoding="utf-8") as f:
        all_lines = f.readlines()

    cited_content_parts: List[str] = []
    for start, end in line_ranges:
        if end > len(all_lines):
            return (
                False,
                "",
                f"Line {end} exceeds file length ({len(all_lines)} lines)",
            )

        # Extract lines (convert 1-indexed to 0-indexed)
        lines = all_lines[start - 1 : end]
        cited_content_parts.append("".join(lines).strip())

    cited_content = "\n\n[...]\n\n".join(cited_content_parts)

    # Verify content matches topic
    is_valid = _verify_content_matches_topic(citation.topic, cited_content)

    if is_valid:
        message = f"✅ Verified: Lines {citation.cited_lines} correctly describe {citation.topic}"
    else:
        message = f"⚠️  Warning: Lines {citation.cited_lines} may not fully match topic '{citation.topic}'"

    return is_valid, cited_content, message


def _verify_content_matches_topic(topic: str, content: str) -> bool:
    """Verify that cited content matches the expected topic.

    Args:
        topic: Expected topic
        content: Cited content from agents_memory.txt

    Returns:
        True if content matches topic, False otherwise
    """
    # Simple keyword matching (can be enhanced with NLP)
    content_lower = content.lower()

    topic_keywords = {
        "Working Memory": ["working memory", "short-term", "conversation history"],
        "Episodic Memory": ["episodic", "past events", "experiences"],
        "Semantic Memory": ["semantic", "knowledge", "world"],
        "Procedural Memory": ["procedural", "how to", "patterns"],
        "Parametric Memory": ["parametric", "parameters", "weights"],
        "MemoryBank Pattern": ["memorybank", "spaced repetition", "forgetting curve"],
        "A-MEM Pattern": ["a-mem", "zettelkasten", "notes"],
        "Search-o1 Pattern": [
            "search-o1",
            "reasoning trace",
            "begin_search_query",
            "reason-in-documents",
        ],
        "Context Engineering": [
            "context engineering",
            "optimize",
            "context window",
            "input tokens",
        ],
        "Lost in the Middle": ["lost in the middle", "primacy", "recency"],
        "RULER Benchmark": ["ruler", "benchmark", "context length"],
        "MMR Algorithm": ["mmr", "maximal marginal relevance", "diversity"],
        "Conversation Trimming": ["trimming", "fifo", "sliding window"],
        "Conversation Summarization": ["summarization", "summarize", "compress"],
        "RAG": ["rag", "retrieval-augmented", "embed", "vector"],
        "LLM Statelessness": ["stateless", "forget", "remember"],
    }

    keywords = topic_keywords.get(topic, [])
    if not keywords:
        # Unknown topic - assume valid
        return True

    # Check if at least one keyword is in content
    return any(keyword in content_lower for keyword in keywords)


def generate_report(
    citations: List[Citation],
    verification_results: List[Tuple[Citation, bool, str, str]],
    output_path: Path,
) -> None:
    """Generate markdown report with verification results.

    Args:
        citations: All citations found
        verification_results: Verification results for each citation
        output_path: Path to save report

    Raises:
        IOError: If unable to write report
    """
    # Group by file and topic
    by_file: Dict[str, List[Tuple[Citation, bool, str, str]]] = defaultdict(list)
    by_topic: Dict[str, int] = defaultdict(int)

    for result in verification_results:
        citation, is_valid, cited_content, message = result
        by_file[citation.file].append(result)
        by_topic[citation.topic] += 1

    # Generate report
    report_lines = [
        "# Citation Verification Report - Lesson 14 Memory Systems Tutorials\n",
        f"**Generated:** {Path(__file__).parent.parent.name}\n",
        f"**Total Citations Found:** {len(citations)}\n",
        f"**Total Verified:** {sum(1 for _, is_valid, _, _ in verification_results if is_valid)}\n",
        f"**Warnings:** {sum(1 for _, is_valid, _, _ in verification_results if not is_valid)}\n",
        "\n---\n\n",
        "## Summary by Tutorial File\n\n",
    ]

    for file_name, results in sorted(by_file.items()):
        verified_count = sum(1 for _, is_valid, _, _ in results if is_valid)
        total_count = len(results)
        status = "✅ PASS" if verified_count == total_count else "⚠️  REVIEW"

        report_lines.append(f"### {file_name} ({verified_count}/{total_count} verified) {status}\n\n")

        # Group by topic within file
        topic_results: Dict[str, List[Tuple[Citation, bool, str, str]]] = defaultdict(list)
        for result in results:
            topic_results[result[0].topic].append(result)

        for topic, topic_results_list in sorted(topic_results.items()):
            report_lines.append(f"**{topic}** ({len(topic_results_list)} citations):\n\n")

            for citation, is_valid, cited_content, message in topic_results_list:
                report_lines.append(f"- Line {citation.line_number}: `lines {citation.cited_lines}` - {message}\n")

            report_lines.append("\n")

    # Summary by topic
    report_lines.extend([
        "\n---\n\n",
        "## Summary by Topic\n\n",
        "| Topic | Citation Count | % of Total |\n",
        "|-------|----------------|------------|\n",
    ])

    total_citations = len(citations)
    for topic, count in sorted(by_topic.items(), key=lambda x: x[1], reverse=True):
        percentage = (count / total_citations * 100) if total_citations > 0 else 0
        report_lines.append(f"| {topic} | {count} | {percentage:.1f}% |\n")

    # Requirements check
    report_lines.extend([
        "\n---\n\n",
        "## Requirements Verification\n\n",
        f"**Requirement:** ≥5 unique citations per tutorial file\n\n",
    ])

    for file_name, results in sorted(by_file.items()):
        unique_line_ranges = set(citation.cited_lines for citation, _, _, _ in results)
        count = len(unique_line_ranges)
        status = "✅ PASS" if count >= 5 else "❌ FAIL"
        report_lines.append(f"- `{file_name}`: {count} unique citations {status}\n")

    # Sample citations
    report_lines.extend([
        "\n---\n\n",
        "## Sample Citation Verification (First 5)\n\n",
    ])

    for i, (citation, is_valid, cited_content, message) in enumerate(verification_results[:5], start=1):
        report_lines.extend([
            f"### {i}. {citation.file} Line {citation.line_number}\n\n",
            f"**Topic:** {citation.topic}\n",
            f"**Cited Lines:** {citation.cited_lines}\n",
            f"**Context:** {citation.context[:100]}...\n\n",
            f"**Verification:** {message}\n\n",
            f"**Cited Content (preview):**\n```\n{cited_content[:500]}...\n```\n\n",
        ])

    # Write report
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.writelines(report_lines)

    print(f"✅ Report generated: {output_path}")


def main() -> None:
    """Main function to validate citations."""
    # Paths
    project_root = Path(__file__).parent.parent.parent
    lesson_14 = project_root / "lesson-14"
    agents_memory_path = lesson_14 / "agents_memory.txt"
    output_path = lesson_14 / "citation_verification_report.md"

    # Tutorial files to check
    tutorial_files = [
        lesson_14 / "memory_systems_fundamentals.md",
        lesson_14 / "context_engineering_guide.md",
    ]

    print("=" * 80)
    print("Citation Verification Script - Lesson 14 Memory Systems Tutorials")
    print("=" * 80)
    print()

    # Extract citations
    all_citations: List[Citation] = []
    for file_path in tutorial_files:
        if not file_path.exists():
            print(f"⚠️  Warning: File not found: {file_path}")
            continue

        print(f"📖 Extracting citations from: {file_path.name}")
        citations = extract_citations_from_file(file_path)
        all_citations.extend(citations)
        print(f"   Found {len(citations)} citations")

    print()
    print(f"📊 Total citations found: {len(all_citations)}")
    print()

    # Verify citations
    print("🔍 Verifying citations against agents_memory.txt...")
    verification_results: List[Tuple[Citation, bool, str, str]] = []

    for citation in all_citations:
        try:
            is_valid, cited_content, message = verify_citation(citation, agents_memory_path)
            verification_results.append((citation, is_valid, cited_content, message))
        except (FileNotFoundError, ValueError) as e:
            print(f"❌ Error verifying {citation.file} line {citation.line_number}: {e}")
            verification_results.append((citation, False, "", f"❌ Error: {e}"))

    verified_count = sum(1 for _, is_valid, _, _ in verification_results if is_valid)
    print(f"   ✅ Verified: {verified_count}/{len(all_citations)}")
    print(f"   ⚠️  Warnings: {len(all_citations) - verified_count}")
    print()

    # Generate report
    print("📝 Generating verification report...")
    generate_report(all_citations, verification_results, output_path)
    print()
    print("=" * 80)
    print(f"✅ Citation verification complete. See: {output_path}")
    print("=" * 80)


if __name__ == "__main__":
    main()
