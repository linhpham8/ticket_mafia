#!/usr/bin/env python3
"""precommit_living_truth.py — Phase 2 (extended Phase 9) git pre-commit hook.

Blocks direct edits to PRISM Living Truth files (per design discussion doc §6.5).

Phase 9 layout (nested per-phase + per-epic folder):
  docs/product/prd.md
  docs/product/glossary.md
  docs/product/personas.md
  docs/product/market-research.md
  docs/product/epics/EP-NNN-*.md          (per-epic files, dynamic)
  docs/design/design-system.md
  docs/architecture/architecture.md
  docs/architecture/nfr.md
  docs/architecture/sequence.md
  docs/architecture/erd.md
  docs/architecture/adr.md
  docs/architecture/data-flow.md
  docs/architecture/api-specs.md
  docs/architecture/events.md
  docs/architecture/project-reference.md
  docs/testing/test-cases.md

These files are updated only by `seal_sprint.py` at sprint seal. A staged
edit indicates either (a) the user is bypassing the proposal / seal workflow,
or (b) the commit IS the seal commit — in which case bypass with
`git commit --no-verify`.

Installation:
  Guided setup installs this hook automatically when the project has a `.git`
  directory and no existing pre-commit hook. If the project already has a hook,
  chain this script manually from that hook.

  ln -s "$PRISM_ROOT/core/tools/precommit_living_truth.py" .git/hooks/pre-commit
  chmod +x .git/hooks/pre-commit

Or copy the file:
  cp "$PRISM_ROOT/core/tools/precommit_living_truth.py" .git/hooks/pre-commit
  chmod +x .git/hooks/pre-commit

Exit codes:
  0  no living-truth files staged → allow commit
  1  living-truth files staged → block (advise --no-verify for seal commits)
"""

from __future__ import annotations

import re
import subprocess
import sys


# Exact-path Living Truth roots (15 root files). Epic files are handled via glob below.
LIVING_TRUTH_FILES = frozenset({
    "docs/product/prd.md",
    "docs/product/glossary.md",
    "docs/product/personas.md",
    "docs/product/market-research.md",
    "docs/design/design-system.md",
    "docs/architecture/architecture.md",
    "docs/architecture/nfr.md",
    "docs/architecture/sequence.md",
    "docs/architecture/erd.md",
    "docs/architecture/adr.md",
    "docs/architecture/data-flow.md",
    "docs/architecture/api-specs.md",
    "docs/architecture/events.md",
    "docs/architecture/project-reference.md",
    "docs/testing/test-cases.md",
})

# Epic files: dynamic path, matched by regex. `EP-\d{3,}` matches the canonical
# zero-padded form every creator emits (get_next_id `{:03d}`, migrate `zfill(3)`,
# apply_proposal.EPIC_FILE_RE) — kept identical so the guard and the merger agree.
EPIC_FILE_RE = re.compile(r"^docs/product/epics/EP-\d{3,}-[a-z0-9-]+\.md$")


def is_living_truth(path: str) -> bool:
    if path in LIVING_TRUTH_FILES:
        return True
    if EPIC_FILE_RE.match(path):
        return True
    return False


def staged_files() -> list[str]:
    try:
        result = subprocess.run(
            ["git", "diff", "--cached", "--name-only"],
            capture_output=True, text=True, check=False,
        )
    except FileNotFoundError:
        return []
    if result.returncode != 0:
        return []
    return [line.strip() for line in result.stdout.splitlines() if line.strip()]


def main() -> int:
    files = staged_files()
    violations = sorted(f for f in files if is_living_truth(f))
    if not violations:
        return 0
    sys.stderr.write(
        "⚠ PRISM pre-commit hook blocked: direct edit to Living Truth file(s):\n"
    )
    for f in violations:
        sys.stderr.write(f"  • {f}\n")
    sys.stderr.write(
        "\n"
        "Living Truth is updated only by `seal_sprint.py` at sprint seal\n"
        "(per design discussion doc §6.5). For same-sprint corrections, use\n"
        "the change-pack flow: `start change: ...`.\n"
        "\n"
        "If this commit IS the seal result, bypass intentionally with:\n"
        "  git commit --no-verify\n"
    )
    return 1


if __name__ == "__main__":
    sys.exit(main())
