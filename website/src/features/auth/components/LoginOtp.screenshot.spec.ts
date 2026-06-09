import { expect, test } from "@playwright/test";
import { mkdir } from "node:fs/promises";
import path from "node:path";

const outputDir = path.resolve("../docs/sprint-v1/implementation/screenshots/tg-1-1");

test.beforeAll(async () => {
  await mkdir(outputDir, { recursive: true });
});

test("captures SCREEN-001 Empty state", async ({ page }) => {
  await page.goto("/screenshot-harness.html");
  await expect(page.getByTestId("login-empty")).toBeVisible();
  await page.screenshot({ path: path.join(outputDir, "screen-001-empty.png"), fullPage: true });
});

test("captures SCREEN-001 Loading state", async ({ page }) => {
  await page.route("**/api/v1/auth/otp/request", () => new Promise(() => undefined));
  await page.goto("/screenshot-harness.html");
  await page.getByLabel("Email hoặc số điện thoại").fill("fan1@example.test");
  await page.getByRole("button", { name: "Tiếp tục" }).click();
  await expect(page.getByTestId("login-loading")).toBeVisible();
  await page.screenshot({ path: path.join(outputDir, "screen-001-loading.png"), fullPage: true });
});

test("captures SCREEN-001 Populated state", async ({ page }) => {
  await page.route("**/api/v1/auth/otp/request", async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({ data: { challengeId: "00000000-0000-0000-0000-000000000001" } })
    });
  });
  await page.goto("/screenshot-harness.html");
  await page.getByLabel("Email hoặc số điện thoại").fill("fan1@example.test");
  await page.getByRole("button", { name: "Tiếp tục" }).click();
  await expect(page.getByText("Demo OTP: 000000")).toBeVisible();
  await page.screenshot({ path: path.join(outputDir, "screen-001-populated.png"), fullPage: true });
});

test("captures SCREEN-001 Error state", async ({ page }) => {
  await page.route("**/api/v1/auth/otp/request", async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({ data: { challengeId: "00000000-0000-0000-0000-000000000001" } })
    });
  });
  await page.route("**/api/v1/auth/otp/verify", async (route) => {
    await route.fulfill({
      status: 401,
      contentType: "application/json",
      body: JSON.stringify({ error: { code: "AUTH_OTP_INVALID" } })
    });
  });
  await page.goto("/screenshot-harness.html");
  await page.getByLabel("Email hoặc số điện thoại").fill("fan1@example.test");
  await page.getByRole("button", { name: "Tiếp tục" }).click();
  await expect(page.getByText("Demo OTP: 000000")).toBeVisible();
  await page.getByLabel("Mã OTP").fill("111111");
  await page.getByRole("button", { name: "Tiếp tục" }).click();
  await expect(page.getByTestId("login-error")).toBeVisible();
  await page.screenshot({ path: path.join(outputDir, "screen-001-error.png"), fullPage: true });
});
