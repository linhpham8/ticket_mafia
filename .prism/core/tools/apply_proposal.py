#!/usr/bin/env python3
"""apply_proposal.py — Phase 2 production (extended Phase 9).

Anchor-based deterministic merge of a sprint proposal into a living-truth
markdown file. Three operations:

  New      append the proposed section block at the end of living truth
  Updated  replace the existing section that shares the same anchor
  Removed  delete the existing section that shares the same anchor (proposal
           body for Removed entries is human-review metadata only — script
           uses just the anchor ID to identify what to delete)

Anchor convention: HTML comment `<!-- ID: PREFIX-NNN -->` (single anchor, no
closing tag) on its own line immediately above an H3 heading. Section boundary
runs from one anchor to the next anchor (exclusive) or to EOF.

Phase 9: anchor regex now supports MULTI-SEGMENT prefixes (`DS-COMP-001`,
`ARCH-COMP-001`). The PREFIX-only portion drives routing to the correct
Living Truth file via `ANCHOR_PREFIX_TO_LT`. Routing tags `<!-- EPIC: EP-XXX -->`,
`<!-- US: US-XXX -->`, `<!-- VERIFIES: ID-XXX -->` may follow the ID anchor on the next line.

Approach A (confirmed in Phase 1 spike findings): the content under each
`### TITLE` heading in the proposal's `Updated` section IS the new section
content that goes into living truth verbatim. Before/After/Reason/Impact
narrative does NOT live in the proposal; it belongs in the PR description
or change-pack `change-request.md`.

CLI (per discussion doc §9.C):
  Explicit paths:
    apply_proposal.py --proposal PATH --living PATH [--dry-run] [--verbose]
For full sprint seal semantics (v1 root LT bootstrap, all proposals/deltas,
snapshots, config stamping, drift scan), prefer `seal_sprint.py`.

Exit codes (per §9.C):
  0  OK
  1  validation fail (anchor conflict, duplicate ID, NEW already exists,
     UPDATED/REMOVED missing in living truth, malformed proposal body)
  2  file not found
  3  config error (missing/malformed YAML frontmatter, unresolved convention)
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

import yaml


# Phase 9: regex now matches multi-segment prefixes (DS-COMP-001, ARCH-COMP-001).
ANCHOR_RE = re.compile(r"^<!--\s*ID:\s*([A-Z]+(?:-[A-Z]+)*-\d+)\s*-->\s*$")
# Routing tags that appear on the line(s) following the ID anchor.
EPIC_TAG_RE = re.compile(r"^<!--\s*EPIC:\s*(EP-\d+)\s*-->\s*$")
US_TAG_RE = re.compile(r"^<!--\s*US:\s*(US-\d+)\s*-->\s*$")
VERIFIES_TAG_RE = re.compile(r"^<!--\s*VERIFIES:\s*([A-Z]+(?:-[A-Z]+)*-\d+)\s*-->\s*$")
FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---\n", re.DOTALL)
H2_RE = re.compile(r"^##\s+(\w+)\s*$")
CODE_FENCE_RE = re.compile(r"^(```+|~~~+)")
PROPOSAL_SECTIONS = ("New", "Updated", "Removed")

# Routing tags and the title line must appear within the first `TAG_SCAN_WINDOW`
# lines of a block (i.e. `block_lines[1:TAG_SCAN_WINDOW]`, after the anchor at
# index 0). Shared by apply + validate so the two parsers can't drift on the
# scan width — a tag the validator accepts but apply ignores would route wrong.
TAG_SCAN_WINDOW = 6

# Phase 9 routing: ID prefix → relative LT path under /docs/.
# Special cases:
#   - EP-NNN: file-level — creates/updates `product/epics/EP-NNN-{slug}.md`. Slug derives
#     from heading text. Handled separately by `derive_lt_for_anchor`.
#   - FR-NNN, US-NNN: route by `<!-- EPIC: EP-XXX -->` tag → `product/epics/EP-XXX-{slug}.md`.
#   - AC-NNN: route by `<!-- US: US-XXX -->` tag → AC block inside the US section in epic file.
ANCHOR_PREFIX_TO_LT: dict[str, str] = {
    "BR": "product/prd.md",
    # Phase-overview narrative blocks — singleton per file (always `-001`). Authored as
    # `## New` in sprint 1, `## Updated` in later sprints (replace-in-place; the ID never
    # changes, so cross-doc/code references stay stable). See `core/phase-*.md`.
    "PRD-OVERVIEW": "product/prd.md",
    "ARCH-OVERVIEW": "architecture/architecture.md",
    "DESIGN-OVERVIEW": "design/design-system.md",
    "GLOSS": "product/glossary.md",
    "PERSONA": "product/personas.md",
    "MR": "product/market-research.md",
    "SCREEN": "design/design-system.md",
    "DS-COMP": "design/design-system.md",
    "ARCH": "architecture/architecture.md",
    "ARCH-COMP": "architecture/architecture.md",
    "NFR": "architecture/nfr.md",
    "SEQ": "architecture/sequence.md",
    "ENT": "architecture/erd.md",
    "ADR": "architecture/adr.md",
    "FLOW": "architecture/data-flow.md",
    "API": "architecture/api-specs.md",
    "EVT": "architecture/events.md",
    "PR": "architecture/project-reference.md",
    "TC": "testing/test-cases.md",
    # Rule / Branch Inventory — singleton coverage block per file (always `-001`), authored
    # `## New` in sprint 1, `## Updated` (replace-in-place, cumulative) later — same singleton
    # pattern as `*-OVERVIEW`. Promotes the per-AC/BR/branch → TC coverage map into Living Truth.
    "TEST-COVERAGE": "testing/test-cases.md",
}

PHASES = ("product", "design", "architecture", "testing")


def split_anchor_id(anchor_id: str) -> tuple[str, int]:
    """Split a multi-segment anchor ID into (prefix, number).
    `FR-001` → ("FR", 1). `DS-COMP-014` → ("DS-COMP", 14). `ARCH-COMP-007` → ("ARCH-COMP", 7).
    """
    m = re.match(r"^([A-Z]+(?:-[A-Z]+)*)-(\d+)$", anchor_id)
    if not m:
        raise ValueError(f"malformed anchor ID: {anchor_id!r}")
    return m.group(1), int(m.group(2))


def slug_from_title(title: str, max_len: int = 40) -> str:
    """Derive a kebab-case slug from a heading title.

    Phase 9 rules: strip Vietnamese diacritics, lowercase, alnum + hyphen only, max 40 chars.
    `"Checkout Flow"` → `"checkout-flow"`. `"Thanh toán"` → `"thanh-toan"`.
    """
    import unicodedata
    nfkd = unicodedata.normalize("NFKD", title)
    no_diacritics = "".join(c for c in nfkd if not unicodedata.combining(c))
    # Common Vietnamese specials not handled by NFKD strip
    no_diacritics = no_diacritics.replace("đ", "d").replace("Đ", "D")
    lower = no_diacritics.lower()
    # Replace non-alnum with hyphens, collapse runs, trim
    s = re.sub(r"[^a-z0-9]+", "-", lower).strip("-")
    if len(s) > max_len:
        s = s[:max_len].rstrip("-")
    return s or "untitled"


def derive_lt_for_anchor(
    anchor_id: str,
    epic_tag: str | None,
    project_root: Path,
    epic_slug_lookup: dict[str, str] | None = None,
    us_to_epic: dict[str, str] | None = None,
    us_tag: str | None = None,
) -> Path | None:
    """Map an anchor (and optional routing tag) to a Living Truth file path.

    Routing rules (Phase 9):
    - EP-NNN: builds `product/epics/EP-NNN-{slug}.md`. Slug from `epic_slug_lookup`.
    - FR/US/AC + epic_tag (`<!-- EPIC: EP-XXX -->`): routes inside that epic's file.
    - AC + us_tag (`<!-- US: US-XXX -->`): looks up US-XXX's epic via `us_to_epic` map,
      then routes inside that epic's file. (AC items live inside US blocks of epic files.)
    - Other prefixes: ANCHOR_PREFIX_TO_LT lookup.

    Returns None if no routing applies.
    """
    prefix, _num = split_anchor_id(anchor_id)
    if prefix == "EP":
        slug = (epic_slug_lookup or {}).get(anchor_id, "untitled")
        return project_root / "docs" / "product" / "epics" / f"{anchor_id}-{slug}.md"
    if prefix in ("FR", "US", "AC") and epic_tag:
        slug = (epic_slug_lookup or {}).get(epic_tag, "untitled")
        return project_root / "docs" / "product" / "epics" / f"{epic_tag}-{slug}.md"
    if prefix == "AC" and us_tag and us_to_epic and us_tag in us_to_epic:
        # AC routes through US tag: look up which epic owns US-XXX
        owning_epic = us_to_epic[us_tag]
        slug = (epic_slug_lookup or {}).get(owning_epic, "untitled")
        return project_root / "docs" / "product" / "epics" / f"{owning_epic}-{slug}.md"
    rel = ANCHOR_PREFIX_TO_LT.get(prefix)
    if rel is None:
        return None
    return project_root / "docs" / rel


def _normalize_line_endings(text: str) -> str:
    """Normalize CRLF / CR line endings to LF. Tools accept files authored on
    any platform; downstream parsing assumes LF only."""
    return text.replace("\r\n", "\n").replace("\r", "\n")


def parse_frontmatter(text: str) -> tuple[dict, str]:
    """Return (frontmatter_dict, remaining_body). Uses PyYAML for robust parsing.

    Returns ({}, text) if no frontmatter present. Raises ValueError on malformed YAML.
    """
    text = _normalize_line_endings(text)
    m = FRONTMATTER_RE.match(text)
    if not m:
        return {}, text
    fm_text = m.group(1)
    try:
        data = yaml.safe_load(fm_text)
    except yaml.YAMLError as e:
        raise ValueError(f"malformed YAML frontmatter: {e}") from e
    if data is None:
        data = {}
    if not isinstance(data, dict):
        raise ValueError("YAML frontmatter is not a mapping")
    return data, text[m.end():]


def _anchor_positions(lines: list[str]) -> list[int]:
    """Return line indices of anchors, skipping content inside fenced code blocks."""
    positions: list[int] = []
    fence: str | None = None  # open fence delimiter ('`' or '~'), or None when outside a fence
    for i, line in enumerate(lines):
        fence_m = CODE_FENCE_RE.match(line)
        if fence_m:
            delim = fence_m.group(1)[0]
            if fence is None:
                fence = delim
            elif fence == delim:  # same delimiter closes; a different one inside is content
                fence = None
            continue
        if fence is not None:
            continue
        if ANCHOR_RE.match(line):
            positions.append(i)
    return positions


def parse_anchored_blocks(text: str) -> tuple[str, list[tuple[str, list[str]]]]:
    """Split markdown into (preamble, [(anchor_id, block_lines), ...]).

    preamble = everything before the first anchor, rstripped of trailing blanks.
    Each block_lines = anchor line + content up to (but not including) the next
    anchor, with trailing blank lines stripped. Anchors inside fenced code
    blocks are ignored (production hardening over the spike).

    CRLF / CR inputs are normalized to LF before parsing; output is always LF.
    """
    text = _normalize_line_endings(text)
    lines = text.split("\n")
    anchor_positions = _anchor_positions(lines)

    if not anchor_positions:
        return text.rstrip("\n"), []

    preamble = "\n".join(lines[: anchor_positions[0]]).rstrip("\n")

    blocks: list[tuple[str, list[str]]] = []
    for idx, start in enumerate(anchor_positions):
        end = anchor_positions[idx + 1] if idx + 1 < len(anchor_positions) else len(lines)
        block_lines = lines[start:end]
        while block_lines and block_lines[-1].strip() == "":
            block_lines.pop()
        m = ANCHOR_RE.match(block_lines[0])
        assert m is not None
        blocks.append((m.group(1), block_lines))

    return preamble, blocks


def split_proposal_sections(body: str) -> dict[str, list[tuple[str, list[str]]]]:
    """Return {section_name: [(anchor_id, block_lines), ...]} for New/Updated/Removed."""
    lines = body.split("\n")
    section_starts: dict[str, int] = {}
    fence: str | None = None  # open fence delimiter ('`' or '~'), or None when outside a fence
    for i, line in enumerate(lines):
        fence_m = CODE_FENCE_RE.match(line)
        if fence_m:
            delim = fence_m.group(1)[0]
            if fence is None:
                fence = delim
            elif fence == delim:
                fence = None
            continue
        if fence is not None:
            continue
        m = H2_RE.match(line)
        if m and m.group(1) in PROPOSAL_SECTIONS:
            section_starts[m.group(1)] = i

    sorted_starts = sorted(section_starts.items(), key=lambda kv: kv[1])

    sections: dict[str, list[tuple[str, list[str]]]] = {}
    for idx, (name, start) in enumerate(sorted_starts):
        end = sorted_starts[idx + 1][1] if idx + 1 < len(sorted_starts) else len(lines)
        body_text = "\n".join(lines[start + 1:end])
        _, blocks = parse_anchored_blocks(body_text)
        cleaned: list[tuple[str, list[str]]] = []
        for aid, block_lines in blocks:
            while block_lines and block_lines[-1].strip() in ("", "---"):
                block_lines.pop()
            cleaned.append((aid, block_lines))
        sections[name] = cleaned

    return sections


def serialize(preamble: str, blocks: list[tuple[str, list[str]]]) -> str:
    """Reconstruct markdown: preamble + one blank line + section blocks separated
    by one blank line each, terminating with a single trailing newline."""
    parts: list[str] = []
    if preamble:
        parts.append(preamble)
    for _aid, block_lines in blocks:
        parts.append("\n".join(block_lines))
    text = "\n\n".join(parts)
    if not text.endswith("\n"):
        text += "\n"
    return text


def apply(proposal_text: str, living_text: str, verbose: bool = False) -> tuple[int, str]:
    """Return (exit_code, result_text_or_error_message)."""
    try:
        _fm, body = parse_frontmatter(proposal_text)
    except ValueError as e:
        return 3, str(e)

    prop_sections = split_proposal_sections(body)
    new_items = prop_sections.get("New", [])
    updated_items = prop_sections.get("Updated", [])
    removed_items = prop_sections.get("Removed", [])
    if not (new_items or updated_items or removed_items):
        return 1, "proposal has no anchored items to merge"

    preamble, living_blocks = parse_anchored_blocks(living_text)
    living_ids = {aid for aid, _ in living_blocks}

    if verbose:
        sys.stderr.write(f"living anchors: {sorted(living_ids)}\n")
        sys.stderr.write(
            f"ops: New={[a for a, _ in new_items]} "
            f"Updated={[a for a, _ in updated_items]} "
            f"Removed={[a for a, _ in removed_items]}\n"
        )

    errors: list[str] = []
    seen_in_proposal: dict[str, str] = {}
    for section_name, items in (("NEW", new_items), ("UPDATED", updated_items), ("REMOVED", removed_items)):
        for aid, _ in items:
            if aid in seen_in_proposal:
                errors.append(
                    f"DUPLICATE {aid}: appears in both {seen_in_proposal[aid]} and {section_name}"
                )
            else:
                seen_in_proposal[aid] = section_name
    for aid, _ in new_items:
        if aid in living_ids:
            errors.append(f"NEW {aid}: already exists in living truth")
    for aid, _ in updated_items:
        if aid not in living_ids:
            errors.append(f"UPDATED {aid}: not found in living truth")
    for aid, _ in removed_items:
        if aid not in living_ids:
            errors.append(f"REMOVED {aid}: not found in living truth")
    if errors:
        return 1, "\n".join(errors)

    removed_ids = {aid for aid, _ in removed_items}
    living_blocks = [(aid, lines) for aid, lines in living_blocks if aid not in removed_ids]

    updated_map = {aid: lines for aid, lines in updated_items}
    living_blocks = [
        (aid, updated_map[aid] if aid in updated_map else lines)
        for aid, lines in living_blocks
    ]

    living_blocks.extend(new_items)

    return 0, serialize(preamble, living_blocks)


def find_project_root(start: Path) -> Path | None:
    """Walk up from `start` looking for prism-config.md to identify project root."""
    p = start.resolve()
    for parent in [p] + list(p.parents):
        if (parent / "prism-config.md").is_file():
            return parent
    return None


# ----------------------------------------------------------------------------
# Phase 9 — multi-target routing helpers
# ----------------------------------------------------------------------------

# `\d{3,}` = the canonical zero-padded epic number every creator emits
# (get_next_id `{:03d}`, migrate `zfill(3)`); kept identical to precommit's matcher.
EPIC_FILE_RE = re.compile(r"^EP-(\d{3,})-([a-z0-9-]+)\.md$")
H3_HEADING_RE = re.compile(r"^###\s+(.+?)\s*$")
# A title line may repeat its own ID before the human title, with a `—`/`:`/`-`
# OR a plain whitespace separator. `validate.BOLD_NAME_RE` / `H3_RE` accept all of
# these, so the extractor must strip the same set — otherwise the lenient space
# form (`**EP-NNN Title**`) validates but yields an `untitled` slug + empty Index
# title, and `### EP-NNN Title` leaks the ID into the slug.
TITLE_ID_PREFIX_RE = re.compile(r"^[A-Z]+(?:-[A-Z]+)*-\d+\s*(?:[—:\-]\s*)?")
# The validator's bold-name title shape (mirrors validate.BOLD_NAME_RE) with the
# inner text captured non-greedily up to the first closing `**`.
BOLD_TITLE_RE = re.compile(r"^\*\*([A-Z]+(?:-[A-Z]+)*-\d+\b.*?)\*\*")


def discover_existing_epic_slugs(
    project_root: Path,
    current_state: dict[Path, str] | None = None,
) -> dict[str, str]:
    """Scan disk and in-memory epic files and return {EP-NNN: slug}.

    Used so that FR / US / AC items routed by `<!-- EPIC: EP-XXX -->` tag can resolve
    to the existing file even if the proposal doesn't redeclare the epic's slug.
    """
    out: dict[str, str] = {}

    def add_if_epic_file(path: Path) -> None:
        m = EPIC_FILE_RE.match(path.name)
        if m:
            out[f"EP-{m.group(1)}"] = m.group(2)

    epics_dir = project_root / "docs" / "product" / "epics"
    if not epics_dir.is_dir():
        pass
    else:
        for f in epics_dir.iterdir():
            if f.is_file():
                add_if_epic_file(f)

    for path in (current_state or {}):
        add_if_epic_file(path)

    return out


def discover_us_to_epic(
    project_root: Path,
    current_state: dict[Path, str] | None = None,
) -> dict[str, str]:
    """Return {US-NNN: EP-NNN} by scanning existing and in-memory epic files.

    `current_state` lets callers route AC items against epic/user-story content
    merged earlier in the same atomic seal/effective-truth composition.
    """
    out: dict[str, str] = {}

    def scan(epic_path: Path, text: str) -> None:
        m = EPIC_FILE_RE.match(epic_path.name)
        if not m:
            return
        epic_id = f"EP-{m.group(1)}"
        _preamble, blocks = parse_anchored_blocks(text)
        for aid, _block_lines in blocks:
            try:
                prefix, _num = split_anchor_id(aid)
            except ValueError:
                continue
            if prefix == "US":
                out[aid] = epic_id

    epics_dir = project_root / "docs" / "product" / "epics"
    if epics_dir.is_dir():
        for f in epics_dir.iterdir():
            if f.is_file():
                scan(f, f.read_text(encoding="utf-8"))

    for path, text in (current_state or {}).items():
        scan(path, text)

    return out


def extract_routing_tag(block_lines: list[str], tag_re: re.Pattern) -> str | None:
    """Find the first routing tag in `block_lines` matching `tag_re`. Returns the tagged ID or None."""
    for line in block_lines[1:TAG_SCAN_WINDOW]:  # tags appear shortly after the anchor
        m = tag_re.match(line.strip())
        if m:
            return m.group(1)
        if line.strip() and not line.strip().startswith("<!--"):
            # First non-comment line — tags must precede content
            break
    return None


def _title_after_id(heading: str) -> str | None:
    """Strip a leading `ID-NNN` + optional `—`/`:`/`-`/whitespace separator from a
    title heading. Returns the remaining human title; the heading unchanged when it
    carries no ID prefix; or None when nothing remains (a bare `EP-NNN` with no title).
    """
    stripped = TITLE_ID_PREFIX_RE.sub("", heading, count=1).strip()
    if stripped == heading.strip():  # no ID prefix was present
        return heading.strip() or None
    return stripped or None


def extract_title_from_block(block_lines: list[str]) -> str | None:
    """Find the title text from a block. Accepts H3 (`### EP-NNN: Title`) or
    bold-name (`**EP-NNN — Title**`). The block's own ID prefix + an optional
    `—`/`:`/`-` OR whitespace separator is stripped (so the lenient space form the
    validator also accepts yields the real title, never `untitled`). Returns the
    title text, or None when there is none (e.g. a bare `**EP-NNN**`).
    """
    for line in block_lines[1:TAG_SCAN_WINDOW]:
        s = line.strip()
        if not s or s.startswith("<!--"):
            continue
        m = H3_HEADING_RE.match(s)
        if m:
            return _title_after_id(m.group(1))
        bm = BOLD_TITLE_RE.match(s)
        if bm:
            return _title_after_id(bm.group(1).strip())
        break
    return None


def scaffold_epic_file(target: Path, epic_id: str, slug: str, project_name: str) -> str:
    """Return MINIMAL initial content for a new epic file — frontmatter only.

    The merge phase (apply_multi_target) supplies the EP-NNN anchor + body from the
    proposal's `## New` section, so the scaffold MUST NOT include any pre-anchored
    content (it would conflict with the merge as "NEW already exists in living truth").

    The template's full structure (Epic Overview, FRs, User Stories sections) becomes
    the canonical pattern for AI to follow when authoring the EP-NNN body in the
    proposal, but the actual file starts as a minimal stub here.
    """
    return f"""---
id: {epic_id}
title: {slug.replace('-', ' ').title()}
status: DRAFT
created: ""
updated: ""
approved_by:
---

<!-- This epic file was bootstrapped by `apply_proposal.py` at sprint seal.
     Content (EP block + FRs + User Stories + AC) is merged from the sprint's
     split epic proposal via anchor-based merge. See `epic-template.md` for
     the canonical structure. -->
"""


def build_synthetic_proposal(
    preamble: str,
    sections_by_name: dict[str, list[tuple[str, list[str]]]],
    frontmatter_text: str,
) -> str:
    """Build a per-target synthetic proposal text containing only the items routed to this target.

    Output: frontmatter + preamble + ## New / ## Updated / ## Removed sections.
    """
    parts: list[str] = []
    if frontmatter_text:
        parts.append(frontmatter_text)
    if preamble:
        parts.append(preamble)
    for section_name in ("New", "Updated", "Removed"):
        items = sections_by_name.get(section_name, [])
        if not items:
            continue
        parts.append(f"## {section_name}")
        for _aid, block_lines in items:
            parts.append("\n".join(block_lines))
    text = "\n\n".join(parts)
    if not text.endswith("\n"):
        text += "\n"
    return text


def _sections_have_items(sections_by_name: dict[str, list[tuple[str, list[str]]]]) -> bool:
    return any(items for items in sections_by_name.values())


def _merge_target_sections(
    current: str,
    preamble: str,
    target_sections: dict[str, list[tuple[str, list[str]]]],
    frontmatter_text: str,
    verbose: bool = False,
) -> tuple[int, str]:
    """Merge one target and keep NEW AC blocks nested under their target US.

    Regular anchor merges append NEW blocks at file end. For epic files that
    would put newly added AC items outside the US they verify. Phase 9 keeps AC
    anchors as separate blocks, but the block must be inserted directly after
    the owning US block and any existing AC siblings for that same US.

    Entire-epic removals are special: a `Removed` EP-NNN entry tombstones the
    whole epic file instead of only deleting the EP anchor and leaving FR/US/AC
    child anchors orphaned.
    """
    removed_ep_items = [
        (aid, block_lines)
        for aid, block_lines in target_sections.get("Removed", [])
        if split_anchor_id(aid)[0] == "EP"
    ]
    if removed_ep_items:
        if len(removed_ep_items) > 1:
            ids = ", ".join(aid for aid, _lines in removed_ep_items)
            return 1, f"cannot remove multiple epic roots in one target merge: {ids}"
        other_items = [
            aid
            for section_name, items in target_sections.items()
            for aid, _lines in items
            if aid != removed_ep_items[0][0]
        ]
        if other_items:
            return (
                1,
                "cannot combine entire epic removal with other edits in the same epic file: "
                + ", ".join(other_items),
            )
        return _tombstone_removed_epic(current, removed_ep_items[0][0], removed_ep_items[0][1])

    normal_sections: dict[str, list[tuple[str, list[str]]]] = {}
    new_ac_items: list[tuple[str, list[str]]] = []

    for section_name, items in target_sections.items():
        for aid, block_lines in items:
            prefix, _num = split_anchor_id(aid)
            if section_name == "New" and prefix == "AC":
                new_ac_items.append((aid, block_lines))
            else:
                normal_sections.setdefault(section_name, []).append((aid, block_lines))

    merged = current
    if _sections_have_items(normal_sections):
        synth = build_synthetic_proposal(preamble, normal_sections, frontmatter_text)
        code, payload = apply(synth, current, verbose=verbose)
        if code != 0:
            return code, payload
        merged = payload

    if not new_ac_items:
        return 0, merged

    return _insert_new_ac_items_under_us(merged, new_ac_items)


def _tombstone_removed_epic(
    current: str,
    epic_id: str,
    removal_block_lines: list[str],
) -> tuple[int, str]:
    """Replace an epic file with a tombstone that retains only the EP anchor.

    The EP ID is never reusable, so the tombstone keeps `<!-- ID: EP-NNN -->`
    as the audit marker. Child FR/US/AC anchors are intentionally removed from
    the active file to keep effective truth from exposing orphaned content.
    """
    _preamble, blocks = parse_anchored_blocks(current)
    living_ids = {aid for aid, _lines in blocks}
    if epic_id not in living_ids:
        return 1, f"REMOVED {epic_id}: not found in living truth"

    title = extract_title_from_block(removal_block_lines) or "Removed epic"
    details = "\n".join(removal_block_lines[2:]).strip()
    if not details:
        details = "- **Reason**: Not specified in removal proposal."

    text = (
        "---\n"
        f"id: {epic_id}\n"
        f"title: {title}\n"
        "status: REMOVED\n"
        "removed: true\n"
        "---\n\n"
        f"<!-- ID: {epic_id} -->\n"
        f"### {epic_id}: {title} [REMOVED]\n\n"
        "<!-- Tombstone generated by apply_proposal.py from a Removed EP entry.\n"
        "     Child FR / US / AC anchors were removed from active Living Truth.\n"
        "     Full pre-removal content remains available in git history and sprint snapshots. -->\n\n"
        f"{details}\n"
    )
    return 0, text


def _insert_new_ac_items_under_us(
    living_text: str,
    ac_items: list[tuple[str, list[str]]],
) -> tuple[int, str]:
    preamble, blocks = parse_anchored_blocks(living_text)
    living_ids = {aid for aid, _lines in blocks}
    seen_new: set[str] = set()

    for aid, block_lines in ac_items:
        us_tag = extract_routing_tag(block_lines, US_TAG_RE)
        if not us_tag:
            return 1, f"NEW {aid}: missing required US routing tag"
        if aid in living_ids or aid in seen_new:
            return 1, f"NEW {aid}: already exists in living truth"
        seen_new.add(aid)

        owner_idx: int | None = None
        for idx, (existing_id, _existing_lines) in enumerate(blocks):
            if existing_id == us_tag:
                owner_idx = idx
                break
        if owner_idx is None:
            return 1, f"NEW {aid}: target US {us_tag} not found in epic file"

        insert_at = owner_idx + 1
        while insert_at < len(blocks):
            next_id, next_lines = blocks[insert_at]
            try:
                next_prefix, _num = split_anchor_id(next_id)
            except ValueError:
                break
            if (
                next_prefix == "AC"
                and extract_routing_tag(next_lines, US_TAG_RE) == us_tag
            ):
                insert_at += 1
                continue
            break

        blocks.insert(insert_at, (aid, block_lines))
        living_ids.add(aid)

    return 0, serialize(preamble, blocks)


def apply_multi_target(
    proposal_text: str,
    project_root: Path,
    project_name: str | None = None,
    current_state: dict[Path, str] | None = None,
    verbose: bool = False,
) -> tuple[int, dict[Path, str] | str]:
    """Phase 9 multi-target merge: route each anchored item in `proposal_text` to the
    correct Living Truth file by ID prefix (plus optional EPIC routing tag), apply
    per-target sub-merges, and return {target_path: merged_text}.

    `current_state` is an optional dict of {target_path: in_memory_content} that the
    caller has already merged in earlier rounds (e.g., seal_sprint chains multiple
    proposals + deltas). When a target is present in `current_state`, it's used as the
    base for this merge instead of reading from disk — this enables atomic write at
    the end (caller only does the final disk write once).

    On error, returns (exit_code, error_message_string).

    For new epic files (EP-NNN anchor in `## New` with no existing file), scaffolds the
    target from `epic-template.md` so the merge has a base to write into.
    """
    if current_state is None:
        current_state = {}
    if project_name is None:
        project_name = project_root.name

    text = _normalize_line_endings(proposal_text)
    try:
        fm, body = parse_frontmatter(text)
    except ValueError as e:
        return 3, str(e)

    # Extract the original frontmatter block (with delimiters) to reuse in per-target proposals.
    fm_match = FRONTMATTER_RE.match(text)
    frontmatter_text = fm_match.group(0).rstrip("\n") if fm_match else ""

    sections = split_proposal_sections(body)
    if not any(sections.values()):
        return 1, "proposal has no anchored items to merge"

    # Preamble (anything between frontmatter and the first merge operation section).
    preamble_match = re.match(r"(.*?)(?=\n## (?:New|Updated|Removed)\b)", body, re.DOTALL)
    preamble = preamble_match.group(1).rstrip() if preamble_match else ""

    # Build epic slug lookup: existing files + this proposal's new EP-NNN items.
    epic_slugs = discover_existing_epic_slugs(project_root, current_state)
    for aid, block_lines in sections.get("New", []):
        prefix, _ = split_anchor_id(aid)
        if prefix != "EP":
            continue
        if aid in epic_slugs:
            # Keep the existing slug stable. If the proposal tries `## New`
            # for an existing EP, the merge target stays the existing file so
            # duplicate-anchor validation can fail instead of creating a
            # second EP-NNN-{new-slug}.md file.
            continue
        title = extract_title_from_block(block_lines)
        slug = slug_from_title(title) if title else "untitled"
        epic_slugs[aid] = slug

    # Pre-scan: build US → epic map (so AC items with `<!-- US: -->` tag can route
    # back to the epic file that contains the US block).
    us_to_epic: dict[str, str] = discover_us_to_epic(project_root, current_state)
    for section_name, items in sections.items():
        for aid, block_lines in items:
            prefix, _ = split_anchor_id(aid)
            if prefix == "US":
                epic_tag = extract_routing_tag(block_lines, EPIC_TAG_RE)
                if epic_tag:
                    us_to_epic[aid] = epic_tag

    # Group items by target LT path.
    by_target: dict[Path, dict[str, list[tuple[str, list[str]]]]] = {}
    epics_to_create: dict[Path, str] = {}  # target_path -> epic_id

    for section_name, items in sections.items():
        for aid, block_lines in items:
            try:
                prefix, _ = split_anchor_id(aid)
            except ValueError:
                return 1, f"malformed anchor ID: {aid}"
            epic_tag = extract_routing_tag(block_lines, EPIC_TAG_RE)
            us_tag = extract_routing_tag(block_lines, US_TAG_RE)
            target = derive_lt_for_anchor(
                aid, epic_tag, project_root, epic_slugs,
                us_to_epic=us_to_epic, us_tag=us_tag,
            )
            if target is None:
                return 1, f"no routing for anchor {aid} (prefix '{prefix}' — needs EPIC or US tag for FR/US/AC)"
            if prefix == "EP" and section_name == "New":
                epics_to_create[target] = aid
            by_target.setdefault(target, {}).setdefault(section_name, []).append((aid, block_lines))

    # Apply per target.
    results: dict[Path, str] = {}
    for target, target_sections in by_target.items():
        # Prefer in-memory state from prior rounds (atomicity); fall back to disk; else bootstrap epic.
        if target in current_state:
            current = current_state[target]
        elif target.exists():
            current = target.read_text(encoding="utf-8")
        elif target in epics_to_create:
            # Bootstrap a new epic file from epic-template
            epic_id = epics_to_create[target]
            slug = epic_slugs.get(epic_id, "untitled")
            current = scaffold_epic_file(target, epic_id, slug, project_name)
        else:
            return 2, f"target Living Truth missing: {target}"

        code, payload = _merge_target_sections(
            current,
            preamble,
            target_sections,
            frontmatter_text,
            verbose=verbose,
        )
        if code != 0:
            return code, f"merge failed for {target}: {payload}"
        results[target] = payload

    if verbose:
        sys.stderr.write(f"multi-target merge: {len(results)} target(s) touched\n")
        for t in results:
            sys.stderr.write(f"  → {t}\n")

    return 0, results


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Apply a sprint proposal to a living-truth markdown file (Phase 2 production).",
    )
    parser.add_argument("--proposal", help="Path to proposal markdown")
    parser.add_argument("--living", help="Path to living-truth markdown")
    parser.add_argument("--dry-run", action="store_true", help="Print result to stdout, do not write")
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args()

    explicit = bool(args.proposal) or bool(args.living)
    if explicit and not (args.proposal and args.living):
        sys.stderr.write("ERROR: --proposal and --living must be specified together\n")
        return 1
    if not explicit:
        sys.stderr.write("ERROR: provide --proposal and --living\n")
        return 1

    proposal_path = Path(args.proposal)
    living_path = Path(args.living)

    if not proposal_path.is_file():
        sys.stderr.write(f"ERROR: proposal not found: {proposal_path}\n")
        return 2

    if not living_path.is_file():
        sys.stderr.write(f"ERROR: living truth not found: {living_path}\n")
        return 2

    proposal_text = proposal_path.read_text(encoding="utf-8")
    living_text = living_path.read_text(encoding="utf-8")

    code, payload = apply(proposal_text, living_text, verbose=args.verbose)
    if code != 0:
        sys.stderr.write(payload + "\n")
        return code

    if args.dry_run:
        sys.stdout.write(payload)
    else:
        tmp = living_path.with_suffix(living_path.suffix + ".tmp")
        tmp.write_text(payload, encoding="utf-8")
        tmp.replace(living_path)

    return 0


if __name__ == "__main__":
    sys.exit(main())
