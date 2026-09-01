import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import test from "node:test";

import { canonicalStringify, recordDigest, verifyBundle } from "../src/bundle.js";
import {
  alternativeById,
  candidateCareer,
  filterLocks,
  ghostForNode,
  ghostOpacity,
  lockById,
  locksForNode,
  verifyClaimCeilingLayer,
  visibleAlternatives,
} from "../src/ceilings.js";

const bundleRecord = new URL("../../../records/ETC6StaticNavigationBundle.json", import.meta.url);
const layerRecord = new URL("../../../records/ETC7ClaimCeilingAlternativeLayer.json", import.meta.url);

async function loadJson(url) {
  return JSON.parse(await readFile(url, "utf8"));
}

test("candidate layer verifies against the accepted static predecessor", async () => {
  const bundle = await verifyBundle(await loadJson(bundleRecord));
  const layer = await loadJson(layerRecord);
  assert.equal(await verifyClaimCeilingLayer(layer, bundle), layer);
  assert.equal(layer.population_counts.locks, 90);
  assert.equal(layer.population_counts.alternatives, 144);
  assert.equal(layer.population_counts.targeted_hardenings, 8);
});

test("tampered lifecycle classification and promotion authority fail closed", async () => {
  const bundle = await verifyBundle(await loadJson(bundleRecord));
  const original = await loadJson(layerRecord);

  const outer = structuredClone(original);
  outer.locks[0].source_reason = "tampered";
  await assert.rejects(() => verifyClaimCeilingLayer(outer, bundle), /layer digest/);

  const lifecycle = structuredClone(original);
  lifecycle.status = "candidate_awaiting_human_review";
  lifecycle.layer_digest = await recordDigest(lifecycle, "layer_digest");
  await assert.rejects(() => verifyClaimCeilingLayer(lifecycle, bundle), /accepted lifecycle/);

  const promotion = structuredClone(original);
  promotion.alternatives[0].promotion_allowed = true;
  promotion.layer_digest = await recordDigest(promotion, "layer_digest");
  await assert.rejects(() => verifyClaimCeilingLayer(promotion, bundle), /alternative authority/);
});

test("visibility is progressive presentation and leaves serialized science unchanged", async () => {
  const layer = await loadJson(layerRecord);
  const before = canonicalStringify(layer);
  const expected = new Map([[0, 0], [20, 1], [40, 13], [60, 109], [80, 138], [100, 144]]);
  for (const [value, count] of expected) {
    assert.equal(visibleAlternatives(layer, value, "").length, count, value);
  }
  const routed = alternativeById(layer, "routed:V4-B-independent-derived-carrier");
  assert.equal(ghostOpacity(routed, 19), 0);
  assert.ok(ghostOpacity(routed, 20) > 0);
  assert.equal(ghostOpacity(routed, 100), 1);
  assert.equal(canonicalStringify(layer), before);
});

test("locks careers and ghosts retain exact immutable classes", async () => {
  const layer = await loadJson(layerRecord);
  const curvature = lockById(layer, "hardening:Candidate_A_future_curvature_rule");
  assert.equal(curvature.hardening.machine_value, "curvature_conditioning_requires_a_new_profile_identity_and_provenance_reopening");
  assert.equal(curvature.readable_annotation.authority, "non_authoritative_readability_annotation");
  assert.ok(locksForNode(layer, "candidate:V4-A-temporalized-W").length >= 2);
  assert.ok(filterLocks(layer, "future curvature").length >= 1);

  const bGhost = ghostForNode(layer, "candidate:V4-B-independent-derived-carrier");
  assert.equal(bGhost.alternative_class, "routed_candidate");
  assert.equal(bGhost.promotion_allowed, false);
  const dGhost = ghostForNode(layer, "candidate:V4-D-source-admitted-structural");
  assert.equal(dGhost.immutable_status, "resolved_negative_uninstantiated_slot");
  assert.equal(candidateCareer(layer, "V4-B-independent-derived-carrier").operation, "candidate_career");
});
