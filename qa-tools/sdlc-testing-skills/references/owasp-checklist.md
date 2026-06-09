# OWASP Security Testing Checklist

> Skill 10 đọc file này để áp dụng vào security testing.
> Dựa trên OWASP Top 10 2021 + OWASP Testing Guide v4.2.
> Với mỗi hạng mục: xác định điểm kiểm tra, kỹ thuật, severity nếu phát hiện.

---

## OWASP Top 10 — 2021

### A01: Broken Access Control ⚠️ Phổ biến nhất

**Mô tả:** Người dùng có thể thực hiện hành động ngoài quyền hạn của mình.

**Kiểm tra:**
- [ ] Truy cập trực tiếp URL của resource thuộc user khác (IDOR — Insecure Direct Object Reference)
  - VD: `/api/orders/123` với order thuộc user khác → phải trả 403, không phải 200
- [ ] Thay đổi role/permission trong request (parameter tampering)
  - VD: gửi `role=admin` trong body hoặc query string
- [ ] Truy cập trang admin khi không có quyền
  - VD: đăng nhập user thường, truy cập `/admin`, `/dashboard/settings`
- [ ] Thực hiện hành động theo phương thức HTTP không được phép
  - VD: endpoint chỉ cho GET nhưng thử DELETE/PUT
- [ ] JWT token: thay đổi payload (user_id, role) mà không có signature hợp lệ
- [ ] CORS: kiểm tra response header khi gửi request từ origin khác

**Severity nếu phát hiện:** S1 (Critical)

---

### A02: Cryptographic Failures

**Mô tả:** Dữ liệu nhạy cảm không được mã hóa hoặc mã hóa yếu.

**Kiểm tra:**
- [ ] Dữ liệu nhạy cảm (password, token, PII) truyền qua HTTP (không phải HTTPS)
- [ ] Password lưu dạng plaintext hoặc MD5/SHA1 trong DB
  - Kiểm tra qua response API hoặc error message tiết lộ hash
- [ ] Token, API key xuất hiện trong URL (bị log vào server logs)
  - VD: `/reset-password?token=abc123` → token phải nằm trong body/header
- [ ] Cookie thiếu flag `Secure` và `HttpOnly`
  - Kiểm tra: DevTools → Application → Cookies
- [ ] Response API trả về dữ liệu nhạy cảm không cần thiết
  - VD: trả về `password_hash`, `ssn`, `card_number` đầy đủ trong response

**Severity nếu phát hiện:** S1 (Critical)

---

### A03: Injection

**Mô tả:** Dữ liệu độc hại được inject vào interpreter (SQL, OS, LDAP...).

**Kiểm tra — SQL Injection:**
- [ ] Nhập payload vào form/query parameter: `' OR '1'='1`, `'; DROP TABLE users--`
- [ ] Quan sát response: lỗi SQL xuất hiện? Dữ liệu không mong đợi trả về?
- [ ] Time-based SQLi: `'; WAITFOR DELAY '0:0:5'--` (SQL Server) / `'; SELECT SLEEP(5)--` (MySQL)

**Kiểm tra — XSS (Cross-Site Scripting):**
- [ ] Nhập vào form input: `<script>alert(document.cookie)</script>`
- [ ] Stored XSS: lưu payload, sau đó kiểm tra trang khác có render không
- [ ] Reflected XSS: payload trong URL parameter hiển thị trực tiếp trên trang

**Kiểm tra — Command Injection:**
- [ ] Nếu app có tính năng xử lý file/shell: thử `; ls -la`, `| cat /etc/passwd`

**Kiểm tra — Path Traversal:**
- [ ] Thử: `../../../etc/passwd`, `..%2F..%2Fetc%2Fpasswd`

**Severity nếu phát hiện:** S1 (Critical)

---

### A04: Insecure Design

**Mô tả:** Thiếu kiểm soát bảo mật ở cấp độ thiết kế.

**Kiểm tra:**
- [ ] Rate limiting: gửi request liên tục (>100 lần/phút) — có bị throttle không?
  - VD: brute force form đăng nhập, spam gửi OTP
- [ ] Chức năng "Quên mật khẩu": token có expire không? Token có thể đoán không?
- [ ] Logic nghiệp vụ: có thể đặt hàng với giá âm? Áp nhiều mã giảm giá cùng lúc?
- [ ] Workflow bỏ qua bước: có thể đến bước 3 mà không qua bước 1-2?

**Severity nếu phát hiện:** S2 (High) đến S1 (Critical) tùy impact

---

### A05: Security Misconfiguration

**Mô tả:** Cấu hình sai gây lộ thông tin hoặc mở rộng attack surface.

**Kiểm tra:**
- [ ] Default credentials còn hoạt động: `admin/admin`, `admin/password`, `root/root`
- [ ] Trang error trả về stack trace, tên thư viện, version, DB query
  - VD: nhập input gây lỗi, xem response body và headers
- [ ] HTTP security headers thiếu:
  - `X-Content-Type-Options: nosniff`
  - `X-Frame-Options: DENY`
  - `Content-Security-Policy`
  - `Strict-Transport-Security` (HSTS)
- [ ] Directory listing bật trên web server: truy cập `/uploads/`, `/assets/`
- [ ] Swagger/OpenAPI UI public trên môi trường production: `/swagger-ui`, `/api-docs`
- [ ] Debug mode bật trên production: `DEBUG=True`, `APP_ENV=development`

**Severity nếu phát hiện:** S2–S3

---

### A06: Vulnerable and Outdated Components

**Mô tả:** Thư viện, framework có lỗ hổng đã biết.

**Kiểm tra:**
- [ ] Kiểm tra version trong response header: `X-Powered-By: Express 3.x`, `Server: Apache/2.2`
- [ ] Tìm CVE cho version đang dùng: https://nvd.nist.gov
- [ ] JavaScript libraries: kiểm tra version trong HTML source hoặc `package.json`
- [ ] Báo cáo với Dev nếu phát hiện dependency có CVE score ≥ 7.0

**Severity nếu phát hiện:** S2–S3 (tùy CVE score)

---

### A07: Identification and Authentication Failures

**Mô tả:** Xác thực yếu, quản lý session không an toàn.

**Kiểm tra:**
- [ ] Brute force: thử nhiều password liên tiếp — có bị khóa sau N lần không?
- [ ] Session ID: sau khi đăng xuất, session cũ còn hoạt động không?
  - Lấy cookie trước khi logout, dùng cookie đó gọi API sau khi logout
- [ ] JWT: thử algorithm `none` — gửi token không có signature
- [ ] Thay đổi session ID trong cookie — có reject không?
- [ ] "Remember me": token lưu bao lâu? Có thể revoke không?
- [ ] Chức năng đổi mật khẩu: có yêu cầu nhập mật khẩu cũ không?

**Severity nếu phát hiện:** S1–S2

---

### A08: Software and Data Integrity Failures

**Mô tả:** Code và infrastructure không xác minh tính toàn vẹn.

**Kiểm tra:**
- [ ] Deserialization: nếu app nhận dữ liệu serialized (JSON, XML, binary) — có validate không?
- [ ] File upload: có kiểm tra MIME type thực sự không (không chỉ extension)?
  - Thử đổi tên `malware.exe` thành `image.jpg` và upload
- [ ] Webhook/callback: có xác thực signature của request từ bên thứ ba không?

**Severity nếu phát hiện:** S1–S2

---

### A09: Security Logging and Monitoring Failures

**Mô tả:** Không log sự kiện bảo mật, không phát hiện tấn công.

**Kiểm tra:**
- [ ] Đăng nhập sai nhiều lần: có được log không? (kiểm tra qua admin dashboard hoặc hỏi Dev)
- [ ] Hành động nhạy cảm (xóa tài khoản, đổi quyền, export data) có audit log không?
- [ ] Log có chứa dữ liệu nhạy cảm (password, token) không? (kiểm tra log nếu được cấp quyền)

**Severity nếu phát hiện:** S3 (Medium)

---

### A10: Server-Side Request Forgery (SSRF)

**Mô tả:** App gửi request đến URL do attacker kiểm soát.

**Kiểm tra:**
- [ ] Tính năng fetch URL từ user input (import từ URL, webhook URL, avatar URL): thử URL nội bộ
  - Payload: `http://169.254.169.254/latest/meta-data/` (AWS metadata)
  - Payload: `http://localhost:8080/admin`
  - Payload: `http://192.168.1.1`
- [ ] Quan sát response: có trả về dữ liệu từ server nội bộ không?

**Severity nếu phát hiện:** S1 (Critical)

---

## Checklist Bổ Sung — Theo Loại Tính Năng

### Tính năng Auth / Login
- [ ] A01: IDOR sau đăng nhập
- [ ] A02: Cookie flags (Secure, HttpOnly, SameSite)
- [ ] A03: XSS trong form login
- [ ] A07: Brute force, session fixation, session invalidation khi logout

### Tính năng Payment / Fintech
- [ ] A02: Card number, CVV không lộ trong log/response
- [ ] A04: Thao túng giá tiền trong request body
- [ ] A08: Signature verification của payment webhook
- [ ] A01: Không truy cập transaction của người khác

### Tính năng Upload File
- [ ] A03: Tên file có chứa path traversal không (`../../../etc/passwd`)
- [ ] A08: MIME type thực sự, không chỉ extension
- [ ] A05: Giới hạn kích thước file (DoS prevention)

### API Endpoints
- [ ] A01: Authentication required trên mọi endpoint cần bảo vệ
- [ ] A05: Không expose thông tin nhạy cảm trong error response
- [ ] A04: Rate limiting trên endpoint quan trọng

---

## Severity Mặc Định Theo Loại Lỗ Hổng

| Lỗ hổng | Severity mặc định | Ghi chú |
|---|---|---|
| SQL Injection | S1 | Có thể dump toàn bộ DB |
| XSS Stored | S1 | Ảnh hưởng nhiều user |
| XSS Reflected | S2 | Cần social engineering |
| IDOR | S1 hoặc S2 | Tùy sensitivity của data |
| Broken Auth | S1 | Nếu bypass toàn bộ auth |
| SSRF internal | S1 | Nếu reach được metadata/nội bộ |
| Missing security headers | S3 | |
| Information disclosure (stack trace) | S2 | |
| Weak session management | S2 | |
| Missing rate limiting | S3 | |
