#!/usr/bin/env python3
"""
Update test case execution status in QMetry (single TC).

Usage:
  python tools/qmetry_update_status.py --tc FDP-TC-6 --cycle FDP-TR-1 --status Pass
  python tools/qmetry_update_status.py --tc FDP-TC-6 --cycle FDP-TR-1 --status Fail --comment "Bug found"
  python tools/qmetry_update_status.py --list-statuses
  python tools/qmetry_update_status.py --create-cycle "Sprint 12 Regression"

For bulk updates across many TCs use: qmetry_bulk_status.py
"""
import sys
import argparse
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from qmetry_client import (
    BASE, PROJECT_ID,
    STATUS_MAP,
    create_test_cycle, update_status,
    create_cycle_link_and_update, ensure_child_folder,
)


def main():
    parser = argparse.ArgumentParser(description="Update QMetry test case execution status")
    parser.add_argument("--cycle",      default="FDP-TR-1",      help="Test cycle key")
    parser.add_argument("--cycle-id",   default="NMMUa7miAok4R", help="Test cycle internal ID")
    parser.add_argument("--tc",         default="FDP-TC-6",      help="Test case key")
    parser.add_argument("--tc-id",      default="vZZI6ZJSm18k7", help="Test case internal ID")
    parser.add_argument("--status",     default="Pass",
                        help="Status: Pass/Fail/Blocked/WIP/Not Executed")
    parser.add_argument("--comment",    default="")
    parser.add_argument("--version",    type=int, default=1)
    parser.add_argument("--new-run",    action="store_true",
                        help="Create a new execution entry before updating")
    parser.add_argument("--list-statuses", action="store_true")
    parser.add_argument("--create-cycle",  metavar="NAME", help="Tạo test cycle mới rồi thoát")
    parser.add_argument("--cycle-desc",    metavar="DESC", default=None)
    parser.add_argument("--cycle-summary", metavar="SUMMARY", default=None)
    parser.add_argument("--cycle-start",   metavar="YYYY-MM-DD", default=None)
    parser.add_argument("--cycle-end",     metavar="YYYY-MM-DD", default=None)
    parser.add_argument("--cycle-folder-id", type=int,
                        help="Folder ID where a newly created cycle should be placed")
    parser.add_argument("--cycle-parent-folder-id", type=int,
                        help="Parent test cycle folder ID; used with --cycle-folder-name")
    parser.add_argument("--cycle-folder-name",
                        help="Find/create this child test cycle folder under --cycle-parent-folder-id")
    parser.add_argument("--create-cycle-link-update", metavar="NAME",
                        help="Create a cycle, link --tc/--tc-id, then update execution to --status")
    args = parser.parse_args()

    print(f"QMetry base : {BASE}")
    print(f"Project ID  : {PROJECT_ID}")

    if args.list_statuses:
        print("\nStatus IDs:")
        for name, sid in STATUS_MAP.items():
            print(f"  {sid:>8}  {name.capitalize()}")
        return

    resolved_cycle_folder_id = args.cycle_folder_id
    if args.cycle_parent_folder_id and args.cycle_folder_name:
        resolved_cycle_folder_id = ensure_child_folder(
            "testcycle",
            args.cycle_parent_folder_id,
            args.cycle_folder_name,
        )
        print(f"Cycle folder: {args.cycle_folder_name} (id={resolved_cycle_folder_id})")

    if args.create_cycle_link_update:
        info = create_cycle_link_and_update(
            cycle_name=args.create_cycle_link_update,
            folder_id=resolved_cycle_folder_id or -1,
            tc_key=args.tc,
            tc_id=getattr(args, "tc_id"),
            status_name=args.status,
            version_no=args.version,
            description=args.cycle_desc or "",
            comment=args.comment,
        )
        print("\nSUCCESS: Created cycle, linked testcase, and updated execution")
        print(json.dumps(info, ensure_ascii=False, indent=2))
        return

    if args.create_cycle:
        info = create_test_cycle(
            name=args.create_cycle,
            description=args.cycle_desc,
            summary=args.cycle_summary,
            start_date=args.cycle_start,
            end_date=args.cycle_end,
            folder_id=resolved_cycle_folder_id,
        )
        if info:
            print(f"Cycle: name='{info.get('name')}' id='{info.get('id')}' key='{info.get('key','')}'")
        return

    update_status(
        cycle_key   = args.cycle,
        cycle_id    = getattr(args, "cycle_id"),
        tc_key      = args.tc,
        tc_id       = getattr(args, "tc_id"),
        status_name = args.status,
        comment     = args.comment,
        version_no  = args.version,
        create_new  = args.new_run,
    )


if __name__ == "__main__":
    main()
