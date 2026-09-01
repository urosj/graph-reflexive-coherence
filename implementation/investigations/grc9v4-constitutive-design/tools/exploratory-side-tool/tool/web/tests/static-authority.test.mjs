import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import test from "node:test";

const app = new URL("../src/app.js", import.meta.url);
const bundle = new URL("../src/bundle.js", import.meta.url);

test("client source contains no scientific propagation or ripple compiler", async () => {
  const source = `${await readFile(app, "utf8")}\n${await readFile(bundle, "utf8")}`;
  for (const forbidden of [
    "compileRipple",
    "compile_ripple",
    "evaluateMutation",
    "evaluate_mutation",
    "breadthFirstSearch",
    "unknown_beyond_evidence_frontier =",
  ]) {
    assert.equal(source.includes(forbidden), false, forbidden);
  }
  assert.ok(source.includes("selection_projections"));
  assert.ok(source.includes("embedded_payload_receipts"));
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
    "ArrowDown",
    "omitted_direct_neighbor_count",
  ]) {
    assert.ok(source.includes(required), required);
  }
  assert.equal(source.includes("hero"), false);
});
