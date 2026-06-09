# Workflow: Test Case → Automation Script

## Mục đích
Từ test case đã approve đến automation script sẵn sàng chạy trong CI.

## Các bước

```
1. TC đã approve (output từ qa-core/05, 06, 07)
        ↓
2. [qa-automation/01] setup-automation (lần đầu cho project)
   → Output: testing-output/automation/ scaffold đầy đủ
        ↓
3. [qa-automation/02] gen-script-test
   → Input: TC file + qa-config.yaml + docs/
   → Bước bắt buộc: Mapping matrix trước khi code
   → Output: .robot files + keyword files + data files
        ↓
4. Review script (manual hoặc qa-core/07 review-tc)
   → Checklist: ai-execution-spec.md DoD
        ↓
5. [qa-automation/04] ci-cd (khi ready)
   → Tích hợp vào pipeline
```

## Quy tắc AI khi gen script

- Đọc `references/ai-execution-spec.md` trước khi generate bất kỳ dòng code nào
- Không generate lại CommonKeyword — reuse từ `KeywordLibraries/CommonKeyword/`
- Mapping matrix là output bắt buộc trước khi code
- DoD checklist phải pass trước khi bàn giao
