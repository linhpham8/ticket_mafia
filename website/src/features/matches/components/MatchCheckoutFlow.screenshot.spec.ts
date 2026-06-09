import { expect, test } from "@playwright/test";
import { mkdir } from "node:fs/promises";
import path from "node:path";

const outputDir = path.resolve("../docs/sprint-v1/implementation/screenshots/tg-1-3");

test.beforeAll(async () => {
  await mkdir(outputDir, { recursive: true });
});

test.beforeEach(async ({ page }) => {
  await page.route("**/api/v1/matches", async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({
        data: [{ id: "match-1", name: "Hanoi FC vs Saigon FC", startsAt: "2026-07-01T12:00:00Z", status: "OPEN_FOR_SALE" }],
        meta: { nextCursor: null }
      })
    });
  });
  await page.route("**/api/v1/matches/match-1/seats", async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({
        data: {
          match: { id: "match-1", status: "OPEN_FOR_SALE" },
          seats: [
            { id: "seat-1", seatCode: "A-T1-001", sectionCode: "A", floorNo: 1, isVip: false, status: "AVAILABLE", priceVnd: 120000 },
            { id: "seat-2", seatCode: "A-T1-002", sectionCode: "A", floorNo: 1, isVip: false, status: "HELD", priceVnd: 120000 }
          ]
        }
      })
    });
  });
  await page.route("**/api/v1/orders/checkout", async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({
        data: {
          orderId: "order-1",
          status: "HELD",
          holdExpiresAt: "2026-07-01T12:10:00Z",
          totalAmountVnd: 120000,
          items: [{ seatId: "seat-1", seatCode: "A-T1-001", priceSnapshotVnd: 120000 }],
          paymentQr: { assetRef: "asset://payment/default" }
        }
      })
    });
  });
  await page.route("**/api/v1/orders/order-1/payment-completed", async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({
        data: {
          orderId: "order-1",
          status: "PENDING_ADMIN_CONFIRM",
          adminConfirmExpiresAt: "2026-07-01T12:20:00Z"
        }
      })
    });
  });
});

test("captures SCREEN-002 Match List populated state", async ({ page }) => {
  await page.goto("/matches-screenshot-harness.html");
  await expect(page.getByTestId("matches-list")).toBeVisible();
  await page.screenshot({ path: path.join(outputDir, "screen-002-populated.png"), fullPage: true });
});

for (const state of ["matches-loading", "matches-empty", "matches-error"]) {
  test(`captures SCREEN-002 Match List ${state} state`, async ({ page }) => {
    await page.goto(`/matches-screenshot-harness.html?state=${state}`);
    await expect(page.getByTestId(state)).toBeVisible();
    await page.screenshot({ path: path.join(outputDir, `screen-002-${state}.png`), fullPage: true });
  });
}

test("captures SCREEN-003 Seat Selection populated state", async ({ page }) => {
  await page.goto("/matches-screenshot-harness.html");
  await page.getByRole("button", { name: "Chọn ghế" }).click();
  await expect(page.getByTestId("seat-map-grid")).toBeVisible();
  await page.screenshot({ path: path.join(outputDir, "screen-003-populated.png"), fullPage: true });
});

for (const state of ["seat-map-loading", "seat-map-empty", "seat-map-error"]) {
  test(`captures SCREEN-003 Seat Selection ${state} state`, async ({ page }) => {
    await page.goto(`/matches-screenshot-harness.html?state=${state}`);
    await expect(page.getByTestId(state)).toBeVisible();
    await page.screenshot({ path: path.join(outputDir, `screen-003-${state}.png`), fullPage: true });
  });
}

test("captures SCREEN-004 Checkout QR populated state", async ({ page }) => {
  await page.goto("/matches-screenshot-harness.html");
  await page.getByRole("button", { name: "Chọn ghế" }).click();
  await page.getByTestId("seat-A-T1-001").click();
  await page.getByRole("button", { name: "Thanh toán" }).click();
  await expect(page.getByTestId("checkout-qr")).toBeVisible();
  await page.screenshot({ path: path.join(outputDir, "screen-004-populated.png"), fullPage: true });
});

for (const state of ["checkout-empty", "checkout-loading", "checkout-expired-error"]) {
  test(`captures SCREEN-004 Checkout QR ${state} state`, async ({ page }) => {
    await page.goto(`/matches-screenshot-harness.html?state=${state}`);
    await expect(page.getByTestId(state)).toBeVisible();
    await page.screenshot({ path: path.join(outputDir, `screen-004-${state}.png`), fullPage: true });
  });
}

test("captures SCREEN-005 Pending Confirmation populated state", async ({ page }) => {
  await page.goto("/matches-screenshot-harness.html");
  await page.getByRole("button", { name: "Chọn ghế" }).click();
  await page.getByTestId("seat-A-T1-001").click();
  await page.getByRole("button", { name: "Thanh toán" }).click();
  await page.getByRole("button", { name: "Tôi đã chuyển khoản" }).click();
  await expect(page.getByTestId("pending-confirmation")).toBeVisible();
  await page.screenshot({ path: path.join(outputDir, "screen-005-populated.png"), fullPage: true });
});

for (const state of ["pending-empty", "pending-loading", "pending-expired-error"]) {
  test(`captures SCREEN-005 Pending Confirmation ${state} state`, async ({ page }) => {
    await page.goto(`/matches-screenshot-harness.html?state=${state}`);
    await expect(page.getByTestId(state)).toBeVisible();
    await page.screenshot({ path: path.join(outputDir, `screen-005-${state}.png`), fullPage: true });
  });
}
