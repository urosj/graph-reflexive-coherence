import { recordDigest } from "./bundle.js";

const SUCCESSOR_SCHEMA = "grcv4_explorer_ET_C11_D11_successor_UX_bundle_v1";

export async function verifySuccessorBundle(bundle) {
  if (bundle?.schema !== SUCCESSOR_SCHEMA || bundle.status !== "candidate") {
    throw new Error("D11 successor UX schema or lifecycle is not admitted");
  }
  if ((await recordDigest(bundle, "bundle_digest")) !== bundle.bundle_digest) {
    throw new Error("D11 successor UX bundle digest failed");
  }
  if (bundle.source_identities.ET_C10_record_digest !== bundle.authority_extension_digest
    && bundle.authority_extension_digest !== undefined) {
    throw new Error("D11 successor authority identity failed");
  }
  const expected = {
    candidate: 12,
    current_claim: 2,
    debt_transformation: 2,
    equation_contract: 31,
    normative_object: 13,
    profile: 2,
    verification_obligation: 7,
  };
  if (bundle.population_counts.catalog !== 69) throw new Error("D11 successor catalog count failed");
  for (const [kind, count] of Object.entries(expected)) {
    if (bundle.population_counts[kind] !== count) throw new Error(`D11 successor ${kind} count failed`);
  }
  if (bundle.population_counts.forensic_API_outputs !== 60
    || bundle.population_counts.source_bound_node_projections !== 9) {
    throw new Error("D11 successor output class population failed");
  }
  const catalogIds = bundle.catalog.map((row) => row.node_id);
  if (new Set(catalogIds).size !== catalogIds.length
    || catalogIds.some((nodeId) => !bundle.views[nodeId])
    || Object.keys(bundle.views).some((nodeId) => !catalogIds.includes(nodeId))) {
    throw new Error("D11 successor catalog/view identity failed");
  }
  for (const row of bundle.catalog) {
    const output = bundle.views[row.node_id].output;
    const digestField = output.output_class === "forensic_evidence_trace"
      ? "trace_digest"
      : "projection_digest";
    if ((await recordDigest(output, digestField)) !== output[digestField]
      || row.output_digest !== output[digestField]) {
      throw new Error(`D11 successor output digest failed: ${row.node_id}`);
    }
  }
  for (const key of [
    "browser_scientific_inference",
    "browser_propagation",
    "browser_rerun_prediction",
    "browser_claim_promotion",
    "notebook_duplicates_forensic_logic",
    "paper_propagation_verified",
    "specification_or_runtime_conformance_verified",
    "GRC9_or_GRC9V3_change_authorized",
  ]) {
    if (bundle.authority[key] !== false) throw new Error(`D11 successor authority widened: ${key}`);
  }
  return bundle;
}

export function filterSuccessorCatalog(bundle, { query = "", scope = "all", kind = "all" } = {}) {
  const needle = query.trim().toLocaleLowerCase();
  return bundle.catalog.filter((row) => {
    if (scope !== "all" && row.scope !== scope) return false;
    if (kind !== "all" && row.kind !== kind) return false;
    if (!needle) return true;
    return `${row.identifier} ${row.label} ${row.kind} ${row.scope}`.toLocaleLowerCase().includes(needle);
  });
}

export function successorView(bundle, nodeId) {
  const value = bundle.views[nodeId];
  if (!value) throw new Error(`D11 successor view is not compiled: ${nodeId}`);
  return value;
}

export function outputRows(view) {
  const output = view.output;
  if (output.output_class === "forensic_evidence_trace") return output.rows;
  return [{
    row_id: `${view.node.node_id}:projection`,
    classification: "source_bound_graph_projection",
    payload: view.node.attributes,
    source_ref: output.source_ref,
    edge_refs: output.edge_refs,
  }];
}
