INSERT INTO users(id, identifier, identifier_type, role, status, created_at, updated_at)
VALUES
  ('00000000-0000-4000-8000-000000000011', 'admin-tg14@example.test', 'EMAIL', 'ADMIN', 'ACTIVE', NOW(), NOW()),
  ('00000000-0000-4000-8000-000000000012', 'fan-tg14@example.test', 'EMAIL', 'CUSTOMER', 'ACTIVE', NOW(), NOW());

INSERT INTO sessions(id, user_id, access_token, expires_at, last_seen_at, created_at)
VALUES
  ('00000000-0000-4000-8000-000000000013', '00000000-0000-4000-8000-000000000011', 'tg14-admin-token', NOW() + INTERVAL '15 minutes', NOW(), NOW()),
  ('00000000-0000-4000-8000-000000000014', '00000000-0000-4000-8000-000000000012', 'tg14-customer-token', NOW() + INTERVAL '15 minutes', NOW(), NOW());

INSERT INTO matches(id, name, starts_at, status, created_at, updated_at)
VALUES ('00000000-0000-4000-8000-000000000021', 'TG 1.4 Smoke Match', NOW() + INTERVAL '1 day', 'OPEN_FOR_SALE', NOW(), NOW());

INSERT INTO seats(id, match_id, section_code, floor_no, seat_code, is_vip, status, created_at, updated_at)
VALUES
  ('00000000-0000-4000-8000-000000000031', '00000000-0000-4000-8000-000000000021', 'A', 1, 'A-T1-901', FALSE, 'PENDING_ADMIN_CONFIRM', NOW(), NOW()),
  ('00000000-0000-4000-8000-000000000032', '00000000-0000-4000-8000-000000000021', 'A', 1, 'A-T1-902', FALSE, 'PENDING_ADMIN_CONFIRM', NOW(), NOW());

INSERT INTO price_versions(id, match_id, section_code, floor_no, is_vip, price_vnd, active_from, created_by, created_at)
VALUES ('00000000-0000-4000-8000-000000000052', '00000000-0000-4000-8000-000000000021', 'A', 1, FALSE, 120000, NOW() - INTERVAL '1 minute', '00000000-0000-4000-8000-000000000011', NOW());

INSERT INTO payment_qr_configs(id, name, qr_asset_ref, is_default, created_by, created_at, updated_at)
VALUES ('00000000-0000-4000-8000-000000000051', 'TG14 Smoke QR', 'asset://payment/tg14-smoke', TRUE, '00000000-0000-4000-8000-000000000011', NOW(), NOW());

INSERT INTO orders(id, user_id, match_id, type, status, total_amount_vnd, hold_expires_at, admin_confirm_expires_at, created_at, updated_at)
VALUES (
  '00000000-0000-4000-8000-000000000041',
  '00000000-0000-4000-8000-000000000012',
  '00000000-0000-4000-8000-000000000021',
  'PURCHASE',
  'PENDING_ADMIN_CONFIRM',
  240000,
  NOW() + INTERVAL '10 minutes',
  NOW() + INTERVAL '10 minutes',
  NOW(),
  NOW()
);

INSERT INTO order_items(id, order_id, seat_id, price_snapshot_vnd, active, created_at)
VALUES
  ('00000000-0000-4000-8000-000000000061', '00000000-0000-4000-8000-000000000041', '00000000-0000-4000-8000-000000000031', 120000, TRUE, NOW()),
  ('00000000-0000-4000-8000-000000000062', '00000000-0000-4000-8000-000000000041', '00000000-0000-4000-8000-000000000032', 120000, TRUE, NOW());

UPDATE seats
SET active_order_item_id = CASE
  WHEN id = '00000000-0000-4000-8000-000000000031' THEN '00000000-0000-4000-8000-000000000061'::uuid
  WHEN id = '00000000-0000-4000-8000-000000000032' THEN '00000000-0000-4000-8000-000000000062'::uuid
END
WHERE id IN (
  '00000000-0000-4000-8000-000000000031',
  '00000000-0000-4000-8000-000000000032'
);
