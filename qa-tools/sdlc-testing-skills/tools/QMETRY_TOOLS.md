# QMetry Tools — Hướng Dẫn Sử Dụng

## Cấu hình chung

| File | Mục đích |
|---|---|
| `tools/qmetry-config.json` | API base URL, project ID, column mapping, priority map |
| `.env` | `QMETRY_API_TOKEN=<token>` (bắt buộc) |

---

## 1. Push test cases lên folder

**Script:** `tools/qmetry_push_testcase_to_folder.py`

Đọc file TSV và tạo test cases trong QMetry, đặt vào folder chỉ định.

### Dùng folder ID biết sẵn

```powershell
python tools/qmetry_push_testcase_to_folder.py `
  --tsv testing-output/test-cases/functional/tc-IAC-01.tsv `
  --folder-id 2489720
```

### Tìm hoặc tạo folder con, rồi push

```powershell
python tools/qmetry_push_testcase_to_folder.py `
  --tsv testing-output/test-cases/functional/tc-IAC-01.tsv `
  --parent-folder-id 2475804 `
  --folder-name test-qmetry
```

Script sẽ tự tạo folder `test-qmetry` nếu chưa có, trả về `FOLDER_ID` sau khi tạo.

### Các flag tùy chọn

| Flag | Mô tả |
|---|---|
| `--max-rows N` | Chỉ push N rows đầu (debug) |
| `--dry-run` | Preview payload, không gọi API |
| `--continue-on-error` | Tiếp tục dù có row lỗi |

### Lưu ý format TSV

- File TSV phải có **header ở dòng 1** (không có comment `#` đầu file)
- Mỗi data row phải có đúng **15 tab-separated values**
- Cột `Test Level` không được để trống (`e2e` / `integration` / `component`)
- Cột `Priority` dùng `High` / `Medium` / `Low`

### Output

Report JSON lưu tại `testing-output/qmetry/qmetry-folder-push-report.json`  
Chứa: `key`, `id`, `priority`, `folderId`, `stepCount` của mỗi TC đã tạo.

---

## 2. Add TC vào cycle + đánh kết quả (bulk)

**Script:** `tools/qmetry_bulk_status.py`

Link test cases vào một test cycle và cập nhật execution status.  
Hỗ trợ 3 cách chỉ định danh sách TC:

### Cách A — Theo folder ID (thường dùng nhất)

Tự động lấy TC từ `qmetry-folder-push-report.json` theo `folderId`.

```powershell
python tools/qmetry_bulk_status.py `
  --cycle FDP-TR-1 `
  --cycle-id NMMUa7miAok4R `
  --folder-id 2489720 `
  --status Fail
```

### Cách B — Theo file TSV

TSV cần có header: `tc_key  tc_id  status  comment`

```powershell
python tools/qmetry_bulk_status.py `
  --cycle FDP-TR-1 `
  --cycle-id NMMUa7miAok4R `
  --file testing-output/qmetry/my-updates.tsv
```

Mỗi row có thể có status riêng. Nếu thiếu cột `status` thì dùng `--status` làm default.

### Cách C — Danh sách KEY:ID trực tiếp

```powershell
python tools/qmetry_bulk_status.py `
  --cycle FDP-TR-1 `
  --cycle-id NMMUa7miAok4R `
  --tcs "FDP-TC-2644:LNNtKZJtm142P,FDP-TC-2645:PVVhnx7u78JYG" `
  --status Pass
```

### Các flag tùy chọn

| Flag | Mặc định | Mô tả |
|---|---|---|
| `--status` | `Pass` | Status áp dụng: `Pass` / `Fail` / `Blocked` / `WIP` / `Not Executed` |
| `--comment` | `""` | Comment gắn kèm execution |
| `--delay` | `0.3` | Giây chờ giữa các request (tránh rate-limit) |
| `--dry-run` | — | Preview, không thực sự update |

### Lấy cycle-id

Cycle-id là internal ID của QMetry (không phải key như `FDP-TR-1`).  
Cách lấy: dùng `qmetry_update_status.py --list-statuses` hoặc xem URL trong QMetry UI.  
Cycle `FDP-TR-1` → `cycle-id = NMMUa7miAok4R`

---

## 3. Update status TC đơn lẻ

**Script:** `tools/qmetry_update_status.py`

### Update status TC trong cycle đã có

```powershell
python tools/qmetry_update_status.py `
  --cycle FDP-TR-1 `
  --cycle-id NMMUa7miAok4R `
  --tc FDP-TC-2644 `
  --tc-id LNNtKZJtm142P `
  --status Pass `
  --comment "Verified OK"
```

### Tạo cycle mới, link TC, update status (1 lệnh)

```powershell
python tools/qmetry_update_status.py `
  --create-cycle-link-update "Sprint 12 Regression" `
  --cycle-folder-id 2489725 `
  --tc FDP-TC-2644 `
  --tc-id LNNtKZJtm142P `
  --status Pass
```

### Tạo cycle mới trong folder con (tự tạo folder nếu chưa có)

```powershell
python tools/qmetry_update_status.py `
  --create-cycle-link-update "Sprint 12 Regression" `
  --cycle-parent-folder-id 2489725 `
  --cycle-folder-name regression `
  --tc FDP-TC-2644 `
  --tc-id LNNtKZJtm142P `
  --status Pass
```

### Xem danh sách status IDs

```powershell
python tools/qmetry_update_status.py --list-statuses
```

---

## 4. Workflow điển hình

### A. Tạo TC mới và push lên cycle

```
1. Gen TSV (skill 05-gen-tc-functional)
2. Push lên folder:
   python tools/qmetry_push_testcase_to_folder.py --tsv <file> --folder-id <id>

3. Add vào cycle + đánh kết quả:
   python tools/qmetry_bulk_status.py --cycle FDP-TR-1 --cycle-id NMMUa7miAok4R
     --folder-id <id> --status Fail
```

### B. Cập nhật kết quả sau khi test

```powershell
# Toàn bộ TC trong folder → Pass
python tools/qmetry_bulk_status.py `
  --cycle FDP-TR-1 --cycle-id NMMUa7miAok4R `
  --folder-id 2489720 --status Pass

# Một số TC cụ thể → mix status (dùng file TSV)
python tools/qmetry_bulk_status.py `
  --cycle FDP-TR-1 --cycle-id NMMUa7miAok4R `
  --file testing-output/qmetry/my-updates.tsv
```

---

## 5. Priority mapping

| Trong TSV | Trong QMetry | ID |
|---|---|---|
| `High` | High | 674922 |
| `Medium` | Medium | 674923 |
| `Low` | Low | 674924 |
| `Critical` / `P1` | Critical | 674921 |
| `P2` | High | 674922 |
| `P3` | Medium | 674923 |
| `P4` | Low | 674924 |

> TSV nên dùng `High` / `Medium` / `Low` — tránh `P1/P2/P3/P4`.
