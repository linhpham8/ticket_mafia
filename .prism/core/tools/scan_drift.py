#!/usr/bin/env python3
"""scan_drift.py — Phase 2.

Cross-sprint drift detector. Replaces the AI-procedural drift scan in
sprint-manager.md (per discussion doc §9.E "converge to Python helper").

Fires from two triggers:
  - `--trigger seal`: a sprint just sealed; check newer unsealed sprints
    for items that overlap the sealed sprint's Updated / Removed IDs.
  - `--trigger change-pack`: a same-sprint change pack was just approved;
    check newer unsealed sprints for items the pack touches.

Storage (Phase 2 design choice — see file docstring §):
  Drift warnings are persisted as per-sprint JSON sidecar files at:
      docs/sprint-vN/.drift-warnings.json
  Each entry: {emitted_at, source_sprint, source_event, affected_items, dismissed}.
  Rationale for sidecar over prism-config.md: per-sprint locality, atomic
  write without YAML comment-preservation complexity. Phase 4 may rationalize
  the storage if a centralized view is needed.

CLI:
  scan_drift.py --trigger seal --sprint vN [--project-root PATH] [--dry-run]
  scan_drift.py --trigger change-pack --pack PATH [--project-root PATH] [--dry-run]

Exit codes (per discussion doc §9.C):
  0 OK
  1 validation fail
  2 file not found
  3 config error
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import sys
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))
from apply_proposal import (  # noqa: E402
    PHASES,
    parse_frontmatter,
    split_proposal_sections,
)
from seal_sprint import (  # noqa: E402
    SPLIT_PROPOSAL_PATTERNS_BY_PHASE,
    collect_unrecognized_split_proposal_files,
)
from validate_proposal import (  # noqa: E402
    infer_expected_phase_from_path,
    infer_expected_target_prefixes_from_path,
    split_proposal_path_errors,
    validate,
)

SPRINT_DIR_RE = re.compile(r"^sprint-v(\d+)$")
DRIFT_SIDECAR_NAME = ".drift-warnings.json"
YAML_BLOCK_RE = re.compile(r"```yaml\n(.*?)\n```", re.DOTALL)


def find_project_root_from(start: Path) -> Path | None:
    p = start.resolve()
    for parent in [p] + list(p.parents):
        if (parent / "prism-config.md").is_file():
            return parent
    return None


def read_sealed_flags(project_root: Path) -> dict[int, bool]:
    """Return {sprint_number: sealed_flag} from prism-config.md sprints array.

    Sprints absent from the config are treated as unsealed (default).
    """
    config = project_root / "prism-config.md"
    if not config.is_file():
        raise ValueError("prism-config.md not found at project root")
    text = config.read_text(encoding="utf-8")
    m = YAML_BLOCK_RE.search(text)
    if not m:
        raise ValueError("no YAML code fence in prism-config.md")
    data = yaml.safe_load(m.group(1))
    if not isinstance(data, dict):
        raise ValueError("prism-config.md YAML did not parse to a mapping")
    sprints = data.get("sprints") or []
    out: dict[int, bool] = {}
    for entry in sprints:
        if not isinstance(entry, dict):
            continue
        sid = entry.get("id")
        if not isinstance(sid, str):
            continue
        sm = re.fullmatch(r"v(\d+)", sid)
        if not sm:
            continue
        out[int(sm.group(1))] = bool(entry.get("sealed", False))
    return out


def collect_affected_ids_from_sprint(project_root: Path, sprint_n: int) -> set[str]:
    """Read all approved proposals (across phases) in sprint-vN; collect Updated+Removed IDs.

    These are the IDs that the sprint seal merged into living truth and might affect
    newer sprints' proposals.
    """
    sprint_dir = project_root / "docs" / f"sprint-v{sprint_n}"
    if not sprint_dir.is_dir():
        return set()
    ids: set[str] = set()
    for phase in PHASES:
        phase_dir = sprint_dir / phase
        if not phase_dir.is_dir():
            continue
        proposals: list[Path] = []
        for pattern in SPLIT_PROPOSAL_PATTERNS_BY_PHASE.get(phase, []):
            proposals.extend(sorted(phase_dir.glob(pattern.format(N=sprint_n))))
        for proposal in proposals:
            try:
                fm, body = parse_frontmatter(proposal.read_text(encoding="utf-8"))
            except ValueError:
                continue
            if fm.get("status") != "APPROVED":
                continue
            sections = split_proposal_sections(body)
            for section_name in ("Updated", "Removed"):
                for aid, _ in sections.get(section_name, []):
                    ids.add(aid)
    return ids


def collect_affected_ids_from_pack(pack_dir: Path) -> set[str]:
    """Read all approved `*-delta-*.md` files in a change-pack dir; collect Updated+Removed IDs."""
    if not pack_dir.is_dir():
        return set()
    ids: set[str] = set()
    for delta in pack_dir.glob("*-delta-*.md"):
        # Only canonical delta filenames (matches seal_sprint.DELTA_FILE_RE) — ignore stray
        # `*-delta-*.md` files that seal would not merge.
        if not re.fullmatch(r"(product|design|architecture|testing)-delta-v\d+\.\d+\.\d+-.+\.md", delta.name):
            continue
        try:
            fm, body = parse_frontmatter(delta.read_text(encoding="utf-8"))
        except ValueError:
            continue
        if fm.get("status") != "APPROVED":
            continue
        sections = split_proposal_sections(body)
        for section_name in ("Updated", "Removed"):
            for aid, _ in sections.get(section_name, []):
                ids.add(aid)
    return ids


def proposal_ids_in_sprint(project_root: Path, sprint_n: int) -> set[str]:
    """Return ALL IDs referenced by any proposal (any section) in sprint-vN.

    Includes Sprint Brief / Notes? No — only the merge-impacting sections
    (New, Updated, Removed). New is included because a NEW item in a later
    sprint with the same ID as a Removed item in the source sprint is also
    drift-relevant (you can't NEW an ID that the source just deleted).

    Intentional asymmetry: this (newer/target) sprint does NOT filter by status — DRAFT
    proposals count too, so an overlap surfaces early as a warning. The source (sealing) sprint
    contributes only APPROVED items (see `collect_affected_ids_from_sprint`).
    """
    sprint_dir = project_root / "docs" / f"sprint-v{sprint_n}"
    if not sprint_dir.is_dir():
        return set()
    ids: set[str] = set()
    for phase in PHASES:
        phase_dir = sprint_dir / phase
        if not phase_dir.is_dir():
            continue
        proposals: list[Path] = []
        for pattern in SPLIT_PROPOSAL_PATTERNS_BY_PHASE.get(phase, []):
            proposals.extend(sorted(phase_dir.glob(pattern.format(N=sprint_n))))
        for proposal in proposals:
            try:
                _fm, body = parse_frontmatter(proposal.read_text(encoding="utf-8"))
            except ValueError:
                continue
            sections = split_proposal_sections(body)
            for section_name in ("New", "Updated", "Removed"):
                for aid, _ in sections.get(section_name, []):
                    ids.add(aid)
    return ids


def collect_unrecognized_split_proposals_in_scope(project_root: Path, source_sprint: int) -> list[Path]:
    """Return unknown canonical proposal files in source/newer unsealed scope."""
    sealed = read_sealed_flags(project_root)
    docs = project_root / "docs"
    if not docs.is_dir():
        return []
    unknown: list[Path] = []
    for sprint_dir in sorted(docs.iterdir()):
        m = SPRINT_DIR_RE.match(sprint_dir.name)
        if not m:
            continue
        n = int(m.group(1))
        if n < source_sprint or (n > source_sprint and sealed.get(n, False)):
            continue
        unknown.extend(collect_unrecognized_split_proposal_files(project_root, n))
    return sorted(unknown, key=lambda p: p.relative_to(project_root).as_posix())


def collect_invalid_split_proposal_paths_in_scope(
    project_root: Path,
    source_sprint: int,
) -> list[tuple[Path, str]]:
    """Return canonical split proposals with path or content contract blockers."""
    sealed = read_sealed_flags(project_root)
    docs = project_root / "docs"
    if not docs.is_dir():
        return []
    invalid: list[tuple[Path, str]] = []
    for sprint_dir in sorted(docs.iterdir()):
        m = SPRINT_DIR_RE.match(sprint_dir.name)
        if not m:
            continue
        n = int(m.group(1))
        if n < source_sprint or (n > source_sprint and sealed.get(n, False)):
            continue
        for phase in PHASES:
            phase_dir = sprint_dir / phase
            if not phase_dir.is_dir():
                continue
            proposals: list[Path] = []
            for pattern in SPLIT_PROPOSAL_PATTERNS_BY_PHASE.get(phase, []):
                proposals.extend(sorted(phase_dir.glob(pattern.format(N=n))))
            for proposal in proposals:
                path_errors = split_proposal_path_errors(proposal)
                if path_errors:
                    for error in path_errors:
                        invalid.append((proposal, error))
                    continue
                expected_prefixes, target_label = infer_expected_target_prefixes_from_path(proposal)
                report = validate(
                    proposal.read_text(encoding="utf-8"),
                    expected_phase=infer_expected_phase_from_path(proposal),
                    expected_target_prefixes=expected_prefixes,
                    target_label=target_label,
                    source_path=proposal,
                )
                for finding in report.blockers:
                    invalid.append((proposal, f"[{finding.rule}] {finding.message}"))
    return sorted(invalid, key=lambda kv: kv[0].relative_to(project_root).as_posix())


def _warning_identity(w: dict) -> tuple:
    """Stable identity for dedup: same source + same affected items = same warning."""
    return (
        w.get("source_sprint"),
        w.get("source_event"),
        tuple(sorted(w.get("affected_items") or [])),
    )


def write_warning(sprint_dir: Path, warning: dict, dry_run: bool) -> bool:
    """Persist `warning` to the sprint's drift sidecar.

    Returns True if the warning was newly written, False if a non-dismissed
    warning with the same identity (source_sprint, source_event, affected_items)
    already existed — caller can use this to avoid double-reporting on retry.
    """
    sidecar = sprint_dir / DRIFT_SIDECAR_NAME
    if sidecar.is_file():
        try:
            data = json.loads(sidecar.read_text(encoding="utf-8"))
            if not isinstance(data, dict) or not isinstance(data.get("warnings"), list):
                data = {"warnings": []}
        except json.JSONDecodeError:
            data = {"warnings": []}
    else:
        data = {"warnings": []}
    new_identity = _warning_identity(warning)
    for existing in data["warnings"]:
        if (
            isinstance(existing, dict)
            and _warning_identity(existing) == new_identity
            and not existing.get("dismissed")
        ):
            return False
    data["warnings"].append(warning)
    if dry_run:
        return True
    sprint_dir.mkdir(parents=True, exist_ok=True)
    tmp = sidecar.with_suffix(sidecar.suffix + ".tmp")
    tmp.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    tmp.replace(sidecar)
    return True


def scan(
    project_root: Path,
    source_sprint: int,
    source_event: str,
    affected_ids: set[str],
    dry_run: bool,
) -> list[dict]:
    """For each newer unsealed sprint, check overlap with `affected_ids`.
    Emits warnings; returns the list of emitted warning dicts.
    """
    sealed = read_sealed_flags(project_root)
    emitted: list[dict] = []
    if not affected_ids:
        return emitted

    docs = project_root / "docs"
    if not docs.is_dir():
        return emitted

    for sprint_dir in sorted(docs.iterdir()):
        m = SPRINT_DIR_RE.match(sprint_dir.name)
        if not m:
            continue
        target_n = int(m.group(1))
        if target_n <= source_sprint:
            continue
        if sealed.get(target_n, False):
            continue

        target_ids = proposal_ids_in_sprint(project_root, target_n)
        overlap = sorted(affected_ids & target_ids)
        if not overlap:
            continue

        warning = {
            "emitted_at": dt.datetime.now().strftime("%Y-%m-%d %H:%M"),
            "source_sprint": f"v{source_sprint}",
            "source_event": source_event,
            "affected_items": overlap,
            "dismissed": False,
        }
        if write_warning(sprint_dir, warning, dry_run):
            emitted.append({"target_sprint": f"v{target_n}", **warning})

    return emitted


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Detect cross-sprint drift and emit warnings (Phase 2).",
    )
    parser.add_argument("--trigger", choices=("seal", "change-pack"), required=True)
    parser.add_argument("--sprint", help="Source sprint version e.g. v3 (required for --trigger seal)")
    parser.add_argument("--pack", help="Path to change-pack dir (required for --trigger change-pack)")
    parser.add_argument(
        "--project-root", help="Project root containing prism-config.md (default: walk up)",
    )
    parser.add_argument("--dry-run", action="store_true", help="Compute + report; do not write sidecar files")
    args = parser.parse_args()

    root = Path(args.project_root) if args.project_root else find_project_root_from(Path.cwd())
    if root is None:
        sys.stderr.write("ERROR: project root not found (no prism-config.md in cwd or parents)\n")
        return 3

    try:
        sealed = read_sealed_flags(root)
    except ValueError as e:
        sys.stderr.write(f"ERROR: {e}\n")
        return 3
    _ = sealed  # consumed inside scan()

    if args.trigger == "seal":
        if not args.sprint:
            sys.stderr.write("ERROR: --sprint required for --trigger seal\n")
            return 1
        m = re.fullmatch(r"v(\d+)", args.sprint)
        if not m:
            sys.stderr.write(f"ERROR: --sprint must be format vN (got {args.sprint!r})\n")
            return 1
        source_n = int(m.group(1))
        affected = collect_affected_ids_from_sprint(root, source_n)
        source_event = "seal"
    else:
        if not args.pack:
            sys.stderr.write("ERROR: --pack required for --trigger change-pack\n")
            return 1
        pack_dir = Path(args.pack)
        if not pack_dir.is_absolute():
            pack_dir = (root / pack_dir).resolve()
        if not pack_dir.is_dir():
            sys.stderr.write(f"ERROR: change-pack dir not found: {pack_dir}\n")
            return 2
        # Derive source sprint number from path: .../docs/sprint-vN/changes/v.x.y.z-slug
        sm = re.search(r"sprint-v(\d+)", str(pack_dir))
        if not sm:
            sys.stderr.write(f"ERROR: cannot infer sprint from pack path: {pack_dir}\n")
            return 3
        source_n = int(sm.group(1))
        affected = collect_affected_ids_from_pack(pack_dir)
        source_event = f"change-pack {pack_dir.name}"

    unknown = collect_unrecognized_split_proposals_in_scope(root, source_n)
    if unknown:
        sys.stderr.write("ERROR: unrecognized split proposal file(s) under proposals/:\n")
        for path in unknown:
            sys.stderr.write(f"  - {path.relative_to(root)}\n")
        return 1
    invalid = collect_invalid_split_proposal_paths_in_scope(root, source_n)
    if invalid:
        sys.stderr.write("ERROR: invalid split proposal(s):\n")
        for path, error in invalid:
            sys.stderr.write(f"  - {path.relative_to(root)}: {error}\n")
        return 1

    emitted = scan(root, source_n, source_event, affected, args.dry_run)

    if not affected:
        print("No affected items from this trigger — nothing to scan.")
        return 0
    if not emitted:
        print(f"Scanned newer unsealed sprints — no drift detected. Affected items: {sorted(affected)}")
        return 0

    print(f"Drift detected for {len(emitted)} target sprint(s):")
    for w in emitted:
        affected_str = ", ".join(w["affected_items"])
        marker = " (dry-run, not written)" if args.dry_run else ""
        print(
            f"  → {w['target_sprint']}: overlap on [{affected_str}] from {w['source_event']} in {w['source_sprint']}{marker}"
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
