#!/usr/bin/env python3
"""validate_proposal.py — Phase 2.

Validates a sprint proposal markdown file for structural correctness BEFORE
`apply_proposal.py` would merge it into living truth.

Rules:
  VP-1  Frontmatter present + required fields valid (status, sprint, phase, version, applied_to_living)
  VP-2  Has at least one ## New / ## Updated / ## Removed section
  VP-3  Each item anchor matches strict format `[PREFIX]-\\d{3,}` and is unique
  VP-4  Each anchor is followed by an H3 heading line + content
  VP-5  (--against-living) Trace IDs resolve against living-truth anchors (warn-level)
  VP-6  Phase 9 routing/trace tags are present where required
  VP-7  Anchor prefixes belong to the proposal's owning phase
  VP-8  Split proposal file contains only prefixes for its Living Truth target
  VP-9  Split proposal path matches canonical target filename rules
  VP-10 Prohibited proposal sections / split epic content ownership
  VP-11 Adding catalog items (components/screens/rules) requires (re-)authoring the
        matching singleton `*-OVERVIEW-001` block in the same proposal
  VP-12 No markdown table in the preamble (before the first ## New/Updated/Removed) —
        a table there is misplaced mergeable content, silently dropped at seal

  Overview-regeneration no-shrink (a `## Updated *-OVERVIEW-001` that silently drops a
  still-live traceability row) is checked on the merged/effective view by
  validate_living_truth.py `LTV-SHRINK` (approve via --effective, and at seal), where
  cross-phase removals are visible — not here, to avoid false positives.

Exit codes (per discussion doc §9.C):
  0  OK — no blocker findings; warnings allowed unless --strict
  1  validation fail — one or more blocker findings
  2  file not found
  3  config error (reserved)
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from apply_proposal import (  # noqa: E402
    ANCHOR_RE,
    CODE_FENCE_RE,
    TAG_SCAN_WINDOW,
    parse_anchored_blocks,
    parse_frontmatter,
    split_proposal_sections,
)


REQUIRED_FRONTMATTER = (
    "status",
    "version",
    "sprint",
    "phase",
    "sprint_id",
    "created",
    "updated",
    "approved_by",
    "applied_to_living",
)
VALID_STATUSES = ("DRAFT", "APPROVED")
VALID_PHASES = ("product", "design", "architecture", "testing")
# Phase 9: 21 ID prefixes (EPIC → EP rename; COMP → DS-COMP + ARCH-COMP split; 13 new).
VALID_ID_PREFIXES = (
    "EP", "FR", "US", "AC", "BR", "GLOSS", "PERSONA", "MR",
    "SCREEN", "DS-COMP",
    "ARCH", "ARCH-COMP", "NFR", "SEQ", "ENT", "ADR", "FLOW", "API", "EVT", "PR",
    "TC",
    # Phase-overview narrative (singleton anchored block per file; routes to prd / architecture / design-system).
    "PRD-OVERVIEW", "ARCH-OVERVIEW", "DESIGN-OVERVIEW",
    # Test Rule/Branch Inventory (singleton coverage block; routes to test-cases.md).
    "TEST-COVERAGE",
)

# Phase 9: support multi-segment prefixes (DS-COMP-NNN, ARCH-COMP-NNN).
STRICT_ID_RE = re.compile(r"^([A-Z]+(?:-[A-Z]+)*)-(\d{3,})$")
ANY_H2_RE = re.compile(r"^##\s+(.+?)\s*$")
H3_RE = re.compile(r"^###\s+")
KNOWN_PROPOSAL_H2 = ("New", "Updated", "Removed")
PROHIBITED_PROPOSAL_H2 = {
    "Sprint Brief": "Sprint Brief belongs in sprint-brief-v{X}.md, not inside mergeable split proposal files",
}
TRACE_RE = re.compile(r"\*\*Trace\*\*\s*:\s*(.+?)(?:\n|$)")


@dataclass
class Finding:
    level: str  # "blocker" | "warn"
    rule: str
    message: str


@dataclass
class Report:
    findings: list[Finding] = field(default_factory=list)

    @property
    def blockers(self) -> list[Finding]:
        return [f for f in self.findings if f.level == "blocker"]

    @property
    def warnings(self) -> list[Finding]:
        return [f for f in self.findings if f.level == "warn"]

    def add_blocker(self, rule: str, msg: str) -> None:
        self.findings.append(Finding("blocker", rule, msg))

    def add_warn(self, rule: str, msg: str) -> None:
        self.findings.append(Finding("warn", rule, msg))


def validate_frontmatter(fm: dict, report: Report) -> None:
    if not fm:
        report.add_blocker("VP-1", "missing YAML frontmatter (--- block at top of file)")
        return
    for key in REQUIRED_FRONTMATTER:
        if key not in fm:
            report.add_blocker("VP-1", f"frontmatter missing required key: {key}")
    if "status" in fm and fm["status"] not in VALID_STATUSES:
        report.add_blocker(
            "VP-1", f"status='{fm['status']}' invalid; expected one of {VALID_STATUSES}"
        )
    if "phase" in fm and fm["phase"] not in VALID_PHASES:
        report.add_blocker(
            "VP-1", f"phase='{fm['phase']}' invalid; expected one of {VALID_PHASES}"
        )
    sprint_int: int | None = None
    if "sprint" in fm:
        try:
            sprint_int = int(fm["sprint"])
            if sprint_int < 1:
                report.add_blocker("VP-1", f"sprint='{fm['sprint']}' must be >= 1")
        except (ValueError, TypeError):
            report.add_blocker("VP-1", f"sprint='{fm['sprint']}' must be an integer")
    if sprint_int is not None and "version" in fm:
        if fm["version"] != f"v{sprint_int}":
            report.add_blocker(
                "VP-1",
                f"version='{fm['version']}' does not match sprint number — expected 'v{sprint_int}'",
            )
    if sprint_int is not None and "sprint_id" in fm:
        expected_sprint_id = f"sprint-v{sprint_int}"
        if fm["sprint_id"] != expected_sprint_id:
            report.add_blocker(
                "VP-1",
                f"sprint_id='{fm['sprint_id']}' does not match sprint number — expected '{expected_sprint_id}'",
            )
    for key in ("created", "updated"):
        if key in fm and str(fm.get(key, "") or "").strip() == "":
            report.add_blocker("VP-1", f"frontmatter {key} must not be empty")
    if fm.get("status") == "APPROVED" and str(fm.get("approved_by", "") or "").strip() == "":
        report.add_blocker("VP-1", "approved proposal frontmatter approved_by must not be empty")
    if "applied_to_living" in fm:
        v = fm["applied_to_living"]
        if isinstance(v, bool):
            pass  # YAML `false` / `true` — both valid
        elif isinstance(v, str):
            lowered = v.strip().lower()
            if lowered not in ("false", "true", "") and not lowered.startswith("true "):
                report.add_warn(
                    "VP-1",
                    f"applied_to_living='{v}' — expected `false` (pre-seal) or `true <commit-hash>` (post-seal)",
                )
        else:
            report.add_warn(
                "VP-1",
                f"applied_to_living must be bool or string, got {type(v).__name__}",
            )


def infer_expected_phase_from_path(path: Path) -> str | None:
    """Infer phase ownership from canonical proposal/delta path conventions."""
    parts = path.parts
    for idx, part in enumerate(parts):
        if re.fullmatch(r"sprint-v\d+", part) and idx + 2 < len(parts):
            phase = parts[idx + 1]
            if phase in VALID_PHASES and parts[idx + 2] == "proposals":
                return phase
    m = re.match(r"^(product|design|architecture|testing)-delta-v\d+\.\d+\.\d+-.+\.md$", path.name)
    if m:
        return m.group(1)
    return None


TARGET_ALLOWED_PREFIXES_BY_NAME = {
    "prd": {"BR", "PRD-OVERVIEW"},
    "glossary": {"GLOSS"},
    "personas": {"PERSONA"},
    "market-research": {"MR"},
    "design-system": {"SCREEN", "DS-COMP", "DESIGN-OVERVIEW"},
    "architecture": {"ARCH", "ARCH-COMP", "ARCH-OVERVIEW"},
    "nfr": {"NFR"},
    "sequence": {"SEQ"},
    "erd": {"ENT"},
    "adr": {"ADR"},
    "data-flow": {"FLOW"},
    "api-specs": {"API"},
    "events": {"EVT"},
    "project-reference": {"PR"},
    "test-cases": {"TC", "TEST-COVERAGE"},
}

TARGET_NAMES_BY_PHASE = {
    "product": {"prd", "glossary", "personas", "market-research"},
    "design": {"design-system"},
    "architecture": {
        "architecture",
        "nfr",
        "sequence",
        "erd",
        "adr",
        "data-flow",
        "api-specs",
        "events",
        "project-reference",
    },
    "testing": {"test-cases"},
}


def infer_expected_target_prefixes_from_path(path: Path) -> tuple[set[str] | None, str | None]:
    """Infer allowed anchor prefixes for canonical split proposal files.

    Returns (allowed_prefixes, target_label). Change-pack delta files return
    (None, None).
    """
    parts = path.parts
    for idx, part in enumerate(parts):
        if not re.fullmatch(r"sprint-v\d+", part) or idx + 3 >= len(parts):
            continue
        phase = parts[idx + 1]
        if phase not in VALID_PHASES or parts[idx + 2] != "proposals":
            continue
        rel_after_proposals = parts[idx + 3:]
        name = path.name
        if not re.search(r"-v\d+\.md$", name):
            return None, None
        if phase == "product" and rel_after_proposals[0] == "epics":
            return {"EP", "FR", "US", "AC"}, "product/proposals/epics"
        target = re.sub(r"-v\d+\.md$", "", name)
        if target not in TARGET_NAMES_BY_PHASE.get(phase, set()):
            return None, None
        allowed = TARGET_ALLOWED_PREFIXES_BY_NAME.get(target)
        if allowed is None:
            return None, None
        return allowed, f"{phase}/proposals/{target}"
    return None, None


def split_proposal_path_errors(path: Path | None) -> list[str]:
    """Return VP-9 path errors for canonical split proposal files."""
    if path is None:
        return []
    parts = path.parts
    for idx, part in enumerate(parts):
        sm = re.fullmatch(r"sprint-v(\d+)", part)
        if not sm or idx + 3 >= len(parts):
            continue
        errors: list[str] = []
        sprint_n = sm.group(1)
        phase = parts[idx + 1]
        if phase not in VALID_PHASES or parts[idx + 2] != "proposals":
            continue

        rel_after_proposals = parts[idx + 3:]
        name = path.name
        expected_suffix = f"-v{sprint_n}.md"
        if not name.endswith(expected_suffix):
            errors.append(
                f"split proposal filename '{name}' must end with '{expected_suffix}' to match {part}",
            )

        if phase == "product" and rel_after_proposals[0] == "epics":
            if len(rel_after_proposals) != 2:
                errors.append(
                    "product epic proposal files must be directly under product/proposals/epics/",
                )
                return errors
            epic_re = re.compile(rf"^EP-\d{{3,}}-[a-z0-9](?:[a-z0-9-]*[a-z0-9])?-v{sprint_n}\.md$")
            if not epic_re.fullmatch(name):
                errors.append(
                    f"epic split proposal filename '{name}' must match EP-NNN-{{slug}}-v{sprint_n}.md with lowercase kebab slug",
                )
            return errors

        if len(rel_after_proposals) != 1:
            errors.append(
                f"unexpected nested split proposal path under {phase}/proposals/: {'/'.join(rel_after_proposals)}",
            )
            return errors

        target = re.sub(r"-v\d+\.md$", "", name)
        if target not in TARGET_NAMES_BY_PHASE.get(phase, set()):
            allowed = ", ".join(sorted(TARGET_NAMES_BY_PHASE.get(phase, set())))
            errors.append(
                f"unknown split proposal target '{target}' for phase '{phase}'; allowed targets: {allowed}",
            )
        return errors
    return []


def epic_id_from_split_proposal_path(path: Path | None) -> str | None:
    """Return EP-NNN from canonical product epic split proposal filename."""
    if path is None:
        return None
    parts = path.parts
    for idx, part in enumerate(parts):
        sm = re.fullmatch(r"sprint-v(\d+)", part)
        if not sm or idx + 4 >= len(parts):
            continue
        if parts[idx + 1] != "product" or parts[idx + 2] != "proposals" or parts[idx + 3] != "epics":
            continue
        m = re.fullmatch(rf"(EP-\d{{3,}})-[a-z0-9](?:[a-z0-9-]*[a-z0-9])?-v{sm.group(1)}\.md", path.name)
        if m:
            return m.group(1)
    return None


def project_root_from_source_path(path: Path | None) -> Path | None:
    """Infer project root from a path under `<root>/docs/sprint-vN/...`."""
    if path is None:
        return None
    parts = path.parts
    for idx, part in enumerate(parts):
        if part == "docs" and idx + 1 < len(parts) and re.fullmatch(r"sprint-v\d+", parts[idx + 1]):
            if idx == 0:
                return Path(".")
            return Path(*parts[:idx])
    return None


def validate_split_proposal_path(path: Path | None, report: Report) -> None:
    """VP-9: canonical split proposals must use known target filenames.

    This catches proposal-looking files that would otherwise validate by
    frontmatter phase but be skipped by discovery, e.g. `api-spec-v2.md`.
    """
    for error in split_proposal_path_errors(path):
        report.add_blocker("VP-9", error)


def validate_expected_phase(fm: dict, expected_phase: str | None, report: Report) -> None:
    if expected_phase is None or "phase" not in fm:
        return
    actual = fm.get("phase")
    if actual != expected_phase:
        report.add_blocker(
            "VP-7",
            f"frontmatter phase='{actual}' does not match canonical path/filename phase '{expected_phase}'",
        )


def validate_structure(body: str, report: Report) -> set[str]:
    """Return the set of recognized ## section names found."""
    found_sections: set[str] = set()
    for line in body.split("\n"):
        m = ANY_H2_RE.match(line)
        if not m:
            continue
        title = m.group(1).strip()
        if title in ("New", "Updated", "Removed"):
            found_sections.add(title)
        elif title in PROHIBITED_PROPOSAL_H2:
            report.add_blocker("VP-10", PROHIBITED_PROPOSAL_H2[title])
        elif title not in KNOWN_PROPOSAL_H2:
            report.add_blocker(
                "VP-2",
                f"unknown ## section '{title}' is not mergeable; every top-level section in a split proposal must be `## New`, `## Updated`, or `## Removed`, with mergeable content under anchored blocks",
            )
    if not found_sections:
        report.add_blocker(
            "VP-2", "proposal has no ## New / ## Updated / ## Removed section"
        )
    return found_sections


def validate_has_merge_items(
    prop_sections: dict[str, list[tuple[str, list[str]]]],
    report: Report,
) -> None:
    """VP-2: a mergeable proposal must contain at least one anchored operation.

    Keeping empty `## New` / `## Updated` / `## Removed` headings is useful inside
    templates, but an approved sprint proposal with zero anchored items would seal
    a no-op source and can make bootstrap-only Living Truth look like real output.
    """
    if any(items for items in prop_sections.values()):
        return
    report.add_blocker(
        "VP-2",
        "proposal has ## New / ## Updated / ## Removed sections but no anchored items to merge",
    )


def validate_anchors_and_headings(
    prop_sections: dict[str, list[tuple[str, list[str]]]],
    report: Report,
) -> set[str]:
    """Return the set of all anchor IDs declared in proposal (across all sections)."""
    all_ids: dict[str, str] = {}
    declared_ids: set[str] = set()
    for section_name, items in prop_sections.items():
        for aid, block_lines in items:
            declared_ids.add(aid)
            m = STRICT_ID_RE.match(aid)
            if not m:
                report.add_blocker(
                    "VP-3",
                    f"{section_name}/{aid}: ID does not match strict format `[A-Z]+(?:-[A-Z]+)*-NNN` (multi-segment OK; ≥3 digits, zero-padded)",
                )
            else:
                prefix = m.group(1)
                if prefix not in VALID_ID_PREFIXES:
                    report.add_warn(
                        "VP-3",
                        f"{section_name}/{aid}: prefix '{prefix}' not in standard set {VALID_ID_PREFIXES}",
                    )

            if aid in all_ids:
                report.add_blocker(
                    "VP-3",
                    f"DUPLICATE {aid}: appears in both {all_ids[aid]} and {section_name}",
                )
            else:
                all_ids[aid] = section_name

            # VP-4: Phase 9 — anchor is followed by 0+ optional routing-tag lines
            # (`<!-- EPIC: EP-XXX -->`, `<!-- US: US-XXX -->`, `<!-- VERIFIES: ID-XXX -->`),
            # then either an H3 heading (`### TITLE`) OR a bold-name line (`**ID — title**: ...`).
            # The bold-name form is used by epic-template (FR/AC inside epic file) per Phase 9
            # product-output-structure-discussion.md §4.
            heading_line_idx = _heading_line_index(block_lines)
            if heading_line_idx is None:
                report.add_blocker(
                    "VP-4",
                    f"{section_name}/{aid}: anchor must be followed by either H3 heading (`### TITLE`) or bold-name line (`**{aid} — title**: ...`); got block: {block_lines[:4]!r}",
                )
    return declared_ids


# Phase 9: accept either H3 heading OR bold-name line as the "title row" after an anchor + optional routing tags.
ROUTING_TAG_RE = re.compile(r"^<!--\s*(EPIC|US|VERIFIES):\s*\S+\s*-->\s*$")
EPIC_TAG_RE = re.compile(r"^<!--\s*EPIC:\s*(EP-\d+)\s*-->\s*$")
US_TAG_RE = re.compile(r"^<!--\s*US:\s*(US-\d+)\s*-->\s*$")
VERIFIES_TAG_RE = re.compile(r"^<!--\s*VERIFIES:\s*([A-Z]+(?:-[A-Z]+)*-\d+)\s*-->\s*$")
BOLD_NAME_RE = re.compile(r"^\*\*[A-Z]+(?:-[A-Z]+)*-\d+\b.*\*\*")
PHASE_ALLOWED_PREFIXES = {
    "product": {"EP", "FR", "US", "AC", "BR", "GLOSS", "PERSONA", "MR", "PRD-OVERVIEW"},
    "design": {"SCREEN", "DS-COMP", "DESIGN-OVERVIEW"},
    "architecture": {"ARCH", "ARCH-COMP", "NFR", "SEQ", "ENT", "ADR", "FLOW", "API", "EVT", "PR", "ARCH-OVERVIEW"},
    "testing": {"TC", "TEST-COVERAGE"},
}

# TEST-3b: TC titles in testing proposals should start with a trace + Technique
# prefix. Canonical PRISM IDs use `[US-NNN][AC-NNN][Technique]`; imported
# project aliases such as `[US-10.1][AC1][Technique]` are accepted to avoid
# churn when normalizing legacy/product-owned story labels.
# Current policy is warnings only; a future minor release will promote to blockers
# — see `core/phase-test.md` step 6.5.
TECHNIQUE_VALUES = (
    "Positive", "Negative", "BVA", "EP", "DT", "ST", "DD", "Security",
    "Regression", "Impact", "BasicFlow", "CornerCase", "Exploratory", "SIT",
    "Performance", "Accessibility",
)
TECHNIQUE_PATTERN = "|".join(TECHNIQUE_VALUES)
TECHNIQUE_TAG_PATTERN = rf"(?:{TECHNIQUE_PATTERN})(?:\+(?:{TECHNIQUE_PATTERN}))*"
US_TAG_PATTERN = r"US-(?:\d{3,}|\d+(?:\.\d+)*)(?:\+US-(?:\d{3,}|\d+(?:\.\d+)*))*"
AC_TAG_PATTERN = r"(?:AC-\d{3,}|AC\d+)(?:\+(?:AC-\d{3,}|AC\d+))*"
TITLE_TECHNIQUE_PREFIX_RE = re.compile(
    rf"^(?:"
    rf"\[{US_TAG_PATTERN}\]\[{AC_TAG_PATTERN}\]\[{TECHNIQUE_TAG_PATTERN}\]"
    rf"|\[NFR-[A-Za-z0-9_.-]+\]\[{TECHNIQUE_TAG_PATTERN}\]"
    rf"|\[FLOW-\d{{3,}}\]\[SIT\]"
    rf")(?=\s|$)"
)
TC_HEADING_RE = re.compile(r"^###\s+(TC-\d+):\s*(.+?)\s*$")


def _heading_line_index(block_lines: list[str]) -> int | None:
    """Find the title line (H3 or bold-name) after the anchor + optional routing tags.

    Returns the line index, or None if no title line is found among the first few lines.
    """
    for i in range(1, min(len(block_lines), TAG_SCAN_WINDOW)):
        line = block_lines[i].strip()
        if not line:
            continue
        if ROUTING_TAG_RE.match(line):
            continue
        if H3_RE.match(line):
            return i
        if BOLD_NAME_RE.match(line):
            return i
        # First non-anchor, non-tag, non-title line → fail
        return None
    return None


def _has_tag(block_lines: list[str], tag_re: re.Pattern) -> bool:
    for line in block_lines[1:TAG_SCAN_WINDOW]:
        s = line.strip()
        if not s:
            continue
        if tag_re.match(s):
            return True
        if s.startswith("<!--"):
            continue
        break
    return False


def _tag_value(block_lines: list[str], tag_re: re.Pattern) -> str | None:
    for line in block_lines[1:TAG_SCAN_WINDOW]:
        s = line.strip()
        if not s:
            continue
        m = tag_re.match(s)
        if m:
            # All current routing regexes have exactly one captured ID.
            return m.group(1) if m.groups() else None
        if s.startswith("<!--"):
            continue
        break
    return None


def validate_required_routing_tags(
    prop_sections: dict[str, list[tuple[str, list[str]]]],
    report: Report,
) -> None:
    """VP-6: fail fast when anchor routing would be ambiguous at seal time."""
    for section_name, items in prop_sections.items():
        for aid, block_lines in items:
            try:
                prefix = STRICT_ID_RE.match(aid).group(1)  # type: ignore[union-attr]
            except AttributeError:
                continue

            if prefix in ("FR", "US") and not _has_tag(block_lines, EPIC_TAG_RE):
                report.add_blocker(
                    "VP-6",
                    f"{section_name}/{aid}: FR/US items must include `<!-- EPIC: EP-NNN -->` routing tag",
                )
            elif prefix == "AC" and not _has_tag(block_lines, US_TAG_RE):
                report.add_blocker(
                    "VP-6",
                    f"{section_name}/{aid}: AC items must include `<!-- US: US-NNN -->` routing tag",
                )
            elif prefix == "TC" and not _has_tag(block_lines, VERIFIES_TAG_RE):
                report.add_blocker(
                    "VP-6",
                    f"{section_name}/{aid}: TC items must include `<!-- VERIFIES: ID-NNN -->` trace tag",
                )


def validate_phase_prefix_ownership(
    phase: str | None,
    prop_sections: dict[str, list[tuple[str, list[str]]]],
    report: Report,
) -> None:
    """VP-7: prevent a phase proposal from mutating another phase's LT files."""
    if phase not in PHASE_ALLOWED_PREFIXES:
        return
    allowed = PHASE_ALLOWED_PREFIXES[phase]
    for section_name, items in prop_sections.items():
        for aid, _block_lines in items:
            m = STRICT_ID_RE.match(aid)
            if not m:
                continue
            prefix = m.group(1)
            if prefix not in allowed:
                report.add_blocker(
                    "VP-7",
                    f"{section_name}/{aid}: prefix '{prefix}' is not allowed in phase '{phase}' proposal; allowed prefixes: {', '.join(sorted(allowed))}",
                )


def validate_target_prefix_ownership(
    expected_target_prefixes: set[str] | None,
    target_label: str | None,
    prop_sections: dict[str, list[tuple[str, list[str]]]],
    report: Report,
) -> None:
    """VP-8: canonical split proposal files must stay scoped to one LT target."""
    if not expected_target_prefixes:
        return
    for section_name, items in prop_sections.items():
        for aid, _block_lines in items:
            m = STRICT_ID_RE.match(aid)
            if not m:
                continue
            prefix = m.group(1)
            if prefix not in expected_target_prefixes:
                report.add_blocker(
                    "VP-8",
                    f"{section_name}/{aid}: prefix '{prefix}' does not belong in split proposal target '{target_label}'; allowed prefixes: {', '.join(sorted(expected_target_prefixes))}",
                )


def discover_living_us_to_epic(project_root: Path | None) -> dict[str, str]:
    """Return {US-NNN: EP-NNN} from existing Living Truth epic files."""
    if project_root is None:
        return {}
    epics_dir = project_root / "docs" / "product" / "epics"
    if not epics_dir.is_dir():
        return {}
    out: dict[str, str] = {}
    for epic_file in sorted(epics_dir.glob("EP-*-*.md")):
        m = re.fullmatch(r"(EP-\d+)-[a-z0-9-]+\.md", epic_file.name)
        if not m:
            continue
        epic_id = m.group(1)
        try:
            _preamble, blocks = parse_anchored_blocks(epic_file.read_text(encoding="utf-8"))
        except OSError:
            continue
        for aid, _block_lines in blocks:
            mid = STRICT_ID_RE.match(aid)
            if mid and mid.group(1) == "US":
                out[aid] = epic_id
    return out


def validate_epic_split_content_ownership(
    source_path: Path | None,
    prop_sections: dict[str, list[tuple[str, list[str]]]],
    report: Report,
) -> None:
    """VP-10: an epic split proposal must only mutate the epic named by its file.

    Filename shape alone is not enough: `EP-001-checkout-v2.md` must not contain
    `EP-002` or route FR/US/AC items to another epic.
    """
    expected_epic = epic_id_from_split_proposal_path(source_path)
    if expected_epic is None:
        return

    proposal_us_to_epic: dict[str, str] = {}
    for items in prop_sections.values():
        for aid, block_lines in items:
            m = STRICT_ID_RE.match(aid)
            if not m or m.group(1) != "US":
                continue
            epic_tag = _tag_value(block_lines, EPIC_TAG_RE)
            if epic_tag:
                proposal_us_to_epic[aid] = epic_tag

    living_us_to_epic = discover_living_us_to_epic(project_root_from_source_path(source_path))

    for section_name, items in prop_sections.items():
        for aid, block_lines in items:
            m = STRICT_ID_RE.match(aid)
            if not m:
                continue
            prefix = m.group(1)
            if prefix == "EP" and aid != expected_epic:
                report.add_blocker(
                    "VP-10",
                    f"{section_name}/{aid}: epic proposal filename owns '{expected_epic}' but contains EP anchor '{aid}'",
                )
            elif prefix in ("FR", "US"):
                epic_tag = _tag_value(block_lines, EPIC_TAG_RE)
                if epic_tag and epic_tag != expected_epic:
                    report.add_blocker(
                        "VP-10",
                        f"{section_name}/{aid}: epic proposal filename owns '{expected_epic}' but routes to '{epic_tag}'",
                    )
            elif prefix == "AC":
                explicit_epic_tag = _tag_value(block_lines, EPIC_TAG_RE)
                if explicit_epic_tag and explicit_epic_tag != expected_epic:
                    report.add_blocker(
                        "VP-10",
                        f"{section_name}/{aid}: epic proposal filename owns '{expected_epic}' but AC routes to '{explicit_epic_tag}'",
                    )
                    continue
                us_tag = _tag_value(block_lines, US_TAG_RE)
                if not us_tag:
                    continue
                owning_epic = proposal_us_to_epic.get(us_tag) or living_us_to_epic.get(us_tag)
                if owning_epic and owning_epic != expected_epic:
                    report.add_blocker(
                        "VP-10",
                        f"{section_name}/{aid}: epic proposal filename owns '{expected_epic}' but target US '{us_tag}' belongs to '{owning_epic}'",
                    )


def validate_traces_against_living(
    body: str,
    living_text: str,
    proposal_declared_ids: set[str],
    report: Report,
) -> None:
    """VP-5: each **Trace**: ID, ID2, ... should resolve to either:
      (a) an existing anchor in living truth, or
      (b) an ID declared in this same proposal (typically as NEW or UPDATED).

    Warn-level: stale traces in legacy areas are common; not a hard blocker.
    """
    _, living_blocks = parse_anchored_blocks(living_text)
    known_ids = {aid for aid, _ in living_blocks} | proposal_declared_ids
    for raw in TRACE_RE.finditer(body):
        refs = [r.strip() for r in raw.group(1).split(",")]
        for r in refs:
            r = re.split(r"\s*\(", r, 1)[0].strip()
            if not r:
                continue
            if not STRICT_ID_RE.match(r):
                report.add_warn(
                    "VP-5", f"trace reference '{r}' is not a valid stable ID format"
                )
                continue
            if r not in known_ids:
                report.add_warn(
                    "VP-5",
                    f"trace reference '{r}' does not resolve in living truth or in this proposal's declared IDs",
                )


def validate_testing_technique_tags(
    prop_sections: dict[str, list[tuple[str, list[str]]]],
    phase: str | None,
    report: Report,
) -> None:
    """TEST-3b (warning-only): every TC heading in a testing proposal SHOULD
    start with a trace + Technique prefix per `core/templates/test-cases-template.md §1`.

    Current policy emits warnings only so existing testing proposals are not retroactively
    broken. A future minor release will promote these to blockers per `core/phase-test.md`
    step 6.5.
    """
    if phase != "testing":
        return
    for section_name, items in prop_sections.items():
        for aid, block_lines in items:
            if not aid.startswith("TC-"):
                continue
            heading_idx = _heading_line_index(block_lines)
            if heading_idx is None:
                continue
            heading = block_lines[heading_idx].strip()
            m = TC_HEADING_RE.match(heading)
            if not m:
                continue
            title_after_id = m.group(2)
            if TITLE_TECHNIQUE_PREFIX_RE.match(title_after_id):
                continue
            report.add_warn(
                "TEST-3b",
                f"{section_name}/{aid}: TC title is missing a valid trace + Technique prefix. "
                f"Recommended fix: start the title with `[US-NNN][AC-NNN][Technique]` "
                f"(functional), `[NFR-NNN][Technique]` (NFR), or `[FLOW-NNN][SIT]` "
                f"(SIT flow). Imported aliases like `[US-10.1][AC1][BVA]` are accepted. "
                f"Technique ∈ {{{', '.join(TECHNIQUE_VALUES)}}}; combine with `+` for "
                f"multi-technique (e.g. `[BVA+Negative]`). See "
                f"`core/templates/test-cases-template.md §1 Conventions` and "
                f"`core/standards/testing-standards.md §1.5` for rules. "
                f"A future minor release will promote this warning to a blocker."
            )


# VP-11: catalog prefixes that are enumerated by a coverage/traceability table living *inside*
# a singleton `*-OVERVIEW-001` narrative block — ARCH-COMP in the ARCH-OVERVIEW §3b Traceability
# Map + Component View, SCREEN in the DESIGN-OVERVIEW §2 Screen Inventory. Adding such an item
# means that table must be re-authored in the same proposal or it silently drifts.
# Deliberately excluded: plain ARCH (architecture decisions, no per-item overview table), DS-COMP
# (§8 specs are separate anchored items), and BR (standalone items with their own **Trace**;
# product FR coverage is enforced by the per-epic Product Traceability Map + LTV-COV instead).
OVERVIEW_SYNC_TRIGGERS = {
    "ARCH-OVERVIEW": {"ARCH-COMP"},
    "DESIGN-OVERVIEW": {"SCREEN"},
}
PREAMBLE_TABLE_RE = re.compile(r"^\s*\|.*\|\s*$")


def _prefix_of(aid: str) -> str | None:
    m = STRICT_ID_RE.match(aid)
    return m.group(1) if m else None


def validate_overview_sync(
    prop_sections: dict[str, list[tuple[str, list[str]]]],
    report: Report,
) -> None:
    """VP-11: when a proposal ADDs catalog items (components/screens/rules), the singleton
    `*-OVERVIEW-001` block that summarizes and traces them must be (re-)authored in the same
    proposal's `## New` or `## Updated`. Otherwise the items merge but the narrative +
    traceability map that must cover them silently drift — and the map cannot be smuggled in
    as preamble prose (that is dropped at seal; see VP-12)."""
    new_prefixes = {p for p in (_prefix_of(a) for a, _ in prop_sections.get("New", [])) if p}
    touched_overviews = {
        p
        for sec in ("New", "Updated")
        for p in (_prefix_of(a) for a, _ in prop_sections.get(sec, []))
        if p
    }
    for overview_prefix, triggers in OVERVIEW_SYNC_TRIGGERS.items():
        hit = new_prefixes & triggers
        if hit and overview_prefix not in touched_overviews:
            report.add_blocker(
                "VP-11",
                f"proposal adds {sorted(hit)} item(s) but has no `## New`/`## Updated` "
                f"{overview_prefix}-001 block; re-author that overview (narrative + "
                f"traceability map) in the same proposal so it covers the new items — "
                f"content placed outside an anchored New/Updated block is dropped at seal",
            )


def validate_preamble_has_no_content(body: str, report: Report) -> None:
    """VP-12: a markdown table before the first `## New`/`## Updated`/`## Removed` is dropped
    at seal (the merge keeps only anchored blocks + the living preamble). A table there is the
    signature of misplaced mergeable content — e.g. a hand-written 'Traceability Map' addendum
    that was meant to update the overview. Flag it so it is moved into an anchored block.
    Narrative headings are allowed (change-pack deltas legitimately carry Rationale / Downstream
    Impact / Acceptance preamble sections). HTML comments and fenced code are ignored."""
    fence_open = False
    in_comment = False
    for raw in body.split("\n"):
        line = raw.rstrip()
        stripped = line.strip()
        if in_comment:
            if "-->" in stripped:
                in_comment = False
            continue
        if fence_open:
            if CODE_FENCE_RE.match(line):
                fence_open = False
            continue
        m = ANY_H2_RE.match(line)
        if m and m.group(1).strip() in KNOWN_PROPOSAL_H2:
            return  # reached the first mergeable section — preamble ends
        if stripped.startswith("<!--"):
            if "-->" not in stripped:
                in_comment = True
            continue
        if CODE_FENCE_RE.match(line):
            fence_open = True
            continue
        if PREAMBLE_TABLE_RE.match(line):
            report.add_blocker(
                "VP-12",
                f"preamble table before the first mergeable section is dropped at seal: "
                f"{stripped!r}; move the table into an anchored New/Updated block",
            )
            return


def validate(
    proposal_text: str,
    living_text: str | None = None,
    expected_phase: str | None = None,
    expected_target_prefixes: set[str] | None = None,
    target_label: str | None = None,
    source_path: Path | None = None,
) -> Report:
    report = Report()
    try:
        fm, body = parse_frontmatter(proposal_text)
    except ValueError as e:
        report.add_blocker("VP-1", str(e))
        return report
    validate_split_proposal_path(source_path, report)
    validate_frontmatter(fm, report)
    validate_expected_phase(fm, expected_phase, report)
    validate_structure(body, report)
    validate_preamble_has_no_content(body, report)
    prop_sections = split_proposal_sections(body)
    validate_has_merge_items(prop_sections, report)
    validate_overview_sync(prop_sections, report)
    declared_ids = validate_anchors_and_headings(prop_sections, report)
    validate_required_routing_tags(prop_sections, report)
    phase = fm.get("phase") if isinstance(fm, dict) else None
    validate_phase_prefix_ownership(phase if isinstance(phase, str) else None, prop_sections, report)
    validate_target_prefix_ownership(expected_target_prefixes, target_label, prop_sections, report)
    validate_epic_split_content_ownership(source_path, prop_sections, report)
    validate_testing_technique_tags(prop_sections, phase if isinstance(phase, str) else None, report)
    if living_text is not None:
        validate_traces_against_living(body, living_text, declared_ids, report)
    return report


def format_report(report: Report, strict: bool) -> tuple[int, str]:
    lines: list[str] = []
    if not report.findings:
        lines.append("✓ proposal validates (no findings)")
    else:
        for f in report.findings:
            symbol = "✗" if f.level == "blocker" else "⚠"
            lines.append(f"{symbol} {f.level} [{f.rule}]: {f.message}")
        lines.append("")
        lines.append(
            f"summary: {len(report.blockers)} blocker(s), {len(report.warnings)} warning(s)"
        )
    code = 1 if report.blockers else 0
    if strict and report.warnings:
        code = 1
    return code, "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate a sprint proposal markdown file for structural correctness.",
    )
    parser.add_argument("--file", required=True, help="Path to proposal markdown")
    parser.add_argument(
        "--against-living",
        help="Optional path to living-truth markdown to resolve Trace IDs",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Treat warnings as blockers (exit 1 if any warning)",
    )
    args = parser.parse_args()

    path = Path(args.file)
    if not path.is_file():
        sys.stderr.write(f"ERROR: file not found: {path}\n")
        return 2

    living_text: str | None = None
    if args.against_living:
        living_path = Path(args.against_living)
        if not living_path.is_file():
            sys.stderr.write(f"ERROR: living truth not found: {living_path}\n")
            return 2
        living_text = living_path.read_text(encoding="utf-8")

    text = path.read_text(encoding="utf-8")
    expected_phase = infer_expected_phase_from_path(path)
    expected_target_prefixes, target_label = infer_expected_target_prefixes_from_path(path)
    report = validate(
        text,
        living_text=living_text,
        expected_phase=expected_phase,
        expected_target_prefixes=expected_target_prefixes,
        target_label=target_label,
        source_path=path,
    )
    code, output = format_report(report, strict=args.strict)
    print(output)
    return code


if __name__ == "__main__":
    sys.exit(main())
