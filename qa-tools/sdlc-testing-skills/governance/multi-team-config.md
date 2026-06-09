# Multi-Team Configuration Guide

Hướng dẫn triển khai QA Skill Suite cho nhiều team trong cùng tổ chức.

---

## Mô hình triển khai

```
Shared skill suite (repo này)
├── skills/                  ← Dùng chung, không thay đổi
├── references/              ← Template dùng chung
├── governance/              ← Governance dùng chung
└── evaluation/              ← Rubric dùng chung

Per-team (mỗi project repo hoặc branch)
├── project/
│   └── qa-config.yaml       ← Config riêng từng team (BẮTBUỘC có team.id)
├── testing-output/
│   └── {team.id}/           ← Output namespace theo team
└── governance/
    └── audit-log.md         ← Audit log riêng từng team
```

---

## qa-config.yaml — Extension cho multi-team

Thêm các field sau vào `qa-config.yaml` của từng team:

```yaml
team:
  id: "team-alpha"                    # unique ID, no spaces, lowercase
  name: "Team Alpha — Payments"
  qc_lead: "Nguyễn Thị QC"
  dev_lead: "Trần Văn Dev"
  pm: "Lê Thị PM"
  product_owner: "Phạm PO"
  stakeholders:
    - name: "Nguyễn Business"
      role: "Finance Business Analyst"
      uat_required: true
  escalation_chain:
    - role: "QC Lead"
      name: "Nguyễn Thị QC"
      contact: "@nguyen-qc"
      sla_hours: 4
    - role: "PM"
      name: "Lê Thị PM"
      contact: "@le-pm"
      sla_hours: 8
    - role: "Director"
      name: "Giám đốc"
      contact: "@director"
      sla_hours: 24

output_paths:
  root: "testing-output/team-alpha"   # Namespace theo team ID
  test_plan: "testing-output/team-alpha/test-plan/"
  test_cases:
    functional: "testing-output/team-alpha/test-cases/functional/"
    sit: "testing-output/team-alpha/test-cases/sit/"
    hltc: "testing-output/team-alpha/test-cases/hltc/"
  test_data: "testing-output/team-alpha/test-data/"
  reports:
    daily: "testing-output/team-alpha/reports/daily/"
    sprint: "testing-output/team-alpha/reports/sprint/"
    gate: "testing-output/team-alpha/reports/gate/"
    html: "testing-output/team-alpha/reports/html/"
  automation: "testing-output/team-alpha/automation/"
```

---

## Isolation rules

| Cấp độ | Rule |
|---|---|
| Output files | Mọi file output phải nằm trong `testing-output/{team.id}/` |
| Audit log | Mỗi team có `governance/audit-log.md` riêng trong project repo |
| qa-config.yaml | Mỗi team có file riêng — không dùng chung |
| Skill files | Dùng chung từ shared repo — không override |

---

## Khi skill suite được dùng với nhiều project cùng lúc

AI phải:
1. Đọc `project/qa-config.yaml` của project đang làm việc để lấy `team.id`
2. Dùng `team.id` làm namespace cho tất cả output paths
3. Append audit log vào file của project đang làm (không cross-team)
4. Sign-off requests gửi đến người trong `team.escalation_chain` của project đó

---

## Shared Confluence space — nếu nhiều team dùng chung Confluence

```yaml
confluence:
  base_url: "https://company.atlassian.net"
  space_key: "QA"                             # Space chung
  parent_pages:
    team_root: "QA / Team Alpha"              # Page gốc riêng từng team
    test_plan: "QA / Team Alpha / Test Plans"
    reports: "QA / Team Alpha / Reports"
```

Tool `tools/confluence_publish_markdown.py` dùng `parent_pages.team_root` để đảm bảo content của mỗi team không bị ghi đè lẫn nhau.

---

## Checklist triển khai team mới

- [ ] Fork hoặc clone skill suite repo
- [ ] Tạo `project/qa-config.yaml` với `team.id` unique
- [ ] Set đầy đủ `output_paths` với namespace `team.id`
- [ ] Set `team.escalation_chain` với đúng người và SLA
- [ ] Tạo Confluence parent page riêng cho team
- [ ] Test thử 1 skill (khuyến nghị: 03-sprint-test-plan) để verify output đúng namespace
- [ ] Add team vào master list của tổ chức (nếu có central tracking)
