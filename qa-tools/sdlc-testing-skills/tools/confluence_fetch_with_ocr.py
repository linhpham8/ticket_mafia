#!/usr/bin/env python3
"""Fetch a Confluence page directly and emit AI-friendly JSON.

Direct mode is optimized for skill execution on a single requirement URL.
The script saves text content and any referenced image attachments. If PIL and
pytesseract are installed, OCR text is added to each image attachment.
"""

from __future__ import annotations

import argparse
import base64
import html
import json
import re
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

try:
    from PIL import Image
except Exception:
    Image = None

try:
    import pytesseract
except Exception:
    pytesseract = None

from credentials import get_env


ROOT = Path(__file__).resolve().parent.parent
CACHE_DIR = ROOT / "docs" / "confluence-cache"
DATA_DIR = ROOT / "docs" / "confluence-data"
DEFAULT_OCR_LANG = "vie+eng"


def parse_page_url(url: str) -> tuple[str, str, str]:
    parsed = urllib.parse.urlparse(url)
    if parsed.scheme not in {"http", "https"}:
        raise RuntimeError("Invalid URL")
    site_root = f"{parsed.scheme}://{parsed.netloc}"
    match = re.search(r"/pages/(\d+)", parsed.path)
    if not match:
        raise RuntimeError("Cannot parse Confluence page ID")
    return site_root, f"{site_root}/wiki", match.group(1)


def build_headers() -> dict[str, str]:
    email = get_env("ATLASSIAN_EMAIL") or get_env("ATLASSIAN_USER_EMAIL") or get_env("ATLASSIAN_USER_EMAIL")
    token = get_env("ATLASSIAN_API_TOKEN")
    if not email or not token:
        raise RuntimeError("Missing Atlassian credentials")
    basic = base64.b64encode(f"{email}:{token}".encode()).decode()
    return {"Authorization": f"Basic {basic}", "Accept": "application/json"}


def get_json(url: str, headers: dict[str, str]) -> dict:
    request = urllib.request.Request(url, headers=headers, method="GET")
    with urllib.request.urlopen(request, timeout=60) as response:
        return json.loads(response.read().decode("utf-8"))


def get_bytes(url: str, headers: dict[str, str]) -> bytes:
    request = urllib.request.Request(url, headers=headers, method="GET")
    with urllib.request.urlopen(request, timeout=60) as response:
        return response.read()


def strip_html_to_text(body_html: str) -> str:
    text = re.sub(r"<br\s*/?>", "\n", body_html, flags=re.IGNORECASE)
    text = re.sub(r"</p>", "\n", text, flags=re.IGNORECASE)
    text = re.sub(r"<[^>]+>", " ", text)
    text = html.unescape(text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def extract_referenced_filenames(body_html: str) -> list[str]:
    seen: set[str] = set()
    names: list[str] = []
    for filename in re.findall(r'ri:filename="([^"]+)"', body_html):
        if filename not in seen:
            seen.add(filename)
            names.append(filename)
    return names


def list_attachments(site_root: str, wiki_base: str, page_id: str, headers: dict[str, str]) -> dict[str, dict[str, str]]:
    url = f"{wiki_base}/rest/api/content/{page_id}/child/attachment?limit=250&expand=version"
    data = get_json(url, headers)
    attachments: dict[str, dict[str, str]] = {}
    for item in data.get("results", []):
        title = item.get("title") or ""
        media_type = item.get("metadata", {}).get("mediaType", "")
        download_rel = (item.get("_links", {}) or {}).get("download") or ""
        if title and download_rel:
            rel_no_query = download_rel.split("?", 1)[0]
            attachments[title] = {
                "media_type": media_type,
                "download_url": urllib.parse.urljoin(site_root, rel_no_query),
            }
    return attachments


def find_tesseract() -> str | None:
    for path in (
        "C:/Program Files/Tesseract-OCR/tesseract.exe",
        "C:/Program Files (x86)/Tesseract-OCR/tesseract.exe",
    ):
        if Path(path).exists():
            return path
    return None


def run_ocr(image_path: Path, ocr_lang: str) -> str:
    if Image is None or pytesseract is None:
        return ""
    tesseract_path = find_tesseract()
    if tesseract_path:
        pytesseract.pytesseract.tesseract_cmd = tesseract_path
    try:
        with Image.open(image_path) as image:
            text = pytesseract.image_to_string(image.convert("L"), lang=ocr_lang, config="--oem 3 --psm 6")
            return re.sub(r"\s+", " ", text).strip()
    except Exception:
        return ""


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url", required=True, help="Confluence page URL")
    parser.add_argument("--json-out", default="", help="Optional JSON output path")
    parser.add_argument("--max-images", type=int, default=20, help="Max referenced images to fetch")
    parser.add_argument("--ocr-lang", default=DEFAULT_OCR_LANG, help="OCR language pack, default vie+eng")
    args = parser.parse_args()

    site_root, wiki_base, page_id = parse_page_url(args.url)
    headers = build_headers()

    page = get_json(f"{site_root}/wiki/api/v2/pages/{page_id}?body-format=storage", headers)
    body_html = page.get("body", {}).get("storage", {}).get("value", "")
    title = page.get("title", "")
    version = str(page.get("version", {}).get("number", ""))
    text_content = strip_html_to_text(body_html)

    referenced = extract_referenced_filenames(body_html)
    attachment_map = list_attachments(site_root, wiki_base, page_id, headers)
    image_dir = CACHE_DIR / f"page-{page_id}" / "images"
    image_dir.mkdir(parents=True, exist_ok=True)

    attachments: list[dict[str, str]] = []
    for filename in referenced[: args.max_images]:
        item = attachment_map.get(filename)
        if not item or not item.get("media_type", "").startswith("image/"):
            continue
        target_path = image_dir / filename
        try:
            target_path.write_bytes(get_bytes(item["download_url"], headers))
            ocr_text = run_ocr(target_path, args.ocr_lang)
            attachments.append({"file": filename, "path": target_path.as_posix(), "ocr": ocr_text})
        except urllib.error.HTTPError:
            continue

    payload = {
        "page": {
            "page_id": page_id,
            "page_url": args.url,
            "title": title,
            "version": version,
        },
        "text_content": text_content,
        "attachments": attachments,
    }

    out_path = Path(args.json_out) if args.json_out else DATA_DIR / f"confluence-{page_id}-direct.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"JSON_SAVED: {out_path}")
    print("CONFLUENCE_DIRECT_JSON_BEGIN")
    print(json.dumps(payload, ensure_ascii=False))
    print("CONFLUENCE_DIRECT_JSON_END")
    print(f"IMAGES_OCR: {len(attachments)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
