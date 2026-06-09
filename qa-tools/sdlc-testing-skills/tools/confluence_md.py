#!/usr/bin/env python3
"""
Shared module: convert Markdown → Confluence storage HTML and push (upsert).

Upsert logic:
  1. Check companion .json for page_id → UPDATE
  2. Find child of parent with matching title → UPDATE
  3. Neither found → CREATE under parent

API strategy:
  - Primary: Confluence API v2 (/wiki/api/v2)
  - Fallback: Confluence API v1 (/wiki/rest/api) when v2 returns 404

CLI (single file):
  python tools/confluence_md.py --file path/to/doc.md --parent-id 3814785380
  python tools/confluence_md.py --file path/to/doc.md --parent-id 3814785380 --dry-run
  python tools/confluence_md.py --file path/to/doc.md --parent-id 3814785380 --title "Override Title"
  python tools/confluence_md.py --file path/to/doc.md --page-id 3817046326
"""
from __future__ import annotations

import json
import re
import sys
import argparse
from datetime import datetime, timezone
from pathlib import Path

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

import markdown
import requests

sys.path.insert(0, str(Path(__file__).parent))
from credentials import load_atlassian_credentials


# ── MD → Confluence storage HTML ──────────────────────────────────────────────

def md_to_storage(text: str) -> str:
    return markdown.markdown(
        text,
        extensions=["tables", "fenced_code", "sane_lists", "nl2br"],
    )


# ── API base helpers ───────────────────────────────────────────────────────────

def _v1_base(api_base: str) -> str:
    """Derive API v1 base from v2 base URL."""
    return api_base.replace("/wiki/api/v2", "/wiki/rest/api")


def _auth(email: str, token: str):
    return (email, token)


# ── Confluence API helpers ─────────────────────────────────────────────────────

def get_page_meta(api_base: str, auth, page_id: str) -> dict:
    """
    Fetch page metadata. Tries API v2 first; falls back to v1 on 404.
    Returns normalized dict with at least: id, title, version.number, spaceId.
    Sets _use_v1=True when v1 fallback was used (update_page respects this).
    """
    r = requests.get(f"{api_base}/pages/{page_id}", auth=auth,
                     headers={"Accept": "application/json"}, timeout=60)
    if r.status_code != 404:
        r.raise_for_status()
        return r.json()

    # v2 returned 404 — fall back to API v1
    rv = requests.get(
        f"{_v1_base(api_base)}/content/{page_id}",
        params={"expand": "version,space"},
        auth=auth, headers={"Accept": "application/json"}, timeout=60,
    )
    rv.raise_for_status()
    d = rv.json()
    return {
        "id": str(d["id"]),
        "title": d["title"],
        "version": {"number": d["version"]["number"]},
        "spaceId": d["space"].get("key", ""),
        "_use_v1": True,
        "_space_key": d["space"].get("key", ""),
    }


def find_child_by_title(api_base: str, auth, parent_id: str, title: str) -> str | None:
    """Walk paginated v2 children; return page_id if title matches, else None."""
    cursor = None
    while True:
        params: dict = {"limit": 50}
        if cursor:
            params["cursor"] = cursor
        r = requests.get(f"{api_base}/pages/{parent_id}/children",
                         auth=auth, params=params,
                         headers={"Accept": "application/json"}, timeout=60)
        r.raise_for_status()
        data = r.json()
        for child in data.get("results", []):
            if child.get("title", "").strip() == title.strip():
                return str(child["id"])
        cursor_match = re.search(r"cursor=([^&]+)", data.get("_links", {}).get("next", ""))
        if not cursor_match:
            return None
        cursor = cursor_match.group(1)


def update_page(api_base: str, auth, page_id: str, title: str,
                body_html: str, message: str) -> dict:
    """
    Update existing page. Uses v2 normally; v1 when get_page_meta flagged _use_v1.
    """
    meta = get_page_meta(api_base, auth, page_id)
    new_version = meta["version"]["number"] + 1

    if meta.get("_use_v1"):
        payload = {
            "id": page_id,
            "type": "page",
            "title": title,
            "version": {"number": new_version},
            "body": {"storage": {"value": body_html, "representation": "storage"}},
        }
        r = requests.put(
            f"{_v1_base(api_base)}/content/{page_id}", auth=auth,
            headers={"Accept": "application/json",
                     "Content-Type": "application/json; charset=utf-8"},
            data=json.dumps(payload).encode("utf-8"), timeout=60,
        )
    else:
        payload = {
            "id": page_id,
            "status": "current",
            "title": title,
            "version": {"number": new_version, "message": message},
            "body": {"representation": "storage", "value": body_html},
        }
        r = requests.put(
            f"{api_base}/pages/{page_id}", auth=auth,
            headers={"Accept": "application/json",
                     "Content-Type": "application/json; charset=utf-8"},
            data=json.dumps(payload).encode("utf-8"), timeout=60,
        )
    r.raise_for_status()
    return r.json()


def create_page(api_base: str, auth, parent_id: str, space_id: str,
                title: str, body_html: str, message: str) -> dict:
    """
    Create new page under parent. Raises descriptive ValueError on title conflict (400).
    """
    payload = {
        "spaceId": space_id,
        "status": "current",
        "title": title,
        "parentId": parent_id,
        "body": {"representation": "storage", "value": body_html},
    }
    r = requests.post(
        f"{api_base}/pages", auth=auth,
        headers={"Accept": "application/json",
                 "Content-Type": "application/json; charset=utf-8"},
        data=json.dumps(payload).encode("utf-8"), timeout=60,
    )
    if r.status_code == 400:
        _check_title_conflict(r, title)
    r.raise_for_status()
    return r.json()


def _check_title_conflict(r: requests.Response, title: str) -> None:
    """Parse 400 response and raise ValueError if it's a title-already-exists conflict."""
    try:
        body = r.json()
        errors = body.get("errors", [])
        for e in errors:
            msg = (str(e.get("title", "")) + " " + str(e.get("detail", ""))).lower()
            if "title" in msg and ("exist" in msg or "unique" in msg or "duplicate" in msg):
                raise ValueError(
                    f"Title conflict: '{title}' already exists in this Confluence space.\n"
                    f"Fix: use --title 'A Different Title' to specify a unique name."
                )
    except ValueError:
        raise
    except Exception:
        pass  # Unknown 400 — let raise_for_status() report the raw error


# ── Sidebar JSON (page_id tracker) ────────────────────────────────────────────

def load_sidebar(md_path: Path) -> dict:
    json_path = md_path.with_suffix(".json")
    if json_path.exists():
        try:
            return json.loads(json_path.read_text(encoding="utf-8"))
        except Exception:
            return {}
    return {}


def save_sidebar(md_path: Path, page_id: str, title: str) -> None:
    json_path = md_path.with_suffix(".json")
    json_path.write_text(
        json.dumps({
            "page_id": page_id,
            "title": title,
            "pushed_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        }, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


# ── Core push function (reusable by all scripts) ───────────────────────────────

def push_md_file(
    md_path: Path,
    parent_id: str,
    space_id: str,
    api_base: str,
    auth,
    message: str = "Auto-push",
    dry_run: bool = False,
    title_override: str | None = None,
) -> tuple[str, str, str]:
    """
    Upsert one .md file to Confluence. Returns (action, page_id, title).
    action: "created" | "updated" | "dry-run"
    """
    md_text = md_path.read_text(encoding="utf-8")
    body_html = md_to_storage(md_text)

    title = title_override
    if not title:
        for line in md_text.splitlines():
            if line.startswith("# "):
                title = line[2:].strip()
                break
        if not title:
            title = md_path.stem.replace("-", " ").replace("_", " ")

    sidebar = load_sidebar(md_path)
    page_id = sidebar.get("page_id", "")
    if not page_id:
        page_id = find_child_by_title(api_base, auth, parent_id, title) or ""

    if dry_run:
        action = "update" if page_id else "create"
        print(f"  [dry-run] would {action}: '{title}'" +
              (f" (page_id={page_id})" if page_id else f" under parent {parent_id}"))
        return "dry-run", page_id, title

    if page_id:
        result = update_page(api_base, auth, page_id, title, body_html, message)
        new_id = str(result.get("id", page_id))
        action = "updated"
    else:
        result = create_page(api_base, auth, parent_id, space_id, title, body_html, message)
        new_id = str(result.get("id", ""))
        action = "created"

    save_sidebar(md_path, new_id, title)
    return action, new_id, title


# ── CLI ────────────────────────────────────────────────────────────────────────

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--file",      required=True, help="Path to .md file")
    grp = parser.add_mutually_exclusive_group(required=True)
    grp.add_argument("--page-id",   help="Update this specific page ID directly (v1 fallback if v2 404)")
    grp.add_argument("--parent-id", help="Upsert under this parent (create if not exists)")
    parser.add_argument("--title",   help="Override page title (default: first H1 or filename)")
    parser.add_argument("--message", default="Auto-push", help="Version message")
    parser.add_argument("--dry-run", action="store_true", help="Preview only, no changes")
    args = parser.parse_args()

    md_path = Path(args.file)
    if not md_path.is_absolute():
        md_path = Path(__file__).resolve().parent.parent / md_path
    if not md_path.exists():
        print(f"ERROR: file not found: {md_path}")
        return 1

    email, token, base_url = load_atlassian_credentials()
    api_base = f"{base_url.rstrip('/')}/wiki/api/v2"
    auth = _auth(email, token)

    md_text = md_path.read_text(encoding="utf-8")
    body_html = md_to_storage(md_text)
    title = args.title
    if not title:
        for line in md_text.splitlines():
            if line.startswith("# "):
                title = line[2:].strip()
                break
        if not title:
            title = md_path.stem.replace("-", " ").replace("_", " ")

    # ── Direct update mode (--page-id) ────────────────────────────────────────
    if args.page_id:
        print(f"File      : {md_path.name}")
        print(f"Page ID   : {args.page_id}")
        print(f"Title     : {title}")

        if args.dry_run:
            print(f"  [dry-run] would update page {args.page_id}: '{title}'")
            return 0

        result = update_page(api_base, auth, args.page_id, title, body_html, args.message)
        new_id = str(result.get("id", args.page_id))
        save_sidebar(md_path, new_id, title)
        url = f"{base_url.rstrip('/')}/wiki/pages/{new_id}"
        print(f"UPDATED: '{title}' → {url}")
        return 0

    # ── Upsert mode (--parent-id) ──────────────────────────────────────────────
    parent_meta = get_page_meta(api_base, auth, args.parent_id)
    space_id = str(parent_meta.get("spaceId", ""))

    print(f"File      : {md_path.name}")
    print(f"Parent    : '{parent_meta.get('title')}' (id={args.parent_id})")
    print(f"Space     : {space_id}")

    try:
        action, page_id, final_title = push_md_file(
            md_path=md_path,
            parent_id=args.parent_id,
            space_id=space_id,
            api_base=api_base,
            auth=auth,
            message=args.message,
            dry_run=args.dry_run,
            title_override=args.title,
        )
    except ValueError as e:
        print(f"ERROR: {e}")
        return 1

    if not args.dry_run:
        url = f"{base_url.rstrip('/')}/wiki/pages/{page_id}"
        print(f"{action.upper()}: '{final_title}' → {url}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
