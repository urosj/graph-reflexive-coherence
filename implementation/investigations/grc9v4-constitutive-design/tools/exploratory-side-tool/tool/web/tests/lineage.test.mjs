import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import test from "node:test";

import { verifyBundle } from "../src/bundle.js";
import { verifyClaimCeilingLayer } from "../src/ceilings.js";
import {
  canonicalScenarioText,
  playbackById,
  playbackFrame,
  playbackRows,
  reconstructionForClaim,
  scrubPosition,
  verifyLineagePlaybackLayer,
} from "../src/lineage.js";

async function loadJson(path) {
  return JSON.parse(await readFile(new URL(path, import.meta.url), "utf8"));
}

function canonicalize(value) {
  if (Array.isArray(value)) return value.map(canonicalize);
  if (value && typeof value === "object") {
    return Object.fromEntries(Object.keys(value).sort().map((key) => [key, canonicalize(value[key])]));
  }
  return value;
}

async function loadLayer() {
  const bundle = await verifyBundle(await loadJson("../public/data/ETC6StaticNavigationBundle.json"));
  const ceilings = await verifyClaimCeilingLayer(
    await loadJson("../public/data/ETC7ClaimCeilingAlternativeLayer.json"),
    bundle,
  );
  return verifyLineagePlaybackLayer(
    await loadJson("../public/data/ETC8LineagePlaybackLayer.json"),
    bundle,
    ceilings,
  );
}

test("lineage spine binds accepted identities and preserves typed overlays", async () => {
  const layer = await loadLayer();
  assert.equal(layer.population_counts.accepted_gate_records, 33);
  assert.equal(layer.population_counts.spine_positions, 26);
  assert.equal(layer.population_counts.branch_nodes, 7);
  assert.equal(layer.population_counts.correction_markers, 1);
  assert.equal(layer.population_counts.supersession_markers, 4);
  assert.equal(scrubPosition(layer, 0).gate_id, "D0");
  assert.equal(scrubPosition(layer, 25).gate_id, "D10.2");
  assert.match(scrubPosition(layer, 11).record_digest, /^[0-9a-f]{64}$/);
  assert.equal(layer.lineage.correction_markers[0].accepted_record_bytes_modified, false);
  assert.equal(layer.lineage.correction_markers[0].accepted_decision_dispositions_reopened, false);
});

test("C1 playback freezes D7-v2 and presents only precomputed frontier states", async () => {
  const layer = await loadLayer();
  const playback = playbackRows(layer, "C1")[0];
  assert.equal(playback.baseline_scrub_position.gate_id, "D7-v2");
  assert.equal(playback.browser_may_recompute, false);
  assert.equal(playback.browser_may_predict_rerun, false);
  assert.deepEqual(playback.minimal_invalidation_root_node_ids, ["gate_record:GRC9V4-CD-D7V2-v1"]);
  assert.ok(playback.evidence_frontier_node_ids.includes("gate_record:GRC9V4-CD-D10.2-v1"));
  const frontier = playbackFrame(playback, 3);
  const states = new Map(frontier.node_states.map((row) => [row.node_id, row.state]));
  assert.equal(states.get("gate_record:GRC9V4-CD-D7V2-v1"), "reopening_gate");
  assert.equal(states.get("gate_record:GRC9V4-CD-D10.2-v1"), "evidence_frontier_unresolved");
  assert.equal(states.get("gate_record:GRC9V4-CD-D0-v1"), "accepted_unaffected");
});

test("canonical scenario export is byte-preserving and C2 remains profile local", async () => {
  const layer = await loadLayer();
  const playback = playbackRows(layer, "C2")[0];
  const text = canonicalScenarioText(playback);
  assert.equal(text.endsWith("\n"), true);
  assert.equal(`${JSON.stringify(canonicalize(JSON.parse(text)))}\n`, text);
  assert.equal(JSON.parse(text).profile_id, "A_CI");
  assert.deepEqual(JSON.parse(text).candidate_ids, ["V4-A-temporalized-W"]);
  assert.equal(playbackById(layer, playback.playback_id).ripple_digest, playback.ripple_digest);
});

test("every visible claim has a verification-excluding backward reconstruction", async () => {
  const layer = await loadLayer();
  assert.equal(Object.keys(layer.claim_reconstructions).length, 68);
  const row = reconstructionForClaim(layer, "D10-CL-N-001");
  assert.equal(row.verification_obligations_excluded, true);
  assert.ok(row.node_ids.includes("current_claim:D10-CL-N-001"));
  assert.equal(row.edge_refs.some((edge) => edge.relation === "requires_verification_from"), false);
  assert.match(row.trace_digest, /^[0-9a-f]{64}$/);
});

test("orientation preserves generic GRC and nine-port specialization roles", async () => {
  const layer = await loadLayer();
  assert.equal(
    layer.orientation_path.factorization,
    "GRCV4 ->[nine-port specialization] GRC9V4 ->[disabled V4 profile] GRC9V3",
  );
  assert.deepEqual(layer.orientation_path.steps.map((row) => row.substrate_id), ["GRCV4", "GRC9V4", "GRC9V3"]);
  assert.equal(layer.orientation_path.steps[1].role, "substantive_nine_port_specialization");
  assert.equal(layer.orientation_path.steps[2].role, "exact_disabled_profile_compatibility_target");
});
