#!/usr/bin/env python3
"""Fetch Confluence tree metadata for a page and save JSON."""

from __future__ import annotations

import argparse
import base64
import json
import re
import urllib.request
from pathlib import Path

from credentials import get_env


ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = ROOT / "docs" / "confluence-data"


def parse_page_id(url: str) -> tuple[str, str]:
    match = re.search(r"https?://([^/]+)/wiki/.*/pages/(\d+)", url)
    if not match:
        raise RuntimeError("Cannot parse page ID from URL")
    return f"https://{match.group(1)}", match.group(2)


def headers() -> dict[str, str]:
    email = get_env("ATLASSIAN_EMAIL") or get_env("ATLASSIAN_USER_EMAIL")
    token = get_env("ATLASSIAN_API_TOKEN")
    if not email or not token:
        raise RuntimeError("Missing Atlassian credentials")
    basic = base64.b64encode(f"{email}:{token}".encode()).decode()
    return {"Authorization": f"Basic {basic}", "Accept": "application/json"}


def get_json(url: str) -> dict:
    request = urllib.request.Request(url, headers=headers())
    with urllib.request.urlopen(request, timeout=60) as response:
        return json.load(response)


def compact(item: dict | None) -> dict | None:
    if not item:
        return None
    return {"id": str(item.get("id", "")), "title": str(item.get("title", ""))}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url", default="", help="Confluence page URL")
    parser.add_argument("--page-id", default="", help="Confluence page ID")
    parser.add_argument("--site-root", default="", help="Site root, for example https://onemount.atlassian.net")
    parser.add_argument("--out", default="", help="Output JSON path")
    parser.add_argument("--limit", type=int, default=200, help="Max sibling pages to fetch")
    args = parser.parse_args()

    if args.url:
        site_root, page_id = parse_page_id(args.url)
    elif args.page_id and args.site_root:
        site_root = args.site_root.rstrip("/")
        page_id = args.page_id
    else:
        raise RuntimeError("Provide --url or both --page-id and --site-root")

    base = f"{site_root}/wiki/rest/api/content"
    page = get_json(f"{base}/{page_id}?expand=ancestors,space,version,title")
    ancestors = page.get("ancestors", [])
    parent = ancestors[-1] if ancestors else None
    grandparent = ancestors[-2] if len(ancestors) >= 2 else None

    target_siblings = []
    if parent:
        target_siblings = [compact(item) for item in get_json(f"{base}/{parent['id']}/child/page?limit={args.limit}").get("results", [])]

    parent_siblings = []
    if grandparent:
        parent_siblings = [compact(item) for item in get_json(f"{base}/{grandparent['id']}/child/page?limit={args.limit}").get("results", [])]

    payload = {
        "target": {
            "id": str(page_id),
            "title": str(page.get("title", "")),
            "space": str(page.get("space", {}).get("key", "")),
            "version": page.get("version", {}).get("number", ""),
        },
        "ancestors": [compact(item) for item in ancestors],
        "parent": compact(parent),
        "target_siblings_under_parent": target_siblings,
        "grandparent": compact(grandparent),
        "parent_siblings_under_grandparent": parent_siblings,
    }

    out_path = Path(args.out) if args.out else OUT_DIR / f"confluence-{page_id}-tree.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"TREE_SAVED: {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
