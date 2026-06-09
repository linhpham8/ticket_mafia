# QA Skill Suite v2.1 — Quick Start

Bắt đầu trong 5 phút. Đọc [README.md](README.md) để biết đầy đủ.

---

## Bước 0 — Hiểu cách dùng

Bộ toolkit này chạy với **Claude** (hoặc AI tương thích). Bạn gõ yêu cầu bằng ngôn ngữ tự nhiên, Claude tự chọn skill đúng và sinh output vào `testing-output/`.

**Bạn không cần nhớ lệnh nào** — chỉ cần nói điều bạn muốn làm.

---

## Bước 1 — Setup (lần đầu)

```powershell
# 1. Cài dependencies
pip install -r tools/requirements-integration.txt

# 2. Tạo .env
copy .env.example .env
# Điền ATLASSIAN_EMAIL, ATLASSIAN_API_TOKEN, QMETRY_API_TOKEN vào .env

# 3. Setup QMetry config
copy tools\qmetry-config.sample.json tools\qmetry-config.json
# Điền apiBaseUrl và project.jiraProjectId vào qmetry-config.json

# 4. Mở Claude Code
claude
```

---

## Bước 2 — Bắt đầu ngay

| Tình huống | Gõ gì với Claude |
|---|---|
| Mới nhận requirements, cần review | "Review AC này cho tôi: [paste AC]" |
| Sprint mới, cần lập kế hoạch | "Tạo sprint test plan cho sprint 5" |
| Cần viết test case | "Viết test case cho IAC-01 — đây là AC: [...]" |
| Có kết quả test cuối ngày | "Daily report: pass 45, fail 3, blocked 2" |
| Sắp release, cần quyết định | "Go/no-go sprint 5, pass rate 94%" |
| Vừa deploy xong | "Smoke test production: https://app.prod.example.com" |

---

## Bước 3 — Luồng sprint chuẩn

```
03 (Sprint Plan) → 05 (TC Functional) → push lên QMetry
→ 09 (Daily check, lặp ngày) → 10 (Sprint Report)
→ 13 (Go/No-Go) → 14 (Smoke Production)
```

---

## Bước 4 — Push output lên QMetry / Confluence

```powershell
# Push TC lên QMetry
python tools/qmetry_push_testcase_to_folder.py --tsv <file.tsv> --folder-id <ID>

# Đánh kết quả hàng loạt
python tools/qmetry_bulk_status.py --cycle FDP-TR-5 --cycle-id <ID> --folder-id <ID> --status Pass

# Push test plan lên Confluence
python tools/confluence_md.py --file testing-output/test-plan/<file.md> --parent-id <ID>
```

---

## Khi bị stuck

| Vấn đề | Giải pháp |
|---|---|
| Không biết dùng skill nào | Nói "skill nào phù hợp khi tôi cần [...]?" |
| Output sai format | Nói "Đọc lại skill file và tạo lại theo format đó" |
| QMetry lỗi | Xem `tools/QMETRY_TOOLS.md` |
| Confluence lỗi | Xem `CONFLUENCE-SYNC-GUIDE.md` |
| Mọi vấn đề khác | Xem `README.md` phần Troubleshooting |
