#!/usr/bin/env python3
"""Convert a Markdown artifact to Confluence storage HTML and push it to a page."""

from __future__ import annotations

import argparse
import base64
import json
from pathlib import Path

import markdown
import requests

from credentials import load_atlassian_credentials


ROOT = Path(__file__).resolve().parent.parent


def markdown_to_storage_html(text: str) -> str:
    return markdown.markdown(text, extensions=["tables", "fenced_code", "sane_lists"])


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--markdown-file", required=True, help="Path to Markdown artifact")
    parser.add_argument("--page-id", required=True, help="Confluence page ID to update")
    parser.add_argument("--message", default="Published from testing-skills", help="Version message")
    args = parser.parse_args()

    markdown_path = Path(args.markdown_file)
    if not markdown_path.is_absolute():
        markdown_path = ROOT / markdown_path
    if not markdown_path.exists():
        raise RuntimeError(f"Markdown file not found: {markdown_path}")

    email, token, base_url = load_atlassian_credentials()
    api_base = f"{base_url.rstrip('/')}/wiki/api/v2"
    auth = (email, token)
    headers = {"Accept": "application/json", "Content-Type": "application/json; charset=utf-8"}

    meta = requests.get(f"{api_base}/pages/{args.page_id}", auth=auth, headers={"Accept": "application/json"}, timeout=60)
    meta.raise_for_status()
    meta_json = meta.json()

    body_html = markdown_to_storage_html(markdown_path.read_text(encoding="utf-8"))
    payload = {
        "id": args.page_id,
        "status": "current",
        "title": meta_json["title"],
        "version": {"number": meta_json["version"]["number"] + 1, "message": args.message},
        "body": {"representation": "storage", "value": body_html},
    }

    response = requests.put(f"{api_base}/pages/{args.page_id}", auth=auth, headers=headers, data=json.dumps(payload).encode("utf-8"), timeout=60)
    response.raise_for_status()
    print(f"UPDATED: {args.page_id}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
