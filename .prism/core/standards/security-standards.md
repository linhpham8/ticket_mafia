# Security Standards

> Tiêu chuẩn bảo mật bắt buộc áp dụng cho mọi hệ thống.
> AI đọc file này khi: thiết kế security architecture, định nghĩa auth/authz, xử lý PII, thiết kế mobile security.

---

## 1. Identity & Access Management

### 1.1 IAM Platform
- **Bắt buộc dùng Central IAM**: AuthOM, One Mount Key Cloak
- Không tự build authentication system

### 1.2 Tài khoản
- Mọi user được gán **unique ID** trước khi truy cập hệ thống
- Tài khoản mặc định của vendor: thay đổi password mặc định hoặc disable nếu không dùng
- Thu hồi quyền truy cập **ngay lập tức** khi user chấm dứt
- Tài khoản inactive **>90 ngày** → disable hoặc xóa
- Session không hoạt động **>15 phút** → yêu cầu xác thực lại

### 1.3 Xác thực (Authentication)
- **Hệ thống quan trọng / admin**: bắt buộc **MFA**
- **External users / khách hàng**: dùng **Passwordless / SSO** (OIDC / SAML) — **không dùng username-password**
- **Backend-to-backend (M2M)**: dùng M2M auth của AuthOM
- Ngăn chặn brute-force: có cơ chế block sau nhiều lần xác thực sai
- Password (nếu bắt buộc phải dùng): tối thiểu 12 ký tự, chứa cả số và chữ

### 1.4 Phân quyền (Authorization)
- Mô hình: **RBAC / ABAC**
- **Bắt buộc có Permission Matrix** — được review và phê duyệt bởi Security + PO + TO (hoặc Security + PO)
- **Least Privilege**: mặc định từ chối tất cả (deny-all), chỉ mở quyền cần thiết
- Permission matrix phải được re-review khi có thay đổi lớn về feature

---

## 2. Data Security

### 2.1 Secret Management

**Production / Runtime secrets** (risk cao) → **BẮT BUỘC** lưu tại:
- **Hashicorp Vault** (khuyến nghị — đặc biệt khi multi-cloud-ready hoặc cần PKI engine)
- **Google Secret Manager** (khi infra là GCP và cost là ưu tiên)

Không bao giờ hardcode secrets trong source code.

**CI/CD secrets ngắn hạn** → secret store của CI platform đang dùng (vd GitLab CI/CD variables, GitHub Actions secrets), giới hạn scope tối thiểu:
- Credentials môi trường dev/staging
- Docker registry token, deploy token, SonarQube token, notification webhooks
- Build secrets (NPM/Maven/PyPI registry token)

### 2.2 Encryption

**At Rest:**
- Thuật toán: **AES-256+** / RSA-4096+ / ECC-384+; Hash: **SHA-256+** / SHA-3 / HMAC-SHA2+
- Dữ liệu nhạy cảm và tài khoản user phải được mã hóa
- **Password**: dùng hàm băm mạnh có SALT (bcrypt / Argon2)
- **PII** phải được mã hóa: CMND/CCCD/Hộ chiếu, số tài khoản ngân hàng, thông tin sinh trắc học, health/financial data
- **Cardholder data**: masking từ tầng Database; **không lưu** CAV2/CID/CVV2/PIN sau giao dịch hoàn tất

**In Transit:**
- **TLS ≥1.3** bắt buộc cho mọi kết nối
- Nâng cao (cho hệ thống quan trọng): mã hóa payload end-to-end over TLS 1.3

**In Use:**
- PII và dữ liệu nhạy cảm trên UI: **masking** và tuân theo phân quyền tối thiểu
- PAN: chỉ hiển thị BIN và 4 số cuối (trừ user có nhu cầu kinh doanh hợp pháp được xác nhận)
- Masking có thể thực hiện từ tầng Database hoặc backend

---

## 3. Compliance Requirements

- **Security Testing ticket** phải được tạo trước golive — tối thiểu 3 ngày làm việc trước golive (để Security đọc đề bài, test, và có thời gian fix + repentest)
- **Vulnerability classification**: dùng **CVSS 3.1**
  - High+ → fix trước khi release
  - Medium và thấp hơn → cần plan xử lý
- **Key generation**: do Security team tạo, Secret Manager lưu, team phát triển chỉ dùng connection reference — không tự tạo và tự lưu
- **Prod/Non-prod isolation**: môi trường production và non-production phải tách biệt; dữ liệu test không được chứa dữ liệu prod
- **Audit log**: immutable (không được sửa/xóa); queryable trong 6 tháng; lưu trữ ít nhất 12 tháng; **không chứa PII, password, token**
- **Threat Modeling**: bắt buộc cho mọi dự án — dùng phương pháp **STRIDE**; phải được ANBM review và phê duyệt
- **Risk assessment**: mọi hệ thống phải có risk assessment toàn diện
- **PII xuyên biên giới**: cần báo cáo đánh giá tác động trước khi transfer

---

## 4. Security Monitoring

**Event log bắt buộc ghi** (When/Where/Who/What):
- User ID
- Loại sự kiện
- Ngày, giờ
- Kết quả (thành công / thất bại)
- Nguồn gốc sự kiện
- Resource bị ảnh hưởng (tên, giao thức)

Yêu cầu:
- **Traceability end-to-end**
- **Admin accounts** phải được giám sát và log chi tiết
- Log mọi lần truy cập không hợp lệ
- Log mọi thay đổi credentials/authentication (tạo tài khoản, nâng quyền, thay đổi admin accounts)
- Log tạo/xóa system-level objects

---

## 5. Integration Security

**Bắt buộc:**
- Whitelist IP cho mọi tích hợp
- Xác thực (authentication) rõ ràng — không anonymous

**Nâng cao (host-to-host standard):**
- Kết nối qua mạng riêng **IPsec VPN**
- HTTP → **HTTPS**; File transfer → **SFTP**
- **mTLS** cho service-to-service
- Thuật toán trao đổi khóa: DH-RSA/RSA hoặc ECDHE/ECDSA
- Mã hóa dữ liệu: AES GCM hoặc AES CCM, key length 256 bit
- Digital Certificate phía client: phải ký bởi trusted CA, còn hạn
- Mã hóa trường nhạy cảm: `cipherData = Base64Encode(RSA(rawData, publicKey))`

---

## 6. Security Controls Infrastructure

- **Code repos**: bắt buộc tích hợp **SAST/SCA**
- **APIs và web apps**: bắt buộc bọc qua **Cloudflare**
- **VMs / K8s pods**: phải cài **Agent Security**
- **Workload ra internet**: phải đi qua **Prisma**
- **GenAI / AI Agent solutions**: phải đi qua **Onemount Guardrail AI**

---

## 7. Mobile Application Security

### 7.1 Principles (luôn áp dụng)

- **Không hardcode** secrets, keys, credentials trong mobile app — có thể dịch ngược
- **Obfuscation**: bắt buộc cho production build
- **System Trusted Certificates**: dùng Network Security Config (Android) và NSAppTransportSecurity (iOS) — không chấp nhận User-Installed Certificates
- **Secure storage**: chỉ lưu key/private key tại system keychain / keystore — không lưu ở thư mục mặc định của user
- **Log policy**: không log password, token, PII, biometrics — mọi thông tin nhạy cảm phải mask trước khi log

### 7.2 Anti-Tampering Suite (bắt buộc cho production build — tất cả phải được kích hoạt cùng nhau)

| Control | Mô tả |
|---------|-------|
| Obfuscation | Làm rối code sau khi build |
| Anti-root / Anti-jailbreak | Phát hiện thiết bị bị root/jailbreak → ngắt kết nối và thông báo user |
| Anti-tamper | Phát hiện app bị chỉnh sửa |
| Anti-emulator | Phát hiện chạy trên môi trường giả lập |
| Anti-repackage | Ngăn chặn đóng gói lại app |
| Anti-hooking | Phát hiện và ngăn chặn hooking vào runtime |
| Anti-debug | Tự động thoát khi có trình gỡ lỗi; production build không ký debug cert; `android:debuggable="false"` |

> Các controls này phải hoạt động cùng nhau để bảo vệ lẫn nhau.

### 7.3 Authentication & Session

- Xác thực **OTP** khi user thêm/sửa PIN / Fingerprint / Face ID
- Khi user kích hoạt app trên thiết bị mới → bắt buộc cập nhật lên phiên bản mới nhất
- **Không downgrade** xuống phiên bản thấp hơn
- WebViews phải cấu hình an toàn — ngăn rò rỉ qua JavaScript bridge

### 7.4 Password & Biometric (Nâng cao — cho ứng dụng tài chính)

- App **không được ghi nhớ password**, trừ khi dùng biometric auth (sau khi user đồng ý và đã có ít nhất 1 giao dịch thành công)
- Thời gian xác thực biometric tối đa: 2 phút
- **PAD (Presentation Attack Detection)** solution phải đạt tiêu chuẩn **ISO 30107 cấp độ 2** — từ chối: ảnh in, ảnh màn hình, video quay sẵn, deepfake offline/realtime, mặt nạ 2D/3D, vân tay giả, điều kiện ánh sáng xấu

> AI hỏi user: ứng dụng có thuộc loại "financial app" cần PAD không? Có cần biometric ghi nhớ không?
