# Final Tranche 8 review — C_OS, C_CI, A_CI and A_PC

Status: **accepted by the user on 2026-10-27; bounded first-group Tranche 8 closed**.
The [closeout acceptance](./P9-Tranche8-FirstGroupAcceptance.json) pins both reviews. P9-8.6 itself was accepted on 2026-10-27. Its unchanged records
and the remaining six families retain their original scope. No production code,
numerical policy, tolerance, public support, scientific claim/debt ledger or
paper/specification changed in this review.

The [method](./P9-Tranche8-FirstGroupEndReview.md),
[mechanism extraction](./P9-Tranche8-FirstGroupMechanisms.json) and
[performance measurements](./P9-Tranche8-FirstGroupPerformance.json) are retained
with repository-relative source hashes. Checking them authenticates/extracts
existing evidence; it does not rerun a numerical campaign.

## Mechanism conclusions

**C_OS:** accepted reference evidence remains sufficient for its bounded scope.
No additional campaign or strengthening requirement was introduced.

**C_CI:** the accepted [P9-8.3C-CI validation](./P9-8.3C-CI-Validation.json)
already supplies native target roots for both roles, independent joint-equation
error bounds, and modulation/feedback/geometry path controls. The feedback
observations are:

| Target role | Represented difference | Combined full-read error | Exact-effect lower bound | Recorded discrimination ratio |
| --- | ---: | ---: | ---: | ---: |
| current | 1.83341e-10 | 2.92341e-15 | 1.83338e-10 | 9752.68 |
| reset | 2.18247e-10 | 3.26492e-15 | 2.18243e-10 | 8003.03 |

The last column is the retained criterion
`delta / (4 * combined_error + 8 * maximum_ulp)`, **not** signal/error.
These are independent formula ablations at the native selected geometry,
not alternative complete CI roots or a new profile declaration. They establish
resolved consumption of the named paths on those admitted subjects. The large
`.g/.h` first-pass/reference-geometry runs still establish root accuracy and
positive continuation without above-rounding feedback separation. The smaller
evidence does not transfer that stronger claim to the large graph. No new
diagnostic is needed for the selected bounded path-discrimination claim.

**A_CI:** all four prepared `.g` cases match the native selected joint-point
digest, geometry digest, all six primitive vectors and independent stage
records. Each native root uses the declared two evaluations. Final-C/W roots
also match their own oracle; continuity/history writing and unchanged reset
remain part of the accepted native successor.

| Prepared subject | Feedback-separated coordinates | Changed H diagonals | Nonzero H off-diagonals |
| --- | ---: | ---: | ---: |
| source/current | 116 | 0 | 1456 |
| source/reset | 127 | 0 | 1440 |
| target/current | 176 | 9 | 1550 |
| target/reset | 177 | 9 | 1534 |

Separation compares exact-root feedback with the reference-H current and the
selected coordinate's independent error bound. It is not a requirement for
every coordinate or diagonal to change. The largest-effect coordinate need not
be the best-resolved coordinate. Prepared target roles are not the actual
postbeat `.h` event pair; no all-state or whole-trajectory discrimination follows.
The required research-to-native link exists, so no new diagnostic is needed.

**A_PC:** the same witness coordinate is used for effect, combined error and
output scale in each row. Bounds and exact rational ratios are in the extraction.

| Role / poststep final read | Effect lower | Both-read error upper | Effect/error | Effect / enabled-current ULP |
| --- | ---: | ---: | ---: | ---: |
| current, step 1 | 2.48878e-15 | 2.68337e-16 | 9.27485 | 5.60424 |
| reset, step 1 | 2.48961e-15 | 1.74930e-16 | 14.23205 | 5.60609 |
| current, step 10 | 2.76013e-14 | 1.72282e-16 | 160.21054 | 31.07636 |
| reset, step 10 | 2.80860e-14 | 5.52459e-16 | 50.83814 | 31.62201 |

The enabled currents have magnitudes about 3.75–4.08. Relative effect lower
bounds range from 6.64e-16 to 6.89e-15. Small absolute effects are therefore
resolved at these points; they are not evidence by themselves of fragility.
The control holds final C/W fixed and replaces carrier-generated H with
reference H; both read errors count. Positive stored Z alone would not suffice.
The reported ULP ratio is scale context, not a newly imposed acceptance rule.
Zero-error ratios have explicit nonfinite/undefined dispositions in the extractor.

**Scope decision:** retain pointwise support. No wider parameter domain is
selected, so nearby-input pressure is not applicable to this review. No uniform
parameter tube, robustness margin or accumulated trajectory enclosure is claimed.
The successful 7/8-history companion and prior exclusions remain distinct.

## Performance and cache conclusion

**Retain the existing implementations; add no cache.** The measured costs are
real, but they do not justify weakening admission or speculatively caching
whole points/decisions before Tranche 9's unified public caller exists.

The retained large C_OS read comparison reports 141.960 s cold and 86.008 s
warm, with identical scientific-view digests and unchanged residual/conditioning
checks. Its scalar-reuse successor reports 133.920 s for a fresh read. These
are different bounded measurements, not additive speedups or whole-event rates.
Historical generic A_CI/A_PC grid comparisons also retain exact state/receipt/
snapshot parity; their timings do not establish GRC9V4 family-wide speedups.

New metadata observations use actual pre/post-event graphs: 964/5128-byte
small payloads and 42278/46462-byte large payloads, straddling the default
8192-byte validation-memo threshold. The 400-row K4 identity payload is
320853 bytes. All three modes produce identical identities/envelopes.

| Repeated entry point | Default memo | Explicit worker memo |
| --- | ---: | ---: |
| Large source graph admission + envelope | 0.142 s | 0.034 s |
| Large target graph admission + envelope | 0.153 s | 0.034 s |
| Large source K4 identity | 3.384 s | 0.092 s |

The large K4 cold call remains about 3.43 s with worker retention. This is reuse
of successful schema validation; copying/canonicalization and identity checking
still occur. Small payloads already benefit from the default memo. Changed
matrix content changes identity and a Boolean numeric impostor fails under
fresh and retained validation. The explicit research memo remains confined to
single-threaded workers; it is not a safe concurrent global configuration API.

The retained 8.6 status call takes 4.363 s and its repeat 4.365 s; selected source
retrieval takes 4.301 s. Coarse inclusive measurements attribute about 2.13 s
to checkpoint canonicalization, 0.81 s to JSON decoding, 0.57 s to encoding,
0.67 s to authentication and 0.064 s to decompression. These times overlap and
must not be summed. There is no semantic status-result cache. Authentication
checks current bytes on every request; the broad source/decompression cost is
not dominant for this selected view. A future selected-family projection could
reduce repeated canonicalization, but must preserve all identity/scope and
source-change checks. It is not needed for this bounded closeout.

The first metadata attempt used whole-call profiling and hit
the 240 s cap without retaining a result. It supports no timing conclusion.
The narrowed successful measurement uses named-call timers and omits redundant
post-event K4 cases; it retains both graph topologies. No failed-session dump
or numerical rerun was kept.

### Cache validity review

| Owner / derived fact | Exact reuse condition | Lifetime and bounds | Required fresh work |
| --- | --- | --- | --- |
| Codec successful schema validation | Complete schema bytes, definition name and canonical payload bytes | Default 128 entries × at most 8 KiB payload; worker override 8 × 4 MiB, discarded on context exit | Input detachment, canonical bytes, current asset checks, content identity; no cached failure |
| Matrix inverse/conditioning fact store | Exact represented matrix; conditioning also includes exact limit; backend and numerical-policy identity | 64 facts per operation, optional selected committed-matrix continuation; count bound, not a topology-independent byte bound | RHS/current/stage/domain admission and caller-specific conditions |
| Certified rounded-solve store | Every exact A and B coefficient, backend and policy; dimension hash only selects an equality bucket | 16 solutions, at most eight million scalar references, operation-local; not a byte bound or checkpoint state | Requested conditioning and exact rounded residuals, point construction and lifecycle publication |
| Scalar/frozen immutable owners | Facts belong to the immutable owner; detached exports cannot mutate it | Owner lifetime; no new cross-event cache selected | New owner/typed content after topology, orientation, profile or state change |
| Retained evidence views | No persistent success cache selected | One request; fresh source authentication | Changed/missing bytes, review pins, historical epochs and selected scope |

Thus topology/history/stage changes cannot reuse an admission verdict merely
because a matrix happens to match. Matrix equality permits only that matrix
fact; current/reset, dt, profile, geometry, history and certificate-domain checks
remain with their callers. Increasing graph size increases per-fact memory;
entry/reference limits must not be described as constant byte usage.

Existing focused pressure covers changed keys, schema identity, eviction,
detachment, invalid numeric types, strict post-hit conditioning/residual
rejection, backend/policy isolation, nested scopes, thread isolation and no
fallback. Fifteen acceptance/cache tests pass in this review; no native
trajectory is repeated. Five additional extraction/API/HTTP/notebook tests and three browser tests
pass for the read-only presentations: **20 focused Python tests in total**.

## Boundary and next work

The applicable `phase9_implementation_policy.current_boundary` check **passed**
in 47.287 seconds: 703 protected baseline files and 334 registered runtime
files. After these documentation-only result notes, the same maintenance roster
and all current bindings were refreshed/rechecked. No production runtime or numerical-evidence change
followed that boundary check. The earlier interrupted full wrapper remains
uncompleted; this direct current-boundary pass does not relabel that attempt. The four-family reviews are accepted;
Tranche 9 has not started. The other six families and all-ten parents stay open.
