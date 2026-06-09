#!/usr/bin/env python3

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path


EXPORTER_VERSION = "1.1.0"

FUNCTIONAL_HEADER = [
    "STT",
    "Summary",
    "Test Level",
    "Precondition",
    "Test Data",
    "Step summary",
    "Expected result",
    "Priority",
    "Story Linkages",
    "Test Type",
    "Smoke",
    "Auto",
    "Phụ thuộc TC",
    "Teardown",
    "Trace",
    "Design Refs",
    "API Refs",
]

# Matches `US-10`, `US-10.1`, `US-10.1.2`, case-insensitive on `US`.
US_ID_RE = re.compile(r"\bUS-(\d+(?:\.\d+)*)", re.IGNORECASE)

SIT_GROUP_HEADER = [
    "",
    "",
    "",
    "",
    "",
    "",
    "Hệ thống A",
    "",
    "",
    "Hệ thống B",
    "",
    "",
    "",
    "",
    "",
    "",
    "",
    "",
    "",
]

SIT_HEADER = [
    "No",
    "Testcase ID",
    "Test Summary",
    "Precondition",
    "Test Data",
    "Steps",
    "Expected Result",
    "Actual Result",
    "Test Result",
    "Expected Result",
    "Actual Result",
    "Test Result",
    "Final Result",
    "Priority",
    "ID Bugs",
    "Link evidence",
    "Màn hình test",
    "Thời gian test",
    "Automation Level",
]


@dataclass
class TestCase:
    test_id: str
    title: str
    priority_tag: str = ""
    planned_tag: str = ""
    section_path: list[str] = field(default_factory=list)
    metadata: dict[str, str] = field(default_factory=dict)
    blocks: dict[str, str] = field(default_factory=dict)


@dataclass
class ExportResult:
    functional_tsv: str
    sit_tsv: str
    manifest_json: str
    output_names: dict[str, str]
    functional_count: int
    sit_count: int
    per_us_tsvs: dict[str, str] = field(default_factory=dict)
    per_us_names: dict[str, str] = field(default_factory=dict)


HEADING_RE = re.compile(r"^(#{2,6})\s+(.+?)\s*$")
# Intentionally lenient on READ: accepts canonical `TC-NNN` AND the legacy
# `TC-{AREA}-NNN` form (pre-migration / hand-authored docs). Canonical `TC-\d+`
# is enforced upstream by `validate_proposal` at `approve test`; tightening here
# would silently reclassify a legacy heading as a section and drop the case.
TC_HEADING_RE = re.compile(r"^(TC-[A-Za-z0-9_-]+)\s*:\s*(.+?)\s*$")
METADATA_RE = re.compile(r"^\*\*(.+?)\*\*:\s*(.*)$")
FENCE_RE = re.compile(r"^\s*```")
PRIORITY_RE = re.compile(r"`(P[0-2])`|\b(P[0-2])\b")
PLANNED_RE = re.compile(r"`\[(planned-[^\]]+)\]`|\[(planned-[^\]]+)\]")
VERSION_RE = re.compile(r"(?:proposal|test-cases)-v([A-Za-z0-9_.-]+)\.md$")


def sha256_text(text: str) -> str:
    # Hashes the DECODED text. Sources are read with `utf-8-sig` (BOM stripped) in
    # text mode (universal newlines → LF), so `source_sha256` is intentionally
    # robust to BOM and CRLF/LF noise: those don't change the parsed test cases or
    # the generated TSVs, so they must not flip `--check` to "stale".
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def display_path(path: Path) -> str:
    resolved = path.resolve()
    try:
        return resolved.relative_to(Path.cwd().resolve()).as_posix()
    except ValueError:
        return str(resolved)


def strip_inline_comment(value: str) -> str:
    return re.sub(r"\s*<!--.*?-->\s*", "", value).strip()


def clean_value(value: str) -> str:
    value = strip_inline_comment(value)
    value = value.strip()
    if value.startswith("`") and value.endswith("`") and len(value) >= 2:
        value = value[1:-1]
    return value.strip()


def clean_title(raw_title: str) -> tuple[str, str, str]:
    priority_match = PRIORITY_RE.search(raw_title)
    planned_match = PLANNED_RE.search(raw_title)
    priority = next((group for group in (priority_match.groups() if priority_match else ()) if group), "")
    planned = next((group for group in (planned_match.groups() if planned_match else ()) if group), "")
    title = PRIORITY_RE.sub("", raw_title)
    title = PLANNED_RE.sub("", title)
    title = title.replace("`", "").strip()
    title = re.sub(r"\s+", " ", title)
    return title, priority, planned


def append_block(blocks: dict[str, str], name: str | None, line: str) -> None:
    if not name:
        return
    existing = blocks.get(name, "")
    if existing:
        blocks[name] = existing + "\n" + line.rstrip()
    else:
        blocks[name] = line.rstrip()


def parse_test_cases(markdown: str) -> list[TestCase]:
    cases: list[TestCase] = []
    current: TestCase | None = None
    active_block: str | None = None
    in_fence = False
    section_stack: list[tuple[int, str]] = []

    lines = markdown.splitlines()
    for line in lines:
        if FENCE_RE.match(line):
            in_fence = not in_fence
            append_block(current.blocks if current else {}, active_block, line)
            continue

        if not in_fence:
            heading_match = HEADING_RE.match(line)
            if heading_match:
                level = len(heading_match.group(1))
                title_text = heading_match.group(2).strip()
                tc_match = TC_HEADING_RE.match(title_text)
                if tc_match and level >= 3:
                    title, priority, planned = clean_title(tc_match.group(2))
                    current = TestCase(
                        test_id=tc_match.group(1),
                        title=title,
                        priority_tag=priority,
                        planned_tag=planned,
                        section_path=[item[1] for item in section_stack],
                    )
                    cases.append(current)
                    active_block = None
                    continue

                current = None
                active_block = None
                while section_stack and section_stack[-1][0] >= level:
                    section_stack.pop()
                section_stack.append((level, title_text))
                continue

            if current:
                block_match = re.match(r"^\*\*(Given|When|Then|Test Data)\*\*:\s*$", line)
                if block_match:
                    active_block = block_match.group(1)
                    current.blocks.setdefault(active_block, "")
                    continue

                metadata_match = METADATA_RE.match(line)
                if metadata_match:
                    key = clean_value(metadata_match.group(1))
                    value = clean_value(metadata_match.group(2))
                    current.metadata[key] = value
                    active_block = None
                    continue

        if current and active_block:
            append_block(current.blocks, active_block, line)

    return cases


def first_metadata(case: TestCase, *keys: str, default: str = "") -> str:
    for key in keys:
        value = case.metadata.get(key)
        if value:
            return value
    return default


def block(case: TestCase, name: str) -> str:
    return case.blocks.get(name, "").strip() or "—"


def priority(case: TestCase) -> str:
    raw = first_metadata(case, "Priority", default=case.priority_tag).upper()
    if raw == "P0":
        return "High"
    if raw == "P1":
        return "Medium"
    if raw == "P2":
        return "Low"
    return raw or "Medium"


def auto_flag(case: TestCase) -> str:
    boundary = first_metadata(case, "Manual / Auto boundary").lower()
    intent = first_metadata(case, "Automation intent").lower()
    if "auto=y" in intent or boundary == "automated":
        return "Y"
    return "N"


def export_target(case: TestCase) -> str:
    explicit = first_metadata(case, "Export target").lower()
    if explicit in {"functional", "sit", "none"}:
        return explicit
    if "SIT" in case.test_id.upper() or "SIT / Integration Scenarios" in case.section_path:
        return "sit"
    if first_metadata(case, "Systems involved", "System A expected", "System B expected"):
        return "sit"
    return "functional"


def test_type(case: TestCase) -> str:
    explicit = first_metadata(case, "Test Type")
    if explicit:
        return explicit
    upper_id = case.test_id.upper()
    if "PERF" in upper_id:
        return "Non-Functional"
    if "SEC" in upper_id:
        return "Non-Functional"
    if "A11Y" in upper_id:
        return "Non-Functional"
    if "Regression" in case.title:
        return "Regression"
    return "Functional"


def functional_row(case: TestCase) -> list[str]:
    traceability = first_metadata(case, "Traceability", default="—")
    api_refs = first_metadata(case, "API / NFR refs")
    trace = traceability if not api_refs else f"{traceability}; {api_refs}"
    test_data = block(case, "Test Data")
    data_needs = first_metadata(case, "Data needs")
    if data_needs and test_data != "—":
        test_data = f"{data_needs}\n{test_data}"
    elif data_needs:
        test_data = data_needs

    return [
        case.test_id,
        case.title,
        first_metadata(case, "Test Level", default="e2e"),
        block(case, "Given"),
        test_data,
        block(case, "When"),
        block(case, "Then"),
        priority(case),
        traceability,
        test_type(case),
        first_metadata(case, "Smoke", default="N"),
        auto_flag(case),
        first_metadata(case, "Depends on", "Phụ thuộc TC", default="—"),
        first_metadata(case, "Teardown / reset", default="—"),
        trace,
        first_metadata(case, "Design states referenced", "Design Refs", default="—"),
        first_metadata(case, "API / NFR refs", "API Refs", default="—"),
    ]


def us_ids_from_case(case: TestCase) -> list[str]:
    """Extract sorted unique US IDs from a case's Traceability metadata."""
    traceability = first_metadata(case, "Traceability")
    if not traceability:
        return []
    matches = US_ID_RE.findall(traceability)
    return sorted({f"US-{m}" for m in matches})


def slugify_us_id(us_id: str) -> str:
    """Convert `US-10.1` → `us-10-1` for filesystem-safe filenames."""
    return us_id.lower().replace(".", "-")


def sit_row(case: TestCase, index: int) -> list[str]:
    level = first_metadata(case, "Test Level", default="integration")
    if not case.title.startswith("[TL:"):
        summary = f"[TL:{level}] {case.title}"
    else:
        summary = case.title

    return [
        str(index),
        case.test_id,
        summary,
        block(case, "Given"),
        first_metadata(case, "Data needs", default=block(case, "Test Data")),
        block(case, "When"),
        first_metadata(case, "System A expected", default=block(case, "Then")),
        "",
        "",
        first_metadata(case, "System B expected"),
        "",
        "",
        "",
        priority(case),
        "",
        "",
        first_metadata(case, "Screen under test", "Màn hình test"),
        "",
        level,
    ]


def write_tsv(rows: list[list[str]]) -> str:
    output = io.StringIO()
    writer = csv.writer(output, delimiter="\t", lineterminator="\n")
    writer.writerows(rows)
    return output.getvalue()


def version_from_path(path: Path) -> str:
    match = VERSION_RE.search(path.name)
    if match:
        return match.group(1)
    return "X"


def generate_export(
    test_cases_path: Path,
    *,
    output_dir: Path | None = None,
    per_us: bool = False,
) -> ExportResult:
    source_text = test_cases_path.read_text(encoding="utf-8-sig")
    cases = parse_test_cases(source_text)
    functional_cases = [case for case in cases if export_target(case) == "functional"]
    sit_cases = [case for case in cases if export_target(case) == "sit"]

    sprint_version = version_from_path(test_cases_path)
    functional_name = f"test-cases-functional-v{sprint_version}.tsv"
    sit_name = f"test-cases-sit-v{sprint_version}.tsv"
    manifest_name = f"test-cases-export-manifest-v{sprint_version}.json"

    functional_rows = [FUNCTIONAL_HEADER, *(functional_row(case) for case in functional_cases)]
    sit_rows = [
        SIT_GROUP_HEADER,
        SIT_HEADER,
        *(sit_row(case, index) for index, case in enumerate(sit_cases, start=1)),
    ]

    per_us_tsvs: dict[str, str] = {}
    per_us_names: dict[str, str] = {}
    if per_us:
        # Group functional cases by US IDs found in Traceability. A case may be
        # listed under multiple US groups when it covers more than one story.
        groups: dict[str, list[TestCase]] = {}
        for case in functional_cases:
            us_ids = us_ids_from_case(case)
            if not us_ids:
                groups.setdefault("no-us", []).append(case)
                continue
            for us_id in us_ids:
                groups.setdefault(us_id, []).append(case)
        for us_id in sorted(groups):
            slug = "no-us" if us_id == "no-us" else slugify_us_id(us_id)
            name = f"test-cases-functional-{slug}-v{sprint_version}.tsv"
            rows = [FUNCTIONAL_HEADER, *(functional_row(case) for case in groups[us_id])]
            per_us_tsvs[us_id] = write_tsv(rows)
            per_us_names[us_id] = name

    resolved_output_dir = output_dir or (test_cases_path.parent / "generated")
    outputs: dict[str, object] = {
        "functional": display_path(resolved_output_dir / functional_name),
        "sit": display_path(resolved_output_dir / sit_name),
    }
    if per_us:
        outputs["per_us"] = {
            us_id: display_path(resolved_output_dir / "per-us" / per_us_names[us_id])
            for us_id in per_us_names
        }

    counts: dict[str, object] = {
        "total_cases": len(cases),
        "functional_cases": len(functional_cases),
        "sit_cases": len(sit_cases),
    }
    if per_us:
        counts["per_us_groups"] = len(per_us_tsvs)

    manifest = {
        "schema": "prism.test_case_export_manifest.v1",
        "exporter": "core/tools/export_test_cases.py",
        "exporter_version": EXPORTER_VERSION,
        "functional_header": FUNCTIONAL_HEADER,
        "functional_column_count": len(FUNCTIONAL_HEADER),
        "source_file": display_path(test_cases_path),
        "source_sha256": sha256_text(source_text),
        "outputs": outputs,
        "counts": counts,
    }

    return ExportResult(
        functional_tsv=write_tsv(functional_rows),
        sit_tsv=write_tsv(sit_rows),
        manifest_json=json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        output_names={
            "functional": functional_name,
            "sit": sit_name,
            "manifest": manifest_name,
        },
        functional_count=len(functional_cases),
        sit_count=len(sit_cases),
        per_us_tsvs=per_us_tsvs,
        per_us_names=per_us_names,
    )


def write_export(test_cases_path: Path, output_dir: Path, *, per_us: bool = False) -> list[Path]:
    result = generate_export(test_cases_path, output_dir=output_dir, per_us=per_us)
    output_dir.mkdir(parents=True, exist_ok=True)
    outputs = {
        result.output_names["functional"]: result.functional_tsv,
        result.output_names["sit"]: result.sit_tsv,
        result.output_names["manifest"]: result.manifest_json,
    }
    written: list[Path] = []
    for name, content in outputs.items():
        path = output_dir / name
        path.write_text(content, encoding="utf-8")
        written.append(path)
    if per_us and result.per_us_tsvs:
        per_us_dir = output_dir / "per-us"
        per_us_dir.mkdir(parents=True, exist_ok=True)
        expected_paths = {per_us_dir / name for name in result.per_us_names.values()}
        sprint_version = version_from_path(test_cases_path)
        for stale_path in per_us_dir.glob(f"test-cases-functional-*-v{sprint_version}.tsv"):
            if stale_path not in expected_paths:
                stale_path.unlink()
        for us_id, content in result.per_us_tsvs.items():
            path = per_us_dir / result.per_us_names[us_id]
            path.write_text(content, encoding="utf-8")
            written.append(path)
    elif per_us:
        per_us_dir = output_dir / "per-us"
        if per_us_dir.is_dir():
            sprint_version = version_from_path(test_cases_path)
            for stale_path in per_us_dir.glob(f"test-cases-functional-*-v{sprint_version}.tsv"):
                stale_path.unlink()
    return written


def check_export(test_cases_path: Path, output_dir: Path, *, per_us: bool = False) -> list[str]:
    result = generate_export(test_cases_path, output_dir=output_dir, per_us=per_us)
    expected = {
        output_dir / result.output_names["functional"]: result.functional_tsv,
        output_dir / result.output_names["sit"]: result.sit_tsv,
        output_dir / result.output_names["manifest"]: result.manifest_json,
    }
    if per_us:
        per_us_dir = output_dir / "per-us"
        expected_per_us_paths: set[Path] = set()
        for us_id, content in result.per_us_tsvs.items():
            path = per_us_dir / result.per_us_names[us_id]
            expected[path] = content
            expected_per_us_paths.add(path)
    errors: list[str] = []
    for path, expected_content in expected.items():
        if not path.exists():
            errors.append(f"missing generated export: {path}")
            continue
        actual = path.read_text(encoding="utf-8")
        if actual != expected_content:
            errors.append(f"stale generated export: {path}")
    if per_us and per_us_dir.is_dir():
        sprint_version = version_from_path(test_cases_path)
        for path in sorted(per_us_dir.glob(f"test-cases-functional-*-v{sprint_version}.tsv")):
            if path not in expected_per_us_paths:
                errors.append(f"unexpected stale generated export: {path}")
    return errors


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Export PRISM testing proposal/test-cases Markdown into generated Functional/SIT TSV companions."
    )
    parser.add_argument("--test-cases", required=True, help="Path to testing proposals/test-cases-v{X}.md or sealed test-cases.md")
    parser.add_argument(
        "--output-dir",
        help="Output directory for generated TSV files. Defaults to a generated/ sibling.",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Check generated files are present and up to date instead of writing them.",
    )
    parser.add_argument(
        "--per-us",
        action="store_true",
        help=(
            "Also emit one functional TSV per User Story under <output-dir>/per-us/. "
            "Groups cases by US-NNN found in Traceability metadata. Cases tracing to "
            "multiple US IDs appear in each group; cases without a US trace go into "
            "test-cases-functional-no-us-v{X}.tsv. Combined files are still emitted."
        ),
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    test_cases_path = Path(args.test_cases).resolve()
    output_dir = Path(args.output_dir).resolve() if args.output_dir else test_cases_path.parent / "generated"

    if not test_cases_path.exists():
        print(f"ERROR: test cases file not found: {test_cases_path}", file=sys.stderr)
        return 2

    if args.check:
        errors = check_export(test_cases_path, output_dir, per_us=args.per_us)
        if errors:
            for error in errors:
                print(f"ERROR: {error}", file=sys.stderr)
            return 1
        print("Test case exports are up to date")
        return 0

    for path in write_export(test_cases_path, output_dir, per_us=args.per_us):
        print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
