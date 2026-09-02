import { recordDigest } from "./bundle.js";

const LAYER_SCHEMA = "grcv4_explorer_ET_C7_claim_ceiling_alternative_layer_v1";
const ALTERNATIVE_CLASSES = new Set([
  "routed_candidate",
  "conditional_claim",
  "blocked_relabel",
  "historical_claim",
  "rejected_candidate",
  "rejected_alternative",
]);
const GHOST_NODE_CLASSES = new Set([
  "routed_candidate",
  "conditional_claim",
  "historical_claim",
  "rejected_candidate",
]);

export async function verifyClaimCeilingLayer(layer, bundle) {
  if (layer?.schema !== LAYER_SCHEMA) throw new Error("claim-ceiling layer schema is not admitted");
  if (layer.status !== "accepted") {
    throw new Error("claim-ceiling layer is outside its accepted lifecycle");
  }
  if ((await recordDigest(layer, "layer_digest")) !== layer.layer_digest) {
    throw new Error("claim-ceiling layer digest failed");
  }
  if (layer.predecessor.static_bundle_digest !== bundle.bundle_digest) {
    throw new Error("claim-ceiling predecessor bundle binding failed");
  }
  if (layer.source_identities.source_bundle_digest !== bundle.accepted_identities.source_bundle_digest) {
    throw new Error("claim-ceiling source identity failed");
  }
  if (layer.source_identities.graph_digest !== bundle.accepted_identities.graph_digest) {
    throw new Error("claim-ceiling graph identity failed");
  }
  if (
    !layer.authority.source_classification_immutable ||
    layer.authority.browser_scientific_inference ||
    layer.authority.browser_propagation ||
    layer.authority.browser_scenario_serialization ||
    layer.authority.ghost_promotion ||
    layer.authority.hidden_score_or_ranking ||
    !layer.authority.slider_changes_presentation_only
  ) {
    throw new Error("claim-ceiling layer exceeds presentation authority");
  }
  for (const row of layer.alternatives) {
    if (!ALTERNATIVE_CLASSES.has(row.alternative_class)) throw new Error("unknown alternative class");
    if (row.promotion_allowed || !row.ghost_style_required) throw new Error("alternative authority failed");
  }
  for (const row of layer.locks) {
    if (row.promotion_allowed || row.readable_annotation.authority !== "non_authoritative_readability_annotation") {
      throw new Error("lock authority failed");
    }
  }
  return layer;
}

const indexesCache = new WeakMap();

function indexes(layer) {
  if (indexesCache.has(layer)) return indexesCache.get(layer);
  const locksById = new Map(layer.locks.map((row) => [row.lock_id, row]));
  const alternativesById = new Map(layer.alternatives.map((row) => [row.alternative_id, row]));
  const locksByNode = new Map();
  const ghostByNode = new Map();
  for (const lock of layer.locks) {
    for (const nodeId of lock.target_node_ids) {
      const rows = locksByNode.get(nodeId) ?? [];
      rows.push(lock);
      locksByNode.set(nodeId, rows);
    }
  }
  for (const alternative of layer.alternatives) {
    if (!alternative.target_node_id || !GHOST_NODE_CLASSES.has(alternative.alternative_class)) continue;
    const current = ghostByNode.get(alternative.target_node_id);
    if (!current || alternative.visibility_threshold < current.visibility_threshold) {
      ghostByNode.set(alternative.target_node_id, alternative);
    }
  }
  const value = { locksById, alternativesById, locksByNode, ghostByNode };
  indexesCache.set(layer, value);
  return value;
}

export function lockById(layer, lockId) {
  return indexes(layer).locksById.get(lockId) ?? null;
}

export function alternativeById(layer, alternativeId) {
  return indexes(layer).alternativesById.get(alternativeId) ?? null;
}

export function locksForNode(layer, nodeId) {
  return indexes(layer).locksByNode.get(nodeId) ?? [];
}

export function ghostForNode(layer, nodeId) {
  return indexes(layer).ghostByNode.get(nodeId) ?? null;
}

export function ghostOpacity(row, visibility) {
  if (!row || visibility < row.visibility_threshold) return 0;
  if (visibility === 100 || row.visibility_threshold === 100) return 1;
  const span = 100 - row.visibility_threshold;
  return 0.25 + (0.75 * (visibility - row.visibility_threshold)) / span;
}

export function filterLocks(layer, query) {
  const needle = query.trim().toLocaleLowerCase();
  return layer.locks.filter((row) => {
    if (!needle) return true;
    return `${row.lock_id} ${row.lock_class} ${row.source_reason} ${row.stronger_blocked_claims.join(" ")}`
      .replaceAll("_", " ")
      .toLocaleLowerCase()
      .includes(needle);
  });
}

export function visibleAlternatives(layer, visibility, query) {
  const needle = query.trim().toLocaleLowerCase();
  return layer.alternatives.filter((row) => {
    if (ghostOpacity(row, visibility) === 0) return false;
    if (!needle) return true;
    return `${row.alternative_id} ${row.alternative_class} ${row.immutable_status} ${row.label}`
      .replaceAll("_", " ")
      .toLocaleLowerCase()
      .includes(needle);
  });
}

export function candidateCareer(layer, candidateId) {
  return layer.candidate_careers[candidateId] ?? null;
}
