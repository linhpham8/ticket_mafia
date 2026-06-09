#!/usr/bin/env python3
"""
Bulk update QMetry execution status cho nhiều test case cùng lúc.

Input: TSV file, danh sách TC từ CLI, hoặc folder ID.

TSV format (có header):
  tc_key  tc_id  status  comment
  FDP-TC-1  abc123  Pass
  FDP-TC-2  def456  Fail  Bug found in login

Usage:
  # Từ file TSV
  python tools/qmetry_bulk_status.py --cycle FDP-TR-1 --cycle-id NMMUa7miAok4R --file updates.tsv

  # Từ CLI (tất cả TC cùng status)
  python tools/qmetry_bulk_status.py --cycle FDP-TR-1 --cycle-id NMMUa7miAok4R \\
      --tcs "FDP-TC-1:abc123,FDP-TC-2:def456" --status Pass

  # Từ folder ID (link + update tất cả TC trong folder)
  python tools/qmetry_bulk_status.py --cycle FDP-TR-1 --cycle-id NMMUa7miAok4R \\
      --folder-id 2489720 --status Fail

  # Dry-run
  python tools/qmetry_bulk_status.py --cycle FDP-TR-1 --cycle-id NMMUa7miAok4R \\
      --folder-id 2489720 --status Fail --dry-run
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from qmetry_client import (
    BASE, PROJECT_ID,
    STATUS_MAP, get_status_id, update_status, get_testcases_in_folder,
)


def load_tsv(path: Path) -> list[dict]:
    """
    Parse TSV. Required column: tc_key.
    Optional: tc_id, status, comment.
    """
    rows = []
    with open(path, encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f, delimiter="\t")
        for row in reader:
            rows.append({k.strip().lower(): v.strip() for k, v in row.items()})
    return rows


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--cycle",     required=True, help="Test cycle key (e.g. FDP-TR-1)")
    parser.add_argument("--cycle-id",  required=True, help="Test cycle internal ID")
    parser.add_argument("--file",      help="TSV file: tc_key, tc_id, status, comment")
    parser.add_argument("--tcs",       help="Comma list: 'KEY:ID,KEY:ID,...'")
    parser.add_argument("--folder-id", type=int,
                        help="QMetry testcase folder ID — fetch all TCs in folder and link+update")
    parser.add_argument("--status",   default="Pass",
                        help="Default status khi không có trong file (default: Pass)")
    parser.add_argument("--comment",  default="", help="Default comment")
    parser.add_argument("--delay",    type=float, default=0.3,
                        help="Giây chờ giữa các request (default: 0.3)")
    parser.add_argument("--dry-run",  action="store_true",
                        help="Preview only, không thực sự update")
    parser.add_argument("--list-statuses", action="store_true")
    args = parser.parse_args()

    print(f"QMetry base : {BASE}")
    print(f"Project ID  : {PROJECT_ID}")

    if args.list_statuses:
        print("\nStatus IDs:")
        for name, sid in STATUS_MAP.items():
            print(f"  {sid:>8}  {name.capitalize()}")
        return 0

    if not args.file and not args.tcs and not args.folder_id:
        print("ERROR: phải truyền --file, --tcs hoặc --folder-id")
        return 1

    # Build task list
    tasks: list[dict] = []

    if args.folder_id:
        print(f"Fetching TCs from folder {args.folder_id} ...")
        tcs = get_testcases_in_folder(args.folder_id)

        # Fallback: đọc từ push report nếu API không hỗ trợ folder listing
        if not tcs:
            root = Path(__file__).parent.parent
            report_path = root / "testing-output" / "qmetry" / "qmetry-folder-push-report.json"
            if report_path.exists():
                print(f"  Folder API unavailable — reading from push report: {report_path.name}")
                with open(report_path, encoding="utf-8") as f:
                    report = json.load(f)
                tcs = [
                    {"key": r["key"], "id": r["id"]}
                    for r in report
                    if r.get("result") == "created"
                    and r.get("folderId") == args.folder_id
                    and r.get("key") and r.get("id")
                ]
                if tcs:
                    print(f"  Found {len(tcs)} TCs in push report for folder {args.folder_id}")

        if not tcs:
            print(f"ERROR: không tìm thấy TC nào cho folder {args.folder_id} (API + push report)")
            return 1

        for tc in tcs:
            tasks.append({
                "tc_key":  tc["key"],
                "tc_id":   tc["id"],
                "status":  args.status,
                "comment": args.comment,
            })
    elif args.file:
        rows = load_tsv(Path(args.file))
        for row in rows:
            tasks.append({
                "tc_key":  row.get("tc_key", ""),
                "tc_id":   row.get("tc_id", ""),
                "status":  row.get("status", "") or args.status,
                "comment": row.get("comment", "") or args.comment,
            })
    elif args.tcs:
        for pair in args.tcs.split(","):
            pair = pair.strip()
            if ":" in pair:
                key, tc_id = pair.split(":", 1)
            else:
                key, tc_id = pair, ""
            tasks.append({
                "tc_key": key.strip(),
                "tc_id":  tc_id.strip(),
                "status": args.status,
                "comment": args.comment,
            })

    tasks = [t for t in tasks if t["tc_key"]]
    if not tasks:
        print("Không có TC nào để xử lý.")
        return 0

    print(f"\nCycle : {args.cycle} (id={args.cycle_id})")
    print(f"Tasks : {len(tasks)} TC")
    if args.dry_run:
        print("(Dry-run — no changes)\n")

    counts = {"ok": 0, "skip": 0, "error": 0}

    for i, t in enumerate(tasks, 1):
        tc_key  = t["tc_key"]
        tc_id   = t["tc_id"]
        status  = t["status"]
        comment = t["comment"]

        print(f"\n[{i}/{len(tasks)}] {tc_key} → {status}" +
              (f"  # {comment}" if comment else ""))

        if get_status_id(status) is None:
            counts["error"] += 1
            continue

        if args.dry_run:
            counts["skip"] += 1
            continue

        if not tc_id:
            print("  WARNING: tc_id trống — ensure_tc_linked sẽ bị skip")

        ok = update_status(
            cycle_key  = args.cycle,
            cycle_id   = getattr(args, "cycle_id"),
            tc_key     = tc_key,
            tc_id      = tc_id,
            status_name= status,
            comment    = comment,
        )
        counts["ok" if ok else "error"] += 1
        if i < len(tasks):
            time.sleep(args.delay)

    print(f"\n{'─'*50}")
    print(f"  Success : {counts['ok']}")
    print(f"  Skipped : {counts['skip']}")
    print(f"  Errors  : {counts['error']}")
    if args.dry_run:
        print("  (Dry-run — no changes made)")
    print(f"{'─'*50}")
    return 0 if counts["error"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
