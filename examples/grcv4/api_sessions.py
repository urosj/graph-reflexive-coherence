"""Runnable debugging, migration and restoration examples; see api_sessions.md.

Run from a checkout: .venv/bin/python examples/grcv4/api_sessions.py --list
"""

import argparse
import json
import sys
from dataclasses import replace
from pathlib import Path
from tempfile import TemporaryDirectory

ROOT = Path(__file__).resolve().parents[2]
# Match the checkout-only fixture convention used by the other V4 examples.
for entry in (ROOT, ROOT / "src"):
    if str(entry) not in sys.path:
        sys.path.insert(0, str(entry))

import numpy as np

from examples.grcv4.session_support import (
    Session,
    differences,
    family,
    fresh,
    require,
    transfer,
)
from pygrc.models.grc_v4_exact import ExactBackend, exact_backend
from pygrc.models.grc_v4_migration import (
    MigrationAdmissionError,
    map_migration,
    migration_history_policy,
)
from pygrc.models.grc_v4_step import ResourceBoundaryError

SCENARIOS = {
    "debug": "Trace, inspect, fork/edit, apply, compare and replay: A_CI and C_CI+PC.",
    "migration-cycle": "A_CI -> A_PC -> A_OS -> A_CI, compared at equal step/time.",
    "os-excursion": "A_CI -> A_OS, edit/step, migrate back; measure agreement, do not assume it.",
    "carrier-excursion": "A_CI -> A_CI+PC for N steps, migrate back versus stay; separate Z loss from rollback.",
    "admission-gates": "A_OS versus C_RG2b: nonconserving edit and conserving out-of-domain edit.",
    "lifecycle": "Public GRCV4: migration receipts, atomic rejection, snapshot/save/load, replay and reset.",
}


def rejected(action, kind):
    try:
        action()
    except kind as exc:
        return {
            "type": type(exc).__name__,
            "message": str(exc),
            "stage": getattr(exc, "stage", None),
            "code": getattr(exc, "code", None),
        }
    raise AssertionError("expected typed rejection was admitted")


def read_difference(left, right):
    result = {}
    for key in sorted(set(left) | set(right)):
        a, b = left.get(key), right.get(key)
        if a is not None and b is not None:
            require(
                np.asarray(a).shape == np.asarray(b).shape,
                "read comparison shape mismatch: " + key,
            )
        result[key] = (
            {"before_present": a is not None, "after_present": b is not None}
            if a is None or b is None
            else {
                "delta": (np.asarray(b) - np.asarray(a)).tolist(),
                "l2": float(np.linalg.norm(np.asarray(b) - np.asarray(a))),
            }
        )
    return result


def debug(session, candidate="A"):
    states, backend = session.fixtures(candidate)
    name = "CI" if candidate == "A" else "CI+PC"
    trace, reads = [states[name]], []
    for _ in range(3):
        after, row = session.advance(trace[-1], backend)
        trace.append(after)
        reads.append(row)
    before = trace[1]
    identity = before.scientific_state_id
    edited = transfer(before, 0.05)
    after, row = session.advance(edited, backend)
    failure = rejected(
        lambda before=before, backend=backend: session.advance(
            transfer(before, 0.05, conserve=False), backend
        ),
        ResourceBoundaryError,
    )
    # The inspector uses saved reads from trace step 1 -> 2, not a fresh solve.
    inspected = reads[1]
    replay, _ = session.advance(before, backend)
    require(
        replay.scientific_state_id == trace[2].scientific_state_id,
        "deterministic replay differs",
    )
    require(
        before.scientific_state_id == identity and trace[1] is before,
        "fork mutated original",
    )
    require(
        transfer(before, 0.0).scientific_state_id == identity,
        "no-op edit changed identity",
    )
    require(edited.reset == before.reset, "fork modified reset baseline")
    return {
        "family": family(before),
        "trace": [session.state_record(x) for x in trace],
        "inspected_step": inspected,
        "edited_step": row,
        "comparison": differences(trace[2], after),
        "read_comparison": read_difference(inspected["read"], row["read"]),
        "rejected_charge_edit": failure,
        "replay_identical": True,
        "original_unchanged": True,
        "no_op_identical": True,
        "scope": "immutable_numerical_records_not_public_set_state_or_commit",
    }


def migration_cycle(session):
    states, backend = session.fixtures("A")
    initial = states["CI"]
    branch = initial
    baseline = initial
    hops = []
    for target_name in ("PC", "OS", "CI"):
        mapped, record = session.migrate(branch, states[target_name].geometry.reference)
        branch, row = session.advance(
            mapped, backend
        )  # actual target admission and step
        baseline, base_row = session.advance(baseline, backend)
        hops.append(
            {
                "migration": record,
                "step": row,
                "matched_baseline": base_row,
                "comparison": differences(baseline, branch),
            }
        )
    wrong = migration_history_policy(initial, initial.geometry.reference)
    failure = rejected(
        lambda: map_migration(initial, states["PC"].geometry.reference, wrong),
        MigrationAdmissionError,
    )
    identity_map = fresh(
        map_migration(
            branch,
            branch.geometry.reference,
            migration_history_policy(branch, branch.geometry.reference),
        )
    )
    require(
        identity_map.scientific_state_id == branch.scientific_state_id,
        "identity migration changed state",
    )
    return {
        "hops": hops,
        "matched_physical_steps": 3,
        "wrong_policy": failure,
        "identity_map_accepted": True,
        "initial": session.state_record(initial),
        "scope": "pure_maps_then_target_steps_no_lifecycle_receipts",
    }


def excursion(session, target_name, steps):
    states, backend = session.fixtures("A")
    initial = states["CI"]
    before = initial
    for _ in range(3):
        before, _ = session.advance(before, backend)
    old = transfer(before, 0.05)
    new, migration = session.migrate(before, states[target_name].geometry.reference)
    new = transfer(new, 0.05)
    rows = []
    for _ in range(steps):
        old, old_row = session.advance(old, backend)
        new, new_row = session.advance(new, backend)
        rows.append(
            {
                "comparison": differences(old, new),
                "read_comparison": read_difference(old_row["read"], new_row["read"]),
                "baseline": old_row,
                "excursion": new_row,
            }
        )
    returned, back = session.migrate(new, initial.geometry.reference)
    require(
        returned.current.C == new.current.C and returned.current.W_A == new.current.W_A,
        "migration back rewound evolved C/W",
    )
    require(returned.current.Z_4 is None, "carrier was not dropped")
    old_next, old_read = session.advance(old, backend)
    restored_next, restored_read = session.advance(returned, backend)
    stayed, stayed_read = session.advance(new, backend)
    # Re-executing the untouched fork is the rollback/replay control; it costs a solve.
    replay, _ = session.advance(transfer(before, 0.05), backend)
    require(
        replay.scientific_state_id == rows[0]["baseline"]["after"]["kernel_digest"],
        "replay differs",
    )
    return {
        "target": target_name,
        "steps": steps,
        "entry": migration,
        "rows": rows,
        "return_map": back,
        "after_return": differences(old_next, restored_next),
        "after_staying": differences(old_next, stayed),
        "final_reads": {
            "baseline": old_read,
            "returned": restored_read,
            "stayed": stayed_read,
        },
        "replay_identical": True,
        "migration_back_preserves_evolved_C_W": True,
        "interpretation": "observed_binary64_differences_not_a_universal_OS_CI_equivalence_or_certified_separation",
    }


def admission_gates(session):
    from fractions import Fraction

    from pygrc.models.grc_v4_rg2b_graph import RG2bGraphDomain

    output = {}
    for candidate, name in [("A", "OS"), ("C", "RG2b")]:
        states, backend = session.fixtures(candidate)
        before = states[name]
        original = before.scientific_state_id
        ordinary, row = session.advance(before, backend)
        edited, changed = session.advance(transfer(before, 0.002), backend)
        charge = rejected(
            lambda before=before, backend=backend: session.advance(
                transfer(before, 0.05, conserve=False), backend
            ),
            ResourceBoundaryError,
        )
        large = transfer(before, 0.05)
        if name == "RG2b":
            domain = RG2bGraphDomain.from_identity(
                before.geometry.reference.profile.params_resolved.realization.extension_evaluator_id
            )
            budget = [
                str(
                    Fraction(domain.inner)
                    - abs(Fraction(v) - Fraction(domain.center_C))
                )
                for v in before.current.C
            ]
            out_of_domain = rejected(
                lambda large=large, backend=backend: session.advance(large, backend),
                ResourceBoundaryError,
            )
        else:
            budget = None
            admitted, _ = session.advance(large, backend)
            out_of_domain = {"admitted": True, "after": session.state_record(admitted)}
        require(before.scientific_state_id == original, "gate probe changed original")
        output[family(before)] = {
            "ordinary": row,
            "edited": changed,
            "comparison": differences(ordinary, edited),
            "read_comparison": read_difference(row["read"], changed["read"]),
            "charge_rejection": charge,
            "large_conserving_edit": out_of_domain,
            "rg_resource_inner_margin_exact": budget,
        }
    output["interpretation"] = (
        "Different candidate laws and parameters as well as realizations; not an isolated substrate comparison."
    )
    return output


def lifecycle(session):
    """Use actual public transactions, not the pure map as a commit stand-in."""
    from pygrc.models.grc_v4 import GRCV4, GRCV4MigrationRequest, GRCV4StepRequestInput
    from pygrc.models.grc_v4_codec import canonical_json_bytes
    from pygrc.models.grc_v4_state import FrozenJSONMap

    states, backend = session.fixtures("A")
    initial = states["CI"]
    refs = {
        n: s.geometry.reference for n, s in states.items() if n in ("CI", "PC", "OS")
    }
    owner = GRCV4(
        initial, targets=(refs["PC"], refs["OS"]), differential_reference=backend
    )

    def request(dt, operation):
        return GRCV4StepRequestInput(
            "grcv4-step-request-input-v1", operation, dt, FrozenJSONMap({})
        )

    first = owner.step_v4_input(request(initial.dt, "session-start"))
    require(first.committed, "initial public step rejected")
    hops = []
    ref = refs["CI"]
    for number, name in enumerate(("PC", "OS", "CI")):
        state = owner.state.lifecycle
        inputs = fresh(
            replace(
                initial,
                geometry=ref.geometry(),
                current=state.current,
                reset=state.reset.authoritative,
                Q_target=state.Q_target,
                step_index=state.step_index,
                time=state.time,
            )
        )
        history = migration_history_policy(inputs, refs[name])
        command = GRCV4MigrationRequest.from_payload(
            {
                "schema_version": "grcv4-migration-request-v1",
                "operation_id": f"session-migration-{number}",
                "source_state_digest": state.scientific_state_digest,
                "target_profile_id": refs[name].profile.complete_profile_id,
                "migration_policy": {
                    "schema_version": "grcv4-migration-policy-v1",
                    "policy_id": "typed_bidirectional_profile_migration_v1",
                    "resource_policy_id": "identity_resource_transport_v1",
                    "target_readmission_policy_id": "full_target_fail_closed_v1",
                },
                "history_policy": history.to_payload(),
                "target_context_value": {},
            }
        )
        result = owner.migrate_profile(command)
        require(
            result.committed, f"public migration to {name} rejected: {result.failure}"
        )
        after = owner.state.lifecycle
        require(
            (state.step_index, state.time) == (after.step_index, after.time),
            "public migration advanced clock",
        )
        for old, new in (
            (state.current, after.current),
            (state.reset.authoritative, after.reset.authoritative),
        ):
            require(
                old.C == new.C and old.W_A == new.W_A, "public migration changed C/W"
            )
        hops.append({"request": command.to_payload(), "result": result.to_payload()})
        step = owner.step_v4_input(request(initial.dt, f"session-after-{name}"))
        require(step.committed, "target public step rejected")
        ref = refs[name]
    snapshot = owner.snapshot()
    frozen = canonical_json_bytes(snapshot)
    failure = owner.step_v4_input(request(-1, "negative-duration"))
    require(
        not failure.committed and canonical_json_bytes(owner.snapshot()) == frozen,
        "failed operation changed publication",
    )
    with TemporaryDirectory(prefix="grcv4-api-session-") as directory:
        path = Path(directory) / "snapshot.json"
        owner.save(str(path))
        restored = GRCV4.load(str(path))
        require(
            path.read_bytes() == frozen
            and canonical_json_bytes(restored.snapshot()) == frozen,
            "save/load changed snapshot",
        )
    duplicate = owner.duplicate()
    command = request(initial.dt, "deterministic-continuation")
    a = owner.step_v4_input(command)
    b = restored.step_v4_input(command)
    require(a.committed and b.committed and a == b, "public replay result differs")
    require(
        canonical_json_bytes(owner.snapshot())
        == canonical_json_bytes(restored.snapshot()),
        "public replay publication differs",
    )
    require(
        canonical_json_bytes(duplicate.snapshot()) == frozen,
        "duplicate changed with original",
    )
    duplicate.reset()
    require(
        duplicate.state.lifecycle.current
        == duplicate.state.lifecycle.reset.authoritative,
        "reset did not restore baseline",
    )
    require(
        owner.state.lifecycle.current != duplicate.state.lifecycle.current,
        "reset affected original branch",
    )
    return {
        "scope": "public_GRCV4_lifecycle",
        "supported_profiles": sorted(owner.list_supported_profiles()),
        "migrations": hops,
        "failure": failure.to_payload(),
        "snapshot": snapshot,
        "replay_identical": True,
        "save_load_identical": True,
        "duplicate_independent": True,
        "reset_restores_declared_baseline": True,
        "final_scientific_digest": owner.state.lifecycle.scientific_state_digest,
        "final_lifecycle_digest": owner.state.lifecycle.lifecycle_digest,
    }


def run(scenario, *, steps=5, session=None):
    if type(steps) is not int or steps < 1:
        raise ValueError("steps must be a positive integer")
    session = Session() if session is None else session
    if scenario == "debug":
        return {c: debug(session, c) for c in ("A", "C")}
    if scenario == "migration-cycle":
        return migration_cycle(session)
    if scenario == "os-excursion":
        return excursion(session, "OS", steps)
    if scenario == "carrier-excursion":
        return excursion(session, "CI+PC", steps)
    if scenario == "admission-gates":
        return admission_gates(session)
    if scenario == "lifecycle":
        return lifecycle(session)
    raise ValueError("unknown scenario")


def report(scenario, *, steps=5):
    session = Session()
    with exact_backend(ExactBackend.FLINT):
        result = run(scenario, steps=steps, session=session)
    declarations = {
        candidate: {
            "initial_inputs": {
                name: state.to_payload() for name, state in states.items()
            },
            "differential_reference": None if backend is None else backend.to_payload(),
        }
        for candidate, (states, backend) in session._fixtures.items()
    }
    return {
        "schema": "grcv4-api-example-v1",
        "scenario": scenario,
        "description": SCENARIOS[scenario],
        "scope": "checkout_example_not_support_or_acceptance_evidence",
        "numerical_comparisons": "observed_binary64_not_certified_separation",
        "declared_fixtures_not_all_executed": declarations,
        "result": result,
    }


def positive_int(value):
    result = int(value)
    if result < 1:
        raise argparse.ArgumentTypeError("must be positive")
    return result


def render(value):
    """Present a completed report without executing or certifying it again."""
    reports = (
        value.get("reports")
        if value.get("schema") == "grcv4-api-example-suite-v1"
        else [value]
    )
    for r in reports:
        require(
            r.get("schema") == "grcv4-api-example-v1"
            and r.get("scenario") in SCENARIOS,
            "not an API example report",
        )
        name, result = r["scenario"], r["result"]
        print(f"{name}: {r['description']}")
        if name == "debug":
            for row in result.values():
                c = row["comparison"]
                print(
                    f"  {row['family']}: |dC|={c['C']['l2']:.6g}; "
                    f"charge edit={row['rejected_charge_edit']['code']}; replay={row['replay_identical']}"
                )
        elif name == "migration-cycle":
            for hop in result["hops"]:
                m = hop["migration"]
                print(
                    f"  {m['source']['family']} -> {m['target']['family']}: "
                    f"W={m['policy']['candidate']['disposition']}; "
                    f"Z={m['policy']['carrier']['disposition']}; "
                    f"matched step={hop['comparison']['step']}"
                )
        elif name.endswith("excursion"):
            for row in result["rows"]:
                c = row["comparison"]
                print(
                    f"  step {c['step']:2d}  time={c['time']:.9g}  "
                    f"|dC|={c['C']['l2']:.6g}  |dW|={c['W_A']['l2']:.6g}"
                )
            for key in ("after_return", "after_staying"):
                c = result[key]
                print(
                    f"  {key}: |dC|={c['C']['l2']:.6g}; "
                    f"same scientific digest={c['same_kernel_digest']}"
                )
        elif name == "admission-gates":
            for key in ("A_OS", "C_RG2b"):
                row = result[key]
                large = row["large_conserving_edit"]
                print(
                    f"  {key}: charge={row['charge_rejection']['code']}; "
                    f"larger conserving edit={large.get('code', 'admitted')}"
                )
        elif name == "lifecycle":
            print(
                f"  {len(result['migrations'])} committed migrations; "
                f"save/load={result['save_load_identical']}; replay={result['replay_identical']}; "
                f"independent fork={result['duplicate_independent']}"
            )
    print(
        "Observed fixture results; no universal equivalence or certified separation. Full diagnostics: --json."
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--list", action="store_true", help="list scenarios without executing a model"
    )
    parser.add_argument(
        "--scenario", choices=tuple(SCENARIOS) + ("all",), default="debug"
    )
    parser.add_argument(
        "--steps",
        type=positive_int,
        default=5,
        help="matched physical steps during OS/carrier excursion (try 1, 5, 10)",
    )
    parser.add_argument(
        "--json", action="store_true", help="print full diagnostics as JSON"
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="write full JSON to a new file; existing files are preserved",
    )
    parser.add_argument(
        "--render-from",
        type=Path,
        help="inspect saved JSON without executing any model",
    )
    args = parser.parse_args()
    if args.list:
        for name, description in SCENARIOS.items():
            print(f"{name:20s} {description}")
        return
    if args.output and args.output.exists():
        parser.error("--output already exists")
    if args.render_from:
        value = json.loads(args.render_from.read_text())
    else:
        names = tuple(SCENARIOS) if args.scenario == "all" else (args.scenario,)
        reports = []
        for name in names:
            print(f"Running {name}...", file=sys.stderr, flush=True)
            reports.append(report(name, steps=args.steps))
        value = (
            reports[0]
            if len(reports) == 1
            else {"schema": "grcv4-api-example-suite-v1", "reports": reports}
        )
    encoded = json.dumps(value, indent=2, allow_nan=False) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with args.output.open("x") as stream:
            stream.write(encoded)
    if args.json:
        print(encoded, end="")
    else:
        render(value)


if __name__ == "__main__":
    main()
