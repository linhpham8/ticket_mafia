# Detailed Procedure: 01-security-testing

> Token-saving archive of the previous full sub-skill body. Read only when the compact sub-skill needs exact legacy wording, templates, or edge-case procedures.

## Kiem tra truoc khi bao DONE

> **L2 - QA Lead review bat buoc.** Report chua duoc gui stakeholder cho den khi nhan Approved. Xem muc Sign-off cuoi file.

- [ ] Da cover scope OWASP Top 10 theo qa-config (hoac scope da xac nhan)
- [ ] Moi S1/S2 bug co repro steps day du
- [ ] Khuyen nghi remediation cu the, khong chung chung
- [ ] Sign-off L2 da emit
- [ ] Append execution record vao governance/audit-log.md
- [ ] Cap nhat project/session-state.yaml -> last_execution, pending_sign_offs

---







## Đầu vào

| Thông tin | Bắt buộc |
|---|---|
| URL môi trường test (staging, không dùng production) | ✅ |
| Danh sách tính năng / luồng cần kiểm tra bảo mật | ✅ |
| Tài khoản test có nhiều role khác nhau (admin, user thường, guest) | ✅ |
| Thông tin domain: loại app (web, API, mobile API) | Khuyến nghị |
| qa-config.yaml (nếu có cấu hình security scope) | Khuyến nghị |

> **Cảnh báo:** Chỉ thực hiện trên môi trường được cấp phép. Không test trên production nếu không có approval rõ ràng.

Nếu project có `qa-config.yaml` → đọc trước:
- `environments.staging.url` → URL test
- `test_accounts` → roles cần thiết (admin, user, guest)
- `security.focus` → danh sách OWASP category ưu tiên (nếu trống → test toàn bộ A01–A10)

Thiếu thông tin bắt buộc → ghi `[Cần bổ sung]`, hỏi lại. Không đoán mò.

---

## Bước 1 — Xác định scope và loại tính năng

Phân loại tính năng để áp dụng checklist phù hợp từ `../../references/owasp-checklist.md`:

| Loại tính năng | Checklist ưu tiên |
|---|---|
| Auth / Login / Session | A01, A02, A07 |
| Form nhập liệu, tìm kiếm | A03 (Injection, XSS) |
| Upload file | A03, A08 |
| API endpoint | A01, A04, A05 |
| Payment / Fintech | A02, A04, A08 |
| Tính năng fetch URL từ input | A10 (SSRF) |

---

## Bước 2 — Thực hiện kiểm tra OWASP Top 10

Đọc `../../references/owasp-checklist.md` để lấy payload và kỹ thuật kiểm tra chi tiết.

Thực hiện theo thứ tự ưu tiên (S1 trước):

### A01 — Broken Access Control (ưu tiên cao nhất)

- [ ] IDOR: truy cập resource của user khác qua ID manipulation
- [ ] Privilege escalation: thêm `role=admin` vào request
- [ ] Truy cập trang admin/restricted khi chưa có quyền
- [ ] HTTP method tampering: thử DELETE/PUT trên endpoint chỉ cho GET
- [ ] JWT payload manipulation (thay user_id, role)

### A02 — Cryptographic Failures

- [ ] Kiểm tra HTTPS enforcement (redirect từ HTTP)
- [ ] Cookie flags: `Secure`, `HttpOnly`, `SameSite`
- [ ] Token, API key không xuất hiện trong URL
- [ ] Response API không trả về data nhạy cảm thừa (password_hash, ssn, card đầy đủ)

### A03 — Injection

- [ ] SQL Injection: `' OR '1'='1`, quan sát lỗi SQL trong response
- [ ] XSS Reflected: `<script>alert(1)</script>` trong URL params
- [ ] XSS Stored: lưu payload, kiểm tra trang render lại
- [ ] Path Traversal: `../../../etc/passwd` trong file-related endpoint

### A04 — Insecure Design

- [ ] Rate limiting: gửi >100 request/phút lên form login, OTP
- [ ] Password reset token: có expire không? Có thể đoán không?
- [ ] Business logic: đặt hàng giá âm, bỏ qua bước trong workflow

### A05 — Security Misconfiguration

- [ ] Default credentials: `admin/admin`, `admin/password`
- [ ] Error response tiết lộ stack trace, tên thư viện, version
- [ ] HTTP security headers (kiểm tra response headers)
- [ ] Swagger/API docs public trên staging/prod

### A06 — Vulnerable and Outdated Components

- [ ] Kiểm tra header `Server`, `X-Powered-By` — có tiết lộ version framework/server không?
- [ ] Swagger UI / API docs có liệt kê version thư viện không?
- [ ] Kiểm tra package versions công khai (nếu có file `package.json`, `pom.xml` expose) — so sánh với CVE known vulnerabilities
- [ ] Third-party scripts (CDN) có pinned version không, hay dùng `latest`?

### A07 — Authentication Failures

- [ ] Brute force: thử nhiều password liên tiếp, có bị khóa không?
- [ ] Session invalidation sau logout (dùng cookie cũ gọi API)
- [ ] JWT algorithm `none`: gửi token không có signature
- [ ] Đổi mật khẩu không yêu cầu mật khẩu cũ

### A08 — Integrity Failures

- [ ] File upload: đổi tên file `.exe` thành `.jpg`, upload thử
- [ ] MIME type thực sự được kiểm tra (không chỉ dựa extension)

### A09 — Security Logging and Monitoring Failures

- [ ] Thực hiện một hành động fail (login sai, truy cập trái phép) — hệ thống có log event này không?
- [ ] Log có chứa thông tin nhạy cảm không? (password, token, PII trong log line)
- [ ] Có alert / notification khi phát hiện nhiều lần đăng nhập sai liên tiếp không?
- [ ] Response lỗi không tiết lộ internal path, stack trace, hoặc SQL query

### A10 — SSRF

- [ ] Tính năng fetch URL từ input: thử `http://localhost`, `http://169.254.169.254/`

---

## Bước 3 — Ghi nhận và phân loại lỗ hổng

Với mỗi lỗ hổng phát hiện, ghi nhận đầy đủ:

| Trường | Nội dung |
|---|---|
| ID | SEC-001, SEC-002... |
| OWASP category | A01–A10 |
| Severity | S1/S2/S3 (xem bảng severity trong owasp-checklist.md) |
| Mô tả | Expected vs Actual |
| Repro steps | Đủ để Dev reproduce độc lập |
| Payload sử dụng | (nếu là injection/XSS) |
| Evidence | Screenshot / response body |
| Khuyến nghị fix | Cụ thể, không chung chung |

> **Lưu ý:** Không bao giờ ghi payload thực sự vào bug tracker public. Dùng kênh bảo mật nội bộ cho S1/S2.

---

## Bước 4 — Kiểm tra HTTP Security Headers

Với mọi response, kiểm tra headers sau:

| Header | Giá trị mong đợi | Thiếu → Severity |
|---|---|---|
| `Strict-Transport-Security` | `max-age=31536000; includeSubDomains` | S2 |
| `X-Content-Type-Options` | `nosniff` | S3 |
| `X-Frame-Options` | `DENY` hoặc `SAMEORIGIN` | S3 |
| `Content-Security-Policy` | Có giá trị hợp lệ | S2 |
| `Referrer-Policy` | `no-referrer` hoặc `same-origin` | S3 |
| `Permissions-Policy` | Hạn chế camera, microphone nếu không cần | S3 |

---

## Format output — Security Test Report

```markdown




| Trường | Giá trị |
|---|---|
| **Ngày test** | [dd/mm/yyyy] |
| **Môi trường** | [URL staging] |
| **Scope** | [Danh sách tính năng đã test] |
| **Tài khoản test** | [Roles đã dùng] |
| **Tester** | [Tên] |

---

## Tổng quan

| Severity | Số lượng |
|---|---:|
| S1 — Critical | [N] |
| S2 — High | [N] |
| S3 — Medium | [N] |
| **Tổng** | **[N]** |

**Mức độ rủi ro tổng thể:** 🔴 Cao / 🟡 Trung bình / 🟢 Thấp

---

## Danh sách lỗ hổng

### SEC-001: [Tiêu đề ngắn gọn]

| Trường | Giá trị |
|---|---|
| **OWASP** | A0X — [Tên category] |
| **Severity** | S1 / S2 / S3 |
| **Endpoint** | [URL / endpoint] |
| **Trạng thái** | Open / Fixed / Accepted Risk |

**Mô tả:** [Expected vs Actual — không paste payload nguy hiểm trực tiếp]

**Repro Steps:**
1. [Bước 1]
2. [Bước 2]
3. **Quan sát:** [Kết quả]

**Khuyến nghị:** [Giải pháp cụ thể — parameterized query / input validation / header config]

---

## HTTP Security Headers

| Header | Hiện tại | Đạt? |
|---|---|---|
| HSTS | [giá trị hoặc Thiếu] | ✅ / ❌ |
| X-Content-Type-Options | [giá trị hoặc Thiếu] | ✅ / ❌ |
| X-Frame-Options | [giá trị hoặc Thiếu] | ✅ / ❌ |
| CSP | [giá trị hoặc Thiếu] | ✅ / ❌ |

---

## Kết luận & Khuyến nghị

**Có thể release không?**
- ❌ Không — Còn [N] lỗ hổng S1 chưa fix
- ⚠️ Có điều kiện — S1 đã fix, còn [N] S2/S3 cần theo dõi
- ✅ Có — Không có lỗ hổng nghiêm trọng

**Top 3 hành động ưu tiên:**
1. [Hành động cụ thể]
2. [Hành động cụ thể]
3. [Hành động cụ thể]
```

---

**Lưu file vào:** `output_paths.reports.security` từ qa-config (default: `testing-output/reports/security/`)
→ `reports/security-report-{project.sprint}.md`

## Sign-off Request (L2)



Sau khi nhan Approved: cap nhat project/session-state.yaml, xoa item khoi pending_sign_offs.

---

## Completion Status

- **DONE** — Đã kiểm tra toàn bộ scope, report đầy đủ, mọi S1 đã có repro steps
- **DONE_WITH_CONCERNS** — Hoàn thành nhưng: {Còn S1 open / Một số endpoint không test được / Thiếu tài khoản role X}
- **BLOCKED** — Không thể test do: {Không có tài khoản test / Môi trường không ổn định / Chưa được cấp phép}
- **NEEDS_CONTEXT** — Cần bổ sung: {URL môi trường / Danh sách tính năng cần test / Tài khoản đa role}


