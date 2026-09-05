import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import test from "node:test";

const app = new URL("../src/app.js", import.meta.url);
const bundle = new URL("../src/bundle.js", import.meta.url);

test("client source contains no scientific propagation or ripple compiler", async () => {
  const ceilings = new URL("../src/ceilings.js", import.meta.url);
  const lineage = new URL("../src/lineage.js", import.meta.url);
  const successor = new URL("../src/successor.js", import.meta.url);
  const source = `${await readFile(app, "utf8")}\n${await readFile(bundle, "utf8")}\n${await readFile(ceilings, "utf8")}\n${await readFile(lineage, "utf8")}\n${await readFile(successor, "utf8")}`;
  for (const forbidden of [
    "compileRipple",
    "compile_ripple",
    "evaluateMutation",
    "evaluate_mutation",
    "breadthFirstSearch",
    "unknown_beyond_evidence_frontier =",
    "promotion_allowed = true",
    "immutable_status =",
    "computeFrontier",
    "compute_frontier",
    "reopenGate(",
  ]) {
    assert.equal(source.includes(forbidden), false, forbidden);
  }
  assert.ok(source.includes("selection_projections"));
  assert.ok(source.includes("embedded_payload_receipts"));
  assert.ok(source.includes("slider_changes_presentation_only"));
  assert.ok(source.includes("non_authoritative_readability_annotation"));
  assert.ok(source.includes("playback_rows_precomputed"));
  assert.ok(source.includes("scenario_canonical_json"));
  assert.ok(source.includes("browser_rerun_prediction"));
  assert.ok(source.includes("ETC11D11SuccessorUXBundle.json"));
  assert.ok(source.includes("Presentation only: no browser inference"));
});

test("interface has bounded focus, modes, tabs, keyboard search, and no landing page", async () => {
  const source = await readFile(app, "utf8");
  for (const required of [
    "GRCv4 Constitutive Explorer",
    "data-mode=\"source\"",
    "data-mode=\"speculative\"",
    "data-tab=\"details\"",
    "data-tab=\"lenses\"",
    "data-tab=\"reach\"",
    "data-tab=\"ceilings\"",
    "alternative-visibility",
    "data-view=\"locks\"",
    "data-view=\"alternatives\"",
    "ArrowDown",
    "omitted_direct_neighbor_count",
    "data-surface=\"lineage\"",
    "data-surface=\"successor\"",
    "lineage-scrubber",
    "scenario-select",
    "reconstruction-select",
    "Precomputed ET-C5 rows only",
  ]) {
    assert.ok(source.includes(required), required);
  }
  assert.equal(source.includes("hero"), false);
});
