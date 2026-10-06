"""Seventeen bounded native C_PC expansion companions and both histories.

Paper D.7/E.10: old carrier read, whole event reset, one held-source ZOH
write. Independent interval equations use this native declaration (R=1,
kappa_H=2^-16, zeta_C=2^-30), not the P9-8.0 research parameters.
Retained validation is distinct from native execution and user acceptance.
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
from p984b_cci_runtime import represented_continuity
from test_p980_os_effect_witness import (
    IV,
    IntervalRows,
    full_error,
    number,
    separation,
    vector,
)
from test_p980_os_numerical_feasibility import ResearchParameters, StagedRows

from pygrc.models import grc_9_v4_lifecycle as native
from pygrc.models import grc_v4_pc as pc
from pygrc.models.grc_v4_pc import CandidatePCRead, ProvisionalCandidatePCStep

SELF = b.HERE + "p984b_cpc_runtime.py"
TEST = b.HERE + "test_p984b_cpc_runtime.py"
INPUTS = b.BASE + "P9-8.4b-CPCCases.json"
RESULTS = b.BASE + "P9-8.4b-CPCResults.json"
REVIEW = b.BASE + "P9-8.4b-CPCRuntimeReview.md"
ROLES = ("current", "reset")
LIMITS = {
    "geometry_error": Q(1, 2**48),
    "current_error": Q(1, 2**40),
    "source_error": Q(1, 2**60),
    "resource_error": Q(1, 2**40),
    "carrier_error": Q(1, 2**48),
}


def state(payload):
    spec = payload["specialization"]
    return native.GRC9V4CPCState(
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


def make_manifest():
    coverage = b.read(b.COVERAGE)
    b.check_digest(coverage)
    old = b.read(b.SEEDS)["states"]["C_PC"]
    initial = b.GeometryStageInputs.from_payload(old["source"]["inputs"])
    z = tuple(
        (1 if i == j else 0.5) * (-1) ** (i + j) / 16
        for i in range(9)
        for j in range(9)
    )
    initial = replace(
        initial,
        current=b.GRCV4AuthoritativeState((3.0, *((193 / 64,) * 9)), None, z),
        step_index=0,
        time=0,
        dt=b.DT,
    )
    initial = replace(initial, geometry=geometry(initial, initial.current))
    wanted = {
        r["fixture_id"]
        for r in coverage["coverage_cells"]
        if r["owner"] == "P9-8.4b" and r["family"] == "C_PC" and r["applicable"]
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
        request["operation_id"] = "p984b-cpc-" + v["fixture_id"]
        if (request["target_effective_degree"], request["growth_phase"]) == (52, 1):
            request["resource_distribution"] = [0.25, 0.5, 0.25]
        cases.append(
            {
                "case_id": "P984B-CPC-" + v["fixture_id"],
                "fixture_id": v["fixture_id"],
                "family": "C_PC",
                "subject_kind": "native_companion_of_literal_carrier_reset"
                if v.get("profile_family_id") == "C_PC"
                else "native_companion",
                "request": request,
                "oracle": b.construction_oracle(
                    v, request, old["source"]["specialization"]
                ),
                "coverage_binding": {
                    "record_digest": coverage["record_digest"],
                    "cell_ids": [v["fixture_id"] + "::C_PC::" + r for r in ROLES],
                },
                "schedule": {
                    "source_current_beats": 1,
                    "source_reset_beats": 0,
                    "target_beats_per_role": 10,
                    "dt": b.DT,
                    "final_read": True,
                },
                "execution_budget_seconds": 480,
                "changes_from_frozen": [
                    "native_C_PC_declaration_and_actual_role_pair",
                    "source_labels_and_event_identities",
                    "D52_phase_one_shares_only",
                ],
                "comparison": {
                    "kind": "full_formula_pointwise_interval_error_and_native_whole_chart_admission",
                    "budgets": {k: str(v) for k, v in LIMITS.items()},
                    "interval_digits": 60,
                    "nominal_trajectory_tolerance": 2**-39,
                    "accumulated_trajectory_error_bound": False,
                    "uniform_parameter_tube": False,
                },
            }
        )
    b.require(len(cases) == 17, "all seventeen C_PC subjects required")
    paths = [
        b.SEEDS,
        b.COVERAGE,
        b.VECTORS,
        b.SELF,
        SELF,
        TEST,
        b.HERE + "p984b_cci_runtime.py",
        "pyproject.toml",
        "uv.lock",
        coverage["scientific_claim_mapping"]["paper"]["path"],
        coverage["scientific_claim_mapping"]["side_tool_source"],
        "specs/grc-9-v4-spec.md",
        "specs/grc-v4-spec.md",
    ]
    paths += [
        str(p.relative_to(b.ROOT))
        for pattern in (
            "src/pygrc/models/grc*v4*.py",
            "src/pygrc/models/grc_v4_assets/*.json",
            "tests/models/test_grc*v4*.py",
            b.HERE + "test_p980*.py",
        )
        for p in b.ROOT.glob(pattern)
    ]
    return b.seal(
        {
            "schema": "p984b-cpc-case-manifest-v1",
            "family": "C_PC",
            "initial_inputs": initial.to_payload(),
            "expected_source": old["source"],
            "cases": cases,
            "source_bindings": b.bind(paths),
            "scientific_contracts": {
                "paper": ["D.4 Candidate C", "D.7 PC", "E.10 whole lifecycle"],
                "expansion_claims": coverage["scientific_claim_mapping"],
                "scope": "native companions; literal frozen identities are checked separately by frozen_mechanics",
            },
            "phase_one_recipe": "explicit [1/4,1/2,1/4]; C_PC continuation independently checked",
            "user_accepted": False,
            "aggregate_closed": False,
        }
    )


def check_manifest(value):
    b.check_digest(value)
    b.check_bindings(value["source_bindings"])
    b.require(value == make_manifest(), "C_PC manifest/case/budget drift")


def independent_target(manifest, case):
    """Complete target reference and both affine resource images before runtime."""
    source = b.GeometryStageInputs.from_payload(manifest["expected_source"]["inputs"])
    graph = b.GRCV4Graph.from_payload(case["oracle"]["target_graph"])
    weights = {edge: 1 for edge in graph.live_edge_ids}
    ref = source.geometry.reference
    params = ref.profile.params_resolved.to_payload()
    params["candidate"]["W_C_tr"] = weights
    params["candidate"]["W_C_tr_content_digest"] = b.payload_identity(
        "wctr_identity_payload",
        {"schema_version": "grcv4-wctr-identity-v1", "W_C_tr": weights},
    )
    params["geometry"]["reference_hodge_digest"] = b.payload_identity(
        "reference_hodge_identity_payload",
        {
            "schema_version": "grcv4-reference-hodge-identity-v1",
            "edge_weights": weights,
        },
    )
    base = tuple((0.0,) * len(weights) for _ in weights)
    params["geometry"]["K4_base_digest"] = b.payload_identity(
        "k4_identity_payload",
        {"schema_version": "grcv4-k4-identity-v1", "K4_base": [list(r) for r in base]},
    )
    identity = ref.profile.identity_payload.to_payload()
    identity["params_hash"] = b.payload_identity("resolved_params", params)
    target = b.GRCV4ReferenceGeometry(
        graph,
        b.resolve_profile(params, identity),
        ref.context,
        base,
        b.FrozenJSONMap(weights),
    )
    states = {}
    for role in ("current", "reset"):
        old = dict(zip(ref.graph.live_node_ids, getattr(source, role).C, strict=True))
        image = {n: old.get(n, 0.0) for n in graph.live_node_ids}
        for branch, share in enumerate(case["request"]["resource_distribution"], 1):
            image[case["oracle"]["event_id"] + f"/satellite/{branch}"] = float(
                Q(old["s"]) * Q(share)
            )
        states[role] = b.GRCV4AuthoritativeState(
            tuple(image[n] for n in graph.live_node_ids),
            None,
            (0.0,) * len(weights) ** 2,
        )
    return replace(
        source,
        geometry=target.geometry(),
        **states,
        operation_id=case["request"]["operation_id"],
        dt=0,
    )


def independent_model(before):
    """Reassemble incidence and star overlap from explicit nonloop endpoints."""
    ref = before.geometry.reference
    p = ref.profile.params_resolved.candidate
    b.require(
        p.kappa_M_C == 2**-24
        and p.kappa_Phi_C == p.eta_C == p.tau_C == 1
        and p.C_ref == 1
        and p.Lambda_C == 1 / 512
        and set(p.W_C_tr.values()) == {1}
        and all(x == 0 for row in ref.K4_base for x in row)
        and set(ref.edge_weights.values()) == {1},
        "independent chart mismatch",
    )
    graph = ref.graph.port_graph
    return StagedRows(
        graph.live_node_ids,
        [e.to_payload() for e in graph.edges],
        ResearchParameters(chi_c=Q(p.chi_C), zeta_c=Q(p.zeta_C)),
    )


def truth(before):
    model = independent_model(before)
    # These connected trees have nonzero Laplacian eigenvalue >=4/(n(n-1)).
    # ||Z||op <= ||Z||F; H >= (1-|kH|R)I. Thus the entire carrier ball
    # retains exactly the constant vertex sector below Lambda, justifying t.
    n, m = len(model.nodes), len(model.edges)
    seen = {model.nodes[0]}
    for _ in model.nodes:
        for e in model.edges:
            a, c = e["tail"]["node_id"], e["head"]["node_id"]
            if a in seen or c in seen:
                seen.update((a, c))
    p = before.geometry.reference.profile.params_resolved
    lower = 1 - abs(Q(p.geometry.kappa_H)) * Q(p.realization.radius)
    b.require(
        len(seen) == n
        and m == n - 1
        and lower > 0
        and 0 < Q(p.candidate.Lambda_C) < lower * 4 / Q(n * (n - 1)),
        "independent whole-ball constant-sector proof failed",
    )
    high = IntervalRows(model)
    z = IV.matrix(np.array(before.current.Z_4).reshape(m, m).tolist())
    h = high.I + number(p.geometry.kappa_H) * z
    c = vector(before.current.C)
    read = high.read("C", c, None, h)
    return {"high": high, "c": c, "z": z, "H": h, "read": read}


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
            "baseline": list(point.algebra.baseline.values),
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
    zeta = Q(before.geometry.reference.profile.params_resolved.candidate.zeta_C)
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
        Q(bounds["geometry_radius"]) == Q(1, 2**16)
        and Q(bounds["carrier_radius"]) == 1
        and Q(bounds["hodge_lower"]) == 1 - Q(1, 2**16)
        and Q(bounds["selector_gap_lower"]) > 0
        and 0 <= Q(bounds["source_norm_upper"]) <= 1
        and bounds["admitted_strata"] == "1",
        "whole-chart admission drift",
    )
    cert = value["independent_certificate"]
    b.require(
        cert["input_identity"] == before.identity
        and cert["selected_read_digest"] == value["record_digest"],
        "certificate binding drift",
    )
    for k in ("geometry_error", "current_error", "source_error"):
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
    a = IV.exp(
        -number(before.dt)
        / number(before.geometry.reference.profile.params_resolved.realization.tau_PC)
    )
    carrier = a * exact["z"] + (1 - a) * exact["read"]["source"]
    resource = exact["c"] - number(before.dt) * exact["high"].B * exact["read"]["J"]
    return {
        "resource_error": str(full_error(after.current.C, resource)),
        "carrier_error": str(full_error(after.current.Z_4, IV.matrix(list(carrier)))),
    }


def perform_step(before):
    calls = []
    original = pc.scalar_zoh

    def observed(z, source, dt, tau):
        calls.append({"Z": list(z), "source": list(source), "dt": dt, "tau": tau})
        return original(z, source, dt, tau)

    with patch.object(pc, "scalar_zoh", observed):
        step = ProvisionalCandidatePCStep(before)
    value = {
        "read": certified_read(step.read),
        "reset_read": certified_read(step.reset_read),
        "restart": certified_read(step.restart),
        "poststate": step.next_inputs.to_payload(),
        "selection_current": list(step.resource.selection.current.values),
        "writer": None if step.writer is None else "unexpected_A_writer",
        "carrier_writes": step.carrier_writes,
        "carrier_calls": calls,
        "errors": step_errors(before, step.next_inputs),
    }
    check_step(before, value)
    return step, value


def check_step(before, value, *, numerics=False):
    check_read(before, value["read"], numerics=numerics)
    check_read(role_input(before, "reset"), value["reset_read"], numerics=numerics)
    source = [x for row in value["read"]["source"] for x in row]
    tau = before.geometry.reference.profile.params_resolved.realization.tau_PC
    b.require(
        value["writer"] is None
        and value["carrier_writes"] == 1
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
        None,
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
    for key in ("resource_error", "carrier_error"):
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
    initial = b.GeometryStageInputs.from_payload(manifest["initial_inputs"])
    step, value = perform_step(initial)
    seed = replace(
        state(manifest["expected_source"]), inputs=replace(step.next_inputs, dt=0)
    )
    b.require(
        seed.to_payload() == manifest["expected_source"],
        "fresh source differs from accepted predecessor",
    )
    return {"source_step": value, "actual_source": seed.to_payload()}, seed


def preflight(target):
    """Nominal independent dense+Decimal predictions before native execution."""
    from tests.models.test_grc_9_v4_lifecycle import independent_pc_beat

    rows = {}
    for role in ROLES:
        before = role_input(target, role, dt=b.DT)
        trajectory = []
        for index in range(1, 11):
            c, z, _ = independent_pc_beat(before)
            b.require(
                np.isfinite(c).all() and min(c) >= 0,
                "preflight predicts inadmissible resource",
            )
            authority = b.GRCV4AuthoritativeState(tuple(c), None, z)
            before = replace(
                before, current=authority, geometry=geometry(before, authority)
            )
            trajectory.append({"index": index, "C": c.tolist(), "Z": list(z)})
        rows[role] = trajectory
    return rows


def effect_checks(before, value):
    """Read-path controls only: no claim of matched forcing or hysteresis."""
    exact = truth(before)
    results = {}
    for channel in ("geometry", "feedback", "modulation"):
        control = exact["high"].read(
            "C", exact["c"], None, exact["H"], **{channel: False}
        )
        nominal = np.array([float(x.mid) for x in control["J"]])
        results[channel] = separation(
            np.array(value["J"]), nominal, exact["read"]["J"], control["J"]
        )
    return results


def event_capture(seed, request):
    owner = native.GRC9V4CPCOperation(seed)
    initial = json.loads(owner.checkpoint())
    reads, publication, detections = [], [], []
    original_step, original_receipts = (
        native.ProvisionalCandidatePCStep,
        native.make_commit_receipts,
    )
    original_detection = native.GRC9V4CandidateDetection

    def observed_step(inputs, *args, **kwargs):
        result = original_step(inputs, *args, **kwargs)
        b.require(
            inputs.dt == 0
            and result.next_inputs == inputs
            and result.carrier_writes == 0,
            "event performed a physical step",
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

    def observed_receipts(*args, **kwargs):
        publication.append(
            {
                "admission_pairs": len(reads),
                "published_state": owner.state.scientific_digest,
            }
        )
        return original_receipts(*args, **kwargs)

    def observed_detection(postbeat, policy):
        result = original_detection(postbeat, policy)
        detections.append(
            {
                "identity": result.identity,
                "row_inputs_identity": postbeat.identity,
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
        patch.object(
            pc, "scalar_zoh", side_effect=AssertionError("event must not write Z")
        ),
    ):
        outcome = owner.expand(request)
    value = {
        "source_checkpoint": initial,
        "admission_reads": reads,
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
            native.GRC9V4CPCOperation.replay(owner.checkpoint()).checkpoint()
            == owner.checkpoint()
        )
    return owner, outcome, value


def check_event(seed, case, value, *, numerics=False):
    expected = independent_target({"expected_source": seed.to_payload()}, case)
    target = replace(seed, inputs=expected)
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
        == [{"admission_pairs": 2, "published_state": seed.scientific_digest}],
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
    source_ref, _target_ref = (
        seed.inputs.geometry.reference,
        target.inputs.geometry.reference,
    )
    # C_PC's accepted checkpoint stores the whole carrier archive. It has no
    # C_CI reference-current envelope; no new checkpoint schema is invented.
    for role in ROLES:
        b.require(
            sum(map(Q, getattr(seed.inputs, role).C))
            == sum(map(Q, getattr(target.inputs, role).C)),
            "exact event charge changed",
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
            "disposition": "rederived",
            "source_history_digest": None,
            "target_history_digest": None,
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


def execute_case(seed, case):
    row = {
        "case_id": case["case_id"],
        "input_digest": b.digest(case),
        "coverage_binding": case["coverage_binding"],
        "family": "C_PC",
        "outcome": "incomplete_case",
        "case_passed": False,
        "event_committed": False,
        "first_failure": None,
        "continuation": [],
        "final_reads": {},
        "final_effects": {},
        "user_accepted": False,
        "aggregate_closed": False,
    }
    stage, role, index = "independent_preflight", "both", 0
    start = time.monotonic()
    try:
        with b.budget(case["execution_budget_seconds"]):
            target = independent_target({"expected_source": seed.to_payload()}, case)
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
                    row["continuation"].append(
                        {
                            "role": role,
                            "index": index,
                            "step": value,
                            "nominal_resource_error": error,
                            "nominal_carrier_error": z_error,
                        }
                    )
                    before = native_step.next_inputs
                stage = "final_read"
                fresh = certified_read(CandidatePCRead(replace(before, dt=0)))
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
    except Exception as exc:
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
        and seed.to_payload() == manifest["expected_source"],
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
        target = check_event(seed, case, row["event"], numerics=numerics)
        b.require(
            [(r["role"], r["index"]) for r in row["continuation"]]
            == [(r, i) for r in ROLES for i in range(1, 11)]
            and set(row["final_reads"]) == set(ROLES),
            "incomplete both-role schedule",
        )
        for role in ROLES:
            before = role_input(target.inputs, role, dt=b.DT)
            for record in (r for r in row["continuation"] if r["role"] == role):
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
                last = record["step"]["restart"]
            check_read(
                replace(before, dt=0), row["final_reads"][role], numerics=numerics
            )
            b.require(
                row["final_reads"][role] == last, "fresh PC read/restart mismatch"
            )
            effects = row["final_effects"][role]
            b.require(
                set(effects) == {"geometry", "feedback", "modulation"}
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
        "cases_required": 17,
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
        print("C_PC inputs bound; no native execution")
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
            "schema": "p984b-cpc-runtime-results-v1",
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
    if report["cases_passed"] != 17:
        raise SystemExit(1)
    # This command's exclusive temporary journal is now fully represented by
    # the validated final artifact. Failed/interrupted journals remain intact.
    journal.unlink()


if __name__ == "__main__":
    main()
