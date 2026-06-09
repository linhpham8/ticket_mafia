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

# ERD Proposal — Sprint v2

## New

## Updated

<!-- ID: ENT-002 -->
### ENT-002: Table `matches`

```sql
CREATE TABLE matches (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name VARCHAR(120) NOT NULL,
  home_team VARCHAR(80) NULL,
  away_team VARCHAR(80) NULL,
  venue_name VARCHAR(120) NULL,
  city VARCHAR(80) NULL,
  hero_image_url TEXT NULL,
  starts_at TIMESTAMPTZ NULL,
  status VARCHAR(20) NOT NULL CHECK (status IN ('OPEN_FOR_SALE','SOLD_OUT','CANCELLED','CLOSED')),
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX idx_matches_status_starts_at ON matches(status, starts_at DESC);
```

**Purpose**: Match sale unit and marketplace card context for user/admin UI.
**Lifecycle**: admin creates and changes status per BR-008; optional presentation fields can be empty during older demo seed data and should degrade to `name`.

> **Assumption**: Sprint v2 needs enough match metadata for marketplace-style cards, but not a separate teams/venues model.
> **Change trigger**: If production team/venue catalogs or reusable stadium media are required, add normalized `teams` / `venues` entities in a future sprint.

## Removed
