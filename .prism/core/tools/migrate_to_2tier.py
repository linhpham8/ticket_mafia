#!/usr/bin/env python3
"""migrate_to_2tier.py — Phase 7.

One-time migration helper that converts a PRISM 1.x project into the 2.0.0
2-tier Living Truth model with Phase 9 nested per-phase layout.

What it does
------------
1. Pre-flight: detects project root (has prism-config.md), finds the latest
   sprint folder (highest `sprint-v{X}/`), and verifies the project is on a
   1.x-style layout (per-sprint full-document files like `prd-v{X}.md`).
2. Backup: snapshots `docs/` → `docs.pre-migrate-{ts}/` and
   `prism-config.md` → `prism-config.md.pre-migrate-{ts}` so the original
   state is recoverable.
3. File migration: copies the latest sprint's per-phase artifacts to the
   Phase 9 Living Truth paths under `/docs/{product,design,architecture,testing}/`.
4. Content transforms applied to migrated content:
     - `EPIC-NNN` → `EP-NNN` (anchor IDs, headings, body references).
     - `<!-- ID: COMP-NNN -->` in `architecture-v{X}.md` → `ARCH-COMP-NNN`.
     - `<!-- ID: COMP-NNN -->` in `design-v{X}.md` → `DS-COMP-NNN`.
     - `TC-{AREA}-NNN` → flat `TC-NNN` + appends a `**Area**: {AREA}` body field.
5. Epic split: parses `epics-v{X}.md` + `user-stories-v{X}.md` for EP-NNN blocks
   and US-NNN blocks (US `Epic:` field links them) and writes one
   `/docs/product/epics/EP-NNN-{slug}.md` per epic with its FRs + USs + ACs.
6. NFR move: extracts NFR-NNN anchored blocks from `prd-v{X}.md` and appends
   them to `/docs/architecture/nfr.md`.
7. Anchor heuristic insertion (Level 3): for narrative LT files that became
   Living Truth in Phase 9 (sequence, erd, adr, data-flow, api-specs, events,
   project-reference, glossary, personas, market-research, nfr), inserts an
   `<!-- ID: PREFIX-NNN -->` anchor above each detected mergeable unit when one
   is missing. Heuristic — flags ambiguous cases for human review.
8. `id_counters` update: scans all migrated files for anchored IDs, sets
   `id_counters[PREFIX]` to the high-water mark per prefix, and adds Phase 9
   counters (BR, NFR, TC, GLOSS, PERSONA, MR, SEQ, ENT, ADR, FLOW, API, EVT,
   PR, DS-COMP, ARCH-COMP) if missing. Legacy `EPIC` counter renamed to `EP`.
9. Older sprints (where N < latest) get a `.historical` marker file so AI
   tooling can flag them as audit history and not load them into effective truth.
10. Reports: stdout receives a human-readable migration summary; stderr
    receives progress + warnings. A mid-run failure leaves `docs/` in a
    partial state, but the backup created in step 2 is untouched and the
    error handler prints copy-paste rollback commands.

CLI
---
  migrate_to_2tier.py --root /path/to/project [--dry-run] [--from-sprint v{X}]

  --dry-run         : Report planned actions without writing anything.
  --from-sprint vX  : Treat sprint vX as the latest (default: auto-detect).
  --root PATH       : Project root (default: walk up from CWD).

Exit codes
----------
  0  OK
  1  validation fail (unmigrateable state, conflicts)
  2  file not found (no project root, no latest sprint)
  3  config error (malformed prism-config.md, no YAML block)

Out of scope
------------
- Re-merging change packs into Living Truth (they migrate alongside their
  sprint folder but stay sprint-only; user re-runs `seal_sprint.py` if they
  want them merged into Living Truth post-migration).
- Sprint-only artifacts (`test-plan-v{X}.md`, `implementation-plan-v{X}.md`):
  left intact in their sprint folder; they don't promote to Living Truth.
- AI judgment for ambiguous anchor units: tool inserts anchors deterministically
  on clearly-typed headings (`### ADR-001 — title`, `### Entity: Users`) and
  flags everything else for human review in the report.
"""

from __future__ import annotations

import argparse
import datetime as dt
import re
import shutil
import sys
import unicodedata
from dataclasses import dataclass, field
from pathlib import Path

import yaml

# --- Path mappings: 1.x sprint-scoped → Phase 9 Living Truth ----------------

PRODUCT_FILE_MAP = {
    "prd-v{X}.md": "product/prd.md",
    "glossary-v{X}.md": "product/glossary.md",
    "personas-v{X}.md": "product/personas.md",
    "market-research-v{X}.md": "product/market-research.md",
}

DESIGN_FILE_MAP = {
    "design-v{X}.md": "design/design-system.md",
}

ARCHITECTURE_FILE_MAP = {
    "architecture-v{X}.md": "architecture/architecture.md",
    "nfr-v{X}.md": "architecture/nfr.md",
    "sequence-v{X}.md": "architecture/sequence.md",
    "erd-v{X}.md": "architecture/erd.md",
    "adr-v{X}.md": "architecture/adr.md",
    "data-flow-v{X}.md": "architecture/data-flow.md",
    "api-specs-v{X}.md": "architecture/api-specs.md",
    "events-v{X}.md": "architecture/events.md",
    "project-reference-v{X}.md": "architecture/project-reference.md",
}

TESTING_FILE_MAP = {
    "test-cases-v{X}.md": "testing/test-cases.md",
}

# Anchor heuristics — patterns to detect mergeable units in narrative files.
# Each entry: (LT_filename → (prefix, regex-matching-an-item-line))
ANCHOR_HEURISTICS = {
    "architecture/nfr.md": ("NFR", re.compile(r"^(##{1,3}|\*\*)\s*(?:NFR[-_]?)?(\d{3,})\b", re.MULTILINE)),
    "architecture/sequence.md": ("SEQ", re.compile(r"^### (?:Flow|Sequence)[: ](.+)$", re.MULTILINE)),
    "architecture/erd.md": ("ENT", re.compile(r"^### (?:Entity|Table)[: ](.+)$", re.MULTILINE)),
    "architecture/adr.md": ("ADR", re.compile(r"^##\s+ADR[-_]?(\d{3,})\b", re.MULTILINE)),
    "architecture/data-flow.md": ("FLOW", re.compile(r"^### Flow[: ](.+)$", re.MULTILINE)),
    "architecture/api-specs.md": ("API", re.compile(r"^### Endpoint[: ](.+)$", re.MULTILINE)),
    "architecture/events.md": ("EVT", re.compile(r"^## Event[: ](.+)$", re.MULTILINE)),
    "architecture/project-reference.md": ("PR", re.compile(r"^### Module[: ](.+)$", re.MULTILINE)),
    "product/glossary.md": ("GLOSS", re.compile(r"^### ([A-Z][A-Za-z ]+)$", re.MULTILINE)),
    "product/personas.md": ("PERSONA", re.compile(r"^### Persona \d+:[ ](.+)$", re.MULTILINE)),
    "product/market-research.md": ("MR", re.compile(r"^### Finding[: ](.+)$", re.MULTILINE)),
}

# Architecture / design split for the legacy `COMP` prefix.
COMP_RENAME_BY_FILE = {
    "architecture/architecture.md": "ARCH-COMP",
    "design/design-system.md": "DS-COMP",
}

# 21 Phase 9 ID counters that prism-config.md should contain post-migration.
PHASE9_COUNTERS = (
    "EP", "FR", "US", "AC", "BR", "GLOSS", "PERSONA", "MR",
    "SCREEN", "DS-COMP",
    "ARCH", "ARCH-COMP", "NFR", "SEQ", "ENT", "ADR", "FLOW", "API", "EVT", "PR",
    "TC",
)

YAML_BLOCK_RE = re.compile(r"(```yaml\n)(.*?)(\n```)", re.DOTALL)
SPRINT_DIR_RE = re.compile(r"^sprint-v(\d+)$")
ANCHOR_RE = re.compile(r"^<!--\s*ID:\s*([A-Z]+(?:-[A-Z]+)*-\d+)\s*-->\s*$", re.MULTILINE)
EPIC_HEADING_RE = re.compile(r"^###\s+EP(?:IC)?-(\d{3,}):\s*(.+?)\s*$", re.MULTILINE)


# ---------------------------------------------------------------------------
# Data classes — planning then execution
# ---------------------------------------------------------------------------


@dataclass
class FileMove:
    src: Path
    dst: Path
    transform: str  # "copy" | "split_epics" | "extract_nfr"


@dataclass
class WarningEntry:
    kind: str
    message: str


@dataclass
class MigrationPlan:
    project_root: Path
    latest_sprint: int
    backup_docs: Path
    backup_config: Path
    file_moves: list[FileMove] = field(default_factory=list)
    epic_split_sources: dict[str, Path] = field(default_factory=dict)  # {"epics": Path, "user_stories": Path}
    older_sprints: list[Path] = field(default_factory=list)
    warnings: list[WarningEntry] = field(default_factory=list)

    def add_warn(self, kind: str, msg: str) -> None:
        self.warnings.append(WarningEntry(kind, msg))


# ---------------------------------------------------------------------------
# Discovery
# ---------------------------------------------------------------------------


def find_project_root(start: Path) -> Path | None:
    p = start.resolve()
    for parent in [p] + list(p.parents):
        if (parent / "prism-config.md").is_file():
            return parent
    return None


def detect_latest_sprint(docs_dir: Path) -> int | None:
    """Highest sprint-v{N} folder under /docs/."""
    if not docs_dir.is_dir():
        return None
    versions: list[int] = []
    for d in docs_dir.iterdir():
        m = SPRINT_DIR_RE.match(d.name)
        if m and d.is_dir():
            versions.append(int(m.group(1)))
    return max(versions) if versions else None


def detect_phase9_already_migrated(docs_dir: Path) -> bool:
    """Refuse second migration. Returns True if *any* Phase 9 LT marker is present.

    Checks the full union of LT files the tool would produce (15 root LT files + the
    `product/epics/EP-*.md` directory). A half-migrated state — e.g. only
    `testing/test-cases.md` was previously promoted — still trips the guard.
    """
    lt_markers: list[str] = []
    for table in (PRODUCT_FILE_MAP, DESIGN_FILE_MAP, ARCHITECTURE_FILE_MAP, TESTING_FILE_MAP):
        lt_markers.extend(table.values())
    for marker in lt_markers:
        if (docs_dir / marker).is_file():
            return True
    epics_dir = docs_dir / "product" / "epics"
    if epics_dir.is_dir() and any(epics_dir.glob("EP-*.md")):
        return True
    return False


# ---------------------------------------------------------------------------
# Slug derivation (mirrors apply_proposal.slug_from_title for consistency)
# ---------------------------------------------------------------------------


def slug_from_title(title: str, max_len: int = 40) -> str:
    nfkd = unicodedata.normalize("NFKD", title)
    no_diacritics = "".join(c for c in nfkd if not unicodedata.combining(c))
    no_diacritics = no_diacritics.replace("đ", "d").replace("Đ", "D")
    lower = no_diacritics.lower()
    s = re.sub(r"[^a-z0-9]+", "-", lower).strip("-")
    if len(s) > max_len:
        s = s[:max_len].rstrip("-")
    return s or "untitled"


# ---------------------------------------------------------------------------
# Plan building
# ---------------------------------------------------------------------------


def build_plan(project_root: Path, latest_sprint: int, timestamp: str) -> MigrationPlan:
    docs_dir = project_root / "docs"
    sprint_dir = docs_dir / f"sprint-v{latest_sprint}"
    plan = MigrationPlan(
        project_root=project_root,
        latest_sprint=latest_sprint,
        backup_docs=project_root / f"docs.pre-migrate-{timestamp}",
        backup_config=project_root / f"prism-config.md.pre-migrate-{timestamp}",
    )

    missing: list[str] = []

    def _check(folder: str, table: dict[str, str]) -> None:
        for src_name, dst_rel in table.items():
            src = sprint_dir / folder / src_name.format(X=latest_sprint)
            if src.is_file():
                plan.file_moves.append(FileMove(src=src, dst=docs_dir / dst_rel, transform="copy"))
            else:
                missing.append(str(src.relative_to(project_root)))

    _check("product", PRODUCT_FILE_MAP)
    _check("design", DESIGN_FILE_MAP)
    _check("architecture", ARCHITECTURE_FILE_MAP)
    _check("testing", TESTING_FILE_MAP)

    # Epic split sources (epics + user-stories) — split into per-epic files
    epics_src = sprint_dir / "product" / f"epics-v{latest_sprint}.md"
    us_src = sprint_dir / "product" / f"user-stories-v{latest_sprint}.md"
    if epics_src.is_file():
        plan.epic_split_sources["epics"] = epics_src
    else:
        missing.append(str(epics_src.relative_to(project_root)))
        # C2: if user-stories exists but epics doesn't, stories cannot be attached and
        # will be lost — flag loudly so the user can recover them manually.
        if us_src.is_file():
            plan.add_warn(
                "stories_without_epics",
                f"{us_src.relative_to(project_root)} found but no epics file alongside it; "
                "user stories cannot be routed to per-epic files and will not appear in "
                "/docs/product/epics/. Recover them manually after migration.",
            )
    if us_src.is_file():
        plan.epic_split_sources["user_stories"] = us_src

    # Aggregate missing-source notices into one summary warning to avoid log noise.
    if missing:
        plan.add_warn(
            "missing_source",
            f"{len(missing)} expected 1.x file(s) not found; skipped: {', '.join(missing)}",
        )

    # Older sprints (< latest) — mark historical
    for d in docs_dir.iterdir():
        m = SPRINT_DIR_RE.match(d.name)
        if m and int(m.group(1)) < latest_sprint:
            plan.older_sprints.append(d)

    return plan


# ---------------------------------------------------------------------------
# Content transforms
# ---------------------------------------------------------------------------


def transform_epic_to_ep(text: str) -> str:
    """EPIC- prefix → EP-: handles anchors, headings, and bare references."""
    text = re.sub(r"\bEPIC-(\d{3,})", r"EP-\1", text)
    text = re.sub(r"\bEPIC-NNN\b", "EP-NNN", text)
    return text


def transform_comp_to_split(text: str, target_dst: str) -> str:
    """COMP-NNN → ARCH-COMP-NNN (in architecture context) or DS-COMP-NNN (design)."""
    new_prefix = COMP_RENAME_BY_FILE.get(target_dst)
    if new_prefix is None:
        return text
    return re.sub(r"\bCOMP-(\d{3,})\b", rf"{new_prefix}-\1", text)


def transform_tc_area_to_flat(text: str) -> str:
    r"""`TC-{AREA}-NNN` → globally-renumbered `TC-NNN` + appends `**Area**: {AREA}` body field.

    Renumbers in document order to avoid collisions when multiple areas used the same NNN
    (e.g. `TC-AUTH-001` and `TC-COURSE-001` would otherwise both flatten to `TC-001`).
    Conservative: only touches IDs matching `TC-[A-Z]+-\d+`. Pure `TC-\d+` IDs are kept.
    """
    legacy_id_re = re.compile(r"TC-([A-Z]+)-(\d{3,})")
    seen: list[tuple[str, str]] = []
    for m in legacy_id_re.finditer(text):
        key = (m.group(1), m.group(2))
        if key not in seen:
            seen.append(key)
    if not seen:
        return text
    mapping = {key: f"TC-{i + 1:03d}" for i, key in enumerate(seen)}

    def replace_anchor_id(m: re.Match[str]) -> str:
        return f"<!-- ID: {mapping[(m.group(1), m.group(2))]} -->"

    def replace_heading(m: re.Match[str]) -> str:
        area = m.group(1)
        new_id = mapping[(area, m.group(2))]
        rest = m.group(3) or ""
        return f"### {new_id}:{rest}\n**Area**: {area}\n"

    text = re.sub(
        r"<!--\s*ID:\s*TC-([A-Z]+)-(\d{3,})\s*-->",
        replace_anchor_id,
        text,
    )
    text = re.sub(
        r"###\s*TC-([A-Z]+)-(\d{3,}):?( .*)?",
        replace_heading,
        text,
    )
    return text


def extract_nfr_blocks(prd_text: str) -> tuple[str, str]:
    """Pulls NFR-NNN anchored blocks out of prd.md content. Returns (remaining_prd, extracted_nfr_md).

    Block boundary rules (in order):
      1. The block STARTS at an `<!-- ID: NFR-NNN -->` anchor line.
      2. The line immediately after the anchor is the heading (`### NFR-NNN: ...`) and is
         always collected.
      3. After the heading, the block continues until ANY of:
         - another `<!-- ID: ... -->` anchor (any prefix);
         - an `^##\\s` H2 heading;
         - an `^###\\s` H3 heading that does NOT begin with `NFR-` (treated as the start
           of a different section that should remain in `prd.md`);
         - end-of-file.

    The H3-cut rule is what prevents a stray non-NFR H3 sub-section that happens to sit
    underneath an NFR block in 1.x PRDs from being swept into the extracted output.
    """
    extracted_blocks: list[str] = []
    out_lines: list[str] = []
    lines = prd_text.split("\n")
    i = 0
    nfr_h3_re = re.compile(r"^###\s+NFR-\d{3,}\b")
    h3_re = re.compile(r"^###\s")
    while i < len(lines):
        if re.match(r"^<!--\s*ID:\s*NFR-\d{3,}\s*-->", lines[i].strip()):
            # Capture this NFR block until the next anchor, H2, non-NFR H3, or EOF.
            block: list[str] = [lines[i]]
            j = i + 1
            heading_seen = False
            while j < len(lines):
                line = lines[j]
                if re.match(r"^<!--\s*ID:\s*[A-Z]", line.strip()):
                    break
                if re.match(r"^##\s", line):
                    break
                if h3_re.match(line):
                    # The first H3 we see is the NFR heading itself — always keep.
                    # Any subsequent H3 that isn't `### NFR-NNN` is a different section
                    # and ends this block.
                    if heading_seen and not nfr_h3_re.match(line):
                        break
                    heading_seen = True
                block.append(line)
                j += 1
            extracted_blocks.append("\n".join(block).rstrip())
            i = j
            continue
        out_lines.append(lines[i])
        i += 1
    return "\n".join(out_lines), "\n\n".join(extracted_blocks)


def split_epics_and_user_stories(
    epics_text: str,
    user_stories_text: str | None,
) -> tuple[dict[str, dict], list[tuple[str, str]]]:
    """Parse epics-v{X}.md (and optionally user-stories-v{X}.md) → produce per-epic content.

    Returns `(epics_by_id, orphans)`:
      - `epics_by_id`: `{"EP-NNN": {"slug": str, "title": str, "block": str, "stories": [story_block, ...]}}`
      - `orphans`: list of `(US-NNN, reason)` for stories that could not be attached.
        `reason` is `"no_epic_ref"` (no `Epic:` field) or `"unknown_epic:EP-NNN"`
        (the referenced epic doesn't exist in `epics_text`). Caller is responsible for
        surfacing these as warnings — they will NOT appear in any per-epic file.

    Epic detection: `### EP-NNN:` or legacy `### EPIC-NNN:`. The full anchored block runs
    until the next epic-level anchor or section break.
    Story-to-epic linking (when user_stories_text is present): each US block is scanned for
    `Epic: EP-NNN` (case-insensitive) — story attaches to that epic.
    """
    epics: dict[str, dict] = {}
    orphans: list[tuple[str, str]] = []
    # Find epic headings + their content
    matches = list(EPIC_HEADING_RE.finditer(epics_text))
    for idx, m in enumerate(matches):
        epic_num = m.group(1)
        epic_id = f"EP-{epic_num.zfill(3)}"
        title = m.group(2).strip()
        slug = slug_from_title(title)
        # Block runs from this heading to the next epic heading or end of text.
        # The `<!-- ID: EP-XXX -->` anchor for THIS epic sits BEFORE the heading in the
        # source — we want to pull it in. Conversely, the next epic's anchor sits at the
        # END of our slice — we want to drop it (it'll be re-attached by its own block).
        start = m.start()
        end = matches[idx + 1].start() if idx + 1 < len(matches) else len(epics_text)
        block = epics_text[start:end].rstrip()
        # Normalize legacy EPIC- → EP- everywhere (anchors, headings, refs).
        block = transform_epic_to_ep(block)
        # Drop any trailing `<!-- ID: EP-NNN -->` anchor that belongs to the NEXT block
        # (would have been swept into our slice when the heading-position split fell
        # below the anchor line).
        block = re.sub(
            r"\n<!--\s*ID:\s*EP-\d+\s*-->\s*$",
            "",
            block,
        ).rstrip()
        # Drop any other-epic anchors elsewhere in the block (defensive).
        def _keep_only_self(m2: re.Match[str]) -> str:
            return m2.group(0) if m2.group(1) == epic_id else ""

        block = re.sub(
            r"<!--\s*ID:\s*(EP-\d+)\s*-->",
            _keep_only_self,
            block,
        )
        # Ensure the block STARTS with the correct anchor for this epic.
        if not re.match(r"^<!--\s*ID:\s*EP-\d+", block):
            block = f"<!-- ID: {epic_id} -->\n{block}"
        epics[epic_id] = {"slug": slug, "title": title, "block": block, "stories": []}

    # Attach user stories to their epic
    if user_stories_text:
        us_text = transform_epic_to_ep(user_stories_text)
        # Each anchored US block: `<!-- ID: US-NNN -->\n### US-NNN: Title\n...`
        # Run from anchor to next anchor or section break.
        us_blocks = re.split(r"(?=<!--\s*ID:\s*US-\d{3,}\s*-->)", us_text)
        for ub in us_blocks:
            us_id_match = re.match(r"^<!--\s*ID:\s*(US-\d{3,})\s*-->", ub.strip())
            if not us_id_match:
                continue
            us_id = us_id_match.group(1)
            # Find epic ref inside the block (legacy: "Epic: EPIC-001" or "EP: EP-001")
            ep_ref = re.search(r"Epic\s*:\s*(EP(?:IC)?-\d{3,})", ub)
            if not ep_ref:
                orphans.append((us_id, "no_epic_ref"))
                continue
            target_epic = ep_ref.group(1)
            if target_epic.startswith("EPIC-"):
                target_epic = "EP-" + target_epic[5:]
            if target_epic not in epics:
                orphans.append((us_id, f"unknown_epic:{target_epic}"))
                continue
            # Add EPIC routing tag right after the ID anchor for Phase 9 routing semantics
            ub = re.sub(
                r"(<!--\s*ID:\s*US-\d{3,}\s*-->)",
                rf"\1\n<!-- EPIC: {target_epic} -->",
                ub,
                count=1,
            )
            epics[target_epic]["stories"].append(ub.rstrip())

    return epics, orphans


# ---------------------------------------------------------------------------
# Anchor heuristic insertion
# ---------------------------------------------------------------------------


def insert_heuristic_anchors(text: str, dst_rel: str) -> tuple[str, list[str]]:
    """For narrative LT files, try to insert `<!-- ID: PREFIX-NNN -->` above clearly
    identifiable mergeable units (per ANCHOR_HEURISTICS).

    Returns (transformed_text, warnings_list). Conservative: only adds anchors where the
    pattern unambiguously matches. Logs uncertain cases to warnings.
    """
    heur = ANCHOR_HEURISTICS.get(dst_rel)
    if heur is None:
        return text, []
    prefix, pattern = heur
    warnings: list[str] = []

    # Skip if file already has anchors
    if ANCHOR_RE.search(text):
        return text, [f"{dst_rel}: already has anchors; no heuristic insertion attempted"]

    # Walk through pattern matches and insert anchors
    counter = 1
    lines = text.split("\n")
    out: list[str] = []
    inserted = 0
    for line in lines:
        if pattern.match(line):
            # Insert anchor above this line
            anchor_id = f"{prefix}-{counter:03d}"
            counter += 1
            out.append(f"<!-- ID: {anchor_id} -->")
            inserted += 1
        out.append(line)
    if inserted == 0:
        warnings.append(f"{dst_rel}: pattern matched 0 items — manual anchor insertion needed")
    else:
        warnings.append(f"{dst_rel}: inserted {inserted} heuristic anchors with prefix {prefix} (review recommended)")
    return "\n".join(out), warnings


# ---------------------------------------------------------------------------
# id_counters update
# ---------------------------------------------------------------------------


def scan_high_water_marks(docs_dir: Path) -> dict[str, int]:
    """Scan migrated Living Truth files for anchored IDs; return {PREFIX: max_NNN_value}.

    Walks only the four LT subtrees (product/, design/, architecture/, testing/) — sprint-v*
    folders are skipped (their legacy IDs would otherwise re-introduce EPIC/COMP/TC-AREA
    counters that the migration is trying to retire).
    """
    counters: dict[str, int] = {}
    for subdir in ("product", "design", "architecture", "testing"):
        sd = docs_dir / subdir
        if not sd.is_dir():
            continue
        for md in sd.rglob("*.md"):
            try:
                text = md.read_text(encoding="utf-8")
            except OSError:
                continue
            for m in ANCHOR_RE.finditer(text):
                anchor_id = m.group(1)
                split_m = re.match(r"^([A-Z]+(?:-[A-Z]+)*)-(\d+)$", anchor_id)
                if not split_m:
                    continue
                prefix = split_m.group(1)
                num = int(split_m.group(2))
                counters[prefix] = max(counters.get(prefix, 0), num)
    return counters


def update_id_counters_in_config(config_path: Path, counters: dict[str, int]) -> None:
    """Rewrite `id_counters:` block in prism-config.md.

    Migration rules:
      - Bootstrap block if missing.
      - Rename legacy `EPIC:` → `EP:` (preserve value, taking max with scanned EP).
      - Add Phase 9 counters that aren't yet present.
      - For each prefix in scanned `counters`, set value = max(existing, scanned).
    """
    full = config_path.read_text(encoding="utf-8")
    m = YAML_BLOCK_RE.search(full)
    if not m:
        raise ValueError("no YAML code fence ```yaml ... ``` found in prism-config.md")
    yaml_text = m.group(2)
    data = yaml.safe_load(yaml_text) or {}
    existing = data.get("id_counters") or {}
    # Phase 9 migration: legacy EPIC → EP
    if "EPIC" in existing:
        existing["EP"] = max(existing.get("EP", 0), int(existing["EPIC"]))
        del existing["EPIC"]
    # Drop other retired legacy prefixes — COMP was split into ARCH-COMP + DS-COMP, and
    # TC-{AREA} buckets were flattened to TC by transform_tc_area_to_flat. The scanned
    # high-water marks already cover the new prefixes.
    for legacy in list(existing.keys()):
        if legacy == "COMP" or re.match(r"^TC-[A-Z]+$", legacy):
            del existing[legacy]
    # Merge with scanned high-water marks
    for prefix, val in counters.items():
        existing[prefix] = max(int(existing.get(prefix, 0)), val)
    # Ensure all Phase 9 counters exist
    for prefix in PHASE9_COUNTERS:
        existing.setdefault(prefix, 0)

    # Rewrite the block in canonical order
    canonical_order = list(PHASE9_COUNTERS) + sorted(set(existing) - set(PHASE9_COUNTERS))
    lines = ["id_counters:"]
    for prefix in canonical_order:
        if prefix in existing:
            lines.append(f"  {prefix}: {existing[prefix]}")
    new_block = "\n".join(lines)

    # Replace existing id_counters: block (if any) with new one
    new_yaml = re.sub(
        r"(?ms)^id_counters:\n(?:\s+\S.*\n?)*",
        new_block + "\n",
        yaml_text,
    )
    if new_yaml == yaml_text:
        # No existing block — append before final newline
        new_yaml = yaml_text.rstrip() + "\n\n" + new_block + "\n"

    new_full = YAML_BLOCK_RE.sub(
        lambda mm: f"{mm.group(1)}{new_yaml}{mm.group(3)}", full, count=1
    )
    config_path.write_text(new_full, encoding="utf-8")


# ---------------------------------------------------------------------------
# Execution
# ---------------------------------------------------------------------------


def execute_plan(plan: MigrationPlan, dry_run: bool) -> None:
    """Apply the plan in order: backup → file moves → epic split → NFR move → anchors → counters → mark historical.

    NOTE on atomicity: a backup of `docs/` and `prism-config.md` is created BEFORE any
    writes, so the original state is always recoverable. Writes themselves are NOT
    transactional — a mid-run crash can leave `docs/{product,design,architecture,testing}/`
    in a partial state; the caller (`main()`) prints rollback instructions in that case.
    """
    docs_dir = plan.project_root / "docs"
    # Single now() so all files migrated in this run share a consistent timestamp.
    migrate_now = dt.datetime.now()
    migrate_date = migrate_now.strftime("%Y-%m-%d")
    migrate_datetime = migrate_now.strftime("%Y-%m-%d %H:%M")

    if dry_run:
        sys.stderr.write("(dry-run) skipping backup\n")
    else:
        # Backup
        shutil.copytree(docs_dir, plan.backup_docs)
        shutil.copy2(plan.project_root / "prism-config.md", plan.backup_config)
        sys.stderr.write(f"backed up: {plan.backup_docs.name}, {plan.backup_config.name}\n")

    # Migrate per-file
    nfr_extra: list[str] = []
    nfr_target = docs_dir / "architecture/nfr.md"
    for fm in plan.file_moves:
        text = fm.src.read_text(encoding="utf-8")
        dst_rel = fm.dst.relative_to(docs_dir).as_posix()
        # Universal transforms
        text = transform_epic_to_ep(text)
        text = transform_comp_to_split(text, dst_rel)
        if dst_rel == "testing/test-cases.md":
            text = transform_tc_area_to_flat(text)
        # Extract NFR from prd → defer to nfr.md
        if dst_rel == "product/prd.md":
            text, extracted = extract_nfr_blocks(text)
            if extracted:
                nfr_extra.append(extracted)
                plan.add_warn(
                    "nfr_extracted",
                    f"extracted NFR block(s) from prd.md → architecture/nfr.md",
                )
        # Heuristic anchor insertion for narrative LT
        text, anchor_warns = insert_heuristic_anchors(text, dst_rel)
        for w in anchor_warns:
            plan.add_warn("anchor_heuristic", w)

        # L4: design is the only LT we don't run heuristic anchor on (SCREEN + DS-COMP
        # share the same file and a single pattern can't disambiguate). Warn if the
        # final design content has zero anchors — proposals against it will fail.
        if dst_rel == "design/design-system.md" and not ANCHOR_RE.search(text):
            plan.add_warn(
                "no_anchors",
                "design/design-system.md has no Phase 9 anchors after migration; add "
                "SCREEN-NNN / DS-COMP-NNN anchors manually before the next sprint, or "
                "future proposals against it will fail validate_proposal.",
            )

        if dry_run:
            sys.stderr.write(f"(dry-run) would write: {dst_rel} (from {fm.src.name})\n")
        else:
            fm.dst.parent.mkdir(parents=True, exist_ok=True)
            fm.dst.write_text(text, encoding="utf-8")

    # Append extracted NFR blocks to architecture/nfr.md
    if nfr_extra:
        existing = nfr_target.read_text(encoding="utf-8") if nfr_target.is_file() else "# Non-Functional Requirements\n"
        merged = existing.rstrip() + "\n\n" + "\n\n".join(nfr_extra) + "\n"
        if dry_run:
            sys.stderr.write(f"(dry-run) would append {len(nfr_extra)} NFR block(s) to architecture/nfr.md\n")
        else:
            nfr_target.parent.mkdir(parents=True, exist_ok=True)
            nfr_target.write_text(merged, encoding="utf-8")

    # Epic split — per-epic files
    if "epics" in plan.epic_split_sources:
        epics_text = plan.epic_split_sources["epics"].read_text(encoding="utf-8")
        us_text = plan.epic_split_sources.get("user_stories")
        us_text_content = us_text.read_text(encoding="utf-8") if us_text else None
        epics, orphans = split_epics_and_user_stories(epics_text, us_text_content)
        epics_dir = docs_dir / "product/epics"
        for epic_id, info in epics.items():
            filename = f"{epic_id}-{info['slug']}.md"
            epic_file = epics_dir / filename
            # C4: full Phase 9 epic frontmatter (matches core/templates/epic-template.md).
            # status=APPROVED because migration only promotes the latest *sealed* sprint;
            # approved_by=pre-2.0-migration marks these as bulk-imported rather than
            # newly-authored content.
            content = (
                "---\n"
                f"id: {epic_id}\n"
                f"title: {info['title']}\n"
                f"status: APPROVED\n"
                f"created: {migrate_date}\n"
                f"updated: {migrate_datetime}\n"
                f"approved_by: pre-2.0-migration\n"
                "---\n\n"
                + info["block"].strip()
                + "\n"
            )
            if info["stories"]:
                content += "\n## User Stories\n\n" + "\n\n".join(s.strip() for s in info["stories"]) + "\n"
            if dry_run:
                sys.stderr.write(f"(dry-run) would write: {epic_file.relative_to(plan.project_root)}\n")
            else:
                epic_file.parent.mkdir(parents=True, exist_ok=True)
                epic_file.write_text(content, encoding="utf-8")
        plan.add_warn("epic_split", f"split into {len(epics)} per-epic file(s)")

        # C1: surface orphan stories so the user can recover them manually.
        for us_id, reason in orphans:
            plan.add_warn(
                "orphan_us",
                f"{us_id} not attached to any epic ({reason}); will NOT appear in "
                "/docs/product/epics/. Recover manually from the backup if needed.",
            )

    # Mark older sprints historical
    for sprint_dir in plan.older_sprints:
        marker = sprint_dir / ".historical"
        if dry_run:
            sys.stderr.write(f"(dry-run) would touch: {marker.relative_to(plan.project_root)}\n")
        else:
            marker.write_text(
                "This sprint is historical (pre-2.0.0 migration). Its content has been "
                "promoted into the Living Truth at /docs/{product,design,architecture,testing}/."
                " AI tooling should not load this sprint into effective truth.\n",
                encoding="utf-8",
            )

    # Update id_counters based on high-water marks of migrated content
    if not dry_run:
        counters = scan_high_water_marks(docs_dir)
        try:
            update_id_counters_in_config(plan.project_root / "prism-config.md", counters)
        except ValueError as e:
            plan.add_warn("counters", f"id_counters update failed: {e}")
    else:
        sys.stderr.write("(dry-run) would scan high-water marks and update id_counters in prism-config.md\n")


# ---------------------------------------------------------------------------
# Reporting
# ---------------------------------------------------------------------------


def report(plan: MigrationPlan, dry_run: bool) -> None:
    print(f"PRISM migrate_to_2tier — {'DRY-RUN' if dry_run else 'APPLIED'}")
    print(f"  Project root      : {plan.project_root}")
    print(f"  Latest sprint     : v{plan.latest_sprint}")
    if not dry_run:
        print(f"  Backup (docs/)    : {plan.backup_docs.name}")
        print(f"  Backup (config)   : {plan.backup_config.name}")
    print(f"\n  Files migrated    : {len(plan.file_moves)}")
    for fm in plan.file_moves:
        print(f"    {fm.src.relative_to(plan.project_root)} → {fm.dst.relative_to(plan.project_root)}")
    if plan.epic_split_sources:
        print(f"\n  Epic split source : {[p.name for p in plan.epic_split_sources.values()]}")
    if plan.older_sprints:
        print(f"\n  Older sprints marked historical : {len(plan.older_sprints)}")
        for d in plan.older_sprints:
            print(f"    {d.relative_to(plan.project_root)}/.historical")
    if plan.warnings:
        print(f"\n  Warnings ({len(plan.warnings)}):")
        for w in plan.warnings:
            print(f"    [{w.kind}] {w.message}")
    if dry_run:
        print("\nNo files were written. Re-run without --dry-run to apply.")
    else:
        print(
            "\nMigration complete. Recommended next steps:\n"
            "  1. Review the migrated content under /docs/{product,design,architecture,testing}/.\n"
            "  2. Resolve any [anchor_heuristic] warnings (manual anchor insertion).\n"
            "  3. Resolve any [orphan_us] / [stories_without_epics] warnings (stories not\n"
            "     attached to an epic — recover manually from the backup if needed).\n"
            "  4. Resolve any [no_anchors] warning on design/design-system.md.\n"
            "  5. Verify id_counters in prism-config.md matches the high-water mark in your files.\n"
            "  6. Commit the migration. The precommit_living_truth hook blocks direct edits\n"
            "     to Living Truth files; for THIS one-time migration commit, bypass it:\n"
            "         git add docs/ prism-config.md\n"
            '         git commit --no-verify -m "chore(prism): migrate to 2.0.0 2-tier layout"\n'
            "     (Subsequent edits must go through proposals + seal_sprint — do not keep\n"
            "     using --no-verify.)\n"
            "  7. Once happy, delete the backup: docs.pre-migrate-* and prism-config.md.pre-migrate-*."
        )


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Migrate a PRISM 1.x project to the 2.0.0 2-tier nested Living Truth layout (Phase 7).",
    )
    parser.add_argument("--root", help="Project root (default: walk up from CWD)")
    parser.add_argument("--from-sprint", help="Override auto-detected latest sprint (format vN)")
    parser.add_argument("--dry-run", action="store_true", help="Plan + report; do not write")
    args = parser.parse_args()

    # Resolve project root
    if args.root:
        root = Path(args.root).resolve()
        if not (root / "prism-config.md").is_file():
            sys.stderr.write(f"ERROR: no prism-config.md at {root}\n")
            return 2
    else:
        root = find_project_root(Path.cwd())
        if root is None:
            sys.stderr.write("ERROR: prism-config.md not found (searched cwd and parents)\n")
            return 2

    docs_dir = root / "docs"
    if not docs_dir.is_dir():
        sys.stderr.write(f"ERROR: no docs/ folder at {root}\n")
        return 2

    # Refuse to migrate if already Phase 9
    if detect_phase9_already_migrated(docs_dir):
        sys.stderr.write(
            "ERROR: this project already has /docs/{product,design,architecture,testing}/ Living Truth files; "
            "it appears to already be migrated. Migration is a one-time operation.\n"
        )
        return 1

    # Resolve latest sprint
    if args.from_sprint:
        m = re.fullmatch(r"v(\d+)", args.from_sprint)
        if not m:
            sys.stderr.write(f"ERROR: --from-sprint must be 'vN' (got {args.from_sprint!r})\n")
            return 3
        latest = int(m.group(1))
    else:
        latest = detect_latest_sprint(docs_dir)
        if latest is None:
            sys.stderr.write("ERROR: no sprint-v{N}/ folders found in docs/; nothing to migrate\n")
            return 2

    timestamp = dt.datetime.now().strftime("%Y%m%d-%H%M%S")
    plan = build_plan(root, latest, timestamp)

    # Safety: both backup targets must not already exist (unless dry-run). Symmetric
    # check on both `docs.pre-migrate-*` and `prism-config.md.pre-migrate-*` so a
    # stale half-backup from a prior aborted run can't be silently overwritten.
    if not args.dry_run:
        if plan.backup_docs.exists():
            sys.stderr.write(f"ERROR: backup target already exists: {plan.backup_docs}\n")
            return 1
        if plan.backup_config.exists():
            sys.stderr.write(f"ERROR: backup target already exists: {plan.backup_config}\n")
            return 1

    try:
        execute_plan(plan, dry_run=args.dry_run)
    except Exception as e:
        sys.stderr.write(f"ERROR: migration failed mid-execution: {e}\n")
        if args.dry_run:
            sys.stderr.write("Dry-run aborted; no files were written.\n")
        else:
            sys.stderr.write(
                "Partial writes may exist under /docs/{product,design,architecture,testing}/.\n"
                "The backup is intact. The backup folder is a complete pre-migration copy\n"
                "of docs/, so the safe rollback is to swap docs/ with the backup:\n"
                f"  rm -rf {root}/docs\n"
                f"  cp -r {plan.backup_docs} {root}/docs\n"
                f"  cp {plan.backup_config} {root}/prism-config.md\n"
                "(Inspect the partial state under /docs/{product,design,architecture,testing}/ first\n"
                " if you want to keep anything before rolling back.)\n"
            )
        return 1

    report(plan, dry_run=args.dry_run)
    return 0


if __name__ == "__main__":
    sys.exit(main())
