# IoT Standards (Optional — Chỉ áp dụng cho IoT Projects)

> **Lưu ý:** File này chỉ được đọc khi project có IoT component.
> AI chỉ load file này khi user xác nhận có yêu cầu IoT.

---

## 1. Message & Streaming Protocols

| Protocol | Khi nào dùng | Quy tắc |
|----------|-------------|---------|
| **Apache Kafka** | Telemetry pipeline, event-driven architecture, service integration | Không publish message ≥1MB; retry mechanism bắt buộc |
| **MQTT / RabbitMQ** | Device-to-cloud messaging | Không dùng wildcard `#` cho publish; QoS 1 cho telemetry thường, QoS 2 cho command quan trọng |

---

## 2. Device Communication Protocols

| Thiết bị | Protocol |
|----------|----------|
| Sensor & IoT nodes | MQTT over TLS |
| Gateway | MQTT + HTTP |
| Thiết bị công nghiệp | Modbus TCP / OPC-UA (qua Gateway) |
| Camera | RTSP + ONVIF |

**Security requirements cho mọi kết nối:**
- TLS bắt buộc
- Xác thực riêng biệt cho từng thiết bị (unique per-device credentials)
- Không cho phép kết nối Anonymous

**Payload data format:**
- JSON, encoding UTF-8, có timestamp UTC
- Key naming: `snake_case`

---

## 3. Database Standards (IoT)

| Loại dữ liệu | Database | Yêu cầu |
|-------------|----------|---------|
| **Dữ liệu thời gian (telemetry)** | TimescaleDB hoặc tương đương | Bắt buộc hypertable; bật compression cho data ≥7 ngày; retention mặc định 12 tháng |
| **Core business data** | PostgreSQL | Primary key + foreign key đầy đủ; index cho columns query nhiều (≥1M bản ghi) |
| **Dữ liệu phi cấu trúc (metadata)** | MongoDB (flexible) hoặc Cassandra/tương đương (distributed scale >10M records/ngày) | Bắt buộc có tài liệu schema design trước khi implement |

> Đây là catalog mở rộng theo domain IoT của `coding-standards-backend.md` §4.2 (general catalog: Redis / PostgreSQL / MongoDB). IoT bổ sung TimescaleDB (telemetry time-series) và Cassandra (distributed scale lớn) cho khối lượng đặc thù IoT — không mâu thuẫn §4.2 mà là phần thêm theo workload.

---

## 4. Caching (IoT)

- Framework: **Redis** cho session, device state cache, token cache & metadata thường xuyên truy cập
- **Không** dùng Redis thay cho database chính
- **TTL bắt buộc** cho mọi key runtime (config đặc biệt phải khai báo trước)
- Max value size: **512 KB**

---

## 5. Logging & Monitoring (IoT)

> Baseline: tuân theo structured-logging của `devsecops-standards.md` §2.1 (JSON + context bắt buộc: `request_id` / `trace_id`, user ID, service name, operation). Mục dưới là phần delta riêng cho IoT, không thay thế baseline đó.

- Format: **JSON** cho mọi log entry (kèm đủ context field theo devsecops §2.1)
- Log levels: INFO / WARN / ERROR
- **Tuyệt đối không log**: password, token, secret key, **thông tin biometrics** (delta riêng IoT, ngoài danh sách PII chung của devsecops)
- **Không hardcode** secret trong code — dùng environment variable hoặc secret manager

---

## 6. IoT Security

### 6.1 Device Authentication & Credentials
- Password thiết bị phải là duy nhất cho mỗi thiết bị (không default chung)
- Password mặc định từ nhà sản xuất phải được tạo bởi cơ chế có kháng tấn công tự động
- Có cơ chế ngăn chặn brute-force qua giao diện mạng
- Cho phép user/admin thay đổi credentials dễ dàng

### 6.2 Firmware & Updates
- Thiết bị phải có cơ chế cập nhật phần mềm an toàn và dễ dùng
- Bản cập nhật phải sử dụng mã mật an toàn và xác thực tính toàn vẹn
- Nhà sản xuất phải cung cấp bản cập nhật bảo mật kịp thời và công bố thời hạn hỗ trợ

### 6.3 Network & Communication
- Không hardcode sensitive parameters trong firmware
- Disable mọi network interface và logic không sử dụng
- Hỗ trợ khôi phục khi mất kết nối (offline operation)
- Validate mọi input từ API và giao diện người dùng
- Thiết bị phải có cơ chế factory reset và xóa dữ liệu user

### 6.4 Vendor Requirements
- Nhà sản xuất phải công bố vulnerability disclosure policy
- Có kênh tiếp nhận báo cáo lỗ hổng và timeline phản hồi rõ ràng

### 6.5 Data Privacy
- Dữ liệu cá nhân nhạy cảm trao đổi giữa device và service phải được mã hóa
- Có cơ chế xin consent và thu hồi consent của người dùng
- Telemetry data phải mô tả đầy đủ mục đích, đối tượng thu thập, nơi lưu trữ
- Hỗ trợ lưu trữ dữ liệu tại Việt Nam (khi cần)
