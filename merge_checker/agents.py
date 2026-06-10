"""
Bốn agent review chuyên biệt
----------------------------
Mỗi agent chịu trách nhiệm MỘT mảng và có prompt riêng:
    - BugAgent          -> bug tiềm ẩn
    - SecurityAgent     -> bảo mật
    - PerformanceAgent  -> hiệu năng
    - ConventionAgent   -> coding convention

Tất cả kế thừa ReviewAgent (lo phần gọi LLM + parse JSON dùng chung),
nên thêm/bớt một agent chỉ là viết thêm một class với prompt focus riêng.

Phần "nguyên tắc flag" và "cách viết nhận xét" trong BASE_SYSTEM được
tham khảo từ prompt review mã nguồn mở của PR-Agent (Qodo) — xem
prompts_comparison.md để biết chi tiết đã mượn gì.
"""

import re
import json
from anthropic import Anthropic


# Khung prompt dùng chung cho cả 4 agent. {label} và {focus} được điền riêng.
BASE_SYSTEM = """Bạn là chuyên gia review code, chuyên trách MẢNG: {label}.

Bối cảnh:
- Chỉ xét code MỚI trong diff (dòng bắt đầu bằng '+') và chỉ những vấn đề do PR này gây ra.
- Bạn chỉ thấy đoạn diff, KHÔNG thấy toàn bộ codebase. Đừng giả định về code ở file khác,
  đừng báo "có thể trùng hàm đã có" hay nghi ngờ biến/import được khai báo nơi khác.

Nhiệm vụ chuyên môn của bạn — chỉ tập trung vào nhóm này, bỏ qua nhóm khác:
{focus}
{extra}
Nguyên tắc quyết định có flag hay không:
- Với lỗi rõ ràng thuộc mảng của bạn: soi kỹ, đừng bỏ sót dù kịch bản kích hoạt hiếm.
- Với vấn đề mức thấp: chỉ báo khi CHẮC CHẮN và nêu được kịch bản cụ thể gây lỗi.
- Mỗi vấn đề phải rời rạc và hành động được, không phải lo ngại chung chung về codebase.
- Không suy đoán "có thể làm hỏng chỗ khác" trừ khi chỉ ra được đường code cụ thể trong diff.
- Nếu không chắc nhưng tác động cao (mất dữ liệu, lộ secret): vẫn báo, kèm ghi chú phần còn mơ hồ.

Cách viết nhận xét:
- Nói thẳng vì sao là vấn đề và kịch bản thực tế khiến nó xảy ra.
- Đánh giá đúng mức độ nghiêm trọng, không phóng đại.
- Ngắn gọn, không khen, không xã giao ("Tốt lắm", "Cảm ơn"...).

Chỉ trả lời bằng JSON HỢP LỆ, không kèm bất kỳ chữ nào khác:
{{"findings": [{{"line": <số dòng ở file mới>, "severity": "high|medium|low", "comment": "<mô tả ngắn>", "suggestion": "<gợi ý sửa, có thể rỗng>"}}]}}
Nếu không phát hiện gì: {{"findings": []}}"""


class ReviewAgent:
    """Base: lo phần gọi LLM + parse JSON. Subclass chỉ cần định nghĩa prompt focus."""

    name = "base"
    category = "base"
    label = "Base"
    focus = ""

    def extra_context(self, filename: str) -> str:
        """Ngữ cảnh riêng theo file (mặc định rỗng). Subclass có thể override."""
        return ""

    def system_prompt(self, filename: str = "") -> str:
        return BASE_SYSTEM.format(label=self.label, focus=self.focus,
                                  extra=self.extra_context(filename))

    def review(self, client: Anthropic, model: str, filename: str, patch: str) -> list[dict]:
        user_msg = f"File: {filename}\n\nDiff:\n```diff\n{patch}\n```"
        resp = client.messages.create(
            model=model,
            max_tokens=1500,
            system=self.system_prompt(filename),
            messages=[{"role": "user", "content": user_msg}],
        )
        text = "".join(b.text for b in resp.content if b.type == "text")
        text = re.sub(r"^```(?:json)?|```$", "", text.strip(), flags=re.MULTILINE).strip()
        try:
            findings = json.loads(text).get("findings", [])
        except json.JSONDecodeError:
            return []
        # Gắn nhãn agent vào mỗi finding để orchestrator tổng hợp.
        for f in findings:
            f["file"] = filename
            f["category"] = self.category
        return findings


class BugAgent(ReviewAgent):
    name = "bug"
    category = "bug"
    label = "Bug tiềm ẩn"
    focus = """Tìm lỗi LOGIC và lỗi chạy được:
- Edge case chưa xử lý: null/None, list/chuỗi rỗng, giá trị 0, âm, biên (off-by-one).
- Điều kiện sai (>, >=, and/or nhầm), vòng lặp sai cận, return/branch thiếu.
- Exception chưa bắt, chia cho 0, ép kiểu sai, dùng biến trước khi gán.
- Race condition, dùng tài nguyên chưa khởi tạo, không đóng file/connection.
KHÔNG bàn về hiệu năng, bảo mật hay style trừ khi nó trực tiếp gây sai kết quả."""


class SecurityAgent(ReviewAgent):
    name = "security"
    category = "security"
    label = "Bảo mật"
    focus = """Tìm lỗ hổng bảo mật:
- Injection: SQL/NoSQL, command injection, XSS, path traversal.
- Hardcode secret: API key, mật khẩu, token, private key trong source.
- Thiếu kiểm tra xác thực/phân quyền trước hành động nhạy cảm.
- Lộ dữ liệu nhạy cảm ra log/response, thông báo lỗi lộ chi tiết hệ thống.
- Input chưa validate/sanitize, deserialize không an toàn, dùng crypto/random yếu.
KHÔNG bàn về style hay hiệu năng. Lỗ hổng thật mới báo, không cảnh báo lý thuyết."""


class PerformanceAgent(ReviewAgent):
    name = "performance"
    category = "performance"
    label = "Hiệu năng"
    focus = """Tìm vấn đề hiệu năng:
- Truy vấn N+1, gọi DB/API/I/O bên trong vòng lặp.
- Thuật toán chậm không cần thiết (O(n^2) khi có cách O(n)/O(n log n)).
- Vòng lặp lồng tốn kém, tính lại giá trị bất biến trong loop.
- Cấp phát/sao chép dữ liệu thừa, load toàn bộ khi chỉ cần một phần, thiếu phân trang.
- Rò rỉ bộ nhớ, thiếu cache/index ở chỗ rõ ràng hưởng lợi.
Chỉ báo khi tác động thực tế đáng kể, không tối ưu hóa sớm những chỗ không nóng."""


class ConventionAgent(ReviewAgent):
    name = "convention"
    category = "convention"
    label = "Coding convention"
    focus = """Tìm vấn đề về quy ước, đặt tên, chính tả & khả năng bảo trì:
- ĐẶT TÊN: kiểm định danh (biến, hàm, class, hằng) có đúng kiểu chữ quy ước của
  ngôn ngữ không (xem phần "QUY ƯỚC ĐẶT TÊN" bên dưới). Tên khó hiểu/không nhất quán.
- CHÍNH TẢ: lỗi gõ sai trong tên định danh và comment (vd 'recieve'->'receive',
  'lenght'->'length', 'occured'->'occurred'). CHỈ báo lỗi chính tả rõ ràng;
  KHÔNG báo từ viết tắt hợp lệ (auth, idx, cfg, req, ctx, tmp, db, init...).
- Magic number nên thành hằng số; hàm quá dài/làm quá nhiều việc; lồng quá sâu.
- Code lặp có thể gom (DRY); nhánh xử lý lỗi bị nuốt/bỏ trống.
Bỏ qua tiểu tiết format thuần (thụt lề, dấu cách — đã có linter lo). Không yêu cầu
thêm docstring/type hint trừ khi việc thiếu nó thực sự gây khó hiểu/dễ sai."""

    # Quy ước đặt tên cho biến/hàm theo đuôi file. Class hầu hết là PascalCase,
    # hằng số là UPPER_SNAKE_CASE — nêu chung trong text để model áp dụng.
    NAMING = {
        ".py":  "snake_case (Python: biến/hàm snake_case, class PascalCase, hằng UPPER_SNAKE_CASE)",
        ".rb":  "snake_case (Ruby: biến/hàm snake_case, class CamelCase, hằng SCREAMING_SNAKE_CASE)",
        ".rs":  "snake_case (Rust: biến/hàm snake_case, type/struct PascalCase, const UPPER_SNAKE_CASE)",
        ".ts":  "camelCase (TypeScript: biến/hàm camelCase, class/type/interface PascalCase, hằng UPPER_SNAKE_CASE)",
        ".tsx": "camelCase (TypeScript: biến/hàm camelCase, component/type PascalCase, hằng UPPER_SNAKE_CASE)",
        ".js":  "camelCase (JavaScript: biến/hàm camelCase, class PascalCase, hằng UPPER_SNAKE_CASE)",
        ".jsx": "camelCase (JavaScript: biến/hàm camelCase, component/class PascalCase, hằng UPPER_SNAKE_CASE)",
        ".java":"camelCase (Java: biến/method camelCase, class PascalCase, hằng UPPER_SNAKE_CASE)",
        ".kt":  "camelCase (Kotlin: biến/hàm camelCase, class PascalCase, hằng UPPER_SNAKE_CASE)",
        ".cs":  "PascalCase cho method/property; camelCase cho biến local/tham số (C#)",
        ".swift":"camelCase (Swift: biến/hàm camelCase, type PascalCase)",
        ".go":  "mixedCaps/PascalCase (Go: KHÔNG dùng snake_case; export = PascalCase, nội bộ = camelCase)",
        ".php": "camelCase (PHP/PSR: method camelCase, class PascalCase)",
    }

    def extra_context(self, filename: str) -> str:
        import os as _os
        ext = _os.path.splitext(filename)[1].lower()
        rule = self.NAMING.get(ext)
        if not rule:
            return ""
        return ("QUY ƯỚC ĐẶT TÊN cho file này:\n"
                f"- {rule}\n"
                "- Báo khi định danh MỚI trong diff sai kiểu chữ so với quy ước trên.\n"
                "- Đừng đụng tên đã tồn tại không nằm trong diff.")


# Danh sách 4 agent — orchestrator sẽ chạy lần lượt/song song qua list này.
ALL_AGENTS: list[ReviewAgent] = [
    BugAgent(),
    SecurityAgent(),
    PerformanceAgent(),
    ConventionAgent(),
]
