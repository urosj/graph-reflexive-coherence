"""Sixteen A_RG2b companions with certified C/scaled-log-W chains and W lineage.

Native execution, independent interval recomputation and scoped acceptance are
separate. The signed argument completion is the accepted R6/native successor,
not the paper's compact-support extension and not an instantaneous CI root.
"""

import argparse
import json
import math
import platform
import time
from contextlib import ExitStack, contextmanager
from contextvars import ContextVar
from copy import deepcopy
from dataclasses import replace
from decimal import Decimal, localcontext
from fractions import Fraction as Q
from functools import wraps
from importlib.metadata import version
from pathlib import Path
from unittest.mock import patch

import numpy as np
import p984b_runtime as b
import test_p980_rg2b_completion as proof
import test_p980_rg2b_numerical as oracle
import verify_p983a_arg2b_oracle as a_oracle
from p984b_cci_runtime import represented_continuity
from test_p980_os_effect_witness import (
    IV,
    PARAMS,
    IntervalRows,
    endpoint,
    full_error,
    infinity,
    inverse,
    number,
    separation,
    staged_write,
    upper_abs,
    vector,
)

from pygrc.models import grc_9_v4_arg2b as signed
from pygrc.models import grc_9_v4_lifecycle as native
from pygrc.models import grc_v4_candidate_a as candidate
from pygrc.models import grc_v4_rg2b as rg
from pygrc.models.grc_9_v4_expansion import arg2b_profile_template
from pygrc.models.grc_9_v4_topology import GRC9V4CandidateADifferentialReference
from pygrc.models.grc_v4_candidate_a import CandidateACurrent
from pygrc.models.grc_v4_ci import _source
from pygrc.models.grc_v4_codec import payload_identity
from tests.models.test_grc_9_v4_arg2b import fixture

SELF = b.HERE + "p984b_arg2b_runtime.py"
TEST = b.HERE + "test_p984b_arg2b_runtime.py"
INPUTS = b.BASE + "P9-8.4b-ARG2bCases.json"
RESULTS = b.BASE + "P9-8.4b-ARG2bResults.json"
REVIEW = b.BASE + "P9-8.4b-ARG2bRuntimeReview.md"
PREDECESSOR = b.BASE + "P9-8.3A.2-ARG2b-Validation.json"
DECLARATION = a_oracle.RECORD
ROLES = ("current", "reset")
LIMITS = {
    "geometry_error": Q(1, 2**48),
    "current_error": Q(1, 2**40),
    "baseline_error": Q(1, 2**40),
    "source_error": Q(1, 2**64),
    "readback_error": Q(1, 2**40),
    "flat_error": Q(1, 2**40),
    "resource_error": Q(1, 2**40),
    "history_error": Q(1, 2**48),
}


# Exclusive wall-clock categories are diagnostic only; never proof inputs.
_TIMING = ContextVar("arg2b_timing", default=None)


@contextmanager
def timing_scope(category):
    profile = _TIMING.get()
    if profile is None:
        yield
        return
    start = time.monotonic()
    frame = [category, 0.0]
    profile["stack"].append(frame)
    try:
        yield
    finally:
        elapsed = time.monotonic() - start
        profile["stack"].pop()
        profile["seconds"][category] = (
            profile["seconds"].get(category, 0.0) + elapsed - frame[1]
        )
        if profile["stack"]:
            profile["stack"][-1][1] += elapsed


def measured(category):
    def decorate(function):
        @wraps(function)
        def wrapped(*args, **kwargs):
            with timing_scope(category):
                return function(*args, **kwargs)

        return wrapped

    return decorate


@contextmanager
def timing_profile():
    result = {"stack": [], "seconds": {}}
    token = _TIMING.set(result)
    try:
        yield result["seconds"]
    finally:
        _TIMING.reset(token)


@contextmanager
def native_disabled():
    forbidden = AssertionError("native numerical producer disabled during recheck")
    with ExitStack() as stack:
        for owner, names in (
            (rg, ("CandidateRG2bSection", "ProvisionalCandidateRG2bStep")),
            (signed, ("propose", "certify_chain", "literal")),
            (native, ("CandidateACurrent", "_arg2b_readmit")),
            (candidate, ("candidate_a_writer_target", "candidate_a_log_interpolation")),
        ):
            for name in names:
                stack.enter_context(patch.object(owner, name, side_effect=forbidden))
        stack.enter_context(
            patch(__name__ + ".CandidateACurrent", side_effect=forbidden)
        )
        yield


def state(payload):
    spec = payload["specialization"]
    return native.GRC9V4ARG2bState(
        b.GeometryStageInputs.from_payload(payload["inputs"]),
        native.GRC9V4Specialization(
            b.FrozenJSONMap(spec["resolved"]), b.FrozenJSONMap(spec["identity_payload"])
        ),
    )


def model(inputs):
    graph = inputs.geometry.reference.graph.port_graph
    return oracle.RepresentedAuxiliary(
        graph.live_node_ids, [e.to_payload() for e in graph.edges], PARAMS
    )


def global_record():
    values = proof.global_bounds("A")
    section = proof.section_budgets(values)
    names = {
        "base_X_lipschitz": "A_X",
        "base_h_lipschitz": "A_H",
        "base_displacement_upper": "M_f",
        "source_upper": "M_S",
        "source_X_lipschitz": "B_X",
        "source_h_lipschitz": "B_H",
        "current_upper": "J",
    }
    native_bounds = {k: str(values[v]) for k, v in names.items()}
    native_bounds.update(
        inverse_lipschitz=str(section["inverse_lip"]),
        contraction_upper=str(section["q_section"]),
        section_lipschitz=str(proof.SECTION_LIP),
        section_radius=str(proof.RHO),
        section_value_radius=str(section["value_radius"]),
        image_lipschitz=str(section["image_lip"]),
        current_inverse_upper=str(1 / values["current_margin"]),
        resource_displacement_upper=str(values["M_C"]),
        scaled_log_displacement_upper=str(values["M_Y"]),
    )
    return {
        "global_bounds": {k: str(v) for k, v in values.items()},
        "section_bounds": {k: str(v) for k, v in section.items()},
        "native_bounds": native_bounds,
    }


def chart_record(inputs):
    m = model(inputs)
    oracle.checked_model(m)
    n, edges = len(m.nodes), len(m.edges)
    adjacency = {v: set() for v in m.nodes}
    for edge in m.edges:
        u, v = edge["tail"]["node_id"], edge["head"]["node_id"]
        b.require(u != v, "signed graph self-loop")
        adjacency[u].add(v)
        adjacency[v].add(u)
    reached = {m.nodes[0]}
    for _ in m.nodes:
        reached |= {v for u in tuple(reached) for v in adjacency[u]}
    bn, dn, mn = (infinity(IV.matrix(x.tolist())) for x in (m.B, m.D, m.mask))
    b.require(
        2 <= n <= 17
        and edges == n - 1
        and len(reached) == n
        and bn <= 9
        and dn <= 10
        and mn <= 5,
        "signed graph hypotheses fail",
    )
    ref = inputs.geometry.reference
    p = ref.profile.params_resolved
    expected = {
        "eta": 1,
        "kappa_c": 1,
        "W_floor": 0.5,
        "alpha": 2**-24,
        "beta": 2**-24,
        "gamma": 2**-24,
        "kappa_Ah": 0.5,
        "chi_A": 1 / 16,
        "zeta_A": 0.5,
        "tau_A": 1,
    }
    b.require(
        all(getattr(p.candidate, k) == v for k, v in expected.items())
        and p.geometry.kappa_H == 0.5
        and all(v == 1 for v in ref.edge_weights.values())
        and all(v == 0 for row in ref.K4_base for v in row),
        "signed A parameter/reference drift",
    )
    b.require(
        p.realization.extension_evaluator_id == signed.EXTENSION
        and p.realization.approximation_policy_id == signed.APPROXIMATION
        and p.realization.containment_certificate_id == signed.CONTAINMENT
        and p.realization.error_norm_id == signed.ERROR_NORM
        and p.realization.error_tolerance == 2**-48
        and p.realization.iteration_limit == 148,
        "signed A completion/recipe drift",
    )
    b.require(
        (1 + proof.RHO) / (1 - proof.RHO) <= Q(p.solver.conditioning_limit),
        "Hodge conditioning",
    )
    b.require(inputs.dt in (0, b.DT), "fixed completion beat drift")
    return {
        "vertices": n,
        "edges": edges,
        "incidence_norm": str(bn),
        "gram_norm": str(dn),
        "mask_norm": str(mn),
        "completion": signed.EXTENSION,
        "graph_digest": ref.graph.graph_digest,
    }


def bind_case(seed, original):
    case = deepcopy(original)
    case["request"]["source_state_digest"] = seed.scientific_digest
    case["request"]["history_policy"] = history_policy(seed)
    case["request"]["expected_event_id"] = None
    case["request"]["expected_target_graph_digest"] = None
    vector_row = next(
        v
        for v in b.read(b.VECTORS)["grc9_expansion_vectors"]
        if v["fixture_id"] == case["fixture_id"]
    )
    case["oracle"] = b.construction_oracle(
        vector_row, case["request"], seed.to_payload()["specialization"]
    )
    # A's accepted fixture retains the frozen outside-p / old-p identities.
    # Only the event namespace changes; no native topology allocator is used.
    graph = deepcopy(vector_row["expected"]["identity_payloads"]["target_graph"])
    old_event = vector_row["expected"]["event_id"]
    event = case["oracle"]["event_id"]

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
    case["oracle"]["target_graph"] = graph
    case["independent_graph_chart"] = chart_record(
        independent_target(seed, case).inputs
    )
    return case


def make_manifest():
    old = b.read(PREDECESSOR)
    b.require(
        old["acceptance"]["status"] == "accepted_by_user",
        "native A_RG2b predecessor not accepted",
    )
    declaration = b.read(DECLARATION)
    b.require(
        b.sha((b.ROOT / DECLARATION).read_bytes())
        == "521787954476c351e5fc99e492ce0e00f1a972255c8274729c7d0c03098ffbc9",
        "accepted oracle source drift",
    )
    seed, request = fixture(declaration)
    initial = replace(
        seed.inputs,
        current=authority(declaration["initial"]["current"]),
        reset=authority(declaration["initial"]["reset"]),
        dt=b.DT,
        step_index=0,
        time=0,
    )
    nominal = replace(seed, inputs=replace(initial, dt=0))
    b.require(
        initial.geometry.reference.profile.complete_profile_id
        == declaration["source"]["reference"]["profile"]["complete_profile_id"],
        "accepted native declaration mismatch",
    )
    coverage = b.read(b.COVERAGE)
    b.check_digest(coverage)
    wanted = {
        r["fixture_id"]
        for r in coverage["coverage_cells"]
        if r["owner"] == "P9-8.4b" and r["family"] == "A_RG2b" and r["applicable"]
    }
    cases = []
    for v in b.read(b.VECTORS)["grc9_expansion_vectors"]:
        if v["fixture_id"] not in wanted:
            continue
        payload = request.to_payload()
        payload.update(
            {
                k: v["request"][k]
                for k in ("target_effective_degree", "module_chirality", "growth_phase")
            }
        )
        payload.update(
            operation_id="p984b-arg2b-" + v["fixture_id"],
            source_state_digest=nominal.scientific_digest,
            target_profile_template_id=arg2b_profile_template(
                initial.geometry.reference
            ).profile_template_id,
            history_policy=history_policy(nominal),
            resource_distribution=[0.25, 0.5, 0.25]
            if (payload["target_effective_degree"], payload["growth_phase"]) == (52, 1)
            else [0.5, 0.25, 0.25],
        )
        case = {
            "case_id": "P984B-ARG2B-" + v["fixture_id"],
            "fixture_id": v["fixture_id"],
            "family": "A_RG2b",
            "subject_kind": "native_companion",
            "request": payload,
            "coverage_binding": {
                "record_digest": coverage["record_digest"],
                "cell_ids": [v["fixture_id"] + "::A_RG2b::" + role for role in ROLES],
            },
            "schedule": {
                "source_current_beats": 1,
                "source_reset_beats": 0,
                "target_beats_per_role": 10,
                "dt": b.DT,
                "final_read": True,
            },
            "execution_budget_seconds": 1800,
            "comparison": {
                "kind": "complete_native_A_chain_and_independent_interval_equations",
                "budgets": {k: str(v) for k, v in LIMITS.items()},
                "section_norm": "induced_infinity",
                "current_bridge_norm": "edge_l2",
                "state_bridge_norm": "C_and_scaled_log_W_sup",
                "depth": 4,
                "sweeps": 18,
                "accumulated_trajectory_error_bound": False,
                "uniform_parameter_tube": False,
            },
        }
        cases.append(bind_case(nominal, case))
    b.require(len(cases) == 16, "all sixteen A_RG2b layouts required")
    paths = [
        SELF,
        TEST,
        b.SELF,
        b.HERE + "p984b_cci_runtime.py",
        b.HERE + "verify_p983a_arg2b_oracle.py",
        b.HERE + "verify_p983a_aos_oracle.py",
        DECLARATION,
        PREDECESSOR,
        b.BASE + "P9-8.3A.1-ARG2b-Acceptance.json",
        b.BASE + "P9-8.3A.2-ARG2b-RuntimeReview.md",
        b.COVERAGE,
        b.VECTORS,
        b.BASE + "P9-8.0-RG2bCompletion.md",
        b.BASE + "P9-8.0-RG2bNumericalFeasibility.md",
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
        )
        for p in b.ROOT.glob(pattern)
    ]
    return b.seal(
        {
            "schema": "p984b-arg2b-case-manifest-v1",
            "family": "A_RG2b",
            "initial_inputs": initial.to_payload(),
            "nominal_source": nominal.to_payload(),
            "cases": cases,
            "source_bindings": b.bind(paths),
            "independent_source_chart": chart_record(initial),
            "independent_global_proof": global_record(),
            "claim_traces": old["numerical_observations"]["side_tool"],
            "scientific_contracts": {
                "completion": "accepted_signed_argument_retraction_not_compact_support",
                "claim_restrictions": {
                    "GTRS-RG-DEBT-C1-SECTION-REGULARITY": "narrowed_unresolved",
                    "D10.2-EC-RG-CLAIM-CEILING": "completion_relative_Lipschitz_no_spectrum_or_indefinite_positivity",
                    "D10-CL-C-012": "no_arbitrary_graph_or_future_exhaustive_support",
                },
            },
            "source_rule": "one actual A_RG beat; bind actual C/W identities before event execution",
            "resource_recipe": "[1/2,1/4,1/4]; explicit D52 phase-one [1/4,1/2,1/4], independently checked for A",
            "retention": {
                "consumer": "independent complete-chain and writer checker",
                "max_git_file_bytes": 10_000_000,
                "raw_result_budget_bytes": 64_000_000,
                "compact_steps": True,
                "operational_runs_retained": False,
            },
            "user_accepted": False,
            "aggregate_closed": False,
        }
    )


def check_manifest(value):
    b.check_digest(value)
    b.check_bindings(value["source_bindings"])
    b.require(value == make_manifest(), "A_RG2b manifest/case/budget drift")


@contextmanager
def capture_chains():
    rows = []
    real = signed.certify_chain

    def captured(cert, query, x, h, exact_query):
        error, bounds = real(cert, query, x, h, exact_query)
        b.require(
            cert.bounds.to_dict() == global_record()["native_bounds"],
            "native global proof mismatch",
        )
        rows.append(
            {
                "input_identity": cert.inputs.identity,
                "query": list(query),
                "x": [a.tolist() for a in x],
                "h": [a.tolist() for a in h],
                "native_chain_error": str(error),
                "native_chain_bounds": {k: str(v) for k, v in bounds.items()},
                "native_global_digest": b.digest(cert.bounds.to_dict()),
            }
        )
        return error, bounds

    with patch.object(signed, "certify_chain", captured):
        yield rows


def chain(value):
    return oracle.Chain(
        [np.asarray(x, dtype=np.float64) for x in value["chain"]["x"]],
        [np.asarray(h, dtype=np.float64) for h in value["chain"]["h"]],
    )


def level_residuals(m, work):
    levels = []
    n = len(m.nodes)
    for i in range(1, 5):
        projected = [
            min(proof.C_HIGH, max(proof.C_LOW, Q(float(z)))) for z in work.x[i][:n]
        ]
        projected += [
            min(proof.Y_HIGH, max(proof.Y_LOW, Q(float(z)))) for z in work.x[i][n:]
        ]
        f, source = proof.literal_signed_increment(
            m, "A", vector(projected), IV.matrix(work.h[i].tolist())
        )
        levels.append(
            {
                "level": i,
                "state_residual": str(
                    infinity(vector(work.x[i]) + f - vector(work.x[i - 1]))
                ),
                "geometry_residual": str(
                    infinity(
                        IV.matrix(work.h[i - 1].tolist())
                        - (m.I + number(Q(1, 2)) * source)
                    )
                ),
            }
        )
    return levels


def truth(before, value, *, ci=None, wi=None):
    b.require((ci is None) == (wi is None), "complete intended C/W inputs required")
    m = model(before)
    work = chain(value)
    c, w = (
        (vector(before.current.C), vector(before.current.W_A))
        if ci is None
        else (ci, wi)
    )
    h, certificate = oracle.certify_chain(
        proof.auxiliary(m), "A", work, proof.state("A", c, w)
    )
    high = IntervalRows(m)
    read = high.read("A", c, w, h)
    drive = high.conductance(c, w, read["baseline"])
    readback = IV.matrix(
        [
            (x - g) / (x + g) * j / 16
            for x, g, j in zip(w, drive, read["J"], strict=True)
        ]
    )
    return {
        "model": m,
        "high": high,
        "H": h,
        "certificate": certificate,
        "read": read,
        "readback": readback,
        "flat": inverse(h) * readback,
        "c": c,
        "w": w,
    }


def independent_certificate(before, value):
    exact = truth(before, value)
    cert = exact["certificate"]
    h_error = min(cert["total_error"], infinity(IV.matrix(value["H"]) - exact["H"]))
    errors = {
        "geometry_error": h_error,
        "current_error": full_error(value["J"], exact["read"]["J"]),
        "baseline_error": full_error(value["baseline"], exact["read"]["baseline"]),
        "source_error": full_error(
            np.asarray(value["source"]).ravel(),
            IV.matrix(list(exact["read"]["source"])),
        ),
        "readback_error": full_error(value["readback"], exact["readback"]),
        "flat_error": full_error(value["flat"], exact["flat"]),
    }
    levels = level_residuals(proof.auxiliary(exact["model"]), chain(value))
    b.require(
        max(Q(x["state_residual"]) for x in levels) == cert["state_residual"]
        and max(Q(x["geometry_residual"]) for x in levels) == cert["geometry_residual"],
        "per-level residual mismatch",
    )
    global_bounds = proof.global_bounds("A")
    section = proof.section_budgets(global_bounds)
    first_tail = (
        section["inverse_lip"]
        * global_bounds["A_H"]
        * section["q_section"] ** 3
        * section["value_radius"]
    )
    zero = [i for i, v in enumerate(before.current.C) if v == 0]
    upper = {
        str(i): str(
            Q(value["chain"]["x"][1][i])
            + cert["state_error"]
            + first_tail
            + section["inverse_lip"] * cert["input_error"] / proof.SECTION_LIP
        )
        for i in zero
    }
    return {
        "input_identity": before.identity,
        "selected_read_digest": value["record_digest"],
        "bounds": {k: str(v) for k, v in errors.items()},
        "chain": {k: str(v) for k, v in cert.items()},
        "level_residuals": levels,
        "first_inverse_tail": str(first_tail),
        "zero_core_first_predecessor_upper": upper,
    }


@measured("independent_checks")
def read_record(section, point, record):
    b.require(
        record["input_identity"] == section.inputs.identity,
        "captured chain operand mismatch",
    )
    result = b.seal(
        {
            "input_identity": section.inputs.identity,
            "identity": section.identity,
            "selected_inputs_identity": point.inputs.identity,
            "point_identity": point.identity,
            "read_source": point.read.source_identity,
            "read_current": list(point.read.current.values),
            "H": [list(r) for r in section.geometry.one_form_hodge.matrix],
            "J": list(point.current.values),
            "baseline": list(point.baseline.values),
            "readback": list(point.read.flux.values),
            "flat": list(point.read.causal_flat.values),
            "source": [list(r) for r in _source(point, point.current).increment],
            "levels": section.levels,
            "evaluations": section.evaluations,
            "error_upper": section.error_upper,
            "enclosure": list(section.enclosure),
            "recipe": section.to_payload()["numerics"],
            "chain": record,
        }
    )
    result["independent_certificate"] = independent_certificate(section.inputs, result)
    check_read(section.inputs, result)
    return result


def native_read(before):
    with timing_scope("native_execution"):
        with capture_chains() as rows:
            section = rg.CandidateRG2bSection(before, backend(before))
        point = CandidateACurrent(
            replace(before, geometry=section.geometry, stage="rg2b_section"),
            backend(before),
        )
    b.require(len(rows) == 1, "read section count drift")
    return read_record(section, point, rows[0])


def check_read(before, value, *, numerics=False):
    b.check_digest({k: v for k, v in value.items() if k != "independent_certificate"})
    chart_record(before)
    b.require(
        all(0 <= Q(c) <= Q(9, 2) for c in before.current.C),
        "physical section query outside K",
    )
    b.require(
        before.current.W_A is not None and before.current.Z_4 is None,
        "A history admission",
    )
    a_oracle.chart_admitted(before.current.C, before.current.W_A, ordinary=False)
    work = chain(value)
    m = model(before)
    b.require(
        value["input_identity"] == before.identity
        and value["recipe"] == signed.APPROXIMATION
        and value["levels"] == 4
        and value["evaluations"] == 148,
        "section input/recipe/depth drift",
    )
    b.require(
        value["identity"]
        == "grcv4-rg2b-section-sha256:"
        + b.digest(
            {
                "numerics": signed.APPROXIMATION,
                "inputs": before.to_payload(),
                "differential_reference": backend(before).to_payload(),
            }
        ),
        "section identity drift",
    )
    b.require(
        value["chain"]["input_identity"] == before.identity
        and value["chain"]["query"]
        == list(before.current.C) + [512 * math.log(w) for w in before.current.W_A]
        and np.array_equal(work.x[0], value["chain"]["query"])
        and len(work.x) == 5
        and len(work.h) == 5,
        "inverse chain query/depth drift",
    )
    for x in work.x:
        oracle.finite_array(x, (len(m.nodes) + len(m.edges),))
    for h in work.h:
        oracle.finite_array(h, m.I.shape)
        b.require(
            np.array_equal(h, h.T)
            and np.all(h[m.mask == 0] == 0)
            and infinity(IV.matrix(h.tolist()) - IV.matrix(m.I.tolist())) <= proof.RHO,
            "chain geometry symmetry/support/norm drift",
        )
    b.require(
        np.array_equal(work.h[-1], m.I) and np.array_equal(value["H"], work.h[0]),
        "chain terminal/selected geometry drift",
    )
    native_bounds = value["chain"]["native_chain_bounds"]
    cert = value["independent_certificate"]
    b.require(
        value["chain"]["native_global_digest"]
        == b.digest(global_record()["native_bounds"]),
        "global proof identity drift",
    )
    recalculated = oracle.chain_error_bounds(
        "A",
        4,
        Q(native_bounds["state_residual"]),
        Q(native_bounds["geometry_residual"]),
    )
    b.require(
        all(
            Q(native_bounds[k]) == recalculated[k]
            for k in ("state_error", "geometry_error", "truncation_error")
        ),
        "native chain error algebra drift",
    )
    b.require(
        Q(value["chain"]["native_chain_error"])
        == Q(native_bounds["geometry_error"])
        + Q(native_bounds["truncation_error"])
        + Q(native_bounds["input_error"])
        and Q(value["chain"]["native_chain_error"])
        <= Q(value["error_upper"])
        <= LIMITS["geometry_error"],
        "section error/tail budget drift",
    )
    b.require(
        Q(value["enclosure"][0]) == -Q(value["error_upper"])
        and Q(value["enclosure"][1]) == Q(value["error_upper"]),
        "section enclosure drift",
    )
    selected = replace(
        before,
        geometry=b.GRCV4Geometry(
            before.geometry.reference,
            b.OneFormHodge(
                before.geometry.reference.graph, tuple(map(tuple, value["H"]))
            ),
        ),
        stage="rg2b_section",
    )
    b.require(
        value["selected_inputs_identity"] == selected.identity
        and value["read_current"] == value["J"]
        and value["read_source"] == value["point_identity"],
        "selected Read-Back operand drift",
    )
    source = [
        [
            float(Q(1, 2) * Q(float(Q(float(m.mask[i, j])) * Q(x) * Q(y))))
            for j, y in enumerate(value["flat"])
        ]
        for i, x in enumerate(value["flat"])
    ]
    b.require(value["source"] == source, "signed flat/source assembly drift")
    b.require(
        cert["input_identity"] == before.identity
        and cert["selected_read_digest"] == value["record_digest"]
        and set(cert["bounds"]) == set(LIMITS) - {"resource_error", "history_error"},
        "independent read binding drift",
    )
    b.require(
        all(0 <= Q(x) < LIMITS[k] for k, x in cert["bounds"].items()),
        "full read error budget unresolved",
    )
    cc = cert["chain"]
    levels = cert["level_residuals"]
    b.require(
        [x["level"] for x in levels] == list(range(1, 5))
        and max(Q(x["state_residual"]) for x in levels) == Q(cc["state_residual"])
        and max(Q(x["geometry_residual"]) for x in levels)
        == Q(cc["geometry_residual"]),
        "per-level residual binding drift",
    )
    recalc = oracle.chain_error_bounds(
        "A", 4, Q(cc["state_residual"]), Q(cc["geometry_residual"])
    )
    b.require(
        all(Q(cc[k]) == v for k, v in recalc.items())
        and Q(cc["input_error"]) >= 0
        and Q(cc["input_error"]) <= Q(native_bounds["input_error"])
        and Q(cc["total_error"])
        == recalc["geometry_error"] + recalc["truncation_error"] + Q(cc["input_error"])
        and Q(cc["total_error"]) < LIMITS["geometry_error"],
        "independent chain/tail/input error drift",
    )
    b.require(
        Q(cc["state_residual"]) <= Q(native_bounds["state_residual"])
        and Q(cc["geometry_residual"]) <= Q(native_bounds["geometry_residual"]),
        "native chain residual understates independent equations",
    )
    gb = proof.global_bounds("A")
    sb = proof.section_budgets(gb)
    expected_tail = (
        sb["inverse_lip"] * gb["A_H"] * sb["q_section"] ** 3 * sb["value_radius"]
    )
    b.require(
        Q(cert["first_inverse_tail"]) == expected_tail, "first predecessor tail drift"
    )
    expected_upper = {
        str(i): str(
            Q(value["chain"]["x"][1][i])
            + Q(cc["state_error"])
            + expected_tail
            + sb["inverse_lip"] * Q(cc["input_error"]) / proof.SECTION_LIP
        )
        for i, c in enumerate(before.current.C)
        if c == 0
    }
    b.require(
        cert["zero_core_first_predecessor_upper"] == expected_upper,
        "signed predecessor bound drift",
    )
    if numerics:
        b.require(
            cert == independent_certificate(before, value),
            "independent section equations drift",
        )


def bridge(before, value):
    """Complete C/Y base map; current uses L2 and H uses induced infinity."""
    high = IntervalRows(model(before))
    h = IV.matrix(value["read"]["H"])
    c, w = vector(before.current.C), vector(before.current.W_A)
    actual = high.read("A", c, w, h)
    cn = c - number(b.DT) * high.B * actual["J"]
    wn = high.write(cn, w, actual["J"])
    after = following_inputs(before, value)
    errs = [
        upper_abs(number(x) - y)
        for x, y in zip(value["read"]["J"], actual["J"], strict=True)
    ]
    je = endpoint(IV.sqrt(number(sum(x * x for x in errs))), 1)
    jn = endpoint(IV.sqrt(number(sum(upper_abs(x) ** 2 for x in actual["J"]))), 1)
    xe = infinity(
        proof.state("A", vector(after.current.C), vector(after.current.W_A))
        - proof.state("A", cn, wn)
    )
    he = infinity(
        IV.matrix(value["generated"]) - high.I - number(Q(1, 2)) * actual["source"]
    )
    bounds = proof.global_bounds("A")
    e = Q(value["read"]["independent_certificate"]["chain"]["total_error"])
    last = Q(value["restart"]["independent_certificate"]["chain"]["total_error"])
    bound = (
        last
        + he
        + Q(1, 2) * bounds["B_H"] * e
        + proof.SECTION_LIP * (xe + bounds["A_H"] * e)
    )
    residual = infinity(
        IV.matrix(value["restart"]["H"]) - IV.matrix(value["generated"])
    )
    exact = truth(before, value["read"])
    true_c = c - number(b.DT) * high.B * exact["read"]["J"]
    true_w = high.write(true_c, w, exact["read"]["J"])
    drive = high.conductance(vector(after.current.C), w, vector(value["read"]["J"]))
    return {
        k: str(v)
        for k, v in {
            "current_l2_error": je,
            "current_l2_upper": jn,
            "state_error": xe,
            "geometry_error": he,
            "invariance_residual": residual,
            "invariance_error_bound": bound,
            "resource_error": full_error(after.current.C, true_c),
            "history_error": full_error(after.current.W_A, true_w),
            "writer_target_error": full_error(
                value["writer_targets"][0]["target"], drive
            ),
        }.items()
    }


def perform_step(before):
    targets, writes = [], []
    original_target, original_write = (
        candidate.candidate_a_writer_target,
        candidate.candidate_a_log_interpolation,
    )

    def target(point, c):
        out = original_target(point, c)
        targets.append(
            {
                "point_identity": point.identity,
                "C": list(c.values),
                "W_A": list(point.inputs.current.W_A),
                "J": list(point.current.values),
                "target": list(out[1]),
            }
        )
        return out

    def write(old, drive, dt, tau):
        out = original_write(old, drive, dt, tau)
        writes.append(
            {
                "old": list(old),
                "target": list(drive),
                "dt": dt,
                "tau": tau,
                "result": list(out),
            }
        )
        return out

    with (
        timing_scope("native_execution"),
        capture_chains() as rows,
        patch.object(candidate, "candidate_a_writer_target", target),
        patch.object(candidate, "candidate_a_log_interpolation", write),
    ):
        step = rg.ProvisionalCandidateRG2bStep(before, backend(before))
    b.require(
        len(rows) == 3 and step.writer is not None,
        "ordinary section/writer count drift",
    )
    value = {
        "prestate_identity": before.identity,
        "poststate_identity": step.next_inputs.identity,
        "poststate": {
            "C": list(step.next_inputs.current.C),
            "W_A": list(step.next_inputs.current.W_A),
            "Z_4": None,
        },
        "reset_read": read_record(step.reset_section, step.reset_point, rows[0]),
        "read": read_record(step.section, step.point, rows[1]),
        "restart": read_record(step.restart, step.restart_point, rows[2]),
        "generated": [list(row) for row in step.generated.one_form_hodge.matrix],
        "selection_current": list(step.resource.selection.current.values),
        "writer_targets": targets,
        "log_writes": writes,
        "diagnostics": step.diagnostics.to_dict(),
    }
    value["independent_bridge"] = bridge(before, value)
    check_step(before, value)
    return value, step.next_inputs


def check_step(before, value, *, numerics=False):
    b.require(
        value["prestate_identity"] == before.identity and before.dt == b.DT,
        "step operand/beat drift",
    )
    for role in ROLES:
        state = getattr(before, role)
        a_oracle.chart_admitted(state.C, state.W_A, ordinary=True)
    after = following_inputs(before, value)
    b.require(
        after.identity == value["poststate_identity"]
        and after.current.C == represented_continuity(before, value["read"]["J"]),
        "continuity/clock/reset drift",
    )
    check_read(before, value["read"], numerics=numerics)
    check_read(
        replace(before, current=before.reset), value["reset_read"], numerics=numerics
    )
    check_read(after, value["restart"], numerics=numerics)
    b.require(
        value["selection_current"] == value["read"]["J"],
        "continuity selected-current drift",
    )
    b.require(
        len(value["writer_targets"]) == len(value["log_writes"]) == 1,
        "single W writer required",
    )
    target, write = value["writer_targets"][0], value["log_writes"][0]
    b.require(
        target
        == {
            "point_identity": value["read"]["point_identity"],
            "C": list(after.current.C),
            "W_A": list(before.current.W_A),
            "J": value["read"]["J"],
            "target": target["target"],
        },
        "fresh-C/selected-J/incoming-W writer operands drift",
    )
    b.require(
        write
        == {
            "old": list(before.current.W_A),
            "target": target["target"],
            "dt": before.dt,
            "tau": 1,
            "result": list(after.current.W_A),
        },
        "W log interpolation operands drift",
    )
    with localcontext() as context:
        context.prec = 150
        a = (-Decimal.from_float(before.dt)).exp()
        expected = tuple(
            float(
                (
                    a * Decimal.from_float(w).ln()
                    + (1 - a) * Decimal.from_float(g).ln()
                ).exp()
            )
            for w, g in zip(before.current.W_A, target["target"], strict=True)
        )
    b.require(after.current.W_A == expected, "log writer output drift")
    size = len(value["read"]["H"])
    generated = [
        [
            float(Q(i == j) + Q(1, 2) * Q(value["read"]["source"][i][j]))
            for j in range(size)
        ]
        for i in range(size)
    ]
    b.require(
        value["generated"] == generated,
        "generated geometry must consume same selected source",
    )
    diag = value["diagnostics"]
    independent = value["independent_bridge"]
    b.require(
        diag["regularity"] == "Lipschitz_only"
        and diag["continuity_evaluations"] == 1
        and diag["carrier_writes"] == 0
        and diag["section_error_upper"] == value["read"]["error_upper"],
        "ordinary stage counts drift",
    )
    b.require(
        all(Q(v) >= 0 for v in independent.values())
        and Q(independent["resource_error"]) < LIMITS["resource_error"]
        and Q(independent["history_error"]) < LIMITS["history_error"]
        and Q(independent["writer_target_error"]) < LIMITS["history_error"]
        and Q(independent["invariance_residual"])
        <= Q(independent["invariance_error_bound"]),
        "independent invariance/C/W error unresolved",
    )
    p = before.geometry.reference.profile.params_resolved.solver
    b.require(
        Q(independent["current_l2_error"])
        <= Q(p.absolute_tolerance)
        + Q(p.relative_tolerance) * Q(independent["current_l2_upper"])
        and Q(independent["geometry_error"]) <= LIMITS["geometry_error"]
        and proof.SECTION_LIP * Q(independent["state_error"])
        <= LIMITS["geometry_error"],
        "native arithmetic bridge unresolved",
    )
    b.require(
        Q(diag["invariance_residual"]) == Q(independent["invariance_residual"])
        and Q(diag["invariance_residual"]) <= Q(diag["invariance_error_bound"]),
        "native invariance residual/bound drift",
    )
    for key in ("current", "state", "geometry"):
        name = "current_l2_error" if key == "current" else key + "_error"
        b.require(
            Q(independent[name]) <= Q(diag["native_" + key + "_error"]),
            "native bridge understates independent error",
        )
    if numerics:
        b.require(independent == bridge(before, value), "bridge equations drift")
    return after


def effect_checks(before, value):
    exact = truth(before, value)
    m, high = exact["model"], exact["high"]
    c, w, h = (
        np.asarray(before.current.C),
        np.asarray(before.current.W_A),
        np.asarray(value["H"]),
    )
    controls = {}
    for name in ("geometry", "feedback"):
        actual = m.read("A", c.copy(), w.copy(), h.copy(), **{name: False})
        expected = high.read("A", exact["c"], exact["w"], exact["H"], **{name: False})
        for field in ("J",) if name == "feedback" else ("J", "baseline"):
            controls[name + "_" + field] = separation(
                np.asarray(value[field]),
                actual[field],
                exact["read"][field],
                expected[field],
            )
    image = np.asarray(
        [
            [float(Q(i == j) + Q(1, 2) * Q(v)) for j, v in enumerate(row)]
            for i, row in enumerate(value["source"])
        ]
    )
    exact_image = high.I + number(Q(1, 2)) * exact["read"]["source"]
    controls["section_vs_instantaneous_image"] = separation(
        h.ravel(),
        image.ravel(),
        IV.matrix(list(exact["H"])),
        IV.matrix(list(exact_image)),
    )
    if len(c) > 10:
        off = m.ordinary_os("A", c.copy(), w.copy())[2]
        oi = high.ordinary_os("A", exact["c"], exact["w"])[2]
        controls["not_OS_current"] = separation(
            np.asarray(value["J"]),
            off["read"]["J"],
            exact["read"]["J"],
            oi["read"]["J"],
        )
        _, _, off = oracle.ordinary(m, "A", c.copy(), np.ones(len(w)))
        controls["retained_W_current"] = separation(
            np.asarray(value["J"]),
            off["read"]["J"],
            exact["read"]["J"],
            off["exact_read"]["J"],
        )
        controls["retained_W_section"] = separation(
            h.ravel(),
            off["H"].ravel(),
            IV.matrix(list(exact["H"])),
            IV.matrix(list(off["exact_H"])),
        )
    return controls


def check_effects(before, value, controls, *, numerics=False):
    names = {
        "geometry_J",
        "geometry_baseline",
        "feedback_J",
        "section_vs_instantaneous_image",
    }
    if len(before.current.C) > 10:
        names |= {"not_OS_current", "retained_W_current", "retained_W_section"}
    b.require(
        set(controls) == names
        and all(
            x["minimum_margin_ratio"] > 1 and x["exact_effect_lower"] > 0
            for x in controls.values()
        ),
        "fixed-section A effect unresolved",
    )
    if numerics:
        b.require(controls == effect_checks(before, value), "effect equations drift")


@measured("independent_checks")
def run_source(manifest):
    initial = b.GeometryStageInputs.from_payload(manifest["initial_inputs"])
    step, after = perform_step(initial)
    seed = replace(state(manifest["nominal_source"]), inputs=replace(after, dt=0))
    reads = {
        role: native_read(replace(seed.inputs, current=getattr(seed.inputs, role)))
        for role in ROLES
    }
    controls = {
        role: effect_checks(
            replace(seed.inputs, current=getattr(seed.inputs, role)), reads[role]
        )
        for role in ROLES
    }
    return {
        "source_step": step,
        "actual_source": seed.to_payload(),
        "source_reads": reads,
        "source_effects": controls,
    }, seed


def preflight(target):
    out = {}
    for role in ROLES:
        c, w = (
            np.asarray(getattr(target.inputs, role).C),
            np.asarray(getattr(target.inputs, role).W_A),
        )
        m = model(target.inputs)
        rows = []
        for _ in range(10):
            before_c, before_w = c.copy(), w.copy()
            a_oracle.chart_admitted(c, w, ordinary=True)
            c, w, truth_value = oracle.ordinary(m, "A", c, w)
            a_oracle.chart_admitted(c, w, ordinary=True)
            rows.append(
                {
                    "C": c.tolist(),
                    "W_A": w.tolist(),
                    "entry_C": before_c.tolist(),
                    "entry_W_A": before_w.tolist(),
                    "section_error": str(truth_value["certificate"]["total_error"]),
                    "current_error": str(truth_value["current_error"]),
                    "resource_error": str(truth_value["resource_error"]),
                    "history_error": str(truth_value["history_error"]),
                }
            )
        out[role] = rows
    return out


@measured("native_execution")
def event_capture(seed, request):
    owner = native.GRC9V4ARG2bOperation(seed)
    initial = json.loads(owner.checkpoint())
    reads = []
    publication = []
    detections = []
    real_readmit = native._arg2b_readmit
    real_section = rg.CandidateRG2bSection
    real_point = native.CandidateACurrent
    real_receipts = native.make_commit_receipts
    real_detection = native.GRC9V4CandidateDetection

    def observed_readmit(subject):
        sections = []
        points = []

        def section(*args, **kwargs):
            result = real_section(*args, **kwargs)
            sections.append(result)
            return result

        def point(*args, **kwargs):
            result = real_point(*args, **kwargs)
            if result.inputs.stage == "rg2b_section":
                points.append(result)
            return result

        with (
            capture_chains() as rows,
            patch.object(rg, "CandidateRG2bSection", section),
            patch.object(native, "CandidateACurrent", point),
        ):
            result = real_readmit(subject)
        b.require(
            len(rows) == len(points) == len(sections) == 2,
            "both-role event section count drift",
        )
        a, z = (
            read_record(ss, pp, cc)
            for ss, pp, cc in zip(sections, points, rows, strict=True)
        )
        reads.append(
            {
                "inputs": subject.inputs.to_payload(),
                "read": a,
                "reset_read": z,
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
        return real_receipts(*args, **kwargs)

    def observed_detection(postbeat, policy):
        result = real_detection(postbeat, policy)
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

    forbidden = AssertionError("event must not execute ordinary/CI/OS/writer work")
    with (
        patch.object(native, "_arg2b_readmit", observed_readmit),
        patch.object(native, "make_commit_receipts", observed_receipts),
        patch.object(native, "GRC9V4CandidateDetection", observed_detection),
        patch.object(rg, "ProvisionalCandidateRG2bStep", side_effect=forbidden),
        patch.object(native, "ProvisionalCandidateCIStep", side_effect=forbidden),
        patch.object(native, "CandidateAOSPass", side_effect=forbidden),
        patch.object(candidate, "candidate_a_log_interpolation", side_effect=forbidden),
    ):
        outcome = owner.expand(request)
    value = {
        "source_checkpoint": initial,
        "admission_reads": reads,
        "publication": publication,
        "detections": detections,
        "checkpoint": json.loads(owner.checkpoint()),
        "actual_target": owner.state.to_payload(),
        "receipts": [r.to_payload() for r in outcome.emitted_receipts],
        "failure": None if outcome.committed else outcome.failure.to_payload(),
        "replay_identical": False,
    }
    if outcome.committed:
        value["replay_identical"] = (
            native.GRC9V4ARG2bOperation.replay(owner.checkpoint()).checkpoint()
            == owner.checkpoint()
        )
    return owner, outcome, value


@measured("independent_checks")
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
            replace(parent.inputs, current=parent.inputs.reset),
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
    refs = cp["reference_currents"]
    source_ref, target_ref = (
        seed.inputs.geometry.reference,
        target.inputs.geometry.reference,
    )
    b.require(
        len(refs) == 1
        and refs[0]["event_id"] == case["oracle"]["event_id"]
        and refs[0]["source_graph_digest"] == source_ref.graph.graph_digest
        and refs[0]["target_graph_digest"] == target_ref.graph.graph_digest,
        "reference lineage identity drift",
    )
    for role, key in (("current", "read"), ("reset", "reset_read")):
        old = value["admission_reads"][0][key]["J"]
        currents = dict(zip(source_ref.graph.live_edge_ids, old, strict=True))
        expected_j = [currents.get(e, 0.0) for e in target_ref.graph.live_edge_ids]
        b.require(
            refs[0]["roles"][role] == {"source": old, "target": expected_j},
            "reference current map drift",
        )
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
        and first["core"]["information_losses"] == [],
        "event/loss drift",
    )
    source_history = case["request"]["history_policy"]["candidate"][
        "source_history_digest"
    ]
    target_history = payload_identity(
        "history_content_identity_payload",
        a_oracle.candidate_content(
            *(
                a_oracle.authority(
                    getattr(target.inputs, role).C, getattr(target.inputs, role).W_A
                )
                for role in ROLES
            )
        ),
    )
    for channel, disposition, source_digest, target_digest in (
        ("candidate", "exact_transport", source_history, target_history),
        ("carrier", "not_applicable", None, None),
    ):
        b.require(
            first["history"][channel]
            == {
                "subject": channel,
                "disposition": disposition,
                "source_history_digest": source_digest,
                "target_history_digest": target_digest,
                "information_loss": "none",
            },
            "A_RG2b history receipt drift",
        )
    b.require(
        value["failure"] is None and value["replay_identical"] is True,
        "event/replay incomplete",
    )
    b.require(
        "carrier_archives" not in cp
        and all(
            getattr(target.inputs, r).W_A is not None
            and getattr(target.inputs, r).Z_4 is None
            for r in ROLES
        ),
        "invented RG persistent history",
    )
    return target


@measured("independent_checks")
def execute_case(seed, original):
    case = bind_case(seed, original)
    start = time.monotonic()
    print("ARG2b_CASE_START " + case["case_id"], flush=True)
    row = {
        "case_id": case["case_id"],
        "input_digest": b.digest(original),
        "executed_case": case,
        "coverage_binding": case["coverage_binding"],
        "family": "A_RG2b",
        "outcome": "passed_named_case",
        "case_passed": True,
        "event_committed": True,
        "first_failure": None,
        "continuation": [],
        "final_reads": {},
        "entry_effects": {},
        "final_effects": {},
        "writer_effects": {},
        "user_accepted": False,
        "aggregate_closed": False,
    }
    with b.budget(case["execution_budget_seconds"]):
        expected = independent_target(seed, case)
        row["predictions"] = preflight(expected)
        _owner, outcome, event = event_capture(
            seed, b.GRC9V4ExpansionRequestInput.from_payload(case["request"])
        )
        b.require(outcome.committed, "native event rejected: " + str(event["failure"]))
        row["event"] = event
        target = check_event(seed, case, event)
        for role in ROLES:
            before = replace(
                target.inputs, current=getattr(target.inputs, role), dt=b.DT
            )
            for index in range(1, 11):
                step, following = perform_step(before)
                if index == 1:
                    row["entry_effects"][role] = effect_checks(before, step["read"])
                    row["writer_effects"][role] = writer_effects(before, step)
                    first = step["read"]["independent_certificate"][
                        "zero_core_first_predecessor_upper"
                    ]
                    b.require(
                        first and any(Q(v) < 0 for v in first.values()),
                        "negative signed predecessor unresolved",
                    )
                prediction = row["predictions"][role][index - 1]
                ce = max(
                    abs(Q(x) - Q(y))
                    for x, y in zip(prediction["C"], following.current.C, strict=True)
                )
                we = max(
                    abs(Q(x) - Q(y))
                    for x, y in zip(
                        prediction["W_A"], following.current.W_A, strict=True
                    )
                )
                b.require(
                    ce < Q(1, 2**39) and we < Q(1, 2**47),
                    "independent nominal C/W trajectory mismatch",
                )
                row["continuation"].append(
                    {
                        "role": role,
                        "index": index,
                        "step": step,
                        "nominal_resource_error": str(ce),
                        "nominal_history_error": str(we),
                    }
                )
                before = following
                print(
                    f"ARG2b_BEAT case={case['case_id']} role={role} index={index} elapsed={time.monotonic() - start:.1f}",
                    flush=True,
                )
            final = replace(before, dt=0)
            row["final_reads"][role] = native_read(final)
            row["final_effects"][role] = effect_checks(final, row["final_reads"][role])
    row["elapsed_seconds"] = time.monotonic() - start
    return row


def validate(manifest, result, *, numerics=False):
    b.check_digest(result)
    b.require(
        result["manifest_digest"] == manifest["record_digest"]
        and result["native_runtime_executed"] is True
        and result["user_accepted"] is False
        and result["aggregate_closed"] is False,
        "runtime binding/scope drift",
    )
    shared = result["shared"]
    initial = b.GeometryStageInputs.from_payload(manifest["initial_inputs"])
    after = check_step(initial, shared["source_step"], numerics=numerics)
    seed = state(shared["actual_source"])
    b.require(
        seed == replace(state(manifest["nominal_source"]), inputs=replace(after, dt=0)),
        "source schedule drift",
    )
    for role in ROLES:
        entry = replace(seed.inputs, current=getattr(seed.inputs, role))
        check_read(entry, shared["source_reads"][role], numerics=numerics)
        check_effects(
            entry,
            shared["source_reads"][role],
            shared["source_effects"][role],
            numerics=numerics,
        )
    b.require(
        [r["case_id"] for r in result["cases"]]
        == [c["case_id"] for c in manifest["cases"]],
        "case roster drift",
    )
    for original, row in zip(manifest["cases"], result["cases"], strict=True):
        case = bind_case(seed, original)
        b.require(
            row["input_digest"] == b.digest(original)
            and row["executed_case"] == case
            and row["coverage_binding"] == case["coverage_binding"]
            and row["user_accepted"] is False
            and row["aggregate_closed"] is False,
            "case input/scope drift",
        )
        b.require(
            row["case_passed"] is True
            and row["outcome"] == "passed_named_case"
            and row["event_committed"] is True
            and row["first_failure"] is None,
            "only complete cases may be published",
        )
        target = check_event(seed, case, row["event"], numerics=numerics)
        b.require(
            [(x["role"], x["index"]) for x in row["continuation"]]
            == [(r, i) for r in ROLES for i in range(1, 11)]
            and set(row["final_reads"]) == set(ROLES),
            "both-role schedule incomplete",
        )
        if numerics:
            b.require(
                row["predictions"] == preflight(target),
                "independent preflight equations drift",
            )
        for role in ROLES:
            before = replace(
                target.inputs, current=getattr(target.inputs, role), dt=b.DT
            )
            for entry in (x for x in row["continuation"] if x["role"] == role):
                if entry["index"] == 1:
                    check_effects(
                        before,
                        entry["step"]["read"],
                        row["entry_effects"][role],
                        numerics=numerics,
                    )
                    first = entry["step"]["read"]["independent_certificate"][
                        "zero_core_first_predecessor_upper"
                    ]
                    b.require(
                        first and any(Q(v) < 0 for v in first.values()),
                        "signed predecessor effect unresolved",
                    )
                    controls = row["writer_effects"][role]
                    b.require(
                        set(controls)
                        == {
                            name + suffix
                            for name in (
                                "stale_C_writer",
                                "baseline_J_writer",
                                "no_W_writer",
                            )
                            for suffix in ("_W", "_next_current")
                        }
                        and all(
                            v["minimum_margin_ratio"] > 1
                            and v["exact_effect_lower"] > 0
                            for v in controls.values()
                        ),
                        "writer/next-read effects unresolved",
                    )
                    if numerics:
                        b.require(
                            controls == writer_effects(before, entry["step"]),
                            "writer effect equations drift",
                        )
                before = check_step(before, entry["step"], numerics=numerics)
                prediction = row["predictions"][role][entry["index"] - 1]
                for field, attr, limit, key in (
                    ("C", "C", Q(1, 2**39), "nominal_resource_error"),
                    ("W_A", "W_A", Q(1, 2**47), "nominal_history_error"),
                ):
                    error = max(
                        abs(Q(x) - Q(y))
                        for x, y in zip(
                            prediction[field],
                            getattr(before.current, attr),
                            strict=True,
                        )
                    )
                    b.require(
                        error == Q(entry[key]) and error < limit,
                        "nominal C/W comparison drift",
                    )
                last = entry["step"]["restart"]
            final = replace(before, dt=0)
            observed = row["final_reads"][role]
            check_read(final, observed, numerics=numerics)
            for key in ("H", "J", "baseline", "readback", "flat", "source"):
                b.require(
                    observed[key] == last[key],
                    "fresh deterministic section/restart mismatch",
                )
            check_effects(
                final, observed, row["final_effects"][role], numerics=numerics
            )
    return {
        "retained_integrity": "passed",
        "cases_passed": len(result["cases"]),
        "cases_required": len(manifest["cases"]),
        "successful_history_cells": 2 * len(result["cases"]),
        "native_trajectories_rerun": False,
        "interval_equations_recomputed": numerics,
        "user_accepted": False,
        "aggregate_closed": False,
    }


def write_new(name, value):
    path = b.ROOT / name
    with path.open("x") as out:
        out.write(json.dumps(value, separators=(",", ":"), allow_nan=False) + "\n")


def backend(inputs):
    return GRC9V4CandidateADifferentialReference(
        inputs.geometry.reference.graph.port_graph
    )


def history_policy(seed):
    return a_oracle.history_policy(
        *(
            a_oracle.authority(
                getattr(seed.inputs, role).C, getattr(seed.inputs, role).W_A
            )
            for role in ROLES
        )
    )


def independent_target(seed, case):
    """Frozen role topology and literal C/W lineage; no native allocator or solver."""
    ref = a_oracle.reference(case["oracle"]["target_graph"])
    old_graph = seed.inputs.geometry.reference.graph
    event = case["oracle"]["event_id"]
    shares = {
        event + f"/satellite/{i}": Q(x)
        for i, x in enumerate(case["request"]["resource_distribution"], 1)
    }
    b.require(
        sum(shares.values()) == 1 and all(x >= 0 for x in shares.values()),
        "resource simplex",
    )
    roles = {}
    for role in ROLES:
        old = getattr(seed.inputs, role)
        c = dict(zip(old_graph.live_node_ids, old.C, strict=True))
        w = dict(zip(old_graph.live_edge_ids, old.W_A, strict=True))
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
            None,
        )
        b.require(
            sum(map(Q, old.C)) == sum(map(Q, roles[role].C)), "exact event charge"
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


def authority(payload):
    return b.GRCV4AuthoritativeState(tuple(payload["C"]), tuple(payload["W_A"]), None)


def following_inputs(before, value):
    b.require(
        set(value["poststate"]) == {"C", "W_A", "Z_4"}
        and value["poststate"]["Z_4"] is None,
        "compact poststate schema/history drift",
    )
    return replace(
        before,
        current=authority(value["poststate"]),
        step_index=before.step_index + 1,
        time=float(Q(before.time) + Q(before.dt)),
    )


def writer_effects(before, step):
    """Exact composed inputs for changed writers and their next section/current."""
    t = truth(before, step["read"])
    high, m = t["high"], t["model"]
    c, w = np.asarray(before.current.C), np.asarray(before.current.W_A)
    after = following_inputs(before, step)
    cn = t["c"] - number(b.DT) * high.B * t["read"]["J"]
    wn = high.write(cn, t["w"], t["read"]["J"])
    nt = truth(after, step["restart"], ci=cn, wi=wn)
    controls = {}
    for name in ("stale_C_writer", "baseline_J_writer", "no_W_writer"):
        if name == "no_W_writer":
            wc, wci = w.copy(), t["w"]
        else:
            wc = staged_write(
                m,
                c.copy() if name == "stale_C_writer" else np.asarray(after.current.C),
                w.copy(),
                np.asarray(
                    step["read"]["baseline"]
                    if name == "baseline_J_writer"
                    else step["read"]["J"]
                ),
            )
            wci = high.write(
                t["c"] if name == "stale_C_writer" else cn,
                t["w"],
                t["read"]["baseline"]
                if name == "baseline_J_writer"
                else t["read"]["J"],
            )
        controls[name + "_W"] = separation(np.asarray(after.current.W_A), wc, wn, wci)
        _, _, off = oracle.ordinary(
            m, "A", np.asarray(after.current.C), np.asarray(wc), exact_c=cn, exact_w=wci
        )
        controls[name + "_next_current"] = separation(
            np.asarray(step["restart"]["J"]),
            off["read"]["J"],
            nt["read"]["J"],
            off["exact_read"]["J"],
        )
    return controls


def main():

    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    for name in ("prepare", "run", "assemble", "check-retained", "numerical-report"):
        mode.add_argument("--" + name, action="store_true")
    parser.add_argument("--case", type=int, action="append", choices=range(1, 17))
    parser.add_argument("--workdir", default="outputs/p984b-arg2b")
    parser.add_argument("--recheck-numerics", action="store_true")
    args = parser.parse_args()
    b.require(
        not args.recheck_numerics or args.check_retained,
        "recheck requires retained mode",
    )
    if args.prepare:
        write_new(INPUTS, make_manifest())
        print("A_RG2b manifest prepared; native campaign not executed")
        return
    manifest = b.read(INPUTS)
    check_manifest(manifest)
    with b.exact_backend(b.ExactBackend.FLINT):
        if args.numerical_report:
            result = b.read(RESULTS)
            started = time.monotonic()
            with native_disabled():
                report = validate(manifest, result, numerics=True)
            report.update(
                schema="p984b-arg2b-independent-recheck-v1",
                manifest_digest=manifest["record_digest"],
                runtime_digest=result["record_digest"],
                native_entry_points_disabled=True,
                elapsed_seconds=time.monotonic() - started,
                source_bindings=b.bind([INPUTS, RESULTS, SELF, TEST]),
                cases=[
                    {
                        "case_id": row["case_id"],
                        "case_digest": b.digest(row),
                        "shared_digest": b.digest(result["shared"]),
                        "successful_history_cells": 2,
                        "interval_equations_recomputed": True,
                        "native_trajectories_rerun": False,
                    }
                    for row in result["cases"]
                ],
            )
            write_new(b.BASE + "P9-8.4b-ARG2bNumericalRecheck.json", b.seal(report))
            print(
                json.dumps(
                    {
                        k: v
                        for k, v in report.items()
                        if k not in ("cases", "source_bindings")
                    },
                    indent=2,
                )
            )
            return
        if args.check_retained:
            print(
                json.dumps(
                    validate(manifest, b.read(RESULTS), numerics=args.recheck_numerics),
                    indent=2,
                )
            )
            return
        work = Path(args.workdir)
        b.require(
            not work.is_absolute() and ".." not in work.parts,
            "repository-relative working directory required",
        )
        work = b.ROOT / work
        work.mkdir(parents=True, exist_ok=True)
        shared_path = work / "source.json"
        if shared_path.exists():
            saved = json.loads(shared_path.read_bytes())
            b.check_digest(saved)
            b.require(
                saved["manifest_digest"] == manifest["record_digest"],
                "completed source subject drift",
            )
            shared = saved["shared"]
            seed = state(shared["actual_source"])
        else:
            t = time.monotonic()
            with timing_profile() as timings:
                shared, seed = run_source(manifest)
            print("ARG2b_SOURCE_TIMING " + json.dumps(timings), flush=True)
            saved = b.seal(
                {
                    "manifest_digest": manifest["record_digest"],
                    "shared": shared,
                    "elapsed_seconds": time.monotonic() - t,
                }
            )
            shared_path.write_text(
                json.dumps(saved, separators=(",", ":"), allow_nan=False) + "\n"
            )
        if args.run:
            for i in args.case or range(1, 17):
                path = work / f"case-{i:02}.json"
                if path.exists():
                    row = json.loads(path.read_bytes())
                    b.check_digest(row)
                    b.require(
                        row["manifest_digest"] == manifest["record_digest"]
                        and row["shared_digest"] == b.digest(shared),
                        "completed case subject drift",
                    )
                    continue
                with timing_profile() as timings:
                    row = execute_case(seed, manifest["cases"][i - 1])
                row["timing_seconds"] = timings
                record = b.seal(
                    {
                        "manifest_digest": manifest["record_digest"],
                        "shared_digest": b.digest(shared),
                        "case": row,
                    }
                )
                serialization_start = time.monotonic()
                encoded = (
                    json.dumps(record, separators=(",", ":"), allow_nan=False) + "\n"
                )
                serialized = time.monotonic() - serialization_start
                path.write_text(encoded)
                print(
                    "ARG2b_TIMING "
                    + json.dumps(
                        {
                            **timings,
                            "json_serialization": serialized,
                            "raw_bytes": len(encoded.encode()),
                        }
                    ),
                    flush=True,
                )
                print(
                    f"ARG2b_CASE_PASS index={i} seconds={row['elapsed_seconds']:.1f}",
                    flush=True,
                )
        if args.assemble:
            rows = []
            for i in range(1, 17):
                row = json.loads((work / f"case-{i:02}.json").read_bytes())
                b.check_digest(row)
                b.require(
                    row["manifest_digest"] == manifest["record_digest"]
                    and row["shared_digest"] == b.digest(shared),
                    "completed case subject drift",
                )
                rows.append(row["case"])
            result = b.seal(
                {
                    "schema": "p984b-arg2b-runtime-v1",
                    "manifest_digest": manifest["record_digest"],
                    "shared": shared,
                    "cases": rows,
                    "environment": {
                        "python": platform.python_version(),
                        "numpy": np.__version__,
                        "python_flint": version("python-flint"),
                    },
                    "native_runtime_executed": True,
                    "user_accepted": False,
                    "aggregate_closed": False,
                }
            )
            report = validate(manifest, result)
            b.require(
                len(json.dumps(result, separators=(",", ":"), allow_nan=False).encode())
                < manifest["retention"]["raw_result_budget_bytes"],
                "raw retention budget exceeded",
            )
            write_new(RESULTS, result)
            print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
