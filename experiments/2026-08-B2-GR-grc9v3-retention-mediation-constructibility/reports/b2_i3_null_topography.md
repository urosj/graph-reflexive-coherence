# B2-GR Iteration 3 - Null Topography

This companion explains the structure hidden by the 52 flat active-null rows.
It is an interpretation of the I3 validator surface, not a new source-current
experiment and not additional GRR evidence.

```text
source_artifact = outputs/b2_i3_active_nulls.json
source_payload_sha256 = a9749a11bde99da30a40aeea20114a8fabe76bf1db2b55d62d8ac79824d04d6a
null_count = 52
rung_blocker_count = 32
non_global_governance_guard_count = 20
suffix_violation_count = 0
sentinel_pair_count = 52
```

[Open the interactive null topography](b2_i3_null_topography.html).

## Two Kinds Of No

The 52 nulls are not 52 equivalent rejections.

The first 32 are global `rung_blocker` rows. Each rejects a candidate surface
needed for one or more GRR rungs. They are the rung-admission layer: a failed
formation, attribution, mediation, or required-control gate prevents the
dependent rung and every stronger rung from being supported by that row.

The other 20 rows are non-global governance or typing guards:

| Effect scope | Rows | Effect |
| --- | ---: | --- |
| `lane_specific_blocker` | 8 | Rejects only the claimed lane while preserving a typed alternative. |
| `route_only` | 5 | Blocks a search, closeout, or extension inference without demoting an independently valid witness. |
| `claim_only_blocker` | 4 | Rejects a stronger label without changing the underlying witness rung. |
| `duplicate_only` | 2 | Prevents double counting while preserving one physical witness. |
| `robustness_only` | 1 | Narrows scope without turning a clean single witness into failure. |

Calling the first layer purely *physical* would be too strong. Some rung
blockers are mechanical or causal failures, while others are provenance,
matching, numerical, or required-assumption failures. The accurate distinction
is therefore:

```text
global rung-admission barriers
versus
non-global interpretation / route / robustness / deduplication guards
```

Lane-specific rows can have `lane_blocked_rungs`, but their global
`blocked_rungs` remain empty. This prevents a rejected durable-`W`, event-free,
native-probe, or other claimed lane from silently erasing an independently
valid retained-`C`, eventful, diagnostic, or producer-mediated alternative.

## The Rung Staircase

Every one of the 32 global rung masks is a contiguous suffix of:

```text
GRR1 -> GRR2 -> GRR3 -> GRR4 -> GRR5
```

There are no holes. No row blocks a stronger rung while reopening a weaker
prerequisite. The lowest rung blocked is therefore the compact topological
identity of each global null:

| Lowest blocked rung | Nulls | Meaning |
| --- | ---: | --- |
| `GRR1` | 9 | Native formation or base admissibility is unavailable. |
| `GRR3` | 11 | Formation/persistence may remain, but slow-cluster attribution cannot proceed. |
| `GRR4` | 6 | Lower retention evidence may remain, but matched later mediation is blocked. |
| `GRR5` | 6 | Lower evidence may remain, but required qualification/control closure is blocked. |

No row first seals `GRR2`: under this frozen null set, failures that prevent
post-input persistence also invalidate the preceding formation/admissibility
surface or are routed into a typed non-global lane.

The staircase is an evidence-admission dependency structure. It is not itself
evidence that current GRC9V3 mechanically cannot reach a rung.

## Why A Row Is Null

Two fields jointly give the reason:

```text
expected_primary_disposition x control_family
```

`expected_primary_disposition` says how the row closes, such as bounded
negative, source/provenance failure, invalid candidate, failed assumption,
failed required control, unresolved search, outside-envelope result, or
duplicate. `control_family` says which causal or governance boundary the reason
protects: formation, temporal attribution, branch relation, mediation,
reset/swap/bypass, lineage, or search/claim governance.

This typed pair is more informative than a generic failed boolean. It separates,
for example, a malformed candidate from a clean negative, and unresolved search
coverage from evidence of impossibility.

## Null And Sentinel As A Pair

Each atomic null has a paired pass-through sentinel under the same rule vector:

```text
sentinel:
  target gate = true
  all other gates = true
  result = validator pass-through
  positive_evidence_eligible = false

atomic null:
  target gate = false
  all other gates = true
  result = prohibited interpretation rejected with typed effect
  positive_evidence_admissible = false
```

The pair validates the adjudicator, not the scientific mechanism. The sentinel
is deliberately **not evidence admissible**; it only proves the validator does
not reject an all-gates-pass fixture. The atomic row proves that flipping one
specific frozen gate activates the intended blocker without an unrelated
earlier rejection.

The artifact binds the reference, tested, and paired-atomic gate vectors by
semantic digest. All 52 pairs reconstruct exactly and every sentinel passes.

## Rebuild

```bash
.venv/bin/python experiments/2026-08-B2-GR-grc9v3-retention-mediation-constructibility/scripts/build_i3_null_topography.py
```

The builder validates the source envelope, scope counts, global suffix masks,
non-global rung preservation, atomic/sentinel vector bindings, and non-evidence
sentinel status before writing the HTML companion.
