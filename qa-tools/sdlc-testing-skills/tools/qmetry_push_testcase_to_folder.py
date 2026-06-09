#!/usr/bin/env python3
"""
Push TSV test cases to a specific QMetry Test Case folder.

Folder workflow for QTM4J Cloud:
  1. In QTM4J Test Case folders, right-click the target folder.
  2. Choose "Copy Folder Id".
  3. Pass that value via --folder-id.

Examples:
  python tools/qmetry_push_testcase_to_folder.py ^
    --tsv testing-output/test-cases/functional/tc-agent-lifecycle-mvp1.tsv ^
    --folder-id 12345 ^
    --max-rows 1

  python tools/qmetry_push_testcase_to_folder.py ^
    --tsv testing-output/test-cases/functional/tc-agent-lifecycle-mvp1.tsv ^
    --parent-folder-id 2475804 ^
    --folder-name fr-02 ^
    --max-rows 1
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import sys
from pathlib import Path

import requests
from dotenv import load_dotenv

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

TOOL_DIR = Path(__file__).parent
ROOT = TOOL_DIR.parent
load_dotenv(ROOT / ".env", override=True)
sys.path.insert(0, str(TOOL_DIR))
from qmetry_client import ensure_child_folder


def load_config(path: Path) -> dict:
    if not path.exists():
        path = TOOL_DIR / "qmetry-config.sample.json"
    with open(path, encoding="utf-8") as f:
        return json.load(f)


PRIORITY_ID_MAP = {
    "critical": 674921,
    "blocker": 674921,
    "high": 674922,
    "medium": 674923,
    "low": 674924,
}


def priority_name(raw: str, cfg: dict) -> str | None:
    if not raw:
        return None
    value = raw.strip()
    priority_map = cfg.get("priorityMap", {})
    for key, mapped in priority_map.items():
        if key.lower() == value.lower():
            return str(mapped)
    normalized = value.lower()
    if normalized in {"critical", "high", "medium", "low"}:
        return normalized.capitalize()
    print(f"WARNING: priority '{value}' is not mapped. Skipping priority.")
    return None


def priority_id(name: str | None) -> int | None:
    if not name:
        return None
    return PRIORITY_ID_MAP.get(name.strip().lower())


def row_value(row: dict, key: str | None) -> str:
    if not key:
        return ""
    return (row.get(key) or "").strip()


def build_payload(row: dict, cfg: dict, folder_id: int) -> tuple[dict, list[dict], str | None]:
    mapping = cfg["mapping"]
    summary = row_value(row, mapping.get("summary"))
    if not summary:
        raise ValueError("Missing Summary")

    labels_raw = row_value(row, mapping.get("labels"))
    labels = [item.strip() for item in labels_raw.replace(";", ",").split(",") if item.strip()]
    steps_raw = row_value(row, mapping.get("steps"))
    actions = [item.strip() for item in steps_raw.split("|") if item.strip()] or ["Execute test"]

    priority = priority_name(row_value(row, mapping.get("priority")), cfg)
    pri_id = priority_id(priority)
    sprint = row_value(row, mapping.get("sprint")) or (cfg.get("defaults", {}).get("sprint") or "")

    test_data = row_value(row, mapping.get("testData"))
    expected = row_value(row, mapping.get("expectedResult"))
    steps: list[dict] = []
    for index, action in enumerate(actions):
        step = {"stepDetails": action}
        if index == 0:
            step["testData"] = test_data
        if index == len(actions) - 1:
            step["expectedResult"] = expected
        steps.append(step)

    payload: dict = {
        "projectId": int(cfg["project"]["jiraProjectId"]),
        "summary": summary,
        "folderId": folder_id,
        "precondition": row_value(row, mapping.get("precondition")),
        "steps": steps,
    }
    if pri_id:
        payload["priority"] = pri_id

    updates: dict = {}
    if payload["precondition"]:
        updates["precondition"] = payload["precondition"]
    if pri_id:
        updates["priority"] = pri_id
    # Store TSV-only metadata in description so it is not lost when QMetry has no matching field.
    description_parts = [
        ("Test Level", row_value(row, "Test Level")),
        ("Test Type", row_value(row, "Test Type")),
        ("Smoke", row_value(row, "Smoke")),
        ("Auto", row_value(row, "Auto")),
        ("Trace", row_value(row, "Trace")),
        ("Teardown", row_value(row, "Teardown")),
    ]
    description = "\n".join(f"{name}: {value}" for name, value in description_parts if value)
    if description:
        payload["description"] = description
        updates["description"] = description
    if labels:
        # Open API requires label IDs. Keep Story Linkage as description text instead of sending invalid label/story body.
        payload["description"] = (payload.get("description", "") + f"\nStory Linkages: {', '.join(labels)}").strip()
        updates["description"] = payload["description"]
    if sprint.isdigit():
        payload["sprint"] = int(sprint)
        updates["sprint"] = int(sprint)
    return payload, steps, updates, priority


def resolve_path(path_text: str) -> Path:
    path = Path(path_text)
    if path.is_absolute():
        return path
    return ROOT / path


def main() -> int:
    parser = argparse.ArgumentParser(description="Push TSV test cases to a QMetry folderId.")
    parser.add_argument("--tsv", required=True, help="TSV file relative to repo root or absolute path")
    parser.add_argument("--folder-id", help="QMetry folderId copied from Test Case folder")
    parser.add_argument("--parent-folder-id", type=int, help="Parent folder id; used with --folder-name to find/create a child folder")
    parser.add_argument("--folder-name", help="Child folder name to find/create under --parent-folder-id")
    parser.add_argument("--config", default=str(TOOL_DIR / "qmetry-config.json"))
    parser.add_argument("--max-rows", type=int, default=0, help="Push only first N rows")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--continue-on-error", action="store_true")
    args = parser.parse_args()

    cfg = load_config(Path(args.config))
    token = os.getenv(cfg["auth"].get("tokenEnvVar", "QMETRY_API_TOKEN"), "")
    if not args.dry_run and not token:
        print("ERROR: QMETRY_API_TOKEN is not set in .env or environment.")
        return 1

    tsv_path = resolve_path(args.tsv)
    if not tsv_path.exists():
        print(f"ERROR: TSV file not found: {tsv_path}")
        return 1

    base = cfg["apiBaseUrl"].rstrip("/")
    endpoint = base + "/" + cfg["createTestCasePath"].lstrip("/")
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json; charset=utf-8",
        cfg["auth"].get("headerName", "apiKey"): token,
    }
    project_id = int(cfg["project"]["jiraProjectId"])

    target_folder_id: int
    if args.parent_folder_id and args.folder_name:
        if args.dry_run:
            target_folder_id = -1
            print(f"DRY_RUN_FOLDER: would find/create '{args.folder_name}' under parent {args.parent_folder_id}")
        else:
            target_folder_id = ensure_child_folder("testcase", args.parent_folder_id, args.folder_name)
            print(f"FOLDER:{args.folder_name}")
            print(f"FOLDER_ID:{target_folder_id}")
    elif args.folder_id:
        target_folder_id = int(args.folder_id)
    else:
        print("ERROR: pass either --folder-id or both --parent-folder-id and --folder-name")
        return 1

    with open(tsv_path, encoding="utf-8-sig", newline="") as f:
        filtered = (line for line in f if not line.startswith("#"))
        rows = list(csv.DictReader(filtered, delimiter="\t"))
    if args.max_rows > 0:
        rows = rows[: args.max_rows]

    report = []
    ok = failed = skipped = 0
    for row in rows:
        try:
            payload, steps, updates, priority = build_payload(row, cfg, target_folder_id)
            if args.dry_run:
                ok += 1
                report.append({
                    "summary": payload["summary"],
                    "result": "dry-run",
                    "priority": priority,
                    "priorityId": updates.get("priority"),
                    "folderId": payload.get("folderId"),
                    "stepCount": len(steps),
                })
                continue

            response = requests.post(endpoint, headers=headers, json=payload, timeout=30)
            if response.status_code not in (200, 201):
                raise RuntimeError(f"create testcase failed: {response.status_code} {response.text[:400]}")
            created = response.json()
            created_id = str(created.get("id") or "")
            created_key = str(created.get("key") or "")

            if created_id and updates:
                update_url = f"{base}/rest/api/latest/testcases/{created_id}/versions/1"
                update_response = requests.put(update_url, headers=headers, json=updates, timeout=30)
                if update_response.status_code not in (200, 201, 204):
                    raise RuntimeError(f"update testcase failed: {update_response.status_code} {update_response.text[:400]}")

            ok += 1
            report.append({
                "summary": payload["summary"],
                "result": "created",
                "id": created_id,
                "key": created_key,
                "priority": priority,
                "priorityId": updates.get("priority"),
                "folderId": payload.get("folderId"),
                "stepCount": len(steps),
            })
        except Exception as exc:
            summary = row.get(cfg["mapping"].get("summary", "Summary"), "")
            if summary:
                failed += 1
                report.append({"summary": summary, "result": "failed", "error": str(exc)})
            else:
                skipped += 1
                report.append({"summary": "", "result": "skipped", "error": str(exc)})
            if not args.continue_on_error:
                break

    report_dir = ROOT / "testing-output" / "qmetry"
    report_dir.mkdir(parents=True, exist_ok=True)
    report_file = report_dir / "qmetry-folder-push-report.json"
    with open(report_file, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    print(f"TOTAL:{len(rows)}")
    print(f"SUCCESS:{ok}")
    print(f"FAILED:{failed}")
    print(f"SKIPPED:{skipped}")
    print(f"REPORT:{report_file}")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
