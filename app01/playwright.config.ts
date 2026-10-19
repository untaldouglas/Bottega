import { defineConfig } from "@playwright/test";
export default defineConfig({
  testDir: "tests/e2e",
  webServer: {
    command: "npm run dev -- --host 127.0.0.1 --port 5183",
    url: "http://127.0.0.1:5183",
    reuseExistingServer: false,
  },
  use: { baseURL: "http://127.0.0.1:5183", serviceWorkers: "block" },
  projects: [
    { name: "chromium", use: { browserName: "chromium" } },
    { name: "firefox", use: { browserName: "firefox" } },
    ...(process.env.E2E_ALL_BROWSERS === "1"
      ? [{ name: "webkit", use: { browserName: "webkit" as const } }]
      : []),
  ],
  reporter: "line",
});
