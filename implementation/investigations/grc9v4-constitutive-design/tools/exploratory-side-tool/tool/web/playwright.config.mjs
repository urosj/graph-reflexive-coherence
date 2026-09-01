import { defineConfig } from "@playwright/test";
import { fileURLToPath } from "node:url";

const outputDir = fileURLToPath(new URL("../generated/iteration7-playwright", import.meta.url));

export default defineConfig({
  testDir: "./e2e",
  outputDir,
  timeout: 45_000,
  expect: { timeout: 10_000 },
  reporter: "line",
  use: {
    baseURL: "http://127.0.0.1:4173",
    colorScheme: "light",
    reducedMotion: "reduce",
    trace: "retain-on-failure",
  },
  projects: [
    { name: "desktop", use: { viewport: { width: 1440, height: 900 } } },
    { name: "mobile", use: { viewport: { width: 390, height: 844 }, isMobile: true } },
  ],
});
