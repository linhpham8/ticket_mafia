#!/usr/bin/env python3
"""
Push tất cả file Markdown trong một folder lên Confluence (upsert).

Usage:
  python tools/confluence_push_folder.py --folder testing-output --parent-id 3814785380
  python tools/confluence_push_folder.py --folder testing-output/test-plan --parent-id 3814785380 --recursive
  python tools/confluence_push_folder.py --folder testing-output --parent-id 3814785380 --dry-run
"""
from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).parent))

from credentials import load_atlassian_credentials
from confluence_md import get_page_meta, push_md_file, _auth


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--folder",    default="testing-output",
                        help="Thư mục chứa file .md (default: testing-output)")
    parser.add_argument("--parent-id", required=True,
                        help="Page ID Confluence làm trang cha")
    parser.add_argument("--pattern",   default="*.md",
                        help="Glob pattern (default: *.md)")
    parser.add_argument("--recursive", action="store_true",
                        help="Tìm .md trong subfolder")
    parser.add_argument("--message",   default="Auto-push from testing-skills",
                        help="Version message khi update")
    parser.add_argument("--delay",     type=float, default=0.5,
                        help="Giây chờ giữa các request (default: 0.5)")
    parser.add_argument("--dry-run",   action="store_true",
                        help="Preview only, không push thật")
    args = parser.parse_args()

    email, token, base_url = load_atlassian_credentials()
    api_base = f"{base_url.rstrip('/')}/wiki/api/v2"
    auth = _auth(email, token)

    folder = Path(args.folder)
    if not folder.is_absolute():
        folder = ROOT / folder
    if not folder.exists():
        print(f"ERROR: folder not found: {folder}")
        return 1

    print(f"Fetching parent page (id={args.parent_id})...")
    parent_meta = get_page_meta(api_base, auth, args.parent_id)
    space_id = str(parent_meta.get("spaceId", ""))
    print(f"  Parent : '{parent_meta.get('title')}' | spaceId: {space_id}")

    md_files = sorted(folder.rglob(args.pattern) if args.recursive else folder.glob(args.pattern))
    if not md_files:
        print(f"No .md files found in {folder}")
        return 0

    print(f"\nFound {len(md_files)} file(s):\n")
    counts: dict[str, int] = {"created": 0, "updated": 0, "dry-run": 0, "error": 0}

    for i, md_path in enumerate(md_files, 1):
        rel = md_path.relative_to(ROOT) if md_path.is_relative_to(ROOT) else md_path
        print(f"[{i}/{len(md_files)}] {rel}")
        try:
            action, page_id, title = push_md_file(
                md_path=md_path,
                parent_id=args.parent_id,
                space_id=space_id,
                api_base=api_base,
                auth=auth,
                message=args.message,
                dry_run=args.dry_run,
            )
            counts[action] = counts.get(action, 0) + 1
            if not args.dry_run:
                url = f"{base_url.rstrip('/')}/wiki/pages/{page_id}"
                print(f"  {action.upper()}: '{title}' -> {url}")
        except Exception as exc:
            counts["error"] += 1
            print(f"  ERROR: {exc}")
        if i < len(md_files):
            time.sleep(args.delay)

    print(f"\n{'─'*50}")
    print(f"  Created : {counts['created']}")
    print(f"  Updated : {counts['updated']}")
    print(f"  Errors  : {counts['error']}")
    if args.dry_run:
        print("  (Dry-run — no changes made)")
    print(f"{'─'*50}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
