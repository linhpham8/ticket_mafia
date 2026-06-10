"""
Bước verify — lọc false positive (LLM-as-judge)
-----------------------------------------------
Sau khi 4 agent trả findings, mỗi finding được "thẩm định" lại bằng một lượt
gọi LLM riêng đóng vai NGƯỜI KIỂM ĐỊNH nghiêm khắc: xác nhận (confirm) hay
loại bỏ (reject). Mục tiêu DUY NHẤT là giảm báo động giả (false positive) —
KHÔNG tìm thêm lỗi mới.

Vì sao tách riêng bước này:
  Anthropic (multi-agent) và Cursor BugBot đều tách hẳn một bước hậu kiểm sau
  bước phát hiện để hạ false positive — agent đi tìm lỗi thường "thà báo nhầm
  còn hơn bỏ sót", nên cần một lượt thứ hai chỉ chuyên đi bác bỏ. File này là
  phiên bản tối giản của ý tưởng đó: gom findings theo từng file rồi hỏi lại
  model MỘT lần / file (rẻ hơn hỏi từng finding, lại cho thẩm phán thấy các
  finding cùng file để phát hiện trùng lặp).

Triết lý FAIL-OPEN: nếu verifier lỗi hoặc trả JSON hỏng -> giữ nguyên findings.
Thà để lọt một false positive còn hơn vô tình nuốt mất một lỗi thật.
"""

import re
import json

from anthropic import Anthropic


VERIFY_SYSTEM = """Bạn là NGƯỜI KIỂM ĐỊNH lại các phát hiện của agent review code.
Với mỗi phát hiện, quyết định nó CÓ THẬT là vấn đề do diff này gây ra hay không.
Bạn nghiêm khắc: mục tiêu là LOẠI BỎ báo động giả (false positive), KHÔNG tìm thêm lỗi mới.

Bối cảnh:
- Bạn chỉ thấy đoạn diff, KHÔNG thấy toàn bộ codebase.
- Mỗi phát hiện gồm: 'id', 'category', 'line', 'severity', 'comment', 'suggestion'.

LOẠI BỎ (verdict="reject") khi:
- Suy đoán về code ngoài diff (biến/hàm/import "có thể" sai ở file khác).
- Lo ngại lý thuyết, không nêu được kịch bản cụ thể kích hoạt trong diff.
- Nitpick style đội lốt bug; hoặc trùng nội dung một phát hiện khác (giữ cái rõ nhất, bỏ phần còn lại).
- Số dòng trỏ sai chỗ, hoặc mô tả không khớp với code thực tế trong diff.

GIỮ LẠI (verdict="confirm") khi:
- Chỉ ra được đường code cụ thể TRONG DIFF gây ra vấn đề.
- Kịch bản kích hoạt rõ ràng và hợp lý.
- Khi giữ: chỉnh 'severity' về đúng mức thực tế (đừng phóng đại, cũng đừng hạ thấp lỗi nặng).

Chỉ trả JSON HỢP LỆ, không kèm bất kỳ chữ nào khác:
{"verdicts": [{"id": <int>, "verdict": "confirm|reject", "severity": "high|medium|low", "reason": "<ngắn gọn vì sao>"}]}
Phải trả verdict cho MỌI id được đưa vào, không thiếu id nào."""


def _strip_fence(text: str) -> str:
    """Bỏ ```json ... ``` nếu model lỡ bọc code fence."""
    return re.sub(r"^```(?:json)?|```$", "", text.strip(), flags=re.MULTILINE).strip()


class Verifier:
    """Thẩm định lại toàn bộ findings của MỘT file trong một lượt gọi LLM."""

    def _format_findings(self, findings: list[dict]) -> str:
        """Đánh số id theo vị trí trong list rồi serialize mỗi finding thành 1 dòng JSON."""
        rows = []
        for i, f in enumerate(findings):
            rows.append(json.dumps(
                {
                    "id": i,
                    "category": f.get("category"),
                    "line": f.get("line"),
                    "severity": f.get("severity"),
                    "comment": f.get("comment"),
                    "suggestion": f.get("suggestion", ""),
                },
                ensure_ascii=False,
            ))
        return "\n".join(rows)

    def verify(self, client: Anthropic, model: str,
               filename: str, patch: str, findings: list[dict]) -> list[dict]:
        """
        Trả về danh sách findings ĐÃ LỌC:
          - bỏ những finding bị reject,
          - cập nhật lại severity nếu verifier chỉnh,
          - giữ nguyên finding nếu verifier không trả verdict cho id đó (an toàn).
        """
        if not findings:
            return []

        user_msg = (
            f"File: {filename}\n\n"
            f"Diff:\n```diff\n{patch}\n```\n\n"
            f"Các phát hiện cần thẩm định (mỗi dòng một JSON):\n{self._format_findings(findings)}"
        )

        try:
            resp = client.messages.create(
                model=model,
                max_tokens=1500,
                system=VERIFY_SYSTEM,
                messages=[{"role": "user", "content": user_msg}],
            )
            text = "".join(b.text for b in resp.content if b.type == "text")
            verdicts = json.loads(_strip_fence(text)).get("verdicts", [])
        except Exception as e:  # noqa: BLE001 — fail-open có chủ đích
            # Verifier hỏng (API lỗi / JSON sai) -> KHÔNG lọc gì, giữ nguyên findings.
            print(f"[warn] Verify {filename} lỗi ({type(e).__name__}); giữ nguyên findings.")
            return findings

        by_id = {v.get("id"): v for v in verdicts if isinstance(v.get("id"), int)}

        kept = []
        for i, f in enumerate(findings):
            v = by_id.get(i)
            if v is None:
                # Verifier quên trả id này -> giữ lại cho an toàn (fail-open).
                kept.append(f)
                continue
            if v.get("verdict") == "reject":
                continue  # bỏ false positive
            # confirm: cập nhật severity nếu verifier chỉnh lại về mức hợp lệ.
            if v.get("severity") in ("high", "medium", "low"):
                f["severity"] = v["severity"]
            kept.append(f)
        return kept
