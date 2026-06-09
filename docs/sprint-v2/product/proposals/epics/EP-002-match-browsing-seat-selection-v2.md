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

# EP-002 Match Browsing And Seat Selection Proposal — Sprint v2

## New

<!-- ID: AC-025 -->
<!-- US: US-002 -->
**AC-025 (Happy Path)**
Given the user opens the match list and at least one match is available for sale, when the page loads, then the user sees a football-ticket marketplace layout with hero context, search/filter controls, date grouping, event cards, starting price, and a clear `Chọn ghế` action for each visible match.

<!-- ID: AC-026 -->
<!-- US: US-002 -->
**AC-026 (Local Demo Resilience)**
Given the local backend match API is unavailable or returns no useful demo data, when the user opens the match list in local development, then the page renders a useful demo match list within 2 seconds instead of staying blank or indefinitely loading.

<!-- ID: AC-027 -->
<!-- US: US-003 -->
**AC-027 (Happy Path)**
Given the user opens seat selection for an available match, when the seat map loads, then the user sees match banner context, starting price, available-seat summary, a seat status legend, visible seat cards with section/floor/VIP/price details, selected-seat count, and a sticky order summary.

<!-- ID: AC-028 -->
<!-- US: US-003 -->
**AC-028 (Local Demo Resilience)**
Given the local backend seat-map API is unavailable for the selected match, when the user enters seat selection in local development, then the page renders demo seats with accurate selected/unavailable behavior while real checkout still requires backend availability.

## Updated

## Removed

### Self-Review Checklist

- [x] Quality Contract refs satisfied: `DOC-1`, `DOC-2`, `DOC-3`, `LINK-1`, `LINK-2`, `ORB-1`, `PROD-1`, `PROD-4`
- [x] New AC items have `<!-- US: US-XXX -->` routing tags
- [x] Product Traceability Map remains valid because FR-to-US coverage is unchanged
