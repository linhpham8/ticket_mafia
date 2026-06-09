#!/usr/bin/env python3
"""
Cập nhật thông tin test case trong QMetry.

Endpoint: PUT /rest/api/latest/testcases/{tcKey}/versions/{versionNo}
→ 204 No Content = success

Usage:
  python tools/qmetry_update_testcase.py --tc FDP-TC-6 --show
  python tools/qmetry_update_testcase.py --tc FDP-TC-6 --summary "Tiêu đề mới"
  python tools/qmetry_update_testcase.py --tc FDP-TC-6 --priority High --labels "automation,regression"
  python tools/qmetry_update_testcase.py --tc FDP-TC-6 --from-json path/to/update.json
  python tools/qmetry_update_testcase.py --list-priorities
"""
import sys
import json
import argparse
import requests
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from qmetry_client import BASE, PROJECT_ID, HEADERS

# Priority name → ID (FDP project)
PRIORITY_MAP = {
    "blocker": 674921,
    "critical": 674921,
    "high":    674922,
    "medium":  674923,
    "low":     674924,
}


def get_testcase(tc_key, version_no=1):
    r = requests.get(
        f"{BASE}/rest/api/latest/testcases/{tc_key}/versions/{version_no}",
        headers=HEADERS, timeout=30,
    )
    if r.status_code == 200:
        return r.json().get("data", r.json())
    print(f"  ERROR fetching TC {tc_key}: {r.status_code} {r.text[:200]}")
    return None


def update_testcase(tc_key, updates: dict, version_no=1):
    r = requests.put(
        f"{BASE}/rest/api/latest/testcases/{tc_key}/versions/{version_no}",
        headers=HEADERS, json=updates, timeout=30,
    )
    return r.status_code, r.text if r.text.strip() else None


def resolve_priority(name_or_id):
    if isinstance(name_or_id, int):
        return name_or_id
    key = str(name_or_id).strip().lower()
    if key in PRIORITY_MAP:
        return PRIORITY_MAP[key]
    try:
        return int(name_or_id)
    except ValueError:
        pass
    print(f"  WARNING: unknown priority '{name_or_id}'. Valid: {list(PRIORITY_MAP.keys())}")
    return None


def parse_steps_from_text(text):
    steps = []
    for line in text.strip().splitlines():
        line = line.strip()
        if not line:
            continue
        parts = [p.strip() for p in line.split("|")]
        steps.append({
            "stepDetail":     parts[0] if len(parts) > 0 else "",
            "expectedResult": parts[1] if len(parts) > 1 else "",
            "testData":       parts[2] if len(parts) > 2 else "",
        })
    return steps


def print_tc(tc_data):
    print(f"\n{'─'*60}")
    print(f"  Key     : {tc_data.get('key')}")
    print(f"  ID      : {tc_data.get('id')}")
    ver = tc_data.get("version", {})
    print(f"  Version : {ver.get('versionNo')} (latest={ver.get('isLatestVersion')})")
    print(f"  Summary : {tc_data.get('summary', '-')}")
    pri = tc_data.get("priority")
    if isinstance(pri, dict):
        print(f"  Priority: {pri.get('name', pri.get('id', '-'))}")
    elif pri:
        rev = {v: k.capitalize() for k, v in PRIORITY_MAP.items()}
        print(f"  Priority: {rev.get(pri, pri)}")
    else:
        print(f"  Priority: -")
    labels = tc_data.get("labels", [])
    if labels:
        print(f"  Labels  : {', '.join(labels) if isinstance(labels, list) else labels}")
    print(f"{'─'*60}")


def main():
    parser = argparse.ArgumentParser(description="Cập nhật thông tin test case trong QMetry")
    parser.add_argument("--tc",           default="FDP-TC-6")
    parser.add_argument("--version",      type=int, default=1)
    parser.add_argument("--summary",      help="Tiêu đề test case")
    parser.add_argument("--precondition", help="Điều kiện tiên quyết")
    parser.add_argument("--description",  help="Mô tả chi tiết")
    parser.add_argument("--priority",     help="Blocker/High/Medium/Low")
    parser.add_argument("--labels",       help="Nhãn, phân cách bằng dấu phẩy")
    parser.add_argument("--steps",        help="Test steps: <step> | <expected> | <data>")
    parser.add_argument("--steps-file",   help="File .json chứa mảng testSteps")
    parser.add_argument("--from-json",    help="File JSON chứa toàn bộ payload update")
    parser.add_argument("--show",         action="store_true")
    parser.add_argument("--list-priorities", action="store_true")
    args = parser.parse_args()

    print(f"QMetry base : {BASE}")
    print(f"Project ID  : {PROJECT_ID}")

    if args.list_priorities:
        print("\nPriority IDs (FDP project):")
        for name, pid in PRIORITY_MAP.items():
            print(f"  {pid:>8}  {name.capitalize()}")
        return

    if args.show:
        tc = get_testcase(args.tc, args.version)
        if tc:
            print_tc(tc)
        return

    updates = {}
    if args.from_json:
        with open(args.from_json, encoding="utf-8") as f:
            updates = json.load(f)
    else:
        if args.summary:      updates["summary"]      = args.summary
        if args.precondition: updates["precondition"] = args.precondition
        if args.description:  updates["description"]  = args.description
        if args.priority:
            pri = resolve_priority(args.priority)
            if pri is not None:
                updates["priority"] = pri
        if args.labels:
            updates["label"] = [l.strip() for l in args.labels.split(",") if l.strip()]
        if args.steps:
            updates["testSteps"] = parse_steps_from_text(args.steps)
        if args.steps_file:
            with open(args.steps_file, encoding="utf-8") as f:
                updates["testSteps"] = json.load(f)

    if not updates:
        print("\nKhông có field nào được chỉ định. Dùng --help để xem cú pháp.")
        return

    print(f"\n[Before] Đang đọc TC {args.tc} v{args.version}...")
    tc_before = get_testcase(args.tc, args.version)
    if tc_before:
        print_tc(tc_before)

    print(f"\n[Update] Payload:")
    print(json.dumps(updates, ensure_ascii=False, indent=2))

    status, body = update_testcase(args.tc, updates, args.version)
    if status == 204:
        print(f"\n  SUCCESS: TC {args.tc} đã được cập nhật (HTTP 204).")
    else:
        print(f"\n  FAILED: HTTP {status}")
        if body:
            try:    print("  Response:", json.dumps(json.loads(body), ensure_ascii=False, indent=2))
            except: print("  Response:", body[:400])
        return

    print(f"\n[After] Xác nhận lại...")
    tc_after = get_testcase(args.tc, args.version)
    if tc_after:
        print_tc(tc_after)


if __name__ == "__main__":
    main()
