# Public GRC9V4 API

`GRC9V4` provides one lifecycle interface for ten scientific contracts: Candidate
A or C, each with OS, CI, PC, CI+PC or RG2b. Configuration and family discovery
cover all ten. The current native execution scope is **C_OS, C_CI, A_CI, A_PC**.
Declaring another family is valid; attempting to execute it raises
`GRC9V4ExecutionUnavailable` before numerical admission. This distinction is
visible in the API and does not depend on decoding a failure message.

## Structure

The interface follows three existing boundaries:

- `GRC9V4Configuration` describes a port-owned reference, specialization,
  independent current/reset authority, clock/budget, and explicit execution
  options. Its profile retains the existing typed candidate and realization
  parameters. Callers do not assemble an internal solver stage or state digests.
- `GRC9V4` supplies common construction, stepping, expansion, migration,
  observation, reset/rebase and replay methods. `grc_9_v4_api_lifecycle.py` owns
  transaction composition and delegates scientific work to the native owners.
  Expansion is prepared as a typed transition; the receiving owner publishes
  the complete state/artifact result atomically.
- `GRC9V4State.lifecycle` is an immutable readable view of the current branch.
  `checkpoint` separately retains the complete replay history. Neither a current
  observation nor a fresh configuration substitutes for that history.

The nine-port chart, fixed-row A descriptor, canonical expansion and exact
legacy branch are shared specialization mechanics. Candidate history and each
realization's numerical method remain in their existing scientific components.
The public class does not turn them into a single generic solver.

## Candidate and realization types

Candidate A parameters use `CandidateAParams` and own edge history `W_A`.
Candidate C parameters use `CandidateCParams`; `W_A` must be absent. Both own
vertex resources `C`. Persistence is independently determined by realization.
All parameter types below are the existing classes from
`pygrc.models.grc_v4_profile`.

| Realization | Parameter type | Derived read/solve | Additional authority |
| --- | --- | --- | --- |
| OS | `OSParams` | Reference predictor, generated-geometry corrector | None |
| CI | `CISolverParams` | Joint current/geometry root | None |
| PC | `PCParams` | Read committed carrier before its writer | `Z_4` |
| CI+PC | `CIPCParams` | Joint root with fixed old carrier and instantaneous geometry | `Z_4` |
| RG2b | `RG2bParams` | Certified realization section at the declared duration | None |

CI roots and RG sections are derived numerical objects, not extra mutable
state slots. `GRCV4AuthoritativeState` retains its existing optional history
fields, but the configuration validates their presence and dimensions against
both axes. For example, C_PC requires `C` and `Z_4`; A_CI requires `C` and `W_A`.
The same checks apply independently to current and reset.

## Construct and inspect

From the repository root, a pinned small declaration can be selected with the
[catalog](catalog.py), then decoded without executing any solver:

```python
from examples.grcv4.catalog import Catalog
from examples.grcv4.run_selection import configuration_from_selection
from pygrc.models import GRC9V4
from pygrc.models.grc_9_v4 import GRC9V4ExecutionUnavailable

catalog = Catalog()
saved = catalog.selection("native-small-C_CI", side="source")
config = configuration_from_selection(
    saved, exact_backend="flint", numerical_policy="legacy_exact_v1"
)
print(config.family.profile_family_id)
print(config.profile.params_resolved.realization)  # CISolverParams
print(config.current.C, config.reset.C)

model = GRC9V4.from_config(config)  # Actual admission occurs here.
state = model.state.lifecycle
print(state.port_graph, state.current, state.reset.authoritative)
print(model.execution_scope())
print([f.profile_family_id for f in model.describe_families()])  # All ten
```

For application-owned data, construct `GRC9V4Configuration` directly with
`reference`, `specialization`, `current`, `reset`, `budget_target`, and
`GRC9V4ExecutionOptions(exact_backend, numerical_policy)`. Optional `step_index`
and `time` default to zero. Optional `targets` contains complete same-graph
reference declarations. The reference's `profile.params_resolved` holds all
scientific parameters; no second public parameter schema is introduced.
`to_payload()`/`from_payload()` round-trip a closed JSON-compatible declaration.
Invalid fields, parameter types, history shapes and execution policies reject.
Structural validation does not assert numerical admission.

Changing the example to `native-small-A_RG2b` still decodes a typed RG2b
configuration. `GRC9V4.from_config(config)` then raises
`GRC9V4ExecutionUnavailable`; the exception exposes `.family` and
`.available_families`. There is no automatic substitution or fallback.

`describe_families()` lists contracts. `list_declared_profiles()` lists exact
registered declarations for the current graph, including known unavailable
families. `list_supported_profiles()` filters those declarations to the current
execution scope; actual state/target admission still applies.
`support_status()` reports both populations and the bounded conformance status.
After expansion, source-graph declarations are not advertised as current targets.

## Execute, observe and restore

The facade accepts the existing typed requests. Ordinary steps use
`GRCV4StepRequestInput` through `step_v4_input()` or `run_v4()`. Convenience
`step()`/`run(n)` require an identity-bearing default request in the profile;
they do not invent a duration. Canonical expansion uses
`GRC9V4ExpansionRequestInput`; profile migration uses `GRCV4MigrationRequest`;
branch crossing uses `GRC9V4BranchRequest`.

Enabled state exposes `current`, the independent `reset` baseline, graph,
profile, specialization, clock, budget, identities and receipt ledger.
`EnabledGRC9V4State` and `DisabledGRC9V3State` are distinct types. The disabled
view exposes the exact legacy checkpoint and a detached `delegate_snapshot`
copy; it does not fabricate V4 history fields. Its observable projection and
ordinary step remain native. A supplied V4 request on that branch rejects.

`model.configuration` returns inputs for a fresh enabled construction at the
current scientific state. Use `snapshot()`/`from_state()`, `save()`/`load()` or
`duplicate()` when lineage and replay must be preserved. `get_state()` and
`set_state()` use the complete immutable state and reject altered metadata.
Reset/rebase preserve the established branch-specific clock/baseline semantics.

Migration remains a scientific admission operation. The retained A_PC source
cannot enter the retained A_CI domain, while A_CI→A_PC→A_CI has a passing
companion. Direct C→A profile migration requires a native fixed-row initializer;
the generic initializer cannot replace it. Explicit native initialization is
available through the accepted branch-entry/return route. Branch crossing is
same-graph; legacy topology growth is not an inferred return map.

## Evidence scope

The [P9-9.4b review](../../implementation/phase-9-grcv4/tranche-9/P9-9.4b-Review.md)
links six all-ten contract checks, twenty native integration/boundary checks
and nine architecture/compatibility/replay checks.
The six additional families have public declarations and typed data validation,
without new native execution evidence. Full conformance, optional completion
and hierarchy remain separate review items. The retained-check command does not
rerun trajectories. Existing CI resolution limits and pointwise A_PC carrier
margins continue to apply.

The [ownership/dispatch decision](../../implementation/phase-9-grcv4/tranche-9/P9-9.4b-Architecture.md)
records independent public execution selection, immutable prepared actions and
sole branch receipt/journal/artifact ownership. A possible consolidation of
standalone and branch checkpoint formats is reserved for after all ten families
are enabled. That future option does not change current usage.
