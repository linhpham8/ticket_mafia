#!/usr/bin/env python3
"""get_next_id.py — Phase 2 (extended Phase 9).

Atomic ID counter for stable identifiers used across PRISM sprints.

Reads the YAML block of `prism-config.md`, increments
`id_counters[TYPE]` by `--reserve` (default 1), writes the file back
atomically, and prints each newly issued ID on its own stdout line.

Concurrency: protected by a side lock file so two parallel invocations
(e.g., concurrent sprints generating IDs) cannot collide. Uses `fcntl` on
POSIX and `msvcrt` on Windows.

Format: zero-padded 3-digit suffix, e.g., FR-001, FR-002, …, FR-999,
FR-1000 (width grows only when natural count exceeds 999). Multi-segment
prefixes (`DS-COMP`, `ARCH-COMP`) form IDs like `DS-COMP-001`.

Phase 9 changes:
  - `EPIC` → `EP` (one-time migration on first run that finds `id_counters.EPIC`)
  - `COMP` split into `DS-COMP` + `ARCH-COMP` (no auto-migration; new projects only)
  - 13 new prefixes: BR, NFR, TC, GLOSS, PERSONA, MR, SEQ, ENT, ADR, FLOW, API, EVT, PR

CLI:
  get_next_id.py --type {EP|FR|US|AC|BR|NFR|TC|SCREEN|DS-COMP|ARCH-COMP|ARCH|GLOSS|PERSONA|MR|SEQ|ENT|ADR|FLOW|API|EVT|PR} [--reserve N] [--config PATH]

Exit codes (per discussion doc §9.C):
  0  OK
  1  validation fail (--reserve < 1)
  2  file not found (config)
  3  config error (no YAML block, malformed YAML)
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

import yaml

try:
    import fcntl
except ImportError:  # pragma: no cover - exercised on Windows
    fcntl = None

try:
    import msvcrt
except ImportError:  # pragma: no cover - exercised on POSIX
    msvcrt = None


VALID_TYPES = (
    # Product
    "EP", "FR", "US", "AC", "BR", "GLOSS", "PERSONA", "MR",
    # Design
    "SCREEN", "DS-COMP",
    # Architecture
    "ARCH", "ARCH-COMP", "NFR", "SEQ", "ENT", "ADR", "FLOW", "API", "EVT", "PR",
    # Testing
    "TC",
    # NOTE: the singleton narrative prefixes PRD-OVERVIEW / ARCH-OVERVIEW / DESIGN-OVERVIEW are
    # intentionally NOT here. Each is a per-file singleton authored as the literal `-001` (no
    # counter); apply_proposal/validate_proposal route + validate them, but they are never issued
    # via get_next_id (migrate_to_2tier likewise carries no OVERVIEW counter — consistent).
)
YAML_BLOCK_RE = re.compile(r"(```yaml\n)(.*?)(\n```)", re.DOTALL)
# Phase 9: anchor parser regex supports multi-segment prefixes (DS-COMP-001, ARCH-COMP-001)
ANCHOR_ID_RE = re.compile(r"\b([A-Z]+(?:-[A-Z]+)*)-(\d+)\b")


def lock_file(file_obj) -> None:
    if fcntl is not None:
        fcntl.flock(file_obj.fileno(), fcntl.LOCK_EX)
        return
    if msvcrt is not None:
        file_obj.seek(0)
        msvcrt.locking(file_obj.fileno(), msvcrt.LK_LOCK, 1)
        return
    raise RuntimeError("no supported file locking API found")


def unlock_file(file_obj) -> None:
    if fcntl is not None:
        fcntl.flock(file_obj.fileno(), fcntl.LOCK_UN)
        return
    if msvcrt is not None:
        file_obj.seek(0)
        msvcrt.locking(file_obj.fileno(), msvcrt.LK_UNLCK, 1)


def find_config(start: Path) -> Path | None:
    """Walk up from `start` looking for prism-config.md."""
    p = start.resolve()
    for parent in [p] + list(p.parents):
        candidate = parent / "prism-config.md"
        if candidate.is_file():
            return candidate
    return None


def extract_yaml_block(full_text: str) -> str:
    m = YAML_BLOCK_RE.search(full_text)
    if not m:
        raise ValueError("no YAML code fence ```yaml ... ``` found in prism-config.md")
    return m.group(2)


def read_counter(yaml_text: str, type_: str) -> int:
    try:
        data = yaml.safe_load(yaml_text)
    except yaml.YAMLError as e:
        raise ValueError(f"YAML parse error: {e}") from e
    if not isinstance(data, dict):
        return 0
    counters = data.get("id_counters") or {}
    # Phase 9 migration: legacy `EPIC` counter -> `EP`. If both exist, EP wins (already migrated).
    if type_ == "EP" and "EP" not in counters and "EPIC" in counters:
        return int(counters["EPIC"])
    return int(counters.get(type_, 0))


def update_yaml_counter(yaml_text: str, type_: str, new_value: int) -> str:
    """Set id_counters[type_] = new_value in `yaml_text` (string), preserving
    surrounding formatting and comments. Bootstraps the `id_counters:` block
    on first use; adds a missing type line if the block exists but lacks it.

    Phase 9 migration: when writing `EP`, also rename any existing `EPIC` line
    to `EP` so the legacy counter doesn't shadow the new one.
    """
    block_pattern = re.compile(r"^id_counters:\s*\n", re.MULTILINE)
    bm = block_pattern.search(yaml_text)

    if bm is None:
        lines = "\n".join(
            f"  {t}: {new_value if t == type_ else 0}" for t in VALID_TYPES
        )
        return yaml_text.rstrip() + "\n\nid_counters:\n" + lines + "\n"

    # Phase 9: if writing EP and legacy EPIC exists, rename in place (one-time migration).
    if type_ == "EP":
        legacy_pattern = re.compile(r"(?m)^([ \t]+)EPIC(\s*:\s*)\d+(.*)$")
        if legacy_pattern.search(yaml_text):
            yaml_text = legacy_pattern.sub(
                rf"\g<1>EP\g<2>{new_value}\g<3>", yaml_text, count=1
            )
            return yaml_text

    # YAML keys with hyphens (DS-COMP, ARCH-COMP) need quoting? Plain YAML allows hyphens in
    # keys as long as they're not at the start. Both `DS-COMP: 5` and `"DS-COMP": 5` parse.
    # We emit unquoted for consistency with existing single-segment prefixes.
    counter_pattern = re.compile(rf"(?m)^([ \t]+){re.escape(type_)}(\s*:\s*)\d+(.*)$")
    if counter_pattern.search(yaml_text):
        return counter_pattern.sub(
            rf"\g<1>{type_}\g<2>{new_value}\g<3>", yaml_text, count=1
        )

    insert_pos = bm.end()
    return yaml_text[:insert_pos] + f"  {type_}: {new_value}\n" + yaml_text[insert_pos:]


def write_config(config_path: Path, full_text: str, new_yaml_text: str) -> None:
    new_full = YAML_BLOCK_RE.sub(
        lambda m: f"{m.group(1)}{new_yaml_text}{m.group(3)}", full_text, count=1
    )
    tmp = config_path.with_suffix(config_path.suffix + ".tmp")
    tmp.write_text(new_full, encoding="utf-8")
    tmp.replace(config_path)


def issue_ids(config_path: Path, type_: str, reserve: int) -> list[str]:
    """Locked atomic operation: read → increment → write → return list of IDs."""
    lock_path = config_path.with_suffix(config_path.suffix + ".lock")
    with open(lock_path, "a+") as lock_f:
        lock_file(lock_f)
        try:
            full_text = config_path.read_text(encoding="utf-8")
            yaml_text = extract_yaml_block(full_text)
            current = read_counter(yaml_text, type_)
            ids = [f"{type_}-{current + i + 1:03d}" for i in range(reserve)]
            new_yaml = update_yaml_counter(yaml_text, type_, current + reserve)
            write_config(config_path, full_text, new_yaml)
        finally:
            unlock_file(lock_f)
    return ids


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Atomic stable-ID counter for PRISM (Phase 2).",
    )
    parser.add_argument("--type", required=True, choices=VALID_TYPES)
    parser.add_argument("--reserve", type=int, default=1)
    parser.add_argument(
        "--config", help="Path to prism-config.md (default: walk up from CWD)"
    )
    args = parser.parse_args()

    if args.reserve < 1:
        sys.stderr.write("ERROR: --reserve must be >= 1\n")
        return 1

    if args.config:
        config_path = Path(args.config)
        if not config_path.is_file():
            sys.stderr.write(f"ERROR: config not found: {config_path}\n")
            return 2
    else:
        config_path = find_config(Path.cwd())
        if config_path is None:
            sys.stderr.write(
                "ERROR: prism-config.md not found (searched cwd and parents)\n"
            )
            return 2

    try:
        ids = issue_ids(config_path, args.type, args.reserve)
    except ValueError as e:
        sys.stderr.write(f"ERROR: {e}\n")
        return 3

    for i in ids:
        print(i)
    return 0


if __name__ == "__main__":
    sys.exit(main())
