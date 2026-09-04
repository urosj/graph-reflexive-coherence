import { expect, test } from "@playwright/test";
import { fileURLToPath } from "node:url";

test("D11 claim and contract authority are reachable through the browser UX", async ({ page }, testInfo) => {
  await page.goto("/");
  await page.locator('[data-surface="successor"]').click();
  await expect(page.locator("#successor-workspace")).toBeVisible();
  await expect(page.locator("#successor-result-count")).toHaveText("69");

  await page.locator("#successor-search").fill("D11-C-CL-O-001");
  await page.locator("#successor-search").press("Enter");
  await expect(page.locator("#successor-selection h2")).toHaveText("D11-C-CL-O-001");
  await expect(page.locator("#successor-output-identity")).toContainText("reconstruction path");
  await expect(page.locator("#successor-source-refs")).toContainText("GRC9V4-D11-C-PROVENANCE-SUPPLEMENT-v1");
  await expect(page.locator("#successor-edge-refs .successor-edge").first()).toBeVisible();

  await page.locator("#successor-search").fill("D11-G9-EC-EXACT-OLD-PORT-MAP");
  await page.locator("#successor-search").press("Enter");
  await expect(page.locator("#successor-selection h2")).toHaveText("D11-G9-EC-EXACT-OLD-PORT-MAP");
  await expect(page.locator("#successor-output-identity")).toContainText("contract provenance");
  await expect(page.locator("#successor-trace-rows")).toContainText("accepted_bounded_GRC9V4_successor");

  const screenshot = fileURLToPath(
    new URL(`../../generated/iteration11-screenshots/${testInfo.project.name}-D11-provenance.png`, import.meta.url),
  );
  await page.screenshot({ path: screenshot, fullPage: true });
});

test("D11 debt and forward obligations remain distinct and bounded", async ({ page }, testInfo) => {
  await page.goto("/");
  await page.locator('[data-surface="successor"]').click();
  await page.locator('[data-successor-scope="D11-G9"]').click();
  await page.locator("#successor-kind").selectOption("debt_transformation");
  await expect(page.locator("#successor-result-count")).toHaveText("1");
  await page.locator("[data-successor-node]").click();
  await expect(page.locator("#successor-selection h2")).toContainText("CANONICAL-PORT-ALLOCATION");
  await expect(page.locator("#successor-trace-rows")).toContainText("resolved bounded");
  await expect(page.locator("#successor-trace-rows")).toContainText("forward verification routing");

  await page.locator("#successor-kind").selectOption("verification_obligation");
  await expect(page.locator("#successor-result-count")).toHaveText("4");
  await page.locator("#successor-search").fill("PAPER-THEN-SPECIFICATION");
  await page.locator("#successor-search").press("Enter");
  await expect(page.locator("#successor-selection h2")).toContainText("PAPER-THEN-SPECIFICATION");
  await expect(page.locator(".successor-ceiling")).toContainText("no browser inference");
  await expect(page.locator("#successor-output-identity")).toContainText("source bound graph projection");

  const screenshot = fileURLToPath(
    new URL(`../../generated/iteration11-screenshots/${testInfo.project.name}-D11-boundary.png`, import.meta.url),
  );
  await page.screenshot({ path: screenshot, fullPage: true });
});
