import { defineConfig, devices } from "@playwright/test";

// Runs against the full stack. Start it first with `docker compose up --build` from the repo root.
export default defineConfig({
  testDir: "./e2e",
  use: {
    baseURL: process.env.E2E_BASE_URL ?? "http://localhost:8080",
  },
  projects: [{ name: "chromium", use: { ...devices["Desktop Chrome"] } }],
});
