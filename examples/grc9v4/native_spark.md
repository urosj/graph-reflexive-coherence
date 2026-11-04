# GRC9V4 native spark completion: a public workflow

This example follows an ordinary source beat through canonical nine-port
expansion, target certificate admission, actual entry into its certified domain,
two further positive beats, and one completed spark. It uses the public
`GRC9V4` interface and exact inputs from the accepted native campaigns.

The [earlier tour](README.md) covers the ordinary zero-site configurations.
The completion example uses a different, explicit quartic-site configuration
and numerical policy. Enabling a completion counter on an old configuration
does not reproduce this experiment.

All ten candidate/realization families have accepted **bounded** native
completion evidence. C_OS is the introductory example; the same script accepts
each family, with its own complete inputs, histories and proof. This does not
claim completion for arbitrary graphs, policies or initial states, general
autonomous topology change, hierarchy tracking, full conformance or G4.

## Start by inspecting the completed experiment

From the repository root, using the existing `.venv`:

```bash
PYTHONPATH=src:. .venv/bin/python -m examples.grc9v4.native_spark inspect
PYTHONPATH=src:. .venv/bin/python -m examples.grc9v4.native_spark inspect --family A_CI_PC
```

[native_spark.py](native_spark.py) authenticates the accepted support identity
and the selected input, campaign and checkpoint bytes. It reports exact model,
profile, graph and certificate identities, transfer/history policies, role
endpoints and recorded completion. It does **not** run a trajectory, recalculate
the mathematical certificate or independently recheck every transition.
The family evidence checkers remain available for those separate operations.

The source has **12 vertices**, including the occupied nine-port vertex `v`,
the parent-anchor neighborhood and a private neighbor. Expansion replaces `v`
with a core and three satellites, producing a **15-vertex target**. Both source
roles carry exact total resource **21** and differ in their resource values.
This is a concrete small construction, not a large-graph demonstration.

The accepted C_OS chain is:

| Stage | Public operation / observation | What it establishes |
| --- | --- | --- |
| Source | One positive `step_v4_input(...)` | Fresh source state and qualified parent/candidate capture; gain 0. |
| Expansion | `expand(request)` | D11 collision-free topology, resource transfer and target readmission; gain 0. |
| Proof installation | `install_completion_certificates(current, reset)` | Both role proofs match the target equations and declaration; no elapsed time or gain. |
| Target beat 374 | Positive `step()`, membership true, one window observation | Actual current history has entered the certified domain; gain 0. |
| Target beat 375 | Another positive `step()`, two observations | One elapsed window beat; gain 0. |
| Target beat 376 | Another positive `step()`, three observations | Two elapsed beats and duration 64; completed evidence and local gain 1. |

Target beat numbers exclude the source beat. The live C_OS clock at entry is
therefore step index 375 and time 12000. Window endpoints are observations
separated by **two** positive transitions, not three elapsed transitions.
The script stops on the actual public completion decision; 376 is a retained
expectation, never an admission counter or a forced stopping criterion.

## Understand the configuration before running

```python
from examples.grc9v4.native_spark import bundle
from pygrc.models import GRC9V4

subject, references, campaign, inputs = bundle("C_OS")
model = GRC9V4.from_config(inputs["source_configuration"])
cfg = model.configuration
print(cfg.reference.profile.FAMILY)
print(cfg.reference.profile.site.to_payload())
print(cfg.policy.to_payload())
print(cfg.current.to_payload())
print(cfg.reset.to_payload())
print(model.list_capabilities())
print(model.support_status())
```

The wire configuration is `grc9v4-configuration-v3`. Its explicit site law is

$$
V(C)=\frac{\mu}{4}\big((C-c_0)^2-a^2\big)^2,
\qquad c_0=2,\quad a=1,\quad\mu=1.
$$

The complete declaration also binds the fixed-port graph, family-specific
profile, zero external context, reference geometry, units, numerical policy
and completion policy. The native policies use FLINT exact resource arithmetic
and validated numerical operations; the selected error bounds and rounding
rules remain part of the scientific declaration. Converting the exact rational
strings to binary64 and reconstructing a nominally similar state changes the
experiment. There is no implicit numerical fallback in this example.

`completed_spark` in capability discovery means that the exact declaration is
in the supported roster. `native_endpoint_verified` describes accepted campaign
evidence. `current_occurrence_completed` describes this model's live occurrence.
At construction, capability can be true while current completion is false.
A family label alone is not sufficient to establish reviewed support.

## Execute just the source and expansion first

```bash
PYTHONPATH=src:. .venv/bin/python -m examples.grc9v4.native_spark prepare
```

This performs a new native source beat, explicit expansion and certificate
admission. It does not jump to a saved target or place the model at equilibrium.
The introductory result has both roles outside their certificate domains,
zero window observations, a pending decision and gain 0.

The essential public operations inside `prepare()` are:

```python
from pygrc.models.grc_9_v4_expansion import GRC9V4ExpansionRequestInput
from pygrc.models.grc_9_v4_completion_certificate import CompletionCertificate
from pygrc.models.grc_v4 import GRCV4StepRequestInput
from pygrc.models.grc_v4_state import FrozenJSONMap
from examples.grc9v4.native_spark import committed

action = inputs["event"]["source_receipt"]["identity_payload"]["action"]
committed(model.step_v4_input(GRCV4StepRequestInput(
    "grcv4-step-request-input-v1", action["operation_id"],
    float(action["duration"]), FrozenJSONMap({}))), "source")
request = GRC9V4ExpansionRequestInput.from_payload(
    inputs["event"]["receipt"]["identity_payload"]["action"]["request"])
committed(model.expand(request), "expansion")
pair = tuple(CompletionCertificate.from_payload(p) for p in inputs["certificates"])
committed(model.install_completion_certificates(*pair), "certificates")
```

The recorded durations are 8, 16 or 32, all exactly representable here.
The request binds the **fresh** source-state and graph digests, node, target
template/specialization, chirality, shares and both history-channel policies.
Reusing that request against a changed source is rejected. This example checks
that its newly admitted target equals the retained target configuration exactly.
It has no private-owner access or imports from tests or investigation harnesses.

For C_OS, the three satellite shares are `1/64, 31/32, 1/64`; the core receives
zero at transfer. This zero is a lawful event poststate, followed by admitted
positive evolution. Other families use their own recorded allocation. Shares
are not an arbitrary search knob in this example.

Expansion is explicitly requested by the caller after a valid source beat.
The native mechanism validates that request and applies canonical mechanics.
Port occupancy alone does not establish eligibility: the fresh geometric
conditions and qualified parent matter too. This demonstrates the bounded
mechanical/completion path, not an autonomous event scheduler for every graph.

## What the certificate proves, and what entry means

`CompletionCertificate.from_payload(...)` recomputes the proof and rejects a
changed proof payload. Installation checks ordered **current/reset** roles,
graph, profile, context/reference, charge and policy. Inspect each certificate's
`operands.binding`, `proof.q`, `proof.image_margin` and `proof.full_step_error`.
The sufficient argument combines full-physical-state return/trapping,
contraction, represented error bounds and geometric classification margins.
Two similar numerical reads or a small residual alone are not that argument.

Proof admission can succeed while the current state is outside the certified
domain. Only actual ordinary evolution can earn entry/window observations.
The live observation is:

```python
completion = model.compute_observables()["completion"]
print(completion["membership"])
print(completion["window_observations"])
print(completion["evidence"])
```

Membership includes its certificate identity and a family-specific measure.
Do not compare raw norm numbers across families: resource charts, log-W/carrier
product measures and RG2b curve metrics differ. CI certificates concern the
selected joint root and full implicit return; a bound at fixed geometry does
not replace that claim. RG2b retains its Lipschitz-section scope, not a C1 claim.

The seed/anchor and flow-region rows identify **spatial geometric basins** under
the admitted policy. Their routing domains are diagnostic organization regions,
not extra constitutive transport paths. Multiple spatial basins can belong to
one attracting full state; they are not automatically distinct dynamical
attractors, autonomous subsystems or a hierarchy. A spark candidate, a seed, an
expansion receipt and a completed child are different observations.

## Current and reset: two different histories

Ordinary steps evolve current authority and leave the reset baseline unchanged.
Expansion transfers/readmits each role separately. A subsequent `reset()`
restores the complete reset C/W/Z state and invalidates the live event/window;
it also resets this native branch's step index and clock to zero. It does not
reproduce the source event or earn a new completion.

The accepted reset campaign evolves a separate reset-restored branch to its
own certificate domain and positive comparison window. Its endpoint field
`completion` denotes that window endpoint. **Its gain is 0 and it is not a
second completed spark**, because reset invalidated the event lineage.

| Family | Physical history beyond C | Current entry → completion | Reset entry → comparison end | Duration / minimum elapsed |
| --- | --- | --- | --- | --- |
| C_OS | None; OS predictor/corrector | 374 → 376 | 375 → 377 | 32 / 64 |
| C_CI | None; selected joint root | 374 → 376 | 375 → 377 | 32 / 64 |
| C_PC | Z carrier | 374 → 376 | 375 → 377 | 32 / 64 |
| C_CI_PC | Z carrier plus instantaneous joint root | 374 → 376 | 375 → 377 | 32 / 64 |
| A_OS | W conductance | 375 → 377 | 372 → 374 | 32 / 64 |
| A_CI | W conductance and selected joint root | 375 → 377 | 372 → 374 | 32 / 64 |
| A_PC | W and Z, separate writers | 375 → 377 | 372 → 374 | 32 / 64 |
| A_CI_PC | W and Z, composite joint root | 375 → 377 | 372 → 374 | 32 / 64 |
| C_RG2b | Derived Lipschitz section; no geometry history | 390 → 392 | 390 → 392 | 8 / 16 |
| A_RG2b | W plus derived Lipschitz section | 300 → 302 | 300 → 302 | 16 / 32 |

The fixtures have different declarations and are not a controlled comparison
of convergence rates. A's physical W is distinct from a reference edge map;
persistent Z is distinct from an instantaneous geometry read. The selected
event policies explicitly account for inherited history, new-edge seeding and
any carrier reset/loss. Inspect `expansion.history_policy` in the report instead
of inferring a transport rule from the family name. The complete A/PC proof
must cover W/Z, not only the resource projection.

## Run the complete public example when wanted

```bash
PYTHONPATH=src:. .venv/bin/python -m examples.grc9v4.native_spark run --family C_OS --max-steps 400 --output outputs/examples/native-spark-cos
```

This is an explicit fresh execution, potentially several minutes or longer.
Inspect `recorded_campaign_seconds` before choosing another family. The accepted
campaigns took roughly 14–67 minutes for two roles, independent checks and replay;
those totals are context, not a timing guarantee for this one-role example.
No full campaign runs when opening documentation, the notebook or the browser.

The loop checks every `committed` result and the actual completion decision.
Admission failure stops immediately. Reaching `--max-steps` without completion
raises an error; it does not report success or change the law/tolerance. The
new output directory must not already exist. Reports and the full checkpoint
are compressed as `.json.xz`, including all files larger than 1 MB.

`run.json.xz` contains each target beat's membership/window/decision and emitted
gain, final completion evidence and the duplicate/reset check. The checkpoint
retains the complete physical state, journal, receipts and referenced evidence
objects. It is a new run with its own occurrence identity, not a replacement for
the accepted campaign. No new independent full-transition oracle is implied.

## Gain, lifecycle and replay

Completion gain is local to the expanded parent's footprint. It counts newly
qualified child organization under this policy, not every basin in the graph,
total resource, elapsed steps or the number of expansion receipts. The accepted
current runs emit one increment. The persistent children/consumed-occurrence
ledger and the latest operation's `local_gain` serve different purposes.

The example resolves the cited certificate using
`model.completion_evidence_object(evidence["proof"]["certificate"])`. Such
references address immutable checkpoint objects; their `path` strings do not
instruct you to open files under an imaginary working directory.

`model.duplicate()` preserves the checkpoint and shares occurrence accounting
within the process. Resetting the duplicate restores its baseline and clears
its live event/window without mutating the original scientific branch. Rebase
also invalidates the window; certificate replacement restarts it. Reading,
saving, loading and duplication earn no positive-window time. Failed operations
do not partially advance C/W/Z, window state or the occurrence ledger.

For an explicit **cold** replay, start a separate process:

```bash
PYTHONPATH=src:. .venv/bin/python -m examples.grc9v4.native_spark replay --checkpoint outputs/examples/native-spark-cos/checkpoint.json.xz
```

The reader decompresses the JSON and calls public `GRC9V4.from_state(...)`.
Cold restoration executes and checks the saved journal; it can cost roughly a
trajectory. A warm duplicate is not evidence that this cold path ran. The
accepted campaigns already tested complete cold replay; this publication reuses
those results. The example's run record keeps `cold_replay_executed: false`;
the separate replay command reports exact checkpoint equality without rewriting
that original run record.

Plain `model.save(path)` / `GRC9V4.load(path)` use uncompressed public JSON;
the example's XZ wrapper avoids large uncompressed artifacts. Loading restores
saved completion/accounting, not another emitted gain. Accounting is scoped to
the process/shared owner: independent processes are not a distributed exactly-once
service. A configuration alone restores construction state, not event lineage.

## Find the evidence and continue

The Phase 9 side-tool's **Native spark workflow** panel links this guide and
code, lists all ten endpoints, and explains execution versus inspection. The
notebook cell `native-spark-workflow` shows the same retained overview; it never
starts a run. Existing family panels retain their detailed numerical evidence.

- [Current support and exact identities](../../implementation/investigations/grc9v4-constitutive-design/tools/exploratory-side-tool/docs/NativeSparkSupport.md)
- [Accepted support record](../../implementation/phase-9-grcv4/tranche-9/P9-9.1a.7-Support.json)
- [Foundational C_OS completion definition](../../specs/grc-9-v4-spark-completion.md)
- [Native lifecycle contract](../../specs/grc-9-v4-native-spark-lifecycle.md)
- [Numerical policy and certificate bridge](../../specs/grc-v4-spark-native-numerical-policy.md)
- [Focused integration regressions](../../implementation/phase-9-grcv4/tranche-10/P9-10.3-NativeSpark-Review.md)

The foundational documents retain their original C_OS scope. The support
record links each later family's own contracts and accepted campaign; the
shared API does not extend the C_OS proof to another family's state space.

P9-10.4-NATIVE-SPARK assembles this workflow. Formal debt adjudication remains
P9-10.5; reviewed release support, residual limitations and G4 remain P9-10.6.
