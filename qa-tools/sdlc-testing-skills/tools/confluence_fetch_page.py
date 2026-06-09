#!/usr/bin/env python3
"""
Fetch Confluence page(s) → lưu thành Markdown, giữ cấu trúc thư mục.

Usage:
  # Một trang đơn
  python tools/confluence_fetch_page.py --url https://your-domain.atlassian.net/wiki/spaces/X/pages/123456/Title
  python tools/confluence_fetch_page.py --page-id 123456 --out project/docs

  # Một trang + toàn bộ cây con
  python tools/confluence_fetch_page.py --page-id 123456 --out project/docs --recursive

  # Tất cả trang con của một folder/page cha
  python tools/confluence_fetch_page.py --parent-id 3755770163 --out project/docs
"""
from __future__ import annotations

import argparse
import re
import sys
import time
from pathlib import Path

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

import requests

sys.path.insert(0, str(Path(__file__).parent))
from credentials import load_atlassian_credentials

ROOT = Path(__file__).resolve().parent.parent


# ── Helpers ───────────────────────────────────────────────────────────────────

def _parse_page_id(url: str) -> str:
    m = re.search(r"/pages/(\d+)", url)
    if m:
        return m.group(1)
    raise ValueError(f"Cannot extract page ID from URL: {url}")


def _safe_name(title: str) -> str:
    name = re.sub(r'[\\/*?:"<>|]', "-", title).strip().rstrip(".")
    return name[:120] or "untitled"


def _storage_to_md(html: str) -> str:
    try:
        from markdownify import markdownify
        return markdownify(html, heading_style="ATX", bullets="-")
    except ImportError:
        pass
    text = re.sub(r"<[^>]+>", "", html)
    text = text.replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">").replace("&nbsp;", " ")
    return text.strip()


# ── Confluence API ─────────────────────────────────────────────────────────────

def fetch_page_v2(page_id: str, api_v2: str, auth) -> dict | None:
    """Fetch page metadata + body via v2. Returns None if 404 (folder/not a page)."""
    r = requests.get(
        f"{api_v2}/pages/{page_id}",
        auth=auth,
        params={"body-format": "storage"},
        headers={"Accept": "application/json"},
        timeout=60,
    )
    if r.status_code == 404:
        return None
    r.raise_for_status()
    return r.json()


def fetch_title_v1(page_id: str, api_v1: str, auth) -> str:
    """Fetch title of a folder or page via v1 API, with CQL fallback for folder types."""
    # Try v1 content endpoint (works for pages)
    try:
        r = requests.get(
            f"{api_v1}/content/{page_id}",
            auth=auth,
            params={"expand": "title"},
            headers={"Accept": "application/json"},
            timeout=30,
        )
        if r.status_code == 200:
            return r.json().get("title", f"folder-{page_id}")
    except Exception:
        pass
    # Fallback: CQL search by ID (works for folder types that 404 on /content/{id})
    try:
        cql = f"id={page_id}"
        r2 = requests.get(
            f"{api_v1}/content/search",
            auth=auth,
            params={"cql": cql, "limit": 1},
            headers={"Accept": "application/json"},
            timeout=30,
        )
        if r2.status_code == 200:
            results = r2.json().get("results", [])
            if results:
                return results[0].get("title", f"folder-{page_id}")
    except Exception:
        pass
    return f"folder-{page_id}"


def get_children(page_id: str, api_v1: str, auth) -> list[dict]:
    """List direct child pages via v1 API, with CQL fallback for folder types."""
    results: list[dict] = []
    # Try v1 child/page endpoint
    try:
        start = 0
        while True:
            r = requests.get(
                f"{api_v1}/content/{page_id}/child/page",
                auth=auth,
                params={"limit": 50, "start": start},
                headers={"Accept": "application/json"},
                timeout=30,
            )
            if r.status_code != 200:
                break
            d = r.json()
            batch = d.get("results", [])
            results.extend(batch)
            if len(batch) < 50:
                break
            start += len(batch)
        if results:
            return results
    except Exception:
        pass
    # Fallback: CQL ancestor search (works for folder types)
    try:
        cql = f"ancestor={page_id} AND depth=1"
        start = 0
        while True:
            r2 = requests.get(
                f"{api_v1}/content/search",
                auth=auth,
                params={"cql": cql, "limit": 50, "start": start},
                headers={"Accept": "application/json"},
                timeout=30,
            )
            if r2.status_code != 200:
                break
            d2 = r2.json()
            batch = d2.get("results", [])
            results.extend(batch)
            if len(batch) < 50:
                break
            start += len(batch)
    except Exception:
        pass
    return results


# ── Core sync ──────────────────────────────────────────────────────────────────

def sync_page(
    page_id: str,
    api_v2: str,
    api_v1: str,
    auth,
    out_dir: Path,
    recursive: bool,
    depth: int = 0,
    delay: float = 0.2,
) -> None:
    indent = "  " * depth
    data = fetch_page_v2(page_id, api_v2, auth)

    if data is None:
        # Folder — no body, just recurse into children
        title = fetch_title_v1(page_id, api_v1, auth)
        print(f"{indent}📁 {title} (folder)")
        if recursive:
            sub_dir = out_dir / _safe_name(title)
            for child in get_children(page_id, api_v1, auth):
                time.sleep(delay)
                sync_page(str(child["id"]), api_v2, api_v1, auth, sub_dir, recursive, depth + 1, delay)
        return

    title = data.get("title", f"page-{page_id}")
    body  = data.get("body", {}).get("storage", {}).get("value", "")
    md    = _storage_to_md(body)

    children = get_children(page_id, api_v1, auth) if recursive else []

    if children:
        # Has children → save as index.md inside a named subdirectory
        page_dir = out_dir / _safe_name(title)
        page_dir.mkdir(parents=True, exist_ok=True)
        out_file = page_dir / "index.md"
        out_file.write_text(f"# {title}\n\n{md}\n", encoding="utf-8")
        print(f"{indent}📁 {out_file.relative_to(ROOT)}")
        for child in children:
            time.sleep(delay)
            sync_page(str(child["id"]), api_v2, api_v1, auth, page_dir, recursive, depth + 1, delay)
    else:
        # Leaf page → save as {title}.md
        out_dir.mkdir(parents=True, exist_ok=True)
        out_file = out_dir / f"{_safe_name(title)}.md"
        out_file.write_text(f"# {title}\n\n{md}\n", encoding="utf-8")
        print(f"{indent}📄 {out_file.relative_to(ROOT)}")


# ── CLI ────────────────────────────────────────────────────────────────────────

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    src = parser.add_mutually_exclusive_group(required=True)
    src.add_argument("--url",       help="Confluence page URL")
    src.add_argument("--page-id",   help="Confluence page ID (numeric)")
    src.add_argument("--parent-id", help="Sync all children under this folder/page ID")
    parser.add_argument("--out",       default="project/docs",
                        help="Output folder (default: project/docs)")
    parser.add_argument("--recursive", "-r", action="store_true",
                        help="Fetch children recursively, mirror folder structure")
    parser.add_argument("--delay",     type=float, default=0.2,
                        help="Delay between API calls in seconds (default: 0.2)")
    parser.add_argument("--stdout",    action="store_true",
                        help="Print first page Markdown to stdout (single page only)")
    args = parser.parse_args()

    email, token, base_url = load_atlassian_credentials()
    api_v2 = f"{base_url.rstrip('/')}/wiki/api/v2"
    api_v1 = f"{base_url.rstrip('/')}/wiki/rest/api"
    auth   = (email, token)

    out_dir = Path(args.out)
    if not out_dir.is_absolute():
        out_dir = ROOT / out_dir

    # ── --parent-id: sync all children of a folder/page ───────────────────────
    if args.parent_id:
        title = fetch_title_v1(args.parent_id, api_v1, auth)
        parent_dir = out_dir / _safe_name(title)
        print(f"Parent : {title} (id={args.parent_id})")
        children = get_children(args.parent_id, api_v1, auth)
        print(f"Children: {len(children)} → {parent_dir.relative_to(ROOT)}")
        for child in children:
            sync_page(str(child["id"]), api_v2, api_v1, auth, parent_dir,
                      recursive=True, depth=0, delay=args.delay)
            time.sleep(args.delay)
        return 0

    # ── --url / --page-id: single page (optionally recursive) ─────────────────
    page_id = args.page_id or _parse_page_id(args.url)

    if args.stdout:
        data = fetch_page_v2(page_id, api_v2, auth)
        if data is None:
            print("ERROR: page not found or is a folder", file=sys.stderr)
            return 1
        title = data.get("title", "")
        body  = data.get("body", {}).get("storage", {}).get("value", "")
        print(f"# {title}\n\n{_storage_to_md(body)}\n")
        return 0

    sync_page(page_id, api_v2, api_v1, auth, out_dir,
              recursive=args.recursive, depth=0, delay=args.delay)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
