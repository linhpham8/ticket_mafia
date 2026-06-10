"""
Tầng giao tiếp với nền tảng (GitHub / GitLab)
---------------------------------------------
Hai client có CÙNG interface để orchestrator dùng chung:
    - get_changed_files() -> list[dict] đã chuẩn hoá: {filename, patch, status}
    - post_review(summary, inline)      -> đăng comment tổng hợp + inline

Nhờ chuẩn hoá, phần 4 agent và phần orchestrator KHÔNG cần biết
đang chạy trên GitHub hay GitLab. Muốn thêm Bitbucket sau này = viết thêm 1 client.
"""

import requests


# ----------------------------------------------------------------------------
# GitHub
# ----------------------------------------------------------------------------

class GitHubClient:
    def __init__(self, token: str, repo: str, pr: int):
        self.repo = repo            # "owner/repo"
        self.pr = pr
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        })

    def _url(self, path: str) -> str:
        return f"https://api.github.com/repos/{self.repo}{path}"

    def get_changed_files(self) -> list[dict]:
        files, page = [], 1
        while True:
            r = self.session.get(self._url(f"/pulls/{self.pr}/files"),
                                 params={"per_page": 100, "page": page})
            r.raise_for_status()
            batch = r.json()
            for f in batch:
                files.append({
                    "filename": f["filename"],
                    "patch": f.get("patch", ""),
                    "status": f.get("status", ""),
                })
            if len(batch) < 100:
                break
            page += 1
        return files

    def _head_sha(self) -> str:
        r = self.session.get(self._url(f"/pulls/{self.pr}"))
        r.raise_for_status()
        return r.json()["head"]["sha"]

    def post_review(self, summary: str, inline: list[dict]):
        # inline (chuẩn hoá) -> định dạng GitHub: path/line/side
        comments = [{"path": c["file"], "line": c["line"], "side": "RIGHT", "body": c["body"]}
                    for c in inline]
        payload = {"commit_id": self._head_sha(), "body": summary,
                   "event": "COMMENT", "comments": comments}
        r = self.session.post(self._url(f"/pulls/{self.pr}/reviews"), json=payload)
        if r.status_code >= 400:
            print(f"[warn] GitHub inline lỗi ({r.status_code}); fallback comment tổng hợp.")
            self.session.post(self._url(f"/issues/{self.pr}/comments"),
                              json={"body": summary}).raise_for_status()
        else:
            r.raise_for_status()


# ----------------------------------------------------------------------------
# GitLab
# ----------------------------------------------------------------------------

class GitLabClient:
    def __init__(self, token: str, project_id: str, mr_iid: int,
                 api_url: str = "https://gitlab.com/api/v4"):
        self.api = api_url.rstrip("/")
        self.project = project_id   # số ID hoặc path đã URL-encode
        self.mr = mr_iid
        self.diff_refs = {}         # base/head/start sha — cần cho comment inline
        self.session = requests.Session()
        self.session.headers.update({"PRIVATE-TOKEN": token})

    def _url(self, path: str) -> str:
        return f"{self.api}/projects/{self.project}/merge_requests/{self.mr}{path}"

    def get_changed_files(self) -> list[dict]:
        r = self.session.get(self._url("/changes"))
        r.raise_for_status()
        data = r.json()
        # diff_refs cần để định vị comment inline (GitLab bắt buộc)
        self.diff_refs = data.get("diff_refs", {}) or {}
        files = []
        for ch in data.get("changes", []):
            files.append({
                "filename": ch["new_path"],
                "patch": ch.get("diff", ""),
                "status": "removed" if ch.get("deleted_file") else "modified",
            })
        return files

    def post_review(self, summary: str, inline: list[dict]):
        # 1) comment tổng hợp = một "note" thường
        self.session.post(self._url("/notes"),
                          json={"body": summary}).raise_for_status()
        # 2) mỗi inline = một "discussion" có position trỏ vào dòng
        refs = self.diff_refs
        for c in inline:
            position = {
                "position_type": "text",
                "base_sha": refs.get("base_sha"),
                "head_sha": refs.get("head_sha"),
                "start_sha": refs.get("start_sha"),
                "new_path": c["file"],
                "new_line": c["line"],
            }
            r = self.session.post(self._url("/discussions"),
                                  json={"body": c["body"], "position": position})
            if r.status_code >= 400:
                # Dòng nằm ngoài diff hoặc lỗi vị trí -> bỏ qua, không chặn các comment khác
                print(f"[warn] GitLab inline {c['file']}:{c['line']} lỗi ({r.status_code}).")
