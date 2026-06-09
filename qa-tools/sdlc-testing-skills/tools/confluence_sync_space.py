#!/usr/bin/env python3
"""Sync a Confluence space or subtree to local (tree metadata only).

Writes artifacts to:
- docs/confluence/space-tree.md

When using --full, fetches page text and saves to:
- docs/confluence/pages/*.json (page metadata + text content)
"""

from __future__ import annotations

import argparse
import os
import re
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


import requests
import json

from credentials import load_atlassian_credentials
from html_to_md import convert


ROOT = Path(__file__).resolve().parent.parent
CONFLUENCE_ROOT = ROOT / "docs" / "confluence"
PAGES_DIR = CONFLUENCE_ROOT / "pages"
SPACE_TREE_PATH = CONFLUENCE_ROOT / "space-tree.md"

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")


class ConfluenceClient:
    def __init__(self, base_url: str, email: str, token: str):
        self.base_url = base_url.rstrip("/")
        self.api_v2 = f"{self.base_url}/wiki/api/v2"
        self.auth = (email, token)

    def get(self, path: str, params: dict | None = None) -> dict:
        response = requests.get(f"{self.api_v2}{path}", auth=self.auth, params=params or {}, timeout=60)
        response.raise_for_status()
        return response.json()

    def get_space_id(self, space_key: str) -> str:
        data = self.get("/spaces", {"keys": space_key, "limit": 1})
        results = data.get("results", [])
        if not results:
            raise RuntimeError(f"Space '{space_key}' not found")
        return str(results[0]["id"])

    def get_homepage_id(self, space_id: str) -> str:
        data = self.get(f"/spaces/{space_id}")
        return str(data.get("homepageId", ""))

    def get_page_meta(self, page_id: str) -> dict:
        return self.get(f"/pages/{page_id}")

    def get_children(self, page_id: str) -> list[dict]:
        results: list[dict] = []
        cursor = None
        while True:
            params = {"limit": 50}
            if cursor:
                params["cursor"] = cursor
            data = self.get(f"/pages/{page_id}/children", params)
            results.extend(data.get("results", []))
            next_link = data.get("_links", {}).get("next")
            if not next_link:
                return results
            match = re.search(r"cursor=([^&]+)", next_link)
            if not match:
                return results
            cursor = match.group(1)

    def get_page_body(self, page_id: str) -> str:
        data = self.get(f"/pages/{page_id}", {"body-format": "storage"})
        return data.get("body", {}).get("storage", {}).get("value", "")


def title_to_slug(title: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9\s-]", "", title)
    slug = re.sub(r"\s+", "-", slug.strip())
    return slug[:120] or "untitled"


def safe_filename(title: str) -> str:
    name = re.sub(r'[\\/*?:"<>|]', "-", title)
    name = re.sub(r"\s+", " ", name).strip().rstrip(".")
    return name[:120] or "untitled"


@dataclass
class PageRecord:
    page_id: str
    title: str
    depth: int
    parent_id: str
    path_parts: list[str]
    has_children: bool


def build_tree(
    client: ConfluenceClient,
    page_id: str,
    depth: int = 0,
    collected: Optional[list[PageRecord]] = None,
    path_parts: Optional[list[str]] = None,
    parent_id: str = "",
) -> tuple[str, list[PageRecord]]:
    if collected is None:
        collected = []
    if path_parts is None:
        path_parts = []

    meta = client.get_page_meta(page_id)
    title = str(meta.get("title", f"Page {page_id}"))
    children = client.get_children(page_id)
    indent = "  " * depth
    current_path_parts = path_parts + [safe_filename(title)]

    collected.append(
        PageRecord(
            page_id=str(page_id),
            title=title,
            depth=depth,
            parent_id=parent_id,
            path_parts=current_path_parts,
            has_children=bool(children),
        )
    )

    if children:
        lines = [f"{indent}📁 **{title}** (ID: `{page_id}`)"]
        for child in children:
            child_text, _ = build_tree(
                client,
                str(child["id"]),
                depth + 1,
                collected,
                current_path_parts,
                str(page_id),
            )
            lines.append(child_text)
        return "\n".join(lines), collected
    return f"{indent}**{title}** (ID: `{page_id}`)", collected


def write_space_tree(space_key: str, space_id: str, homepage_id: str, pages: list[PageRecord], tree_text: str, out_path: Path) -> None:
    CONFLUENCE_ROOT.mkdir(parents=True, exist_ok=True)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    now = time.strftime("%Y-%m-%d %H:%M")
    content = [
        f"# {space_key} Confluence Space Tree",
        "",
        f"Space ID: `{space_id}` | Homepage ID: `{homepage_id}`",
        "",
        f"_Last synced: {now} - {len(pages)} pages_",
        "",
        "---",
        "",
        tree_text,
        "",
    ]
    out_path.write_text("\n".join(content), encoding="utf-8")


def resolve_output_paths(record: PageRecord, preserve_tree: bool, used_paths: dict[str, str]) -> tuple[Path, Path]:
    if preserve_tree:
        out_dir = PAGES_DIR.joinpath(*record.path_parts[:-1]) if len(record.path_parts) > 1 else PAGES_DIR
        stem = record.path_parts[-1]
    else:
        out_dir = PAGES_DIR
        stem = title_to_slug(record.title)

    stem_path = out_dir / stem
    key = os.path.normcase(str(stem_path))
    if key in used_paths and used_paths[key] != record.page_id:
        stem_path = out_dir / f"{stem}-{record.page_id}"
        key = os.path.normcase(str(stem_path))
    used_paths[key] = record.page_id

    return stem_path.with_suffix(".md"), stem_path.with_suffix(".json")


def resolve_tree_out(argument: str) -> Path:
    if not argument:
        return SPACE_TREE_PATH
    path = Path(argument)
    return path if path.is_absolute() else ROOT / path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--full", action="store_true", help="Also fetch HTML bodies and generate Markdown files")
    parser.add_argument("--space-key", default="", help="Override CONFLUENCE_SPACE_KEY")
    parser.add_argument("--limit", type=int, default=0, help="Max pages to fetch in full mode")
    parser.add_argument("--parent-id", default="", help="Fetch a subtree under this page ID")
    parser.add_argument("--delay", type=float, default=0.2, help="Delay between page fetches in seconds")
    parser.add_argument("--preserve-tree", action="store_true", help="Save pages into folders matching the Confluence hierarchy")
    parser.add_argument("--tree-out", default="", help="Tree markdown output path (default: docs/confluence/space-tree.md)")
    args = parser.parse_args()

    email, token, base_url, default_space_key = load_atlassian_credentials(require_space_key=True)
    space_key = args.space_key or default_space_key
    client = ConfluenceClient(base_url, email, token)

    PAGES_DIR.mkdir(parents=True, exist_ok=True)

    print(f"Looking up space '{space_key}'...")
    space_id = client.get_space_id(space_key)
    homepage_id = client.get_homepage_id(space_id)
    root_id = args.parent_id or homepage_id
    print(f"  Space ID: {space_id} | Homepage ID: {homepage_id} | Root ID: {root_id}")

    print("Building page tree...")
    tree_text, all_pages = build_tree(client, root_id)
    tree_out = resolve_tree_out(args.tree_out)
    write_space_tree(space_key, space_id, homepage_id, all_pages, tree_text, tree_out)
    print(f"Saved: {tree_out}")

    if not args.full:
        return 0

    pages_to_fetch = all_pages[: args.limit] if args.limit > 0 else all_pages
    print(f"Fetching {len(pages_to_fetch)} page(s)...")

    def minimal_page_json(meta: dict) -> dict:
        # Lấy các trường metadata cần thiết
        return {
            "title": meta.get("title"),
            "page_id": meta.get("id"),
            "url": f"{base_url.rstrip('/')}/wiki/pages/{meta.get('id')}",
            "updated": (meta.get("version") or {}).get("when"),
            "creator": ((meta.get("version") or {}).get("by") or {}).get("displayName"),
            "space_id": meta.get("spaceId"),
            "parent_id": meta.get("parentId"),
        }

    used_paths: dict[str, str] = {}
    for index, record in enumerate(pages_to_fetch, start=1):
        page_id = record.page_id
        title = record.title
        md_path, json_path = resolve_output_paths(record, args.preserve_tree, used_paths)
        try:
            meta = client.get_page_meta(page_id)
            body = client.get_page_body(page_id)
            md_path.parent.mkdir(parents=True, exist_ok=True)
            page_url = f"{base_url.rstrip('/')}/wiki/pages/{page_id}"
            markdown_body = convert(body)
            md_path.write_text(f"# {title}\n\n<{page_url}>\n\n{markdown_body}\n", encoding="utf-8")
            # Save JSON chỉ với metadata cần thiết
            json_data = minimal_page_json(meta)
            json_path.write_text(json.dumps(json_data, ensure_ascii=False, indent=2), encoding="utf-8")
            print(f"  [{index}/{len(pages_to_fetch)}] {md_path.relative_to(ROOT)} + .json")
        except Exception as exc:
            print(f"  [error] {title} ({page_id}): {exc}")
        time.sleep(args.delay)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
