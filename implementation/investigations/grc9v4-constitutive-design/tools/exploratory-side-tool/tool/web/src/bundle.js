const BUNDLE_SCHEMA = "grcv4_explorer_ET_C6_static_navigation_bundle_v1";

function sortedValue(value) {
  if (Array.isArray(value)) return value.map(sortedValue);
  if (value && typeof value === "object") {
    return Object.fromEntries(
      Object.keys(value)
        .sort()
        .map((key) => [key, sortedValue(value[key])]),
    );
  }
  return value;
}

export function canonicalStringify(value) {
  return JSON.stringify(sortedValue(value)).replace(/[\u007f-\uffff]/g, (character) =>
    `\\u${character.charCodeAt(0).toString(16).padStart(4, "0")}`,
  );
}

export async function sha256Text(value) {
  const bytes = new TextEncoder().encode(value);
  const digest = await crypto.subtle.digest("SHA-256", bytes);
  return Array.from(new Uint8Array(digest), (byte) => byte.toString(16).padStart(2, "0")).join("");
}

export async function recordDigest(value, field) {
  const payload = structuredClone(value);
  delete payload[field];
  return sha256Text(canonicalStringify(payload));
}

async function requireDigest(value, receipt, label) {
  if (!value || value[receipt.digest_field] !== receipt.digest) {
    throw new Error(`${label} declared digest binding failed`);
  }
  const actual = await recordDigest(value, receipt.digest_field);
  if (actual !== receipt.digest) throw new Error(`${label} canonical digest failed`);
}

export async function verifyBundle(bundle) {
  if (bundle?.schema !== BUNDLE_SCHEMA) throw new Error("navigation bundle schema is not admitted");
  if (bundle.status !== "accepted") {
    throw new Error("navigation bundle lifecycle status is not admitted");
  }
  const actual = await recordDigest(bundle, "bundle_digest");
  if (actual !== bundle.bundle_digest) throw new Error("navigation bundle digest failed");
  const payloads = bundle.embedded_payloads;
  const receipts = bundle.embedded_payload_receipts;
  for (const key of ["source_manifest", "graph_projection", "scenario_bundle", "ripple_aggregate", "ripple_index"]) {
    await requireDigest(payloads[key], receipts[key], key);
  }
  if (payloads.ripple_shards.length !== receipts.ripple_shards.length) {
    throw new Error("ripple shard receipt population failed");
  }
  for (let index = 0; index < payloads.ripple_shards.length; index += 1) {
    await requireDigest(payloads.ripple_shards[index], receipts.ripple_shards[index], `ripple_shard_${index}`);
  }
  if (bundle.authority.browser_propagation_rule || bundle.authority.browser_ripple_compilation) {
    throw new Error("browser bundle exceeds static lookup authority");
  }
  return bundle;
}

const lookupCache = new WeakMap();

function lookups(bundle) {
  if (lookupCache.has(bundle)) return lookupCache.get(bundle);
  const graph = bundle.embedded_payloads.graph_projection;
  const value = {
    catalog: new Map(bundle.catalog.map((row) => [row.node_id, row])),
    nodes: new Map(graph.nodes.map((row) => [row.node_id, row])),
    edges: new Map([...graph.propagation_edges, ...graph.annotation_edges].map((row) => [row.edge_id, row])),
    ripples: new Map(
      bundle.embedded_payloads.ripple_shards.flatMap((shard) => shard.rows).map((row) => [row.ripple_digest, row]),
    ),
  };
  lookupCache.set(bundle, value);
  return value;
}

export function projectionFor(bundle, nodeId) {
  const compiled = bundle.selection_projections[nodeId];
  if (!compiled) throw new Error(`selection is outside the compiled bundle: ${nodeId}`);
  const indexes = lookups(bundle);
  const nodePayload = (value) => ({ ...indexes.catalog.get(value), attributes: indexes.nodes.get(value).attributes });
  return {
    schema: compiled.schema,
    selection: nodePayload(compiled.selection_node_id),
    focus: {
      root_node_id: compiled.focus.root_node_id,
      node_limit: compiled.focus.node_limit,
      edge_limit: compiled.focus.edge_limit,
      omitted_direct_neighbor_count: compiled.focus.omitted_direct_neighbor_count,
      omitted_incident_edge_count: compiled.focus.omitted_incident_edge_count,
      nodes: compiled.focus.node_ids.map(nodePayload),
      edges: compiled.focus.edge_ids.map((value) => indexes.edges.get(value)),
    },
    triangulation: compiled.triangulation.map((lens) => ({
      lens_id: lens.lens_id,
      label: lens.label,
      edge_count: lens.edge_count,
      rows: lens.rows.map((row) => ({
        neighbor: nodePayload(row.neighbor_node_id),
        direction: row.direction,
        edge: indexes.edges.get(row.edge_id),
      })),
    })),
    dependency_reach: compiled.dependency_reach,
    selected_ripple_row: indexes.ripples.get(compiled.selected_ripple_digest) ?? null,
  };
}

export function familyById(bundle, familyId) {
  return bundle.family_coverage.find((row) => row.family_id === familyId) ?? null;
}

export function filterCatalog(bundle, query, familyId = "all") {
  const needle = query.trim().toLocaleLowerCase();
  const family = familyById(bundle, familyId);
  const familyIds = family ? new Set(family.node_ids) : null;
  return bundle.catalog.filter((row) => {
    if (familyIds && !familyIds.has(row.node_id)) return false;
    if (!needle) return true;
    return `${row.identifier} ${row.label} ${row.kind}`.toLocaleLowerCase().includes(needle);
  });
}

export function sourceState(bundle) {
  const state = bundle.source_observation.state;
  const rows = {
    current_bundle_exact: ["Current", "current"],
    new_unprocessed_source_available: ["Historical snapshot / new source", "historical"],
    admitted_source_identity_changed: ["Stale / source changed", "blocked"],
    admitted_source_missing: ["Stale / source missing", "blocked"],
    source_observation_unreadable: ["Observation blocked", "blocked"],
  };
  const [label, tone] = rows[state] ?? ["Observation blocked", "blocked"];
  return { state, label, tone, renderAllowed: tone !== "blocked" };
}
