-- Sprint: v1 | Feature: FR-001,NFR-003,NFR-004,NFR-005 | US: US-001 | Task Group: TG 1.1 Foundation and Auth
-- Contract: erd-v1.md ENT-001/ENT-009/ENT-010 plus TG 1.1 auth/session baseline migration
CREATE EXTENSION IF NOT EXISTS pgcrypto;

CREATE TABLE users (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  identifier VARCHAR(255) NOT NULL UNIQUE,
  identifier_type VARCHAR(20) NOT NULL CHECK (identifier_type IN ('EMAIL','PHONE')),
  role VARCHAR(20) NOT NULL DEFAULT 'CUSTOMER' CHECK (role IN ('CUSTOMER','ADMIN')),
  status VARCHAR(20) NOT NULL DEFAULT 'ACTIVE' CHECK (status IN ('ACTIVE','DISABLED')),
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX idx_users_identifier ON users(identifier);

CREATE TABLE otp_challenges (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  identifier VARCHAR(255) NOT NULL,
  identifier_type VARCHAR(20) NOT NULL CHECK (identifier_type IN ('EMAIL','PHONE')),
  otp_code VARCHAR(8) NOT NULL,
  expires_at TIMESTAMPTZ NOT NULL,
  consumed_at TIMESTAMPTZ NULL,
  attempt_count INTEGER NOT NULL DEFAULT 0,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX idx_otp_challenges_identifier_created ON otp_challenges(identifier, created_at DESC);

CREATE TABLE sessions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES users(id),
  access_token VARCHAR(80) NOT NULL UNIQUE,
  expires_at TIMESTAMPTZ NOT NULL,
  last_seen_at TIMESTAMPTZ NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX idx_sessions_access_token ON sessions(access_token);
CREATE INDEX idx_sessions_expires ON sessions(expires_at);

CREATE TABLE idempotency_records (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  scope VARCHAR(80) NOT NULL,
  idempotency_key VARCHAR(120) NOT NULL,
  user_id UUID NULL REFERENCES users(id),
  request_hash VARCHAR(128) NOT NULL,
  resource_id UUID NULL,
  response_status INTEGER NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  expires_at TIMESTAMPTZ NOT NULL,
  UNIQUE(scope, idempotency_key)
);
CREATE INDEX idx_idempotency_expires ON idempotency_records(expires_at);

CREATE TABLE audit_logs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  actor_user_id UUID NULL REFERENCES users(id),
  action VARCHAR(80) NOT NULL,
  resource_type VARCHAR(60) NOT NULL,
  resource_id UUID NOT NULL,
  result VARCHAR(20) NOT NULL CHECK (result IN ('SUCCESS','FAILURE')),
  request_id VARCHAR(120) NULL,
  trace_id VARCHAR(120) NULL,
  metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX idx_audit_resource ON audit_logs(resource_type, resource_id, created_at DESC);
CREATE INDEX idx_audit_actor_created ON audit_logs(actor_user_id, created_at DESC);

-- Sprint: v1 | Feature: FR-006,FR-007,BR-004,BR-008,NFR-004 | US: US-006,US-007 | Task Group: TG 1.2 Admin Match Inventory, Pricing, and QR
-- Contract: erd-v1.md ENT-002/ENT-003/ENT-006/ENT-007 plus SEQ-002 admin inventory transaction/audit path
CREATE TABLE matches (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name VARCHAR(120) NOT NULL,
  starts_at TIMESTAMPTZ NULL,
  status VARCHAR(20) NOT NULL CHECK (status IN ('OPEN_FOR_SALE','SOLD_OUT','CANCELLED','CLOSED')),
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  UNIQUE(name, starts_at)
);
CREATE INDEX idx_matches_status_starts_at ON matches(status, starts_at DESC);

CREATE TABLE seats (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  match_id UUID NOT NULL REFERENCES matches(id) ON DELETE CASCADE,
  section_code VARCHAR(10) NOT NULL CHECK (section_code IN ('A','B','C','D')),
  floor_no INTEGER NOT NULL CHECK (floor_no IN (1,2)),
  seat_code VARCHAR(40) NOT NULL,
  is_vip BOOLEAN NOT NULL DEFAULT FALSE,
  status VARCHAR(30) NOT NULL DEFAULT 'AVAILABLE'
    CHECK (status IN ('AVAILABLE','HELD','PENDING_ADMIN_CONFIRM','ISSUED','USED_SCANNED','RELEASED_EXPIRED','REJECTED_CANCELLED','EXCHANGED')),
  active_order_item_id UUID NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  UNIQUE(match_id, seat_code)
);
CREATE INDEX idx_seats_match_status ON seats(match_id, status);
CREATE UNIQUE INDEX uq_seats_generation_slice ON seats(match_id, section_code, floor_no, is_vip, seat_code);

CREATE TABLE price_versions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  match_id UUID NOT NULL REFERENCES matches(id) ON DELETE CASCADE,
  section_code VARCHAR(10) NOT NULL CHECK (section_code IN ('A','B','C','D')),
  floor_no INTEGER NOT NULL CHECK (floor_no IN (1,2)),
  is_vip BOOLEAN NOT NULL DEFAULT FALSE,
  price_vnd NUMERIC(14,2) NOT NULL CHECK (price_vnd > 0),
  active_from TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  created_by UUID NOT NULL REFERENCES users(id),
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX idx_price_versions_lookup ON price_versions(match_id, section_code, floor_no, is_vip, active_from DESC);

CREATE TABLE payment_qr_configs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name VARCHAR(80) NOT NULL,
  qr_asset_ref TEXT NOT NULL,
  is_default BOOLEAN NOT NULL DEFAULT FALSE,
  created_by UUID NOT NULL REFERENCES users(id),
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE UNIQUE INDEX uq_payment_qr_one_default ON payment_qr_configs(is_default) WHERE is_default = TRUE;

-- Sprint: v1 | Feature: FR-004,FR-005,BR-002,BR-003,BR-004,NFR-002 | US: US-004,US-005 | Task Group: TG 1.3 User Browse, Seat Selection, Checkout Hold, and Payment Completion
-- Contract: erd-v1.md ENT-004/ENT-005; sequence-v1.md SEQ-003 checkout hold and payment completion
CREATE TABLE orders (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES users(id),
  match_id UUID NOT NULL REFERENCES matches(id),
  type VARCHAR(20) NOT NULL DEFAULT 'PURCHASE' CHECK (type IN ('PURCHASE','EXCHANGE')),
  status VARCHAR(30) NOT NULL CHECK (status IN ('HELD','PENDING_ADMIN_CONFIRM','ISSUED','REJECTED','CANCELLED','EXPIRED')),
  total_amount_vnd NUMERIC(14,2) NOT NULL CHECK (total_amount_vnd >= 0),
  hold_expires_at TIMESTAMPTZ NOT NULL,
  admin_confirm_expires_at TIMESTAMPTZ NULL,
  original_ticket_id UUID NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX idx_orders_user_created ON orders(user_id, created_at DESC);
CREATE INDEX idx_orders_status_expires ON orders(status, hold_expires_at, admin_confirm_expires_at);

CREATE TABLE order_items (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  order_id UUID NOT NULL REFERENCES orders(id) ON DELETE CASCADE,
  seat_id UUID NOT NULL REFERENCES seats(id),
  price_snapshot_vnd NUMERIC(14,2) NOT NULL CHECK (price_snapshot_vnd >= 0),
  active BOOLEAN NOT NULL DEFAULT TRUE,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  UNIQUE(order_id, seat_id)
);
CREATE UNIQUE INDEX uq_active_seat_order_item ON order_items(seat_id) WHERE active = TRUE;

ALTER TABLE seats
  ADD CONSTRAINT fk_seats_active_order_item
  FOREIGN KEY (active_order_item_id) REFERENCES order_items(id);

-- Sprint: v1 | Feature: FR-008,BR-005,NFR-004 | US: US-008 | Task Group: TG 1.4 Admin Payment Confirmation and Audit
-- Contract: erd-v1.md ENT-008; sequence-v1.md SEQ-004 ticket issuance after admin confirmation
CREATE TABLE tickets (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  order_id UUID NOT NULL REFERENCES orders(id),
  seat_id UUID NOT NULL REFERENCES seats(id),
  user_id UUID NOT NULL REFERENCES users(id),
  status VARCHAR(30) NOT NULL CHECK (status IN ('ISSUED','USED_SCANNED','CANCELLED','EXCHANGED')),
  qr_token_hash VARCHAR(128) NOT NULL UNIQUE,
  issued_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  scanned_at TIMESTAMPTZ NULL,
  exchanged_to_ticket_id UUID NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX idx_tickets_user_created ON tickets(user_id, created_at DESC);
CREATE INDEX idx_tickets_status ON tickets(status);
