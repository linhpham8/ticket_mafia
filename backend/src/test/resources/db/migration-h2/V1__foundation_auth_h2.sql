CREATE TABLE users (
  id UUID DEFAULT RANDOM_UUID() PRIMARY KEY,
  identifier VARCHAR(255) NOT NULL UNIQUE,
  identifier_type VARCHAR(20) NOT NULL CHECK (identifier_type IN ('EMAIL','PHONE')),
  role VARCHAR(20) NOT NULL DEFAULT 'CUSTOMER' CHECK (role IN ('CUSTOMER','ADMIN')),
  status VARCHAR(20) NOT NULL DEFAULT 'ACTIVE' CHECK (status IN ('ACTIVE','DISABLED')),
  created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);
CREATE INDEX idx_users_identifier ON users(identifier);

CREATE TABLE otp_challenges (
  id UUID DEFAULT RANDOM_UUID() PRIMARY KEY,
  identifier VARCHAR(255) NOT NULL,
  identifier_type VARCHAR(20) NOT NULL CHECK (identifier_type IN ('EMAIL','PHONE')),
  otp_code VARCHAR(8) NOT NULL,
  expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
  consumed_at TIMESTAMP WITH TIME ZONE NULL,
  attempt_count INTEGER NOT NULL DEFAULT 0,
  created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE TABLE sessions (
  id UUID DEFAULT RANDOM_UUID() PRIMARY KEY,
  user_id UUID NOT NULL REFERENCES users(id),
  access_token VARCHAR(80) NOT NULL UNIQUE,
  expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
  last_seen_at TIMESTAMP WITH TIME ZONE NOT NULL,
  created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE TABLE idempotency_records (
  id UUID DEFAULT RANDOM_UUID() PRIMARY KEY,
  scope VARCHAR(80) NOT NULL,
  idempotency_key VARCHAR(120) NOT NULL,
  user_id UUID NULL REFERENCES users(id),
  request_hash VARCHAR(128) NOT NULL,
  resource_id UUID NULL,
  response_status INTEGER NULL,
  created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
  expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
  UNIQUE(scope, idempotency_key)
);

CREATE TABLE audit_logs (
  id UUID DEFAULT RANDOM_UUID() PRIMARY KEY,
  actor_user_id UUID NULL REFERENCES users(id),
  action VARCHAR(80) NOT NULL,
  resource_type VARCHAR(60) NOT NULL,
  resource_id UUID NOT NULL,
  result VARCHAR(20) NOT NULL CHECK (result IN ('SUCCESS','FAILURE')),
  request_id VARCHAR(120) NULL,
  trace_id VARCHAR(120) NULL,
  metadata JSON NOT NULL DEFAULT '{}',
  created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE TABLE matches (
  id UUID DEFAULT RANDOM_UUID() PRIMARY KEY,
  name VARCHAR(120) NOT NULL,
  starts_at TIMESTAMP WITH TIME ZONE NULL,
  status VARCHAR(20) NOT NULL CHECK (status IN ('OPEN_FOR_SALE','SOLD_OUT','CANCELLED','CLOSED')),
  created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
  UNIQUE(name, starts_at)
);
CREATE INDEX idx_matches_status_starts_at ON matches(status, starts_at DESC);

CREATE TABLE seats (
  id UUID DEFAULT RANDOM_UUID() PRIMARY KEY,
  match_id UUID NOT NULL REFERENCES matches(id) ON DELETE CASCADE,
  section_code VARCHAR(10) NOT NULL CHECK (section_code IN ('A','B','C','D')),
  floor_no INTEGER NOT NULL CHECK (floor_no IN (1,2)),
  seat_code VARCHAR(40) NOT NULL,
  is_vip BOOLEAN NOT NULL DEFAULT FALSE,
  status VARCHAR(30) NOT NULL DEFAULT 'AVAILABLE'
    CHECK (status IN ('AVAILABLE','HELD','PENDING_ADMIN_CONFIRM','ISSUED','USED_SCANNED','RELEASED_EXPIRED','REJECTED_CANCELLED','EXCHANGED')),
  active_order_item_id UUID NULL,
  created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
  UNIQUE(match_id, seat_code)
);
CREATE INDEX idx_seats_match_status ON seats(match_id, status);
CREATE UNIQUE INDEX uq_seats_generation_slice ON seats(match_id, section_code, floor_no, is_vip, seat_code);

CREATE TABLE price_versions (
  id UUID DEFAULT RANDOM_UUID() PRIMARY KEY,
  match_id UUID NOT NULL REFERENCES matches(id) ON DELETE CASCADE,
  section_code VARCHAR(10) NOT NULL CHECK (section_code IN ('A','B','C','D')),
  floor_no INTEGER NOT NULL CHECK (floor_no IN (1,2)),
  is_vip BOOLEAN NOT NULL DEFAULT FALSE,
  price_vnd NUMERIC(14,2) NOT NULL CHECK (price_vnd > 0),
  active_from TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
  created_by UUID NOT NULL REFERENCES users(id),
  created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);
CREATE INDEX idx_price_versions_lookup ON price_versions(match_id, section_code, floor_no, is_vip, active_from DESC);

CREATE TABLE payment_qr_configs (
  id UUID DEFAULT RANDOM_UUID() PRIMARY KEY,
  name VARCHAR(80) NOT NULL,
  qr_asset_ref VARCHAR(2048) NOT NULL,
  is_default BOOLEAN NOT NULL DEFAULT FALSE,
  created_by UUID NOT NULL REFERENCES users(id),
  created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE TABLE orders (
  id UUID DEFAULT RANDOM_UUID() PRIMARY KEY,
  user_id UUID NOT NULL REFERENCES users(id),
  match_id UUID NOT NULL REFERENCES matches(id),
  type VARCHAR(20) NOT NULL DEFAULT 'PURCHASE' CHECK (type IN ('PURCHASE','EXCHANGE')),
  status VARCHAR(30) NOT NULL CHECK (status IN ('HELD','PENDING_ADMIN_CONFIRM','ISSUED','REJECTED','CANCELLED','EXPIRED')),
  total_amount_vnd NUMERIC(14,2) NOT NULL CHECK (total_amount_vnd >= 0),
  hold_expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
  admin_confirm_expires_at TIMESTAMP WITH TIME ZONE NULL,
  original_ticket_id UUID NULL,
  created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);
CREATE INDEX idx_orders_user_created ON orders(user_id, created_at DESC);
CREATE INDEX idx_orders_status_expires ON orders(status, hold_expires_at, admin_confirm_expires_at);

CREATE TABLE order_items (
  id UUID DEFAULT RANDOM_UUID() PRIMARY KEY,
  order_id UUID NOT NULL REFERENCES orders(id) ON DELETE CASCADE,
  seat_id UUID NOT NULL REFERENCES seats(id),
  price_snapshot_vnd NUMERIC(14,2) NOT NULL CHECK (price_snapshot_vnd >= 0),
  active BOOLEAN NOT NULL DEFAULT TRUE,
  created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
  UNIQUE(order_id, seat_id)
);

CREATE TABLE tickets (
  id UUID DEFAULT RANDOM_UUID() PRIMARY KEY,
  order_id UUID NOT NULL REFERENCES orders(id),
  seat_id UUID NOT NULL REFERENCES seats(id),
  user_id UUID NOT NULL REFERENCES users(id),
  status VARCHAR(30) NOT NULL CHECK (status IN ('ISSUED','USED_SCANNED','CANCELLED','EXCHANGED')),
  qr_token_hash VARCHAR(128) NOT NULL UNIQUE,
  issued_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
  scanned_at TIMESTAMP WITH TIME ZONE NULL,
  exchanged_to_ticket_id UUID NULL,
  created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);
