"""Progressive public GRC9V4 examples. See README.md for contracts and interpretation.

Run one named lesson, or 'all' for one family. Independent family processes may
run in parallel. No implicit policy fallback, automatic event, or parameter fit.
"""
import argparse
from dataclasses import fields, replace
from fractions import Fraction
import hashlib
import json
import lzma
from pathlib import Path
import time

from pygrc.models import GRC9V4
from pygrc.models.grc_9_v4 import GRC9V4BranchRequest, GRC9V4ExpansionRequestInput
from pygrc.models.grc_v4 import GRCV4StepRequestInput, GRCV4MigrationRequest
from pygrc.models.grc_v4_geometry import GeometryStageInputs
from pygrc.models.grc_v4_migration import migration_history_policy
from pygrc.models.grc_v4_state import FrozenJSONMap
from pygrc.models.grc_9_v4_lifecycle import GRC9SparkPolicy, GRC9V4CandidateDetection
from pygrc.models.grc_9_v4_topology import GRC9V4PostbeatRows
from pygrc.models.grc_v4_exact import exact_backend
from examples.grc9v4.fixtures import configuration, fixture, FAMILIES


def encoded(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()


def digest(value):
    return hashlib.sha256(encoded(value)).hexdigest()


def require(value, message):
    if not value:
        raise AssertionError(message)


def request(name, dt=2**-12):
    return GRCV4StepRequestInput("grcv4-step-request-input-v1", name, dt, FrozenJSONMap({}))


def committed(result):
    require(result.committed, "operation rejected: " + str(result.failure))
    return result.to_payload()


def authority(state):
    return {key: getattr(state, key) for key in ("C", "W_A", "Z_4")}


def state_summary(model):
    c = model.configuration
    return dict(family=c.family.profile_family_id, C=c.current.C, W_A=c.current.W_A,
        Z_4=c.current.Z_4, reset=authority(c.reset), step_index=c.step_index, time=c.time,
        represented_charge=str(sum(map(Fraction, c.current.C))),
        budget_target=c.budget_target, complete_profile_id=model.active_profile_id,
        model_identity=model.active_model_identity, lifecycle_digest=model.lifecycle_digest,
        ledger_length=len(model.receipt_ledger),
        vertices=list(c.reference.graph.live_node_ids), edges=list(c.reference.graph.live_edge_ids))


def discovery():
    """Static family contracts are not claims of admission of arbitrary data."""
    return dict(execution_families=list(GRC9V4.execution_scope()), families=[dict(
        family=f.profile_family_id, candidate=f.candidate, realization=f.realization,
        authoritative_fields=f.authoritative_fields, solve_kind=f.solve_kind,
        geometry_read=f.geometry_read, history_write=f.history_write,
        candidate_parameters=[p.name for p in fields(f.candidate_parameters)],
        realization_parameters=[p.name for p in fields(f.realization_parameters)],
    ) for f in GRC9V4.describe_families()],
        limits=["Declaration and execution dispatch do not guarantee input admission.",
                "Bounded all-ten Tranches 8–10 evidence is not full conformance or G4.",
                "General autonomous topology selection, completed spark and hierarchy are not enabled."])


def evolution(family, steps=3):
    model = GRC9V4.from_config(configuration(family))
    rows = []
    for i in range(steps):
        before = state_summary(model)
        result = model.step_v4_input(request(f"evolution-{i}"))
        payload = committed(result)
        # This fresh query is intentionally distinct from the read consumed by
        # the completed step. It must not write history or append a receipt.
        boundary = model.lifecycle_digest
        fresh = model.compute_observables()
        require(model.lifecycle_digest == boundary, "read-only query changed lifecycle")
        rows.append(dict(before=before, transaction=payload, after=state_summary(model),
                         fresh_poststate_observables=fresh))
    return dict(steps=rows, final=state_summary(model),
                support=model.support_status(), capabilities=sorted(model.list_capabilities()))


def checkpoint(family):
    model = GRC9V4.from_config(configuration(family))
    committed(model.step_v4_input(request("before-checkpoint")))
    saved = model.snapshot()
    restored = GRC9V4.from_state(saved)
    require(restored.snapshot() == saved, "checkpoint did not restore exactly")
    clone = model.duplicate()
    a = committed(model.step_v4_input(request("same-next-step")))
    b = committed(restored.step_v4_input(request("same-next-step")))
    require(a == b and model.snapshot() == restored.snapshot(), "continuation replay differs")
    require(clone.snapshot() == saved, "duplicate shared mutable publication")
    baseline = model.configuration.reset
    clock = (model.configuration.step_index, model.configuration.time)
    model.reset()
    require(model.configuration.current == baseline, "reset did not restore C/W/Z")
    require((model.configuration.step_index, model.configuration.time) == clock, "reset rewound clock")
    committed(model.step_v4_input(request("after-reset")))
    new_baseline = model.configuration.current
    model.rebase_reset_baseline()
    model.reset()
    require(model.configuration.current == new_baseline, "rebase/reset mismatch")
    return dict(checkpoint_digest=digest(saved), continuation_equal=True,
        duplicate_independent=True, reset_restored_all_authority=True,
        reset_preserved_clock=True, rebase_restored_new_baseline=True,
        final=state_summary(model))


def signals(model):
    """Detached seed/candidate diagnostics; this does not authorize an event."""
    c = model.configuration
    fresh = model.compute_observables()
    with exact_backend(c.execution.exact_backend):
        rows = GRC9V4PostbeatRows(c.reference.graph.port_graph, c.profile, c.current,
            tuple(fresh["authoritative_current"]["values"]), c.step_index,
            c.specialization.identity_payload["hessian_sign"])
        policy = GRC9SparkPolicy.from_payload(c.specialization.resolved["spark"])
        detection = GRC9V4CandidateDetection(rows, policy)
        result = [dict(node_id=r.node_id, occupied_ports=r.occupied_ports,
            gradient=r.row.gradient, minimum_signed_hessian=r.minimum_signed_hessian,
            saturated=r.saturated, small_gradient=r.small_gradient,
            hessian_degenerate=r.hessian_degenerate, basin_seed=r.basin_seed,
            hybrid_spark_candidate=r.is_candidate) for r in detection.assess()]
    return dict(policy=policy.to_payload(), assessments=result,
        candidate_node_ids=list(detection.candidate_node_ids()),
        causal_boundary="fresh detached diagnostic; native expansion rechecks source and chronology",
        completed_spark=False, hierarchy_update=False)


def sparks(family):
    model = GRC9V4.from_config(configuration(family))
    before = model.snapshot()
    initial = signals(model)
    require(model.snapshot() == before, "seed/candidate query mutated state")
    step = committed(model.step_v4_input(request("fresh-spark-observation")))
    after = signals(model)
    require(after["candidate_node_ids"] == step["observables"]["hybrid_spark_candidates"],
            "detached diagnostics differ from native postbeat candidates")
    require(len(model.configuration.current.C) == 10, "observation automatically expanded topology")
    return dict(initial=initial, after_positive_step=after,
                native_postbeat_candidates=step["observables"]["hybrid_spark_candidates"],
                topology_unchanged=True, completed_spark=False)


def expansion(family):
    row = fixture(family)
    model = GRC9V4.from_config(configuration(family))
    before = state_summary(model)
    # The fixture is already the saved poststate of a positive source beat.
    # A declared zero-duration beat publishes fresh postbeat detection for this
    # new owner, as in its accepted native journal; it adds no source time.
    prefix = committed(model.step_v4_input(GRCV4StepRequestInput.from_payload(row["prefix_step"])))
    diagnostics = signals(model)
    require(row["expansion"]["source_node_id"] in diagnostics["candidate_node_ids"],
            "saved source is not trigger eligible")
    result = committed(model.expand(GRC9V4ExpansionRequestInput.from_payload(row["expansion"])))
    after_event = state_summary(model)
    require(len(after_event["vertices"]) == 17 and len(after_event["edges"]) == 16,
            "D52 fixture topology differs")
    event_snapshot = model.snapshot()
    # Stale input cannot silently expand an already changed topology.
    rejected = model.expand(GRC9V4ExpansionRequestInput.from_payload(row["expansion"]))
    require(not rejected.committed and model.snapshot() == event_snapshot, "stale event changed publication")
    continuation = committed(model.step_v4_input(request("target-positive-step")))
    require(GRC9V4.from_state(model.snapshot()).snapshot() == model.snapshot(), "event replay differs")
    model.reset()
    require(len(model.configuration.current.C) == 17, "reset erased topology event")
    return dict(before=before, source_detection=diagnostics, prefix_step=prefix,
        request=row["expansion"], event=result, after_event=after_event,
        stale_event_rejection=rejected.to_payload(), full_rollback=True,
        target_continuation=continuation, reset_on_target=state_summary(model))


def basin(family):
    model = GRC9V4.from_config(configuration(family))
    old = model.active_model_identity
    before = model.configuration
    migration = committed(model.migrate_basin_policy("select-basin-v2"))
    require(model.configuration.current == before.current and model.configuration.reset == before.reset,
            "basin policy migration altered authoritative histories")
    require(old != model.active_model_identity, "explicit v2 identity did not change")
    observations = model.compute_observables()
    require("basin_attributes" in observations, "basin observation absent")
    exact, state_only = model.snapshot(), model.snapshot(replay_mode="state_only")
    require(GRC9V4.from_state(exact).snapshot() == exact, "exact observation replay differs")
    recovered = GRC9V4.from_state(state_only)
    require(recovered.configuration.current == model.configuration.current, "state-only authority differs")
    return dict(migration=migration, old_model_identity=old,
        new_model_identity=model.active_model_identity, observation=observations["basin_attributes"],
        basin_identity=observations["basin_identity"], exact_replay=True, state_only_replay=True,
        exact_checkpoint_digest=digest(exact), state_only_checkpoint_digest=digest(state_only))


def branch_request(model, direction, target=None):
    if direction == "enable":
        declaration = dict(target_reference=target.to_payload())
    else:
        # Explicit native incoming weights/flux; V4 histories are not secretly
        # reinterpreted as V3 conductance or a second resource ledger.
        n = len(model.configuration.reference.graph.live_edge_ids)
        declaration = dict(legacy_config=dict(dt=2**-12, seed=19,
            evolution=dict(alpha=1e-12, beta=1e-12, gamma=1e-12, eta=1., kappa_c=1.,
                v0=1., rho=1., eps_tau=1e-12, site_potential_selection="quadratic",
                site_potential_params=dict(mu=0., scale=0.), eps_gradient=.01,
                eps_hessian=.01, eps_spark=0.),
            constitutive_semantic_modes=dict(boundary_mode="prune", hessian_backend="row_basis_diagonal")),
            current_incoming_weights=[1+i/16 for i in range(n)],
            reset_incoming_weights=[.75+i/32 for i in range(n)],
            current_incoming_flux=[.01*(i+1) for i in range(n)],
            reset_incoming_flux=[-.02*(i+1) for i in range(n)])
    return GRC9V4BranchRequest(direction+":"+model.lifecycle_digest,
        model.lifecycle_digest, direction, declaration)


def compatibility(family):
    model = GRC9V4.from_config(configuration(family))
    ref = model.configuration.reference
    before = state_summary(model)
    down = committed(model.migrate_branch(branch_request(model, "disable")))
    require(model.compatibility_branch == "disabled_grc9v3", "wrong branch")
    disabled = model.snapshot()
    require(GRC9V4.from_state(disabled).snapshot() == disabled, "legacy replay differs")
    try:
        model.step_v4_input(request("cannot-ignore-V4-input"))
    except ValueError:
        pass
    else:
        raise AssertionError("V4 request silently consumed by V3")
    require(model.snapshot() == disabled, "wrong-branch input changed state")
    model.step()  # Native V3 operation: its dt is in the explicit legacy config.
    legacy_observables = model.compute_observables()
    up = committed(model.migrate_branch(branch_request(model, "enable", ref)))
    step = committed(model.step_v4_input(request("returned-positive-step")))
    return dict(before=before, disable=down, disabled_state_type="DisabledGRC9V3State",
        native_observables=legacy_observables, wrong_branch_rejected=True,
        enable=up, enabled_continuation=step, after=state_summary(model))


def migration_request(model, target):
    c = model.configuration
    # Public scientific declaration, used only to compute the two history
    # channel declarations. The owner independently recomputes admission.
    inputs = GeometryStageInputs(c.reference.geometry(), c.reference.context,
        c.current, c.reset, "declare-migration", c.budget_target, (),
        c.step_index, c.time, 0., "pre_read", 0, None)
    policy = migration_history_policy(inputs, target)
    return GRCV4MigrationRequest.from_payload(dict(
        schema_version="grcv4-migration-request-v1", operation_id="migrate:"+model.lifecycle_digest,
        source_state_digest=model.state.lifecycle.scientific_state_digest,
        target_profile_id=target.profile.complete_profile_id,
        migration_policy=dict(schema_version="grcv4-migration-policy-v1",
            policy_id="typed_bidirectional_profile_migration_v1",
            resource_policy_id="identity_resource_transport_v1",
            target_readmission_policy_id="full_target_fail_closed_v1"),
        history_policy=policy.to_payload(), target_context_value={}))


def migration():
    # Two lawful routes and one explicit target-domain exclusion; family
    # availability alone never promises that every crossing is admissible.
    rows = []
    for source, destinations in (("C_OS", ("C_CI",)), ("A_CI", ("A_PC", "A_CI"))):
        refs = tuple(configuration(f).reference for f in destinations)
        model = GRC9V4.from_config(replace(configuration(source), targets=refs))
        for target in refs:
            req = migration_request(model, target)
            before = state_summary(model)
            result = committed(model.migrate_profile(req))
            rows.append(dict(before=before, request=req.to_payload(), result=result, after=state_summary(model)))
    target = configuration("A_CI").reference
    model = GRC9V4.from_config(replace(configuration("A_PC"), targets=(target,)))
    snap = model.snapshot()
    failed = model.migrate_profile(migration_request(model, target))
    require(not failed.committed and model.snapshot() == snap, "excluded A_PC source entered CI domain")
    return dict(routes=rows, target_domain_exclusion=failed.to_payload(), full_rollback=True)


def rejection(family):
    model = GRC9V4.from_config(configuration(family))
    before = model.snapshot()
    result = model.step_v4_input(request("negative-duration", -1.))
    require(not result.committed and model.snapshot() == before, "failed step mutated full publication")
    try:
        request("nonfinite", float("nan"))
    except (ValueError, TypeError):
        pass
    else:
        raise AssertionError("nonfinite input was shape-valid")
    return dict(semantic_failure=result.to_payload(), malformed_input_raises=True,
        full_rollback=True, baseline_digest=digest(before), final_digest=digest(model.snapshot()))


LESSONS = dict(evolution=evolution, checkpoint=checkpoint, sparks=sparks, expansion=expansion,
               basin=basin, compatibility=compatibility, rejection=rejection)


def run(lesson, family="C_OS", steps=3):
    start = time.monotonic()
    if lesson == "discovery":
        result = discovery()
    elif lesson == "migration":
        result = migration()
    elif lesson == "all":
        result = {name: fn(family, steps) if name == "evolution" else fn(family)
                  for name, fn in LESSONS.items()}
    elif lesson == "evolution":
        result = evolution(family, steps)
    else:
        result = LESSONS[lesson](family)
    return dict(schema="grc9v4-tutorial-run-v1", lesson=lesson, family=family,
        elapsed_seconds=round(time.monotonic()-start, 3), result=result,
        user_accepted=False, full_GRC9V4_conformance=False, G4_accepted=False)


def write_output(path, value):
    raw = json.dumps(value, indent=2, allow_nan=False).encode()+b"\n"
    path = Path(path)
    if len(raw) > 1_000_000 or path.suffix == ".xz":
        if path.suffix != ".xz":
            path = path.with_suffix(path.suffix+".xz")
        raw = lzma.compress(raw)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("xb") as stream:  # Never replace evidence from an earlier run.
        stream.write(raw)
    return path


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("lesson", choices=["discovery", *LESSONS, "migration", "all"])
    p.add_argument("--family", choices=FAMILIES, default="C_OS")
    p.add_argument("--steps", type=int, default=3, help="positive evolution steps (default 3)")
    p.add_argument("--output", help="optional new JSON path; >1 MB is automatically .xz")
    args = p.parse_args()
    if args.steps < 1:
        p.error("--steps must be positive")
    value = run(args.lesson, args.family, args.steps)
    if args.output:
        out = write_output(args.output, value)
        print(json.dumps(dict(lesson=args.lesson, family=args.family,
            elapsed_seconds=value["elapsed_seconds"], output=str(out), status="passed")))
    else:
        print(json.dumps(value, indent=2, allow_nan=False))


if __name__ == "__main__":
    main()
