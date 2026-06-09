---
status: APPROVED
version: v2
sprint: 2
phase: design
sprint_id: sprint-v2
created: 2026-06-09
updated: 2026-06-09 12:04
approved_by: user
applied_to_living: false
---

# Design System Proposal — Sprint v2

## New

## Updated

<!-- ID: DESIGN-OVERVIEW-001 -->
### Design Overview

#### 1. Design Principles & Brand Guidelines

Industry vertical = ticketing / football ticket sales, inherited from Product v2. Sprint v2 keeps the existing product lifecycle and turns the user/admin surfaces into a credible ticket marketplace and operations console.

Design principles:
1. Ticket context first — every user-facing screen must show match, date, venue, price, seat, and status context before secondary details.
2. Operational clarity — admin screens prioritize counts, state, expiry, and next action over decoration.
3. Demo resilience without production confusion — local fallback data can prevent blank browsing, but checkout/payment copy must still signal that real actions require backend availability.
4. Test-observable states — every loading, empty, populated, error, validation, and local fallback state has stable QA-visible identifiers and exact copy.
5. Accessible defaults — use practical WCAG AA contrast, keyboard-reachable controls, 44px+ touch targets for user web, and visible focus states.

Brand/system defaults:

| Element | Value | Notes |
|---|---|---|
| Primary Color | `#0F766E` | Selected seats, primary CTAs, active filters |
| Secondary Color | `#111827` | Headers, admin shell, dense table text |
| Accent Color | `#F59E0B` | Countdown, pending confirmation, price emphasis |
| Surface Color | `#F8FAFC` | Page background, avoids plain white-only pages |
| Error Color | `#DC2626` | Expired, rejected, unavailable, destructive action |
| Success Color | `#16A34A` | Issued, confirmed, valid-entry signals |
| Typography | Inter / system sans-serif | Same across user web and admin web |
| Border Radius | 8px | Cards, buttons, inputs, chips |
| Spacing Unit | 4px | 8/12/16/24/32 scale |
| Visual Assets | Real match/team/stadium imagery where available; otherwise generated/demo event media | No abstract hero gradients as primary product signal |
| Platform | User Web responsive mobile/desktop; Admin Web desktop-first | iOS/Android unchanged in Sprint v2 |

#### 2. Screen Inventory

| Screen ID | Screen | Route / Surface | Entry From | Exit To | Auth Required | FR liên quan | Sprint v2 Status |
|---|---|---|---|---|---|---|---|
| SCREEN-001 | Login OTP | `/login` | Auth-required action | previous route / match list | No | FR-001 | Carry forward |
| SCREEN-002 | Match List | `/matches` | Home / login success | Match Seat Selection | No for browse, Yes before checkout | FR-002 | Updated |
| SCREEN-003 | Match Seat Selection | `/matches/{matchId}/seats` | Match List | Checkout | Yes for checkout | FR-003 | Updated |
| SCREEN-004 | Checkout Transfer QR | `/checkout/{orderId}` | Seat Selection / Exchange | Pending Confirmation | Yes | FR-004, FR-005 | Updated |
| SCREEN-005 | Pending Confirmation | `/orders/{orderId}/pending` | Checkout | History / Ticket Detail | Yes | FR-005 | Updated |
| SCREEN-006 | Admin Match Management | `/admin/matches` | Admin nav | Seat/Price config | Admin | FR-006 | Updated |
| SCREEN-007 | Admin Seat Price QR Config | `/admin/matches/{matchId}/inventory` | Admin Match Management | Admin Match Management | Admin | FR-007 | Updated |
| SCREEN-008 | Admin Payment Confirmation | `/admin/confirmations` | Admin nav | issued/rejected result | Admin | FR-008 | Updated |
| SCREEN-009 | Purchase History | `/orders` | User nav | Ticket Detail | Yes | FR-009 | Updated |
| SCREEN-010 | Ticket Detail | `/tickets/{ticketId}` | History | Exchange / QR display | Yes | FR-009 | Updated |
| SCREEN-011 | Scan Status Result | API consumer / simple result surface | Gate scan API call | status result | Service/admin | FR-010 | Carry forward |
| SCREEN-012 | Seat Exchange | `/tickets/{ticketId}/exchange` | Ticket Detail | Checkout Transfer QR | Yes | FR-011, FR-012 | Carry forward |

#### 3. User Flows

| Flow | FR / US / AC | Entry | Success | Error / Edge Handling |
|---|---|---|---|---|
| Marketplace browsing | FR-002 / US-002 / AC-003, AC-004, AC-025, AC-026 | `/matches` | User sees marketplace-style event cards grouped by date and opens seat selection with `Chọn ghế` | Empty state for no open matches; local fallback state for unavailable/unseeded API; retry error when non-demo fetch fails |
| Seat selection | FR-003 / US-003 / AC-005, AC-006, AC-027, AC-028 | SCREEN-002 | User selects 1-5 available seats and sees sticky order summary | Sixth seat blocked; unavailable seat disabled; local fallback seats only allow display/selection preview, checkout still requires backend |
| Manual transfer checkout | FR-004, FR-005 / US-004, US-005 / AC-007..AC-010, AC-029, AC-030 | SCREEN-003 | User sees hold timer, QR, total amount, and submits `Tôi đã chuyển khoản` | Expired hold blocks submit and routes to seat selection; backend error preserves selected order summary |
| Admin match operations | FR-006 / US-006 / AC-011, AC-012, AC-031 | `/admin/matches` | Admin sees metrics, status filters, match table, and inventory action | Empty table CTA; load error retry; cancelled/closed status visually blocks sale |
| Admin inventory operations | FR-007 / US-007 / AC-013, AC-014, AC-032 | SCREEN-006 | Admin manages seats, prices, QR tabs and default QR | Missing price/QR validation; API error keeps form data |
| Admin payment queue | FR-008 / US-008 / AC-015, AC-016, AC-033 | `/admin/confirmations` | Admin confirms/rejects pending records with clear primary action | Expired/non-pending records disable actions; reject requires confirmation |
| Ticket history/detail | FR-009 / US-009, US-010 / AC-017, AC-018, AC-034, AC-035 | User nav / history | User sees ticket-marketplace order cards and e-ticket detail with valid-entry signal | Empty history state; invalid ticket state; QR hidden/disabled when not valid |

#### 4. Error & Success Message Copy

| Context | Trigger | Message Text | Type | Stable Hook |
|---|---|---|---|---|
| Match list | no open matches | `Chưa có trận đấu đang bán vé.` | empty panel | `matches-empty` |
| Match list | local fallback active | `Đang hiển thị dữ liệu demo vì backend local chưa sẵn sàng.` | info banner | `matches-demo-fallback` |
| Match list | fetch failed outside demo fallback | `Không thể tải danh sách trận đấu. Vui lòng thử lại.` | error panel | `matches-error` |
| Seat map | no seats in selected section/filter | `Khu này chưa có ghế khả dụng.` | empty panel | `seat-map-empty` |
| Seat map | select sixth seat | `Bạn chỉ có thể chọn tối đa 5 ghế cho mỗi lần mua.` | toast | `seat-limit-error` |
| Seat map | backend unavailable in local fallback | `Đang hiển thị sơ đồ ghế demo. Thanh toán cần backend hoạt động.` | info banner | `seat-map-demo-fallback` |
| Seat map | unavailable seat selected | `Ghế này không còn khả dụng. Vui lòng chọn ghế khác.` | inline/toast | `seat-unavailable-error` |
| Checkout | hold expired | `Đã hết thời gian giữ ghế. Vui lòng tạo đơn mới.` | error panel | `checkout-expired-error` |
| Checkout | payment submitted | `Đã gửi xác nhận thanh toán. Admin sẽ kiểm tra trong 10 phút.` | success toast | `payment-submitted-toast` |
| Pending | admin confirmation expired | `Admin chưa xác nhận trong 10 phút. Đơn đã bị hủy và ghế đã được mở lại.` | error panel | `pending-expired-error` |
| Admin matches | load failed | `Không thể tải danh sách trận đấu.` | error panel | `admin-matches-error` |
| Admin inventory | missing active QR | `Cấu hình QR thanh toán mặc định.` | inline error | `qr-default-error` |
| Admin confirmation | confirm success | `Đã xác nhận thanh toán và phát hành vé.` | success toast | `admin-confirm-success` |
| Admin confirmation | reject success | `Đã từ chối giao dịch. Ghế đã được mở lại.` | success toast | `admin-reject-success` |
| Ticket detail | invalid entry | `Vé này không còn hiệu lực để vào cổng.` | error panel | `ticket-invalid-error` |

#### 5. Form Validation Spec

| Form | Field | Required | Rule | Trigger | Error Message |
|---|---|---|---|---|---|
| Admin Match | `matchName` | Yes | 3-120 chars | on blur / submit | `Nhập tên trận đấu.` |
| Admin Match | `saleStatus` | Yes | `OPEN_FOR_SALE`, `SOLD_OUT`, `CANCELLED`, `CLOSED` | on submit | `Chọn trạng thái bán vé.` |
| Admin Inventory | `section` | Yes | A/B/C/D; VIP only under A | on submit | `Chọn khu hợp lệ.` |
| Admin Inventory | `floor` | Yes | 1 or 2 | on submit | `Chọn tầng hợp lệ.` |
| Admin Inventory | `price` | Yes | VND amount > 0 | on blur / submit | `Giá vé phải lớn hơn 0.` |
| Admin QR Config | `qrName` | Yes | 2-80 chars | on blur | `Nhập tên QR.` |
| Admin QR Config | `qrImage` | Yes | image or configured QR reference | on submit | `Cấu hình QR thanh toán mặc định.` |
| Admin Confirm | `decision` | Yes | confirm or reject | on submit | `Chọn xác nhận hoặc từ chối.` |

#### 6. Design-to-FR Traceability

| FR | Related US | Screens | Components | Status |
|---|---|---|---|---|
| FR-001 | US-001 | SCREEN-001 | Status Chip | Designed in v1 / carry forward |
| FR-002 | US-002 | SCREEN-002 | Status Chip, Admin Data Table pattern for grouped lists | Updated for Sprint v2 |
| FR-003 | US-003 | SCREEN-003 | Seat Chip, Status Chip | Updated for Sprint v2 |
| FR-004 | US-004 | SCREEN-004 | Countdown Banner, Seat Chip | Updated for Sprint v2 |
| FR-005 | US-005 | SCREEN-004, SCREEN-005 | Countdown Banner, Status Chip | Updated for Sprint v2 |
| FR-006 | US-006 | SCREEN-006 | Admin Data Table, Status Chip | Updated for Sprint v2 |
| FR-007 | US-007 | SCREEN-007 | Admin Data Table, Status Chip | Updated for Sprint v2 |
| FR-008 | US-008 | SCREEN-008 | Admin Data Table, Countdown Banner, Status Chip | Updated for Sprint v2 |
| FR-009 | US-009, US-010 | SCREEN-009, SCREEN-010 | Ticket QR Card, Status Chip | Updated for Sprint v2 |
| FR-010 | US-011 | SCREEN-011 | Ticket QR Card, Status Chip | Designed in v1 / carry forward |
| FR-011 | US-012 | SCREEN-012 | Seat Chip, Status Chip | Designed in v1 / carry forward |
| FR-012 | US-012 | SCREEN-012, SCREEN-004, SCREEN-005 | Countdown Banner, Status Chip | Designed in v1 / carry forward |

> Assumption: Custom Tailwind components remain the design-system implementation target, not MUI.
> Validate: Product Owner / Tech Lead confirm before implementation planning.
> Change trigger: If a third-party component library is mandated, component specs and tokens must be revised.

<!-- ID: SCREEN-001 -->
### SCREEN-001: Login OTP

- **Purpose**: Let user authenticate by email or phone OTP before purchase/history/exchange actions.
- **FR / US / AC**: FR-001 / US-001 / AC-001, AC-002.
- **Layout**: centered auth panel; identifier field; OTP field after request; primary CTA `Tiếp tục`; secondary demo OTP helper copy.
- **Key interactions**: submit identifier to request OTP; submit OTP to authenticate; unauthenticated purchase action redirects here and returns to intended route after success.
- **Exit**: intended route or SCREEN-002 after successful login.

**States**

| State | Stable Identifier | Visible Signal | Exit Condition |
|---|---|---|---|
| Empty | `login-empty` | Heading `Đăng nhập để mua vé`, identifier field empty, CTA disabled until input | User enters identifier -> Populated |
| Loading | `login-loading` | CTA shows `Đang gửi...` or `Đang xác thực...`, fields disabled, `aria-busy="true"` | Request resolves -> Populated / Error |
| Populated | `login-form` | Identifier/OTP fields visible, CTA `Tiếp tục`, demo helper copy visible | Valid OTP -> intended route |
| Error | `login-error` | Inline copy `Mã OTP không đúng. Vui lòng kiểm tra và thử lại.`, `role="alert"` | User edits OTP or retries -> Populated / Loading |

**Validation Behavior**

| Field / Control | Rule | Trigger | Error Copy |
|---|---|---|---|
| `identifier` | email or phone-like text required | on submit | `Nhập email hoặc số điện thoại hợp lệ.` |
| `otp` | 4-8 numeric chars for demo | on submit | `Nhập mã OTP hợp lệ.` |
| Auth-required action | user must be logged in | on checkout/exchange click | `Vui lòng đăng nhập để tiếp tục mua vé.` |

> Assumption: OTP delivery remains demo-capable and does not require vendor-specific UX in Sprint v2.
> Validate: Architecture confirms OTP delivery approach.
> Change trigger: If production identity is required, add resend limits, lockout, and vendor error states.

<!-- ID: SCREEN-002 -->
### SCREEN-002: Match List

- **Purpose**: Show matches currently selling tickets in a football-ticket marketplace layout.
- **FR / US / AC**: FR-002 / US-002 / AC-003, AC-004, AC-025, AC-026.
- **Layout**: page header with `ticket_mafia` nav and primary search; full-width football event hero band; filter row with search, date, venue/status chips; grouped date sections; event cards with team/match title, venue, kickoff time, remaining-ticket signal, starting price, status chip, and `Chọn ghế` CTA.
- **Key interactions**: search filters cards; date/status chips narrow list; `Chọn ghế` opens SCREEN-003; local fallback info banner is dismissible for the session only.
- **Exit**: SCREEN-003 for an open match.

**States**

| State | Stable Identifier | Visible Signal | Exit Condition |
|---|---|---|---|
| Empty | `matches-empty` | Heading `Chưa có trận đấu đang bán vé.`, subtext `Quay lại sau khi admin mở bán trận đấu mới.`, CTA `Tải lại` | Data appears -> Populated; retry starts -> Loading |
| Loading | `matches-loading` | Hero skeleton + 3 event-card skeleton rows, filters disabled, `aria-busy="true"` | Fetch resolved -> Populated / Empty / Error |
| Populated | `matches-list` | Date groups, event cards, visible starting price, `Chọn ghế` buttons enabled for open matches | User selects match -> SCREEN-003; filters return 0 -> Empty |
| Error | `matches-error` | Copy `Không thể tải danh sách trận đấu. Vui lòng thử lại.`, CTA `Thử lại`, `role="alert"` | Retry succeeds -> Populated / Empty |
| Local Fallback | `matches-demo-fallback` | Info banner `Đang hiển thị dữ liệu demo vì backend local chưa sẵn sàng.` and demo event cards | Backend data becomes available -> Populated |

**Validation Behavior**

| Control | Rule | Trigger | Error Copy |
|---|---|---|---|
| Search | optional, max 80 chars | on change | N/A |
| Date/status filters | optional, one active value per filter group | on click | N/A |
| `Chọn ghế` | enabled only for sellable/open match cards | on click | `Trận này hiện chưa mở bán.` |

> Assumption: Product accepts demo fallback only for local browsing, not production purchase behavior.
> Validate: Tech Lead confirms in Architecture / Test before Implement approval.
> Change trigger: If fallback is disabled, remove `matches-demo-fallback` state and rely only on error/empty.

<!-- ID: SCREEN-003 -->
### SCREEN-003: Match Seat Selection

- **Purpose**: Let user inspect match detail context and select up to 5 available concrete seats.
- **FR / US / AC**: FR-003 / US-003 / AC-005, AC-006, AC-027, AC-028.
- **Layout**: event banner with match, venue, kickoff, starting price; availability summary cards; section segmented control A/B/C/D with VIP sub-tab under A; floor selector; seat status legend; seat card grid; sticky selected-seat summary with total and `Thanh toán` CTA.
- **Key interactions**: section/floor change filters seats; seat card toggles selected state when available; sticky summary updates count/total; checkout requires 1-5 selected seats and backend availability.
- **Exit**: SCREEN-004 after valid checkout start.

**States**

| State | Stable Identifier | Visible Signal | Exit Condition |
|---|---|---|---|
| Empty | `seat-map-empty` | Copy `Khu này chưa có ghế khả dụng.`, alternate section chips remain available | User selects section with seats -> Populated |
| Loading | `seat-map-loading` | Banner skeleton, disabled seat cards, sticky summary skeleton, `aria-busy="true"` | Fetch resolved -> Populated / Empty / Error |
| Populated | `seat-map-grid` | Seat cards with available/selected/held/issued/VIP variants, selected count, total VND, enabled CTA when valid | Checkout starts -> SCREEN-004; selected count becomes 0 -> CTA disabled |
| Error | `seat-map-error` | Copy `Không thể tải sơ đồ ghế. Vui lòng thử lại.`, CTA `Thử lại`, `role="alert"` | Retry succeeds -> Populated / Empty |
| Local Fallback | `seat-map-demo-fallback` | Banner `Đang hiển thị sơ đồ ghế demo. Thanh toán cần backend hoạt động.`; seat interactions work for preview; checkout CTA disabled or shows backend requirement | Backend available -> Populated |

**Validation Behavior**

| Control | Rule | Trigger | Error Copy |
|---|---|---|---|
| Seat card | selectable only when `AVAILABLE` | on click | `Ghế này không còn khả dụng. Vui lòng chọn ghế khác.` |
| Selected seats | min 1, max 5 | on click / checkout | `Bạn chỉ có thể chọn tối đa 5 ghế cho mỗi lần mua.` |
| Checkout CTA | requires login, 1-5 seats, backend available | on click | `Vui lòng đăng nhập để tiếp tục mua vé.` or `Thanh toán cần backend hoạt động.` |

> Assumption: Seat layout is card/grid based, not exact stadium geometry.
> Validate: Product Owner confirms before Plan.
> Change trigger: If real irregular stadium map is required, SCREEN-003 becomes a map-editor/display scope and must be reworked.

<!-- ID: SCREEN-004 -->
### SCREEN-004: Checkout Transfer QR

- **Purpose**: Show held seats, price snapshot, transfer QR, and payment completion CTA.
- **FR / US / AC**: FR-004, FR-005 / US-004, US-005 / AC-007, AC-008, AC-009, AC-010, AC-029.
- **Layout**: countdown banner `Còn MM:SS để giữ ghế`; match/order summary; selected seat list; total amount; large QR payment area; transfer instructions; primary CTA `Tôi đã chuyển khoản`; secondary link `Chọn lại ghế`.
- **Key interactions**: countdown ticks every second; CTA disabled after expiry; payment submission shows loading state; success routes to SCREEN-005.
- **Exit**: SCREEN-005 after payment completion.

**States**

| State | Stable Identifier | Visible Signal | Exit Condition |
|---|---|---|---|
| Empty | `checkout-empty` | Copy `Không có ghế trong đơn thanh toán.`, CTA `Chọn ghế` | User returns to seat selection |
| Loading | `checkout-loading` | Summary skeleton, QR skeleton, CTA disabled with `Đang tải...` | Order loads -> Populated / Error |
| Populated | `checkout-qr` | Countdown, QR image, seat list, total amount, `Tôi đã chuyển khoản` enabled while hold active | Submit succeeds -> SCREEN-005; countdown expires -> Error |
| Error | `checkout-expired-error` | Copy `Đã hết thời gian giữ ghế. Vui lòng tạo đơn mới.`, CTA `Chọn lại ghế` | User starts new order |

**Validation Behavior**

| Control | Rule | Trigger | Error Copy |
|---|---|---|---|
| Payment completion CTA | hold must be active | on click / timer expiry | `Đã hết thời gian giữ ghế. Vui lòng tạo đơn mới.` |
| QR block | active default QR required | on load | `Chưa có QR thanh toán. Vui lòng thử lại sau.` |
| Submit | backend required | on submit | `Không thể gửi xác nhận thanh toán. Vui lòng thử lại.` |

> Assumption: User does not upload a transfer receipt in Sprint v2.
> Validate: Product Owner confirms during Design review.
> Change trigger: If receipt upload becomes required, add upload validation and preview/error states.

<!-- ID: SCREEN-005 -->
### SCREEN-005: Pending Confirmation

- **Purpose**: Confirm to the user that payment completion was submitted and admin has a deadline to decide.
- **FR / US / AC**: FR-005 / US-005 / AC-009, AC-030.
- **Layout**: status hero `Đang chờ admin xác nhận`; confirmation deadline countdown; order summary; selected seats; CTA `Xem lịch sử mua vé`; secondary `Quay lại danh sách trận`.
- **Key interactions**: user can leave to history; status refreshes to issued/rejected/expired; expired/rejected states show recovery copy.
- **Exit**: SCREEN-009 or SCREEN-010 when ticket is issued.

**States**

| State | Stable Identifier | Visible Signal | Exit Condition |
|---|---|---|---|
| Empty | `pending-empty` | Copy `Không có giao dịch chờ xác nhận.` | User navigates to history |
| Loading | `pending-loading` | Status skeleton and disabled actions | Status loads -> Populated / Error |
| Populated | `pending-confirmation` | Pending chip, deadline countdown, order summary, CTA `Xem lịch sử mua vé` | Admin confirms -> issued; rejects/expires -> Error state |
| Error | `pending-expired-error` | Copy `Admin chưa xác nhận trong 10 phút. Đơn đã bị hủy và ghế đã được mở lại.` | User returns to match list |

**Validation Behavior**

| Control | Rule | Trigger | Error Copy |
|---|---|---|---|
| Status refresh | order must still exist | refresh / polling | `Không thể cập nhật trạng thái đơn. Vui lòng thử lại.` |

> Assumption: Polling/refresh behavior is implementation-owned; design requires only visible status and retry.
> Validate: Architecture confirms refresh mechanism.
> Change trigger: If realtime push is introduced, add live-update and stale-state copy.

<!-- ID: SCREEN-006 -->
### SCREEN-006: Admin Match Management

- **Purpose**: Give admin a dashboard-style match list with metrics, status filters, and inventory entry actions.
- **FR / US / AC**: FR-006 / US-006 / AC-011, AC-012, AC-031.
- **Layout**: admin shell; header `Quản lý trận đấu`; metric strip for total/open/sold-out/cancelled; status segmented filter; search; dense match table; row actions `Cấu hình vé`, `Sửa`, status chip.
- **Key interactions**: filter table by status; edit/create match drawer; inventory action opens SCREEN-007.
- **Exit**: SCREEN-007 or same page after save.

**States**

| State | Stable Identifier | Visible Signal | Exit Condition |
|---|---|---|---|
| Empty | `admin-matches-empty` | Copy `Chưa có trận đấu nào.`, CTA `Tạo trận đấu` | Admin creates first match |
| Loading | `admin-matches-loading` | Metric/table skeleton, disabled row actions | Fetch resolved -> Populated / Empty / Error |
| Populated | `admin-matches-table` | Metrics, table rows, status chips, `Cấu hình vé` actions | Filter returns 0 -> Empty filtered variant |
| Error | `admin-matches-error` | Copy `Không thể tải danh sách trận đấu.`, CTA `Thử lại` | Retry succeeds |

**Validation Behavior**

| Field / Control | Rule | Trigger | Error Copy |
|---|---|---|---|
| `matchName` | required, 3-120 chars | on blur / submit | `Nhập tên trận đấu.` |
| `saleStatus` | one allowed state | on submit | `Chọn trạng thái bán vé.` |
| Save | form valid | on submit | `Không thể lưu trận đấu. Vui lòng thử lại.` |

> Assumption: Admin match edit happens in a drawer/modal, not a separate route.
> Validate: Admin stakeholder confirms during Design review.
> Change trigger: If match creation becomes multi-step, split into a dedicated screen.

<!-- ID: SCREEN-007 -->
### SCREEN-007: Admin Seat Price QR Config

- **Purpose**: Configure seat inventory, active prices, and default transfer QR for one match.
- **FR / US / AC**: FR-007 / US-007 / AC-013, AC-014, AC-032.
- **Layout**: match context header; inventory metrics; tabs `Ghế`, `Giá`, `QR thanh toán`; structured section/floor/VIP inputs; seat rows; price rows; QR cards with `Chọn QR mặc định`.
- **Key interactions**: switch tabs without losing form state; add/update seats; edit price; select default QR; status/error chips for incomplete configuration.
- **Exit**: SCREEN-006 after save or admin nav.

**States**

| State | Stable Identifier | Visible Signal | Exit Condition |
|---|---|---|---|
| Empty | `admin-inventory-empty` | Copy `Chưa cấu hình ghế cho trận này.`, CTA `Tạo ghế` | Admin generates/configures seats |
| Loading | `admin-inventory-loading` | Header/tabs/table skeleton, disabled inputs | Data loads -> Populated / Error |
| Populated | `admin-inventory-config` | Metrics, tabbed tables, default QR card highlighted | Save succeeds; tab switch preserves data |
| Error | `admin-inventory-error` | Copy `Không thể tải cấu hình vé.`, CTA `Thử lại` | Retry succeeds |

**Validation Behavior**

| Field / Control | Rule | Trigger | Error Copy |
|---|---|---|---|
| Section | A/B/C/D; VIP only under A | on submit | `Chọn khu hợp lệ.` |
| Floor | 1 or 2 | on submit | `Chọn tầng hợp lệ.` |
| Price | VND amount > 0 | on blur / submit | `Giá vé phải lớn hơn 0.` |
| Default QR | at least one default active QR | on submit / choose default | `Cấu hình QR thanh toán mặc định.` |

> Assumption: Seat generation remains rule-based by section/floor/VIP and does not require a visual stadium editor.
> Validate: Product Owner confirms before Plan.
> Change trigger: If real layout editing is required, add a separate stadium layout screen.

<!-- ID: SCREEN-008 -->
### SCREEN-008: Admin Payment Confirmation

- **Purpose**: Let admin confirm or reject pending manual transfer records quickly and safely.
- **FR / US / AC**: FR-008 / US-008 / AC-015, AC-016, AC-033.
- **Layout**: queue metrics; filter chips for pending/expired/type; pending transaction table; row detail side panel; primary action `Xác nhận đã nhận tiền`; secondary destructive action `Từ chối`.
- **Key interactions**: select row opens details; confirm/reject requires active pending state; reject uses confirmation dialog; success removes or updates row.
- **Exit**: same page with refreshed queue.

**States**

| State | Stable Identifier | Visible Signal | Exit Condition |
|---|---|---|---|
| Empty | `admin-confirm-empty` | Copy `Không có giao dịch chờ xác nhận.`, metrics show zero pending | New pending payment appears |
| Loading | `admin-confirm-loading` | Metric/table skeleton, disabled actions | Fetch resolved -> Populated / Empty / Error |
| Populated | `admin-confirm-table` | Queue metrics, pending rows, expiry context, confirm/reject CTAs | Admin decision updates row |
| Error | `admin-confirm-error` | Copy `Không thể tải giao dịch chờ xác nhận.`, CTA `Thử lại` | Retry succeeds |

**Validation Behavior**

| Control | Rule | Trigger | Error Copy |
|---|---|---|---|
| Confirm | record must be pending and unexpired | on click | `Giao dịch này không còn chờ xác nhận.` |
| Reject | record must be pending; confirmation dialog accepted | on click | `Giao dịch này không còn chờ xác nhận.` |
| Refresh | backend available | on retry | `Không thể tải giao dịch chờ xác nhận.` |

> Assumption: Reject does not require a typed reason in Sprint v2.
> Validate: Product Owner confirms during Design review.
> Change trigger: If finance/audit needs rejection reason, add required reason validation.

<!-- ID: SCREEN-009 -->
### SCREEN-009: Purchase History

- **Purpose**: Let user review purchase/order history with ticket-marketplace styling and open ticket details.
- **FR / US / AC**: FR-009 / US-009 / AC-017, AC-034.
- **Layout**: page header `Vé của tôi`; order/ticket cards with match image/context, seat codes, status chip, total amount, order date, and per-ticket button `Xem vé`.
- **Key interactions**: card status helps distinguish pending/issued/rejected/expired; `Xem vé` opens SCREEN-010; empty state routes back to matches.
- **Exit**: SCREEN-010 or SCREEN-002.

**States**

| State | Stable Identifier | Visible Signal | Exit Condition |
|---|---|---|---|
| Empty | `orders-empty` | Copy `Bạn chưa có vé nào.`, CTA `Xem trận đang bán vé` | User opens matches or orders appear |
| Loading | `orders-loading` | Ticket card skeletons, `aria-busy="true"` | Fetch resolved -> Populated / Empty / Error |
| Populated | `orders-list` | Order cards, match context, statuses, total amount, `Xem vé` buttons | User opens ticket detail |
| Error | `orders-error` | Copy `Không thể tải lịch sử mua vé. Vui lòng thử lại.`, CTA `Thử lại` | Retry succeeds |

**Validation Behavior**

| Control | Rule | Trigger | Error Copy |
|---|---|---|---|
| `Xem vé` | ticket id exists and belongs to user | on click | `Không tìm thấy vé.` |

> Assumption: History search/filter is not required in Sprint v2.
> Validate: Product Owner confirms during Design review.
> Change trigger: If users need many orders, add date/status filters.

<!-- ID: SCREEN-010 -->
### SCREEN-010: Ticket Detail

- **Purpose**: Show issued QR/e-ticket with clear valid-entry signal and match/seat context.
- **FR / US / AC**: FR-009 / US-010 / AC-018, AC-035.
- **Layout**: e-ticket card with match name, venue/date, seat code, status chip, QR/e-ticket area, valid-entry banner, and optional `Đổi ghế` CTA when eligible.
- **Key interactions**: QR visible only for valid issued ticket; invalid/exchanged/scanned states replace QR with status explanation; exchange CTA opens SCREEN-012.
- **Exit**: SCREEN-012 or back to SCREEN-009.

**States**

| State | Stable Identifier | Visible Signal | Exit Condition |
|---|---|---|---|
| Empty | `ticket-empty` | Copy `Không tìm thấy vé.`, CTA `Quay lại lịch sử` | User returns to history |
| Loading | `ticket-loading` | E-ticket/QR skeleton, `aria-busy="true"` | Fetch resolved -> Populated / Error |
| Populated | `ticket-detail` | E-ticket styled card, QR visible, `Vé hợp lệ để vào cổng` signal | Ticket becomes scanned/exchanged/cancelled -> Error/invalid variant |
| Error | `ticket-invalid-error` | Copy `Vé này không còn hiệu lực để vào cổng.`, QR hidden/disabled | User returns to history |

**Validation Behavior**

| Control | Rule | Trigger | Error Copy |
|---|---|---|---|
| QR display | ticket status must be `ISSUED` and not scanned/exchanged/cancelled | on load/status refresh | `Vé này không còn hiệu lực để vào cổng.` |
| Exchange CTA | visible only for eligible issued ticket | on render / click | `Vé này không đủ điều kiện đổi ghế.` |

> Assumption: QR graphic generation/format remains implementation-owned; design only requires visible QR area and validity state.
> Validate: Architecture confirms QR rendering contract.
> Change trigger: If QR contains time-limited token, add refresh/expired-token states.

<!-- ID: SCREEN-011 -->
### SCREEN-011: Scan Status Result

- **Purpose**: Provide a simple observable result for the API-driven scan status update.
- **FR / US / AC**: FR-010 / US-011 / AC-019, AC-020.
- **Layout**: compact result panel with ticket id, match, seat, status chip, and clear success/error copy.
- **Key interactions**: scan consumer submits ticket token; result panel displays accepted/rejected state; no full scanner app UX in Sprint v2.
- **Exit**: scanner/API consumer returns to scan input or closes result.

**States**

| State | Stable Identifier | Visible Signal | Exit Condition |
|---|---|---|---|
| Empty | `scan-empty` | Copy `Chưa có dữ liệu quét vé.`, no ticket status shown | Scan request starts -> Loading |
| Loading | `scan-loading` | Copy `Đang kiểm tra vé...`, `aria-busy="true"` | Scan resolves -> Populated / Error |
| Populated | `scan-success` | Success chip, copy `Vé hợp lệ. Đã cập nhật trạng thái đã quét.` | Operator starts next scan |
| Error | `scan-error` | Error chip, copy `Vé đã được quét trước đó.`, QR/ticket rejected | Operator starts next scan |

**Validation Behavior**

| Control | Rule | Trigger | Error Copy |
|---|---|---|---|
| Scan result | only `ISSUED` tickets can transition to scanned | on scan submit | `Vé đã được quét trước đó.` |
| Invalid/cancelled ticket | ticket must be active and valid | on scan submit | `Vé này không còn hiệu lực để vào cổng.` |

> Assumption: Sprint v2 keeps scan as an API/result surface, not a full gate scanner app.
> Validate: Product Owner confirms before Plan.
> Change trigger: If scanner app UX enters scope, add camera permission, scan input, retry, and offline states.

<!-- ID: SCREEN-012 -->
### SCREEN-012: Seat Exchange

- **Purpose**: Let user exchange an issued ticket to an available equal-or-higher priced seat.
- **FR / US / AC**: FR-011, FR-012 / US-012 / AC-021, AC-022, AC-023, AC-024.
- **Layout**: current ticket summary; eligible seat grid; price difference panel; status legend; CTA `Tiếp tục đổi ghế`; old-ticket validity note.
- **Key interactions**: select eligible seat; cheaper/unavailable seat is blocked; continue routes to SCREEN-004 for manual confirmation when needed.
- **Exit**: SCREEN-004 for exchange payment/confirmation or SCREEN-010 when cancelled.

**States**

| State | Stable Identifier | Visible Signal | Exit Condition |
|---|---|---|---|
| Empty | `exchange-empty` | Copy `Không có ghế phù hợp để đổi.`, current ticket summary remains visible | Eligible seats become available or user returns |
| Loading | `exchange-loading` | Seat grid skeleton, disabled CTA, `aria-busy="true"` | Fetch resolved -> Populated / Empty / Error |
| Populated | `exchange-seat-grid` | Eligible seat cards, price difference panel, CTA `Tiếp tục đổi ghế` enabled after valid selection | Continue -> SCREEN-004 |
| Error | `exchange-error` | Copy `Chỉ được đổi sang ghế có giá bằng hoặc cao hơn.`, selected invalid seat cleared | User selects eligible seat |

**Validation Behavior**

| Control | Rule | Trigger | Error Copy |
|---|---|---|---|
| Replacement seat | must be available and equal-or-higher priced | on click / continue | `Chỉ được đổi sang ghế có giá bằng hoặc cao hơn.` |
| Continue exchange | requires one eligible selected seat | on click | `Chọn ghế hợp lệ để tiếp tục đổi vé.` |
| Existing ticket | must remain issued and exchange-eligible | on load / continue | `Vé này không đủ điều kiện đổi ghế.` |

> Assumption: Original ticket remains valid until admin confirms the exchange, matching Product BR-007.
> Validate: Architecture confirms exchange state handling.
> Change trigger: If instant exchange without admin confirmation is introduced, update checkout/pending flow coverage.

<!-- ID: DS-COMP-001 -->
### DS-COMP-001: Seat Chip

- **Purpose**: Represents one concrete seat code and its current availability/selectability state.
- **Props / Variants**: `available`, `selected`, `held`, `issued`, `unavailable`, `vip`, `disabled`.
- **Behavior**: click toggles only available seats; selected state updates sticky summary; disabled states ignore click and expose reason to screen reader.
- **States covered**: default, hover, focus, active, selected, disabled, error/unavailable.
- **Accessibility**: `button` role where interactive; `aria-pressed` for selected; `aria-disabled` for unavailable; visible focus ring.
- **Tokens consumed**: primary teal for selected, amber for held, slate for issued/unavailable, 8px radius.
- **Stable identifier hook**: `seat-chip-{seatCode}`.
- **Used by screens**: SCREEN-003, SCREEN-012.

<!-- ID: DS-COMP-002 -->
### DS-COMP-002: Countdown Banner

- **Purpose**: Shows remaining time for checkout hold or admin confirmation deadline.
- **Props / Variants**: `hold`, `pending-admin`, `expired`, `warning`.
- **Behavior**: visible time text updates at least once per second; expired variant swaps to error copy and disables dependent action.
- **States covered**: normal, warning under 2 minutes, expired, loading.
- **Accessibility**: `aria-live="polite"` for minute/threshold changes; avoid announcing every second.
- **Tokens consumed**: amber accent, red error, status icon.
- **Stable identifier hook**: `countdown-banner`.
- **Used by screens**: SCREEN-004, SCREEN-005, SCREEN-008.

<!-- ID: DS-COMP-003 -->
### DS-COMP-003: Ticket QR Card

- **Purpose**: Displays QR/e-ticket with match, seat, and validity status.
- **Props / Variants**: `issued`, `scanned`, `invalid`, `exchanged`, `loading`.
- **Behavior**: QR area visible for issued valid tickets; invalid variants hide/disable QR and show exact reason copy.
- **States covered**: loading skeleton, valid QR, invalid panel, scanned panel.
- **Accessibility**: QR region labeled `QR vé vào cổng`; text fallback includes ticket id and seat code.
- **Tokens consumed**: surface card, success/error status colors, 8px radius.
- **Stable identifier hook**: `ticket-qr-card`.
- **Used by screens**: SCREEN-010, SCREEN-011.

<!-- ID: DS-COMP-004 -->
### DS-COMP-004: Admin Data Table

- **Purpose**: Dense admin table for matches, inventory, and confirmation queues.
- **Props / Variants**: sortable columns, status filters, row actions, side-panel detail, empty/loading/error states.
- **Behavior**: row actions stay right-aligned; primary action visually prioritized; loading preserves table dimensions to prevent layout shift.
- **States covered**: empty, loading, populated, error, row selected, action disabled.
- **Accessibility**: semantic table; visible focus for row actions; buttons have descriptive labels.
- **Tokens consumed**: slate text, subtle borders, status chips, 8px radius.
- **Stable identifier hook**: `admin-data-table`.
- **Used by screens**: SCREEN-006, SCREEN-007, SCREEN-008.

<!-- ID: DS-COMP-005 -->
### DS-COMP-005: Status Chip

- **Purpose**: Consistent visual status for match, order, seat, payment, and ticket states.
- **Props / Variants**: `open`, `soldOut`, `cancelled`, `closed`, `held`, `pending`, `issued`, `scanned`, `rejected`, `expired`, `exchanged`, `demo`.
- **Behavior**: status labels are short, color-coded, and never rely on color alone; chip text is visible in table/card contexts.
- **States covered**: default, compact, high-emphasis, disabled.
- **Accessibility**: text label always present; contrast meets practical AA baseline.
- **Tokens consumed**: primary/success/amber/error/slate colors.
- **Stable identifier hook**: `status-chip-{status}`.
- **Used by screens**: SCREEN-002 through SCREEN-012.

## Removed

### Self-Review Checklist

- [x] `PROP-1`: Quality Contract refs satisfied: `DOC-1`, `DOC-2`, `DOC-3`, `LINK-1`, `LINK-2`, `ORB-1`, `DES-1`, `DES-2`
- [x] `PROP-2`: Frontmatter required keys all present and well-formed
- [x] `PROP-3`: `status` is DRAFT and `applied_to_living: false`
- [x] `PROP-4`: `version` matches `v2`
- [x] `PROP-5`: Updated items start with ID anchors
- [x] `PROP-17`: Design proposal contains only `DESIGN-OVERVIEW`, `SCREEN`, and `DS-COMP` prefixes
- [x] `DES-1`: Sprint-v2 affected Must FRs include full state coverage, exact copy, validation behavior, and FR / US mapping
- [x] `DES-2`: Each state includes stable identifier, visible signal, and exit condition
