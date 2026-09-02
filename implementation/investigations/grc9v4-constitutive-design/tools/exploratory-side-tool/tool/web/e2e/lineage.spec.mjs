import { expect, test } from "@playwright/test";
import { fileURLToPath } from "node:url";

test("accepted lineage scrubbing preserves branches, correction, and substrate orientation", async ({ page }, testInfo) => {
  await page.goto("/");
  await page.locator('[data-surface="lineage"]').click();
  await expect(page.locator("#lineage-workspace")).not.toHaveClass(/is-hidden/);
  await expect(page.locator("#lineage-graph canvas").first()).toBeVisible();
  await expect(page.locator("#lineage-summary")).toContainText("33 accepted records");
  await expect(page.locator("#lineage-markers")).toContainText("7");
  await expect(page.locator("#lineage-markers")).toContainText("post-v2 typed correction");
  await expect(page.locator("#orientation-path")).toContainText("GRCv4");
  await expect(page.locator("#orientation-path")).toContainText("GRC9v4");
  await expect(page.locator("#orientation-path")).toContainText("GRC9v3");
  await expect(page.locator("#orientation-path")).toContainText("nine port specialization");

  await page.locator("#lineage-scrubber").evaluate((element) => {
    element.value = "11";
    element.dispatchEvent(new Event("input", { bubbles: true }));
  });
  await expect(page.locator("#scrub-receipt")).toContainText("D7-v2");
  await expect(page.locator("#scrub-receipt")).toContainText("f0d355c3");

  await page.locator("#reconstruction-select").selectOption("D10-CL-N-001");
  await expect(page.locator("#reconstruction-result")).toContainText("accepted nodes");
  await expect(page.locator("#reconstruction-result")).toContainText("support links");
  await expect(page.locator("#reconstruction-result")).toContainText("D10-CL-N-001");

  const layout = await page.evaluate(() => {
    const selectors = [".lineage-control-panel", ".lineage-graph-panel", ".lineage-inspector"];
    const rectangles = Object.fromEntries(selectors.map((selector) => {
      const rect = document.querySelector(selector).getBoundingClientRect();
      return [selector, { left: rect.left, right: rect.right, top: rect.top, bottom: rect.bottom, width: rect.width, height: rect.height }];
    }));
    const canvas = document.querySelector("#lineage-graph canvas");
    return {
      rectangles,
      canvas: { width: canvas.width, height: canvas.height },
      viewport: { width: window.innerWidth, height: window.innerHeight },
      horizontalOverflow: document.documentElement.scrollWidth > window.innerWidth + 1,
    };
  });
  expect(layout.horizontalOverflow).toBe(false);
  expect(layout.canvas.width).toBeGreaterThan(100);
  expect(layout.canvas.height).toBeGreaterThan(100);
  for (const rect of Object.values(layout.rectangles)) {
    expect(rect.width).toBeGreaterThan(0);
    expect(rect.height).toBeGreaterThan(0);
    expect(rect.left).toBeGreaterThanOrEqual(0);
    expect(rect.right).toBeLessThanOrEqual(layout.viewport.width + 1);
  }
  if (testInfo.project.name === "desktop") {
    expect(layout.rectangles[".lineage-control-panel"].right).toBeLessThanOrEqual(layout.rectangles[".lineage-graph-panel"].left + 1);
    expect(layout.rectangles[".lineage-graph-panel"].right).toBeLessThanOrEqual(layout.rectangles[".lineage-inspector"].left + 1);
  } else {
    expect(layout.rectangles[".lineage-control-panel"].bottom).toBeLessThanOrEqual(layout.rectangles[".lineage-graph-panel"].top + 1);
    expect(layout.rectangles[".lineage-graph-panel"].bottom).toBeLessThanOrEqual(layout.rectangles[".lineage-inspector"].top + 1);
  }

  const screenshot = fileURLToPath(
    new URL(`../../generated/iteration8-screenshots/${testInfo.project.name}-source-lineage.png`, import.meta.url),
  );
  await page.screenshot({ path: screenshot, fullPage: true });
});

test("precomputed C1 fork marks reopening and frontier without changing source state", async ({ page }, testInfo) => {
  await page.goto("/");
  const sourceBefore = await page.evaluate(async () => (await fetch("/data/ETC8LineagePlaybackLayer.json")).text());
  await page.locator('[data-surface="lineage"]').click();
  await page.locator('[data-mode="speculative"]').click();
  await expect(page.locator("#lineage-workspace")).toHaveAttribute("data-mode", "speculative");
  await expect(page.locator("#scenario-select")).toHaveValue(/ET-C5-C1/);
  const c1 = await page.locator("#scenario-select").inputValue();
  await expect(page.locator("#lineage-scrubber")).toBeDisabled();
  await expect(page.locator("#scrub-receipt")).toContainText("D7-v2");

  await page.locator("#step-playback").click();
  await expect(page.locator("#frame-status")).toContainText("Direct source effects");
  await page.locator("#step-playback").click();
  await expect(page.locator("#frame-status")).toContainText("Recorded transitive effects");
  await page.locator("#step-playback").click();
  await expect(page.locator("#frame-status")).toContainText("Reopening gate and evidence frontier");
  await expect(page.locator(".effect-row.reopening")).toHaveCount(1);
  await expect(page.locator(".effect-row.frontier").first()).toBeVisible();
  await expect(page.locator("#effect-list")).toContainText("GRC9V4-CD-D10.2-v1");

  const graphStates = await page.evaluate(() => ({
    root: window.__ETC8__.layer.playbacks[window.document.querySelector("#scenario-select").value].minimal_invalidation_root_node_ids,
    frontier: window.__ETC8__.layer.playbacks[window.document.querySelector("#scenario-select").value].evidence_frontier_node_ids,
    sourceImmutable: window.__ETC8__.layer.authority.source_mode_changed_by_playback === false,
  }));
  expect(graphStates.root).toEqual(["gate_record:GRC9V4-CD-D7V2-v1"]);
  expect(graphStates.frontier).toContain("gate_record:GRC9V4-CD-D10.2-v1");
  expect(graphStates.sourceImmutable).toBe(true);

  const c2 = await page.locator("#scenario-select option").evaluateAll((options) => options.find((row) => row.value.includes("ET-C5-C2"))?.value);
  await page.locator("#scenario-select").selectOption(c2);
  const roundtrip = await page.evaluate((playbackId) => {
    const text = window.__ETC8__.getCanonicalScenarioText(playbackId);
    return { text, parsed: JSON.parse(text) };
  }, c2);
  expect(roundtrip.text.endsWith("\n")).toBe(true);
  expect(roundtrip.parsed.profile_id).toBe("A_CI");
  expect(roundtrip.parsed.candidate_ids).toEqual(["V4-A-temporalized-W"]);

  await page.locator("#scenario-select").selectOption(c1);
  await page.locator("#step-playback").click();
  const speculativeLayout = await page.evaluate(() => {
    const brand = document.querySelector(".brand-block").getBoundingClientRect();
    return {
      scrollX: window.scrollX,
      horizontalOverflow: document.documentElement.scrollWidth > window.innerWidth + 1,
      brand: { left: brand.left, right: brand.right, width: brand.width },
      viewportWidth: window.innerWidth,
    };
  });
  expect(speculativeLayout.scrollX).toBe(0);
  expect(speculativeLayout.horizontalOverflow).toBe(false);
  expect(speculativeLayout.brand.width).toBeGreaterThan(0);
  expect(speculativeLayout.brand.left).toBeGreaterThanOrEqual(0);
  expect(speculativeLayout.brand.right).toBeLessThanOrEqual(speculativeLayout.viewportWidth + 1);
  const screenshot = fileURLToPath(
    new URL(`../../generated/iteration8-screenshots/${testInfo.project.name}-speculative-fork.png`, import.meta.url),
  );
  await page.screenshot({ path: screenshot, fullPage: true });

  await page.locator('[data-mode="source"]').click();
  await expect(page.locator("#frame-status")).toContainText("Playback cannot alter accepted lineage");
  await expect(page.locator("#lineage-scrubber")).toBeEnabled();
  const sourceAfter = await page.evaluate(async () => (await fetch("/data/ETC8LineagePlaybackLayer.json")).text());
  expect(sourceAfter).toBe(sourceBefore);
});
