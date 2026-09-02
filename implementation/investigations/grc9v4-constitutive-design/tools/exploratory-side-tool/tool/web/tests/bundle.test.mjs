import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import test from "node:test";

import {
  canonicalStringify,
  familyById,
  filterCatalog,
  projectionFor,
  recordDigest,
  sourceState,
  verifyBundle,
} from "../src/bundle.js";

const record = new URL("../../../records/ETC6StaticNavigationBundle.json", import.meta.url);
const parityRecord = new URL("../../../records/ETC6CrossSurfaceParity.json", import.meta.url);

async function loadJson(url) {
  return JSON.parse(await readFile(url, "utf8"));
}

test("accepted embedded payloads and bundle verify", async () => {
  const bundle = await loadJson(record);
  assert.equal(await verifyBundle(bundle), bundle);
  assert.equal(bundle.selection_projection_count, 436);
  assert.equal(bundle.family_coverage.length, 9);
  assert.equal(bundle.family_coverage.reduce((total, row) => total + row.object_count, 0), 67);
});

test("tampered outer and embedded payloads fail closed", async () => {
  const original = await loadJson(record);
  const outer = structuredClone(original);
  outer.catalog[0].label = "tampered";
  await assert.rejects(() => verifyBundle(outer), /navigation bundle digest/);

  const embedded = structuredClone(original);
  embedded.embedded_payloads.graph_projection.nodes[0].identifier = "tampered";
  embedded.bundle_digest = await recordDigest(embedded, "bundle_digest");
  await assert.rejects(() => verifyBundle(embedded), /graph_projection canonical digest/);

  const authority = structuredClone(original);
  authority.authority.browser_propagation_rule = true;
  authority.bundle_digest = await recordDigest(authority, "bundle_digest");
  await assert.rejects(() => verifyBundle(authority), /static lookup authority/);

  const candidate = structuredClone(original);
  candidate.status = "candidate_awaiting_human_review";
  candidate.bundle_digest = await recordDigest(candidate, "bundle_digest");
  await assert.rejects(() => verifyBundle(candidate), /lifecycle status/);
});

test("family coverage is exact and is not profile propagation", async () => {
  const bundle = await loadJson(record);
  const family = familyById(bundle, "candidate_A");
  assert.equal(family.object_count, 7);
  assert.equal(family.classification, "coverage_not_profile_scope_or_ranking");
  assert.equal(filterCatalog(bundle, "", "candidate_A").length, 7);
  assert.ok(filterCatalog(bundle, "directional", "candidate_A").length >= 1);
});

test("browser dereferencing equals Python parity payloads byte for byte", async () => {
  const bundle = await loadJson(record);
  const parity = await loadJson(parityRecord);
  for (const [nodeId, expected] of Object.entries(parity.selection_payloads)) {
    assert.equal(canonicalStringify(projectionFor(bundle, nodeId)), canonicalStringify(expected), nodeId);
  }
});

test("source-state vocabulary covers current historical stale and blocked states", async () => {
  const bundle = await loadJson(record);
  const expectations = {
    current_bundle_exact: ["current", true],
    new_unprocessed_source_available: ["historical", true],
    admitted_source_identity_changed: ["blocked", false],
    admitted_source_missing: ["blocked", false],
    source_observation_unreadable: ["blocked", false],
  };
  for (const [value, [tone, renderAllowed]] of Object.entries(expectations)) {
    const fixture = structuredClone(bundle);
    fixture.source_observation.state = value;
    const result = sourceState(fixture);
    assert.equal(result.tone, tone);
    assert.equal(result.renderAllowed, renderAllowed);
  }
});

test("every projection remains bounded and refers only to embedded identities", async () => {
  const bundle = await loadJson(record);
  const nodeIds = new Set(bundle.embedded_payloads.graph_projection.nodes.map((row) => row.node_id));
  const edgeIds = new Set(
    [
      ...bundle.embedded_payloads.graph_projection.propagation_edges,
      ...bundle.embedded_payloads.graph_projection.annotation_edges,
    ].map((row) => row.edge_id),
  );
  for (const [nodeId, projection] of Object.entries(bundle.selection_projections)) {
    assert.equal(projection.selection_node_id, nodeId);
    assert.ok(projection.focus.node_ids.length <= 32);
    assert.ok(projection.focus.edge_ids.length <= 72);
    assert.ok(projection.focus.node_ids.every((value) => nodeIds.has(value)));
    assert.ok(projection.focus.edge_ids.every((value) => edgeIds.has(value)));
  }
});
