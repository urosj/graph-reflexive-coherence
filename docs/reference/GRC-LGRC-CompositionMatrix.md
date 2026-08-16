# GRC/LGRC Composition Matrix

**Status:** Iteration 108 directional composition matrix frozen
**Pathway registry:** [`grc-lgrc-causal-pathway-contracts.json`](../../specs/grc-lgrc-causal-pathway-contracts.json)
**Evidence crosswalk:** [`grc-lgrc-causal-pathway-evidence-crosswalk.json`](../../specs/grc-lgrc-causal-pathway-evidence-crosswalk.json)
**Machine matrix:** [`grc-lgrc-causal-pathway-composition-matrix.json`](../../specs/grc-lgrc-causal-pathway-composition-matrix.json)

## Purpose

This matrix classifies directional crossings between independently grounded
pathway stages. It does not execute new behavior or upgrade either endpoint.

> Endpoint test coverage of both pathways is not evidence for the crossing.
> `lawful_native` requires source semantics and current evidence for the
> crossing itself.

## Status Meanings

| Status | Meaning |
| --- | --- |
| `lawful_native` | The crossing exists in source semantics, has current crossing evidence, and adds no load-bearing external relation. Configured residue can still bound the claim. |
| `lawful_with_explicit_adapter` | A named adapter performs a lawful crossing while retaining ownership of the mapping. |
| `diagnostic_only` | The crossing produces a bounded readout, not ordinary constitutive behavior. |
| `producer_mediated` | A producer supplies a load-bearing relation and remains part of the claim. |
| `unsupported_missing_crossing` | Endpoint mechanics exist, but the required source read/call relation is absent. |
| `invalid_relabel` | Mechanics or records exist, but the proposed composition claim erases authority or scope. |

## Frozen Matrix

| ID | Directional composition | Status | Source refs | Crossing evidence refs | Adapter / owner | Claim ceiling |
| --- | --- | --- | ---: | ---: | --- | --- |
| `CMP-01` | GRC transport into synchronous continuity | `lawful_native` | 2 | 1 | `none` / `native` | Native synchronous transport-to-continuity mechanics only. |
| `CMP-02` | Packet schedule through debit and arrival credit | `lawful_native` | 3 | 1 | `none` / `native` | Native packet debit/arrival mechanics; route, amount, and schedule remain supplied. |
| `CMP-03` | GRC flux into bounded packet work | `producer_mediated` | 0 | 2 | `flux_to_packet_adapter` / `experiment_or_consumer_producer` | Producer-mediated GRC-flux-to-LGRC-packet candidate; not native causal admission. |
| `CMP-04` | LGRC checkpoint into explicit GRC diagnostic reconstruction | `diagnostic_only` | 2 | 1 | `prepare_lgrc9v3_grc9v3_diagnostics` / `library_helper_invoked_by_caller` | Explicit bounded diagnostic reconstruction only. |
| `CMP-05` | Diagnostic reconstruction relabeled as ordinary LGRC behavior | `invalid_relabel` | 0 | 0 | `none` / `none` | No ordinary LGRC behavior claim is allowed. |
| `CMP-06` | Sink compatibility into route scheduling | `unsupported_missing_crossing` | 0 | 0 | `none` / `none` | Unsupported until an explicit admission and scheduling relation is supplied. |
| `CMP-07` | Native arbitration selection into collapse commit | `lawful_native` | 1 | 1 | `none` / `native` | Native arbitration-to-collapse commit mechanics; candidate and score formation remain external/configured. |
| `CMP-08` | External score formation relabeled as native route formation | `invalid_relabel` | 1 | 0 | `none` / `external_or_configured_candidate_producer` | Native selection over supplied candidates only. |
| `CMP-09` | Basin assignment into later transport | `unsupported_missing_crossing` | 0 | 0 | `none` / `none` | Current basin assignment may be described, not claimed as transport mediation. |
| `CMP-10` | Event queue mutation relabeled as causal eligibility | `invalid_relabel` | 2 | 0 | `none` / `none` | Queue mutation supports scheduled execution, not native causal eligibility. |
| `CMP-11` | Configured route relabeled as native formed role | `invalid_relabel` | 1 | 0 | `none` / `configuration_or_producer` | Configured-route packet production only. |
| `CMP-12` | Route surplus into packet continuation | `lawful_native` | 1 | 1 | `none` / `native_with_configured_semantics` | Native mechanics for configured surplus-to-packet continuation. |
| `CMP-13` | Outward flux and front capacity into boundary birth | `lawful_native` | 1 | 1 | `none` / `native_with_configured_semantics` | Native configured boundary-birth mechanics only. |
| `CMP-14` | Boundary-birth admission relabeled as generic packet admission | `invalid_relabel` | 1 | 0 | `none` / `none` | Boundary-birth eligibility remains topology-specific. |
| `CMP-15` | Causal spark candidate into mechanical refinement | `lawful_native` | 1 | 1 | `none` / `native_with_configured_semantics` | Native configured spark-to-refinement mechanics. |
| `CMP-16` | Arbitrated collapse into lineage and active-state transport | `lawful_native` | 1 | 2 | `none` / `native_with_configured_semantics` | Native commit and state-transport mechanics; candidate formation remains separate. |
| `CMP-17` | Derived history into temporary conductance and later flux | `producer_mediated` | 0 | 2 | `N31_C2_exact_history_closure` / `experiment_producer` | Producer-mediated exact-history conductance candidate; not a native read path. |
| `CMP-18` | Ledger persistence into native Read-Back | `unsupported_missing_crossing` | 0 | 0 | `none` / `none` | Ledger persistence and replay identity only. |
| `CMP-19` | Restoration identity relabeled as unrestricted identity | `invalid_relabel` | 1 | 0 | `none` / `none` | Versioned restoration/replay identity only. |
| `CMP-20` | Feedback eligibility producer into packet mechanics | `producer_mediated` | 1 | 1 | `feedback_eligibility_producer` / `installed_producer` | Producer-mediated feedback eligibility followed by native packet mechanics. |
| `CMP-21` | Packet arrival into causal pulse surface emission | `lawful_native` | 1 | 1 | `none` / `native_with_configured_semantics` | Native configured packet-to-surface recording mechanics. |
| `CMP-22` | Transported surface lineage into feedback scheduling | `producer_mediated` | 1 | 1 | `feedback_eligibility_producer` / `installed_producer` | Producer-mediated lineage-aware feedback scheduling. |
| `CMP-23` | Collapse commit into surface lineage reabsorption | `lawful_native` | 1 | 2 | `none` / `native_with_configured_semantics` | Native configured topology-to-surface-lineage mechanics. |
| `CMP-24` | Arbitration topology commit into multi-basin records | `diagnostic_only` | 1 | 1 | `none` / `runtime_diagnostic_hook` | Diagnostic records over a committed native/configured topology event. |
| `CMP-25` | Snapshot through load/reset and restoration validation | `lawful_native` | 3 | 1 | `none` / `native_utility` | Versioned restoration/reset/replay utility mechanics. |
| `CMP-26` | GRC front-capacity state into LGRC boundary-birth runtime | `lawful_with_explicit_adapter` | 2 | 1 | `build_lgrc9v3_corrected_cascade_runtime` / `library_construction_adapter_invoked_by_caller` | Lawful explicit construction adapter; not native cross-runtime formation or inherited event history. |

The machine matrix records state, temporal, spatial, and budget compatibility;
authority retained/transferred; adapter ownership; information loss; shared
carrier and interaction terms; controls; endpoint refs; crossing source and
evidence refs; claim ceilings; and blocked relabels.

## Direction And Authority

`A -> B` supplies no evidence for `B -> A`. If a caller, adapter, producer, or
experiment controller supplies direction, funding, eligibility, scheduling,
commitment, or reception authority, that owner remains visible even when both
endpoint mutations use native runtime mechanics.

## Remaining Boundary

Iteration 108 grounds representative crossings. It does not establish a
universal composition algebra. A composition status is not a maturity score:
a `lawful_native` row can remain narrow, default-off, configured, or bounded by
its recorded lifecycle and portability evidence. An
`unsupported_missing_crossing` row records absence under the frozen source and
evidence boundary; it does not by itself authorize a generic extension.

No composition row establishes ecology, agency, native Read-Back, or N32.
Iteration 109 may derive selection semantics from the registry, crosswalk, and
this matrix; it cannot invent a missing crossing.
