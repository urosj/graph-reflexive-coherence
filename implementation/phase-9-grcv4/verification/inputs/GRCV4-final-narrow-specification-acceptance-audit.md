# Final Narrow Acceptance Audit of the GRC-v4 Specification Release

**Audit date:** 2026-09-05
**Audited release:** `grcv4_specification_release_manifest_v2`
**Release ID:** `grcv4-spec-release-sha256:9f4c8fe5b57b1c477d834a3e4dae3f98a2b18c70e6e7f598e3c9652170c8645f`
**Audit scope:** the final correction surfaces requested after the preceding acceptance audit; no reopening of D10, D11-C, D11-G9, the proposal, or the substrate paper.

## 0. Final verdict

The corrected specification release **passes this final targeted acceptance audit**.

The previously remaining vector defect and three release-hardening items are closed:

1. cyclic covariance now rotates rows, columns, and branches simultaneously;
2. reflection now acts on the whole row-column chart and flips chirality;
3. metamorphic vectors identify their base and expected target vectors and bind an exact normalization policy;
4. schema-negative cases are separated from post-schema semantic negatives;
5. multiple information-loss classes have one exact canonical order and a checked multi-loss receipt identity;
6. the port-graph content payload is explicitly separated from its digest envelope.

Independent verification also confirms that the vector and release builders reproduce their published outputs deterministically, the current release checksum and identity are exact, and the supplied schema/vector/specification surfaces are mutually consistent.

### Acceptance disposition

```text
scientific equations and claim boundaries             = unchanged and accepted
D11-C implementation contract                         = pass
D11-G9 implementation contract                        = pass
public state/result/event contract                     = pass
schema and semantic-admission partition                = pass
canonical identity and subdigest contract              = pass
GRC9V4 exact and metamorphic plan vectors               = pass
release/checksum integrity                             = pass

specification release accepted as implementation source = yes
further specification-design audit before implementation = no
runtime conformance established                         = no
implementation phase activated by current gate          = no
new scientific investigation required                   = no
```

The specification is now technically fit to be frozen as the authoritative preimplementation contract. Project governance remains separate: the supplied correction gate still records `implementation_authorized = false` and routes next to `GRCV4_GRC9V4_implementation_review`. Activating that next gate is an authorization step, not a remaining specification defect.

---

## 1. Audited artifacts

| Repository artifact | Supplied audit file | SHA-256 | Release binding |
|---|---|---|---|
| `specs/grc-v4-conformance-vectors.json` | `grc-v4-conformance-vectors(2).json` | `ab12e2ffe02e9a9267eca9bdc3ca9361c0cf973cb87917d0eb090d3d68654ce4` | pass |
| `specs/grc-v4-contract-schema.json` | `grc-v4-contract-schema(2).json` | `3fd072fc8c2b315f1b5dc32a4e4821a5082b5f3fc9d9a4794c007419a7aa0bea` | pass |
| `specs/grc-common-interface-v4-ext.md` | `grc-common-interface-v4-ext(4).md` | `7d5be95242619fcaaae7ea5d8e950b3f335efe9a81492e67e6baa91c4643bc26` | pass |
| `specs/grc-9-v4-spec.md` | `grc-9-v4-spec(4).md` | `7552166d5dd60308ffe56934cf187a74d62296673c8c6b64320f7e57c7310262` | pass |
| `specs/grc-v4-conformance-fixtures.json` | `grc-v4-conformance-fixtures(3).json` | `90b4f4fd5b259f94363a29e23715af0450bef944002f8e611f23efabc9c7043a` | pass |
| `specs/grc-v4-source-manifest.json` | `grc-v4-source-manifest(3).json` | `23a6182e5e469b7445ccc36871234ad0227d0b87b3718bc140afbcc65530e85b` | pass |
| correction gate | `GRCV4SpecificationEngineeringCorrectionGate.json` | `57f2e8e634ae362933e94e72f634141e989dc357858940a4e5a4342dfc530f73` | pass |
| phase-aware audit | `audit_grcv4_post_d10_specifications.py` | `fccf5d7b6e1da64ab7c826d66928a4bba12687608bb6a0a128825e9e9010001b` | pass |
| vector builder | `build_grcv4_specification_vectors.py` | `4a09ea851bf24e8dec748f033f9b4e97e7eefd74458b4351cabb835afc302c7f` | pass |
| release builder | `build_grcv4_specification_release.py` | `26d8a3c5aeec49fc5e0e2da465c80ee30dac1014cc1beedcf0232afcc5839bf9` | pass |
| release manifest | `grc-v4-specification-release(2).json` | `bba0bb649bc2e80c5bfa99f96bd5824bbdda3b3fbc87fb68c3e3a59da1cee46b` | checksum target |
| detached checksum | `grc-v4-specification-release(2).sha256` | `50b20509b84a6b21f3036ecb1d7e13861f662bc8319873c5321fc0317ada7e33` | pass |

Every supplied artifact that appears in the release identity matches its bound hash.

The release binds additional unchanged scientific, provenance, registry, and phase-boundary files that were not requested again for this narrow pass. This audit therefore reattests the corrected surfaces and the content-addressed release construction, not every byte of every historical release member from scratch.

---

## 2. Release integrity

The detached checksum states:

```text
bba0bb649bc2e80c5bfa99f96bd5824bbdda3b3fbc87fb68c3e3a59da1cee46b
  specs/grc-v4-specification-release.json
```

The actual SHA-256 of the supplied release file is the same value.

Independent canonicalization of `release_identity_payload` gives:

```text
9f4c8fe5b57b1c477d834a3e4dae3f98a2b18c70e6e7f598e3c9652170c8645f
```

which exactly reproduces both:

```text
release_id =
  grcv4-spec-release-sha256:9f4c8fe5b57b1c477d834a3e4dae3f98a2b18c70e6e7f598e3c9652170c8645f

bundle_digest =
  sha256:9f4c8fe5b57b1c477d834a3e4dae3f98a2b18c70e6e7f598e3c9652170c8645f
```

The 29 identity bindings are sorted and path-unique.

The release builder was also executed through its published deterministic construction using the release-bound file hashes. It regenerated the supplied release JSON byte-for-byte.

---

## 3. Deterministic vector rebuild

The supplied vector builder was placed at its canonical repository depth with the supplied schema and fixture catalog. The D11-C witness script itself was not among the requested files, so its already published SHA-256 was supplied to the builder as the immutable witness binding; no vector content or builder logic was changed.

The generated bytes were exactly equal to the supplied vector file:

```text
generated size = 1,036,286 bytes
supplied size  = 1,036,286 bytes
byte equality  = true
SHA-256        = ab12e2ffe02e9a9267eca9bdc3ca9361c0cf973cb87917d0eb090d3d68654ce4
```

The build itself executes its covariance comparisons and would fail if either transported D52 plan differed from its declared target.

---

## 4. Canonicalization and identity verification

An independent Node.js implementation of RFC 8785/JCS recomputed the concrete canonicalization and identity surfaces rather than calling the Python builder's canonicalizer.

Results:

```text
canonicalization / canonical bytes / typed IDs / event IDs /
failure-receipt IDs / release ID assertions = 121 / 121 pass
```

The checked population includes:

- 3 canonicalization vectors;
- 12 top-level identity vectors;
- 10 subdigest identity vectors;
- 17 GRC9V4 expansion event identities;
- 1 generic mapped-event identity;
- 7 failure-receipt identities;
- the release identity and bundle digest.

A separate differential pressure test compared the Python vector builder's binary64 number spelling with ECMAScript `JSON.stringify` for 50,000 finite randomly sampled binary64 values plus threshold and extreme cases. It found zero mismatches.

---

## 5. JSON Schema and semantic-admission partition

The machine schema passes `Draft202012Validator.check_schema`.

A total of 375 schema assertions passed across:

- resolved parameters;
- generic and GRC9V4 identities;
- Candidate A and Candidate C profile templates;
- port-graph payload and digest envelope;
- subdigest preimages;
- all 17 expansion requests, event identities, target states, reset payloads,
  history policies, receipts, commits, and lifecycle payloads;
- the affine generic mapped event;
- 7 pre-admission failure inputs and failure receipts;
- 2 step-result vectors;
- schema-negative and post-schema semantic-negative test wrappers.

The two cases that strict JSON Schema already rejects are now correctly stored under `schema_negative_vectors`:

```text
SCHEMA-REJECT-PROFILE-FIELD-MISMATCH
SCHEMA-REJECT-HISTORY-SUBJECT-MISMATCH
```

The remaining five negative cases are shape-valid and remain owned by the named semantic admission validator:

```text
resource_distribution_unit_sum
resource_transform_dimensions
growth_phase_matches_remainder
target_W_C_tr_matches_live_edges
identity_payload_matches_resolved_parameters
```

This closes the former layer-classification ambiguity without weakening the schema.

---

## 6. Canonical information-loss ordering

The interface now fixes the sole ordering:

```text
candidate_history_loss
carrier_history_loss
v4_surface_projection
whole_state_delegate_crossing
```

with absent classes omitted, no duplicates, and no synthetic `none` value in `ReceiptCore.information_losses`.

The schema enumerates all 16 ordered subsets of those four classes. The concrete multi-loss receipt vector contains:

```json
[
  "candidate_history_loss",
  "carrier_history_loss"
]
```

and its independently reproduced identity is:

```text
grc-receipt-sha256:c968a71de00b275db446ab20f0ebde0de6d1159bee9694aeeeb8620a8f503e9d
```

This closes the prior possibility that two implementations could hash the same set of losses in different orders.

---

## 7. Port-graph payload and digest envelope

The specialization now states one exact two-level construction:

```text
GRC9V4PortGraphPayload
  = schema_version + live_node_ids + edges

GRC9V4SerializedPortGraph
  = payload fields + graph_digest
```

The digest is computed only from the content payload:

```text
graph_digest =
  "grc-graph-sha256:" + SHA256(JCS(port_graph_payload))
```

`graph_digest` is excluded from its own preimage. Admission must project the envelope back to the content payload, recompute the digest, and reject mismatch.

The schema and the dedicated envelope vector agree with this wording.

---

## 8. GRC9V4 exact plan and lifecycle vectors

Independent graph checks were applied to all 17 concrete expansion vectors.

```text
vectors                                       = 17
independent invariant assertions              = 355
failures                                      = 0
```

The assertions cover:

- unique node IDs, edge IDs, and local endpoint-port occupancy;
- nine exact inherited boundary edges;
- identical internal port type at both endpoints;
- the accepted positive and negative primary spines;
- connected, acyclic internal module graph;
- exactly `n - 1` internal edges;
- external capacity `7n + 2` and minimality above the four-node floor;
- exact active/inactive growth-phase semantics;
- row and column imbalance at most one;
- positive, exact-edge-set-complete target `W_C_tr`;
- exact target resource coverage and conservation;
- truthful `C_OS` no-carrier receipts;
- a genuine non-null `C_PC` source carrier followed by whole-carrier reset and
  `carrier_history_loss`.

The affine generic mapped event also independently reconstructs:

```text
source resource = [1, 2]
target resource = [1, 2, 0.5]
charge delta    = 0.5
target Q_target = 3.5
```

All 7 rollback vectors preserve both state and lifecycle digests, commit no persistent receipt, and return typed failures.

---

## 9. Corrected covariance vectors

### 9.1 Cyclic rotation

The final port permutation is the simultaneous chart rotation

\[
(a,b)\longmapsto(a\oplus_3 1,b\oplus_3 1),
\]

encoded as:

```json
{
  "1": 5,
  "2": 6,
  "3": 4,
  "4": 8,
  "5": 9,
  "6": 7,
  "7": 2,
  "8": 3,
  "9": 1
}
```

with branch permutation:

```json
{"1": 2, "2": 3, "3": 1}
```

It transports:

```text
G9-EXPAND-D52-CHIRALITY-POSITIVE-PHASE-1
```

exactly to:

```text
G9-EXPAND-D52-CHIRALITY-POSITIVE-PHASE-2
```

under the declared normalization policy. Chirality remains `+1`; phase `1`
becomes `2`.

### 9.2 Reflection

The final port permutation is the whole-chart reflection

\[
(a,b)\longmapsto(4-a,4-b),
\]

encoded as:

```json
{
  "1": 9,
  "2": 8,
  "3": 7,
  "4": 6,
  "5": 5,
  "6": 4,
  "7": 3,
  "8": 2,
  "9": 1
}
```

with branch reflection:

```json
{"1": 3, "2": 2, "3": 1}
```

It transports:

```text
G9-EXPAND-D52-CHIRALITY-POSITIVE-PHASE-1
```

exactly to:

```text
G9-EXPAND-D52-CHIRALITY-NEGATIVE-PHASE-3
```

under normalization. Chirality flips to `-1`; phase `1` becomes `3`.

### 9.3 Independent result

```text
source-edge ordering permutation              = pass
cyclic transported plan equals target exactly = pass
reflection transported plan equals target     = pass
edge differences in either corrected case     = 0
```

The vectors now also bind:

```text
base_vector_id
expected_target_vector_id
normalization_policy_id
```

and the normalization policy specifies event namespace, branch-indexed node
and edge roles, old boundary IDs, external labels, endpoint ports, chirality,
phase, sorting, and exact target comparison.

---

## 10. Candidate C numerical witness

The D11-C T3a vector was independently recomputed from its incidence matrix,
Hodge data, selector, retained modulation, mobility, potential, resolvent, and
current closure.

Every expected quantity agrees within the declared `1e-12` absolute tolerance:

```text
baseline potential                         = pass
baseline current J0_C                      = pass
total current J_C                          = pass
read current                               = pass
retained H1 diagonal                       = pass
closure residual                           = pass
charge residual                            = pass
baseline dissipation                       = pass
retained-geometry-off direct-path effect   = pass
```

The largest observed difference was ordinary binary64 roundoff,
`5.55e-17`, in the retained-geometry control norm.

---

## 11. Source and builder surfaces

All three supplied Python tools compile successfully.

The vector builder's current hash is bound both by the vector file and the
release. Its own internal construction rejects a covariance drift before
writing output.

The release builder's current hash is release-bound. Reconstructing its output
from the bound artifact map and current source manifest produced the supplied
release JSON byte-for-byte.

The two Markdown contracts parse as GFM/MathJax. Pandoc reports only its normal
inability to render several advanced TeX expressions as native HTML math; it
reports no Markdown structural failure.

---

## 12. Remaining holds

The remaining holds are correctly classified as **runtime conformance holds**,
not gaps in specification authority:

- Candidate A numerical and GRC9V4 expansion vectors;
- per-realization executable step vectors;
- RG2b evaluator certification;
- child stabilization, completed spark, and hierarchy tracking;
- 40 exact GRC9V3 disabled-delegate executions;
- snapshot/reset/migration runtime execution;
- generic mapped-event runtime execution;
- cross-implementation charge edge cases;
- deep-immutability runtime tests;
- runtime-generated receipt evidence;
- runtime D52 and covariance execution before arbitrary-size mechanical
  refinement conformance is advertised.

These limits determine which capabilities an implementation may claim. They
do not prevent implementation against the frozen contract.

---

## 13. Governance boundary

The technical release is accepted as an implementation source, but the current
correction gate explicitly says:

```text
implementation_authorized = false
runtime_or_src_tests_change_authorized = false
next_gate = GRCV4_GRC9V4_implementation_review
```

Therefore the appropriate next project action is to open or accept the
implementation-review authority. That step should not revisit the V4
mathematics or specification design unless implementation discovers an actual
contradiction.

---

## 14. Final acceptance statement

Release

```text
grcv4-spec-release-sha256:
9f4c8fe5b57b1c477d834a3e4dae3f98a2b18c70e6e7f598e3c9652170c8645f
```

is accepted by this final targeted audit as the **normative
preimplementation GRCV4/GRC9V4 specification release**.

It is suitable to serve as the authoritative source for implementation,
subject to the explicit profile- and capability-specific runtime holds.

No further specification-design audit is required before implementation.
The next audit should be a staged implementation/runtime conformance audit
against this frozen release rather than another paper/specification pressure
round.
