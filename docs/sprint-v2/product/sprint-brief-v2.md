---
status: APPROVED
version: v2
sprint: 2
phase: product
sprint_id: sprint-v2
created: 2026-06-09
updated: 2026-06-09 11:42
approved_by: user
---

# Sprint Brief — Product v2

## 1. Scope Summary

Sprint v2 captures the UI and local runtime hardening work needed to make the existing `ticket_mafia` demo feel like a real football-ticket marketplace instead of a set of sparse white pages.

The sprint does not introduce new ticketing business lifecycle rules. It improves presentation and operability across the existing v1 flows: match discovery, seat selection, manual QR checkout, purchase history / e-ticket detail, admin match / inventory management, and admin payment confirmation.

## 2. Sprint Rationale

The v1 product flow is functionally complete, but the user and admin surfaces are not demo-ready: the match list, ticket detail, and admin pages do not communicate the ticketing domain strongly enough, and the user web can show a blank/loading experience when the local backend API is unavailable or unseeded.

Sprint v2 formalizes the UI polish and local API/runtime resilience already requested for the demo so that Product, Design, Architecture, Plan, Test, and Implement can pass through this scope cleanly before sprint-v3 starts.

## 3. Review Notes

- This sprint is UI/runtime polish over existing v1 epics, not a new product capability expansion.
- Local demo fallback data is in scope only to prevent blank match browsing during development/demo setup; real checkout and payment actions still require backend availability.
- Production traffic management, real payment gateway integration, scanner app UX, refunds, resale, and complex stadium map editing remain out of scope.

## Industry Lens Applied (PROD-5)

- Detected vertical: ticketing / football ticket sales
- Detection confidence: high
- Items surfaced: 0 [industry-standard] / 6 [common] / 0 [niche]
- Region-specific items global-only: 0 — none
- Cross-domain tension: yes — sprint-v2 keeps manual transfer checkout and local demo fallback behavior while improving ticket-marketplace presentation.
