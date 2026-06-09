---
status: APPROVED
version: v2
sprint: 2
phase: product
sprint_id: sprint-v2
created: 2026-06-09
updated: 2026-06-09 11:42
approved_by: user
applied_to_living: false
---

# EP-003 Manual Transfer Checkout Proposal — Sprint v2

## New

<!-- ID: AC-029 -->
<!-- US: US-005 -->
**AC-029 (Happy Path)**
Given checkout has been created and the hold is still valid, when the user reaches the manual transfer step, then the page clearly shows the hold expiry time, QR payment area, selected seats, total amount, and a primary `Tôi đã chuyển khoản` action.

<!-- ID: AC-030 -->
<!-- US: US-005 -->
**AC-030 (Pending State)**
Given the user marks payment as completed successfully, when the order moves to pending admin confirmation, then the page shows a clear pending-confirmation status, the admin confirmation deadline, and a next action to view purchase history.

## Updated

## Removed

### Self-Review Checklist

- [x] Quality Contract refs satisfied: `DOC-1`, `DOC-2`, `DOC-3`, `LINK-1`, `LINK-2`, `ORB-1`, `PROD-1`, `PROD-4`
- [x] New AC items have `<!-- US: US-XXX -->` routing tags
- [x] Product Traceability Map remains valid because FR-to-US coverage is unchanged
