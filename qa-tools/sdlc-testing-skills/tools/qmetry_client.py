#!/usr/bin/env python3
"""
Shared QMetry API client — config loader + core API helpers.
Imported by qmetry_update_status.py, qmetry_update_testcase.py, qmetry_bulk_status.py.
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import requests
from dotenv import load_dotenv

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

load_dotenv(Path(__file__).parent.parent / ".env", override=True)

# ── Config & auth ─────────────────────────────────────────────────────────────

_CONFIG_DIR = Path(__file__).parent
_CONFIG_PATH = _CONFIG_DIR / "qmetry-config.json"
if not _CONFIG_PATH.exists():
    _CONFIG_PATH = _CONFIG_DIR / "qmetry-config.sample.json"

with open(_CONFIG_PATH, encoding="utf-8") as _f:
    _cfg = json.load(_f)

BASE       = _cfg["apiBaseUrl"].rstrip("/")
PROJECT_ID = int(_cfg["project"]["jiraProjectId"])
TOKEN      = os.getenv("QMETRY_API_TOKEN", "")

if not TOKEN:
    print("ERROR: QMETRY_API_TOKEN not set in .env")
    sys.exit(1)

HEADERS = {
    "apiKey": TOKEN,
    "Content-Type": "application/json",
    "Accept": "application/json",
}

# ── Status map ────────────────────────────────────────────────────────────────

STATUS_MAP: dict[str, int] = {
    "blocked":      295106,
    "fail":         295107,
    "wip":          295108,
    "notexecuted":  295109,
    "not executed": 295109,
    "pass":         295110,
}


def get_status_id(status_name: str) -> int | None:
    key = status_name.strip().lower()
    if key in STATUS_MAP:
        return STATUS_MAP[key]
    try:
        return int(status_name)
    except ValueError:
        pass
    print(f"  ERROR: unknown status '{status_name}'. Valid: {list(STATUS_MAP.keys())}")
    return None


# ── Core API helpers ──────────────────────────────────────────────────────────

def create_test_cycle(name: str, project_id: int | None = None,
                      description: str | None = None,
                      summary: str | None = None,
                      start_date: str | None = None,
                      end_date: str | None = None,
                      folder_id: int | None = None,
                      test_cases_to_link: list[dict] | None = None) -> dict | None:
    payload: dict = {
        "summary": summary or name,
        "projectId": project_id or PROJECT_ID,
    }
    if description: payload["description"] = description
    if start_date:  payload["plannedStartDate"] = start_date
    if end_date:    payload["plannedEndDate"] = end_date
    if folder_id:   payload["folderId"] = int(folder_id)
    if test_cases_to_link:
        payload["testCasesToLink"] = {"testCases": test_cases_to_link}
    r = requests.post(f"{BASE}/rest/api/latest/testcycles",
                      headers=HEADERS, json=payload, timeout=30)
    if r.status_code in (200, 201):
        data = r.json()
        print(f"SUCCESS: Created cycle '{name}' (id={data.get('id')})")
        return data
    print(f"ERROR: Failed to create cycle '{name}': {r.status_code} {r.text[:200]}")
    return None


def ensure_tc_linked(cycle_id: str, tc_id: str, version_no: int = 1) -> bool:
    r = requests.post(
        f"{BASE}/rest/api/latest/testcycles/{cycle_id}/testcases",
        headers=HEADERS,
        json={"testCases": [{"id": tc_id, "versionNo": version_no}]},
        timeout=30,
    )
    if r.status_code in (200, 201, 204, 409):
        return True
    print(f"  WARNING: link returned {r.status_code}: {r.text[:150]}")
    return False


def get_map_id(cycle_id: str, tc_key: str) -> tuple[str | None, str | None]:
    """Return (testCycleTestCaseMapId, testCaseExecutionId) or (None, None)."""
    r = requests.post(
        f"{BASE}/rest/api/latest/testcycles/{cycle_id}/testcases/search",
        headers=HEADERS, json={"filter": {}}, timeout=30,
    )
    if r.status_code != 200:
        print(f"  ERROR getting mapId: {r.status_code} {r.text[:200]}")
        return None, None
    for item in r.json().get("data", []):
        if item.get("key") == tc_key:
            return item.get("testCycleTestCaseMapId"), item.get("testCaseExecutionId")
    return None, None


def find_linked_testcase(cycle_id: str, tc_key: str) -> dict | None:
    r = requests.post(
        f"{BASE}/rest/api/latest/testcycles/{cycle_id}/testcases/search",
        headers=HEADERS,
        json={"filter": {"key": tc_key}},
        timeout=30,
    )
    if r.status_code == 200:
        data = r.json().get("data", [])
        if data:
            return data[0]
    else:
        print(f"  WARNING searching linked testcase by key returned {r.status_code}: {r.text[:150]}")

    r = requests.post(
        f"{BASE}/rest/api/latest/testcycles/{cycle_id}/testcases/search",
        headers=HEADERS,
        json={"filter": {}},
        timeout=30,
    )
    if r.status_code != 200:
        print(f"  ERROR searching linked testcases: {r.status_code} {r.text[:200]}")
        return None
    for item in r.json().get("data", []):
        if item.get("key") == tc_key:
            return item
    return None


def get_latest_exec_id(cycle_id: str, map_id: str) -> tuple[str | None, str | None]:
    """Return (testCaseExecutionId, currentStatusName) or (None, None)."""
    r = requests.get(
        f"{BASE}/rest/api/latest/testcycles/{cycle_id}/testcases/{map_id}/executions",
        headers=HEADERS, timeout=30,
    )
    if r.status_code != 200:
        print(f"  ERROR getting executions: {r.status_code} {r.text[:200]}")
        return None, None
    execs = r.json().get("executions", {}).get("data", [])
    if not execs:
        return None, None
    latest = execs[0]
    return (latest.get("testCaseExecutionId"),
            latest.get("executionResult", {}).get("name", "?"))


def create_execution(cycle_id: str, map_id: str) -> bool:
    r = requests.post(
        f"{BASE}/rest/api/latest/testcycles/{cycle_id}/testcases/{map_id}/executions",
        headers=HEADERS, json={}, timeout=30,
    )
    return r.status_code in (200, 201, 204)


def update_execution_result(cycle_id: str, exec_id: str,
                             result_id: int, comment: str = "") -> tuple[bool, str | None]:
    body: dict = {"executionResultId": result_id}
    if comment:
        body["comment"] = comment
    r = requests.put(
        f"{BASE}/rest/api/latest/testcycles/{cycle_id}/testcase-executions/{exec_id}",
        headers=HEADERS, json=body, timeout=30,
    )
    return r.status_code == 204, r.text if r.text.strip() else None


def update_status(cycle_key: str, cycle_id: str, tc_key: str, tc_id: str,
                  status_name: str, comment: str = "",
                  version_no: int = 1, create_new: bool = False) -> bool:
    result_id = get_status_id(status_name)
    if result_id is None:
        return False

    print(f"\nUpdating {tc_key} in {cycle_key} → {status_name}")
    ensure_tc_linked(cycle_id, tc_id, version_no)

    map_id, _ = get_map_id(cycle_id, tc_key)
    if map_id is None:
        print("  ERROR: could not get testCycleTestCaseMapId")
        return False

    exec_id, current_status = get_latest_exec_id(cycle_id, map_id)
    if exec_id is None or create_new:
        print("  Creating new execution entry...")
        create_execution(cycle_id, map_id)
        exec_id, current_status = get_latest_exec_id(cycle_id, map_id)

    if exec_id is None:
        print("  ERROR: could not get testCaseExecutionId")
        return False

    print(f"  mapId={map_id}  execId={exec_id}  currentStatus={current_status}")
    ok, err = update_execution_result(cycle_id, exec_id, result_id, comment)
    if ok:
        print(f"  SUCCESS → '{status_name}'")
        return True
    print(f"  FAILED: {err}")
    return False


def get_object_id(value: dict) -> int | None:
    for key in ("id", "folderId"):
        if key in value and value[key] not in (None, ""):
            return int(value[key])
    return None


def flatten_folders(items: list[dict], parent_id: int | None = None) -> list[dict]:
    result: list[dict] = []
    for item in items:
        if parent_id is not None and "parentId" not in item:
            item["parentId"] = parent_id
        result.append(item)
        current_id = get_object_id(item)
        for child_key in ("children", "childFolders", "folders"):
            children = item.get(child_key)
            if isinstance(children, list):
                result.extend(flatten_folders(children, current_id))
    return result


def get_folders(folder_type: str, project_id: int | None = None) -> list[dict]:
    if folder_type not in {"testcase", "testcycle", "testplan"}:
        raise ValueError("folder_type must be testcase, testcycle, or testplan")
    project = project_id or PROJECT_ID
    r = requests.get(
        f"{BASE}/rest/api/latest/projects/{project}/{folder_type}-folders",
        headers=HEADERS,
        timeout=30,
    )
    r.raise_for_status()
    data = r.json()
    if isinstance(data, list):
        return flatten_folders(data)
    for key in ("data", "folders", "children"):
        if isinstance(data.get(key), list):
            return flatten_folders(data[key])
    return []


def find_child_folder(folder_type: str, parent_id: int, folder_name: str,
                      project_id: int | None = None) -> int | None:
    for folder in get_folders(folder_type, project_id):
        name = str(folder.get("name") or folder.get("folderName") or "")
        folder_parent = folder.get("parentId") or folder.get("parentFolderId")
        if name.lower() == folder_name.lower() and str(folder_parent) == str(parent_id):
            return get_object_id(folder)
    return None


def create_folder(folder_type: str, parent_id: int, folder_name: str,
                  description: str = "", project_id: int | None = None) -> int:
    if folder_type not in {"testcase", "testcycle", "testplan"}:
        raise ValueError("folder_type must be testcase, testcycle, or testplan")
    project = project_id or PROJECT_ID
    body: dict = {"folderName": folder_name, "parentId": parent_id}
    if description:
        body["description"] = description
    r = requests.post(
        f"{BASE}/rest/api/latest/projects/{project}/{folder_type}-folders",
        headers=HEADERS,
        json=body,
        timeout=30,
    )
    if r.status_code not in (200, 201):
        raise RuntimeError(f"create {folder_type} folder failed: {r.status_code} {r.text[:400]}")
    folder_id = get_object_id(r.json())
    if folder_id is None:
        raise RuntimeError(f"create {folder_type} folder response missing id: {r.text[:400]}")
    return folder_id


def ensure_child_folder(folder_type: str, parent_id: int, folder_name: str,
                        description: str = "", project_id: int | None = None) -> int:
    existing = find_child_folder(folder_type, parent_id, folder_name, project_id)
    if existing is not None:
        return existing
    return create_folder(folder_type, parent_id, folder_name, description, project_id)


def get_testcases_in_folder(folder_id: int, project_id: int | None = None,
                            max_results: int = 500) -> list[dict]:
    """Fetch test cases in a folder. Returns list of {key, id} dicts.
    Tries multiple QMetry Cloud API patterns with fallback."""
    project = project_id or PROJECT_ID

    def _extract(data) -> list[dict]:
        items = data if isinstance(data, list) else data.get("data", [])
        return [{"key": i.get("key"), "id": i.get("id")} for i in items if i.get("key")]

    attempts = [
        # 1. GET /testcases?folderId=X
        lambda: requests.get(
            f"{BASE}/rest/api/latest/testcases",
            headers=HEADERS,
            params={"folderId": folder_id, "projectId": project, "maxResults": max_results},
            timeout=30,
        ),
        # 2. GET /projects/{project}/testcases?folderId=X
        lambda: requests.get(
            f"{BASE}/rest/api/latest/projects/{project}/testcases",
            headers=HEADERS,
            params={"folderId": folder_id, "maxResults": max_results},
            timeout=30,
        ),
        # 3. POST /testcases/search  body flat
        lambda: requests.post(
            f"{BASE}/rest/api/latest/testcases/search",
            headers=HEADERS,
            json={"projectId": project, "folderId": folder_id, "maxResults": max_results},
            timeout=30,
        ),
        # 4. POST /testcases/search  body nested filter
        lambda: requests.post(
            f"{BASE}/rest/api/latest/testcases/search",
            headers=HEADERS,
            json={"projectId": project, "filter": {"folderId": folder_id}, "maxResults": max_results},
            timeout=30,
        ),
        # 5. POST /projects/{project}/testcases/search
        lambda: requests.post(
            f"{BASE}/rest/api/latest/projects/{project}/testcases/search",
            headers=HEADERS,
            json={"folderId": folder_id, "maxResults": max_results},
            timeout=30,
        ),
    ]

    for i, attempt in enumerate(attempts, 1):
        try:
            r = attempt()
            if r.status_code == 200:
                result = _extract(r.json())
                if result:
                    print(f"  [folder API attempt {i}] found {len(result)} TCs")
                    return result
            else:
                print(f"  [folder API attempt {i}] {r.status_code} — trying next...")
        except Exception as e:
            print(f"  [folder API attempt {i}] exception: {e}")

    print(f"ERROR: all folder-listing attempts failed for folder {folder_id}")
    return []


def create_cycle_link_and_update(
    cycle_name: str,
    folder_id: int,
    tc_key: str,
    tc_id: str,
    status_name: str = "Pass",
    version_no: int = 1,
    description: str = "",
    comment: str = "",
    project_id: int | None = None,
) -> dict:
    result_id = get_status_id(status_name)
    if result_id is None:
        raise ValueError(f"Unknown execution status: {status_name}")

    cycle = create_test_cycle(
        name=cycle_name,
        project_id=project_id or PROJECT_ID,
        description=description,
        folder_id=folder_id,
        test_cases_to_link=[{"id": tc_id, "versionNo": version_no}],
    )
    if not cycle:
        raise RuntimeError("Failed to create test cycle")
    cycle_id = str(cycle.get("id") or "")
    cycle_key = str(cycle.get("key") or "")
    if not cycle_id:
        raise RuntimeError(f"Create cycle response missing id: {cycle}")

    ensure_tc_linked(cycle_id, tc_id, version_no)
    linked = find_linked_testcase(cycle_id, tc_key)
    if not linked:
        raise RuntimeError(f"Test case {tc_key} was not found in cycle {cycle_id}")

    map_id = linked.get("testCycleTestCaseMapId")
    exec_id = linked.get("testCaseExecutionId") or linked.get("latestTcExecutionId")
    if not exec_id:
        create_execution(cycle_id, map_id)
        exec_id, _ = get_latest_exec_id(cycle_id, map_id)
    if not exec_id:
        raise RuntimeError(f"Could not resolve execution id for {tc_key} in {cycle_id}")

    ok, err = update_execution_result(cycle_id, str(exec_id), result_id, comment)
    if not ok:
        raise RuntimeError(err or "Failed to update execution result")
    return {
        "cycleId": cycle_id,
        "cycleKey": cycle_key,
        "folderId": folder_id,
        "tcKey": tc_key,
        "tcId": tc_id,
        "testCycleTestCaseMapId": map_id,
        "executionId": str(exec_id),
        "status": status_name,
    }
