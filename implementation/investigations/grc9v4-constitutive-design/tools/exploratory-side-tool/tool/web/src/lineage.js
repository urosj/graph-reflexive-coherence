import { recordDigest } from "./bundle.js";

const LAYER_SCHEMA = "grcv4_explorer_ET_C8_lineage_playback_layer_v1";
const ADMITTED_STATES = new Set([
  "accepted_unaffected",
  "baseline_anchor",
  "direct_effect",
  "transitive_effect",
  "reopening_gate",
  "evidence_frontier_unresolved",
]);

export async function verifyLineagePlaybackLayer(layer, bundle, ceilingLayer) {
  if (layer?.schema !== LAYER_SCHEMA) throw new Error("lineage playback schema is not admitted");
  if (layer.status !== "awaiting_human_review" && layer.status !== "accepted") {
    throw new Error("lineage playback layer is outside its candidate lifecycle");
  }
  if ((await recordDigest(layer, "layer_digest")) !== layer.layer_digest) {
    throw new Error("lineage playback layer digest failed");
  }
  if (layer.predecessor.layer_digest !== ceilingLayer.layer_digest) {
    throw new Error("lineage playback predecessor binding failed");
  }
  if (layer.source_identities.source_bundle_digest !== bundle.accepted_identities.source_bundle_digest) {
    throw new Error("lineage playback source identity failed");
  }
  if (layer.source_identities.graph_digest !== bundle.accepted_identities.graph_digest) {
    throw new Error("lineage playback graph identity failed");
  }
  const authority = layer.authority;
  if (
    !authority.source_graph_immutable ||
    !authority.lineage_projection_only ||
    authority.browser_propagation ||
    authority.browser_rerun_prediction ||
    authority.browser_scenario_editing ||
    authority.browser_scenario_recomputation ||
    !authority.playback_rows_precomputed ||
    authority.source_mode_changed_by_playback ||
    authority.unresolved_frontier_promoted ||
    authority.scientific_claim_added
  ) {
    throw new Error("lineage playback layer exceeds presentation authority");
  }
  const nodeIds = new Set(layer.lineage.nodes.map((row) => row.node_id));
  for (const position of layer.lineage.scrub_positions) {
    if (!nodeIds.has(position.node_id) || !position.record_id || !position.record_digest) {
      throw new Error("scrub position lacks accepted identity");
    }
  }
  for (const playback of Object.values(layer.playbacks)) {
    if (playback.browser_may_recompute || playback.browser_may_predict_rerun) {
      throw new Error("playback grants browser scientific authority");
    }
    if ((await recordDigest(playback, "playback_digest")) !== playback.playback_digest) {
      throw new Error("playback digest failed");
    }
    if (!playback.scenario_canonical_json.endsWith("\n")) {
      throw new Error("canonical scenario is not newline terminated");
    }
    for (const frame of playback.frames) {
      if (frame.node_states.length !== layer.population_counts.accepted_gate_records) {
        throw new Error("playback frame does not classify every accepted gate");
      }
      if (frame.node_states.some((row) => !ADMITTED_STATES.has(row.state))) {
        throw new Error("playback frame contains an unknown state");
      }
    }
  }
  return layer;
}

export function scrubPosition(layer, index) {
  return layer.lineage.scrub_positions[index] ?? null;
}

export function playbackById(layer, playbackId) {
  return layer.playbacks[playbackId] ?? null;
}

export function playbackRows(layer, sourceScenarioId = null) {
  return Object.values(layer.playbacks)
    .filter((row) => !sourceScenarioId || row.source_scenario_id === sourceScenarioId)
    .sort((left, right) => left.playback_id.localeCompare(right.playback_id));
}

export function playbackFrame(playback, frameIndex) {
  return playback?.frames[frameIndex] ?? null;
}

export function reconstructionForClaim(layer, claimId) {
  return layer.claim_reconstructions[claimId] ?? null;
}

export function reconstructionRows(layer, query = "") {
  const needle = query.trim().toLocaleLowerCase();
  return Object.values(layer.claim_reconstructions)
    .filter((row) => {
      if (!needle) return true;
      return `${row.claim_id} ${row.claim_class} ${row.statement}`
        .replaceAll("_", " ")
        .toLocaleLowerCase()
        .includes(needle);
    })
    .sort((left, right) => left.claim_id.localeCompare(right.claim_id));
}

export function canonicalScenarioText(playback) {
  if (!playback || playback.browser_may_recompute || playback.browser_may_predict_rerun) {
    throw new Error("unverified playback cannot be serialized");
  }
  return playback.scenario_canonical_json;
}
