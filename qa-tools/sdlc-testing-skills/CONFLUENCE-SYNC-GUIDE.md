# Confluence Sync Guide

Hướng dẫn đồng bộ data giữa Confluence và local — cả hai chiều:
- **Sync-down** (Confluence → local `docs/`): để AI đọc requirement, PRD, spec
- **Push-up** (local `testing-output/` → Confluence): để publish test plan, report

---

## Cấu hình tiên quyết

File `.env` ở root thư mục phải có:

```dotenv
ATLASSIAN_EMAIL=your@email.com
ATLASSIAN_API_TOKEN=your_atlassian_api_token
ATLASSIAN_BASE_URL=https://your-domain.atlassian.net
CONFLUENCE_SPACE_KEY=YOUR_SPACE_KEY
```

Lấy API token tại: https://id.atlassian.com → Security → Create and manage API tokens

---

## Phần 1 — Sync-Down: Confluence → Local

Dữ liệu được lưu vào `docs/confluence/` để Claude đọc khi gen TC, test plan, v.v.

### Công cụ có sẵn

| Script | Chức năng | Output |
|---|---|---|
| `confluence_sync_space.py` | Sync toàn bộ space/subtree | `docs/confluence/pages/` |
| `confluence_fetch_with_ocr.py` | Fetch 1 page (URL hoặc ID) + OCR ảnh | `docs/confluence/pages/` |
| `confluence_fetch_tree.py` | Lấy parent/siblings/children của 1 page | JSON |
| `confluence_qa_fetch.py` | Tìm pages theo keyword tự nhiên | `docs/confluence/pages/` |
| `confluence_fetch_page.py` | Fetch 1 page cơ bản (không OCR) | `docs/confluence/pages/` |
| `html_to_md.py` | Convert HTML đã fetch sang Markdown | in-place |

---

### Kịch bản A — Sync toàn bộ space (lần đầu setup)

Tải tất cả pages từ space về local:

```powershell
python tools/confluence_sync_space.py --full --space-key YOUR_SPACE_KEY
```

Output:
```
docs/confluence/
├── space-tree.md          ← Cây hierarchy toàn space
└── pages/
    ├── Page-Title-1.html + .md
    ├── Page-Title-2.html + .md
    └── ...
```

> Lưu ý: `--full` chỉ fetch pages ở các cấp đầu. Pages nằm sâu (FR-01, AC-05, v.v.) → dùng Kịch bản B.

---

### Kịch bản B — Fetch 1 page cụ thể (bất kể nằm sâu bao nhiêu)

Khi cần lấy 1 requirement page cụ thể (FR-01, AC-05, User Story, v.v.):

```powershell
# Từ URL đầy đủ
python tools/confluence_fetch_with_ocr.py `
  --url "https://your-domain.atlassian.net/wiki/spaces/FDP/pages/3731718216/FR-01-Title" `
  --json-out docs/confluence/pages/FR-01.json

# Từ page ID (ngắn hơn)
python tools/confluence_fetch_with_ocr.py `
  --url "https://your-domain.atlassian.net/wiki/spaces/FDP/pages/3731718216" `
  --json-out docs/confluence/pages/FR-01.json
```

Output JSON chứa `text_content` đầy đủ — Claude đọc file này để gen TC.

Sau đó nói với Claude:
```
"Đọc docs/confluence/pages/FR-01.json và viết test case functional đầy đủ"
```

---

### Kịch bản C — Tìm pages theo keyword (không biết URL/ID)

Khi cần tìm tất cả pages liên quan đến một chủ đề:

```powershell
python tools/confluence_qa_fetch.py "agent registration deployment" --top 5
```

Output:
```
Matching pages (scored):
1. FR-01 — Register & Deploy Agent  (score: 0.92)
2. FR-49 — Agent Visual Builder     (score: 0.78)
3. ...
```

Sau đó dùng page ID để fetch đầy đủ nội dung (Kịch bản B).

---

### Kịch bản D — Lấy tất cả FR pages liên quan (siblings)

Khi cần FR-01, FR-02, FR-03 cùng lúc — không cần biết từng ID:

```powershell
# Bước 1: Lấy hierarchy của FR-01 → thấy danh sách siblings
python tools/confluence_fetch_tree.py `
  --page-id 3731718216 `
  --site-root "https://your-domain.atlassian.net" `
  --out docs/confluence/pages/FR-01-tree.json
```

Output JSON có mục `target_siblings_under_parent` chứa ID + title của FR-02, FR-03...

```powershell
# Bước 2: Fetch từng page
python tools/confluence_fetch_with_ocr.py `
  --url "https://your-domain.atlassian.net/wiki/spaces/FDP/pages/<FR-02-ID>" `
  --json-out docs/confluence/pages/FR-02.json
```

---

### Cấu trúc `docs/` sau sync

```
docs/
├── confluence/
│   ├── space-tree.md                  ← Cây hierarchy space
│   └── pages/
│       ├── FR-01.json                 ← Full content (text + OCR)
│       ├── FR-01.html                 ← Storage HTML gốc
│       ├── FR-01.md                   ← Markdown version
│       └── FR-01.json.sidebar.json    ← Metadata: page_id, version (dùng khi push lại)
│
└── jira/
    └── searches/
        ├── jira-search-*.json
        └── jira-search-*.md
```

> `.json.sidebar.json` hoặc `.json` bên cạnh `.md` lưu `page_id` — **không xóa** —
> dùng để push ngược lên đúng page mà không cần tìm lại ID.

---

## Phần 2 — Push-Up: Local → Confluence

Publish test plan, sprint report, v.v. lên Confluence sau khi Claude tạo xong.

### Push 1 file .md lên Confluence

```powershell
# Tạo page mới dưới parent page
python tools/confluence_md.py `
  --file testing-output/test-plan/Sprint_Test_Plan_FDP_Sprint5_v1.0_2026-05-20.md `
  --parent-id <PARENT_PAGE_ID>

# Update page đã có (dùng page ID trực tiếp)
python tools/confluence_md.py `
  --file testing-output/test-plan/Sprint_Test_Plan_FDP_Sprint5_v1.0_2026-05-20.md `
  --page-id <EXISTING_PAGE_ID>
```

> Nếu bên cạnh file `.md` đã có `.json` sidebar (từ lần fetch trước), script tự đọc
> `page_id` từ đó — không cần truyền `--page-id` nữa.

### Push toàn bộ folder lên Confluence

```powershell
# Push tất cả .md trong folder (không recursive)
python tools/confluence_push_folder.py `
  --folder testing-output/test-plan `
  --parent-id <PARENT_PAGE_ID>

# Preview trước khi push (dry-run)
python tools/confluence_push_folder.py `
  --folder testing-output `
  --parent-id <PARENT_PAGE_ID> `
  --recursive --dry-run
```

---

## Phần 3 — Luồng đầy đủ: Fetch requirement → Gen TC → Push kết quả

```
[Bước 1] Fetch requirement từ Confluence về local
  python tools/confluence_fetch_with_ocr.py --url "<URL>" --json-out docs/confluence/pages/IAC-01.json

[Bước 2] Nói với Claude gen test case
  "Đọc docs/confluence/pages/IAC-01.json và viết TC functional đầy đủ"
  → Output: testing-output/test-cases/functional/tc-functional-IAC-01-Sprint5-v1.0-2026-05-20.tsv

[Bước 3] Push TC lên QMetry
  python tools/qmetry_push_testcase_to_folder.py --tsv <file> --folder-id <FOLDER_ID>

[Bước 4] Nói với Claude gen sprint report
  "Sprint report sprint 5: pass 142, fail 8, blocked 3"
  → Output: testing-output/reports/sprint-report-Sprint5-2026-05-20-v1.0.md

[Bước 5] Push report lên Confluence
  python tools/confluence_md.py --file <file> --parent-id <PARENT_ID>
```

---

## Troubleshooting

| Lỗi | Nguyên nhân | Giải pháp |
|---|---|---|
| `Missing credentials` | `.env` chưa có token | Thêm `ATLASSIAN_API_TOKEN` vào `.env` |
| `401 Unauthorized` | Token sai hoặc hết hạn | Tạo token mới trên id.atlassian.com |
| `404 Not Found` | Page ID sai hoặc page bị xóa | Kiểm tra URL trên Confluence |
| `403 Forbidden` | Không có quyền truy cập space | Yêu cầu admin grant quyền |
| File output trống | Confluence page trống | Mở page trên browser kiểm tra |
| Pages sâu không fetch được bằng `sync_space` | `--full` chỉ lấy top-level | Dùng `fetch_with_ocr` với URL/ID cụ thể |
