import { expect, test } from "@playwright/test";
import { fileURLToPath } from "node:url";

test("locked claims and alternatives remain source-bounded and non-promotable", async ({ page }, testInfo) => {
  await page.goto("/");
  await expect(page.locator(".source-state")).toContainText("Current");
  await expect(page.locator(".authority-populations")).toContainText("29 current transformations");
  await expect(page.locator(".authority-populations")).toContainText("11 verification obligations");
  await expect(page.locator(".authority-populations")).toContainText("29 historical claims");

  await page.locator('[data-view="locks"]').click();
  await page.locator("#search-input").fill("future curvature");
  await page.locator("#search-input").press("Enter");
  await expect(page.locator(".lock-surface")).toHaveAttribute("data-lock-status", "accepted-source-lock");
  await expect(page.locator(".hardening-block")).toContainText("Candidate_A_future_curvature_rule");
  await expect(page.locator(".hardening-block")).toContainText("curvature_conditioning_requires_a_new_profile_identity_and_provenance_reopening");
  await expect(page.locator(".annotation-note")).toContainText("non-authoritative");

  const sourceScreenshot = fileURLToPath(
    new URL(`../../generated/iteration7-screenshots/${testInfo.project.name}-source-locks.png`, import.meta.url),
  );
  await page.screenshot({ path: sourceScreenshot, fullPage: true });

  const layerBefore = await page.evaluate(async () => (await fetch("/data/ETC7ClaimCeilingAlternativeLayer.json")).text());
  await page.locator('[data-view="alternatives"]').click();
  await page.locator("#alternative-visibility").evaluate((element) => {
    element.value = "100";
    element.dispatchEvent(new Event("input", { bubbles: true }));
  });
  await expect(page.locator("#visibility-value")).toHaveText("100%");
  await page.locator("#search-input").fill("routed candidate");
  await page.locator("#search-input").press("Enter");
  await expect(page.locator(".alternative-surface")).toHaveAttribute("data-promotion-allowed", "false");
  await expect(page.locator(".alternative-surface")).toContainText("routed not rejected");
  await expect(page.locator(".readmission-block")).toContainText("derive_and_admit_U_B_then_reopen_D2_through_D9_for_B");
  await expect(page.locator(".readmission-block")).toContainText("open work not promised success");
  const layerAfter = await page.evaluate(async () => (await fetch("/data/ETC7ClaimCeilingAlternativeLayer.json")).text());
  expect(layerAfter).toBe(layerBefore);

  await page.locator('[data-mode="speculative"]').click();
  await expect(page.locator(".workspace")).toHaveAttribute("data-mode", "speculative");
  const speculativeScreenshot = fileURLToPath(
    new URL(`../../generated/iteration7-screenshots/${testInfo.project.name}-speculative-alternatives.png`, import.meta.url),
  );
  await page.screenshot({ path: speculativeScreenshot, fullPage: true });

  await page.locator("#alternative-visibility").evaluate((element) => {
    element.value = "0";
    element.dispatchEvent(new Event("input", { bubbles: true }));
  });
  await expect(page.locator("#visibility-value")).toHaveText("0%");
  await expect(page.locator("[data-alternative-id]")).toHaveCount(0);
  await expect(page.locator(".alternative-surface")).toHaveCount(0);

  await page.locator("#alternative-visibility").evaluate((element) => {
    element.value = "100";
    element.dispatchEvent(new Event("input", { bubbles: true }));
  });
  await page.locator("#search-input").fill("resolved negative uninstantiated slot");
  await page.locator("#search-input").press("Enter");
  await expect(page.locator(".alternative-surface")).toContainText("resolved negative uninstantiated slot");
  await expect(page.locator(".alternative-surface")).toContainText("Promotion");
  await expect(page.locator(".alternative-surface")).toContainText("Forbidden by ET-C7 authority");

  await page.locator('[data-family="candidate_C"]').click();
  await page.locator("#search-input").fill("V4-C-constitutive-C-sector");
  await page.locator('[data-node-id="candidate:V4-C-constitutive-C-sector"]').click();
  await expect(page.locator(".selection-id")).toContainText("V4-C-constitutive-C-sector");
  await expect(page.locator(".career-block")).toContainText("D7G eligible complete candidate transition");
});
