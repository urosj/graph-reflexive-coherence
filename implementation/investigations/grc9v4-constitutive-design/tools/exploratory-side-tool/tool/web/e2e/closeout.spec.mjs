import { expect, test } from "@playwright/test";
import { fileURLToPath } from "node:url";

test("forensic task reaches source-bound reconstruction through admitted lenses", async ({ page }, testInfo) => {
  await page.goto("/");
  await expect(page.locator(".source-state")).toContainText("Current");
  await page.locator('[data-family="complete_step_lifecycle"]').click();
  await page.locator("#search-input").fill("D10-CL-N-001");
  await page.locator("#search-input").press("Enter");
  await expect(page.locator(".selection-id")).toContainText("D10-CL-N-001");
  await expect(page.locator(".detail-list")).toContainText("Source record");
  await expect(page.locator(".detail-list")).toContainText("JSON pointer");

  await page.locator('[data-tab="lenses"]').click();
  await expect(page.locator(".lens-block").first()).toBeVisible();
  await page.locator('[data-tab="reach"]').click();
  await expect(page.locator(".reach-note")).toContainText("not importance or priority");

  await page.locator('[data-surface="lineage"]').click();
  await page.locator("#reconstruction-select").selectOption("D10-CL-N-001");
  await expect(page.locator("#reconstruction-result")).toContainText("accepted nodes");
  await expect(page.locator("#reconstruction-result")).toContainText("support links");
  await expect(page.locator("#reconstruction-result .scrub-digest")).toHaveText(/[0-9a-f]{64}/);

  const screenshot = fileURLToPath(
    new URL(`../../generated/iteration9-screenshots/${testInfo.project.name}-forensic-usability.png`, import.meta.url),
  );
  await page.screenshot({ path: screenshot, fullPage: true });
});
test("navigation task crosses families, boundaries, lineage, and precomputed ripple", async ({ page }, testInfo) => {
  await page.goto("/");
  await page.locator('[data-family="candidate_A"]').click();
  await expect(page.locator('[data-family="candidate_A"]')).toHaveClass(/is-active/);

  await page.locator('[data-view="locks"]').click();
  await page.locator("#search-input").fill("future curvature");
  await page.locator("#search-input").press("Enter");
  await expect(page.locator(".lock-surface")).toHaveAttribute("data-lock-status", "accepted-source-lock");

  await page.locator('[data-view="alternatives"]').click();
  await page.locator("#alternative-visibility").evaluate((element) => {
    element.value = "100";
    element.dispatchEvent(new Event("input", { bubbles: true }));
  });
  await page.locator("#search-input").fill("routed candidate");
  await page.locator("#search-input").press("Enter");
  await expect(page.locator(".alternative-surface")).toHaveAttribute("data-promotion-allowed", "false");

  await page.locator('[data-surface="lineage"]').click();
  await expect(page.locator("#orientation-path")).toContainText("GRCv4");
  await expect(page.locator("#orientation-path")).toContainText("GRC9v4");
  await page.locator('[data-mode="speculative"]').click();
  const c1 = await page.locator("#scenario-select option").evaluateAll(
    (options) => options.find((row) => row.value.includes("ET-C5-C1"))?.value,
  );
  await page.locator("#scenario-select").selectOption(c1);
  await page.locator("#step-playback").click();
  await page.locator("#step-playback").click();
  await page.locator("#step-playback").click();
  await expect(page.locator("#frame-status")).toContainText("evidence frontier");
  await expect(page.locator(".effect-row.reopening")).toHaveCount(1);
  await expect(page.locator(".effect-row.frontier").first()).toBeVisible();

  const screenshot = fileURLToPath(
    new URL(`../../generated/iteration9-screenshots/${testInfo.project.name}-navigation-usability.png`, import.meta.url),
  );
  await page.screenshot({ path: screenshot, fullPage: true });
});
