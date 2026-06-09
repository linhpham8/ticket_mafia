#!/usr/bin/env python3
"""
Tạo sub-task Jira dưới 1 parent issue.
Yêu cầu: đã có file credentials.py (giống các script sync Jira khác)
Usage:
  python tools/jira_create_subtask.py --parent FDP-382 --summary "Tên subtask" --assignee "email hoặc accountId"
"""
import argparse
import json
from pathlib import Path
import requests
from credentials import load_atlassian_credentials

APPLICATION_JSON = "application/json"

parser = argparse.ArgumentParser(description="Tạo sub-task Jira dưới parent issue.")
parser.add_argument("--parent", required=True, help="Parent issue key (ví dụ: FDP-382)")
parser.add_argument("--summary", required=True, help="Tiêu đề sub-task")
parser.add_argument("--description", default=None, help="Nội dung chi tiết cho sub-task (markdown hoặc text)")
parser.add_argument("--assignee", default=None, help="Assignee (email hoặc accountId, tuỳ cấu hình Jira)")
parser.add_argument("--project", default=None, help="Project key (nếu cần)")
args = parser.parse_args()

email, token, base_url = load_atlassian_credentials()
auth = (email, token)

# Lấy project key nếu chưa có
if not args.project:
    # Gọi API lấy parent issue
    url = f"{base_url}/rest/api/3/issue/{args.parent}"
    resp = requests.get(url, auth=auth, headers={"Accept": APPLICATION_JSON}, timeout=60)
    resp.raise_for_status()
    parent_issue = resp.json()
    project_key = parent_issue["fields"]["project"]["key"]
else:
    project_key = args.project

# Tìm issueType id cho sub-task
url = f"{base_url}/rest/api/3/issuetype"
resp = requests.get(url, auth=auth, headers={"Accept": APPLICATION_JSON}, timeout=60)
resp.raise_for_status()
types = resp.json()
subtask_type = next((t for t in types if t.get("subtask") and t["name"].lower().startswith("sub-task")), None)
if not subtask_type:
    raise RuntimeError("Không tìm thấy issueType sub-task trên Jira này!")


payload = {
    "fields": {
        "project": {"key": project_key},
        "parent": {"key": args.parent},
        "summary": args.summary,
        "issuetype": {"id": subtask_type["id"]},
    }
}
if args.description:
    payload["fields"]["description"] = args.description
if args.assignee:
    payload["fields"]["assignee"] = {"name": args.assignee}  # Có thể cần đổi thành "accountId"

url = f"{base_url}/rest/api/3/issue"
resp = requests.post(url, auth=auth, headers={"Content-Type": APPLICATION_JSON, "Accept": APPLICATION_JSON}, json=payload, timeout=60)
if resp.status_code >= 300:
    print("Lỗi tạo sub-task:", resp.text)
    exit(1)
result = resp.json()
print("Tạo sub-task thành công:", result)
