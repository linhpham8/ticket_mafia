---
status: APPROVED
version: v1
sprint: 1
phase: design
sprint_id: sprint-v1
created: 2026-06-08
updated: 2026-06-08 05:24
approved_by: user
approved_at: 2026-06-08T05:24:02Z
applied_to_living: true 8225310878e8569297961fcc0ec8090f2034566d (sealed 2026-06-08 22:21)
---

# Design System Proposal — Sprint v1

## New

<!-- ID: DESIGN-OVERVIEW-001 -->
### Design Overview

#### 1. Design Principles & Brand Guidelines

Industry vertical = ticketing / football ticket sales. The v1 design applies a mobile-first ticketing UX with Material-inspired interaction patterns, shared visual language across mobile app, user web, and admin web, and no dark mode/offline mode for demo.

| Element | Value | Notes |
|---|---|---|
| Primary Color | `#0F766E` | Teal: active, primary CTA, selected seats |
| Secondary Color | `#1F2937` | Neutral slate for headers and admin navigation |
| Accent Color | `#F59E0B` | Amber: pending confirmation, countdown |
| Error Color | `#DC2626` | Red: expired/rejected/error states |
| Success Color | `#16A34A` | Green: issued/scanned success |
| Typography | Inter / system sans-serif | Same family across web/mobile |
| Shape | 8px radius | Material-style surfaces without heavy decoration |
| Spacing | 4px base unit | 8/12/16/24/32 scale |
| Accessibility | Demo baseline only | WCAG AA not committed; text remains readable and controls target 44px+ where practical |

#### 2. Screen Inventory

| Screen ID | Screen | Route / Surface | Entry From | Exit To | Auth Required | FR liên quan |
|---|---|---|---|---|---|---|
| SCREEN-001 | Login OTP | `/login` | Auth-required action | previous route / match list | No | FR-001 |
| SCREEN-002 | Match List | `/matches` | Home / login success | Match Seat Selection | No for browse, Yes before checkout | FR-002 |
| SCREEN-003 | Match Seat Selection | `/matches/{matchId}/seats` | Match List | Checkout | Yes for checkout | FR-003 |
| SCREEN-004 | Checkout Transfer QR | `/checkout/{orderId}` | Seat Selection / Exchange | Pending Confirmation | Yes | FR-004, FR-005 |
| SCREEN-005 | Pending Confirmation | `/orders/{orderId}/pending` | Checkout | History / Ticket Detail | Yes | FR-005 |
| SCREEN-006 | Admin Match Management | `/admin/matches` | Admin nav | Seat/Price config | Admin | FR-006 |
| SCREEN-007 | Admin Seat Price QR Config | `/admin/matches/{matchId}/inventory` | Admin Match Management | Admin Match Management | Admin | FR-007 |
| SCREEN-008 | Admin Payment Confirmation | `/admin/confirmations` | Admin nav | issued/rejected result | Admin | FR-008 |
| SCREEN-009 | Purchase History | `/orders` | User nav | Ticket Detail | Yes | FR-009 |
| SCREEN-010 | Ticket Detail | `/tickets/{ticketId}` | History | Exchange / QR display | Yes | FR-009 |
| SCREEN-011 | Scan Status Result | API consumer / simple result surface | Gate scan API call | status result | Service/admin | FR-010 |
| SCREEN-012 | Seat Exchange | `/tickets/{ticketId}/exchange` | Ticket Detail | Checkout Transfer QR | Yes | FR-011, FR-012 |

#### 3. User Flows

| Flow | FR / US | Entry | Success | Error / Edge Handling |
|---|---|---|---|---|
| Login OTP | FR-001 / US-001 | Auth-required action or `/login` | Authenticated session, redirect to intended route | Invalid OTP shows inline error; unauthenticated checkout redirects to login |
| Browse and choose seats | FR-002, FR-003 / US-002, US-003 | Match List | Up to 5 selected seats, checkout enabled | Sold-out/cancelled matches unavailable; sixth seat blocked |
| Manual transfer checkout | FR-004, FR-005 / US-004, US-005 | Seat Selection | Held seats, QR shown, pending confirmation created | Hold expiry shows expired state and requires new order |
| Admin setup and confirmation | FR-006, FR-007, FR-008 / US-006, US-007, US-008 | Admin nav | Match/inventory configured; order confirmed or rejected | Closed/cancelled match blocks sale; rejected payment releases seats |
| Ticket access and scan | FR-009, FR-010 / US-009, US-010, US-011 | History / scanner API | QR displayed; first scan marks used | Cancelled/exchanged tickets not valid; repeated scan rejected |
| Seat exchange | FR-011, FR-012 / US-012 | Ticket Detail | New ticket issued; old ticket exchanged | Cheaper/unavailable seats blocked; old ticket remains valid until confirm |

#### 4. Error & Success Message Copy

| Context | Trigger | Message Text | Type | Notes |
|---|---|---|---|---|
| Login | Invalid OTP | `Mã OTP không đúng. Vui lòng kiểm tra và thử lại.` | inline error | OTP field |
| Auth required | User starts checkout unauthenticated | `Vui lòng đăng nhập để tiếp tục mua vé.` | modal | CTA: `Đăng nhập` |
| Seat selection | Select sixth seat | `Bạn chỉ có thể chọn tối đa 5 ghế cho mỗi lần mua.` | toast | Keep existing selection |
| Seat selection | Seat no longer available | `Ghế này vừa được người khác giữ. Vui lòng chọn ghế khác.` | inline/seat toast | Refresh seat state |
| Checkout | Hold expired | `Đã hết thời gian giữ ghế. Vui lòng tạo đơn mới.` | error panel | CTA: `Chọn lại ghế` |
| Checkout | Payment submitted | `Đã gửi xác nhận thanh toán. Admin sẽ kiểm tra trong 10 phút.` | success toast | Go pending |
| Admin confirm | Payment confirmed | `Đã xác nhận thanh toán và phát hành vé.` | success toast | Order becomes issued |
| Admin confirm | Payment rejected | `Đã từ chối giao dịch. Ghế đã được mở lại.` | success toast | Order rejected |
| Ticket detail | Invalid ticket | `Vé này không còn hiệu lực để vào cổng.` | error panel | For cancelled/exchanged |
| Scan | Already scanned | `Vé đã được quét trước đó.` | error result | No state change |
| Exchange | Cheaper seat selected | `Chỉ được đổi sang ghế có giá bằng hoặc cao hơn.` | inline error | Block continue |

#### 5. Form Validation Spec

| Form | Field | Required | Rule | Trigger | Error Message |
|---|---|---|---|---|---|
| Login OTP | `identifier` | Yes | email or Vietnamese phone-like text | on submit | `Nhập email hoặc số điện thoại hợp lệ.` |
| Login OTP | `otp` | Yes | 4-8 numeric chars for demo | on submit | `Nhập mã OTP hợp lệ.` |
| Admin Match | `matchName` | Yes | 3-120 chars | on blur / submit | `Nhập tên trận đấu.` |
| Admin Match | `saleStatus` | Yes | `OPEN_FOR_SALE`, `SOLD_OUT`, `CANCELLED`, `CLOSED` | on submit | `Chọn trạng thái bán vé.` |
| Admin Inventory | `section` | Yes | A/B/C/D, VIP under A | on submit | `Chọn khu hợp lệ.` |
| Admin Inventory | `floor` | Yes | 1 or 2 | on submit | `Chọn tầng hợp lệ.` |
| Admin Inventory | `price` | Yes | VND amount > 0 | on blur / submit | `Giá vé phải lớn hơn 0.` |
| Admin QR Config | `qrName` | Yes | 2-80 chars | on blur | `Nhập tên QR.` |
| Admin QR Config | `qrImage` | Yes | image or configured QR reference | on submit | `Cấu hình QR thanh toán mặc định.` |
| Admin Confirm | `decision` | Yes | confirm or reject | on submit | `Chọn xác nhận hoặc từ chối.` |

#### 6. Design-to-FR Traceability

| FR | Related US | Screens | Required UX Coverage |
|---|---|---|---|
| FR-001 | US-001 | SCREEN-001 | OTP form, unauthenticated redirect, invalid OTP copy |
| FR-002 | US-002 | SCREEN-002 | Match list states and unavailable match behavior |
| FR-003 | US-003 | SCREEN-003 | Seat map, colors, 5-seat cap, unavailable seat error |
| FR-004 | US-004 | SCREEN-004 | Hold countdown, price snapshot display, expiry error |
| FR-005 | US-005 | SCREEN-004, SCREEN-005 | Transfer QR, payment completion CTA, pending countdown |
| FR-006 | US-006 | SCREEN-006 | Admin match CRUD and status changes |
| FR-007 | US-007 | SCREEN-007 | Seat generation, price versions, default QR config |
| FR-008 | US-008 | SCREEN-008 | Pending list filters, confirm/reject actions |
| FR-009 | US-009, US-010 | SCREEN-009, SCREEN-010 | History, ticket status, QR display |
| FR-010 | US-011 | SCREEN-011 | Scan success/repeat failure state |
| FR-011 | US-012 | SCREEN-012 | Eligible replacement seat selection |
| FR-012 | US-012 | SCREEN-012, SCREEN-004, SCREEN-005 | Exchange confirmation, old/new ticket states |

> **Assumption**: Material-style custom components are built with Tailwind tokens, not MUI.
> **Validate**: Product Owner confirms during Design review.
> **Change trigger**: If MUI is mandated, component specs and tokens must be revised.

<!-- ID: SCREEN-001 -->
### SCREEN-001: Login OTP

- **Purpose**: Let user authenticate by email or phone OTP.
- **FR / US**: FR-001 / US-001
- **Layout**: centered auth panel; identifier field; OTP field shown after request; primary CTA `Tiếp tục`; secondary copy for demo OTP.
- **States**:
  - Empty: `login-empty`, copy `Đăng nhập để mua vé`, CTA disabled until identifier is present; exits when user types.
  - Loading: `login-loading`, CTA shows `Đang gửi...` or `Đang xác thực...`; exits on response.
  - Populated: `login-form`, fields visible; exits on valid OTP to intended route.
  - Error: `login-error`, exact copy `Mã OTP không đúng. Vui lòng kiểm tra và thử lại.`; exits when user edits OTP or retries.
- **Validation**: identifier validates on submit; OTP validates on submit.

<!-- ID: SCREEN-002 -->
### SCREEN-002: Match List

- **Purpose**: Show matches currently selling tickets.
- **FR / US**: FR-002 / US-002
- **Layout**: top app bar, match cards, status chip, date/time, CTA `Chọn ghế`.
- **States**:
  - Empty: `matches-empty`, copy `Chưa có trận đấu đang bán vé.`; exits when data appears.
  - Loading: `matches-loading`, skeleton list; exits on fetch resolved.
  - Populated: `matches-list`, cards for `OPEN_FOR_SALE`; exits to SCREEN-003.
  - Error: `matches-error`, copy `Không thể tải danh sách trận đấu. Vui lòng thử lại.` CTA `Thử lại`.
- **Validation**: N/A — no form fields.

<!-- ID: SCREEN-003 -->
### SCREEN-003: Match Seat Selection

- **Purpose**: Let user select up to 5 available concrete seat codes.
- **FR / US**: FR-003 / US-003
- **Layout**: section tabs A/B/C/D, floor segmented control, VIP tab under A, seat grid, color legend, selected-seat tray, CTA `Thanh toán`.
- **States**:
  - Empty: `seat-map-empty`, copy `Khu này chưa có ghế khả dụng.`; exits when another section has seats.
  - Loading: `seat-map-loading`, grid skeleton and disabled CTA.
  - Populated: `seat-map-grid`, seat chips show available/held/issued/selected colors; countdown absent until checkout.
  - Error: `seat-map-error`, copy `Không thể tải sơ đồ ghế. Vui lòng thử lại.` CTA `Thử lại`.
- **Validation**: max 5 seats; unavailable seat cannot be selected; checkout requires login and at least 1 seat.

<!-- ID: SCREEN-004 -->
### SCREEN-004: Checkout Transfer QR

- **Purpose**: Hold seats, show QR payment instructions, and let user submit payment completion.
- **FR / US**: FR-004, FR-005 / US-004, US-005
- **Layout**: countdown banner `Còn MM:SS để giữ ghế`, order summary, selected seats, total VND, large QR, instruction copy, CTA `Tôi đã chuyển khoản`.
- **States**:
  - Empty: `checkout-empty`, copy `Không có ghế trong đơn thanh toán.`; exits to seat selection.
  - Loading: `checkout-loading`, order summary skeleton; CTA disabled.
  - Populated: `checkout-qr`, countdown and QR visible; exits to SCREEN-005 after submit.
  - Error: `checkout-expired-error`, copy `Đã hết thời gian giữ ghế. Vui lòng tạo đơn mới.` CTA `Chọn lại ghế`.
- **Validation**: CTA enabled only while hold is active; submit creates pending confirmation.

<!-- ID: SCREEN-005 -->
### SCREEN-005: Pending Confirmation

- **Purpose**: Show admin confirmation wait state.
- **FR / US**: FR-005 / US-005
- **Layout**: status banner `Đang chờ admin xác nhận`, countdown 10 minutes, order summary, CTA `Xem lịch sử mua vé`.
- **States**:
  - Empty: `pending-empty`, copy `Không có giao dịch chờ xác nhận.`
  - Loading: `pending-loading`, status skeleton.
  - Populated: `pending-confirmation`, countdown and status visible; exits to issued/rejected/expired.
  - Error: `pending-expired-error`, copy `Admin chưa xác nhận trong 10 phút. Đơn đã bị hủy và ghế đã được mở lại.`
- **Validation**: N/A.

<!-- ID: SCREEN-006 -->
### SCREEN-006: Admin Match Management

- **Purpose**: Manage match list, creation, updates, and sale status.
- **FR / US**: FR-006 / US-006
- **Layout**: admin shell, table, status filter, `Tạo trận đấu` button, edit drawer.
- **States**:
  - Empty: `admin-matches-empty`, copy `Chưa có trận đấu nào.`
  - Loading: `admin-matches-loading`, table skeleton.
  - Populated: `admin-matches-table`, rows with status chips and actions.
  - Error: `admin-matches-error`, copy `Không thể tải danh sách trận đấu.`
- **Validation**: match name required; sale status required.

<!-- ID: SCREEN-007 -->
### SCREEN-007: Admin Seat Price QR Config

- **Purpose**: Configure seats, active prices, and default transfer QR.
- **FR / US**: FR-007 / US-007
- **Layout**: match context header, tabs `Ghế`, `Giá`, `QR thanh toán`, editable tables.
- **States**:
  - Empty: `admin-inventory-empty`, copy `Chưa cấu hình ghế cho trận này.`
  - Loading: `admin-inventory-loading`, table skeleton.
  - Populated: `admin-inventory-config`, seat/price/QR tables visible.
  - Error: `admin-inventory-error`, copy `Không thể tải cấu hình vé.`
- **Validation**: section/floor/price/QR required as in §5.

<!-- ID: SCREEN-008 -->
### SCREEN-008: Admin Payment Confirmation

- **Purpose**: Confirm or reject pending payment completion records.
- **FR / US**: FR-008 / US-008
- **Layout**: pending table, filters status/time remaining, order detail side panel, CTAs `Xác nhận đã nhận tiền`, `Từ chối`.
- **States**:
  - Empty: `admin-confirm-empty`, copy `Không có giao dịch chờ xác nhận.`
  - Loading: `admin-confirm-loading`, table skeleton.
  - Populated: `admin-confirm-table`, pending rows with time remaining.
  - Error: `admin-confirm-error`, copy `Không thể tải giao dịch chờ xác nhận.`
- **Validation**: confirm/reject disabled when order is no longer pending.

<!-- ID: SCREEN-009 -->
### SCREEN-009: Purchase History

- **Purpose**: Let user review orders and ticket statuses.
- **FR / US**: FR-009 / US-009
- **Layout**: list of orders/tickets with match, seats, amount, status, CTA to detail.
- **States**:
  - Empty: `orders-empty`, copy `Bạn chưa có vé nào.`
  - Loading: `orders-loading`, list skeleton.
  - Populated: `orders-list`, own records only.
  - Error: `orders-error`, copy `Không thể tải lịch sử mua vé. Vui lòng thử lại.`
- **Validation**: N/A.

<!-- ID: SCREEN-010 -->
### SCREEN-010: Ticket Detail

- **Purpose**: Show issued QR/e-ticket and ticket status.
- **FR / US**: FR-009 / US-010
- **Layout**: large QR block, match, section/floor/seat, status chip, CTA `Đổi ghế` when eligible.
- **States**:
  - Empty: `ticket-empty`, copy `Không tìm thấy vé.`
  - Loading: `ticket-loading`, QR skeleton.
  - Populated: `ticket-detail`, QR and details visible for `ISSUED`.
  - Error: `ticket-invalid-error`, copy `Vé này không còn hiệu lực để vào cổng.`
- **Validation**: exchange CTA visible only for issued, not scanned/exchanged/cancelled tickets.

<!-- ID: SCREEN-011 -->
### SCREEN-011: Scan Status Result

- **Purpose**: Provide simple observable result for scan status update.
- **FR / US**: FR-010 / US-011
- **Layout**: API consumer result or minimal admin result panel with status.
- **States**:
  - Empty: `scan-empty`, copy `Chưa có dữ liệu quét vé.`
  - Loading: `scan-loading`, copy `Đang kiểm tra vé...`
  - Populated: `scan-success`, copy `Vé hợp lệ. Đã cập nhật trạng thái đã quét.`
  - Error: `scan-error`, copy `Vé đã được quét trước đó.`
- **Validation**: only `ISSUED` tickets can transition to scanned.

<!-- ID: SCREEN-012 -->
### SCREEN-012: Seat Exchange

- **Purpose**: Let user exchange an issued ticket to an available equal-or-higher priced seat.
- **FR / US**: FR-011, FR-012 / US-012
- **Layout**: current ticket summary, eligible seat grid, price difference panel, CTA `Tiếp tục đổi ghế`.
- **States**:
  - Empty: `exchange-empty`, copy `Không có ghế phù hợp để đổi.`
  - Loading: `exchange-loading`, grid skeleton.
  - Populated: `exchange-seat-grid`, only eligible seats selectable; exits to SCREEN-004.
  - Error: `exchange-error`, copy `Chỉ được đổi sang ghế có giá bằng hoặc cao hơn.`
- **Validation**: cheaper/unavailable seats blocked; old ticket remains valid until admin confirms exchange.

<!-- ID: DS-COMP-001 -->
### DS-COMP-001: Seat Chip

- **Purpose**: Represents one seat code and availability state.
- **Variants**: available, selected, held, issued, unavailable, VIP.
- **States**: disabled when not selectable; selected uses primary color; held uses amber.
- **Trace**: SCREEN-003, SCREEN-012.

<!-- ID: DS-COMP-002 -->
### DS-COMP-002: Countdown Banner

- **Purpose**: Shows remaining time for seat hold or admin confirmation.
- **Variants**: hold countdown, pending confirmation countdown, expired.
- **Trace**: SCREEN-004, SCREEN-005.

<!-- ID: DS-COMP-003 -->
### DS-COMP-003: Ticket QR Card

- **Purpose**: Displays QR/e-ticket with ticket metadata and status.
- **Variants**: issued, scanned, invalid, exchanged.
- **Trace**: SCREEN-010.

<!-- ID: DS-COMP-004 -->
### DS-COMP-004: Admin Data Table

- **Purpose**: Dense admin table for matches, inventory, and confirmation queues.
- **Variants**: sortable, filterable, row action side panel.
- **Trace**: SCREEN-006, SCREEN-007, SCREEN-008.

<!-- ID: DS-COMP-005 -->
### DS-COMP-005: Status Chip

- **Purpose**: Consistent visual status for match, order, seat, and ticket states.
- **Variants**: open, sold out, cancelled, closed, held, pending, issued, scanned, rejected, exchanged.
- **Trace**: all screens with state.

## Updated

## Removed

