#!/usr/bin/env python3
"""Fetch the most relevant Confluence pages for a natural-language query."""

from __future__ import annotations

import argparse
import base64
import json
import re
import urllib.request
from pathlib import Path

from credentials import get_env
from html_to_md import convert


ROOT = Path(__file__).resolve().parent.parent
CONFLUENCE_ROOT = ROOT / "docs" / "confluence"
SPACE_TREE = CONFLUENCE_ROOT / "space-tree.md"
PAGES_DIR = CONFLUENCE_ROOT / "pages"
STOPWORDS = {
    "the", "a", "an", "is", "are", "was", "were", "be", "been", "being", "have", "has", "had",
    "do", "does", "did", "will", "would", "could", "should", "may", "might", "shall", "can", "and",
    "or", "but", "in", "on", "at", "to", "for", "of", "with", "by", "from", "what", "how", "why",
    "when", "where", "which", "who", "this", "that", "these", "those", "about", "out", "as", "its",
    "it", "my", "me", "we", "our", "you",
}


def parse_space_tree() -> list[dict]:
    if not SPACE_TREE.exists():
        raise RuntimeError(f"{SPACE_TREE} not found. Run confluence_sync_space.py first.")

    pages: list[dict] = []
    folder_stack: list[str] = []
    for line in SPACE_TREE.read_text(encoding="utf-8").splitlines():
        match = re.search(r"\*\*(.+?)\*\*\s*\(ID:\s*`(\d+)`\)", line)
        if not match:
            continue
        title, page_id = match.groups()
        is_folder = "📁" in line
        depth = (len(line) - len(line.lstrip())) // 2
        folder_stack = folder_stack[:depth]
        context = " > ".join(folder_stack)
        pages.append({"title": title, "page_id": page_id, "context": context, "is_folder": is_folder})
        if is_folder:
            if len(folder_stack) <= depth:
                folder_stack.append(title)
            else:
                folder_stack[depth] = title
    return pages


def tokenize(text: str) -> set[str]:
    return {token.lower() for token in re.split(r"\W+", text) if len(token) > 2 and token.lower() not in STOPWORDS}


def score_pages(pages: list[dict], query: str, top_n: int) -> list[dict]:
    query_tokens = tokenize(query)
    scored: list[dict] = []
    for page in pages:
        if page["is_folder"]:
            continue
        title_tokens = tokenize(page["title"])
        context_tokens = tokenize(page["context"])
        title_exact = len(query_tokens & title_tokens) * 4
        context_exact = len(query_tokens & context_tokens)
        partial = sum(2 for left in query_tokens for right in title_tokens if left != right and (left in right or right in left))
        score = title_exact + context_exact + partial
        if score > 0:
            scored.append({**page, "score": score})
    return sorted(scored, key=lambda item: item["score"], reverse=True)[:top_n]


def title_to_slug(title: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9\s-]", "", title)
    slug = re.sub(r"\s+", "-", slug.strip())
    return slug[:120]


def fetch_page(page_id: str, title: str) -> Path:
    email = get_env("ATLASSIAN_EMAIL") or get_env("ATLASSIAN_USER_EMAIL")
    token = get_env("ATLASSIAN_API_TOKEN")
    base = get_env("ATLASSIAN_BASE_URL", "").rstrip("/")
    if not all([email, token, base]):
        raise RuntimeError("Missing Atlassian credentials for live fetch")

    creds = base64.b64encode(f"{email}:{token}".encode()).decode()
    request = urllib.request.Request(
        f"{base}/wiki/api/v2/pages/{page_id}?body-format=storage",
        headers={"Authorization": f"Basic {creds}", "Accept": "application/json"},
    )
    with urllib.request.urlopen(request, timeout=60) as response:
        data = json.load(response)

    slug = title_to_slug(title)
    md_path = PAGES_DIR / f"{slug}.md"
    json_path = PAGES_DIR / f"{slug}.json"
    body = data.get("body", {}).get("storage", {}).get("value", "")
    PAGES_DIR.mkdir(parents=True, exist_ok=True)
    md_path.write_text(convert(body), encoding="utf-8")
    # Save JSON with text content and metadata
    json_data = {
        "title": title,
        "page_id": page_id,
        "body_html": body,
        "text_content": convert(body)
    }
    json_path.write_text(json.dumps(json_data, ensure_ascii=False, indent=2), encoding="utf-8")
    return md_path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("query", nargs="+", help="Natural-language query")
    parser.add_argument("--top", type=int, default=5, help="Top N candidates to fetch")
    parser.add_argument("--no-fetch", action="store_true", help="Only show candidates, do not fetch missing pages")
    args = parser.parse_args()

    query = " ".join(args.query)
    candidates = score_pages(parse_space_tree(), query, args.top)
    if not candidates:
        print("No relevant pages found")
        return 0

    ready: list[Path] = []
    for index, page in enumerate(candidates, start=1):
        slug = title_to_slug(page["title"])
        md_path = PAGES_DIR / f"{slug}.md"
        print(f"{index}. {page['title']} [score={page['score']}] | context={page['context'] or '(root)'} | page_id={page['page_id']}")
        if md_path.exists() or args.no_fetch:
            ready.append(md_path)
            continue
        ready.append(fetch_page(page["page_id"], page["title"]))

    print("Files ready:")
    for path in ready:
        print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
