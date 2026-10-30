"""P9-10.2: reuse accepted execution; check saved operands, not native trajectories."""

from __future__ import annotations

import argparse
import ast
from concurrent.futures import ProcessPoolExecutor
from contextlib import contextmanager, ExitStack
from copy import deepcopy
from fractions import Fraction as Q
import hashlib
import json
import math
from pathlib import Path
import platform
import subprocess
from unittest.mock import patch

import rfc8785
import p9101b_target_compatibility as targets
import p9101c_target_basin as basin

ROOT, FAMILIES = targets.ROOT, targets.FAMILIES
BASE = "implementation/phase-9-grcv4/"
SELF = BASE + "verification/p9102_verification.py"
TEST = BASE + "verification/test_p9102_verification.py"
PATH = BASE + "tranche-10/P9-10.2-Verification.json"
REVIEW = BASE + "tranche-10/P9-10.2-Review.md"
SOURCE_EPOCH = "02528b5d"
OTHER = ("A_OS", "C_PC", "C_CI_PC", "A_CI_PC", "C_RG2b", "A_RG2b")


def require(value, message):
    if not value:
        raise ValueError(message)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def seal(value):
    body = {k: v for k, v in value.items() if k != "record_digest"}
    return dict(body, record_digest=sha(rfc8785.dumps(body)))


def reference(root, name):
    path = Path(name)
    require(not path.is_absolute() and ".." not in path.parts, "nonportable source")
    return dict(path=name, sha256=sha((root / name).read_bytes()))


def accepted_inputs(root):
    """Authenticate the pinned decisions directly, without recursive old campaigns.

    Current-path applicability is checked separately. A historical source-epoch
    projection is neither needed nor treated as current numerical execution.
    """
    import p9101a_acceptance as a
    import p9101b_acceptance as b
    import p9101c_acceptance as c
    decisions = {}
    for module, closed in ((a, "P9_10_1a_closed"), (b, "P9_10_1b_closed"),
                           (c, "P9_10_1c_closed")):
        raw = (root / module.PATH).read_bytes()
        decision = json.loads(raw)
        historical = subprocess.check_output(
            ["git", "show", SOURCE_EPOCH + ":" + module.PATH], cwd=root)
        canonical = c.execution.seal if module is c else targets.seal
        require(raw == historical and decision == canonical(decision)
                and decision["record_digest"] == module.ACCEPTANCE
                and decision["user_accepted"] is True and decision[closed] is True
                and decision["families"] == list(FAMILIES), "unaccepted or changed predecessor")
        for ref in decision["review_sources"]:
            require(reference(root, ref["path"])["sha256"] == ref["sha256"],
                    "accepted predecessor review drift")
        for ref in decision.get("evidence", []) if isinstance(decision.get("evidence"), list) else []:
            require(reference(root, ref["path"])["sha256"] == ref["sha256"],
                    "accepted execution evidence drift")
        decisions[closed] = decision
    return decisions


def accepted_family(root, family):
    decisions = accepted_inputs(root)
    execution, eref = targets.load(root, family)
    exact, xref = basin.load(root, family)
    for value, ref, roster in (
        (execution, eref, decisions["P9_10_1b_closed"]["evidence"]),
        (exact, xref, decisions["P9_10_1c_closed"]["direct_target_evidence"]),
    ):
        require(value == targets.seal(value) and value["family"] == family,
                "accepted family record identity")
        matches = [r for r in roster if r["path"] == ref["path"]]
        require(len(matches) == 1 and all(matches[0][k] == ref[k]
                for k in ("path", "sha256", "record_digest")), "unaccepted family evidence")
    require(exact["predecessor"] == eref, "exact-target predecessor substitution")
    return execution, eref, exact, xref


@contextmanager
def no_native_runs():
    """A retained check must never silently invoke construction/replay/readmission."""
    from pygrc.models import GRC9V4
    from pygrc.models import grc_9_v4_basin, grc_v4_transport

    with ExitStack() as stack:
        for owner, method in ((GRC9V4, "from_config"), (GRC9V4, "from_state"),
                              (grc_9_v4_basin, "_read_once"),
                              (grc_v4_transport, "provisional_continuity")):
            stack.enter_context(patch.object(owner, method, side_effect=AssertionError(
                "P9-10.2 retained validation must not execute native trajectories")))
        yield


def source_applicability(root):
    """Verify the inspected additive changes; unknown changes require review."""
    prefix = "src/pygrc/models/"
    original = subprocess.check_output(
        ["git", "ls-tree", "-r", "--name-only", SOURCE_EPOCH, "src/pygrc"], cwd=root
    ).decode().splitlines()
    rows, same = [], 0
    extension = ', '.join('"' + f + '"' for f in OTHER)
    first = ', '.join('"' + f + '"' for f in FAMILIES)
    rg_only = {prefix + "grc_v4_rg2b.py", prefix + "grc_9_v4_crg2b_connected.py",
               prefix + "grc_9_v4_arg2b_connected.py"}
    # Pinned RG-only changes are outside the selected dispatch. Do not infer
    # their correctness or RG conformance from this first-group check.
    for name in original:
        old = subprocess.check_output(["git", "show", SOURCE_EPOCH + ":" + name], cwd=root)
        raw = (root / name).read_bytes()
        if old == raw:
            same += 1
            continue
        if name in rg_only:
            disposition = "RG2b_only_not_selected_by_these_four_families"
        else:
            text = raw.decode()
            if name == prefix + "grc_9_v4_api_lifecycle.py":
                text = text.replace('PUBLIC_ENABLED_FAMILIES = (' + first + ', ' + extension + ')',
                                    'PUBLIC_ENABLED_FAMILIES = (' + first + ')')
            elif name == prefix + "grc_9_v4_legacy.py":
                text = text.replace('FAMILIES = frozenset((' + first + ', ' + extension + '))',
                                    'FAMILIES = frozenset((' + first + '))')
            elif name == prefix + "grc_9_v4_owner.py":
                for family, cls in zip(OTHER, ("AOS", "CPC", "CCIPC", "ACIPC", "CRG2b", "ARG2b")):
                    text = text.replace(f'    "{family}": events.GRC9V4{cls}Operation,\n', '')
                text = text.replace('expected a selected native GRC9V4 state',
                                    'expected a selected native C_OS/C_CI/A_CI/A_PC state')
            elif name == prefix + "grc_9_v4_crossing.py":
                text = text.replace('profile.identity_payload.realization in ("PC", "CI+PC")',
                                    'profile.identity_payload.realization == "PC"')
            else:
                raise ValueError("unreviewed first-group source change: " + name)
            require(ast.dump(ast.parse(text)) == ast.dump(ast.parse(old)),
                    "first-group source changed beyond reviewed extension: " + name)
            disposition = "same_first_group_path_after_explicit_additive_projection"
        rows.append(dict(path=name, original_sha256=sha(old), current_sha256=sha(raw),
                         disposition=disposition))
    current = {p.relative_to(root).as_posix() for p in (root / "src/pygrc").rglob("*")
               if p.is_file() and p.suffix in (".py", ".json")}
    additions = current - set(original)
    require(additions <= rg_only, "unreviewed runtime addition")
    rows.extend(dict(**reference(root, n), disposition="RG2b_only_new_module")
                for n in sorted(additions))
    return dict(source_epoch=subprocess.check_output(
        ["git", "rev-parse", SOURCE_EPOCH], cwd=root).decode().strip(),
        unchanged_files=same, reviewed_changes=rows,
        original_execution_relabelled=False, native_rerun_required=False)


def charge_oracle(values):
    """Independent padded recursive tree, exact rational nodes rounded once."""
    require(all(math.isfinite(x) and x >= 0 for x in values), "charge domain")
    if not values:
        return 0.0
    size = 1 << (len(values) - 1).bit_length()
    leaves = tuple(values) + (0.0,) * (size - len(values))

    def subtree(lo, hi):
        if hi - lo == 1:
            return leaves[lo]
        middle = (lo + hi) // 2
        result = float(Q(subtree(lo, middle)) + Q(subtree(middle, hi)))
        require(math.isfinite(result), "charge overflow")
        return result

    return subtree(0, size)


def charge_expected(values, target, absolute, relative):
    actual = charge_oracle(values)
    delta = Q(actual) - Q(target)
    bound = Q(absolute) + Q(relative) * max(abs(Q(target)), 1)
    residual = float(delta)
    require(math.isfinite(residual), "charge residual overflow")
    return dict(actual=actual.hex(), residual=residual.hex(),
                admitted=abs(delta) <= bound, exact_bound=str(bound),
                stored_coordinate_sum=str(sum(map(Q, values), Q(0))),
                tree_minus_coordinate_sum=str(Q(actual) - sum(map(Q, values), Q(0))))


def charge_check(values, target, profile):
    from pygrc.models.grc_v4_geometry import GRCV4Graph, VertexScalar
    from pygrc.models.grc_v4_transport import ChargeEvaluation

    policy = profile.params_resolved.charge
    expected = charge_expected(values, target, policy.absolute_tolerance, policy.relative_tolerance)
    resource = VertexScalar(GRCV4Graph(tuple(range(len(values))), ()), tuple(values))
    actual = ChargeEvaluation(resource, target, profile)
    require((actual.actual.hex(), actual.residual.hex(), actual.admitted)
            == (expected["actual"], expected["residual"], expected["admitted"]),
            "independent charge comparison")
    require(actual.resource == resource and actual.remainder is None, "charge repaired resource")
    require(actual.receipt_values() == dict(target_charge=target, admitted_charge=actual.actual,
                                           residual=actual.residual), "charge receipt values")
    return expected


def charge_edges(profile):
    from pygrc.models.grc_v4_codec import payload_identity
    from pygrc.models.grc_v4_profile import resolve_profile
    from pygrc.models.grc_v4_exact import exact_backend, ExactBackend

    large, tiny = float(2**53), math.ulp(0.0)
    cases = [
        ("empty", [], 0., 0., 0.),
        ("subnormal", [tiny], 0., tiny, 0.),
        ("tree_tie_odd", [large, 1., 1.], large, 0., 0.),
        ("tree_differs_from_left_fold", [large, 1., 1., 1.], large + 2, 0., 0.),
        ("canonical_order_matters", [1., 1., large], large + 2, 0., 0.),
        ("absolute_equality", [1.25], 1., .25, 0.),
        ("absolute_above", [math.nextafter(1.25, math.inf)], 1., .25, 0.),
        ("absolute_below", [math.nextafter(.75, 0.)], 1., .25, 0.),
        ("relative_floor", [.75], .5, 0., .25),
        ("relative_equality", [5.], 4., 0., .25),
        ("rounded_bound_must_not_enlarge", [math.nextafter(3., math.inf)], 3., 0.,
         float.fromhex("0x1.5555555555555p-53")),
        ("adjacent_relative_admission", [math.nextafter(3., math.inf)], 3., 0.,
         math.nextafter(float.fromhex("0x1.5555555555555p-53"), math.inf)),
    ]
    rows = []
    for label, values, target, absolute, relative in cases:
        p = deepcopy(profile.params_resolved.to_payload())
        i = deepcopy(profile.identity_payload.to_payload())
        p["charge"].update(absolute_tolerance=absolute, relative_tolerance=relative)
        i["params_hash"] = payload_identity("resolved_params", p)
        configured = resolve_profile(p, i)
        outputs = {}
        for backend in (ExactBackend.PYTHON, ExactBackend.FLINT):
            with exact_backend(backend):
                outputs[backend.value] = charge_check(values, target, configured)
        require(outputs["python"] == outputs["flint"], "charge backend disagreement")
        rows.append(dict(case=label, C=[x.hex() for x in values], target=target.hex(),
                         absolute=absolute.hex(), relative=relative.hex(), **outputs))
    require(rows[3]["python"]["actual"] != sum([large, 1., 1., 1.]).hex()
            or rows[3]["python"]["actual"] != float(sum(map(Q, [large, 1., 1., 1.]))).hex(),
            "charge controls do not discriminate alternative reductions")
    require(not rows[-2]["python"]["admitted"] and rows[-1]["python"]["admitted"],
            "relative edge controls")
    return dict(scope="synthetic_charge_kernel_not_native_profile_or_trajectory_admission",
                oracle="recursive_padded_tree_exact_fraction_nodes_binary64_roundTiesToEven",
                cases=rows, evaluations=2 * len(rows), backends=["python", "flint"])


def thaw(value):
    if isinstance(value, dict):
        if set(value) == {"_items"}:
            return {k: thaw(v) for k, v in value["_items"]}
        return {k: thaw(v) for k, v in value.items()}
    return [thaw(v) for v in value] if isinstance(value, list) else value


def ledger_check(owner, result):
    """Independent content hashes, primary-parent chain and emitted delta join."""
    receipts = owner["receipts"]
    require(receipts and len({r["receipt_id"] for r in receipts}) == len(receipts),
            "empty or repeated receipt")
    groups, seen = [], set()
    for r in receipts:
        require(r["schema_version"] == "grcv4-successful-receipt-envelope-v1",
                "failure in successful ledger")
        payload = r["identity_payload"]
        require(r["receipt_id"] == "grc-receipt-sha256:" + sha(rfc8785.dumps(payload)),
                "receipt content identity")
        require(payload["core"]["disposition"] == "committed", "noncommitting receipt")
        if not groups or r["commit_id"] != groups[-1][0]["commit_id"]:
            require(r["commit_id"] not in seen, "noncontiguous commit group")
            seen.add(r["commit_id"])
            groups.append([])
        groups[-1].append(r)
    for i, group in enumerate(groups):
        core = group[0]["identity_payload"]["core"]
        expected = [] if i == 0 else [groups[i - 1][0]["receipt_id"]]
        for r in group:
            require(r["identity_payload"]["core"] == core, "commit core disagreement")
            require(core["parent_receipt_ids"] == expected, "receipt parent DAG")
        if i:
            previous = groups[i - 1][0]["identity_payload"]["core"]
            for field in ("state_digest", "reset_digest", "model_identity", "graph_digest",
                          "authoritative_digest"):
                require(core["source_" + field] == previous["target_" + field],
                        "receipt endpoint chain: " + field)
    require(len(groups) == len(owner["journal"]), "journal/receipt group count")
    last = groups[-1][0]["identity_payload"]["core"]
    require(last["target_state_digest"] == owner["state"]["scientific_digest"]
            and last["target_reset_digest"] == owner["state"]["reset_digest"]
            and last["target_model_identity"] == owner["state"]["model_identity"],
            "receipt final endpoint")
    delta = thaw(result["emitted_receipts"])
    match = [g for g in groups if g[0]["commit_id"] == result["commit_id"]]
    require(len(match) == 1 and delta == match[0], "emitted delta differs from persistent ledger")
    core = delta[0]["identity_payload"]["core"]
    commit = dict(schema_version="grcv4-commit-payload-v1", operation_id=core["operation_id"],
                  source_state_digest=core["source_state_digest"],
                  target_state_digest=core["target_state_digest"],
                  emitted_receipt_ids=[r["receipt_id"] for r in delta],
                  target_step_index=result["step_index"], target_time=result["time"])
    require(result["commit_id"] == "grc-commit-sha256:" + sha(rfc8785.dumps(commit)),
            "runtime commit preimage")
    charge = next(r["identity_payload"] for r in delta
                  if r["identity_payload"]["schema_version"] == "grcv4-charge-receipt-v1")
    observations = thaw(result["observables"])
    require({k: charge[k] for k in ("target_charge", "admitted_charge", "residual")}
            == observations["charge"], "receipt/observable charge disagreement")
    require(charge["residual"] == float(Q(charge["admitted_charge"]) - Q(charge["target_charge"])),
            "receipt residual arithmetic")
    return dict(receipts=len(receipts), commit_groups=len(groups),
                emitted_delta_receipts=len(delta), full_parent_chain=True,
                final_endpoint_bound=True, emitted_delta_bound=True,
                ordinary_commit_preimage_verified=True)


def family_check(root, family, *, equations=True):
    from pygrc.models.grc_v4_exact import exact_backend, ExactBackend
    with no_native_runs(), exact_backend(ExactBackend.FLINT):
        execution, eref, exact, xref = accepted_family(root, family)
        basin.validate(exact, execution["evidence"]["v2"], equations=equations)
        native_path = targets.BASE + "P9-10.1a-Native-" + family + ".json"
        native = json.loads((root / native_path).read_bytes())
        require(native["family"] == family and native == targets.seal(native)
                and native["evidence"]["lifecycle"]["exact_replay"] is True
                and native["evidence"]["lifecycle"]["state_only"] is True,
                "missing accepted explicit replay modes")
        versions = []
        for version in ("v1", "v2"):
            e = execution["evidence"][version]
            require(e["disabled_replay"] and e["enabled_replay"], "missing accepted replay")
            ledger = ledger_check(e["final_checkpoint"]["owner"], e["enabled_continuation"])
            versions.append(dict(version=version, subject=e["subject"],
                                 original_replay_executed=True, replay_rerun=False,
                                 ledger=ledger))
        charges = []
        for case in exact["observations"]:
            saved = basin.restore_state(case["saved_native_state"], family)
            for role in ("current", "reset"):
                values = getattr(saved.inputs, role).C
                check = charge_check(values, saved.inputs.Q_target,
                                     saved.inputs.geometry.reference.profile)
                require(check["admitted"], "saved admitted state fails charge")
                charges.append(dict(boundary=case["label"], role=role,
                                    source_ref=dict(xref, json_pointer="/observations/" +
                                                    str(exact["observations"].index(case)) +
                                                    "/saved_native_state/inputs/" + role),
                                    **check))
        return dict(family=family, outcome="passed_bounded_retained_verification",
                    execution_ref=eref, exact_target_ref=xref, versions=versions,
                    inherited_replay_modes=dict(source_ref=reference(root, native_path),
                        exact_observation=True, state_only=True, native_rerun=False,
                        subject_scope="original_10.1a_subjects_not_transferred_to_10.1b_targets"),
                    independent_charge_checks=charges,
                    independent_equations_recomputed=4,
                    full_selected_read_and_classification_checked=True,
                    exact_CI_root_signs_claimed=False, native_steps=0, native_replays=0)


def bindings(root):
    names = {SELF, TEST, REVIEW,
             BASE + "verification/p9101c_target_basin.py",
             BASE + "verification/p9101a_basin_oracle.py",
             BASE + "verification/p9101b_target_compatibility.py",
             "specs/grc-v4-spec.md", "specs/grc-9-v4-spec.md",
             "specs/grc-9-v4-basin-interface.md"}
    # Bind the executable readers/certifiers as well as production dependencies.
    names.update(p.relative_to(root).as_posix()
                 for p in (root / "src/pygrc").rglob("*")
                 if p.is_file() and p.suffix in (".py", ".json"))
    names.update(p.relative_to(root).as_posix()
                 for p in (root / (BASE + "verification")).glob("p9*_historical.py"))
    for pattern in ("p9101*.py", "test_p9101*.py", "test_p980*.py"):
        names.update(p.relative_to(root).as_posix()
                     for p in (root / (BASE + "verification")).glob(pattern))
    names.update(p.relative_to(root).as_posix()
                 for p in (root / "tests/models").glob("test_grc*.py"))
    return [reference(root, n) for n in sorted(names)]


def run(root=ROOT, workers=4):
    from p9101c_acceptance import PATH as acceptance_path
    from pygrc.models.grc_v4_profile import resolve_profile
    import flint
    import numpy

    with no_native_runs():
        accepted = accepted_inputs(root)["P9_10_1c_closed"]
    before = bindings(root)
    applicability = source_applicability(root)
    with ProcessPoolExecutor(max_workers=workers) as pool:
        futures = [pool.submit(family_check, root, f) for f in FAMILIES]
        rows = [f.result() for f in futures]
    raw = basin.load(root, "C_OS")[0]["observations"][0]["saved_native_state"]
    p = raw["inputs"]["reference"]["profile"]
    edges = charge_edges(resolve_profile(p["params_resolved"], p["identity_payload"]))
    require(before == bindings(root), "sources changed during verification")
    return seal(dict(schema="p9102-retained-verification-v1", families=list(FAMILIES),
                     state="passed_bounded_pending_acceptance", user_accepted=False,
                     P9_10_2_closed=False, G4_accepted=False, full_GRC9V4_conformance=False,
                     new_support=[], native_steps=0, native_replays=0,
                     execution_mode="retained_equations_and_charge_kernel_checks",
                     environment=dict(python=platform.python_version(), python_flint=flint.__version__,
                                      numpy=numpy.__version__, equation_backend="FLINT_Arb",
                                      charge_backends=["python", "flint"]),
                     workers=workers, predecessor=dict(**reference(root, acceptance_path),
                                                       record_digest=accepted["record_digest"]),
                     source_applicability=applicability, source_refs=before,
                     families_checked=rows, shared_charge_edges=edges,
                     comparison_conventions=dict(
                         identities="exact_canonical_content_and_subject",
                         native_legacy="retained_exact_native_bytes_including_signed_zero",
                         basin="represented_current_flow_and_full_selected_read",
                         numerical="independent_fixed_H_bounds_and_separate_geometry_equation",
                         replay="accepted_exact_observation_or_explicit_state_only_policy",
                         charge="balanced_binary64_tree_then_exact_tolerance_inequality",
                         cross_platform_bitwise_guarantee=False),
                     next_work="Review bounded four-family P9-10.2; then A_OS P9-10.1a-c and P9-10.2. Consolidated P9-10.3-10.6 remain separate."))


def check(root=ROOT):
    value = json.loads((root / PATH).read_bytes())
    require(value == seal(value) and value["schema"] == "p9102-retained-verification-v1",
            "P9-10.2 record identity")
    require(value["families"] == list(FAMILIES)
            and [r["family"] for r in value["families_checked"]] == list(FAMILIES)
            and value["state"] == "passed_bounded_pending_acceptance"
            and all(value[k] is False for k in ("user_accepted", "P9_10_2_closed", "G4_accepted",
                                                "full_GRC9V4_conformance"))
            and value["new_support"] == []
            and value["native_steps"] == value["native_replays"] == 0,
            "P9-10.2 scope or acceptance changed")
    require(value["source_refs"] == bindings(root), "P9-10.2 source drift")
    for ref in [value["predecessor"], *[r[k] for r in value["families_checked"]
                                       for k in ("execution_ref", "exact_target_ref")]]:
        require(reference(root, ref["path"])["sha256"] == ref["sha256"], "P9-10.2 input drift")
    require(all(r["outcome"] == "passed_bounded_retained_verification"
                and len(r["versions"]) == 2 and len(r["independent_charge_checks"]) == 4
                and r["independent_equations_recomputed"] == 4
                and r["native_steps"] == r["native_replays"] == 0
                and r["exact_CI_root_signs_claimed"] is False for r in value["families_checked"]),
            "P9-10.2 family coverage")
    require(value["shared_charge_edges"]["evaluations"] == 24, "P9-10.2 charge coverage")
    with no_native_runs():
        for row in value["families_checked"]:
            require(row == family_check(root, row["family"], equations=False),
                    "P9-10.2 retained result drift")
    for row in value["shared_charge_edges"]["cases"]:
        expected = charge_expected(tuple(map(float.fromhex, row["C"])),
                                   float.fromhex(row["target"]), float.fromhex(row["absolute"]),
                                   float.fromhex(row["relative"]))
        require(row["python"] == row["flint"] == expected, "P9-10.2 charge edge result drift")
    return value


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--run", action="store_true")
    modes.add_argument("--check", action="store_true")
    parser.add_argument("--workers", type=int, choices=range(1, 5), default=4)
    args = parser.parse_args()
    if args.run:
        require(not (ROOT / PATH).exists(), "refuse to overwrite retained verification")
        value = run(workers=args.workers)
        with (ROOT / PATH).open("x") as stream:
            json.dump(value, stream, indent=2, ensure_ascii=False)
            stream.write("\n")
    else:
        value = check()
    print(json.dumps(dict(state=value["state"], families=value["families"],
                          native_steps=value["native_steps"], native_replays=value["native_replays"],
                          record_digest=value["record_digest"])))
