#!/usr/bin/env python3
"""
Cập nhật nội dung (description) hoặc trạng thái (status) cho một issue Jira.
Usage:
  python tools/jira_update_issue.py --issue AISDLC-105 --description "Nội dung mới"
  python tools/jira_update_issue.py --issue AISDLC-105 --status "Done"
"""
import argparse
import json
import requests
from credentials import load_atlassian_credentials

APPLICATION_JSON = "application/json"

parser = argparse.ArgumentParser(description="Cập nhật nội dung hoặc trạng thái cho một issue Jira.")
parser.add_argument("--issue", required=True, help="Issue key (ví dụ: AISDLC-105)")
parser.add_argument("--description", default=None, help="Nội dung mới cho description")
parser.add_argument("--status", default=None, help="Tên trạng thái mới (Done, In Progress, ...)")
args = parser.parse_args()

email, token, base_url = load_atlassian_credentials()
auth = (email, token)

if args.description:
    url = f"{base_url}/rest/api/3/issue/{args.issue}"
    # Đóng gói description dạng Atlassian Document Format (ADF)
    adf = {
        "type": "doc",
        "version": 1,
        "content": [
            {
                "type": "paragraph",
                "content": [
                    {"type": "text", "text": args.description}
                ]
            }
        ]
    }
    payload = {"fields": {"description": adf}}
    resp = requests.put(url, auth=auth, headers={"Content-Type": APPLICATION_JSON, "Accept": APPLICATION_JSON}, json=payload, timeout=60)
    if resp.status_code >= 300:
        print("Lỗi cập nhật description:", resp.text)
        exit(1)
    print(f"Đã cập nhật description cho {args.issue}")

if args.status:
    # Lấy danh sách các transition hợp lệ
    url = f"{base_url}/rest/api/3/issue/{args.issue}/transitions"
    resp = requests.get(url, auth=auth, headers={"Accept": APPLICATION_JSON}, timeout=60)
    resp.raise_for_status()
    transitions = resp.json().get("transitions", [])
    # Tìm id của trạng thái cần chuyển
    target = next((t for t in transitions if t["name"].lower() == args.status.lower()), None)
    if not target:
        print(f"Không tìm thấy trạng thái '{args.status}' cho issue này. Các trạng thái hợp lệ:")
        for t in transitions:
            print("-", t["name"])
        exit(1)
    # Thực hiện chuyển trạng thái
    url = f"{base_url}/rest/api/3/issue/{args.issue}/transitions"
    payload = {"transition": {"id": target["id"]}}
    resp = requests.post(url, auth=auth, headers={"Content-Type": APPLICATION_JSON, "Accept": APPLICATION_JSON}, json=payload, timeout=60)
    if resp.status_code >= 300:
        print("Lỗi chuyển trạng thái:", resp.text)
        exit(1)
    print(f"Đã chuyển trạng thái {args.issue} sang '{args.status}'")
