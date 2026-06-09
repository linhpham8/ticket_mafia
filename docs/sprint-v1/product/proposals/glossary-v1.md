---
status: APPROVED
version: v1
sprint: 1
phase: product
sprint_id: sprint-v1
created: 2026-06-08
updated: 2026-06-08 04:25
approved_by: user
approved_at: 2026-06-08T04:25:15Z
applied_to_living: true 8225310878e8569297961fcc0ec8090f2034566d (sealed 2026-06-08 22:21)
---

# Glossary Proposal — Sprint v1

## New

<!-- ID: GLOSS-001 -->
### GLOSS-001: Match

- **Definition**: A football match that admin can open for ticket sales.
- **Why it matters**: Tickets, seats, prices, and sale status are scoped by match.
- **Source / Related**: EP-004, BR-008.

<!-- ID: GLOSS-002 -->
### GLOSS-002: Section

- **Definition**: Stadium area such as A, B, C, or D.
- **Why it matters**: Seat generation and pricing are configured by section.
- **Source / Related**: EP-002, EP-004.

<!-- ID: GLOSS-003 -->
### GLOSS-003: Floor

- **Definition**: Seating level inside a stadium section; each section has 2 floors in v1.
- **Why it matters**: Seat code and price depend on section and floor.
- **Source / Related**: EP-002, EP-004.

<!-- ID: GLOSS-004 -->
### GLOSS-004: VIP Area

- **Definition**: Additional premium area under section A.
- **Why it matters**: VIP seats can have different pricing from normal section/floor seats.
- **Source / Related**: EP-002, EP-004.

<!-- ID: GLOSS-005 -->
### GLOSS-005: Seat Code

- **Definition**: Unique seat identifier generated from section, floor, and seat number.
- **Why it matters**: Users select concrete seats by code.
- **Source / Related**: EP-002, FR-003.

<!-- ID: GLOSS-006 -->
### GLOSS-006: Seat Hold

- **Definition**: Temporary reservation of selected seats for 10 minutes after user starts checkout.
- **Why it matters**: Prevents another user from selecting the same seats during payment.
- **Source / Related**: BR-002.

<!-- ID: GLOSS-007 -->
### GLOSS-007: Manual Transfer QR

- **Definition**: Admin-configured QR code shown to users for bank transfer payment.
- **Why it matters**: v1 does not integrate a payment gateway.
- **Source / Related**: EP-003, EP-004.

<!-- ID: GLOSS-008 -->
### GLOSS-008: Payment Completion

- **Definition**: User action that says they have completed bank transfer.
- **Why it matters**: Creates a pending admin confirmation record.
- **Source / Related**: EP-003, EP-005.

<!-- ID: GLOSS-009 -->
### GLOSS-009: Admin Confirmation

- **Definition**: Admin decision to confirm or reject a pending purchase after checking received money.
- **Why it matters**: Tickets are issued only after confirmation.
- **Source / Related**: EP-005, BR-005.

<!-- ID: GLOSS-010 -->
### GLOSS-010: E-ticket

- **Definition**: Issued digital ticket containing QR information for stadium entry.
- **Why it matters**: User needs it to enter the stadium.
- **Source / Related**: EP-006.

<!-- ID: GLOSS-011 -->
### GLOSS-011: Seat Exchange

- **Definition**: User flow that changes an issued ticket to another available equal-or-higher priced seat.
- **Why it matters**: Allows user seat changes while preserving price and confirmation rules.
- **Source / Related**: EP-007, BR-007.

<!-- ID: GLOSS-012 -->
### GLOSS-012: Price Snapshot

- **Definition**: Price captured on an order at checkout start.
- **Why it matters**: Later admin price updates must not affect existing orders.
- **Source / Related**: BR-004.

## Updated

## Removed

