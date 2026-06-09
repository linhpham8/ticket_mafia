---
status: APPROVED
version: v2
sprint: 2
phase: architecture
sprint_id: sprint-v2
created: 2026-06-09
updated: 2026-06-09 14:03
approved_by: user
applied_to_living: false
---

# API Specifications Proposal — Sprint v2

## New

## Updated

<!-- ID: API-003 -->
### API-003: `GET /api/v1/matches`

| Attribute | Value |
|---|---|
| Auth | Optional |
| Roles | public/customer |
| Idempotent | Yes |
| Rate limit | demo baseline |

#### Query Parameters
| Field | Type | Required | Validation | Default | Example |
|---|---|---|---|---|---|
| `status` | enum | No | `OPEN_FOR_SALE` only for public list | `OPEN_FOR_SALE` | `"OPEN_FOR_SALE"` |
| `query` | string | No | max 80 chars; matches name/team/venue if implemented | — | `"Mexico"` |
| `cursor` | string | No | opaque cursor | — | `"eyJpZCI6..."` |
| `limit` | integer | No | 1-50 | 20 | `20` |

#### Response Body Schema
| Field | Type | Always Present | Description |
|---|---|---|---|
| `data[]` | array | Yes | match rows |
| `data[].id` | UUID | Yes | match ID |
| `data[].name` | string | Yes | match display name |
| `data[].homeTeam` | string/null | Yes | optional home/team A label for marketplace card |
| `data[].awayTeam` | string/null | Yes | optional away/team B label for marketplace card |
| `data[].venueName` | string/null | Yes | optional venue label |
| `data[].city` | string/null | Yes | optional city label |
| `data[].heroImageUrl` | string/null | Yes | optional event media URL/reference |
| `data[].startsAt` | ISO UTC datetime/null | Yes | scheduled start time |
| `data[].status` | enum | Yes | sale status |
| `data[].availableSeatCount` | integer | Yes | seats currently available for sale; `0` when none |
| `data[].startingPriceVnd` | decimal/null | Yes | minimum active price for available seats |
| `meta.nextCursor` | string/null | Yes | next page cursor |

#### Errors
| Status | Code | Condition | Details |
|---|---|---|---|
| 400 | `MATCH_QUERY_INVALID` | invalid status/query/cursor/limit | query field |
| 401 | `AUTH_UNAUTHORIZED` | N/A for public endpoint | not used |
| 403 | `AUTH_FORBIDDEN` | N/A for public endpoint | not used |
| 404 | `MATCH_NOT_FOUND` | N/A for collection | not used |
| 409 | `MATCH_STATE_CONFLICT` | N/A for read | not used |
| 422 | `VALIDATION_ERROR` | query schema invalid | field-level details |
| 429 | `RATE_LIMITED` | rate exceeded | retry after policy |
| 500 | `INTERNAL_ERROR` | unexpected server error | request/trace IDs |

> **Assumption**: Local fallback data for this endpoint is implemented in User Website only; backend still returns authoritative rows or errors.

<!-- ID: API-004 -->
### API-004: `GET /api/v1/matches/{matchId}/seats`

| Attribute | Value |
|---|---|
| Auth | Optional |
| Roles | public/customer |
| Idempotent | Yes |
| Rate limit | demo baseline |

#### Path / Query Parameters
| Field | Type | Required | Validation | Default | Example |
|---|---|---|---|---|---|
| `matchId` | UUID | Yes | existing match | — | `"550e8400-e29b-41d4-a716-446655440000"` |
| `section` | enum | No | A/B/C/D | all | `"A"` |
| `floorNo` | integer | No | 1 or 2 | all | `1` |

#### Response Body Schema
| Field | Type | Always Present | Description |
|---|---|---|---|
| `data.match.id` | UUID | Yes | match ID |
| `data.match.name` | string | Yes | match display name |
| `data.match.homeTeam` | string/null | Yes | optional home/team A label |
| `data.match.awayTeam` | string/null | Yes | optional away/team B label |
| `data.match.venueName` | string/null | Yes | optional venue label |
| `data.match.startsAt` | ISO UTC datetime/null | Yes | scheduled start time |
| `data.match.status` | enum | Yes | match status |
| `data.summary.availableSeatCount` | integer | Yes | currently available seats in response scope |
| `data.summary.startingPriceVnd` | decimal/null | Yes | minimum active price in response scope |
| `data.seats[]` | array | Yes | seat rows |
| `data.seats[].id` | UUID | Yes | seat ID |
| `data.seats[].seatCode` | string | Yes | concrete seat code |
| `data.seats[].sectionCode` | string | Yes | A/B/C/D |
| `data.seats[].floorNo` | integer | Yes | floor number |
| `data.seats[].isVip` | boolean | Yes | VIP flag |
| `data.seats[].status` | enum | Yes | current seat state |
| `data.seats[].priceVnd` | decimal | Yes | current active price |

#### Errors
| Status | Code | Condition | Details |
|---|---|---|---|
| 400 | `SEAT_QUERY_INVALID` | invalid filter | field-level details |
| 401 | `AUTH_UNAUTHORIZED` | N/A for public read | not used |
| 403 | `AUTH_FORBIDDEN` | N/A for public read | not used |
| 404 | `MATCH_NOT_FOUND` | match ID not found | matchId |
| 409 | `MATCH_NOT_SELLABLE` | match not open for sale | current status |
| 422 | `VALIDATION_ERROR` | parameter schema invalid | field-level details |
| 429 | `RATE_LIMITED` | rate exceeded | retry after policy |
| 500 | `INTERNAL_ERROR` | unexpected server error | request/trace IDs |

> **Assumption**: Local fallback seat map is User Website display behavior only; API-005 must reject unknown/demo seat IDs because checkout requires backend-owned seat rows.

## Removed
