#!/usr/bin/env python3
"""seal_sprint.py — Phase 2 orchestrator.

Single trigger for the sprint seal event (`approve implement`). Performs in
order, per discussion doc §9.E:

  1. Pre-flight validate ALL proposals + change-pack deltas in the sprint
     (delegates to validate_proposal.py via import). Any blocker aborts.
  2. Multi-target atomic merge of approved proposals + approved change-pack
     deltas into the 15 Living Truth files (Phase 9 nested layout) +
     per-epic files. apply_proposal.apply_multi_target routes each anchored
     item by ID prefix to the correct LT file. All merges are computed
     in-memory first via current_state buffer; .tmp files are written;
     renames happen at the end. If any in-memory merge fails, no living
     file is touched.
  3. Create read-only snapshots `sprint-v{N}/snapshots/{name}-at-vN-sealed.md`
     (chmod 444) by byte-for-byte copy from the just-merged living files.
  4. Sync the sealing sprint's phase assets into Living Truth `docs/{phase}/assets/**`:
     copy `sprint-v{N}/{phase}/assets/**` (override on filename collision — the sprint
     folder keeps the historical copy) so the `assets/...` diagram/image references that
     merged into Living Truth resolve, then delete any path listed in that phase's
     `assets/.removed` manifest (idempotent; add+remove of the same path is a blocker).
  5. Set `sprints[].sealed = true` and `sprints[].sealed_at` in prism-config.md.
  6. Stamp `applied_to_living: true <commit-hash-placeholder>` in each
     proposal's / delta's frontmatter.
  7. Invoke scan_drift.py to emit cross-sprint drift warnings.
  8. Report the seal result.

CLI:
  seal_sprint.py --sprint vN [--project-root PATH] [--skip-drift-scan]
                 [--dry-run] [--verbose]

Exit codes:
  0  OK — sprint sealed
  1  validation fail (blocker findings, DRAFT change pack, missing test approval, etc.)
  2  file not found
  3  config error
"""

from __future__ import annotations

import argparse
import datetime as dt
import re
import shutil
import stat
import subprocess
import sys
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path, PurePosixPath

import yaml

try:
    import fcntl
except ImportError:  # pragma: no cover - exercised on Windows
    fcntl = None

try:
    import msvcrt
except ImportError:  # pragma: no cover - exercised on POSIX
    msvcrt = None

sys.path.insert(0, str(Path(__file__).resolve().parent))
from apply_proposal import (  # noqa: E402
    EPIC_FILE_RE,
    apply,
    extract_title_from_block,
    find_project_root,
    parse_anchored_blocks,
    parse_frontmatter,
    serialize,
    split_anchor_id,
)
from validate_proposal import (  # noqa: E402
    infer_expected_phase_from_path,
    infer_expected_target_prefixes_from_path,
    validate,
)


YAML_BLOCK_RE = re.compile(r"(```yaml\n)(.*?)(\n```)", re.DOTALL)
DELTA_FILE_RE = re.compile(r"^(product|design|architecture|testing)-delta-v\d+\.\d+\.\d+-.+\.md$")
CHANGE_PACK_DIR_RE = re.compile(r"^v\d+\.\d+\.\d+-.+$")

# Phase 9: nested per-phase Living Truth layout.
# Split-proposal rollout: canonical sprint deltas live under `<phase>/proposals/`
# by Living Truth target.


def lock_file(file_obj, *, nonblocking: bool = False) -> None:
    if fcntl is not None:
        flags = fcntl.LOCK_EX | (fcntl.LOCK_NB if nonblocking else 0)
        fcntl.flock(file_obj.fileno(), flags)
        return
    if msvcrt is not None:
        file_obj.seek(0)
        mode = msvcrt.LK_NBLCK if nonblocking else msvcrt.LK_LOCK
        try:
            msvcrt.locking(file_obj.fileno(), mode, 1)
        except OSError as e:
            if nonblocking:
                raise BlockingIOError(str(e)) from e
            raise
        return
    raise RuntimeError("no supported file locking API found")


def unlock_file(file_obj) -> None:
    if fcntl is not None:
        fcntl.flock(file_obj.fileno(), fcntl.LOCK_UN)
        return
    if msvcrt is not None:
        file_obj.seek(0)
        msvcrt.locking(file_obj.fileno(), msvcrt.LK_UNLCK, 1)

# Phase → list of root LT file relative paths under /docs/
PHASE_TO_LIVING_FILES = {
    "product": [
        "product/prd.md",
        "product/glossary.md",
        "product/personas.md",
        "product/market-research.md",
        # epic files (`product/epics/EP-NNN-*.md`) are dynamic — discovered at seal time
    ],
    "design": ["design/design-system.md"],
    "architecture": [
        "architecture/architecture.md",
        "architecture/nfr.md",
        "architecture/sequence.md",
        "architecture/erd.md",
        "architecture/adr.md",
        "architecture/data-flow.md",
        "architecture/api-specs.md",
        "architecture/events.md",
        "architecture/project-reference.md",
    ],
    "testing": ["testing/test-cases.md"],
}

# Canonical split proposal files, ordered to keep merge/effective-truth output deterministic.
# Glob entries are relative to `docs/sprint-v{N}/{phase}/`.
SPLIT_PROPOSAL_PATTERNS_BY_PHASE = {
    "product": [
        "proposals/prd-v{N}.md",
        "proposals/glossary-v{N}.md",
        "proposals/personas-v{N}.md",
        "proposals/market-research-v{N}.md",
        "proposals/epics/*-v{N}.md",
    ],
    "design": [
        "proposals/design-system-v{N}.md",
    ],
    "architecture": [
        "proposals/architecture-v{N}.md",
        "proposals/nfr-v{N}.md",
        "proposals/sequence-v{N}.md",
        "proposals/erd-v{N}.md",
        "proposals/adr-v{N}.md",
        "proposals/data-flow-v{N}.md",
        "proposals/api-specs-v{N}.md",
        "proposals/events-v{N}.md",
        "proposals/project-reference-v{N}.md",
    ],
    "testing": [
        "proposals/test-cases-v{N}.md",
    ],
}

# Delta file primary target (same per-phase mapping as proposal primary).
DELTA_TO_LIVING = {
    "product": "product/prd.md",
    "design": "design/design-system.md",
    "architecture": "architecture/architecture.md",
    "testing": "testing/test-cases.md",
}

# Living Truth assets: each phase keeps editable diagram/image sources (Draw.io / XML
# C4 + DFD, wireframe PNGs, PDFs) next to its markdown. The `assets/...` paths that
# proposals reference are written relative to the Living Truth file (vd
# `architecture.md` → `assets/c4-model.drawio` = `docs/architecture/assets/c4-model.drawio`),
# but the source files live under the sprint folder until seal. At seal we mirror the
# sealing sprint's `{phase}/assets/**` into `docs/{phase}/assets/**` so those references
# resolve. Phases match the canonical Living Truth phase folders.
ASSET_PHASES = ("product", "design", "architecture", "testing")

# Asset removal manifest. A sprint deletes an asset from Living Truth by listing its
# path (relative to `docs/<phase>/assets/`) in `docs/sprint-v{N}/<phase>/assets/.removed`
# — one path per line; blank lines and `#` comments ignored. The manifest itself is never
# copied into Living Truth. Removal is additive-aware: only the listed paths are deleted,
# everything else carried over from earlier sprints is preserved.
ASSET_REMOVAL_MANIFEST = ".removed"

# v1 bootstrap: 15 root LT files scaffold from their templates atomically.
# Epic files (`product/epics/EP-NNN-*.md`) bootstrap on-demand by apply_proposal
# when a `## New` section has `<!-- ID: EP-NNN -->`.
LIVING_TO_TEMPLATE = {
    "product/prd.md": "prd-template.md",
    "product/glossary.md": "glossary-template.md",
    "product/personas.md": "personas-template.md",
    "product/market-research.md": "market-research-template.md",
    "design/design-system.md": "design-template.md",
    "architecture/architecture.md": "architecture-template.md",
    "architecture/nfr.md": "nfr-template.md",
    "architecture/sequence.md": "sequence-template.md",
    "architecture/erd.md": "erd-template.md",
    "architecture/adr.md": "adr-template.md",
    "architecture/data-flow.md": "data-flow-template.md",
    "architecture/api-specs.md": "api-specs-template.md",
    "architecture/events.md": "events-template.md",
    "architecture/project-reference.md": "project-reference-template.md",
    "testing/test-cases.md": "test-cases-template.md",
}


# Living Truth bootstrap sentinel. Authoring templates (`core/templates/*-template.md`)
# are dual-purpose: above this marker is the sprint-agnostic LT skeleton (frontmatter,
# title, anchor-convention note); below it is authoring guidance only — example anchored
# blocks, narrative-placeholder sections, and the Self-Review Checklist. That guidance must
# NOT seed Living Truth: example anchors use the literal `-NNN` placeholder (not a valid
# `-\d+` anchor) so they fall into the preamble and the merge never touches them, freezing
# `{{...}}` junk into LT forever. When bootstrapping an LT file we keep only the skeleton.
LT_SKELETON_SENTINEL = "<!-- PRISM:LT-SKELETON-END -->"
HTML_COMMENT_EXAMPLE_RE = re.compile(
    r"<!--\s*(ID|EPIC|US|VERIFIES):\s*([A-Z0-9-]+(?:-[A-Z0-9]+)*|\.\.\.)\s*-->"
)


def _strip_below_skeleton_sentinel(text: str) -> str:
    """Keep only the LT skeleton region above `LT_SKELETON_SENTINEL`.

    Returns `text` unchanged when the marker is absent (safe fallback so a template that
    has not yet been annotated still bootstraps, just without the strip).
    """
    idx = text.find(LT_SKELETON_SENTINEL)
    if idx == -1:
        return text
    return text[:idx].rstrip() + "\n"


def _escape_html_comment_examples(text: str) -> str:
    """Escape literal PRISM comment examples inside LT skeleton prose.

    HTML comments do not nest. A skeleton comment that says ``use `<!-- ID: ... -->` ``
    is rendered incorrectly by Markdown preview because the inner ``-->`` closes
    the outer comment early. Living Truth must keep real anchors raw, but prose
    examples inside the skeleton should be escaped.
    """
    return HTML_COMMENT_EXAMPLE_RE.sub(
        lambda m: f"&lt;!-- {m.group(1)}: {m.group(2)} --&gt;",
        text,
    )


def _strip_sprint_bound_frontmatter(text: str) -> str:
    """Strip sprint-bound fields (`version:`, `sprint:`, `phase:`) from a template's
    YAML frontmatter when materializing a Living Truth file.

    Templates are dual-purpose: they scaffold sprint-agnostic LT files (guided
    mode, via `bootstrap_living_from_template`) and per-sprint freedom-mode
    files (which keep version/sprint/phase). When copying for LT we drop those
    fields so the LT file does not freeze a misleading `sprint: 1` marker that
    no tool reads but readers may misinterpret. Placeholder `created` / `updated`
    values are also dropped; Living Truth history is carried by seal snapshots
    and proposal metadata, not template date placeholders.
    """
    if not text.startswith("---\n"):
        return text
    end = text.find("\n---", 4)
    if end == -1:
        return text
    fm_block = text[4:end]
    body = text[end:]
    kept_lines = []
    for line in fm_block.split("\n"):
        stripped = line.lstrip()
        if (
            stripped.startswith("version:")
            or stripped.startswith("sprint:")
            or stripped.startswith("phase:")
            or stripped == "created: YYYY-MM-DD"
            or stripped == "updated: YYYY-MM-DD HH:MM"
        ):
            continue
        kept_lines.append(line)
    return "---\n" + "\n".join(kept_lines) + body


def bootstrap_living_from_template(living: Path, project_root: Path, sprint_n: int) -> bool:
    """Create `living` from its template when missing and `sprint_n == 1`.
    Returns True if a file was scaffolded, False if not eligible (sprint > 1,
    no template mapping, template not on disk).

    Phase 9: looks up by relative path (e.g. `product/prd.md`) not basename.
    LT frontmatter is normalized via `_strip_sprint_bound_frontmatter` so the
    resulting LT file does not carry sprint-bound `version`/`sprint`/`phase`
    fields that templates keep for freedom-mode per-sprint reuse.
    """
    if sprint_n != 1 or living.exists():
        return False
    text = render_living_from_template(living, project_root)
    if text is None:
        return False
    living.parent.mkdir(parents=True, exist_ok=True)
    living.write_text(text, encoding="utf-8")
    return True


def render_living_from_template(living: Path, project_root: Path) -> str | None:
    """Return scaffold text for a missing root LT file, or None if not templated."""
    try:
        rel_key = living.relative_to(project_root / "docs").as_posix()
    except ValueError:
        return None
    template_name = LIVING_TO_TEMPLATE.get(rel_key)
    if template_name is None:
        return None
    template_path = Path(__file__).resolve().parent.parent / "templates" / template_name
    if not template_path.is_file():
        return None
    text = template_path.read_text(encoding="utf-8")
    text = text.replace("{{PROJECT_NAME}}", project_root.name)
    text = text.replace("{{TÊN_DỰ_ÁN}}", project_root.name)
    text = _strip_below_skeleton_sentinel(text)
    text = _escape_html_comment_examples(text)
    return _strip_sprint_bound_frontmatter(text)


def plan_all_living_v1_bootstrap(project_root: Path, sprint_n: int) -> dict[Path, str]:
    """Return missing v1 root LT scaffold content without writing files.

    seal_sprint keeps this in the same in-memory merge buffer as proposal
    output, so dry-run and failed merge attempts leave the project tree
    untouched.
    """
    if sprint_n != 1:
        return {}
    templates_dir = Path(__file__).resolve().parent.parent / "templates"
    missing_templates: list[str] = []
    for rel_path, template_name in LIVING_TO_TEMPLATE.items():
        template_path = templates_dir / template_name
        living = project_root / "docs" / rel_path
        if not template_path.is_file() and not living.exists():
            missing_templates.append(template_name)
    if missing_templates:
        raise FileNotFoundError(
            f"cannot bootstrap v1 Living Truth: templates missing: {missing_templates}"
        )

    planned: dict[Path, str] = {}
    for rel_path in LIVING_TO_TEMPLATE:
        living = project_root / "docs" / rel_path
        if living.exists():
            continue
        text = render_living_from_template(living, project_root)
        if text is not None:
            planned[living] = text
    return planned


def bootstrap_all_living_v1(project_root: Path, sprint_n: int) -> list[Path]:
    """At sprint v1, scaffold ALL 15 root LT files atomically.

    Returns list of files actually scaffolded (files already present are skipped).
    Atomicity: if any template missing on disk, raises before touching anything.
    """
    if sprint_n != 1:
        return []
    templates_dir = Path(__file__).resolve().parent.parent / "templates"
    # Pre-flight: verify all templates exist before any write.
    missing_templates: list[str] = []
    for rel_path, template_name in LIVING_TO_TEMPLATE.items():
        template_path = templates_dir / template_name
        if not template_path.is_file():
            living = project_root / "docs" / rel_path
            if not living.exists():
                missing_templates.append(template_name)
    if missing_templates:
        raise FileNotFoundError(
            f"cannot bootstrap v1 Living Truth: templates missing: {missing_templates}"
        )
    scaffolded: list[Path] = []
    for rel_path in LIVING_TO_TEMPLATE:
        living = project_root / "docs" / rel_path
        if bootstrap_living_from_template(living, project_root, sprint_n):
            scaffolded.append(living)
    return scaffolded


def discover_snapshot_living_paths(project_root: Path, pending_state: dict[Path, str]) -> list[Path]:
    """Return all Living Truth paths that should be snapshotted at seal time."""
    paths = {project_root / "docs" / rel for rel in LIVING_TO_TEMPLATE}
    epics_dir = project_root / "docs" / "product" / "epics"
    if epics_dir.is_dir():
        paths.update(p for p in epics_dir.iterdir() if p.is_file() and EPIC_FILE_RE.match(p.name))
    paths.update(pending_state.keys())
    return sorted(
        (p for p in paths if p.exists() or p in pending_state),
        key=lambda p: p.relative_to(project_root).as_posix(),
    )


def write_living_files_atomically(merged_text: dict[Path, str]) -> None:
    """Write Living Truth files with rollback if any replace step fails.

    Each individual `Path.replace` is atomic, but a multi-file seal is only
    all-or-nothing if we restore files already replaced when a later replace
    fails. This helper keeps original bytes + mode in memory, writes all tmp
    files first, then commits. On any exception, it removes new files and
    restores previous file contents before re-raising.
    """
    originals: dict[Path, tuple[bool, bytes | None, int | None]] = {}
    tmp_paths: dict[Path, Path] = {}

    try:
        for living, text in merged_text.items():
            living.parent.mkdir(parents=True, exist_ok=True)
            if living.exists() and living.is_file():
                originals[living] = (
                    True,
                    living.read_bytes(),
                    stat.S_IMODE(living.stat().st_mode),
                )
            else:
                originals[living] = (False, None, None)
            tmp = living.with_suffix(living.suffix + ".tmp")
            tmp.write_text(text, encoding="utf-8")
            tmp_paths[living] = tmp

        for living, tmp in tmp_paths.items():
            tmp.replace(living)
    except Exception:
        for _living, tmp in tmp_paths.items():
            if tmp.exists():
                try:
                    tmp.unlink()
                except OSError:
                    pass
        for living, (existed, content, mode) in originals.items():
            try:
                if existed:
                    assert content is not None
                    living.parent.mkdir(parents=True, exist_ok=True)
                    living.write_bytes(content)
                    if mode is not None:
                        living.chmod(mode)
                elif living.exists() and living.is_file():
                    living.unlink()
            except OSError:
                pass
        raise


@dataclass
class FileState:
    existed: bool
    content: bytes | None
    mode: int | None


def capture_file_states(paths: list[Path]) -> dict[Path, FileState]:
    """Capture file bytes + mode for rollback across the full seal event."""
    states: dict[Path, FileState] = {}
    for path in paths:
        if path in states:
            continue
        if path.exists() and path.is_file():
            states[path] = FileState(
                existed=True,
                content=path.read_bytes(),
                mode=stat.S_IMODE(path.stat().st_mode),
            )
        else:
            states[path] = FileState(existed=False, content=None, mode=None)
    return states


def restore_file_states(states: dict[Path, FileState]) -> None:
    """Best-effort rollback for files touched after merge planning.

    Paths absent before the seal are removed. Existing paths are restored with
    their previous bytes and mode. Parent directories are intentionally left in
    place; empty directory cleanup is cosmetic and not worth risking rollback.
    """
    for path, state in states.items():
        try:
            if state.existed:
                assert state.content is not None
                path.parent.mkdir(parents=True, exist_ok=True)
                if path.exists():
                    try:
                        path.chmod(stat.S_IWUSR | stat.S_IRUSR)
                    except OSError:
                        pass
                path.write_bytes(state.content)
                if state.mode is not None:
                    path.chmod(state.mode)
            elif path.exists() and path.is_file():
                try:
                    path.chmod(stat.S_IWUSR | stat.S_IRUSR)
                except OSError:
                    pass
                path.unlink()
        except OSError:
            pass


def snapshot_path_for_living(living: Path, project_root: Path, sprint_n: int) -> Path:
    """Return the Phase 9 nested snapshot path for one Living Truth file."""
    snap_root = project_root / "docs" / f"sprint-v{sprint_n}" / "snapshots"
    try:
        rel = living.relative_to(project_root / "docs")
    except ValueError:
        rel = Path(living.name)
    return snap_root / rel.parent / f"{rel.stem}-at-v{sprint_n}-sealed.md"


@dataclass
class MergePlan:
    """A single (source markdown, living target) merge step."""
    source: Path
    living: Path
    kind: str  # "proposal" | "delta"


@contextmanager
def sprint_seal_lock(root: Path, sprint_n: int):
    """Exclusive file lock so only one seal_sprint process can run at a time per
    project. Non-blocking acquire — if the lock is held, exit immediately with
    a clear error rather than queuing behind a stalled prior run.
    """
    lock_path = root / "prism-config.md.seal.lock"
    f = open(lock_path, "a+")
    try:
        try:
            lock_file(f, nonblocking=True)
        except BlockingIOError as e:
            f.close()
            raise RuntimeError(
                f"another seal_sprint process is already running for project {root} "
                f"(lock held on {lock_path}); refusing to start a concurrent seal"
            ) from e
        try:
            yield
        finally:
            unlock_file(f)
    finally:
        if not f.closed:
            f.close()


def parse_sprint_arg(s: str) -> int:
    m = re.fullmatch(r"v(\d+)", s)
    if not m:
        raise ValueError(f"--sprint must be format vN (got {s!r})")
    return int(m.group(1))


def read_config_yaml(config_path: Path) -> tuple[dict, str, str]:
    full = config_path.read_text(encoding="utf-8")
    m = YAML_BLOCK_RE.search(full)
    if not m:
        raise ValueError("no YAML code fence in prism-config.md")
    data = yaml.safe_load(m.group(2))
    if not isinstance(data, dict):
        raise ValueError("prism-config.md YAML did not parse to a mapping")
    return data, full, m.group(2)


def check_sprint_sealable(data: dict, sprint_n: int) -> str | None:
    """Return None if sprint is sealable, else a human-readable blocker reason.

    Checks (per `core/sprint-manager.md`):
    1. Sprint must be declared in `sprints` array.
    2. Sprint must not already be sealed.
    3. All earlier sprints (v{Y} where Y < sprint_n) MUST already be sealed —
       sealing skipping a sprint would break the Living Truth chain and the
       Plan Gate in sprint-manager.md. seal_sprint enforces this defensively
       even though the orchestrator should refuse `approve implement` earlier.
    """
    sprints = data.get("sprints") or []
    target = None
    unsealed_earlier: list[str] = []
    for entry in sprints:
        if not isinstance(entry, dict):
            continue
        sid = entry.get("id")
        if not isinstance(sid, str):
            continue
        sm = re.fullmatch(r"v(\d+)", sid)
        if not sm:
            continue
        n = int(sm.group(1))
        if n == sprint_n:
            target = entry
        elif n < sprint_n and not entry.get("sealed", False):
            unsealed_earlier.append(sid)
    if target is None:
        return f"sprint v{sprint_n} not declared in prism-config.md sprints array"
    if target.get("sealed", False):
        return f"sprint v{sprint_n} is already sealed"
    if unsealed_earlier:
        return (
            f"cannot seal sprint v{sprint_n}: earlier sprint(s) still unsealed: "
            f"{', '.join(unsealed_earlier)}. Seal them in order (oldest first)"
        )
    return None


def collect_proposals(project_root: Path, sprint_n: int) -> list[Path]:
    """Return all proposal markdown files for the sprint, ordered by phase and target.

    Supports canonical split `<phase>/proposals/*-vN.md` files only.
    """
    sprint_dir = project_root / "docs" / f"sprint-v{sprint_n}"
    found: list[Path] = []
    for phase in SPLIT_PROPOSAL_PATTERNS_BY_PHASE:
        for pattern in SPLIT_PROPOSAL_PATTERNS_BY_PHASE.get(phase, []):
            matches = sorted((sprint_dir / phase).glob(pattern.format(N=sprint_n)))
            found.extend(p for p in matches if p.is_file())
    return found


def collect_unrecognized_split_proposal_files(
    project_root: Path,
    sprint_n: int,
    phase: str | None = None,
) -> list[Path]:
    """Return `.md` files under canonical `proposals/` folders not discovered.

    Without this guard, a typo like `api-spec-v2.md` could look like a proposal
    to a reviewer while being ignored by seal/effective-truth/drift scans.
    """
    sprint_dir = project_root / "docs" / f"sprint-v{sprint_n}"
    phases = [phase] if phase is not None else list(SPLIT_PROPOSAL_PATTERNS_BY_PHASE)
    unknown: list[Path] = []
    for ph in phases:
        phase_dir = sprint_dir / ph
        proposals_dir = phase_dir / "proposals"
        if not proposals_dir.is_dir():
            continue
        recognized: set[Path] = set()
        for pattern in SPLIT_PROPOSAL_PATTERNS_BY_PHASE.get(ph, []):
            recognized.update(
                p for p in phase_dir.glob(pattern.format(N=sprint_n)) if p.is_file()
            )
        for candidate in sorted(proposals_dir.rglob("*.md")):
            if candidate.is_file() and candidate not in recognized:
                unknown.append(candidate)
    return unknown


def collect_delta_files(project_root: Path, sprint_n: int) -> list[Path]:
    """Return all change-pack delta files for the sprint, ordered by pack version then phase."""
    changes_dir = project_root / "docs" / f"sprint-v{sprint_n}" / "changes"
    if not changes_dir.is_dir():
        return []
    out: list[tuple[tuple[int, int, int, str], Path]] = []
    for pack_dir in sorted(changes_dir.iterdir()):
        if not pack_dir.is_dir() or not CHANGE_PACK_DIR_RE.match(pack_dir.name):
            continue
        pm = re.match(r"^v(\d+)\.(\d+)\.(\d+)-(.+)$", pack_dir.name)
        assert pm is not None
        key = (int(pm.group(1)), int(pm.group(2)), int(pm.group(3)), pm.group(4))
        for delta in sorted(pack_dir.iterdir()):
            if DELTA_FILE_RE.match(delta.name):
                out.append((key, delta))
    out.sort(key=lambda kv: kv[0])
    return [p for _k, p in out]


def collect_asset_copies(project_root: Path, sprint_n: int) -> list[tuple[Path, Path]]:
    """Return (source, destination) pairs for every asset file this seal copies into
    Living Truth.

    Source: `docs/sprint-v{N}/{phase}/assets/**` (the canonical per-phase asset store).
    Destination: `docs/{phase}/assets/**`, preserving the relative sub-path so nested
    layouts (vd `assets/dfd/checkout.drawio.xml`) land in the same shape.

    Override semantics: a destination that already exists (from an earlier sprint) is
    overwritten at copy time — the sprint folder keeps the historical copy, so Living
    Truth always reflects the newest source. Living Truth assets from earlier sprints not
    present in this sprint are left untouched (additive across sprints; asset *removal* is
    not modeled here). Only the canonical phase-root `assets/` folder is mirrored;
    large-project domain sub-folder assets (`{phase}/domain-*/assets/`) are working
    context per `core/context-strategy.md` and stay sprint-local.
    """
    pairs: list[tuple[Path, Path]] = []
    seen: set[Path] = set()
    for phase in ASSET_PHASES:
        src_root = project_root / "docs" / f"sprint-v{sprint_n}" / phase / "assets"
        if not src_root.is_dir():
            continue
        dest_root = project_root / "docs" / phase / "assets"
        for src in sorted(src_root.rglob("*")):
            if not src.is_file():
                continue
            if src.name == ASSET_REMOVAL_MANIFEST:
                continue  # the `.removed` manifest drives deletion; never copy it into LT
            dest = dest_root / src.relative_to(src_root)
            if dest in seen:
                continue
            seen.add(dest)
            pairs.append((src, dest))
    return pairs


def copy_assets_into_living(asset_copies: list[tuple[Path, Path]]) -> None:
    """Copy each (source, destination) asset pair into Living Truth, overwriting on
    collision. Clears a read-only bit on an existing destination first (a prior tool run
    may have left one). The caller captures destination states beforehand so a later seal
    failure rolls these copies back with the rest of the seal event.
    """
    for src, dest in asset_copies:
        dest.parent.mkdir(parents=True, exist_ok=True)
        if dest.exists():
            try:
                dest.chmod(stat.S_IWUSR | stat.S_IRUSR)
            except OSError:
                pass
        shutil.copy2(src, dest)


def parse_asset_removal_manifest(text: str) -> list[str]:
    """Return the relative asset paths listed in a `.removed` manifest.

    One path per line; blank lines and `#` comments (after optional leading whitespace)
    are ignored. An inline ` #` comment is NOT stripped — filenames may legitimately
    contain `#`, so only whole-line comments are recognized. Backslashes are normalized to
    `/` and a leading `/` is trimmed for consistent matching against the assets folder.
    """
    paths: list[str] = []
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        paths.append(line.replace("\\", "/").lstrip("/"))
    return paths


def collect_asset_removals(project_root: Path, sprint_n: int) -> list[tuple[str, str, Path]]:
    """Return (phase, rel_path, living_dest) for every asset a phase `.removed` manifest
    lists for deletion from Living Truth.

    Manifest path: `docs/sprint-v{N}/<phase>/assets/.removed`. Each listed path is relative
    to `docs/<phase>/assets/`. Path validity (no traversal, no add/remove conflict) is
    checked separately by `validate_asset_removals` before any deletion runs.
    """
    removals: list[tuple[str, str, Path]] = []
    seen: set[Path] = set()
    for phase in ASSET_PHASES:
        manifest = (
            project_root / "docs" / f"sprint-v{sprint_n}" / phase / "assets" / ASSET_REMOVAL_MANIFEST
        )
        if not manifest.is_file():
            continue
        dest_root = project_root / "docs" / phase / "assets"
        for rel in parse_asset_removal_manifest(manifest.read_text(encoding="utf-8")):
            dest = dest_root / rel
            if dest in seen:
                continue
            seen.add(dest)
            removals.append((phase, rel, dest))
    return removals


def validate_asset_removals(
    asset_removals: list[tuple[str, str, Path]],
    asset_copies: list[tuple[Path, Path]],
    sprint_n: int,
) -> list[str]:
    """Return blocker messages for an invalid `.removed` manifest.

    Blocks when a listed path escapes its phase `assets/` folder (absolute or `..`
    traversal), or when the same path is both present in the sprint (would be copied) and
    listed for removal in the same seal — an ambiguous add+remove.
    """
    blockers: list[str] = []
    copy_dests = {dest for _src, dest in asset_copies}
    for phase, rel, dest in asset_removals:
        manifest_rel = f"docs/sprint-v{sprint_n}/{phase}/assets/{ASSET_REMOVAL_MANIFEST}"
        rel_pp = PurePosixPath(rel)
        if not rel or rel_pp.is_absolute() or ".." in rel_pp.parts:
            blockers.append(f"{manifest_rel}: path escapes the assets folder: {rel!r}")
            continue
        if dest in copy_dests:
            blockers.append(
                f"{manifest_rel}: '{rel}' is both present in the sprint and listed for "
                "removal — drop one (a sprint cannot add and remove the same asset)"
            )
    return blockers


def remove_assets_from_living(
    asset_removals: list[tuple[str, str, Path]],
) -> tuple[list[Path], list[Path]]:
    """Delete each listed Living Truth asset file. Returns (removed, missing) dest paths.

    Idempotent: a path already absent from Living Truth (earlier sprint removed it, or a
    typo) is reported as `missing`, not an error. Only regular files are deleted; a path
    that resolves to a directory is treated as missing. Caller captures these dests for
    rollback before invoking this.
    """
    removed: list[Path] = []
    missing: list[Path] = []
    for _phase, _rel, dest in asset_removals:
        if dest.is_file():
            try:
                dest.chmod(stat.S_IWUSR | stat.S_IRUSR)
            except OSError:
                pass
            dest.unlink()
            removed.append(dest)
        else:
            missing.append(dest)
    return removed, missing


def derive_living_for(source: Path, project_root: Path) -> Path | None:
    """Resolve which primary Living Truth file a change-pack delta merges into."""
    name = source.name
    # delta under sprint-vN/changes/v.x.y.z-slug/<phase>-delta-...
    m = re.match(r"^(product|design|architecture|testing)-delta-v\d+\.\d+\.\d+-.+\.md$", name)
    if m:
        phase = m.group(1)
        return project_root / "docs" / DELTA_TO_LIVING[phase]
    return None


def status_of(source: Path) -> str:
    try:
        fm, _ = parse_frontmatter(source.read_text(encoding="utf-8"))
    except ValueError:
        return "MALFORMED"
    s = fm.get("status")
    return s if isinstance(s, str) else "MISSING"


def update_sealed_flag(yaml_text: str, sprint_n: int, sealed_at: str) -> str:
    """Set `sealed: true` and add `sealed_at: <ts>` line on the entry whose id is vN.
    Preserves surrounding formatting and comments.
    """
    lines = yaml_text.splitlines(keepends=True)

    sprints_idx: int | None = None
    for i, line in enumerate(lines):
        if re.match(r"^sprints:\s*$", line):
            sprints_idx = i
            break
    if sprints_idx is None:
        raise ValueError("sprints: block not found in prism-config.md")

    target_id = f"v{sprint_n}"
    in_target_entry = False
    sealed_line_idx: int | None = None
    entry_indent = "    "  # default 4-space body indent under list entry
    last_idx_of_entry = sprints_idx
    target_entry_start_idx = sprints_idx  # line index of the target `- id: vN` entry

    for i in range(sprints_idx + 1, len(lines)):
        line = lines[i]
        if line.strip() and not line.startswith((" ", "\t")):
            break  # next top-level key
        m = re.match(r"^(\s+)-\s+id:\s*['\"]?(\S+?)['\"]?\s*$", line)
        if m:
            if in_target_entry:
                break
            if m.group(2) == target_id:
                in_target_entry = True
                # body indent = `- ` indent + 2 (e.g. "  - id: v1" → body "    sealed: false")
                entry_indent = m.group(1) + "  "
                last_idx_of_entry = i
                target_entry_start_idx = i
            continue
        if in_target_entry:
            last_idx_of_entry = i
            sm = re.match(r"^(\s+)sealed:\s*(true|false)\s*$", line)
            if sm:
                sealed_line_idx = i
                entry_indent = sm.group(1)

    if not in_target_entry:
        raise ValueError(f"sprint {target_id} entry not found in sprints: array")

    new_lines = list(lines)
    sealed_at_line = f'{entry_indent}sealed_at: "{sealed_at}"\n'

    if sealed_line_idx is not None:
        replaced = re.sub(
            r"sealed:\s*(true|false)", "sealed: true", new_lines[sealed_line_idx], count=1
        )
        # Ensure the sealed line ends with exactly one newline before the next line is inserted
        if not replaced.endswith("\n"):
            replaced += "\n"
        new_lines[sealed_line_idx] = replaced
        already_at = any(
            re.match(r"^\s+sealed_at:\s*", new_lines[j])
            for j in range(target_entry_start_idx, min(len(new_lines), last_idx_of_entry + 2))
        )
        if not already_at:
            new_lines.insert(sealed_line_idx + 1, sealed_at_line)
    else:
        insert_at = last_idx_of_entry + 1
        # Make sure the previous line ends with newline
        if insert_at > 0 and not new_lines[insert_at - 1].endswith("\n"):
            new_lines[insert_at - 1] += "\n"
        new_lines = (
            new_lines[:insert_at]
            + [f"{entry_indent}sealed: true\n", sealed_at_line]
            + new_lines[insert_at:]
        )

    return "".join(new_lines)


def write_config(config_path: Path, full_text: str, new_yaml: str) -> None:
    new_full = YAML_BLOCK_RE.sub(
        lambda m: f"{m.group(1)}{new_yaml}{m.group(3)}", full_text, count=1
    )
    tmp = config_path.with_suffix(config_path.suffix + ".tmp")
    tmp.write_text(new_full, encoding="utf-8")
    tmp.replace(config_path)


def stamp_applied_to_living(source: Path, marker: str) -> None:
    """Set `applied_to_living: <marker>` in the frontmatter of `source`."""
    text = source.read_text(encoding="utf-8")
    m = re.match(r"^(---\n)(.*?)(\n---\n)", text, re.DOTALL)
    if not m:
        return
    fm_text = m.group(2)
    if re.search(r"^applied_to_living:.*$", fm_text, re.MULTILINE):
        new_fm = re.sub(
            r"^(applied_to_living:).*$",
            rf"\1 {marker}",
            fm_text,
            count=1,
            flags=re.MULTILINE,
        )
    else:
        new_fm = fm_text.rstrip() + f"\napplied_to_living: {marker}"
    new_text = m.group(1) + new_fm + m.group(3) + text[m.end():]
    tmp = source.with_suffix(source.suffix + ".tmp")
    tmp.write_text(new_text, encoding="utf-8")
    tmp.replace(source)


def _first_frontmatter_value(frontmatters: list[dict], key: str, default: object = "") -> object:
    for fm in frontmatters:
        value = fm.get(key)
        if value not in (None, ""):
            return value
    return default


def _source_frontmatters(sources: list[Path]) -> list[dict]:
    out: list[dict] = []
    for source in sources:
        try:
            fm, _body = parse_frontmatter(source.read_text(encoding="utf-8"))
        except ValueError:
            continue
        out.append(fm)
    return out


def _source_approvers_from_frontmatters(frontmatters: list[dict]) -> str:
    approvers: list[str] = []
    seen: set[str] = set()
    for fm in frontmatters:
        raw = str(fm.get("approved_by", "") or "").strip()
        if not raw:
            continue
        for part in re.split(r"[,;]\s*", raw):
            approver = part.strip()
            if approver and approver not in seen:
                seen.add(approver)
                approvers.append(approver)
    return ", ".join(approvers)


def _source_approvers(sources: list[Path]) -> str:
    return _source_approvers_from_frontmatters(_source_frontmatters(sources))


def _phase_for_living_path(path: Path, project_root: Path) -> str:
    try:
        rel = path.relative_to(project_root / "docs").as_posix()
    except ValueError:
        return ""
    if rel.startswith("product/"):
        return "product"
    if rel.startswith("design/"):
        return "design"
    if rel.startswith("architecture/"):
        return "architecture"
    if rel.startswith("testing/"):
        return "testing"
    return ""


def _set_frontmatter_field(fm_text: str, key: str, value: str) -> str:
    pattern = rf"^{re.escape(key)}:[ \t]*.*$"
    replacement = f"{key}: {value}"
    if re.search(pattern, fm_text, flags=re.MULTILINE):
        return re.sub(pattern, replacement, fm_text, count=1, flags=re.MULTILINE)
    return fm_text.rstrip() + f"\n{replacement}"


def _stamp_living_text(
    text: str,
    *,
    approvers: str,
    sealed_at: str,
    version: str,
    sprint: str,
    phase: str,
    sprint_id: str,
    created: str,
) -> str:
    m = re.match(r"^(---\n)(.*?)(\n---\n)", text, re.DOTALL)
    if m:
        fm_text = m.group(2)
        try:
            fm, _body = parse_frontmatter(text)
        except ValueError:
            fm = {}
        if str(fm.get("status", "")).upper() != "REMOVED":
            fm_text = _set_frontmatter_field(fm_text, "status", "APPROVED")
        fm_text = _set_frontmatter_field(fm_text, "version", version)
        fm_text = _set_frontmatter_field(fm_text, "sprint", sprint)
        fm_text = _set_frontmatter_field(fm_text, "phase", phase)
        fm_text = _set_frontmatter_field(fm_text, "sprint_id", sprint_id)
        if str(fm.get("created", "") or "").strip() == "":
            fm_text = _set_frontmatter_field(fm_text, "created", created)
        fm_text = _set_frontmatter_field(fm_text, "updated", sealed_at)
        fm_text = _set_frontmatter_field(fm_text, "approved_by", approvers or "PRISM seal")
        return m.group(1) + fm_text + m.group(3) + text[m.end():]

    return (
        "---\n"
        "status: APPROVED\n"
        f"version: {version}\n"
        f"sprint: {sprint}\n"
        f"phase: {phase}\n"
        f"sprint_id: {sprint_id}\n"
        f"created: {created}\n"
        f"updated: {sealed_at}\n"
        f"approved_by: {approvers or 'PRISM seal'}\n"
        "---\n\n"
        + text
    )


def stamp_living_approval_metadata(
    merged_text: dict[Path, str],
    sources: list[Path],
    *,
    sealed_at: str,
    sprint_n: int,
    project_root: Path | None = None,
    source_to_targets: dict[Path, list[Path]] | None = None,
) -> None:
    """Mutate merged Living Truth text so sealed files expose approval metadata.

    Proposal files carry approval metadata before seal; readers inspect the
    Living Truth files after seal. Without copying a concise approval stamp into
    Living Truth, sealed output still looks like DRAFT in Markdown preview.
    """
    all_frontmatters = _source_frontmatters(sources)
    all_approvers = _source_approvers_from_frontmatters(all_frontmatters)
    sources_by_target: dict[Path, list[Path]] = {}
    for source, targets in (source_to_targets or {}).items():
        for target in targets:
            sources_by_target.setdefault(target, []).append(source)

    for path in list(merged_text):
        target_frontmatters = _source_frontmatters(sources_by_target.get(path, []))
        frontmatters = target_frontmatters or all_frontmatters
        phase = str(
            _first_frontmatter_value(
                target_frontmatters,
                "phase",
                _phase_for_living_path(path, project_root) if project_root else "",
            )
        )
        created = str(_first_frontmatter_value(frontmatters, "created", sealed_at.split()[0]))
        merged_text[path] = _stamp_living_text(
            merged_text[path],
            approvers=_source_approvers_from_frontmatters(frontmatters) or all_approvers,
            sealed_at=sealed_at,
            version=str(_first_frontmatter_value(frontmatters, "version", f"v{sprint_n}")),
            sprint=str(_first_frontmatter_value(frontmatters, "sprint", sprint_n)),
            phase=phase,
            sprint_id=str(_first_frontmatter_value(frontmatters, "sprint_id", f"sprint-v{sprint_n}")),
            created=created,
        )


# ---------------------------------------------------------------------------
# Phase C — auto-generated index sections.
# ---------------------------------------------------------------------------
# After merge, each root Living Truth file gets a regenerated `## Index` of its own
# anchored items (ID + Title), read straight from the anchors so the IDs are preserved
# exactly and ordered by ascending number — cross-doc / code links never drift. prd.md
# also gets an Epic Index derived from the per-epic files. The section is delimited by
# markers and rebuilt each seal (idempotent), so re-sealing yields byte-stable output.
INDEX_START = "<!-- PRISM:INDEX:START (auto-generated by seal_sprint.py — do not edit by hand) -->"
INDEX_END = "<!-- PRISM:INDEX:END -->"
_INDEX_BLOCK_RE = re.compile(re.escape(INDEX_START) + r".*?" + re.escape(INDEX_END) + r"\n?", re.DOTALL)


def _strip_index_section(text: str) -> str:
    cleaned = _INDEX_BLOCK_RE.sub("", text)
    return re.sub(r"\n{3,}", "\n\n", cleaned)


def _index_cell(value: str) -> str:
    return value.replace("|", "\\|").strip()


def _index_items(text: str) -> list[tuple[str, str]]:
    """Return [(id, title)] for the file's own anchored catalog items, excluding singleton
    blocks (`*-OVERVIEW` narrative, `TEST-COVERAGE` Rule/Branch Inventory), sorted by
    (prefix, ascending number). Singletons are sections, not catalog entries."""
    _preamble, blocks = parse_anchored_blocks(text)
    rows: list[tuple[str, int, str, str]] = []
    for aid, block_lines in blocks:
        try:
            prefix, num = split_anchor_id(aid)
        except ValueError:
            continue
        if prefix.endswith("OVERVIEW") or prefix == "TEST-COVERAGE":
            continue
        title = (extract_title_from_block(block_lines) or "").strip()
        rows.append((prefix, num, aid, title))
    rows.sort(key=lambda r: (r[0], r[1]))
    return [(aid, title) for _p, _n, aid, title in rows]


# `**Priority**: Must` line inside an EP block body (MoSCoW). Used to fill the auto Epic
# Index Priority column without hand-maintenance.
EPIC_PRIORITY_RE = re.compile(r"^\*\*Priority\*\*:\s*(.+?)\s*$", re.MULTILINE)


def _epic_index_rows(
    project_root: Path, merged_text: dict[Path, str]
) -> list[tuple[str, str, str, str, str]]:
    """Return [(EP-id, title, priority, status, filename)] from epic files (disk ∪ in-memory
    merge), sorted by EP id. In-memory (this seal) overrides disk so the Epic Index reflects the
    sealed state.

    `status` is read from each epic's frontmatter. At seal, `inject_indexes` runs AFTER
    `stamp_living_approval_metadata`, so a freshly-scaffolded epic (`status: DRAFT`) has already
    been flipped to APPROVED before it is read here — the auto index never shows a stale DRAFT
    (the epic-index bug this replaced). `priority` is parsed from the EP block's `**Priority**:`
    line. Both default to `—` when absent."""
    epic_texts: dict[str, str] = {}
    epics_dir = project_root / "docs" / "product" / "epics"
    if epics_dir.is_dir():
        for f in epics_dir.iterdir():
            if f.is_file() and EPIC_FILE_RE.match(f.name):
                epic_texts[f.name] = f.read_text(encoding="utf-8")
    for path, text in merged_text.items():
        if EPIC_FILE_RE.match(path.name):
            epic_texts[path.name] = text
    rows: list[tuple[str, str, str, str, str]] = []
    for name, text in epic_texts.items():
        m = EPIC_FILE_RE.match(name)
        assert m is not None
        ep_id = f"EP-{m.group(1)}"
        try:
            fm, _ = parse_frontmatter(text)
        except ValueError:
            fm = {}
        # Tombstoned epics (a `Removed` EP at a prior seal) drop out of the active Epic Index.
        if fm.get("removed") is True or str(fm.get("status", "")).upper() == "REMOVED":
            continue
        status = str(fm.get("status", "") or "").strip().upper() or "—"
        title = ""
        priority = ""
        _preamble, blocks = parse_anchored_blocks(text)
        for aid, block_lines in blocks:
            if aid == ep_id:
                title = (extract_title_from_block(block_lines) or "").strip()
                pm = EPIC_PRIORITY_RE.search("\n".join(block_lines))
                if pm:
                    priority = pm.group(1).strip()
                break
        if not title:
            title = str(fm.get("title", "") or "").strip()
        rows.append((ep_id, title, priority or "—", status, name))
    rows.sort(key=lambda r: r[0])
    return rows


def _render_index(
    items: list[tuple[str, str]], epic_rows: list[tuple[str, str, str, str, str]]
) -> str:
    lines = [INDEX_START, "", "## Index", ""]
    if items:
        lines += ["| ID | Title |", "|---|---|"]
        lines += [f"| {aid} | {_index_cell(title)} |" for aid, title in items]
        lines.append("")
    if epic_rows:
        lines += ["### Epics", "", "| Epic | Title | Priority | Status | File |", "|---|---|---|---|---|"]
        lines += [
            f"| {ep} | {_index_cell(title)} | {_index_cell(priority)} | {_index_cell(status)} | `epics/{name}` |"
            for ep, title, priority, status, name in epic_rows
        ]
        lines.append("")
    lines.append(INDEX_END)
    return "\n".join(lines)


def inject_indexes(merged_text: dict[Path, str], project_root: Path) -> None:
    """Regenerate the `## Index` section of each root Living Truth file in `merged_text`
    (mutated in place). Idempotent — an existing index block is stripped and rebuilt.

    prd.md's Epic Index depends on the per-epic files, so when any epic file changed this
    seal, prd.md is pulled into the write set (loaded from disk if untouched) and re-indexed.
    """
    prd_rel = "product/prd.md"
    prd_path = project_root / "docs" / prd_rel
    epics_touched = any(EPIC_FILE_RE.match(p.name) for p in merged_text)
    if epics_touched and prd_path not in merged_text and prd_path.is_file():
        merged_text[prd_path] = prd_path.read_text(encoding="utf-8")

    for path in list(merged_text):
        try:
            rel = path.relative_to(project_root / "docs").as_posix()
        except ValueError:
            continue
        if rel not in LIVING_TO_TEMPLATE:
            # Deliberate: only the 15 root LT files get an auto `## Index`. Per-epic files
            # (`product/epics/EP-*.md`) are skipped by design — each carries its own
            # "Product Traceability Map" (EP → FR → Related US, see epic-template.md), which
            # is richer and authored, not a flat ID|Title list. prd.md's Epic Index (above)
            # already gives the cross-epic catalog, so a per-epic `## Index` would be redundant.
            continue
        text = _strip_index_section(merged_text[path])
        items = _index_items(text)
        epic_rows = _epic_index_rows(project_root, merged_text) if rel == prd_rel else []
        if not items and not epic_rows:
            merged_text[path] = text
            continue
        index_md = _render_index(items, epic_rows)
        preamble, blocks = parse_anchored_blocks(text)
        new_preamble = (preamble.rstrip() + "\n\n" + index_md) if preamble.strip() else index_md
        merged_text[path] = serialize(new_preamble, blocks)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Seal a sprint: validate → merge → snapshot → sealed flag → drift scan.",
    )
    parser.add_argument("--sprint", required=True, help="Sprint version e.g. v3")
    parser.add_argument(
        "--project-root", help="Project root containing prism-config.md (default: walk up)",
    )
    parser.add_argument(
        "--skip-drift-scan", action="store_true", help="Skip scan_drift.py invocation",
    )
    parser.add_argument("--dry-run", action="store_true", help="Plan + report, do not write")
    parser.add_argument(
        "--strict-content",
        action="store_true",
        help="Treat Living Truth content-hygiene findings as seal blockers",
    )
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args()

    try:
        sprint_n = parse_sprint_arg(args.sprint)
    except ValueError as e:
        sys.stderr.write(f"ERROR: {e}\n")
        return 1

    root = Path(args.project_root) if args.project_root else find_project_root(Path.cwd())
    if root is None:
        sys.stderr.write("ERROR: project root not found (no prism-config.md in cwd or parents)\n")
        return 3

    config_path = root / "prism-config.md"
    try:
        config_data, config_full, config_yaml = read_config_yaml(config_path)
    except ValueError as e:
        sys.stderr.write(f"ERROR: {e}\n")
        return 3

    sealable_err = check_sprint_sealable(config_data, sprint_n)
    if sealable_err:
        sys.stderr.write(f"ERROR: {sealable_err}\n")
        return 1

    try:
        with sprint_seal_lock(root, sprint_n):
            return _run_seal_pipeline(args, root, sprint_n, config_path, config_full, config_yaml)
    except RuntimeError as e:
        sys.stderr.write(f"ERROR: {e}\n")
        return 1


def _run_seal_pipeline(
    args: argparse.Namespace,
    root: Path,
    sprint_n: int,
    config_path: Path,
    config_full: str,
    config_yaml: str,
) -> int:
    """Core seal pipeline. Caller holds the per-project flock."""
    # Discover sources
    proposals = collect_proposals(root, sprint_n)
    deltas = collect_delta_files(root, sprint_n)
    unknown_split_proposals = collect_unrecognized_split_proposal_files(root, sprint_n)

    if not proposals and not deltas and not unknown_split_proposals:
        sys.stderr.write(f"ERROR: no proposals or change-pack deltas found for sprint-v{sprint_n}\n")
        return 1

    # Block on DRAFT change packs (must be approved before seal)
    draft_packs: list[str] = []
    changes_dir = root / "docs" / f"sprint-v{sprint_n}" / "changes"
    if changes_dir.is_dir():
        for pack_dir in changes_dir.iterdir():
            if not pack_dir.is_dir():
                continue
            req = pack_dir / "change-request.md"
            if not req.is_file():
                continue
            try:
                fm, _ = parse_frontmatter(req.read_text(encoding="utf-8"))
            except ValueError:
                continue
            if fm.get("status") == "DRAFT":
                draft_packs.append(pack_dir.name)
    if draft_packs:
        sys.stderr.write(
            "ERROR: cannot seal — DRAFT change pack(s) still open in sprint-v"
            f"{sprint_n}: {', '.join(draft_packs)}\n"
        )
        return 1

    # Validate every source: status APPROVED + validate_proposal report has no blockers
    blockers: list[str] = []
    for src in unknown_split_proposals:
        blockers.append(
            f"{src.relative_to(root)}: unrecognized split proposal filename/path; "
            "use the canonical target names under proposals/"
        )
    sources = proposals + deltas
    for src in sources:
        st = status_of(src)
        if st != "APPROVED":
            blockers.append(f"{src.relative_to(root)}: status='{st}' (must be APPROVED)")
            continue
        expected_target_prefixes, target_label = infer_expected_target_prefixes_from_path(src)
        report = validate(
            src.read_text(encoding="utf-8"),
            expected_phase=infer_expected_phase_from_path(src),
            expected_target_prefixes=expected_target_prefixes,
            target_label=target_label,
            source_path=src,
        )
        if report.blockers:
            for f in report.blockers:
                blockers.append(f"{src.relative_to(root)}: [{f.rule}] {f.message}")

    if blockers:
        sys.stderr.write("ERROR: pre-flight validation blockers:\n")
        for b in blockers:
            sys.stderr.write(f"  • {b}\n")
        return 1

    # Phase 9: multi-target merge. Each proposal/delta routes its anchored items to
    # multiple Living Truth files via `apply_proposal.apply_multi_target` (by ID prefix
    # and optional `<!-- EPIC: -->` routing tag). Sources are processed in order:
    # proposals first, then deltas in pack-version order. All merges happen in memory
    # (current_state buffer); final tmp + atomic rename writes everything at once.
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from apply_proposal import apply_multi_target  # noqa: E402

    try:
        merged_text: dict[Path, str] = plan_all_living_v1_bootstrap(root, sprint_n)
    except FileNotFoundError as e:
        sys.stderr.write(f"ERROR: {e}\n")
        return 2
    scaffolded_paths = list(merged_text)
    source_to_targets: dict[Path, list[Path]] = {}

    for src in proposals + deltas:
        code, payload = apply_multi_target(
            src.read_text(encoding="utf-8"),
            root,
            project_name=root.name,
            current_state=merged_text,
            verbose=args.verbose,
        )
        if isinstance(payload, str):
            sys.stderr.write(
                f"ERROR: multi-target merge failed for {src.relative_to(root)}: {payload}\n"
            )
            return 1 if code == 1 else code
        if not payload:
            sys.stderr.write(
                f"ERROR: multi-target merge produced no Living Truth changes for "
                f"{src.relative_to(root)}; proposal/delta must contain at least one anchored item\n"
            )
            return 1
        # `payload` is {target_path: merged_text}. Buffer in memory for chaining + final write.
        for target, content in payload.items():
            merged_text[target] = content
        source_to_targets[src] = list(payload.keys())

    # Phase C: stamp approval metadata FIRST, then regenerate `## Index` sections.
    # Order matters: prd.md's Epic Index reads each epic's frontmatter `status`, and a
    # freshly-scaffolded epic still carries `status: DRAFT` until stamping flips it to
    # APPROVED. Indexing before stamping would freeze that stale DRAFT into Living Truth
    # (the exact epic-index bug). So we (1) pull prd.md into the write set when any epic
    # changed — so it is both stamped and re-indexed this seal — then (2) stamp, (3) inject.
    prd_path = root / "docs" / "product" / "prd.md"
    if (
        any(EPIC_FILE_RE.match(p.name) for p in merged_text)
        and prd_path not in merged_text
        and prd_path.is_file()
    ):
        merged_text[prd_path] = prd_path.read_text(encoding="utf-8")

    sealed_at = dt.datetime.now().strftime("%Y-%m-%d %H:%M")
    stamp_living_approval_metadata(
        merged_text,
        sources,
        sealed_at=sealed_at,
        sprint_n=sprint_n,
        project_root=root,
        source_to_targets=source_to_targets,
    )

    # Regenerate `## Index` sections from the just-merged anchored content (IDs preserved,
    # ascending order), reading post-stamp APPROVED frontmatter. Runs on the in-memory buffer
    # so the indexes are part of the atomic write + snapshots.
    inject_indexes(merged_text, root)

    from validate_living_truth import format_findings, validate_living_texts  # noqa: E402

    living_findings = validate_living_texts(
        merged_text,
        root,
        sealed=True,
        strict_content=getattr(args, "strict_content", False),
        sprint_n=sprint_n,
    )
    living_blockers = [f for f in living_findings if f.level == "blocker"]
    if living_blockers:
        sys.stderr.write("ERROR: post-merge Living Truth validation blockers:\n")
        sys.stderr.write(format_findings(living_blockers) + "\n")
        return 1
    if args.verbose:
        living_warnings = [f for f in living_findings if f.level == "warn"]
        if living_warnings:
            sys.stderr.write("post-merge Living Truth validation warnings:\n")
            sys.stderr.write(format_findings(living_warnings) + "\n")

    if args.verbose:
        for src, targets in source_to_targets.items():
            tlist = ", ".join(t.relative_to(root).as_posix() for t in targets)
            sys.stderr.write(f"merge: {src.relative_to(root)} → [{tlist}]\n")

    asset_copies = collect_asset_copies(root, sprint_n)
    asset_removals = collect_asset_removals(root, sprint_n)
    asset_removal_blockers = validate_asset_removals(asset_removals, asset_copies, sprint_n)
    if asset_removal_blockers:
        sys.stderr.write("ERROR: asset removal manifest blockers:\n")
        for b in asset_removal_blockers:
            sys.stderr.write(f"  • {b}\n")
        return 1

    if args.dry_run:
        print(f"Dry-run: would seal sprint-v{sprint_n} merging:")
        for src, targets in source_to_targets.items():
            print(f"  source: {src.relative_to(root)}")
            for t in targets:
                print(f"    → {t.relative_to(root)}")
        if asset_copies:
            print(f"  would copy {len(asset_copies)} asset(s) into Living Truth:")
            for _src, dest in asset_copies:
                print(f"    → {dest.relative_to(root)}")
        if asset_removals:
            print(f"  would remove {len(asset_removals)} asset(s) from Living Truth:")
            for _phase, _rel, dest in asset_removals:
                suffix = "" if dest.is_file() else " (already absent)"
                print(f"    ✗ {dest.relative_to(root)}{suffix}")
        return 0

    # Prepare all post-merge side effects before touching Living Truth. From
    # here until source stamping completes, failures roll back Living Truth,
    # snapshots, config, and proposal/delta frontmatter as one seal event.
    try:
        new_yaml = update_sealed_flag(config_yaml, sprint_n, sealed_at)
    except ValueError as e:
        sys.stderr.write(f"ERROR: failed to update sealed flag: {e}\n")
        return 3
    marker = f"true {sealed_at}"
    try:
        git = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=root, capture_output=True, text=True, check=False,
        )
        if git.returncode == 0 and git.stdout.strip():
            marker = f"true {git.stdout.strip()} (sealed {sealed_at})"
    except FileNotFoundError:
        pass

    living_paths = discover_snapshot_living_paths(root, merged_text)
    snapshot_paths = [snapshot_path_for_living(p, root, sprint_n) for p in living_paths]
    asset_dest_paths = [dest for _src, dest in asset_copies]
    asset_removal_paths = [dest for _phase, _rel, dest in asset_removals]
    rollback_states = capture_file_states(
        list(merged_text.keys())
        + [config_path]
        + sources
        + snapshot_paths
        + asset_dest_paths
        + asset_removal_paths
    )
    removed_assets: list[Path] = []
    missing_removals: list[Path] = []

    try:
        write_living_files_atomically(merged_text)

        for path in scaffolded_paths:
            sys.stderr.write(f"bootstrapped: {path.relative_to(root)}\n")

        # Snapshots — byte-for-byte clone from the just-merged living files.
        # Phase 9: nested layout mirrors LT structure
        # (vd `snapshots/product/prd-at-v1-sealed.md`, `snapshots/product/epics/EP-001-at-v1-sealed.md`).
        for living, snap_path in zip(living_paths, snapshot_paths):
            snap_path.parent.mkdir(parents=True, exist_ok=True)
            # Clear read-only bit if a previous run left one
            if snap_path.exists():
                try:
                    snap_path.chmod(stat.S_IWUSR | stat.S_IRUSR)
                except OSError:
                    pass
            shutil.copy(living, snap_path)
            snap_path.chmod(0o444)

        # Copy sprint phase assets into Living Truth so the `assets/...` references that
        # merged into Living Truth resolve. Override on collision; destinations were
        # captured in rollback_states so a later failure restores them.
        copy_assets_into_living(asset_copies)

        # Delete assets listed in each phase's `.removed` manifest (disjoint from copies —
        # add+remove conflicts were blocked above). Removal dests are in rollback_states.
        removed_assets, missing_removals = remove_assets_from_living(asset_removals)

        # Update sealed flag in config
        write_config(config_path, config_full, new_yaml)

        # Stamp applied_to_living on each source — prefer git commit hash per design §9.B
        # ("true + commit hash"); fall back to timestamp when not in a git repo.
        for src in sources:
            stamp_applied_to_living(src, marker)

        from validate_living_truth import validate_project  # noqa: E402

        post_findings = validate_project(
            root,
            sprint_n=sprint_n,
            sealed=True,
            strict_content=args.strict_content,
        )
        post_blockers = [f for f in post_findings if f.level == "blocker"]
        if post_blockers:
            raise RuntimeError(
                "post-write Living Truth validation failed:\n"
                + format_findings(post_blockers)
            )
    except Exception as e:
        restore_file_states(rollback_states)
        sys.stderr.write(f"ERROR: seal side-effect failed; rolled back seal outputs: {e}\n")
        return 2

    # Drift scan
    drift_emitted: list[str] = []
    if not args.skip_drift_scan:
        scan_cmd = [
            sys.executable,
            str(Path(__file__).resolve().parent / "scan_drift.py"),
            "--trigger", "seal",
            "--sprint", f"v{sprint_n}",
            "--project-root", str(root),
        ]
        sd = subprocess.run(scan_cmd, capture_output=True, text=True, check=False)
        if sd.returncode == 0 and sd.stdout:
            drift_emitted.append(sd.stdout.rstrip())
        elif sd.returncode != 0:
            drift_emitted.append(f"WARNING: scan_drift.py exit {sd.returncode}: {sd.stderr}")

    # Report
    print(f"✓ Sprint-v{sprint_n} sealed at {sealed_at}")
    print(f"  Merged {len(source_to_targets)} source(s) into {len(merged_text)} living file(s):")
    for living in merged_text:
        print(f"    → {living.relative_to(root)}")
    print(f"  Snapshots written ({len(snapshot_paths)}):")
    for s in snapshot_paths:
        print(f"    → {s.relative_to(root)} (chmod 444)")
    if asset_copies:
        print(f"  Assets copied into Living Truth ({len(asset_copies)}):")
        for _src, dest in asset_copies:
            print(f"    → {dest.relative_to(root)}")
    if removed_assets:
        print(f"  Assets removed from Living Truth ({len(removed_assets)}):")
        for dest in removed_assets:
            print(f"    ✗ {dest.relative_to(root)}")
    if missing_removals:
        print(
            f"  Note: {len(missing_removals)} removal path(s) had no matching Living Truth "
            "asset (already absent or a typo):"
        )
        for dest in missing_removals:
            print(f"    - {dest.relative_to(root)}")
    print(f"  applied_to_living stamped on {len(sources)} source(s)")
    print(f"  prism-config.md updated: sprints.v{sprint_n}.sealed=true")
    if drift_emitted:
        print("  Drift scan:")
        for line in drift_emitted:
            for sub in line.splitlines():
                print(f"    {sub}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
