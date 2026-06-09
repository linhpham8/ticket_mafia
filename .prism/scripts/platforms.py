#!/usr/bin/env python3
"""Shell-friendly query helper for adapters/platforms.json.

setup.sh / setup.ps1 call this to avoid parsing JSON in shell.

Usage:
    python3 platforms.py keys
        Print one platform key per line.

    python3 platforms.py field <key> <field>
        Print the value of a single field (dest, label, adapter_subdir,
        guided_filename, freedom_filename, shares_dest_with).

    python3 platforms.py legacy-dests
        Print all legacy_dests across all platforms, one per line, deduped.

    python3 platforms.py tsv
        Print one TSV row per platform:
            key<TAB>label<TAB>dest<TAB>guided_src<TAB>freedom_src<TAB>legacy_dests(comma)<TAB>size_warning_chars
        where guided_src/freedom_src are paths relative to the PRISM root.
        size_warning_chars is empty if no soft limit is declared.

    python3 platforms.py validate
        Exit 0 if the registry is well-formed. Used by tests.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REGISTRY_PATH = ROOT / "adapters" / "platforms.json"


def load_registry() -> dict:
    return json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))


def _source_path(platform: dict, filename_key: str) -> str:
    return f"adapters/{platform['adapter_subdir']}/{platform[filename_key]}"


def cmd_keys(registry: dict) -> int:
    for p in registry["platforms"]:
        print(p["key"])
    return 0


def cmd_field(registry: dict, key: str, field: str) -> int:
    for p in registry["platforms"]:
        if p["key"] == key:
            value = p.get(field, "")
            if isinstance(value, list):
                print(",".join(value))
            else:
                print(value)
            return 0
    print(f"Unknown platform key: {key}", file=sys.stderr)
    return 1


def cmd_legacy_dests(registry: dict) -> int:
    seen: set[str] = set()
    for p in registry["platforms"]:
        for legacy in p.get("legacy_dests", []):
            if legacy not in seen:
                seen.add(legacy)
                print(legacy)
    return 0


def cmd_tsv(registry: dict) -> int:
    # POSIX `read` with IFS=\t collapses consecutive tabs (empty fields). To keep
    # column alignment robust in shell loops, emit "-" for missing optional values
    # and have the consumer treat "-" as empty.
    for p in registry["platforms"]:
        guided_src = _source_path(p, "guided_filename")
        freedom_src = _source_path(p, "freedom_filename")
        legacy = ",".join(p.get("legacy_dests", [])) or "-"
        size_warn = str(p["size_warning_chars"]) if p.get("size_warning_chars") else "-"
        print("\t".join([p["key"], p["label"], p["dest"], guided_src, freedom_src, legacy, size_warn]))
    return 0


def cmd_validate(registry: dict) -> int:
    required_top = {"platforms", "roles"}
    missing_top = required_top - registry.keys()
    if missing_top:
        print(f"Missing top-level keys: {missing_top}", file=sys.stderr)
        return 1

    required_platform = {"key", "label", "dest", "adapter_subdir", "guided_filename", "freedom_filename"}
    seen_keys: set[str] = set()
    for p in registry["platforms"]:
        missing = required_platform - p.keys()
        if missing:
            print(f"Platform missing fields {missing}: {p}", file=sys.stderr)
            return 1
        if p["key"] in seen_keys:
            print(f"Duplicate platform key: {p['key']}", file=sys.stderr)
            return 1
        seen_keys.add(p["key"])

        shares = p.get("shares_dest_with")
        if shares and shares not in {x["key"] for x in registry["platforms"]}:
            print(f"shares_dest_with points to unknown key: {shares}", file=sys.stderr)
            return 1

    print(f"OK: {len(registry['platforms'])} platforms, {len(registry['roles'])} roles")
    return 0


def main() -> int:
    if len(sys.argv) < 2:
        print(__doc__, file=sys.stderr)
        return 2

    registry = load_registry()
    cmd = sys.argv[1]

    if cmd == "keys":
        return cmd_keys(registry)
    if cmd == "field":
        if len(sys.argv) != 4:
            print("usage: platforms.py field <key> <field>", file=sys.stderr)
            return 2
        return cmd_field(registry, sys.argv[2], sys.argv[3])
    if cmd == "legacy-dests":
        return cmd_legacy_dests(registry)
    if cmd == "tsv":
        return cmd_tsv(registry)
    if cmd == "validate":
        return cmd_validate(registry)

    print(f"unknown command: {cmd}", file=sys.stderr)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
