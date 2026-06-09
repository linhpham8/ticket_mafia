#!/usr/bin/env python3
"""
Push 1 test case mẫu lên QMetry Cloud để kiểm tra kết nối và format payload.

Chạy: python tools/qmetry_push_sample.py
"""
import os, sys, json, requests
from pathlib import Path
from dotenv import load_dotenv

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

load_dotenv(Path(__file__).parent.parent / ".env", override=True)

CONFIG_DIR = Path(__file__).parent
CONFIG_PATH = CONFIG_DIR / "qmetry-config.json"
if not CONFIG_PATH.exists():
    CONFIG_PATH = CONFIG_DIR / "qmetry-config.sample.json"

import json
with open(CONFIG_PATH, encoding="utf-8") as f:
    _cfg = json.load(f)

QMETRY_BASE = _cfg["apiBaseUrl"].rstrip("/")
ENDPOINT = _cfg.get("createTestCasePath", "/rest/api/latest/testcases")
PROJECT_ID = _cfg["project"]["jiraProjectId"]

token = os.getenv("QMETRY_API_TOKEN", "")
if not token:
    print("ERROR: QMETRY_API_TOKEN chua duoc set trong .env")
    sys.exit(1)

headers = {
    "apiKey": token,
    "Content-Type": "application/json",
    "Accept": "application/json",
}

# Format dung: projectId (int) + testSteps (khong phai steps)
sample_payload = {
    "summary": "[AUTO-TEST] Sample TC - push thu nghiem",
    "description": "Test case duoc push tu script de kiem tra ket noi QMetry API",
    "precondition": "He thong dang chay, user da dang nhap",
    "projectId": PROJECT_ID,
    "testSteps": [
        {
            "stepDetail": "Truy cap man hinh chinh",
            "expectedResult": "Man hinh hien thi dung",
            "testData": ""
        },
        {
            "stepDetail": "Thuc hien hanh dong kiem tra",
            "expectedResult": "Ket qua dung voi yeu cau",
            "testData": "Du lieu test mau"
        }
    ]
}

url = QMETRY_BASE + ENDPOINT
print(f"POST {url}")
print("Payload:", json.dumps(sample_payload, ensure_ascii=False, indent=2))
print("-" * 60)

try:
    resp = requests.post(url, headers=headers, json=sample_payload, timeout=30)
    print(f"Status: {resp.status_code}")
    try:
        body = resp.json()
        print("Response:", json.dumps(body, ensure_ascii=False, indent=2))
    except Exception:
        print("Response:", resp.text[:800])

    if resp.status_code in (200, 201):
        tc_key = body.get("key") or body.get("testCaseKey") or body.get("id") or "?"
        print(f"\nSUCCESS: Test case da duoc tao, Key = {tc_key}")
    elif resp.status_code == 400:
        errors = body.get("errors", []) if isinstance(body, dict) else []
        print(f"\nFAIL 400: {'; '.join(errors) or body.get('errorMessage','')}")
    elif resp.status_code == 401:
        print("\nFAIL 401: API token sai hoac het han.")
except Exception as e:
    print("Connection error:", e)
