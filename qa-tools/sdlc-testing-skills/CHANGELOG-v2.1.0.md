# CHANGELOG — QA Skill Suite v2.1.0

**Ngày phát hành:** 2026-05-19  
**Version trước:** v2.0.0  
**Loại:** Minor — backward-compatible enhancements

---

## Tóm tắt thay đổi

| # | File thay đổi | Loại | Mô tả ngắn |
|---|---|---|---|
| 1 | `skills/qa-core/05-gen-tc-functional/gen-tc-functional.md` | Enhancement | Thêm Bước 7: Self-review bắt buộc trước khi xuất TSV |
| 2 | `skills/qa-core/07-review-tc/review-tc.md` | Rewrite | Inline toàn bộ quy tắc, thêm kiểm tra Priority/Auto/ET |
| 3 | `skills/qa-core/08-gen-data-test/gen-data-test.md` | Enhancement | Thêm Format B (flat all-in-one TSV, 1 dòng/TC) |
| 4 | `references/rf-keyword-convention.md` | Fix | Làm rõ VerificationKeywords được dùng Get Text + Should Contain |
| 5 | `skills/qa-automation/02-gen-script-test/gen-script-test.md` | Fix | Sửa typo `Playwirght` → `Playwright` |
| 6 | `QUICKSTART.md` | Fix | Sửa bảng governance: Skill 07 là L2 (không phải L1) |
| 7 | `references/rf-ui-rule.md` | New | Quy tắc chi tiết UI keyword: 4-layer, locator, wait, ví dụ QuanLyNhanVien |
| 8 | `references/rf-api-rule.md` | New | Quy tắc chi tiết API keyword: LowLevel/Payload Builder/Flow/Verification từ Swagger |

---

## Chi tiết từng thay đổi

---

### 1. Skill 05 — Gen TC Functional: Bước 7 Self-review bắt buộc

**Lý do cập nhật:**  
Trước đây skill 05 chỉ có review coverage (R1/R2/R3) nhưng không có bước quét chất lượng từng TC trước khi xuất. Kết quả là file TSV vẫn có thể chứa lỗi format (Priority P1/P2/P3, Expected result mơ hồ, thiếu ET rows) dù đã qua R3.

**Thay đổi:**  
Thêm **Bước 7 — Self-review chất lượng bắt buộc** ngay trước Bước 8 (lưu file). AI phải quét toàn bộ file TSV theo 8 tiêu chí:

| Tiêu chí | Hành động khi fail |
|---|---|
| Priority dùng `High`/`Medium`/`Low` (không P1/P2/P3) | Đổi format |
| Priority = `High` → Smoke = `Y` | Sửa hoặc hạ Priority |
| Auto ≥80% toàn file; Auto=N có lý do trong Trace | Đặt lại Y hoặc ghi lý do |
| Expected result không mơ hồ | Viết lại cụ thể |
| Trace map về Rule ID tồn tại | Bổ sung hoặc sửa |
| Test Data không dùng placeholder | Điền giá trị thật |
| Teardown không để `-` nếu TC tạo/sửa/xóa data | Bổ sung teardown |
| Có ≥2 ET rows cuối file, STT số nguyên tiếp nối | Thêm nếu thiếu |

**Output bắt buộc của Bước 7:**  
AI phải ghi rõ: "Sửa N TC: [vấn đề]" hoặc "Self-review: OK — không có vi phạm".

**Cách dùng:**  
Không cần làm gì khác — Bước 7 tự động chạy trước khi AI lưu file TSV. Nếu muốn yêu cầu AI re-review file có sẵn, nói:
> "Self-review lại file TC này theo Bước 7 của skill 05"

---

### 2. Skill 07 — Review TC: Rewrite toàn bộ + thêm 4 kiểm tra mới

**Lý do cập nhật:**  
Phiên bản cũ dùng format compact (22 dòng, dẫn sang detail file). Thiếu 4 kiểm tra chất lượng quan trọng: Priority format, Smoke consistency, Auto ≥80%, ET rows.

**Thay đổi:**
- Inline toàn bộ quy tắc vào 1 file — không cần đọc detail file
- Thêm 4 tiêu chí chất lượng trong Bước 4 (Quality Check):

| Tiêu chí mới | Cờ khi fail |
|---|---|
| Priority dùng `High`/`Medium`/`Low` — không P1/P2/P3 | `TC-XXX: Priority sai format` |
| Priority=High → Smoke=Y | `TC-XXX: Priority=High nhưng Smoke=N` |
| Auto ≥80% toàn file; Auto=N có lý do trong Trace | `TC-XXX: Auto=N không có lý do` |
| ET rows ≥2 ở cuối file, STT số nguyên tiếp nối | `File thiếu ET rows hoặc STT ET sai format` |

- Thêm 4 mục tương ứng vào Review Gate checklist (12 mục tổng)

**Review Gate verdict:**
- `Approved` khi pass 100% (12/12 mục)
- `Not Approved` + liệt kê mục fail khi có bất kỳ mục nào fail

**Cách dùng:**  
Không thay đổi trigger: "Review testcase" / "coverage analysis" vẫn route đúng skill 07. Output bổ sung 4 cột mới trong bảng Quality Check.

---

### 3. Skill 08 — Gen Test Data: Thêm Format B (flat all-in-one)

**Lý do cập nhật:**  
Format cũ (6 cột: TC_ID | Dataset_ID | Test_Data | Loại | Teardown | Ghi chú) phù hợp cho BVA/EP với nhiều biến thể. Nhưng với happy path TC (1 bộ data duy nhất), đặc biệt khi dùng API automation, format này làm data phân tán khó review.

**Thay đổi:**  
Thêm **Format B — flat all-in-one**:
- 1 dòng / TC, mỗi field là 1 cột riêng
- JSON payload, container image, API payload inline trong cell tương ứng
- Không cần Dataset_ID (không có biến thể)

**Khi nào dùng Format B:**
- TC là happy path, không cần BVA/EP variations
- Team dùng TSV là nguồn duy nhất để review + chạy (không dùng YAML riêng)
- Payload phức tạp (JSON flow, container spec) cần inline để không phải quản lý nhiều file

**Ví dụ Format B:**
```
TC_ID	TC_Summary	Role	Account_Email	Entity_ID	Agent_Name	Agent_Type	Flow_JSON	Expected_HTTP	Expected_Status	Teardown
TC-001	Publish low-code agent	developer	dev@test.keystone.ai	ent-001	fr01-agent	low-code	{"flow_name":"..."}	-	Deployed	DELETE agent via API
```

**Format A vẫn là mặc định** — Format B chỉ dùng khi có lý do cụ thể.

---

### 4. rf-keyword-convention.md — Làm rõ VerificationKeywords

**Vấn đề cũ:**  
Câu "Chỉ dùng `Browser.Wait For Elements State` để verify element hiện/ẩn/enabled" bị hiểu nhầm là VerificationKeywords chỉ được dùng Wait For Elements State, trong khi thực tế còn cần Get Text + Should Contain để verify nội dung.

**Thay đổi:**  
Làm rõ quy tắc VerificationKeywords layer:
- `Browser.Wait For Elements State` — dùng để check visibility/enabled state
- `Browser.Get Text` + `Should Contain` / `Should Be Equal As Strings` — dùng để verify nội dung text
- Không dùng IF/FOR trong Verification layer
- Không gọi action (Click, Fill) trong Verification layer

---

### 7. rf-ui-rule.md — Quy tắc chi tiết UI keyword (mới)

**Lý do thêm:**  
`rf-keyword-convention.md` chỉ cung cấp overview 3-layer. Khi AI sinh UI keyword, vẫn thiếu quy tắc cụ thể về: cách viết VerificationKeywords với Get Text, locator priority trong Strict Mode, ví dụ đầy đủ từng layer, và pattern tạo module mới.

**Nội dung:**  
File `references/rf-ui-rule.md` bao gồm:
- **4-layer architecture** — LowLevel / HighLevel / VerificationKeywords / General
- **Quy tắc từng layer** — naming convention, header bắt buộc, forbidden patterns
- **Locator priority table** — data-autoid > id > chain (`>>`) > XPath > CSS > text
- **Strict Mode notes** — nth=, chain selector để cô lập element
- **Wait strategy** — thay thế Sleep bằng `Browser.Wait For Elements State`
- **Ví dụ đầy đủ** — module QuanLyNhanVien (filter, tạo mới, verify danh sách, verify chi tiết)
- **Checklist trước khi xuất** — 8 tiêu chí AI phải check trước khi nộp keyword

**Khi nào AI đọc:**  
Khi gen UI automation script với `robotframework-browser` (Playwright). INDEX.md đã được cập nhật để route đúng.

---

### 8. rf-api-rule.md — Quy tắc chi tiết API keyword (mới)

**Lý do thêm:**  
Trước đây không có tài liệu quy tắc cụ thể cho API testing với RESTinstance. AI thường tự sáng tạo cấu trúc không nhất quán — đặc biệt với: authorization header, Payload Builder pattern, cách tổ chức Flow vs Payload Builder trong cùng 1 file.

**Nội dung:**  
File `references/rf-api-rule.md` bao gồm:
- **4-layer architecture** — LowLevel (Api_Module.resource) / HighLevel (Payload Builder + Flow) / Verification / General-API
- **LowLevel rules** — naming `Api {METHOD} {path}`, hardcode authorization header, không dùng `${headers}` argument
- **Payload Builder rules** — dùng `Create Dictionary` + `RETURN`, không `Library Collections`, field optional qua IF + `Set To Dictionary`
- **Flow keyword rules** — gọi Payload Builder trước, không assign response
- **Verification rules** — `REST.Output` + JSONPath, group assertions theo context
- **Gen từ Swagger** — 1 file .robot per controller/tag, chỉ import General-API
- **Ví dụ đầy đủ** — module QuanLyNhanVien API (search, create, update, verify)
- **Checklist trước khi xuất** — 8 tiêu chí AI phải check

**Khi nào AI đọc:**  
Khi gen API automation script với RESTinstance từ Swagger. INDEX.md đã được cập nhật để route đúng.

---

### 5–6. Bugfixes nhỏ

**Typo:** `Playwirght` → `Playwright` trong description của gen-script-test.md

**QUICKSTART.md Section 7:**  
Đổi từ "Skills 01-08 không cần approval" thành:
- L1 (không cần): Skills 01-06, 08
- L2 (QA Lead): Skill 07, 09-11, qa-automation/02, qa-specialist
- L3 (Stakeholder/PM): Skills 12-14

---

## Hướng dẫn upgrade từ v2.0 → v2.1

1. **Không có breaking change** — tất cả skill trigger keywords giữ nguyên
2. **File TC hiện có**: không cần sửa — các quy tắc mới chỉ apply khi gen TC mới hoặc review TC
3. **Test data hiện có**: Format A vẫn hợp lệ — Format B là tùy chọn thêm
4. **rf-keyword-convention**: Script RF hiện có không bị ảnh hưởng — quy tắc chỉ làm rõ, không thay đổi behavior
5. **rf-ui-rule.md / rf-api-rule.md**: Hai file mới, thêm vào `references/`. AI tự đọc khi sinh UI/API script. Không cần action thủ công.

---

## Compatibility

| Component | v2.0 | v2.1 |
|---|---|---|
| Skills qa-core 01-04, 06, 09-14 | ✅ | ✅ (không đổi) |
| Skill 05 gen-tc-functional | ✅ | ✅+ Bước 7 |
| Skill 07 review-tc | ✅ | ✅+ 4 tiêu chí mới |
| Skill 08 gen-data-test | ✅ | ✅+ Format B |
| qa-automation 01-02 | ✅ | ✅ (fix typo only) |
| qa-specialist 01-03 | ✅ | ✅ (không đổi) |
| RF keyword convention | ✅ | ✅ (clarification only) |
| rf-ui-rule.md (UI keyword rules) | — | ✅ New |
| rf-api-rule.md (API keyword rules) | — | ✅ New |
| testing-output/ data format | ✅ | ✅ (backward compat) |

---

## Hướng dẫn kết nối Tool Integration

Bộ skill tích hợp sẵn với 3 hệ thống ngoài: **Confluence**, **Jira**, **QMetry**. Mọi lệnh chạy từ thư mục root của skill suite. Cần cài credentials trước — xem phần Setup bên dưới.

### Setup credentials (bắt buộc trước khi dùng bất kỳ tool nào)

Tạo file `.env` ở thư mục root (không commit — đã có trong `.gitignore`):

```bash
ATLASSIAN_EMAIL=your@email.com
ATLASSIAN_API_TOKEN=your_atlassian_api_token
ATLASSIAN_BASE_URL=https://your-domain.atlassian.net/
CONFLUENCE_SPACE_KEY=FDP
JIRA_PROJECT_KEY=FDP
```

Lấy API token tại: `https://id.atlassian.com/manage-profile/security/api-tokens`

Cài Python dependencies:
```bash
pip install requests markdown beautifulsoup4 python-docx python-dotenv markdownify
```

---

### Confluence Integration

**Script chính:** `tools/confluence_md.py`

#### Push file Markdown lên Confluence

```bash
# Push 1 file .md (tự động tạo mới hoặc cập nhật page)
python tools/confluence_md.py \
  --file testing-output/test-plan/Sprint_Test_Plan_S1.md \
  --parent-id <PARENT_PAGE_ID>

# Push vào page ID cụ thể (không cần tìm lại — dùng khi đã biết page_id)
python tools/confluence_md.py \
  --file testing-output/test-plan/Sprint_Test_Plan_S1.md \
  --page-id <PAGE_ID>
```

#### Push toàn bộ folder lên Confluence

```bash
# Push tất cả file trong folder (không recursive)
python tools/confluence_push_folder.py \
  --folder testing-output/test-plan \
  --parent-id <PARENT_PAGE_ID>

# Dry run — kiểm tra trước khi push thật
python tools/confluence_push_folder.py \
  --folder testing-output \
  --parent-id <PARENT_PAGE_ID> \
  --recursive --dry-run

# Push thật recursive
python tools/confluence_push_folder.py \
  --folder testing-output \
  --parent-id <PARENT_PAGE_ID> \
  --recursive
```

#### Fetch page từ Confluence về local

```bash
# Fetch 1 page → lưu .md + .json sidebar (sidebar chứa page_id để push lại)
python tools/confluence_fetch_page.py \
  --url "https://your-domain.atlassian.net/wiki/spaces/FDP/pages/<PAGE_ID>/..." \
  --out docs/confluence/pages

# Sync toàn bộ space/subtree về local
python tools/confluence_sync_space.py \
  --space-key FDP \
  --parent-id <PARENT_PAGE_ID>

# Fetch page có ảnh (dùng OCR để extract text từ ảnh)
python tools/confluence_fetch_with_ocr.py \
  --url "https://your-domain.atlassian.net/wiki/spaces/FDP/pages/<PAGE_ID>/..."
```

**Lưu ý quan trọng:**
- File `.json` sinh ra cạnh `.md` (sidebar) chứa `page_id` — **không xóa** — cần để push ngược lên sau này
- Script tự thử API v2 trước, fallback sang v1 nếu gặp 404
- Chỉ push sau khi có governance approval (skill 07+ cần L2, skill 12–14 cần L3)

**Artifact thường push lên Confluence:**

| Artifact | Trigger skill | Lệnh điển hình |
|---|---|---|
| Master Test Plan | Skill 02 | `--file testing-output/test-plan/Test_Plan_*.md --parent-id <id>` |
| Sprint Test Plan | Skill 03 | `--file testing-output/test-plan/Sprint_Test_Plan_*.md --parent-id <id>` |
| Sprint Report | Skill 10 | `--file testing-output/reports/sprint/sprint-report-*.md --parent-id <id>` |
| HLTC | Skill 04 | `--file testing-output/test-cases/hltc/hltc-*.md --parent-id <id>` |
| Daily Report | Skill 09 | `--file testing-output/reports/daily/daily-report-*.md --parent-id <id>` |

---

### Jira Integration

**Script chính:** `tools/jira_sync.py`, `tools/jira_create_subtask.py`, `tools/jira_update_issue.py`

#### Sync Jira về local

```bash
# Kéo toàn bộ issues của project về local cache (docs/jira/)
python tools/jira_sync.py --project FDP
```

Dùng khi: cần AI đọc ticket context mà không cần paste nội dung thủ công.  
Output: `docs/jira/issues/<ISSUE_KEY>.md` + `.json`

#### Tạo subtask

```bash
# Tạo subtask dưới 1 issue cha
python tools/jira_create_subtask.py \
  --parent FDP-1059 \
  --summary "Viết TC cho FR-01 Register Agent"
```

Dùng khi: breakdown công việc QA thành subtask trong sprint.

#### Cập nhật issue

```bash
# Đổi status
python tools/jira_update_issue.py --issue FDP-1059 --status "In Progress"

# Cập nhật nhiều field cùng lúc (xem --help để biết các flag)
python tools/jira_update_issue.py --issue FDP-1059 --status "Done" --assignee "qa-member"
```

**Luồng Jira điển hình trong sprint:**
```
Đầu sprint: jira_sync.py → AI đọc tickets → Skill 03 (Sprint Plan)
Trong sprint: jira_update_issue.py → đổi status TC/bug
Cuối sprint: Skill 10 (Sprint Report) → push lên Confluence
```

---

### QMetry Integration

**Script chính:** `tools/qmetry_import.ps1` (Windows), `tools/qmetry_bulk_status.py`, `tools/qmetry_update_status.py`

#### Setup QMetry config

```bash
# Copy sample config và điền thông tin project
cp tools/qmetry-config.sample.json tools/qmetry-config.json
```

Nội dung cần điền trong `tools/qmetry-config.json`:
```json
{
  "base_url": "https://your-domain.atlassian.net",
  "api_token": "your_qmetry_api_token",
  "project_key": "FDP",
  "test_cycle_name": "Sprint 1"
}
```

#### Import test case TSV lên QMetry

```powershell
# Windows PowerShell — import file TSV (15-cột chuẩn) lên QMetry
powershell -ExecutionPolicy Bypass -File tools/qmetry_import.ps1 `
  -TsvFile testing-output/test-cases/functional/tc-fr01-register-deploy-agent-s1.tsv `
  -ConfigFile tools/qmetry-config.json
```

Dùng ngay sau khi hoàn thành skill 05 hoặc 07 (sau khi TC đã Approved).

#### Cập nhật status hàng loạt

```bash
# Update nhiều TC trong 1 cycle cùng lúc (từ file kết quả test)
python tools/qmetry_bulk_status.py \
  --cycle "Sprint 1" \
  --file testing-output/reports/daily/results-2026-05-19.tsv

# Update theo danh sách TC cụ thể (key:id pairs)
python tools/qmetry_bulk_status.py \
  --cycle "Sprint 1" \
  --tcs "KST-TC-001:123,KST-TC-002:124" \
  --status Pass
```

#### Cập nhật status 1 TC

```bash
python tools/qmetry_update_status.py \
  --cycle "Sprint 1" \
  --tc-key KST-TC-001 \
  --tc-id 123 \
  --status Pass
```

**Status hợp lệ:** `Pass` / `Fail` / `Blocked` / `Not Run`

**Luồng QMetry điển hình trong sprint:**

```
Skill 05/06 → xuất TSV → qmetry_import.ps1 (import TC lên QMetry)
           ↓
Execution thủ công/tự động
           ↓
Skill 09 (daily check) → qmetry_bulk_status.py (update Pass/Fail)
           ↓
Skill 10 (sprint report) → tổng hợp từ QMetry + push Confluence
```

---

### Tiện ích bổ sung — Chuyển Markdown sang DOCX

```bash
# Chuyển 1 file .md → .docx (dùng khi cần gửi report dạng Word)
python tools/md_to_docx.py \
  --file testing-output/test-plan/Sprint_Test_Plan_S1.md

# Chuyển toàn bộ folder
python tools/md_to_docx.py \
  --folder testing-output/test-plan \
  --out testing-output/docx

# Recursive toàn bộ testing-output
python tools/md_to_docx.py \
  --folder testing-output \
  --out testing-output/docx \
  --recursive
```

Output: file `.docx` cùng tên, lưu vào `--out` folder.

---

### Tổng quan governance khi dùng tool integration

| Hành động | Governance | Điều kiện |
|---|---|---|
| Push Test Plan lên Confluence | L1 tự động | Sau khi skill 02/03 DONE |
| Push Sprint Report lên Confluence | L2 — QA Lead review | Sau khi nhận sign-off từ skill 10 |
| Push UAT / Go-No-Go lên Confluence | L3 — PM/Stakeholder | Sau khi nhận sign-off từ skill 12/13 |
| Import TC lên QMetry | L1 tự động | Sau khi TC Approved (skill 07) |
| Update status QMetry | L1 tự động | Sau mỗi ngày test (skill 09) |
| Tạo subtask Jira | L1 tự động | Khi breakdown công việc |
| Update status Jira | L1 tự động | Khi đổi trạng thái issue |

> **Quy tắc chung:** Không push lên Confluence hoặc cập nhật Jira/QMetry khi output chưa có sign-off ở mức tương ứng. AI sẽ emit sign-off request và chờ — không tự publish.

---

## Automation Framework — assets/automation-template/

Thư mục `assets/automation-template/` là **bộ khung Robot Framework đầy đủ** — AI có thể dùng trực tiếp khi gen script (skill `qa-automation/02`). Không cần build lại từ đầu; chỉ scaffold module mới trên nền này.

### Cấu trúc tổng thể

```
assets/automation-template/
├── KeywordLibraries/
│   ├── CommonKeyword/          ← Shared keywords dùng cho mọi project
│   ├── KeyCloak/               ← Auth token từ KeyCloak
│   └── {Module}/               ← Domain keywords (LowLevel/HighLevel/Verification + General)
├── Libs/                       ← Python custom libraries (30+ lib sẵn)
├── Projects/                   ← Ví dụ test suite cho từng module
├── Variables/                  ← ENV config (DEV/QC/UAT/PRD/MOBILE)
├── ExternalSystem/             ← Kết nối hệ thống ngoài (Dremio)
├── DataTest/                   ← File dữ liệu kiểm thử (Excel, YAML)
├── .vscode/                    ← VS Code config, snippets, templates
├── .gitlab-ci.yml              ← CI/CD pipeline mẫu
└── requirements.txt            ← Toàn bộ RF dependencies
```

---

### CommonKeyword — dùng trực tiếp trong mọi project

Mọi keyword layer đều import từ đây. AI sinh script luôn reference các file này — không tạo lại.

#### BrowserCore.resource
Keyword nền cho UI test (Playwright). Import: `Resource ../../CommonKeyword/BrowserCore.resource`

| Keyword | Mô tả | Dùng khi |
|---|---|---|
| `OPEN BROWSER AND DELETE COOKIES` | Mở browser mới + xóa cookies. Args: `${url}` `${testBrowser}` `${ALIAS}` | Suite Setup — test UI cần browser sạch |
| `Open Browser Reusing Existing Browser` | Kết nối vào Chrome đang chạy qua CDP port 6969 | Debug thủ công — không mở thêm browser |

> Trước khi dùng `Open Browser Reusing Existing Browser`, chạy Chrome với flag:  
> `chrome.exe --remote-debugging-port=6969 --user-data-dir="C:\temp\gdata"`

#### ApiCore.resource
Keyword HTTP thuần, wraps `RESTinstance` library. Import: `Resource ../../CommonKeyword/ApiCore.resource`  
Mỗi keyword tự set `${RESPONSE}` thành test variable sau khi call.

| Keyword | Signature | Trả về |
|---|---|---|
| `METHOD GET` | `${URL}` `${SET_HEADERS}` `${SET_QUERY}` | `${RESPONSE}` = response body |
| `METHOD POST` | `${URL}` `${SET_HEADERS}` `${SET_BODY}` | `${RESPONSE}` = response body |
| `METHOD PUT` | `${URL}` `${SET_HEADERS}` `${SET_BODY}` | `${RESPONSE}` = response body |
| `METHOD DELETE` | `${URL}` `${SET_HEADERS}` `${SET_BODY}` | `${RESPONSE}` = response body |
| `METHOD PATCH` | `${URL}` `${SET_HEADERS}` `${SET_BODY}` | `${RESPONSE}` = response body |

> **Lưu ý:** `${SET_HEADERS}` và `${SET_BODY}` nhận Dictionary. `${RESPONSE}` đã được log — không cần log lại.

#### Utils.resource
Helper keywords tái sử dụng. Import: `Resource ../../CommonKeyword/Utils.resource`

| Keyword | Mô tả |
|---|---|
| `Get Random String` | Sinh chuỗi chữ hoa ngẫu nhiên. Arg: `${length}=8` |
| `Get Random Number` | Sinh chuỗi số ngẫu nhiên. Arg: `${length}=8` |
| `Get random item in List` | Lấy ngẫu nhiên 1 item từ list |
| `Get DateTime` | Ngày giờ hiện tại theo format. Arg: `${date_format}=%Y-%m-%d %H:%M:%S` |
| `Get DateTime and Add day` | Ngày giờ + N ngày. Args: `${day}` `${date_format}` |
| `Get DateTime and Subtract day` | Ngày giờ − N ngày. Args: `${day}` `${date_format}` |
| `Get Day/Month/Year after increase days` | Lấy riêng ngày/tháng/năm sau khi cộng N ngày |
| `Get list key or value from dictionary YAML` | Extract keys hoặc values từ YAML dict |

#### NSP_UI_Utils.resource (shared UI utilities)
Keyword chờ đặc thù cho Angular/Material UI. Import: `Resource ../../{Module}/LowLevelKeywords/NSP_UI_Utils.resource`

| Keyword | Mô tả |
|---|---|
| `Wait for loading table on NSP Page` | Đợi spinner `div.c-loading` xuất hiện rồi biến mất (timeout 120s) |
| `Wait for networkidle on NSP Page` | `Browser.Wait For Load State networkidle` — dùng sau khi nhập search |
| `Focus mouse out` | Click ra ngoài để đóng dropdown/combobox |
| `Press Key Enter` | Focus vào input đầu tiên trong table filter và nhấn Enter |
| `Check Message Toast on NSP Page` | Verify nội dung toast message bằng `Browser.Get Text` |
| `Get total row in table on NPS Page` | Đếm số dòng trong `tbody tr.c-row` |
| `Get str text paginator on NSP Page` | Lấy text từ paginator (hiển thị "1-10 of 100") |
| `Wait For Api Search Changes on NSP Page` | Chờ response từ pattern `/api/v1/.*/search/` (timeout 180s) |

---

### KeyCloak Auth
`KeywordLibraries/KeyCloak/Api_KeyCloak_Token.resource`

| Keyword | Mô tả | Return |
|---|---|---|
| `Api get token from Sales Platform` | Lấy Bearer token qua KeyCloak OpenID Connect. Args: `${username}` `${password}` | `${nsp_token}` |

Intern dùng `Libs/extend_keycloak.py → Get Token From Keycloak`.  
URL realm tự build từ biến `${ENV}`: `keycloak-admin.ops.../realms/real-{page}-{env}/...`

---

### Variables — ENV config

Mỗi environment có 1 file YAML riêng. AI đọc đúng file theo `${ENV}` variable.

| File | Environment | Chứa |
|---|---|---|
| `ENV_DEV.yaml` | Development | URL, API endpoints dev |
| `ENV_QC.yaml` | QC/Test | URL, API endpoints QC |
| `ENV_UAT.yaml` | UAT | URL, API endpoints UAT |
| `ENV_PRD.yaml` | Production | URL, API endpoints PRD |
| `ENV_Auth0.yaml` | Auth0 SSO | Auth0 domain, client_id |
| `ENV_AuthOM.yaml` | OneMount SSO | OAuth endpoints OM |
| `ENV_MOBILE.yaml` | Mobile | Appium URL, device settings |
| `CONFIG_MOBILE.yaml` | Mobile caps | platformName, appPackage, deviceName |

`CommonVariable.resource` load đúng file theo pattern:
```robot
Variables    ../../Variables/ENV_${ENV}.yaml
```

Các biến toàn cục quan trọng:
```yaml
${ENV}              QC          # override khi chạy: --variable ENV:UAT
${RUN_BROWSER}      chrome      # hoặc msedge, firefox
${RUNNING_ON_JENKIN} N          # Y khi chạy trên Jenkins
${UPDATE_TEST_CASE}  N          # Y để auto-update QMetry sau mỗi TC
${timeout}          30s
${RESPONSE}         ${EMPTY}    # luôn được ghi đè bởi ApiCore
```

Chạy trên environment khác:
```bash
robot --variable ENV:UAT --variable RUN_BROWSER:msedge tests/
```

---

### Python Libraries (Libs/) — 30+ thư viện sẵn

AI có thể reference trực tiếp trong script mà không cần tự viết lại.

#### Nhóm Authentication & Security

| File | Class/Function | Keyword RF | Mô tả |
|---|---|---|---|
| `extend_keycloak.py` | `ExtendKeycloak` | `Get Token From Keycloak` | Lấy access_token từ KeyCloak (OpenID Connect password grant) |
| `extend_pgp_decrypt.py` | — | — | Giải mã PGP encrypted data |

#### Nhóm Database

| File | Class/Keyword RF | DB | Mô tả |
|---|---|---|---|
| `extend_nsp_postgresql.py` | `Postgres Query Mag Sales Platform` | PostgreSQL | Query DB + `Check No Empty Values` |
| `extend_pss_oracle.py` | — | Oracle | Query Oracle PSS environment |
| `extend_nextid_oracle.py` | — | Oracle | Query NextID Oracle |
| `extend_pss_tidb.py` | — | TiDB | Query TiDB PSS |
| `extend_ods.py` | — | ODS | Query ODS data warehouse |
| `database_output.py` | — | Generic | Format và log query results |
| `dremio_api.py` | — | Dremio | REST query đến Dremio data lake |

Ví dụ dùng PostgreSQL trong RF:
```robot
Library    ../../Libs/extend_nsp_postgresql.py

${result}    Postgres Query Mag Sales Platform
...    SELECT * FROM agent_hub.agents WHERE name = 'fr01-agent'
Check No Empty Values    ${result}    columns=id,name,status
```

#### Nhóm Messaging & Notification

| File | Class | Dùng cho |
|---|---|---|
| `ConnectKafka.py` | `send_message(topics, mes, key)` | Publish message lên Kafka (SSL) |
| `kafConsumer.py` | — | Consume Kafka message |
| `Kafka_Lib.py` | — | RF-friendly Kafka wrapper |
| `Slack.py` | `connect()` | Gửi message/file lên Slack channel qua `SLACK_BOT_TOKEN` |
| `SlackEx.py` | — | Extended Slack operations |
| `extend_google_chat.py` | `extend_google_chat` | Gửi notification lên Google Chat space |

Ví dụ gửi Slack report:
```robot
Library    ../../Libs/Slack.py
${client}    connect    # đọc SLACK_BOT_TOKEN từ env
```

#### Nhóm Google Integration

| File | Chức năng |
|---|---|
| `GoogleSheet.py` | Đọc/ghi Google Sheets (OAuth2 credentials) |
| `extend_google_chat.py` | Gửi notification Google Chat |

Setup: đặt file credentials tại path trong biến env `GOOGLESHEET_CREDENTIALS`.

#### Nhóm Reporting & CI

| File | Class/Function | Mô tả |
|---|---|---|
| `extend_reports.py` | `robot_report_database` | Push kết quả test lên internal report DB + Slack |
| `extend_qmetry.py` | `RobotReportQmetry` | `qmetry_Update_Status_Testcase` — Update Pass/Fail lên QMetry Cloud |
| `QmetryAPIUpdateTC.py` | — | Alternative QMetry update |
| `listener.py` | — | RF listener hook — capture events |
| `RobotSTF.py` | — | RF Suite/Test filter utilities |

Ví dụ auto-update QMetry ngay trong teardown:
```robot
Library    ../../Libs/extend_qmetry.py

[Teardown]    qmetry Update Status Testcase
...    ${TESTCYCLES}    KST-TC-001    ${TEST_STATUS}    WEB
```

#### Nhóm Mobile

| File | Chức năng |
|---|---|
| `ScrollAppMoblie.py` | Scroll Android native app theo tỉ lệ màn hình |
| `ScrollIOSMoblie.py` | Scroll iOS native app |

Dùng khi test type là mobile (Appium). Import qua `Utils.resource` hoặc trực tiếp.

#### Nhóm Image & Visual

| File | Chức năng |
|---|---|
| `ImageLibrary.py` | So sánh ảnh, capture screenshot, OCR |

#### Nhóm Performance

| File | Chức năng |
|---|---|
| `gen_data_jmeter.py` | Generate test data cho JMeter script |

#### Nhóm Legacy/Specialist

| File | Chức năng |
|---|---|
| `SeleniumLibEx.py` / `SeleniumLibraryEx.py` | Extended SeleniumLibrary (dự án cũ) |
| `SapGuiLibraryEx.py` | SAP GUI automation |
| `MemberPortal.py` | Member portal specific helpers |
| `MyLibrary.py` | Project utilities chung |
| `extend_pss_temporal_client.py` | Temporal workflow client |
| `extend_cdp.py` | Chrome DevTools Protocol extensions |

---

### VS Code Setup — .vscode/

Cấu hình sẵn cho VS Code khi làm việc với Robot Framework:

| File | Nội dung |
|---|---|
| `extensions.json` | Khuyến nghị cài: RobotFramework LSP, YAML, Python |
| `settings.json` | Robot path, Python interpreter, auto-format |
| `launch.json` | Debug config — chạy test file hiện tại từ VS Code |
| `robot.code-snippets` | Snippets: `*** Settings ***`, `*** Keywords ***`, keyword template |
| `templates/resource.resource` | Template resource file có đúng header Documentation + Author |
| `templates/test_suite.robot` | Template test suite có Suite Setup/Teardown + import chuẩn |

Dùng templates khi tạo module mới — copy từ template thay vì viết lại header.

---

### CI/CD — .gitlab-ci.yml

Pipeline mẫu GitLab CI gồm:
- Install Python + RF dependencies từ `requirements.txt`
- Chạy robot với `--variable ENV:QC`
- Xuất artifact: `log.html`, `report.html`, `output.xml`
- Parallel execution với `pabot` (config trong `Variables/pabot_oms_arg.txt`)

Adapt file này cho project mới bằng cách đổi `--variable ENV:` và path test suite.

---

### Cách AI dùng automation-template khi gen script

Khi skill `qa-automation/02` (gen-script-test) được trigger, AI:

1. **Không đọc toàn bộ asset vào context** — chỉ reference path
2. **Tái dùng CommonKeyword** — import `BrowserCore`, `ApiCore`, `Utils` thay vì tự viết keywords tương đương
3. **Chọn Lib phù hợp** theo loại integration cần:
   - DB verify → `extend_nsp_postgresql.py` (PostgreSQL) hoặc lib tương ứng
   - Auth → `extend_keycloak.py` → keyword `Get Token From Keycloak`
   - Notify → `extend_qmetry.py` → auto-update QMetry trong Teardown
   - Mobile → `ScrollAppMoblie.py` / `ScrollIOSMoblie.py`
4. **Đọc ENV_*.yaml** tương ứng — không hardcode URL
5. **Copy từ template** `templates/resource.resource` và `templates/test_suite.robot` cho file mới
6. **Scaffold theo 3-layer**: LowLevel → HighLevel → Verification → update General hub

Quy tắc tham chiếu trong script sinh ra:
```robot
Library    ../../Libs/extend_keycloak.py      # Auth
Library    ../../Libs/extend_nsp_postgresql.py # DB verify
Resource   ../../CommonKeyword/BrowserCore.resource
Resource   ../../CommonKeyword/ApiCore.resource
Resource   ../../CommonKeyword/Utils.resource
Variables  ../../Variables/ENV_${ENV}.yaml
```
