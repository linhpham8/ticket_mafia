import { readFileSync } from "node:fs";
import { strict as assert } from "node:assert";

const matchesPage = readFileSync(new URL("../src/app/admin/matches/page.tsx", import.meta.url), "utf8");
const inventoryPage = readFileSync(
  new URL("../src/app/admin/matches/[matchId]/inventory/page.tsx", import.meta.url),
  "utf8",
);
const confirmationsPage = readFileSync(
  new URL("../src/app/admin/confirmations/page.tsx", import.meta.url),
  "utf8",
);

for (const id of [
  "admin-matches-empty",
  "admin-matches-loading",
  "admin-matches-table",
  "admin-matches-error",
]) {
  assert(matchesPage.includes(id), `SCREEN-006 state missing: ${id}`);
}

for (const id of [
  "admin-inventory-empty",
  "admin-inventory-loading",
  "admin-inventory-config",
  "admin-inventory-error",
]) {
  assert(inventoryPage.includes(id), `SCREEN-007 state missing: ${id}`);
}

for (const label of ["Ghế", "Giá", "QR thanh toán", "Chọn QR mặc định"]) {
  assert(inventoryPage.includes(label), `SCREEN-007 control missing: ${label}`);
}

for (const id of [
  "admin-confirm-empty",
  "admin-confirm-loading",
  "admin-confirm-table",
  "admin-confirm-error",
]) {
  assert(confirmationsPage.includes(id), `SCREEN-008 state missing: ${id}`);
}

for (const label of ["Lọc trạng thái", "Xác nhận đã nhận tiền", "Xác nhận đổi ghế", "Từ chối"]) {
  assert(confirmationsPage.includes(label), `SCREEN-008 control missing: ${label}`);
}
