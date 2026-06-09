# Workflow: Regression Cycle

## Mục đích
Quy trình chạy regression cuối sprint hoặc trước release.

## Các bước

```
1. [qa-core/09] check-result (daily trong sprint)
   → Sprint Snapshot tích lũy mỗi ngày
        ↓
2. Cuối sprint: paste Sprint Snapshot → [qa-core/10] test-report
   → Output: Sprint Report + Ship Readiness
        ↓
3. [qa-core/11] demo-preparation (song song)
   → Output: Demo Script + Pre-demo checklist
        ↓
4. [qa-core/12] uat-support (nếu cần UAT)
   → Output: UAT sign-off tracking
        ↓
5. [qa-core/13] go-no-go
   → Input: Sprint Report + UAT result + Security/Perf (nếu có)
   → Output: Go/No-Go Report với quyết định rõ ràng
        ↓
6. Nếu GO: [qa-core/14] smoke-production sau deploy
   → Output: Production smoke result
```

## Parallel tracks

Trong khi regression chạy, các track sau chạy độc lập:
- `qa-specialist/01` security-testing
- `qa-specialist/02` performance-testing
- `qa-specialist/03` accessibility-testing

Kết quả 3 tracks này đưa vào Gate 3, 3.5, 4 của `go-no-go`.
