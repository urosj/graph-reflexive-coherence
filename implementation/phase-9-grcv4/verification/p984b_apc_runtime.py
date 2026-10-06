"""Sixteen native A_PC companions: independent fixed-row equations and W/Z lifecycle.

Reuses the accepted R=2048 native declaration, with bounded all-layout proofs.
Execution, retained checks and user acceptance remain separate.
"""

import argparse
import json
import platform
import time
from copy import deepcopy
from dataclasses import replace
from decimal import Decimal, localcontext
from fractions import Fraction as Q
from importlib.metadata import version
from unittest.mock import patch

import numpy as np
import p984b_runtime as b
import verify_p983a_apc_oracle as oracle
from p984b_cci_runtime import represented_continuity
from test_p980_os_effect_witness import (
    IV,
    IntervalRows,
    full_error,
    inverse,
    number,
    separation,
    vector,
)

from pygrc.models import grc_9_v4_lifecycle as native
from pygrc.models import grc_v4_candidate_a as candidate
from pygrc.models import grc_v4_pc as pc
from pygrc.models.grc_9_v4_topology import GRC9V4CandidateADifferentialReference
from pygrc.models.grc_v4_pc import CandidatePCRead, ProvisionalCandidatePCStep
from tests.models.test_grc_9_v4_apc import ORACLE_SHA, authority, fixture

SELF = b.HERE + "p984b_apc_runtime.py"
TEST = b.HERE + "test_p984b_apc_runtime.py"
INPUTS = b.BASE + "P9-8.4b-APCCases.json"
RESULTS = b.BASE + "P9-8.4b-APCResults.json"
REVIEW = b.BASE + "P9-8.4b-APCRuntimeReview.md"
PREDECESSOR = b.BASE + "P9-8.3A.2-APC-Validation.json"
RECIPE = "pc_exact_input_enclosed_scalar_zoh_binary64_v1"
ROLES = ("current", "reset")
LIMITS = {
    "geometry_error": Q(1, 2**48),
    "current_error": Q(1, 2**40),
    "source_error": Q(1, 2**56),
    "resource_error": Q(1, 2**40),
    "carrier_error": Q(1, 2**40),
    "history_error": Q(1, 2**48),
    "readback_error": Q(1, 2**40),
    "flat_error": Q(1, 2**40),
}


def predecessor():
    b.require(
        b.sha((b.ROOT / oracle.RECORD).read_bytes()) == ORACLE_SHA,
        "accepted A_PC oracle changed",
    )
    old = b.read(oracle.RECORD)
    b.check_digest(old)
    b.require(
        b.read(PREDECESSOR)["acceptance"]["status"] == "accepted_by_user",
        "native A_PC predecessor not accepted",
    )
    return old


def backend(before):
    return GRC9V4CandidateADifferentialReference(
        before.geometry.reference.graph.port_graph
    )


def state(payload):
    spec = payload["specialization"]
    return native.GRC9V4APCState(
        b.GeometryStageInputs.from_payload(payload["inputs"]),
        native.GRC9V4Specialization(
            b.FrozenJSONMap(spec["resolved"]), b.FrozenJSONMap(spec["identity_payload"])
        ),
    )


def geometry(before, authority):
    """Independent represented affine H; no production carrier builder."""
    ref = before.geometry.reference
    m = len(ref.graph.live_edge_ids)
    b.require(
        authority.Z_4 is not None and len(authority.Z_4) == m * m,
        "whole carrier required",
    )
    h = tuple(
        tuple(
            float(
                Q(int(i == j))
                + Q(ref.profile.params_resolved.geometry.kappa_H)
                * Q(authority.Z_4[i * m + j])
            )
            for j in range(m)
        )
        for i in range(m)
    )
    return b.GRCV4Geometry(ref, b.OneFormHodge(ref.graph, h))


def role_input(before, role, **changes):
    authority = getattr(before, role)
    return replace(
        before, current=authority, geometry=geometry(before, authority), **changes
    )


def bind_case(seed, case):
    """Fresh actual-state identities; frozen expected port graph supplies topology."""
    case = deepcopy(case)
    request = case["request"]
    request.update(
        source_state_digest=seed.scientific_digest,
        history_policy=oracle.history_policy(
            b.authority_payload(seed.inputs.current),
            b.authority_payload(seed.inputs.reset),
        ),
        expected_event_id=None,
        expected_target_graph_digest=None,
    )
    vector = next(
        v
        for v in b.read(b.VECTORS)["grc9_expansion_vectors"]
        if v["fixture_id"] == case["fixture_id"]
    )
    identity = deepcopy(predecessor()["event_identity_payload"])
    for key in identity:
        if key in request and key != "schema_version":
            identity[key] = request[key]
    identity["canonical_module_node_count"] = vector["event_identity_payload"][
        "canonical_module_node_count"
    ]
    for channel in ("candidate", "carrier"):
        key = channel + "_history_policy_digest"
        identity[key] = request["history_policy"][key]
    event = oracle.common.payload_identity("expansion_event_identity_payload", identity)
    graph = deepcopy(vector["expected"]["identity_payloads"]["target_graph"])
    old_event = vector["expected"]["event_id"]

    def rename(value):
        return (
            event + value[len(old_event) :]
            if value.startswith(old_event + "/")
            else value
        )

    graph["live_node_ids"] = sorted(map(rename, graph["live_node_ids"]))
    for edge in graph["edges"]:
        edge["edge_id"] = rename(edge["edge_id"])
        for end in ("tail", "head"):
            edge[end]["node_id"] = rename(edge[end]["node_id"])
    graph["edges"].sort(key=lambda e: e["edge_id"])
    case["oracle"] = {
        "event_id": event,
        "event_identity": identity,
        "target_graph": graph,
    }
    return case


def make_manifest():
    old = predecessor()
    seed, _ = fixture(old)
    initial = replace(
        seed.inputs,
        current=authority(old["initial"]["current"]),
        reset=authority(old["initial"]["reset"]),
        step_index=0,
        time=0,
        dt=b.DT,
    )
    initial = replace(initial, geometry=geometry(initial, initial.current))
    coverage = b.read(b.COVERAGE)
    b.check_digest(coverage)
    wanted = {
        r["fixture_id"]
        for r in coverage["coverage_cells"]
        if r["owner"] == "P9-8.4b" and r["family"] == "A_PC" and r["applicable"]
    }
    cases = []
    for v in b.read(b.VECTORS)["grc9_expansion_vectors"]:
        if v["fixture_id"] not in wanted:
            continue
        request = deepcopy(old["request"])
        request.update(
            {
                k: v["request"][k]
                for k in ("target_effective_degree", "module_chirality", "growth_phase")
            }
        )
        request["operation_id"] = "p984b-apc-" + v["fixture_id"]
        cases.append(
            bind_case(
                seed,
                {
                    "case_id": "P984B-APC-" + v["fixture_id"],
                    "fixture_id": v["fixture_id"],
                    "family": "A_PC",
                    "subject_kind": "native_companion",
                    "request": request,
                    "coverage_binding": {
                        "record_digest": coverage["record_digest"],
                        "cell_ids": [v["fixture_id"] + "::A_PC::" + r for r in ROLES],
                    },
                    "schedule": {
                        "source_current_beats": 1,
                        "source_reset_beats": 0,
                        "target_beats_per_role": 10,
                        "dt": b.DT,
                        "final_read": True,
                    },
                    "execution_budget_seconds": 600,
                    "comparison": {
                        "kind": "pointwise_full_formula_interval_and_native_whole_base_chart_carrier_ball",
                        "budgets": {k: str(v) for k, v in LIMITS.items()},
                        "native_radius": "2048",
                        "numerical_recipe": RECIPE,
                        "accumulated_trajectory_error_bound": False,
                        "uniform_parameter_tube": False,
                    },
                },
            )
        )
    b.require(len(cases) == 16, "all sixteen A_PC layouts required")
    for case in cases:
        case["independent_whole_chart"] = oracle.whole_chart(
            case["oracle"]["target_graph"]
        )

    paths = [
        *oracle.SOURCES,
        SELF,
        TEST,
        b.SELF,
        b.HERE + "p984b_cci_runtime.py",
        PREDECESSOR,
        oracle.RECORD,
        b.BASE + "P9-8.3A.1-APC-Acceptance.json",
        b.BASE + "P9-8.3A.2-APC-RuntimeReview.md",
        b.COVERAGE,
        b.VECTORS,
        coverage["scientific_claim_mapping"]["paper"]["path"],
        coverage["scientific_claim_mapping"]["side_tool_source"],
        "implementation/investigations/grc9v4-constitutive-design/decisions/D10NormativeClaimTopology.json",
        "pyproject.toml",
        "uv.lock",
    ]
    paths += [
        str(p.relative_to(b.ROOT))
        for pattern in (
            "src/pygrc/models/grc*v4*.py",
            "src/pygrc/models/grc_v4_assets/*.json",
            "tests/models/test_grc*v4*.py",
            b.HERE + "test_p980*.py",
            b.HERE + "verify_p983a_*oracle.py",
        )
        for p in b.ROOT.glob(pattern)
    ]
    return b.seal(
        {
            "schema": "p984b-apc-case-manifest-v1",
            "family": "A_PC",
            "initial_inputs": initial.to_payload(),
            "nominal_source": seed.to_payload(),
            "cases": cases,
            "source_bindings": b.bind(paths),
            "claim_traces": old["side_tool_provenance"],
            "independent_source_chart": oracle.whole_chart(
                seed.inputs.geometry.reference.graph.port_graph.to_payload()
            ),
            "scientific_contracts": {
                "paper": ["10.5 PC", "C.9 A-PC", "E.10 whole lifecycle"],
                "expansion_claims": coverage["scientific_claim_mapping"],
                "claim_restrictions": {
                    "D10-CL-O-006": "scalar_ZOH_PC_only",
                    "D10-CL-C-004": "no_endpoint_hysteresis_inferred",
                    "D10-CL-C-012": "no_universal_realization_or_graph_support",
                },
            },
            "source_rule": "one actual source beat; recompute event/history identities, never substitute nominal state",
            "resource_recipe": "accepted [1/4,3/8,3/8] shares on every layout, independently checked",
            "user_accepted": False,
            "aggregate_closed": False,
        }
    )


def check_manifest(value):
    b.check_digest(value)
    b.check_bindings(value["source_bindings"])
    b.require(value == make_manifest(), "A_PC manifest/case/budget drift")


def charge_record(inputs, authority):
    actual = oracle.adjacent_charge(authority.C)
    delta = Q(actual) - Q(inputs.Q_target)
    policy = inputs.geometry.reference.profile.params_resolved.charge
    bound = Q(policy.absolute_tolerance) + Q(policy.relative_tolerance) * max(
        abs(Q(inputs.Q_target)), 1
    )
    b.require(
        min(authority.C) >= 0 and abs(delta) <= bound,
        "declared charge admission failed",
    )
    return {
        "actual": actual,
        "target": inputs.Q_target,
        "residual": str(delta),
        "bound": str(bound),
        "represented_sum": str(sum(map(Q, authority.C))),
    }


def independent_target(seed, case):
    ref = oracle.reference(case["oracle"]["target_graph"])
    source = seed.inputs.geometry.reference.graph
    event = case["oracle"]["event_id"]
    shares = {
        event + f"/satellite/{i}": Q(s)
        for i, s in enumerate(case["request"]["resource_distribution"], 1)
    }
    roles = {}
    for role in ROLES:
        old = getattr(seed.inputs, role)
        c = dict(zip(source.live_node_ids, old.C, strict=True))
        w = dict(zip(source.live_edge_ids, old.W_A, strict=True))
        roles[role] = b.GRCV4AuthoritativeState(
            tuple(
                c[n]
                if n in c
                else float(Q(c[case["request"]["source_node_id"]]) * shares.get(n, 0))
                for n in ref.graph.live_node_ids
            ),
            tuple(
                w.get(e, seed.specialization.resolved["expansion"]["bond_seed"])
                for e in ref.graph.live_edge_ids
            ),
            (0.0,) * len(ref.graph.live_edge_ids) ** 2,
        )
        b.require(
            sum(shares.values()) == 1 and bool(charge_record(seed.inputs, roles[role])),
            "resource simplex/represented charge drift",
        )
    return replace(
        seed,
        inputs=replace(
            seed.inputs,
            geometry=ref.geometry(),
            **roles,
            operation_id=case["request"]["operation_id"],
            dt=0,
        ),
    )


def independent_model(before):
    b.require(
        before.geometry.reference.to_payload()
        == oracle.reference(
            before.geometry.reference.graph.port_graph.to_payload()
        ).to_payload(),
        "independent A_PC declaration drift",
    )
    return oracle.model_for(before.geometry.reference.graph.port_graph.to_payload())


def truth(before):
    high = IntervalRows(independent_model(before))
    m = len(before.current.W_A)
    z = IV.matrix(np.array(before.current.Z_4).reshape(m, m).tolist())
    h = high.I + number(oracle.KAPPA_H) * z
    c, w = vector(before.current.C), vector(before.current.W_A)
    read = high.read("A", c, w, h)
    drive = high.conductance(c, w, read["baseline"])
    readback = IV.matrix(
        [
            number(Q(1, 16)) * (x - g) / (x + g) * j
            for x, g, j in zip(w, drive, read["J"], strict=True)
        ]
    )
    flat = inverse(h) * readback
    return {
        "high": high,
        "c": c,
        "w": w,
        "z": z,
        "H": h,
        "read": read,
        "readback": readback,
        "flat": flat,
    }


def independent_certificate(before, value):
    exact = truth(before)
    matrix_error = lambda a, h: full_error(np.asarray(a).ravel(), IV.matrix(list(h)))
    errors = {
        "geometry_error": matrix_error(value["H"], exact["H"]),
        "current_error": max(
            full_error(value["J"], exact["read"]["J"]),
            full_error(value["baseline"], exact["read"]["baseline"]),
        ),
        "source_error": matrix_error(value["source"], exact["read"]["source"]),
        "readback_error": full_error(value["readback"], exact["readback"]),
        "flat_error": full_error(value["flat"], exact["flat"]),
    }
    return {
        "input_identity": before.identity,
        "selected_read_digest": value["record_digest"],
        "bounds": {k: str(v) for k, v in errors.items()},
    }


def certified_read(read):
    point = read.point
    value = b.seal(
        {
            "input_identity": read.inputs.identity,
            "selected_inputs_identity": point.inputs.identity,
            "point_identity": point.identity,
            "read_source": point.read.source_identity,
            "read_current": list(point.read.current.values),
            "J": list(point.current.values),
            "H": [list(r) for r in point.inputs.geometry.one_form_hodge.matrix],
            "baseline": list(point.baseline.values),
            "readback": list(point.read.flux.values),
            "flat": list(point.read.causal_flat.values),
            "source": [list(r) for r in read.structural_source.increment],
            "bounds": dict(read.certificate.bounds),
        }
    )
    value["independent_certificate"] = independent_certificate(read.inputs, value)
    check_read(read.inputs, value)
    return value


def check_read(before, value, *, numerics=False):
    raw = {k: v for k, v in value.items() if k != "independent_certificate"}
    b.check_digest(raw)
    b.require(
        value["input_identity"] == before.identity
        and value["selected_inputs_identity"]
        == replace(before, stage="pc_old_history").identity,
        "old-carrier read operand drift",
    )
    b.require(
        value["H"]
        == [list(r) for r in geometry(before, before.current).one_form_hodge.matrix],
        "geometry does not read the whole old carrier",
    )
    b.require(
        value["read_current"] == value["J"]
        and value["read_source"] == value["point_identity"],
        "Read-Back current binding drift",
    )
    model = independent_model(before)
    flat = value["flat"]
    zeta = Q(before.geometry.reference.profile.params_resolved.candidate.zeta_A)
    source = [
        [
            float(zeta * Q(float(Q(float(model.mask[i, j])) * Q(x) * Q(y))))
            for j, y in enumerate(flat)
        ]
        for i, x in enumerate(flat)
    ]
    b.require(source == value["source"], "same-read staged structural source drift")
    bounds = value["bounds"]
    b.require(
        Q(bounds["geometry_radius"]) == Q(1, 8)
        and Q(bounds["carrier_radius"]) == 2048
        and Q(bounds["hodge_lower"]) == Q(7, 8)
        and 0 <= Q(bounds["source_norm_upper"]) <= 2048,
        "whole-chart admission drift",
    )
    cert = value["independent_certificate"]
    b.require(
        cert["input_identity"] == before.identity
        and cert["selected_read_digest"] == value["record_digest"],
        "certificate binding drift",
    )
    for k in (
        "geometry_error",
        "current_error",
        "source_error",
        "readback_error",
        "flat_error",
    ):
        b.require(
            0 <= Q(cert["bounds"][k]) < LIMITS[k], "full formula error budget: " + k
        )
    if numerics:
        b.require(
            cert == independent_certificate(before, raw), "interval certificate drift"
        )


def held_write(z, source, dt, tau):
    """Separate 150-digit scalar ODE solution; never native scalar_zoh."""
    with localcontext() as context:
        context.prec = 150
        a = (-Decimal.from_float(float(dt)) / Decimal.from_float(float(tau))).exp()
        return tuple(
            float(
                a * Decimal.from_float(float(x))
                + (1 - a) * Decimal.from_float(float(s))
            )
            for x, s in zip(z, source, strict=True)
        )


def step_errors(before, after):
    exact = truth(before)
    a = IV.exp(-number(before.dt))
    carrier = a * exact["z"] + (1 - a) * exact["read"]["source"]
    resource = exact["c"] - number(before.dt) * exact["high"].B * exact["read"]["J"]
    history = exact["high"].write(resource, exact["w"], exact["read"]["J"])
    return {
        "resource_error": str(full_error(after.current.C, resource)),
        "carrier_error": str(full_error(after.current.Z_4, IV.matrix(list(carrier)))),
        "history_error": str(full_error(after.current.W_A, history)),
    }


def perform_step(before):
    calls, targets, writes = [], [], []
    original, original_target, original_write = (
        pc.scalar_zoh,
        candidate.candidate_a_writer_target,
        candidate.candidate_a_log_interpolation,
    )

    def observed(z, source, dt, tau):
        calls.append({"Z": list(z), "source": list(source), "dt": dt, "tau": tau})
        return original(z, source, dt, tau)

    def target(point, c):
        result = original_target(point, c)
        targets.append(
            {
                "point_identity": point.identity,
                "C": list(c.values),
                "W_A": list(point.inputs.current.W_A),
                "J": list(point.current.values),
                "target": list(result[1]),
            }
        )
        return result

    def write(old, drive, dt, tau):
        result = original_write(old, drive, dt, tau)
        writes.append(
            {
                "old": list(old),
                "target": list(drive),
                "dt": dt,
                "tau": tau,
                "result": list(result),
            }
        )
        return result

    with (
        patch.object(pc, "scalar_zoh", observed),
        patch.object(candidate, "candidate_a_writer_target", target),
        patch.object(candidate, "candidate_a_log_interpolation", write),
    ):
        step = ProvisionalCandidatePCStep(before, backend(before))
    value = {
        "read": certified_read(step.read),
        "reset_read": certified_read(step.reset_read),
        "restart": certified_read(step.restart),
        "poststate": step.next_inputs.to_payload(),
        "selection_current": list(step.resource.selection.current.values),
        "writer_targets": targets,
        "log_writes": writes,
        "carrier_writes": step.carrier_writes,
        "carrier_calls": calls,
        "errors": step_errors(before, step.next_inputs),
    }
    value["writer_certificate"] = writer_certificate(before, value)
    check_step(before, value)
    return step, value


def writer_certificate(before, value):
    high = truth(before)["high"]
    after = b.GeometryStageInputs.from_payload(value["poststate"])
    drive = high.conductance(
        vector(after.current.C), vector(before.current.W_A), vector(value["read"]["J"])
    )
    error = full_error(value["writer_targets"][0]["target"], drive)
    return {
        "input_identity": before.identity,
        "read_digest": value["read"]["record_digest"],
        "poststate_identity": after.identity,
        "targets_digest": b.digest(value["writer_targets"]),
        "error": str(error),
    }


def check_step(before, value, *, numerics=False):
    check_read(before, value["read"], numerics=numerics)
    check_read(role_input(before, "reset"), value["reset_read"], numerics=numerics)
    source = [x for row in value["read"]["source"] for x in row]
    tau = before.geometry.reference.profile.params_resolved.realization.tau_PC
    b.require(
        value["carrier_writes"] == 1
        and value["carrier_calls"]
        == [
            {
                "Z": list(before.current.Z_4),
                "source": source,
                "dt": before.dt,
                "tau": tau,
            }
        ],
        "PC must write the actual old carrier and incoming source exactly once",
    )
    b.require(
        value["selection_current"] == value["read"]["J"],
        "continuity consumed wrong current",
    )
    final = b.GRCV4AuthoritativeState(
        represented_continuity(before, value["read"]["J"]),
        tuple(value["poststate"]["current"]["W_A"]),
        held_write(before.current.Z_4, source, before.dt, tau),
    )
    expected = replace(
        before,
        current=final,
        geometry=geometry(before, final),
        step_index=before.step_index + 1,
        time=float(Q(before.time) + Q(before.dt)),
    )
    b.require(
        expected.to_payload() == value["poststate"], "resource/clock/reset/ZOH drift"
    )
    b.require(before.dt == b.DT, "unexpected timestep")
    b.require(
        len(value["writer_targets"]) == len(value["log_writes"]) == 1,
        "W writer count drift",
    )
    target, write = value["writer_targets"][0], value["log_writes"][0]
    b.require(
        target
        == {
            "point_identity": value["read"]["point_identity"],
            "C": list(final.C),
            "W_A": list(before.current.W_A),
            "J": value["read"]["J"],
            "target": target["target"],
        },
        "W writer operand substitution",
    )
    b.require(
        write
        == {
            "old": list(before.current.W_A),
            "target": target["target"],
            "dt": before.dt,
            "tau": 1,
            "result": list(final.W_A),
        },
        "log writer operand/output drift",
    )
    with localcontext() as context:
        context.prec = 150
        a = (-Decimal.from_float(before.dt)).exp()
        w = [
            float(
                (
                    a * Decimal.from_float(x).ln()
                    + (1 - a) * Decimal.from_float(g).ln()
                ).exp()
            )
            for x, g in zip(before.current.W_A, target["target"], strict=True)
        ]
    b.require(w == list(final.W_A), "represented log interpolation drift")
    cert = value["writer_certificate"]
    b.require(
        cert["input_identity"] == before.identity
        and cert["read_digest"] == value["read"]["record_digest"]
        and cert["poststate_identity"] == expected.identity
        and cert["targets_digest"] == b.digest(value["writer_targets"])
        and 0 <= Q(cert["error"]) < LIMITS["history_error"],
        "W target certificate drift",
    )
    if numerics:
        b.require(cert == writer_certificate(before, value), "W target interval drift")
    for key in ("resource_error", "carrier_error", "history_error"):
        b.require(
            0 <= Q(value["errors"][key]) < LIMITS[key], "full output error: " + key
        )
    check_read(replace(expected, dt=0), value["restart"], numerics=numerics)
    b.require(min(expected.current.C) >= 0, "negative resource continuation")
    if numerics:
        b.require(
            value["errors"] == step_errors(before, expected), "output certificate drift"
        )
    return expected


def run_source(manifest):
    nominal = state(manifest["nominal_source"])
    before = b.GeometryStageInputs.from_payload(manifest["initial_inputs"])
    step, row = perform_step(before)
    after = step.next_inputs
    seed = replace(nominal, inputs=replace(after, dt=0))
    for key, limit in (
        ("C", oracle.RESOURCE_ERROR),
        ("W_A", oracle.HISTORY_ERROR),
        ("Z_4", oracle.CARRIER_ERROR),
    ):
        b.require(
            max(
                abs(Q(x) - Q(y))
                for x, y in zip(
                    getattr(seed.inputs.current, key),
                    getattr(nominal.inputs.current, key),
                    strict=True,
                )
            )
            < limit,
            "source beat differs from accepted nominal comparison",
        )
    return {"source_step": row, "actual_source": seed.to_payload()}, seed


def preflight(target):
    graph = target.inputs.geometry.reference.graph.port_graph.to_payload()
    paper = oracle.PaperAPC(graph)
    oracle.whole_chart(graph)
    rows = {}
    for role in ROLES:
        old = getattr(target.inputs, role)
        c, w, z = old.C, old.W_A, old.Z_4
        trajectory = []
        for i in range(10):
            out = paper.step(c, w, z)
            # Independent interval equations certify every predicted stage before native execution.
            proof = oracle.check_step(graph, c, w, z, out)
            trajectory.append(
                {
                    "index": i + 1,
                    "C": out["C"],
                    "W_A": out["W_A"],
                    "Z": out["Z_4"],
                    "errors": {k: str(v) for k, v in proof["errors"].items()},
                }
            )
            c, w, z = out["C"], out["W_A"], out["Z_4"]
        rows[role] = trajectory
    return rows


def effect_checks(before, value):
    """Read-path controls only: no claim of matched forcing or hysteresis."""
    exact = truth(before)
    results = {}
    for channel in ("geometry", "feedback"):
        control = exact["high"].read(
            "A", exact["c"], exact["w"], exact["H"], **{channel: False}
        )
        nominal = np.array([float(x.mid) for x in control["J"]])
        results[channel] = separation(
            np.array(value["J"]), nominal, exact["read"]["J"], control["J"]
        )
    return results


def writer_effects(before, value):
    """Full composed interval/ULP controls at the actual next-current consumer."""
    exact = truth(before)
    high = exact["high"]
    a = IV.exp(-number(before.dt))
    c = exact["c"] - number(before.dt) * high.B * exact["read"]["J"]
    w = high.write(c, exact["w"], exact["read"]["J"])
    z = a * exact["z"] + (1 - a) * exact["read"]["source"]

    def read(w, z):
        return high.read("A", c, w, high.I + number(oracle.KAPPA_H) * z)["J"]

    nxt = read(w, z)
    final = b.GeometryStageInputs.from_payload(value["poststate"]).current
    out = {}

    def compare(name, observed, truth, control):
        truth, control = IV.matrix(list(truth)), IV.matrix(list(control))
        nominal = np.array([float(x.mid) for x in control])
        out[name] = separation(np.asarray(observed).ravel(), nominal, truth, control)

    compare(
        "written_carrier_next_current",
        value["restart"]["J"],
        nxt,
        read(w, IV.zeros(len(w))),
    )
    wrong_source = high.read("A", c, w, exact["H"])["source"]
    wrong_z = a * exact["z"] + (1 - a) * wrong_source
    compare("same_source_carrier", final.Z_4, z, wrong_z)
    compare("same_source_next_current", value["restart"]["J"], nxt, read(w, wrong_z))
    for name, ci, ji in (
        ("stale_resource_writer", exact["c"], exact["read"]["J"]),
        ("baseline_current_writer", c, exact["read"]["baseline"]),
    ):
        wrong_w = high.write(ci, exact["w"], ji)
        compare(name + "_W", final.W_A, w, wrong_w)
        compare(name + "_next_current", value["restart"]["J"], nxt, read(wrong_w, z))
    compare(
        "next_current_consumes_written_W",
        value["restart"]["J"],
        nxt,
        read(exact["w"], z),
    )
    return out


def event_capture(seed, request):
    owner = native.GRC9V4APCOperation(seed)
    reads, publication, detections, surfaces = [], [], [], []
    initial = json.loads(owner.checkpoint())
    original_step, original_receipts = (
        native.ProvisionalCandidatePCStep,
        native.make_commit_receipts,
    )
    original_detection, original_surface = (
        native.GRC9V4CandidateDetection,
        native.candidate_a_writer_target,
    )

    def observed_step(inputs, *args, **kwargs):
        result = original_step(inputs, *args, **kwargs)
        b.require(
            inputs.dt == 0 and result.next_inputs == inputs and result.writer is None,
            "event performed a physical step/write",
        )
        reads.append(
            {
                "inputs": inputs.to_payload(),
                "read": certified_read(result.read),
                "reset_read": certified_read(result.reset_read),
                "published_state": owner.state.scientific_digest,
            }
        )
        return result

    def observed_surface(point, c):
        result = original_surface(point, c)
        surfaces.append(
            {
                "point_identity": point.identity,
                "C": list(c.values),
                "W_A": list(point.inputs.current.W_A),
                "J": list(point.current.values),
                "target": list(result[1]),
            }
        )
        return result

    def observed_receipts(*args, **kwargs):
        publication.append(
            {
                "admission_pairs": len(reads),
                "writer_surfaces": len(surfaces),
                "published_state": owner.state.scientific_digest,
            }
        )
        return original_receipts(*args, **kwargs)

    def observed_detection(postbeat, policy):
        result = original_detection(postbeat, policy)
        detections.append(
            {
                "identity": result.identity,
                "current": list(postbeat.physical_current),
                "candidate_node_ids": list(result.candidate_node_ids()),
                "published_state": owner.state.scientific_digest,
            }
        )
        return result

    with (
        patch.object(native, "ProvisionalCandidatePCStep", observed_step),
        patch.object(native, "make_commit_receipts", observed_receipts),
        patch.object(native, "GRC9V4CandidateDetection", observed_detection),
        patch.object(native, "candidate_a_writer_target", observed_surface),
        patch.object(
            pc, "scalar_zoh", side_effect=AssertionError("event must not write Z")
        ),
        patch.object(
            candidate,
            "candidate_a_log_interpolation",
            side_effect=AssertionError("event must not write W"),
        ),
    ):
        outcome = owner.expand(request)
    value = {
        "source_checkpoint": initial,
        "admission_reads": reads,
        "writer_surfaces": surfaces,
        "publication": publication,
        "checkpoint": json.loads(owner.checkpoint()),
        "actual_target": owner.state.to_payload(),
        "receipts": [r.to_payload() for r in outcome.emitted_receipts],
        "failure": None if outcome.committed else outcome.failure.to_payload(),
        "replay_identical": False,
        "detections": detections,
    }
    if outcome.committed:
        value["replay_identical"] = (
            native.GRC9V4APCOperation.replay(owner.checkpoint()).checkpoint()
            == owner.checkpoint()
        )
    return owner, outcome, value


def check_event(seed, case, value, *, numerics=False):
    target = independent_target(seed, case)
    b.require(
        value["actual_target"] == target.to_payload(),
        "independent graph/reference/resource transfer drift",
    )
    b.require(len(value["admission_reads"]) == 2, "missing source/target admission")
    for parent, observed in zip((seed, target), value["admission_reads"], strict=True):
        b.require(
            observed["inputs"] == parent.inputs.to_payload()
            and observed["published_state"] == seed.scientific_digest,
            "admission operand/publication drift",
        )
        check_read(parent.inputs, observed["read"], numerics=numerics)
        check_read(
            role_input(parent.inputs, "reset"),
            observed["reset_read"],
            numerics=numerics,
        )
    detection = value["detections"]
    b.require(
        len(detection) == 1
        and detection[0]["current"] == value["admission_reads"][0]["read"]["J"]
        and case["request"]["source_node_id"] in detection[0]["candidate_node_ids"]
        and detection[0]["published_state"] == seed.scientific_digest,
        "fresh trigger/current binding drift",
    )
    b.require(
        value["publication"]
        == [
            {
                "admission_pairs": 2,
                "writer_surfaces": 4,
                "published_state": seed.scientific_digest,
            }
        ],
        "publication preceded both-role admission",
    )
    cp = value["checkpoint"]
    b.require(
        cp["initial"] == seed.to_payload()
        and cp["state"] == target.to_payload()
        and cp["requests"] == [case["request"]]
        and cp["receipts"] == value["receipts"],
        "checkpoint drift",
    )
    source_ref, target_ref = (
        seed.inputs.geometry.reference,
        target.inputs.geometry.reference,
    )
    refs = cp["reference_currents"]
    b.require(
        len(refs) == 1
        and refs[0]["event_id"] == case["oracle"]["event_id"]
        and refs[0]["source_graph_digest"] == source_ref.graph.graph_digest
        and refs[0]["target_graph_digest"] == target_ref.graph.graph_digest,
        "reference lineage drift",
    )
    for role, key in (("current", "read"), ("reset", "reset_read")):
        old = value["admission_reads"][0][key]["J"]
        currents = dict(zip(source_ref.graph.live_edge_ids, old, strict=True))
        b.require(
            refs[0]["roles"][role]
            == {
                "source": old,
                "target": [
                    currents.get(e, 0.0) for e in target_ref.graph.live_edge_ids
                ],
            },
            "reference current map drift",
        )
    b.require(len(value["writer_surfaces"]) == 4, "missing A writer admission")
    for i, parent in enumerate((seed, target)):
        for ri, (role, key) in enumerate(
            (("current", "read"), ("reset", "reset_read"))
        ):
            authority = getattr(parent.inputs, role)
            read = value["admission_reads"][i][key]
            surface = value["writer_surfaces"][2 * i + ri]
            b.require(
                surface
                == {
                    "point_identity": read["point_identity"],
                    "C": list(authority.C),
                    "W_A": list(authority.W_A),
                    "J": read["J"],
                    "target": surface["target"],
                },
                "event W writer-surface operand drift",
            )
            if numerics:
                high = IntervalRows(
                    oracle.model_for(
                        parent.inputs.geometry.reference.graph.port_graph.to_payload()
                    )
                )
                b.require(
                    full_error(
                        surface["target"],
                        high.conductance(
                            vector(authority.C),
                            vector(authority.W_A),
                            vector(read["J"]),
                        ),
                    )
                    < LIMITS["history_error"],
                    "event writer surface equation drift",
                )
    for role in ROLES:
        b.require(
            bool(charge_record(target.inputs, getattr(target.inputs, role))),
            "prescribed adjacent-pair charge changed",
        )
    receipts = value["receipts"]
    b.require(len(receipts) == 4, "event receipt count drift")
    _, checked = native.make_commit_receipts(
        [r["identity_payload"] for r in receipts],
        operation_id=case["request"]["operation_id"],
        source_state_digest=seed.scientific_digest,
        target_state_digest=target.scientific_digest,
        target_step_index=target.inputs.step_index,
        target_time=target.inputs.time,
    )
    b.require(
        [r.to_payload() for r in checked] == receipts
        and cp["lifecycle_digest"] == target.lifecycle_digest(checked),
        "receipt/commit digest drift",
    )
    first = receipts[0]["identity_payload"]
    b.require(
        first["event_id"] == case["oracle"]["event_id"]
        and first["core"]["information_losses"] == ["carrier_history_loss"],
        "event/loss drift",
    )
    content = {
        "schema_version": "grcv4-history-content-identity-v1",
        "subject": "carrier",
        "content": list(seed.inputs.current.Z_4 + seed.inputs.reset.Z_4),
    }
    archive = cp["carrier_archives"]
    b.require(
        len(archive) == 1
        and archive[0]["history_content"] == content
        and archive[0]["source_edge_ids"] == list(source_ref.graph.live_edge_ids)
        and archive[0]["source_state_digest"] == seed.scientific_digest
        and archive[0]["source_graph_digest"] == source_ref.graph.graph_digest
        and archive[0]["history_digest"]
        == b.payload_identity("history_content_identity_payload", content),
        "whole actual current/reset carrier archive drift",
    )
    target_content = {
        "schema_version": "grcv4-history-content-identity-v1",
        "subject": "carrier",
        "content": list(target.inputs.current.Z_4 + target.inputs.reset.Z_4),
    }
    b.require(
        first["history"]["candidate"]
        == {
            "subject": "candidate",
            "disposition": "exact_transport",
            "source_history_digest": b.payload_identity(
                "history_content_identity_payload",
                oracle.candidate_content(
                    b.authority_payload(seed.inputs.current),
                    b.authority_payload(seed.inputs.reset),
                ),
            ),
            "target_history_digest": b.payload_identity(
                "history_content_identity_payload",
                oracle.candidate_content(
                    b.authority_payload(target.inputs.current),
                    b.authority_payload(target.inputs.reset),
                ),
            ),
            "information_loss": "none",
        }
        and first["history"]["carrier"]
        == {
            "subject": "carrier",
            "disposition": "whole_carrier_reset",
            "source_history_digest": archive[0]["history_digest"],
            "target_history_digest": b.payload_identity(
                "history_content_identity_payload", target_content
            ),
            "information_loss": "carrier_history_loss",
        },
        "candidate/carrier channel drift",
    )
    b.require(
        all(
            r["identity_payload"]["core"]["information_losses"]
            == ["carrier_history_loss"]
            for r in receipts
        ),
        "loss omitted from receipt",
    )
    b.require(
        value["failure"] is None and value["replay_identical"] is True,
        "event/replay incomplete",
    )
    return target


def execute_case(seed, declared):
    case = bind_case(seed, declared)
    row = {
        "case_id": case["case_id"],
        "input_digest": b.digest(declared),
        "actual_case": case,
        "coverage_binding": case["coverage_binding"],
        "family": "A_PC",
        "outcome": "incomplete_case",
        "case_passed": False,
        "event_committed": False,
        "first_failure": None,
        "continuation": [],
        "final_reads": {},
        "final_effects": {},
        "entry_effects": {},
        "user_accepted": False,
        "aggregate_closed": False,
    }
    stage, role, index = "independent_preflight", "both", 0
    start = time.monotonic()
    try:
        with b.budget(case["execution_budget_seconds"]):
            target = independent_target(seed, case)
            row["target_charge"] = {
                role: charge_record(target.inputs, getattr(target.inputs, role))
                for role in ROLES
            }
            row["predictions"] = preflight(target)
            stage = "event"
            request = b.GRC9V4ExpansionRequestInput.from_payload(case["request"])
            owner, outcome, event = event_capture(seed, request)
            row.update(event=event, event_committed=outcome.committed)
            b.require(
                outcome.committed, "native event rejected: " + str(event["failure"])
            )
            target = check_event(seed, case, event)
            for role in ROLES:
                before = role_input(target.inputs, role, dt=b.DT)
                for index in range(1, 11):
                    stage = "target_continuation"
                    native_step, value = perform_step(before)
                    expected = row["predictions"][role][index - 1]
                    error = max(
                        abs(x - y)
                        for x, y in zip(
                            expected["C"],
                            native_step.next_inputs.current.C,
                            strict=True,
                        )
                    )
                    b.require(
                        error < 2**-39,
                        "nominal independent trajectory comparison failed",
                    )
                    z_error = max(
                        abs(x - y)
                        for x, y in zip(
                            expected["Z"],
                            native_step.next_inputs.current.Z_4,
                            strict=True,
                        )
                    )
                    b.require(
                        z_error < LIMITS["carrier_error"],
                        "nominal carrier trajectory drift",
                    )
                    w_error = max(
                        abs(x - y)
                        for x, y in zip(
                            expected["W_A"],
                            native_step.next_inputs.current.W_A,
                            strict=True,
                        )
                    )
                    b.require(
                        w_error < LIMITS["history_error"], "nominal W trajectory drift"
                    )
                    row["continuation"].append(
                        {
                            "role": role,
                            "index": index,
                            "step": value,
                            "nominal_resource_error": error,
                            "nominal_carrier_error": z_error,
                            "nominal_history_error": w_error,
                        }
                    )
                    if index == 1:
                        row["entry_effects"][role] = writer_effects(before, value)
                    before = native_step.next_inputs
                stage = "final_read"
                fresh = certified_read(
                    CandidatePCRead(replace(before, dt=0), backend(before))
                )
                b.require(
                    fresh == row["continuation"][-1]["step"]["restart"],
                    "fresh final PC read differs from restart",
                )
                row["final_reads"][role] = fresh
                row["final_effects"][role] = effect_checks(replace(before, dt=0), fresh)
            b.require(
                owner.state.to_payload() == event["actual_target"],
                "detached continuation mutated owner",
            )
            row.update(outcome="passed_named_case", case_passed=True)
    except Exception as exc:  # noqa: BLE001 -- retain typed failure evidence before stopping campaign
        row["first_failure"] = {
            "stage": stage,
            "role": role,
            "index": index,
            "type": type(exc).__name__,
            "message": str(exc).replace(str(b.ROOT), "<repository>"),
            "kind": "operational_timeout"
            if isinstance(exc, b.BudgetExpired)
            else "numerical_or_lifecycle_failure",
        }
    row["elapsed_seconds"] = time.monotonic() - start
    return row


def validate(manifest, results, *, numerics=False):
    b.check_digest(results)
    b.require(
        results["manifest_digest"] == manifest["record_digest"]
        and results["native_runtime_executed"] is True
        and results["user_accepted"] is False
        and results["aggregate_closed"] is False,
        "runtime binding/scope drift",
    )
    source = results["shared"]
    initial = b.GeometryStageInputs.from_payload(manifest["initial_inputs"])
    after = check_step(initial, source["source_step"], numerics=numerics)
    seed = state(source["actual_source"])
    b.require(
        seed.inputs == replace(after, dt=0)
        and seed.specialization == state(manifest["nominal_source"]).specialization,
        "source schedule drift",
    )
    b.require(
        [r["case_id"] for r in results["cases"]]
        == [c["case_id"] for c in manifest["cases"]],
        "case roster drift",
    )
    passed = 0
    for case, row in zip(manifest["cases"], results["cases"], strict=True):
        b.require(
            row["input_digest"] == b.digest(case)
            and row["coverage_binding"] == case["coverage_binding"]
            and row["user_accepted"] is False
            and row["aggregate_closed"] is False,
            "case input/scope drift",
        )
        if not row["case_passed"]:
            b.require(
                row["outcome"] == "incomplete_case"
                and row["first_failure"] is not None,
                "incomplete case overclaim",
            )
            continue
        b.require(
            row["outcome"] == "passed_named_case"
            and row["event_committed"] is True
            and row["first_failure"] is None,
            "false success",
        )
        actual = bind_case(seed, case)
        b.require(actual == row["actual_case"], "actual event identity drift")
        target = check_event(seed, actual, row["event"], numerics=numerics)
        b.require(
            row["target_charge"]
            == {
                role: charge_record(target.inputs, getattr(target.inputs, role))
                for role in ROLES
            },
            "charge record drift",
        )
        b.require(
            [(r["role"], r["index"]) for r in row["continuation"]]
            == [(r, i) for r in ROLES for i in range(1, 11)]
            and set(row["final_reads"]) == set(ROLES),
            "incomplete both-role schedule",
        )
        for role in ROLES:
            before = role_input(target.inputs, role, dt=b.DT)
            controls = row["entry_effects"][role]
            b.require(
                set(controls)
                == {
                    "written_carrier_next_current",
                    "same_source_carrier",
                    "same_source_next_current",
                    "stale_resource_writer_W",
                    "stale_resource_writer_next_current",
                    "baseline_current_writer_W",
                    "baseline_current_writer_next_current",
                    "next_current_consumes_written_W",
                }
                and all(
                    v["minimum_margin_ratio"] > 1 and v["exact_effect_lower"] > 0
                    for v in controls.values()
                ),
                "unresolved W/Z consumer effects",
            )
            for record in (r for r in row["continuation"] if r["role"] == role):
                if numerics and record["index"] == 1:
                    b.require(
                        controls == writer_effects(before, record["step"]),
                        "W/Z effect interval drift",
                    )
                before = check_step(before, record["step"], numerics=numerics)
                expected = row["predictions"][role][record["index"] - 1]
                error = max(
                    abs(x - y)
                    for x, y in zip(expected["C"], before.current.C, strict=True)
                )
                b.require(
                    error == record["nominal_resource_error"] and error < 2**-39,
                    "nominal comparison drift",
                )
                z_error = max(
                    abs(x - y)
                    for x, y in zip(expected["Z"], before.current.Z_4, strict=True)
                )
                b.require(
                    z_error == record["nominal_carrier_error"]
                    and z_error < LIMITS["carrier_error"],
                    "nominal carrier comparison drift",
                )
                w_error = max(
                    abs(x - y)
                    for x, y in zip(expected["W_A"], before.current.W_A, strict=True)
                )
                b.require(
                    w_error == record["nominal_history_error"]
                    and w_error < LIMITS["history_error"],
                    "nominal W comparison drift",
                )
                last = record["step"]["restart"]
            check_read(
                replace(before, dt=0), row["final_reads"][role], numerics=numerics
            )
            b.require(
                row["final_reads"][role] == last, "fresh PC read/restart mismatch"
            )
            effects = row["final_effects"][role]
            b.require(
                set(effects) == {"geometry", "feedback"}
                and all(
                    v["minimum_margin_ratio"] > 1 and v["exact_effect_lower"] > 0
                    for v in effects.values()
                ),
                "unresolved final read-path effects",
            )
            if numerics:
                b.require(
                    effects
                    == effect_checks(replace(before, dt=0), row["final_reads"][role]),
                    "final effect certificate drift",
                )
        passed += 1
    return {
        "retained_integrity": "passed",
        "cases_passed": passed,
        "cases_required": 16,
        "successful_history_cells": 2 * passed,
        "native_trajectories_rerun": False,
        "interval_equations_recomputed": numerics,
        "user_accepted": False,
        "aggregate_closed": False,
    }


def write_new(name, value):
    path = b.ROOT / name
    with path.open("x") as out:
        out.write(json.dumps(value, separators=(",", ":"), allow_nan=False) + "\n")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--prepare", action="store_true")
    mode.add_argument("--run", action="store_true")
    mode.add_argument("--check-retained", action="store_true")
    parser.add_argument("--recheck-numerics", action="store_true")
    parser.add_argument("--manifest", default=INPUTS)
    parser.add_argument("--output", default=RESULTS)
    args = parser.parse_args()
    b.require(
        not args.recheck_numerics or args.check_retained,
        "recheck requires retained mode",
    )
    for name in (args.manifest, args.output):
        b.require(
            not b.Path(name).is_absolute() and ".." not in b.Path(name).parts,
            "repository-relative path required",
        )
    if args.prepare:
        write_new(args.manifest, make_manifest())
        print("A_PC inputs bound; no native execution")
        return
    manifest = b.read(args.manifest)
    check_manifest(manifest)
    if args.check_retained:
        print(
            json.dumps(
                validate(manifest, b.read(args.output), numerics=args.recheck_numerics),
                indent=2,
            )
        )
        return
    b.require(
        not (b.ROOT / args.output).exists(), "refusing to overwrite native evidence"
    )
    journal = b.ROOT / (args.output + ".progress.jsonl")
    b.require(not journal.exists(), "existing progress requires explicit recovery")
    with b.exact_backend(b.ExactBackend.FLINT):
        shared, seed = run_source(manifest)
        results = {
            "schema": "p984b-apc-runtime-results-v1",
            "manifest_digest": manifest["record_digest"],
            "environment": {
                "python": platform.python_version(),
                "numpy": version("numpy"),
                "mpmath": version("mpmath"),
                "python_flint": version("python-flint"),
            },
            "shared": shared,
            "cases": [],
            "native_runtime_executed": True,
            "user_accepted": False,
            "aggregate_closed": False,
        }
        with journal.open("x") as progress:
            progress.write(b.canonical_json_bytes(b.seal(results)).decode() + "\n")
            progress.flush()
            for case in manifest["cases"]:
                row = execute_case(seed, case)
                # Strict wire validation and durable per-case evidence precede
                # starting another expensive trajectory. Preserve on failure.
                progress.write(b.canonical_json_bytes(b.seal(row)).decode() + "\n")
                progress.flush()
                results["cases"].append(row)
                print(
                    case["fixture_id"], row["outcome"], row["first_failure"], flush=True
                )
                if not row["case_passed"]:
                    break
    results = b.seal(results)
    write_new(args.output, results)
    if len(results["cases"]) != len(manifest["cases"]):
        print("INCOMPLETE_CAMPAIGN: first failure retained; remaining cases not run")
        raise SystemExit(1)
    report = validate(manifest, results)
    print(json.dumps({**report, "native_execution_in_this_command": True}, indent=2))
    if report["cases_passed"] != 16:
        raise SystemExit(1)
    # This command's exclusive temporary journal is now fully represented by
    # the validated final artifact. Failed/interrupted journals remain intact.
    journal.unlink()


if __name__ == "__main__":
    main()
