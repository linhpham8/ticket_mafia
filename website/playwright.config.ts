import { defineConfig, devices } from "@playwright/test";

export default defineConfig({
  testDir: ".",
  timeout: 30_000,
  use: {
    baseURL: "http://127.0.0.1:3100",
    browserName: "chromium",
    channel: "chrome",
    viewport: { width: 390, height: 844 },
    ...devices["Desktop Chrome"]
  },
  webServer: {
    command: "npx vite --host 127.0.0.1 --port 3100 --force",
    url: "http://127.0.0.1:3100/screenshot-harness.html",
    reuseExistingServer: true,
    timeout: 60_000
  }
});
