#!/usr/bin/env python3
"""Convert a synced Confluence HTML page to Markdown.

Usage:
  python tools/html_to_md.py <slug>
  python tools/html_to_md.py docs/confluence/pages/<slug>.html
"""

from __future__ import annotations

import re
import sys
from html import unescape
from pathlib import Path

from bs4 import BeautifulSoup
from markdownify import markdownify as md

from credentials import get_env


ROOT = Path(__file__).resolve().parent.parent
CONFLUENCE_ROOT = ROOT / "docs" / "confluence"
PAGES_DIR = CONFLUENCE_ROOT / "pages"
SPACE_TREE = CONFLUENCE_ROOT / "space-tree.md"
ATLASSIAN_BASE_URL = get_env("ATLASSIAN_BASE_URL", "https://your-company.atlassian.net")
CONFLUENCE_SPACE_KEY = get_env("CONFLUENCE_SPACE_KEY", "YOURSPACE")
CONFLUENCE_BASE = f"{ATLASSIAN_BASE_URL.rstrip('/')}/wiki"


def build_page_url_map() -> dict[str, str]:
    if not SPACE_TREE.exists():
        return {}
    url_map: dict[str, str] = {}
    text = SPACE_TREE.read_text(encoding="utf-8")
    for match in re.finditer(r"\*\*(.+?)\*\*\s*\(ID:\s*`(\d+)`\)", text):
        title, page_id = match.groups()
        url_map[title] = f"{CONFLUENCE_BASE}/spaces/{CONFLUENCE_SPACE_KEY}/pages/{page_id}"
    return url_map


def convert_ac_links(soup: BeautifulSoup, page_url_map: dict[str, str]) -> None:
    for link_tag in list(soup.find_all("ac:link")):
        anchor = link_tag.get("ac:anchor")
        ri_page = link_tag.find("ri:page")
        link_body = link_tag.find("ac:link-body")
        if not link_body:
            link_tag.decompose()
            continue

        text = link_body.get_text(" ", strip=True)
        url = None
        if ri_page:
            raw_title = ri_page.get("ri:content-title", "")
            page_title = unescape(raw_title)
            if page_title in page_url_map:
                url = page_url_map[page_title]
                if anchor:
                    url = f"{url}#{anchor}"

        if url:
            new_tag = soup.new_tag("a", href=url)
            new_tag.string = text
            link_tag.replace_with(new_tag)
        else:
            link_tag.replace_with(text)


def expand_table_spans(soup: BeautifulSoup) -> None:
    for table in soup.find_all("table"):
        rows = table.find_all("tr")
        if not rows:
            continue
        grid: dict[tuple[int, int], tuple[str, str]] = {}
        for row_index, row in enumerate(rows):
            column_index = 0
            for cell in list(row.find_all(["td", "th"], recursive=False)):
                while (row_index, column_index) in grid:
                    column_index += 1
                rowspan = int(cell.get("rowspan", 1))
                colspan = int(cell.get("colspan", 1))
                for row_offset in range(rowspan):
                    for column_offset in range(colspan):
                        grid[(row_index + row_offset, column_index + column_offset)] = (str(cell), cell.name)
                column_index += colspan
        if not grid:
            continue
        max_column = max(column for _, column in grid.keys()) + 1
        for row_index, row in enumerate(rows):
            for cell in list(row.find_all(["td", "th"], recursive=False)):
                cell.decompose()
            for column_index in range(max_column):
                html_text, _ = grid.get((row_index, column_index), ("<td></td>", "td"))
                clone_soup = BeautifulSoup(html_text, "html.parser")
                clone = clone_soup.find(["td", "th"])
                if clone is None:
                    clone = BeautifulSoup("<td></td>", "html.parser").find("td")
                clone.attrs.pop("rowspan", None)
                clone.attrs.pop("colspan", None)
                clone.extract()
                row.append(clone)


def clean_html(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")
    convert_ac_links(soup, build_page_url_map())

    unwrap_tags = {"ac:inline-comment-marker", "ac:link-body", "ac:layout", "ac:layout-section", "ac:layout-cell"}
    for tag in list(soup.find_all(True)):
        if tag.name and ":" in tag.name:
            if tag.name in unwrap_tags:
                tag.unwrap()
            else:
                tag.decompose()
    for tag in soup.find_all(True):
        for attribute in list(tag.attrs):
            if attribute.startswith("ac:") or attribute.startswith("data-") or attribute == "local-id":
                del tag.attrs[attribute]

    expand_table_spans(soup)
    return str(soup)


def convert(html: str) -> str:
    cleaned = clean_html(html)
    result = md(cleaned, heading_style="ATX", bullets="-", strip=["script", "style"], newline_style="backslash")
    result = re.sub(r"\n{4,}", "\n\n\n", result)
    result = "\n".join(line.rstrip() for line in result.splitlines())
    return result.strip()


def resolve_paths(argument: str) -> tuple[Path, Path]:
    candidate = Path(argument)
    if candidate.suffix.lower() == ".html":
        html_path = candidate if candidate.is_absolute() else ROOT / candidate
        md_path = html_path.with_suffix(".md")
        return html_path, md_path
    html_path = PAGES_DIR / f"{argument}.html"
    md_path = PAGES_DIR / f"{argument}.md"
    return html_path, md_path


def main() -> int:
    if len(sys.argv) < 2:
        print("Usage: python tools/html_to_md.py <slug-or-html-path>")
        return 1

    html_path, md_path = resolve_paths(sys.argv[1])
    if not html_path.exists():
        print(f"Error: {html_path} not found")
        return 1

    html = html_path.read_text(encoding="utf-8")
    md_path.write_text(convert(html), encoding="utf-8")
    print(f"Written: {md_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
