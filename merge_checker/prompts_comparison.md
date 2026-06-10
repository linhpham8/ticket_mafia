# So sánh prompt & kiến trúc với các framework có sẵn

Tài liệu này đối chiếu cách thiết kế prompt trong project (4 agent chuyên biệt) với các tool code-review thực tế, để thấy mình đang đứng ở đâu và đã học/mượn được gì.

---

## 1. Hai trường phái kiến trúc

| Kiểu | Cách làm | Tool tiêu biểu |
|------|----------|----------------|
| **Một prompt tổng hợp** | 1 lần gọi LLM, một "reviewer" lo tất cả (bug + security + perf), kết quả trả về có trường phân loại | PR-Agent (open-source), GitHub Copilot review |
| **Nhiều agent chuyên biệt** | Mỗi mảng một agent/prompt riêng, chạy song song rồi gộp | Project này, Qodo 2.0 (Qodo Merge), Anthropic multi-agent, Cursor BugBot |

Project của mình thuộc nhóm thứ hai. Đây cũng là hướng các tool thương mại đang chuyển sang: Qodo Merge dùng các agent chuyên biệt riêng cho bug, security, code quality và test coverage chạy song song; còn hệ thống mới của Anthropic dùng các agent đi tìm bug, verify lại để giảm false positive, rồi xếp hạng theo độ nghiêm trọng. Cursor BugBot thì cực đoan hơn: chạy 8 lượt phân tích song song với thứ tự diff ngẫu nhiên, rồi dùng majority vote cộng một bộ validator để chọn finding nào đáng giữ.

---

## 2. Prompt của PR-Agent (mã nguồn mở) — phân tích

PR-Agent (Qodo, ~10.8k sao GitHub) dùng **một prompt tổng hợp**, persona tên "PR-Reviewer". File `pr_reviewer_prompts.toml` dài ~350 dòng. Những kỹ thuật prompt đáng chú ý (diễn giải lại):

**a) Khoá phạm vi để giảm false positive.** Prompt nhấn mạnh chỉ xét code mới (dòng `+`) và chỉ vấn đề do PR này tạo ra. Đặc biệt nó cảnh báo model rằng nó **chỉ thấy đoạn diff chứ không thấy toàn codebase**, nên đừng nghi ngờ biến/import được khai báo ở nơi khác hay báo "trùng hàm đã có" — đây là nguồn false positive kinh điển.

**b) Quy tắc "khi nào thì flag".** Prompt phân tầng: với bug và lỗ hổng bảo mật thì soi kỹ, đừng bỏ sót; với vấn đề mức thấp thì phải chắc chắn và nêu được kịch bản cụ thể mới báo. Không được suy đoán "có thể làm hỏng chỗ khác" nếu không chỉ ra đường code cụ thể. Nếu không chắc nhưng tác động cao thì vẫn báo kèm ghi chú phần còn mơ hồ.

**c) Quy tắc viết comment.** Yêu cầu nói thẳng vì sao là vấn đề + kịch bản thực tế, đánh giá đúng mức độ, ngắn gọn, và tránh khen hay xã giao. Prompt còn liệt kê thẳng những cụm cần tránh như lời cảm ơn sáo rỗng.

**d) Output có cấu trúc + trường security riêng.** Bắt model trả YAML theo schema Pydantic. Đáng chú ý là nó tách hẳn một trường `security_concerns`, và yêu cầu nếu có lỗ hổng thì mở đầu bằng header dạng phân loại (ví dụ "SQL injection: ..."). Tức là dù dùng một prompt, PR-Agent vẫn **mô phỏng tư duy nhiều mảng** bằng cách ép schema.

**e) Định dạng diff riêng + số dòng tham chiếu.** Nó không đưa diff thô mà gói lại thành các khối `__new hunk__` / `__old hunk__` kèm số dòng để model trỏ chính xác — giải quyết đúng bài toán map line mà project mình xử lý bằng `parse_added_lines()`.

**f) Tính năng bật/tắt bằng template.** Qua Jinja, PR-Agent bật thêm: chấm điểm công sức review (1–5), điểm chất lượng PR (0–100), kiểm tra có test chưa, quét TODO, gợi ý tách PR, đối chiếu yêu cầu ticket. Đây là thứ project mình chưa có và là hướng mở rộng tốt.

> Quan sát: PR-Agent dồn tất cả vào một prompt rất dài và một schema giàu trường. Mạnh ở chi phí (1 lần gọi) nhưng prompt cồng kềnh, khó tinh chỉnh riêng từng mảng.

---

## 3. Các tool khác (mức tổng quan)

- **CodeRabbit** (SaaS, không mở prompt): điểm mạnh quảng bá là phân tích đồ thị code (Code Graph) và tra cứu web thời gian thực, tức là **bơm thêm context** ngoài diff chứ không chỉ chỉnh prompt. Greptile thì index toàn bộ codebase và điều tra nhiều bước, được cho là bắt được 82% bug so với 44% của CodeRabbit.
- **Qodo Merge / Anthropic**: multi-agent + bước verify riêng để hạ false positive (giống mục 1).
- **Điểm chung quan trọng nhất:** chất lượng review không chỉ nằm ở prompt, mà ở **lượng context đưa vào** (cả repo, lịch sử, ticket) và **bước hậu kiểm** (verify/voting). Prompt chỉ là một phần.

---

## 4. Đối chiếu trực tiếp với prompt của project

| Tiêu chí | Project (4 agent) | PR-Agent (1 prompt) |
|----------|-------------------|---------------------|
| Số lần gọi LLM / file | 4 (song song) | 1 |
| Tách mảng | Bằng **agent riêng**, prompt focus riêng | Bằng **trường trong schema** |
| Khoá phạm vi "+ lines" | Có | Có |
| Cảnh báo "không thấy cả codebase" | Có (đã mượn) | Có |
| Quy tắc flag phân tầng | Có (đã mượn) | Có |
| Quy tắc viết comment (cấm khen/xã giao) | Có (đã mượn) | Có |
| Output có cấu trúc | JSON | YAML + Pydantic |
| Định dạng diff đặc biệt + số dòng | Không (dùng diff thô + parse line ở code) | Có (`__new/old hunk__`) |
| Verify/voting giảm false positive | Chưa có | Chưa có (bản OSS) |
| Chấm điểm PR / quét TODO / tách PR | Chưa có | Có |

**Chi phí đánh đổi:** 4 agent = prompt mỗi con ngắn, dễ chỉnh, dễ bật/tắt từng mảng, dễ giải thích "ai chịu trách nhiệm gì" — nhưng tốn ~4× token và phải gộp/khử trùng kết quả. PR-Agent 1 prompt thì rẻ và mạch lạc hơn về severity tổng thể, nhưng prompt phình to và khó tách bạch từng mối quan tâm.

---

## 5. Những gì project đã mượn từ PR-Agent

Ba khối trong `BASE_SYSTEM` (file `agents.py`) tham khảo trực tiếp từ prompt PR-Agent:
1. **Khoá phạm vi**: chỉ xét dòng `+`, cảnh báo model không thấy toàn codebase → chống false positive.
2. **Quy tắc flag phân tầng**: soi kỹ bug/security, nâng ngưỡng cho vấn đề mức thấp, không suy đoán thiếu căn cứ, báo cái rủi-ro-cao-nhưng-chưa-chắc kèm ghi chú.
3. **Quy tắc viết comment**: thẳng + nêu kịch bản, đúng severity, ngắn, cấm khen/xã giao.

Điểm project làm **khác đi có chủ đích**: thay vì một persona lo tất cả, mình chia thành 4 agent để mỗi prompt chỉ chăm một mảng — dễ mở rộng (thêm agent = thêm 1 class) và minh bạch về phân loại, đúng tinh thần kiến trúc multi-agent mà các tool thương mại đang theo.

---

## 6. Nguồn

- PR-Agent (Qodo) — prompt review mã nguồn mở: `github.com/qodo-ai/pr-agent` (`pr_agent/settings/pr_reviewer_prompts.toml`).
- So sánh kiến trúc multi-agent: các bài đánh giá CodeRabbit / Qodo Merge / Anthropic / Cursor BugBot 2026.
