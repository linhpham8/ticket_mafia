# Workflow: Requirement → Test Case

## Mục đích
Hướng dẫn từng bước từ khi nhận requirements đến khi có test case sẵn sàng để execute.

## Các bước

```
1. Nhận requirements (AC / BR / User Story / PRD)
        ↓
2. [qa-core/01] review-requirements
   → Output: TSV issues list cho BA/PM
   → Gate: Không còn Blocker trước khi tiếp tục
        ↓
3. [qa-core/02] test-plan (nếu project mới hoặc milestone mới)
   → Output: Master Test Plan + qa-config.yaml
        ↓
4. [qa-core/03] sprint-test-plan (mỗi sprint)
   → Output: Sprint Test Plan 5 mục
        ↓
5. [qa-core/04] test-design-high-level (optional — module phức tạp)
   → Output: HLTC Markdown outline
   → Gate: Approved trước khi viết TC chi tiết
        ↓
6. [qa-core/05] gen-tc-functional
   → Output: tc-functional-*.tsv
        ↓
   [qa-core/06] gen-tc-sit (song song nếu có integration)
   → Output: tc-sit-*.tsv
        ↓
7. [qa-core/07] review-tc
   → Output: Coverage map + Gap analysis + Supplemental TC
   → Gate: Approved trước khi move sang data + automation
        ↓
8. [qa-core/08] gen-data-test
   → Output: master-dataset-*.tsv
```

## Điều kiện chuyển bước

| Từ → Sang | Điều kiện |
|---|---|
| 01 → 03/04/05 | Không còn Blocker issue trong TSV |
| 04 → 05/06 | HLTC gate = Approved |
| 07 → 08 | Review gate = Approved, không còn gap chưa address |
