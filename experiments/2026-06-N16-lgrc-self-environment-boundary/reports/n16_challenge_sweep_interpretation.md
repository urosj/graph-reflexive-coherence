# N16 Challenge Sweep Interpretation

This is an interpretation of `reports/n16_challenge_sweep_matrix.md`, not an
additional matrix run.

## Core Reading

Iteration 4 is a good first N16 MVP scientific result. It holds `B2` fixed,
runs `C0-C5`, records differentiated outcomes, keeps AP6 provisional, and
identifies why Iterations 5-6 are justified.

The most important ceiling is:

```text
accepted_b2_challenge_sweep_partial_mvp_no_ap6
```

The matrix tells a coherent requirements-discovery story:

```text
B2 survives quiet/noise/structured-false-positive pressure.
B2 is partial under directional flux and breach pressure.
B2 fails under shared-medium / coupled-neighbor pressure.
```

## Row Interpretation

```text
C0 supported - quiet anchor
C1 supported - bounded noise tolerance
C2 partial - flux leakage exceeds quiet ceiling
C3 supported - structured external false-positive rejected
C4 partial - breach/reclosure pressure exposes need for B3
C5 rejected - shared-medium leakage / merge pressure exceeds B2 policy
```

The values move in the expected direction: quiet has low leakage and high
stability; noise degrades mildly; flux and breach degrade substantially; and
shared-medium pressure is the strongest failure case.

## Supported Claims

Iteration 4 supports only provisional AP6-relevant requirements discovery:

```text
B2 is usable for MVP challenge testing.
B2 remains bounded under C0 quiet reference.
B2 tolerates bounded unstructured perturbation at the tested noise amplitude.
B2 rejects structured external coherence as a false-positive self-boundary.
Directional flux is harder boundary pressure than noise.
Breach/reclosure requires B3-style follow-up.
Shared-medium separability requires B4-style follow-up.
```

It does not support:

```text
final AP6 closeout
B3 regulated repair/reabsorption
B4 multi-basin separability
native support
selfhood
agency
resource assimilation
structured environment assimilation
```

## Requirements Split

The strongest scientific output is that `B2` is enough for quiet/noise/false-
positive rejection, but not enough for flux, breach, or shared-medium
conditions.

```text
B2 sufficient:
  C0 quiet anchor
  C1 bounded noise
  C3 structured external false-positive rejection

B2 insufficient / partial:
  C2 directional flux
  C4 breach/reclosure pressure

B2 rejected:
  C5 shared-medium / coupled-neighbor pressure
```

This justifies the next extensions:

```text
Iteration 5:
  compare B0-B4 under the same C2 flux pressure to identify which boundary
  state improves retention, leakage, and asymmetry.

Iteration 6:
  run B3 x C4 and B4 x C5 because Iteration 4 exposed those as missing
  requirements.
```

## Double Checks

1. The fixed `B2` audit is backed by row-derived digest validation. The
   canonical digest is computed from the Iteration 3 `B2_C0` source row fields,
   not from a hand-copied metadata block.

   ```text
   recomputed = e60b71228ee2411e95a77f1724f2c37f6738a8192d2eeab974a385b4dbb2fda0
   recorded   = e60b71228ee2411e95a77f1724f2c37f6738a8192d2eeab974a385b4dbb2fda0
   match      = true
   ```

2. `same_boundary_side_assignments = true` is intentional for Iteration 4. The
   sweep compares challenge effects against the initial fixed `B2` boundary
   assignment; post-challenge drift, leakage, and merge pressure are measured
   as effects. Iterations 5-6 should distinguish initial/frozen side assignment
   from observed post-challenge drift surfaces.

   ```text
   unique_boundary_side_assignments_across_rows = 1
   post_challenge_drift_surface_deferred_to = [5, 6]
   ```

3. The numeric floors and ceilings are recorded in the JSON artifact under
   `challenge_thresholds`, not only in Markdown. This is important for
   Iteration 5, which should reuse the same C2 pressure rather than retune it.

   ```text
   internal_support_floor = 0.85
   internal_coherence_floor = 0.84
   minimum_coherence_margin_floor = 0.52
   quiet_leakage_ceiling = 0.12
   flux_leakage_warning = 0.12
   breach_reclosure_floor = 0.7
   shared_medium_basin_separation_floor = 0.7
   ```

4. The C5 rejection is a reference failure and should be preserved. It should
   motivate B4, not be fixed by retuning B2.

   ```text
   row_decision = rejected
   boundary_claim_allowed = false
   final_ap6_supported = false
   leakage_ratio = 0.31
   boundary_stability_score = 0.32
   basin_separation_score = 0.38
   failure_mode = shared_medium_leakage_and_merge_pressure_exceed_B2_policy
   ```

## Review Hardening

The Iteration 4 review exposed several audit risks that are now recorded in the
artifact rather than left as interpretation-only notes.

The metric values are now explicitly marked as deterministic MVP stress-probe
construction values derived from the fixed Iteration 3 `B2` baseline. They are
not independent physics simulation outputs. This keeps the evidentiary claim
at requirements discovery:

```text
metric_construction_rationale recorded at top level and per row
challenge_pressure_rationale recorded at top level and per row
```

The Iteration 3 provenance check now uses the stable semantic output digest,
while still recording the current file SHA-256 bytes. The file SHA can change
when generated metadata changes; the stable source-current acceptance check is:

```text
accepted_output_digest = 863dcbf79421ee5b620d047ca47949ea1e82e3169f8a0284343a532a36b6a1a1
current_output_digest  = 863dcbf79421ee5b620d047ca47949ea1e82e3169f8a0284343a532a36b6a1a1
match                  = true
```

The C2 role is now frozen as a coupling-channel case, not an unstructured
perturbation case:

```text
external_state_role = coupling_channel
perturbation_present = false
directional_flux_pressure = 0.34
```

The C4 and C5 failures now record both their extension-specific blockers and
their general threshold failures. This prevents a reader from treating breach
or shared-medium failure as only a B3/B4 scheduling note:

```text
C4 fails leakage, internal-support, and coherence-margin floors.
C5 fails leakage, internal-support, internal-coherence, and coherence-margin floors.
```

The C5 neighbor basin is explicitly synthetic:

```text
neighbor_basin_q0 = synthetic_shared_medium_stressor
claim_boundary = not source-backed B4 multi-basin separability evidence
```

The validator now enforces these review fixes: stable Iteration 3 output digest
provenance, C0 metric equivalence to the Iteration 3 `B2` reference row,
threshold-failure recording, C2 role semantics, C5 synthetic-neighbor
annotation, and `transform_count = 1` per row.

## Next-Step Guard

Proceed to Iteration 5 with C2 as the fixed stressor:

```text
Under the hard directional-flux challenge C2, which boundary-state maturity
level survives best: B0, B1, B2, B3, or B4?
```

The key guard is:

```text
Do not retune C2 to make B3/B4 look good.
Use the same C2 challenge pressure that made B2 partial.
```
