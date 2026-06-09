# Architecture Principles

> Nguyên tắc nền tảng dẫn dắt mọi quyết định thiết kế kiến trúc.
> AI đọc file này khi cần định hướng lựa chọn kiến trúc, evaluate trade-offs, hoặc viết ADR.

---

## 1. Business-Driven Architecture

Mục tiêu kinh doanh dẫn dắt quyết định công nghệ, không phải ngược lại.

- Mỗi hệ thống phải thể hiện rõ: business outcome cụ thể là gì, KPI nào đo thành công, owner phía business là ai
- Quyết định kỹ thuật cần giải thích được giá trị kinh doanh đem lại
- Tránh over-engineering vì lý do kỹ thuật thuần túy

## 2. Modular & Loosely Coupled

Mô-đun hóa để tăng tính linh hoạt, khả năng mở rộng và tái sử dụng.

- Ưu tiên kiến trúc mô-đun: Modular Monolith → Service-based → Microservices (theo thứ tự phức tạp tăng dần)
- Tránh hard dependencies giữa các module/service
- **Tuyệt đối không** chia sẻ database trực tiếp giữa các service/bounded context khác nhau
- Mỗi module/service chỉ giao tiếp qua interface được định nghĩa rõ ràng (API, event, contract)

## 3. Cloud / Hybrid First — Multi-Cloud-Ready

- Ưu tiên thiết kế Multi-Cloud-Ready: tránh vendor lock-in, dùng chuẩn mở
- Có thể chọn GCP-specific khi hệ thống không có kế hoạch mở rộng ra đối tác/thị trường ngoài
- On-prem hoặc Private Cloud chỉ khi có yêu cầu bắt buộc về data sovereignty hoặc tuân thủ pháp luật
- Cloud-native approach: container, auto-scaling, managed services khi phù hợp

## 4. API & Event First

Mọi tích hợp giữa hệ thống đi qua API hoặc Event — không có kết nối tùy tiện.

- Giao tiếp đồng bộ (synchronous): REST API (mặc định) hoặc gRPC (khi cần hiệu năng cao)
- Giao tiếp bất đồng bộ (asynchronous): Event/Stream (Kafka là chuẩn)
- **Hạn chế tối đa** tích hợp point-to-point khó kiểm soát
- Event là immutable sau khi phát

## 5. Security & Privacy by Design

Bảo mật được thiết kế từ đầu, không phải thêm vào sau.

- **Zero Trust**: không implicit trust giữa bất kỳ 2 thành phần nào — luôn authenticate + authorize rõ ràng
- **Least Privilege**: mỗi component/user chỉ có quyền tối thiểu cần thiết
- PII và dữ liệu nhạy cảm được bảo vệ từ thiết kế database, API, đến UI
- Threat modeling (STRIDE) bắt buộc cho mọi hệ thống trước khi golive

## 6. AI-Ready & Data-Centric

Dữ liệu là tài sản lõi — thiết kế để có thể khai thác được.

- Đảm bảo data consistency, data quality từ thiết kế ban đầu — không để data silos
- Single Source of Truth: mỗi entity được sở hữu bởi đúng một context
- Thiết kế data model hỗ trợ tích hợp AI/ML trong tương lai: sạch, tagged, có lineage
- Sẵn sàng cho ML models, Agentic AI và Automation ở lớp AI/Automation Layer

## 7. Cost Tracking & Optimization

Chi phí là constraint thiết kế, không chỉ là concern của Finance.

- Nhận thức rõ quan hệ giữa thiết kế kỹ thuật và chi phí vận hành
- Right-sizing: không over-provision, không under-provision
- Tài nguyên phải được tagged theo cost center/business unit để theo dõi được
- ROI phải đo được — thiết kế hỗ trợ tracking và cải tiến liên tục
