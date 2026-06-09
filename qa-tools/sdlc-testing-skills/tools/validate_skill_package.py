#!/usr/bin/env python3
"""Validate the QA skill package structure.

Default mode fails on structural errors and prints warnings for schema/template
drift. Use --strict-schema to fail on testcase schema/template mismatch.
"""

from __future__ import annotations

import argparse
import csv
import re
import sys
from pathlib import Path

import yaml


if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")


ROOT_DEFAULT = Path(__file__).resolve().parent.parent
ALLOWED_FRONTMATTER = {"name", "description", "license", "allowed-tools", "metadata"}
EXCLUDED_PARTS = {".git", ".venv", "testing-output", "project"}
RUNTIME_PATHS = {".env", ".env.local", ".env.secrets", "tools/qmetry-config.json"}


def rel(path: Path, root: Path) -> str:
    return path.relative_to(root).as_posix()


def is_excluded(path: Path, root: Path) -> bool:
    return bool(set(path.relative_to(root).parts) & EXCLUDED_PARTS)


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def parse_frontmatter(path: Path) -> dict:
    text = read_text(path)
    match = re.match(r"^---\r?\n(.*?)\r?\n---", text, re.S)
    if not match:
        raise ValueError("missing YAML frontmatter")
    data = yaml.safe_load(match.group(1))
    if not isinstance(data, dict):
        raise ValueError("frontmatter must be a YAML dictionary")
    return data


def check_bom(root: Path, errors: list[str]) -> None:
    for path in root.rglob("*"):
        if not path.is_file() or is_excluded(path, root):
            continue
        if path.read_bytes().startswith(b"\xef\xbb\xbf"):
            errors.append(f"{rel(path, root)}: UTF-8 BOM detected")


def check_frontmatter(root: Path, errors: list[str]) -> None:
    skill_files = [root / "SKILL.md", *sorted((root / "skills").rglob("*.md"))]
    for path in skill_files:
        try:
            data = parse_frontmatter(path)
        except Exception as exc:
            errors.append(f"{rel(path, root)}: {exc}")
            continue

        unexpected = set(data) - ALLOWED_FRONTMATTER
        if unexpected:
            errors.append(f"{rel(path, root)}: unexpected frontmatter keys {sorted(unexpected)}")
        name = data.get("name")
        expected = "qa-skill" if path.name == "SKILL.md" else path.parent.name
        if name != expected:
            errors.append(f"{rel(path, root)}: name {name!r} != expected {expected!r}")
        if not isinstance(data.get("description"), str) or not data["description"].strip():
            errors.append(f"{rel(path, root)}: missing description")


def check_line_limits(root: Path, errors: list[str]) -> None:
    limits = {root / "SKILL.md": 150}
    for path in (root / "skills").rglob("*.md"):
        limits[path] = 150
    for path, limit in limits.items():
        count = len(read_text(path).splitlines())
        if count > limit:
            errors.append(f"{rel(path, root)}: {count} lines > {limit}")


def check_duplicate_routing(root: Path, errors: list[str]) -> None:
    routing_markers = ("| User intent |", "## Routing Rules", "## Bảng định tuyến")
    allowed = {root / "SKILL.md"}
    candidates = [
        root / "AGENTS.md",
        root / "CLAUDE.md",
        root / ".clinerules",
        root / ".cursor" / "rules" / "qa-testing.mdc",
        root / ".github" / "copilot-instructions.md",
    ]
    for path in candidates:
        if not path.exists():
            continue
        text = read_text(path)
        if path not in allowed and any(marker in text for marker in routing_markers):
            errors.append(f"{rel(path, root)}: duplicate routing table/section")


def check_heavy_references(root: Path, warnings: list[str]) -> None:
    for path in (root / "references").rglob("*"):
        if not path.is_file():
            continue
        size = path.stat().st_size
        max_size = 30_000 if "skill-details" in path.relative_to(root).parts else 20_000
        if size > max_size:
            warnings.append(f"{rel(path, root)}: reference is large ({size} bytes)")


def check_runtime_files(root: Path, warnings: list[str]) -> None:
    for item in RUNTIME_PATHS:
        if (root / item).exists():
            warnings.append(f"{item}: runtime/local file exists in workspace; keep out of shared releases")


def check_tc_schema_template(root: Path, warnings: list[str]) -> None:
    schema_path = root / "shared-schema" / "testcase.schema.yaml"
    template_path = root / "references" / "tc-template.tsv"
    if not schema_path.exists() or not template_path.exists():
        return
    schema = yaml.safe_load(read_text(schema_path))
    schema_cols = [column["name"] for column in schema.get("columns", [])]
    with template_path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.reader(handle, delimiter="\t")
        header = next(reader, [])
    if header != schema_cols:
        warnings.append("tc-template.tsv header differs from shared-schema/testcase.schema.yaml columns")
        return

    def normalize_schema_scalar(value: object) -> str:
        if value is True:
            return "Yes"
        if value is False:
            return "No"
        return str(value)

    enum_by_col = {
        column["name"]: {normalize_schema_scalar(value) for value in column.get("values", [])}
        for column in schema.get("columns", [])
        if column.get("type") == "enum"
    }
    pattern_by_col = {
        column["name"]: re.compile(column["pattern"])
        for column in schema.get("columns", [])
        if column.get("pattern")
    }

    with template_path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.reader(handle, delimiter="\t")
        next(reader, None)
        for row_num, raw_row in enumerate(reader, start=2):
            if row_num > 6:
                break
            if len(raw_row) != len(header):
                warnings.append(
                    f"tc-template.tsv row {row_num}: {len(raw_row)} fields, expected {len(header)}"
                )
                continue
            row = dict(zip(header, raw_row))
            for column, allowed in enum_by_col.items():
                value = (row.get(column) or "").strip()
                if value and value not in allowed:
                    warnings.append(
                        f"tc-template.tsv row {row_num}: {column}={value!r} not in schema enum {sorted(allowed)}"
                    )
            for column, pattern in pattern_by_col.items():
                value = (row.get(column) or "").strip()
                if value and not pattern.fullmatch(value):
                    warnings.append(
                        f"tc-template.tsv row {row_num}: {column}={value!r} does not match {pattern.pattern!r}"
                    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=str(ROOT_DEFAULT), help="Skill package root")
    parser.add_argument("--strict-schema", action="store_true", help="Fail on schema/template warnings")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    errors: list[str] = []
    warnings: list[str] = []

    check_bom(root, errors)
    check_frontmatter(root, errors)
    check_line_limits(root, errors)
    check_duplicate_routing(root, errors)
    check_heavy_references(root, warnings)
    check_runtime_files(root, warnings)
    check_tc_schema_template(root, warnings)

    for warning in warnings:
        print(f"WARN: {warning}")
    for error in errors:
        print(f"ERROR: {error}")

    if errors or (args.strict_schema and warnings):
        return 1
    print("Skill package validation passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
