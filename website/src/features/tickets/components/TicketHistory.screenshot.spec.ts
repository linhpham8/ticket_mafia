import { expect, test } from "@playwright/test";
import { mkdir } from "node:fs/promises";
import path from "node:path";

const outputDir = path.resolve("../docs/sprint-v1/implementation/screenshots/tg-1-5");

test.beforeAll(async () => {
  await mkdir(outputDir, { recursive: true });
});

test("captures SCREEN-009 Purchase History populated state", async ({ page }) => {
  await routeHistory(page, "ISSUED");
  await page.goto("/tickets-screenshot-harness.html");
  await expect(page.getByTestId("ticket-history-list")).toBeVisible();
  await page.screenshot({ path: path.join(outputDir, "screen-009-populated.png"), fullPage: true });
});

test("captures SCREEN-009 Purchase History empty state", async ({ page }) => {
  await page.route("**/api/v1/orders", async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({ data: [], meta: { nextCursor: null } })
    });
  });
  await page.goto("/tickets-screenshot-harness.html");
  await expect(page.getByTestId("ticket-history-empty")).toBeVisible();
  await page.screenshot({ path: path.join(outputDir, "screen-009-empty.png"), fullPage: true });
});

test("captures SCREEN-010 Ticket Detail issued QR state", async ({ page }) => {
  await routeHistory(page, "ISSUED");
  await routeDetail(page, "ISSUED", "tk_v1_signedopaque");
  await page.goto("/tickets-screenshot-harness.html");
  await page.getByRole("button", { name: "A-T1-001 · ISSUED" }).click();
  await expect(page.getByTestId("ticket-qr-card")).toBeVisible();
  await page.screenshot({ path: path.join(outputDir, "screen-010-issued-qr.png"), fullPage: true });
});

test("captures SCREEN-010 Ticket Detail invalid state", async ({ page }) => {
  await routeHistory(page, "CANCELLED");
  await routeDetail(page, "CANCELLED", null);
  await page.goto("/tickets-screenshot-harness.html");
  await page.getByRole("button", { name: "A-T1-001 · CANCELLED" }).click();
  await expect(page.getByRole("alert")).toContainText("không còn hợp lệ");
  await page.screenshot({ path: path.join(outputDir, "screen-010-invalid.png"), fullPage: true });
});

async function routeHistory(page: import("@playwright/test").Page, ticketStatus: string) {
  await page.route("**/api/v1/orders", async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({
        data: [{
          orderId: "order-1",
          status: ticketStatus === "ISSUED" ? "ISSUED" : "REJECTED",
          matchName: "Hanoi FC vs Saigon FC",
          totalAmountVnd: 120000,
          createdAt: "2026-07-01T12:00:00Z",
          tickets: [{ ticketId: "ticket-1", status: ticketStatus, seatCode: "A-T1-001" }]
        }],
        meta: { nextCursor: null }
      })
    });
  });
}

async function routeDetail(page: import("@playwright/test").Page, status: string, qrToken: string | null) {
  await page.route("**/api/v1/tickets/ticket-1", async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({
        data: {
          ticketId: "ticket-1",
          match: { id: "match-1", name: "Hanoi FC vs Saigon FC" },
          seatCode: "A-T1-001",
          status,
          qrToken,
          issuedAt: "2026-07-01T12:00:00Z",
          scannedAt: null
        }
      })
    });
  });
}
