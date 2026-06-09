#!/usr/bin/env python3
"""effective_truth.py — Phase 2 production.

Compose the effective truth that AI loads as context: living truth + every
APPROVED split proposals from earlier unsealed sprints (Y < X) + the active
sprint's own approved proposals, applied in sprint order.

Per discussion doc §5.4 / §6.5. This script is read-only over living truth;
it writes nothing back to disk. Output goes to stdout (`md` format) or to
stdout as JSON (`--format json`).

Two modes:
  Explicit: --living PATH --proposals PATH... (caller controls order)
  Auto:     --phase PHASE [--up-to-sprint vN] [--project-root PATH]
            (enumerates proposals from prism-config.md sprints array)

CLI (per discussion doc §9.C):
  effective_truth.py --phase {product|design|architecture|testing|all}
                     [--up-to-sprint vN] [--project-root PATH]
                     [--format md|json]
  effective_truth.py --living PATH --proposals PATH1 [PATH2 ...]
                     [--format md|json]

Exit codes:
  0  OK
  1  validation fail (a proposal failed to apply)
  2  file not found
  3  config error (missing prism-config.md, malformed sprints array)
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))
from apply_proposal import (  # noqa: E402
    PHASES,
    apply,
    apply_multi_target,
    find_project_root,
    parse_frontmatter,
)
from seal_sprint import (  # noqa: E402
    LIVING_TO_TEMPLATE,
    collect_unrecognized_split_proposal_files,
    inject_indexes,
    render_living_from_template,
)
from seal_sprint import SPLIT_PROPOSAL_PATTERNS_BY_PHASE  # noqa: E402
from validate_proposal import (  # noqa: E402
    infer_expected_phase_from_path,
    infer_expected_target_prefixes_from_path,
    split_proposal_path_errors,
    validate,
)

YAML_BLOCK_RE = re.compile(r"```yaml\n(.*?)\n```", re.DOTALL)
SPRINT_DIR_RE = re.compile(r"^sprint-v(\d+)$")
# Phase 9: nested per-phase Living Truth layout. Each phase has multiple LT files; product
# additionally has dynamic epic files under `product/epics/EP-NNN-*.md` resolved at compose time.
PHASE_LIVING_FILES = {
    "product": (
        "product/prd.md",
        "product/glossary.md",
        "product/personas.md",
        "product/market-research.md",
    ),
    "design": ("design/design-system.md",),
    "architecture": (
        "architecture/architecture.md",
        "architecture/nfr.md",
        "architecture/sequence.md",
        "architecture/erd.md",
        "architecture/adr.md",
        "architecture/data-flow.md",
        "architecture/api-specs.md",
        "architecture/events.md",
        "architecture/project-reference.md",
    ),
    "testing": ("testing/test-cases.md",),
}


def discover_epic_files(project_root: Path) -> list[str]:
    """Return relative paths (under /docs/) for all epic files in product/epics/.

    Epic files are dynamic; effective_truth must compose them on demand.
    """
    epics_dir = project_root / "docs" / "product" / "epics"
    if not epics_dir.is_dir():
        return []
    out: list[str] = []
    for epic_file in sorted(epics_dir.iterdir()):
        if epic_file.is_file() and re.match(r"^EP-\d+-[a-z0-9-]+\.md$", epic_file.name):
            out.append(f"product/epics/{epic_file.name}")
    return out


def read_prism_config(config_path: Path) -> dict:
    full = config_path.read_text(encoding="utf-8")
    m = YAML_BLOCK_RE.search(full)
    if not m:
        raise ValueError("no YAML code fence in prism-config.md")
    data = yaml.safe_load(m.group(1))
    if not isinstance(data, dict):
        raise ValueError("prism-config.md YAML did not parse to a mapping")
    return data


def read_sealed_sprints(project_root: Path) -> set[int]:
    """Return the set of sprint numbers whose `sealed: true` in prism-config.md.

    Sealed sprints' proposals are NOT loaded by effective_truth — per
    `core/version-manager.md § Living Truth`, their content already lives in
    the Living Truth files. Returns empty set if config missing / malformed
    (callers fall back to treating all sprints as unsealed).
    """
    config = project_root / "prism-config.md"
    if not config.is_file():
        return set()
    try:
        data = read_prism_config(config)
    except ValueError:
        return set()
    sealed: set[int] = set()
    for entry in data.get("sprints") or []:
        if not isinstance(entry, dict):
            continue
        sid = entry.get("id")
        if not isinstance(sid, str):
            continue
        sm = re.fullmatch(r"v(\d+)", sid)
        if not sm:
            continue
        if entry.get("sealed", False):
            sealed.add(int(sm.group(1)))
    return sealed


def enumerate_proposals(
    project_root: Path,
    phase: str,
    up_to_sprint: int | None,
) -> list[Path]:
    """Return ordered list of approved proposal paths for the given phase.

    - Walks canonical split `docs/sprint-v*/<phase>/proposals/**/*-v*.md`.
    - Filters to those with status: APPROVED.
    - SKIPS sprints with `sealed: true` in prism-config.md (per
      `core/version-manager.md § Living Truth` — their content is already
      in Living Truth, re-applying would duplicate).
    - Sorts by sprint number ascending.
    - If `up_to_sprint` is provided, drops any sprint > that number.
    """
    docs = project_root / "docs"
    if not docs.is_dir():
        return []
    sealed = read_sealed_sprints(project_root)

    candidates: list[tuple[int, Path]] = []
    for sprint_dir in docs.iterdir():
        if not sprint_dir.is_dir():
            continue
        m = SPRINT_DIR_RE.match(sprint_dir.name)
        if not m:
            continue
        n = int(m.group(1))
        if up_to_sprint is not None and n > up_to_sprint:
            continue
        if n in sealed:
            continue
        proposal_paths: list[Path] = []
        phase_dir = sprint_dir / phase
        for pattern in SPLIT_PROPOSAL_PATTERNS_BY_PHASE.get(phase, []):
            proposal_paths.extend(sorted(phase_dir.glob(pattern.format(N=n))))

        for proposal in proposal_paths:
            if not proposal.is_file():
                continue
            try:
                fm, _ = parse_frontmatter(proposal.read_text(encoding="utf-8"))
            except ValueError:
                continue
            if fm.get("status") != "APPROVED":
                continue
            candidates.append((n, proposal))

    candidates.sort(key=lambda kv: kv[0])
    return [p for _n, p in candidates]


def enumerate_unrecognized_split_proposals(
    project_root: Path,
    phase: str,
    up_to_sprint: int | None,
) -> list[Path]:
    """Return proposal-looking files that canonical discovery would ignore."""
    docs = project_root / "docs"
    if not docs.is_dir():
        return []
    sealed = read_sealed_sprints(project_root)
    unknown: list[Path] = []
    for sprint_dir in docs.iterdir():
        if not sprint_dir.is_dir():
            continue
        m = SPRINT_DIR_RE.match(sprint_dir.name)
        if not m:
            continue
        n = int(m.group(1))
        if up_to_sprint is not None and n > up_to_sprint:
            continue
        if n in sealed:
            continue
        unknown.extend(collect_unrecognized_split_proposal_files(project_root, n, phase))
    return sorted(unknown, key=lambda p: p.relative_to(project_root).as_posix())


def enumerate_change_packs(
    project_root: Path,
    phase: str,
    up_to_sprint: int | None,
) -> list[Path]:
    """Return ordered approved `*-delta-v{X}.{Y}.{Z}-{slug}.md` files for the phase.

    Change packs live under `sprint-v{X}/changes/v{X}.{Y}.{Z}-{slug}/` and contain
    delta files following the same anchor format as proposals. Approval state is
    read from each delta's frontmatter (`status: APPROVED`).

    Phase-to-delta filename match (per `core/templates/delta-template.md`
    convention): the filename starts with `{phase}-delta-`.
    """
    docs = project_root / "docs"
    if not docs.is_dir():
        return []
    sealed = read_sealed_sprints(project_root)

    packs: list[tuple[tuple[int, int, int, str], Path]] = []
    for sprint_dir in sorted(docs.iterdir()):
        m = SPRINT_DIR_RE.match(sprint_dir.name)
        if not m:
            continue
        n = int(m.group(1))
        if up_to_sprint is not None and n > up_to_sprint:
            continue
        if n in sealed:
            continue
        changes_dir = sprint_dir / "changes"
        if not changes_dir.is_dir():
            continue
        for pack_dir in changes_dir.iterdir():
            if not pack_dir.is_dir():
                continue
            pm = re.match(r"^v(\d+)\.(\d+)\.(\d+)-(.+)$", pack_dir.name)
            if not pm:
                continue
            key = (int(pm.group(1)), int(pm.group(2)), int(pm.group(3)), pm.group(4))
            for delta in pack_dir.glob(f"{phase}-delta-*.md"):
                try:
                    fm, _ = parse_frontmatter(delta.read_text(encoding="utf-8"))
                except ValueError:
                    continue
                if fm.get("phase") != phase:
                    continue
                if fm.get("status") != "APPROVED":
                    continue
                packs.append((key, delta))

    packs.sort(key=lambda kv: kv[0])
    return [p for _k, p in packs]


def validate_source_contracts(project_root: Path, phase: str, sources: list[Path]) -> list[str]:
    """Return validation blocker strings for proposal/delta sources.

    Effective truth is a preview of the same content seal_sprint will merge, so
    it must enforce the same proposal contract before composing.
    """
    blockers: list[str] = []
    for source in sources:
        expected_prefixes, target_label = infer_expected_target_prefixes_from_path(source)
        report = validate(
            source.read_text(encoding="utf-8"),
            expected_phase=infer_expected_phase_from_path(source),
            expected_target_prefixes=expected_prefixes,
            target_label=target_label,
            source_path=source,
        )
        for finding in report.blockers:
            blockers.append(
                f"{source.relative_to(project_root)}: [{finding.rule}] {finding.message}"
            )
    return blockers


def compose(
    living_text: str,
    proposal_texts: list[str],
    verbose: bool = False,
) -> tuple[int, str]:
    current = living_text
    for idx, proposal_text in enumerate(proposal_texts, start=1):
        code, payload = apply(proposal_text, current, verbose=verbose)
        if code != 0:
            return code, f"proposal #{idx} failed:\n{payload}"
        current = payload
    return 0, current


def compose_multi_target(
    project_root: Path,
    phase: str,
    living_files: tuple[str, ...],
    source_paths: list[Path],
    verbose: bool = False,
) -> tuple[int, dict[Path, str] | str]:
    """Compose effective truth for a Phase 9 phase using the same router as seal.

    A single proposal can contain anchors for multiple Living Truth files, so
    composing each LT independently with the legacy single-target merger leaks
    every anchor into every file. This function keeps a per-target in-memory
    state and lets `apply_multi_target` route anchors by ID/tag.

    For sprint v1 before seal, root LT files may not exist yet because setup
    defers bootstrapping until seal. Effective truth is still needed by later
    phases, so missing root LT files are rendered into this in-memory state only.
    """
    state: dict[Path, str] = {}
    bootstrap_missing = should_bootstrap_missing_roots(project_root, source_paths)
    for living_name in living_files:
        living_path = project_root / "docs" / living_name
        if living_path.is_file():
            state[living_path] = living_path.read_text(encoding="utf-8")
        elif bootstrap_missing and living_name in LIVING_TO_TEMPLATE:
            rendered = render_living_from_template(living_path, project_root)
            if rendered is None:
                return 2, f"cannot bootstrap missing Living Truth in memory: {living_path}"
            state[living_path] = rendered
        else:
            sys.stderr.write(f"WARN: living truth not found, skipping: {living_path}\n")

    for idx, source in enumerate(source_paths, start=1):
        code, payload = apply_multi_target(
            source.read_text(encoding="utf-8"),
            project_root,
            project_name=project_root.name,
            current_state=state,
            verbose=verbose,
        )
        if isinstance(payload, str):
            return code, f"proposal #{idx} failed ({source.relative_to(project_root)}):\n{payload}"
        state.update(payload)

    # Parity with seal: regenerate `## Index` sections so the preview reflects the
    # combined (sealed + unsealed) anchored content, not a stale sealed-only index.
    inject_indexes(state, project_root)

    return 0, state


def compose_effective_state(
    project_root: Path,
    phases: tuple[str, ...],
    up_to: int | None = None,
) -> tuple[int, dict[Path, str] | str]:
    """Compose the merged (pre-seal) Living Truth state across `phases` into one dict.

    Returns (0, {living_path: merged_text}) or (code, error_message). This is the same
    in-memory merge seal performs, exposed so approve-time validators can check the
    EFFECTIVE truth (living + this sprint's approved proposals/deltas) without waiting
    for seal. Used by `validate_living_truth.py --effective` (LTV-COV at approve)."""
    merged: dict[Path, str] = {}
    for phase in phases:
        living_files: tuple[str, ...] = PHASE_LIVING_FILES.get(phase, ())
        if phase == "product":
            living_files = living_files + tuple(discover_epic_files(project_root))
        sources = (
            enumerate_proposals(project_root, phase, up_to)
            + enumerate_change_packs(project_root, phase, up_to)
        )
        code, payload = compose_multi_target(project_root, phase, living_files, sources)
        if isinstance(payload, str):
            return code, payload
        merged.update(payload)
    return 0, merged


def should_bootstrap_missing_roots(project_root: Path, source_paths: list[Path]) -> bool:
    """Return True when composing unsealed sprint-v1 proposals before LT bootstrap.

    Sealed sprint v1 means its content should already be on disk in Living Truth,
    so missing files remain warnings/errors. This function is intentionally
    conservative: it only enables in-memory bootstrap when a source is from v1.
    """
    if 1 in read_sealed_sprints(project_root):
        return False
    for source in source_paths:
        try:
            fm, _ = parse_frontmatter(source.read_text(encoding="utf-8"))
        except ValueError:
            continue
        sprint = fm.get("sprint")
        if sprint == 1 or sprint == "1":
            return True
        version = fm.get("version")
        if version == "v1":
            return True
        if any(part == "sprint-v1" for part in source.parts):
            return True
    return False


def main_auto(args: argparse.Namespace) -> int:
    project_root = Path(args.project_root) if args.project_root else find_project_root(Path.cwd())
    if project_root is None:
        sys.stderr.write("ERROR: project root not found (no prism-config.md in cwd or parents)\n")
        return 3
    config = project_root / "prism-config.md"
    if not config.is_file():
        sys.stderr.write(f"ERROR: prism-config.md not found at {config}\n")
        return 2

    up_to: int | None = None
    if args.up_to_sprint:
        m = re.fullmatch(r"v(\d+)", args.up_to_sprint)
        if not m:
            sys.stderr.write(f"ERROR: --up-to-sprint must be format vN (got {args.up_to_sprint!r})\n")
            return 3
        up_to = int(m.group(1))

    phases = list(PHASES) if args.phase == "all" else [args.phase]
    outputs: dict[str, dict] = {}
    for phase in phases:
        living_files: tuple[str, ...] = PHASE_LIVING_FILES.get(phase, ())
        # Phase 9: product phase additionally includes dynamic epic files.
        if phase == "product":
            living_files = living_files + tuple(discover_epic_files(project_root))
        unknown = enumerate_unrecognized_split_proposals(project_root, phase, up_to)
        if unknown:
            sys.stderr.write(
                f"[{phase}] ERROR: unrecognized split proposal file(s) under proposals/:\n"
            )
            for path in unknown:
                sys.stderr.write(f"  - {path.relative_to(project_root)}\n")
            return 1
        proposals = enumerate_proposals(project_root, phase, up_to)
        path_errors = [
            (path, error)
            for path in proposals
            for error in split_proposal_path_errors(path)
        ]
        if path_errors:
            sys.stderr.write(f"[{phase}] ERROR: invalid split proposal path(s):\n")
            for path, error in path_errors:
                sys.stderr.write(f"  - {path.relative_to(project_root)}: {error}\n")
            return 1
        change_packs = enumerate_change_packs(project_root, phase, up_to)
        sources = proposals + change_packs
        blockers = validate_source_contracts(project_root, phase, sources)
        if blockers:
            sys.stderr.write(f"[{phase}] ERROR: proposal validation blocker(s):\n")
            for blocker in blockers:
                sys.stderr.write(f"  - {blocker}\n")
            return 1
        applied_files = [str(p.relative_to(project_root)) for p in sources]
        code, payload = compose_multi_target(
            project_root,
            phase,
            living_files,
            sources,
            verbose=args.verbose,
        )
        if code != 0:
            sys.stderr.write(f"[{phase}] {payload}\n")
            return code
        assert isinstance(payload, dict)
        for living_path, content in sorted(
            payload.items(),
            key=lambda kv: kv[0].relative_to(project_root).as_posix(),
        ):
            try:
                living_name = living_path.relative_to(project_root / "docs").as_posix()
            except ValueError:
                living_name = living_path.relative_to(project_root).as_posix()
            outputs[f"{phase}:{living_name}"] = {
                "phase": phase,
                "living": str(living_path.relative_to(project_root)),
                "applied_proposals": applied_files,
                "content": content,
            }

    if args.format == "json":
        sys.stdout.write(json.dumps(list(outputs.values()), indent=2, ensure_ascii=False))
        sys.stdout.write("\n")
    else:
        if len(outputs) == 1:
            sys.stdout.write(next(iter(outputs.values()))["content"])
        else:
            for key, entry in outputs.items():
                sys.stdout.write(f"<!-- effective truth for {key} -->\n")
                sys.stdout.write(entry["content"])
                sys.stdout.write("\n")
    return 0


def main_explicit(args: argparse.Namespace) -> int:
    """Explicit single-file preview: apply the given proposals to ONE living file via the
    single-target merger. This intentionally does NOT do multi-target ID routing or regenerate
    the `## Index` — use `--phase` (auto mode) for output that matches what `seal_sprint.py`
    produces at seal.
    """
    living_path = Path(args.living)
    if not living_path.is_file():
        sys.stderr.write(f"ERROR: living truth not found: {living_path}\n")
        return 2
    proposal_texts: list[str] = []
    proposal_files: list[str] = []
    for p in args.proposals:
        pp = Path(p)
        if not pp.is_file():
            sys.stderr.write(f"ERROR: proposal not found: {pp}\n")
            return 2
        proposal_texts.append(pp.read_text(encoding="utf-8"))
        proposal_files.append(str(pp))

    living_text = living_path.read_text(encoding="utf-8")
    code, payload = compose(living_text, proposal_texts, verbose=args.verbose)
    if code != 0:
        sys.stderr.write(payload + "\n")
        return code

    if args.format == "json":
        out = {
            "phase": None,
            "living": str(living_path),
            "applied_proposals": proposal_files,
            "content": payload,
        }
        sys.stdout.write(json.dumps(out, indent=2, ensure_ascii=False))
        sys.stdout.write("\n")
    else:
        sys.stdout.write(payload)
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Compose effective truth from living + approved proposals (Phase 2 production).",
    )
    # Explicit mode
    parser.add_argument("--living", help="Path to living-truth markdown (explicit mode)")
    parser.add_argument(
        "--proposals", nargs="+",
        help="Ordered paths to approved proposal markdown files (explicit mode, earliest first)",
    )
    # Auto mode
    parser.add_argument(
        "--phase", choices=list(PHASES) + ["all"],
        help="Auto-enumerate proposals for this phase (auto mode)",
    )
    parser.add_argument("--up-to-sprint", help="Restrict auto-enumeration to sprints v1..vN")
    parser.add_argument(
        "--project-root", help="Project root containing prism-config.md (default: walk up from CWD)",
    )
    # Output / behavior
    parser.add_argument("--format", choices=("md", "json"), default="md")
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args()

    explicit = bool(args.living) or bool(args.proposals)
    auto = bool(args.phase)
    if explicit and auto:
        sys.stderr.write("ERROR: use either --living/--proposals OR --phase, not both\n")
        return 1
    if explicit and not (args.living and args.proposals):
        sys.stderr.write("ERROR: --living and --proposals must be specified together\n")
        return 1
    if not explicit and not auto:
        sys.stderr.write("ERROR: provide --living/--proposals OR --phase\n")
        return 1

    return main_auto(args) if auto else main_explicit(args)


if __name__ == "__main__":
    sys.exit(main())
