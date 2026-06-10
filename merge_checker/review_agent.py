"""
AI Code Review Agent — Orchestrator (GitHub + GitLab)
-----------------------------------------------------
Luồng:
  1. Chọn nền tảng (GitHub PR hoặc GitLab MR) — tự nhận từ biến môi trường CI,
     hoặc chỉ định bằng --platform.
  2. Lấy diff các file thay đổi (qua client tương ứng).
  3. Với mỗi file, chạy SONG SONG 4 agent (bug / security / performance / convention).
  4. VERIFY: thẩm định lại từng findings để loại false positive (bật/tắt bằng REVIEW_VERIFY).
  5. Gộp findings.
  6. Comment vào PR/MR (1 comment tổng hợp + comment inline đúng dòng).

Phần 4 agent (agents.py), bước verify (verifier.py) và phần này KHÔNG phụ thuộc
nền tảng — chỉ tầng client (clients.py) là khác nhau giữa GitHub và GitLab.

Chạy thử:
  # GitHub
  python review_agent.py --platform github --repo owner/repo --pr 12 --dry-run
  # GitLab
  python review_agent.py --platform gitlab --project 123 --mr 5 --dry-run
"""

import os
import re
import sys
import argparse
from concurrent.futures import ThreadPoolExecutor

from anthropic import Anthropic

from agents import ALL_AGENTS
from verifier import Verifier
from clients import GitHubClient, GitLabClient

MODEL = os.getenv("REVIEW_MODEL", "claude-sonnet-4-6")

CODE_EXTENSIONS = (
    ".py",
    ".js",
    ".ts",
    ".tsx",
    ".jsx",
    ".go",
    ".java",
    ".rb",
    ".php",
    ".c",
    ".cpp",
    ".cs",
    ".rs",
    ".kt",
    ".swift",
)
MAX_PATCH_CHARS = 6000

SEVERITY_ICON = {"high": "🔴", "medium": "🟡", "low": "🔵"}
CATEGORY_LABEL = {a.category: a.label for a in ALL_AGENTS}

# Nhóm phát hiện sẽ CHẶN merge nếu có. Convention không nằm đây -> chỉ là góp ý.
# Có thể đổi qua biến môi trường, vd: REVIEW_BLOCKING_CATEGORIES="bug,security"
BLOCKING_CATEGORIES = set(
    os.getenv("REVIEW_BLOCKING_CATEGORIES", "bug,security,performance").split(",")
)

# Bật/tắt bước verify. Mặc định BẬT. Tắt bằng REVIEW_VERIFY=0 (hoặc false/no).
VERIFY_ENABLED = os.getenv("REVIEW_VERIFY", "1").lower() not in ("0", "false", "no", "")


def has_blocking(findings: list[dict]) -> bool:
    """True nếu có ít nhất một finding thuộc nhóm chặn merge."""
    return any(f.get("category") in BLOCKING_CATEGORIES for f in findings)


# ----------------------------------------------------------------------------
# Tiện ích diff
# ----------------------------------------------------------------------------


def parse_added_lines(patch: str) -> set[int]:
    """Tập số dòng (file mới) nằm trong diff — chỉ những dòng này comment inline được."""
    valid, new_line = set(), 0
    for line in patch.splitlines():
        m = re.match(r"@@ -\d+(?:,\d+)? \+(\d+)(?:,\d+)? @@", line)
        if m:
            new_line = int(m.group(1))
            continue
        if line.startswith("+"):
            valid.add(new_line)
            new_line += 1
        elif line.startswith("-"):
            continue
        else:
            new_line += 1
    return valid


# ----------------------------------------------------------------------------
# Chạy 4 agent song song
# ----------------------------------------------------------------------------


def review_file(client: Anthropic, filename: str, patch: str) -> list[dict]:
    findings = []
    with ThreadPoolExecutor(max_workers=len(ALL_AGENTS)) as pool:
        futures = [
            pool.submit(a.review, client, MODEL, filename, patch) for a in ALL_AGENTS
        ]
        for fut in futures:
            findings.extend(fut.result())
    return findings


# ----------------------------------------------------------------------------
# Tổng hợp & định dạng (chung cho cả 2 nền tảng)
# ----------------------------------------------------------------------------


def build_summary(all_findings: list[dict], verify_stats: dict | None = None) -> str:
    # Dòng ghi chú bước verify (nếu có chạy và có loại được cái nào).
    verify_note = ""
    if verify_stats and verify_stats.get("dropped", 0) > 0:
        verify_note = (
            f"🔍 Bước verify đã loại **{verify_stats['dropped']}** báo động giả "
            f"(còn lại {verify_stats['kept']}/{verify_stats['raw']})."
        )

    if not all_findings:
        body = (
            "## 🤖 AI Code Review\n\n"
            "✅ Cả 4 agent không phát hiện vấn đề đáng kể. **Cho phép merge.**"
        )
        if verify_note:
            body += f"\n\n{verify_note}"
        return body

    counts = {}
    for f in all_findings:
        counts[f["category"]] = counts.get(f["category"], 0) + 1

    # Phán quyết gate
    blocking = has_blocking(all_findings)
    block_labels = ", ".join(CATEGORY_LABEL.get(c, c) for c in BLOCKING_CATEGORIES)
    if blocking:
        verdict = (
            f"### ❌ CHẶN MERGE\n"
            f"Phát hiện vấn đề thuộc nhóm chặn ({block_labels}). "
            f"Cần xử lý trước khi merge."
        )
    else:
        verdict = (
            "### ✅ CHO PHÉP MERGE\n"
            "Chỉ có góp ý về coding convention — không bắt buộc, nên xem qua."
        )

    lines = [
        "## 🤖 Merge Checker",
        "",
        verdict,
        "",
        f"Tổng cộng **{len(all_findings)}** vấn đề:",
        "",
    ]
    if verify_note:
        lines += [verify_note, ""]
    for cat, label in CATEGORY_LABEL.items():
        if cat in counts:
            tag = " (chặn)" if cat in BLOCKING_CATEGORIES else ""
            lines.append(f"- {label}{tag}: {counts[cat]}")
    lines += ["", "Tổng hợp:", ""]
    for f in sorted(all_findings, key=lambda x: x.get("severity", "low")):
        icon = SEVERITY_ICON.get(f.get("severity"), "")
        label = CATEGORY_LABEL.get(f["category"], f["category"])
        lines.append(
            f"- {icon} `{f['file']}:{f.get('line', '?')}` **[{label}]** {f['comment']}"
        )
    footer = "_Được review bởi 4 checker"
    footer += " + 1 bước verify lọc false positive" if verify_stats else ""
    footer += ". AI có thể sai, checker có thể nhầm. Merge hay không là quyền năng của bro. Merge at your own risk._"
    lines += ["", footer]
    return "\n".join(lines)


def build_inline_comments(
    all_findings: list[dict], valid_lines: dict[str, set]
) -> list[dict]:
    """Trả về dạng CHUẨN HOÁ {file, line, body}; client tự đổi sang API của mình."""
    comments = []
    for f in all_findings:
        if f.get("line") in valid_lines.get(f["file"], set()):
            icon = SEVERITY_ICON.get(f.get("severity"), "")
            label = CATEGORY_LABEL.get(f["category"], f["category"])
            body = f"{icon} **[{label}]** {f['comment']}"
            if f.get("suggestion"):
                body += f"\n\n**Gợi ý:** {f['suggestion']}"
            comments.append({"file": f["file"], "line": f["line"], "body": body})
    return comments


# ----------------------------------------------------------------------------
# Chọn client theo nền tảng
# ----------------------------------------------------------------------------


def detect_platform(arg_platform: str | None) -> str:
    if arg_platform:
        return arg_platform
    if os.getenv("GITLAB_CI"):  # GitLab CI tự set biến này = "true"
        return "gitlab"
    return "github"  # mặc định


def build_client(platform: str, args):
    if platform == "github":
        repo = args.repo or os.getenv("GITHUB_REPOSITORY")
        pr = args.pr or int(os.getenv("PR_NUMBER", 0) or 0)
        if not repo or not pr:
            raise SystemExit(
                "GitHub: thiếu --repo / --pr (hoặc GITHUB_REPOSITORY / PR_NUMBER)."
            )
        return GitHubClient(os.getenv("GITHUB_TOKEN", ""), repo, pr)

    if platform == "gitlab":
        project = args.project or os.getenv("CI_PROJECT_ID")
        mr = args.mr or int(os.getenv("CI_MERGE_REQUEST_IID", 0) or 0)
        api_url = os.getenv("CI_API_V4_URL", "https://gitlab.com/api/v4")
        if not project or not mr:
            raise SystemExit(
                "GitLab: thiếu --project / --mr (hoặc CI_PROJECT_ID / CI_MERGE_REQUEST_IID)."
            )
        return GitLabClient(os.getenv("GITLAB_TOKEN", ""), project, mr, api_url)

    raise SystemExit(f"Nền tảng không hỗ trợ: {platform}")


# ----------------------------------------------------------------------------
# Main
# ----------------------------------------------------------------------------


def main():
    p = argparse.ArgumentParser(description="AI Code Review Agent  — GitHub & GitLab")
    p.add_argument(
        "--platform",
        choices=["github", "gitlab"],
        default=None,
        help="mặc định tự nhận từ môi trường CI",
    )
    # GitHub
    p.add_argument("--repo", default=None, help="GitHub: owner/repo")
    p.add_argument("--pr", type=int, default=0, help="GitHub: số PR")
    # GitLab
    p.add_argument("--project", default=None, help="GitLab: project id")
    p.add_argument("--mr", type=int, default=0, help="GitLab: MR iid")
    p.add_argument("--dry-run", action="store_true")
    # Cho phép tắt verify ngay trên dòng lệnh (ngoài biến môi trường REVIEW_VERIFY).
    p.add_argument(
        "--no-verify",
        action="store_true",
        help="bỏ qua bước verify lọc false positive",
    )
    args = p.parse_args()

    if not os.getenv("ANTHROPIC_API_KEY"):
        p.error("Chưa set ANTHROPIC_API_KEY.")

    verify_on = VERIFY_ENABLED and not args.no_verify

    platform = detect_platform(args.platform)
    client = build_client(platform, args)
    llm = Anthropic()
    verifier = Verifier()
    print(f"[*] Nền tảng: {platform} | verify: {'BẬT' if verify_on else 'TẮT'}")

    print("[1/5] Lấy file thay đổi ...")
    files = client.get_changed_files()
    code_files = [
        f
        for f in files
        if f.get("patch")
        and f["filename"].endswith(CODE_EXTENSIONS)
        and f.get("status") != "removed"
    ]
    print(f"      {len(code_files)}/{len(files)} file code cần review.")

    print(f"[2/5] Mỗi file chạy {len(ALL_AGENTS)} agent song song ...")
    # Lưu patch (đã cắt) theo file để bước verify dùng lại đúng đoạn diff agent đã thấy.
    patches: dict[str, str] = {}
    valid_lines: dict[str, set] = {}
    raw_by_file: dict[str, list[dict]] = {}
    for f in code_files:
        name = f["filename"]
        patch = f["patch"][:MAX_PATCH_CHARS]
        patches[name] = patch
        valid_lines[name] = parse_added_lines(patch)
        found = review_file(llm, name, patch)
        raw_by_file[name] = found
        print(f"      - {name}: {len(found)} phát hiện")

    raw_count = sum(len(v) for v in raw_by_file.values())

    print("[3/5] Verify (lọc false positive) ...")
    all_findings: list[dict] = []
    if verify_on:
        for name, found in raw_by_file.items():
            kept = verifier.verify(llm, MODEL, name, patches[name], found)
            dropped = len(found) - len(kept)
            if dropped:
                print(f"      - {name}: giữ {len(kept)}/{len(found)} (loại {dropped} false positive)")
            all_findings.extend(kept)
        kept_count = len(all_findings)
        print(
            f"      Verify xong: giữ {kept_count}/{raw_count}, "
            f"loại {raw_count - kept_count} báo động giả."
        )
    else:
        for found in raw_by_file.values():
            all_findings.extend(found)
        print("      (bỏ qua — verify đang TẮT)")

    verify_stats = (
        {"raw": raw_count, "kept": len(all_findings), "dropped": raw_count - len(all_findings)}
        if verify_on
        else None
    )

    print("[4/5] Tổng hợp ...")
    summary = build_summary(all_findings, verify_stats)
    inline = build_inline_comments(all_findings, valid_lines)
    blocking = has_blocking(all_findings)

    if args.dry_run:
        print("\n[5/5] (dry-run)\n")
        print(summary)
        print(f"\n--- {len(inline)} comment inline ---")
        for c in inline:
            print(f"  {c['file']}:{c['line']} -> {c['body'][:80]}")
    else:
        print("[5/5] Đăng review ...")
        client.post_review(summary, inline)
        print("      Đã đăng ✅")

    # ----- Merge gate -----
    # Comment LUÔN được đăng ở trên (để reviewer thấy mọi góp ý).
    # Sau đó job thoát theo phán quyết: có bug/security/performance -> exit 1
    # (job CI fail). Convention-only hoặc sạch -> exit 0 (job pass).
    # LƯU Ý: exit 1 chỉ làm "đỏ" check; muốn CHẶN merge thật phải bật
    # branch protection (GitHub) / "Pipelines must succeed" (GitLab). Xem README.
    if blocking:
        print("❌ Có lỗi thuộc nhóm chặn (bug/security/performance) -> chặn merge.")
        sys.exit(1)
    print("✅ Không có lỗi chặn -> cho phép merge.")
    sys.exit(0)


if __name__ == "__main__":
    main()
