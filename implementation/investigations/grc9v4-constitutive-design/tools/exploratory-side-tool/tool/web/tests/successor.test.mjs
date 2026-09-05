import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import test from "node:test";

import { recordDigest } from "../src/bundle.js";
import {
  filterSuccessorCatalog,
  outputRows,
  successorView,
  verifySuccessorBundle,
} from "../src/successor.js";

const bundlePath = new URL("../../../records/ETC11D11SuccessorUXBundle.json", import.meta.url);

async function loadBundle() {
  return JSON.parse(await readFile(bundlePath, "utf8"));
}

test("D11 successor UX verifies and exposes the complete source-bound catalog", async () => {
  const bundle = await verifySuccessorBundle(await loadBundle());
  assert.equal(bundle.catalog.length, 69);
  assert.equal(filterSuccessorCatalog(bundle, { scope: "D11-C" }).length, 25);
  assert.equal(filterSuccessorCatalog(bundle, { scope: "D11-G9" }).length, 44);
  assert.deepEqual(
    filterSuccessorCatalog(bundle, { kind: "current_claim" }).map((row) => row.identifier),
    ["D11-C-CL-O-001", "D11-G9-CL-N-001"],
  );
});

test("D11 claims, contracts, debts, profiles, and obligations are inspectable", async () => {
  const bundle = await verifySuccessorBundle(await loadBundle());
  for (const nodeId of [
    "current_claim:D11-C-CL-O-001",
    "debt_transformation:D11-G9-DEBT-CANONICAL-PORT-ALLOCATION",
    "equation_contract:D11-C-EC-C-J0-CURRENT",
    "normative_object:GRC9-EXPANSION-EXACT-BOUNDARY-MAP",
    "profile:C-HM-STIFFNESS-BASELINE-v1",
    "verification_obligation:D11-G9-VERIFY-PAPER-THEN-SPECIFICATION-PROPAGATION",
  ]) {
    const view = successorView(bundle, nodeId);
    const rows = outputRows(view);
    assert.ok(rows.length > 0, nodeId);
    assert.ok(rows.every((row) => row.source_ref?.record_digest), nodeId);
    assert.ok(rows.some((row) => row.edge_refs?.length), nodeId);
  }
});

test("D11 successor UX fails closed on bundle, trace, and authority tampering", async () => {
  const bundle = await loadBundle();
  const stale = structuredClone(bundle);
  stale.source_identities.ET_C10_record_digest = "0".repeat(64);
  await assert.rejects(() => verifySuccessorBundle(stale), /bundle digest failed/);

  const trace = structuredClone(bundle);
  trace.views["current_claim:D11-C-CL-O-001"].output.rows[0].classification = "normative";
  trace.bundle_digest = await recordDigest(trace, "bundle_digest");
  await assert.rejects(() => verifySuccessorBundle(trace), /output digest failed/);

  const widened = structuredClone(bundle);
  widened.authority.browser_claim_promotion = true;
  widened.bundle_digest = await recordDigest(widened, "bundle_digest");
  await assert.rejects(() => verifySuccessorBundle(widened), /authority widened/);
});
