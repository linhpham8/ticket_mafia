#!/usr/bin/env python3
"""Sync Jira issues to local JSON + Markdown snapshots."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import requests

from credentials import get_env, load_atlassian_credentials


ROOT = Path(__file__).resolve().parent.parent
JIRA_ROOT = ROOT / "docs" / "jira"
SEARCH_DIR = JIRA_ROOT / "searches"
ISSUE_DIR = JIRA_ROOT / "issues"
APPLICATION_JSON = "application/json"


def adf_to_markdown(adf: dict) -> str:
    # Chuyển đổi đơn giản một số loại node phổ biến từ Jira ADF sang Markdown
    if not adf or not isinstance(adf, dict) or "content" not in adf:
        return ""
    lines = []
    for node in adf["content"]:
        t = node.get("type")
        if t == "heading":
            level = node.get("attrs", {}).get("level", 2)
            text = "".join([c.get("text", "") for c in node.get("content", [])])
            lines.append(f"{'#'*level} {text}")
        elif t == "paragraph":
            segs = []
            for c in node.get("content", []):
                if c.get("type") == "text":
                    txt = c.get("text", "")
                    marks = c.get("marks", [])
                    for m in marks:
                        if m.get("type") == "strong":
                            txt = f"**{txt}**"
                        if m.get("type") == "em":
                            txt = f"*{txt}*"
                        if m.get("type") == "code":
                            txt = f"`{txt}`"
                    segs.append(txt)
            lines.append(" ".join(segs))
        elif t == "bulletList":
            for item in node.get("content", []):
                for para in item.get("content", []):
                    if para.get("type") == "paragraph":
                        txt = "".join([c.get("text", "") for c in para.get("content", [])])
                        lines.append(f"- {txt}")
        elif t == "orderedList":
            idx = 1
            for item in node.get("content", []):
                for para in item.get("content", []):
                    if para.get("type") == "paragraph":
                        txt = "".join([c.get("text", "") for c in para.get("content", [])])
                        lines.append(f"{idx}. {txt}")
                        idx += 1
        # Có thể mở rộng thêm các loại node khác nếu cần
    return "\n\n".join(lines)

def write_markdown_summary(out_path: Path, title: str, issues: list[dict], query_text: str) -> None:
    lines = [f"# {title}", "", f"- query: {query_text}", f"- total: {len(issues)}", "", "| Key | Summary | Status | Assignee |", "|---|---|---|---|"]
    for issue in issues:
        fields = issue.get("fields", {})
        status = (fields.get("status") or {}).get("name", "")
        assignee = ((fields.get("assignee") or {}).get("displayName") or "Unassigned")
        summary = (fields.get("summary") or "").replace("|", "/")
        lines.append(f"| {issue.get('key', '')} | {summary} | {status} | {assignee} |")
        # Thêm description nếu có
        desc = fields.get("description")
        if isinstance(desc, dict) and desc.get("type") == "doc":
            md_desc = adf_to_markdown(desc)
            if md_desc.strip():
                lines.append("\n## Description\n")
                lines.append(md_desc)
        elif isinstance(desc, str) and desc.strip():
            lines.append("\n## Description\n")
            lines.append(desc.strip())
    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def search_issues(base_url: str, auth: tuple[str, str], jql: str, fields: list[str], max_results: int) -> dict:
    url = f"{base_url}/rest/api/3/search/jql"
    payload = {"jql": jql, "fields": fields, "maxResults": max_results}
    response = requests.post(
        url,
        auth=auth,
        headers={"Content-Type": APPLICATION_JSON, "Accept": APPLICATION_JSON},
        json=payload,
        timeout=60,
    )
    response.raise_for_status()
    return response.json()


def get_issue(base_url: str, auth: tuple[str, str], issue_key: str) -> dict:
    url = f"{base_url}/rest/api/3/issue/{issue_key}"
    response = requests.get(url, auth=auth, headers={"Accept": APPLICATION_JSON}, timeout=60)
    response.raise_for_status()
    return response.json()



# Hàm tối ưu chỉ lấy các trường cần thiết cho JSON
def minimal_issue_json(issue: dict) -> dict:
    fields = issue.get("fields", {})
    # Sprint có thể là list hoặc customfield_xxx, fixVersions là list, parent là dict
    sprint = None
    # Tìm trường Sprint (tùy Jira, có thể là 'customfield_10020' hoặc tên khác)
    for k in fields:
        if k.lower().startswith("customfield") and isinstance(fields[k], list):
            # Sprint thường là list có name
            if fields[k] and isinstance(fields[k][0], dict) and "name" in fields[k][0]:
                sprint = [s.get("name") for s in fields[k] if "name" in s]
                break
    fix_versions = [v.get("name") for v in fields.get("fixVersions", []) if "name" in v]
    parent = fields.get("parent")
    parent_key = parent.get("key") if parent and isinstance(parent, dict) else None
    return {
        "key": issue.get("key"),
        "summary": fields.get("summary"),
        "status": (fields.get("status") or {}).get("name"),
        "assignee": ((fields.get("assignee") or {}).get("displayName")),
        "priority": (fields.get("priority") or {}).get("name"),
        "labels": fields.get("labels"),
        "updated": fields.get("updated"),
        "sprint": sprint,
        "fixVersions": fix_versions,
        "parent": parent_key,
    }

def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--jql", default="", help="Custom JQL to sync")
    parser.add_argument("--project", default="", help="Override JIRA_PROJECT_KEY")
    parser.add_argument("--issue", default="", help="Fetch a single issue key")
    parser.add_argument("--max-results", type=int, default=50, help="Search result cap")
    parser.add_argument("--fields", nargs="*", default=["summary", "status", "assignee", "issuetype", "priority", "labels", "updated", "fixVersions", "parent"], help="Fields to fetch")
    args = parser.parse_args()

    email, token, base_url = load_atlassian_credentials()
    project_key = args.project or get_env("JIRA_PROJECT_KEY")
    auth = (email, token)

    SEARCH_DIR.mkdir(parents=True, exist_ok=True)
    ISSUE_DIR.mkdir(parents=True, exist_ok=True)

    if args.issue:
        issue = get_issue(base_url, auth, args.issue)
        json_path = ISSUE_DIR / f"{args.issue}.json"
        md_path = ISSUE_DIR / f"{args.issue}.md"
        # Lưu JSON tối ưu
        json_path.write_text(json.dumps(minimal_issue_json(issue), ensure_ascii=False, indent=2), encoding="utf-8")
        write_markdown_summary(md_path, f"Jira Issue {args.issue}", [issue], args.issue)
        print(f"JSON_SAVED: {json_path}")
        print(f"MD_SAVED: {md_path}")
        return

    jql = args.jql or f"project = {project_key} ORDER BY updated DESC"
    result = search_issues(base_url, auth, jql, args.fields, args.max_results)
    safe_name = "jira-search-" + str(abs(hash(jql)))
    json_path = SEARCH_DIR / f"{safe_name}.json"
    md_path = SEARCH_DIR / f"{safe_name}.md"
    # Lưu danh sách JSON tối ưu
    issues_min = [minimal_issue_json(i) for i in result.get("issues", [])]
    json_path.write_text(json.dumps(issues_min, ensure_ascii=False, indent=2), encoding="utf-8")
    write_markdown_summary(md_path, "Jira Search Result", result.get("issues", []), jql)
    print(f"JSON_SAVED: {json_path}")
    print(f"MD_SAVED: {md_path}")
    print(f"TOTAL: {len(result.get('issues', []))}")


if __name__ == "__main__":
    main()
