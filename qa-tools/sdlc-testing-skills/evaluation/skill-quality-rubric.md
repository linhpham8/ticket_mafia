# Skill Output Quality Rubric

Rubric đánh giá chất lượng output của từng skill. Dùng để:
1. QA Lead review output trước khi approve (L2/L3 gates)
2. Monthly audit để phát hiện AI drift
3. Benchmark chất lượng theo sprint

---

## Scoring framework — 4 dimensions (tổng 10 điểm)

| Dimension | Max | Mô tả |
|---|---|---|
| Completeness | 3 | Đủ tất cả section bắt buộc của skill |
| Format compliance | 3 | Đúng format (header, table, TSV columns, field names) |
| Accuracy | 2 | Logic nhất quán, numbers add up, traces đúng |
| Actionability | 2 | Output đủ cụ thể để act on ngay, không cần hỏi thêm |

**Thang điểm:**
- 9-10: Excellent — enterprise quality
- 7-8: Good — minor issues, acceptable
- 5-6: Acceptable — notable gaps, cần manual fix
- 3-4: Poor — major rework needed
- 0-2: Failed — output không dùng được

---

## Rubric theo skill

### Skills 01-03 (Requirements Review + Test Plan)

| Dimension | 3 điểm | 2 điểm | 1 điểm | 0 điểm |
|---|---|---|---|---|
| Completeness | Đủ tất cả section per skill spec | Thiếu 1 section phụ | Thiếu 1 section bắt buộc | Thiếu nhiều section |
| Format | TSV/MD đúng header, traceability ID có, naming file đúng | Lệch nhỏ về format | Lệch lớn, cần reformat | Sai hoàn toàn |
| Accuracy | Không có mâu thuẫn, số liệu/ước tính hợp lý | 1-2 mâu thuẫn nhỏ | Mâu thuẫn rõ | Logic sai cơ bản |
| Actionability | BA/Dev có thể act ngay trên output | Cần 1-2 làm rõ | Cần nhiều làm rõ | Không actionable |

### Skills 05-07 (Test Case Design + Review)

| Dimension | 3 điểm | 2 điểm | 1 điểm | 0 điểm |
|---|---|---|---|---|
| Completeness | 12 nhóm TC đủ, mọi AC/BR có ít nhất 1 TC, DoD pass | Thiếu 1-2 nhóm phụ | Thiếu nhóm quan trọng (happy path thiếu) | Coverage rất thấp |
| Format | 15 cột đủ, TSV valid, trace đúng Rule ID | 1-2 cột thiếu data | Nhiều cột trống, trace sai format | Format sai |
| Accuracy | Step logic rõ, Expected result cụ thể, data hợp lý | 1-2 step mơ hồ | Step không rõ, Expected result chung chung | Không thể execute |
| Actionability | Tester có thể execute ngay | Cần 1-2 hỏi về data | Cần nhiều clarification | Không execute được |

### Skills 09-10 (Daily + Sprint Report)

| Dimension | 3 điểm | 2 điểm | 1 điểm | 0 điểm |
|---|---|---|---|---|
| Completeness | Daily: đủ triage + health score + sprint snapshot. Sprint: đủ 5 mục báo cáo | Thiếu sprint snapshot hoặc health score | Thiếu triage hoặc action items | Thiếu nhiều |
| Format | Markdown + HTML đúng template, YAML improvement_snapshot valid | Lệch nhỏ format | Template sai nhiều | Không theo template |
| Accuracy | Numbers consistent (pass+fail+blocked=total), health score tính đúng | 1 sai số nhỏ | Số liệu mâu thuẫn | Số sai hoàn toàn |
| Actionability | Action items cụ thể, assignee rõ, deadline rõ | Action items chung | Không có action items | Report chỉ mô tả, không đề xuất |

### Skills 12-14 (UAT + Go/No-Go + Smoke)

| Dimension | 3 điểm | 2 điểm | 1 điểm | 0 điểm |
|---|---|---|---|---|
| Completeness | Tất cả gate đánh giá, sign-off request rõ, audit log entry đủ | Thiếu 1 gate | Thiếu >1 gate | Thiếu cơ bản |
| Format | Report đúng template, decision section rõ ràng (GO/NO-GO/STABLE/ROLLBACK) | Decision có nhưng mơ hồ | Không rõ quyết định | Không có quyết định |
| Accuracy | Gate pass/fail logic đúng, no S1 → GO, rollback trigger rõ | 1 logic lỗi | Nhiều logic lỗi | Logic sai cơ bản |
| Actionability | Stakeholder biết làm gì ngay sau đọc | Cần 1-2 câu hỏi thêm | Cần nhiều clarification | Không actionable |

---

## Cách dùng rubric

### Monthly audit (khuyến nghị ngày 1 mỗi tháng):

1. Chọn ngẫu nhiên 3-5 output từ sprint vừa qua
2. Score từng output theo rubric
3. So sánh với tháng trước
4. Ghi vào `evaluation/audit-history.md` (tạo nếu chưa có)

### Red flags cần action ngay:

| Signal | Threshold | Action |
|---|---|---|
| Average score giảm liên tiếp 2 tháng | Giảm > 1 điểm | Review và update skill file liên quan |
| Format compliance < 2 điểm thường xuyên | >30% output bị | Update format instructions trong skill |
| Actionability < 2 điểm | >20% output bị | Thêm examples vào skill file |
| Missing section xuất hiện pattern | Same section bị bỏ | Thêm checklist enforcement vào skill |

---

## audit-history.md template

```markdown
# Skill Quality Audit History

## {yyyy-mm} — {Tháng}

| Skill | Score | Completeness | Format | Accuracy | Actionability | Sample output |
|---|---|---|---|---|---|---|
| 09-check-result | 8.5 | 3 | 2.5 | 2 | 1 | testing-output/reports/daily/daily-2026-05-01.md |
| 13-go-no-go | 9 | 3 | 3 | 2 | 1 | testing-output/reports/gate/go-no-go-Sprint12.md |

**Trend:** Up / Down / Stable vs. tháng trước
**Action items:**
- [ ] {action nếu có}
```
