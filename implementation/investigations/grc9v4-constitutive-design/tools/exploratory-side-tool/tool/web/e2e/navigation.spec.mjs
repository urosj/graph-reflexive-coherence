import { expect, test } from "@playwright/test";
import { fileURLToPath } from "node:url";

test("verified static navigation workbench remains bounded and usable", async ({ page }, testInfo) => {
  await page.goto("/");
  await expect(page).toHaveTitle("GRCv4 Constitutive Explorer");
  await expect(page.locator("h1")).toHaveText("GRCv4 Constitutive Explorer");
  await expect(page.locator(".source-state")).toContainText("Current");
  await expect(page.locator(".family-row")).toHaveCount(9);
  await expect(page.locator("#graph canvas").first()).toBeVisible();
  await expect(page.locator(".graph-summary")).toContainText("nodes");

  await page.locator('[data-family="complete_step_lifecycle"]').click();
  await expect(page.locator('[data-family="complete_step_lifecycle"]')).toHaveClass(/is-active/);
  await page.locator("#search-input").fill("D10-CL-N-001");
  await page.locator("#search-input").press("Enter");
  await expect(page.locator(".selection-id")).toContainText("D10-CL-N-001");

  await page.locator('[data-tab="lenses"]').click();
  await expect(page.locator(".lens-block").first()).toBeVisible();
  await page.locator('[data-tab="reach"]').click();
  await expect(page.locator(".reach-note")).toContainText("not importance or priority");
  await expect(page.locator(".reach-row")).toHaveCount(7);
  await page.locator('[data-mode="speculative"]').click();
  await expect(page.locator(".workspace")).toHaveAttribute("data-mode", "speculative");
  await page.locator('[data-mode="source"]').click();

  const layout = await page.evaluate(() => {
    const selectors = [".topbar", ".navigation-panel", ".graph-panel", ".inspector-panel"];
    const rectangles = Object.fromEntries(
      selectors.map((selector) => {
        const rect = document.querySelector(selector).getBoundingClientRect();
        return [selector, { left: rect.left, right: rect.right, top: rect.top, bottom: rect.bottom, width: rect.width, height: rect.height }];
      }),
    );
    return {
      rectangles,
      viewport: { width: window.innerWidth, height: window.innerHeight },
      horizontalOverflow: document.documentElement.scrollWidth > window.innerWidth + 1,
    };
  });
  expect(layout.horizontalOverflow).toBe(false);
  for (const rect of Object.values(layout.rectangles)) {
    expect(rect.width).toBeGreaterThan(0);
    expect(rect.height).toBeGreaterThan(0);
    expect(rect.left).toBeGreaterThanOrEqual(0);
    expect(rect.right).toBeLessThanOrEqual(layout.viewport.width + 1);
  }
  if (testInfo.project.name === "desktop") {
    expect(layout.rectangles[".navigation-panel"].right).toBeLessThanOrEqual(layout.rectangles[".graph-panel"].left + 1);
    expect(layout.rectangles[".graph-panel"].right).toBeLessThanOrEqual(layout.rectangles[".inspector-panel"].left + 1);
  } else {
    expect(layout.rectangles[".navigation-panel"].bottom).toBeLessThanOrEqual(layout.rectangles[".graph-panel"].top + 1);
    expect(layout.rectangles[".graph-panel"].bottom).toBeLessThanOrEqual(layout.rectangles[".inspector-panel"].top + 1);
  }

  const screenshot = fileURLToPath(
    new URL(`../../generated/iteration6-screenshots/${testInfo.project.name}.png`, import.meta.url),
  );
  await page.screenshot({ path: screenshot, fullPage: true });
});
