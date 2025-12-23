#!/usr/bin/env python3
"""
Extract and categorize dispute reason codes from the dispute-schema folder.

Outputs (written to lesson-18/dispute-schema/):
- REASON_CODES_CATALOG.md
- reason_codes_catalog.json
- reason_codes_catalog.csv

Two categorizations are produced:
1) unified_category: DisputeReason (repo's canonical categories)
2) network_family: higher-level network-family buckets (fraud/authorization/etc.)
"""

from __future__ import annotations

import csv
import json
import os
import re
from collections import defaultdict
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Set, Tuple


REPO_ROOT = Path(__file__).resolve().parents[3]  # .../recipe-chatbot
BASE_DIR = REPO_ROOT / "lesson-18" / "dispute-schema"

CANONICAL_TS = BASE_DIR / "network_reason_codes.ts"

OUT_MD = BASE_DIR / "REASON_CODES_CATALOG.md"
OUT_JSON = BASE_DIR / "reason_codes_catalog.json"
OUT_CSV = BASE_DIR / "reason_codes_catalog.csv"


UNIFIED_CATEGORIES = {
    "credit_not_processed",
    "duplicate",
    "fraudulent",
    "general",
    "product_not_received",
    "product_unacceptable",
    "subscription_canceled",
    "unrecognized",
}


NETWORK_FAMILIES = {
    "fraud",
    "authorization",
    "processing_errors",
    "consumer_disputes",
    "cardholder_disputes",
    "retrieval_inquiry",
    "other",
    "non_card_dispute",
}


NON_CARD_UNIFIED_MAP = {
    # PayPal common-ish signals observed in-repo
    "ITEM_NOT_RECEIVED": "product_not_received",
    "SNAD": "product_unacceptable",  # significantly not as described
    "UNAUTHORIZED": "fraudulent",
    # Generic fallbacks (kept here for future expansion)
    "INR": "product_not_received",
}


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass(frozen=True)
class SourceRef:
    path: str
    line: Optional[int] = None
    kind: str = "observed"  # canonical | observed


@dataclass
class ReasonCodeRecord:
    namespace: str  # visa/mastercard/amex/discover/paypal/klarna/other
    code: str
    description: Optional[str] = None
    unified_category: Optional[str] = None  # DisputeReason
    network_family: Optional[str] = None
    source_type: str = "observed"  # canonical | observed
    unmapped: bool = False
    sources: List[SourceRef] = None  # populated later

    def key(self) -> Tuple[str, str]:
        return (self.namespace, self.code)


def _normalize_family(raw: str) -> str:
    s = raw.strip().lower()
    s = s.replace(" ", "_").replace("-", "_").replace("/", "_")
    if s in NETWORK_FAMILIES:
        return s
    # coarse normalization
    if "fraud" in s:
        return "fraud"
    if "auth" in s:
        return "authorization"
    if "process" in s or "error" in s:
        return "processing_errors"
    if "consumer" in s:
        return "consumer_disputes"
    if "cardholder" in s:
        return "cardholder_disputes"
    if "retrieval" in s or "inquiry" in s:
        return "retrieval_inquiry"
    return "other"


def parse_canonical_network_reason_codes(ts_path: Path) -> List[ReasonCodeRecord]:
    """
    Parse `network_reason_codes.ts` without a TS parser by using robust regexes.

    We rely on the stable pattern:
      '10.4': { description: '...', category: 'fraudulent' },
    and section comments to derive network_family.
    """
    text = ts_path.read_text(encoding="utf-8")
    lines = text.splitlines()

    # Identify blocks by exports like: export const VISA_REASON_CODES = { ... }
    export_re = re.compile(r"export\s+const\s+([A-Z_]+)_REASON_CODES\b")
    entry_re = re.compile(
        r"^\s*'(?P<code>[^']+)'\s*:\s*\{\s*description:\s*'(?P<desc>(?:\\'|[^'])*)'\s*,\s*category:\s*'(?P<cat>[^']+)'\s*\}\s*,?\s*$"
    )

    current_namespace: Optional[str] = None
    current_family: Optional[str] = None
    results: List[ReasonCodeRecord] = []

    def set_namespace_from_export(export_name: str) -> Optional[str]:
        m = export_name.upper()
        if m == "VISA":
            return "visa"
        if m == "MASTERCARD":
            return "mastercard"
        if m == "AMEX":
            return "amex"
        if m == "DISCOVER":
            return "discover"
        return None

    for idx, line in enumerate(lines, start=1):
        em = export_re.search(line)
        if em:
            current_namespace = set_namespace_from_export(em.group(1))
            current_family = None
            continue

        # Track family from section comments e.g. "// Fraud", "// Processing Errors (12.x series)"
        if line.strip().startswith("//") and current_namespace:
            comment = line.strip().lstrip("/").strip()
            # Skip separator lines
            if set(comment) <= {"=", " "}:
                continue
            # Normalize specific section patterns
            if comment.lower().startswith("fraud"):
                current_family = "fraud"
            elif comment.lower().startswith("authorization"):
                current_family = "authorization"
            elif comment.lower().startswith("processing"):
                current_family = "processing_errors"
            elif comment.lower().startswith("consumer"):
                current_family = "consumer_disputes"
            elif comment.lower().startswith("cardholder"):
                current_family = "cardholder_disputes"
            elif comment.lower().startswith("inquiry") or comment.lower().startswith("retrieval"):
                current_family = "retrieval_inquiry"
            elif comment.lower().startswith("point of interaction"):
                current_family = "processing_errors"
            else:
                # keep the current family; many comments are not family headers
                pass
            continue

        if current_namespace:
            m = entry_re.match(line)
            if not m:
                continue

            code = m.group("code")
            desc = m.group("desc").replace("\\'", "'")
            cat = m.group("cat")
            unified = cat if cat in UNIFIED_CATEGORIES else None
            family = current_family
            if current_namespace == "visa" and family is None:
                # Visa can be derived from numeric prefix too
                if code.startswith("10."):
                    family = "fraud"
                elif code.startswith("11."):
                    family = "authorization"
                elif code.startswith("12."):
                    family = "processing_errors"
                elif code.startswith("13."):
                    family = "consumer_disputes"
            if family is None:
                family = "other"

            results.append(
                ReasonCodeRecord(
                    namespace=current_namespace,
                    code=code,
                    description=desc,
                    unified_category=unified,
                    network_family=family,
                    source_type="canonical",
                    unmapped=False,
                    sources=[SourceRef(path=str(ts_path.relative_to(REPO_ROOT)), line=idx, kind="canonical")],
                )
            )

    return results


def _iter_text_files(root: Path) -> Iterable[Path]:
    # keep it conservative; we only need human-readable sources
    exts = {".ts", ".py", ".json", ".yaml", ".yml", ".md", ".txt"}
    for p in root.rglob("*"):
        if not p.is_file():
            continue
        if p.name.startswith("."):
            continue
        # Avoid self-referential scanning (script + generated outputs)
        try:
            rel = p.relative_to(root)
            if rel.parts and rel.parts[0] == "scripts":
                continue
            if p.name in {"REASON_CODES_CATALOG.md", "reason_codes_catalog.json", "reason_codes_catalog.csv"}:
                continue
        except Exception:
            pass
        if p.suffix.lower() not in exts:
            continue
        yield p


def scan_observed_reason_codes(root: Path) -> List[ReasonCodeRecord]:
    """
    Sweep the subtree for non-canonical reason code values.

    We focus on patterns like:
      "reason_code": "ITEM_NOT_RECEIVED"
      reason_code: ITEM_NOT_RECEIVED
      network_reason_code: "10.4"

    Canonical card-network codes are already covered by `network_reason_codes.ts`,
    but we still allow them as observed sources (dedupe will merge sources).
    """
    # Capture a value on the same line after reason_code / network_reason_code
    kv_re = re.compile(
        r"""(?ix)
        (?P<q>["']?)\b(?P<field>reason_code|network_reason_code)\b(?P=q)
        \s*[:=]\s*
        (?P<val>
            "(?:\\.|[^"\\])*" |
            '(?:\\.|[^'\\])*' |
            [A-Za-z0-9_.-]+
        )
        """
    )

    # Restrict OpenAPI token capture to the gateway-responses block; these are not dispute reason codes,
    # but they *are* "reason-like codes" referenced in-repo (keep in their own namespace).
    openapi_gateway_response_key_re = re.compile(r"^\s{2}([A-Z0-9_]+):\s*$")

    # Track payment method context within a file to classify `reason_code` namespace (paypal/klarna)
    pm_type_re = re.compile(r'(?i)"type"\s*:\s*"(?P<t>paypal|klarna)"')

    # Filter out obvious non-codes that appear in type annotations / placeholders
    ignore_tokens = {
        "string",
        "number",
        "boolean",
        "null",
        "undefined",
        "unknown",
        "n/a",
        "na",
    }

    found: Dict[Tuple[str, str], ReasonCodeRecord] = {}

    for path in _iter_text_files(root):
        rel = str(path.relative_to(REPO_ROOT))
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except Exception:
            continue

        in_gateway_responses = False
        last_pm_type: Optional[str] = None

        for i, line in enumerate(text.splitlines(), start=1):
            # Payment method context (mostly for JSON examples)
            pm = pm_type_re.search(line)
            if pm:
                last_pm_type = pm.group("t").lower()

            # Key/value style
            for m in kv_re.finditer(line):
                field = m.group("field").lower()
                raw_token = m.group("val").strip()
                was_quoted = raw_token.startswith('"') or raw_token.startswith("'")
                raw = raw_token
                if (raw.startswith('"') and raw.endswith('"')) or (raw.startswith("'") and raw.endswith("'")):
                    raw = raw[1:-1]
                if not raw:
                    continue
                if raw.strip().lower() in ignore_tokens:
                    continue
                # If the value is unquoted, require it to look like a code.
                # This prevents false positives from snippets like: reason_code: dispute["network_reason_code"]
                if not was_quoted:
                    if not (
                        re.fullmatch(r"\d{2}\.\d(?:\.\d)?", raw)  # Visa-like
                        or re.fullmatch(r"\d{4}", raw)  # Mastercard-like
                        or re.fullmatch(r"[A-Z]\d{2}", raw)  # Amex-like
                        or re.fullmatch(r"(?:UA\d{2}|RN2|[A-Z]{2})", raw)  # Discover-like
                        or re.fullmatch(r"[A-Z][A-Z0-9_]{2,}", raw)  # non-card code-like
                    ):
                        continue

                # Determine namespace heuristically
                namespace = "other"
                if last_pm_type in {"paypal", "klarna"} and field == "reason_code":
                    namespace = last_pm_type
                elif "paypal" in rel.lower() or ("payment_method_details" in line and "paypal" in line):
                    namespace = "paypal"
                elif "klarna" in rel.lower() or "klarna" in line.lower():
                    namespace = "klarna"
                else:
                    # Try to infer card network by common shapes (for both network_reason_code and docs that say reason_code)
                    if re.fullmatch(r"\d{2}\.\d(?:\.\d)?", raw):
                        namespace = "visa"
                    elif re.fullmatch(r"\d{4}", raw):
                        namespace = "mastercard"
                    elif re.fullmatch(r"[A-Z]\d{2}", raw):
                        namespace = "amex"
                    elif re.fullmatch(r"(?:UA\d{2}|RN2|[A-Z]{2})", raw):
                        namespace = "discover"

                key = (namespace, raw)
                rec = found.get(key)
                if rec is None:
                    unified = NON_CARD_UNIFIED_MAP.get(raw)
                    rec = ReasonCodeRecord(
                        namespace=namespace,
                        code=raw,
                        description=None,
                        unified_category=unified,
                        network_family="non_card_dispute" if namespace in {"paypal", "klarna"} else None,
                        source_type="observed",
                        unmapped=(namespace in {"paypal", "klarna", "other"} and unified is None),
                        sources=[],
                    )
                    found[key] = rec
                rec.sources.append(SourceRef(path=rel, line=i, kind="observed"))

            # OpenAPI gateway response keys (e.g., UNAUTHORIZED, QUOTA_EXCEEDED)
            if path.name == "openapi.yaml":
                if line.strip() == "x-amazon-apigateway-gateway-responses:":
                    in_gateway_responses = True
                    continue
                if in_gateway_responses:
                    # Block ends when we hit a top-level (no-indent) key
                    if re.match(r"^[A-Za-z0-9_-]+:\s*$", line) and not line.startswith(" "):
                        in_gateway_responses = False
                        continue
                    em = openapi_gateway_response_key_re.match(line)
                    if em:
                        token = em.group(1)
                        if token in {"DEFAULT_4XX", "DEFAULT_5XX"}:
                            continue
                        namespace = "openapi_gateway_response"
                        unified = NON_CARD_UNIFIED_MAP.get(token)
                        key = (namespace, token)
                        rec = found.get(key)
                        if rec is None:
                            rec = ReasonCodeRecord(
                                namespace=namespace,
                                code=token,
                                description=None,
                                unified_category=unified,
                                network_family="other",
                                source_type="observed",
                                unmapped=(unified is None),
                                sources=[],
                            )
                            found[key] = rec
                        rec.sources.append(SourceRef(path=rel, line=i, kind="observed"))

    return list(found.values())


def merge_records(canonical: List[ReasonCodeRecord], observed: List[ReasonCodeRecord]) -> List[ReasonCodeRecord]:
    merged: Dict[Tuple[str, str], ReasonCodeRecord] = {}

    def upsert(rec: ReasonCodeRecord) -> None:
        k = rec.key()
        if k not in merged:
            if rec.sources is None:
                rec.sources = []
            merged[k] = rec
            return

        existing = merged[k]

        # Prefer canonical fields when available
        if existing.description is None and rec.description is not None:
            existing.description = rec.description
        if existing.unified_category is None and rec.unified_category is not None:
            existing.unified_category = rec.unified_category
        if existing.network_family is None and rec.network_family is not None:
            existing.network_family = rec.network_family

        # Source type: canonical wins
        if existing.source_type != "canonical" and rec.source_type == "canonical":
            existing.source_type = "canonical"

        # Unmapped: only true if we genuinely have no mapping
        existing.unmapped = existing.unified_category is None and existing.source_type != "canonical"

        # Merge sources, de-dupe
        seen = {(s.path, s.line, s.kind) for s in existing.sources or []}
        for s in rec.sources or []:
            key = (s.path, s.line, s.kind)
            if key in seen:
                continue
            existing.sources.append(s)
            seen.add(key)

    for r in canonical:
        upsert(r)
    for r in observed:
        upsert(r)

    # Final normalization
    for r in merged.values():
        if r.network_family:
            r.network_family = _normalize_family(r.network_family)
        if r.unified_category and r.unified_category not in UNIFIED_CATEGORIES:
            r.unified_category = None
        if r.sources is None:
            r.sources = []

    # Stable sort
    return sorted(merged.values(), key=lambda x: (x.namespace, x.code))


def _count_by(records: List[ReasonCodeRecord], key_fn) -> Dict[str, int]:
    counts: Dict[str, int] = defaultdict(int)
    for r in records:
        k = key_fn(r) or "null"
        counts[str(k)] += 1
    return dict(sorted(counts.items(), key=lambda kv: (-kv[1], kv[0])))


def _md_table(rows: List[List[str]], headers: List[str]) -> str:
    # Basic Markdown table renderer
    lines = []
    lines.append("| " + " | ".join(headers) + " |")
    lines.append("| " + " | ".join(["---"] * len(headers)) + " |")
    for row in rows:
        lines.append("| " + " | ".join(row) + " |")
    return "\n".join(lines)


def write_outputs(records: List[ReasonCodeRecord]) -> None:
    payload = {
        "generated_at": _now_iso(),
        "root": str(BASE_DIR.relative_to(REPO_ROOT)),
        "counts": {
            "total": len(records),
            "by_namespace": _count_by(records, lambda r: r.namespace),
            "by_unified_category": _count_by(records, lambda r: r.unified_category),
            "by_network_family": _count_by(records, lambda r: r.network_family),
            "by_source_type": _count_by(records, lambda r: r.source_type),
            "unmapped": sum(1 for r in records if r.unmapped),
        },
        "records": [
            {
                **{k: v for k, v in asdict(r).items() if k != "sources"},
                "sources": [asdict(s) for s in (r.sources or [])],
            }
            for r in records
        ],
    }
    OUT_JSON.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    # CSV
    with OUT_CSV.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(
            f,
            fieldnames=[
                "namespace",
                "code",
                "description",
                "unified_category",
                "network_family",
                "source_type",
                "unmapped",
                "sources",
            ],
        )
        w.writeheader()
        for r in records:
            src = "; ".join(
                f"{s.path}:{s.line}" if s.line is not None else f"{s.path}"
                for s in (r.sources or [])
            )
            w.writerow(
                {
                    "namespace": r.namespace,
                    "code": r.code,
                    "description": r.description or "",
                    "unified_category": r.unified_category or "",
                    "network_family": r.network_family or "",
                    "source_type": r.source_type,
                    "unmapped": "true" if r.unmapped else "false",
                    "sources": src,
                }
            )

    # Markdown report
    counts = payload["counts"]
    md_lines: List[str] = []
    md_lines.append("# Reason Codes Catalog (Dispute Schema)")
    md_lines.append("")
    md_lines.append(f"**Generated:** `{payload['generated_at']}`")
    md_lines.append(f"**Scope:** `{payload['root']}` (in-repo exhaustive)")
    md_lines.append("")

    md_lines.append("## Summary")
    md_lines.append("")
    md_lines.append(f"- **Total codes:** {counts['total']}")
    md_lines.append(f"- **Unmapped (non-canonical observed):** {counts['unmapped']}")
    md_lines.append("")

    md_lines.append("### Counts by namespace")
    md_lines.append("")
    md_lines.append(_md_table([[k, str(v)] for k, v in counts["by_namespace"].items()], ["namespace", "count"]))
    md_lines.append("")

    md_lines.append("### Counts by unified category (`DisputeReason`)")
    md_lines.append("")
    md_lines.append(_md_table([[k, str(v)] for k, v in counts["by_unified_category"].items()], ["unified_category", "count"]))
    md_lines.append("")

    md_lines.append("### Counts by network-family bucket")
    md_lines.append("")
    md_lines.append(_md_table([[k, str(v)] for k, v in counts["by_network_family"].items()], ["network_family", "count"]))
    md_lines.append("")

    md_lines.append("## Tables: Unified categories (`DisputeReason`)")
    md_lines.append("")
    for cat in sorted(UNIFIED_CATEGORIES):
        subset = [r for r in records if r.unified_category == cat]
        if not subset:
            continue
        md_lines.append(f"### {cat}")
        md_lines.append("")
        rows = []
        for r in subset:
            rows.append(
                [
                    r.namespace,
                    r.code,
                    (r.network_family or ""),
                    (r.description or ""),
                    ("canonical" if r.source_type == "canonical" else "observed"),
                ]
            )
        md_lines.append(_md_table(rows, ["namespace", "code", "network_family", "description", "source_type"]))
        md_lines.append("")

    md_lines.append("## Tables: Network-family buckets")
    md_lines.append("")
    for fam in sorted(NETWORK_FAMILIES):
        subset = [r for r in records if _normalize_family(r.network_family or "") == fam]
        if not subset:
            continue
        md_lines.append(f"### {fam}")
        md_lines.append("")
        rows = []
        for r in subset:
            rows.append(
                [
                    r.namespace,
                    r.code,
                    (r.unified_category or ""),
                    (r.description or ""),
                    ("true" if r.unmapped else "false"),
                ]
            )
        md_lines.append(_md_table(rows, ["namespace", "code", "unified_category", "description", "unmapped"]))
        md_lines.append("")

    unmapped = [r for r in records if r.unmapped]
    if unmapped:
        md_lines.append("## Observed-only codes needing mapping")
        md_lines.append("")
        rows = []
        for r in unmapped:
            rows.append(
                [
                    r.namespace,
                    r.code,
                    (r.network_family or ""),
                    (r.description or ""),
                    "; ".join(sorted({s.path for s in (r.sources or [])})),
                ]
            )
        md_lines.append(_md_table(rows, ["namespace", "code", "network_family", "description", "sources"]))
        md_lines.append("")

    OUT_MD.write_text("\n".join(md_lines).rstrip() + "\n", encoding="utf-8")


def main() -> int:
    if not CANONICAL_TS.exists():
        raise SystemExit(f"Missing canonical file: {CANONICAL_TS}")

    canonical = parse_canonical_network_reason_codes(CANONICAL_TS)
    observed = scan_observed_reason_codes(BASE_DIR)
    records = merge_records(canonical, observed)
    write_outputs(records)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


