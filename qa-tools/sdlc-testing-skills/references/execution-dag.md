# Execution DAG

## Thứ tự thực hiện trong sprint

```
Giai đoạn Review & Planning
  01 (Review Requirements) ──────────────────  AC / BR / PRD → TSV issues list
  02 (Test Plan) ─────────────────────────────  → Master Test Plan + qa-config.yaml
  03 (Sprint Test Plan) ──────────────────────  → Sprint Test Plan (mỗi sprint)

Giai đoạn Thiết kế & Chuẩn bị                      Artifact cần trước
  04 (High-Level Test Design, optional) ──────  AC / BR → HLTC Markdown outline
  05 (Gen TC Functional) ─────────────────────  AC / BR (+ HLTC từ 04 nếu có)
  06 (Gen TC SIT) ────────────────────────────  API spec / sequence diagram
  07 (Review TC) ─────────────────────────────  Output của 05 / 06, hoặc TC có sẵn
  08 (Gen Data Test) ─────────────────────────  Output của 05 / 06

Automation (song song khi cần)
  qa-automation/01 (Setup Automation) ────────  Lần đầu cho project
  qa-automation/02 (Gen Script Test) ─────────  TC approve từ 05/06/07 + qa-config.yaml

Giai đoạn Thực thi
  09 (Check Result) ──────────────────────────  Kết quả pass/fail từ test run
  09 ──► 09 ──► … (chạy lặp mỗi ngày, tích lũy Sprint Snapshot)

Giai đoạn Báo cáo
  10 (Test Report) ───────────────────────────  Sprint Snapshot từ 09

Giai đoạn Release
  11 (Demo Preparation) ──────────────────────  Danh sách ticket DONE
  12 (UAT Support) ───────────────────────────  TC + môi trường UAT
  13 (Go/No-Go) ──────────────────────────────  Output 09/10 + kết quả specialist (nếu có)
  14 (Smoke Production) ──────────────────────  Deploy xong + approval từ 13

Specialist testing — chạy song song khi cần, không phụ thuộc thứ tự lẫn nhau
  qa-specialist/01 (Security Testing) ────────  URL staging + tài khoản test
  qa-specialist/02 (Performance Testing) ─────  URL staging + API list
  qa-specialist/03 (Accessibility Testing) ───  URL staging + danh sách trang
```

## Bắt đầu giữa sprint (không có artifact từ bước trước)

- Có TC sẵn → bỏ qua 01–06, vào thẳng 07 (review) hoặc 08 (data)
- Có function logic phức tạp nhưng chưa cần TC chi tiết → chạy 04 (HLTC) trước, sau đó mới vào 05 và 06
- Không có `qa-config.yaml` → skill vẫn chạy được; dùng thông tin user cung cấp trực tiếp (xem Nhóm B)
- Không có Sprint Snapshot → 10 chấp nhận fallback: kết quả TC + danh sách bug tổng hợp thủ công

## Gate conditions

| Từ → Sang | Điều kiện |
|---|---|
| 01 → 03/04/05 | Không còn Blocker issue trong TSV |
| 04 → 05/06 | HLTC gate = Approved |
| 07 → 08 | Review gate = Approved, không còn gap chưa address |
| 09/10/12 → 13 | Sprint Report hoàn chỉnh + specialist results (nếu có) |
| 13 → 14 | Go/No-Go quyết định GO |
