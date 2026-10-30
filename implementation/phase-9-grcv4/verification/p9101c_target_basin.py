"""Focused exact-v2-target basin checks. --check rechecks saved equations, not native trajectories."""

from p9_aos_historical import references_match

import argparse
from copy import deepcopy
from fractions import Fraction as Q
import json
import lzma
from pathlib import Path
import platform
import time
from types import SimpleNamespace as NS
from unittest.mock import patch

import p9101a_basin_oracle as oracle
import p9101a_basin_pressure as pressure
import p9101b_target_compatibility as predecessor

ROOT, BASE, FAMILIES = predecessor.ROOT, predecessor.BASE, predecessor.FAMILIES
LABELS = ("after_basin_policy_migration", "after_disabled_return")
SELF = "implementation/phase-9-grcv4/verification/p9101c_target_basin.py"
TEST = "implementation/phase-9-grcv4/verification/test_p9101c_target_basin.py"
require = oracle.require


def references(root):
    refs = {
        r["path"]: r for r in pressure.references(root) + predecessor.references(root)
    }
    for name in (SELF, TEST):
        refs[name] = dict(path=name, sha256=predecessor.sha((root / name).read_bytes()))
    for family in FAMILIES:
        _, ref = predecessor.load(root, family)
        refs[ref["path"]] = dict(path=ref["path"], sha256=ref["sha256"])
    return [refs[k] for k in sorted(refs)]


def restore_state(payload, family):
    from pygrc.models import grc_9_v4_lifecycle as lifecycle
    from pygrc.models.grc_v4_geometry import GeometryStageInputs

    cls = getattr(
        lifecycle,
        dict(
            C_OS="GRC9V4COSState",
            C_CI="GRC9V4CCIState",
            A_CI="GRC9V4ACIState",
            A_PC="GRC9V4APCState",
            A_OS="GRC9V4AOSState",
            C_PC="GRC9V4CPCState",
        )[family],
    )
    return cls(
        GeometryStageInputs.from_payload(payload["inputs"]),
        lifecycle.GRC9V4Specialization(**payload["specialization"]),
    )


def assumptions(saved, role):
    """Supplement the original oracle's dynamic gap/floor/regularity checks."""
    ref = saved.inputs.geometry.reference
    p = ref.profile.params_resolved.to_payload()
    graph = ref.graph.port_graph
    authority = getattr(saved.inputs, role)
    require(
        saved.inputs.context.contract_id == "constant_zero_context_v1"
        and saved.inputs.context.value.to_dict() == {},
        "oracle zero context",
    )
    require(ref.context == saved.inputs.context, "oracle reference context")
    common = p["common"]
    require(
        all(
            common[k] == v
            for k, v in dict(
                boundary_policy_id="closed_no_flux_v1",
                measure_profile_id="unit_vertex_measure_v1",
                normalization_id="unnormalized_vertex_stiffness_v1",
                differential_backend_id="oriented_incidence_d0_equals_BT_v1",
                gauge_id="component_zero_mean_potential_v1",
            ).items()
        ),
        "oracle common law",
    )
    gp = p["geometry"]
    require(
        gp["star_cover_id"] == "vertex_star_exact_overlap_v1"
        and gp["overlap_normalization_id"] == "edge_multiplicity_inverse_sqrt_v1",
        "oracle star mask",
    )
    require(
        all(v == 1 for v in ref.edge_weights.values())
        and all(v == 0 for row in ref.K4_base for v in row),
        "oracle reference/base",
    )
    require(
        len(graph.live_node_ids) == 17
        and len(graph.edges) == 16
        and all(e.tail.node_id != e.head.node_id for e in graph.edges),
        "oracle target graph",
    )
    require(all(x >= 0 for x in authority.C), "oracle nonnegative resources")
    cp = p["candidate"]
    candidate = ref.profile.identity_payload.candidate
    if candidate == "C":
        require(
            cp["potential_evaluator_id"]
            == "quadratic_site_potential_zero_derivative_v1"
            and cp["transport_id"] == "C-HM-STIFFNESS-BASELINE-v1"
            and cp["E_H_policy_id"] == "diag_W_C_tr_structural_hodge_v1"
            and cp["E_M_policy_id"] == "eta_C_diag_W_C_tr_mobility_v1"
            and set(cp["W_C_tr"]) == {e.edge_id for e in graph.edges}
            and all(v == 1 for v in cp["W_C_tr"].values()),
            "oracle C transport",
        )
    else:
        require(
            cp["site_potential_id"] == "quadratic_site_potential_zero_derivative_v1"
            and cp["conductance_evaluator_id"] == "curvature_disabled_G_W_v1"
            and all(w > 0 for w in authority.W_A),
            "oracle A conductance",
        )
    return dict(
        context="constant_zero",
        reference_hodge="identity",
        K4_base="zero",
        geometry="vertex_star_exact_overlap",
        graph_vertices=17,
        graph_edges=16,
        candidate=candidate,
        dynamic_checks="original oracle: parameters, selector gap, inactive floor, current regularity, H equation",
    )


def capture(model, label):
    from pygrc.models import grc_9_v4_basin as basin
    from test_p9101a_basin_pressure import saved_state

    saved = saved_state(model)
    before = deepcopy(saved.to_payload())
    lifecycle = model.lifecycle_digest
    checks = {role: assumptions(saved, role) for role in ("current", "reset")}
    reads = []
    native = basin._read_once

    def spy(inputs, backend):
        r, p = native(inputs, backend)
        reads.append((r, p))
        return r, p

    with patch.object(basin, "_read_once", side_effect=spy):
        snapshot = model.snapshot()
    require(len(reads) == 2, "exactly two independently read roles")
    require(snapshot["owner"]["state"] == before, "saved snapshot authority")
    extension = snapshot["owner"]["basin"]
    roots, equations, mechanisms = {}, {}, {}
    real = saved.inputs.geometry.reference.profile.identity_payload.realization
    for role, (read, point) in zip(("current", "reset"), reads, strict=True):
        oracle.captured_inputs(
            saved, role, extension[role + "_observation"], read, point
        )
        roots[role] = oracle.root_payload(read, point)[0]
        if real == "OS":
            require(
                point.inputs.geometry == saved.inputs.geometry.reference.geometry(),
                "OS fresh reference-geometry restart",
            )
            mechanisms[role] = "fresh_reference_geometry_restart"
        elif real == "CI":
            require(
                read.selected.point is point and read.selected.inputs == point.inputs,
                "complete joint selected root",
            )
            mechanisms[role] = "full_J_H_root_domain_certificate_bound"
        else:
            require(
                read.inputs.current.Z_4 == getattr(saved.inputs, role).Z_4,
                "PC committed carrier consumption",
            )
            mechanisms[role] = "committed_W_Z_and_carrier_geometry_equation"
        equations[role] = oracle.equation_check(saved, role, point)
    require(
        model._operation._published.owner.state.to_payload() == before
        and model.lifecycle_digest == lifecycle,
        "observation changed authority/lifecycle",
    )
    return dict(
        label=label,
        fixture_identity=oracle.digest(before),
        saved_native_state=before,
        observations=extension,
        selected_roots=roots,
        role_equations=equations,
        oracle_assumptions=checks,
        realization_checks=mechanisms,
        expected_classification={
            role: oracle.classification(
                extension[role + "_observation"]["witness"],
                extension[role + "_observation"]["binding"]["graph_digest"],
            )
            for role in ("current", "reset")
        },
    )


def run(root, family):
    import flint
    from pygrc.models import GRC9V4
    from test_p9101b_target_compatibility import target, subject, request

    refs = references(root)
    accepted, accepted_ref = predecessor.load(root, family)
    old = accepted["evidence"]["v2"]
    start = time.monotonic()
    model = GRC9V4.from_config(
        dict(
            initial=target(family),
            exact_backend="flint",
            numerical_policy="legacy_exact_v1",
        )
    )
    receipt = model.migrate_basin_policy("target-basin-opt-in")
    require(receipt.committed, "basin migration rejected")
    require(subject(model) == old["subject"], "exact accepted v2 target")
    cfg = model.configuration
    cases = [capture(model, LABELS[0])]
    require(
        model.migrate_branch(request(model, "disable")).committed, "disable rejected"
    )
    for op in ("step", "reset", "step"):
        getattr(model, op)()
    require(
        model.migrate_branch(request(model, "enable", cfg.reference)).committed,
        "return rejected",
    )
    require(subject(model) == old["subject"], "return target changed")
    returned = model.configuration
    require(returned.current.C != returned.reset.C, "return lost distinct resources")
    for role in ("current", "reset"):
        require(
            model._operation._published.owner.state.inputs.to_payload()[role]
            == old["returned_roles"][role],
            "returned C/W/Z differs from accepted target campaign",
        )
    if family.startswith("A_"):
        require(
            returned.current.W_A != returned.reset.W_A,
            "return lost distinct A histories",
        )
    if family in ("A_PC", "C_PC"):
        require(
            all(
                any(getattr(cfg, r).Z_4) and not any(getattr(returned, r).Z_4)
                for r in ("current", "reset")
            ),
            "declared carrier loss/zero initialization",
        )
    cases.append(capture(model, LABELS[1]))
    require(refs == references(root), "sources changed during execution")
    value = dict(
        schema="p9101c-exact-target-basin-v1",
        family=family,
        status="passed_bounded_exact_target_check",
        subject=subject(model),
        predecessor=accepted_ref,
        observations=cases,
        native_boundaries=2,
        native_role_captures=4,
        native_expansion_events=0,
        disabled_steps=2,
        new_enabled_steps=0,
        distinct_return_resources=True,
        distinct_return_W_A=family.startswith("A_"),
        return_carrier="explicit_loss_and_zero" if family in ("A_PC", "C_PC") else "absent",
        exact_root_signs_claimed=False,
        new_support=[],
        user_accepted=False,
        source_refs=refs,
        python_version=platform.python_version(),
        python_flint_version=flint.__version__,
        exact_backend="flint",
        numerical_policy="legacy_exact_v1",
        elapsed_seconds=round(time.monotonic() - start, 3),
    )
    return predecessor.seal(json.loads(json.dumps(value, allow_nan=False)))


def stem(family):
    require(family in FAMILIES, "unselected family")
    return BASE + "P9-10.1c-ExactTargetBasin-" + family + ".json"


def load(root, family):
    paths = [root / stem(family), root / (stem(family) + ".xz")]
    paths = [p for p in paths if p.exists()]
    require(len(paths) == 1, "exactly one target basin record required")
    p = paths[0]
    raw = p.read_bytes()
    value = json.loads(lzma.decompress(raw) if p.suffix == ".xz" else raw)
    return value, dict(
        path=p.relative_to(root).as_posix(),
        sha256=predecessor.sha(raw),
        record_digest=value["record_digest"],
        family=family,
    )


def validate(value, old, *, equations=False):
    """Retained bindings/classification; optional independent equations, never native replay."""
    family = value["family"]
    require(
        value == predecessor.seal(value)
        and value["schema"] == "p9101c-exact-target-basin-v1"
        and value["status"] == "passed_bounded_exact_target_check"
        and value["subject"] == old["subject"]
        and value["user_accepted"] is False
        and value["exact_root_signs_claimed"] is False
        and value["new_support"] == []
        and value["native_boundaries"] == 2
        and value["native_role_captures"] == 4
        and value["native_expansion_events"] == value["new_enabled_steps"] == 0
        and value["disabled_steps"] == 2
        and value["exact_backend"] == "flint"
        and value["numerical_policy"] == "legacy_exact_v1",
        "target basin identity/scope drift",
    )
    require(
        tuple(c["label"] for c in value["observations"]) == LABELS, "missing boundary"
    )
    from p9101c_support_reconciliation import basin_subject

    for case in value["observations"]:
        state = case["saved_native_state"]
        require(case["fixture_identity"] == oracle.digest(state), "saved state drift")
        require(
            basin_subject(state, case["observations"])["subject"] == value["subject"],
            "wrong exact target",
        )
        saved = restore_state(state, family)
        require(saved.to_payload() == state, "state reconstruction mismatch")
        if case["label"] == LABELS[0]:
            from test_p9101b_target_compatibility import target

            for role in ("current", "reset"):
                require(
                    state["inputs"][role] == target(family)["inputs"][role],
                    "migration changed C/W/Z",
                )
        else:
            require(
                state["inputs"]["current"]["C"] != state["inputs"]["reset"]["C"],
                "return resources collapsed",
            )
            for role in ("current", "reset"):
                require(
                    state["inputs"][role] == old["returned_roles"][role],
                    "wrong return boundary",
                )
        for role in ("current", "reset"):
            observed = case["observations"][role + "_observation"]
            selected = case["selected_roots"][role]
            require(
                case["oracle_assumptions"][role] == assumptions(saved, role),
                "oracle assumptions changed",
            )
            require(
                observed["binding"]["read_identity"]
                == "grc9v4-basin-read-sha256:" + oracle.digest(selected),
                "full selected read drift",
            )
            recipe_inputs = selected["recipe"]["inputs"]
            require(
                recipe_inputs["reference"] == state["inputs"]["reference"]
                and recipe_inputs["current"] == state["inputs"][role]
                and recipe_inputs["context"] == state["inputs"]["context"]
                and recipe_inputs["dt"] == 0
                and recipe_inputs["stage"]
                == ("pc_old_history" if family in ("A_PC", "C_PC") else "pre_read"),
                "selected recipe input drift",
            )
            h = [[float.fromhex(x) for x in r] for r in selected["H1_form"]]
            if family.endswith("CI"):
                require(
                    selected["selected_inputs"]["H1_form"] == h
                    and selected["selected_inputs"]["current"] == state["inputs"][role]
                    and observed["binding"]["root_certificate_binding"]
                    == "grc9v4-basin-joint-root-sha256:" + oracle.digest(selected),
                    "joint geometry/certificate drift",
                )
            else:
                require(recipe_inputs["H1_form"] == h, "selected geometry drift")
                expected = (
                    "grc9v4-basin-pc-read-sha256:" + oracle.digest(selected)
                    if family in ("A_PC", "C_PC")
                    else None
                )
                require(
                    observed["binding"]["root_certificate_binding"] == expected,
                    "read certificate drift",
                )
            values = tuple(map(float.fromhex, selected["current"]))
            require(
                [e["current"] for e in observed["witness"]["edges"]]
                == selected["current"]
                and oracle.row_witness(saved, role, values)
                == observed["witness"]["rows"],
                "saved rows/current mismatch",
            )
            oracle.compare_classification(observed)
            require(
                case["expected_classification"][role]
                == oracle.classification(
                    observed["witness"], observed["binding"]["graph_digest"]
                ),
                "expected classification drift",
            )
            eq = case["role_equations"][role]
            require(
                eq["exact_root_signs_claimed"] is False
                and Q(eq["current_error_upper"]) < Q(1, 2**40),
                "current bound scope",
            )
            if equations:
                point = NS(
                    current=NS(values=values),
                    inputs=NS(
                        geometry=NS(
                            one_form_hodge=NS(
                                matrix=tuple(
                                    tuple(map(float.fromhex, r))
                                    for r in selected["H1_form"]
                                )
                            )
                        )
                    ),
                )
                require(
                    oracle.equation_check(saved, role, point) == eq,
                    "saved independent equation drift",
                )
    return value


def check(root=ROOT, family="C_OS", *, equations=False):
    root = Path(root)
    value, ref = load(root, family)
    old, old_ref = predecessor.load(root, family)
    require(
        references_match(root, value["source_refs"], references(root)) and value["predecessor"] == old_ref,
        "target basin execution/source drift",
    )
    return validate(value, old["evidence"]["v2"], equations=equations), ref


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--family", choices=FAMILIES, required=True)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--run", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.run:
        path = ROOT / stem(args.family)
        require(
            not path.exists() and not Path(str(path) + ".xz").exists(),
            "existing evidence preserved",
        )
        value = run(ROOT, args.family)
        raw = (json.dumps(value, indent=2) + "\n").encode()
        if len(raw) > 1_000_000:
            path = Path(str(path) + ".xz")
            raw = lzma.compress(raw)
        with path.open("xb") as f:
            f.write(raw)
        print(
            json.dumps(
                dict(
                    family=args.family,
                    path=path.name,
                    bytes=len(raw),
                    elapsed_seconds=value["elapsed_seconds"],
                )
            )
        )
    else:
        value, ref = check(family=args.family, equations=True)
        print(
            json.dumps(
                dict(
                    **ref,
                    check_mode="saved_equations_rows_classification_not_native_rerun",
                )
            )
        )
