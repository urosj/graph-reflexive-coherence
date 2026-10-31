# GRC9V4: from one step to a complete lifecycle

GRC9V4 combines the graph-generic V4 constitutive laws with an intrinsic nine-port
chart, fixed-row differentials, column coarse-graining, hybrid spark detection
and a collision-free mechanical expansion. One public class exposes **all ten
candidate/realization families**. Their state, reads, solvers and history writers
remain different. This guide shows those differences through executable public
operations, rather than treating a family name as a cosmetic switch.

These are small, exact configurations extracted from accepted native runs.
They demonstrate bounded behavior; they are not universal admission certificates
for arbitrary graphs, parameters or trajectories. The all-ten Tranches 8–9 and
P9-10.1–10.3 decisions are accepted. P9-10.4 supplies bounded example execution;
its user acceptance is recorded separately. Full conformance and G4 remain separate.

## Run the first example

From the repository root, with the repository's `.venv` and its dependencies:

```bash
PYTHONPATH=src:. .venv/bin/python -m examples.grc9v4.quickstart
```

[quickstart.py](quickstart.py) is the complete minimal example. The essential call is:

```python
from pygrc.models import GRC9V4
from pygrc.models.grc_v4 import GRCV4StepRequestInput
from pygrc.models.grc_v4_state import FrozenJSONMap
from examples.grc9v4.fixtures import configuration

model = GRC9V4.from_config(configuration("C_OS"))
result = model.step_v4_input(GRCV4StepRequestInput(
    "grcv4-step-request-input-v1", "my-step", 2**-12, FrozenJSONMap({})))
if not result.committed:
    raise RuntimeError(result.failure)
print(model.configuration.current.C)
print(result.observables["authoritative_current"])
```

The source graph has ten vertices and nine edges: one node occupies all nine
ports, with a different neighbor at each port. The fixture starts at the saved
poststate of a positive source beat, with distinct current/reset histories.
`configuration()` loads a complete typed declaration; it does not load the old
run's receipts or grant its acceptance to a new run. `from_config()` performs
native admission. The example then commits a new positive step.

The output contains the updated resources and the current **consumed by that
step**. A subsequent `compute_observables()` performs a fresh read of the new
state. In C_OS the two current vectors differ: the first came from the completed
predictor/corrector computation, while the second is a new reference read. Both
are meaningful; neither should be relabeled as the other.

## A progressive set of lessons

Run a lesson independently, or `all` for the seven family-specific lessons.
`migration` is a separate cross-family lesson. Nothing starts a large campaign.
The default evolution length is three positive steps; `--steps` changes only
that lesson. Every invocation constructs fresh owners.

```bash
PYTHONPATH=src:. .venv/bin/python -m examples.grc9v4.tour discovery
PYTHONPATH=src:. .venv/bin/python -m examples.grc9v4.tour evolution --family A_CI_PC --steps 3
PYTHONPATH=src:. .venv/bin/python -m examples.grc9v4.tour sparks --family C_OS
PYTHONPATH=src:. .venv/bin/python -m examples.grc9v4.seeds
PYTHONPATH=src:. .venv/bin/python -m examples.grc9v4.tour basin --family C_CI
PYTHONPATH=src:. .venv/bin/python -m examples.grc9v4.tour expansion --family A_PC
PYTHONPATH=src:. .venv/bin/python -m examples.grc9v4.tour checkpoint --family A_RG2b
PYTHONPATH=src:. .venv/bin/python -m examples.grc9v4.tour migration
PYTHONPATH=src:. .venv/bin/python -m examples.grc9v4.tour compatibility --family A_CI
PYTHONPATH=src:. .venv/bin/python -m examples.grc9v4.tour rejection --family C_PC
```

For a human-readable JSON file instead of stdout:

```bash
PYTHONPATH=src:. .venv/bin/python -m examples.grc9v4.tour all --family C_OS --output /tmp/grc9v4-cos-new-run.json
```

The runner refuses to replace an existing output. Outputs larger than 1 MB are
compressed to `.json.xz` automatically; a new run never replaces retained
acceptance evidence. The machine-readable results contain full per-step C/W/Z,
reset authority, transaction results, fresh observations and identities—not
only a pass/fail line. [Retained results](results/) allow inspection without a
rerun. [tour.py](tour.py) is ordinary Python calling the public model; it has no
test-fixture imports or access to private transaction owners.

## Understand the two independent axes

| Axis | Choice | Authoritative state and consequences |
| --- | --- | --- |
| Candidate | A | Retains one positive `W_A` per live edge. The native fixed-row differential backend is part of the declaration. History is transported or explicitly lost at lifecycle boundaries. |
| Candidate | C | No `W_A`. Reconstructs the derived sector and baseline transport from the complete stable-edge reference map `W_C_tr`. That map is a profile/reference operand, not an extra evolving resource. |
| Realization | OS | Reference predictor, generated-geometry corrector; no persistent carrier. |
| Realization | CI | Selects a joint current/geometry root; admission binds the solver, contraction domain, certificate and full selected point. |
| Realization | PC | Reads the old committed carrier, advances resources/history, then writes the next carrier. The new carrier is not consumed retroactively. |
| Realization | CI+PC | Joint root with the old carrier held fixed plus instantaneous feedback. Both mechanisms matter; the carrier writer uses the selected root. |
| Realization | RG2b | Evaluates the declared certified section for the requested duration. The section is derived, not another retained history slot. |

With `N` vertices and `E` edges, `C` has length `N`, A's `W_A` has length `E`,
and persistent `Z_4` is a flattened **E × E tensor**, length `E**2`, in the bound
edge order. `Z_4=None` means the realization has no carrier; a zero tensor means
it has a carrier whose current value is zero. These are different contracts.
`A_CI_PC` and `C_CI_PC` are family IDs; their realization label is `CI+PC`.

`discovery` lists all ten contracts, authoritative fields, solver/read/write
semantics and the actual typed parameter field names. A common facade does not
require invented W slots in C or carrier slots in CI/OS/RG2b.

```python
from examples.grc9v4.fixtures import configuration

cfg = configuration("A_CI_PC")
print(type(cfg.profile.params_resolved.candidate).__name__)
print(type(cfg.profile.params_resolved.realization).__name__)
print(cfg.family.authoritative_fields)
print(cfg.profile.params_resolved.to_payload())
```

Relevant controls include Candidate A's history/read-back parameters,
Candidate C's mobility/potential/reference map and selector cutoff, geometry
gain, CI's domain/root selector/tolerance/iteration limits, PC's `tau_PC`,
carrier radius/norm/writer/envelope, CI+PC's instantaneous coupling, and RG2b's
completion/containment/section settings. They are serialized scientific
contracts. Changing one generally changes the complete profile identity and
requires appropriate readmission; it is not a runtime `setattr` tuning knob.
The fixture loader does not silently repair inconsistent solver declarations.

These ten fixtures share a small topology class, **not identical parameters or
initial histories**. Comparing their printed numbers is not a controlled
candidate/realization ablation. For controlled generic V4 evolution comparisons,
see [the earlier comparison examples](../grcv4/README.md); those do not establish
native nine-port conformance.

## Read a step and its continuation correctly

`evolution` records, for every step:

1. The full current and reset C/W/Z, clock and identities before the operation.
2. The typed transaction result: commitment, solver disposition, the consumed
   authoritative current, receipts and postbeat nine-port observables.
3. The committed state and an additional **nonmutating fresh poststate read**.

Look at `authoritative_current.stage` and `consumed_by_continuity`, rather than
assuming every displayed current was integrated. Look at `solver_disposition`
for the selected realization. Inspect W and Z separately from C: positive
stored history alone does not demonstrate a numerically resolved mechanism
effect. The stronger effect-separation evidence lives in the accepted numerical
campaigns, not in an arbitrary rounded terminal printout.

The printed rational `represented_charge` is the exact sum of the saved
binary64 values. It is not a claim that every real-number trajectory is enclosed.
Do not clip a negative resource or change a tolerance to force a step through.
`committed=False` is an admission result that must be handled explicitly.

`step_v4_input()` accepts shape-valid external input and can return a structured
semantic rejection. `step_v4()` takes a strict `GRCV4StepRequest`; `run_v4()`
applies an ordered iterable of those requests and is **not one atomic batch**.
Earlier commits remain if a later request fails. `step()`/`run(n)` on an enabled
model require an immutable serialized default request; these fixtures have no
implicit default. On the disabled branch, `step()` is the native V3 operation.

The numerical observations have explicit roles:

| Fields | Interpretation |
| --- | --- |
| `charge`, `charge_target`, `charge_current`, `budget_error` | The single resource ledger and its admission residual; no second hidden mass ledger. |
| `authoritative_current`, `continuity_evaluations` | Which current was integrated and how many continuity evaluations occurred. |
| `row_gradient`, `signed_row_hessian`, `row_net_flux` | Fresh fixed-row nine-port diagnostics with the declared sign convention. |
| `active_port_degree`, `port_occupancy` | Mechanical endpoint occupation; not a semantic saturation verdict on its own. |
| `coarse_columns`, `coarse_profiles` | Exact rational column totals and normalized profiles of native row weights; not generic graph coarsening. |
| `hybrid_spark_candidates`, `candidate_stage` | Positive-postbeat candidate observations, or explicitly unavailable outside that boundary. |
| `mechanical_expansions`, `receipt_ledger` | Committed mechanical events and persistent history; distinct from one operation's emitted receipt delta. |
| `abundance`, `abundance_status`, `abundance_observation` | These fixtures report `unavailable_no_admitted_definition` with null values. A resource sum, basin count or expansion count is not substituted for abundance. |
| `basin_attributes`, `basin_identity` | Present only with the explicit v2 basin-policy successor discussed below. |

## Seeds, hybrid sparks and mechanical expansion

Three different uses of “seed” must stay separate:

| Term | Meaning |
| --- | --- |
| Initial configuration | The graph and initial current/reset authority from which this owner is constructed. |
| Basin seed | A node satisfying the declared small-gradient and positive signed-Hessian test. It is an observation, not a new node. |
| Positive bond seed | The explicit positive reference/history value assigned to newly created internal edges by the expansion contract. It is not an extra resource source. |

The baseline predicates are:

$$
\text{basin seed}:\quad \|g_i\|<\varepsilon_\nabla,
\quad\lambda_{\min}(\widetilde H_i)>\varepsilon_H>0,
$$

$$
\text{hybrid spark candidate}:\quad \deg_{\rm act}(i)=9,
\quad\|g_i\|<\varepsilon_\nabla,
\quad\lambda_{\min}(\widetilde H_i)<\varepsilon_{\rm spark}.
$$

Thus nine occupied ports alone do not authorize expansion. A basin seed does
not require saturation. Equality at the strict thresholds does not pass that
predicate. The signed Hessian uses the selected fixed-row backend and sign
convention, not a generic graph-Laplacian eigenvalue substituted for it.

The `sparks` lesson computes detached diagnostics from a **fresh** native read,
prints every node's occupied ports, gradient, minimum signed Hessian, seed flag
and candidate flag, then checks them against the candidates emitted by a new
positive ordinary beat. It verifies that observation and ordinary evolution
do not automatically expand the graph. These particular fixtures need not
contain a positive basin seed; a false seed flag is useful information, not a
failure to be patched by adjusting a threshold.

[seeds.py](seeds.py) supplies a **separate, explicitly declared** positive-seed
example. It transfers 9/256 resource to the center and subtracts 1/256 from each
leaf, preserving the exact represented total, and selects a basin-Hessian
threshold of 0.01 in a newly identified specialization. The center's gradient
is approximately (-0.02306, -0.02306, -0.02306), with positive minimum signed
Hessian approximately 0.02306. It is a geometric seed and is not spark-eligible.
The example then installs the basin policy and prints the complete observation.
It changes neither the accepted expansion fixtures nor a live owner's frozen
policy. This illustrates a valid parameter choice and identity construction;
it proves no attracting basin or child completion.

The `expansion` lesson uses the saved eligible source and a separate explicit
request. Its declared zero-duration prefix reproduces the accepted journal's
admission boundary; it does **not** manufacture another positive source beat.
The public step result deliberately does not publish a new positive-postbeat
candidate list for that prefix. The lesson inspects detached fresh diagnostics;
the native event owner independently checks chronology, trigger and source.

The request binds source state/graph/node, target profile template and
specialization, target effective degree, chirality, growth phase, resource
shares and both history-policy channels. The examples use D52: a ten-node,
nine-edge source becomes seventeen nodes and sixteen edges. **D52 is effective
module capacity, not 52 ports on one vertex.** Every individual vertex still has
at most nine distinct occupied ports.

For A, old-edge W follows exact lineage and new internal edges receive the
declared positive bond seed. For C, the target's complete edge reference map
and derived state are reconstructed. Persistent carriers undergo the selected
whole-carrier reset with an explicit loss record; this example does not claim
lossless carrier interpolation. Current and reset resource/history roles are
transported and re-admitted independently before atomic publication.

Inspect the event receipt, full before/after authority, actual port occupancy,
column totals/profiles, and the positive target-continuation step. A stale
request is rejected without changing the full checkpoint. Reset remains on the
**expanded** graph: it restores the transported reset baseline, not the old graph.

An admitted event can be followed by a rejected continuation. Its event receipt
then remains valid; it does not prove trajectory success. The lesson checks
event commitment and continuation separately.

**A completed spark is not implemented by implication.** It additionally needs
the selected post-expansion stable child-basin/attractor gain and hierarchy
contract. `completed_spark` and `hierarchy_tracking` are not advertised here.
The optional column-H-assisted lane and general autonomous partition/ATC
scheduling are also not established by this baseline example. See the
[specialization contract](../../specs/grc-9-v4-spec.md#saturation-and-hybrid-spark-semantics).

## Basins: versioned observations with provenance

`basin` explicitly migrates from specialization v1 to the v2 basin policy,
preserving C/W/Z in both roles while changing the combined model identity.
It prints `basin_attributes`, `basin_identity`, the migration receipt and the
two replay modes. Merely renaming a v1 snapshot or adding a cached label cannot
perform this migration.

The represented-flow classifier builds directed adjacency from the sign of
the fresh selected current, finds strongly connected components and terminal
structure, and combines this with the declared seed diagnostics. Zero-current
edges do not acquire an invented direction. Multiple reachable terminal
organizations remain distinguishable; there is no strongest-edge shortcut.
Inspect the witness's graph, typed node IDs, hex-encoded current/row operands,
role, profile/context/read binding and classification—not just a basin label.

`basin_identity` identifies the classification on its bound graph. It is not
the complete profile ID, model ID, scientific state digest, lifecycle digest,
or a persistent child-hierarchy identity. Node relabeling, graph changes and
policy changes must respect those separate identities.

The observations are **represented-flow diagnostics**. They do not feed a
resource/history writer, alter spark thresholds or guarantee dynamical
attractors. A fixed-geometry current bound does not prove the sign of an exact
implicit CI root. Connected RG2b's unresolved C1 regularity is not closed by
successfully producing a basin classification. See
[basin interface specification](../../specs/grc-9-v4-basin-interface.md).

## Lifecycle: reset, replay and identities

| Operation / object | What it preserves or changes |
| --- | --- |
| `configuration` | Current typed scientific construction inputs; reconstructing from it starts a new lineage. |
| `state` / `get_state()` | Immutable readable lifecycle view plus a complete checkpoint. Enabled and disabled views have different types. |
| `snapshot()` / `from_state()` | Complete publication, history/receipts, registered targets and execution choices; reconstructs lineage. |
| `duplicate()` | Independent owner with the same checkpoint; later mutation does not affect the original. |
| `reset()` | Restores the current reset C/W/Z on the current graph/profile; preserves clock and records the operation. |
| `rebase_reset_baseline()` | Explicitly replaces the reset baseline with the current authority. |
| `save(path)` / `load(path)` | JSON checkpoint persistence; native `save` replaces the named file, so choose a new output path. |
| `set_state(state)` | Restores a complete compatible immutable public state; not an arbitrary partial C/W/Z update. |

`checkpoint` restores a checkpoint, runs the same next request on both owners
and compares results and complete checkpoints. It also exercises duplication,
reset after evolution and rebase/reset. It checks the full authority, not just
resource equality. The `basin` lesson separately exercises `exact_observation`
and `state_only` replay; state-only restoration retains scientific authority
without claiming that a saved observation was authenticated as an exact replay.

To persist your own model, use an explicit new path:

```python
from pathlib import Path
from pygrc.models import GRC9V4
from examples.grc9v4.fixtures import configuration

model = GRC9V4.from_config(configuration("A_PC"))
path = Path("/tmp/my-grc9v4-checkpoint.json")
if path.exists():
    raise FileExistsError(path)
model.save(path)
restored = GRC9V4.load(path)
assert restored.snapshot() == model.snapshot()
```

Profile IDs bind constitutive declarations; specialization IDs bind nine-port
policies; the combined model identity includes both and the branch. Scientific
state binds authority and its scientific preimages. Lifecycle identity also
tracks the operation history. Receipt deltas emitted by one operation are not
the entire persistent ledger. A reset need not restore an old lifecycle digest
even when its C/W/Z equal a prior baseline.

## Profile migration and explicit V3 compatibility

`migration` registers exact same-graph target references up front. It exercises
C_OS → C_CI and A_CI → A_PC → A_CI, and retains the expected rejection of the
independently supplied A_PC source outside the A_CI domain. Both C and the
history channels must pass target readmission. Family dispatch availability
does not mean every state can migrate into every domain.

The two channels are independent: A→C loses candidate history; C→A needs the
native initializer; nonpersistent→persistent initializes a carrier without
losing a nonexistent source carrier; persistent→nonpersistent loses carrier
history. Persistent→persistent preservation additionally requires the exact
carrier contract. The policy helper computes a declaration from public
scientific inputs; the owner recomputes and checks it against both roles.

`compatibility` demonstrates an explicit enabled→disabled→enabled crossing.
It declares incoming legacy edge weights/flux for both histories, executes
native GRC9V3 evolution, restores a disabled checkpoint, rejects a V4 request
on the disabled branch, then returns through the native initialization stage
and performs positive V4 continuation. Direct C→A migration cannot silently
use the graph-generic initializer instead of the fixed-row native stage.

This is a **declared branch transition**, not an automatic fallback when V4
fails. The disabled state exposes a native legacy snapshot, not invented V4
history slots. The legacy saturated expansion with the inherited port-5
collision is rejected by the V4 compatibility adapter as
`legacy_expansion_target_undefined`; it is not repaired by invoking V4's native
expansion. Standalone GRC9V3 remains unchanged.

## Construct and inspect your own declarations

The full scientific inputs are visible in [fixtures.json](fixtures.json).
They are ordinary `GRC9V4Configuration.to_payload()` output, with provenance
and requests stored alongside. Load a configuration you saved yourself with:

```python
import json
from pathlib import Path
from pygrc.models import GRC9V4
from pygrc.models.grc_9_v4 import GRC9V4Configuration
from examples.grc9v4.fixtures import configuration

payload = configuration("C_PC").to_payload()
decoded = json.loads(json.dumps(payload))
model = GRC9V4.from_config(GRC9V4Configuration.from_payload(decoded))
print(model.configuration.reference.graph.port_graph)
print(model.list_declared_profiles())
print(model.list_supported_profiles())
print(model.list_capabilities())
```

A port graph binds stable node/edge order and one occupied endpoint `(node,
port)` per incident edge. Ports 1–9 form a 3×3 intrinsic row/column chart.
Orientation reversal transforms signed fields; relabeling, row/column
permutation, cyclic rotation and full-chart reflection have different
covariance obligations. Editing only endpoint labels or only current signs is
not a valid representation transport. The public facade intentionally rejects
generic graph transport and generic topology replay; use native declared event
contracts and complete checkpoints. Native covariance evidence is in the
accepted Tranche 8 records.

For a new graph, build a complete consistent reference (including C's entire
edge map or A's fixed-row backend), both current/reset authorities, the full
profile and specialization identities, budget, context and execution choices.
`from_payload` is closed-schema validation, while `from_config` performs native
admission. Neither automatically supplies missing mathematical domain evidence.
See [typed contracts](../../src/pygrc/models/grc_9_v4_contracts.py), the
[generic spec](../../specs/grc-v4-spec.md) and the
[nine-port spec](../../specs/grc-9-v4-spec.md).

## Performance, failure and evidence boundaries

These examples explicitly select FLINT exact scalars with `legacy_exact_v1`
for the small graphs. There is no silent switch to approximate arithmetic or
an unbounded inverse fallback. Larger accepted cases use the separately named
`certified_arb_256_weighted_v1` policy where its assumptions/certificates apply.
Backend choice and numerical policy are distinct; FLINT alone does not select
all certified shortcuts. The optimized solves certify the specified represented
result or fail explicitly. They do not confer a uniform trajectory theorem.

Independent families can run as separate processes, up to the available CPU
budget. Avoid concurrent mutations of one owner or changing shared numerical
contexts mid-operation. `rejection` distinguishes malformed inputs that raise
before admission from semantic failures that return a noncommitting result;
it checks full checkpoint rollback. Do not retry by silently weakening a law,
clipping a resource, shrinking a threshold or swapping solver policies.

To execute the whole published lesson set in ten independent workers, writing
new evidence in a new directory:

```bash
PYTHONPATH=src:.:implementation/phase-9-grcv4/verification .venv/bin/python implementation/phase-9-grcv4/verification/p9104_examples.py --run --workers 10 --output /tmp/grc9v4-new-examples
```

To inspect retained evidence without running any trajectory:

```bash
PYTHONPATH=src:.:implementation/phase-9-grcv4/verification .venv/bin/python implementation/phase-9-grcv4/verification/p9104_examples.py --check
```

The retained family jobs took approximately 20–172 seconds each on the recording
machine (C_OS's initial standalone run took 27 seconds). Timings are not a
portable runtime promise. Complete family reports are compressed losslessly;
for example, `xz -dc examples/grc9v4/results/C_OS.json.xz` prints the original JSON.

The capability list describes implemented surfaces, while complete profile IDs
describe this instance's registered declarations. Some low-level display strings
still contain the historical `pending_P9_9_6` wording; those strings are not the
current acceptance ledger. Current bounded acceptance comes from the
[P9-10.3 decision](../../implementation/phase-9-grcv4/tranche-10/P9-10.3-Acceptance.json).
The tutorial's own retained results establish new example execution, not new
scientific authority, release semantics, completed-spark support or G4.

Each fixture is linked to its frozen catalog entry and the exact accepted
source artifact from which it was extracted. RG2b uses the connected completion
successors; the older catalog's nominal RG2b declarations are not silently
substituted for them. The [verification record](../../implementation/phase-9-grcv4/tranche-10/P9-10.4-Examples.json)
binds the new example inputs, code and outputs. Its integrity check does not
rerun numerical trajectories. A fresh invocation creates new execution evidence.
