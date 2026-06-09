# QA Skill Suite v2.1.0

Bộ skill kiểm thử AI-Driven — từ review requirements → test plan → viết TC → test data → automation → báo cáo → release gate.

---

## Claude/AI làm gì trong bộ toolkit này?

Bộ toolkit này được thiết kế để chạy với **Claude Code CLI** (hoặc bất kỳ AI client tương thích nào).
Claude **không phải** chỉ là chatbot trả lời câu hỏi — Claude đọc các file skill, hiểu quy trình QA, rồi **tự sinh output theo đúng format chuẩn** (TSV test case, Markdown test plan, Robot Framework script, v.v.).

Luồng hoạt động:

```
Bạn gõ yêu cầu bằng tiếng Việt / tiếng Anh
        ↓
Claude đọc SKILL.md → chọn đúng sub-skill
        ↓
Claude đọc sub-skill + references cần thiết
        ↓
Claude sinh output → ghi file vào testing-output/
        ↓
Bạn review, chỉnh sửa nếu cần, rồi push lên Confluence / QMetry
```

**Lợi ích thực tế:**
- Viết 35 functional TC từ 1 User Story trong < 5 phút
- Gen sprint test plan đầy đủ 8 mục chỉ cần nói tên sprint
- Upload hàng chục TC lên QMetry và đánh status hàng loạt bằng 2 lệnh Python
- Đồng bộ Confluence → local để Claude đọc requirement mà không cần copy-paste

---

## Yêu cầu

| Thứ | Version | Ghi chú |
|---|---|---|
| Python | 3.9+ | Cần cho tools/ |
| AI Client | bất kỳ | Claude Code CLI (khuyến nghị), Claude.ai, Cursor, Copilot, Cline |
| QMetry | Cloud | Cần API token |
| Confluence / Jira | Cloud | Cần API token (nếu dùng tools sync) |

Cài dependencies:

```powershell
pip install -r tools/requirements-integration.txt
```

---

## Setup

### 1. Credentials

Tạo file `.env` ở root thư mục (không commit — đã có trong `.gitignore`):

```dotenv
# Atlassian (Confluence + Jira)
ATLASSIAN_EMAIL=your@email.com
ATLASSIAN_API_TOKEN=your_api_token
ATLASSIAN_BASE_URL=https://your-domain.atlassian.net
CONFLUENCE_SPACE_KEY=YOUR_SPACE
JIRA_PROJECT_KEY=YOUR_PROJECT

# QMetry
QMETRY_API_TOKEN=your_qmetry_api_token
```

Xem `.env.example` cho danh sách đầy đủ các biến.

### 2. QMetry config

```powershell
copy tools\qmetry-config.sample.json tools\qmetry-config.json
```

Mở `tools/qmetry-config.json` và điền:
- `apiBaseUrl` — URL QMetry Cloud của team (vd: `https://qtmcloud.qmetry.com`)
- `project.jiraProjectId` — numeric ID của Jira project liên kết QMetry

### 3. Mở với AI Client

**Claude Code CLI:**
```powershell
cd d:\path\to\qa-skill-v2.1.0
claude
```
Claude Code tự đọc `CLAUDE.md` → load context → sẵn sàng nhận lệnh.

**Claude.ai / Cursor / Copilot:** Thêm toàn bộ thư mục này vào context/workspace của tool đó.

---

## Cấu trúc thư mục

```
qa-skill-v2.1.0/
│
├── CLAUDE.md                    ← Claude Code đọc khi khởi động (instructions)
├── SKILL.md                     ← Router trung tâm — AI định tuyến đến đúng skill
├── AGENTS.md                    ← Instructions cho Codex CLI / Copilot Agent
├── .github/copilot-instructions.md  ← Instructions cho Copilot Chat
│
├── skills/                      ← Bộ não AI — 19 skills
│   ├── qa-core/01-14/           ← 14 skills luồng chính
│   ├── qa-automation/01-02/     ← Setup project + Gen automation script
│   └── qa-specialist/01-03/     ← Security / Performance / Accessibility
│
├── references/                  ← Tài liệu chuẩn AI đọc khi cần
│   ├── INDEX.md                 ← Chỉ mục để AI chọn đúng reference
│   ├── tc-template.tsv          ← Template TC functional 15 cột
│   ├── sit-template.tsv         ← Template TC SIT 19 cột
│   ├── test-plan-template.md
│   ├── report-template.md
│   └── skill-details/           ← Chi tiết từng skill (fallback/legacy)
│
├── tools/                       ← Integration scripts
│   ├── confluence_md.py         ← Push 1 file .md lên Confluence
│   ├── confluence_push_folder.py← Push cả folder lên Confluence
│   ├── confluence_fetch_page.py ← Fetch 1 page về local
│   ├── confluence_fetch_with_ocr.py ← Fetch page + extract ảnh (OCR)
│   ├── confluence_fetch_tree.py ← Lấy hierarchy (parent/siblings/children)
│   ├── confluence_qa_fetch.py   ← Search pages theo keyword tự nhiên
│   ├── confluence_sync_space.py ← Sync toàn bộ space về local
│   ├── html_to_md.py            ← Convert Confluence HTML → Markdown
│   ├── jira_sync.py             ← Sync Jira project / issue về local
│   ├── jira_create_subtask.py   ← Tạo subtask Jira
│   ├── jira_update_issue.py     ← Update Jira issue
│   ├── qmetry_push_testcase_to_folder.py ← Push TC TSV lên QMetry folder
│   ├── qmetry_bulk_status.py    ← Link TC vào cycle + đánh status hàng loạt
│   ├── qmetry_update_status.py  ← Update status 1 TC đơn lẻ
│   ├── md_to_docx.py            ← Chuyển .md → .docx
│   ├── qmetry-config.json       ← QMetry project config (tạo từ .sample.json)
│   └── QMETRY_TOOLS.md          ← Hướng dẫn chi tiết QMetry tools
│
├── assets/
│   └── automation-template/     ← Framework Robot Framework đầy đủ (template)
│
├── testing-output/              ← AI ghi output ra đây
│   ├── test-plan/               ← Master + Sprint Test Plans
│   ├── test-cases/functional/   ← TC functional (.tsv)
│   ├── test-cases/sit/          ← TC SIT (.tsv)
│   ├── test-cases/hltc/         ← High-level test design (.md)
│   ├── test-data/               ← Test data (.tsv)
│   ├── reports/                 ← Daily + Sprint reports
│   ├── automation/              ← Generated Robot Framework scripts
│   └── qmetry/                  ← Push reports, bulk-status files
│
├── project/
│   ├── qa-config.yaml           ← Config project (tạo bằng skill 02)
│   └── docs/                    ← Local mirror Confluence + Jira (read cache)
│       ├── confluence/pages/    ← Pages fetched/synced (.md + .json)
│       └── jira/                ← Jira issues + searches
│
├── governance/                  ← GOVERNANCE.md, sign-off-gates, audit-log
├── evaluation/                  ← Rubric đánh giá chất lượng output AI
└── workflows/                   ← End-to-end workflow guides
```

---

## Danh sách Skills

### qa-core — 14 skills (luồng chính)

| # | Skill | Gõ gì để trigger | Output |
|---|---|---|---|
| 01 | Review Requirements | "review AC cho tôi: [paste]", "review BR" | Danh sách issues TSV |
| 02 | Master Test Plan | "tạo master test plan", "QA strategy MVP" | .md + `qa-config.yaml` |
| 03 | Sprint Test Plan | "sprint test plan sprint 5", "test plan sprint mới" | .md 8 mục |
| 04 | High-Level Test Design | "HLTC module login", "mindmap test design" | .md outline + mindmap |
| 05 | TC Functional | "viết test case IAC-01", "gen TC từ AC này: [...]" | .tsv 15 cột |
| 06 | TC SIT | "SIT cho service auth", "integration test API" | .tsv 19 cột |
| 07 | Review TC | "review testcase của tôi", "coverage analysis" | Markdown report |
| 08 | Gen Test Data | "tạo test data cho login", "gen dataset Sprint 5" | .tsv + .sql |
| 09 | Check Result | "daily report: pass 45, fail 3", "bug triage" | .md + .html |
| 10 | Test Report | "sprint report sprint 5", "báo cáo kiểm thử" | .md + .html |
| 11 | Demo Preparation | "chuẩn bị demo sprint 5" | Markdown script |
| 12 | UAT Support | "UAT checklist", "hỗ trợ nghiệm thu" | Markdown |
| 13 | Go/No-Go | "go/no-go sprint 5, pass rate 92%" | Markdown decision |
| 14 | Smoke Production | "smoke test production URL: [...]" | Markdown checklist |

### qa-automation — 2 skills

| # | Skill | Gõ gì | Output |
|---|---|---|---|
| A1 | Setup Automation | "khởi tạo automation project", "setup RF project" | Scaffold project .robot |
| A2 | Gen Script Test | "viết automation script cho TC-001", "gen RF script" | .robot files |

### qa-specialist — 3 skills

| # | Skill | Gõ gì | Output |
|---|---|---|---|
| S1 | Security Testing | "security testing module auth", "OWASP checklist" | Markdown |
| S2 | Performance Testing | "load test API login", "performance baseline" | Markdown + k6/JMeter script |
| S3 | Accessibility Testing | "a11y testing màn đăng nhập", "WCAG checklist" | Markdown |

---

## Kịch bản điển hình

### Kịch bản 1 — Bắt đầu project mới

```
1. Tạo Master Test Plan + config:
   → "Tạo master test plan cho dự án FDP Sprint 1-3, domain: FinTech, team: 3 QC"

2. Verify file được tạo:
   testing-output/test-plan/Test_Plan_FDP_MVP1_v1.0_2026-05-20.md
   project/qa-config.yaml

3. Sprint đầu tiên → sang Kịch bản 2
```

### Kịch bản 2 — Sprint mới (luồng chuẩn hàng sprint)

```
1. Sprint test plan:
   → "Tạo sprint test plan sprint 5"

2. High-level test design (nếu module phức tạp):
   → "HLTC cho module IAM & SSO — User Story IAC-01, IAC-02, IAC-03"

3. Viết test case:
   → "Viết test case functional cho IAC-01 (đây là AC): [paste AC]"
   → Output: testing-output/test-cases/functional/tc-functional-IAC-01-Sprint5-v1.0-2026-05-20.tsv

4. Review TC:
   → "Review testcase vừa tạo, file: testing-output/test-cases/functional/tc-functional-IAC-01-Sprint5-v1.0-2026-05-20.tsv"

5. Push lên QMetry:
   python tools/qmetry_push_testcase_to_folder.py \
     --tsv testing-output/test-cases/functional/tc-functional-IAC-01-Sprint5-v1.0-2026-05-20.tsv \
     --folder-id <YOUR_FOLDER_ID>

6. Đánh kết quả sau khi test:
   python tools/qmetry_bulk_status.py \
     --cycle FDP-TR-5 --cycle-id <CYCLE_INTERNAL_ID> \
     --folder-id <YOUR_FOLDER_ID> --status Pass
```

### Kịch bản 3 — Lấy requirement từ Confluence rồi gen TC

```
1. Fetch page Confluence về local:
   python tools/confluence_fetch_with_ocr.py \
     --url "https://your-domain.atlassian.net/wiki/spaces/FDP/pages/3731718216" \
     --json-out project/docs/confluence/pages/IAC-01.json

2. Nói với Claude:
   → "Đọc project/docs/confluence/pages/IAC-01.json rồi viết test case functional đầy đủ"

3. Claude đọc file đã fetch → gen TC → ghi vào testing-output/test-cases/functional/
```

### Kịch bản 4 — Push output lên Confluence

```
1. Sau khi Claude tạo sprint test plan:
   python tools/confluence_md.py \
     --file testing-output/test-plan/Sprint_Test_Plan_FDP_Sprint5_v1.0_2026-05-20.md \
     --parent-id <CONFLUENCE_PARENT_PAGE_ID>

2. Lần update sau (Claude đã lưu page_id vào .json sidebar):
   python tools/confluence_md.py \
     --file testing-output/test-plan/Sprint_Test_Plan_FDP_Sprint5_v1.0_2026-05-20.md
   (tự động upsert vào đúng page)
```

### Kịch bản 5 — Cuối sprint: report + go/no-go

```
1. Sprint report:
   → "Sprint report sprint 5: pass 142, fail 8, blocked 3, coverage 92%"

2. Go/No-Go decision:
   → "Go/no-go sprint 5 — pass rate 94.7%, 2 critical bug còn open, deadline mai"

3. Smoke test production sau deploy:
   → "Smoke test production URL: https://app.prod.example.com, tài khoản: admin/P@ssw0rd"
```

### Kịch bản 6 — QMetry nâng cao (mix status)

```
# Tạo cycle mới + link TC + đánh Pass (1 lệnh)
python tools/qmetry_update_status.py \
  --create-cycle-link-update "Sprint 5 Regression" \
  --cycle-folder-id <FOLDER_ID> \
  --tc FDP-TC-2644 --tc-id LNNtKZJtm142P \
  --status Pass

# Nhiều TC với status khác nhau → tạo file TSV rồi bulk update
# File TSV: header = tc_key  tc_id  status  comment
python tools/qmetry_bulk_status.py \
  --cycle FDP-TR-5 --cycle-id <CYCLE_ID> \
  --file testing-output/qmetry/mixed-results.tsv
```

---

## Tools Integration — Confluence

Xem chi tiết: [CONFLUENCE-SYNC-GUIDE.md](CONFLUENCE-SYNC-GUIDE.md)

| Việc cần làm | Script |
|---|---|
| Fetch 1 page về local | `confluence_fetch_page.py` hoặc `confluence_fetch_with_ocr.py` |
| Tìm page theo keyword | `confluence_qa_fetch.py` |
| Lấy parent/siblings/children của page | `confluence_fetch_tree.py` |
| Sync toàn bộ space về local | `confluence_sync_space.py` |
| Push 1 file .md lên Confluence | `confluence_md.py` |
| Push cả folder .md lên Confluence | `confluence_push_folder.py` |

---

## Tools Integration — QMetry

Xem chi tiết: [tools/QMETRY_TOOLS.md](tools/QMETRY_TOOLS.md)

**Luồng chuẩn:**

```powershell
# Bước 1: Push TC từ TSV lên folder
python tools/qmetry_push_testcase_to_folder.py `
  --tsv testing-output/test-cases/functional/tc-functional-Sprint5-v1.0.tsv `
  --folder-id <FOLDER_ID>

# Bước 2: Link TC vào cycle + đánh status hàng loạt
python tools/qmetry_bulk_status.py `
  --cycle FDP-TR-5 `
  --cycle-id <CYCLE_INTERNAL_ID> `
  --folder-id <FOLDER_ID> `
  --status Fail
```

---

## Tools Integration — Jira

```powershell
# Sync toàn bộ project về local
python tools/jira_sync.py --project FDP

# Sync 1 issue cụ thể
python tools/jira_sync.py --issue FDP-1059

# Tạo subtask
python tools/jira_create_subtask.py --parent FDP-1059 --summary "Viết TC cho feature X"

# Update status
python tools/jira_update_issue.py --issue FDP-1059 --status "In Progress"
```

---

## Tools Integration — Xuất .docx

```powershell
# 1 file
python tools/md_to_docx.py --file testing-output/test-plan/Sprint_Test_Plan_FDP_Sprint5_v1.0.md

# Toàn bộ folder
python tools/md_to_docx.py --folder testing-output/test-plan --out testing-output/docx

# Recursive tất cả subfolder
python tools/md_to_docx.py --folder testing-output --out testing-output/docx --recursive
```

---

## Quy ước đặt tên file output

Mọi artifact phải có: `version (vX.Y)` + `ngày (yyyy-mm-dd)`.

| Artifact | Pattern | Thư mục |
|---|---|---|
| Master Test Plan | `Test_Plan_{code}_{milestone}_v{ver}_{date}.md` | `testing-output/test-plan/` |
| Sprint Test Plan | `Sprint_Test_Plan_{code}_{sprint}_v{ver}_{date}.md` | `testing-output/test-plan/` |
| HLTC | `hltc-{module}-{sprint}-v{ver}-{date}.md` | `testing-output/test-cases/hltc/` |
| Functional TC | `tc-functional-{module}-{sprint}-v{ver}-{date}.tsv` | `testing-output/test-cases/functional/` |
| SIT TC | `tc-sit-{module}-{sprint}-v{ver}-{date}.tsv` | `testing-output/test-cases/sit/` |
| Test Data | `master-dataset-{sprint}-v{ver}-{date}.tsv` | `testing-output/test-data/` |
| Daily Report | `daily-report-{date}-R{N}-v{ver}.md` | `testing-output/reports/` |
| Sprint Report | `sprint-report-{sprint}-{date}-v{ver}.md` | `testing-output/reports/` |

Chi tiết: `references/project-folder-convention.md`

---

## Governance & Approval

| Level | Skills | Yêu cầu |
|---|---|---|
| L1 — Auto | 01–06, 08 | AI tự hoàn thành, không cần approval |
| L2 — QA Lead review | 07, 09–11, qa-automation/02, qa-specialist/* | QA Lead phải review trước khi dùng |
| L3 — Stakeholder | 12–14 | PM/Stakeholder phải approve |

Chi tiết: `governance/sign-off-gates.md`

---

## Chuyển giao sang sprint mới

1. Sửa `project/qa-config.yaml`: đổi `project.sprint` thành sprint mới
2. Dùng skill 03 thay vì 02 (ngắn hơn, tái dùng config)
3. `testing-output/` cũ giữ nguyên — file mới có timestamp khác, không bị ghi đè

---

## Troubleshooting

| Vấn đề | Giải pháp |
|---|---|
| Claude không biết dùng skill nào | Nói rõ hơn: "Dùng skill 05 gen TC functional cho module X" |
| Output thiếu section | "Output thiếu [section], bổ sung theo đúng format" |
| AI tạo sai format | "Đọc lại file skill 05 và tạo lại theo format đó" |
| QMetry: `QMETRY_API_TOKEN not set` | Kiểm tra `.env` ở root, chắc chắn đã có token |
| QMetry: push 0 rows | TSV có comment `#` ở đầu, hoặc thiếu cột `Test Level` → xem `tools/QMETRY_TOOLS.md` |
| Confluence: 401 Unauthorized | Kiểm tra `ATLASSIAN_API_TOKEN` trong `.env` |
| Confluence: 404 Not Found | Page ID sai, hoặc URL không đúng |
| `ModuleNotFoundError` | Chạy `pip install -r tools/requirements-integration.txt` |
