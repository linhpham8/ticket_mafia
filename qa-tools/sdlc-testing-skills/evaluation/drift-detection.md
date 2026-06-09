# AI Drift Detection Guide

Hướng dẫn phát hiện và xử lý khi AI bắt đầu tạo ra output kém chất lượng hơn theo thời gian (model drift, prompt drift, context drift).

---

## Tại sao drift xảy ra?

1. **Model update**: Model AI được update, behavior thay đổi
2. **Context accumulation**: Session dài làm AI "quên" bớt instruction đầu
3. **Skill file stale**: Skill file không được cập nhật khi quy trình thay đổi
4. **Shortcut learning**: AI học pattern người dùng accept output ngắn → output ngày càng ngắn
5. **Routing failure**: AI route sai skill, dùng heuristic thay vì đọc skill file

---

## Signals cần theo dõi hàng sprint

### Signal 1 — Output length drift
```
Baseline: Sprint 1, skill 09-check-result output trung bình 800 dòng
Alert: Sprint 5, output trung bình 400 dòng (-50%)
```
Cách check: So sánh file size của daily-report giữa các sprint.

### Signal 2 — Missing sections
```
Sprint 1: Mọi daily report đều có improvement_snapshot YAML block
Sprint 4: 3/10 report thiếu improvement_snapshot
```
Cách check: `grep -l "improvement_snapshot" testing-output/reports/daily/`

### Signal 3 — Format regression
```
Sprint 1: TSV có đủ 15 cột, trace đúng Rule ID
Sprint 6: TC file chỉ có 10 cột, trace field trống
```
Cách check: Đếm cột header trong TSV file, grep trace field.

### Signal 4 — Gate bypass
```
Sprint 1: go-no-go report luôn có sign-off request
Sprint 7: AI đôi khi tự kết luận DONE mà không emit sign-off request
```
Cách check: `grep "APPROVAL REQUIRED" testing-output/reports/gate/*.md`

### Signal 5 — Routing accuracy
```
Sprint 1: User nhắc "daily report" → AI chạy skill 09
Sprint 5: User nhắc "daily report" → AI tự gen format riêng mà không đọc skill 09
```
Cách check: Review audit-log, xem skill name có khớp với intent không.

---

## Drift detection protocol (chạy cuối mỗi sprint)

```markdown
### Sprint Drift Check — {Sprint-N}

**1. Sample 3 output ngẫu nhiên từ sprint:**
- [path/output-1]
- [path/output-2]
- [path/output-3]

**2. Score theo evaluation/skill-quality-rubric.md**
Avg score: [N]/10

**3. So sánh với Sprint trước:**
- Sprint N-1 avg: [N]/10
- Delta: [+/-N]

**4. Check specific signals:**
- [ ] Output length trong ±20% của baseline
- [ ] improvement_snapshot present trong 100% daily reports
- [ ] TSV files đủ 15 cột
- [ ] Sign-off requests present trong L2/L3 skills
- [ ] Audit log entries đầy đủ

**5. Kết luận:**
- ✅ No drift detected
- ⚠️ Minor drift — monitor
- ❌ Drift detected — action required
```

---

## Action khi phát hiện drift

### Minor drift (score giảm 1-1.5 điểm):
1. Re-read skill file và check nếu có section bị unclear
2. Thêm explicit example vào skill file cho section bị drift
3. Test lại với cùng input → compare output

### Major drift (score giảm >1.5 điểm hoặc signal 4/5):
1. Restart conversation mới (clear context)
2. Đọc lại CLAUDE.md / AGENTS.md explicitly
3. Chạy lại skill với instruction: "Đọc kỹ [skill-file] trước khi trả lời"
4. Nếu vẫn drift → review và rewrite skill file

### Structural drift (AI không follow routing):
1. Kiểm tra SKILL.md routing table còn đúng không
2. Kiểm tra AGENTS.md / copilot-instructions.md còn match routing table
3. Check nếu keyword mới cần thêm vào routing

---

## Baseline metrics (set khi triển khai lần đầu)

```yaml
# Lưu file này sau sprint đầu tiên thành công
baseline:
  sprint: "Sprint-1"
  date: "{yyyy-mm-dd}"
  skills_evaluated:
    - skill: "09-check-result"
      avg_output_lines: 280
      avg_score: 9.0
      sections_present: ["improvement_snapshot", "sprint_snapshot", "health_score"]
    - skill: "05-gen-tc-functional"
      avg_output_lines: 120
      avg_score: 8.5
      tc_columns: 15
    - skill: "13-go-no-go"
      avg_output_lines: 80
      avg_score: 9.0
      sign_off_emitted: true
  alert_thresholds:
    score_drop_minor: 1.0
    score_drop_major: 1.5
    output_length_drop_pct: 20
```

Lưu file này tại: `evaluation/baseline.yaml`
